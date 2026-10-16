"""Pruebas del programa de soldaduras: tablas de grupos (Shigley 9-1/9-2, Compendio Anexo 1), ejemplos 9-1, 9-2 y 9-4 de Shigley, estática y entrada."""
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "001_Codigo"))

from struttura.soldadura.datos import KSI_MPA, electrodo, filete_minimo_mm  # noqa: E402
from struttura.soldadura.entrada import cargar_csv, desde_linea  # noqa: E402
from struttura.soldadura.grupo import ErrorSoldadura, Grupo, crear  # noqa: E402
from struttura.soldadura.verificar import Soldadura, verificar  # noqa: E402
from struttura.emparrillado.entrada import ErrorDeEntrada  # noqa: E402

EJ = RAIZ / "003_Ejemplos" / "005_Soldadura"


class TestTablasDeGrupos(unittest.TestCase):
    """Propiedades como línea contra las fórmulas de Shigley (Tablas 9-1 y 9-2) y del Compendio (cap. 18, Anexo 1)."""
    b, d = 56.0, 190.0

    def g(self, nombre):
        return crear(nombre, dict(b=self.b, d=self.d))

    def test_polares_Ju(self):
        b, d = self.b, self.d
        casos = {
            "costados": (2 * d, d * (3 * b**2 + d**2) / 6),
            "arriba_abajo": (2 * b, (b**3 + 3 * b * d**2) / 6),
            "L": (b + d, ((b + d) ** 4 - 6 * b**2 * d**2) / (12 * (b + d))),
            "C": (2 * b + d, (8 * b**3 + 6 * b * d**2 + d**3) / 12 - b**4 / (2 * b + d)),
            "C_invertida": (b + 2 * d, (b + 2 * d) ** 3 / 12 - d**2 * (b + d) ** 2 / (b + 2 * d)),
            "rectangulo": (2 * b + 2 * d, (b + d) ** 3 / 6),
            "doble_t": (2 * b + 2 * d, (b**3 + 3 * b * d**2 + d**3) / 6),
        }
        for n, (A, J) in casos.items():
            g = self.g(n)
            self.assertAlmostEqual(g.Lw / A, 1, 10, n)
            self.assertAlmostEqual(g.Ju / J, 1, 9, n)
        self.assertAlmostEqual(crear("linea", dict(d=self.d)).Ju, self.d**3 / 12, 5)
        c = crear("circulo", dict(d=self.d))
        self.assertAlmostEqual(c.Lw, math.pi * self.d, 9)
        self.assertAlmostEqual(c.Ju / (math.pi * self.d**3 / 4), 1, 12)

    def test_flexion_Iu_tabla_9_2(self):
        b, d = self.b, self.d
        yb = d**2 / (b + 2 * d)
        casos = {
            "costados": d**3 / 6,
            "arriba_abajo": b * d**2 / 2,
            "C": d**2 * (6 * b + d) / 12,
            "C_invertida": 2 * d**3 / 3 - 2 * d**2 * yb + (b + 2 * d) * yb**2,
            "rectangulo": d**2 * (3 * b + d) / 6,
            "doble_t": d**2 * (3 * b + d) / 6,
        }
        for n, I in casos.items():
            self.assertAlmostEqual(self.g(n).Iyu / I, 1, 9, n)
        self.assertAlmostEqual(crear("circulo", dict(d=d)).Iyu / (math.pi * d**3 / 8), 1, 12)

    def test_baricentros(self):
        b, d = self.b, self.d
        self.assertAlmostEqual(self.g("C").yg, b**2 / (2 * b + d), 9)
        L = self.g("L")
        self.assertAlmostEqual(L.yg, b**2 / (2 * (b + d)), 9)
        self.assertAlmostEqual(L.zg, d**2 / (2 * (b + d)), 9)
        self.assertAlmostEqual(self.g("C_invertida").zg, -d**2 / (b + 2 * d), 9)


