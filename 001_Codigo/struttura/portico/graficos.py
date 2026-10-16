"""Gráficos (matplotlib) del pórtico plano, devueltos como SVG en texto para incrustar en el informe HTML.

Se dibuja en el plano X–Y (X a la derecha, Y hacia arriba).  Colores de las cargas (iguales en el visor 2D):
Px azul, Py rojo, M ámbar."""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Polygon

from struttura.emparrillado.formato import fg
from struttura.emparrillado.graficos import (COL_NEG, COL_NEG_E, COL_POS, COL_POS_E, _a_svg, _extension, _partes,
                                   _puntos_a_rotular, _rotular)

from .esfuerzos import elastica

COL_PX, COL_PY, COL_M = "#1f5fbf", "#c0392b", "#d68910"
COL_TEMP = "#7d3c98"


# ------------------------------------------------------------------ base
def _base(modelo, ax, etiquetas_barras=True, etiquetas_nodos=True, gris=False):
    xs, ys, dim = _extension(modelo)
    col = "#9a9a9a" if gris else "black"
    for b in modelo.barras:
        ni, nj = modelo.nodos[b.i], modelo.nodos[b.j]
        ax.plot([ni.x, nj.x], [ni.y, nj.y], color=col, lw=1.6, solid_capstyle="round", zorder=2)
        if etiquetas_barras:
            ax.text((ni.x + nj.x) / 2, (ni.y + nj.y) / 2, b.id, fontsize=7, style="italic", ha="center",
                    va="center", zorder=5, bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="#888888", lw=0.5))
        for art, s, nd in ((b.art_i and not hasattr(modelo, 'ret_pandeo'), 0.05, ni), (b.art_j and not hasattr(modelo, 'ret_pandeo'), 0.95, nj)):
            if art:
                ax.plot(ni.x + s * (nj.x - ni.x), ni.y + s * (nj.y - ni.y), "o", ms=5.5, mfc="white", mec="black",
                        mew=1.1, zorder=6)
    ax.plot(xs, ys, "o", color=col, ms=3.5, zorder=4)
    if etiquetas_nodos:
        for n in modelo.nodos:
            ax.text(n.x + 0.018 * dim, n.y + 0.018 * dim, n.id, fontsize=8, fontweight="bold", zorder=6, color="#222222")
    ax.set_aspect("equal", adjustable="datalim")
    ax.margins(0.14)
    u = modelo.config["unidad_longitud"]
    ax.set_xlabel(f"X [{u}]")
    ax.set_ylabel(f"Y [{u}]")


COL_RES = "#0b7a6b"        # resortes (verde azulado): no son barras


def _resorte(ax, n, ang, dim, rotulo, largo=0.10):
    """Resorte lineal (zigzag) desde el nodo hasta un empotramiento rayado; ang = dirección (°) desde el nodo hacia el
    empotramiento, en ejes globales."""
    u = np.array([np.cos(np.radians(ang)), np.sin(np.radians(ang))])
    nv = np.array([-u[1], u[0]])
    L = largo * dim
    p0 = np.array([n.x, n.y])
    lead, nz = 0.16 * L, 7
    pts = [p0, p0 + u * lead]
    for i in range(nz):
        t = lead + (L - 2 * lead) * (i + 0.5) / nz
        pts.append(p0 + u * t + nv * (0.014 * dim) * (1 if i % 2 == 0 else -1))
    pts += [p0 + u * (L - lead), p0 + u * L]
    P = np.array(pts)
    ax.plot(P[:, 0], P[:, 1], color=COL_RES, lw=1.4, zorder=3, solid_joinstyle="round")
    f = p0 + u * L
    w = 0.022 * dim
    ax.plot(*zip(f + nv * w, f - nv * w), color=COL_RES, lw=1.6, zorder=3)
    for j in range(-2, 3):
        q = f + nv * w * j / 2
        ax.plot(*zip(q, q + u * 0.008 * dim + nv * 0.005 * dim), color=COL_RES, lw=0.8, zorder=3)
    m = p0 + u * L * 0.55 + nv * 0.03 * dim
    ax.text(m[0], m[1], rotulo, fontsize=6.3, color=COL_RES, ha="center", va="center", zorder=4,
            bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.85))


