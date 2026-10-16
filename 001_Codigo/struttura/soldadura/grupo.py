"""Grupos de cordones de filete tratados como LÍNEAS (ancho unitario) y fuerza por unidad de longitud en la garganta.

Ejes de la sección de la barra (los mismos que el pórtico 3D): x = eje de la barra (normal al plano de los cordones),
y, z = ejes locales en el plano de los cordones.  Esfuerzos (cara +x):  N, Vy, Vz, T (= Mx), My, Mz.

Propiedades del grupo como línea (Shigley (9-6) y Tablas 9-1/9-2; Compendio cap. 18 Anexo 1):
    Lw = Σ l      (área unitaria)           Iyu = ∫ z'² ds      Izu = ∫ y'² ds      Iyzu = ∫ y'z' ds      Ju = Iyu + Izu
con (y', z') medidos desde el baricentro del grupo.

Fuerza por unidad de longitud de cordón en un punto (se compone en forma vectorial, Compendio (14) y Shigley (9-4)–(9-6)):
    f_x = N/Lw + a·z' + b·y'        con  [Iyu Iyzu; Iyzu Izu]·(a, b) = (My, −Mz)    (flexión; con Iyzu = 0: My·z'/Iyu − Mz·y'/Izu)
    f_y = Vy/Lw − T·z'/Ju           (corte primario + torsión secundaria en el plano del cordón)
    f_z = Vz/Lw + T·y'/Ju
    f   = √(f_x² + f_y² + f_z²)     τ_garganta = f / (0,707·w)      (método simplificado, garganta mínima: Shigley (9-3))
"""
from __future__ import annotations

import math

import numpy as np


class ErrorSoldadura(Exception):
    """Dato o disposición de soldadura no válidos."""


_GX, _GW = np.polynomial.legendre.leggauss(5)


def _nodos_linea(y0, z0, y1, z1):
    L = math.hypot(y1 - y0, z1 - z0)
    u = (_GX + 1) / 2
    return y0 + (y1 - y0) * u, z0 + (z1 - z0) * u, L * _GW / 2


def _nodos_arco(cy, cz, R, a0, a1):
    n = max(1, int(math.ceil(abs(a1 - a0) / math.radians(10))))
    edges = np.linspace(a0, a1, n + 1)
    ys, zs, ws = [], [], []
    for k in range(n):
        t = edges[k] + (edges[k + 1] - edges[k]) * (_GX + 1) / 2
        ys.append(cy + R * np.cos(t))
        zs.append(cz + R * np.sin(t))
        ws.append(R * (edges[k + 1] - edges[k]) * _GW / 2)
    return np.concatenate(ys), np.concatenate(zs), np.concatenate(ws)


