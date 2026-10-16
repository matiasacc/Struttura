"""Datos tabulados de soldadura (de los libros) y conversión de unidades.

Fuentes:
  Tabla 9-3 de Shigley (ed. 2024, p. 511) y Anexo 2 del Compendio cap. 18: resistencias de electrodos AWS.
  Tabla 9-6 Cuadro A de Shigley (p. 513): corte admisible en la garganta del filete (ksi).
  Tabla 9-6 Cuadro B de Shigley (p. 513): pie mínimo de filete según el espesor de la pieza más gruesa (pulgadas).
  Tabla 9-4 de Shigley (p. 512): el corte en el metal base no debe exceder 0,40·Sy del base.
Orden de búsqueda de un electrodo: 1) bloque ELECTRODOS del CSV del modelo (a mano), 2) 006_Biblioteca/electrodos.csv, 3) esta tabla (si no hay biblioteca).
"""
from __future__ import annotations

KSI_MPA = 6.894757293168361                  # 1 ksi en MPa (1 ksi = 1000 psi)
IN_MM = 25.4

U_FUERZA = {"n": 1.0, "kn": 1e3, "mn": 1e6, "kgf": 9.80665, "tf": 9806.65, "lbf": 4.4482216, "kip": 4448.2216}   # en N
U_LONG = {"mm": 1.0, "cm": 10.0, "m": 1000.0, "in": 25.4, "ft": 304.8}                                           # en mm


def fac_tension(uf: str, ul: str) -> float:
    """Factor que pasa MPa (N/mm²) a fuerza/longitud² de las unidades del modelo."""
    return (1.0 / U_FUERZA[uf.lower()]) * (U_LONG[ul.lower()] ** 2)


# id: (Sut ksi, Sy ksi, τ_adm ksi) — Tabla 9-3 (Sut, Sy) y Tabla 9-6 Cuadro A (τ_adm).  E110 no figura en la Tabla 9-3.
ELECTRODOS = {
    "E60": (62.0, 50.0, 18.0),
    "E70": (70.0, 57.0, 21.0),
    "E80": (80.0, 67.0, 24.0),
    "E90": (90.0, 77.0, 27.0),
    "E100": (100.0, 87.0, 30.0),
    "E110": (None, None, 33.0),
    "E120": (120.0, 107.0, 36.0),
}

# Cuadro B: (espesor máx. de la pieza más gruesa [in], pie mínimo [in]); la última fila no tiene tope.
FILETE_MINIMO = [(0.25, 1 / 8), (0.5, 3 / 16), (0.75, 1 / 4), (1.5, 5 / 16), (2.25, 3 / 8), (6.0, 1 / 2), (float("inf"), 5 / 8)]


def electrodo(nombre: str, extra: dict | None = None):
    """(Sut, Sy, τ_adm) en MPa; None donde no hay dato.  'extra' = electrodos del usuario {id: (sut, sy, tau_adm)} en MPa."""
    k = nombre.strip().upper().replace("XX", "")
    if extra and nombre.strip() in extra:
        return extra[nombre.strip()]
    if extra and k in {e.upper() for e in extra}:
        for e, v in extra.items():
            if e.upper() == k:
                return v
    from ..biblioteca import electrodos as _lib            # biblioteca de electrodos (CSV): entre lo escrito a mano y la tabla interna
    if _lib.existe():
        r = _lib.buscar(nombre.strip()) or _lib.buscar(k)
        if r is not None:
            return _lib.datos(r["id"])
    if k not in ELECTRODOS:
        raise KeyError(k)
    su, sy, ta = ELECTRODOS[k]
    return (None if su is None else su * KSI_MPA, None if sy is None else sy * KSI_MPA, ta * KSI_MPA)


def filete_minimo_mm(espesor_grueso_mm: float) -> float:
    """Pie mínimo [mm] (Tabla 9-6 Cuadro B) para el espesor [mm] de la pieza más gruesa."""
    t_in = espesor_grueso_mm / IN_MM
    for tope, h in FILETE_MINIMO:
        if t_in <= tope + 1e-12:
            return h * IN_MM
    return FILETE_MINIMO[-1][1] * IN_MM


_CANON = {"n": "N", "kn": "kN", "mn": "MN", "kgf": "kgf", "tf": "tf", "lbf": "lbf", "kip": "kip"}


def canon(u: str) -> str:
    """Nombre de unidad para mostrar (kN, N, mm...)."""
    return _CANON.get(u.lower(), u)
