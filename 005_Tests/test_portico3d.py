"""Tests del pórtico espacial (3D).  Ejecutar:  python -m unittest discover -s 005_Tests   (desde la raíz)"""
import math
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "001_Codigo"))

from struttura.portico3d import cargas_barra as cb3  # noqa: E402
from struttura.portico3d.barra import rigidez_local, terna_local  # noqa: E402
from struttura.portico3d.entrada import ErrorDeEntrada, cargar_modelo  # noqa: E402
from struttura.portico3d.esfuerzos import diagramas  # noqa: E402
from struttura.portico3d.solver import ErrorEstructura, equilibrio, resolver  # noqa: E402

E_, G_, A_, IY, IZ, J_ = 210e3, 80e3, 1000.0, 3e6, 2e6, 4e6


def escribir(texto):
    p = Path(tempfile.mkdtemp()) / "t.csv"
    p.write_text(texto, encoding="utf-8")
    return p


def modelo3d(nodos, barras, apoyos, cargas="", extra="", sec="s;generica;1000;3000000;2000000;4000000", barcols="",
             sec_cab="id;tipo;A;Iy;Iz;J"):
    """nodos: [(id,x,y,z)]; barras: [(id,i,j[,extra])]; apoyos: [(nodo, '111111')]"""
    t = "PROYECTO\ntipo;portico3d\n\nNODOS\nid;x;y;z\n" + "\n".join(";".join(map(str, n)) for n in nodos)
    t += "\n\nMATERIALES\nid;E;G;fy\nm;210000;80000;235\n\nSECCIONES\n" + sec_cab + "\n" + sec + "\n\nBARRAS\nid;nodo_i;nodo_j;material;seccion" + barcols + "\n"
    t += "\n".join(f"{b[0]};{b[1]};{b[2]};m;s" + (";" + b[3] if len(b) > 3 else "") for b in barras)
    t += "\n\nAPOYOS\nnodo;ux;uy;uz;phix;phiy;phiz\n" + "\n".join(f"{n};" + ";".join(f) for n, f in apoyos)
    t += "\n\n" + cargas + "\n" + extra
    return cargar_modelo(escribir(t))


FIJO = "1;1;1;1;1;1".split(";")


class TestMatriz(unittest.TestCase):
    def test_simetrica_y_seis_modos_rigidos(self):
        k = rigidez_local(E_, G_, A_, IY, IZ, J_, 1000.0)
        self.assertLess(np.abs(k - k.T).max(), 1e-9)
        w = np.linalg.eigvalsh(k)
        self.assertEqual(int((abs(w) < 1e-9 * w.max()).sum()), 6)

    def test_voladizo_cada_gdl(self):
        L = 1000.0
        k = rigidez_local(E_, G_, A_, IY, IZ, J_, L)
        kk = k[6:, 6:]                            # nudo i empotrado
        f = np.zeros(6)
        for c, esperado in ((0, L / (E_ * A_)), (3, L / (G_ * J_)), (1, L**3 / (3 * E_ * IZ)), (2, L**3 / (3 * E_ * IY))):
            f[:] = 0
            f[c] = 1
            self.assertAlmostEqual(np.linalg.solve(kk, f)[c] / esperado, 1.0, places=9)
        # momento en la punta: giro M L/EI ; flecha M L²/2EI (con el signo de θy = -dw/dx)
        f[:] = 0
        f[5] = 1
        u = np.linalg.solve(kk, f)
        self.assertAlmostEqual(u[5], L / (E_ * IZ), places=12)
        self.assertAlmostEqual(u[1], L**2 / (2 * E_ * IZ), places=12)
        f[:] = 0
        f[4] = 1
        u = np.linalg.solve(kk, f)
        self.assertAlmostEqual(u[4], L / (E_ * IY), places=12)
        self.assertAlmostEqual(u[2], -L**2 / (2 * E_ * IY), places=12)

    def test_terna_derecha_y_defecto(self):
        R, L = terna_local([0, 0, 0], [3, 4, 0])
        self.assertAlmostEqual(L, 5)
        np.testing.assert_allclose(R @ R.T, np.eye(3), atol=1e-12)
        self.assertAlmostEqual(np.linalg.det(R), 1.0)
        np.testing.assert_allclose(R[2], [0, 0, 1], atol=1e-12)          # z local = Z global
        R, _ = terna_local([0, 0, 0], [0, 0, 2])                           # barra vertical: z local = +X
        np.testing.assert_allclose(R[2], [1, 0, 0], atol=1e-12)
        self.assertAlmostEqual(np.linalg.det(R), 1.0)


class TestAnaliticos(unittest.TestCase):
    def test_voladizo_en_L(self):
        m = cargar_modelo(RAIZ / "003_Ejemplos" / "004_Portico_espacial" / "ejemplo1_voladizo_en_L.csv")
        r = resolver(m)[0]["P"]
        b = m.barras[0]
        E, G, I, J = b.mat.E, b.mat.G, b.sec.Iy, b.sec.J
        L1, L2, P = 1000.0, 600.0, 1000.0
        uz = -P * L2**3 / (3 * E * I) - P * L1**3 / (3 * E * I) - (P * L2 * L1 / (G * J)) * L2
        self.assertAlmostEqual(r.u[2, 2] / uz, 1.0, places=9)
        self.assertLess(equilibrio(m, r)["rel"], 1e-12)
        # esfuerzos en la barra 1: T = P·L2 y My en la raíz = P·L1 (hogging, tracciona +z)
        xs, Ed = diagramas(m, r, 0)
        self.assertAlmostEqual(abs(Ed[0, 3]), P * L2, delta=1e-6 * P * L2)
        self.assertAlmostEqual(abs(Ed[0, 4]), P * L1, delta=1e-6 * P * L1)

    def test_carga_distribuida_voladizo_diagramas(self):
        w, L = 2.0, 1000.0
        m = modelo3d([(1, 0, 0, 0), (2, L, 0, 0)], [(1, 1, 2)], [(1, FIJO)],
                     "CARGAS EN BARRAS\ncaso;barra;tipo;valor;valor2;a\nQ;1;qz;-2;;")
        r = resolver(m)[0]["Q"]
        self.assertAlmostEqual(r.u[1, 2], -w * L**4 / (8 * E_ * IY), places=9)
        xs, Ed = diagramas(m, r, 0)
        self.assertAlmostEqual(Ed[0, 2], -w * L, places=6)                  # Vz en la raíz
        self.assertAlmostEqual(Ed[0, 4], w * L**2 / 2, places=4)             # My en la raíz
        i = len(xs) // 2
        x = xs[i]
        self.assertAlmostEqual(Ed[i, 4], w * (L - x) ** 2 / 2, places=4)
        self.assertLess(np.abs(Ed[-1]).max(), 1e-6)                          # extremo libre sin esfuerzos

    def test_empotramiento_perfecto_distribuida_y_puntual(self):
        L, w = 1000.0, 3.0
        f = cb3.equivalente_local(("q", np.array([0, w, 0.0]), np.array([0, w, 0.0]), L), L)
        self.assertAlmostEqual(f[1], w * L / 2, places=9)
        self.assertAlmostEqual(f[7], w * L / 2, places=9)
        self.assertAlmostEqual(f[5], w * L**2 / 12, places=6)
        self.assertAlmostEqual(f[11], -w * L**2 / 12, places=6)
        a, P = 300.0, 500.0
        f = cb3.equivalente_local(("P", a, np.array([0, 0, P])), L)
        b = L - a
        self.assertAlmostEqual(f[2], P * b**2 * (3 * a + b) / L**3, places=6)       # reacción en i
        self.assertAlmostEqual(f[4], -P * a * b**2 / L**2, places=6)                # My_i equivalente (signo de θy)
        self.assertAlmostEqual(f[10], P * a**2 * b / L**2, places=6)
        self.assertAlmostEqual(f[2] + f[8], P, places=9)

    def test_carga_trapezoidal_resultante_y_centroide(self):
        L = 1000.0
        f = cb3.equivalente_local(("q", np.array([0, 0, 1.0]), np.array([0, 0, 3.0]), L), L)
        self.assertAlmostEqual(f[2] + f[8], 2.0 * L, places=6)
        # momento respecto de i: centroide del trapecio en (1+2·3)/(3(1+3))·L... = (q1+2q2)/(3(q1+q2)) L
        cen = (1 + 2 * 3) / (3 * (1 + 3)) * L
        self.assertAlmostEqual((f[8] * L - f[4] - f[10]) / (f[2] + f[8]), cen, places=6)


