#!/usr/bin/env python3
"""Genera las notas del release comparando contra la etiqueta anterior.

Lo unico que le importa a quien consume el marketplace es si tiene que
reinstalar algo y que. Eso no se deduce de la lista de commits, asi que las
notas empiezan por la tabla de plugins y skills que han cambiado de version.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def git(*args: str) -> str:
    r = subprocess.run(["git", *args], capture_output=True, text=True, cwd=ROOT)
    return r.stdout.strip() if r.returncode == 0 else ""


def version_en(ref: str, path: str) -> str | None:
    """Version de un plugin.json (o SKILL.md) en una referencia dada."""
    raw = git("show", f"{ref}:{path}")
    if not raw:
        return None
    if path.endswith(".json"):
        try:
            return json.loads(raw).get("version")
        except json.JSONDecodeError:
            return None
    m = re.search(r'^\s*version:\s*"([^"]+)"', raw.split("---", 2)[1], re.M) if "---" in raw else None
    return m.group(1) if m else None


version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
tags = [t for t in git("tag", "--list", "v*", "--sort=-v:refname").splitlines() if t]
anterior = tags[0] if tags else None

out: list[str] = []
if anterior is None:
    out.append(f"Primera release del marketplace (`{version}`).\n")
else:
    out.append(f"Cambios desde `{anterior}`.\n")

    filas = []
    for pj in sorted(ROOT.glob("plugins/*/.claude-plugin/plugin.json")):
        rel = str(pj.relative_to(ROOT))
        antes, ahora = version_en(anterior, rel), json.loads(pj.read_text(encoding="utf-8")).get("version")
        if antes != ahora:
            filas.append((pj.parts[-3], antes or "nuevo", ahora))
    if filas:
        out.append("## Plugins que cambian de versión\n")
        out.append("| Plugin | Antes | Ahora |")
        out.append("|---|---|---|")
        out += [f"| `{n}` | {a} | **{b}** |" for n, a, b in filas]
        out.append("")

    filas_s = []
    for sk in sorted(ROOT.glob("plugins/*/skills/*/SKILL.md")):
        rel = str(sk.relative_to(ROOT))
        antes = version_en(anterior, rel)
        m = re.search(r'^\s*version:\s*"([^"]+)"', sk.read_text(encoding="utf-8").split("---", 2)[1], re.M)
        ahora = m.group(1) if m else None
        if ahora and antes != ahora:
            filas_s.append((sk.parent.name, antes or "nuevo", ahora))
    if filas_s:
        out.append("## Skills que cambian de versión\n")
        out.append("| Skill | Antes | Ahora |")
        out.append("|---|---|---|")
        out += [f"| `{n}` | {a} | **{b}** |" for n, a, b in filas_s]
        out.append("")

    if not filas and not filas_s:
        out.append("_Sin cambios de versión en plugins ni skills; cambios de documentación o infraestructura._\n")

    commits = git("log", "--no-merges", "--pretty=format:- %s", f"{anterior}..HEAD")
    if commits:
        out.append("## Commits\n")
        out.append(commits)

print("\n".join(out))
