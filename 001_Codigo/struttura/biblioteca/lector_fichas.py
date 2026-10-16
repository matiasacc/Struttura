"""Lee una ficha de datos de un material (PDF o texto copiado).  Solo interpreta lo que la ficha dice; lo que no reconoce NO se descarta:
queda en 'no_interpretado' y en 'texto_original', y se avisa al importar.  Nada se completa ni se estima."""
import re

# (clave, nombre en la ficha [las palabras pueden estar en renglones distintos], tipo)
#   tipo 'num': valor métrico (con unidad) + valor inglés (con unidad);  'rango': como num pero el valor puede ser un rango o '<=';  'adim': sin unidad
PROPIEDADES = [
    ("densidad", r"Density", "num"),
    ("dureza_brinell", r"Hardness, Brinell", "adim"),
    ("dureza_knoop", r"Hardness, Knoop", "adim"),
    ("dureza_rockwell_b", r"Hardness, Rockwell B", "adim"),
    ("dureza_rockwell_c", r"Hardness, Rockwell C", "adim"),
    ("dureza_vickers", r"Hardness, Vickers", "adim"),
    ("sut", r"Tensile Strength, Ultimate", "num"),
    ("sy", r"Tensile Strength, Yield", "num"),
    ("alargamiento", r"Elongation at Break", "adim"),
    ("reduccion_area", r"Reduction of Area", "adim"),
    ("E", r"Modulus of Elasticity", "num"),
    ("K", r"Bulk Modulus", "num"),
    ("nu", r"Poissons? Ratio", "adim"),
    ("maquinabilidad", r"Machinability", "adim"),
    ("G", r"Shear Modulus", "num"),
    ("resistividad", r"Electrical Resistivity", "multi"),
    ("calor_especifico", r"Specific Heat Capacity", "multi"),
    ("conductividad", r"Thermal Conductivity", "num"),
    ("cte_lineal", r"CTE, linear", "multi"),
    ("compresion_fluencia", r"Compressive Yield Strength", "num"),
    ("fatiga", r"Fatigue Strength", "num"),
    ("izod", r"Izod Impact", "num"),
    ("charpy", r"Charpy Impact", "num"),
]
ELEMENTOS = r"(?:Carbon, C|Iron, Fe|Manganese, Mn|Phosphorus, P|Sulfur, S|Silicon, Si|Chromium, Cr|Nickel, Ni|Molybdenum, Mo|Copper, Cu|Aluminum, Al|Vanadium, V|Tungsten, W|Cobalt, Co|Titanium, Ti|Niobium, Nb|Boron, B|Nitrogen, N|Lead, Pb|Zinc, Zn|Magnesium, Mg|Tin, Sn)"
NUM2 = r"(?:[<>]=?\s*)?\d[\d.,eE+-]*(?:\s*-\s*\d[\d.,eE+-]*)?"      # segundo valor: sin "=" suelto (p. ej. "steel = 100%" no es un valor)
NUM = r"[<>=]*\s*\d[\d.,eE+-]*(?:\s*-\s*\d[\d.,eE+-]*)?"
_UNIDADES = r"(?:g/cc|MPa|GPa|%|ohm-cm|J/g-°C|W/m-K|µm/m-°C|kg/m³|J|kJ/m²|kJ/m2|mm|HB|HRC)"


def _limpiar(t):
    t = t.replace("\x00", " ").replace(" ", " ")
    return re.sub(r"[ \t]+", " ", t)


def texto_de_pdf(ruta):
    """Texto del PDF con pypdf (pip install pypdf)."""
    try:
        from pypdf import PdfReader
    except ImportError:
        raise RuntimeError("para leer PDF hace falta  pip install pypdf  (o pasá la ficha como .txt copiando el texto de la página)")
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return "\n".join((p.extract_text() or "") for p in PdfReader(str(ruta)).pages)


def _bloque(texto, ini, fin_alts):
    i = texto.find(ini)
    if i < 0:
        return ""
    j = min([k for k in (texto.find(f, i + len(ini)) for f in fin_alts) if k > 0] or [len(texto)])
    return texto[i + len(ini):j]


