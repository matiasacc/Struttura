"""Peso propio: pieza común a los programas planos (pórtico, emparrillado, reticulado).  Mismo criterio que el pórtico 3D.

PROYECTO:  peso_propio;<caso>   agrega el peso propio de todas las barras al caso <caso>   (si no se escribe, no se calcula)
           gravedad;<±eje>      dirección de la gravedad (pórtico y reticulado: ±x, ±y, por defecto -y;  emparrillado: ±z, por defecto -z)
MATERIALES: rho = densidad en kg/m³ (o la trae la ficha de la biblioteca con lib)
Barra: carga distribuida uniforme  q = ρ·g·A  por unidad de longitud (g = 9,80665 m/s²), convertida a las unidades del modelo.
Reticulado [propio]: las barras son bielas y no admiten carga en el tramo; el peso de cada barra se reparte mitad en cada nudo extremo.
"""
from __future__ import annotations

G_STD = 9.80665


def validar_gravedad(config, permitidos, defecto):
    from .emparrillado.entrada import ErrorDeEntrada
    g = (config.get("gravedad") or defecto).lower().replace(" ", "")
    if g not in {s + e for e in permitidos for s in ("", "+", "-")}:
        raise ErrorDeEntrada(f"Bloque PROYECTO: 'gravedad' debe ser {', '.join('±' + e for e in permitidos)} (por defecto {defecto})")
    config["gravedad"] = g
    return g


def peso_especifico(config, barras):
    """ρ·g en [fuerza/longitud³] del modelo, por barra (lista).  Valida unidades y que cada material tenga rho."""
    from .emparrillado.entrada import ErrorDeEntrada
    from .portico3d.entrada import _U_FUERZA, _U_LONG
    uf, ul = config["unidad_fuerza"].strip().lower(), config["unidad_longitud"].strip().lower()
    if uf not in _U_FUERZA or ul not in _U_LONG:
        raise ErrorDeEntrada(f"Peso propio: no sé convertir las unidades '{config['unidad_fuerza']}' / '{config['unidad_longitud']}' "
                             f"(admitidas: fuerza {', '.join(_U_FUERZA)};  longitud {', '.join(_U_LONG)}).  O bien cargá el peso propio a mano.")
    sin = sorted({b.mat.id for b in barras if b.mat.rho is None})
    if sin:
        raise ErrorDeEntrada(f"Peso propio: falta la columna rho (densidad en kg/m³) en el/los material(es): {', '.join(sin)}")
    sinA = sorted({b.sec.id for b in barras if not b.sec.A})
    if sinA:
        raise ErrorDeEntrada(f"Peso propio: falta el área A en la/s sección(es): {', '.join(sinA)}")
    fF, fL = _U_FUERZA[uf], _U_LONG[ul]
    return [b.mat.rho * G_STD / fF * fL ** 3 for b in barras], fL
