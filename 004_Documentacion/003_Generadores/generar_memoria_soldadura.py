"""Genera 004_Documentacion/002_Memorias/Struttura_Memoria_soldadura.html.   Ejecutar desde la raíz:  python 004_Documentacion/003_Generadores/generar_memoria_soldadura.py
La tabla sale de struttura/soldadura/fundamento.py (cada ampliación agrega sus filas ahí)."""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "001_Codigo"))

from struttura import __version__
from struttura.emparrillado.informe import tabla
from struttura.soldadura.fundamento import filas
from struttura.soldadura.grupo import DISPOSICIONES
from struttura.soldadura.informe import documento
from _esquema import Esquema


def esquema():
    e = Esquema(1000, 800)
    e.caja(350, 10, 300, 46, "Cómo se usa: soldaduras", ["¿Dónde están las cargas?"], "inicio")
    e.caja(20, 100, 470, 190, "A · Modo rápido  (esfuerzos que conocés)", [
        "tipo;soldadura  en el CSV,  o  --soldadura \"...\"",
        "Bloques a completar:",
        "  ELECTRODOS (opcional): id; sut; sy; tau_adm; lib",
        "  SOLDADURAS: id; tipo; disposicion; b; d; arcos; esp;",
        "      electrodo; w; sy_base | lib; t_gruesa; t_fina",
        "  CARGAS: soldadura; caso; N; Vy; Vz; T; My; Mz; yp; zp",
        "  (yp; zp = punto donde actúa la carga, si es excéntrica)"], "dato")
    e.caja(510, 100, 470, 190, "B · Dentro del pórtico 3D  (las cargas las da el solver)", [
        "Agregar al CSV del modelo el bloque SOLDADURAS:",
        "  id; barra; extremo (i o j); tipo; disposicion;",
        "  electrodo; w; sy_base; t_gruesa; t_fina; esp",
        "  oy; oz (opcional): posición del origen respecto del baricentro",
        "Las cargas NO se escriben: salen de los esfuerzos de la barra",
        "Circulo / rectangulo / costados / arriba_abajo toman d, b, h",
        "y espesor de la sección de la barra si no los ponés"], "dato")
    e.flecha(430, 56, 255, 100, "ya sé N, V, M, T")
    e.flecha(570, 56, 745, 100, "tengo el modelo", dx=-100)
    e.caja(20, 330, 470, 150, "Tipo de unión:  tipo = filete  (por defecto)", [
        "Cordón de filete: se verifica la garganta 0,707·w",
        "Datos: electrodo (E60 ... E120, o uno propio con tau_adm)",
        "  w (opcional): si no lo das, se calcula el w requerido",
        "  sy_base (para la tensión en el metal base)",
        "  t_gruesa; t_fina (para filete mínimo y máximo)"], "dato")
    e.caja(510, 330, 470, 150, "Tipo de unión:  tipo = tope  (penetración completa)", [
        "Garganta = espesor de la pieza (esp)",
        "Datos: electrodo (sut y sy), sy_base, esp",
        "  en el 3D, esp sale de la pared del tubo si no lo das",
        "Límites: sigma <= 0,60 Sy;  tau <= min(0,30 Sut ; 0,40 Sy base)",
        "Penetración parcial: no está"], "dato")
    e.linea(255, 290, 255, 310)
    e.linea(745, 290, 745, 310)
    e.linea(255, 310, 745, 310)
    e.flecha(255, 310, 255, 330)
    e.flecha(745, 310, 745, 330)
    e.p.append('<text x="500" y="304" font-size="11.5" font-style="italic" fill="#51626b" text-anchor="middle">en A y en B se elige el tipo</text>')
    e.caja(20, 520, 960, 112, "Disposición del cordón  (la forma; el programa evalúa todo el contorno, vos no elegís puntos)", [
        "Tubo o barra redonda:  circulo (d)    arco (d; arcos = \"centro:abertura|centro:abertura\" en grados, sin superponerse)  [propio]",
        "Tubo rectangular:  rectangulo, costados, arriba_abajo (b; d)",
        "Perfiles abiertos:  L, C, C_invertida, doble_t (b; d)    linea (d)",
        "Cualquier otra forma:  custom  (segmentos = \"y0 z0 y1 z1|y0 z0 y1 z1\", solo rectas)"], "dato")
    e.flecha(500, 480, 500, 520)
    e.caja(20, 670, 470, 110, "Resultado, filete", [
        "f máx por unidad de longitud y el punto crítico",
        "w requerido (por aporte, por base y por mínimo) y garganta",
        "CS por código y convencional; tensión en el metal base",
        "CUMPLE / NO CUMPLE con avisos"], "sal")
    e.caja(510, 670, 470, 110, "Resultado, tope", [
        "sigma máx, tau máx y sigma de Von Mises",
        "CS sigma, CS tau y CS Von Mises",
        "t requerido aproximado [propio]",
        "CUMPLE / NO CUMPLE con avisos"], "sal")
    e.flecha(255, 632, 255, 670)
    e.flecha(745, 632, 745, 670)
    return e.svg()


