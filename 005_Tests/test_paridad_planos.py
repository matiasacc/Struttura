"""Paridad entre los 4 programas: peso propio (peso_propio / gravedad / rho) y modo Utilización de los visores planos."""
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "001_Codigo"))

from struttura.emparrillado.entrada import ErrorDeEntrada, cargar_modelo as c_emp  # noqa: E402
from struttura.emparrillado.barra import parsear_articulacion  # noqa: E402
from struttura.emparrillado.solver import resolver as resolver_emp  # noqa: E402
from struttura.portico.entrada import cargar_modelo as c_por  # noqa: E402
from struttura.reticulado.entrada import cargar_modelo as c_ret  # noqa: E402

A = math.pi * (20 ** 2 - 18 ** 2)                       # tubo 40 x 2 [mm²]
PESO = 7850 * 9.80665 * A * 1000 * 1e-9                 # N, barra de 1000 mm
PROY = "PROYECTO\nproyecto;x\nunidad_fuerza;N\nunidad_longitud;mm\ntipo;{t}\n{extra}\nNODOS\nid;x;y\n1;0;0\n2;1000;0\n\nMATERIALES\nid;E;nu;fy;sadm;rho\nm;200000;0.3;235;140;7850\n\nSECCIONES\nid;tipo;d;t\ns;tubo;40;2\n\n"
RESTO = {"portico": "BARRAS\nid;nodo_i;nodo_j;material;seccion;art_i;art_j\nB;1;2;m;s;0;0\n\nAPOYOS\nnodo;ux;uy;phi\n1;1;1;1\n\nCARGAS\ncaso;nodo;Px;Py;M\nc;2;0;-100;0\n",
         "emparrillado": "BARRAS\nid;nodo_i;nodo_j;material;seccion\nB;1;2;m;s\n\nAPOYOS\nnodo;uz;phix;phiy\n1;1;1;1\n\nCARGAS\ncaso;nodo;Pz;Mx;My\nc;2;-100;0;0\n",
         "reticulado": "BARRAS\nid;nodo_i;nodo_j;material;seccion\nB;1;2;m;s\n\nAPOYOS\nnodo;ux;uy\n1;1;1\n2;0;1\n\nCARGAS\ncaso;nodo;Px;Py\nc;2;0;-1\n"}
CARGAR = {"portico": c_por, "emparrillado": c_emp, "reticulado": c_ret}


def modelo(tipo, extra, tmp):
    f = Path(tmp) / f"{tipo}.csv"
    f.write_text(PROY.format(t=tipo, extra=extra) + RESTO[tipo], encoding="utf-8")
    return CARGAR[tipo](f)


