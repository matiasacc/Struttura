"""Visor 3D interactivo del pórtico espacial (HTML + JavaScript dentro del informe, sin internet).

Muestra barras, nodos, apoyos, cargas, deformada y diagramas de esfuerzos (N, Vy, Vz, T, My, Mz).
Navegación estándar (ver visor_comun.py): girar, Ctrl+arrastrar = desplazar, rueda/Shift = zoom.  Terna derecha global X, Y, Z (Z hacia arriba).
"""
from __future__ import annotations

import json

import numpy as np

from ..emparrillado.entrada import ErrorDeEntrada  # noqa: F401
from .cargas_barra import _formas
from .esfuerzos import NOMBRES, diagramas
from ..visor_comun import AYUDA_3D, CSS_COMUN, NAV_JS
from .tensor import analizar

CSS = """
.visor { margin: 8pt 0 12pt; page-break-inside: avoid; }
.visor .ctrl { font-size: 9.5pt; margin: 0 0 4pt; text-align: left; }
.visor .ctrl button, .visor .ctrl select { font-family: inherit; font-size: 9.5pt; padding: 1pt 8pt;
      border: 1px solid #000; background: #f2f2f2; cursor: pointer; margin-right: 3pt; }
.visor .ctrl label { margin-right: 9pt; white-space: nowrap; }
.visor svg.lienzo { width: 100%; height: auto; border: 1px solid #000; background: #fff; cursor: grab; touch-action: none; user-select: none; }
.visor .pie { font-size: 9.5pt; font-style: italic; text-align: center; }
.contenido table.tensor { font-size: 11pt; margin: 4pt 0 8pt; }
.contenido table.tensor td, .contenido table.tensor th { padding: 2pt 14pt; }
@media print { .visor .ctrl { display: none !important; } .visor svg.lienzo { border: 0; } }
""" + CSS_COMUN

