"""Estándar común de los visores interactivos de Struttura (los 4 programas usan esto).
Utilización (modo «Utilización»): u = σeq/fy y σeq/σadm; el recuadro al pasar el mouse muestra ambos; 1 = fluencia (fy) o tensión admisible.

Navegación (estilo SolidWorks / CAD):
    * Girar ............ arrastrar con el botón izquierdo  (o botón central)           [solo visores 3D]
    * Desplazar ........ Ctrl + arrastrar  (o botón derecho)   — en 2D basta con arrastrar
    * Zoom ............. rueda (hacia el cursor)  o  Shift + arrastrar
    * Ajustar vista .... doble clic  o  botón «Ajustar»
Modos de vista (mismo orden y nombres en todos):  Estructura · Cargas · Deformada · [Utilización] · diagramas.
    * «Estructura» muestra SOLO geometría, apoyos y rótulos: nunca cargas ni deformada.
    * Las cargas solo aparecen en el modo «Cargas», o en otros modos si se tilda «superponer cargas».
Diagramas: selector «Barra» = todas / una sola (las demás quedan en gris como contexto).
Rendimiento: las líneas se acumulan en pocos <path> y el redibujado se agrupa por cuadro (requestAnimationFrame).
"""

CSS_COMUN = """
.visor { position: relative; }
.visor .ayuda { font-size: 8.5pt; color: #444; text-align: center; margin: 2pt 0 0; }
.visor .tip { position: absolute; display: none; pointer-events: none; z-index: 5; white-space: nowrap;
      background: rgba(255,255,255,.97); border: 1px solid #9aa5a3; border-radius: 3px; padding: 3px 8px;
      font: 9.5pt/1.4 sans-serif; color: #222; text-align: left; box-shadow: 0 1px 5px rgba(0,0,0,.2); }
.visor .tip .lib { color: #777; }
.visor .ctrl .sep { display: inline-block; width: 10pt; }
.visor .ctrl select:disabled { opacity: .45; }
@media print { .visor .ayuda, .visor .tip { display: none !important; } }
"""

AYUDA_NODOS = "Pasá el mouse sobre un nudo verde (apoyo) o naranja (resorte) para ver sus condiciones de borde"
AYUDA_3D = ("Girar: arrastrar (o botón central) · Desplazar: Ctrl + arrastrar (o botón derecho) · "
            "Zoom: rueda o Shift + arrastrar · Doble clic: ajustar vista · " + AYUDA_NODOS)
AYUDA_2D = ("Desplazar: arrastrar (o Ctrl + arrastrar) · Zoom: rueda o Shift + arrastrar · "
            "Doble clic: ajustar vista · " + AYUDA_NODOS)

