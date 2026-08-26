#!/usr/bin/env python3
"""Valida los manifiestos del marketplace: JSON correcto y rutas que existen.

Un `marketplace.json` que apunte a un plugin inexistente rompe la instalacion
para todo el mundo y no falla hasta que alguien lo intenta. Aqui falla en la PR.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
errors: list[str] = []


def load(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{path.relative_to(ROOT)}: no se puede leer como JSON ({exc})")
        return None


mk_path = ROOT / ".claude-plugin" / "marketplace.json"
mk = load(mk_path)
declarados: set[str] = set()

if mk is not None:
    for campo in ("name", "owner", "plugins"):
        if campo not in mk:
            errors.append(f"marketplace.json: falta el campo '{campo}'")
    for entry in mk.get("plugins", []):
        nombre, source = entry.get("name"), entry.get("source")
        if not nombre or not source:
            errors.append(f"marketplace.json: entrada incompleta {entry}")
            continue
        declarados.add(nombre)
        destino = (ROOT / source).resolve()
        if not destino.is_dir():
            errors.append(f"marketplace.json: '{nombre}' apunta a {source}, que no existe")
            continue
        pj = destino / ".claude-plugin" / "plugin.json"
        if not pj.is_file():
            errors.append(f"{nombre}: falta {pj.relative_to(ROOT)}")
            continue
        d = load(pj)
        if d is None:
            continue
        if d.get("name") != nombre:
            errors.append(f"{nombre}: plugin.json declara name='{d.get('name')}', "
                          f"pero marketplace.json lo llama '{nombre}'")
        if not d.get("version"):
            errors.append(f"{nombre}: plugin.json sin 'version'")

# Plugins en disco que nadie declara: no se instalan y nadie se entera.
en_disco = {p.parent.parent.name for p in ROOT.glob("plugins/*/.claude-plugin/plugin.json")}
for huerfano in sorted(en_disco - declarados):
    errors.append(f"plugins/{huerfano}/ existe pero no esta en marketplace.json")

version = (ROOT / "VERSION")
if not version.is_file():
    errors.append("falta el fichero VERSION en la raiz")
elif not version.read_text(encoding="utf-8").strip():
    errors.append("VERSION esta vacio")

if errors:
    print("Manifiestos con problemas:", file=sys.stderr)
    for e in errors:
        print(f"  - {e}", file=sys.stderr)
    sys.exit(1)
print(f"Manifiestos correctos: {len(declarados)} plugins declarados y presentes.")
