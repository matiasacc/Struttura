"""Genera 004_Documentacion/002_Memorias/Struttura_Memoria_editor.html.   Ejecutar desde la raíz:  python 004_Documentacion/003_Generadores/generar_memoria_editor.py"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "001_Codigo"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from struttura import __version__
from struttura.editor.esquema import ESQUEMAS
from struttura.emparrillado.informe import tabla
from struttura.soldadura.informe import documento
from _esquema import Esquema


def esquema():
    e = Esquema(1000, 640)
    e.caja(300, 10, 400, 46, "Cómo se usa: editor visual de modelos", ["python struttura.py --editor [modelo.csv]"], "inicio")
    e.caja(20, 90, 300, 110, "1 · Abrir o crear", [
        "Nuevo ▾: elegís el tipo de estructura",
        "Abrir: cualquier CSV de Struttura",
        "(sus comentarios y columnas extra se conservan)"], "dato")
    e.caja(350, 90, 300, 110, "2 · Cargar en orden", [
        "Barra de pasos: Proyecto, Nodos, Materiales,",
        "Secciones, Barras, Apoyos, Cargas...",
        "Cada columna tiene su ayuda y sus opciones"], "dato")
    e.caja(680, 90, 300, 110, "3 · Dibujar", [
        "Herramientas: nodo, barra, apoyo, carga,",
        "carga en tramo, borrar; arrastrar nodos",
        "El dibujo y las tablas son el mismo modelo"], "dato")
    e.flecha(500, 56, 170, 90); e.flecha(500, 56, 500, 90); e.flecha(500, 56, 830, 90)
    e.caja(20, 250, 960, 80, "Revisar (se hace solo al editar): carga el modelo con el programa real", [
        "Marca el bloque y la fila con error y muestra los avisos; mientras haya errores no se puede calcular"], "calc")
    e.flecha(500, 200, 500, 250)
    e.caja(20, 380, 470, 100, "4 · Guardar / Guardar como…", [
        "Escribe el CSV (separador ;) en la carpeta que elijas",
        "Ctrl+S guarda · Ctrl+Mayús+S guarda como",
        "Deshacer / rehacer: Ctrl+Z / Ctrl+Y"], "neutro")
    e.caja(510, 380, 470, 100, "5 · Calcular (F5)", [
        "Guarda y corre el mismo cálculo que la línea de comandos",
        "El informe.html se abre en el navegador",
        "Carpeta <modelo>_salida/ igual que siempre"], "sal")
    e.flecha(300, 330, 255, 380); e.flecha(700, 330, 745, 380)
    e.caja(20, 530, 960, 70, "El CSV sigue siendo la fuente de verdad", [
        "Se puede seguir editando a mano o desde el editor, indistintamente; el editor no cambia los resultados"], "neutro")
    return e.svg()


def cuerpo():
    p = [f"<h1>Memoria del editor visual</h1><div class='sub'>Cómo cargar los modelos sin escribir el CSV a mano (Struttura v{__version__})</div>"]
    p.append("<h2>0. Mapa de uso</h2><p>De arriba hacia abajo.  Amarillo: lo que cargás; verde: la comprobación; rojizo: lo que se obtiene.</p>" + esquema())
    p.append("<h2>1. Qué es</h2><p>Una página que corre en tu computadora (servidor local en <code>127.0.0.1</code>, puerto al azar, con una clave por sesión) y se abre en el navegador.  "
             "No es un CAD: es el mismo archivo CSV de siempre con tablas guiadas y un dibujo del modelo.  <b>No agrega ni cambia ningún cálculo</b>: Calcular llama al mismo despachador que la línea de comandos.  "
             "No usa internet ni librerías externas.</p>")
    p.append("<h2>2. Qué se puede cargar</h2><p>Todo lo que admite el CSV.  Hay un esquema por tipo con cada bloque y cada columna (tipo de dato, opciones, ayuda), y un test que lo compara contra los cargadores del programa: "
             "si el cargador acepta una columna, el editor tiene dónde ponerla.</p>")
    filas = [[s["nombre"], s["tipo"], {0: "tablas (sin dibujo)", 2: "dibujo 2D (vista fija)", 3: "dibujo 3D (se gira)"}[s["dim"]], len(s["bloques"]), sum(len(b["cols"]) for b in s["bloques"])] for s in ESQUEMAS.values()]
    p.append(tabla(["Tipo", "Clave", "Vista", "Bloques", "Columnas"], filas))
    p.append("<h2>3. Dibujo</h2>" + tabla(["Herramienta", "Atajo", "Qué hace"], [
        ["Seleccionar", "V", "elige nodo o barra (se edita en el inspector); arrastrar un nodo lo mueve"],
        ["Nodo", "N", "crea un nodo en la posición del mouse (con paso e imán a nodos)"],
        ["Barra", "B", "clic en un nodo y luego en otro; si no hay nodo bajo el mouse lo crea"],
        ["Apoyo", "A", "pone el tipo elegido (empotrado, articulado, etc.) o lo quita"],
        ["Carga", "C", "carga nodal con el caso y los valores elegidos"],
        ["Carga en tramo", "L", "carga en una barra (tipo, valor, posición según el tipo)"],
        ["Borrar", "X / Supr", "borra el elemento y lo que dependía de él (barras, apoyos, cargas)"],
        ["Vista", "—", "Ajustar (doble clic); en 3D: Iso, Planta, Frente, Lado y giro con el mouse"],
    ], nota="En 3D un clic cae en el plano de trabajo (x, y o z = valor) elegido en la barra de herramientas.  Las unidades y los signos son los del modelo: el editor no convierte nada."))
    p.append("<h2>4. Reglas del archivo</h2>" + tabla(["Tema", "Regla"], [
        ["Fidelidad", "al abrir y guardar se conservan comentarios, columnas desconocidas y el orden de bloques; los valores se guardan como texto, tal cual se escribieron"],
        ["Separador y decimal", "se guarda con <code>;</code>; el decimal (coma o punto) es el que ya usa el archivo, y coma si es nuevo"],
        ["Columnas", "se agregan solo las que el cargador exige o las que se usan; las vacías no se completan"],
        ["Renombrar", "cambiar el id de un nodo, material o sección actualiza las barras, apoyos y cargas que lo usan"],
        ["Revisión", "usa el cargador real sobre una copia temporal; señala bloque y fila del error"],
        ["Modo soldaduras", "solo tablas (ELECTRODOS, SOLDADURAS, CARGAS); no tiene estructura para dibujar"],
    ]))
    p.append("<h2>5. Nombres, desplegables y biblioteca</h2>" + tabla(["Tema", "Cómo se ve en el editor"], [
        ["Nombres", "cada columna lleva un nombre claro y su unidad según las unidades del proyecto (por ejemplo «Módulo de elasticidad E [N/mm²]»); el nombre que usa el CSV queda en letra chica debajo"],
        ["Opciones", "las opciones también tienen nombre (por ejemplo «Rectangular hueca» en lugar de <code>rect_hueca</code>); en el archivo se guarda el valor de siempre"],
        ["Materiales", "la primera columna es el <b>material de la biblioteca</b> (desplegable); «+ Agregar material de la biblioteca» agrega la fila lista.  Las celdas vacías muestran en azul el valor de la biblioteca; lo que se escribe a mano manda"],
        ["Secciones (perfiles)", "el tipo <b>Perfil de la biblioteca</b> y la columna «Perfil de la biblioteca» (desplegable agrupado por familia: IPN, IPE, W, UPN, ángulos, tes, tubos…); «+ Agregar perfil de la biblioteca» agrega la sección lista, con el nombre del perfil.  A, I, J… salen en azul en las celdas vacías, en las unidades del modelo; lo escrito a mano manda"],
        ["Electrodos", "igual que los materiales; en SOLDADURAS el electrodo se elige entre los del modelo, la biblioteca y la tabla de Shigley"],
        ["Referencias", "nodo, barra, material, sección y electrodo se eligen de un desplegable con «id: detalle» (coordenadas, nodos de la barra, nombre del material, forma y medidas de la sección)"],
        ["Secciones", "cada forma muestra solo las medidas que usa (tomado de los cargadores); «Mostrar todas las columnas» las muestra todas"],
        ["Apoyos", "cada movimiento es un botón <b>Fijo</b> (vale 0) o <b>Libre</b>; una columna «Tipo de apoyo» completa todo de una vez (Empotrado, Articulado...)"],
        ["Articulaciones", "se eligen por nombre (Rígida, Articulada, Rótula esférica, Libera My...)"],
        ["Enter", "acepta lo escrito; en las tablas pasa a la celda de abajo"],
        ["Nodos repetidos", "no se crean dos nodos en el mismo punto; si el archivo los trae, el estado avisa y «Unir» los junta"],
        ["Guardar como", "comprueba que el archivo quedó escrito, muestra la ruta completa y tiene «Abrir carpeta» y «Copiar ruta»"],
    ]))
    p.append("<h2>6. Límites</h2><p>En 3D se edita con el plano de trabajo y las tablas; no hay selección por ventana ni copiar/pegar de elementos.  "
             "Probado con Chrome (Chromium); en Edge debería funcionar igual.  La comodidad de uso no se pudo evaluar sin una persona usándolo: las correcciones de interfaz se hacen con tu experiencia.  "
             "Pendiente por decisión: cargas de temperatura 3D, resortes inclinados, falta de ajuste de resortes (también faltan en el CSV).</p>")
    p.append("<h2>7. Cómo se verifica</h2><p><code>005_Tests/test_editor.py</code>: esquema contra los cargadores; idas y vueltas del CSV de todos los ejemplos con resultados idénticos; servidor (abrir, revisar, guardar, calcular, clave); "
             "y la página con un navegador real: modelos armados con el mouse (pórtico, emparrillado, reticulado, pórtico 3D) dan resultados <b>idénticos byte a byte</b> a los CSV escritos a mano.</p>")
    return "\n".join(p)


if __name__ == "__main__":
    salida = RAIZ / "004_Documentacion" / "002_Memorias" / "Struttura_Memoria_editor.html"
    salida.write_text(documento("Struttura — Memoria del editor visual", cuerpo()), encoding="utf-8")
