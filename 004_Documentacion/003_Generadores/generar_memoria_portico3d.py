"""Genera 004_Documentacion/002_Memorias/Struttura_Memoria_portico3d.html.   Ejecutar desde la raíz:  python 004_Documentacion/003_Generadores/generar_memoria_portico3d.py
La tabla de fundamento sale de struttura/portico3d/fundamento.py (cada unidad nueva agrega sus filas ahí)."""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "001_Codigo"))

from struttura import __version__
from struttura.emparrillado.informe import tabla
from struttura.portico3d.fundamento import filas
from struttura.portico3d.informe import documento


import sys as _s
_s.path.insert(0, str(Path(__file__).resolve().parent))
from _esquema import esquema_modelo  # noqa: E402

def esquema():
    return esquema_modelo('Cómo se usa: pórtico espacial 3D', 'plantilla_portico3d.csv', 'portico3d',
        [('NODOS', 'id; x; y; z   (Z arriba)'), ('MATERIALES', 'id; E; (G o nu); fy...   o   id; lib  (n.º de la biblioteca)'), ('SECCIONES', 'id; tipo; d; t; b; h ...  (tubo, rectangular, canal, doble_t...)'), ('BARRAS', 'id; nodo_i; nodo_j; material; seccion  [+ art_i / art_j, giro]'), ('APOYOS', 'nodo; ux uy uz phix phiy phiz   (1 = restringido)')],
        [('CARGAS / CARGAS EN BARRAS', 'caso; nodo; Fx Fy Fz Mx My Mz   |   caso; barra; tipo; valor'), ('COMBINACIONES', 'combinacion; caso; factor'), ('RESORTES / DESPLAZAMIENTOS PREFIJADOS', 'apoyos elásticos y asentamientos'), ('PUNTOS DE TENSION', 'id; barra; x; y; z; caso   (tensor y criterio de falla)'), ('SOLDADURAS', 'id; barra; extremo; disposicion; electrodo; w  (ver Memoria de soldadura)'), ('PROYECTO: peso_propio', 'peso_propio;CASO  (necesita rho en MATERIALES)')],
        ['informe.html con visor 3D (estructura, deformada, diagramas, utilización con el mouse)', 'desplazamientos, reacciones, esfuerzos, tensiones, tensores y matriz_K (.csv)', 'soldaduras.csv (si hay bloque SOLDADURAS)'])


def cuerpo():
    p = [f"<h1>Memoria del programa de pórtico espacial 3D</h1><div class='sub'>Qué se usa para calcular: fórmulas, fuente y caso de aplicación (Struttura v{__version__})</div>"]
    p.append("<h2>0. Mapa de uso</h2><p>De arriba hacia abajo: qué copiás, qué bloques completás (amarillo = obligatorios) y qué obtenés.  Los bloques en gris son opcionales.</p>" + esquema())
    p.append("<h2>1. Qué hace</h2><p>Pórtico espacial por el método matricial de rigidez: barras de 12×12 (Euler-Bernoulli), articulaciones por barra, resortes, peso propio, "
             "cargas en nudos y en barras, combinaciones, tensor de tensiones en puntos de la sección y criterios de falla.  Uso: <code>python struttura.py MIARCHIVO.csv</code> con "
             "<code>tipo;portico3d</code>; plantilla en <code>002_Plantillas/plantilla_portico3d.csv</code>.</p>")
    p.append("<h2>2. Fundamento de cálculo</h2>")
    p.append(tabla(["Tema", "Fórmula", "Fuente (libro, ecuación, sección)", "Se aplica a"], filas(),
                   nota="Lo marcado <b>[propio]</b> no está en los libros cargados: es una decisión o extensión de este programa y debe verificarse."))
    return "\n".join(p)


if __name__ == "__main__":
    salida = RAIZ / "004_Documentacion" / "002_Memorias" / "Struttura_Memoria_portico3d.html"
    salida.write_text(documento("Struttura — Memoria del pórtico 3D", cuerpo()), encoding="utf-8")
    print("Escrito:", salida)
