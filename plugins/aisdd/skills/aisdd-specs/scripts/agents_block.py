#!/usr/bin/env python3
"""aisdd-specs · agents_block.py — bloque idempotente dentro de AGENTS.md.

Gestiona un bloque delimitado del fichero ``AGENTS.md`` del proyecto:

    <!-- BEGIN aisdd-specs <marker> (auto-generado, no editar a mano) -->
    <contenido>
    <!-- END aisdd-specs <marker> -->

Si el bloque existe lo reemplaza íntegro; si no, lo añade al final precedido de
una línea en blanco. No toca el resto del fichero, de modo que los distintos
bloques conviven sin pisarse: ``commands`` lo gestiona ``aisdd init`` y
``roadmap`` lo gestiona ``aisdd roadmap``.

Sustituye a la prosa que pedía al agente hacer este reemplazo a mano. Un
reemplazo de bloque delimitado es exacto o no es: dejarlo al modelo invita a que
un día duplique el bloque o se lleve por delante lo que hay alrededor.

Migración: si existe un bloque legacy ``native-ai-specs <marker>`` y no el
actual, se reemplaza también (queda uno solo, con los marcadores nuevos).

Uso:
    python agents_block.py <marker> --content-file <f> [--root <dir>] [--file <path>]
    echo '<contenido>' | python agents_block.py <marker> [--root <dir>]

Salida (stdout): JSON con {"file", "action", "marker"}, donde ``action`` es
``created`` | ``replaced`` | ``appended`` | ``migrated``.

Solo biblioteca estándar.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SKILL = "aisdd-specs"
LEGACY_SKILL = "native-ai-specs"


def markers(skill: str, marker: str) -> tuple[str, str]:
    return (f"<!-- BEGIN {skill} {marker} (auto-generado, no editar a mano) -->",
            f"<!-- END {skill} {marker} -->")


def block_re(skill: str, marker: str) -> re.Pattern[str]:
    """Bloque completo, tolerante con el texto del comentario de apertura."""
    return re.compile(
        rf"<!--\s*BEGIN\s+{re.escape(skill)}\s+{re.escape(marker)}\b.*?-->"
        rf".*?"
        rf"<!--\s*END\s+{re.escape(skill)}\s+{re.escape(marker)}\s*-->",
        re.DOTALL,
    )


def render(marker: str, content: str) -> str:
    begin, end = markers(SKILL, marker)
    return f"{begin}\n{content.strip()}\n{end}"


def main() -> int:
    ap = argparse.ArgumentParser(description="Bloque idempotente en AGENTS.md.")
    ap.add_argument("marker", help="p. ej. 'commands' o 'roadmap'")
    ap.add_argument("--root", default=".", help="raíz del proyecto (default: cwd)")
    ap.add_argument("--file", default=None, help="ruta de AGENTS.md (default: <root>/AGENTS.md)")
    ap.add_argument("--content-file", default=None, help="fichero con el contenido; sin él, stdin")
    args = ap.parse_args()

    if args.content_file:
        content = Path(args.content_file).read_text(encoding="utf-8")
    else:
        content = sys.stdin.read()
    if not content.strip():
        print("error: contenido vacío", file=sys.stderr)
        return 2

    target = Path(args.file) if args.file else Path(args.root) / "AGENTS.md"
    new_block = render(args.marker, content)

    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(f"# AGENTS.md\n\n{new_block}\n", encoding="utf-8")
        action = "created"
    else:
        text = target.read_text(encoding="utf-8")
        current = block_re(SKILL, args.marker)
        legacy = block_re(LEGACY_SKILL, args.marker)
        if current.search(text):
            text, action = current.sub(lambda _: new_block, text, count=1), "replaced"
        elif legacy.search(text):
            text, action = legacy.sub(lambda _: new_block, text, count=1), "migrated"
        else:
            text, action = text.rstrip("\n") + f"\n\n{new_block}\n", "appended"
        target.write_text(text, encoding="utf-8")

    print(json.dumps({"file": str(target), "action": action, "marker": args.marker},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
