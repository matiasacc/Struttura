"""Lectura y validación del archivo CSV ÚNICO de entrada.

El archivo se divide en BLOQUES.  Cada bloque empieza con una línea que contiene solamente
su título (en mayúsculas o minúsculas, con o sin tildes) y sigue con la fila de encabezados y
las filas de datos.  Las líneas en blanco y las que empiezan con '#' se ignoran.

    NODOS
    id;x;y
    1;0;0
    2;1000;0

Títulos válidos:  PROYECTO, NODOS, MATERIALES, SECCIONES, BARRAS, APOYOS, RESORTES, CARGAS,
                  CARGAS EN BARRAS, DESPLAZAMIENTOS PREFIJADOS, RESORTES GIRO INCLINADO,
                  DESAJUSTE DE RESORTES, COMBINACIONES
Obligatorios:     NODOS, MATERIALES, SECCIONES, BARRAS, APOYOS
                  (y al menos una carga: en CARGAS, en CARGAS EN BARRAS o desplazamientos prefijados)

Se aceptan el CSV "estándar" (separador ',' y decimal '.') y el de Excel en español
(separador ';' y decimal ',').  Si el archivo contiene algún ';' se usa ';' como separador.
"""
from __future__ import annotations

import csv
import math
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from ..falla_plana import resolver_teoria
from .barra import condensar, liberados, parsear_articulacion, rigidez_local, matriz_rotacion
from .cargas_barra import CargaBarra, TIPOS as TIPOS_CARGA_BARRA
from .secciones import Seccion, crear_seccion

NOMBRES_GDL = ("uz", "φx", "φy")

TITULOS = ["PROYECTO", "NODOS", "MATERIALES", "SECCIONES", "BARRAS", "APOYOS", "RESORTES",
           "RESORTES GIRO INCLINADO", "CARGAS", "CARGAS EN BARRAS", "DESPLAZAMIENTOS PREFIJADOS",
           "DESAJUSTE DE RESORTES", "COMBINACIONES", "SOLDADURAS", "ELECTRODOS"]
OBLIGATORIOS = ["NODOS", "MATERIALES", "SECCIONES", "BARRAS", "APOYOS"]


class ErrorDeEntrada(Exception):
    """Problema en los datos cargados por el usuario."""


# --------------------------------------------------------------------------
# Modelo
# --------------------------------------------------------------------------
@dataclass
class Nodo:
    id: str
    x: float
    y: float


@dataclass
class Material:
    id: str
    E: float
    G: float
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
    i: int                 # índice (0-based) del nodo inicial
    j: int                 # índice (0-based) del nodo final
    mat: Material
    sec: Seccion
    L: float
    g1: float              # cos del ángulo de xl respecto de X global
    g2: float              # sen del ángulo de xl respecto de X global
    art_i: str = ""        # articulación en el extremo i: "" | "m" (flexión) | "t" (torsión) | "mt"
    art_j: str = ""

    def __post_init__(self):
        self.rel = liberados(self.art_i, self.art_j)
        self.k_full = rigidez_local(self.mat.E, self.mat.G, self.sec.I, self.sec.J, self.L)   # local, sin condensar
        self.k_cond, _ = condensar(self.k_full, None, self.rel)                               # local, con articulaciones

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
    restr: np.ndarray                 # (n,3) bool: True = GDL restringido
    resortes: np.ndarray              # (n,3) rigidez de resorte [kz, kφx, kφy]; 0 = sin resorte
    casos: dict                       # nombre -> F (n,3)
    prefij: dict                      # nombre -> (n,3) desplazamientos prefijados
    combinaciones: dict               # nombre -> [(caso, factor), ...]
    avisos: list = field(default_factory=list)
    cargas_barra: dict = field(default_factory=dict)   # caso -> [CargaBarra, ...]
    resortes_giro: list = field(default_factory=list)  # [{"nodo": k, "id": str, "k": rigidez, "beta": grados}, ...]
    desaj: dict = field(default_factory=dict)          # caso -> (n,3) desplazamiento impuesto al apoyo del resorte
    peso_propio: dict | None = None                    # {"caso", "gravedad", "peso", "masa"} si se pidió peso propio
    soldaduras: list = field(default_factory=list)     # [soldadura.verificar.Soldadura] (bloque SOLDADURAS)
    electrodos: dict = field(default_factory=dict)     # electrodos propios {id: (sut, sy, tau_adm)} en MPa
    estab: list = field(default_factory=list)          # [(GDL globales, vector, eps)]: giros sin rigidez por articulaciones
    resortes_pc: list = field(default_factory=list)    # resorte kz con carga crítica de pandeo (pandeo_resortes)

    @property
    def res_mask(self) -> np.ndarray:
        """(n,3) bool: GDL que tienen algún resorte (recto o de giro inclinado)."""
        m = self.resortes > 0
        for sp in self.resortes_giro:
            m[sp["nodo"], 1:] = True
        return m

    @property
    def n(self) -> int:
        return len(self.nodos)

    def nombre_gdl(self, k: int) -> str:
        return f"nodo {self.nodos[k // 3].id} ({NOMBRES_GDL[k % 3]})"