class TestPesoPropio(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def test_sin_peso_propio_no_se_agrega_nada(self):
        for t in CARGAR:
            m = modelo(t, "", self.tmp)
            self.assertIsNone(m.peso_propio)
            self.assertFalse(m.cargas_barra)

    def test_peso_total_y_masa(self):
        for t in CARGAR:
            pp = modelo(t, "peso_propio;PP\n", self.tmp).peso_propio
            self.assertAlmostEqual(pp["peso"], PESO, 9, t)
            self.assertAlmostEqual(pp["masa"], 7850 * A * 1000 * 1e-9, 9, t)

    def test_portico_y_emparrillado_distribuida(self):
        m = modelo("portico", "peso_propio;PP\n", self.tmp)
        c = m.cargas_barra["PP"][0]
        self.assertAlmostEqual(c.v1, -PESO / 1000, 12)                       # -ρ g A por mm, gravedad -y
        m = modelo("emparrillado", "peso_propio;PP\n", self.tmp)
        self.assertAlmostEqual(m.cargas_barra["PP"][0].v1, -PESO / 1000, 12)  # q en z, gravedad -z
        m = modelo("portico", "peso_propio;PP\ngravedad;+y\n", self.tmp)
        self.assertAlmostEqual(m.cargas_barra["PP"][0].v1, PESO / 1000, 12)

    def test_reticulado_mitad_en_cada_nudo(self):
        m = modelo("reticulado", "peso_propio;PP\n", self.tmp)
        F = m.casos["PP"]
        self.assertAlmostEqual(F[0, 1], -PESO / 2, 9)
        self.assertAlmostEqual(F[1, 1], -PESO / 2, 9)
        self.assertEqual(F[:, 0].tolist(), [0.0, 0.0])
        self.assertFalse(m.cargas_barra.get("PP"))                           # una biela no lleva carga en el tramo

    def test_errores(self):
        with self.assertRaises(ErrorDeEntrada):
            modelo("emparrillado", "peso_propio;PP\ngravedad;-x\n", self.tmp)    # el emparrillado solo ±z
        with self.assertRaises(ErrorDeEntrada):
            modelo("portico", "peso_propio;PP\ngravedad;-z\n", self.tmp)         # el pórtico plano solo ±x, ±y
        f = Path(self.tmp) / "sin_rho.csv"
        f.write_text((PROY.format(t="portico", extra="peso_propio;PP\n") + RESTO["portico"]).replace(";rho\nm;200000;0.3;235;140;7850", "\nm;200000;0.3;235;140"), encoding="utf-8")
        with self.assertRaises(ErrorDeEntrada) as c:
            c_por(f)
        self.assertIn("rho", str(c.exception))


class TestColumnasDesconocidas(unittest.TestCase):
    def test_aviso_en_los_tres_programas(self):
        tmp = tempfile.mkdtemp()
        for t in CARGAR:
            f = Path(tmp) / f"{t}.csv"
            f.write_text((PROY.format(t=t, extra="") + RESTO[t]).replace("id;E;nu;fy;sadm;rho", "id;E;nu;fy;sadm;rho;fyy").replace("m;200000;0.3;235;140;7850", "m;200000;0.3;235;140;7850;1"), encoding="utf-8")
            avisos = CARGAR[t](f).avisos
            self.assertTrue(any("'fyy' no se usa" in a for a in avisos), t)
            f.write_text(PROY.format(t=t, extra="") + RESTO[t], encoding="utf-8")
            self.assertFalse(any("no se usa" in a for a in CARGAR[t](f).avisos), t)


class TestUtilizacionPlanos(unittest.TestCase):
    def test_datos_del_visor(self):
        """Cada escena trae σeq en 21 puntos por barra y el visor recibe fy y σadm: de ahí salen σ/fy y σ/σadm."""
        from struttura.portico.solver import resolver
        from struttura.portico import visor2d
        tmp = tempfile.mkdtemp()
        m = modelo("portico", "", tmp)
        res, _ = resolver(m)
        html = visor2d.visor_html(m, [{"nombre": "c", "F": m.casos["c"], "cb": [], "res": res["c"]}], "v")
        D = json.loads(html.split('emp2d("v", ', 1)[1].rsplit(");</script>", 1)[0])
        self.assertEqual(D["fy"], [235.0])
        self.assertEqual(D["sadm"], [140.0])
        vm = D["escenas"][0]["vm"][0]
        self.assertEqual(len(vm), 21)
        # voladizo con P en la punta: σ máxima = P·L·c/I en el empotramiento (nudo 1)
        I = math.pi / 64 * (40 ** 4 - 36 ** 4)
        self.assertAlmostEqual(vm[0], 100 * 1000 * 20 / I, 6)
        self.assertLess(vm[-1], 0.05 * vm[0])                                # en la punta solo queda el corte (σeq = √3·τ)


BASE_ART = """PROYECTO
proyecto;art
unidad_fuerza;N
unidad_longitud;mm

NODOS
id;x;y
1;0;0
2;1000;0
3;2000;0

MATERIALES
id;E;nu
A;210000;0,3

SECCIONES
id;tipo;d;t
T1;tubo;50;3

BARRAS
id;nodo_i;nodo_j;material;seccion;art_i;art_j
1;1;2;A;T1;;
2;2;3;A;T1;{a2i};{a2j}

APOYOS
nodo;uz;phix;phiy
1;1;1;1
{apoyo3}

CARGAS EN BARRAS
caso;barra;tipo;valor
q;1;q;-1
q;2;q;{q2}
"""


class TestArticulacionesEmparrillado(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def _m(self, a2i="m", a2j="", apoyo3="3;1;1;0", q2="-1"):
        f = Path(self.tmp) / "a.csv"
        f.write_text(BASE_ART.format(a2i=a2i, a2j=a2j, apoyo3=apoyo3, q2=q2), encoding="utf-8")
        return c_emp(f)

    def test_flexion_articulada_momento_nulo_y_equilibrio(self):
        m = self._m()
        res, _ = resolver_emp(m)
        r = res["q"]
        self.assertAlmostEqual(r.fb[1][2], 0.0, 6)                         # M = 0 en la rótula
        self.assertAlmostEqual(r.R[2][0], 500.0, 6)                        # apoyo simple: q·L/2
        self.assertAlmostEqual(r.fb[0][0], 1500.0, 6)                      # corte en el empotramiento
        self.assertAlmostEqual(r.fb[0][2], -1e6, 3)                        # momento en el empotramiento
        self.assertAlmostEqual(r.R[:, 0].sum(), 2000.0, 6)

    def test_sin_articulacion_distinto(self):
        r1 = resolver_emp(self._m(a2i=""))[0]["q"]
        self.assertGreater(abs(r1.fb[1][2]), 1.0)

    def test_torsion_articulada(self):
        self.assertEqual(parsear_articulacion("t"), "t")
        self.assertEqual(parsear_articulacion("m+t"), "mt")
        self.assertEqual(parsear_articulacion("1"), "m")
        self.assertEqual(parsear_articulacion(""), "")
        self.assertIsNone(parsear_articulacion("z"))
        m = self._m(a2i="t", apoyo3="3;1;1;1")
        self.assertEqual(m.barras[1].rel, [1])
        res, _ = resolver_emp(m)
        self.assertAlmostEqual(res["q"].fb[1][1], 0.0, 6)                  # T = 0 en la rótula de torsión

    def test_valor_invalido(self):
        with self.assertRaises(ErrorDeEntrada):
            self._m(a2i="zz")

    def test_giro_sin_rigidez_se_estabiliza_y_avisa(self):
        m = self._m(a2i="", a2j="mt", apoyo3="", q2="0")
        self.assertTrue(any("sin rigidez" in a for a in m.avisos))
        self.assertEqual(sum("Nodo 3" in a for a in m.avisos), 1)
        res, _ = resolver_emp(m)
        self.assertAlmostEqual(res["q"].fb[1][2], 0.0, 6)


class TestDiagramasEmparrillado(unittest.TestCase):
    def test_datos_de_diagramas_en_el_visor(self):
        from struttura.emparrillado import visor3d
        tmp = tempfile.mkdtemp()
        f = Path(tmp) / "e.csv"
        f.write_text(PROY.format(t="emparrillado", extra="") + RESTO["emparrillado"], encoding="utf-8")
        m = c_emp(f)
        res, _ = resolver_emp(m)
        html = visor3d.visor_html(m, [{"nombre": "c", "F": m.casos["c"], "cb": [], "res": res["c"]}], "v")
        D = json.loads(html.split('emp3d("v", ', 1)[1].rsplit(");</script>", 1)[0])
        dia = D["escenas"][0]["dia"]
        self.assertEqual(set(dia), {"V", "T", "M"})
        self.assertEqual(D["art"], [["", ""]])


SEC_TUBO = "SECCIONES\nid;tipo;d;t\nT;tubo;50;3\n"


def _txt(tipo, extra_mat="", sec=SEC_TUBO, barras_extra="", cargas=None, bloques_extra=""):
    if tipo == "portico":
        return ("PROYECTO\nproyecto;x\nunidad_fuerza;N\nunidad_longitud;mm\ntipo;portico\nNODOS\nid;x;y\n1;0;0\n2;1000;0\n"
                f"MATERIALES\nid;E;nu;fy;sut;suc;teoria\nA;210000;0,3;235;{extra_mat}\n{sec}"
                f"BARRAS\nid;nodo_i;nodo_j;material;seccion{barras_extra}\n1;1;2;A;T{'' if not barras_extra else ';;;emp-lib'}\n"
                "APOYOS\nnodo;ux;uy;phi\n1;1;1;1\nCARGAS\ncaso;nodo;Px;Py;M\nc;2;" + (cargas or "0;-500;0") + "\n" + bloques_extra)
    return ("PROYECTO\nproyecto;x\nunidad_fuerza;N\nunidad_longitud;mm\ntipo;emparrillado\nNODOS\nid;x;y\n1;0;0\n2;1000;0\n"
            f"MATERIALES\nid;E;nu;fy;sut;suc;teoria\nA;210000;0,3;235;{extra_mat}\n{sec}"
            "BARRAS\nid;nodo_i;nodo_j;material;seccion\n1;1;2;A;T\nAPOYOS\nnodo;uz;phix;phiy\n1;1;1;1\nCARGAS\ncaso;nodo;Pz;Mx;My\nc;2;" + (cargas or "-500;0;0") + "\n" + bloques_extra)


class TestFallaPandeoParedSoldadura(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def _cargar(self, tipo, txt):
        f = Path(self.tmp) / f"{tipo}.csv"
        f.write_text(txt, encoding="utf-8")
        return CARGAR[tipo](f)

    def test_teoria_por_defecto_es_von_mises_y_tresca_es_mayor(self):
        from struttura.portico.esfuerzos import esfuerzos as ep, tensiones as tp
        from struttura.portico.solver import resolver as rp
        vm = self._cargar("portico", _txt("portico", ";;"))
        tr = self._cargar("portico", _txt("portico", ";;").replace("A;210000;0,3;235;;;", "A;210000;0,3;235;;;tresca"))
        self.assertEqual(vm.materiales["A"].teoria, "vm")
        a = tp(vm, ep(vm, rp(vm)[0]["c"]["res"] if False else rp(vm)[0]["c"]))[0]
        b = tp(tr, ep(tr, rp(tr)[0]["c"]))[0]
        self.assertGreaterEqual(b["vm"], a["vm"] - 1e-9)                  # σTresca ≥ σVM
        self.assertEqual(b["teoria"], "tresca")

    def test_teoria_invalida_y_faltante(self):
        with self.assertRaises(ErrorDeEntrada):
            self._cargar("emparrillado", _txt("emparrillado", ";;").replace("A;210000;0,3;235;;;", "A;210000;0,3;235;;;inventada"))
        with self.assertRaises(ErrorDeEntrada):                           # rankine necesita sut
            self._cargar("portico", _txt("portico", ";;").replace("A;210000;0,3;235;;;", "A;210000;0,3;235;;;rankine"))

    def test_mohr_modificado_en_emparrillado(self):
        from struttura.emparrillado.esfuerzos import esfuerzos as ee, tensiones as te
        from struttura.emparrillado.solver import resolver as re_
        m = self._cargar("emparrillado", _txt("emparrillado", ";;").replace("A;210000;0,3;235;;;", "A;100000;0,26;;200;750;mohrmod"))
        t = te(m, ee(m, re_(m)[0]["c"]))[0]
        self.assertEqual(t["teoria"], "mohrmod")
        self.assertIsNotNone(t["n_fy"])                                   # CS de la teoría (sut/σ*)

    def test_pandeo_voladizo_euler(self):
        from struttura.portico.esfuerzos import esfuerzos as ep, tensiones as tp
        from struttura.portico.solver import resolver as rp
        m = self._cargar("portico", _txt("portico", ";;", barras_extra=";art_i;art_j;pandeo", cargas="-10000;0;0"))
        t = tp(m, ep(m, rp(m)[0]["c"]))[0]
        I = math.pi / 64 * (50 ** 4 - 44 ** 4)
        Pc = math.pi ** 2 * 210000 * I / (2 * 1000) ** 2                  # empotrado-libre: K = 2
        self.assertAlmostEqual(t["Pc"], Pc, 6)
        self.assertAlmostEqual(t["n_pand"], Pc / 10000, 6)

    def test_pandeo_sin_compresion_no_da_cs(self):
        from struttura.portico.esfuerzos import esfuerzos as ep, tensiones as tp
        from struttura.portico.solver import resolver as rp
        m = self._cargar("portico", _txt("portico", ";;"))                # solo carga transversal
        self.assertIsNone(tp(m, ep(m, rp(m)[0]["c"]))[0]["n_pand"])

    def test_pandeo_valor_invalido(self):
        with self.assertRaises(ErrorDeEntrada):
            self._cargar("portico", _txt("portico", ";;", barras_extra=";art_i;art_j;pandeo").replace("emp-lib", "xx"))

    def test_pared_delgada_planos_igual_al_3d(self):
        """Canal en el emparrillado: mismo σeq que el pórtico 3D con la misma sección y las mismas cargas."""
        from struttura.emparrillado.esfuerzos import esfuerzos as ee, tensiones as te
        from struttura.emparrillado.solver import resolver as re_
        from struttura.portico3d.entrada import cargar_modelo as c3
        from struttura.portico3d.solver import resolver as r3
        from struttura.portico3d.tensor import analizar
        sec = "SECCIONES\nid;tipo;h;b;t\nT;canal;100;50;4\n"
        m = self._cargar("emparrillado", _txt("emparrillado", ";;", sec=sec))
        t = te(m, ee(m, re_(m)[0]["c"]))[0]
        f3 = Path(self.tmp) / "c3.csv"
        f3.write_text("PROYECTO\nproyecto;x\nunidad_fuerza;N\nunidad_longitud;mm\ntipo;portico3d\nNODOS\nid;x;y;z\n1;0;0;0\n2;1000;0;0\n"
                      "MATERIALES\nid;E;nu;fy\nA;210000;0,3;235\n" + sec + "BARRAS\nid;nodo_i;nodo_j;material;seccion\n1;1;2;A;T\n"
                      "APOYOS\nnodo;ux;uy;uz;phix;phiy;phiz\n1;1;1;1;1;1;1\nCARGAS\ncaso;nodo;Fx;Fy;Fz;Mx;My;Mz\nc;2;0;0;-500;0;0;0\n", encoding="utf-8")
        m3 = c3(f3)
        a3 = analizar(m3, r3(m3)[0]["c"])["barras"][0]
        self.assertAlmostEqual(t["vm"], a3["eq"], 6)

    def test_pared_delgada_portico_secciones_nuevas(self):
        sec = "SECCIONES\nid;tipo;h;b;t\nT;te;100;60;4\n"
        m = self._cargar("portico", _txt("portico", ";;", sec=sec))
        self.assertIsNotNone(m.secciones["T"].pared)
        self.assertGreater(m.secciones["T"].I, 0)

    def test_soldadura_en_planos_coincide_con_3d(self):
        from struttura.soldadura import en_modelo
        sold = "SOLDADURAS\nid;barra;extremo;disposicion;electrodo;w;sy_base\nS1;1;i;circulo;E70;4;235\n"
        for tipo, cargas, f3 in (("emparrillado", "-500;0;0", "0;0;-500;0;0;0"), ("portico", "0;-500;0", "0;0;-500;0;0;0")):
            m = self._cargar(tipo, _txt(tipo, ";;", cargas=cargas, bloques_extra=sold))
            res = resolver_emp(m)[0] if tipo == "emparrillado" else __import__("struttura.portico.solver", fromlist=["x"]).resolver(m)[0]
            r = en_modelo.evaluar(m, res, tipo)["S1"][0][3]
            from struttura.portico3d.entrada import cargar_modelo as c3
            from struttura.portico3d.solver import resolver as r3
            from struttura.portico3d.soldaduras import evaluar as ev
            from struttura.portico3d.esfuerzos import esfuerzos_extremos
            f = Path(self.tmp) / "w3.csv"
            f.write_text("PROYECTO\nproyecto;x\nunidad_fuerza;N\nunidad_longitud;mm\ntipo;portico3d\nNODOS\nid;x;y;z\n1;0;0;0\n2;1000;0;0\n"
                         "MATERIALES\nid;E;nu;fy\nA;210000;0,3;235\nSECCIONES\nid;tipo;d;t\nT;tubo;50;3\nBARRAS\nid;nodo_i;nodo_j;material;seccion\n1;1;2;A;T\n"
                         "APOYOS\nnodo;ux;uy;uz;phix;phiy;phiz\n1;1;1;1;1;1;1\nCARGAS\ncaso;nodo;Fx;Fy;Fz;Mx;My;Mz\nc;2;" + f3 + "\n" + sold, encoding="utf-8")
            m3 = c3(f)
            res3 = r3(m3)[0]
            r3_ = ev(m3, res3, {n: esfuerzos_extremos(m3, x) for n, x in res3.items()})["S1"][0][3]
            self.assertAlmostEqual(r["fmax"], r3_["fmax"], 6, msg=tipo)

    def test_soldadura_electrodo_de_la_biblioteca_y_electrodo_propio(self):
        from struttura.biblioteca import electrodos as el
        from struttura.soldadura.datos import KSI_MPA, electrodo
        sut, sy, tau = electrodo("E70")
        self.assertAlmostEqual(tau, 21 * KSI_MPA, 6)                       # Shigley Tabla 9-6 A
        if el.existe():
            self.assertAlmostEqual(el.datos("E70")[2], 21 * KSI_MPA, 4)
            self.assertEqual(el.cargar("2")["id"], "E70")
        self.assertAlmostEqual(electrodo("E70", {"E70": (1.0, 2.0, 3.0)})[2], 3.0)   # lo escrito a mano manda


if __name__ == "__main__":
    unittest.main()


class TestEjemploFuselajeSoldado(unittest.TestCase):
    def test_ejemplo16_corre_y_tiene_cordones(self):
        import os, tempfile
        from struttura.portico3d.entrada import cargar_modelo
        ruta = os.path.join(os.path.dirname(__file__), "..", "003_Ejemplos", "004_Portico_espacial", "ejemplo16_fuselaje_soldaduras_criticas.csv")
        m = cargar_modelo(ruta)
        self.assertEqual(len(m.soldaduras), 10)
        self.assertEqual({s.electrodo for s in m.soldaduras}, {"E70"})
