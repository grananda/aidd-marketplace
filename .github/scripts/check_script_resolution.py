#!/usr/bin/env python3
"""Todo sitio que invoque un script dice tambien como resolver su ruta.

`${CLAUDE_PLUGIN_ROOT}` la define Claude Code. **Otros agentes la dejan vacia**
--medido en Codex CLI 0.151.0: `echo "ROOT=[${CLAUDE_PLUGIN_ROOT}]"` devuelve
`ROOT=[]`-- y entonces `python3 "${CLAUDE_PLUGIN_ROOT}/skills/.../audit.py"` se
convierte en `/skills/.../audit.py` y falla. Ahi se cae la entrada de auditoria,
que el metodo declara obligatoria en todos los comandos.

El script sigue estando en el disco: basta localizarlo una vez y usar la ruta
absoluta. Pero eso solo ocurre si el documento que manda ejecutarlo **lo dice**.
Un fichero nuevo que copie la forma de invocacion sin la nota deja el agujero
otra vez, y no falla: simplemente no se ejecuta lo que hacia falta.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Una invocacion real: `python3 "${CLAUDE_PLUGIN_ROOT}/..../algo.py"`.
INVOCA = re.compile(r'python3? "\$\{CLAUDE_PLUGIN_ROOT\}[^"]*\.py"')
# La nota que explica que hacer si la variable llega vacia.
MARCA = "comprueba que la ruta resuelve"

errors: list[str] = []
con_nota = 0

for f in sorted(ROOT.glob("plugins/**/*.md")):
    if "methodology" in f.parts:
        continue                      # prosa descriptiva, no ordenes a ejecutar
    texto = f.read_text(encoding="utf-8", errors="replace")
    if not INVOCA.search(texto):
        continue
    if MARCA in texto:
        con_nota += 1
    else:
        errors.append(
            f"{f.relative_to(ROOT)}: invoca un script por "
            f"${{CLAUDE_PLUGIN_ROOT}} y no dice que hacer si llega vacia "
            f"(anade la nota de resolucion; fuera de Claude Code la orden falla)"
        )

if errors:
    print("Invocaciones de script sin regla de resolucion:", file=sys.stderr)
    for e in errors:
        print(f"  - {e}", file=sys.stderr)
    sys.exit(1)
print(f"Resolucion de scripts documentada en los {con_nota} ficheros que invocan alguno.")
