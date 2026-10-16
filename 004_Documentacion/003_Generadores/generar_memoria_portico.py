"""Genera 004_Documentacion/002_Memorias/Struttura_Memoria_portico.html: cómo se usa y cómo funciona el programa de pórtico plano.

Ejecutar desde la carpeta raíz del proyecto:   python 004_Documentacion/003_Generadores/generar_memoria_portico.py
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]  # carpeta Struttura
sys.path.insert(0, str(RAIZ / "001_Codigo"))

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Arc, FancyArrowPatch

from struttura import __version__
from struttura.emparrillado.graficos import _a_svg
from struttura.portico import graficos, visor2d
from struttura.portico.entrada import cargar_modelo
from struttura.portico.esfuerzos import esfuerzos
from struttura.portico.informe import documento, tabla
from struttura.portico.solver import resolver

EJ = RAIZ / "003_Ejemplos" / "002_Portico"


def figura(n, svg, cap):
    return f'<figure>{svg}<figcaption>Figura {n}. {cap}</figcaption></figure>'


def _flecha(ax, p0, p1, col="black", lw=1.4):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=10, lw=lw, color=col, shrinkA=0, shrinkB=0))


def fig_signos():
    """Convenciones de signos positivos de N, V, M sobre un elemento de barra."""
    fig, ax = plt.subplots(figsize=(7.4, 3.0))
    ax.set_xlim(-1, 15)
    ax.set_ylim(-3.2, 3.2)
    ax.set_aspect("equal")
    ax.axis("off")
    for x0, tit in ((0.0, "N > 0 (tracción)"), (5.5, "V > 0"), (11.0, "M > 0")):
        ax.add_patch(plt.Rectangle((x0 + 0.4, -0.35), 3.2, 0.7, fc="#e6e6e6", ec="black", lw=1.2))
        ax.text(x0 + 2.0, 2.6, tit, ha="center", fontsize=9, fontweight="bold")
    _flecha(ax, (0.4, 0), (-0.9, 0), "#1f5fbf"); _flecha(ax, (3.6, 0), (4.9, 0), "#1f5fbf")
    _flecha(ax, (5.9, -0.35), (5.9, 1.3), "#c0392b"); _flecha(ax, (9.1, 0.35), (9.1, -1.3), "#c0392b")
    for x, sg in ((11.4, 1), (14.6, -1)):
        ax.add_patch(Arc((x, 0), 1.6, 1.6, theta1=(200 if sg > 0 else -20), theta2=(340 if sg > 0 else 160), color="#d68910", lw=1.6))
    ax.annotate("", xy=(11.4 + 0.75, -0.2), xytext=(11.4 + 0.5, -0.65), arrowprops=dict(arrowstyle="-|>", color="#d68910", lw=1.6))
    ax.text(13.0, -1.6, "fibra −y_l traccionada", ha="center", fontsize=8, style="italic")
    ax.text(7.5, -1.9, "actúan sobre la cara +x_l hacia −y_l\n(y en la cara −x_l hacia +y_l)", ha="center", fontsize=8, style="italic")
    ax.text(1.9, -1.2, "x_l →   y_l ↑", ha="center", fontsize=8)
    return _a_svg(fig)


import sys as _s
_s.path.insert(0, str(Path(__file__).resolve().parent))
from _esquema import esquema_modelo  # noqa: E402

def esquema():
    return esquema_modelo('Cómo se usa: pórtico plano', 'plantilla_portico.csv', 'portico',
        [('NODOS', 'id; x; y'), ('MATERIALES', 'id; E; nu; fy; sadm; alfa  |  o  id; lib   (+ rho para peso propio)'), ('SECCIONES', 'id; tipo; d; t; b; h; I; A; c; kv'), ('BARRAS', 'id; nodo_i; nodo_j; material; seccion  [+ art_i / art_j]'), ('APOYOS', 'nodo; ux; uy; phi   (1 = restringido)')],
        [('CARGAS', 'caso; nodo; Px; Py; M'), ('CARGAS EN BARRAS', 'caso; barra; tipo; valor; valor2; a; b'), ('COMBINACIONES', 'combinacion; caso; factor'), ('RESORTES / RESORTES INCLINADOS', 'apoyos elásticos'), ('DESPLAZAMIENTOS PREFIJADOS', 'asentamientos de apoyo'), ('DESAJUSTE DE RESORTES', 'desajuste inicial'), ('PROYECTO: peso_propio', 'peso_propio;CASO · gravedad;-y  (necesita rho en MATERIALES)')],
        ['informe.html con visor (estructura, utilización, deformada, diagramas N, V, M, resultados por caso y combinación)', 'desplazamientos, reacciones, esfuerzos, tensiones y matriz_K (.csv)', 'resortes.csv (si hay resortes)'])


def cuerpo() -> str:
    m1 = cargar_modelo(EJ / "ejemplo1_portico_simple.csv")
    r1, _ = resolver(m1)
    m2 = cargar_modelo(EJ / "ejemplo2_tres_articulaciones.csv")
    r2, _ = resolver(m2)
    e2 = esfuerzos(m2, r2["NIEVE"])
    csv1 = (EJ / "ejemplo1_portico_simple.csv").read_text(encoding="utf-8")
    p = []
    p.append("<h1>Memoria del programa de pórtico plano</h1><div class='sub'>Método matricial de rigidez – cómo se usa y cómo funciona (Struttura v"+__version__+")</div>")
    p.append("<h2>0. Mapa de uso</h2><p>De arriba hacia abajo: qué copiás, qué bloques completás (amarillo = obligatorios) y qué obtenés.  Los bloques en gris son opcionales.</p>" + esquema())
    p.append("""<ul class="conv"><li><b>1.</b> Qué hace</li><li><b>2.</b> Cómo se usa</li><li><b>3.</b> El archivo de datos (plantilla de pórtico)</li>
