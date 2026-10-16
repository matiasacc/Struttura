"""Esfuerzos internos, tensiones y elástica de cada barra (ejes LOCALES de la barra).

Convención de signos:
    V(x) = Pz_i + ∫q             V > 0: en la cara +xl actúa una fuerza hacia -z
                                  (sin cargas en el tramo es constante y vale Pz_i).
    T(x) = -Mx_i                  constante.  T > 0: vector momento torsor = +xl en la cara +xl.
    M(x) = My_i + x·Pz_i + M_q(x) M > 0: tracciona la fibra inferior (lado -z).
donde Pz_i, Mx_i, My_i son las fuerzas de extremo que el nodo i ejerce sobre la barra (ejes
locales, YA incluyen las fuerzas de empotramiento perfecto de las cargas del tramo) y q es la carga
en z (positiva hacia +z).  En el extremo j:  M(L) = -My_j,  T = Mx_j,  V(L) = -Pz_j.
"""
from __future__ import annotations

import numpy as np

from ..falla_plana import curva_utilizacion, evaluar_estados, tension_pared

from .cargas_barra import esfuerzos_en, flecha_particular
from .entrada import Modelo
from .solver import Resultado


def estaciones(L: float, cargas, n: int = 161):
    """Abscisas x (desde el nodo i) para dibujar/evaluar diagramas de una barra.

    Incluye los puntos donde empieza/termina una carga; en una fuerza puntual interior la abscisa se repite
    (antes y después del salto).  Devuelve (x, s) con s = -1/0/+1: lado desde el que se evalúa V."""
    xs = list(np.linspace(0.0, L, n))
    sg = [0] * len(xs)
    eps = 1e-9 * L
    for c, _ in cargas:
        if c.tipo == "P" and eps < c.a < L - eps:          # el cortante salta: abscisa repetida
            xs += [c.a, c.a]
            sg += [-1, +1]
        elif c.tipo == "q":                                # V continuo; solo cambia la pendiente de M
            for xv in (c.a, c.b):
                if eps < xv < L - eps:
                    xs.append(xv)
                    sg.append(0)
    x = np.array(xs)
    s = np.array(sg)
    saltos = x[s != 0]
    o = np.lexsort((s, x))
    x, s = x[o], s[o]
    # descartar puntos "normales" repetidos o coincidentes con un salto
    tol = 1e-7 * L
    ok = np.ones(len(x), dtype=bool)
    for i in range(1, len(x)):
        if s[i] == 0 and abs(x[i] - x[i - 1]) < tol:
            ok[i] = False
        if s[i] == 0 and saltos.size and np.min(np.abs(saltos - x[i])) < tol:
            ok[i] = False
        if s[i - 1] == 0 and s[i] != 0 and abs(x[i] - x[i - 1]) < tol:
            ok[i - 1] = False
    return x[ok], s[ok]


def curvas_barra(modelo: Modelo, res: Resultado, k: int, n: int = 161) -> dict:
    """V(x) y M(x) de la barra k (índice), en ejes locales, con las cargas del tramo.

    V(x) = Pz_i + ΣV_carga(x)       M(x) = My_i + x·Pz_i + ΣM_carga(x)     T(x) = -Mx_i (constante)
    (Pz_i, My_i ya incluyen las fuerzas de empotramiento perfecto f0.)
    """
    b = modelo.barras[k]
    cargas = res.cargas_de(k)
    x, s = estaciones(b.L, cargas, n)
    d = 1e-9 * b.L
    xv = np.clip(x + s * d, 0.0, b.L)
    Pz, My = res.fb[k, 0], res.fb[k, 2]
    V, _ = esfuerzos_en(b, (Pz, My), cargas, xv)
    _, M = esfuerzos_en(b, (Pz, My), cargas, x)
    return {"x": x, "V": V, "M": M, "T": -res.fb[k, 1]}


