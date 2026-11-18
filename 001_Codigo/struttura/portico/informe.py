"""Informe HTML autocontenido del pórtico plano, con formato de memoria de cálculo (sobrio, imprimible)."""
from __future__ import annotations

from struttura import plegable

import datetime
import html

import numpy as np

from struttura.emparrillado.formato import fe, fg, limpiar
from struttura.emparrillado.informe import CSS as CSS_BASE, _figura, _poli, tabla, unidad_tension

from .. import __version__
from . import graficos, visor2d
from ..falla_plana import rotulos
from ..pandeo import PANDEO
from .barra import constantes
from .cargas_barra import describir
from .entrada import Modelo
from .esfuerzos import esfuerzos, funciones_barra, tensiones
from .solver import Info, Resultado, equilibrio, rigidez_barra_global

e_ = html.escape
CSS = CSS_BASE + visor2d.CSS
GDL_H = ("u<sub>x</sub>", "u<sub>y</sub>", "φ")


def documento(titulo: str, cuerpo: str, boton: bool = True, visor: bool = False) -> str:
    """Página HTML.  Márgenes con la tabla 'hoja' (thead/tfoot se repiten al imprimir) y @page{margin:0}."""
    b = ('<div class="boton-imprimir no-print"><button onclick="window.print()">Imprimir</button>'
         '<div class="nota">Si el navegador agrega fecha o título en los bordes, desactivar '
         '"Encabezados y pies de página" en el diálogo de impresión.</div></div>') if boton else ""
    return (f"<!DOCTYPE html><html lang='es'><head><meta charset='utf-8'><title>{e_(titulo)}</title>"
            f"<style>{CSS}</style>" + (f"<script>{visor2d.LIB_JS}</script>" if visor else "") + f"<style>{plegable.CSS}</style><script>{plegable.JS}</script></head><body>"
            '<table class="hoja"><thead><tr><td><div class="esp"></div></td></tr></thead><tbody><tr><td>'
            f'<div class="contenido">{cuerpo}{b}</div>'
            '</td></tr></tbody><tfoot><tr><td><div class="esp"></div></td></tr></tfoot></table></body></html>')


def _unidades(modelo):
    f, l = modelo.config["unidad_fuerza"], modelo.config["unidad_longitud"]
    return {"F": f, "L": l, "M": f"{f}·{l}", "S": unidad_tension(f, l), "E": unidad_tension(f, l)}


def _cabecera(modelo, U, titulo_doc):
    cfg = modelo.config
    p = [f"<h1>{titulo_doc}</h1><div class='sub'>{e_(cfg['proyecto'])}</div>"]
    n_cb = sum(len(v) for v in modelo.cargas_barra.values())
    filas = [["Proyecto", e_(cfg["proyecto"])]]
    if cfg["autor"]:
        filas.append(["Autor", e_(cfg["autor"])])
    filas += [["Fecha", datetime.date.today().strftime("%d/%m/%Y")],
              ["Archivo de datos", e_(modelo.archivo.name)],
              ["Programa", f"Struttura {__version__}"],
              ["Unidades", f"fuerza [{U['F']}], longitud [{U['L']}], momento [{U['M']}], tensión [{U['S']}]"],
              ["Método", "Método matricial de rigidez, pórtico plano, 3 GDL por nodo (u<sub>x</sub>, u<sub>y</sub>, φ); "
                         "deformación axial y por flexión (Euler-Bernoulli)"],
              ["Datos", f"{modelo.n} nodos, {len(modelo.barras)} barras, {len(modelo.casos)} caso(s) de carga"
                        + (f", {n_cb} carga(s) en tramos" if n_cb else "")
                        + (f", {len(modelo.combinaciones)} combinación(es)" if modelo.combinaciones else "")]]
    p.append(tabla(["Dato", "Valor"], filas, clase="datos"))
    for a in modelo.avisos:
        p.append(f'<p class="nota">{e_(a)}</p>' if a.startswith("Nota: ") else f'<div class="aviso"><b>Aviso:</b> {e_(a)}</div>')
    return p


