"""Criterios de falla en los programas planos (pórtico plano y emparrillado): misma teoría y mismas fórmulas que el pórtico 3D.

Columnas de MATERIALES:  sut ; suc ; teoria   (teoria: vm | tresca | rankine | mohr | mohrmod; por defecto vm si hay fy, rankine si solo hay sut).
Los criterios se evalúan en los mismos puntos de control de cada programa plano (fibras extremas y eje neutro), con el estado plano
σx, τ de esos puntos.  Fórmulas y fuentes: ver portico3d/tensor.py (Von Mises, Tresca, Rankine, Mohr y Mohr modificado, Compendio cap. 2)."""
from __future__ import annotations

import numpy as np

from .portico3d.tensor import TEORIAS, criterios  # noqa: F401

_ALIAS = {"": "", "vm": "vm", "mises": "vm", "von mises": "vm", "vonmises": "vm", "tresca": "tresca",
          "rankine": "rankine", "mohr": "mohr", "mohr-coulomb": "mohr", "coulomb": "mohr",
          "mohrmod": "mohrmod", "mohr modificado": "mohrmod", "mohr-modificado": "mohrmod",
          "mohr_modificado": "mohrmod", "mohr mod": "mohrmod"}


def resolver_teoria(id_, n, fy, sut, suc, texto, avisos, Error):
    """(teoria, suc) del material.  Error: la excepción de entrada del programa."""
    t = (texto or "").strip().lower()
    if t not in _ALIAS:
        raise Error(f"Bloque MATERIALES, línea {n}: teoria '{t}' desconocida (vm, tresca, rankine, mohr, mohrmod)")
    explicita = _ALIAS[t]
    teoria = explicita or ("vm" if fy is not None else ("rankine" if sut is not None else "vm"))
    if teoria in ("vm", "tresca") and fy is None and explicita:
        raise Error(f"Bloque MATERIALES, línea {n}: la teoría '{teoria}' necesita fy")
    if teoria in ("rankine", "mohr", "mohrmod") and sut is None:
        raise Error(f"Bloque MATERIALES, línea {n}: la teoría '{teoria}' necesita sut (resistencia a tracción)")
    if suc is None:
        suc = sut
    if teoria in ("mohr", "mohrmod") and suc < sut:
        avisos.append(f"Material '{id_}': suc ({suc:g}) < sut ({sut:g}); las teorías de Mohr suponen |σc| ≥ σt.")
    return teoria, suc


def referencia(mat):
    """Resistencia con la que se normaliza la utilización: fy (Von Mises, Tresca) o sut (Rankine, Mohr)."""
    if mat.teoria in ("vm", "tresca"):
        return mat.fy
    return mat.sut


def evaluar_estados(mat, estados):
    """estados: lista de (σx, τ) con arrays de igual forma (una estación por posición).
    Devuelve (eq, cs, cs_adm): σ equivalente gobernante (máximo entre estados), CS mínimo (o None) y CS respecto de σadm (o None)."""
    eq = cs = None
    for sx, tau in estados:
        sx, tau = np.asarray(sx, float), np.asarray(tau, float)
        c = criterios(sx, tau, np.zeros_like(tau), mat)
        eq = c["eq_gob"] if eq is None else np.maximum(eq, c["eq_gob"])
        if c["cs_gob"] is not None:
            cs = c["cs_gob"] if cs is None else np.minimum(cs, c["cs_gob"])
    cs_adm = None
    if mat.sadm:
        with np.errstate(divide="ignore", invalid="ignore"):
            cs_adm = np.where(eq > 0, mat.sadm / eq, np.inf)
    return eq, cs, cs_adm


def curva_utilizacion(mat, eq, cs):
    """Curva que ve el visor en el modo Utilización: σeq si la referencia es fy (Von Mises, Tresca); σ* = sut/CS en las demás teorías."""
    if mat.teoria in ("vm", "tresca") or cs is None:
        return eq
    return referencia(mat) / np.maximum(cs, 1e-300)


def tension_pared(sec, mat, N, V, M, T=None, corte=True):
    """Tensiones de un perfil de pared delgada en una barra de un programa plano, con el mismo motor del 3D (portico3d/tensor.py:
    Jourawski + torsión de Saint-Venant, centro de corte).  N, V, M, T: arrays por estación con las convenciones del programa plano
    (V y M como los informa el programa; T = 0 en el pórtico plano).  La dimensión h del perfil está en el plano de la flexión
    (eje z del perfil; en el pórtico plano, el eje local y de la barra).
    Devuelve dict: sx (m,p), tau (m,p), eq (m,), cs (m,)|None, cs_adm (m,)|None, punto (rótulo del punto más exigido)."""
    from types import SimpleNamespace

    from .portico3d.tensor import campos, puntos_candidatos
    pd = sec.pared
    s3 = SimpleNamespace(A=pd.A, Iy=pd.Iy, Iz=pd.Iz, pared=pd, tipo=sec.tipo, dim=sec.dim, cy=pd.cy, cz=pd.cz, Wt=pd.Wt, J=pd.J)
    N, V, M = (np.asarray(a, float) for a in (N, V, M))
    T = np.zeros_like(N) if T is None else np.asarray(T, float)
    E = np.stack([N, 0 * N, -V, T, -M, 0 * N], axis=1)             # convención del 3D: Vz = −V, My = −M (verificado contra el solver 3D)
    pts = puntos_candidatos(s3)
    ys = np.array([p[0] for p in pts])
    zs = np.array([p[1] for p in pts])
    sx, txy, txz = campos(s3, E, ys, zs, corte)
    c = criterios(sx, txy, txz, mat)
    eq = c["eq_gob"]
    j = int(np.unravel_index(np.argmax(eq), eq.shape)[1])
    cs = None if c["cs_gob"] is None else c["cs_gob"].min(axis=1)
    cs_adm = c["cs_adm"].min(axis=1) if "cs_adm" in c else None
    return {"sx": sx, "tau": c["tau"], "eq": eq.max(axis=1), "cs": cs, "cs_adm": cs_adm, "punto": pts[j][2]}


def rotulos(modelo):
    """Textos de los informes planos según la(s) teoría(s) de falla usadas y los perfiles de pared delgada presentes."""
    teo = sorted({TEORIAS[b.mat.teoria] for b in modelo.barras})
    vm = teo == ["Von Mises"]
    pared = any(getattr(b.sec, "pared", None) is not None for b in modelo.barras)
    nota = "" if vm else (f"  σ<sub>eq</sub> según la teoría de cada material ({', '.join(teo)}); CS = resistencia/σ<sub>eq</sub> "
                          "(Von Mises y Tresca: f<sub>y</sub>; Rankine, Mohr y Mohr modificado: s<sub>ut</sub>/s<sub>uc</sub>; fórmulas en la Memoria), evaluada en los mismos puntos de control.")
    if pared:
        nota += ("  Perfiles de pared delgada: tensiones en 5 a 24 puntos de la línea media con el corte de flexión de Jourawski y la torsión de Saint-Venant "
                 "(τ<sub>v</sub> es el máximo de corte y torsión juntos); la flexión se supone alrededor del eje principal fuerte, con h en el plano de la flexión.")
    return {"cs": "CS fluencia" if vm else "CS", "eq": "σ<sub>VM,máx</sub>" if vm else "σ<sub>eq,máx</sub>", "nombre": "Von Mises" if vm else "equivalente", "nota": nota}