class TestContraLosProgramasPlanos(unittest.TestCase):
    """El 3D con estructura plana debe dar lo mismo que el pórtico plano y el emparrillado ya validados."""

    def _portico2d(self, texto):
        from struttura.portico.entrada import cargar_modelo as cm2
        from struttura.portico.solver import resolver as rs2
        m = cm2(escribir(texto))
        return m, rs2(m)[0]

    def test_portico_plano_XY_y_XZ(self):
        cab2 = """PROYECTO
tipo;portico

NODOS
id;x;y
1;0;0
2;0;3000
3;4000;3000
4;4000;0

MATERIALES
id;E
m;210000

SECCIONES
id;tipo;I;A
s;generica;2000000;1000

BARRAS
id;nodo_i;nodo_j;material;seccion
1;1;2;m;s
2;2;3;m;s
3;4;3;m;s

APOYOS
nodo;ux;uy;phi
1;1;1;1
4;1;1;0

CARGAS
caso;nodo;Px;Py;M
C;2;5000;-2000;100000

CARGAS EN BARRAS
caso;barra;tipo;valor;valor2;a;b
C;2;qgy;-3;;;
"""
        m2, r2 = self._portico2d(cab2)
        r2 = r2["C"]
        # 3D en el plano XY (flexión con Iz) y en el plano XZ (flexión con Iy: mismos datos numéricos)
        for plano in ("XY", "XZ"):
            if plano == "XY":
                nodos = [(1, 0, 0, 0), (2, 0, 3000, 0), (3, 4000, 3000, 0), (4, 4000, 0, 0)]
                cargas = "CARGAS\ncaso;nodo;Fx;Fy;Fz;Mx;My;Mz\nC;2;5000;-2000;0;0;0;100000\n\nCARGAS EN BARRAS\ncaso;barra;tipo;valor;valor2;a\nC;2;qgy;-3;;"
                sec = "s;generica;1000;9000000;2000000;4000000"
                ap = [(1, FIJO), (4, "1;1;1;1;1;0".split(";"))]
            else:
                nodos = [(1, 0, 0, 0), (2, 0, 0, 3000), (3, 4000, 0, 3000), (4, 4000, 0, 0)]
                # φ2D (antihorario en x-y) ↔ en x-z con eje Y: giro positivo alrededor de Y = -(giro antihorario x-z)... se usa -M
                cargas = "CARGAS\ncaso;nodo;Fx;Fy;Fz;Mx;My;Mz\nC;2;5000;0;-2000;0;-100000;0\n\nCARGAS EN BARRAS\ncaso;barra;tipo;valor;valor2;a\nC;2;qgz;-3;;"
                sec = "s;generica;1000;2000000;9000000;4000000"
                ap = [(1, FIJO), (4, "1;1;1;1;0;1".split(";"))]
            m = modelo3d(nodos, [(1, 1, 2), (2, 2, 3), (3, 4, 3)], ap, cargas, sec=sec)
            r = resolver(m)[0]["C"]
            self.assertLess(equilibrio(m, r)["rel"], 1e-12)
            sg = 1.0 if plano == "XY" else -1.0
            uy = 1 if plano == "XY" else 2
            gi = 5 if plano == "XY" else 4
            for k in range(4):
                self.assertAlmostEqual(r.u[k, 0], r2.u[k, 0], places=9, msg=f"{plano} ux nudo {k}")
                self.assertAlmostEqual(r.u[k, uy], r2.u[k, 1], places=9, msg=f"{plano} uy nudo {k}")
                self.assertAlmostEqual(sg * r.u[k, gi], r2.u[k, 2], places=11, msg=f"{plano} φ nudo {k}")
            # reacciones
            for k in (0, 3):
                self.assertAlmostEqual(r.R[k, 0], r2.R[k, 0], places=6)
                self.assertAlmostEqual(r.R[k, uy], r2.R[k, 1], places=6)
                if k == 0:
                    self.assertAlmostEqual(sg * r.R[k, gi], r2.R[k, 2], places=3)

    def test_emparrillado_en_XY(self):
        from struttura.emparrillado.entrada import cargar_modelo as cm_e
        from struttura.emparrillado.solver import resolver as rs_e
        te = """PROYECTO
proyecto;g

NODOS
id;x;y
1;0;0
2;3000;0
3;3000;2000
4;0;2000

MATERIALES
id;E;G
m;210000;80000

SECCIONES
id;tipo;I;J
s;generica;3000000;4000000

BARRAS
id;nodo_i;nodo_j;material;seccion
1;1;2;m;s
2;2;3;m;s
3;3;4;m;s
4;4;1;m;s

APOYOS
nodo;uz;phix;phiy
1;1;1;1
3;1;0;0

CARGAS
caso;nodo;Pz;Mx;My
C;2;-4000;20000;-30000
C;4;-1500;0;0

CARGAS EN BARRAS
caso;barra;tipo;valor;valor2;a;b
C;2;q;-2;;;
"""
        me = cm_e(escribir(te))
        re_ = rs_e(me)[0]["C"]
        m = modelo3d([(1, 0, 0, 0), (2, 3000, 0, 0), (3, 3000, 2000, 0), (4, 0, 2000, 0)],
                     [(1, 1, 2), (2, 2, 3), (3, 3, 4), (4, 4, 1)],
                     [(1, FIJO), (3, "0;0;1;0;0;0".split(";"))],
                     "CARGAS\ncaso;nodo;Fx;Fy;Fz;Mx;My;Mz\nC;2;0;0;-4000;20000;-30000;0\nC;4;0;0;-1500;0;0;0\n\n"
                     "CARGAS EN BARRAS\ncaso;barra;tipo;valor;valor2;a\nC;2;qz;-2;;")
        # nudo 3 en emparrillado: uz restringido (phix, phiy libres); en 3D restringir también el plano (ux, uy, φz) para
        # que sea isostático en el plano: no afecta a la flexión fuera de plano.
        m = modelo3d([(1, 0, 0, 0), (2, 3000, 0, 0), (3, 3000, 2000, 0), (4, 0, 2000, 0)],
                     [(1, 1, 2), (2, 2, 3), (3, 3, 4), (4, 4, 1)],
                     [(1, FIJO), (3, "1;1;1;0;0;1".split(";"))],
                     "CARGAS\ncaso;nodo;Fx;Fy;Fz;Mx;My;Mz\nC;2;0;0;-4000;20000;-30000;0\nC;4;0;0;-1500;0;0;0\n\n"
                     "CARGAS EN BARRAS\ncaso;barra;tipo;valor;valor2;a\nC;2;qz;-2;;",
                     sec="s;generica;1000;3000000;3000000;4000000")
        r = resolver(m)[0]["C"]
        for k in range(4):
            self.assertAlmostEqual(r.u[k, 2], re_.u[k, 0], places=8, msg=f"uz nudo {k}")
            self.assertAlmostEqual(r.u[k, 3], re_.u[k, 1], places=11, msg=f"φx nudo {k}")
            self.assertAlmostEqual(r.u[k, 4], re_.u[k, 2], places=11, msg=f"φy nudo {k}")


