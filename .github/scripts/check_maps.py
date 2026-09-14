#!/usr/bin/env python3
"""Los mapas de `docs/mapas/` no se quedan atras.

Los mapas se escriben a mano, y en este repo entran skills a menudo: un mapa que
no nombra un skill le dice a quien llega que esa herramienta no existe, y una
cuenta de skills desfasada hace dudar de todo lo demas. Se comprueba lo que se
puede comprobar sin opinar sobre el dibujo:

1. Cada skill del repo tiene fila en `docs/mapas/skills.md`, con enlace a su
   `SKILL.md`, y sale en el mindmap de ese mismo fichero por su nombre corto
   (`requirements` para `aidd-requirements`).
2. Cada plugin dice en `docs/mapas/plugins.md` cuantos skills trae, en el nodo
   que lleva su nombre, y la cifra es la real.
3. Todo enlace relativo de los mapas lleva a algo que existe --y, si lleva
   ancla, a una seccion que existe, con el mismo slug que genera GitHub--, y cada
   mapa --el indice aparte-- tiene al menos un bloque Mermaid.

Uso:  python3 .github/scripts/check_maps.py
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
MAPAS = RAIZ / "docs" / "mapas"
MERMAID = re.compile(r"```mermaid\n(.*?)```", re.S)
ENLACE = re.compile(r"\]\(([^)\s#]*)(?:#([^)\s]*))?\)")
CERCADO = re.compile(r"^```.*?^```", re.S | re.M)


def skills() -> list[Path]:
    return sorted(p.parent for p in RAIZ.glob("plugins/*/skills/*/SKILL.md"))


def nombre_corto(skill: Path) -> str:
    return skill.name.split("-", 1)[1]


def anclas(md: Path) -> set[str]:
    """Las anclas que GitHub genera para los titulos de un markdown."""
    texto = CERCADO.sub("", md.read_text(encoding="utf-8"))
    vistas: dict[str, int] = {}
    salida: set[str] = set()
    for titulo in re.findall(r"^#{1,6}\s+(.+?)\s*#*$", texto, re.M):
        base = re.sub(r"[^\w\- ]", "", titulo.replace("`", "").lower()).replace(" ", "-")
        n = vistas.get(base, 0)
        vistas[base] = n + 1
        salida.add(base if n == 0 else f"{base}-{n}")
    return salida


def comprobar() -> list[str]:
    errores: list[str] = []
    if not MAPAS.is_dir():
        return [f"No existe {MAPAS.relative_to(RAIZ)}."]

    # 1. Cada skill, en la tabla y en el mindmap.
    tabla = (MAPAS / "skills.md").read_text(encoding="utf-8")
    mindmap = next((b for b in MERMAID.findall(tabla) if b.lstrip().startswith("mindmap")), "")
    if not mindmap:
        errores.append("docs/mapas/skills.md no tiene el mindmap de skills.")
    palabras = set(re.findall(r"[\w-]+", mindmap))
    for skill in skills():
        ruta = os.path.relpath(skill / "SKILL.md", MAPAS).replace(os.sep, "/")
        if f"]({ruta})" not in tabla:
            errores.append(f"{skill.name}: sin fila en docs/mapas/skills.md (falta el enlace a {ruta}).")
        if mindmap and nombre_corto(skill) not in palabras:
            errores.append(f"{skill.name}: no sale en el mindmap de docs/mapas/skills.md "
                           f"como «{nombre_corto(skill)}».")

    # 2. La cuenta de skills de cada plugin.
    plugins = (MAPAS / "plugins.md").read_text(encoding="utf-8")
    for plugin in sorted({s.parents[1] for s in skills()}):
        real = sum(1 for s in skills() if s.parents[1] == plugin)
        m = re.search(rf'"{re.escape(plugin.name)}<br/>[^"]*?\b(\d+) skills?\b', plugins)
        if not m:
            errores.append(f"{plugin.name}: docs/mapas/plugins.md no dice cuántos skills trae.")
        elif int(m.group(1)) != real:
            errores.append(f"{plugin.name}: docs/mapas/plugins.md dice {m.group(1)} skills y trae {real}.")

    # 3. Enlaces que resuelven y mapas con diagrama.
    for md in sorted(MAPAS.glob("*.md")):
        texto = md.read_text(encoding="utf-8")
        if md.name != "README.md" and not MERMAID.search(texto):
            errores.append(f"docs/mapas/{md.name}: no tiene ningún bloque Mermaid.")
        for destino, ancla in ENLACE.findall(texto):
            if re.match(r"[a-z]+:", destino):
                continue
            objetivo = md.parent / destino if destino else md
            if not objetivo.exists():
                errores.append(f"docs/mapas/{md.name}: el enlace a {destino} no lleva a ningún sitio.")
            elif ancla and objetivo.suffix == ".md" and ancla not in anclas(objetivo):
                errores.append(f"docs/mapas/{md.name}: el enlace a {destino or md.name}#{ancla} "
                               "apunta a una sección que no existe.")
    return errores


def main() -> int:
    errores = comprobar()
    if errores:
        print("Los mapas de docs/mapas/ no cuadran con el repo:\n")
        for e in errores:
            print(f"  - {e}")
        print("\nQué tocar al añadir un skill: docs/mapas/README.md, «Mantenerlos al día».")
        return 1
    print(f"Mapas al día: {len(skills())} skills nombrados y enlaces resueltos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
