#!/usr/bin/env python3
"""Stamp an AIDD planning document with an auto-incrementing version and a real timestamp.

Every AIDD skill that generates a document calls this right after (over)writing its
``.md`` (before rendering the HTML view). It adds/updates a single header line just
below the title:

    > **Version N** - **Generado:** YYYY-MM-DD HH:MM TZ

The version lives in a sidecar (``docs/.aidd-doc-meta.json`` by default) so it keeps
incrementing across regenerations even though the ``.md`` is rewritten each time. The
timestamp is the real local date and time -- neither value should be invented by the
model; this script is the single source of both.

APPROVAL STATE
--------------
Most AIDD planning documents are gated on human approval. That gate used to be a
fixed line -- ``> Pendiente de aprobacion humana.`` -- written into the template by
each skill. It never went away: nothing read it, nothing cleared it, and since the
``.md`` is rewritten on every run, a human who deleted it after approving got it back
on the next generation. A marker that always says the same thing tells you nothing,
and an unapproved document became indistinguishable from an approved one.

The approval now lives in the same sidecar as the version, because approving is
always approving **a version**:

    > **Version 3** - **Generado:** ... - **Pendiente de aprobacion**
    > **Version 3** - **Generado:** ... - **Aprobada** por Ana Ruiz el 2026-08-28
    > **Version 3** - **Generado:** ... - **Pendiente** (aprobada la v2)

The third line is the one that earns the feature: it says the document changed after
someone approved it, which is exactly what a stale approval looks like and what no
amount of fixed text could express.

Usage:
    python stamp_doc.py --input docs/detalle-historias-usuario.md
    python stamp_doc.py --input docs/roadmap.md --reset 1   # force a version
    python stamp_doc.py --input docs/requisitos.md --gated  # add the approval state
    python stamp_doc.py --input docs/requisitos.md --approve "Ana Ruiz"  # approve current
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# Matches a stamp line previously written by this script (so it is replaced, not duplicated).
STAMP_RE = re.compile(r"^>\s*\*\*Versi[oó]n\b.*$", re.MULTILINE)


def _load_meta(path: Path) -> dict:
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except (ValueError, OSError):
            pass
    return {}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Stamp an AIDD document with version + datetime.")
    p.add_argument("--input", required=True, help="Markdown document to stamp (in place).")
    p.add_argument("--meta", default=None,
                   help="Sidecar JSON with per-document versions (default: <dir>/.aidd-doc-meta.json).")
    p.add_argument("--gated", action="store_true",
                   help="Documento sujeto a aprobacion humana: anade el estado al sello.")
    p.add_argument("--approve", metavar="QUIEN", default=None,
                   help="Marca la version ACTUAL como aprobada por QUIEN y sale sin regenerar.")
    p.add_argument("--reset", type=int, default=None,
                   help="Force this version number instead of incrementing.")
    args = p.parse_args(argv)

    md = Path(args.input)
    if not md.is_file():
        sys.stderr.write(f"ERROR: no existe el documento: {md}\n")
        return 2

    meta_path = Path(args.meta) if args.meta else md.parent / ".aidd-doc-meta.json"
    meta = _load_meta(meta_path)
    entry = meta.get(md.name)
    prev = int(entry["version"]) if isinstance(entry, dict) and "version" in entry else 0
    # `--approve` no genera nada: solo anota que la version que ya hay quedo
    # aprobada. Separarlo de la generacion es lo que permite distinguir despues
    # "aprobada" de "cambiada despues de aprobarse".
    if args.approve is not None:
        if not prev:
            print(f"error: {md} no tiene version todavia; genera el documento antes de aprobarlo",
                  file=sys.stderr)
            return 2
        entry = entry if isinstance(entry, dict) else {"version": prev}
        entry["approved_version"] = prev
        entry["approved_by"] = args.approve
        entry["approved_on"] = datetime.now().astimezone().strftime("%Y-%m-%d")
        meta[md.name] = entry
        meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
                             encoding="utf-8")
        print(json.dumps({"file": str(md), "approved_version": prev,
                          "approved_by": args.approve, "approved_on": entry["approved_on"]},
                         ensure_ascii=False))
        return 0

    version = args.reset if args.reset is not None else prev + 1

    now = datetime.now().astimezone()
    ts = now.strftime("%Y-%m-%d %H:%M")
    tz = now.strftime("%Z")
    when = f"{ts} {tz}".strip()
    stamp = f"> **Versión {version}** · **Generado:** {when}"
    if args.gated:
        aprobada = entry.get("approved_version") if isinstance(entry, dict) else None
        if aprobada == version:
            stamp += (f" · **Aprobada** por {entry['approved_by']} el {entry['approved_on']}")
        elif aprobada:
            # El caso que justifica todo esto: hubo aprobacion, pero de otra version.
            stamp += f" · **Pendiente de aprobación** (aprobada la v{aprobada})"
        else:
            stamp += " · **Pendiente de aprobación**"

    text = md.read_text(encoding="utf-8")
    text = STAMP_RE.sub("", text)  # drop any previous stamp
    lines = text.splitlines()

    # Insert the stamp as the first blockquote header line; else just under the H1; else at top.
    insert_at = None
    for idx, ln in enumerate(lines):
        if ln.lstrip().startswith(">"):
            insert_at = idx
            break
    if insert_at is None:
        for idx, ln in enumerate(lines):
            if ln.startswith("# "):
                insert_at = idx + 1
                if insert_at < len(lines) and lines[insert_at].strip() == "":
                    insert_at += 1  # keep the blank line under the title
                break
    if insert_at is None:
        insert_at = 0

    lines.insert(insert_at, stamp)
    new = "\n".join(lines)
    new = re.sub(r"\n{3,}", "\n\n", new)
    if not new.endswith("\n"):
        new += "\n"
    md.write_text(new, encoding="utf-8")

    # Se actualiza la entrada, no se reemplaza: sustituirla borraria la aprobacion
    # en la siguiente generacion, que es justo el defecto que este estado arregla.
    meta[md.name] = {**(entry if isinstance(entry, dict) else {}), "version": version}
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"OK  {md}  ->  v{version}  ({when})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
