"""Línea de comandos:  python -m struttura.portico3d ARCHIVO.csv   (normalmente:  python struttura.py ARCHIVO.csv)"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

from struttura.emparrillado.__main__ import _escribir_csv

from .. import __version__
from .entrada import ErrorDeEntrada, NOMBRES_GDL, cargar_modelo
from .esfuerzos import esfuerzos_extremos, tensiones
from .tensor import analizar
from .informe import generar_html, generar_html_esquema
from .solver import ErrorEstructura, equilibrio, resolver, verificar


def exportar_csv(modelo, resultados, info, carpeta: Path, sold=None):
    est = modelo.config["csv_salida"]
    desp, reac, esf, tens, resr, tens_p = [], [], [], [], [], []
    for nombre, res in resultados.items():
        ex = esfuerzos_extremos(modelo, res)
        an = analizar(modelo, res)
        ts = tensiones(modelo, res, an)
        for tag, lista in (("critico", an["criticos"]), ("pedido", an["usuario"])):
            for i, c in enumerate(lista):
                tens_p.append([nombre, c.get("id", f"{tag}{i + 1}"), tag, modelo.barras[c["barra"]].id, c["x"], c["y"], c["z"], c["sx"], c["txy"], c["txz"],
                               c["s1"], c["s3"], c["tau_max"], c["vm"], c["tresca"], c["rankine"], *[c["cs"].get(t, "") for t in ("vm", "tresca", "rankine", "mohr", "mohrmod")],
                               "" if c["cs_gob"] is None else c["cs_gob"]])
        for k, n in enumerate(modelo.nodos):
            desp.append([nombre, n.id, *res.u[k]])
            if modelo.restr[k].any():
                reac.append([nombre, n.id, *[res.R[k, c] if modelo.restr[k, c] else "" for c in range(6)]])
            tiene_i = any(sp["nodo"] == k for sp in modelo.resortes_incl)
            if (modelo.resortes[k] > 0).any() or tiene_i:
                resr.append([nombre, n.id, *[res.Rk[k, c] if (modelo.resortes[k, c] > 0 or (tiene_i and c < 3)) else "" for c in range(6)]])
        for k, b in enumerate(modelo.barras):
            for lab, v in (("i", ex[k]["i"]), ("j", ex[k]["j"])):
                esf.append([nombre, b.id, lab, *v])
            t = ts[k]
            tens.append([nombre, b.id] + [("" if t[c] is None else t[c]) for c in ("sig_t", "sig_c", "tau_t", "vm", "cs")]
                        + [*ex[k]["max"]])
    _escribir_csv(carpeta / "desplazamientos.csv", ["caso", "nodo", "ux", "uy", "uz", "phix", "phiy", "phiz"], desp, est)
    _escribir_csv(carpeta / "reacciones.csv", ["caso", "nodo", "Rx", "Ry", "Rz", "Mx", "My", "Mz"], reac, est)
    if resr:
        _escribir_csv(carpeta / "resortes.csv", ["caso", "nodo", "Fx", "Fy", "Fz", "Mx", "My", "Mz"], resr, est)
    _escribir_csv(carpeta / "esfuerzos.csv", ["caso", "barra", "extremo", "N", "Vy", "Vz", "T", "My", "Mz"], esf, est)
    _escribir_csv(carpeta / "tensiones.csv", ["caso", "barra", "sigma_traccion_max", "sigma_compresion_max", "tau_torsion_max",
                                             "sigma_eq_max", "CS_min", "N_max", "Vy_max", "Vz_max", "T_max", "My_max", "Mz_max"], tens, est)
    _escribir_csv(carpeta / "tensores.csv", ["caso", "punto", "tipo", "barra", "x", "y", "z", "sigma_x", "tau_xy", "tau_xz", "sigma_1", "sigma_3",
                                             "tau_max", "sigma_VM", "sigma_Tresca", "sigma_Rankine", "CS_VM", "CS_Tresca", "CS_Rankine", "CS_Mohr", "CS_MohrMod",
                                             "CS_gobernante"], tens_p, est)
    if sold:
        from ..soldadura import en_modelo
        en_modelo.exportar(modelo, sold, carpeta, _escribir_csv, est)
    cab = [f"{modelo.nodos[k // 6].id}:{NOMBRES_GDL[k % 6]}" for k in range(6 * modelo.n)]
    _escribir_csv(carpeta / "matriz_K.csv", [""] + cab, [[cab[i], *info.K[i]] for i in range(6 * modelo.n)], est)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="struttura.py", description="Pórticos espaciales (3D) por el método matricial de rigidez.")
    ap.add_argument("--version", action="version", version=f"Struttura {__version__}")
    ap.add_argument("archivo")
    ap.add_argument("-o", "--salida", help="carpeta de salida (por defecto: <archivo>_salida)")
    ap.add_argument("--solo-esquema", action="store_true", help="no calcula: dibuja datos y cargas para revisar la entrada")
    ap.add_argument("--sin-graficos", action="store_true", help="(sin efecto en 3D; se acepta por compatibilidad)")
    a = ap.parse_args(argv)
    try:
        modelo = cargar_modelo(a.archivo)
    except ErrorDeEntrada as e:
        print(f"\nERROR EN LOS DATOS DE ENTRADA\n  {e}\n", file=sys.stderr)
        return 1
    for av in modelo.avisos:
        print(av if av.startswith("Nota: ") else f"Aviso: {av}")
    n_av = len(modelo.avisos)
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
    for av in modelo.avisos[n_av:]:
        print(av if av.startswith("Nota: ") else f"Aviso: {av}")
    sold = None
    if modelo.soldaduras:
        from ..soldadura.grupo import ErrorSoldadura
        from .soldaduras import evaluar
        try:
            sold = evaluar(modelo, resultados, {n: esfuerzos_extremos(modelo, r) for n, r in resultados.items()})
        except ErrorSoldadura as e:
            print(f"\nERROR EN SOLDADURAS\n  {e}\n", file=sys.stderr)
            return 1
    (salida / "informe.html").write_text(generar_html(modelo, resultados, info, sold), encoding="utf-8")
    exportar_csv(modelo, resultados, info, salida, sold)
    print(f"Struttura v{__version__} · Pórtico espacial  |  Proyecto: {modelo.config['proyecto']}")
    print(f"  {modelo.n} nodos, {len(modelo.barras)} barras, {len(resultados)} caso(s)/combinación(es)")
    if modelo.peso_propio:
        pp = modelo.peso_propio
        print(f"  Peso propio en el caso '{pp['caso']}' (gravedad {pp['gravedad']}): masa {pp['masa']:.4g} kg, peso {pp['peso']:.4g} {modelo.config['unidad_fuerza']}")
    for nombre, res in resultados.items():
        eq = equilibrio(modelo, res)
        print(f"  {nombre:>14}: max|u| = {np.abs(res.u[:, :3]).max():.4g}   equilibrio {eq['rel']:.1e} [{'OK' if eq['rel'] < 1e-8 else 'REVISAR'}]")
    if sold:
        from ..soldadura.__main__ import resumen
        from types import SimpleNamespace
        print("\n  Soldaduras:")
        print(resumen(SimpleNamespace(config=modelo.config, soldaduras=modelo.soldaduras), sold))
    print(f"\nInforme: {salida / 'informe.html'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
