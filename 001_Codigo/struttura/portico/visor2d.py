"""Visor 2D interactivo (HTML + JavaScript incluidos en el propio informe; no usa internet).

Muestra el pórtico: barras, articulaciones, apoyos, resortes, cargas (nodales y en tramos), la deformada y los
diagramas de N, V y M.  Navegación estándar de Struttura (ver visor_comun.py): arrastrar = desplazar, rueda/Shift = zoom.

Colores:  Px azul · Py, P, q rojo · M ámbar · ΔT violeta.
Fuerza: flecha con la punta en el punto de aplicación.  Momento: arco con flecha (antihorario si es positivo).
Diagramas: N y V con ordenada hacia +yl (izquierda de i→j); M hacia la fibra traccionada (−yl), como en el informe.
"""
from __future__ import annotations

import json

import numpy as np

from ..falla_plana import referencia
from ..visor_comun import AYUDA_2D, CSS_COMUN, NAV_JS
from .esfuerzos import elastica, esfuerzos, tensiones
from .graficos import COL_M, COL_PX, COL_PY, COL_TEMP, escala_auto

CSS = """
.visor { margin: 8pt 0 12pt; page-break-inside: avoid; break-inside: avoid; }
.visor .ctrl { font-size: 9.5pt; margin: 0 0 4pt; text-align: left; }
.visor .ctrl button, .visor .ctrl select { font-family: inherit; font-size: 9.5pt; padding: 1pt 8pt;
      border: 1px solid #000; background: #f2f2f2; cursor: pointer; margin-right: 3pt; }
.visor .ctrl button:hover { background: #e2e2e2; }
.visor .ctrl label { margin-right: 9pt; white-space: nowrap; }
.visor svg.lienzo { width: 100%; height: auto; border: 1px solid #000; background: #fff; cursor: grab;
      touch-action: none; user-select: none; -webkit-user-select: none; }
.visor svg.lienzo:active { cursor: grabbing; }
.visor .pie { font-size: 9.5pt; font-style: italic; text-align: center; }
@media print { .visor .ctrl { display: none !important; } .visor svg.lienzo { border: 0; } }
""" + CSS_COMUN