# --------------------------------------------------------------------------
# Lectura y partición en bloques
# --------------------------------------------------------------------------
def _norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.lower().strip().strip("[]:").strip()
    return " ".join(s.split())


_TITULOS_NORM = {_norm(t): t for t in TITULOS}


def _partir_bloques(ruta: Path, titulos=None) -> dict:
    """Devuelve {título_normalizado: {'titulo', 'linea', 'filas': [(nro_linea, [celdas])]}}."""
    titulos = titulos or TITULOS
    titulos_norm = {_norm(t): t for t in titulos}
    datos = ruta.read_bytes()
    try:
        texto = datos.decode("utf-8-sig")
    except UnicodeDecodeError:
        texto = datos.decode("cp1252", errors="replace")      # Excel en Windows guarda así
    lineas = []
    for n, l in enumerate(texto.splitlines(), 1):
        if not l.strip() or l.lstrip().startswith("#"):
            continue
        if not l.replace(";", "").replace(",", "").replace("\t", "").strip():
            continue                                   # fila vacía exportada por Excel (;;;;)
        lineas.append((n, l))
    if not lineas:
        raise ErrorDeEntrada(f"El archivo '{ruta.name}' está vacío")
    delim = ";" if any(";" in l for _, l in lineas) else ("\t" if any("\t" in l for _, l in lineas) else ",")

    bloques: dict = {}
    actual = None
    for n, l in lineas:
        celdas = [c.strip() for c in next(csv.reader([l], delimiter=delim))]
        while celdas and celdas[-1] == "":
            celdas.pop()
        if len(celdas) == 1:
            clave = _norm(celdas[0])
            if clave in titulos_norm:
                if clave in bloques:
                    raise ErrorDeEntrada(f"Línea {n}: el bloque {titulos_norm[clave]} aparece dos veces "
                                         f"(la primera vez en la línea {bloques[clave]['linea']})")
                actual = {"titulo": titulos_norm[clave], "linea": n, "filas": []}
                bloques[clave] = actual
                continue
            if actual is None or actual["titulo"] != "PROYECTO":
                raise ErrorDeEntrada(
                    f"Línea {n}: '{celdas[0]}' parece un título de bloque pero no es válido "
                    f"(o es una fila con un solo dato).  Títulos válidos: {', '.join(titulos)}")
        if actual is None:
            raise ErrorDeEntrada(f"Línea {n}: hay datos antes del primer título de bloque")
        actual["filas"].append((n, celdas))
    return bloques


_SI_SUPR = ("1", "si", "sí", "s", "x", "true", "yes")


def suprimir_barras(bloques) -> list:
    """Barras con 'suprimida' = 1 en BARRAS: salen del cálculo pero quedan en el archivo (como «suprimir» en un programa de elementos
    finitos).  Se quitan de BARRAS y las filas de CARGAS EN BARRAS, SOLDADURAS y PUNTOS DE TENSION que las nombran.
    Devuelve los ids suprimidos.  Los nodos y los resortes que se pongan en ellos siguen como están."""
    b = bloques.get(_norm("BARRAS"))
    if not b or len(b["filas"]) < 2:
        return []
    cab = [c.lower() for c in b["filas"][0][1]]
    if "suprimida" not in cab or "id" not in cab:
        return []
    ic, isup = cab.index("id"), cab.index("suprimida")
    sup, nuevas = [], [b["filas"][0]]
    for n, v in b["filas"][1:]:
        if len(v) > isup and v[isup].strip().lower() in _SI_SUPR:
            sup.append(v[ic] if len(v) > ic else "")
        else:
            nuevas.append((n, v))
    b["filas"] = nuevas
    if not sup:
        return []
    for t in ("CARGAS EN BARRAS", "SOLDADURAS", "PUNTOS DE TENSION"):
        bl = bloques.get(_norm(t))
        if not bl or len(bl["filas"]) < 2:
            continue
        cb = [c.lower() for c in bl["filas"][0][1]]
        if "barra" not in cb:
            continue
        k = cb.index("barra")
        bl["filas"] = [bl["filas"][0]] + [(n, v) for n, v in bl["filas"][1:] if not (len(v) > k and v[k] in sup)]
    return sup


