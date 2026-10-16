"""Lector y escritor del CSV de Struttura para el editor, sin pérdida de información.

Documento (JSON-izable):
    {"tipo": "portico", "pre": [líneas de comentario antes del primer bloque], "bom": bool,
     "bloques": [{"t": "NODOS", "antes": [comentarios antes del título], "cab": ["id","x","y"] | None (PROYECTO),
                  "filas": [{"c": [celdas como texto], "n": [comentarios justo antes de la fila]}], "fin": [comentarios al final]}]}
Las celdas se guardan como el texto original (no se reformatean los números).  Al escribir, el separador es «;».
"""
from __future__ import annotations

import csv
import io
import unicodedata

from .esquema import ESQUEMAS, bloque_de

_TIPOS_ALIAS = {"espacial": "portico3d", "3d": "portico3d"}


def _norm(s):
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn").lower().strip().strip("[]:").strip()


def _titulos(tipo):
    """{título normalizado: título canónico}; con tipo None, la unión de todos los tipos."""
    tipos = [tipo] if tipo in ESQUEMAS else list(ESQUEMAS)
    return {_norm(b["t"]): b["t"] for t in tipos for b in ESQUEMAS[t]["bloques"]}


def decodificar(datos: bytes):
    try:
        return datos.decode("utf-8-sig"), datos.startswith(b"\xef\xbb\xbf")
    except UnicodeDecodeError:
        return datos.decode("cp1252", errors="replace"), False


def _delim(lineas):
    return ";" if any(";" in l for l in lineas) else ("\t" if any("\t" in l for l in lineas) else ",")


def detectar_tipo(doc):
    """Tipo de estructura de un documento leído sin tipo, como el despachador (PROYECTO/tipo o el encabezado de APOYOS)."""
    for b in doc["bloques"]:
        if b["t"] == "PROYECTO":
            for f in b["filas"]:
                if f["c"] and _norm(f["c"][0]) == "tipo" and len(f["c"]) > 1:
                    t = _norm(f["c"][1])
                    t = _TIPOS_ALIAS.get(t, t)
                    if t in ESQUEMAS:
                        return t
    for b in doc["bloques"]:
        if b["t"] == "APOYOS" and b["cab"]:
            cab = [_norm(c) for c in b["cab"]]
            if "ux" in cab and "uz" in cab:
                return "portico3d"
            if "ux" in cab:
                return "portico" if "phi" in cab else "reticulado"
            if "uz" in cab:
                return "emparrillado"
    for b in doc["bloques"]:
        if b["t"] in ("SOLDADURAS",) and b["cab"] and "barra" not in [_norm(c) for c in b["cab"]]:
            return "soldadura"
    return None


def leer_texto(texto: str, tipo=None, bom=False):
    """Texto CSV → documento.  Lanza ValueError si hay datos antes del primer título de bloque."""
    tit = _titulos(tipo)
    lineas = texto.splitlines()
    con_datos = [l for l in lineas if l.strip() and not l.lstrip().startswith("#") and l.replace(";", "").replace(",", "").replace("\t", "").strip()]
    delim = _delim(con_datos)
    doc = {"tipo": tipo, "pre": [], "bom": bom, "bloques": []}
    pend, actual = [], None
    for k, l in enumerate(lineas, 1):
        if not l.strip():
            continue
        if l.lstrip().startswith("#"):
            pend.append(l.strip())
            continue
        if not l.replace(";", "").replace(",", "").replace("\t", "").strip():
            continue
        celdas = [c.strip() for c in next(csv.reader([l], delimiter=delim))]
        while celdas and celdas[-1] == "":
            celdas.pop()
        if len(celdas) == 1 and _norm(celdas[0]) in tit:
            actual = {"t": tit[_norm(celdas[0])], "antes": pend, "cab": None, "filas": [], "fin": []}
            pend = []
            if actual["t"] != "PROYECTO":
                actual["_espera_cab"] = True
            doc["bloques"].append(actual)
            continue
        if actual is None:
            raise ValueError(f"Línea {k}: hay datos antes del primer título de bloque")
        if actual.pop("_espera_cab", False):
            actual["cab"] = celdas
            actual["antes_cab"] = pend
            pend = []
            continue
        actual["filas"].append({"c": celdas, "n": pend})
        pend = []
    if actual is None:
        doc["pre"] = pend
    else:
        actual["fin"] = pend
    for b in doc["bloques"]:
        b.pop("_espera_cab", None)
        if b["cab"] is not None:
            n = len(b["cab"])
            for f in b["filas"]:
                f["c"] = f["c"] + [""] * (n - len(f["c"]))
    # los comentarios antes del encabezado se conservan junto al título
    for b in doc["bloques"]:
        extra = b.pop("antes_cab", [])
        if extra:
            b["antes_cab"] = extra
    if doc["tipo"] is None:
        doc["tipo"] = detectar_tipo(doc)
    return doc


