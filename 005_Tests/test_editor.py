"""Editor visual: lógica (esquema, lector/escritor, servidor) y página en un navegador simulado (se omite si no hay Playwright)."""
import contextlib
import glob
import io
import json
import os
import sys
import tempfile
import threading
import unittest
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "001_Codigo"))

from struttura.editor import csvio, servidor  # noqa: E402
from struttura.editor.esquema import ESQUEMAS  # noqa: E402

EJEMPLOS = sorted(p for p in glob.glob(str(RAIZ / "003_Ejemplos" / "**" / "*.csv"), recursive=True) + glob.glob(str(RAIZ / "002_Plantillas" / "*.csv")) if "_salida" not in p)
POR_TIPO = {}
for _p in EJEMPLOS:
    try:
        _t = csvio.leer_archivo(_p)["tipo"]
    except Exception:
        continue
    POR_TIPO.setdefault(_t, []).append(_p)


class TestEsquema(unittest.TestCase):
    def test_coincide_con_los_cargadores(self):
        import importlib
        mods = {"portico3d": "struttura.portico3d.entrada", "portico": "struttura.portico.entrada",
                "emparrillado": "struttura.emparrillado.entrada", "reticulado": "struttura.reticulado.entrada"}
        for t, mn in mods.items():
            m = importlib.import_module(mn)
            self.assertEqual([b["t"] for b in ESQUEMAS[t]["bloques"]], list(m.TITULOS), t)
            cols = {b["t"]: [c["n"] for c in b["cols"]] for b in ESQUEMAS[t]["bloques"]}
            for k, v in m._COLUMNAS.items():
                self.assertEqual(set(v), set(cols[k]), f"{t}: {k}")

    def test_soldadura_modo_rapido(self):
        t = [b["t"] for b in ESQUEMAS["soldadura"]["bloques"]]
        self.assertEqual(t, ["PROYECTO", "ELECTRODOS", "SOLDADURAS", "CARGAS"])
        from struttura.soldadura.entrada import TITULOS, COMP
        self.assertEqual(t, list(TITULOS))
        cargas = [c["n"] for c in ESQUEMAS["soldadura"]["bloques"][3]["cols"]]
        for c in COMP:
            self.assertIn(c, cargas)

    def test_claves_de_proyecto_son_las_que_acepta_el_programa(self):
        import re
        for t, mn in {"portico3d": "portico3d", "portico": "portico", "emparrillado": "emparrillado"}.items():
            src = (RAIZ / "001_Codigo" / "struttura" / mn / "entrada.py").read_text(encoding="utf-8")
            cfg = re.search(r"config = \{(.*?)\}\n", src, re.S).group(1)
            claves = set(re.findall(r'"(\w+)":', cfg)) - {"_nodal"}
            sch = {c["n"] for c in ESQUEMAS[t]["bloques"][0]["cols"]}
            self.assertEqual(claves, sch, t)


class TestCsvIO(unittest.TestCase):
    def test_ida_y_vuelta_de_todos_los_ejemplos(self):
        from struttura.despachador import main
        malos = []
        for a in EJEMPLOS:
            doc = csvio.leer_archivo(a)
            txt, _ = csvio.a_texto(doc)
            with tempfile.TemporaryDirectory() as d:
                p2 = os.path.join(d, os.path.basename(a))
                Path(p2).write_text(txt, encoding="utf-8")
                res = []
                for p in (a, p2):
                    o = os.path.join(d, "s" + str(len(res)))
                    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                        rc = main([p, "-o", o])
                    res.append((rc, o))
                if res[0][0] != res[1][0]:
                    malos.append((a, "código de salida"))
                    continue
                for n in ("desplazamientos.csv", "reacciones.csv", "esfuerzos.csv", "soldaduras.csv", "soldaduras_tope.csv"):
                    f1, f2 = os.path.join(res[0][1], n), os.path.join(res[1][1], n)
                    if os.path.exists(f1) != os.path.exists(f2) or (os.path.exists(f1) and Path(f1).read_bytes() != Path(f2).read_bytes()):
                        malos.append((a, n))
        self.assertEqual(malos, [])

    def test_conserva_comentarios_y_columnas_propias(self):
        txt = "# titulo\n\nPROYECTO\n# dato\nproyecto;x\ntipo;portico\nunidad_fuerza;N\nunidad_longitud;mm\n\n# nodos\nNODOS\nid;x;y;nota\n1;0;0;origen\n# segundo\n2;1;0;\n"
        doc = csvio.leer_texto(txt)
        self.assertEqual(doc["tipo"], "portico")
        out, _ = csvio.a_texto(doc)
        self.assertIn("# titulo", out)
        self.assertIn("# nodos", out)
        self.assertIn("# segundo", out)
        self.assertIn("1;0;0;origen", out)
        self.assertIn("id;x;y;nota", out)

    def test_documento_nuevo_se_puede_escribir(self):
        for t in ESQUEMAS:
            doc = csvio.doc_nuevo(t)
            txt, _ = csvio.a_texto(doc)
            self.assertIn(f"tipo;{t}", txt)
            self.assertEqual(csvio.leer_texto(txt)["tipo"], t)


