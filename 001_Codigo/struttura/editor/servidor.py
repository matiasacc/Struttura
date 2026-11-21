"""Servidor local del editor:  python struttura.py --editor [ARCHIVO.csv]

Sirve la página del editor en 127.0.0.1 y atiende sus pedidos: abrir / guardar (con explorador de carpetas), revisar el modelo
con los mismos cargadores que usa el cálculo, y calcular (corre el programa del tipo de estructura y sirve el informe).
Cada pedido lleva un código que solo conoce la página que abrió este servidor."""
from __future__ import annotations

import contextlib
import io
import json
import mimetypes
import os
import re
import secrets
import sys
import tempfile
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from .. import __version__
from . import csvio
from .esquema import ESQUEMAS

WEB = Path(__file__).resolve().parent / "web"
_LOCK = threading.Lock()
_SALIDAS: dict = {}                       # id → carpeta de resultados que se puede servir


# ----------------------------------------------------------------------------------------------------------------------
# Lógica (se prueba sin servidor)
# ----------------------------------------------------------------------------------------------------------------------
def abrir(ruta):
    ruta = Path(ruta).expanduser()
    if not ruta.is_file():
        raise FileNotFoundError(f"No se encuentra el archivo '{ruta}'")
    doc = csvio.leer_archivo(ruta)
    if doc["tipo"] not in ESQUEMAS:
        raise ValueError("No pude deducir el tipo de estructura del archivo.  Agregá en PROYECTO la línea tipo;portico, portico3d, reticulado, emparrillado o soldadura.")
    return {"doc": doc, "ruta": str(ruta.resolve()), "nombre": ruta.name}


def guardar(ruta, doc):
    ruta = Path(ruta).expanduser()
    if ruta.suffix.lower() not in (".csv", ".txt"):
        ruta = ruta.with_suffix(".csv")
    texto, _ = csvio.a_texto(doc)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    datos = (b"\xef\xbb\xbf" if doc.get("bom") else b"") + texto.encode("utf-8")
    ruta.write_bytes(datos)
    if not ruta.is_file() or ruta.stat().st_size != len(datos):                                # se comprueba que quedó escrito
        raise OSError(f"No pude comprobar que el archivo quedó guardado en '{ruta}'")
    return {"ruta": str(ruta.resolve()), "nombre": ruta.name, "carpeta": str(ruta.resolve().parent), "bytes": len(datos), "equipo": _equipo(ruta.resolve())}


def _es_wsl():
    try:
        return "microsoft" in Path("/proc/version").read_text().lower()
    except OSError:
        return False


def _equipo(ruta):
    """Dónde está el archivo desde el punto de vista de quien lo busca: en WSL, la ruta que se ve desde Windows."""
    if _es_wsl():
        try:
            import subprocess
            w = subprocess.run(["wslpath", "-w", str(ruta)], capture_output=True, text=True, timeout=5).stdout.strip()
            if w:
                return {"sistema": "WSL", "ruta_windows": w}
        except (OSError, subprocess.SubprocessError):
            pass
        return {"sistema": "WSL"}
    return {"sistema": os.name}


def abrir_carpeta(ruta):
    """Abre la carpeta del archivo en el explorador del sistema (y lo marca, si el sistema lo permite)."""
    import subprocess
    p = Path(ruta).expanduser()
    if not p.exists():
        raise FileNotFoundError(f"No existe '{p}'")
    carpeta = p if p.is_dir() else p.parent
    if os.name == "nt":
        if p.is_file():
            subprocess.Popen(["explorer", "/select,", str(p)])
        else:
            os.startfile(str(carpeta))                                            # noqa: S606 (solo Windows)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", "-R", str(p)] if p.is_file() else ["open", str(carpeta)])
    elif _es_wsl():
        w = _equipo(p)
        subprocess.Popen(["explorer.exe", f"/select,{w['ruta_windows']}" if p.is_file() and w.get("ruta_windows") else str(carpeta)])
    else:
        subprocess.Popen(["xdg-open", str(carpeta)])
    return {"ok": True}


