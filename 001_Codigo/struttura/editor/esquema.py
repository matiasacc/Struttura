"""Esquema único del editor: para cada tipo de estructura, sus bloques, columnas, tipos de dato, valores permitidos y ayuda.

El editor arma sus formularios con este esquema.  Un test compara estos nombres con los que acepta cada cargador de
datos (`_COLUMNAS` y `TITULOS` de cada programa), de modo que no puede quedar una columna del CSV sin su lugar en la interfaz.

Tipos de dato de una columna:  txt (texto libre) | num (número; coma o punto) | opc (una de las opciones, o vacío) |
flag (1 = sí, vacío = no) | ref:<lista> (identificador de otra tabla: nodos, barras, materiales, secciones, casos, electrodos, soldaduras).
Las ayudas describen lo que el programa hace con el dato; no agregan criterios."""
from __future__ import annotations

UF = ["N", "kN", "MN", "kgf", "tf", "lbf", "kip"]
UL = ["mm", "cm", "m", "in", "ft"]
TEORIAS = ["vm", "tresca", "rankine", "mohr", "mohrmod"]
PANDEO = ["art-art", "emp-lib", "emp-art", "emp-emp"]
SECC_BASE = ["generica", "tubo", "circular", "rectangular", "rect_hueca"]
SECC_PARED = ["canal", "doble_t", "te", "z", "angular"]
DISPOSICIONES = ["circulo", "arco", "rectangulo", "costados", "arriba_abajo", "linea", "L", "C", "C_invertida", "doble_t", "custom"]


def C(n, t="txt", ay="", op=None, ob=False, **kw):
    d = {"n": n, "t": t, "ay": ay, "ob": ob}
    if op:
        d["op"] = list(op)
    d.update(kw)
    return d


def bloque(titulo, cols, ay, ob=False, k="tabla", min=None, **kw):
    """min = columnas que el cargador exige en el encabezado; el resto se escribe solo si ya estaba o tiene datos (None = se escriben todas)."""
    return {"t": titulo, "k": k, "ob": ob, "ay": ay, "cols": cols, "min": min, **kw}


# ----------------------------------------------------------------------------------------------------------------------
# Piezas comunes
# ----------------------------------------------------------------------------------------------------------------------
def proyecto(tipo, gravedad, defecto_grav, con_corte=True, soldadura=False):
    cols = [C("proyecto", "txt", "Nombre del proyecto (aparece en el informe)"),
            C("autor", "txt", "Autor (opcional)"),
            C("tipo", "opc", "Tipo de estructura; define el programa que calcula", [tipo], fijo=True, d=tipo),
            C("unidad_fuerza", "opc", "Unidad de fuerza de todo el modelo", UF, d="N"),
            C("unidad_longitud", "opc", "Unidad de longitud de todo el modelo", UL, d="mm")]
    if soldadura:
        return bloque("PROYECTO", cols, "Datos generales del archivo.", ob=True, k="claves")
    cols += [C("escala_deformada", "txt", "Factor de amplificación de la deformada en el dibujo; «auto» (o vacío) lo elige el programa", d="auto"),
             C("csv_salida", "opc", "Formato de los CSV de resultados: excel_es (coma decimal, para Excel en español) o estandar", ["excel_es", "estandar"], d="excel_es"),
             C("anexo_matrices", "opc", "Anexo del informe con las matrices de rigidez (si / no / auto)", ["si", "no", "auto"], d="si"),
             C("escala_diagramas", "opc", "Escala de los diagramas V, T, M: cada barra con la suya (barra) o una única (global)", ["barra", "global"], d="barra"),
             C("peso_propio", "ref:casos", "Nombre del caso al que se suma el peso propio de todas las barras (usa rho del material); vacío = sin peso propio"),
             C("gravedad", "opc", "Dirección de la gravedad en ejes globales (para el peso propio)", gravedad, d=defecto_grav)]
    if con_corte:
        cols.insert(6, C("corte_tensiones", "opc", "Incluir la tensión de corte en el cálculo de tensiones (si / no)", ["si", "no"], d="si"))
    return bloque("PROYECTO", cols, "Datos generales del archivo: unidades, opciones del informe y peso propio.", ob=True, k="claves")


