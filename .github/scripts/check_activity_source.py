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


def corre(config: str | None, plugin_root: str = "") -> list[str]:
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
        import os                                               # noqa: PLC0415
        subprocess.run([sys.executable, str(AUDIT), "--root", str(raiz)],
                       input=json.dumps(ENTRADA), text=True,
                       env=dict(os.environ, CLAUDE_PLUGIN_ROOT=plugin_root),
                       capture_output=True, timeout=60)
        log = raiz / "docs" / "aidd-activity.md"
        return [l for l in log.read_text(encoding="utf-8").splitlines() if l.startswith("- ")]


errors: list[str] = []

# `plugin_root` no vacio simula un agente que **si** ejecuta los hooks de plugin
# (Claude Code); vacio simula Codex o Cline, donde no se ejecutan.
casos = {
    # Sin clave se resuelve por ejecucion: es el caso de todos los proyectos ya
    # inicializados, y el que dejaba a Cline y a Codex sin registrar nada.
    "sin config, agente con hooks":  (None, "/ruta/plugin", 0),
    "sin config, agente sin hooks":  (None, "", 3),
    "auto, agente con hooks":        ("activity:\n  source: auto\n", "/ruta/plugin", 0),
    "auto, agente sin hooks":        ("activity:\n  source: auto\n", "", 3),
    # Anulaciones explicitas: se respetan, aunque contradigan a la plataforma.
    "hooks explicito":               ("activity:\n  source: hooks\n", "/ruta/plugin", 0),
    "skills explicito":              ("activity:\n  source: skills\n", "", 3),
}
for nombre, (cfg, root, esperadas) in casos.items():
    try:
        lineas = corre(cfg, root)
    except Exception as exc:                                    # noqa: BLE001
        errors.append(f"{nombre}: audit.py no se pudo ejecutar ({exc})")
        continue
    if len(lineas) != esperadas:
        errors.append(f"{nombre}: {len(lineas)} lineas en el registro, se esperaban "
                      f"{esperadas} ({'duplicaria al hook' if lineas else 'no registra nada'})")
        continue
    if esperadas:
        # La linea lleva el **nombre del skill**, no el comando: `compute_kpis`
        # clasifica por skill, y con el comando entero cada linea caeria en
        # "Otros" y se perderia el desglose por etapa sin que nada avisara.
        sys.path.insert(0, str(ROOT / "plugins/aiba/skills/aiba-metrics/scripts"))
        import compute_kpis                                     # noqa: PLC0415
        for l in lineas:
            skill = l.split("| skill:")[1].split("|")[0].strip()
            if compute_kpis.stage_of(skill)[0] == "Otros":
                errors.append(f"{nombre}: la linea usa skill '{skill}', que "
                              f"`compute_kpis` no sabe clasificar (cae en 'Otros')")
                break

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
