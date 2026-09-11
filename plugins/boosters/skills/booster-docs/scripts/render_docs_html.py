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
  * scope "dentro / fuera de esta fase" rendered as side-by-side cards;
  * a visual shape per document type, for the types in ``SHAPED_TYPES``: user
    stories as cards, sprints as boxes with their load, phases as a timeline. A
    section that does not have the expected shape renders as plain Markdown.

Doc-type is auto-detected from the H1 / filename but can be forced with
``--doc-type``. Unknown doc types still get a faithful render plus whatever KPIs
can be derived generically.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import os
import re
import sys
import tempfile
import unicodedata
import urllib.request
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


# --- Mermaid asset ----------------------------------------------------------

# The HTML loads the *self-contained* Mermaid bundle (``mermaid.min.js``: one
# request, no lazy chunks), preferring a copy next to the HTML over the CDN. That
# local copy is provisioned here, lazily: the bundle is downloaded once per
# machine into a user cache and copied into each output folder, instead of being
# vendored in the plugin (a 3,5 MB blob every clone of the marketplace would carry
# forever). Version and sha256 are pinned, so a lazy fetch is as deterministic as
# a vendored file, and the URL below is the same one the HTML falls back to.
MERMAID_VERSION = "11.16.0"
MERMAID_ASSET_NAME = "mermaid.min.js"
MERMAID_URL = f"https://cdn.jsdelivr.net/npm/mermaid@{MERMAID_VERSION}/dist/{MERMAID_ASSET_NAME}"
MERMAID_SHA256 = "74d7c46dabca328c2294733910a8aa1ed0c37451776e8d5295da38a2b758fb9b"
MERMAID_SIZE = 3565102
MERMAID_TIMEOUT = 20.0

MERMAID_BLOCK_RE = re.compile(r"^\s*```mermaid\b", re.MULTILINE)


def has_mermaid_blocks(markdown: str) -> bool:
    return bool(MERMAID_BLOCK_RE.search(markdown))


def _asset_is_valid(path: Path) -> bool:
    """True when *path* is exactly the pinned bundle (cheap size check, then hash)."""
    try:
        if path.stat().st_size != MERMAID_SIZE:
            return False
        return hashlib.sha256(path.read_bytes()).hexdigest() == MERMAID_SHA256
    except OSError:
        return False


def _mermaid_cache_path() -> Path:
    base = os.environ.get("XDG_CACHE_HOME") or (Path.home() / ".cache")
    return Path(base) / "aidd-marketplace" / f"mermaid-{MERMAID_VERSION}.min.js"


def _write_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as tmp:
        tmp.write(data)
        tmp_path = Path(tmp.name)
    # NamedTemporaryFile creates 0600; the asset sits next to a world-readable HTML.
    os.chmod(tmp_path, 0o644)
    os.replace(tmp_path, path)


def ensure_mermaid_asset(output_dir: Path) -> tuple[Path | None, str]:
    """Best-effort: put the pinned ``mermaid.min.js`` next to the generated HTML.

    Returns ``(path, note)`` when the asset is in place and ``(None, reason)``
    otherwise. Never raises: without the local asset the HTML still falls back to
    the CDN and, failing that, shows the diagram source with a notice.
    """
    target = output_dir / MERMAID_ASSET_NAME
    if _asset_is_valid(target):
        return target, "ya presente"

    cache = _mermaid_cache_path()
    if _asset_is_valid(cache):
        note = "copiado de la cache local"
        try:
            data = cache.read_bytes()
        except OSError as exc:
            return None, f"no se pudo leer la cache ({exc})"
    else:
        note = f"descargado de la CDN (mermaid@{MERMAID_VERSION})"
        try:
            with urllib.request.urlopen(MERMAID_URL, timeout=MERMAID_TIMEOUT) as response:
                data = response.read()
        except Exception as exc:  # noqa: BLE001 - best-effort by design
            return None, f"no se pudo descargar de la CDN ({exc})"
        if len(data) != MERMAID_SIZE or hashlib.sha256(data).hexdigest() != MERMAID_SHA256:
            return None, f"la descarga no coincide con mermaid@{MERMAID_VERSION} (tamano/hash)"
        try:
            _write_atomic(cache, data)
        except OSError:
            pass  # the cache is only an optimization; the copy below is what matters

    try:
        _write_atomic(target, data)
    except OSError as exc:
        return None, f"no se pudo escribir junto al HTML ({exc})"
    return target, note


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
    "kpis-ia": {"label": "KPIs de uso de IA", "phase": "Medicion"},
    "onboarding": {"label": "Onboarding del proyecto", "phase": "Transversal"},
    "traspaso": {"label": "Traspaso al equipo de mantenimiento", "phase": "Transversal"},
}


def detect_doc_type(stem: str) -> str:
    """Tipo de documento a partir del nombre de fichero, por subcadena.

    De la clave mas larga a la mas corta, no en el orden del dict. Varias son
    prefijo de otras -- `arquitectura-base` lo es de `arquitectura-base-prototipo`,
    y `requisitos` de `cliente-requisitos` -- asi que recorrer el dict tal cual
    solo acierta mientras nadie mueva una entrada. El orden actual es el correcto,
    pero es una propiedad invisible al anadir un tipo nuevo y que nada comprueba:
    un documento mal tipado no falla, sale con la etiqueta y la fase de otro.
    """
    stem = stem.lower()
    for key in sorted(DOC_TYPES, key=len, reverse=True):
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
# Multilane roadmap phase ids (see aisdd-specs, "Lanes"): F-<lane-id>-NN is a lane
# phase, FB-NN is a barrier that blocks every lane. F0 (foundation) is a barrier too.
# Lane ids are kebab-case but real roadmaps capitalize them (F-Data-Manager-01), so
# the class stays permissive; the trailing digits keep it from eating ordinary prose.
LANE_PHASE_RE = re.compile(r"\bF-([A-Za-z0-9]+(?:-[A-Za-z0-9]+)*)-(\d{1,3})\b")
BARRIER_PHASE_RE = re.compile(r"\b(FB-\d{1,3}|F0)\b")
# "[CONFLICTO DE FASEADO]" -- a cross-lane dependency that is neither declared via
# depends_on nor resolved by a barrier; the sprint plan flags it as a phasing error.
LANE_CONFLICT_RE = re.compile(r"\[\s*CONFLICTO DE FASEADO\s*\]", re.IGNORECASE)
# Waves ("oleadas"): the alternative parallelism mode, where phases are grouped into
# batches of up to parallel_developers instead of persistent lanes. Matches the wave
# label the roadmap and sprint plan write ("Oleada 2", "oleada 2").
WAVE_RE = re.compile(r"\bOleadas?\s+(\d{1,2})\b", re.IGNORECASE)

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
# Escala de tallas AIDD, 1 d = jornada de 8 h.
#
# SYNC: esta tabla vive replicada en tres scripts de tres plugins, porque no se
# pueden importar entre si (Claude Code instala cada plugin por separado). Si
# cambia en uno, cambia en los tres:
#   plugins/aisdd/skills/aisdd-specs/scripts/optimize_phasing.py
#   plugins/boosters/skills/booster-docs/scripts/render_docs_html.py
#   plugins/aiba/skills/aiba-metrics/scripts/compute_kpis.py
# Y en la prosa que la declara: aidd-user-story-details y aiba-hu-review-plan.
# De ella salen el calendario del faseado, el panel de KPIs y el ahorro medido:
# una copia rezagada no falla, hace que los tres den cifras distintas.
# La comprobacion la hace .github/scripts/check_plugin_assets.py.
EFFORT_DAYS = {"XS": 0.5, "S": 1.5, "M": 3.0, "L": 5.0, "XL": 8.0}

# Inline per-story metadata (e.g. "**Prioridad**: Alta   **Estimacion**: M"): turn
# the priority and effort *values* into pills so the human can scan them at a glance,
# and drop the estimation onto its own line when it trails other metadata. The label
# separator tolerates the closing </strong> left by bold conversion, colons and spaces.
PRIO_INLINE_RE = re.compile(
    r"(Prioridad(?:\s|:|</strong>){0,6})(Alta|Media|Baja|Cr[íi]tica)\b", re.IGNORECASE)
# Dos formatos, dos regex. La decoracion corre sobre HTML ya escapado, donde el
# `**Estimacion**` del markdown es `<strong>Estimacion</strong>`; el recuento de
# KPIs corre sobre el markdown crudo, con los asteriscos intactos. Compartir uno
# solo hacia que el recuento no encontrase nada: el panel decia 0 dias sobre un
# documento donde todas las historias tenian talla, y sin fallar.
# El de markdown es identico al de compute_kpis.py, que lee el mismo fichero.
EFFORT_INLINE_HTML_RE = re.compile(
    r"(Estimaci[oó]n(?:\s|:|</strong>){0,6})(XS|XL|S|M|L)\b")