class TestEjemplosShigley(unittest.TestCase):
    def test_ejemplo_9_1(self):
        g = crear("C", dict(b=56, d=190))
        w = 6.0
        self.assertAlmostEqual(0.707 * w * g.Lw, 1280, delta=2)                      # A = 1280 mm²
        self.assertAlmostEqual(g.yg, 10.4, delta=0.05)
        self.assertAlmostEqual(0.707 * w * g.Ju / 7.07e6, 1.0, delta=0.002)          # J = 7,07·10⁶ mm⁴
        E = (0, 0, -25000, 0, 0, 0)
        self.assertAlmostEqual(g.trasladar(E, (-100, 0))[3], 2760e3, delta=2e3)       # M = 2760 N·m
        r = g.evaluar(E, (-100, 0))
        tau = r["fmax"] / (0.707 * w)
        self.assertAlmostEqual(tau, 43.9, delta=0.1)                                  # τ máx = 43,9 MPa
        self.assertEqual(r["punto"][0], 0.0)
        self.assertAlmostEqual(abs(r["punto"][1]), 95.0)                              # en C / D (extremos del cordón vertical)
        # primario τ' = 19,5 MPa y τ'' en A y C (41,0 y 37,3 MPa)
        self.assertAlmostEqual(25000 / (0.707 * w * g.Lw), 19.5, delta=0.05)
        T = g.trasladar(E, (-100, 0))[3]
        rA, rC = math.hypot(95, 56 - g.yg), math.hypot(95, g.yg)
        self.assertAlmostEqual(T * rA / (0.707 * w * g.Ju), 41.0, delta=0.2)
        self.assertAlmostEqual(T * rC / (0.707 * w * g.Ju), 37.3, delta=0.1)

    def test_ejemplo_9_2(self):
        g = crear("custom", dict(segmentos="0 -1 0 1|1 -1 1 1"))                     # dos cordones de 2 in
        s = Soldadura("e92", g, "E70", w=0.375, sy_base=27.5e3)
        r = verificar(s, (14000, 0, 0, 0, 0, 0), (0.5, 0), "lbf", "in")
        self.assertAlmostEqual(r["tau_adm"] * 0.707 * 0.375 * g.Lw / 1000, 22.28, delta=0.03)   # F = 5,57·4 = 22,28 kip
        self.assertTrue(r["cumple"])
        self.assertAlmostEqual(r["tau_base"], 9333, delta=2)                           # τ base = F/(2hl) = 9,3 kpsi
        self.assertAlmostEqual(r["w_req_base"], r["fmax"] / (0.4 * 27.5e3), 9)                # τ_adm,base = 0,4·Sy = 11 kpsi

    def test_ejemplo_9_4(self):
        g = crear("costados", dict(b=0.375, d=2))
        s = Soldadura("e94", g, "E60", w=0.375, sy_base=32e3)
        r = verificar(s, (0, 0, -500, 0, 3000, 0), None, "lbf", "in")
        self.assertAlmostEqual(0.707 * 0.375 * g.Lw, 1.06, delta=0.002)               # A = 1,06 in²
        self.assertAlmostEqual(r["tau"] / 1000, 8.51, delta=0.02)                      # τ = 8,51 kpsi
        self.assertAlmostEqual(r["cs_conv"], 3.39, delta=0.01)                         # n = 3,39
        self.assertAlmostEqual(r["tau_adm"] / 1000, 18.0, delta=0.01)
        self.assertAlmostEqual(1.6 * r["cs_cod"], 3.38, delta=0.04)                    # n = 3,38 (código × 1,6)


class TestGargantaYContorno(unittest.TestCase):
    def test_garganta(self):
        g = crear("costados", dict(b=20, d=80))
        r = verificar(Soldadura("a", g, "E70", w=6.0), (0, 0, -1000, 0, 0, 0), None, "N", "mm")
        self.assertAlmostEqual(r["t"], 0.707 * 6.0, 12)
        self.assertAlmostEqual(r["t_req"], 0.707 * r["w_req"], 12)
        self.assertAlmostEqual(r["t_adoptar"], 0.707 * r["w_adoptar"], 12)

    def test_contorno_de_la_seccion(self):
        self.assertEqual(len(crear("circulo", dict(d=40, esp=2)).contorno), 2)          # exterior + interior
        self.assertEqual(len(crear("costados", dict(b=20, d=80)).contorno), 1)           # rectángulo completo (se ven los lados sin cordón)
        self.assertEqual(crear("L", dict(b=20, d=80)).contorno, [])

    def test_informe_sin_circulo_critico_y_con_contorno(self):
        from struttura.soldadura.__main__ import resolver
        from struttura.soldadura.informe import generar_html
        m = desde_linea("costados b=20 d=80 Vz=2000 My=100000 electrodo=E70 w=4 esp=2")
        h = generar_html(m, resolver(m))
        self.assertNotIn("crítico</text>", h)
        self.assertNotIn("<circle", h)
        self.assertIn("<polyline", h)
        self.assertIn("garganta", h)


