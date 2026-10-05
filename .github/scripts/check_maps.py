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
4. La traduccion inglesa de `docs/maps/` tiene los mismos mapas que la espanola.
   Se comprueban las dos carpetas con las mismas reglas: los nombres de skill, de
   plugin y de fichero no se traducen, asi que valen igual en ambas.

Uso:  python3 .github/scripts/check_maps.py
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
MAPAS = RAIZ / "docs" / "mapas"
MAPS = RAIZ / "docs" / "maps"
# Cada mapa y su traduccion. El nombre del fichero ingles no es el espanol: anadir
# un mapa obliga a anadir aqui su pareja, que es justo lo que evita que la carpeta
# inglesa se quede a medias sin que nadie se entere.
PAREJAS = {
    "README.md": "README.md",
    "plugins.md": "plugins.md",
    "skills.md": "skills.md",
    "proceso.md": "process.md",
    "que-uso-cuando.md": "what-do-i-use-when.md",
    "ciclo-change.md": "change-lifecycle.md",
    "artefactos.md": "artifacts.md",
}
MERMAID = re.compile(r"```mermaid\n(.*?)```", re.S)
ENLACE = re.compile(r"\]\(([^)\s#]*)(?:#([^)\s]*))?\)")
CERCADO = re.compile(r"^```.*?^```", re.S | re.M)


def rel(ruta: Path) -> str:
    return ruta.relative_to(RAIZ).as_posix()


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
    for carpeta in (MAPAS, MAPS):
        if not carpeta.is_dir():
            errores.append(f"No existe {carpeta.relative_to(RAIZ)}.")
    if errores:
        return errores

    # 0. Cada mapa espanol tiene su traduccion, y al reves.
    esperados_es, esperados_en = set(PAREJAS), set(PAREJAS.values())
    for carpeta, esperados in ((MAPAS, esperados_es), (MAPS, esperados_en)):
        hay = {p.name for p in carpeta.glob("*.md")}
        for falta in sorted(esperados - hay):
            errores.append(f"{rel(carpeta)}/{falta}: no existe, y su pareja del otro idioma sí.")
        for sobra in sorted(hay - esperados):
            errores.append(f"{rel(carpeta)}/{sobra}: no tiene pareja declarada en PAREJAS "
                           f"de check_maps.py; añádela con su traducción.")

    for carpeta in (MAPAS, MAPS):
        indice = PAREJAS["skills.md"] if carpeta is MAPS else "skills.md"
        tabla_md = carpeta / indice
        if not tabla_md.is_file():
            continue

        # 1. Cada skill, en la tabla y en el mindmap.
        tabla = tabla_md.read_text(encoding="utf-8")
        mindmap = next((b for b in MERMAID.findall(tabla) if b.lstrip().startswith("mindmap")), "")
        if not mindmap:
            errores.append(f"{rel(carpeta)}/{indice} no tiene el mindmap de skills.")
        palabras = set(re.findall(r"[\w-]+", mindmap))
        for skill in skills():
            ruta = os.path.relpath(skill / "SKILL.md", carpeta).replace(os.sep, "/")
            if f"]({ruta})" not in tabla:
                errores.append(f"{skill.name}: sin fila en {rel(carpeta)}/{indice} "
                               f"(falta el enlace a {ruta}).")
            if mindmap and nombre_corto(skill) not in palabras:
                errores.append(f"{skill.name}: no sale en el mindmap de {rel(carpeta)}/{indice} "
                               f"como «{nombre_corto(skill)}».")

        # 2. La cuenta de skills de cada plugin.
        plugins = (carpeta / "plugins.md").read_text(encoding="utf-8")
        for plugin in sorted({s.parents[1] for s in skills()}):
            real = sum(1 for s in skills() if s.parents[1] == plugin)
            m = re.search(rf'"{re.escape(plugin.name)}<br/>[^"]*?\b(\d+) skills?\b', plugins)
            if not m:
                errores.append(f"{plugin.name}: {rel(carpeta)}/plugins.md no dice cuántos skills trae.")
            elif int(m.group(1)) != real:
                errores.append(f"{plugin.name}: {rel(carpeta)}/plugins.md dice {m.group(1)} skills "
                               f"y trae {real}.")

        # 3. Enlaces que resuelven y mapas con diagrama.
        for md in sorted(carpeta.glob("*.md")):
            texto = md.read_text(encoding="utf-8")
            if md.name != "README.md" and not MERMAID.search(texto):
                errores.append(f"{rel(carpeta)}/{md.name}: no tiene ningún bloque Mermaid.")
            for destino, ancla in ENLACE.findall(texto):
                if re.match(r"[a-z]+:", destino):
                    continue
                objetivo = md.parent / destino if destino else md
                if not objetivo.exists():
                    errores.append(f"{rel(carpeta)}/{md.name}: el enlace a {destino} "
                                   f"no lleva a ningún sitio.")
                elif ancla and objetivo.suffix == ".md" and ancla not in anclas(objetivo):
                    errores.append(f"{rel(carpeta)}/{md.name}: el enlace a {destino or md.name}#{ancla} "
                                   "apunta a una sección que no existe.")
    return errores


def main() -> int:
    errores = comprobar()
    if errores:
        print("Los mapas no cuadran con el repo:\n")
        for e in errores:
            print(f"  - {e}")
        print("\nQué tocar al añadir un skill: docs/mapas/README.md, «Mantenerlos al día»,\ny su traducción en docs/maps/.")
        return 1
    print(f"Mapas al día en los dos idiomas: {len(skills())} skills nombrados "
          f"y enlaces resueltos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
