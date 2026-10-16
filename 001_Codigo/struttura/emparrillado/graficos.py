"""Gráficos (matplotlib) devueltos como SVG en texto, para incrustar en el informe HTML."""
from __future__ import annotations

import io
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Polygon
from matplotlib.transforms import Bbox

from .esfuerzos import elastica
from .formato import fg

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Liberation Serif", "DejaVu Serif"],
    "font.size": 9,
    "svg.fonttype": "path",
    "axes.linewidth": 0.8,
    "axes.grid": True,
    "grid.color": "#d0d0d0",
    "grid.linewidth": 0.5,
    "mathtext.fontset": "dejavuserif",
})

COL_POS, COL_POS_E = "#a9c8e8", "#1f4e79"
COL_NEG, COL_NEG_E = "#f0b8ac", "#8a2c1a"
# Colores de las tres componentes de carga (iguales en la planta y en el visor 3D)
COL_PZ, COL_MX, COL_MY = "#c0392b", "#1f5fbf", "#d68910"
_contador = [0]


def _a_svg(fig) -> str:
    _contador[0] += 1
    plt.rcParams["svg.hashsalt"] = f"emp{_contador[0]}"       # ids únicos entre SVG del mismo HTML
    buf = io.StringIO()
    fig.savefig(buf, format="svg", bbox_inches="tight")
    plt.close(fig)
    s = buf.getvalue()
    s = s[s.find("<svg"):]
    return re.sub(r'<svg([^>]*?)width="[^"]*"\s+height="[^"]*"', r'<svg\1width="100%"', s, count=1)


def _extension(modelo):
    xs = np.array([n.x for n in modelo.nodos])
    ys = np.array([n.y for n in modelo.nodos])
    dim = max(np.ptp(xs), np.ptp(ys), max(b.L for b in modelo.barras) * 0.5, 1e-9)
    return xs, ys, dim


def _base_plano(modelo, ax, etiquetas_barras=True, etiquetas_nodos=True):
    xs, ys, dim = _extension(modelo)
    for b in modelo.barras:
        ni, nj = modelo.nodos[b.i], modelo.nodos[b.j]
        ax.plot([ni.x, nj.x], [ni.y, nj.y], color="black", lw=1.6, solid_capstyle="round", zorder=2)
        if etiquetas_barras:
            ax.text((ni.x + nj.x) / 2, (ni.y + nj.y) / 2, b.id, fontsize=7, style="italic",
                    ha="center", va="center", zorder=5,
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="#888888", lw=0.5))
    ax.plot(xs, ys, "o", color="black", ms=3.5, zorder=4)
    if etiquetas_nodos:
        for n in modelo.nodos:
            ax.text(n.x + 0.018 * dim, n.y + 0.018 * dim, n.id, fontsize=8, fontweight="bold",
                    zorder=6, color="#222222")
    ax.set_aspect("equal", adjustable="datalim")
    ax.margins(0.14)
    u = modelo.config["unidad_longitud"]
    ax.set_xlabel(f"X [{u}]")
    ax.set_ylabel(f"Y [{u}]")


def _apoyos(modelo, ax, dim):
    """Apoyos (cuadrado = empotrado, triángulo = parcial) y resortes (rombo)."""
    for k, n in enumerate(modelo.nodos):
        r = modelo.restr[k]
        kk = modelo.resortes[k]
        lineas = []
        inc = [sp for sp in modelo.resortes_giro if sp["nodo"] == k]
        if kk.any() or inc:
            ax.plot(n.x, n.y, "D", ms=9, mfc="#e6e6e6", mec="black", mew=1.0, zorder=3)
            nombres = ("kz", "kφx", "kφy")
            if kk.any():
                lineas.append(", ".join(f"{nm}={fg(v, 3)}" for nm, v in zip(nombres, kk) if v > 0))
            for sp in inc:
                lineas.append(f"kφ={fg(sp['k'], 3)} eje {fg(sp['beta'], 3)}°")
                b = np.radians(sp["beta"])
                for sg in (1, -1):
                    ax.plot([n.x, n.x + sg * 0.07 * dim * np.cos(b)], [n.y, n.y + sg * 0.07 * dim * np.sin(b)],
                            color="#7d3c98", lw=1.6, zorder=3)
        if r.any():
            if r.all():
                ax.plot(n.x, n.y, "s", ms=10, mfc="#666666", mec="black", zorder=3)
                lineas.insert(0, "empotr.")
            else:
                ax.plot(n.x, n.y, "^", ms=10, mfc="white", mec="black", mew=1.2, zorder=3)
                lineas.insert(0, ",".join(nm for nm, f in zip(("uz", "φx", "φy"), r) if f))
        if lineas:
            ax.text(n.x, n.y - 0.045 * dim, "\n".join(lineas), fontsize=6.5, ha="center", va="top",
                    color="#333333")


