"""Ayuda para dibujar esquemas de uso (cajas y flechas) en SVG, para las memorias.  Uso: e = Esquema(ancho, alto); e.caja(...); e.flecha(...); e.svg()"""
from html import escape

COL = {"inicio": ("#dfe9ec", "#5d8794"), "dato": ("#f6f1e4", "#b39b5a"), "calc": ("#e6f0e6", "#6f9a72"), "sal": ("#f2e6e0", "#b3745a"), "neutro": ("#f1f3f4", "#8a979c")}


class Esquema:
    def __init__(self, ancho, alto):
        self.w, self.h, self.p = ancho, alto, []

    def caja(self, x, y, w, h, titulo, lineas=(), tipo="neutro", alin="start"):
        fill, stroke = COL[tipo]
        self.p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="{fill}" stroke="{stroke}" stroke-width="1.4"/>')
        self.p.append(f'<text x="{x + 12}" y="{y + 21}" font-size="13.5" font-weight="700" fill="#22313a">{escape(titulo)}</text>')
        for i, l in enumerate(lineas):
            self.p.append(f'<text x="{x + 12}" y="{y + 42 + 17 * i}" font-size="12" fill="#33444e">{escape(l)}</text>')

    def flecha(self, x0, y0, x1, y1, rotulo="", dx=6):
        self.p.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="#6b7c85" stroke-width="1.6" marker-end="url(#p)"/>')
        if rotulo:
            self.p.append(f'<text x="{(x0 + x1) / 2 + dx}" y="{(y0 + y1) / 2 + 4}" font-size="11.5" font-style="italic" fill="#51626b">{escape(rotulo)}</text>')

    def linea(self, x0, y0, x1, y1):
        self.p.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="#6b7c85" stroke-width="1.6"/>')

    def svg(self):
        defs = '<defs><marker id="p" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" fill="#6b7c85"/></marker></defs>'
        return (f'<svg viewBox="0 0 {self.w} {self.h}" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI,Helvetica,Arial,sans-serif" '
                f'role="img" style="max-width:{self.w}px;background:#fff;border:1px solid #d5dde0;border-radius:10px">{defs}{"".join(self.p)}</svg>')


def esquema_modelo(titulo, plantilla, tipo, obligatorios, opcionales, salidas, revisar="--solo-esquema"):
    """Mapa de uso estándar de un programa con CSV por bloques.  obligatorios/opcionales: [(bloque, 'columnas o qué lleva')]; salidas: [líneas]."""
    n = max(len(obligatorios), len(opcionales))
    alto_b = 52
    e = Esquema(1000, 340 + n * (alto_b + 10) + 40)
    e.caja(250, 10, 500, 46, titulo, ["Partís de la plantilla y la completás por bloques"], "inicio")
    e.caja(20, 90, 960, 70, f"1 · Copiar {plantilla} y renombrarla", [f"En PROYECTO:  tipo;{tipo}   y las unidades (fuerza y longitud, coherentes entre sí)",
                                                                   "Las líneas que empiezan con # se ignoran; las columnas que no uses se dejan vacías"], "dato")
    e.flecha(500, 56, 500, 90)
    y0 = 212
    e.caja(20, y0 - 30, 470, 28, "2 · Bloques OBLIGATORIOS", [], "neutro")
    e.caja(510, y0 - 30, 470, 28, "Bloques OPCIONALES (según lo que necesites)", [], "neutro")
    e.flecha(500, 160, 255, y0 - 30)
    e.flecha(500, 160, 745, y0 - 30)
    for i, (b, c) in enumerate(obligatorios):
        e.caja(20, y0 + i * (alto_b + 10), 470, alto_b, b, [c], "dato")
    for i, (b, c) in enumerate(opcionales):
        e.caja(510, y0 + i * (alto_b + 10), 470, alto_b, b, [c], "neutro")
    y = y0 + n * (alto_b + 10) + 5
    e.caja(20, y, 960, 52, f"3 · Revisar y calcular", [f"python struttura.py MIARCHIVO.csv {revisar}   (dibuja los datos sin calcular)   →   luego sin el último argumento"], "calc")
    e.flecha(500, y - 10, 500, y)
    e.caja(20, y + 80, 960, 36 + 17 * len(salidas), "Resultado:  carpeta MIARCHIVO_salida/", salidas, "sal")
    e.flecha(500, y + 52, 500, y + 80)
    e.h = y + 80 + 36 + 17 * len(salidas) + 16
    return e.svg()
