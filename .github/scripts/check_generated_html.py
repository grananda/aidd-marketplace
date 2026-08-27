#!/usr/bin/env python3
"""Comprueba que los HTML de metodologia estan al dia y que las copias coinciden.

Dos fallos que se cuelan solos y no rompen nada visiblemente:

1. Editar un `.md` de `methodology/` y olvidar regenerar su `.html`. La version
   publicada sigue diciendo lo anterior, y nadie lo nota hasta que alguien la lee.
2. Tocar la copia de `aidd/` y no la de `aisdd/` (o al reves). Son espejo, pero
   nada lo hace cumplir.
"""
from __future__ import annotations

import filecmp
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RENDER = ROOT / "plugins/boosters/skills/booster-docs/scripts/render_docs_html.py"

# (md relativo a plugins/<plugin>/methodology, titulo forzado)
DOCS = [
    ("native-ai-aidd-sdd", "Native AI · AIDD-SDD — Metodología AI-Native"),
    ("native-ai-aidd-sdd-getting-started", "AIDD-SDD — Getting Started"),
]
ESPEJO = ["aidd", "aisdd"]          # deben ser identicos entre si
SUELTOS = [("aiad", "native-ai-aiad", "Native AI · AIAD — AI-Augmented Development"),
           ("aiba", "native-ai-aiba", "Native AI · AIBA — Análisis de negocio, entrega y medición")]

errors: list[str] = []


# El renderer estampa la fecha de generacion en la cabecera, asi que comparar
# byte a byte falla al dia siguiente aunque no haya cambiado nada. Lo que hay que
# comprobar es el CONTENIDO, no cuando se genero.
SELLO_FECHA = re.compile(r"Vista generada el \d{4}-\d{2}-\d{2}")


def contenido(path: Path) -> str:
    return SELLO_FECHA.sub("Vista generada el <fecha>",
                           path.read_text(encoding="utf-8", errors="replace"))


def iguales(a: Path, b: Path) -> bool:
    return contenido(a) == contenido(b)


def regenera(md: Path, titulo: str) -> Path:
    salida = Path(tempfile.mkdtemp()) / "out.html"
    subprocess.run(
        [sys.executable, str(RENDER), "--input", str(md), "--output", str(salida),
         "--title", titulo, "--no-mermaid-asset"],
        check=True, capture_output=True,
    )
    return salida


for stem, titulo in DOCS:
    fuentes = [ROOT / f"plugins/{p}/methodology/{stem}.md" for p in ESPEJO]
    if not filecmp.cmp(fuentes[0], fuentes[1], shallow=False):
        errors.append(f"{stem}.md difiere entre aidd/ y aisdd/ (son espejo)")
    htmls = [ROOT / f"plugins/{p}/methodology/{stem}.html" for p in ESPEJO]
    if not iguales(htmls[0], htmls[1]):
        errors.append(f"{stem}.html difiere entre aidd/ y aisdd/")
    esperado = regenera(fuentes[0], titulo)
    if not iguales(esperado, htmls[0]):
        errors.append(f"{stem}.html no coincide con lo que produce el renderer: "
                      f"regeneralo (ver README, seccion Mantenimiento)")

for plugin, stem, titulo in SUELTOS:
    md = ROOT / f"plugins/{plugin}/methodology/{stem}.md"
    html = ROOT / f"plugins/{plugin}/methodology/{stem}.html"
    if not md.is_file():
        continue
    if not iguales(regenera(md, titulo), html):
        errors.append(f"{stem}.html no coincide con su .md: regeneralo")

if errors:
    print("Documentacion generada desincronizada:", file=sys.stderr)
    for e in errors:
        print(f"  - {e}", file=sys.stderr)
    sys.exit(1)
print("HTML de metodologia al dia y copias sincronizadas.")
