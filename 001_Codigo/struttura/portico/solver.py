"""Ensamblaje, solución, reacciones y esfuerzos de extremo de barra del pórtico plano."""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field

import numpy as np

from .barra import condensar, matriz_rotacion, recuperar_liberados
from .cargas_barra import f0_local, feq_local
from .entrada import Modelo

TOL_MECANISMO = 1e-12      # autovalor mínimo (matriz normalizada) por debajo del cual hay mecanismo
MAX_GDL_AUTOVALORES = 3000


class ErrorEstructura(Exception):
    """La estructura no se puede resolver (inestable, mal condicionada, etc.)."""


@dataclass
class Resultado:
    nombre: str
    u: np.ndarray            # (n,3) desplazamientos nodales GLOBALES [ux, uy, φ]
    R: np.ndarray            # (n,3) reacciones GLOBALES (fuerza del apoyo sobre la estructura)
    F: np.ndarray            # (n,3) cargas nodales aplicadas GLOBALES
    Rk: np.ndarray           # (n,3) fuerzas de los RESORTES sobre la estructura, GLOBALES
    ub: np.ndarray           # (nb,6) desplazamientos de extremo de barra, ejes LOCALES (incluye giros liberados)
    fb: np.ndarray           # (nb,6) fuerzas de extremo de barra (nodo sobre barra), ejes LOCALES
    combo: list | None = None
    Feq: np.ndarray | None = None      # (n,3) cargas nodales equivalentes de las cargas en tramos, GLOBALES
    f0: np.ndarray | None = None       # (nb,6) fuerzas de empotramiento perfecto (nodo sobre barra), LOCALES
    cb: list = field(default_factory=list)

    @property
    def Ftot(self) -> np.ndarray:
        return self.F if self.Feq is None else self.F + self.Feq

    def cargas_de(self, k: int) -> list:
        return [(c, f) for c, f in self.cb if c.barra == k]


@dataclass
class Info:
    K: np.ndarray
    libres: np.ndarray
    lam_min: float | None
    residuos: dict = field(default_factory=dict)


# --------------------------------------------------------------------------
def matriz_resortes(modelo: Modelo) -> np.ndarray:
    Ks = np.zeros((3 * modelo.n, 3 * modelo.n))
    Ks[np.diag_indices_from(Ks)] += modelo.resortes.reshape(-1)
    for sp in modelo.resortes_incl:
        b = np.radians(sp["beta"])
        a = np.array([np.cos(b), np.sin(b)])
        d = [3 * sp["nodo"], 3 * sp["nodo"] + 1]
        Ks[np.ix_(d, d)] += sp["k"] * np.outer(a, a)
    return Ks


def carga_desajuste(modelo: Modelo, nombre: str) -> np.ndarray:
    """Carga equivalente (3n,) del desajuste de los resortes: k·e (rectos) + k·e_incl·a (inclinados)."""
    v = modelo.resortes.reshape(-1) * modelo.desaj[nombre].reshape(-1)
    for sp in modelo.resortes_incl:
        e = modelo.desaj_incl.get(nombre, {}).get(sp["nodo"], 0.0)
        if e:
            b = np.radians(sp["beta"])
            v[3 * sp["nodo"]] += sp["k"] * e * np.cos(b)
            v[3 * sp["nodo"] + 1] += sp["k"] * e * np.sin(b)
    return v


def _dofs(b):
    return np.r_[3 * b.i:3 * b.i + 3, 3 * b.j:3 * b.j + 3]


def rigidez_barra_global(b) -> np.ndarray:
    T = matriz_rotacion(b.g1, b.g2)
    return T @ b.k_cond @ T.T


def ensamblar_barras(modelo: Modelo) -> np.ndarray:
    K = np.zeros((3 * modelo.n, 3 * modelo.n))
    for b in modelo.barras:
        K[np.ix_(_dofs(b), _dofs(b))] += rigidez_barra_global(b)
    return K


def ensamblar(modelo: Modelo) -> np.ndarray:
    return ensamblar_barras(modelo) + matriz_resortes(modelo)


def fijos(modelo: Modelo) -> np.ndarray:
    """(3n,) bool: GDL con valor conocido (apoyos + giros sin rigidez fijados por el programa)."""
    return (modelo.restr | modelo.aut).reshape(-1)


def _nombre_modo(modelo, u, dg):
    u = u / dg
    u = u / np.abs(u).max()
    sel = [k for k in np.argsort(-np.abs(u)) if abs(u[k]) > 0.3][:8]
    return ", ".join(sorted({modelo.nombre_gdl(int(k)) for k in sel}))


def _verificar_estabilidad(modelo, K, libres):
    idx = np.flatnonzero(libres)
    if idx.size == 0:
        return None
    Kff = K[np.ix_(idx, idx)]
    dg = np.diag(Kff)
    sin_rigidez = idx[dg <= 1e-12 * dg.max()]
    if sin_rigidez.size:
        lista = ", ".join(modelo.nombre_gdl(int(k)) for k in sin_rigidez[:10])
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
            + "\nRevisá los apoyos, las articulaciones y las conexiones (una cadena de barras con demasiadas "
              "rótulas o apoyos insuficientes forma un mecanismo).")
    return float(w[0])


def verificar(modelo: Modelo):
    return _verificar_estabilidad(modelo, ensamblar(modelo), ~fijos(modelo))


