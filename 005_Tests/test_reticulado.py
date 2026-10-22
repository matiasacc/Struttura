"""Tests del programa de reticulado plano (unittest)."""
import math
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "001_Codigo"))

from struttura.despachador import detectar_tipo  # noqa: E402
from struttura.portico.entrada import ErrorDeEntrada  # noqa: E402
from struttura.portico.solver import equilibrio, resolver  # noqa: E402
from struttura.reticulado.analisis import carga_critica, verificar_barras  # noqa: E402
from struttura.reticulado.entrada import cargar_modelo  # noqa: E402

EJ = RAIZ / "003_Ejemplos" / "003_Reticulado"


def cabecera_tabla(extra=""):
    return f"""PROYECTO
tipo;reticulado

NODOS
id;x;y
1;0;0
2;4000;0
3;2000;1500

MATERIALES
id;E;fy
m;210000;235

SECCIONES
id;tipo;d;t
t;tubo;60.3;3.2

BARRAS
id;nodo_i;nodo_j;material;seccion{extra}
1;1;2;m;t
2;1;3;m;t
3;2;3;m;t

APOYOS
nodo;ux;uy
1;1;1
2;0;1

CARGAS
caso;nodo;Px;Py
P;3;0;-10000
"""


def escribir(texto):
    d = tempfile.mkdtemp()
    p = Path(d) / "t.csv"
    p.write_text(texto, encoding="utf-8")
    return p


