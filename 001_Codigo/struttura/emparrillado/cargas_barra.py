"""Cargas en el tramo de las barras.

Todo se resuelve en ejes LOCALES de la barra (xl de i a j, z común y hacia arriba):
las cargas son perpendiculares al plano, así que z local = z global y no hace falta rotarlas.

Tipos de carga (bloque CARGAS EN BARRAS):
    q     carga distribuida en z [fuerza/longitud], positiva hacia +z.
          valor = q en el punto 'a'; valor2 = q en el punto 'b' (vacío = igual a valor → uniforme).
          a y b: distancias medidas desde el nodo i (vacíos = toda la barra).
    P     fuerza puntual en z [fuerza], positiva hacia +z, a la distancia 'a' desde el nodo i.
    temp  gradiente térmico lineal en la altura: valor = ΔT de la fibra superior (+z),
          valor2 = ΔT de la fibra inferior.  Requiere α (MATERIALES) y h (SECCIONES).
          Toda la barra.  (La parte uniforme de ΔT produce solo axil, que el emparrillado no tiene.)

Método (más simple que separar estados 0/1/2 a mano, pero equivalente):
    * Cargas nodales equivalentes CONSISTENTES:  F_eq = ∫ Nᵀ q dx   con las funciones de forma
      de Hermite N = [H1, -L·H2, H3, -L·H4] sobre los GDL locales [uz_i, φy_i, uz_j, φy_j]
      (el signo de H2, H4 sale de θy = -dw/dx).
    * Fuerzas de empotramiento perfecto (nodo sobre barra):  f0 = -F_eq.
      Son las que la tabla de "Estados Biempotrados" da a mano.
    * Se resuelve  K·u = F + ΣF_eq  y las fuerzas de extremo de barra son  f = k·u_loc + f0.
    * Con las fuerzas de extremo (f) se reconstruyen V(x) y M(x) sumando la carga en el tramo.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

TIPOS = ("q", "P", "temp")
_GAUSS_X, _GAUSS_W = np.polynomial.legendre.leggauss(4)     # exacto hasta grado 7
_IDX = [0, 2, 3, 5]                                          # uz_i, φy_i, uz_j, φy_j dentro de los 6 GDL


@dataclass
class CargaBarra:
    caso: str
    barra: int              # índice (0-based) en modelo.barras
    barra_id: str
    tipo: str               # 'q' | 'P' | 'temp'
    v1: float               # q en a  |  P  |  ΔT superior
    v2: float               # q en b  |  -  |  ΔT inferior
    a: float                # distancia desde el nodo i
    b: float                # (solo q) distancia desde el nodo i


def _forma(xi, L):
    """Funciones de forma (uz_i, φy_i, uz_j, φy_j) en xi=x/L: arreglo (4, len(xi))."""
    xi = np.atleast_1d(np.asarray(xi, dtype=float))
    H1 = 1 - 3 * xi**2 + 2 * xi**3
    H2 = xi - 2 * xi**2 + xi**3
    H3 = 3 * xi**2 - 2 * xi**3
    H4 = -xi**2 + xi**3
    return np.array([H1, -L * H2, H3, -L * H4])


def _q_en(c: CargaBarra, x):
    m = (c.v2 - c.v1) / (c.b - c.a)
    return c.v1 + m * (x - c.a)


def curvatura_termica(c: CargaBarra, barra) -> float:
    """κ_T = α (ΔTsup - ΔTinf) / h  (positiva si la fibra superior se calienta más)."""
    return barra.mat.alfa * (c.v1 - c.v2) / barra.sec.h


def momento_termico(c: CargaBarra, barra) -> float:
    """M_T = E·I·κ_T: momento de empotramiento (sentido flector positivo = tracciona abajo)."""
    return barra.mat.E * barra.sec.I * curvatura_termica(c, barra)


def feq_local(c: CargaBarra, barra) -> np.ndarray:
    """Cargas nodales equivalentes (6,) en ejes locales, con el factor 1."""
    L = barra.L
    f = np.zeros(6)
    if c.tipo == "q":
        x = c.a + (c.b - c.a) * (_GAUSS_X + 1) / 2
        w = _GAUSS_W * (c.b - c.a) / 2
        N = _forma(x / L, L)                                  # (4, ng)
        f[_IDX] = N @ (w * _q_en(c, x))
    elif c.tipo == "P":
        f[_IDX] = c.v1 * _forma(c.a / L, L)[:, 0]
    elif c.tipo == "temp":
        MT = momento_termico(c, barra)
        f[2], f[5] = -MT, +MT
    return f


def f0_local(c: CargaBarra, barra) -> np.ndarray:
    """Fuerzas de empotramiento perfecto (nodo sobre barra), ejes locales: f0 = -F_eq."""
    return -feq_local(c, barra)


def sumar(cargas, barra, fun) -> np.ndarray:
    """Suma fun(carga, barra)*factor sobre una lista de (CargaBarra, factor) de ESA barra."""
    tot = np.zeros(6)
    for c, fac in cargas:
        tot += fac * fun(c, barra)
    return tot


def cortante_carga(c: CargaBarra, x):
    """Aporte de la carga en el tramo al cortante V(x) (suma de fuerzas z entre 0 y x)."""
    x = np.asarray(x, dtype=float)
    if c.tipo == "q":
        t = np.clip(x, c.a, c.b) - c.a
        m = (c.v2 - c.v1) / (c.b - c.a)
        return c.v1 * t + m * t**2 / 2
    if c.tipo == "P":
        return np.where(x >= c.a, c.v1, 0.0)
    return np.zeros_like(x)


def momento_carga(c: CargaBarra, x):
    """Aporte de la carga en el tramo al flector M(x) (positivo tracciona abajo)."""
    x = np.asarray(x, dtype=float)
    if c.tipo == "q":
        t = np.clip(x, c.a, c.b) - c.a
        d = np.maximum(x - c.a, 0.0)
        m = (c.v2 - c.v1) / (c.b - c.a)
        return c.v1 * (d * t - t**2 / 2) + m * (d * t**2 / 2 - t**3 / 3)
    if c.tipo == "P":
        return c.v1 * np.maximum(x - c.a, 0.0)
    return np.zeros_like(x)


def esfuerzos_en(barra, fb_i, cargas, x):
    """V(x) y M(x) en las abscisas x (desde el nodo i).

    fb_i = (Pz_i, My_i): fuerzas de extremo en i (nodo sobre barra) que YA incluyen f0.
    cargas = lista de (CargaBarra, factor) de esa barra.
    """
    x = np.asarray(x, dtype=float)
    Pz, My = fb_i
    V = Pz + np.zeros_like(x)
    M = My + x * Pz
    for c, fac in cargas:
        V = V + fac * cortante_carga(c, x)
        M = M + fac * momento_carga(c, x)
    return V, M


def flecha_particular(barra, cargas, x) -> np.ndarray:
    """w_p(x): flecha de la barra biempotrada bajo las cargas MECÁNICAS del tramo.

    EI·w'' = M_p(x) con w(0)=w'(0)=0 (ambos extremos empotrados → w(L)=0).
    El gradiente térmico no aporta: la curvatura libre se cancela con la restringida.
    """
    mec = [(c, f) for c, f in cargas if c.tipo != "temp"]
    x = np.asarray(x, dtype=float)
    if not mec:
        return np.zeros_like(x)
    L = barra.L
    xf = np.linspace(0.0, L, 1601)
    f0 = sum(f * f0_local(c, barra) for c, f in mec)
    Mp = f0[2] + xf * f0[0]
    for c, fac in mec:
        Mp = Mp + fac * momento_carga(c, xf)
    kap = Mp / (barra.mat.E * barra.sec.I)
    h = xf[1] - xf[0]
    th = np.concatenate([[0.0], np.cumsum((kap[1:] + kap[:-1]) / 2 * h)])
    w = np.concatenate([[0.0], np.cumsum((th[1:] + th[:-1]) / 2 * h)])
    return np.interp(x, xf, w)
