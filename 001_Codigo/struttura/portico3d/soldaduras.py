"""Soldaduras en los extremos de las barras del pórtico 3D (bloques SOLDADURAS y ELECTRODOS).

    SOLDADURAS   id;tipo;esp;barra;extremo;disposicion;b;d;arcos;segmentos;oy;oz;electrodo;w;sy_base;lib;t_gruesa;t_fina
    ELECTRODOS   id;sut;sy;tau_adm;lib          (opcional, aportes propios, en unidades de tensión del modelo)

La disposición se define en el plano de la sección de la barra (y, z locales).  Su origen coincide con el baricentro de la barra salvo que se
indique (oy, oz) = posición del origen de la disposición respecto del baricentro de la barra.  Si faltan, se toman de la sección de la barra:
'circulo' con d = diámetro del tubo/barra redonda;  'rectangulo', 'costados', 'arriba_abajo' con b y d = b y h de la sección rectangular o del tubo rectangular.
Los esfuerzos son los de la cara +x de la barra en ese extremo (del solver), para cada caso y combinación.
"""
from __future__ import annotations

from ..emparrillado.entrada import ErrorDeEntrada, _num, _tabla
from ..soldadura.entrada import leer_electrodos, sy_base_de
from ..soldadura.grupo import ErrorSoldadura, crear
from ..soldadura.verificar import Soldadura, verificar

COLUMNAS = ("id", "tipo", "esp", "barra", "extremo", "disposicion", "b", "d", "arcos", "segmentos", "oy", "oz", "electrodo", "w", "sy_base", "lib", "t_gruesa", "t_fina")
COLUMNAS_ELECTRODOS = ("id", "sut", "sy", "tau_adm", "lib")


def contorno_seccion(sec, oy=0.0, oz=0.0):
    """Polilíneas del contorno de la sección de la barra, en coordenadas de la disposición (origen desplazado (oy, oz)); solo para dibujar."""
    import math
    circ = lambda d, n=120: [(d / 2 * math.cos(2 * math.pi * k / n), d / 2 * math.sin(2 * math.pi * k / n)) for k in range(n + 1)]
    rect = lambda b, h: [(-b / 2, -h / 2), (b / 2, -h / 2), (b / 2, h / 2), (-b / 2, h / 2), (-b / 2, -h / 2)]
    pls = []
    if sec.tipo in ("tubo", "circular"):
        d, t = sec.dim["d"], sec.dim.get("t") or 0.0
        pls = [circ(d)] + ([circ(d - 2 * t)] if t else [])
    elif sec.tipo == "rectangular":
        pls = [rect(sec.dim["b"], sec.dim["h"])]
    elif sec.tipo == "rect_hueca":
        b, h, t = sec.dim["b"], sec.dim["h"], sec.dim["t"]
        pls = [rect(b, h), rect(b - 2 * t, h - 2 * t)]
    elif sec.pared is not None:
        for y0, z0, y1, z1, t in sec.pared.segmentos():
            L = math.hypot(y1 - y0, z1 - z0)
            ny, nz = -(z1 - z0) / L * t / 2, (y1 - y0) / L * t / 2
            pls.append([(y0 + ny, z0 + nz), (y1 + ny, z1 + nz), (y1 - ny, z1 - nz), (y0 - ny, z0 - nz), (y0 + ny, z0 + nz)])
    return [[(y - oy, z - oz) for y, z in pl] for pl in pls]


def leer(bloques, barras, config):
    """Devuelve (lista de Soldadura, {electrodos propios en MPa})."""
    uf, ul = config["unidad_fuerza"], config["unidad_longitud"]
    extra = leer_electrodos(bloques, uf, ul)
    ids = {b.id: b for b in barras}
    sols = []
    for n, r in _tabla(bloques, "SOLDADURAS", ["id", "barra", "extremo", "disposicion", "electrodo"], requerido=False) or []:
        ctx = "Bloque SOLDADURAS"
        sid = r["id"].strip()
        if sid in {s.id for s in sols}:
            raise ErrorDeEntrada(f"{ctx}, línea {n}: la soldadura '{sid}' está repetida")
        if r["barra"] not in ids:
            raise ErrorDeEntrada(f"{ctx}, línea {n}: la barra '{r['barra']}' no existe")
        ext = r["extremo"].strip().lower()
        if ext not in ("i", "j"):
            raise ErrorDeEntrada(f"{ctx}, línea {n}: 'extremo' debe ser i o j")
        b = ids[r["barra"]]
        num = lambda c: _num(r.get(c), ctx, n, c, obligatorio=False)
        p = {c: num(c) for c in ("b", "d")}
        if (r.get("arcos") or "").strip():
            p["arcos"] = r["arcos"].strip()
        disp = r["disposicion"].strip()
        sec = b.sec
        tipo = (r.get("tipo") or "filete").strip().lower()
        if tipo not in ("filete", "tope"):
            raise ErrorDeEntrada(f"{ctx}, línea {n}: 'tipo' debe ser filete o tope")
        p["esp"] = num("esp")
        if p["d"] is None and disp.lower() in ("circulo", "arco") and sec.tipo in ("tubo", "circular"):
            p["d"] = sec.dim["d"]
        if tipo == "tope" and p["esp"] is None and sec.tipo in ("tubo", "rect_hueca"):
            p["esp"] = sec.dim["t"]                                       # espesor de la pared de la barra
        if disp.lower() in ("rectangulo", "costados", "arriba_abajo") and sec.tipo in ("rectangular", "rect_hueca"):
            p["b"] = p["b"] if p["b"] is not None else sec.dim["b"]
            p["d"] = p["d"] if p["d"] is not None else sec.dim["h"]
        if r.get("segmentos", "").strip():
            p["segmentos"] = r["segmentos"]
        try:
            g = crear(disp, p, tope=(tipo == "tope"))
        except ErrorSoldadura as e:
            raise ErrorDeEntrada(f"{ctx}, línea {n} (soldadura '{sid}'): {e}")
        elec = (r.get("electrodo") or "").strip()
        if not elec:
            raise ErrorDeEntrada(f"{ctx}, línea {n}: falta el electrodo")
        s = Soldadura(sid, g, elec, num("w"), sy_base_de(r, ctx, n, uf, ul), num("t_gruesa"), num("t_fina"), barra=b.id, extremo=ext, tipo=tipo, esp=p["esp"])
        s.oy, s.oz = num("oy") or 0.0, num("oz") or 0.0
        g.contorno = contorno_seccion(sec, s.oy, s.oz)
        sols.append(s)
    return sols, extra


def evaluar(modelo, resultados, esf_extremos):
    """{id_soldadura: [(caso, E, punto, resultado)]};  esf_extremos: {caso: esfuerzos_extremos(...)}."""
    uf, ul = modelo.config["unidad_fuerza"], modelo.config["unidad_longitud"]
    idx = {b.id: k for k, b in enumerate(modelo.barras)}
    out = {}
    for s in modelo.soldaduras:
        k = idx[s.barra]
        punto = None if (s.oy == 0 and s.oz == 0) else (-s.oy, -s.oz)        # la carga actúa en el baricentro de la barra
        lista = []
        for caso in resultados:
            E = [float(v) for v in esf_extremos[caso][k][s.extremo]]
            try:
                r = verificar(s, E, punto, uf, ul, modelo.electrodos)
            except ErrorSoldadura as e:
                raise ErrorSoldadura(f"soldadura '{s.id}' (barra {s.barra}, extremo {s.extremo}), caso '{caso}': {e}")
            lista.append((caso, E, punto, r))
        out[s.id] = lista
    return out
