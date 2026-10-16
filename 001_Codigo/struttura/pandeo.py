"""Pandeo de Euler por barra (igual en reticulado, pórtico plano y pórtico espacial 3D).

Carga crítica  Pc = π²·E·I / (K·L)²  con la condición de extremos de la tabla de la cátedra:
    empotrado–libre π²EI/(4L²) · articulado–articulado π²EI/L² · empotrado–articulado 2π²EI/L² · empotrado–empotrado 4π²EI/L²
CS pandeo = Pc / |N| en barras comprimidas.  La condición de extremos la elige el diseñador (columna `pandeo` de BARRAS, por defecto art-art)."""
from __future__ import annotations

import math
import unicodedata

# condición de extremos: código → (rótulo, factor de longitud efectiva K)
# (empotrado-articulado: la tabla usa Pc = 2π²EI/L², es decir K = 1/√2)
PANDEO = {
    "art-art": ("articulado – articulado", 1.0),
    "emp-lib": ("empotrado – libre", 2.0),
    "emp-art": ("empotrado – articulado", 1.0 / math.sqrt(2.0)),
    "emp-emp": ("empotrado – empotrado", 0.5),
}
ALIAS = {"": "art-art", "aa": "art-art", "art-art": "art-art", "articulado-articulado": "art-art", "biarticulado": "art-art",
         "el": "emp-lib", "emp-lib": "emp-lib", "empotrado-libre": "emp-lib", "voladizo": "emp-lib",
         "ea": "emp-art", "emp-art": "emp-art", "empotrado-articulado": "emp-art",
         "ee": "emp-emp", "emp-emp": "emp-emp", "empotrado-empotrado": "emp-emp", "biempotrado": "emp-emp"}
VALORES = "art-art (defecto), emp-lib, emp-art, emp-emp"


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s.strip().lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def codigo(txt):
    """Código normalizado a partir del texto de la columna `pandeo`; None si no es válido."""
    c = _norm(txt or "").replace(" ", "").replace("_", "-").replace("–", "-")
    return ALIAS.get(c)


def carga_critica(E: float, I: float, L: float, cod: str) -> float:
    return math.pi ** 2 * E * I / (PANDEO[cod][1] * L) ** 2


def verificar(E: float, I, A, L: float, cod: str, Nmin: float) -> dict:
    """{Pc, lam, n_pand} (None donde no hay dato).  n_pand solo si hay compresión (Nmin < 0)."""
    d = {"cod": cod, "Pc": None, "lam": None, "n_pand": None}
    if not I or not A:
        return d
    d["Pc"] = carga_critica(E, I, L, cod)
    d["lam"] = PANDEO[cod][1] * L / math.sqrt(I / A)
    if Nmin < -1e-9 * d["Pc"]:                       # compresión (no cuenta el ruido numérico)
        d["n_pand"] = d["Pc"] / abs(Nmin)
    return d
