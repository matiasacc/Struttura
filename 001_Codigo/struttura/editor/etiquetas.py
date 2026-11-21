"""Nombres claros para el editor: título de cada bloque, etiqueta y unidad de cada columna, y nombre de cada opción.

Solo cambia lo que ve la persona que usa el editor.  El archivo CSV sigue usando los nombres de siempre (columna `n` del esquema),
que el editor muestra en chico debajo de cada etiqueta.  Las ayudas (`ay`) siguen siendo las del esquema.

Unidades (código `u`):  F fuerza · L longitud · S tensión (F/L²) · FL momento (F·L) · K rigidez (F/L) · KG rigidez de giro (F·L)
L2 área · L3 módulo resistente · L4 inercia · rad · deg · rho (kg/m³) · alfa (1/°C) · FpL fuerza por longitud · "" sin unidad."""
from __future__ import annotations

BLOQUES = {
    "PROYECTO": "Datos generales", "NODOS": "Nodos", "MATERIALES": "Materiales", "SECCIONES": "Secciones", "BARRAS": "Barras",
    "APOYOS": "Apoyos", "RESORTES": "Resortes en nodos", "RESORTES INCLINADOS": "Resortes inclinados",
    "RESORTES GIRO INCLINADO": "Resorte de giro inclinado", "CARGAS": "Cargas en nodos", "CARGAS EN BARRAS": "Cargas en barras",
    "DESPLAZAMIENTOS PREFIJADOS": "Desplazamientos impuestos", "DESAJUSTE DE RESORTES": "Desajuste de resortes",
    "COMBINACIONES": "Combinaciones de cargas", "PUNTOS DE TENSION": "Puntos de tensión", "SOLDADURAS": "Soldaduras", "ELECTRODOS": "Electrodos",
}

AYUDA_BLOQUE = {
    "APOYOS": "Qué movimientos impide cada apoyo.  Fijo = ese desplazamiento o giro vale 0 (el apoyo lo impide); Libre = el nodo se puede mover.  Elegí un tipo (Empotrado, Articulado...) o cambiá cada uno.",
    "MATERIALES": "Elegí el material de la biblioteca (completa E, G, ν, σy, ρ...) o cargá los valores a mano; lo que escribas a mano manda sobre la biblioteca.",
    "SECCIONES": "Forma y medidas de cada sección.  Se muestran solo las medidas que usa la forma elegida; los perfiles de pared delgada usan medidas de la línea media.",
    "BARRAS": "Cada barra une dos nodos y lleva un material y una sección.",
    "CARGAS": "Fuerzas y momentos aplicados en los nodos, agrupados en casos de carga.",
}

