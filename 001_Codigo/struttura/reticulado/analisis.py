"""Verificación de las barras del reticulado: axil, tensión, coeficientes de seguridad y pandeo de Euler."""
from __future__ import annotations

import math

import numpy as np

from struttura.portico.esfuerzos import esfuerzos

from .entrada import PANDEO


from ..pandeo import carga_critica  # noqa: E402,F401


def verificar_barras(modelo, res) -> list:
    """Una fila por barra (dict):
       N (axil en i), Nmax / Nmin (extremos del axil a lo largo de la barra; difieren si hay carga axial distribuida),
       sigma (=N/A, con el N de mayor valor absoluto), dL (alargamiento), estado, CS fluencia / admisible,
       Pc, CS pandeo (solo compresión), esbeltez."""
    esf = esfuerzos(modelo, res)
    filas = []
    for k, b in enumerate(modelo.barras):
        N = esf["curvas"][k]["N"]
        tol = 1e-9 * max(float(np.abs(N).max()), 1e-300, 1e-6 * abs(res.Ftot[:, :2]).max())
        N = np.where(np.abs(N) < tol, 0.0, N)
        Nmax, Nmin = float(N.max()), float(N.min())
        Nc = Nmax if abs(Nmax) >= abs(Nmin) else Nmin          # axil dominante
        A = b.sec.A
        sig = Nc / A
        d = {"barra": b, "N": float(N[0]), "Nj": float(N[-1]), "Nmax": Nmax, "Nmin": Nmin, "Ndom": Nc,
             "sigma": sig, "dL": float(res.ub[k, 3] - res.ub[k, 0]),
             "estado": "tracción" if Nc > 1e-9 * (abs(Nmax) + abs(Nmin) + 1e-300) else
                       ("compresión" if Nc < -1e-9 * (abs(Nmax) + abs(Nmin) + 1e-300) else "sin esfuerzo"),
             "n_fy": None, "n_adm": None, "Pc": None, "n_pand": None, "lam": None, "cod": modelo.ret_pandeo[k]}
        if abs(sig) > 0:
            if b.mat.fy:
                d["n_fy"] = b.mat.fy / abs(sig)
            if b.mat.sadm:
                d["n_adm"] = b.mat.sadm / abs(sig)
        I = b.sec.I
        if getattr(b.sec, "pared", None) is not None:          # perfil de pared delgada: eje débil (menor inercia principal)
            I = min(b.sec.pared.Iy, b.sec.pared.Iz)
        tiene_I = b.sec.id not in modelo.ret_sin_I and I
        if tiene_I:
            d["Pc"] = carga_critica(b.mat.E, I, b.L, d["cod"])
            r = math.sqrt(I / A)
            d["lam"] = PANDEO[d["cod"]][1] * b.L / r
            if Nmin < 0:
                d["n_pand"] = d["Pc"] / abs(Nmin)
        filas.append(d)
    return filas
