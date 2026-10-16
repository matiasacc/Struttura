"""Propiedades de secciones transversales.

Convención: la flexión de las barras se da alrededor del eje horizontal
perpendicular a la barra (eje local yl), porque las cargas son verticales
(perpendiculares al plano del emparrillado).  Por eso, en las secciones
rectangulares, ``h`` es la dimensión VERTICAL (en z) y ``b`` la horizontal.

Cada sección entrega:
    I   inercia a flexión respecto del eje horizontal
    J   constante de torsión (St. Venant)
    A   área
    c   distancia del eje neutro a la fibra extrema (para sigma = M*c/I)
    Wt  módulo resistente a torsión (tau_max = T/Wt)
    kv  factor de corte:  tau_max por corte vertical = kv * V / A
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass
class Seccion:
    id: str
    tipo: str
    descripcion: str
    I: float
    J: float
    A: float | None = None
    c: float | None = None
    Wt: float | None = None
    kv: float | None = None
    h: float | None = None      # altura de la sección (para gradientes térmicos)
    pared: object = None        # ParedDelgada (perfiles abiertos de pared delgada), si corresponde
    dim: dict = field(default_factory=dict)    # d, t, b, h, tf, tw según el tipo (el motor de tensiones del 3D los usa)


def _req(p: dict, *nombres):
    faltan = [n for n in nombres if p.get(n) is None]
    if faltan:
        raise ValueError(f"faltan los parámetros {', '.join(faltan)}")
    return [p[n] for n in nombres]


PERFILES_PARED = ("canal", "doble_t", "te", "z", "angular")


def crear_seccion(id_: str, tipo: str, p: dict) -> Seccion:
    """Crea una sección a partir de su tipo y parámetros (dict nombre -> valor|None)."""
    s = _crear_seccion(id_, tipo, p)
    if not s.dim:
        s.dim = {k: p[k] for k in ("d", "t", "b", "h", "tf", "tw") if p.get(k) is not None}
    return s


def _crear_seccion(id_: str, tipo: str, p: dict) -> Seccion:
    tipo = tipo.strip().lower()

    if tipo in PERFILES_PARED:
        # Perfil abierto de pared delgada (dimensiones de línea media): mismo método que el pórtico 3D (Gere cap. 6.7–6.9, Compendio cap. 10).
        # La flexión se da alrededor del eje principal fuerte y (h en el plano de la flexión), como en las demás secciones de este programa.
        from ..portico3d.pared_delgada import ParedDelgada, perfil
        dims = {c: p.get(c) for c in ("h", "b", "t", "tf", "tw")}
        pd = ParedDelgada(perfil(tipo, dims))
        nombre = {"canal": "Canal (U)", "doble_t": "Doble T", "te": "Té", "z": "Z", "angular": "Ángulo (L)"}[tipo]
        dd = ", ".join(f"{c}={x:g}" for c, x in dims.items() if x is not None)
        zs = [pd.P[:, 1], pd.P[:, 3]]
        alto = float(max(a.max() for a in zs) - min(a.min() for a in zs))
        return Seccion(id_, tipo, f"{nombre} de pared delgada abierta ({dd}, línea media)", pd.Iy, pd.J, pd.A, pd.cz, pd.Wt, None, h=alto,
                       pared=pd, dim={k: x for k, x in dims.items() if x is not None})

    if tipo == "tubo":
        d, t = _req(p, "d", "t")
        if not (d > 0 and 0 < t < d / 2):
            raise ValueError("un tubo requiere d > 0 y 0 < t < d/2")
        ro, ri = d / 2, d / 2 - t
        I = math.pi / 64 * (d**4 - (d - 2 * t) ** 4)
        A = math.pi * (ro**2 - ri**2)
        J = 2 * I
        kv = 4 / 3 * (ro**2 + ro * ri + ri**2) / (ro**2 + ri**2)
        return Seccion(id_, tipo, f"Tubo circular Ø{d:g} × {t:g}", I, J, A, ro, J / ro, kv, h=d)

    if tipo == "circular":
        (d,) = _req(p, "d")
        if d <= 0:
            raise ValueError("requiere d > 0")
        I = math.pi * d**4 / 64
        J = 2 * I
        A = math.pi * d**2 / 4
        return Seccion(id_, tipo, f"Maciza circular Ø{d:g}", I, J, A, d / 2, J / (d / 2), 4 / 3, h=d)

    if tipo == "rectangular":
        b, h = _req(p, "b", "h")
        if b <= 0 or h <= 0:
            raise ValueError("requiere b > 0 y h > 0")
        I = b * h**3 / 12
        A = b * h
        a_, s_ = max(b, h), min(b, h)          # lado mayor / lado menor
        r = s_ / a_
        J = a_ * s_**3 * (1 / 3 - 0.21 * r * (1 - r**4 / 12))
        f = 1 + 0.6095 * r + 0.8865 * r**2 - 1.8023 * r**3 + 0.9100 * r**4
        Wt = a_ * s_**2 / (3 * f)               # tau_max = 3T f /(a s^2)
        return Seccion(id_, tipo, f"Maciza rectangular b={b:g} × h={h:g} (h vertical)",
                       I, J, A, h / 2, Wt, 1.5, h=h)

    if tipo == "rect_hueca":
        b, h, t = _req(p, "b", "h", "t")
        if not (b > 0 and h > 0 and 0 < t < min(b, h) / 2):
            raise ValueError("requiere b, h > 0 y 0 < t < min(b,h)/2")
        bi, hi = b - 2 * t, h - 2 * t
        I = (b * h**3 - bi * hi**3) / 12
        A = b * h - bi * hi
        bm, hm = b - t, h - t                    # línea media
        Am = bm * hm
        J = 4 * Am**2 * t / (2 * (bm + hm))      # Bredt
        Wt = 2 * Am * t
        Q = b * h**2 / 8 - bi * hi**2 / 8        # momento estático de media sección
        kv = A * Q / (I * 2 * t)                 # tau = V*Q/(I*2t) = kv*V/A
        return Seccion(id_, tipo, f"Tubo rectangular b={b:g} × h={h:g} × t={t:g} (h vertical)",
                       I, J, A, h / 2, Wt, kv, h=h)

    if tipo == "generica":
        I, J = _req(p, "I", "J")
        if I <= 0 or J <= 0:
            raise ValueError("requiere I > 0 y J > 0")
        h = p.get("h")
        if h is None and p.get("c") is not None:
            h = 2 * p["c"]                       # sección simétrica: altura = 2·c
        return Seccion(id_, tipo, "Sección genérica (datos cargados)", I, J,
                       p.get("A"), p.get("c"), p.get("Wt"), p.get("kv"), h=h)

    raise ValueError(f"tipo de sección desconocido: '{tipo}' "
                     "(tipos válidos: tubo, circular, rectangular, rect_hueca, canal, doble_t, te, z, angular, generica)")