def _cargas_tramo_plano(modelo, ax, cb, dim):
    """Dibuja en la planta las cargas en el tramo: q (banda con marcas), P (círculo) y ΔT (rótulo)."""
    for c, fac in cb:
        b = modelo.barras[c.barra]
        ni = modelo.nodos[b.i]
        nx_, ny_ = -b.g2, b.g1
        glob = lambda x, d=0.0: (ni.x + x * b.g1 + d * nx_ * dim, ni.y + x * b.g2 + d * ny_ * dim)
        if c.tipo == "q":
            q1, q2 = c.v1 * fac, c.v2 * fac
            xs = np.linspace(c.a, c.b, max(2, min(9, int((c.b - c.a) / (0.06 * dim)) + 2)))
            P0, P1 = glob(c.a, 0.03), glob(c.b, 0.03)
            ax.plot([P0[0], P1[0]], [P0[1], P1[1]], color=COL_PZ, lw=2.6, alpha=0.35, zorder=3,
                    solid_capstyle="butt")
            for x in xs:
                qx = q1 + (q2 - q1) * (x - c.a) / (c.b - c.a)
                gx, gy = glob(x, 0.03)
                if abs(qx) > 1e-12 * max(abs(q1), abs(q2), 1e-300):
                    ax.plot(gx, gy, marker="." if qx > 0 else "x", ms=5 if qx > 0 else 5.5, color=COL_PZ,
                            mew=1.2, zorder=6)
            txt = f"q={fg(q1, 3)}" if abs(q1 - q2) <= 1e-12 * max(abs(q1), 1e-300) else f"q={fg(q1, 3)}→{fg(q2, 3)}"
            gx, gy = glob((c.a + c.b) / 2, 0.075)
            ax.text(gx, gy, txt, fontsize=6.8, color=COL_PZ, ha="center", va="center", zorder=8,
                    bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.85))
        elif c.tipo == "P":
            v = c.v1 * fac
            gx, gy = glob(c.a)
            ax.plot(gx, gy, "o", ms=11, mfc="white", mec=COL_PZ, mew=1.3, zorder=7)
            ax.plot(gx, gy, marker="." if v > 0 else "x", ms=5 if v > 0 else 6, color=COL_PZ, mew=1.3, zorder=8)
            tx, ty = glob(c.a, 0.06)
            ax.text(tx, ty, f"P={fg(v, 3)}\na={fg(c.a, 3)}", fontsize=6.5, color=COL_PZ, ha="center", va="bottom",
                    zorder=8, bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.85))
        elif c.tipo == "temp":
            gx, gy = glob(b.L / 2, -0.06)
            ax.text(gx, gy, f"ΔT sup={fg(c.v1 * fac, 3)} / inf={fg(c.v2 * fac, 3)} °", fontsize=6.5, color="#7d3c98",
                    ha="center", va="top", zorder=8,
                    bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.85))


