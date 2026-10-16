"""Arma 006_Biblioteca/perfiles.csv a partir del PDF "Tablas de perfiles laminados y tubos estructurales" (Reglamento CIRSOC 301-EL / 302-EL).
Uso:  python construir_perfiles.py  tablas.pdf  salida.csv
Todos los valores se copian tal cual figuran en el PDF y quedan en las unidades de las tablas (mm, cm, cm², cm³, cm⁴, cm⁶, kg/m); la unidad va en el nombre
de la columna.  Las comprobaciones de coherencia solo AVISAN en la columna 'observaciones'; nunca corrigen un dato."""
import csv, math, os, re, sys
sys.argv = [sys.argv[0]] + sys.argv[1:]
sys.path.insert(0, os.path.dirname(__file__))
import parse_perfiles as PL                      # (lee sys.argv[1] como PDF)
import parse_ang as PA
import parse_tub as PT
from parse_perfiles import page, NUM, f

COLS = ["n", "ref", "familia", "designacion", "comercial", "forma", "norma", "racionalizado", "d_mm", "b_mm", "tf_mm", "tw_mm", "hw_mm", "t_mm", "r_mm", "r1_mm", "r2_mm",
        "Ag_cm2", "Peso_kgm", "p_m2_m", "Ix_cm4", "Sx_cm3", "rx_cm", "Qx_cm3", "Zx_cm3", "Iy_cm4", "Sy_cm3", "ry_cm", "Qy_cm3", "Sy15_cm3", "Zy_cm3",
        "J_cm4", "Cw_cm6", "C_cm3", "xbar_cm", "eo_cm", "xp_cm", "ey_cm", "ec_cm", "dx_cm", "w_cm", "v1_cm", "Iv_cm4", "Sv_cm3", "iv_cm", "Iz_cm4", "iz_cm",
        "X1_MPa", "X2_1e6_MPa2", "observaciones", "fuente"]
NORMA_T, NORMA_A = "IRAM-IAS U 500-561", "IRAM-IAS U 500-558"
NORMA_TUBO = "IRAM-IAS U 500-218 / U 500-2592"
FORMA = {"IPN": "I", "IPB": "I", "IPBl": "I", "IPBv": "I", "IPE": "I", "W": "I", "HP": "I", "M": "I", "UPN": "canal", "C": "canal", "MC": "canal"}
PAG = {"IPN": 4, "IPB": 5, "IPBl": 6, "IPBv": 7, "IPE": 8, "W": "9-19", "HP": 20, "M": 21, "UPN": 22, "C": 23, "MC": "24-25"}


def r_(x):
    return "" if x is None else (repr(x) if not float(x).is_integer() else str(int(x)))


def fmt(x):
    if x is None: return ""
    return ("%g" % x) if abs(x) < 1e9 else str(x)


def laminados():
    for r in PL.parse_laminados():
        o = {"familia": r["familia"], "designacion": r["designacion"], "forma": FORMA[r["familia"]], "norma": r["norma"],
             "d_mm": r["d_mm"], "b_mm": r["bf_mm"], "tf_mm": r["tf_mm"], "tw_mm": r["tw_mm"], "hw_mm": r["hw_mm"], "r2_mm": r.get("r2_mm"),
             "fuente": f"Tablas CIRSOC 301/302, p. {PAG[r['familia']]}"}
        for k in ("Ag_cm2", "Peso_kgm", "Ix_cm4", "Sx_cm3", "rx_cm", "Qx_cm3", "Zx_cm3", "Iy_cm4", "Sy_cm3", "ry_cm", "Qy_cm3", "Sy15_cm3", "Zy_cm3", "J_cm4", "Cw_cm6",
                  "X1_MPa", "X2_1e6_MPa2", "xbar_cm", "eo_cm", "xp_cm", "ey_cm", "ec_cm"):
            if k in r: o[k] = r[k]
        yield o


def angulos():
    for a in PA.parse_angulos():
        if a["raw"].startswith("x"): a["raw"] = None
        yield a