def listar(ruta=None):
    """Contenido de una carpeta para el explorador: subcarpetas y archivos CSV."""
    p = Path(ruta).expanduser() if ruta else Path.home()
    if not p.is_dir():
        p = p.parent if p.parent.is_dir() else Path.home()
    p = p.resolve()
    dirs, files = [], []
    try:
        for e in sorted(p.iterdir(), key=lambda x: x.name.lower()):
            if e.name.startswith("."):
                continue
            try:
                if e.is_dir():
                    dirs.append(e.name)
                elif e.suffix.lower() in (".csv", ".txt"):
                    files.append(e.name)
            except OSError:
                continue
    except OSError as ex:
        raise PermissionError(f"No se puede leer la carpeta '{p}': {ex}")
    raices = [{"n": "Inicio", "r": str(Path.home())}]
    for nombre, cands in (("Escritorio", ("Desktop", "Escritorio", "OneDrive/Desktop", "OneDrive/Escritorio")),
                          ("Documentos", ("Documents", "Documentos", "OneDrive/Documents", "OneDrive/Documentos")),
                          ("Descargas", ("Downloads", "Descargas"))):
        for c in cands:
            q = Path.home() / c
            if q.is_dir():
                raices.append({"n": nombre, "r": str(q)})
                break
    if os.name == "nt":
        raices += [{"n": f"{c}:", "r": f"{c}:\\"} for c in "CDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{c}:\\")]
    else:
        raices.append({"n": "/", "r": "/"})
    ej = Path(__file__).resolve().parents[3] / "003_Ejemplos"
    if ej.is_dir():
        raices.append({"n": "Ejemplos", "r": str(ej)})
    return {"ruta": str(p), "padre": str(p.parent) if p.parent != p else None, "dirs": dirs, "archivos": files, "raices": raices}


def _cargar(tipo, ruta):
    if tipo == "portico3d":
        from ..portico3d.entrada import cargar_modelo
    elif tipo == "portico":
        from ..portico.entrada import cargar_modelo
    elif tipo == "emparrillado":
        from ..emparrillado.entrada import cargar_modelo
    elif tipo == "reticulado":
        from ..reticulado.entrada import cargar_modelo
    else:
        from ..soldadura.entrada import cargar_csv as cargar_modelo
    return cargar_modelo(ruta)


def revisar(doc):
    """Carga el modelo con el cargador real.  → {ok, error, linea, bloque, fila, avisos}."""
    tipo = doc.get("tipo")
    if tipo not in ESQUEMAS:
        return {"ok": False, "error": "Falta el tipo de estructura", "avisos": []}
    texto, mapa = csvio.a_texto(doc)
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "modelo.csv"
        p.write_text(texto, encoding="utf-8")
        try:
            m = _cargar(tipo, p)
        except Exception as e:                                                        # ErrorDeEntrada u otro error de los datos
            msg = str(e)
            out = {"ok": False, "error": msg, "avisos": []}
            g = re.search(r"l[ií]nea (\d+)", msg)
            if g and int(g.group(1)) in mapa and mapa[int(g.group(1))]:
                out["bloque"], out["fila"] = mapa[int(g.group(1))]
            else:
                g = re.search(r"[Bb]loque ([A-ZÁÉÍÓÚ ]+?)(?:[,:\s(]|$)", msg)
                if g:
                    out["bloque"], out["fila"] = g.group(1).strip(), -1
            return out
    return {"ok": True, "error": None, "avisos": [str(a) for a in getattr(m, "avisos", [])]}