def leer_archivo(ruta, tipo=None):
    from pathlib import Path
    texto, bom = decodificar(Path(ruta).read_bytes())
    doc = leer_texto(texto, tipo, bom)
    if tipo is None and doc["tipo"] in ESQUEMAS:                       # releer con los títulos del tipo detectado
        doc = leer_texto(texto, doc["tipo"], bom)
    return doc


def _requeridas(tipo, t):
    """Columnas que se escriben siempre en el encabezado de un bloque."""
    b = bloque_de(tipo, t) if tipo in ESQUEMAS else None
    if b is None:
        return []
    return list(b["min"]) if b.get("min") is not None else [c["n"] for c in b["cols"]]


def encabezado(doc, b):
    """Encabezado a escribir: el que ya tenía el bloque más las columnas exigidas por el cargador que falten."""
    cab = list(b["cab"] or [])
    bajos = [c.lower() for c in cab]
    for c in _requeridas(doc["tipo"], b["t"]):
        if c.lower() not in bajos:
            cab.append(c)
            bajos.append(c.lower())
    return cab


def a_texto(doc):
    """Documento → (texto CSV, mapa {nº de línea: (título del bloque, índice de fila | -1 = título o encabezado)})."""
    sal, mapa = [], {}

    def linea(txt, ref):
        sal.append(txt)
        mapa[len(sal)] = ref

    def fila_csv(celdas):
        buf = io.StringIO()
        csv.writer(buf, delimiter=";", lineterminator="").writerow(celdas)
        return buf.getvalue()

    for c in doc.get("pre", []):
        linea(c, None)
    for b in doc["bloques"]:
        propio = b["t"] == "PROYECTO"
        filas = [f for f in b["filas"] if any(str(x).strip() for x in f["c"])]
        if propio:
            filas = [f for f in filas if len(f["c"]) >= 2 and str(f["c"][1]).strip()]       # claves sin valor no se escriben
        usadas = {id(f) for f in filas}
        obligatorio = bool(bloque_de(doc["tipo"], b["t"]) and bloque_de(doc["tipo"], b["t"])["ob"]) if doc["tipo"] in ESQUEMAS else False
        if not filas and not obligatorio and not b.get("antes") and not b.get("fin"):
            continue
        if sal:
            linea("", None)
        for c in b.get("antes", []):
            linea(c, (b["t"], -1))
        linea(b["t"], (b["t"], -1))
        if not propio:
            cab = encabezado(doc, b)
            for c in b.get("antes_cab", []):
                linea(c, (b["t"], -1))
            linea(fila_csv(cab), (b["t"], -1))
        for k, f in enumerate(b["filas"]):
            if id(f) not in usadas:
                continue
            for c in f.get("n", []):
                linea(c, (b["t"], k))
            celdas = list(f["c"])
            if not propio:
                celdas += [""] * (len(cab) - len(celdas))
            while celdas and str(celdas[-1]).strip() == "":
                celdas.pop()
            linea(fila_csv([str(x) for x in celdas]), (b["t"], k))
        for c in b.get("fin", []):
            linea(c, (b["t"], -1))
    return "\n".join(sal) + "\n", mapa


def doc_nuevo(tipo):
    """Documento vacío de un tipo: PROYECTO con el tipo y los bloques obligatorios con su encabezado."""
    if tipo not in ESQUEMAS:
        raise ValueError(f"tipo desconocido '{tipo}'")
    doc = {"tipo": tipo, "pre": [], "bom": False, "bloques": []}
    for b in ESQUEMAS[tipo]["bloques"]:
        if b["t"] == "PROYECTO":
            filas = [{"c": ["tipo", tipo], "n": []}]
            doc["bloques"].append({"t": "PROYECTO", "antes": [], "cab": None, "filas": filas, "fin": []})
        elif b["ob"]:
            cab = list(b["min"]) if b.get("min") is not None else [c["n"] for c in b["cols"]]
            doc["bloques"].append({"t": b["t"], "antes": [], "cab": cab, "filas": [], "fin": []})
    return doc