def _convenciones() -> str:
    return """<h2>1. Convenciones</h2>
<ul class="conv">
<li><b>Ejes globales:</b> X hacia la derecha, Y hacia arriba, z hacia el lector (terna derecha).  Los giros y momentos son
positivos en sentido <b>antihorario</b>.  Las cargas gravitatorias son <b>negativas</b> (en Y).</li>
<li><b>GDL por nodo</b> (ejes globales): u<sub>x</sub>, u<sub>y</sub>, φ.  Desplazamientos, reacciones y cargas nodales se informan en ejes <b>globales</b>.</li>
<li><b>Ejes locales de barra:</b> x<sub>l</sub> de i a j; y<sub>l</sub> a 90° antihorario de x<sub>l</sub>.
γ<sub>1</sub> = cos α = Δx/L, γ<sub>2</sub> = sen α = Δy/L.  Rotación: v<sub>glo</sub> = R·v<sub>loc</sub>, con R = [γ<sub>1</sub> −γ<sub>2</sub> 0; γ<sub>2</sub> γ<sub>1</sub> 0; 0 0 1]
y k<sub>glo</sub> = T·k<sub>loc</sub>·Tᵀ (T = diag(R, R)).  Los esfuerzos internos se informan en ejes <b>locales</b>.</li>
<li><b>Matriz de la barra</b> (tabla de cátedra): K = A·E/L, K<sub>1</sub> = 12·E·I/L³, K<sub>2</sub> = 6·E·I/L², K<sub>3</sub> = 4·E·I/L.</li>
<li><b>Esfuerzos:</b> <i>N</i> axil (positivo = tracción); <i>V</i> cortante (positivo si sobre la cara +x<sub>l</sub> actúa una fuerza hacia −y<sub>l</sub>);
<i>M</i> flector (positivo si traccionan las fibras del lado −y<sub>l</sub>, es decir, <i>M</i> > 0 cuando la barra "se panza" hacia −y<sub>l</sub>).
En términos de las fuerzas de extremo en i (nodo sobre barra): N = −P<sub>x,i</sub>, V = P<sub>y,i</sub>, M = −M<sub>i</sub>; en j: N = P<sub>x,j</sub>, V = −P<sub>y,j</sub>, M = M<sub>j</sub>.</li>
<li><b>Sentido i→j:</b> el lado "+y<sub>l</sub>" depende del orden en que se cargaron los nodos de cada barra; invertirlo cambia el signo de M (y no el de N ni el de V),
pero el resultado físico es el mismo (los diagramas de M se dibujan siempre del lado traccionado).  Las posiciones <i>a</i> y <i>b</i> de las cargas en el tramo se miden desde el nodo i.</li>
<li><b>Articulaciones:</b> se condensa el giro del extremo articulado (M = 0 en ese extremo).  En el nodo el giro φ es el de las barras rígidamente unidas;
el giro propio de la barra en el extremo articulado se informa aparte.</li>
<li><b>Cargas en el tramo:</b> se reemplazan por cargas nodales equivalentes <i>consistentes</i> (integrando las funciones de forma de la barra); las fuerzas de extremo son
<i>f = k·u + f<sub>0</sub></i>, con <i>f<sub>0</sub></i> las fuerzas de empotramiento perfecto, y los diagramas se reconstruyen sumando la carga del tramo.
Variación de temperatura: la parte uniforme (ΔT<sub>+yl</sub> + ΔT<sub>−yl</sub>)/2 produce esfuerzo axil E·A·α·ΔT<sub>m</sub> y el gradiente produce el momento E·I·α·(ΔT<sub>+yl</sub> − ΔT<sub>−yl</sub>)/h.</li>
<li><b>Reacciones:</b> fuerza/momento que el apoyo (o el resorte) ejerce sobre la estructura, en ejes globales.</li>
<li><b>Diagramas:</b> N y V se dibujan hacia +y<sub>l</sub> (izquierda de i→j) y M hacia la fibra traccionada; cada valor está rotulado.
Con escala por barra, cada barra se normaliza a su propio máximo (se ve la forma); los números son los reales.</li></ul>"""


def _txt_carga(c):
    if c.tipo == "q":
        f = lambda v: fg(v[0]) if v[0] == v[1] else f"{fg(v[0])} → {fg(v[1])}"
        partes = []
        if any(c.qx):
            partes.append(f"q<sub>x</sub> = {f(c.qx)}")
        if any(c.qy):
            partes.append(f"q<sub>y</sub> = {f(c.qy)}")
        return "; ".join(partes) or "0"
    if c.tipo == "P":
        return f"P<sub>x</sub> = {fg(c.Px)}; P<sub>y</sub> = {fg(c.Py)}"
    if c.tipo == "M":
        return f"M<sub>0</sub> = {fg(c.M0)}"
    return f"ΔT(+y<sub>l</sub>) = {fg(c.Ts)}; ΔT(−y<sub>l</sub>) = {fg(c.Ti)}"


