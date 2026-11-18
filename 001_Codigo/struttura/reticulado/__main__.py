"""Línea de comandos:  python struttura.py ARCHIVO.csv   (o  python -m struttura.reticulado ARCHIVO.csv)"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

from struttura.emparrillado.__main__ import _escribir_csv
from struttura.portico.entrada import ErrorDeEntrada
from struttura.portico.esfuerzos import esfuerzos
from struttura.portico.solver import ErrorEstructura, equilibrio, resolver, verificar

from .. import __version__
from .analisis import verificar_barras
from .entrada import PANDEO, cargar_modelo
from .informe import generar_html, generar_html_esquema


def exportar_csv(modelo, resultados, info, carpeta: Path):
    est = modelo.config["csv_salida"]
    desp, reac, bar, resr = [], [], [], []
    for nombre, res in resultados.items():
        for k, n in enumerate(modelo.nodos):
            desp.append([nombre, n.id, res.u[k, 0], res.u[k, 1]])
            if modelo.restr[k, :2].any():
                reac.append([nombre, n.id] + [res.R[k, c] if modelo.restr[k, c] else "" for c in range(2)])
            if modelo.res_mask[k].any():
                resr.append([nombre, n.id, res.Rk[k, 0], res.Rk[k, 1]])
        for d in verificar_barras(modelo, res):
            b = d["barra"]
            bar.append([nombre, b.id, modelo.nodos[b.i].id, modelo.nodos[b.j].id, d["N"], d["Nj"], d["estado"], d["sigma"], d["dL"],
                        d["n_fy"] or "", d["n_adm"] or "", PANDEO[d["cod"]][0] if d["Pc"] else "", d["Pc"] or "", d["n_pand"] or ""])
    _escribir_csv(carpeta / "desplazamientos.csv", ["caso", "nodo", "ux", "uy"], desp, est)
    _escribir_csv(carpeta / "reacciones.csv", ["caso", "nodo", "Rx", "Ry"], reac, est)
    if resr:
        _escribir_csv(carpeta / "resortes.csv", ["caso", "nodo", "Fx", "Fy"], resr, est)
    _escribir_csv(carpeta / "barras.csv", ["caso", "barra", "nodo_i", "nodo_j", "N_i", "N_j", "estado", "sigma", "alargamiento",
                                        "CS_fluencia", "CS_admisible", "vinculos_pandeo", "Pc", "CS_pandeo"], bar, est)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="struttura.py", description="Reticulados planos por el método matricial de rigidez.")
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
    (salida / "informe.html").write_text(generar_html(modelo, resultados, info, con_graficos=not a.sin_graficos), encoding="utf-8")
    exportar_csv(modelo, resultados, info, salida)
    print(f"Struttura v{__version__} · Reticulado plano  |  Proyecto: {modelo.config['proyecto']}")
    print(f"  {modelo.n} nodos, {len(modelo.barras)} barras, {len(resultados)} caso(s)/combinación(es)")
    if getattr(modelo, "peso_propio", None):
        pp = modelo.peso_propio
        print(f"  Peso propio en el caso '{pp['caso']}' (gravedad {pp['gravedad']}): masa {pp['masa']:.4g} kg, peso {pp['peso']:.4g} {modelo.config['unidad_fuerza']}")
    for nombre, res in resultados.items():
        eq = equilibrio(modelo, res)
        vb = verificar_barras(modelo, res)
        cs = [d["n_pand"] for d in vb if d["n_pand"]] + [d["n_fy"] for d in vb if d["n_fy"]]
        extra = f"   CS mín = {min(cs):.3g}" if cs else ""
        print(f"  {nombre:>14}: max|u| = {np.abs(res.u[:, :2]).max():.4g}   equilibrio {eq['rel']:.1e} [{'OK' if eq['rel'] < 1e-8 else 'REVISAR'}]{extra}")
    print(f"\nInforme: {salida / 'informe.html'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
