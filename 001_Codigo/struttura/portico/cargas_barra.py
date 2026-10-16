"""Cargas en el tramo de las barras del pórtico plano.

Todo se resuelve en ejes LOCALES de la barra (xl de i a j, yl a 90° antihorario, z hacia el lector).
Cada carga del CSV se descompone al leerla en sus componentes locales.

Tipos (bloque CARGAS EN BARRAS, columna 'tipo'):
    q      distribuida perpendicular a la barra (+yl), trapecial: valor en a, valor2 en b   [fuerza/longitud]
    qa     distribuida axial (+xl), trapecial
    qgx    distribuida en dirección X GLOBAL, por unidad de longitud de barra (trapecial)
    qgy    distribuida en dirección Y GLOBAL, por unidad de longitud de barra (trapecial)
    qgxp   distribuida en X global por unidad de longitud PROYECTADA sobre la vertical (p. ej. viento)
    qgyp   distribuida en Y global por unidad de longitud PROYECTADA sobre la horizontal (p. ej. nieve)
    P      puntual perpendicular (+yl) en a
    Pa     puntual axial (+xl) en a
    Pgx    puntual en X global en a
    Pgy    puntual en Y global en a
    Mp     momento puntual en a (positivo antihorario)
    dl     desajuste de longitud (barra larga +e / corta −e): axil de empotramiento E·A·e/L
    temp   variación de temperatura: valor = ΔT de la cara +yl, valor2 = ΔT de la cara −yl
           (necesita α en MATERIALES y h en SECCIONES; toda la barra; parte uniforme → axil,
            gradiente → flexión)
a y b se miden a lo largo de la barra desde el nodo i.

Método (consistente):  F_eq = ∫ Nᵀ q dx con las funciones de forma de la barra
    axial      N = [1−ξ, ξ]                          sobre [u_i, u_j]
    flexión    N = [H1, L·H2, H3, L·H4]              sobre [v_i, θ_i, v_j, θ_j]
    f0 = −F_eq (fuerzas de empotramiento perfecto, nodo sobre barra);  f = k·u + f0.
Esfuerzos (ver esfuerzos.py):
    N(x) = −Px_i − ∫qx          V(x) = Py_i + ∫qy          M(x) = −M_i + x·Py_i + ∫qy·(x−s)ds − Σ M0·H(x−a)
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from numpy.polynomial import Polynomial as Pol

TIPOS = ("q", "qa", "qgx", "qgy", "qgxp", "qgyp", "P", "Pa", "Pgx", "Pgy", "Mp", "temp", "dl")
_GX, _GW = np.polynomial.legendre.leggauss(4)          # exacto hasta grado 7
X = Pol([0.0, 1.0])


@dataclass
class CargaBarra:
    caso: str
    barra: int              # índice (0-based) en modelo.barras
    barra_id: str
    tipo: str               # 'q' (distribuida) | 'P' (puntual) | 'M' (momento puntual) | 'temp'
    orig: str               # tipo tal como se cargó (q, qgy, Pgx, ...)
    v1: float               # valor 1 tal como se cargó
    v2: float               # valor 2 tal como se cargó
    a: float
    b: float
    qx: tuple = (0.0, 0.0)  # q: componentes locales (en a, en b) según xl
    qy: tuple = (0.0, 0.0)  # q: componentes locales según yl
    Px: float = 0.0         # P: componentes locales
    Py: float = 0.0
    M0: float = 0.0         # M: momento puntual (antihorario +)
    Ts: float = 0.0         # temp: ΔT cara +yl
    Ti: float = 0.0         # temp: ΔT cara −yl
    e0: float = 0.0         # dl: desajuste de longitud (+ = barra LARGA, − = barra CORTA), en unidades de longitud


def descomponer(orig: str, v1: float, v2: float, g1: float, g2: float):
    """Componentes locales de una carga de valores v1, v2 dados en la dirección/criterio 'orig'.
    Devuelve ((qx1, qx2), (qy1, qy2)) para distribuidas o (Px, Py) para puntuales (usar v1)."""
    if orig in ("q", "P"):
        cx, cy = 0.0, 1.0
    elif orig in ("qa", "Pa"):
        cx, cy = 1.0, 0.0
    elif orig in ("qgx", "Pgx", "qgxp"):
        cx, cy = g1, -g2                      # global X: componente en xl y en yl
    elif orig in ("qgy", "Pgy", "qgyp"):
        cx, cy = g2, g1
    else:
        raise ValueError(orig)
    if orig == "qgxp":                        # por unidad de longitud proyectada sobre la vertical: × |senα|
        cx, cy = cx * abs(g2), cy * abs(g2)
    elif orig == "qgyp":                      # sobre la horizontal: × |cosα|
        cx, cy = cx * abs(g1), cy * abs(g1)
    return (cx * v1, cx * v2), (cy * v1, cy * v2)


# ---------------------------------------------------------------- funciones de forma
def _forma_flex(xi, L):
    xi = np.atleast_1d(np.asarray(xi, dtype=float))
    return np.array([1 - 3 * xi**2 + 2 * xi**3, L * (xi - 2 * xi**2 + xi**3),
                     3 * xi**2 - 2 * xi**3, L * (-xi**2 + xi**3)])


def _forma_ax(xi):
    xi = np.atleast_1d(np.asarray(xi, dtype=float))
    return np.array([1 - xi, xi])


def _dforma_flex(xi, L):
    """dN/dx de las funciones de flexión (para momentos puntuales)."""
    return np.array([(-6 * xi + 6 * xi**2) / L, 1 - 4 * xi + 3 * xi**2, (6 * xi - 6 * xi**2) / L, -2 * xi + 3 * xi**2])


def _lineal(v, a, b, x):
    """Valor en x de la variación lineal (v[0] en a, v[1] en b)."""
    return v[0] + (v[1] - v[0]) * (x - a) / (b - a)


# ---------------------------------------------------------------- térmica
def momento_termico(c: CargaBarra, barra) -> float:
    """M_T = E·I·α·(Ts − Ti)/h : momento flector (sagging +) que aparece al impedir la curvatura libre."""
    if c.Ts == c.Ti:
        return 0.0                                     # temperatura uniforme: no hace falta h
    return barra.mat.E * barra.sec.I * barra.mat.alfa * (c.Ts - c.Ti) / barra.sec.h


def axil_termico(c: CargaBarra, barra) -> float:
    """E·A·α·ΔTm con ΔTm = (Ts + Ti)/2: compresión que aparece al impedir la dilatación libre."""
    N = barra.mat.E * barra.sec.A * (barra.mat.alfa or 0.0) * (c.Ts + c.Ti) / 2
    return N + barra.mat.E * barra.sec.A * c.e0 / barra.L        # + desajuste: barra larga (e0 > 0) queda comprimida


# ---------------------------------------------------------------- equivalentes y empotramiento
def feq_local(c: CargaBarra, barra) -> np.ndarray:
    """Cargas nodales equivalentes consistentes (6,), ejes locales, con factor 1."""
    L = barra.L
    f = np.zeros(6)
    if c.tipo == "q":
        x = c.a + (c.b - c.a) * (_GX + 1) / 2
        w = _GW * (c.b - c.a) / 2
        xi = x / L
        f[[0, 3]] = _forma_ax(xi) @ (w * _lineal(c.qx, c.a, c.b, x))
        f[[1, 2, 4, 5]] = _forma_flex(xi, L) @ (w * _lineal(c.qy, c.a, c.b, x))
    elif c.tipo == "P":
        xi = c.a / L
        f[[0, 3]] = c.Px * _forma_ax(xi)[:, 0]
        f[[1, 2, 4, 5]] = c.Py * _forma_flex(xi, L)[:, 0]
    elif c.tipo == "M":
        f[[1, 2, 4, 5]] = c.M0 * _dforma_flex(c.a / L, L)
    elif c.tipo == "temp":
        MT, NT = momento_termico(c, barra), axil_termico(c, barra)
        f[0], f[3] = -NT, +NT
        f[2], f[5] = +MT, -MT
    return f


def f0_local(c: CargaBarra, barra) -> np.ndarray:
    """Fuerzas de empotramiento perfecto (nodo sobre barra), ejes locales:  f0 = −F_eq."""
    return -feq_local(c, barra)


# ---------------------------------------------------------------- esfuerzos por tramos (polinomios en x)
def _integral_q(v, a, b, xm):
    """(∫ q, ∫ q·(x−s) ds) hasta x, como polinomios en x, para el tramo de punto medio xm."""
    if xm <= a:
        return Pol([0.0]), Pol([0.0])
    m = (v[1] - v[0]) / (b - a)
    q1 = v[0]
    t = Pol([-a, 1.0])                                    # x − a
    if xm < b:
        return q1 * t + m * t**2 / 2, q1 * t**2 / 2 + m * t**3 / 6
    T = b - a
    Q = q1 * T + m * T**2 / 2
    G0 = q1 * T**2 / 2 + m * T**3 / 3                     # ∫ (s−a)·q ds
    return Pol([Q]), t * Q - G0


def cortes_barra(L, cargas) -> list:
    eps = 1e-9 * L
    cortes = {0.0, float(L)}
    for c, _ in cargas:
        xs = (c.a, c.b) if c.tipo == "q" else ((c.a,) if c.tipo in ("P", "M") else ())
        for xv in xs:
            if eps < xv < L - eps:
                cortes.add(float(xv))
    return sorted(cortes)


def piezas(L: float, fi, cargas) -> list:
    """Funciones exactas N(x), V(x), M(x) por tramos.

    fi = (Px_i, Py_i, M_i): fuerzas de extremo en i (nodo sobre barra, YA incluyen f0).
    cargas = [(CargaBarra, factor), ...] de esa barra (las térmicas no aportan: están en fi).
    Devuelve [{"x0", "x1", "N", "V", "M"}, ...] con polinomios numpy en x (desde i)."""
    Px, Py, Mi = fi
    cs = [(c, f) for c, f in cargas if c.tipo != "temp"]
    cortes = cortes_barra(L, cs)
    out = []
    for x0, x1 in zip(cortes[:-1], cortes[1:]):
        xm = (x0 + x1) / 2
        N, V, M = Pol([-Px]), Pol([Py]), Pol([-Mi]) + Py * X
        for c, f in cs:
            if c.tipo == "q":
                Fx, _ = _integral_q(c.qx, c.a, c.b, xm)
                Fy, My = _integral_q(c.qy, c.a, c.b, xm)
                N = N - f * Fx
                V = V + f * Fy
                M = M + f * My
            elif c.tipo == "P" and xm > c.a:
                N = N - f * c.Px
                V = V + f * c.Py
                M = M + f * c.Py * (X - c.a)
            elif c.tipo == "M" and xm > c.a:
                M = M - f * c.M0
        out.append({"x0": x0, "x1": x1, "N": N, "V": V, "M": M})
    return out


def evaluar(pz: list, x, s=None):
    """Evalúa N, V, M en las abscisas x.  s = -1/0/+1: lado desde el que se evalúa en los saltos."""
    x = np.asarray(x, dtype=float)
    s = np.zeros(x.shape, dtype=int) if s is None else np.asarray(s)
    cuts = np.array([p["x0"] for p in pz] + [pz[-1]["x1"]])
    idx = np.where(s > 0, np.searchsorted(cuts, x, side="right"), np.searchsorted(cuts, x, side="left")) - 1
    idx = np.clip(idx, 0, len(pz) - 1)
    N, V, M = np.zeros(x.shape), np.zeros(x.shape), np.zeros(x.shape)
    for k, p in enumerate(pz):
        m = idx == k
        if m.any():
            N[m], V[m], M[m] = p["N"](x[m]), p["V"](x[m]), p["M"](x[m])
    return N, V, M


def desplazamiento_particular(barra, cargas, x) -> tuple:
    """(u_p(x), v_p(x)): desplazamientos axial y transversal de la barra biempotrada bajo las cargas MECÁNICAS.

    EA·u_p' = N_p(x),  EI·v_p'' = M_p(x)  (M sagging +), con u_p(0)=v_p(0)=v_p'(0)=0.
    Las cargas térmicas no aportan (la deformación libre se cancela con la restringida)."""
    mec = [(c, f) for c, f in cargas if c.tipo != "temp"]
    x = np.asarray(x, dtype=float)
    if not mec:
        return np.zeros_like(x), np.zeros_like(x)
    L = barra.L
    f0 = sum(f * f0_local(c, barra) for c, f in mec)
    pz = piezas(L, (f0[0], f0[1], f0[2]), mec)
    EA, EI = barra.mat.E * barra.sec.A, barra.mat.E * barra.sec.I
    cuts = np.array([p["x0"] for p in pz] + [pz[-1]["x1"]])
    up, vp = np.zeros_like(x), np.zeros_like(x)
    u0 = th0 = v0 = 0.0                                   # valores al inicio de cada tramo (integración exacta)
    for k, p in enumerate(pz):
        x0, x1 = p["x0"], p["x1"]
        U = (p["N"] / EA).integ(lbnd=x0) + u0
        TH = (p["M"] / EI).integ(lbnd=x0) + th0
        V = TH.integ(lbnd=x0) + v0
        m = (x >= x0) & (x <= x1) if k == len(pz) - 1 else (x >= x0) & (x < x1)
        up[m], vp[m] = U(x[m]), V(x[m])
        u0, th0, v0 = U(x1), TH(x1), V(x1)
    return up, vp


def describir(c: CargaBarra) -> str:
    """Texto corto para tablas y gráficos."""
    return {"q": "q ⊥ a la barra", "qa": "q axial", "qgx": "q en X global", "qgy": "q en Y global",
            "qgxp": "q en X global (proyectada)", "qgyp": "q en Y global (proyectada)",
            "P": "P ⊥ a la barra", "Pa": "P axial", "Pgx": "P en X global", "Pgy": "P en Y global",
            "Mp": "momento puntual", "temp": "variación de temperatura", "dl": "desajuste de longitud"}[c.orig]
