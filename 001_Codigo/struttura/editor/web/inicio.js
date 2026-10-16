'use strict';
/* Arranque del editor: atajos de teclado, bibliotecas y archivo inicial. */
window.addEventListener('keydown', ev => {
  const mod = ev.ctrlKey || ev.metaKey;
  if (mod && ev.key.toLowerCase() === 's') { ev.preventDefault(); guardar(ev.shiftKey); }
  else if (mod && ev.key.toLowerCase() === 'o') { ev.preventDefault(); abrir(); }
  else if (mod && ev.key.toLowerCase() === 'z' && !ev.target.closest('input,textarea')) { ev.preventDefault(); ev.shiftKey ? rehacer() : deshacer(); }
  else if (mod && ev.key.toLowerCase() === 'y' && !ev.target.closest('input,textarea')) { ev.preventDefault(); rehacer(); }
  else if (ev.key === 'F5') { ev.preventDefault(); calcular(); }
});
(async function () {
  try { S.bib = await api('bibliotecas', {}); } catch (e) { /* sin bibliotecas */ }
  if (CFG.inicial) cargarDoc(CFG.inicial);
  else inicioVacio();
})();
function inicioVacio() {
  S.doc = null; $('#pasos').textContent = ''; $('#tabla-wrap').textContent = ''; $('#titulo-bloque').textContent = '';
  renderArchivo(); renderEstado(); if (window.V) { V.herramientas(); V.dibujar(); }
  $('#tabla-wrap').append(el('div', { class: 'vacio guia' },
    el('h2', {}, 'Editor de modelos'),
    el('p', {}, 'El editor arma el mismo archivo CSV que ya usa Struttura, pero con tablas guiadas y un dibujo donde se ve lo que se está cargando.  Todo lo que acepta el CSV está acá.'),
    el('ol', {}, el('li', {}, 'Elegí «Nuevo» (el tipo de estructura) o «Abrir» un CSV existente.'),
      el('li', {}, 'Cargá los bloques en orden con la barra de arriba: Proyecto → Nodos → Materiales → Secciones → Barras → Apoyos → Cargas.'),
      el('li', {}, 'En el dibujo se puede crear nodos y barras con el mouse, poner apoyos y cargas, y arrastrar nodos.'),
      el('li', {}, '«Revisar» carga el modelo con el programa y marca errores y avisos; «Calcular» guarda, calcula y abre el informe.')),
    el('p', { class: 'nota' }, 'Atajos: V seleccionar · N nodo · B barra · A apoyo · C carga · L carga en tramo · X borrar · Supr borra lo seleccionado · Ctrl+S guardar · Ctrl+Z deshacer · F5 calcular.')));
}

/* Enter acepta lo escrito: en una tabla pasa a la celda de abajo (como en una planilla); en los demás campos confirma el valor */
document.addEventListener('keydown', ev => {
  const t = ev.target;
  if (ev.key !== 'Enter' || ev.isComposing || !t || t.tagName !== 'INPUT' || t.type !== 'text' || t.closest('#modal')) return;
  ev.preventDefault();
  const r = t.dataset.r, c = t.dataset.c;
  t.blur();                                                  // dispara «change»: confirma el valor
  if (r !== undefined && c !== undefined) {
    const sig = document.querySelector(`#tabla-wrap input[data-r="${+r + (ev.shiftKey ? -1 : 1)}"][data-c="${c}"]`);
    if (sig) { sig.focus(); sig.select(); }
  } else if (typeof aviso === 'function' && t.closest('#herr')) aviso('Valor aceptado: ahora hacé clic en el dibujo.');
});