def _tabla(bloques, titulo, obligatorias, requerido=True):
    """Filas de un bloque con encabezado: lista de (nro_linea, dict columna->texto) o None."""
    b = bloques.get(_norm(titulo))
    if b is None:
        if requerido:
            raise ErrorDeEntrada(f"Falta el bloque {titulo}")
        return None
    if not b["filas"]:
        raise ErrorDeEntrada(f"El bloque {titulo} (línea {b['linea']}) no tiene fila de encabezados")
    _, cab = b["filas"][0]
    cols = [c.lower() for c in cab]
    if len(set(cols)) != len(cols):
        raise ErrorDeEntrada(f"Bloque {titulo}: hay columnas repetidas en el encabezado {cols}")
    faltan = [c for c in obligatorias if c not in cols]
    if faltan:
        raise ErrorDeEntrada(f"Bloque {titulo}: faltan las columnas {faltan}.  Encabezado encontrado: {cols}")
    filas = []
    for n, v in b["filas"][1:]:
        if len(v) > len(cols):
            raise ErrorDeEntrada(f"Bloque {titulo}, línea {n}: hay más valores ({len(v)}) que columnas ({len(cols)})")
        v = v + [""] * (len(cols) - len(v))
        filas.append((n, dict(zip(cols, v))))
    return filas


_COLUMNAS_LIBRES = ("descripcion", "descripción", "desc", "nota", "notas", "comentario", "comentarios", "obs", "observaciones")


def avisar_columnas(bloques, avisos, columnas):
    """Avisa de las columnas que el programa no usa (por ejemplo un error de tipeo en el encabezado).  Igual en los 4 programas.
    columnas: {título del bloque: columnas válidas (en minúscula)}."""
    for titulo, conocidas in columnas.items():
        b = bloques.get(_norm(titulo))
        if not b or not b["filas"]:
            continue
        for c in b["filas"][0][1]:
            c = c.strip().lower()
            if c and c not in conocidas and c not in _COLUMNAS_LIBRES:
                avisos.append(f"Bloque {titulo}: la columna '{c}' no se usa (se ignora).  Columnas válidas: {', '.join(conocidas)}.")


_COLUMNAS = {
    "SOLDADURAS": ("id", "tipo", "esp", "barra", "extremo", "disposicion", "b", "d", "arcos", "segmentos", "oy", "oz", "electrodo", "w", "sy_base", "lib", "t_gruesa", "t_fina"),
    "ELECTRODOS": ("id", "sut", "sy", "tau_adm", "lib"),
    "NODOS": ("id", "x", "y"),
    "MATERIALES": ("id", "e", "g", "nu", "fy", "sadm", "alfa", "sut", "suc", "teoria", "rho", "lib"),
    "SECCIONES": ("id", "tipo", "lib", "d", "t", "b", "h", "i", "j", "a", "c", "wt", "kv", "tf", "tw"),
    "BARRAS": ("id", "nodo_i", "nodo_j", "material", "seccion", "art_i", "art_j", "suprimida"),
    "APOYOS": ("nodo", "uz", "phix", "phiy"),
    "RESORTES": ("nodo", "kz", "kphix", "kphiy", "pc"),
    "RESORTES GIRO INCLINADO": ("nodo", "k", "angulo"),
    "DESAJUSTE DE RESORTES": ("caso", "nodo", "uz", "phix", "phiy"),
    "CARGAS": ("caso", "nodo", "pz", "mx", "my"),
    "CARGAS EN BARRAS": ("caso", "barra", "tipo", "valor", "valor2", "a", "b"),
    "DESPLAZAMIENTOS PREFIJADOS": ("caso", "nodo", "uz", "phix", "phiy"),
    "COMBINACIONES": ("combinacion", "caso", "factor"),
}


