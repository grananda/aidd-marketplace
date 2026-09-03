#!/usr/bin/env python3
"""aisdd-specs · audit.py — entrada de auditoría estructurada en JSON Lines.

Escribe una entrada en ``openspec/audit/YYYY-MM/<quien>.jsonl`` calculando los
hashes SHA-256 de los ficheros de entrada y salida, y aplicando la purga por
retención.

**Un fichero por escritor, y no uno por mes.** El registro es append-only y cada
comando añade una línea al final: con un fichero compartido, dos developers que
parten de la misma base tocan la misma región y el merge conflicta. No es un
caso raro —pasa en cada merge— y es justo el escenario que ``multilane`` fabrica
a propósito. Separando por escritor el conflicto deja de ser posible en vez de
tener que resolverse.

``<quien>`` sale de la identidad de git, porque lo que se evita es un conflicto
*de git* y esa identidad es justo lo que distingue a los escritores ahí.

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

Campos admitidos en el JSON de entrada: command, change_id, repo, skill_version,
prompt_version, model, platform, user, input_files[], output_files[],
decisions[], status, errors[], correction_of, **corrects_archived**, id,
timestamp, **started_at**,
**preflight_rounds**, **turns**, **interventions**, **verification{}**.

``attempt``, el bloque ``preflight`` y ``verification.first_run_green`` **no se
pasan**: los deriva el script del propio registro, de ``decisions[]`` y del
resultado de la verificacion. Un recuento que el agente teclea aparte
puede contradecir a la lista de la que sale, y entonces no se sabe a cual creer.

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
import os
import re
import subprocess
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


SLUG_RE = re.compile(r"[^a-z0-9._-]+")
EMAIL_RE = re.compile(r"[^\s<>@]+@[^\s<>@]+")


def quien_escribe(root: Path, entry: dict) -> str:
    """Identificador del escritor, estable y valido como nombre de fichero.

    Por orden: el ``user`` que declara la entrada, la identidad de git del
    repositorio, y ``desconocido``. Las tres son deterministas: el nombre no
    puede depender de nada que cambie entre dos invocaciones del mismo dev, o
    proliferarian ficheros sin separar a nadie.
    """
    for candidato in (entry.get("user"), _git_email(root)):
        if not candidato or not str(candidato).strip():
            continue
        crudo = str(candidato).strip()
        # `Nombre Apellido <correo@dominio>` es la forma en que git escribe una
        # identidad. El correo ya es unico y sobrevive a las tildes, que en un
        # nombre de fichero se convierten en guiones y lo dejan ilegible.
        m = EMAIL_RE.search(crudo)
        slug = SLUG_RE.sub("-", (m.group(0) if m else crudo).lower()).strip("-._")
        if slug:
            return slug[:60]
    return "desconocido"


def _git_email(root: Path) -> str | None:
    try:
        r = subprocess.run(["git", "-C", str(root), "config", "user.email"],
                           capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip() or None


def mes_de(f: Path) -> tuple[int, int] | None:
    """El mes al que pertenece un fichero de auditoria, en las dos disposiciones.

    La nueva lo lleva en el directorio (``2026-08/ana.jsonl``) y la anterior en
    el propio nombre (``2026-08.jsonl``). Los proyectos que ya existen siguen
    purgandose igual.
    """
    for texto in (f.parent.name, f.stem):
        try:
            year, month = (int(p) for p in texto.split("-"))
        except ValueError:
            continue
        if 1 <= month <= 12:
            return year, month
    return None


def ficheros_de_auditoria(audit_dir: Path) -> list[Path]:
    """Las dos disposiciones a la vez: `YYYY-MM/*.jsonl` y `YYYY-MM.jsonl`."""
    return sorted(list(audit_dir.glob("*.jsonl")) + list(audit_dir.glob("*/*.jsonl")))


def contar_intento(audit_dir: Path, command: str, change_id) -> int:
    """Cuantas veces se ha ejecutado ya este comando sobre este change, +1.

    Lo cuenta el script y no lo declara el agente: un reintento es justo la
    situacion en la que el agente ha perdido el hilo, y pedirle que se acuerde
    de que va por la tercera es pedirle el dato precisamente cuando menos
    fiable es. Aqui sale de contar lineas.
    """
    if not change_id or not audit_dir.is_dir():
        return 1
    n = 0
    for f in ficheros_de_auditoria(audit_dir):
        try:
            texto = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for linea in texto.splitlines():
            linea = linea.strip()
            if not linea:
                continue
            try:
                e = json.loads(linea)
            except json.JSONDecodeError:
                continue
            if (isinstance(e, dict) and e.get("command") == command
                    and e.get("change_id") == change_id):
                n += 1
    return n + 1


def resumen_preflight(decisions: list, rounds) -> dict:
    """El pre-flight, contado desde `decisions[]`.

    Cuatro de los cinco numeros ya estan en las decisiones --cuantas hubo, quien
    las resolvio y cuantas eran bloqueantes--, asi que se derivan en vez de
    pedirse: un recuento que el agente teclea aparte puede contradecir a la lista
    de la que sale, y entonces no se sabe cual de los dos creer.

    Las de `type: correccion` no entran: son de la implementacion, no del
    pre-flight, y contarlas inflaria la intensidad de las preguntas iniciales.

    `rounds` es lo unico que el agente aporta, porque no deja rastro en la lista.
    Y es el numero que mas dice: cinco preguntas de golpe son un pre-flight; tres
    rondas de dos son que no se capto el problema a la primera.
    """
    utiles = [d for d in decisions if isinstance(d, dict) and d.get("type") != "correccion"]
    r = None
    if isinstance(rounds, (int, float)) and rounds >= 0:
        r = int(rounds)
    return {
        "rounds": r,
        "questions": len(utiles),
        "by_user": sum(1 for d in utiles if d.get("origen") == "usuario"),
        "auto": sum(1 for d in utiles if d.get("origen") == "auto-default"),
        "blocking": sum(1 for d in utiles if d.get("type") == "bloqueante"),
    }


ESTADOS_BUILD = ("ok", "failed", "skipped", "n/a")


def resumen_verificacion(verification, attempt: int, warnings: list[str]) -> dict | None:
    """Lo que dieron el build y los tests, y si salio verde a la primera.

    ``first_run_green`` no se declara: se deriva de que sea el primer intento y
    de que no falle nada. Es el mejor indicador de si las specs iban bien --mejor
    que contar correcciones, que llegan despues y ya con el problema encima-- y
    justo por eso no puede depender de que el agente se acuerde de marcarlo.

    Sin bloque, ``None``: el comando no verifico o no supo decirlo. Un cero seria
    peor, porque se leeria como cero fallos.
    """
    if not isinstance(verification, dict) or not verification:
        return None
    build = str(verification.get("build", "n/a")).lower()
    if build not in ESTADOS_BUILD:
        warnings.append(f"verification.build '{build}' no valido; se registra como 'n/a'")
        build = "n/a"
    nums = {}
    for k in ("tests_run", "passed", "failed", "added", "modified"):
        nums[k] = entero_no_negativo(verification.get(k), f"verification.{k}", warnings)
    gates = [g for g in (verification.get("gates") or []) if isinstance(g, dict)]

    fallos = (nums["failed"] or 0) + sum(
        1 for g in gates if str(g.get("status", "")).lower() not in ("ok", "skipped"))
    corrio = build == "ok" or (nums["tests_run"] or 0) > 0
    return {**nums, "build": build, "gates": gates,
            # Verde a la primera solo si de verdad fue la primera y de verdad
            # corrio algo: `attempt` lo cuenta el script, asi que no se puede
            # maquillar reintentando y volviendo a declarar.
            "first_run_green": bool(corrio and attempt == 1 and fallos == 0
                                    and build != "failed")}


def entero_no_negativo(valor, nombre: str, warnings: list[str]):
    """Los contadores que declara el agente. Un valor imposible se descarta.

    Es preferible el hueco al numero raro: un KPI construido sobre un `turns`
    negativo no avisa de nada, simplemente sale mal.
    """
    if valor is None:
        return None
    try:
        n = int(valor)
    except (TypeError, ValueError):
        warnings.append(f"{nombre}: '{valor}' no es un entero; se omite")
        return None
    if n < 0:
        warnings.append(f"{nombre}: {n} es negativo; se omite")
        return None
    return n


def purge(audit_dir: Path, retention_days: int, now: datetime, warnings: list[str]) -> list[str]:
    """Borra los .jsonl cuyo mes terminó antes del corte. Purga por meses completos."""
    removed: list[str] = []
    if not audit_dir.is_dir():
        return removed
    cutoff = now.timestamp() - retention_days * 86400
    for f in ficheros_de_auditoria(audit_dir):
        mes = mes_de(f)
        if mes is None:
            continue  # nombre ajeno al esquema: no es nuestro, no se toca
        year, month = mes
        end = datetime(year + month // 12, month % 12 + 1, 1, tzinfo=timezone.utc)
        if end.timestamp() < cutoff:
            try:
                f.unlink()
                removed.append(str(f.relative_to(audit_dir)))
                # El directorio del mes se va con su ultimo fichero.
                if f.parent != audit_dir and not any(f.parent.iterdir()):
                    f.parent.rmdir()
            except OSError as exc:
                warnings.append(f"no se pudo purgar {f.name}: {exc}")
    return removed


LOG_ACTIVIDAD = Path("docs") / "aidd-activity.md"
CABECERA_ACTIVIDAD = """# Registro de actividad AIDD

