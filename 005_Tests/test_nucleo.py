"""Tests del núcleo.  Ejecutar:  python -m unittest discover -s tests -v   (desde la carpeta raíz)"""
import math
import sys
import tempfile
import os
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "001_Codigo"))

from struttura.emparrillado.barra import constantes, rigidez_global, rigidez_local, matriz_rotacion
from struttura.emparrillado.entrada import cargar_modelo, ErrorDeEntrada
from struttura.emparrillado.solver import resolver, equilibrio, ErrorEstructura
from struttura.emparrillado.esfuerzos import esfuerzos, tensiones, elastica
from struttura.emparrillado.secciones import crear_seccion


# ---------------------------------------------------------------- utilidades
def escribir_csv(texto: str) -> Path:
    d = Path(tempfile.mkdtemp())
    ruta = d / "modelo.csv"
    ruta.write_text(texto, encoding="utf-8")
    return ruta


def crear_modelo_csv(nodos, barras, apoyos, cargas, E=210000.0, nu=0.3, seccion="tubo,50,3",
                     sep=",", prefij=None, combos=None, resortes=None, fy="", sadm=""):
    """Escribe UN CSV con bloques titulados y lo carga."""
    s = sep
    L = []
    L.append("NODOS")
    L.append(f"id{s}x{s}y")
    L += [f"{a}{s}{b}{s}{c}" for a, b, c in nodos]
    L += ["", "MATERIALES", f"id{s}E{s}nu{s}fy{s}sadm", f"M{s}{E}{s}{nu}{s}{fy}{s}{sadm}", "", "SECCIONES"]
    L.append(f"id{s}tipo{s}d{s}t{s}b{s}h{s}I{s}J")
    tipo, *par = seccion.split(",")
    if tipo == "tubo":
        fila = ["S", "tubo", par[0], par[1], "", "", "", ""]
    elif tipo == "rectangular":
        fila = ["S", "rectangular", "", "", par[0], par[1], "", ""]
    else:
        fila = ["S", "generica", "", "", "", "", par[0], par[1]]
    L.append(s.join(fila))
    L += ["", "BARRAS", f"id{s}nodo_i{s}nodo_j{s}material{s}seccion"]
    L += [f"{k + 1}{s}{a}{s}{b}{s}M{s}S" for k, (a, b) in enumerate(barras)]
    L += ["", "APOYOS", f"nodo{s}uz{s}phix{s}phiy"]
    L += [f"{a}{s}{b}{s}{c}{s}{d}" for a, b, c, d in apoyos]
    if resortes:
        L += ["", "RESORTES", f"nodo{s}kz{s}kphix{s}kphiy"]
        L += [f"{n}{s}{a}{s}{b}{s}{c}" for n, a, b, c in resortes]
    L += ["", "CARGAS", f"caso{s}nodo{s}Pz{s}Mx{s}My"]
    L += [f"{c}{s}{n}{s}{p}{s}{mx}{s}{my}" for c, n, p, mx, my in cargas]
    if prefij:
        L += ["", "DESPLAZAMIENTOS PREFIJADOS", f"caso{s}nodo{s}uz{s}phix{s}phiy"]
        L += [f"{c}{s}{n}{s}{a}{s}{b}{s}{d}" for c, n, a, b, d in prefij]
    if combos:
        L += ["", "COMBINACIONES", f"combinacion{s}caso{s}factor"]
        L += [f"{a}{s}{b}{s}{c}" for a, b, c in combos]
    return cargar_modelo(escribir_csv("\n".join(L) + "\n"))


def k_tabla(K, K1, K2, K3, g1, g2):
    """Matriz 'Barra General' transcripta literalmente de la tabla (independiente de T·k·Tᵀ)."""
    A = g2 * K2
    B = -g1 * K2
    C = g1**2 * K + g2**2 * K3
    D = g1 * g2 * (K - K3)
    E = g2**2 * K + g1**2 * K3
    F = -g1 * g2 * (K + K3 / 2)
    G = -g1**2 * K + g2**2 * K3 / 2
    H = -g2**2 * K + g1**2 * K3 / 2
    K1_ = K1
    return np.array([
        [K1_, A, B, -K1_, A, B],
        [A, C, D, -A, G, F],
        [B, D, E, -B, F, H],
        [-K1_, -A, -B, K1_, -A, -B],
        [A, G, F, -A, C, D],
        [B, F, H, -B, D, E]])


