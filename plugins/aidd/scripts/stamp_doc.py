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

Usage:
    python stamp_doc.py --input docs/detalle-historias-usuario.md
    python stamp_doc.py --input docs/roadmap.md --reset 1   # force a version
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
    version = args.reset if args.reset is not None else prev + 1

    now = datetime.now().astimezone()
    ts = now.strftime("%Y-%m-%d %H:%M")
    tz = now.strftime("%Z")
    when = f"{ts} {tz}".strip()
    stamp = f"> **Versión {version}** · **Generado:** {when}"

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

    meta[md.name] = {"version": version}
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"OK  {md}  ->  v{version}  ({when})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