Traza automatica de las acciones sobre el codigo: que skill se ejecuta, que
ficheros toca la IA y cuanto dura cada turno. La consume `aiba metrics` para
calcular los KPIs. Es opt-in: existe este fichero, se registra; borralo y el
registro se apaga en este proyecto.

No se guarda el texto de los prompts ni el contenido del codigo.

Formato (marcas de tiempo en UTC):

`- <fecha-hora> | user:<usuario> | skill:<skill> | ctx:<HU o change> | <accion> | note:<nota>`

Acciones: `run` (skill invocado), `file:<ruta>` (fichero escrito por la IA),
`turn` (fin de turno, con duracion y numero de acciones).

"""


def fuente_actividad(root: Path) -> str:
    """Quien escribe el registro de actividad: `hooks` o `skills`.

    Los hooks de plugin **no se ejecutan en todas partes** --medido en Codex CLI
    0.151.0: se registran con su hash de confianza y no llegan a correr, y Cline
    ni siquiera tiene un mecanismo compatible--. Donde no corren, el registro lo
    escribe este script.

    **La decision se declara, no se adivina en cada ejecucion**: la fija
    `aisdd init` en `activity.source` de `openspec/config.yaml`. Sin esa clave se
    asume `hooks`, que es el comportamiento historico: preferimos perder una
    linea a **duplicarla**, porque un registro con lo mismo dos veces infla el
    tiempo atendido y nadie lo nota.
    """
    cfg = root / "openspec" / "config.yaml"
    if not cfg.is_file():
        return "hooks"
    dentro = False
    for line in cfg.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line[:1].isspace():
            dentro = line.strip().rstrip(":") == "activity"
            continue
        if dentro and line.strip().startswith("source:"):
            valor = line.split(":", 1)[1].strip().strip('"\'')
            return valor if valor in ("hooks", "skills") else "hooks"
    return "hooks"


def registrar_actividad(root: Path, record: dict, warnings: list[str]) -> str | None:
    """Escribe en el registro de actividad lo que este comando ha hecho.

    Solo cuando `activity.source` es `skills`. Es el plan B para agentes que no
    ejecutan los hooks: sin esto, `aiba metrics` se queda sin **tiempo atendido**
    y el ahorro no se puede calcular.

    **Lo que anota no es un turno, es un comando.** El hook ve el turno entero
    --incluido revisar, conversar e iterar-- y un comando solo se ve a si mismo.
    Por eso la linea lleva `scope=comando`: es una base mas estrecha y quien lea
    el informe tiene que poder saberlo. Sustituir una por otra en silencio daria
    un tiempo atendido menor y una aceleracion inflada.
    """
    if fuente_actividad(root) != "skills":
        return None
    log = root / LOG_ACTIVIDAD
    if not log.is_file():                 # opt-in: sin fichero no se registra
        return None

    def limpio(v) -> str:
        return re.sub(r"[|\r\n\t]+", " ", str(v or "-")).strip()[:120] or "-"

    ts = record.get("timestamp") or ""
    # El mismo identificador que escribe el hook, para que la misma persona no
    # salga como dos usuarios distintos en un proyecto que cambie de fuente.
    usuario = limpio(record.get("user") or os.environ.get("USER")
                     or os.environ.get("USERNAME") or quien_escribe(root, {}))
    comando = limpio(record.get("command"))
    # `compute_kpis.py` clasifica por **nombre de skill**, no por comando: con el
    # comando entero cada linea caeria en "Otros" y se perderia el desglose por
    # etapa. El comando se conserva en la nota, que no se pierde nada.
    skill = "aisdd-amend" if comando.startswith("aisdd amend") else "aisdd-specs"
    ctx = limpio(record.get("change_id") or record.get("hu") or "-")
    lineas = [f"- {ts} | user:{usuario} | skill:{skill} | ctx:{ctx} | "
              f"run | note:{comando}"]

    escritos = [f.get("path") for f in (record.get("output_files") or []) if f.get("path")]
    for ruta in escritos:
        if str(ruta).replace("\\", "/") == LOG_ACTIVIDAD.as_posix():
            continue                      # nunca registrar la escritura del propio registro
        lineas.append(f"- {ts} | user:{usuario} | skill:{skill} | ctx:{ctx} | "
                      f"file:{limpio(ruta)} | note:-")

    dur = "-"
    inicio, fin = record.get("started_at"), record.get("timestamp")
    if inicio and fin:
        try:
            a = datetime.fromisoformat(str(inicio).replace("Z", "+00:00"))
            b = datetime.fromisoformat(str(fin).replace("Z", "+00:00"))
            segundos = int((b - a).total_seconds())
            if segundos >= 0:
                dur = f"{segundos}s"
        except ValueError:
            warnings.append("started_at o timestamp no son fechas ISO: duracion sin calcular")
    lineas.append(f"- {ts} | user:{usuario} | skill:{skill} | ctx:{ctx} | turn | "
                  f"note:dur={dur} skills=1 files={len(escritos)} scope=comando")

    with log.open("a", encoding="utf-8", newline="\n") as fh:
        if log.stat().st_size == 0:
            fh.write(CABECERA_ACTIVIDAD)
        fh.write("\n".join(lineas) + "\n")
    return str(LOG_ACTIVIDAD.as_posix())


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

    audit_dir_pre = root / "openspec" / "audit"
    decisions = entry.get("decisions", [])
    started_at = entry.get("started_at")
    if not started_at:
        warnings.append(
            "sin `started_at`: no se puede medir cuanto duro el comando. "
            "Anota la hora UTC al empezar y pasala en la entrada")

    intento = contar_intento(audit_dir_pre, entry["command"], entry.get("change_id"))

    record = {
        "id": entry.get("id") or str(uuid.uuid4()),
        # Dos marcas y no una. Con solo el final, la duracion de un comando no
        # existe: el hueco hasta la entrada anterior mide la comida de por medio,
        # no el trabajo. Un comando que empieza a las 18:50 y acaba a las 09:10
        # duro minutos, no catorce horas.
        "started_at": started_at,
        "timestamp": entry.get("timestamp") or now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "command": entry["command"],
        "change_id": entry.get("change_id"),
        # `repo` solo tiene sentido con la auditoria compartida de la topologia
        # `externalizado`, donde un mismo registro recoge varios repos de codigo.
        # En `mono` queda a null; el campo esta siempre para que la entrada se
        # lea igual venga de donde venga.
        "repo": entry.get("repo"),
        "skill_version": entry.get("skill_version", "desconocido"),
        "prompt_version": entry.get("prompt_version", "desconocido"),
        "model": entry.get("model", "desconocido"),
        "platform": entry.get("platform", "desconocido"),
        "user": entry.get("user"),
        "input_hash": f"sha256:{in_hash}",
        "input_files": in_files,
        "output_hash": f"sha256:{out_hash}",
        "output_files": out_files,
        "decisions": decisions,
        # Ejecucion n-esima de este comando sobre este change. La cuenta el
        # script leyendo el propio registro (ver `contar_intento`).
        "attempt": intento,
        # Intensidad del pre-flight. Cuatro de los cinco numeros salen de
        # `decisions[]`; solo `rounds` lo aporta el agente.
        "preflight": resumen_preflight(decisions, entry.get("preflight_rounds")),
        # Autoinformados por el agente: no dejan rastro en ningun artefacto, asi
        # que no se pueden contrastar. Van por eso en su propio bloque, y ningun
        # KPI debe depender solo de ellos.
        "self_reported": {
            "turns": entero_no_negativo(entry.get("turns"), "turns", warnings),
            "interventions": entero_no_negativo(
                entry.get("interventions"), "interventions", warnings),
        },
        # Resultado del build, los tests y las puertas de calidad. `None` cuando
        # el comando no verifica: un bloque a cero se leeria como cero fallos.
        "verification": resumen_verificacion(entry.get("verification"), intento, warnings),
        "status": status,
        "errors": entry.get("errors", []),
        # Acciones con efecto externo que no son ficheros (hoy, Jira). Sin este campo
        # el registro las perdia en silencio, que en una auditoria obligatoria es
        # peor que no prometerlas.
        "notes": entry.get("notes", []),
    }
    if entry.get("correction_of"):
        record["correction_of"] = entry["correction_of"]

    # Retrabajo sobre lo ya entregado. Es lo mas caro que hay --el change se
    # declaro terminado, sus specs se promovieron y alguien lo dio por bueno--
    # y hasta ahora entraba en el registro **como cualquier otro**: un equipo
    # que abre tres changes al mes para arreglar lo del mes pasado se leia igual
    # que uno que entrega limpio.
    #
    # No confundir con `correction_of`, que corrige **una entrada de auditoria**
    # mal escrita: eso es higiene de un log append-only, no retrabajo.
    corrige = entry.get("corrects_archived")
    if corrige:
        archivo = root / "openspec" / "changes" / "archive" / str(corrige)
        if not archivo.is_dir():
            # No se descarta: el dato del agente vale mas que nuestra
            # comprobacion --el change pudo archivarse en otro repo, o el
            # nombre pudo cambiar--. Pero se avisa, porque un slug inventado
            # ensuciaria el KPI de retrabajo sin que nadie lo notara.
            warnings.append(
                f"corrects_archived '{corrige}' no aparece en openspec/changes/archive/: "
                f"se registra igual, pero comprueba el identificador")
        record["corrects_archived"] = str(corrige)

    audit_dir = root / "openspec" / "audit"
    audit_dir.mkdir(parents=True, exist_ok=True)
    removed = purge(audit_dir, resolve_retention_days(root, warnings), now, warnings)

    mes_dir = audit_dir / now.strftime("%Y-%m")
    mes_dir.mkdir(parents=True, exist_ok=True)
    audit_file = mes_dir / f"{quien_escribe(root, entry)}.jsonl"
    with audit_file.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    actividad = registrar_actividad(root, record, warnings)

    print(json.dumps({
        "audit_file": str(audit_file.relative_to(root)),
        "id": record["id"],
        "purged": removed,
        "activity_log": actividad,
        "warnings": warnings,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
