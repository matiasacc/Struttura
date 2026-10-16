"""Visor 3D interactivo (HTML + JavaScript incluidos en el propio informe; no usa internet).

Muestra la estructura en el espacio: barras, apoyos, resortes, cargas y (opcional) la deformada.
Navegación estándar de Struttura (ver visor_comun.py): girar, Ctrl+arrastrar = desplazar, rueda/Shift = zoom.
Botones de vistas predefinidas: isométrica, planta, frente y lateral.

Convenciones del dibujo (iguales a las de la planta):
    * Terna derecha global:  X, Y en el plano de la estructura y Z hacia arriba (hacia el lector en planta).
    * Colores por componente:   Pz (fuerzas en z) rojo · Mx azul · My ámbar.
    * Fuerza: flecha simple, con la PUNTA en el punto de aplicación y apuntando en el sentido de la carga
      (una carga gravitatoria llega desde arriba).
    * Momento: vector con DOS puntas (regla de la mano derecha): Mx a lo largo de X, My a lo largo de Y;
      si el valor es positivo apunta hacia +X / +Y, si es negativo hacia −X / −Y.
    * Una sola flecha por componente y por nodo (la resultante de lo cargado en ese nodo).
    * Cargas en el tramo: q = fila de flechas con altura proporcional a q; P = flecha; ΔT = rótulo.
    * Longitudes proporcionales: todas las fuerzas con la misma escala, todos los momentos con la suya,
      q con la propia (las unidades son distintas).  Escalas idénticas para todos los casos del visor.
"""
from __future__ import annotations

import json

import numpy as np

