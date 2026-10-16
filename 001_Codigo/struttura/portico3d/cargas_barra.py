"""Cargas en el tramo de las barras espaciales: cargas equivalentes nodales (consistentes) y esfuerzos exactos.

Tipos de carga (columna 'tipo' de CARGAS EN BARRAS; valor y valor2 según el tipo):
    qx qy qz      distribuida en ejes LOCALES de la barra [fuerza/longitud]; valor = en i, valor2 = en j (vacío = uniforme)
    qgx qgy qgz   distribuida en ejes GLOBALES (por unidad de longitud de barra); mismo criterio de valor/valor2
    Px Py Pz      fuerza puntual LOCAL a la distancia a del nudo i
    Pgx Pgy Pgz   fuerza puntual en ejes GLOBALES a la distancia a del nudo i
    Mx My Mz      momento puntual LOCAL (vector según el eje) a la distancia a del nudo i
    Mgx Mgy Mgz   momento puntual en ejes GLOBALES a la distancia a del nudo i

Todas las cargas se convierten a tres formas locales:  ('q', q_i, q_j)  |  ('P', a, F)  |  ('M', a, M)
con vectores (3,) en ejes locales.  Las cargas equivalentes se integran con las mismas funciones de forma de la
matriz de rigidez (consistentes) y los esfuerzos internos salen del equilibrio del tramo (exactos).
"""
from __future__ import annotations

import numpy as np

TIPOS = ("qx", "qy", "qz", "qgx", "qgy", "qgz", "Px", "Py", "Pz", "Pgx", "Pgy", "Pgz",
         "Mx", "My", "Mz", "Mgx", "Mgy", "Mgz")
_EJE = {"x": 0, "y": 1, "z": 2}


def clasificar(tipo: str):
    """('q'|'P'|'M', global?, eje)"""
    t = tipo
    glob = len(t) == 3
    return t[0].lower() if t[0] == "q" else t[0], glob, _EJE[t[-1]]


def convertir(tipo, v1, v2, a, R):
    """Carga en la forma local interna.  R: matriz 3×3 global→local."""
    clase, glob, eje = clasificar(tipo)
    e = np.zeros(3)
    e[eje] = 1.0
    if glob:
        e = R @ e                                   # vector unitario global expresado en ejes locales
    if clase == "q":
        return ("q", e * v1, e * (v1 if v2 is None else v2))
    return (clase, a, e * v1)


def _formas(x, L):
    """Funciones de forma (vectores de 12) y sus derivadas en x."""
    s = x / L
    n1 = 1 - 3 * s**2 + 2 * s**3
    n2 = L * (s - 2 * s**2 + s**3)
    n3 = 3 * s**2 - 2 * s**3
    n4 = L * (-(s**2) + s**3)
    d1 = (-6 * s + 6 * s**2) / L
    d2 = 1 - 4 * s + 3 * s**2
    d3 = (6 * s - 6 * s**2) / L
    d4 = -2 * s + 3 * s**2
    Nu = np.zeros(12); Nu[0], Nu[6] = 1 - s, s
    Nt = np.zeros(12); Nt[3], Nt[9] = 1 - s, s
    Nv = np.zeros(12); Nv[1], Nv[5], Nv[7], Nv[11] = n1, n2, n3, n4
    Nw = np.zeros(12); Nw[2], Nw[4], Nw[8], Nw[10] = n1, -n2, n3, -n4
    dNv = np.zeros(12); dNv[1], dNv[5], dNv[7], dNv[11] = d1, d2, d3, d4
    dNw = np.zeros(12); dNw[2], dNw[4], dNw[8], dNw[10] = d1, -d2, d3, -d4
    return Nu, Nv, Nw, Nt, dNv, dNw


_GX, _GW = np.polynomial.legendre.leggauss(6)      # exacto hasta grado 11


def equivalente_local(carga, L) -> np.ndarray:
    """Cargas nodales equivalentes (12,) en ejes locales, que actúan sobre los nudos."""
    f = np.zeros(12)
    if carga[0] == "q":
        qi, qj = carga[1], carga[2]
        for g, w in zip(_GX, _GW):
            x = L * (g + 1) / 2
            q = qi + (qj - qi) * x / L
            Nu, Nv, Nw, _, _, _ = _formas(x, L)
            f += (q[0] * Nu + q[1] * Nv + q[2] * Nw) * w * L / 2
    elif carga[0] == "P":
        _, a, F = carga
        Nu, Nv, Nw, _, _, _ = _formas(a, L)
        f += F[0] * Nu + F[1] * Nv + F[2] * Nw
    else:
        _, a, M = carga
        _, _, _, Nt, dNv, dNw = _formas(a, L)
        f += M[0] * Nt + M[2] * dNv - M[1] * dNw     # θz = v' ;  θy = -w'
    return f


def resultante_izquierda(carga, x):
    """Fuerza (3,) y momento (3,) respecto del punto x (ejes locales) de la carga aplicada en [0, x]."""
    if carga[0] == "q":
        qi, qj = carga[1], carga[2]
        L = carga[3]
        m = (qj - qi) / L
        F = qi * x + m * x**2 / 2
        I1 = qi * x**2 / 2 + m * x**3 / 6           # ∫0^x (x-s) q(s) ds
        # r × q con r = (s-x, 0, 0):  My = ∫ (x-s) qz ds ;  Mz = ∫ (s-x) qy ds = -∫ (x-s) qy ds
        M = np.array([0.0, I1[2], -I1[1]])
        return F, M
    if carga[0] == "P":
        _, a, Fp = carga
        return Fp, np.array([0.0, (x - a) * Fp[2], -(x - a) * Fp[1]])
    _, a, Mp = carga
    return np.zeros(3), Mp


def agregar_longitud(carga, L):
    return carga + (L,) if carga[0] == "q" else carga


def esfuerzos_en(x, Fi, Mi, cargas, L, despues=True):
    """Esfuerzos internos [N, Vy, Vz, T, My, Mz] sobre la cara +x de la sección x (equilibrio del tramo izquierdo).

    Fi, Mi: fuerzas y momentos que actúan sobre la barra en el extremo i (ejes locales).
    despues: en la abscisa de una carga puntual, incluye (True) o no (False) la carga.
    """
    F = np.array(Fi, float)
    M = np.array(Mi, float) + np.array([0.0, x * Fi[2], -x * Fi[1]])
    for c in cargas:
        if c[0] == "q":
            f, m = resultante_izquierda(c, x)
        else:
            a = c[1]
            if a < x or (despues and abs(a - x) <= 1e-9 * L):
                f, m = resultante_izquierda(c, x)
            else:
                continue
        F = F + f
        M = M + m
    return np.array([-F[0], -F[1], -F[2], -M[0], -M[1], -M[2]])
