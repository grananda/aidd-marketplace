#!/usr/bin/env python3
"""Comprueba el frontmatter de cada SKILL.md.

Sin frontmatter valido el skill no se carga, y sin `description` el modelo no
sabe cuando invocarlo: falla en silencio, que es la peor forma de fallar.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
errors: list[str] = []
ok = 0

for skill in sorted(ROOT.glob("plugins/*/skills/*/SKILL.md")):
    rel = skill.relative_to(ROOT)
    texto = skill.read_text(encoding="utf-8")
    if not texto.startswith("---\n"):
        errors.append(f"{rel}: no empieza con frontmatter")
        continue
    partes = texto.split("---\n", 2)
    if len(partes) < 3:
        errors.append(f"{rel}: frontmatter sin cierre")
        continue
    fm = partes[1]

    nombre = re.search(r"^name:\s*(\S+)\s*$", fm, re.M)
    if not nombre:
        errors.append(f"{rel}: falta 'name'")
    elif nombre.group(1) != skill.parent.name:
        errors.append(f"{rel}: name='{nombre.group(1)}' no coincide con el "
                      f"directorio '{skill.parent.name}'")

    desc = re.search(r"^description:\s*(.+)$", fm, re.M)
    if not desc:
        errors.append(f"{rel}: falta 'description' (el modelo no sabra cuando usarlo)")
    elif len(desc.group(1).strip()) < 40:
        errors.append(f"{rel}: 'description' demasiado corta para decidir la invocacion")

    if not re.search(r'^\s*version:\s*"[^"]+"\s*$', fm, re.M):
        errors.append(f"{rel}: falta metadata.version entrecomillada")

    if errors and errors[-1].startswith(str(rel)):
        continue
    ok += 1

if errors:
    print("Skills con problemas de frontmatter:", file=sys.stderr)
    for e in errors:
        print(f"  - {e}", file=sys.stderr)
    sys.exit(1)
print(f"Frontmatter correcto en {ok} skills.")