LIB_JS = r"""
function emp2d(id, D) {
  var root = document.getElementById(id);
  var W = 760, H = 520, NS = "http://www.w3.org/2000/svg";
  var C = {px: "%(PX)s", py: "%(PY)s", m: "%(M)s", t: "%(T)s", r: "#0b7a6b"};
  var st = {esc: 0, zoom: 1, ox: 0, oy: 0, dia: "", modo: "carg", barra: -1, base: "fy", unica: D.escala === "global",
            sw: {carg: false, val: true, hov: false, ids: true, apo: true}};
  function fm(v) { if (v === 0) return "0"; var a = Math.abs(v);
    return (a >= 1e-3 && a < 1e7) ? String(+v.toPrecision(4)) : v.toExponential(3); }

  var xs = D.nodos.map(function (n) { return n[0]; }), ys = D.nodos.map(function (n) { return n[1]; });
  var x0 = Math.min.apply(null, xs), x1 = Math.max.apply(null, xs), y0 = Math.min.apply(null, ys), y1 = Math.max.apply(null, ys);
  var cx = (x0 + x1) / 2, cy = (y0 + y1) / 2, ext = Math.max(x1 - x0, y1 - y0, 1e-9);
  var S0 = Math.min((W - 300) / Math.max(x1 - x0, ext * 0.25), (H - 220) / Math.max(y1 - y0, ext * 0.25));
  // ---- máximos para escalar cargas (comunes a todos los casos) ----
  var maxF = 1e-300, maxM = 1e-300, maxQ = 1e-300;
  D.escenas.forEach(function (e) {
    e.F.forEach(function (f) { maxF = Math.max(maxF, Math.abs(f[0]), Math.abs(f[1])); maxM = Math.max(maxM, Math.abs(f[2])); });
    e.P.forEach(function (p) { maxF = Math.max(maxF, Math.abs(p[1]), Math.abs(p[2])); });
    e.M.forEach(function (m) { maxM = Math.max(maxM, Math.abs(m[1])); });
    e.q.forEach(function (q) { maxQ = Math.max(maxQ, Math.hypot(q[1], q[3]), Math.hypot(q[2], q[4])); });
  });
  function T(x, y) { var s = S0 * st.zoom; return [W / 2 + 50 + (x - cx) * s + st.ox, H / 2 + 10 - (y - cy) * s + st.oy]; }

  var svg, gr, hits = [];
  function el(tag, at) { var e = document.createElementNS(NS, tag);
    for (var k in at) e.setAttribute(k, at[k]); gr.appendChild(e); return e; }
  function lin(a, b, col, w, dash) { el("line", {x1: a[0], y1: a[1], x2: b[0], y2: b[1], stroke: col, "stroke-width": w,
      "stroke-linecap": "round", "stroke-dasharray": dash || ""}); }
  function txt(x, y, t, col, sz, anc, it, bold) { var e = el("text", {x: x, y: y, fill: col, "font-size": sz || 11,
      "text-anchor": anc || "middle", "font-family": "'Times New Roman',serif", "font-style": it ? "italic" : "normal",
      stroke: "#fff", "stroke-width": 3, "paint-order": "stroke"}); if (bold) e.setAttribute("font-weight", "bold"); e.textContent = t; }
  function flecha(A, B, col, w) {                      // A: cola, B: punta (pantalla)
    var dx = B[0] - A[0], dy = B[1] - A[1], L = Math.hypot(dx, dy); if (L < 1) return;
    var u = [dx / L, dy / L], hl = Math.min(10, L * 0.6);
    lin(A, [B[0] - u[0] * hl * 0.8, B[1] - u[1] * hl * 0.8], col, w || 2);
    var bx = B[0] - u[0] * hl, by = B[1] - u[1] * hl;
    el("polygon", {points: B[0] + "," + B[1] + " " + (bx - u[1] * 3.6) + "," + (by + u[0] * 3.6) + " " + (bx + u[1] * 3.6) + "," + (by - u[0] * 3.6), fill: col}); }
  function arco(P, ccw, col) {                         // momento: arco con flecha; en pantalla el eje y está invertido
    var r = 15, pts = [], a0 = 35, a1 = 300;
    for (var i = 0; i <= 30; i++) { var a = (a0 + (a1 - a0) * i / 30) * Math.PI / 180; if (!ccw) a = (a0 + a1) * Math.PI / 180 - a;
      pts.push([P[0] + r * Math.cos(a), P[1] - r * Math.sin(a)]); }
    el("polyline", {points: pts.map(function (p) { return p.join(","); }).join(" "), fill: "none", stroke: col, "stroke-width": 2});
    var n = pts.length; flecha(pts[n - 3], pts[n - 1], col, 2); }
  function vg(g, cx_, cy_) { return [g[0] * cx_ - g[1] * cy_, g[1] * cx_ + g[0] * cy_]; }   // local -> global
  function pos(k, x) { var A = D.nodos[D.barras[k][0]], g = D.g[k]; return [A[0] + g[0] * x, A[1] + g[1] * x]; }

  function mejor(k, cand) {                            // dirección (°) alejada de las barras del nodo; devuelve vector de pantalla
    var A = D.nodos[k], angs = [];
    D.barras.forEach(function (b) { if (b[0] === k || b[1] === k) { var O = D.nodos[b[0] === k ? b[1] : b[0]]; angs.push(Math.atan2(O[1] - A[1], O[0] - A[0]) * 180 / Math.PI); } });
    var best = cand[0], bh = -1;
    cand.forEach(function (c) { var h = 360; angs.forEach(function (a) { h = Math.min(h, Math.abs(((c - a + 540) - 360 * Math.floor((c - a + 540) / 360)) - 180)); }); if (h > bh) { bh = h; best = c; } });
    var r = best * Math.PI / 180; return [Math.cos(r), -Math.sin(r)]; }
  function resorte(p, u, len, col, rot) {              // resorte lineal: zigzag desde el nodo hasta un empotramiento (rayado)
    var nx = -u[1], ny = u[0], lead = 0.16 * len, nz = 7, body = len - 2 * lead, pts = [p, [p[0] + u[0] * lead, p[1] + u[1] * lead]];
    for (var i = 0; i < nz; i++) { var t = lead + body * (i + 0.5) / nz, sg = (i - 2 * Math.floor(i / 2) ? -1 : 1) * 6; pts.push([p[0] + u[0] * t + nx * sg, p[1] + u[1] * t + ny * sg]); }
    var e = [p[0] + u[0] * (len - lead), p[1] + u[1] * (len - lead)], f = [p[0] + u[0] * len, p[1] + u[1] * len]; pts.push(e); pts.push(f);
    el("polyline", {points: pts.map(function (q) { return q.join(","); }).join(" "), fill: "none", stroke: col, "stroke-width": 1.7, "stroke-linejoin": "round"});
    lin([f[0] + nx * 10, f[1] + ny * 10], [f[0] - nx * 10, f[1] - ny * 10], col, 2);
    for (var j = -2; j <= 2; j++) lin([f[0] + nx * 5 * j, f[1] + ny * 5 * j], [f[0] + nx * 5 * j + u[0] * 5 + nx * 3, f[1] + ny * 5 * j + u[1] * 5 + ny * 3], col, 1);
    if (rot) txt(p[0] + u[0] * len * 0.55 + nx * 15, p[1] + u[1] * len * 0.55 + ny * 15, "resorte " + rot, col, 10); }
  function resTors(p, col) {                           // resorte torsional: espiral alrededor del nodo + rayado de anclaje
    var pts = [];
    for (var i = 0; i <= 60; i++) { var a = i / 60 * 4.5 * Math.PI, r = 4 + 11 * i / 60; pts.push([p[0] + r * Math.cos(a), p[1] - r * Math.sin(a)]); }
    el("polyline", {points: pts.map(function (q) { return q.join(","); }).join(" "), fill: "none", stroke: col, "stroke-width": 1.7});
    var q = pts[60]; lin(q, [q[0] + 14, q[1]], col, 1.7); lin([q[0] + 14, q[1] - 8], [q[0] + 14, q[1] + 8], col, 2);
    txt(q[0] + 32, q[1] + 18, "resorte torsional k\u03c6", col, 10, "start"); }
  function partes(x, v) {                              // parte una curva donde cambia de signo
    var out = [], px = [x[0]], pv = [v[0]];
    for (var i = 1; i < x.length; i++) {
      if (pv[pv.length - 1] * v[i] < 0) { var t = pv[pv.length - 1] / (pv[pv.length - 1] - v[i]), xc = px[px.length - 1] + t * (x[i] - px[px.length - 1]);
        px.push(xc); pv.push(0); out.push([px, pv]); px = [xc]; pv = [0]; }
      px.push(x[i]); pv.push(v[i]); }
    out.push([px, pv]); return out; }

  function dibujar() {
    while (gr.firstChild) gr.removeChild(gr.firstChild);
    var es = D.escenas[st.esc], verDef = st.modo === "def" && es.def, verC = st.modo === "carg" || (st.modo !== "est" && st.sw.carg),
        una = st.barra >= 0 && !!st.dia, s = S0 * st.zoom;
    // barras
    var verU = st.modo === "util" && es.vm, unaU = verU && st.barra >= 0, hitsU = [];
    D.barras.forEach(function (b, k) { var A = T(D.nodos[b[0]][0], D.nodos[b[0]][1]), B = T(D.nodos[b[1]][0], D.nodos[b[1]][1]);
      if (verU) { var v = es.vm[k], fy = D.fy[k], sa = D.sadm[k], base = st.base === "sadm" ? sa : fy;
        if (!v || !base || (unaU && k !== st.barra)) { lin(A, B, unaU && k !== st.barra ? "#b5b5b5" : "#999", 2.4, "4,3"); return; }
        var m = v.length - 1;
        for (var q = 0; q < m; q++) lin([A[0] + (B[0] - A[0]) * q / m, A[1] + (B[1] - A[1]) * q / m], [A[0] + (B[0] - A[0]) * (q + 1) / m, A[1] + (B[1] - A[1]) * (q + 1) / m],
                                        stColU(Math.max(v[q], v[q + 1]) / base), unaU ? 7 : 5, "");
        for (var q2 = 0; q2 <= m; q2++) hitsU.push({x: A[0] + (B[0] - A[0]) * q2 / m, y: A[1] + (B[1] - A[1]) * q2 / m, html: stTextoU(D.bid[k], D.L[k] * q2 / m, v[q2], fy, sa, fm, D.unid[0] + "/" + D.unid[1] + "\u00b2", D.unid[1], D.refn[k])});
        return; }
      lin(A, B, verDef ? "#9a9a9a" : st.dia ? (una && k === st.barra ? "#555" : "#b5b5b5") : "#000", verDef ? 1.4 : st.dia ? 2.2 : 3, ""); });
    // apoyos y resortes
    if (st.sw.apo) D.nodos.forEach(function (n, k) { var p = T(n[0], n[1]), r = D.restr[k], sp = D.resortes[k];
      if (sp[0]) resorte(p, mejor(k, [180, 0]), 46, C.r, "kx");
      if (sp[1]) resorte(p, mejor(k, [-90, 90]), 46, C.r, "ky");
      if (sp[2]) resTors(p, C.r);
      D.incl.forEach(function (ic) { if (ic[0] === k) { resorte(p, mejor(k, [ic[1] + 180, ic[1]]), 50, C.r, "k incl. " + fm(ic[1]) + "\u00b0"); } });
    });
    // leyenda de resortes
    if (st.sw.apo && (D.incl.length || D.resortes.some(function (q) { return q[0] || q[1] || q[2]; }))) {
      resorte([14, H - 18], [1, 0], 34, C.r, ""); txt(64, H - 14, "resorte (elemento elástico; NO es una barra)", C.r, 10.5, "start"); }
    // articulaciones
    D.barras.forEach(function (b, k) { [[D.art[k][0], 0.045], [D.art[k][1], 0.955]].forEach(function (a) { if (a[0]) { var q = pos(k, a[1] * D.L[k]), p = T(q[0], q[1]);
      el("circle", {cx: p[0], cy: p[1], r: 4.5, fill: "#fff", stroke: "#000", "stroke-width": 1.4}); } }); });
    // diagramas
    if (st.dia) {
      var series = es.dia[st.dia], lado = st.dia === "M" ? -1 : 1, vmax = 1e-300;
      series.forEach(function (sr) { sr.v.forEach(function (v) { vmax = Math.max(vmax, Math.abs(v)); }); });
      series.forEach(function (sr, k) { var vk = 1e-300; sr.v.forEach(function (v) { vk = Math.max(vk, Math.abs(v)); });
        if (vk <= 1e-6 * vmax || (una && k !== st.barra)) return;
        var g = D.g[k], nx = -g[1] * lado, ny = g[0] * lado, esc = (una ? 0.3 * D.L[k] : 0.13 * ext) / (st.unica && !una ? vmax : vk);
        function P(x, v) { var q = pos(k, x); return T(q[0] + v * esc * nx, q[1] + v * esc * ny); }
        if (st.sw.hov) { var un = st.dia === "M" ? D.unid[0] + "\u00b7" + D.unid[1] : D.unid[0];       // recuadro al pasar el mouse: valor del esfuerzo en ese punto
          sr.x.forEach(function (x, i) { var h = "<b>Barra " + D.bid[k] + "</b><br>x = " + fm(x) + " " + D.unid[1] + "<br>" + st.dia + " = <b>" + fm(sr.v[i]) + "</b> " + un;
            [0, sr.v[i]].forEach(function (vv) { var q = P(x, vv); hitsU.push({x: q[0], y: q[1], html: h}); }); }); }
        partes(sr.x, sr.v).forEach(function (pt) { var sm = 0; pt[1].forEach(function (v) { sm += v; }); var pos_ = sm >= 0;
          var pts = [P(pt[0][0], 0)].concat(pt[0].map(function (x, i) { return P(x, pt[1][i]); })).concat([P(pt[0][pt[0].length - 1], 0)]);
          el("polygon", {points: pts.map(function (p) { return p.join(","); }).join(" "), fill: pos_ ? "#a9c8e8" : "#f0b8ac", "fill-opacity": 0.85, stroke: pos_ ? "#1f4e79" : "#8a2c1a", "stroke-width": 1}); });
        if (st.sw.val) { var n = sr.x.length, idx = {}; idx[0] = 1; idx[n - 1] = 1;
          for (var i = 1; i < n - 1; i++) { if (sr.x[i] === sr.x[i + 1] || sr.x[i] === sr.x[i - 1] || (sr.v[i] - sr.v[i - 1]) * (sr.v[i + 1] - sr.v[i]) < 0) idx[i] = 1; }
          var lst = Object.keys(idx).map(Number).sort(function (a, b) { return Math.abs(sr.v[b]) - Math.abs(sr.v[a]); }).slice(0, 6);
          lst.forEach(function (i) { if (Math.abs(sr.v[i]) > 1e-9 * vmax) { var p = P(sr.x[i], sr.v[i]), sg = sr.v[i] > 0 ? 1 : -1;
            txt(p[0] + sg * nx * 12, p[1] - sg * ny * 12 + 3, fm(sr.v[i]), "#000", 10.5); } }); }
      }); }
    // deformada
    if (verDef && st.sw.hov) es.def.curvas.forEach(function (c, k) {   // recuadro al pasar el mouse: desplazamiento en ese punto
      c.forEach(function (p, i) { var q = T(p[0] + es.def.esc * p[2], p[1] + es.def.esc * p[3]);
        hitsU.push({x: q[0], y: q[1], html: "<b>Barra " + D.bid[k] + "</b><br>x = " + fm(D.L[k] * i / (c.length - 1)) + " " + D.unid[1] + "<br>|u| = <b>" + fm(Math.hypot(p[2], p[3])) + "</b> " + D.unid[1] +
          "<br>ux = " + fm(p[2]) + ", uy = " + fm(p[3]) }); }); });
    if (verDef) es.def.curvas.forEach(function (c) { var pts = c.map(function (p) { var q = T(p[0] + es.def.esc * p[2], p[1] + es.def.esc * p[3]); return q.join(","); });
      el("polyline", {points: pts.join(" "), fill: "none", stroke: "#000", "stroke-width": 2.6, "stroke-linejoin": "round"}); });
    // nodos
    hits = hitsU;
    D.nodos.forEach(function (n, k) { var p = T(n[0], n[1]), r = D.restr[k], sp = D.resortes[k], rig = r[0] || r[1] || r[2];
      var inc = D.incl.filter(function (ic) { return ic[0] === k; });
      if (!st.sw.apo || (!rig && !(sp[0] || sp[1] || sp[2]) && !inc.length)) { el("circle", {cx: p[0], cy: p[1], r: 3, fill: "#000"}); return; }
      el("circle", {cx: p[0], cy: p[1], r: 6.5, fill: rig ? "#0b7a6b" : "#d98a00", stroke: "#fff", "stroke-width": 1.5});
      var ub = es.ub ? es.ub[k] : [0, 0, 0];
      var h = stTexto("Nudo " + D.nid[k] + (rig ? " · apoyo" : " · resorte"), D.ret ? ["ux", "uy"] : ["ux", "uy", "φz"], r, ub, sp, fm, D.unid[0], D.unid[1]);
      inc.forEach(function (ic) { h += "<br>k inclinado = " + fm(ic[2]) + " " + D.unid[0] + "/" + D.unid[1] + ", β = " + fm(ic[1]) + "° <i>(resorte)</i>"; });
      hits.push({x: p[0], y: p[1], html: h}); });
    // cargas
    if (verC) {
      es.q.forEach(function (q) { var k = q[0], g = D.g[k], a = q[5], b = q[6], n = Math.max(3, Math.min(14, Math.round((b - a) * s / 28) + 1)), colas = [];
        for (var i = 0; i < n; i++) { var x = a + (b - a) * i / (n - 1), t = (x - a) / (b - a), v = vg(g, q[1] + (q[2] - q[1]) * t, q[3] + (q[4] - q[3]) * t), m = Math.hypot(v[0], v[1]);
          if (m < 1e-9 * maxQ) continue; var w = pos(k, x), tip = T(w[0], w[1]), L = 46 * m / maxQ, tail = [tip[0] - L * v[0] / m, tip[1] + L * v[1] / m];
          flecha(tail, tip, C.py, 1.6); colas.push(tail); }
        for (var j = 0; j + 1 < colas.length; j++) lin(colas[j], colas[j + 1], C.py, 1.4);
        if (st.sw.val && colas.length) { var mm = colas[Math.floor(colas.length / 2)]; txt(mm[0], mm[1] - 6, q[7] + " = " + (q[8] === q[9] ? fm(q[8]) : fm(q[8]) + " → " + fm(q[9])), C.py, 11); } });
      es.P.forEach(function (p) { var k = p[0], v = vg(D.g[k], p[1], p[2]), m = Math.hypot(v[0], v[1]); if (m === 0) return; var w = pos(k, p[3]), tip = T(w[0], w[1]), L = 20 + 50 * m / maxF, tail = [tip[0] - L * v[0] / m, tip[1] + L * v[1] / m];
        flecha(tail, tip, C.py, 2.6); if (st.sw.val) txt(tail[0], tail[1] - 6, p[4] + " = " + fm(p[5]), C.py, 11); });
      es.M.forEach(function (mm) { var w = pos(mm[0], mm[2]), P = T(w[0], w[1]); arco(P, mm[1] > 0, C.m); if (st.sw.val) txt(P[0] + 20, P[1] - 14, "Mp = " + fm(mm[1]), C.m, 11, "start"); });
      es.T.forEach(function (t) { var w = pos(t[0], D.L[t[0]] / 2), p = T(w[0], w[1]); txt(p[0], p[1] + 22, "ΔT(+yl) " + fm(t[1]) + " / ΔT(−yl) " + fm(t[2]) + " °", C.t, 10.5); });
      es.F.forEach(function (f, k) { var n = D.nodos[k], p = T(n[0], n[1]);
        if (f[0]) { var L = 20 + 55 * Math.abs(f[0]) / maxF, sg = f[0] > 0 ? 1 : -1; flecha([p[0] - sg * L, p[1]], p, C.px, 2.8); if (st.sw.val) txt(p[0] - sg * L, p[1] - 8, "Px = " + fm(f[0]), C.px, 11, sg > 0 ? "end" : "start"); }
        if (f[1]) { var L2 = 20 + 55 * Math.abs(f[1]) / maxF, sg2 = f[1] > 0 ? 1 : -1; flecha([p[0], p[1] + sg2 * L2], p, C.py, 2.8); if (st.sw.val) txt(p[0] + 6, p[1] + sg2 * L2 + (sg2 > 0 ? 12 : -5), "Py = " + fm(f[1]), C.py, 11, "start"); }
        if (f[2]) { arco(p, f[2] > 0, C.m); if (st.sw.val) txt(p[0] + 20, p[1] + 26, "M = " + fm(f[2]), C.m, 11, "start"); } }); }
    // rótulos
    if (st.sw.ids) {
      D.nodos.forEach(function (n, k) { var p = T(n[0], n[1]); txt(p[0] + 8, p[1] - 8, D.nid[k], "#000", 12.5, "start", false, true); });
      D.barras.forEach(function (b, k) { var w = pos(k, D.L[k] / 2), p = T(w[0], w[1]); txt(p[0] + 8, p[1] + 14, D.bid[k], "#555", 10.5, "middle", true); }); }
    if (verDef && st.sw.val) D.nodos.forEach(function (n, k) { var u = es.def.u[k]; if (Math.hypot(u[0], u[1]) > 1e-9 * es.def.umax) { var p = T(n[0] + es.def.esc * u[0], n[1] + es.def.esc * u[1]);
      txt(p[0], p[1] - 8, "(" + fm(u[0]) + "; " + fm(u[1]) + ")", "#000", 10); } });
    if (verU) { var gx = W - 190, gy = H - 32, bs = st.base === "sadm" ? "σeq/σadm" : "σeq/" + (D.refn[0] || "fy");
      for (var q3 = 0; q3 < 100; q3++) el("rect", {x: gx + q3 * 1.5, y: gy, width: 2, height: 10, fill: stColU(q3 / 100 * 1.3)});
      txt(gx, gy - 4, "utilizaci\u00f3n = " + bs, "#000", 10, "start");
      [[0, "0"], [0.5, "0,5"], [1, "1"]].forEach(function (t) { txt(gx + t[0] / 1.3 * 150, gy + 22, t[1], "#000", 10, "middle"); }); }
    // referencias
    var ly = 18; txt(12, ly, (D.escenas.length > 1 ? "Caso " + es.nombre + " · " : "") + ({est: "Estructura", carg: "Cargas", def: "Deformada", util: "Utilizaci\u00f3n"}[st.modo] || "Diagrama " + st.dia) + (una || unaU ? " · barra " + D.bid[st.barra] : ""), "#000", 12, "start", false, true);
    if (verC) { ly += 16; txt(12, ly, "Referencias", "#000", 11, "start", false, true); }
    (verC ? [["Px", C.px], ["Py, P, q", C.py], ["M (arco: antihorario +)", C.m]] : []).forEach(function (it) { ly += 16; lin([12, ly - 4], [40, ly - 4], it[1], 2.4); txt(48, ly, it[0], "#000", 10.5, "start"); });
    if (st.dia) { ly += 16; txt(12, ly, "ordenada " + (st.dia === "M" ? "hacia la fibra traccionada" : "hacia +yl (izquierda de i→j)") + "; escala " + (una ? "propia de la barra" : st.unica ? "única" : "propia de cada barra"), "#555", 10.5, "start"); }
  }

  function ui() {
    var ctrl = document.createElement("div"); ctrl.className = "ctrl no-print"; var h = "";
    if (D.escenas.length > 1) h += "<label>Caso: <select data-r='caso'>" + D.escenas.map(function (e, i) { return "<option value='" + i + "'>" + e.nombre + "</option>"; }).join("") + "</select></label>";
    var hayDia = D.escenas.some(function (e) { return e.dia; }), hayDef = D.escenas.some(function (e) { return e.def; }), hayUtil = D.escenas.some(function (e) { return e.vm; });
    h += "<button data-v='ini'>Ajustar</button><br>";
    h += "<label>Modo: <select data-r='modo'><option value='est'>Estructura</option><option value='carg' selected>Cargas</option>" + (hayDef ? "<option value='def'>Deformada</option>" : "") + (hayUtil ? "<option value='util'>Utilizaci\u00f3n</option>" : "") +
         (hayDia ? "<option value='N'>N (axil)</option>" + (D.ret ? "" : "<option value='V'>V (corte)</option><option value='M'>M (flector)</option>") : "") + "</select></label> ";
    h += "<label>Barra: <select data-r='barra' disabled><option value='-1'>todas</option>" + D.bid.map(function (b, i) { return "<option value='" + i + "'>" + b + "</option>"; }).join("") + "</select></label> ";
    if (hayDia) h += "<label><input type='checkbox' data-s='unica'> escala única</label>";
    if (hayUtil) h += "<label>Color seg\u00fan: <select data-r='base'><option value='fy'>" + (D.refn[0] || "fy") + "</option><option value='sadm'>\u03c3adm</option></select></label> ";
    [["val", "valores"], ["hov", "valor al pasar el mouse"], ["ids", "nodos y barras"], ["apo", "apoyos"], ["carg", "superponer cargas"]].forEach(function (s) {
      h += "<label><input type='checkbox' data-s='" + s[0] + "'" + (st.sw[s[0]] ? " checked" : "") + "> " + s[1] + "</label>"; });
    ctrl.innerHTML = h; root.appendChild(ctrl);
    svg = document.createElementNS(NS, "svg"); svg.setAttribute("class", "lienzo"); svg.setAttribute("viewBox", "0 0 " + W + " " + H); root.appendChild(svg);
    gr = document.createElementNS(NS, "g"); svg.appendChild(gr);
    var pie = document.createElement("div"); pie.className = "pie"; pie.textContent = D.pie; root.appendChild(pie);
    var ay = document.createElement("div"); ay.className = "ayuda"; ay.textContent = D.ayuda; root.appendChild(ay);
    var un = ctrl.querySelector("[data-s='unica']"); if (un) un.checked = st.unica;
    function ajustar() { st.zoom = 1; st.ox = 0; st.oy = 0; }
    ctrl.addEventListener("click", function (e) { if (e.target.getAttribute("data-v")) { ajustar(); dibujar(); } });
    ctrl.addEventListener("change", function (e) { var t = e.target, r = t.getAttribute("data-r");
      if (r === "caso") st.esc = +t.value;
      else if (r === "modo") { st.modo = t.value; st.dia = "NVM".indexOf(t.value) >= 0 && t.value.length === 1 ? t.value : ""; ctrl.querySelector("[data-r='barra']").disabled = !st.dia && st.modo !== "util"; }
      else if (r === "base") st.base = t.value;
      else if (r === "barra") st.barra = +t.value;
      else if (t.getAttribute("data-s") === "unica") st.unica = t.checked; else if (t.getAttribute("data-s")) st.sw[t.getAttribute("data-s")] = t.checked; dibujar(); });
    stNav(svg, {W: W, rotar: null, pan: function (dx, dy) { st.ox += dx; st.oy += dy; },
      zoomFactor: function (f, mx, my) { stZoomEn(st, f, mx, my, W / 2 + 50, H / 2 + 10, 0.3, 30); },
      reset: ajustar, dib: dibujar});
    stTip(root, svg, W, function () { return hits; });
  }
  ui(); dibujar();
}
""" % {"PX": COL_PX, "PY": COL_PY, "M": COL_M, "T": COL_TEMP}
LIB_JS = NAV_JS + LIB_JS