# (bloque o None, columna) → (etiqueta, código de unidad).  Se busca primero con el bloque y después sin él.
COLS = {
    # --- datos generales
    (None, "proyecto"): ("Nombre del proyecto", ""), (None, "autor"): ("Autor", ""), (None, "tipo"): ("Tipo de estructura", ""),
    (None, "unidad_fuerza"): ("Unidad de fuerza", ""), (None, "unidad_longitud"): ("Unidad de longitud", ""),
    (None, "escala_deformada"): ("Escala de la deformada", ""), (None, "corte_tensiones"): ("Incluir tensión de corte", ""),
    (None, "csv_salida"): ("Formato de los CSV de resultados", ""), (None, "anexo_matrices"): ("Anexo con matrices de rigidez", ""),
    (None, "escala_diagramas"): ("Escala de los diagramas", ""), (None, "peso_propio"): ("Peso propio (caso donde se suma)", ""),
    (None, "gravedad"): ("Dirección de la gravedad", ""),
    # --- nodos
    ("NODOS", "id"): ("Nodo", ""), ("NODOS", "x"): ("Coordenada x", "L"), ("NODOS", "y"): ("Coordenada y", "L"), ("NODOS", "z"): ("Coordenada z", "L"),
    # --- materiales
    ("MATERIALES", "lib"): ("Material de la biblioteca", ""), ("MATERIALES", "id"): ("Nombre en este modelo", ""),
    ("MATERIALES", "e"): ("Módulo de elasticidad E", "S"), ("MATERIALES", "g"): ("Módulo de corte G", "S"),
    ("MATERIALES", "nu"): ("Coeficiente de Poisson ν", ""), ("MATERIALES", "fy"): ("Tensión de fluencia σy", "S"),
    ("MATERIALES", "sadm"): ("Tensión admisible σadm", "S"), ("MATERIALES", "alfa"): ("Dilatación térmica α", "alfa"),
    ("MATERIALES", "sut"): ("Resistencia a tracción σu", "S"), ("MATERIALES", "suc"): ("Resistencia a compresión σuc", "S"),
    ("MATERIALES", "teoria"): ("Criterio de falla", ""), ("MATERIALES", "rho"): ("Densidad ρ", "rho"),
    # --- secciones
    ("SECCIONES", "id"): ("Nombre en este modelo", ""), ("SECCIONES", "lib"): ("Perfil de la biblioteca", ""), ("SECCIONES", "tipo"): ("Forma de la sección", ""),
    ("SECCIONES", "a"): ("Área A", "L2"), ("SECCIONES", "iy"): ("Inercia Iy (flexión alrededor de y)", "L4"),
    ("SECCIONES", "iz"): ("Inercia Iz (flexión alrededor de z)", "L4"), ("SECCIONES", "i"): ("Inercia a flexión I", "L4"),
    ("SECCIONES", "j"): ("Constante de torsión J", "L4"), ("SECCIONES", "cy"): ("Fibra extrema cy", "L"), ("SECCIONES", "cz"): ("Fibra extrema cz", "L"),
    ("SECCIONES", "c"): ("Fibra extrema c", "L"), ("SECCIONES", "wt"): ("Módulo resistente a torsión Wt", "L3"),
    ("SECCIONES", "kv"): ("Factor de corte kv", ""), ("SECCIONES", "d"): ("Diámetro exterior d", "L"), ("SECCIONES", "t"): ("Espesor de pared t", "L"),
    ("SECCIONES", "b"): ("Ancho b", "L"), ("SECCIONES", "h"): ("Altura h", "L"), ("SECCIONES", "tf"): ("Espesor de ala tf", "L"),
    ("SECCIONES", "tw"): ("Espesor de alma tw", "L"),
    # --- barras
    ("BARRAS", "id"): ("Barra", ""), ("BARRAS", "nodo_i"): ("Nodo inicial (i)", ""), ("BARRAS", "nodo_j"): ("Nodo final (j)", ""),
    ("BARRAS", "material"): ("Material", ""), ("BARRAS", "seccion"): ("Sección", ""),
    ("BARRAS", "rx"): ("Orientación: componente x", ""), ("BARRAS", "ry"): ("Orientación: componente y", ""), ("BARRAS", "rz"): ("Orientación: componente z", ""),
    ("BARRAS", "giro"): ("Giro de la sección", "deg"), ("BARRAS", "art_i"): ("Articulación en i", ""), ("BARRAS", "art_j"): ("Articulación en j", ""),
    ("BARRAS", "pandeo"): ("Apoyo de los extremos (pandeo)", ""),
    # --- apoyos y resortes
    (None, "nodo"): ("Nodo", ""),
    ("APOYOS", "ux"): ("Desplazamiento en x", ""), ("APOYOS", "uy"): ("Desplazamiento en y", ""), ("APOYOS", "uz"): ("Desplazamiento en z", ""),
    ("APOYOS", "phi"): ("Giro", ""), ("APOYOS", "phix"): ("Giro alrededor de x", ""), ("APOYOS", "phiy"): ("Giro alrededor de y", ""), ("APOYOS", "phiz"): ("Giro alrededor de z", ""),
    ("RESORTES", "kx"): ("Rigidez en x", "K"), ("RESORTES", "ky"): ("Rigidez en y", "K"), ("RESORTES", "kz"): ("Rigidez en z", "K"),
    ("RESORTES", "kphi"): ("Rigidez de giro", "KG"), ("RESORTES", "kphix"): ("Rigidez de giro alrededor de x", "KG"),
    ("RESORTES", "kphiy"): ("Rigidez de giro alrededor de y", "KG"), ("RESORTES", "kphiz"): ("Rigidez de giro alrededor de z", "KG"),
    ("RESORTES INCLINADOS", "dx"): ("Dirección: componente x", ""), ("RESORTES INCLINADOS", "dy"): ("Dirección: componente y", ""),
    ("RESORTES INCLINADOS", "dz"): ("Dirección: componente z", ""), ("RESORTES INCLINADOS", "ax"): ("Ángulo con el eje X", "deg"),
    ("RESORTES INCLINADOS", "ay"): ("Ángulo con el eje Y", "deg"), ("RESORTES INCLINADOS", "az"): ("Ángulo con el eje Z", "deg"),
    (None, "k"): ("Rigidez del resorte", "K"), (None, "angulo"): ("Ángulo del eje respecto de +x", "deg"),
    # --- cargas
    (None, "caso"): ("Caso de carga", ""),
    ("CARGAS", "fx"): ("Fuerza en x", "F"), ("CARGAS", "fy"): ("Fuerza en y", "F"), ("CARGAS", "fz"): ("Fuerza en z", "F"),
    ("CARGAS", "px"): ("Fuerza en x", "F"), ("CARGAS", "py"): ("Fuerza en y", "F"), ("CARGAS", "pz"): ("Fuerza perpendicular al plano (z)", "F"),
    ("CARGAS", "m"): ("Momento", "FL"), ("CARGAS", "mx"): ("Momento alrededor de x", "FL"), ("CARGAS", "my"): ("Momento alrededor de y", "FL"),
    ("CARGAS", "mz"): ("Momento alrededor de z", "FL"),
    ("CARGAS EN BARRAS", "barra"): ("Barra cargada", ""), ("CARGAS EN BARRAS", "tipo"): ("Tipo de carga", ""),
    ("CARGAS EN BARRAS", "valor"): ("Valor (en i, o único)", ""), ("CARGAS EN BARRAS", "valor2"): ("Valor en j (si varía)", ""),
    ("CARGAS EN BARRAS", "a"): ("Posición o inicio a (desde i)", "L"), ("CARGAS EN BARRAS", "b"): ("Fin b (desde i)", "L"),
    # --- desplazamientos impuestos y desajuste
    ("DESPLAZAMIENTOS PREFIJADOS", "ux"): ("Desplazamiento impuesto en x", "L"), ("DESPLAZAMIENTOS PREFIJADOS", "uy"): ("Desplazamiento impuesto en y", "L"),
    ("DESPLAZAMIENTOS PREFIJADOS", "uz"): ("Desplazamiento impuesto en z", "L"), ("DESPLAZAMIENTOS PREFIJADOS", "phi"): ("Giro impuesto", "rad"),
    ("DESPLAZAMIENTOS PREFIJADOS", "phix"): ("Giro impuesto alrededor de x", "rad"), ("DESPLAZAMIENTOS PREFIJADOS", "phiy"): ("Giro impuesto alrededor de y", "rad"),
    ("DESPLAZAMIENTOS PREFIJADOS", "phiz"): ("Giro impuesto alrededor de z", "rad"),
    ("DESAJUSTE DE RESORTES", "ux"): ("Corrimiento en x", "L"), ("DESAJUSTE DE RESORTES", "uy"): ("Corrimiento en y", "L"),
    ("DESAJUSTE DE RESORTES", "uz"): ("Corrimiento en z", "L"), ("DESAJUSTE DE RESORTES", "phi"): ("Giro corrido", "rad"),
    ("DESAJUSTE DE RESORTES", "phix"): ("Giro corrido alrededor de x", "rad"), ("DESAJUSTE DE RESORTES", "phiy"): ("Giro corrido alrededor de y", "rad"),
    ("DESAJUSTE DE RESORTES", "inclinado"): ("Corrimiento sobre el eje inclinado", "L"),
    # --- combinaciones y puntos de tensión
    ("COMBINACIONES", "combinacion"): ("Combinación", ""), ("COMBINACIONES", "caso"): ("Caso que entra", ""), ("COMBINACIONES", "factor"): ("Factor", ""),
    ("PUNTOS DE TENSION", "id"): ("Punto", ""), ("PUNTOS DE TENSION", "barra"): ("Barra", ""),
    ("PUNTOS DE TENSION", "x"): ("Posición a lo largo de la barra", "L"), ("PUNTOS DE TENSION", "y"): ("Coordenada y en la sección", "L"),
    ("PUNTOS DE TENSION", "z"): ("Coordenada z en la sección", "L"), ("PUNTOS DE TENSION", "caso"): ("Caso o combinación", ""),
    # --- soldaduras y electrodos
    ("SOLDADURAS", "id"): ("Soldadura", ""), ("SOLDADURAS", "tipo"): ("Tipo de unión", ""), ("SOLDADURAS", "esp"): ("Espesor de las piezas", "L"),
    ("SOLDADURAS", "barra"): ("Barra", ""), ("SOLDADURAS", "extremo"): ("Extremo de la barra", ""), ("SOLDADURAS", "disposicion"): ("Forma del cordón", ""),
    ("SOLDADURAS", "b"): ("Medida horizontal b", "L"), ("SOLDADURAS", "d"): ("Medida vertical d (o diámetro)", "L"),
    ("SOLDADURAS", "arcos"): ("Arcos (centro:abertura)", ""), ("SOLDADURAS", "segmentos"): ("Segmentos propios", ""),
    ("SOLDADURAS", "oy"): ("Corrimiento del cordón en y", "L"), ("SOLDADURAS", "oz"): ("Corrimiento del cordón en z", "L"),
    ("SOLDADURAS", "electrodo"): ("Electrodo", ""), ("SOLDADURAS", "w"): ("Pie del filete adoptado w", "L"),
    ("SOLDADURAS", "sy_base"): ("Fluencia del metal base", "S"), ("SOLDADURAS", "lib"): ("Material base de la biblioteca", ""),
    ("SOLDADURAS", "t_gruesa"): ("Espesor de la pieza más gruesa", "L"), ("SOLDADURAS", "t_fina"): ("Espesor de la pieza más fina", "L"),
    ("ELECTRODOS", "id"): ("Nombre del electrodo", ""), ("ELECTRODOS", "sut"): ("Resistencia a tracción del aporte", "S"),
    ("ELECTRODOS", "sy"): ("Fluencia del aporte", "S"), ("ELECTRODOS", "tau_adm"): ("Corte admisible en la garganta", "S"),
    ("ELECTRODOS", "lib"): ("Electrodo de la biblioteca", ""),
    # --- modo rápido de soldaduras: cargas
    ("CARGAS", "soldadura"): ("Soldadura", ""), ("CARGAS", "N"): ("Fuerza axial N", "F"), ("CARGAS", "Vy"): ("Corte Vy", "F"), ("CARGAS", "Vz"): ("Corte Vz", "F"),
    ("CARGAS", "T"): ("Momento torsor T", "FL"), ("CARGAS", "My"): ("Momento flector My", "FL"), ("CARGAS", "Mz"): ("Momento flector Mz", "FL"),
    ("CARGAS", "yp"): ("Punto de aplicación yp", "L"), ("CARGAS", "zp"): ("Punto de aplicación zp", "L"),
}

