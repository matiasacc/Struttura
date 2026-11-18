"""Informe HTML (memoria de cálculo) del pórtico espacial, con visor 3D."""
from __future__ import annotations

import datetime
import html

import numpy as np

from .. import __version__
from ..emparrillado.formato import fe, fg, limpiar
from ..emparrillado.informe import CSS as CSS_BASE, tabla, unidad_tension
from . import visor
from .barra import descripcion_articulacion
from .entrada import NOMBRES_GDL, Modelo
from ..pandeo import PANDEO
from .esfuerzos import NOMBRES, esfuerzos_extremos, pandeo_barras, tensiones
from .tensor import TEORIAS, analizar
from .solver import Info, equilibrio

e_ = html.escape
CSS = CSS_BASE + visor.CSS


def documento(titulo: str, cuerpo: str) -> str:
    return (f"<!DOCTYPE html><html lang='es'><head><meta charset='utf-8'><title>{e_(titulo)}</title>"
            f"<style>{CSS}</style><script>{visor.JS}</script></head><body>"
            '<table class="hoja"><thead><tr><td><div class="esp"></div></td></tr></thead><tbody><tr><td>'
            f'<div class="contenido">{cuerpo}'
            '<div class="boton-imprimir no-print"><button onclick="window.print()">Imprimir</button></div></div>'
            '</td></tr></tbody><tfoot><tr><td><div class="esp"></div></td></tr></tfoot></table></body></html>')


def _U(modelo):
    f, l = modelo.config["unidad_fuerza"], modelo.config["unidad_longitud"]
    return {"F": f, "L": l, "M": f"{f}·{l}", "S": unidad_tension(f, l)}


def _convenciones():
    return """<h2>Convenciones</h2><ul class="conv">
<li>Ejes globales X, Y, Z (terna derecha, Z hacia arriba).  Seis GDL por nudo: u<sub>x</sub>, u<sub>y</sub>, u<sub>z</sub>, φ<sub>x</sub>, φ<sub>y</sub>, φ<sub>z</sub> (giros positivos por regla de la mano derecha).</li>
<li>Ejes locales de cada barra: x de i a j; y, z principales de la sección (x × y = z).  Por defecto z local apunta hacia +Z global (en barras verticales, hacia +X global).</li>
<li>Reacciones = fuerza/momento que el apoyo ejerce sobre la estructura (ejes globales).</li>
<li>Esfuerzos sobre la cara +x de la sección: N (tracción +), V<sub>y</sub>, V<sub>z</sub>, T, M<sub>y</sub> (&gt;0 traccciona la fibra +z), M<sub>z</sub> (&gt;0 traccciona la fibra −y).  σ = N/A + M<sub>y</sub>·z/I<sub>y</sub> − M<sub>z</sub>·y/I<sub>z</sub>.</li>
<li>En los diagramas de momento, la ordenada se dibuja del lado de la fibra traccionada.  Sin deformación por corte (Euler-Bernoulli).</li></ul>"""