class TestReticulado(unittest.TestCase):
    def _sol(self, nombre, caso="P"):
        m = cargar_modelo(EJ / nombre)
        return m, resolver(m)[0][caso]

    def test_brewer_1_carga_nodal(self):
        m, r = self._sol("ejemplo1_brewer_carga_nodal.csv")
        self.assertAlmostEqual(r.u[3, 0], 0.055, delta=5e-4)
        self.assertTrue(np.allclose([d["N"] for d in verificar_barras(m, r)], [1732.1, 1385.6, 1039.2], atol=0.2))
        self.assertAlmostEqual(r.R[3, 1], 3663, delta=1)

    def test_brewer_2_desplazamiento_prefijado(self):
        m, r = self._sol("ejemplo2_brewer_desplazamiento_prefijado.csv")
        self.assertAlmostEqual(r.u[3, 0], 0.0742, delta=5e-5)
        self.assertTrue(np.allclose([d["N"] for d in verificar_barras(m, r)], [2337, 357, 1402], atol=1))
        self.assertAlmostEqual(r.R[3, 1], 3336, delta=1)

    def test_brewer_3_barra_corta_y_temperatura(self):
        m, r = self._sol("ejemplo3_brewer_barra_corta_y_temperatura.csv")
        self.assertAlmostEqual(r.u[1, 0], -5.540e-3, delta=1e-5)
        N = [d["N"] for d in verificar_barras(m, r)]
        self.assertTrue(np.allclose(N, [469, 0, -1519], atol=1.5))
        self.assertAlmostEqual(r.R[0, 0], -1518.7, delta=0.5)
        self.assertAlmostEqual(r.R[1, 1], 2775.2, delta=0.5)
        self.assertAlmostEqual(r.R[3, 0], -281.4, delta=0.5)
        self.assertAlmostEqual(r.R[3, 1], -375.2, delta=0.5)

    def test_brewer_4_resorte_barra_larga_temperatura(self):
        m, r = self._sol("ejemplo4_brewer_resorte_barra_larga_temperatura.csv")
        self.assertAlmostEqual(r.u[2, 0], 0.1188, delta=2e-4)
        self.assertAlmostEqual(r.u[2, 1], -0.0558, delta=2e-4)
        N = [d["N"] for d in verificar_barras(m, r)]
        self.assertTrue(np.allclose(N[1:3], [1108.8, -781.2], atol=1.5))
        self.assertAlmostEqual(N[3], 2344.2, delta=3)
        self.assertAlmostEqual(N[4], 528.11 - 777.8, delta=1)      # el libro imprime -259.9 (error de cuenta: 528,11 - 777,8 = -249,7)
        self.assertAlmostEqual(r.Rk[2, 1], 279, delta=1)
        self.assertAlmostEqual(r.R[3, 0], 1948.2, delta=1.5)

    def test_barra_corta_larga_signos(self):
        """Barra entre dos apoyos fijos: corta (hay que estirarla) → tracción E·A·e/L; larga → compresión.  Isostática: sin esfuerzo."""
        t = """PROYECTO
tipo;reticulado

NODOS
id;x;y
1;0;0
2;1000;0

MATERIALES
id;E
m;200000

SECCIONES
id;tipo;A
s;generica;100

BARRAS
id;nodo_i;nodo_j;material;seccion
1;1;2;m;s

APOYOS
nodo;ux;uy
1;1;1
2;1;1

CARGAS EN BARRAS
caso;barra;tipo;valor
X;1;{t};0.5
"""
        for tp, sg in (("corta", 1), ("larga", -1)):
            m = cargar_modelo(escribir(t.format(t=tp)))
            r = resolver(m)[0]["X"]
            self.assertAlmostEqual(verificar_barras(m, r)[0]["N"], sg * 200000 * 100 * 0.5 / 1000, places=6)
        m = cargar_modelo(escribir(cabecera_tabla() + "\nCARGAS EN BARRAS\ncaso;barra;tipo;valor\nX;2;corta;0.5\n"))
        self.assertAlmostEqual(verificar_barras(m, resolver(m)[0]["X"])[1]["N"], 0.0, places=8)   # isostática

    def test_triangulo_estatica(self):
        m = cargar_modelo(escribir(cabecera_tabla()))
        r = resolver(m)[0]["P"]
        # carga en el vértice, simétrica: reacciones 5000; N en las diagonales = -5000/sen(a)
        self.assertAlmostEqual(r.R[0, 1], 5000, places=6)
        self.assertAlmostEqual(r.R[1, 1], 5000, places=6)
        L = math.hypot(2000, 1500)
        vb = verificar_barras(m, r)
        self.assertAlmostEqual(vb[1]["N"], -5000 * L / 1500, places=4)
        self.assertAlmostEqual(vb[0]["N"], 5000 * 2000 / 1500, places=4)      # tirante
        self.assertLess(equilibrio(m, r)["rel"], 1e-12)

    def test_solver_independiente_2gdl(self):
        """Ensamblado directo con la tabla de la cátedra (γ1²K, γ1γ2K, γ2²K) contra el resultado del programa."""
        m = cargar_modelo(EJ / "ejemplo5_cercha_con_pandeo.csv")
        res = resolver(m)[0]["TOTAL"]
        n = m.n
        K = np.zeros((2 * n, 2 * n))
        for b in m.barras:
            k = b.mat.E * b.sec.A / b.L
            g1, g2 = b.g1, b.g2
            a = np.array([-g1, -g2, g1, g2])
            ke = k * np.outer(a, a)
            d = [2 * b.i, 2 * b.i + 1, 2 * b.j, 2 * b.j + 1]
            K[np.ix_(d, d)] += ke
        F = np.zeros(2 * n)
        for c in ("V", "W"):
            F += m.casos[c][:, :2].reshape(-1)
        fix = m.restr[:, :2].reshape(-1)
        lib = ~fix
        u = np.zeros(2 * n)
        u[lib] = np.linalg.solve(K[np.ix_(lib, lib)], F[lib])
        self.assertTrue(np.allclose(u, res.u[:, :2].reshape(-1), rtol=1e-9, atol=1e-12))

    def test_pandeo_tabla_catedra(self):
        E, I, L = 210000.0, 1.0e6, 3000.0
        base = math.pi ** 2 * E * I / L ** 2
        self.assertAlmostEqual(carga_critica(E, I, L, "art-art"), base)
        self.assertAlmostEqual(carga_critica(E, I, L, "emp-lib"), base / 4)
        self.assertAlmostEqual(carga_critica(E, I, L, "emp-art"), 2 * base)
        self.assertAlmostEqual(carga_critica(E, I, L, "emp-emp"), 4 * base)

    def test_cs_pandeo_en_barra_comprimida(self):
        m = cargar_modelo(EJ / "ejemplo5_cercha_con_pandeo.csv")
        r = resolver(m)[0]["V"]
        vb = verificar_barras(m, r)
        b4 = vb[3]
        self.assertAlmostEqual(b4["N"], -16000, delta=1e-6)
        self.assertAlmostEqual(b4["n_pand"], b4["Pc"] / 16000, places=9)
        self.assertIsNone(vb[0]["n_pand"])                  # tirante traccionado: sin pandeo

    def test_condicion_de_vinculo_cambia_pc(self):
        m1 = cargar_modelo(escribir(cabecera_tabla()))
        m2 = cargar_modelo(escribir(cabecera_tabla(";pandeo").replace("1;1;2;m;t", "1;1;2;m;t;emp-emp")
                                    .replace("2;1;3;m;t", "2;1;3;m;t;emp-emp").replace("3;2;3;m;t", "3;2;3;m;t;emp-emp")))
        v1 = verificar_barras(m1, resolver(m1)[0]["P"])
        v2 = verificar_barras(m2, resolver(m2)[0]["P"])
        self.assertAlmostEqual(v2[1]["Pc"] / v1[1]["Pc"], 4.0, places=9)

    def test_resorte_inclinado_y_prefijado(self):
        t = cabecera_tabla() + """
RESORTES INCLINADOS
nodo;k;angulo
3;500;90

DESPLAZAMIENTOS PREFIJADOS
caso;nodo;ux;uy
S;2;0;-2
"""
        m = cargar_modelo(escribir(t))
        res = resolver(m)
        for r in res[0].values():
            self.assertLess(equilibrio(m, r)["rel"], 1e-10)
        self.assertAlmostEqual(res[0]["S"].u[1, 1], -2.0)

    def test_errores(self):
        with self.assertRaises(ErrorDeEntrada):                       # columna phi en APOYOS
            cargar_modelo(escribir(cabecera_tabla().replace("nodo;ux;uy\n1;1;1\n2;0;1", "nodo;ux;uy;phi\n1;1;1;1\n2;0;1;0")))
        for tipo in ("q", "qa", "P", "Pa", "qgy"):                    # las barras son bielas: sin carga en el tramo
            with self.assertRaises(ErrorDeEntrada, msg=tipo):
                cargar_modelo(escribir(cabecera_tabla() + f"\nCARGAS EN BARRAS\ncaso;barra;tipo;valor;valor2;a;b\nP;1;{tipo};1;1;0;4000\n"))
        with self.assertRaises(ErrorDeEntrada):                       # e negativo: usar corta/larga con número positivo
            cargar_modelo(escribir(cabecera_tabla() + "\nCARGAS EN BARRAS\ncaso;barra;tipo;valor\nP;1;corta;-1\n"))
        with self.assertRaises(ErrorDeEntrada):                       # vínculo de pandeo inexistente
            cargar_modelo(escribir(cabecera_tabla(";pandeo").replace("1;1;2;m;t", "1;1;2;m;t;xx")))
        with self.assertRaises(ErrorDeEntrada):
            cargar_modelo(escribir(cabecera_tabla(";art_i")))

    def test_deteccion_de_tipo(self):
        self.assertEqual(detectar_tipo(EJ / "ejemplo1_brewer_carga_nodal.csv"), "reticulado")
        t = cabecera_tabla().replace("tipo;reticulado\n", "")
        self.assertEqual(detectar_tipo(escribir(t)), "reticulado")

    def test_lineas_de_error_son_del_archivo_original(self):
        t = cabecera_tabla().replace("1;1;2;m;t", "1;1;9;m;t")
        with self.assertRaises(ErrorDeEntrada) as cm:
            cargar_modelo(escribir(t))
        self.assertIn("línea 20", str(cm.exception))