JS = NAV_JS + r"""
function st3d(id, D) {
  var root = document.getElementById(id), NS = "http://www.w3.org/2000/svg", W = 780, H = 560;
  var S = {az: -35, el: 25, base: 1, zoom: 1, ox: 0, oy: 0, caso: 0, modo: "carg", comp: 0, barra: -1, ids: true, cargas: false, val: true, hov: false, unica: D.escala === "global"};
  var VISTAS = {iso: [-35, 25], planta: [0, 90], frente: [0, 0], lateral: [90, 0]};
  var MODOS = ["Estructura", "Cargas", "Deformada", "Utilización", "N", "Vy", "Vz", "T", "My", "Mz"];
  var c0 = D.centro, dim = D.dim, ca, sa, ce, se;
  function fm(v) { if (v === 0) return "0"; var a = Math.abs(v); return (a >= 1e-3 && a < 1e7) ? String(+v.toPrecision(4)) : v.toExponential(2); }
  root.innerHTML = '<div class="ctrl"></div><svg class="lienzo" viewBox="0 0 ' + W + ' ' + H + '"></svg>' +
                   '<div class="pie">' + D.pie + '</div><div class="ayuda">' + D.ayuda + '</div>';
  var ctrl = root.querySelector(".ctrl"), svg = root.querySelector("svg"), selBarra;
  function boton(t, f) { var b = document.createElement("button"); b.textContent = t; b.onclick = f; ctrl.appendChild(b); }
  function lab(t) { var l = document.createElement("label"); l.appendChild(document.createTextNode(t + " ")); ctrl.appendChild(l); return l; }
  function sel(padre, opts, val, f) { var s = document.createElement("select");
    opts.forEach(function (o, i) { var e = document.createElement("option"); e.value = i; e.textContent = o; s.appendChild(e); });
    s.value = val; s.onchange = function () { f(+s.value); }; padre.appendChild(s); return s; }
  function chk(t, k) { var l = document.createElement("label"), c = document.createElement("input");
    c.type = "checkbox"; c.checked = S[k]; c.onchange = function () { S[k] = c.checked; dib(); };
    l.appendChild(c); l.appendChild(document.createTextNode(" " + t)); ctrl.appendChild(l); }
  function camara() { var a = S.az * Math.PI / 180, e = S.el * Math.PI / 180; ca = Math.cos(a); sa = Math.sin(a); ce = Math.cos(e); se = Math.sin(e); }
  function proj(x, y, z) { var x1 = x * ca - y * sa, y1 = x * sa + y * ca; return [x1, -(z * ce + y1 * se)]; }
  function P(p) { var q = proj(p[0] - c0[0], p[1] - c0[1], p[2] - c0[2]), sc = S.base * S.zoom; return [W / 2 + q[0] * sc + S.ox, H / 2 + q[1] * sc + S.oy]; }
  function ajustar(vista) {          // encuadra la estructura completa en la vista actual
    if (vista) { S.az = vista[0]; S.el = vista[1]; }
    camara(); S.zoom = 1; S.ox = 0; S.oy = 0; S.base = 1;
    var lo = [1e300, 1e300], hi = [-1e300, -1e300];
    D.nodos.forEach(function (n) { var q = proj(n[0] - c0[0], n[1] - c0[1], n[2] - c0[2]);
      for (var i = 0; i < 2; i++) { lo[i] = Math.min(lo[i], q[i]); hi[i] = Math.max(hi[i], q[i]); } });
    S.base = Math.min(0.80 * W / Math.max(hi[0] - lo[0], 1e-9), 0.74 * H / Math.max(hi[1] - lo[1], 1e-9));
    S.ox = -S.base * (lo[0] + hi[0]) / 2; S.oy = -S.base * (lo[1] + hi[1]) / 2;
  }
  var modoIdx = 1;
  Object.keys(VISTAS).forEach(function (k) { boton(k, function () { ajustar(VISTAS[k]); dib(); }); });
  boton("Ajustar", function () { ajustar(); dib(); });
  ctrl.appendChild(document.createElement("br"));
  if (D.casos.length > 1) { lab("Caso:"); sel(ctrl, D.casos.map(function (c) { return c.nombre; }), 0, function (v) { S.caso = v; dib(); }); ctrl.appendChild(document.createTextNode(" ")); }
  lab("Modo:"); sel(ctrl, MODOS, 1, function (v) { modoIdx = v; S.modo = v === 0 ? "est" : v === 1 ? "carg" : v === 2 ? "def" : v === 3 ? "util" : "dia"; if (v > 3) S.comp = v - 4;
    selBarra.disabled = !(S.modo === "dia" || S.modo === "util"); dib(); });
  ctrl.appendChild(document.createTextNode(" ")); lab("Barra:");
  selBarra = sel(ctrl, ["todas"].concat(D.barras.map(function (b) { return b.id; })), 0, function (v) { S.barra = v - 1; dib(); });
  selBarra.disabled = true; ctrl.appendChild(document.createTextNode(" "));
  chk("nodos y barras", "ids"); chk("valores", "val"); chk("valor al pasar el mouse", "hov"); chk("superponer cargas", "cargas"); chk("escala única", "unica");

  var g, LT, polis, hits = [];
  function el(t, at, txt) { var e = document.createElementNS(NS, t); for (var k in at) e.setAttribute(k, at[k]); if (txt !== undefined) e.textContent = txt; svg.appendChild(e); return e; }
  function linea(a, b, col, w, dash, op) { LT.l(P(a), P(b), col, w, dash, op); }
  function texto(p, t, col, sz) { var q = P(p); el("text", {x: q[0] + 4, y: q[1] - 4, fill: col, "font-size": sz || 11, "font-family": "sans-serif", stroke: "#fff", "stroke-width": 3, "paint-order": "stroke"}, t); }
  function textoPx(x, y, t, col, sz, anc) { el("text", {x: x, y: y, fill: col, "font-size": sz || 11, "font-family": "sans-serif", "text-anchor": anc || "start"}, t); }
  function punta(q, dx, dy, col) { var key = col, s = 1;
    (polis[key] = polis[key] || []).push("M" + q[0].toFixed(1) + " " + q[1].toFixed(1) + "L" + (q[0] - 9 * dx + 4 * dy).toFixed(1) + " " + (q[1] - 9 * dy - 4 * dx).toFixed(1) +
      "L" + (q[0] - 9 * dx - 4 * dy).toFixed(1) + " " + (q[1] - 9 * dy + 4 * dx).toFixed(1) + "Z"); }
  function flecha(desde, hasta, col, w, doble) {
    var p = P(desde), q = P(hasta); LT.l(p, q, col, w);
    var dx = q[0] - p[0], dy = q[1] - p[1], L = Math.hypot(dx, dy); if (L < 1) return; dx /= L; dy /= L;
    punta(q, dx, dy, col); if (doble) punta([q[0] - 9 * dx, q[1] - 9 * dy], dx, dy, col); }
  function add(a, b, k) { return [a[0] + k * b[0], a[1] + k * b[1], a[2] + k * b[2]]; }
  function sub(a, b) { return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]; }
  function largo(k) { var b = D.barras[k], d = sub(D.nodos[b.j], D.nodos[b.i]); return Math.hypot(d[0], d[1], d[2]); }
  function col(u) {
    var stops = [[0, [42, 157, 143]], [0.5, [233, 196, 106]], [1, [230, 57, 70]], [1.3, [120, 0, 30]]];
    u = Math.max(0, Math.min(1.3, Math.round(u * 40) / 40));
    for (var s = 1; s < stops.length; s++) if (u <= stops[s][0]) { var a = stops[s - 1], b = stops[s], f = (u - a[0]) / (b[0] - a[0]);
      return "rgb(" + [0, 1, 2].map(function (i) { return Math.round(a[1][i] + f * (b[1][i] - a[1][i])); }).join(",") + ")"; }
    return "rgb(120,0,30)"; }

  function dib() {
    camara(); svg.innerHTML = ""; LT = stLotes(NS, svg); polis = {};
    var cs = D.casos[S.caso], m = S.modo, una = S.barra >= 0 && (m === "dia" || m === "util");
    var verCargas = m === "carg" || (m !== "est" && S.cargas);
    // barras (base)
    D.barras.forEach(function (b, k) { var A = D.nodos[b.i], B = D.nodos[b.j], c, w, d = "", op = 1;
      if (m === "def") { c = "#aaa"; w = 1.2; d = "5,4"; }
      else if (m === "util") { c = "#ccc"; w = 1.6; }
      else if (m === "dia") { c = una && k === S.barra ? "#555" : "#b5b5b5"; w = una && k === S.barra ? 2.2 : 1.5; }
      else { c = "#000"; w = 2.4; }
      linea(A, B, c, w, d, op); });
    LT.vaciar();
    // nodos y apoyos (verde = apoyo, naranja = solo resorte); el recuadro muestra las condiciones de borde
    hits = [];
    if (m !== "dia" || !una) D.nodos.forEach(function (n) { var p = P(n); el("circle", {cx: p[0], cy: p[1], r: 2.6, fill: "#000"}); });
    D.apoyos.forEach(function (a, i) { var p = P(D.nodos[a.k]), rig = a.r.some(function (x) { return x; });
      el("circle", {cx: p[0], cy: p[1], r: 6.5, fill: rig ? "#0b7a6b" : "#d98a00", stroke: "#fff", "stroke-width": 1.5});
      hits.push({x: p[0], y: p[1], html: stTexto("Nudo " + D.ids[a.k] + (rig ? " · apoyo" : " · resorte"), ["ux", "uy", "uz", "φx", "φy", "φz"], a.r, cs.apo[i], a.ks, fm, D.unid[0], D.unid[1])}); });
    if (S.ids) { D.barras.forEach(function (b, k) { if (una && k !== S.barra) return; var A = D.nodos[b.i], B = D.nodos[b.j];
        texto(add(A, sub(B, A), 0.5), b.id, "#1a5fb4", 10.5); });
      D.nodos.forEach(function (n, k) { texto(n, D.ids[k], "#000", 10.5); }); }
    // cargas
    if (verCargas) {
      cs.F.forEach(function (f) { var k = f[0], F = [f[1], f[2], f[3]], M = [f[4], f[5], f[6]];
        var nf = Math.hypot(F[0], F[1], F[2]), nm = Math.hypot(M[0], M[1], M[2]), n = D.nodos[k];
        if (nf > 0) { var d = 0.14 * dim / nf; flecha(add(n, F, -d), n, "#c01c28", 2); if (S.val) texto(add(n, F, -d), fm(nf), "#c01c28", 10); }
        if (nm > 0) { var d2 = 0.11 * dim / nm; flecha(add(n, M, -d2), add(n, M, d2 * 0.0), "#9141ac", 2, true); if (S.val) texto(add(n, M, -d2), fm(nm), "#9141ac", 10); } });
      cs.q.forEach(function (q) { var A = D.nodos[D.barras[q.b].i], B = D.nodos[D.barras[q.b].j], n = Math.hypot(q.q[0], q.q[1], q.q[2]); if (!n) return;
        var AB = sub(B, A); for (var s = 0; s <= 2; s++) { var p = add(A, AB, s / 2); flecha(add(p, q.q, -0.1 * dim / q.qmax), p, "#e66100", 1.4); } });
      cs.P.forEach(function (p) { var A = D.nodos[D.barras[p.b].i], B = D.nodos[D.barras[p.b].j], q = add(A, sub(B, A), p.t);
        var n = Math.hypot(p.f[0], p.f[1], p.f[2]); if (n > 0) { flecha(add(q, p.f, -0.12 * dim / n), q, "#c01c28", 2); if (S.val) texto(add(q, p.f, -0.12 * dim / n), fm(n), "#c01c28", 10); } });
    }
    // utilización
    if (m === "util") {
      cs.util.forEach(function (u, k) { if (!u || (una && k !== S.barra)) return; var b = D.barras[k], A = D.nodos[b.i], AB = sub(D.nodos[b.j], A);
        for (var s = 0; s < u.length - 1; s++) linea(add(A, AB, s / (u.length - 1)), add(A, AB, (s + 1) / (u.length - 1)), col(Math.max(u[s], u[s + 1])), una ? 7 : 5);
        for (var s3 = 0; s3 < u.length; s3++) { var q3 = P(add(A, AB, s3 / (u.length - 1)));            // globo al pasar el mouse: utilización en ese punto
          hits.push({x: q3[0], y: q3[1], html: "<b>Barra " + b.id + "</b><br>x = " + fm(largo(k) * s3 / (u.length - 1)) + " " + D.unid[1] + "<br>utilización = <b>" + u[s3].toFixed(3) + "</b>" + (u[s3] > 1 ? " (supera 1)" : "") + (cs.utilA[k] ? "<br>σeq/σadm = <b>" + cs.utilA[k][s3].toFixed(3) + "</b>" + (cs.utilA[k][s3] > 1 ? " (supera 1)" : "") : "")}); } });
      LT.vaciar();
      var gx = W - 190, gy = H - 32; for (var q = 0; q < 100; q++) el("rect", {x: gx + q * 1.5, y: gy, width: 2, height: 10, fill: col(q / 100 * 1.3)});
      textoPx(gx, gy - 4, D.utilrot, "#000", 10);
      [[0, "0"], [0.5, "0,5"], [1, "1"]].forEach(function (t) { textoPx(gx + t[0] / 1.3 * 150 - 3, gy + 22, t[1], "#000", 10); });
    }
    // deformada
    if (m === "def") {
      cs.def.forEach(function (c, k) { for (var s = 0; s < c.length - 1; s++) linea(c[s], c[s + 1], "#d00", 2.2);
        if (S.hov && cs.defu && !(una && k !== S.barra)) c.forEach(function (pt, s) { var q = P(pt), u = cs.defu[k][s];     // recuadro al pasar el mouse: desplazamiento en ese punto
          hits.push({x: q[0], y: q[1], html: "<b>Barra " + D.barras[k].id + "</b><br>x = " + fm(largo(k) * s / (c.length - 1)) + " " + D.unid[1] + "<br>|u| = <b>" + fm(Math.hypot(u[0], u[1], u[2])) + "</b> " + D.unid[1] +
            "<br>ux = " + fm(u[0]) + ", uy = " + fm(u[1]) + ", uz = " + fm(u[2]) }); }); });
      LT.vaciar();
      cs.desp.forEach(function (d) { if (S.val) texto(add(D.nodos[d[0]], d[1], D.escdef), "|u|=" + fm(d[2]), "#d00", 10); });
    }
    // diagramas
    if (m === "dia") {
      var esc = D.escdia[S.comp], sgn = D.signo[S.comp], ax = D.eje[S.comp], vg = 0;
      cs.dia.forEach(function (d) { d.v[S.comp].forEach(function (a) { vg = Math.max(vg, Math.abs(a)); }); });
      cs.dia.forEach(function (d, k) { if (una && k !== S.barra) return;
        var b = D.barras[k], A = D.nodos[b.i], v = d.v[S.comp], vm = 0, im = 0;
        v.forEach(function (a, q) { if (Math.abs(a) > Math.abs(vm)) { vm = a; im = q; } });
        var e1 = una ? (vm ? 0.3 * largo(k) / Math.abs(vm) : 1) : (S.unica ? esc : (vm ? 0.13 * dim / Math.abs(vm) : 1)), dir = [b.R[ax][0] * sgn, b.R[ax][1] * sgn, b.R[ax][2] * sgn];
        var pts = d.xs.map(function (x, q) { var p = add(A, b.R[0], x); return [p, add(p, dir, v[q] * e1)]; });
        var paso = una || D.barras.length <= 30 ? 1 : 2;
        for (var s = 0; s < pts.length; s += paso) linea(pts[s][0], pts[s][1], "#9bb7e6", 0.8);
        for (var s2 = 0; s2 < pts.length - 1; s2++) linea(pts[s2][1], pts[s2 + 1][1], "#1a5fb4", una ? 2.6 : 2);
        if (S.hov) { var un = S.comp < 3 ? D.unid[0] : D.unid[0] + "·" + D.unid[1];               // recuadro al pasar el mouse: valor del esfuerzo en ese punto
          pts.forEach(function (pp, s5) { var h = "<b>Barra " + b.id + "</b><br>x = " + fm(d.xs[s5]) + " " + D.unid[1] + "<br>" + MODOS[modoIdx] + " = <b>" + fm(v[s5]) + "</b> " + un;
            [pp[0], pp[1]].forEach(function (z) { var q = P(z); hits.push({x: q[0], y: q[1], html: h}); }); }); }
        if (S.val && vm !== 0 && (una || Math.abs(vm) >= 0.35 * vg)) texto(pts[im][1], fm(vm), "#1a5fb4", 10.5);
        if (una && S.val) { [0, pts.length - 1].forEach(function (q) { if (Math.abs(v[q]) > 1e-9 * Math.abs(vm) && q !== im) texto(pts[q][1], fm(v[q]), "#555", 10); }); } });
      LT.vaciar();
    }
    // flechas (puntas) acumuladas
    for (var cl in polis) { var e = el("path", {d: polis[cl].join(""), fill: cl}); }
    // triedro fijo en pantalla
    var ox = 44, oy = H - 44, ls = 30;
    [[[1, 0, 0], "X"], [[0, 1, 0], "Y"], [[0, 0, 1], "Z"]].forEach(function (a) { var q = proj(a[0][0], a[0][1], a[0][2]), sx = ls * q[0], sy = ls * q[1], L = Math.hypot(sx, sy);
      if (L > 5) { el("line", {x1: ox, y1: oy, x2: ox + sx, y2: oy + sy, stroke: "#555", "stroke-width": 1.4}); textoPx(ox + sx * 1.3, oy + sy * 1.3 + 4, a[1], "#555", 12, "middle"); }
      else { el("circle", {cx: ox, cy: oy, r: 4, fill: "none", stroke: "#555"}); textoPx(ox + 8, oy + 4, a[1], "#555", 12); } });
    // rótulo de estado
    textoPx(10, 18, (D.casos.length > 1 ? "Caso " + cs.nombre + " · " : "") + MODOS[modoIdx] + (una ? " · barra " + D.barras[S.barra].id : ""), "#000", 12);
    if (m === "dia") textoPx(10, 34, "ordenada hacia " + ["+z", "+y", "+z", "+z", "+z", "−y"][S.comp] + " local; escala " + (una ? "propia de la barra" : "común a todas"), "#555", 10.5);
  }
  stNav(svg, {W: W, rotar: function (dx, dy) { S.az += dx * 0.4; S.el = Math.max(-90, Math.min(90, S.el + dy * 0.4)); },
    pan: function (dx, dy) { S.ox += dx; S.oy += dy; },
    zoomFactor: function (f, mx, my) { stZoomEn(S, f, mx, my, W / 2, H / 2, 0.2, 80); },
    reset: function () { ajustar(VISTAS.iso); }, dib: dib});
  stTip(root, svg, W, function () { return hits; });
  ajustar(VISTAS.iso); dib();
}
"""