class TestServidor(unittest.TestCase):
    def test_abrir_revisar_guardar_y_calcular(self):
        a = str(RAIZ / "003_Ejemplos" / "002_Portico" / "ejemplo14_portico_biempotrado.csv")
        j = servidor.abrir(a)
        self.assertEqual(j["doc"]["tipo"], "portico")
        self.assertTrue(servidor.revisar(j["doc"])["ok"])
        with tempfile.TemporaryDirectory() as d:
            r = servidor.calcular(os.path.join(d, "x.csv"), j["doc"])
            self.assertEqual(r["rc"], 0, r["texto"])
            self.assertTrue(r["informe"])
            self.assertTrue(os.path.exists(os.path.join(d, "x_salida", "informe.html")))

    def test_error_de_datos_indica_bloque_y_fila(self):
        a = str(RAIZ / "003_Ejemplos" / "002_Portico" / "ejemplo14_portico_biempotrado.csv")
        doc = servidor.abrir(a)["doc"]
        b = [x for x in doc["bloques"] if x["t"] == "BARRAS"][0]
        b["filas"][1]["c"][b["cab"].index("nodo_j")] = "99"
        r = servidor.revisar(doc)
        self.assertFalse(r["ok"])
        self.assertEqual(r["bloque"], "BARRAS")
        self.assertEqual(r["fila"], 1)

    def test_guardar_comprueba_y_dice_donde(self):
        with tempfile.TemporaryDirectory() as d:
            r = servidor.guardar(os.path.join(d, "sub", "m"), csvio.doc_nuevo("portico"))
            self.assertTrue(Path(r["ruta"]).is_file())
            self.assertEqual(r["bytes"], Path(r["ruta"]).stat().st_size)
            self.assertEqual(r["carpeta"], str(Path(d, "sub").resolve()))
            with self.assertRaises(FileNotFoundError):
                servidor.abrir_carpeta(os.path.join(d, "no_existe"))

    def test_ficha_de_biblioteca(self):
        from struttura.biblioteca import biblioteca
        if not biblioteca.archivo().is_file():
            self.skipTest("no hay biblioteca de materiales")
        j = servidor.ficha("material", biblioteca.listar()[0][0], "N", "mm")
        self.assertTrue(j["ok"], j)
        self.assertIn("e", j["valores"])
        self.assertFalse(servidor.ficha("material", "no-existe", "N", "mm")["ok"])

    def test_listar_carpeta(self):
        j = servidor.listar(str(RAIZ / "003_Ejemplos"))
        self.assertIn("002_Portico", j["dirs"])

    def test_pedidos_sin_codigo_son_rechazados(self):
        srv = servidor.iniciar(None, 0, False, False)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            rq = urllib.request.Request(f"http://127.0.0.1:{srv.server_port}/api/listar", data=b"{}", method="POST")
            with self.assertRaises(urllib.error.HTTPError) as c:
                urllib.request.urlopen(rq)
            self.assertEqual(c.exception.code, 403)
        finally:
            srv.shutdown()
            srv.server_close()


try:
    from playwright.sync_api import sync_playwright
except Exception:                                                                      # pragma: no cover
    sync_playwright = None


