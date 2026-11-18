"""Línea de comandos:   python struttura.py ARCHIVO.csv [-o CARPETA_DE_SALIDA] [--sin-graficos] [--solo-esquema]"""
from __future__ import annotations

import argparse
from .. import __version__
import csv
import sys
from pathlib import Path

import numpy as np

from .entrada import ErrorDeEntrada, NOMBRES_GDL, cargar_modelo
from .esfuerzos import esfuerzos, tensiones
from .informe import generar_html, generar_html_esquema
from .solver import ErrorEstructura, equilibrio, resolver, verificar


def _escribir_csv(ruta: Path, cabecera, filas, estilo: str):
    """estilo 'excel_es': separador ';' y coma decimal.  'estandar': ',' y punto."""
    delim = ";" if estilo == "excel_es" else ","

    def f(v):
        if isinstance(v, (float, np.floating)):
            s = repr(float(v))
            return s.replace(".", ",") if estilo == "excel_es" else s
        return str(v)

    with open(ruta, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh, delimiter=delim)
        w.writerow(cabecera)
        for fila in filas:
            w.writerow([f(v) for v in fila])


def exportar_csv(modelo, resultados, info, carpeta: Path, sold=None):
    est = modelo.config["csv_salida"]
    desp, reac, esfz, tens, resr = [], [], [], [], []
    for nombre, res in resultados.items():
        e = esfuerzos(modelo, res)
        t = tensiones(modelo, e)
        for k, n in enumerate(modelo.nodos):
            desp.append([nombre, n.id, *res.u[k]])
            if modelo.restr[k].any():
                reac.append([nombre, n.id, *[res.R[k, c] if modelo.restr[k, c] else "" for c in range(3)]])
            if modelo.res_mask[k].any():
                resr.append([nombre, n.id, *[res.Rk[k, c] if modelo.res_mask[k, c] else "" for c in range(3)]])
        for k, b in enumerate(modelo.barras):
            esfz.append([nombre, b.id, modelo.nodos[b.i].id, modelo.nodos[b.j].id,
                         e["V"][k], e["Vj"][k], e["T"][k], e["Mi"][k], e["Mj"][k],
                         e["Mmax"][k], e["xMmax"][k], e["Mmin"][k], e["xMmin"][k]])
            d = t[k]
            tens.append([nombre, b.id] + [("" if d[c] is None else d[c])
                                          for c in ("sig_i", "sig_j", "sig_max", "tau_t", "tau_v", "vm", "n_fy", "n_adm")])
    _escribir_csv(carpeta / "desplazamientos.csv", ["caso", "nodo", "uz", "phix", "phiy"], desp, est)
    _escribir_csv(carpeta / "reacciones.csv", ["caso", "nodo", "Rz", "Mx", "My"], reac, est)
    if resr:
        _escribir_csv(carpeta / "resortes.csv", ["caso", "nodo", "Fz", "Mx", "My"], resr, est)
    _escribir_csv(carpeta / "esfuerzos.csv", ["caso", "barra", "nodo_i", "nodo_j", "V_i", "V_j", "T", "M_i", "M_j",
                                           "M_max", "x_M_max", "M_min", "x_M_min"], esfz, est)
    _escribir_csv(carpeta / "tensiones.csv",
                  ["caso", "barra", "sigma_i", "sigma_j", "sigma_max", "tau_torsion", "tau_corte", "sigma_VM_max", "CS_fluencia", "CS_admisible"],
                  tens, est)
    if sold:
        from ..soldadura import en_modelo
        en_modelo.exportar(modelo, sold, carpeta, _escribir_csv, est)
    cab = [f"{modelo.nodos[k // 3].id}:{NOMBRES_GDL[k % 3]}" for k in range(3 * modelo.n)]
    _escribir_csv(carpeta / "matriz_K.csv", [""] + cab, [[cab[i], *info.K[i]] for i in range(3 * modelo.n)], est)


def _evaluar_soldaduras(modelo, resultados, tipo):
    """None si no hay soldaduras; False si hubo error (ya informado); si no, el resultado de evaluarlas."""
    if not modelo.soldaduras:
        return None
    from ..soldadura import en_modelo
    from ..soldadura.grupo import ErrorSoldadura
    try:
        return en_modelo.evaluar(modelo, resultados, tipo)
    except ErrorSoldadura as e:
        print(f"\nERROR EN SOLDADURAS\n  {e}\n", file=sys.stderr)
        return False


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="struttura.py",
                                 description="Emparrillados planos por el método matricial de rigidez.")
    ap.add_argument("--version", action="version", version=f"Struttura {__version__}")
    ap.add_argument("archivo", help="archivo CSV con todos los datos (bloques con título)")
    ap.add_argument("-o", "--salida", help="carpeta de salida (por defecto: <archivo>_salida)")
    ap.add_argument("--sin-graficos", action="store_true", help="informe sin gráficos (más rápido)")
    ap.add_argument("--solo-esquema", action="store_true",
                    help="no calcula: dibuja datos y cargas para revisar la entrada")
    a = ap.parse_args(argv)

    try:
        modelo = cargar_modelo(a.archivo)
    except ErrorDeEntrada as e:
        print(f"\nERROR EN LOS DATOS DE ENTRADA\n  {e}\n", file=sys.stderr)
        return 1
    for av in modelo.avisos:
        print(av if av.startswith("Nota: ") else f"Aviso: {av}")

    ruta = Path(a.archivo)
    salida = Path(a.salida) if a.salida else ruta.with_name(ruta.stem + "_salida")
    salida.mkdir(parents=True, exist_ok=True)

    if a.solo_esquema:
        try:
            verificar(modelo)
            msg = None
        except ErrorEstructura as e:
            msg = str(e)
            print(f"\nATENCIÓN (estabilidad)\n  {msg}\n")
        (salida / "esquema.html").write_text(generar_html_esquema(modelo, msg), encoding="utf-8")
        print(f"Revisión de datos: {salida / 'esquema.html'}")
        return 0

    try:
        resultados, info = resolver(modelo)
    except ErrorEstructura as e:
        print(f"\nERROR DE ESTRUCTURA\n  {e}\n", file=sys.stderr)
        return 2

    sold = _evaluar_soldaduras(modelo, resultados, "emparrillado")
    if sold is False:
        return 1
    html = generar_html(modelo, resultados, info, con_graficos=not a.sin_graficos, sold=sold)
    (salida / "informe.html").write_text(html, encoding="utf-8")
    exportar_csv(modelo, resultados, info, salida, sold)

    print(f"Struttura v{__version__} · Emparrillado  |  Proyecto: {modelo.config['proyecto']}")
    print(f"  {modelo.n} nodos, {len(modelo.barras)} barras, {len(resultados)} caso(s)/combinación(es)")
    if getattr(modelo, "peso_propio", None):
        pp = modelo.peso_propio
        print(f"  Peso propio en el caso '{pp['caso']}' (gravedad {pp['gravedad']}): masa {pp['masa']:.4g} kg, peso {pp['peso']:.4g} {modelo.config['unidad_fuerza']}")
    for nombre, res in resultados.items():
        eq = equilibrio(modelo, res)
        estado = "OK" if eq["rel"] < 1e-8 else "REVISAR"
        print(f"  {nombre:>14}: max|uz| = {np.abs(res.u[:, 0]).max():.4g}   equilibrio {eq['rel']:.1e} [{estado}]")
    if sold:
        from ..soldadura import en_modelo
        print(en_modelo.resumen_consola(modelo, sold))
    print(f"\nInforme: {salida / 'informe.html'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