# Se pisan para un tipo de estructura:  (tipo, bloque, columna) → (etiqueta, unidad)
POR_TIPO = {
    ("soldadura", "SOLDADURAS", "tipo"): ("Tipo de unión", ""),
    ("emparrillado", "CARGAS EN BARRAS", "valor"): ("Valor (en a, o único)", ""),
    ("portico", "CARGAS EN BARRAS", "valor"): ("Valor (en a, o único)", ""), ("emparrillado", "CARGAS EN BARRAS", "valor2"): ("Valor en b (si varía)", ""),
    ("portico", "CARGAS EN BARRAS", "valor2"): ("Valor en b (si varía)", ""),
}

# Nombres de las opciones (el valor que se guarda en el CSV no cambia)
OPCIONES = {
    "tipo": {"portico3d": "Pórtico espacial 3D", "portico": "Pórtico plano", "emparrillado": "Emparrillado", "reticulado": "Reticulado", "soldadura": "Soldaduras (modo rápido)"},
    "csv_salida": {"excel_es": "Excel en español (coma decimal)", "estandar": "Estándar (punto decimal)"},
    "anexo_matrices": {"si": "Sí", "no": "No", "auto": "Automático"},
    "corte_tensiones": {"si": "Sí", "no": "No"},
    "escala_diagramas": {"barra": "Una por barra", "global": "Una sola para todas"},
    "teoria": {"vm": "Von Mises", "tresca": "Tresca", "rankine": "Rankine", "mohr": "Mohr", "mohrmod": "Mohr modificado"},
    "pandeo": {"art-art": "Articulada – articulada", "emp-lib": "Empotrada – libre", "emp-art": "Empotrada – articulada", "emp-emp": "Empotrada – empotrada"},
    "extremo": {"i": "Extremo i (inicial)", "j": "Extremo j (final)"},
    "disposicion": {"circulo": "Círculo", "arco": "Arcos", "rectangulo": "Rectángulo", "costados": "Solo costados", "arriba_abajo": "Solo arriba y abajo",
                    "linea": "Línea", "L": "Ángulo en L", "C": "C", "C_invertida": "C invertida", "doble_t": "Doble T", "custom": "Segmentos propios"},
    ("SECCIONES", "tipo"): {"perfil": "Perfil de la biblioteca", "generica": "Genérica (datos propios)", "tubo": "Tubo circular", "circular": "Circular maciza", "rectangular": "Rectangular maciza",
                            "rect_hueca": "Rectangular hueca", "canal": "Canal (U)", "doble_t": "Doble T", "te": "Te", "z": "Z", "angular": "Ángulo (L)"},
    ("BARRAS", "art_i"): {"1": "Rótula esférica (libera My y Mz)", "my": "Libera solo My", "mz": "Libera solo Mz", "t": "Libera solo la torsión T",
                          "my+t": "Libera My y T", "mz+t": "Libera Mz y T", "my+mz+t": "Libera My, Mz y T",
                          "m": "Libera la flexión (m)", "mt": "Libera flexión y torsión (m + t)"},
    ("SOLDADURAS", "tipo"): {"filete": "Filete", "tope": "A tope"},
    ("CARGAS EN BARRAS", "tipo"): {
        "q": "Distribuida", "qa": "Distribuida axial", "qgx": "Distribuida en x global", "qgy": "Distribuida en y global",
        "qgxp": "Distribuida en x global (longitud proyectada)", "qgyp": "Distribuida en y global (longitud proyectada)",
        "P": "Puntual", "Pa": "Puntual axial", "Pgx": "Puntual en x global", "Pgy": "Puntual en y global", "Mp": "Momento puntual",
        "temp": "Temperatura", "dl": "Desajuste de longitud",
        "qx": "Distribuida en x local", "qy": "Distribuida en y local", "qz": "Distribuida en z local",
        "qgz": "Distribuida en z global",
        "Px": "Puntual en x local", "Py": "Puntual en y local", "Pz": "Puntual en z local", "Pgz": "Puntual en z global",
        "Mx": "Momento alrededor de x local", "My": "Momento alrededor de y local", "Mz": "Momento alrededor de z local",
        "Mgx": "Momento alrededor de x global", "Mgy": "Momento alrededor de y global", "Mgz": "Momento alrededor de z global"},
}
OPCIONES[("BARRAS", "art_j")] = OPCIONES[("BARRAS", "art_i")]
OPCIONES[("BARRAS", "art_i")]["t"] = "Libera solo la torsión T"
# la opción "tipo" de CARGAS EN BARRAS del 3D usa qgx/qgy/Pgx/Pgy con otro significado que en los planos: se aclara por tipo de estructura
OPCIONES_TIPO = {
    ("portico3d", "CARGAS EN BARRAS", "tipo"): {"qgx": "Distribuida en x global", "qgy": "Distribuida en y global", "qgz": "Distribuida en z global",
                                                "Pgx": "Puntual en x global", "Pgy": "Puntual en y global", "Pgz": "Puntual en z global"},
    ("emparrillado", "CARGAS EN BARRAS", "tipo"): {"q": "Distribuida (perpendicular al plano)", "P": "Puntual (perpendicular al plano)", "temp": "Temperatura (gradiente)"},
}

