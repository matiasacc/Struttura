"""Lectura y validación del archivo CSV de PÓRTICO ESPACIAL (3D).  Mismo formato de bloques que los otros programas.

    PROYECTO   proyecto;...   unidad_fuerza;N   unidad_longitud;mm   tipo;portico3d
    NODOS      id;x;y;z
    MATERIALES id;E;G;nu;fy;sadm;alfa [;sut;suc;teoria;rho]   (G, o bien nu: G = E / 2(1+nu))
                                                teoria: vm | tresca | rankine | mohr | mohrmod   (rho = densidad en kg/m³, para el peso propio)
    SECCIONES  id;tipo;...                      tipos: generica (A;Iy;Iz;J [;cy;cz;Wt]), tubo (d;t), circular (d),
                                                rectangular (b;h), rect_hueca (b;h;t)
    BARRAS     id;nodo_i;nodo_j;material;seccion [;rx;ry;rz] [;giro] [;art_i;art_j] [;pandeo]
                                                art_i / art_j: articulación en ese extremo.  1 = rótula esférica (libera My y Mz;
                                                se transmiten N, Vy, Vz y T);  o my / mz / t combinados con '+'  (ej.: my+t)
    APOYOS     nodo;ux;uy;uz;phix;phiy;phiz     (1 = restringido)
    RESORTES   nodo;kx;ky;kz;kphix;kphiy;kphiz  (ejes globales)
    RESORTES INCLINADOS  nodo;k;dx;dy;dz;ax;ay;az  (resorte lineal en una dirección cualquiera, a tierra;
               dirección = vector dx;dy;dz  o  ángulos ax;ay;az que forma con X, Y, Z)
    CARGAS     caso;nodo;Fx;Fy;Fz;Mx;My;Mz      (ejes globales)
    CARGAS EN BARRAS   caso;barra;tipo;valor;valor2;a      (tipos en cargas_barra.py)
    DESPLAZAMIENTOS PREFIJADOS   caso;nodo;ux;uy;uz;phix;phiy;phiz
    SOLDADURAS  id;barra;extremo;disposicion;b;d;...;electrodo;[w]   (ver soldaduras.py)    ELECTRODOS  id;sut;sy;tau_adm (opcional)
    COMBINACIONES      combinacion;caso;factor
    PROYECTO (claves opcionales)   peso_propio;<caso>   agrega el peso propio de todas las barras al caso <caso> (usa rho del material)
                                   gravedad;-z          dirección de la gravedad en ejes globales (±x, ±y, ±z; por defecto -z)

Ejes de la barra: x de i a j.  z local por defecto = +Z global (proyectado); en barras verticales, +X global.
Con rx;ry;rz se indica hacia dónde apunta z local (vector en globales); 'giro' rota la sección alrededor de x (grados).
Sección: Iy = inercia para flexión alrededor de y local (deflexión en z), Iz = alrededor de z local (deflexión en y).
En rectangular: b es la medida según y local y h según z local.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from ..pandeo import VALORES as PANDEO_VALORES, codigo as pandeo_codigo

from struttura.emparrillado.entrada import ErrorDeEntrada, _norm, _num, _partir_bloques, _tabla
from struttura.emparrillado.secciones import crear_seccion

from .barra import (condensar, descripcion_articulacion, gdl_liberados, parsear_articulacion, rigidez_global,
                    rigidez_local, terna_local)
from .cargas_barra import TIPOS as TIPOS_CARGA, agregar_longitud, convertir

NOMBRES_GDL = ("ux", "uy", "uz", "φx", "φy", "φz")
TITULOS = ["PROYECTO", "NODOS", "MATERIALES", "SECCIONES", "BARRAS", "APOYOS", "RESORTES", "RESORTES INCLINADOS", "CARGAS",
           "CARGAS EN BARRAS", "DESPLAZAMIENTOS PREFIJADOS", "COMBINACIONES", "PUNTOS DE TENSION", "SOLDADURAS", "ELECTRODOS"]
OBLIGATORIOS = ["NODOS", "MATERIALES", "SECCIONES", "BARRAS", "APOYOS"]

__all__ = ["ErrorDeEntrada", "cargar_modelo", "Modelo", "Barra", "Nodo", "NOMBRES_GDL"]


@dataclass
class Nodo:
    id: str
    x: float
    y: float
    z: float

    @property
    def p(self):
        return np.array([self.x, self.y, self.z])


@dataclass
class Material:
    id: str
    E: float
    G: float
    fy: float | None
    sadm: float | None
    alfa: float | None
    sut: float | None = None     # resistencia a tracción (materiales frágiles)
    suc: float | None = None     # resistencia a compresión (por defecto = sut)
    teoria: str = "vm"           # vm | tresca | rankine | mohr | mohrmod
    rho: float | None = None     # densidad [kg/m³] (peso propio)
    fuente: str | None = None    # si vino de la biblioteca: de qué ficha


@dataclass
class Seccion3D:
    id: str
    descripcion: str
    A: float
    Iy: float
    Iz: float
    J: float
    cy: float | None = None     # distancia máxima a la fibra extrema según y local
    cz: float | None = None
    Wt: float | None = None     # módulo resistente a torsión (tau = T/Wt)
    circular: bool = False
    tipo: str = "generica"
    dim: dict = field(default_factory=dict)     # d, t, b, h según el tipo
    pared: object = None        # ParedDelgada (perfiles abiertos de pared delgada), si corresponde


@dataclass
class Barra:
    id: str
    i: int
    j: int
    mat: Material
    sec: Seccion3D
    L: float
    R: np.ndarray                  # 3×3 global → local (filas ex, ey, ez)
    ref_auto: bool = True
    art_i: str = ""                # giros liberados en el extremo i: letras de 't', 'y', 'z' ('' = rígido)
    art_j: str = ""
    pandeo: str = "art-art"        # condición de extremos para el pandeo de Euler (ver struttura/pandeo.py)

    def __post_init__(self):
        self.k_local = rigidez_local(self.mat.E, self.mat.G, self.sec.A, self.sec.Iy, self.sec.Iz, self.sec.J, self.L)
        self.rel = gdl_liberados(self.art_i, self.art_j)
        if self.rel:
            kBB = self.k_local[np.ix_(self.rel, self.rel)]
            if np.linalg.matrix_rank(kBB, tol=1e-9 * np.abs(kBB).max()) < len(self.rel):
                raise ValueError(f"las articulaciones pedidas dejan a la barra '{self.id}' como un mecanismo "
                                 "(p. ej. torsión liberada en los dos extremos)")
        self.k_cond, _ = condensar(self.k_local, None, self.rel)       # matriz que entra al ensamblaje
        self.k_global = rigidez_global(self.k_cond, self.R)

    @property
    def articulada(self) -> bool:
        return bool(self.rel)

    @property
    def ex(self):
        return self.R[0]


@dataclass
class Modelo:
    archivo: Path
    config: dict
    nodos: list
    barras: list
    materiales: dict
    secciones: dict
    restr: np.ndarray                 # (n,6) bool
    resortes: np.ndarray              # (n,6)
    casos: dict                       # nombre -> (n,6) fuerzas nodales
    prefij: dict                      # nombre -> (n,6)
    cargas_barra: dict                # nombre -> {idx_barra: [cargas locales]}
    cargas_barra_orig: dict           # nombre -> [(barra_id, tipo, valor, valor2, a)]  (para informar)
    combinaciones: dict
    avisos: list = field(default_factory=list)
    puntos: list = field(default_factory=list)   # [{"id", "barra"(idx), "x", "y", "z", "caso"|None}]
    peso_propio: dict | None = None              # {"caso", "gravedad", "peso" (fuerza), "masa" [kg]} si se pidió peso propio
    soldaduras: list = field(default_factory=list)   # [soldadura.verificar.Soldadura] (bloque SOLDADURAS)
    electrodos: dict = field(default_factory=dict)   # electrodos propios {id: (sut, sy, tau_adm)} en MPa
    resortes_incl: list = field(default_factory=list)   # [{"nodo": idx, "id", "k", "d": (dx, dy, dz) unitario}]  resortes lineales a tierra en dirección cualquiera

    @property
    def n(self) -> int:
        return len(self.nodos)


# --------------------------------------------------------------------------
def cargar_modelo(ruta) -> Modelo:
    ruta = Path(ruta)
    if not ruta.is_file():
        raise ErrorDeEntrada(f"No se encuentra el archivo '{ruta}'")
    bloques = _partir_bloques(ruta, TITULOS)
    faltan = [t for t in OBLIGATORIOS if _norm(t) not in bloques]
    if faltan:
        raise ErrorDeEntrada(f"Faltan bloques obligatorios: {', '.join(faltan)}.  Bloques encontrados: "
                             f"{', '.join(b['titulo'] for b in bloques.values()) or 'ninguno'}")
    avisos: list[str] = []
    _avisar_columnas(bloques, avisos)
    config = _leer_config(bloques, ruta, avisos)
    nodos, idx = _leer_nodos(bloques)
    materiales = _leer_materiales(bloques, avisos, config)
    secciones = _leer_secciones(bloques, config, avisos)
    barras = _leer_barras(bloques, nodos, idx, materiales, secciones, avisos)
    restr = _leer_bool6(bloques, "APOYOS", nodos, idx, ("ux", "uy", "uz", "phix", "phiy", "phiz"))
    resortes = _leer_resortes(bloques, nodos, idx)
    incl = _leer_resortes_incl(bloques, nodos, idx, avisos)
    if not restr.any() and not resortes.any() and not incl:
        raise ErrorDeEntrada("No hay ningún apoyo: ni GDL restringidos (APOYOS) ni resortes (RESORTES, RESORTES INCLINADOS)")
    casos = _leer_cargas(bloques, nodos, idx)
    cargas_barra, orig = _leer_cargas_barra(bloques, barras, avisos)
    peso = _peso_propio(config, barras, cargas_barra, orig)
    prefij = _leer_prefijados(bloques, nodos, idx, restr)
    for d in (cargas_barra, prefij):
        for nombre in d:
            casos.setdefault(nombre, np.zeros((len(nodos), 6)))
    for nombre in casos:
        prefij.setdefault(nombre, np.zeros((len(nodos), 6)))
        cargas_barra.setdefault(nombre, {})
        orig.setdefault(nombre, [])
    if not casos:
        raise ErrorDeEntrada("No hay ningún caso de carga (CARGAS, CARGAS EN BARRAS y "
                             "DESPLAZAMIENTOS PREFIJADOS no tienen filas)")
    combos = _leer_combinaciones(bloques, casos)
    puntos = _leer_puntos(bloques, barras, casos, combos)
    from .soldaduras import leer as _leer_soldaduras
    soldaduras, electrodos = _leer_soldaduras(bloques, barras, config)
    usados = {b.i for b in barras} | {b.j for b in barras}
    for k, nd in enumerate(nodos):
        if k not in usados:
            avisos.append(f"El nodo {nd.id} no está conectado a ninguna barra.")
    return Modelo(ruta, config, nodos, barras, materiales, secciones, restr, resortes, casos, prefij,
                  cargas_barra, orig, combos, avisos, puntos, peso, soldaduras, electrodos, incl)


_COLUMNAS = {
    "NODOS": ("id", "x", "y", "z"),
    "MATERIALES": ("id", "e", "g", "nu", "fy", "sadm", "alfa", "sut", "suc", "teoria", "rho", "lib"),
    "SECCIONES": ("id", "tipo", "lib", "a", "iy", "iz", "j", "cy", "cz", "wt", "d", "t", "b", "h", "tf", "tw"),
    "BARRAS": ("id", "nodo_i", "nodo_j", "material", "seccion", "rx", "ry", "rz", "giro", "art_i", "art_j", "pandeo"),
    "APOYOS": ("nodo", "ux", "uy", "uz", "phix", "phiy", "phiz"),
    "RESORTES": ("nodo", "kx", "ky", "kz", "kphix", "kphiy", "kphiz"),
    "RESORTES INCLINADOS": ("nodo", "k", "dx", "dy", "dz", "ax", "ay", "az"),
    "CARGAS": ("caso", "nodo", "fx", "fy", "fz", "mx", "my", "mz"),
    "CARGAS EN BARRAS": ("caso", "barra", "tipo", "valor", "valor2", "a"),
    "DESPLAZAMIENTOS PREFIJADOS": ("caso", "nodo", "ux", "uy", "uz", "phix", "phiy", "phiz"),
    "COMBINACIONES": ("combinacion", "caso", "factor"),
    "PUNTOS DE TENSION": ("id", "barra", "x", "y", "z", "caso"),
    "SOLDADURAS": ("id", "tipo", "esp", "barra", "extremo", "disposicion", "b", "d", "arcos", "segmentos", "oy", "oz", "electrodo", "w", "sy_base", "lib", "t_gruesa", "t_fina"),
    "ELECTRODOS": ("id", "sut", "sy", "tau_adm", "lib"),
}
_COLUMNAS_LIBRES = ("descripcion", "descripción", "desc", "nota", "notas", "comentario", "comentarios", "obs", "observaciones")


def _avisar_columnas(bloques, avisos):
    """Avisa de las columnas que el programa no usa (por ejemplo un error de tipeo en el encabezado)."""
    for titulo, conocidas in _COLUMNAS.items():
        b = bloques.get(_norm(titulo))
        if not b or not b["filas"]:
            continue
        for c in b["filas"][0][1]:
            c = c.strip().lower()
            if c and c not in conocidas and c not in _COLUMNAS_LIBRES:
                avisos.append(f"Bloque {titulo}: la columna '{c}' no se usa (se ignora).  Columnas válidas: {', '.join(conocidas)}.")


# unidades → factor a N y a m (para el peso propio)
_U_FUERZA = {"n": 1.0, "kn": 1e3, "mn": 1e6, "kgf": 9.80665, "tf": 9806.65, "lbf": 4.4482216, "kip": 4448.2216}
_U_LONG = {"mm": 1e-3, "cm": 1e-2, "m": 1.0, "in": 0.0254, "ft": 0.3048}
G_STD = 9.80665


def _peso_propio(config, barras, cargas_barra, orig):
    """Si PROYECTO trae peso_propio;<caso>, agrega a ese caso una carga distribuida uniforme (ρ·g·A) en cada barra.
    ρ en kg/m³ (columna rho de MATERIALES); se convierte a las unidades del modelo."""
    caso = (config.get("peso_propio") or "").strip()
    if not caso:
        return None
    uf, ul = config["unidad_fuerza"].strip().lower(), config["unidad_longitud"].strip().lower()
    if uf not in _U_FUERZA or ul not in _U_LONG:
        raise ErrorDeEntrada(f"Peso propio: no sé convertir las unidades '{config['unidad_fuerza']}' / '{config['unidad_longitud']}' "
                             f"(admitidas: fuerza {', '.join(_U_FUERZA)};  longitud {', '.join(_U_LONG)}).  "
                             "O bien cargá el peso propio a mano con CARGAS EN BARRAS.")
    sin = sorted({b.mat.id for b in barras if b.mat.rho is None})
    if sin:
        raise ErrorDeEntrada(f"Peso propio: falta la columna rho (densidad en kg/m³) en el/los material(es): {', '.join(sin)}")
    g = config["gravedad"].replace("+", "")
    signo, eje = (-1.0 if g.startswith("-") else 1.0), g[-1]
    tipo = "qg" + eje
    fF, fL = _U_FUERZA[uf], _U_LONG[ul]
    peso, masa = 0.0, 0.0
    for k, b in enumerate(barras):
        w = b.mat.rho * G_STD / fF * fL**3            # peso específico en [fuerza/longitud³] del modelo
        q = signo * w * b.sec.A
        c = agregar_longitud(convertir(tipo, q, q, None, b.R), b.L)
        cargas_barra.setdefault(caso, {}).setdefault(k, []).append(c)
        orig.setdefault(caso, []).append((b.id, tipo, q, q, None))
        peso += w * b.sec.A * b.L
        masa += b.mat.rho * b.sec.A * b.L * fL**3
    return {"caso": caso, "gravedad": config["gravedad"], "peso": peso, "masa": masa}


def _leer_config(bloques, ruta, avisos):
    config = {"proyecto": ruta.stem, "autor": "", "unidad_fuerza": "N", "unidad_longitud": "mm",
              "escala_deformada": None, "csv_salida": "excel_es", "tipo": "portico3d", "anexo_matrices": "si", "corte_tensiones": "si",
              "peso_propio": "", "gravedad": "-z", "escala_diagramas": "barra"}
    b = bloques.get("proyecto")
    for n, celdas in (b["filas"] if b else []):
        k = celdas[0].strip().lower()
        v = celdas[1].strip() if len(celdas) > 1 else ""
        if k not in config:
            avisos.append(f"Bloque PROYECTO, línea {n}: clave desconocida '{k}' (ignorada).")
            continue
        if k == "escala_deformada":
            v = None if v.lower() in ("", "auto") else _num(v, "PROYECTO", n, k)
        elif k in ("csv_salida", "tipo", "anexo_matrices", "corte_tensiones", "gravedad", "escala_diagramas"):
            v = v.lower().replace(" ", "")
        config[k] = v
    if config["tipo"] not in ("portico3d", "espacial", "3d"):
        raise ErrorDeEntrada("Bloque PROYECTO: 'tipo' debe ser portico3d (para este programa)")
    config["tipo"] = "portico3d"
    if config["anexo_matrices"] not in ("auto", "si", "no"):
        raise ErrorDeEntrada("Bloque PROYECTO: 'anexo_matrices' debe ser si o no")
    if config["corte_tensiones"] not in ("si", "no"):
        raise ErrorDeEntrada("Bloque PROYECTO: 'corte_tensiones' debe ser si o no")
    if config["escala_diagramas"] not in ("barra", "global"):
        raise ErrorDeEntrada("Bloque PROYECTO: 'escala_diagramas' debe ser barra o global")
    if config["gravedad"] not in ("x", "y", "z", "+x", "+y", "+z", "-x", "-y", "-z"):
        raise ErrorDeEntrada("Bloque PROYECTO: 'gravedad' debe ser ±x, ±y o ±z (ejes globales; por defecto -z)")
    if config["csv_salida"] not in ("excel_es", "estandar"):
        raise ErrorDeEntrada("Bloque PROYECTO: 'csv_salida' debe ser excel_es o estandar")
    return config


def _leer_nodos(bloques):
    nodos, idx = [], {}
    for n, r in _tabla(bloques, "NODOS", ["id", "x", "y", "z"]):
        id_ = r["id"]
        if not id_:
            raise ErrorDeEntrada(f"Bloque NODOS, línea {n}: falta el id del nodo")
        if id_ in idx:
            raise ErrorDeEntrada(f"Bloque NODOS, línea {n}: el nodo '{id_}' está repetido")
        idx[id_] = len(nodos)
        nodos.append(Nodo(id_, *[_num(r[c], "NODOS", n, c) for c in ("x", "y", "z")]))
    if len(nodos) < 2:
        raise ErrorDeEntrada("Bloque NODOS: hacen falta al menos 2 nodos")
    return nodos, idx


def _de_biblioteca(lib, config, n, avisos, id_):
    """Valores de la ficha de la biblioteca convertidos a las unidades del modelo (MPa y kg/m³ -> unidades del modelo)."""
    from ..biblioteca.biblioteca import ErrorBiblioteca, datos
    uf, ul = config["unidad_fuerza"].strip().lower(), config["unidad_longitud"].strip().lower()
    if uf not in _U_FUERZA or ul not in _U_LONG:
        raise ErrorDeEntrada(f"Bloque MATERIALES, línea {n}: no sé convertir las unidades '{config['unidad_fuerza']}' / '{config['unidad_longitud']}' "
                             "para leer la biblioteca; cargá los valores a mano")
    try:
        d = datos(lib)
    except ErrorBiblioteca as e:
        raise ErrorDeEntrada(f"Bloque MATERIALES, línea {n}: {e}")
    k = 1e6 * _U_LONG[ul] ** 2 / _U_FUERZA[uf]                       # MPa -> fuerza/longitud² del modelo
    for c in ("E", "G", "fy", "sut"):
        if d[c] is not None:
            d[c] *= k
    avisos.append(f"Nota: Material '{id_}': datos de la biblioteca ({d['fuente']}); valores típicos de la ficha, no garantizados.")
    return d


def _leer_materiales(bloques, avisos, config=None):
    mats = {}
    for n, r in _tabla(bloques, "MATERIALES", ["id"]):
        id_ = r["id"]
        if id_ in mats:
            raise ErrorDeEntrada(f"Bloque MATERIALES, línea {n}: el material '{id_}' está repetido")
        lib = (r.get("lib") or "").strip()
        dl = _de_biblioteca(lib, config, n, avisos, id_) if lib else {}
        if not lib and "e" not in r:
            raise ErrorDeEntrada("Bloque MATERIALES: faltan las columnas ['e'].  Se puede completar con lib;<código de la biblioteca>")
        E = _num(r.get("e"), "MATERIALES", n, "E", obligatorio=not lib)
        if E is None:
            E = dl.get("E")
            if E is None:
                raise ErrorDeEntrada(f"Bloque MATERIALES, línea {n}: la ficha '{lib}' no trae módulo de elasticidad; cargá E a mano")
        G = _num(r.get("g"), "MATERIALES", n, "G", obligatorio=False)
        nu = _num(r.get("nu"), "MATERIALES", n, "nu", obligatorio=False)
        if G is None and nu is None:                                  # lo que cargó el usuario manda; la ficha completa lo que falta
            G, nu = dl.get("G"), dl.get("nu")
        if E <= 0:
            raise ErrorDeEntrada(f"Bloque MATERIALES, línea {n}: E debe ser > 0")
        if G is None:
            if nu is None:
                raise ErrorDeEntrada(f"Bloque MATERIALES, línea {n}: el pórtico espacial necesita G (o nu, "
                                     "con G = E/2(1+nu)) para la torsión")
            if not -1 < nu < 0.5:
                raise ErrorDeEntrada(f"Bloque MATERIALES, línea {n}: nu debe estar entre -1 y 0,5")
            G = E / (2 * (1 + nu))
        if G <= 0:
            raise ErrorDeEntrada(f"Bloque MATERIALES, línea {n}: G debe ser > 0")
        fy = _num(r.get("fy"), "MATERIALES", n, "fy", obligatorio=False)
        fy = dl.get("fy") if fy is None else fy
        sut = _num(r.get("sut"), "MATERIALES", n, "sut", obligatorio=False)
        sut = dl.get("sut") if sut is None else sut
        suc = _num(r.get("suc"), "MATERIALES", n, "suc", obligatorio=False)
        teoria = (r.get("teoria") or "").strip().lower()
        alias = {"": "", "vm": "vm", "mises": "vm", "von mises": "vm", "vonmises": "vm", "tresca": "tresca",
                 "rankine": "rankine", "mohr": "mohr", "mohr-coulomb": "mohr", "coulomb": "mohr",
                 "mohrmod": "mohrmod", "mohr modificado": "mohrmod", "mohr-modificado": "mohrmod",
                 "mohr_modificado": "mohrmod", "mohr mod": "mohrmod"}
        if teoria not in alias:
            raise ErrorDeEntrada(f"Bloque MATERIALES, línea {n}: teoria '{teoria}' desconocida (vm, tresca, rankine, mohr, mohrmod)")
        explicita = alias[teoria]
        teoria = explicita or ("vm" if fy is not None else ("rankine" if sut is not None else "vm"))
        if teoria in ("vm", "tresca") and fy is None and explicita:
            raise ErrorDeEntrada(f"Bloque MATERIALES, línea {n}: la teoría '{teoria}' necesita fy")
        if teoria in ("rankine", "mohr", "mohrmod") and sut is None:
            raise ErrorDeEntrada(f"Bloque MATERIALES, línea {n}: la teoría '{teoria}' necesita sut (resistencia a tracción)")
        if suc is None:
            suc = sut
        if teoria in ("mohr", "mohrmod") and suc < sut:
            avisos.append(f"Material '{id_}': suc ({suc:g}) < sut ({sut:g}); las teorías de Mohr suponen |σc| ≥ σt.")
        rho = _num(r.get("rho"), "MATERIALES", n, "rho", obligatorio=False)
        rho = dl.get("rho") if rho is None else rho
        if rho is not None and rho <= 0:
            raise ErrorDeEntrada(f"Bloque MATERIALES, línea {n}: rho (densidad en kg/m³) debe ser > 0")
        mats[id_] = Material(id_, E, G, fy, _num(r.get("sadm"), "MATERIALES", n, "sadm", obligatorio=False),
                             _num(r.get("alfa"), "MATERIALES", n, "alfa", obligatorio=False), sut, suc, teoria, rho, dl.get("fuente"))
    if not mats:
        raise ErrorDeEntrada("Bloque MATERIALES: no hay materiales")
    return mats


def _leer_secciones(bloques, config=None, avisos=None):
    secs = {}
    for n, r in _tabla(bloques, "SECCIONES", ["id", "tipo"]):
        id_ = r["id"]
        if id_ in secs:
            raise ErrorDeEntrada(f"Bloque SECCIONES, línea {n}: la sección '{id_}' está repetida")
        if r["tipo"].strip().lower() == "perfil":
            try:
                from ..biblioteca.biblioteca import ErrorBiblioteca
                from ..biblioteca.perfiles import expandir
                r = expandir(r, "3d", config or {"unidad_longitud": "mm"}, n, avisos if avisos is not None else [])
            except ErrorBiblioteca as e:
                raise ErrorDeEntrada(str(e))
        tipo = r["tipo"].strip().lower()
        v = lambda c, obl=False: _num(r.get(c), "SECCIONES", n, c, obligatorio=obl)
        try:
            if tipo == "generica":
                A, Iy, Iz, J = v("a", True), v("iy", True), v("iz", True), v("j", True)
                if min(A, Iy, Iz, J) <= 0:
                    raise ValueError("A, Iy, Iz y J deben ser > 0")
                s = Seccion3D(id_, "Sección genérica (datos cargados)", A, Iy, Iz, J, v("cy"), v("cz"), v("wt"), tipo="generica")
            elif tipo in ("tubo", "circular"):
                p = {"d": v("d", True), "t": v("t", tipo == "tubo")}
                b = crear_seccion(id_, tipo, {**p, "J": 1.0})
                s = Seccion3D(id_, b.descripcion, b.A, b.I, b.I, b.J, b.c, b.c, b.Wt, circular=True, tipo=tipo,
                              dim={"d": p["d"], "t": p["t"] or 0.0})
            elif tipo == "rectangular":
                bb, hh = v("b", True), v("h", True)
                b = crear_seccion(id_, tipo, {"b": bb, "h": hh})
                s = Seccion3D(id_, f"Maciza rectangular b={bb:g} (eje y) × h={hh:g} (eje z)", b.A,
                              bb * hh**3 / 12, hh * bb**3 / 12, b.J, bb / 2, hh / 2, b.Wt, tipo=tipo, dim={"b": bb, "h": hh})
            elif tipo == "rect_hueca":
                bb, hh, t = v("b", True), v("h", True), v("t", True)
                b = crear_seccion(id_, tipo, {"b": bb, "h": hh, "t": t})
                bi, hi = bb - 2 * t, hh - 2 * t
                s = Seccion3D(id_, f"Tubo rectangular b={bb:g} (eje y) × h={hh:g} (eje z) × t={t:g}", b.A,
                              b.I, (hh * bb**3 - hi * bi**3) / 12, b.J, bb / 2, hh / 2, b.Wt, tipo=tipo,
                              dim={"b": bb, "h": hh, "t": t})
            elif tipo in ("canal", "doble_t", "te", "z", "angular"):
                from .pared_delgada import ParedDelgada, perfil
                dims = {c: v(c) for c in ("h", "b", "t", "tf", "tw")}
                pd = ParedDelgada(perfil(tipo, dims))
                nombre = {"canal": "Canal (U)", "doble_t": "Doble T", "te": "Té", "z": "Z", "angular": "Ángulo (L)"}[tipo]
                dd = ", ".join(f"{c}={x:g}" for c, x in dims.items() if x is not None)
                ang = f"; ejes principales girados {math.degrees(pd.theta):.2f}° respecto del dibujo" if pd.theta else ""
                s = Seccion3D(id_, f"{nombre} de pared delgada abierta ({dd}, línea media){ang}", pd.A, pd.Iy, pd.Iz, pd.J,
                              pd.cy, pd.cz, pd.Wt, tipo=tipo, dim={k: x for k, x in dims.items() if x is not None}, pared=pd)
            else:
                raise ValueError(f"tipo de sección desconocido '{tipo}' (válidos: perfil, generica, tubo, circular, "
                                 "rectangular, rect_hueca, canal, doble_t, te, z, angular)")
        except ValueError as e:
            raise ErrorDeEntrada(f"Bloque SECCIONES, línea {n} (sección '{id_}'): {e}")
        if r.get("_perfil"):
            s.descripcion = r["_perfil"]
        secs[id_] = s
    if not secs:
        raise ErrorDeEntrada("Bloque SECCIONES: no hay secciones")
    return secs


def _leer_barras(bloques, nodos, idx, materiales, secciones, avisos):
    barras, ids = [], set()
    P = np.array([nd.p for nd in nodos])
    dim = max(np.ptp(P, axis=0).max(), 1.0)
    filas = _tabla(bloques, "BARRAS", ["id", "nodo_i", "nodo_j", "material", "seccion"])
    for n, r in filas:
        id_ = r["id"]
        if id_ in ids:
            raise ErrorDeEntrada(f"Bloque BARRAS, línea {n}: la barra '{id_}' está repetida")
        ids.add(id_)
        for campo in ("nodo_i", "nodo_j"):
            if r[campo] not in idx:
                raise ErrorDeEntrada(f"Bloque BARRAS, línea {n}: {campo} '{r[campo]}' no existe en NODOS")
        if r["material"] not in materiales:
            raise ErrorDeEntrada(f"Bloque BARRAS, línea {n}: material '{r['material']}' no existe en MATERIALES")
        if r["seccion"] not in secciones:
            raise ErrorDeEntrada(f"Bloque BARRAS, línea {n}: sección '{r['seccion']}' no existe en SECCIONES")
        i, j = idx[r["nodo_i"]], idx[r["nodo_j"]]
        if i == j:
            raise ErrorDeEntrada(f"Bloque BARRAS, línea {n}: la barra '{id_}' une un nodo consigo mismo")
        if np.linalg.norm(P[j] - P[i]) < 1e-9 * dim:
            raise ErrorDeEntrada(f"Bloque BARRAS, línea {n}: la barra '{id_}' tiene longitud nula")
        ref = [_num(r.get(c), "BARRAS", n, c, obligatorio=False) for c in ("rx", "ry", "rz")]
        if all(x is None for x in ref):
            ref = None
        elif any(x is None for x in ref):
            raise ErrorDeEntrada(f"Bloque BARRAS, línea {n}: el vector de referencia necesita rx, ry y rz")
        giro = _num(r.get("giro"), "BARRAS", n, "giro", obligatorio=False, defecto=0.0)
        try:
            R, L = terna_local(P[i], P[j], ref, giro)
        except ValueError as e:
            raise ErrorDeEntrada(f"Bloque BARRAS, línea {n} (barra '{id_}'): {e}")
        try:
            ai = parsear_articulacion(r.get("art_i"))
            aj = parsear_articulacion(r.get("art_j"))
            cod = pandeo_codigo(r.get("pandeo"))
            if cod is None:
                raise ErrorDeEntrada(f"Bloque BARRAS, línea {n}: pandeo '{r.get('pandeo')}' no es válido para la barra '{id_}'.  Valores: {PANDEO_VALORES}")
            barras.append(Barra(id_, i, j, materiales[r["material"]], secciones[r["seccion"]], L, R, ref is None, ai, aj, cod))
        except ValueError as e:
            raise ErrorDeEntrada(f"Bloque BARRAS, línea {n} (barra '{id_}'): {e}")
    if not barras:
        raise ErrorDeEntrada("Bloque BARRAS: no hay barras")
    return barras


def _fila_nodo(r, nodos, idx, ctx, n):
    if r["nodo"] not in idx:
        raise ErrorDeEntrada(f"Bloque {ctx}, línea {n}: el nodo '{r['nodo']}' no existe en NODOS")
    return idx[r["nodo"]]


def _leer_bool6(bloques, titulo, nodos, idx, cols):
    out = np.zeros((len(nodos), 6), dtype=bool)
    for n, r in _tabla(bloques, titulo, ["nodo"]):
        k = _fila_nodo(r, nodos, idx, titulo, n)
        for c, col in enumerate(cols):
            t = (r.get(col) or "").strip().lower()
            if t in ("1", "si", "sí", "s", "x", "true", "yes"):
                out[k, c] = True
            elif t not in ("", "0", "no", "n", "false", "-"):
                raise ErrorDeEntrada(f"Bloque {titulo}, línea {n}: '{t}' no es válido en '{col}' (usar 1 o 0)")
    return out


def _leer_vec6(bloques, titulo, cols, nodos, idx, extra=("caso",)):
    """Filas: lista de (caso, k, vec6 con NaN donde no hay dato)."""
    res = []
    for n, r in _tabla(bloques, titulo, list(extra) + ["nodo"], requerido=False) or []:
        k = _fila_nodo(r, nodos, idx, titulo, n)
        v = np.array([_num(r.get(c), titulo, n, c, obligatorio=False, defecto=np.nan) for c in cols], float)
        res.append((n, r.get("caso"), k, v))
    return res


def _leer_resortes(bloques, nodos, idx):
    k6 = np.zeros((len(nodos), 6))
    for n, _, k, v in _leer_vec6(bloques, "RESORTES", ("kx", "ky", "kz", "kphix", "kphiy", "kphiz"), nodos, idx, extra=()):
        if np.nanmin(np.where(np.isnan(v), 0, v)) < 0:
            raise ErrorDeEntrada(f"Bloque RESORTES, línea {n}: las rigideces deben ser >= 0")
        k6[k] += np.where(np.isnan(v), 0.0, v)
    return k6


def _leer_resortes_incl(bloques, nodos, idx, avisos):
    """RESORTES INCLINADOS:  nodo;k;dx;dy;dz;ax;ay;az.  Resorte lineal a tierra con rigidez k [fuerza/longitud] en la
    dirección d (unitaria): aporta k·d·dᵀ a (ux, uy, uz) del nodo.  La dirección se da con el vector (dx;dy;dz) o con los
    ángulos ax, ay, az [°] que forma con los ejes X, Y, Z (cosenos directores: cos²ax + cos²ay + cos²az = 1).
    Con dos ángulos el tercero se calcula (componente >= 0).  Se pueden poner varios resortes en un mismo nodo."""
    ctx = "RESORTES INCLINADOS"
    out = []
    for n, r in _tabla(bloques, ctx, ["nodo", "k"], requerido=False) or []:
        k = _fila_nodo(r, nodos, idx, ctx, n)
        kk = _num(r["k"], ctx, n, "k")
        if kk <= 0:
            raise ErrorDeEntrada(f"Bloque {ctx}, línea {n}: k debe ser > 0")
        nan = float("nan")
        v = [_num(r.get(c), ctx, n, c, obligatorio=False, defecto=nan) for c in ("dx", "dy", "dz")]
        a = [_num(r.get(c), ctx, n, c, obligatorio=False, defecto=nan) for c in ("ax", "ay", "az")]
        hay_v, hay_a = any(not np.isnan(x) for x in v), any(not np.isnan(x) for x in a)
        if hay_v and hay_a:
            raise ErrorDeEntrada(f"Bloque {ctx}, línea {n}: dar la dirección con el vector (dx;dy;dz) o con los ángulos (ax;ay;az), no con ambos")
        if not hay_v and not hay_a:
            raise ErrorDeEntrada(f"Bloque {ctx}, línea {n}: falta la dirección (dx;dy;dz) o los ángulos (ax;ay;az)")
        if hay_v:
            d = np.array([0.0 if np.isnan(x) else x for x in v])
            nd = float(np.linalg.norm(d))
            if nd == 0:
                raise ErrorDeEntrada(f"Bloque {ctx}, línea {n}: el vector de dirección es nulo")
            d = d / nd
        else:
            falt = [i for i, x in enumerate(a) if np.isnan(x)]
            if len(falt) > 1:
                raise ErrorDeEntrada(f"Bloque {ctx}, línea {n}: con ángulos hay que dar al menos dos de los tres (ax;ay;az)")
            c = [np.cos(np.radians(x)) if not np.isnan(x) else np.nan for x in a]
            if falt:
                resto = 1.0 - sum(x * x for x in c if not np.isnan(x))
                if resto < -1e-9:
                    raise ErrorDeEntrada(f"Bloque {ctx}, línea {n}: los dos ángulos no son compatibles (cos² ax + cos² ay + cos² az = 1)")
                c[falt[0]] = float(np.sqrt(max(resto, 0.0)))
                ang = float(np.degrees(np.arccos(c[falt[0]])))
                avisos.append(f"Nota: RESORTES INCLINADOS, línea {n}: el ángulo {'xyz'[falt[0]]} se calculó = {ang:.4g}° (cos² ax + cos² ay + cos² az = 1; componente ≥ 0)")
            else:
                sc = sum(x * x for x in c)
                if abs(sc - 1.0) > 1e-3:
                    raise ErrorDeEntrada(f"Bloque {ctx}, línea {n}: los tres ángulos no cumplen cos² ax + cos² ay + cos² az = 1 (da {sc:.4g})")
            d = np.array(c) / np.linalg.norm(c)
        out.append({"nodo": k, "id": r["nodo"], "k": kk, "d": tuple(float(x) for x in d)})
    return out


def _leer_cargas(bloques, nodos, idx):
    casos: dict = {}
    for n, caso, k, v in _leer_vec6(bloques, "CARGAS", ("fx", "fy", "fz", "mx", "my", "mz"), nodos, idx):
        if not caso:
            raise ErrorDeEntrada(f"Bloque CARGAS, línea {n}: falta el nombre del caso")
        casos.setdefault(caso, np.zeros((len(nodos), 6)))
        casos[caso][k] += np.where(np.isnan(v), 0.0, v)
    return casos


def _leer_prefijados(bloques, nodos, idx, restr):
    pref: dict = {}
    for n, caso, k, v in _leer_vec6(bloques, "DESPLAZAMIENTOS PREFIJADOS", ("ux", "uy", "uz", "phix", "phiy", "phiz"),
                                    nodos, idx):
        if not caso:
            raise ErrorDeEntrada(f"Bloque DESPLAZAMIENTOS PREFIJADOS, línea {n}: falta el nombre del caso")
        for c in range(6):
            if not np.isnan(v[c]) and v[c] != 0 and not restr[k, c]:
                raise ErrorDeEntrada(f"Bloque DESPLAZAMIENTOS PREFIJADOS, línea {n}: se prefija {NOMBRES_GDL[c]}="
                                     f"{v[c]:g} en el nodo '{nodos[k].id}', pero ese GDL no está restringido en APOYOS")
        pref.setdefault(caso, np.zeros((len(nodos), 6)))
        pref[caso][k] += np.where(np.isnan(v), 0.0, v)
    return pref


def _leer_cargas_barra(bloques, barras, avisos):
    ids = {b.id: k for k, b in enumerate(barras)}
    out: dict = {}
    orig: dict = {}
    for n, r in _tabla(bloques, "CARGAS EN BARRAS", ["caso", "barra", "tipo", "valor"], requerido=False) or []:
        caso = r["caso"]
        if not caso:
            raise ErrorDeEntrada(f"Bloque CARGAS EN BARRAS, línea {n}: falta el nombre del caso")
        if r["barra"] not in ids:
            raise ErrorDeEntrada(f"Bloque CARGAS EN BARRAS, línea {n}: la barra '{r['barra']}' no existe")
        tipo = r["tipo"].strip()
        tt = {t.lower(): t for t in TIPOS_CARGA}
        if tipo.lower() not in tt:
            raise ErrorDeEntrada(f"Bloque CARGAS EN BARRAS, línea {n}: tipo '{tipo}' desconocido.  Tipos válidos: "
                                 f"{', '.join(TIPOS_CARGA)}")
        tipo = tt[tipo.lower()]
        k = ids[r["barra"]]
        b = barras[k]
        v1 = _num(r["valor"], "CARGAS EN BARRAS", n, "valor")
        v2 = _num(r.get("valor2"), "CARGAS EN BARRAS", n, "valor2", obligatorio=False)
        a = _num(r.get("a"), "CARGAS EN BARRAS", n, "a", obligatorio=False)
        if tipo[0] == "q":
            a = None
        else:
            if a is None:
                raise ErrorDeEntrada(f"Bloque CARGAS EN BARRAS, línea {n}: la carga puntual '{tipo}' necesita la "
                                     "columna 'a' (distancia desde el nudo i)")
            if not 0 <= a <= b.L:
                raise ErrorDeEntrada(f"Bloque CARGAS EN BARRAS, línea {n}: a = {a:g} está fuera de la barra "
                                     f"(longitud {b.L:g})")
            v2 = None
        c = agregar_longitud(convertir(tipo, v1, v2, a, b.R), b.L)
        out.setdefault(caso, {}).setdefault(k, []).append(c)
        orig.setdefault(caso, []).append((b.id, tipo, v1, v2, a))
    return out, orig


def _leer_combinaciones(bloques, casos):
    filas = _tabla(bloques, "COMBINACIONES", ["combinacion", "caso", "factor"], requerido=False)
    combos: dict = {}
    for n, r in filas or []:
        nombre = r["combinacion"]
        if nombre in casos:
            raise ErrorDeEntrada(f"Bloque COMBINACIONES, línea {n}: '{nombre}' ya es un caso de carga")
        if r["caso"] not in casos:
            raise ErrorDeEntrada(f"Bloque COMBINACIONES, línea {n}: el caso '{r['caso']}' no existe")
        combos.setdefault(nombre, []).append((r["caso"], _num(r["factor"], "COMBINACIONES", n, "factor")))
    if not combos and len(casos) > 1 and "TOTAL" not in casos:   # estado total: suma de todos los casos (factor 1), solo si no hay combinaciones propias
        combos["TOTAL"] = [(c, 1.0) for c in casos]
    return combos


def _leer_puntos(bloques, barras, casos, combos):
    """PUNTOS DE TENSION:  id;barra;x;y;z[;caso]   x = distancia desde el nudo i; (y, z) = coordenadas locales en la
    sección respecto del baricentro; caso vacío = en todos los casos y combinaciones."""
    ids = {b.id: k for k, b in enumerate(barras)}
    out, usados = [], set()
    for n, r in _tabla(bloques, "PUNTOS DE TENSION", ["barra", "x"], requerido=False) or []:
        pid = r.get("id") or f"P{len(out) + 1}"
        if pid in usados:
            raise ErrorDeEntrada(f"Bloque PUNTOS DE TENSION, línea {n}: el punto '{pid}' está repetido")
        usados.add(pid)
        if r["barra"] not in ids:
            raise ErrorDeEntrada(f"Bloque PUNTOS DE TENSION, línea {n}: la barra '{r['barra']}' no existe")
        b = barras[ids[r["barra"]]]
        x = _num(r["x"], "PUNTOS DE TENSION", n, "x")
        if not 0 <= x <= b.L:
            raise ErrorDeEntrada(f"Bloque PUNTOS DE TENSION, línea {n}: x = {x:g} está fuera de la barra (longitud {b.L:g})")
        y = _num(r.get("y"), "PUNTOS DE TENSION", n, "y", obligatorio=False, defecto=0.0)
        z = _num(r.get("z"), "PUNTOS DE TENSION", n, "z", obligatorio=False, defecto=0.0)
        caso = (r.get("caso") or "").strip() or None
        if caso and caso not in casos and caso not in combos:
            raise ErrorDeEntrada(f"Bloque PUNTOS DE TENSION, línea {n}: el caso '{caso}' no existe")
        out.append({"id": pid, "barra": ids[r["barra"]], "x": x, "y": y, "z": z, "caso": caso})
    return out