def frame3d_referencia(nodos, barras, apoyos_uz, E, G, I, J, A, cargas):
    """Solver de pórtico ESPACIAL 12x12 (independiente), con la estructura en el plano XY.

    Se restringen los GDL en el plano (ux, uy, θz) de todos los nodos; solo quedan uz, θx, θy.
    apoyos_uz: dict nodo -> (uz, θx, θy) booleanos.  cargas: dict nodo -> (Fz, Mx, My).
    """
    n = len(nodos)
    K = np.zeros((6 * n, 6 * n))
    for (a, b) in barras:
        dx, dy = nodos[b][0] - nodos[a][0], nodos[b][1] - nodos[a][1]
        L = math.hypot(dx, dy)
        ex = np.array([dx / L, dy / L, 0.0])
        ez = np.array([0.0, 0.0, 1.0])
        ey = np.cross(ez, ex)
        lam = np.array([ex, ey, ez])
        T = np.zeros((12, 12))
        for k in range(4):
            T[3 * k:3 * k + 3, 3 * k:3 * k + 3] = lam
        Iy = Iz = I
        k = np.zeros((12, 12))
        k[0, 0] = k[6, 6] = E * A / L
        k[0, 6] = k[6, 0] = -E * A / L
        k[3, 3] = k[9, 9] = G * J / L
        k[3, 9] = k[9, 3] = -G * J / L
        # flexión en plano xy (v, θz)
        for (p, q, val) in [(1, 1, 12 * E * Iz / L**3), (7, 7, 12 * E * Iz / L**3),
                            (1, 7, -12 * E * Iz / L**3), (1, 5, 6 * E * Iz / L**2),
                            (1, 11, 6 * E * Iz / L**2), (5, 5, 4 * E * Iz / L),
                            (11, 11, 4 * E * Iz / L), (5, 11, 2 * E * Iz / L),
                            (5, 7, -6 * E * Iz / L**2), (7, 11, -6 * E * Iz / L**2)]:
            k[p, q] = k[q, p] = val
        # flexión en plano xz (w, θy)
        for (p, q, val) in [(2, 2, 12 * E * Iy / L**3), (8, 8, 12 * E * Iy / L**3),
                            (2, 8, -12 * E * Iy / L**3), (2, 4, -6 * E * Iy / L**2),
                            (2, 10, -6 * E * Iy / L**2), (4, 4, 4 * E * Iy / L),
                            (10, 10, 4 * E * Iy / L), (4, 10, 2 * E * Iy / L),
                            (4, 8, 6 * E * Iy / L**2), (8, 10, 6 * E * Iy / L**2)]:
            k[p, q] = k[q, p] = val
        kg = T.T @ k @ T
        d = np.r_[6 * a:6 * a + 6, 6 * b:6 * b + 6]
        K[np.ix_(d, d)] += kg
    fijo = np.zeros(6 * n, dtype=bool)
    F = np.zeros(6 * n)
    for i in range(n):
        fijo[6 * i + 0] = fijo[6 * i + 1] = fijo[6 * i + 5] = True     # ux, uy, θz
        r = apoyos_uz.get(i, (False, False, False))
        fijo[6 * i + 2], fijo[6 * i + 3], fijo[6 * i + 4] = r
    for i, (fz, mx, my) in cargas.items():
        F[6 * i + 2], F[6 * i + 3], F[6 * i + 4] = fz, mx, my
    libre = ~fijo
    u = np.zeros(6 * n)
    u[libre] = np.linalg.solve(K[np.ix_(libre, libre)], F[libre])
    return np.array([[u[6 * i + 2], u[6 * i + 3], u[6 * i + 4]] for i in range(n)])


# -------------------------------------------------------------------- tests
class TestMatrices(unittest.TestCase):
    def test_general_vs_tabla_todos_los_angulos(self):
        E, G, I, J, L = 210000.0, 80769.0, 1.2e5, 2.4e5, 1500.0
        K, K1, K2, K3 = constantes(E, G, I, J, L)
        for ang in np.linspace(-180, 180, 73):
            g1, g2 = math.cos(math.radians(ang)), math.sin(math.radians(ang))
            kg = rigidez_global(E, G, I, J, L, g1, g2)
            kt = k_tabla(K, K1, K2, K3, g1, g2)
            np.testing.assert_allclose(kg, kt, rtol=1e-10, atol=1e-6 * K1)

    def test_casos_particulares_de_la_tabla(self):
        E, G, I, J, L = 200000.0, 77000.0, 8e4, 1.6e5, 1000.0
        K, K1, K2, K3 = constantes(E, G, I, J, L)
        h = K3 / 2
        Z = 0.0
        esperadas = {
            (1, 0): [[K1, Z, -K2, -K1, Z, -K2], [Z, K, Z, Z, -K, Z], [-K2, Z, K3, K2, Z, h],
                     [-K1, Z, K2, K1, Z, K2], [Z, -K, Z, Z, K, Z], [-K2, Z, h, K2, Z, K3]],
            (0, 1): [[K1, K2, Z, -K1, K2, Z], [K2, K3, Z, -K2, h, Z], [Z, Z, K, Z, Z, -K],
                     [-K1, -K2, Z, K1, -K2, Z], [K2, h, Z, -K2, K3, Z], [Z, Z, -K, Z, Z, K]],
            (-1, 0): [[K1, Z, K2, -K1, Z, K2], [Z, K, Z, Z, -K, Z], [K2, Z, K3, -K2, Z, h],
                      [-K1, Z, -K2, K1, Z, -K2], [Z, -K, Z, Z, K, Z], [K2, Z, h, -K2, Z, K3]],
            (0, -1): [[K1, -K2, Z, -K1, -K2, Z], [-K2, K3, Z, K2, h, Z], [Z, Z, K, Z, Z, -K],
                      [-K1, K2, Z, K1, K2, Z], [-K2, h, Z, K2, K3, Z], [Z, Z, -K, Z, Z, K]],
        }
        for (g1, g2), M in esperadas.items():
            np.testing.assert_allclose(rigidez_global(E, G, I, J, L, g1, g2), np.array(M),
                                       atol=1e-6 * K1, err_msg=f"barra según γ=({g1},{g2})")

    def test_simetria_y_modos_rigidos(self):
        kg = rigidez_global(210000, 80000, 1e5, 2e5, 1234.0, 0.6, 0.8)
        np.testing.assert_allclose(kg, kg.T, atol=1e-8)
        # traslación rígida en z y rotación rígida => fuerza nula
        L, g1, g2 = 1234.0, 0.6, 0.8
        rig_z = np.array([1, 0, 0, 1, 0, 0.0])
        self.assertLess(np.abs(kg @ rig_z).max(), 1e-6)
        # rotación rígida alrededor de un eje horizontal cualquiera que pasa por el nodo i
        # φ = (φx, φy) = ω·(cos a, sen a) en i y j;  uz_j = -(x_j·φy - y_j·φx)... uz = φx·y - φy·x
        w = np.array([0.3, -0.7])
        xj, yj = L * g1, L * g2
        u = np.array([0, w[0], w[1], w[0] * yj - w[1] * xj, w[0], w[1]])
        self.assertLess(np.abs(kg @ u).max(), 1e-6)


