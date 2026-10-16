"""python struttura.py ARCHIVO.csv   (tipo;soldadura)     o     python struttura.py --soldadura "circulo d=50.8 Vz=3000 electrodo=E70 w=3" """
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .. import __version__
from ..emparrillado.__main__ import _escribir_csv
from ..emparrillado.entrada import ErrorDeEntrada
from .datos import canon
from .entrada import cargar_csv, desde_linea
from .grupo import ErrorSoldadura
from .informe import generar_html
from .verificar import verificar


def resolver(modelo):
    uf, ul = modelo.config["unidad_fuerza"], modelo.config["unidad_longitud"]
    por = {s.id: [] for s in modelo.soldaduras}
    idx = {s.id: s for s in modelo.soldaduras}
    for sid, caso, E, punto in modelo.cargas:
        por[sid].append((caso, E, punto, verificar(idx[sid], E, punto, uf, ul, modelo.electrodos)))
    return por


def modelo_unidad(modelo) -> str:
    from ..emparrillado.informe import unidad_tension
    return unidad_tension(canon(modelo.config["unidad_fuerza"]), modelo.config["unidad_longitud"])


def resumen(modelo, por) -> str:
    L = []
    ul = modelo.config["unidad_longitud"]
    uf = canon(modelo.config["unidad_fuerza"])
    for s in modelo.soldaduras:
        vistos = set()                                     # cada aviso una sola vez por soldadura
        for caso, E, punto, r in por[s.id]:
            if s.tipo == "tope":
                t = (f"  {s.id} · {caso} (a tope, t = {s.esp:g} {ul}): σ máx = {r['sig_max']:.4g}, τ máx = {r['tau_max']:.4g}, σ VM = {r['vm_max']:.4g} "
                     f"[{modelo_unidad(modelo)}];  CS σ = {r['cs_sig']:.3g}, CS τ = {r['cs_tau']:.3g}, CS Von Mises = {r['cs_vm']:.3g}  [{'CUMPLE' if r['cumple'] else 'NO CUMPLE'}]")
                L.append(t)
                for a in r["avisos"]:
                    if a not in vistos:
                        vistos.add(a)
                        L.append(f"    Aviso: {a}")
                continue
            t = f"  {s.id} · {caso}: f máx = {r['fmax']:.4g} {uf}/{ul} en ({r['punto'][0]:.4g}; {r['punto'][1]:.4g}); w requerido = {r['w_req']:.4g} {ul} (garganta t = {r['t_req']:.4g}; {r['gobierna']})"
            if s.w:
                t += f"; con w = {s.w:g} (t = {r['t']:.4g}): CS código = {r['cs_cod']:.3g}  [{'CUMPLE' if r['cumple'] else 'NO CUMPLE'}]"
            L.append(t)
            for a in r["avisos"]:
                if a not in vistos:
                    vistos.add(a)
                    L.append(f"    Aviso: {a}")
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="struttura", description="Soldaduras de filete (modo rápido)")
    ap.add_argument("--version", action="version", version=f"Struttura {__version__}")
    ap.add_argument("archivo", nargs="?")
    ap.add_argument("--soldadura", help="una línea: 'disposicion clave=valor ...'")
    ap.add_argument("-o", "--salida", help="carpeta de salida")
    ap.add_argument("--sin-informe", action="store_true", help="solo imprime el resultado")
    a = ap.parse_args(argv)
    try:
        if a.soldadura:
            modelo = desde_linea(a.soldadura)
        elif a.archivo:
            modelo = cargar_csv(a.archivo)
        else:
            print("Indicá un archivo CSV o --soldadura \"...\"", file=sys.stderr)
            return 1
        por = resolver(modelo)
    except (ErrorDeEntrada, ErrorSoldadura) as e:
        print(f"\nERROR EN LOS DATOS DE ENTRADA\n  {e}\n", file=sys.stderr)
        return 1
    print(f"Struttura v{__version__} · Soldaduras  |  {modelo.config['proyecto']}")
    print(resumen(modelo, por))
    if not a.sin_informe:
        if a.archivo:
            ruta = Path(a.archivo)
            salida = Path(a.salida) if a.salida else ruta.with_name(ruta.stem + "_salida")
        else:
            salida = Path(a.salida) if a.salida else Path("soldadura_salida")
        salida.mkdir(parents=True, exist_ok=True)
        (salida / "informe.html").write_text(generar_html(modelo, por), encoding="utf-8")
        print(f"\nInforme: {salida / 'informe.html'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