<li><b>4.</b> Modelo: ejes, GDL y matriz de la barra</li><li><b>5.</b> Articulaciones</li><li><b>6.</b> Cargas en el tramo</li>
<li><b>7.</b> Apoyos, resortes, desajustes y desplazamientos prefijados</li><li><b>8.</b> Esfuerzos, signos y funciones</li>
<li><b>9.</b> Tensiones y coeficientes de seguridad</li><li><b>10.</b> Gráficos e informe</li><li><b>11.</b> Verificaciones</li>
<li><b>12.</b> Estructura del código</li><li><b>13.</b> Supuestos y limitaciones</li></ul>""")

    p.append("<h2>1. Qué hace</h2>")
    p.append("""<p>Resuelve <b>pórticos planos</b> (barras en el plano XY con esfuerzos en su plano).  Cada nodo tiene 3 grados de libertad
(u<sub>x</sub>, u<sub>y</sub>, φ) y cada barra trabaja a <b>axil, corte y flexión</b> (Euler-Bernoulli).  Desde un CSV calcula desplazamientos, reacciones, esfuerzos
(N, V, M), tensiones y coeficientes de seguridad, y genera un informe HTML con el formato de memoria de cálculo.  Todo lo del emparrillado está disponible:
cargas nodales y en tramos, resortes, desplazamientos prefijados, desajuste de resortes, combinaciones, diagramas normalizados por barra, funciones de los diagramas
y vista interactiva.  Además: articulaciones (rótulas) en los extremos de las barras y variación de temperatura uniforme y en gradiente.</p>
<p>Es un programa <b>separado</b> del de emparrillado (paquete <code>struttura/portico/</code>), con su propia plantilla de CSV.  <code>struttura.py</code> elige el programa
según <code>tipo;portico</code> / <code>tipo;emparrillado</code> en el bloque PROYECTO (o según el encabezado de APOYOS: <code>ux;uy;phi</code> vs. <code>uz;phix;phiy</code>).</p>""")

    p.append("<h2>2. Cómo se usa</h2>")
    p.append("""<pre class="codigo">python struttura.py 003_Ejemplos/002_Portico/ejemplo1_portico_simple.csv                  # calcula y genera el informe