class TestVoladizos(unittest.TestCase):
    E, nu = 210000.0, 0.3

    def _props(self):
        s = crear_seccion("S", "tubo", {"d": 50.0, "t": 3.0})
        return s, self.E, self.E / (2 * (1 + self.nu))

    def test_voladizo_recto_flexion_y_torsion(self):
        s, E, G = self._props()
        L, P, M = 1200.0, -800.0, 5.0e4
        m = crear_modelo_csv([(1, 0, 0), (2, L, 0)], [(1, 2)], [(1, 1, 1, 1)],
                             [("P", 2, P, 0, 0), ("T", 2, 0, M, 0)])
        res, _ = resolver(m)
        w = P * L**3 / (3 * E * s.I)
        th = -P * L**2 / (2 * E * s.I)      # θy = -w'  (con P<0: θy > 0)
        self.assertAlmostEqual(res["P"].u[1, 0] / w, 1.0, places=9)
        self.assertAlmostEqual(res["P"].u[1, 2] / (-w * 3 / (2 * L)), 1.0, places=9)
        self.assertAlmostEqual(res["P"].u[1, 2] / (-P * L**2 / (2 * E * s.I)), 1.0, places=9)
        self.assertAlmostEqual(res["T"].u[1, 1] / (M * L / (G * s.J)), 1.0, places=9)
        # reacciones
        np.testing.assert_allclose(res["P"].R[0], [-P, 0.0, P * L], atol=1e-6)
        # esfuerzos: M en empotramiento = P·L (hogging con P<0 => M<0)
        e = esfuerzos(m, res["P"])
        self.assertAlmostEqual(e["Mi"][0], P * L, places=6)
        self.assertAlmostEqual(e["Mj"][0], 0.0, places=6)
        self.assertAlmostEqual(e["V"][0], -P, places=6)

    def test_voladizo_en_L(self):
        """Solución analítica: w = P a³/(3EI) + P b² a/(GJ) + P b³/(3EI)."""
        s, E, G = self._props()
        a, b, P = 1000.0, 800.0, -500.0
        m = crear_modelo_csv([(1, 0, 0), (2, a, 0), (3, a, b)], [(1, 2), (2, 3)],
                             [(1, 1, 1, 1)], [("P", 3, P, 0, 0)])
        res, info = resolver(m)
        w = P * a**3 / (3 * E * s.I) + P * b**2 * a / (G * s.J) + P * b**3 / (3 * E * s.I)
        self.assertAlmostEqual(res["P"].u[2, 0] / w, 1.0, places=9)
        # esfuerzos: barra 1 (según X): torsión = P·b, momento en empotramiento = P·a
        e = esfuerzos(m, res["P"])
        self.assertAlmostEqual(abs(e["T"][0]), abs(P) * b, places=5)
        self.assertAlmostEqual(abs(e["Mi"][0]), abs(P) * a, places=5)
        self.assertAlmostEqual(abs(e["T"][1]), 0.0, places=5)
        self.assertAlmostEqual(abs(e["Mi"][1]), abs(P) * b, places=5)
        self.assertLess(equilibrio(m, res["P"])["rel"], 1e-12)

    def test_invariancia_por_rotacion(self):
        """La misma L rotada un ángulo cualquiera debe dar el mismo uz, y esfuerzos iguales."""
        a, b, P = 1000.0, 800.0, -500.0
        base = None
        for ang in (0, 17, 45, 90, 133, 200, -60):
            c, s_ = math.cos(math.radians(ang)), math.sin(math.radians(ang))
            pts = [(0, 0), (a, 0), (a, b)]
            nodos = [(k + 1, x * c - y * s_ + 300, x * s_ + y * c - 150) for k, (x, y) in enumerate(pts)]
            m = crear_modelo_csv(nodos, [(1, 2), (2, 3)], [(1, 1, 1, 1)], [("P", 3, P, 0, 0)])
            res, _ = resolver(m)
            e = esfuerzos(m, res["P"])
            vals = np.array([res["P"].u[2, 0], abs(e["T"][0]), abs(e["Mi"][0]), abs(e["Mi"][1])])
            if base is None:
                base = vals
            np.testing.assert_allclose(vals, base, rtol=1e-9)


