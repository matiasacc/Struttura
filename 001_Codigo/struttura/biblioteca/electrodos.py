"""Biblioteca personal de electrodos: UN solo archivo CSV (006_Biblioteca/electrodos.csv, o el que indique STRUTTURA_ELECTRODOS).

Mismo criterio que la de materiales: una fila por electrodo con número permanente (n); los datos que faltan quedan vacíos.
Columnas: n ; id ; sut_MPa ; sy_MPa ; tau_adm_MPa ; fuente ; notas
Se usa por el nombre (columna id) en SOLDADURAS: electrodo;E70   — lo escrito a mano en el bloque ELECTRODOS manda sobre la biblioteca.
Si el archivo no existe, el programa usa la tabla de Shigley que trae en el código (datos.ELECTRODOS)."""
import csv
import os
from pathlib import Path

from .biblioteca import ErrorBiblioteca

COLUMNAS = ["n", "id", "sut_MPa", "sy_MPa", "tau_adm_MPa", "fuente", "notas"]


def archivo() -> Path:
    env = os.environ.get("STRUTTURA_ELECTRODOS")
    return Path(env) if env else Path(__file__).resolve().parents[3] / "006_Biblioteca" / "electrodos.csv"


def _leer():
    p = archivo()
    if not p.is_file():
        return []
    with p.open(encoding="utf-8-sig", newline="") as fh:
        return [{k: (v or "").strip() for k, v in r.items()} for r in csv.DictReader(fh, delimiter=";")]


def listar():
    return [(r["n"], r["id"]) for r in _leer()]


def existe() -> bool:
    return archivo().is_file()


def cargar(ref):
    """Busca por número (n) o por id (sin distinguir mayúsculas)."""
    k = str(ref).strip().lower()
    for r in _leer():
        if r["n"] == k or r["id"].lower() == k:
            return r
    raise ErrorBiblioteca(f"el electrodo '{ref}' no está en la biblioteca de electrodos ({archivo()}).")


def buscar(ref):
    """Como cargar, pero devuelve None si no está."""
    try:
        return cargar(ref)
    except ErrorBiblioteca:
        return None


def _num(txt, ref, campo):
    if txt == "":
        return None
    try:
        return float(txt.replace(",", "."))
    except ValueError:
        raise ErrorBiblioteca(f"electrodo '{ref}': {campo} dice '{txt}', que no es un número")


def datos(ref):
    """(Sut, Sy, τ_adm) en MPa; None donde el CSV está vacío.  Exige τ_adm."""
    r = cargar(ref)
    d = tuple(_num(r[c], r["id"], c) for c in ("sut_MPa", "sy_MPa", "tau_adm_MPa"))
    if d[2] is None:
        raise ErrorBiblioteca(f"electrodo '{r['id']}' (n.º {r['n']}): falta tau_adm_MPa en la biblioteca; cargalo a mano en ELECTRODOS")
    return d


def sy_base(lib, unidad_fuerza, unidad_longitud):
    """Fluencia del metal base (unidades del modelo) tomada del material n.º 'lib' de la biblioteca de materiales."""
    from .biblioteca import datos_modelo
    d = datos_modelo(lib, unidad_fuerza, unidad_longitud)
    if d["fy"] is None:
        raise ErrorBiblioteca(f"el material n.º {lib} de la biblioteca no tiene fy; cargá sy_base a mano")
    return d["fy"]
