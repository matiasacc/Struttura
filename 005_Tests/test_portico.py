"""Tests del programa de pórtico plano (unittest).  Ejecutar:  python -m unittest discover -s tests"""
import math
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "001_Codigo"))

from struttura.portico.barra import matriz_rotacion, rigidez_global_catedra, rigidez_local  # noqa: E402
from struttura.portico.entrada import ErrorDeEntrada, cargar_modelo  # noqa: E402
from struttura.portico.esfuerzos import elastica, esfuerzos, funciones_barra, tensiones  # noqa: E402
from struttura.portico.solver import ErrorEstructura, equilibrio, resolver  # noqa: E402

E0, A0, I0 = 200000.0, 1000.0, 2.0e7
CAB = """PROYECTO
tipo;portico

MATERIALES
id;E;nu;fy;sadm;alfa
m;200000;0.3;250;150;0.00001

SECCIONES
id;tipo;I;A;c;kv;h
s;generica;20000000;1000;100;1.5;200

"""


def modelo_de(nodos, barras, apoyos, extra="", cab=CAB):
    """nodos: [(id,x,y)], barras: [(id,i,j[,ai,aj])], apoyos: [(nodo,ux,uy,phi)]."""
    t = cab + "NODOS\nid;x;y\n" + "".join(f"{a};{b};{c}\n" for a, b, c in nodos)
    t += "\nBARRAS\nid;nodo_i;nodo_j;material;seccion;art_i;art_j\n"
    for b in barras:
        ai, aj = (b[3], b[4]) if len(b) > 3 else (0, 0)
        t += f"{b[0]};{b[1]};{b[2]};m;s;{ai};{aj}\n"
    t += "\nAPOYOS\nnodo;ux;uy;phi\n" + "".join(f"{a};{b};{c};{d}\n" for a, b, c, d in apoyos)
    t += "\n" + extra
    d = tempfile.mkdtemp()
    p = Path(d) / "t.csv"
    p.write_text(t, encoding="utf-8")
    return cargar_modelo(p)


def resolver_uno(m, caso=None):
    res, info = resolver(m)
    return res[caso or next(iter(m.casos))]


def ref_2d(nodos, barras, fijos, F, E, A, I):
    """Solver de pórtico plano de referencia (fórmula clásica con c, s; independiente del programa)."""
    n = len(nodos)
    K = np.zeros((3 * n, 3 * n))
    for a, b in barras:
        dx, dy = nodos[b][0] - nodos[a][0], nodos[b][1] - nodos[a][1]
        L = math.hypot(dx, dy)
        c, s = dx / L, dy / L
        ea, ei = E * A / L, E * I
        kl = np.zeros((6, 6))
        kl[0, 0] = kl[3, 3] = ea
        kl[0, 3] = kl[3, 0] = -ea
        kl[1, 1] = kl[4, 4] = 12 * ei / L**3
        kl[1, 4] = kl[4, 1] = -12 * ei / L**3
        kl[1, 2] = kl[2, 1] = kl[1, 5] = kl[5, 1] = 6 * ei / L**2
        kl[2, 4] = kl[4, 2] = kl[4, 5] = kl[5, 4] = -6 * ei / L**2
        kl[2, 2] = kl[5, 5] = 4 * ei / L
        kl[2, 5] = kl[5, 2] = 2 * ei / L
        r = np.array([[c, s, 0], [-s, c, 0], [0, 0, 1]])           # global -> local
        T = np.zeros((6, 6))
        T[:3, :3] = r
        T[3:, 3:] = r
        d = np.r_[3 * a:3 * a + 3, 3 * b:3 * b + 3]
        K[np.ix_(d, d)] += T.T @ kl @ T
    libre = ~np.array(fijos, dtype=bool).reshape(-1)
    u = np.zeros(3 * n)
    u[libre] = np.linalg.solve(K[np.ix_(libre, libre)], np.asarray(F, dtype=float).reshape(-1)[libre])
    return u.reshape(-1, 3)


class TestMatriz(unittest.TestCase):
    def test_catedra_igual_a_T_k_Tt(self):
        for ang in (0.0, 0.3, 1.2, 2.5, -1.0, math.pi / 2):
            g1, g2 = math.cos(ang), math.sin(ang)
            T = matriz_rotacion(g1, g2)
            a = T @ rigidez_local(E0, A0, I0, 3000.0) @ T.T
            b = rigidez_global_catedra(E0, A0, I0, 3000.0, g1, g2)
            self.assertTrue(np.allclose(a, b, rtol=1e-12, atol=1e-6))

    def test_simetrica_y_solido_rigido(self):
        k = rigidez_local(E0, A0, I0, 2500.0)
        self.assertTrue(np.allclose(k, k.T))
        self.assertTrue(np.allclose(k @ np.array([1, 0, 0, 1, 0, 0.0]), 0, atol=1e-8))
        self.assertTrue(np.allclose(k @ np.array([0, 1, 0, 0, 1, 0.0]), 0, atol=1e-8))
        self.assertTrue(np.allclose(k @ np.array([0, 0, 1, 0, 2500.0, 1.0]), 0, atol=1e-6))