def esfuerzos(modelo: Modelo, res: Resultado, n: int = 161) -> dict:
    """Esfuerzos por barra.  Claves (arreglos por barra):
        V, Vj     cortante en i y en j (con cargas en el tramo Vj ≠ V)
        T         torsor (constante: no hay torsores en el tramo)
        Mi, Mj    flector en i y en j
        Mmax, xMmax, Mmin, xMmin   extremos del flector a lo largo de la barra (x desde i)
        Vabs      máximo |V| a lo largo de la barra
        curvas    lista de dicts {x, V, M, T} (ver curvas_barra)
    """
    nb = len(modelo.barras)
    e = {k: np.zeros(nb) for k in ("V", "Vj", "T", "Mi", "Mj", "Mmax", "xMmax", "Mmin", "xMmin", "Vabs")}
    e["curvas"] = []
    for k, b in enumerate(modelo.barras):
        cv = curvas_barra(modelo, res, k, n)
        e["curvas"].append(cv)
        e["V"][k] = res.fb[k, 0]
        e["Vj"][k] = -res.fb[k, 3]
        e["T"][k] = cv["T"]
        e["Mi"][k] = res.fb[k, 2]
        e["Mj"][k] = -res.fb[k, 5]
        M, x = cv["M"], cv["x"]
        e["Mmax"][k], e["xMmax"][k] = M.max(), x[M.argmax()]
        e["Mmin"][k], e["xMmin"][k] = M.min(), x[M.argmin()]
        e["Vabs"][k] = np.abs(cv["V"]).max()
    return e


def funciones_barra(modelo: Modelo, res: Resultado, k: int) -> list:
    """Funciones exactas de V(x) y M(x) de la barra k, por tramos (x desde el nodo i, ejes locales).

    Devuelve [{"x0", "x1", "V": Polynomial, "M": Polynomial, "T": valor}, ...].  Los tramos se parten donde
    empieza o termina una carga.  V y M son polinomios en x (V hasta grado 2, M hasta grado 3)."""
    from numpy.polynomial import Polynomial as Pol
    b = modelo.barras[k]
    cargas = [(c, f) for c, f in res.cargas_de(k) if c.tipo in ("q", "P")]
    eps = 1e-9 * b.L
    cortes = {0.0, b.L}
    for c, _ in cargas:
        for xv in ((c.a, c.b) if c.tipo == "q" else (c.a,)):
            if eps < xv < b.L - eps:
                cortes.add(float(xv))
    cortes = sorted(cortes)
    X = Pol([0.0, 1.0])
    Pz, My = res.fb[k, 0], res.fb[k, 2]
    out = []
    for x0, x1 in zip(cortes[:-1], cortes[1:]):
        xm = (x0 + x1) / 2
        V, M = Pol([Pz]), Pol([My]) + Pz * X
        for c, f in cargas:
            if c.tipo == "P":
                if xm > c.a:
                    V = V + f * c.v1
                    M = M + f * c.v1 * (X - c.a)
                continue
            if xm <= c.a:
                continue
            m = (c.v2 - c.v1) / (c.b - c.a)
            q = Pol([c.v1 - m * c.a, m])
            F, G = q.integ(), (Pol([0.0, 1.0]) * q).integ()
            hasta = X if xm < c.b else Pol([c.b])
            Fx, Gx = F(hasta) if xm < c.b else Pol([F(c.b)]), G(hasta) if xm < c.b else Pol([G(c.b)])
            Vq = Fx - F(c.a)
            Mq = X * Vq - (Gx - G(c.a))
            V = V + f * Vq
            M = M + f * Mq
        out.append({"x0": x0, "x1": x1, "V": V, "M": M, "T": -res.fb[k, 1]})
    return out