def cuerpo():
    p = [f"<h1>Memoria del programa de soldaduras</h1><div class='sub'>Qué se usa para calcular: fórmulas, fuente y caso de aplicación (Struttura v{__version__})</div>"]
    p.append("<h2>0. Mapa de uso</h2><p>De arriba hacia abajo: elegís cómo cargar los esfuerzos, el tipo de unión y la forma del cordón.  Las cajas amarillas son los datos que se completan; las rojizas, lo que se obtiene.  Informe: el modo rápido genera su propio <code>informe.html</code>; en el 3D la sección Soldaduras va dentro del informe del modelo.</p>" + esquema())
    p.append("<h2>1. Qué hace</h2><p>Verifica grupos de cordones de filete y uniones a tope sometidos a N, V<sub>y</sub>, V<sub>z</sub>, T, M<sub>y</sub> y M<sub>z</sub>: da la fuerza por unidad de longitud en el punto "
             "más exigido, la tensión en la garganta, el coeficiente de seguridad y el <b>pie de filete requerido</b>.  Modo rápido: <code>python struttura.py --soldadura \"circulo d=50.8 Vz=3000 My=200000 electrodo=E70 w=3\"</code> "
             "o un CSV mínimo con <code>tipo;soldadura</code> (plantilla en <code>002_Plantillas/plantilla_soldadura.csv</code>).  En el pórtico 3D, el bloque SOLDADURAS toma los esfuerzos del solver.</p>")
    p.append("<h2>2. Disposiciones</h2>" + tabla(["Nombre", "Descripción", "Parámetros", "Origen de coordenadas"],
             [[k, v[0], ", ".join(v[1]), v[2]] for k, v in DISPOSICIONES.items()],
             nota="b = medida según y; d = medida según z (como en los libros). El pie del filete se llama w (como en el Compendio)."))
    p.append("<h2>3. Fundamento de cálculo</h2>")
    p.append(tabla(["Tema", "Fórmula", "Fuente (libro, ecuación, página)", "Se aplica a"], filas(),
                   nota="Lo marcado <b>[propio]</b> no está en los libros cargados: es una decisión o extensión de este programa y debe verificarse."))
    p.append("<h2>3b. Dónde se usa y de dónde salen los datos</h2>")
    p.append("<p>El bloque SOLDADURAS se usa igual en el pórtico 3D, el pórtico plano y el emparrillado (en el reticulado no corresponde): la soldadura va en el extremo i o j de una barra y los esfuerzos salen del solver, para cada caso y combinación. "
             "Del pórtico plano se toman N, V y M; del emparrillado V, T y M; el programa los pasa a las cargas del grupo (ver «Funciones comunes» de cada Memoria) y se verifican con las mismas fórmulas de esta Memoria. "
             "<b>Electrodos:</b> se buscan por nombre en el bloque ELECTRODOS del modelo, después en <code>006_Biblioteca/electrodos.csv</code> y, si no hay biblioteca, en la tabla de Shigley que trae el programa. "
             "<b>Metal base:</b> <code>sy_base</code> a mano o <code>lib;N</code> (f<sub>y</sub> del material N de la biblioteca de materiales; lo escrito a mano manda).</p>")
    p.append("<h2>4. Casos de prueba</h2><p>Ejemplos 9-1, 9-2 y 9-4 de Shigley (con sus resultados numéricos) y las tablas de propiedades de grupos (Shigley 9-1 y 9-2; Compendio Anexo 1); "
             "ver <code>005_Tests/test_soldadura.py</code> y <code>003_Ejemplos/005_Soldadura/</code>.</p>")
    return "\n".join(p)


if __name__ == "__main__":
    salida = RAIZ / "004_Documentacion" / "002_Memorias" / "Struttura_Memoria_soldadura.html"
    salida.write_text(documento("Struttura — Memoria de soldaduras", cuerpo()), encoding="utf-8")
    print("Escrito:", salida)
