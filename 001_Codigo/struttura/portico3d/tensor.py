"""Tensor de tensiones en puntos de la sección de las barras espaciales (teoría de vigas) y criterios de falla.

En un punto (y, z) de la sección (coordenadas locales desde el baricentro) el estado de tensiones es
                    | σx   τxy  τxz |
            σ  =    | τxy   0    0  |          σx = N/A + My·z/Iy − Mz·y/Iz
                    | τxz   0    0  |          τ  = torsión (T) + corte de flexión (Vy, Vz; Jourawski)

Sus tensiones principales son  σ1 = (σx + √(σx² + 4τ²))/2 ≥ 0,  σ2 = 0,  σ3 = (σx − √(σx² + 4τ²))/2 ≤ 0,  con τ² = τxy² + τxz².

Criterios (σeq y coeficiente de seguridad CS = resistencia / σeq):
    Von Mises   σeq = √(σx² + 3τ²)                          CS = fy / σeq
    Tresca      σeq = σ1 − σ3 = √(σx² + 4τ²)                CS = fy / σeq
    Rankine     σeq = máx(σ1, |σ3|)                          CS = mín(sut/σ1, suc/|σ3|)
    Mohr (dúctil, |σc| > σt)   σ* = σ1 + α·|σ3|,  α = sut/suc            CS = sut / σ*      (Compendio cap. 2, (64)-(66))
    Mohr modificado (frágil, |σc| > σt)   σ* = mayor{σ1 ; α·|σ3| + (1−α)·σ1}   CS = sut / σ*   (Compendio cap. 2, (70)-(73))

Distribución del corte (aproximaciones clásicas, todas verifican ∫τ dA = V y ∫(y·τxz − z·τxy) dA = T):
    circular / tubo   torsión T·r/J tangencial;  corte: circular macizo 4V/(3A)(1 − (c/R)²) ; tubo (pared delgada) V·cos(φ)/(π·Rm·t)
    rectangular       torsión T/Wt (conservadora, en la dirección de la cara);  corte parabólico 3V/(2A)(1 − (2c/dim)²)
    rect. hueca       torsión de Bredt T/(2·Am·t);  corte de Jourawski en almas y alas (pared delgada: sin acople entre Vy y Vz ni
                      flujo en las esquinas; en paredes gruesas el corte integrado queda 5–10 % por debajo de V)
    genérica          torsión T/Wt (si hay Wt); sin corte de flexión (no hay datos de la geometría)
"""
from __future__ import annotations

import math

import numpy as np

TEORIAS = {"vm": "Von Mises", "tresca": "Tresca", "rankine": "Rankine", "mohr": "Mohr", "mohrmod": "Mohr modificado"}


# --------------------------------------------------------------------------
def puntos_candidatos(sec):
    """Puntos (y, z, rótulo) de la sección donde se evalúa el tensor automáticamente."""
    pts = []
    if sec.pared is not None:
        return sec.pared.puntos()
    if sec.tipo in ("tubo", "circular"):
        R = sec.dim["d"] / 2
        for k in range(24):                                   # cada 15°: error de muestreo de σ ≤ 0,9 %
            f = k * math.pi / 12
            pts.append((R * math.cos(f), R * math.sin(f), f"borde {15 * k}°"))
        if sec.tipo == "circular":
            pts.append((0.0, 0.0, "centro"))
    elif sec.cy is not None and sec.cz is not None:
        cy, cz = sec.cy, sec.cz
        for y, z, n in ((cy, cz, "esquina +y+z"), (-cy, cz, "esquina −y+z"), (-cy, -cz, "esquina −y−z"), (cy, -cz, "esquina +y−z"),
                        (cy, 0, "cara +y"), (-cy, 0, "cara −y"), (0, cz, "cara +z"), (0, -cz, "cara −z")):
            pts.append((y, z, n))
        pts.append((0.0, 0.0, "baricentro"))
    return pts