def _num(txt, ctx, n, campo, obligatorio=True, defecto=None):
    t = (txt or "").strip().replace(",", ".")
    if t == "":
        if obligatorio:
            raise ErrorDeEntrada(f"Bloque {ctx}, línea {n}: falta el valor de '{campo}'")
        return defecto
    try:
        v = float(t)
    except ValueError:
        raise ErrorDeEntrada(f"Bloque {ctx}, línea {n}: '{txt}' no es un número (campo '{campo}')")
    if not math.isfinite(v):
        raise ErrorDeEntrada(f"Bloque {ctx}, línea {n}: valor no finito en '{campo}'")
    return v


def _flag(txt, ctx, n, campo):
    t = (txt or "").strip().lower()
    if t in ("1", "si", "sí", "s", "x", "true", "yes"):
        return True
    if t in ("0", "no", "n", "false", "", "-"):
        return False
    raise ErrorDeEntrada(f"Bloque {ctx}, línea {n}: '{txt}' no es válido en '{campo}' (usar 1 o 0)")


# --------------------------------------------------------------------------
# Carga del modelo completo
# --------------------------------------------------------------------------
def cargar_modelo(ruta) -> Modelo:
    ruta = Path(ruta)
    if not ruta.is_file():
        raise ErrorDeEntrada(f"No se encuentra el archivo '{ruta}'")
    bloques = _partir_bloques(ruta)
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
    resortes_giro = _leer_resortes_giro(bloques, nodos, idx)
    if not restr.any() and not resortes.any() and not resortes_giro:
        raise ErrorDeEntrada("No hay ningún apoyo: ni GDL restringidos (APOYOS) ni resortes (RESORTES)")
    for k in range(len(nodos)):
        for c in range(3):
            if restr[k, c] and resortes[k, c] > 0:
                avisos.append(f"El nodo {nodos[k].id} tiene un resorte en {NOMBRES_GDL[c]} y ese GDL además "
                              "está restringido: el resorte no tiene efecto sobre los desplazamientos.")
    casos = _leer_cargas(bloques, nodos, idx)
    cargas_barra = _leer_cargas_barra(bloques, barras, avisos)
    peso = _peso_propio(config, barras, cargas_barra)
    desaj = _leer_desajustes(bloques, nodos, idx, resortes, restr)
    for nombre in desaj:
        casos.setdefault(nombre, np.zeros((len(nodos), 3)))
    for nombre in cargas_barra:
        casos.setdefault(nombre, np.zeros((len(nodos), 3)))
    prefij = _leer_prefijados(bloques, nodos, idx, restr)
    for nombre in prefij:
        casos.setdefault(nombre, np.zeros((len(nodos), 3)))
    for nombre in casos:
        prefij.setdefault(nombre, np.zeros((len(nodos), 3)))
        desaj.setdefault(nombre, np.zeros((len(nodos), 3)))
    if not casos:
        raise ErrorDeEntrada("No hay ningún caso de carga (CARGAS, CARGAS EN BARRAS y "
                             "DESPLAZAMIENTOS PREFIJADOS no tienen filas)")
    combos = _leer_combinaciones(bloques, casos)

    usados = {b.i for b in barras} | {b.j for b in barras}
    for k, nd in enumerate(nodos):
        if k not in usados:
            avisos.append(f"El nodo {nd.id} no está conectado a ninguna barra.")

    m = Modelo(ruta, config, nodos, barras, materiales, secciones, restr, resortes,
               casos, prefij, combos, avisos, cargas_barra, resortes_giro, desaj, peso)
    m.estab = _giros_sin_rigidez(m)
    from ..portico3d.soldaduras import leer as _leer_soldaduras
    m.soldaduras, m.electrodos = _leer_soldaduras(bloques, barras, config)
    from struttura import pandeo_resortes as _pr
    m.resortes_pc = _pr.leer_rectos(bloques, idx, [("kz", 0)])
    return m


