"""python struttura.py --biblioteca listar | ver NUMERO               (materiales: las fichas las carga Claude en 006_Biblioteca/materiales.csv)
       python struttura.py --biblioteca electrodos | electrodo N_O_ID   (electrodos: 006_Biblioteca/electrodos.csv)
       python struttura.py --biblioteca perfiles [FAMILIA] | perfil N_O_DESIGNACION   (perfiles: 006_Biblioteca/perfiles.csv, tablas CIRSOC)"""
import sys

from . import electrodos as _el
from . import perfiles as _pf
from .biblioteca import ErrorBiblioteca, archivo, cargar, listar


def main(argv=None):
    a = [x for x in (sys.argv[1:] if argv is None else argv) if x != "--biblioteca"]
    try:
        if a[:1] == ["listar"]:
            filas = listar()
            print(f"Biblioteca ({archivo()}): {len(filas)} material(es)")
            for n, nombre in filas:
                print(f"  {n:>4s}  {nombre}")
            return 0
        if a[:1] == ["electrodos"]:
            filas = _el.listar()
            print(f"Electrodos ({_el.archivo()}): {len(filas)}")
            for n, i in filas:
                print(f"  {n:>4s}  {i}")
            return 0
        if a[:1] == ["electrodo"] and len(a) > 1:
            for k, v in _el.cargar(a[1]).items():
                if v:
                    print(f"  {k:14s} {v}")
            return 0
        if a[:1] == ["perfiles"]:
            filas = [x for x in _pf.listar() if len(a) < 2 or x[2].lower() == a[1].lower()]
            print(f"Perfiles ({_pf.archivo()}): {len(filas)}" + (f" de la familia {a[1]}" if len(a) > 1 else ""))
            for n, ref, fam in filas:
                print(f"  {n:>4s}  {ref}")
            return 0
        if a[:1] == ["perfil"] and len(a) > 1:
            for k, v in _pf.cargar(" ".join(a[1:])).items():
                if v:
                    print(f"  {k:16s} {v}")
            return 0
        if a[:1] == ["ver"] and len(a) > 1:
            for k, v in cargar(a[1]).items():
                if v:
                    print(f"  {k:20s} {v}")
            return 0
    except ErrorBiblioteca as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    print(__doc__, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