def ang_filas():
    out, cur = [], None
    for a in PA.parse_angulos():
        raw = a["raw"]
        if not raw.startswith("x"):
            partes = raw.replace("*", " ").replace("  ", " ")
            # "L 16x 16 x 3,2 L 5/8 x 5/8 x1/8": separar nombre de perfil y comercial en el segundo 'L'
            i = partes.index(" L ", 1)
            cur = (partes[:i].strip(), partes[i + 1:].strip(), "*" in raw)
            nom, com, racio = cur
        else:
            nom_base = cur[0].split("x")[0].replace("L", "").strip()
            nom = f"L {nom_base} x {nom_base} x {raw.split('x')[1].split()[0].replace('*','')}"
            com = None; racio = "*" in raw
            # comercial: 'L <dim> x <dim> x <esp>' con la dimensión del grupo
            fr = raw.replace("*", "").split()[-1].replace("x", "")
            c0 = cur[1].split(" x ")
            com = f"{c0[0]} x {c0[1]} x {fr}"
        v = a["rest"]
        nom = re.sub(r"^L\s*(\d+)\s*x\s*(\d+)\s*x\s*([\d,]+)$", r"L \1 x \2 x \3", nom.replace("*", "").strip())
        com = com.replace("1l", "1")                    # errata evidente de impresión en el PDF ("L 1 x 1l x 1/8")
        o = {"familia": "L", "designacion": nom, "comercial": com, "forma": "L", "norma": NORMA_A, "racionalizado": "*" if racio else "",
             "b_mm": a["b"], "t_mm": a["t"], "r_mm": a["r"], "r1_mm": a["r1"],
             "Ag_cm2": v[0], "Peso_kgm": v[1], "xbar_cm": v[2], "w_cm": v[3], "v1_cm": v[4], "Ix_cm4": v[5], "Sx_cm3": v[6], "rx_cm": v[7], "Iv_cm4": v[8], "Sv_cm3": v[9],
             "iv_cm": v[10], "Iz_cm4": v[11], "iz_cm": v[12], "J_cm4": v[13], "Cw_cm6": v[14], "fuente": "Tablas CIRSOC 301/302, p. 26-27"}
        o["Iy_cm4"], o["Sy_cm3"], o["ry_cm"] = o["Ix_cm4"], o["Sx_cm3"], o["rx_cm"]
        o["d_mm"] = a["b"]
        out.append(o)
    # r y r1 se imprimen una sola vez por grupo de igual dimensión (en la fila central): valen para todo el grupo
    grupo = {}
    for o in out:
        if o["r_mm"] is not None: grupo[o["b_mm"]] = (o["r_mm"], o["r1_mm"])
    for o in out:
        if o["r_mm"] is None and o["b_mm"] in grupo: o["r_mm"], o["r1_mm"] = grupo[o["b_mm"]]
    return out


def tes():
    out = []
    for l in page(28):
        t = l.split()
        if len(t) < 30 or not all(NUM.match(x) or x == "-" for x in t[-24:]): continue
        v = [f(x) for x in t[-24:]]; head = " ".join(t[:-24])
        i = head.index(" T ", 1)
        nom, com = head[:i].strip(), head[i + 1:].strip()
        rac = "*" in nom; nom = nom.replace("*", "").strip()
        out.append({"familia": "T", "designacion": nom, "comercial": com, "forma": "T", "norma": NORMA_T, "racionalizado": "*" if rac else "",
                    "d_mm": v[0], "b_mm": v[1], "tf_mm": v[2], "tw_mm": v[2], "r_mm": v[3], "r1_mm": v[4], "r2_mm": v[5],
                    "Ag_cm2": v[8], "Peso_kgm": v[9], "dx_cm": v[10], "Ix_cm4": v[11], "Sx_cm3": v[12], "rx_cm": v[13], "Qx_cm3": v[14], "Zx_cm3": v[15],
                    "Iy_cm4": v[16], "Sy_cm3": v[17], "ry_cm": v[18], "Qy_cm3": v[19], "Sy15_cm3": v[20], "Zy_cm3": v[21], "J_cm4": v[22], "Cw_cm6": v[23],
                    "fuente": "Tablas CIRSOC 301/302, p. 28"})
    return out


