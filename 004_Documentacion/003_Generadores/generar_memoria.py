"""Genera 004_Documentacion/002_Memorias/Struttura_Memoria_emparrillado.html: cómo se usa y cómo funciona el programa.

Ejecutar desde la carpeta raíz del proyecto:   python 004_Documentacion/003_Generadores/generar_memoria.py
"""
import html
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]  # carpeta Struttura
sys.path.insert(0, str(RAIZ / "001_Codigo"))

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Arc, FancyArrowPatch, FancyBboxPatch, Rectangle

from struttura import __version__
from struttura.emparrillado import graficos
from struttura.emparrillado import visor3d
from struttura.emparrillado.entrada import cargar_modelo
from struttura.emparrillado.informe import documento, tabla

e_ = html.escape
AZUL, NARANJA, VERDE, GRIS, ROJO = "#cfe0f3", "#f8dcc0", "#d3ead0", "#e6e6e6", "#f0c8c0"


# ----------------------------------------------------------------------------- utilidades de dibujo
def _caja(ax, x, y, w, h, titulo, sub="", color=AZUL, fs=8.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3,rounding_size=1.2", fc=color, ec="black", lw=1.0))
    ax.text(x + w / 2, y + h * (0.62 if sub else 0.5), titulo, ha="center", va="center", fontsize=fs, fontweight="bold")
    if sub:
        ax.text(x + w / 2, y + h * 0.2, sub, ha="center", va="center", fontsize=7, style="italic")


def _flecha(ax, p0, p1, rad=0.0, lw=1.2, color="black", estilo="-|>"):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle=estilo, mutation_scale=10, lw=lw, color=color,
                                 connectionstyle=f"arc3,rad={rad}", shrinkA=0, shrinkB=0))


def _doble(ax, p0, p1, color="#1f4e79", lw=1.4):
    """Flecha de vector momento/giro: doble punta."""
    p0, p1 = np.array(p0, float), np.array(p1, float)
    d = (p1 - p0) / np.linalg.norm(p1 - p0)
    _flecha(ax, p0, p1, lw=lw, color=color)
    _flecha(ax, p0, p1 - d * 0.28, lw=lw, color=color)


def _lienzo(w, h, xlim, ylim):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


# ----------------------------------------------------------------------------- figuras
def fig_flujo():
    fig, ax = _lienzo(7.4, 3.9, (0, 100), (-3, 58))
    top = [(1, "ARCHIVO CSV ÚNICO", "bloques con título", GRIS, "lo escribís vos"),
           (36, "1. LECTURA Y\nVALIDACIÓN", "entrada.py", AZUL, "nodos, barras, apoyos,\ncargas (nodos y tramos)"),
           (71, "2. MATRIZ DE\nCADA BARRA", "barra.py · secciones.py", AZUL, "k local → k global (6×6)")]
    bot = [(71, "3. ENSAMBLAJE Y\nSOLUCIÓN", "solver.py", AZUL, "K·u = F, reacciones,\nchequeo de estabilidad"),
           (36, "4. ESFUERZOS Y\nTENSIONES", "esfuerzos.py", AZUL, "V(x), T, M(x), σ, τ, σVM,\nCS, deformada"),
           (1, "5. INFORME", "informe.py · graficos.py", GRIS, "HTML + CSV de resultados")]
    for x, t, s, c, out in top:
        _caja(ax, x, 36, 28, 15, t, s, c)
        ax.text(x + 14, 32, out, ha="center", va="top", fontsize=6.8)
    for x, t, s, c, out in bot:
        _caja(ax, x, 6, 28, 15, t, s, c)
        ax.text(x + 14, 2.5, out, ha="center", va="top", fontsize=6.8)
    for x0 in (29.6, 64.6):
        _flecha(ax, (x0, 43.5), (x0 + 5.4, 43.5))
    _flecha(ax, (85, 35.5), (85, 21.5))
    for x0 in (70.4, 35.4):
        _flecha(ax, (x0, 13.5), (x0 - 5.8, 13.5))
    return graficos._a_svg(fig)


def fig_lectura():
    csv = [("PROYECTO", 0), ("proyecto;Ejemplo 1", 0),
           ("NODOS", 1), ("id;x;y", 1), ("1;0;0", 1), ("2;1000;0", 1),
           ("BARRAS", 2), ("id;nodo_i;nodo_j;material;seccion", 2), ("1;1;2;ACERO;T1", 2),
           ("APOYOS", 3), ("nodo;uz;phix;phiy", 3), ("1;1;1;1", 3),
           ("CARGAS", 4), ("caso;nodo;Pz;Mx;My", 4), ("P;2;-500;0;0", 4)]
    colores = [GRIS, AZUL, VERDE, NARANJA, ROJO]
    destinos = ["config: unidades,\nescala, opciones", "lista de Nodo(id, x, y)",
                "Barra(i, j, material, sección,\nL, γ1, γ2)", "restr[n × 3]\n(verdadero = restringido)",
                "F[caso][n × 3]\n(cargas en ejes globales)"]
    lh = 3.7
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    ax.axis("off")
    ax.set_xlim(0, 100)
    ax.set_ylim(-1, lh * len(csv) + 3)
    ytop = lh * len(csv)
    bandas = {}
    for i, (txt, b) in enumerate(csv):
        y = ytop - (i + 1) * lh
        bandas.setdefault(b, []).append(y)
        ax.add_patch(Rectangle((0, y), 50, lh, fc=colores[b], ec="none", alpha=0.85))
        ax.text(1.5, y + lh / 2, txt, family="monospace", fontsize=6.8, va="center",
                fontweight="bold" if txt in ("PROYECTO", "NODOS", "BARRAS", "APOYOS", "CARGAS") else "normal")
    ax.text(25, ytop + 1.5, "archivo .csv (un solo archivo)", ha="center", fontsize=8, fontweight="bold")
    ax.text(79, ytop + 1.5, "lo que el programa arma", ha="center", fontsize=8, fontweight="bold")
    for b, ys in bandas.items():
        yc = (min(ys) + max(ys) + lh) / 2
        _caja(ax, 62, yc - 3.4, 34, 6.8, destinos[b], "", colores[b], fs=6.8)
        _flecha(ax, (50.6, yc), (61.6, yc))
    return graficos._a_svg(fig)


