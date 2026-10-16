"""Informe HTML autocontenido con formato de memoria de cálculo (sobrio, imprimible)."""
from __future__ import annotations

import datetime
import html

import numpy as np

from .. import __version__
from . import graficos, visor3d
from ..falla_plana import rotulos
from .barra import descripcion_articulacion, matriz_rotacion
from .entrada import Modelo
from .esfuerzos import esfuerzos, funciones_barra, tensiones
from .formato import fe, fg, limpiar
from .solver import Info, Resultado, equilibrio

e_ = html.escape

CSS = """
@page { size: A4; margin: 0; }
html, body { margin: 0; padding: 0; background: #fff; }
body { font-family: "Times New Roman", "Liberation Serif", Georgia, serif; font-size: 11pt;
       color: #000; line-height: 1.35; }
table.hoja { width: 100%; border-collapse: collapse; table-layout: fixed; }
table.hoja > thead > tr > td, table.hoja > tbody > tr > td, table.hoja > tfoot > tr > td
   { padding: 0; border: 0; text-align: left; vertical-align: top; }
.esp { height: 14mm; }
.contenido { max-width: 186mm; margin: 0 auto; padding: 0 6mm; }
.contenido h1 { font-size: 18pt; text-align: center; margin: 0 0 4pt; }
.sub { text-align: center; font-size: 10.5pt; margin-bottom: 10pt; border-bottom: 2px solid #000; padding-bottom: 6pt; }
.contenido h2 { font-size: 14pt; border-bottom: 1px solid #000; margin: 22pt 0 6pt; padding-bottom: 2pt; }
.contenido h3 { font-size: 12pt; margin: 14pt 0 4pt; }
.contenido h4 { font-size: 11pt; font-style: italic; margin: 10pt 0 2pt; }
.contenido h2, .contenido h3, .contenido h4 { page-break-after: avoid; break-after: avoid; }
.contenido table { border-collapse: collapse; margin: 4pt 0 10pt; font-size: 9.5pt; }
.contenido th, .contenido td { padding: 1.5pt 9pt; text-align: center; }
.contenido th { border-top: 1.5px solid #000; border-bottom: 1px solid #000; font-weight: bold; }
.contenido tr:last-child td { border-bottom: 1.5px solid #000; }
.contenido td.n { text-align: right; font-variant-numeric: tabular-nums; }
.contenido td.t { text-align: left; }
.contenido table.datos td:first-child { text-align: left; font-weight: bold; }
.contenido table.datos td:nth-child(2) { text-align: left; }
.contenido table.funciones { font-size: 9pt; }
.contenido table.funciones td { text-align: left; white-space: nowrap; }
.contenido table.matriz { font-size: 7pt; }
.contenido table.matriz th, .contenido table.matriz td { padding: 1pt 4pt; }
.contenido figure { margin: 8pt 0 12pt; page-break-inside: avoid; text-align: center; }
.contenido figure svg { max-width: 100%; height: auto; }
.contenido figcaption { font-size: 9.5pt; font-style: italic; }
.nota { font-size: 9.5pt; margin: 2pt 0 8pt; }
.ok { font-weight: bold; }
.aviso { border: 1px solid #000; padding: 4pt 8pt; font-size: 10pt; margin: 6pt 0; }
ul.conv { margin: 2pt 0 8pt 16pt; padding: 0; font-size: 10.5pt; }
pre.codigo { font-family: "Courier New", "Liberation Mono", monospace; font-size: 8.5pt; border: 1px solid #000;
             padding: 5pt 8pt; overflow-x: auto; page-break-inside: avoid; line-height: 1.25; }
code { font-family: "Courier New", "Liberation Mono", monospace; font-size: 9.5pt; }
.caso { page-break-before: always; }
.scroll { overflow-x: auto; }
.boton-imprimir { text-align: center; margin: 22pt 0 10pt; }
.boton-imprimir button { font-family: inherit; font-size: 11pt; padding: 5pt 22pt; border: 1px solid #000;
                         background: #f2f2f2; cursor: pointer; }
.boton-imprimir button:hover { background: #e2e2e2; }
@media print { .contenido { max-width: none; padding: 0 14mm; } .no-print { display: none !important; } }
""" + visor3d.CSS


def documento(titulo: str, cuerpo: str, boton: bool = True, visor: bool = False) -> str:
    """Envuelve el cuerpo en una página HTML.  Los márgenes se logran con la tabla 'hoja'
    (thead/tfoot se repiten en cada página impresa) y @page{margin:0}: así los navegadores
    basados en Chromium no imprimen fecha, título ni URL en los bordes."""
    b = ('<div class="boton-imprimir no-print"><button onclick="window.print()">Imprimir</button>'
         '<div class="nota">Si el navegador agrega fecha o título en los bordes, desactivar '
         '"Encabezados y pies de página" en el diálogo de impresión.</div></div>') if boton else ""
    return (f"<!DOCTYPE html><html lang='es'><head><meta charset='utf-8'><title>{e_(titulo)}</title>"
            f"<style>{CSS}</style>" + (f"<script>{visor3d.LIB_JS}</script>" if visor else "") + "</head><body>"
            '<table class="hoja"><thead><tr><td><div class="esp"></div></td></tr></thead><tbody><tr><td>'
            f'<div class="contenido">{cuerpo}{b}</div>'
            '</td></tr></tbody><tfoot><tr><td><div class="esp"></div></td></tr></tfoot></table></body></html>')