class TestInvarianciaYOrientacion(unittest.TestCase):
    def test_rotacion_rigida_de_toda_la_estructura(self):
        rng = np.random.default_rng(3)
        Q, _ = np.linalg.qr(rng.normal(size=(3, 3)))
        if np.linalg.det(Q) < 0:
            Q[:, 0] *= -1
        nod = [(1, 0, 0, 0), (2, 1500, 300, 800), (3, 2500, 1200, 200), (4, 900, 1500, 1600)]
        bar = [(1, 1, 2), (2, 2, 3), (3, 2, 4), (4, 3, 4)]
        F2 = np.array([1000.0, -500.0, 800.0]); M2 = np.array([30000.0, 20000.0, -10000.0])
        F4 = np.array([-200.0, 300.0, -900.0])
        sec = "s;tubo;76.1;4"
        cab = "id;tipo;d;t"

        def armar(Qm, off):
            nn = [(n[0], *(Qm @ np.array(n[1:]) + off)) for n in nod]
            c = "CARGAS\ncaso;nodo;Fx;Fy;Fz;Mx;My;Mz\n"
            for nd, F, M in ((2, F2, M2), (4, F4, np.zeros(3))):
                c += f"C;{nd};" + ";".join(repr(float(v)) for v in (*(Qm @ F), *(Qm @ M))) + "\n"
            m = modelo3d(nn, bar, [(1, FIJO), (3, "1;1;1;0;0;0".split(";"))], c, sec=sec, sec_cab=cab)
            return m, resolver(m)[0]["C"]
        m0, r0 = armar(np.eye(3), np.zeros(3))
        m1, r1 = armar(Q, np.array([1e3, -2e3, 5e2]))
        for k in range(4):
            np.testing.assert_allclose(r1.u[k, :3], Q @ r0.u[k, :3], rtol=1e-8, atol=1e-12)
            np.testing.assert_allclose(r1.u[k, 3:], Q @ r0.u[k, 3:], rtol=1e-8, atol=1e-14)
        # esfuerzos locales de barra: N, |V|, |T|, |M| no cambian
        for kb in range(4):
            a, b = r0.fb[kb], r1.fb[kb]
            self.assertAlmostEqual(a[0], b[0], places=5)
            self.assertAlmostEqual(math.hypot(a[1], a[2]), math.hypot(b[1], b[2]), places=5)
            self.assertAlmostEqual(abs(a[3]), abs(b[3]), places=4)
            self.assertAlmostEqual(math.hypot(a[4], a[5]), math.hypot(b[4], b[5]), places=3)

    def test_giro_90_equivale_a_intercambiar_b_y_h(self):
        nod = [(1, 0, 0, 0), (2, 2000, 0, 0)]
        c = "CARGAS\ncaso;nodo;Fx;Fy;Fz;Mx;My;Mz\nC;2;0;500;-800;0;0;0\n"
        cab = "id;tipo;b;h"
        base = modelo3d(nod, [(1, 1, 2)], [(1, FIJO)], c, sec="s;rectangular;40;80", sec_cab=cab)
        g0 = modelo3d(nod, [(1, 1, 2, "0")], [(1, FIJO)], c, sec="s;rectangular;40;80", sec_cab=cab, barcols=";giro")
        g90 = modelo3d(nod, [(1, 1, 2, "90")], [(1, FIJO)], c, sec="s;rectangular;80;40", sec_cab=cab, barcols=";giro")
        g90_igual = modelo3d(nod, [(1, 1, 2, "90")], [(1, FIJO)], c, sec="s;rectangular;40;80", sec_cab=cab, barcols=";giro")
        ub = resolver(base)[0]["C"].u
        np.testing.assert_allclose(resolver(g0)[0]["C"].u, ub, rtol=1e-12, atol=1e-15)
        # giro 90° con b=80, h=40: la dimensión de 80 mm queda vertical -> mismo comportamiento que la sección original
        np.testing.assert_allclose(resolver(g90)[0]["C"].u, ub, rtol=1e-9, atol=1e-13)
        # giro 90° sin cambiar b y h: la sección queda acostada -> la flecha vertical crece (I baja de 80³·40/12 a 40³·80/12)
        ug = resolver(g90_igual)[0]["C"].u
        self.assertAlmostEqual(ug[1, 2] / ub[1, 2], (40 * 80**3 / 12) / (80 * 40**3 / 12), places=6)

    def test_vector_de_referencia_equivale_a_giro(self):
        nod = [(1, 0, 0, 0), (2, 1500, 1000, 0)]
        c = "CARGAS\ncaso;nodo;Fx;Fy;Fz;Mx;My;Mz\nC;2;0;0;-800;0;0;0\n"
        a = modelo3d(nod, [(1, 1, 2)], [(1, FIJO)], c, sec="s;rectangular;30;90", sec_cab="id;tipo;b;h")
        b = modelo3d(nod, [(1, 1, 2, "0;0;1")], [(1, FIJO)], c, sec="s;rectangular;30;90", sec_cab="id;tipo;b;h", barcols=";rx;ry;rz")
        np.testing.assert_allclose(resolver(a)[0]["C"].u, resolver(b)[0]["C"].u, rtol=1e-12, atol=1e-15)
        # con la sección vertical (h según Z) la flecha en Z es menor que con la sección acostada (ref horizontal)
        h = modelo3d(nod, [(1, 1, 2, "-1;1.5;0")], [(1, FIJO)], c, sec="s;rectangular;30;90", sec_cab="id;tipo;b;h", barcols=";rx;ry;rz")
        self.assertGreater(abs(resolver(h)[0]["C"].u[1, 2]), 5 * abs(resolver(a)[0]["C"].u[1, 2]))


class TestSolverYEntrada(unittest.TestCase):
    def test_esfuerzos_en_j_igualan_fuerzas_de_extremo(self):
        m = cargar_modelo(RAIZ / "003_Ejemplos" / "004_Portico_espacial" / "ejemplo2_portico_espacial.csv")
        res = resolver(m)[0]
        for nombre in ("PESO", "VIENTO", "ULT"):
            r = res[nombre]
            self.assertLess(equilibrio(m, r)["rel"], 1e-10)
            for k in range(len(m.barras)):
                xs, Ed = diagramas(m, r, k)
                esperado = r.fb[k][6:]
                np.testing.assert_allclose(Ed[-1], esperado, rtol=1e-7, atol=1e-6 * (np.abs(esperado).max() + 1))

    def test_combinacion_lineal(self):
        m = cargar_modelo(RAIZ / "003_Ejemplos" / "004_Portico_espacial" / "ejemplo2_portico_espacial.csv")
        res = resolver(m)[0]
        np.testing.assert_allclose(res["ULT"].u, 1.4 * (res["PESO"].u + res["VIENTO"].u), rtol=1e-9, atol=1e-12)

    def test_mecanismo_da_error_claro(self):
        m = modelo3d([(1, 0, 0, 0), (2, 1000, 0, 0)], [(1, 1, 2)], [(1, "1;1;1;0;0;0".split(";"))],
                     "CARGAS\ncaso;nodo;Fx;Fy;Fz;Mx;My;Mz\nC;2;0;0;-100;0;0;0")
        with self.assertRaises(ErrorEstructura) as cm:
            resolver(m)
        self.assertIn("inestable", str(cm.exception))

    def test_errores_de_datos(self):
        with self.assertRaises(ErrorDeEntrada):                 # falta G y nu
            cargar_modelo(escribir("PROYECTO\ntipo;portico3d\nNODOS\nid;x;y;z\n1;0;0;0\n2;1;0;0\nMATERIALES\nid;E\nm;1\n"
                                   "SECCIONES\nid;tipo;A;Iy;Iz;J\ns;generica;1;1;1;1\nBARRAS\nid;nodo_i;nodo_j;material;seccion\n1;1;2;m;s\n"
                                   "APOYOS\nnodo;ux;uy;uz;phix;phiy;phiz\n1;1;1;1;1;1;1\n"))
        with self.assertRaises(ErrorDeEntrada):                 # ref paralelo a la barra
            modelo3d([(1, 0, 0, 0), (2, 1000, 0, 0)], [(1, 1, 2, "1;0;0")], [(1, FIJO)],
                     "CARGAS\ncaso;nodo;Fx;Fy;Fz;Mx;My;Mz\nC;2;1;0;0;0;0;0", barcols=";rx;ry;rz")
        with self.assertRaises(ErrorDeEntrada):                 # prefijado en GDL libre
            modelo3d([(1, 0, 0, 0), (2, 1000, 0, 0)], [(1, 1, 2)], [(1, FIJO)],
                     "DESPLAZAMIENTOS PREFIJADOS\ncaso;nodo;ux;uy;uz;phix;phiy;phiz\nC;2;1;0;0;0;0;0")
        with self.assertRaises(ErrorDeEntrada):                 # tipo de carga desconocido
            modelo3d([(1, 0, 0, 0), (2, 1000, 0, 0)], [(1, 1, 2)], [(1, FIJO)],
                     "CARGAS EN BARRAS\ncaso;barra;tipo;valor;valor2;a\nC;1;qq;1;;")

    def test_desplazamiento_prefijado_y_resorte(self):
        L = 1000.0
        m = modelo3d([(1, 0, 0, 0), (2, L, 0, 0)], [(1, 1, 2)], [(1, FIJO), (2, "0;0;1;0;0;0".split(";"))],
                     "DESPLAZAMIENTOS PREFIJADOS\ncaso;nodo;ux;uy;uz;phix;phiy;phiz\nA;2;0;0;-2;0;0;0")
        r = resolver(m)[0]["A"]
        # barra empotrada-guiada (uz impuesto, giro libre): R = 3EI·δ/L³ ; M = 3EI δ/L² en la raíz
        self.assertAlmostEqual(r.R[1, 2], -3 * E_ * IY * 2 / L**3, places=6)
        self.assertLess(equilibrio(m, r)["rel"], 1e-12)