# --------------------------------------------------------------------------
def _torsion(sec, y, z):
    """Tensiones por unidad de T: (txy, txz)."""
    if sec.tipo in ("tubo", "circular"):
        return -z / sec.J, y / sec.J
    if sec.tipo == "rect_hueca":
        b, h, t = sec.dim["b"], sec.dim["h"], sec.dim["t"]
        tau = 1.0 / (2 * (b - t) * (h - t) * t)
        lado = np.abs(y) / (b / 2) >= np.abs(z) / (h / 2)          # cara ±y (alma) o ±z (ala)
        return np.where(lado, 0.0, -np.sign(z) * tau), np.where(lado, np.sign(y) * tau, 0.0)
    if sec.Wt:
        tau = 1.0 / sec.Wt
        if sec.tipo == "rectangular":
            b, h = sec.dim["b"], sec.dim["h"]
            lado = np.abs(y) / (b / 2) >= np.abs(z) / (h / 2)
            return np.where(lado, 0.0, -np.sign(z) * tau), np.where(lado, np.sign(y) * tau, 0.0)
        r = np.hypot(y, z)
        rr = np.where(r > 0, r, 1.0)
        return np.where(r > 0, -tau * z / rr, 0.0), np.where(r > 0, tau * y / rr, 0.0)
    return np.zeros_like(y), np.zeros_like(y)


def _corte(sec, Vy, Vz, y, z):
    """Tensiones por corte de flexión: (txy, txz).  Vy, Vz: arrays (m,1); y, z: arrays (1,p)."""
    A = sec.A
    zero = np.zeros(np.broadcast(Vy, y).shape)
    if sec.tipo == "circular":
        R = sec.dim["d"] / 2
        return 4 * Vy / (3 * A) * (1 - (y / R) ** 2), 4 * Vz / (3 * A) * (1 - (z / R) ** 2)
    if sec.tipo == "tubo":
        d, t = sec.dim["d"], sec.dim["t"]
        Rm = (d - t) / 2
        f = np.arctan2(z, y)
        tt = (Vz * np.cos(f) - Vy * np.sin(f)) / (math.pi * Rm * t)
        return -tt * np.sin(f), tt * np.cos(f)
    if sec.tipo == "rectangular":
        b, h = sec.dim["b"], sec.dim["h"]
        return 1.5 * Vy / A * (1 - (2 * y / b) ** 2), 1.5 * Vz / A * (1 - (2 * z / h) ** 2)
    if sec.tipo == "rect_hueca":
        b, h, t = sec.dim["b"], sec.dim["h"], sec.dim["t"]
        bi, hi = b - 2 * t, h - 2 * t
        Qz = b * (h**2 - hi**2) / 8 + t * (hi**2 / 4 - z**2)          # Vz: en las almas (|y| > bi/2)
        Qy = h * (b**2 - bi**2) / 8 + t * (bi**2 / 4 - y**2)          # Vy: en las alas (|z| > hi/2)
        en_alma = (np.abs(y) > bi / 2 - 1e-9) & (np.abs(z) <= hi / 2 + 1e-9)
        en_ala = (np.abs(z) > hi / 2 - 1e-9) & (np.abs(y) <= bi / 2 + 1e-9)
        txz = np.where(en_alma, Vz * Qz / (sec.Iy * 2 * t), 0.0)
        txy = np.where(en_ala, Vy * Qy / (sec.Iz * 2 * t), 0.0)
        return txy + zero, txz + zero
    return zero, zero


def campos(sec, E, y, z, corte=True):
    """σx, τxy, τxz en los puntos (y, z) para cada fila de E (m,6) = [N, Vy, Vz, T, My, Mz].
    y, z: escalares o arrays (p,).  Devuelve arrays (m, p)."""
    E = np.atleast_2d(E)
    y = np.atleast_1d(np.asarray(y, float))[None, :]
    z = np.atleast_1d(np.asarray(z, float))[None, :]
    N, Vy, Vz, T, My, Mz = (E[:, c][:, None] for c in range(6))
    sx = N / sec.A + My * z / sec.Iy - Mz * y / sec.Iz
    if sec.pared is not None:
        z0 = np.zeros_like(Vy)
        txy, txz = sec.pared.tensiones(y, z, Vy if corte else z0, Vz if corte else z0, T)
        shape = np.broadcast(sx, txy, txz).shape
        return (np.broadcast_to(sx, shape).copy(), np.broadcast_to(txy, shape).copy(), np.broadcast_to(txz, shape).copy())
    ty0, tz0 = _torsion(sec, y, z)
    txy, txz = T * ty0, T * tz0
    if corte:
        cy, cz = _corte(sec, Vy, Vz, y, z)
        txy = txy + cy
        txz = txz + cz
    shape = np.broadcast(sx, txy, txz).shape
    return (np.broadcast_to(sx, shape).copy(), np.broadcast_to(txy, shape).copy(), np.broadcast_to(txz, shape).copy())