def _datos(modelo, U):
    P = []
    P.append("<h2>1. Datos</h2>")
    P.append(tabla(["Nudo", "x", "y", "z", "Apoyo (GDL restringidos)", "Resortes"],
                   [[nd.id, fg(nd.x), fg(nd.y), fg(nd.z),
                     " ".join(NOMBRES_GDL[c] for c in range(6) if modelo.restr[k, c]) or "–",
                     " ".join(f"{NOMBRES_GDL[c]}={fg(modelo.resortes[k, c])}" for c in range(6) if modelo.resortes[k, c] > 0) or "–"]
                    for k, nd in enumerate(modelo.nodos)], num=(1, 2, 3)))
    filas = []
    hay_art = any(b.articulada for b in modelo.barras)
    for b in modelo.barras:
        s = b.sec
        filas.append([b.id, modelo.nodos[b.i].id, modelo.nodos[b.j].id, fg(b.L), e_(b.mat.id), e_(s.id),
                      "  ".join(fg(v, 4) for v in b.R[0]), "  ".join(fg(v, 4) for v in b.R[1]),
                      "  ".join(fg(v, 4) for v in b.R[2])] + ([descripcion_articulacion(b.art_i), descripcion_articulacion(b.art_j)] if hay_art else []))
    P.append("<h3>Barras y ejes locales</h3>")
    P.append(tabla(["Barra", "i", "j", f"L [{U['L']}]", "Material", "Sección", "x local (global)", "y local", "z local"]
                   + (["Articulación en i", "en j"] if hay_art else []), filas, num=(3,)))
    if modelo.peso_propio:
        pp = modelo.peso_propio
        P.append(f"<p class='nota'>Peso propio incluido en el caso <b>{e_(pp['caso'])}</b> (gravedad {e_(pp['gravedad'])}): "
                 f"carga distribuida uniforme ρ·g·A en cada barra.  Masa total de las barras = {fg(pp['masa'], 4)} kg, "
                 f"peso = {fg(pp['peso'], 4)} {U['F']}.</p>")
    P.append("<h3>Materiales y secciones</h3>")
    P.append(tabla(["Material", f"E [{U['S']}]", f"G [{U['S']}]", "fy", "σadm"],
                   [[e_(m.id), fg(m.E), fg(m.G), fg(m.fy), fg(m.sadm)] for m in modelo.materiales.values()], num=(1, 2, 3, 4)))
    fuentes = [f"<b>{e_(m.id)}</b>: {e_(m.fuente)}" for m in modelo.materiales.values() if m.fuente]
    if fuentes:
        P.append("<p class='nota'>Datos tomados de la biblioteca de materiales (valores típicos de la ficha, no garantizados): " + "; ".join(fuentes) + ".</p>")
    P.append(tabla(["Sección", "Descripción", f"A [{U['L']}²]", f"I<sub>y</sub> [{U['L']}⁴]", f"I<sub>z</sub> [{U['L']}⁴]", f"J [{U['L']}⁴]"],
                   [[e_(s.id), e_(s.descripcion), fg(s.A), fg(s.Iy), fg(s.Iz), fg(s.J)] for s in modelo.secciones.values()], num=(2, 3, 4, 5)))
    for nombre in modelo.casos:
        filas = [[modelo.nodos[k].id] + [fg(v) for v in modelo.casos[nombre][k]] for k in range(modelo.n) if modelo.casos[nombre][k].any()]
        pref = [[modelo.nodos[k].id] + [fg(v) for v in modelo.prefij[nombre][k]] for k in range(modelo.n) if modelo.prefij[nombre][k].any()]
        bar = modelo.cargas_barra_orig.get(nombre, [])
        if not (filas or pref or bar):
            continue
        P.append(f"<h3>Caso {e_(nombre)}</h3>")
        if filas:
            P.append(tabla(["Nudo", f"F<sub>x</sub> [{U['F']}]", "F<sub>y</sub>", "F<sub>z</sub>", f"M<sub>x</sub> [{U['M']}]", "M<sub>y</sub>", "M<sub>z</sub>"], filas, num=range(1, 7)))
        if bar:
            P.append(tabla(["Barra", "Tipo", "Valor", "Valor 2", "a"], [[e_(b), t, fg(v1), fg(v2), fg(a)] for b, t, v1, v2, a in bar], num=(2, 3, 4)))
        if pref:
            P.append(tabla(["Nudo (prefijado)", "u<sub>x</sub>", "u<sub>y</sub>", "u<sub>z</sub>", "φ<sub>x</sub>", "φ<sub>y</sub>", "φ<sub>z</sub>"], pref, num=range(1, 7)))
    for nombre, lista in modelo.combinaciones.items():
        P.append(f"<p><b>Combinación {e_(nombre)}</b> = " + " + ".join(f"{fg(f)}·{e_(c)}" for c, f in lista) + "</p>")
    return P


def _cab_gdl(nodos_ids):
    g = ("u<sub>x</sub>", "u<sub>y</sub>", "u<sub>z</sub>", "φ<sub>x</sub>", "φ<sub>y</sub>", "φ<sub>z</sub>")
    return [f"{x}<sub>{e_(n)}</sub>" for n in nodos_ids for x in g]


