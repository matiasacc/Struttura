"""Esfuerzos internos a lo largo de las barras espaciales (exactos, por equilibrio) y tensiones.

Esfuerzos sobre la cara +x de la sección (regla de la mano derecha respecto de los ejes locales):
    N   axil (tracción +)             Vy, Vz   cortes en y y en z locales
    T   torsión                        My       momento alrededor de y  (My > 0 traccciona la fibra +z)
    Mz  momento alrededor de z  (Mz > 0 traccciona la fibra −y)
Tensión normal:  σ = N/A + My·z/Iy − Mz·y/Iz
"""
from __future__ import annotations

import numpy as np

from .cargas_barra import esfuerzos_en

NOMBRES = ("N", "Vy", "Vz", "T", "My", "Mz")


def estaciones(cargas, L, n=41):
    xs = list(np.linspace(0.0, L, n))
    dup = []
    for c in cargas:
        if c[0] != "q":
            a = c[1]
            xs.append(a)
            dup.append(a)
    xs = sorted(set(round(x, 9) for x in xs))
    pares = []
    for x in xs:
        if any(abs(x - a) < 1e-9 * L for a in dup):
            pares.append((x, False))
            pares.append((x, True))
        else:
            pares.append((x, True))
    return pares


def diagramas(modelo, res, k, n=41):
    """(xs, E) con E (m,6) = [N, Vy, Vz, T, My, Mz] en cada estación de la barra k."""
    b = modelo.barras[k]
    fb = res.fb[k]
    cargas = [(tuple(c[:3]) + (b.L,) if c[0] == "q" else c, f) for c, f in res.cargas_de(k)]
    esc = [_escalar(c, f) for c, f in cargas]
    xs, E = [], []
    for x, despues in estaciones(esc, b.L, n):
        xs.append(x)
        E.append(esfuerzos_en(x, fb[:3], fb[3:6], esc, b.L, despues))
    return np.array(xs), np.array(E)


def _escalar(c, f):
    if c[0] == "q":
        return ("q", c[1] * f, c[2] * f, c[3])
    return (c[0], c[1], c[2] * f)


def esfuerzos_extremos(modelo, res):
    """Por barra: valores en i y j y máximos absolutos de cada componente (con su abscisa)."""
    out = []
    for k, b in enumerate(modelo.barras):
        xs, E = diagramas(modelo, res, k)
        d = {"xs": xs, "E": E, "i": E[0], "j": E[-1]}
        idx = np.abs(E).argmax(axis=0)
        d["max"] = np.array([E[idx[c], c] for c in range(6)])
        d["x_max"] = np.array([xs[idx[c]] for c in range(6)])
        out.append(d)
    return out


def tensiones(modelo, res, analisis=None):
    """Por barra (a partir del tensor de tensiones en los puntos candidatos de la sección):
    σx máxima de tracción / compresión, τ total máxima, σ equivalente gobernante máxima (según la teoría del material) y CS mínimo."""
    from .tensor import analizar
    an = analisis or analizar(modelo, res)
    return [{"sig_t": d["sig_t"], "sig_c": d["sig_c"], "tau_t": d["tau"], "vm": d["eq"], "cs": d["cs"], "x_vm": d["x_eq"],
             "punto": d["punto"]} for d in an["barras"]]


def pandeo_barras(modelo, res, ext=None):
    """Pandeo de Euler por barra (lista de dicts {cod, Pc, lam, n_pand, Nmin, I}): I = la menor de Iy e Iz (eje débil de la sección);
    CS = Pc/|Nmin| solo en barras comprimidas.  Condición de extremos: columna `pandeo` de BARRAS (struttura/pandeo.py)."""
    from ..pandeo import verificar
    ext = ext or esfuerzos_extremos(modelo, res)
    out = []
    for b, e in zip(modelo.barras, ext):
        I = min(b.sec.Iy, b.sec.Iz)
        d = verificar(b.mat.E, I, b.sec.A, b.L, b.pandeo, float(e["E"][:, 0].min()))
        d.update(Nmin=float(e["E"][:, 0].min()), I=I)
        out.append(d)
    return out
