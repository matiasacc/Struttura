"""Genera el CSV del fuselaje tipo Sonerai II (celosía espacial de tubos rectos) para Struttura 3D.

Geometría APROXIMADA (forma, no medidas reales).  Ejes: x hacia adelante (desde el cortafuego), y hacia la IZQUIERDA, z arriba.  Unidades N, mm.
Uso:  python generar_fuselaje_sonerai.py   →  escribe 003_Ejemplos/004_Portico_espacial/ejemplo4_fuselaje_sonerai_ii.csv
"""
import math
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = RAIZ / "003_Ejemplos" / "004_Portico_espacial" / "ejemplo4_fuselaje_sonerai_ii.csv"

G = 9.81
RHO = 7.85e-6          # kg/mm³ (acero)

# cuadernas: (x, semiancho abajo, semiancho arriba, z abajo, z arriba)
CUADERNAS = [(0, 240, 280, 0, 600), (650, 280, 300, 0, 700), (1300, 300, 300, 0, 900), (2100, 290, 290, 40, 900),
             (2900, 220, 210, 130, 700), (3700, 140, 130, 210, 480), (4400, 50, 50, 250, 340)]
SECCIONES = {"larg": (25.4, 1.65), "trav": (19.05, 1.24), "diag": (15.875, 0.89), "bancada": (25.4, 1.65), "cola": (25.4, 1.24)}

nodos, barras = {}, []          # nombre -> (x,y,z) ; (id, i, j, seccion)


def nodo(n, x, y, z):
    nodos[n] = (x, y, z)


def barra(i, j, sec, pref):
    bid = f"{pref}{len([b for b in barras if b[0].startswith(pref)]) + 1}"
    barras.append((bid, i, j, sec))
    return bid


for k, (x, wb, wt, zb, zt) in enumerate(CUADERNAS):
    nodo(f"{k}BL", x, wb, zb); nodo(f"{k}BR", x, -wb, zb); nodo(f"{k}TL", x, wt, zt); nodo(f"{k}TR", x, -wt, zt)

n = len(CUADERNAS)
for k in range(n - 1):
    for c in ("BL", "BR", "TL", "TR"):
        barra(f"{k}{c}", f"{k + 1}{c}", "larg", "LG")                      # largueros
    alt = k % 2 == 0                                                       # diagonales alternadas (Warren)
    for lado, (b, t) in (("L", ("BL", "TL")), ("R", ("BR", "TR"))):        # caras laterales
        barra(f"{k}{b}", f"{k + 1}{t}", "diag", "DL") if alt else barra(f"{k}{t}", f"{k + 1}{b}", "diag", "DL")
    barra(f"{k}TL", f"{k + 1}TR", "diag", "DT") if alt else barra(f"{k}TR", f"{k + 1}TL", "diag", "DT")   # cara superior
    barra(f"{k}BL", f"{k + 1}BR", "diag", "DB") if alt else barra(f"{k}BR", f"{k + 1}BL", "diag", "DB")   # cara inferior
for k in range(n):                                                         # cuadernas
    barra(f"{k}BL", f"{k}BR", "trav", "CB")
    barra(f"{k}TL", f"{k}TR", "trav", "CT")
    barra(f"{k}BL", f"{k}TL", "trav", "MV")
    barra(f"{k}BR", f"{k}TR", "trav", "MV")
for k in (0, 2, 3):                                                        # diagonales de cuaderna (cortafuego, cabina)
    barra(f"{k}BL", f"{k}TR", "diag", "DC")
    barra(f"{k}BR", f"{k}TL", "diag", "DC")

# bancada del motor (4 tubos rectos convergentes)
for nm, (y, z, c0) in {"MBL": (130, 120, "0BL"), "MBR": (-130, 120, "0BR"), "MTL": (130, 480, "0TL"), "MTR": (-130, 480, "0TR")}.items():
    nodo(nm, -380, y, z)
    barra(c0, nm, "bancada", "BM")
for a, b in (("MBL", "MTL"), ("MBR", "MTR"), ("MBL", "MBR"), ("MTL", "MTR"), ("MBL", "MTR"), ("MBR", "MTL")):
    barra(a, b, "bancada", "BM")
for nm, c0 in (("MBL", "0TL"), ("MBR", "0TR"), ("MTL", "0BL"), ("MTR", "0BR")):
    barra(c0, nm, "bancada", "BM")                                          # cruzados: triangulan la bancada

# cola: estabilizador horizontal (tubo pasante) y deriva
nodo("STL", 4300, 220, 300); nodo("STR", 4300, -220, 300); nodo("FIN", 4500, 0, 800)
barra("6TL", "STL", "cola", "ES"); barra("6TR", "STR", "cola", "ES")
barra("6TL", "FIN", "cola", "DV"); barra("6TR", "FIN", "cola", "DV")
barra("6BL", "FIN", "cola", "DV"); barra("6BR", "FIN", "cola", "DV")

