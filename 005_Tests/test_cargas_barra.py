"""Tests de las cargas en el tramo de las barras.  Ejecutar desde la raíz:
    python -m unittest discover -s tests -v
"""
import math
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "001_Codigo"))

from struttura.emparrillado.entrada import cargar_modelo, ErrorDeEntrada
from struttura.emparrillado.solver import resolver, equilibrio
from struttura.emparrillado.esfuerzos import esfuerzos, tensiones, elastica

RAIZ = Path(__file__).resolve().parents[1]
E_, I_, L_ = 210000.0, 1.0e6, 1000.0       # N/mm², mm⁴, mm


def modelo(cargas_barra, apoyos, nodos=None, barras=None, extra="", alfa="", h="", enc="utf-8"):
    """Viga de 1000 mm sobre X (nodos 1→2) por defecto.  Sección genérica I=1e6, J=2e6."""
    nodos = nodos or [(1, 0, 0), (2, L_, 0)]
    barras = barras or [(1, 1, 2)]
    t = ["NODOS", "id;x;y"] + [f"{a};{b};{c}" for a, b, c in nodos]
    t += ["", "MATERIALES", "id;E;G;alfa", f"M;{E_};80000;{alfa}"]
    t += ["", "SECCIONES", "id;tipo;I;J;c;h", f"S;generica;{I_};2000000;35;{h}"]
    t += ["", "BARRAS", "id;nodo_i;nodo_j;material;seccion"] + [f"{a};{b};{c};M;S" for a, b, c in barras]
    t += ["", "APOYOS", "nodo;uz;phix;phiy"] + [";".join(map(str, a)) for a in apoyos]
    t += ["", "CARGAS EN BARRAS", "caso;barra;tipo;valor;valor2;a;b"] + cargas_barra
    t += ["", extra]
    d = Path(tempfile.mkdtemp())
    r = d / "m.csv"
    r.write_bytes(("\n".join(t) + "\n").encode(enc))
    return cargar_modelo(r)


EMP = [(1, 1, 1, 1), (2, 1, 1, 1)]          # ambos nodos empotrados
VOL = [(1, 1, 1, 1)]                        # voladizo: nodo 1 empotrado