def fig_ejes():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.4, 3.5), gridspec_kw={"width_ratios": [1.5, 1]})
    for a in (a1, a2):
        a.set_aspect("equal")
        a.axis("off")
    # (a) barra en la planta
    a1.set_xlim(-1.2, 5.6)
    a1.set_ylim(-1.0, 3.6)
    _flecha(a1, (-0.6, 0), (5.2, 0), lw=1.3)
    _flecha(a1, (0, -0.6), (0, 3.3), lw=1.3)
    a1.text(5.3, -0.05, "X", fontsize=10, va="center")
    a1.text(0.1, 3.4, "Y", fontsize=10)
    a1.plot(-0.55, -0.6, "o", ms=9, mfc="white", mec="black")
    a1.plot(-0.55, -0.6, ".", ms=4, color="black")
    a1.text(-0.3, -0.62, "z (hacia el lector)", fontsize=7, va="center")
    pi, pj = np.array([1.0, 0.8]), np.array([4.2, 2.7])
    a1.plot(*zip(pi, pj), color="black", lw=3, solid_capstyle="round")
    a1.plot(*pi, "o", color="black", ms=6)
    a1.plot(*pj, "o", color="black", ms=6)
    a1.text(pi[0] - 0.25, pi[1] - 0.25, "i", fontsize=10, fontweight="bold")
    a1.text(pj[0] + 0.12, pj[1] + 0.05, "j", fontsize=10, fontweight="bold")
    ang = np.arctan2(*(pj - pi)[::-1])
    u = np.array([np.cos(ang), np.sin(ang)])
    v = np.array([-u[1], u[0]])
    _flecha(a1, pi, pi + 1.7 * u, color="#1f4e79", lw=1.8)
    _flecha(a1, pi, pi + 1.2 * v, color="#8a2c1a", lw=1.8)
    a1.text(*(pi + 1.85 * u + 0.05 * v), r"$x_l$", color="#1f4e79", fontsize=10)
    a1.text(*(pi + 1.3 * v - 0.15 * u), r"$y_l$", color="#8a2c1a", fontsize=10)
    a1.plot([pi[0], pj[0]], [pi[1], pi[1]], ls=":", color="gray")
    a1.plot([pj[0], pj[0]], [pi[1], pj[1]], ls=":", color="gray")
    a1.add_patch(Arc(pi, 1.7, 1.7, theta1=0, theta2=np.degrees(ang), color="black", lw=1))
    a1.text(pi[0] + 1.05, pi[1] + 0.18, r"$\alpha$", fontsize=10)
    a1.text((pi[0] + pj[0]) / 2, pi[1] - 0.28, r"$\Delta x$", fontsize=9, ha="center")
    a1.text(pj[0] + 0.1, (pi[1] + pj[1]) / 2, r"$\Delta y$", fontsize=9)
    a1.text(2.3, 3.4, r"$\gamma_1=\cos\alpha=\Delta x/L\quad\gamma_2=\sin\alpha=\Delta y/L$", fontsize=8, ha="center")
    a1.set_title("(a) Ejes global (X, Y, z) y local de la barra (xl, yl)", fontsize=8.5)
    # (b) GDL de un nodo
    a2.set_xlim(-1.6, 2.6)
    a2.set_ylim(-1.5, 2.6)
    a2.plot(0, 0, "o", ms=13, mfc="white", mec="#8a2c1a", mew=1.4)
    a2.plot(0, 0, ".", ms=6, color="#8a2c1a")
    a2.text(-0.25, -0.5, r"$u_z$ (hacia +z)", fontsize=8, color="#8a2c1a", ha="center")
    _doble(a2, (0.25, 0), (2.1, 0))
    a2.text(2.15, -0.08, r"$\varphi_x$", fontsize=10, color="#1f4e79")
    _doble(a2, (0, 0.25), (0, 2.0))
    a2.text(0.12, 2.15, r"$\varphi_y$", fontsize=10, color="#1f4e79")
    a2.text(0.5, -1.1, "3 GDL por nodo\n(giros = vectores)", fontsize=8, ha="center")
    a2.set_title("(b) Grados de libertad de un nodo", fontsize=8.5)
    fig.tight_layout()
    return graficos._a_svg(fig)


def fig_ensamblaje():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.4, 3.9), gridspec_kw={"width_ratios": [1, 2.2]})
    a1.set_aspect("equal")
    a1.axis("off")
    a1.set_xlim(-0.6, 2.8)
    a1.set_ylim(-0.6, 2.2)
    p = {1: (0, 0), 2: (2, 0), 3: (2, 1.6)}
    a1.plot(*zip(p[1], p[2]), color="#1f4e79", lw=3)
    a1.plot(*zip(p[2], p[3]), color="#c0641c", lw=3)
    for k, (x, y) in p.items():
        a1.plot(x, y, "o", color="black", ms=7)
        a1.text(x - 0.22, y - 0.25, str(k), fontsize=10, fontweight="bold")
    a1.text(1.0, 0.1, "barra 1", color="#1f4e79", fontsize=8, ha="center")
    a1.text(2.1, 0.8, "barra 2", color="#c0641c", fontsize=8, rotation=90, va="center")
    a1.set_title("Estructura de ejemplo", fontsize=8.5)
    # matriz 9x9 en bloques
    a2.set_aspect("equal")
    a2.axis("off")
    a2.set_xlim(-2.2, 9.6)
    a2.set_ylim(-9.8, 1.8)
    b1, b2, bm, cero = AZUL, NARANJA, VERDE, "white"
    bloques = {(0, 0): (b1, "k¹[i,i]"), (0, 1): (b1, "k¹[i,j]"), (1, 0): (b1, "k¹[j,i]"),
               (1, 1): (bm, "k¹[j,j]\n+ k²[i,i]"), (1, 2): (b2, "k²[i,j]"), (2, 1): (b2, "k²[j,i]"),
               (2, 2): (b2, "k²[j,j]"), (0, 2): (cero, "0"), (2, 0): (cero, "0")}
    for (r, c), (col, txt) in bloques.items():
        a2.add_patch(Rectangle((c * 3, -(r + 1) * 3), 3, 3, fc=col, ec="black", lw=1.2))
        for t in (1, 2):
            a2.plot([c * 3 + t, c * 3 + t], [-(r + 1) * 3, -r * 3], color="#999999", lw=0.4)
            a2.plot([c * 3, c * 3 + 3], [-(r * 3 + t), -(r * 3 + t)], color="#999999", lw=0.4)
        a2.text(c * 3 + 1.5, -(r * 3 + 1.5), txt, ha="center", va="center", fontsize=7.5)
    for k in range(3):
        a2.text(k * 3 + 1.5, 0.5, f"nodo {k + 1}", ha="center", fontsize=8, fontweight="bold")
        a2.text(-0.4, -(k * 3 + 1.5), f"nodo {k + 1}", ha="right", va="center", fontsize=8, fontweight="bold")
        for d, nm in enumerate((r"$u_z$", r"$\varphi_x$", r"$\varphi_y$")):
            a2.text(k * 3 + d + 0.5, -0.05, nm, ha="center", va="bottom", fontsize=5.5)
    a2.text(4.5, -9.6, "Cada barra suma su matriz 6×6 en los bloques de sus dos nodos;\n"
                       "donde dos barras comparten nodo, los aportes se suman.", ha="center", va="top", fontsize=7.3)
    a2.set_title("Matriz de rigidez global K (9 × 9): 3 GDL por nodo", fontsize=8.5)
    fig.tight_layout()
    return graficos._a_svg(fig)


