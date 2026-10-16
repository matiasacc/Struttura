"""Elemento de barra espacial (Euler-Bernoulli) de 12 GDL.

Orden de GDL locales (por nodo):  u, v, w, θx, θy, θz   →  [nodo i (6), nodo j (6)]
    x local = eje de la barra (de i a j);  y, z = ejes principales de la sección (terna derecha x × y = z).
    u axial · v en y · w en z · θx torsión · θy giro alrededor de y · θz giro alrededor de z.
    Flexión en el plano x-y:  (v, θz), inercia Iz.     Flexión en el plano x-z:  (w, θy), inercia Iy.
    Con la terna derecha:  θy = -dw/dx   y   θz = +dv/dx.
"""
from __future__ import annotations

import numpy as np


def rigidez_local(E, G, A, Iy, Iz, J, L) -> np.ndarray:
    """Matriz de rigidez local 12×12 (sin deformación por corte)."""
    k = np.zeros((12, 12))
    a = E * A / L
    t = G * J / L
    # axial (u1, u2) -> índices 0, 6
    k[np.ix_([0, 6], [0, 6])] = a * np.array([[1, -1], [-1, 1]])
    # torsión (θx1, θx2) -> 3, 9
    k[np.ix_([3, 9], [3, 9])] = t * np.array([[1, -1], [-1, 1]])
    # flexión en x-y: (v1, θz1, v2, θz2) -> 1, 5, 7, 11
    c = E * Iz / L**3
    kz = c * np.array([[12, 6 * L, -12, 6 * L],
                       [6 * L, 4 * L**2, -6 * L, 2 * L**2],
                       [-12, -6 * L, 12, -6 * L],
                       [6 * L, 2 * L**2, -6 * L, 4 * L**2]])
    k[np.ix_([1, 5, 7, 11], [1, 5, 7, 11])] = kz
    # flexión en x-z: (w1, θy1, w2, θy2) -> 2, 4, 8, 10   (signo cruzado por θy = -dw/dx)
    c = E * Iy / L**3
    ky = c * np.array([[12, -6 * L, -12, -6 * L],
                       [-6 * L, 4 * L**2, 6 * L, 2 * L**2],
                       [-12, 6 * L, 12, 6 * L],
                       [-6 * L, 2 * L**2, 6 * L, 4 * L**2]])
    k[np.ix_([2, 4, 8, 10], [2, 4, 8, 10])] = ky
    return k


def terna_local(pi, pj, ref=None, giro_deg: float = 0.0):
    """Ejes locales de la barra.  Devuelve (R, L) con R (3×3): filas = ex, ey, ez expresados en globales
    (v_local = R · v_global).

    ref: vector (globales) hacia donde apunta el eje z local (se proyecta sobre el plano perpendicular a x).
         Por defecto:  +Z global; si la barra es vertical (paralela a Z),  +X global.
    giro_deg: giro de la sección alrededor del eje x local (positivo por regla de la mano derecha).
    """
    d = np.asarray(pj, float) - np.asarray(pi, float)
    L = float(np.linalg.norm(d))
    ex = d / L
    if ref is None:
        ref = np.array([0.0, 0.0, 1.0])
        if abs(ex @ ref) > 0.999999:
            ref = np.array([1.0, 0.0, 0.0])
    ref = np.asarray(ref, float)
    ez = ref - (ref @ ex) * ex
    nz = np.linalg.norm(ez)
    if nz < 1e-9 * max(1.0, np.linalg.norm(ref)):
        raise ValueError("el vector de referencia es paralelo al eje de la barra")
    ez /= nz
    ey = np.cross(ez, ex)
    if giro_deg:
        g = np.radians(giro_deg)
        ey, ez = np.cos(g) * ey + np.sin(g) * ez, -np.sin(g) * ey + np.cos(g) * ez
    return np.vstack([ex, ey, ez]), L