def _giros_sin_rigidez(m):
    """Nodos con giros libres sin rigidez (todas las barras concurrentes articuladas en alguna dirección).
    Devuelve [(GDL globales, vector unitario, eps)] y avisa.  No cambia los esfuerzos: en esa dirección
    no actúa ninguna fuerza; la rigidez ficticia (1e-6 de la de la barra) solo evita la singularidad."""
    out = []
    avisado = set()
    for k, nd in enumerate(m.nodos):
        libres = [c for c in (1, 2) if not m.restr[k, c]]
        if not libres:
            continue
        blk = np.zeros((2, 2))
        esc = 0.0
        for b in m.barras:
            if k not in (b.i, b.j):
                continue
            T = matriz_rotacion(b.g1, b.g2)
            kg = T @ b.k_cond @ T.T
            o = 0 if b.i == k else 3
            blk += kg[o + 1:o + 3, o + 1:o + 3]
            esc = max(esc, b.k_full[2, 2], b.k_full[1, 1])
        for sp in m.resortes_giro:
            if sp["nodo"] == k:
                a = np.array([np.cos(np.radians(sp["beta"])), np.sin(np.radians(sp["beta"]))])
                blk += sp["k"] * np.outer(a, a)
        blk[0, 0] += m.resortes[k, 1]
        blk[1, 1] += m.resortes[k, 2]
        sel = [c - 1 for c in libres]
        w, v = np.linalg.eigh(blk[np.ix_(sel, sel)])
        for wi, vi in zip(w, v.T):
            if wi < 1e-9 * esc:
                full = np.zeros(2)
                full[sel] = vi
                out.append((np.array([3 * k + 1, 3 * k + 2]), full, 1e-6 * esc))
                if k in avisado:
                    continue
                avisado.add(k)
                m.avisos.append(f"Nodo {nd.id}: las articulaciones de las barras dejan un giro sin rigidez en ese nodo "
                                "(indeterminado).  El programa lo estabiliza internamente; no afecta a los esfuerzos "
                                "(los giros de cada barra se informan igual).")
    return out


def _leer_config(bloques, ruta, avisos):
    config = {"proyecto": ruta.stem, "autor": "", "unidad_fuerza": "N", "unidad_longitud": "mm",
              "escala_deformada": None, "anexo_matrices": "si", "csv_salida": "excel_es",
              "escala_diagramas": "barra", "tipo": "emparrillado", "corte_tensiones": "si", "peso_propio": "", "gravedad": "-z"}
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
    if config["tipo"] not in ("emparrillado", "portico"):
        raise ErrorDeEntrada("Bloque PROYECTO: 'tipo' debe ser emparrillado o portico")
    if config["tipo"] == "portico":
        raise ErrorDeEntrada("Este archivo dice tipo=portico: usar  python struttura.py archivo.csv  "
                             "(el despachador elige el programa de pórtico plano).")
    if config["anexo_matrices"] not in ("auto", "si", "no"):
        raise ErrorDeEntrada("Bloque PROYECTO: 'anexo_matrices' debe ser si o no (auto = si)")
    if config["escala_diagramas"] not in ("barra", "global"):
        raise ErrorDeEntrada("Bloque PROYECTO: 'escala_diagramas' debe ser barra o global")
    if config["csv_salida"] not in ("excel_es", "estandar"):
        raise ErrorDeEntrada("Bloque PROYECTO: 'csv_salida' debe ser excel_es o estandar")
    if config["corte_tensiones"] not in ("si", "no"):
        raise ErrorDeEntrada("Bloque PROYECTO: 'corte_tensiones' debe ser si o no")
    from ..peso_propio import validar_gravedad
    validar_gravedad(config, ("z",), "-z")
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
        G = _num(r.get("g"), "MATERIALES", n, "G", obligatorio=False)
        nu = _num(r.get("nu"), "MATERIALES", n, "nu", obligatorio=False)
        if G is None and nu is None:                                  # lo que cargó el usuario manda; la ficha completa lo que falta
            G, nu = dl.get("G"), dl.get("nu")
        fy = _num(r.get("fy"), "MATERIALES", n, "fy", obligatorio=False)
        fy = dl.get("fy") if fy is None else fy
        sadm = _num(r.get("sadm"), "MATERIALES", n, "sadm", obligatorio=False)
        alfa = _num(r.get("alfa"), "MATERIALES", n, "alfa", obligatorio=False)
        if E <= 0:
            raise ErrorDeEntrada(f"Bloque MATERIALES, línea {n}: E debe ser > 0")
        if G is None:
            if nu is None:
                raise ErrorDeEntrada(f"Bloque MATERIALES, línea {n}: cargar G o nu")
            G = E / (2 * (1 + nu))
        elif G <= 0:
            raise ErrorDeEntrada(f"Bloque MATERIALES, línea {n}: G debe ser > 0")
        rho = _num(r.get("rho"), "MATERIALES", n, "rho", obligatorio=False)
        rho = dl.get("rho") if rho is None else rho
        if rho is not None and rho <= 0:
            raise ErrorDeEntrada(f"Bloque MATERIALES, línea {n}: rho (densidad en kg/m³) debe ser > 0")
        sut = _num(r.get("sut"), "MATERIALES", n, "sut", obligatorio=False)
        sut = dl.get("sut") if sut is None else sut
        teoria, suc = resolver_teoria(id_, n, fy, sut, _num(r.get("suc"), "MATERIALES", n, "suc", obligatorio=False), r.get("teoria"), avisos, ErrorDeEntrada)
        mats[id_] = Material(id_, E, G, nu, fy, sadm, alfa, dl.get("fuente", ""), rho, sut, suc, teoria)
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
                r = expandir(r, "emparrillado", config or {"unidad_longitud": "mm"}, n, avisos if avisos is not None else [])
            except ErrorBiblioteca as e:
                raise ErrorDeEntrada(str(e))
        p = {}
        for clave, col in (("d", "d"), ("t", "t"), ("b", "b"), ("h", "h"), ("I", "i"), ("J", "j"),
                           ("A", "a"), ("c", "c"), ("Wt", "wt"), ("kv", "kv"), ("tf", "tf"), ("tw", "tw")):
            p[clave] = _num(r.get(col), "SECCIONES", n, col, obligatorio=False)
        try:
            secs[id_] = crear_seccion(id_, r["tipo"], p)
            if r.get("_perfil"):
                secs[id_].descripcion = r["_perfil"]
        except ValueError as e:
            raise ErrorDeEntrada(f"Bloque SECCIONES, línea {n} (sección '{id_}'): {e}")
    if not secs:
        raise ErrorDeEntrada("Bloque SECCIONES: no hay secciones")
    return secs


