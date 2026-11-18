"""Biblioteca de perfiles (tablas CIRSOC 301/302): integridad del CSV, conversión de unidades y uso en SECCIONES de los cuatro programas."""
import csv
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "001_Codigo"))

from struttura.biblioteca import perfiles as per  # noqa: E402
from struttura.biblioteca.biblioteca import ErrorBiblioteca  # noqa: E402
from struttura.emparrillado.entrada import ErrorDeEntrada, cargar_modelo as cargar_emp  # noqa: E402
from struttura.portico.entrada import cargar_modelo as cargar_plano  # noqa: E402
from struttura.portico3d.entrada import cargar_modelo as cargar_3d  # noqa: E402

FILAS = per._leer()


def n_de(ref):
    return next(r["n"] for r in FILAS if r["ref"] == ref)


def escribir(texto):
    d = tempfile.mkdtemp()
    p = Path(d) / "m.csv"
    p.write_text(texto, encoding="utf-8")
    return p


def modelo3d(seccion, uf="N", ul="mm"):
    return escribir(f"""PROYECTO
proyecto;t
tipo;portico3d
unidad_fuerza;{uf}
unidad_longitud;{ul}

NODOS
id;x;y;z
1;0;0;0
2;1000;0;0

MATERIALES
id;e;nu
a;200000;0.3

SECCIONES
{seccion}

BARRAS
id;nodo_i;nodo_j;material;seccion
B1;1;2;a;S

APOYOS
nodo;ux;uy;uz;phix;phiy;phiz
1;1;1;1;1;1;1

CARGAS
caso;nodo;Fx;Fy;Fz;Mx;My;Mz
c;2;0;0;-1;0;0;0
""")


class TestCSV(unittest.TestCase):
    def test_hay_perfiles_y_numeros_unicos(self):
        self.assertGreaterEqual(len(FILAS), 890)
        self.assertEqual(len({r["n"] for r in FILAS}), len(FILAS))
        self.assertEqual(len({r["ref"] for r in FILAS}), len(FILAS))

    def test_todos_traen_area_e_inercia_y_numeros_validos(self):
        for r in FILAS:
            for c in ("Ag_cm2", "Peso_kgm", "Ix_cm4", "Iy_cm4"):
                self.assertNotEqual(r[c], "", f"{r['ref']}: falta {c}")
            for c, v in r.items():
                if c.endswith(("_mm", "_cm", "_cm2", "_cm3", "_cm4", "_cm6", "_kgm", "_MPa")) and v:
                    float(v)

    def test_valores_de_las_tablas(self):               # valores copiados del PDF
        r = next(x for x in FILAS if x["ref"] == "IPE 200")
        self.assertEqual((r["d_mm"], r["b_mm"], r["Ag_cm2"], r["Ix_cm4"], r["Iy_cm4"]), ("200", "100", "28.5", "1940", "142"))
        r = next(x for x in FILAS if x["ref"] == "UPN 200")
        self.assertEqual((r["Ag_cm2"], r["Ix_cm4"], r["Iy_cm4"]), ("32.2", "1910", "148"))

    def test_incoherencias_de_la_fuente_marcadas(self):
        obs = {r["ref"]: r["observaciones"] for r in FILAS if r["observaciones"]}
        self.assertEqual(set(obs), {"IPBv 320", "UPN 50"})

    def test_familias(self):
        fam = {r["familia"] for r in FILAS}
        self.assertEqual(fam, {"IPN", "IPB", "IPBl", "IPBv", "IPE", "W", "HP", "M", "UPN", "C", "MC", "L", "T", "TC", "TQ", "TR"})


class TestUnidades(unittest.TestCase):
    def test_conversion(self):
        n = n_de("IPE 200")
        mm, _, _ = per.datos_modelo(n, "3d", "mm")
        cm, _, _ = per.datos_modelo(n, "3d", "cm")
        m, _, _ = per.datos_modelo(n, "3d", "m")
        self.assertAlmostEqual(mm["a"], 2850.0)
        self.assertAlmostEqual(mm["iy"], 1.94e7)
        self.assertAlmostEqual(cm["a"], 28.5)
        self.assertAlmostEqual(cm["iy"], 1940.0)
        self.assertAlmostEqual(m["a"], 28.5e-4)
        self.assertAlmostEqual(m["iz"], 142e-8)
        self.assertAlmostEqual(mm["cz"], 100.0)
        self.assertAlmostEqual(mm["cy"], 50.0)
        pul, _, _ = per.datos_modelo(n, "3d", "in")
        self.assertAlmostEqual(pul["a"] * 25.4 ** 2, 2850.0)
        self.assertAlmostEqual(pul["iy"] * 25.4 ** 4, 1.94e7, delta=1)

    def test_unidad_desconocida(self):
        with self.assertRaises(ErrorBiblioteca):
            per.datos_modelo(n_de("IPE 200"), "3d", "furlong")

    def test_perfil_inexistente(self):
        with self.assertRaises(ErrorBiblioteca):
            per.cargar("99999")

    def test_ejes_de_te_y_canal(self):
        t = per.datos_modelo(n_de("T 51 x 51 x 6,4"), "3d", "mm")[0]
        self.assertAlmostEqual(t["cz"], 51 - 14.4)                    # dx = 1,44 cm desde el ala: la fibra más lejana es la punta del alma
        c = per.datos_modelo(n_de("UPN 200"), "3d", "mm")[0]
        r = next(x for x in FILAS if x["ref"] == "UPN 200")
        e = float(r["ey_cm"]) * 10
        self.assertAlmostEqual(c["cy"], max(e, 75 - e))

    def test_tubo_trae_wt(self):
        d = per.datos_modelo(n_de("TC 38.1 x 2.5"), "3d", "mm")[0]
        self.assertAlmostEqual(d["wt"], 4670.0)
        self.assertAlmostEqual(d["j"], 89000.0)