def matriz_T(R: np.ndarray) -> np.ndarray:
    """Matriz de transformación 12×12 (global → local):  u_local = T · u_global."""
    T = np.zeros((12, 12))
    for b in range(4):
        T[3 * b:3 * b + 3, 3 * b:3 * b + 3] = R
    return T


def rigidez_global(k_local, R):
    T = matriz_T(R)
    return T.T @ k_local @ T


# --------------------------------------------------------------------------
# Articulaciones (liberaciones de extremo)
# --------------------------------------------------------------------------
# Índices locales de los giros de cada extremo:  i → θx=3, θy=4, θz=5   j → θx=9, θy=10, θz=11
_GIROS = {"t": 3, "y": 4, "z": 5}
_ETIQ = {"t": "T", "y": "My", "z": "Mz"}


def parsear_articulacion(texto) -> str:
    """Texto de la columna art_i / art_j → letras ordenadas de los giros liberados ('' = nudo rígido).

        1, si, x, rotula ........ rótula esférica: libera My y Mz (se transmiten N, Vy, Vz y T)
        my, mz, t (o mx) ........ libera solo ese momento;  se pueden combinar con '+':  my+mz,  my+t
    Lanza ValueError si no se entiende."""
    s = (texto or "").strip().lower().replace(" ", "")
    if s in ("", "0", "no", "n", "false", "-"):
        return ""
    if s in ("1", "si", "sí", "s", "x", "true", "yes", "rotula", "rótula", "esferica", "esférica"):
        return "yz"
    letras = set()
    for tok in s.replace(",", "+").split("+"):
        tok = {"my": "y", "mz": "z", "mx": "t", "t": "t", "y": "y", "z": "z"}.get(tok)
        if tok is None:
            raise ValueError(f"'{texto}' no es una articulación válida (usar 1, o my / mz / t combinados con '+')")
        letras.add(tok)
    return "".join(c for c in "tyz" if c in letras)


def descripcion_articulacion(letras: str) -> str:
    return "+".join(_ETIQ[c] for c in letras) if letras else "–"


def gdl_liberados(art_i: str, art_j: str) -> list:
    """Índices locales (0..11) de los GDL liberados."""
    return [_GIROS[c] for c in art_i] + [6 + _GIROS[c] for c in art_j]


def condensar(k: np.ndarray, f0: np.ndarray | None, rel: list):
    """Condensación estática de los GDL liberados 'rel':
        kc  = k_AA − k_AB · k_BB⁻¹ · k_BA          (con ceros en las filas/columnas liberadas)
        f0c = f0_A − k_AB · k_BB⁻¹ · f0_B
    Devuelve (kc, f0c).  Sin liberaciones devuelve (k, f0)."""
    if not rel:
        return k, f0
    B = list(rel)
    A = [d for d in range(12) if d not in B]
    kBB_inv = np.linalg.inv(k[np.ix_(B, B)])
    kc = np.zeros((12, 12))
    kc[np.ix_(A, A)] = k[np.ix_(A, A)] - k[np.ix_(A, B)] @ kBB_inv @ k[np.ix_(B, A)]
    f0c = None
    if f0 is not None:
        f0c = np.zeros(12)
        f0c[A] = f0[A] - k[np.ix_(A, B)] @ kBB_inv @ f0[B]
    return kc, f0c


def recuperar_liberados(k: np.ndarray, f0: np.ndarray, u: np.ndarray, rel: list) -> np.ndarray:
    """Completa los desplazamientos locales u (12,) con los giros liberados:
        u_B = −k_BB⁻¹ · (k_BA · u_A + f0_B)."""
    if not rel:
        return u
    B = list(rel)
    A = [d for d in range(12) if d not in B]
    u = np.array(u, dtype=float, copy=True)
    u[B] = -np.linalg.solve(k[np.ix_(B, B)], k[np.ix_(B, A)] @ u[A] + f0[B])
    return u