def _anexo(modelo, info) -> str:
    P = ['<div class="caso"><h2>Anexo A. Matrices de rigidez</h2>']
    P.append("<p class='nota'>La matriz local de 12×12 es la <b>suma directa</b> de dos bloques de 6×6 que no se acoplan: "
             "el de <b>pórtico plano</b> (u, v, θ<sub>z</sub>: axil y flexión en x-y, con I<sub>z</sub>) y el de "
             "<b>emparrillado</b> (w, θ<sub>x</sub>, θ<sub>y</sub>: flexión en x-z con I<sub>y</sub> y torsión con GJ/L).  "
             "El acople aparece recién al pasar a ejes globales cuando la barra es oblicua en el espacio: "
             "k<sub>glo</sub> = Tᵀ·k<sub>loc</sub>·T.</p>")
    P.append("<h3>A.1 Matriz de cada barra</h3>")
    for b in modelo.barras:
        ni, nj = modelo.nodos[b.i].id, modelo.nodos[b.j].id
        s = b.sec
        E, G, L = b.mat.E, b.mat.G, b.L
        P.append(f"<h4>Barra {e_(b.id)} (nudos {e_(ni)}–{e_(nj)})</h4>")
        P.append(f'<p class="nota">EA/L = {fg(E * s.A / L, 5)},  GJ/L = {fg(G * s.J / L, 5)},  12EI<sub>z</sub>/L³ = {fg(12 * E * s.Iz / L**3, 5)},  '
                 f'6EI<sub>z</sub>/L² = {fg(6 * E * s.Iz / L**2, 5)},  4EI<sub>z</sub>/L = {fg(4 * E * s.Iz / L, 5)},  '
                 f'12EI<sub>y</sub>/L³ = {fg(12 * E * s.Iy / L**3, 5)},  6EI<sub>y</sub>/L² = {fg(6 * E * s.Iy / L**2, 5)},  4EI<sub>y</sub>/L = {fg(4 * E * s.Iy / L, 5)}.</p>')
        cab_l = [f"{x}<sub>{y}</sub>" for y in ("i", "j") for x in ("u", "v", "w", "θ<sub>x</sub>", "θ<sub>y</sub>", "θ<sub>z</sub>")]
        if b.articulada:
            P.append(f"<p class='nota'>Articulaciones: en i = {descripcion_articulacion(b.art_i)}, en j = {descripcion_articulacion(b.art_j)}. "
                     "La matriz local es la <b>condensada</b>: k<sub>c</sub> = k<sub>AA</sub> − k<sub>AB</sub>·k<sub>BB</sub><sup>-1</sup>·k<sub>BA</sub> "
                     "(filas y columnas de los giros liberados en cero).</p>")
        P.append("<p class='nota'><b>Local</b> (ejes de la barra)</p>")
        P.append('<div class="scroll">' + tabla([""] + cab_l, [[cab_l[i]] + [fg(b.k_cond[i, j], 4) for j in range(12)] for i in range(12)],
                                               num=range(1, 13), clase="matriz") + "</div>")
        cab_g = _cab_gdl((ni, nj))
        P.append("<p class='nota'><b>Global</b> (ejes X, Y, Z)</p>")
        P.append('<div class="scroll">' + tabla([""] + cab_g, [[cab_g[i]] + [fg(b.k_global[i, j], 4) for j in range(12)] for i in range(12)],
                                                num=range(1, 13), clase="matriz") + "</div>")
    P.append("<h3>A.2 Matriz de rigidez ensamblada (ejes globales, incluye resortes)</h3>")
    cab = _cab_gdl([nd.id for nd in modelo.nodos])
    N = 6 * modelo.n
    P.append('<div class="scroll">' + tabla([""] + cab, [[cab[i]] + [fg(info.K[i, j], 3) for j in range(N)] for i in range(N)],
                                           num=range(1, N + 1), clase="matriz") + "</div>")
    P.append("</div>")
    return "\n".join(P)


def _fcs(v):
    return "–" if v is None else ("∞" if not np.isfinite(v) else fg(v, 4))