python struttura.py 003_Ejemplos/002_Portico/ejemplo1_portico_simple.csv --solo-esquema   # solo dibuja los datos para revisarlos
python struttura.py mi_porticos.csv -o carpeta --sin-graficos</pre>
<p>Los resultados quedan en <code>&lt;archivo&gt;_salida/</code>: <code>informe.html</code> y los CSV <code>desplazamientos, reacciones, resortes, esfuerzos, tensiones, matriz_K</code>.
El informe se imprime con el botón <i>Imprimir</i>.  Recomendación: correr primero con <code>--solo-esquema</code> para verificar numeración, apoyos, articulaciones y signo de las cargas.</p>""")

    p.append("<h2>3. El archivo de datos (plantilla de pórtico)</h2>")
    p.append("<p>Un solo CSV con bloques titulados; la plantilla comentada está en <code>002_Plantillas/plantilla_portico.csv</code>.  Separador <code>;</code> con coma decimal, o <code>,</code> con punto.</p>")
    p.append(tabla(["Bloque", "Oblig.", "Columnas"], [
        ["PROYECTO", "no", "<code>clave;valor</code>: proyecto, autor, unidad_fuerza, unidad_longitud, escala_deformada, escala_diagramas (barra|global), anexo_matrices, csv_salida, <b>tipo;portico</b>"],
        ["NODOS", "sí", "<code>id;x;y</code>"],
        ["MATERIALES", "sí", "<code>id;E;nu;fy;sadm;alfa</code> (fy, sadm: coeficientes de seguridad; alfa: temperatura)"],
        ["SECCIONES", "sí", "<code>id;tipo;d;t;b;h;I;A;c;kv</code>; tipos tubo, circular, rectangular, rect_hueca, generica (I y A). <code>h</code> = dimensión en el plano"],
        ["BARRAS", "sí", "<code>id;nodo_i;nodo_j;material;seccion;art_i;art_j</code> (art = 1: articulación en ese extremo)"],
        ["APOYOS", "sí", "<code>nodo;ux;uy;phi</code> (1 = restringido)"],
        ["RESORTES", "no", "<code>nodo;kx;ky;kphi</code>"],
        ["RESORTES INCLINADOS", "no", "<code>nodo;k;angulo</code> (eje del resorte a <i>angulo</i> grados de +X, antihorario)"],
        ["CARGAS", "no", "<code>caso;nodo;Px;Py;M</code> (M antihorario +)"],
        ["CARGAS EN BARRAS", "no", "<code>caso;barra;tipo;valor;valor2;a;b</code> con tipos q, qa, qgx, qgy, qgxp, qgyp, P, Pa, Pgx, Pgy, Mp, temp (sección 6)"],
        ["DESPLAZAMIENTOS PREFIJADOS", "no", "<code>caso;nodo;ux;uy;phi</code> (solo GDL restringidos)"],
        ["DESAJUSTE DE RESORTES", "no", "<code>caso;nodo;ux;uy;phi;inclinado</code> (apoyo corrido del resorte; más corto → e &lt; 0)"],
        ["COMBINACIONES", "no", "<code>combinacion;caso;factor</code>"]], clase="datos"))
    p.append("<h3>Ejemplo 1 (portal empotrado)</h3><pre class=\"codigo\">" + csv1.replace("&", "&amp;").replace("<", "&lt;") + "</pre>")

    p.append("<h2>4. Modelo: ejes, GDL y matriz de la barra</h2>")
    p.append("""<p>Ejes globales X → derecha, Y ↑; φ positivo <b>antihorario</b>.  La barra tiene ejes locales x<sub>l</sub> (de i a j) e y<sub>l</sub> (90° antihorario), con
γ<sub>1</sub> = cos α = Δx/L y γ<sub>2</sub> = sen α = Δy/L.  Con las constantes de la tabla de cátedra
K = A·E/L, K<sub>1</sub> = 12·E·I/L³, K<sub>2</sub> = 6·E·I/L², K<sub>3</sub> = 4·E·I/L, la matriz de la barra sobre el eje x<sub>l</sub> (GDL u<sub>i</sub>, v<sub>i</sub>, θ<sub>i</sub>, u<sub>j</sub>, v<sub>j</sub>, θ<sub>j</sub>) es</p>
<pre class="codigo">        [  K    0     0    -K    0     0  ]
        [  0    K1    K2    0   -K1    K2 ]
k_loc = [  0    K2    K3    0   -K2    K3/2]
        [ -K    0     0     K    0     0  ]
        [  0   -K1   -K2    0    K1   -K2 ]
        [  0    K2   K3/2   0   -K2    K3 ]</pre>
<p>y la matriz global es k<sub>glo</sub> = T·k<sub>loc</sub>·Tᵀ, con T = diag(R, R) y R = [γ<sub>1</sub> −γ<sub>2</sub> 0; γ<sub>2</sub> γ<sub>1</sub> 0; 0 0 1].  Esto coincide término a término con la
"barra general" de la tabla (A = γ<sub>1</sub>²K + γ<sub>2</sub>²K<sub>1</sub>, B = γ<sub>1</sub>γ<sub>2</sub>(K − K<sub>1</sub>), C = γ<sub>2</sub>K<sub>2</sub>, D = γ<sub>2</sub>²K + γ<sub>1</sub>²K<sub>1</sub>, E = γ<sub>1</sub>K<sub>2</sub>); un test lo verifica
para varios ángulos.  Se ensambla K (3n × 3n), se resuelve K<sub>ff</sub>·u<sub>f</sub> = F<sub>f</sub> − K<sub>fr</sub>·u<sub>r</sub> y se obtienen las fuerzas de extremo f = k·u<sub>loc</sub> + f<sub>0</sub>.
La estabilidad se controla con los autovalores de K<sub>ff</sub> normalizada (mecanismo si &lt; 1E-12).</p>""")

    p.append("<h2>5. Articulaciones</h2>")
    p.append("""<p>Con <code>art_i</code> / <code>art_j</code> = 1 el momento en ese extremo de la barra es nulo.  Se hace <b>condensación estática</b> del giro del extremo articulado:
