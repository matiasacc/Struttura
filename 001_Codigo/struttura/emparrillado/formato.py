"""Formato de números para tablas y gráficos."""
from __future__ import annotations

import math

import numpy as np


def _vacio(v) -> bool:
    return v is None or (isinstance(v, float) and math.isnan(v))


def fg(v, cifras: int = 5) -> str:
    """Formato general: 'cifras' cifras significativas; notación científica fuera de [1e-3, 1e7)."""
    if _vacio(v):
        return "–"
    v = float(v)
    if v == 0.0:
        return "0"
    a = abs(v)
    if 1e-3 <= a < 1e7:
        s = np.format_float_positional(v, precision=cifras, unique=False, fractional=False, trim="-")
        return s
    return f"{v:.{cifras - 1}E}"


def fe(v, dec: int = 4) -> str:
    """Notación científica con 'dec' decimales (para desplazamientos y giros)."""
    if _vacio(v):
        return "–"
    v = float(v)
    return "0" if v == 0.0 else f"{v:.{dec}E}"


def limpiar(a, rel: float = 1e-9):
    """Pone en cero los valores que son ruido numérico respecto del máximo de la columna."""
    a = np.array(a, dtype=float, copy=True)
    m = np.abs(a).max() if a.size else 0.0
    a[np.abs(a) < rel * m] = 0.0
    return a