EFFORT_INLINE_MD_RE = re.compile(
    r"(Estimaci[oó]n(?:\s|:|\*){0,6})(XS|XL|S|M|L)\b")
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
    # Barriers first: FB-01 would otherwise be left untouched by the lane pattern,
    # but F0 must not be swallowed by a later pass over already-emitted markup.
    escaped = BARRIER_PHASE_RE.sub(r'<span class="chip chip-barrier">\1</span>', escaped)
    escaped = LANE_PHASE_RE.sub(r'<span class="chip chip-lane">F-\1-\2</span>', escaped)
    escaped = LANE_CONFLICT_RE.sub(
        '<span class="chip chip-block">CONFLICTO DE FASEADO</span>', escaped)
    escaped = WAVE_RE.sub(r'<span class="chip chip-barrier">Oleada \1</span>', escaped)
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
    escaped = EFFORT_INLINE_HTML_RE.sub(_eff, escaped)
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
    # Targets: http(s)/mailto, in-page anchors, and relative paths (any target
    # without a scheme colon, e.g. "otro-doc.md" or "docs/x.md#seccion").
    escaped = re.sub(
        r"\[([^\]]+)\]\((https?:[^\s)]+|mailto:[^\s)]+|#[^\s)]+|[^:\s)]+)\)",
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

    # Capitalized-only matching: MoSCoW buckets are written "Must"/"Should"/... in
    # the docs; lowercase matches would overcount English prose ("it should...").
    moscow = Counter()
    for key, (label, _) in MOSCOW.items():
        n = len(re.findall(rf"\b{re.escape(label)}\b", markdown))
        if n:
            moscow[label] += n
    if moscow.get("Must"):
        kpis.append({"value": moscow["Must"], "label": "Must have", "tone": "must"})

    low = markdown.lower()
    if "fuera de esta fase" in low or "fuera de alcance" in low:
        # Best-effort: count bullet lines within scope-out region (skip if none found).
        scope_out = _scope_out_count(markdown)
        if scope_out:
            kpis.append({"value": scope_out, "label": "Fuera de alcance", "tone": "muted"})

    # Estimated effort in person-days from the fixed size scale (1 d = 8 h):
    # XS=0.5 · S=1.5 · M=3 · L=5 · XL=8. Counts "Estimacion: <talla>" inline labels
    # when present; otherwise standalone size cells in tables. Never both (a story's
    # inline size often reappears in a summary table and would double-count).
    sizes = [m.group(2).upper() for m in EFFORT_INLINE_MD_RE.finditer(markdown)]
    if not sizes:
        for tline in markdown.splitlines():
            t = tline.strip()
            if t.startswith("|") and t.endswith("|"):
                for cell in t.strip("|").split("|"):
                    if cell.strip() in EFFORT_DAYS:
                        sizes.append(cell.strip())
    if len(sizes) >= 2:
        total = sum(EFFORT_DAYS[s] for s in sizes)
        value = f"{total:g} d"
        kpis.append({"value": value, "label": f"Esfuerzo estimado ({len(sizes)} items)", "tone": "eff"})

    essentials = len(ESSENTIAL_RE.findall(markdown))
    if essentials:
        kpis.append({"value": essentials, "label": "Imprescindibles", "tone": "essential"})

    if blockers:
        kpis.append({"value": blockers, "label": "Bloqueantes", "tone": "block"})

    open_q = len(re.findall(r"^\s*[-*]\s+", _section_body(markdown, "pregunt"), re.MULTILINE))
    if open_q:
        kpis.append({"value": open_q, "label": "Preguntas abiertas", "tone": "warn"})

    kpis.extend(_lane_kpis(markdown, doc_type))

    return kpis


def _lane_kpis(markdown: str, doc_type: str) -> list[dict]:
    """Lane metrics for multilane roadmaps and the sprint plans built on them.

    Only meaningful where phases carry lane ids, so it stays scoped to the two doc
    types that name them; anywhere else the F-x-NN pattern would be a false positive.
    Returns [] for atomic roadmaps -- no lane ids, nothing to report.
    """
    if doc_type not in ("roadmap", "sprint-plan"):
        return []

    # Case-folded: a doc that writes both "F-api-01" and "F-API-02" means one lane,
    # not two -- the lane id is the same key the roadmap and the sprint plan share.
    lanes = {m.group(1).lower() for m in LANE_PHASE_RE.finditer(markdown)}
    waves = {int(m.group(1)) for m in WAVE_RE.finditer(markdown)}

    # waves and lanes are alternative modes, so a doc normally shows one or the other.
    if not lanes:
        return ([{"value": len(waves), "label": "Oleadas", "tone": "barrier"}]
                if waves else [])

    kpis = [{"value": len(lanes), "label": "Lanes", "tone": "lane"}]

    barriers = {b.upper() for b in BARRIER_PHASE_RE.findall(markdown)}
    if barriers:
        kpis.append({"value": len(barriers), "label": "Barreras", "tone": "barrier"})

    # A cross-lane dependency outside a barrier is a phasing error, not a note: the
    # target lane sits blocked waiting, which is the very stall multilane removes.
    conflicts = len(LANE_CONFLICT_RE.findall(markdown))
    if conflicts:
        kpis.append({"value": conflicts, "label": "Conflictos de faseado", "tone": "block"})

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


LIST_ITEM_RE = re.compile(r"^(\s*)(?:([-*])|(\d+)\.)\s+(.+)$")
TASK_RE = re.compile(r"^\[( |x|X)\]\s+(.*)$")
HR_RE = re.compile(r"^(-{3,}|\*{3,}|_{3,})$")


def render_list_block(lines: list[str]) -> str:
    """Render consecutive list lines supporting nesting (indent) and task checkboxes."""
    out: list[str] = []
    stack: list[tuple[int, str]] = []  # (indent, tag)
    for raw in lines:
        m = LIST_ITEM_RE.match(raw)
        if not m:
            continue
        indent = len(m.group(1).replace("\t", "  "))
        tag = "ul" if m.group(2) else "ol"
        content = m.group(4).strip()
        while stack and indent < stack[-1][0]:
            out.append(f"</li></{stack.pop()[1]}>")
        if stack and indent == stack[-1][0] and tag != stack[-1][1]:
            out.append(f"</li></{stack.pop()[1]}>")
        if not stack or indent > stack[-1][0]:
            out.append(f"<{tag}>")  # nested list stays inside the open <li>
            stack.append((indent, tag))
        else:
            out.append("</li>")
        task = TASK_RE.match(content)
        if task:
            checked = " checked" if task.group(1).lower() == "x" else ""
            out.append(
                f'<li class="task"><input type="checkbox" disabled{checked}> '
                + inline_markdown(task.group(2))
            )
        else:
            out.append("<li>" + inline_markdown(content))
    while stack:
        out.append(f"</li></{stack.pop()[1]}>")
    return "".join(out)


def markdown_to_html(markdown: str,
                     components: dict[str, str] | None = None) -> tuple[str, list[dict]]:
    output: list[str] = []
    toc: list[dict] = []
    lines = markdown.splitlines()
    i = 0
    section_open = False

    def close_lists() -> None:  # lists are now rendered as whole blocks; nothing pending
        return

    def close_section() -> None:
        nonlocal section_open
        if section_open:
            output.append("</section>")
            section_open = False

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # A block a shaper already turned into a component (see "Forma por tipo").
        if components and stripped in components:
            output.append(components[stripped])
            i += 1
            continue

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

        if HR_RE.match(stripped):
            output.append("<hr>")
            i += 1
            continue

        if LIST_ITEM_RE.match(line):
            list_lines = []
            while i < len(lines) and LIST_ITEM_RE.match(lines[i]):
                list_lines.append(lines[i])
                i += 1
            output.append(render_list_block(list_lines))
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


# --- Forma por tipo de documento --------------------------------------------
#
# `DOC_TYPES` dice que documento se esta pintando, y hasta aqui solo servia para
# la cabecera: los catorce tipos salian con la misma forma, y el lector tenia
# que leerlos enteros para saber que era cada cosa. Aqui sirve para dar a cada
# uno la forma de lo que cuenta: las historias como tarjetas, los sprints como
# cajas con su carga, las fases como linea temporal.
#
# La regla que no se rompe: **el markdown es la fuente de verdad y el HTML una
# vista**. Un formador solo sustituye los tramos que reconoce, y dentro de cada
# uno pinta tambien lo que no sabe clasificar. Lo que no esta donde lo espera se
# queda en el markdown y sale como siempre: un formador que exigiera una
# estructura haria del documento un rehen del renderizador.
#
# Solo se forman bloques de nivel 3 o mas: un `##` es una seccion del indice, y
# convertirla en tarjeta la sacaria del TOC.
#
# Cada tipo de esta lista tiene su caso en `.github/scripts/check_generated_html.py`:
# una entrada con la forma, que tiene que recibirla, y otra sin ella, que tiene
# que salir como siempre sin perder texto.
SHAPED_TYPES = ("detalle-historias-usuario", "sprint-plan", "roadmap")

LABEL_RE = re.compile(r"\*\*([^*:\n]{1,48}?)\s*(?::\*\*|\*\*\s*:)\s*")
HU_HEAD_RE = re.compile(r"^((?:HU|US)-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*)\s*[—–:\-]*\s*(.*)$")
SPRINT_HEAD_RE = re.compile(r"^Sprint\s*(\d{1,3})\b\s*(.*)$", re.IGNORECASE)
SPRINT_DATES_RE = re.compile(
    r"\(?\s*(\d{1,2}[/.-]\d{1,2}(?:[/.-]\d{2,4})?)\s*(?:al|a|hasta|–|—|-|→)\s*"
    r"(\d{1,2}[/.-]\d{1,2}(?:[/.-]\d{2,4})?)\s*\)?")
SPRINT_LABEL_RE = re.compile(
    r"(?:^|(?<=[\s.;|]))(objetivo|unidades(?:\s+incluidas)?|incluye|"
    r"carga(?:\s+real)?(?:\s+agregada)?|capacidad|ocupaci[oó]n|"
    r"perfiles?(?:\s+asignados?)?|asignaci[oó]n(?:\s+de\s+perfiles)?|"
    r"definition\s+of\s+done|dod)\s*:", re.IGNORECASE)
NUM_RE = r"(\d+(?:[.,]\d+)?)"
# F0, F1, F-01, F-api-01, FB-01, "Fase 2". El de lane va antes que el corto para
# que `F-api-01` no se quede en nada.
PHASE_ID = (r"(?:F0|FB-\d{1,3}|F-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*-\d{1,3}|F-?\d{1,3}"
            r"|Fase\s*\d{1,3})")
PHASE_START_RE = re.compile(rf"^({PHASE_ID})\b", re.IGNORECASE)
PHASE_ANY_RE = re.compile(rf"\b{PHASE_ID}\b", re.IGNORECASE)

STORY_KEYS = (
    ("fase", ("fase",)),
    ("prioridad", ("prioridad",)),
    ("talla", ("estimacion", "talla", "esfuerzo")),
    ("rf", ("rf", "requisito")),
    ("descripcion", ("descripcion", "enunciado", "historia")),
    ("criterios", ("criterios",)),
    ("notas", ("notas", "dependencias")),
)
PHASE_KEYS = (
    ("nombre", ("nombre", "titulo")),
    ("objetivo", ("objetivo", "descripcion", "que entra")),
    ("depende", ("depend",)),
    ("oleada", ("oleada", "wave")),
    ("lane", ("lane", "linea")),
    ("sprint", ("sprint",)),
    ("riesgo", ("riesgo",)),
    ("esfuerzo", ("esfuerzo", "talla", "estimacion")),
    ("estado", ("estado",)),
    ("change", ("change",)),
)
TONE = {"chip-prio-high": "high", "chip-prio-mid": "mid", "chip-prio-low": "low"}
RISK = {"bajo": "chip-prio-low", "medio": "chip-prio-mid", "alto": "chip-prio-high"}
# El estado de una fase se pinta con icono y **con su texto**: el color solo no
# dice nada a quien no lo distingue, y el texto es el del documento.
STATES = ((r"cerrad|hech|complet|termin|archiv|done", "done", "✓"),
          (r"curso|progres|abiert|activ|doing", "doing", "◐"),
          (r"pendient|por hacer|sin empezar|planific|todo", "todo", "○"))


def _norm(text: str) -> str:
    """Comparable: sin tildes, sin enfasis y en minusculas."""
    t = unicodedata.normalize("NFKD", re.sub(r"[*`]", "", text or ""))
    return "".join(c for c in t if not unicodedata.combining(c)).lower().strip()


def _plain(text: str) -> str:
    return re.sub(r"[*`]", "", text or "").strip()


def _empty(text: str) -> bool:
    return _norm(text) in ("", "—", "–", "-", "n/a", "na", "ninguna", "ninguno", "no aplica")


def _heading(line: str) -> tuple[int, str] | None:
    m = re.match(r"^(#{1,6})\s+(.+)$", line.strip())
    return (len(m.group(1)), m.group(2).strip()) if m else None


def _block_end(lines: list[str], start: int, level: int) -> int:
    """Donde acaba el bloque que abre un titulo de nivel `level`."""
    j = start
    while j < len(lines):
        h = _heading(lines[j])
        if h and h[0] <= level:
            break
        j += 1
    return j


def _fields(text: str) -> tuple[str, list[tuple[str, str]]]:
    """Lo que precede a la primera etiqueta, y los pares `**Etiqueta**: valor`."""
    marks = list(LABEL_RE.finditer(text))
    pairs = [(m.group(1).strip(),
              text[m.end():(marks[k + 1].start() if k + 1 < len(marks) else len(text))].strip())
             for k, m in enumerate(marks)]
    return (text[:marks[0].start()].strip() if marks else text), pairs


def _dedent(lines: list[str]) -> list[str]:
    real = [l for l in lines if l.strip()]
    if not real:
        return []
    cut = min(len(l) - len(l.lstrip()) for l in real)
    return [l[cut:] for l in lines]


def _items(body: list[str]) -> list[dict]:
    """El cuerpo de un bloque, en orden: vinetas de primer nivel con lo que les
    cuelga, y lineas sueltas. No se descarta ninguna."""
    out, i = [], 0
    while i < len(body):
        m = LIST_ITEM_RE.match(body[i])
        if m and not m.group(1):
            j = i + 1
            while j < len(body) and body[j].strip() and body[j][:1] in (" ", "\t"):
                j += 1
            out.append({"text": m.group(4).strip(), "sub": _dedent(body[i + 1:j]),
                        "raw": body[i:j]})
            i = j
        else:
            out.append({"loose": body[i]})
            i += 1
    return out


def _key_of(label: str, keys: tuple) -> str | None:
    n = _norm(label)
    return next((k for k, starts in keys if n.startswith(starts)), None)


def _md(lines: list[str]) -> str:
    """Un trozo de markdown dentro de un componente, pintado como siempre."""
    return markdown_to_html("\n".join(lines))[0] if any(l.strip() for l in lines) else ""


def _chip(text: str, cls: str, title: str = "") -> str:
    t = f' title="{html.escape(title)}"' if title else ""
    return f'<span class="chip {cls}"{t}>{html.escape(text)}</span>'


def _days(d: float) -> str:
    return f"{d:g}".replace(".", ",") + " d"


def _plural(n: int, one: str, many: str | None = None) -> str:
    return f"{n} {one if n == 1 else (many or one + 's')}"


def _mark(comps: dict, fragment: str) -> list[str]:
    key = f"\x00{len(comps)}\x00"
    comps[key] = fragment
    return ["", key, ""]


def _runs(markdown: str, match, build, comps: dict) -> str:
    """Sustituye cada racha de bloques seguidos, del mismo nivel, que `match`
    reconoce en su titulo. `build([(match, titulo, cuerpo)])` devuelve el HTML,
    o None si la racha no le basta: entonces se queda como estaba."""
    lines = markdown.splitlines()
    out, i = [], 0
    while i < len(lines):
        h = _heading(lines[i])
        m = match(h[1]) if h and h[0] >= 3 else None
        if not m:
            out.append(lines[i])
            i += 1
            continue
        level, blocks, start = h[0], [], i
        while i < len(lines):
            h = _heading(lines[i])
            m = match(h[1]) if h and h[0] == level else None
            if not m:
                break
            end = _block_end(lines, i + 1, level)
            blocks.append((m, h[1], lines[i + 1:end]))
            i = end
        fragment = build(blocks)
        out += _mark(comps, fragment) if fragment else lines[start:i]
    return "\n".join(out)


# Historias de usuario: una tarjeta por HU --id, titulo, fase, prioridad, talla y
# RF de un vistazo, criterios plegados--, agrupadas por fase y con un indice
# cuando son muchas. Hoy eran treinta historias seguidas.

def _prio(value: str) -> tuple[str, str] | None:
    n = _norm(value)
    return PRIORITY.get(n.split()[0]) if n else None


def _tone(s: dict) -> str:
    prio = _prio(s["prioridad"])
    return TONE.get(prio[1], "none") if prio else "none"


def _parse_story(m, heading: str, body: list[str]) -> dict:
    s = {"id": m.group(1), "title": m.group(2).strip() or m.group(1),
         "slug": slugify(heading), "fase": "", "prioridad": "", "talla": "", "talla_txt": "",
         "rf": "", "desc": [], "crit": [], "crit_label": "Criterios de aceptación",
         "notas": [], "notas_label": "", "extra": [], "rest": []}
    for it in _items(body):
        if "loose" in it:
            s["rest"].append(it["loose"])
            continue
        prefix, pairs = _fields(it["text"])
        if not pairs or prefix:
            s["rest"] += it["raw"]
            continue
        for n, (label, value) in enumerate(pairs):
            sub = it["sub"] if n == len(pairs) - 1 else []
            key = _key_of(label, STORY_KEYS)
            size = re.search(r"\b(XS|XL|S|M|L)\b", value) if key == "talla" else None
            if key in ("fase", "prioridad", "rf") and not sub:
                s[key] = value
            elif size and not sub:
                s["talla"], s["talla_txt"] = size.group(1), _plain(value)
            elif key == "descripcion":
                s["desc"] = ([value, ""] if value else []) + sub
            elif key == "criterios":
                s["crit_label"] = label
                s["crit"] = ([f"- {value}"] if value else []) + sub
            elif key == "notas":
                s["notas_label"] = label
                s["notas"] = ([value, ""] if value else []) + sub
            else:
                s["extra"].append((label, value, sub))
    return s


def _story_card(s: dict) -> str:
    prio = _prio(s["prioridad"])
    meta = []
    if s["fase"]:
        meta.append(_chip(_plain(s["fase"]), "chip-phase", "Fase"))
    if prio:
        meta.append(_chip(prio[0], prio[1], "Prioridad"))
    elif s["prioridad"]:
        meta.append(_chip(_plain(s["prioridad"]), "chip-soft", "Prioridad"))
    if s["talla"]:
        meta.append(_chip(s["talla_txt"], EFFORT[s["talla"].lower()], "Estimación"))
    if s["rf"]:
        meta.append(inline_markdown(s["rf"], meta=False))
    out = [f'<article class="hu-card tone-{_tone(s)}" id="{s["slug"]}">',
           f'<header class="hu-head"><span class="hu-id">{html.escape(s["id"])}</span>'
           f'<h3 class="hu-title">{inline_markdown(s["title"], chips=False)}</h3></header>']
    if meta:
        out.append(f'<div class="hu-meta">{" ".join(meta)}</div>')
    if s["desc"]:
        out.append(f'<div class="hu-desc">{_md(s["desc"])}</div>')
    if s["crit"]:
        first = [l for l in s["crit"] if (m := LIST_ITEM_RE.match(l)) and not m.group(1)]
        ess = len(ESSENTIAL_RE.findall("\n".join(s["crit"])))
        count = str(len(first)) + (f" · {_plural(ess, 'imprescindible')}" if ess else "")
        out.append(f'<details class="hu-criteria"><summary>{html.escape(s["crit_label"])}'
                   f'<span class="hu-count">{count}</span></summary>{_md(s["crit"])}</details>')
    if s["notas"]:
        out.append(f'<div class="hu-notes"><span class="hu-label">{html.escape(s["notas_label"])}'
                   f'</span>{_md(s["notas"])}</div>')
    if s["extra"]:
        out.append('<dl class="hu-extra">' + "".join(
            f"<dt>{html.escape(label)}</dt><dd>{inline_markdown(value)}{_md(sub)}</dd>"
            for label, value, sub in s["extra"]) + "</dl>")
    if any(l.strip() for l in s["rest"]):
        out.append(f'<div class="hu-rest">{_md(s["rest"])}</div>')
    out.append("</article>")
    return "".join(out)


def _stories_html(blocks: list) -> str:
    stories = [_parse_story(m, title, body) for m, title, body in blocks]
    groups: dict[str, list] = {}
    for s in stories:
        groups.setdefault(_plain(s["fase"]), []).append(s)
    out = ['<div class="hu-board">']
    if len(stories) >= 6:
        out.append('<nav class="hu-index" aria-label="Índice de historias">' + "".join(
            f'<a class="hu-tile tone-{_tone(s)}" href="#{s["slug"]}">'
            f'<span class="hu-id">{html.escape(s["id"])}</span>'
            f'<span class="hu-tile-title">{html.escape(_plain(s["title"]))}</span>'
            + (_chip(s["talla"], EFFORT[s["talla"].lower()], "Estimación") if s["talla"] else "")
            + "</a>" for s in stories) + "</nav>")
    for phase, members in groups.items():
        if len(groups) > 1 or phase:
            days = sum(EFFORT_DAYS[s["talla"]] for s in members if s["talla"])
            name = phase if not phase or _norm(phase).startswith("fase") else f"Fase {phase}"
            out.append(f'<h3 class="hu-group">{html.escape(name or "Sin fase")} <small>'
                       + _plural(len(members), "historia") + (f" · {_days(days)}" if days else "")
                       + "</small></h3>")
        out.append('<div class="hu-list">' + "".join(_story_card(s) for s in members) + "</div>")
    out.append("</div>")
    return "".join(out)


def shape_stories(markdown: str, comps: dict) -> str:
    return _runs(markdown, lambda t: HU_HEAD_RE.match(_plain(t)), _stories_html, comps)


# Plan de sprints: una caja numerada por sprint, con sus fechas, su objetivo, su
# carga frente a la capacidad y sus unidades. La carga se pinta como barra y con
# su texto original al lado: la cifra es del documento, la barra solo la ensena.

def _to_float(text: str) -> float:
    return float(text.replace(",", "."))


def _load(sp: dict, key: str, value: str) -> None:
    pct = re.search(NUM_RE + r"\s*%", value)
    if pct and sp["pct"] is None:
        sp["pct"] = _to_float(pct.group(1))
    rest = re.sub(NUM_RE + r"\s*%", " ", value)
    pair = re.search(NUM_RE + r"\s*(?:d|días|dias|jornadas|pts|puntos)?\s*"
                     r"(?:/|de|sobre|vs\.?|frente\s+a)\s*" + NUM_RE, rest)
    one = re.search(NUM_RE, rest)
    if key.startswith("capacidad"):
        if one and sp["capacidad"] is None:
            sp["capacidad"] = _to_float(one.group(1))
    elif key.startswith("carga"):
        if pair:
            sp["carga"] = _to_float(pair.group(1))
            sp["capacidad"] = sp["capacidad"] or _to_float(pair.group(2))
        elif one and sp["carga"] is None:
            sp["carga"] = _to_float(one.group(1))


def _parse_sprint(m, heading: str, body: list[str]) -> dict:
    tail = m.group(2)
    dates = SPRINT_DATES_RE.search(tail)
    title = (SPRINT_DATES_RE.sub(" ", tail) if dates else tail).strip(" \t—–-:·|()")
    sp = {"num": m.group(1), "title": title, "slug": slugify(heading),
          "desde": dates.group(1) if dates else "", "hasta": dates.group(2) if dates else "",
          "objetivo": None, "unidades": None, "carga": None, "capacidad": None, "pct": None,
          "carga_txt": [], "fields": [], "rest": []}
    i = 0
    while i < len(body):
        line = body[i]
        i += 1
        s = line.strip()
        text = re.sub(r"^(?:[-*]|\d+\.)\s+", "", s).replace("**", "")
        marks = list(SPRINT_LABEL_RE.finditer(text)) if s and not s.startswith("|") else []
        if not marks or text[:marks[0].start()].strip():
            sp["rest"].append(line)
            continue
        for k, mm in enumerate(marks):
            end = marks[k + 1].start() if k + 1 < len(marks) else len(text)
            label, value = mm.group(1).strip(), text[mm.end():end].strip().rstrip(".;,").strip()
            sub: list[str] = []
            if not value and k == len(marks) - 1:
                # Una etiqueta sin valor lleva debajo lo que la rellena.
                while i < len(body) and body[i].strip() and body[i][:1] in (" ", "\t"):
                    sub.append(body[i])
                    i += 1
                sub = _dedent(sub)
            key = _norm(label)
            if key.startswith("objetivo") and sp["objetivo"] is None:
                sp["objetivo"] = (label, value, sub)
            elif key.startswith(("unidades", "incluye")) and sp["unidades"] is None:
                sp["unidades"] = (label, value, sub)
            elif key.startswith(("carga", "capacidad", "ocupacion")):
                _load(sp, key, value)
                sp["carga_txt"].append(f"{label}: {value}")
            else:
                sp["fields"].append((label, value, sub))
    if sp["pct"] is None and sp["carga"] is not None and sp["capacidad"]:
        sp["pct"] = sp["carga"] / sp["capacidad"] * 100
    return sp


def _load_html(sp: dict) -> str:
    pct = sp["pct"]
    tone, figure, bar = "none", "", ""
    if pct is not None:
        tone, state = (("over", "sobrecargado") if pct > 100 else
                       ("low", "con holgura") if pct < 60 else ("ok", "en capacidad"))
        figure = f"<strong>{pct:.0f} %</strong> de la capacidad · {state}"
        bar = (f'<div class="load-bar" role="img" aria-label="{pct:.0f} % de la capacidad">'
               f'<span style="width:{min(pct, 100):.0f}%"></span></div>')
    source = " · ".join(inline_markdown(t) for t in sp["carga_txt"])
    sep = "<br>" if figure and source else ""
    return (f'<div class="sprint-load load-{tone}">{bar}<p class="load-text">{figure}{sep}'
            f'<span class="load-src">{source}</span></p></div>')


def _labelled(cls: str, field: tuple) -> str:
    label, value, sub = field
    return (f'<div class="{cls}"><span class="k">{html.escape(label)}</span> '
            f'{inline_markdown(value)}{_md(sub)}</div>')


def _sprint_box(sp: dict) -> str:
    out = [f'<article class="sprint-box" id="{sp["slug"]}">',
           f'<header class="sprint-head"><span class="sprint-num" aria-hidden="true">'
           f'{html.escape(sp["num"])}</span><div>',
           f'<h3 class="sprint-title">Sprint {html.escape(sp["num"])}'
           + (f' <span class="sprint-sub">{inline_markdown(sp["title"], chips=False)}</span>'
              if sp["title"] else "") + "</h3>"]
    if sp["desde"]:
        out.append(f'<p class="sprint-dates">{html.escape(sp["desde"])} → '
                   f'{html.escape(sp["hasta"])}</p>')
    out.append("</div></header>")
    if sp["objetivo"]:
        out.append(_labelled("sprint-goal", sp["objetivo"]))
    if sp["pct"] is not None or sp["carga_txt"]:
        out.append(_load_html(sp))
    if sp["unidades"]:
        out.append(_labelled("sprint-units", sp["unidades"]))
    if sp["fields"]:
        out.append('<dl class="sprint-extra">' + "".join(
            f"<dt>{html.escape(label)}</dt><dd>{inline_markdown(value)}{_md(sub)}</dd>"
            for label, value, sub in sp["fields"]) + "</dl>")
    if any(l.strip() for l in sp["rest"]):
        out.append(f'<details class="sprint-more"><summary>Más detalle</summary>'
                   f'{_md(sp["rest"])}</details>')
    out.append("</article>")
    return "".join(out)


def _sprints_html(blocks: list) -> str:
    sprints = [_parse_sprint(m, title, body) for m, title, body in blocks]
    over = sum(1 for s in sprints if s["pct"] is not None and s["pct"] > 100)
    parts = [_plural(len(sprints), "sprint")]
    if sprints[0]["desde"] and sprints[-1]["hasta"]:
        parts.append(f'{sprints[0]["desde"]} → {sprints[-1]["hasta"]}')
    if over:
        parts.append(_plural(over, "sobrecargado"))
    return ('<div class="sprint-board">'
            f'<p class="board-summary">{html.escape(" · ".join(parts))}</p>'
            '<div class="sprint-grid">' + "".join(_sprint_box(s) for s in sprints)
            + "</div></div>")


def shape_sprints(markdown: str, comps: dict) -> str:
    return _runs(markdown, lambda t: SPRINT_HEAD_RE.match(_plain(t)), _sprints_html, comps)


# Roadmap: las fases como linea temporal. En `multilane`, una calle por lane con
# las barreras cruzandolas todas --que es lo que hacen: detienen todos los
# lanes--; en `waves`, una fila por oleada con sus fases lado a lado; si no, una
# linea. Sale de la tabla de fases o de una fase por titulo. La tabla de
# dependencias cross-lane y la de oleadas **no** son la lista de fases y se
# quedan como tabla.

def _phase(pid: str, name: str = "") -> dict:
    return {"id": pid, "nombre": name, "objetivo": "", "depende": "", "oleada": "",
            "lane": "", "sprint": "", "riesgo": "", "esfuerzo": "", "estado": "",
            "change": "", "extra": [], "more": [], "slug": ""}


def _barrier(pid: str) -> bool:
    p = pid.upper().replace(" ", "")
    return p == "F0" or p.startswith("FB-")


def _lane_of(f: dict) -> str:
    if not _empty(f["lane"]):
        return _plain(f["lane"])
    m = LANE_PHASE_RE.match(f["id"])
    return m.group(1) if m else ""


def _wave_of(f: dict) -> int:
    m = re.search(r"\d+", _plain(f["oleada"])) if not _empty(f["oleada"]) else None
    return int(m.group()) if m else 0


def _state(value: str) -> tuple[str, str] | None:
    if _empty(value):
        return None
    n = _norm(value)
    for pattern, cls, icon in STATES:
        if re.search(pattern, n):
            return cls, f"{icon} {_plain(value)}"
    return "other", _plain(value)


def _phase_node(f: dict) -> str:
    barrier = _barrier(f["id"])
    st = _state(f["estado"])
    cls = "rm-node" + (" rm-barrier-node" if barrier else "") + (f" st-{st[0]}" if st else "")
    anchor = f' id="{f["slug"]}"' if f["slug"] else ""
    out = [f'<div class="{cls}"{anchor}><div class="rm-node-head">',
           _chip(f["id"], "chip-barrier" if barrier else "chip-phase",
                 "Barrera: detiene todos los lanes" if barrier else "Fase")]
    if st:
        out.append(f'<span class="rm-state st-{st[0]}">{html.escape(st[1])}</span>')
    out.append("</div>")
    if f["nombre"]:
        out.append(f'<p class="rm-name">{inline_markdown(f["nombre"])}</p>')
    if f["objetivo"]:
        out.append(f'<p class="rm-obj">{inline_markdown(f["objetivo"])}</p>')
    meta = []
    if not _empty(f["sprint"]):
        s = _plain(f["sprint"])
        meta.append(_chip(f"Sprint {s}" if re.fullmatch(r"[\d ,y\-–]+", s) else s,
                          "chip-soft", "Sprint"))
    if not _empty(f["riesgo"]):
        r = _plain(f["riesgo"])
        cls_r = next((c for k, c in RISK.items() if re.search(rf"\b{k}\b", _norm(r))), "chip-soft")
        meta.append(_chip(r if _norm(r).startswith("riesgo") else f"riesgo {r.lower()}",
                          cls_r, "Riesgo de contexto"))
    if not _empty(f["esfuerzo"]):
        meta.append(f'<span class="rm-effort">{inline_markdown(f["esfuerzo"], meta=False)}</span>')
    if not _empty(f["change"]):
        meta.append(f"<code>{html.escape(_plain(f['change']))}</code>")
    if meta:
        out.append('<div class="rm-meta">' + " ".join(meta) + "</div>")
    if not _empty(f["depende"]):
        plain = _plain(f["depende"])
        deps = PHASE_ANY_RE.findall(plain)
        only_ids = deps and not re.sub(r"[\s,;/y]+", "", PHASE_ANY_RE.sub("", plain))
        value = (" ".join(_chip(d, "chip-barrier" if _barrier(d) else "chip-phase") for d in deps)
                 if only_ids else inline_markdown(f["depende"]))
        out.append(f'<p class="rm-deps"><span class="k">Depende de</span> {value}</p>')
    if f["extra"]:
        out.append('<dl class="rm-extra">' + "".join(
            f"<dt>{inline_markdown(k, chips=False)}</dt><dd>{inline_markdown(v)}</dd>"
            for k, v in f["extra"]) + "</dl>")
    if any(l.strip() for l in f["more"]):
        out.append(f'<details class="rm-more"><summary>Detalle de la fase</summary>'
                   f'{_md(f["more"])}</details>')
    out.append("</div>")
    return "".join(out)


def _swimlanes(phases: list[dict], lanes: list[str]) -> str:
    out = [f'<div class="rm-scroll"><div class="rm-lanes" style="--lanes:{len(lanes)}">',
           '<div class="rm-lane-heads">' + "".join(
               f'<div class="rm-lane-head">{html.escape(l)}</div>' for l in lanes) + "</div>"]
    stretch: dict[str, list] = {l: [] for l in lanes}
    loose: list[dict] = []

    def flush() -> None:
        if any(stretch.values()):
            out.append('<div class="rm-tramo">' + "".join(
                '<div class="rm-col">' + "".join(_phase_node(f) for f in stretch[l]) + "</div>"
                for l in lanes) + "</div>")
            for l in lanes:
                stretch[l] = []

    for f in phases:
        if _barrier(f["id"]):
            flush()
            out.append(f'<div class="rm-barrier">{_phase_node(f)}</div>')
        elif _lane_of(f) in stretch:
            stretch[_lane_of(f)].append(f)
        else:
            loose.append(f)
    flush()
    out.append("</div></div>")
    if loose:
        out.append('<p class="rm-loose-title">Sin lane</p><div class="rm-row">'
                   + "".join(_phase_node(f) for f in loose) + "</div>")
    return "".join(out)


def _waves(phases: list[dict]) -> str:
    groups: dict[int, list] = {}
    for f in phases:
        groups.setdefault(_wave_of(f), []).append(f)
    out = ['<ol class="rm-waves">']
    for n in sorted(k for k in groups if k) + ([0] if 0 in groups else []):
        members = groups[n]
        sub = _plural(len(members), "fase") + (" en paralelo" if len(members) > 1 else "")
        out.append('<li class="rm-wave"><div class="rm-wave-head"><span class="rm-wave-num">'
                   + (f"Oleada {n}" if n else "Sin oleada") + '</span>'
                   f'<span class="rm-wave-sub">{sub}</span></div><div class="rm-row">'
                   + "".join(_phase_node(f) for f in members) + "</div></li>")
    out.append("</ol>")
    return "".join(out)


def _roadmap_html(phases: list[dict], leftover: str = "") -> str:
    lanes: list[str] = []
    for f in phases:
        lane = _lane_of(f)
        if lane and not _barrier(f["id"]) and lane not in lanes:
            lanes.append(lane)
    parts = [_plural(len(phases), "fase")]
    if len(lanes) >= 2:
        body = _swimlanes(phases, lanes)
        parts.append(f"{len(lanes)} lanes")
        barriers = sum(1 for f in phases if _barrier(f["id"]))
        if barriers:
            parts.append(_plural(barriers, "barrera"))
    elif any(_wave_of(f) for f in phases):
        body = _waves(phases)
        parts.append(_plural(len({_wave_of(f) for f in phases if _wave_of(f)}), "oleada"))
    else:
        body = ('<ol class="rm-line">' + "".join(
            f'<li class="rm-step">{_phase_node(f)}</li>' for f in phases) + "</ol>")
    states = Counter(st[0] for f in phases if (st := _state(f["estado"])))
    for cls, one, many in (("done", "cerrada", "cerradas"), ("doing", "en curso", "en curso"),
                           ("todo", "pendiente", "pendientes")):
        if states.get(cls):
            parts.append(_plural(states[cls], one, many))
    return (f'<div class="rm-board"><p class="board-summary">{html.escape(" · ".join(parts))}</p>'
            f"{body}{leftover}</div>")


def _phase_table(table: list[str]) -> tuple[list[dict], str] | None:
    """La tabla de fases como fases, o None si no lo es."""
    rows = [[c.strip() for c in l.strip().strip("|").split("|")] for l in table]
    rows = [r for r in rows if not all(re.fullmatch(r":?-{3,}:?", c) for c in r)]
    if len(rows) < 3:
        return None
    head, body = rows[0], rows[1:]
    # Origen y destino: son las dependencias entre fases, no la lista de fases.
    if any("origen" in c or "destino" in c for c in map(_norm, head)):
        return None

    def is_id(cell: str) -> bool:
        t = _plain(cell)
        return bool(PHASE_START_RE.match(t)) and len(PHASE_ANY_RE.findall(t)) == 1

    ncol = len(head)
    idc = next((k for k in range(ncol)
                if sum(1 for r in body if k < len(r) and is_id(r[k])) >= max(2, .6 * len(body))),
               None)
    if idc is None:
        return None
    cols = {k: _key_of(head[k], PHASE_KEYS) for k in range(ncol) if k != idc}
    phases, leftover, seen = [], [], set()
    for r in body:
        r = (r + [""] * ncol)[:ncol]
        if not is_id(r[idc]):
            leftover.append(r)
            continue
        t = _plain(r[idc])
        m = PHASE_START_RE.match(t)
        if m.group(1).upper() in seen:
            return None     # la misma fase dos veces: no es la lista de fases
        seen.add(m.group(1).upper())
        f = _phase(m.group(1), t[m.end():].strip(" —–-:·"))
        for k, key in cols.items():
            if _empty(r[k]):
                continue
            if key is None or (key == "nombre" and f["nombre"]) or f.get(key):
                f["extra"].append((head[k], r[k]))
            else:
                f[key] = r[k]
        if not f["nombre"] and f["objetivo"]:
            f["nombre"], f["objetivo"] = f["objetivo"], ""
        phases.append(f)
    rest = ""
    if leftover:
        rest = render_table(["| " + " | ".join(head) + " |", "|" + "---|" * ncol]
                            + ["| " + " | ".join(r) + " |" for r in leftover])
    return phases, rest


def _phase_from_heading(m, title: str, body: list[str]) -> dict:
    t = _plain(title)
    mm = PHASE_START_RE.match(t)
    f = _phase(mm.group(1), t[mm.end():].strip(" —–-:·"))
    f["slug"] = slugify(title)
    for it in _items(body):
        if "loose" in it:
            f["more"].append(it["loose"])
            continue
        prefix, pairs = _fields(it["text"])
        if not pairs or prefix:
            f["more"] += it["raw"]
            continue
        for n, (label, value) in enumerate(pairs):
            sub = it["sub"] if n == len(pairs) - 1 else []
            key = _key_of(label, PHASE_KEYS)
            if key and key != "nombre" and not sub and not f[key]:
                f[key] = value
            else:
                f["more"] += [f"- **{label}**: {value}"] + ["  " + l for l in sub]
    return f


def _phase_headings_html(blocks: list) -> str | None:
    if len(blocks) < 2:
        return None
    return _roadmap_html([_phase_from_heading(m, t, b) for m, t, b in blocks])


def shape_roadmap(markdown: str, comps: dict) -> str:
    markdown = _runs(markdown, lambda t: PHASE_START_RE.match(_plain(t)),
                     _phase_headings_html, comps)
    lines, out, i = markdown.splitlines(), [], 0
    while i < len(lines):
        s = lines[i].strip()
        if s.startswith("|") and s.endswith("|"):
            j = i
            while j < len(lines) and lines[j].strip().startswith("|") and lines[j].strip().endswith("|"):
                j += 1
            table = _phase_table(lines[i:j])
            out += _mark(comps, _roadmap_html(*table)) if table else lines[i:j]
            i = j
            continue
        out.append(lines[i])
        i += 1
    return "\n".join(out)


SHAPERS = {"detalle-historias-usuario": shape_stories, "sprint-plan": shape_sprints,
           "roadmap": shape_roadmap}


def shape(markdown: str, doc_type: str) -> tuple[str, dict[str, str]]:
    """El markdown con los tramos que tienen forma propia ya convertidos."""
    shaper = SHAPERS.get(doc_type)
    comps: dict[str, str] = {}
    if shaper is None:
        return markdown, comps
    try:
        return shaper(markdown, comps), comps
    except Exception as exc:  # noqa: BLE001 - la vista nunca puede tumbar el render
        print(f"ADVERTENCIA: no se pudo dar forma a '{doc_type}' ({exc}); se pinta como texto.",
              file=sys.stderr)
        return markdown, {}


SHAPE_CSS = """
    /* Forma por tipo de documento: tarjetas, cajas y linea temporal */
    .board-summary { margin: 0 0 12px; color: var(--muted); font-size: .9rem; max-width: none; }
    .k, .hu-label { margin-right: 6px; color: var(--muted); font-size: .72rem; font-weight: 600;
      text-transform: uppercase; letter-spacing: .06em; }
    .chip-phase { color: var(--accent); background: var(--accent-soft); font-family: "SF Mono",Menlo,monospace; }
    .chip-soft { color: var(--text-soft); background: var(--panel-soft); }
    .hu-extra, .sprint-extra, .rm-extra { display: grid; grid-template-columns: max-content minmax(0, 1fr);
      gap: 4px 14px; margin: 10px 0 0; font-size: .9rem; }
    .hu-extra dt, .sprint-extra dt, .rm-extra dt { color: var(--muted); font-weight: 600; }
    .hu-extra dd, .sprint-extra dd, .rm-extra dd { margin: 0; color: var(--text-soft); }
    .hu-extra dd p, .sprint-extra dd p, .sprint-goal p, .sprint-units p { margin: 0; }
    details > summary { cursor: pointer; color: var(--text); font-weight: 600; font-size: .9rem; }
    details > summary::marker { color: var(--accent); }
    /* Historias */
    .hu-index { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 8px; margin: 0 0 18px; }
    .hu-tile { display: flex; align-items: center; gap: 8px; min-width: 0; padding: 7px 10px;
      border: 1px solid var(--line); border-left: 3px solid var(--line-strong); border-radius: 8px;
      background: var(--panel-soft); color: var(--text-soft); font-size: .85rem; }
    .hu-tile:hover { border-color: var(--accent); text-decoration: none; }
    .hu-tile-title { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .hu-id { flex: none; font-family: "SF Mono",Menlo,monospace; font-size: .78rem; font-weight: 700; color: var(--us); }
    .hu-group { display: flex; align-items: baseline; gap: 10px; margin: 22px 0 10px; font-size: 1rem; }
    .hu-group small { color: var(--muted); font-weight: 400; font-size: .85rem; }
    .hu-list { display: flex; flex-direction: column; gap: 10px; }
    .hu-card { background: var(--panel); border: 1px solid var(--line); border-left: 4px solid var(--line-strong);
      border-radius: 10px; padding: 14px 18px; }
    .tone-high { border-left-color: var(--prio-high); }
    .tone-mid { border-left-color: var(--prio-mid); }
    .tone-low { border-left-color: var(--prio-low); }
    .hu-head { display: flex; align-items: baseline; gap: 10px; }
    .hu-title { margin: 0; font-size: 1.02rem; line-height: 1.35; }
    .hu-meta { display: flex; flex-wrap: wrap; gap: 6px; margin: 8px 0 2px; }
    .hu-desc { margin-top: 8px; }
    .hu-desc p { margin: 0 0 6px; }
    .hu-criteria { margin-top: 10px; padding-top: 8px; border-top: 1px dashed var(--line); }
    .hu-criteria > ul, .hu-criteria > ol { margin: 8px 0 4px; }
    .hu-count { margin-left: 8px; color: var(--muted); font-weight: 400; }
    .hu-notes, .hu-rest { margin-top: 10px; font-size: .92rem; }
    .hu-notes p { margin: 2px 0 6px; }
    /* Sprints */
    .sprint-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(290px, 1fr)); gap: 14px; align-items: start; }
    .sprint-box { display: flex; flex-direction: column; gap: 10px; background: var(--panel);
      border: 1px solid var(--line); border-radius: 12px; padding: 16px 18px; }
    .sprint-head { display: flex; align-items: center; gap: 12px; }
    .sprint-num { flex: none; display: grid; place-items: center; width: 38px; height: 38px; border-radius: 10px;
      background: var(--accent); color: var(--panel); font-weight: 700; font-size: 1.1rem; font-variant-numeric: tabular-nums; }
    .sprint-title { margin: 0; font-size: 1rem; }
    .sprint-sub { color: var(--text-soft); font-weight: 400; }
    .sprint-dates { margin: 2px 0 0; color: var(--muted); font-size: .84rem; font-variant-numeric: tabular-nums; }
    .sprint-goal, .sprint-units { font-size: .94rem; color: var(--text-soft); }
    .load-bar { height: 8px; border-radius: 999px; background: var(--panel-soft); border: 1px solid var(--line); overflow: hidden; }
    .load-bar span { display: block; height: 100%; background: var(--good); }
    .load-over .load-bar span { background: var(--critical); }
    .load-low .load-bar span { background: var(--caution); }
    .load-text { margin: 6px 0 0; font-size: .86rem; color: var(--text-soft); max-width: none; }
    .load-over .load-text strong { color: var(--critical); }
    .load-src { color: var(--muted); }
    .sprint-more { font-size: .92rem; }
    /* Roadmap */
    .rm-node { background: var(--panel); border: 1px solid var(--line); border-radius: 10px; padding: 12px 14px; }
    .rm-node.st-done { border-left: 4px solid var(--good); }
    .rm-node.st-doing { border-left: 4px solid var(--caution); }
    .rm-barrier-node { border-style: dashed; border-color: var(--barrier);
      background: color-mix(in srgb, var(--barrier) 7%, var(--panel)); }
    .rm-node-head { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; }
    .rm-name { margin: 6px 0 2px; color: var(--text); font-weight: 600; }
    .rm-obj { margin: 0 0 4px; font-size: .92rem; }
    .rm-meta { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; margin-top: 6px; }
    .rm-deps { margin: 8px 0 0; font-size: .86rem; max-width: none; }
    .rm-state { font-size: .76rem; font-weight: 600; padding: 1px 8px; border-radius: 999px; }
    .rm-state.st-done { color: var(--good); background: color-mix(in srgb, var(--good) 14%, transparent); }
    .rm-state.st-doing { color: var(--caution); background: color-mix(in srgb, var(--caution) 14%, transparent); }
    .rm-state.st-todo, .rm-state.st-other { color: var(--muted); background: var(--panel-soft); }
    .rm-more { margin-top: 8px; font-size: .9rem; }
    .rm-line { list-style: none; margin: 0; padding: 0 0 0 22px; border-left: 2px solid var(--line-strong); }
    .rm-step { position: relative; margin: 0 0 12px; }
    .rm-step::before { content: ""; position: absolute; left: -29px; top: 16px; width: 12px; height: 12px;
      border-radius: 50%; background: var(--panel); border: 2px solid var(--accent); }
    .rm-waves { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 16px; }
    .rm-wave-head { display: flex; align-items: baseline; gap: 10px; margin-bottom: 8px; }
    .rm-wave-num { font-weight: 700; color: var(--barrier); }
    .rm-wave-sub { color: var(--muted); font-size: .86rem; }
    .rm-row { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 10px; align-items: start; }
    .rm-scroll { overflow-x: auto; }
    .rm-lanes { display: flex; flex-direction: column; gap: 10px; min-width: calc(var(--lanes) * 230px); }
    .rm-lane-heads, .rm-tramo { display: grid; grid-template-columns: repeat(var(--lanes), minmax(220px, 1fr)); gap: 10px; }
    .rm-lane-head { padding: 4px 10px; border-bottom: 2px solid var(--lane); color: var(--lane);
      font-family: "SF Mono",Menlo,monospace; font-weight: 700; }
    .rm-col { display: flex; flex-direction: column; gap: 10px; }
    .rm-loose-title { margin: 14px 0 6px; color: var(--muted); font-size: .86rem; }
    @media print { .hu-card, .sprint-box, .rm-node { break-inside: avoid; } }
"""

# Al imprimir, lo plegado se despliega: una tarjeta impresa con los criterios
# ocultos es una tarjeta sin criterios.
SHAPE_JS = ("window.addEventListener('beforeprint', function () {"
            " document.querySelectorAll('details').forEach(function (d) { d.open = true; }); });")


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


STAMP_LINE_RE = re.compile(r"^>\s*(\*\*Versi[oó]n\s+\d+\*\*.*?Generado.*)$", re.MULTILINE)

# Dark palette, shared by the OS preference (auto) and the manual [data-theme="dark"]
# override set by the theme-toggle button.
DARK_VARS = """
        --bg: #0f1623; --panel: #161f2f; --panel-soft: #1b2536;
        --text: #e6ebf4; --text-soft: #c2cad8; --muted: #94a0b3;
        --line: #28324a; --line-strong: #364260;
        --accent: #4dd0e1; --accent-soft: #143038; --code-bg: #1f2940;
        --shadow: 0 1px 2px rgba(0,0,0,.35), 0 1px 3px rgba(0,0,0,.25);
        --rf: #35c4d6; --nfr: #a99bff; --us: #4dd0e1; --must: #ff6b74;
        --block: #ff7a8a; --warn: #f6d784; --essential: #ff8f4d;
        --prio-high: #ff6b74; --prio-mid: #ffb340; --prio-low: #7fd07f;
        --eff-xs: #5fd0a8; --eff-s: #7fd07f; --eff-m: #ffb340; --eff-l: #ff6b74; --eff-xl: #ff9aa2;
        --lane: #8fd694; --barrier: #ffb340;
        --good: #7fd07f; --caution: #f6c56b; --critical: #ff6b74;
"""


def build_html(title: str, doc_type: str, markdown: str) -> str:
    # The stamp_doc.py version/timestamp line ("> **Version N** - **Generado:** ...")
    # belongs in the header, next to the doc badges -- not as a stray blockquote.
    stamp_html = ""
    stamp_match = STAMP_LINE_RE.search(markdown)
    if stamp_match:
        stamp_html = (
            '<span class="dot">&middot;</span> <span class="stamp">'
            + inline_markdown(stamp_match.group(1).strip(), chips=False)
            + "</span> "
        )
        markdown = STAMP_LINE_RE.sub("", markdown, count=1)

    shaped, components = shape(markdown, doc_type)
    body, toc = markdown_to_html(shaped, components)
    toc_html = build_toc(toc)
    kpi_html = build_kpi_html(build_kpis(markdown, doc_type))
    meta = DOC_TYPES.get(doc_type, {"label": "Documento AIDD", "phase": ""})
    generated = date.today().isoformat()
    subtitle = (
        f'<p class="doc-meta"><span class="badge">{html.escape(meta["label"])}</span> '
        + (f'<span class="badge badge-soft">{html.escape(meta["phase"])}</span> ' if meta["phase"] else "")
        + stamp_html
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
      --lane: #2f7d4f; --barrier: #d98a00;
      --good: #2f7d4f; --caution: #b7791f; --critical: #c1121f;
    }}
    @media (prefers-color-scheme: dark) {{
      :root:not([data-theme="light"]) {{ {DARK_VARS} }}
    }}
    :root[data-theme="dark"] {{ {DARK_VARS} }}
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
    .doc-meta .stamp strong {{ color: var(--accent); }}
    hr {{ border: 0; border-top: 1px solid var(--line); margin: 28px 0; }}
    li.task {{ list-style: none; margin-left: -20px; }}
    li.task input {{ accent-color: var(--accent); margin-right: 6px; vertical-align: -.1em; }}
    .theme-toggle {{ position: fixed; top: 14px; right: 16px; z-index: 10;
      width: 36px; height: 36px; border-radius: 999px; border: 1px solid var(--line-strong);
      background: var(--panel); color: var(--text-soft); font-size: 1rem; cursor: pointer;
      box-shadow: var(--shadow); line-height: 1; }}
    .theme-toggle:hover {{ color: var(--accent); border-color: var(--accent); }}
    .diagram.offline::after {{ content: "Diagrama Mermaid sin renderizar (falta mermaid.min.js junto al HTML y la CDN no responde; el codigo fuente se muestra arriba)";
      display: block; margin-top: 10px; font-size: .8rem; color: var(--warn); }}
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
    .kpi-eff {{ border-left-color: var(--eff-m); }} .kpi-eff .kpi-value {{ color: var(--eff-m); }}
    .kpi-lane {{ border-left-color: var(--lane); }} .kpi-lane .kpi-value {{ color: var(--lane); }}
    .kpi-barrier {{ border-left-color: var(--barrier); }} .kpi-barrier .kpi-value {{ color: var(--barrier); }}
    /* Chips */
    .chip {{ display: inline-block; font-size: .74rem; font-weight: 600; padding: 1px 8px; border-radius: 999px;
      vertical-align: baseline; letter-spacing: .02em; white-space: nowrap;
      border: 1px solid color-mix(in srgb, currentColor 35%, transparent); }}
    .chip-rf {{ color: var(--rf); background: color-mix(in srgb, var(--rf) 12%, transparent); font-family: "SF Mono",Menlo,monospace; }}
    .chip-nfr {{ color: var(--nfr); background: color-mix(in srgb, var(--nfr) 12%, transparent); font-family: "SF Mono",Menlo,monospace; }}
    .chip-us {{ color: var(--us); background: color-mix(in srgb, var(--us) 12%, transparent); font-family: "SF Mono",Menlo,monospace; }}
    .chip-block {{ color: #fff; background: var(--block); border-color: var(--block); text-transform: uppercase; letter-spacing: .05em; }}
    .chip-essential {{ color: #fff; background: var(--essential); border-color: var(--essential); text-transform: uppercase; letter-spacing: .05em; }}
    .chip-lane {{ color: var(--lane); background: color-mix(in srgb, var(--lane) 14%, transparent); font-family: "SF Mono",Menlo,monospace; }}
    .chip-barrier {{ color: #fff; background: var(--barrier); border-color: var(--barrier); font-family: "SF Mono",Menlo,monospace; }}
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
    {SHAPE_CSS}
    @media print {{
      body {{ background: #fff; }} .layout {{ display: block; padding: 0; }} .toc {{ display: none; }}
      .doc-section, .kpi {{ box-shadow: none; break-inside: avoid; }}
    }}
  </style>
</head>
<body>
  <button class="theme-toggle" id="themeToggle" aria-label="Cambiar tema">&#9681;</button>
  <div class="layout">
    {toc_html}
    <main>
{body}
    </main>
  </div>
  <script>
    // Theme toggle (auto -> claro -> oscuro), persisted per browser. Classic script:
    // must keep working even without network (the Mermaid loader lives apart).
    (function () {{
      const KEY = 'booster-docs-theme';
      const btn = document.getElementById('themeToggle');
      const modes = ['auto', 'light', 'dark'];
      const icons = {{ auto: '\\u25D1', light: '\\u2600', dark: '\\u263E' }};
      let mode = localStorage.getItem(KEY);
      if (!modes.includes(mode)) mode = 'auto';
      function apply() {{
        if (mode === 'auto') delete document.documentElement.dataset.theme;
        else document.documentElement.dataset.theme = mode;
        btn.textContent = icons[mode];
        btn.title = 'Tema: ' + mode;
      }}
      btn.addEventListener('click', () => {{
        mode = modes[(modes.indexOf(mode) + 1) % modes.length];
        localStorage.setItem(KEY, mode);
        apply();
      }});
      apply();
    }})();

    // Scroll-spy: highlight the current section in the TOC.
    (function () {{
      const links = [...document.querySelectorAll('.toc a')];
      if (!links.length) return;
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
    }})();
  </script>
  <script>
    // Mermaid loader, best-effort and fail-visible.
    //
    // Uses the SELF-CONTAINED bundle (mermaid.min.js), never the ESM entry: the
    // ESM build lazy-loads one chunk per diagram type at render time, so a single
    // blocked request behind a corporate proxy leaves the diagrams silently blank
    // -- and it fails inside Mermaid's async render, out of reach of any try/catch
    // around the import.
    //
    // Order: the local copy next to this HTML first (works offline, over file://
    // and behind a
    // proxy), then the CDN. Classic <script> tags, so onerror actually fires and
    // the fallback chain is real. If everything fails, the source stays visible
    // with a notice instead of an empty gap.
    (function () {{
      if (!document.querySelector('.mermaid')) return;
      // Same pinned version on both ends, so the CDN fallback cannot drift from
      // the local asset this script provisions.
      var sources = ['{MERMAID_ASSET_NAME}',
                     '{MERMAID_URL}'];
      function fail() {{
        document.querySelectorAll('.diagram').forEach(function (d) {{
          d.classList.add('offline');
        }});
      }}
      function start() {{
        try {{
          var dark = document.documentElement.dataset.theme === 'dark'
            || (document.documentElement.dataset.theme !== 'light'
                && window.matchMedia('(prefers-color-scheme: dark)').matches);
          mermaid.initialize({{ startOnLoad: false, securityLevel: 'strict',
                               theme: dark ? 'dark' : 'default' }});
          // Explicit run() instead of startOnLoad: it returns a promise, so a
          // render error is catchable rather than swallowed.
          mermaid.run({{ querySelector: '.mermaid' }}).catch(fail);
        }} catch (e) {{ fail(); }}
      }}
      function load(i) {{
        if (i >= sources.length) {{ fail(); return; }}
        var s = document.createElement('script');
        s.src = sources[i];
        s.onload = start;
        s.onerror = function () {{ load(i + 1); }};
        document.head.appendChild(s);
      }}
      load(0);
    }})();
  </script>
  <script>{SHAPE_JS}</script>
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
    parser.add_argument(
        "--no-mermaid-asset",
        dest="mermaid_asset",
        action="store_false",
        help=(
            f"Do not provision {MERMAID_ASSET_NAME} next to the HTML (useful in CI). "
            "Diagrams then depend on the CDN at open time."
        ),
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

    # Only when the document actually has diagrams: a doc without Mermaid blocks
    # neither downloads nor copies anything.
    if args.mermaid_asset and has_mermaid_blocks(markdown):
        asset, note = ensure_mermaid_asset(output.parent)
        if asset:
            print(f"Asset Mermaid: {asset} ({note})")
        else:
            print(
                f"ADVERTENCIA: No se pudo dejar {MERMAID_ASSET_NAME} junto al HTML ({note}). "
                "Los diagramas dependeran de la CDN al abrirlo.",
                file=sys.stderr,
            )

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