def _peso_propio(config, barras, cargas_barra):
    """peso_propio;<caso>: carga distribuida uniforme ρ·g·A en cada barra (q en z; la gravedad actúa en -z por defecto)."""
    caso = (config.get("peso_propio") or "").strip()
    if not caso:
        return None
    from ..peso_propio import peso_especifico
    w, fL = peso_especifico(config, barras)
    signo = -1.0 if config["gravedad"].startswith("-") else 1.0
    peso = masa = 0.0
    for k, b in enumerate(barras):
        q = signo * w[k] * b.sec.A
        cargas_barra.setdefault(caso, []).append(CargaBarra(caso, k, b.id, "q", q, q, 0.0, b.L))
        peso += w[k] * b.sec.A * b.L
        masa += b.mat.rho * b.sec.A * b.L * fL ** 3
    return {"caso": caso, "gravedad": config["gravedad"], "peso": peso, "masa": masa, "nodal": False}


def _leer_barras(bloques, nodos, idx, materiales, secciones, avisos):
    barras, ids, pares = [], set(), {}
    xs = [nd.x for nd in nodos]
    ys = [nd.y for nd in nodos]
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
            raise ErrorDeEntrada(f"Bloque BARRAS, línea {n}: la barra '{id_}' tiene longitud nula (nodos coincidentes)")
        par = frozenset((i, j))
        if par in pares:
            avisos.append(f"Las barras '{pares[par]}' y '{id_}' unen los mismos dos nodos.")
        pares[par] = id_
        arts = []
        for campo in ("art_i", "art_j"):
            a = parsear_articulacion(r.get(campo))
            if a is None:
                raise ErrorDeEntrada(f"Bloque BARRAS, línea {n}: '{r.get(campo)}' no es válido en '{campo}' "
                                     "(usar vacío, m = flexión, t = torsión o mt)")
            arts.append(a)
        barras.append(Barra(id_, i, j, materiales[r["material"]], secciones[r["seccion"]], L, dx / L, dy / L, *arts))
    if not barras:
        raise ErrorDeEntrada("Bloque BARRAS: no hay barras")
    return barras


def _leer_apoyos(bloques, nodos, idx):
    restr = np.zeros((len(nodos), 3), dtype=bool)
    vistos = set()
    for n, r in _tabla(bloques, "APOYOS", ["nodo", "uz", "phix", "phiy"]):
        if r["nodo"] not in idx:
            raise ErrorDeEntrada(f"Bloque APOYOS, línea {n}: el nodo '{r['nodo']}' no existe")
        if r["nodo"] in vistos:
            raise ErrorDeEntrada(f"Bloque APOYOS, línea {n}: el nodo '{r['nodo']}' aparece dos veces")
        vistos.add(r["nodo"])
        k = idx[r["nodo"]]
        for c, campo in enumerate(("uz", "phix", "phiy")):
            restr[k, c] = _flag(r[campo], "APOYOS", n, campo)
    return restr


