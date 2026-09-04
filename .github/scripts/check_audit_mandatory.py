#!/usr/bin/env python3
"""Todo comando de aisdd ordena su entrada de auditoria, y no puede omitirla.

La auditoria es obligatoria en todos los comandos salvo `aisdd lane`. Y no es
una formalidad: en una auditoria real de un proyecto se descubrio que **no habia
ni una entrada hasta la fase 5**, porque el agente aplico la carga bajo demanda
tambien al fichero que explica como escribirla. No fallo nada --por eso tardo
cinco fases en verse--.

Dos cosas se comprueban aqui, y las dos son de las que no dan error por su
cuenta:

1. **Cada ficha que documenta un comando ordena la entrada**, con el
   `prompt_version` que le corresponde. Una ficha nueva que se olvide del paso
   final produce un comando que nunca deja rastro, y el hueco solo se ve
   auditando el proyecto meses despues.
2. **El indice dice que la auditoria no entra en la carga bajo demanda.** Es la
   clausula que causo el fallo: sin ella, "no cargues lo que no necesitas" se
   lee como permiso para no abrir `audit.md`, y sin ese fichero la entrada no se
   compone.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "plugins/aisdd/skills/aisdd-specs/SKILL.md"
REFS = ROOT / "plugins/aisdd/skills/aisdd-specs/references"

# Una ficha documenta un comando si tiene un encabezado `## \`aisdd ...\``.
CABECERA = re.compile(r"^## `aisdd [^`]+`", re.M)
# `aisdd lane` solo mueve un puntero local: es la unica excepcion declarada.
EXENTOS = {"lane.md"}

errors: list[str] = []
comprobadas = 0

for ficha in sorted(REFS.glob("*.md")):
    texto = ficha.read_text(encoding="utf-8", errors="replace")
    if not CABECERA.search(texto):
        continue                      # no documenta un comando
    if ficha.name in EXENTOS:
        continue
    comprobadas += 1
    if "entrada de auditoria" not in texto.lower():
        errors.append(f"{ficha.name}: documenta un comando y **no ordena la entrada de "
                      f"auditoria**. Ese comando no dejaria rastro, y el hueco solo se "
                      f"ve auditando el proyecto meses despues")
    elif "prompt_version" not in texto:
        errors.append(f"{ficha.name}: ordena la auditoria pero no dice que "
                      f"`prompt_version` usar; sin el no se sabe que instrucciones "
                      f"produjeron la entrada")

# El skill hermano documenta `aisdd amend change`, que tambien audita --incluidas
# sus cuatro paradas-- y no vive en `references/`: sin esto se quedaba fuera del
# guardian, que es como se cuelan justo estos fallos.
AMEND = ROOT / "plugins/aisdd/skills/aisdd-amend/SKILL.md"
if not AMEND.is_file():
    errors.append("no existe el SKILL.md de aisdd-amend")
else:
    amend = AMEND.read_text(encoding="utf-8", errors="replace")
    comprobadas += 1
    if "entrada de auditoria" not in amend.lower():
        errors.append("aisdd-amend/SKILL.md: documenta un comando y no ordena la "
                      "entrada de auditoria")
    elif "prompt_version" not in amend:
        errors.append("aisdd-amend/SKILL.md: ordena la auditoria pero no dice que "
                      "`prompt_version` usar")

if not SKILL.is_file():
    errors.append("no existe el SKILL.md de aisdd-specs")
else:
    indice = SKILL.read_text(encoding="utf-8", errors="replace").lower()
    if "bajo demanda" in indice and "no alcanza a la auditoria" not in indice:
        errors.append("SKILL.md declara la carga bajo demanda y **no la acota**: sin "
                      "decir que la auditoria queda fuera, 'no cargues lo que no "
                      "necesitas' se lee como permiso para no abrir `audit.md`")

if errors:
    print("Comandos que podrian quedarse sin auditoria:", file=sys.stderr)
    for e in errors:
        print(f"  - {e}", file=sys.stderr)
    sys.exit(1)
print(f"Auditoria ordenada en las {comprobadas} fichas de comando "
      f"({len(EXENTOS)} exenta) y acotada la carga bajo demanda en el indice.")