class TestTope(unittest.TestCase):
    """Unión a tope de tubo: contra las fórmulas exactas del tubo (A, I, J) con tolerancia por la aproximación de pared delgada."""
    d, t = 38.1, 2.0

    def sec(self):
        di = self.d - 2 * self.t
        return math.pi / 4 * (self.d**2 - di**2), math.pi / 64 * (self.d**4 - di**4), math.pi / 32 * (self.d**4 - di**4)

    def run_(self, E, **kw):
        m = desde_linea(f"circulo d={self.d} esp={self.t} tipo=tope electrodo=E70 sy_base=460 " + " ".join(f"{k}={v}" for k, v in kw.items()))
        return verificar(m.soldaduras[0], E, None, "N", "mm")

    def test_axil_flexion_corte_torsion(self):
        A, I, J = self.sec()
        r = self.run_((5000, 0, 0, 0, 0, 0))
        self.assertAlmostEqual(r["sig_max"] / (5000 / A), 1, delta=0.01)                 # N/A
        r = self.run_((0, 0, 0, 0, 600000, 0))
        self.assertAlmostEqual(r["sig_max"] / (600000 * self.d / 2 / I), 1, delta=0.01)  # M c / I (fibra exterior)
        r = self.run_((0, 0, 1500, 0, 0, 0))
        self.assertAlmostEqual(r["tau_max"] / (1500 / A), 1, delta=0.01)                 # V/A (distribución uniforme)
        r = self.run_((0, 0, 0, 100000, 0, 0))
        self.assertAlmostEqual(r["tau_max"] / (100000 * self.d / 2 / J), 1, delta=0.01)  # T r / J

    def test_von_mises_y_admisibles(self):
        r = self.run_((0, 0, -1500, 0, -600000, 0))
        self.assertLessEqual(r["vm_max"], math.sqrt(r["sig_max"]**2 + 3 * r["tau_max"]**2) + 1e-9)       # el máximo de σ_VM no supera la suma de máximos
        self.assertGreaterEqual(r["vm_max"], r["sig_max"] - 1e-9)
        self.assertAlmostEqual(r["sy_ref"], 57 * KSI_MPA, 6)                               # menor entre E70 (57 ksi) y base 460
        self.assertAlmostEqual(r["sig_adm"], 0.60 * 57 * KSI_MPA, 6)
        self.assertAlmostEqual(r["cs_sig"], r["sig_adm"] / r["sig_max"], 9)
        self.assertFalse(r["cumple"])                                                      # 309 MPa > 0,60·393 = 236 MPa

    def test_necesita_espesor_y_sy(self):
        with self.assertRaises(ErrorDeEntrada):
            desde_linea("circulo d=38.1 tipo=tope electrodo=E70 Vz=1")
        with self.assertRaises(ErrorDeEntrada):
            desde_linea("circulo d=38.1 esp=2 tipo=raro electrodo=E70 Vz=1")

    def test_informe_y_comando(self):
        from struttura.soldadura.__main__ import resolver
        from struttura.soldadura.informe import generar_html
        m = desde_linea("circulo d=38.1 esp=2 tipo=tope electrodo=E70 sy_base=460 Vz=-1500 My=-600000")
        h = generar_html(m, resolver(m))
        self.assertIn("A tope", h)
        self.assertIn("NO CUMPLE", h)