def tubos():
    out = []
    for tp, fam, forma, p in (("circ", "TC", "circular", "29-35"), ("cuad", "TQ", "cuadrado", "36-39"), ("rect", "TR", "rectangular", "40-44")):
        for labs, r in PT.verificar(tp, PT.parse_tubos(tp)):
            def num(x): return ("%g" % x)
            if tp == "circ":
                D = labs[0]; t, p_, A, g, I, S, rr, Z, J, C = r
                o = {"designacion": f"TC {num(D)} x {num(t)}", "d_mm": D, "b_mm": D, "Ix_cm4": I, "Sx_cm3": S, "rx_cm": rr, "Zx_cm3": Z, "Iy_cm4": I, "Sy_cm3": S, "ry_cm": rr, "Zy_cm3": Z}
            elif tp == "cuad":
                D = labs[0]; t, p_, A, g, I, S, rr, Z, J, C = r
                o = {"designacion": f"TQ {num(D)} x {num(D)} x {num(t)}", "d_mm": D, "b_mm": D, "Ix_cm4": I, "Sx_cm3": S, "rx_cm": rr, "Zx_cm3": Z, "Iy_cm4": I, "Sy_cm3": S, "ry_cm": rr, "Zy_cm3": Z}
            else:
                B, H = labs; t, p_, A, g, Ix, Sx, rx, Zx, Iy, Sy, ry, Zy, J, C = r
                o = {"designacion": f"TR {num(B)} x {num(H)} x {num(t)}", "d_mm": H, "b_mm": B, "Ix_cm4": Ix, "Sx_cm3": Sx, "rx_cm": rx, "Zx_cm3": Zx, "Iy_cm4": Iy, "Sy_cm3": Sy, "ry_cm": ry, "Zy_cm3": Zy}
            o.update(familia=fam, forma=forma, norma=NORMA_TUBO, t_mm=t, p_m2_m=p_, Ag_cm2=A, Peso_kgm=g, J_cm4=J, C_cm3=C, fuente=f"Tablas CIRSOC 301/302, p. {p}")
            out.append(o)
    return out


def chequear(o):
    obs = []
    def rel(a, b, tol=0.015): return 0 if (not b or abs(a - b) < tol) else abs(a - b) / b      # sin avisar por redondeo de las tablas
    if o.get("Peso_kgm") and o.get("Ag_cm2") and rel(o["Peso_kgm"], 0.785 * o["Ag_cm2"]) > 0.03:
        obs.append("Peso distinto de 0,785·Ag")
    if o.get("Ix_cm4") and o.get("Ag_cm2") and o.get("rx_cm") and rel(o["rx_cm"], (o["Ix_cm4"] / o["Ag_cm2"]) ** .5, 0.03) > 0.03:
        obs.append("rx distinto de raíz(Ix/Ag)")
    if o.get("Iy_cm4") and o.get("Ag_cm2") and o.get("ry_cm") and rel(o["ry_cm"], (o["Iy_cm4"] / o["Ag_cm2"]) ** .5, 0.03) > 0.03:
        obs.append("Iy no coincide con ry (Iy ≠ ry²·Ag)")
    if o["forma"] in ("I", "canal") and o.get("Sx_cm3") and rel(o["Sx_cm3"], 2 * o["Ix_cm4"] / (o["d_mm"] / 10)) > 0.03:
        obs.append("Sx distinto de 2·Ix/d")
    if o["forma"] == "circular":
        D, t = o["d_mm"], o["t_mm"]; I = math.pi / 64 * (D ** 4 - (D - 2 * t) ** 4) / 1e4
        if rel(o["Ix_cm4"], I) > 0.03: obs.append("Ix distinto del cálculo geométrico")
    return "; ".join(obs)


def main(pdf, salida):
    filas = list(laminados()) + ang_filas() + tes() + tubos()
    for i, o in enumerate(filas, 1):
        o["n"] = i; o["ref"] = f"{o['familia']} {o['designacion']}" if o["familia"] not in ("L", "T", "TC", "TQ", "TR") else o["designacion"]
        o["observaciones"] = chequear(o)
    with open(salida, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, delimiter=";", extrasaction="raise")
        w.writeheader()
        for o in filas:
            w.writerow({c: (fmt(o[c]) if isinstance(o.get(c), float) else ("" if o.get(c) is None else o[c])) for c in COLS})
    print(len(filas), "perfiles")
    for o in filas:
        if o["observaciones"]: print(" obs:", o["ref"], "->", o["observaciones"])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
