"""Lectura y validación del archivo CSV de PÓRTICO PLANO (un solo archivo, bloques con título).

Cada bloque empieza con una línea que contiene solamente su título y sigue con la fila de
encabezados y las filas de datos.  Las líneas en blanco y las que empiezan con '#' se ignoran.

    NODOS
    id;x;y
    1;0;0

Títulos válidos:  PROYECTO, NODOS, MATERIALES, SECCIONES, BARRAS, APOYOS, RESORTES, RESORTES INCLINADOS,
                  CARGAS, CARGAS EN BARRAS, DESPLAZAMIENTOS PREFIJADOS, DESAJUSTE DE RESORTES, COMBINACIONES
Obligatorios:     NODOS, MATERIALES, SECCIONES, BARRAS, APOYOS
                  (y al menos una carga: en CARGAS, en CARGAS EN BARRAS o desplazamientos prefijados)

GDL por nodo: ux, uy, φ (φ positivo antihorario).  Separador ';' con coma decimal (Excel en español)
o ',' con punto decimal: se detecta solo.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from struttura.emparrillado.entrada import ErrorDeEntrada, _flag, _norm, _num, _partir_bloques, _tabla, suprimir_barras, avisar_columnas
from struttura.emparrillado.secciones import Seccion, crear_seccion

from ..falla_plana import resolver_teoria
from ..pandeo import VALORES as PANDEO_VALORES, codigo as pandeo_codigo
from .barra import condensar, liberados, rigidez_local
from .cargas_barra import CargaBarra, TIPOS as TIPOS_CARGA, descomponer

NOMBRES_GDL = ("ux", "uy", "φ")

_COLUMNAS = {
    "SOLDADURAS": ("id", "tipo", "esp", "barra", "extremo", "disposicion", "b", "d", "arcos", "segmentos", "oy", "oz", "electrodo", "w", "sy_base", "lib", "t_gruesa", "t_fina"),
    "ELECTRODOS": ("id", "sut", "sy", "tau_adm", "lib"),
    "NODOS": ("id", "x", "y"),
    "MATERIALES": ("id", "e", "nu", "fy", "sadm", "alfa", "sut", "suc", "teoria", "rho", "lib"),
    "SECCIONES": ("id", "tipo", "lib", "d", "t", "b", "h", "i", "a", "c", "kv", "tf", "tw"),
    "BARRAS": ("id", "nodo_i", "nodo_j", "material", "seccion", "art_i", "art_j", "pandeo", "suprimida"),
    "APOYOS": ("nodo", "ux", "uy", "phi"),
    "RESORTES": ("nodo", "kx", "ky", "kphi"),
    "RESORTES INCLINADOS": ("nodo", "k", "angulo"),
    "DESAJUSTE DE RESORTES": ("caso", "nodo", "ux", "uy", "phi", "inclinado"),
    "CARGAS": ("caso", "nodo", "px", "py", "m"),
    "CARGAS EN BARRAS": ("caso", "barra", "tipo", "valor", "valor2", "a", "b"),
    "DESPLAZAMIENTOS PREFIJADOS": ("caso", "nodo", "ux", "uy", "phi"),
    "COMBINACIONES": ("combinacion", "caso", "factor"),
}
TITULOS = ["PROYECTO", "NODOS", "MATERIALES", "SECCIONES", "BARRAS", "APOYOS", "RESORTES",
           "RESORTES INCLINADOS", "CARGAS", "CARGAS EN BARRAS", "DESPLAZAMIENTOS PREFIJADOS",
           "DESAJUSTE DE RESORTES", "COMBINACIONES", "SOLDADURAS", "ELECTRODOS"]
OBLIGATORIOS = ["NODOS", "MATERIALES", "SECCIONES", "BARRAS", "APOYOS"]

__all__ = ["ErrorDeEntrada", "cargar_modelo", "Modelo", "Barra", "Nodo", "Material", "NOMBRES_GDL"]


@dataclass
class Nodo:
    id: str
    x: float
    y: float


@dataclass
class Material:
    id: str
    E: float
    nu: float | None
    fy: float | None
    sadm: float | None
    alfa: float | None = None      # coeficiente de dilatación térmica [1/°C]
    fuente: str = ""               # si viene de la biblioteca: de qué ficha
    rho: float | None = None       # densidad [kg/m³] (peso propio)
    sut: float | None = None       # resistencia a tracción (materiales frágiles)
    suc: float | None = None       # resistencia a compresión (por defecto = sut)
    teoria: str = "vm"             # vm | tresca | rankine | mohr | mohrmod  (ver struttura/falla_plana.py)


@dataclass
class Barra:
    id: str
    i: int
    j: int
    mat: Material
    sec: Seccion
    L: float
    g1: float              # cos α
    g2: float              # sen α
    art_i: bool = False    # articulación (M = 0) en el extremo i
    art_j: bool = False
    pandeo: str = "art-art"    # condición de extremos para el pandeo de Euler (ver struttura/pandeo.py)

    def __post_init__(self):
        self.rel = liberados(self.art_i, self.art_j)
        self.k_full = rigidez_local(self.mat.E, self.sec.A, self.sec.I, self.L)     # local, sin condensar
        self.k_cond, _ = condensar(self.k_full, None, self.rel)                    # local, con articulaciones

    @property
    def angulo_deg(self) -> float:
        return math.degrees(math.atan2(self.g2, self.g1))


@dataclass
class Modelo:
    archivo: Path
    config: dict
    nodos: list
    barras: list
    materiales: dict
    secciones: dict
    restr: np.ndarray                 # (n,3) bool: GDL restringido por un apoyo
    resortes: np.ndarray              # (n,3) rigidez de resorte [kx, ky, kφ]
    casos: dict                       # nombre -> F (n,3)  [Px, Py, M]
    prefij: dict                      # nombre -> (n,3)
    combinaciones: dict
    avisos: list = field(default_factory=list)
    cargas_barra: dict = field(default_factory=dict)
    resortes_incl: list = field(default_factory=list)   # [{"nodo": k, "id": str, "k": rigidez, "beta": grados}]
    desaj: dict = field(default_factory=dict)           # caso -> (n,3) apoyo corrido de los resortes rectos
    desaj_incl: dict = field(default_factory=dict)      # caso -> {nodo(idx): e} apoyo corrido del resorte inclinado
    aut: np.ndarray | None = None                       # (n,3) bool: GDL fijados por el programa (φ sin rigidez)
    peso_propio: dict | None = None                     # {"caso", "gravedad", "peso", "masa"} si se pidió peso propio
    soldaduras: list = field(default_factory=list)      # [soldadura.verificar.Soldadura] (bloque SOLDADURAS)
    electrodos: dict = field(default_factory=dict)      # electrodos propios {id: (sut, sy, tau_adm)} en MPa

    def __post_init__(self):
        if self.aut is None:
            self.aut = np.zeros((len(self.nodos), 3), dtype=bool)

    @property
    def res_mask(self) -> np.ndarray:
        m = self.resortes > 0
        for sp in self.resortes_incl:
            m[sp["nodo"], :2] = True
        return m

    @property
    def n(self) -> int:
        return len(self.nodos)

    def nombre_gdl(self, k: int) -> str:
        return f"nodo {self.nodos[k // 3].id} ({NOMBRES_GDL[k % 3]})"


# --------------------------------------------------------------------------
def cargar_modelo(ruta) -> Modelo:
    ruta = Path(ruta)
    if not ruta.is_file():
        raise ErrorDeEntrada(f"No se encuentra el archivo '{ruta}'")
    bloques = _partir_bloques(ruta, TITULOS)
    suprimidas = suprimir_barras(bloques)
    faltan = [t for t in OBLIGATORIOS if _norm(t) not in bloques]
    if faltan:
        raise ErrorDeEntrada(
            f"Faltan bloques obligatorios: {', '.join(faltan)}.  Cada bloque empieza con una línea que "
            f"contiene solo su título.  Bloques encontrados: "
            f"{', '.join(b['titulo'] for b in bloques.values()) or 'ninguno'}")
    avisos: list[str] = []
    if suprimidas:
        avisos.append("Nota: barras suprimidas (no entran al cálculo; siguen en el archivo): " + ", ".join(suprimidas))
    config = _leer_config(bloques, ruta, avisos)
    avisar_columnas(bloques, avisos, _COLUMNAS)
    nodos, idx = _leer_nodos(bloques)
    materiales = _leer_materiales(bloques, avisos, config)
    secciones = _leer_secciones(bloques, config, avisos)
    barras = _leer_barras(bloques, nodos, idx, materiales, secciones, avisos)
    restr = _leer_apoyos(bloques, nodos, idx)
    resortes = _leer_resortes(bloques, nodos, idx)
    incl = _leer_resortes_incl(bloques, nodos, idx)
    if not restr.any() and not resortes.any() and not incl:
        raise ErrorDeEntrada("No hay ningún apoyo: ni GDL restringidos (APOYOS) ni resortes (RESORTES)")
    for k in range(len(nodos)):
        for c in range(3):
            if restr[k, c] and resortes[k, c] > 0:
                avisos.append(f"El nodo {nodos[k].id} tiene un resorte en {NOMBRES_GDL[c]} y ese GDL además está "
                              "restringido: el resorte no modifica los desplazamientos (solo recibe fuerza si hay "
                              "desplazamientos prefijados).")
    casos = _leer_cargas(bloques, nodos, idx)
    cargas_barra = _leer_cargas_barra(bloques, barras, avisos)
    peso = _peso_propio(config, barras, casos, cargas_barra, len(nodos))
    desaj, desaj_incl = _leer_desajustes(bloques, nodos, idx, resortes, restr, incl)
    prefij = _leer_prefijados(bloques, nodos, idx, restr)
    for d in (cargas_barra, desaj, desaj_incl, prefij):
        for nombre in d:
            casos.setdefault(nombre, np.zeros((len(nodos), 3)))
    for nombre in casos:
        prefij.setdefault(nombre, np.zeros((len(nodos), 3)))
        desaj.setdefault(nombre, np.zeros((len(nodos), 3)))
        desaj_incl.setdefault(nombre, {})
    if not casos:
        raise ErrorDeEntrada("No hay ningún caso de carga (CARGAS, CARGAS EN BARRAS y "
                             "DESPLAZAMIENTOS PREFIJADOS no tienen filas)")
    combos = _leer_combinaciones(bloques, casos)

    usados = {b.i for b in barras} | {b.j for b in barras}
    for k, nd in enumerate(nodos):
        if k not in usados:
            avisos.append(f"El nodo {nd.id} no está conectado a ninguna barra.")
    aut = _giros_sin_rigidez(nodos, barras, restr, resortes, avisos)
    m = Modelo(ruta, config, nodos, barras, materiales, secciones, restr, resortes, casos, prefij, combos,
               avisos, cargas_barra, incl, desaj, desaj_incl, aut, peso)
    from ..portico3d.soldaduras import leer as _leer_soldaduras
    m.soldaduras, m.electrodos = _leer_soldaduras(bloques, barras, config)
    return m


def _giros_sin_rigidez(nodos, barras, restr, resortes, avisos):
    """φ de los nodos donde TODAS las barras están articuladas (y sin resorte de giro ni apoyo):
    no tiene rigidez y queda indeterminado.  Se fija (aut) sin ningún efecto sobre los esfuerzos."""
    aut = np.zeros((len(nodos), 3), dtype=bool)
    for k, nd in enumerate(nodos):
        inc = [(b.art_i if b.i == k else b.art_j) for b in barras if k in (b.i, b.j)]
        if inc and all(inc) and not restr[k, 2] and resortes[k, 2] <= 0:
            aut[k, 2] = True
            avisos.append(f"Nodo {nd.id}: todas las barras concurrentes están articuladas en ese nodo, "
                          "su giro φ no tiene rigidez (indeterminado).  El programa lo fija internamente "
                          "(no afecta a los esfuerzos; los giros de cada barra se informan igual).")
    return aut


def _leer_config(bloques, ruta, avisos):
    config = {"proyecto": ruta.stem, "autor": "", "unidad_fuerza": "N", "unidad_longitud": "mm",
              "escala_deformada": None, "anexo_matrices": "si", "csv_salida": "excel_es",
              "escala_diagramas": "barra", "tipo": "portico", "corte_tensiones": "si", "peso_propio": "", "gravedad": "-y", "_nodal": ""}
    b = bloques.get("proyecto")
    for n, celdas in (b["filas"] if b else []):
        k = celdas[0].strip().lower()
        v = celdas[1].strip() if len(celdas) > 1 else ""
        if k not in config:
            avisos.append(f"Bloque PROYECTO, línea {n}: clave desconocida '{k}' (ignorada).")
            continue
        if k == "escala_deformada":
            v = None if v.lower() in ("", "auto") else _num(v, "PROYECTO", n, k)
        elif k in ("anexo_matrices", "csv_salida", "escala_diagramas", "tipo", "gravedad", "corte_tensiones"):
            v = v.lower()
        config[k] = v
    if config["tipo"] == "emparrillado":
        raise ErrorDeEntrada("Este archivo dice tipo=emparrillado: usar  python struttura.py archivo.csv  "
                             "(el despachador elige el programa de emparrillado).")
    if config["tipo"] != "portico":
        raise ErrorDeEntrada("Bloque PROYECTO: 'tipo' debe ser portico")
    if config["anexo_matrices"] not in ("auto", "si", "no"):
        raise ErrorDeEntrada("Bloque PROYECTO: 'anexo_matrices' debe ser si o no (auto = si)")
    if config["escala_diagramas"] not in ("barra", "global"):
        raise ErrorDeEntrada("Bloque PROYECTO: 'escala_diagramas' debe ser barra o global")
    if config["csv_salida"] not in ("excel_es", "estandar"):
        raise ErrorDeEntrada("Bloque PROYECTO: 'csv_salida' debe ser excel_es o estandar")
    if config["corte_tensiones"] not in ("si", "no"):
        raise ErrorDeEntrada("Bloque PROYECTO: 'corte_tensiones' debe ser si o no")
    from ..peso_propio import validar_gravedad
    validar_gravedad(config, ("x", "y"), "-y")
    return config


def _leer_nodos(bloques):
    nodos, idx = [], {}
    for n, r in _tabla(bloques, "NODOS", ["id", "x", "y"]):
        id_ = r["id"]
        if not id_:
            raise ErrorDeEntrada(f"Bloque NODOS, línea {n}: falta el id del nodo")
        if id_ in idx:
            raise ErrorDeEntrada(f"Bloque NODOS, línea {n}: el nodo '{id_}' está repetido")
        idx[id_] = len(nodos)
        nodos.append(Nodo(id_, _num(r["x"], "NODOS", n, "x"), _num(r["y"], "NODOS", n, "y")))
    if len(nodos) < 2:
        raise ErrorDeEntrada("Bloque NODOS: hacen falta al menos 2 nodos")
    return nodos, idx


def _leer_materiales(bloques, avisos=None, config=None):
    from ..biblioteca.biblioteca import ErrorBiblioteca, datos_modelo
    avisos = [] if avisos is None else avisos
    mats = {}
    for n, r in _tabla(bloques, "MATERIALES", ["id"]):
        id_ = r["id"]
        if id_ in mats:
            raise ErrorDeEntrada(f"Bloque MATERIALES, línea {n}: el material '{id_}' está repetido")
        lib = (r.get("lib") or "").strip()
        dl = {}
        if lib:
            try:
                dl = datos_modelo(lib, config["unidad_fuerza"], config["unidad_longitud"])
            except ErrorBiblioteca as e:
                raise ErrorDeEntrada(f"Bloque MATERIALES, línea {n}: {e}")
            avisos.append(f"Nota: Material '{id_}': datos de la biblioteca ({dl['fuente']}); valores típicos de la ficha, no garantizados.")
        elif "e" not in r:
            raise ErrorDeEntrada("Bloque MATERIALES: faltan las columnas ['e'].  Se puede completar con lib;<número de la biblioteca>")
        E = _num(r.get("e"), "MATERIALES", n, "E", obligatorio=not lib)
        if E is None:
            E = dl.get("E")
            if E is None:
                raise ErrorDeEntrada(f"Bloque MATERIALES, línea {n}: la ficha '{lib}' no trae módulo de elasticidad; cargá E a mano")
        if E <= 0:
            raise ErrorDeEntrada(f"Bloque MATERIALES, línea {n}: E debe ser > 0")
        nu = _num(r.get("nu"), "MATERIALES", n, "nu", obligatorio=False)
        fy = _num(r.get("fy"), "MATERIALES", n, "fy", obligatorio=False)
        rho = _num(r.get("rho"), "MATERIALES", n, "rho", obligatorio=False)
        rho = dl.get("rho") if rho is None else rho
        if rho is not None and rho <= 0:
            raise ErrorDeEntrada(f"Bloque MATERIALES, línea {n}: rho (densidad en kg/m³) debe ser > 0")
        fy = dl.get("fy") if fy is None else fy
        sut = _num(r.get("sut"), "MATERIALES", n, "sut", obligatorio=False)
        sut = dl.get("sut") if sut is None else sut
        teoria, suc = resolver_teoria(id_, n, fy, sut, _num(r.get("suc"), "MATERIALES", n, "suc", obligatorio=False), r.get("teoria"), avisos, ErrorDeEntrada)
        mats[id_] = Material(id_, E, dl.get("nu") if nu is None else nu, fy,
                             _num(r.get("sadm"), "MATERIALES", n, "sadm", obligatorio=False),
                             _num(r.get("alfa"), "MATERIALES", n, "alfa", obligatorio=False), dl.get("fuente", ""), rho, sut, suc, teoria)
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
                r = expandir(r, "plano", config or {"unidad_longitud": "mm"}, n, avisos if avisos is not None else [])
            except ErrorBiblioteca as e:
                raise ErrorDeEntrada(str(e))
        p = {}
        for clave, col in (("d", "d"), ("t", "t"), ("b", "b"), ("h", "h"), ("I", "i"), ("A", "a"),
                           ("c", "c"), ("kv", "kv"), ("tf", "tf"), ("tw", "tw")):
            p[clave] = _num(r.get(col), "SECCIONES", n, col, obligatorio=False)
        p["J"] = 1.0                                   # la torsión no interviene en el pórtico plano
        if r["tipo"].strip().lower() == "generica" and p["A"] is None:
            raise ErrorDeEntrada(f"Bloque SECCIONES, línea {n} (sección '{id_}'): la sección genérica necesita I y A")
        try:
            s = crear_seccion(id_, r["tipo"], p)
        except ValueError as e:
            raise ErrorDeEntrada(f"Bloque SECCIONES, línea {n} (sección '{id_}'): {e}")
        s.J, s.Wt = None, None
        s.descripcion = r["_perfil"] if r.get("_perfil") else s.descripcion.replace("(h vertical)", "(h en el plano del pórtico)")
        secs[id_] = s
    if not secs:
        raise ErrorDeEntrada("Bloque SECCIONES: no hay secciones")
    return secs


def _leer_barras(bloques, nodos, idx, materiales, secciones, avisos):
    barras, ids, pares = [], set(), {}
    xs, ys = [nd.x for nd in nodos], [nd.y for nd in nodos]
    dim = max(max(xs) - min(xs), max(ys) - min(ys), 1.0)
    for n, r in _tabla(bloques, "BARRAS", ["id", "nodo_i", "nodo_j", "material", "seccion"]):
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
        dx, dy = nodos[j].x - nodos[i].x, nodos[j].y - nodos[i].y
        L = math.hypot(dx, dy)
        if L < 1e-9 * dim:
            raise ErrorDeEntrada(f"Bloque BARRAS, línea {n}: la barra '{id_}' tiene longitud nula")
        par = frozenset((i, j))
        if par in pares:
            avisos.append(f"Las barras '{pares[par]}' y '{id_}' unen los mismos dos nodos.")
        pares[par] = id_
        ai = _flag(r.get("art_i"), "BARRAS", n, "art_i")
        aj = _flag(r.get("art_j"), "BARRAS", n, "art_j")
        cod = pandeo_codigo(r.get("pandeo"))
        if cod is None:
            raise ErrorDeEntrada(f"Bloque BARRAS, línea {n}: pandeo '{r.get('pandeo')}' no es válido para la barra '{id_}'.  Valores: {PANDEO_VALORES}")
        barras.append(Barra(id_, i, j, materiales[r["material"]], secciones[r["seccion"]], L, dx / L, dy / L, ai, aj, cod))
    if not barras:
        raise ErrorDeEntrada("Bloque BARRAS: no hay barras")
    return barras


def _leer_apoyos(bloques, nodos, idx):
    restr = np.zeros((len(nodos), 3), dtype=bool)
    vistos = set()
    for n, r in _tabla(bloques, "APOYOS", ["nodo", "ux", "uy", "phi"]):
        if r["nodo"] not in idx:
            raise ErrorDeEntrada(f"Bloque APOYOS, línea {n}: el nodo '{r['nodo']}' no existe")
        if r["nodo"] in vistos:
            raise ErrorDeEntrada(f"Bloque APOYOS, línea {n}: el nodo '{r['nodo']}' aparece dos veces")
        vistos.add(r["nodo"])
        for c, campo in enumerate(("ux", "uy", "phi")):
            restr[idx[r["nodo"]], c] = _flag(r[campo], "APOYOS", n, campo)
    return restr


def _leer_resortes(bloques, nodos, idx):
    k_res = np.zeros((len(nodos), 3))
    vistos = set()
    for n, r in _tabla(bloques, "RESORTES", ["nodo", "kx", "ky", "kphi"], requerido=False) or []:
        if r["nodo"] not in idx:
            raise ErrorDeEntrada(f"Bloque RESORTES, línea {n}: el nodo '{r['nodo']}' no existe")
        if r["nodo"] in vistos:
            raise ErrorDeEntrada(f"Bloque RESORTES, línea {n}: el nodo '{r['nodo']}' aparece dos veces")
        vistos.add(r["nodo"])
        for c, campo in enumerate(("kx", "ky", "kphi")):
            v = _num(r[campo], "RESORTES", n, campo, obligatorio=False, defecto=0.0)
            if v < 0:
                raise ErrorDeEntrada(f"Bloque RESORTES, línea {n}: {campo} no puede ser negativo")
            k_res[idx[r["nodo"]], c] = v
    return k_res


def _leer_resortes_incl(bloques, nodos, idx):
    """RESORTES INCLINADOS:  nodo;k;angulo.  Resorte lineal (fuerza) cuyo eje forma 'angulo' grados con +X
    (antihorario).  Aporta k·a·aᵀ a (ux, uy) con a = (cos β, sen β)."""
    ctx = "RESORTES INCLINADOS"
    out, vistos = [], set()
    for n, r in _tabla(bloques, ctx, ["nodo", "k", "angulo"], requerido=False) or []:
        if r["nodo"] not in idx:
            raise ErrorDeEntrada(f"Bloque {ctx}, línea {n}: el nodo '{r['nodo']}' no existe")
        if r["nodo"] in vistos:
            raise ErrorDeEntrada(f"Bloque {ctx}, línea {n}: el nodo '{r['nodo']}' aparece dos veces")
        vistos.add(r["nodo"])
        k = _num(r["k"], ctx, n, "k")
        if k <= 0:
            raise ErrorDeEntrada(f"Bloque {ctx}, línea {n}: k debe ser > 0")
        out.append({"nodo": idx[r["nodo"]], "id": r["nodo"], "k": k, "beta": _num(r["angulo"], ctx, n, "angulo")})
    return out


def _leer_desajustes(bloques, nodos, idx, resortes, restr, incl):
    """DESAJUSTE DE RESORTES:  caso;nodo;ux;uy;phi;inclinado.

    Desplazamiento impuesto al APOYO (extremo fijo) del resorte, en el sentido positivo del GDL
    (columna 'inclinado': a lo largo del eje del resorte inclinado).  Fuerza del resorte: −k·(u − e)."""
    ctx = "DESAJUSTE DE RESORTES"
    out, out_i = {}, {}
    con_incl = {sp["nodo"] for sp in incl}
    for n, r in _tabla(bloques, ctx, ["caso", "nodo", "ux", "uy", "phi"], requerido=False) or []:
        if r["nodo"] not in idx:
            raise ErrorDeEntrada(f"Bloque {ctx}, línea {n}: el nodo '{r['nodo']}' no existe")
        k = idx[r["nodo"]]
        A = out.setdefault(r["caso"], np.zeros((len(nodos), 3)))
        for c, campo in enumerate(("ux", "uy", "phi")):
            v = _num(r[campo], ctx, n, campo, obligatorio=False, defecto=0.0)
            if v != 0.0 and resortes[k, c] <= 0:
                raise ErrorDeEntrada(f"Bloque {ctx}, línea {n}: se da un desajuste en {campo} del nodo "
                                     f"'{r['nodo']}', pero ese GDL no tiene resorte recto en RESORTES")
            A[k, c] += v
        vi = _num(r.get("inclinado"), ctx, n, "inclinado", obligatorio=False, defecto=0.0)
        if vi != 0.0:
            if k not in con_incl:
                raise ErrorDeEntrada(f"Bloque {ctx}, línea {n}: desajuste 'inclinado' en el nodo '{r['nodo']}', "
                                     "que no tiene resorte en RESORTES INCLINADOS")
            out_i.setdefault(r["caso"], {})
            out_i[r["caso"]][k] = out_i[r["caso"]].get(k, 0.0) + vi
    return out, out_i


def _leer_cargas(bloques, nodos, idx):
    casos: dict = {}
    for n, r in _tabla(bloques, "CARGAS", ["caso", "nodo", "px", "py", "m"], requerido=False) or []:
        caso = r["caso"]
        if not caso:
            raise ErrorDeEntrada(f"Bloque CARGAS, línea {n}: falta el nombre del caso")
        if r["nodo"] not in idx:
            raise ErrorDeEntrada(f"Bloque CARGAS, línea {n}: el nodo '{r['nodo']}' no existe")
        F = casos.setdefault(caso, np.zeros((len(nodos), 3)))
        for c, campo in enumerate(("px", "py", "m")):
            F[idx[r["nodo"]], c] += _num(r[campo], "CARGAS", n, campo, obligatorio=False, defecto=0.0)
    return casos


_DISTRIB = ("q", "qa", "qgx", "qgy", "qgxp", "qgyp")
_PUNTUAL = ("P", "Pa", "Pgx", "Pgy", "Mp")


def _peso_propio(config, barras, casos, cargas_barra, n_nodos):
    """peso_propio;<caso>: carga distribuida uniforme ρ·g·A en cada barra (en el reticulado, mitad del peso en cada nudo extremo)."""
    caso = (config.get("peso_propio") or "").strip()
    if not caso:
        return None
    from ..peso_propio import peso_especifico
    w, fL = peso_especifico(config, barras)
    g = config["gravedad"].replace("+", "")
    signo, eje = (-1.0 if g.startswith("-") else 1.0), g[-1]
    tipo = "qg" + eje
    peso = masa = 0.0
    if config.get("_nodal"):
        casos.setdefault(caso, np.zeros((n_nodos, 3)))
    for k, b in enumerate(barras):
        W = w[k] * b.sec.A * b.L
        if config.get("_nodal"):                              # reticulado: biela, mitad en cada nudo
            for nd in (b.i, b.j):
                casos[caso][nd, 0 if eje == "x" else 1] += signo * W / 2
        else:
            q = signo * w[k] * b.sec.A
            qx, qy = descomponer(tipo, q, q, b.g1, b.g2)
            cargas_barra.setdefault(caso, []).append(CargaBarra(caso, k, b.id, "q", tipo, q, q, 0.0, b.L, qx=qx, qy=qy))
        peso += W
        masa += b.mat.rho * b.sec.A * b.L * fL ** 3
    return {"caso": caso, "gravedad": config["gravedad"], "peso": peso, "masa": masa, "nodal": bool(config.get("_nodal"))}


def _leer_cargas_barra(bloques, barras, avisos):
    """Bloque CARGAS EN BARRAS:  caso;barra;tipo;valor;valor2;a;b   (ver cargas_barra.py)."""
    ctx = "CARGAS EN BARRAS"
    por_id = {b.id: k for k, b in enumerate(barras)}
    canon = {t.lower(): t for t in TIPOS_CARGA}
    out: dict = {}
    for n, r in _tabla(bloques, ctx, ["caso", "barra", "tipo", "valor"], requerido=False) or []:
        caso = r["caso"]
        if not caso:
            raise ErrorDeEntrada(f"Bloque {ctx}, línea {n}: falta el nombre del caso")
        if r["barra"] not in por_id:
            raise ErrorDeEntrada(f"Bloque {ctx}, línea {n}: la barra '{r['barra']}' no existe en BARRAS")
        k = por_id[r["barra"]]
        b = barras[k]
        tipo = canon.get(r["tipo"].strip().lower())
        if tipo is None:
            raise ErrorDeEntrada(f"Bloque {ctx}, línea {n}: tipo '{r['tipo']}' desconocido "
                                 f"(tipos válidos: {', '.join(TIPOS_CARGA)})")
        v1 = _num(r["valor"], ctx, n, "valor")
        eps = 1e-9 * b.L
        if tipo in _DISTRIB:
            v2 = _num(r.get("valor2"), ctx, n, "valor2", obligatorio=False, defecto=v1)
            a = _num(r.get("a"), ctx, n, "a", obligatorio=False, defecto=0.0)
            bb = _num(r.get("b"), ctx, n, "b", obligatorio=False, defecto=b.L)
            if not (-eps <= a < bb <= b.L + eps):
                raise ErrorDeEntrada(f"Bloque {ctx}, línea {n}: se exige 0 ≤ a < b ≤ L "
                                     f"(a={a:g}, b={bb:g}, L={b.L:g} de la barra '{b.id}')")
            a, bb = max(a, 0.0), min(bb, b.L)
            qx, qy = descomponer(tipo, v1, v2, b.g1, b.g2)
            out.setdefault(caso, []).append(CargaBarra(caso, k, b.id, "q", tipo, v1, v2, a, bb, qx=qx, qy=qy))
        elif tipo in _PUNTUAL:
            a = _num(r.get("a"), ctx, n, "a")
            if not (-eps <= a <= b.L + eps):
                raise ErrorDeEntrada(f"Bloque {ctx}, línea {n}: la posición a={a:g} está fuera de la barra "
                                     f"'{b.id}' (0 ≤ a ≤ L = {b.L:g})")
            a = min(max(a, 0.0), b.L)
            if tipo == "Mp":
                c = CargaBarra(caso, k, b.id, "M", tipo, v1, 0.0, a, a, M0=v1)
            else:
                (px, _), (py, _) = descomponer(tipo, v1, v1, b.g1, b.g2)
                c = CargaBarra(caso, k, b.id, "P", tipo, v1, 0.0, a, a, Px=px, Py=py)
            out.setdefault(caso, []).append(c)
        elif tipo == "dl":                                      # desajuste de longitud (barra larga +, corta −)
            out.setdefault(caso, []).append(CargaBarra(caso, k, b.id, "temp", tipo, v1, 0.0, 0.0, b.L, e0=v1))
        else:                                                   # temp
            v2 = _num(r.get("valor2"), ctx, n, "valor2")
            if not b.mat.alfa:
                raise ErrorDeEntrada(f"Bloque {ctx}, línea {n}: la carga térmica en la barra '{b.id}' necesita "
                                     f"'alfa' en el material '{b.mat.id}' (bloque MATERIALES)")
            if v1 != v2 and not b.sec.h:
                raise ErrorDeEntrada(f"Bloque {ctx}, línea {n}: el gradiente térmico en la barra '{b.id}' necesita "
                                     f"la altura 'h' de la sección '{b.sec.id}' (bloque SECCIONES)")
            out.setdefault(caso, []).append(CargaBarra(caso, k, b.id, "temp", tipo, v1, v2, 0.0, b.L, Ts=v1, Ti=v2))
    return out


def _leer_prefijados(bloques, nodos, idx, restr):
    ctx = "DESPLAZAMIENTOS PREFIJADOS"
    prefij: dict = {}
    for n, r in _tabla(bloques, ctx, ["caso", "nodo", "ux", "uy", "phi"], requerido=False) or []:
        if r["nodo"] not in idx:
            raise ErrorDeEntrada(f"Bloque {ctx}, línea {n}: el nodo '{r['nodo']}' no existe")
        k = idx[r["nodo"]]
        A = prefij.setdefault(r["caso"], np.zeros((len(nodos), 3)))
        for c, campo in enumerate(("ux", "uy", "phi")):
            v = _num(r[campo], ctx, n, campo, obligatorio=False, defecto=0.0)
            if v != 0.0 and not restr[k, c]:
                raise ErrorDeEntrada(f"Bloque {ctx}, línea {n}: se prefija {campo}={v:g} en el nodo "
                                     f"'{r['nodo']}', pero ese GDL no está restringido en APOYOS")
            A[k, c] += v
    return prefij


def _leer_combinaciones(bloques, casos):
    combos: dict = {}
    for n, r in _tabla(bloques, "COMBINACIONES", ["combinacion", "caso", "factor"], requerido=False) or []:
        nombre = r["combinacion"]
        if nombre in casos:
            raise ErrorDeEntrada(f"Bloque COMBINACIONES, línea {n}: '{nombre}' ya es un caso de carga")
        if r["caso"] not in casos:
            raise ErrorDeEntrada(f"Bloque COMBINACIONES, línea {n}: el caso '{r['caso']}' no existe")
        combos.setdefault(nombre, []).append((r["caso"], _num(r["factor"], "COMBINACIONES", n, "factor")))
    if not combos and len(casos) > 1 and "TOTAL" not in casos:   # estado total: suma de todos los casos (factor 1), solo si no hay combinaciones propias
        combos["TOTAL"] = [(c, 1.0) for c in casos]
    return combos