class TestBiempotrada(unittest.TestCase):
    def test_uniforme(self):
        q = -2.0
        m = modelo([f"C;1;q;{q};;;"], EMP)
        res, _ = resolver(m)
        r = res["C"]
        self.assertAlmostEqual(r.R[0, 0], -q * L_ / 2, places=6)
        self.assertAlmostEqual(r.R[1, 0], -q * L_ / 2, places=6)
        e = esfuerzos(m, r)
        self.assertAlmostEqual(e["Mi"][0], q * L_**2 / 12, places=4)         # hogging (<0) con q<0
        self.assertAlmostEqual(e["Mj"][0], q * L_**2 / 12, places=4)
        self.assertAlmostEqual(e["Mmax"][0], -q * L_**2 / 24, delta=abs(q) * L_**2 / 24 * 1e-6)
        self.assertAlmostEqual(e["xMmax"][0], L_ / 2, delta=L_ * 1e-3)
        self.assertAlmostEqual(e["V"][0], -q * L_ / 2, places=6)
        self.assertAlmostEqual(e["Vj"][0], q * L_ / 2, places=6)
        X, Y, W = elastica(m, r)[0]
        self.assertAlmostEqual(W[len(W) // 2], q * L_**4 / (384 * E_ * I_), delta=abs(q) * L_**4 / (384 * E_ * I_) * 1e-4)
        self.assertAlmostEqual(W[-1], 0.0, places=5)
        self.assertLess(equilibrio(m, r)["rel"], 1e-12)

    def test_puntual_al_medio(self):
        P = -1000.0
        m = modelo([f"C;1;P;{P};;{L_ / 2};"], EMP)
        r = resolver(m)[0]["C"]
        e = esfuerzos(m, r)
        self.assertAlmostEqual(r.R[0, 0], -P / 2, places=6)
        self.assertAlmostEqual(e["Mi"][0], P * L_ / 8, places=4)
        self.assertAlmostEqual(e["Mmax"][0], -P * L_ / 8, places=3)
        self.assertAlmostEqual(e["V"][0], -P / 2, places=6)
        self.assertAlmostEqual(e["Vj"][0], P / 2, places=6)
        W = elastica(m, r)[0][2]
        self.assertAlmostEqual(W[len(W) // 2], P * L_**3 / (192 * E_ * I_), delta=abs(P) * L_**3 / (192 * E_ * I_) * 1e-4)

    def test_puntual_excentrica(self):
        P, a = -500.0, 300.0
        m = modelo([f"C;1;P;{P};;{a};"], EMP)
        r = resolver(m)[0]["C"]
        b = L_ - a
        self.assertAlmostEqual(r.R[0, 0], -P * b**2 * (3 * a + b) / L_**3, places=6)     # reacción en i
        self.assertAlmostEqual(esfuerzos(m, r)["Mi"][0], P * a * b**2 / L_**2, places=4)  # empotramiento i

    def test_termico(self):
        alfa, h = 1.2e-5, 70.0
        m = modelo(["C;1;temp;40;0;;"], EMP, alfa=alfa, h=h)
        r = resolver(m)[0]["C"]
        MT = E_ * I_ * alfa * 40 / h
        e = esfuerzos(m, r)
        self.assertAlmostEqual(e["Mi"][0], MT, delta=abs(MT) * 1e-9)
        self.assertAlmostEqual(e["Mj"][0], MT, delta=abs(MT) * 1e-9)
        self.assertAlmostEqual(e["Mmax"][0], MT, delta=abs(MT) * 1e-9)
        self.assertLess(abs(e["V"][0]), 1e-6)
        self.assertLess(np.abs(r.u).max(), 1e-12)                  # empotrada: no se mueve
        W = elastica(m, r)[0][2]
        self.assertLess(np.abs(W).max(), 1e-12)                    # y la elástica queda recta

    def test_trapecial_parcial_conserva_resultante(self):
        q1, q2, a, b = -1.0, -3.0, 200.0, 700.0
        m = modelo([f"C;1;q;{q1};{q2};{a};{b}"], EMP)
        r = resolver(m)[0]["C"]
        Ftot = (q1 + q2) / 2 * (b - a)
        self.assertAlmostEqual(r.Feq[:, 0].sum(), Ftot, places=6)
        # momento respecto de i: My = -x·Fz  →  Fz_j·L - ΣMy debe dar F·xc (carga real)
        xc = a + (b - a) * (q1 + 2 * q2) / (3 * (q1 + q2))
        self.assertAlmostEqual(r.Feq[1, 0] * L_ - r.Feq[:, 2].sum(), Ftot * xc, delta=abs(Ftot * xc) * 1e-9)
        self.assertLess(equilibrio(m, r)["rel"], 1e-12)


class TestViga2Tramos(unittest.TestCase):
    def test_continua_carga_uniforme(self):
        """Viga continua de 2 tramos iguales con q uniforme: R_extremos = 3qL/8, R_medio = 10qL/8, M_medio = -qL²/8."""
        q = -1.0
        m = modelo(["C;1;q;-1;;;", "C;2;q;-1;;;"], [(1, 1, 1, 0), (2, 1, 1, 0), (3, 1, 1, 0)],
                   nodos=[(1, 0, 0), (2, L_, 0), (3, 2 * L_, 0)], barras=[(1, 1, 2), (2, 2, 3)])
        r = resolver(m)[0]["C"]
        self.assertAlmostEqual(r.R[0, 0], -q * 3 * L_ / 8, places=6)
        self.assertAlmostEqual(r.R[2, 0], -q * 3 * L_ / 8, places=6)
        self.assertAlmostEqual(r.R[1, 0], -q * 10 * L_ / 8, places=6)
        e = esfuerzos(m, r)
        self.assertAlmostEqual(e["Mj"][0], q * L_**2 / 8, places=4)          # hogging en el apoyo central
        self.assertAlmostEqual(e["Mi"][1], q * L_**2 / 8, places=4)
        self.assertAlmostEqual(e["Mmax"][0], -q * 9 * L_**2 / 128, delta=1e-3 * L_**2)   # 9qL²/128 en 3L/8
        self.assertAlmostEqual(e["xMmax"][0], 3 * L_ / 8, delta=L_ * 2e-3)
        self.assertLess(equilibrio(m, r)["rel"], 1e-12)


class TestResortesEspeciales(unittest.TestCase):
    """Resorte de giro con eje inclinado y desajuste (apoyo corrido) de resortes rectos."""

    def _voladizo(self, extra, carga="C;1;q;0;;;"):
        return modelo([carga], VOL, extra=extra)

    def test_giro_inclinado_a_0_y_90_grados_equivale_a_kphix_kphiy(self):
        k = 5.0e6
        cargas = "CARGAS\ncaso;nodo;Pz;Mx;My\nC;2;-100;3000000;2000000"
        ref = {}
        for nombre, bloque in (("x", f"RESORTES\nnodo;kz;kphix;kphiy\n2;;{k};"), ("y", f"RESORTES\nnodo;kz;kphix;kphiy\n2;;;{k}")):
            ref[nombre] = resolver(self._voladizo(cargas + "\n\n" + bloque))[0]["C"].u
        for nombre, ang in (("x", 0), ("y", 90)):
            bloque = f"RESORTES GIRO INCLINADO\nnodo;k;angulo\n2;{k};{ang}"
            u = resolver(self._voladizo(cargas + "\n\n" + bloque))[0]["C"].u
            np.testing.assert_allclose(u, ref[nombre], rtol=1e-9, atol=1e-15)

    def test_giro_inclinado_fuerza_paralela_al_eje(self):
        k, ang = 5.0e6, 45.0
        cargas = "CARGAS\ncaso;nodo;Pz;Mx;My\nC;2;-100;3000000;2000000"
        m = self._voladizo(cargas + f"\n\nRESORTES GIRO INCLINADO\nnodo;k;angulo\n2;{k};{ang}")
        r = resolver(m)[0]["C"]
        a = np.array([math.cos(math.radians(ang)), math.sin(math.radians(ang))])
        th = a @ r.u[1, 1:]
        np.testing.assert_allclose(r.Rk[1, 1:], -k * th * a, rtol=1e-9)
        self.assertLess(equilibrio(m, r)["rel"], 1e-12)

    def test_desajuste_equivale_a_carga_k_por_e(self):
        k, e = 5000.0, -5.0
        base = "RESORTES\nnodo;kz;kphix;kphiy\n2;5000;;"
        a = self._voladizo(base + "\n\nDESAJUSTE DE RESORTES\ncaso;nodo;uz;phix;phiy\nC;2;-5;;", carga="C;1;q;-1;;;")
        b = self._voladizo(base + "\n\nCARGAS\ncaso;nodo;Pz;Mx;My\nC;2;-25000;0;0", carga="C;1;q;-1;;;")
        ra, rb = resolver(a)[0]["C"], resolver(b)[0]["C"]
        np.testing.assert_allclose(ra.u, rb.u, rtol=1e-9, atol=1e-15)
        # la fuerza del resorte incluye la tensión inicial: -k(u - e)
        self.assertAlmostEqual(ra.Rk[1, 0], -k * (ra.u[1, 0] - e), places=6)
        self.assertLess(equilibrio(a, ra)["rel"], 1e-12)

    def test_desajuste_en_gdl_sin_resorte_es_error(self):
        with self.assertRaises(ErrorDeEntrada):
            self._voladizo("DESAJUSTE DE RESORTES\ncaso;nodo;uz;phix;phiy\nC;2;-5;;")


class TestVoladizo(unittest.TestCase):
    def test_uniforme_flecha_exacta_en_todo_el_tramo(self):
        q = -3.0
        m = modelo([f"C;1;q;{q};;;"], VOL)
        r = resolver(m)[0]["C"]
        self.assertAlmostEqual(r.u[1, 0], q * L_**4 / (8 * E_ * I_), places=9)
        # w(x) exacta (cuártica): q x²(6L²-4Lx+x²)/(24EI)
        X, Y, W = elastica(m, r)[0]
        x = X
        w_ex = q * x**2 * (6 * L_**2 - 4 * L_ * x + x**2) / (24 * E_ * I_)
        self.assertLess(np.abs(W - w_ex).max(), abs(q * L_**4 / (8 * E_ * I_)) * 1e-4)
        e = esfuerzos(m, r)
        self.assertAlmostEqual(e["Mi"][0], q * L_**2 / 2, places=3)   # empotramiento (hogging si q<0)
        self.assertAlmostEqual(e["Mj"][0], 0.0, places=3)
        self.assertAlmostEqual(e["Vj"][0], 0.0, places=6)

    def test_reaccion_y_giro_de_extremo(self):
        q = -3.0
        m = modelo([f"C;1;q;{q};;;"], VOL)
        r = resolver(m)[0]["C"]
        self.assertAlmostEqual(r.R[0, 0], -q * L_, places=6)
        # θy = -dw/dx → en el extremo libre  φy = -q L³/(6EI)
        self.assertAlmostEqual(r.u[1, 2], -q * L_**3 / (6 * E_ * I_), places=9)


class TestOrientacionEIntercambio(unittest.TestCase):
    def test_intercambiar_i_j_no_cambia_reacciones_ni_flector(self):
        P, a = -800.0, 300.0
        m1 = modelo([f"C;1;P;{P};;{a};"], EMP)
        m2 = modelo([f"C;1;P;{P};;{L_ - a};"], EMP, barras=[(1, 2, 1)])
        r1, r2 = resolver(m1)[0]["C"], resolver(m2)[0]["C"]
        np.testing.assert_allclose(r1.R[:, 0], r2.R[:, 0], atol=1e-6)
        c1, c2 = esfuerzos(m1, r1)["curvas"][0], esfuerzos(m2, r2)["curvas"][0]
        x = np.linspace(0, L_, 11)
        M1 = np.interp(x, c1["x"], c1["M"])
        M2 = np.interp(L_ - x, c2["x"], c2["M"])
        np.testing.assert_allclose(M1, M2, atol=1e-3)

    def test_barra_en_y_y_diagonal_equivalen_por_rotacion(self):
        """Misma viga biempotrada a 0°, 90° y 37°: reacciones verticales y flector idénticos."""
        q = -1.5
        ref = None
        for ang in (0, 90, 37, 200):
            c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
            m = modelo([f"C;1;q;{q};;;"], EMP, nodos=[(1, 0, 0), (2, L_ * c, L_ * s)])
            r = resolver(m)[0]["C"]
            e = esfuerzos(m, r)
            cur = (r.R[:, 0].copy(), e["Mi"][0], e["Mmax"][0], e["T"][0])
            if ref is None:
                ref = cur
            np.testing.assert_allclose(cur[0], ref[0], atol=1e-6)
            self.assertAlmostEqual(cur[1], ref[1], places=3)
            self.assertAlmostEqual(cur[2], ref[2], places=3)
            self.assertAlmostEqual(cur[3], 0.0, places=6)


class TestCombinacionesYEntrada(unittest.TestCase):
    def test_combinacion_escala_las_cargas_en_tramo(self):
        m = modelo(["A;1;q;-1;;;", "B;1;P;-1000;;500;"], EMP,
                   extra="COMBINACIONES\ncombinacion;caso;factor\nX;A;1,5\nX;B;2")
        res, _ = resolver(m)
        x = res["X"]
        self.assertAlmostEqual(x.R[0, 0], 1.5 * res["A"].R[0, 0] + 2 * res["B"].R[0, 0], places=6)
        ex, ea, eb = (esfuerzos(m, res[k]) for k in ("X", "A", "B"))
        # el flector de la combinación en cada x es la combinación de los flectores
        cx = ex["curvas"][0]
        xs = np.linspace(0, L_, 9)
        for xx in xs:
            v = np.interp(xx, cx["x"], cx["M"])
            va = np.interp(xx, ea["curvas"][0]["x"], ea["curvas"][0]["M"])
            vb = np.interp(xx, eb["curvas"][0]["x"], eb["curvas"][0]["M"])
            self.assertAlmostEqual(v, 1.5 * va + 2 * vb, delta=1e-3)
        self.assertLess(equilibrio(m, x)["rel"], 1e-12)

    def test_errores_de_entrada(self):
        casos = [
            (["C;9;q;-1;;;"], "no existe"),
            (["C;1;q;-1;;800;200"], "a < b"),
            (["C;1;q;-1;;0;5000"], "a < b"),
            (["C;1;P;-1;;5000;"], "fuera de la barra"),
            (["C;1;P;-1;;;"], "falta"),
            (["C;1;temp;10;0;;"], "alfa"),
            (["C;1;zzz;1;;;"], "desconocido"),
        ]
        for filas, texto in casos:
            with self.assertRaises(ErrorDeEntrada, msg=str(filas)) as cm:
                modelo(filas, EMP)
            self.assertIn(texto, str(cm.exception), msg=str(filas))
        # sección genérica con c cargado y sin h: h se toma como 2·c
        self.assertEqual(modelo(["C;1;temp;10;0;;"], EMP, alfa=1.2e-5).secciones["S"].h, 70.0)

    def test_csv_windows_cp1252(self):
        m = modelo(["C;1;q;-1;;;"], EMP, extra="# comentario con tildes: sección, ñandú", enc="cp1252")
        self.assertEqual(len(m.barras), 1)


class TestInformeConCargasEnTramos(unittest.TestCase):
    def test_informe_y_esquema_con_visor(self):
        from struttura.emparrillado.informe import generar_html, generar_html_esquema
        m = cargar_modelo(RAIZ / "003_Ejemplos" / "001_Emparrillado" / "ejemplo6_cargas_en_tramos.csv")
        res, info = resolver(m)
        h = generar_html(m, res, info)
        self.assertIn("emp3d(", h)
        self.assertIn("Cargas en barras", h)
        self.assertIn("M máx", h)
        self.assertIn("gradiente térmico", h)
        self.assertIn("Vista 3D", h)
        h2 = generar_html_esquema(m)
        self.assertIn("emp3d(", h2)

    def test_combinacion_incluye_cargas_en_tramo_y_termicas(self):
        m = cargar_modelo(RAIZ / "003_Ejemplos" / "001_Emparrillado" / "ejemplo6_cargas_en_tramos.csv")
        res, _ = resolver(m)
        x = res["1.2D+1.6L"]
        self.assertEqual(len(x.cb), len(res["D"].cb) + len(res["L"].cb))
        e = esfuerzos(m, x)
        ed, el_ = esfuerzos(m, res["D"]), esfuerzos(m, res["L"])
        for k in ("Mi", "Mj", "V", "Vj", "T"):
            np.testing.assert_allclose(e[k], 1.2 * ed[k] + 1.6 * el_[k], atol=1e-6)
        # y la elástica de la combinación es la combinación de las elásticas
        Wx = elastica(m, x)
        Wd, Wl = elastica(m, res["D"]), elastica(m, res["L"])
        for (X, Y, W), (_, _, w1), (_, _, w2) in zip(Wx, Wd, Wl):
            np.testing.assert_allclose(W, 1.2 * w1 + 1.6 * w2, atol=1e-9)


class TestFuncionesDeEsfuerzos(unittest.TestCase):
    def test_polinomios_coinciden_con_las_curvas(self):
        from struttura.emparrillado.esfuerzos import funciones_barra
        m = cargar_modelo(RAIZ / "003_Ejemplos" / "001_Emparrillado" / "ejemplo6_cargas_en_tramos.csv")
        res, _ = resolver(m)
        for nombre in ("L", "1.2D+1.6L"):
            r = res[nombre]
            e = esfuerzos(m, r)
            for k in range(len(m.barras)):
                cv = e["curvas"][k]
                esc = 1 + np.abs(cv["M"]).max()
                for sg in funciones_barra(m, r, k):
                    sel = (cv["x"] > sg["x0"] + 1e-6) & (cv["x"] < sg["x1"] - 1e-6)
                    if sel.any():
                        self.assertLess(np.abs(sg["M"](cv["x"][sel]) - cv["M"][sel]).max() / esc, 1e-9)
                        self.assertLess(np.abs(sg["V"](cv["x"][sel]) - cv["V"][sel]).max() / (1 + np.abs(cv["V"]).max()), 1e-9)

    def test_tramos_se_parten_en_las_cargas(self):
        from struttura.emparrillado.esfuerzos import funciones_barra
        m = modelo(["C;1;q;-1;;200;600", "C;1;P;-50;;800;"], EMP)
        r = resolver(m)[0]["C"]
        cortes = [(sg["x0"], sg["x1"]) for sg in funciones_barra(m, r, 0)]
        self.assertEqual(cortes, [(0.0, 200.0), (200.0, 600.0), (600.0, 800.0), (800.0, 1000.0)])


class TestParcial2020(unittest.TestCase):
    """1er parcial, 1er semestre 2020 (Cálculo Estructural I): valores del examen resuelto."""

    def setUp(self):
        self.m = cargar_modelo(RAIZ / "003_Ejemplos" / "001_Emparrillado" / "ejemplo5_parcial2020.csv")
        self.res, _ = resolver(self.m)
        self.r = self.res["E"]

    def test_cargas_equivalentes_estado_2(self):
        np.testing.assert_allclose(self.r.Feq[1], [-3062.5, 1728000.0, 2189229.17], rtol=1e-6)

    def test_desplazamientos_del_nudo_2(self):
        self.assertAlmostEqual(self.r.u[1, 0], 1.152, delta=1e-3)
        self.assertAlmostEqual(self.r.u[1, 2], 0.00409, delta=1e-5)

    def test_esfuerzos_barra_2_3(self):
        e = esfuerzos(self.m, self.r)
        self.assertAlmostEqual(abs(e["V"][1]), 1082, delta=2)
        self.assertAlmostEqual(abs(e["T"][1]), 738012, delta=738012 * 5e-3)
        self.assertAlmostEqual(e["Mi"][1], 3580114, delta=3580114 * 5e-3)
        self.assertAlmostEqual(abs(e["Mj"][1]), 1686927, delta=1686927 * 5e-3)

    def test_tension_en_el_empotramiento_3(self):
        t = tensiones(self.m, esfuerzos(self.m, self.r))[1]
        self.assertAlmostEqual(abs(t["sig_j"]), 59.04, delta=0.3)

    def test_equilibrio(self):
        self.assertLess(equilibrio(self.m, self.r)["rel"], 1e-12)


if __name__ == "__main__":
    unittest.main()
