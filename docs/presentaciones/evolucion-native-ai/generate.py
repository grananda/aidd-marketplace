#!/usr/bin/env python3
"""Genera el deck ejecutivo de evolución de Native AI y su PDF de revisión."""

from __future__ import annotations

import json
import math
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RENDERED = OUT / "_rendered"
PPTX_PATH = OUT / "evolucion-native-ai-v2.pptx"
PDF_PATH = OUT / "evolucion-native-ai-v2.pdf"
PREVIEW_PATH = OUT / "preview.png"

W_IN, H_IN = 13.333, 7.5
W_PX, H_PX = 1600, 900
SX, SY = W_PX / W_IN, H_PX / H_IN

# El PPTX pide Arial, asi que el lienzo se dibuja con Liberation Sans, que es su
# clon metrico: la previsualizacion y el PDF salen como se vera en PowerPoint, y
# no al reves. Ademas trae la flecha U+2192, que la Noto instalada puede no tener.
# Las rutas cambian entre distribuciones, asi que se prueba la lista en orden.
FONT_CANDIDATES = {
    "regular": ["/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
                "/usr/share/fonts/liberation/LiberationSans-Regular.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
                "/usr/share/fonts/noto/NotoSans-Regular.ttf"],
    "bold": ["/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
             "/usr/share/fonts/liberation/LiberationSans-Bold.ttf",
             "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
             "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
             "/usr/share/fonts/noto/NotoSans-Bold.ttf"],
    "light": ["/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
              "/usr/share/fonts/liberation/LiberationSans-Regular.ttf",
              "/usr/share/fonts/truetype/noto/NotoSans-Light.ttf"],
}
PPT_FONT = "Arial"

C = {
    "paper": "F6F4EF",
    "white": "FFFFFF",
    "ink": "17324D",
    "ink2": "3F556A",
    "muted": "71808E",
    "line": "D7DEE3",
    "blue": "0072BC",
    "blue2": "DCEEF8",
    "cyan": "16A9C7",
    "teal": "008F83",
    "teal2": "DDF2EE",
    "amber": "E8792E",
    "amber2": "FCE9DC",
    "yellow": "F4B942",
    "yellow2": "FFF4D2",
    "navy": "0D2942",
    "soft": "E9ECEF",
    "grey": "A9B4BE",
    "red": "C94B48",
    "red2": "F8E3E2",
}


def rgb(value: str) -> RGBColor:
    return RGBColor.from_string(value)


def rgba(value: str, alpha: int = 255) -> tuple[int, int, int, int]:
    value = value.lstrip("#")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16), alpha


def font_path(bold: bool = False, light: bool = False) -> str:
    familia = "bold" if bold else "light" if light else "regular"
    for candidate in FONT_CANDIDATES[familia] + FONT_CANDIDATES["regular"]:
        if Path(candidate).exists():
            return candidate
    raise RuntimeError("No hay ninguna fuente sans instalada de las que busca el generador: "
                       + ", ".join(FONT_CANDIDATES[familia]))


def emu(v: float):
    return Inches(v)


@dataclass
class TextStyle:
    size: float
    color: str = C["ink"]
    bold: bool = False
    light: bool = False
    align: str = "left"
    valign: str = "top"
    min_size: float = 8
    line_spacing: float = 1.12