def tabla(cab, filas, num=(), clase="", nota=None) -> str:
    """cab: lista de encabezados (HTML permitido).  filas: lista de listas de str.
    num: índices de columnas numéricas (alineadas a la derecha)."""
    num = set(num)
    h = [f'<table class="{clase}">', "<thead><tr>" + "".join(f"<th>{c}</th>" for c in cab) + "</tr></thead><tbody>"]
    for f in filas:
        celdas = "".join(f'<td class="{"n" if i in num else ""}">{c}</td>' for i, c in enumerate(f))
        h.append(f"<tr>{celdas}</tr>")
    h.append("</tbody></table>")
    if nota:
        h.append(f'<p class="nota">{nota}</p>')
    return "\n".join(h)


def unidad_tension(fuerza: str, longitud: str) -> str:
    tabla_u = {("N", "mm"): "MPa", ("kN", "cm"): "kN/cm²", ("N", "m"): "Pa", ("kN", "m"): "kPa",
               ("kgf", "cm"): "kgf/cm²", ("kN", "mm"): "GPa", ("N", "cm"): "N/cm²"}
    return tabla_u.get((fuerza, longitud), f"{fuerza}/{longitud}²")


def _unidades(modelo):
    f, l = modelo.config["unidad_fuerza"], modelo.config["unidad_longitud"]
    return {"F": f, "L": l, "M": f"{f}·{l}", "S": unidad_tension(f, l), "E": unidad_tension(f, l)}


def _figura(svg, caption, num):
    return f'<figure>{svg}<figcaption>Figura {num}. {caption}</figcaption></figure>'


# --------------------------------------------------------------------------
GDL_H = ("u<sub>z</sub>", "φ<sub>x</sub>", "φ<sub>y</sub>")


def _cabecera(modelo, U, titulo_doc):
    cfg = modelo.config
    p = [f"<h1>{titulo_doc}</h1><div class='sub'>{e_(cfg['proyecto'])}</div>"]
    filas = [["Proyecto", e_(cfg["proyecto"])]]
    if cfg["autor"]:
        filas.append(["Autor", e_(cfg["autor"])])
    filas += [["Fecha", datetime.date.today().strftime("%d/%m/%Y")],
              ["Archivo de datos", e_(modelo.archivo.name)],
              ["Programa", f"Struttura {__version__}"],
              ["Unidades", f"fuerza [{U['F']}], longitud [{U['L']}], momento [{U['M']}], tensión [{U['S']}]"],
              ["Método", "Método matricial de rigidez, 3 GDL por nodo (u<sub>z</sub>, φ<sub>x</sub>, φ<sub>y</sub>)"],
              ["Datos", f"{modelo.n} nodos, {len(modelo.barras)} barras, {len(modelo.casos)} caso(s) de carga"
                        + (f", {sum(len(v) for v in modelo.cargas_barra.values())} carga(s) en tramos"
                           if modelo.cargas_barra else "")
                        + (f", {len(modelo.combinaciones)} combinación(es)" if modelo.combinaciones else "")]]
    p.append(tabla(["Dato", "Valor"], filas, clase="datos"))
    for a in modelo.avisos:
        p.append(f'<div class="aviso"><b>Aviso:</b> {e_(a)}</div>')
    return p


def _convenciones() -> str:
    return """<h2>1. Convenciones</h2>
<ul class="conv">
<li><b>Ejes globales:</b> X hacia la derecha, Y hacia arriba en la planta, z fuera del plano
(hacia el lector), terna derecha.  Las cargas <i>Pz</i> son positivas hacia +z; las cargas
gravitatorias son <b>negativas</b>.  Los momentos y giros son vectores (regla de la mano derecha):
<i>Mx</i>, <i>φx</i> alrededor de X; <i>My</i>, <i>φy</i> alrededor de Y.</li>
<li><b>GDL por nodo</b> (ejes globales): u<sub>z</sub>, φ<sub>x</sub>, φ<sub>y</sub>.
Desplazamientos, reacciones y cargas se informan en ejes <b>globales</b>.</li>
<li><b>Ejes locales de barra:</b> x<sub>l</sub> de i a j; y<sub>l</sub> a 90° antihorario de x<sub>l</sub>;
z común.  γ<sub>1</sub> = cos α = Δx/L, γ<sub>2</sub> = sen α = Δy/L.
Rotación: v<sub>glo</sub> = R·v<sub>loc</sub>, con R = [1 0 0; 0 γ<sub>1</sub> −γ<sub>2</sub>; 0 γ<sub>2</sub> γ<sub>1</sub>].
Los esfuerzos internos se informan en ejes <b>locales</b>.</li>
<li><b>Esfuerzos:</b> <i>V</i> cortante (positivo si sobre la cara +x<sub>l</sub> actúa una fuerza hacia −z);
<i>T</i> torsor (positivo si su vector momento coincide con +x<sub>l</sub> en la cara +x<sub>l</sub>);
<i>M</i> flector (positivo si traccionan las fibras inferiores, lado −z).</li>
<li><b>Sentido i→j:</b> el signo de V depende del orden en que se cargaron los nodos de cada barra (invertirlo cambia el signo de V, no el de T ni el de M, ni ningún resultado físico).
Las posiciones <i>a</i> y <i>b</i> de las cargas en el tramo se miden desde el nodo i.</li>
<li><b>Cargas en el tramo:</b> se reemplazan por cargas nodales equivalentes <i>consistentes</i> (integrando las funciones de forma de la viga);
las fuerzas de extremo de barra son <i>f = k·u + f<sub>0</sub></i>, con <i>f<sub>0</sub></i> las fuerzas de empotramiento perfecto.
Los diagramas de V y M se reconstruyen sumando la carga del tramo.  El gradiente térmico (ΔT<sub>sup</sub> − ΔT<sub>inf</sub>)/h
produce un momento de empotramiento E·I·α·(ΔT<sub>sup</sub> − ΔT<sub>inf</sub>)/h; su parte uniforme genera solo esfuerzo axil y no se considera.</li>
<li><b>Reacciones:</b> fuerza/momento que el apoyo (o el resorte) ejerce sobre la estructura, en ejes globales.</li>
<li><b>Diagramas:</b> dibujados sobre la planta con la ordenada perpendicular a la barra, hacia la izquierda
de i→j para valores positivos; cada valor está rotulado.</li></ul>"""