secs = {k: (d, t) for k, (d, t) in SECCIONES.items()}


def area(d, t):
    return math.pi / 4 * (d**2 - (d - 2 * t) ** 2)


def long_barra(b):
    a, c = nodos[b[1]], nodos[b[2]]
    return math.dist(a, c)


L = []
L.append("# Fuselaje tipo SONERAI II (celosía espacial de tubos de acero 4130).  Forma APROXIMADA, solo tubos rectos.")
L.append("# Generado por 004_Documentacion/003_Generadores/generar_fuselaje_sonerai.py.  Unidades N, mm.  Ejes: x adelante, y izquierda, z arriba.")
L.append("# Apoyos = herrajes del ala (4 puntos abajo, cuadernas 2 y 3).  Casos: PESO (1 g), MOTOR (par), COLA, LATERAL.")
L.append("# Combinaciones: N38 = 3,8 g de maniobra, LAT = carga lateral en la deriva + par del motor.")
L += ["", "PROYECTO", "proyecto;Fuselaje Sonerai II (modelo de prueba)", "unidad_fuerza;N", "unidad_longitud;mm", "tipo;portico3d", "corte_tensiones;si"]
L += ["", "NODOS", "id;x;y;z"] + [f"{n_};{x};{y};{z}" for n_, (x, y, z) in nodos.items()]
L += ["", "MATERIALES", "id;E;nu;fy;rho", "4130;205000;0.29;435;7.85e-6"]
L += ["", "SECCIONES", "id;tipo;d;t"] + [f"{k};tubo;{d};{t}" for k, (d, t) in secs.items()]
L += ["", "BARRAS", "id;nodo_i;nodo_j;material;seccion"] + [f"{b[0]};{b[1]};{b[2]};4130;{b[3]}" for b in barras]
L += ["", "APOYOS", "nodo;ux;uy;uz;phix;phiy;phiz",
      "2BL;1;1;1;0;0;0", "2BR;0;0;1;0;0;0", "3BL;0;0;1;0;0;0", "3BR;0;1;1;0;0;0"]
L += ["", "CARGAS", "caso;nodo;Fx;Fy;Fz;Mx;My;Mz"]
for nm in ("MBL", "MBR", "MTL", "MTR"):
    L.append(f"PESO;{nm};0;0;{-80 * G / 4:.1f};0;0;0")                       # motor 80 kg
for nm in ("STL", "STR"):
    L.append(f"PESO;{nm};0;0;{-6 * G:.1f};0;0;0")                             # cola 6 kg c/lado
L.append(f"PESO;FIN;0;0;{-5 * G:.1f};0;0;0")
L.append("MOTOR;MTL;0;0;0;130000;0;0")                                        # par del motor 130 N·m
L.append("COLA;STL;0;0;-300;0;0;0")
L.append("COLA;STR;0;0;-300;0;0;0")
L.append("LATERAL;FIN;0;1500;0;0;0;0")
qs = [("PESO", b[0], "qgz", f"{-RHO * G * area(*secs[b[3]]):.5f}") for b in barras]
# ocupantes (piloto 85 kg en la bahía 1-2 y pasajero 85 kg en la bahía 2-3): apoyan en los largueros inferiores, a mitad de bahía
L += ["", "CARGAS EN BARRAS", "caso;barra;tipo;valor;valor2;a"]
for cs_, bid, t, v in qs:
    L.append(f"{cs_};{bid};{t};{v};;")
for k in (1, 2):
    for c in ("BL", "BR"):
        bid = next(b[0] for b in barras if b[0].startswith("LG") and b[1] == f"{k}{c}")
        L.append(f"PESO;{bid};Pgz;{-85 * G / 2:.1f};;{long_barra(next(x for x in barras if x[0] == bid)) / 2:.1f}")
L += ["", "COMBINACIONES", "combinacion;caso;factor", "N38;PESO;3.8", "N38;COLA;1",
      "LAT;PESO;1", "LAT;LATERAL;1", "LAT;MOTOR;1"]
# puntos de tensión pedidos: raíz de los largueros inferiores en el herraje del ala
L += ["", "PUNTOS DE TENSION", "id;barra;x;y;z;caso"]
lg = next(b[0] for b in barras if b[0].startswith("LG") and b[1] == "2BL")
L.append(f"larguero_inf_izq_tras_herraje;{lg};0;12.7;0;N38")
SALIDA.write_text("\n".join(L) + "\n", encoding="utf-8")
print(f"{SALIDA}: {len(nodos)} nodos, {len(barras)} barras")
