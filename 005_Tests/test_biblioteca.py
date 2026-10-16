"""Biblioteca de materiales: lectura de fichas (texto sintético con valores de PRUEBA), importación, conversión de unidades y uso en MATERIALES."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "001_Codigo"))

from struttura.biblioteca import biblioteca as bib  # noqa: E402
from struttura.biblioteca.lector_fichas import parsear  # noqa: E402
from struttura.emparrillado.entrada import ErrorDeEntrada  # noqa: E402
from struttura.portico3d.entrada import cargar_modelo  # noqa: E402

FICHA = """Searches: Advanced | Category | Property | Metals 1999
ACERO DE PRUEBA, estirado
Categories:Metal ; Ferrous Metal
Material
Notes:Ficha inventada para los tests.
Key Words: PRUEBA
Vendors: No vendors are listed for this material.
Physical
PropertiesMetric English Comments
Density 7.00 g/cc 0.253 lb/in³
Mechanical
PropertiesMetric English Comments
Tensile Strength,
Ultimate 500 MPa 72500 psi
Tensile Strength,
Yield 400 MPa 58000 psi 0.2% offset
Modulus of
Elasticity 200 GPa 29000 ksi Typical for steel
Poissons Ratio 0.30 0.30
Machinability 55 % 55 % Based on AISI 1212 steel = 100%. Group I bar.
Shear Modulus 77.0 GPa 11200 ksi
Hardness, Brinell 150 150
Elongation at
Break 15 % 15 % In 50 mm
Electrical
PropertiesMetric English Comments
Electrical
Resistivity 0.0000159 ohm-cm
@Temperature 0.000 °C0.0000159 ohm-cm
@Temperature 32.0 °Fcondition unknown
0.0000219 ohm-cm
@Temperature 100 °C0.0000219 ohm-cm
@Temperature 212 °Fcondition unknown
Thermal
PropertiesMetric English Comments
CTE, linear 
12.0 µm/m-°C
@Temperature 0.000 - 100 °C6.67 µin/in-°F
@Temperature 32.0 - 212 °F
13.0 µm/m-°C
@Temperature 0.000 - 300 °C7.22 µin/in-°F
@Temperature 32.0 - 572 °F
Component
Elements
PropertiesMetric English Comments
Carbon, C 0.10 - 0.20 % 0.10 - 0.20 %
Iron, Fe 99 - 99.5 % 99 - 99.5 % As remainder
References for this datasheet.
M9999T / 1
"""


def modelo(tmp, unidades="N;mm", extra_mat="", cab="id;lib", fila="m;1"):
    uf, ul = unidades.split(";")
    p = Path(tmp) / "m.csv"
    p.write_text(f"PROYECTO\nproyecto;x\nunidad_fuerza;{uf}\nunidad_longitud;{ul}\ntipo;portico3d\n\nNODOS\nid;x;y;z\n1;0;0;0\n2;100;0;0\n\n"
                 f"MATERIALES\n{cab}\n{fila}\n\nSECCIONES\nid;tipo;d;t\ns;tubo;40;2\n\nBARRAS\nid;nodo_i;nodo_j;material;seccion\nB;1;2;m;s\n\n"
                 "APOYOS\nnodo;ux;uy;uz;phix;phiy;phiz\n1;1;1;1;1;1;1\n\nCARGAS\ncaso;nodo;Fx;Fy;Fz;Mx;My;Mz\nc;2;0;0;-1;0;0;0\n", encoding="utf-8")
    return cargar_modelo(p)


class TestBiblioteca(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["STRUTTURA_BIBLIOTECA"] = str(Path(self.tmp) / "materiales.csv")
        (Path(self.tmp) / "ficha.txt").write_text(FICHA, encoding="utf-8")

    def tearDown(self):
        os.environ.pop("STRUTTURA_BIBLIOTECA", None)

    def test_parseo_de_la_ficha(self):
        f = parsear(FICHA)
        self.assertEqual(f["nombre"], "ACERO DE PRUEBA, estirado")
        self.assertEqual(f["ref"], "M9999T")
        P = f["propiedades"]
        self.assertEqual(P["sy"][0]["metrico"], {"valor": "400", "unidad": "MPa"})
        self.assertEqual(P["sy"][0]["comentario"], "0.2% offset")
        self.assertEqual(P["E"][0]["ingles"], {"valor": "29000", "unidad": "ksi"})
        self.assertEqual(P["alargamiento"][0]["comentario"], "In 50 mm")
        self.assertEqual([v["condicion"] for v in P["cte_lineal"][0]["valores"]], ["0.000 - 100 °C", "0.000 - 300 °C"])
        self.assertEqual([(c["elemento"], c["valor"], c["comentario"]) for c in f["composicion"]],
                         [("Carbon, C", "0.10 - 0.20 %", None), ("Iron, Fe", "99 - 99.5 %", "As remainder")])
        self.assertEqual([(v["valor"], v["condicion"]) for v in P["resistividad"][0]["valores"]], [("0.0000159", "0.000 °C"), ("0.0000219", "100 °C")])
        self.assertEqual(f["palabras_clave"], "PRUEBA")
        self.assertEqual(f["no_interpretado"], [])
        self.assertEqual(P["maquinabilidad"][0]["comentario"], "Based on AISI 1212 steel = 100%. Group I bar.")   # "= 100%" del comentario no es una propiedad

    def test_texto_desconocido_no_se_pierde(self):
        f = parsear(FICHA.replace("Shear Modulus 77.0", "Propiedad Rara 5.5 xx 9 yy\nShear Modulus 77.0"))
        self.assertTrue(any("Propiedad Rara" in x for x in f["no_interpretado"]))
        self.assertIn("Propiedad Rara", f["texto_original"])

    def test_importar_listar_datos(self):
        r, av = bib.agregar(Path(self.tmp) / "ficha.txt")
        self.assertEqual(av, [])
        self.assertEqual((r["E_MPa"], r["fy_MPa"], r["rho_kg_m3"]), ("200000", "400", "7000"))
        self.assertIn("0.2% offset", r["comentarios"])                      # los comentarios de la ficha no se pierden
        self.assertIn("0.000 - 100 °C", r["cte_lineal"])
        self.assertIn("Iron, Fe 99 - 99.5 % (As remainder)", r["composicion"])
        self.assertEqual(bib.listar(), [("1", "ACERO DE PRUEBA, estirado")])
        bib.agregar(Path(self.tmp) / "ficha.txt")                           # volver a cargar la misma ficha la actualiza, no la duplica
        self.assertEqual(len(bib.listar()), 1)
        d = bib.datos("1")
        self.assertEqual(bib.datos("m9999t")["E"], d["E"])                  # también por el código de la ficha
        self.assertEqual((d["E"], d["G"], d["nu"], d["fy"], d["sut"], d["rho"]), (200000.0, 77000.0, 0.30, 400.0, 500.0, 7000.0))
        self.assertIn("n.º 1", d["fuente"])
        
    def test_ficha_incompleta_avisa_y_no_inventa(self):
        sin_E = "\n".join(l for l in FICHA.splitlines() if "Elasticity" not in l and not l.startswith("Modulus"))
        (Path(self.tmp) / "f2.txt").write_text(sin_E.replace("Modulus of\n", ""), encoding="utf-8")
        r, av = bib.agregar(Path(self.tmp) / "f2.txt")
        self.assertTrue(any("no trae E" in a for a in av))
        self.assertIsNone(bib.datos("M9999T")["E"])

    def test_uso_en_materiales_N_mm_y_kN_cm(self):
        bib.agregar(Path(self.tmp) / "ficha.txt")
        m = modelo(self.tmp).materiales["m"]
        self.assertEqual((m.E, m.G, m.fy, m.sut, m.rho), (200000.0, 77000.0, 400.0, 500.0, 7000.0))
        self.assertIn("n.º 1", m.fuente)
        m = modelo(self.tmp, "kN;cm").materiales["m"]                       # 1 MPa = 0,1 kN/cm²
        self.assertAlmostEqual(m.E, 20000.0, 6)
        self.assertAlmostEqual(m.fy, 40.0, 9)
        self.assertEqual(m.rho, 7000.0)                                     # la densidad no cambia de unidad

    def test_numeros_permanentes(self):
        bib.agregar(Path(self.tmp) / "ficha.txt")
        (Path(self.tmp) / "f2.txt").write_text(FICHA.replace("M9999T / 1", "M8888T / 2").replace("ACERO DE PRUEBA, estirado", "OTRO ACERO"), encoding="utf-8")
        bib.agregar(Path(self.tmp) / "f2.txt")
        self.assertEqual([n for n, _ in bib.listar()], ["1", "2"])
        bib.agregar(Path(self.tmp) / "f2.txt")                              # recargar la misma ficha no cambia su número
        self.assertEqual([n for n, _ in bib.listar()], ["1", "2"])
        # borrar la fila 2 a mano y cargar otra ficha: el 2 no se reutiliza
        p = bib.archivo()
        p.write_text("\n".join(p.read_text(encoding="utf-8-sig").splitlines()[:2]) + "\n", encoding="utf-8-sig")
        (Path(self.tmp) / "f3.txt").write_text(FICHA.replace("M9999T / 1", "M7777T / 3").replace("ACERO DE PRUEBA, estirado", "TERCER ACERO"), encoding="utf-8")
        bib.agregar(Path(self.tmp) / "f3.txt")
        self.assertEqual([n for n, _ in bib.listar()], ["1", "3"])

    def test_lo_cargado_a_mano_manda(self):
        bib.agregar(Path(self.tmp) / "ficha.txt")
        m = modelo(self.tmp, cab="id;lib;fy;rho", fila="m;1;250;7850").materiales["m"]
        self.assertEqual((m.fy, m.rho, m.E), (250.0, 7850.0, 200000.0))

    def test_errores(self):
        with self.assertRaises(ErrorDeEntrada) as c:
            modelo(self.tmp, fila="m;NOEXISTE")
        self.assertIn("no está en la biblioteca", str(c.exception))
        bib.agregar(Path(self.tmp) / "ficha.txt")
        with self.assertRaises(ErrorDeEntrada):
            modelo(self.tmp, cab="id;nu", fila="m;0.3")                       # sin E ni lib

    def test_programas_planos_tambien_leen_la_biblioteca(self):
        """Pórtico plano, emparrillado y reticulado: lib completa E, nu/G y fy (en las unidades del modelo); lo escrito a mano manda."""
        from struttura.emparrillado.entrada import cargar_modelo as c_emp
        from struttura.portico.entrada import cargar_modelo as c_por
        from struttura.reticulado.entrada import cargar_modelo as c_ret
        bib.agregar(Path(self.tmp) / "ficha.txt")
        base = "PROYECTO\nproyecto;x\nunidad_fuerza;{uf}\nunidad_longitud;{ul}\ntipo;{t}\n\nNODOS\nid;x;y\n1;0;0\n2;1000;0\n\nMATERIALES\n{mat}\n\n"
        casos = {"portico": (c_por, "SECCIONES\nid;tipo;d;t\ns;tubo;40;2\n\nBARRAS\nid;nodo_i;nodo_j;material;seccion;art_i;art_j\nB;1;2;m;s;0;0\n\nAPOYOS\nnodo;ux;uy;phi\n1;1;1;1\n\nCARGAS\ncaso;nodo;Px;Py;M\nc;2;0;-1;0\n"),
                 "emparrillado": (c_emp, "SECCIONES\nid;tipo;d;t\ns;tubo;40;2\n\nBARRAS\nid;nodo_i;nodo_j;material;seccion\nB;1;2;m;s\n\nAPOYOS\nnodo;uz;phix;phiy\n1;1;1;1\n\nCARGAS\ncaso;nodo;Pz;Mx;My\nc;2;-1;0;0\n"),
                 "reticulado": (c_ret, "SECCIONES\nid;tipo;d;t\ns;tubo;40;2\n\nBARRAS\nid;nodo_i;nodo_j;material;seccion\nB;1;2;m;s\n\nAPOYOS\nnodo;ux;uy\n1;1;1\n2;0;1\n\nCARGAS\ncaso;nodo;Px;Py\nc;2;-1;0\n")}
        for t, (cargar, resto) in casos.items():
            for uf, ul, fE in (("N", "mm", 200000.0), ("kN", "cm", 20000.0)):
                f = Path(self.tmp) / f"{t}.csv"
                f.write_text(base.format(uf=uf, ul=ul, t=t, mat="id;lib\nm;1") + resto, encoding="utf-8")
                m = cargar(f).materiales["m"]
                self.assertAlmostEqual(m.E, fE, 6, t)
                self.assertAlmostEqual(m.fy, fE / 500, 6, t)
                self.assertIn("n.º 1", m.fuente)
            f.write_text(base.format(uf="N", ul="mm", t=t, mat="id;lib;fy\nm;1;250") + resto, encoding="utf-8")
            self.assertEqual(cargar(f).materiales["m"].fy, 250.0)


if __name__ == "__main__":
    unittest.main()
