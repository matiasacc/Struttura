"""Ensamblaje, solución, reacciones y esfuerzos de extremo de barra del pórtico espacial."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .barra import condensar, recuperar_liberados
from .cargas_barra import equivalente_local
from .entrada import Modelo

TOL_MECANISMO = 1e-12
MAX_GDL_AUTOVALORES = 3000


class ErrorEstructura(Exception):
    """La estructura no se puede resolver (inestable, mal condicionada, etc.)."""


@dataclass
class Resultado:
    nombre: str
    u: np.ndarray            # (n,6) desplazamientos GLOBALES [ux, uy, uz, φx, φy, φz]
    R: np.ndarray            # (n,6) reacciones GLOBALES (fuerza/momento del apoyo sobre la estructura)
    F: np.ndarray            # (n,6) cargas nodales aplicadas GLOBALES
    Rk: np.ndarray           # (n,6) fuerzas de los RESORTES sobre la estructura, GLOBALES
    ub: np.ndarray           # (nb,12) desplazamientos de extremo de barra, ejes LOCALES
    fb: np.ndarray           # (nb,12) fuerzas de extremo (nodo sobre barra), ejes LOCALES
    combo: list | None = None
    Feq: np.ndarray | None = None      # (n,6) cargas nodales equivalentes de las cargas en tramos, GLOBALES
    f0: np.ndarray | None = None       # (nb,12) fuerzas de empotramiento perfecto (nodo sobre barra), LOCALES
    cb: list = field(default_factory=list)      # [(idx_barra, carga_local, factor)]

    @property
    def Ftot(self) -> np.ndarray:
        return self.F if self.Feq is None else self.F + self.Feq

    def cargas_de(self, k: int) -> list:
        return [(c, f) for kb, c, f in self.cb if kb == k]


@dataclass
class Info:
    K: np.ndarray
    libres: np.ndarray
    lam_min: float | None
    residuos: dict = field(default_factory=dict)


def _dofs(b):
    return np.r_[6 * b.i:6 * b.i + 6, 6 * b.j:6 * b.j + 6]


def ensamblar_barras(modelo: Modelo) -> np.ndarray:
    K = np.zeros((6 * modelo.n, 6 * modelo.n))
    for b in modelo.barras:
        d = _dofs(b)
        K[np.ix_(d, d)] += b.k_global
    return K


def matriz_resortes(modelo: Modelo) -> np.ndarray:
    Ks = np.zeros((6 * modelo.n, 6 * modelo.n))
    Ks[np.diag_indices_from(Ks)] += modelo.resortes.reshape(-1)
    return Ks


def nombre_gdl(modelo, k):
    from .entrada import NOMBRES_GDL
    return f"nodo {modelo.nodos[k // 6].id} ({NOMBRES_GDL[k % 6]})"


def rotaciones_indeterminadas(modelo: Modelo, K: np.ndarray):
    """Giros de nudo que ninguna barra ni resorte resiste (p. ej. nudo con todas sus barras articuladas).

    Esos giros no entran en el equilibrio (filas y columnas nulas de K) y son indeterminados: no afectan a ningún resultado.
    Se estabilizan con un resorte ficticio Kaux = ε·q·qᵀ SOLO en la dirección nula q; como K·q = 0, la solución del resto
    no cambia (el valor de ese giro sale 0).  Devuelve (Kaux (6n×6n), lista [(nudo, q (3,))])."""
    n = modelo.n
    Kaux = np.zeros_like(K)
    lista = []
    tol = 1e-10 * np.abs(K).max()
    rot = np.array([K[6 * k + c, 6 * k + c] for k in range(n) for c in (3, 4, 5)])
    eps = float(np.median(rot[rot > tol])) if (rot > tol).any() else 1.0
    for k in range(n):
        cols = [c for c in (3, 4, 5) if not modelo.restr[k, c]]
        if not cols:
            continue
        M = K[:, [6 * k + c for c in cols]]
        _, sv, Vt = np.linalg.svd(M, full_matrices=False)
        for v in Vt[sv < tol]:
            q = np.zeros(3)
            q[[c - 3 for c in cols]] = v
            sl = slice(6 * k + 3, 6 * k + 6)
            Kaux[sl, sl] += eps * np.outer(q, q)
            lista.append((k, q))
    return Kaux, lista


def _aviso_rotaciones(modelo, lista):
    nodos = sorted({modelo.nodos[k].id for k, _ in lista})
    msg = (f"Nudo(s) {', '.join(nodos)}: todas las barras que llegan están articuladas en giro, así que el giro del nudo "
           "es indeterminado (no afecta a los resultados).  Se lo estabiliza automáticamente.")
    if msg not in modelo.avisos:
        modelo.avisos.append(msg)


def _nombre_modo(modelo, u, dg):
    u = u / dg
    u = u / np.abs(u).max()
    sel = [k for k in np.argsort(-np.abs(u)) if abs(u[k]) > 0.3][:8]
    return ", ".join(sorted({nombre_gdl(modelo, int(k)) for k in sel}))


def _verificar_estabilidad(modelo, K, libres):
    idx = np.flatnonzero(libres)
    if idx.size == 0:
        return None
    Kff = K[np.ix_(idx, idx)]
    dg = np.diag(Kff)
    sin_rigidez = idx[dg <= 1e-12 * dg.max()]
    if sin_rigidez.size:
        lista = ", ".join(nombre_gdl(modelo, int(k)) for k in sin_rigidez[:10])
        raise ErrorEstructura(f"Hay GDL libres sin rigidez alguna: {lista}. "
                              "Revisá que todos los nodos libres estén conectados a barras.")
    if idx.size > MAX_GDL_AUTOVALORES:
        return None
    d = np.sqrt(dg)
    w, v = np.linalg.eigh(Kff / np.outer(d, d))
    nmec = int(np.sum(w < TOL_MECANISMO))
    if nmec:
        modos = [f"  Modo {k + 1}: se mueve libremente {_nombre_modo(modelo, v[:, k], d)}"
                 for k in range(min(nmec, 4))]
        raise ErrorEstructura(
            f"La estructura es inestable (hipostática): {nmec} modo(s) de mecanismo.\n" + "\n".join(modos)
            + "\nRevisá los apoyos y las conexiones: una estructura espacial necesita al menos 6 restricciones "
              "bien distribuidas (que impidan las 3 traslaciones y las 3 rotaciones del cuerpo rígido).")
    return float(w[0])


def verificar(modelo: Modelo):
    K = ensamblar_barras(modelo) + matriz_resortes(modelo)
    Kaux, lista = rotaciones_indeterminadas(modelo, K)
    if lista:
        _aviso_rotaciones(modelo, lista)
    return _verificar_estabilidad(modelo, K + Kaux, ~modelo.restr.reshape(-1))


def cargas_equivalentes(modelo: Modelo, cb: list):
    """Cargas nodales equivalentes GLOBALES (n,6) y fuerzas de empotramiento perfecto LOCALES (nb,12).
    Las fuerzas f0 devueltas son las de la barra con nudos rígidos; las cargas nodales equivalentes usan f0 condensado
    (si la barra tiene articulaciones)."""
    f0 = np.zeros((len(modelo.barras), 12))
    for k, c, fac in cb:
        f0[k] += -fac * equivalente_local(c, modelo.barras[k].L)
    Feq = np.zeros(6 * modelo.n)
    for k, b in enumerate(modelo.barras):
        if not f0[k].any():
            continue
        f0c = condensar(b.k_local, f0[k], b.rel)[1]
        T = np.zeros((12, 12))
        for q in range(4):
            T[3 * q:3 * q + 3, 3 * q:3 * q + 3] = b.R
        Feq[_dofs(b)] += T.T @ (-f0c)
    return Feq.reshape(-1, 6), f0


def _armar(modelo, nombre, u, R, Fv, Feq, f0, cb, Rk) -> Resultado:
    nb = len(modelo.barras)
    ub, fb = np.zeros((nb, 12)), np.zeros((nb, 12))
    for k, b in enumerate(modelo.barras):
        T = np.zeros((12, 12))
        for q in range(4):
            T[3 * q:3 * q + 3, 3 * q:3 * q + 3] = b.R
        ub[k] = recuperar_liberados(b.k_local, f0[k], T @ u[_dofs(b)], b.rel)     # incluye giros liberados
        fb[k] = b.k_local @ ub[k] + f0[k]
    return Resultado(nombre, u.reshape(-1, 6), R.reshape(-1, 6), Fv.reshape(-1, 6), Rk.reshape(-1, 6),
                     ub, fb, Feq=Feq, f0=f0, cb=list(cb))


def resolver(modelo: Modelo):
    """Resuelve todos los casos.  Devuelve (dict nombre->Resultado, Info)."""
    n = modelo.n
    Kb = ensamblar_barras(modelo)
    Ks = matriz_resortes(modelo)
    K = Kb + Ks
    Kaux, indet = rotaciones_indeterminadas(modelo, K)
    if indet:
        _aviso_rotaciones(modelo, indet)
    fij = modelo.restr.reshape(-1)
    libres = ~fij
    lam_min = _verificar_estabilidad(modelo, K + Kaux, libres)
    f, r = np.flatnonzero(libres), np.flatnonzero(fij)
    Kt = K + Kaux
    Kff, Kfr = Kt[np.ix_(f, f)], Kt[np.ix_(f, r)]
    info = Info(K, libres, lam_min)
    resultados = {}
    for nombre, F in modelo.casos.items():
        Fv = F.reshape(-1)
        cb = [(k, c, 1.0) for k, lista in modelo.cargas_barra.get(nombre, {}).items() for c in lista]
        Feq, f0 = cargas_equivalentes(modelo, cb)
        Ft = Fv + Feq.reshape(-1)
        for k, q in indet:
            mom = Ft[6 * k + 3:6 * k + 6] @ q
            if abs(mom) > 1e-9 * max(np.abs(Ft).max(), 1e-300):
                raise ErrorEstructura(f"Caso '{nombre}': al nudo {modelo.nodos[k].id} se le aplica un momento, pero todas las barras "
                                      "que llegan están articuladas en esa dirección: no hay con qué equilibrarlo.")
        ur = modelo.prefij[nombre].reshape(-1)[r]
        rhs = Ft[f] - Kfr @ ur
        try:
            uf = np.linalg.solve(Kff, rhs) if f.size else np.zeros(0)
        except np.linalg.LinAlgError:
            raise ErrorEstructura("La matriz reducida es singular: estructura inestable.")
        u = np.zeros(6 * n)
        u[f], u[r] = uf, ur
        Rk = -(Ks @ u)
        R = np.zeros(6 * n)
        R[r] = (Kb @ u)[r] - Ft[r] - Rk[r]
        nr = np.linalg.norm(rhs)
        info.residuos[nombre] = (np.linalg.norm(Kff @ uf - rhs) / nr) if nr > 0 else 0.0
        resultados[nombre] = _armar(modelo, nombre, u, R, Fv, Feq, f0, cb, Rk)
    for nombre, lista in modelo.combinaciones.items():
        resultados[nombre] = combinar(nombre, lista, resultados)
        info.residuos[nombre] = max(info.residuos[c] for c, _ in lista)
    return resultados, info


def combinar(nombre, lista, resultados) -> Resultado:
    base = resultados[lista[0][0]]
    z = np.zeros_like
    u, R, F, Rk, ub, fb = z(base.u), z(base.R), z(base.F), z(base.Rk), z(base.ub), z(base.fb)
    Feq, f0, cb = z(base.F), z(base.fb), []
    for caso, fac in lista:
        r = resultados[caso]
        u += fac * r.u
        R += fac * r.R
        F += fac * r.F
        Rk += fac * r.Rk
        ub += fac * r.ub
        fb += fac * r.fb
        Feq += fac * r.Feq
        f0 += fac * r.f0
        cb += [(k, c, f * fac) for k, c, f in r.cb]
    return Resultado(nombre, u, R, F, Rk, ub, fb, combo=list(lista), Feq=Feq, f0=f0, cb=cb)


def equilibrio(modelo: Modelo, res: Resultado) -> dict:
    """Equilibrio global (fuerzas y momentos respecto del origen): cargas + reacciones (apoyos y resortes) = 0."""
    P = np.array([nd.p for nd in modelo.nodos])
    A = res.Ftot
    B = res.R + res.Rk
    def suma(V):
        return V[:, :3].sum(axis=0), (V[:, 3:] + np.cross(P, V[:, :3])).sum(axis=0)
    fa, ma = suma(A)
    fb, mb = suma(B)
    esc_f = np.abs(A[:, :3]).sum() + np.abs(B[:, :3]).sum()
    esc_m = (np.abs(A[:, 3:]) + np.abs(np.cross(P, A[:, :3]))).sum() + (np.abs(B[:, 3:]) + np.abs(np.cross(P, B[:, :3]))).sum()
    rf, rm = np.abs(fa + fb).max(), np.abs(ma + mb).max()
    rel = max(rf / esc_f if esc_f > 0 else 0.0, rm / esc_m if esc_m > 0 else 0.0)
    return {"F_cargas": fa, "F_reacc": fb, "M_cargas": ma, "M_reacc": mb,
            "res_F": fa + fb, "res_M": ma + mb, "rel": rel}
