#!/usr/bin/env python3
"""Render a Markdown UML report with Mermaid blocks into a standalone HTML file."""

from __future__ import annotations

import argparse
import html
import re
import sys
from datetime import date
from pathlib import Path


MERMAID_DANGEROUS = re.compile(r"(?<!-)[<>&]|<<\s*(include|extend)\s*>>", re.IGNORECASE)
MOJIBAKE_RE = re.compile(
    r"(?:"
    r"\u00c3[\u0080-\u00bf]"
    r"|\u00c2[\u0080-\u00bf]"
    r"|\u00e2[\u20ac\u201a-\u201e\u2020-\u2026\u2030\u0160\u2039\u0152\u017d"
    r"\u2018-\u201d\u2022\u2013-\u2014\u02dc\u2122\u0161\u203a\u0153\u017e\u0178]"
    r"|\ufffd"
    r")"
)
MOJIBAKE_TOKEN_RE = re.compile(r"\S*(?:" + MOJIBAKE_RE.pattern + r")\S*")
LOSSY_STDIN_RE = re.compile(r"[A-Za-z]\?[A-Za-z]")

CALLOUT_KEYWORDS = {
    "supuestos": "callout-assumptions",
    "huecos": "callout-assumptions",
    "supuestos y huecos": "callout-assumptions",
    "trazabilidad": "section-traceability",
}


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return slug or "section"


def configure_text_streams() -> None:
    """Prefer UTF-8 for CLI diagnostics on Windows and POSIX."""

    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name)
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def read_stdin_utf8() -> str:
    """Read stdin as bytes to avoid platform-default text decoding mojibake."""

    buffer = getattr(sys.stdin, "buffer", None)
    if buffer is None:
        data = sys.stdin.read()
        if isinstance(data, str):
            return data
        return data.decode("utf-8-sig")

    raw = buffer.read()
    return raw.decode("utf-8-sig")


def mojibake_score(text: str) -> int:
    return len(MOJIBAKE_RE.findall(text))


def repair_common_mojibake(text: str) -> tuple[str, int]:
    """Repair common UTF-8 text that was decoded as Windows-1252/Latin-1."""

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


def inline_markdown(text: str) -> str:
    escaped = html.escape(text)
    # Inline code: `code`
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    # Links: [text](url) - url must be http(s), relative, anchor or mailto
    escaped = re.sub(
        r"\[([^\]]+)\]\((https?:[^\s)]+|mailto:[^\s)]+|#[^\s)]+|\.{0,2}/[^\s)]+)\)",
        r'<a href="\2">\1</a>',
        escaped,
    )
    # Bold: **text**
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    # Italic: *text* (avoid matching inside **)
    escaped = re.sub(r"(?<!\*)\*(?!\s)([^*\n]+?)(?<!\s)\*(?!\*)", r"<em>\1</em>", escaped)
    return escaped


def render_table(lines: list[str]) -> str:
    rows = []
    for line in lines:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        rows.append(cells)
    if not rows:
        return ""

    head = "".join(f"<th>{inline_markdown(cell)}</th>" for cell in rows[0])
    body_rows = []
    for row in rows[1:]:
        body_rows.append(
            "<tr>" + "".join(f"<td>{inline_markdown(cell)}</td>" for cell in row) + "</tr>"
        )
    return (
        '<div class="table-wrap"><table><thead><tr>'
        + head
        + "</tr></thead><tbody>"
        + "".join(body_rows)
        + "</tbody></table></div>"
    )


def section_class_for(title: str) -> str:
    key = title.strip().lower()
    for needle, cls in CALLOUT_KEYWORDS.items():
        if needle in key:
            return cls
    if key.startswith("casos de uso"):
        return "section-usecase"
    if key.startswith("actividad"):
        return "section-activity"
    if key.startswith("secuencia"):
        return "section-sequence"
    if key.startswith("estado"):
        return "section-state"
    return "section-generic"


