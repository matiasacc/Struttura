"""Esfuerzos internos, tensiones y elástica de cada barra del pórtico (ejes LOCALES de la barra).

Convención de signos (xl de i a j, yl a 90° antihorario):
    N(x) = −Px_i − ∫qx            N > 0: tracción
    V(x) =  Py_i + ∫qy            V > 0: sobre la cara +xl actúa una fuerza hacia −yl (corte "horario")
    M(x) = −M_i + x·Py_i + ∫qy·(x−s)ds − ΣM0·H(x−a)      M > 0: tracciona la fibra −yl ("sagging")
donde (Px_i, Py_i, M_i) son las fuerzas de extremo que el nodo i ejerce sobre la barra (ejes locales,
YA incluyen las fuerzas de empotramiento perfecto de las cargas del tramo).
En el extremo j:  N(L) = Px_j,  V(L) = −Py_j,  M(L) = M_j.
"""
from __future__ import annotations

import numpy as np

from ..falla_plana import curva_utilizacion, evaluar_estados, tension_pared
from ..pandeo import verificar as pandeo_verificar

from .cargas_barra import desplazamiento_particular, evaluar, piezas
from .entrada import Modelo
from .solver import Resultado


def estaciones(L: float, cargas, n: int = 161):
    """Abscisas x para dibujar/evaluar diagramas de una barra.  Devuelve (x, s): s = -1/0/+1 es el lado
    desde el que se evalúa en los saltos (fuerza o momento puntual interior: la abscisa se repite)."""
    eps = 1e-9 * L
    saltos = sorted({float(c.a) for c, _ in cargas if c.tipo in ("P", "M") and eps < c.a < L - eps})
    xs = list(np.linspace(0.0, L, n))
    for c, _ in cargas:
        if c.tipo == "q":
            xs += [float(v) for v in (c.a, c.b) if eps < v < L - eps]
    xs = sorted(xs)
    tol = 1e-7 * L
    reg = [xv for k, xv in enumerate(xs) if (k == 0 or xv - xs[k - 1] > tol)
           and not any(abs(xv - sj) < tol for sj in saltos)]
    pts = [(xv, 0) for xv in reg]
    for sj in saltos:
        pts += [(sj, -1), (sj, +1)]
    pts.sort()
    return np.array([p[0] for p in pts]), np.array([p[1] for p in pts])


def piezas_barra(modelo: Modelo, res: Resultado, k: int) -> list:
    b = modelo.barras[k]
    return piezas(b.L, (res.fb[k, 0], res.fb[k, 1], res.fb[k, 2]), res.cargas_de(k))


def curvas_barra(modelo: Modelo, res: Resultado, k: int, n: int = 161) -> dict:
    b = modelo.barras[k]
    x, s = estaciones(b.L, res.cargas_de(k), n)
    N, V, M = evaluar(piezas_barra(modelo, res, k), x, s)
    return {"x": x, "N": N, "V": V, "M": M}


def esfuerzos(modelo: Modelo, res: Resultado, n: int = 161) -> dict:
    """Esfuerzos por barra.  Claves (arreglos por barra):
        N, Nj   axil en i y en j            V, Vj   cortante en i y en j            Mi, Mj  flector en i y en j
        Nmax, Nmin, Mmax, xMmax, Mmin, xMmin, Vabs   extremos a lo largo de la barra
        curvas  lista de dicts {x, N, V, M}"""
    nb = len(modelo.barras)
    e = {k: np.zeros(nb) for k in ("N", "Nj", "V", "Vj", "Mi", "Mj", "Nmax", "Nmin", "Mmax", "xMmax",
                                   "Mmin", "xMmin", "Vabs")}
    e["curvas"] = []
    for k in range(nb):
        cv = curvas_barra(modelo, res, k, n)
        e["curvas"].append(cv)
        e["N"][k], e["Nj"][k] = -res.fb[k, 0], res.fb[k, 3]
        e["V"][k], e["Vj"][k] = res.fb[k, 1], -res.fb[k, 4]
        e["Mi"][k], e["Mj"][k] = -res.fb[k, 2], res.fb[k, 5]
        M, x = cv["M"], cv["x"]
        e["Mmax"][k], e["xMmax"][k] = M.max(), x[M.argmax()]
        e["Mmin"][k], e["xMmin"][k] = M.min(), x[M.argmin()]
        e["Nmax"][k], e["Nmin"][k] = cv["N"].max(), cv["N"].min()
        e["Vabs"][k] = np.abs(cv["V"]).max()
    return e


def funciones_barra(modelo: Modelo, res: Resultado, k: int) -> list:
    """Funciones exactas de N(x), V(x), M(x) de la barra k, por tramos (x desde el nodo i, ejes locales).
    [{"x0", "x1", "N": Polynomial, "V": Polynomial, "M": Polynomial}, ...]"""
    return piezas_barra(modelo, res, k)