def materiales(g=False, tension=True, ext=True):
    cols = [C("id", "txt", "Nombre del material (lo usa BARRAS)", ob=True),
            C("e", "num", "Módulo de elasticidad E [fuerza/longitud²]")]
    if g:
        cols.append(C("g", "num", "Módulo de corte G (alternativa a nu)"))
    cols += [C("nu", "num", "Coeficiente de Poisson" + (" (alternativa a G)" if g else "")),
             C("fy", "num", "Tensión de fluencia [fuerza/longitud²]"),
             C("sadm", "num", "Tensión admisible (alternativa a fy para el coeficiente de seguridad)"),
             C("alfa", "num", "Coeficiente de dilatación térmica [1/°C] (cargas de temperatura)")]
    if ext:
        cols += [C("sut", "num", "Tensión de rotura a tracción (criterios Rankine y Mohr)"),
                 C("suc", "num", "Tensión de rotura a compresión (criterios Mohr; en frágiles)"),
                 C("teoria", "opc", "Criterio de falla: vm = Von Mises, tresca, rankine, mohr, mohrmod = Mohr modificado (sin dato: vm si hay fy; rankine si solo hay sut)", TEORIAS)]
    cols += [C("rho", "num", "Densidad [kg/m³] (peso propio)"),
             C("lib", "txt", "N.º de la biblioteca de materiales (006_Biblioteca/materiales.csv): completa lo que no se escribió acá", lista="lib_materiales")]
    return bloque("MATERIALES", cols, "Propiedades del material.  Lo escrito a mano manda sobre la biblioteca (lib).", ob=True, min=["id"])


def secciones(tipos, extra):
    cols = [C("id", "txt", "Nombre de la sección (lo usa BARRAS)", ob=True),
            C("tipo", "opc", "Tipo de sección; define qué columnas se usan", ["perfil"] + tipos, ob=True),
            C("lib", "txt", "N.º del perfil de la biblioteca (006_Biblioteca/perfiles.csv): completa A, I, J... lo que no se escribió acá", lista="lib_perfiles")] + extra
    return bloque("SECCIONES", cols, "Secciones transversales.  Con el tipo «perfil» se elige un perfil de la biblioteca (tablas CIRSOC); los de pared delgada usan dimensiones de línea media.", ob=True, min=["id", "tipo"])


def combinaciones():
    return bloque("COMBINACIONES", [C("combinacion", "txt", "Nombre de la combinación", ob=True),
                                    C("caso", "ref:casos", "Caso que entra en la combinación", ob=True),
                                    C("factor", "num", "Factor que multiplica al caso", ob=True)],
                  "Combinaciones de casos: una fila por caso que interviene.")


def electrodos():
    return bloque("ELECTRODOS", [C("id", "txt", "Nombre del electrodo (lo usa SOLDADURAS)", ob=True),
                                 C("sut", "num", "Resistencia a la tracción del aporte [fuerza/longitud²]"),
                                 C("sy", "num", "Fluencia del aporte"),
                                 C("tau_adm", "num", "Corte admisible en la garganta (obligatorio, a mano o con lib)"),
                                 C("lib", "txt", "N.º de la biblioteca de electrodos (006_Biblioteca/electrodos.csv)", lista="lib_electrodos")],
                  "Electrodos propios; si el nombre no está acá se busca en la biblioteca y después en la tabla de Shigley.", min=["id"])