class Grupo:
    """Conjunto de segmentos (rectas y arcos) en el plano (y, z).  Longitudes en la unidad del modelo."""

    def __init__(self, segmentos, descripcion="", origen=""):
        """segmentos: [('l', y0, z0, y1, z1)] o [('a', cy, cz, R, ang0, ang1)] (ángulos en radianes desde +y hacia +z)."""
        if not segmentos:
            raise ErrorSoldadura("el grupo de cordones no tiene segmentos")
        self.segmentos = [tuple(s) for s in segmentos]
        self.descripcion = descripcion
        self.origen = origen
        self.escala_fibra = (1.0, 1.0)      # (ky, kz): pasa de la línea media a la fibra exterior (solo uniones a tope de pared delgada)
        self.contorno = []          # polilíneas [[(y, z), ...]] del contorno de la sección, solo para dibujar
        Y, Z, W = [], [], []
        for s in self.segmentos:
            y, z, w = _nodos_linea(*s[1:]) if s[0] == "l" else _nodos_arco(*s[1:])
            Y.append(y), Z.append(z), W.append(w)
        self._y, self._z, self._w = np.concatenate(Y), np.concatenate(Z), np.concatenate(W)
        self.Lw = float(self._w.sum())
        if self.Lw <= 0:
            raise ErrorSoldadura("longitud total de cordón nula")
        self.yg = float((self._w * self._y).sum() / self.Lw)
        self.zg = float((self._w * self._z).sum() / self.Lw)
        esc = max(np.abs(self._y).max(), np.abs(self._z).max())
        self.yg = 0.0 if abs(self.yg) < 1e-12 * esc else self.yg
        self.zg = 0.0 if abs(self.zg) < 1e-12 * esc else self.zg
        dy, dz = self._y - self.yg, self._z - self.zg
        self.Iyu = float((self._w * dz**2).sum())
        self.Izu = float((self._w * dy**2).sum())
        self.Iyzu = float((self._w * dy * dz).sum())
        self.Ju = self.Iyu + self.Izu
        if self.Ju <= 1e-12 * self.Lw**3:
            raise ErrorSoldadura("el grupo de cordones no resiste torsión (todos los puntos coinciden)")

    # -- puntos de evaluación ------------------------------------------------
    def puntos(self, fino=False):
        """Puntos donde se evalúa f.  En un tramo recto f es afín en la posición, por lo tanto |f| es convexa y su máximo está en los
        extremos; los arcos se muestrean cada 2° (o cada 1° para dibujar).  Devuelve lista de (y, z, segmento)."""
        pts = []
        for k, s in enumerate(self.segmentos):
            if s[0] == "l":
                n = 90 if fino else 1
                for t in np.linspace(0.0, 1.0, n + 1):
                    pts.append((s[1] + (s[3] - s[1]) * t, s[2] + (s[4] - s[2]) * t, k))
            else:
                _, cy, cz, R, a0, a1 = s
                n = max(2, int(math.ceil(abs(a1 - a0) / math.radians(0.5 if fino else 2))))
                for a in np.linspace(a0, a1, n + 1):
                    pts.append((cy + R * math.cos(a), cz + R * math.sin(a), k))
        return pts

    # -- traslado de las cargas al baricentro del grupo ------------------------
    def trasladar(self, E, punto=None):
        """E = (N, Vy, Vz, T, My, Mz) aplicados en 'punto' = (y, z) (por defecto el origen del sistema del grupo).  Devuelve los esfuerzos
        equivalentes en el baricentro del grupo (estática):  T' = T + (yp−yg)·Vz − (zp−zg)·Vy ;  My' = My + (zp−zg)·N ;  Mz' = Mz − (yp−yg)·N."""
        N, Vy, Vz, T, My, Mz = (float(v) for v in E)
        yp, zp = (0.0, 0.0) if punto is None else punto
        ry, rz = yp - self.yg, zp - self.zg
        return (N, Vy, Vz, T + ry * Vz - rz * Vy, My + rz * N, Mz - ry * N)

    # -- fuerza por unidad de longitud ----------------------------------------
    def _coef_flexion(self, My, Mz):
        M = np.array([[self.Iyu, self.Iyzu], [self.Iyzu, self.Izu]])
        rhs = np.array([My, -Mz])
        if abs(My) + abs(Mz) == 0:
            return 0.0, 0.0
        sol, *_ = np.linalg.lstsq(M, rhs, rcond=None)
        if np.linalg.norm(M @ sol - rhs) > 1e-9 * max(np.linalg.norm(rhs), 1e-300):
            raise ErrorSoldadura("el grupo de cordones no puede resistir ese momento flector (por ejemplo, un solo cordón recto no "
                                 "resiste el momento alrededor de su propio eje)")
        return float(sol[0]), float(sol[1])

    def fuerza(self, E, y, z, punto=None):
        """(fx, fy, fz) por unidad de longitud de cordón en los puntos (y, z) [arrays]; E aplicados en 'punto' (ver trasladar)."""
        N, Vy, Vz, T, My, Mz = self.trasladar(E, punto)
        a, b = self._coef_flexion(My, Mz)
        dy, dz = np.asarray(y, float) - self.yg, np.asarray(z, float) - self.zg
        fx = N / self.Lw + a * dz + b * dy
        fy = Vy / self.Lw - T * dz / self.Ju
        fz = Vz / self.Lw + T * dy / self.Ju
        return fx, fy, fz

    def evaluar(self, E, punto=None, fino=False):
        """Resultado en todos los puntos: dict con f máxima, punto crítico y las componentes."""
        pts = self.puntos(fino)
        y = np.array([p[0] for p in pts])
        z = np.array([p[1] for p in pts])
        fx, fy, fz = self.fuerza(E, y, z, punto)
        f = np.sqrt(fx**2 + fy**2 + fz**2)
        esc = max(np.abs(y).max(), np.abs(z).max(), 1e-300)
        y = np.where(np.abs(y) < 1e-9 * esc, 0.0, y)
        z = np.where(np.abs(z) < 1e-9 * esc, 0.0, z)
        i = int(np.argmax(f))
        return {"y": y, "z": z, "seg": [p[2] for p in pts], "fx": fx, "fy": fy, "fz": fz, "f": f, "i": i, "fmax": float(f[i]),
                "punto": (float(y[i]), float(z[i])), "E_bar": self.trasladar(E, punto)}


