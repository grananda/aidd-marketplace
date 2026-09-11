#!/usr/bin/env python3
"""Los sprints del plan y en que punto del calendario esta el proyecto.

Vive en los scripts compartidos del plugin porque lo leen dos skills:
`aiba-status-report`, para el avance previsto, y `aiba-onboarding`, para decirle
a quien llega en que sprint estamos. Dos lectores del mismo fichero con dos
expresiones distintas acabarian discrepando el dia que `aiba sprint-planning`
cambie el formato de sus titulos, y ninguno de los dos fallaria: simplemente
dejarian de reconocer sprints.

Se importa como `branding.py`: los scripts de los skills anaden
`parents[3] / "scripts"` al `sys.path`.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

# `### Sprint 2 — (08/09/2026 a 19/09/2026)`, que es como titula los sprints
# `aiba sprint-planning`. El rango de fechas es opcional.
SPRINT_RE = re.compile(
    r"^#{2,4}\s*(Sprint\s*[0-9]+[^\n|]{0,60}?)\s*(?:[—–-]\s*)?"
    r"(?:\(?\s*(\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?)\s*(?:a|–|—|-|hasta)\s*"
    r"(\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?)\s*\)?)?\s*$",
    re.M)


def leer_sprints(root: Path) -> tuple[list[dict], str | None]:
    """Sprints y sus fechas del plan de sprints.

    Es markdown escrito por otro skill, no un formato de datos: se extrae lo que
    se reconoce con seguridad --el nombre y, si esta, el rango de fechas-- y lo
    demas se deja vacio en vez de adivinarse.
    """
    f = root / "docs" / "sprint-plan.md"
    if not f.is_file():
        return [], "no existe docs/sprint-plan.md"
    texto = f.read_text(encoding="utf-8", errors="replace")
    sprints = []
    for m in SPRINT_RE.finditer(texto):
        sprints.append({"nombre": m.group(1).strip(),
                        "desde": m.group(2) or "", "hasta": m.group(3) or ""})
    if not sprints:
        return [], "docs/sprint-plan.md existe pero no se reconocio ningun sprint"
    return sprints, None


def _fecha(txt: str, hoy: date) -> date | None:
    """`19/09/2026`, `19-09-26` o `19/09` -> fecha. Sin ano, se asume el actual."""
    if not txt:
        return None
    p = re.split(r"[/-]", txt.strip())
    try:
        d, m = int(p[0]), int(p[1])
        a = int(p[2]) if len(p) > 2 else hoy.year
        if a < 100:
            a += 2000
        return date(a, m, d)
    except (ValueError, IndexError):
        return None


def clasificar_sprints(sprints: list, hoy: date) -> dict:
    """Que sprints han terminado, cual esta en curso y cual viene despues.

    Un sprint sin fechas no se clasifica: no se sabe si ya paso, y suponerlo
    colocaria al proyecto en un punto del calendario que nadie ha fijado.
    """
    cerrados, actual, siguiente = [], None, None
    for s in sprints:
        fin = _fecha(s.get("hasta", ""), hoy)
        ini = _fecha(s.get("desde", ""), hoy)
        if fin and fin < hoy:
            cerrados.append(s["nombre"])
        elif ini and ini <= hoy and (not fin or fin >= hoy):
            actual = s["nombre"]
        elif ini and ini > hoy and siguiente is None:
            siguiente = s["nombre"]
    return {"cerrados": cerrados, "actual": actual, "siguiente": siguiente}
