#!/usr/bin/env python3
"""aiba-status-report · compute_status.py — los numeros del informe de situacion.

Lee lo que el proyecto ya tiene escrito y calcula el estado. **Solo calcula**:
la narrativa la escribe el skill, con estas cifras delante. Esa separacion es la
que impide que el resumen cualitativo diga una cosa y la barra de progreso otra.

**El avance real se mide por trabajo ejecutado, no por fechas.** La fuente son
los changes: `openspec/changes/archive/` son los cerrados y `openspec/changes/`
los activos, cruzados con `roadmap.phases` por `change_hint` --el mismo criterio
que usa `aisdd roadmap` para clasificar fases en un re-faseado--. Cada fase pesa
sus dias de esfuerzo, asi que cerrar una fase L cuenta mas que cerrar una XS.

Dos metricas, y en este orden: **changes** (principal, es la unidad que se abre
y se cierra) y **HUs** (secundaria, es lo que el negocio reconoce). Tres estados
en la principal --cerrado, activo, pendiente--, porque un change a medias no es
ni lo uno ni lo otro y meterlo en cualquiera de los dos lados miente.

Nada se inventa. Cada bloque del JSON declara de que documento sale, y lo que no
se puede derivar sale como hueco con su motivo, nunca como cifra plausible.

Uso:
    python3 compute_status.py --root . --out estado.json
    python3 compute_status.py --schema
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path

# Escala de tallas AIDD. Replicada a proposito en varios plugins --no se pueden
# importar entre si-- y vigilada por .github/scripts/check_plugin_assets.py.
EFFORT_DAYS = {"XS": 0.5, "S": 1.5, "M": 3.0, "L": 5.0, "XL": 8.0}


def _ensure_yaml(allow_install: bool):
    try:
        import yaml
        return yaml
    except ImportError:
        pass
    if not allow_install or os.environ.get("AIBA_ST_NO_INSTALL"):
        return None
    sys.stderr.write("Aviso: 'PyYAML' no esta instalado; instalandolo automaticamente...\n")
    for cmd in ([sys.executable, "-m", "pip", "install", "--quiet", "PyYAML"],
                [sys.executable, "-m", "pip", "install", "--quiet", "--user", "PyYAML"]):
        try:
            subprocess.check_call(cmd)
        except Exception:  # noqa: BLE001
            continue
        try:
            import yaml
            return yaml
        except ImportError:
            continue
    return None


SCHEMA = """\
Salida (JSON). Todo bloque declara su fuente; lo que no se puede derivar sale
como hueco con su motivo, nunca como cifra inventada.