def soldaduras_modelo():
    return bloque("SOLDADURAS", [C("id", "txt", "Nombre de la soldadura", ob=True),
                                 C("tipo", "opc", "filete (método de la garganta) o tope", ["filete", "tope"], d="filete"),
                                 C("esp", "num", "Espesor de las piezas (en tope es la garganta)"),
                                 C("barra", "ref:barras", "Barra donde está el cordón", ob=True),
                                 C("extremo", "opc", "Extremo de la barra: i o j", ["i", "j"], ob=True),
                                 C("disposicion", "opc", "Forma del grupo de cordones", DISPOSICIONES, ob=True),
                                 C("b", "num", "Medida horizontal (según y) de la disposición"),
                                 C("d", "num", "Medida vertical (según z) o diámetro"),
                                 C("arcos", "txt", "Solo «arco»: centro:abertura|centro:abertura en grados"),
                                 C("segmentos", "txt", "Solo «custom»: segmentos propios"),
                                 C("oy", "num", "Desplazamiento del origen de la disposición respecto del baricentro (y)"),
                                 C("oz", "num", "Ídem (z)"),
                                 C("electrodo", "ref:electrodos", "Electrodo (ELECTRODOS, biblioteca o tabla interna)", ob=True, lista="nombres_electrodos"),
                                 C("w", "num", "Pie del filete adoptado; vacío = el programa calcula el requerido"),
                                 C("sy_base", "num", "Fluencia del metal base"),
                                 C("lib", "txt", "N.º de material de la biblioteca: toma de ahí sy_base", lista="lib_materiales"),
                                 C("t_gruesa", "num", "Espesor de la pieza más gruesa (pie mínimo, Tabla 9-6 B)"),
                                 C("t_fina", "num", "Espesor de la pieza más fina (aviso si el pie lo supera)")],
                  "Cordones de soldadura en los extremos de las barras; los esfuerzos salen del solver, para cada caso y combinación.", min=["id", "barra", "extremo", "disposicion", "electrodo"])


ART_3D = "Articulación: 1 = rótula esférica; o my / mz / t, combinables con «+» (ej.: my+t); vacío = rígido"


def barras(dim, art, rot=False, pandeo=True):
    cols = [C("id", "txt", "Nombre de la barra", ob=True),
            C("nodo_i", "ref:nodos", "Nodo inicial", ob=True), C("nodo_j", "ref:nodos", "Nodo final", ob=True),
            C("material", "ref:materiales", "Material (MATERIALES)", ob=True), C("seccion", "ref:secciones", "Sección (SECCIONES)", ob=True)]
    if rot:
        cols += [C("rx", "num", "Vector de referencia: hacia dónde apunta z local (en globales); necesita rx, ry y rz"),
                 C("ry", "num", "Ídem (y)"), C("rz", "num", "Ídem (z)"),
                 C("giro", "num", "Giro de la sección alrededor del eje de la barra [grados]")]
    if art:
        cols += [dict(C("art_i", art["t"], art["ay"] + " (extremo i)", art.get("op")), **({} if "op" in art else {})),
                 C("art_j", art["t"], art["ay"] + " (extremo j)", art.get("op"))]
    if pandeo:
        cols.append(C("pandeo", "opc", "Condición de extremos para el pandeo de Euler (defecto art-art): K = 1, 2, 1/√2, 1/2", PANDEO, d="art-art"))
    cols.append(C("suprimida", "flag", "Barra suprimida: queda en el archivo pero no entra al cálculo (sus cargas, soldaduras y puntos de tensión tampoco). "
                  "Para reemplazarla por su rigidez, poner un resorte en el nodo (botón «Calcular k de una barra»)"))
    return bloque("BARRAS", cols, "Barras: de un nodo a otro, con su material y su sección.", ob=True, min=["id", "nodo_i", "nodo_j", "material", "seccion"])


def nodos(ejes):
    return bloque("NODOS", [C("id", "txt", "Nombre del nodo", ob=True)] + [C(e, "num", f"Coordenada {e}", ob=True) for e in ejes],
                  "Puntos de la estructura.", ob=True)


def apoyos(cols, ay):
    return bloque("APOYOS", [C("nodo", "ref:nodos", "Nodo apoyado", ob=True)] + [C(n, "flag", t) for n, t in cols], ay, ob=True)


