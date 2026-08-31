#!/usr/bin/env python3
"""Cada plugin trae lo que sus skills invocan, y lo compartido no ha divergido.

Claude Code instala cada plugin por separado y no resuelve dependencias entre
ellos: un skill que ejecuta `${CLAUDE_PLUGIN_ROOT}/scripts/stamp_doc.py` falla en
tiempo de uso si ese script vive en otro plugin. Es justo lo que pasa al mover
skills de sitio con `git mv`, y no lo detecta ninguna otra comprobacion.

Dos invariantes:

1. **Rutas resolubles** — toda referencia `${CLAUDE_PLUGIN_ROOT}/...` de un skill
   o de un hook apunta a un fichero que ese mismo plugin lleva dentro.
   Se excluye `methodology/`: son documentos en prosa, copiados en varios
   plugins, donde la variable describe el proceso y no la ejecuta nadie.

2. **Copias sincronizadas** — los ficheros que viajan replicados en varios
   plugins (el hook de actividad, `stamp_doc.py`) son identicos entre si.
   Se replican porque cada plugin debe ser autosuficiente; nada garantiza que
   se editen los N a la vez, y una copia rezagada no falla, solo miente.

3. **Constantes replicadas** — la escala de tallas AIDD vive duplicada en cuatro
   scripts de tres plugins distintos, por la misma razon: no se pueden importar
   entre si. De ella salen el calendario de `aisdd roadmap`, el panel de KPIs de
   `booster-docs`, el ahorro que calcula `aiba metrics` y el avance real que mide
   `aiba status-report`. Si una copia se queda
   atras, los tres siguen dando numeros y ninguno coincide, sin que nada avise.
"""
from __future__ import annotations

import ast

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# Las dos formas de la variable. La de PowerShell (`$env:CLAUDE_PLUGIN_ROOT\...`)
# no la cubria esta comprobacion, y por ahi sobrevivio una ruta del empaquetado
# anterior: en booster-docs la invocacion bash ya estaba migrada y su hermana en
# PowerShell seguia apuntando a `.agents\skills\...`, que en un plugin no existe.
REF = re.compile(r"(?:\$\{CLAUDE_PLUGIN_ROOT\}|\$env:CLAUDE_PLUGIN_ROOT)"
                 r"[/\\]([A-Za-z0-9_./\\-]+)")
LEIBLES = {".md", ".py", ".sh", ".json", ".yaml", ".yml"}

# Ficheros replicados a proposito. Cada entrada: ruta relativa al plugin y los
# plugins que deben llevarla identica.
COMPARTIDOS = [
    ("hooks/aidd-activity-hook.sh", ["aidd", "aisdd", "aiad", "aiba", "boosters"]),
    ("hooks/hooks.json", ["aidd", "aisdd", "aiba", "boosters"]),  # aiad suma su journal
    ("scripts/stamp_doc.py", ["aidd", "aiba"]),
]

# Nombre de la constante -> ficheros que deben declararla igual. Se comparan por
# valor, no por texto: dan igual el formato y el orden de las claves.
CONSTANTES = [
    # Los tres pines de Mermaid van juntos: version, hash e integridad del bundle.
    # Si divergen, los dos renderizadores se pelean por el mismo fichero cacheado y
    # cada uno rechaza por hash el que dejo el otro -- descargando en cada ejecucion
    # sin decir por que. El README ya advertia de mantenerlos a la vez; nada lo comprobaba.
    ("MERMAID_VERSION", [
        "plugins/boosters/skills/booster-uml/scripts/render_uml_html.py",
        "plugins/boosters/skills/booster-docs/scripts/render_docs_html.py",
    ]),
    ("MERMAID_SHA256", [
        "plugins/boosters/skills/booster-uml/scripts/render_uml_html.py",
        "plugins/boosters/skills/booster-docs/scripts/render_docs_html.py",
    ]),
    ("MERMAID_SIZE", [
        "plugins/boosters/skills/booster-uml/scripts/render_uml_html.py",
        "plugins/boosters/skills/booster-docs/scripts/render_docs_html.py",
    ]),
    ("EFFORT_DAYS", [
        "plugins/aisdd/skills/aisdd-specs/scripts/optimize_phasing.py",
        "plugins/boosters/skills/booster-docs/scripts/render_docs_html.py",
        "plugins/aiba/skills/aiba-metrics/scripts/compute_kpis.py",
        "plugins/aiba/skills/aiba-status-report/scripts/compute_status.py",
    ]),
]