def _datos_visor(modelo, resultados, esc_def=None, pie=""):
    P = np.array([nd.p for nd in modelo.nodos])
    centro = ((P.max(axis=0) + P.min(axis=0)) / 2).tolist()
    dim = float(max(np.ptp(P, axis=0).max(), 1e-9))
    nb = len(modelo.barras)
    # escala de deformada
    umax = max((np.abs(r.u[:, :3]).max() for r in resultados.values()), default=0.0)
    esc = modelo.config["escala_deformada"] or (0.08 * dim / umax if umax > 0 else 1.0)
    # escalas de diagramas por componente
    dmax = np.zeros(6)
    dia = {}
    for nombre, r in resultados.items():
        dia[nombre] = [diagramas(modelo, r, k) for k in range(nb)]
        for xs, E in dia[nombre]:
            dmax = np.maximum(dmax, np.abs(E).max(axis=0))
    escdia = [(0.13 * dim / m if m > 0 else 1.0) for m in dmax]
    # rótulos de apoyo
    apoyos = []
    for k in range(modelo.n):
        if modelo.restr[k].any() or modelo.resortes[k].any():
            apoyos.append({"k": k, "r": modelo.restr[k].astype(int).tolist(), "ks": modelo.resortes[k].tolist()})
    barras = [{"id": b.id, "i": b.i, "j": b.j, "R": b.R.tolist()} for b in modelo.barras]
    casos = []
    qmax = max((np.abs(np.concatenate([c[1], c[2]])).max() for r in resultados.values() for kb, c, f in r.cb if c[0] == "q"),
               default=1.0) or 1.0
    for nombre, r in resultados.items():
        F = []
        for k in range(modelo.n):
            if np.abs(r.Ftot[k]).max() > 0 and np.abs(r.F[k]).max() > 0:
                F.append([k, *r.F[k].tolist()])
        q, Pp = [], []
        for kb, c, f in r.cb:
            b = modelo.barras[kb]
            if c[0] == "q":
                v = b.R.T @ ((c[1] + c[2]) / 2 * f)
                q.append({"b": kb, "q": v.tolist(), "qmax": float(qmax)})
            elif c[0] == "P":
                Pp.append({"b": kb, "t": c[1] / b.L, "f": (b.R.T @ (c[2] * f)).tolist()})
        curvas, defu = [], []
        for k, b in enumerate(modelo.barras):
            ub = r.ub[k]
            pts, us = [], []
            for x in np.linspace(0, b.L, 21):
                Nu, Nv, Nw, *_ = _formas(x, b.L)
                dl = np.array([Nu @ ub, Nv @ ub, Nw @ ub])
                pts.append((P[b.i] + b.R[0] * x + esc * (b.R.T @ dl)).tolist())
                us.append([float(a) for a in (b.R.T @ dl)])        # desplazamiento en ejes globales (sin escala)
            curvas.append(pts)
            defu.append(us)
        desp = [[k, (r.u[k, :3] * esc).tolist(), float(np.linalg.norm(r.u[k, :3]))]
                for k in range(modelo.n) if np.linalg.norm(r.u[k, :3]) > 0]
        an = analizar(modelo, r)
        util, utilA = [], []
        for k, d in enumerate(an["barras"]):
            xs = np.array(d["xs"])
            for lista, clave in ((util, "util"), (utilA, "util_adm")):
                lista.append(None if d[clave] is None else np.interp(np.linspace(0, modelo.barras[k].L, 21), xs, d[clave]).round(4).tolist())
        apo = [[float(v) for v in r.u[a["k"], :6]] for a in apoyos]
        casos.append({"nombre": nombre, "apo": apo, "util": util, "utilA": utilA, "F": F, "q": q, "P": Pp, "def": curvas, "defu": defu,
                      "desp": desp,
                      "dia": [{"xs": dia[nombre][k][0].tolist(), "v": dia[nombre][k][1].T.tolist()} for k in range(nb)]})
    return {"nodos": P.tolist(), "ids": [nd.id for nd in modelo.nodos], "centro": centro, "dim": dim, "barras": barras,
            "apoyos": apoyos, "casos": casos, "escdef": 1.0, "escdia": escdia, "escala": modelo.config["escala_diagramas"],
            "unid": [modelo.config["unidad_fuerza"], modelo.config["unidad_longitud"]], "signo": [1, 1, 1, 1, 1, -1], "eje": [2, 1, 2, 2, 2, 1], "pie": pie, "ayuda": AYUDA_3D + " · En modo Utilización, pasá el mouse sobre una barra para ver el valor en ese punto",
            "utilrot": "utilización = σeq/fy (o 1/CS)"}


def visor_html(modelo, resultados, id_, pie=""):
    D = _datos_visor(modelo, resultados, pie=pie)
    return f'<div class="visor" id="{id_}"></div><script>st3d("{id_}", {json.dumps(D, separators=(",", ":"))});</script>'