class TestContraPorticoEspacial(unittest.TestCase):
    """Parrilla irregular con barras en ángulos arbitrarios, contra un solver 3D independiente."""

    def test_parrilla_irregular(self):
        nodos = [(1, 0, 0), (2, 1800, 100), (3, 3700, -200), (4, 200, 1500), (5, 1900, 1700),
                 (6, 3600, 1300), (7, -100, 3100), (8, 2100, 3000), (9, 3900, 3300)]
        barras = [(1, 2), (2, 3), (4, 5), (5, 6), (7, 8), (8, 9), (1, 4), (4, 7), (2, 5), (5, 8),
                  (3, 6), (6, 9), (1, 5), (5, 9), (2, 6)]
        apoyos = [(1, 1, 0, 0), (3, 1, 0, 0), (7, 1, 1, 0), (9, 1, 0, 1)]
        cargas = [("C", 5, -2000, 3e5, -1e5), ("C", 2, -700, 0, 0), ("C", 8, 300, -2e5, 0),
                  ("C", 6, -900, 1e5, 4e5)]
        m = crear_modelo_csv(nodos, barras, apoyos, cargas, seccion="tubo,60,3")
        res, info = resolver(m)
        s = m.secciones["S"]
        E = 210000.0
        G = E / 2.6
        ref = frame3d_referencia(
            [(x, y) for _, x, y in nodos], [(a - 1, b - 1) for a, b in barras],
            {i - 1: (bool(a), bool(b), bool(c)) for i, a, b, c in apoyos}, E, G, s.I, s.J, s.A,
            {i - 1: (p, mx, my) for _, i, p, mx, my in cargas})
        np.testing.assert_allclose(res["C"].u, ref, rtol=1e-8, atol=1e-10)
        self.assertLess(equilibrio(m, res["C"])["rel"], 1e-10)

    def test_desplazamiento_prefijado_de_apoyo(self):
        """Apoyo que desciende: desplazamiento impuesto exacto y reacciones autoequilibradas."""
        nodos = [(1, 0, 0), (2, 1500, 0), (3, 1500, 1000)]
        m = crear_modelo_csv(nodos, [(1, 2), (2, 3)], [(1, 1, 1, 1), (3, 1, 0, 0)],
                             [("C", 2, -100, 0, 0)], prefij=[("A", 3, -4.0, 0, 0)])
        res, _ = resolver(m)
        # el caso A solo tiene desplazamiento prefijado: uz del nodo 3 = -4
        self.assertAlmostEqual(res["A"].u[2, 0], -4.0, places=12)
        # equilibrio del caso A: reacciones nulas en suma
        self.assertLess(equilibrio(m, res["A"])["rel"], 1e-10)
        # superposición: caso C (con apoyo 3 fijo) + A == combinación
        self.assertAlmostEqual(res["A"].R[:, 0].sum(), 0.0, places=6)


class TestBarraSegunY(unittest.TestCase):
    """En una barra según Y global, la torsión y la flexión intercambian GDL globales:
    el momento Mx (global) FLEXA la barra y My (global) la TORSIONA.  La matriz local es siempre
    la misma; lo que cambia es la rotación."""

    E, nu = 210000.0, 0.3

    def _caso(self, y2, mx, my):
        m = crear_modelo_csv([(1, 0, 0), (2, 0, y2)], [(1, 2)], [(1, 1, 1, 1)], [("C", 2, 0, mx, my)])
        res, _ = resolver(m)
        return m, res["C"]

    def test_momento_Mx_flexa_barra_segun_mas_Y_y_menos_Y(self):
        M, L = 5.0e4, 900.0
        for signo in (+1, -1):
            m, r = self._caso(signo * L, M, 0.0)
            s = m.secciones["S"]
            self.assertAlmostEqual(r.u[1, 1] / (M * L / (self.E * s.I)), 1.0, places=9)
            self.assertAlmostEqual(r.u[1, 0] / (signo * M * L**2 / (2 * self.E * s.I)), 1.0, places=9)
            self.assertAlmostEqual(r.u[1, 2], 0.0, places=12)

    def test_momento_My_tuerce_barra_segun_mas_Y_y_menos_Y(self):
        M, L = 5.0e4, 900.0
        G = self.E / (2 * (1 + self.nu))
        for signo in (+1, -1):
            m, r = self._caso(signo * L, 0.0, M)
            s = m.secciones["S"]
            self.assertAlmostEqual(abs(r.u[1, 2]) / (M * L / (G * s.J)), 1.0, places=9)
            self.assertAlmostEqual(r.u[1, 1], 0.0, places=12)
            self.assertAlmostEqual(r.u[1, 0], 0.0, places=12)

    def test_esfuerzos_locales_se_reparten_al_reves(self):
        """Barra según Y: Mx global = flexión (M local), My global = torsión (T local)."""
        M, L = 5.0e4, 900.0
        m, r = self._caso(L, M, 0.0)
        e = esfuerzos(m, r)
        self.assertAlmostEqual(abs(e["Mi"][0]), M, places=6)
        self.assertAlmostEqual(abs(e["T"][0]), 0.0, places=6)
        m2, r2 = self._caso(L, 0.0, M)
        e2 = esfuerzos(m2, r2)
        self.assertAlmostEqual(abs(e2["T"][0]), M, places=6)
        self.assertAlmostEqual(abs(e2["Mi"][0]), 0.0, places=6)


