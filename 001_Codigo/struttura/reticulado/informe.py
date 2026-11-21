"""Memoria de cálculo (HTML imprimible) del reticulado plano."""
from __future__ import annotations

import datetime
import math

import numpy as np

from struttura.emparrillado.formato import fe, fg, limpiar
from struttura.emparrillado.informe import _figura, tabla
from struttura.portico import graficos, visor2d
from struttura.portico.esfuerzos import esfuerzos
from struttura.portico.informe import _cabecera, _unidades, documento, e_
from struttura.portico.solver import equilibrio, rigidez_barra_global

from .. import __version__
from .analisis import verificar_barras
from .entrada import PANDEO


def _convenciones():
    return ("<h2>1. Convenciones</h2><ul>"
            "<li><b>Ejes globales</b>: X hacia la derecha, Y hacia arriba.  GDL por nodo: u<sub>x</sub>, u<sub>y</sub> (2 por nodo).</li>"
            "<li><b>Barra</b>: eje local x<sub>l</sub> de nodo i a nodo j; γ<sub>1</sub> = cos α = Δx/L, γ<sub>2</sub> = sen α = Δy/L.  "
            "Todas las barras son articuladas en ambos extremos y solo trabajan a esfuerzo axil.</li>"
            "<li><b>Axil N</b>: positivo = <b>tracción</b>, negativo = compresión.  σ = N/A.</li>"
            "<li><b>Matriz de la barra</b> (tabla de la cátedra): K = AE/L; términos γ<sub>1</sub>²K, γ<sub>1</sub>γ<sub>2</sub>K, γ<sub>2</sub>²K.</li>"
            "<li><b>Resortes</b>: se dibujan en verde con forma de zigzag (lineales según X, Y o inclinados). "
            "<b>No son barras</b>: son elementos elásticos concentrados en el nodo, con un extremo empotrado (rayado).</li>"
            "<li><b>Desplazamientos prefijados</b>: valores impuestos a un GDL restringido (asentamiento de apoyo, etc.).</li>"
            "<li><b>Reacciones</b>: fuerza que el apoyo ejerce sobre la estructura, en ejes globales.</li></ul>")


