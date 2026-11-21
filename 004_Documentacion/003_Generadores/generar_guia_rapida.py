"""Genera la GUÍA RÁPIDA (HTML + PDF) de las plantillas: qué va en cada bloque, cada columna, valores posibles y recetas.

Ejecutar desde la raíz del proyecto:   python 004_Documentacion/003_Generadores/generar_guia_rapida.py
Salida: 004_Documentacion/001_Guia_rapida/Struttura_Guia_rapida.html y 004_Documentacion/001_Guia_rapida/Struttura_Guia_rapida.pdf
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]  # carpeta Struttura
sys.path.insert(0, str(RAIZ / "001_Codigo"))

from struttura.portico import graficos
from struttura.portico.entrada import cargar_modelo
from struttura import __version__

CSS = """
@page { size: A4; margin: 14mm 13mm 14mm 13mm; }
* { box-sizing: border-box; }
body { font-family: 'Liberation Sans', 'DejaVu Sans', Arial, sans-serif; font-size: 8.6pt; line-height: 1.32; color: #111; margin: 0; }
h1 { font-size: 18pt; margin: 0 0 1mm 0; border-bottom: 2px solid #111; padding-bottom: 1.5mm; }
.sub { font-size: 9.5pt; color: #444; margin-bottom: 3mm; }
h2 { font-size: 12pt; margin: 5mm 0 1.6mm; padding: 1mm 2mm; background: #1f3a5f; color: #fff; break-after: avoid; }
h3 { font-size: 10pt; margin: 3.2mm 0 1mm; color: #1f3a5f; border-bottom: 1px solid #99a; break-after: avoid; }
p { margin: 1mm 0 1.6mm; }
table { border-collapse: collapse; width: 100%; margin: 1mm 0 2.2mm; break-inside: avoid; }
th, td { border: 0.6px solid #777; padding: 1px 4px; vertical-align: top; text-align: left; }
th { background: #e6ebf2; font-weight: bold; }
code, pre { font-family: 'DejaVu Sans Mono', 'Liberation Mono', monospace; font-size: 7.6pt; }
pre { background: #f3f3f3; border: 0.6px solid #aaa; padding: 2mm; margin: 1mm 0 2mm; white-space: pre-wrap; break-inside: avoid; }
.caja { border: 1.2px solid #1f3a5f; padding: 1.5mm 3mm; margin: 2mm 0; background: #f4f7fb; break-inside: avoid; }
.warn { border: 1.2px solid #a33; background: #fbf1f1; padding: 1.5mm 3mm; margin: 2mm 0; break-inside: avoid; }
.dos { display: flex; gap: 4mm; } .dos > div { flex: 1; min-width: 0; }
.ob { color: #a00; font-weight: bold; } .op { color: #555; }
svg { max-width: 100%; height: auto; }
.pag { break-before: page; }
figure { margin: 2mm 0; text-align: center; break-inside: avoid; } figcaption { font-size: 8pt; font-style: italic; }
"""


def T(cab, filas, ancho=None):
    h = "<tr>" + "".join(f"<th>{c}</th>" for c in cab) + "</tr>"
    b = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in f) + "</tr>" for f in filas)
    return f"<table>{h}{b}</table>"


OB, OP = '<span class="ob">obligatorio</span>', '<span class="op">opcional</span>'


def cuerpo():
    p = []
    p.append(f"<h1>Guía rápida de plantillas</h1><div class='sub'>Estructuras por el método matricial de rigidez · "
             f"Struttura versión {__version__} · emparrillado · pórtico plano · reticulado plano · pórtico espacial</div>")

    # ------------------------------------------------------------------ 1
    p.append("<h2>1. En 30 segundos</h2>")
    p.append("""<div class="caja"><b>1)</b> Copiá la plantilla que corresponde (<code>002_Plantillas/plantilla_portico.csv</code>,
<code>plantilla_reticulado.csv</code>, <code>plantilla_emparrillado.csv</code>, <code>plantilla_portico3d.csv</code> o <code>plantilla_soldadura.csv</code>) y renombrala.&nbsp; <b>2)</b> Completá los bloques.&nbsp;
<b>3)</b> Ejecutá <code>python struttura.py MIARCHIVO.csv</code> (elige solo el programa según <code>tipo;…</code> del bloque PROYECTO).&nbsp;
<b>4)</b> Abrí <code>MIARCHIVO_salida/informe.html</code> (botón Imprimir → PDF) y los CSV de resultados.<br>
<b>O sin escribir el CSV a mano:</b> <code>python struttura.py --editor [MIARCHIVO.csv]</code> abre el editor visual (tablas guiadas + dibujo, Guardar como y Calcular); ver <code>Struttura_Memoria_editor.html</code>.</div>""")
    p.append(T(["Opción", "Qué hace"],
               [["<code>--solo-esquema</code>", "No calcula: dibuja datos y cargas para <b>revisar la entrada</b> (numeración, apoyos, resortes, signo de cargas). Conviene hacerlo siempre antes."],
                ["<code>--sin-graficos</code>", "Informe sin gráficos (más rápido en modelos grandes)."],
                ["<code>-o CARPETA</code>", "Carpeta de salida (por defecto <code>MIARCHIVO_salida</code>)."],
                ["<code>--tipo portico|portico3d|reticulado|emparrillado|soldadura</code>", "Fuerza el programa si el archivo no dice <code>tipo;…</code>."],
                ["<code>--soldadura \"circulo d=50.8 Vz=3000 electrodo=E70 w=3\"</code>", "Verifica una soldadura de filete en una línea, sin archivo (ver sección 4c)."],
                ["<code>--biblioteca listar</code> · <code>--biblioteca ver N</code>", "Lista los materiales de tu biblioteca (número y nombre) o muestra todos los datos de uno."],
                ["<code>--biblioteca electrodos</code> · <code>--biblioteca electrodo N_O_ID</code>", "Lo mismo para la biblioteca de electrodos (<code>006_Biblioteca/electrodos.csv</code>)."],
                ["<code>--biblioteca perfiles [FAMILIA]</code> · <code>--biblioteca perfil N_O_DESIGNACION</code>", "Lo mismo para la biblioteca de perfiles (<code>006_Biblioteca/perfiles.csv</code>, tablas CIRSOC)."]]))
    p.append("<h3>¿Qué programa uso?</h3>")
    p.append(T(["Estructura", "tipo;", "GDL por nodo", "Columnas de APOYOS", "Qué calcula"],
               [["Pórtico plano (vigas y columnas con flexión, axil y corte; permite articulaciones)", "<code>portico</code>", "ux, uy, φ", "<code>nodo;ux;uy;phi</code>",
                 "N, V, M, tensiones, CS (criterios de falla), pandeo, soldaduras, deformada, resortes, prefijados, temperatura"],
                ["Reticulado plano (barras articuladas, solo axil)", "<code>reticulado</code>", "ux, uy", "<code>nodo;ux;uy</code>",
                 "N, σ, ΔL, CS fluencia / adm., <b>pandeo de Euler</b>, deformada"],
                ["Emparrillado (estructura plana cargada perpendicular a su plano)", "<code>emparrillado</code>", "uz, φx, φy", "<code>nodo;uz;phix;phiy</code>",
                 "V, T, M, tensiones (criterios de falla), soldaduras, deformada"],
                ["<b>Pórtico espacial 3D</b> (barras de 12×12, nudos rígidos)", "<code>portico3d</code>", "ux, uy, uz, φx, φy, φz", "<code>nodo;ux;uy;uz;phix;phiy;phiz</code>",
                 "N, Vy, Vz, T, My, Mz, tensiones (criterios de falla), pandeo, soldaduras, visor 3D con diagramas y deformada"]]))
    p.append('<div class="warn"><b>Reticulado = bielas:</b> articuladas en los nudos, solo axil, cargas solo en nudos (más ΔT y barra corta/larga). <b>Reticulado dentro de un pórtico:</b> si una estructura mezcla barras rígidas y barras de reticulado, usá el programa de <b>pórtico</b> '
             'y marcá esas barras con <code>art_i = 1</code> y <code>art_j = 1</code> (articuladas en ambos extremos): trabajan solo a axil. '
             'Con todas las barras articuladas también sirve el pórtico, pero el programa de reticulado agrega pandeo y un informe más corto.</div>')

    # ------------------------------------------------------------------ 2
    p.append("<h2>2. Reglas del archivo (valen para los tres tipos)</h2>")
    p.append("""<ul style="margin:0 0 0 4mm;padding:0">
<li>Un <b>único CSV</b> con <b>bloques</b>: una línea con solo el título del bloque, luego la fila de <b>encabezados</b> y luego los datos.</li>
<li>Se ignoran las líneas vacías y las que empiezan con <code>#</code> (comentarios). Títulos y encabezados: sin distinguir mayúsculas ni tildes.</li>
<li>Separador <code>;</code> con coma decimal (CSV de Excel en español) <b>o</b> <code>,</code> con punto decimal. Si hay algún <code>;</code>, se usa <code>;</code>.</li>
<li>Unidades: <b>coherentes</b> a elección (N–mm–MPa, kg–cm–kg/cm², kN–cm–kN/cm²…). El programa no convierte: solo rotula lo que escribís en <code>unidad_fuerza</code> y <code>unidad_longitud</code>.</li>
<li>Los <b>id</b> (nodos, barras, materiales, secciones, casos) son texto libre pero <b>únicos</b>. Celda vacía = «no aplica / cero».</li>
<li>Los errores dicen bloque, línea y columna. Un archivo con <code>--solo-esquema</code> también avisa si la estructura es un mecanismo.</li>
</ul>""")

    # ------------------------------------------------------------------ 3 pórtico
    p.append('<h2>3. Pórtico plano — bloque por bloque</h2>')
    p.append("<p>Ejes globales: X → derecha, Y ↑. Giro φ positivo <b>antihorario</b>. Barra: eje local x<sub>l</sub> de <code>nodo_i</code> a <code>nodo_j</code>, y<sub>l</sub> a 90° antihorario. "
             "La gravedad es <b>negativa</b> en Y.</p>")
    p.append(T(["Bloque", "Columnas", "Notas / valores posibles"],
               [["PROYECTO<br>" + OP, "<code>clave;valor</code>",
                 "<code>proyecto</code>, <code>autor</code>, <code>unidad_fuerza</code>, <code>unidad_longitud</code>, <code>tipo;portico</code>, "
                 "<code>escala_deformada</code> (auto | número), <code>escala_diagramas</code> (barra | global; defecto barra), <code>anexo_matrices</code> (auto | si | no), <code>csv_salida</code> (excel_es | estandar), <code>peso_propio</code> (CASO) y <code>gravedad</code> (±x, ±y; por defecto -y) — el peso propio necesita <b>rho</b> en kg/m³ en MATERIALES"],
                ["NODOS<br>" + OB, "<code>id;x;y</code>", "Coordenadas en ejes globales."],
                ["MATERIALES<br>" + OB, "<code>id;E;nu;fy;sadm;alfa;sut;suc;teoria</code> (+ <code>lib</code>)", "Solo <b>E</b> es obligatorio (o <b>lib</b> = número de un material de tu biblioteca: completa E, nu y fy; lo escrito a mano manda). <b>fy</b> y <b>sadm</b> → coeficientes de seguridad. <b>teoria</b> = vm (defecto) · tresca · rankine · mohr · mohrmod (rankine y mohr necesitan <b>sut</b>; <b>suc</b> por defecto = sut). <b>alfa</b> [1/°C] solo si hay temperatura."],
                ["SECCIONES<br>" + OB, "<code>id;tipo;lib;d;t;b;h;I;A;c;kv;tf;tw</code>", "Ver tabla de tipos abajo. <b>h</b> = dimensión en el plano del pórtico. <b>Perfil de la biblioteca</b>: <code>tipo;perfil</code> + <code>lib;N</code> (número de <code>006_Biblioteca/perfiles.csv</code>, tablas CIRSOC): completa A, I, J... en las unidades del modelo; lo escrito a mano manda."],
                ["BARRAS<br>" + OB, "<code>id;nodo_i;nodo_j;material;seccion;art_i;art_j;pandeo</code>", "<b>art_i / art_j = 1</b>: articulación (M = 0) en ese extremo; vacío o 0 = rígido. Dos articulaciones = barra de reticulado. <b>pandeo</b> (opcional): <code>art-art</code> (defecto) · <code>emp-lib</code> · <code>emp-art</code> · <code>emp-emp</code>: da <b>CS pandeo</b> en barras comprimidas."],
                ["APOYOS<br>" + OB, "<code>nodo;ux;uy;phi</code>", "<b>1 = restringido</b>, 0 o vacío = libre. Empotrado <code>1;1;1</code> · fijo <code>1;1;0</code> · móvil vertical <code>0;1;0</code> · móvil horizontal <code>1;0;0</code>."],
                ["RESORTES<br>" + OP, "<code>nodo;kx;ky;kphi</code>", "Rigidez [fuerza/longitud] en ux, uy y <b>kphi</b> [momento/rad] (resorte torsional). Vacío = sin resorte."],
                ["RESORTES INCLINADOS<br>" + OP, "<code>nodo;k;angulo</code>", "Resorte lineal cuyo eje forma <b>angulo</b> grados con +X (antihorario). Ej.: perpendicular a una barra a 53,13° → 143,13° (o −36,87°)."],
                ["CARGAS<br>" + OP, "<code>caso;nodo;Px;Py;M</code>", "Nodales en ejes globales. M positivo antihorario."],
                ["CARGAS EN BARRAS<br>" + OP, "<code>caso;barra;tipo;valor;valor2;a;b</code>", "Tipos abajo. <b>a</b>, <b>b</b> desde nodo_i; vacíos = toda la barra."],
                ["DESPLAZAMIENTOS PREFIJADOS<br>" + OP, "<code>caso;nodo;ux;uy;phi</code>", "Solo sobre GDL <b>restringidos</b> en APOYOS (asentamientos, giros impuestos). Un caso puede tener solo prefijados."],
                ["DESAJUSTE DE RESORTES<br>" + OP, "<code>caso;nodo;ux;uy;phi;inclinado</code>", "Desplazamiento impuesto al <i>apoyo del resorte</i>: fuerza = −k(u − e). Resorte estirado para conectarlo → e negativo."],
                ["COMBINACIONES<br>" + OP, "<code>combinacion;caso;factor</code>", "Superposición lineal de casos (una fila por caso). Ej.: <code>COMB1;PP;1.2</code> y <code>COMB1;VIENTO;1.6</code>."],
                ["SOLDADURAS / ELECTRODOS<br>" + OP, "<code>id;barra;extremo;disposicion;electrodo;w;sy_base;lib;t_gruesa;t_fina</code> · <code>id;sut;sy;tau_adm;lib</code>", "Igual que en el 3D (ver 4c). Esfuerzos del extremo: N = N, Vz = −V, My = −M. Da <code>soldaduras.csv</code>."]]))
    p.append("<h3>Tipos de sección (columna <code>tipo</code>)</h3>")
    p.append(T(["tipo", "Datos que hay que dar", "Calcula solo"],
               [["<code>tubo</code>", "d (diámetro exterior), t (espesor)", "A, I, c, kv, h"],
                ["<code>circular</code>", "d", "A, I, c, kv, h"],
                ["<code>rectangular</code>", "b, h", "A, I, c, kv, h"],
                ["<code>rect_hueca</code>", "b, h, t", "A, I, c, kv, h"],
                ["<code>canal</code>, <code>doble_t</code>, <code>te</code>, <code>z</code>, <code>angular</code>", "h, b, t (o tf y tw), de <b>línea media</b>", "A, I (eje fuerte), c, J, Wt; corte de Jourawski y torsión; h en el plano de la flexión"],
                ["<code>generica</code>", "<b>I y A</b> (pórtico) · <b>A</b> (reticulado; I solo si querés pandeo) · <b>I y J</b> (emparrillado). Opcionales: c (fibra extrema), kv (τ = kv·V/A), h",
                 "Sin <b>c</b> no hay tensiones de flexión; sin <b>A/kv</b> no hay corte"]]))
    p.append("<h3>Tipos de carga en barras (columna <code>tipo</code>) — pórtico</h3>")
    p.append(T(["Código", "Qué es", "valor / valor2", "Posición"],
               [["<code>q</code>", "Distribuida <b>perpendicular</b> a la barra, + hacia +y<sub>l</sub>", "valor en <i>a</i>, valor2 en <i>b</i> (vacío = uniforme)", "a, b"],
                ["<code>qa</code>", "Distribuida <b>axial</b>, + hacia +x<sub>l</sub>", "ídem", "a, b"],
                ["<code>qgx</code> / <code>qgy</code>", "Distribuida en X / Y <b>globales</b> por unidad de longitud de barra (peso propio: qgy negativa)", "ídem", "a, b"],
                ["<code>qgxp</code> / <code>qgyp</code>", "Distribuida global por unidad de longitud <b>proyectada</b> (viento sobre paramento: qgxp; nieve: qgyp)", "ídem", "a, b"],
                ["<code>P</code> / <code>Pa</code>", "Puntual perpendicular / axial a la barra", "valor", "a"],
                ["<code>Pgx</code> / <code>Pgy</code>", "Puntual en X / Y globales", "valor", "a"],
                ["<code>Mp</code>", "Momento puntual (antihorario +)", "valor", "a"],
                ["<code>dl</code>", "Desajuste de longitud de una barra: valor e &gt; 0 = barra <b>larga</b>, e &lt; 0 = <b>corta</b> (axil de empotramiento E·A·e/L)", "valor = e", "toda la barra"],
                ["<code>temp</code>", "Temperatura (necesita <b>alfa</b> del material; el gradiente necesita <b>h</b> de la sección)", "valor = ΔT cara +y<sub>l</sub>, valor2 = ΔT cara −y<sub>l</sub> [°C] (iguales = uniforme)", "toda la barra"]]))

    # ------------------------------------------------------------------ 4b pórtico espacial
    p.append('<h2>4b. Pórtico espacial 3D — bloque por bloque</h2>')
    p.append("<p>Mismo formato de bloques. Cada nudo tiene <b>6 GDL</b> (ux, uy, uz, φx, φy, φz) y cada barra una matriz de <b>12×12</b>. "
             "Nudos rígidos o articulados por barra (<code>art_i</code> / <code>art_j</code>). Ejes globales X, Y, Z con <b>Z hacia arriba</b>.</p>")
    p.append(T(["Bloque", "Columnas", "Notas"],
               [["PROYECTO", "<code>tipo;portico3d</code> + opcionales", "Opcional: <code>peso_propio;CASO</code> (agrega al caso el peso propio de todas las barras; necesita <b>rho</b> en kg/m³ en MATERIALES; si no se escribe, no se calcula) y <code>gravedad;-z</code> (±x, ±y, ±z)."],
                ["NODOS", "<code>id;x;y;z</code>", "—"],
                ["MATERIALES", "<code>id;E;G</code> (o <code>nu</code>);fy;sadm;alfa;<b>sut;suc;teoria</b>", "G (o nu) es obligatorio: la torsión lo usa. <b>teoria</b>: <code>vm</code> (por defecto con fy), <code>tresca</code>, <code>rankine</code>, <code>mohr</code> (dúctil con |σc| &gt; σt), <code>mohrmod</code> (Mohr modificado, frágiles): piden <code>sut</code>; <code>suc</code> = sut por defecto. <b>rho</b> en kg/m³ para el peso propio. <b>lib</b> = número de un material de tu biblioteca (<code>lib;1</code>): completa E, G, nu, fy, sut y rho; lo que escribas a mano manda (ver Memoria de la biblioteca)."],
                ["SECCIONES", "<code>perfil</code>: <code>lib</code> (perfil de la biblioteca: completa A;Iy;Iz;J;cy;cz;Wt) · <code>generica</code>: <code>A;Iy;Iz;J</code> (+ <code>cy;cz;Wt</code> para tensiones) · <code>tubo</code> d;t · <code>circular</code> d · <code>rectangular</code> b;h · <code>rect_hueca</code> b;h;t · perfiles abiertos de pared delgada, dimensiones de <b>línea media</b>: <code>canal</code> h;b;t (o tf;tw) · <code>doble_t</code> / <code>te</code> / <code>z</code> h;b;tf;tw · <code>angular</code> b;h;t",
                 "<b>Iy</b>: flexión alrededor de y local (flecha en z). <b>Iz</b>: alrededor de z local. b según y local, h según z local. Canal: alma en y&lt;0, alas hacia +y. En ángulo y Z el programa gira la sección a los ejes principales. Calcula centro de corte, corte de Jourawski y torsión J = Σ l·t³/3."],
                ["BARRAS", "<code>id;nodo_i;nodo_j;material;seccion</code> + opcional <code>rx;ry;rz</code>, <code>giro</code>, <code>art_i;art_j</code> y <code>pandeo</code>",
                 "<b>pandeo</b> (opcional): <code>art-art</code> (defecto) · <code>emp-lib</code> · <code>emp-art</code> · <code>emp-emp</code>; da CS pandeo con la menor inercia de la sección. x local de i a j. z local por defecto = +Z global (barra vertical: +X). <code>rx;ry;rz</code> = hacia dónde apunta z local. <code>giro</code> = grados alrededor de x."],
                ["APOYOS / RESORTES", "<code>nodo;ux;uy;uz;phix;phiy;phiz</code> · <code>nodo;kx;ky;kz;kphix;kphiy;kphiz</code>", "1 = restringido. Resortes en ejes globales."],
                ["Columna <code>pc</code> (RESORTES y RESORTES INCLINADOS)", "<code>pc</code>", "Carga crítica de pandeo de la barra que el resorte reemplaza (Euler, la calcula el botón «Calcular k de una barra» del editor). El informe da <b>CS pandeo = Pc/|F|</b>. La fila debe tener un solo resorte lineal. El CS vale si la barra trabaja a compresión (a criterio del diseñador)."],
                ["RESORTES INCLINADOS<br>" + OP, "<code>nodo;k;dx;dy;dz;ax;ay;az</code>", "Resorte lineal a tierra en una dirección cualquiera. Dirección: vector <b>dx;dy;dz</b> o los ángulos <b>ax;ay;az</b> que forma con X, Y, Z (con dos alcanza; cos² suman 1). Aporta k·d·dᵀ. Varios por nodo."],
                ["CARGAS", "<code>caso;nodo;Fx;Fy;Fz;Mx;My;Mz</code>", "Ejes globales."],
                ["CARGAS EN BARRAS", "<code>caso;barra;tipo;valor;valor2;a</code>",
                 "<code>qx qy qz</code> (local) · <code>qgx qgy qgz</code> (global, por longitud de barra) · <code>Px Py Pz</code>, <code>Pgx Pgy Pgz</code> (puntuales, <b>a</b> = distancia desde i) · <code>Mx My Mz</code>, <code>Mgx Mgy Mgz</code> (momentos puntuales). valor2 = valor en j (trapecio)."],
                ["PUNTOS DE TENSION", "<code>id;barra;x;y;z;caso</code>", "<b>Tensor de tensiones completo</b> en esos puntos. x = distancia desde i; (y, z) = coordenadas locales desde el baricentro (vacío = 0); caso vacío = todos."],
                ["SOLDADURAS / ELECTRODOS", "<code>id;barra;extremo;disposicion;b;d;...;electrodo;w;sy_base;lib;t_gruesa;t_fina</code> · <code>id;sut;sy;tau_adm;lib</code>", "Verifica la soldadura en el extremo i o j de una barra con los esfuerzos del solver (ver 4c)."],
                ["DESPLAZAMIENTOS PREFIJADOS / COMBINACIONES", "<code>caso;nodo;ux;uy;uz;phix;phiy;phiz</code> · <code>combinacion;caso;factor</code>", "Prefijado solo en GDL restringidos."]]))
    p.append("<p><b>Esfuerzos</b> (cara +x de la sección): N (tracción +), Vy, Vz, T, My (&gt;0 tracciona la fibra +z), Mz (&gt;0 tracciona la fibra −y). "
             "σ = N/A + My·z/Iy − Mz·y/Iz. El informe trae un <b>visor 3D</b> (arrastrar = girar) con deformada, diagramas de cada esfuerzo y <b>mapa de utilización</b> (al pasar el mouse muestra el valor; 1 = fluencia).</p>")
    p.append("<p><b>Tensor de tensiones:</b> en cada punto σ<sub>x</sub> (N, M<sub>y</sub>, M<sub>z</sub>) y τ<sub>xy</sub>, τ<sub>xz</sub> (torsión + corte de flexión); "
             "principales σ<sub>1</sub> ≥ 0 = σ<sub>2</sub> ≥ σ<sub>3</sub>; criterios Von Mises √(σ²+3τ²), Tresca √(σ²+4τ²), Rankine, Mohr y Mohr modificado con CS = resistencia/σ<sub>eq</sub>. "
             "El informe da los <b>puntos más exigidos</b> (automáticos) y los del bloque PUNTOS DE TENSION; <code>tensores.csv</code> los exporta. "
             "<code>corte_tensiones;no</code> quita el corte de flexión. Teoría de vigas: valores <b>nominales</b> (sin concentración local en nudos soldados). "
             "En tubos y circulares se evalúa cada 15° del perímetro; para el peor punto exacto pedilo en PUNTOS DE TENSION.</p>")

    # ------------------------------------------------------------------ 4c soldaduras
    p.append('<h2>4c. Soldaduras de filete — modo rápido (<code>tipo;soldadura</code>) y bloque SOLDADURAS (3D, pórtico plano y emparrillado)</h2>')
    p.append("<p>Verifica grupos de cordones de filete o uniones a tope con N, Vy, Vz, T, My, Mz. <b>Sin <code>w</code></b> calcula el <b>pie de filete requerido</b>; <b>con <code>w</code></b> da el CS. "
             "Una línea: <code>python struttura.py --soldadura \"circulo d=50.8 Vz=3000 My=200000 electrodo=E70 w=3\"</code> (parámetros: N Vy Vz T My Mz yp zp electrodo w sy_base t_gruesa t_fina tau_adm uf ul). "
             "Plantilla: <code>002_Plantillas/plantilla_soldadura.csv</code>. Fórmulas y fuentes: <code>004_Documentacion/002_Memorias/Struttura_Memoria_soldadura.html</code>.</p>")
    p.append(T(["Bloque", "Columnas", "Notas"],
               [["SOLDADURAS", "<code>id;tipo;disposicion;b;d;arcos;esp;segmentos;electrodo;w;sy_base;t_gruesa;t_fina</code> (en las estructuras además <code>barra;extremo;oy;oz</code>) ; <code>lib</code> = material de la biblioteca (da sy_base)",
                 "<b>sy_base</b> a mano o <b>lib;N</b> (fy del material N de la biblioteca de materiales; lo escrito a mano manda). <b>tipo</b> = <code>filete</code> (por defecto) o <code>tope</code> (penetración completa; <code>esp</code> = espesor de las piezas = garganta; veredicto por 0,60·S<sub>y</sub> y 0,30·S<sub>ut</sub>, más Von Mises). Disposiciones: <code>circulo</code> (d) · <code>arco</code> (d;arcos = <code>centro:abertura|centro:abertura</code> en grados) · <code>rectangulo</code> · <code>costados</code> (solo laterales) · <code>arriba_abajo</code> · <code>L</code> · <code>C</code> · <code>C_invertida</code> · <code>doble_t</code> (b;d) · <code>linea</code> (d) · <code>custom</code> (segmentos \"y0 z0 y1 z1|...\"). b según y, d según z."],
                ["ELECTRODOS", "<code>id;sut;sy;tau_adm;lib</code>", "Opcional: aportes propios (tau_adm en unidades de tensión del modelo); <b>lib</b> = número de <code>006_Biblioteca/electrodos.csv</code> (completa lo que no escribas). Un electrodo que no está en ELECTRODOS se busca por nombre en esa biblioteca (E60 … E120 de Shigley, más los que se carguen); <code>--biblioteca electrodos</code> los lista."],
                ["CARGAS (solo modo rápido)", "<code>soldadura;caso;N;Vy;Vz;T;My;Mz;yp;zp</code>", "yp;zp = punto de aplicación de la carga: el programa calcula el torsor y traslada todo al baricentro del grupo."]]))
    p.append("<p><b>Resultado:</b> fuerza por unidad de longitud f en el punto crítico, τ = f/(0,707·w), CS contra τ<sub>adm</sub> del electrodo, garganta t = 0,707·w (w = cateto), verificación del metal base (0,40·S<sub>y</sub>), "
             "pie mínimo por espesor (Tabla 9-6 B de Shigley) y dibujo 2D del cordón coloreado por f, con el contorno de la sección (en el 3D, el de la barra). En las estructuras: <code>soldaduras.csv</code>.</p>")

    # ------------------------------------------------------------------ 4 reticulado
    p.append('<h2>4. Reticulado plano — bloque por bloque</h2>')
    p.append("<p>Igual que el pórtico, pero <b>sin giros ni momentos</b>: todas las barras son articuladas y solo tienen axil (<b>N &gt; 0 tracción</b>). "
             "Si dejás una columna de giro/momento, el programa avisa el error.</p>")
    p.append(T(["Bloque", "Columnas", "Diferencias con el pórtico"],
               [["PROYECTO", "<code>tipo;reticulado</code> + opcionales", "Opcional: <code>peso_propio;CASO</code> (agrega al caso el peso propio de todas las barras; necesita <b>rho</b> en kg/m³ en MATERIALES; si no se escribe, no se calcula) y <code>gravedad;-y</code> (±x, ±y). En el reticulado el peso de cada barra se reparte mitad en cada nudo extremo."],
                ["SECCIONES<br>" + OB, "<code>id;tipo;lib;d;t;b;h;I;A</code>", "Alcanza con el área: <code>generica</code> con solo <b>A</b>. Para <b>pandeo</b> hace falta <b>I</b> (eje débil). <b>Perfil de la biblioteca</b>: <code>tipo;perfil</code> + <code>lib;N</code> (número de <code>006_Biblioteca/perfiles.csv</code>, tablas CIRSOC): completa A, I, J... en las unidades del modelo; lo escrito a mano manda."],
                ["BARRAS<br>" + OB, "<code>id;nodo_i;nodo_j;material;seccion;pandeo</code>",
                 "<b>pandeo</b> (opcional): condición de vínculos para Pc de Euler: <code>art-art</code> (defecto) · <code>emp-lib</code> · <code>emp-art</code> · <code>emp-emp</code>. No usar art_i/art_j."],
                ["APOYOS<br>" + OB, "<code>nodo;ux;uy</code>", "Fijo <code>1;1</code> · móvil vertical <code>0;1</code> · móvil horizontal <code>1;0</code>."],
                ["RESORTES", "<code>nodo;kx;ky</code>", "Sin kphi."],
                ["RESORTES INCLINADOS", "<code>nodo;k;angulo</code>", "Igual."],
                ["CARGAS", "<code>caso;nodo;Px;Py</code>", "Sin M."],
                ["CARGAS EN BARRAS", "<code>caso;barra;tipo;valor;valor2;a;b</code>", "Las barras son bielas: <b>las cargas van solo en los nudos</b>. En este bloque solo entran efectos que alargan/acortan la barra: <code>temp</code> (ΔT uniforme), <code>corta</code> y <code>larga</code> (desajuste e &gt; 0). Cualquier otra se rechaza."],
                ["DESPLAZAMIENTOS PREFIJADOS", "<code>caso;nodo;ux;uy</code>", "Asentamientos."],
                ["DESAJUSTE DE RESORTES", "<code>caso;nodo;ux;uy;inclinado</code>", "—"],
                ["MATERIALES, NODOS, COMBINACIONES", "—", "Igual que el pórtico."]]))
    p.append("<h3>Pandeo de Euler (tabla de la cátedra)</h3>")
    p.append(T(["Código", "Vínculos", "Carga crítica P<sub>c</sub>"],
               [["<code>emp-lib</code>", "empotrado – libre", "π²EI / (4L²)"],
                ["<code>art-art</code>", "articulado – articulado (defecto)", "π²EI / L²"],
                ["<code>emp-art</code>", "empotrado – articulado", "2π²EI / L² (valor de la tabla)"],
                ["<code>emp-emp</code>", "empotrado – empotrado", "4π²EI / L²"]]))
    p.append("<p>El informe da, por barra comprimida, <b>CS pandeo = P<sub>c</sub>/|N|</b> y la esbeltez λ = KL/r. I es el <b>menor</b> momento de inercia de la sección (eje débil): si la sección no es simétrica, cargalo vos como <code>generica</code>.</p>")

    # ------------------------------------------------------------------ 5 emparrillado
    p.append('<h2>5. Emparrillado plano — bloque por bloque</h2>')
    p.append("<p>Estructura en el plano XY <b>cargada perpendicularmente</b>. GDL: u<sub>z</sub> (+ hacia el lector), φ<sub>x</sub>, φ<sub>y</sub> (vectores de mano derecha). "
             "En las barras: φ<sub>x</sub> local = torsión, φ<sub>y</sub> local = flexión. La gravedad es <b>negativa</b> en z.</p>")
    p.append(T(["Bloque", "Columnas", "Notas"],
               [["PROYECTO", "<code>tipo;emparrillado</code> + mismas claves", "Opcional: <code>peso_propio;CASO</code> (agrega al caso el peso propio de todas las barras; necesita <b>rho</b> en kg/m³ en MATERIALES; si no se escribe, no se calcula) y <code>gravedad;-z</code> (±z)."],
                ["NODOS", "<code>id;x;y</code>", "—"],
                ["MATERIALES", "<code>id;E;nu;G;fy;sadm;alfa;sut;suc;teoria</code> (+ <code>lib</code>)", "E y (G <b>o</b> nu). Opcionales fy, sadm, alfa. <b>lib</b> = número de un material de tu biblioteca (completa E, nu o G y fy; lo escrito a mano manda). <b>teoria</b> = vm (defecto) · tresca · rankine · mohr · mohrmod."],
                ["SECCIONES", "<code>id;tipo;lib;d;t;b;h;I;J;A;c;Wt;kv;tf;tw</code>", "<b>Perfil de la biblioteca</b>: <code>tipo;perfil</code> + <code>lib;N</code> (número de <code>006_Biblioteca/perfiles.csv</code>, tablas CIRSOC): completa A, I, J... en las unidades del modelo; lo escrito a mano manda. tubo, circular, rectangular, rect_hueca, <code>canal</code>, <code>doble_t</code>, <code>te</code>, <code>z</code>, <code>angular</code> (línea media: h, b, t o tf y tw) calculan todo (h = dimensión <b>vertical</b>). <code>generica</code>: I y J obligatorios."],
                ["BARRAS", "<code>id;nodo_i;nodo_j;material;seccion;art_i;art_j</code>", "<b>art_i / art_j</b> (opcionales): vacío = rígido · <code>m</code> = articulación de flexión · <code>t</code> = de torsión · <code>mt</code> = ambas."],
                ["APOYOS", "<code>nodo;uz;phix;phiy</code>", "1 = restringido. Empotrado <code>1;1;1</code>."],
                ["RESORTES", "<code>nodo;kz;kphix;kphiy</code>", "kz [fuerza/longitud]; kphi [momento/rad]."],
                ["RESORTES GIRO INCLINADO", "<code>nodo;k;angulo</code>", "Resorte de torsión con eje en el plano a <b>angulo</b>° de +X."],
                ["CARGAS", "<code>caso;nodo;Pz;Mx;My</code>", "Ejes globales."],
                ["CARGAS EN BARRAS", "<code>caso;barra;tipo;valor;valor2;a;b</code>",
                 "<code>q</code> distribuida en z · <code>P</code> puntual en z (posición a) · <code>temp</code> gradiente: valor = ΔT fibra superior, valor2 = ΔT fibra inferior."],
                ["DESPLAZAMIENTOS PREFIJADOS", "<code>caso;nodo;uz;phix;phiy</code>", "Solo GDL restringidos."],
                ["DESAJUSTE DE RESORTES", "según plantilla", "—"],
                ["COMBINACIONES", "<code>combinacion;caso;factor</code>", "—"],
                ["SOLDADURAS / ELECTRODOS", "<code>id;barra;extremo;disposicion;electrodo;w;sy_base;lib;t_gruesa;t_fina</code> · <code>id;sut;sy;tau_adm;lib</code>", "Igual que en el 3D (ver 4c). Esfuerzos del extremo: Vz = −V, T = T, My = −M. Da <code>soldaduras.csv</code>."]]))

    # ------------------------------------------------------------------ 6 signos
    p.append("<h2>6. Signos y convenciones que hay que tener presentes</h2>")
    p.append(T(["Tema", "Convención"],
               [["Ejes globales / giro", "X →, Y ↑ (pórtico y reticulado). φ y M positivos <b>antihorarios</b>. Pórtico 3D: X, Y, Z (Z arriba), giros por regla de la mano derecha."],
                ["Axil N", "<b>Tracción positiva</b>. σ = N/A ± M·c/I."],
                ["Corte V (pórtico)", "Positivo: fuerza hacia −y<sub>l</sub> sobre la cara +x<sub>l</sub> (horario). Se dibuja hacia +y<sub>l</sub>."],
                ["Momento M (pórtico)", "Positivo: tracciona la fibra −y<sub>l</sub>. Se dibuja del lado <b>traccionado</b>. Invertir i↔j cambia solo el signo de M."],
                ["Reacciones", "Fuerza que el apoyo ejerce <b>sobre la estructura</b>, en ejes globales."],
                ["Resortes", "Fuerza = −k(u − e) sobre la estructura; el gráfico y el informe rotulan el valor y su signo global."],
                ["Cargas gravitatorias", "Negativas (Y en pórtico/reticulado, z en emparrillado)."],
                ["Ángulo de resorte inclinado", "Grados desde +X, antihorario. El eje del resorte es una recta: 30° y 210° son lo mismo."]]))

    # ------------------------------------------------------------------ 7 resortes
    p.append('<h2>7. Cómo se ven los resortes en los gráficos</h2>')
    m9 = cargar_modelo(RAIZ / "003_Ejemplos" / "002_Portico" / "ejemplo9_todos_los_resortes.csv")
    svg = graficos.fig_esquema(m9)
    p.append(f'<figure><div style="width:150mm;margin:auto">{svg}</div><figcaption>Todos los resortes disponibles '
             f'(<code>003_Ejemplos/002_Portico/ejemplo9_todos_los_resortes.csv</code>). Verde = <b>resorte (no es una barra)</b>.</figcaption></figure>')
    p.append(T(["Dibujo", "Qué es", "Cómo se carga"],
               [["Zigzag horizontal con rayado", "Resorte lineal según X", "RESORTES → <code>kx</code>"],
                ["Zigzag vertical con rayado", "Resorte lineal según Y", "RESORTES → <code>ky</code>"],
                ["Zigzag a un ángulo", "Resorte lineal inclinado", "RESORTES INCLINADOS → <code>k</code> y <code>angulo</code>"],
                ["Espiral alrededor del nodo con rayado", "Resorte torsional (giro)", "RESORTES → <code>kphi</code> (solo pórtico)"]]))
    p.append("<p>El rayado marca el extremo empotrado del resorte. Su dirección se elige del lado que menos se superpone con las barras del nodo; la dirección real del eje es la que dice el dato (X, Y o <code>angulo</code>). "
             "En el visor interactivo del informe, el tilde «apoyos» muestra u oculta apoyos y resortes.</p>")

    # ------------------------------------------------------------------ 8 recetas
    p.append('<h2>8. Recetas (cómo modelar situaciones típicas)</h2>')
    rec = [
        ("Apoyo móvil (rodillo)", "APOYOS: restringí solo el GDL que impide el rodillo. Rodillo sobre piso horizontal (pórtico): <code>N;0;1;0</code>."),
        ("Asentamiento de un apoyo", "Restringí el GDL en APOYOS y agregá en DESPLAZAMIENTOS PREFIJADOS el valor (negativo = baja). Puede ser un caso sin otras cargas y combinarlo después."),
        ("Giro prefijado", "Restringí <code>phi</code> en APOYOS y poné el giro en DESPLAZAMIENTOS PREFIJADOS (col. <code>phi</code>, en radianes)."),
        ("Apoyo elástico", "RESORTES (<code>kx</code>/<code>ky</code>/<code>kphi</code>) en el nodo. No restrinjas ese GDL en APOYOS: el resorte lo controla."),
        ("Resorte perpendicular a una barra", "RESORTES INCLINADOS con <code>angulo</code> = ángulo de la barra ± 90°. Barra a α → eje a α + 90° (si α = −53,13°, entonces 36,87°)."),
        ("Resorte estirado o corto al montarlo", "DESAJUSTE DE RESORTES con e negativo si hubo que estirarlo para conectarlo."),
        ("Articulación intermedia", "En BARRAS ponés <code>art_i</code> o <code>art_j</code> = 1 en las barras que llegan a esa articulación. Un nodo con todas las barras articuladas no tiene rigidez de giro: el programa fija φ solo."),
        ("Barra de reticulado dentro de un pórtico", "<code>art_i = 1</code> y <code>art_j = 1</code> en esa barra; sección <code>generica</code> con I pequeña (1) y A real. Tensión = N/A."),
        ("Peso propio", "<code>qgy</code> negativa por unidad de longitud de barra (peso por metro). En reticulado no hay cargas en el tramo: llevá el peso a los nudos."),
        ("Barra corta / larga (montaje forzado)", "Reticulado: <code>corta</code> o <code>larga</code> con e positivo en CARGAS EN BARRAS. Pórtico: tipo <code>dl</code> (e &gt; 0 larga, e &lt; 0 corta). Solo genera esfuerzo si la estructura es hiperestática."),
        ("Nieve / viento sobre proyección", "<code>qgyp</code> (nieve, por unidad de longitud horizontal) · <code>qgxp</code> (viento sobre paramento vertical)."),
        ("Temperatura", "Material con <code>alfa</code>. Pórtico: <code>temp</code> con ΔT de cada cara (y <b>h</b> en la sección si difieren). Reticulado: <code>temp</code> con un solo valor (ΔT uniforme). Sin hiperestaticidad no hay esfuerzo, solo deformación."),
        ("Combinar casos", "COMBINACIONES: una fila por caso con su factor. Resultados y tensiones se calculan sobre lo combinado."),
        ("Verificar que quedó bien cargado", "<code>python struttura.py archivo.csv --solo-esquema</code> y mirar numeración, apoyos y sentido de las cargas."),
    ]
    p.append(T(["Situación", "Cómo se carga"], [[a, b] for a, b in rec]))

    # ------------------------------------------------------------------ 9 resultados
    p.append("<h2>9. Qué sale y dónde mirarlo</h2>")
    p.append(T(["Archivo (carpeta <code>*_salida</code>)", "Contenido"],
               [["<code>informe.html</code>", "Memoria de cálculo imprimible: datos, resultados por caso, tensiones/CS (y pandeo), diagramas, verificación de equilibrio, anexo de matrices. Botón <b>Imprimir</b> → «Guardar como PDF»."],
                ["<code>desplazamientos.csv</code>", "Desplazamientos nodales por caso."],
                ["<code>reacciones.csv</code>, <code>resortes.csv</code>", "Reacciones de apoyo y fuerzas en resortes."],
                ["<code>esfuerzos.csv</code> / <code>barras.csv</code>", "Pórtico: N, V, M en i y j y extremos del flector · Reticulado: N, σ, ΔL, CS y pandeo por barra."],
                ["<code>tensiones.csv</code>", "Pórtico/emparrillado: tensiones máximas, Von Mises y coeficientes de seguridad."],
                ["<code>matriz_K.csv</code>", "Matriz de rigidez global ensamblada (pórtico)."]]))
    p.append("<h3>Visor del informe (igual en los cuatro programas)</h3>")
    p.append(T(["Modo", "Qué muestra"],
               [["Estructura", "Solo geometría, apoyos y rótulos."], ["Cargas", "Cargas del caso o combinación elegida."], ["Deformada", "Estructura deformada (con escala)."],
                ["Utilización", "Barras coloreadas por σeq/fy (o σeq/σadm, según «Color según»). Al pasar el mouse sobre una barra, el recuadro muestra σeq, σeq/fy y σeq/σadm en ese punto. 1 = fluencia o tensión admisible. Necesita fy o σadm en MATERIALES."],
                ["Diagramas", "Pórtico y reticulado: N, V, M · Emparrillado: V, T, M · 3D: N, Vy, Vz, T, My, Mz; el selector «Barra» muestra una sola."]]))
    p.append("<p><b>Chequeos automáticos:</b> estabilidad (avisa si hay mecanismo y qué modo), equilibrio global ΣFx, ΣFy, ΣM y residuo K·u−F. Todo debe decir <b>OK</b>.</p>")

    # ------------------------------------------------------------------ 10 errores
    p.append("<h2>10. Errores frecuentes</h2>")
    p.append(T(["Mensaje / síntoma", "Causa y solución"],
               [["«Faltan bloques obligatorios»", "Un título mal escrito o con más de una celda en la línea. El título va solo en su línea."],
                ["«faltan las columnas […]»", "Encabezado incompleto o con otro nombre. Copiá los encabezados de la plantilla."],
                ["«ERROR DE ESTRUCTURA / mecanismo»", "Faltan vínculos o hay articulaciones de más. Mirá el modo indicado, con <code>--solo-esquema</code>."],
                ["Los resultados salen «al revés»", "Signo de la carga (gravedad negativa) o nodo_i/nodo_j invertidos (cambia el signo de M local). Revisar con el esquema."],
                ["CS o tensiones aparecen «–»", "Falta <code>fy/sadm</code> en el material, o <code>c</code>/<code>A</code>/<code>I</code> en la sección."],
                ["Prefijado ignorado o error", "El GDL no está restringido en APOYOS: los prefijados solo valen sobre GDL restringidos."],
                ["Temperatura sin efecto", "Falta <code>alfa</code> en el material (o ΔT = 0)."],
                ["Reticulado: «no se verifica pandeo»", "La sección genérica no tiene <b>I</b>."],
                ["Números con coma o punto", "Usá una sola convención por archivo; con <code>;</code> se espera coma decimal, aunque el punto también se entiende."],
                ["El archivo se ve «desordenado» en Excel", "Guardar como <i>CSV UTF-8 (delimitado por comas)</i> o «CSV (MS-DOS)»; el programa lee ambos."]]))
    p.append("<p style='font-size:8pt;color:#555'>Para detalles teóricos, ver <code>004_Documentacion/002_Memorias/Struttura_Memoria_portico.html</code> y <code>004_Documentacion/002_Memorias/Struttura_Memoria_emparrillado.html</code> (emparrillado). "
             "Ejemplos resueltos y contrastados con la cátedra en <code>003_Ejemplos/</code>.</p>")
    return "\n".join(p)


def main():
    html = f"<!DOCTYPE html><html lang='es'><head><meta charset='utf-8'><title>Guía rápida de plantillas</title><style>{CSS}</style></head><body>{cuerpo()}</body></html>"
    (RAIZ / "004_Documentacion" / "001_Guia_rapida" / "Struttura_Guia_rapida.html").write_text(html, encoding="utf-8")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page()
        pg.goto((RAIZ / "004_Documentacion" / "001_Guia_rapida" / "Struttura_Guia_rapida.html").as_uri())
        pg.pdf(path=str(RAIZ / "004_Documentacion" / "001_Guia_rapida" / "Struttura_Guia_rapida.pdf"), format="A4", print_background=True, prefer_css_page_size=True)
        b.close()
    print("Guía rápida:", RAIZ / "004_Documentacion" / "001_Guia_rapida" / "Struttura_Guia_rapida.pdf")


if __name__ == "__main__":
    main()
