"""Pandeo de una barra que se reemplazó por un resorte (igual en los cuatro programas).

Un resorte lineal a tierra y una barra cargada axialmente rigidizan igual (k = E·A/L); si la barra trabaja a compresión puede pandear.
En la fila del resorte (RESORTES o RESORTES INCLINADOS) se anota la carga crítica de esa barra en la columna `pc` (la calcula el botón
«Calcular k de una barra» del editor con la teoría de Euler, Pc = π²·E·I/(K·L)², o se escribe a mano).  El informe compara |F| del resorte
con Pc:  CS pandeo = Pc/|F|.

Limitación: un resorte no sabe hacia dónde está el otro extremo de la barra, así que no se puede decidir si la barra está comprimida o
traccionada.  Se informa |F| (valor absoluto) y el CS vale solo si esa barra trabaja a compresión: queda a criterio del diseñador."""
from __future__ import annotations

import math

from struttura.emparrillado.entrada import ErrorDeEntrada, _num, _tabla


def leer_rectos(bloques, idx, cols_k):
    """Filas de RESORTES con `pc`.  cols_k: [(columna, componente de u)] de los resortes lineales del programa
    (3D: kx,ky,kz → 0,1,2; plano y reticulado: kx,ky → 0,1; emparrillado: kz → 0).
    Devuelve [{"nodo": idx, "id", "k", "d": vector unitario (en las componentes de u), "pc"}]."""
    out = []
    ncomp = max(c for _, c in cols_k) + 1
    for n, r in _tabla(bloques, "RESORTES", ["nodo"], requerido=False) or []:
        txt = r.get("pc", "")
        if txt == "":
            continue
        if r["nodo"] not in idx:
            raise ErrorDeEntrada(f"Bloque RESORTES, línea {n}: el nodo '{r['nodo']}' no existe")
        pc = _num(txt, "RESORTES", n, "pc")
        if pc <= 0:
            raise ErrorDeEntrada(f"Bloque RESORTES, línea {n}: pc (carga crítica de pandeo) debe ser > 0")
        ks = [(c, _num(r.get(nom), "RESORTES", n, nom, obligatorio=False, defecto=0.0)) for nom, c in cols_k]
        ks = [(c, v) for c, v in ks if v > 0]
        if len(ks) != 1:
            raise ErrorDeEntrada(f"Bloque RESORTES, línea {n}: con `pc` la fila debe tener un solo resorte lineal con k > 0 "
                                 f"(la barra que reemplaza trabaja en una dirección); separarlo en filas")
        c, k = ks[0]
        d = [0.0] * ncomp
        d[c] = 1.0
        out.append({"nodo": idx[r["nodo"]], "id": r["nodo"], "k": k, "d": tuple(d), "pc": pc})
    return out


def leer_pc_incl(r, ctx, n):
    """`pc` opcional de una fila de RESORTES INCLINADOS (None si no hay)."""
    txt = r.get("pc", "")
    if txt == "":
        return None
    pc = _num(txt, ctx, n, "pc")
    if pc <= 0:
        raise ErrorDeEntrada(f"Bloque {ctx}, línea {n}: pc (carga crítica de pandeo) debe ser > 0")
    return pc


def lista(modelo):
    """Resortes con carga crítica: [{"id", "nodo", "k", "d", "pc"}]."""
    out = list(getattr(modelo, "resortes_pc", []))
    for sp in getattr(modelo, "resortes_incl", []):
        if sp.get("pc"):
            d = tuple(sp["d"]) if "d" in sp else (math.cos(math.radians(sp["beta"])), math.sin(math.radians(sp["beta"])))
            out.append({"id": sp["id"], "nodo": sp["nodo"], "k": sp["k"], "d": d, "pc": sp["pc"]})
    return out


def verificar(modelo, res):
    """[{"id", "k", "F" (|F| del resorte), "pc", "cs"}] para un resultado (caso o combinación); cs = None si F ≈ 0."""
    out = []
    for sp in lista(modelo):
        u = res.u[sp["nodo"]]
        F = abs(sp["k"] * sum(a * b for a, b in zip(sp["d"], u)))
        cs = sp["pc"] / F if F > 1e-9 * sp["pc"] else None
        out.append({"id": sp["id"], "k": sp["k"], "F": F, "pc": sp["pc"], "cs": cs})
    return out


def tabla_html(modelo, res, tabla, fg, e_, uF, uL):
    """Tabla del informe (lista de cadenas HTML) o [] si ningún resorte tiene `pc`."""
    v = verificar(modelo, res)
    if not v:
        return []
    filas = [[e_(d["id"]), fg(d["k"]), fg(d["F"], 5), fg(d["pc"], 5), "–" if d["cs"] is None else fg(d["cs"], 4)] for d in v]
    return ["<h4>Pandeo de las barras reemplazadas por resorte</h4>",
            tabla(["Nodo", f"k [{uF}/{uL}]", f"|F| resorte [{uF}]", f"P<sub>c</sub> [{uF}]", "CS pandeo*"], filas, num=(1, 2, 3, 4),
                  nota="P<sub>c</sub> = carga crítica de la barra que reemplaza el resorte (columna <code>pc</code>; Euler, π²·E·I/(K·L)²).  "
                       "CS pandeo = P<sub>c</sub>/|F|; '–': el resorte no trabaja.  * Un resorte no indica hacia dónde está el otro extremo de la barra: "
                       "|F| va en valor absoluto y el CS solo vale si esa barra trabaja a compresión (queda a criterio del diseñador).")]
