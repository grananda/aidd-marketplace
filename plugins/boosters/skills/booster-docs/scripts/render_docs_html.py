#!/usr/bin/env python3
"""Render an AIDD planning Markdown document into a standalone, visual HTML file.

The Markdown files under ``docs/`` remain the single source of truth (read and
written by the AIDD/SDD skills and reviewed by humans via git). This script
produces a *complementary* human-facing HTML view: it never edits the Markdown.

Beyond a faithful Markdown render it adds planning-oriented visual elements:
  * a KPI dashboard auto-computed from the content (RF/NFR counts, blockers,
    open questions, scope in/out balance, effort mix, MoSCoW mix...);
  * colored chips for traceable IDs (RF-XX, NFR-XX), priorities (Alta/Media/Baja,
    S/M/L), MoSCoW buckets, [IMPRESCINDIBLE] essential-criterion markers (prominent
    red-orange) and [BLOQUEANTE] real-impediment markers (red), both inline, in
    tables and summarized in the top KPI dashboard;
  * a color swatch shown next to any #hex / rgb() / hsl() color code (handy for the
    style-guide palette and design tokens);
  * scope "dentro / fuera de esta fase" rendered as side-by-side cards.

Doc-type is auto-detected from the H1 / filename but can be forced with
``--doc-type``. Unknown doc types still get a faithful render plus whatever KPIs
can be derived generically.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
import webbrowser
from collections import Counter
from datetime import date
from pathlib import Path


# --- Encoding hygiene (shared approach with render_uml_html.py) --------------

MOJIBAKE_RE = re.compile(
    r"(?:"
    r"Ã[-¿]"
    r"|Â[-¿]"
    r"|â[€‚-„†-…‰Š‹ŒŽ"
    r"‘-”•–-—˜™š›œžŸ]"
    r"|�"
    r")"
)
MOJIBAKE_TOKEN_RE = re.compile(r"\S*(?:" + MOJIBAKE_RE.pattern + r")\S*")
LOSSY_STDIN_RE = re.compile(r"[A-Za-z]\?[A-Za-z]")


def configure_text_streams() -> None:
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name)
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def read_stdin_utf8() -> str:
    buffer = getattr(sys.stdin, "buffer", None)
    if buffer is None:
        data = sys.stdin.read()
        return data if isinstance(data, str) else data.decode("utf-8-sig")
    return buffer.read().decode("utf-8-sig")


def mojibake_score(text: str) -> int:
    return len(MOJIBAKE_RE.findall(text))


def repair_common_mojibake(text: str) -> tuple[str, int]:
    repaired_count = 0

    def repair_token(match: re.Match[str]) -> str:
        nonlocal repaired_count
        token = match.group(0)
        try:
            repaired = token.encode("cp1252").decode("utf-8")
        except UnicodeError:
            return token
        if mojibake_score(repaired) < mojibake_score(token):
            repaired_count += 1
            return repaired
        return token

    return MOJIBAKE_TOKEN_RE.sub(repair_token, text), repaired_count


# --- Doc types --------------------------------------------------------------

DOC_TYPES = {
    "cliente-requisitos": {"label": "Brief del cliente", "phase": "Fase 0"},
    "requisitos": {"label": "Requisitos", "phase": "Fase 1 · 1.1"},
    "mapa-historias-usuario": {"label": "Mapa de historias", "phase": "Fase 1 · 1.2"},
    "detalle-historias-usuario": {"label": "Detalle de historias", "phase": "Fase 1 · 1.3"},
    "arquitectura-base-prototipo": {"label": "Arquitectura del prototipo", "phase": "Fase 2 · 2.1"},
    "propuesta-arquitectura-base": {"label": "Propuesta de arquitectura", "phase": "Fase 2 · 2.3"},
    "guia-estilos": {"label": "Guia de estilos", "phase": "Fase 2 · 2.3"},
    "arquitectura-base": {"label": "Arquitectura base", "phase": "Fase 2 · 2.4"},
    "roadmap": {"label": "Roadmap", "phase": "Fase 3"},
    "planificacion-proyecto": {"label": "Plan de proyecto", "phase": "Fase 3.5 · 3.5.1"},
    "sprint-plan": {"label": "Plan de sprints", "phase": "Fase 3.5 · 3.5.2"},
}


def detect_doc_type(stem: str) -> str:
    stem = stem.lower()
    for key in DOC_TYPES:
        if key in stem:
            return key
    return "generic"


# --- Inline chip decoration -------------------------------------------------

RF_ID_RE = re.compile(r"\b(RF-\d+)\b")
NFR_ID_RE = re.compile(r"\b(NFR-\d+)\b")
US_ID_RE = re.compile(r"\b(HU-\d+|US-\d+)\b")
BLOCKING_RE = re.compile(r"\[\s*BLOQUEANTE\s*\]", re.IGNORECASE)
# Essential acceptance criterion: a must-have (NOT an impediment). Kept visually
# prominent -- a red-orange pill and a top-dashboard KPI, as the old [BLOQUEANTE]
# marker was -- but with a softer word (it is a requirement, not a blocker).
ESSENTIAL_RE = re.compile(r"\[\s*(?:IMPRESCINDIBLE|ESENCIAL)\s*\]", re.IGNORECASE)

MOSCOW = {
    "must": ("Must", "chip-must"),
    "should": ("Should", "chip-should"),
    "could": ("Could", "chip-could"),
    "won't": ("Won't", "chip-wont"),
    "wont": ("Won't", "chip-wont"),
}
PRIORITY = {
    "alta": ("Alta", "chip-prio-high"),
    "media": ("Media", "chip-prio-mid"),
    "baja": ("Baja", "chip-prio-low"),
    "critica": ("Critica", "chip-prio-high"),
}
EFFORT = {"xs": "chip-eff-xs", "s": "chip-eff-s", "m": "chip-eff-m",
          "l": "chip-eff-l", "xl": "chip-eff-xl"}

# Inline per-story metadata (e.g. "**Prioridad**: Alta   **Estimacion**: M"): turn
# the priority and effort *values* into pills so the human can scan them at a glance,
# and drop the estimation onto its own line when it trails other metadata. The label
# separator tolerates the closing </strong> left by bold conversion, colons and spaces.
PRIO_INLINE_RE = re.compile(
    r"(Prioridad(?:\s|:|</strong>){0,6})(Alta|Media|Baja|Cr[íi]tica)\b", re.IGNORECASE)
EFFORT_INLINE_RE = re.compile(
    r"(Estimaci[oó]n(?:\s|:|</strong>){0,6})(XS|XL|S|M|L)\b")
ESTIM_BREAK_RE = re.compile(r"(\S)[ \t]+(?=(?:<strong>)?Estimaci[oó]n\b)")

# Color codes (style guides / design tokens): show a swatch next to the code so the
# human sees the actual color beside its value. Matches #hex (3/4/6/8) and rgb()/hsl().
HEX_COLOR_RE = re.compile(
    r'(?<![\w"=#])(#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{4}|[0-9a-fA-F]{3}))\b')
COLOR_FUNC_RE = re.compile(
    r'(?<![\w"=(])((?:rgba?|hsla?)\([0-9,.%\s/]*\))', re.IGNORECASE)


def decorate_chips(escaped: str) -> str:
    """Wrap traceable IDs and markers in styled chips (input already escaped)."""
    escaped = RF_ID_RE.sub(r'<span class="chip chip-rf">\1</span>', escaped)
    escaped = NFR_ID_RE.sub(r'<span class="chip chip-nfr">\1</span>', escaped)
    escaped = US_ID_RE.sub(r'<span class="chip chip-us">\1</span>', escaped)
    escaped = BLOCKING_RE.sub('<span class="chip chip-block">BLOQUEANTE</span>', escaped)
    escaped = ESSENTIAL_RE.sub('<span class="chip chip-essential">IMPRESCINDIBLE</span>', escaped)
    return escaped


def decorate_meta(escaped: str) -> str:
    """Priority & effort values as pills; estimation on its own line. Input escaped."""
    escaped = ESTIM_BREAK_RE.sub(r"\1<br>", escaped)

    def _prio(m):
        label, cls = PRIORITY[m.group(2).lower().replace("í", "i")]
        return f'{m.group(1)}<span class="chip {cls}">{label}</span>'

    def _eff(m):
        return f'{m.group(1)}<span class="chip {EFFORT[m.group(2).lower()]}">{m.group(2).upper()}</span>'

    escaped = PRIO_INLINE_RE.sub(_prio, escaped)
    escaped = EFFORT_INLINE_RE.sub(_eff, escaped)
    return escaped


def _swatch(value: str) -> str:
    return f'<span class="swatch" style="background:{value}"></span>{value}'


def decorate_colors(escaped: str) -> str:
    """Prepend a color swatch to hex/rgb/hsl color codes (input already escaped)."""
    escaped = HEX_COLOR_RE.sub(lambda m: _swatch(m.group(1)), escaped)
    escaped = COLOR_FUNC_RE.sub(lambda m: _swatch(m.group(1)), escaped)
    return escaped


def inline_markdown(text: str, chips: bool = True, meta: bool = True) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(
        r"\[([^\]]+)\]\((https?:[^\s)]+|mailto:[^\s)]+|#[^\s)]+|\.{0,2}/[^\s)]+)\)",
        r'<a href="\2">\1</a>',
        escaped,
    )
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"(?<!\*)\*(?!\s)([^*\n]+?)(?<!\s)\*(?!\*)", r"<em>\1</em>", escaped)
    if chips:
        escaped = decorate_chips(escaped)
        escaped = decorate_colors(escaped)
        if meta:
            escaped = decorate_meta(escaped)
    return escaped


def cell_html(cell: str, header: bool) -> str:
    """Render a table cell, turning standalone priority/MoSCoW/effort tokens into chips."""
    rendered = inline_markdown(cell, meta=False)
    if header:
        return rendered
    token = cell.strip().lower().strip(".")
    if token in MOSCOW:
        label, cls = MOSCOW[token]
        return f'<span class="chip {cls}">{label}</span>'
    if token in PRIORITY:
        label, cls = PRIORITY[token]
        return f'<span class="chip {cls}">{label}</span>'
    if token in EFFORT:
        return f'<span class="chip {EFFORT[token]}">{cell.strip().upper()}</span>'
    return rendered


# --- KPI dashboard ----------------------------------------------------------

def build_kpis(markdown: str, doc_type: str) -> list[dict]:
    """Compute a small set of headline metrics from the raw Markdown."""
    kpis: list[dict] = []

    rf = sorted(set(RF_ID_RE.findall(markdown)))
    nfr = sorted(set(NFR_ID_RE.findall(markdown)))
    us = sorted(set(US_ID_RE.findall(markdown)))
    blockers = len(BLOCKING_RE.findall(markdown))

    if rf:
        kpis.append({"value": len(rf), "label": "Requisitos funcionales", "tone": "rf"})
    if nfr:
        kpis.append({"value": len(nfr), "label": "No funcionales", "tone": "nfr"})
    if us:
        kpis.append({"value": len(us), "label": "Historias de usuario", "tone": "us"})

    moscow = Counter()
    for key, (label, _) in MOSCOW.items():
        n = len(re.findall(rf"\b{re.escape(key)}\b", markdown, re.IGNORECASE))
        if n:
            moscow[label] += n
    if moscow.get("Must"):
        kpis.append({"value": moscow["Must"], "label": "Must have", "tone": "must"})

    low = markdown.lower()
    if "fuera de esta fase" in low or "fuera de alcance" in low:
        # Best-effort: count bullet lines within scope-out region.
        kpis.append({"value": _scope_out_count(markdown), "label": "Fuera de alcance", "tone": "muted"})

    essentials = len(ESSENTIAL_RE.findall(markdown))
    if essentials:
        kpis.append({"value": essentials, "label": "Imprescindibles", "tone": "essential"})

    if blockers:
        kpis.append({"value": blockers, "label": "Bloqueantes", "tone": "block"})

    open_q = len(re.findall(r"^\s*[-*]\s+", _section_body(markdown, "pregunt"), re.MULTILINE))
    if open_q:
        kpis.append({"value": open_q, "label": "Preguntas abiertas", "tone": "warn"})

    return kpis


def _section_body(markdown: str, needle: str) -> str:
    lines = markdown.splitlines()
    out: list[str] = []
    capture = False
    for line in lines:
        h = re.match(r"^(#{1,4})\s+(.+)$", line.strip())
        if h:
            capture = needle.lower() in h.group(2).lower()
            continue
        if capture:
            out.append(line)
    return "\n".join(out)


def _scope_out_count(markdown: str) -> int:
    """Count bullets under a "fuera de esta fase / fuera de alcance" marker.

    The marker may be a heading or a bold lead-in (e.g. ``**Fuera de esta fase:**``);
    count consecutive bullet lines after it, skipping blank lines.
    """
    lines = markdown.splitlines()
    marker = re.compile(r"fuera de (esta fase|alcance)", re.IGNORECASE)
    for idx, line in enumerate(lines):
        if marker.search(line):
            count = 0
            for follow in lines[idx + 1:]:
                s = follow.strip()
                if not s:
                    continue
                if re.match(r"^[-*]\s+", s):
                    count += 1
                    continue
                break
            if count:
                return count
    return 0


def build_kpi_html(kpis: list[dict]) -> str:
    if not kpis:
        return ""
    cards = "".join(
        f'<div class="kpi kpi-{k["tone"]}">'
        f'<span class="kpi-value">{html.escape(str(k["value"]))}</span>'
        f'<span class="kpi-label">{html.escape(k["label"])}</span>'
        "</div>"
        for k in kpis
    )
    return f'<div class="kpi-grid">{cards}</div>'


# --- Markdown to HTML -------------------------------------------------------

def slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return slug or "section"


SCOPE_SECTION_RE = re.compile(r"alcance", re.IGNORECASE)


def render_table(lines: list[str]) -> str:
    rows = []
    for line in lines:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        rows.append(cells)
    if not rows:
        return ""
    head = "".join(f"<th>{cell_html(cell, True)}</th>" for cell in rows[0])
    body_rows = []
    for row in rows[1:]:
        body_rows.append(
            "<tr>" + "".join(f"<td>{cell_html(cell, False)}</td>" for cell in row) + "</tr>"
        )
    return (
        '<div class="table-wrap"><table><thead><tr>'
        + head
        + "</tr></thead><tbody>"
        + "".join(body_rows)
        + "</tbody></table></div>"
    )


def markdown_to_html(markdown: str) -> tuple[str, list[dict]]:
    output: list[str] = []
    toc: list[dict] = []
    lines = markdown.splitlines()
    i = 0
    in_ul = False
    in_ol = False
    section_open = False

    def close_lists() -> None:
        nonlocal in_ul, in_ol
        if in_ul:
            output.append("</ul>")
            in_ul = False
        if in_ol:
            output.append("</ol>")
            in_ol = False

    def close_section() -> None:
        nonlocal section_open
        if section_open:
            output.append("</section>")
            section_open = False

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("```mermaid"):
            close_lists()
            i += 1
            code_lines = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            output.append(
                '<figure class="diagram"><pre class="mermaid">'
                + html.escape("\n".join(code_lines))
                + "</pre></figure>"
            )
            i += 1
            continue

        if stripped.startswith("```"):
            close_lists()
            i += 1
            code_lines = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            output.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
            i += 1
            continue

        if stripped.startswith(">"):
            close_lists()
            quote_lines = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote_lines.append(lines[i].strip().lstrip(">").strip())
                i += 1
            output.append(
                '<blockquote>'
                + "<br>".join(inline_markdown(q) for q in quote_lines)
                + "</blockquote>"
            )
            continue

        if stripped.startswith("|") and stripped.endswith("|"):
            close_lists()
            table_lines = []
            while (
                i < len(lines)
                and lines[i].strip().startswith("|")
                and lines[i].strip().endswith("|")
            ):
                table_lines.append(lines[i])
                i += 1
            output.append(render_table(table_lines))
            continue

        heading = re.match(r"^(#{1,4})\s+(.+)$", stripped)
        if heading:
            close_lists()
            level = len(heading.group(1))
            title = heading.group(2).strip()
            slug = slugify(title)
            if level == 1:
                close_section()
                output.append(
                    f'<header class="doc-header"><h1 id="{slug}">{inline_markdown(title, chips=False)}</h1></header>'
                )
            elif level == 2:
                close_section()
                is_scope = bool(SCOPE_SECTION_RE.search(title))
                cls = "doc-section" + (" section-scope" if is_scope else "")
                output.append(f'<section class="{cls}" id="{slug}">')
                output.append(
                    f'<h2><a class="anchor" href="#{slug}" aria-label="Enlace">#</a>'
                    f"{inline_markdown(title, chips=False)}</h2>"
                )
                section_open = True
                toc.append({"slug": slug, "title": title})
            else:
                output.append(f'<h{level} id="{slug}">{inline_markdown(title, chips=False)}</h{level}>')
            i += 1
            continue

        ol_match = re.match(r"^(\d+)\.\s+(.+)$", stripped)
        if ol_match:
            if in_ul:
                output.append("</ul>")
                in_ul = False
            if not in_ol:
                output.append("<ol>")
                in_ol = True
            output.append(f"<li>{inline_markdown(ol_match.group(2).strip())}</li>")
            i += 1
            continue

        if stripped.startswith("- ") or stripped.startswith("* "):
            if in_ol:
                output.append("</ol>")
                in_ol = False
            if not in_ul:
                output.append("<ul>")
                in_ul = True
            output.append(f"<li>{inline_markdown(stripped[2:].strip())}</li>")
            i += 1
            continue

        if not stripped:
            close_lists()
            i += 1
            continue

        close_lists()
        output.append(f"<p>{inline_markdown(stripped)}</p>")
        i += 1

    close_lists()
    close_section()
    return "\n".join(output), toc


def build_toc(toc: list[dict]) -> str:
    if not toc:
        return ""
    items = "".join(
        f'<li><a href="#{entry["slug"]}">{html.escape(entry["title"])}</a></li>'
        for entry in toc
    )
    return (
        '<nav class="toc" aria-label="Indice">'
        '<p class="toc-title">En esta pagina</p>'
        f"<ol>{items}</ol></nav>"
    )


def build_html(title: str, doc_type: str, markdown: str) -> str:
    body, toc = markdown_to_html(markdown)
    toc_html = build_toc(toc)
    kpi_html = build_kpi_html(build_kpis(markdown, doc_type))
    meta = DOC_TYPES.get(doc_type, {"label": "Documento AIDD", "phase": ""})
    generated = date.today().isoformat()
    subtitle = (
        f'<p class="doc-meta"><span class="badge">{html.escape(meta["label"])}</span> '
        + (f'<span class="badge badge-soft">{html.escape(meta["phase"])}</span> ' if meta["phase"] else "")
        + f'<span class="dot">&middot;</span> Vista generada el {generated} '
        '<span class="dot">&middot;</span> <span class="sot">El .md es la fuente de verdad</span></p>'
    )
    if "</h1></header>" in body:
        body = body.replace("</h1></header>", f"</h1>{subtitle}{kpi_html}</header>", 1)
    else:
        body = (
            f'<header class="doc-header"><h1>{html.escape(title)}</h1>{subtitle}{kpi_html}</header>'
            + body
        )

    document = f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{
      color-scheme: light dark;
      --bg: #f5f7fa; --panel: #ffffff; --panel-soft: #fbfcfd;
      --text: #1a2230; --text-soft: #404a5c; --muted: #5b6675;
      --line: #e1e6ed; --line-strong: #c8d1dc;
      --accent: #005f73; --accent-soft: #d6eef3;
      --code-bg: #eef2f6;
      --shadow: 0 1px 2px rgba(15,23,42,.04), 0 1px 3px rgba(15,23,42,.06);
      --rf: #0a7d8c; --nfr: #6b5bd6; --us: #0a9396; --must: #c1121f;
      --block: #b00020; --warn: #b58a25; --essential: #e8590c;
      --prio-high: #c1121f; --prio-mid: #d98a00; --prio-low: #4a8a4a;
      --eff-xs: #2f8f6b; --eff-s: #4a8a4a; --eff-m: #d98a00; --eff-l: #c1121f; --eff-xl: #7a0a15;
    }}
    @media (prefers-color-scheme: dark) {{
      :root {{
        --bg: #0f1623; --panel: #161f2f; --panel-soft: #1b2536;
        --text: #e6ebf4; --text-soft: #c2cad8; --muted: #94a0b3;
        --line: #28324a; --line-strong: #364260;
        --accent: #4dd0e1; --accent-soft: #143038; --code-bg: #1f2940;
        --shadow: 0 1px 2px rgba(0,0,0,.35), 0 1px 3px rgba(0,0,0,.25);
        --rf: #35c4d6; --nfr: #a99bff; --us: #4dd0e1; --must: #ff6b74;
        --block: #ff7a8a; --warn: #f6d784; --essential: #ff8f4d;
        --prio-high: #ff6b74; --prio-mid: #ffb340; --prio-low: #7fd07f;
        --eff-xs: #5fd0a8; --eff-s: #7fd07f; --eff-m: #ffb340; --eff-l: #ff6b74; --eff-xl: #ff9aa2;
      }}
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0; background: var(--bg); color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", Roboto, "Helvetica Neue", Arial, sans-serif;
      font-size: 16px; line-height: 1.65; -webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility;
    }}
    .layout {{
      display: grid; grid-template-columns: 260px minmax(0, 1fr); gap: 40px;
      max-width: 1280px; margin: 0 auto; padding: 40px 28px 80px;
    }}
    @media (max-width: 960px) {{
      .layout {{ grid-template-columns: 1fr; padding: 24px 18px 56px; gap: 24px; }}
      .toc {{ position: static !important; max-height: none !important; }}
    }}
    main {{ min-width: 0; }}
    .doc-header {{ margin-bottom: 24px; padding-bottom: 18px; border-bottom: 1px solid var(--line); }}
    h1 {{ font-size: 2rem; line-height: 1.2; margin: 0 0 10px; letter-spacing: -0.01em; }}
    h2 {{ font-size: 1.35rem; line-height: 1.3; margin: 0 0 14px; display: flex; align-items: baseline; gap: 8px; }}
    h3 {{ font-size: 1.08rem; margin: 22px 0 10px; }}
    h4 {{ font-size: .98rem; margin: 18px 0 8px; color: var(--text-soft); text-transform: uppercase; letter-spacing: .04em; }}
    h2 .anchor {{ color: var(--line-strong); text-decoration: none; font-weight: 400; opacity: 0; transition: opacity .15s ease, color .15s ease; }}
    h2:hover .anchor {{ opacity: 1; }}
    h2 .anchor:hover {{ color: var(--accent); }}
    p {{ margin: 0 0 14px; color: var(--text-soft); max-width: 74ch; }}
    li {{ color: var(--text-soft); }}
    ul, ol {{ padding-left: 24px; margin: 0 0 16px; }}
    ul li, ol li {{ margin-bottom: 6px; }}
    a {{ color: var(--accent); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    strong {{ color: var(--text); }}
    blockquote {{
      margin: 0 0 16px; padding: 12px 16px; border-left: 3px solid var(--accent);
      background: var(--panel-soft); border-radius: 0 8px 8px 0; color: var(--muted); font-size: .95rem;
    }}
    code {{ background: var(--code-bg); border: 1px solid var(--line); border-radius: 4px; padding: 1px 6px;
      font-family: "SF Mono","JetBrains Mono","Fira Code",Consolas,Menlo,monospace; font-size: .88em; }}
    pre {{ background: var(--panel-soft); border: 1px solid var(--line); border-radius: 8px; padding: 16px 18px;
      overflow-x: auto; font-family: "SF Mono","JetBrains Mono","Fira Code",Consolas,Menlo,monospace; font-size: .88em; line-height: 1.55; }}
    pre code {{ background: transparent; border: 0; padding: 0; }}
    .badge {{ display: inline-block; background: var(--accent-soft); color: var(--accent);
      font-size: .72rem; font-weight: 600; text-transform: uppercase; letter-spacing: .06em;
      padding: 2px 8px; border-radius: 999px; vertical-align: middle; }}
    .badge-soft {{ background: transparent; border: 1px solid var(--line-strong); color: var(--muted); }}
    .doc-meta {{ margin: 0; color: var(--muted); font-size: .92rem; }}
    .doc-meta .dot {{ margin: 0 6px; color: var(--line-strong); }}
    .doc-meta .sot {{ font-style: italic; }}
    /* KPI dashboard */
    .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 14px; margin-top: 20px; }}
    .kpi {{ background: var(--panel); border: 1px solid var(--line); border-left: 4px solid var(--accent);
      border-radius: 10px; padding: 14px 16px; box-shadow: var(--shadow); display: flex; flex-direction: column; gap: 2px; }}
    .kpi-value {{ font-size: 1.9rem; font-weight: 700; line-height: 1; letter-spacing: -.02em; color: var(--text); font-variant-numeric: tabular-nums; }}
    .kpi-label {{ font-size: .78rem; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; }}
    .kpi-rf {{ border-left-color: var(--rf); }} .kpi-rf .kpi-value {{ color: var(--rf); }}
    .kpi-nfr {{ border-left-color: var(--nfr); }} .kpi-nfr .kpi-value {{ color: var(--nfr); }}
    .kpi-us {{ border-left-color: var(--us); }} .kpi-us .kpi-value {{ color: var(--us); }}
    .kpi-must {{ border-left-color: var(--must); }} .kpi-must .kpi-value {{ color: var(--must); }}
    .kpi-block {{ border-left-color: var(--block); }} .kpi-block .kpi-value {{ color: var(--block); }}
    .kpi-essential {{ border-left-color: var(--essential); }} .kpi-essential .kpi-value {{ color: var(--essential); }}
    .kpi-warn {{ border-left-color: var(--warn); }} .kpi-warn .kpi-value {{ color: var(--warn); }}
    .kpi-muted {{ border-left-color: var(--line-strong); }} .kpi-muted .kpi-value {{ color: var(--muted); }}
    /* Chips */
    .chip {{ display: inline-block; font-size: .74rem; font-weight: 600; padding: 1px 8px; border-radius: 999px;
      vertical-align: baseline; letter-spacing: .02em; white-space: nowrap;
      border: 1px solid color-mix(in srgb, currentColor 35%, transparent); }}
    .chip-rf {{ color: var(--rf); background: color-mix(in srgb, var(--rf) 12%, transparent); font-family: "SF Mono",Menlo,monospace; }}
    .chip-nfr {{ color: var(--nfr); background: color-mix(in srgb, var(--nfr) 12%, transparent); font-family: "SF Mono",Menlo,monospace; }}
    .chip-us {{ color: var(--us); background: color-mix(in srgb, var(--us) 12%, transparent); font-family: "SF Mono",Menlo,monospace; }}
    .chip-block {{ color: #fff; background: var(--block); border-color: var(--block); text-transform: uppercase; letter-spacing: .05em; }}
    .chip-essential {{ color: #fff; background: var(--essential); border-color: var(--essential); text-transform: uppercase; letter-spacing: .05em; }}
    .swatch {{ display: inline-block; width: .9em; height: .9em; border-radius: 3px; margin-right: .35em;
      vertical-align: -.12em; border: 1px solid color-mix(in srgb, var(--text) 30%, transparent);
      box-shadow: 0 0 0 1px rgba(255,255,255,.35) inset; }}
    .chip-must {{ color: var(--must); background: color-mix(in srgb, var(--must) 14%, transparent); }}
    .chip-should {{ color: var(--prio-mid); background: color-mix(in srgb, var(--prio-mid) 14%, transparent); }}
    .chip-could {{ color: var(--prio-low); background: color-mix(in srgb, var(--prio-low) 14%, transparent); }}
    .chip-wont {{ color: var(--muted); background: color-mix(in srgb, var(--muted) 14%, transparent); }}
    .chip-prio-high {{ color: var(--prio-high); background: color-mix(in srgb, var(--prio-high) 14%, transparent); }}
    .chip-prio-mid {{ color: var(--prio-mid); background: color-mix(in srgb, var(--prio-mid) 14%, transparent); }}
    .chip-prio-low {{ color: var(--prio-low); background: color-mix(in srgb, var(--prio-low) 14%, transparent); }}
    .chip-eff-xs {{ color: var(--eff-xs); background: color-mix(in srgb, var(--eff-xs) 14%, transparent); }}
    .chip-eff-s {{ color: var(--eff-s); background: color-mix(in srgb, var(--eff-s) 14%, transparent); }}
    .chip-eff-m {{ color: var(--eff-m); background: color-mix(in srgb, var(--eff-m) 14%, transparent); }}
    .chip-eff-l {{ color: var(--eff-l); background: color-mix(in srgb, var(--eff-l) 14%, transparent); }}
    .chip-eff-xl {{ color: var(--eff-xl); background: color-mix(in srgb, var(--eff-xl) 14%, transparent); }}
    /* Sections */
    .doc-section {{ background: var(--panel); border: 1px solid var(--line); border-radius: 12px;
      padding: 24px 26px; margin: 22px 0; box-shadow: var(--shadow); }}
    .doc-section h2 {{ margin-top: 0; }}
    .doc-section > h2::before {{ content: ""; display: inline-block; width: 6px; height: 22px; border-radius: 3px;
      background: var(--accent); transform: translateY(3px); margin-right: 2px; }}
    .section-scope > h2::before {{ background: var(--must); }}
    .section-scope ul {{ list-style: none; padding-left: 0; }}
    .section-scope ul li {{ padding: 6px 12px; margin-bottom: 6px; border-radius: 8px; background: var(--panel-soft); border: 1px solid var(--line); }}
    .table-wrap {{ overflow-x: auto; border: 1px solid var(--line); border-radius: 10px; margin: 14px 0; }}
    table {{ width: 100%; border-collapse: collapse; background: var(--panel); font-size: .94rem; }}
    th, td {{ padding: 10px 14px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; color: var(--text-soft); }}
    tbody tr:last-child td {{ border-bottom: 0; }}
    tbody tr:nth-child(even) td {{ background: var(--panel-soft); }}
    th {{ background: var(--panel-soft); color: var(--text); font-weight: 600; font-size: .82rem;
      text-transform: uppercase; letter-spacing: .05em; border-bottom: 1px solid var(--line-strong); }}
    .diagram {{ margin: 18px 0 4px; padding: 18px; background: var(--panel-soft);
      border: 1px dashed var(--line-strong); border-radius: 10px; overflow-x: auto; }}
    .diagram .mermaid {{ text-align: center; background: transparent; border: 0; padding: 0; margin: 0; }}
    .toc {{ position: sticky; top: 24px; align-self: start; max-height: calc(100vh - 48px); overflow-y: auto;
      padding: 18px 18px 14px; background: var(--panel); border: 1px solid var(--line); border-radius: 12px;
      box-shadow: var(--shadow); font-size: .9rem; }}
    .toc-title {{ margin: 0 0 10px; font-size: .74rem; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); }}
    .toc ol {{ list-style: none; counter-reset: toc; padding: 0; margin: 0; }}
    .toc li {{ counter-increment: toc; margin: 0; }}
    .toc li a {{ display: block; padding: 6px 10px 6px 12px; color: var(--text-soft); border-radius: 6px; }}
    .toc li a::before {{ content: counter(toc) "."; color: var(--muted); margin-right: 8px; font-variant-numeric: tabular-nums; }}
    .toc li a:hover, .toc li a.active {{ background: var(--accent-soft); color: var(--accent); text-decoration: none; }}
    @media print {{
      body {{ background: #fff; }} .layout {{ display: block; padding: 0; }} .toc {{ display: none; }}
      .doc-section, .kpi {{ box-shadow: none; break-inside: avoid; }}
    }}
  </style>
</head>
<body>
  <div class="layout">
    {toc_html}
    <main>
{body}
    </main>
  </div>
  <script type="module">
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
    const dark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    mermaid.initialize({{ startOnLoad: true, securityLevel: 'strict', theme: dark ? 'dark' : 'default' }});

    // Scroll-spy: highlight the current section in the TOC.
    const links = [...document.querySelectorAll('.toc a')];
    const map = new Map(links.map(a => [a.getAttribute('href').slice(1), a]));
    const obs = new IntersectionObserver(entries => {{
      entries.forEach(e => {{
        if (e.isIntersecting) {{
          links.forEach(a => a.classList.remove('active'));
          const a = map.get(e.target.id);
          if (a) a.classList.add('active');
        }}
      }});
    }}, {{ rootMargin: '-10% 0px -80% 0px' }});
    document.querySelectorAll('section[id]').forEach(s => obs.observe(s));
  </script>
</body>
</html>
"""
    return document