@unittest.skipIf(sync_playwright is None, "Playwright no está instalado")
class TestPagina(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = servidor.iniciar(None, 0, False, False)
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.pw = sync_playwright().start()
        cls.nav = cls.pw.chromium.launch()
        cls.url = f"http://127.0.0.1:{cls.srv.server_port}/"

    @classmethod
    def tearDownClass(cls):
        cls.nav.close()
        cls.pw.stop()
        cls.srv.shutdown()
        cls.srv.server_close()

    def pagina(self):
        pg = self.nav.new_page(viewport={"width": 1500, "height": 900})
        self.errs = []
        pg.on("pageerror", lambda e: self.errs.append("PAGEERROR " + str(e)))
        pg.on("console", lambda m: self.errs.append(m.text) if m.type == "error" else None)
        pg.on("dialog", lambda d: d.accept())
        pg.goto(self.url)
        pg.wait_for_function("window.V && typeof S !== 'undefined'")
        return pg

    def abrir(self, pg, ruta):
        pg.evaluate("async r => { cargarDoc(await api('abrir', {ruta: r})); }", ruta)
        pg.wait_for_function("S.rev !== null", timeout=15000)

    def test_cada_tipo_muestra_todas_las_columnas_de_cada_bloque(self):
        pg = self.pagina()
        for tipo, lista in POR_TIPO.items():
            ruta = lista[0]
            self.abrir(pg, ruta)
            for sp in ESQUEMAS[tipo]["bloques"]:
                if sp["k"] == "claves":
                    pg.evaluate("t => irBloque(t)", sp["t"])
                    etiquetas = pg.eval_on_selector_all("#tabla-wrap .form label", "els => els.map(e => (e.querySelector('small.cl') || {}).textContent)")
                    for c in sp["cols"]:
                        self.assertIn(c["n"], etiquetas, f"{tipo} PROYECTO.{c['n']}")
                    continue
                # el bloque tiene que poder mostrarse completo, también vacío
                pg.evaluate("t => { S.todasCols = true; blk(t, true); irBloque(t); }", sp["t"])
                if pg.query_selector("#tabla-wrap table.t") is None:
                    pg.click("text=+ Agregar fila")
                cab = pg.eval_on_selector_all("#tabla-wrap table.t thead th", "els => els.map(e => (e.querySelector('small.cl') || {}).textContent)")
                for c in sp["cols"]:
                    self.assertIn(c["n"], cab, f"{tipo} {sp['t']}.{c['n']}")
        self.assertEqual(self.errs, [])
        pg.close()

    def test_los_ejemplos_abren_sin_errores_y_son_validos(self):
        pg = self.pagina()
        for tipo, lista in POR_TIPO.items():
            for ruta in lista:
                self.abrir(pg, ruta)
                ok = pg.evaluate("S.rev.ok")
                self.assertTrue(ok, f"{ruta}: {pg.evaluate('S.rev.error')}")
        self.assertEqual(self.errs, [])
        pg.close()

    def test_armar_un_portico_con_el_mouse_y_calcularlo(self):
        pg = self.pagina()
        pg.evaluate("async () => cargarDoc(await api('nuevo', {tipo: 'portico'}))")
        pg.evaluate("() => { setP('unidad_fuerza', 'N'); setP('unidad_longitud', 'mm'); cambio(); }")
        # material y sección por las tablas
        pg.evaluate("t => irBloque(t)", "MATERIALES")
        pg.click("text=+ Agregar fila")
        fila = pg.locator("#tabla-wrap tbody tr").last
        for col, v in (("id", "acero"), ("e", "210000"), ("nu", "0,3"), ("fy", "235")):
            idx = pg.evaluate("n => spec('MATERIALES').cols.findIndex(c => c.n === n)", col)
            fila.locator("td").nth(idx + 1).locator("input").fill(v)
        pg.evaluate("t => irBloque(t)", "SECCIONES")
        pg.click("text=+ Agregar fila")
        fila = pg.locator("#tabla-wrap tbody tr").last
        cols = pg.evaluate("spec('SECCIONES').cols.map(c => c.n)")
        fila.locator("td").nth(cols.index("id") + 1).locator("input").fill("viga")
        fila.locator("td").nth(cols.index("tipo") + 1).locator("select").select_option("rect_hueca")
        for col, v in (("b", "100"), ("h", "200"), ("t", "5")):            # la tabla ahora muestra solo las medidas de esa forma
            vis = pg.eval_on_selector_all("#tabla-wrap table.t thead th small.cl", "els => els.map(e => e.textContent)")
            pg.locator("#tabla-wrap tbody tr").last.locator("td").nth(vis.index(col) + 1).locator("input").fill(v)
        # nodos y barras con el mouse
        pg.evaluate("t => irBloque(t)", "NODOS")
        pg.evaluate("() => { V.opt.paso = '1000'; V.ajustar(); V.usar('barra'); }")

        def clic(x, y):
            pg.evaluate("() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")
            caja = pg.locator("#lienzo").bounding_box()
            sx, sy, _ = pg.evaluate("p => V.proy(p)", [x, y, 0])
            pg.mouse.click(caja["x"] + sx, caja["y"] + sy)

        for p in ((0, 0), (0, 4000), (6000, 4000), (6000, 0)):
            clic(*p)
        self.assertEqual(pg.evaluate("filas('NODOS').length"), 4)
        self.assertEqual(pg.evaluate("filas('BARRAS').length"), 3)
        coords = pg.evaluate("filas('NODOS').map(f => [get(blk('NODOS'), f, 'x'), get(blk('NODOS'), f, 'y')])")
        self.assertEqual([[num_(a), num_(b)] for a, b in coords], [[0, 0], [0, 4000], [6000, 4000], [6000, 0]])
        # apoyos empotrados en los nodos 1 y 4, carga horizontal en el 2 y carga distribuida en la viga
        pg.evaluate("() => { V.opt.apoyoPreset = 0; V.usar('apoyo'); }")
        clic(0, 0)
        clic(6000, 0)
        self.assertEqual(pg.evaluate("apoyoDe('1')"), ["ux", "uy", "phi"])
        pg.evaluate("() => { V.opt.casoNuevo = 'V'; V.opt.carga = {px: '10000'}; V.usar('carga'); }")
        clic(0, 4000)
        pg.evaluate("() => { V.opt.casoNuevo = 'Q'; V.opt.cargaBarra = {tipo: 'qgy', valor: '-10', valor2: '', a: '', b: ''}; V.usar('cbarra'); }")
        clic(3000, 4000)
        self.assertEqual(pg.evaluate("filas('CARGAS EN BARRAS').length"), 1, pg.evaluate("S.msg"))
        self.assertEqual(pg.evaluate("filas('CARGAS').length"), 1)
        pg.evaluate("() => { programarRevision(); }")
        pg.wait_for_function("S.rev && S.rev.ok", timeout=15000)
        self.assertTrue(pg.evaluate("S.rev.ok"), pg.evaluate("S.rev.error"))
        with tempfile.TemporaryDirectory() as d:
            ruta = os.path.join(d, "armado.csv")
            r = pg.evaluate("async r => { S.ruta = r; await calcular(); return S.calc; }", ruta)
            self.assertEqual(r["rc"], 0, r["texto"])
            self.assertTrue(os.path.exists(os.path.join(d, "armado_salida", "informe.html")))
            # el mismo modelo escrito a mano tiene que dar exactamente los mismos resultados
            from struttura.despachador import main
            ref = os.path.join(d, "ref.csv")
            Path(ref).write_text(REFERENCIA, encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main([ref]), 0)
            for n in ("desplazamientos.csv", "reacciones.csv", "esfuerzos.csv", "tensiones.csv"):
                self.assertEqual(Path(d, "armado_salida", n).read_bytes(), Path(d, "ref_salida", n).read_bytes(), n)
        self.assertEqual(self.errs, [])
        pg.close()

    # ---- los otros tres tipos armados con el mouse, contra el mismo modelo escrito a mano ----
    def _clic(self, pg, p):
        pg.evaluate("() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")
        caja = pg.locator("#lienzo").bounding_box()
        sx, sy, _ = pg.evaluate("p => V.proy(p)", [*p, 0][:3] if len(p) == 2 else list(p))
        pg.mouse.click(caja["x"] + sx, caja["y"] + sy)

    def _armar_y_comparar(self, tipo, fila_extra, pasos, referencia, archivos):
        pg = self.pagina()
        pg.evaluate("async t => cargarDoc(await api('nuevo', {tipo: t}))", tipo)
        pg.evaluate("() => { setP('unidad_fuerza', 'N'); setP('unidad_longitud', 'mm'); cambio(); }")
        pg.evaluate("""f => { for (const [t, c] of f) { const b = blk(t, true); const fl = filaVacia(b); for (const [k, v] of Object.entries(c)) set(b, fl, k, v); b.filas.push(fl); } cambio(); }""", fila_extra)
        pasos(pg)
        pg.evaluate("() => revisar()")
        pg.wait_for_function("S.rev && S.rev.ok", timeout=15000)
        with tempfile.TemporaryDirectory() as d:
            r = pg.evaluate("async r => { S.ruta = r; await calcular(); return S.calc; }", os.path.join(d, "armado.csv"))
            self.assertEqual(r["rc"], 0, r["texto"])
            from struttura.despachador import main
            ref = os.path.join(d, "ref.csv")
            Path(ref).write_text(referencia, encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main([ref]), 0)
            for n in archivos:
                self.assertEqual(Path(d, "armado_salida", n).read_bytes(), Path(d, "ref_salida", n).read_bytes(), n)
        self.assertEqual(self.errs, [])
        pg.close()

    def test_armar_un_emparrillado_con_el_mouse(self):
        def pasos(pg):
            pg.evaluate("() => { V.opt.paso = '500'; V.ajustar(); V.usar('barra'); }")
            self._clic(pg, (0, 0))
            self._clic(pg, (3000, 0))
            pg.evaluate("() => { V.opt.apoyoPreset = 0; V.usar('apoyo'); }")
            self._clic(pg, (0, 0))
            pg.evaluate("() => { V.opt.casoNuevo = 'P'; V.opt.carga = {pz: '-1000'}; V.usar('carga'); }")
            self._clic(pg, (3000, 0))
        self._armar_y_comparar("emparrillado",
            [("MATERIALES", {"id": "a", "e": "210000", "nu": "0,3"}), ("SECCIONES", {"id": "t", "tipo": "tubo", "d": "60", "t": "4"})],
            pasos, "PROYECTO\ntipo;emparrillado\nunidad_fuerza;N\nunidad_longitud;mm\nNODOS\nid;x;y\n1;0;0\n2;3000;0\nMATERIALES\nid;e;nu\na;210000;0,3\n"
            "SECCIONES\nid;tipo;d;t\nt;tubo;60;4\nBARRAS\nid;nodo_i;nodo_j;material;seccion\n1;1;2;a;t\nAPOYOS\nnodo;uz;phix;phiy\n1;1;1;1\n"
            "CARGAS\ncaso;nodo;pz;mx;my\nP;2;-1000;;\n", ("desplazamientos.csv", "reacciones.csv", "esfuerzos.csv"))

    def test_armar_un_reticulado_con_el_mouse(self):
        def pasos(pg):
            pg.evaluate("() => { V.opt.paso = '500'; V.ajustar(); V.usar('barra'); }")
            for p in ((0, 0), (2000, 0), (1000, 1500), (0, 0)):
                self._clic(pg, p)
            pg.evaluate("() => { V.opt.apoyoPreset = 0; V.usar('apoyo'); }")
            self._clic(pg, (0, 0))
            pg.evaluate("() => { V.opt.apoyoPreset = 1; V.usar('apoyo'); }")
            self._clic(pg, (2000, 0))
            pg.evaluate("() => { V.opt.casoNuevo = 'P'; V.opt.carga = {py: '-5000'}; V.usar('carga'); }")
            self._clic(pg, (1000, 1500))
        self._armar_y_comparar("reticulado",
            [("MATERIALES", {"id": "a", "e": "210000"}), ("SECCIONES", {"id": "s", "tipo": "circular", "d": "25"})],
            pasos, "PROYECTO\ntipo;reticulado\nunidad_fuerza;N\nunidad_longitud;mm\nNODOS\nid;x;y\n1;0;0\n2;2000;0\n3;1000;1500\nMATERIALES\nid;e\na;210000\n"
            "SECCIONES\nid;tipo;d\ns;circular;25\nBARRAS\nid;nodo_i;nodo_j;material;seccion\n1;1;2;a;s\n2;2;3;a;s\n3;3;1;a;s\n"
            "APOYOS\nnodo;ux;uy\n1;1;1\n2;;1\nCARGAS\ncaso;nodo;px;py\nP;3;;-5000\n", ("desplazamientos.csv", "reacciones.csv", "barras.csv"))

    def test_armar_un_portico_3d_con_el_mouse(self):
        def pasos(pg):
            pg.evaluate("() => { V.opt.paso = '500'; V.opt.plano = 'z'; V.opt.planoV = '0'; V.ajustar(); V.usar('barra'); }")
            self._clic(pg, (0, 0, 0))
            self._clic(pg, (2000, 0, 0))
            pg.evaluate("() => { V.opt.plano = 'y'; V.opt.planoV = '0'; }")
            self._clic(pg, (2000, 0, 1500))
            pg.evaluate("() => { V.opt.apoyoPreset = 0; V.usar('apoyo'); }")
            self._clic(pg, (0, 0, 0))
            pg.evaluate("() => { V.opt.casoNuevo = 'P'; V.opt.carga = {fz: '-1000'}; V.usar('carga'); }")
            self._clic(pg, (2000, 0, 1500))
        self._armar_y_comparar("portico3d",
            [("MATERIALES", {"id": "a", "e": "210000", "nu": "0,3"}), ("SECCIONES", {"id": "t", "tipo": "tubo", "d": "40", "t": "3"})],
            pasos, "PROYECTO\ntipo;portico3d\nunidad_fuerza;N\nunidad_longitud;mm\nNODOS\nid;x;y;z\n1;0;0;0\n2;2000;0;0\n3;2000;0;1500\nMATERIALES\nid;e;nu\na;210000;0,3\n"
            "SECCIONES\nid;tipo;d;t\nt;tubo;40;3\nBARRAS\nid;nodo_i;nodo_j;material;seccion\n1;1;2;a;t\n2;2;3;a;t\n"
            "APOYOS\nnodo;ux;uy;uz;phix;phiy;phiz\n1;1;1;1;1;1;1\nCARGAS\ncaso;nodo;fx;fy;fz;mx;my;mz\nP;3;;;-1000;;;\n",
            ("desplazamientos.csv", "reacciones.csv", "esfuerzos.csv"))

    def test_guardar_como_abrir_y_deshacer(self):
        pg = self.pagina()
        pg.evaluate("async () => cargarDoc(await api('nuevo', {tipo: 'portico'}))")
        pg.evaluate("() => { V.opt.paso = '1000'; V.ajustar(); V.usar('nodo'); }")
        self._clic(pg, (0, 0))
        self._clic(pg, (1000, 1000))
        self.assertEqual(pg.evaluate("filas('NODOS').length"), 2)
        pg.keyboard.press("Control+z")
        self.assertEqual(pg.evaluate("filas('NODOS').length"), 1)
        pg.keyboard.press("Control+y")
        self.assertEqual(pg.evaluate("filas('NODOS').length"), 2)
        with tempfile.TemporaryDirectory() as d:
            ruta = os.path.join(d, "sub", "m.csv")
            j = pg.evaluate("async r => await api('guardar', {ruta: r, doc: S.doc})", ruta)
            self.assertTrue(os.path.exists(ruta))
            self.assertEqual(Path(j["ruta"]).name, "m.csv")
            pg.evaluate("async r => cargarDoc(await api('abrir', {ruta: r}))", ruta)
            self.assertEqual(pg.evaluate("filas('NODOS').length"), 2)
            # borrar un nodo con elementos asociados pide confirmación y borra en cascada
            pg.evaluate("() => { crearBarra('1', '2'); }")
            pg.evaluate("() => borrarElemento('nodo', '1')")
            self.assertEqual(pg.evaluate("filas('BARRAS').length"), 0)
        self.assertEqual(self.errs, [])
        pg.close()

    # ---- nombres claros, desplegables, apoyos, Enter, nodos repetidos ----
    def test_no_se_crean_nodos_en_el_mismo_punto_y_se_pueden_unir(self):
        pg = self.pagina()
        pg.evaluate("async () => cargarDoc(await api('nuevo', {tipo: 'portico'}))")
        a = pg.evaluate("crearNodo([0, 0])")
        b = pg.evaluate("crearNodo([0, 0])")
        self.assertEqual(a, b)
        self.assertEqual(pg.evaluate("filas('NODOS').length"), 1)
        # un archivo con nodos repetidos: se avisa y «Unir» los junta (barras y apoyos pasan al nodo que queda)
        pg.evaluate("""() => { const n = blk('NODOS'); const f = filaVacia(n); set(n, f, 'id', '2'); set(n, f, 'x', '0'); set(n, f, 'y', '0'); n.filas.push(f);
            const g = filaVacia(n); set(n, g, 'id', '3'); set(n, g, 'x', '5'); set(n, g, 'y', '0'); n.filas.push(g);
            const bb = blk('BARRAS', true); const h = filaVacia(bb); set(bb, h, 'id', 'B'); set(bb, h, 'nodo_i', '2'); set(bb, h, 'nodo_j', '3'); bb.filas.push(h); cambio(); }""")
        self.assertEqual(pg.evaluate("nodosDuplicados()"), [["1", "2"]])
        self.assertIn("mismo punto", pg.inner_text("#estado-linea"))
        pg.evaluate("unirNodos(nodosDuplicados()[0])")
        self.assertEqual(pg.evaluate("filas('NODOS').length"), 2)
        self.assertEqual(pg.evaluate("get(blk('BARRAS'), filas('BARRAS')[0], 'nodo_i')"), "1")
        self.assertEqual(self.errs, [])
        pg.close()

    def test_etiquetas_claras_y_apoyos_fijo_libre(self):
        pg = self.pagina()
        pg.evaluate("async () => cargarDoc(await api('nuevo', {tipo: 'portico'}))")
        pg.evaluate("t => { crearNodo([0, 0]); irBloque(t); }", "APOYOS")
        pg.click("text=+ Agregar fila")
        cab = pg.eval_on_selector_all("#tabla-wrap table.t thead th .et", "els => els.map(e => e.textContent)")
        self.assertIn("Desplazamiento en x", cab)
        self.assertNotIn("ux", cab)
        pg.evaluate("t => irBloque(t)", "CARGAS")
        pg.click("text=+ Agregar fila")
        cab = pg.eval_on_selector_all("#tabla-wrap table.t thead th .et", "els => els.map(e => e.textContent)")
        self.assertTrue(any(c.startswith("Fuerza en x") and "[N]" in c for c in cab), cab)
        # los apoyos son botones Fijo / Libre y el atajo de tipo completa todos
        pg.evaluate("t => irBloque(t)", "APOYOS")
        self.assertEqual(pg.locator("#tabla-wrap button.apoyo").count(), 3)
        pg.locator("#tabla-wrap tbody tr select").first.select_option("1")
        pg.locator("#tabla-wrap button.apoyo").first.click()
        self.assertEqual(pg.evaluate("apoyoDe('1')"), ["ux"])
        pg.locator("#tabla-wrap tbody tr select").last.select_option(label="Empotrado")
        self.assertEqual(pg.evaluate("apoyoDe('1')"), ["ux", "uy", "phi"])
        self.assertEqual(self.errs, [])
        pg.close()

    def test_desplegables_con_id_y_detalle_y_secciones_por_forma(self):
        pg = self.pagina()
        self.abrir(pg, str(RAIZ / "003_Ejemplos" / "002_Portico" / "ejemplo14_portico_biempotrado.csv"))
        pg.evaluate("t => irBloque(t)", "BARRAS")
        textos = pg.eval_on_selector_all("#tabla-wrap tbody tr:first-child select option", "els => els.map(e => e.textContent)")
        self.assertIn("1: (0; 0)", textos)                                   # nodo con sus coordenadas
        self.assertTrue(any(t.startswith("acero:") for t in textos), textos)  # material con su detalle
        self.assertTrue(any(t.startswith("perfil: Doble T") for t in textos), textos)  # sección con su forma y medidas
        # la sección doble T muestra solo sus medidas
        pg.evaluate("t => irBloque(t)", "SECCIONES")
        cab = pg.eval_on_selector_all("#tabla-wrap table.t thead th small.cl", "els => els.map(e => e.textContent)")
        self.assertIn("tf", cab)
        self.assertNotIn("kv", cab)
        pg.check("text=Mostrar todas las columnas")
        cab = pg.eval_on_selector_all("#tabla-wrap table.t thead th small.cl", "els => els.map(e => e.textContent)")
        self.assertIn("kv", cab)
        self.assertEqual(self.errs, [])
        pg.close()

    def test_material_de_la_biblioteca_y_enter(self):
        pg = self.pagina()
        pg.evaluate("async () => cargarDoc(await api('nuevo', {tipo: 'portico'}))")
        pg.evaluate("t => irBloque(t)", "MATERIALES")
        if not pg.evaluate("S.bib.materiales.length"):
            self.skipTest("no hay biblioteca de materiales en esta copia")
        pg.select_option("select.agregar-lib", index=1)
        fila = pg.locator("#tabla-wrap tbody tr").first
        self.assertEqual(pg.evaluate("get(blk('MATERIALES'), filas('MATERIALES')[0], 'lib')"), pg.evaluate("S.bib.materiales[0].n"))
        self.assertEqual(pg.evaluate("get(blk('MATERIALES'), filas('MATERIALES')[0], 'id')"), "1")
        # el valor de la biblioteca se ve en la celda vacía
        pg.wait_for_function("document.querySelector('#tabla-wrap input.de-lib')")
        # Enter acepta y baja a la celda de abajo
        pg.click("text=+ Agregar fila")
        celdas = pg.locator("#tabla-wrap tbody tr td input[data-c='2']")
        celdas.nth(0).click()
        celdas.nth(0).fill("210000")
        celdas.nth(0).press("Enter")
        self.assertEqual(pg.evaluate("document.activeElement.dataset.r"), "1")
        self.assertEqual(pg.evaluate("get(blk('MATERIALES'), filas('MATERIALES')[0], 'e')"), "210000")
        self.assertEqual(self.errs, [])
        pg.close()

    def test_perfil_de_la_biblioteca(self):
        pg = self.pagina()
        for tipo in ("portico3d", "emparrillado"):
            pg.evaluate("async t => cargarDoc(await api('nuevo', {tipo: t}))", tipo)
            pg.evaluate("t => irBloque(t)", "SECCIONES")
            if not pg.evaluate("S.bib.perfiles.length"):
                self.skipTest("no hay biblioteca de perfiles en esta copia")
            n = pg.evaluate("S.bib.perfiles.find(p => p.t === 'IPE 200').n")
            pg.evaluate("n => agregarFila({ id: idPerfil(n), tipo: 'perfil', lib: n })", n)
            f = "filas('SECCIONES')[0]"
            self.assertEqual(pg.evaluate(f"get(blk('SECCIONES'), {f}, 'id')"), "IPE 200")
            self.assertEqual(pg.evaluate(f"get(blk('SECCIONES'), {f}, 'tipo')"), "perfil")
            pg.wait_for_function("document.querySelector('#tabla-wrap input.de-lib')")     # A, I... de la biblioteca como valor sugerido
            ph = pg.eval_on_selector_all("#tabla-wrap input.de-lib", "els => els.map(e => e.placeholder)")
            self.assertTrue(any("2850" in x or "2 850" in x for x in ph), ph)
            self.assertEqual(pg.evaluate("detalle('secciones', 'IPE 200')"), "Doble T IPE 200")
            # el desplegable de la celda lib agrupa por familia
            self.assertGreater(pg.evaluate("document.querySelectorAll('#tabla-wrap select.lib optgroup').length"), 10)
        self.assertEqual(self.errs, [])
        pg.close()

    def test_unidades_al_escribir_y_peso_propio(self):
        pg = self.pagina()
        self.abrir(pg, str(RAIZ / "003_Ejemplos" / "004_Portico_espacial" / "ejemplo1_voladizo_en_L.csv"))
        pg.evaluate("t => irBloque(t)", "NODOS")
        campo = pg.locator("#tabla-wrap tbody tr").first.locator("td").nth(2).locator("input")
        campo.fill("5 in")
        campo.press("Tab")
        self.assertEqual(pg.evaluate("get(blk('NODOS'), filas('NODOS')[0], 'x')"), "127")
        campo.fill("5 kN")                                     # fuerza en una columna de longitud: no se convierte
        campo.press("Tab")
        self.assertEqual(pg.evaluate("get(blk('NODOS'), filas('NODOS')[0], 'x')"), "5 kN")
        self.assertEqual(pg.evaluate("[convertirUnidad('30 ksi','MPa').v, convertirUnidad('2 kN','N').v, convertirUnidad('10 kgf/cm2','MPa').v]"), ["206.842719", "2000", "0.980665"])
        # peso propio: casilla + nombre
        pg.evaluate("t => irBloque(t)", "PROYECTO")
        pg.evaluate("setP('peso_propio', '')"); pg.evaluate("renderTabla()")
        pg.locator(".form input[type=checkbox]").first.check()
        self.assertEqual(pg.evaluate("getP('peso_propio')"), "PESO PROPIO")
        pg.locator(".form input[type=checkbox]").first.uncheck()
        self.assertEqual(pg.evaluate("getP('peso_propio')"), "")
        self.assertEqual(self.errs, [])
        pg.close()

    def test_calculadora_de_rigidez_y_resorte_inclinado(self):
        pg = self.pagina()
        pg.evaluate("async t => cargarDoc(await api('nuevo', {tipo: t}))", "portico3d")
        self.assertTrue(pg.evaluate("!!spec('RESORTES INCLINADOS')"))
        self.assertEqual(pg.evaluate("spec('RESORTES INCLINADOS').cols.map(c => c.n)"), ["nodo", "k", "dx", "dy", "dz", "ax", "ay", "az", "pc"])
        pg.evaluate("t => irBloque(t)", "RESORTES INCLINADOS")
        pg.get_by_text("Calcular k de una barra (EA/L)").click()
        pg.fill("#modal input[placeholder^='E ']", "210 GPa")
        pg.fill("#modal input[placeholder^='A ']", "5 cm2")
        pg.fill("#modal input[placeholder^='L ']", "2 m")
        self.assertIn("52500", pg.inner_text("#modal .resultado-k"))
        pg.get_by_text("Agregar fila con estos valores").click()
        self.assertEqual(pg.evaluate("get(blk('RESORTES INCLINADOS'), filas('RESORTES INCLINADOS')[0], 'k')"), "52500")
        self.assertEqual(self.errs, [])
        pg.close()

    def test_suprimir_una_barra(self):
        pg = self.pagina()
        self.abrir(pg, str(RAIZ / "003_Ejemplos" / "004_Portico_espacial" / "ejemplo2_portico_espacial.csv"))
        pg.evaluate("t => irBloque(t)", "BARRAS")
        sel = pg.locator("#tabla-wrap tbody tr").first.locator("select").last
        sel.select_option(label="Suprimida")
        self.assertEqual(pg.evaluate("get(blk('BARRAS'), filas('BARRAS')[0], 'suprimida')"), "1")
        self.assertEqual(self.errs, [])
        pg.close()

    def test_calculadora_escribe_k_y_pc_en_la_celda_elegida(self):
        import math
        pg = self.pagina()
        pg.evaluate("async t => cargarDoc(await api('nuevo', {tipo: t}))", "portico3d")
        pg.evaluate("t => irBloque(t)", "RESORTES")
        pg.evaluate("agregarFila({ kx: '7' })")
        pg.evaluate("agregarFila({})")
        celdas = pg.locator("#tabla-wrap tbody tr").nth(1).locator("input")
        columnas = pg.evaluate("spec('RESORTES').cols.map(c => c.n)")
        celdas.nth(columnas.index("kz") - 1).click()      # «nodo» es un desplegable, no un input
        #                      # el usuario toca la celda donde quiere el valor
        pg.get_by_text("Calcular k de una barra (EA/L)").click()
        pg.fill("#modal input[placeholder^='E ']", "210 GPa")
        pg.fill("#modal input[placeholder^='A ']", "5 cm2")
        pg.fill("#modal input[placeholder^='L ']", "2 m")
        pg.fill("#modal input[placeholder^='I ']", "10 cm4")
        self.assertIn("Pc = ", pg.inner_text("#modal .resultado-k"))
        pg.get_by_text("Escribir en la celda").click()
        self.assertEqual(pg.evaluate("get(blk('RESORTES'), filas('RESORTES')[1], 'kz')"), "52500")
        pc = float(pg.evaluate("get(blk('RESORTES'), filas('RESORTES')[1], 'pc')").replace(",", "."))
        self.assertAlmostEqual(pc, math.pi ** 2 * 210000 * 1e5 / 2000 ** 2, delta=pc * 1e-6)       # art-art, K = 1
        self.assertEqual(pg.evaluate("get(blk('RESORTES'), filas('RESORTES')[0], 'kz')"), "")         # la otra fila no se toca
        self.assertEqual(self.errs, [])
        pg.close()

    def test_renombrar_un_nodo_actualiza_las_barras(self):
        pg = self.pagina()
        self.abrir(pg, str(RAIZ / "003_Ejemplos" / "002_Portico" / "ejemplo14_portico_biempotrado.csv"))
        pg.evaluate("t => irBloque(t)", "NODOS")
        campo = pg.locator("#tabla-wrap tbody tr").first.locator("td").nth(1).locator("input")
        campo.fill("A1")
        campo.press("Tab")
        self.assertEqual(pg.evaluate("get(blk('BARRAS'), filas('BARRAS')[0], 'nodo_i')"), "A1")
        self.assertEqual(pg.evaluate("apoyoDe('A1')"), ["ux", "uy", "phi"])
        pg.wait_for_function("S.rev && S.rev.ok", timeout=15000)
        pg.close()


REFERENCIA = """PROYECTO
proyecto;x
tipo;portico
unidad_fuerza;N
unidad_longitud;mm
NODOS
id;x;y
1;0;0
2;0;4000
3;6000;4000
4;6000;0
MATERIALES
id;e;nu;fy
acero;210000;0,3;235
SECCIONES
id;tipo;b;h;t
viga;rect_hueca;100;200;5
BARRAS
id;nodo_i;nodo_j;material;seccion
1;1;2;acero;viga
2;2;3;acero;viga
3;3;4;acero;viga
APOYOS
nodo;ux;uy;phi
1;1;1;1
4;1;1;1
CARGAS
caso;nodo;px;py;m
V;2;10000;0;0
CARGAS EN BARRAS
caso;barra;tipo;valor;valor2;a;b
Q;2;qgy;-10;;;
"""


def num_(s):
    return float(str(s).replace(",", "."))


if __name__ == "__main__":
    unittest.main()
