"""Secciones plegables de los informes (HTML): clic en un título de sección la pliega o la despliega.
Los <h2> quedan abiertos (salvo los Anexos) y los <h3> cerrados; botones «Expandir todo / Contraer todo».
Al imprimir se abre todo.  Sin JavaScript el informe se ve completo."""

CSS = """
.pleg-barra{margin:0 0 10px;font-size:12px}.pleg-barra button{font-size:12px;padding:2px 8px;margin-right:6px}
.pleg-t{cursor:pointer}.pleg-t::before{content:"\\25BE\\00a0";color:#666;font-size:.8em}
.pleg-t.cerrado::before{content:"\\25B8\\00a0"}
.pleg-oculto{display:none!important}
@media print{.pleg-barra{display:none}.pleg-t::before{content:""}.pleg-oculto{display:revert!important}}
"""

JS = """
(function(){
function nivel(e){return e.tagName==='H2'?2:3}
function hijos(h){var r=[],e=h.nextElementSibling;while(e&&!(/^H[123]$/.test(e.tagName)&&nivel(e)<=nivel(h))){r.push(e);e=e.nextElementSibling}return r}
function poner(h,cerrar){h.classList.toggle('cerrado',cerrar);hijos(h).forEach(function(e){e.classList.toggle('pleg-oculto',cerrar)})}
function todos(c){document.querySelectorAll('.pleg-t').forEach(function(h){poner(h,c)})}
window.addEventListener('DOMContentLoaded',function(){
 var hs=document.querySelectorAll('.contenido h2,.contenido h3');if(!hs.length)return;
 hs.forEach(function(h){h.classList.add('pleg-t');h.addEventListener('click',function(){poner(h,!h.classList.contains('cerrado'))})});
 var b=document.createElement('div');b.className='pleg-barra no-print';
 b.innerHTML='<button type="button">Expandir todo</button><button type="button">Contraer todo</button>';
 b.children[0].onclick=function(){todos(false)};b.children[1].onclick=function(){todos(true)};
 var c=document.querySelector('.contenido');c.insertBefore(b,c.firstChild);
 hs.forEach(function(h){if(h.tagName==='H3'||/^Anexo/.test(h.textContent))poner(h,true)});
 window.addEventListener('beforeprint',function(){todos(false)});
});
})();
"""