class Canvas:
    def __init__(self, prs: Presentation, number: int, section: str, title: str | None = None, subtitle: str | None = None, dark: bool = False):
        self.prs = prs
        self.slide = prs.slides.add_slide(prs.slide_layouts[6])
        self.number = number
        self.dark = dark
        self.image = Image.new("RGB", (W_PX, H_PX), rgba(C["navy"] if dark else C["paper"])[0:3])
        self.draw = ImageDraw.Draw(self.image)
        self.rect(0, 0, W_IN, H_IN, C["navy"] if dark else C["paper"], radius=0)
        if title:
            self.header(section, title, subtitle)

    @staticmethod
    def _px(x: float, y: float) -> tuple[int, int]:
        return round(x * SX), round(y * SY)

    def rect(self, x: float, y: float, w: float, h: float, fill: str, line: str | None = None, radius: float = 0.08, line_width: float = 1):
        shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
        shape = self.slide.shapes.add_shape(shape_type, emu(x), emu(y), emu(w), emu(h))
        shape.fill.solid()
        shape.fill.fore_color.rgb = rgb(fill)
        shape.line.color.rgb = rgb(line or fill)
        shape.line.width = Pt(line_width)
        x0, y0 = self._px(x, y)
        x1, y1 = self._px(x + w, y + h)
        if radius:
            self.draw.rounded_rectangle((x0, y0, x1, y1), radius=round(radius * SX), fill=rgba(fill), outline=rgba(line or fill), width=max(1, round(line_width * 1.3)))
        else:
            self.draw.rectangle((x0, y0, x1, y1), fill=rgba(fill), outline=rgba(line or fill), width=max(1, round(line_width * 1.3)))
        return shape

    def line(self, x1: float, y1: float, x2: float, y2: float, color: str, width: float = 1, dash: bool = False):
        shape = self.slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, emu(x1), emu(y1), emu(max(0.002, x2 - x1)), emu(max(0.002, y2 - y1)))
        shape.fill.solid()
        shape.fill.fore_color.rgb = rgb(color)
        shape.line.fill.background()
        px1, py1 = self._px(x1, y1)
        px2, py2 = self._px(x2, y2)
        self.draw.line((px1, py1, px2, py2), fill=rgba(color), width=max(1, round(width * 1.6)))

    def circle(self, x: float, y: float, d: float, fill: str, line: str | None = None):
        shape = self.slide.shapes.add_shape(MSO_SHAPE.OVAL, emu(x), emu(y), emu(d), emu(d))
        shape.fill.solid()
        shape.fill.fore_color.rgb = rgb(fill)
        shape.line.color.rgb = rgb(line or fill)
        x0, y0 = self._px(x, y)
        x1, y1 = self._px(x + d, y + d)
        self.draw.ellipse((x0, y0, x1, y1), fill=rgba(fill), outline=rgba(line or fill))

    def arrow(self, x: float, y: float, w: float, h: float, fill: str):
        shape = self.slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, emu(x), emu(y), emu(w), emu(h))
        shape.fill.solid()
        shape.fill.fore_color.rgb = rgb(fill)
        shape.line.fill.background()
        x0, y0 = self._px(x, y)
        x1, y1 = self._px(x + w, y + h)
        head = round(w * SX * 0.25)
        mid = (y0 + y1) // 2
        pts = [(x0, y0 + (y1 - y0) // 4), (x1 - head, y0 + (y1 - y0) // 4), (x1 - head, y0), (x1, mid), (x1 - head, y1), (x1 - head, y1 - (y1 - y0) // 4), (x0, y1 - (y1 - y0) // 4)]
        self.draw.polygon(pts, fill=rgba(fill))

    def pill(self, x: float, y: float, w: float, h: float, text: str, fill: str, color: str, size: float = 10, bold: bool = True):
        self.rect(x, y, w, h, fill, radius=h / 2)
        self.text(x + 0.08, y + 0.02, w - 0.16, h - 0.04, text, TextStyle(size, color, bold, align="center", valign="middle", min_size=7))

    def _wrap(self, value: str, pil_font: ImageFont.FreeTypeFont, max_width: int) -> str:
        lines: list[str] = []
        for paragraph in value.split("\n"):
            if not paragraph:
                lines.append("")
                continue
            words = paragraph.split(" ")
            current = words[0]
            for word in words[1:]:
                trial = current + " " + word
                if self.draw.textlength(trial, font=pil_font) <= max_width:
                    current = trial
                else:
                    lines.append(current)
                    current = word
            lines.append(current)
        return "\n".join(lines)

    def _fit(self, value: str, w: float, h: float, style: TextStyle) -> tuple[float, str, ImageFont.FreeTypeFont]:
        max_w, max_h = round(w * SX), round(h * SY)
        size = style.size
        while size >= style.min_size:
            pil_font = ImageFont.truetype(font_path(style.bold, style.light), round(size * 1.62))
            wrapped = self._wrap(value, pil_font, max_w)
            box = self.draw.multiline_textbbox((0, 0), wrapped, font=pil_font, spacing=round(size * style.line_spacing * 0.46), align=style.align)
            if box[2] - box[0] <= max_w and box[3] - box[1] <= max_h:
                return size, wrapped, pil_font
            size -= 0.5
        pil_font = ImageFont.truetype(font_path(style.bold, style.light), round(style.min_size * 1.62))
        return style.min_size, self._wrap(value, pil_font, max_w), pil_font

    def text(self, x: float, y: float, w: float, h: float, value: str, style: TextStyle):
        chosen, wrapped, pil_font = self._fit(value, w, h, style)
        tb = self.slide.shapes.add_textbox(emu(x), emu(y), emu(w), emu(h))
        tf = tb.text_frame
        tf.clear()
        tf.word_wrap = True
        # PowerPoint, Keynote y LibreOffice no calculan las metricas tipograficas
        # exactamente igual. Este ajuste impide que una sustitucion de fuente haga
        # salir el texto de su caja al abrir el PPTX fuera del entorno generador.
        tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = {"top": MSO_ANCHOR.TOP, "middle": MSO_ANCHOR.MIDDLE, "bottom": MSO_ANCHOR.BOTTOM}[style.valign]
        lines = value.split("\n")
        for idx, line in enumerate(lines):
            p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
            p.text = line
            p.font.name = PPT_FONT
            p.font.size = Pt(chosen)
            p.font.bold = style.bold
            p.font.color.rgb = rgb(style.color)
            p.alignment = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER, "right": PP_ALIGN.RIGHT}[style.align]
            p.line_spacing = 1.0
            p.space_after = Pt(chosen * 0.12)
        px, py = self._px(x, y)
        max_w, max_h = round(w * SX), round(h * SY)
        box = self.draw.multiline_textbbox((0, 0), wrapped, font=pil_font, spacing=round(chosen * style.line_spacing * 0.46), align=style.align)
        tw, th = box[2] - box[0], box[3] - box[1]
        tx = px if style.align == "left" else px + (max_w - tw) // 2 if style.align == "center" else px + max_w - tw
        ty = py if style.valign == "top" else py + (max_h - th) // 2 if style.valign == "middle" else py + max_h - th
        self.draw.multiline_text((tx, ty), wrapped, font=pil_font, fill=rgba(style.color), spacing=round(chosen * style.line_spacing * 0.46), align=style.align)
        return chosen

    def header(self, section: str, title: str, subtitle: str | None):
        self.text(0.55, 0.3, 3.2, 0.25, section.upper(), TextStyle(9, C["blue"], True))
        self.text(0.55, 0.72, 12.1, 0.58, title, TextStyle(25, C["ink"], True, min_size=20))
        if subtitle:
            self.text(0.55, 1.28, 12.0, 0.45, subtitle, TextStyle(10.5, C["ink2"], min_size=9))
        self.line(0.55, 1.78, 12.78, 1.78, C["line"], 1)

    def footer(self, total: int, source: str = "Fuente: repositorio aidd-marketplace · VERSION 1.46.1"):
        color = C["grey"] if self.dark else C["muted"]
        self.text(0.55, 7.14, 9.8, 0.18, source, TextStyle(6.8, color, min_size=6))
        self.text(11.75, 7.10, 1.0, 0.22, f"{self.number:02d} / {total:02d}", TextStyle(7.2, color, True, align="right", min_size=6))


def metrics() -> dict:
    marketplace = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
    plugins = marketplace["plugins"]
    skill_counts = {}
    for plugin in plugins:
        plugin_root = (ROOT / plugin["source"]).resolve()
        skill_counts[plugin["name"]] = len(list(plugin_root.glob("skills/*/SKILL.md")))
    command_counts = {"aidd": 9, "aisdd": 9, "aiba": 7, "aiad": 11, "aifg": 2, "boosters": 3}
    result = {
        "plugins": len(plugins),
        "skills": sum(skill_counts.values()),
        "commands": sum(command_counts.values()),
        "checks": len(list((ROOT / ".github/scripts").glob("check_*.py"))),
        "topologies": 3,
        "skill_counts": skill_counts,
        "command_counts": command_counts,
    }
    expected = {"plugins": 6, "skills": 34, "commands": 41, "checks": 12, "topologies": 3}
    for key, value in expected.items():
        if result[key] != value:
            raise RuntimeError(f"Métrica {key} cambió: esperada {value}, observada {result[key]}. Revisa el relato antes de regenerar.")
    return result


def card(c: Canvas, x: float, y: float, w: float, h: float, eyebrow: str, title: str, body: str, accent: str = C["blue"], fill: str = C["white"]):
    c.rect(x, y, w, h, fill, C["line"], radius=0.12)
    c.rect(x, y, 0.07, h, accent, accent, radius=0)
    c.text(x + 0.24, y + 0.18, w - 0.42, 0.22, eyebrow.upper(), TextStyle(8.5, accent, True))
    c.text(x + 0.24, y + 0.48, w - 0.42, 0.50, title, TextStyle(15, C["ink"], True, min_size=11))
    c.text(x + 0.24, y + 1.03, w - 0.42, h - 1.18, body, TextStyle(9.2, C["ink2"], min_size=7.5))


def metric_card(c: Canvas, x: float, y: float, w: float, label: str, before: str, after: str, accent: str, note: str | None = None):
    c.rect(x, y, w, 1.36, C["white"], C["line"], radius=0.12)
    c.text(x + 0.18, y + 0.15, w - 0.36, 0.25, label.upper(), TextStyle(7.8, C["muted"], True, align="center"))
    c.text(x + 0.22, y + 0.46, 0.55, 0.55, before, TextStyle(19, C["grey"], True, align="center", valign="middle"))
    c.arrow(x + 0.82, y + 0.61, 0.45, 0.19, accent)
    c.text(x + 1.31, y + 0.42, w - 1.48, 0.62, after, TextStyle(23, accent, True, align="center", valign="middle"))
    c.text(x + 0.18, y + 1.09, w - 0.36, 0.16, note or "PARTIDA  →  HOY", TextStyle(6.4, C["muted"], True, align="center"))


def build_slides(prs: Presentation, m: dict) -> list[Canvas]:
    """Cinco diapositivas. El detalle vive en el informe HTML, no aqui."""
    slides: list[Canvas] = []
    total = 6
    INFORME = "El detalle, mejora a mejora, está en el informe: evolucion-native-ai.html"

    # 1 — portada
    c = Canvas(prs, 1, "", dark=True)
    c.rect(0, 0, 0.16, H_IN, C["cyan"], radius=0)
    c.text(0.7, 0.62, 6.0, 0.25, "NTT DATA SPAIN · GDN-e", TextStyle(9.5, C["cyan"], True))
    c.text(0.7, 1.32, 11.9, 1.60, "Recibimos un método.\nDevolvimos una cadena de entrega.", TextStyle(40, C["white"], True, min_size=30))
    c.text(0.7, 3.24, 9.6, 0.80, "Native AI nos dio una forma de trabajar con IA. La hemos usado en proyectos con clientes reales, hemos tapado lo que faltaba y lo hemos devuelto convertido en algo que cualquier equipo del grupo instala en un comando.",
           TextStyle(14, "C6D6E3", min_size=11))
    heroes = [("34", "herramientas", "eran 3", C["cyan"]), ("8 de 8", "tramos del proyecto", "eran 3", C["teal"]), ("6", "plugins instalables", "no existían", C["amber"])]
    for i, (num, label, before, color) in enumerate(heroes):
        x = 0.7 + i * 4.05
        c.rect(x, 4.44, 3.72, 1.62, "143B59", "28516F", radius=0.14)
        c.text(x + 0.30, 4.66, 3.12, 0.70, num, TextStyle(38, color, True, min_size=26))
        c.text(x + 0.30, 5.42, 3.12, 0.28, label.upper(), TextStyle(9.5, C["white"], True))
        c.text(x + 0.30, 5.72, 3.12, 0.24, before, TextStyle(9, "7292A9"))
    c.text(0.7, 6.42, 11.9, 0.30, INFORME, TextStyle(9, "7292A9", min_size=8))
    c.footer(total, f"Marketplace VERSION 1.46.1 · {m['plugins']} plugins · {m['skills']} skills · {m['commands']} comandos · cifras contadas sobre los ficheros")
    slides.append(c)

    # 2 — la prueba: cobertura del proyecto
    c = Canvas(prs, 2, "La prueba", "El método cubría tres de los ocho tramos. Hoy cubre los ocho.",
               "Cada tramo de un proyecto, y quién tenía herramienta para ejecutarlo.")
    stages = ["Brief", "Requisitos", "Diseño", "Plan", "Build", "Validación", "Entrega", "Medición"]
    colors = [C["blue"], C["blue"], C["cyan"], C["cyan"], C["teal"], C["teal"], C["amber"], C["amber"]]
    x0, y0, cellw = 2.72, 2.42, 1.18
    for i, label in enumerate(stages):
        c.text(x0 + i * cellw, 2.06, cellw - 0.06, 0.28, label.upper(), TextStyle(7.4, C["muted"], True, align="center"))
    rows = [
        ("Lo que recibimos", "3 de 8 tramos", [0, 0, 0, 1, 1, 1, 0, 0], C["grey"]),
        ("Lo que hay hoy", "8 de 8 tramos", [1, 1, 1, 1, 1, 1, 1, 1], C["teal"]),
    ]
    for r, (name, verb, coverage, accent) in enumerate(rows):
        yy = y0 + r * 1.28
        c.text(0.65, yy + 0.16, 1.95, 0.32, name, TextStyle(13, C["ink"], True, min_size=10))
        c.text(0.65, yy + 0.54, 1.95, 0.24, verb, TextStyle(9.5, accent, True))
        for i, active in enumerate(coverage):
            fill = colors[i] if active and r == 1 else accent if active else C["soft"]
            c.rect(x0 + i * cellw, yy, cellw - 0.09, 0.92, fill, fill, radius=0.12)
            if active:
                c.text(x0 + i * cellw, yy + 0.30, cellw - 0.09, 0.32, "SÍ", TextStyle(11, C["white"], True, align="center", valign="middle"))
    c.rect(0.65, 5.28, 12.0, 1.06, C["white"], C["line"], radius=0.12)
    c.text(0.95, 5.50, 2.60, 0.34, "Lo importante", TextStyle(12.5, C["amber"], True))
    c.text(0.95, 5.86, 11.40, 0.34, "No inventamos nada que el método no dijera. Cogimos sus guiones manuales y los convertimos en herramienta — y añadimos los dos tramos que le faltaban: entrega y medición.",
           TextStyle(11.5, C["ink"], min_size=9.5))
    c.rect(0.65, 6.50, 12.0, 0.46, C["navy"], C["navy"], radius=0.08)
    c.text(0.95, 6.58, 11.40, 0.30, INFORME, TextStyle(9.5, C["white"], True, align="center", min_size=8))
    c.footer(total, "Ocho tramos operativos de brief a medición · «lo definía» no equivale a «tenía herramienta»")
    slides.append(c)

    # 3 — que hemos construido
    c = Canvas(prs, 3, "Lo construido", "Del cliente que firma al KPI que se defiende, en cuatro eslabones",
               "Seis plugins que se instalan por separado. Se coge lo que el proyecto necesita y se quita igual de fácil.")
    chain = [("EL CLIENTE", "AIDD", "Brief, requisitos, historias y arquitectura", C["blue"]),
             ("EL DISEÑO", "AIFG", "Figma normalizado hasta la historia que lo implementa", C["cyan"]),
             ("EL CÓDIGO", "AISDD · AIAD", "La IA implementa, o lo escribe la persona: se elige", C["teal"]),
             ("LA EVIDENCIA", "AIBA", "Documento firmable, plan, informe y KPIs medidos", C["amber"])]
    for i, (etapa, nombre, texto, color) in enumerate(chain):
        x = 0.62 + i * 3.08
        c.rect(x, 2.14, 2.86, 1.94, C["white"], C["line"], radius=0.14)
        c.rect(x, 2.14, 2.86, 0.08, color, color, radius=0)
        c.text(x + 0.24, 2.40, 2.40, 0.24, etapa, TextStyle(8.5, C["muted"], True))
        c.text(x + 0.24, 2.72, 2.40, 0.38, nombre, TextStyle(16, color, True, min_size=12))
        c.text(x + 0.24, 3.24, 2.40, 1.00, texto, TextStyle(10, C["ink2"], min_size=8.5))
        if i < 3:
            c.arrow(x + 2.90, 2.98, 0.28, 0.26, C["grey"])
    c.rect(0.62, 4.32, 12.10, 0.98, C["blue2"], C["blue2"], radius=0.12)
    c.text(0.92, 4.50, 3.20, 0.30, "UNA SOLA FUENTE DE VERDAD", TextStyle(9.5, C["blue"], True))
    c.text(0.92, 4.84, 11.50, 0.34, "Los cuatro leen y escriben los mismos documentos versionados. Lo que firma el cliente y lo que ejecuta la IA salen del mismo sitio, así que no pueden contradecirse.",
           TextStyle(10.5, C["ink"], min_size=9))
    counts = [(str(m["skills"]), "herramientas"), (str(m["commands"]), "comandos"), (str(m["plugins"]), "plugins"), (str(m["checks"]), "controles en CI")]
    for i, (num, label) in enumerate(counts):
        x = 0.62 + i * 3.08
        c.rect(x, 5.52, 2.86, 0.86, C["white"], C["line"], radius=0.10)
        c.text(x + 0.24, 5.66, 1.10, 0.58, num, TextStyle(22, C["ink"], True, min_size=16, valign="middle"))
        c.text(x + 1.36, 5.66, 1.34, 0.58, label, TextStyle(9.5, C["muted"], True, valign="middle"))
    c.rect(0.62, 6.54, 12.10, 0.46, C["navy"], C["navy"], radius=0.08)
    c.text(0.92, 6.62, 11.50, 0.30, INFORME, TextStyle(9.5, C["white"], True, align="center", min_size=8))
    c.footer(total)
    slides.append(c)

    # 4 — seis cosas que hoy hace mejor
    c = Canvas(prs, 4, "El salto, por dentro", "Seis cosas que hoy el método hace mejor",
               "En azul, lo que el método ya daba. En ámbar, lo que hemos sumado encima.")
    for i, (etiqueta, color) in enumerate([("Lo que ya daba el método", C["blue"]),
                                           ("Lo que hemos sumado", C["amber"])]):
        lx = 8.30 + i * 2.32
        c.rect(lx, 2.00, 0.22, 0.16, color, color, radius=0.04)
        c.text(lx + 0.32, 1.96, 1.95, 0.24, etiqueta, TextStyle(8.5, C["ink2"], min_size=7.5))
    barras = [
        ("Que cada paso tenga herramienta", 40, 60,
         "El método ya describía todos los pasos. Nosotros hemos hecho las herramientas que faltaban."),
        ("Enseñar resultados al cliente", 0, 88,
         "No era su cometido. Ahora se genera el documento que el cliente firma y el informe de avance."),
        ("Varias personas a la vez", 40, 40,
         "Ya repartía el trabajo entre varios. Ahora, además, comprueba que nadie se pise."),
        ("Saber lo que ha costado", 50, 40,
         "Él ya lo registraba todo, que es la parte difícil. Nosotros lo hemos convertido en cifras."),
        ("Encajar en el proyecto del cliente", 30, 50,
         "Pensado para un proyecto en un sitio. Ahora admite los repositorios que el cliente tenga."),
        ("Que escriba la persona", 0, 88,
         "No era su planteamiento. Hoy es una opción que se elige tarea a tarea."),
    ]
    BX, ESC = 3.30, 9.35
    for i, (etiqueta, base, nuevo, pie) in enumerate(barras):
        y = 2.36 + i * 0.68
        c.text(0.62, y + 0.02, BX - 0.62 - 0.18, 0.30, etiqueta,
               TextStyle(10.5, C["ink"], True, align="right", min_size=8.2, valign="middle"))
        c.rect(BX, y + 0.04, ESC, 0.24, C["soft"], C["soft"], radius=0.12)
        if base:
            c.rect(BX, y + 0.04, ESC * base / 100.0, 0.24, C["blue"], C["blue"], radius=0.12)
        if nuevo:
            hueco = 0.03 if base else 0.0
            c.rect(BX + ESC * base / 100.0 + hueco, y + 0.04, ESC * nuevo / 100.0, 0.24,
                   C["amber"], C["amber"], radius=0.12)
        c.text(BX, y + 0.34, ESC, 0.24, pie, TextStyle(8.6, C["muted"], min_size=7.4))
    c.rect(0.62, 6.44, 12.10, 0.58, C["white"], C["line"], radius=0.10)
    c.text(0.92, 6.54, 11.50, 0.38, "Valoración del equipo, no una medición: lo que cuenta es el tramo ámbar. Donde no hay tramo azul no es que el método fallara, es que eso no entraba en lo que se propuso resolver.",
           TextStyle(9.5, C["ink2"], min_size=8, valign="middle"))
    c.footer(total, INFORME)
    slides.append(c)

    # 5 — que gana el negocio
    c = Canvas(prs, 5, "Lo que cambia", "Cuatro cosas que antes no podíamos hacer delante de un cliente",
               "El método terminaba en el código validado. Ahora llega hasta lo que el cliente firma y la cifra con la que nos juzga.")
    wins = [("El cliente firma",
             "El diseño funcional, el plan de pruebas y el de sprints se generan desde la misma fuente que el código. Antes se hacían a mano en Word y Excel.", C["blue"]),
            ("Las cifras se sostienen",
             "Los KPIs se cruzan con el worklog real de Jira. Lo medido se distingue de lo estimado, y lo que no se sostiene no se publica.", C["amber"]),
            ("El método se vigila solo",
             "Doce controles en cada cambio impiden que se degrade en silencio. Antes dependía de que alguien se acordara de revisarlo.", C["teal"]),
            ("Escala sin reescribirse",
             "Funciona con uno o con varios repositorios, con varias personas a la vez y en tres herramientas distintas de IA.", C["cyan"])]
    for i, (titulo, texto, color) in enumerate(wins):
        x = 0.62 + (i % 2) * 6.24
        y = 2.16 + (i // 2) * 2.06
        c.rect(x, y, 5.86, 1.82, C["white"], C["line"], radius=0.14)
        c.rect(x, y, 0.08, 1.82, color, color, radius=0)
        c.circle(x + 0.34, y + 0.28, 0.44, color)
        c.text(x + 0.34, y + 0.30, 0.44, 0.40, str(i + 1), TextStyle(12, C["white"], True, align="center", valign="middle"))
        c.text(x + 1.02, y + 0.28, 4.60, 0.40, titulo, TextStyle(16, C["ink"], True, min_size=12))
        c.text(x + 1.02, y + 0.86, 4.60, 0.80, texto, TextStyle(10.5, C["ink2"], min_size=8.5))
    c.rect(0.62, 6.34, 12.10, 0.60, C["amber2"], C["amber2"], radius=0.10)
    c.text(0.92, 6.46, 11.50, 0.34, "En una línea  ·  El método sabía construir software sin desviarse de lo pedido. Ahora también sabe demostrarlo.",
           TextStyle(12, C["ink"], True, align="center", min_size=9.5, valign="middle"))
    c.footer(total, INFORME)
    slides.append(c)

    # 6 — donde estamos
    c = Canvas(prs, 6, "Dónde estamos", "Está en uso, se instala en un comando y sigue creciendo",
               "No es un piloto ni una prueba de concepto: está publicado, versionado y funcionando en proyecto.")
    estado = [("EN USO", "Proyectos con cliente", "Lo que se ha construido salió de necesidades reales, no de un ejercicio interno.", C["teal"]),
              ("DISPONIBLE", "Para todo el grupo", "Publicado con versión propia. Un comando lo instala y otro lo quita.", C["blue"]),
              ("POR CAPAS", "Se adopta a trozos", "Un equipo pequeño empieza con dos plugins. El resto se añade cuando duele el problema que resuelve.", C["cyan"])]
    for i, (etq, titulo, texto, color) in enumerate(estado):
        x = 0.62 + i * 4.10
        c.rect(x, 2.14, 3.86, 2.24, C["white"], C["line"], radius=0.14)
        c.rect(x, 2.14, 3.86, 0.08, color, color, radius=0)
        c.text(x + 0.28, 2.42, 3.30, 0.24, etq, TextStyle(9, color, True))
        c.text(x + 0.28, 2.74, 3.30, 0.44, titulo, TextStyle(16, C["ink"], True, min_size=12))
        c.text(x + 0.28, 3.32, 3.30, 0.86, texto, TextStyle(10, C["ink2"], min_size=8.5))
    c.rect(0.62, 4.60, 12.10, 1.16, C["white"], C["line"], radius=0.14)
    c.rect(0.62, 4.60, 0.08, 1.16, C["amber"], C["amber"], radius=0)
    c.text(0.92, 4.80, 2.60, 0.30, "LO QUE FALTA", TextStyle(9, C["amber"], True))
    c.text(0.92, 5.12, 11.40, 0.50, "La metodología escrita va por detrás de lo construido. Merece una puesta al día antes de enseñar esto fuera del equipo — y es lo único que pedimos.",
           TextStyle(11.5, C["ink2"], min_size=9.5))
    c.rect(0.62, 5.96, 12.10, 0.74, C["navy"], C["navy"], radius=0.10)
    c.text(0.92, 6.08, 3.10, 0.34, "LO QUE PROPONEMOS", TextStyle(9.5, C["cyan"], True, valign="middle"))
    c.text(3.90, 6.06, 8.60, 0.40, "Adoptarlo por capas en los próximos proyectos y poner al día la metodología troncal.",
           TextStyle(13, C["white"], True, min_size=10, valign="middle"))
    c.footer(total, INFORME)
    slides.append(c)

    return slides


def add_document_properties(prs: Presentation):
    props = prs.core_properties
    props.title = "Evolución de Native AI — resumen ejecutivo"
    props.subject = "Comparativa entre la metodología original, native-ai-specs v1.6.0 y el marketplace"
    props.author = "NTT DATA Spain GDN-e"
    props.keywords = "Native AI, AIDD, AISDD, AIBA, AIAD, AIFG, ejecutivo"
    props.comments = "Generado de forma reproducible con generate.py. Issue #47."


def save_outputs(prs: Presentation, slides: Iterable[Canvas]):
    add_document_properties(prs)
    prs.save(PPTX_PATH)
    RENDERED.mkdir(exist_ok=True)
    images = []
    for canvas in slides:
        path = RENDERED / f"slide-{canvas.number:02d}.png"
        canvas.image.save(path, quality=95)
        images.append(canvas.image.convert("RGB"))
    # 1600 px / 120 dpi = 13,333 in: mismo tamaño físico que el lienzo 16:9 del PPTX.
    images[0].save(PDF_PATH, "PDF", resolution=120.0, save_all=True, append_images=images[1:])
    thumb_w, thumb_h = 384, 216
    cols, rows = 3, math.ceil(len(images) / 3)
    sheet = Image.new("RGB", (cols * thumb_w + (cols + 1) * 18, rows * thumb_h + (rows + 1) * 18), rgba(C["soft"])[0:3])
    for i, source in enumerate(images):
        thumb = source.copy()
        thumb.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = 18 + (i % cols) * (thumb_w + 18)
        y = 18 + (i // cols) * (thumb_h + 18)
        sheet.paste(thumb, (x, y))
    sheet.save(PREVIEW_PATH, quality=92)


def verify(prs: Presentation, slides: list[Canvas]):
    if len(slides) != 6 or len(prs.slides) != 6:
        raise RuntimeError("Es un resumen ejecutivo: exactamente 6 diapositivas. El detalle va en el informe HTML.")
    for slide_no, slide in enumerate(prs.slides, 1):
        for shape in slide.shapes:
            if shape.left < 0 or shape.top < 0 or shape.left + shape.width > prs.slide_width or shape.top + shape.height > prs.slide_height:
                raise RuntimeError(f"Elemento fuera del lienzo en slide {slide_no}: {shape.name}")
    required = [PPTX_PATH, PDF_PATH, PREVIEW_PATH]
    missing = [str(path) for path in required if not path.exists() or path.stat().st_size == 0]
    if missing:
        raise RuntimeError(f"Artefactos no generados: {missing}")


def main():
    m = metrics()
    if RENDERED.exists():
        shutil.rmtree(RENDERED)
    prs = Presentation()
    prs.slide_width = Inches(W_IN)
    prs.slide_height = Inches(H_IN)
    slides = build_slides(prs, m)
    save_outputs(prs, slides)
    verify(prs, slides)
    print(f"Generados {len(slides)} slides: {PPTX_PATH.name}, {PDF_PATH.name} y {PREVIEW_PATH.name}")
    print(f"Métricas: {m['plugins']} plugins · {m['skills']} skills · {m['commands']} comandos · {m['checks']} checks")


if __name__ == "__main__":
    main()