def _datos(modelo, U, fig, con_graficos, fig_visor=None):
    """Sección 2 (datos de entrada).  Devuelve lista de fragmentos HTML."""
    p = ["<h2>2. Datos de entrada</h2>"]
    sec = [0]
    fig_visor = fig_visor or (lambda escenas, cap: "")

    def h3(t):
        sec[0] += 1
        p.append(f"<h3>2.{sec[0]} {t}</h3>")

    if con_graficos:
        h3("Esquema de la estructura")
        p.append(fig(graficos.fig_esquema(modelo), "Planta: numeración de nodos y barras, apoyos y resortes."))
    h3("Nodos")
    p.append(tabla(["Nodo", f"x [{U['L']}]", f"y [{U['L']}]", "Vínculos (GDL restringidos)"],
                   [[e_(n.id), fg(n.x), fg(n.y),
                     ", ".join(nm for nm, f in zip(GDL_H, modelo.restr[k]) if f) or "libre"]
                    for k, n in enumerate(modelo.nodos)], num=(1, 2)))
    h3("Materiales")
    hay_alfa = any(m.alfa for m in modelo.materiales.values())
    p.append(tabla(["Material", f"E [{U['E']}]", f"G [{U['E']}]", "ν", f"f<sub>y</sub> [{U['S']}]",
                    f"σ<sub>adm</sub> [{U['S']}]"] + (["α [1/°]"] if hay_alfa else []),
                   [[e_(m.id), fg(m.E), fg(m.G), fg(m.nu) if m.nu is not None else "–",
                     fg(m.fy) if m.fy else "–", fg(m.sadm) if m.sadm else "–"]
                    + ([fg(m.alfa) if m.alfa else "–"] if hay_alfa else [])
                    for m in modelo.materiales.values()], num=range(1, 7 if hay_alfa else 6)))
    fuentes = [f"<b>{e_(m.id)}</b>: {e_(m.fuente)}" for m in modelo.materiales.values() if m.fuente]
    if fuentes:
        p.append("<p class='nota'>Datos tomados de la biblioteca de materiales (valores típicos de la ficha, no garantizados): " + "; ".join(fuentes) + ".</p>")
    if getattr(modelo, "peso_propio", None):
        pp = modelo.peso_propio
        how = "mitad del peso de cada barra aplicada en cada nudo extremo (las barras son bielas)" if pp.get("nodal") else "carga distribuida uniforme ρ·g·A en cada barra"
        p.append(f"<p class='nota'>Peso propio incluido en el caso <b>{e_(pp['caso'])}</b> (gravedad {e_(pp['gravedad'])}): {how}.  "
                 f"Masa total de las barras = {fg(pp['masa'], 4)} kg, peso = {fg(pp['peso'], 4)} {U['F']}.</p>")
    h3("Secciones")
    L2, L3, L4 = U["L"] + "²", U["L"] + "³", U["L"] + "⁴"
    hay_temp = any(c.tipo == "temp" for lst in modelo.cargas_barra.values() for c in lst)
    p.append(tabla(["Sección", "Descripción", f"I [{L4}]", f"J [{L4}]", f"A [{L2}]", f"c [{U['L']}]",
                    f"W<sub>t</sub> [{L3}]"] + ([f"h [{U['L']}]"] if hay_temp else []),
                   [[e_(s.id), e_(s.descripcion), fg(s.I), fg(s.J), fg(s.A), fg(s.c), fg(s.Wt)]
                    + ([fg(s.h)] if hay_temp else [])
                    for s in modelo.secciones.values()], num=range(2, 8 if hay_temp else 7)))
    p.append('<p class="nota">I: inercia a flexión respecto del eje horizontal; J: constante de torsión de '
             'Saint-Venant; c: distancia a la fibra extrema; W<sub>t</sub>: módulo resistente a torsión.</p>')
    h3("Barras")
    p.append(tabla(["Barra", "i", "j", f"L [{U['L']}]", "α [°]", "γ<sub>1</sub>", "γ<sub>2</sub>", "Material", "Sección", "Articulación"],
                   [[e_(b.id), e_(modelo.nodos[b.i].id), e_(modelo.nodos[b.j].id), fg(b.L), fg(b.angulo_deg, 5),
                     f"{b.g1:.5f}", f"{b.g2:.5f}", e_(b.mat.id), e_(b.sec.id),
                     " y ".join(f"{descripcion_articulacion(a)} {t}" for t, a in (("en i", b.art_i), ("en j", b.art_j)) if a) or "–"]
                    for b in modelo.barras],
                   num=(3, 4, 5, 6)))
    if modelo.res_mask.any():
        h3("Resortes")
        filas = []
        for k, n in enumerate(modelo.nodos):
            if modelo.resortes[k].any():
                filas.append([e_(n.id)] + [fg(v) if v > 0 else "–" for v in modelo.resortes[k]])
        if filas:
            p.append(tabla(["Nodo", f"k<sub>z</sub> [{U['F']}/{U['L']}]", f"k<sub>φx</sub> [{U['M']}/rad]",
                            f"k<sub>φy</sub> [{U['M']}/rad]"], filas, num=(1, 2, 3),
                           nota="Resortes lineales concentrados en el nodo, uno por GDL; '–': sin resorte."))
        if modelo.resortes_giro:
            p.append(tabla(["Nodo", f"k [{U['M']}/rad]", "Eje del resorte (ángulo desde +X)", "Ejes globales"],
                           [[e_(sp["id"]), fg(sp["k"]), f"{fg(sp['beta'], 5)}°",
                             f"a = (cos β, sen β) = ({np.cos(np.radians(sp['beta'])):.4f}, {np.sin(np.radians(sp['beta'])):.4f})"]
                            for sp in modelo.resortes_giro], num=(1,),
                           nota="Resortes de giro con eje en el plano, inclinado respecto de X: se oponen a la componente del giro "
                                "θ<sub>a</sub> = φ<sub>x</sub>·cos β + φ<sub>y</sub>·sen β; aportan k·a·aᵀ a la matriz de rigidez (términos φx-φy incluidos)."))
        if any(np.any(A != 0) for A in modelo.desaj.values()):
            filas = []
            for nombre, A in modelo.desaj.items():
                for k, n in enumerate(modelo.nodos):
                    if np.any(A[k] != 0):
                        filas.append([e_(nombre), e_(n.id)] + [fg(v) if v != 0 else "–" for v in A[k]])
            p.append(tabla(["Caso", "Nodo", f"e<sub>z</sub> [{U['L']}]", "e<sub>φx</sub> [rad]", "e<sub>φy</sub> [rad]"], filas,
                           num=(2, 3, 4),
                           nota="Desajuste de resortes: desplazamiento impuesto al apoyo (extremo fijo) del resorte, positivo hacia el sentido "
                                "positivo del GDL.  La fuerza del resorte es −k·(u − e).  Un resorte más corto que lo proyectado (estirado al "
                                "conectarlo) tiene e < 0."))
    if con_graficos:
        h3("Vista 3D de las cargas")
        p.append(fig_visor([{"nombre": nombre, "F": F, "cb": [(c, 1.0) for c in modelo.cargas_barra.get(nombre, [])]}
                            for nombre, F in modelo.casos.items()],
                           "Vista 3D (arrastrar con el mouse para girar; rueda: zoom; doble clic: vista inicial). "
                           "Pz rojo, Mx azul, My ámbar; longitudes proporcionales."))
    h3("Cargas nodales")
    filas = []
    for nombre, F in modelo.casos.items():
        for k, n in enumerate(modelo.nodos):
            if np.any(F[k] != 0):
                filas.append([e_(nombre), e_(n.id), fg(F[k, 0]), fg(F[k, 1]), fg(F[k, 2])])
    if not filas:
        filas = [["–", "–", "–", "–", "–"]]
    p.append(tabla(["Caso", "Nodo", f"P<sub>z</sub> [{U['F']}]", f"M<sub>x</sub> [{U['M']}]", f"M<sub>y</sub> [{U['M']}]"],
                   filas, num=(2, 3, 4), nota="Ejes globales; P<sub>z</sub> positivo hacia +z."))
    if modelo.cargas_barra:
        h3("Cargas en barras (en el tramo)")
        filas = []
        for nombre, lista in modelo.cargas_barra.items():
            for c in lista:
                if c.tipo == "q":
                    filas.append([e_(nombre), e_(c.barra_id), "q distribuida", fg(c.v1), fg(c.v2), fg(c.a), fg(c.b)])
                elif c.tipo == "P":
                    filas.append([e_(nombre), e_(c.barra_id), "P puntual", fg(c.v1), "–", fg(c.a), "–"])
                else:
                    filas.append([e_(nombre), e_(c.barra_id), "gradiente térmico", fg(c.v1), fg(c.v2), "–", "–"])
        p.append(tabla(["Caso", "Barra", "Tipo", "Valor 1", "Valor 2", f"a [{U['L']}]", f"b [{U['L']}]"], filas,
                       num=(3, 4, 5, 6),
                       nota=f"Ejes locales de la barra (z local = z global); a y b se miden desde el nodo i.  "
                            f"<b>q</b> [{U['F']}/{U['L']}]: Valor 1 = q en a, Valor 2 = q en b (varía linealmente), positiva hacia +z.  "
                            f"<b>P</b> [{U['F']}]: fuerza puntual en a, positiva hacia +z.  "
                            f"<b>Gradiente térmico</b>: Valor 1 = ΔT de la fibra superior, Valor 2 = ΔT de la fibra inferior [°]; "
                            f"toda la barra."))
    hay_pref = any(np.any(A != 0) for A in modelo.prefij.values())
    if hay_pref:
        h3("Desplazamientos prefijados")
        filas = []
        for nombre, A in modelo.prefij.items():
            for k, n in enumerate(modelo.nodos):
                if np.any(A[k] != 0):
                    filas.append([e_(nombre), e_(n.id)] + [fg(v) if modelo.restr[k, c] else "–"
                                                           for c, v in enumerate(A[k])])
        p.append(tabla(["Caso", "Nodo", f"u<sub>z</sub> [{U['L']}]", "φ<sub>x</sub> [rad]", "φ<sub>y</sub> [rad]"],
                       filas, num=(2, 3, 4),
                       nota="Valores impuestos a GDL restringidos (por ejemplo, descenso de un apoyo). "
                            "Un caso puede tener solo desplazamientos prefijados y ninguna carga."))
    if modelo.combinaciones:
        h3("Combinaciones")
        filas = [[e_(n), " + ".join(f"{fg(f)}·{e_(c)}" for c, f in lista)] for n, lista in modelo.combinaciones.items()]
        p.append(tabla(["Combinación", "Definición"], filas))
    return p


