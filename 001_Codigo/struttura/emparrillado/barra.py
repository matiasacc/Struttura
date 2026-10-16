"""Matrices de la barra de emparrillado plano.

GDL por nodo (en este orden):  uz, φx, φy
    - En ejes GLOBALES: φx y φy son giros (vectores, regla de la mano derecha)
      alrededor de X e Y globales.
    - En ejes LOCALES:  φx = giro alrededor del eje de la barra (torsión),
      φy = giro de flexión.  El eje local xl va de i a j, yl está a 90°
      antihorario de xl y z es común (fuera del plano).

Rotación (tabla de cátedra):   v_glo = R · v_loc
        R = [[1,  0,   0 ],
             [0, γ1, -γ2 ],
             [0, γ2,  γ1 ]]          γ1 = cos(ángulo) = Δx/L,  γ2 = sen(ángulo) = Δy/L

Nomenclatura: sufijo _loc = ejes locales de la barra, _glo = ejes globales.
"""
from __future__ import annotations

import numpy as np


def matriz_rotacion(g1: float, g2: float) -> np.ndarray:
    """T (6x6) tal que  u_glo = T @ u_loc  para los 6 GDL de la barra (i y j)."""
    R = np.array([[1.0, 0.0, 0.0],
                  [0.0, g1, -g2],
                  [0.0, g2, g1]])
    T = np.zeros((6, 6))
    T[:3, :3] = R
    T[3:, 3:] = R
    return T


def constantes(E: float, G: float, I: float, J: float, L: float):
    """K, K1, K2, K3 según la tabla."""
    K = G * J / L
    K1 = 12 * E * I / L**3
    K2 = 6 * E * I / L**2
    K3 = 4 * E * I / L
    return K, K1, K2, K3


def rigidez_local(E: float, G: float, I: float, J: float, L: float) -> np.ndarray:
    """k_loc (6x6): barra sobre el eje xl (equivale a la 'barra según eje X_G' de la tabla)."""
    K, K1, K2, K3 = constantes(E, G, I, J, L)
    return np.array([
        [ K1, 0.0, -K2, -K1, 0.0, -K2],
        [0.0,   K, 0.0, 0.0,  -K, 0.0],
        [-K2, 0.0,  K3,  K2, 0.0, K3 / 2],
        [-K1, 0.0,  K2,  K1, 0.0,  K2],
        [0.0,  -K, 0.0, 0.0,   K, 0.0],
        [-K2, 0.0, K3 / 2, K2, 0.0, K3],
    ])


def rigidez_global(E, G, I, J, L, g1, g2) -> np.ndarray:
    """k_glo = T · k_loc · Tᵀ  (equivale a la 'barra general' de la tabla)."""
    T = matriz_rotacion(g1, g2)
    return T @ rigidez_local(E, G, I, J, L) @ T.T


# --------------------------------------------------------------------------
# Articulaciones por barra (misma idea que el pórtico plano)
# --------------------------------------------------------------------------
def parsear_articulacion(texto) -> str:
    """Convierte el texto de la columna art_i / art_j en letras: 'm' (flexión) y/o 't' (torsión).
    ''/0/no -> ''   1/si/m/my -> 'm'   t/mx -> 't'   mt, m+t, 'm t' -> 'mt'.  Devuelve None si no es válido."""
    t = (texto or "").strip().lower().replace(" ", "")
    if t in ("", "0", "no", "n", "false", "-"):
        return ""
    if t in ("1", "si", "sí", "s", "x", "true", "yes"):
        return "m"
    letras = set()
    for p in t.replace("+", ",").replace(";", ",").split(","):
        if p in ("m", "my", "flexion", "flexión"):
            letras.add("m")
        elif p in ("t", "mx", "torsion", "torsión"):
            letras.add("t")
        elif p in ("mt", "tm"):
            letras |= {"m", "t"}
        else:
            return None
    return "".join(c for c in "mt" if c in letras)


def descripcion_articulacion(art: str) -> str:
    return {"": "—", "m": "flexión", "t": "torsión", "mt": "flexión y torsión"}[art]


def liberados(art_i: str, art_j: str) -> list:
    """Índices locales de los GDL liberados: flexión i->2, j->5; torsión i->1, j->4."""
    r = []
    if "t" in art_i: r.append(1)
    if "m" in art_i: r.append(2)
    if "t" in art_j: r.append(4)
    if "m" in art_j: r.append(5)
    return r


def condensar(k, f0, rel):
    """Condensación estática de los GDL 'rel'.  Devuelve (kc, f0c); sin liberados devuelve (k, f0)."""
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


def recuperar_liberados(k, f0, u, rel):
    """Completa u (6,) local con los giros liberados:  u_B = −k_BB⁻¹ (k_BA u_A + f0_B)."""
    if not rel:
        return u
    B = list(rel)
    A = [d for d in range(6) if d not in B]
    u = np.array(u, dtype=float, copy=True)
    u[B] = -np.linalg.solve(k[np.ix_(B, B)], k[np.ix_(B, A)] @ u[A] + f0[B])
    return u