def calcular(ruta, doc):
    """Guarda en 'ruta' y corre el programa del tipo de estructura.  → {rc, texto, informe (id/archivo) | None}."""
    r = guardar(ruta, doc)
    from ..despachador import main
    buf = io.StringIO()
    with _LOCK, contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        try:
            rc = main([r["ruta"]])
        except SystemExit as e:
            rc = e.code if isinstance(e.code, int) else 1
        except Exception as e:
            print(f"ERROR: {e}")
            rc = 1
    salida = Path(r["ruta"]).with_name(Path(r["ruta"]).stem + "_salida")
    informe = None
    if rc == 0 and salida.is_dir():
        sid = secrets.token_urlsafe(6)
        _SALIDAS[sid] = salida
        h = salida / "informe.html"
        if not h.exists():
            hs = sorted(salida.glob("*.html"))
            h = hs[0] if hs else None
        if h:
            informe = f"/salida/{sid}/{h.name}"
    return {"rc": rc, "texto": buf.getvalue(), "informe": informe, "carpeta": str(salida), "ruta": r["ruta"], "nombre": r["nombre"], "guardado": r}


def bibliotecas():
    out = {"materiales": [], "electrodos": [], "perfiles": []}
    try:
        from ..biblioteca import biblioteca as b
        out["archivo_materiales"] = str(b.archivo())
        out["existe_materiales"] = b.archivo().is_file()
        out["materiales"] = [{"n": str(n), "t": t} for n, t in b.listar()]
    except Exception:
        pass
    try:
        from ..biblioteca import electrodos as e
        if e.existe():
            out["electrodos"] = [{"n": str(n), "t": t} for n, t in e.listar()]
    except Exception:
        pass
    try:
        from ..biblioteca import perfiles as p
        out["archivo_perfiles"] = str(p.archivo())
        out["existe_perfiles"] = p.archivo().is_file()
        tit = p.titulos()
        out["perfiles"] = [{"n": str(n), "t": t, "f": f, "nm": tit.get(str(n), t)} for n, t, f in p.listar()]
    except Exception:
        pass
    from ..soldadura.datos import ELECTRODOS
    out["electrodos_tabla"] = list(ELECTRODOS)
    return out


def ficha(tipo, lib, uf, ul, destino="3d"):
    """Valores de un material (o electrodo) de la biblioteca en las unidades del modelo, para mostrarlos en el editor."""
    from ..biblioteca import biblioteca as b, electrodos as e
    try:
        if tipo == "perfil":
            from ..biblioteca import perfiles as p
            campos, ref, av = p.datos_modelo(lib, destino, ul)
            return {"ok": True, "valores": campos, "ref": ref, "avisos": av}
        if tipo == "electrodo":
            sut, sy, tau = e.datos(lib)
            from ..portico3d.entrada import _U_FUERZA, _U_LONG
            k = 1e6 * _U_LONG[ul.lower()] ** 2 / _U_FUERZA[uf.lower()]
            return {"ok": True, "valores": {"sut": sut and sut * k, "sy": sy and sy * k, "tau_adm": tau and tau * k}}
        d = b.datos_modelo(lib, uf, ul)
        return {"ok": True, "valores": {"e": d["E"], "g": d["G"], "nu": d["nu"], "fy": d["fy"], "sut": d["sut"], "rho": d["rho"]}}
    except Exception as ex:
        return {"ok": False, "error": str(ex)}


# ----------------------------------------------------------------------------------------------------------------------
# HTTP
# ----------------------------------------------------------------------------------------------------------------------
class Servidor(ThreadingHTTPServer):
    daemon_threads = True
    token = ""
    inicial = None


