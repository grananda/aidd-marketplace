#!/usr/bin/env python3
"""Compute AI-usage KPIs for an AIDD/AISDD project from measured data.

Reads three sources and never guesses beyond them:

  * ``docs/aidd-activity.md``  -- the activity log written by ``aidd-activity-hook.sh``:
    which skill ran, which files the AI wrote, and how long each turn lasted.
    This is the *measured* side.
  * ``git log``                -- commits and lines of code in the same window.
  * ``docs/detalle-historias-usuario.md`` -- the XS/S/M/L/XL sizes, which give the
    *baseline*: what the same scope was estimated to cost a human, declared
    before execution (that is what makes it a legitimate counterfactual rather
    than a retro-fitted one).

The comparison the report is built on:

    ahorro = esfuerzo humano estimado (baseline)  -  tiempo atendido medido

"Tiempo atendido" is the sum of turn durations: the human sent a request and
waited for it. It is NOT wall-clock across the calendar (which would count
nights and meetings) and it is NOT pure machine time. It is the closest honest
proxy for person-hours available without telemetry.

What this script deliberately does NOT do: invent a quality dimension, estimate
what it cannot measure, or count the code the human typed by hand (that never
goes through the AI's tools, so the log cannot see it -- by design).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

# --- The AIDD size scale (1 d = 8 h working day), same points as the skills ---
EFFORT_DAYS = {"XS": 0.5, "S": 1.5, "M": 3.0, "L": 5.0, "XL": 8.0}
HOURS_PER_DAY = 8.0

# --- Where each skill sits in the process ------------------------------------
# Lets the report split planning from execution, which is the question behind
# "cuanto ahorramos": the two compress very differently.
SKILL_STAGE = {
    "aidd-client-requirements": ("Definicion", "Fase 0"),
    "aidd-requirements": ("Definicion", "Fase 1.1"),
    "aidd-user-stories": ("Definicion", "Fase 1.2"),
    "aidd-user-story-details": ("Definicion", "Fase 1.3"),
    "aidd-hu-review-plan": ("Definicion", "Fase 1.4"),
    "aidd-prototype-architecture": ("Diseno", "Fase 2.1"),
    "aidd-prototype": ("Diseno", "Fase 2.2"),
    "aidd-style-guide": ("Diseno", "Fase 2.3"),
    "aidd-architecture-proposal": ("Diseno", "Fase 2.3"),
    "aidd-architecture": ("Diseno", "Fase 2.4"),
    "aidd-project-plan": ("Entrega", "Fase 3.5.1"),
    "aidd-sprint-planning": ("Entrega", "Fase 3.5.2"),
    "aidd-metrics": ("Soporte", "KPIs"),
    "aisdd-specs": ("Ejecucion", "Fase 3"),
    "booster-docs": ("Soporte", "Booster"),
    "booster-uml": ("Soporte", "Booster"),
    "booster-ux": ("Soporte", "Booster"),
}

LINE_RE = re.compile(
    r"^-\s+(?P<ts>\S+)\s+\|\s+user:(?P<user>[^|]*?)\s+\|\s+skill:(?P<skill>[^|]*?)\s+"
    r"\|\s+ctx:(?P<ctx>[^|]*?)\s+\|\s+(?P<action>[^|]*?)\s+\|\s+note:(?P<note>.*)$"
)
DUR_RE = re.compile(r"\bdur=(\d+)s\b")
# Same inline-size matcher the HTML renderer uses, so both read the sizes alike.
EFFORT_INLINE_RE = re.compile(r"(Estimaci[oó]n(?:\s|:|\*){0,6})(XS|XL|S|M|L)\b")


def parse_ts(value: str) -> datetime | None:
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def stage_of(skill: str) -> tuple[str, str]:
    """Map a namespaced skill (``aidd:aidd-requirements``) to (stage, phase)."""
    bare = skill.split(":")[-1]
    if bare in SKILL_STAGE:
        return SKILL_STAGE[bare]
    if bare.startswith("aiad-"):
        return ("Ejecucion", "Human-first")
    if bare.startswith("booster-"):
        return ("Soporte", "Booster")
    return ("Otros", "-")


class Activity:
    """The measured side: everything parsed out of the activity log."""

    def __init__(self) -> None:
        self.runs: list[dict] = []
        self.files: list[dict] = []
        self.turns: list[dict] = []
        self.skipped = 0

    @property
    def empty(self) -> bool:
        return not (self.runs or self.files or self.turns)

    def load(self, path: Path) -> None:
        for raw in path.read_text(encoding="utf-8").splitlines():
            if not raw.startswith("- "):
                continue
            m = LINE_RE.match(raw.strip())
            if not m:
                self.skipped += 1
                continue
            ts = parse_ts(m.group("ts"))
            if ts is None:
                self.skipped += 1
                continue
            entry = {
                "ts": ts,
                "user": m.group("user").strip(),
                "skill": m.group("skill").strip(),
                "ctx": m.group("ctx").strip(),
                "note": m.group("note").strip(),
            }
            action = m.group("action").strip()
            if action == "run":
                self.runs.append(entry)
            elif action.startswith("file:"):
                entry["file"] = action[len("file:"):].strip()
                self.files.append(entry)
            elif action == "turn":
                d = DUR_RE.search(entry["note"])
                entry["dur"] = int(d.group(1)) if d else None
                self.turns.append(entry)


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    k = (len(ordered) - 1) * pct
    lo, hi = int(k), min(int(k) + 1, len(ordered) - 1)
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (k - lo)


def read_baseline_days(details: Path) -> tuple[float, int]:
    """Human baseline in person-days from the XS/S/M/L/XL sizes of the stories.

    Mirrors the renderer: prefer inline ``Estimacion: <talla>`` labels and fall
    back to standalone size cells in tables, never both (a story's inline size
    usually reappears in a summary table and would double-count).
    """
    if not details.is_file():
        return (0.0, 0)
    text = details.read_text(encoding="utf-8")
    sizes = [m.group(2).upper() for m in EFFORT_INLINE_RE.finditer(text)]
    if not sizes:
        for line in text.splitlines():
            t = line.strip()
            if t.startswith("|") and t.endswith("|"):
                for cell in t.strip("|").split("|"):
                    if cell.strip() in EFFORT_DAYS:
                        sizes.append(cell.strip())
    return (sum(EFFORT_DAYS[s] for s in sizes), len(sizes))


def git_stats(repo: Path, since: datetime | None, until: datetime | None) -> dict:
    """Commits and lines of code inside the measured window (best-effort)."""
    out = {"available": False, "commits": 0, "added": 0, "removed": 0, "authors": {}}
    cmd = ["git", "-C", str(repo), "log", "--numstat", "--no-merges",
           "--pretty=format:%x01%H%x02%aI%x02%an"]
    if since:
        cmd.append(f"--since={since.isoformat()}")
    if until:
        cmd.append(f"--until={until.isoformat()}")
    try:
        raw = subprocess.run(cmd, capture_output=True, text=True, timeout=30, check=False)
    except (OSError, subprocess.SubprocessError):
        return out
    if raw.returncode != 0:
        return out
    out["available"] = True
    authors: Counter = Counter()
    for block in raw.stdout.split("\x01"):
        if not block.strip():
            continue
        head, _, body = block.partition("\n")
        parts = head.split("\x02")
        if len(parts) < 3:
            continue
        out["commits"] += 1
        authors[parts[2]] += 1
        for line in body.splitlines():
            cols = line.split("\t")
            if len(cols) == 3 and cols[0].isdigit() and cols[1].isdigit():
                out["added"] += int(cols[0])
                out["removed"] += int(cols[1])
    out["authors"] = dict(authors.most_common())
    return out


def read_audit(audit_dir: Path, since: datetime | None, until: datetime | None) -> dict:
    """The AISDD side: what the structured audit log records about each change.

    ``openspec/audit/*.jsonl`` is append-only, one entry per ``aisdd`` command.
    It is the only source that sees the *specification* side of the work: how
    many doubts the pre-flight raised, how many the agent resolved alone, and
    how many corrections a change needed once its specs were supposedly closed.

    Corrections are the quality counterpart to churn. Churn measures code that
    had to be rewritten; corrections measure specs that turned out to be wrong.
    A change can have low churn and bad specs (the developer guessed well), or
    high churn from a legitimate refactor. They diagnose different things.

    The count is a FLOOR, never exact: it only sees corrections that were
    actually recorded. The report must say so.
    """
    out: dict = {"available": False, "path": str(audit_dir)}
    if not audit_dir.is_dir():
        return out
    files = sorted(audit_dir.glob("*.jsonl"))
    if not files:
        return out

    parsed, malformed, in_window = 0, 0, []
    for path in files:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                malformed += 1
                continue
            if not isinstance(entry, dict):
                malformed += 1
                continue
            ts = parse_ts(str(entry.get("timestamp", "")))
            if ts is None:
                malformed += 1
                continue
            parsed += 1
            if (since and ts < since) or (until and ts > until):
                continue
            entry["_ts"] = ts
            in_window.append(entry)

    out.update({"available": True, "files": len(files), "entries_total": parsed,
                "entries_in_window": len(in_window), "malformed": malformed})
    if not in_window:
        return out

    commands: Counter = Counter()
    changes: dict[str, dict] = defaultdict(
        lambda: {"commands": 0, "decisions": 0, "corrections": 0, "auto_defaults": 0,
                 "opened": None, "closed": None, "status_issues": 0})
    corrections = decisions_total = auto_defaults = status_issues = 0

    for e in in_window:
        command = str(e.get("command") or "desconocido")
        commands[command] += 1
        if str(e.get("status") or "ok") != "ok":
            status_issues += 1

        change_id = e.get("change_id")
        slug = str(change_id) if change_id else None
        if slug:
            c = changes[slug]
            c["commands"] += 1
            if str(e.get("status") or "ok") != "ok":
                c["status_issues"] += 1
            if command.endswith("open change"):
                c["opened"] = min(c["opened"], e["_ts"]) if c["opened"] else e["_ts"]
            elif command.endswith("close change"):
                c["closed"] = max(c["closed"], e["_ts"]) if c["closed"] else e["_ts"]

        for d in e.get("decisions") or []:
            if not isinstance(d, dict):
                continue
            decisions_total += 1
            is_correction = str(d.get("type") or "") == "correccion"
            is_auto = str(d.get("origen") or "") == "auto-default"
            corrections += int(is_correction)
            auto_defaults += int(is_auto)
            if slug:
                changes[slug]["decisions"] += 1
                changes[slug]["corrections"] += int(is_correction)
                changes[slug]["auto_defaults"] += int(is_auto)

    lead_times: list[float] = []
    for slug, c in changes.items():
        if c["opened"] and c["closed"] and c["closed"] >= c["opened"]:
            c["lead_time_s"] = (c["closed"] - c["opened"]).total_seconds()
            lead_times.append(c["lead_time_s"])
        else:
            c["lead_time_s"] = None
        c["opened"] = c["opened"].strftime("%Y-%m-%d") if c["opened"] else None
        c["closed"] = c["closed"].strftime("%Y-%m-%d") if c["closed"] else None

    tracked = len(changes)
    out.update({
        "commands": dict(commands.most_common()),
        "changes": dict(sorted(changes.items())),
        "changes_tracked": tracked,
        "changes_closed": sum(1 for c in changes.values() if c["closed"]),
        "changes_open": sorted(s for s, c in changes.items() if not c["closed"]),
        "corrections_total": corrections,
        "corrections_per_change": (corrections / tracked) if tracked else 0.0,
        "changes_with_corrections": sum(1 for c in changes.values() if c["corrections"]),
        "decisions_total": decisions_total,
        "auto_defaults": auto_defaults,
        "auto_default_pct": (auto_defaults / decisions_total * 100) if decisions_total else 0.0,
        "status_issues": status_issues,
        "lead_time_p50_s": percentile(lead_times, 50) if lead_times else 0.0,
        "lead_times_measured": len(lead_times),
    })
    return out


def fmt_hours(seconds: float) -> str:
    hours = seconds / 3600.0
    if hours < 1:
        return f"{seconds / 60:.0f} min"
    return f"{hours:.1f} h"


def build_facts(act: Activity, baseline_days: float, sized_items: int, git: dict,
                real_days: float | None = None, cost_per_day: float | None = None,
                audit: dict | None = None) -> dict:
    stamps = [e["ts"] for e in (act.runs + act.files + act.turns)]
    first, last = (min(stamps), max(stamps)) if stamps else (None, None)

    durations = [t["dur"] for t in act.turns if t.get("dur") is not None]
    attended = float(sum(durations))
    attended_days = attended / 3600.0 / HOURS_PER_DAY

    writes = Counter(e["file"] for e in act.files)
    reworked = {f: n for f, n in writes.items() if n > 2}

    by_skill = Counter(e["skill"] for e in act.runs)
    by_stage: Counter = Counter()
    for e in act.runs:
        by_stage[stage_of(e["skill"])[0]] += 1

    # Attended time per stage: attribute each turn to the stage of the last skill
    # invoked at or before it. A turn with no skill inherits the previous one.
    stage_seconds: dict[str, float] = defaultdict(float)
    events = sorted(act.runs + act.turns, key=lambda e: e["ts"])
    current = None
    for e in events:
        if "dur" in e:
            if e["dur"] is not None and current:
                stage_seconds[current] += e["dur"]
        else:
            current = stage_of(e["skill"])[0]

    ctx_stats: dict[str, dict] = {}
    for e in act.runs + act.files + act.turns:
        ctx = e["ctx"]
        if not ctx or ctx == "-":
            continue
        slot = ctx_stats.setdefault(ctx, {"first": e["ts"], "last": e["ts"],
                                          "turns": 0, "files": set(), "seconds": 0.0})
        slot["first"] = min(slot["first"], e["ts"])
        slot["last"] = max(slot["last"], e["ts"])
        if "file" in e:
            slot["files"].add(e["file"])
        if "dur" in e:
            slot["turns"] += 1
            if e["dur"] is not None:
                slot["seconds"] += e["dur"]

    days_active = len({e["ts"].date() for e in (act.runs + act.files + act.turns)})

    facts = {
        "window": {
            "first": first.isoformat() if first else None,
            "last": last.isoformat() if last else None,
            "days_with_activity": days_active,
        },
        "volume": {
            "turns": len(act.turns),
            "skill_runs": len(act.runs),
            "file_writes": len(act.files),
            "files_touched": len(writes),
            "unparsed_lines": act.skipped,
        },
        "attended": {
            "seconds": attended,
            "hours": attended / 3600.0,
            "days": attended_days,
            "turns_measured": len(durations),
            "turns_without_duration": len(act.turns) - len(durations),
            "mean_turn_s": (attended / len(durations)) if durations else 0.0,
            "p50_turn_s": percentile([float(d) for d in durations], 0.5),
            "p90_turn_s": percentile([float(d) for d in durations], 0.9),
            "longest_turn_s": max(durations) if durations else 0,
        },
        "by_skill": by_skill.most_common(),
        "by_stage": {
            "runs": dict(by_stage.most_common()),
            "seconds": {k: v for k, v in sorted(stage_seconds.items(),
                                                key=lambda kv: -kv[1])},
        },
        "rework": {
            "writes_per_file": (len(act.files) / len(writes)) if writes else 0.0,
            "files_rewritten_3plus": len(reworked),
            "top_churn": writes.most_common(10),
        },
        "by_context": {
            k: {
                "first": v["first"].isoformat(),
                "last": v["last"].isoformat(),
                "lead_time_s": (v["last"] - v["first"]).total_seconds(),
                "attended_s": v["seconds"],
                "turns": v["turns"],
                "files": len(v["files"]),
            }
            for k, v in sorted(ctx_stats.items(), key=lambda kv: -kv[1]["seconds"])
        },
        "git": git,
        "audit": audit or {"available": False},
        "baseline": {
            "days": baseline_days,
            "sized_items": sized_items,
            "source": "docs/detalle-historias-usuario.md (escala XS/S/M/L/XL)",
        },
    }

    # --- Ahorro: solo con esfuerzo humano real declarado ---------------------
    # El tiempo atendido NO es el esfuerzo humano total: el registro solo ve los
    # minutos dentro de los turnos de la IA, no leer, revisar, probar, teclear a
    # mano ni reunirse. Restarlo del baseline daria aceleraciones absurdas (x100),
    # asi que el ahorro solo se calcula contra el esfuerzo real que declare el
    # equipo. Sin ese dato se publica actividad medida, no ahorro.
    facts["savings"] = None
    facts["intensity"] = None
    if real_days and real_days > 0:
        facts["intensity"] = {
            "attended_share_pct": min(100.0, (attended_days / real_days) * 100),
            "real_days": real_days,
        }
        if baseline_days > 0:
            saved = baseline_days - real_days
            savings = {
                "baseline_days": baseline_days,
                "real_days": real_days,
                "saved_days": saved,
                "reduction_pct": (1 - real_days / baseline_days) * 100,
                "acceleration": (baseline_days / real_days) if real_days else 0.0,
                "implausible": (baseline_days / real_days) > 10 if real_days else False,
            }
            if cost_per_day and cost_per_day > 0:
                savings["cost_per_day"] = cost_per_day
                savings["saved_cost"] = saved * cost_per_day
            facts["savings"] = savings
    return facts


# --- Markdown rendering ------------------------------------------------------

def md_tables(f: dict) -> str:
    out: list[str] = []
    w, v, a = f["window"], f["volume"], f["attended"]

    out.append("### Ventana medida\n")
    out.append("| Concepto | Valor |")
    out.append("|---|---|")
    out.append(f"| Primera accion registrada | {w['first'] or '-'} |")
    out.append(f"| Ultima accion registrada | {w['last'] or '-'} |")
    out.append(f"| Dias naturales con actividad | {w['days_with_activity']} |")
    out.append(f"| Turnos registrados | {v['turns']} |")
    out.append(f"| Skills ejecutados | {v['skill_runs']} |")
    out.append(f"| Escrituras de fichero por la IA | {v['file_writes']} |")
    out.append(f"| Ficheros distintos tocados | {v['files_touched']} |")
    out.append("")

    out.append("### Tiempo atendido\n")
    out.append("| KPI | Valor |")
    out.append("|---|---|")
    out.append(f"| Tiempo atendido total | {fmt_hours(a['seconds'])} |")
    out.append(f"| Equivalente en jornadas (8 h) | {a['days']:.2f} d |")
    out.append(f"| Turnos con duracion medida | {a['turns_measured']} |")
    out.append(f"| Duracion media por turno | {fmt_hours(a['mean_turn_s'])} |")
    out.append(f"| Mediana (p50) | {fmt_hours(a['p50_turn_s'])} |")
    out.append(f"| p90 | {fmt_hours(a['p90_turn_s'])} |")
    out.append(f"| Turno mas largo | {fmt_hours(a['longest_turn_s'])} |")
    if a["turns_without_duration"]:
        out.append(f"| Turnos sin duracion (no computados) | {a['turns_without_duration']} |")
    out.append("")

    if f["by_stage"]["runs"]:
        out.append("### Reparto planificacion vs ejecucion\n")
        out.append("| Etapa | Skills ejecutados | Tiempo atendido |")
        out.append("|---|---|---|")
        secs = f["by_stage"]["seconds"]
        for stage, runs in f["by_stage"]["runs"].items():
            out.append(f"| {stage} | {runs} | {fmt_hours(secs.get(stage, 0.0))} |")
        out.append("")

    if f["by_skill"]:
        out.append("### Skills mas usados\n")
        out.append("| Skill | Invocaciones |")
        out.append("|---|---|")
        for skill, n in f["by_skill"][:15]:
            out.append(f"| `{skill}` | {n} |")
        out.append("")

    if f["by_context"]:
        out.append("### Por historia de usuario / change\n")
        out.append("| Contexto | Turnos | Tiempo atendido | Lead time | Ficheros |")
        out.append("|---|---|---|---|---|")
        for ctx, s in f["by_context"].items():
            lead = s["lead_time_s"] / 3600.0
            out.append(f"| {ctx} | {s['turns']} | {fmt_hours(s['attended_s'])} "
                       f"| {lead:.1f} h | {s['files']} |")
        out.append("")

    r = f["rework"]
    out.append("### Retrabajo (churn)\n")
    out.append("| KPI | Valor |")
    out.append("|---|---|")
    out.append(f"| Escrituras por fichero (media) | {r['writes_per_file']:.2f} |")
    out.append(f"| Ficheros reescritos 3+ veces | {r['files_rewritten_3plus']} |")
    out.append("")
    if r["top_churn"]:
        out.append("| Fichero | Escrituras |")
        out.append("|---|---|")
        for path, n in r["top_churn"]:
            out.append(f"| `{path}` | {n} |")
        out.append("")

    au = f["audit"]
    if au.get("available") and au.get("entries_in_window"):
        out.append("### Correcciones y ciclo de los changes (auditoria AISDD)\n")
        out.append("| KPI | Valor |")
        out.append("|---|---|")
        out.append(f"| Comandos `aisdd` registrados | {au['entries_in_window']} |")
        out.append(f"| Changes con actividad | {au['changes_tracked']} |")
        out.append(f"| Changes cerrados | {au['changes_closed']} |")
        out.append(f"| Correcciones registradas | {au['corrections_total']} |")
        out.append(f"| Correcciones por change (media) | {au['corrections_per_change']:.2f} |")
        out.append(f"| Changes que necesitaron correccion | "
                   f"{au['changes_with_corrections']} de {au['changes_tracked']} |")
        out.append(f"| Decisiones registradas | {au['decisions_total']} |")
        out.append(f"| Resueltas por la IA sin preguntar | {au['auto_default_pct']:.0f} % |")
        if au.get("lead_times_measured"):
            out.append(f"| Lead time de un change, open->close (p50) | "
                       f"{fmt_hours(au['lead_time_p50_s'])} |")
        if au.get("status_issues"):
            out.append(f"| Comandos no completados (partial/aborted) | {au['status_issues']} |")
        out.append("")

        if au.get("changes"):
            out.append("| Change | Comandos | Decisiones | Correcciones | Lead time | Estado |")
            out.append("|---|---|---|---|---|---|")
            for slug, c in au["changes"].items():
                lead = fmt_hours(c["lead_time_s"]) if c.get("lead_time_s") else "-"
                estado = "cerrado" if c["closed"] else "abierto"
                out.append(f"| `{slug}` | {c['commands']} | {c['decisions']} | "
                           f"{c['corrections']} | {lead} | {estado} |")
            out.append("")

        out.append("> Las correcciones son **retrabajo de especificacion**: lo que el change "
                   "necesito cambiar despues de dar sus specs por cerradas. Complementan al "
                   "churn, que mide retrabajo de *codigo*. Un change puede tener churn bajo "
                   "y specs malas (el desarrollador acerto adivinando) o churn alto por un "
                   "refactor legitimo: diagnostican cosas distintas.")
        out.append("")
        out.append("> **Es una cota inferior.** Solo cuenta las correcciones que llegaron a "
                   "`decisions.md`; las que se resolvieron sin anotar no aparecen. Sirve "
                   "para comparar changes entre si, no como recuento exacto.")
        out.append("")
    elif au.get("available"):
        out.append("### Correcciones y ciclo de los changes (auditoria AISDD)\n")
        out.append(f"Hay auditoria en `{au['path']}` ({au.get('entries_total', 0)} entradas), "
                   "pero ninguna cae dentro de la ventana que mide el registro de actividad. "
                   "No se calculan correcciones.")
        out.append("")

    g = f["git"]
    if g.get("available"):
        out.append("### Codigo entregado en la ventana (git)\n")
        out.append("| KPI | Valor |")
        out.append("|---|---|")
        out.append(f"| Commits | {g['commits']} |")
        out.append(f"| Lineas anadidas | {g['added']} |")
        out.append(f"| Lineas eliminadas | {g['removed']} |")
        if a["hours"] > 0:
            out.append(f"| Lineas netas por hora atendida | "
                       f"{(g['added'] - g['removed']) / a['hours']:.0f} |")
        for author, n in list(g.get("authors", {}).items())[:5]:
            out.append(f"| Commits de {author} | {n} |")
        out.append("")

    b, s, i = f["baseline"], f["savings"], f["intensity"]
    out.append("### Contraste con el baseline humano\n")
    if s:
        out.append("| KPI | Valor |")
        out.append("|---|---|")
        out.append(f"| Esfuerzo humano estimado (baseline) | {b['days']:.1f} d-persona |")
        out.append(f"| Esfuerzo real declarado | {s['real_days']:.2f} d-persona |")
        out.append(f"| Ahorro absoluto | {s['saved_days']:.2f} d-persona |")
        out.append(f"| Reduccion | {s['reduction_pct']:.1f} % |")
        out.append(f"| Factor de aceleracion | x{s['acceleration']:.1f} |")
        if "saved_cost" in s:
            out.append(f"| Ahorro estimado ({s['cost_per_day']:.0f} por jornada) "
                       f"| {s['saved_cost']:,.0f} |")
        if i:
            out.append(f"| Del tiempo real, atendiendo a la IA | "
                       f"{i['attended_share_pct']:.0f} % |")
        out.append("")
        out.append(f"Baseline calculado sobre {b['sized_items']} elementos con talla en "
                   f"`{b['source']}`.")
        if s["implausible"]:
            out.append("")
            out.append("> **Cifra no publicable.** Una aceleracion mayor de x10 casi nunca "
                       "es real: lo habitual es que el esfuerzo real declarado no incluya "
                       "todo el tiempo dedicado (revision, pruebas, reuniones, correcciones) "
                       "o que el baseline estuviera inflado. Revisa ambos antes de usar "
                       "este numero fuera del equipo.")
    else:
        out.append("**No se calcula ahorro.** El registro mide el tiempo *atendido* "
                   f"({fmt_hours(a['seconds'])}, {a['days']:.2f} d), que es solo la parte "
                   "del trabajo que transcurre dentro de los turnos de la IA: no incluye "
                   "leer, revisar, probar, teclear a mano ni reunirse. Restarlo del "
                   "baseline daria aceleraciones absurdas.")
        out.append("")
        out.append("Para obtener ahorro hace falta el **esfuerzo real declarado** por el "
                   "equipo en esta misma ventana (partes de horas, worklogs de Jira o una "
                   "estimacion honesta): pasalo con `--real-days N`. Mientras tanto, el "
                   f"tiempo atendido es una **cota inferior** del trabajo asistido por IA.")
        if b["days"] > 0:
            out.append("")
            out.append(f"Baseline disponible para cuando lo tengas: **{b['days']:.1f} "
                       f"d-persona** sobre {b['sized_items']} elementos con talla.")
        else:
            out.append("")
            out.append("Ademas no hay baseline: no se han encontrado tallas XS/S/M/L/XL en "
                       "`docs/detalle-historias-usuario.md`.")
    out.append("")
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Calcula KPIs medidos de uso de IA para un proyecto AIDD/AISDD.")
    parser.add_argument("--activity", default="docs/aidd-activity.md",
                        help="Registro de actividad (por defecto docs/aidd-activity.md).")
    parser.add_argument("--details", default="docs/detalle-historias-usuario.md",
                        help="Documento con las tallas XS/S/M/L/XL para el baseline.")
    parser.add_argument("--repo", default=".", help="Raiz del repositorio git.")
    parser.add_argument("--baseline-days", type=float,
                        help="Fuerza el baseline en dias-persona en vez de derivarlo de las tallas.")
    parser.add_argument("--real-days", type=float,
                        help="Esfuerzo humano REAL dedicado en la ventana, en dias-persona "
                             "(partes de horas, worklogs). Sin esto no se calcula ahorro: el "
                             "tiempo atendido solo cubre los turnos de la IA.")
    parser.add_argument("--cost-per-day", type=float,
                        help="Coste de una jornada-persona, para traducir el ahorro a dinero.")
    parser.add_argument("--format", choices=["md", "json"], default="md",
                        help="Tablas en Markdown (por defecto) o hechos en JSON.")
    parser.add_argument("--no-git", action="store_true", help="Omite las metricas de git.")
    parser.add_argument("--audit", default="openspec/audit",
                        help="Directorio de auditoria AISDD (por defecto openspec/audit). "
                             "Si no existe, el informe sale igual sin esa seccion.")
    parser.add_argument("--no-audit", action="store_true",
                        help="Omite las metricas de la auditoria AISDD.")
    args = parser.parse_args()

    activity = Path(args.activity)
    if not activity.is_file():
        print(f"ERROR: No existe el registro de actividad: {activity}", file=sys.stderr)
        print("Activalo con `touch docs/aidd-activity.md` y vuelve a intentarlo "
              "cuando haya actividad registrada.", file=sys.stderr)
        return 2

    act = Activity()
    act.load(activity)
    if act.empty:
        print(f"ERROR: {activity} no contiene ninguna entrada legible todavia.", file=sys.stderr)
        return 3

    if args.baseline_days is not None:
        baseline_days, sized = args.baseline_days, 0
    else:
        baseline_days, sized = read_baseline_days(Path(args.details))

    stamps = [e["ts"] for e in (act.runs + act.files + act.turns)]
    git = {"available": False}
    if not args.no_git:
        git = git_stats(Path(args.repo), min(stamps), max(stamps))

    audit = {"available": False}
    if not args.no_audit:
        audit = read_audit(Path(args.audit), min(stamps), max(stamps))

    facts = build_facts(act, baseline_days, sized, git,
                        real_days=args.real_days, cost_per_day=args.cost_per_day,
                        audit=audit)
    if args.baseline_days is not None:
        facts["baseline"]["source"] = "--baseline-days (indicado a mano)"

    if args.format == "json":
        print(json.dumps(facts, indent=2, ensure_ascii=False))
    else:
        print(md_tables(facts))
    if act.skipped:
        print(f"ADVERTENCIA: {act.skipped} lineas del registro no encajan con el "
              "formato esperado y se han ignorado.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
