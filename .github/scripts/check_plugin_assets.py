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
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REF = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([A-Za-z0-9_./-]+)")
LEIBLES = {".md", ".py", ".sh", ".json", ".yaml", ".yml"}

# Ficheros replicados a proposito. Cada entrada: ruta relativa al plugin y los
# plugins que deben llevarla identica.
COMPARTIDOS = [
    ("hooks/aidd-activity-hook.sh", ["aidd", "aisdd", "aiad", "aiba", "boosters"]),
    ("hooks/hooks.json", ["aidd", "aisdd", "aiba", "boosters"]),  # aiad suma su journal
    ("scripts/stamp_doc.py", ["aidd", "aiba"]),
]

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
            if not (plugin_dir / m.group(1)).exists():
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

if errors:
    print("Plugins con dependencias rotas o copias desincronizadas:", file=sys.stderr)
    for e in errors:
        print(f"  - {e}", file=sys.stderr)
    sys.exit(1)
print(f"Plugins autosuficientes: {comprobadas} referencias resueltas y "
      f"{len(COMPARTIDOS)} ficheros compartidos sincronizados.")