class TestVisorSoloAxil(unittest.TestCase):
    def test_el_visor_del_reticulado_no_trae_corte_ni_flector(self):
        import re
        import subprocess
        raiz = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as d:
            subprocess.run([sys.executable, str(raiz / "struttura.py"), str(raiz / "003_Ejemplos" / "003_Reticulado" / "ejemplo1_brewer_carga_nodal.csv"), "-o", d],
                           capture_output=True, check=True)
            h = (Path(d) / "informe.html").read_text(encoding="utf-8")
        self.assertIn('"dia": {"N"', h)
        self.assertFalse(re.search(r'"dia": \{[^{]*?"V":', h))


if __name__ == "__main__":
    unittest.main()


class TestGraficosResortes(unittest.TestCase):
    def test_esquema_con_todos_los_resortes(self):
        from struttura.portico import graficos
        from struttura.portico.entrada import cargar_modelo as cp
        m = cp(RAIZ / "003_Ejemplos" / "002_Portico" / "ejemplo9_todos_los_resortes.csv")
        svg = graficos.fig_esquema(m)
        self.assertIn("resorte", svg.lower())
        m2 = cargar_modelo(EJ / "ejemplo5_cercha_con_pandeo.csv")
        self.assertNotIn("articulación", graficos.fig_esquema(m2))