def _datos(modelo, U, fig, con_graficos, fig_visor=None):
    p = ["<h2>2. Datos de entrada</h2>"]
    sec = [0]
    fig_visor = fig_visor or (lambda escenas, cap: "")

    def h3(t):
        sec[0] += 1
        p.append(f"<h3>2.{sec[0]} {t}</h3>")

    if con_graficos:
        h3("Esquema de la estructura")
        p.append(fig(graficos.fig_esquema(modelo), "Numeración de nodos y barras, apoyos, resortes y articulaciones."))
    h3("Nodos")
    filas = []
    for k, n in enumerate(modelo.nodos):
        v = ", ".join(nm for nm, f in zip(GDL_H, modelo.restr[k]) if f) or "libre"
        if modelo.aut[k, 2]:
            v += " (φ fijado por el programa: todas las barras articuladas)"
        filas.append([e_(n.id), fg(n.x), fg(n.y), v])
    p.append(tabla(["Nodo", f"x [{U['L']}]", f"y [{U['L']}]", "Vínculos (GDL restringidos)"], filas, num=(1, 2)))
    h3("Materiales")
    hay_alfa = any(m.alfa for m in modelo.materiales.values())
    p.append(tabla(["Material", f"E [{U['E']}]", "ν", f"f<sub>y</sub> [{U['S']}]", f"σ<sub>adm</sub> [{U['S']}]"]
                   + (["α [1/°]"] if hay_alfa else []),
                   [[e_(m.id), fg(m.E), fg(m.nu) if m.nu is not None else "–", fg(m.fy) if m.fy else "–",
                     fg(m.sadm) if m.sadm else "–"] + ([fg(m.alfa) if m.alfa else "–"] if hay_alfa else [])
                    for m in modelo.materiales.values()], num=range(1, 6 if hay_alfa else 5)))
    fuentes = [f"<b>{e_(m.id)}</b>: {e_(m.fuente)}" for m in modelo.materiales.values() if m.fuente]
    if fuentes:
        p.append("<p class='nota'>Datos tomados de la biblioteca de materiales (valores típicos de la ficha, no garantizados): " + "; ".join(fuentes) + ".</p>")
    if getattr(modelo, "peso_propio", None):
        pp = modelo.peso_propio
        how = "mitad del peso de cada barra aplicada en cada nudo extremo (las barras son bielas)" if pp.get("nodal") else "carga distribuida uniforme ρ·g·A en cada barra"
        p.append(f"<p class='nota'>Peso propio incluido en el caso <b>{e_(pp['caso'])}</b> (gravedad {e_(pp['gravedad'])}): {how}.  "
                 f"Masa total de las barras = {fg(pp['masa'], 4)} kg, peso = {fg(pp['peso'], 4)} {U['F']}.</p>")
    h3("Secciones")
    L2, L4 = U["L"] + "²", U["L"] + "⁴"
    p.append(tabla(["Sección", "Descripción", f"I [{L4}]", f"A [{L2}]", f"c [{U['L']}]", f"h [{U['L']}]", "k<sub>v</sub>"],
                   [[e_(s.id), e_(s.descripcion), fg(s.I), fg(s.A), fg(s.c), fg(s.h), fg(s.kv)]
                    for s in modelo.secciones.values()], num=range(2, 7),
                   nota="I: inercia a flexión (eje z); A: área; c: distancia a la fibra extrema; h: altura en el plano; "
                        "k<sub>v</sub>: τ<sub>máx</sub> por corte = k<sub>v</sub>·V/A."))
    h3("Barras")
    p.append(tabla(["Barra", "i", "j", f"L [{U['L']}]", "α [°]", "γ<sub>1</sub>", "γ<sub>2</sub>", "Material", "Sección", "Articulación", "Pandeo (extremos)"],
                   [[e_(b.id), e_(modelo.nodos[b.i].id), e_(modelo.nodos[b.j].id), fg(b.L), fg(b.angulo_deg, 5),
                     f"{b.g1:.5f}", f"{b.g2:.5f}", e_(b.mat.id), e_(b.sec.id),
                     " y ".join(t for t, f in (("en i", b.art_i), ("en j", b.art_j)) if f) or "–", PANDEO[b.pandeo][0]] for b in modelo.barras],
                   num=(3, 4, 5, 6)))
    if modelo.res_mask.any():
        h3("Resortes")
        filas = [[e_(n.id)] + [fg(v) if v > 0 else "–" for v in modelo.resortes[k]]
                 for k, n in enumerate(modelo.nodos) if modelo.resortes[k].any()]
        if filas:
            p.append(tabla(["Nodo", f"k<sub>x</sub> [{U['F']}/{U['L']}]", f"k<sub>y</sub> [{U['F']}/{U['L']}]",
                            f"k<sub>φ</sub> [{U['M']}/rad]"], filas, num=(1, 2, 3),
                           nota="Resortes lineales concentrados en el nodo, uno por GDL; '–': sin resorte."))
        if modelo.resortes_incl:
            p.append(tabla(["Nodo", f"k [{U['F']}/{U['L']}]", "Eje del resorte (ángulo desde +X)", "Ejes globales"],
                           [[e_(sp["id"]), fg(sp["k"]), f"{fg(sp['beta'], 5)}°",
                             f"a = (cos β, sen β) = ({np.cos(np.radians(sp['beta'])):.4f}, {np.sin(np.radians(sp['beta'])):.4f})"]
                            for sp in modelo.resortes_incl], num=(1,),
                           nota="Resortes lineales con eje inclinado: aportan k·a·aᵀ a la matriz de rigidez (términos u<sub>x</sub>-u<sub>y</sub> incluidos)."))
        hay_d = any(np.any(A != 0) for A in modelo.desaj.values()) or any(v for v in modelo.desaj_incl.values())
        if hay_d:
            filas = []
            for nombre in modelo.casos:
                A, Di = modelo.desaj[nombre], modelo.desaj_incl.get(nombre, {})
                for k, n in enumerate(modelo.nodos):
                    if np.any(A[k] != 0) or k in Di:
                        filas.append([e_(nombre), e_(n.id)] + [fg(v) if v != 0 else "–" for v in A[k]]
                                     + [fg(Di[k]) if k in Di else "–"])
            p.append(tabla(["Caso", "Nodo", f"e<sub>x</sub> [{U['L']}]", f"e<sub>y</sub> [{U['L']}]", "e<sub>φ</sub> [rad]",
                            f"e<sub>incl</sub> [{U['L']}]"], filas, num=(2, 3, 4, 5),
                           nota="Desajuste de resortes: desplazamiento impuesto al apoyo (extremo fijo) del resorte, positivo en el sentido "
                                "positivo del GDL (e<sub>incl</sub>: a lo largo del eje del resorte inclinado).  Fuerza del resorte = −k·(u − e); "
                                "un resorte más corto que lo proyectado (estirado al conectarlo) tiene e < 0."))
    if con_graficos:
        h3("Vista interactiva de las cargas")
        p.append(fig_visor([{"nombre": nombre, "F": F, "cb": [(c, 1.0) for c in modelo.cargas_barra.get(nombre, [])]}
                            for nombre, F in modelo.casos.items()],
                           "Vista interactiva (arrastrar: mover; rueda: zoom; doble clic: vista inicial).  "
                           "Px azul, Py / P / q rojo, M ámbar."))
    h3("Cargas nodales")
    filas = [[e_(nombre), e_(n.id), fg(F[k, 0]), fg(F[k, 1]), fg(F[k, 2])]
             for nombre, F in modelo.casos.items() for k, n in enumerate(modelo.nodos) if np.any(F[k] != 0)]
    p.append(tabla(["Caso", "Nodo", f"P<sub>x</sub> [{U['F']}]", f"P<sub>y</sub> [{U['F']}]", f"M [{U['M']}]"],
                   filas or [["–"] * 5], num=(2, 3, 4), nota="Ejes globales; M positivo antihorario."))
    if modelo.cargas_barra:
        h3("Cargas en barras (en el tramo)")
        filas = [[e_(nombre), e_(c.barra_id), describir(c), c.orig, fg(c.v1), fg(c.v2) if c.tipo in ("q", "temp") else "–",
                  fg(c.a) if c.tipo != "temp" else "–", fg(c.b) if c.tipo == "q" else "–", _txt_carga(c)]
                 for nombre, lista in modelo.cargas_barra.items() for c in lista]
        p.append(tabla(["Caso", "Barra", "Tipo", "Código", "Valor 1", "Valor 2", f"a [{U['L']}]", f"b [{U['L']}]",
                        "Componentes locales (x<sub>l</sub>, y<sub>l</sub>)"], filas, num=(4, 5, 6, 7),
                       nota=f"a y b se miden desde el nodo i a lo largo de la barra.  Distribuidas [{U['F']}/{U['L']}]: Valor 1 en a, Valor 2 en b (variación lineal).  "
                            f"Las de código qgx / qgy son por unidad de longitud de barra, y qgxp / qgyp por unidad de longitud proyectada "
                            f"(sobre la vertical / horizontal), por lo que la última columna las muestra ya multiplicadas por |sen α| / |cos α| y descompuestas en ejes locales.  "
                            f"Puntuales: P [{U['F']}], Mp [{U['M']}] (antihorario +).  Temperatura: Valor 1 = ΔT de la cara +y<sub>l</sub>, "
                            f"Valor 2 = ΔT de la cara −y<sub>l</sub> [°]."))
    if any(np.any(A != 0) for A in modelo.prefij.values()):
        h3("Desplazamientos prefijados")
        filas = [[e_(nombre), e_(n.id)] + [fg(v) if modelo.restr[k, c] else "–" for c, v in enumerate(A[k])]
                 for nombre, A in modelo.prefij.items() for k, n in enumerate(modelo.nodos) if np.any(A[k] != 0)]
        p.append(tabla(["Caso", "Nodo", f"u<sub>x</sub> [{U['L']}]", f"u<sub>y</sub> [{U['L']}]", "φ [rad]"], filas,
                       num=(2, 3, 4), nota="Valores impuestos a GDL restringidos (por ejemplo, el asentamiento de un apoyo).  "
                                           "Un caso puede tener solo desplazamientos prefijados y ninguna carga."))
    if modelo.combinaciones:
        h3("Combinaciones")
        p.append(tabla(["Combinación", "Definición"],
                       [[e_(n), " + ".join(f"{fg(f)}·{e_(c)}" for c, f in lista)] for n, lista in modelo.combinaciones.items()]))
    return p