class TestIntercambioIJ(unittest.TestCase):
    """Invertir el sentido i->j de las barras no cambia la física: M, tensiones, reacciones y
    desplazamientos son idénticos.  Solo V cambia de signo (se define respecto de xl); T y M no: su signo
    no depende del sentido en que se recorre la barra."""

    NODOS = [(1, 0, 0), (2, 1800, 100), (3, 3700, -200), (4, 200, 1500), (5, 1900, 1700),
             (6, 3600, 1300), (7, -100, 3100), (8, 2100, 3000), (9, 3900, 3300)]
    BARRAS = [(1, 2), (2, 3), (4, 5), (5, 6), (7, 8), (8, 9), (1, 4), (4, 7), (2, 5), (5, 8),
              (3, 6), (6, 9), (1, 5), (5, 9), (2, 6)]
    APOYOS = [(1, 1, 0, 0), (3, 1, 0, 0), (7, 1, 1, 0), (9, 1, 0, 1)]
    CARGAS = [("C", 5, -2000, 3e5, -1e5), ("C", 2, -700, 0, 0), ("C", 8, 300, -2e5, 0), ("C", 6, -900, 1e5, 4e5)]

    def _resolver(self, barras):
        m = crear_modelo_csv(self.NODOS, barras, self.APOYOS, self.CARGAS, seccion="tubo,60,3",
                             fy=235, sadm=156)
        res, _ = resolver(m)
        return m, res["C"]

    def test_invertir_todas_las_barras(self):
        m1, r1 = self._resolver(self.BARRAS)
        m2, r2 = self._resolver([(b, a) for a, b in self.BARRAS])
        np.testing.assert_allclose(r1.u, r2.u, rtol=1e-9, atol=1e-12)
        np.testing.assert_allclose(r1.R, r2.R, rtol=1e-9, atol=1e-6)
        e1, e2 = esfuerzos(m1, r1), esfuerzos(m2, r2)
        # M: el flector en el extremo i de una es el del extremo j de la otra, y no cambia de signo
        np.testing.assert_allclose(e1["Mi"], e2["Mj"], rtol=1e-9, atol=1e-6)
        np.testing.assert_allclose(e1["Mj"], e2["Mi"], rtol=1e-9, atol=1e-6)
        # V: mismo valor absoluto, signo opuesto.  T: idéntico (positivo si su vector sale de la cara)
        np.testing.assert_allclose(e1["V"], -e2["V"], rtol=1e-9, atol=1e-6)
        np.testing.assert_allclose(e1["T"], e2["T"], rtol=1e-9, atol=1e-6)
        t1, t2 = tensiones(m1, e1), tensiones(m2, e2)
        for a, b in zip(t1, t2):
            self.assertAlmostEqual(a["vm"], b["vm"], places=8)
            self.assertAlmostEqual(a["n_fy"], b["n_fy"], places=8)

    def test_invertir_solo_algunas_barras(self):
        """Mezcla de sentidos (lo normal al cargar a mano): los resultados globales no cambian."""
        mezcla = [(b, a) if k % 2 else (a, b) for k, (a, b) in enumerate(self.BARRAS)]
        m1, r1 = self._resolver(self.BARRAS)
        m2, r2 = self._resolver(mezcla)
        np.testing.assert_allclose(r1.u, r2.u, rtol=1e-9, atol=1e-12)
        v1 = max(t["vm"] for t in tensiones(m1, esfuerzos(m1, r1)))
        v2 = max(t["vm"] for t in tensiones(m2, esfuerzos(m2, r2)))
        self.assertAlmostEqual(v1, v2, places=8)


class TestTensiones(unittest.TestCase):
    def test_voladizo_tubo(self):
        L, P = 1000.0, -600.0
        m = crear_modelo_csv([(1, 0, 0), (2, L, 0)], [(1, 2)], [(1, 1, 1, 1)], [("P", 2, P, 0, 0)])
        res, _ = resolver(m)
        s = m.secciones["S"]
        t = tensiones(m, esfuerzos(m, res["P"]))[0]
        self.assertAlmostEqual(t["sig_i"], P * L * s.c / s.I, places=6)
        self.assertAlmostEqual(t["sig_j"], 0.0, places=6)
        self.assertAlmostEqual(t["tau_v"], s.kv * abs(P) / s.A, places=9)
        self.assertAlmostEqual(t["vm"], max(abs(t["sig_i"]), math.sqrt(3) * t["tau_v"]), places=6)

    def test_torsion_pura(self):
        m = crear_modelo_csv([(1, 0, 0), (2, 1000, 0)], [(1, 2)], [(1, 1, 1, 1)], [("T", 2, 0, 1e5, 0)])
        res, _ = resolver(m)
        s = m.secciones["S"]
        t = tensiones(m, esfuerzos(m, res["T"]))[0]
        self.assertAlmostEqual(t["tau_t"], 1e5 / s.Wt, places=8)
        self.assertAlmostEqual(t["vm"], math.sqrt(3) * 1e5 / s.Wt, places=6)


class TestInforme(unittest.TestCase):
    def test_genera_html_con_y_sin_graficos(self):
        from struttura.emparrillado.informe import generar_html
        m = crear_modelo_csv([(1, 0, 0), (2, 1000, 0), (3, 1000, 800)], [(1, 2), (2, 3)],
                             [(1, 1, 1, 1)], [("P", 3, -500, 0, 0)])
        res, info = resolver(m)
        h = generar_html(m, res, info, con_graficos=False)
        self.assertIn("Memoria de cálculo", h)
        self.assertIn("OK", h)
        h2 = generar_html(m, res, info, con_graficos=True)
        self.assertEqual(h2.count("<svg"), 6)     # esquema + (cargas, deformada, M, T, V)
        self.assertIn("window.print()", h2)       # botón imprimir
        self.assertIn("@page { size: A4; margin: 0; }", h2)
        self.assertNotIn("asentamiento", h2.lower())

    def test_esquema_sin_calcular(self):
        from struttura.emparrillado.informe import generar_html_esquema
        m = crear_modelo_csv([(1, 0, 0), (2, 1000, 0)], [(1, 2)], [(1, 1, 1, 1)], [("P", 2, -500, 0, 0)])
        h = generar_html_esquema(m)
        self.assertIn("sin calcular", h)
        self.assertNotIn("Desplazamientos nodales", h)


