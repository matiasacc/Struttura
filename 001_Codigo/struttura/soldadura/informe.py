"""Informe HTML de soldaduras: tabla de resultados y dibujo 2D del cordón coloreado por la fuerza por unidad de longitud."""
from __future__ import annotations

import datetime
import html
import math

import numpy as np

from .. import __version__
from ..emparrillado.formato import fg
from ..emparrillado.informe import CSS as CSS_BASE, tabla, unidad_tension
from .datos import canon

e_ = html.escape
COMP = ("N", "V<sub>y</sub>", "V<sub>z</sub>", "T", "M<sub>y</sub>", "M<sub>z</sub>")


def documento(titulo: str, cuerpo: str) -> str:
    return (f"<!DOCTYPE html><html lang='es'><head><meta charset='utf-8'><title>{e_(titulo)}</title><style>{CSS_BASE}</style></head><body>"
            '<table class="hoja"><thead><tr><td><div class="esp"></div></td></tr></thead><tbody><tr><td>'
            f'<div class="contenido">{cuerpo}'
            '<div class="boton-imprimir no-print"><button onclick="window.print()">Imprimir</button></div></div>'
            '</td></tr></tbody><tfoot><tr><td><div class="esp"></div></td></tr></tfoot></table></body></html>')


def _color(t: float) -> str:
    """t en [0, 1]: azul grisáceo → verde agua → verde claro → arena → terracota (paleta suave, interpolación continua)."""
    t = min(max(t, 0.0), 1.0)
    stops = [(0.0, (74, 111, 165)), (0.25, (96, 165, 172)), (0.5, (152, 196, 132)), (0.75, (236, 204, 112)), (1.0, (214, 110, 90))]
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        if t <= b:
            u = (t - a) / (b - a)
            u = u * u * (3 - 2 * u)                                  # suavizado (smoothstep) dentro de cada tramo
            return "rgb({},{},{})".format(*[int(round(ca[i] + (cb[i] - ca[i]) * u)) for i in range(3)])
    return "rgb(214,110,90)"


def dibujo_svg(grupo, res, U, punto_carga=None, ancho=560, alto=420, tope=None) -> str:
    """Dibujo 2D del cordón (plano y–z, y a la derecha, z arriba), coloreado de forma continua por f (filete) o por σ_VM (tope).
    tope: espesor (garganta) de la unión a tope, o None para filete."""
    pts = grupo.puntos(fino=True)
    y = np.array([p[0] for p in pts])
    z = np.array([p[1] for p in pts])
    if tope:
        ky, kz = grupo.escala_fibra
        fx, fy, fz = grupo.fuerza(res["E_orig"], grupo.yg + (y - grupo.yg) * ky, grupo.zg + (z - grupo.zg) * kz, res.get("punto_carga"))
        f = np.sqrt((fx / tope) ** 2 + 3 * ((fy / tope) ** 2 + (fz / tope) ** 2))
        etiqueta, unidad = "σ VM máx", U["S"]
    else:
        fx, fy, fz = grupo.fuerza(res["E_orig"], y, z, res.get("punto_carga"))
        f = np.sqrt(fx**2 + fy**2 + fz**2)
        etiqueta, unidad = "f máx", f"{U['F']}/{U['L']}"
    fm = float(max(f.max(), 1e-300))
    cy_ = [p[0] for pl in grupo.contorno for p in pl]
    cz_ = [p[1] for pl in grupo.contorno for p in pl]
    xs = list(y) + cy_ + [grupo.yg] + ([punto_carga[0]] if punto_carga else [])
    zs = list(z) + cz_ + [grupo.zg] + ([punto_carga[1]] if punto_carga else [])
    ymin, ymax, zmin, zmax = min(xs), max(xs), min(zs), max(zs)
    sy, sz = ymax - ymin or 1.0, zmax - zmin or 1.0
    m = 55
    esc = min((ancho - 2 * m - 70) / sy, (alto - 2 * m) / sz)
    X = lambda v: m + (v - ymin) * esc
    Z = lambda v: alto - m - (v - zmin) * esc
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ancho} {alto}" width="{ancho}" height="{alto}" style="max-width:100%;height:auto;background:#fff">']
    for pl in grupo.contorno:                                       # contorno de la sección, fino y gris
        pts_ = " ".join(f"{X(a):.1f},{Z(b):.1f}" for a, b in pl)
        o.append(f'<polyline points="{pts_}" fill="none" stroke="#8a8a8a" stroke-width="1.2"/>')
    for k in range(len(pts) - 1):
        if pts[k][2] != pts[k + 1][2]:
            continue
        c = _color(float((f[k] + f[k + 1]) / 2 / fm))
        o.append(f'<line x1="{X(y[k]):.1f}" y1="{Z(z[k]):.1f}" x2="{X(y[k + 1]):.1f}" y2="{Z(z[k + 1]):.1f}" stroke="{c}" stroke-width="6" stroke-linecap="round"/>')
    # baricentro del grupo, punto de carga y punto crítico
    gx, gz = X(grupo.yg), Z(grupo.zg)
    o.append(f'<path d="M{gx - 7:.1f} {gz:.1f}H{gx + 7:.1f}M{gx:.1f} {gz - 7:.1f}V{gz + 7:.1f}" stroke="#000" stroke-width="1.5"/>')
    o.append(f'<text x="{gx + 9:.1f}" y="{gz - 7:.1f}" font-size="11">G</text>')
    if punto_carga:
        px, pz = X(punto_carga[0]), Z(punto_carga[1])
        o.append(f'<path d="M{px - 6:.1f} {pz - 6:.1f}L{px + 6:.1f} {pz + 6:.1f}M{px - 6:.1f} {pz + 6:.1f}L{px + 6:.1f} {pz - 6:.1f}" stroke="#000" stroke-width="2"/>')
        o.append(f'<text x="{px + 9:.1f}" y="{pz - 7:.1f}" font-size="11">carga</text>')
    # ejes
    ox, oz = 14, alto - 14
    o.append(f'<path d="M{ox} {oz}h34M{ox} {oz}v-34" stroke="#444" stroke-width="1"/><text x="{ox + 36}" y="{oz + 4}" font-size="11">y</text><text x="{ox - 3}" y="{oz - 38}" font-size="11">z</text>')
    # barra de colores
    bx, by, bh = ancho - 52, m, alto - 2 * m
    for k in range(60):
        o.append(f'<rect x="{bx}" y="{by + bh * k / 60:.1f}" width="14" height="{bh / 60 + 0.6:.1f}" fill="{_color(1 - k / 59)}"/>')
    o.append(f'<text x="{bx + 14}" y="{by - 20}" font-size="11" text-anchor="end">{etiqueta}</text><text x="{bx + 14}" y="{by - 6}" font-size="11" text-anchor="end">{fg(fm)} {unidad}</text>'
             f'<text x="{bx + 18}" y="{by + bh}" font-size="10">0</text>')
    o.append("</svg>")
    return "".join(o)