PC_AY = ("Carga crítica de pandeo de la barra que este resorte reemplaza (opcional; la calcula el botón «Calcular k de una barra»). "
         "El informe da CS pandeo = Pc/|F del resorte|; con pc la fila debe tener un solo resorte lineal")


def resortes(cols):
    return bloque("RESORTES", [C("nodo", "ref:nodos", "Nodo con resorte", ob=True)] + [C(n, "num", t) for n, t in cols] + [C("pc", "num", PC_AY)],
                  "Resortes elásticos en el nodo; rigidez en fuerza/longitud o momento/giro.")


def resortes_incl(giro=False):
    return bloque("RESORTES GIRO INCLINADO" if giro else "RESORTES INCLINADOS",
                  [C("nodo", "ref:nodos", "Nodo con resorte", ob=True), C("k", "num", "Rigidez del resorte", ob=True),
                   C("angulo", "num", "Ángulo del eje del resorte respecto de +X [grados]", ob=True)] + ([] if giro else [C("pc", "num", PC_AY)]),
                  "Resorte cuyo eje forma un ángulo con +X.")


def resortes_incl3d():
    return bloque("RESORTES INCLINADOS",
                  [C("nodo", "ref:nodos", "Nodo con resorte", ob=True), C("k", "num", "Rigidez del resorte (fuerza/longitud)", ob=True),
                   C("dx", "num", "Dirección del resorte: componente en x (vector; se normaliza)"), C("dy", "num", "Dirección del resorte: componente en y"),
                   C("dz", "num", "Dirección del resorte: componente en z"),
                   C("ax", "num", "Ángulo del resorte con el eje X [grados]"), C("ay", "num", "Ángulo del resorte con el eje Y [grados]"),
                   C("az", "num", "Ángulo del resorte con el eje Z [grados]"), C("pc", "num", PC_AY)],
                  "Resorte lineal a tierra en una dirección cualquiera.  Dar la dirección con el vector (dx; dy; dz) o con los ángulos que forma con X, Y, Z "
                  "(con dos ángulos alcanza: el tercero se calcula).  Se pueden poner varios resortes en un nodo.", min=["nodo", "k"])


def cargas(cols, ay):
    return bloque("CARGAS", [C("caso", "ref:casos", "Nombre del caso de carga", ob=True), C("nodo", "ref:nodos", "Nodo cargado", ob=True)]
                  + [C(n, "num", t) for n, t in cols], ay)


def prefijados(cols):
    return bloque("DESPLAZAMIENTOS PREFIJADOS", [C("caso", "ref:casos", "Caso", ob=True), C("nodo", "ref:nodos", "Nodo", ob=True)]
                  + [C(n, "num", t) for n, t in cols], "Desplazamientos impuestos en nodos restringidos (asentamientos).")


# ----------------------------------------------------------------------------------------------------------------------
# Esquemas por tipo
# ----------------------------------------------------------------------------------------------------------------------
def _sec_plana(giro_j):
    ex = [C("d", "num", "Diámetro exterior (tubo, circular)"), C("t", "num", "Espesor de pared (tubo, rect_hueca, perfiles de pared delgada)"),
          C("b", "num", "Ancho (rectangular, rect_hueca, pared delgada)"), C("h", "num", "Altura, en el plano de flexión"),
          C("i", "num", "Inercia a flexión (genérica)")]
    if giro_j:
        ex.append(C("j", "num", "Constante de torsión (genérica)"))
    ex += [C("a", "num", "Área (genérica)"), C("c", "num", "Distancia del eje neutro a la fibra extrema (genérica)")]
    if giro_j:
        ex.append(C("wt", "num", "Módulo resistente a torsión (genérica)"))
    ex += [C("kv", "num", "Factor de corte: τ = kv·V/A (genérica)"),
           C("tf", "num", "Espesor de ala (doble_t, te, z)"), C("tw", "num", "Espesor de alma (doble_t, te, z)")]
    return ex


