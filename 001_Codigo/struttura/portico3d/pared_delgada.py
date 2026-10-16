"""Secciones abiertas de pared delgada (canal, doble T, T, ángulo, Z): propiedades, centro de corte y tensiones.

Método (clásico, Gere & Goodno 7ª ed., cap. 6.7–6.9; Compendio de Cálculo Estructural II, cap. 10):
  - La sección es un árbol de segmentos rectos de espesor t, medidos sobre la línea media (dimensiones "de línea media").
  - Propiedades: A = Σ t·l ; momentos de área con la línea media (se desprecian los t³ propios, como en Gere (6-62)).
    Si el producto de inercia no es nulo (ángulo, Z) se giran los ejes a los principales (los ejes y,z locales del programa).
  - Corte de flexión (Jourawski, Gere (6-45)):  τ = V·Q / (I·t),  Q = momento estático, respecto del baricentro, de la parte de
    la sección que queda al otro lado del punto (el flujo q = τ·t sigue la línea media).  El signo se fija exigiendo que la
    resultante del flujo sea +V (equilibrio).
  - Centro de corte: la resultante del flujo de corte de Vz = 1 (Vy = 1) debe dar el momento respecto del baricentro  ys·Vz  (−zs·Vy).
    Validado contra Gere (6-65) (canal) y contra los casos particulares (ángulo y Té: en la unión de las líneas medias; Z y doble T:
    en el baricentro).
  - Torsión de Saint-Venant de pared delgada abierta:  J = Σ l·t³/3 ,  τ = T·t/J  (Compendio cap. 10, Anexo caso 7).
  - [propio] Equilibrio de torsión: el momento total de las tensiones respecto del baricentro debe ser T (el del solver), por lo
    tanto  T_SV = T − (ys·Vz − zs·Vy):  el corte aplicado en el eje baricéntrico, sin pasar por el centro de corte, se resta del
    momento que tuerce la sección.  Se desprecia el alabeo impedido (torsión no uniforme).
  - [propio] Se suman en módulo el corte de flexión y el de torsión (ambos tangentes a la línea media): envolvente conservadora
    en la superficie de la chapa.
"""
from __future__ import annotations

import math

import numpy as np


def perfil(tipo: str, p: dict):
    """Segmentos [(y0, z0, y1, z1, t)] de la línea media.  Dimensiones: h, b, tf, tw, t (de línea media)."""
    h, b = p.get("h"), p.get("b")
    tf, tw, t = p.get("tf"), p.get("tw"), p.get("t")
    if tipo in ("canal", "doble_t", "z", "te"):
        if tf is None:
            tf = t
        if tw is None:
            tw = t
        if None in (h, b, tf, tw):
            raise ValueError(f"'{tipo}' necesita h, b, tf y tw (o t si tf = tw)")
    if tipo == "canal":      # alma en y = 0, alas hacia +y
        return [(0, h / 2, b, h / 2, tf), (0, h / 2, 0, -h / 2, tw), (0, -h / 2, b, -h / 2, tf)]
    if tipo == "doble_t":
        return [(-b / 2, h / 2, 0, h / 2, tf), (0, h / 2, b / 2, h / 2, tf), (0, h / 2, 0, -h / 2, tw),
                (-b / 2, -h / 2, 0, -h / 2, tf), (0, -h / 2, b / 2, -h / 2, tf)]   # alas partidas en la unión con el alma
    if tipo == "te":         # ala arriba (z = 0), alma hacia −z de longitud h (línea media)
        return [(-b / 2, 0, 0, 0, tf), (0, 0, b / 2, 0, tf), (0, 0, 0, -h, tw)]
    if tipo == "z":          # alas iguales, alma vertical
        return [(0, h / 2, b, h / 2, tf), (0, h / 2, 0, -h / 2, tw), (-b, -h / 2, 0, -h / 2, tf)]
    if tipo == "angular":    # patas b (hacia +y) y h (hacia +z) con espesor t
        if None in (b, h, t):
            raise ValueError("'angular' necesita b, h y t")
        return [(0, 0, b, 0, t), (0, 0, 0, h, t)]
    raise ValueError(f"perfil de pared delgada desconocido '{tipo}'")


