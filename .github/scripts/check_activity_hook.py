#!/usr/bin/env python3
"""El hook de actividad registra lo mismo en Claude Code y en Codex.

Cada plataforma nombra sus eventos a su manera: Claude Code manda
`PostToolUse`, Codex normaliza a `post_tool_use`. El hook comparaba literales,
asi que bajo Codex **no reconocia ningun evento y salia con 0**: el registro
quedaba vacio y `aiba metrics` publicaba ceros sin ninguna senal de que
faltara nada. No fallaba -- mentia, que es peor.

Esta comprobacion dispara el hook con la misma secuencia escrita de las dos
formas y exige que produzca las mismas lineas. Si alguien vuelve a comparar
literales, o anade un evento cubriendo solo una plataforma, falla aqui y no
tres meses despues al leer un informe.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOOK = ROOT / "plugins" / "aidd" / "hooks" / "aidd-activity-hook.sh"

# La misma secuencia en los dos vocabularios: prompt, escritura, fin de turno.
FORMAS = {
    "claude-code": ("UserPromptSubmit", "PostToolUse", "Stop", "Write"),
    "codex": ("user_prompt_submit", "post_tool_use", "stop", "apply_patch"),
}


def secuencia(ups: str, ptu: str, stop: str, herramienta: str, cwd: str) -> list[dict]:
    return [
        {"hook_event_name": ups, "prompt_id": "p", "session_id": "s", "cwd": cwd},
        {"hook_event_name": ptu, "tool_name": herramienta, "tool_use_id": "u1",
         "session_id": "s", "cwd": cwd,
         "tool_input": {"file_path": "src/app.ts", "content": "x"}},
        {"hook_event_name": stop, "prompt_id": "p", "session_id": "s", "cwd": cwd},
    ]


def corre(nombre: str, forma: tuple) -> list[str]:
    """Ejecuta la secuencia en un proyecto limpio y devuelve las lineas de log."""
    with tempfile.TemporaryDirectory() as proyecto, tempfile.TemporaryDirectory() as tmp:
        docs = Path(proyecto) / "docs"
        docs.mkdir()
        log = docs / "aidd-activity.md"
        log.touch()
        entorno = dict(os.environ, TMPDIR=tmp)
        for evento in secuencia(*forma, cwd=proyecto):
            subprocess.run(["bash", str(HOOK)], input=json.dumps(evento),
                           text=True, cwd=proyecto, env=entorno,
                           capture_output=True, timeout=30)
        return [l for l in log.read_text(encoding="utf-8").splitlines()
                if l.startswith("- ")]


def firma(lineas: list[str]) -> list[str]:
    """Lo comparable: la accion de cada linea, sin marca de tiempo ni duracion."""
    salida = []
    for l in lineas:
        campos = [c.strip() for c in l.split("|")]
        accion = campos[4] if len(campos) > 4 else ""
        # La duracion depende del reloj; el resto de la nota si es estable.
        salida.append(accion.split(" dur=")[0] if accion.startswith("turn") else accion)
    return salida


errors: list[str] = []

if not HOOK.is_file():
    print(f"no existe {HOOK.relative_to(ROOT)}", file=sys.stderr)
    sys.exit(1)

resultados = {}
for nombre, forma in FORMAS.items():
    try:
        resultados[nombre] = firma(corre(nombre, forma))
    except Exception as exc:                                    # noqa: BLE001
        errors.append(f"{nombre}: el hook no se pudo ejecutar ({exc})")

# Una lectura no es actividad sobre el codigo. Va aqui porque el fallback para
# herramientas desconocidas mira si hay ruta de fichero, y una lectura tambien
# la trae: sin esta prueba, ampliar la deteccion inflaria el registro con ruido.
def lectura_no_registra() -> list[str]:
    with tempfile.TemporaryDirectory() as proyecto, tempfile.TemporaryDirectory() as tmp:
        docs = Path(proyecto) / "docs"
        docs.mkdir()
        log = docs / "aidd-activity.md"
        log.touch()
        for payload in (
            {"hook_event_name": "PostToolUse", "tool_name": "Read", "tool_use_id": "r1",
             "session_id": "s", "cwd": proyecto,
             "tool_input": {"file_path": "src/app.ts"}},
            {"hook_event_name": "post_tool_use", "tool_name": "shell", "tool_use_id": "r2",
             "session_id": "s", "cwd": proyecto,
             "tool_input": {"path": "src/app.ts"}},
        ):
            subprocess.run(["bash", str(HOOK)], input=json.dumps(payload), text=True,
                           cwd=proyecto, env=dict(os.environ, TMPDIR=tmp),
                           capture_output=True, timeout=30)
        return [l for l in log.read_text(encoding="utf-8").splitlines()
                if l.startswith("- ")]


if not errors:
    sobra = lectura_no_registra()
    if sobra:
        errors.append(f"una lectura quedo registrada como actividad: {sobra}")

if not errors:
    esperado = ["file:src/app.ts", "turn"]
    for nombre, obtenido in resultados.items():
        if obtenido != esperado:
            errors.append(f"{nombre}: registro {obtenido}, se esperaba {esperado}")
    if len(set(map(tuple, resultados.values()))) > 1:
        detalle = " vs ".join(f"{k}={v}" for k, v in resultados.items())
        errors.append(f"las plataformas no registran lo mismo -> {detalle}")

if errors:
    print("El hook de actividad no es agnostico de plataforma:", file=sys.stderr)
    for e in errors:
        print(f"  - {e}", file=sys.stderr)
    sys.exit(1)
print(f"Hook de actividad coherente en {len(FORMAS)} plataformas: "
      f"{' y '.join(FORMAS)} registran las mismas lineas.")
