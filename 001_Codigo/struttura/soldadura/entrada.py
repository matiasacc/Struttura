"""Entrada del modo rápido de soldaduras: CSV mínimo (tipo;soldadura) o una línea de comando.

CSV:
    PROYECTO     proyecto;...   unidad_fuerza;N   unidad_longitud;mm   tipo;soldadura
    ELECTRODOS   id;sut;sy;tau_adm;lib    (opcional: electrodos propios, en unidades de tensión del modelo; lib = n.º de 006_Biblioteca/electrodos.csv)
    SOLDADURAS   id;tipo;disposicion;b;d;arcos;esp;segmentos;electrodo;w;sy_base;lib;t_gruesa;t_fina     (tipo = filete | tope; esp = espesor de las piezas: en tope es la garganta; en filete solo dibuja el contorno)
    CARGAS       soldadura;caso;N;Vy;Vz;T;My;Mz;yp;zp
Línea de comando:  python struttura.py --soldadura "circulo d=50.8 Vz=3000 My=200000 electrodo=E70 w=3"
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ..emparrillado.entrada import ErrorDeEntrada, _num, _partir_bloques, _tabla
from ..portico3d.entrada import _U_FUERZA, _U_LONG
from .datos import fac_tension
from .grupo import DISPOSICIONES, ErrorSoldadura, crear
from .verificar import Soldadura

TITULOS = ("PROYECTO", "ELECTRODOS", "SOLDADURAS", "CARGAS")
COMP = ("N", "Vy", "Vz", "T", "My", "Mz")


@dataclass
class ModeloSoldadura:
    config: dict
    soldaduras: list
    cargas: list                      # [(id_soldadura, caso, (N,Vy,Vz,T,My,Mz), punto|None)]
    electrodos: dict = field(default_factory=dict)      # propios, en unidades de tensión del modelo
    avisos: list = field(default_factory=list)


def sy_base_de(r, ctx, n, uf, ul):
    """sy_base de la fila: lo escrito a mano manda; si no, el fy del material n.º 'lib' de la biblioteca de materiales."""
    v = _num(r.get("sy_base"), ctx, n, "sy_base", obligatorio=False)
    lib = (r.get("lib") or "").strip()
    if v is not None or not lib:
        return v
    from ..biblioteca.biblioteca import ErrorBiblioteca
    from ..biblioteca.electrodos import sy_base
    try:
        return sy_base(lib, uf, ul)
    except ErrorBiblioteca as e:
        raise ErrorDeEntrada(f"{ctx}, línea {n}: {e}")


def leer_electrodos(bl, uf, ul):
    """Bloque ELECTRODOS: id;sut;sy;tau_adm;lib.  'lib' = número de la biblioteca de electrodos (completa lo que no se escribió a mano).
    Devuelve {id: (sut, sy, tau_adm)} en MPa."""
    from ..biblioteca.biblioteca import ErrorBiblioteca
    from ..biblioteca.electrodos import datos as dato_lib
    out = {}
    filas = _tabla(bl, "ELECTRODOS", ["id"], requerido=False) or []
    if not filas:
        return out
    k = fac_tension(uf, ul)
    for n, r in filas:
        v = lambda c: _num(r.get(c), "ELECTRODOS", n, c, obligatorio=False)
        cv = lambda x: None if x is None else x / k                                          # se guarda en MPa
        base = (None, None, None)
        if (r.get("lib") or "").strip():
            try:
                base = dato_lib(r["lib"])
            except ErrorBiblioteca as e:
                raise ErrorDeEntrada(f"Bloque ELECTRODOS, línea {n}: {e}")
        mano = (cv(v("sut")), cv(v("sy")), cv(v("tau_adm")))
        fin = tuple(m if m is not None else b for m, b in zip(mano, base))
        if fin[2] is None:
            raise ErrorDeEntrada(f"Bloque ELECTRODOS, línea {n}: falta tau_adm (a mano o con lib)")
        out[r["id"].strip()] = fin
    return out


def _unidades(config):
    uf, ul = config["unidad_fuerza"].lower(), config["unidad_longitud"].lower()
    if uf not in _U_FUERZA or ul not in _U_LONG:
        raise ErrorDeEntrada(f"unidades no admitidas ('{config['unidad_fuerza']}', '{config['unidad_longitud']}'): fuerza {', '.join(_U_FUERZA)}; longitud {', '.join(_U_LONG)}")
    config["unidad_fuerza"], config["unidad_longitud"] = uf, ul


def _crear_soldadura(id_, r, ctx, n, cfg, extra):
    """r: dict de textos."""
    num = lambda c: _num(r.get(c), ctx, n, c, obligatorio=False)
    p = {c: num(c) for c in ("b", "d", "esp")}
    if r.get("arcos", "").strip():
        p["arcos"] = r["arcos"].strip()
    if r.get("segmentos", "").strip():
        p["segmentos"] = r["segmentos"]
    elec = (r.get("electrodo") or "").strip()
    if not elec:
        raise ErrorDeEntrada(f"{ctx}, línea {n}: falta el electrodo")
    tipo = (r.get("tipo") or "filete").strip().lower()
    if tipo not in ("filete", "tope"):
        raise ErrorDeEntrada(f"{ctx}, línea {n}: 'tipo' debe ser filete o tope")
    try:
        g = crear(r.get("disposicion", ""), p, tope=(tipo == "tope"))
    except ErrorSoldadura as e:
        raise ErrorDeEntrada(f"{ctx}, línea {n}: {e}")
    return Soldadura(id_, g, elec, num("w"), sy_base_de(r, ctx, n, cfg["unidad_fuerza"], cfg["unidad_longitud"]), num("t_gruesa"), num("t_fina"), tipo=tipo, esp=num("esp"))


def cargar_csv(ruta) -> ModeloSoldadura:
    ruta = Path(ruta)
    if not ruta.is_file():
        raise ErrorDeEntrada(f"No se encuentra el archivo '{ruta}'")
    bl = _partir_bloques(ruta, TITULOS)
    cfg = {"proyecto": ruta.stem, "unidad_fuerza": "N", "unidad_longitud": "mm", "tipo": "soldadura"}
    b = bl.get("proyecto")
    if b:
        for n, c in b["filas"]:
            if len(c) >= 2 and c[0].lower() in cfg:
                cfg[c[0].lower()] = c[1]
    _unidades(cfg)
    uf, ul = cfg["unidad_fuerza"], cfg["unidad_longitud"]
    avisos = []
    extra = leer_electrodos(bl, uf, ul)
    sols = []
    for n, r in _tabla(bl, "SOLDADURAS", ["id", "disposicion", "electrodo"]):
        sols.append(_crear_soldadura(r["id"], r, "Bloque SOLDADURAS", n, cfg, extra))
    if len({s.id for s in sols}) != len(sols):
        raise ErrorDeEntrada("Bloque SOLDADURAS: hay ids repetidos")
    cargas = []
    for n, r in _tabla(bl, "CARGAS", ["caso"]) or []:
        sid = (r.get("soldadura") or "").strip()
        if not sid:
            if len(sols) != 1:
                raise ErrorDeEntrada(f"Bloque CARGAS, línea {n}: indicá a qué soldadura corresponde (columna 'soldadura')")
            sid = sols[0].id
        if sid not in {s.id for s in sols}:
            raise ErrorDeEntrada(f"Bloque CARGAS, línea {n}: la soldadura '{sid}' no existe")
        E = tuple(_num(r.get(c.lower()), "CARGAS", n, c, obligatorio=False, defecto=0.0) for c in COMP)
        yp, zp = _num(r.get("yp"), "CARGAS", n, "yp", False), _num(r.get("zp"), "CARGAS", n, "zp", False)
        punto = None if (yp is None and zp is None) else (yp or 0.0, zp or 0.0)
        cargas.append((sid, r["caso"], E, punto))
    if not cargas:
        raise ErrorDeEntrada("Bloque CARGAS: no hay cargas")
    return ModeloSoldadura(cfg, sols, cargas, extra, avisos)


def desde_linea(texto: str) -> ModeloSoldadura:
    """'circulo d=50.8 Vz=3000 My=200000 electrodo=E70 w=3 [uf=N ul=mm sy_base=.. t_gruesa=.. t_fina=.. yp= zp= tau_adm=..]'"""
    tok = texto.replace(",", ".").split()
    if not tok:
        raise ErrorDeEntrada("--soldadura: falta la disposición (ej.: 'circulo d=50.8 Vz=3000 electrodo=E70 w=3')")
    disp, kv = tok[0], {}
    for t in tok[1:]:
        if "=" not in t:
            raise ErrorDeEntrada(f"--soldadura: '{t}' no tiene la forma clave=valor")
        k, v = t.split("=", 1)
        kv[k.strip()] = v.strip()
    low = {k.lower(): k for k in kv}
    get = lambda c: kv.get(low.get(c.lower(), ""), None)
    cfg = {"proyecto": "Soldadura (modo rápido)", "unidad_fuerza": get("uf") or "N", "unidad_longitud": get("ul") or "mm", "tipo": "soldadura"}
    _unidades(cfg)
    usados = {"lib", "uf", "ul", "electrodo", "w", "sy_base", "t_gruesa", "t_fina", "yp", "zp", "tau_adm", "segmentos", "b", "d", "arcos", "esp", "tipo", "n", "vy", "vz", "t", "my", "mz", "v"}
    raros = [k for k in kv if k.lower() not in usados]
    if raros:
        raise ErrorDeEntrada(f"--soldadura: parámetros desconocidos: {', '.join(raros)}")
    p = {c: get(c) for c in ("b", "d", "esp")}
    if get("arcos"):
        p["arcos"] = get("arcos")
    if get("segmentos"):
        p["segmentos"] = get("segmentos").replace("_", " ")
    elec = get("electrodo")
    if not elec:
        raise ErrorDeEntrada("--soldadura: falta electrodo=E70 (o electrodo=propio tau_adm=...)")
    extra = {}
    try:
        p = {k: (float(v) if v not in (None, "") and k not in ("segmentos", "arcos") else v) for k, v in p.items()}
        fl = lambda c: None if get(c) is None else float(get(c))
        if get("tau_adm"):
            extra[elec] = (None, None, fl("tau_adm") / fac_tension(cfg["unidad_fuerza"], cfg["unidad_longitud"]))
        tipo = (get("tipo") or "filete").lower()
        if tipo not in ("filete", "tope"):
            raise ErrorDeEntrada("--soldadura: tipo debe ser filete o tope")
        g = crear(disp, p, tope=(tipo == "tope"))
        syb = fl("sy_base")
        if syb is None and get("lib"):
            from ..biblioteca.biblioteca import ErrorBiblioteca
            from ..biblioteca.electrodos import sy_base as _syb
            try:
                syb = _syb(get("lib"), cfg["unidad_fuerza"], cfg["unidad_longitud"])
            except ErrorBiblioteca as e:
                raise ErrorDeEntrada(f"--soldadura: {e}")
        sol = Soldadura("S1", g, elec, fl("w"), syb, fl("t_gruesa"), fl("t_fina"), tipo=tipo, esp=fl("esp"))
        N, Vy, Vz, T, My, Mz = (fl(c) or 0.0 for c in ("N", "Vy", "Vz", "T", "My", "Mz"))
        if fl("V"):
            Vz = fl("V")
        yp, zp = fl("yp"), fl("zp")
    except ValueError as e:
        raise ErrorDeEntrada(f"--soldadura: valor no numérico ({e})")
    except ErrorSoldadura as e:
        raise ErrorDeEntrada(f"--soldadura: {e}")
    punto = None if (yp is None and zp is None) else (yp or 0.0, zp or 0.0)
    return ModeloSoldadura(cfg, [sol], [("S1", "Carga", (N, Vy, Vz, T, My, Mz), punto)], extra, [])