k<sub>c</sub> = k<sub>AA</sub> − k<sub>AB</sub>·k<sub>BB</sub><sup>−1</sup>·k<sub>BA</sub> y f<sub>0c</sub> = f<sub>0,A</sub> − k<sub>AB</sub>·k<sub>BB</sub><sup>−1</sup>·f<sub>0,B</sub>
(A = GDL que se conservan, B = giros liberados).  Después de resolver, el giro liberado se recupera con u<sub>B</sub> = −k<sub>BB</sub><sup>−1</sup>(k<sub>BA</sub>·u<sub>A</sub> + f<sub>0,B</sub>) y f = k·u + f<sub>0</sub> da M = 0 en la articulación.
El informe muestra ese giro de la barra, distinto del φ del nodo.  Si en un nodo <b>todas</b> las barras están articuladas (y no hay apoyo ni resorte de giro), φ no tiene rigidez:
el programa lo fija internamente (aviso) sin efecto sobre los esfuerzos.  Una articulación demás produce un mecanismo, que se detecta y se describe.</p>""")
    m2d = m2
    p.append(figura(1, graficos.fig_esquema(m2d, None, r2["NIEVE"].cb), "Ejemplo 2 (arco de tres articulaciones): apoyos articulados, articulación en la cumbrera (círculos blancos) y nieve por metro proyectado."))

    p.append("<h2>6. Cargas en el tramo</h2>")
    p.append(tabla(["Código", "Carga", "Descomposición local"], [
        ["q", "distribuida ⊥ a la barra (+y<sub>l</sub>), trapecial (valor en a, valor2 en b)", "q<sub>y</sub> = q"],
        ["qa", "distribuida axial (+x<sub>l</sub>)", "q<sub>x</sub> = q"],
        ["qgx, qgy", "distribuida en X / Y global por longitud de barra", "q<sub>x</sub> = γ<sub>1</sub>g<sub>x</sub> + γ<sub>2</sub>g<sub>y</sub>; q<sub>y</sub> = −γ<sub>2</sub>g<sub>x</sub> + γ<sub>1</sub>g<sub>y</sub>"],
        ["qgxp, qgyp", "por longitud <b>proyectada</b> (vertical / horizontal): nieve, viento", "igual que arriba con el valor × |sen α| (qgxp) o × |cos α| (qgyp)"],
        ["P, Pa, Pgx, Pgy", "fuerza puntual en a (⊥, axial, X global, Y global)", "descomposición análoga"],
        ["Mp", "momento puntual en a (antihorario +)", "M<sub>0</sub>"],
        ["temp", "ΔT de la cara +y<sub>l</sub> (valor) y de la cara −y<sub>l</sub> (valor2)", "ΔT<sub>m</sub> = (Ts+Ti)/2 → axil; gradiente → flexión"]], clase="datos"))
    p.append("""<p>Las cargas se reemplazan por cargas nodales equivalentes <b>consistentes</b> F<sub>eq</sub> = ∫Nᵀq dx, con N = [1−ξ, ξ] para lo axial y
N = [H<sub>1</sub>, L·H<sub>2</sub>, H<sub>3</sub>, L·H<sub>4</sub>] (Hermite) para lo transversal; el momento puntual usa dN/dx en a.  Las fuerzas de empotramiento perfecto son f<sub>0</sub> = −F<sub>eq</sub>.
Térmica: N<sub>T</sub> = E·A·α·ΔT<sub>m</sub> (compresión al impedir la dilatación) y M<sub>T</sub> = E·I·α·(T<sub>s</sub> − T<sub>i</sub>)/h; f<sub>0</sub>: P<sub>x,i</sub> = +N<sub>T</sub>, P<sub>x,j</sub> = −N<sub>T</sub>, M<sub>i</sub> = −M<sub>T</sub>, M<sub>j</sub> = +M<sub>T</sub>.
La deformada de cada barra suma a la interpolación de los extremos la solución particular de la barra biempotrada (integrada en forma exacta a partir de los polinomios de esfuerzos).</p>""")

    p.append("<h2>7. Apoyos, resortes, desajustes y desplazamientos prefijados</h2>")
    p.append("""<p>Los GDL restringidos entran al segundo miembro con el valor prefijado (asentamiento).  Los resortes suman k a la diagonal (o k·a·aᵀ en (u<sub>x</sub>, u<sub>y</sub>) si son inclinados, a = (cos β, sen β)).