def esquema_portico3d():
    sec = [C("a", "num", "Área (genérica)"), C("iy", "num", "Inercia para flexión alrededor de y local (genérica)"),
           C("iz", "num", "Inercia para flexión alrededor de z local (genérica)"), C("j", "num", "Constante de torsión (genérica)"),
           C("cy", "num", "Distancia a la fibra extrema en y (genérica)"), C("cz", "num", "Distancia a la fibra extrema en z (genérica)"),
           C("wt", "num", "Módulo resistente a torsión (genérica)"),
           C("d", "num", "Diámetro exterior (tubo, circular)"), C("t", "num", "Espesor de pared"),
           C("b", "num", "Ancho (según y local)"), C("h", "num", "Altura (según z local)"),
           C("tf", "num", "Espesor de ala (pared delgada)"), C("tw", "num", "Espesor de alma (pared delgada)")]
    g6 = [("ux", "Restringe el desplazamiento en x"), ("uy", "Restringe el desplazamiento en y"), ("uz", "Restringe el desplazamiento en z"),
          ("phix", "Restringe el giro alrededor de x"), ("phiy", "Restringe el giro alrededor de y"), ("phiz", "Restringe el giro alrededor de z")]
    k6 = [("kx", "Rigidez en x"), ("ky", "Rigidez en y"), ("kz", "Rigidez en z"), ("kphix", "Rigidez de giro alrededor de x"),
          ("kphiy", "Rigidez de giro alrededor de y"), ("kphiz", "Rigidez de giro alrededor de z")]
    from_cargas = [("fx", "Fuerza en x global"), ("fy", "Fuerza en y global"), ("fz", "Fuerza en z global"),
                   ("mx", "Momento alrededor de x"), ("my", "Momento alrededor de y"), ("mz", "Momento alrededor de z")]
    tipos_q = ["qx", "qy", "qz", "qgx", "qgy", "qgz", "Px", "Py", "Pz", "Pgx", "Pgy", "Pgz", "Mx", "My", "Mz", "Mgx", "Mgy", "Mgz"]
    cb = bloque("CARGAS EN BARRAS", [C("caso", "ref:casos", "Caso", ob=True), C("barra", "ref:barras", "Barra cargada", ob=True),
                                     C("tipo", "opc", "q = distribuida, P = puntual, M = momento; x y z = ejes LOCALES, gx gy gz = ejes GLOBALES", tipos_q, ob=True),
                                     C("valor", "num", "Distribuida: valor en i (o uniforme).  Puntual / momento: su valor", ob=True),
                                     C("valor2", "num", "Distribuida: valor en j; vacío = uniforme"),
                                     C("a", "num", "Puntual / momento: distancia desde el nodo i")],
                "Cargas en el tramo de las barras (distribuidas, puntuales, momentos).", min=["caso", "barra", "tipo", "valor"])
    pt = bloque("PUNTOS DE TENSION", [C("id", "txt", "Nombre del punto", ob=True), C("barra", "ref:barras", "Barra", ob=True),
                                      C("x", "num", "Posición a lo largo de la barra desde i", ob=True), C("y", "num", "Coordenada y local en la sección"),
                                      C("z", "num", "Coordenada z local en la sección"), C("caso", "ref:casos", "Caso o combinación", ob=True)],
                "Puntos donde se pide el tensor de tensiones (además de los críticos automáticos).", min=["barra", "x"])
    return {"tipo": "portico3d", "nombre": "Pórtico espacial (3D)", "dim": 3, "ejes": ["x", "y", "z"],
            "geo": {"apoyos": [c[0] for c in g6], "cargas": [c[0] for c in from_cargas], "resortes": [c[0] for c in k6], "fuerzas": ["fx", "fy", "fz"], "momentos": ["mx", "my", "mz"]},
            "bloques": [proyecto("portico3d", ["-z", "+z", "-x", "+x", "-y", "+y"], "-z"),
                        nodos(["x", "y", "z"]), materiales(g=True),
                        secciones(SECC_BASE + SECC_PARED, sec),
                        barras(3, {"t": "opc", "ay": ART_3D, "op": ["1", "my", "mz", "t", "my+t", "mz+t", "my+mz+t"]}, rot=True),
                        apoyos(g6, "Apoyos: 1 = restringido, vacío = libre."), resortes(k6), resortes_incl3d(),
                        cargas(from_cargas, "Cargas en nodos, en ejes globales."), cb, prefijados([(a, b) for a, b in g6]),
                        combinaciones(), pt, soldaduras_modelo(), electrodos()]}


