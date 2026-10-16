"""Soldaduras en los extremos de las barras de los programas planos (pórtico plano y emparrillado).  Mismo bloque SOLDADURAS / ELECTRODOS que el 3D.

Cómo se pasan los esfuerzos de la barra a las cargas del grupo de cordones (plano de la sección: y = fuera del plano de la estructura / horizontal,
z = en el plano de la flexión; la dimensión h de la sección está en z, igual que en el cálculo de tensiones):
    Pórtico plano :  N = N ;  Vz = −V ;  My = −M            (Vy = T = Mz = 0)
    Emparrillado  :  Vz = −V ;  T = T ;  My = −M            (N = Vy = Mz = 0)
V, M, N, T son los esfuerzos que informa cada programa en el extremo; el signo es el de la convención del 3D (verificado con el solver 3D en modelos
equivalentes).  Se toman, como en el 3D, los esfuerzos de la sección del extremo indicado (x = 0 en i, x = L en j)."""
from __future__ import annotations

import numpy as np


def extremos(modelo, res, tipo):
    """[{"i": E6, "j": E6}, ...] con E6 = [N, Vy, Vz, T, My, Mz] en el extremo de cada barra."""
    if tipo == "portico":
        from ..portico.esfuerzos import esfuerzos
        cur = esfuerzos(modelo, res, n=3)["curvas"]
        return [{"i": np.array([c["N"][0], 0.0, -c["V"][0], 0.0, -c["M"][0], 0.0]),
                 "j": np.array([c["N"][-1], 0.0, -c["V"][-1], 0.0, -c["M"][-1], 0.0])} for c in cur]
    from ..emparrillado.esfuerzos import esfuerzos
    e = esfuerzos(modelo, res, n=3)
    return [{"i": np.array([0.0, 0.0, -c["V"][0], e["T"][k], -c["M"][0], 0.0]),
             "j": np.array([0.0, 0.0, -c["V"][-1], e["T"][k], -c["M"][-1], 0.0])} for k, c in enumerate(e["curvas"])]


def evaluar(modelo, resultados, tipo):
    from ..portico3d.soldaduras import evaluar as ev
    return ev(modelo, resultados, {n: extremos(modelo, r, tipo) for n, r in resultados.items()})


def html(modelo, sold, U, tipo):
    """Sección 'Soldaduras' del informe de un programa plano."""
    from ..soldadura.informe import bloque
    mapeo = ("N = N, V<sub>z</sub> = −V, M<sub>y</sub> = −M" if tipo == "portico" else "V<sub>z</sub> = −V, T = T, M<sub>y</sub> = −M")
    P = ['<div class="caso"><h2>Soldaduras</h2>',
         "<p class='nota'>Esfuerzos de la sección del extremo indicado de la barra, para cada caso y combinación (" + mapeo + "; h de la sección en el plano de la flexión); "
         "el cordón se verifica como grupo de líneas (método de la garganta).  Fórmulas y fuentes: Memoria del programa de soldaduras.</p>"]
    for s in modelo.soldaduras:
        P.append(bloque(s, sold[s.id], U, titulo=f"Soldadura {s.id} · barra {s.barra}, extremo {s.extremo}"))
    P.append("</div>")
    return "\n".join(P)


def filas_csv(modelo, sold):
    """(filas de filete, filas de tope) para soldaduras.csv y soldaduras_tope.csv (mismas columnas que el 3D)."""
    filas, filas_tope = [], []
    for s in modelo.soldaduras:
        for caso, E, punto, r in sold[s.id]:
            if s.tipo == "tope":
                filas_tope.append([s.id, s.barra, s.extremo, caso, *E, "tope", r["sig_max"], r["tau_max"], r["vm_max"], r["sig_adm"], r["tau_adm"], r["cs_sig"], r["cs_tau"], r["cs_vm"], r["t_req"],
                                   "SI" if r["cumple"] else "NO"])
                continue
            filas.append([s.id, s.barra, s.extremo, caso, *E, r["fmax"], r["punto"][0], r["punto"][1], r["tau_adm"], r["w_req_aporte"],
                          "" if r["w_req_base"] is None else r["w_req_base"], r["w_req"], r["t_req"], r["w_adoptar"], r["t_adoptar"], "" if s.w is None else s.w, "" if s.w is None else r["t"],
                          r.get("tau", ""), r.get("cs_cod", ""), r.get("cs_base") or "", "" if r["cumple"] is None else ("SI" if r["cumple"] else "NO")])
    return filas, filas_tope


CAB_FILETE = ["soldadura", "barra", "extremo", "caso", "N", "Vy", "Vz", "T", "My", "Mz", "f_max", "y_critico", "z_critico",
              "tau_adm", "w_req_aporte", "w_req_base", "w_req", "t_garganta_req", "w_adoptar", "t_garganta_adoptar", "w", "t_garganta", "tau", "CS_codigo", "CS_base", "cumple"]
CAB_TOPE = ["soldadura", "barra", "extremo", "caso", "N", "Vy", "Vz", "T", "My", "Mz", "tipo", "sigma_max", "tau_max", "sigma_VM_max",
            "sigma_adm", "tau_adm", "CS_sigma", "CS_tau", "CS_VM", "t_aprox_req", "cumple"]


def exportar(modelo, sold, carpeta, escribir_csv, estilo):
    filas, tope = filas_csv(modelo, sold)
    if tope:
        escribir_csv(carpeta / "soldaduras_tope.csv", CAB_TOPE, tope, estilo)
    if filas:
        escribir_csv(carpeta / "soldaduras.csv", CAB_FILETE, filas, estilo)


def resumen_consola(modelo, sold):
    from types import SimpleNamespace

    from .__main__ import resumen
    return "\n  Soldaduras:\n" + resumen(SimpleNamespace(config=modelo.config, soldaduras=modelo.soldaduras), sold)