def _tensor_html(reg, modelo, U, titulo):
    b = modelo.barras[reg["barra"]]
    m = b.mat
    S = U["S"]
    h = [f"<h4>{titulo}</h4>"]
    h.append(f"<p class='nota'>Barra <b>{e_(b.id)}</b> ({e_(modelo.nodos[b.i].id)}–{e_(modelo.nodos[b.j].id)}), x = {fg(reg['x'])} {U['L']} desde i; "
             f"punto (y, z) = ({fg(reg['y'])}; {fg(reg['z'])}) {U['L']}"
             + (f" — {e_(reg['rotulo'])}" if reg['rotulo'] != 'pedido' else "") + ".<br>"
             "Esfuerzos: " + ",  ".join(f"{n} = {fg(v, 4)}" for n, v in zip(NOMBRES, reg["E"])) + ".</p>")
    sx, txy, txz = reg["sx"], reg["txy"], reg["txz"]
    T = [[sx, txy, txz], [txy, 0.0, 0.0], [txz, 0.0, 0.0]]
    h.append(tabla([f"σ [{S}]", "x local", "y local", "z local"], [[f"<b>{n}</b>"] + [fg(v, 5) for v in fila] for n, fila in zip(("x", "y", "z"), T)],
                   num=(1, 2, 3), clase="tensor"))
    filas = [["σ<sub>1</sub>, σ<sub>2</sub>, σ<sub>3</sub>", f"{fg(reg['s1'], 5)},  {fg(reg['s2'], 5)},  {fg(reg['s3'], 5)}"],
             ["τ<sub>máx</sub> = (σ<sub>1</sub> − σ<sub>3</sub>)/2", fg(reg["tau_max"], 5)],
             ["Ángulo de σ<sub>1</sub> respecto de x local", f"{fg(reg['ang'], 4)}°"]]
    crit = [("vm", "Von Mises", reg["vm"]), ("tresca", "Tresca", reg["tresca"]), ("rankine", "Rankine", reg["rankine"]), ("mohr", "Mohr", reg.get("mohr")), ("mohrmod", "Mohr modificado", reg.get("mohrmod"))]
    for k, nom, eq in crit:
        if k in reg["cs"]:
            gob = " ◄ gobernante" if k == m.teoria else ""
            filas.append([f"{nom}" + gob, (f"σ<sub>eq</sub> = {fg(eq, 5)},  " if eq is not None else "") + f"CS = {_fcs(reg['cs'][k])}"])
    if reg["cs_adm"] is not None:
        filas.append(["CS respecto de σ<sub>adm</sub>", _fcs(reg["cs_adm"])])
    h.append(tabla(["Magnitud", "Valor"], filas, clase="datos"))
    return "\n".join(h)