def _leer_resortes(bloques, nodos, idx):
    k_res = np.zeros((len(nodos), 3))
    filas = _tabla(bloques, "RESORTES", ["nodo", "kz", "kphix", "kphiy"], requerido=False)
    vistos = set()
    for n, r in filas or []:
        if r["nodo"] not in idx:
            raise ErrorDeEntrada(f"Bloque RESORTES, línea {n}: el nodo '{r['nodo']}' no existe")
        if r["nodo"] in vistos:
            raise ErrorDeEntrada(f"Bloque RESORTES, línea {n}: el nodo '{r['nodo']}' aparece dos veces")
        vistos.add(r["nodo"])
        for c, campo in enumerate(("kz", "kphix", "kphiy")):
            v = _num(r[campo], "RESORTES", n, campo, obligatorio=False, defecto=0.0)
            if v < 0:
                raise ErrorDeEntrada(f"Bloque RESORTES, línea {n}: {campo} no puede ser negativo")
            k_res[idx[r["nodo"]], c] = v
    return k_res


def _leer_resortes_giro(bloques, nodos, idx):
    """RESORTES GIRO INCLINADO:  nodo;k;angulo.

    Resorte de torsión cuyo eje está en el plano XY, a 'angulo' grados de +X (antihorario hacia +Y).
    Se opone a la componente del giro alrededor de ese eje:  θa = φx·cosβ + φy·senβ.
    Aporta  k·a·aᵀ  (a = [cosβ, senβ]) a los GDL φx, φy del nodo."""
    ctx = "RESORTES GIRO INCLINADO"
    out = []
    vistos = set()
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


def _leer_desajustes(bloques, nodos, idx, resortes, restr):
    """DESAJUSTE DE RESORTES:  caso;nodo;uz;phix;phiy.

    Desplazamiento impuesto al APOYO (extremo fijo) del resorte, en el sentido positivo del GDL.
    Fuerza del resorte sobre la estructura:  -k·(u - e).  Un resorte más corto que lo proyectado
    (hay que estirarlo para conectarlo) equivale a un apoyo corrido en sentido negativo: e < 0."""
    ctx = "DESAJUSTE DE RESORTES"
    out: dict = {}
    for n, r in _tabla(bloques, ctx, ["caso", "nodo", "uz", "phix", "phiy"], requerido=False) or []:
        if r["nodo"] not in idx:
            raise ErrorDeEntrada(f"Bloque {ctx}, línea {n}: el nodo '{r['nodo']}' no existe")
        k = idx[r["nodo"]]
        A = out.setdefault(r["caso"], np.zeros((len(nodos), 3)))
        for c, campo in enumerate(("uz", "phix", "phiy")):
            v = _num(r[campo], ctx, n, campo, obligatorio=False, defecto=0.0)
            if v != 0.0 and resortes[k, c] <= 0:
                raise ErrorDeEntrada(f"Bloque {ctx}, línea {n}: se da un desajuste en {campo} del nodo '{r['nodo']}', "
                                     "pero ese GDL no tiene resorte recto en RESORTES")
            if v != 0.0 and restr[k, c]:
                raise ErrorDeEntrada(f"Bloque {ctx}, línea {n}: el GDL {campo} del nodo '{r['nodo']}' está restringido "
                                     "en APOYOS: el resorte no actúa")
            A[k, c] += v
    return out


def _leer_cargas(bloques, nodos, idx):
    casos: dict = {}
    for n, r in _tabla(bloques, "CARGAS", ["caso", "nodo", "pz", "mx", "my"], requerido=False) or []:
        caso = r["caso"]
        if not caso:
            raise ErrorDeEntrada(f"Bloque CARGAS, línea {n}: falta el nombre del caso")
        if r["nodo"] not in idx:
            raise ErrorDeEntrada(f"Bloque CARGAS, línea {n}: el nodo '{r['nodo']}' no existe")
        F = casos.setdefault(caso, np.zeros((len(nodos), 3)))
        k = idx[r["nodo"]]
        for c, campo in enumerate(("pz", "mx", "my")):
            F[k, c] += _num(r[campo], "CARGAS", n, campo, obligatorio=False, defecto=0.0)
    return casos