def _resortes_caso(modelo, res):
    filas, mask = [], modelo.res_mask
    Rk = [limpiar(res.Rk[:, c]) for c in range(3)]
    for k, n in enumerate(modelo.nodos):
        if mask[k].any():
            filas.append([e_(n.id)] + [fg(Rk[c][k], 5) if mask[k, c] else "–" for c in range(3)])
    return filas


def generar_html(modelo: Modelo, resultados: dict, info: Info, con_graficos: bool = True, sold: dict | None = None) -> str:
    U = _unidades(modelo)
    cfg = modelo.config
    fig_n, vis_n = [0], [0]

    def fig(svg, cap):
        fig_n[0] += 1
        return _figura(svg, cap, fig_n[0])

    def fig_visor(escenas, cap):
        vis_n[0] += 1
        return f'<figure>{visor2d.visor_html(modelo, escenas, f"visor{vis_n[0]}")}<figcaption>{cap}</figcaption></figure>'

    p = _cabecera(modelo, U, "Memoria de cálculo – Pórtico plano")
    p.append(_convenciones())
    p += _datos(modelo, U, fig, con_graficos, fig_visor)

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
        p.append(tabla(["Nodo", f"u<sub>x</sub> [{U['L']}]", f"u<sub>y</sub> [{U['L']}]", "φ [rad]"],
                       [[e_(n.id), fe(u[k, 0]), fe(u[k, 1]), "–" if modelo.aut[k, 2] else fe(u[k, 2])]
                        for k, n in enumerate(modelo.nodos)], num=(1, 2, 3),
                       nota="'–': giro indeterminado (todas las barras articuladas en el nodo)." if modelo.aut.any() else None))
        R = np.column_stack([limpiar(res.R[:, c]) for c in range(3)])
        filas = [[e_(n.id)] + [fg(R[k, c], 5) if modelo.restr[k, c] else "–" for c in range(3)]
                 for k, n in enumerate(modelo.nodos) if modelo.restr[k].any()]
        if filas:
            p.append("<h4>Reacciones de apoyo (ejes globales)</h4>")
            p.append(tabla(["Nodo", f"R<sub>x</sub> [{U['F']}]", f"R<sub>y</sub> [{U['F']}]", f"M [{U['M']}]"], filas, num=(1, 2, 3)))
        filas = _resortes_caso(modelo, res)
        if filas:
            p.append("<h4>Fuerzas en los resortes (ejes globales)</h4>")
            p.append(tabla(["Nodo", f"F<sub>x</sub> [{U['F']}]", f"F<sub>y</sub> [{U['F']}]", f"M [{U['M']}]"], filas, num=(1, 2, 3),
                           nota="Fuerza que el resorte ejerce sobre la estructura (= −k·(u − e); e = desajuste, 0 si no se dio)."))
        arts = [(k, b) for k, b in enumerate(modelo.barras) if b.rel]
        if arts:
            p.append("<h4>Giros de las barras en los extremos articulados</h4>")
            filas = []
            for k, b in arts:
                for t, f, col, nodo in (("i", b.art_i, 2, b.i), ("j", b.art_j, 5, b.j)):
                    if f:
                        filas.append([e_(b.id), f"{t} (nodo {e_(modelo.nodos[nodo].id)})", fe(limpiar(res.ub[k])[col]),
                                      "–" if modelo.aut[nodo, 2] else fe(limpiar(res.u[:, 2])[nodo])])
            p.append(tabla(["Barra", "Extremo", "θ de la barra [rad]", "φ del nodo [rad]"], filas, num=(2, 3),
                           nota="En una articulación la barra gira distinto que el nodo; θ es el giro absoluto de la sección extrema de la barra."))
        con_tramo = bool(res.cb)
        N, Nj, V, Vj, Mi, Mj = (limpiar(esf[k]) for k in ("N", "Nj", "V", "Vj", "Mi", "Mj"))
        p.append("<h4>Esfuerzos en barras (ejes locales)</h4>")
        filas = []
        for k, b in enumerate(modelo.barras):
            fila = [e_(b.id), f"{e_(modelo.nodos[b.i].id)}–{e_(modelo.nodos[b.j].id)}", fg(N[k]), fg(Nj[k]), fg(V[k]), fg(Vj[k]),
                    fg(Mi[k]), fg(Mj[k])]
            if con_tramo:
                tiene = any(c.barra == k for c, _ in res.cb)
                fila += ([f"{fg(esf['Mmax'][k], 5)} (x={fg(esf['xMmax'][k], 4)})", f"{fg(esf['Mmin'][k], 5)} (x={fg(esf['xMmin'][k], 4)})"]
                         if tiene else ["–", "–"])
            filas.append(fila)
        cab = ["Barra", "i–j", f"N en i [{U['F']}]", f"N en j [{U['F']}]", f"V en i [{U['F']}]", f"V en j [{U['F']}]",
               f"M en i [{U['M']}]", f"M en j [{U['M']}]"] + ([f"M máx [{U['M']}]", f"M mín [{U['M']}]"] if con_tramo else [])
        nota = ("N > 0 tracción; V > 0: fuerza hacia −y<sub>l</sub> sobre la cara +x<sub>l</sub>; M > 0: tracciona el lado −y<sub>l</sub>.  "
                "Ejes locales de cada barra (x<sub>l</sub> de i a j).")
        if con_tramo:
            nota += ("  Con cargas en el tramo se dan los valores en ambos extremos y los extremos del flector a lo largo de la barra "
                     "(x medida desde i; '–': barra sin cargas en el tramo, ahí los extremos son los de i y j).")
        p.append(tabla(cab, filas, num=range(2, len(cab)), nota=nota))
        p.append("<h4>Funciones de esfuerzos de cada barra (ejes locales)</h4>")
        filas = []
        for k, b in enumerate(modelo.barras):
            for sg in funciones_barra(modelo, res, k):
                filas.append([e_(b.id), f"{fg(sg['x0'], 5)} ≤ x ≤ {fg(sg['x1'], 5)}", _poli(sg["N"]), _poli(sg["V"]), _poli(sg["M"])])
        p.append(tabla(["Barra", f"Tramo [{U['L']}]", f"N(x) [{U['F']}]", f"V(x) [{U['F']}]", f"M(x) [{U['M']}]"], filas, clase="funciones",
                       nota=f"x se mide desde el nodo i de cada barra, en [{U['L']}]; ejes y signos locales (ver convenciones).  "
                            "Los coeficientes se dan con 5 cifras significativas."))
        filas, sin_datos = [], False
        rot = rotulos(modelo)
        f4 = lambda v: fg(v, 4) if v is not None else "–"
        for k, (b, t) in enumerate(zip(modelo.barras, ten)):
            sin_datos |= t["vm"] is None
            filas.append([e_(b.id),
                          f"{fg(t['sig_t'], 4)} (x={fg(t['x_sig_t'], 4)})" if t["sig_t"] is not None else "–",
                          f"{fg(t['sig_c'], 4)} (x={fg(t['x_sig_c'], 4)})" if t["sig_c"] is not None else "–",
                          f4(t["tau_v"]), f4(t["vm"]), fg(t["n_fy"], 3) if t["n_fy"] else "–", fg(t["n_adm"], 3) if t["n_adm"] else "–",
                          (fg(t["n_pand"], 3) + ("" if t["n_pand"] >= 1 else " <b>NO CUMPLE</b>")) if t["n_pand"] else "–"])
        p.append("<h4>Tensiones y coeficientes de seguridad</h4>")
        nota = (f"σ = N/A ± M·c/I en las fibras extremas: σ<sub>tracc</sub> = N/A + |M|·c/I y σ<sub>compr</sub> = N/A − |M|·c/I (extremos a lo largo de la barra, "
                f"con la abscisa x desde i); τ<sub>v</sub> = k<sub>v</sub>·|V|/A en el eje neutro (máximo de la barra).  σ<sub>VM</sub>: máximo entre la fibra extrema "
                f"(|σ|, sin corte) y el eje neutro (√((N/A)² + 3·τ<sub>v</sub>²)), evaluado a lo largo de toda la barra.  CS fluencia = f<sub>y</sub>/σ<sub>VM</sub>; "
                f"CS admisible = σ<sub>adm</sub>/σ<sub>eq</sub> (cumple si ≥ 1).  Tensiones en [{U['S']}].{rot['nota']}  "
                f"CS pandeo = P<sub>c</sub>/|N<sub>min</sub>| en barras comprimidas, P<sub>c</sub> = π²·E·I/(K·L)² con la condición de extremos de cada barra (ver tabla de barras); "
                f"'–': la barra no está comprimida o la sección no tiene I.  *La condición de extremos de cada barra se deja a criterio del diseñador.")
        if sin_datos:
            nota += "  '–': la sección no tiene datos suficientes (c, A e I)."
        cab = ["Barra", "σ tracc. máx", "σ compr. máx", "τ<sub>v</sub>", rot["eq"], rot["cs"], "CS admisible", "CS pandeo*"]
        p.append(tabla(cab, filas, num=range(1, 8), nota=nota))
        vms = [(t["vm"], b.id) for b, t in zip(modelo.barras, ten) if t["vm"] is not None]
        if vms:
            vm, bid = max(vms)
            txt = f'Tensión {rot["nombre"]} máxima: <b>{fg(vm, 4)} {U["S"]}</b> en la barra {e_(bid)}.'
            for clave, rotulo in (("n_fy", "a fluencia"), ("n_adm", "respecto de la tensión admisible"), ("n_pand", "a pandeo*")):
                cs = [(t[clave], b.id) for b, t in zip(modelo.barras, ten) if t[clave]]
                if cs:
                    c_min, b_min = min(cs)
                    txt += f"  CS mínimo {rotulo}: <b>{fg(c_min, 3)}</b> (barra {e_(b_min)}), {'cumple' if c_min >= 1 else '<b>NO CUMPLE</b>'}."
            p.append(f'<p class="nota">{txt}</p>')
        if con_graficos:
            svg_d, esc = graficos.fig_deformada(modelo, res, cfg["escala_deformada"])
            p.append(fig(graficos.fig_esquema(modelo, res.F, res.cb),
                         f"{e_(nombre)}: cargas aplicadas (nodales" + (" y en el tramo" if res.cb else "") + ")."))
            p.append(fig_visor([{"nombre": nombre, "F": res.F, "cb": res.cb, "res": res, "escala": esc}],
                               f"{e_(nombre)}: vista interactiva (cargas, deformada ×{esc:g} y diagramas N, V, M); arrastrar para mover, rueda para zoom."))
            p.append(fig(svg_d, f"{e_(nombre)}: estructura deformada, desplazamientos amplificados ×{esc:g}; "
                                f"los números son (u<sub>x</sub>; u<sub>y</sub>) reales en [{U['L']}]."))
            cur, esc_d = esf["curvas"], cfg["escala_diagramas"]
            p.append(fig(graficos.fig_diagrama_curvas(modelo, [(c["x"], c["M"]) for c in cur], U["M"], texto_signo="M: hacia la fibra traccionada",
                                                      escala=esc_d, lado=-1),
                         f"{e_(nombre)}: diagrama de momentos flectores M [{U['M']}] (dibujado del lado traccionado)."))
            p.append(fig(graficos.fig_diagrama_curvas(modelo, [(c["x"], c["V"]) for c in cur], U["F"], texto_signo="V: hacia +y_l", escala=esc_d),
                         f"{e_(nombre)}: diagrama de esfuerzos de corte V [{U['F']}]."))
            p.append(fig(graficos.fig_diagrama_curvas(modelo, [(c["x"], c["N"]) for c in cur], U["F"], texto_signo="N: hacia +y_l", escala=esc_d),
                         f"{e_(nombre)}: diagrama de esfuerzos axiles N [{U['F']}] (tracción positiva)."))
        p.append("</div>")

    p.append('<div class="caso"><h2>4. Verificaciones</h2>')
    lam = f"{info.lam_min:.3e}" if info.lam_min is not None else "no calculado (sistema grande)"
    p.append(f"<p>Estabilidad: menor autovalor de la matriz reducida normalizada = {lam} "
             "(un valor próximo a cero, por debajo de 1E-12, indicaría un mecanismo; el programa se detiene en ese caso).</p>")
    filas = []
    for nombre, res in resultados.items():
        eq = equilibrio(modelo, res)
        ok = eq["rel"] < 1e-8 and info.residuos[nombre] < 1e-8
        filas.append([e_(nombre), fg(eq["Fx_cargas"], 5), fg(eq["Fx_reacc"], 5), fg(eq["Fy_cargas"], 5), fg(eq["Fy_reacc"], 5),
                      fg(eq["M_cargas"], 5), fg(eq["M_reacc"], 5), f"{eq['rel']:.1e}", f"{info.residuos[nombre]:.1e}",
                      '<span class="ok">OK</span>' if ok else "<b>REVISAR</b>"])
    p.append(tabla(["Caso", "ΣFx cargas", "ΣFx reacc.", "ΣFy cargas", "ΣFy reacc.", "ΣM cargas", "ΣM reacc.", "Error equilibrio",
                    "Residuo K·u−F", "Estado"], filas, num=range(1, 9),
                   nota="Equilibrio global: ΣFx, ΣFy y ΣM = Σ(M + x·F<sub>y</sub> − y·F<sub>x</sub>) respecto del origen; las cargas (nodales y equivalentes) y las "
                        "reacciones (apoyos y resortes) deben sumar cero.  Errores relativos a la magnitud de las acciones."))
    p.append("</div>")

    if modelo.soldaduras:
        from ..soldadura import en_modelo
        p.append(en_modelo.html(modelo, sold if sold is not None else en_modelo.evaluar(modelo, resultados, "portico"), U, "portico"))

    if cfg["anexo_matrices"] != "no":
        p.append('<div class="caso"><h2>Anexo A. Matrices de rigidez</h2>')
        p.append("<h3>A.1 Matriz de cada barra en ejes globales (k<sub>glo</sub> = T·k<sub>loc</sub>·Tᵀ, con articulaciones condensadas)</h3>")
        for b in modelo.barras:
            k = rigidez_barra_global(b)
            ni, nj = modelo.nodos[b.i].id, modelo.nodos[b.j].id
            K, K1, K2, K3 = constantes(b.mat.E, b.sec.A, b.sec.I, b.L)
            cab = [""] + [f"{g}<sub>{e_(n)}</sub>" for n in (ni, nj) for g in GDL_H]
            filas = [[cab[i + 1]] + [fg(k[i, j], 4) for j in range(6)] for i in range(6)]
            p.append(f"<h4>Barra {e_(b.id)} (nodos {e_(ni)}–{e_(nj)})</h4>")
            p.append(f'<p class="nota">K = {fg(K, 5)},  K<sub>1</sub> = {fg(K1, 5)},  K<sub>2</sub> = {fg(K2, 5)},  K<sub>3</sub> = {fg(K3, 5)}.</p>')
            p.append('<div class="scroll">' + tabla(cab, filas, num=range(1, 7), clase="matriz") + "</div>")
        if True:
            p.append("<h3>A.2 Matriz de rigidez ensamblada (ejes globales, incluye resortes)</h3>")
            cab = [f"{g}<sub>{e_(n.id)}</sub>" for n in modelo.nodos for g in GDL_H]
            filas = [[cab[i]] + [fg(info.K[i, j], 3) for j in range(3 * modelo.n)] for i in range(3 * modelo.n)]
            p.append('<div class="scroll">' + tabla([""] + cab, filas, num=range(1, 3 * modelo.n + 1), clase="matriz") + "</div>")
        p.append("</div>")
    return documento(f"{cfg['proyecto']} – Pórtico plano", "\n".join(p), visor=con_graficos)


