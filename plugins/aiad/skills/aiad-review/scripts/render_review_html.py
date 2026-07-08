#!/usr/bin/env python3
"""Render an AIAD code-review result into a standalone, self-contained HTML report.

This is the reporting half of the ``aiad-review`` skill. The skill (or its
``aiad-reviewer`` subagent) produces the didactic findings; this script turns a
JSON manifest of those findings into a single ``.html`` file the human can open
to follow the recommendations. For every finding it embeds the **actual code
lines** referenced (read from the repo by ``file:line``, or taken from an
explicit snippet), shown with line numbers and the relevant line(s) highlighted.

The report is standalone (inline CSS/JS, no external requests), theme-aware
(light/dark), responsive, and print-friendly. It never modifies source code.

Usage:
    python render_review_html.py --input review.json --output docs/aiad-reviews/review.html [--open]

Only the Python standard library is used (AIAD ships no third-party deps).
"""

from __future__ import annotations

import argparse
import html
import json
import sys
import webbrowser
from datetime import date
from pathlib import Path


# --------------------------------------------------------------------------- #
# Defaults / labels
# --------------------------------------------------------------------------- #

DEFAULT_LABELS = {
    "blocking": "Blocking",
    "improvement": "Improvement",
    "optional": "Optional",
    "what": "What happens",
    "why": "Why it matters",
    "suggestion": "Suggested direction",
    "good": "What is well done",
    "location": "Location",
    "summary": "Summary",
    "verdict": "Verdict",
    "scope": "Scope",
    "focus": "Focus",
    "no_code": "Code not available",
    "change": "Recommended change",
    "before": "Current code",
    "after": "Suggested code",
    "test_gap": "Tests",
    "impact": "Impact",
}

PRIORITY_ORDER = ["blocking", "improvement", "optional"]
PRIORITY_META = {
    "blocking": ("#e5484d", "Blocking"),
    "improvement": ("#f5a524", "Improvement"),
    "optional": ("#8b93a7", "Optional"),
}
VERDICT_META = {
    "ready": ("#30a46c", "READY"),
    "fixes-needed": ("#e5484d", "FIXES NEEDED"),
}


# --------------------------------------------------------------------------- #
# Code extraction
# --------------------------------------------------------------------------- #

def _target_lines(finding: dict) -> set[int]:
    hl = finding.get("highlight")
    if isinstance(hl, list) and hl:
        return {int(x) for x in hl}
    if isinstance(finding.get("lines"), list) and len(finding["lines"]) == 2:
        a, b = int(finding["lines"][0]), int(finding["lines"][1])
        return set(range(min(a, b), max(a, b) + 1))
    if finding.get("line") is not None:
        return {int(finding["line"])}
    return set()


def code_rows(finding: dict, base_dir: Path) -> list[tuple[int, str, bool]]:
    """Return [(lineno, text, is_target)] for the finding's code block.

    Prefers an explicit ``snippet``; otherwise reads the referenced file and
    extracts a context window around the target line(s).
    """
    targets = _target_lines(finding)

    snippet = finding.get("snippet")
    if isinstance(snippet, str) and snippet != "":
        start = int(finding.get("snippet_start", finding.get("line", 1)) or 1)
        rows = []
        for i, text in enumerate(snippet.splitlines()):
            ln = start + i
            rows.append((ln, text, ln in targets))
        return rows

    fpath = finding.get("file")
    if not fpath:
        return []
    try:
        lines = (base_dir / fpath).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []

    if not targets:
        targets = {1}
    ctx = int(finding.get("context", 3))
    lo = max(1, min(targets) - ctx)
    hi = min(len(lines), max(targets) + ctx)
    return [(ln, lines[ln - 1], ln in targets) for ln in range(lo, hi + 1)]


# --------------------------------------------------------------------------- #
# HTML building
# --------------------------------------------------------------------------- #

def esc(x) -> str:
    return html.escape("" if x is None else str(x))


def render_code_block(finding: dict, base_dir: Path) -> str:
    rows = code_rows(finding, base_dir)
    lang = finding.get("lang", "")
    if not rows:
        return f'<div class="code-empty">{esc(DEFAULT_LABELS["no_code"])}</div>'
    body = []
    for ln, text, is_target in rows:
        cls = "ln target" if is_target else "ln"
        body.append(
            f'<tr class="{"row-target" if is_target else ""}">'
            f'<td class="{cls}">{ln}</td>'
            f'<td class="src"><pre>{esc(text) or "&nbsp;"}</pre></td></tr>'
        )
    lang_badge = f'<span class="lang">{esc(lang)}</span>' if lang else ""
    return (
        f'<div class="code">{lang_badge}'
        f'<table class="codetable"><tbody>{"".join(body)}</tbody></table></div>'
    )


