"""Struttura – punto de entrada:  python struttura.py ARCHIVO.csv [opciones]

Elige solo el programa (emparrillado, pórtico o reticulado) según la línea  tipo;…  del bloque PROYECTO del CSV.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "001_Codigo"))

from struttura.despachador import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
