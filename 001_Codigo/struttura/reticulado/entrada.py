"""Lectura del CSV de RETICULADO PLANO.

Es el mismo formato de bloques que el pórtico, pero más corto: no hay giros ni momentos.

    PROYECTO   tipo;reticulado
    NODOS      id;x;y
    MATERIALES id;E;[nu;fy;sadm;alfa]
    SECCIONES  id;tipo;...   (para el reticulado alcanza con A; para verificar pandeo también hace falta I)
    BARRAS     id;nodo_i;nodo_j;material;seccion;[pandeo]
    APOYOS     nodo;ux;uy            (1 = restringido, 0 = libre)
    RESORTES   nodo;kx;ky
    RESORTES INCLINADOS  nodo;k;angulo
    CARGAS     caso;nodo;Px;Py
    CARGAS EN BARRAS  caso;barra;tipo;valor                  (solo  temp, corta, larga:  efectos que alargan/acortan la barra)
    DESPLAZAMIENTOS PREFIJADOS  caso;nodo;ux;uy
    DESAJUSTE DE RESORTES  caso;nodo;ux;uy;inclinado
    COMBINACIONES  combinacion;caso;factor

Internamente el archivo se convierte a un modelo de pórtico plano con TODAS las barras articuladas en ambos
extremos (que es exactamente un reticulado: la matriz de la barra queda con los términos K = AE/L de la tabla
de la cátedra y los giros de nudo se fijan solos).  El solver, los esfuerzos y los gráficos son los del pórtico,
verificados contra los ejercicios de la cátedra.
"""
from __future__ import annotations

import math
import re
import tempfile
from pathlib import Path

from struttura.emparrillado.entrada import ErrorDeEntrada, _norm, _partir_bloques, avisar_columnas
from struttura.portico.entrada import cargar_modelo as _cargar_portico

TITULOS = ["PROYECTO", "NODOS", "MATERIALES", "SECCIONES", "BARRAS", "APOYOS", "RESORTES",
           "RESORTES INCLINADOS", "CARGAS", "CARGAS EN BARRAS", "DESPLAZAMIENTOS PREFIJADOS",
           "DESAJUSTE DE RESORTES", "COMBINACIONES"]

_COLUMNAS = {
    "NODOS": ("id", "x", "y"),
    "MATERIALES": ("id", "e", "nu", "fy", "sadm", "alfa", "rho", "lib"),
    "SECCIONES": ("id", "tipo", "lib", "d", "t", "b", "h", "i", "a", "c", "kv", "tf", "tw"),
    "BARRAS": ("id", "nodo_i", "nodo_j", "material", "seccion", "pandeo"),
    "APOYOS": ("nodo", "ux", "uy"),
    "RESORTES": ("nodo", "kx", "ky"),
    "RESORTES INCLINADOS": ("nodo", "k", "angulo"),
    "DESAJUSTE DE RESORTES": ("caso", "nodo", "ux", "uy", "inclinado"),
    "CARGAS": ("caso", "nodo", "px", "py"),
    "CARGAS EN BARRAS": ("caso", "barra", "tipo", "valor", "valor2"),
    "DESPLAZAMIENTOS PREFIJADOS": ("caso", "nodo", "ux", "uy"),
    "COMBINACIONES": ("combinacion", "caso", "factor"),
}

from ..pandeo import ALIAS as _ALIAS, PANDEO  # noqa: E402  (condición de extremos: módulo común struttura/pandeo.py)


def _codigo_pandeo(txt, n, bid):
    c = _norm(txt or "").replace(" ", "").replace("_", "-").replace("–", "-")
    if c not in _ALIAS:
        raise ErrorDeEntrada(f"Bloque BARRAS, línea {n}: pandeo '{txt}' no es válido para la barra '{bid}'.  "
                             "Valores: art-art (defecto), emp-lib, emp-art, emp-emp")
    return _ALIAS[c]


def _emitir(f):
    return ";".join(f)


