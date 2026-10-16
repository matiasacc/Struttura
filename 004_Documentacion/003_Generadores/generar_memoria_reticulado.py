"""Genera 004_Documentacion/002_Memorias/Struttura_Memoria_reticulado.html.   Ejecutar desde la raíz:  python 004_Documentacion/003_Generadores/generar_memoria_reticulado.py"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]  # carpeta Struttura
sys.path.insert(0, str(RAIZ / "001_Codigo"))

from struttura import __version__
from struttura.portico import graficos
from struttura.portico.informe import documento, tabla
from struttura.portico.solver import resolver
from struttura.reticulado.analisis import verificar_barras
from struttura.reticulado.entrada import cargar_modelo

EJ = RAIZ / "003_Ejemplos" / "003_Reticulado"


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;")


import sys as _s
_s.path.insert(0, str(Path(__file__).resolve().parent))
from _esquema import esquema_modelo  # noqa: E402

def esquema():
    return esquema_modelo('Cómo se usa: reticulado plano', 'plantilla_reticulado.csv', 'reticulado',
        [('NODOS', 'id; x; y'), ('MATERIALES', 'id; E; fy; sadm; alfa  |  o  id; lib   (+ rho para peso propio)'), ('SECCIONES', 'id; tipo; d; t'), ('BARRAS', 'id; nodo_i; nodo_j; material; seccion; pandeo (emp-lib, art-art, emp-art, emp-emp)'), ('APOYOS', 'nodo; ux; uy   (1 = restringido)')],
        [('CARGAS', 'caso; nodo; Px; Py   (solo en nudos)'), ('COMBINACIONES', 'combinacion; caso; factor'), ('RESORTES / RESORTES INCLINADOS', 'apoyos elásticos'), ('DESPLAZAMIENTOS PREFIJADOS', 'asentamientos de apoyo'), ('DESAJUSTE DE RESORTES', 'desajuste inicial'), ('temperatura y barra corta/larga', 'ΔT uniforme y desajuste de longitud'), ('PROYECTO: peso_propio', 'peso_propio;CASO · gravedad;-y  (necesita rho en MATERIALES)')],
        ['informe.html con visor (estructura, utilización, deformada, axiles, tensiones, CS a fluencia y pandeo)', 'desplazamientos, reacciones, barras y matriz_K (.csv)', 'resortes.csv (si hay resortes)'])


def cuerpo():
    m = cargar_modelo(EJ / "ejemplo5_cercha_con_pandeo.csv")
    res, _ = resolver(m)
    csv = esc((EJ / "ejemplo5_cercha_con_pandeo.csv").read_text(encoding="utf-8"))
    p = [f"<h1>Memoria del programa de reticulado plano</h1><div class='sub'>Método matricial de rigidez – cómo se usa y cómo funciona (Struttura v{__version__})</div>"]
    p.append("<h2>0. Mapa de uso</h2><p>De arriba hacia abajo: qué copiás, qué bloques completás (amarillo = obligatorios) y qué obtenés.  Los bloques en gris son opcionales.</p>" + esquema())
    p.append("<h2>1. Qué hace</h2><p>Resuelve reticulados planos: barras articuladas en ambos extremos que solo transmiten esfuerzo axil, con 2 grados de libertad por nodo (u<sub>x</sub>, u<sub>y</sub>). "
             "Calcula desplazamientos, reacciones, axil N de cada barra (tracción positiva), tensión σ = N/A, alargamiento, coeficientes de seguridad a fluencia y admisible y "
             "<b>pandeo de Euler</b>. Las barras son <b>bielas</b>: las cargas se aplican <b>solo en los nudos</b>; no hay cargas en el tramo ni perpendiculares a la barra. Admite además apoyos, resortes (rectos e inclinados, con desajuste), desplazamientos prefijados, temperatura uniforme, barra corta/larga (desajuste de longitud) y combinaciones.</p>")
    p.append("<h2>2. Cómo se usa</h2><p><code>python struttura.py MIARCHIVO.csv</code>; el archivo lleva <code>tipo;reticulado</code> en PROYECTO. Plantilla: <code>002_Plantillas/plantilla_reticulado.csv</code>; "
             "descripción de cada columna en <code>004_Documentacion/001_Guia_rapida/Struttura_Guia_rapida.pdf</code>. <code>--solo-esquema</code> revisa los datos sin calcular.</p>")
    p.append("<h2>3. Modelo</h2><p>Matriz de la barra en ejes globales (tabla de la cátedra), con K = AE/L, γ<sub>1</sub> = cos α, γ<sub>2</sub> = sen α:</p>"
             "<pre class='codigo'>          [  γ1²K   γ1γ2K  −γ1²K  −γ1γ2K ] [u_x^i]   [P_x^i]\n"
             "          [  γ1γ2K  γ2²K  −γ1γ2K −γ2²K  ] [u_y^i] = [P_y^i]\n"
             "          [ −γ1²K  −γ1γ2K  γ1²K   γ1γ2K ] [u_x^j]   [P_x^j]\n"
             "          [ −γ1γ2K −γ2²K   γ1γ2K  γ2²K  ] [u_y^j]   [P_y^j]</pre>"
             "<p>Internamente el archivo se convierte a un modelo de pórtico plano con todas las barras articuladas en ambos extremos; la condensación estática deja exactamente esa matriz, "
             "y el giro de los nodos (sin rigidez) se fija automáticamente. El solver, los esfuerzos y los gráficos son los del programa de pórtico, verificados contra ejercicios de la cátedra "
             "(el test compara además con un ensamblado independiente de 2 GDL por nodo).</p>")
    p.append("<h2>4. Resortes</h2><p>Los resortes <b>no son barras</b>: se dibujan en verde con forma de zigzag y un extremo empotrado rayado (lineales según X, Y o inclinados), con la leyenda «resorte (no es una barra)». "
             "Aportan k (o k·a·aᵀ si son inclinados) a la diagonal de K; con desajuste e la fuerza es −k(u − e).</p>")
    p.append("<h2>5. Pandeo</h2>")
    p.append(tabla(["Vínculos (código)", "P<sub>c</sub>"], [["empotrado–libre (<code>emp-lib</code>)", "π²EI/(4L²)"], ["articulado–articulado (<code>art-art</code>)", "π²EI/L²"],
                                                  ["empotrado–articulado (<code>emp-art</code>)", "2π²EI/L²  (tabla de la cátedra)"], ["empotrado–empotrado (<code>emp-emp</code>)", "4π²EI/L²"]]))
    p.append("<p>CS pandeo = P<sub>c</sub>/|N| en barras comprimidas (N mínimo de la barra). I es el momento de inercia respecto del eje débil. La esbeltez λ = KL/r se informa a modo indicativo: "
             "Euler es válido para barras esbeltas; para barras cortas la falla es por fluencia/pandeo inelástico y no está cubierta.</p>")
    p.append("<h2>6. Ejemplo: cercha triangular con pandeo</h2>")
    p.append(f"<pre class='codigo'>{csv}</pre>")
    vb = verificar_barras(m, res["TOTAL"])
    p.append(tabla(["Barra", "N", "Estado", "σ", "CS fluencia", "P<sub>c</sub>", "CS pandeo"],
                   [[d["barra"].id, f"{d['N']:.5g}", d["estado"], f"{d['sigma']:.4g}", f"{d['n_fy']:.3g}" if d["n_fy"] else "–",
                     f"{d['Pc']:.5g}" if d["Pc"] else "–", f"{d['n_pand']:.3g}" if d["n_pand"] else "–"] for d in vb],
                   num=(1, 3, 4, 5, 6), nota="Combinación TOTAL (V + W), unidades N y mm."))
    p.append(f"<figure>{graficos.fig_esquema(m, res['TOTAL'].F, res['TOTAL'].cb)}<figcaption>Cercha del ejemplo con las cargas de la combinación.</figcaption></figure>")
    p.append("<h2>7. Verificaciones</h2><ul class='conv'><li>Los cuatro ejercicios resueltos de Brewer (carga nodal; desplazamiento prefijado; barra corta + ΔT + prefijado; resorte + barra larga + ΔT + prefijado).</li>"
             "<li>Triángulo simétrico con carga en el vértice: N por estática.</li><li>Ensamblado independiente de 2 GDL con la tabla de la cátedra.</li>"
             "<li>Cargas críticas de la tabla; resortes inclinados y prefijados; equilibrio global.</li></ul><p>Todo en <code>tests/test_reticulado.py</code>.</p>")
    p.append("<h2>8. Supuestos y limitaciones</h2><ul class='conv'><li>Lineal, pequeños desplazamientos; barras articuladas con cargas solo en los nudos (más ΔT y desajuste de longitud, que no flexan la barra).</li>"
             "<li>Un solo momento de inercia por sección (eje débil informado por el usuario); sin pandeo inelástico.</li>"
             "<li>Estructuras con barras rígidas y de reticulado a la vez: usar el programa de pórtico con <code>art_i = art_j = 1</code> en las barras de reticulado.</li></ul>")
    from _comun import seccion_comun
    p.append(seccion_comun("reticulado"))
    return "\n".join(p)


if __name__ == "__main__":
    salida = RAIZ / "004_Documentacion" / "002_Memorias" / "Struttura_Memoria_reticulado.html"
    salida.write_text(documento("Memoria del programa – Reticulado plano", cuerpo(), boton=True), encoding="utf-8")
    print("Escrito:", salida)