class Manejador(BaseHTTPRequestHandler):
    server_version = "StrutturaEditor"

    def log_message(self, *a):
        pass

    def _host_ok(self):
        h = (self.headers.get("Host") or "").lower()
        return h in (f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}")

    def _enviar(self, codigo, cuerpo: bytes, tipo="application/json; charset=utf-8"):
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(cuerpo)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(cuerpo)

    def _json(self, obj, codigo=200):
        self._enviar(codigo, json.dumps(obj, ensure_ascii=False).encode("utf-8"))

    def do_GET(self):
        if not self._host_ok():
            return self._enviar(403, b"host no permitido", "text/plain")
        ruta = unquote(urlparse(self.path).path)
        if ruta == "/":
            html = (WEB / "editor.html").read_text(encoding="utf-8")
            cfg = {"token": self.server.token, "version": __version__, "esquemas": ESQUEMAS, "inicial": self.server.inicial}
            html = html.replace("/*__CFG__*/", "window.CFG = " + json.dumps(cfg, ensure_ascii=False).replace("</", "<\\/") + ";")
            return self._enviar(200, html.encode("utf-8"), "text/html; charset=utf-8")
        if ruta.startswith("/static/"):
            f = (WEB / ruta[8:]).resolve()
            if f.parent == WEB.resolve() and f.is_file():
                return self._enviar(200, f.read_bytes(), (mimetypes.guess_type(f.name)[0] or "text/plain") + "; charset=utf-8")
        m = re.match(r"^/salida/([\w-]+)/(.+)$", ruta)
        if m and m.group(1) in _SALIDAS:
            base = _SALIDAS[m.group(1)].resolve()
            f = (base / m.group(2)).resolve()
            if base in f.parents and f.is_file():
                return self._enviar(200, f.read_bytes(), (mimetypes.guess_type(f.name)[0] or "application/octet-stream") + "; charset=utf-8")
        self._enviar(404, b"no encontrado", "text/plain")

    def do_POST(self):
        if not self._host_ok() or self.headers.get("X-Struttura-Token") != self.server.token:
            return self._json({"error": "pedido no autorizado"}, 403)
        n = int(self.headers.get("Content-Length") or 0)
        try:
            d = json.loads(self.rfile.read(n) or b"{}")
        except ValueError:
            return self._json({"error": "pedido mal formado"}, 400)
        api = urlparse(self.path).path
        try:
            if api == "/api/nuevo":
                return self._json({"doc": csvio.doc_nuevo(d["tipo"]), "ruta": None, "nombre": "sin título"})
            if api == "/api/abrir":
                return self._json(abrir(d["ruta"]))
            if api == "/api/listar":
                return self._json(listar(d.get("ruta")))
            if api == "/api/existe":
                p = Path(d["ruta"]).expanduser()
                if p.suffix.lower() not in (".csv", ".txt"):
                    p = p.with_suffix(".csv")
                return self._json({"existe": p.exists(), "ruta": str(p)})
            if api == "/api/guardar":
                return self._json(guardar(d["ruta"], d["doc"]))
            if api == "/api/revisar":
                return self._json(revisar(d["doc"]))
            if api == "/api/calcular":
                return self._json(calcular(d["ruta"], d["doc"]))
            if api == "/api/abrir_carpeta":
                return self._json(abrir_carpeta(d["ruta"]))
            if api == "/api/ficha":
                return self._json(ficha(d["tipo"], d["lib"], d.get("unidad_fuerza") or "N", d.get("unidad_longitud") or "mm", d.get("destino") or "3d"))
            if api == "/api/bibliotecas":
                return self._json(bibliotecas())
            if api == "/api/salir":
                self._json({"ok": True})
                threading.Thread(target=self.server.shutdown, daemon=True).start()
                return
        except (OSError, ValueError, KeyError) as e:
            return self._json({"error": str(e)}, 400)
        except Exception as e:                                                        # error inesperado: se informa, el servidor sigue
            return self._json({"error": f"{type(e).__name__}: {e}"}, 500)
        self._json({"error": "pedido desconocido"}, 404)


def iniciar(archivo=None, puerto=0, abrir_navegador=True, bloquear=True):
    srv = Servidor(("127.0.0.1", puerto), Manejador)
    srv.token = secrets.token_urlsafe(16)
    if archivo:
        try:
            srv.inicial = abrir(archivo)
        except Exception as e:
            print(f"No se pudo abrir '{archivo}': {e}", file=sys.stderr)
    url = f"http://127.0.0.1:{srv.server_port}/"
    print(f"Struttura v{__version__} · Editor visual\n  {url}\n  (Ctrl+C o el botón «Salir» de la página cierran el editor)")
    if abrir_navegador:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    if bloquear:
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            srv.server_close()
    return srv


def main(argv=None):
    a = [x for x in (argv if argv is not None else sys.argv[1:]) if x != "--editor"]
    iniciar(a[0] if a else None)
    return 0
