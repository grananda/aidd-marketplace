#!/usr/bin/env python3
"""Genera las notas del release comparando contra la etiqueta anterior.

Tres criterios, en este orden:

**Claro** — primero lo que rompe, luego lo que hay de nuevo, luego que reinstalar.
El volcado de `git log` va al final y plegado: describe defectos internos que a
quien consume el marketplace no le dicen nada.

**Justo** — todo sale de datos que ya existen y nadie mantiene aparte: las
versiones semver de los manifiestos, el estado de las entradas de ROADMAP.md y
la marca `!` de conventional commits. Nada se redacta a mano, asi que nada se
queda sin contar cuando alguien tiene prisa.

**Automatico** — lo lanza release.yml en cada merge a main que traiga una
VERSION sin etiquetar. No hay fichero que recordar editar.
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


def es_major(antes: str | None, ahora: str | None) -> bool:
    """Un salto de mayor es la unica declaracion de incompatibilidad que no
    depende de que alguien se acuerde de escribirla."""
    try:
        return int(str(ahora).split(".")[0]) > int(str(antes).split(".")[0])
    except (ValueError, AttributeError):
        return False


FILA_ROADMAP = re.compile(r"^\|\s*(F-\d+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|")


def roadmap_estados(texto: str) -> dict[str, tuple[str, str]]:
    """{id: (titulo, estado)} de la tabla de ROADMAP.md."""
    fuera = {}
    for linea in texto.splitlines():
        m = FILA_ROADMAP.match(linea)
        if m:
            fuera[m.group(1)] = (m.group(2), m.group(4))
    return fuera


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

    majors: list[str] = []
    # 1. Lo que rompe. Dos fuentes independientes: el salto de mayor, que es
    # mecanico, y la marca `!` de conventional commits, que es deliberada.
    rotos = [l[2:] for l in git("log", "--no-merges", "--pretty=format:- %s",
                                f"{anterior}..HEAD").splitlines()
             if re.match(r"- \w+(\([^)]*\))?!:", l)]

    filas = []
    for pj in sorted(ROOT.glob("plugins/*/.claude-plugin/plugin.json")):
        rel = str(pj.relative_to(ROOT))
        antes, ahora = version_en(anterior, rel), json.loads(pj.read_text(encoding="utf-8")).get("version")
        if antes != ahora:
            filas.append((pj.parts[-3], antes or "nuevo", ahora))
            if es_major(antes, ahora):
                majors.append(f"`{pj.parts[-3]}` ({antes} → {ahora})")
    # Hueco reservado: la seccion va la primera, pero no se puede componer hasta
    # haber recorrido plugins Y skills.
    hueco = len(out)

    nuevas = []
    antes_rm = roadmap_estados(git("show", f"{anterior}:ROADMAP.md"))
    for fid, (titulo, estado) in roadmap_estados(
            (ROOT / "ROADMAP.md").read_text(encoding="utf-8")).items():
        if "implementada" in estado and "implementada" not in antes_rm.get(fid, ("", ""))[1]:
            nuevas.append(f"- **{fid}** · {titulo}")
    if nuevas:
        out.append("## Novedades\n")
        out += nuevas
        out.append("")

    if filas:
        out.append("## Plugins que cambian de versión\n")
        out.append("| Plugin | Antes | Ahora |")
        out.append("|---|---|---|")
        out += [f"| `{n}` | {a} | **{b}** |" for n, a, b in filas]
        out.append("")

    filas_s = []
    actuales: set[str] = set()
    for sk in sorted(ROOT.glob("plugins/*/skills/*/SKILL.md")):
        rel = str(sk.relative_to(ROOT))
        actuales.add(rel)
        antes = version_en(anterior, rel)
        m = re.search(r'^\s*version:\s*"([^"]+)"', sk.read_text(encoding="utf-8").split("---", 2)[1], re.M)
        ahora = m.group(1) if m else None
        if ahora and antes != ahora:
            filas_s.append((sk.parent.name, antes or "nuevo", ahora))
            if es_major(antes, ahora):
                majors.append(f"`{sk.parent.name}` ({antes} → {ahora})")
    if filas_s:
        out.append("## Skills que cambian de versión\n")
        out.append("| Skill | Antes | Ahora |")
        out.append("|---|---|---|")
        out += [f"| `{n}` | {a} | **{b}** |" for n, a, b in filas_s]
        out.append("")

    # Un skill que desaparece o cambia de plugin es lo que mas le rompe a quien
    # ya lo tenia en uso, y el recorrido de arriba solo ve lo que existe HOY:
    # sin esto, la unica ruptura de verdad seria la que no aparece en las notas.
    previos = [l for l in git("ls-tree", "-r", "--name-only", anterior).splitlines()
               if re.fullmatch(r"plugins/[^/]+/skills/[^/]+/SKILL\.md", l)]
    idas = sorted(set(previos) - actuales)
    if idas:
        # `aidd-metrics` -> `metrics`, para reconocer el mismo skill bajo otro prefijo.
        def sufijo(ruta: str) -> str:
            return Path(ruta).parent.name.split("-", 1)[-1]

        destinos = {sufijo(r): r for r in sorted(actuales)}
        out.append("## Skills que ya no están donde estaban\n")
        out.append("| Skill | Estaba en | Ahora |")
        out.append("|---|---|---|")
        for r in idas:
            llegada = destinos.get(sufijo(r))
            ahora = (f"`{llegada.split('/')[1]}` como `{Path(llegada).parent.name}`"
                     if llegada else "eliminado")
            out.append(f"| `{Path(r).parent.name}` | `{r.split('/')[1]}` | {ahora} |")
        out.append("")
        out.append("> Si tenías alguno instalado, reinstala el plugin de destino: "
                   "sus comandos ya no responden con el prefijo antiguo.\n")

    if majors or rotos:
        seccion = ["## Atención al actualizar\n"]
        if majors:
            seccion.append("Versión mayor — revisa antes de actualizar: "
                           + ", ".join(majors) + ".\n")
        seccion += [f"- {r}" for r in rotos]
        seccion.append("")
        out[hueco:hueco] = seccion

    if not filas and not filas_s and not idas:
        out.append("_Sin cambios de versión en plugins ni skills; cambios de documentación o infraestructura._\n")

    lineas = [l for l in git("log", "--no-merges", "--pretty=format:- %s",
                             f"{anterior}..HEAD").splitlines() if l.strip()]
    if lineas:
        grupos: dict[str, list[str]] = {"Nuevo": [], "Corregido": [], "Resto": []}
        for l in lineas:
            tipo = re.match(r"- (\w+)", l)
            clave = ("Nuevo" if tipo and tipo.group(1) == "feat"
                     else "Corregido" if tipo and tipo.group(1) == "fix" else "Resto")
            grupos[clave].append(l)
        out.append(f"<details>\n<summary>{len(lineas)} commits</summary>\n")
        for clave, items in grupos.items():
            if items:
                out.append(f"**{clave}**\n")
                out += items
                out.append("")
        out.append("</details>")

print("\n".join(out))