Con desajuste e del apoyo del resorte, la fuerza sobre la estructura es −k·(u − e) y la carga equivalente es k·e (un resorte más corto que lo proyectado, estirado para conectarlo, tiene e &lt; 0).
Las reacciones de apoyo salen del equilibrio del nodo (incluyen la fuerza de cualquier resorte que caiga en un GDL restringido).  Las combinaciones son superposición lineal de resultados.</p>
<p><b>Dibujo de los resortes.</b> Los resortes no son barras y se dibujan distinto: zigzag verde con un extremo empotrado (rayado) para los lineales (k<sub>x</sub> horizontal, k<sub>y</sub> vertical, inclinados según su ángulo)
y una espiral alrededor del nodo para el resorte torsional (k<sub>φ</sub>).  Cada uno lleva su rótulo «resorte …» y la leyenda dice «resorte (no es una barra)».</p>""")

    p.append("<h2>8. Esfuerzos, signos y funciones</h2>")
    p.append(figura(2, fig_signos(), "Signos positivos: N (tracción), V (horario) y M (tracciona la fibra −y<sub>l</sub>)."))
    p.append("""<p>Con (P<sub>x,i</sub>, P<sub>y,i</sub>, M<sub>i</sub>) las fuerzas de extremo en i (nodo sobre barra, ya con f<sub>0</sub>):</p>
<pre class="codigo">N(x) = −Px_i − ∫qx          V(x) = Py_i + ∫qy
M(x) = −M_i + x·Py_i + ∫qy(s)·(x − s) ds − Σ M0·H(x − a)        (M &gt; 0 tracciona la fibra −yl)
en j:  N(L) = Px_j,   V(L) = −Py_j,   M(L) = M_j</pre>
<p>El informe da, por tramo (partido donde empieza o termina una carga), los <b>polinomios exactos</b> N(x), V(x), M(x) con x desde el nodo i.  Los diagramas de N y V se dibujan hacia +y<sub>l</sub> y el de M
del lado de la <b>fibra traccionada</b>.  Invertir el orden i–j de una barra cambia el signo de M (y no el de N ni el de V); el dibujo físico es el mismo.  Con <code>escala_diagramas;barra</code>
cada barra se normaliza a su máximo (se ve la forma) y los números rotulados son los reales.</p>""")
    cur = e2["curvas"]
    p.append(figura(3, graficos.fig_diagrama_curvas(m2, [(c["x"], c["M"]) for c in cur], "N·mm", "M: hacia la fibra traccionada", lado=-1),
                    "Ejemplo 2, nieve: momentos flectores; nulos en las articulaciones (cumbrera) y con máximos en los tramos inclinados."))
    p.append(figura(4, graficos.fig_deformada(m2, r2["NIEVE"])[0], "Ejemplo 2, nieve: deformada amplificada."))

    p.append("<h2>9. Tensiones y coeficientes de seguridad</h2>")
    p.append("""<p>Fibras extremas: σ = N/A ± M·c/I (se informan la tracción y la compresión máximas a lo largo de la barra).  Corte: τ<sub>v</sub> = k<sub>v</sub>·|V|/A en el eje neutro.