def _bloque_tope(sol, resultados, U, titulo=None) -> str:
    g = sol.grupo
    P = [f"<h3>{e_(titulo or 'Soldadura a tope ' + sol.id)}</h3>"]
    r0 = resultados[0][3]
    filas = [["Tipo", "A tope, penetración completa (garganta = espesor de las piezas, sin refuerzo)"], ["Disposición", e_(g.descripcion)],
             ["Origen de coordenadas", e_(g.origen)], ["Electrodo", e_(sol.electrodo)],
             ["Espesor (garganta) t", f"{fg(sol.esp)} {U['L']}"], ["Longitud del cordón (línea media)", f"{fg(g.Lw)} {U['L']}"],
             ["S<sub>y</sub> de referencia (el menor entre aporte y base)", f"{fg(r0['sy_ref'])} {U['S']}"],
             ["σ<sub>adm</sub> = 0,60·S<sub>y</sub> · τ<sub>adm</sub>", f"{fg(r0['sig_adm'])} · {fg(r0['tau_adm'])} {U['S']}"]]
    P.append(tabla(["Dato", "Valor"], filas))
    cab = ["Caso", f"σ máx [{U['S']}]", f"τ máx [{U['S']}]", f"σ<sub>VM</sub> máx [{U['S']}]", "CS σ (0,60·S<sub>y</sub>)", "CS τ", "CS Von Mises (S<sub>y</sub>/σ<sub>VM</sub>)",
           f"t aprox. requerido [{U['L']}]", "Estado"]
    rows = []
    for caso, E, punto, r in resultados:
        rows.append([e_(str(caso)), fg(r["sig_max"]), fg(r["tau_max"]), fg(r["vm_max"]), fg(r["cs_sig"]), fg(r["cs_tau"]), fg(r["cs_vm"]), fg(r["t_req"]),
                     '<span class="ok">CUMPLE</span>' if r["cumple"] else "<b>NO CUMPLE</b>"])
    P.append(tabla(cab, rows, num=range(1, 8)))
    peor = min(resultados, key=lambda t: min(t[3]["cs_sig"], t[3]["cs_tau"]))
    r = peor[3]
    nota = [f"Gobierna el caso <b>{e_(str(peor[0]))}</b>. Veredicto por los admisibles de la Tabla 9-4 de Shigley (σ ≤ 0,60·S<sub>y</sub>, τ ≤ 0,30·S<sub>ut</sub> del electrodo y 0,40·S<sub>y</sub> del base); "
            "el CS de Von Mises (cargas combinadas, Compendio cap. 18) contra la fluencia se informa aparte."]
    if r["cs_sig"] < 1 <= r["cs_vm"]:
        nota.append("Con σ y τ combinadas por Von Mises la unión resiste la fluencia, pero <b>no cumple el admisible 0,60·S<sub>y</sub></b> de la tabla.")
    nota.append("El espesor requerido es aproximado: supone el mismo diámetro / lados y que la tensión varía con 1/t.")
    for t in resultados:
        for a in t[3]["avisos"]:
            nota.append(f"<b>Aviso ({e_(str(t[0]))}):</b> {e_(a)}")
    P.append("<p class='nota'>" + "<br>".join(nota) + "</p>")
    filas = [[e_(str(c))] + [fg(v) for v in E] + ["—" if p is None else f"({fg(p[0])}; {fg(p[1])})"] for c, E, p, _ in resultados]
    P.append(tabla(["Caso"] + [c + (f" [{U['F']}]" if k < 3 else f" [{U['M']}]") for k, c in enumerate(COMP)] + ["Punto de aplicación"], filas, num=range(1, 7)))
    r["E_orig"], r["punto_carga"] = peor[1], peor[2]
    P.append(f"<div class='dib'>{dibujo_svg(g, r, U, peor[2], tope=sol.esp)}</div><p class='nota'>Cordón coloreado por la tensión de Von Mises σ<sub>VM</sub> = √(σ² + 3τ²) "
             f"(caso {e_(str(peor[0]))}); σ y τ en la fibra exterior. G = baricentro del grupo.</p>")
    return "\n".join(P)