def _convertir(bloques):
    """Arma el texto CSV de pórtico.  Devuelve (líneas, mapa_línea_nueva→línea_original, pandeo, sin_I)."""
    out, mapa, pandeo, sin_I = [], {}, {}, set()

    def add(txt, n):
        out.append(txt)
        mapa[len(out)] = n

    for b in bloques.values():
        t = b["titulo"]
        filas = b["filas"]
        add(t, b["linea"])
        if t == "PROYECTO":
            for n, f in filas:
                if f and _norm(f[0]) == "tipo":
                    f = ["tipo", "portico"]
                add(_emitir(f), n)
            add("_nodal;si", b["linea"])                 # peso propio [propio]: mitad del peso de cada biela en cada nudo extremo
            continue
        if not filas:
            continue
        n0, cab = filas[0]
        cab = [c.strip().lower() for c in cab]
        datos = filas[1:]
        if t == "SECCIONES":
            if "i" not in cab:
                cab = cab + ["i"]
                datos = [(n, f + [""] * (len(cab) - 1 - len(f)) + [""]) for n, f in datos]
            ii = cab.index("i")
            it = cab.index("tipo") if "tipo" in cab else None
            nd = []
            for n, f in datos:
                f = list(f) + [""] * (len(cab) - len(f))
                if it is not None and _norm(f[it]) == "generica" and not f[ii].strip():
                    f[ii] = "1"
                    sin_I.add(f[0])
                nd.append((n, f))
            add(_emitir(cab), n0)
            for n, f in nd:
                add(_emitir(f), n)
            continue
        if t == "BARRAS":
            obl = ["id", "nodo_i", "nodo_j", "material", "seccion"]
            faltan = [c for c in obl if c not in cab]
            if faltan:
                raise ErrorDeEntrada(f"Bloque BARRAS: faltan las columnas {faltan}.  Encabezado encontrado: {cab}")
            if "art_i" in cab or "art_j" in cab:
                raise ErrorDeEntrada("Bloque BARRAS: en un reticulado todas las barras son articuladas; "
                                     "no uses art_i / art_j (si necesitás barras rígidas, usá el programa de pórtico)")
            ip = cab.index("pandeo") if "pandeo" in cab else None
            add(_emitir(obl + ["art_i", "art_j"]), n0)
            for n, f in datos:
                f = list(f) + [""] * (len(cab) - len(f))
                d = {c: f[k] for k, c in enumerate(cab)}
                pandeo[d["id"]] = _codigo_pandeo(f[ip] if ip is not None else "", n, d["id"])
                add(_emitir([d[c] for c in obl] + ["1", "1"]), n)
            continue
        extra = {"APOYOS": ("phi", "0", "apoyos"), "RESORTES": ("kphi", "", "resortes"),
                 "CARGAS": ("m", "0", "cargas"), "DESPLAZAMIENTOS PREFIJADOS": ("phi", "0", "prefijados"),
                 "DESAJUSTE DE RESORTES": ("phi", "", "desajustes")}
        if t in extra:
            col, val, _ = extra[t]
            if col in cab or (t == "CARGAS" and "m" in cab):
                raise ErrorDeEntrada(f"Bloque {t}: en un reticulado no hay giros ni momentos "
                                     f"(sobra la columna '{col}'); usá solo ux/uy o Px/Py")
            if t == "DESAJUSTE DE RESORTES" and "inclinado" in cab:
                k = cab.index("inclinado")
                cab = cab[:k] + [col] + cab[k:]
                datos = [(n, (list(f) + [""] * (len(cab) - 1 - len(f)))[:k] + [val] + (list(f) + [""] * (len(cab) - 1 - len(f)))[k:])
                         for n, f in datos]
            else:
                cab = cab + [col]
                datos = [(n, list(f) + [""] * (len(cab) - 1 - len(f)) + [val]) for n, f in datos]
        if t == "CARGAS EN BARRAS":
            if "valor2" not in cab:                                 # en reticulado alcanza con 'valor'
                cab = cab + ["valor2"]
            it = cab.index("tipo") if "tipo" in cab else None
            ib = cab.index("barra") if "barra" in cab else None
            iv, iv2 = (cab.index("valor") if "valor" in cab else None), (cab.index("valor2") if "valor2" in cab else None)
            nd = []
            for n, f in datos:
                f = list(f) + [""] * (len(cab) - len(f))
                tp = _norm(f[it]) if it is not None else ""
                if tp in ("corta", "larga"):
                    e = f[iv].strip() if iv is not None else ""
                    if not e or e.startswith("-"):
                        raise ErrorDeEntrada(f"Bloque CARGAS EN BARRAS, línea {n}: '{tp}' lleva el desajuste e como número POSITIVO "
                                             f"(cuánto es más {tp} la barra que la distancia entre nudos)")
                    f[it] = "dl"
                    f[iv] = ("-" if tp == "corta" else "") + e
                    tp = "dl"
                if tp == "temp" and iv is not None and iv2 is not None and not f[iv2].strip():
                    f[iv2] = f[iv]                      # temperatura uniforme: una sola cifra alcanza
                nd.append((n, f))
                if tp not in ("temp", "dl"):
                    raise ErrorDeEntrada(f"Bloque CARGAS EN BARRAS, línea {n}: en un reticulado las cargas van SOLO en los nudos (bloque CARGAS): "
                                         f"las barras son bielas y no admiten carga en el tramo ni perpendicular.  En el bloque CARGAS EN BARRAS solo se "
                                         f"aceptan efectos que no flexan la barra: 'temp' (ΔT uniforme), 'corta' o 'larga' (desajuste de longitud e); "
                                         f"'{f[it]}' no es válido")
            datos = nd
        add(_emitir(cab), n0)
        for n, f in datos:
            add(_emitir(f), n)
    return out, mapa, pandeo, sin_I


def cargar_modelo(ruta):
    """Devuelve un Modelo de pórtico (todas las barras articuladas) con los atributos extra:
    modelo.ret_pandeo {índice_barra: código}, modelo.ret_sin_I {ids de sección sin inercia}."""
    ruta = Path(ruta)
    if not ruta.is_file():
        raise ErrorDeEntrada(f"No se encuentra el archivo '{ruta}'")
    bloques = _partir_bloques(ruta, TITULOS)
    lineas, mapa, pandeo, sin_I = _convertir(bloques)
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d) / ruta.name
        tmp.write_text("\n".join(lineas) + "\n", encoding="utf-8")
        try:
            m = _cargar_portico(tmp)
        except ErrorDeEntrada as e:
            msg = re.sub(r"línea (\d+)", lambda g: f"línea {mapa.get(int(g.group(1)), g.group(1))}", str(e))
            raise ErrorDeEntrada(msg) from None
    m.archivo = ruta
    m.ret_pandeo = {k: pandeo[b.id] for k, b in enumerate(m.barras)}
    m.ret_sin_I = set(sin_I)
    m.avisos = [a for a in m.avisos if "articulad" not in a.lower()]
    avisar_columnas(bloques, m.avisos, _COLUMNAS)
    return m