def tensiones(modelo: Modelo, esf: dict) -> list:
    """Tensiones por barra.  Devuelve lista de dicts (None si la sección no tiene datos).

    - Flexión:  σ = M·c/I en la fibra extrema (se informa con signo: + = tracción en fibra inferior).
    - Torsión:  τt = |T|/Wt en el contorno.
    - Corte:    τv = kv·|V|/A en el eje neutro.
    - Von Mises evaluada en dos puntos de control en cada sección estudiada:
        (a) fibra extrema:  σeq = √(σ² + 3·τt²)          (el corte vertical es nulo ahí)
        (b) eje neutro:     σeq = √3·(τt + τv)           (σ = 0; se suman: caso desfavorable)
      Se informa el máximo entre todas las secciones estudiadas (a lo largo de toda la barra
      cuando hay cargas en el tramo; solo en los extremos si no las hay, donde es lo mismo).
    """
    salida = []
    for k, b in enumerate(modelo.barras):
        s = b.sec
        cv = esf["curvas"][k]
        T = esf["T"][k]
        d = {"sig_i": None, "sig_j": None, "sig_max": None, "x_sig_max": None,
             "tau_t": None, "tau_v": None, "vm": None, "x_vm": None, "n_fy": None, "n_adm": None,
             "corte_incluido": s.kv is not None and s.A is not None and modelo.config.get("corte_tensiones", "si") == "si"}
        if getattr(s, "pared", None) is not None:                  # perfil de pared delgada: motor del 3D (Jourawski + torsión + centro de corte)
            corte = modelo.config.get("corte_tensiones", "si") == "si"
            tp = tension_pared(s, b.mat, np.zeros_like(cv["V"]), cv["V"], cv["M"], np.full_like(cv["V"], T), corte)
            d["corte_incluido"] = corte
            sx = tp["sx"]
            ext = lambda f: sx[f][np.abs(sx[f]).argmax()]
            d["sig_i"], d["sig_j"] = float(ext(0)), float(ext(-1))
            i, j = np.unravel_index(np.abs(sx).argmax(), sx.shape)
            d["sig_max"], d["x_sig_max"] = float(sx[i, j]), float(cv["x"][i])
            d["tau_v"] = float(tp["tau"].max())          # en perfiles de pared delgada: corte + torsión juntos (ver nota del informe)
            eq = tp["eq"]
            m = int(eq.argmax())
            d["vm"], d["x_vm"], d["punto"], d["teoria"] = float(eq[m]), float(cv["x"][m]), tp["punto"], b.mat.teoria
            d["curva_vm"], d["x_curva"] = curva_utilizacion(b.mat, eq, tp["cs"]), cv["x"]
            if d["vm"] > 0:
                d["n_fy"] = None if tp["cs"] is None else float(tp["cs"].min())
                d["n_adm"] = None if tp["cs_adm"] is None else float(tp["cs_adm"].min())
            salida.append(d)
            continue
        if s.c is not None and s.I:
            d["sig_i"] = esf["Mi"][k] * s.c / s.I
            d["sig_j"] = esf["Mj"][k] * s.c / s.I
            sig = cv["M"] * s.c / s.I
            m = int(np.abs(sig).argmax())
            d["sig_max"], d["x_sig_max"] = float(sig[m]), float(cv["x"][m])
        if s.Wt:
            d["tau_t"] = abs(T) / s.Wt
        tv = s.kv * np.abs(cv["V"]) / s.A if d["corte_incluido"] else np.zeros_like(cv["V"])
        d["tau_v"] = float(tv.max())
        if d["sig_max"] is not None and d["tau_t"] is not None:
            tt = d["tau_t"]
            # criterio de falla del material (por defecto Von Mises) en tres estados de control: fibra inferior, fibra superior y eje neutro
            eq, cs, cs_adm = evaluar_estados(b.mat, [(sig, tt + 0 * sig), (-sig, tt + 0 * sig), (0 * sig, tt + tv)])
            m = int(eq.argmax())
            d["vm"], d["x_vm"] = float(eq[m]), float(cv["x"][m])
            d["curva_vm"], d["x_curva"] = curva_utilizacion(b.mat, eq, cs), cv["x"]     # σeq a lo largo de la barra (visor: modo Utilización)
            d["teoria"] = b.mat.teoria
            if d["vm"] > 0:
                if cs is not None:
                    d["n_fy"] = float(cs.min())             # CS de la teoría del material (Von Mises: fy/σVM)
                if cs_adm is not None:
                    d["n_adm"] = float(cs_adm.min())        # coeficiente respecto de la tensión admisible
        salida.append(d)
    return salida


def elastica(modelo: Modelo, res: Resultado, n: int = 25):
    """Curva elástica de cada barra en coordenadas globales.

    w(x) = Hermite cúbico de (uz, φy) de los extremos (θy = -dw/dx)  +  w_p(x), la flecha de la barra
    biempotrada bajo las cargas del tramo (0 si no hay).  Devuelve lista de (X, Y, W) por barra.
    """
    curvas = []
    for k, b in enumerate(modelo.barras):
        cargas = res.cargas_de(k)
        xi = np.linspace(0.0, 1.0, max(n, 61) if res.cb else n)
        H1 = 1 - 3 * xi**2 + 2 * xi**3
        H2 = xi - 2 * xi**2 + xi**3
        H3 = 3 * xi**2 - 2 * xi**3
        H4 = -xi**2 + xi**3
        wi, thi, wj, thj = res.ub[k, 0], res.ub[k, 2], res.ub[k, 3], res.ub[k, 5]
        W = wi * H1 + (-thi) * b.L * H2 + wj * H3 + (-thj) * b.L * H4
        if cargas:
            W = W + flecha_particular(b, cargas, xi * b.L)
        ni, nj = modelo.nodos[b.i], modelo.nodos[b.j]
        X = ni.x + xi * (nj.x - ni.x)
        Y = ni.y + xi * (nj.y - ni.y)
        curvas.append((X, Y, W))
    return curvas