def _leer_cargas_barra(bloques, barras, avisos):
    """Bloque CARGAS EN BARRAS:  caso;barra;tipo;valor;valor2;a;b   (ver cargas_barra.py)."""
    ctx = "CARGAS EN BARRAS"
    filas = _tabla(bloques, ctx, ["caso", "barra", "tipo", "valor"], requerido=False)
    por_id = {b.id: k for k, b in enumerate(barras)}
    out: dict = {}
    for n, r in filas or []:
        caso = r["caso"]
        if not caso:
            raise ErrorDeEntrada(f"Bloque {ctx}, línea {n}: falta el nombre del caso")
        if r["barra"] not in por_id:
            raise ErrorDeEntrada(f"Bloque {ctx}, línea {n}: la barra '{r['barra']}' no existe en BARRAS")
        k = por_id[r["barra"]]
        b = barras[k]
        tipo = r["tipo"].strip()
        tl = tipo.lower()
        tipo = {"q": "q", "p": "P", "temp": "temp", "t": "temp"}.get(tl)
        if tipo is None:
            raise ErrorDeEntrada(f"Bloque {ctx}, línea {n}: tipo '{r['tipo']}' desconocido "
                                 f"(tipos válidos: {', '.join(TIPOS_CARGA_BARRA)})")
        v1 = _num(r["valor"], ctx, n, "valor")
        v2 = _num(r.get("valor2"), ctx, n, "valor2", obligatorio=(tipo == "temp"))
        a = _num(r.get("a"), ctx, n, "a", obligatorio=(tipo == "P"), defecto=0.0)
        bb = _num(r.get("b"), ctx, n, "b", obligatorio=False, defecto=b.L)
        eps = 1e-9 * b.L
        if tipo == "q":
            if v2 is None:
                v2 = v1
            if not (-eps <= a < bb <= b.L + eps):
                raise ErrorDeEntrada(f"Bloque {ctx}, línea {n}: se exige 0 ≤ a < b ≤ L "
                                     f"(a={a:g}, b={bb:g}, L={b.L:g} de la barra '{b.id}')")
            a, bb = max(a, 0.0), min(bb, b.L)
        elif tipo == "P":
            if not (-eps <= a <= b.L + eps):
                raise ErrorDeEntrada(f"Bloque {ctx}, línea {n}: la posición a={a:g} está fuera de la barra "
                                     f"'{b.id}' (0 ≤ a ≤ L = {b.L:g})")
            a = min(max(a, 0.0), b.L)
            v2, bb = 0.0, a
        else:                                              # temp
            if not b.mat.alfa:
                raise ErrorDeEntrada(f"Bloque {ctx}, línea {n}: la carga térmica en la barra '{b.id}' "
                                     f"necesita 'alfa' en el material '{b.mat.id}' (bloque MATERIALES)")
            if not b.sec.h:
                raise ErrorDeEntrada(f"Bloque {ctx}, línea {n}: la carga térmica en la barra '{b.id}' "
                                     f"necesita la altura 'h' de la sección '{b.sec.id}' (bloque SECCIONES)")
            a, bb = 0.0, b.L
        out.setdefault(caso, []).append(CargaBarra(caso, k, b.id, tipo, v1, v2, a, bb))
    return out


def _leer_prefijados(bloques, nodos, idx, restr):
    filas = _tabla(bloques, "DESPLAZAMIENTOS PREFIJADOS", ["caso", "nodo", "uz", "phix", "phiy"], requerido=False)
    prefij: dict = {}
    ctx = "DESPLAZAMIENTOS PREFIJADOS"
    for n, r in filas or []:
        if r["nodo"] not in idx:
            raise ErrorDeEntrada(f"Bloque {ctx}, línea {n}: el nodo '{r['nodo']}' no existe")
        A = prefij.setdefault(r["caso"], np.zeros((len(nodos), 3)))
        k = idx[r["nodo"]]
        for c, campo in enumerate(("uz", "phix", "phiy")):
            v = _num(r[campo], ctx, n, campo, obligatorio=False, defecto=0.0)
            if v != 0.0 and not restr[k, c]:
                raise ErrorDeEntrada(
                    f"Bloque {ctx}, línea {n}: se prefija {campo}={v:g} en el nodo '{r['nodo']}', "
                    "pero ese GDL no está restringido en APOYOS")
            A[k, c] += v
    return prefij


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
