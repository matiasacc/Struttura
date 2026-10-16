"""Biblioteca de perfiles: UN solo archivo CSV (006_Biblioteca/perfiles.csv, o el que indique STRUTTURA_PERFILES).
Contiene las tablas del Reglamento CIRSOC 301-EL / 302-EL (perfiles laminados y tubos); los valores están copiados tal cual figuran en las tablas y quedan
en sus unidades (mm, cm, cm², cm³, cm⁴, cm⁶, kg/m: la unidad va en el nombre de cada columna).  Este módulo los pasa a las unidades del modelo.
El archivo se genera con biblioteca/_fuente/construir_perfiles.py."""
import csv
import os
from pathlib import Path

from .biblioteca import ErrorBiblioteca


def archivo() -> Path:
    env = os.environ.get("STRUTTURA_PERFILES")
    return Path(env) if env else Path(__file__).resolve().parents[3] / "006_Biblioteca" / "perfiles.csv"


def _leer():
    p = archivo()
    if not p.is_file():
        return []
    with p.open(encoding="utf-8-sig", newline="") as fh:
        return [{k: (v or "").strip() for k, v in r.items()} for r in csv.DictReader(fh, delimiter=";")]


def listar():
    """[(n, ref, familia)] para el desplegable del editor."""
    return [(r["n"], r["ref"], r["familia"]) for r in _leer()]


def cargar(n):
    for r in _leer():
        if r["n"] == str(n).strip() or r["ref"].lower() == str(n).strip().lower():
            return r
    raise ErrorBiblioteca(f"el perfil '{n}' no está en la biblioteca de perfiles ({archivo()}).")


def _v(r, col):
    x = r.get(col, "")
    if x == "":
        return None
    try:
        return float(x.replace(",", "."))
    except ValueError:
        raise ErrorBiblioteca(f"perfil '{r.get('ref')}': {col} dice '{x}', que no es un número")


def datos_modelo(lib, destino, unidad_longitud):
    """Datos del perfil n.º `lib` en la unidad de longitud del modelo.

    destino: "3d" (a, iy, iz, j, cy, cz, wt, h), "plano" (i, a, c, h) o "emparrillado" (i, j, a, c, wt, h).
    Eje fuerte del catálogo (x-x, con la altura d) → i / iy, el del plano del pórtico; y-y → iz.  Devuelve (campos, ref, avisos);
    un dato que la tabla no trae no aparece en `campos` (queda a cargo del usuario)."""
    from ..portico3d.entrada import _U_LONG
    ul = unidad_longitud.strip().lower()
    if ul not in _U_LONG:
        raise ErrorBiblioteca(f"no sé convertir la unidad de longitud '{unidad_longitud}' para leer la biblioteca de perfiles; cargá los valores a mano")
    r = cargar(lib)
    cm = 0.01 / _U_LONG[ul]                                  # cm → unidad del modelo
    mm = 0.001 / _U_LONG[ul]
    g = lambda col, k: (None if _v(r, col) is None else _v(r, col) * k)
    A, Ix, Iy, J = g("Ag_cm2", cm ** 2), g("Ix_cm4", cm ** 4), g("Iy_cm4", cm ** 4), g("J_cm4", cm ** 4)
    d, b = g("d_mm", mm), g("b_mm", mm)
    forma, avisos = r["forma"], []
    cz = cy = None
    if forma in ("I", "circular", "cuadrado", "rectangular", "canal"):
        cz = d / 2 if d is not None else None
    if forma in ("I", "circular", "cuadrado", "rectangular"):
        cy = b / 2 if b is not None else None
    if forma == "canal":
        e = g("ey_cm", cm) if r.get("ey_cm") else g("xbar_cm", cm)          # distancia del centro de gravedad a la cara externa del alma
        cy = max(e, b - e) if (e is not None and b is not None) else None
    if forma == "T":
        dx = g("dx_cm", cm)                                                 # del centro de gravedad al borde del ala
        cz = max(dx, d - dx) if (dx is not None and d is not None) else None
        cy = b / 2 if b is not None else None
    if forma == "L":
        avisos.append(f"Perfil '{r['ref']}': ángulo; se usan los momentos de inercia respecto de ejes paralelos a las alas (Ix = Iy).  La tabla trae también los ejes principales "
                      "(Iv, Iz); la flexión asimétrica del ángulo no se considera.")
    wt = g("C_cm3", cm ** 3)
    if destino == "3d":
        campos = {"a": A, "iy": Ix, "iz": Iy, "j": J, "cy": cy, "cz": cz, "wt": wt, "h": d}
    elif destino == "plano":
        campos = {"i": Ix, "a": A, "c": cz, "h": d}
    else:
        campos = {"i": Ix, "j": J, "a": A, "c": cz, "wt": wt, "h": d}
    return {k: v for k, v in campos.items() if v is not None}, r["ref"], avisos


def expandir(fila, destino, config, n, avisos):
    """Fila de SECCIONES con tipo 'perfil': la completa con los datos de la biblioteca y la convierte en 'generica'.  Lo escrito a mano manda."""
    lib = (fila.get("lib") or "").strip()
    if not lib:
        raise ErrorBiblioteca(f"Bloque SECCIONES, línea {n}: el tipo 'perfil' necesita el número de la biblioteca de perfiles en la columna lib")
    campos, ref, av = datos_modelo(lib, destino, config["unidad_longitud"])
    for a in av:
        if a not in avisos:
            avisos.append(a)
    out = dict(fila)
    out["tipo"] = "generica"
    for k, v in campos.items():
        if (out.get(k) or "").strip() == "":
            out[k] = repr(v)
    out["_perfil"] = f"Perfil {ref} (biblioteca de perfiles n.º {cargar(lib)['n']})"
    return out