def _cb_plano(tipos, ay_tipo):
    return bloque("CARGAS EN BARRAS", [C("caso", "ref:casos", "Caso", ob=True), C("barra", "ref:barras", "Barra cargada", ob=True),
                                       C("tipo", "opc", ay_tipo, tipos, ob=True),
                                       C("valor", "num", "Distribuida: valor en a (o uniforme).  Puntual: su valor.  temp: ΔT de la cara +y local", ob=True),
                                       C("valor2", "num", "Distribuida: valor en b.  temp: ΔT de la cara −y local"),
                                       C("a", "num", "Distribuida: inicio del tramo.  Puntual: posición.  (desde el nodo i)"),
                                       C("b", "num", "Distribuida: fin del tramo (vacío = hasta j)")],
                  "Cargas en el tramo de las barras.", min=["caso", "barra", "tipo", "valor"])


def esquema_portico():
    art = {"t": "flag", "ay": "Articulación (M = 0)"}
    tipos = ["q", "qa", "qgx", "qgy", "qgxp", "qgyp", "P", "Pa", "Pgx", "Pgy", "Mp", "temp", "dl"]
    ay = ("q = distribuida perpendicular a la barra; qa = axial; qgx / qgy = en X / Y global; qgxp / qgyp = por longitud proyectada; "
          "P = puntual perpendicular; Pa = axial; Pgx / Pgy = global; Mp = momento; temp = temperatura; dl = desajuste de longitud")
    return {"tipo": "portico", "nombre": "Pórtico plano", "dim": 2, "ejes": ["x", "y"],
            "geo": {"apoyos": ["ux", "uy", "phi"], "cargas": ["px", "py", "m"], "resortes": ["kx", "ky", "kphi"], "fuerzas": ["px", "py"], "momentos": ["m"]},
            "bloques": [proyecto("portico", ["-y", "+y", "-x", "+x"], "-y"),
                        nodos(["x", "y"]), materiales(), secciones(SECC_BASE + SECC_PARED, _sec_plana(False)),
                        barras(2, art), apoyos([("ux", "Restringe ux"), ("uy", "Restringe uy"), ("phi", "Restringe el giro")], "Apoyos: 1 = restringido, vacío = libre."),
                        resortes([("kx", "Rigidez en x"), ("ky", "Rigidez en y"), ("kphi", "Rigidez de giro")]), resortes_incl(),
                        cargas([("px", "Fuerza en x"), ("py", "Fuerza en y"), ("m", "Momento (positivo antihorario)")], "Cargas en nodos, en ejes globales."),
                        _cb_plano(tipos, ay), prefijados([("ux", "ux impuesto"), ("uy", "uy impuesto"), ("phi", "giro impuesto")]),
                        bloque("DESAJUSTE DE RESORTES", [C("caso", "ref:casos", "Caso", ob=True), C("nodo", "ref:nodos", "Nodo", ob=True),
                                                         C("ux", "num", "Apoyo corrido en x"), C("uy", "num", "Apoyo corrido en y"), C("phi", "num", "Giro corrido"),
                                                         C("inclinado", "num", "Corrimiento a lo largo del eje del resorte inclinado")],
                               "Desajuste (apoyo corrido) de los resortes.  Fuerza del resorte: −k·(u − e)."),
                        combinaciones(), soldaduras_modelo(), electrodos()]}