def _poli(P, cifras=5) -> str:
    """Polinomio en x como HTML:  a + b·x + c·x² + d·x³  (descarta coeficientes que son ruido numérico)."""
    c = np.array(P.coef, dtype=float)
    m = np.abs(c).max() if c.size else 0.0
    partes = []
    for n, v in enumerate(c):
        # un coeficiente de grado n es despreciable si su aporte máximo en el tramo es ínfimo (se decide por magnitud relativa)
        if v == 0.0 or abs(v) < 1e-14 * max(m, 1e-300):
            continue
        x = "" if n == 0 else ("·x" if n == 1 else f"·x<sup>{n}</sup>")
        partes.append((v, x))
    if not partes:
        return "0"
    s = ""
    for i, (v, x) in enumerate(partes):
        mag = fg(abs(v), cifras)
        if i == 0:
            s += ("−" if v < 0 else "") + mag + x
        else:
            s += (" − " if v < 0 else " + ") + mag + x
    return s


def _resortes_caso(modelo, res, U):
    filas = []
    mask = modelo.res_mask
    for k, n in enumerate(modelo.nodos):
        if mask[k].any():
            Rk = limpiar(res.Rk[:, 0]), limpiar(res.Rk[:, 1]), limpiar(res.Rk[:, 2])
            filas.append([e_(n.id)] + [fg(Rk[c][k], 5) if mask[k, c] else "–" for c in range(3)])
    return filas


