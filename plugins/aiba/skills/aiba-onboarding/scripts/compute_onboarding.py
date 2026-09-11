#!/usr/bin/env python3
"""aiba-onboarding · compute_onboarding.py — lo que necesita saber quien llega.

Calcula los hechos del onboarding a partir de los documentos de negocio del
proyecto --brief, mapa y detalle de historias, plan de revision, plan de
sprints-- y, si se le pasa, del estado que `compute_status.py` saca de OpenSpec.
Despues escribe el documento con la narrativa que el skill anade al JSON.

**La estructura, las tablas y las listas salen de aqui y no del modelo.** Es la
leccion del diseno funcional: cuando el modelo compone el documento entero, cada
modelo lo compone distinto. Aqui el modelo solo escribe dos parrafos; todo lo
demas sale igual lo genere quien lo genere.

**OpenSpec es la fuente secundaria.** Dice que historias estan construidas, no
de que va el proyecto. Sin el, el onboarding sale igual y dice que no lo sabe.

Uso:
    python3 compute_onboarding.py --root . --out onboarding.json [--estado estado.json]
    python3 compute_onboarding.py --render onboarding.json --output docs/onboarding.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from sprints import SPRINT_RE, _fecha, clasificar_sprints, leer_sprints  # noqa: E402

HU_RE = re.compile(r"\bHU-[A-Za-z0-9]+\b")
TALLA_RE = re.compile(r"Estimaci[oó]n[^\n]*?\b(XS|XL|S|M|L)\b", re.I)

# De donde sale cada cosa, y que comando la genera si falta. Un hueco sin el
# comando que lo llena es solo una queja; con el, es una accion.
FUENTES = [
    ("brief", "docs/cliente-requisitos.md", "aidd client-requirements"),
    ("mapa", "docs/mapa-historias-usuario.md", "aidd user-stories"),
    ("detalle", "docs/detalle-historias-usuario.md", "aidd user-story-details"),
    ("revision", "docs/plan-revision-hu.json", "aiba hu-review-plan"),
    ("sprints", "docs/sprint-plan.md", "aiba sprint-planning"),
    ("openspec", "openspec", "aisdd init"),
]

# Que leer y en que orden. No los quince documentos del metodo: los que dan una
# idea global, primero los de todos y despues los de cada perfil.
LECTURA = [
    ("docs/cliente-requisitos.md", "Todos", "Por qué existe el proyecto y para quién"),
    ("docs/mapa-historias-usuario.md", "Todos", "Qué se construye, fase a fase"),
    ("docs/sprint-plan.md", "Todos", "Cuándo se construye cada cosa"),
    ("docs/arquitectura-base.md", "Desarrollo", "Cómo está construido y por qué"),
    ("docs/guia-estilos.md", "Desarrollo (front)", "Cómo se ve"),
    ("docs/detalle-historias-usuario.md", "Desarrollo y QA",
     "Los criterios de aceptación de tu historia"),
    ("docs/planificacion-proyecto.md", "PM y BA", "Equipo, perfiles y recursos"),
    ("docs/plan-revision-hu.md", "BA", "Qué historias están cerradas con negocio"),
    ("docs/html/estado-proyecto.html", "PM", "El avance medido y sus desviaciones"),
]

# En externalizado y fraccionado, lo primero que pregunta quien llega es en que
# repositorio trabaja y desde donde lanza cada comando. Es la tabla de
# `governance-repo.md` de aisdd-specs, resuelta para su caso.
DONDE_SE_EJECUTA = {
    "externalizado": [
        ("aisdd init, aisdd roadmap", "La raíz del repositorio de gobierno",
         "Lead / Arquitectura"),
        ("aisdd open, implement, amend y close change",
         "Tu repositorio de código: el openspec/ está más arriba y se encuentra solo",
         "Desarrollo"),
    ],
    "fraccionado": [
        ("Todos los comandos aisdd", "Tu repositorio: cada uno lleva su propio openspec/",
         "Todos"),
        ("aisdd lane", "No se cambia de lane: el lane es el repositorio", "Desarrollo"),
    ],
}


# --- Lectura de los documentos ------------------------------------------------

def _clave(texto: str) -> str:
    t = unicodedata.normalize("NFKD", texto or "")
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    t = re.sub(r"^[\d.\s]+", "", t.strip())
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def _secciones(md: str) -> dict:
    """Cuerpo de cada seccion de segundo nivel, por su titulo normalizado."""
    fuera = {}
    for bloque in re.split(r"^##\s+", md, flags=re.M)[1:]:
        titulo, _, cuerpo = bloque.partition("\n")
        fuera[_clave(titulo)] = cuerpo
    return fuera


def _buscar(sec: dict, palabra: str) -> str:
    return next((v for k, v in sec.items() if palabra in k), "")


def _parrafo(cuerpo: str, limite: int = 700) -> str:
    lineas = []
    for l in cuerpo.splitlines():
        l = l.strip()
        if not l:
            if lineas:
                break
            continue
        if l.startswith(("#", "|", ">")):
            continue
        lineas.append(l.lstrip("-* ").strip())
    return " ".join(lineas)[:limite]


def _vinetas(cuerpo: str, n: int = 6) -> list[str]:
    return [l.strip()[2:].strip() for l in cuerpo.splitlines()
            if l.strip().startswith(("- ", "* "))][:n]


def leer_proyecto(root: Path) -> dict:
    """Nombre, contexto, usuarios y stack, del brief del cliente."""
    f = root / "docs" / "cliente-requisitos.md"
    if not f.is_file():
        return {"nombre": "", "contexto": "", "usuarios": [], "stack": []}
    md = f.read_text(encoding="utf-8", errors="replace")
    h1 = re.search(r"^#\s+(.+)$", md, re.M)
    nombre = re.split(r"\s[—–-]\s", h1.group(1))[-1].strip() if h1 else ""
    sec = _secciones(md)
    return {"nombre": nombre, "contexto": _parrafo(_buscar(sec, "contexto")),
            "usuarios": _vinetas(_buscar(sec, "usuario")),
            "stack": _vinetas(_buscar(sec, "stack"))}


def _titulo_de_enunciado(texto: str) -> str:
    m = re.search(r"quiero\s+(.+?)(?:\s+para\b|$)", texto, re.I)
    t = (m.group(1) if m else texto).strip().rstrip(".")
    return (t[:1].upper() + t[1:])[:90]


def leer_hus(root: Path) -> dict:
    """Cada historia con su titulo, fase, talla y estado de revision.

    Tres fuentes que se completan: el detalle da el titulo y la talla, el mapa
    la fase, y el plan de revision si esta cerrada con negocio. Ninguna trae un
    estado de "hecha": eso lo dicen los sprints y, si existe, OpenSpec.
    """
    hus: dict[str, dict] = {}

    def hu(i: str) -> dict:
        return hus.setdefault(i, {"id": i, "titulo": "", "fase": "", "talla": "",
                                  "revision": "", "bloqueada": False})

    f = root / "docs" / "mapa-historias-usuario.md"
    if f.is_file():
        fase = ""
        for linea in f.read_text(encoding="utf-8", errors="replace").splitlines():
            if linea.startswith("## "):
                fase = ""
            h = re.match(r"^#{3,4}\s+(.*)$", linea)
            if h:
                mf = re.search(r"\b(F\d+)\b", h.group(1))
                fase = mf.group(1) if mf else fase
            fila = re.match(r"^\|\s*(HU-[A-Za-z0-9]+)\s*\|\s*([^|]*?)\s*\|", linea)
            if fila:
                x = hu(fila.group(1))
                x["fase"] = x["fase"] or fase
                x.setdefault("_enunciado", fila.group(2))

    f = root / "docs" / "detalle-historias-usuario.md"
    if f.is_file():
        md = f.read_text(encoding="utf-8", errors="replace")
        cab = list(re.finditer(r"^#{2,4}\s*(HU-[A-Za-z0-9]+)\b[\s—–:-]*(.*)$", md, re.M))
        for k, m in enumerate(cab):
            fin = cab[k + 1].start() if k + 1 < len(cab) else len(md)
            x = hu(m.group(1))
            x["titulo"] = m.group(2).strip() or x["titulo"]
            t = TALLA_RE.search(md[m.end():fin])
            if t:
                x["talla"] = t.group(1).upper()

    f = root / "docs" / "plan-revision-hu.json"
    if f.is_file():
        try:
            datos = json.loads(f.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            datos = {}
        for r in datos.get("hus") or []:
            if not isinstance(r, dict) or not r.get("id"):
                continue
            x = hu(str(r["id"]))
            x["revision"] = str(r.get("estado") or "")
            x["bloqueada"] = bool(r.get("bloqueada"))
            x["fase"] = x["fase"] or str(r.get("fase") or "")
            x["talla"] = x["talla"] or str(r.get("estimacion") or "")
            if not x["titulo"] and r.get("quiero"):
                x["titulo"] = _titulo_de_enunciado("quiero " + str(r["quiero"]))

    for x in hus.values():
        enun = x.pop("_enunciado", "")
        if not x["titulo"] and enun:
            x["titulo"] = _titulo_de_enunciado(enun)
    return hus


def hus_por_sprint(root: Path) -> tuple[dict, dict]:
    """A que sprint va cada historia, y el objetivo de cada sprint."""
    f = root / "docs" / "sprint-plan.md"
    if not f.is_file():
        return {}, {}
    texto = f.read_text(encoding="utf-8", errors="replace")
    cab = list(SPRINT_RE.finditer(texto))
    asignacion, objetivos = {}, {}
    for k, m in enumerate(cab):
        fin = cab[k + 1].start() if k + 1 < len(cab) else len(texto)
        tramo = texto[m.end():fin]
        corte = re.search(r"^##\s", tramo, re.M)     # la seccion siguiente del plan
        if corte:
            tramo = tramo[:corte.start()]
        nombre = m.group(1).strip()
        obj = re.search(r"Objetivo[^:\n]*:\s*(.+)", tramo)
        if obj:
            # El plan suele poner detras, en la misma linea, las unidades o la
            # carga: el objetivo es la primera frase y nada mas.
            primera = re.split(r"(?<=\w)\.(?:\s|$)|\s\|\s", obj.group(1), maxsplit=1)[0]
            objetivos[nombre] = primera.strip().rstrip(".")
        for i in HU_RE.findall(tramo):
            asignacion.setdefault(i, nombre)
    return asignacion, objetivos


def leer_estado(ruta: str | None, avisos: list) -> dict | None:
    if not ruta:
        return None
    p = Path(ruta)
    if not p.is_file():
        avisos.append(f"no existe {ruta}: sin el estado de OpenSpec el onboarding no "
                      "dice qué historias están construidas")
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        avisos.append(f"{ruta} no se puede leer ({e}): se sigue sin OpenSpec")
        return None


# --- Calculo -----------------------------------------------------------------

def _num(i: str) -> tuple:
    m = re.search(r"\d+", i)
    return (int(m.group()) if m else 10 ** 6, i)


def calcular(root: Path, hoy: date, ruta_estado: str | None) -> dict:
    avisos: list[str] = []
    fuentes = [{"clave": c, "ruta": r, "existe": (root / r).exists(), "genera": g}
               for c, r, g in FUENTES]

    hus = leer_hus(root)
    sprints, motivo = leer_sprints(root)
    if motivo:
        avisos.append(motivo)
    punto = clasificar_sprints(sprints, hoy)
    asignacion, objetivos = hus_por_sprint(root)

    def estado_sprint(s: dict) -> str:
        if s["nombre"] in punto["cerrados"]:
            return "cerrado"
        if s["nombre"] == punto["actual"]:
            return "en curso"
        ini = _fecha(s.get("desde", ""), hoy)
        return "futuro" if ini and ini > hoy else "sin fechas"

    lista_sprints = [{**s, "estado": estado_sprint(s),
                      "objetivo": objetivos.get(s["nombre"], ""),
                      "hus": sorted((i for i, n in asignacion.items() if n == s["nombre"]),
                                    key=_num)} for s in sprints]
    por_nombre = {s["nombre"]: s["estado"] for s in lista_sprints}

    estado = leer_estado(ruta_estado, avisos)
    if estado is None and (root / "openspec").is_dir() and not ruta_estado:
        avisos.append("hay openspec/ pero no se ha pasado --estado: el onboarding no "
                      "dirá qué historias están construidas")
    ok = curso = None
    if estado is not None:
        h = (estado.get("avance") or {}).get("hus") or {}
        ok, curso = set(h.get("ids_ok") or []), set(h.get("ids_en_curso") or [])
        for i in h.get("ids_todas") or []:   # las que OpenSpec conoce y el mapa no
            hus.setdefault(i, {"id": i, "titulo": "", "fase": "", "talla": "",
                               "revision": "", "bloqueada": False})

    for i, x in hus.items():
        x["sprint"] = asignacion.get(i, "")
        x["sprint_estado"] = por_nombre.get(x["sprint"], "") if x["sprint"] else "sin sprint"
        x["construida"] = (None if ok is None else
                           "sí" if i in ok else "en curso" if i in curso else "no")

    ids = sorted(hus, key=_num)
    lista = [hus[i] for i in ids]
    sprint_n = Counter(x["sprint_estado"] for x in lista)
    resumen = {
        "total": len(lista),
        "por_fase": dict(sorted(Counter(x["fase"] or "sin fase" for x in lista).items())),
        "revision": (dict(Counter(x["revision"] or "sin dato" for x in lista))
                     if (root / "docs" / "plan-revision-hu.json").is_file() else None),
        "en_sprints_cerrados": sprint_n.get("cerrado", 0),
        "en_sprint_en_curso": sprint_n.get("en curso", 0),
        "en_sprints_futuros": sprint_n.get("futuro", 0),
        "sin_sprint": sprint_n.get("sin sprint", 0),
        "construidas": None if ok is None else sum(1 for x in lista if x["construida"] == "sí"),
        "en_construccion": None if ok is None else sum(1 for x in lista
                                                        if x["construida"] == "en curso"),
        # Planificadas en un sprint que ya termino y no construidas: la unica
        # senal de desfase que cabe en una vision global.
        "planificadas_sin_construir": (None if ok is None else
                                       [x["id"] for x in lista
                                        if x["sprint_estado"] == "cerrado"
                                        and x["construida"] != "sí"]),
        "bloqueadas": [x["id"] for x in lista if x["bloqueada"]],
    }

    openspec = {"disponible": estado is not None,
                "existe_directorio": (root / "openspec").is_dir()}
    if estado is not None:
        topo = estado.get("topology") or "mono"
        openspec.update({
            "topologia": topo, "modo": estado.get("modo_faseado"),
            "repo": estado.get("repo"),
            "parallel_developers": estado.get("parallel_developers"),
            "donde_se_ejecuta": ([{"comando": c, "desde": d, "quien": q}
                                  for c, d, q in DONDE_SE_EJECUTA[topo]]
                                 if topo in DONDE_SE_EJECUTA else None)})

    if not hus:
        avisos.append("no se ha encontrado ninguna historia de usuario: faltan el mapa y "
                      "el detalle de historias")
    proyecto = leer_proyecto(root)
    proyecto["nombre"] = (proyecto["nombre"] or (estado or {}).get("proyecto")
                          or root.resolve().name)
    return {
        "generado": hoy.isoformat(),
        "proyecto": proyecto,
        "fuentes": fuentes,
        "hus": lista,
        "resumen": resumen,
        "sprints": {"lista": lista_sprints, "cerrados": punto["cerrados"],
                    "actual": punto["actual"], "siguiente": punto["siguiente"]},
        "openspec": openspec,
        "lectura": [{"ruta": r, "para": p, "que": q} for r, p, q in LECTURA
                    if (root / r).exists()],
        "avisos": avisos,
    }


# --- Documento ---------------------------------------------------------------

# El plan de revision escribe los estados sin tilde --es un valor de maquina--;
# el documento es para personas. Orden logico, no alfabetico, y con plural.
REVISION = [("Cerrada", "cerrada", "cerradas"),
            ("En revision", "en revisión", "en revisión"),
            ("Pendiente", "pendiente", "pendientes"),
            ("sin dato", "sin dato", "sin dato")]


def _revision(valor: str) -> str:
    return {"En revision": "En revisión"}.get(valor, valor)

def _tabla(filas: list[dict], con_sprint: bool = False) -> list[str]:
    cab = "| HU | Historia | Fase | Revisión |" + (" Sprint |" if con_sprint else "")
    sep = "|---|---|---|---|" + ("---|" if con_sprint else "")
    out = [cab, sep]
    for x in filas:
        tit = x["titulo"] or "[PENDIENTE: sin título en el mapa ni en el detalle]"
        if x["bloqueada"]:
            tit += " **(bloqueada)**"
        out.append(f"| {x['id']} | {tit} | {x['fase'] or '—'} | {_revision(x['revision']) or '—'} |"
                   + (f" {x['sprint'] or '—'} |" if con_sprint else ""))
    return out + [""]


def _fechas(s: dict) -> str:
    return f" ({s['desde']} → {s['hasta']})" if s.get("desde") and s.get("hasta") else ""


def render(d: dict) -> str:
    nar = d.get("narrativa") or {}
    pr, res, sp, osp = d["proyecto"], d["resumen"], d["sprints"], d["openspec"]
    hus = d["hus"]
    L = [f"# Onboarding — {pr.get('nombre') or 'Proyecto'}", "",
         "> Visión global para quien se incorpora. No entra en detalle: dice qué es "
         "el proyecto, dónde está y qué leer primero.", ""]

    L += ["## 1. Qué es este proyecto", "",
          nar.get("que_es") or "[PENDIENTE: falta el párrafo sobre qué es el proyecto]", ""]
    if pr.get("usuarios"):
        L += ["**Para quién:** " + " · ".join(pr["usuarios"]), ""]
    if pr.get("stack"):
        L += ["**Con qué se construye:** " + " · ".join(pr["stack"]), ""]

    L += ["## 2. Cómo se trabaja aquí", "",
          nar.get("como_se_trabaja")
          or "[PENDIENTE: falta el párrafo sobre cómo se trabaja en el proyecto]", ""]
    if osp.get("donde_se_ejecuta"):
        L += [f"**Desde dónde se ejecuta cada comando** (topología `{osp['topologia']}`):",
              "", "| Comando | Desde dónde | Quién |", "|---|---|---|"]
        L += [f"| `{x['comando']}` | {x['desde']} | {x['quien']} |"
              for x in osp["donde_se_ejecuta"]] + [""]

    L += ["## 3. Dónde estamos", ""]
    actual = next((s for s in sp["lista"] if s["nombre"] == sp["actual"]), None)
    siguiente = next((s for s in sp["lista"] if s["nombre"] == sp["siguiente"]), None)
    if not sp["lista"]:
        L.append("- **Sprints:** no hay plan de sprints. Lo genera `aiba sprint-planning`.")
    else:
        if actual:
            L.append(f"- **Sprint en curso:** {actual['nombre']}{_fechas(actual)}"
                     + (f" — {actual['objetivo']}" if actual["objetivo"] else ""))
        else:
            L.append("- **Sprint en curso:** ninguno según las fechas del plan.")
        L.append("- **Sprints cerrados:** " + (", ".join(sp["cerrados"]) or "ninguno todavía"))
        if siguiente:
            L.append(f"- **Siguiente:** {siguiente['nombre']}{_fechas(siguiente)}"
                     + (f" — {siguiente['objetivo']}" if siguiente["objetivo"] else ""))
    linea = f"- **Historias de usuario:** {res['total']} en total"
    if res.get("revision"):
        conocidos = {k for k, _, _ in REVISION}
        partes = [f"{n} {uno if n == 1 else varios}" for k, uno, varios in REVISION
                  if (n := res["revision"].get(k))]
        partes += [f"{n} {k.lower()}" for k, n in res["revision"].items()
                   if k not in conocidos]
        linea += " — con negocio: " + ", ".join(partes)
    L.append(linea + ".")
    if res["construidas"] is not None:
        L.append(f"- **Construidas:** {res['construidas']} de {res['total']}"
                 + (f", y {res['en_construccion']} en construcción"
                    if res["en_construccion"] else "") + ".")
    else:
        L.append("- **Construidas:** no se sabe todavía — el proyecto no tiene OpenSpec "
                 "que consultar." if not osp["existe_directorio"] else
                 "- **Construidas:** no se sabe — no se ha consultado OpenSpec.")
    if res["bloqueadas"]:
        L.append("- **Bloqueadas:** " + ", ".join(res["bloqueadas"]) + ".")
    L.append("")

    L += ["## 4. Qué se ha hecho", ""]
    if res["construidas"] is not None:
        hechas = [x for x in hus if x["construida"] == "sí"]
        L += (_tabla(hechas) if hechas else ["Todavía no hay ninguna historia construida.", ""])
        if res["planificadas_sin_construir"]:
            L += ["> **Ojo:** " + ", ".join(res["planificadas_sin_construir"])
                  + " estaban en sprints ya cerrados y no están construidas.", ""]
    else:
        hechas = [x for x in hus if x["sprint_estado"] == "cerrado"]
        if not sp["lista"]:
            L += ["Sin OpenSpec ni plan de sprints no se puede saber qué se ha hecho.", ""]
        else:
            L += ["Sin OpenSpec no se puede saber qué está construido. Lo que sí dice el "
                  "plan es qué estaba previsto en los sprints ya cerrados:", ""]
            L += (_tabla(hechas, con_sprint=True) if hechas
                  else ["Todavía no se ha cerrado ningún sprint.", ""])

    L += ["## 5. Qué queda", ""]
    pendientes = [x for x in hus if x["construida"] != "sí"
                  and (res["construidas"] is not None or x["sprint_estado"] != "cerrado")]
    en_curso = [x for x in pendientes if x["sprint_estado"] == "en curso"]
    futuras = [x for x in pendientes if x["sprint_estado"] in ("futuro", "sin fechas")]
    sin = [x for x in pendientes if x["sprint_estado"] == "sin sprint"]
    if en_curso:
        L += [f"### En el sprint en curso ({sp['actual']})", ""] + _tabla(en_curso)
    if futuras:
        L += ["### En los sprints siguientes", ""] + _tabla(futuras, con_sprint=True)
    if sin:
        L += ["### Sin sprint asignado", ""] + _tabla(sin)
    if not hus:
        L += ["No hay historias de usuario definidas todavía: las genera "
              "`aidd user-stories`.", ""]
    elif not (en_curso or futuras or sin):
        L += ["No queda ninguna historia pendiente.", ""]

    L += ["## 6. Qué leer y en qué orden", ""]
    if d["lectura"]:
        L += ["| # | Documento | Para quién | Qué cuenta |", "|---|---|---|---|"]
        L += [f"| {n} | `{x['ruta']}` | {x['para']} | {x['que']} |"
              for n, x in enumerate(d["lectura"], 1)] + [""]
    else:
        L += ["Todavía no hay ningún documento del proyecto que leer: el primero lo "
              "genera `aidd client-requirements`.", ""]

    faltan = [f for f in d["fuentes"] if not f["existe"]]
    L += ["## 7. Lo que falta para completar este onboarding", ""]
    if faltan:
        L += ["| Documento | Lo genera | |", "|---|---|---|"]
        L += [f"| `{f['ruta']}` | `{f['genera']}` | "
              f"{'opcional: solo dice qué está construido' if f['clave'] == 'openspec' else ''} |"
              for f in faltan] + [""]
    else:
        L += ["Nada: están todas las fuentes.", ""]
    return "\n".join(L).rstrip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Hechos y documento del onboarding del proyecto.")
    ap.add_argument("--root", default=".", help="raiz del proyecto")
    ap.add_argument("--estado", default=None,
                    help="JSON de compute_status.py (aiba-status-report), si hay OpenSpec")
    ap.add_argument("--out", default=None, help="donde escribir el JSON de hechos")
    ap.add_argument("--hoy", default=None, help="fecha de referencia AAAA-MM-DD (pruebas)")
    ap.add_argument("--render", default=None, metavar="JSON",
                    help="escribe el documento a partir de un JSON de hechos con narrativa")
    ap.add_argument("--output", default=None, help="ruta del documento (con --render)")
    args = ap.parse_args()

    if args.render:
        if not args.output:
            ap.error("--render necesita --output")
        d = json.loads(Path(args.render).read_text(encoding="utf-8"))
        salida = Path(args.output)
        salida.parent.mkdir(parents=True, exist_ok=True)
        salida.write_text(render(d), encoding="utf-8")
        print(salida)
        return 0

    if not args.out:
        ap.error("hace falta --out (calcular) o --render/--output (escribir)")
    hoy = date.fromisoformat(args.hoy) if args.hoy else date.today()
    d = calcular(Path(args.root), hoy, args.estado)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    for a in d["avisos"]:
        print(f"Aviso: {a}", file=sys.stderr)
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
