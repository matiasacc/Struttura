"""Ensamblaje, solución, reacciones y esfuerzos de extremo de barra."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .barra import condensar, matriz_rotacion, recuperar_liberados
from .cargas_barra import f0_local, feq_local
from .entrada import Modelo, NOMBRES_GDL

TOL_MECANISMO = 1e-9      # autovalor mínimo (matriz normalizada) por debajo del cual hay mecanismo
MAX_GDL_AUTOVALORES = 3000


class ErrorEstructura(Exception):
    """La estructura no se puede resolver (inestable, mal condicionada, etc.)."""


@dataclass
class Resultado:
    nombre: str
    u: np.ndarray            # (n,3) desplazamientos nodales GLOBALES  [uz, φx, φy]
    R: np.ndarray            # (n,3) reacciones GLOBALES (fuerza del apoyo sobre la estructura)
    F: np.ndarray            # (n,3) cargas nodales aplicadas GLOBALES (solo las cargadas en nodos)
    Rk: np.ndarray           # (n,3) fuerzas de los RESORTES sobre la estructura (= -k·u), GLOBALES
    ub: np.ndarray           # (nb,6) desplazamientos de extremo de barra, ejes LOCALES
    fb: np.ndarray           # (nb,6) fuerzas de extremo de barra (nodo sobre barra), ejes LOCALES
    combo: list | None = None
    Feq: np.ndarray | None = None      # (n,3) cargas nodales equivalentes de las cargas en tramos, GLOBALES
    f0: np.ndarray | None = None       # (nb,6) fuerzas de empotramiento perfecto (nodo sobre barra), LOCALES
    cb: list = field(default_factory=list)   # [(CargaBarra, factor), ...] cargas en tramos que actúan

    @property
    def Ftot(self) -> np.ndarray:
        """Cargas nodales totales: aplicadas + equivalentes de las cargas en tramos."""
        return self.F if self.Feq is None else self.F + self.Feq

    def cargas_de(self, k: int) -> list:
        """Cargas en el tramo de la barra k (índice): lista de (CargaBarra, factor)."""
        return [(c, f) for c, f in self.cb if c.barra == k]


@dataclass
class Info:
    K: np.ndarray
    libres: np.ndarray       # (3n,) bool
    lam_min: float | None
    residuos: dict = field(default_factory=dict)


# --------------------------------------------------------------------------
def matriz_resortes(modelo: Modelo) -> np.ndarray:
    """Rigidez de los resortes (3n x 3n): rectos en la diagonal + resortes de giro con eje inclinado."""
    Ks = np.zeros((3 * modelo.n, 3 * modelo.n))
    Ks[np.diag_indices_from(Ks)] += modelo.resortes.reshape(-1)
    for sp in modelo.resortes_giro:
        b = np.radians(sp["beta"])
        a = np.array([np.cos(b), np.sin(b)])
        d = [3 * sp["nodo"] + 1, 3 * sp["nodo"] + 2]
        Ks[np.ix_(d, d)] += sp["k"] * np.outer(a, a)
    return Ks


def ensamblar(modelo: Modelo) -> np.ndarray:
    """Matriz de rigidez global K (3n x 3n), ejes globales: barras + resortes en los nodos."""
    K = np.zeros((3 * modelo.n, 3 * modelo.n))
    for b in modelo.barras:
        T = matriz_rotacion(b.g1, b.g2)
        kg = T @ b.k_cond @ T.T                                      # con articulaciones condensadas
        d = np.r_[3 * b.i:3 * b.i + 3, 3 * b.j:3 * b.j + 3]
        K[np.ix_(d, d)] += kg
    K += matriz_resortes(modelo)                                     # resortes (rectos e inclinados)
    for d, v, eps in modelo.estab:                                   # giros sin rigidez (barras articuladas)
        K[np.ix_(d, d)] += eps * np.outer(v, v)
    return K


def _nombre_modo(modelo, u, dg):
    """Describe un modo de mecanismo: qué GDL se mueven libremente."""
    u = u / dg
    u = u / np.abs(u).max()
    sel = np.argsort(-np.abs(u))
    sel = [k for k in sel if abs(u[k]) > 0.3][:8]
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
        raise ErrorEstructura(
            f"Hay GDL libres sin rigidez alguna: {lista}. "
            "Revisá que todos los nodos libres estén conectados a barras.")
    if idx.size > MAX_GDL_AUTOVALORES:
        return None
    d = np.sqrt(dg)
    Kn = Kff / np.outer(d, d)                 # normalizada: autovalores adimensionales
    w, v = np.linalg.eigh(Kn)
    nmec = int(np.sum(w < TOL_MECANISMO))
    if nmec:
        modos = [f"  Modo {k + 1}: se mueve libremente {_nombre_modo(modelo, v[:, k], d)}"
                 for k in range(min(nmec, 4))]
        raise ErrorEstructura(
            f"La estructura es inestable (hipostática): {nmec} modo(s) de mecanismo.\n"
            + "\n".join(modos)
            + "\nRevisá los apoyos y las conexiones.  En un emparrillado no alcanza con impedir uz: "
              "también hay que impedir el giro alrededor del eje de cada tramo recto "
              "(torsión) con algún apoyo o barra transversal.")
    return float(w[0])


def verificar(modelo: Modelo):
    """Solo chequea la estabilidad (sin resolver).  Devuelve el menor autovalor normalizado
    o levanta ErrorEstructura si hay un mecanismo."""
    return _verificar_estabilidad(modelo, ensamblar(modelo), ~modelo.restr.reshape(-1))


def resolver(modelo: Modelo):
    """Resuelve todos los casos de carga.  Devuelve (dict nombre->Resultado, Info)."""
    n = modelo.n
    K = ensamblar(modelo)
    restr = modelo.restr.reshape(-1)
    libres = ~restr
    lam_min = _verificar_estabilidad(modelo, K, libres)
    f = np.flatnonzero(libres)
    r = np.flatnonzero(restr)
    Kff = K[np.ix_(f, f)]
    Kfr = K[np.ix_(f, r)]
    info = Info(K, libres, lam_min)
    Ks = matriz_resortes(modelo)
    kd = modelo.resortes.reshape(-1)

    resultados = {}
    for nombre, F in modelo.casos.items():
        Fv = F.reshape(-1)
        cb = [(c, 1.0) for c in modelo.cargas_barra.get(nombre, [])]
        Feq, f0 = cargas_equivalentes(modelo, cb)
        e = modelo.desaj[nombre].reshape(-1)                       # desajuste (apoyo corrido) de los resortes
        Ft = Fv + Feq.reshape(-1) + kd * e                         # cargas nodales + equivalentes + k·e
        for d, v, eps in modelo.estab:
            if abs(Ft[d] @ v) > 1e-9 * max(np.abs(Ft).max(), 1e-300):
                raise ErrorEstructura(f"Caso {nombre}: hay una carga en un giro sin rigidez ({modelo.nombre_gdl(int(d[0]))}): "
                                      "las articulaciones forman un mecanismo en ese nodo.")
        ur = modelo.prefij[nombre].reshape(-1)[r]
        rhs = Ft[f] - Kfr @ ur
        try:
            uf = np.linalg.solve(Kff, rhs) if f.size else np.zeros(0)
        except np.linalg.LinAlgError:
            raise ErrorEstructura("La matriz reducida es singular: estructura inestable.")
        u = np.zeros(3 * n)
        u[f] = uf
        u[r] = ur
        R = np.zeros(3 * n)
        R[r] = K[r, :] @ u - Ft[r]                       # reacción de los apoyos (K incluye resortes)
        nr = np.linalg.norm(rhs)
        info.residuos[nombre] = (np.linalg.norm(Kff @ uf - rhs) / nr) if nr > 0 else 0.0
        resultados[nombre] = _armar_resultado(modelo, nombre, u, R, Fv, Feq, f0, cb, Ks, e)

    for nombre, lista in modelo.combinaciones.items():
        resultados[nombre] = combinar(nombre, lista, resultados)
        info.residuos[nombre] = max(info.residuos[c] for c, _ in lista)
    return resultados, info


def cargas_equivalentes(modelo: Modelo, cb: list):
    """Cargas nodales equivalentes GLOBALES (n,3) y fuerzas de empotramiento LOCALES (nb,6)
    de una lista [(CargaBarra, factor), ...]."""
    Feq = np.zeros(3 * modelo.n)
    f0 = np.zeros((len(modelo.barras), 6))
    for c, fac in cb:
        f0[c.barra] += fac * f0_local(c, modelo.barras[c.barra])
    for k, b in enumerate(modelo.barras):
        if not f0[k].any():
            continue
        _, f0c = condensar(b.k_full, f0[k], b.rel)                  # con articulaciones
        d = np.r_[3 * b.i:3 * b.i + 3, 3 * b.j:3 * b.j + 3]
        Feq[d] += matriz_rotacion(b.g1, b.g2) @ (-f0c)              # local -> global
    return Feq.reshape(-1, 3), f0


def _armar_resultado(modelo, nombre, u, R, Fv, Feq=None, f0=None, cb=None, Ks=None, e=None) -> Resultado:
    nb = len(modelo.barras)
    ub = np.zeros((nb, 6))
    fb = np.zeros((nb, 6))
    for k, b in enumerate(modelo.barras):
        d = np.r_[3 * b.i:3 * b.i + 3, 3 * b.j:3 * b.j + 3]
        T = matriz_rotacion(b.g1, b.g2)
        ub[k] = T.T @ u[d]                                          # global -> local
        if f0 is not None:
            ub[k] = recuperar_liberados(b.k_full, f0[k], ub[k], b.rel)   # completa los giros articulados
            fb[k] = b.k_full @ ub[k] + f0[k]                        # + empotramiento perfecto
        else:
            fb[k] = b.k_full @ ub[k]
    Ks = matriz_resortes(modelo) if Ks is None else Ks
    Rk = -(Ks @ u)                                       # fuerza de los resortes sobre la estructura
    if e is not None:
        Rk = Rk + modelo.resortes.reshape(-1) * e        # apoyo corrido: -k·(u - e)
    if Feq is None:
        Feq = np.zeros((modelo.n, 3))
    if f0 is None:
        f0 = np.zeros((len(modelo.barras), 6))
    return Resultado(nombre, u.reshape(-1, 3), R.reshape(-1, 3), Fv.reshape(-1, 3),
                     Rk.reshape(-1, 3), ub, fb, Feq=Feq, f0=f0, cb=list(cb or []))


def combinar(nombre, lista, resultados) -> Resultado:
    """Combinación lineal de casos (todo es lineal: se combinan resultados)."""
    base = resultados[lista[0][0]]
    z = lambda a: np.zeros_like(a)
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
    """Chequeo de equilibrio global: cargas + reacciones (apoyos y resortes) deben sumar cero."""
    x = np.array([nd.x for nd in modelo.nodos])
    y = np.array([nd.y for nd in modelo.nodos])
    RR = res.R + res.Rk                                  # todo lo que aportan apoyos y resortes
    res = _con_cargas_totales(res)
    T = res.F + RR
    sFz = T[:, 0].sum()
    sMx = (T[:, 1] + y * T[:, 0]).sum()
    sMy = (T[:, 2] - x * T[:, 0]).sum()
    esc_f = np.abs(res.F[:, 0]).sum() + np.abs(RR[:, 0]).sum()
    esc_mx = np.abs(res.F[:, 1]).sum() + np.abs(RR[:, 1]).sum() + np.abs(y * res.F[:, 0]).sum() \
        + np.abs(y * RR[:, 0]).sum()
    esc_my = np.abs(res.F[:, 2]).sum() + np.abs(RR[:, 2]).sum() + np.abs(x * res.F[:, 0]).sum() \
        + np.abs(x * RR[:, 0]).sum()
    rel = lambda v, e: abs(v) / e if e > 0 else 0.0
    return {
        "Fz_cargas": res.F[:, 0].sum(), "Fz_reacc": RR[:, 0].sum(),
        "Mx_cargas": (res.F[:, 1] + y * res.F[:, 0]).sum(),
        "Mx_reacc": (RR[:, 1] + y * RR[:, 0]).sum(),
        "My_cargas": (res.F[:, 2] - x * res.F[:, 0]).sum(),
        "My_reacc": (RR[:, 2] - x * RR[:, 0]).sum(),
        "res_Fz": sFz, "res_Mx": sMx, "res_My": sMy,
        "rel": max(rel(sFz, esc_f), rel(sMx, esc_mx), rel(sMy, esc_my)),
    }


def _con_cargas_totales(res: Resultado) -> Resultado:
    """Copia de res donde F = cargas nodales + equivalentes (para chequear el equilibrio global)."""
    import dataclasses
    return dataclasses.replace(res, F=res.Ftot, Feq=None)