# --------------------------------------------------------------------------
def generar_html(modelo: Modelo, resultados: dict, info: Info, con_graficos: bool = True, sold: dict | None = None) -> str:
    U = _unidades(modelo)
    cfg = modelo.config
    fig_n = [0]

    def fig(svg, cap):
        fig_n[0] += 1
        return _figura(svg, cap, fig_n[0])

    vis_n = [0]

    def fig_visor(escenas, cap):
        vis_n[0] += 1
        return f'<figure>{visor3d.visor_html(modelo, escenas, f"visor{vis_n[0]}")}<figcaption>{cap}</figcaption></figure>'

    p = _cabecera(modelo, U, "Memoria de cálculo – Emparrillado plano")
    p.append(_convenciones())
    p += _datos(modelo, U, fig, con_graficos, fig_visor)

    # ---------------------------------------------------------------- 3. resultados
    p.append("<h2>3. Resultados</h2>")
    p.append('<p class="nota">Las combinaciones se obtienen por superposición lineal de los resultados de los casos '
             '(desplazamientos, reacciones y esfuerzos); las tensiones se calculan sobre los esfuerzos combinados.</p>')
    for idx_r, (nombre, res) in enumerate(resultados.items(), 1):
        p.append(f'<div class="caso"><h3>3.{idx_r} {"Combinación" if res.combo else "Caso"}: {e_(nombre)}</h3>')
        if res.combo:
            p.append('<p class="nota">' + " + ".join(f"{fg(f)}·{e_(c)}" for c, f in res.combo) + "</p>")
        esf = esfuerzos(modelo, res)
        ten = tensiones(modelo, esf)

        u = np.column_stack([limpiar(res.u[:, c]) for c in range(3)])
        p.append("<h4>Desplazamientos nodales (ejes globales)</h4>")
        p.append(tabla(["Nodo", f"u<sub>z</sub> [{U['L']}]", "φ<sub>x</sub> [rad]", "φ<sub>y</sub> [rad]"],
                       [[e_(n.id), fe(u[k, 0]), fe(u[k, 1]), fe(u[k, 2])] for k, n in enumerate(modelo.nodos)],
                       num=(1, 2, 3)))
        R = np.column_stack([limpiar(res.R[:, c]) for c in range(3)])
        filas = []
        for k, n in enumerate(modelo.nodos):
            if modelo.restr[k].any():
                filas.append([e_(n.id)] + [fg(R[k, c], 5) if modelo.restr[k, c] else "–" for c in range(3)])
        if filas:
            p.append("<h4>Reacciones de apoyo (ejes globales)</h4>")
            p.append(tabla(["Nodo", f"R<sub>z</sub> [{U['F']}]", f"M<sub>x</sub> [{U['M']}]", f"M<sub>y</sub> [{U['M']}]"],
                           filas, num=(1, 2, 3)))
        filas = _resortes_caso(modelo, res, U)
        if filas:
            p.append("<h4>Fuerzas en los resortes (ejes globales)</h4>")
            p.append(tabla(["Nodo", f"F<sub>z</sub> [{U['F']}]", f"M<sub>x</sub> [{U['M']}]", f"M<sub>y</sub> [{U['M']}]"],
                           filas, num=(1, 2, 3),
                           nota="Fuerza que el resorte ejerce sobre la estructura (= −k·(u − e); e = desajuste, 0 si no se dio)."))
        con_tramo = bool(res.cb)
        V, Vj, T, Mi, Mj = (limpiar(esf[k]) for k in ("V", "Vj", "T", "Mi", "Mj"))
        p.append("<h4>Esfuerzos en barras (ejes locales)</h4>")
        if con_tramo:
            filas = []
            for k, b in enumerate(modelo.barras):
                tiene = any(c.barra == k for c, _ in res.cb)
                ext = ([f"{fg(esf['Mmax'][k], 5)} (x={fg(esf['xMmax'][k], 4)})",
                        f"{fg(esf['Mmin'][k], 5)} (x={fg(esf['xMmin'][k], 4)})"] if tiene else ["–", "–"])
                filas.append([e_(b.id), f"{e_(modelo.nodos[b.i].id)}–{e_(modelo.nodos[b.j].id)}",
                              fg(V[k]), fg(Vj[k]), fg(T[k]), fg(Mi[k]), fg(Mj[k])] + ext)
            p.append(tabla(["Barra", "i–j", f"V en i [{U['F']}]", f"V en j [{U['F']}]", f"T [{U['M']}]",
                            f"M en i [{U['M']}]", f"M en j [{U['M']}]", f"M máx [{U['M']}]", f"M mín [{U['M']}]"],
                           filas, num=(2, 3, 4, 5, 6),
                           nota="Con cargas en el tramo: V(x) = P<sub>z,i</sub> + ∫q, M(x) = M<sub>i</sub> + x·P<sub>z,i</sub> + M<sub>q</sub>(x); "
                                "V en i y en j son los valores en los extremos, y M máx / M mín los extremos a lo largo de la barra "
                                "(con su abscisa x medida desde i; '–': barra sin cargas en el tramo, ahí los extremos son los de i y j). "
                                "El torsor T es constante (no hay torsores distribuidos).  Ejes locales de cada barra (x<sub>l</sub> de i a j)."))
        else:
            p.append(tabla(["Barra", "i–j", f"V [{U['F']}]", f"T [{U['M']}]", f"M en i [{U['M']}]", f"M en j [{U['M']}]"],
                           [[e_(b.id), f"{e_(modelo.nodos[b.i].id)}–{e_(modelo.nodos[b.j].id)}",
                             fg(V[k]), fg(T[k]), fg(Mi[k]), fg(Mj[k])] for k, b in enumerate(modelo.barras)],
                           num=(2, 3, 4, 5),
                           nota="Sin cargas en los tramos: V y T constantes, M lineal entre los extremos.  V, T y M están en los ejes locales de cada barra (x<sub>l</sub> de i a j): si se invierte el orden i–j de una barra, V cambia de signo y T y M no cambian; el resultado físico es el mismo."))
        # funciones de esfuerzos
        p.append("<h4>Funciones de esfuerzos de cada barra (ejes locales)</h4>")
        filas = []
        for k, b in enumerate(modelo.barras):
            for sg in funciones_barra(modelo, res, k):
                filas.append([e_(b.id), f"{fg(sg['x0'], 5)} ≤ x ≤ {fg(sg['x1'], 5)}", _poli(sg["V"]), _poli(sg["M"]),
                              fg(limpiar([sg["T"]])[0], 5)])
        p.append(tabla(["Barra", f"Tramo [{U['L']}]", f"V(x) [{U['F']}]", f"M(x) [{U['M']}]", f"T [{U['M']}]"], filas,
                       clase="funciones",
                       nota=f"x se mide desde el nodo i de cada barra, en [{U['L']}]; ejes y signos locales (ver convenciones).  "
                            "Los coeficientes se dan con 5 cifras significativas.  T es constante en toda la barra."))
        # tensiones
        filas, sin_datos = [], False
        rot = rotulos(modelo)
        f4 = lambda v: fg(v, 4) if v is not None else "–"
        for k, (b, t) in enumerate(zip(modelo.barras, ten)):
            if t["vm"] is None:
                sin_datos = True
            fila = [e_(b.id), f4(t["sig_i"]), f4(t["sig_j"])]
            if con_tramo:
                fila.append(f"{fg(t['sig_max'], 4)} (x={fg(t['x_sig_max'], 4)})" if t["sig_max"] is not None else "–")
            fila += [f4(t["tau_t"]), f4(t["tau_v"]), f4(t["vm"]), fg(t["n_fy"], 3) if t["n_fy"] else "–",
                     fg(t["n_adm"], 3) if t["n_adm"] else "–"]
            filas.append(fila)
        p.append("<h4>Tensiones y coeficientes de seguridad</h4>")
        nota = (f"σ = M·c/I en la fibra extrema (+ = tracción en la fibra inferior); τ<sub>t</sub> = |T|/W<sub>t</sub>; "
                f"τ<sub>v</sub> = k<sub>v</sub>·|V|/A en el eje neutro (máximo de la barra).  σ<sub>VM</sub>: máximo entre la fibra extrema "
                f"(√(σ²+3τ<sub>t</sub>²)) y el eje neutro (√3·(τ<sub>t</sub>+τ<sub>v</sub>)), evaluado "
                + ("a lo largo de toda la barra (hay cargas en el tramo)" if con_tramo else "en ambos extremos de la barra")
                + f".  CS fluencia = f<sub>y</sub>/σ<sub>VM</sub>;  CS admisible = σ<sub>adm</sub>/σ<sub>eq</sub> "
                f"(cumple si ≥ 1).  Tensiones en [{U['S']}].{rot['nota']}")
        if sin_datos:
            nota += "  '–': la sección no tiene datos suficientes (c y W<sub>t</sub>)."
        cab = ["Barra", "σ en i", "σ en j"] + (["σ máx (x)"] if con_tramo else []) + \
              ["τ<sub>t</sub>", "τ<sub>v</sub>", rot["eq"], rot["cs"], "CS admisible"]
        p.append(tabla(cab, filas, num=range(1, len(cab)), nota=nota))
        vms = [(t["vm"], b.id) for b, t in zip(modelo.barras, ten) if t["vm"] is not None]
        if vms:
            vm, bid = max(vms)
            txt = f'Tensión {rot["nombre"]} máxima: <b>{fg(vm, 4)} {U["S"]}</b> en la barra {e_(bid)}.'
            for clave, rotulo in (("n_fy", "a fluencia"), ("n_adm", "respecto de la tensión admisible")):
                cs = [(t[clave], b.id) for b, t in zip(modelo.barras, ten) if t[clave]]
                if cs:
                    c_min, b_min = min(cs)
                    estado = "cumple" if c_min >= 1 else "<b>NO CUMPLE</b>"
                    txt += f"  CS mínimo {rotulo}: <b>{fg(c_min, 3)}</b> (barra {e_(b_min)}), {estado}."
            p.append(f'<p class="nota">{txt}</p>')
        # gráficos
        if con_graficos:
            svg_d, esc = graficos.fig_deformada(modelo, res, cfg["escala_deformada"])
            p.append(fig(graficos.fig_esquema(modelo, res.F, res.cb),
                         f"{e_(nombre)}: cargas aplicadas en planta (nodales" + (" y en el tramo" if res.cb else "") + ")."))
            p.append(fig_visor([{"nombre": nombre, "F": res.F, "cb": res.cb, "res": res, "escala": esc}],
                               f"{e_(nombre)}: vista 3D interactiva de cargas y deformada (uz × {esc:g}); "
                               "arrastrar para girar."))
            p.append(fig(svg_d, f"{e_(nombre)}: estructura deformada. Desplazamientos verticales amplificados "
                                f"×{esc:g}; los números son u<sub>z</sub> reales en [{U['L']}]."))
            cur = esf["curvas"]
            esc_d = cfg["escala_diagramas"]
            p.append(fig(graficos.fig_diagrama_curvas(modelo, [(c["x"], c["M"]) for c in cur], U["M"],
                                                      texto_signo="M > 0: tracciona fibra inferior", escala=esc_d),
                         f"{e_(nombre)}: diagrama de momentos flectores M [{U['M']}]."))
            p.append(fig(graficos.fig_diagrama_curvas(
                             modelo, [(np.array([0, b.L / 2, b.L]), np.full(3, c["T"])) for b, c in zip(modelo.barras, cur)], U["M"],
                             escala=esc_d),
                         f"{e_(nombre)}: diagrama de momentos torsores T [{U['M']}]."))
            p.append(fig(graficos.fig_diagrama_curvas(modelo, [(c["x"], c["V"]) for c in cur], U["F"], escala=esc_d),
                         f"{e_(nombre)}: diagrama de esfuerzos de corte V [{U['F']}]."))
        p.append("</div>")

    # ---------------------------------------------------------------- 4. verificaciones
    p.append('<div class="caso"><h2>4. Verificaciones</h2>')
    lam = f"{info.lam_min:.3e}" if info.lam_min is not None else "no calculado (sistema grande)"
    p.append(f"<p>Estabilidad: menor autovalor de la matriz reducida normalizada = {lam} "
             "(un valor próximo a cero, por debajo de 1E-9, indicaría un mecanismo; el programa se detiene en ese caso).</p>")
    filas = []
    for nombre, res in resultados.items():
        eq = equilibrio(modelo, res)
        ok = eq["rel"] < 1e-8 and info.residuos[nombre] < 1e-8
        filas.append([e_(nombre), fg(eq["Fz_cargas"], 5), fg(eq["Fz_reacc"], 5), fg(eq["Mx_cargas"], 5),
                      fg(eq["Mx_reacc"], 5), fg(eq["My_cargas"], 5), fg(eq["My_reacc"], 5),
                      f"{eq['rel']:.1e}", f"{info.residuos[nombre]:.1e}",
                      '<span class="ok">OK</span>' if ok else "<b>REVISAR</b>"])
    p.append(tabla(["Caso", "ΣFz cargas", "ΣFz reacc.", "ΣMx cargas", "ΣMx reacc.", "ΣMy cargas", "ΣMy reacc.",
                    "Error equilibrio", "Residuo K·u−F", "Estado"], filas, num=range(1, 9),
                   nota="Equilibrio global respecto del origen: ΣFz, ΣMx = Σ(Mx + y·Pz), ΣMy = Σ(My − x·Pz); "
                        "las cargas y las reacciones (apoyos y resortes) deben sumar cero. "
                        "Errores relativos a la magnitud de las acciones."))
    p.append("</div>")

    if modelo.soldaduras:
        from ..soldadura import en_modelo
        p.append(en_modelo.html(modelo, sold if sold is not None else en_modelo.evaluar(modelo, resultados, "emparrillado"), U, "emparrillado"))

    # ---------------------------------------------------------------- anexo
    mostrar = cfg["anexo_matrices"] != "no"
    if mostrar:
        p.append('<div class="caso"><h2>Anexo A. Matrices de rigidez</h2>')
        p.append("<h3>A.1 Matriz de cada barra, en ejes globales (k<sub>glo</sub> = T·k<sub>loc</sub>·Tᵀ; con las articulaciones ya condensadas)</h3>")
        for b in modelo.barras:
            T_ = matriz_rotacion(b.g1, b.g2)
            k = T_ @ b.k_cond @ T_.T
            ni, nj = modelo.nodos[b.i].id, modelo.nodos[b.j].id
            cab = [""] + [f"{g}<sub>{e_(n)}</sub>" for n in (ni, nj) for g in GDL_H]
            filas = [[cab[i + 1]] + [fg(k[i, j], 4) for j in range(6)] for i in range(6)]
            p.append(f"<h4>Barra {e_(b.id)} (nodos {e_(ni)}–{e_(nj)})</h4>")
            p.append('<div class="scroll">' + tabla(cab, filas, num=range(1, 7), clase="matriz") + "</div>")
        if True:
            p.append("<h3>A.2 Matriz de rigidez ensamblada (ejes globales, incluye resortes)</h3>")
            cab = [f"{g}<sub>{e_(n.id)}</sub>" for n in modelo.nodos for g in GDL_H]
            filas = [[cab[i]] + [fg(info.K[i, j], 3) for j in range(3 * modelo.n)] for i in range(3 * modelo.n)]
            p.append('<div class="scroll">' + tabla([""] + cab, filas, num=range(1, 3 * modelo.n + 1), clase="matriz") + "</div>")
        p.append("</div>")

    return documento(f"{cfg['proyecto']} – Emparrillado plano", "\n".join(p), visor=con_graficos)