class ParedDelgada:
    """Sección abierta de pared delgada ya referida al baricentro y a los ejes principales."""

    def __init__(self, segmentos):
        seg = np.array(segmentos, float)
        if seg.ndim != 2 or seg.shape[1] != 5 or len(seg) == 0:
            raise ValueError("segmentos mal formados")
        if (seg[:, 4] <= 0).any():
            raise ValueError("los espesores deben ser > 0")
        L = np.hypot(seg[:, 2] - seg[:, 0], seg[:, 3] - seg[:, 1])
        if (L <= 0).any():
            raise ValueError("hay segmentos de longitud cero")
        self.t = seg[:, 4].copy()
        self.l = L
        self.A = float((self.t * L).sum())
        # baricentro (línea media)
        ym, zm = (seg[:, 0] + seg[:, 2]) / 2, (seg[:, 1] + seg[:, 3]) / 2
        yc, zc = float((self.t * L * ym).sum() / self.A), float((self.t * L * zm).sum() / self.A)
        P = np.stack([seg[:, 0] - yc, seg[:, 1] - zc, seg[:, 2] - yc, seg[:, 3] - zc], axis=1)
        Iy, Iz, Iyz = self._inercias(P)
        # ejes principales
        self.theta = 0.5 * math.atan2(-2 * Iyz, Iy - Iz) if abs(Iyz) > 1e-12 * max(Iy, Iz) else 0.0
        c, s = math.cos(self.theta), math.sin(self.theta)
        y0, z0, y1, z1 = P.T
        self.P = np.stack([y0 * c + z0 * s, -y0 * s + z0 * c, y1 * c + z1 * s, -y1 * s + z1 * c], axis=1)
        self.Iy, self.Iz, Iyz2 = self._inercias(self.P)
        if abs(Iyz2) > 1e-9 * max(self.Iy, self.Iz):
            raise ValueError("no se pudo llevar la sección a ejes principales")
        self.J = float((self.t**3 * L).sum() / 3)
        self.cy = float(np.abs(self.P[:, [0, 2]]).max())
        self.cz = float(np.abs(self.P[:, [1, 3]]).max())
        self.Wt = self.J / float(self.t.max())
        self._arbol()
        self._flujos_unitarios()

    # -- propiedades -------------------------------------------------------
    def _inercias(self, P):
        y0, z0, y1, z1 = P.T
        w = self.t * self.l
        Iy = float((w * (z0**2 + z0 * z1 + z1**2) / 3).sum())          # ∫ z² dA
        Iz = float((w * (y0**2 + y0 * y1 + y1**2) / 3).sum())          # ∫ y² dA
        Iyz = float((w * (2 * y0 * z0 + y0 * z1 + y1 * z0 + 2 * y1 * z1) / 6).sum())
        return Iy, Iz, Iyz

    # -- árbol y momentos estáticos ---------------------------------------
    def _arbol(self):
        """Orienta cada segmento de la raíz hacia la hoja: self.dir[k] = ±1 (+1: de (y0,z0) a (y1,z1)) y calcula el estático
        de la parte que queda más allá (hoja) en el extremo lejano: self.Qfar[k] = (Qy, Qz) = (∫y t ds, ∫z t ds)."""
        P = self.P
        nodos = []

        def nid(y, z):
            for i, (a, b) in enumerate(nodos):
                if math.hypot(a - y, b - z) < 1e-9 * max(self.cy, self.cz, 1.0):
                    return i
            nodos.append((y, z))
            return len(nodos) - 1

        ext = [(nid(P[k, 0], P[k, 1]), nid(P[k, 2], P[k, 3])) for k in range(len(P))]
        if len(nodos) != len(P) + 1:
            raise ValueError("la sección debe ser un árbol de segmentos (abierta y conexa)")
        ady = {i: [] for i in range(len(nodos))}
        for k, (a, b) in enumerate(ext):
            ady[a].append(k)
            ady[b].append(k)
        raiz = max(ady, key=lambda i: len(ady[i]))                     # nodo de mayor grado (unión)
        self._orientar(raiz, ext, ady)

    def _estatico_seg(self, k):
        y0, z0, y1, z1 = self.P[k]
        w = self.t[k] * self.l[k]
        return np.array([w * (y0 + y1) / 2, w * (z0 + z1) / 2])

    def _orientar(self, raiz, ext, ady):
        n = len(self.P)
        self.dir = np.zeros(n)
        hijos = {k: [] for k in range(n)}
        lejos = {}
        pila = [(raiz, None)]
        orden = []
        while pila:
            nodo, padre = pila.pop()
            for k in ady[nodo]:
                if k == padre:
                    continue
                a, b = ext[k]
                self.dir[k] = 1.0 if a == nodo else -1.0
                lejos[k] = b if a == nodo else a
                if padre is not None:
                    hijos[padre].append(k)
                orden.append(k)
                pila.append((lejos[k], k))
        sub = {}
        for k in reversed(orden):                                # hojas primero
            sub[k] = self._estatico_seg(k) + sum((sub[h] for h in hijos[k]), np.zeros(2))
        self.Qfar = np.array([sub[k] - self._estatico_seg(k) for k in range(n)])
        self.sub = sub

    # -- flujo de corte ----------------------------------------------------
    def _Q_en(self, k, u):
        """Estático (Qy, Qz) de lo que queda más allá del punto situado a la fracción u (0..1) de la línea media del segmento k,
        medida desde el extremo cercano a la raíz."""
        y0, z0, y1, z1 = self.P[k]
        if self.dir[k] < 0:
            y0, z0, y1, z1 = y1, z1, y0, z0
        # tramo [u, 1] del segmento (desde el extremo cercano a la raíz hacia la hoja)
        w = self.t[k] * self.l[k] * (1 - u)
        ym = y0 + (y1 - y0) * (1 + u) / 2
        zm = z0 + (z1 - z0) * (1 + u) / 2
        return self.Qfar[k] + np.array([w * ym, w * zm])

    def _tangente(self, k):
        """Vector unitario hoja → raíz."""
        y0, z0, y1, z1 = self.P[k]
        d = np.array([y1 - y0, z1 - z0]) / self.l[k]
        return -self.dir[k] * d

    def _flujos_unitarios(self):
        """Calibra el signo del flujo (q = c·V·Q/I con tangente hoja→raíz) y calcula el centro de corte (ys, zs)."""
        n = len(self.P)
        gx, gw = np.polynomial.legendre.leggauss(3)                  # Gauss de 3 puntos: exacto para integrandos de grado ≤ 5 (aquí ≤ 3)
        us, pesos = (gx + 1) / 2, gw / 2
        Ry = Rz = 0.0
        Mz = My = 0.0        # momentos respecto del baricentro de los flujos de Vz=1 y de Vy=1 (con c = +1)
        for k in range(n):
            tg = self._tangente(k)
            for u, wu in zip(us, pesos):
                ds = self.l[k] * wu
                Qy, Qz = self._Q_en(k, u)
                qz = Qz / self.Iy                  # flujo por Vz = 1 (c = +1)
                qy = Qy / self.Iz                  # flujo por Vy = 1
                # posición del punto
                y0, z0, y1, z1 = self.P[k]
                if self.dir[k] < 0:
                    y0, z0, y1, z1 = y1, z1, y0, z0
                py, pz = y0 + (y1 - y0) * u, z0 + (z1 - z0) * u
                Rz += qz * tg[1] * ds
                Ry += qy * tg[0] * ds
                Mz += qz * (py * tg[1] - pz * tg[0]) * ds
                My += qy * (py * tg[1] - pz * tg[0]) * ds
        # el flujo de Vz debe dar una resultante +1 en z; el de Vy, +1 en y
        self.cz_signo = 1.0 if Rz > 0 else -1.0
        self.cy_signo = 1.0 if Ry > 0 else -1.0
        self.chequeo_resultante = (abs(Ry), abs(Rz))              # deben ser 1 (verificación del equilibrio)
        # Torque de la resultante: ys·Vz − zs·Vy  =  Mz·c_z (Vz=1)  y  My·c_y (Vy=1)
        self.ys = self.cz_signo * Mz
        self.zs = -self.cy_signo * My

    # -- evaluación --------------------------------------------------------
    def _ubicar(self, y, z):
        """Segmento más cercano y fracción u (desde el extremo cercano a la raíz) para cada punto (arrays 1-D)."""
        y = np.asarray(y, float)
        z = np.asarray(z, float)
        mejor = np.full(y.shape, np.inf)
        ks = np.zeros(y.shape, int)
        us = np.zeros(y.shape)
        for k in range(len(self.P)):
            y0, z0, y1, z1 = self.P[k]
            if self.dir[k] < 0:
                y0, z0, y1, z1 = y1, z1, y0, z0
            dy, dz = y1 - y0, z1 - z0
            u = np.clip(((y - y0) * dy + (z - z0) * dz) / (dy * dy + dz * dz), 0.0, 1.0)
            d = np.hypot(y - (y0 + u * dy), z - (z0 + u * dz))
            m = d < mejor - 1e-12
            mejor = np.where(m, d, mejor)
            ks = np.where(m, k, ks)
            us = np.where(m, u, us)
        return ks, us

    def tensiones(self, y, z, Vy, Vz, T):
        """(τxy, τxz) en los puntos (y,z) (arrays (1,p)) para esfuerzos Vy, Vz, T (arrays (m,1)).  Devuelve arrays (m,p)."""
        y1d, z1d = np.ravel(y), np.ravel(z)
        ks, us = self._ubicar(y1d, z1d)
        Qy = np.zeros(len(ks))
        Qz = np.zeros(len(ks))
        tg = np.zeros((len(ks), 2))
        tk = np.zeros(len(ks))
        for i, (k, u) in enumerate(zip(ks, us)):
            Qy[i], Qz[i] = self._Q_en(k, u)
            tg[i] = self._tangente(k)
            tk[i] = self.t[k]
        # flujo (fuerza/longitud) a lo largo de la tangente hoja→raíz
        q = Vy * self.cy_signo * Qy[None, :] / self.Iz + Vz * self.cz_signo * Qz[None, :] / self.Iy
        tf = q / tk[None, :]
        Tsv = T - (self.ys * Vz - self.zs * Vy)
        tt = np.abs(Tsv) * tk[None, :] / self.J
        mod = tf + np.where(tf >= 0, 1.0, -1.0) * tt                  # suma en módulo (envolvente)
        return mod * tg[None, :, 0], mod * tg[None, :, 1]

    def puntos(self, us=(0.01, 0.25, 0.5, 0.75, 0.99)):
        """Puntos candidatos sobre la línea media: (y, z, rótulo)."""
        pts = []
        for k in range(len(self.P)):
            y0, z0, y1, z1 = self.P[k]
            if self.dir[k] < 0:
                y0, z0, y1, z1 = y1, z1, y0, z0
            for u in us:
                pts.append((y0 + (y1 - y0) * u, z0 + (z1 - z0) * u, f"tramo {k + 1} ({100 * u:.0f} %)"))
        return pts

    def centro_corte(self):
        """(ys, zs) del centro de corte respecto del baricentro, en los ejes principales."""
        return self.ys, self.zs

    def segmentos(self):
        """Segmentos [(y0, z0, y1, z1, t)] en ejes principales (para dibujar)."""
        return [(*self.P[k], self.t[k]) for k in range(len(self.P))]