def resolver(modelo: Modelo):
    """Resuelve todos los casos.  Devuelve (dict nombre->Resultado, Info)."""
    n = modelo.n
    Kb = ensamblar_barras(modelo)
    Ks = matriz_resortes(modelo)
    K = Kb + Ks
    fij = fijos(modelo)
    libres = ~fij
    lam_min = _verificar_estabilidad(modelo, K, libres)
    f, r = np.flatnonzero(libres), np.flatnonzero(fij)
    Kff, Kfr = K[np.ix_(f, f)], K[np.ix_(f, r)]
    info = Info(K, libres, lam_min)

    resultados = {}
    for nombre, F in modelo.casos.items():
        Fv = F.reshape(-1)
        cb = [(c, 1.0) for c in modelo.cargas_barra.get(nombre, [])]
        Feq, f0 = cargas_equivalentes(modelo, cb)
        kse = carga_desajuste(modelo, nombre)                       # k·e de los resortes
        Ft = Fv + Feq.reshape(-1)
        ur = modelo.prefij[nombre].reshape(-1)[r]
        rhs = (Ft + kse)[f] - Kfr @ ur
        try:
            uf = np.linalg.solve(Kff, rhs) if f.size else np.zeros(0)
        except np.linalg.LinAlgError:
            raise ErrorEstructura("La matriz reducida es singular: estructura inestable.")
        u = np.zeros(3 * n)
        u[f], u[r] = uf, ur
        Rk = -(Ks @ u) + kse                                        # resortes sobre la estructura
        R = np.zeros(3 * n)
        R[r] = (Kb @ u)[r] - Ft[r] - Rk[r]                           # apoyos: equilibrio del nodo
        R[modelo.aut.reshape(-1)] = 0.0
        nr = np.linalg.norm(rhs)
        info.residuos[nombre] = (np.linalg.norm(Kff @ uf - rhs) / nr) if nr > 0 else 0.0
        resultados[nombre] = _armar_resultado(modelo, nombre, u, R, Fv, Feq, f0, cb, Rk)

    for nombre, lista in modelo.combinaciones.items():
        resultados[nombre] = combinar(nombre, lista, resultados)
        info.residuos[nombre] = max(info.residuos[c] for c, _ in lista)
    return resultados, info


def cargas_equivalentes(modelo: Modelo, cb: list):
    """Cargas nodales equivalentes GLOBALES (n,3) [con condensación de articulaciones] y
    fuerzas de empotramiento perfecto LOCALES (nb,6) [sin condensar, nodo sobre barra]."""
    f0 = np.zeros((len(modelo.barras), 6))
    for c, fac in cb:
        f0[c.barra] += fac * f0_local(c, modelo.barras[c.barra])
    Feq = np.zeros(3 * modelo.n)
    for k, b in enumerate(modelo.barras):
        if not f0[k].any():
            continue
        _, f0c = condensar(b.k_full, f0[k], b.rel)
        Feq[_dofs(b)] += matriz_rotacion(b.g1, b.g2) @ (-f0c)
    return Feq.reshape(-1, 3), f0


def _armar_resultado(modelo, nombre, u, R, Fv, Feq, f0, cb, Rk) -> Resultado:
    nb = len(modelo.barras)
    ub, fb = np.zeros((nb, 6)), np.zeros((nb, 6))
    for k, b in enumerate(modelo.barras):
        ul = matriz_rotacion(b.g1, b.g2).T @ u[_dofs(b)]
        ub[k] = recuperar_liberados(b.k_full, f0[k], ul, b.rel)      # completa los giros articulados
        fb[k] = b.k_full @ ub[k] + f0[k]
    return Resultado(nombre, u.reshape(-1, 3), R.reshape(-1, 3), Fv.reshape(-1, 3), Rk.reshape(-1, 3),
                     ub, fb, Feq=Feq, f0=f0, cb=list(cb or []))


def combinar(nombre, lista, resultados) -> Resultado:
    """Combinación lineal de casos (todo es lineal: se combinan resultados)."""
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
        cb += [(c, f * fac) for c, f in r.cb]
    return Resultado(nombre, u, R, F, Rk, ub, fb, combo=list(lista), Feq=Feq, f0=f0, cb=cb)


def equilibrio(modelo: Modelo, res: Resultado) -> dict:
    """Equilibrio global: cargas (nodales + equivalentes) + reacciones (apoyos y resortes) = 0."""
    x = np.array([nd.x for nd in modelo.nodos])
    y = np.array([nd.y for nd in modelo.nodos])
    RR = res.R + res.Rk
    Fa = res.Ftot
    m = lambda A: A[:, 2] + x * A[:, 1] - y * A[:, 0]                 # momento respecto del origen
    sFx, sFy, sM = (Fa[:, 0] + RR[:, 0]).sum(), (Fa[:, 1] + RR[:, 1]).sum(), (m(Fa) + m(RR)).sum()
    esc_f = np.abs(Fa[:, :2]).sum() + np.abs(RR[:, :2]).sum()
    esc_m = (np.abs(Fa[:, 2]) + np.abs(x * Fa[:, 1]) + np.abs(y * Fa[:, 0])).sum() \
        + (np.abs(RR[:, 2]) + np.abs(x * RR[:, 1]) + np.abs(y * RR[:, 0])).sum()
    rel = lambda v, e: abs(v) / e if e > 0 else 0.0
    return {
        "Fx_cargas": Fa[:, 0].sum(), "Fx_reacc": RR[:, 0].sum(),
        "Fy_cargas": Fa[:, 1].sum(), "Fy_reacc": RR[:, 1].sum(),
        "M_cargas": m(Fa).sum(), "M_reacc": m(RR).sum(),
        "res_Fx": sFx, "res_Fy": sFy, "res_M": sM,
        "rel": max(rel(sFx, esc_f), rel(sFy, esc_f), rel(sM, esc_m)),
    }
