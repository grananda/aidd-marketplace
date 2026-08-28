#!/usr/bin/env python3
"""aisdd-specs · audit.py — entrada de auditoría estructurada en JSON Lines.

Escribe una entrada en ``openspec/audit/YYYY-MM.jsonl`` calculando los hashes
SHA-256 de los ficheros de entrada y salida, y aplicando la purga por retención.

Sustituye a la mecánica que vivía como prosa en ``SKILL.md``. La fórmula del
hash agregado, la retención y el formato son exactamente los que ese documento
especifica; la diferencia es que aquí se ejecutan igual todas las veces. Un
registro de auditoría que el modelo compone a mano deja de ser auditable en
cuanto se equivoca una vez, y no hay forma de saber cuándo pasó.

El agente aporta lo que solo él sabe (comando, modelo, decisiones, listas de
ficheros); el script rellena ``id``, ``timestamp`` y los hashes, y persiste.

Uso:
    python audit.py --entry <entry.json> [--root <dir>]
    echo '<json>' | python audit.py [--root <dir>]

Campos admitidos en el JSON de entrada: command, change_id, skill_version,
prompt_version, model, platform, user, input_files[], output_files[],
decisions[], status, errors[], correction_of, id, timestamp.

``input_files`` y ``output_files`` son listas de **rutas relativas** a la raíz
del proyecto; el script las convierte en ``[{path, sha256}]``. Un fichero que no
exista no aborta: se omite de la lista y se reporta en ``warnings``, porque
perder la entrada entera por una ruta mal escrita es peor que registrarla
incompleta y avisar.

Salida (stdout): JSON con {"audit_file", "id", "warnings"}.

Solo biblioteca estándar.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
DEFAULT_RETENTION_DAYS = 365
MIN_RETENTION_DAYS = 30
VALID_STATUS = ("ok", "partial", "aborted")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def hash_file_list(root: Path, rel_paths, warnings: list[str]) -> tuple[list[dict], str]:
    """[{path, sha256}] + hash agregado, según la fórmula del SKILL.md.

    Agregado = SHA-256 del string '<path>\\n<sha256>\\n' concatenado en orden
    alfabético ascendente por path. Lista vacía -> hash del string vacío.
    """
    files: list[dict] = []
    for rel in rel_paths or []:
        norm = str(rel).replace("\\", "/").lstrip("./")
        abs_path = root / norm
        if not abs_path.is_file():
            warnings.append(f"no existe, omitido: {norm}")
            continue
        files.append({"path": norm, "sha256": sha256_file(abs_path)})
    files.sort(key=lambda f: f["path"])
    if not files:
        return [], EMPTY_SHA256
    concat = "".join(f"{f['path']}\n{f['sha256']}\n" for f in files)
    return files, hashlib.sha256(concat.encode("utf-8")).hexdigest()


def resolve_retention_days(root: Path, warnings: list[str]) -> int:
    """config.yaml (audit.retention_days) > openspec/audit/.retention > 365."""
    cfg = root / "openspec" / "config.yaml"
    if cfg.is_file():
        for line in cfg.read_text(encoding="utf-8", errors="replace").splitlines():
            stripped = line.strip()
            if stripped.startswith("retention_days:"):
                value = stripped.split(":", 1)[1].strip()
                if value.isdigit():
                    return clamp_retention(int(value), warnings)
    marker = root / "openspec" / "audit" / ".retention"
    if marker.is_file():
        first = marker.read_text(encoding="utf-8", errors="replace").strip().splitlines()
        if first and first[0].strip().isdigit():
            return clamp_retention(int(first[0].strip()), warnings)
    return DEFAULT_RETENTION_DAYS


def clamp_retention(days: int, warnings: list[str]) -> int:
    if days < MIN_RETENTION_DAYS:
        warnings.append(f"retencion {days} d por debajo del minimo; se usa {MIN_RETENTION_DAYS}")
        return MIN_RETENTION_DAYS
    return days


def purge(audit_dir: Path, retention_days: int, now: datetime, warnings: list[str]) -> list[str]:
    """Borra los .jsonl cuyo mes terminó antes del corte. Purga por meses completos."""
    removed: list[str] = []
    if not audit_dir.is_dir():
        return removed
    cutoff = now.timestamp() - retention_days * 86400
    for f in sorted(audit_dir.glob("*.jsonl")):
        try:
            year, month = (int(p) for p in f.stem.split("-"))
        except ValueError:
            continue  # nombre ajeno al esquema YYYY-MM: no es nuestro, no se toca
        if not 1 <= month <= 12:
            continue  # '2026-13.jsonl' no lo generamos nosotros
        end = datetime(year + month // 12, month % 12 + 1, 1, tzinfo=timezone.utc)
        if end.timestamp() < cutoff:
            try:
                f.unlink()
                removed.append(f.name)
            except OSError as exc:
                warnings.append(f"no se pudo purgar {f.name}: {exc}")
    return removed


def main() -> int:
    ap = argparse.ArgumentParser(description="Entrada de auditoria de aisdd-specs.")
    ap.add_argument("--root", default=".", help="raíz del proyecto (default: cwd)")
    ap.add_argument("--entry", default=None, help="fichero JSON con la entrada; sin él, stdin")
    args = ap.parse_args()

    raw = Path(args.entry).read_text(encoding="utf-8") if args.entry else sys.stdin.read()
    try:
        entry = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"error: JSON invalido: {exc}", file=sys.stderr)
        return 2
    if not isinstance(entry, dict) or not entry.get("command"):
        print("error: falta el campo obligatorio 'command'", file=sys.stderr)
        return 2

    root = Path(args.root).resolve()
    warnings: list[str] = []
    now = datetime.now(timezone.utc)

    in_files, in_hash = hash_file_list(root, entry.get("input_files"), warnings)
    out_files, out_hash = hash_file_list(root, entry.get("output_files"), warnings)

    status = entry.get("status", "ok")
    if status not in VALID_STATUS:
        warnings.append(f"status '{status}' no valido; se registra como 'partial'")
        status = "partial"

    record = {
        "id": entry.get("id") or str(uuid.uuid4()),
        "timestamp": entry.get("timestamp") or now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "command": entry["command"],
        "change_id": entry.get("change_id"),
        "skill_version": entry.get("skill_version", "desconocido"),
        "prompt_version": entry.get("prompt_version", "desconocido"),
        "model": entry.get("model", "desconocido"),
        "platform": entry.get("platform", "desconocido"),
        "user": entry.get("user"),
        "input_hash": f"sha256:{in_hash}",
        "input_files": in_files,
        "output_hash": f"sha256:{out_hash}",
        "output_files": out_files,
        "decisions": entry.get("decisions", []),
        "status": status,
        "errors": entry.get("errors", []),
        # Acciones con efecto externo que no son ficheros (hoy, Jira). Sin este campo
        # el registro las perdia en silencio, que en una auditoria obligatoria es
        # peor que no prometerlas.
        "notes": entry.get("notes", []),
    }
    if entry.get("correction_of"):
        record["correction_of"] = entry["correction_of"]

    audit_dir = root / "openspec" / "audit"
    audit_dir.mkdir(parents=True, exist_ok=True)
    removed = purge(audit_dir, resolve_retention_days(root, warnings), now, warnings)

    audit_file = audit_dir / f"{now.strftime('%Y-%m')}.jsonl"
    with audit_file.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(json.dumps({
        "audit_file": str(audit_file.relative_to(root)),
        "id": record["id"],
        "purged": removed,
        "warnings": warnings,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