class TestComandoYDespachador(unittest.TestCase):
    def test_detectar_tipo(self):
        from struttura import despachador
        for f in (RAIZ / "003_Ejemplos" / "004_Portico_espacial").glob("*.csv"):
            self.assertEqual(despachador.detectar_tipo(f), "portico3d")

    def test_comando_struttura_ejemplos_3d(self):
        for f in sorted((RAIZ / "003_Ejemplos" / "004_Portico_espacial").glob("*.csv")):
            out = Path(tempfile.mkdtemp())
            p = subprocess.run([sys.executable, str(RAIZ / "struttura.py"), str(f), "-o", str(out)], capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn("Pórtico espacial", p.stdout)
            self.assertTrue((out / "informe.html").is_file())
            self.assertGreater((out / "informe.html").stat().st_size, 20000)
            for nombre in ("desplazamientos.csv", "reacciones.csv", "esfuerzos.csv", "tensiones.csv"):
                self.assertTrue((out / nombre).is_file())

    def test_solo_esquema(self):
        f = RAIZ / "003_Ejemplos" / "004_Portico_espacial" / "ejemplo2_portico_espacial.csv"
        out = Path(tempfile.mkdtemp())
        p = subprocess.run([sys.executable, str(RAIZ / "struttura.py"), str(f), "--solo-esquema", "-o", str(out)],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertTrue((out / "esquema.html").is_file())


class TestTensorDeTensiones(unittest.TestCase):
    """Tensor de tensiones en puntos de la sección y criterios de falla."""

    @staticmethod
    def _sec(tipo, **d):
        from struttura.portico3d.entrada import _leer_secciones  # noqa: F401
        from struttura.emparrillado.entrada import _partir_bloques
        cols = ["id", "tipo"] + list(d)
        txt = "SECCIONES\n" + ";".join(cols) + "\n" + ";".join(["s", tipo] + [str(v) for v in d.values()]) + "\n"
        f = escribir(txt)
        from struttura.portico3d.entrada import TITULOS
        return _leer_secciones(_partir_bloques(f, TITULOS))["s"]

    @staticmethod
    def _malla(sec, n=500):
        """Puntos y áreas elementales de la sección (para integrar tensiones)."""
        if sec.tipo in ("tubo", "circular"):
            R = sec.dim["d"] / 2
            ri = R - sec.dim["t"] if sec.tipo == "tubo" else 0.0
            rs = ri + (np.arange(400) + 0.5) * (R - ri) / 400
            ph = (np.arange(720) + 0.5) * 2 * np.pi / 720
            RR, PH = np.meshgrid(rs, ph, indexing="ij")
            dA = RR * (R - ri) / 400 * 2 * np.pi / 720
            return (RR * np.cos(PH)).ravel(), (RR * np.sin(PH)).ravel(), dA.ravel()
        b, h = sec.dim["b"], sec.dim["h"]
        ys = -b / 2 + (np.arange(n) + 0.5) * b / n
        zs = -h / 2 + (np.arange(n) + 0.5) * h / n
        Y, Z = np.meshgrid(ys, zs, indexing="ij")
        dA = np.full(Y.shape, (b / n) * (h / n))
        if sec.tipo == "rect_hueca":
            t = sec.dim["t"]
            dA = np.where((np.abs(Y) < b / 2 - t) & (np.abs(Z) < h / 2 - t), 0.0, dA)
        return Y.ravel(), Z.ravel(), dA.ravel()

    def test_uniaxial_y_principales_contra_numpy(self):
        from struttura.portico3d import tensor as tn
        rng = np.random.default_rng(7)
        m = SimpleNamespace(fy=250.0, sut=None, suc=None, sadm=None, teoria="vm")
        for _ in range(20):
            sx, txy, txz = rng.normal(size=3) * 100
            c = tn.criterios(np.array([sx]), np.array([txy]), np.array([txz]), m)
            w = np.sort(np.linalg.eigvalsh(tn.matriz(sx, txy, txz)))[::-1]
            np.testing.assert_allclose([c["s1"][0], c["s2"][0], c["s3"][0]], w, atol=1e-9)
            vm = math.sqrt(0.5 * ((w[0] - w[1]) ** 2 + (w[1] - w[2]) ** 2 + (w[2] - w[0]) ** 2))
            self.assertAlmostEqual(c["vm"][0], vm, places=9)
            self.assertAlmostEqual(c["tresca"][0], w[0] - w[2], places=9)
        c = tn.criterios(np.array([120.0]), np.array([0.0]), np.array([0.0]), m)
        self.assertAlmostEqual(c["vm"][0], 120.0)
        self.assertAlmostEqual(c["tresca"][0], 120.0)
        self.assertAlmostEqual(c["cs"]["vm"][0], 250 / 120)

    def test_torsion_pura_tubo(self):
        from struttura.portico3d import tensor as tn
        s = self._sec("tubo", d=60, t=4)
        Ts = 100000.0
        sx, txy, txz = tn.campos(s, np.array([[0, 0, 0, Ts, 0, 0]]), [30.0], [0.0])
        self.assertAlmostEqual(txz[0, 0], Ts * 30 / s.J, places=9)
        self.assertAlmostEqual(txy[0, 0], 0.0, places=12)
        m = SimpleNamespace(fy=250.0, sut=None, suc=None, sadm=None, teoria="vm")
        c = tn.criterios(sx, txy, txz, m)
        tau = Ts * 30 / s.J
        self.assertAlmostEqual(c["s1"][0, 0], tau, places=9)
        self.assertAlmostEqual(c["s3"][0, 0], -tau, places=9)
        self.assertAlmostEqual(c["vm"][0, 0], math.sqrt(3) * tau, places=9)
        self.assertAlmostEqual(c["tresca"][0, 0], 2 * tau, places=9)
        self.assertAlmostEqual(tn.angulo_s1(sx[0, 0], txy[0, 0], txz[0, 0]), 45.0, places=9)

    def test_mohr_y_rankine(self):
        from struttura.portico3d import tensor as tn
        m = SimpleNamespace(fy=None, sut=200.0, suc=800.0, sadm=None, teoria="mohr")
        # σx = 100 y τ tal que σ1 = 100 + …: se fijan σ1 y σ3 con sx y tau: sx = σ1 + σ3, tau² = -σ1·σ3
        s1, s3 = 100.0, -200.0
        sx, tau = s1 + s3, math.sqrt(-s1 * s3)
        c = tn.criterios(np.array([sx]), np.array([tau]), np.array([0.0]), m)
        self.assertAlmostEqual(c["s1"][0], s1, places=9)
        self.assertAlmostEqual(c["s3"][0], s3, places=9)
        self.assertAlmostEqual(c["cs"]["mohr"][0], 1 / (100 / 200 + 200 / 800), places=9)
        self.assertAlmostEqual(c["cs"]["rankine"][0], min(200 / 100, 800 / 200), places=9)
        self.assertAlmostEqual(c["cs_gob"][0], c["cs"]["mohr"][0])

    def test_el_corte_y_la_torsion_equilibran_los_esfuerzos(self):
        """∫τxz dA = Vz, ∫τxy dA = Vy y ∫(y·τxz − z·τxy) dA = T en todas las secciones con fórmula."""
        from struttura.portico3d import tensor as tn
        casos = [("circular", dict(d=50), 0.01, 0.01), ("tubo", dict(d=60, t=4), 0.01, 0.01),
                 ("rectangular", dict(b=40, h=80), 0.01, 0.06), ("rect_hueca", dict(b=60, h=100, t=6), 0.11, 0.05)]
        for tipo, d, tolV, tolT in casos:
            s = self._sec(tipo, **d)
            Y, Z, dA = self._malla(s)
            E = np.array([[0, 300.0, 500.0, 7000.0, 0, 0]])
            _, txy, txz = tn.campos(s, E, Y, Z, corte=True)
            if tipo == "rectangular":                       # la torsión de la sección maciza es conservadora (no equilibra exacto)
                _, ty0, tz0 = tn.campos(s, np.array([[0, 300.0, 500.0, 0, 0, 0]]), Y, Z, corte=True)
                txy, txz = ty0, tz0
            self.assertAlmostEqual((txz[0] * dA).sum() / 500.0, 1.0, delta=tolV, msg=tipo)
            self.assertAlmostEqual((txy[0] * dA).sum() / 300.0, 1.0, delta=tolV, msg=tipo)
            if tipo != "rectangular":
                E = np.array([[0, 0, 0, 7000.0, 0, 0]])
                _, txy, txz = tn.campos(s, E, Y, Z, corte=False)
                self.assertAlmostEqual(((Y * txz[0] - Z * txy[0]) * dA).sum() / 7000.0, 1.0, delta=tolT, msg=tipo)

    def test_sin_corte_de_flexion(self):
        from struttura.portico3d import tensor as tn
        s = self._sec("tubo", d=60, t=4)
        E = np.array([[0, 100.0, 200.0, 0, 0, 0]])
        _, txy, txz = tn.campos(s, E, [30.0, 0.0], [0.0, 30.0], corte=False)
        self.assertEqual(float(np.abs(txy).max() + np.abs(txz).max()), 0.0)
        _, txy, txz = tn.campos(s, E, [30.0, 0.0], [0.0, 30.0], corte=True)
        self.assertGreater(float(np.abs(txy).max() + np.abs(txz).max()), 0.0)

    def test_voladizo_tubo_contra_formulas(self):
        from struttura.portico3d.tensor import analizar
        d, t, L, P = 60.0, 4.0, 1000.0, 2000.0
        m = modelo3d([(1, 0, 0, 0), (2, L, 0, 0)], [(1, 1, 2)], [(1, FIJO)], "CARGAS\ncaso;nodo;Fx;Fy;Fz;Mx;My;Mz\nC;2;0;0;-2000;0;0;0",
                     sec="s;tubo;60;4", sec_cab="id;tipo;d;t")
        r = resolver(m)[0]["C"]
        an = analizar(m, r)
        I = math.pi / 64 * (d**4 - (d - 2 * t) ** 4)
        top = an["criticos"][0]
        self.assertAlmostEqual(top["sx"], P * L * (d / 2) / I, delta=P * L * (d / 2) / I * 1e-6)     # σ = M c / I en el borde
        self.assertEqual(top["x"], 0.0)
        # punto pedido en el eje neutro del empotramiento: τ = V/(π Rm t) por corte
        m.puntos.append({"id": "EN", "barra": 0, "x": 0.0, "y": d / 2, "z": 0.0, "caso": None})
        an = analizar(m, r)
        u = an["usuario"][0]
        Rm = (d - t) / 2
        self.assertAlmostEqual(abs(u["txz"]), P / (math.pi * Rm * t), places=6)
        self.assertAlmostEqual(u["sx"], 0.0, places=6)

    def test_invariancia_de_VM_ante_rotacion_rigida(self):
        from struttura.portico3d.tensor import analizar
        rng = np.random.default_rng(11)
        Q, _ = np.linalg.qr(rng.normal(size=(3, 3)))
        if np.linalg.det(Q) < 0:
            Q[:, 0] *= -1
        nod = [(1, 0, 0, 0), (2, 1500, 300, 800), (3, 2500, 1200, 200)]
        F = np.array([1000.0, -500.0, 800.0])
        out = []
        for Qm in (np.eye(3), Q):
            nn = [(n[0], *(Qm @ np.array(n[1:]))) for n in nod]
            c = "CARGAS\ncaso;nodo;Fx;Fy;Fz;Mx;My;Mz\nC;3;" + ";".join(repr(float(v)) for v in (*(Qm @ F), 0, 0, 0))
            m = modelo3d(nn, [(1, 1, 2), (2, 2, 3)], [(1, FIJO)], c, sec="s;tubo;76.1;4", sec_cab="id;tipo;d;t")
            out.append(analizar(m, resolver(m)[0]["C"])["criticos"][0]["vm"])
        self.assertAlmostEqual(out[1] / out[0], 1.0, delta=0.012)          # muestreo cada 15° del perímetro

    def test_bloque_puntos_y_errores(self):
        base = "CARGAS\ncaso;nodo;Fx;Fy;Fz;Mx;My;Mz\nC;2;0;0;-100;0;0;0\nD;2;0;100;0;0;0;0\n\n"
        m = modelo3d([(1, 0, 0, 0), (2, 1000, 0, 0)], [(1, 1, 2)], [(1, FIJO)],
                     base + "PUNTOS DE TENSION\nid;barra;x;y;z;caso\nA;1;0;0;30;C\nB;1;500;10;-20;",
                     sec="s;tubo;60;4", sec_cab="id;tipo;d;t")
        self.assertEqual([p["id"] for p in m.puntos], ["A", "B"])
        from struttura.portico3d.tensor import analizar
        res = resolver(m)[0]
        self.assertEqual([u["id"] for u in analizar(m, res["C"])["usuario"]], ["A", "B"])
        self.assertEqual([u["id"] for u in analizar(m, res["D"])["usuario"]], ["B"])              # A solo en el caso C
        with self.assertRaises(ErrorDeEntrada):
            modelo3d([(1, 0, 0, 0), (2, 1000, 0, 0)], [(1, 1, 2)], [(1, FIJO)], base + "PUNTOS DE TENSION\nid;barra;x;y;z\nA;1;1500;0;0")
        with self.assertRaises(ErrorDeEntrada):
            modelo3d([(1, 0, 0, 0), (2, 1000, 0, 0)], [(1, 1, 2)], [(1, FIJO)], base + "PUNTOS DE TENSION\nid;barra;x;y;z\nA;9;10;0;0")

    def test_materiales_teoria(self):
        def cm(mat):
            t = ("PROYECTO\ntipo;portico3d\nNODOS\nid;x;y;z\n1;0;0;0\n2;1;0;0\nMATERIALES\n" + mat +
                 "\nSECCIONES\nid;tipo;A;Iy;Iz;J\ns;generica;1;1;1;1\nBARRAS\nid;nodo_i;nodo_j;material;seccion\n1;1;2;m;s\n"
                 "APOYOS\nnodo;ux;uy;uz;phix;phiy;phiz\n1;1;1;1;1;1;1\nCARGAS\ncaso;nodo;Fx;Fy;Fz;Mx;My;Mz\nC;2;1;0;0;0;0;0\n")
            return cargar_modelo(escribir(t))
        self.assertEqual(cm("id;E;G;fy\nm;1;1;200").materiales["m"].teoria, "vm")
        self.assertEqual(cm("id;E;G;sut\nm;1;1;200").materiales["m"].teoria, "rankine")
        self.assertEqual(cm("id;E;G;fy;teoria\nm;1;1;200;tresca").materiales["m"].teoria, "tresca")
        m = cm("id;E;G;sut;suc;teoria\nm;1;1;200;600;mohr").materiales["m"]
        self.assertEqual((m.teoria, m.sut, m.suc), ("mohr", 200.0, 600.0))
        with self.assertRaises(ErrorDeEntrada):
            cm("id;E;G;fy;teoria\nm;1;1;200;rankine")            # rankine sin sut
        with self.assertRaises(ErrorDeEntrada):
            cm("id;E;G;fy;teoria\nm;1;1;200;inventada")

    def test_ejemplos_generan_tensores_csv(self):
        f = RAIZ / "003_Ejemplos" / "004_Portico_espacial" / "ejemplo3_mensula_fundicion_mohr.csv"
        out = Path(tempfile.mkdtemp())
        p = subprocess.run([sys.executable, str(RAIZ / "struttura.py"), str(f), "-o", str(out)], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        h = (out / "informe.html").read_text(encoding="utf-8")
        for txt in ("Puntos pedidos", "Mohr modificado", "gobernante", "raiz_ala_sup"):
            self.assertIn(txt, h)
        self.assertTrue((out / "tensores.csv").is_file())
        self.assertGreater(len((out / "tensores.csv").read_text(encoding="utf-8-sig").splitlines()), 4)


class TestMatricesEnLosInformes(unittest.TestCase):
    """Todos los informes incluyen la matriz de rigidez ensamblada (sin límite de tamaño)."""

    def test_los_cuatro_informes_traen_la_matriz_ensamblada(self):
        for carpeta, minimo in (("001_Emparrillado", "ejemplo2_parrilla.csv"), ("002_Portico", "ejemplo3_resortes_asentamiento.csv"),
                                ("003_Reticulado", "ejemplo5_cercha_con_pandeo.csv"), ("004_Portico_espacial", "ejemplo2_portico_espacial.csv")):
            f = RAIZ / "003_Ejemplos" / carpeta / minimo
            out = Path(tempfile.mkdtemp())
            p = subprocess.run([sys.executable, str(RAIZ / "struttura.py"), str(f), "-o", str(out)], capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            h = (out / "informe.html").read_text(encoding="utf-8")
            self.assertIn("Anexo A", h, carpeta)
            self.assertIn("ensamblada", h, carpeta)
            self.assertNotIn("se omite por tamaño", h, carpeta)

    def test_anexo_se_puede_apagar(self):
        t = (RAIZ / "003_Ejemplos" / "004_Portico_espacial" / "ejemplo1_voladizo_en_L.csv").read_text(encoding="utf-8")
        t = t.replace("tipo;portico3d", "tipo;portico3d\nanexo_matrices;no")
        f = escribir(t)
        out = Path(tempfile.mkdtemp())
        subprocess.run([sys.executable, str(RAIZ / "struttura.py"), str(f), "-o", str(out)], capture_output=True, text=True, check=True)
        self.assertNotIn("Anexo A", (out / "informe.html").read_text(encoding="utf-8"))




class TestVisorEstandar(unittest.TestCase):
    """Los 4 visores comparten el estándar de navegación y de modos (visor_comun.py)."""

    def test_modulo_comun_y_modos(self):
        from struttura import visor_comun
        from struttura.emparrillado import visor3d
        from struttura.portico import visor2d
        from struttura.portico3d import visor
        for js in (visor.JS, visor3d.LIB_JS, visor2d.LIB_JS):
            self.assertIn("function stNav", js)
            self.assertIn("stZoomEn", js)
        self.assertIn("Estructura", visor.JS)
        self.assertIn("Estructura", visor3d.LIB_JS)
        self.assertIn("Estructura", visor2d.LIB_JS)
        self.assertIn("Barra:", visor.JS)
        self.assertIn("Barra:", visor2d.LIB_JS)
        self.assertIn("Ctrl", visor_comun.AYUDA_3D)
        self.assertIn("Shift", visor_comun.AYUDA_2D)
        for css in (visor.CSS, visor3d.CSS, visor2d.CSS):
            self.assertIn(".ayuda", css)

    def test_informe_3d_incluye_ayuda(self):
        import os
        import subprocess
        import sys
        import tempfile
        raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv = os.path.join(raiz, "003_Ejemplos", "004_Portico_espacial", "ejemplo2_portico_espacial.csv")
        with tempfile.TemporaryDirectory() as d:
            import shutil
            dst = os.path.join(d, "x.csv")
            shutil.copy(csv, dst)
            r = subprocess.run([sys.executable, os.path.join(raiz, "struttura.py"), dst], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            html = open(os.path.join(d, "x_salida", "informe.html"), encoding="utf-8").read()
            self.assertIn("Ctrl + arrastrar", html)


class TestVisorApoyos(unittest.TestCase):
    """Apoyos como nudos de color + recuadro de condiciones de borde (estándar de los 4 visores)."""

    def test_codigo_comun(self):
        from struttura import visor_comun
        from struttura.emparrillado import visor3d
        from struttura.portico import visor2d
        from struttura.portico3d import visor
        for js in (visor.JS, visor3d.LIB_JS, visor2d.LIB_JS):
            self.assertIn("function stTip", js)
            self.assertIn("stTexto(", js)
            self.assertIn("#0b7a6b", js)
        self.assertNotIn("polygon", visor.JS.split("// nodos y apoyos")[1].split("// cargas")[0])
        self.assertIn("condiciones de borde", visor_comun.AYUDA_3D)
        self.assertIn("condiciones de borde", visor_comun.AYUDA_2D)


# --------------------------------------------------------------------------
# U0 (v1.1.6): articulaciones, peso propio, columnas ignoradas, Mohr / Mohr modificado
# --------------------------------------------------------------------------
class TestArticulaciones(unittest.TestCase):
    def test_voladizo_apoyado_viga_empotrada_articulada(self):
        """Empotrada en i, articulada en j con apoyo simple: R_j = 3qL/8, M_emp = qL²/8, M_j = 0."""
        L, q = 1000.0, 10.0
        m = modelo3d([(1, 0, 0, 0), (2, L, 0, 0)], [("b", 1, 2, ";1")], [(1, "111111"), (2, "111000")],
                     cargas=f"CARGAS EN BARRAS\ncaso;barra;tipo;valor\nC;b;qgz;{-q}\n", barcols=";art_i;art_j")
        res, _ = resolver(m)
        r = res["C"]
        self.assertAlmostEqual(r.R[1][2], 3 * q * L / 8, delta=1e-6 * q * L)
        self.assertAlmostEqual(abs(r.R[0][4]), q * L**2 / 8, delta=1e-6 * q * L**2)
        xs, E = diagramas(m, r, 0)
        self.assertAlmostEqual(E[-1][4], 0.0, delta=1e-6 * q * L**2)          # My = 0 en la articulación
        self.assertTrue(any("indeterminado" in a for a in m.avisos))          # el giro del nudo 2 queda libre
        self.assertLess(equilibrio(m, r)["rel"], 1e-10)

    def test_biarticulada_es_viga_simplemente_apoyada(self):
        L, q = 2000.0, 5.0
        m = modelo3d([(1, 0, 0, 0), (2, L, 0, 0)], [("b", 1, 2, "1;1")], [(1, "111100"), (2, "011100")],
                     cargas=f"CARGAS EN BARRAS\ncaso;barra;tipo;valor\nC;b;qgz;{-q}\n", barcols=";art_i;art_j")
        res, _ = resolver(m)
        xs, E = diagramas(m, res["C"], 0)
        self.assertAlmostEqual(abs(E[:, 4]).max(), q * L**2 / 8, delta=1e-4 * q * L**2)
        self.assertAlmostEqual(E[0][4], 0.0, delta=1e-6 * q * L**2)
        self.assertAlmostEqual(E[-1][4], 0.0, delta=1e-6 * q * L**2)
        self.assertAlmostEqual(res["C"].R[0][2], q * L / 2, delta=1e-6 * q * L)

    def test_letras_my_mz_t(self):
        from struttura.portico3d.barra import gdl_liberados, parsear_articulacion
        self.assertEqual(parsear_articulacion("1"), "yz")
        self.assertEqual(parsear_articulacion(""), "")
        self.assertEqual(parsear_articulacion("my+t"), "ty")
        self.assertEqual(gdl_liberados("yz", "t"), [4, 5, 9])
        with self.assertRaises(ValueError):
            parsear_articulacion("xyz")

    def test_torsion_liberada_en_ambos_extremos_es_mecanismo(self):
        with self.assertRaises(ErrorDeEntrada):
            modelo3d([(1, 0, 0, 0), (2, 1000, 0, 0)], [("b", 1, 2, "t;t")], [(1, "111111")], barcols=";art_i;art_j")

    def test_momento_en_nudo_totalmente_articulado_da_error(self):
        m = modelo3d([(1, 0, 0, 0), (2, 1000, 0, 0), (3, 2000, 0, 0)], [("a", 1, 2, ";1"), ("b", 2, 3, "1;")],
                     [(1, "111111"), (3, "111111")], cargas="CARGAS\ncaso;nodo;Fx;Fy;Fz;Mx;My;Mz\nC;2;0;0;0;0;100;0\n",
                     barcols=";art_i;art_j")
        with self.assertRaises(ErrorEstructura):
            resolver(m)

    def test_matriz_condensada_tiene_filas_nulas(self):
        m = modelo3d([(1, 0, 0, 0), (2, 1000, 0, 0)], [("b", 1, 2, ";my")], [(1, "111111")], barcols=";art_i;art_j",
                     cargas="CARGAS\ncaso;nodo;Fx;Fy;Fz;Mx;My;Mz\nC;2;1;0;0;0;0;0\n")
        k = m.barras[0].k_cond
        self.assertTrue(np.allclose(k[10], 0) and np.allclose(k[:, 10], 0))
        self.assertTrue(np.allclose(k, k.T))


class TestPesoPropioYColumnas(unittest.TestCase):
    CSV = ("PROYECTO\ntipo;portico3d\nunidad_fuerza;N\nunidad_longitud;mm\n{extra}\nNODOS\nid;x;y;z\n1;0;0;0\n2;1000;0;0\n"
           "MATERIALES\nid;E;G;fy{matcol}\nm;210000;80000;235{matval}\nSECCIONES\nid;tipo;d;t\ns;tubo;50;3\n"
           "BARRAS\nid;nodo_i;nodo_j;material;seccion\nb;1;2;m;s\nAPOYOS\nnodo;ux;uy;uz;phix;phiy;phiz\n1;1;1;1;1;1;1\n"
           "CARGAS\ncaso;nodo;Fx;Fy;Fz;Mx;My;Mz\nC;2;1;0;0;0;0;0\n")

    def test_peso_propio_voladizo(self):
        m = cargar_modelo(escribir(self.CSV.format(extra="peso_propio;PP", matcol=";rho", matval=";7850")))
        res, _ = resolver(m)
        A = math.pi / 4 * (50**2 - 44**2)
        W = 7850 * 9.80665 * 1e-9 * A * 1000.0                  # N
        self.assertAlmostEqual(res["PP"].R[0][2], W, delta=1e-9 * W)
        self.assertAlmostEqual(abs(res["PP"].R[0][4]), W * 500.0, delta=1e-9 * W * 500)
        self.assertAlmostEqual(m.peso_propio["masa"], 7850 * A * 1000 * 1e-9, delta=1e-9)
        self.assertLess(equilibrio(m, res["PP"])["rel"], 1e-12)

    def test_gravedad_en_otro_eje(self):
        m = cargar_modelo(escribir(self.CSV.format(extra="peso_propio;PP\ngravedad;+y", matcol=";rho", matval=";7850")))
        res, _ = resolver(m)
        self.assertGreater(abs(res["PP"].R[0][1]), 0)
        self.assertAlmostEqual(res["PP"].R[0][2], 0.0, delta=1e-9)

    def test_peso_propio_sin_rho_da_error(self):
        with self.assertRaises(ErrorDeEntrada):
            cargar_modelo(escribir(self.CSV.format(extra="peso_propio;PP", matcol="", matval="")))

    def test_sin_peso_propio_no_agrega_carga(self):
        m = cargar_modelo(escribir(self.CSV.format(extra="", matcol=";rho", matval=";7850")))
        self.assertIsNone(m.peso_propio)
        self.assertFalse(any("rho" in a for a in m.avisos))      # rho es columna válida

    def test_columna_desconocida_avisa(self):
        m = cargar_modelo(escribir(self.CSV.format(extra="", matcol=";color", matval=";rojo")))
        self.assertTrue(any("'color'" in a and "MATERIALES" in a for a in m.avisos))


class TestMohr(unittest.TestCase):
    def _cs(self, sx, tau, teoria):
        from struttura.portico3d.tensor import criterios
        mat = SimpleNamespace(fy=None, sut=200.0, suc=800.0, sadm=None, teoria=teoria)
        c = criterios(np.array([sx]), np.array([tau]), np.array([0.0]), mat)
        return c

    def test_corte_puro(self):
        # σ1 = 100, σ3 = -100, α = 0,25:  Mohr σ* = 125 (CS 1,6);  Mohr modificado σ* = 100 (CS 2)
        c = self._cs(0.0, 100.0, "mohr")
        self.assertAlmostEqual(c["mohr"][0], 125.0, places=9)
        self.assertAlmostEqual(c["cs"]["mohr"][0], 1.6, places=9)
        self.assertAlmostEqual(c["mohrmod"][0], 100.0, places=9)
        self.assertAlmostEqual(c["cs"]["mohrmod"][0], 2.0, places=9)

    def test_traccion_y_compresion_uniaxial(self):
        c = self._cs(100.0, 0.0, "mohr")
        self.assertAlmostEqual(c["mohr"][0], 100.0)
        self.assertAlmostEqual(c["mohrmod"][0], 100.0)
        c = self._cs(-200.0, 0.0, "mohrmod")
        self.assertAlmostEqual(c["cs"]["mohr"][0], 4.0)          # suc / |σ3| = 800/200
        self.assertAlmostEqual(c["cs"]["mohrmod"][0], 4.0)

    def test_rama_abs_s3_mayor_que_s1(self):
        c = self._cs(-100.0, 100.0, "mohrmod")
        s1, s3 = (-100 + math.hypot(100, 200)) / 2, (-100 - math.hypot(100, 200)) / 2
        self.assertAlmostEqual(c["mohrmod"][0], 0.25 * abs(s3) + 0.75 * s1, places=9)
        self.assertAlmostEqual(c["eq_gob"][0], c["mohrmod"][0])         # σeq gobernante = σ* de Mohr modificado

    def test_mohr_modificado_nunca_mas_conservador_que_mohr(self):
        for sx, t in ((0, 100), (100, 200), (-100, 100), (50, 10), (-300, 40)):
            c = self._cs(float(sx), float(t), "mohr")
            self.assertLessEqual(c["mohrmod"][0], c["mohr"][0] + 1e-12)

    def test_alias_en_la_entrada(self):
        t = ("PROYECTO\ntipo;portico3d\nNODOS\nid;x;y;z\n1;0;0;0\n2;1;0;0\nMATERIALES\nid;E;G;sut;suc;teoria\nm;1;1;200;800;Mohr modificado\n"
             "SECCIONES\nid;tipo;A;Iy;Iz;J\ns;generica;1;1;1;1\nBARRAS\nid;nodo_i;nodo_j;material;seccion\n1;1;2;m;s\n"
             "APOYOS\nnodo;ux;uy;uz;phix;phiy;phiz\n1;1;1;1;1;1;1\nCARGAS\ncaso;nodo;Fx;Fy;Fz;Mx;My;Mz\nC;2;1;0;0;0;0;0\n")
        self.assertEqual(cargar_modelo(escribir(t)).materiales["m"].teoria, "mohrmod")


class TestEjemplo5Articulaciones(unittest.TestCase):
    def test_ejemplo5_estatica_y_articulaciones(self):
        from struttura.portico3d.esfuerzos import esfuerzos_extremos
        m = cargar_modelo(RAIZ / "003_Ejemplos" / "004_Portico_espacial" / "ejemplo5_articulaciones_y_peso_propio.csv")
        res, _ = resolver(m)
        r = res["SERVICIO"]
        ex = esfuerzos_extremos(m, r)
        idx = {b.id: k for k, b in enumerate(m.barras)}
        esc = abs(ex[idx["col2"]]["i"][4])
        self.assertAlmostEqual(ex[idx["viga"]]["i"][4], 0.0, delta=1e-9 * esc)          # viga articulada en la columna
        for extremo in ("i", "j"):                                                         # tensor biarticulado: solo axil
            self.assertAlmostEqual(ex[idx["tensor"]][extremo][4], 0.0, delta=1e-9 * esc)
            self.assertAlmostEqual(ex[idx["tensor"]][extremo][5], 0.0, delta=1e-9 * esc)
        # equilibrio vertical del tensor: componente vertical de N = 2000 + peso de lo que cuelga (≈ P + peso viga/2 + tensor/2)
        N = ex[idx["tensor"]]["j"][0]
        P = 2000.0
        self.assertGreater(N * math.sin(math.atan2(1500, 1500)), P)
        self.assertLess(equilibrio(m, r)["rel"], 1e-10)


# ---------------------------------------------------------------------------
class TestParedDelgada(unittest.TestCase):
    """Perfiles abiertos de pared delgada: propiedades, centro de corte, Jourawski y torsión (Gere 7ª §6.7–6.9; Compendio cap. 10)."""

    @staticmethod
    def _pd(tipo, **p):
        from struttura.portico3d.pared_delgada import ParedDelgada, perfil
        return ParedDelgada(perfil(tipo, p))

    def test_canal_gere_6_62_6_65_y_compendio(self):
        h, b, t = 200.0, 100.0, 5.0
        s = self._pd("canal", h=h, b=b, t=t)
        self.assertAlmostEqual(s.A, 2000.0, 9)
        self.assertAlmostEqual(s.Iy, t * h**3 / 12 + b * h**2 * t / 2, 3)                 # (6-62)
        e = 3 * b**2 * t / (h * t + 6 * b * t)                                           # (6-65) = 37,5
        self.assertAlmostEqual(e, 37.5, 9)
        yc = 2 * b * t * (b / 2) / s.A                                                   # baricentro desde el alma
        self.assertAlmostEqual(s.ys, -(yc + e), 2)
        self.assertAlmostEqual(s.zs, 0.0, 6)
        self.assertAlmostEqual(s.J, 16666.6667, 3)                                       # Σ l t³/3 (Compendio cap. 10)

    def test_resultante_del_flujo_es_V(self):
        for tipo in ("canal", "doble_t", "te", "z", "angular"):
            s = self._pd(tipo, h=200.0, b=100.0, t=5.0)
            self.assertAlmostEqual(s.chequeo_resultante[0], 1.0, 2, tipo)
            self.assertAlmostEqual(s.chequeo_resultante[1], 1.0, 2, tipo)

    def test_centros_de_corte_particulares(self):
        for tipo in ("doble_t", "z"):                                                    # en el baricentro
            s = self._pd(tipo, h=200.0, b=100.0, t=5.0)
            self.assertAlmostEqual(s.ys, 0.0, 5)
            self.assertAlmostEqual(s.zs, 0.0, 5)
        te = self._pd("te", h=200.0, b=100.0, t=5.0)                                     # en la unión: zc = −66,67 → zs = +66,67
        self.assertAlmostEqual(te.zs, 200 * 5 * 100 / 1500, 3)
        ang = self._pd("angular", h=100.0, b=100.0, t=5.0)                               # en la unión de las patas
        self.assertAlmostEqual(abs(ang.ys), 35.3553, 3)
        self.assertAlmostEqual(math.degrees(abs(ang.theta)), 45.0, 6)

    def test_jourawski_alma_del_canal(self):
        s = self._pd("canal", h=200.0, b=100.0, t=5.0)
        y = np.array([[-25.0]])
        z = np.array([[0.0]])
        Vz = np.array([[1000.0]])
        cero = np.array([[0.0]])
        _, tz = s.tensiones(y, z, cero, Vz, Vz * s.ys)                                   # T tal que T_SV = 0
        Q = 100 * 5 * 100 + 5 * 100 * 50
        self.assertAlmostEqual(abs(float(tz[0, 0])), 1000 * Q / (s.Iy * 5), 3)           # V·Q/(I·t) = 1,125

    def test_voladizo_de_canal_ejemplo6(self):
        from struttura.portico3d.tensor import analizar
        m = cargar_modelo(str(Path(__file__).resolve().parents[1] / "003_Ejemplos/004_Portico_espacial/ejemplo6_perfiles_pared_delgada.csv"))
        res = list(resolver(m)[0].values())[0]
        an = analizar(m, res)
        p = {u["id"]: u for u in an["usuario"]}["alma_media"]
        # corte 1,125 MPa + torsión |T_SV|·t/J con T_SV = 0 − (ys·Vz) = 62,5·1000 N·mm → 18,75 MPa
        self.assertAlmostEqual(math.hypot(p["txy"], p["txz"]), 1.125 + 62500 * 5 / 16666.6667, 2)
        self.assertAlmostEqual(abs(p["sx"]), 0.0, 6)                                     # en el eje neutro de My
        punta = {u["id"]: u for u in an["usuario"]}["ala_punta"]
        self.assertAlmostEqual(punta["sx"], 1e6 * 100 / 13333333.333, 3)                 # M·z/Iy = 7,5 MPa
        self.assertAlmostEqual(math.hypot(punta["txy"], punta["txz"]), 18.75, 2)         # solo torsión (corte nulo en la punta)

    def test_contra_sectionproperties_si_esta_instalada(self):
        try:
            from sectionproperties.analysis import Section
            from sectionproperties.pre.library import channel_section
        except Exception:
            self.skipTest("sectionproperties no está instalada (validación opcional)")
        g = channel_section(d=205, b=102.5, t_f=5, t_w=5, r=0, n_r=1)                    # dimensiones exteriores equivalentes
        g.create_mesh([2.0])
        sec = Section(g)
        sec.calculate_geometric_properties()
        sec.calculate_warping_properties()
        s = self._pd("canal", h=200.0, b=100.0, t=5.0)
        self.assertAlmostEqual(s.A / sec.get_area(), 1.0, 2)
        self.assertAlmostEqual(s.Iy / sec.get_ic()[0], 1.0, 2)
        self.assertAlmostEqual(s.J / sec.get_j(), 1.0, 2)
        xsc = sec.get_sc()[0]                                                            # desde la cara exterior del alma
        self.assertAlmostEqual((xsc - sec.get_c()[0]), s.ys, delta=0.3)

    def test_perfil_mal_definido(self):
        from struttura.portico3d.pared_delgada import perfil
        with self.assertRaises(ValueError):
            perfil("canal", {"h": 100, "b": 50})


if __name__ == "__main__":
    unittest.main()


class TestResorteInclinado3D(unittest.TestCase):
    """RESORTES INCLINADOS (3D): k·d·dᵀ; la dirección se da con vector o con ángulos a los ejes."""

    BASE = os.path.join(os.path.dirname(__file__), "..", "003_Ejemplos", "004_Portico_espacial", "ejemplo1_voladizo_en_L.csv")

    def _correr(self, extra):
        import tempfile
        from struttura.portico3d.entrada import cargar_modelo
        from struttura.portico3d.solver import resolver
        with tempfile.TemporaryDirectory() as d:
            f = os.path.join(d, "m.csv")
            with open(f, "w", encoding="utf-8") as h:
                h.write(open(self.BASE, encoding="utf-8").read() + "\n" + extra + "\n")
            m = cargar_modelo(f)
        return m, resolver(m)[0]["P"]

    def test_equivale_al_resorte_en_z_y_al_proyectado(self):
        _, r0 = self._correr("RESORTES\nnodo;kz\n3;50")
        for extra in ("RESORTES INCLINADOS\nnodo;k;dx;dy;dz\n3;50;0;0;-7",
                      "RESORTES INCLINADOS\nnodo;k;ax;ay;az\n3;50;90;90;0",
                      "RESORTES INCLINADOS\nnodo;k;ax;ay;az\n3;50;90;90;"):
            _, r = self._correr(extra)
            self.assertLess(abs(r.u - r0.u).max(), 1e-12)
        m, r = self._correr("RESORTES INCLINADOS\nnodo;k;dx;dy;dz\n3;50;1;1;1")
        d = np.ones(3) / np.sqrt(3)
        self.assertTrue(np.allclose(r.Rk[2, :3], -50 * d * (d @ r.u[2, :3])))

    def test_errores_de_direccion(self):
        from struttura.portico3d.entrada import ErrorDeEntrada
        for extra in ("RESORTES INCLINADOS\nnodo;k;ax;ay;az\n3;50;10;10;10",          # cos² no suma 1
                      "RESORTES INCLINADOS\nnodo;k;ax;ay;az\n3;50;10;;",              # un solo ángulo
                      "RESORTES INCLINADOS\nnodo;k;dx;dy;dz;ax\n3;50;1;0;0;90",       # vector y ángulos
                      "RESORTES INCLINADOS\nnodo;k;dx;dy;dz\n3;50;0;0;0"):            # vector nulo
            with self.assertRaises(ErrorDeEntrada, msg=extra):
                self._correr(extra)
