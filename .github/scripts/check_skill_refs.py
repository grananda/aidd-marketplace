#!/usr/bin/env python3
"""Las rutas que un skill nombra en prosa resuelven donde el skill las busca.

Los skills se cargan en diferido: `SKILL.md` es un indice y las reglas viven en
`references/*.md`, que el agente lee **solo cuando el indice se lo dice**. Una
ruta que no resuelve no da error: el agente no encuentra el fichero, sigue sin
el, y la regla que contenia simplemente no se aplica. Es el peor fallo posible
en este repo, porque se parece exactamente a que todo funciona.

`check_plugin_assets.py` cubre las rutas ejecutables (`${CLAUDE_PLUGIN_ROOT}/...`).
Esta cubre las otras tres formas, que son las que se escriben a mano:

1. **Rutas internas** — `references/x.md`, `scripts/x.py` entre comillas simples
   resuelven **dentro del propio skill**. La convencion del repo es:

   | Destino | Forma |
   |---|---|
   | El mismo skill | `references/x.md` |
   | Otro skill, mismo plugin | `${CLAUDE_PLUGIN_ROOT}/skills/<skill>/references/x.md` |
   | Otro plugin | sin ruta: nombra el skill y nada mas |

   La tercera fila no es estilo. Los plugins se instalan sueltos, asi que una
   ruta a otro plugin apunta a un fichero que el usuario puede no tener.

2. **Rutas del empaquetado anterior** — `.agents/skills/`, `%USERPROFILE%`,
   `~/.claude/skills/`. En una instalacion por plugin no existen ninguna.

3. **Rutas del repo** — `plugins/<x>/...` describe este repositorio, no lo que
   el usuario tiene instalado.

Y el reverso: un `references/*.md` que ningun fichero del skill nombra no lo
lee nadie. No rompe nada, y ese es el problema: parece documentacion vigente.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Ruta interna entre comillas simples: `references/x.md`. La comilla de apertura
# la exige el patron, asi que la forma cross-skill (`${CLAUDE_PLUGIN_ROOT}/...`)
# no entra aqui -- la valida check_plugin_assets.py.
INTERNA = re.compile(r"`((?:references|scripts|assets|templates)/[A-Za-z0-9_./-]+\.[A-Za-z0-9]+)`")

# Un comando dentro de un bloque de codigo se ejecuta desde el proyecto del
# usuario, no desde el directorio del skill: ahi una ruta relativa no resuelve
# nunca. En prosa si vale (es un puntero, no una orden), y por eso la regla
# distingue los dos sitios en vez de prohibir la forma relativa a secas.
BLOQUE = re.compile(r"```(?:bash|sh|shell|powershell|ps1)\n(.*?)```", re.S)
RELATIVA_EN_COMANDO = re.compile(
    r"(?<![\w/${:\\-])(?:\./)?((?:scripts|references|assets|templates)/[A-Za-z0-9_./-]+)")

# Rutas que no existen en una instalacion por plugin.
LEGACY = [
    (re.compile(r"\.agents[/\\]skills"), ".agents/skills/",
     ".agents/skills/ es del empaquetado anterior al marketplace"),
    (re.compile(r"%USERPROFILE%"), "%USERPROFILE%",
     "%USERPROFILE% apunta a la instalacion global, no al plugin"),
    (re.compile(r"~/\.claude/skills"), "~/.claude/skills",
     "~/.claude/skills es la instalacion global, no el plugin"),
    (re.compile(r"`plugins/[a-z]+/"), "plugins/",
     "plugins/<x>/ es una ruta de este repo, no de la instalacion"),
]

# Sitios donde una ruta obsoleta aparece a proposito, para desaconsejarla. Va
# por (fichero, patron) y no por fichero: eximir el fichero entero dejaria pasar
# tambien las formas que ahi no tienen excusa.
PERMITIDO = {
    ("plugins/aisdd/skills/aisdd-specs/SKILL.md", ".agents/skills/"),
    ("plugins/aisdd/skills/aisdd-specs/SKILL.md", "%USERPROFILE%"),
}

LEIBLES = {".md", ".py", ".sh", ".json", ".yaml", ".yml"}

errores: list[str] = []
internas = 0
enlazados = 0

for skill_dir in sorted(ROOT.glob("plugins/*/skills/*/")):
    if not skill_dir.is_dir():
        continue
    nombrados: set[str] = set()
    for f in sorted(skill_dir.rglob("*")):
        if not f.is_file() or f.suffix not in LEIBLES or "__pycache__" in f.parts:
            continue
        texto = f.read_text(encoding="utf-8", errors="replace")
        for m in INTERNA.finditer(texto):
            internas += 1
            nombrados.add(m.group(1))
            if not (skill_dir / m.group(1)).exists():
                errores.append(
                    f"{f.relative_to(ROOT)}: nombra `{m.group(1)}`, que no existe en "
                    f"{skill_dir.relative_to(ROOT)}. Si el destino es otro skill del mismo "
                    f"plugin, escribe la ruta completa "
                    f"(${{CLAUDE_PLUGIN_ROOT}}/skills/<skill>/{m.group(1)}); si es de otro "
                    f"plugin, quita la ruta y nombra solo el skill"
                )
        for b in BLOQUE.finditer(texto):
            for m in RELATIVA_EN_COMANDO.finditer(b.group(1)):
                errores.append(
                    f"{f.relative_to(ROOT)}: el comando usa `{m.group(1)}`, relativa al "
                    f"directorio del skill. Se ejecuta desde el proyecto del usuario, "
                    f"donde esa ruta no existe: anclala en "
                    f"${{CLAUDE_PLUGIN_ROOT}}/skills/{skill_dir.name}/{m.group(1)}")

    # Un reference que nadie nombra no se lee nunca: la carga es en diferido.
    for ref in sorted(skill_dir.glob("references/*.md")):
        rel = f"references/{ref.name}"
        enlazados += 1
        if rel not in nombrados:
            errores.append(
                f"{ref.relative_to(ROOT)}: ningun fichero del skill lo nombra, asi que "
                f"nadie lo lee (la carga es en diferido). Enlazalo desde SKILL.md o borralo"
            )

for f in sorted(ROOT.glob("plugins/**/*")):
    if not f.is_file() or f.suffix not in LEIBLES or "__pycache__" in f.parts:
        continue
    rel = str(f.relative_to(ROOT))
    # `methodology/` queda fuera por la misma razon que en check_plugin_assets.py:
    # son documentos en prosa sobre el metodo, que citan el corpus de este repo
    # para un lector humano. Ahi la ruta describe, no la resuelve nadie.
    if "methodology" in Path(rel).parts:
        continue
    texto = f.read_text(encoding="utf-8", errors="replace")
    for patron, etiqueta, motivo in LEGACY:
        if patron.search(texto) and (rel, etiqueta) not in PERMITIDO:
            errores.append(f"{rel}: {motivo}")

if errores:
    print("Rutas que no resuelven donde el skill las busca:", file=sys.stderr)
    for e in errores:
        print(f"  - {e}", file=sys.stderr)
    sys.exit(1)
print(f"Rutas de skills coherentes: {internas} referencias internas resueltas, "
      f"{enlazados} references enlazados desde su skill, comandos anclados al "
      f"plugin y sin rutas del empaquetado anterior.")