NAV_JS = r"""
// Escala de color de la utilización (igual en los 4 visores): 0 verde · 0,5 amarillo · 1 rojo (fluencia) · 1,3 granate
function stColU(u) {
  var stops = [[0, [42, 157, 143]], [0.5, [233, 196, 106]], [1, [230, 57, 70]], [1.3, [120, 0, 30]]];
  u = Math.max(0, Math.min(1.3, Math.round(u * 40) / 40));
  for (var s = 1; s < stops.length; s++) if (u <= stops[s][0]) { var a = stops[s - 1], b = stops[s], f = (u - a[0]) / (b[0] - a[0]);
    return "rgb(" + [0, 1, 2].map(function (i) { return Math.round(a[1][i] + f * (b[1][i] - a[1][i])); }).join(",") + ")"; }
  return "rgb(120,0,30)"; }
// Texto del recuadro de la utilización en un punto (planos): vm = σeq; fy, sadm pueden ser null; us = unidad de tensión
function stTextoU(id, xs, vm, fy, sadm, fm, us, ul, rn) {
  rn = rn || "fy";
  var h = "<b>Barra " + id + "</b><br>x = " + fm(xs) + " " + ul + "<br>σeq = " + fm(vm) + " " + us;
  if (fy) h += "<br>σeq/" + rn + " = <b>" + (vm / fy).toFixed(3) + "</b>" + (vm / fy > 1 ? " (supera 1)" : "");
  if (sadm) h += "<br>σeq/σadm = <b>" + (vm / sadm).toFixed(3) + "</b>" + (vm / sadm > 1 ? " (supera 1)" : "");
  if (!fy && !sadm) h += "<br><span class='lib'>(el material no tiene resistencia de referencia ni σadm)</span>";
  return h; }
function stZoomEn(st, f, mx, my, cx, cy, zmin, zmax) {      // zoom hacia el punto (mx,my) del visor
  var z = Math.max(zmin, Math.min(zmax, st.zoom * f)), g = z / st.zoom;
  st.ox = mx - (mx - st.ox - cx) * g - cx; st.oy = my - (my - st.oy - cy) * g - cy; st.zoom = z;
}
// A = {W, cx, cy, zmin, zmax, rotar(dx,dy)|null, pan(dx,dy), zoomFactor(f,mx,my), reset(), dib()}
function stNav(svg, A) {
  var d = null, raf = 0, pr = 0, pp = [0, 0], pz = 1, pm = null, hecho = false;
  function k() { return A.W / svg.getBoundingClientRect().width; }
  function flush() { raf = 0;
    if (pr && A.rotar) { A.rotar(pr[0], pr[1]); } pr = 0;
    if (pp[0] || pp[1]) { A.pan(pp[0], pp[1]); } pp = [0, 0];
    if (pz !== 1) { A.zoomFactor(pz, pm[0], pm[1]); } pz = 1;
    A.dib(); }
  function prog() { if (!raf) raf = requestAnimationFrame(flush); }
  svg.addEventListener("contextmenu", function (e) { e.preventDefault(); });
  svg.addEventListener("pointerdown", function (e) { d = {x: e.clientX, y: e.clientY}; svg.setPointerCapture(e.pointerId); e.preventDefault(); });
  svg.addEventListener("pointermove", function (e) {
    if (!d) return;
    var dx = (e.clientX - d.x) * k(), dy = (e.clientY - d.y) * k(), b = e.buttons;
    d.x = e.clientX; d.y = e.clientY;
    var r = svg.getBoundingClientRect(), mx = (e.clientX - r.left) * k(), my = (e.clientY - r.top) * k();
    var pan = e.ctrlKey || e.metaKey || (b & 2), zoom = e.shiftKey && !pan;
    if (pan || (!A.rotar && !zoom)) { pp[0] += dx; pp[1] += dy; }
    else if (zoom) { pz *= Math.exp(-dy * 0.012); pm = [mx, my]; }
    else { pr = pr || [0, 0]; pr[0] += dx; pr[1] += dy; }
    prog(); });
  function fin() { d = null; }
  svg.addEventListener("pointerup", fin); svg.addEventListener("pointercancel", fin);
  svg.addEventListener("wheel", function (e) { e.preventDefault(); var r = svg.getBoundingClientRect();
    pm = [(e.clientX - r.left) * k(), (e.clientY - r.top) * k()]; pz *= e.deltaY < 0 ? 1.12 : 1 / 1.12; prog(); }, {passive: false});
  svg.addEventListener("dblclick", function () { A.reset(); A.dib(); });
}
// Acumulador de trazos: pocos <path> en vez de miles de <line> (clave = estilo)
function stLotes(NS, padre) {
  var lotes = {};
  return {
    l: function (p, q, col, w, dash, op) { var key = col + "|" + w + "|" + (dash || "") + "|" + (op || 1);
      (lotes[key] = lotes[key] || []).push("M" + p[0].toFixed(1) + " " + p[1].toFixed(1) + "L" + q[0].toFixed(1) + " " + q[1].toFixed(1)); },
    vaciar: function () { for (var key in lotes) { var a = key.split("|"), e = document.createElementNS(NS, "path");
      e.setAttribute("d", lotes[key].join("")); e.setAttribute("stroke", a[0]); e.setAttribute("stroke-width", a[1]);
      e.setAttribute("fill", "none"); e.setAttribute("stroke-linecap", "round"); if (a[2]) e.setAttribute("stroke-dasharray", a[2]);
      if (a[3] !== "1") e.setAttribute("opacity", a[3]); padre.appendChild(e); } lotes = {}; }
  };
}

// Texto del recuadro de condiciones de borde de un nudo (nom: nombres de GDL; r: restringido; v: valor impuesto; ks: resortes)
function stTexto(tit, nom, r, v, ks, fm, uf, ul) {
  var h = "<b>" + tit + "</b>", lib = [], i, rot;
  for (i = 0; i < nom.length; i++) {
    rot = nom[i].charAt(0) === "φ";
    if (r[i]) { var nz = Math.abs(v[i]) > 1e-12; h += "<br>" + nom[i] + " = " + (nz ? fm(v[i]) + (rot ? " rad" : " " + ul) + " <i>(prefijado)</i>" : "0"); }
    else lib.push(nom[i]); }
  for (i = 0; i < nom.length; i++) if (ks && ks[i] > 0) { rot = nom[i].charAt(0) === "φ";
    h += "<br>k" + (rot ? "φ" + nom[i].slice(1) : nom[i].slice(1)) + " = " + fm(ks[i]) + " " + (rot ? uf + "·" + ul + "/rad" : uf + "/" + ul) + " <i>(resorte)</i>"; }
  if (lib.length) h += '<br><span class="lib">libre: ' + lib.join(", ") + "</span>";
  return h; }
// Recuadro al pasar el mouse (o tocar) sobre un nudo: getHits() -> [{x, y, html}] en coordenadas del visor
function stTip(root, svg, W, getHits) {
  var tip = document.createElement("div"); tip.className = "tip"; root.appendChild(tip);
  function ver(e) {
    var rc = svg.getBoundingClientRect(), k = rc.width / W, mejor = null, dm = 13;
    getHits().forEach(function (h) { var d = Math.hypot(rc.left + h.x * k - e.clientX, rc.top + h.y * k - e.clientY); if (d < dm) { dm = d; mejor = h; } });
    if (!mejor) { tip.style.display = "none"; return; }
    tip.innerHTML = mejor.html; tip.style.display = "block";
    var rr = root.getBoundingClientRect(), x = e.clientX - rr.left + 14, y = e.clientY - rr.top + 14;
    if (x + tip.offsetWidth > rr.width) x = e.clientX - rr.left - tip.offsetWidth - 10;
    tip.style.left = x + "px"; tip.style.top = y + "px"; }
  svg.addEventListener("pointermove", function (e) { if (e.buttons) tip.style.display = "none"; else ver(e); });
  svg.addEventListener("pointerdown", function (e) { if (e.pointerType === "touch") ver(e); });
  svg.addEventListener("pointerleave", function () { tip.style.display = "none"; });
}
"""