class TestElastica(unittest.TestCase):
    def test_extremos_y_pendiente(self):
        m = crear_modelo_csv([(1, 0, 0), (2, 1000, 500)], [(1, 2)], [(1, 1, 1, 1)],
                             [("P", 2, -300, 1e4, 2e4)])
        res, _ = resolver(m)
        X, Y, W = elastica(m, res["P"], n=41)[0]
        self.assertAlmostEqual(W[0], 0.0, places=12)
        self.assertAlmostEqual(W[-1], res["P"].u[1, 0], places=10)
        # pendiente en el extremo j: θy_local = -dw/dx
        L = m.barras[0].L
        dw = (W[-1] - W[-2]) / (L / 40)
        self.assertAlmostEqual(-dw, res["P"].ub[0, 5], delta=abs(res["P"].ub[0, 5]) * 0.08 + 1e-12)


class TestRobustez(unittest.TestCase):
    def test_mecanismo_por_torsion(self):
        """Viga recta sobre X con apoyos solo en uz: puede girar alrededor de su eje."""
        m = crear_modelo_csv([(1, 0, 0), (2, 1000, 0)], [(1, 2)], [(1, 1, 0, 0), (2, 1, 0, 0)],
                             [("P", 2, -100, 0, 0)])
        with self.assertRaises(ErrorEstructura) as cm:
            resolver(m)
        self.assertIn("inestable", str(cm.exception))

    def test_nodo_sin_barras(self):
        with self.assertRaises(ErrorEstructura):
            m = crear_modelo_csv([(1, 0, 0), (2, 1000, 0), (3, 500, 500)], [(1, 2)],
                                 [(1, 1, 1, 1)], [("P", 2, -100, 0, 0)])
            resolver(m)

    def test_csv_excel_es(self):
        """Separador ';' y decimal con coma."""
        m = crear_modelo_csv([(1, "0", "0"), (2, "1000,5", "0")], [(1, 2)], [(1, 1, 1, 1)],
                             [("P", 2, "-100,25", 0, 0)], sep=";")
        self.assertAlmostEqual(m.nodos[1].x, 1000.5)
        self.assertAlmostEqual(m.casos["P"][1, 0], -100.25)

    def test_errores_de_entrada(self):
        with self.assertRaises(ErrorDeEntrada):     # nodo inexistente en barra
            crear_modelo_csv([(1, 0, 0), (2, 1, 0)], [(1, 9)], [(1, 1, 1, 1)], [("P", 2, -1, 0, 0)])
        with self.assertRaises(ErrorDeEntrada):     # desplazamiento prefijado en GDL libre
            crear_modelo_csv([(1, 0, 0), (2, 1000, 0)], [(1, 2)], [(1, 1, 1, 1)],
                             [("P", 2, -1, 0, 0)], prefij=[("A", 2, -1.0, 0, 0)])

    def test_combinacion(self):
        m = crear_modelo_csv([(1, 0, 0), (2, 1000, 0)], [(1, 2)], [(1, 1, 1, 1)],
                             [("D", 2, -100, 0, 0), ("L", 2, -50, 0, 0)],
                             combos=[("U", "D", 1.2), ("U", "L", 1.6)])
        res, _ = resolver(m)
        np.testing.assert_allclose(res["U"].u, 1.2 * res["D"].u + 1.6 * res["L"].u)
        np.testing.assert_allclose(esfuerzos(m, res["U"])["Mi"],
                                   1.2 * esfuerzos(m, res["D"])["Mi"] + 1.6 * esfuerzos(m, res["L"])["Mi"])


class TestParserBloques(unittest.TestCase):
    BASE = """# comentario
PROYECTO
proyecto;X
autor;

NODOS
id;x;y
1;0;0
2;1000;0
;;

MATERIALES
id;E;nu
M;210000;0,3

SECCIONES
id;tipo;d;t
S;tubo;50;3

BARRAS
id;nodo_i;nodo_j;material;seccion
1;1;2;M;S

APOYOS
nodo;uz;phix;phiy
1;1;1;1

CARGAS
caso;nodo;Pz;Mx;My
P;2;-100;0;0
"""

    def test_base_ok_con_comentarios_y_filas_vacias_de_excel(self):
        m = cargar_modelo(escribir_csv(self.BASE))
        self.assertEqual(len(m.nodos), 2)
        self.assertEqual(m.config["proyecto"], "X")

    def test_titulos_sin_importar_mayusculas_ni_tildes(self):
        t = self.BASE.replace("SECCIONES", "Secciónes").replace("APOYOS", "[apoyos]")
        cargar_modelo(escribir_csv(t))

    def test_falta_un_bloque_obligatorio(self):
        t = self.BASE.replace("SECCIONES", "# SECCIONES")
        with self.assertRaises(ErrorDeEntrada) as cm:
            cargar_modelo(escribir_csv(t))
        self.assertIn("SECCIONES", str(cm.exception))

    def test_sin_ninguna_carga_falla(self):
        t = self.BASE.replace("CARGAS", "# CARGAS")
        with self.assertRaises(ErrorDeEntrada):
            cargar_modelo(escribir_csv(t))

    def test_titulo_mal_escrito(self):
        with self.assertRaises(ErrorDeEntrada) as cm:
            cargar_modelo(escribir_csv(self.BASE.replace("BARRAS", "BARRA")))
        self.assertIn("BARRA", str(cm.exception))

    def test_bloque_repetido(self):
        with self.assertRaises(ErrorDeEntrada):
            cargar_modelo(escribir_csv(self.BASE + "\nNODOS\nid;x;y\n3;0;0\n"))

    def test_datos_antes_del_primer_titulo(self):
        with self.assertRaises(ErrorDeEntrada):
            cargar_modelo(escribir_csv("1;2;3\n" + self.BASE))

    def test_csv_con_comas_estandar(self):
        t = self.BASE.replace(";", ",").replace("210000,0,3", "210000,0.3")
        m = cargar_modelo(escribir_csv(t))
        self.assertAlmostEqual(m.materiales["M"].nu, 0.3)

    def test_columna_faltante_nombra_el_bloque(self):
        with self.assertRaises(ErrorDeEntrada) as cm:
            cargar_modelo(escribir_csv(self.BASE.replace("id;x;y", "id;x;z")))
        self.assertIn("NODOS", str(cm.exception))


