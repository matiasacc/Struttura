"""Biblioteca personal de materiales: UN solo archivo CSV  (006_Biblioteca/materiales.csv, o el que indique la variable STRUTTURA_BIBLIOTECA).
Las fichas las carga Claude en ese CSV cuando se las pasás (PDF o texto); el programa solo lee el CSV."""
import csv
import os
import shutil
from pathlib import Path

from .lector_fichas import parsear

COLUMNAS = ["n", "ref", "nombre", "categorias", "notas_material", "palabras_clave", "E_MPa", "G_MPa", "nu", "fy_MPa", "sut_MPa", "rho_kg_m3",
            "dureza_HB", "dureza_HK", "dureza_HRB", "dureza_HRC", "dureza_HV", "alargamiento_pct", "reduccion_area_pct", "K_MPa", "maquinabilidad_pct",
            "resistividad", "conductividad", "cte_lineal", "calor_especifico", "composicion", "comentarios", "sin_interpretar", "fuente"]


class ErrorBiblioteca(Exception):
    pass


def archivo() -> Path:
    env = os.environ.get("STRUTTURA_BIBLIOTECA")
    return Path(env) if env else Path(__file__).resolve().parents[3] / "006_Biblioteca" / "materiales.csv"


def _leer():
    p = archivo()
    if not p.is_file():
        return []
    with p.open(encoding="utf-8-sig", newline="") as fh:
        return [{k: (v or "").strip() for k, v in r.items()} for r in csv.DictReader(fh, delimiter=";")]


def listar():
    return [(r["n"], r["nombre"]) for r in _leer()]


def fila(r):
    """Fila del CSV como dict de textos."""
    return {c: r.get(c, "") for c in COLUMNAS}


def _fila_de_ficha(f, fuente=None):
    P, g = f["propiedades"], f["origen_pdf"] if "origen_pdf" in f else None
    out, com = {c: "" for c in COLUMNAS}, []
    out.update(ref=f["ref"], nombre=f["nombre"], categorias=(f["categorias"] or "").replace(";", " /"), notas_material=f["notas"] or "", palabras_clave=f["palabras_clave"] or "", fuente=fuente or f"ficha {f['ref']}")

    def prop(clave, col, factor=None, unidades=(), etiqueta=None):
        if clave not in P:
            return
        x = P[clave][0]
        m = x.get("metrico")
        if not m:
            return
        val = m["valor"]
        if factor is not None:
            try:
                ok = m.get("unidad") in unidades or (not unidades)
                out[col] = repr(round(float(val) * factor[m.get("unidad")], 10)).rstrip("0").rstrip(".") if ok else ""
            except (ValueError, KeyError):
                out[col] = ""
                com.append(f"{etiqueta or clave}: {val} {m.get('unidad') or ''} (rango o unidad no convertida; no se usa en el cálculo)")
        else:
            out[col] = val if m.get("unidad") in (None, "%") else f"{val} {m['unidad']}"
        if x.get("comentario"):
            com.append(f"{etiqueta or clave}: {x['comentario']}")
    prop("E", "E_MPa", {"GPa": 1e3, "MPa": 1.0}, ("GPa", "MPa"), "E")
    prop("G", "G_MPa", {"GPa": 1e3, "MPa": 1.0}, ("GPa", "MPa"), "G")
    prop("nu", "nu", None, (), "nu")
    prop("sy", "fy_MPa", {"MPa": 1.0, "GPa": 1e3}, ("MPa", "GPa"), "fy")
    prop("sut", "sut_MPa", {"MPa": 1.0, "GPa": 1e3}, ("MPa", "GPa"), "sut")
    prop("densidad", "rho_kg_m3", {"g/cc": 1e3}, ("g/cc",), "densidad")
    for clave, col in (("dureza_brinell", "dureza_HB"), ("dureza_knoop", "dureza_HK"), ("dureza_rockwell_b", "dureza_HRB"), ("dureza_rockwell_c", "dureza_HRC"),
                       ("dureza_vickers", "dureza_HV"), ("alargamiento", "alargamiento_pct"), ("reduccion_area", "reduccion_area_pct"), ("maquinabilidad", "maquinabilidad_pct")):
        prop(clave, col, None, (), clave.replace("_", " "))
    prop("K", "K_MPa", {"GPa": 1e3, "MPa": 1.0}, ("GPa", "MPa"), "K")
    prop("conductividad", "conductividad", None, (), "conductividad")
    prop("resistividad", "resistividad", None, (), "resistividad")        # valor único (si trae temperaturas, se completa abajo)
    for clave, col in (("cte_lineal", "cte_lineal"), ("calor_especifico", "calor_especifico"), ("resistividad", "resistividad")):
        if clave in P and P[clave][0].get("valores"):
            out[col] = " | ".join(f"{v['valor']} {v['unidad']} @ {v['condicion']}" for v in P[clave][0]["valores"])
            if P[clave][0].get("comentario"):
                com.append(f"{clave.replace('_', ' ')}: {P[clave][0]['comentario']}")
    out["composicion"] = " | ".join(f"{c['elemento']} {c['valor']}" + (f" ({c['comentario']})" if c["comentario"] else "") for c in f["composicion"])
    out["comentarios"] = " | ".join(com)
    out["sin_interpretar"] = " | ".join(f["no_interpretado"])
    return out