Von Mises en dos puntos de control por sección: la fibra extrema (|σ|, corte nulo) y el eje neutro (√((N/A)² + 3τ<sub>v</sub>²)); se toma el máximo sobre la barra.
CS fluencia = f<sub>y</sub>/σ<sub>VM</sub> y CS admisible = σ<sub>adm</sub>/σ<sub>VM</sub> (cumple si ≥ 1).  El pandeo de Euler se verifica por barra comprimida (ver «Funciones comunes»).</p>""")

    p.append("<h2>10. Gráficos e informe</h2>")
    esc = [{"nombre": n, "F": r.F, "cb": r.cb, "res": r} for n, r in r1.items()]
    p.append(f'<figure>{visor2d.visor_html(m1, esc, "visorM1")}<figcaption>Vista interactiva del ejemplo 1: caso, diagrama N/V/M, deformada, cargas; arrastrar para mover, rueda para zoom.</figcaption></figure>')
    p.append("""<p>El informe contiene: convenciones, datos (con esquema y vista interactiva), resultados de cada caso y combinación (desplazamientos, reacciones, fuerzas en resortes, giros en articulaciones,
esfuerzos, funciones, tensiones, gráficos), verificaciones (estabilidad y equilibrio global ΣF<sub>x</sub>, ΣF<sub>y</sub>, ΣM) y anexo con las matrices.</p>""")

    p.append("<h2>11. Verificaciones</h2>")
    p.append("""<ul class="conv"><li>Fórmulas de tablas: voladizo (puntual, distribuida, trapecial, momento), biempotrada (uniforme, puntual centrada y excéntrica), empotrada-articulada, resorte en punta, asentamiento y temperatura.</li>
<li>Arco de tres articulaciones: empuje H = qL²/(8f) y reacciones verticales.</li>
<li>Solver clásico independiente (fórmula con cos y sen) sobre un pórtico irregular: mismos desplazamientos.</li>
<li>Invariancia: rotar toda la estructura y las cargas rota los desplazamientos y no cambia los esfuerzos; intercambiar i↔j da los mismos resultados físicos.</li>
<li>Cargas globales equivalentes a q + qa locales; cargas puntuales y momentos en el extremo equivalen a cargas nodales.</li>
<li>Los polinomios de esfuerzos coinciden con los valores de extremo; la deformada pasa por los desplazamientos nodales; equilibrio global en todos los ejemplos.</li></ul>
<p>Todo en <code>tests/test_portico.py</code> (<code>python -m unittest discover -s tests</code>).</p>""")

    p.append("<h2>12. Estructura del código</h2>")
    p.append(tabla(["Archivo", "Función"], [
        ["<code>struttura.py</code>", "despachador: elige emparrillado, pórtico o reticulado"],
        ["<code>portico/entrada.py</code>", "lectura y validación del CSV de pórtico (bloques propios)"],
        ["<code>portico/barra.py</code>", "k local de la tabla, rotación, condensación de articulaciones"],
        ["<code>portico/cargas_barra.py</code>", "descomposición local, cargas equivalentes, f<sub>0</sub>, polinomios N/V/M, solución particular"],
        ["<code>portico/solver.py</code>", "ensamblaje, estabilidad, solución, reacciones, resortes, combinaciones, equilibrio"],
        ["<code>portico/esfuerzos.py</code>", "curvas, extremos, funciones, tensiones, deformada"],
        ["<code>portico/graficos.py</code>, <code>visor2d.py</code>", "gráficos SVG y visor interactivo 2D"],
        ["<code>portico/informe.py</code>, <code>__main__.py</code>", "informe HTML, línea de comandos y CSV de resultados"],
        ["<code>reticulado/</code>", "reticulado plano: convierte su CSV a un pórtico con todas las barras articuladas y agrega verificación de pandeo e informe propio"],
        ["<code>002_Plantillas/</code>", "plantillas comentadas de los tres programas"]], clase="datos"))

    p.append("<h2>13. Supuestos y limitaciones</h2>")
    p.append("""<ul class="conv"><li>Teoría de Euler-Bernoulli (sin deformación por corte), pequeños desplazamientos, comportamiento lineal, sin efectos de segundo orden (el pandeo de Euler se verifica por barra con la condición de extremos que elige el diseñador).</li>
<li>Deformación axial incluida (el programa no supone barras inextensibles).</li>
<li>Secciones simétricas respecto del eje de flexión (la misma distancia c a ambas fibras).</li>
<li>Articulaciones solo en el extremo de barras (no hay apoyos inclinados, ni rótulas con resorte de giro).</li>
<li>Los gradientes térmicos se dan por diferencia entre las dos caras; la variación es lineal en la altura h.</li>
<li>Matriz densa: adecuada para hasta unos cientos de nodos.</li></ul>""")
    from _comun import seccion_comun
    p.append(seccion_comun("portico"))
    return "\n".join(p)


if __name__ == "__main__":
    salida = RAIZ / "004_Documentacion" / "002_Memorias" / "Struttura_Memoria_portico.html"
    salida.write_text(documento("Memoria del programa – Pórtico plano", cuerpo(), boton=True, visor=True), encoding="utf-8")
    print("Escrito:", salida)