def fig_particion():
    fig, ax = _lienzo(7.4, 4.3, (-1, 60), (-42, 3))
    nf, nr = 20, 8
    c_f, c_r = AZUL, NARANJA
    # K
    ax.add_patch(Rectangle((0, -nf), nf, nf, fc=c_f, ec="black"))
    ax.add_patch(Rectangle((nf, -nf), nr, nf, fc="white", ec="black"))
    ax.add_patch(Rectangle((0, -nf - nr), nf, nr, fc="white", ec="black"))
    ax.add_patch(Rectangle((nf, -nf - nr), nr, nr, fc=c_r, ec="black"))
    ax.text(nf / 2, -nf / 2, r"$K_{ff}$", ha="center", va="center", fontsize=12)
    ax.text(nf + nr / 2, -nf / 2, r"$K_{fr}$", ha="center", va="center", fontsize=10)
    ax.text(nf / 2, -nf - nr / 2, r"$K_{rf}$", ha="center", va="center", fontsize=10)
    ax.text(nf + nr / 2, -nf - nr / 2, r"$K_{rr}$", ha="center", va="center", fontsize=10)
    # u
    x0 = 33
    ax.add_patch(Rectangle((x0, -nf), 6, nf, fc=c_f, ec="black"))
    ax.add_patch(Rectangle((x0, -nf - nr), 6, nr, fc=c_r, ec="black"))
    ax.text(x0 + 3, -nf / 2, r"$u_f$" + "\nincógnita", ha="center", va="center", fontsize=8)
    ax.text(x0 + 3, -nf - nr / 2, r"$u_r$" + "\nprefijado", ha="center", va="center", fontsize=7)
    ax.text(x0 - 2.2, -nf - nr / 2 - 10 + 10, "×", fontsize=13, ha="center", va="center")
    ax.text(x0 + 9, -(nf + nr) / 2, "=", fontsize=16, ha="center", va="center")
    x1 = 46
    ax.add_patch(Rectangle((x1, -nf), 7, nf, fc=c_f, ec="black"))
    ax.add_patch(Rectangle((x1, -nf - nr), 7, nr, fc=c_r, ec="black"))
    ax.text(x1 + 3.5, -nf / 2, r"$F_f$" + "\ncargas", ha="center", va="center", fontsize=8)
    ax.text(x1 + 3.5, -nf - nr / 2, r"$F_r + R$", ha="center", va="center", fontsize=8)
    ax.text(nf / 2, 1.2, "GDL libres", ha="center", fontsize=8, color="#1f4e79", fontweight="bold")
    ax.text(nf + nr / 2, 1.2, "restring.", ha="center", fontsize=8, color="#c0641c", fontweight="bold")
    ax.text(0, -nf - nr - 3.5, "1)  " + r"$K_{ff}\,u_f = F_f - K_{fr}\,u_r$" + "   →  se resuelve " + r"$u_f$"
            + "  (los resortes ya están sumados en la diagonal de K)", fontsize=8.3)
    ax.text(0, -nf - nr - 7.7, "2)  " + r"$R = K_{rf}\,u_f + K_{rr}\,u_r - F_r$" + "   →  reacciones de apoyo", fontsize=8.3)
    ax.text(0, -nf - nr - 11.9, "3)  " + r"$F_{resorte} = -k\,u$" + "   →  fuerza de cada resorte sobre la estructura", fontsize=8.3)
    return graficos._a_svg(fig)


def fig_signos():
    fig, ax = _lienzo(7.4, 3.3, (-3.2, 10.0), (-3.6, 3.0))
    ax.add_patch(Rectangle((0, -0.5), 6.5, 1.0, fc=GRIS, ec="black", lw=1.4))
    ax.plot([0, 0], [-0.5, 0.5], color="black", lw=3)
    ax.plot([6.5, 6.5], [-0.5, 0.5], color="black", lw=3)
    ax.text(3.25, 0, "elemento de barra (vista lateral: x → derecha, z ↑)", ha="center", va="center", fontsize=7.5)
    # cortante: cara izquierda hacia arriba, cara derecha hacia abajo
    _flecha(ax, (-0.35, -1.5), (-0.35, 1.5), lw=2, color="#1f4e79")
    _flecha(ax, (6.85, 1.5), (6.85, -1.5), lw=2, color="#1f4e79")
    ax.text(-0.65, 1.7, "V", fontsize=11, color="#1f4e79", ha="center")
    ax.text(7.15, -1.85, "V", fontsize=11, color="#1f4e79", ha="center")
    # momento: cara izquierda horario, cara derecha antihorario
    _flecha(ax, (-1.3, -1.3), (-1.3, 1.3), rad=-0.9, lw=1.8, color="#8a2c1a")
    _flecha(ax, (7.8, -1.3), (7.8, 1.3), rad=0.9, lw=1.8, color="#8a2c1a")
    ax.text(-2.6, 0, "M", fontsize=11, color="#8a2c1a", ha="center", va="center")
    ax.text(9.6, 0, "M", fontsize=11, color="#8a2c1a", ha="center", va="center")
    ax.text(3.25, -2.3, "Positivos:  V → la cara +xl (derecha) recibe fuerza hacia −z\n"
                        "M → tracciona la fibra inferior (−z);  T → vector momento hacia +xl en la cara +xl",
            ha="center", va="center", fontsize=8)
    ax.text(3.25, 1.7, "cara −xl (lado i)          cara +xl (lado j)", ha="center", fontsize=7, style="italic", color="#444444")
    return graficos._a_svg(fig)


def fig_metodo_tramo():
    fig, ax = _lienzo(7.4, 4.6, (0, 100), (-4, 62))
    ax.text(1, 58, "A mano (cátedra): tres estados", fontsize=9, fontweight="bold")
    filas = [("ESTADO 1\nbarra biempotrada\ncon la carga", "f₀, diagramas", NARANJA),
             ("ESTADO 2\nestructura con −f₀ en los\nnodos + prefijados", "u, k·u", AZUL),
             ("SUPERPOSICIÓN\nestado 1 + estado 2", "esfuerzos finales", VERDE)]
    x0 = 1
    for k, (t, sub, c) in enumerate(filas):
        _caja(ax, x0 + k * 33, 38, 28, 15, t, sub, c, fs=7.6)
    for k in range(2):
        _flecha(ax, (x0 + k * 33 + 29.2, 45.5), (x0 + (k + 1) * 33 - 1.2, 45.5))
    ax.text(1, 27, "En el programa: mismo resultado, sin separar los estados", fontsize=9, fontweight="bold")
    caj = [("f₀ de la tabla\n(por carga y barra)", "cargas_barra.py", NARANJA),
           ("F_eq = −f₀ girada\na globales, en los nodos", "solver.py", AZUL),
           ("K·u = F + ΣF_eq\n(una sola solución)", "solver.py", AZUL),
           ("f = k·u_loc + f₀\nV(x), M(x) = f + tramo", "esfuerzos.py", VERDE)]
    for k, (t, sub, c) in enumerate(caj):
        _caja(ax, 0.5 + k * 25, 4, 22, 15, t, sub, c, fs=7.0)
    for k in range(3):
        _flecha(ax, (0.5 + k * 25 + 23.3, 11.5), (0.5 + (k + 1) * 25 - 1.0, 11.5))
    ax.text(50, -2.5, "Estado 1 ⇔ f₀ y diagramas del tramo biempotrado;   estado 2 ⇔ resolver con las cargas equivalentes;   "
                      "superposición ⇔ f = k·u + f₀", ha="center", fontsize=6.8, style="italic")
    return graficos._a_svg(fig)


# ----------------------------------------------------------------------------- texto
def figura(n, svg, cap):
    return f'<figure>{svg}<figcaption>Figura {n}. {cap}</figcaption></figure>'


import sys as _s
_s.path.insert(0, str(Path(__file__).resolve().parent))
from _esquema import esquema_modelo  # noqa: E402

def esquema():
    return esquema_modelo('Cómo se usa: emparrillado plano', 'plantilla_emparrillado.csv', 'emparrillado',
        [('NODOS', 'id; x; y'), ('MATERIALES', 'id; E; nu o G; fy; sadm; alfa  |  o  id; lib   (+ rho para peso propio)'), ('SECCIONES', 'id; tipo; d; t; b; h; I; J; A; c; Wt; kv'), ('BARRAS', 'id; nodo_i; nodo_j; material; seccion'), ('APOYOS', 'nodo; uz; phix; phiy   (1 = restringido)')],
        [('CARGAS', 'caso; nodo; Pz; Mx; My'), ('CARGAS EN BARRAS', 'caso; barra; tipo; valor; valor2; a; b'), ('COMBINACIONES', 'combinacion; caso; factor'), ('RESORTES / RESORTES GIRO INCLINADO', 'apoyos elásticos'), ('DESPLAZAMIENTOS PREFIJADOS', 'asentamientos de apoyo'), ('DESAJUSTE DE RESORTES', 'desajuste inicial'), ('PROYECTO: peso_propio', 'peso_propio;CASO · gravedad;-z  (necesita rho en MATERIALES)')],
        ['informe.html con visor (estructura, utilización, deformada, diagramas, resultados por caso y combinación)', 'desplazamientos, reacciones, esfuerzos, tensiones y matriz_K (.csv)', 'resortes.csv (si hay resortes)'])