def _resorte_torsional(ax, n, dim, rotulo):
    """Resorte torsional: espiral alrededor del nodo con su anclaje rayado."""
    t = np.linspace(0, 4.5 * np.pi, 80)
    r = (0.008 + 0.028 * t / t[-1]) * dim
    x, y = n.x + r * np.cos(t), n.y + r * np.sin(t)
    ax.plot(x, y, color=COL_RES, lw=1.4, zorder=3)
    a = 0.03 * dim
    ax.plot([x[-1], x[-1] + a], [y[-1], y[-1]], color=COL_RES, lw=1.4, zorder=3)
    ax.plot([x[-1] + a] * 2, [y[-1] - 0.015 * dim, y[-1] + 0.015 * dim], color=COL_RES, lw=1.6, zorder=3)
    ax.text(x[-1] + a + 0.008 * dim, y[-1] - 0.03 * dim, rotulo, fontsize=6.3, color=COL_RES, ha="left", va="center",
            zorder=4, bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.85))


def _mejor_dir(modelo, k, candidatos):
    """De las direcciones candidatas (°), la más alejada de las barras que llegan al nodo k (evita dibujar el resorte
    encima de una barra)."""
    n = modelo.nodos[k]
    angs = []
    for b in modelo.barras:
        if b.i == k or b.j == k:
            o = modelo.nodos[b.j if b.i == k else b.i]
            angs.append(np.degrees(np.arctan2(o.y - n.y, o.x - n.x)))
    if not angs:
        return candidatos[0]
    def hueco(c):
        return min(abs((c - a + 180) % 360 - 180) for a in angs)
    return max(candidatos, key=hueco)


def _apoyos(modelo, ax, dim):
    """Apoyos (cuadrado = empotrado, triángulo = articulado / móvil) y resortes (zigzag verde: lineales según X, Y o
    inclinados; espiral para el torsional).  Los resortes NO son barras y así se rotulan."""
    for k, n in enumerate(modelo.nodos):
        r, kk = modelo.restr[k], modelo.resortes[k]
        lineas = []
        inc = [sp for sp in modelo.resortes_incl if sp["nodo"] == k]
        if kk[0] > 0:
            _resorte(ax, n, _mejor_dir(modelo, k, [180, 0]), dim, f"resorte kx={fg(kk[0], 3)}")
        if kk[1] > 0:
            _resorte(ax, n, _mejor_dir(modelo, k, [-90, 90]), dim, f"resorte ky={fg(kk[1], 3)}")
        if kk[2] > 0:
            _resorte_torsional(ax, n, dim, f"resorte torsional kφ={fg(kk[2], 3)}")
        for sp in inc:
            _resorte(ax, n, _mejor_dir(modelo, k, [sp["beta"] + 180, sp["beta"]]), dim, f"resorte incl. k={fg(sp['k'], 3)} (eje {fg(sp['beta'], 3)}°)", largo=0.11)
        if r.any():
            if r.all():
                ax.plot(n.x, n.y, "s", ms=10, mfc="#666666", mec="black", zorder=3)
                lineas.insert(0, "empotr.")
            elif r[0] and r[1]:
                ax.plot(n.x, n.y, "^", ms=10, mfc="white", mec="black", mew=1.2, zorder=3)
                lineas.insert(0, "art. fijo" + (" (φ elástico)" if kk[2] > 0 else ""))
            elif r[1] and not r[0]:
                ax.plot(n.x, n.y, "^", ms=10, mfc="white", mec="black", mew=1.2, zorder=3)
                ax.plot([n.x - 0.02 * dim, n.x + 0.02 * dim], [n.y - 0.036 * dim] * 2, color="black", lw=1.2)
                lineas.insert(0, "uy" + (",φ" if r[2] else ""))
            elif r[0] and not r[1]:
                ax.plot(n.x, n.y, "<", ms=10, mfc="white", mec="black", mew=1.2, zorder=3)
                ax.plot([n.x - 0.036 * dim] * 2, [n.y - 0.02 * dim, n.y + 0.02 * dim], color="black", lw=1.2)
                lineas.insert(0, "ux" + (",φ" if r[2] else ""))
            else:
                ax.plot(n.x, n.y, "s", ms=8, mfc="white", mec="black", mew=1.2, zorder=3)
                lineas.insert(0, "φ")
        if lineas:
            ax.text(n.x, n.y - 0.05 * dim, "\n".join(lineas), fontsize=6.5, ha="center", va="top", color="#333333")