def generar_html_esquema(modelo: Modelo, aviso_estabilidad: str | None = None) -> str:
    """Informe corto SIN cálculo: datos + dibujos de cargas de cada caso, para revisar la entrada."""
    U = _unidades(modelo)
    fig_n, vis_n = [0], [0]

    def fig(svg, cap):
        fig_n[0] += 1
        return _figura(svg, cap, fig_n[0])

    def fig_visor(escenas, cap):
        vis_n[0] += 1
        return f'<figure>{visor2d.visor_html(modelo, escenas, f"visor{vis_n[0]}")}<figcaption>{cap}</figcaption></figure>'

    p = _cabecera(modelo, U, "Revisión de datos de entrada")
    p.append('<div class="aviso">Este documento se generó <b>sin calcular</b> (opción --solo-esquema): '
             'sirve para revisar numeración, apoyos, articulaciones y signo de las cargas antes de resolver.</div>')
    if aviso_estabilidad:
        p.append('<div class="aviso"><b>Atención – estabilidad:</b><br>' + e_(aviso_estabilidad).replace("\n", "<br>") + "</div>")
    else:
        p.append('<p class="nota">Chequeo de estabilidad: la estructura no presenta mecanismos.</p>')
    p += _datos(modelo, U, fig, True, fig_visor)
    p.append("<h2>3. Cargas de cada caso</h2>")
    for nombre, F in modelo.casos.items():
        cb = [(c, 1.0) for c in modelo.cargas_barra.get(nombre, [])]
        if np.any(F != 0) or cb:
            p.append(fig(graficos.fig_esquema(modelo, F, cb), f"Caso {e_(nombre)}: cargas" + (" nodales y en tramos." if cb else " nodales.")))
    return documento(f"{modelo.config['proyecto']} – Revisión de datos", "\n".join(p), visor=True)
