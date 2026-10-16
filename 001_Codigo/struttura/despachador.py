"""Despachador de Struttura:  python struttura.py ARCHIVO.csv [opciones]

Elige solo el programa según el archivo:
    - PROYECTO / tipo;portico        →  pórtico plano   (columnas de APOYOS: nodo;ux;uy;phi)
    - PROYECTO / tipo;reticulado     →  reticulado plano (columnas de APOYOS: nodo;ux;uy)
    - PROYECTO / tipo;emparrillado   →  emparrillado    (columnas de APOYOS: nodo;uz;phix;phiy)
    - PROYECTO / tipo;portico3d      →  pórtico espacial (columnas de APOYOS: nodo;ux;uy;uz;phix;phiy;phiz)
    - python struttura.py --editor [ARCHIVO.csv]   →  editor visual (página local en el navegador; carga y revisa el modelo y lo calcula)
    - python struttura.py --biblioteca listar | ver CODIGO   →  biblioteca personal de materiales (006_Biblioteca/materiales.csv)
    - PROYECTO / tipo;soldadura      →  verificación rápida de soldaduras de filete   (o:  --soldadura "circulo d=50.8 Vz=3000 electrodo=E70 w=3")
Si el archivo no dice el tipo, se deduce del encabezado de APOYOS (con phi: pórtico; solo ux;uy: reticulado).  También se puede forzar con  --tipo.
"""
import csv
import sys
import unicodedata
from pathlib import Path


def _norm(s):
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn").lower().strip().strip("[]:").strip()


def detectar_tipo(ruta):
    """'portico' | 'emparrillado' | None (no se pudo decidir)."""
    try:
        datos = Path(ruta).read_bytes()
    except OSError:
        return None
    try:
        texto = datos.decode("utf-8-sig")
    except UnicodeDecodeError:
        texto = datos.decode("cp1252", errors="replace")
    lineas = [l for l in texto.splitlines() if l.strip() and not l.lstrip().startswith("#")]
    delim = ";" if any(";" in l for l in lineas) else ("\t" if any("\t" in l for l in lineas) else ",")
    filas = [[c.strip() for c in next(csv.reader([l], delimiter=delim))] for l in lineas]
    en, tipo = None, None
    for k, f in enumerate(filas):
        f = [c for c in f if c != ""] or [""]
        if len(f) == 1:                                   # título de bloque
            en = _norm(f[0])
            if en == "apoyos" and k + 1 < len(filas):
                cab = [_norm(c) for c in filas[k + 1]]
                if "ux" in cab and "uz" in cab:
                    return tipo if tipo in ("portico3d",) else "portico3d"
                if "ux" in cab:
                    return tipo or ("portico" if "phi" in cab else "reticulado")
                if "uz" in cab:
                    return tipo or "emparrillado"
            continue
        if en == "proyecto" and _norm(f[0]) == "tipo" and len(f) > 1:
            tipo = _norm(f[1])
            if tipo in ("portico", "emparrillado", "reticulado", "portico3d", "soldadura"):
                return tipo
    return tipo


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--editor" in argv:
        from .editor.servidor import main as m
        return m(argv)
    if "--biblioteca" in argv:
        from .biblioteca.__main__ import main as m
        return m(argv)
    if "--soldadura" in argv:
        from .soldadura.__main__ import main as m
        return m(argv)
    tipo = None
    if "--tipo" in argv:
        i = argv.index("--tipo")
        tipo = argv[i + 1] if i + 1 < len(argv) else None
        del argv[i:i + 2]
        if tipo not in ("portico", "emparrillado", "reticulado", "portico3d", "soldadura"):
            print("--tipo debe ser portico, portico3d, reticulado, emparrillado o soldadura", file=sys.stderr)
            return 1
    if tipo is None:
        archivos = [a for a in argv if not a.startswith("-") and Path(a).suffix.lower() in (".csv", ".txt")]
        if archivos:
            tipo = detectar_tipo(archivos[0])
        if tipo is None and archivos:
            print("No pude deducir el tipo de estructura.  Agregá en el bloque PROYECTO la línea "
                  "'tipo;portico', 'tipo;reticulado' o 'tipo;emparrillado' (o usá --tipo).", file=sys.stderr)
            return 1
    if tipo == "soldadura":
        from .soldadura.__main__ import main as m
    elif tipo == "portico3d":
        from .portico3d.__main__ import main as m
    elif tipo == "portico":
        from .portico.__main__ import main as m
    elif tipo == "reticulado":
        from .reticulado.__main__ import main as m
    else:
        from .emparrillado.__main__ import main as m
    return m(argv)