def cuerpo() -> str:
    ej1 = (RAIZ / "003_Ejemplos" / "001_Emparrillado" / "ejemplo1_voladizo_L.csv").read_text(encoding="utf-8")
    p = []
    p.append("<h1>Memoria del programa</h1><div class='sub'>Emparrillados planos por el método matricial de rigidez – "
             "cómo se usa y cómo funciona (Struttura v" + __version__ + ")</div>")
    p.append("<h2>0. Mapa de uso</h2><p>De arriba hacia abajo: qué copiás, qué bloques completás (amarillo = obligatorios) y qué obtenés.  Los bloques en gris son opcionales.</p>" + esquema())
    p.append("""<ul class="conv">
<li><b>1.</b> Qué hace el programa</li><li><b>2.</b> Cómo se usa</li><li><b>3.</b> El archivo de datos (CSV único)</li>
<li><b>4.</b> Cómo lee y valida los datos</li><li><b>5.</b> Modelo de cálculo: ejes, GDL y matriz de la barra</li>
<li><b>6.</b> Ensamblaje</li><li><b>7.</b> Apoyos, resortes, desplazamientos prefijados y solución</li>
<li><b>8.</b> Esfuerzos y deformada</li><li><b>9.</b> Cargas en el tramo (q, P, gradiente térmico)</li>
<li><b>10.</b> Tensiones y coeficientes de seguridad</li><li><b>11.</b> Vista 3D interactiva</li>
<li><b>12.</b> Verificaciones internas</li><li><b>13.</b> Estructura del código</li>
<li><b>14.</b> Cómo agregar cosas (tipos de sección)</li><li><b>15.</b> Limitaciones y próximos pasos</li></ul>""")

    # 1
    p.append("<h2>1. Qué hace el programa</h2>")
    p.append("""<p>Resuelve <b>emparrillados planos</b>: estructuras de barras en el plano XY cargadas
perpendicularmente a su plano.  Cada nodo tiene 3 grados de libertad (u<sub>z</sub>, φ<sub>x</sub>, φ<sub>y</sub>) y cada
barra trabaja a flexión, corte y torsión.  A partir de un único archivo CSV calcula desplazamientos, reacciones,
esfuerzos (V, T, M), tensiones y coeficientes de seguridad, y genera un informe HTML con la estructura deformada
y los diagramas.  Solo usa Python, numpy y matplotlib.</p>
<p><b>Struttura 1.1.0:</b> resuelve también <b>reticulados planos</b> (<code>tipo;reticulado</code>, memoria <code>004_Documentacion/002_Memorias/Struttura_Memoria_reticulado.html</code>) y trae una <b>guía rápida en PDF</b> (<code>004_Documentacion/001_Guia_rapida/Struttura_Guia_rapida.pdf</code>).  <b>Desde la versión 2.1:</b> el mismo <code>struttura.py</code> resuelve también <b>pórticos planos</b> (programa aparte,
paquete <code>struttura/portico/</code>, con su propia plantilla de CSV y su propia memoria: <code>004_Documentacion/002_Memorias/Struttura_Memoria_portico.html</code>).
El despachador elige el programa por la línea <code>tipo;emparrillado</code> / <code>tipo;portico</code> / <code>tipo;reticulado</code> del bloque PROYECTO
o, si falta, por el encabezado del bloque APOYOS.  Plantillas comentadas en <code>002_Plantillas/</code>.</p>""")
    p.append(figura(1, fig_flujo(), "Flujo general: del archivo de datos al informe."))

    # 2
    p.append("<h2>2. Cómo se usa</h2>")
    p.append("""<ol>
<li>Escribir el archivo de datos (por ejemplo <code>mi_parrilla.csv</code>) con los bloques descriptos en la sección 3.
Se puede editar con Excel, LibreOffice o cualquier editor de texto.</li>
<li>Revisar los datos <b>sin calcular</b>: <code>python struttura.py mi_parrilla.csv --solo-esquema</code>.
Crea <code>esquema.html</code> con la numeración, los apoyos, los resortes y las cargas dibujadas, y avisa si la estructura
es un mecanismo.  Conviene mirar el signo de las cargas acá antes de resolver.</li>
<li>Calcular: <code>python struttura.py mi_parrilla.csv</code>.  Genera la carpeta <code>mi_parrilla_salida/</code> con
<code>informe.html</code> y los resultados en CSV.</li>
<li>Abrir <code>informe.html</code> en el navegador.  El botón <b>Imprimir</b> del final arma la versión para papel o PDF.</li></ol>""")
    p.append(tabla(["Opción", "Efecto"],
                   [["<code>-o CARPETA</code>", "carpeta de salida distinta de la de por defecto"],
                    ["<code>--sin-graficos</code>", "informe sin figuras (más rápido para estructuras grandes)"],
                    ["<code>--solo-esquema</code>", "no calcula: dibuja los datos y las cargas para revisarlos"]],
                   clase="datos"))
    p.append(tabla(["Archivo de salida", "Contenido"],
                   [["<code>informe.html</code>", "memoria de cálculo completa (datos, resultados, gráficos, verificaciones)"],
                    ["<code>desplazamientos.csv</code>", "u<sub>z</sub>, φ<sub>x</sub>, φ<sub>y</sub> de cada nodo y caso (ejes globales)"],
                    ["<code>reacciones.csv</code>, <code>resortes.csv</code>", "reacciones de apoyo y fuerzas en resortes"],
                    ["<code>esfuerzos.csv</code>", "V en i y j, T, M en i y j, y M máx/mín con su abscisa, de cada barra (ejes locales)"],
                    ["<code>tensiones.csv</code>", "σ (en i, en j y máxima), τ, σ<sub>VM</sub> y coeficientes de seguridad"],
                    ["<code>matriz_K.csv</code>", "matriz de rigidez ensamblada"]], clase="datos"))

    # 3
    p.append("<h2>3. El archivo de datos (CSV único)</h2>")
    p.append("""<p>Todo va en <b>un solo archivo</b>, dividido en <b>bloques</b>.  Cada bloque empieza con una línea que tiene
solamente su <b>título</b>; la línea siguiente son los <b>encabezados</b> de las columnas y después van los datos.  Las líneas en
blanco y las que empiezan con <code>#</code> se ignoran.  Los títulos pueden ir en mayúsculas o minúsculas, con o sin tildes.
Se aceptan el formato estándar (separador <code>,</code> y punto decimal) y el de Excel en español (separador <code>;</code>
y coma decimal); si el archivo tiene algún <code>;</code>, se usa ese separador.  La codificación puede ser UTF-8 o la de Excel en Windows
(cp1252): si el archivo no es UTF-8 válido, se lee como cp1252.</p>""")
    p.append(tabla(["Bloque", "¿Obligatorio?", "Columnas", "Notas"], [
        ["PROYECTO", "no", "clave ; valor", "proyecto, autor, unidad_fuerza, unidad_longitud, escala_deformada (auto o número), "
                                             "anexo_matrices (auto/si/no), csv_salida (excel_es/estandar), escala_diagramas (barra = cada barra a su propia escala, por defecto; global = una escala única)"],
        ["NODOS", "sí", "id ; x ; y", "coordenadas en el plano"],
        ["MATERIALES", "sí", "id ; E ; nu ; G ; fy ; sadm ; alfa", "cargar G o nu; fy y sadm son opcionales (coeficientes de seguridad); alfa [1/°C] solo si hay cargas térmicas"],
        ["SECCIONES", "sí", "id ; tipo ; d ; t ; b ; h ; I ; J ; A ; c ; Wt ; kv", "según el tipo (tabla siguiente); lo que no aplica queda vacío.  La altura h se usa en las cargas térmicas (en la sección genérica, si falta se toma 2·c)"],
        ["BARRAS", "sí", "id ; nodo_i ; nodo_j ; material ; seccion ; art_i ; art_j", "el eje local xl va de nodo_i a nodo_j; art_i / art_j (opcionales): vacío = rígido, m = articulación de flexión, t = de torsión, mt = ambas"],
        ["APOYOS", "sí", "nodo ; uz ; phix ; phiy", "1 = restringido, 0 = libre.  Puede quedar solo con el encabezado si la estructura se apoya únicamente en resortes"],
        ["RESORTES", "no", "nodo ; kz ; kphix ; kphiy", "rigidez del resorte [F/L] y [F·L/rad]; vacío = sin resorte"],
        ["CARGAS", "no", "caso ; nodo ; Pz ; Mx ; My", "cargas en los nodos; varias filas por caso, las del mismo nodo se suman.  Tiene que haber alguna carga en CARGAS, en CARGAS EN BARRAS o desplazamientos prefijados"],
        ["RESORTES GIRO INCLINADO", "no", "nodo ; k ; angulo", "resorte de torsión con eje en el plano a 'angulo' grados de +X (antihorario): se opone a θa = φx·cosβ + φy·senβ y aporta k·a·aᵀ (a = [cosβ, senβ]) a los GDL φx, φy"],
        ["DESAJUSTE DE RESORTES", "no", "caso ; nodo ; uz ; phix ; phiy", "desplazamiento impuesto al apoyo del resorte recto, positivo en el sentido del GDL; fuerza del resorte = −k·(u − e).  Un resorte más corto que lo proyectado (estirado al conectarlo) tiene e < 0"],
        ["CARGAS EN BARRAS", "no", "caso ; barra ; tipo ; valor ; valor2 ; a ; b", "cargas en el tramo (sección 9): tipo q, P o temp; a y b se miden desde el nodo i"],
        ["DESPLAZAMIENTOS PREFIJADOS", "no", "caso ; nodo ; uz ; phix ; phiy", "solo sobre GDL restringidos en APOYOS (por ejemplo, descenso de un apoyo)"],
        ["COMBINACIONES", "no", "combinacion ; caso ; factor", "una fila por término"],
    ], clase="datos"))
    p.append("<h4>Tipos de sección disponibles</h4>")
    p.append(tabla(["Tipo", "Parámetros", "Fórmulas usadas"], [
        ["tubo", "d (exterior), t", "I = π/64·(d⁴ − (d−2t)⁴);  J = 2I;  A = π/4·(d² − (d−2t)²)"],
        ["circular", "d", "I = πd⁴/64;  J = πd⁴/32"],
        ["rectangular", "b, h  (<b>h vertical</b>)", "I = b·h³/12;  J y τ<sub>t,máx</sub> con las fórmulas de Saint-Venant para rectángulo"],
        ["rect_hueca", "b, h, t  (h vertical)", "I = (b·h³ − b<sub>i</sub>·h<sub>i</sub>³)/12;  J = 4A<sub>m</sub>²·t/p<sub>m</sub> (Bredt);  W<sub>t</sub> = 2A<sub>m</sub>·t"],
        ["generica", "I, J (y opc. A, c, Wt, kv)", "datos cargados directamente; sin c y Wt no se calculan tensiones"]],
        clase="datos", nota="I es la inercia respecto del eje horizontal (flexión por cargas verticales)."))
    p.append("<h4>Ejemplo completo (ejemplo1_voladizo_L.csv)</h4>")
    p.append(f'<pre class="codigo">{e_(ej1)}</pre>')

    # 4
    p.append("<h2>4. Cómo lee y valida los datos</h2>")
    p.append(figura(2, fig_lectura(), "El archivo se parte en bloques; cada bloque se convierte en datos del modelo."))
    p.append("""<ol>
<li><b>Partición en bloques.</b>  Se leen las líneas ignorando comentarios y filas vacías.  Una línea con un solo dato que coincide
con un título válido abre un bloque nuevo; todo lo que sigue pertenece a ese bloque hasta el próximo título.</li>
<li><b>Encabezados.</b>  La primera fila de cada bloque (salvo PROYECTO) da los nombres de columna; el orden de las columnas
no importa y las columnas que no se usan se ignoran.</li>
<li><b>Conversión.</b>  Cada fila se convierte en un objeto: Nodo, Material, Sección, Barra, etc.  Los números aceptan coma o punto decimal.</li>
<li><b>Validaciones</b> (si algo falla el programa se detiene y dice bloque y número de línea):
títulos obligatorios presentes; título mal escrito o repetido; datos antes del primer título; ids repetidos; nodos, materiales y
secciones referenciados que no existen; barras de longitud nula; G o ν presente; desplazamientos prefijados solo en GDL restringidos;
casos de las combinaciones existentes; al menos un apoyo o resorte.</li>
<li><b>Geometría de cada barra.</b>  Se calcula L = √(Δx² + Δy²), γ<sub>1</sub> = Δx/L y γ<sub>2</sub> = Δy/L, que definen el eje local.</li></ol>""")
    p.append('<pre class="codigo">ERROR EN LOS DATOS DE ENTRADA\n  Línea 21: \'BARRA\' parece un título de bloque pero no es válido (o es una fila con un solo dato).  Títulos válidos: PROYECTO, NODOS, ...\n\nERROR EN LOS DATOS DE ENTRADA\n  Bloque BARRAS, línea 25: nodo_j \'9\' no existe en NODOS</pre>')
    p.append("<p class='nota'>Ejemplos de mensajes de error.</p>")

    # 5
    p.append("<h2>5. Modelo de cálculo: ejes, GDL y matriz de la barra</h2>")
    p.append(figura(3, fig_ejes(), "Ejes globales y locales, y grados de libertad nodales."))
    p.append("""<p>Trabajo con dos sistemas de ejes y el código los distingue con sufijos: <code>_glo</code> (globales) y
<code>_loc</code> (locales de la barra).  Las variables globales son las coordenadas, los desplazamientos nodales, las cargas
y las reacciones; las locales son las fuerzas de extremo y los esfuerzos internos de cada barra.</p>
<p><b>Matriz local</b> (barra sobre el eje x<sub>l</sub>; coincide con la "barra según eje X" de la tabla de cátedra):</p>""")
    p.append("""<pre class="codigo">          uz_i    φx_i    φy_i  |  uz_j    φx_j    φy_j
uz_i  [   K1      0      −K2   |  −K1      0      −K2  ]
φx_i  [   0       K       0    |   0      −K       0   ]
φy_i  [  −K2      0       K3   |   K2      0      K3/2 ]
uz_j  [  −K1      0       K2   |   K1      0       K2  ]
φx_j  [   0      −K       0    |   0       K       0   ]
φy_j  [  −K2      0      K3/2  |   K2      0       K3  ]

K = G·J/L      K1 = 12·E·I/L³      K2 = 6·E·I/L²      K3 = 4·E·I/L</pre>""")
    p.append("""<p><b>Rotación.</b>  Con γ<sub>1</sub> = cos α y γ<sub>2</sub> = sen α, los tres GDL de cada nodo se rotan con
R = [1 0 0; 0 γ<sub>1</sub> −γ<sub>2</sub>; 0 γ<sub>2</sub> γ<sub>1</sub>] (v<sub>glo</sub> = R·v<sub>loc</sub>).  Para la barra completa,
T = diag(R, R) y</p>
<pre class="codigo">k_glo = T · k_loc · Tᵀ      (equivale a la "barra general" de la tabla)</pre>
<p>Este resultado se compara en los tests con las fórmulas de la tabla escritas a mano, para 73 ángulos.</p>""")

    # 6
    p.append("<h2>6. Ensamblaje</h2>")
    p.append(figura(4, fig_ensamblaje(), "Ensamblaje de K: cada barra suma su k_glo en los bloques de sus nodos."))
    p.append("""<p>El nodo n ocupa las posiciones 3n, 3n+1 y 3n+2 del vector de desplazamientos.  Para cada barra se
calcula k<sub>glo</sub> (6×6) y se suma en los bloques correspondientes a sus nodos i y j.  Los resortes se suman después en la
<b>diagonal</b> de K, en el GDL que corresponda.</p>""")
    p.append("<h3>6.1 Articulaciones por barra</h3>")
    p.append("""<p>Con <code>art_i</code> / <code>art_j</code> se libera un giro en ese extremo de la barra: <b>m</b> libera el giro de flexión (el momento flector en ese extremo es nulo),
<b>t</b> libera el giro de torsión (el torsor es nulo), <b>mt</b> libera ambos; <code>1</code> o <code>si</code> equivale a <b>m</b>.  Los índices locales liberados son: flexión i → 3, j → 6; torsión i → 2, j → 5
(orden uz, φx, φy en cada extremo).  Se hace <b>condensación estática</b> como en el programa de pórtico plano:</p>
<p style="text-align:center">k<sub>c</sub> = k<sub>AA</sub> − k<sub>AB</sub>·k<sub>BB</sub><sup>−1</sup>·k<sub>BA</sub>,&nbsp;&nbsp; f<sub>0c</sub> = f<sub>0,A</sub> − k<sub>AB</sub>·k<sub>BB</sub><sup>−1</sup>·f<sub>0,B</sub></p>
<p>(A = GDL que se conservan, B = liberados).  Después de resolver, el giro liberado se recupera con u<sub>B</sub> = −k<sub>BB</sub><sup>−1</sup>(k<sub>BA</sub>·u<sub>A</sub> + f<sub>0,B</sub>) y f = k·u + f<sub>0</sub> da el esfuerzo nulo en la articulación.
Si en un nodo los giros quedan sin rigidez (por ejemplo, el extremo libre de una barra articulada), el programa agrega una rigidez ficticia de 10<sup>−6</sup> de la de la barra solo en esa dirección y avisa; no cambia los esfuerzos.
Si hubiera una carga en ese giro sin rigidez, o articulaciones de más, se informa como mecanismo.  Ejemplo: <code>ejemplo10_articulaciones.csv</code> (viga empotrada–apoyada con articulación; M = 0 en la rótula, reacción q·L/2).</p>""")

    # 7
    p.append("<h2>7. Apoyos, resortes, desplazamientos prefijados y solución</h2>")
    p.append(figura(5, fig_particion(), "Partición de K en GDL libres y restringidos y pasos de la solución."))
    p.append("""<p><b>Estabilidad.</b>  Antes de resolver se normaliza K<sub>ff</sub> por su diagonal y se calculan sus autovalores.  Un
autovalor menor que 10<sup>−9</sup> indica un mecanismo: el programa se detiene y nombra los GDL que se mueven libremente.  En un
emparrillado, además de impedir u<sub>z</sub>, hay que impedir el giro alrededor del eje de los tramos rectos (torsión).</p>
<p><b>Desplazamientos prefijados.</b>  El valor impuesto entra como u<sub>r</sub> y su efecto pasa al lado de las cargas
(F<sub>f</sub> − K<sub>fr</sub>·u<sub>r</sub>).  Sirve para descensos de apoyo o giros impuestos, y cada caso puede tener los suyos.</p>
<p><b>Resortes.</b>  Un resorte de rigidez k en un GDL suma k a la diagonal de K.  Permite representar apoyos elásticos (por
ejemplo, k<sub>z</sub>) sin restringir el GDL.  Si el GDL además está restringido, el resorte no tiene efecto y el programa avisa.</p>
<p><b>Combinaciones.</b>  Como el problema es lineal, cada combinación es la suma ponderada de los resultados de los casos.</p>""")

    # 8
    p.append("<h2>8. Esfuerzos y deformada</h2>")
    p.append(figura(6, fig_signos(), "Convención de signos de los esfuerzos internos (ejes locales)."))
    p.append("""<p>Para cada barra se pasan los desplazamientos nodales a ejes locales (u<sub>loc</sub> = Tᵀ·u<sub>glo</sub>) y se calculan las
fuerzas de extremo f<sub>loc</sub> = k<sub>loc</sub>·u<sub>loc</sub> (+ f<sub>0</sub> si hay cargas en el tramo, sección 9).  Sin cargas en el tramo:</p>
<pre class="codigo">V  = Pz_i                 (constante)
T  = −Mx_i                (constante)
M(x) = My_i + x·Pz_i      (lineal;  M en i = My_i,  M en j = My_i + L·Pz_i)</pre>
<p><b>Funciones y diagramas.</b>  El informe da, para cada barra y por tramos (los tramos se parten donde empieza o termina una carga), las
expresiones exactas de V(x) y M(x) con x medido desde el nodo i, y el valor de T.  Los diagramas se dibujan por defecto <b>normalizados a la
escala de cada barra</b> para que se vea la forma aunque los valores sean chicos frente a los de otras barras; lo que vale son los números
rotulados.  Con <code>escala_diagramas;global</code> se usa una escala única.</p>
<p><b>Deformada.</b>  Con cargas solo en los nodos, la elástica de cada barra es exactamente una cúbica (interpolación de Hermite)
definida por u<sub>z</sub> y φ<sub>y</sub> de sus extremos, con φ<sub>y</sub> = −dw/dx.  Por eso la deformada dibujada es la real y no
una poligonal.  Con cargas en el tramo se le suma w<sub>p</sub>(x), la flecha de la barra biempotrada bajo esa carga
(E·I·w<sub>p</sub>'' = M<sub>p</sub>(x), w<sub>p</sub>(0) = w<sub>p</sub>'(0) = 0, que integra el programa numéricamente).  El desplazamiento
vertical se amplifica con un factor que se muestra en la figura.</p>""")

    # 9
    p.append("""<h4>Qué pasa según cómo esté orientada la barra</h4>
<p>La matriz local <code>k_loc</code> es siempre la misma; lo único que cambia con la orientación es la rotación
<code>T(γ1, γ2)</code>.  En una barra según Y los GDL globales φx y φy intercambian su papel: el momento Mx global
<b>flexiona</b> la barra y My global la <b>tuerce</b> (en una barra según X es al revés).  El programa lo resuelve solo,
pero conviene saberlo para interpretar los resultados.</p>
<ul class="conv">
<li><b>Globales:</b> coordenadas, cargas, desplazamientos, reacciones y deformada.</li>
<li><b>Locales:</b> V, T, M, tensiones y, por lo tanto, los diagramas (se dibujan sobre la planta, pero con el valor local de cada barra).</li>
<li><b>Si se invierte i↔j:</b> M y T no cambian; V cambia de signo (su signo se define respecto de x<sub>l</sub>).  Los resultados
físicos, tensiones y coeficientes de seguridad son idénticos.  Un test lo verifica.</li></ul>""")
    # 9 cargas en el tramo
    p.append("<h2>9. Cargas en el tramo (q, P, gradiente térmico)</h2>")
    p.append("""<p>Bloque <code>CARGAS EN BARRAS</code>, una fila por carga: <code>caso ; barra ; tipo ; valor ; valor2 ; a ; b</code>.
Todo se da en los ejes locales de la barra, pero como las cargas son perpendiculares al plano, z local = z global y el signo es el
global: <b>positivo hacia +z (la gravedad es negativa)</b>.  Las posiciones <i>a</i> y <i>b</i> se miden desde el nodo i.</p>""")
    p.append(tabla(["tipo", "valor", "valor2", "a", "b", "qué representa"], [
        ["q", "q en a [F/L]", "q en b (vacío = igual a valor)", "inicio (vacío = 0)", "fin (vacío = L)", "distribuida uniforme, trapecial o parcial"],
        ["P", "P [F]", "–", "posición", "–", "fuerza puntual"],
        ["temp", "ΔT fibra superior [°]", "ΔT fibra inferior [°]", "–", "–", "gradiente térmico en toda la barra; necesita alfa (MATERIALES) y h (SECCIONES)"]],
        clase="datos"))
    p.append(figura(7, fig_metodo_tramo(), "Método de la cátedra (estados 1 y 2) y su equivalente en el programa."))
    p.append("""<p><b>Idea.</b>  El método de la cátedra separa el problema en el <b>estado 1</b> (cada barra cargada, con los extremos
empotrados: fuerzas de empotramiento f<sub>0</sub> y sus diagramas, tabla <i>Estados Biempotrados</i>) y el <b>estado 2</b> (la estructura
con las fuerzas opuestas, −f<sub>0</sub>, aplicadas en los nodos, y los desplazamientos prefijados), para sumarlos.  Hecho a mano tiene
sentido; en la computadora se puede hacer directamente:</p>
<ol>
<li>Para cada carga se calcula <b>F<sub>eq</sub> = ∫ Nᵀ·q dx</b> con las funciones de forma de la viga
N = [H<sub>1</sub>, −L·H<sub>2</sub>, H<sub>3</sub>, −L·H<sub>4</sub>] sobre (u<sub>z,i</sub>, φ<sub>y,i</sub>, u<sub>z,j</sub>, φ<sub>y,j</sub>)
(el signo de H<sub>2</sub> y H<sub>4</sub> sale de φ<sub>y</sub> = −dw/dx).  Da exactamente las fuerzas de la tabla de biempotrados; f<sub>0</sub> = −F<sub>eq</sub>.</li>
<li>Se giran a ejes globales y se suman al vector de cargas: <b>K·u = F + ΣF<sub>eq</sub></b>.  Se resuelve una sola vez, con los desplazamientos
prefijados y resortes como siempre.</li>
<li>Las fuerzas de extremo de cada barra son <b>f = k<sub>loc</sub>·u<sub>loc</sub> + f<sub>0</sub></b>, y las reacciones R = K·u − (F + F<sub>eq</sub>) en los GDL restringidos.</li>
<li>Los diagramas a lo largo de la barra se reconstruyen con las fuerzas de extremo en i y la carga del tramo:
V(x) = P<sub>z,i</sub> + ∫q, M(x) = M<sub>i</sub> + x·P<sub>z,i</sub> + M<sub>q</sub>(x).  De ahí salen también M máx/mín y sus posiciones, y las tensiones se evalúan a lo largo de toda la barra.</li></ol>""")
    p.append(tabla(["Carga (q, P positivas hacia +z)", "Fuerzas de empotramiento f<sub>0</sub> (nodo sobre barra)"], [
        ["q uniforme", "P<sub>z,i</sub> = P<sub>z,j</sub> = −q·L/2;   M<sub>y,i</sub> = +q·L²/12,  M<sub>y,j</sub> = −q·L²/12"],
        ["P a la distancia a (b = L−a)", "P<sub>z,i</sub> = −P·b²(3a+b)/L³;   M<sub>y,i</sub> = +P·a·b²/L²,  M<sub>y,j</sub> = −P·a²·b/L²"],
        ["Gradiente térmico", "M<sub>y,i</sub> = +E·I·α·(ΔT<sub>sup</sub> − ΔT<sub>inf</sub>)/h,  M<sub>y,j</sub> = −M<sub>y,i</sub>;  sin fuerzas"]],
        clase="datos", nota="La q trapecial y la parcial se integran numéricamente (Gauss, exacto para este caso), sin fórmulas especiales."))
    p.append("""<p><b>Térmica.</b>  La curvatura libre por gradiente es κ<sub>T</sub> = α·(ΔT<sub>sup</sub> − ΔT<sub>inf</sub>)/h.  Si los extremos
se impiden, aparece un momento constante E·I·κ<sub>T</sub> (positivo = tracciona abajo, si la fibra superior se calienta más).  La parte
uniforme de la temperatura (ΔT medio) produce solo esfuerzo <b>axil</b>, que el emparrillado no tiene, y por eso no se considera.
La elástica de la barra con gradiente no suma nada extra: la curvatura libre y la restringida se cancelan.</p>
<p><b>Validación.</b>  <code>003_Ejemplos/001_Emparrillado/ejemplo5_parcial2020.csv</code> reproduce el 1er parcial 2020 (q en la viga 1-2, gradiente en la 2-3, resorte y giros
prefijados): cargas equivalentes del estado 2 (−3062,5 N; 1 728 000 y 2 189 229 N·mm), u<sub>z2</sub> = 1,152 mm, φ<sub>y2</sub> = 0,00409, momento de 3,58·10⁶ N·mm
en el nudo 2, 1,687·10⁶ N·mm en el 3 y σ = 59,04 MPa en el empotramiento 3.  Los tests además comparan con soluciones analíticas
(biempotrada con q y con P, voladizo, viga continua de dos tramos, gradiente térmico), giran la estructura y cambian i↔j.</p>
<p><b>Combinaciones.</b>  Cada combinación arrastra las cargas en el tramo de sus casos multiplicadas por el factor, de modo que los diagramas
de la combinación son la suma de los diagramas de los casos.</p>""")

    p.append("<h2>10. Tensiones y coeficientes de seguridad</h2>")
    p.append("""<p>Sin cargas en el tramo el momento es lineal y basta mirar los extremos; con cargas en el tramo se evalúa a lo largo de toda
la barra (se informa también la abscisa del máximo):</p>
<pre class="codigo">σ  = M·c/I            fibra extrema (flexión)
τt = |T|/Wt           contorno (torsión)
τv = kv·|V|/A         eje neutro (corte)
σVM = máx{ √(σ² + 3·τt²)   [fibra extrema],   √3·(τt + τv)   [eje neutro] }

CS fluencia  = fy / σVM
CS admisible = σadm / σVM        (cumple si CS ≥ 1)</pre>
<p><i>f<sub>y</sub></i> y <i>σ<sub>adm</sub></i> se cargan en MATERIALES; si faltan, el coeficiente correspondiente no se calcula.
El criterio de Von Mises es el mismo para ambos; solo cambia el valor de referencia.</p>""")

    # 10
    # 11 visor 3D
    m6 = cargar_modelo(RAIZ / "003_Ejemplos" / "001_Emparrillado" / "ejemplo6_cargas_en_tramos.csv")
    esc6 = [{"nombre": n, "F": F, "cb": [(c, 1.0) for c in m6.cargas_barra.get(n, [])]} for n, F in m6.casos.items()]
    p.append("<h2>11. Vista 3D interactiva</h2>")
    p.append("""<p>Además de la planta, el informe incluye una vista 3D que se <b>gira con el mouse</b> (arrastrar), con zoom
(rueda) y vistas predefinidas (isométrica, planta, frente, lateral); doble clic vuelve a la vista inicial.  Se puede elegir el caso y
mostrar u ocultar cada componente, los valores, los apoyos y la deformada.  Funciona sin internet: el código está dentro del HTML.
Al imprimir, sale la vista que esté en pantalla.  Ejemplo con el ejemplo 6:</p>""")
    p.append(f'<figure>{visor3d.visor_html(m6, esc6, "visor_memoria")}<figcaption>Figura 8. Vista 3D interactiva (ejemplo 6).</figcaption></figure>')
    p.append("""<ul class="conv">
<li><b>Ejes:</b> terna derecha X, Y, Z (el triedro de la esquina gira con la vista).  Todos los giros y momentos siguen la regla de la mano derecha.</li>
<li><b>Colores:</b> <span style="color:#c0392b"><b>Pz, P, q: rojo</b></span> · <span style="color:#1f5fbf"><b>Mx: azul</b></span> ·
<span style="color:#d68910"><b>My: ámbar</b></span>.  Los mismos colores se usan en la planta.</li>
<li><b>Fuerza:</b> flecha simple con la <b>punta en el punto de aplicación</b>, en el sentido de la carga (una carga gravitatoria llega desde arriba).</li>
<li><b>Momento:</b> vector con <b>dos puntas</b>: M<sub>x</sub> a lo largo de X y M<sub>y</sub> a lo largo de Y; si el valor es positivo apunta hacia +X o +Y, si es negativo hacia el otro lado.</li>
<li><b>Una flecha resultante por componente y por nodo</b> (P<sub>z</sub>, M<sub>x</sub>, M<sub>y</sub>: como máximo tres por nodo).</li>
<li><b>Proporcionalidad:</b> todas las fuerzas comparten escala, todos los momentos comparten la suya, y la q (distinta unidad) la propia; las escalas son las mismas
para todos los casos del visor, de modo que se pueden comparar.  Una flecha vista de punta se dibuja como círculo con punto (hacia el lector) o con cruz (hacia atrás).</li>
<li><b>Diagramas:</b> V, T y M dibujados en planta, con la ordenada a la izquierda de i→j para valores positivos; selector «Barra» para ver una sola.  <b>Utilización:</b> σeq/fy (o σeq/σadm) por barra, con el valor al pasar el mouse.  <b>Articulaciones:</b> círculo = flexión, cuadrado = torsión, círculo con punto = ambas.</li>
<li><b>Cargas en el tramo:</b> q como fila de flechas de altura proporcional; P como flecha; el gradiente térmico como rótulo.</li></ul>""")
    p.append("<h2>12. Verificaciones internas</h2>")
    p.append("""<ul class="conv">
<li><b>Equilibrio global</b> de cada caso: ΣFz, ΣMx y ΣMy de cargas + reacciones (apoyos y resortes) deben dar cero.</li>
<li><b>Residuo</b> del sistema K<sub>ff</sub>·u<sub>f</sub> = F<sub>f</sub> − K<sub>fr</sub>·u<sub>r</sub>.</li>
<li><b>Estabilidad</b> (autovalores normalizados), sección 7.</li>
<li><b>Cargas en el tramo:</b> las cargas nodales equivalentes conservan la resultante y su momento; el equilibrio global incluye F<sub>eq</sub>.</li>
<li><b>Tests</b> (<code>python -m unittest discover -s tests -v</code>): matriz contra la tabla (73 ángulos y las 4 particulares),
voladizos y voladizo en L contra la solución analítica, invariancia al rotar la estructura, una parrilla irregular contra un
solver de pórtico espacial 12×12 independiente, resortes, coeficientes de seguridad, lectura del CSV y generación del informe, y las cargas
en el tramo (soluciones analíticas y el examen resuelto de la cátedra).</li></ul>""")

    # 11
    p.append("<h2>13. Estructura del código</h2>")
    p.append(tabla(["Archivo", "Función"], [
        ["<code>struttura.py</code>", "punto de entrada único: elige emparrillado o pórtico según el archivo"],
        ["<code>emparrillado/__main__.py</code>", "línea de comandos, exportación de los CSV de resultados"],
        ["<code>emparrillado/entrada.py</code>", "partición en bloques, lectura, validación; clases Nodo, Material, Barra, Modelo"],
        ["<code>emparrillado/secciones.py</code>", "propiedades de cada tipo de sección"],
        ["<code>emparrillado/barra.py</code>", "matriz local, rotación y matriz global de la barra"],
        ["<code>emparrillado/solver.py</code>", "ensamblaje, estabilidad, solución, reacciones, combinaciones, equilibrio"],
        ["<code>emparrillado/cargas_barra.py</code>", "cargas en el tramo: cargas equivalentes, f<sub>0</sub>, V(x), M(x), flecha particular"],
        ["<code>emparrillado/esfuerzos.py</code>", "V(x), T, M(x), extremos, tensiones, coeficientes de seguridad, elástica"],
        ["<code>emparrillado/graficos.py</code>", "esquema en planta, deformada 3D estática, diagramas (SVG)"],
        ["<code>emparrillado/visor3d.py</code>", "visor 3D interactivo (HTML + JavaScript incluidos en el informe)"],
        ["<code>emparrillado/informe.py</code>", "informe HTML (formato memoria de cálculo, botón imprimir)"],
        ["<code>tests/test_nucleo.py</code>, <code>tests/test_cargas_barra.py</code>", "tests de validación"],
        ["<code>004_Documentacion/003_Generadores/generar_memoria.py</code>", "genera este documento"]], clase="datos"))
    p.append("""<p>Nombres en el código: <code>u_glo</code>/<code>u_loc</code> desplazamientos; <code>k_glo</code>/<code>k_loc</code>
matrices de barra; <code>ub</code> y <code>fb</code> desplazamientos y fuerzas de extremo de cada barra en ejes locales;
<code>R</code> reacciones de apoyo y <code>Rk</code> fuerzas de los resortes (ejes globales).</p>""")

    # 12
    p.append("<h2>14. Cómo agregar cosas (tipos de sección)</h2>")
    p.append("""<p>Los tipos de sección viven en <code>emparrillado/secciones.py</code>, en la función
<code>crear_seccion</code>.  Para agregar uno se suma una rama con sus fórmulas.  Ejemplo con un perfil de tabla:</p>
<pre class="codigo">    if tipo == "perfil_tabla":
        h, I, J, A = _req(p, "h", "I", "J", "A")     # parámetros leídos del CSV
        return Seccion(id_, tipo, f"Perfil h={h:g}", I, J, A, c=h/2)</pre>
<p>Cada sección debe entregar I, J y, si se quieren tensiones, A, c, W<sub>t</sub> y k<sub>v</sub>.  Después conviene agregar un test
en <code>tests/test_nucleo.py</code> con un caso conocido, y sumar el tipo a la tabla de la sección 3.</p>""")

    # 13
    p.append("<h2>15. Limitaciones y próximos pasos</h2>")
    p.append("""<ul class="conv">
<li>Cargas en el tramo: q (uniforme, trapecial, parcial), P puntual y gradiente térmico.  No hay momentos ni torsores concentrados o distribuidos dentro del tramo,
ni la parte uniforme de la temperatura (produce solo axil, que el emparrillado no tiene).</li>
<li>Sin apoyos inclinados.  Las articulaciones por barra (flexión y/o torsión) sí existen, ver 6.1.</li>
<li>Diagramas dibujados sobre la planta; a futuro, en el plano propio de cada barra.</li>
<li>Más tipos de sección (perfiles doble T, ángulos) y, más adelante, una interfaz gráfica.</li>
<li>Matriz densa: adecuada para hasta unos cientos de nodos.</li>
<li>Tensiones con fórmulas de resistencia de materiales; no incluye concentración de tensiones ni pandeo.</li></ul>""")
    from _comun import seccion_comun
    p.append(seccion_comun("emparrillado"))
    return "\n".join(p)


if __name__ == "__main__":
    salida = RAIZ / "004_Documentacion" / "002_Memorias" / "Struttura_Memoria_emparrillado.html"
    salida.write_text(documento("Memoria del programa – Emparrillado plano", cuerpo(), boton=True, visor=True), encoding="utf-8")
    print("Escrito:", salida)