def fig_esquema(modelo, F=None, cb=None) -> str:
    """Esquema en planta: barras, nodos, apoyos y (si se pasa F / cb) las cargas nodales y en tramos.

    Colores: Pz rojo, Mx azul, My ámbar (los mismos que en el visor 3D)."""
    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    xs, ys, dim = _extension(modelo)
    _base_plano(modelo, ax)
    _apoyos(modelo, ax, dim)
    if F is not None:
        escala = max(np.abs(F).max(), 1e-300)
        for k, n in enumerate(modelo.nodos):
            pz, mx, my = F[k]
            if abs(pz) > 1e-12 * escala:
                ax.plot(n.x, n.y, "o", ms=13, mfc="white", mec=COL_PZ, mew=1.3, zorder=7)
                ax.plot(n.x, n.y, marker="." if pz > 0 else "x", ms=6 if pz > 0 else 7,
                        color=COL_PZ, mew=1.3, zorder=8)
                ax.text(n.x - 0.03 * dim, n.y - 0.03 * dim, f"Pz={fg(pz, 4)}", fontsize=7,
                        color=COL_PZ, ha="right", va="top", zorder=8)
            for val, vec, nom, col in ((mx, (1, 0), "Mx", COL_MX), (my, (0, 1), "My", COL_MY)):
                if abs(val) > 1e-12 * escala:
                    s = 1 if val > 0 else -1
                    p1 = (n.x + s * vec[0] * 0.09 * dim, n.y + s * vec[1] * 0.09 * dim)
                    ax.annotate("", xy=p1, xytext=(n.x, n.y), zorder=8,
                                arrowprops=dict(arrowstyle="-|>", color=col, lw=1.4,
                                                shrinkA=0, shrinkB=0, mutation_scale=9))
                    ax.text(p1[0] + s * vec[0] * 0.012 * dim, p1[1] + s * vec[1] * 0.012 * dim + 0.012 * dim,
                            f"{nom}={fg(val, 4)}", fontsize=7, color=col,
                            ha="left" if s * vec[0] >= 0 else "right", va="bottom", zorder=8)
    if cb:
        _cargas_tramo_plano(modelo, ax, cb, dim)
    proxies = [Line2D([], [], marker="s", ls="", mfc="#666666", mec="black", ms=7, label="apoyo (GDL restringidos rotulados)"),
               Line2D([], [], marker="^", ls="", mfc="white", mec="black", ms=7, label="apoyo parcial")]
    if modelo.res_mask.any():
        proxies.append(Line2D([], [], marker="D", ls="", mfc="#e6e6e6", mec="black", ms=6,
                              label="resorte (rigidez rotulada)"))
    if F is not None or cb:
        proxies += [Line2D([], [], marker="o", ls="", mfc="white", mec=COL_PZ, ms=8,
                           label="Pz, P, q  (punto: hacia +z, cruz: hacia −z)"),
                    Line2D([], [], color=COL_MX, lw=1.4, label="Mx (vector, mano derecha)"),
                    Line2D([], [], color=COL_MY, lw=1.4, label="My (vector, mano derecha)")]
    ax.legend(handles=proxies, loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=2,
              fontsize=7, frameon=False)
    return _a_svg(fig)


def _tramos(v0, v1, L):
    """Polígonos (en coords locales s, v) de un diagrama lineal, partido donde cambia de signo."""
    if v0 * v1 >= 0:
        return [([(0, 0), (0, v0), (L, v1), (L, 0)], 1 if (v0 + v1) >= 0 else -1)]
    s = L * v0 / (v0 - v1)
    return [([(0, 0), (0, v0), (s, 0)], 1 if v0 > 0 else -1),
            ([(s, 0), (L, v1), (L, 0)], 1 if v1 > 0 else -1)]


def _rotular(fig, ax, etiquetas, puntos):
    """Coloca rótulos evitando que se pisen entre sí y con los nodos.

    etiquetas: lista de (x, y, texto, (ux, uy), prioridad); (ux, uy) es la dirección preferida
    (en datos) hacia donde alejar el rótulo del punto.  Se prueban posiciones candidatas
    (más lejos / desplazadas a lo largo de la barra) y se elige la que menos se solapa."""
    fig.canvas.draw()                       # fija las transformaciones definitivas
    rend = fig.canvas.get_renderer()
    inv = ax.transData.inverted()
    ocupados = []
    for (px, py) in puntos:
        x, y = ax.transData.transform((px, py))
        ocupados.append(Bbox([[x - 6, y - 6], [x + 6, y + 6]]))

    def solape(b):
        s = 0.0
        for o in ocupados:
            w = min(b.x1, o.x1) - max(b.x0, o.x0)
            h = min(b.y1, o.y1) - max(b.y0, o.y0)
            if w > 0 and h > 0:
                s += w * h
        return s

    for (x, y, txt, d, _) in sorted(etiquetas, key=lambda e: -e[4]):
        p0 = np.array(ax.transData.transform((x, y)))
        p1 = np.array(ax.transData.transform((x + d[0], y + d[1])))
        dv = p1 - p0
        dv = dv / (np.linalg.norm(dv) or 1.0)
        tv = np.array([-dv[1], dv[0]])
        t = ax.text(x, y, txt, fontsize=6.8, ha="center", va="center", zorder=9,
                    bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.85))
        mejor, mejor_costo = None, None
        for r in (8, 14, 21, 29, 39):
            for s_ in (0, 1, -1, 2, -2):
                pos = p0 + dv * r + tv * s_ * 13
                t.set_position(inv.transform(pos))
                bb = t.get_window_extent(rend)
                bb = Bbox([[bb.x0 - 2, bb.y0 - 2], [bb.x1 + 2, bb.y1 + 2]])
                costo = solape(bb) + 0.05 * r + 0.02 * abs(s_) * 13
                if mejor_costo is None or costo < mejor_costo:
                    mejor, mejor_costo, mejor_bb = pos, costo, bb
            if mejor_costo < 1.0:                # ya hay una posición sin solapes: no alejar más
                break
        t.set_position(inv.transform(mejor))
        ocupados.append(mejor_bb)