def generar_html_esquema(modelo: Modelo, aviso_estabilidad: str | None = None) -> str:
    """Informe corto SIN cálculo: datos + dibujos de cargas de cada caso, para revisar la entrada."""
    U = _unidades(modelo)
    fig_n = [0]

    def fig(svg, cap):
        fig_n[0] += 1
        return _figura(svg, cap, fig_n[0])

    p = _cabecera(modelo, U, "Revisión de datos de entrada")
    p.append('<div class="aviso">Este documento se generó <b>sin calcular</b> (opción --solo-esquema): '
             'sirve para revisar numeración, apoyos y signo de las cargas antes de resolver.</div>')
    if aviso_estabilidad:
        p.append('<div class="aviso"><b>Atención – estabilidad:</b><br>' + e_(aviso_estabilidad).replace("\n", "<br>") + "</div>")
    else:
        p.append('<p class="nota">Chequeo de estabilidad: la estructura no presenta mecanismos.</p>')
    vis_n = [0]

    def fig_visor(escenas, cap):
        vis_n[0] += 1
        return f'<figure>{visor3d.visor_html(modelo, escenas, f"visor{vis_n[0]}")}<figcaption>{cap}</figcaption></figure>'

    p += _datos(modelo, U, fig, True, fig_visor)
    p.append("<h2>3. Cargas de cada caso</h2>")
    for nombre, F in modelo.casos.items():
        cb = [(c, 1.0) for c in modelo.cargas_barra.get(nombre, [])]
        if np.any(F != 0) or cb:
            p.append(fig(graficos.fig_esquema(modelo, F, cb),
                         f"Caso {e_(nombre)}: cargas" + (" nodales y en tramos." if cb else " nodales.")))
    return documento(f"{modelo.config['proyecto']} – Revisión de datos", "\n".join(p), visor=True)