# --------------------------------------------------------------------------
def criterios(sx, txy, txz, mat):
    """Principales, τmáx, tensiones equivalentes y CS.  Devuelve dict de arrays."""
    tau = np.hypot(txy, txz)
    rad = np.sqrt(sx**2 + 4 * tau**2)
    s1, s3 = (sx + rad) / 2, (sx - rad) / 2
    out = {"tau": tau, "s1": s1, "s2": np.zeros_like(s1), "s3": s3, "tau_max": rad / 2,
           "vm": np.sqrt(sx**2 + 3 * tau**2), "tresca": rad, "rankine": np.maximum(s1, -s3)}
    with np.errstate(divide="ignore", invalid="ignore"):
        cs = {}
        if mat.fy:
            cs["vm"] = np.where(out["vm"] > 0, mat.fy / out["vm"], np.inf)
            cs["tresca"] = np.where(out["tresca"] > 0, mat.fy / out["tresca"], np.inf)
        if mat.sut:
            suc = mat.suc or mat.sut
            ct = np.where(s1 > 0, mat.sut / s1, np.inf)
            cc = np.where(s3 < 0, suc / -s3, np.inf)
            cs["rankine"] = np.minimum(ct, cc)
            alfa = mat.sut / suc
            s1p, s3n = np.maximum(s1, 0.0), np.maximum(-s3, 0.0)
            out["mohr"] = s1p + alfa * s3n                                          # σ* de Mohr
            out["mohrmod"] = np.maximum(s1p, alfa * s3n + (1 - alfa) * s1p)         # σ* de Mohr modificado
            for t in ("mohr", "mohrmod"):
                cs[t] = np.where(out[t] > 0, mat.sut / out[t], np.inf)
    out["cs"] = cs
    eq = {k: out[k] for k in ("vm", "tresca", "rankine", "mohr", "mohrmod") if k in out}
    out["eq_gob"] = eq[mat.teoria]
    out["cs_gob"] = cs.get(mat.teoria)
    if mat.sadm:
        with np.errstate(divide="ignore", invalid="ignore"):
            out["cs_adm"] = np.where(out["eq_gob"] > 0, mat.sadm / out["eq_gob"], np.inf)
    return out


def matriz(sx, txy, txz):
    return np.array([[sx, txy, txz], [txy, 0.0, 0.0], [txz, 0.0, 0.0]])


def angulo_s1(sx, txy, txz):
    """Ángulo (grados) entre el eje de σ1 y el eje x local de la barra."""
    tau = math.hypot(txy, txz)
    return math.degrees(0.5 * math.atan2(2 * tau, sx))