def _datos(modelo, U, fig):
    p = ["<h2>2. Datos de entrada</h2>"]
    n = [0]

    def h3(t):
        n[0] += 1
        p.append(f"<h3>2.{n[0]} {t}</h3>")

    h3("Esquema de la estructura")
    p.append(fig(graficos.fig_esquema(modelo), "Numeración de nodos y barras, apoyos y resortes."))
    h3("Nodos")
    filas = []
    for k, nd in enumerate(modelo.nodos):
        v = ", ".join(nm for nm, f in zip(("u<sub>x</sub>", "u<sub>y</sub>"), modelo.restr[k][:2]) if f) or "libre"
        filas.append([e_(nd.id), fg(nd.x), fg(nd.y), v])
    p.append(tabla(["Nodo", f"x [{U['L']}]", f"y [{U['L']}]", "GDL restringidos"], filas, num=(1, 2)))
    h3("Materiales y secciones")
    hay_alfa = any(m.alfa for m in modelo.materiales.values())
    p.append(tabla(["Material", f"E [{U['E']}]", f"f<sub>y</sub> [{U['S']}]", f"σ<sub>adm</sub> [{U['S']}]"] + (["α [1/°C]"] if hay_alfa else []),
                   [[e_(m.id), fg(m.E), fg(m.fy) if m.fy else "–", fg(m.sadm) if m.sadm else "–"] + ([fg(m.alfa) if m.alfa else "–"] if hay_alfa else [])
                    for m in modelo.materiales.values()], num=range(1, 5 if hay_alfa else 4)))
    fuentes = [f"<b>{e_(m.id)}</b>: {e_(m.fuente)}" for m in modelo.materiales.values() if m.fuente]
    if fuentes:
        p.append("<p class='nota'>Datos tomados de la biblioteca de materiales (valores típicos de la ficha, no garantizados): " + "; ".join(fuentes) + ".</p>")
    if getattr(modelo, "peso_propio", None):
        pp = modelo.peso_propio
        p.append(f"<p class='nota'>Peso propio incluido en el caso <b>{e_(pp['caso'])}</b> (gravedad {e_(pp['gravedad'])}): mitad del peso de cada barra aplicada en cada nudo extremo "
                 f"(las barras son bielas).  Masa total de las barras = {fg(pp['masa'], 4)} kg, peso = {fg(pp['peso'], 4)} {U['F']}.</p>")
    p.append(tabla(["Sección", "Descripción", f"A [{U['L']}²]", f"I [{U['L']}⁴]"],
                   [[e_(s.id), e_(s.descripcion) if s.id not in modelo.ret_sin_I else "genérica (solo A)", fg(s.A),
                     fg(s.I) if s.id not in modelo.ret_sin_I else "–"] for s in modelo.secciones.values()], num=(2, 3),
                   nota="I se usa solo para la verificación de pandeo; '–': no se informó (no se verifica pandeo)."))
    h3("Barras")
    filas = []
    for k, b in enumerate(modelo.barras):
        K = b.mat.E * b.sec.A / b.L
        filas.append([e_(b.id), e_(modelo.nodos[b.i].id), e_(modelo.nodos[b.j].id), fg(b.L), fg(b.angulo_deg, 5), f"{b.g1:.5f}", f"{b.g2:.5f}",
                      e_(b.mat.id), e_(b.sec.id), fg(K, 5), PANDEO[modelo.ret_pandeo[k]][0]])
    p.append(tabla(["Barra", "i", "j", f"L [{U['L']}]", "α [°]", "γ<sub>1</sub>", "γ<sub>2</sub>", "Material", "Sección",
                    f"K = AE/L [{U['F']}/{U['L']}]", "Vínculos (pandeo)"], filas, num=(3, 4, 5, 6, 9)))
    if modelo.res_mask.any():
        h3("Resortes (no son barras)")
        filas = [[e_(nd.id)] + [fg(v) if v > 0 else "–" for v in modelo.resortes[k][:2]] for k, nd in enumerate(modelo.nodos)
                 if modelo.resortes[k][:2].any()]
        if filas:
            p.append(tabla(["Nodo", f"k<sub>x</sub> [{U['F']}/{U['L']}]", f"k<sub>y</sub> [{U['F']}/{U['L']}]"], filas, num=(1, 2)))
        if modelo.resortes_incl:
            p.append(tabla(["Nodo", f"k [{U['F']}/{U['L']}]", "Eje (ángulo desde +X)"],
                           [[e_(sp["id"]), fg(sp["k"]), f"{fg(sp['beta'], 5)}°"] for sp in modelo.resortes_incl], num=(1,),
                           nota="Resorte con eje inclinado: aporta k·a·aᵀ, con a = (cos β, sen β)."))
        filas = []
        for nombre in modelo.casos:
            A, Di = modelo.desaj[nombre], modelo.desaj_incl.get(nombre, {})
            for k, nd in enumerate(modelo.nodos):
                if np.any(A[k][:2] != 0) or k in Di:
                    filas.append([e_(nombre), e_(nd.id)] + [fg(v) if v != 0 else "–" for v in A[k][:2]] + [fg(Di[k]) if k in Di else "–"])
        if filas:
            p.append(tabla(["Caso", "Nodo", f"e<sub>x</sub> [{U['L']}]", f"e<sub>y</sub> [{U['L']}]", f"e<sub>incl</sub> [{U['L']}]"], filas,
                           num=(2, 3, 4), nota="Desajuste de montaje: fuerza del resorte = −k·(u − e)."))
    h3("Cargas nodales")
    filas = [[e_(nombre), e_(nd.id), fg(F[k, 0]), fg(F[k, 1])] for nombre, F in modelo.casos.items()
             for k, nd in enumerate(modelo.nodos) if np.any(F[k][:2] != 0)]
    p.append(tabla(["Caso", "Nodo", f"P<sub>x</sub> [{U['F']}]", f"P<sub>y</sub> [{U['F']}]"], filas or [["–"] * 4], num=(2, 3),
                   nota="Ejes globales."))
    if modelo.cargas_barra:
        h3("Cargas en barras")
        from struttura.portico.cargas_barra import describir
        filas = [[e_(nombre), e_(c.barra_id), describir(c),
                  (("larga " if c.e0 > 0 else "corta ") + fg(abs(c.e0))) if c.orig == "dl" else fg(c.v1)]
                 for nombre, lista in modelo.cargas_barra.items() for c in lista]
        p.append(tabla(["Caso", "Barra", "Efecto", "Valor"], filas, num=(3,),
                       nota=f"Las cargas se aplican solo en los nudos; estos son efectos que no flexan la barra (Estado I de Brewer).  "
                            f"Temperatura: ΔT uniforme [°C] (dilatación libre α·ΔT·L).  Desajuste: e [{U['L']}] de barra corta (se estira para montarla, "
                            f"queda en tracción) o larga (se comprime).  En estructura isostática no producen esfuerzo, solo deformación.")) 
    if any(np.any(A[:, :2] != 0) for A in modelo.prefij.values()):
        h3("Desplazamientos prefijados")
        filas = [[e_(nombre), e_(nd.id)] + [fg(v) if modelo.restr[k, c] else "–" for c, v in enumerate(A[k][:2])]
                 for nombre, A in modelo.prefij.items() for k, nd in enumerate(modelo.nodos) if np.any(A[k][:2] != 0)]
        p.append(tabla(["Caso", "Nodo", f"u<sub>x</sub> [{U['L']}]", f"u<sub>y</sub> [{U['L']}]"], filas, num=(2, 3)))
    if modelo.combinaciones:
        h3("Combinaciones")
        p.append(tabla(["Combinación", "Definición"],
                       [[e_(nm), " + ".join(f"{fg(f)}·{e_(c)}" for c, f in lista)] for nm, lista in modelo.combinaciones.items()]))
    return p