def fig_diagrama(modelo, vi, vj, unidad: str, constante: bool = False, texto_signo: str = "") -> str:
    """Diagrama sobre la planta.  Ordenadas perpendiculares a la barra, hacia la izquierda de i→j
    para valores positivos.  vi, vj: valor al inicio y al final de cada barra."""
    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    xs, ys, dim = _extension(modelo)
    _base_plano(modelo, ax, etiquetas_barras=False)
    vmax = max(np.abs(vi).max(), np.abs(vj).max())
    if vmax <= 1e-12:
        ax.text(0.5, 0.5, "Esfuerzo nulo en toda la estructura", transform=ax.transAxes,
                ha="center", va="center", fontsize=10)
        return _a_svg(fig)
    esc = 0.12 * dim / vmax
    etiquetas = []
    for k, b in enumerate(modelo.barras):
        ni = modelo.nodos[b.i]
        nx_, ny_ = -b.g2, b.g1                               # normal (izquierda de i→j)

        def glob(s, v):
            return (ni.x + s * b.g1 + v * esc * nx_, ni.y + s * b.g2 + v * esc * ny_)

        for pts, sg in _tramos(vi[k], vj[k], b.L):
            ax.add_patch(Polygon([glob(s, v) for s, v in pts], closed=True,
                                 fc=COL_POS if sg > 0 else COL_NEG,
                                 ec=COL_POS_E if sg > 0 else COL_NEG_E, lw=0.9, alpha=0.9, zorder=3))
        for s, v in ([(b.L / 2, vi[k])] if constante else [(0, vi[k]), (b.L, vj[k])]):
            if abs(v) > 1e-9 * vmax:
                sg = 1 if v > 0 else -1
                px, py = glob(s, v)
                etiquetas.append((px, py, fg(v, 4), (sg * nx_, sg * ny_), abs(v)))
    _rotular(fig, ax, etiquetas, [(n.x, n.y) for n in modelo.nodos]
             + [(n.x + 0.03 * dim, n.y + 0.03 * dim) for n in modelo.nodos])    # nodo y su número
    ax.legend(handles=[Patch(fc=COL_POS, ec=COL_POS_E, label="valores positivos"),
                       Patch(fc=COL_NEG, ec=COL_NEG_E, label="valores negativos")],
              loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=2, fontsize=7.5, frameon=False)
    ax.text(0.99, 0.01, f"[{unidad}]   {texto_signo}", transform=ax.transAxes, fontsize=7,
            ha="right", va="bottom", color="#333333")
    return _a_svg(fig)


def _partes(x, v):
    """Parte una curva (x, v) donde cambia de signo.  Devuelve [(xs, vs, signo)]."""
    partes, xs, vs = [], [x[0]], [v[0]]
    for i in range(1, len(x)):
        if vs[-1] * v[i] < 0:
            t = vs[-1] / (vs[-1] - v[i])
            xc = xs[-1] + t * (x[i] - xs[-1])
            xs.append(xc)
            vs.append(0.0)
            partes.append((xs, vs))
            xs, vs = [xc], [0.0]
        xs.append(x[i])
        vs.append(v[i])
    partes.append((xs, vs))
    out = []
    for px, pv in partes:
        sm = sum(pv)
        out.append((px, pv, 1 if sm >= 0 else -1))
    return out