# --------------------------------------------------------------------------
# Disposiciones predefinidas  (b = medida horizontal según y;  d = medida vertical según z;  como en Shigley y el Compendio)
# --------------------------------------------------------------------------
DISPOSICIONES = {
    "circulo":      ("Tubo / barra redonda, vuelta completa", ("d",), "centro del círculo (d = diámetro del cordón, el exterior del tubo)"),
    "arco":         ("Arcos de círculo sobre tubo [propio: extensión, los libros no la traen]", ("d", "arcos"),
                     "centro del círculo; arcos = 'centro:abertura|centro:abertura' en grados (centro medido desde +y hacia +z; la abertura se reparte mitad a cada lado)"),
    "rectangulo":   ("Rectángulo, vuelta completa (4 lados)", ("b", "d"), "centro del rectángulo"),
    "costados":     ("Dos cordones verticales (solo a los costados)", ("b", "d"), "centro (cordones en y = ±b/2, largo d)"),
    "arriba_abajo": ("Dos cordones horizontales (solo arriba y abajo)", ("b", "d"), "centro (cordones en z = ±d/2, largo b)"),
    "linea":        ("Un solo cordón recto vertical", ("d",), "punto medio del cordón (a lo largo de z)"),
    "L":            ("Cordón en L: uno horizontal b + uno vertical d", ("b", "d"), "esquina de la L (+y el cordón b, +z el cordón d)"),
    "C":            ("Cordón en C: dos horizontales b + uno vertical d", ("b", "d"), "punto medio del cordón vertical (los horizontales salen hacia +y)"),
    "C_invertida":  ("Cordón en C invertida: uno horizontal b + dos verticales d", ("b", "d"), "punto medio del cordón horizontal (los verticales bajan hacia −z)"),
    "doble_t":      ("Perfil doble T: un cordón por ala (b) y dos por el alma (d)", ("b", "d"), "centro del alma"),
    "custom":       ("Segmentos propios", ("segmentos",), "origen que defina el usuario"),
}


def _arcos(texto):
    """'centro:abertura|centro:abertura' (grados) -> [(ang0, ang1)] en radianes.  Los arcos no pueden superponerse."""
    out = []
    for tr in str(texto).split("|"):
        v = tr.replace(",", ".").split(":")
        try:
            if len(v) != 2:
                raise ValueError
            c, ab = float(v[0]), float(v[1])
        except ValueError:
            raise ErrorSoldadura(f"arco mal formado '{tr.strip()}': debe ser 'centro:abertura' en grados (ej. 0:45|180:45)")
        if not 0 < ab <= 360:
            raise ErrorSoldadura(f"arco '{tr.strip()}': la abertura debe estar entre 0 y 360°")
        out.append((c - ab / 2, c + ab / 2))
    for i in range(len(out)):
        for j in range(i + 1, len(out)):
            for k in (-360, 0, 360):                       # los ángulos son periódicos
                lo, hi = max(out[i][0], out[j][0] + k), min(out[i][1], out[j][1] + k)
                if hi - lo > 1e-9:
                    raise ErrorSoldadura(f"los arcos {i + 1} y {j + 1} se superponen ({hi - lo:.4g}°)")
    return [(math.radians(a), math.radians(b)) for a, b in out]


def _circulo(d, n=120):
    return [(d / 2 * math.cos(2 * math.pi * k / n), d / 2 * math.sin(2 * math.pi * k / n)) for k in range(n + 1)]


def _rect(b, d):
    return [(-b / 2, -d / 2), (b / 2, -d / 2), (b / 2, d / 2), (-b / 2, d / 2), (-b / 2, -d / 2)]