class TestAnaliticos(unittest.TestCase):
    L = 3000.0

    def voladizo(self, extra):
        return modelo_de([(1, 0, 0), (2, self.L, 0)], [(1, 1, 2)], [(1, 1, 1, 1)], extra)

    def test_voladizo_puntual(self):
        m = self.voladizo("CARGAS\ncaso;nodo;Px;Py;M\nP;2;500;-1000;2e5\n")
        r = resolver_uno(m)
        L = self.L
        self.assertAlmostEqual(r.u[1, 1], -1000 * L**3 / (3 * E0 * I0) + 2e5 * L**2 / (2 * E0 * I0), places=9)
        self.assertAlmostEqual(r.u[1, 0], 500 * L / (E0 * A0), places=9)
        self.assertTrue(np.allclose(r.R[0], [-500, 1000, 1000 * L - 2e5]))

    def test_voladizo_distribuida(self):
        m = self.voladizo("CARGAS EN BARRAS\ncaso;barra;tipo;valor;valor2;a;b\nq;1;q;-2;;;\n")
        r = resolver_uno(m)
        self.assertAlmostEqual(r.u[1, 1], -2 * self.L**4 / (8 * E0 * I0), places=8)
        e = esfuerzos(m, r)
        self.assertAlmostEqual(e["Mi"][0], -2 * self.L**2 / 2, places=4)          # hogging en el empotramiento
        self.assertAlmostEqual(e["V"][0], 2 * self.L, places=6)

    def test_trapecial(self):
        m = self.voladizo("CARGAS EN BARRAS\ncaso;barra;tipo;valor;valor2;a;b\nq;1;q;0;-3;;\n")
        r = resolver_uno(m)
        L = self.L
        self.assertAlmostEqual(r.R[0, 1], 1.5 * L, places=6)
        self.assertAlmostEqual(r.R[0, 2], 1.5 * L * (2 * L / 3), places=3)      # resultante a 2L/3
        self.assertAlmostEqual(r.u[1, 1], -11 * 3 * L**4 / (120 * E0 * I0), places=8)

    def test_biempotrada_uniforme_y_puntual(self):
        L = self.L
        m = modelo_de([(1, 0, 0), (2, L, 0)], [(1, 1, 2)], [(1, 1, 1, 1), (2, 1, 1, 1)],
                      "CARGAS EN BARRAS\ncaso;barra;tipo;valor;valor2;a;b\nU;1;q;-2;;;\nP;1;P;-1000;;1000;\nC;1;P;-1000;;1500;\n")
        res, _ = resolver(m)
        e = esfuerzos(m, res["U"])
        self.assertAlmostEqual(e["Mi"][0], -2 * L**2 / 12, places=4)
        self.assertAlmostEqual(e["Mmax"][0], 2 * L**2 / 24, places=4)
        eC = esfuerzos(m, res["C"])
        self.assertAlmostEqual(eC["Mi"][0], -1000 * L / 8, places=4)
        self.assertAlmostEqual(eC["Mmax"][0], 1000 * L / 8, places=4)
        # P en a=1000 (b=2000): M_i = -P a b²/L²
        eP = esfuerzos(m, res["P"])
        self.assertAlmostEqual(eP["Mi"][0], -1000 * 1000 * 2000**2 / L**2, places=3)

    def test_empotrada_articulada(self):
        L = 4000.0
        m = modelo_de([(1, 0, 0), (2, L, 0)], [(1, 1, 2, 0, 1)], [(1, 1, 1, 1), (2, 1, 1, 0)],
                      "CARGAS EN BARRAS\ncaso;barra;tipo;valor;valor2;a;b\nq;1;q;-2;;;\n")
        r = resolver_uno(m)
        e = esfuerzos(m, r)
        self.assertAlmostEqual(e["Mi"][0], -2 * L**2 / 8, places=3)
        self.assertAlmostEqual(e["Mj"][0], 0.0, places=6)
        self.assertAlmostEqual(r.R[1, 1], 3 * 2 * L / 8, places=5)
        self.assertAlmostEqual(r.R[0, 1], 5 * 2 * L / 8, places=5)
        # el giro liberado de la barra es no nulo, y el del nodo (apoyo con φ libre) coincide con el de la barra
        self.assertGreater(abs(r.ub[0, 5]), 0)

    def test_articulacion_igual_a_nodo_articulado(self):
        """Dos vigas en línea unidas por una articulación de barra == barras separadas por un nodo con giros independientes."""
        L = 2000.0
        m1 = modelo_de([(1, 0, 0), (2, L, 0), (3, 2 * L, 0)], [(1, 1, 2, 0, 1), (2, 2, 3, 1, 0)],
                       [(1, 1, 1, 1), (3, 1, 1, 1)], "CARGAS\ncaso;nodo;Px;Py;M\nP;2;0;-1000;0\n")
        r = resolver_uno(m1)
        self.assertTrue(m1.aut[1, 2])                                    # φ del nodo 2 indeterminado → fijado
        e = esfuerzos(m1, r)
        self.assertAlmostEqual(e["Mj"][0], 0.0, places=6)
        self.assertAlmostEqual(e["Mi"][1], 0.0, places=6)
        self.assertAlmostEqual(r.u[1, 1], -500 * L**3 / (3 * E0 * I0), places=8)      # cada mitad: voladizo con P/2

    def test_resorte_en_punta(self):
        L, k = 3000.0, 50.0
        m = modelo_de([(1, 0, 0), (2, L, 0)], [(1, 1, 2)], [(1, 1, 1, 1)],
                      f"RESORTES\nnodo;kx;ky;kphi\n2;;{k};\n\nCARGAS\ncaso;nodo;Px;Py;M\nP;2;0;-1000;0\n")
        r = resolver_uno(m)
        self.assertAlmostEqual(r.u[1, 1], -1000 / (k + 3 * E0 * I0 / L**3), places=9)
        self.assertAlmostEqual(r.Rk[1, 1], -k * r.u[1, 1], places=9)

    def test_resorte_con_desajuste_e_inclinado(self):
        L, k = 2000.0, 400.0
        base = f"CARGAS\ncaso;nodo;Px;Py;M\nX;2;0;0;0\n\nDESAJUSTE DE RESORTES\ncaso;nodo;ux;uy;phi;inclinado\nD;2;{{e}};;;{{ei}}\n"
        m = modelo_de([(1, 0, 0), (2, L, 0)], [(1, 1, 2)], [(1, 1, 1, 1)],
                      "RESORTES\nnodo;kx;ky;kphi\n2;" + str(k) + ";;\n\n" + base.format(e=-3, ei=""))
        r = resolver_uno(m, "D")
        self.assertAlmostEqual(r.u[1, 0], k * -3 / (k + E0 * A0 / L), places=10)
        # un resorte inclinado a 0° equivale al recto
        m2 = modelo_de([(1, 0, 0), (2, L, 0)], [(1, 1, 2)], [(1, 1, 1, 1)],
                       "RESORTES INCLINADOS\nnodo;k;angulo\n2;" + str(k) + ";0\n\n" + base.format(e="", ei=-3))
        r2 = resolver_uno(m2, "D")
        self.assertAlmostEqual(r2.u[1, 0], r.u[1, 0], places=12)

    def test_asentamiento_viga_biempotrada(self):
        L, d = 3000.0, -10.0
        m = modelo_de([(1, 0, 0), (2, L, 0)], [(1, 1, 2)], [(1, 1, 1, 1), (2, 1, 1, 1)],
                      f"DESPLAZAMIENTOS PREFIJADOS\ncaso;nodo;ux;uy;phi\nA;2;0;{d};0\n")
        r = resolver_uno(m)
        self.assertAlmostEqual(r.R[1, 1], 12 * E0 * I0 * d / L**3, places=9)
        e = esfuerzos(m, r)
        self.assertAlmostEqual(abs(e["Mi"][0]), 6 * E0 * I0 * abs(d) / L**2, places=5)
        self.assertLess(equilibrio(m, r)["rel"], 1e-10)

    def test_temperatura(self):
        L = 2000.0
        m = modelo_de([(1, 0, 0), (2, L, 0)], [(1, 1, 2)], [(1, 1, 1, 1), (2, 1, 1, 1)],
                      "CARGAS EN BARRAS\ncaso;barra;tipo;valor;valor2;a;b\nU;1;temp;30;30;;\nG;1;temp;20;0;;\n")
        res, _ = resolver(m)
        eU = esfuerzos(m, res["U"])
        self.assertAlmostEqual(eU["N"][0], -E0 * A0 * 1e-5 * 30, places=4)          # compresión
        self.assertAlmostEqual(np.abs(eU["Mmax"]).max(), 0.0, places=6)
        eG = esfuerzos(m, res["G"])
        self.assertAlmostEqual(eG["Mi"][0], E0 * I0 * 1e-5 * 20 / 200, places=4)     # constante, "sagging" (+)
        self.assertAlmostEqual(eG["Mj"][0], eG["Mi"][0], places=4)
        self.assertAlmostEqual(eG["N"][0], -E0 * A0 * 1e-5 * 10, places=4)          # ΔTm = 10

    def test_temperatura_voladizo_libre(self):
        L = 2000.0
        m = self.voladizo_L(L, "CARGAS EN BARRAS\ncaso;barra;tipo;valor;valor2;a;b\nG;1;temp;20;0;;\n")
        r = resolver_uno(m)
        self.assertAlmostEqual(r.u[1, 0], 1e-5 * 10 * L, places=8)                      # dilatación uniforme
        self.assertAlmostEqual(r.u[1, 1], -1e-5 * 20 / 200 * L**2 / 2, places=8)        # cara +y caliente: curva hacia −y
        self.assertAlmostEqual(np.abs(esfuerzos(m, r)["Mi"]).max(), 0.0, places=6)

    def voladizo_L(self, L, extra):
        return modelo_de([(1, 0, 0), (2, L, 0)], [(1, 1, 2)], [(1, 1, 1, 1)], extra)

    def test_axial_biempotrada(self):
        L = 2000.0
        m = modelo_de([(1, 0, 0), (2, L, 0)], [(1, 1, 2)], [(1, 1, 1, 1), (2, 1, 1, 1)],
                      "CARGAS EN BARRAS\ncaso;barra;tipo;valor;valor2;a;b\nA;1;qa;1;;;\n")
        r = resolver_uno(m)
        X0, Y0, DX, DY = elastica(m, r)[0]
        self.assertAlmostEqual(DX[len(DX) // 2], 1 * L**2 / (8 * E0 * A0), places=7)
        self.assertAlmostEqual(r.R[0, 0], -L / 2, places=6)

    def test_tres_articulaciones(self):
        m = cargar_modelo(RAIZ / "003_Ejemplos" / "002_Portico" / "ejemplo2_tres_articulaciones.csv")
        res, _ = resolver(m)
        r = res["NIEVE"]
        q, Lx, f = 1.5, 8000.0, 4500.0
        self.assertAlmostEqual(abs(r.R[0, 0]), q * Lx**2 / (8 * f), places=6)
        self.assertAlmostEqual(r.R[0, 1], q * Lx / 2, places=6)
        self.assertAlmostEqual(r.R[0, 0] + r.R[4, 0], 0.0, places=6)


class TestCargasGlobales(unittest.TestCase):
    def test_qgy_en_barra_inclinada_equivale_a_q_y_qa(self):
        nod = [(1, 0, 0), (2, 3000, 2000)]
        L = math.hypot(3000, 2000)
        g1, g2 = 3000 / L, 2000 / L
        m1 = modelo_de(nod, [(1, 1, 2)], [(1, 1, 1, 1)], "CARGAS EN BARRAS\ncaso;barra;tipo;valor;valor2;a;b\nA;1;qgy;-2;;;\n")
        m2 = modelo_de(nod, [(1, 1, 2)], [(1, 1, 1, 1)],
                       f"CARGAS EN BARRAS\ncaso;barra;tipo;valor;valor2;a;b\nA;1;q;{-2 * g1};;;\nA;1;qa;{-2 * g2};;;\n")
        r1, r2 = resolver_uno(m1), resolver_uno(m2)
        self.assertTrue(np.allclose(r1.u, r2.u, rtol=1e-10, atol=1e-14))
        self.assertAlmostEqual(r1.R[0, 1], 2 * L, places=6)                     # resultante vertical total
        # proyectada: qgyp por longitud horizontal → resultante 2·Lx
        m3 = modelo_de(nod, [(1, 1, 2)], [(1, 1, 1, 1)], "CARGAS EN BARRAS\ncaso;barra;tipo;valor;valor2;a;b\nA;1;qgyp;-2;;;\n")
        r3 = resolver_uno(m3)
        self.assertAlmostEqual(r3.R[0, 1], 2 * 3000, places=6)
        self.assertAlmostEqual(r3.R[0, 0], 0.0, places=8)
        # qgxp: resultante horizontal = valor × extensión vertical
        m4 = modelo_de(nod, [(1, 1, 2)], [(1, 1, 1, 1)], "CARGAS EN BARRAS\ncaso;barra;tipo;valor;valor2;a;b\nA;1;qgxp;5;;;\n")
        r4 = resolver_uno(m4)
        self.assertAlmostEqual(r4.R[0, 0], -5 * 2000, places=6)
        self.assertAlmostEqual(r4.R[0, 1], 0.0, places=8)

    def test_Pgx_Pgy_equivalen_a_nodal_en_extremo(self):
        nod = [(1, 0, 0), (2, 3000, 2000)]
        L = math.hypot(3000, 2000)
        m1 = modelo_de(nod, [(1, 1, 2)], [(1, 1, 1, 1)], f"CARGAS EN BARRAS\ncaso;barra;tipo;valor;valor2;a;b\nA;1;Pgx;700;;{L};\nA;1;Pgy;-900;;{L};\n")
        m2 = modelo_de(nod, [(1, 1, 2)], [(1, 1, 1, 1)], "CARGAS\ncaso;nodo;Px;Py;M\nA;2;700;-900;0\n")
        self.assertTrue(np.allclose(resolver_uno(m1).u, resolver_uno(m2).u, rtol=1e-10, atol=1e-14))

    def test_momento_puntual_extremo_equivale_a_nodal(self):
        m1 = modelo_de([(1, 0, 0), (2, 3000, 0)], [(1, 1, 2)], [(1, 1, 1, 1)],
                       "CARGAS EN BARRAS\ncaso;barra;tipo;valor;valor2;a;b\nA;1;Mp;1e6;;3000;\n")
        m2 = modelo_de([(1, 0, 0), (2, 3000, 0)], [(1, 1, 2)], [(1, 1, 1, 1)], "CARGAS\ncaso;nodo;Px;Py;M\nA;2;0;0;1e6\n")
        self.assertTrue(np.allclose(resolver_uno(m1).u, resolver_uno(m2).u, rtol=1e-10, atol=1e-14))

    def test_momento_puntual_intermedio_salto_en_M(self):
        L = 3000.0
        m = modelo_de([(1, 0, 0), (2, L, 0)], [(1, 1, 2)], [(1, 1, 1, 0), (2, 0, 1, 0)],
                      "CARGAS EN BARRAS\ncaso;barra;tipo;valor;valor2;a;b\nA;1;Mp;9e5;;1000;\n")
        r = resolver_uno(m)
        e = esfuerzos(m, r)
        cv = e["curvas"][0]
        i = np.flatnonzero(np.isclose(cv["x"], 1000.0))
        self.assertEqual(len(i), 2)
        self.assertAlmostEqual(cv["M"][i[1]] - cv["M"][i[0]], -9e5, places=4)       # M0 antihorario: −M0 en el corte


class TestReferenciaIndependiente(unittest.TestCase):
    def test_portico_aleatorio_vs_solver_clasico(self):
        rng = np.random.default_rng(3)
        nodos = [(0, 0), (0, 3000), (4000, 3500), (4000, 0), (2000, 4200), (6500, 1500)]
        barras = [(0, 1), (1, 4), (4, 2), (3, 2), (2, 5)]
        fijos = np.zeros((6, 3), dtype=bool)
        fijos[0] = [1, 1, 1]
        fijos[3] = [1, 1, 0]
        fijos[5] = [0, 1, 0]
        F = rng.normal(size=(6, 3)) * [1000, 1000, 1e6]
        F[fijos] = 0
        extra = "CARGAS\ncaso;nodo;Px;Py;M\n" + "".join(f"P;{k + 1};{F[k, 0]};{F[k, 1]};{F[k, 2]}\n" for k in range(6))
        ap = [(k + 1, *[int(v) for v in fijos[k]]) for k in range(6) if fijos[k].any()]
        m = modelo_de([(k + 1, *nodos[k]) for k in range(6)], [(k + 1, a + 1, b + 1) for k, (a, b) in enumerate(barras)], ap, extra)
        r = resolver_uno(m)
        u = ref_2d(nodos, barras, fijos, F, E0, A0, I0)
        self.assertTrue(np.allclose(r.u, u, rtol=1e-9, atol=1e-12))
        self.assertLess(equilibrio(m, r)["rel"], 1e-12)

    def test_invariancia_por_rotacion(self):
        ang = math.radians(37)
        c, s = math.cos(ang), math.sin(ang)
        nodos = [(0, 0), (0, 3000), (5000, 3000), (5000, 0)]
        barras = [(1, 1, 2), (2, 2, 3), (3, 4, 3)]
        Fx, Fy = 20000.0, -15000.0
        m1 = modelo_de([(k + 1, *p) for k, p in enumerate(nodos)], barras, [(1, 1, 1, 1), (4, 1, 1, 1)],
                       f"CARGAS\ncaso;nodo;Px;Py;M\nP;2;{Fx};{Fy};1e6\n\nCARGAS EN BARRAS\ncaso;barra;tipo;valor;valor2;a;b\nP;2;qgy;-3;;;\n")
        rot = lambda x, y: (c * x - s * y, s * x + c * y)
        m2 = modelo_de([(k + 1, *rot(*p)) for k, p in enumerate(nodos)], barras, [(1, 1, 1, 1), (4, 1, 1, 1)],
                       f"CARGAS\ncaso;nodo;Px;Py;M\nP;2;{c * Fx - s * Fy};{s * Fx + c * Fy};1e6\n\nCARGAS EN BARRAS\ncaso;barra;tipo;valor;valor2;a;b\n"
                       f"P;2;qgx;{-3 * -s};;;\nP;2;qgy;{-3 * c};;;\n")
        r1, r2 = resolver_uno(m1), resolver_uno(m2)
        for k in range(4):
            ux, uy = r1.u[k, :2]
            self.assertTrue(np.allclose(rot(ux, uy), r2.u[k, :2], rtol=1e-9, atol=1e-12))
            self.assertAlmostEqual(r1.u[k, 2], r2.u[k, 2], places=12)
        e1, e2 = esfuerzos(m1, r1), esfuerzos(m2, r2)
        for clave in ("N", "V", "Mi", "Mj", "Mmax", "Mmin"):
            self.assertTrue(np.allclose(e1[clave], e2[clave], rtol=1e-8, atol=1e-6), clave)

    def test_intercambio_i_j(self):
        nod = [(1, 0, 0), (2, 2500, 1500)]
        cargas = "CARGAS EN BARRAS\ncaso;barra;tipo;valor;valor2;a;b\nA;1;q;-2;;;\nA;1;P;-800;;600;\n"
        m1 = modelo_de(nod, [(1, 1, 2)], [(1, 1, 1, 1)], cargas)
        m2 = modelo_de(nod, [(1, 2, 1)], [(1, 1, 1, 1)],
                       "CARGAS EN BARRAS\ncaso;barra;tipo;valor;valor2;a;b\nA;1;q;2;;;\nA;1;P;800;;" + str(math.hypot(2500, 1500) - 600) + ";\n")
        r1, r2 = resolver_uno(m1), resolver_uno(m2)
        self.assertTrue(np.allclose(r1.u, r2.u, rtol=1e-9, atol=1e-12))
        e1, e2 = esfuerzos(m1, r1), esfuerzos(m2, r2)
        self.assertAlmostEqual(e1["N"][0], e2["Nj"][0], places=5)
        self.assertAlmostEqual(e1["V"][0], e2["Vj"][0], places=5)          # el corte "horario" no cambia
        self.assertAlmostEqual(e1["Mi"][0], -e2["Mj"][0], places=4)              # el flector cambia de signo (cambia yl)
        self.assertAlmostEqual(e1["Mmax"][0], -e2["Mmin"][0], places=4)


class TestReticuladoParcial2020(unittest.TestCase):
    """Reticulado del 1er parcial 2do sem. 2020 (Brewer): barras articuladas, ΔT uniforme, q axial, uy prefijado."""

    def test_resultados_del_examen(self):
        m = cargar_modelo(RAIZ / "003_Ejemplos" / "002_Portico" / "ejemplo5_reticulado_parcial2020.csv")
        r = resolver(m)[0]["E"]
        self.assertAlmostEqual(r.u[0, 0], -0.0124, delta=5e-5)
        self.assertAlmostEqual(r.u[2, 1], 0.0088, delta=5e-5)
        e = esfuerzos(m, r)
        self.assertAlmostEqual(e["N"][0], -406.6, delta=0.5)          # barra 1: compresión
        self.assertAlmostEqual(e["N"][2], 325.5, delta=0.6)           # barra 3: tracción
        self.assertAlmostEqual(-r.R[0, 1], 244.0, delta=0.5)          # reacción vertical en el nudo 1
        self.assertAlmostEqual(e["N"][1] - e["Nj"][1], 10 * 90, places=6)   # q axial: ΔN = q·L


class TestEjerciciosCatedra(unittest.TestCase):
    """Ejercicios resueltos por la cátedra (TP5 2022, parcial con prefijado y pórtico con barra de reticulado)."""

    def _res(self, nombre, caso):
        m = cargar_modelo(RAIZ / "003_Ejemplos" / "002_Portico" / nombre)
        return m, resolver(m)[0][caso]

    def test_parcial_2S2020_ej3_desplazamiento_ux_prefijado(self):
        m, r = self._res("ejemplo10_parcial_2S2020_Ej3_desplazamiento_ux.csv", "C")
        self.assertAlmostEqual(r.u[1, 1], -0.0062, delta=1e-4)
        self.assertAlmostEqual(r.u[1, 2], 0.0042, delta=1e-4)
        e = esfuerzos(m, r)
        self.assertAlmostEqual(abs(e["V"][0]), 1982, delta=5)
        self.assertAlmostEqual(abs(e["V"][1]), 1701, delta=5)

    def test_parcial_1S2022_temperatura_resorte_y_prefijado(self):
        m, r = self._res("ejemplo11_parcial_1S2022_temperatura_resorte.csv", "C")
        self.assertAlmostEqual(r.u[1, 0], -0.34892, delta=1e-4)
        self.assertAlmostEqual(r.u[1, 2], 0.006588, delta=1e-5)
        e = esfuerzos(m, r)
        self.assertAlmostEqual(e["N"][0], -2808.5, delta=5)
        self.assertAlmostEqual(abs(e["V"][0]), 2828.3, delta=1)

    def test_tp5_2022_resorte_inclinado_y_prefijados(self):
        m, r = self._res("ejemplo6_TP5_2022_resorte_inclinado.csv", "C")
        self.assertAlmostEqual(r.u[0, 1], 1.9242, delta=5e-4)
        self.assertAlmostEqual(r.u[1, 0], -0.0289, delta=5e-4)
        self.assertAlmostEqual(r.u[1, 2], 0.0068, delta=5e-5)
        self.assertAlmostEqual(r.u[2, 0], 3.9043, delta=5e-4)
        e = esfuerzos(m, r)
        self.assertAlmostEqual(e["N"][0], -9708.3, delta=0.2)
        self.assertAlmostEqual(e["N"][1], -13459.3, delta=0.2)
        self.assertAlmostEqual(e["V"][1], 2405.6, delta=0.2)
        self.assertAlmostEqual(math.hypot(*r.Rk[1, :2]), 364.62, delta=0.02)
        t = tensiones(m, e)
        self.assertAlmostEqual(t[0]["vm"], 181.53, delta=0.02)
        self.assertAlmostEqual(t[1]["n_fy"], 3.61, delta=0.01)

    def test_parcial_momento_y_desplazamiento_prefijado(self):
        m, r = self._res("ejemplo7_TP_parcial_desplazamiento_prefijado.csv", "C")
        self.assertAlmostEqual(r.u[1, 0], -0.0062, delta=5e-5)
        self.assertAlmostEqual(r.u[1, 2], 0.0042, delta=5e-5)
        e = esfuerzos(m, r)
        self.assertAlmostEqual(abs(e["Mi"][0]), 1320656, delta=3000)
        self.assertAlmostEqual(e["Mj"][0], 2643656, delta=5000)
        self.assertAlmostEqual(e["V"][1], 1701, delta=5)
        self.assertAlmostEqual(abs(r.R[1, 1]), 50.6, delta=3)

    def test_portico_con_barra_de_reticulado(self):
        m, r = self._res("ejemplo8_portico_con_barra_reticulado.csv", "C")
        self.assertAlmostEqual(r.u[0, 2], 0.00227, delta=5e-6)
        self.assertAlmostEqual(r.u[1, 0], -0.01878, delta=5e-5)
        self.assertAlmostEqual(r.u[2, 1], -0.03773, delta=5e-5)
        e = esfuerzos(m, r)
        self.assertAlmostEqual(e["Mj"][0], 181310, delta=10)
        self.assertAlmostEqual(e["N"][2], -2330.8, delta=0.2)
        t = tensiones(m, e)
        self.assertAlmostEqual(t[2]["sig_c"], -97.1, delta=0.05)
        self.assertAlmostEqual(t[0]["sig_t"], 1049.2, delta=0.2)
        self.assertAlmostEqual(r.R[3, 0], 1499.13, delta=0.1)


class TestDesajusteDeLongitud(unittest.TestCase):
    def test_barra_biempotrada_larga_y_corta(self):
        t = CAB + """NODOS
id;x;y
1;0;0
2;1000;0

BARRAS
id;nodo_i;nodo_j;material;seccion
1;1;2;m;s

APOYOS
nodo;ux;uy;phi
1;1;1;1
2;1;1;1

CARGAS EN BARRAS
caso;barra;tipo;valor
X;1;dl;{e}
"""
        for e in (0.5, -0.5):
            d = Path(tempfile.mkdtemp()) / "t.csv"
            d.write_text(t.format(e=e), encoding="utf-8")
            m = cargar_modelo(d)
            r = resolver(m)[0]["X"]
            self.assertAlmostEqual(esfuerzos(m, r)["N"][0], -E0 * A0 * e / 1000, places=6)      # larga (+) → compresión


class TestFuncionesYCurvas(unittest.TestCase):
    def test_funciones_coinciden_con_extremos_y_continuidad(self):
        m = cargar_modelo(RAIZ / "003_Ejemplos" / "002_Portico" / "ejemplo4_temperatura_y_puntuales.csv")
        res, _ = resolver(m)
        for nombre, r in res.items():
            e = esfuerzos(m, r)
            for k, b in enumerate(m.barras):
                pz = funciones_barra(m, r, k)
                self.assertAlmostEqual(pz[-1]["N"](b.L), e["Nj"][k], delta=1e-6 * (1 + abs(e["Nj"][k])) + 1e-7)
                self.assertAlmostEqual(pz[-1]["M"](b.L), e["Mj"][k], delta=1e-6 * (1 + abs(e["Mj"][k])) + 1e-7)
                self.assertAlmostEqual(pz[-1]["V"](b.L), e["Vj"][k], delta=1e-6 * (1 + abs(e["Vj"][k])) + 1e-7)
                self.assertAlmostEqual(pz[0]["M"](0.0), e["Mi"][k], delta=1e-6 * (1 + abs(e["Mi"][k])) + 1e-7)

    def test_elastica_coincide_con_nodos(self):
        m = cargar_modelo(RAIZ / "003_Ejemplos" / "002_Portico" / "ejemplo1_portico_simple.csv")
        res, _ = resolver(m)
        r = res["COMB1"]
        for k, b in enumerate(m.barras):
            X0, Y0, DX, DY = elastica(m, r)[k]
            self.assertAlmostEqual(DX[0], r.u[b.i, 0], places=8)
            self.assertAlmostEqual(DY[-1], r.u[b.j, 1], places=8)
            self.assertAlmostEqual(DX[-1], r.u[b.j, 0], places=8)

    def test_combinacion_lineal(self):
        m = cargar_modelo(RAIZ / "003_Ejemplos" / "002_Portico" / "ejemplo1_portico_simple.csv")
        res, _ = resolver(m)
        a = 1.2 * res["CARGA_MUERTA"].u + 1.6 * res["VIENTO"].u
        self.assertTrue(np.allclose(a, res["COMB1"].u))
        ea, eb = esfuerzos(m, res["COMB1"]), esfuerzos(m, res["VIENTO"])
        ec = esfuerzos(m, res["CARGA_MUERTA"])
        self.assertTrue(np.allclose(ea["Mi"], 1.2 * ec["Mi"] + 1.6 * eb["Mi"]))


class TestTensiones(unittest.TestCase):
    def test_flexion_pura_y_axil(self):
        L = 2000.0
        m = modelo_de([(1, 0, 0), (2, L, 0)], [(1, 1, 2)], [(1, 1, 1, 1)], "CARGAS\ncaso;nodo;Px;Py;M\nP;2;5000;-1000;0\n")
        r = resolver_uno(m)
        t = tensiones(m, esfuerzos(m, r))[0]
        s = 5000 / 1000 + 1000 * L * 100 / 2e7
        self.assertAlmostEqual(t["sig_t"], s, places=6)
        self.assertAlmostEqual(t["sig_c"], 5000 / 1000 - 1000 * L * 100 / 2e7, places=6)
        self.assertAlmostEqual(t["tau_v"], 1.5 * 1000 / 1000, places=8)
        self.assertAlmostEqual(t["n_fy"], 250 / t["vm"], places=8)


class TestErrores(unittest.TestCase):
    def test_mecanismo(self):
        with self.assertRaises(ErrorEstructura):
            m = modelo_de([(1, 0, 0), (2, 3000, 0), (3, 6000, 0)], [(1, 1, 2, 1, 1), (2, 2, 3, 1, 1)],
                          [(1, 1, 1, 0), (3, 1, 1, 0)], "CARGAS\ncaso;nodo;Px;Py;M\nP;2;0;-1;0\n")
            resolver(m)

    def test_columna_biarticulada_aislada_es_mecanismo(self):
        with self.assertRaises(ErrorEstructura):
            m = modelo_de([(1, 0, 0), (2, 0, 3000)], [(1, 1, 2)], [(1, 1, 1, 0)], "CARGAS\ncaso;nodo;Px;Py;M\nP;2;100;0;0\n")
            resolver(m)

    def test_datos_invalidos(self):
        nod, bar, ap = [(1, 0, 0), (2, 3000, 0)], [(1, 1, 2)], [(1, 1, 1, 1)]
        for extra, frag in [
            ("CARGAS EN BARRAS\ncaso;barra;tipo;valor;valor2;a;b\nA;1;zz;1;;;\n", "desconocido"),
            ("CARGAS EN BARRAS\ncaso;barra;tipo;valor;valor2;a;b\nA;1;q;1;;2000;5000\n", "0 ≤ a < b ≤ L"),
            ("CARGAS EN BARRAS\ncaso;barra;tipo;valor;valor2;a;b\nA;1;P;1;;9000;\n", "fuera de la barra"),
            ("CARGAS EN BARRAS\ncaso;barra;tipo;valor;valor2;a;b\nA;9;P;1;;10;\n", "no existe"),
            ("DESPLAZAMIENTOS PREFIJADOS\ncaso;nodo;ux;uy;phi\nA;2;1;0;0\n", "no está restringido"),
            ("CARGAS\ncaso;nodo;Px;Py;M\nA;9;1;0;0\n", "no existe"),
        ]:
            with self.assertRaises(ErrorDeEntrada, msg=extra) as cm:
                modelo_de(nod, bar, ap, extra)
            self.assertIn(frag, str(cm.exception))

    def test_temperatura_sin_alfa(self):
        cab = CAB.replace("m;200000;0.3;250;150;0.00001", "m;200000;0.3;250;150;")
        with self.assertRaises(ErrorDeEntrada):
            modelo_de([(1, 0, 0), (2, 3000, 0)], [(1, 1, 2)], [(1, 1, 1, 1)],
                      "CARGAS EN BARRAS\ncaso;barra;tipo;valor;valor2;a;b\nA;1;temp;10;0;;\n", cab=cab)

    def test_tipo_emparrillado_redirige(self):
        cab = CAB.replace("tipo;portico", "tipo;emparrillado")
        with self.assertRaises(ErrorDeEntrada):
            modelo_de([(1, 0, 0), (2, 3000, 0)], [(1, 1, 2)], [(1, 1, 1, 1)], "CARGAS\ncaso;nodo;Px;Py;M\nA;2;1;0;0\n", cab=cab)


class TestDespachadorEInformes(unittest.TestCase):
    def test_detectar_tipo(self):
        sys.path.insert(0, str(RAIZ / "001_Codigo"))
        from struttura import despachador as calcular
        self.assertEqual(calcular.detectar_tipo(RAIZ / "003_Ejemplos" / "002_Portico" / "ejemplo1_portico_simple.csv"), "portico")
        self.assertEqual(calcular.detectar_tipo(RAIZ / "003_Ejemplos" / "001_Emparrillado" / "ejemplo2_parrilla.csv"), "emparrillado")

    def test_comando_struttura_con_las_tres_plantillas(self):
        """Punto de entrada real (struttura.py): elige el programa y escribe el informe."""
        import subprocess
        for nombre in ("plantilla_portico", "plantilla_reticulado", "plantilla_emparrillado"):
            with tempfile.TemporaryDirectory() as d:
                r = subprocess.run([sys.executable, str(RAIZ / "struttura.py"), str(RAIZ / "002_Plantillas" / f"{nombre}.csv"),
                                    "--sin-graficos", "-o", d], capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertTrue((Path(d) / "informe.html").exists(), nombre)

    def test_plantillas_son_validas(self):
        from struttura.emparrillado.entrada import cargar_modelo as cargar_emp
        from struttura.emparrillado.solver import resolver as resolver_emp
        m = cargar_modelo(RAIZ / "002_Plantillas" / "plantilla_portico.csv")
        resolver(m)
        me = cargar_emp(RAIZ / "002_Plantillas" / "plantilla_emparrillado.csv")
        resolver_emp(me)
        with self.assertRaises(ErrorDeEntrada):                      # cada programa rechaza el archivo del otro
            cargar_emp(RAIZ / "002_Plantillas" / "plantilla_portico.csv")
        with self.assertRaises(ErrorDeEntrada):
            cargar_modelo(RAIZ / "002_Plantillas" / "plantilla_emparrillado.csv")

    def test_ejemplos_calculan_con_equilibrio_e_informe(self):
        from struttura.portico.informe import generar_html, generar_html_esquema
        for f in sorted((RAIZ / "003_Ejemplos" / "002_Portico").glob("*.csv")):
            m = cargar_modelo(f)
            res, info = resolver(m)
            for nombre, r in res.items():
                self.assertLess(equilibrio(m, r)["rel"], 1e-9, f"{f.name}/{nombre}")
            h = generar_html(m, res, info, con_graficos=True)
            self.assertIn("Memoria de cálculo", h)
            self.assertIn("emp2d(", h)
            self.assertGreater(len(h), 50000)
            generar_html(m, res, info, con_graficos=False)
            self.assertIn("Revisión de datos", generar_html_esquema(m))


if __name__ == "__main__":
    unittest.main()