def esquema_emparrillado():
    art = {"t": "opc", "ay": "Articulación: m = flexión, t = torsión, mt = ambas; vacío = rígido", "op": ["m", "t", "mt"]}
    ay = "q = distribuida (+z), P = puntual, temp = temperatura (gradiente)"
    return {"tipo": "emparrillado", "nombre": "Emparrillado plano", "dim": 2, "ejes": ["x", "y"],
            "geo": {"apoyos": ["uz", "phix", "phiy"], "cargas": ["pz", "mx", "my"], "resortes": ["kz", "kphix", "kphiy"], "fuerzas": ["pz"], "momentos": ["mx", "my"], "fuera_de_plano": True},
            "bloques": [proyecto("emparrillado", ["-z", "+z"], "-z"),
                        nodos(["x", "y"]), materiales(g=True), secciones(SECC_BASE + SECC_PARED, _sec_plana(True)),
                        barras(2, art, pandeo=False),
                        apoyos([("uz", "Restringe el desplazamiento vertical"), ("phix", "Restringe el giro alrededor de x"), ("phiy", "Restringe el giro alrededor de y")],
                               "Apoyos: 1 = restringido, vacío = libre."),
                        resortes([("kz", "Rigidez vertical"), ("kphix", "Rigidez de giro alrededor de x"), ("kphiy", "Rigidez de giro alrededor de y")]),
                        resortes_incl(giro=True),
                        cargas([("pz", "Fuerza vertical"), ("mx", "Momento alrededor de x"), ("my", "Momento alrededor de y")], "Cargas en nodos (fuera del plano)."),
                        _cb_plano(["q", "P", "temp"], ay), prefijados([("uz", "uz impuesto"), ("phix", "giro x impuesto"), ("phiy", "giro y impuesto")]),
                        bloque("DESAJUSTE DE RESORTES", [C("caso", "ref:casos", "Caso", ob=True), C("nodo", "ref:nodos", "Nodo", ob=True),
                                                         C("uz", "num", "Apoyo corrido en z"), C("phix", "num", "Giro corrido en x"), C("phiy", "num", "Giro corrido en y")],
                               "Desajuste (apoyo corrido) de los resortes."),
                        combinaciones(), soldaduras_modelo(), electrodos()]}


def esquema_reticulado():
    ay = "temp = temperatura; corta / larga = la barra es más corta / más larga que la distancia entre nudos (valor = e, positivo)"
    cb = bloque("CARGAS EN BARRAS", [C("caso", "ref:casos", "Caso", ob=True), C("barra", "ref:barras", "Barra", ob=True),
                                     C("tipo", "opc", ay, ["temp", "corta", "larga"], ob=True),
                                     C("valor", "num", "temp: ΔT (uniforme).  corta / larga: el desajuste e (número positivo)", ob=True),
                                     C("valor2", "num", "temp: ΔT de la otra cara (vacío = uniforme)")],
                "Efectos que alargan o acortan las barras.", min=["caso", "barra", "tipo", "valor"])
    return {"tipo": "reticulado", "nombre": "Reticulado plano", "dim": 2, "ejes": ["x", "y"],
            "geo": {"apoyos": ["ux", "uy"], "cargas": ["px", "py"], "resortes": ["kx", "ky"], "fuerzas": ["px", "py"], "momentos": []},
            "bloques": [proyecto("reticulado", ["-y", "+y", "-x", "+x"], "-y", con_corte=False),
                        nodos(["x", "y"]), materiales(ext=False), secciones(SECC_BASE + SECC_PARED, _sec_plana(False)),
                        barras(2, None), apoyos([("ux", "Restringe ux"), ("uy", "Restringe uy")], "Apoyos: 1 = restringido, vacío = libre."),
                        resortes([("kx", "Rigidez en x"), ("ky", "Rigidez en y")]), resortes_incl(),
                        cargas([("px", "Fuerza en x"), ("py", "Fuerza en y")], "Cargas en nodos, en ejes globales."),
                        cb, prefijados([("ux", "ux impuesto"), ("uy", "uy impuesto")]),
                        bloque("DESAJUSTE DE RESORTES", [C("caso", "ref:casos", "Caso", ob=True), C("nodo", "ref:nodos", "Nodo", ob=True),
                                                         C("ux", "num", "Apoyo corrido en x"), C("uy", "num", "Apoyo corrido en y"),
                                                         C("inclinado", "num", "Corrimiento a lo largo del eje del resorte inclinado")],
                               "Desajuste (apoyo corrido) de los resortes."),
                        combinaciones()]}


