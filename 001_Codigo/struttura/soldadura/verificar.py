"""Verificación de una soldadura de filete: tensión en la garganta, coeficiente de seguridad y pie requerido.

Método (Shigley cap. 9 y Compendio cap. 18, coinciden):
    τ = f / (0,707·w)                     f = fuerza por unidad de longitud en el punto más exigido (grupo.py)
    Código (AWS/AISC):  CS_cód = τ_adm / τ ;  w_req = f_máx / (0,707·τ_adm) ;   τ_adm = tabla por electrodo (Shigley Tabla 9-6, A)
    Convencional (Shigley ej. 9-4a):  n = 0,577·Sy_aporte / τ
    Metal base (Shigley ej. 9-2b, Tabla 9-4):  τ_base = f / w ≤ 0,40·Sy_base ;  w_req,base = f_máx / (0,40·Sy_base)
    Pie mínimo según el espesor de la pieza más gruesa: Tabla 9-6 Cuadro B ;  el pie no debe superar el espesor de la pieza más delgada.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .datos import U_LONG, electrodo, fac_tension, filete_minimo_mm
from .grupo import ErrorSoldadura, Grupo

GARGANTA = 0.707          # t = 0,707·w  (Shigley (9-3); Compendio (3))
CORTE_BASE = 0.40         # τ_base ≤ 0,40·Sy_base  (Shigley Tabla 9-4; Compendio Anexo 2)
VM_CORTE = 0.577          # Ssy = 0,577·Sy  (Shigley ej. 9-4a)


@dataclass
class Soldadura:
    id: str
    grupo: Grupo
    electrodo: str
    w: float | None = None            # pie del filete (si no se da, se calcula el requerido)
    sy_base: float | None = None      # fluencia del metal base (unidades de tensión del modelo)
    t_gruesa: float | None = None     # espesor de la pieza más gruesa unida
    t_fina: float | None = None       # espesor de la pieza más delgada
    barra: str = ""
    extremo: str = ""
    tipo: str = "filete"              # "filete" | "tope"
    esp: float | None = None          # tope: espesor de las piezas unidas (= garganta, sin refuerzo)


def datos_electrodo(nombre, uf, ul, extra=None):
    """(Sut, Sy, τ_adm) del electrodo en las unidades de tensión del modelo."""
    try:
        sut, sy, ta = electrodo(nombre, extra)
    except KeyError:
        raise ErrorSoldadura(f"electrodo '{nombre}' desconocido.  Tabla incluida: E60, E70, E80, E90, E100, E110, E120; "
                             "otros se cargan en el bloque ELECTRODOS (id;sut;sy;tau_adm) o con tau_adm=")
    f = fac_tension(uf, ul)
    cv = lambda v: None if v is None else v * f
    return cv(sut), cv(sy), cv(ta)


SIG_ADM = 0.60            # tracción, compresión y flexión a tope: 0,60·Sy  (Shigley Tabla 9-4: flexión 0,60–0,66·Sy; se toma el menor)


def verificar_tope(sol: Soldadura, E, punto, uf, ul, extra=None, fino=False):
    """Soldadura a tope de penetración completa.  Garganta = espesor de las piezas (sin refuerzo).
    σ = (N/L_w + M·c/I_u)/t  (normal al plano del cordón);  τ = |V/L_w + T·r/J_u|/t (en el plano);  σ_VM = √(σ² + 3τ²).
    Admisibles (Shigley Tabla 9-4):  σ ≤ 0,60·Sy ;  τ ≤ 0,30·S_ut del electrodo (y ≤ 0,40·Sy del base).  Sy = el menor entre aporte y base."""
    if not sol.esp:
        raise ErrorSoldadura(f"soldadura '{sol.id}': la unión a tope necesita el espesor de las piezas (esp)")
    sut, sy_e, tau_e = datos_electrodo(sol.electrodo, uf, ul, extra)
    sys_ = [x for x in (sy_e, sol.sy_base) if x]
    if not sys_:
        raise ErrorSoldadura(f"soldadura '{sol.id}': para la unión a tope hace falta Sy (del electrodo o sy_base)")
    sy = min(sys_)
    g = sol.grupo
    r = g.evaluar(E, punto, fino)
    ky, kz = getattr(g, "escala_fibra", (1.0, 1.0))
    # tensión en la fibra exterior: se amplían las coordenadas respecto del baricentro (línea media → fibra exterior)
    y = g.yg + (r["y"] - g.yg) * ky
    z = g.zg + (r["z"] - g.zg) * kz
    fx, fy, fz = g.fuerza(E, y, z, punto)
    t = sol.esp
    sig, tau = fx / t, np.hypot(fy, fz) / t
    vm = np.sqrt(sig**2 + 3 * tau**2)
    i = int(np.argmax(vm))
    tau_adm = min([tau_e] + ([CORTE_BASE * sol.sy_base] if sol.sy_base else []))
    sig_adm = SIG_ADM * sy
    smax, tmax, vmax = float(np.abs(sig).max()), float(tau.max()), float(vm.max())
    out = dict(r)
    out.update(tipo="tope", sig=sig, tau_arr=tau, vm=vm, i=i, punto=(float(r["y"][i]), float(r["z"][i])), sig_max=smax, tau_max=tmax, vm_max=vmax,
               sig_adm=sig_adm, tau_adm=tau_adm, sy_ref=sy, esp=t,
               cs_sig=sig_adm / smax if smax > 0 else float("inf"), cs_tau=tau_adm / tmax if tmax > 0 else float("inf"),
               cs_vm=sy / vmax if vmax > 0 else float("inf"))
    out["t_req"] = t / min(out["cs_sig"], out["cs_tau"]) if min(out["cs_sig"], out["cs_tau"]) < float("inf") else 0.0
    av = []
    if sol.t_fina and t > sol.t_fina + 1e-9:
        av.append(f"el espesor {t:g} supera el de la pieza más delgada ({sol.t_fina:g})")
    out["avisos"] = av
    out["cumple"] = out["cs_sig"] >= 1 and out["cs_tau"] >= 1 and not av
    return out


def verificar(sol: Soldadura, E, punto, uf, ul, extra=None, fino=False):
    """Resultado de una carga E = (N, Vy, Vz, T, My, Mz) aplicada en 'punto' (y, z) (o None = origen del grupo)."""
    if sol.tipo == "tope":
        return verificar_tope(sol, E, punto, uf, ul, extra, fino)
    sut, sy_e, tau_adm = datos_electrodo(sol.electrodo, uf, ul, extra)
    r = sol.grupo.evaluar(E, punto, fino)
    fmax = r["fmax"]
    out = dict(r)
    out.update(tau_adm=tau_adm, sy_aporte=sy_e)
    out["w_req_aporte"] = fmax / (GARGANTA * tau_adm)
    out["w_req_base"] = None if not sol.sy_base else fmax / (CORTE_BASE * sol.sy_base)
    reqs = [out["w_req_aporte"]] + ([out["w_req_base"]] if out["w_req_base"] else [])
    out["w_req"] = max(reqs)
    out["gobierna"] = "metal de aporte" if out["w_req"] == out["w_req_aporte"] else "metal base"
    f_mm = U_LONG[ul.lower()]
    out["w_min"] = None if not sol.t_gruesa else filete_minimo_mm(sol.t_gruesa * f_mm) / f_mm
    out["w_max"] = sol.t_fina
    out["t_req"] = GARGANTA * out["w_req"]
    out["w_adoptar"] = max(out["w_req"], out["w_min"] or 0.0)        # [propio] el pie a ejecutar no baja del mínimo constructivo
    out["t_adoptar"] = GARGANTA * out["w_adoptar"]
    w = sol.w
    out["w"] = w
    out["t"] = None if not w else GARGANTA * w
    if w:
        tau = fmax / (GARGANTA * w)
        out.update(tau=tau, cs_cod=tau_adm / tau if tau > 0 else float("inf"),
                   cs_conv=(VM_CORTE * sy_e / tau if (sy_e and tau > 0) else None),
                   cs_cod_equiv=(VM_CORTE * sy_e / tau_adm * tau_adm / tau if (sy_e and tau > 0) else None),
                   tau_base=fmax / w, cs_base=(CORTE_BASE * sol.sy_base / (fmax / w) if (sol.sy_base and fmax > 0) else None))
        av = []
        if out["w_min"] and w < out["w_min"] - 1e-9:
            av.append(f"el pie {w:g} es menor que el mínimo de la Tabla 9-6 B ({out['w_min']:.3g}) para la pieza más gruesa")
        if out["w_max"] and w > out["w_max"] + 1e-9:
            av.append(f"el pie {w:g} supera el espesor de la pieza más delgada ({out['w_max']:g})")
        out["avisos"] = av
        out["cumple"] = out["cs_cod"] >= 1 and (out["cs_base"] is None or out["cs_base"] >= 1) and not av
    else:
        out["avisos"] = []
        out["cumple"] = None
    return out