def literal_de(ruta: Path, nombre: str):
    """Valor de una asignacion de nivel de modulo, sin ejecutar el fichero."""
    arbol = ast.parse(ruta.read_text(encoding="utf-8"))
    for nodo in arbol.body:
        if isinstance(nodo, ast.Assign) and any(
                isinstance(d, ast.Name) and d.id == nombre for d in nodo.targets):
            try:
                return ast.literal_eval(nodo.value)
            except ValueError:
                return None
    return None


errors: list[str] = []
comprobadas = 0

for plugin_dir in sorted(ROOT.glob("plugins/*/")):
    plugin = plugin_dir.name
    for f in sorted(plugin_dir.rglob("*")):
        if not f.is_file() or f.suffix not in LEIBLES:
            continue
        rel = f.relative_to(plugin_dir)
        if rel.parts[0] == "methodology" or "__pycache__" in rel.parts:
            continue
        texto = f.read_text(encoding="utf-8", errors="replace")
        for m in REF.finditer(texto):
            comprobadas += 1
            # PowerShell escribe la ruta con barras invertidas; el fichero es el mismo.
            if not (plugin_dir / m.group(1).replace("\\", "/")).exists():
                errors.append(
                    f"{f.relative_to(ROOT)}: referencia ${{CLAUDE_PLUGIN_ROOT}}/{m.group(1)}, "
                    f"que no existe en plugins/{plugin}/ (los plugins se instalan sueltos: "
                    f"cada uno debe traer lo que ejecuta)"
                )

for ruta, plugins in COMPARTIDOS:
    huellas: dict[str, list[str]] = {}
    for plugin in plugins:
        f = ROOT / "plugins" / plugin / ruta
        if not f.is_file():
            errors.append(f"plugins/{plugin}/{ruta}: falta (deberia viajar en {', '.join(plugins)})")
            continue
        huellas.setdefault(hashlib.sha256(f.read_bytes()).hexdigest(), []).append(plugin)
    if len(huellas) > 1:
        grupos = " vs ".join("+".join(v) for v in huellas.values())
        errors.append(f"{ruta}: las copias han divergido ({grupos})")

for nombre, rutas in CONSTANTES:
    valores: dict[str, list[str]] = {}
    for rel in rutas:
        f = ROOT / rel
        if not f.is_file():
            errors.append(f"{rel}: falta, pero debe declarar {nombre}")
            continue
        v = literal_de(f, nombre)
        if v is None:
            errors.append(f"{rel}: no declara {nombre} como literal de modulo")
            continue
        valores.setdefault(repr(sorted(v.items()) if isinstance(v, dict) else v),
                           []).append(rel)
    if len(valores) > 1:
        detalle = " vs ".join(f"{v[0]} {k}" for k, v in valores.items())
        errors.append(f"{nombre}: las copias no coinciden -> {detalle}")

if errors:
    print("Plugins con dependencias rotas o copias desincronizadas:", file=sys.stderr)
    for e in errors:
        print(f"  - {e}", file=sys.stderr)
    sys.exit(1)
print(f"Plugins autosuficientes: {comprobadas} referencias resueltas y "
      f"{len(COMPARTIDOS)} ficheros compartidos sincronizados, "
      f"{len(CONSTANTES)} constantes replicadas coherentes.")