_AST = '<b style="color:#c0392b">*</b>'


def _supera(r):
    """El pie a adoptar supera el espesor de la pieza más delgada (el criterio queda a cargo del diseñador)."""
    return bool(r.get("w_max")) and r["w_adoptar"] > r["w_max"] + 1e-9


def _ast(r):
    return _AST if _supera(r) else ""


def bloque(sol, resultados, U, titulo=None) -> str:
    """HTML de una soldadura: datos, resultado por carga y dibujo del caso más exigido.  resultados: [(caso, E, punto, res)]."""
    if sol.tipo == "tope":
        return _bloque_tope(sol, resultados, U, titulo)
    g = sol.grupo
    P = [f"<h3>{e_(titulo or 'Soldadura ' + sol.id)}</h3>"]
    filas = [["Disposición", e_(g.descripcion)], ["Origen de coordenadas", e_(g.origen)],
             ["Electrodo", e_(sol.electrodo)],
             ["Longitud total del cordón", f"{fg(g.Lw)} {U['L']}"],
             ["Baricentro del grupo (y, z)", f"({fg(g.yg)}; {fg(g.zg)}) {U['L']}"],
             ["Propiedades como línea", f"I<sub>yu</sub> = {fg(g.Iyu)} · I<sub>zu</sub> = {fg(g.Izu)} · J<sub>u</sub> = {fg(g.Ju)} {U['L']}³"]]
    if sol.w:
        filas.append(["Pie del filete w (cateto) · garganta t = 0,707·w", f"w = {fg(sol.w)} {U['L']} · t = {fg(0.707 * sol.w)} {U['L']}"])
    if sol.sy_base:
        filas.append(["Fluencia del metal base", f"{fg(sol.sy_base)} {U['S']}"])
    P.append(tabla(["Dato", "Valor"], filas))
    cab = ["Caso", "f<sub>máx</sub> [" + f"{U['F']}/{U['L']}]", "Punto crítico (y; z)", f"τ<sub>adm</sub> [{U['S']}]", f"w requerido [{U['L']}] (garganta t)", f"w a adoptar [{U['L']}] (garganta t)"]
    if sol.w:
        cab += [f"τ [{U['S']}]", "CS código", "CS base", "Estado"]
    rows = []
    for caso, E, punto, r in resultados:
        fila = [e_(str(caso)), fg(r["fmax"]), f"({fg(r['punto'][0])}; {fg(r['punto'][1])})", fg(r["tau_adm"]),
                f'{fg(r["w_req"])}<br><span class="nota">t = {fg(r["t_req"])}</span>', f'{fg(r["w_adoptar"])}{_ast(r)}<br><span class="nota">t = {fg(r["t_adoptar"])}</span>']
        if sol.w:
            fila += [fg(r["tau"]), fg(r["cs_cod"]), "—" if r["cs_base"] is None else fg(r["cs_base"]),
                     ('<span class="ok">CUMPLE</span>' if r["cumple"] else "<b>NO CUMPLE</b>")]
        rows.append(fila)
    P.append(tabla(cab, rows, num=range(1, len(cab) - (1 if sol.w else 0))))
    nota = []
    peor = max(resultados, key=lambda t: t[3]["fmax"])
    r = peor[3]
    nota.append(f"Gobierna el caso <b>{e_(str(peor[0]))}</b>; el pie requerido w = {fg(r['w_req'])} {U['L']} (garganta t = {fg(r['t_req'])} {U['L']}) lo fija el <b>{r['gobierna']}</b> "
                f"(aporte: {fg(r['w_req_aporte'])}" + (f"; base: {fg(r['w_req_base'])}" if r["w_req_base"] else "") + ").")
    if r["w_min"]:
        nota.append(f"Pie mínimo por espesor (Tabla 9-6 B de Shigley): {fg(r['w_min'])} {U['L']}.  \"w a adoptar\" = mayor entre el requerido y el mínimo.")
    if r["w_max"]:
        nota.append(f"El pie no debe superar el espesor de la pieza más delgada: {fg(r['w_max'])} {U['L']}.")
    for t in resultados:
        if _supera(t[3]):
            q = t[3]
            motivo = (f"el mínimo de la Tabla 9-6 B ({fg(q['w_min'])} {U['L']}) supera" if (q["w_min"] or 0) > q["w_max"] + 1e-9
                      else f"el pie requerido ({fg(q['w_req'])} {U['L']}) supera")
            nota.append(f"{_AST} En el caso <b>{e_(str(t[0]))}</b>, {motivo} el espesor de la pieza más delgada ({fg(q['w_max'])} {U['L']}). "
                        "Se deja a criterio del diseñador.")
            break
    for t in resultados:
        for a in t[3]["avisos"]:
            nota.append(f"<b>Aviso ({e_(str(t[0]))}):</b> {e_(a)}")
    if r.get("cs_conv"):
        nota.append(f"CS convencional (0,577·S<sub>y</sub> del aporte / τ) en el caso gobernante: {fg(r['cs_conv'])}.")
    P.append("<p class='nota'>" + "<br>".join(nota) + "</p>")
    # esfuerzos de cada caso
    filas = []
    for caso, E, punto, r in resultados:
        filas.append([e_(str(caso))] + [fg(v) for v in E] + ["—" if punto is None else f"({fg(punto[0])}; {fg(punto[1])})"])
    P.append(tabla(["Caso"] + [c + (f" [{U['F']}]" if i < 3 else f" [{U['M']}]") for i, c in enumerate(COMP)] + ["Punto de aplicación"], filas, num=range(1, 8),
                   nota="Esfuerzos aplicados en el punto indicado (o en el origen del grupo); el programa los traslada al baricentro del grupo."))
    r = peor[3]
    r["E_orig"] = peor[1]
    r["punto_carga"] = peor[2]
    P.append(f"<div class='dib'>{dibujo_svg(g, r, U, peor[2])}</div><p class='nota'>Cordón coloreado por la fuerza por unidad de longitud f (caso {e_(str(peor[0]))}). "
             "G = baricentro del grupo.  El espesor del trazo no está a escala.</p>")
    return "\n".join(P)


