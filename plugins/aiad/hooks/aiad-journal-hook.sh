#!/usr/bin/env bash
# aiad-journal-hook — factual authorship capture for AIAD (ia-in-the-loop).
#
# Fires on PostToolUse for Write/Edit/MultiEdit and appends one factual line to
# docs/aiad-journal.md recording that the AI edited a file. It is:
#   - OPT-IN  : does nothing unless docs/aiad-journal.md already exists in the
#               project. A project enables factual journaling by creating that
#               file (e.g. `aiad journal log ...` once, or `touch docs/aiad-journal.md`).
#   - PASSIVE : it only records. It never blocks, never edits code, never asks.
#               This is the one allowed "push" in AIAD: it registers, it does not
#               police. Free will over guardrails.
#   - SAFE    : never fails the session. Always exits 0.
#
# Why this matters: edits the AI makes go through its tools and get logged here;
# what the human types by hand in their editor is NOT seen by this hook and is
# therefore theirs by definition. The craft ratio becomes factual, not self-reported.

JOURNAL="docs/aiad-journal.md"

# Opt-in: only act in projects that have a journal.
[ -f "$JOURNAL" ] || exit 0

input="$(cat 2>/dev/null)"
[ -n "$input" ] || exit 0

tool=""
file=""

if command -v jq >/dev/null 2>&1; then
  tool="$(printf '%s' "$input" | jq -r '.tool_name // empty' 2>/dev/null)"
  file="$(printf '%s' "$input" | jq -r '.tool_input.file_path // (.tool_input.edits[0].file_path) // empty' 2>/dev/null)"
elif command -v python3 >/dev/null 2>&1; then
  eval "$(printf '%s' "$input" | python3 -c '
import sys, json, shlex
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)
ti = d.get("tool_input") or {}
f = ti.get("file_path")
if not f:
    edits = ti.get("edits") or []
    if isinstance(edits, list) and edits:
        f = (edits[0] or {}).get("file_path")
print("tool=" + shlex.quote(str(d.get("tool_name") or "")))
print("file=" + shlex.quote(str(f or "")))
' 2>/dev/null)"
else
  # No JSON parser available: do not guess, just skip silently.
  exit 0
fi

[ -n "$file" ] || exit 0

# Make the path relative to the project root when possible.
case "$file" in
  "$PWD"/*) rel="${file#"$PWD"/}" ;;
  *)        rel="$file" ;;
esac

# Never log the journal editing itself.
[ "$rel" = "$JOURNAL" ] && exit 0

ts="$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date 2>/dev/null)"

printf -- '- %s | US:- | skill:aiad-hook | mode:%s | authored:ai-edit | file:%s | note:auto-captured AI edit\n' \
  "$ts" "${tool:-edit}" "$rel" >> "$JOURNAL" 2>/dev/null

exit 0