def extract_title(markdown: str, fallback: str) -> str:
    for line in markdown.splitlines():
        m = re.match(r"^#\s+(.+)$", line.strip())
        if m:
            return m.group(1).strip()
    return fallback


def main() -> int:
    configure_text_streams()
    parser = argparse.ArgumentParser(description="Render an AIDD planning Markdown document to visual HTML.")
    parser.add_argument("--input", help="Markdown input path. Reads stdin when omitted.")
    parser.add_argument("--output", required=True, help="HTML output path.")
    parser.add_argument("--doc-type", help="Force a doc type; otherwise auto-detected from filename/H1.")
    parser.add_argument("--title", help="Override the document title.")
    parser.add_argument(
        "--open",
        dest="open_browser",
        action="store_true",
        help="Open the generated HTML in the default browser (best-effort; no-op in headless environments).",
    )
    args = parser.parse_args()
    reads_stdin = not args.input

    try:
        if args.input:
            markdown = Path(args.input).read_text(encoding="utf-8-sig")
        else:
            markdown = read_stdin_utf8()
    except UnicodeDecodeError as exc:
        print("ERROR: La entrada no esta codificada como UTF-8.", file=sys.stderr)
        print(f"Detalle: {exc}", file=sys.stderr)
        return 3

    if not markdown.strip():
        print("No se recibio contenido Markdown.", file=sys.stderr)
        return 2

    if reads_stdin and LOSSY_STDIN_RE.search(markdown):
        print("ERROR: La entrada por stdin parece haber perdido caracteres. Usa --input con UTF-8.", file=sys.stderr)
        return 6

    markdown, repaired_count = repair_common_mojibake(markdown)
    if mojibake_score(markdown):
        print("ERROR: La entrada contiene mojibake no reparable automaticamente.", file=sys.stderr)
        return 4

    stem = Path(args.input).stem if args.input else "generic"
    doc_type = args.doc_type or detect_doc_type(stem)
    title = args.title or extract_title(markdown, DOC_TYPES.get(doc_type, {}).get("label", "Documento AIDD"))

    document = build_html(title, doc_type, markdown)
    if mojibake_score(document):
        print("ERROR: El HTML generado contiene mojibake.", file=sys.stderr)
        return 5

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(document, encoding="utf-8")

    if repaired_count:
        print(f"ADVERTENCIA: Se repararon {repaired_count} fragmentos con mojibake comun.", file=sys.stderr)

    if args.open_browser:
        try:
            opened = webbrowser.open(output.resolve().as_uri())
        except Exception:  # noqa: BLE001 - best-effort, never fail the render for this
            opened = False
        if not opened:
            print(
                "ADVERTENCIA: No se pudo abrir el navegador automaticamente "
                f"(entorno sin GUI?). Abre el HTML manualmente: {output}",
                file=sys.stderr,
            )

    print(str(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