# --------------------------------------------------------------------------
# Análisis de un modelo resuelto
# --------------------------------------------------------------------------
def _punto(modelo, res, k, x, y, z, rotulo, corte, E=None):
    """Registro completo de un punto (barra k, abscisa x, coordenadas locales y, z)."""
    from .cargas_barra import esfuerzos_en
    b = modelo.barras[k]
    if E is None:
        fb = res.fb[k]
        esc = []
        for c, f in res.cargas_de(k):
            esc.append(("q", c[1] * f, c[2] * f, c[3]) if c[0] == "q" else (c[0], c[1], c[2] * f))
        E = esfuerzos_en(x, fb[:3], fb[3:6], esc, b.L, True)
    sx, txy, txz = (float(v[0, 0]) for v in campos(b.sec, E, y, z, corte))
    esc_t = max(abs(sx), abs(txy), abs(txz), 1e-300)
    sx, txy, txz = (0.0 if abs(v) < 1e-9 * esc_t else v for v in (sx, txy, txz))
    c = criterios(np.array([sx]), np.array([txy]), np.array([txz]), b.mat)
    E = np.array(E, float)
    E[np.abs(E) < 1e-9 * max(np.abs(E).max(), 1e-300)] = 0.0
    reg = {"barra": k, "x": float(x), "y": float(y), "z": float(z), "rotulo": rotulo, "E": E,
           "sx": float(sx), "txy": float(txy), "txz": float(txz), "ang": angulo_s1(sx, txy, txz)}
    for nom in ("tau", "s1", "s2", "s3", "tau_max", "vm", "tresca", "rankine", "mohr", "mohrmod"):
        if nom in c:
            reg[nom] = float(c[nom][0])
    reg["cs"] = {kk: float(v[0]) for kk, v in c["cs"].items()}
    reg["cs_gob"] = None if c["cs_gob"] is None else float(c["cs_gob"][0])
    reg["eq_gob"] = float(c["eq_gob"][0])
    reg["cs_adm"] = float(c["cs_adm"][0]) if "cs_adm" in c else None
    return reg


def analizar(modelo, res, ntop=6, corte=None):
    """Devuelve {"barras": [...], "criticos": [...], "usuario": [...]} para un resultado (caso o combinación).

    barras[k]: resumen por barra (σ máx/mín, τ máx, σeq máx, CS mínimo, punto crítico) y utilización a lo largo de la barra.
    criticos: los ntop puntos más exigidos (uno por barra como máximo), ordenados por σeq gobernante.
    usuario:  tensores de los puntos pedidos en el bloque PUNTOS DE TENSION.
    """
    from .esfuerzos import diagramas
    corte = (modelo.config.get("corte_tensiones", "si") == "si") if corte is None else corte
    res_barras, candidatos = [], []
    for k, b in enumerate(modelo.barras):
        xs, E = diagramas(modelo, res, k)
        pts = puntos_candidatos(b.sec)
        d = {"sig_t": None, "sig_c": None, "tau": None, "eq": None, "cs": None, "x_eq": None, "punto": None,
             "util": None, "util_adm": None, "xs": xs}
        if pts:
            ys = np.array([p[0] for p in pts])
            zs = np.array([p[1] for p in pts])
            sx, txy, txz = campos(b.sec, E, ys, zs, corte)
            c = criterios(sx, txy, txz, b.mat)
            eq = c["eq_gob"]
            i, j = np.unravel_index(np.argmax(eq), eq.shape)
            d.update(sig_t=float(sx.max()), sig_c=float(sx.min()), tau=float(c["tau"].max()), eq=float(eq[i, j]),
                     x_eq=float(xs[i]), punto=pts[j][2])
            if c["cs_gob"] is not None:
                d["cs"] = float(c["cs_gob"].min())
            ref = (b.mat.fy if b.mat.teoria in ("vm", "tresca") else None)
            if ref:
                d["util"] = (eq.max(axis=1) / ref).tolist()
            elif c["cs_gob"] is not None:
                d["util"] = (1.0 / np.maximum(c["cs_gob"].min(axis=1), 1e-12)).tolist()
            if b.mat.sadm:                                       # σeq/σadm en cada sección (mismo criterio que los programas planos)
                d["util_adm"] = (eq.max(axis=1) / b.mat.sadm).tolist()
            candidatos.append((float(eq[i, j]), k, float(xs[i]), pts[j], E[i]))
        res_barras.append(d)
    candidatos.sort(key=lambda t: -t[0])
    criticos = [_punto(modelo, res, k, x, p[0], p[1], p[2], corte, E) for _, k, x, p, E in candidatos[:ntop]]
    usuario = []
    for pu in modelo.puntos:
        if pu["caso"] is None or pu["caso"] == res.nombre:
            r = _punto(modelo, res, pu["barra"], pu["x"], pu["y"], pu["z"], "pedido", corte)
            r["id"] = pu["id"]
            usuario.append(r)
    return {"barras": res_barras, "criticos": criticos, "usuario": usuario, "corte": corte}