def markdown_to_html(markdown: str) -> tuple[str, list[str], list[dict]]:
    output: list[str] = []
    warnings: list[str] = []
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
            code = "\n".join(code_lines)
            if MERMAID_DANGEROUS.search(code):
                warnings.append(
                    "Un bloque Mermaid contiene caracteres o etiquetas potencialmente incompatibles."
                )
            output.append(
                '<figure class="diagram"><pre class="mermaid">'
                + html.escape(code)
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
            output.append(
                "<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>"
            )
            i += 1
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
                    f'<header class="doc-header"><h1 id="{slug}">'
                    f"{inline_markdown(title)}</h1></header>"
                )
            elif level == 2:
                close_section()
                cls = section_class_for(title)
                output.append(f'<section class="doc-section {cls}" id="{slug}">')
                output.append(
                    f'<h2><a class="anchor" href="#{slug}" aria-label="Enlace">#</a>'
                    f"{inline_markdown(title)}</h2>"
                )
                section_open = True
                toc.append({"slug": slug, "title": title})
            else:
                output.append(
                    f'<h{level} id="{slug}">{inline_markdown(title)}</h{level}>'
                )
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

        if stripped.startswith("- "):
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
    return "\n".join(output), warnings, toc


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


def build_html(change_id: str, markdown: str) -> tuple[str, list[str]]:
    body, warnings, toc = markdown_to_html(markdown)
    toc_html = build_toc(toc)
    title = f"Diagramas UML - {change_id}"
    generated = date.today().isoformat()
    subtitle = (
        f'<p class="doc-meta">'
        f'<span class="badge">Change</span> <code>{html.escape(change_id)}</code> '
        f'<span class="dot">&middot;</span> Generado el {generated}'
        "</p>"
    )
    # Inject metadata inside the document header, just after the <h1>.
    if "</h1></header>" in body:
        body = body.replace("</h1></header>", f"</h1>{subtitle}</header>", 1)
    else:
        body = (
            f'<header class="doc-header"><h1>{html.escape(title)}</h1>{subtitle}</header>'
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
      --bg: #f5f7fa;
      --panel: #ffffff;
      --panel-soft: #fbfcfd;
      --text: #1a2230;
      --text-soft: #404a5c;
      --muted: #5b6675;
      --line: #e1e6ed;
      --line-strong: #c8d1dc;
      --accent: #005f73;
      --accent-soft: #d6eef3;
      --warn-bg: #fff7e6;
      --warn-border: #f3c969;
      --warn-text: #6b4a00;
      --code-bg: #eef2f6;
      --shadow: 0 1px 2px rgba(15, 23, 42, .04), 0 1px 3px rgba(15, 23, 42, .06);
    }}
    @media (prefers-color-scheme: dark) {{
      :root {{
        --bg: #0f1623;
        --panel: #161f2f;
        --panel-soft: #1b2536;
        --text: #e6ebf4;
        --text-soft: #c2cad8;
        --muted: #94a0b3;
        --line: #28324a;
        --line-strong: #364260;
        --accent: #4dd0e1;
        --accent-soft: #143038;
        --warn-bg: #3a2e0d;
        --warn-border: #b58a25;
        --warn-text: #f6d784;
        --code-bg: #1f2940;
        --shadow: 0 1px 2px rgba(0, 0, 0, .35), 0 1px 3px rgba(0, 0, 0, .25);
      }}
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", Roboto, "Helvetica Neue", Arial, sans-serif;
      font-size: 16px;
      line-height: 1.65;
      -webkit-font-smoothing: antialiased;
      text-rendering: optimizeLegibility;
    }}
    .layout {{
      display: grid;
      grid-template-columns: 260px minmax(0, 1fr);
      gap: 40px;
      max-width: 1280px;
      margin: 0 auto;
      padding: 40px 28px 80px;
    }}
    @media (max-width: 960px) {{
      .layout {{ grid-template-columns: 1fr; padding: 24px 18px 56px; gap: 24px; }}
      .toc {{ position: static !important; max-height: none !important; }}
    }}
    main {{ min-width: 0; }}
    .doc-header {{
      margin-bottom: 24px;
      padding-bottom: 18px;
      border-bottom: 1px solid var(--line);
    }}
    h1 {{
      font-size: 2rem;
      line-height: 1.2;
      margin: 0 0 8px;
      letter-spacing: -0.01em;
      color: var(--text);
    }}
    h2 {{
      font-size: 1.35rem;
      line-height: 1.3;
      margin: 0 0 14px;
      letter-spacing: -0.005em;
      color: var(--text);
      display: flex;
      align-items: baseline;
      gap: 8px;
    }}
    h3 {{
      font-size: 1.08rem;
      margin: 22px 0 10px;
      color: var(--text);
    }}
    h4 {{
      font-size: 0.98rem;
      margin: 18px 0 8px;
      color: var(--text-soft);
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
    h2 .anchor {{
      color: var(--line-strong);
      text-decoration: none;
      font-weight: 400;
      opacity: 0;
      transition: opacity .15s ease, color .15s ease;
    }}
    h2:hover .anchor {{ opacity: 1; }}
    h2 .anchor:hover {{ color: var(--accent); }}
    p {{
      margin: 0 0 14px;
      color: var(--text-soft);
      max-width: 72ch;
    }}
    li {{ color: var(--text-soft); }}
    ul, ol {{ padding-left: 24px; margin: 0 0 16px; }}
    ul li, ol li {{ margin-bottom: 6px; }}
    a {{ color: var(--accent); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    strong {{ color: var(--text); }}
    code {{
      background: var(--code-bg);
      border: 1px solid var(--line);
      border-radius: 4px;
      padding: 1px 6px;
      font-family: "SF Mono", "JetBrains Mono", "Fira Code", Consolas, "Liberation Mono", Menlo, monospace;
      font-size: 0.88em;
    }}
    pre {{
      background: var(--panel-soft);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px 18px;
      overflow-x: auto;
      font-family: "SF Mono", "JetBrains Mono", "Fira Code", Consolas, "Liberation Mono", Menlo, monospace;
      font-size: 0.88em;
      line-height: 1.55;
    }}
    pre code {{ background: transparent; border: 0; padding: 0; font-size: inherit; }}
    .doc-meta {{
      margin: 0;
      color: var(--muted);
      font-size: 0.92rem;
    }}
    .doc-meta code {{ font-size: 0.88em; }}
    .doc-meta .dot {{ margin: 0 4px; color: var(--line-strong); }}
    .badge {{
      display: inline-block;
      background: var(--accent-soft);
      color: var(--accent);
      font-size: 0.72rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      padding: 2px 8px;
      border-radius: 999px;
      vertical-align: middle;
    }}
    .doc-section {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 24px 26px;
      margin: 22px 0;
      box-shadow: var(--shadow);
    }}
    .doc-section h2 {{ margin-top: 0; }}
    .doc-section > h2::before {{
      content: "";
      display: inline-block;
      width: 6px;
      height: 22px;
      border-radius: 3px;
      background: var(--accent);
      transform: translateY(3px);
      margin-right: 2px;
    }}
    .section-usecase > h2::before {{ background: #0a9396; }}
    .section-activity > h2::before {{ background: #ee9b00; }}
    .section-sequence > h2::before {{ background: #9b5de5; }}
    .section-state > h2::before {{ background: #e76f51; }}
    .section-traceability > h2::before {{ background: #6b8e23; }}
    .callout-assumptions {{
      background: var(--warn-bg);
      border-color: var(--warn-border);
    }}
    .callout-assumptions h2,
    .callout-assumptions p,
    .callout-assumptions li {{ color: var(--warn-text); }}
    .callout-assumptions > h2::before {{ background: var(--warn-border); }}
    .callout-assumptions code {{ background: rgba(0,0,0,0.06); }}
    .diagram {{
      margin: 18px 0 4px;
      padding: 18px;
      background: var(--panel-soft);
      border: 1px dashed var(--line-strong);
      border-radius: 10px;
      overflow-x: auto;
    }}
    .diagram .mermaid {{
      text-align: center;
      background: transparent;
      border: 0;
      padding: 0;
      margin: 0;
    }}
    .table-wrap {{
      overflow-x: auto;
      border: 1px solid var(--line);
      border-radius: 10px;
      margin: 14px 0;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: var(--panel);
      font-size: 0.94rem;
    }}
    th, td {{
      padding: 10px 14px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
      color: var(--text-soft);
    }}
    tbody tr:last-child td {{ border-bottom: 0; }}
    tbody tr:nth-child(even) td {{ background: var(--panel-soft); }}
    th {{
      background: var(--panel-soft);
      color: var(--text);
      font-weight: 600;
      font-size: 0.82rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      border-bottom: 1px solid var(--line-strong);
    }}
    .toc {{
      position: sticky;
      top: 24px;
      align-self: start;
      max-height: calc(100vh - 48px);
      overflow-y: auto;
      padding: 18px 18px 14px;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 12px;
      box-shadow: var(--shadow);
      font-size: 0.9rem;
    }}
    .toc-title {{
      margin: 0 0 10px;
      font-size: 0.74rem;
      font-weight: 600;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--muted);
    }}
    .toc ol {{
      list-style: none;
      counter-reset: toc;
      padding: 0;
      margin: 0;
    }}
    .toc li {{
      counter-increment: toc;
      margin: 0;
      border-left: 2px solid transparent;
    }}
    .toc li a {{
      display: block;
      padding: 6px 10px 6px 12px;
      color: var(--text-soft);
      border-radius: 6px;
    }}
    .toc li a::before {{
      content: counter(toc) ".";
      color: var(--muted);
      margin-right: 8px;
      font-variant-numeric: tabular-nums;
    }}
    .toc li a:hover {{
      background: var(--accent-soft);
      color: var(--accent);
      text-decoration: none;
    }}
    @media print {{
      body {{ background: #fff; }}
      .layout {{ display: block; padding: 0; }}
      .toc {{ display: none; }}
      .doc-section {{ box-shadow: none; break-inside: avoid; }}
      .diagram {{ break-inside: avoid; }}
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
    mermaid.initialize({{
      startOnLoad: true,
      securityLevel: 'strict',
      theme: dark ? 'dark' : 'default'
    }});
  </script>
</body>
</html>
"""
    return document, warnings


def main() -> int:
    configure_text_streams()
    parser = argparse.ArgumentParser(description="Render OpenSpec UML Mermaid Markdown to HTML.")
    parser.add_argument("--change-id", required=True, help="OpenSpec change identifier.")
    parser.add_argument("--output", required=True, help="HTML output path.")
    parser.add_argument("--input", help="Optional Markdown input path. Reads stdin when omitted.")
    args = parser.parse_args()
    reads_stdin = not args.input

    try:
        if args.input:
            markdown = Path(args.input).read_text(encoding="utf-8-sig")
        else:
            markdown = read_stdin_utf8()
    except UnicodeDecodeError as exc:
        print(
            "ERROR: La entrada no esta codificada como UTF-8. "
            "Guarda el Markdown con UTF-8 o usa PowerShell con -Encoding utf8.",
            file=sys.stderr,
        )
        print(f"Detalle: {exc}", file=sys.stderr)
        return 3

    if not markdown.strip():
        print("No se recibio contenido Markdown.", file=sys.stderr)
        return 2

    if reads_stdin and LOSSY_STDIN_RE.search(markdown):
        print(
            "ERROR: La entrada por stdin contiene signos '?' dentro de palabras. "
            "Esto suele indicar perdida de caracteres por la codificacion de la shell. "
            "Guarda el Markdown como UTF-8 y usa --input.",
            file=sys.stderr,
        )
        return 6

    markdown, repaired_count = repair_common_mojibake(markdown)
    if mojibake_score(markdown):
        print(
            "ERROR: La entrada contiene secuencias compatibles con mojibake "
            "que no pudieron repararse automaticamente.",
            file=sys.stderr,
        )
        return 4

    document, warnings = build_html(args.change_id, markdown)
    if mojibake_score(document):
        print(
            "ERROR: El HTML generado contiene secuencias compatibles con mojibake.",
            file=sys.stderr,
        )
        return 5

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(document, encoding="utf-8")

    if repaired_count:
        print(
            f"ADVERTENCIA: Se repararon {repaired_count} fragmentos con mojibake comun.",
            file=sys.stderr,
        )
    for warning in warnings:
        print(f"ADVERTENCIA: {warning}", file=sys.stderr)
    print(str(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