class TestEstatica(unittest.TestCase):
    def test_equilibrio_de_momentos_en_grupo_no_principal(self):
        g = crear("L", dict(b=80, d=50))
        E = (1000, 0, 0, 0, 40000, -25000)
        a, b = g._coef_flexion(*g.trasladar(E)[4:])
        My, Mz = g.trasladar(E)[4:]
        self.assertAlmostEqual((a * g.Iyu + b * g.Iyzu), My, 6)                         # ∫ fx z' ds = My'
        self.assertAlmostEqual((a * g.Iyzu + b * g.Izu), -Mz, 6)                        # ∫ fx y' ds = −Mz'

    def test_invariancia_por_giro(self):
        base = [("l", 0, 0, 80, 0), ("l", 0, 0, 0, 50), ("l", 80, 0, 80, -30)]
        th = math.radians(37)
        c, s = math.cos(th), math.sin(th)
        rot = [("l", c * a - s * b_, s * a + c * b_, c * x - s * y, s * x + c * y) for _, a, b_, x, y in base]
        g1, g2 = Grupo(base), Grupo(rot)
        V, Mv = np.array([300.0, -700.0]), np.array([30000.0, -12000.0])                # (My, Mz)
        E1 = (500, V[0], V[1], 9000, Mv[0], Mv[1])
        # el giro de ejes en el plano (y,z) rota Vy,Vz y My,Mz como vectores; N y T no cambian
        R = np.array([[c, -s], [s, c]])
        V2, M2 = R @ V, R @ Mv
        E2 = (500, V2[0], V2[1], 9000, M2[0], M2[1])
        self.assertAlmostEqual(g1.evaluar(E1)["fmax"], g2.evaluar(E2)["fmax"], 6)

    def test_traslado_de_la_carga_no_cambia_el_resultado(self):
        g = crear("C", dict(b=56, d=190))
        E = (800, 100, -500, 200, 3000, -4000)
        y, z = 30.0, -20.0
        N, Vy, Vz, T, My, Mz = E
        # la misma carga aplicada en (ry, rz) equivale a esta otra aplicada en el origen del grupo
        ry, rz = 12.0, 7.0
        E2 = (N, Vy, Vz, T + ry * Vz - rz * Vy, My + rz * N, Mz - ry * N)
        a = g.fuerza(E, y, z, punto=(ry, rz))
        b = g.fuerza(E2, y, z, punto=(0, 0))
        for u, v in zip(a, b):
            self.assertAlmostEqual(float(u), float(v), 9)

    def test_circulo_formulas_cerradas(self):
        d = 50.0
        g = crear("circulo", dict(d=d))
        self.assertAlmostEqual(g.evaluar((0, 0, 0, 0, 1e5, 0))["fmax"], 4 * 1e5 / (math.pi * d**2), 6)    # M c / Iu
        self.assertAlmostEqual(g.evaluar((0, 0, 0, 1e5, 0, 0))["fmax"], 2 * 1e5 / (math.pi * d**2), 6)    # T r / Ju
        self.assertAlmostEqual(g.evaluar((1000, 0, 0, 0, 0, 0))["fmax"], 1000 / (math.pi * d), 9)
        self.assertAlmostEqual(g.evaluar((0, 0, 1000, 0, 0, 0))["fmax"], 1000 / (math.pi * d), 9)

    def test_cordon_recto_no_resiste_su_propio_eje(self):
        with self.assertRaises(ErrorSoldadura):
            crear("linea", dict(d=100)).evaluar((0, 0, 0, 0, 0, 1000))

    def test_arco_completo_igual_circulo_y_media_vuelta(self):
        c = crear("circulo", dict(d=40))
        a = crear("arco", dict(d=40, arcos="0:360"))
        self.assertAlmostEqual(c.Ju, a.Ju, 6)
        m = crear("arco", dict(d=40, arcos="90:180"))
        self.assertAlmostEqual(m.Lw, math.pi * 20, 9)
        self.assertAlmostEqual(m.zg, 2 * 20 / math.pi, 6)                               # baricentro de una semicircunferencia

    def test_varios_arcos_y_superposicion(self):
        g = crear("arco", dict(d=40, arcos="0:45|180:45"))                              # dos costados de 45°
        self.assertAlmostEqual(g.Lw, 2 * 20 * math.radians(45), 9)
        self.assertAlmostEqual(g.yg, 0, 9)
        self.assertAlmostEqual(g.zg, 0, 9)
        for malo in ("0:45|20:45", "350:30|10:30", "0:0", "0-45", "0:400"):           # superpuestos (incluso cruzando 360°) o mal formados
            with self.assertRaises(ErrorSoldadura):
                crear("arco", dict(d=40, arcos=malo))


class TestAsteriscoPieFino(unittest.TestCase):
    """Si el pie a adoptar supera la pieza más delgada: asterisco rojo y nota, sin cambiar los números (criterio del diseñador)."""

    def _html(self, t_gruesa, t_fina, E=(0, 0, -1500, 0, -600000, 0)):
        from struttura.soldadura.informe import bloque
        sol = Soldadura(id="x", grupo=crear("circulo", dict(d=38.1)), electrodo="E70", sy_base=460, t_gruesa=t_gruesa, t_fina=t_fina)
        r = verificar(sol, E, None, "N", "mm")
        return r, bloque(sol, [("c", E, None, r)], {"F": "N", "L": "mm", "M": "N·mm", "S": "MPa", "E": "MPa"})

    def test_tubo_fino_marca_asterisco_y_no_cambia_el_numero(self):
        r, h = self._html(6, 2)                                                           # pie requerido (5,14) > pared (2)
        self.assertAlmostEqual(r["w_adoptar"], r["w_req"], 9)                             # los números no cambian
        self.assertIn("color:#c0392b", h)
        self.assertIn("criterio del diseñador", h)
        r, h = self._html(6, 2, E=(0, 0, -10, 0, 0, 0))                                   # solo el mínimo de la tabla (3,175) > pared (2)
        self.assertAlmostEqual(r["w_adoptar"], 3.175, 3)
        self.assertIn("supera el espesor de la pieza más delgada", h)
        self.assertIn("criterio del diseñador", h)

    def test_sin_conflicto_no_hay_asterisco(self):
        _, h = self._html(10, 10)
        self.assertNotIn("criterio del diseñador", h)


