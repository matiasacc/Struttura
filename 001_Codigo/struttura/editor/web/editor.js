'use strict';
/* Editor de Struttura – núcleo: estado, documento, tablas, inspector, archivos, revisión y cálculo.  Todo se guarda en el CSV. */
const CFG = window.CFG;
const $ = (s, r = document) => r.querySelector(s);
function el(tag, attrs, ...kids) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (k === 'class') e.className = v;
    else if (k === 'text') e.textContent = v;
    else if (k.startsWith('on')) e.addEventListener(k.slice(2), v);
    else if (v === true) e.setAttribute(k, '');
    else if (v !== false && v != null) e.setAttribute(k, v);
  }
  kids.flat().forEach(c => { if (c != null && c !== false) e.append(c.nodeType ? c : document.createTextNode(c)); });
  return e;
}
async function api(ruta, datos) {
  const r = await fetch('/api/' + ruta, { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Struttura-Token': CFG.token }, body: JSON.stringify(datos || {}) });
  const j = await r.json();
  if (!r.ok) throw new Error(j.error || ('Error ' + r.status));
  return j;
}

/* ------------------------------------------------------------------ estado */
const S = { doc: null, ruta: null, nombre: 'sin título', sucio: false, bloque: 'PROYECTO', undo: [], redo: [], pend: null,
            rev: null, calc: null, bib: { materiales: [], electrodos: [], electrodos_tabla: [], perfiles: [] }, dec: ',', sel: null, tool: 'sel', detalle: false };
const esq = () => CFG.esquemas[S.doc.tipo];
const spec = t => esq().bloques.find(b => b.t === t);
const low = s => String(s == null ? '' : s).trim().toLowerCase();

function blk(t, crear) {
  let b = S.doc.bloques.find(x => x.t === t);
  if (!b && crear) {
    const sp = spec(t);
    b = { t, antes: [], cab: sp.k === 'claves' ? null : (sp.min ? sp.min.slice() : sp.cols.map(c => c.n)), filas: [], fin: [] };
    const orden = esq().bloques.map(x => x.t);
    const i = S.doc.bloques.findIndex(x => orden.indexOf(x.t) > orden.indexOf(t));
    if (i < 0) S.doc.bloques.push(b); else S.doc.bloques.splice(i, 0, b);
  }
  return b;
}
const ci = (b, n) => b.cab.findIndex(c => low(c) === low(n));
function ensureCol(b, n) {
  let i = ci(b, n);
  if (i < 0) { b.cab.push(n); b.filas.forEach(f => f.c.push('')); i = b.cab.length - 1; }
  return i;
}
function get(b, f, n) { const i = ci(b, n); return i < 0 ? '' : String(f.c[i] == null ? '' : f.c[i]); }
function set(b, f, n, v) { const i = ensureCol(b, n); while (f.c.length < b.cab.length) f.c.push(''); f.c[i] = v; }
const filaVacia = b => ({ c: b.cab.map(() => ''), n: [] });
const filas = t => { const b = blk(t); return b ? b.filas : []; };
function claveP(k) { const b = blk('PROYECTO'); return b ? b.filas.find(f => low(f.c[0]) === k) : null; }
function getP(k) { const f = claveP(k); return f ? String(f.c[1] || '') : ''; }
function setP(k, v) {
  const b = blk('PROYECTO', true); let f = claveP(k);
  if (!f) { f = { c: [k, ''], n: [] }; b.filas.push(f); }
  f.c[1] = v;
}
const esNum = s => /^[+-]?(\d+([.,]\d*)?|[.,]\d+)([eE][+-]?\d+)?$/.test(String(s).trim());
const num = s => { const t = String(s == null ? '' : s).trim().replace(',', '.'); if (t === '') return null; const v = Number(t); return Number.isFinite(v) ? v : null; };
function fmt(v) { let t = String(+Number(v).toPrecision(9)); if (/e/i.test(t)) t = Number(v).toFixed(6).replace(/\.?0+$/, ''); return S.dec === ',' ? t.replace('.', ',') : t; }
function detectarDec() {
  for (const b of S.doc.bloques) for (const f of b.filas) for (const c of f.c) if (/^[+-]?\d+,\d+$/.test(String(c).trim())) return ',';
  for (const b of S.doc.bloques) for (const f of b.filas) for (const c of f.c) if (/^[+-]?\d+\.\d+$/.test(String(c).trim())) return '.';
  return ',';
}

/* ------------------------------------------------------------------ listas de identificadores */
function ids(t, col) { return filas(t).map(f => get(blk(t), f, col)).filter(x => x !== ''); }
function casos() {
  const out = [];
  for (const [t, c] of [['CARGAS', 'caso'], ['CARGAS EN BARRAS', 'caso'], ['DESPLAZAMIENTOS PREFIJADOS', 'caso'], ['DESAJUSTE DE RESORTES', 'caso']])
    if (blk(t)) for (const f of blk(t).filas) { const v = get(blk(t), f, c); if (v && !out.includes(v)) out.push(v); }
  const pp = getP('peso_propio'); if (pp && !out.includes(pp)) out.push(pp);
  return out;
}
function combinaciones() { const o = []; if (blk('COMBINACIONES')) for (const f of blk('COMBINACIONES').filas) { const v = get(blk('COMBINACIONES'), f, 'combinacion'); if (v && !o.includes(v)) o.push(v); } return o; }
const REF = { nodos: ['NODOS', 'id'], barras: ['BARRAS', 'id'], materiales: ['MATERIALES', 'id'], secciones: ['SECCIONES', 'id'], soldaduras: ['SOLDADURAS', 'id'], electrodos: ['ELECTRODOS', 'id'] };
function actualizarListas() {
  const cont = $('#listas'); cont.textContent = '';
  const mk = (id, vals) => cont.append(el('datalist', { id }, vals.map(v => typeof v === 'string' ? el('option', { value: v }) : el('option', { value: v.n }, v.t))));
  for (const k of Object.keys(REF)) mk('dl-' + k, ids(...REF[k]));
  mk('dl-casos', casos());
  mk('dl-casos-comb', [...casos(), ...combinaciones()]);
  mk('dl-lib_materiales', S.bib.materiales);
  mk('dl-lib_electrodos', S.bib.electrodos);
  mk('dl-lib_perfiles', S.bib.perfiles);
  mk('dl-nombres_electrodos', [...ids('ELECTRODOS', 'id'), ...S.bib.electrodos.map(e => e.t), ...S.bib.electrodos_tabla]);
}

/* ------------------------------------------------------------------ edición con deshacer */
const snap = () => JSON.stringify(S.doc);
function empujar(s) { S.undo.push(s); if (S.undo.length > 150) S.undo.shift(); S.redo = []; }
function mut(fn) { const s = snap(); fn(); empujar(s); cambio(); }
function cambio() { S.sucio = true; actualizarListas(); refrescoLigero(); programarRevision(); }
function refrescoLigero() { renderPasos(); renderArchivo(); renderEstado(); if (window.V) V.dibujar(); renderBotones(); }
function deshacer() { cerrarPend(); if (!S.undo.length) return; S.redo.push(snap()); S.doc = JSON.parse(S.undo.pop()); restaurar(); }
function rehacer() { cerrarPend(); if (!S.redo.length) return; S.undo.push(snap()); S.doc = JSON.parse(S.redo.pop()); restaurar(); }
function cerrarPend() { if (S.pend != null) { empujar(S.pend); S.pend = null; } }
function restaurar() {
  S.sucio = true;
  if (S.sel && !existeSel(S.sel)) S.sel = null;
  actualizarListas(); renderTodo(); programarRevision();
}
const existeSel = s => s.k === 'nodo' ? ids('NODOS', 'id').includes(s.id) : ids('BARRAS', 'id').includes(s.id);

/* renombrar un identificador actualiza todo lo que lo nombra */
function propagarRenombre(tipoRef, viejo, nuevo) {
  if (!viejo || viejo === nuevo) return;
  for (const sp of esq().bloques) {
    const b = blk(sp.t); if (!b || !b.cab) continue;
    for (const c of sp.cols) if (c.t === 'ref:' + tipoRef && ci(b, c.n) >= 0)
      for (const f of b.filas) if (get(b, f, c.n) === viejo) set(b, f, c.n, nuevo);
  }
}

/* ------------------------------------------------------------------ pasos (navegación entre bloques) */
function renderPasos() {
  const nav = $('#pasos'); nav.textContent = '';
  const bl = esq().bloques; let n = 0, sepPuesta = false;
  bl.forEach((sp, k) => {
    if (!sp.ob && !sepPuesta) { nav.append(el('span', { class: 'sep' })); sepPuesta = true; }
    const b = blk(sp.t); const cant = b ? (sp.k === 'claves' ? b.filas.filter(f => String(f.c[1] || '').trim()).length : b.filas.length) : 0;
    const ok = cant > 0;
    n += sp.ob ? 1 : 0;
    const e = el('button', { class: 'paso' + (S.bloque === sp.t ? ' sel' : '') + (sp.ob && !ok && sp.k !== 'claves' ? ' falta' : ''), onclick: () => irBloque(sp.t), title: sp.ay },
      sp.ob ? el('span', { class: 'n' }, String(n)) : null, sp.et,
      sp.k === 'claves' ? null : el('span', { class: ok ? 'marca-ok' : 'req' }, ok ? '✔ ' + cant : (sp.ob ? '•' : '')));
    nav.append(e);
    if (sp.ob && k < bl.length - 1 && bl[k + 1].ob) nav.append(el('span', { class: 'flecha' }, '›'));
  });
}
function irBloque(t) { cerrarPend(); S.bloque = t; renderPasos(); renderTabla(); }

/* ------------------------------------------------------------------ tabla del bloque */
function colsVisibles(b, sp) {
  const cols = sp.cols.slice(); const conocidas = new Set(cols.map(c => low(c.n)));
  (b.cab || []).forEach(n => { if (!conocidas.has(low(n))) cols.push({ n, t: 'txt', ay: 'Columna que el programa no usa (se conserva en el archivo)', extra: true }); });
  return cols;
}
function colsMostradas(b, sp) {                  // en SECCIONES: solo los datos que usan las formas elegidas (o que ya tienen valor)
  let cols = colsVisibles(b, sp);
  if (sp.t === 'SECCIONES') { const ord = ['id', 'tipo', 'lib', 'd', 'b', 'h', 't', 'tf', 'tw', 'a', 'i', 'iy', 'iz', 'j', 'cy', 'cz', 'c', 'wt', 'kv']; const k = c => { const i = ord.indexOf(c.n); return i < 0 ? 99 : i; }; cols = cols.slice().sort((x, y) => k(x) - k(y)); }
  if (sp.t !== 'SECCIONES' || S.todasCols) return cols;
  const usadas = new Set(['id', 'tipo']);
  for (const f of b.filas) {
    const u = esq().seccion_campos[low(get(b, f, 'tipo'))];
    if (!u) return cols;                                   // forma sin elegir o desconocida: se muestra todo
    [...u.ob, ...u.op].forEach(c => usadas.add(c));
    cols.forEach(c => { if (get(b, f, c.n) !== '') usadas.add(c.n); });
  }
  return cols.filter(c => usadas.has(c.n) || c.extra);
}
function opcionesCon(col, valor) { const op = col.op || []; return (valor !== '' && !op.some(o => low(o) === low(valor))) ? [...op, valor] : op; }
function errFila(t, r) { return S.rev && !S.rev.ok && S.rev.bloque === t && S.rev.fila === r; }

/* ---- nombres claros: etiqueta, unidad y nombre de cada opción (el CSV conserva los nombres de siempre) */
const colDe = (t, n) => (spec(t) || { cols: [] }).cols.find(c => low(c.n) === low(n));
const etq = (t, n) => { const c = colDe(t, n); return c ? c.et : n; };
function unidad(cod) {
  const F = getP('unidad_fuerza') || 'N', L = getP('unidad_longitud') || 'mm';
  return ({ F, L, S: `${F}/${L}²`, FL: `${F}·${L}`, K: `${F}/${L}`, KG: `${F}·${L}/rad`, L2: `${L}²`, L3: `${L}³`, L4: `${L}⁴`, rad: 'rad', deg: '°', rho: 'kg/m³', alfa: '1/°C' })[cod] || '';
}
/* ---- conversión de unidades al escribir «5 in», «2 kN», «30 ksi»: al aceptar la celda se pasa a la unidad del proyecto */
const U_BASE = { mm: [0.001, 'L'], cm: [0.01, 'L'], m: [1, 'L'], in: [0.0254, 'L'], ft: [0.3048, 'L'],
  N: [1, 'F'], kN: [1e3, 'F'], MN: [1e6, 'F'], kgf: [9.80665, 'F'], tf: [9806.65, 'F'], lbf: [4.4482216152605, 'F'], kip: [4448.2216152605, 'F'],
  rad: [1, 'A'], deg: [Math.PI / 180, 'A'], '°': [Math.PI / 180, 'A'] };
const U_PRES = { Pa: 1, kPa: 1e3, MPa: 1e6, GPa: 1e9, psi: 6894.757293168, ksi: 6894757.293168 };   // N/m²
function parseUnidad(t) {                      // → { f: factor al SI (N, m, rad), d: {F, L, A} } o null
  const d = { F: 0, L: 0, A: 0 }; let f = 1;
  const partes = t.trim().replace(/\s+/g, '').split('/');
  for (let i = 0; i < partes.length; i++) {
    const signo = i === 0 ? 1 : -1;
    for (const tok of partes[i].split(/[·*]/)) {
      const m = tok.match(/^([A-Za-z°]+)(?:\^?(-?\d)|(²)|(³))?$/); if (!m) return null;
      const e = (m[3] ? 2 : m[4] ? 3 : m[2] ? +m[2] : 1) * signo;
      if (U_PRES[m[1]] != null) { f *= Math.pow(U_PRES[m[1]], e); d.F += e; d.L -= 2 * e; continue; }
      const u = U_BASE[m[1]]; if (!u) return null;
      f *= Math.pow(u[0], e); d[u[1]] += e;
    }
  }
  return { f, d };
}
function convertirUnidad(texto, destino) {     // → { v } convertido, { err } o null si no trae unidad
  const t = String(texto).trim(); if (!t || !destino) return null;
  const m = t.match(/^([-+]?(?:\d+[.,]?\d*|[.,]\d+)(?:[eE][-+]?\d+)?)\s*([A-Za-z°].*)$/); if (!m) return null;
  const o = parseUnidad(m[2]), dst = parseUnidad(destino);
  if (!o) return { err: `unidad «${m[2]}» no reconocida` };
  if (!dst) return null;
  if (['F', 'L', 'A'].some(k => o.d[k] !== dst.d[k])) return { err: `«${m[2]}» no corresponde a esta columna (se espera ${destino})` };
  return { v: fmt(parseFloat(m[1].replace(',', '.')) * o.f / dst.f) };
}
const conUnidad = c => c.et + (c.u && unidad(c.u) ? ` [${unidad(c.u)}]` : '');
const nombreOpc = (c, o) => (c && c.ope && c.ope[o]) || o;
const SI = ['1', 'si', 'sí', 's', 'x', 'true', 'yes'];
const esSi = v => SI.includes(low(v));

/* ---- textos de los desplegables: «id: detalle» */
const fichaMat = n => S.bib.materiales.find(m => m.n === String(n).trim());
function detalle(tipo, id) {
  if (tipo === 'nodos') { const b = blk('NODOS'), f = b && b.filas.find(x => get(b, x, 'id') === id); return f ? '(' + esq().ejes.map(e => get(b, f, e)).join('; ') + ')' : ''; }
  if (tipo === 'barras') { const b = blk('BARRAS'), f = b && b.filas.find(x => get(b, x, 'id') === id); return f ? `${get(b, f, 'nodo_i')} → ${get(b, f, 'nodo_j')}` : ''; }
  if (tipo === 'materiales') {
    const b = blk('MATERIALES'), f = b && b.filas.find(x => get(b, x, 'id') === id); if (!f) return '';
    const lib = get(b, f, 'lib'); const m = lib && fichaMat(lib); if (m) return m.t;
    const p = ['e', 'fy'].filter(c => get(b, f, c)).map(c => `${c === 'e' ? 'E' : 'σy'} = ${get(b, f, c)}`); return p.join(', ');
  }
  if (tipo === 'secciones') {
    const b = blk('SECCIONES'), f = b && b.filas.find(x => get(b, x, 'id') === id); if (!f) return '';
    if (low(get(b, f, 'tipo')) === 'perfil') { const m = S.bib.perfiles.find(x => x.n === get(b, f, 'lib')); return m ? (m.nm || m.t) : 'perfil de la biblioteca (elegir)'; }
    const cd = colDe('SECCIONES', 'tipo'); const forma = nombreOpc(cd, low(get(b, f, 'tipo')));
    const u = (esq().seccion_campos[low(get(b, f, 'tipo'))] || { ob: [], op: [] }); const campos = [...u.ob, ...u.op].filter(c => get(b, f, c));
    return forma + (campos.length ? ' · ' + campos.map(c => `${c} = ${get(b, f, c)}`).join(', ') : '');
  }
  return '';
}
function opcionesRef(tipo, valor) {
  let items = ids(...REF[tipo]).map(id => ({ v: id, t: detalle(tipo, id) ? `${id}: ${detalle(tipo, id)}` : id }));
  if (tipo === 'electrodos') {
    const propios = new Set(items.map(i => i.v));
    items = items.concat(S.bib.electrodos.filter(e => !propios.has(e.t)).map(e => ({ v: e.t, t: `${e.t} (biblioteca n.º ${e.n})` })),
      S.bib.electrodos_tabla.filter(n => !propios.has(n) && !S.bib.electrodos.some(e => e.t === n)).map(n => ({ v: n, t: `${n} (tabla de Shigley)` })));
  }
  if (valor !== '' && !items.some(i => i.v === valor)) items.push({ v: valor, t: valor + '  ← no existe', mal: true });
  return items;
}

/* ---- valores de la biblioteca (para mostrar lo que se completa solo) */
S.fichas = {};
function fichaDe(tipo, lib) {
  if (!lib) return null;
  const destino = S.doc.tipo === 'portico3d' ? '3d' : S.doc.tipo === 'emparrillado' ? 'emparrillado' : 'plano';
  const k = [tipo, lib, getP('unidad_fuerza'), getP('unidad_longitud'), destino].join('|');
  if (S.fichas[k] === undefined) {
    S.fichas[k] = 'pendiente';
    api('ficha', { tipo, lib, unidad_fuerza: getP('unidad_fuerza') || 'N', unidad_longitud: getP('unidad_longitud') || 'mm', destino })
      .then(j => { S.fichas[k] = j; if (['MATERIALES', 'ELECTRODOS', 'SOLDADURAS', 'SECCIONES'].includes(S.bloque)) renderTabla(); renderInspector(); })
      .catch(() => { S.fichas[k] = { ok: false }; });
  }
  const v = S.fichas[k]; return v && v.ok ? v.valores : null;
}
function deBiblioteca(b, f, col) {                  // valor que la biblioteca aporta a una celda vacía, o null
  const lib = get(b, f, 'lib'); if (!lib) return null;
  if (b.t === 'MATERIALES') { const v = fichaDe('material', lib); return v && v[col] != null ? v[col] : null; }
  if (b.t === 'ELECTRODOS') { const v = fichaDe('electrodo', lib); return v && v[col] != null ? v[col] : null; }
  if (b.t === 'SECCIONES') { if (low(get(b, f, 'tipo')) !== 'perfil') return null; const v = fichaDe('perfil', lib); return v && v[col] != null ? v[col] : null; }
  if (b.t === 'SOLDADURAS' && col === 'sy_base') { const v = fichaDe('material', lib); return v && v.fy != null ? v.fy : null; }
  return null;
}
function elegirLib(b, f, valor) {                  // al elegir un material/electrodo de la biblioteca: se anota el n.º y, si falta, el nombre en el modelo
  mut(() => { set(b, f, 'lib', valor); if (b.t === 'SECCIONES') { if (valor) { set(b, f, 'tipo', 'perfil'); if (!get(b, f, 'id')) set(b, f, 'id', idPerfil(valor)); } }
    else if (valor && (b.t === 'MATERIALES' || b.t === 'ELECTRODOS') && !get(b, f, 'id')) set(b, f, 'id', b.t === 'ELECTRODOS' ? (S.bib.electrodos.find(e => e.n === valor) || { t: siguienteId('ELECTRODOS') }).t : siguienteId('MATERIALES')); });
  renderTabla(); renderInspector();
}

/* ---- forma de sección: qué datos usa cada una */
function usoSeccion(b, f, col) {
  if (b.t !== 'SECCIONES' || ['id', 'tipo'].includes(col)) return null;
  const u = esq().seccion_campos[low(get(b, f, 'tipo'))]; if (!u) return null;
  return u.ob.includes(col) ? 'ob' : u.op.includes(col) ? 'op' : 'no';
}

/* ---- el control de una celda (lo usan la tabla y el inspector) */
function control(b, f, col, o = {}) {
  const v = get(b, f, col.n);
  const confirmar = (prev) => {
    cerrarPend();
    if (col.n === 'id' && REF2[b.t] && prev !== undefined) { const s = snap(); propagarRenombre(REF2[b.t], prev, get(b, f, 'id')); if (snap() !== s) empujar(s); }
    cambio(); renderInspector();
  };
  const tras = () => { renderInspector(); if (o.tabla && S.bloque === b.t) renderTabla(); };
  if (col.n === 'suprimida') {                              // barra suprimida: sigue en el archivo pero no entra al cálculo
    const inp = el('select', { title: col.ay, onchange: e => { mut(() => set(b, f, col.n, e.target.value)); tras(); if (window.V) V.dibujar(); } },
      el('option', { value: '' }, 'Activa'), el('option', { value: '1' }, 'Suprimida'));
    inp.value = esSi(v) ? '1' : ''; return inp;
  }
  if (col.t === 'flag' && b.t !== 'APOYOS') {              // por ahora solo la articulación de las barras del pórtico plano
    const inp = el('select', { title: col.ay, onchange: e => { mut(() => set(b, f, col.n, e.target.value)); tras(); } },
      el('option', { value: '' }, 'Rígida'), el('option', { value: '1' }, 'Articulada (M = 0)'));
    inp.value = esSi(v) ? '1' : ''; return inp;
  }
  if (col.t === 'flag') {
    const fijo = esSi(v);
    return el('button', { type: 'button', class: 'apoyo ' + (fijo ? 'fijo' : 'libre'), title: col.ay + '\nClic para cambiar entre Fijo (desplazamiento = 0) y Libre.',
      onclick: () => { mut(() => set(b, f, col.n, fijo ? '' : '1')); if (S.bloque === b.t) renderTabla(); renderInspector(); } }, fijo ? 'Fijo' : 'Libre');
  }
  if (col.n === 'lib' && b.t === 'SECCIONES') {
    const lista = S.bib.perfiles;
    const inp = el('select', { title: col.ay, class: 'lib', onchange: e => elegirLib(b, f, e.target.value) },
      el('option', { value: '' }, lista.length ? '— elegir perfil —' : '(sin biblioteca de perfiles)'), opcionesPerfiles(lista),
      v && !lista.some(m => m.n === v) ? el('option', { value: v }, v + '  ← no está en la biblioteca') : null);
    inp.value = v; return inp;
  }
  if (col.n === 'lib' && ['MATERIALES', 'SOLDADURAS', 'ELECTRODOS'].includes(b.t)) {
    const lista = b.t === 'ELECTRODOS' ? S.bib.electrodos : S.bib.materiales;
    const inp = el('select', { title: col.ay, class: 'lib', onchange: e => elegirLib(b, f, e.target.value) },
      el('option', { value: '' }, lista.length ? '— elegir —' : '(sin biblioteca: ver aviso arriba)'),
      lista.map(m => el('option', { value: m.n }, `${m.n}: ${m.t}`)),
      v && !lista.some(m => m.n === v) ? el('option', { value: v }, v + '  ← no está en la biblioteca') : null);
    inp.value = v; return inp;
  }
  if (col.t === 'opc') {
    const op = opcionesCon(col, v);
    const inp = el('select', { title: col.ay, onchange: e => { mut(() => set(b, f, col.n, e.target.value)); tras(); if (b.t === 'SECCIONES' && col.n === 'tipo') renderTabla(); } },
      el('option', { value: '' }, /^art_/.test(col.n) ? 'Rígida' : col.d ? `(por defecto: ${nombreOpc(col, col.d)})` : ''), op.map(x => el('option', { value: x }, nombreOpc(col, x))));
    inp.value = op.find(x => low(x) === low(v)) || ''; return inp;
  }
  const tipoRef = col.t.startsWith('ref:') ? col.t.slice(4) : null;
  if (tipoRef && tipoRef !== 'casos') {
    const items = opcionesRef(tipoRef, v);
    const inp = el('select', { title: col.ay, class: 'ref', onchange: e => { mut(() => set(b, f, col.n, e.target.value)); tras(); } },
      el('option', { value: '' }, ''), items.map(i => el('option', { value: i.v }, i.t)));
    inp.value = v; if (v !== '' && inp.value !== v) inp.value = ''; if (items.some(i => i.mal && i.v === v)) inp.classList.add('mal'); return inp;
  }
  const lista = tipoRef ? (b.t === 'COMBINACIONES' || b.t === 'PUNTOS DE TENSION' ? 'dl-casos-comb' : 'dl-casos') : (col.lista ? 'dl-' + col.lista : null);
  const uso = usoSeccion(b, f, col.n); const lib = col.t === 'num' && v === '' ? deBiblioteca(b, f, col.n) : null;
  const inp = el('input', { type: 'text', value: v, title: col.ay + (uso === 'no' ? '\n(Esta forma de sección no usa este dato.)' : ''), class: (col.n === 'id' ? 'id ' : '') + (uso === 'no' ? 'no-usa ' : '') + (lib != null ? 'de-lib' : ''),
    list: lista, autocomplete: 'off', spellcheck: 'false', 'data-r': o.r, 'data-c': o.c,
    placeholder: lib != null ? fmt(lib) : (uso === 'ob' ? 'obligatorio' : uso === 'no' ? '—' : ''),
    onfocus: e => { e.target.dataset.prev = e.target.value; S.celda = { t: b.t, f, n: col.n }; },
    oninput: e => {
      if (S.pend == null) S.pend = snap();
      set(b, f, col.n, e.target.value); S.sucio = true;
      if (col.t === 'num') e.target.classList.toggle('mal', e.target.value.trim() !== '' && !esNum(e.target.value));
      if (window.V) V.dibujar(); renderArchivo(); programarRevision(); renderBotones();
    },
    onchange: e => {
      if (col.t === 'num') {
        const c = convertirUnidad(e.target.value, unidadCarga(b, f, col.n) || (col.u ? unidad(col.u) : ''));
        if (c && c.v != null) { aviso(`${e.target.value.trim()} → ${c.v} ${unidadCarga(b, f, col.n) || unidad(col.u)}`); e.target.value = c.v; set(b, f, col.n, c.v); e.target.classList.remove('mal'); }
        else if (c && c.err) { aviso('No se convirtió: ' + c.err); e.target.classList.add('mal'); }
      }
      confirmar(e.target.dataset.prev);
    },
    onpaste: o.pegar ? (e => pegar(e, b, spec(b.t))) : null });
  if (lib != null) inp.title += '\nValor de la biblioteca: se usa mientras esta celda esté vacía; si escribís otro, manda el tuyo.';
  if (col.t === 'num' && v.trim() !== '' && !esNum(v)) inp.classList.add('mal');
  const uc = unidadCarga(b, f, col.n);
  return uc ? el('span', { class: 'con-u' }, inp, el('small', { class: 'u', title: 'Unidad de este valor' }, uc)) : inp;
}
function unidadCarga(b, f, col) {               // unidad del valor de una carga en barra: depende del tipo de carga de la fila
  if (b.t !== 'CARGAS EN BARRAS' || !['valor', 'valor2'].includes(col)) return '';
  const t = low(get(b, f, 'tipo')); if (!t) return '';
  const F = getP('unidad_fuerza') || 'N', L = getP('unidad_longitud') || 'mm';
  if (t.startsWith('temp')) return '°C';
  if (t === 'dl') return L;
  if (t[0] === 'q') return `${F}/${L}`;
  if (t[0] === 'm') return `${F}·${L}`;
  if (t[0] === 'p') return F;
  return '';
}
function editorCelda(b, f, col, r, ci_) { return el('td', {}, control(b, f, col, { r, c: ci_, pegar: true, tabla: true })); }
const REF2 = { NODOS: 'nodos', BARRAS: 'barras', MATERIALES: 'materiales', SECCIONES: 'secciones', SOLDADURAS: 'soldaduras' };

function ajustarAncho() {                      // el panel de tablas se ensancha lo justo para no necesitar la barra de desplazamiento horizontal
  const izq = $('#izq'), w = $('#tabla-wrap'); if (!izq || !w) return;
  const base = S.anchoBase || Math.round(window.innerWidth * 0.54);
  izq.style.width = base + 'px';
  const tope = Math.round(window.innerWidth * 0.85);
  for (let i = 0; i < 3; i++) {
    const falta = w.scrollWidth - w.clientWidth;
    if (falta <= 1) break;
    izq.style.width = Math.min(izq.offsetWidth + falta + 2, tope) + 'px';
  }
  if (window.V) V.redim();
}
function renderTabla() {
  const sp = spec(S.bloque); const wrap = $('#tabla-wrap'); const st = wrap.scrollTop;
  $('#titulo-bloque').replaceChildren(el('h2', {}, sp.et + (sp.ob ? '' : '  (opcional)'), el('small', { class: 'cl' }, sp.k === 'claves' ? '' : sp.t)), el('p', {}, sp.ay));
  const b = blk(sp.t);
  wrap.textContent = '';
  if (sp.k === 'claves') return renderClaves(wrap, sp);
  if (!b || !b.filas.length) {
    wrap.append(...[avisoBiblioteca(sp)].filter(Boolean), el('div', { class: 'vacio' }, sp.ob ? 'Este bloque todavía no tiene filas.' : 'Bloque opcional: si no lo necesitás, dejalo vacío (no se escribe en el archivo).'));
    wrap.append(el('div', { class: 'barra-tabla' }, el('button', { onclick: () => agregarFila() }, '+ Agregar fila'), selectorBiblioteca(sp), botonCalcK(sp)));
    return;
  }
  const cols = colsMostradas(b, sp);
  const tabla = el('table', { class: 't' });
  tabla.append(el('thead', {}, el('tr', {}, el('th', {}, '#'), cols.map(c => el('th', { title: c.ay, class: (c.ob ? 'ob' : '') }, el('span', { class: 'et' }, c.et ? conUnidad(c) : c.n), el('small', { class: 'cl' }, c.n))),
    sp.t === 'APOYOS' ? el('th', { title: 'Resumen: elegir un tipo completa Fijo/Libre de todas las columnas' }, el('span', { class: 'et' }, 'Tipo de apoyo'), el('small', { class: 'cl' }, 'atajo')) : null, el('th', {}, ''))));
  const tb = el('tbody', {});
  b.filas.forEach((f, r) => {
    const tr = el('tr', { class: (errFila(sp.t, r) ? 'err ' : '') + (filaSeleccionada(sp.t, b, f) ? 'sel' : ''), 'data-fila': r },
      el('td', { class: 'idx', onclick: () => seleccionarDesdeFila(b, f), title: errFila(sp.t, r) ? S.rev.error : 'Seleccionar en el dibujo' }, String(r + 1)));
    cols.forEach((c, k) => tr.append(editorCelda(b, f, c, r, k)));
    if (sp.t === 'APOYOS') tr.append(celdaTipoApoyo(b, f));
    tr.append(el('td', { class: 'acc' },
      el('button', { title: 'Duplicar fila', onclick: () => duplicarFila(b, r) }, '⧉'),
      el('button', { title: 'Borrar fila', onclick: () => borrarFilaUI(b, r) }, '✕')));
    tb.append(tr);
  });
  tabla.append(tb);
  wrap.append(...[avisoBiblioteca(sp)].filter(Boolean), tabla, el('div', { class: 'barra-tabla' }, el('button', { onclick: () => agregarFila() }, '+ Agregar fila'), selectorBiblioteca(sp), botonCalcK(sp), sp.t === 'SECCIONES' ? el('label', { class: 'nota' }, el('input', { type: 'checkbox', checked: !!S.todasCols, onchange: e => { S.todasCols = e.target.checked; renderTabla(); } }), ' Mostrar todas las columnas') : null,
    el('span', { class: 'nota' }, 'Se pueden pegar celdas copiadas de Excel (Ctrl+V).  Pasá el mouse por el título de una columna para ver qué es.')));
  wrap.scrollTop = st;
  ajustarAncho();
}
function botonCalcK(sp) { return ['RESORTES', 'RESORTES INCLINADOS'].includes(sp.t) ? el('button', { title: 'Calcula la rigidez axial de una barra, k = E·A/L', onclick: () => calculadoraK(sp) }, 'Calcular k de una barra (EA/L)') : null; }
const EXTREMOS = [['art-art', 'articulado – articulado', 1], ['emp-lib', 'empotrado – libre', 2], ['emp-art', 'empotrado – articulado', 1 / Math.sqrt(2)], ['emp-emp', 'empotrado – empotrado', 0.5]];
function calculadoraK(sp) {                    // k = E·A/L (Gere & Goodno, cap. 2) y carga crítica de Euler Pc = π²·E·I/(K·L)²; se escribe en la celda elegida
  const uF = unidad('F'), uL = unidad('L');
  const num_ = (t, dst) => { const c = convertirUnidad(t, dst); if (c && c.v != null) return parseFloat(String(c.v).replace(',', '.')); if (c && c.err) return NaN; const x = parseFloat(String(t).replace(',', '.')); return isFinite(x) && String(t).trim() !== '' ? x : NaN; };
  const b0 = blk(sp.t, true), kCols = sp.cols.filter(c => /^k[xyz]?$/.test(c.n));
  const cel = S.celda && S.celda.t === sp.t && b0.filas.includes(S.celda.f) ? S.celda : null;            // celda que el usuario tocó antes
  const filaDest = cel ? cel.f : null, colDest = cel && kCols.some(c => c.n === cel.n) ? cel.n : (kCols.length === 1 ? kCols[0].n : null);
  const campos = {}, R = {};
  const mats = filas('MATERIALES').map(f => get(blk('MATERIALES'), f, 'id')).filter(Boolean), secs = filas('SECCIONES').map(f => get(blk('SECCIONES'), f, 'id')).filter(Boolean);
  const salida = el('div', { class: 'resultado-k' });
  const colSel = kCols.length > 1 ? el('select', { onchange: () => { } }, kCols.map(c => el('option', { value: c.n }, c.et || c.n))) : null;
  if (colSel && colDest) colSel.value = colDest;
  const calc = () => {
    const E = num_(campos.E.value, `${uF}/${uL}²`), A = num_(campos.A.value, `${uL}²`), L = num_(campos.L.value, uL), I = num_(campos.I.value, `${uL}⁴`.replace('⁴', '4'));
    const K = EXTREMOS[campos.X.value][2], k = E * A / L; R.k = isFinite(k) && L > 0 && k > 0 ? k : null;
    R.pc = R.k != null && isFinite(I) && I > 0 ? Math.PI ** 2 * E * I / (K * L) ** 2 : null; R.lam = R.pc != null ? K * L / Math.sqrt(I / A) : null;
    salida.textContent = ''; salida.append(R.k == null ? 'Completar E, A y L (con unidades válidas)' : `k = E·A/L = ${fmt(R.k)} ${uF}/${uL}`);
    if (R.pc != null) salida.append(el('br'), `Pc = π²·E·I/(K·L)² = ${fmt(R.pc)} ${uF}   (K = ${fmt(K)}, λ = KL/r = ${fmt(R.lam)})`);
    else if (campos.I.value.trim()) salida.append(el('br'), 'I no válida');
  };
  const fila = (txt, ayuda, inp) => el('label', { class: 'fila-k', title: ayuda }, txt, inp);
  const mk = (ph, f) => el('input', { type: 'text', placeholder: ph, oninput: f || calc, autocomplete: 'off' });
  campos.E = mk(`E [${uF}/${uL}²]`); campos.A = mk(`A [${uL}²]`); campos.L = mk(`L [${uL}]`); campos.I = mk(`I [${uL}⁴] (opcional, para Pc)`);
  campos.X = el('select', { onchange: calc }, EXTREMOS.map((x, i) => el('option', { value: i }, `${x[1]} (K = ${fmt(x[2])})`)));
  const deMat = el('select', { onchange: e => { const b = blk('MATERIALES'), f = b.filas.find(x => get(b, x, 'id') === e.target.value); if (!f) return; const lib = get(b, f, 'lib'); const v = get(b, f, 'e') || (lib && (fichaDe('material', lib) || {}).e); if (v != null && v !== '') campos.E.value = String(v); calc(); } },
    el('option', { value: '' }, 'o tomar de un material del modelo…'), mats.map(m => el('option', { value: m }, m)));
  const deSec = el('select', { onchange: e => { const b = blk('SECCIONES'), f = b.filas.find(x => get(b, x, 'id') === e.target.value); if (!f) return;
      const g = c => { const v = get(b, f, c) || deBiblioteca(b, f, c); return v != null && v !== '' ? v : null; };
      if (g('a') != null) campos.A.value = String(g('a'));
      const ii = [g('iy'), g('iz')].filter(v => v != null).map(Number).filter(isFinite); if (ii.length) campos.I.value = String(Math.min(...ii));       // eje débil
      calc(); } },
    el('option', { value: '' }, 'o tomar de una sección del modelo…'), secs.map(m => el('option', { value: m }, m)));
  calc();
  const destino = cel ? `fila ${b0.filas.indexOf(cel.f) + 1}${colDest ? ' · ' + ((kCols.find(c => c.n === colDest) || {}).et || colDest) : ''}` : 'una fila nueva';
  modal(el('div', { class: 'caja' }, el('h3', {}, 'Rigidez y pandeo de una barra: k = E·A/L'),
    el('div', { class: 'cuerpo' },
      el('p', { class: 'nota' }, `Se puede escribir con unidad («210 GPa», «5 cm2», «2 m»); se pasa a ${uF}, ${uL}.  Fuentes: Gere & Goodno, cap. 2 (rigidez axial) y tabla de la cátedra para la carga crítica de Euler.  Vale para una barra recta de sección constante, material elástico y columna esbelta (el programa no verifica el rango de validez de Euler).`),
      el('p', { class: 'nota' }, [el('b', {}, 'Se escribe en: '), destino, cel ? '' : '  (tocá antes una celda de k de la tabla para elegir dónde)']),
      fila('E', 'Módulo de elasticidad', campos.E), deMat, fila('A', 'Área de la sección', campos.A), fila('I', 'Momento de inercia del eje débil (para la carga crítica)', campos.I), deSec,
      fila('L', 'Longitud de la barra', campos.L), fila('Extremos', 'Condición de extremos para el pandeo', campos.X), salida, colSel ? fila('Poner k en', 'Columna donde se escribe k', colSel) : null),
    el('div', { class: 'pie' }, el('button', { onclick: cerrarModal }, 'Cancelar'),
      el('button', { class: 'principal', onclick: () => {
        if (R.k == null) return;
        const col = colSel ? colSel.value : (colDest || 'k'), valores = { [col]: fmt(R.k) }; if (R.pc != null) valores.pc = fmt(R.pc);
        if (filaDest) mut(() => { for (const [c, v] of Object.entries(valores)) set(b0, filaDest, c, v); }); else agregarFila(valores);
        cerrarModal(); renderTabla(); renderInspector(); } }, cel ? 'Escribir en la celda' : 'Agregar fila con estos valores'))));
}
function avisoBiblioteca(sp) {                 // si no se encuentra el archivo, se dice dónde se lo busca y qué hacer
  const per = sp.t === 'SECCIONES';
  if (!(per || sp.t === 'MATERIALES') || (per ? S.bib.perfiles : S.bib.materiales).length) return null;
  const ruta = (per ? S.bib.archivo_perfiles : S.bib.archivo_materiales) || `006_Biblioteca/${per ? 'perfiles' : 'materiales'}.csv`;
  const existe = per ? S.bib.existe_perfiles : S.bib.existe_materiales;
  return el('div', { class: 'aviso-bib' }, existe === false ? `No se encontró la biblioteca de ${per ? 'perfiles' : 'materiales'}.` : `La biblioteca de ${per ? 'perfiles' : 'materiales'} está vacía.`,
    ' Se busca en: ', el('code', {}, ruta), '.  La carpeta ', el('code', {}, '006_Biblioteca'), ' viene con el programa; si la moviste, restituila y reiniciá el editor.');
}
function opcionesPerfiles(lista) {              // desplegable agrupado por familia (IPN, IPE, W, tubos...)
  const grupos = new Map(); lista.forEach(m => { if (!grupos.has(m.f)) grupos.set(m.f, []); grupos.get(m.f).push(m); });
  return [...grupos].map(([f, ms]) => el('optgroup', { label: NOMBRE_FAMILIA[f] || f }, ms.map(m => el('option', { value: m.n }, `${m.n}: ${m.nm || m.t}`))));
}
const NOMBRE_FAMILIA = { IPN: 'Doble T · IPN', IPB: 'Doble T · IPB', IPBl: 'Doble T · IPBl', IPBv: 'Doble T · IPBv', IPE: 'Doble T · IPE', W: 'Doble T · W (ala ancha)', HP: 'Doble T · HP', M: 'Doble T · M',
  UPN: 'Canal · UPN', C: 'Canal · C (americano)', MC: 'Canal · MC (americano)', L: 'Ángulos L', T: 'Tes T', TC: 'Tubo circular (TC)', TQ: 'Tubo cuadrado (TQ)', TR: 'Tubo rectangular (TR)' };
function idPerfil(n) {                          // nombre en el modelo = designación del perfil (único)
  const m = S.bib.perfiles.find(x => x.n === n); const base = m ? m.t : 'perfil'; const usados = new Set(ids('SECCIONES', 'id'));
  let id = base, k = 2; while (usados.has(id)) id = `${base} (${k++})`; return id;
}
function selectorBiblioteca(sp) {              // «+ Agregar material de la biblioteca»: una fila lista con solo elegirlo
  if (sp.t === 'SECCIONES' && S.bib.perfiles.length) {
    return el('select', { class: 'agregar-lib', title: 'Agrega una sección con el perfil elegido; A, I, J... salen de la biblioteca (tablas CIRSOC).',
      onchange: e => { const n = e.target.value; if (!n) return; agregarFila({ id: idPerfil(n), tipo: 'perfil', lib: n }); e.target.value = ''; } },
      el('option', { value: '' }, '+ Agregar perfil de la biblioteca…'), opcionesPerfiles(S.bib.perfiles));
  }
  const lista = sp.t === 'ELECTRODOS' ? S.bib.electrodos : sp.t === 'MATERIALES' ? S.bib.materiales : null;
  if (!lista || !lista.length) return null;
  const sel = el('select', { class: 'agregar-lib', title: 'Agrega una fila con el material elegido; sus valores (E, G, ν, σy, ρ...) salen de la biblioteca.',
    onchange: e => { const n = e.target.value; if (!n) return; const m = lista.find(x => x.n === n);
      agregarFila(sp.t === 'ELECTRODOS' ? { id: m.t, lib: n } : { id: siguienteId('MATERIALES'), lib: n }); e.target.value = ''; } },
    el('option', { value: '' }, sp.t === 'ELECTRODOS' ? '+ Agregar electrodo de la biblioteca…' : '+ Agregar material de la biblioteca…'), lista.map(m => el('option', { value: m.n }, `${m.n}: ${m.t}`)));
  return sel;
}
function celdaTipoApoyo(b, f) {
  const g = esq().geo.apoyos, flags = g.filter(c => esSi(get(b, f, c))), P = presetsApoyo();
  const sel = el('select', { onchange: e => { const i = +e.target.value; if (i < 0) return; const fl = P[i][1]; mut(() => g.forEach(c => set(b, f, c, fl.includes(c) ? '1' : ''))); renderTabla(); renderInspector(); } },
    el('option', { value: -1 }, nombreApoyo(flags)), P.map(([n], i) => el('option', { value: i }, n)));
  return el('td', {}, sel);
}
function renderClaves(wrap, sp) {
  const b = blk('PROYECTO', true); const form = el('div', { class: 'form' });
  const conocidas = new Set(sp.cols.map(c => c.n));
  const campo = (c, v, extra) => {
    let inp;
    if (c.n === 'peso_propio') {                 // casilla + nombre del caso; el CSV sigue guardando solo el nombre (vacío = sin peso propio)
      const on = !!v;
      const chk = el('input', { type: 'checkbox', checked: on, title: 'Incluir el peso propio de todas las barras (usa rho del material)',
        onchange: e => { mut(() => setP('peso_propio', e.target.checked ? (S.ppUlt || 'PESO PROPIO') : '')); } });
      const nom = on ? el('input', { type: 'text', value: v, placeholder: 'Nombre del caso', title: 'Nombre del caso de carga del peso propio', autocomplete: 'off', spellcheck: 'false',
        oninput: e => { if (S.pend == null) S.pend = snap(); S.ppUlt = e.target.value; setP(c.n, e.target.value); S.sucio = true; renderArchivo(); programarRevision(); renderBotones(); },
        onchange: () => { cerrarPend(); cambio(); } }) : null;
      if (on) S.ppUlt = v;
      inp = el('span', { class: 'con-u', style: 'gap:8px' }, chk, nom);
      form.append(el('label', { title: c.ay }, 'Incluir peso propio', el('small', {}, 'Suma el peso de todas las barras como un caso de carga (usa rho del material)'), el('small', { class: 'cl' }, c.n)), inp);
      return;
    }
    if (c.n === 'gravedad' && !getP('peso_propio')) {
      form.append(el('label', { title: c.ay }, c.et || c.n, el('small', {}, 'Se usa solo con el peso propio'), el('small', { class: 'cl' }, c.n)), el('span', { class: 'fijo' }, '— (sin peso propio)'));
      return;
    }
    if (c.t === 'opc' && !c.fijo) {
      inp = el('select', { onchange: e => { mut(() => setP(c.n, e.target.value)); } }, el('option', { value: '' }, c.d ? `(por defecto: ${nombreOpc(c, c.d)})` : ''), opcionesCon(c, v).map(o => el('option', { value: o }, nombreOpc(c, o))));
      inp.value = opcionesCon(c, v).find(o => low(o) === low(v)) || '';
    } else if (c.fijo) {
      inp = el('span', { class: 'fijo' }, nombreOpc(c, v || c.d));
    } else {
      inp = el('input', { type: 'text', value: v, placeholder: c.d || '', list: c.t === 'ref:casos' ? 'dl-casos' : null, autocomplete: 'off', spellcheck: 'false',
        oninput: e => { if (S.pend == null) S.pend = snap(); setP(c.n, e.target.value); S.sucio = true; renderArchivo(); programarRevision(); renderBotones(); },
        onchange: () => { cerrarPend(); cambio(); } });
    }
    form.append(el('label', { title: c.ay }, c.et || c.n, el('small', {}, c.ay || ''), c.et ? el('small', { class: 'cl' }, c.n) : null), inp);
  };
  sp.cols.forEach(c => campo(c, c.fijo ? getP(c.n) || S.doc.tipo : getP(c.n)));
  b.filas.forEach(f => { if (!conocidas.has(low(f.c[0]))) campo({ n: f.c[0], t: 'txt', ay: 'Clave que el programa no usa (se conserva en el archivo)' }, String(f.c[1] || '')); });
  wrap.append(form);
}
function filaSeleccionada(t, b, f) {
  if (!S.sel) return false;
  if (t === 'NODOS') return S.sel.k === 'nodo' && get(b, f, 'id') === S.sel.id;
  if (t === 'BARRAS') return S.sel.k === 'barra' && get(b, f, 'id') === S.sel.id;
  if (ci(b, 'nodo') >= 0 && S.sel.k === 'nodo') return get(b, f, 'nodo') === S.sel.id;
  if (ci(b, 'barra') >= 0 && S.sel.k === 'barra') return get(b, f, 'barra') === S.sel.id;
  return false;
}
function seleccionarDesdeFila(b, f) {
  let s = null;
  if (b.t === 'NODOS') s = { k: 'nodo', id: get(b, f, 'id') };
  else if (b.t === 'BARRAS') s = { k: 'barra', id: get(b, f, 'id') };
  else if (ci(b, 'nodo') >= 0 && get(b, f, 'nodo')) s = { k: 'nodo', id: get(b, f, 'nodo') };
  else if (ci(b, 'barra') >= 0 && get(b, f, 'barra')) s = { k: 'barra', id: get(b, f, 'barra') };
  seleccionar(s, true);
}
function seleccionar(s, desdeTabla) {
  S.sel = s && s.id !== '' ? s : null;
  document.querySelectorAll('#tabla-wrap tr[data-fila]').forEach(tr => {
    const b = blk(S.bloque); const f = b.filas[+tr.dataset.fila];
    tr.classList.toggle('sel', !!f && filaSeleccionada(S.bloque, b, f));
  });
  if (!desdeTabla) { const tr = $('#tabla-wrap tr.sel'); if (tr) tr.scrollIntoView({ block: 'nearest' }); }
  renderInspector(); if (window.V) V.dibujar();
}
function agregarFila(valores) {
  const sp = spec(S.bloque);
  mut(() => {
    const b = blk(sp.t, true); const f = filaVacia(b);
    for (const [k, v] of Object.entries(valores || {})) set(b, f, k, v);
    if (!valores) { if (sp.cols.some(c => c.n === 'id') && !get(b, f, 'id')) set(b, f, 'id', siguienteId(sp.t)); }
    b.filas.push(f);
  });
  renderTabla(); const u = $('#tabla-wrap tbody tr:last-child input'); if (u) u.focus();
}
function duplicarFila(b, r) {
  mut(() => { const f = JSON.parse(JSON.stringify(b.filas[r])); f.n = []; if (ci(b, 'id') >= 0) set(b, f, 'id', siguienteId(b.t)); b.filas.splice(r + 1, 0, f); });
  renderTabla();
}
function borrarFilaUI(b, r) {
  const f = b.filas[r]; const id = get(b, f, 'id');
  if ((b.t === 'NODOS' || b.t === 'BARRAS') && id) return borrarElemento(b.t === 'NODOS' ? 'nodo' : 'barra', id);
  mut(() => b.filas.splice(r, 1)); renderTabla(); renderInspector();
}
function siguienteId(t) {
  const ex = ids(t, 'id'); const todosNum = ex.every(x => /^\d+$/.test(x));
  if (todosNum) return String(Math.max(0, ...ex.map(Number)) + 1);
  const pref = { NODOS: 'N', BARRAS: 'B', MATERIALES: 'M', SECCIONES: 'S', SOLDADURAS: 'W', ELECTRODOS: 'E' }[t] || 'X';
  let n = ex.length + 1; while (ex.includes(pref + n)) n++;
  return pref + n;
}
function pegar(e, b, sp) {
  const txt = (e.clipboardData || window.clipboardData).getData('text');
  if (!/[\t\n]/.test(txt.replace(/\n$/, ''))) return;
  e.preventDefault();
  const r0 = +e.target.dataset.r, c0 = +e.target.dataset.c; const cols = colsMostradas(b, sp);
  const filasTxt = txt.replace(/\r/g, '').replace(/\n$/, '').split('\n').map(l => l.split('\t'));
  mut(() => {
    filasTxt.forEach((cs, i) => {
      while (b.filas.length <= r0 + i) b.filas.push(filaVacia(b));
      cs.forEach((v, j) => { const c = cols[c0 + j]; if (c && c.t !== 'flag') set(b, b.filas[r0 + i], c.n, v.trim()); else if (c) set(b, b.filas[r0 + i], c.n, /^(1|si|sí|x|true)$/i.test(v.trim()) ? '1' : ''); });
    });
  });
  renderTabla();
}

/* ------------------------------------------------------------------ operaciones sobre el modelo (las usan el dibujo y el inspector) */
function borrarElemento(k, id) {
  const refs = [];
  const cuenta = (t, col, v) => filas(t).filter(f => get(blk(t), f, col) === v).length;
  let nref = 0;
  if (k === 'nodo') {
    nref = cuenta('BARRAS', 'nodo_i', id) + cuenta('BARRAS', 'nodo_j', id);
    for (const t of ['APOYOS', 'RESORTES', 'RESORTES INCLINADOS', 'RESORTES GIRO INCLINADO', 'CARGAS', 'DESPLAZAMIENTOS PREFIJADOS', 'DESAJUSTE DE RESORTES']) if (blk(t)) nref += cuenta(t, 'nodo', id);
  } else {
    for (const t of ['CARGAS EN BARRAS', 'SOLDADURAS', 'PUNTOS DE TENSION']) if (blk(t)) nref += cuenta(t, 'barra', id);
  }
  if (nref && !confirm(`${k === 'nodo' ? 'El nodo' : 'La barra'} ${id} tiene ${nref} elemento(s) asociado(s) (barras, apoyos, cargas...).  ¿Borrarlos también?`)) return;
  mut(() => {
    const quitar = (t, pred) => { const b = blk(t); if (b) b.filas = b.filas.filter(f => !pred(b, f)); };
    if (k === 'nodo') {
      const barrasQuitadas = filas('BARRAS').filter(f => [get(blk('BARRAS'), f, 'nodo_i'), get(blk('BARRAS'), f, 'nodo_j')].includes(id)).map(f => get(blk('BARRAS'), f, 'id'));
      quitar('BARRAS', (b, f) => barrasQuitadas.includes(get(b, f, 'id')));
      for (const t of ['CARGAS EN BARRAS', 'SOLDADURAS', 'PUNTOS DE TENSION']) quitar(t, (b, f) => barrasQuitadas.includes(get(b, f, 'barra')));
      for (const t of ['APOYOS', 'RESORTES', 'RESORTES INCLINADOS', 'RESORTES GIRO INCLINADO', 'CARGAS', 'DESPLAZAMIENTOS PREFIJADOS', 'DESAJUSTE DE RESORTES']) quitar(t, (b, f) => get(b, f, 'nodo') === id);
      quitar('NODOS', (b, f) => get(b, f, 'id') === id);
    } else {
      for (const t of ['CARGAS EN BARRAS', 'SOLDADURAS', 'PUNTOS DE TENSION']) quitar(t, (b, f) => get(b, f, 'barra') === id);
      quitar('BARRAS', (b, f) => get(b, f, 'id') === id);
    }
  });
  if (S.sel && S.sel.id === id && S.sel.k === k) S.sel = null;
  renderTabla(); renderInspector();
}
function nodoEn(coords) {                       // nodo ya existente en ese punto (misma posición), o null
  const b = blk('NODOS'); if (!b) return null; const ej = esq().ejes;
  const nd = b.filas.map(f => ({ id: get(b, f, 'id'), p: ej.map(e => num(get(b, f, e)) || 0) }));
  const tol = 1e-6 * Math.max(1, ...nd.flatMap(n => n.p.map(Math.abs)));
  const q = ej.map((e, i) => coords[i] == null ? 0 : coords[i]);
  const h = nd.find(n => n.p.every((v, i) => Math.abs(v - q[i]) <= tol)); return h ? h.id : null;
}
function nodosDuplicados() {                    // grupos de nodos que están en el mismo punto
  const b = blk('NODOS'); if (!b) return []; const ej = esq().ejes; const g = new Map();
  b.filas.forEach(f => { const id = get(b, f, 'id'); const k = ej.map(e => num(get(b, f, e)) || 0).map(v => +v.toPrecision(9)).join('|'); if (!g.has(k)) g.set(k, []); g.get(k).push(id); });
  return [...g.values()].filter(x => x.length > 1);
}
function unirNodos(grupo) {                     // deja el primero y reasigna todo lo que usaba a los demás
  mut(() => {
    const [quedan, ...otros] = grupo;
    otros.forEach(o => { propagarRenombre('nodos', o, quedan); const b = blk('NODOS'); const i = b.filas.findIndex(f => get(b, f, 'id') === o); if (i >= 0) b.filas.splice(i, 1); });
    // una barra de un nodo a sí mismo, o dos apoyos / resortes iguales en el mismo nodo, no tienen sentido
    const bb = blk('BARRAS'); if (bb) bb.filas = bb.filas.filter(f => get(bb, f, 'nodo_i') !== get(bb, f, 'nodo_j'));
    for (const t of ['APOYOS', 'RESORTES']) { const b = blk(t); if (!b) continue; const vistos = new Set(); b.filas = b.filas.filter(f => { const n = get(b, f, 'nodo'); if (vistos.has(n)) return false; vistos.add(n); return true; }); }
  });
  renderTodo();
}
function crearNodo(coords) {
  const ya = nodoEn(coords); if (ya) { aviso(`Ya hay un nodo (${ya}) en ese punto: se usa ese.`); return ya; }
  let id;
  mut(() => {
    const b = blk('NODOS', true); const f = filaVacia(b); id = siguienteId('NODOS'); set(b, f, 'id', id);
    esq().ejes.forEach((e, i) => set(b, f, e, fmt(coords[i] == null ? 0 : coords[i]))); b.filas.push(f);
  });
  if (S.bloque === 'NODOS') renderTabla();
  return id;
}
function moverNodo(id, coords, sinHistorial) {
  const b = blk('NODOS'); const f = b.filas.find(x => get(b, x, 'id') === id); if (!f) return;
  esq().ejes.forEach((e, i) => { if (coords[i] != null) set(b, f, e, fmt(coords[i])); });
}
function crearBarra(i, j) {
  if (i === j) return null;
  const bb = blk('BARRAS');
  if (bb && bb.filas.some(f => (get(bb, f, 'nodo_i') === i && get(bb, f, 'nodo_j') === j) || (get(bb, f, 'nodo_i') === j && get(bb, f, 'nodo_j') === i))) { aviso('Ya existe una barra entre esos dos nodos.'); return null; }
  const u = bb && bb.filas.length ? bb.filas[bb.filas.length - 1] : null;
  const mat = u ? get(bb, u, 'material') : (ids('MATERIALES', 'id')[0] || ''), sec = u ? get(bb, u, 'seccion') : (ids('SECCIONES', 'id')[0] || '');
  let id;
  mut(() => {
    const b = blk('BARRAS', true); const f = filaVacia(b); id = siguienteId('BARRAS');
    set(b, f, 'id', id); set(b, f, 'nodo_i', i); set(b, f, 'nodo_j', j); set(b, f, 'material', mat); set(b, f, 'seccion', sec); b.filas.push(f);
  });
  if (!mat || !sec) aviso('Falta definir un material y una sección (bloques MATERIALES y SECCIONES) para completar la barra ' + id + '.');
  if (S.bloque === 'BARRAS') renderTabla();
  return id;
}
function aviso(t) { S.msg = t; renderEstado(); }
function filaPorNodo(t, nodo, caso) {
  const b = blk(t); return b ? b.filas.find(f => get(b, f, 'nodo') === nodo && (caso == null || get(b, f, 'caso') === caso)) : null;
}
function fijarApoyo(nodo, flags) {           // flags: lista de columnas restringidas ([] = quitar el apoyo)
  mut(() => {
    const b = blk('APOYOS', true); let f = filaPorNodo('APOYOS', nodo);
    if (!flags.length) { if (f) b.filas.splice(b.filas.indexOf(f), 1); return; }
    if (!f) { f = filaVacia(b); set(b, f, 'nodo', nodo); b.filas.push(f); }
    for (const c of esq().geo.apoyos) set(b, f, c, flags.includes(c) ? '1' : '');
  });
  if (S.bloque === 'APOYOS') renderTabla();
}
function apoyoDe(nodo) { const f = filaPorNodo('APOYOS', nodo); const b = blk('APOYOS'); return f ? esq().geo.apoyos.filter(c => ['1', 'si', 'sí', 's', 'x', 'true', 'yes'].includes(low(get(b, f, c)))) : []; }
function nombreApoyo(flags) {
  if (!flags.length) return 'Sin apoyo';
  const p = presetsApoyo().find(([, fl]) => fl.length === flags.length && fl.every(x => flags.includes(x)));
  return p ? p[0] : 'Personalizado';
}
function presetsApoyo() {
  const t = S.doc.tipo, g = esq().geo.apoyos;
  if (t === 'portico') return [['Empotrado', g], ['Articulado fijo', ['ux', 'uy']], ['Móvil (restringe y)', ['uy']], ['Móvil (restringe x)', ['ux']]];
  if (t === 'reticulado') return [['Articulado fijo', ['ux', 'uy']], ['Móvil (restringe y)', ['uy']], ['Móvil (restringe x)', ['ux']]];
  if (t === 'emparrillado') return [['Empotrado', g], ['Apoyo simple (uz)', ['uz']]];
  if (t === 'portico3d') return [['Empotrado', g], ['Articulado (ux uy uz)', ['ux', 'uy', 'uz']], ['Móvil (uz)', ['uz']]];
  return [];
}
function agregarCargaNodo(nodo, caso, valores) {
  mut(() => {
    const b = blk('CARGAS', true); const f = filaVacia(b); set(b, f, 'caso', caso); set(b, f, 'nodo', nodo);
    for (const [k, v] of Object.entries(valores)) set(b, f, k, v); b.filas.push(f);
  });
  if (S.bloque === 'CARGAS') renderTabla();
}
function agregarCargaBarra(barra, valores) {
  mut(() => {
    const b = blk('CARGAS EN BARRAS', true); const f = filaVacia(b); set(b, f, 'barra', barra);
    for (const [k, v] of Object.entries(valores)) set(b, f, k, v); b.filas.push(f);
  });
  if (S.bloque === 'CARGAS EN BARRAS') renderTabla();
}

/* ------------------------------------------------------------------ inspector (elemento seleccionado) */
function renderInspector() {
  const cont = $('#inspector'); cont.textContent = '';
  if (!S.doc || esq().dim === 0) { cont.append(el('div', { class: 'nota' }, 'Modo rápido de soldaduras: se carga todo en las tablas de arriba.')); return; }
  if (!S.sel) { cont.append(el('div', { class: 'nota' }, 'Elegí un nodo o una barra en el dibujo (o en una tabla) para editar sus datos acá: coordenadas, apoyos, resortes y cargas.')); return; }
  S.sel.k === 'nodo' ? inspNodo(cont, S.sel.id) : inspBarra(cont, S.sel.id);
}
function ligado(b, f, col, label) {   // campo ligado a una celda (para el inspector)
  const c = colDe(b.t, col) || { t: 'txt', n: col, et: col, ay: '' };
  const inp = control(b, f, c, { tabla: false });
  return label === null ? inp : el('label', {}, label || conUnidad(c), inp);
}
function inspNodo(cont, id) {
  const b = blk('NODOS'); const f = b && b.filas.find(x => get(b, x, 'id') === id); if (!f) return;
  cont.append(el('h3', {}, 'Nodo ' + id));
  const dim = esq().dim;
  cont.append(el('div', { class: 'campos' }, esq().ejes.map(e => ligado(b, f, e)), el('button', { class: 'chico', onclick: () => borrarElemento('nodo', id) }, 'Borrar nodo')));
  // apoyo
  const flags = apoyoDe(id);
  cont.append(el('div', { class: 'sub' }, 'Apoyo  ', el('small', { class: 'nota' }, 'Fijo = ese desplazamiento o giro vale 0 · Libre = se mueve')));
  const g = esq().geo.apoyos;
  cont.append(el('div', { class: 'campos' }, g.map(c => el('label', { title: colDe('APOYOS', c).ay }, colDe('APOYOS', c).et,
    el('button', { type: 'button', class: 'apoyo ' + (flags.includes(c) ? 'fijo' : 'libre'),
      onclick: () => { const n = new Set(apoyoDe(id)); n.has(c) ? n.delete(c) : n.add(c); fijarApoyo(id, g.filter(x => n.has(x))); renderInspector(); } }, flags.includes(c) ? 'Fijo' : 'Libre'))),
    el('label', {}, 'Tipo', el('select', { onchange: e => { const i = +e.target.value; if (i >= 0) { fijarApoyo(id, i < presetsApoyo().length ? presetsApoyo()[i][1] : []); renderInspector(); } } },
      el('option', { value: -1 }, nombreApoyo(flags)), presetsApoyo().map(([n], i) => el('option', { value: i }, n)), el('option', { value: presetsApoyo().length }, 'Sin apoyo')))));
  // resorte
  const rb = blk('RESORTES'); const rf = rb && rb.filas.find(x => get(rb, x, 'nodo') === id);
  if (spec('RESORTES')) {
    cont.append(el('div', { class: 'sub' }, 'Resorte (apoyo elástico)'));
    if (rf) cont.append(el('div', { class: 'campos' }, esq().geo.resortes.map(c => ligado(rb, rf, c)), el('button', { class: 'chico', onclick: () => { mut(() => rb.filas.splice(rb.filas.indexOf(rf), 1)); renderInspector(); } }, 'Quitar')));
    else cont.append(el('div', { class: 'campos' }, el('button', { class: 'chico', onclick: () => { mut(() => { const bb = blk('RESORTES', true); const ff = filaVacia(bb); set(bb, ff, 'nodo', id); bb.filas.push(ff); }); renderInspector(); } }, '+ Resorte')));
  }
  // cargas
  cont.append(el('div', { class: 'sub' }, 'Cargas en el nodo'));
  const cb = blk('CARGAS'); const lista = cb ? cb.filas.filter(x => get(cb, x, 'nodo') === id) : [];
  if (lista.length) {
    const tb = el('table', {}, el('tr', {}, el('th', {}, etq('CARGAS', 'caso')), esq().geo.cargas.map(c => el('th', { title: colDe('CARGAS', c).ay }, conUnidad(colDe('CARGAS', c)))), el('th', {})));
    lista.forEach(x => tb.append(el('tr', {}, el('td', {}, ligado(cb, x, 'caso', null)), esq().geo.cargas.map(c => el('td', {}, ligado(cb, x, c, null))),
      el('td', {}, el('button', { class: 'chico', onclick: () => { mut(() => cb.filas.splice(cb.filas.indexOf(x), 1)); renderInspector(); } }, '✕')))));
    cont.append(tb);
  }
  cont.append(el('div', { class: 'campos' }, el('button', { class: 'chico', onclick: () => { agregarCargaNodo(id, casos()[0] || 'C1', {}); renderInspector(); } }, '+ Carga')));
}
function inspBarra(cont, id) {
  const b = blk('BARRAS'); const f = b && b.filas.find(x => get(b, x, 'id') === id); if (!f) return;
  cont.append(el('h3', {}, 'Barra ' + id));
  const camposB = ['nodo_i', 'nodo_j', 'material', 'seccion', 'art_i', 'art_j', 'pandeo'].filter(c => ci(b, c) >= 0 || spec('BARRAS').cols.some(x => x.n === c));
  cont.append(el('div', { class: 'campos' }, camposB.map(c => ligado(b, f, c)), el('button', { class: 'chico', onclick: () => borrarElemento('barra', id) }, 'Borrar barra')));
  if (window.V) { const L = V.longitud(id); if (L != null) cont.append(el('div', { class: 'nota' }, 'Longitud: ' + fmt(L) + ' ' + (getP('unidad_longitud') || 'mm'))); }
  cont.append(el('div', { class: 'sub' }, 'Cargas en el tramo'));
  const cb = blk('CARGAS EN BARRAS'); const cols = spec('CARGAS EN BARRAS').cols.filter(c => c.n !== 'barra');
  const lista = cb ? cb.filas.filter(x => get(cb, x, 'barra') === id) : [];
  if (lista.length) {
    const tb = el('table', {}, el('tr', {}, cols.map(c => el('th', { title: c.ay }, c.et)), el('th', {})));
    lista.forEach(x => tb.append(el('tr', {}, cols.map(c => el('td', {}, ligado(cb, x, c.n, null))),
      el('td', {}, el('button', { class: 'chico', onclick: () => { mut(() => cb.filas.splice(cb.filas.indexOf(x), 1)); renderInspector(); } }, '✕')))));
    cont.append(tb);
  }
  cont.append(el('div', { class: 'campos' }, el('button', { class: 'chico', onclick: () => { agregarCargaBarra(id, { caso: casos()[0] || 'C1', tipo: spec('CARGAS EN BARRAS').cols.find(c => c.n === 'tipo').op[0] }); renderInspector(); } }, '+ Carga en el tramo')));
  const sol = blk('SOLDADURAS') ? blk('SOLDADURAS').filas.filter(x => get(blk('SOLDADURAS'), x, 'barra') === id).map(x => get(blk('SOLDADURAS'), x, 'id')) : [];
  if (sol.length) cont.append(el('div', { class: 'nota' }, 'Soldaduras en esta barra: ' + sol.join(', ')));
}

/* ------------------------------------------------------------------ barra superior y estado */
function renderArchivo() {
  $('#archivo').replaceChildren(el('b', {}, S.nombre), S.sucio ? ' ●' : '', S.doc ? '  ·  ' + esq().nombre : '');
}
function renderBotones() {
  $('#b-deshacer').disabled = !S.undo.length && S.pend == null; $('#b-rehacer').disabled = !S.redo.length;
}
function renderEstado() {
  const ln = $('#estado-linea'); ln.textContent = '';
  const r = S.rev;
  if (!r) ln.append(el('span', { class: 'chip n' }, 'Sin revisar'));
  else if (r.ok) { ln.append(el('span', { class: 'chip ok' }, '✔ Modelo válido')); const nt = r.avisos.filter(a => a.startsWith('Nota: ')), av = r.avisos.length - nt.length; if (av) ln.append(el('span', { class: 'chip av' }, av + ' aviso(s)')); if (nt.length) ln.append(el('span', { class: 'chip n', title: 'Informativo: no es un error' }, nt.length + ' nota(s)')); }
  else ln.append(el('span', { class: 'chip mal' }, '✖ ' + (r.bloque ? r.bloque + (r.fila >= 0 ? ', fila ' + (r.fila + 1) : '') + ': ' : '') + r.error.split('\n')[0].slice(0, 160)));
  if (S.msg) ln.append(el('span', { class: 'chip av' }, S.msg));
  if (S.doc && esq().dim) for (const g of nodosDuplicados().slice(0, 3))
    ln.append(el('span', { class: 'chip av' }, `Nodos ${g.join(' y ')} en el mismo punto `, el('button', { class: 'chico', onclick: ev => { ev.stopPropagation(); unirNodos(g); } }, 'Unir')));
  if (S.guardado) ln.append(el('span', { class: 'chip ok', title: S.guardado.ruta }, 'Guardado en ' + (S.guardado.equipo && S.guardado.equipo.ruta_windows || S.guardado.ruta), ' ',
    el('button', { class: 'chico', onclick: ev => { ev.stopPropagation(); abrirCarpeta(S.guardado.ruta); } }, 'Abrir carpeta')));
  if (S.doc && esq().dim) {
    const nn = filas('NODOS').length, nb = filas('BARRAS').length;
    ln.append(el('span', { class: 'chip n', style: 'margin-left:auto' }, `${nn} nodos · ${nb} barras · ${casos().length} caso(s)`));
  }
  ln.append(el('span', { class: 'chip n' }, S.detalle ? '▾ ocultar detalle' : '▸ detalle'));
  const det = $('#estado-detalle'); det.textContent = '';
  if (S.detalle) {
    if (r && !r.ok) det.append(el('div', { class: 'err' }, r.error + '\n'));
    if (r && r.avisos.length) { const av = r.avisos.filter(a => !a.startsWith('Nota: ')), nt = r.avisos.filter(a => a.startsWith('Nota: '));
      if (av.length) det.append(el('div', { class: 'av' }, av.map(a => 'Aviso: ' + a).join('\n') + '\n')); if (nt.length) det.append(el('div', { class: 'nt' }, nt.join('\n') + '\n')); }
    if (S.calc) {
      det.append(el('div', {}, '\n— Último cálculo (' + S.calc.nombre + ') —\n' + S.calc.texto));
      if (S.calc.informe) det.append(el('a', { href: S.calc.informe, target: '_blank' }, 'Abrir el informe'));
    }
  }
}
$('#estado-linea').addEventListener('click', () => { S.detalle = !S.detalle; renderEstado(); });

let _timer = null, _seq = 0;
function programarRevision() { clearTimeout(_timer); _timer = setTimeout(revisar, 600); }
async function revisar() {
  clearTimeout(_timer); if (!S.doc) return; const n = ++_seq;
  try {
    const r = await api('revisar', { doc: S.doc });
    if (n !== _seq) return;
    S.rev = r; S.msg = null; renderEstado(); marcarErrores();
  } catch (e) { if (n === _seq) { S.rev = { ok: false, error: String(e.message || e), avisos: [] }; renderEstado(); } }
  return S.rev;
}
function marcarErrores() {
  document.querySelectorAll('#tabla-wrap tr[data-fila]').forEach(tr => tr.classList.toggle('err', errFila(S.bloque, +tr.dataset.fila)));
  if (S.rev && !S.rev.ok && S.rev.bloque && S.rev.fila >= 0) { /* el estado ofrece saltar al error */ }
}

/* ------------------------------------------------------------------ archivos */
function modal(contenido) { const m = $('#modal'); m.textContent = ''; m.append(contenido); m.hidden = false; }
function cerrarModal() { $('#modal').hidden = true; $('#modal').textContent = ''; }
function confirmarDescartar() { return !S.sucio || confirm('Hay cambios sin guardar.  ¿Descartarlos?'); }

function dialogoArchivo(modo) {
  return new Promise(resolve => {
    let ruta = S.ruta ? S.ruta.replace(/[\\/][^\\/]*$/, '') : (CFG.inicial ? CFG.inicial.ruta.replace(/[\\/][^\\/]*$/, '') : null);
    let sel = '';
    const inpRuta = el('input', { type: 'text', spellcheck: 'false' }), inpNombre = el('input', { type: 'text', spellcheck: 'false', value: modo === 'guardar' ? (S.ruta ? S.nombre : 'modelo.csv') : '' });
    const lista = el('div', { class: 'lista' }), raices = el('div', { class: 'raices' }), msg = el('div', { class: 'nota' });
    const ok = el('button', { class: 'principal' }, modo === 'abrir' ? 'Abrir' : 'Guardar');
    const cerrar = v => { cerrarModal(); resolve(v); };
    async function ir(r) {
      try {
        const j = await api('listar', { ruta: r }); ruta = j.ruta; inpRuta.value = j.ruta; msg.textContent = '';
        raices.replaceChildren(...j.raices.map(x => el('div', { class: 'it', onclick: () => ir(x.r) }, x.n)));
        lista.replaceChildren(...(j.padre ? [el('div', { class: 'it', onclick: () => ir(j.padre) }, '↰  ..')] : []),
          ...j.dirs.map(d => el('div', { class: 'it', onclick: () => ir(sep(j.ruta) + d) }, '📁 ' + d)),
          ...j.archivos.map(a => el('div', { class: 'it' + (a === sel ? ' sel' : ''), onclick: ev => { sel = a; if (modo === 'guardar') inpNombre.value = a; [...lista.children].forEach(c => c.classList.remove('sel')); ev.currentTarget.classList.add('sel'); }, ondblclick: aceptar }, '📄 ' + a)));
      } catch (e) { msg.textContent = e.message; }
    }
    const sep = r => r.endsWith('/') || r.endsWith('\\') ? r : r + (r.includes('\\') && !r.includes('/') ? '\\' : '/');
    async function aceptar() {
      const nombre = modo === 'abrir' ? sel : inpNombre.value.trim();
      if (!nombre) { msg.textContent = modo === 'abrir' ? 'Elegí un archivo de la lista.' : 'Escribí el nombre del archivo.'; return; }
      const completa = sep(ruta) + nombre;
      if (modo === 'guardar') {
        const e = await api('existe', { ruta: completa });
        if (e.existe && e.ruta !== S.ruta && !confirm(`Ya existe ${e.ruta}.  ¿Reemplazarlo?`)) return;
        return cerrar(e.ruta);
      }
      cerrar(completa);
    }
    ok.onclick = aceptar;
    inpRuta.addEventListener('keydown', e => { if (e.key === 'Enter') ir(inpRuta.value); });
    inpNombre.addEventListener('keydown', e => { if (e.key === 'Enter') aceptar(); });
    modal(el('div', { class: 'caja explorador' }, el('h3', {}, modo === 'abrir' ? 'Abrir modelo' : 'Guardar como'),
      el('div', { class: 'cuerpo' }, el('div', { class: 'ruta' }, el('button', { onclick: () => ir(inpRuta.value) }, 'Ir'), inpRuta),
        el('div', { class: 'cols' }, raices, lista),
        modo === 'guardar' ? el('div', { class: 'nombre' }, 'Nombre:', inpNombre) : null, msg),
      el('div', { class: 'pie' }, el('button', { onclick: () => cerrar(null) }, 'Cancelar'), ok)));
    ir(ruta);
  });
}
function cargarDoc(j) {
  S.doc = j.doc; S.ruta = j.ruta; S.nombre = j.nombre; S.sucio = false; S.undo = []; S.redo = []; S.pend = null; S.sel = null; S.rev = null; S.calc = null; S.msg = null;
  S.guardado = null; S.dec = detectarDec(); S.bloque = 'PROYECTO'; S.tool = 'sel';
  actualizarListas(); renderTodo(); if (window.V) V.ajustar(); programarRevision();
}
async function abrir() {
  if (!confirmarDescartar()) return;
  const r = await dialogoArchivo('abrir'); if (!r) return;
  try { cargarDoc(await api('abrir', { ruta: r })); } catch (e) { alert(e.message); }
}
async function nuevo(tipo) {
  if (!confirmarDescartar()) return;
  try { cargarDoc(await api('nuevo', { tipo })); } catch (e) { alert(e.message); }
}
async function abrirCarpeta(ruta) { try { await api('abrir_carpeta', { ruta }); } catch (e) { alert('No pude abrir la carpeta: ' + e.message + '\nLa ruta es: ' + ruta); } }
function avisoGuardado(j) {
  const win = j.equipo && j.equipo.ruta_windows;
  modal(el('div', { class: 'caja' }, el('h3', {}, 'Archivo guardado'),
    el('div', { class: 'cuerpo' }, el('p', {}, 'El archivo quedó escrito en:'), el('p', { class: 'ruta-guardada' }, win || j.ruta),
      win ? el('p', { class: 'nota' }, 'Corre dentro de WSL; en Linux la ruta es ' + j.ruta) : null,
      el('p', { class: 'nota' }, `${j.bytes} bytes · carpeta de resultados al calcular: ${(win || j.ruta).replace(/\.[^.\\/]+$/, '')}_salida`)),
    el('div', { class: 'pie' }, el('button', { onclick: () => { navigator.clipboard && navigator.clipboard.writeText(win || j.ruta); } }, 'Copiar ruta'),
      el('button', { onclick: () => abrirCarpeta(j.ruta) }, 'Abrir carpeta'), el('button', { class: 'principal', onclick: cerrarModal }, 'Aceptar'))));
}
async function guardar(como) {
  if (!S.doc) return false; cerrarPend();
  let ruta = S.ruta; const conDialogo = !ruta || como;
  if (conDialogo) { ruta = await dialogoArchivo('guardar'); if (!ruta) return false; }
  try {
    const j = await api('guardar', { ruta, doc: S.doc }); S.ruta = j.ruta; S.nombre = j.nombre; S.sucio = false; S.msg = null; S.guardado = j;
    renderArchivo(); renderEstado(); if (conDialogo) avisoGuardado(j); return true;
  } catch (e) { alert('No se pudo guardar: ' + e.message); return false; }
}
async function calcular() {
  if (!S.doc) return; cerrarPend();
  if (!S.ruta && !(await guardar(true))) return;
  let w = null; try { w = window.open('', '_blank'); if (w) w.document.write('<p style="font:14px sans-serif">Calculando…</p>'); } catch (e) { w = null; }
  S.msg = 'Calculando…'; renderEstado();
  try {
    const j = await api('calcular', { ruta: S.ruta, doc: S.doc });
    S.calc = j; S.sucio = false; S.msg = null; S.detalle = true; S.guardado = j.guardado || S.guardado;
    if (j.informe && w) w.location = j.informe; else if (w) w.close();
    if (j.rc !== 0) S.msg = 'El cálculo terminó con errores (ver detalle)';
  } catch (e) { S.calc = { nombre: S.nombre, texto: 'ERROR: ' + e.message, informe: null }; S.detalle = true; if (w) w.close(); }
  renderEstado(); renderArchivo();
}
async function salir() {
  if (!confirmarDescartar()) return;
  S.sucio = false; try { await api('salir', {}); } catch (e) { /* ya cerró */ }
  document.body.textContent = 'Editor cerrado.  Podés cerrar esta pestaña.';
}

/* ------------------------------------------------------------------ armado */
function renderTodo() { renderPasos(); renderTabla(); renderInspector(); renderArchivo(); renderEstado(); renderBotones(); if (window.V) { V.herramientas(); V.dibujar(); } }
function menuNuevo(ev) {
  const prev = $('.menu'); if (prev) { prev.remove(); return; }
  const r = ev.currentTarget.getBoundingClientRect();
  const m = el('div', { class: 'menu', style: `left:${r.left}px;top:${r.bottom + 2}px` },
    Object.values(CFG.esquemas).map(e => el('div', { onclick: () => { m.remove(); nuevo(e.tipo); } }, e.nombre, el('small', {}, e.dim === 3 ? 'nodos x, y, z' : e.dim === 2 ? 'nodos x, y' : 'sin geometría'))));
  document.body.append(m);
  setTimeout(() => document.addEventListener('click', function f() { m.remove(); document.removeEventListener('click', f); }, { once: true }), 0);
}
$('#b-nuevo').onclick = menuNuevo; $('#b-abrir').onclick = abrir; $('#b-guardar').onclick = () => guardar(false); $('#b-guardar-como').onclick = () => guardar(true);
$('#b-deshacer').onclick = deshacer; $('#b-rehacer').onclick = rehacer; $('#b-revisar').onclick = () => { S.detalle = true; revisar(); };
$('#b-calcular').onclick = calcular; $('#b-salir').onclick = salir;
window.addEventListener('beforeunload', e => { if (S.sucio) { e.preventDefault(); e.returnValue = ''; } });
(function divisor() {
  const d = $('#divisor'); let x0 = null, w0 = 0;
  d.addEventListener('pointerdown', e => { x0 = e.clientX; w0 = $('#izq').offsetWidth; d.setPointerCapture(e.pointerId); });
  d.addEventListener('pointermove', e => { if (x0 == null) return; S.anchoBase = Math.max(320, Math.min(window.innerWidth - 340, w0 + e.clientX - x0)); $('#izq').style.width = S.anchoBase + 'px'; if (window.V) V.redim(); });
  d.addEventListener('pointerup', () => { x0 = null; });
})();