from ..falla_plana import referencia
from ..visor_comun import AYUDA_3D, CSS_COMUN, NAV_JS
from .esfuerzos import elastica, esfuerzos, tensiones
from .graficos import COL_MX, COL_MY, COL_PZ

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
function emp3d(id, D) {
  var root = document.getElementById(id);
  var W = 760, H = 540, NS = "http://www.w3.org/2000/svg";
  var C = {pz: "%(PZ)s", mx: "%(MX)s", my: "%(MY)s"};
  var st = {az: -32, el: 28, zoom: 1, ox: 0, oy: 0, esc: 0, modo: "carg", base: "fy", dia: "", barra: -1, unica: D.escala === "global", sw: {pz: true, mx: true, my: true, val: true, ids: true, carg: false, apo: true}};
  var VISTAS = {iso: [-32, 28], planta: [0, 90], frente: [0, 0], lateral: [90, 0]};
  var nn = D.nodos.length;

  function fm(v) { if (v === 0) return "0"; var a = Math.abs(v);
    return (a >= 1e-3 && a < 1e7) ? String(+v.toPrecision(4)) : v.toExponential(3); }

  // ---- escalas (proporcionales y comunes a todos los casos) ----
  var maxF = 0, maxM = 0, maxQ = 0, maxW = 0;
  D.escenas.forEach(function (e) {
    e.F.forEach(function (f) { maxF = Math.max(maxF, Math.abs(f[0])); maxM = Math.max(maxM, Math.abs(f[1]), Math.abs(f[2])); });
    e.P.forEach(function (p) { maxF = Math.max(maxF, Math.abs(p[1])); });
    e.q.forEach(function (q) { maxQ = Math.max(maxQ, Math.abs(q[1]), Math.abs(q[2])); });
  });
  var LF = 0.24 * D.dim, LM = 0.24 * D.dim, LQ = 0.16 * D.dim;
  var kF = maxF > 0 ? LF / maxF : 0, kM = maxM > 0 ? LM / maxM : 0, kQ = maxQ > 0 ? LQ / maxQ : 0;

  // ---- radio de la escena (esfera envolvente, fija: no salta al girar) ----
  var pts = [];
  D.nodos.forEach(function (n) { pts.push([n[0], n[1], 0]); });
  D.escenas.forEach(function (e) {
    e.F.forEach(function (f, k) { var n = D.nodos[k];
      if (f[0]) pts.push([n[0], n[1], -Math.sign(f[0]) * Math.abs(f[0]) * kF]);
      if (f[1]) pts.push([n[0] - Math.sign(f[1]) * Math.abs(f[1]) * kM, n[1], 0]);
      if (f[2]) pts.push([n[0], n[1] - Math.sign(f[2]) * Math.abs(f[2]) * kM, 0]); });
    e.q.forEach(function (q) { var b = D.barras[q[0]], A = D.nodos[b[0]];
      var m = Math.max(Math.abs(q[1]), Math.abs(q[2])) * kQ;
      pts.push([A[0] + D.g[q[0]][0] * q[3], A[1] + D.g[q[0]][1] * q[3], m]);
      pts.push([A[0] + D.g[q[0]][0] * q[4], A[1] + D.g[q[0]][1] * q[4], -m]); });
    if (e.def) e.def.curvas.forEach(function (c) { c.forEach(function (p) { pts.push([p[0], p[1], p[2] * e.def.esc]); }); });
  });
  var lo = [1e300, 1e300, 1e300], hi = [-1e300, -1e300, -1e300];
  pts.forEach(function (p) { for (var i = 0; i < 3; i++) { lo[i] = Math.min(lo[i], p[i]); hi[i] = Math.max(hi[i], p[i]); } });
  var ctr = [(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, (lo[2] + hi[2]) / 2];
  var R = 1e-9; pts.forEach(function (p) { R = Math.max(R, Math.hypot(p[0] - ctr[0], p[1] - ctr[1], p[2] - ctr[2])); });

  // ---- cámara ----
  function cam() {
    var a = st.az * Math.PI / 180, e = st.el * Math.PI / 180;
    return {r: [Math.cos(a), Math.sin(a), 0],
            u: [-Math.sin(e) * Math.sin(a), Math.sin(e) * Math.cos(a), Math.cos(e)],
            b: [Math.sin(a) * Math.cos(e), -Math.cos(a) * Math.cos(e), Math.sin(e)]};   // hacia el lector
  }
  var K;
  function P(p) {                                   // 3D -> pantalla
    var q = [p[0] - ctr[0], p[1] - ctr[1], p[2] - ctr[2]], s = Math.min(W, H) * 0.44 / R * st.zoom;
    return [W / 2 + st.ox + s * (q[0] * K.r[0] + q[1] * K.r[1] + q[2] * K.r[2]),
            H / 2 + st.oy - s * (q[0] * K.u[0] + q[1] * K.u[1] + q[2] * K.u[2])];
  }
  function dot(a, b) { return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]; }

  // ---- primitivas SVG ----
  var svg, gr, hits = [];
  function el(tag, at, padre) { var e = document.createElementNS(NS, tag);
    for (var k in at) e.setAttribute(k, at[k]); (padre || gr).appendChild(e); return e; }
  function linea(a, b, col, w, dash, op) { var A = P(a), B = P(b);
    el("line", {x1: A[0], y1: A[1], x2: B[0], y2: B[1], stroke: col, "stroke-width": w, "stroke-linecap": "round",
                "stroke-dasharray": dash || "", opacity: op || 1}); }
  function texto(x, y, t, col, sz, anc, neg) { var e = el("text", {x: x, y: y, fill: col, "font-size": sz || 11,
      "text-anchor": anc || "middle", "font-family": "'Times New Roman',serif", "font-style": neg ? "italic" : "normal",
      stroke: "#fff", "stroke-width": 3, "paint-order": "stroke"}); e.textContent = t; }
  function punta(T, dir, col, atras) {            // triángulo en T (pantalla) apuntando a dir (unitario)
    var L = 10, w = 3.6, bx = T[0] - dir[0] * (L + atras), by = T[1] - dir[1] * (L + atras);
    var tx = T[0] - dir[0] * atras, ty = T[1] - dir[1] * atras;
    el("polygon", {points: tx + "," + ty + " " + (bx - dir[1] * w) + "," + (by + dir[0] * w) + " " +
                           (bx + dir[1] * w) + "," + (by - dir[0] * w), fill: col}); }
  function flecha(tail, tip, col, dobles, w) {   // flecha 3D con punta en 'tip'; dobles = momento
    var A = P(tail), B = P(tip), dx = B[0] - A[0], dy = B[1] - A[1], L = Math.hypot(dx, dy);
    var d3 = [tip[0] - tail[0], tip[1] - tail[1], tip[2] - tail[2]];
    if (L < 9) {                                  // casi a lo largo de la visual: símbolo círculo con punto / cruz
      var haciaLector = dot(d3, K.b) > 0, r = 7;
      el("circle", {cx: B[0], cy: B[1], r: r, fill: "#fff", stroke: col, "stroke-width": 1.6});
      if (dobles) el("circle", {cx: B[0], cy: B[1], r: r + 3, fill: "none", stroke: col, "stroke-width": 1.2});
      if (haciaLector) el("circle", {cx: B[0], cy: B[1], r: 2.4, fill: col});
      else { el("line", {x1: B[0] - 4, y1: B[1] - 4, x2: B[0] + 4, y2: B[1] + 4, stroke: col, "stroke-width": 1.6});
             el("line", {x1: B[0] - 4, y1: B[1] + 4, x2: B[0] + 4, y2: B[1] - 4, stroke: col, "stroke-width": 1.6}); }
      return A; }
    var u = [dx / L, dy / L];
    el("line", {x1: A[0], y1: A[1], x2: B[0] - u[0] * 6, y2: B[1] - u[1] * 6, stroke: col, "stroke-width": w || 2.2,
                "stroke-linecap": "round"});
    punta(B, u, col, 0);
    if (dobles) punta(B, u, col, Math.min(9, L * 0.4));
    return A; }

  // ---- escena ----
  function dibujar() {
    K = cam();
    while (gr.firstChild) gr.removeChild(gr.firstChild);
    var es = D.escenas[st.esc], verDef = st.modo === "def" && es.def, verC = st.modo === "carg" || (st.modo !== "est" && st.sw.carg);
    // barras
    var verU = st.modo === "util" && es.vm, hitsU = [];
    D.barras.forEach(function (b, k) { var A = D.nodos[b[0]], B = D.nodos[b[1]];
      if (verU) { var v = es.vm[k], fy = D.fy[k], sa = D.sadm[k], base = st.base === "sadm" ? sa : fy;
        if (!v || !base) { linea([A[0], A[1], 0], [B[0], B[1], 0], "#999", 2.4, "4,3"); return; }
        var m = v.length - 1, pt = function (q) { return [A[0] + (B[0] - A[0]) * q / m, A[1] + (B[1] - A[1]) * q / m, 0]; };
        for (var q = 0; q < m; q++) linea(pt(q), pt(q + 1), stColU(Math.max(v[q], v[q + 1]) / base), 5);
        for (var q2 = 0; q2 <= m; q2++) { var pp = P(pt(q2)); hitsU.push({x: pp[0], y: pp[1], html: stTextoU(D.bid[k], D.L[k] * q2 / m, v[q2], fy, sa, fm, D.unid[0] + "/" + D.unid[1] + "\u00b2", D.unid[1], D.refn[k])}); }
        return; }
      linea([A[0], A[1], 0], [B[0], B[1], 0], verDef ? "#8a8a8a" : st.dia ? (st.barra === k ? "#555" : "#b5b5b5") : "#000", verDef ? 1.2 : st.dia ? 2.2 : 2.6,
            verDef ? "5,4" : ""); });
    // articulaciones: circulo = flexion (m), cuadrado = solo torsion (t); circulo con punto = flexion y torsion
    if (!verU) D.barras.forEach(function (b, k) { var A = D.nodos[b[0]], B = D.nodos[b[1]];
      [[D.art[k][0], 0.06], [D.art[k][1], 0.94]].forEach(function (a) { if (!a[0]) return;
        var p = P([A[0] + (B[0] - A[0]) * a[1], A[1] + (B[1] - A[1]) * a[1], 0]);
        if (a[0] === "t") el("rect", {x: p[0] - 4, y: p[1] - 4, width: 8, height: 8, fill: "#fff", stroke: "#000", "stroke-width": 1.4});
        else { el("circle", {cx: p[0], cy: p[1], r: 4.5, fill: "#fff", stroke: "#000", "stroke-width": 1.4});
          if (a[0] === "mt") el("circle", {cx: p[0], cy: p[1], r: 1.6, fill: "#000"}); } }); });
    // diagramas V, T, M: ordenadas en el plano, hacia la izquierda de i→j para valores positivos (igual que las figuras del informe)
    if (st.dia && es.dia) {
      var series = es.dia[st.dia], vmax = 1e-300, una = st.barra >= 0;
      series.forEach(function (sr) { sr.v.forEach(function (v) { vmax = Math.max(vmax, Math.abs(v)); }); });
      series.forEach(function (sr, k) { var vk = 1e-300; sr.v.forEach(function (v) { vk = Math.max(vk, Math.abs(v)); });
        if (vk <= 1e-6 * vmax || (una && k !== st.barra)) return;
        var g = D.g[k], A0 = D.nodos[D.barras[k][0]], nx = -g[1], ny = g[0], esc = (una ? 0.3 * D.L[k] : 0.13 * D.dim) / (st.unica && !una ? vmax : vk);
        function Q(x, v) { return P([A0[0] + g[0] * x + nx * v * esc, A0[1] + g[1] * x + ny * v * esc, 0]); }
        var cortes = [[sr.x[0]], [sr.v[0]]], partes = [];
        for (var i = 1; i < sr.x.length; i++) {
          var u = cortes[1][cortes[1].length - 1];
          if (u * sr.v[i] < 0) { var t = u / (u - sr.v[i]), xc = cortes[0][cortes[0].length - 1] + t * (sr.x[i] - cortes[0][cortes[0].length - 1]);
            cortes[0].push(xc); cortes[1].push(0); partes.push(cortes); cortes = [[xc], [0]]; }
          cortes[0].push(sr.x[i]); cortes[1].push(sr.v[i]); }
        partes.push(cortes);
        partes.forEach(function (pt) { var sm = 0; pt[1].forEach(function (v) { sm += v; }); var pos_ = sm >= 0;
          var pts = [Q(pt[0][0], 0)].concat(pt[0].map(function (x, i) { return Q(x, pt[1][i]); })).concat([Q(pt[0][pt[0].length - 1], 0)]);
          el("polygon", {points: pts.map(function (q) { return q.join(","); }).join(" "), fill: pos_ ? "#a9c8e8" : "#f0b8ac", "fill-opacity": 0.85, stroke: pos_ ? "#1f4e79" : "#8a2c1a", "stroke-width": 1}); });
        if (st.sw.val) { var n = sr.x.length, idx = {}; idx[0] = 1; idx[n - 1] = 1;
          for (var i2 = 1; i2 < n - 1; i2++) { if (sr.x[i2] === sr.x[i2 + 1] || sr.x[i2] === sr.x[i2 - 1] || (sr.v[i2] - sr.v[i2 - 1]) * (sr.v[i2 + 1] - sr.v[i2]) < 0) idx[i2] = 1; }
          Object.keys(idx).map(Number).sort(function (a, b) { return Math.abs(sr.v[b]) - Math.abs(sr.v[a]); }).slice(0, 6).forEach(function (i3) {
            if (Math.abs(sr.v[i3]) > 1e-9 * vmax) { var q = Q(sr.x[i3], sr.v[i3]); texto(q[0], q[1] - 4, fm(sr.v[i3]), "#000", 10.5); } }); }
      }); }
    // deformada
    if (verDef) es.def.curvas.forEach(function (c) {
      for (var i = 0; i + 1 < c.length; i++) linea([c[i][0], c[i][1], c[i][2] * es.def.esc], [c[i + 1][0], c[i + 1][1], c[i + 1][2] * es.def.esc], "#000", 2.6); });
    // nodos y apoyos (verde = apoyo, naranja = solo resorte); el recuadro muestra las condiciones de borde
    D.nodos.forEach(function (n) { var p = P([n[0], n[1], 0]); el("circle", {cx: p[0], cy: p[1], r: 2.8, fill: "#000"}); });
    hits = hitsU;
    if (st.sw.apo) D.nodos.forEach(function (n, k) { var r = D.restr[k], sp = D.resortes[k], rig = r[0] || r[1] || r[2];
      if (!rig && !(sp[0] || sp[1] || sp[2])) return;
      var p = P([n[0], n[1], 0]), ub = es.ub ? es.ub[k] : [0, 0, 0];
      el("circle", {cx: p[0], cy: p[1], r: 6.5, fill: rig ? "#0b7a6b" : "#d98a00", stroke: "#fff", "stroke-width": 1.5});
      var h = stTexto("Nudo " + D.nid[k] + (rig ? " · apoyo" : " · resorte"), ["uz", "φx", "φy"], r, ub, D.ks[k], fm, D.unid[0], D.unid[1]);
      D.kg.forEach(function (g) { if (g[0] === k) h += "<br>k giro inclinado = " + fm(g[1]) + " " + D.unid[0] + "·" + D.unid[1] + "/rad, β = " + fm(g[2]) + "° <i>(resorte)</i>"; });
      hits.push({x: p[0], y: p[1], html: h}); });
    // cargas en el tramo
    if (verC && st.sw.pz) {
      es.q.forEach(function (q) { var k = q[0], A = D.nodos[D.barras[k][0]], g = D.g[k], n = Math.max(2, Math.min(12, Math.round((q[4] - q[3]) / (0.05 * D.dim)) + 1)), cima = [];
        for (var i = 0; i < n; i++) { var x = q[3] + (q[4] - q[3]) * (n === 1 ? 0 : i / (n - 1)), v = q[1] + (q[2] - q[1]) * (x - q[3]) / (q[4] - q[3]);
          var tip = [A[0] + g[0] * x, A[1] + g[1] * x, 0], h = v * kQ, tail = [tip[0], tip[1], -h];
          if (Math.abs(v) > 1e-12 * maxQ) { flecha(tail, tip, C.pz, false, 1.5); cima.push(tail); } }
        for (var j = 0; j + 1 < cima.length; j++) linea(cima[j], cima[j + 1], C.pz, 1.2);
        if (st.sw.val && cima.length) { var m = cima[Math.floor(cima.length / 2)], p = P(m);
          texto(p[0], p[1] - 6, (q[1] === q[2]) ? "q = " + fm(q[1]) : "q = " + fm(q[1]) + " → " + fm(q[2]), C.pz, 11); } });
      es.P.forEach(function (p) { var k = p[0], A = D.nodos[D.barras[k][0]], g = D.g[k], tip = [A[0] + g[0] * p[2], A[1] + g[1] * p[2], 0],
          tail = [tip[0], tip[1], -p[1] * kF];
        flecha(tail, tip, C.pz, false, 2.4);
        if (st.sw.val) { var T = P(tail); texto(T[0] + 8, T[1] + (p[1] < 0 ? -4 : 12), "P = " + fm(p[1]), C.pz, 11, "start"); } });
    }
    // temperatura
    if (verC) es.T.forEach(function (t) { var k = t[0], A = D.nodos[D.barras[k][0]], g = D.g[k], m = P([A[0] + g[0] * D.L[k] / 2, A[1] + g[1] * D.L[k] / 2, 0]);
      texto(m[0], m[1] + 22, "ΔT sup " + fm(t[1]) + " / inf " + fm(t[2]) + " °", "#7d3c98", 10.5); });
    // cargas nodales: una resultante por componente y por nodo
    if (verC) es.F.forEach(function (f, k) { var n = D.nodos[k];
      if (verC && st.sw.pz && f[0]) { var tail = [n[0], n[1], -f[0] * kF]; flecha(tail, [n[0], n[1], 0], C.pz, false, 2.6);
        if (st.sw.val) { var T = P(tail); texto(T[0] + 8, T[1] + (f[0] < 0 ? -4 : 12), "Pz = " + fm(f[0]), C.pz, 11, "start"); } }
      if (verC && st.sw.mx && f[1]) { var tl = [n[0] - Math.sign(f[1]) * Math.abs(f[1]) * kM, n[1], 0]; flecha(tl, [n[0], n[1], 0], C.mx, true, 2.6);
        if (st.sw.val) { var T2 = P(tl); texto(T2[0] + 6, T2[1] - 9, "Mx = " + fm(f[1]), C.mx, 11, "start"); } }
      if (verC && st.sw.my && f[2]) { var tm = [n[0], n[1] - Math.sign(f[2]) * Math.abs(f[2]) * kM, 0]; flecha(tm, [n[0], n[1], 0], C.my, true, 2.6);
        if (st.sw.val) { var T3 = P(tm); texto(T3[0] + 6, T3[1] - 9, "My = " + fm(f[2]), C.my, 11, "start"); } } });
    // rótulos
    if (st.sw.ids) {
      D.nodos.forEach(function (n, k) { var p = P([n[0], n[1], 0]); texto(p[0] + 9, p[1] + 15, D.nid[k], "#000", 12.5, "start"); gr.lastChild.setAttribute("font-weight", "bold"); });
      D.barras.forEach(function (b, k) { var A = D.nodos[b[0]], B = D.nodos[b[1]], p = P([(A[0] + B[0]) / 2, (A[1] + B[1]) / 2, 0]); texto(p[0], p[1] - 6, D.bid[k], "#555", 10.5, "middle", true); });
    }
    // valores de uz en la deformada
    if (verDef && st.sw.val) es.def.uz.forEach(function (w, k) { if (Math.abs(w) > 1e-9 * es.def.wmax) { var n = D.nodos[k], p = P([n[0], n[1], w * es.def.esc]); texto(p[0], p[1] - 7, "uz=" + fm(w), "#000", 10.5); } });
    // triedro
    var ox = 44, oy = H - 40, ls = 30;
    [[[1, 0, 0], "X"], [[0, 1, 0], "Y"], [[0, 0, 1], "Z"]].forEach(function (ax) { var v = ax[0], sx = ls * dot(v, K.r), sy = -ls * dot(v, K.u), L = Math.hypot(sx, sy);
      if (L > 6) { el("line", {x1: ox, y1: oy, x2: ox + sx, y2: oy + sy, stroke: "#333", "stroke-width": 1.6}); punta([ox + sx, oy + sy], [sx / L, sy / L], "#333", 0); texto(ox + sx * 1.32, oy + sy * 1.32 + 4, ax[1], "#333", 12, "middle", true); }
      else { el("circle", {cx: ox, cy: oy, r: 5, fill: "none", stroke: "#333"}); if (dot(v, K.b) > 0) el("circle", {cx: ox, cy: oy, r: 1.8, fill: "#333"}); texto(ox + 11, oy + 4, ax[1], "#333", 12, "start", true); } });
    if (verU) { var gx = W - 190, gy = H - 32, bs = st.base === "sadm" ? "σeq/σadm" : "σeq/" + (D.refn[0] || "fy");
      for (var q3 = 0; q3 < 100; q3++) el("rect", {x: gx + q3 * 1.5, y: gy, width: 2, height: 10, fill: stColU(q3 / 100 * 1.3)});
      texto(gx, gy - 4, "utilizaci\u00f3n = " + bs, "#000", 10, "start");
      [[0, "0"], [0.5, "0,5"], [1, "1"]].forEach(function (t) { texto(gx + t[0] / 1.3 * 150, gy + 22, t[1], "#000", 10, "middle"); }); }
    // referencias
    var ly = 18;
    texto(12, ly, (D.escenas.length > 1 ? "Caso " + es.nombre + " · " : "") + (({est: "Estructura", carg: "Cargas", def: "Deformada", util: "Utilizaci\u00f3n"})[st.modo] || ("Diagrama " + st.dia)) + (st.dia && st.barra >= 0 ? " \u00b7 barra " + D.bid[st.barra] : ""), "#000", 12, "start");
    if (verC) { ly += 16; texto(12, ly, "Referencias", "#000", 11, "start"); gr.lastChild.setAttribute("font-weight", "bold"); }
    (verC ? [["Pz, P, q (fuerza: 1 punta)", C.pz, false], ["Mx (vector, 2 puntas)", C.mx, true], ["My (vector, 2 puntas)", C.my, true]] : []).forEach(function (it) {
      ly += 16; el("line", {x1: 12, y1: ly - 4, x2: 42, y2: ly - 4, stroke: it[1], "stroke-width": 2.2}); punta([42, ly - 4], [1, 0], it[1], 0); if (it[2]) punta([42, ly - 4], [1, 0], it[1], 8);
      texto(50, ly, it[0], "#000", 10.5, "start"); });
  }

  // ---- interfaz ----
  function ui() {
    var ctrl = document.createElement("div"); ctrl.className = "ctrl no-print";
    var h = "";
    if (D.escenas.length > 1) { h += "<label>Caso: <select data-r='caso'>" + D.escenas.map(function (e, i) { return "<option value='" + i + "'>" + e.nombre + "</option>"; }).join("") + "</select></label>"; }
    h += "<button data-v='iso'>iso</button><button data-v='planta'>planta</button><button data-v='frente'>frente</button><button data-v='lateral'>lateral</button><button data-v='aj'>Ajustar</button><br>";
    var hayDef = D.escenas.some(function (e) { return e.def; }), hayUtil = D.escenas.some(function (e) { return e.vm; }), hayDia = D.escenas.some(function (e) { return e.dia; });
    h += "<label>Modo: <select data-r='modo'><option value='est'>Estructura</option><option value='carg' selected>Cargas</option>" + (hayDef ? "<option value='def'>Deformada</option>" : "") + (hayUtil ? "<option value='util'>Utilizaci\u00f3n</option>" : "") +
         (hayDia ? "<option value='V'>V (corte)</option><option value='T'>T (torsor)</option><option value='M'>M (flector)</option>" : "") + "</select></label> ";
    h += "<label>Barra: <select data-r='barra' disabled><option value='-1'>todas</option>" + D.bid.map(function (b, i) { return "<option value='" + i + "'>" + b + "</option>"; }).join("") + "</select></label> ";
    if (hayDia) h += "<label><input type='checkbox' data-s='unica'" + (st.unica ? " checked" : "") + "> escala \u00fanica</label>";
    if (hayUtil) h += "<label>Color seg\u00fan: <select data-r='base'><option value='fy'>" + (D.refn[0] || "fy") + "</option><option value='sadm'>\u03c3adm</option></select></label> ";
    [["pz", "Pz / P / q"], ["mx", "Mx"], ["my", "My"], ["val", "valores"], ["ids", "nodos y barras"], ["apo", "apoyos"], ["carg", "superponer cargas"]].forEach(function (s) {
      h += "<label><input type='checkbox' data-s='" + s[0] + "'" + (st.sw[s[0]] ? " checked" : "") + "> " + s[1] + "</label>"; });
    ctrl.innerHTML = h; root.appendChild(ctrl);
    svg = document.createElementNS(NS, "svg"); svg.setAttribute("class", "lienzo"); svg.setAttribute("viewBox", "0 0 " + W + " " + H); root.appendChild(svg);
    gr = document.createElementNS(NS, "g"); svg.appendChild(gr);
    var pie = document.createElement("div"); pie.className = "pie";
    pie.textContent = D.pie; root.appendChild(pie);
    var ay = document.createElement("div"); ay.className = "ayuda"; ay.textContent = D.ayuda; root.appendChild(ay);
    function ajustar(v) { if (v) { st.az = v[0]; st.el = v[1]; } st.zoom = 1; st.ox = 0; st.oy = 0; }
    ctrl.addEventListener("click", function (e) { var v = e.target.getAttribute("data-v"); if (v) { ajustar(v === "aj" ? null : VISTAS[v]); dibujar(); } });
    ctrl.addEventListener("change", function (e) { var t = e.target;
      if (t.getAttribute("data-r") === "caso") st.esc = +t.value; else if (t.getAttribute("data-r") === "modo") { st.modo = t.value; st.dia = "VTM".indexOf(t.value) >= 0 && t.value.length === 1 ? t.value : ""; ctrl.querySelector("[data-r='barra']").disabled = !st.dia && st.modo !== "util"; }
      else if (t.getAttribute("data-r") === "base") st.base = t.value; else if (t.getAttribute("data-r") === "barra") st.barra = +t.value;
      else if (t.getAttribute("data-s") === "unica") st.unica = t.checked; else if (t.getAttribute("data-s")) st.sw[t.getAttribute("data-s")] = t.checked; dibujar(); });
    stNav(svg, {W: W, rotar: function (dx, dy) { st.az -= dx * 0.45; st.el = Math.max(-90, Math.min(90, st.el + dy * 0.45)); },
      pan: function (dx, dy) { st.ox += dx; st.oy += dy; },
      zoomFactor: function (f, mx, my) { stZoomEn(st, f, mx, my, W / 2, H / 2, 0.3, 60); },
      reset: function () { ajustar(VISTAS.iso); }, dib: dibujar});
    stTip(root, svg, W, function () { return hits; });
  }
  ui(); dibujar();
}
""" % {"PZ": COL_PZ, "MX": COL_MX, "MY": COL_MY}
LIB_JS = NAV_JS + LIB_JS


def _escena(modelo, e: dict) -> dict:
    """e: {nombre, F (n,3), cb [(CargaBarra, factor)], res (opcional), escala (opcional)}"""
    q, P, T = [], [], []
    for c, fac in e.get("cb", []):
        if c.tipo == "q":
            q.append([c.barra, c.v1 * fac, c.v2 * fac, c.a, c.b])
        elif c.tipo == "P":
            P.append([c.barra, c.v1 * fac, c.a])
        elif c.tipo == "temp":
            T.append([c.barra, c.v1 * fac, c.v2 * fac])
    d = None
    vm = []
    dia = None
    res = e.get("res")
    ub = np.asarray(res.u, dtype=float).tolist() if res is not None else None
    if res is not None:
        from .graficos import escala_auto
        esc = e.get("escala") or escala_auto(modelo, res)
        curvas = elastica(modelo, res, n=25)
        d = {"esc": esc, "wmax": float(np.abs(res.u[:, 0]).max()),
             "curvas": [[[float(x), float(y), float(w)] for x, y, w in zip(X, Y, W)] for X, Y, W in curvas],
             "uz": [float(v) for v in res.u[:, 0]]}
        vm = []                                          # σeq a lo largo de cada barra (21 puntos) para el modo Utilización
        esf = esfuerzos(modelo, res, n=41)
        dia = {"V": [{"x": [float(v) for v in cv["x"]], "v": [float(v) for v in cv["V"]]} for cv in esf["curvas"]],
               "M": [{"x": [float(v) for v in cv["x"]], "v": [float(v) for v in cv["M"]]} for cv in esf["curvas"]],
               "T": [{"x": [0.0, float(b.L)], "v": [float(esf["T"][k])] * 2} for k, b in enumerate(modelo.barras)]}
        for k, tk in enumerate(tensiones(modelo, esf)):
            vm.append(None if tk.get("curva_vm") is None else
                      np.interp(np.linspace(0, modelo.barras[k].L, 21), tk["x_curva"], tk["curva_vm"]).tolist())
    return {"nombre": str(e["nombre"]), "F": np.asarray(e["F"], dtype=float).tolist(), "q": q, "P": P, "T": T, "def": d, "ub": ub, "dia": dia, "vm": vm if d is not None and any(v is not None for v in vm) else None}


def visor_html(modelo, escenas: list, id_: str, pie: str = "") -> str:
    """Fragmento HTML del visor (necesita LIB_JS y CSS una vez en el documento)."""
    xs = [n.x for n in modelo.nodos]
    ys = [n.y for n in modelo.nodos]
    dim = max(np.ptp(xs), np.ptp(ys), max(b.L for b in modelo.barras) * 0.5, 1e-9)
    D = {
        "nodos": [[n.x, n.y] for n in modelo.nodos], "nid": [n.id for n in modelo.nodos],
        "barras": [[b.i, b.j] for b in modelo.barras], "bid": [b.id for b in modelo.barras],
        "g": [[b.g1, b.g2] for b in modelo.barras], "art": [[b.art_i, b.art_j] for b in modelo.barras], "L": [b.L for b in modelo.barras],
        "restr": modelo.restr.astype(int).tolist(), "resortes": modelo.res_mask.astype(int).tolist(),
        "ks": modelo.resortes.tolist(), "kg": [[sp["nodo"], sp["k"], sp["beta"]] for sp in modelo.resortes_giro],
        "unid": [modelo.config["unidad_fuerza"], modelo.config["unidad_longitud"]],
        "fy": [referencia(b.mat) for b in modelo.barras], "refn": ["fy" if b.mat.teoria in ("vm", "tresca") else "sut" for b in modelo.barras], "sadm": [b.mat.sadm for b in modelo.barras], "escala": modelo.config["escala_diagramas"], "dim": float(dim), "pie": pie, "ayuda": AYUDA_3D,
        "escenas": [_escena(modelo, e) for e in escenas],
    }
    datos = json.dumps(D, ensure_ascii=False).replace("</", "<\\/")
    return f'<div class="visor" id="{id_}"></div><script>emp3d("{id_}", {datos});</script>'