def _tensiones_html(modelo, r, an, U):
    S = U["S"]
    P = ["<h3>Tensiones y criterios de falla</h3>"]
    ts = tensiones(modelo, r, an)
    if not any(t["vm"] is not None for t in ts):
        P.append("<p class='nota'>Ninguna sección tiene datos para calcular tensiones (dar cy, cz o usar tubo, circular, rectangular, rect_hueca).</p>")
    else:
        teorias = sorted({TEORIAS[b.mat.teoria] for b in modelo.barras})
        P.append(tabla(["Barra", f"σ<sub>x</sub> tracción máx [{S}]", "σ<sub>x</sub> compresión máx", "τ máx", "σ<sub>eq</sub> máx", "x de σ<sub>eq</sub>", "Punto", "CS mín"],
                       [[b.id, fg(t["sig_t"]), fg(t["sig_c"]), fg(t["tau_t"]), fg(t["vm"]), fg(t["x_vm"]), e_(t["punto"] or "–"), _fcs(t["cs"])]
                        for b, t in zip(modelo.barras, ts)], num=(1, 2, 3, 4, 5, 7),
                       nota=f"σ<sub>eq</sub> según la teoría de cada material ({', '.join(teorias)}); CS = resistencia/σ<sub>eq</sub>.  "
                            "Se evalúa en todas las estaciones de la barra y en los puntos candidatos de la sección (24 en el perímetro de tubos y circulares, cada 15°; esquinas, caras y baricentro en las demás).  "
                            + ("Incluye el corte de flexión (Jourawski)." if an["corte"] else "<b>No</b> incluye el corte de flexión (corte_tensiones;no).")))
        pb = pandeo_barras(modelo, r)
        P.append("<h4>Pandeo de Euler (barras comprimidas)*</h4>")
        P.append(tabla(["Barra", "Extremos (pandeo)", f"I débil [{U['L']}<sup>4</sup>]", "λ = KL/r", f"P<sub>c</sub> [{U['F']}]", f"|N<sub>min</sub>| [{U['F']}]", "CS pandeo"],
                       [[b.id, PANDEO[d["cod"]][0], fg(d["I"]), fg(d["lam"], 4) if d["lam"] else "–", fg(d["Pc"], 5) if d["Pc"] else "–",
                         fg(-d["Nmin"], 5) if d["n_pand"] else "–",
                         (fg(d["n_pand"], 3) + ("" if d["n_pand"] >= 1 else " <b>NO CUMPLE</b>")) if d["n_pand"] else "–"] for b, d in zip(modelo.barras, pb)],
                       num=(2, 3, 4, 5, 6),
                       nota="P<sub>c</sub> = π²·E·I/(K·L)², con I la menor de I<sub>y</sub> e I<sub>z</sub> y K según los extremos de la barra (columna <code>pandeo</code> de BARRAS; por defecto art-art).  "
                            "CS pandeo = P<sub>c</sub>/|N<sub>min</sub>| (N<sub>min</sub>: mayor compresión a lo largo de la barra); '–': la barra no está comprimida.  "
                            "*La condición de extremos de cada barra se deja a criterio del diseñador."))
        if an["criticos"]:
            P.append(f"<h4>Puntos más exigidos (uno por barra, hasta {len(an['criticos'])})</h4>")
            P.append(tabla(["#", "Barra", "x", "Punto", f"σ<sub>x</sub> [{S}]", "τ<sub>xy</sub>", "τ<sub>xz</sub>", "σ<sub>1</sub>", "σ<sub>3</sub>", "σ<sub>VM</sub>", "σ<sub>Tresca</sub>", "CS"],
                           [[i + 1, modelo.barras[c["barra"]].id, fg(c["x"]), e_(c["rotulo"]), fg(c["sx"]), fg(c["txy"]), fg(c["txz"]), fg(c["s1"]), fg(c["s3"]),
                             fg(c["vm"]), fg(c["tresca"]), _fcs(c["cs_gob"])] for i, c in enumerate(an["criticos"])], num=range(4, 12)))
            for i, c in enumerate(an["criticos"][:3]):
                P.append(_tensor_html(c, modelo, U, f"Tensor en el punto crítico #{i + 1}"))
    if an["usuario"]:
        P.append("<h4>Puntos pedidos (bloque PUNTOS DE TENSION)</h4>")
        for c in an["usuario"]:
            P.append(_tensor_html(c, modelo, U, f"Punto {e_(c['id'])}"))
    return P


def _soldaduras_html(modelo, resultados, sold=None) -> str:
    """Sección 'Soldaduras': una verificación por soldadura con los esfuerzos del extremo de la barra en cada caso y combinación."""
    from ..soldadura.datos import canon
    from ..soldadura.informe import bloque
    from .soldaduras import evaluar
    if sold is None:
        sold = evaluar(modelo, resultados, {n: esfuerzos_extremos(modelo, r) for n, r in resultados.items()})
    uf, ul = canon(modelo.config["unidad_fuerza"]), modelo.config["unidad_longitud"]
    U = {"F": uf, "L": ul, "M": f"{uf}·{ul}", "S": unidad_tension(uf, ul)}
    P = ['<div class="caso"><h2>Soldaduras</h2>',
         "<p class='nota'>Esfuerzos de la cara +x de la barra en el extremo indicado, para cada caso y combinación; el cordón se verifica como grupo de líneas "
         "(método de la garganta).  Fórmulas y fuentes: Memoria del programa de soldaduras.</p>"]
    for s in modelo.soldaduras:
        P.append(bloque(s, sold[s.id], U, titulo=f"Soldadura {s.id} · barra {s.barra}, extremo {s.extremo}"))
    P.append("</div>")
    return "\n".join(P)


