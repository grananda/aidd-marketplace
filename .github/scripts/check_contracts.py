#!/usr/bin/env python3
"""Lo que un skill documenta coincide con lo que el script hace.

Un skill y el script que invoca son productor y consumidor de un formato, y el
formato vive en dos sitios a la vez: la prosa del skill y el codigo del script.
Nada los ata. Cuando divergen no falla la CI, falla el usuario, en su proyecto,
a mitad de un comando -- que es donde menos se puede diagnosticar.

Dos contratos, los dos comprobables sin ejecutar nada:

1. **La invocacion documentada y el argparse del script.** Cada flag que un
   `SKILL.md` escribe existe en el script, y cada flag que el script exige
   aparece en alguna invocacion documentada. Los dos sentidos importan: una
   flag inventada aborta el comando, y una flag nueva `required=True` deja
   obsoletas todas las invocaciones ya escritas sin tocarlas.

2. **El tipo de documento y su vista HTML.** `booster-docs` deduce el tipo por
   el nombre del fichero contra `DOC_TYPES`. Un documento sin entrada no falla:
   sale con la etiqueta y el dashboard generico, que es una vista peor sin que
   nadie lo note. Paso justo eso con `kpis-ia`.
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Invocacion documentada: la ruta del script y todo lo que le sigue, incluidas
# las lineas continuadas con `\` -- los ejemplos largos se parten en varias, y ahi
# es justo donde van las flags. El grupo de continuacion va **antes** del resto de
# la linea: al reves, `[^\n]*` se come la barra final, la continuacion casa cero
# veces, el patron ya encaja y nada le obliga a retroceder. Se pierden todas las
# flags del ejemplo y el script parece invocado sin sus obligatorias.
# Las dos formas de la variable, como en check_plugin_assets.py: la de PowerShell
# escribe la ruta con barras invertidas y por ahi ya se colo una ruta obsoleta.
INVOCACION = re.compile(
    r"(?:\$\{CLAUDE_PLUGIN_ROOT\}|\$env:CLAUDE_PLUGIN_ROOT)"
    r"[/\\]([A-Za-z0-9_./\\-]+\.py)\"?((?:[^\n]*\\\n)*[^\n]*)")
FLAG = re.compile(r"(?<![\w-])(--[a-z0-9][a-z0-9-]*)")

RENDER = ROOT / "plugins/boosters/skills/booster-docs/scripts/render_docs_html.py"
HTML_DECLARADO = re.compile(r"docs/html/([A-Za-z0-9._-]+)\.html")

# Vistas HTML que no las genera booster-docs, asi que no les toca DOC_TYPES.
SIN_DOC_TYPE = {
    "faseado-comparativa": "la genera optimize_phasing.py, no booster-docs",
}


def argparse_de(script: Path) -> tuple[set[str], set[str]] | None:
    """Flags que el script acepta y las que exige, sin ejecutarlo."""
    try:
        arbol = ast.parse(script.read_text(encoding="utf-8"))
    except SyntaxError:
        return None
    acepta: set[str] = set()
    exige: set[str] = set()
    for n in ast.walk(arbol):
        if not (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr == "add_argument"):
            continue
        nombres = [a.value for a in n.args
                   if isinstance(a, ast.Constant) and isinstance(a.value, str)
                   and a.value.startswith("-")]
        if not nombres:
            continue
        acepta.update(nombres)
        for kw in n.keywords:
            if (kw.arg == "required" and isinstance(kw.value, ast.Constant)
                    and kw.value.value is True):
                exige.add(nombres[-1])  # la forma larga
    return acepta, exige


def literal_de(ruta: Path, nombre: str):
    for nodo in ast.parse(ruta.read_text(encoding="utf-8")).body:
        if isinstance(nodo, ast.Assign) and any(
                isinstance(d, ast.Name) and d.id == nombre for d in nodo.targets):
            return ast.literal_eval(nodo.value)
    return None


errores: list[str] = []
flags_vistas = 0
documentadas: dict[Path, set[str]] = {}

for plugin_dir in sorted(ROOT.glob("plugins/*/")):
    for md in sorted(plugin_dir.rglob("*.md")):
        if "methodology" in md.parts:
            continue
        for m in INVOCACION.finditer(md.read_text(encoding="utf-8", errors="replace")):
            script = plugin_dir / m.group(1).replace("\\", "/")
            if not script.is_file():
                continue  # ruta rota: la reporta check_plugin_assets.py
            parsed = argparse_de(script)
            if parsed is None:
                continue
            acepta, _ = parsed
            if not acepta:
                continue  # el script no usa argparse; no hay contrato que comprobar
            usadas = set(FLAG.findall(m.group(2)))
            documentadas.setdefault(script, set()).update(usadas)
            for f in sorted(usadas):
                flags_vistas += 1
                if f not in acepta:
                    errores.append(
                        f"{md.relative_to(ROOT)}: documenta `{f}` para {script.name}, "
                        f"que no la acepta (acepta: {', '.join(sorted(acepta))})")
            # Se comprueba **por invocacion**, no sobre la union de todas: que entre
            # dos ejemplos esten todas las obligatorias no salva a ninguno de los dos.
            for f in sorted(parsed[1] - usadas):
                errores.append(
                    f"{md.relative_to(ROOT)}: invoca {script.name} sin `{f}`, que el "
                    f"script exige (required=True): ese comando fallaria al ejecutarse")

doc_types = literal_de(RENDER, "DOC_TYPES") if RENDER.is_file() else None
if doc_types is None:
    errores.append(f"{RENDER.relative_to(ROOT)}: no declara DOC_TYPES como literal de modulo")
else:
    claves = sorted(doc_types, key=len, reverse=True)  # el orden de detect_doc_type
    vistos: set[str] = set()
    for md in sorted(ROOT.glob("plugins/*/skills/*/**/*.md")):
        for m in HTML_DECLARADO.finditer(md.read_text(encoding="utf-8", errors="replace")):
            stem = m.group(1).lower()
            if stem in vistos or stem in SIN_DOC_TYPE:
                continue
            vistos.add(stem)
            if not any(k in stem for k in claves):
                errores.append(
                    f"{md.relative_to(ROOT)}: genera docs/html/{m.group(1)}.html, y "
                    f"DOC_TYPES no tiene entrada que case con '{stem}': saldria con la "
                    f"etiqueta y el dashboard genericos")

if errores:
    print("Contratos rotos entre lo documentado y lo implementado:", file=sys.stderr)
    for e in errores:
        print(f"  - {e}", file=sys.stderr)
    sys.exit(1)
print(f"Contratos coherentes: {flags_vistas} flags documentadas existen en su script, "
      f"{len(documentadas)} scripts con sus flags obligatorias en cada invocacion, "
      f"{len(doc_types or {})} tipos de documento con vista HTML propia.")