# Campos de la sección que usa cada forma:  forma → (obligatorios, opcionales).  Tomado de los cargadores de cada programa.
SECCION_CAMPOS = {
    "portico3d": {"generica": (["a", "iy", "iz", "j"], ["cy", "cz", "wt"]), "tubo": (["d", "t"], []), "circular": (["d"], []),
                  "rectangular": (["b", "h"], []), "rect_hueca": (["b", "h", "t"], [])},
    "plano": {"generica": (["i", "a"], ["c", "kv", "h"]), "tubo": (["d", "t"], []), "circular": (["d"], []), "rectangular": (["b", "h"], []),
              "rect_hueca": (["b", "h", "t"], [])},
    "emparrillado": {"generica": (["i", "j"], ["a", "c", "wt", "kv", "h"]), "tubo": (["d", "t"], []), "circular": (["d"], []),
                     "rectangular": (["b", "h"], []), "rect_hueca": (["b", "h", "t"], [])},
}
PARED = {"canal": (["h", "b"], ["t", "tf", "tw"]), "doble_t": (["h", "b"], ["t", "tf", "tw"]), "te": (["h", "b"], ["t", "tf", "tw"]),
         "z": (["h", "b"], ["t", "tf", "tw"]), "angular": (["h", "b", "t"], [])}