def generar_html(modelo: Modelo, resultados: dict, info: Info, sold: dict | None = None) -> str:
    U = _U(modelo)
    cfg = modelo.config
    P = [f"<h1>Memoria de cálculo · Pórtico espacial</h1><div class='sub'>{e_(cfg['proyecto'])}</div>"]
    P.append(tabla(["Dato", "Valor"], [
        ["Proyecto", e_(cfg["proyecto"])], ["Fecha", datetime.date.today().strftime("%d/%m/%Y")],
        ["Archivo de datos", e_(modelo.archivo.name)], ["Programa", f"Struttura {__version__}"],
        ["Unidades", f"fuerza [{U['F']}], longitud [{U['L']}], momento [{U['M']}], tensión [{U['S']}]"],
        ["Método", "Método matricial de rigidez, 6 GDL por nudo, barras de 12×12"],
        ["Datos", f"{modelo.n} nudos, {len(modelo.barras)} barras, {len(modelo.casos)} caso(s)"
                  + (f", {len(modelo.combinaciones)} combinación(es)" if modelo.combinaciones else "")]], clase="datos"))
    for a in modelo.avisos:
        P.append(f'<p class="nota">{e_(a)}</p>' if a.startswith("Nota: ") else f'<div class="aviso"><b>Aviso:</b> {e_(a)}</div>')
    P.append(_convenciones())
    P += _datos(modelo, U)
    P.append("<h2>2. Modelo 3D y resultados</h2>")
    P.append(visor.visor_html(modelo, resultados, "v3d",
                              "Modo: estructura, cargas, deformada, utilización o diagrama (N, Vy, Vz, T, My, Mz); «Barra» permite ver una sola."))
    n = 3
    for nombre, r in resultados.items():
        P.append(f'<div class="caso"><h2>{n}. Resultados · {e_(nombre)}</h2>')
        n += 1
        P.append("<h3>Desplazamientos y giros de los nudos</h3>")
        u = limpiar(r.u)
        P.append(tabla(["Nudo", f"u<sub>x</sub> [{U['L']}]", "u<sub>y</sub>", "u<sub>z</sub>", "φ<sub>x</sub> [rad]", "φ<sub>y</sub>", "φ<sub>z</sub>"],
                       [[modelo.nodos[k].id] + [fe(v) for v in u[k]] for k in range(modelo.n)], num=range(1, 7)))
        filas = [[modelo.nodos[k].id] + [fg(limpiar(r.R)[k, c]) if modelo.restr[k, c] else "" for c in range(6)]
                 for k in range(modelo.n) if modelo.restr[k].any()]
        P.append("<h3>Reacciones</h3>")
        P.append(tabla(["Nudo", f"R<sub>x</sub> [{U['F']}]", "R<sub>y</sub>", "R<sub>z</sub>", f"M<sub>x</sub> [{U['M']}]", "M<sub>y</sub>", "M<sub>z</sub>"], filas, num=range(1, 7)))
        if modelo.resortes.any():
            rk = limpiar(r.Rk)
            filas = [[modelo.nodos[k].id] + [fg(rk[k, c]) if modelo.resortes[k, c] > 0 else "" for c in range(6)] for k in range(modelo.n) if (modelo.resortes[k] > 0).any()]
            P.append("<h3>Fuerza en los resortes (sobre la estructura)</h3>")
            P.append(tabla(["Nudo", "F<sub>x</sub>", "F<sub>y</sub>", "F<sub>z</sub>", "M<sub>x</sub>", "M<sub>y</sub>", "M<sub>z</sub>"], filas, num=range(1, 7)))
        ex = esfuerzos_extremos(modelo, r)
        P.append("<h3>Esfuerzos en los extremos de cada barra (cara +x; i = inicio, j = fin)</h3>")
        filas = []
        for k, b in enumerate(modelo.barras):
            for lab, v in (("i", ex[k]["i"]), ("j", ex[k]["j"])):
                filas.append([b.id, lab] + [fg(x) for x in limpiar(v, 1e-9)])
        P.append(tabla(["Barra", "Extremo", f"N [{U['F']}]", "V<sub>y</sub>", "V<sub>z</sub>", f"T [{U['M']}]", "M<sub>y</sub>", "M<sub>z</sub>"], filas, num=range(2, 8)))
        P.append("<h3>Máximos en el tramo (valor absoluto máximo y abscisa desde i)</h3>")
        filas = [[b.id] + sum(([fg(ex[k]["max"][c]), fg(ex[k]["x_max"][c])] for c in range(6)), []) for k, b in enumerate(modelo.barras)]
        P.append('<div class="scroll">' + tabla(["Barra"] + sum(([NOMBRES[c], "x"] for c in range(6)), []), filas, num=range(1, 13)) + "</div>")
        an = analizar(modelo, r)
        P += _tensiones_html(modelo, r, an, U)
        eq = equilibrio(modelo, r)
        P.append("<h3>Verificación de equilibrio global</h3>")
        P.append(tabla(["", "ΣF<sub>x</sub>", "ΣF<sub>y</sub>", "ΣF<sub>z</sub>", "ΣM<sub>x</sub>", "ΣM<sub>y</sub>", "ΣM<sub>z</sub>"],
                       [["Cargas", *[fg(v) for v in eq["F_cargas"]], *[fg(v) for v in eq["M_cargas"]]],
                        ["Reacciones", *[fg(v) for v in eq["F_reacc"]], *[fg(v) for v in eq["M_reacc"]]],
                        ["Residuo", *[fg(v) for v in eq["res_F"]], *[fg(v) for v in eq["res_M"]]]], num=range(1, 7),
                       nota=f"Momentos respecto del origen.  Error relativo: {eq['rel']:.1e} — "
                            + ('<span class="ok">OK</span>' if eq["rel"] < 1e-8 else "<b>REVISAR</b>")))
        P.append("</div>")

    if modelo.soldaduras:
        P.append(_soldaduras_html(modelo, resultados, sold))
    if cfg["anexo_matrices"] != "no":
        P.append(_anexo(modelo, info))
    return documento(f"Struttura — {cfg['proyecto']}", "\n".join(P))


