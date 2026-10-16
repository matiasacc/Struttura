'use strict';
/* Dibujo del editor: nodos, barras, apoyos, resortes y cargas, con herramientas para crear y editar.  Proyección ortogonal; en los
   programas planos la vista es fija (planta).  Todo lo que se dibuja sale de las tablas del CSV; todo lo que se edita vuelve a ellas. */
const V = (() => {
  const cv = $('#lienzo'), ctx = cv.getContext('2d'), tip = $('#tip'), wrap = $('#lienzo-wrap');
  let W = 0, H = 0, dpr = 1;
  const cam = { yaw: -35 * Math.PI / 180, elev: 25 * Math.PI / 180, esc: 1, px: 0, py: 0 };
  const opt = { paso: '', iman: true, plano: 'z', planoV: '0', apoyoPreset: 0, caso: '', etiquetas: true, cargas: true,
                carga: {}, cargaBarra: { tipo: '', valor: '', valor2: '', a: '', b: '' }, casoNuevo: 'C1', _desdeNodo: null };
  let ghost = null, hover = null, arr = null;                 // vista previa, elemento bajo el mouse, arrastre en curso
  const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  const es3d = () => S.doc && esq().dim === 3;
  const planar = () => S.doc && esq().dim === 2;

  /* ---------- proyección ---------- */
  function rot(p) {
    const cy = Math.cos(cam.yaw), sy = Math.sin(cam.yaw), ce = Math.cos(cam.elev), se = Math.sin(cam.elev);
    const x1 = cy * p[0] + sy * p[1], y1 = -sy * p[0] + cy * p[1], z1 = p[2] || 0;
    return { u: x1, v: y1 * se + z1 * ce, d: z1 * se - y1 * ce };
  }
  const proy = p => { const r = rot(p); return [W / 2 + cam.px + cam.esc * r.u, H / 2 + cam.py - cam.esc * r.v, r.d]; };
  const dirPantalla = v => { const a = rot(v), o = rot([0, 0, 0]); return [cam.esc * (a.u - o.u), -cam.esc * (a.v - o.v)]; };
  function solve3(A, b) {
    const d = (m) => m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0]) + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]);
    const D = d(A); if (Math.abs(D) < 1e-6) return null;
    return [0, 1, 2].map(k => d(A.map((r, i) => r.map((v, j) => j === k ? b[i] : v))) / D);
  }
  function desproyectar(sx, sy) {                           // punto del plano de trabajo bajo el mouse
    const u = (sx - W / 2 - cam.px) / cam.esc, v = -(sy - H / 2 - cam.py) / cam.esc;
    if (!es3d()) return [u, v, 0];
    const cy = Math.cos(cam.yaw), sn = Math.sin(cam.yaw), ce = Math.cos(cam.elev), se = Math.sin(cam.elev);
    const eje = { x: 0, y: 1, z: 2 }[opt.plano]; const fila = [0, 0, 0]; fila[eje] = 1;
    return solve3([[cy, sn, 0], [-sn * se, cy * se, ce], fila], [u, v, num(opt.planoV) || 0]);
  }

  /* ---------- modelo leído de las tablas ---------- */
  function modelo() {
    const m = { nodos: new Map(), barras: [], apoyos: new Map(), resortes: new Set(), cargas: [], cb: [] };
    if (!S.doc || !esq().dim) return m;
    const nb = blk('NODOS');
    if (nb) for (const f of nb.filas) {
      const id = get(nb, f, 'id'); const p = esq().ejes.map(e => num(get(nb, f, e)));
      if (id && p.every(v => v != null)) { while (p.length < 3) p.push(0); m.nodos.set(id, { id, p }); }
    }
    const bb = blk('BARRAS');
    if (bb) for (const f of bb.filas) {
      const id = get(bb, f, 'id'), i = m.nodos.get(get(bb, f, 'nodo_i')), j = m.nodos.get(get(bb, f, 'nodo_j'));
      if (id && i && j) m.barras.push({ id, i, j, ai: low(get(bb, f, 'art_i')) !== '' && !['0', 'no', 'n', 'false', '-'].includes(low(get(bb, f, 'art_i'))),
                                       aj: low(get(bb, f, 'art_j')) !== '' && !['0', 'no', 'n', 'false', '-'].includes(low(get(bb, f, 'art_j'))) });
    }
    for (const f of filas('APOYOS')) { const n = get(blk('APOYOS'), f, 'nodo'); if (n) m.apoyos.set(n, apoyoDe(n)); }
    for (const f of filas('RESORTES')) { const b = blk('RESORTES'); if (esq().geo.resortes.some(c => num(get(b, f, c)))) m.resortes.add(get(b, f, 'nodo')); }
    const cb = blk('CARGAS');
    if (cb) for (const f of cb.filas) m.cargas.push({ caso: get(cb, f, 'caso'), nodo: get(cb, f, 'nodo'), v: Object.fromEntries(esq().geo.cargas.map(c => [c, num(get(cb, f, c)) || 0])) });
    const bq = blk('CARGAS EN BARRAS');
    if (bq) for (const f of bq.filas) m.cb.push({ caso: get(bq, f, 'caso'), barra: get(bq, f, 'barra'), tipo: get(bq, f, 'tipo'), valor: get(bq, f, 'valor'), valor2: get(bq, f, 'valor2'), a: get(bq, f, 'a') });
    return m;
  }
  function longitud(id) { const m = modelo(); const b = m.barras.find(x => x.id === id); return b ? Math.hypot(...b.j.p.map((v, k) => v - b.i.p[k])) : null; }

  /* ---------- ajuste de vista ---------- */
  function ajustar() {
    resize();
    if (!S.doc || !esq().dim) return;
    if (!es3d()) { cam.yaw = 0; cam.elev = Math.PI / 2; }
    const m = modelo(); const pts = [...m.nodos.values()].map(n => rot(n.p));
    if (!pts.length) {
      const ext = { mm: 6000, cm: 600, m: 6, in: 240, ft: 20 }[low(getP('unidad_longitud')) || 'mm'] || 6000;
      cam.esc = Math.min(W * 0.8, H * 1.0) / ext; cam.px = -W * 0.4; cam.py = H * 0.35; return dibujar();      // el origen queda abajo a la izquierda
    }
    const us = pts.map(p => p.u), vs = pts.map(p => p.v);
    const u0 = Math.min(...us), u1 = Math.max(...us), v0 = Math.min(...vs), v1 = Math.max(...vs);
    const dx = Math.max(u1 - u0, 1e-9), dy = Math.max(v1 - v0, 1e-9);
    cam.esc = Math.min((W - 120) / dx, (H - 120) / dy); if (!isFinite(cam.esc) || cam.esc <= 0) cam.esc = 1;
    if (u1 - u0 < 1e-9 && v1 - v0 < 1e-9) cam.esc = Math.min(W, H) / 10;
    cam.px = -cam.esc * (u0 + u1) / 2; cam.py = cam.esc * (v0 + v1) / 2;
    dibujar();
  }
  function vista(nombre) {
    const v = { iso: [-35, 25], planta: [0, 90], frente: [0, 0], lado: [90, 0] }[nombre];
    cam.yaw = v[0] * Math.PI / 180; cam.elev = v[1] * Math.PI / 180; ajustar();
  }
  function resize() {
    dpr = window.devicePixelRatio || 1; const r = wrap.getBoundingClientRect(); W = Math.max(50, r.width); H = Math.max(50, r.height);
    cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr); ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }
  const redim = () => { resize(); dibujar(); };
  window.addEventListener('resize', redim);
  new ResizeObserver(redim).observe(wrap);

  /* ---------- paso de la grilla ---------- */
  function paso() {
    const v = num(opt.paso); if (v && v > 0) return v;
    const raw = 28 / cam.esc, e = Math.pow(10, Math.floor(Math.log10(raw))), f = raw / e;
    return (f <= 1 ? 1 : f <= 2 ? 2 : f <= 5 ? 5 : 10) * e;
  }
  const ajusta = v => opt.iman ? Math.round(v / paso()) * paso() : v;
  function puntoMouse(ev) {
    const r = cv.getBoundingClientRect(); const sx = ev.clientX - r.left, sy = ev.clientY - r.top;
    const p = desproyectar(sx, sy); if (!p) return { sx, sy, p: null };
    const q = p.map((v, k) => (es3d() && 'xyz'[k] === opt.plano) ? (num(opt.planoV) || 0) : ajusta(v));
    q.forEach((v, k) => { q[k] = Math.round(v * 1e9) / 1e9; });
    return { sx, sy, p: q };
  }

  /* ---------- dibujo ---------- */
  function flecha(x0, y0, x1, y1, col, ancho = 1.6) {
    const dx = x1 - x0, dy = y1 - y0, L = Math.hypot(dx, dy); if (L < 1) return;
    const ux = dx / L, uy = dy / L, h = Math.min(8, L * 0.5);
    ctx.strokeStyle = col; ctx.fillStyle = col; ctx.lineWidth = ancho; ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x1, y1); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x1 - ux * h - uy * h * 0.45, y1 - uy * h + ux * h * 0.45); ctx.lineTo(x1 - ux * h + uy * h * 0.45, y1 - uy * h - ux * h * 0.45); ctx.closePath(); ctx.fill();
  }
  function texto(t, x, y, col, tam = 11, align = 'left') { ctx.fillStyle = col; ctx.font = `${tam}px system-ui, sans-serif`; ctx.textAlign = align; ctx.fillText(t, x, y); }

  function grilla() {
    if (!S.doc || !esq().dim) return;
    const st = paso(); const col = css('--suave'); ctx.lineWidth = 1; ctx.strokeStyle = col;
    if (!es3d()) {
      const px = st * cam.esc; if (px < 7) return;
      const p0 = desproyectar(0, H), p1 = desproyectar(W, 0);
      ctx.beginPath();
      for (let x = Math.ceil(p0[0] / st) * st; x <= p1[0]; x += st) { const s = proy([x, 0, 0])[0]; ctx.moveTo(Math.round(s) + .5, 0); ctx.lineTo(Math.round(s) + .5, H); }
      for (let y = Math.ceil(p0[1] / st) * st; y <= p1[1]; y += st) { const s = proy([0, y, 0])[1]; ctx.moveTo(0, Math.round(s) + .5); ctx.lineTo(W, Math.round(s) + .5); }
      ctx.stroke();
      ctx.strokeStyle = css('--borde'); ctx.beginPath(); const o = proy([0, 0, 0]); ctx.moveTo(o[0] + .5, 0); ctx.lineTo(o[0] + .5, H); ctx.moveTo(0, o[1] + .5); ctx.lineTo(W, o[1] + .5); ctx.stroke();
      return;
    }
    // 3D: grilla del plano de trabajo alrededor del modelo
    const m = modelo(); const ps = [...m.nodos.values()].map(n => n.p); const eje = { x: 0, y: 1, z: 2 }[opt.plano]; const [a, b] = [0, 1, 2].filter(k => k !== eje);
    const rg = k => { const v = ps.map(p => p[k]); return v.length ? [Math.min(...v), Math.max(...v)] : [0, st * 10]; };
    let [a0, a1] = rg(a), [b0, b1] = rg(b); a0 = Math.floor(a0 / st) * st - st; a1 = Math.ceil(a1 / st) * st + st; b0 = Math.floor(b0 / st) * st - st; b1 = Math.ceil(b1 / st) * st + st;
    if ((a1 - a0) / st > 80 || (b1 - b0) / st > 80) return;
    const c = num(opt.planoV) || 0; const P = (x, y) => { const p = [0, 0, 0]; p[a] = x; p[b] = y; p[eje] = c; return proy(p); };
    ctx.beginPath();
    for (let x = a0; x <= a1 + 1e-9; x += st) { const s = P(x, b0), t = P(x, b1); ctx.moveTo(s[0], s[1]); ctx.lineTo(t[0], t[1]); }
    for (let y = b0; y <= b1 + 1e-9; y += st) { const s = P(a0, y), t = P(a1, y); ctx.moveTo(s[0], s[1]); ctx.lineTo(t[0], t[1]); }
    ctx.stroke();
  }
  function triada() {
    const o = [46, H - 40]; const ejes = [[[1, 0, 0], 'x'], [[0, 1, 0], 'y'], [[0, 0, 1], 'z']];
    ctx.lineWidth = 1.4;
    for (const [v, n] of ejes) {
      if (!es3d() && n === 'z') continue;
      const d = dirPantalla(v); const L = Math.hypot(d[0], d[1]) || 1; const k = 26 / (cam.esc || 1);
      const x = o[0] + d[0] / cam.esc * 26, y = o[1] + d[1] / cam.esc * 26; if (Math.hypot(d[0], d[1]) < 1e-6) continue;
      ctx.strokeStyle = css('--apagado'); ctx.beginPath(); ctx.moveTo(o[0], o[1]); ctx.lineTo(x, y); ctx.stroke(); texto(n, x + 3, y - 3, css('--apagado'), 11);
    }
  }
  function simboloApoyo(x, y, flags) {
    const t = S.doc.tipo, col = css('--texto'), geo = esq().geo.apoyos; if (!flags.length) return;
    const tr = flags.filter(c => /^u/.test(c)), ro = flags.filter(c => /^phi/.test(c));
    const todosRot = geo.filter(c => /^phi/.test(c)).every(c => flags.includes(c)) && ro.length > 0;
    ctx.strokeStyle = col; ctx.fillStyle = css('--panel'); ctx.lineWidth = 1.5;
    if ((t === 'portico' || t === 'reticulado') && !(tr.length === 1 && tr[0] === 'ux')) {
      if (todosRot && tr.length === 2) { ctx.fillStyle = col; ctx.fillRect(x - 11, y + 4, 22, 5); hatch(x - 12, y + 9, 24); return; }
      ctx.beginPath(); ctx.moveTo(x, y + 2); ctx.lineTo(x - 9, y + 16); ctx.lineTo(x + 9, y + 16); ctx.closePath(); ctx.fill(); ctx.stroke();
      if (tr.length === 1) { ctx.beginPath(); ctx.arc(x - 4, y + 19, 3, 0, 7); ctx.arc(x + 4, y + 19, 3, 0, 7); ctx.stroke(); hatch(x - 12, y + 23, 24); } else hatch(x - 12, y + 16, 24);
      if (ro.length && !todosRot) texto('φ', x + 12, y + 14, col, 11);
      return;
    }
    if (t === 'portico' || t === 'reticulado') {                         // solo ux: apoyo móvil sobre pared vertical
      ctx.beginPath(); ctx.moveTo(x - 2, y); ctx.lineTo(x - 16, y - 9); ctx.lineTo(x - 16, y + 9); ctx.closePath(); ctx.fill(); ctx.stroke();
      ctx.beginPath(); ctx.arc(x - 19, y - 4, 3, 0, 7); ctx.arc(x - 19, y + 4, 3, 0, 7); ctx.stroke(); return;
    }
    // emparrillado y 3D: triángulo (desplazamientos) + cuadrado (giros) + etiqueta con lo restringido
    if (tr.length) { ctx.beginPath(); ctx.moveTo(x, y + 2); ctx.lineTo(x - 8, y + 15); ctx.lineTo(x + 8, y + 15); ctx.closePath(); ctx.fill(); ctx.stroke(); }
    if (todosRot) { ctx.fillStyle = col; ctx.fillRect(x - 10, y + 15, 20, 4); }
    texto(flags.map(c => c.replace('phi', 'φ')).join(' '), x, y + 30, css('--apagado'), 10, 'center');
  }
  function hatch(x, y, w) { ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + w, y); for (let k = 0; k <= w; k += 5) { ctx.moveTo(x + k, y); ctx.lineTo(x + k - 4, y + 5); } ctx.stroke(); }
  function resorte(x, y) {
    ctx.strokeStyle = css('--apagado'); ctx.lineWidth = 1.3; ctx.beginPath(); ctx.moveTo(x + 4, y + 4);
    for (let k = 1; k <= 6; k++) ctx.lineTo(x + 4 + k * 3 + (k % 2 ? 3 : -3) * 0.6, y + 4 + k * 3 + (k % 2 ? -3 : 3) * 0.6); ctx.stroke(); texto('k', x + 24, y + 26, css('--apagado'), 10);
  }
  const casoVisible = c => !opt.caso || c === opt.caso;

  function cargasNodales(m) {
    const col = '#a4562c', geo = esq().geo; const mx = Math.max(1e-300, ...m.cargas.filter(c => casoVisible(c.caso)).flatMap(c => geo.fuerzas.map(k => Math.abs(c.v[k]))));
    for (const c of m.cargas) {
      if (!casoVisible(c.caso)) continue; const n = m.nodos.get(c.nodo); if (!n) continue; const [x, y] = proy(n.p);
      if (geo.fuera_de_plano) {                                            // emparrillado: pz sale del plano (+z hacia el lector)
        const pz = c.v.pz; if (pz) { ctx.strokeStyle = col; ctx.lineWidth = 1.6; ctx.beginPath(); ctx.arc(x, y, 9, 0, 7); ctx.stroke();
          if (pz > 0) { ctx.fillStyle = col; ctx.beginPath(); ctx.arc(x, y, 2.5, 0, 7); ctx.fill(); } else { ctx.beginPath(); ctx.moveTo(x - 5, y - 5); ctx.lineTo(x + 5, y + 5); ctx.moveTo(x + 5, y - 5); ctx.lineTo(x - 5, y + 5); ctx.stroke(); }
          texto(`${fmt(pz)}`, x + 11, y - 9, col, 11); }
      } else {
        const vec = geo.fuerzas.map(k => c.v[k]); const v3 = es3d() ? vec : [vec[0] || 0, vec[1] || 0, 0];
        const f = Math.hypot(...v3);
        if (f > 0) {
          const d = dirPantalla(v3.map(a => a / (f || 1))); const dl = Math.hypot(d[0], d[1]) / cam.esc || 0;
          const L = Math.max(16, 46 * f / mx); const ux = dl > 1e-6 ? d[0] / (dl * cam.esc) : 0, uy = dl > 1e-6 ? d[1] / (dl * cam.esc) : -1;
          flecha(x - ux * L, y - uy * L, x - ux * 0, y - uy * 0, col);
          texto(geo.fuerzas.map((k, i) => vec[i] ? `${k}=${fmt(vec[i])}` : '').filter(Boolean).join(' '), x - ux * L + 4, y - uy * L - 4, col, 11);
        }
      }
      const mom = geo.momentos.filter(k => c.v[k]);
      if (mom.length) { ctx.strokeStyle = col; ctx.lineWidth = 1.6; ctx.beginPath(); ctx.arc(x, y, 14, 0.3, 4.9); ctx.stroke(); texto(mom.map(k => `${k}=${fmt(c.v[k])}`).join(' '), x + 15, y + 16, col, 11); }
    }
  }
  function dirCarga(tipo, valor, bar) {
    const t = S.doc.tipo, s = Math.sign(num(valor) || 0) || 1; const dx = bar.j.p[0] - bar.i.p[0], dy = bar.j.p[1] - bar.i.p[1], dz = (bar.j.p[2] || 0) - (bar.i.p[2] || 0);
    const L = Math.hypot(dx, dy, dz) || 1;
    if (t === 'portico') {
      if (/^(q|P)$/.test(tipo)) return [-dy / L * s, dx / L * s, 0];
      if (/^(qa|Pa)$/.test(tipo)) return [dx / L * s, dy / L * s, 0];
      if (/^(qgx|qgxp|Pgx)$/.test(tipo)) return [s, 0, 0];
      if (/^(qgy|qgyp|Pgy)$/.test(tipo)) return [0, s, 0];
    }
    if (t === 'portico3d') {
      const m = /^[qP]g([xyz])$/.exec(tipo); if (m) { const v = [0, 0, 0]; v['xyz'.indexOf(m[1])] = s; return v; }
    }
    return null;
  }
  function cargasBarra(m) {
    const col = '#a4562c';
    const vis = m.cb.filter(c => casoVisible(c.caso)); const mucho = vis.length > 30;
    const selB = S.sel && S.sel.k === 'barra' ? S.sel.id : null;
    if (mucho && !selB) texto(`${vis.length} cargas en tramos: elegí un caso (abajo) o una barra para verlas`, 12, H - 12, col, 11);
    for (const c of vis) {
      if (mucho && c.barra !== selB) continue; const b = m.barras.find(x => x.id === c.barra); if (!b) continue;
      const a = proy(b.i.p), z = proy(b.j.p); const L = Math.hypot(z[0] - a[0], z[1] - a[1]); if (L < 1) continue;
      const nx = -(z[1] - a[1]) / L, ny = (z[0] - a[0]) / L;
      const v = dirCarga(c.tipo, c.valor, b); const dist = /^q/.test(c.tipo);
      const txt = `${c.tipo} ${c.valor}${c.valor2 ? '→' + c.valor2 : ''}${c.a ? ' @' + c.a : ''}`;
      let mx = (a[0] + z[0]) / 2, my = (a[1] + z[1]) / 2;
      if (v) {
        const d = dirPantalla(v); const dl = Math.hypot(d[0], d[1]); const ux = dl > 1e-6 ? d[0] / dl : 0, uy = dl > 1e-6 ? d[1] / dl : 0;
        if (dist) { for (let k = 0; k <= 4; k++) { const t = k / 4, x = a[0] + (z[0] - a[0]) * t, y = a[1] + (z[1] - a[1]) * t; flecha(x - ux * 16, y - uy * 16, x, y, col, 1.2); }
          ctx.strokeStyle = col; ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(a[0] - ux * 16, a[1] - uy * 16); ctx.lineTo(z[0] - ux * 16, z[1] - uy * 16); ctx.stroke(); mx -= ux * 20; my -= uy * 20; }
        else { const t = Math.min(1, Math.max(0, (num(c.a) || 0) / (Math.hypot(...b.j.p.map((q, k) => q - b.i.p[k])) || 1))); const x = a[0] + (z[0] - a[0]) * t, y = a[1] + (z[1] - a[1]) * t; flecha(x - ux * 24, y - uy * 24, x, y, col, 1.8); mx = x - ux * 28; my = y - uy * 28; }
      } else { mx += nx * 12; my += ny * 12; }
      if (vis.length <= 14 || c.barra === selB) texto(txt, mx + 3, my - 3, col, 10);
    }
  }

  function dibujar() {
    if (!W) resize();
    ctx.clearRect(0, 0, W, H);
    if (!S.doc) { texto('Abrí un modelo o creá uno nuevo.', 20, 30, css('--apagado'), 13); return; }
    if (!esq().dim) { texto('Modo rápido de soldaduras: sin dibujo de estructura.  Cargá las tablas (ELECTRODOS, SOLDADURAS, CARGAS).', 20, 30, css('--apagado'), 13); return; }
    grilla(); triada();
    const m = modelo(); const col = css('--texto'), ac = css('--acento');
    // barras
    ctx.lineCap = 'round';
    for (const b of m.barras) {
      const sel = S.sel && S.sel.k === 'barra' && S.sel.id === b.id; const hv = hover && hover.k === 'barra' && hover.id === b.id;
      const a = proy(b.i.p), z = proy(b.j.p);
      ctx.strokeStyle = sel ? ac : hv ? css('--apagado') : col; ctx.lineWidth = sel ? 4 : 2.6; ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(z[0], z[1]); ctx.stroke();
      const L = Math.hypot(z[0] - a[0], z[1] - a[1]);
      if (L > 24) {
        const ux = (z[0] - a[0]) / L, uy = (z[1] - a[1]) / L; ctx.fillStyle = css('--panel'); ctx.strokeStyle = col; ctx.lineWidth = 1.4;
        for (const [flag, p, s] of [[b.ai, a, 1], [b.aj, z, -1]]) if (flag) { ctx.beginPath(); ctx.arc(p[0] + ux * 9 * s, p[1] + uy * 9 * s, 3.8, 0, 7); ctx.fill(); ctx.stroke(); }
        if (opt.etiquetas && L > 40 && (m.barras.length <= 40 || sel || hv)) texto(b.id, (a[0] + z[0]) / 2 + 4, (a[1] + z[1]) / 2 - 5, ac, 11);
      }
    }
    // apoyos y resortes
    for (const [n, fl] of m.apoyos) { const nd = m.nodos.get(n); if (nd) { const [x, y] = proy(nd.p); simboloApoyo(x, y, fl); } }
    for (const n of m.resortes) { const nd = m.nodos.get(n); if (nd) { const [x, y] = proy(nd.p); resorte(x, y); } }
    if (opt.cargas) { cargasBarra(m); cargasNodales(m); }
    // nodos
    const etiq = new Map();
    for (const n of m.nodos.values()) {
      const [x, y] = proy(n.p); const sel = S.sel && S.sel.k === 'nodo' && S.sel.id === n.id; const hv = hover && hover.k === 'nodo' && hover.id === n.id;
      ctx.fillStyle = sel ? ac : hv ? css('--apagado') : col; ctx.beginPath(); ctx.arc(x, y, sel ? 5.5 : 4, 0, 7); ctx.fill();
      if (sel) { ctx.strokeStyle = ac; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.arc(x, y, 9, 0, 7); ctx.stroke(); }
      if (opt.etiquetas && (m.nodos.size <= 60 || sel || hv)) { const k = Math.round(x / 6) + ',' + Math.round(y / 6); const e = etiq.get(k) || { x, y, ids: [], sel: false }; e.ids.push(n.id); e.sel = e.sel || sel; etiq.set(k, e); }
    }
    for (const e of etiq.values()) texto(e.ids.join(' = '), e.x + 7, e.y - 7, e.sel ? ac : css('--apagado'), 11);   // varios nodos en el mismo punto: una sola etiqueta «2 = 3»
    // herramientas: banda elástica y vista previa
    if (opt._desdeNodo && m.nodos.get(opt._desdeNodo)) {
      const a = proy(m.nodos.get(opt._desdeNodo).p); const g = ghost && ghost.p ? proy(ghost.p) : null;
      if (g) { ctx.setLineDash([5, 4]); ctx.strokeStyle = ac; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(g[0], g[1]); ctx.stroke(); ctx.setLineDash([]); }
    }
    if (ghost && ghost.p && ['nodo', 'barra'].includes(S.tool) && !(hover && hover.k === 'nodo')) {
      const [x, y] = proy(ghost.p); ctx.strokeStyle = ac; ctx.lineWidth = 1.4; ctx.beginPath(); ctx.arc(x, y, 6, 0, 7); ctx.moveTo(x - 9, y); ctx.lineTo(x + 9, y); ctx.moveTo(x, y - 9); ctx.lineTo(x, y + 9); ctx.stroke();
      texto(ghost.p.slice(0, esq().dim === 3 ? 3 : 2).map(fmt).join(', '), x + 11, y + 18, ac, 11);
    }
  }

  /* ---------- selección bajo el mouse ---------- */
  function bajoMouse(sx, sy) {
    const m = modelo(); let mejor = null, dm = 11;
    for (const n of m.nodos.values()) { const p = proy(n.p); const d = Math.hypot(p[0] - sx, p[1] - sy); if (d < dm) { dm = d; mejor = { k: 'nodo', id: n.id }; } }
    if (mejor) return mejor;
    dm = 7;
    for (const b of m.barras) {
      const a = proy(b.i.p), z = proy(b.j.p); const dx = z[0] - a[0], dy = z[1] - a[1], L2 = dx * dx + dy * dy; if (L2 < 1) continue;
      const t = Math.max(0, Math.min(1, ((sx - a[0]) * dx + (sy - a[1]) * dy) / L2)); const d = Math.hypot(a[0] + t * dx - sx, a[1] + t * dy - sy);
      if (d < dm) { dm = d; mejor = { k: 'barra', id: b.id }; }
    }
    return mejor;
  }
  function textoTip(h) {
    const m = modelo();
    if (h.k === 'nodo') { const n = m.nodos.get(h.id); const fl = m.apoyos.get(h.id) || []; const ncarg = m.cargas.filter(c => c.nodo === h.id).length;
      return `Nodo ${h.id}\n${esq().ejes.map((e, i) => `${e} = ${fmt(n.p[i])}`).join('   ')}` + (fl.length ? `\nApoyo: ${fl.join(' ')}` : '') + (ncarg ? `\n${ncarg} carga(s)` : ''); }
    const b = m.barras.find(x => x.id === h.id); const bb = blk('BARRAS'); const f = bb.filas.find(x => get(bb, x, 'id') === h.id);
    return `Barra ${h.id}   ${b.i.id} → ${b.j.id}\nL = ${fmt(longitud(h.id))}   ${get(bb, f, 'material')} / ${get(bb, f, 'seccion')}`;
  }

  /* ---------- herramientas ---------- */
  const HERR = [['sel', 'Seleccionar', 'V'], ['nodo', 'Nodo', 'N'], ['barra', 'Barra', 'B'], ['apoyo', 'Apoyo', 'A'], ['carga', 'Carga', 'C'], ['cbarra', 'Carga en tramo', 'L'], ['borrar', 'Borrar', 'X']];
  function herramientas() {
    const box = $('#herr'); box.textContent = '';
    if (!S.doc || !esq().dim) { box.append(el('span', { class: 'nota' }, S.doc ? 'Sin dibujo en este modo.' : '')); return; }
    HERR.forEach(([k, n, t]) => box.append(el('button', { class: S.tool === k ? 'activo' : '', title: `${n} (${t})`, onclick: () => usar(k) }, n)));
    box.append(el('span', { class: 'sepv' }));
    const ctxp = [];
    if (['nodo', 'barra', 'sel'].includes(S.tool)) {
      ctxp.push(el('label', {}, 'Paso', el('input', { type: 'text', value: opt.paso, placeholder: fmt(paso()), onchange: e => { opt.paso = e.target.value; } })),
                el('label', {}, el('input', { type: 'checkbox', checked: opt.iman, onchange: e => { opt.iman = e.target.checked; } }), 'Imán'));
      if (es3d()) ctxp.push(el('label', {}, 'Plano', el('select', { onchange: e => { opt.plano = e.target.value; dibujar(); } }, ['x', 'y', 'z'].map(a => el('option', { value: a, selected: opt.plano === a }, a + ' =')))),
                            el('input', { type: 'text', value: opt.planoV, onchange: e => { opt.planoV = e.target.value; dibujar(); } }));
    }
    if (S.tool === 'apoyo') ctxp.push(el('label', {}, 'Tipo de apoyo', el('select', { onchange: e => { opt.apoyoPreset = +e.target.value; } },
      [...presetsApoyo().map(p => p[0]), 'Quitar apoyo'].map((n, i) => el('option', { value: i, selected: opt.apoyoPreset === i }, n)))));
    if (S.tool === 'carga') {
      ctxp.push(el('label', {}, 'Caso de carga', el('input', { type: 'text', value: opt.casoNuevo, list: 'dl-casos', onchange: e => { opt.casoNuevo = e.target.value; } })));
      esq().geo.cargas.forEach(c => ctxp.push(el('label', { title: colDe('CARGAS', c).ay }, conUnidad(colDe('CARGAS', c)).replace(' en ', ' ').replace('alrededor de ', '').replace('perpendicular al plano (z)', 'en z'), el('input', { type: 'text', value: opt.carga[c] || '', placeholder: '0', onchange: e => { opt.carga[c] = e.target.value; } }))));
    }
    if (S.tool === 'cbarra') {
      const sp = spec('CARGAS EN BARRAS'); const tipos = sp.cols.find(c => c.n === 'tipo').op; if (!opt.cargaBarra.tipo) opt.cargaBarra.tipo = tipos[0];
      ctxp.push(el('label', {}, 'Caso de carga', el('input', { type: 'text', value: opt.casoNuevo, list: 'dl-casos', onchange: e => { opt.casoNuevo = e.target.value; } })),
        el('label', {}, 'Tipo de carga', el('select', { title: sp.cols.find(c => c.n === 'tipo').ay, onchange: e => { opt.cargaBarra.tipo = e.target.value; } }, tipos.map(t => el('option', { value: t, selected: t === opt.cargaBarra.tipo }, nombreOpc(sp.cols.find(c => c.n === 'tipo'), t))))));
      sp.cols.filter(c => ['valor', 'valor2', 'a', 'b'].includes(c.n)).forEach(c => ctxp.push(el('label', { title: c.ay }, c.et + (c.u && unidad(c.u) ? ` [${unidad(c.u)}]` : ''), el('input', { type: 'text', value: opt.cargaBarra[c.n] || '', onchange: e => { opt.cargaBarra[c.n] = e.target.value; } }))));
    }
    box.append(...ctxp);
    box.append(el('span', { class: 'sepv' }), el('button', { onclick: ajustar, title: 'Ajustar la vista al modelo (doble clic en el dibujo)' }, 'Ajustar'));
    if (es3d()) ['iso', 'planta', 'frente', 'lado'].forEach(n => box.append(el('button', { class: 'chico', onclick: () => vista(n) }, n[0].toUpperCase() + n.slice(1))));
    box.append(el('span', { class: 'sepv' }),
      el('label', {}, 'Caso', el('select', { onchange: e => { opt.caso = e.target.value; dibujar(); } }, el('option', { value: '' }, 'todos'), casos().map(c => el('option', { value: c, selected: c === opt.caso }, c)))),
      el('label', {}, el('input', { type: 'checkbox', checked: opt.etiquetas, onchange: e => { opt.etiquetas = e.target.checked; dibujar(); } }), 'Etiquetas'),
      el('label', {}, el('input', { type: 'checkbox', checked: opt.cargas, onchange: e => { opt.cargas = e.target.checked; dibujar(); } }), 'Cargas'));
  }
  function usar(k) { S.tool = k; opt._desdeNodo = null; herramientas(); dibujar(); cv.style.cursor = k === 'sel' ? 'default' : 'crosshair'; }

  /* ---------- interacción ---------- */
  function clicHerramienta(ev, pm) {
    const h = bajoMouse(pm.sx, pm.sy);
    if (S.tool === 'sel') return seleccionar(h);
    if (S.tool === 'nodo') {
      if (h && h.k === 'nodo') return seleccionar(h);
      if (!pm.p) return aviso('Girá la vista: el plano de trabajo se ve de canto.');
      const id = crearNodo(pm.p); return seleccionar({ k: 'nodo', id });
    }
    if (S.tool === 'barra') {
      let nodo = h && h.k === 'nodo' ? h.id : null;
      if (!nodo) { if (!pm.p) return aviso('Girá la vista: el plano de trabajo se ve de canto.'); nodo = crearNodo(pm.p); }
      if (!opt._desdeNodo) { opt._desdeNodo = nodo; seleccionar({ k: 'nodo', id: nodo }); return dibujar(); }
      const id = crearBarra(opt._desdeNodo, nodo); opt._desdeNodo = nodo; if (id) seleccionar({ k: 'barra', id }); return dibujar();
    }
    if (S.tool === 'apoyo') {
      if (!h || h.k !== 'nodo') return;
      const pr = presetsApoyo(); fijarApoyo(h.id, opt.apoyoPreset < pr.length ? pr[opt.apoyoPreset][1] : []); return seleccionar(h);
    }
    if (S.tool === 'carga') {
      if (!h || h.k !== 'nodo') return;
      const v = {}; esq().geo.cargas.forEach(c => { if ((opt.carga[c] || '').trim() !== '') v[c] = opt.carga[c]; });
      if (!Object.keys(v).length) return aviso('Escribí el valor de al menos una componente de la carga (en la barra de herramientas).');
      agregarCargaNodo(h.id, opt.casoNuevo || 'C1', v); return seleccionar(h);
    }
    if (S.tool === 'cbarra') {
      if (!h || h.k !== 'barra') return;
      const v = { caso: opt.casoNuevo || 'C1', tipo: opt.cargaBarra.tipo }; ['valor', 'valor2', 'a', 'b'].forEach(c => { if ((opt.cargaBarra[c] || '').trim() !== '') v[c] = opt.cargaBarra[c]; });
      if (!v.valor) return aviso('Escribí el valor de la carga (en la barra de herramientas).');
      agregarCargaBarra(h.id, v); return seleccionar(h);
    }
    if (S.tool === 'borrar') { if (h) borrarElemento(h.k, h.id); }
  }
  let down = null;
  cv.addEventListener('contextmenu', e => e.preventDefault());
  cv.addEventListener('pointerdown', ev => {
    cv.setPointerCapture(ev.pointerId); const pm = puntoMouse(ev);
    down = { x: ev.clientX, y: ev.clientY, mov: false, boton: ev.button, ctrl: ev.ctrlKey || ev.metaKey, pan0: [cam.px, cam.py], yaw0: cam.yaw, el0: cam.elev, nodo: null };
    const h = bajoMouse(pm.sx, pm.sy);
    if (ev.button === 0 && !down.ctrl && S.tool === 'sel' && h && h.k === 'nodo') { down.nodo = h.id; down.snap = snap(); }
  });
  cv.addEventListener('pointermove', ev => {
    const pm = puntoMouse(ev); ghost = pm;
    if (down) {
      const dx = ev.clientX - down.x, dy = ev.clientY - down.y; if (Math.hypot(dx, dy) > 3) down.mov = true;
      if (down.mov) {
        if (down.nodo) { if (pm.p) { moverNodo(down.nodo, pm.p.slice(0, esq().dim)); S.sucio = true; dibujar(); } return; }
        const orbitar = es3d() && down.boton === 0 && !down.ctrl;
        if (orbitar) { cam.yaw = down.yaw0 + dx * 0.008; cam.elev = Math.max(-1.55, Math.min(1.55, down.el0 + dy * 0.008)); }
        else { cam.px = down.pan0[0] + dx; cam.py = down.pan0[1] + dy; }
        dibujar(); return;
      }
    }
    const h = bajoMouse(pm.sx, pm.sy); const cambio_ = JSON.stringify(h) !== JSON.stringify(hover); hover = h;
    if (h) { tip.textContent = textoTip(h); tip.style.display = 'block'; const r = wrap.getBoundingClientRect(); tip.style.left = Math.min(pm.sx + 14, r.width - tip.offsetWidth - 6) + 'px'; tip.style.top = Math.min(pm.sy + 14, r.height - tip.offsetHeight - 6) + 'px'; }
    else tip.style.display = 'none';
    if (cambio_ || ['nodo', 'barra'].includes(S.tool)) dibujar();
  });
  cv.addEventListener('pointerup', ev => {
    const d = down; down = null; if (!d) return;
    if (d.nodo && d.mov) { empujar(d.snap); cambio(); if (S.bloque === 'NODOS') renderTabla(); renderInspector(); return; }
    if (!d.mov && d.boton === 0) clicHerramienta(ev, puntoMouse(ev));
  });
  cv.addEventListener('pointerleave', () => { hover = null; ghost = null; tip.style.display = 'none'; dibujar(); });
  cv.addEventListener('dblclick', () => { if (S.tool === 'sel') ajustar(); });
  cv.addEventListener('wheel', ev => {
    ev.preventDefault(); const r = cv.getBoundingClientRect(); const sx = ev.clientX - r.left, sy = ev.clientY - r.top;
    const k = Math.exp(-ev.deltaY * 0.0015); const e0 = cam.esc; cam.esc = Math.max(1e-6, e0 * k);
    cam.px = (cam.px + W / 2 - sx) * (cam.esc / e0) - W / 2 + sx; cam.py = (cam.py + H / 2 - sy) * (cam.esc / e0) - H / 2 + sy; dibujar();
  }, { passive: false });
  window.addEventListener('keydown', ev => {
    if (!S.doc || ev.target.closest('input,select,textarea') || ev.ctrlKey || ev.metaKey) return;
    const m = { v: 'sel', n: 'nodo', b: 'barra', a: 'apoyo', c: 'carga', l: 'cbarra', x: 'borrar' }[ev.key.toLowerCase()];
    if (m && esq().dim) { usar(m); ev.preventDefault(); }
    if (ev.key === 'Escape') { opt._desdeNodo = null; usar('sel'); }
    if ((ev.key === 'Delete' || ev.key === 'Supr') && S.sel) borrarElemento(S.sel.k, S.sel.id);
  });
  return { dibujar, ajustar, redim, herramientas, longitud, vista, usar, opt, cam, modelo, proy, bajoMouse };
})();
window.V = V;
