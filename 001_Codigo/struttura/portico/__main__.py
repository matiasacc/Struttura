"""Línea de comandos:  python -m struttura.portico ARCHIVO.csv   (normalmente se usa  python struttura.py ARCHIVO.csv)"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

from struttura.emparrillado.__main__ import _escribir_csv

from .. import __version__
from .entrada import ErrorDeEntrada, NOMBRES_GDL, cargar_modelo
from .esfuerzos import esfuerzos, tensiones
from .informe import generar_html, generar_html_esquema
from .solver import ErrorEstructura, equilibrio, resolver, verificar


def exportar_csv(modelo, resultados, info, carpeta: Path, sold=None):
    est = modelo.config["csv_salida"]
    desp, reac, esf_, tens, resr = [], [], [], [], []
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
            esf_.append([nombre, b.id, modelo.nodos[b.i].id, modelo.nodos[b.j].id, e["N"][k], e["Nj"][k], e["V"][k], e["Vj"][k],
                         e["Mi"][k], e["Mj"][k], e["Mmax"][k], e["xMmax"][k], e["Mmin"][k], e["xMmin"][k]])
            d = t[k]
            tens.append([nombre, b.id] + [("" if d[c] is None else d[c]) for c in ("sig_t", "sig_c", "tau_v", "vm", "n_fy", "n_adm")])
    _escribir_csv(carpeta / "desplazamientos.csv", ["caso", "nodo", "ux", "uy", "phi"], desp, est)
    _escribir_csv(carpeta / "reacciones.csv", ["caso", "nodo", "Rx", "Ry", "M"], reac, est)
    if resr:
        _escribir_csv(carpeta / "resortes.csv", ["caso", "nodo", "Fx", "Fy", "M"], resr, est)
    _escribir_csv(carpeta / "esfuerzos.csv", ["caso", "barra", "nodo_i", "nodo_j", "N_i", "N_j", "V_i", "V_j", "M_i", "M_j",
                                           "M_max", "x_M_max", "M_min", "x_M_min"], esf_, est)
    _escribir_csv(carpeta / "tensiones.csv", ["caso", "barra", "sigma_traccion_max", "sigma_compresion_max", "tau_corte",
                                           "sigma_VM_max", "CS_fluencia", "CS_admisible"], tens, est)
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
    ap = argparse.ArgumentParser(prog="struttura.py", description="Pórticos planos por el método matricial de rigidez.")
    ap.add_argument("--version", action="version", version=f"Struttura {__version__}")
    ap.add_argument("archivo", help="archivo CSV con todos los datos (bloques con título)")
    ap.add_argument("-o", "--salida", help="carpeta de salida (por defecto: <archivo>_salida)")
    ap.add_argument("--sin-graficos", action="store_true", help="informe sin gráficos (más rápido)")
    ap.add_argument("--solo-esquema", action="store_true", help="no calcula: dibuja datos y cargas para revisar la entrada")
    a = ap.parse_args(argv)
    try:
        modelo = cargar_modelo(a.archivo)
    except ErrorDeEntrada as e:
        print(f"\nERROR EN LOS DATOS DE ENTRADA\n  {e}\n", file=sys.stderr)
        return 1
    for av in modelo.avisos:
        print(f"Aviso: {av}")
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
    sold = _evaluar_soldaduras(modelo, resultados, "portico")
    if sold is False:
        return 1
    (salida / "informe.html").write_text(generar_html(modelo, resultados, info, con_graficos=not a.sin_graficos, sold=sold), encoding="utf-8")
    exportar_csv(modelo, resultados, info, salida, sold)
    print(f"Struttura v{__version__} · Pórtico plano  |  Proyecto: {modelo.config['proyecto']}")
    print(f"  {modelo.n} nodos, {len(modelo.barras)} barras, {len(resultados)} caso(s)/combinación(es)")
    if getattr(modelo, "peso_propio", None):
        pp = modelo.peso_propio
        print(f"  Peso propio en el caso '{pp['caso']}' (gravedad {pp['gravedad']}): masa {pp['masa']:.4g} kg, peso {pp['peso']:.4g} {modelo.config['unidad_fuerza']}")
    for nombre, res in resultados.items():
        eq = equilibrio(modelo, res)
        print(f"  {nombre:>14}: max|u| = {np.abs(res.u[:, :2]).max():.4g}   equilibrio {eq['rel']:.1e} [{'OK' if eq['rel'] < 1e-8 else 'REVISAR'}]")
    if sold:
        from ..soldadura import en_modelo
        print(en_modelo.resumen_consola(modelo, sold))
    print(f"\nInforme: {salida / 'informe.html'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