def _puntos_a_rotular(x, v, L):
    """Abscisas donde se rotula el valor: extremos, extremos interiores y saltos (fuerzas puntuales)."""
    idx = {0, len(x) - 1}
    n = len(x)
    if np.ptp(v) < 1e-9 * max(np.abs(v).max(), 1e-300):        # constante: un solo rótulo al medio
        return [n // 2]
    for i in range(1, n - 1):
        if x[i] == x[i + 1] or x[i] == x[i - 1]:                # salto
            idx.add(i)
        elif (v[i] - v[i - 1]) * (v[i + 1] - v[i]) < 0:         # máximo / mínimo local
            idx.add(i)
    idx = sorted(idx)
    if len(idx) > 6:                                            # demasiados: dejar los mayores
        idx = sorted(sorted(idx, key=lambda i: -abs(v[i]))[:6])
    return idx


def fig_diagrama_curvas(modelo, series, unidad: str, texto_signo: str = "", escala: str = "barra") -> str:
    """Diagrama sobre la planta con curvas x-v por barra (admite cargas en el tramo).

    series[k] = (x, v): abscisa local desde el nodo i y valor.  Ordenadas perpendiculares a la barra,
    hacia la izquierda de i→j para valores positivos.

    escala = "barra": cada barra se dibuja normalizada a SU máximo (se ve la forma aunque los valores sean
    chicos frente a otras barras; los números rotulados son los reales).  escala = "global": una sola escala
    para toda la estructura.  Las barras con valores despreciables (< 1e-6 del máximo global) no se dibujan."""
    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    xs, ys, dim = _extension(modelo)
    _base_plano(modelo, ax, etiquetas_barras=False)
    vmax = max(np.abs(v).max() for _, v in series)
    if vmax <= 1e-12:
        ax.text(0.5, 0.5, "Esfuerzo nulo en toda la estructura", transform=ax.transAxes,
                ha="center", va="center", fontsize=10)
        return _a_svg(fig)
    etiquetas = []
    for k, b in enumerate(modelo.barras):
        ni = modelo.nodos[b.i]
        nx_, ny_ = -b.g2, b.g1
        x, v = np.asarray(series[k][0]), np.asarray(series[k][1])
        vk = np.abs(v).max()
        if vk <= 1e-6 * vmax:
            continue
        esc = 0.12 * dim / (vk if escala == "barra" else vmax)

        def glob(sx, sv):
            return (ni.x + sx * b.g1 + sv * esc * nx_, ni.y + sx * b.g2 + sv * esc * ny_)

        for px, pv, sg in _partes(x, v):
            pts = [glob(px[0], 0.0)] + [glob(a, c) for a, c in zip(px, pv)] + [glob(px[-1], 0.0)]
            ax.add_patch(Polygon(pts, closed=True, fc=COL_POS if sg > 0 else COL_NEG,
                                 ec=COL_POS_E if sg > 0 else COL_NEG_E, lw=0.9, alpha=0.9, zorder=3))
        for i in _puntos_a_rotular(x, v, b.L):
            if abs(v[i]) > 1e-9 * vmax:
                sg = 1 if v[i] > 0 else -1
                px, py = glob(x[i], v[i])
                etiquetas.append((px, py, fg(v[i], 4), (sg * nx_, sg * ny_), abs(v[i])))
    _rotular(fig, ax, etiquetas, [(n.x, n.y) for n in modelo.nodos]
             + [(n.x + 0.03 * dim, n.y + 0.03 * dim) for n in modelo.nodos])
    ax.legend(handles=[Patch(fc=COL_POS, ec=COL_POS_E, label="valores positivos"),
                       Patch(fc=COL_NEG, ec=COL_NEG_E, label="valores negativos")],
              loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=2, fontsize=7.5, frameon=False)
    nota = "cada barra a su propia escala; valores rotulados = reales" if escala == "barra" else "escala única"
    ax.text(0.99, 0.01, f"[{unidad}]   {texto_signo}   ({nota})", transform=ax.transAxes, fontsize=7,
            ha="right", va="bottom", color="#333333")
    return _a_svg(fig)


def escala_auto(modelo, res) -> float:
    """Factor de amplificación de la deformada: el máximo desplazamiento se ve ~12 % de la luz."""
    xs, ys, dim = _extension(modelo)
    wmax = np.abs(res.u[:, 0]).max()
    if wmax <= 0:
        return 1.0
    return float(f"{0.12 * dim / wmax:.1g}")


def fig_deformada(modelo, res, escala: float | None = None) -> tuple[str, float]:
    """Estructura deformada en 3D (uz amplificado).  Devuelve (svg, escala_usada)."""
    esc = escala if escala else escala_auto(modelo, res)
    curvas = elastica(modelo, res, n=31)
    xs, ys, dim = _extension(modelo)
    fig = plt.figure(figsize=(7.4, 5.6))
    ax = fig.add_subplot(projection="3d")
    ax.grid(True)
    for eje in (ax.xaxis, ax.yaxis, ax.zaxis):
        eje.pane.set_facecolor("white")
        eje.pane.set_edgecolor("#bbbbbb")
    for X, Y, W in curvas:                                    # indeformada
        ax.plot(X, Y, np.zeros_like(W), color="#888888", lw=1.0, ls="--", zorder=1)
    for X, Y, W in curvas:                                    # deformada
        ax.plot(X, Y, W * esc, color="black", lw=2.0, zorder=3)
    w_nodal = res.u[:, 0]
    ax.scatter(xs, ys, np.zeros(len(xs)), s=8, color="#666666", zorder=2)
    ax.scatter(xs, ys, w_nodal * esc, s=14, color="black", zorder=4)
    for k, n in enumerate(modelo.nodos):                      # guías verticales
        ax.plot([n.x, n.x], [n.y, n.y], [0, w_nodal[k] * esc], color="#999999", lw=0.6, ls=":")
    # apoyos (marcas en z = 0)
    for k, n in enumerate(modelo.nodos):
        if modelo.restr[k, 0]:
            ax.scatter([n.x], [n.y], [0], marker="^", s=45, facecolor="white", edgecolor="black",
                       linewidth=1.1, zorder=5, depthshade=False)
    # etiquetas de valor real de uz en los nodos más desplazados
    orden = np.argsort(-np.abs(w_nodal))
    nlab = len(w_nodal) if len(w_nodal) <= 12 else 8
    for k in orden[:nlab]:
        if abs(w_nodal[k]) > 1e-9 * max(np.abs(w_nodal).max(), 1e-300):
            n = modelo.nodos[k]
            ax.text(n.x, n.y, w_nodal[k] * esc, f"{fg(w_nodal[k], 3)}", fontsize=8,
                    ha="center", va="bottom" if w_nodal[k] >= 0 else "top", zorder=10,
                    bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.8))
    dx, dy = max(np.ptp(xs), 0.2 * dim), max(np.ptp(ys), 0.2 * dim)
    zmin, zmax = min(0.0, w_nodal.min() * esc), max(0.0, w_nodal.max() * esc)
    dz = max((zmax - zmin) * 1.5, 0.30 * max(dx, dy))
    zc = (zmin + zmax) / 2
    ax.set_xlim(xs.min() - 0.05 * dx, xs.max() + 0.05 * dx)
    ax.set_ylim(ys.min() - 0.05 * dy, ys.max() + 0.05 * dy)
    ax.set_zlim(zc - dz / 2, zc + dz / 2)
    ax.set_box_aspect((dx, dy, dz))
    ax.set_zticks([])
    ax.set_xlabel(f"X [{modelo.config['unidad_longitud']}]")
    ax.set_ylabel(f"Y [{modelo.config['unidad_longitud']}]")
    ax.view_init(elev=27, azim=-62)
    ax.legend(handles=[Line2D([], [], color="#888888", ls="--", lw=1, label="indeformada"),
                       Line2D([], [], color="black", lw=2, label=f"deformada (uz × {esc:g})"),
                       Line2D([], [], color="none", label=f"cifras: uz real [{modelo.config['unidad_longitud']}]")],
              loc="upper left", fontsize=7.5, frameon=False)
    return _a_svg(fig), esc