def _escena(modelo, e: dict) -> dict:
    """e: {nombre, F (n,3), cb [(CargaBarra, factor)], res (opcional), escala (opcional)}"""
    q, P, M, T = [], [], [], []
    for c, fac in e.get("cb", []):
        if c.tipo == "q":
            q.append([c.barra, c.qx[0] * fac, c.qx[1] * fac, c.qy[0] * fac, c.qy[1] * fac, c.a, c.b, c.orig,
                      c.v1 * fac, c.v2 * fac])
        elif c.tipo == "P":
            P.append([c.barra, c.Px * fac, c.Py * fac, c.a, c.orig, c.v1 * fac])
        elif c.tipo == "M":
            M.append([c.barra, c.M0 * fac, c.a])
        elif c.tipo == "temp" and c.orig != "dl":
            T.append([c.barra, c.Ts * fac, c.Ti * fac])
    d = dia = None
    vm = []
    res = e.get("res")
    ub = np.asarray(res.u, dtype=float).tolist() if res is not None else None
    if res is not None:
        esc = e.get("escala") or escala_auto(modelo, res)
        d = {"esc": esc, "umax": float(np.hypot(res.u[:, 0], res.u[:, 1]).max()),
             "u": [[float(a), float(b)] for a, b, _ in res.u],
             "curvas": [[[float(a), float(b), float(c), float(dd)] for a, b, c, dd in zip(*cur)]
                        for cur in elastica(modelo, res, n=25)]}
        esf = esfuerzos(modelo, res, n=41)
        dia = {k: [{"x": [float(v) for v in cv["x"]], "v": [float(v) for v in cv[k]]} for cv in esf["curvas"]]
               for k in (("N",) if hasattr(modelo, "ret_pandeo") else ("N", "V", "M"))}      # reticulado: solo axil
        vm = []                                          # σeq a lo largo de cada barra (21 puntos) para el modo Utilización
        for k, tk in enumerate(tensiones(modelo, esf)):
            vm.append(None if tk.get("curva_vm") is None else
                      np.interp(np.linspace(0, modelo.barras[k].L, 21), tk["x_curva"], tk["curva_vm"]).tolist())
    return {"nombre": str(e["nombre"]), "F": np.asarray(e["F"], dtype=float).tolist(), "q": q, "P": P, "M": M,
            "T": T, "def": d, "dia": dia, "ub": ub, "vm": vm if res is not None and any(v is not None for v in vm) else None}