def esquema_soldadura():
    cols = [C("id", "txt", "Nombre de la soldadura", ob=True),
            C("tipo", "opc", "filete (método de la garganta) o tope", ["filete", "tope"], d="filete"),
            C("disposicion", "opc", "Forma del grupo de cordones", DISPOSICIONES, ob=True),
            C("b", "num", "Medida horizontal (según y)"), C("d", "num", "Medida vertical (según z) o diámetro"),
            C("arcos", "txt", "Solo «arco»: centro:abertura|centro:abertura en grados"),
            C("esp", "num", "Espesor de las piezas (en tope es la garganta; en filete solo dibuja el contorno)"),
            C("segmentos", "txt", "Solo «custom»: segmentos propios"),
            C("electrodo", "ref:electrodos", "Electrodo (ELECTRODOS, biblioteca o tabla interna)", ob=True, lista="nombres_electrodos"),
            C("w", "num", "Pie del filete adoptado; vacío = el programa calcula el requerido"),
            C("sy_base", "num", "Fluencia del metal base"), C("lib", "txt", "N.º de material de la biblioteca: toma de ahí sy_base", lista="lib_materiales"),
            C("t_gruesa", "num", "Espesor de la pieza más gruesa"), C("t_fina", "num", "Espesor de la pieza más fina")]
    car = [C("soldadura", "ref:soldaduras", "Soldadura cargada (vacío si hay una sola)"), C("caso", "ref:casos", "Nombre del caso", ob=True)] + \
          [C(n, "num", t) for n, t in (("N", "Fuerza axial"), ("Vy", "Corte en y"), ("Vz", "Corte en z"), ("T", "Torsión"), ("My", "Momento alrededor de y"),
                                       ("Mz", "Momento alrededor de z"), ("yp", "Punto de aplicación y (vacío = centro de la disposición)"), ("zp", "Punto de aplicación z"))]
    return {"tipo": "soldadura", "nombre": "Soldaduras (modo rápido)", "dim": 0, "ejes": [], "geo": {},
            "bloques": [proyecto("soldadura", [], "", soldadura=True), electrodos(),
                        bloque("SOLDADURAS", cols, "Grupos de cordones a verificar.", ob=True, min=["id", "disposicion", "electrodo"]),
                        bloque("CARGAS", car, "Esfuerzos sobre cada soldadura, en el plano de la sección.", ob=True, min=["caso"])]}


ESQUEMAS = {f: globals()["esquema_" + f]() for f in ("portico3d", "portico", "emparrillado", "reticulado", "soldadura")}
TIPOS = list(ESQUEMAS)


def _mover(bloque, col, antes_de=None):
    """Cambia solo el orden en que el editor muestra una columna (el archivo se lee por nombre de columna)."""
    cols = bloque["cols"]
    c = next((x for x in cols if x["n"] == col), None)
    if c is None:
        return
    cols.remove(c)
    cols.insert(0 if antes_de is None else next(i for i, x in enumerate(cols) if x["n"] == antes_de), c)


for _s in ESQUEMAS.values():
    for _b in _s["bloques"]:
        if _b["t"] in ("MATERIALES", "ELECTRODOS"):
            _mover(_b, "lib")                                   # lo primero que se elige: el material (o electrodo) de la biblioteca
        elif _b["t"] == "SOLDADURAS":
            _mover(_b, "lib", "sy_base")

from . import etiquetas as _et  # noqa: E402
_et.aplicar(ESQUEMAS)


def bloque_de(tipo, titulo):
    for b in ESQUEMAS[tipo]["bloques"]:
        if b["t"] == titulo:
            return b
    return None