{
  "generado": "2026-08-31",
  "proyecto": "<de openspec/config.yaml o del roadmap>",
  "fuentes":  [{"documento": "...", "existe": true, "usado_para": "..."}],
  "avance": {
    "changes": {"total","cerrados","activos","pendientes","pct_cerrado",
                "pct_activo","ids_cerrados","ids_activos"},
    "esfuerzo": {"total_dias","cerrado_dias","activo_dias","pct_cerrado","base"},
    "hus": {"total","ok","en_curso","sin_iniciar","pct_ok"}
  },
  "previsto":    {"pct","dias","base","sprint_actual","motivo_si_falta"},
  "desviacion":  {"puntos","dias","sentido"},
  "sprints":     [{"nombre","desde","hasta","estado","changes_previstos",
                   "changes_cerrados","hus","esfuerzo_dias","pct_carga"}],
  "bloqueos":    [{"origen","change","decision","desde"}],
  "dependencias":{"listas","bloqueadas","conflictos"},
  "camino_critico": {"dias","cadena"},
  "ritmo":       {"lead_time_medio_dias","changes_medidos","por_change"},
  "avisos":      ["..."]
}
"""


# --- Lectura de fuentes ------------------------------------------------------

def leer_config(root: Path, yaml_mod) -> tuple[dict, str | None]:
    """La seccion `roadmap` de `openspec/config.yaml`: la fuente mas fiable.

    Trae fases con `change_hint`, `hus`, `depends_on`, `sprint` y esfuerzo. Todo
    lo demas de este script son fallbacks de cuando no existe.
    """
    f = root / "openspec" / "config.yaml"
    if not f.is_file():
        return {}, "no existe openspec/config.yaml"
    if yaml_mod is None:
        return {}, "falta PyYAML y no se pudo instalar; no se puede leer config.yaml"
    try:
        datos = yaml_mod.safe_load(f.read_text(encoding="utf-8")) or {}
    except Exception as e:  # noqa: BLE001 - un YAML roto no debe tumbar el informe
        return {}, f"openspec/config.yaml no es YAML valido: {e}"
    return (datos.get("roadmap") or {}), None


def leer_changes(root: Path) -> tuple[set[str], set[str], str | None]:
    """Changes activos y archivados, por el nombre de su directorio."""
    base = root / "openspec" / "changes"
    if not base.is_dir():
        return set(), set(), "no existe openspec/changes/"
    archivo = base / "archive"
    cerrados = {d.name for d in archivo.iterdir() if d.is_dir()} if archivo.is_dir() else set()
    activos = {d.name for d in base.iterdir() if d.is_dir() and d.name != "archive"}
    return activos, cerrados, None


def leer_auditoria(root: Path) -> tuple[dict, str | None]:
    """Cuando se abrio y se cerro cada change, y que bloqueos siguen pendientes.

    Es lo unico que sabe el **cuando**: los directorios dicen que un change esta
    cerrado, no en que fecha. Sin auditoria hay avance pero no hay ritmo.
    """
    d = root / "openspec" / "audit"
    if not d.is_dir():
        return {"disponible": False}, "no existe openspec/audit/"
    eventos: dict[str, dict] = {}
    bloqueos: list[dict] = []
    entradas = 0
    vistos: set[str] = set()
    # Dos disposiciones: `YYYY-MM/<quien>.jsonl` (un fichero por escritor, para
    # que dos devs no conflicten en cada merge) y `YYYY-MM.jsonl`, la anterior.
    for f in sorted(list(d.glob("*.jsonl")) + list(d.glob("*/*.jsonl"))):
        for linea in f.read_text(encoding="utf-8", errors="replace").splitlines():
            linea = linea.strip()
            if not linea:
                continue
            try:
                e = json.loads(linea)
            except json.JSONDecodeError:
                continue  # una linea corrupta no invalida el resto del registro
            # `merge=union` puede repetir una linea al concatenar dos lados. El
            # `id` es unico por diseno: la repetida se descarta y no duplica ni
            # un bloqueo ni un evento de apertura o cierre.
            eid = str(e.get("id") or "")
            if eid and eid in vistos:
                continue
            if eid:
                vistos.add(eid)
            entradas += 1
            cid, cmd, ts = e.get("change_id"), e.get("command", ""), e.get("timestamp")
            if cid and ts:
                reg = eventos.setdefault(cid, {})
                if "open change" in cmd:
                    reg.setdefault("abierto", ts)
                elif "close change" in cmd:
                    reg["cerrado"] = ts
            for dec in e.get("decisions") or []:
                if (dec.get("type") == "bloqueante"
                        and str(dec.get("decision", "")).strip().lower() == "pendiente"):
                    bloqueos.append({"origen": "auditoria", "change": cid,
                                     "decision": dec.get("slug", ""), "desde": ts})
    return {"disponible": True, "entradas": entradas, "eventos": eventos,
            "bloqueos": bloqueos}, None


TALLA_RE = re.compile(r"\b(HU-[A-Za-z0-9-]+)\b")
TALLA_VAL = re.compile(r"\b(XS|XL|S|M|L)\b")


def leer_tallas(root: Path) -> tuple[dict, str | None]:
    """Talla XS/S/M/L/XL por HU, del detalle de historias.

    Se busca la talla **en la misma linea o en las tres siguientes** al id de la
    HU: el detalle las escribe unas veces en tabla y otras como `Estimacion: M`.
    """
    f = root / "docs" / "detalle-historias-usuario.md"
    if not f.is_file():
        return {}, "no existe docs/detalle-historias-usuario.md"
    lineas = f.read_text(encoding="utf-8", errors="replace").splitlines()
    tallas: dict[str, str] = {}
    for i, linea in enumerate(lineas):
        for hu in TALLA_RE.findall(linea):
            if hu in tallas:
                continue
            ventana = " ".join(lineas[i:i + 4])
            tras = ventana.split(hu, 1)[-1]
            # El separador no puede tragarse letras: con `\D` se come la `X` de
            # `XS` y la talla se lee `S`, que es la mitad de dias. Silencioso y
            # en todas las fases a la vez.
            m = re.search(r"(?:Estimaci[oó]n|Talla|Esfuerzo)[^A-Za-z0-9]{0,12}"
                          r"\b(XS|XL|S|M|L)\b", tras)
            if not m:
                m = TALLA_VAL.search(tras)
            if m:
                tallas[hu] = m.group(1)
    return tallas, None


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


# --- Calculo -----------------------------------------------------------------

def esfuerzo_fase(fase: dict, tallas: dict) -> tuple[float, str]:
    """Dias de esfuerzo de una fase, y de donde salen.

    Por orden de fiabilidad: lo que el plan de recursos calculo (`effort_ai`),
    lo que costaria sin IA (`effort_human`), o la suma de las tallas de sus HUs.
    Sin ninguno de los tres, la fase no pesa y se dice: repartir un peso a ojo
    ensuciaria el porcentaje de avance, que es la cifra que mira todo el mundo.
    """
    for clave in ("effort_ai", "effort_human"):
        v = fase.get(clave)
        if isinstance(v, (int, float)) and v > 0:
            return float(v), clave
    hus = fase.get("hus") or []
    dias = sum(EFFORT_DAYS.get(tallas.get(str(h), ""), 0.0) for h in hus)
    if dias > 0:
        return dias, "tallas de las HU"
    return 0.0, "sin dato"


def clasificar(fases: list, activos: set, cerrados: set) -> dict:
    """Cada fase, en uno de tres estados, por su `change_hint`.

    Mismo criterio que `aisdd roadmap` al re-fasear: la fase esta hecha si su
    change esta archivado. Tres estados y no dos porque un change abierto no
    esta ni entregado ni sin empezar, y meterlo en cualquiera de los dos lados
    miente en la direccion que le convenga a quien presenta.
    """
    out = {"cerradas": [], "activas": [], "pendientes": [], "sin_hint": []}
    for f in fases:
        hint = f.get("change_hint")
        if not hint:
            out["sin_hint"].append(f)
            continue
        if hint in cerrados:
            out["cerradas"].append(f)
        elif hint in activos:
            out["activas"].append(f)
        else:
            out["pendientes"].append(f)
    return out


def camino_critico(fases: list, pesos: dict) -> dict:
    """La cadena de dependencias mas larga, en dias.

    Ningun reparto de trabajo baja de ahi, con los devs que sea. Es la unica
    cota del calendario que no depende de cuanta gente haya.
    """
    por_id = {str(f.get("id")): f for f in fases}
    memo: dict[str, tuple[float, list]] = {}
    ciclos: set[str] = set()

    def largo(fid: str, visitando: frozenset) -> tuple[float, list]:
        if fid in memo:
            return memo[fid]
        if fid in visitando:
            ciclos.add(fid)  # se corta aqui, pero no en silencio: sale como aviso
            return 0.0, []
        f = por_id.get(fid)
        if f is None:
            return 0.0, []
        mejor = (0.0, [])
        for dep in f.get("depends_on") or []:
            d, cadena = largo(str(dep), visitando | {fid})
            if d > mejor[0]:
                mejor = (d, cadena)
        total = mejor[0] + pesos.get(fid, 0.0)
        memo[fid] = (total, mejor[1] + [fid])
        return memo[fid]

    mejor = (0.0, [])
    for fid in por_id:
        r = largo(fid, frozenset())
        if r[0] > mejor[0]:
            mejor = r
    return {"dias": round(mejor[0], 2), "cadena": mejor[1],
            "ciclos": sorted(ciclos)}


def dependencias(fases: list, cls: dict) -> dict:
    """Que se puede abrir hoy, que espera, y que no cuadra."""
    hechas = {str(f.get("id")) for f in cls["cerradas"]}
    en_curso = {str(f.get("id")) for f in cls["activas"]}
    listas, bloqueadas = [], []
    for f in cls["pendientes"]:
        deps = [str(d) for d in (f.get("depends_on") or [])]
        falta = [d for d in deps if d not in hechas]
        if falta:
            bloqueadas.append({"fase": str(f.get("id")), "nombre": f.get("name", ""),
                               "espera_a": falta,
                               "alguna_en_curso": [d for d in falta if d in en_curso]})
        else:
            listas.append({"fase": str(f.get("id")), "nombre": f.get("name", ""),
                           "change_hint": f.get("change_hint", "")})
    # En multilane, una dependencia entre lanes que no pasa por una barrera es
    # un error de faseado: los lanes dejan de ser independientes sin decirlo.
    conflictos = []
    lane = {str(f.get("id")): f.get("lane") for f in fases}
    barrera = {str(f.get("id")): bool(f.get("barrier")) for f in fases}
    for f in fases:
        fid, mi = str(f.get("id")), f.get("lane")
        if not mi or barrera.get(fid):
            continue
        for d in f.get("depends_on") or []:
            otro = lane.get(str(d))
            if otro and otro != mi and not barrera.get(str(d)):
                conflictos.append({"fase": fid, "lane": mi,
                                   "depende_de": str(d), "lane_origen": otro})
    return {"listas": listas, "bloqueadas": bloqueadas, "conflictos": conflictos}


def ritmo(eventos: dict, cerrados: set) -> dict:
    """Lead time real `open change` -> `close change`, por change.

    Es lo que dice si el equipo esta acelerando o frenando, y no se puede sacar
    de ningun otro sitio: los directorios no llevan fecha.
    """
    medidos = []
    for cid, e in sorted(eventos.items()):
        if cid not in cerrados or not e.get("abierto") or not e.get("cerrado"):
            continue
        try:
            a = datetime.fromisoformat(e["abierto"].replace("Z", "+00:00"))
            c = datetime.fromisoformat(e["cerrado"].replace("Z", "+00:00"))
        except ValueError:
            continue
        medidos.append({"change": cid, "dias": round((c - a).total_seconds() / 86400, 2),
                        "abierto": e["abierto"], "cerrado": e["cerrado"]})
    if not medidos:
        return {"changes_medidos": 0, "por_change": [],
                "motivo": "la auditoria no tiene pares open/close con fecha"}
    dias = [m["dias"] for m in medidos]
    ultimos = dias[-3:]
    previos = dias[:-3]
    tendencia = "sin base para comparar"
    if previos:
        m1, m2 = sum(previos) / len(previos), sum(ultimos) / len(ultimos)
        tendencia = ("acelerando" if m2 < m1 * 0.9 else
                     "frenando" if m2 > m1 * 1.1 else "estable")
    return {"changes_medidos": len(medidos),
            "lead_time_medio_dias": round(sum(dias) / len(dias), 2),
            "lead_time_ultimo": medidos[-1]["dias"],
            "tendencia": tendencia, "por_change": medidos}


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


def clave_sprint(nombre: str) -> str:
    """`Sprint 1 — Funnel de cotizacion` y `sprint 1` son el mismo sprint.

    La cabecera del plan lleva el objetivo detras del numero y `config.yaml`
    solo el numero. Comparando los textos enteros no casan nunca, y el avance
    previsto sale vacio sin que nada lo explique.
    """
    m = re.search(r"sprint\s*0*(\d+)", str(nombre or ""), re.I)
    return f"sprint {m.group(1)}" if m else str(nombre or "").strip().lower()


def previsto(fases: list, pesos: dict, sprints: list, hoy: date,
             total: float) -> dict:
    """Cuanto esfuerzo deberia estar cerrado hoy, segun el plan de sprints.

    Se cuenta por **sprints ya terminados**, no por el calendario prorrateado:
    un sprint entrega al cerrarse, y repartir su carga dia a dia inventaria un
    avance continuo que no existe. Del sprint en curso no se da nada por hecho.
    """
    if not sprints:
        return {"pct": None, "dias": None, "base": "docs/sprint-plan.md",
                "motivo_si_falta": "no hay sprints reconocidos en el plan"}
    con_fecha = [s for s in sprints if _fecha(s.get("hasta", ""), hoy)]
    if not con_fecha:
        return {"pct": None, "dias": None, "base": "docs/sprint-plan.md",
                "motivo_si_falta": "los sprints del plan no traen fechas de fin"}

    cerrados, actual = [], None
    for s in sprints:
        fin = _fecha(s.get("hasta", ""), hoy)
        ini = _fecha(s.get("desde", ""), hoy)
        if fin and fin < hoy:
            cerrados.append(s["nombre"])
        elif ini and ini <= hoy and (not fin or fin >= hoy):
            actual = s["nombre"]

    nombres = {clave_sprint(c) for c in cerrados}
    dias = sum(pesos.get(str(f.get("id")), 0.0) for f in fases
               if f.get("sprint") and clave_sprint(f.get("sprint")) in nombres)
    if dias == 0 and cerrados:
        return {"pct": None, "dias": None, "base": "docs/sprint-plan.md",
                "sprint_actual": actual,
                "motivo_si_falta": "las fases no declaran a que sprint pertenecen "
                                   "(campo `sprint` de openspec/config.yaml)"}
    return {"pct": round(dias / total * 100, 1) if total else None,
            "dias": round(dias, 2), "base": "docs/sprint-plan.md",
            "sprints_cerrados": cerrados, "sprint_actual": actual}


def construir(root: Path, yaml_mod, hoy: date) -> dict:
    fuentes: list[dict] = []
    avisos: list[str] = []

    def fuente(doc, existe, para, motivo=None):
        fuentes.append({"documento": doc, "existe": existe, "usado_para": para})
        if motivo:
            avisos.append(motivo)

    roadmap, err = leer_config(root, yaml_mod)
    fuente("openspec/config.yaml", bool(roadmap),
           "fases, change_hint, dependencias, HUs y esfuerzo por fase", err)
    activos, cerrados, err = leer_changes(root)
    fuente("openspec/changes/", err is None, "changes activos y archivados", err)
    aud, err = leer_auditoria(root)
    fuente("openspec/audit/", aud.get("disponible", False),
           "fechas de apertura y cierre, y bloqueos pendientes", err)
    tallas, err = leer_tallas(root)
    fuente("docs/detalle-historias-usuario.md", bool(tallas),
           "tallas XS/S/M/L/XL para pesar cada fase", err)
    sprints, err = leer_sprints(root)
    fuente("docs/sprint-plan.md", bool(sprints), "sprints y fechas del avance previsto", err)
    for doc, para in (("docs/roadmap.md", "faseado en prosa, referencia del informe"),
                      ("docs/planificacion-proyecto.md", "riesgos de recursos y equipo"),
                      ("docs/kpis-ia.md", "KPIs medidos de uso de IA (se enlaza, no se recalcula)"),
                      ("docs/mapa-historias-usuario.md", "personas y fases de las HU")):
        fuentes.append({"documento": doc, "existe": (root / doc).is_file(), "usado_para": para})

    fases = list(roadmap.get("phases") or [])
    if not fases:
        avisos.append("sin fases en openspec/config.yaml no hay avance que calcular: "
                      "el informe sale con lo que haya y lo dice")

    pesos, origen_peso = {}, {}
    for f in fases:
        d, o = esfuerzo_fase(f, tallas)
        pesos[str(f.get("id"))] = d
        origen_peso[str(f.get("id"))] = o
    sin_peso = [k for k, v in pesos.items() if v == 0]
    if sin_peso:
        avisos.append(f"{len(sin_peso)} fases sin esfuerzo conocido ({', '.join(sin_peso[:6])}"
                      f"{'...' if len(sin_peso) > 6 else ''}): no pesan en el porcentaje, "
                      f"asi que el avance por esfuerzo se queda corto")

    cc = camino_critico(fases, pesos)
    if cc.get("ciclos"):
        avisos.append(f"ciclo en `depends_on` que pasa por {', '.join(cc['ciclos'])}: "
                      f"el camino critico sale corto y el faseado no es ejecutable "
                      f"tal cual. Lo arregla `aisdd roadmap`")

    cls = clasificar(fases, activos, cerrados)
    if cls["sin_hint"]:
        avisos.append(f"{len(cls['sin_hint'])} fases sin `change_hint`: no se pueden "
                      f"cruzar con los changes y cuentan como pendientes")

    total_d = sum(pesos.values())
    cerr_d = sum(pesos.get(str(f.get("id")), 0.0) for f in cls["cerradas"])
    act_d = sum(pesos.get(str(f.get("id")), 0.0) for f in cls["activas"])
    n = len(fases) or 1

    hus_todas = {str(h) for f in fases for h in (f.get("hus") or [])}
    hus_ok = {str(h) for f in cls["cerradas"] for h in (f.get("hus") or [])}
    hus_curso = {str(h) for f in cls["activas"] for h in (f.get("hus") or [])}

    prev = previsto(fases, pesos, sprints, hoy, total_d)
    real_pct = round(cerr_d / total_d * 100, 1) if total_d else None
    desv = {}
    if prev.get("pct") is not None and real_pct is not None:
        puntos = round(real_pct - prev["pct"], 1)
        desv = {"puntos": puntos, "dias": round(cerr_d - (prev.get("dias") or 0), 2),
                "sentido": "adelantado" if puntos > 1 else
                           "retrasado" if puntos < -1 else "en linea"}
    else:
        desv = {"puntos": None, "dias": None, "sentido": "no comparable",
                "motivo": prev.get("motivo_si_falta", "falta el avance previsto")}

    huerfanos = sorted((activos | cerrados) - {f.get("change_hint") for f in fases})
    if huerfanos:
        avisos.append(f"changes sin fase en el roadmap: {', '.join(huerfanos[:6])}"
                      f"{'...' if len(huerfanos) > 6 else ''}. O el roadmap se re-faseo "
                      f"sin conservar los `change_hint`, o se abrieron fuera de plan")

    return {
        "generado": hoy.isoformat(),
        "proyecto": roadmap.get("project") or roadmap.get("name") or "",
        "modo_faseado": roadmap.get("mode", "atomic"),
        "parallel_developers": roadmap.get("parallel_developers"),
        "fuentes": fuentes,
        "avance": {
            "changes": {
                "total": len(fases), "cerrados": len(cls["cerradas"]),
                "activos": len(cls["activas"]), "pendientes": len(cls["pendientes"]),
                "pct_cerrado": round(len(cls["cerradas"]) / n * 100, 1),
                "pct_activo": round(len(cls["activas"]) / n * 100, 1),
                "ids_cerrados": [f.get("change_hint") for f in cls["cerradas"]],
                "ids_activos": [f.get("change_hint") for f in cls["activas"]],
            },
            "esfuerzo": {
                "total_dias": round(total_d, 2), "cerrado_dias": round(cerr_d, 2),
                "activo_dias": round(act_d, 2), "pct_cerrado": real_pct,
                "base": "effort_ai/effort_human de config.yaml, o tallas de las HU",
                "origen_por_fase": origen_peso,
            },
            "hus": {
                "total": len(hus_todas), "ok": len(hus_ok), "en_curso": len(hus_curso),
                "sin_iniciar": len(hus_todas - hus_ok - hus_curso),
                "pct_ok": round(len(hus_ok) / len(hus_todas) * 100, 1) if hus_todas else None,
                "ids_ok": sorted(hus_ok),
            },
        },
        "previsto": prev,
        "desviacion": desv,
        "sprints": sprints,
        "bloqueos": aud.get("bloqueos", []),
        "dependencias": dependencias(fases, cls),
        "camino_critico": cc,
        "ritmo": ritmo(aud.get("eventos", {}), cerrados),
        "avisos": avisos,
    }


def comparar(actual: dict, anterior: dict) -> dict:
    """Que ha cambiado desde el informe anterior.

    Comparar dos JSON a ojo es como se cuelan los errores en un comite. Y el
    dato que menos se ve mirando solo el de hoy es el **bloqueo que repite**:
    uno que aparece en dos informes seguidos ya no es un bloqueo, es un problema
    de gobierno, y se resuelve escalando y no esperando.
    """
    def pct(d):
        return ((d.get("avance") or {}).get("esfuerzo") or {}).get("pct_cerrado")

    a, b = pct(actual), pct(anterior)
    bl_a = {x.get("decision") for x in (actual.get("bloqueos") or [])}
    bl_b = {x.get("decision") for x in (anterior.get("bloqueos") or [])}
    cer_a = set((actual["avance"]["changes"].get("ids_cerrados") or []))
    cer_b = set((anterior.get("avance", {}).get("changes", {}).get("ids_cerrados") or []))

    dv_a = (actual.get("desviacion") or {}).get("puntos")
    dv_b = (anterior.get("desviacion") or {}).get("puntos")
    return {
        "desde": anterior.get("generado"),
        "avance_puntos": round(a - b, 1) if a is not None and b is not None else None,
        "desviacion_puntos": round(dv_a - dv_b, 1)
                             if dv_a is not None and dv_b is not None else None,
        "changes_cerrados_desde": sorted(cer_a - cer_b),
        "bloqueos_nuevos": sorted(x for x in bl_a - bl_b if x),
        "bloqueos_resueltos": sorted(x for x in bl_b - bl_a if x),
        "bloqueos_que_repiten": sorted(x for x in bl_a & bl_b if x),
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Calcula el estado del proyecto para el informe de situacion.")
    ap.add_argument("--root", default=".", help="raiz del proyecto (por defecto, cwd)")
    ap.add_argument("--out", help="fichero JSON de salida; sin el, stdout")
    ap.add_argument("--schema", action="store_true", help="imprime el esquema y sale")
    ap.add_argument("--anterior", metavar="RUTA",
                    help="JSON del informe anterior; anade el bloque `comparativa` "
                         "con lo que ha cambiado desde entonces")
    ap.add_argument("--no-install", action="store_true", help="no instalar PyYAML al vuelo")
    args = ap.parse_args()

    if args.schema:
        print(SCHEMA)
        return 0

    estado = construir(Path(args.root), _ensure_yaml(not args.no_install),
                       datetime.now(timezone.utc).date())
    if args.anterior:
        p = Path(args.anterior)
        if p.is_file():
            try:
                estado["comparativa"] = comparar(estado, json.loads(p.read_text(encoding="utf-8")))
            except (json.JSONDecodeError, KeyError) as ex:
                estado["avisos"].append(f"no se pudo comparar con {p}: {ex}")
        else:
            estado["avisos"].append(f"no existe el informe anterior {p}: "
                                    f"este es el primero, o cambio de ruta")
    texto = json.dumps(estado, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(texto + "\n", encoding="utf-8")
        print(args.out)
    else:
        print(texto)
    for a in estado["avisos"]:
        sys.stderr.write(f"Aviso: {a}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