def visor_html(modelo, escenas: list, id_: str, pie: str = "") -> str:
    """Fragmento HTML del visor (necesita LIB_JS y CSS una vez en el documento)."""
    D = {
        "nodos": [[n.x, n.y] for n in modelo.nodos], "nid": [n.id for n in modelo.nodos],
        "barras": [[b.i, b.j] for b in modelo.barras], "bid": [b.id for b in modelo.barras],
        "g": [[b.g1, b.g2] for b in modelo.barras], "L": [b.L for b in modelo.barras],
        "art": [[0, 0] if hasattr(modelo, "ret_pandeo") else [int(b.art_i), int(b.art_j)] for b in modelo.barras],
        "restr": modelo.restr.astype(int).tolist(), "resortes": modelo.resortes.tolist(), "ret": hasattr(modelo, "ret_pandeo"), "unid": [modelo.config["unidad_fuerza"], modelo.config["unidad_longitud"]],
        "incl": [[sp["nodo"], sp["beta"], sp["k"]] for sp in modelo.resortes_incl],
        "escala": modelo.config["escala_diagramas"], "pie": pie, "ayuda": AYUDA_2D,
        "fy": [referencia(b.mat) for b in modelo.barras], "refn": ["fy" if b.mat.teoria in ("vm", "tresca") else "sut" for b in modelo.barras], "sadm": [b.mat.sadm for b in modelo.barras],
        "escenas": [_escena(modelo, e) for e in escenas],
    }
    datos = json.dumps(D, ensure_ascii=False).replace("</", "<\\/")
    return f'<div class="visor" id="{id_}"></div><script>emp2d("{id_}", {datos});</script>'