for _k in SECCION_CAMPOS.values():
    _k.update(PARED)
    _k["perfil"] = (["lib"], _k["generica"][0] + _k["generica"][1])          # lo escrito a mano manda sobre la biblioteca

AYUDA_PARED = "Perfil de pared delgada: las medidas son de la línea media.  Se da el espesor único t, o bien tf (ala) y tw (alma)."


def aplicar(esquemas: dict) -> None:
    """Agrega `et` (etiqueta), `u` (unidad) y `ope` (nombres de opciones) a cada bloque y columna de los esquemas."""
    for tipo, s in esquemas.items():
        sec = SECCION_CAMPOS["plano" if tipo in ("portico", "reticulado") else tipo] if tipo != "soldadura" else {}
        s["seccion_campos"] = {k: {"ob": ob, "op": op} for k, (ob, op) in sec.items()}
        for b in s["bloques"]:
            b["et"] = BLOQUES.get(b["t"], b["t"].capitalize())
            if b["t"] in AYUDA_BLOQUE and not (tipo == "soldadura" and b["t"] == "CARGAS"):
                b["ay"] = AYUDA_BLOQUE[b["t"]]
            for c in b["cols"]:
                k = POR_TIPO.get((tipo, b["t"], c["n"])) or COLS.get((b["t"], c["n"])) or COLS.get((None, c["n"]))
                c["et"], c["u"] = (k if k else (c["n"], ""))
                if c.get("op"):
                    om = {}
                    for fuente in (OPCIONES.get(c["n"]), OPCIONES.get((b["t"], c["n"])), OPCIONES_TIPO.get((tipo, b["t"], c["n"]))):
                        if fuente:
                            om.update(fuente)
                    if om:
                        c["ope"] = {o: om[o] for o in c["op"] if o in om}