def agregar(ruta_ficha, copiar_a=None, fuente=None):
    """(Herramienta de Claude) Lee una ficha (PDF o TXT) y agrega/actualiza su fila en el CSV.  Devuelve (fila, avisos)."""
    from .lector_fichas import texto_de_pdf
    ruta = Path(ruta_ficha)
    texto = texto_de_pdf(ruta) if ruta.suffix.lower() == ".pdf" else ruta.read_text(encoding="utf-8", errors="replace")
    f = parsear(texto)
    if not f["ref"] or not f["nombre"]:
        raise ErrorBiblioteca("no pude leer el código o el nombre de la ficha")
    r = _fila_de_ficha(f, fuente)
    av = [f"la ficha no trae {t}" for c, t in (("E_MPa", "E"), ("fy_MPa", "fy"), ("sut_MPa", "sut"), ("rho_kg_m3", "densidad")) if not r[c]]
    if r["sin_interpretar"]:
        av.append(f"texto sin interpretar: {r['sin_interpretar'][:200]}")
    previas = _leer()
    igual = [x for x in previas if x["ref"].lower() == r["ref"].lower()]
    if igual:                                                           # misma ficha: se actualiza y conserva su número
        r["n"] = igual[0]["n"]
    else:                                                               # número nuevo: nunca se renumera ni se reutiliza
        usados = [int(x["n"]) for x in previas if x["n"].isdigit()]
        r["n"] = str(max(usados + [_ultimo()]) + 1)
        _ultimo(int(r["n"]))
    filas = [x for x in previas if x["ref"].lower() != r["ref"].lower()] + [r]
    filas.sort(key=lambda x: int(x["n"]) if x["n"].isdigit() else 10**9)
    archivo().parent.mkdir(parents=True, exist_ok=True)
    with archivo().open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNAS, delimiter=";")
        w.writeheader()
        w.writerows(fila(x) for x in filas)
    if copiar_a and ruta.suffix.lower() == ".pdf":
        Path(copiar_a).mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ruta, Path(copiar_a) / f"{r['ref']}.pdf")
    return r, av


def _ultimo(nuevo=None):
    """Mayor número asignado alguna vez (guardado junto al CSV), para no reutilizar números de filas borradas."""
    p = archivo().with_suffix(".ultimo")
    if nuevo is not None:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(str(nuevo))
        return nuevo
    try:
        return int(p.read_text().strip())
    except (OSError, ValueError):
        return 0


def cargar(n):
    """Busca por número de la biblioteca (lo normal) o por el código de la ficha."""
    for r in _leer():
        if r["n"] == str(n).strip() or r["ref"].lower() == str(n).strip().lower():
            return r
    raise ErrorBiblioteca(f"el material '{n}' no está en la biblioteca ({archivo()}).  Pasale la ficha del material a Claude para cargarla, o agregá la fila a mano.")


def _num(txt, ref, campo):
    if txt == "":
        return None
    try:
        return float(txt.replace(",", "."))
    except ValueError:
        raise ErrorBiblioteca(f"'{ref}': {campo} dice '{txt}', que no es un número; corregilo en el CSV o cargalo a mano en MATERIALES")


def datos(ref):
    """Valores para el solver (MPa y kg/m³):  E, G, nu, fy, sut, rho, más 'fuente'.  Un dato vacío en el CSV queda None (no se completa)."""
    r = cargar(ref)
    return {"E": _num(r["E_MPa"], ref, "E_MPa"), "G": _num(r["G_MPa"], ref, "G_MPa"), "nu": _num(r["nu"], ref, "nu"), "fy": _num(r["fy_MPa"], ref, "fy_MPa"),
            "sut": _num(r["sut_MPa"], ref, "sut_MPa"), "rho": _num(r["rho_kg_m3"], ref, "rho_kg_m3"), "fuente": f"biblioteca n.º {r['n']}: {r['nombre']}"}


def datos_modelo(lib, unidad_fuerza, unidad_longitud):
    """Datos de la ficha en las unidades del modelo (E, G, fy, sut; rho queda en kg/m³).  Lo usan todos los programas.  Levanta ErrorBiblioteca si no se puede."""
    from ..portico3d.entrada import _U_FUERZA, _U_LONG
    uf, ul = unidad_fuerza.strip().lower(), unidad_longitud.strip().lower()
    if uf not in _U_FUERZA or ul not in _U_LONG:
        raise ErrorBiblioteca(f"no sé convertir las unidades '{unidad_fuerza}' / '{unidad_longitud}' para leer la biblioteca; cargá los valores a mano")
    d = datos(lib)
    k = 1e6 * _U_LONG[ul] ** 2 / _U_FUERZA[uf]                       # MPa -> fuerza/longitud² del modelo
    for c in ("E", "G", "fy", "sut"):
        if d[c] is not None:
            d[c] *= k
    return d
