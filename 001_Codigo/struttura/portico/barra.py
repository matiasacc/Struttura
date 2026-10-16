"""Matrices de la barra de pórtico plano (tabla de cátedra).

GDL por nodo (en este orden):  ux, uy, φ      (φ positivo antihorario; z hacia el lector)

Constantes:  K = A·E/L,  K1 = 12·E·I/L³,  K2 = 6·E·I/L²,  K3 = 4·E·I/L

Rotación:   v_glo = R · v_loc,     R = [[γ1, -γ2, 0], [γ2, γ1, 0], [0, 0, 1]]
            γ1 = cos α = Δx/L,  γ2 = sen α = Δy/L         (α: ángulo de xl respecto de X)
Matriz global de la barra:  k_glo = T · k_loc · Tᵀ,  T = diag(R, R).

Articulaciones (rótulas) en los extremos: se condensa el giro del extremo articulado
(condensación estática); ver `condensar`.
"""
from __future__ import annotations

import numpy as np

NOMBRES_GDL = ("ux", "uy", "φ")


def matriz_rotacion(g1: float, g2: float) -> np.ndarray:
    """T (6x6) tal que  u_glo = T @ u_loc."""
    R = np.array([[g1, -g2, 0.0],
                  [g2, g1, 0.0],
                  [0.0, 0.0, 1.0]])
    T = np.zeros((6, 6))
    T[:3, :3] = R
    T[3:, 3:] = R
    return T


def constantes(E: float, A: float, I: float, L: float):
    """K, K1, K2, K3 de la tabla."""
    return A * E / L, 12 * E * I / L**3, 6 * E * I / L**2, 4 * E * I / L


def rigidez_local(E: float, A: float, I: float, L: float) -> np.ndarray:
    """k_loc (6x6) de la barra sobre el eje xl, GDL [u_i, v_i, θ_i, u_j, v_j, θ_j]."""
    K, K1, K2, K3 = constantes(E, A, I, L)
    return np.array([
        [K, 0.0, 0.0, -K, 0.0, 0.0],
        [0.0, K1, K2, 0.0, -K1, K2],
        [0.0, K2, K3, 0.0, -K2, K3 / 2],
        [-K, 0.0, 0.0, K, 0.0, 0.0],
        [0.0, -K1, -K2, 0.0, K1, -K2],
        [0.0, K2, K3 / 2, 0.0, -K2, K3],
    ])


def liberados(art_i: bool, art_j: bool) -> list:
    """Índices locales de los GDL liberados (giros articulados)."""
    return ([2] if art_i else []) + ([5] if art_j else [])


def condensar(k: np.ndarray, f0: np.ndarray | None, rel: list):
    """Condensación estática de los GDL 'rel' (giros de extremos articulados).

    kc  = k_AA − k_AB · k_BB⁻¹ · k_BA           (con ceros en las filas/columnas liberadas)
    f0c = f0_A − k_AB · k_BB⁻¹ · f0_B
    Devuelve (kc, f0c).  Si no hay GDL liberados devuelve (k, f0)."""
    if not rel:
        return k, f0
    B = list(rel)
    A = [d for d in range(6) if d not in B]
    kBB_inv = np.linalg.inv(k[np.ix_(B, B)])
    kc = np.zeros((6, 6))
    kc[np.ix_(A, A)] = k[np.ix_(A, A)] - k[np.ix_(A, B)] @ kBB_inv @ k[np.ix_(B, A)]
    f0c = None
    if f0 is not None:
        f0c = np.zeros(6)
        f0c[A] = f0[A] - k[np.ix_(A, B)] @ kBB_inv @ f0[B]
    return kc, f0c


def recuperar_liberados(k: np.ndarray, f0: np.ndarray, u: np.ndarray, rel: list) -> np.ndarray:
    """Completa los desplazamientos locales u (6,) con los giros liberados:
    u_B = −k_BB⁻¹ · (k_BA · u_A + f0_B).   (u en las posiciones B se ignora al entrar)."""
    if not rel:
        return u
    B = list(rel)
    A = [d for d in range(6) if d not in B]
    u = np.array(u, dtype=float, copy=True)
    u[B] = -np.linalg.solve(k[np.ix_(B, B)], k[np.ix_(B, A)] @ u[A] + f0[B])
    return u


def rigidez_global_catedra(E, A, I, L, g1, g2) -> np.ndarray:
    """Matriz 'barra general' de la tabla de cátedra, escrita término a término
    (sirve para verificar que coincide con T·k_loc·Tᵀ)."""
    K, K1, K2, K3 = constantes(E, A, I, L)
    a = g1**2 * K + g2**2 * K1
    b = g1 * g2 * (K - K1)
    c = g2 * K2
    d = g2**2 * K + g1**2 * K1
    e = g1 * K2
    return np.array([
        [a, b, -c, -a, -b, -c],
        [b, d, e, -b, -d, e],
        [-c, e, K3, c, -e, K3 / 2],
        [-a, -b, c, a, b, c],
        [-b, -d, -e, b, d, -e],
        [-c, e, K3 / 2, c, -e, K3],
    ])
