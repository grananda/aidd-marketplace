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
SUELTOS = [("aiad", "native-ai-aiad", "Native AI · AIAD — AI-Augmented Development")]

errors: list[str] = []


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
    if not filecmp.cmp(htmls[0], htmls[1], shallow=False):
        errors.append(f"{stem}.html difiere entre aidd/ y aisdd/")
    esperado = regenera(fuentes[0], titulo)
    if not filecmp.cmp(esperado, htmls[0], shallow=False):
        errors.append(f"{stem}.html no coincide con lo que produce el renderer: "
                      f"regeneralo (ver README, seccion Mantenimiento)")

for plugin, stem, titulo in SUELTOS:
    md = ROOT / f"plugins/{plugin}/methodology/{stem}.md"
    html = ROOT / f"plugins/{plugin}/methodology/{stem}.html"
    if not md.is_file():
        continue
    if not filecmp.cmp(regenera(md, titulo), html, shallow=False):
        errors.append(f"{stem}.html no coincide con su .md: regeneralo")

if errors:
    print("Documentacion generada desincronizada:", file=sys.stderr)
    for e in errors:
        print(f"  - {e}", file=sys.stderr)
    sys.exit(1)
print("HTML de metodologia al dia y copias sincronizadas.")