def _pandeo_nota():
    return ("Pandeo de Euler (tabla de la cátedra): P<sub>c</sub> = π²EI/(K·L)² con empotrado–libre P<sub>c</sub> = π²EI/(4L²); "
            "articulado–articulado π²EI/L²; empotrado–articulado 2π²EI/L²; empotrado–empotrado 4π²EI/L².  "
            "CS pandeo = P<sub>c</sub>/|N| en barras comprimidas.  I es la inercia respecto del eje débil que informó el usuario.  "
            "La esbeltez λ = K·L/r, con r = √(I/A), es solo informativa (Euler vale para λ grandes).")


def generar_html(modelo, resultados, info, con_graficos=True) -> str:
    U = _unidades(modelo)
    cfg = modelo.config
    fig_n, vis_n = [0], [0]

    def fig(svg, cap):
        fig_n[0] += 1
        return _figura(svg, cap, fig_n[0])

    def fig_visor(escenas, cap):
        vis_n[0] += 1
        return f'<figure>{visor2d.visor_html(modelo, escenas, f"visor{vis_n[0]}")}<figcaption>{cap}</figcaption></figure>'

    p = _cabecera(modelo, U, "Memoria de cálculo – Reticulado plano")
    p[1:] = [f for f in p[1:]]                                        # cabecera del pórtico (tabla de datos)
    p.append(_convenciones())
    p += _datos(modelo, U, fig)
    p.append("<h2>3. Resultados</h2>")
    for idx, (nombre, res) in enumerate(resultados.items(), 1):
        p.append(f'<div class="caso"><h3>3.{idx} {"Combinación" if res.combo else "Caso"}: {e_(nombre)}</h3>')
        if res.combo:
            p.append('<p class="nota">' + " + ".join(f"{fg(f)}·{e_(c)}" for c, f in res.combo) + "</p>")
        u = np.column_stack([limpiar(res.u[:, c]) for c in range(2)])
        p.append("<h4>Desplazamientos nodales (ejes globales)</h4>")
        p.append(tabla(["Nodo", f"u<sub>x</sub> [{U['L']}]", f"u<sub>y</sub> [{U['L']}]"],
                       [[e_(nd.id), fe(u[k, 0]), fe(u[k, 1])] for k, nd in enumerate(modelo.nodos)], num=(1, 2)))
        R = np.column_stack([limpiar(res.R[:, c]) for c in range(2)])
        filas = [[e_(nd.id)] + [fg(R[k, c], 5) if modelo.restr[k, c] else "–" for c in range(2)]
                 for k, nd in enumerate(modelo.nodos) if modelo.restr[k, :2].any()]
        if filas:
            p.append("<h4>Reacciones de apoyo (ejes globales)</h4>")
            p.append(tabla(["Nodo", f"R<sub>x</sub> [{U['F']}]", f"R<sub>y</sub> [{U['F']}]"], filas, num=(1, 2)))
        Rk = limpiar(res.Rk)
        filas = [[e_(nd.id), fg(Rk[k, 0], 5), fg(Rk[k, 1], 5), fg(math.hypot(Rk[k, 0], Rk[k, 1]), 5)]
                 for k, nd in enumerate(modelo.nodos) if modelo.res_mask[k].any()]
        if filas:
            p.append("<h4>Fuerza en los resortes (no son barras)</h4>")
            p.append(tabla(["Nodo", f"F<sub>x</sub> [{U['F']}]", f"F<sub>y</sub> [{U['F']}]", f"|F| [{U['F']}]"], filas, num=(1, 2, 3),
                           nota="Fuerza que el resorte ejerce sobre la estructura (= −k·(u − e))."))
        from struttura import pandeo_resortes as _pr
        p += _pr.tabla_html(modelo, res, tabla, fg, e_, U['F'], U['L'])
        vb = verificar_barras(modelo, res)
        p.append("<h4>Esfuerzos axiles y tensiones en barras</h4>")
        filas = []
        for d in vb:
            b = d["barra"]
            nx = fg(d["N"], 5) if abs(d["Nmax"] - d["Nmin"]) <= 1e-9 * (abs(d["Nmax"]) + abs(d["Nmin"]) + 1e-300) else \
                f"{fg(d['N'], 5)} → {fg(d['Nj'], 5)}"
            filas.append([e_(b.id), f"{e_(modelo.nodos[b.i].id)}–{e_(modelo.nodos[b.j].id)}", nx, d["estado"], fg(d["sigma"], 4),
                          fe(d["dL"]), fg(d["n_fy"], 3) if d["n_fy"] else "–", fg(d["n_adm"], 3) if d["n_adm"] else "–"])
        p.append(tabla(["Barra", "i–j", f"N [{U['F']}]", "Estado", f"σ = N/A [{U['S']}]", f"ΔL [{U['L']}]", "CS fluencia", "CS admisible"],
                       filas, num=(2, 4, 5, 6, 7),
                       nota="N > 0 tracción (N es constante en cada barra: solo hay cargas en los nudos).  ΔL = u<sub>j</sub> − u<sub>i</sub> (proyectados sobre la barra), positivo = alargamiento.  "
                            "CS fluencia = f<sub>y</sub>/|σ|; CS admisible = σ<sub>adm</sub>/|σ|."))
        if any(d["Pc"] for d in vb):
            p.append("<h4>Verificación a pandeo (barras comprimidas)</h4>")
            filas = []
            for d in vb:
                b = d["barra"]
                comp = d["Nmin"] < 0
                filas.append([e_(b.id), PANDEO[d["cod"]][0], fg(d["lam"], 4) if d["lam"] else "–", fg(d["Pc"], 5) if d["Pc"] else "–",
                              fg(-d["Nmin"], 5) if comp else "–",
                              (fg(d["n_pand"], 3) + ("" if d["n_pand"] >= 1 else " <b>NO CUMPLE</b>")) if d["n_pand"] else ("–" if d["Pc"] else "sin I")])
            p.append(tabla(["Barra", "Vínculos", "λ = KL/r", f"P<sub>c</sub> [{U['F']}]", f"|N| compresión [{U['F']}]", "CS pandeo"], filas,
                           num=(2, 3, 4, 5), nota=_pandeo_nota()))
        # resumen
        res_txt = []
        for clave, rot in (("n_fy", "a fluencia"), ("n_adm", "respecto de la tensión admisible"), ("n_pand", "a pandeo")):
            cs = [(d[clave], d["barra"].id) for d in vb if d[clave]]
            if cs:
                c_min, b_min = min(cs)
                res_txt.append(f"CS mínimo {rot}: <b>{fg(c_min, 3)}</b> (barra {e_(b_min)}), {'cumple' if c_min >= 1 else '<b>NO CUMPLE</b>'}")
        if res_txt:
            p.append('<p class="nota">' + ".  ".join(res_txt) + ".</p>")
        if con_graficos:
            esf = esfuerzos(modelo, res)
            svg_d, esc = graficos.fig_deformada(modelo, res, cfg["escala_deformada"])
            p.append(fig(graficos.fig_esquema(modelo, res.F, res.cb),
                         f"{e_(nombre)}: cargas aplicadas" + (" (incluye cargas en barras)." if res.cb else ".")))
            p.append(fig_visor([{"nombre": nombre, "F": res.F, "cb": res.cb, "res": res, "escala": esc}],
                               f"{e_(nombre)}: vista interactiva (cargas, deformada ×{esc:g} y diagrama de axiles N); arrastrar para mover, rueda para zoom."))
            p.append(fig(svg_d, f"{e_(nombre)}: estructura deformada, desplazamientos amplificados ×{esc:g}; los números son "
                                f"(u<sub>x</sub>; u<sub>y</sub>) reales en [{U['L']}]."))
            cur = esf["curvas"]
            p.append(fig(graficos.fig_diagrama_curvas(modelo, [(c["x"], c["N"]) for c in cur], U["F"], texto_signo="N: tracción positiva",
                                                      escala="global"),
                         f"{e_(nombre)}: esfuerzos axiles N [{U['F']}] (escala única; azul = tracción, rojo = compresión)."))
        p.append("</div>")

    p.append('<div class="caso"><h2>4. Verificaciones</h2>')
    lam = f"{info.lam_min:.3e}" if info.lam_min is not None else "no calculado (sistema grande)"
    p.append(f"<p>Estabilidad: menor autovalor de la matriz reducida normalizada = {lam} "
             "(por debajo de 1E-12 indicaría un mecanismo; el programa se detiene en ese caso).</p>")
    filas = []
    for nombre, res in resultados.items():
        eq = equilibrio(modelo, res)
        ok = eq["rel"] < 1e-8 and info.residuos[nombre] < 1e-8
        filas.append([e_(nombre), fg(eq["Fx_cargas"], 5), fg(eq["Fx_reacc"], 5), fg(eq["Fy_cargas"], 5), fg(eq["Fy_reacc"], 5),
                      f"{eq['rel']:.1e}", f"{info.residuos[nombre]:.1e}", '<span class="ok">OK</span>' if ok else "<b>REVISAR</b>"])
    p.append(tabla(["Caso", "ΣFx cargas", "ΣFx reacc.", "ΣFy cargas", "ΣFy reacc.", "Error equilibrio", "Residuo K·u−F", "Estado"], filas,
                   num=range(1, 7), nota="Las cargas (nodales y equivalentes) y las reacciones (apoyos y resortes) deben sumar cero; "
                                          "el equilibrio de momentos respecto del origen también se verifica (incluido en el error)."))
    p.append("</div>")
    if cfg["anexo_matrices"] != "no":
        p.append('<div class="caso"><h2>Anexo A. Matriz de rigidez de cada barra (ejes globales, GDL u<sub>x</sub>, u<sub>y</sub> de i y j)</h2>')
        for b in modelo.barras:
            K = b.mat.E * b.sec.A / b.L
            g1, g2 = b.g1, b.g2
            a, bb, c = g1 * g1 * K, g1 * g2 * K, g2 * g2 * K
            M = np.array([[a, bb, -a, -bb], [bb, c, -bb, -c], [-a, -bb, a, bb], [-bb, -c, bb, c]])
            cab = [f"{g}<sub>{e_(nd)}</sub>" for nd in (modelo.nodos[b.i].id, modelo.nodos[b.j].id) for g in ("u<sub>x</sub>", "u<sub>y</sub>")]
            p.append(f"<h4>Barra {e_(b.id)}</h4>")
            p.append(f'<p class="nota">K = AE/L = {fg(K, 5)};  γ<sub>1</sub>² K = {fg(a, 5)};  γ<sub>1</sub>γ<sub>2</sub> K = {fg(bb, 5)};  '
                     f'γ<sub>2</sub>² K = {fg(c, 5)}.</p>')
            p.append('<div class="scroll">' + tabla([""] + cab, [[cab[i]] + [fg(M[i, j], 4) for j in range(4)] for i in range(4)],
                                                   num=range(1, 5), clase="matriz") + "</div>")
        p.append("<h3>Matriz de rigidez ensamblada (ejes globales, GDL u<sub>x</sub>, u<sub>y</sub> de cada nudo; incluye resortes)</h3>")
        gd = [3 * k + c for k in range(modelo.n) for c in (0, 1)]
        cab = [f"{g}<sub>{e_(nd.id)}</sub>" for nd in modelo.nodos for g in ("u<sub>x</sub>", "u<sub>y</sub>")]
        Kr = info.K[np.ix_(gd, gd)]
        p.append('<div class="scroll">' + tabla([""] + cab, [[cab[i]] + [fg(Kr[i, j], 3) for j in range(len(gd))] for i in range(len(gd))],
                                               num=range(1, len(gd) + 1), clase="matriz") + "</div>")
        p.append("</div>")
    return documento(f"{cfg['proyecto']} – Reticulado plano", "\n".join(p), visor=con_graficos)


def generar_html_esquema(modelo, aviso=None) -> str:
    U = _unidades(modelo)
    fig_n = [0]

    def fig(svg, cap):
        fig_n[0] += 1
        return _figura(svg, cap, fig_n[0])

    p = _cabecera(modelo, U, "Revisión de datos de entrada – Reticulado plano")
    p.append('<div class="aviso">Documento generado <b>sin calcular</b> (--solo-esquema): sirve para revisar numeración, apoyos, resortes y cargas.</div>')
    if aviso:
        p.append('<div class="aviso"><b>Atención – estabilidad:</b><br>' + e_(aviso).replace("\n", "<br>") + "</div>")
    p += _datos(modelo, U, fig)
    for nombre, F in modelo.casos.items():
        cb = [(c, 1.0) for c in modelo.cargas_barra.get(nombre, [])]
        if np.any(F != 0) or cb:
            p.append(fig(graficos.fig_esquema(modelo, F, cb), f"Caso {e_(nombre)}: cargas."))
    return documento(f"{modelo.config['proyecto']} – Revisión de datos", "\n".join(p))