class TestEnLosProgramas(unittest.TestCase):
    def test_3d_igual_que_generica_a_mano(self):
        n = n_de("IPE 200")
        a = cargar_3d(modelo3d(f"id;tipo;lib\nS;perfil;{n}")).secciones["S"]
        b = cargar_3d(modelo3d("id;tipo;a;iy;iz;j;cy;cz\nS;generica;2850;19400000;1420000;51700;50;100")).secciones["S"]
        for c in ("A", "Iy", "Iz", "J", "cy", "cz"):
            self.assertAlmostEqual(getattr(a, c), getattr(b, c), places=6, msg=c)
        self.assertIn("IPE 200", a.descripcion)

    def test_3d_lo_escrito_a_mano_manda(self):
        n = n_de("IPE 200")
        a = cargar_3d(modelo3d(f"id;tipo;lib;j\nS;perfil;{n};99999")).secciones["S"]
        self.assertAlmostEqual(a.J, 99999.0)
        self.assertAlmostEqual(a.A, 2850.0)

    def test_3d_en_centimetros(self):
        n = n_de("IPE 200")
        a = cargar_3d(modelo3d(f"id;tipo;lib\nS;perfil;{n}", "kN", "cm")).secciones["S"]
        self.assertAlmostEqual(a.A, 28.5)
        self.assertAlmostEqual(a.Iy, 1940.0)

    def test_3d_sin_lib(self):
        with self.assertRaises(ErrorDeEntrada):
            cargar_3d(modelo3d("id;tipo;lib\nS;perfil;"))

    def test_3d_perfil_inexistente(self):
        with self.assertRaises(ErrorDeEntrada):
            cargar_3d(modelo3d("id;tipo;lib\nS;perfil;99999"))

    def test_3d_angulo_avisa(self):
        n = n_de("L 51 x 51 x 6,4")
        m = cargar_3d(modelo3d(f"id;tipo;lib\nS;perfil;{n}"))
        self.assertTrue(any("ángulo" in a for a in m.avisos))

    def test_plano_y_reticulado(self):
        n = n_de("IPE 200")
        txt = f"""PROYECTO
proyecto;t
tipo;portico
unidad_fuerza;N
unidad_longitud;mm

NODOS
id;x;y
1;0;0
2;1000;0

MATERIALES
id;e
a;200000

SECCIONES
id;tipo;lib
S;perfil;{n}

BARRAS
id;nodo_i;nodo_j;material;seccion
B1;1;2;a;S

APOYOS
nodo;ux;uy;phi
1;1;1;1

CARGAS
caso;nodo;Px;Py;M
c;2;0;-1;0
"""
        s = cargar_plano(escribir(txt)).secciones["S"]
        self.assertAlmostEqual(s.A, 2850.0)
        self.assertAlmostEqual(s.I, 1.94e7)
        self.assertAlmostEqual(s.c, 100.0)
        from struttura.reticulado.entrada import cargar_modelo as cargar_ret
        ret = txt.replace("tipo;portico", "tipo;reticulado").replace("nodo;ux;uy;phi\n1;1;1;1", "nodo;ux;uy\n1;1;1").replace("caso;nodo;Px;Py;M\nc;2;0;-1;0", "caso;nodo;Px;Py\nc;2;0;-1")
        s2 = cargar_ret(escribir(ret)).secciones["S"]
        self.assertAlmostEqual(s2.A, 2850.0)

    def test_emparrillado(self):
        n = n_de("TC 38.1 x 2.5")
        txt = f"""PROYECTO
proyecto;t
tipo;emparrillado
unidad_fuerza;N
unidad_longitud;mm

NODOS
id;x;y
1;0;0
2;1000;0

MATERIALES
id;e;g
a;200000;77000

SECCIONES
id;tipo;lib
S;perfil;{n}

BARRAS
id;nodo_i;nodo_j;material;seccion
B1;1;2;a;S

APOYOS
nodo;uz;phix;phiy
1;1;1;1

CARGAS
caso;nodo;Pz;Mx;My
c;2;-1;0;0
"""
        s = cargar_emp(escribir(txt)).secciones["S"]
        self.assertAlmostEqual(s.I, 44500.0)
        self.assertAlmostEqual(s.J, 89000.0)
        self.assertAlmostEqual(s.Wt, 4670.0)


class TestNotas(unittest.TestCase):
    def test_material_de_biblioteca_es_nota_no_aviso(self):
        from struttura.biblioteca import biblioteca as bib
        if not bib.archivo().is_file():
            self.skipTest("no hay biblioteca de materiales")
        n = bib.listar()[0][0]
        t = modelo3d("id;tipo;lib\nS;perfil;" + n_de("IPE 200")).read_text(encoding="utf-8").replace("id;e;nu\na;200000;0.3", f"id;lib\na;{n}")
        m = cargar_3d(escribir(t))
        mat = [a for a in m.avisos if "biblioteca" in a and "Material" in a]
        self.assertTrue(mat and all(a.startswith("Nota: ") for a in mat))


if __name__ == "__main__":
    unittest.main()