def render_change(finding: dict, labels: dict) -> str:
    """Optional recommended change: current code -> suggested code (a proposal, not applied)."""
    ch = finding.get("change")
    if not isinstance(ch, dict):
        return ""
    before, after = ch.get("before"), ch.get("after")
    cols = []
    if before:
        cols.append(
            f'<div class="diffcol diff-before"><div class="difflabel">{esc(labels["before"])}</div>'
            f'<pre>{esc(before)}</pre></div>'
        )
    if after:
        cols.append(
            f'<div class="diffcol diff-after"><div class="difflabel">{esc(labels["after"])}</div>'
            f'<pre>{esc(after)}</pre></div>'
        )
    if not cols:
        return ""
    return (
        f'<div class="fblock"><div class="flabel">{esc(labels["change"])}</div>'
        f'<div class="diffwrap">{"".join(cols)}</div></div>'
    )


def render_finding(finding: dict, labels: dict, base_dir: Path) -> str:
    prio = (finding.get("priority") or "improvement").lower()
    color, _ = PRIORITY_META.get(prio, PRIORITY_META["improvement"])
    tag = finding.get("tag", "")
    fid = finding.get("id", "")
    title = finding.get("title", "")

    loc = ""
    if finding.get("file"):
        line_txt = ""
        if finding.get("lines"):
            line_txt = f':{finding["lines"][0]}-{finding["lines"][1]}'
        elif finding.get("line") is not None:
            line_txt = f':{finding["line"]}'
        loc = f'<code class="loc">{esc(finding["file"])}{esc(line_txt)}</code>'

    def block(label_key, value):
        if not value:
            return ""
        return (
            f'<div class="fblock"><div class="flabel">{esc(labels[label_key])}</div>'
            f'<div class="ftext">{esc(value)}</div></div>'
        )

    tag_html = f'<span class="tag">{esc(tag)}</span>' if tag else ""
    id_html = f'<span class="fid">{esc(fid)}</span>' if fid else ""
    floc_html = f'<div class="floc">{esc(labels["location"])}: {loc}</div>' if loc else ""
    return (
        f'<article class="finding" style="--accent:{color}">'
        f'<header class="fhead">'
        f'<span class="prio" style="background:{color}">{esc(labels.get(prio, prio))}</span>'
        f'{tag_html}{id_html}'
        f'<h3 class="ftitle">{esc(title)}</h3>'
        f'</header>'
        f'{floc_html}'
        f'{render_code_block(finding, base_dir)}'
        f'{block("what", finding.get("what"))}'
        f'{block("impact", finding.get("impact"))}'
        f'{block("why", finding.get("why"))}'
        f'{block("suggestion", finding.get("suggestion"))}'
        f'{render_change(finding, labels)}'
        f'{block("test_gap", finding.get("test_gap"))}'
        f'</article>'
    )


def build_html(manifest: dict, base_dir: Path) -> str:
    labels = {**DEFAULT_LABELS, **(manifest.get("labels") or {})}
    title = manifest.get("title") or "AIAD review"
    scope = manifest.get("scope", "")
    focus = manifest.get("focus", "")
    the_date = manifest.get("date") or date.today().isoformat()
    verdict = (manifest.get("verdict") or "").lower()
    vcolor, vtext = VERDICT_META.get(verdict, ("#8b93a7", (verdict or "—").upper()))
    verdict_note = manifest.get("verdict_note", "")
    summary = manifest.get("summary", "")
    good = manifest.get("good") or []
    findings = manifest.get("findings") or []

    counts = {p: 0 for p in PRIORITY_ORDER}
    for f in findings:
        p = (f.get("priority") or "improvement").lower()
        counts[p] = counts.get(p, 0) + 1

    kpis = "".join(
        f'<div class="kpi" style="--c:{PRIORITY_META[p][0]}">'
        f'<div class="kpi-n">{counts.get(p, 0)}</div>'
        f'<div class="kpi-l">{esc(labels[p])}</div></div>'
        for p in PRIORITY_ORDER
    )

    sections = []
    for p in PRIORITY_ORDER:
        group = [f for f in findings if (f.get("priority") or "improvement").lower() == p]
        if not group:
            continue
        cards = "".join(render_finding(f, labels, base_dir) for f in group)
        sections.append(
            f'<section class="group"><h2 class="ghead" style="--c:{PRIORITY_META[p][0]}">'
            f'{esc(labels[p])} <span class="gcount">{len(group)}</span></h2>{cards}</section>'
        )

    good_html = ""
    if good:
        items = "".join(f"<li>{esc(g)}</li>" for g in good)
        good_html = (
            f'<section class="good"><h2 class="ghead ghead-good">{esc(labels["good"])}</h2>'
            f'<ul>{items}</ul></section>'
        )

    summary_html = (
        f'<p class="summary">{esc(summary)}</p>' if summary else ""
    )
    meta_bits = []
    if scope:
        meta_bits.append(f'<span><b>{esc(labels["scope"])}:</b> {esc(scope)}</span>')
    if focus:
        meta_bits.append(f'<span><b>{esc(labels["focus"])}:</b> {esc(focus)}</span>')
    meta_bits.append(f"<span>{esc(the_date)}</span>")
    meta_html = " · ".join(meta_bits)

    vnote = f'<span class="vnote">{esc(verdict_note)}</span>' if verdict_note else ""

    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<style>
{CSS}
</style>
</head>
<body>
<main class="wrap">
  <header class="top">
    <div class="top-row">
      <h1>{esc(title)}</h1>
      <span class="verdict" style="background:{vcolor}">{esc(vtext)}</span>
    </div>
    <div class="meta">{meta_html}</div>
    {vnote}
    {summary_html}
    <div class="kpis">{kpis}</div>
  </header>
  {"".join(sections) if sections else '<p class="empty">Sin hallazgos.</p>'}
  {good_html}
  <footer class="foot">AIAD · aiad-review — revision didactica (ia-in-the-loop). El codigo es tuyo; tu decides que cambiar.</footer>