class TestDatos(unittest.TestCase):
    def test_electrodos(self):
        self.assertAlmostEqual(electrodo("E70")[2], 21 * KSI_MPA, 6)                    # 145 MPa (Compendio 145)
        self.assertAlmostEqual(electrodo("E60")[2], 124.1, delta=0.1)
        self.assertAlmostEqual(electrodo("E70")[0], 482.6, delta=0.2)                   # Tabla 9-3: 70 ksi = 482 MPa
        with self.assertRaises(KeyError):
            electrodo("E55")

    def test_filete_minimo(self):
        for t_in, h_in in ((0.25, 1 / 8), (0.26, 3 / 16), (0.5, 3 / 16), (0.75, 1 / 4), (1.0, 5 / 16), (1.5, 5 / 16), (2.0, 3 / 8), (3.0, 1 / 2), (7.0, 5 / 8)):
            self.assertAlmostEqual(filete_minimo_mm(t_in * 25.4) / 25.4, h_in, 9, t_in)

    def test_unidades_equivalentes(self):
        g = crear("costados", dict(b=0.375, d=2))
        gm = crear("costados", dict(b=0.375 * 25.4, d=2 * 25.4))
        ri = verificar(Soldadura("a", g, "E60", w=0.375), (0, 0, -500, 0, 3000, 0), None, "lbf", "in")
        rm = verificar(Soldadura("b", gm, "E60", w=0.375 * 25.4), (0, 0, -500 * 4.4482216, 0, 3000 * 4.4482216 * 25.4, 0), None, "N", "mm")
        self.assertAlmostEqual(ri["cs_cod"], rm["cs_cod"], 4)
        self.assertAlmostEqual(ri["w_req"] * 25.4, rm["w_req"], 3)