# ------------------------------------------------------------------ cargas
def _arco(ax, x, y, r, ccw, col, lw=1.4, zorder=8):
    """Arco de casi 270° con punta de flecha; sentido antihorario si ccw."""
    t = np.radians(np.linspace(35, 300, 40))
    if not ccw:
        t = t[::-1]
    px, py = x + r * np.cos(t), y + r * np.sin(t)
    ax.plot(px[:-1], py[:-1], color=col, lw=lw, zorder=zorder)
    ax.annotate("", xy=(px[-1], py[-1]), xytext=(px[-3], py[-3]), zorder=zorder,
                arrowprops=dict(arrowstyle="-|>", color=col, lw=lw, shrinkA=0, shrinkB=0, mutation_scale=9))


def _flecha(ax, tail, tip, col, lw=1.4, ms=9, zorder=8):
    ax.annotate("", xy=tip, xytext=tail, zorder=zorder,
                arrowprops=dict(arrowstyle="-|>", color=col, lw=lw, shrinkA=0, shrinkB=0, mutation_scale=ms))


def _vec_glob(b, cx, cy):
    """Vector global de una componente local (cx según xl, cy según yl)."""
    return b.g1 * cx - b.g2 * cy, b.g2 * cx + b.g1 * cy


def _etiqueta(ax, x, y, txt, col, ha="center", va="center", fs=6.8):
    ax.text(x, y, txt, fontsize=fs, color=col, ha=ha, va=va, zorder=9,
            bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.85))