def parsear(texto):
    """Devuelve la ficha como dict.  Campos: nombre, ref, categorias, notas, palabras_clave, propiedades{clave: {...}}, composicion[], no_interpretado[], texto_original."""
    t = _limpiar(texto)
    lineas = [l.strip() for l in t.splitlines() if l.strip()]
    plano = " ".join(lineas)
    ficha = {"nombre": None, "ref": None, "categorias": None, "notas": None, "palabras_clave": None, "propiedades": {}, "composicion": [],
             "no_interpretado": [], "texto_original": texto}
    for k, l in enumerate(lineas):                                     # el nombre es el renglón que sigue al buscador, antes de 'Categories:'
        if l.startswith("Categories:"):
            ficha["nombre"] = lineas[k - 1]
            ficha["categorias"] = l.split(":", 1)[1].strip()
            break
    m = re.search(r"Material Notes:\s*(.*?)\s*Key Words:", plano) or re.search(r"Material\s+Notes:\s*(.*?)\s*Key Words:", plano)
    if m:
        ficha["notas"] = m.group(1).strip()
    m = re.search(r"Key Words:\s*(.*?)\s*Vendors:", plano)
    if m:
        ficha["palabras_clave"] = m.group(1).strip()
    m = re.search(r"\b(M[A-Z0-9]{3,12})\s*/\s*(\d+)\s*$", plano.split("Subscribe to Premium")[0].strip()) or re.search(r"\b(M[A-Z0-9]{3,12}) / (\d+)\b", plano)
    if m:
        ficha["ref"] = m.group(1)
    # sección de propiedades (entre la tabla de acciones y las referencias)
    cuerpo = plano
    for marca in ("Physical Properties", "Physical PropertiesMetric", "PhysicalProperties"):
        if marca in cuerpo:
            cuerpo = cuerpo[cuerpo.find(marca):]
            break
    for marca in ("References for this datasheet", "Some of the values displayed above"):
        if marca in cuerpo:
            cuerpo = cuerpo[:cuerpo.find(marca)]
    cuerpo = re.sub(r"(Physical|Mechanical|Electrical|Thermal|Component Elements|Component|Other|Processing) ?Properties ?(?:Metric English Comments)?", " | ", cuerpo)
    cuerpo = re.sub(r"Metric English Comments", " ", cuerpo)
    nombres = "|".join(f"(?:{n.replace(' ', r'[ ]?')})" for _, n, _ in PROPIEDADES)
    for clave, nombre, tipo in PROPIEDADES:
        patron = re.compile(rf"(?<![A-Za-z]){nombre.replace(' ', r'[ ]?')}\s+(?P<resto>.*?)(?=(?<![A-Za-z])(?:{nombres}|{ELEMENTOS})|\|\s|$)")
        for mm in patron.finditer(cuerpo):
            resto = mm.group("resto").strip()
            v = _valores(resto, tipo)
            c = v.get("comentario")
            sospechoso = re.search(rf"(?<![A-Za-z0-9])[A-Z][A-Za-z,'. -]{{2,40}}?\s+{NUM}\s*[^\s\d]*\s+{NUM2}", c) if c else None
            if sospechoso:                                              # otra propiedad (desconocida) quedó pegada al comentario: se separa y se avisa
                ficha["no_interpretado"].append(c[sospechoso.start():].strip())
                v["comentario"] = c[:sospechoso.start()].strip() or None
                if not v["comentario"]:
                    del v["comentario"]
            ficha["propiedades"].setdefault(clave, []).append(v)
    # composición: cada elemento hasta el siguiente elemento
    pos = [(m.start(), m.end(), m.group(0)) for m in re.finditer(ELEMENTOS, cuerpo)]
    for i, (ini, fin, el) in enumerate(pos):
        seg = cuerpo[fin:(pos[i + 1][0] if i + 1 < len(pos) else len(cuerpo))].split("|")[0].strip()
        mm = re.match(rf"(?P<m>{NUM})\s*%\s*(?P<i>{NUM})\s*%\s*(?P<c>.*)$", seg)
        if mm:
            ficha["composicion"].append({"elemento": el, "valor": mm.group("m").strip() + " %", "comentario": mm.group("c").strip() or None})
    # lo que no se reconoció: se avisa, no se pierde
    ficha["no_interpretado"] += _no_interpretado(cuerpo, nombres)
    return ficha


def _valores(resto, tipo):
    """'365 MPa 52900 psi Typical for steel' -> métrico / inglés / comentario.  Siempre se guarda 'crudo' (el texto tal cual)."""
    out = {"crudo": resto}
    if tipo == "multi":                                                  # varios valores según la temperatura (se descartan los repetidos en °F)
        vals = [{"valor": v.strip(), "unidad": u, "condicion": c.strip()}
                for v, u, c in re.findall(rf"({NUM})\s*(J/g-°C|µm/m-°C|W/m-K|ohm-cm)\s*@Temperature\s*([^@]*?)\s*(?=[\d]+\.?\d*\s*(?:BTU|µin|ohm-cm)|\s*$)", resto)]
        out["valores"] = [v for v in vals if "°F" not in v["condicion"]]
        if not out["valores"]:                                           # sin temperaturas: valor único
            return _valores(resto, "num")
        if "condition unknown" in resto:
            out["comentario"] = "condition unknown"
        return out
    m1 = re.match(rf"(?P<v>{NUM})\s*(?P<u>{'' if tipo == 'adim' else '[A-Za-zµ°/³²%-]+'})", resto) if tipo != "adim" else re.match(rf"(?P<v>{NUM})(?P<u>)", resto)
    if not m1:
        return out
    u1 = m1.group("u").strip() or None
    if tipo == "adim" and re.match(r"\s*%", resto[m1.end():]):          # el '%' es unidad
        u1 = "%"
        m1 = re.match(rf"(?P<v>{NUM})\s*%", resto)
    out["metrico"] = {"valor": m1.group("v").strip(), "unidad": u1}
    rest = resto[m1.end():].strip()
    if tipo == "adim":
        m2 = re.match(rf"(?P<v>{NUM})\s*(?P<u>%)?", rest)
        un = "%" if m2 and m2.group("u") else None
    else:
        m2 = re.match(rf"(?P<v>{NUM})\s*(?P<u>[A-Za-zµ°/³²·-]+(?:-[A-Za-z°³²/-]+)*)", rest)
        un = m2.group("u") if m2 else None
    if m2:
        out["ingles"] = {"valor": m2.group("v").strip(), "unidad": un}
        rest = rest[m2.end():].strip()
    if rest:
        out["comentario"] = rest
    return out


def _no_interpretado(cuerpo, nombres):
    """Fragmentos del cuerpo que empiezan con un nombre de propiedad desconocido: se devuelven textuales."""
    # se consideran conocidos los nombres de PROPIEDADES y elementos; cualquier otro renglón numérico se lista
    restos = re.sub(rf"(?:{nombres}|{ELEMENTOS}).*?(?=(?:{nombres}|{ELEMENTOS})|\|\s|$)", " ", cuerpo)
    restos = re.sub(r"\|", " ", restos)
    restos = re.sub(r"\s+", " ", restos).strip()
    return [restos] if restos and re.search(r"\d", restos) else []