def tensiones(modelo: Modelo, esf: dict) -> list:
    """Tensiones por barra (lista de dicts; None si la sección no tiene datos).

    - Fibras extremas:  σ = N/A ± M·c/I   →  σ_tracc = N/A + |M|c/I,  σ_compr = N/A − |M|c/I  (extremos a lo largo de la barra)
    - Corte:            τv = kv·|V|/A en el eje neutro
    - Von Mises evaluada en dos puntos de control de cada sección estudiada:
        (a) fibra extrema:  σeq = |N/A ± M·c/I|                (el corte es nulo ahí)
        (b) eje neutro:     σeq = √((N/A)² + 3·τv²)            (la flexión es nula ahí)
      Se informa el máximo sobre toda la barra.
    CS fluencia = fy/σVM;  CS admisible = σadm/σVM."""
    salida = []
    for k, b in enumerate(modelo.barras):
        s = b.sec
        cv = esf["curvas"][k]
        d = {"sig_t": None, "x_sig_t": None, "sig_c": None, "x_sig_c": None, "tau_v": None,
             "vm": None, "x_vm": None, "n_fy": None, "n_adm": None,
             "Pc": None, "lam": None, "n_pand": None,
             "corte_incluido": s.kv is not None and s.A is not None and modelo.config.get("corte_tensiones", "si") == "si"}
        if not s.A:
            salida.append(d)
            continue
        if getattr(s, "pared", None) is not None:                  # perfil de pared delgada: motor del 3D (Jourawski + centro de corte)
            tp = tension_pared(s, b.mat, cv["N"], cv["V"], cv["M"], None, modelo.config.get("corte_tensiones", "si") == "si")
            d["corte_incluido"] = modelo.config.get("corte_tensiones", "si") == "si"
            sx = tp["sx"]
            i, j = np.unravel_index(sx.argmax(), sx.shape)
            d["sig_t"], d["x_sig_t"] = float(sx[i, j]), float(cv["x"][i])
            i, j = np.unravel_index(sx.argmin(), sx.shape)
            d["sig_c"], d["x_sig_c"] = float(sx[i, j]), float(cv["x"][i])
            d["tau_v"] = float(tp["tau"].max())
            eq = tp["eq"]
            m = int(eq.argmax())
            d["vm"], d["x_vm"], d["punto"], d["teoria"] = float(eq[m]), float(cv["x"][m]), tp["punto"], b.mat.teoria
            d["curva_vm"], d["x_curva"] = curva_utilizacion(b.mat, eq, tp["cs"]), cv["x"]
            if d["vm"] > 0:
                d["n_fy"] = None if tp["cs"] is None else float(tp["cs"].min())
                d["n_adm"] = None if tp["cs_adm"] is None else float(tp["cs_adm"].min())
            d.update(pandeo_verificar(b.mat.E, s.I, s.A, b.L, b.pandeo, float(cv["N"].min())))
            salida.append(d)
            continue
        sN = cv["N"] / s.A
        # sin c e I (barra de reticulado) solo hay tensión axial
        sM = np.abs(cv["M"]) * s.c / s.I if (s.c is not None and s.I) else np.zeros_like(sN)
        st, sc = sN + sM, sN - sM
        m = int(st.argmax())
        d["sig_t"], d["x_sig_t"] = float(st[m]), float(cv["x"][m])
        m = int(sc.argmin())
        d["sig_c"], d["x_sig_c"] = float(sc[m]), float(cv["x"][m])
        tv = s.kv * np.abs(cv["V"]) / s.A if d["corte_incluido"] else np.zeros_like(sN)
        d["tau_v"] = float(tv.max())
        # criterio de falla del material (por defecto Von Mises) en los tres estados de control: fibra traccionada, fibra comprimida y eje neutro
        eq, cs, cs_adm = evaluar_estados(b.mat, [(st, 0 * st), (sc, 0 * sc), (sN, tv)])
        m = int(eq.argmax())
        d["vm"], d["x_vm"] = float(eq[m]), float(cv["x"][m])
        d["curva_vm"], d["x_curva"] = curva_utilizacion(b.mat, eq, cs), cv["x"]     # σeq a lo largo de la barra (visor: modo Utilización)
        d["teoria"] = b.mat.teoria
        if d["vm"] > 0:
            if cs is not None:
                d["n_fy"] = float(cs.min())                        # CS de la teoría del material (Von Mises: fy/σVM)
            if cs_adm is not None:
                d["n_adm"] = float(cs_adm.min())
        d.update(pandeo_verificar(b.mat.E, s.I, s.A, b.L, b.pandeo, float(cv["N"].min())))     # pandeo de Euler (barras comprimidas)
        salida.append(d)
    return salida


def elastica(modelo: Modelo, res: Resultado, n: int = 25):
    """Deformada de cada barra: lista de (X0, Y0, DX, DY) con la posición indeformada y el desplazamiento
    GLOBAL en cada punto.

    Local:  u(x) = interpolación lineal de (u_i, u_j) + u_p(x);   v(x) = Hermite cúbico de (v_i, θ_i, v_j, θ_j) + v_p(x)
    (u_p, v_p: barra biempotrada bajo las cargas del tramo, 0 si no hay).  Luego se rota a ejes globales."""
    curvas = []
    for k, b in enumerate(modelo.barras):
        cargas = res.cargas_de(k)
        xi = np.linspace(0.0, 1.0, max(n, 61) if res.cb else n)
        ui, vi, ti, uj, vj, tj = res.ub[k]
        H1, H2 = 1 - 3 * xi**2 + 2 * xi**3, xi - 2 * xi**2 + xi**3
        H3, H4 = 3 * xi**2 - 2 * xi**3, -xi**2 + xi**3
        u = ui * (1 - xi) + uj * xi
        v = vi * H1 + ti * b.L * H2 + vj * H3 + tj * b.L * H4
        if cargas:
            up, vp = desplazamiento_particular(b, cargas, xi * b.L)
            u, v = u + up, v + vp
        ni, nj = modelo.nodos[b.i], modelo.nodos[b.j]
        X0, Y0 = ni.x + xi * (nj.x - ni.x), ni.y + xi * (nj.y - ni.y)
        curvas.append((X0, Y0, b.g1 * u - b.g2 * v, b.g2 * u + b.g1 * v))
    return curvas