</main>
</body>
</html>
"""


CSS = """
:root{
  --bg:#f7f8fa; --card:#ffffff; --ink:#1c2230; --muted:#5b6472; --line:#e3e6ec;
  --code-bg:#f4f6f9; --code-ink:#1c2230; --target:#fff6d6; --target-line:#f5a524;
}
@media (prefers-color-scheme: dark){
  :root{ --bg:#0f1319; --card:#161b23; --ink:#e6e9ef; --muted:#9aa3b2; --line:#252c37;
    --code-bg:#0c1016; --code-ink:#dbe1ea; --target:#2c2410; --target-line:#f5a524; }
}
:root[data-theme="light"]{ --bg:#f7f8fa; --card:#ffffff; --ink:#1c2230; --muted:#5b6472; --line:#e3e6ec; --code-bg:#f4f6f9; --code-ink:#1c2230; --target:#fff6d6; --target-line:#f5a524; }
:root[data-theme="dark"]{ --bg:#0f1319; --card:#161b23; --ink:#e6e9ef; --muted:#9aa3b2; --line:#252c37; --code-bg:#0c1016; --code-ink:#dbe1ea; --target:#2c2410; --target-line:#f5a524; }
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;}
.wrap{max-width:960px;margin:0 auto;padding:28px 20px 60px}
.top{border-bottom:1px solid var(--line);padding-bottom:18px;margin-bottom:22px}
.top-row{display:flex;align-items:center;gap:14px;flex-wrap:wrap}
h1{font-size:24px;margin:0;flex:1;min-width:220px}
.verdict{color:#fff;font-weight:700;font-size:12px;letter-spacing:.06em;padding:6px 12px;border-radius:999px;white-space:nowrap}
.meta{color:var(--muted);font-size:13px;margin-top:8px;display:flex;gap:6px;flex-wrap:wrap}
.vnote{display:block;margin-top:8px;color:var(--muted);font-style:italic}
.summary{margin:12px 0 0;color:var(--ink)}
.kpis{display:flex;gap:12px;margin-top:18px;flex-wrap:wrap}
.kpi{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--c);
  border-radius:10px;padding:10px 16px;min-width:120px}
.kpi-n{font-size:26px;font-weight:800;color:var(--c);line-height:1}
.kpi-l{font-size:12px;color:var(--muted);margin-top:2px;text-transform:uppercase;letter-spacing:.05em}
.group{margin-top:30px}
.ghead{font-size:15px;text-transform:uppercase;letter-spacing:.06em;color:var(--c);
  border-bottom:2px solid var(--c);padding-bottom:6px;margin:0 0 16px;display:flex;align-items:center;gap:8px}
.ghead-good{--c:#30a46c;color:#30a46c;border-color:#30a46c}
.gcount{background:var(--c);color:#fff;font-size:11px;border-radius:999px;padding:1px 8px}
.finding{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--accent);
  border-radius:12px;padding:16px 18px;margin-bottom:16px}
.fhead{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.prio{color:#fff;font-size:11px;font-weight:700;padding:2px 9px;border-radius:999px;text-transform:uppercase;letter-spacing:.04em}
.tag{font-size:11px;color:var(--muted);border:1px solid var(--line);border-radius:999px;padding:1px 8px}
.fid{font-size:12px;color:var(--muted);font-weight:600}
.ftitle{font-size:16px;margin:0;flex:1 1 100%;order:9}
.floc{margin:10px 0 8px;font-size:13px;color:var(--muted)}
.loc{background:var(--code-bg);border:1px solid var(--line);border-radius:6px;padding:1px 7px;
  font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12.5px}
.code{position:relative;background:var(--code-bg);border:1px solid var(--line);border-radius:10px;
  overflow-x:auto;margin:10px 0 4px}
.lang{position:absolute;top:6px;right:10px;font-size:10.5px;color:var(--muted);
  text-transform:uppercase;letter-spacing:.06em;z-index:1}
.codetable{border-collapse:collapse;width:100%;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12.5px}
.codetable td{padding:0;vertical-align:top}
.ln{width:1%;white-space:nowrap;text-align:right;color:var(--muted);user-select:none;
  padding:1px 12px 1px 12px;border-right:1px solid var(--line);opacity:.75}
.ln.target{color:var(--target-line);font-weight:700;opacity:1}
.src{width:100%}
.src pre{margin:0;padding:1px 14px;white-space:pre;color:var(--code-ink)}
.row-target{background:var(--target)}
.row-target .src pre{box-shadow:inset 3px 0 0 var(--target-line)}
.code-empty{color:var(--muted);font-style:italic;padding:10px 14px;background:var(--code-bg);
  border:1px dashed var(--line);border-radius:10px;margin:10px 0}
.fblock{margin-top:12px}
.flabel{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);font-weight:700;margin-bottom:2px}
.ftext{color:var(--ink)}
.diffwrap{display:grid;grid-template-columns:1fr 1fr;gap:10px}
@media(max-width:640px){.diffwrap{grid-template-columns:1fr}}
.diffcol{border:1px solid var(--line);border-radius:8px;overflow-x:auto}
.difflabel{font-size:10.5px;text-transform:uppercase;letter-spacing:.05em;font-weight:700;padding:4px 10px;border-bottom:1px solid var(--line)}
.diffcol pre{margin:0;padding:8px 12px;white-space:pre;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12.5px;color:var(--code-ink)}
.diff-before{background:color-mix(in srgb,#e5484d 7%,var(--code-bg))}
.diff-before .difflabel{color:#e5484d;background:color-mix(in srgb,#e5484d 12%,transparent)}
.diff-after{background:color-mix(in srgb,#30a46c 8%,var(--code-bg))}
.diff-after .difflabel{color:#30a46c;background:color-mix(in srgb,#30a46c 12%,transparent)}
.good{margin-top:30px;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 18px}
.good ul{margin:8px 0 0;padding-left:20px}
.good li{margin:4px 0}
.empty{color:var(--muted);font-style:italic}
.foot{margin-top:40px;padding-top:16px;border-top:1px solid var(--line);color:var(--muted);font-size:12px}
@media print{
  body{background:#fff}
  .finding,.kpi,.good{break-inside:avoid}
  .code{overflow-x:visible}
  .src pre{white-space:pre-wrap;word-break:break-word}
}
"""


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Render an AIAD review result to standalone HTML.")
    p.add_argument("--input", required=True, help="JSON manifest with the review findings.")
    p.add_argument("--output", required=True, help="Output .html path.")
    p.add_argument("--base-dir", default=".", help="Repo root to resolve file paths (default: cwd).")
    p.add_argument("--open", action="store_true", help="Open the HTML when done (best-effort).")
    args = p.parse_args(argv)

    in_path = Path(args.input)
    out_path = Path(args.output)
    base_dir = Path(args.base_dir)

    if not in_path.is_file():
        sys.stderr.write(f"ERROR: input manifest not found: {in_path}\n")
        return 2
    try:
        manifest = json.loads(in_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"ERROR: invalid JSON manifest: {exc}\n")
        return 2
    if not isinstance(manifest, dict):
        sys.stderr.write("ERROR: the manifest root must be a JSON object.\n")
        return 2

    doc = build_html(manifest, base_dir)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(doc, encoding="utf-8")

    n = len(manifest.get("findings") or [])
    print(f"OK  -> {out_path}")
    print(f"    findings: {n}")
    if args.open:
        try:
            webbrowser.open(out_path.resolve().as_uri())
        except Exception:  # noqa: BLE001 - never fail on open
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
