#!/usr/bin/env python3
"""El registro de actividad lo escribe uno solo: el hook o el comando.

Los hooks de plugin no se ejecutan en todas partes --medido en Codex CLI 0.151.0
y en Cline--, asi que donde no corren el registro lo escribe `audit.py`. Pero
donde si corren, **los dos escribiendo duplicarian cada linea**, y eso no falla:
infla el tiempo atendido y la aceleracion sale mejor de lo que fue.

De ahi que la fuente se **declare** en `activity.source` de `openspec/config.yaml`
en vez de adivinarse, y que sin la clave se asuma `hooks` --el comportamiento
historico--: preferimos perder una linea a duplicarla.

Esta comprobacion fija las tres ramas y que la linea de turno declare su base
mas estrecha (`scope=comando`), que es lo que impide que `aiba metrics` la
confunda con un turno de verdad.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "plugins" / "aisdd" / "skills" / "aisdd-specs" / "scripts" / "audit.py"

ENTRADA = {
    "command": "aisdd implement change",
    "prompt_version": "test",
    "started_at": "2026-09-03T10:00:00Z",
    "change_id": "un-change",
    "output_files": ["src/app.ts"],
}


def corre(config: str | None) -> list[str]:
    """Ejecuta audit.py en un proyecto limpio y devuelve las lineas del registro."""
    with tempfile.TemporaryDirectory() as d:
        raiz = Path(d)
        (raiz / "openspec").mkdir()
        (raiz / "docs").mkdir()
        (raiz / "src").mkdir()
        (raiz / "src" / "app.ts").write_text("x", encoding="utf-8")
        (raiz / "docs" / "aidd-activity.md").touch()
        if config is not None:
            (raiz / "openspec" / "config.yaml").write_text(config, encoding="utf-8")
        subprocess.run([sys.executable, str(AUDIT), "--root", str(raiz)],
                       input=json.dumps(ENTRADA), text=True,
                       capture_output=True, timeout=60)
        log = raiz / "docs" / "aidd-activity.md"
        return [l for l in log.read_text(encoding="utf-8").splitlines() if l.startswith("- ")]


errors: list[str] = []

casos = {
    "sin config (historico)": (None, 0),
    "activity.source: hooks": ("activity:\n  source: hooks\n", 0),
    "activity.source: skills": ("activity:\n  source: skills\n", 3),
}
for nombre, (cfg, esperadas) in casos.items():
    try:
        lineas = corre(cfg)
    except Exception as exc:                                    # noqa: BLE001
        errors.append(f"{nombre}: audit.py no se pudo ejecutar ({exc})")
        continue
    if len(lineas) != esperadas:
        errors.append(f"{nombre}: {len(lineas)} lineas en el registro, se esperaban "
                      f"{esperadas} ({'duplicaria al hook' if lineas else 'no registra nada'})")
        continue
    if esperadas and not any("scope=comando" in l for l in lineas):
        errors.append(f"{nombre}: la linea de turno no declara `scope=comando`, "
                      f"asi que se leeria como un turno completo y el tiempo "
                      f"atendido saldria mal")

if errors:
    print("El registro de actividad no reparte bien quien escribe:", file=sys.stderr)
    for e in errors:
        print(f"  - {e}", file=sys.stderr)
    sys.exit(1)
print(f"Fuente del registro coherente en {len(casos)} casos: "
      f"con hooks no escribe, sin hooks escribe y declara su base.")