def generar_html(modelo, resultados_por_sol) -> str:
    """resultados_por_sol: {id: [(caso, E, punto, res)]}"""
    cfg = modelo.config
    uf, ul = canon(cfg["unidad_fuerza"]), cfg["unidad_longitud"]
    U = {"F": uf, "L": ul, "M": f"{uf}·{ul}", "S": unidad_tension(uf, ul)}
    P = [f"<h1>Verificación de soldaduras</h1><div class='sub'>{e_(cfg['proyecto'])} · Struttura v{__version__} · {datetime.date.today():%d/%m/%Y}</div>"]
    for a in modelo.avisos:
        P.append(f'<p class="nota">{e_(a)}</p>' if a.startswith("Nota: ") else f'<div class="aviso"><b>Aviso:</b> {e_(a)}</div>')
    P.append("<p class='nota'>Convenciones: w = pie (cateto) del filete y t = 0,707·w = garganta (distancia desde la raíz perpendicular a la hipotenusa); x = eje de la barra (normal al plano de los cordones); y, z en el plano de los cordones; N tracción +; "
             "T = momento alrededor de x. Las fórmulas y fuentes usadas están en la Memoria del programa de soldaduras.</p>")
    for s in modelo.soldaduras:
        if s.id in resultados_por_sol:
            P.append(bloque(s, resultados_por_sol[s.id], U))
    return documento(f"Struttura — soldaduras {cfg['proyecto']}", "\n".join(P))