def _cargas_tramo(modelo, ax, cb, dim):
    """Cargas en el tramo: q = fila de flechas con las puntas sobre la barra; P = flecha; M = arco; ΔT = rótulo."""
    qmax = max([max(abs(c.qx[0]), abs(c.qx[1]), abs(c.qy[0]), abs(c.qy[1])) * abs(f)
                for c, f in cb if c.tipo == "q"] + [1e-300])
    Pmax = max([max(abs(c.Px), abs(c.Py)) * abs(f) for c, f in cb if c.tipo == "P"] + [1e-300])
    for c, fac in cb:
        b = modelo.barras[c.barra]
        ni = modelo.nodos[b.i]
        pos = lambda x: (ni.x + x * b.g1, ni.y + x * b.g2)
        if c.tipo == "q":
            n = max(3, min(10, int((c.b - c.a) / (0.07 * dim)) + 2))
            colas = []
            for x in np.linspace(c.a, c.b, n):
                t = (x - c.a) / (c.b - c.a)
                cx = (c.qx[0] + (c.qx[1] - c.qx[0]) * t) * fac
                cy = (c.qy[0] + (c.qy[1] - c.qy[0]) * t) * fac
                vx, vy = _vec_glob(b, cx, cy)
                m = np.hypot(vx, vy)
                tip = pos(x)
                if abs(cy) < 0.25 * abs(cx):                     # carga casi axial: separarla lateralmente de la barra
                    tip = (tip[0] - b.g2 * 0.03 * dim, tip[1] + b.g1 * 0.03 * dim)
                if m > 1e-9 * qmax:
                    k = 0.13 * dim / qmax
                    tail = (tip[0] - k * vx, tip[1] - k * vy)
                    _flecha(ax, tail, tip, COL_PY, lw=1.0, ms=6)
                    colas.append(tail)
            if len(colas) > 1:
                ax.plot([p[0] for p in colas], [p[1] for p in colas], color=COL_PY, lw=1.0, zorder=7)
            if colas:
                m = colas[len(colas) // 2]
                v1, v2 = c.v1 * fac, c.v2 * fac
                txt = f"{c.orig}={fg(v1, 3)}" if abs(v1 - v2) <= 1e-12 * max(abs(v1), 1e-300) else \
                    f"{c.orig}={fg(v1, 3)}→{fg(v2, 3)}"
                dx, dy = m[0] - pos((c.a + c.b) / 2)[0], m[1] - pos((c.a + c.b) / 2)[1]
                nn = np.hypot(dx, dy) or 1.0
                _etiqueta(ax, m[0] + 0.03 * dim * dx / nn, m[1] + 0.03 * dim * dy / nn, txt, COL_PY)
        elif c.tipo == "P":
            vx, vy = _vec_glob(b, c.Px * fac, c.Py * fac)
            m = np.hypot(vx, vy)
            tip = pos(c.a)
            if m > 0:
                k = 0.16 * dim / Pmax
                tail = (tip[0] - k * vx, tip[1] - k * vy)
                _flecha(ax, tail, tip, COL_PY, lw=1.6)
                _etiqueta(ax, tail[0] - 0.02 * dim * vx / m, tail[1] - 0.02 * dim * vy / m,
                          f"{c.orig}={fg(c.v1 * fac, 3)}\na={fg(c.a, 3)}", COL_PY, fs=6.5)
        elif c.tipo == "M":
            p = pos(c.a)
            _arco(ax, p[0], p[1], 0.045 * dim, c.M0 * fac > 0, COL_M)
            _etiqueta(ax, p[0] + 0.07 * dim, p[1] + 0.06 * dim, f"Mp={fg(c.M0 * fac, 3)}\na={fg(c.a, 3)}", COL_M, fs=6.5)
        elif c.tipo == "temp" and c.orig == "dl":
            p = pos(0.3 * b.L)
            _etiqueta(ax, p[0] - b.g2 * 0.06 * dim * -1, p[1] + b.g1 * 0.06 * dim * -1,
                      f"barra {'LARGA' if c.e0 * fac > 0 else 'CORTA'} e={fg(abs(c.e0 * fac), 3)}", COL_TEMP, fs=6.5)
        elif c.tipo == "temp" and hasattr(modelo, "ret_pandeo"):
            p = pos(0.3 * b.L)
            _etiqueta(ax, p[0] - b.g2 * 0.06 * dim * -1, p[1] + b.g1 * 0.06 * dim * -1,
                      f"ΔT={fg(c.Ts * fac, 3)} °", COL_TEMP, fs=6.5)
        elif c.tipo == "temp":
            p = pos(b.L / 2)
            _etiqueta(ax, p[0] - b.g2 * 0.06 * dim * -1, p[1] + b.g1 * 0.06 * dim * -1,
                      f"ΔT(+yl)={fg(c.Ts * fac, 3)} / ΔT(−yl)={fg(c.Ti * fac, 3)} °", COL_TEMP, fs=6.5)


def _cargas_nodales(modelo, ax, F, dim):
    escala = max(np.abs(F[:, :2]).max() if F.size else 0.0, 1e-300)
    for k, n in enumerate(modelo.nodos):
        px, py, m = F[k]
        for val, vec, nom, col in ((px, (1, 0), "Px", COL_PX), (py, (0, 1), "Py", COL_PY)):
            if abs(val) > 1e-12 * escala:
                L = 0.13 * dim * max(abs(val) / escala, 0.35)
                s = 1 if val > 0 else -1
                tail = (n.x - s * vec[0] * L, n.y - s * vec[1] * L)
                _flecha(ax, tail, (n.x, n.y), col, lw=1.6)
                _etiqueta(ax, tail[0] - s * vec[0] * 0.01 * dim + (0 if vec[0] else 0.0),
                          tail[1] - s * vec[1] * 0.01 * dim, f"{nom}={fg(val, 4)}", col, fs=7,
                          ha="right" if (vec[0] and s > 0) else ("left" if vec[0] else "center"),
                          va="center" if vec[0] else ("top" if s > 0 else "bottom"))
        if abs(m) > 1e-12 * max(np.abs(F[:, 2]).max(), 1e-300):
            _arco(ax, n.x, n.y, 0.05 * dim, m > 0, COL_M)
            _etiqueta(ax, n.x + 0.06 * dim, n.y - 0.06 * dim, f"M={fg(m, 4)}", COL_M, ha="left", fs=7)


def fig_esquema(modelo, F=None, cb=None) -> str:
    """Esquema: barras, nodos, articulaciones, apoyos, resortes y (si se pasan) las cargas nodales y en tramos."""
    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    xs, ys, dim = _extension(modelo)
    _base(modelo, ax)
    _apoyos(modelo, ax, dim)
    if F is not None:
        _cargas_nodales(modelo, ax, F, dim)
    if cb:
        _cargas_tramo(modelo, ax, cb, dim)
    proxies = [Line2D([], [], marker="s", ls="", mfc="#666666", mec="black", ms=7, label="empotramiento"),
               Line2D([], [], marker="^", ls="", mfc="white", mec="black", ms=7, label="apoyo articulado / móvil"),
               ]
    if not hasattr(modelo, "ret_pandeo"):
        proxies.append(Line2D([], [], marker="o", ls="", mfc="white", mec="black", ms=6, label="articulación (M = 0)"))
    if modelo.res_mask.any():
        proxies.append(Line2D([], [], color=COL_RES, lw=1.4, marker=r"$\sim$", ms=10, label="resorte (no es una barra)"))
    if F is not None or cb:
        proxies += [Line2D([], [], color=COL_PX, lw=1.4, label="Px"), Line2D([], [], color=COL_PY, lw=1.4, label="Py, P, q"),
                    ]
        if not hasattr(modelo, "ret_pandeo"):
            proxies.append(Line2D([], [], color=COL_M, lw=1.4, label="M (antihorario +)"))
    ax.legend(handles=proxies, loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=3, fontsize=7, frameon=False)
    return _a_svg(fig)


# ------------------------------------------------------------------ diagramas
def fig_diagrama_curvas(modelo, series, unidad: str, texto_signo: str = "", escala: str = "barra", lado: int = 1) -> str:
    """Diagrama sobre el pórtico con curvas x–v por barra.

    series[k] = (x, v): abscisa local desde el nodo i y valor.  lado = +1: los valores positivos se dibujan hacia
    +yl (izquierda de i→j); lado = −1: hacia −yl (derecha de i→j; se usa para M: lado de la fibra traccionada).
    escala = "barra": cada barra a su propia escala (se ve la forma; los números rotulados son los reales);
    "global": una escala única.  Barras con valores despreciables (< 1e-6 del máximo) no se dibujan."""
    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    xs, ys, dim = _extension(modelo)
    _base(modelo, ax, etiquetas_barras=False, gris=False)
    vmax = max(np.abs(v).max() for _, v in series)
    if vmax <= 1e-12:
        ax.text(0.5, 0.5, "Esfuerzo nulo en toda la estructura", transform=ax.transAxes, ha="center", va="center",
                fontsize=10)
        return _a_svg(fig)
    etiquetas = []
    for k, b in enumerate(modelo.barras):
        ni = modelo.nodos[b.i]
        nx_, ny_ = -b.g2 * lado, b.g1 * lado
        x, v = np.asarray(series[k][0]), np.asarray(series[k][1])
        vk = np.abs(v).max()
        if vk <= 1e-6 * vmax:
            continue
        esc = 0.12 * dim / (vk if escala == "barra" else vmax)
        glob = lambda sx, sv: (ni.x + sx * b.g1 + sv * esc * nx_, ni.y + sx * b.g2 + sv * esc * ny_)
        for px, pv, sg in _partes(x, v):
            pts = [glob(px[0], 0.0)] + [glob(a, c) for a, c in zip(px, pv)] + [glob(px[-1], 0.0)]
            ax.add_patch(Polygon(pts, closed=True, fc=COL_POS if sg > 0 else COL_NEG,
                                 ec=COL_POS_E if sg > 0 else COL_NEG_E, lw=0.9, alpha=0.9, zorder=3))
        for i in _puntos_a_rotular(x, v, b.L):
            if abs(v[i]) > 1e-9 * vmax:
                sg = 1 if v[i] > 0 else -1
                px, py = glob(x[i], v[i])
                etiquetas.append((px, py, fg(v[i], 4), (sg * nx_, sg * ny_), abs(v[i])))
    _rotular(fig, ax, etiquetas, [(n.x, n.y) for n in modelo.nodos] + [(n.x + 0.03 * dim, n.y + 0.03 * dim) for n in modelo.nodos])
    ax.legend(handles=[Patch(fc=COL_POS, ec=COL_POS_E, label="valores positivos"),
                       Patch(fc=COL_NEG, ec=COL_NEG_E, label="valores negativos")],
              loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=2, fontsize=7.5, frameon=False)
    nota = "cada barra a su propia escala; valores rotulados = reales" if escala == "barra" else "escala única"
    ax.text(0.99, 0.01, f"[{unidad}]   {texto_signo}   ({nota})", transform=ax.transAxes, fontsize=7,
            ha="right", va="bottom", color="#333333")
    return _a_svg(fig)


# ------------------------------------------------------------------ deformada
def escala_auto(modelo, res) -> float:
    xs, ys, dim = _extension(modelo)
    dmax = np.abs(res.u[:, :2]).max()
    if dmax <= 0:
        return 1.0
    return float(f"{0.12 * dim / dmax:.1g}")


def fig_deformada(modelo, res, escala: float | None = None) -> tuple:
    """Estructura deformada (desplazamientos amplificados).  Devuelve (svg, escala_usada)."""
    esc = escala if escala else escala_auto(modelo, res)
    xs, ys, dim = _extension(modelo)
    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    _base(modelo, ax, etiquetas_barras=False, gris=True)
    _apoyos(modelo, ax, dim)
    for X0, Y0, DX, DY in elastica(modelo, res, n=31):
        ax.plot(X0 + esc * DX, Y0 + esc * DY, color="black", lw=2.0, zorder=5)
    orden = np.argsort(-np.hypot(res.u[:, 0], res.u[:, 1]))
    nlab = len(orden) if len(orden) <= 10 else 7
    umax = max(np.hypot(res.u[:, 0], res.u[:, 1]).max(), 1e-300)
    etiquetas = []
    for k in orden[:nlab]:
        ux, uy, ph = res.u[k]
        if np.hypot(ux, uy) > 1e-9 * umax:
            n = modelo.nodos[k]
            px, py = n.x + esc * ux, n.y + esc * uy
            ax.plot(px, py, "o", ms=3.5, color="black", zorder=6)
            etiquetas.append((px, py, f"({fg(ux, 3)}; {fg(uy, 3)})", (0, 1), abs(ux) + abs(uy)))
    _rotular(fig, ax, etiquetas, [(n.x, n.y) for n in modelo.nodos])
    ax.legend(handles=[Line2D([], [], color="#9a9a9a", lw=1.6, label="indeformada"),
                       Line2D([], [], color="black", lw=2, label=f"deformada (× {esc:g})"),
                       Line2D([], [], color="none", label=f"cifras: (ux; uy) reales [{modelo.config['unidad_longitud']}]")],
              loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=3, fontsize=7.5, frameon=False)
    return _a_svg(fig), esc
