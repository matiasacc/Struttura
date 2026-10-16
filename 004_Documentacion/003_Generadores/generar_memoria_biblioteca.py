"""Genera 004_Documentacion/002_Memorias/Struttura_Memoria_biblioteca.html.   Ejecutar desde la raíz:  python 004_Documentacion/003_Generadores/generar_memoria_biblioteca.py"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "001_Codigo"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from struttura import __version__
from struttura.biblioteca.lector_fichas import PROPIEDADES
from struttura.emparrillado.informe import tabla
from struttura.soldadura.informe import documento
from _esquema import Esquema


def esquema():
    e = Esquema(1000, 600)
    e.caja(300, 10, 400, 46, "Cómo se usa: biblioteca de materiales", ["Partís de la ficha de datos de un material"], "inicio")
    e.caja(20, 100, 470, 120, "1 · Pasarle la ficha a Claude", [
        "La ficha del material en PDF (la que trae la tabla de propiedades)",
        "(o pegar el texto de la página en el chat)",
        "Una ficha por condición: laminado en frío, en caliente,",
        "templado y revenido a cada temperatura, etc."], "dato")
    e.caja(510, 100, 470, 120, "2 · Claude la anota en el CSV", [
        "Una fila por material, con un NÚMERO permanente (1, 2, 3...)",
        "Con todos los datos de la ficha y sus comentarios",
        "Nombre completo, código y fuente quedan en la fila; lo que no trae queda vacío",
        "Lo que no se interpreta queda en la columna sin_interpretar"], "dato")
    e.flecha(450, 56, 255, 100)
    e.flecha(550, 56, 745, 100)
    e.flecha(490, 160, 510, 160)
    e.caja(20, 270, 960, 80, "Biblioteca personal:  006_Biblioteca/materiales.csv   (copia de cada PDF en 006_Biblioteca/fichas/)", [
        "Se puede abrir y corregir en Excel.   python struttura.py --biblioteca listar   |   --biblioteca ver NUMERO",
        "Viene con el programa (carpeta 006_Biblioteca); son datos de terceros: respetar la licencia de la fuente de cada ficha"], "neutro")
    e.flecha(745, 220, 745, 270)
    e.caja(20, 395, 960, 135, "3 · Usarla en el modelo", [
        "Bloque MATERIALES (3D, pórtico, emparrillado, reticulado):   id;lib   →   acero;1   (1 = número en la biblioteca)",
        "La ficha completa E, G, nu, fy (= Yield) y, en el 3D, también sut y rho (los programas planos usan E, nu o G y fy)",
        "Lo que escribas a mano en una columna (e, g, nu, fy, sut, rho, ...) MANDA sobre la ficha",
        "teoria, suc y sadm no están en la ficha: se cargan a mano si se necesitan",
        "Si la ficha no trae un dato, el programa NO lo completa: lo cargás vos"], "dato")
    e.flecha(500, 350, 500, 395)
    e.caja(20, 560, 960, 36, "Resultado: valores en las unidades del modelo; el informe dice de qué ficha salieron", [], "sal")
    e.flecha(500, 530, 500, 560)
    return e.svg()


def esquema_perfiles():
    e = Esquema(1000, 330)
    e.caja(20, 10, 470, 110, "1 · Tablas de perfiles (CIRSOC 301/302)", [
        "006_Biblioteca/perfiles.csv: una fila por perfil, con NÚMERO",
        "IPN, IPB, IPE, W, HP, M, UPN, C, MC, L, T y tubos",
        "Valores como están en las tablas, con la unidad en el nombre de la columna"], "dato")
    e.caja(510, 10, 470, 110, "2 · SECCIONES del modelo", [
        "id;tipo;lib   →   viga;perfil;103   (103 = número del perfil)",
        "En el editor: «+ Agregar perfil de la biblioteca…»",
        "Lo escrito a mano en una columna manda"], "dato")
    e.flecha(490, 65, 510, 65)
    e.caja(20, 170, 960, 100, "3 · El programa convierte a la unidad de longitud del modelo y completa la sección", [
        "3D: a, iy, iz, j, cy, cz, wt      Plano / reticulado: i, a, c, h      Emparrillado: i, j, a, c, wt, h",
        "Eje fuerte del catálogo (Ix) = flexión en el plano; un dato que la tabla no trae no se completa"], "neutro")
    e.flecha(500, 120, 500, 170)
    e.caja(20, 295, 960, 32, "Resultado: la sección queda como «Perfil … (biblioteca de perfiles n.º N)» en el informe", [], "sal")
    e.flecha(500, 270, 500, 295)
    return e.svg()


def cuerpo():
    p = [f"<h1>Memoria de la biblioteca (materiales, electrodos y perfiles)</h1><div class='sub'>Qué se usa y de dónde sale cada dato (Struttura v{__version__})</div>"]
    p.append("<h2>0. Mapa de uso</h2><p>De arriba hacia abajo: le pasás la ficha a Claude, él la anota en el CSV y vos la usás por su código.  Las cajas amarillas son los datos que se completan; la rojiza, lo que se obtiene.</p>" + esquema())
    p.append("<h2>1. Qué hace</h2><p>Guarda las fichas de materiales en un CSV y le entrega al solver los datos que necesita.  <b>No inventa ni completa nada</b>: si la ficha no trae un dato (o viene como rango, por ejemplo <code>0.10 - 0.20 %</code>), el programa lo avisa y el valor se carga a mano.  "
             "Lo que no se reconoce de una ficha no se descarta: queda en la columna <code>sin_interpretar</code> y se avisa al cargarla; el PDF original se guarda en <code>006_Biblioteca/fichas</code>.</p>")
    usos = {"densidad": "rho = g/cc × 1000 [kg/m³]  (peso propio)", "E": "E = GPa × 1000 [MPa]", "G": "G = GPa × 1000 [MPa]  (torsión)", "nu": "nu (si no hay G: G = E/2(1+nu))",
            "sy": "fy [MPa]  (Tensile Strength, Yield)", "sut": "sut [MPa]  (Tensile Strength, Ultimate)"}
    filas = [[k, n.replace("[ ]?", " "), usos.get(k, "se guarda en la ficha (no lo usa el solver)")] for k, n, _ in PROPIEDADES]
    p.append("<h2>2. Qué se lee de la ficha</h2>" + tabla(["Clave", "Nombre en la ficha", "Uso"], filas,
             nota="Se toma siempre el primer valor <b>métrico</b> de la ficha.  Los comentarios de la ficha (por ejemplo «Typical for steel», «0.2% offset») quedan guardados con cada valor.  También se guardan composición química y valores según temperatura."))
    p.append("<h2>3. Fundamento</h2>" + tabla(["Tema", "Fórmula / regla", "Fuente", "Se aplica a"], [
        ["Unidades de tensión del modelo", "σ<sub>modelo</sub> = σ[MPa] · 10<sup>6</sup> · L<sub>u</sub>² / F<sub>u</sub>  (L<sub>u</sub> en m, F<sub>u</sub> en N por unidad del modelo)", "conversión de unidades", "E, G, fy, sut"],
        ["Densidad", "ρ [kg/m³] = ρ [g/cc] · 1000", "conversión de unidades", "peso propio"],
        ["Datos de las fichas", "valores típicos de la ficha, no garantizados", "ficha de cada material (columna fuente del CSV)", "todo lo cargado"],
        ["Licencia de los datos", "respetar la licencia de la fuente de cada ficha (uso propio, sin redistribuir)", "la que figura en la columna fuente del CSV", "biblioteca personal"],
        ["Numeración", "cada material tiene un número permanente: no se renumera ni se reutiliza", "[propio] criterio del programa (para que un modelo viejo no cambie de material)", "columna n, y lib en MATERIALES"],
        ["Prioridad de datos", "lo cargado a mano en MATERIALES manda sobre la ficha", "[propio] criterio del programa", "columnas e, g, nu, fy, sut, rho"],
    ]))
    p.append("<h2>4. Cargar un material a mano</h2><p>También se puede agregar una fila al final de <code>materiales.csv</code> sin pasar por Claude: el programa no necesita cambios, busca el material por su número.  "
             "Reglas: número <code>n</code> = el siguiente libre y sin repetir (el programa sigue desde el máximo que haya); columnas separadas por <code>;</code>; tensiones en MPa y densidad en kg/m³ (<code>E_MPa</code>, <code>fy_MPa</code>, <code>rho_kg_m3</code>...); "
             "las columnas que no uses quedan vacías (un dato vacío no se completa solo); un valor que no es número se marca con aviso.  En el informe aparece como «biblioteca n.º N: nombre», así que conviene poner un nombre claro.</p>")
    p.append("<h2>5. Por ahora</h2><p>La leen el pórtico espacial 3D, el pórtico plano, el emparrillado y el reticulado (columna <code>lib</code> de MATERIALES; en los planos completa E, nu o G y fy).  La soldadura toma de ella el metal base: <code>lib;N</code> en SOLDADURAS da <code>sy_base</code> = <code>fy_MPa</code> de ese material (lo escrito a mano manda).</p>")
    p.append("<h2>6. Biblioteca de electrodos</h2><p>Mismo criterio, otro archivo: <code>006_Biblioteca/electrodos.csv</code> (o el de la variable <code>STRUTTURA_ELECTRODOS</code>), con número permanente. "
             "Columnas: <code>n;id;sut_MPa;sy_MPa;tau_adm_MPa;fuente;notas</code> (MPa; un dato vacío no se completa solo; <code>tau_adm_MPa</code> es obligatorio para usar el electrodo). "
             "Viene cargada la tabla de Shigley 2024 (E60 … E120: Tabla 9-3 para S<sub>ut</sub> y S<sub>y</sub>, Tabla 9-6 cuadro A para τ<sub>adm</sub>); se agregan filas a mano o pasándole la ficha a Claude. "
             "En SOLDADURAS, <code>electrodo;E70</code> busca el nombre así: 1) bloque ELECTRODOS del modelo (a mano), 2) esta biblioteca, 3) la tabla de Shigley que trae el programa (si no existe el archivo). "
             "En ELECTRODOS, <code>lib;N</code> trae los valores de la fila N y lo escrito a mano manda. Comandos: <code>python struttura.py --biblioteca electrodos</code> y <code>--biblioteca electrodo N_O_ID</code>.</p>")
    p.append(perfiles())
    return "\n".join(p)


def perfiles():
    from collections import Counter
    from struttura.biblioteca import perfiles as pf
    filas = pf._leer()
    cont = Counter(r["familia"] for r in filas)
    nombre = {"IPN": "Doble T, alas con pendiente (IPN)", "IPB": "Doble T ala ancha, serie normal (IPB)", "IPBl": "Doble T ala ancha, serie liviana (IPBl)", "IPBv": "Doble T ala ancha, serie reforzada (IPBv)",
              "IPE": "Doble T de alas paralelas (IPE)", "W": "Doble T ala ancha, serie W", "HP": "Doble T tipo pilote (HP)", "M": "Doble T serie M", "UPN": "Canal UPN", "C": "Canal americano C",
              "MC": "Canal americano MC", "L": "Ángulo de lados iguales (L)", "T": "Te (T)", "TC": "Tubo circular", "TQ": "Tubo cuadrado", "TR": "Tubo rectangular"}
    norma = {r["familia"]: r["norma"] for r in filas}
    pag = {r["familia"]: r["fuente"].replace("Tablas CIRSOC 301/302, p. ", "") for r in filas}
    q = ["<h2>7. Biblioteca de perfiles (tablas CIRSOC)</h2>", esquema_perfiles(),
         "<p>Archivo <code>006_Biblioteca/perfiles.csv</code> (o el de la variable <code>STRUTTURA_PERFILES</code>): las tablas <i>Perfiles laminados y tubos estructurales</i> del Reglamento CIRSOC 301-EL / 302-EL, "
         "pasadas a una fila por perfil.  Los valores están <b>copiados tal cual figuran en las tablas</b> y quedan en sus unidades (mm, cm, cm², cm³, cm⁴, cm⁶, kg/m); la unidad va en el nombre de cada columna "
         "(<code>Ix_cm4</code>, <code>Ag_cm2</code>...).  El programa los pasa a la unidad de longitud del modelo al usarlos.  El PDF de origen queda en <code>006_Biblioteca/fuentes/</code> y el script que arma el CSV, "
         "en <code>001_Codigo/struttura/biblioteca/_fuente/construir_perfiles.py</code>.</p>",
         tabla(["Familia", "Descripción", "Norma", "Perfiles", "Pág. del PDF"], [[f, nombre[f], norma[f], str(cont[f]), pag[f]] for f in nombre if f in cont],
               nota=f"Total: {len(filas)} perfiles.  Los marcados con * en las tablas (racionalizados) tienen la columna <code>racionalizado</code> = *."),
         "<h3>Cómo se usa</h3><p>En SECCIONES: <code>tipo;perfil</code> y <code>lib;N</code> (N = columna <code>n</code> del CSV; el editor lo elige de un desplegable agrupado por familia).  "
         "Completa los datos de la sección y la deja como «genérica».  Lo escrito a mano en una columna manda sobre la biblioteca.  Comandos: <code>python struttura.py --biblioteca perfiles [FAMILIA]</code> y <code>--biblioteca perfil N_O_DESIGNACION</code>.</p>",
         "<h3>Qué toma cada programa</h3>" + tabla(["Programa", "Columnas de SECCIONES que completa", "Desde las tablas"], [
             ["Pórtico espacial 3D", "a, iy, iz, j, cy, cz, wt", "A<sub>g</sub>, I<sub>x</sub>, I<sub>y</sub>, J, b/2 (o la fibra más lejana), d/2 (o la fibra más lejana), C (solo tubos)"],
             ["Pórtico plano y reticulado", "i, a, c, h", "I<sub>x</sub>, A<sub>g</sub>, d/2 (o la fibra más lejana), d"],
             ["Emparrillado", "i, j, a, c, wt, h", "I<sub>x</sub>, J, A<sub>g</sub>, d/2 (o la fibra más lejana), C (solo tubos), d"]],
               nota="Un dato que la tabla no trae no se completa (queda a cargo del usuario): por ejemplo, W<sub>t</sub> en los perfiles abiertos."),
         "<h3>Ejes</h3><p>Los ejes del catálogo son x-x (horizontal, de la altura <i>d</i>) e y-y (vertical).  Se toma <b>I<sub>x</sub> (eje fuerte) como I de flexión</b> en el plano del pórtico plano y del emparrillado, "
         "y como I<sub>y</sub> del 3D (altura <i>d</i> sobre el eje local z; ancho <i>b</i> sobre el eje local y); I<sub>y</sub> del catálogo pasa a I<sub>z</sub> del 3D.  Si la barra debe flexar por el eje débil, se carga I a mano "
         "(lo escrito a mano manda) o se gira la sección con <code>giro</code> en BARRAS (3D).</p>",
         "<h3>Fibra extrema (c, cy, cz)</h3>" + tabla(["Forma", "c<sub>z</sub> (altura)", "c<sub>y</sub> (ancho)", "Fuente"], [
             ["Doble T, tubos, canal", "d/2", "b/2 (canal: máx(e, b − e), e = distancia del centro de gravedad a la cara externa del alma)", "geometría de la tabla (simetría)"],
             ["Te", "máx(d<sub>x</sub>, d − d<sub>x</sub>)", "b/2", "d<sub>x</sub> de la tabla"],
             ["Ángulo", "no se completa", "no se completa", "—"]]),
         "<h3>Ángulos [propio]</h3><p>Las tablas dan, para el ángulo, I<sub>x</sub> = I<sub>y</sub> respecto de ejes paralelos a las alas, y también los ejes principales (v-v y z-z).  El programa usa I<sub>x</sub> = I<sub>y</sub> y <b>avisa</b> en el informe que "
         "no considera la flexión asimétrica del ángulo.  Los valores principales (I<sub>v</sub>, I<sub>z</sub>) están en el CSV para cargarlos a mano si hace falta.  [propio] criterio provisorio, a decidir.</p>",
         "<h3>Revisión de los datos</h3><p>Al armar el CSV se comprobó cada fila (W<sub>x</sub> ≈ 2·I<sub>x</sub>/d, r ≈ √(I/A), peso ≈ 0,785·A<sub>g</sub>, y para tubos circulares la inercia geométrica).  Nada se corrige: lo que no cierra "
         "se anota en la columna <code>observaciones</code>.  Hoy hay dos: " + "; ".join(f"<b>{r['ref']}</b> ({r['observaciones']})" for r in filas if r["observaciones"]) + ".  Se mantienen los valores como están impresos en la tabla.</p>",
         "<h3>Límites</h3><ul><li>Solo estas tablas; no hay perfiles de otros catálogos (se agregan filas a mano o con otro PDF).</li><li>La resistencia (σ<sub>y</sub>) no está en estas tablas: sale del material.</li>"
         "<li>Los datos de torsión (J, C<sub>w</sub>) son los impresos; para perfiles abiertos el programa 3D los usa como están (torsión de Saint-Venant; el alabeo impedido se desprecia).</li>"
         "<li>Las unidades de longitud admitidas son las del programa (mm, cm, m, in, ft).</li></ul>"]
    return "\n".join(q)


if __name__ == "__main__":
    salida = RAIZ / "004_Documentacion" / "002_Memorias" / "Struttura_Memoria_biblioteca.html"
    salida.write_text(documento("Struttura — Memoria de la biblioteca (materiales, electrodos y perfiles)", cuerpo()), encoding="utf-8")
    print("Escrito:", salida)