def crear(disposicion: str, p: dict, tope: bool = False) -> Grupo:
    """Crea el grupo.  p: parámetros numéricos (b, d, ang0, ang1, ...) o 'segmentos' como texto 'y0 z0 y1 z1|y0 z0 y1 z1|...'."""
    k = disposicion.strip()
    clave = {c.lower(): c for c in DISPOSICIONES}.get(k.lower())
    if clave is None:
        raise ErrorSoldadura(f"disposición desconocida '{disposicion}'.  Válidas: {', '.join(DISPOSICIONES)}")
    nombre, req, origen = DISPOSICIONES[clave]
    faltan = [r for r in req if p.get(r) in (None, "")]
    if faltan:
        raise ErrorSoldadura(f"la disposición '{clave}' necesita {', '.join(req)} (faltan: {', '.join(faltan)})")
    if clave == "custom":
        segs = []
        for tr in str(p["segmentos"]).split("|"):
            v = tr.replace(",", ".").split()
            if len(v) != 4:
                raise ErrorSoldadura(f"segmento mal formado '{tr.strip()}': deben ser 4 números 'y0 z0 y1 z1' separados por espacio y los segmentos por '|'")
            try:
                segs.append(("l", *map(float, v)))
            except ValueError:
                raise ErrorSoldadura(f"segmento con valores no numéricos: '{tr.strip()}'")
        return Grupo(segs, nombre, origen)
    v = {r: float(p[r]) for r in req if r != "arcos"}
    esp_tope = None
    if tope and clave in ("circulo", "arco", "rectangulo", "costados", "arriba_abajo"):
        # [propio] unión a tope de pared delgada: el cordón es la línea media de la pared y la tensión se evalúa en la fibra exterior
        if p.get("esp") in (None, ""):
            raise ErrorSoldadura("la unión a tope necesita el espesor de las piezas (esp)")
        esp_tope = float(p["esp"])
        if "d" in v and (clave in ("circulo", "arco")):
            ext = (v["d"], v["d"])
            v["d"] = v["d"] - esp_tope
        elif clave in ("rectangulo", "costados", "arriba_abajo"):
            ext = (v["b"], v["d"])
            v["b"], v["d"] = v["b"] - esp_tope, v["d"] - esp_tope
        if min(v.get("b", 1e9), v["d"]) <= 0:
            raise ErrorSoldadura("el espesor es mayor que la sección")
    if any(x <= 0 for r, x in v.items() if r in ("b", "d")):
        raise ErrorSoldadura("b y d deben ser > 0")
    b, d = v.get("b"), v.get("d")
    S = []
    if clave == "circulo":
        S = [("a", 0.0, 0.0, d / 2, 0.0, 2 * math.pi)]
    elif clave == "arco":
        S = [("a", 0.0, 0.0, d / 2, a0, a1) for a0, a1 in _arcos(p["arcos"])]
    elif clave == "rectangulo":
        S = [("l", -b / 2, d / 2, b / 2, d / 2), ("l", b / 2, d / 2, b / 2, -d / 2), ("l", b / 2, -d / 2, -b / 2, -d / 2), ("l", -b / 2, -d / 2, -b / 2, d / 2)]
    elif clave == "costados":
        S = [("l", -b / 2, -d / 2, -b / 2, d / 2), ("l", b / 2, -d / 2, b / 2, d / 2)]
    elif clave == "arriba_abajo":
        S = [("l", -b / 2, d / 2, b / 2, d / 2), ("l", -b / 2, -d / 2, b / 2, -d / 2)]
    elif clave == "linea":
        S = [("l", 0.0, -d / 2, 0.0, d / 2)]
    elif clave == "L":
        S = [("l", 0.0, 0.0, b, 0.0), ("l", 0.0, 0.0, 0.0, d)]
    elif clave == "C":
        S = [("l", 0.0, -d / 2, 0.0, d / 2), ("l", 0.0, d / 2, b, d / 2), ("l", 0.0, -d / 2, b, -d / 2)]
    elif clave == "C_invertida":
        S = [("l", -b / 2, 0.0, b / 2, 0.0), ("l", -b / 2, 0.0, -b / 2, -d), ("l", b / 2, 0.0, b / 2, -d)]
    elif clave == "doble_t":
        S = [("l", -b / 2, d / 2, b / 2, d / 2), ("l", -b / 2, -d / 2, b / 2, -d / 2), ("l", 0.0, -d / 2, 0.0, d / 2), ("l", 0.0, -d / 2, 0.0, d / 2)]
    grp = Grupo(S, nombre, origen)
    if esp_tope:
        grp.escala_fibra = (ext[0] / v["b"] if "b" in v else ext[0] / v["d"], ext[1] / v["d"])
    t = float(p["esp"]) if p.get("esp") not in (None, "") else None            # espesor de pared, solo para dibujar el contorno interior
    if esp_tope:                                         # el cordón está en la línea media: el contorno son las caras de la pared
        t = None
        if clave in ("circulo", "arco"):
            grp.contorno = [_circulo(ext[0]), _circulo(ext[0] - 2 * esp_tope)]
        else:
            grp.contorno = [_rect(*ext), _rect(ext[0] - 2 * esp_tope, ext[1] - 2 * esp_tope)]
    elif clave in ("circulo", "arco"):
        grp.contorno = [_circulo(d)] + ([_circulo(d - 2 * t)] if t and t < d / 2 else [])
    elif clave in ("rectangulo", "costados", "arriba_abajo"):
        grp.contorno = [_rect(b, d)] + ([_rect(b - 2 * t, d - 2 * t)] if t and t < min(b, d) / 2 else [])
    return grp