class TestResortes(unittest.TestCase):
    E, nu = 210000.0, 0.3

    def test_voladizo_con_resorte_en_la_punta(self):
        """w = P / (kz + 3EI/L³) para un voladizo con resorte vertical en el extremo libre."""
        L, P, kz = 1000.0, -900.0, 350.0
        m = crear_modelo_csv([(1, 0, 0), (2, L, 0)], [(1, 2)], [(1, 1, 1, 1)], [("P", 2, P, 0, 0)],
                             resortes=[(2, kz, "", "")])
        res, _ = resolver(m)
        s = m.secciones["S"]
        w = P / (kz + 3 * self.E * s.I / L**3)
        self.assertAlmostEqual(res["P"].u[1, 0] / w, 1.0, places=9)
        self.assertAlmostEqual(res["P"].Rk[1, 0], -kz * w, places=8)
        self.assertLess(equilibrio(m, res["P"])["rel"], 1e-12)

    def test_estructura_apoyada_solo_en_resortes(self):
        nodos = [(1, 0, 0), (2, 2000, 0), (3, 2000, 1500), (4, 0, 1500)]
        m = crear_modelo_csv(nodos, [(1, 2), (2, 3), (3, 4), (4, 1)], [],
                             [("Q", 3, -1000, 2e4, 0)], resortes=[(k, 400, "", "") for k in (1, 2, 3, 4)])
        res, info = resolver(m)
        r = res["Q"]
        self.assertLess(equilibrio(m, r)["rel"], 1e-10)
        self.assertAlmostEqual(r.Rk[:, 0].sum(), 1000.0, places=6)     # los resortes sostienen toda la carga
        self.assertAlmostEqual(np.abs(r.R).max(), 0.0, places=12)      # no hay apoyos rígidos

    def test_sin_ningun_apoyo_es_error(self):
        with self.assertRaises(ErrorDeEntrada):
            crear_modelo_csv([(1, 0, 0), (2, 1000, 0)], [(1, 2)], [], [("P", 2, -1, 0, 0)])

    def test_resorte_con_apoyo_rigido_avisa(self):
        m = crear_modelo_csv([(1, 0, 0), (2, 1000, 0)], [(1, 2)], [(1, 1, 1, 1)],
                             [("P", 2, -1, 0, 0)], resortes=[(1, 100, "", "")])
        self.assertTrue(any("resorte" in a for a in m.avisos))


class TestCoeficientesDeSeguridad(unittest.TestCase):
    def test_fluencia_y_admisible(self):
        m = crear_modelo_csv([(1, 0, 0), (2, 1000, 0)], [(1, 2)], [(1, 1, 1, 1)],
                             [("P", 2, -600, 0, 0)], fy=235, sadm=156)
        res, _ = resolver(m)
        t = tensiones(m, esfuerzos(m, res["P"]))[0]
        self.assertAlmostEqual(t["n_fy"], 235 / t["vm"], places=9)
        self.assertAlmostEqual(t["n_adm"], 156 / t["vm"], places=9)

    def test_sin_datos_no_hay_coeficientes(self):
        m = crear_modelo_csv([(1, 0, 0), (2, 1000, 0)], [(1, 2)], [(1, 1, 1, 1)], [("P", 2, -600, 0, 0)])
        res, _ = resolver(m)
        t = tensiones(m, esfuerzos(m, res["P"]))[0]
        self.assertIsNone(t["n_fy"])
        self.assertIsNone(t["n_adm"])


class TestSecciones(unittest.TestCase):
    def test_tubo_y_circular_limite(self):
        d = 40.0
        t = crear_seccion("a", "tubo", {"d": d, "t": 1e-4 * d})
        # tubo delgado: J ≈ 2π r³ t,  kv → 2
        r = d / 2 - 0.5e-4 * d
        self.assertAlmostEqual(t.J / (2 * math.pi * r**3 * 1e-4 * d), 1.0, places=3)
        self.assertAlmostEqual(t.kv, 2.0, places=2)
        c = crear_seccion("b", "circular", {"d": d})
        self.assertAlmostEqual(c.J, math.pi * d**4 / 32)

    def test_rectangular_cuadrada(self):
        s = crear_seccion("r", "rectangular", {"b": 30.0, "h": 30.0})
        self.assertAlmostEqual(s.J / 30.0**4, 0.1406, delta=0.001)
        self.assertAlmostEqual(s.Wt / 30.0**3, 0.208, delta=0.001)

    def test_rect_hueca_cuadrada(self):
        s = crear_seccion("h", "rect_hueca", {"b": 50.0, "h": 50.0, "t": 3.0})
        # Bredt: J = t·(b-t)³ para sección cuadrada
        self.assertAlmostEqual(s.J, 3.0 * 47.0**3, places=6)