def generar_html_esquema(modelo: Modelo, aviso: str | None = None) -> str:
    """Solo datos y modelo 3D (sin resolver): sirve para revisar numeración, apoyos, ejes locales y cargas."""
    from .solver import Resultado, _armar, cargas_equivalentes
    U = _U(modelo)
    res = {}
    n = modelo.n
    for nombre, F in modelo.casos.items():
        cb = [(k, c, 1.0) for k, lista in modelo.cargas_barra.get(nombre, {}).items() for c in lista]
        Feq, f0 = cargas_equivalentes(modelo, cb)
        z = np.zeros(6 * n)
        res[nombre] = _armar(modelo, nombre, z, z.copy(), F.reshape(-1), Feq, f0, cb, z.copy())
    P = [f"<h1>Revisión de datos · Pórtico espacial</h1><div class='sub'>{e_(modelo.config['proyecto'])}</div>"]
    if aviso:
        P.append(f'<div class="aviso"><b>Atención (estabilidad):</b> <pre>{e_(aviso)}</pre></div>')
    for a in modelo.avisos:
        P.append(f'<p class="nota">{e_(a)}</p>' if a.startswith("Nota: ") else f'<div class="aviso"><b>Aviso:</b> {e_(a)}</div>')
    P.append(_convenciones())
    P += _datos(modelo, U)
    P.append("<h2>Modelo 3D</h2>")
    P.append(visor.visor_html(modelo, res, "v3d", "Solo datos: elegí el caso para ver sus cargas.  Los diagramas y la deformada aparecen vacíos."))
    return documento(f"Struttura — revisión {modelo.config['proyecto']}", "\n".join(P))