class TestEntradaYComando(unittest.TestCase):
    def test_ejemplos_csv(self):
        m = cargar_csv(EJ / "ejemplo1_shigley_9_1_fitting_en_C.csv")
        r = verificar(m.soldaduras[0], m.cargas[0][2], m.cargas[0][3], "N", "mm")
        self.assertAlmostEqual(r["tau"], 43.9, delta=0.1)
        m4 = cargar_csv(EJ / "ejemplo2_shigley_9_4_voladizo_lbf_in.csv")
        r4 = verificar(m4.soldaduras[0], m4.cargas[0][2], m4.cargas[0][3], "lbf", "in")
        self.assertAlmostEqual(r4["cs_conv"], 3.39, delta=0.01)

    def test_linea_de_comando(self):
        m = desde_linea("circulo d=50.8 Vz=3000 My=200000 electrodo=E70 w=3")
        self.assertEqual(len(m.soldaduras), 1)
        for malo in ("", "circulo d=50 electrodo=E70 foo=1", "circulo electrodo=E70 Vz=1", "circulo d=50 Vz=1", "circulo d=50 Vz=1 electrodo=E55"):
            def correr(txt=malo):
                m = desde_linea(txt)
                verificar(m.soldaduras[0], m.cargas[0][2], None, "N", "mm", m.electrodos)
            with self.assertRaises((ErrorDeEntrada, ErrorSoldadura), msg=malo):
                correr()

    def test_electrodo_propio_por_tau_adm(self):
        m = desde_linea("circulo d=50 Vz=3000 electrodo=mio tau_adm=200 w=3")
        r = verificar(m.soldaduras[0], m.cargas[0][2], None, "N", "mm", m.electrodos)
        self.assertAlmostEqual(r["tau_adm"], 200.0, 6)

    def test_comando_y_despachador(self):
        with tempfile.TemporaryDirectory() as d:
            p = subprocess.run([sys.executable, str(RAIZ / "struttura.py"), "--soldadura", "costados b=20 d=80 Vz=2000 My=100000 electrodo=E70 w=4", "-o", d],
                               capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn("w requerido", p.stdout)
            self.assertTrue((Path(d) / "informe.html").is_file())
            p = subprocess.run([sys.executable, str(RAIZ / "struttura.py"), str(EJ / "ejemplo1_shigley_9_1_fitting_en_C.csv"), "-o", d], capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn("43", (Path(d) / "informe.html").read_text(encoding="utf-8"))


class TestIntegracion3D(unittest.TestCase):
    """Bloque SOLDADURAS del pórtico 3D: esfuerzos del solver en el extremo de la barra."""
    EJ3 = RAIZ / "003_Ejemplos" / "004_Portico_espacial" / "ejemplo7_soldadura_en_el_empotramiento.csv"

    def correr(self, texto=None):
        from struttura.portico3d.entrada import cargar_modelo
        from struttura.portico3d.esfuerzos import esfuerzos_extremos
        from struttura.portico3d.soldaduras import evaluar
        from struttura.portico3d.solver import resolver
        ruta = self.EJ3
        if texto is not None:
            d = tempfile.mkdtemp()
            ruta = Path(d) / "m.csv"
            ruta.write_text(texto, encoding="utf-8")
        m = cargar_modelo(ruta)
        res, _ = resolver(m)
        return m, evaluar(m, res, {n: esfuerzos_extremos(m, r) for n, r in res.items()})

    def test_igual_al_modo_rapido(self):
        m, sold = self.correr()
        r = sold["empotramiento"][0][3]
        E = sold["empotramiento"][0][1]
        self.assertAlmostEqual(abs(E[2]), 1500, 3)                                         # V del solver
        self.assertAlmostEqual(abs(E[4]), 600000, 1)                                       # M = V·L
        rq = cargar_csv(EJ / "ejemplo3_tubo_en_voladizo_disposiciones.csv")
        q = verificar(rq.soldaduras[0], rq.cargas[0][2], None, "N", "mm")
        self.assertAlmostEqual(r["fmax"] / q["fmax"], 1.0, 9)
        self.assertEqual(m.soldaduras[0].grupo.Lw, math.pi * 38.1)                         # d tomado de la sección

    def test_salida_csv(self):
        with tempfile.TemporaryDirectory() as d:
            p = subprocess.run([sys.executable, str(RAIZ / "struttura.py"), str(self.EJ3), "-o", d], capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn("w requerido", p.stdout)
            self.assertTrue((Path(d) / "soldaduras.csv").is_file())
            self.assertIn("Soldadura empotramiento", (Path(d) / "informe.html").read_text(encoding="utf-8"))

    def test_errores_de_datos(self):
        base = self.EJ3.read_text(encoding="utf-8").split("SOLDADURAS\n")[0]
        for bloque, msg in (("id;barra;extremo;disposicion;electrodo\ns;XX;i;circulo;E70\n", "barra"),
                            ("id;barra;extremo;disposicion;electrodo\ns;B1;k;circulo;E70\n", "extremo"),
                            ("id;barra;extremo;disposicion;electrodo\ns;B1;i;triangulo;E70\n", "disposición")):
            with self.assertRaises(ErrorDeEntrada) as cm:
                self.correr(base + "SOLDADURAS\n" + bloque)
            self.assertIn(msg, str(cm.exception))

    def test_tope_en_3d_toma_el_espesor_del_tubo(self):
        base = self.EJ3.read_text(encoding="utf-8").split("SOLDADURAS\n")[0]
        m, sold = self.correr(base + "SOLDADURAS\nid;tipo;barra;extremo;disposicion;electrodo;sy_base\nt;tope;B1;i;circulo;E70;460\n")
        r = sold["t"][0][3]
        self.assertEqual(m.soldaduras[0].esp, 2.0)
        self.assertEqual(r["tipo"], "tope")
        self.assertGreater(r["sig_max"], 0)

    def test_extremo_j_y_desplazamiento_del_origen(self):
        base = self.EJ3.read_text(encoding="utf-8").split("SOLDADURAS\n")[0]
        m, sold = self.correr(base + "SOLDADURAS\nid;barra;extremo;disposicion;b;d;electrodo;oy;oz\nj;B1;j;L;30;50;E70;10;0\n")
        E = sold["j"][0][1]
        self.assertAlmostEqual(abs(E[4]), 0.0, 3)                                           # en la punta no hay momento flector
        self.assertAlmostEqual(abs(E[2]), 1500, 3)
        self.assertEqual(sold["j"][0][2], (-10.0, 0.0))


if __name__ == "__main__":
    unittest.main()