class TestParcialesEmparrillado(unittest.TestCase):
    """Parciales de la cátedra con giros prefijados, resorte y carga térmica."""

    def _run(self, nombre):
        m = cargar_modelo(Path(__file__).resolve().parents[1] / "003_Ejemplos" / "001_Emparrillado" / nombre)
        return m, resolver(m)[0]["C"]

    def test_parcial_1S2020_op2(self):
        m, r = self._run("ejemplo8_parcial_1S2020_giros_prefijados.csv")
        self.assertAlmostEqual(r.u[1, 0], -1.145, delta=1e-3)
        self.assertAlmostEqual(r.u[1, 1], 0.00074, delta=1e-5)

    def test_parcial_1S2021_op2(self):
        m, r = self._run("ejemplo9_parcial_1S2021_chapa_soldada.csv")
        self.assertAlmostEqual(r.u[0, 2], -0.0074, delta=1e-4)
        self.assertAlmostEqual(r.u[1, 2], -0.0054, delta=1e-4)


class TestMenuSinArgumentos(unittest.TestCase):
    def test_sin_argumentos_muestra_las_opciones(self):
        import contextlib
        import io
        from struttura.despachador import main
        for args in ([], ["-h"]):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = main(args)
            self.assertEqual(rc, 0)
            for t in ("--editor", "--soldadura", "--biblioteca", "--sin-graficos"):
                self.assertIn(t, buf.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)


class TestEstadoTotal(unittest.TestCase):
    """Sin COMBINACIONES propias y con más de un caso, el modelo agrega TOTAL = suma de todos los casos (factor 1)."""

    def test_total_automatico_en_el_3d(self):
        import tempfile
        from struttura.portico3d.entrada import cargar_modelo
        raiz = os.path.join(os.path.dirname(__file__), "..", "003_Ejemplos", "004_Portico_espacial", "ejemplo5_articulaciones_y_peso_propio.csv")
        t = open(raiz, encoding="utf-8").read().replace("SERVICIO;PP;1\nSERVICIO;P;1", "").replace("COMBINACIONES\ncombinacion;caso;factor", "")
        with tempfile.TemporaryDirectory() as d:
            f = os.path.join(d, "m.csv")
            with open(f, "w", encoding="utf-8") as h:
                h.write(t)
            m = cargar_modelo(f)
        self.assertEqual(sorted(c for c, _ in m.combinaciones["TOTAL"]), ["P", "PP"])
        self.assertTrue(all(fa == 1.0 for _, fa in m.combinaciones["TOTAL"]))


class TestValorAlPasarElMouse(unittest.TestCase):
    """Los visores de los tres códigos de dibujo traen la casilla «valor al pasar el mouse» (apagada por defecto)."""

    def test_casilla_en_los_visores(self):
        from struttura.portico3d import visor as v3
        from struttura.portico import visor2d
        from struttura.emparrillado import visor3d
        for modulo in (v3, visor2d, visor3d):
            fuente = open(modulo.__file__, encoding="utf-8").read()
            self.assertIn("valor al pasar el mouse", fuente, modulo.__name__)
            self.assertIn("hov: false", fuente, modulo.__name__)


class TestBarraSuprimida(unittest.TestCase):
    """`suprimida;1` en BARRAS: la barra sale del cálculo, queda en el archivo y se avisa con una Nota."""

    RAIZ = os.path.join(os.path.dirname(__file__), "..", "003_Ejemplos")
    CASOS = [("portico3d", "004_Portico_espacial/ejemplo2_portico_espacial.csv"),
             ("portico", "002_Portico/ejemplo4_temperatura_y_puntuales.csv"),
             ("emparrillado", "001_Emparrillado/ejemplo6_cargas_en_tramos.csv"),
             ("reticulado", "003_Reticulado/ejemplo5_cercha_con_pandeo.csv")]

    def _con_suprimida(self, ruta):
        lineas = open(ruta, encoding="utf-8").read().splitlines()
        i = next(k for k, l in enumerate(lineas) if l.strip().upper() == "BARRAS")
        j = i + 1
        lineas[j] = lineas[j] + ";suprimida"
        k = j + 1
        while k < len(lineas) and lineas[k].strip() and not lineas[k].strip().upper().isalpha() and ";" in lineas[k]:
            k += 1
        n_cols = lineas[j].count(";") + 1
        ultima = k - 1
        falt = n_cols - 1 - (lineas[ultima].count(";") + 1)
        lineas[ultima] = lineas[ultima] + ";" * (falt + 1) + "1"
        return "\n".join(lineas) + "\n", lineas[ultima].split(";")[0]

    def test_la_barra_sale_del_calculo(self):
        import importlib
        import tempfile
        for prog, rel in self.CASOS:
            ruta = os.path.join(self.RAIZ, rel)
            cargar = importlib.import_module(f"struttura.{prog}.entrada").cargar_modelo
            n0 = len(cargar(ruta).barras)
            texto, ident = self._con_suprimida(ruta)
            with tempfile.TemporaryDirectory() as d:
                f = os.path.join(d, "m.csv")
                with open(f, "w", encoding="utf-8") as h:
                    h.write(texto)
                try:
                    m = cargar(f)
                except Exception as e:                       # quitar la barra puede dejar el modelo inestable o sin cargas: eso no es lo que se prueba
                    self.fail(f"{prog}: {e}")
            self.assertEqual(len(m.barras), n0 - 1, prog)
            self.assertTrue(any(a.startswith("Nota: barras suprimidas") and ident in a for a in m.avisos), (prog, m.avisos))
