#!/usr/bin/env python3
"""aisdd-specs · check_mojibake.py — detecta (y opcionalmente repara) mojibake.

Mojibake es texto UTF-8 leído como Latin-1/CP1252: 'Ã³' donde debía ir 'ó',
'â€"' donde iba un guión largo. Aparece cuando un artefacto pasa por una
herramienta que asume la codificación equivocada, y una vez dentro del fichero
se propaga a todo lo que se genere a partir de él.

Importa aquí porque los artefactos de un change (``proposal.md``, ``spec.md``,
``decisions.md``) y los documentos de ``docs/`` son español con tildes, se
generan desde el agente y se leen desde otras herramientas.

La lógica de detección y reparación es la misma que ya usa
``booster-docs/scripts/render_docs_html.py``, extraída para poder ejecutarla
sobre ficheros sueltos sin renderizar nada.

Uso:
    python check_mojibake.py <fichero...>           # solo informa
    python check_mojibake.py --fix <fichero...>     # repara in situ

Código de salida:
    0  sin mojibake, o todo reparado con --fix
    1  queda mojibake
    2  error de uso

Solo biblioteca estándar.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Secuencias que delatan UTF-8 malinterpretado, más U+FFFD (carácter de
# reemplazo: ahí la información original ya se perdió y no hay reparación).
# Mantener sincronizado con render_docs_html.py de booster-docs: es el mismo
# fenomeno y debe detectarse igual en ambos sitios. El tercer caso NO admite un
# rango tipo [\x80-\x9f]: en Python eso son codepoints U+0080-U+009F, y los
# caracteres que de verdad aparecen tras 'â' son tipograficos (U+20AC '€',
# U+2019, U+2014...). Por eso van enumerados uno a uno.
MOJIBAKE_RE = re.compile(
    r"(?:"
    r"\xc3[\x80-\xbf]"
    r"|\xc2[\x80-\xbf]"
    r"|\xe2[\u20ac\u201a-\u201e\u2020-\u2026\u2030\u0160\u2039\u0152\u017d"
    r"\u2018-\u201d\u2022\u2013-\u2014\u02dc\u2122\u0161\u203a\u0153\u017e\u0178]"
    r"|\ufffd"
    r")"
)
TOKEN_RE = re.compile(r"\S*(?:" + MOJIBAKE_RE.pattern + r")\S*")


def score(text: str) -> int:
    return len(MOJIBAKE_RE.findall(text))


def repair(text: str) -> tuple[str, int]:
    """Repara token a token, y solo si el resultado mejora.

    El round-trip cp1252 -> utf-8 puede empeorar texto legítimo (una palabra
    francesa, un símbolo suelto), así que cada token se acepta únicamente
    cuando baja su propia puntuación de mojibake.
    """
    repaired = 0

    def fix_token(m: re.Match[str]) -> str:
        nonlocal repaired
        token = m.group(0)
        try:
            candidate = token.encode("cp1252").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            return token
        if score(candidate) < score(token):
            repaired += 1
            return candidate
        return token

    return TOKEN_RE.sub(fix_token, text), repaired


def main() -> int:
    ap = argparse.ArgumentParser(description="Detecta o repara mojibake.")
    ap.add_argument("files", nargs="+", help="ficheros a revisar")
    ap.add_argument("--fix", action="store_true", help="repara in situ")
    args = ap.parse_args()

    remaining = 0
    for name in args.files:
        path = Path(name)
        if not path.is_file():
            print(f"  omitido (no existe): {name}", file=sys.stderr)
            continue
        # newline="" preserva los finales de linea tal cual: este script repara
        # mojibake y nada mas. Convertir CRLF a LF de paso ensuciaria el diff
        # del fichero entero en equipos que trabajan en Windows.
        with path.open("r", encoding="utf-8", errors="replace", newline="") as fh:
            text = fh.read()
        found = score(text)
        if not found:
            continue
        if args.fix:
            fixed, n = repair(text)
            left = score(fixed)
            if n:
                with path.open("w", encoding="utf-8", newline="") as fh:
                    fh.write(fixed)
            print(f"  {name}: {found} detectados, {n} reparados, {left} sin reparar")
            remaining += left
        else:
            print(f"  {name}: {found} secuencias de mojibake")
            remaining += found

    if remaining:
        print(f"mojibake pendiente: {remaining} secuencia(s)", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
