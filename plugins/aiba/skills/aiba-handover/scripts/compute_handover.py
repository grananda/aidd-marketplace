#!/usr/bin/env python3
"""aiba-handover · compute_handover.py — el traspaso a quien se queda con el sistema.

Tres modos, en el orden en que los usa el skill:

    --preparar  crea el cuestionario de lo que nunca se escribio, o le anade las
                preguntas que le falten sin tocar lo contestado.
    --out       calcula los hechos: lo que dicen los documentos, las specs, el
                archivo de changes y la auditoria, y lo contestado.
    --render    escribe el documento con los hechos y lo que anade el skill.

**Dos mitades con dos origenes.** Que hace el sistema y como esta construido ya
esta escrito --specs, arquitectura, archivo de changes--. Como se opera no lo
escribio nadie: sale del cuestionario, que rellena quien lo sabe, no
necesariamente el BA. Lo que no esta en ninguno de los dos sale como hueco
declarado: un traspaso con huecos honestos sirve, uno con relleno plausible es
peligroso, porque el equipo entrante actuara sobre el.

**La estructura sale de aqui y no del modelo**, como en el onboarding. El modelo
escribe dos parrafos, los tres diagramas que exigen leer la arquitectura y la
tabla del equipo de mantenimiento, que es un juicio. El diagrama de despliegue
no: sale del cuestionario, porque es el unico que no esta en ningun documento.

**Nunca un secreto.** El cuestionario se lee y el documento se escribe pasando
por `secretos.py`: si algo tiene pinta de contrasena, token o cadena de
conexion, el script se niega y dice donde esta, sin repetirlo.

Uso:
    python3 compute_handover.py --root . --preparar
    python3 compute_handover.py --root . --out traspaso.json [--estado estado.json]
    python3 compute_handover.py --render traspaso.json --output docs/traspaso.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
import secretos  # noqa: E402
from documentos import buscar, clave, leer_proyecto, parrafo, secciones, vinetas  # noqa: E402

CUESTIONARIO = "docs/traspaso-cuestionario.md"
ID_RE = re.compile(r"<!--\s*id:\s*([a-z_]+)\s*-->")

# De donde sale cada cosa, que aporta y que comando la genera si falta.
FUENTES = [
    ("brief", "docs/cliente-requisitos.md", "`aidd client-requirements`",
     "Qué es el sistema y para quién"),
    ("arquitectura", "docs/arquitectura-base.md", "`aidd architecture`",
     "Repositorios, integraciones y los diagramas de cómo está construido"),
    ("planificacion", "docs/planificacion-proyecto.md", "`aiba project-plan`",
     "El equipo que lo construyó y los entornos previstos"),
    ("roadmap", "docs/roadmap.md", "`aisdd roadmap`", "Qué queda por construir"),
    ("specs", "openspec/specs", "`aisdd close change`, o `aisdd init` en un proyecto existente",
     "Qué hace el sistema hoy, capacidad por capacidad"),
    ("archivo", "openspec/changes/archive", "`aisdd close change`",
     "Qué se construyó, en qué orden y con qué decisiones"),
    ("auditoria", "openspec/audit", "cualquier comando `aisdd`",
     "Quién construyó cada parte"),
]

# Lo que conviene tener a mano junto al traspaso, si existe.
ACOMPANAN = [
    ("docs/arquitectura-base.md", "Cómo está construido y por qué"),
    ("openspec/specs", "Qué hace el sistema, requisito a requisito"),
    ("docs/detalle-historias-usuario.md", "El comportamiento esperado, en lenguaje de negocio"),
    ("docs/df", "Los diseños funcionales, historia a historia"),
    ("docs/design", "Las pantallas"),
    ("docs/guia-estilos.md", "Cómo se ve"),
    ("docs/roadmap.md", "El faseado completo"),
    ("docs/onboarding.md", "La visión global del proyecto"),
]

# Lo que ningun documento dice. (tema, titulo, [(id, pregunta, pista, columnas)])
# Una pregunta con columnas se contesta con una tabla; sin ellas, con texto. El
# `id` es lo que la identifica en el fichero: el titulo se puede retocar.
TEMAS = [
    ("entornos", "Entornos", [
        ("entornos", "Qué entornos hay",
         "Una fila por entorno. Lo que importa es en qué se diferencia cada uno de "
         "producción: datos, integraciones reales o simuladas, tamaño.",
         ["Entorno", "URL", "En qué se diferencia de producción", "Quién lo administra"]),
    ]),
    ("infraestructura", "Infraestructura", [
        ("componentes", "Dónde corre cada componente",
         "Una fila por repositorio o pieza desplegable, tal como está en producción. En "
         "«Se conecta con», los nombres de otras filas, de un almacén de datos o de un "
         "servicio externo, separados por comas: con eso se dibuja el diagrama de despliegue.",
         ["Componente", "Dónde corre (producción)", "Recursos", "Se conecta con",
          "Quién lo administra"]),
    ]),
    ("despliegue", "Despliegue", [
        ("como_se_despliega", "Cómo se despliega",
         "Pipeline, pasos manuales y quién puede lanzarlo.", None),
        ("cuanto_tarda", "Cuánto tarda",
         "Desde que se lanza hasta que está en producción, y si hay corte de servicio.", None),
        ("vuelta_atras", "Cómo se vuelve atrás",
         "Los pasos, no la intención. Si nunca se ha hecho, dilo.", None),
        ("fallo_a_medias", "Qué se rompe si falla a medias",
         "Migraciones de datos, cachés, colas: lo que queda a medio hacer.", None),
    ]),
    ("datos", "Datos", [
        ("almacenes", "Dónde están los datos y cómo se copian",
         "Una fila por base de datos o almacén. En la última columna, la fecha de la "
         "última restauración probada; si nadie la ha probado, escribe «nunca».",
         ["Almacén", "Dónde está", "Cómo y cada cuánto se copia",
          "Última restauración probada"]),
    ]),
    ("operacion", "Operación", [
        ("logs", "Dónde están los logs",
         "Herramienta, ruta o consulta, y cuánto tiempo se guardan.", None),
        ("metricas", "Dónde están las métricas", "Paneles y herramienta.", None),
        ("alertas", "Qué alertas hay y a quién avisan",
         "Una fila por alerta. Una alerta que no avisa a nadie es un registro, no una alerta.",
         ["Alerta", "Qué la dispara", "A quién avisa"]),
    ]),
    ("accesos", "Accesos y secretos", [
        ("accesos", "Qué accesos hay que pedir",
         "Cuentas, permisos, VPN, repositorios. A quién se piden y con cuánta antelación: "
         "es lo que bloquea el primer día.",
         ["Acceso", "A quién se pide", "Con cuánta antelación"]),
        ("secretos", "Dónde viven los secretos",
         "El gestor y la ruta, y quién da acceso. Nunca el valor.",
         ["Secreto", "Dónde vive (gestor y ruta)", "Quién da acceso"]),
    ]),
    ("dependencias", "Dependencias externas", [
        ("servicios", "Qué servicios de terceros se usan",
         "Contrato o licencia, quién lo paga y a quién se llama cuando falla.",
         ["Servicio", "Para qué", "Contrato", "Quién lo paga", "Contacto"]),
    ]),
    ("incidencias", "Lo que se rompe a menudo", [
        ("habituales", "Lo que se rompe a menudo",
         "La lista que todo equipo tiene en la cabeza y nadie escribe.",
         ["Síntoma", "Causa habitual", "Cómo se arregla"]),
    ]),
    ("contactos", "Contactos", [
        ("contactos", "Quién sabe de qué",
         "Incluidos los de fuera del equipo: el cliente, sistemas, los proveedores.",
         ["Quién", "De qué sabe", "Cómo localizarle"]),
    ]),
    ("cobertura", "Cobertura del mantenimiento", [
        ("horario", "En qué horario se da servicio", "", None),
        ("guardias", "Si hay guardias, y cómo funcionan", "", None),
        ("ausencias", "Qué pasa cuando el único que sabe de algo no está", "", None),
    ]),
]
PREGUNTAS = {q[0]: {"tema": titulo, "pregunta": q[1], "pista": q[2], "columnas": q[3]}
             for _, titulo, preguntas in TEMAS for q in preguntas}

# El diagrama que se espera en cada clave de `diagramas`. El de despliegue no
# esta: lo dibuja este script con el cuestionario.
TIPOS_DIAGRAMA = {
    "contexto": ("flowchart", "graph", "C4Context", "C4Container"),
    "flujos": ("sequenceDiagram",),
    "datos": ("erDiagram", "classDiagram"),
}

# Los comandos que dejan conocimiento del codigo en quien los ejecuta. Abrir un
# change es escribir su spec; implementarlo, enmendarlo y cerrarlo es conocerlo.
CONOCIMIENTO = ("implement change", "amend change", "close change")

# «nunca», «no», «nadie»: al principio de una celda corta es la respuesta
# entera. En un texto largo solo cuenta si lo dice explicitamente: «No hay
# rollback automatico; se redespliega la anterior» no es «nunca se ha probado».
NUNCA_CELDA = re.compile(r"^\s*(?:nunca|no\b|nadie|sin probar|jam[aá]s)", re.I)
NUNCA_TEXTO = re.compile(r"\bnunca\b|\bno se ha probado\b|\bsin probar\b|\bnadie lo ha\b",
                         re.I)


# --- Lectura de las fuentes --------------------------------------------------

def _tablas(texto: str) -> list[list[list[str]]]:
    """Cada tabla markdown del texto, con su cabecera y sin la linea separadora."""
    tablas, actual = [], []
    for l in texto.splitlines():
        if l.lstrip().startswith("|"):
            actual.append([c.strip() for c in l.strip().strip("|").split("|")])
        elif actual:
            tablas.append(actual)
            actual = []
    if actual:
        tablas.append(actual)
    return [[f for f in t if not all(re.fullmatch(r":?-{2,}:?", c) or not c for c in f)]
            for t in tablas]


def _limpio(texto: str) -> str:
    return re.sub(r"[*`]", "", texto or "").strip()


def _nombres(cuerpo: str, n: int = 12) -> list[str]:
    """Nombres de una seccion: la primera columna de sus tablas o sus vinetas."""
    fuera = [f[0] for t in _tablas(cuerpo) for f in t[1:] if f and f[0]]
    if not fuera:
        for v in vinetas(cuerpo, 40):
            m = re.match(r"\*\*(.+?)\*\*", v) or re.match(r"([^:—–(]{2,60}?)\s*[:—–(]", v)
            if m:
                fuera.append(m.group(1))
    limpios: list[str] = []
    for x in map(_limpio, fuera):
        if x and len(x) <= 60 and x not in limpios:
            limpios.append(x)
    return limpios[:n]


def leer_arquitectura(root: Path) -> dict:
    f = root / "docs" / "arquitectura-base.md"
    if not f.is_file():
        return {"existe": False, "repositorios": [], "integraciones": []}
    md = f.read_text(encoding="utf-8", errors="replace")
    repos = []
    m = re.search(r"^###\s+Repositorios\s*$(.*?)(?=^#{2,3}\s|\Z)", md, re.M | re.S)
    for t in _tablas(m.group(1)) if m else []:
        for fila in t[1:]:
            if fila and _limpio(fila[0]):
                repos.append({"id": _limpio(fila[0]),
                              "contiene": fila[1] if len(fila) > 1 else ""})
    return {"existe": True, "repositorios": repos,
            "integraciones": _nombres(buscar(secciones(md), "integracion"))}


def leer_planificacion(root: Path) -> dict:
    f = root / "docs" / "planificacion-proyecto.md"
    if not f.is_file():
        return {"existe": False, "perfiles": [], "perfiles_texto": "", "entornos_previstos": ""}
    sec = secciones(f.read_text(encoding="utf-8", errors="replace"))
    cuerpo = buscar(sec, "perfiles")
    perfiles = []
    for t in _tablas(cuerpo):
        cab = [clave(c) for c in t[0]]
        ip = next((i for i, c in enumerate(cab) if "perfil" in c or c == "rol"), 0)
        idd = next((i for i, c in enumerate(cab) if "dedicacion" in c), None)
        for fila in t[1:]:
            if len(fila) > ip and _limpio(fila[ip]):
                perfiles.append({"perfil": _limpio(fila[ip]),
                                 "dedicacion": (fila[idd] if idd is not None
                                                and idd < len(fila) else "")})
    return {"existe": True, "perfiles": perfiles, "perfiles_texto": cuerpo.strip()[:2500],
            "entornos_previstos": parrafo(buscar(sec, "infraestructura"), 300)}


def leer_specs(root: Path) -> list[dict]:
    """Lo que el sistema hace hoy: una fila por capacidad de `openspec/specs/`."""
    base = root / "openspec" / "specs"
    if not base.is_dir():
        return []
    fuera = []
    for d in sorted(x for x in base.iterdir() if (x / "spec.md").is_file()):
        md = (d / "spec.md").read_text(encoding="utf-8", errors="replace")
        sec = secciones(md)
        proposito = parrafo(buscar(sec, "purpose") or buscar(sec, "proposito"), 220)
        # Al archivar un change que crea una capacidad, OpenSpec deja
        # `TBD - created by archiving change ...` como proposito.
        if re.match(r"(?i)^tbd\b", proposito):
            proposito = ""
        fuera.append({"capacidad": d.name, "proposito": proposito,
                      "requisitos": len(re.findall(r"^###\s+(?:Requirement|Requisito)\b",
                                                   md, re.M | re.I))})
    return fuera


def leer_decisiones(f: Path) -> list[dict]:
    """Las entradas de un `decisions.md`: `## slug` y sus campos en negrita."""
    if not f.is_file():
        return []
    fuera = []
    for bloque in re.split(r"^##\s+", f.read_text(encoding="utf-8", errors="replace"),
                           flags=re.M)[1:]:
        slug, _, cuerpo = bloque.partition("\n")

        def campo(nombre: str) -> str:
            m = re.search(rf"^\s*-\s*\*\*{nombre}\*\*\s*:\s*(.+)$", cuerpo, re.M | re.I)
            return m.group(1).strip() if m else ""

        fuera.append({"slug": slug.strip(), "tipo": campo("Tipo"),
                      "decision": campo("Decisi[oó]n"), "porque": campo("Justificaci[oó]n")})
    return fuera


def leer_archivo(root: Path, cierres: dict) -> list[dict]:
    """Los changes cerrados, en el orden en que se cerraron."""
    base = root / "openspec" / "changes" / "archive"
    if not base.is_dir():
        return []
    fuera = []
    for d in (x for x in base.iterdir() if x.is_dir()):
        m = re.match(r"^(\d{4}-\d{2}-\d{2})-(.+)$", d.name)
        cid = m.group(2) if m else d.name
        specs = d / "specs"
        fuera.append({"change": cid, "fecha": m.group(1) if m else cierres.get(cid, ""),
                      "capacidades": sorted(x.name for x in specs.iterdir() if x.is_dir())
                      if specs.is_dir() else [],
                      "decisiones": leer_decisiones(d / "decisions.md")})
    return sorted(fuera, key=lambda c: (c["fecha"] or "9999", c["change"]))


def _persona(e: dict, f: Path) -> str:
    """Quien escribio la entrada: el `user`, o el nombre de su fichero."""
    u = str(e.get("user") or "").strip()
    m = re.search(r"<([^>]+)>", u)
    if m:
        return m.group(1).strip()
    if u and u.lower() not in ("null", "none"):
        return u
    # Disposicion nueva: `YYYY-MM/<quien>.jsonl`. En la anterior el fichero es
    # el mes y no dice nada de quien escribio.
    return f.stem if re.fullmatch(r"\d{4}-\d{2}", f.parent.name) else "desconocido"


def leer_autoria(root: Path) -> dict:
    d = root / "openspec" / "audit"
    if not d.is_dir():
        return {"disponible": False, "por_change": {}, "cierres": {}}
    por_change: dict[str, set] = {}
    cierres: dict[str, str] = {}
    vistos: set[str] = set()
    for f in sorted(list(d.glob("*.jsonl")) + list(d.glob("*/*.jsonl"))):
        for linea in f.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                e = json.loads(linea)
            except json.JSONDecodeError:
                continue
            eid = str(e.get("id") or "")
            if eid and eid in vistos:
                continue
            vistos.add(eid)
            cid, cmd = e.get("change_id"), str(e.get("command") or "")
            if cid and any(c in cmd for c in CONOCIMIENTO):
                por_change.setdefault(cid, set()).add(_persona(e, f))
            if cid and "close change" in cmd and e.get("timestamp"):
                cierres[cid] = str(e["timestamp"])[:10]
    return {"disponible": True, "por_change": {k: sorted(v) for k, v in por_change.items()},
            "cierres": cierres}


def conocimiento(archivo: list, autoria: dict) -> dict:
    """Que parte del sistema conoce una sola persona. Sale de la auditoria."""
    if not autoria["disponible"]:
        return {"disponible": False}
    caps: dict[str, dict] = {}
    por_change = []
    for ch in archivo:
        pers = sorted(set(autoria["por_change"].get(ch["change"], [])) - {"desconocido"})
        por_change.append({"change": ch["change"], "personas": pers})
        for cap in ch["capacidades"]:
            r = caps.setdefault(cap, {"changes": 0, "personas": set()})
            r["changes"] += 1
            r["personas"] |= set(pers)
    todas = sorted({p for c in por_change for p in c["personas"]})
    return {"disponible": True, "personas": todas, "una_sola_global": len(todas) == 1,
            "por_capacidad": [{"capacidad": k, "changes": v["changes"],
                               "personas": sorted(v["personas"]),
                               "una_sola": len(v["personas"]) == 1}
                              for k, v in sorted(caps.items())],
            "por_change": por_change,
            "sin_autor": [c["change"] for c in por_change if not c["personas"]]}


def leer_estado(ruta: str | None, avisos: list) -> dict | None:
    if not ruta:
        return None
    p = Path(ruta)
    if not p.is_file():
        avisos.append(f"no existe {ruta}: sin el estado de OpenSpec el traspaso no dice "
                      "qué queda por construir")
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        avisos.append(f"{ruta} no se puede leer ({e}): se sigue sin el estado de OpenSpec")
        return None


def _num(i: str) -> tuple:
    m = re.search(r"\d+", i)
    return (int(m.group()) if m else 10 ** 6, i)


def pendiente(estado: dict | None) -> dict | None:
    if estado is None:
        return None
    av = estado.get("avance") or {}
    ch, hus = av.get("changes") or {}, av.get("hus") or {}
    dep = estado.get("dependencias") or {}
    todas, ok = set(hus.get("ids_todas") or []), set(hus.get("ids_ok") or [])
    curso = set(hus.get("ids_en_curso") or [])
    return {"total": ch.get("total", 0), "cerrados": ch.get("cerrados", 0),
            "activos": ch.get("activos", 0), "pendientes": ch.get("pendientes", 0),
            "en_curso": ch.get("ids_activos") or [],
            "listas": dep.get("listas") or [], "bloqueadas": dep.get("bloqueadas") or [],
            "hus_pendientes": sorted(todas - ok - curso, key=_num),
            "hus_en_curso": sorted(curso, key=_num)}


# --- Cuestionario ------------------------------------------------------------

def leer_cuestionario(ruta: Path) -> dict:
    if not ruta.is_file():
        return {"existe": False, "respuestas": {}}
    texto = ruta.read_text(encoding="utf-8", errors="replace")
    respuestas: dict[str, dict] = {}
    for bloque in re.split(r"^(?=#{1,3}\s)", texto, flags=re.M):
        cab, _, cuerpo = bloque.partition("\n")
        m = ID_RE.search(cab)
        if not (cab.startswith("### ") and m and m.group(1) in PREGUNTAS):
            continue
        qid = m.group(1)
        cuerpo = re.sub(r"<!--.*?-->", "", cuerpo, flags=re.S)
        # Las citas son las pistas del cuestionario, no respuestas.
        lineas = [l for l in cuerpo.splitlines() if not l.lstrip().startswith(">")]
        columnas = PREGUNTAS[qid]["columnas"]
        if columnas:
            n = len(columnas)
            filas, sin = [], []
            for t in _tablas("\n".join(lineas)):
                for fila in t[1:]:
                    fila = (fila + [""] * n)[:n]
                    if not any(fila):
                        continue
                    if any(fila[1:]):
                        filas.append(fila)
                    else:
                        # Solo la primera celda es lo precargado: la fila esta
                        # nombrada, pero nadie la ha contestado.
                        sin.append(fila[0])
            respuestas[qid] = {"filas": filas, "sin_contestar": sin}
        else:
            # Una respuesta de texto puede traer su propia tabla: se conserva.
            valor = "\n".join(l.rstrip() for l in lineas)
            respuestas[qid] = {"valor": re.sub(r"\n{3,}", "\n\n", valor).strip()}
    return {"existe": True, "respuestas": respuestas}


def _contestada(r: dict | None) -> bool:
    return bool(r and (r.get("filas") or r.get("valor")))


def _filas(r: dict | None) -> list[list[str]]:
    return list((r or {}).get("filas") or [])


def _celda(fila: list[str], i: int) -> str:
    return fila[i].strip() if i < len(fila) else ""


def _bloque(q: tuple, filas: list[str] | None, extra: str | None) -> list[str]:
    qid, pregunta, pista, columnas = q
    L = [f"### {pregunta} <!-- id: {qid} -->", ""]
    notas = [x for x in (pista, extra) if x]
    for k, x in enumerate(notas):
        L += ([">"] if k else []) + [f"> {x}"]
    if notas:
        L.append("")
    if columnas:
        L.append("| " + " | ".join(columnas) + " |")
        L.append("|" + "---|" * len(columnas))
        for f in filas or [""]:
            L.append("| " + " | ".join([f] + [""] * (len(columnas) - 1)) + " |")
    L.append("")
    return L


def precarga(root: Path, avisos: list) -> tuple[dict, dict]:
    """Lo que ya se sabe antes de preguntar: filas nombradas y pistas."""
    arq, plan = leer_arquitectura(root), leer_planificacion(root)
    aut = leer_autoria(root)
    personas = sorted({p for v in aut["por_change"].values() for p in v} - {"desconocido"})
    filas = {"entornos": ["Desarrollo", "Preproducción", "Producción"],
             "componentes": [r["id"] for r in arq["repositorios"]] or [root.resolve().name],
             "servicios": arq["integraciones"], "contactos": personas}
    extra = {}
    if plan["entornos_previstos"]:
        extra["entornos"] = "La planificación preveía: " + plan["entornos_previstos"]
    if arq["repositorios"]:
        extra["componentes"] = "Precargados los repositorios de `docs/arquitectura-base.md`."
    if arq["integraciones"]:
        extra["servicios"] = ("Precargadas las integraciones de `docs/arquitectura-base.md`: "
                              "borra las que no sean de terceros.")
    if personas:
        extra["contactos"] = "Precargadas las personas que aparecen en la auditoría de OpenSpec."
    # Lo precargado viene de documentos que nadie ha revisado buscando secretos,
    # y el cuestionario se versiona: lo sospechoso no se copia.
    for k in list(extra):
        if secretos.buscar(extra[k]):
            del extra[k]
            avisos.append(f"lo que se iba a precargar en «{PREGUNTAS[k]['pregunta']}» tiene "
                          "pinta de secreto y no se copia: revisa el documento de origen")
    for k in filas:
        filas[k] = [x for x in filas[k] if not secretos.buscar(x)]
    return filas, extra


def escribir_cuestionario(nombre: str, filas: dict, extra: dict) -> str:
    L = [f"# Cuestionario de traspaso — {nombre}", "",
         "> Lo que el traspaso necesita y ningún documento del proyecto dice. Lo rellena "
         "quien lo sepa —desarrollo, sistemas, el propio BA—, y al volver a lanzar "
         "`aiba handover` lo contestado entra en el documento y lo que no, sale como hueco.",
         ">",
         "> **Nunca escribas un secreto.** Ni contraseñas, ni tokens, ni cadenas de conexión, "
         "ni claves: escribe dónde viven —qué gestor, qué ruta— y quién da acceso. Si el "
         "comando encuentra algo con pinta de secreto, se detiene.",
         ">",
         "> «No aplica» y «no se sabe» son respuestas. La segunda vale mucho: «nadie ha "
         "probado a restaurar» es justo lo que necesita saber quien se queda con esto.",
         ">",
         "> Contesta debajo de cada pregunta, fuera de las citas, o rellenando las tablas; "
         "añade o borra filas. No toques los comentarios `<!-- id: ... -->`: es como el "
         "comando reconoce cada pregunta.", ""]
    for i, (_, titulo, preguntas) in enumerate(TEMAS, 1):
        L += [f"## {i}. {titulo}", ""]
        for q in preguntas:
            L += _bloque(q, filas.get(q[0]), extra.get(q[0]))
    return "\n".join(L).rstrip() + "\n"


def estado_cuestionario(ruta: Path) -> tuple[int, int]:
    resp = leer_cuestionario(ruta)["respuestas"]
    return sum(1 for q in PREGUNTAS if _contestada(resp.get(q))), len(PREGUNTAS)


def preparar(root: Path, ruta: Path) -> tuple[int, list[str]]:
    """Crea el cuestionario o le anade lo que falte. Nunca toca lo contestado."""
    avisos: list[str] = []
    if ruta.is_file():
        texto = ruta.read_text(encoding="utf-8", errors="replace")
        hall = secretos.buscar(texto)
        if hall:
            return 2, secretos.informe(hall, str(ruta))
        presentes = set(ID_RE.findall(texto))
        faltan = [q for _, _, ps in TEMAS for q in ps if q[0] not in presentes]
        if faltan:
            filas, extra = precarga(root, avisos)
            add = [""]
            for _, titulo, ps in TEMAS:
                nuevas = [q for q in ps if q in faltan]
                if nuevas:
                    add += [f"## {titulo}", ""]
                    for q in nuevas:
                        add += _bloque(q, filas.get(q[0]), extra.get(q[0]))
            ruta.write_text(texto.rstrip("\n") + "\n" + "\n".join(add).rstrip() + "\n",
                            encoding="utf-8")
        c, t = estado_cuestionario(ruta)
        return 0, avisos + [f"{ruta}: {c} de {t} preguntas contestadas; "
                            + (f"añadidas {len(faltan)} que faltaban" if faltan
                               else "sin cambios")]
    filas, extra = precarga(root, avisos)
    nombre = leer_proyecto(root)["nombre"] or root.resolve().name
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(escribir_cuestionario(nombre, filas, extra), encoding="utf-8")
    return 0, avisos + [f"{ruta}: creado, 0 de {len(PREGUNTAS)} preguntas contestadas"]


# --- Calculo -----------------------------------------------------------------

def _esc(t: str) -> str:
    return re.sub(r"\s+", " ", (t or "").replace('"', "'")).strip()


def _encaja(k: str, nodos: dict) -> str | None:
    if k in nodos:
        return k
    cand = [n for n in nodos if n and (n.startswith(k) or k.startswith(n))]
    return cand[0] if len(cand) == 1 else None


def diagrama_despliegue(resp: dict) -> dict:
    """La topologia de produccion, dibujada con las tablas del cuestionario."""
    comp = _filas(resp.get("componentes"))
    if not comp:
        return {"mermaid": None,
                "motivo": "la tabla de componentes del cuestionario está sin contestar"}
    # Almacenes y servicios nombrados: los contestados salen siempre; los que
    # solo estan precargados, si algun componente se conecta con ellos.
    candidatos: dict[str, tuple] = {}
    for tipo, r in (("d", resp.get("almacenes")), ("e", resp.get("servicios"))):
        for f in _filas(r):
            candidatos.setdefault(clave(f[0]), (tipo, f[0], _celda(f, 1), True))
        for nombre in (r or {}).get("sin_contestar") or []:
            candidatos.setdefault(clave(nombre), (tipo, nombre, "", False))
    L, nodos, cuenta = ["flowchart LR"], {}, {"c": 0, "d": 0, "e": 0, "x": 0}

    def nodo(tipo: str, nombre: str, donde: str = "") -> str:
        cuenta[tipo] += 1
        i = f"{tipo}{cuenta[tipo]}"
        nodos[clave(nombre)] = i
        texto = _esc(nombre) + (f"<br/>{_esc(donde)}" if donde else "")
        forma = {"d": '[("%s")]', "e": '{{"%s"}}'}.get(tipo, '["%s"]') % texto
        L.append(f"  {i}{forma}")
        return i

    grupos: dict[str, list] = {}
    for f in comp:
        grupos.setdefault(_celda(f, 1) or "Sin dato de dónde corre", []).append(f)
    for g, (donde, filas) in enumerate(grupos.items()):
        L.append(f'  subgraph g{g}["{_esc(donde)}"]')
        for f in filas:
            nodo("c", f[0] or "(sin nombre)")
            L[-1] = "  " + L[-1]            # dentro del subgraph
        L.append("  end")
    for k, (tipo, nombre, donde, contestado) in candidatos.items():
        if contestado and k not in nodos:
            nodo(tipo, nombre, donde)
    aristas: list[tuple[str, str]] = []
    for f in comp:
        origen = nodos[clave(f[0] or "(sin nombre)")]
        for destino in (x.strip() for x in re.split(r"[,;]", _celda(f, 3))):
            if not destino:
                continue
            k = _encaja(clave(destino), nodos)
            if k is None:
                kc = _encaja(clave(destino), candidatos)
                if kc is not None:
                    tipo, nombre, donde, _ = candidatos[kc]
                    nodo(tipo, nombre, donde)
                    k = clave(nombre)
                else:
                    nodo("x", destino)
                    k = clave(destino)
            if (origen, nodos[k]) not in aristas and origen != nodos[k]:
                aristas.append((origen, nodos[k]))
    L += [f"  {a} --> {b}" for a, b in aristas]
    return {"mermaid": "\n".join(L), "nodos": len(nodos), "conexiones": len(aristas)}


def calcular_riesgos(resp: dict, cono: dict) -> list[str]:
    """Lo que un equipo entrante tiene que saber antes de firmar."""
    r = []
    for f in _filas(resp.get("almacenes")):
        prueba = _celda(f, 3)
        if not prueba:
            r.append(f"No consta que se haya probado a restaurar «{f[0]}».")
        elif NUNCA_CELDA.match(prueba):
            r.append(f"Nunca se ha probado a restaurar «{f[0]}»: una copia que no se ha "
                     "restaurado nunca no se sabe si sirve.")
    va = (resp.get("vuelta_atras") or {}).get("valor", "")
    if va and NUNCA_TEXTO.search(va):
        r.append("La vuelta atrás de un despliegue no está probada.")
    for f in _filas(resp.get("alertas")):
        if not _celda(f, 2):
            r.append(f"La alerta «{f[0]}» no avisa a nadie.")
    for f in _filas(resp.get("componentes")):
        if not _celda(f, 4):
            r.append(f"No consta quién administra «{f[0]}».")
    if cono.get("disponible"):
        if cono["una_sola_global"]:
            r.append(f"Todo lo construido con OpenSpec lo ha hecho una sola persona "
                     f"({cono['personas'][0]}): es el traspaso de una persona, no de un equipo.")
        else:
            r += [f"«{c['capacidad']}» la ha construido solo {c['personas'][0]}: si no está, "
                  "nadie más la conoce." for c in cono["por_capacidad"] if c["una_sola"]]
    return r


def calcular(root: Path, hoy: date, ruta_estado: str | None, ruta_c: Path) -> dict:
    avisos: list[str] = []
    estado = leer_estado(ruta_estado, avisos)
    if estado is None and (root / "openspec").is_dir() and not ruta_estado:
        avisos.append("hay openspec/ pero no se ha pasado --estado: el traspaso no dirá "
                      "qué queda por construir")
    proyecto = leer_proyecto(root)
    proyecto["nombre"] = (proyecto["nombre"] or (estado or {}).get("proyecto")
                          or root.resolve().name)
    autoria = leer_autoria(root)
    archivo = leer_archivo(root, autoria["cierres"])
    cono = conocimiento(archivo, autoria)
    cu = leer_cuestionario(ruta_c)
    try:
        rel = str(ruta_c.resolve().relative_to(root.resolve()))
    except ValueError:
        rel = str(ruta_c)
    if not cu["existe"]:
        avisos.append(f"no existe {rel}: todo lo operativo sale como hueco. Lo crea "
                      "`compute_handover.py --preparar`")
    resp = cu["respuestas"]
    sin = [{"id": q, "tema": p["tema"], "pregunta": p["pregunta"]}
           for q, p in PREGUNTAS.items() if not _contestada(resp.get(q))]
    fuentes = [{"clave": c, "ruta": r, "existe": (root / r).exists(), "genera": g, "aporta": a}
               for c, r, g, a in FUENTES]
    fuentes.append({"clave": "cuestionario", "ruta": rel, "existe": cu["existe"],
                    "genera": "`aiba handover`",
                    "aporta": "Cómo se opera: entornos, despliegue, datos, accesos, contactos"})
    if not archivo and (root / "openspec").is_dir():
        avisos.append("no hay changes archivados: sin ellos no se sabe qué se construyó "
                      "ni quién lo conoce")
    return {
        "generado": hoy.isoformat(),
        "proyecto": proyecto,
        "fuentes": fuentes,
        "cuestionario": {"ruta": rel, "existe": cu["existe"], "total": len(PREGUNTAS),
                         "contestadas": len(PREGUNTAS) - len(sin), "sin_contestar": sin,
                         "respuestas": resp},
        "arquitectura": leer_arquitectura(root),
        "planificacion": leer_planificacion(root),
        "specs": leer_specs(root),
        "archivo": archivo,
        "conocimiento": cono,
        "pendiente": pendiente(estado),
        "despliegue": diagrama_despliegue(resp),
        "riesgos": calcular_riesgos(resp, cono),
        "acompanan": [{"ruta": r, "que": q} for r, q in ACOMPANAN if (root / r).exists()],
        "avisos": avisos,
    }


# --- Documento ---------------------------------------------------------------

def _c(t) -> str:
    """Texto seguro dentro de una celda de tabla."""
    return re.sub(r"\s+", " ", str(t or "")).replace("|", "\\|").strip()


def _corta(t: str, n: int = 160) -> str:
    t = _c(t)
    return t if len(t) <= n else t[:n - 1].rstrip() + "…"


def _hueco(texto: str) -> list[str]:
    return [f"> **Hueco:** {texto}", ""]


def _sin_contestar(qid: str) -> list[str]:
    return _hueco(f"«{PREGUNTAS[qid]['pregunta']}» está sin contestar en el cuestionario.")


def _texto(d: dict, qid: str) -> list[str]:
    valor = (d["cuestionario"]["respuestas"].get(qid) or {}).get("valor")
    return [valor, ""] if valor else _sin_contestar(qid)


def _tabla(d: dict, qid: str) -> list[str]:
    r = d["cuestionario"]["respuestas"].get(qid) or {}
    cols = PREGUNTAS[qid]["columnas"]
    if not r.get("filas"):
        return _sin_contestar(qid)
    L = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for f in r["filas"]:
        L.append("| " + " | ".join(_c(_celda(f, i)) or "*sin dato*"
                                  for i in range(len(cols))) + " |")
    L.append("")
    if r.get("sin_contestar"):
        L += [f"> **Sin contestar:** {', '.join(r['sin_contestar'])}.", ""]
    return L


def _diagrama(texto, permitidos: tuple) -> tuple[str | None, str | None]:
    if not isinstance(texto, str) or not texto.strip():
        return None, None
    t = re.sub(r"^\s*```(?:mermaid)?[^\n]*\n|\n?```\s*$", "", texto.strip()).strip()
    primera = next((l.strip() for l in t.splitlines()
                    if l.strip() and not l.strip().startswith("%%")), "")
    tipo = primera.split()[0] if primera else ""
    if tipo not in permitidos:
        return None, (f"empieza por «{tipo}» y tiene que ser " + " o ".join(permitidos))
    return t, None


def _mermaid(t: str) -> list[str]:
    return ["```mermaid", t, "```", ""]


def _fte(txt) -> float | None:
    """La dedicacion como fraccion de jornada, si se puede leer."""
    txt = str(txt or "")
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*%", txt)
    if m:
        return float(m.group(1).replace(",", ".")) / 100
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:FTE|jornadas?)\b", txt, re.I)
    if m:
        return float(m.group(1).replace(",", "."))
    if re.search(r"media jornada", txt, re.I):
        return 0.5
    if re.search(r"jornada completa|tiempo completo|full[- ]time", txt, re.I):
        return 1.0
    return None


def _num_es(x: float) -> str:
    return f"{x:.2f}".rstrip("0").rstrip(".").replace(".", ",")


def _n(n: int, palabra: str) -> str:
    return f"{n} {palabra}{'' if n == 1 else 's'}"


def render(d: dict) -> tuple[str, list[str]]:
    nar = d.get("narrativa") or {}
    dia = d.get("diagramas") or {}
    equipo = d.get("equipo") or {}
    pr, cu = d["proyecto"], d["cuestionario"]
    avisos: list[str] = []

    # Lo que aporta el skill se valida antes de escribir nada, porque sus huecos
    # tambien van a la seccion 1.
    diagramas = {}
    for k in ("contexto", "datos"):
        diagramas[k], motivo = _diagrama(dia.get(k), TIPOS_DIAGRAMA[k])
        if motivo:
            avisos.append(f"el diagrama «{k}» no se incluye: {motivo}")
    flujos = []
    for i, f in enumerate(dia.get("flujos") or []):
        t, motivo = _diagrama((f or {}).get("mermaid"), TIPOS_DIAGRAMA["flujos"])
        if t:
            flujos.append((str(f.get("titulo") or f"Flujo {i + 1}"), t))
        elif motivo:
            avisos.append(f"el flujo {i + 1} no se incluye: {motivo}")
    perfiles = [p for p in equipo.get("perfiles") or [] if isinstance(p, dict)]
    sin_dedicacion = [p.get("perfil") or "(sin nombre)" for p in perfiles
                      if _fte(p.get("dedicacion")) is None]
    sin_escribir = []
    if not perfiles:
        sin_escribir.append("Falta la tabla del equipo de mantenimiento.")
    elif sin_dedicacion:
        sin_escribir.append("Falta la dedicación de " + ", ".join(sin_dedicacion)
                            + ": sin ella no se puede presupuestar.")
    if not equipo.get("diferencias"):
        sin_escribir.append("Falta decir en qué se diferencia del equipo que lo construyó.")
    faltan_diag = [n for n, v in (("de contexto y contenedores", diagramas["contexto"]),
                                  ("de los flujos críticos", flujos),
                                  ("del modelo de datos", diagramas["datos"])) if not v]
    if len(faltan_diag) == 1:
        sin_escribir.append(f"Falta el diagrama {faltan_diag[0]}.")
    elif faltan_diag:
        sin_escribir.append("Faltan los diagramas " + ", ".join(faltan_diag[:-1])
                            + f" y {faltan_diag[-1]}.")

    L = [f"# Traspaso — {pr.get('nombre') or 'Proyecto'}", "",
         "> Para el equipo que se hace cargo del sistema. Lo operativo va primero; el porqué "
         "de las decisiones y lo que queda por construir, al final. Los huecos están "
         "marcados a propósito: un traspaso con huecos honestos sirve, uno con relleno "
         "plausible es peligroso.", ">",
         "> No contiene secretos: dice dónde viven y quién da acceso.", ""]

    L += ["## 1. Lo que hay que resolver antes de cerrar el traspaso", ""]
    if d["riesgos"]:
        L += ["**Riesgos**", ""] + [f"- {x}" for x in d["riesgos"]] + [""]
    if cu["sin_contestar"]:
        L += [f"**Sin contestar en el cuestionario** ({len(cu['sin_contestar'])} de "
              f"{cu['total']}, en `{cu['ruta']}`)", ""]
        por_tema: dict[str, list] = {}
        for s in cu["sin_contestar"]:
            por_tema.setdefault(s["tema"], []).append(s["pregunta"].lower())
        # Punto y coma entre preguntas: alguna lleva coma dentro. Y sin repetir
        # el tema cuando la unica pregunta dice lo mismo.
        for t, ps in por_tema.items():
            L.append(f"- {t}." if ps == [t.lower()] else f"- {t}: {'; '.join(ps)}.")
        L.append("")
    if sin_escribir:
        L += ["**Sin escribir**", ""] + [f"- {x}" for x in sin_escribir] + [""]
    faltan = [f for f in d["fuentes"] if not f["existe"] and f["clave"] != "cuestionario"]
    if faltan:
        L += ["**Fuentes que faltan:** " + ", ".join(f"`{f['ruta']}`" for f in faltan)
              + ". La sección 15 dice qué comando genera cada una.", ""]
    if not (d["riesgos"] or cu["sin_contestar"] or sin_escribir or faltan):
        L += ["Nada pendiente: el cuestionario está completo, no falta ninguna fuente y no "
              "se ha detectado ningún riesgo.", ""]

    L += ["## 2. Qué es el sistema", "",
          nar.get("que_es") or "[PENDIENTE: falta el párrafo sobre qué es el sistema]", ""]
    if pr.get("usuarios"):
        L += ["**Para quién:** " + " · ".join(pr["usuarios"]), ""]
    if pr.get("stack"):
        L += ["**Con qué está construido:** " + " · ".join(pr["stack"]), ""]

    L += ["## 3. Dónde corre", "", "### Entornos", ""] + _tabla(d, "entornos")
    L += ["### Componentes", ""] + _tabla(d, "componentes")
    L += ["### Topología de despliegue", ""]
    if d["despliegue"].get("mermaid"):
        L += ["Dibujada con la tabla de componentes: dónde corre cada uno en producción y "
              "con qué se conecta.", ""] + _mermaid(d["despliegue"]["mermaid"])
    else:
        L += _hueco(f"sin diagrama de despliegue: {d['despliegue'].get('motivo')}.")

    L += ["## 4. Despliegue", ""]
    for q in ("como_se_despliega", "cuanto_tarda", "vuelta_atras", "fallo_a_medias"):
        L += [f"### {PREGUNTAS[q]['pregunta']}", ""] + _texto(d, q)
    L += ["## 5. Datos", ""] + _tabla(d, "almacenes")
    L += ["## 6. Operación", "", "### Logs", ""] + _texto(d, "logs")
    L += ["### Métricas", ""] + _texto(d, "metricas")
    L += ["### Alertas", ""] + _tabla(d, "alertas")
    L += ["## 7. Accesos y secretos", "", "### Qué accesos hay que pedir", ""]
    L += _tabla(d, "accesos")
    L += ["### Dónde viven los secretos", "",
          "Solo dónde viven y quién da acceso: este documento no lleva ningún valor.", ""]
    L += _tabla(d, "secretos")
    L += ["## 8. Dependencias externas", ""] + _tabla(d, "servicios")
    L += ["## 9. Lo que se rompe a menudo", ""] + _tabla(d, "habituales")
    L += ["## 10. Contactos", ""] + _tabla(d, "contactos")

    L += ["## 11. El equipo que lo mantiene", "", "### Perfiles y dedicación", ""]
    if perfiles:
        L += ["| Perfil | Dedicación | Skills | Cobertura |", "|---|---|---|---|"]
        for p in perfiles:
            ded = _c(p.get("dedicacion"))
            if _fte(ded) is None:
                ded = (ded + " " if ded else "") + "[PENDIENTE: dedicación en %]"
            L.append(f"| {_c(p.get('perfil')) or '*sin dato*'} | {ded} | "
                     f"{_c(p.get('skills')) or '*sin dato*'} | "
                     f"{_c(p.get('cobertura')) or '*sin dato*'} |")
        L.append("")
        if not sin_dedicacion:
            total = sum(_fte(p.get("dedicacion")) for p in perfiles)
            L += [f"**En total:** {_num_es(total)} personas a jornada completa, repartidas "
                  f"en {len(perfiles)} perfiles.", ""]
        else:
            L += ["No se puede sumar la dedicación: hay perfiles sin porcentaje.", ""]
    else:
        L += _hueco("falta la tabla del equipo de mantenimiento: cuántas personas, con qué "
                    "dedicación y con qué skills.")
    L += ["### En qué se diferencia del equipo que lo construyó", ""]
    if equipo.get("diferencias"):
        L += [f"- {x}" for x in equipo["diferencias"]] + [""]
    else:
        L += _hueco("falta decir en qué se diferencia del equipo de construcción. No es el "
                    "mismo cálculo: el equipo que construye no es el que mantiene.")
    plan = d["planificacion"]
    if plan["existe"]:
        linea = "El equipo que lo construyó está en `docs/planificacion-proyecto.md`, sección 2"
        if plan["perfiles"]:
            linea += (": " + ", ".join(p["perfil"] + (f" ({_c(p['dedicacion'])})"
                                                      if p["dedicacion"] else "")
                                       for p in plan["perfiles"]))
        L += [linea + ".", ""]
    L += ["### Cobertura", ""]
    for q, etiqueta in (("horario", "Horario"), ("guardias", "Guardias"),
                        ("ausencias", "Cuando el único que sabe de algo no está")):
        valor = (cu["respuestas"].get(q) or {}).get("valor")
        L += [f"**{etiqueta}.** " + (valor if valor else "*Sin contestar en el cuestionario.*"),
              ""]
    L += ["### Conocimiento de una sola persona", ""]
    cono = d["conocimiento"]
    if not cono.get("disponible"):
        L += _hueco("sin la auditoría de OpenSpec no se sabe quién construyó cada parte.")
    elif not d["archivo"]:
        L += ["Todavía no se ha cerrado ningún change: no hay nada construido que atribuir.", ""]
    elif cono["una_sola_global"]:
        L += [f"Todo lo construido con OpenSpec lo ha hecho **una sola persona**: "
              f"{cono['personas'][0]}. El traspaso es de una persona, no de un equipo, y "
              "conviene que acompañe al equipo entrante las primeras semanas.", ""]
    elif cono["por_capacidad"]:
        L += ["Quién ha implementado o cerrado los changes de cada capacidad, según la "
              "auditoría. Una capacidad que solo conoce una persona es un riesgo de traspaso.",
              "", "| Capacidad | Changes | Quién la conoce |", "|---|---|---|"]
        for c in cono["por_capacidad"]:
            quien = ", ".join(c["personas"]) or "*sin autor en la auditoría*"
            L.append(f"| {c['capacidad']} | {c['changes']} | {quien}"
                     + (" — **solo esta persona**" if c["una_sola"] else "") + " |")
        L.append("")
    else:
        L += ["| Change | Quién lo conoce |", "|---|---|"]
        L += [f"| {c['change']} | {', '.join(c['personas']) or '*sin autor en la auditoría*'} |"
              for c in cono["por_change"]] + [""]
    if cono.get("disponible") and cono.get("sin_autor") and not cono["una_sola_global"]:
        L += [f"> Sin autor en la auditoría: {', '.join(cono['sin_autor'])}.", ""]

    L += ["## 12. Qué hace el sistema hoy", ""]
    if d["specs"]:
        L += ["Una fila por capacidad de `openspec/specs/`, que es lo que el sistema hace hoy "
              "con sus requisitos y escenarios.", "",
              "| Capacidad | Qué hace | Requisitos |", "|---|---|---|"]
        L += [f"| {s['capacidad']} | {_corta(s['proposito'], 220) or '*sin propósito escrito*'}"
              f" | {s['requisitos']} |" for s in d["specs"]] + [""]
    else:
        L += _hueco("no hay specs en `openspec/specs/`. Son el activo más valioso de un "
                    "traspaso: se consolidan al cerrar cada change, y en un proyecto que no "
                    "empezó con OpenSpec las genera `aisdd init`.")

    L += ["## 13. Cómo está construido", "",
          nar.get("como_esta_construido")
          or "[PENDIENTE: falta el párrafo sobre cómo está construido]", ""]
    repos = d["arquitectura"]["repositorios"]
    if repos:
        L += ["| Repositorio | Contiene |", "|---|---|"]
        L += [f"| `{r['id']}` | {_c(r['contiene'])} |" for r in repos] + [""]
    L += ["### Contexto y contenedores", ""]
    L += _mermaid(diagramas["contexto"]) if diagramas["contexto"] else _hueco(
        "falta el diagrama de contexto y contenedores.")
    L += ["### Flujos críticos", ""]
    if flujos:
        for titulo, t in flujos:
            L += [f"#### {titulo}", ""] + _mermaid(t)
    else:
        L += _hueco("faltan los diagramas de secuencia de los flujos críticos.")
    L += ["### Modelo de datos", ""]
    L += _mermaid(diagramas["datos"]) if diagramas["datos"] else _hueco(
        "falta el diagrama del modelo de datos.")
    if d["arquitectura"]["existe"]:
        L += ["> El detalle —capas, módulos, integraciones y decisiones de diseño— está en "
              "`docs/arquitectura-base.md`.", ""]

    L += ["## 14. Para seguir evolucionándolo", "", "### Decisiones tomadas por el camino", ""]
    decs = [(ch["change"], x) for ch in d["archivo"] for x in ch["decisiones"]]
    if decs:
        L += ["| Change | Tipo | Decisión | Por qué |", "|---|---|---|---|"]
        L += [f"| {ch} | {_c(x['tipo']) or '—'} | {_corta(x['decision'] or x['slug'])} | "
              f"{_corta(x['porque']) or '*sin justificar*'} |" for ch, x in decs[:40]]
        L.append("")
        if len(decs) > 40:
            L += [f"Y {len(decs) - 40} más en los `decisions.md` de "
                  "`openspec/changes/archive/`.", ""]
    else:
        L += ["Ningún change cerrado tiene `decisions.md`." if d["archivo"]
              else "Todavía no hay changes cerrados.", ""]
    if d["arquitectura"]["existe"]:
        L += ["Las decisiones de arquitectura, con su porqué, están en "
              "`docs/arquitectura-base.md`, secciones 2 y 14.", ""]
    L += ["### Qué se construyó, y en qué orden", ""]
    if d["archivo"]:
        L += ["| Cerrado | Change | Capacidades que toca |", "|---|---|---|"]
        L += [f"| {ch['fecha'] or '—'} | {ch['change']} | "
              f"{', '.join(ch['capacidades']) or '—'} |" for ch in d["archivo"][:40]] + [""]
        if len(d["archivo"]) > 40:
            L += [f"Y {len(d['archivo']) - 40} más en `openspec/changes/archive/`.", ""]
    else:
        L += ["Todavía no hay changes cerrados.", ""]
    L += ["### Qué queda por construir", ""]
    p = d["pendiente"]
    if p is None:
        L += ["Sin el estado de OpenSpec no se sabe qué queda por construir."
              + (" El faseado previsto está en `docs/roadmap.md`."
                 if any(f["clave"] == "roadmap" and f["existe"] for f in d["fuentes"]) else ""),
              ""]
    else:
        L.append(f"- **Changes:** {_n(p['cerrados'], 'cerrado')}, {p['activos']} en curso y "
                 f"{_n(p['pendientes'], 'pendiente')}, de {p['total']}.")
        if p["en_curso"]:
            L.append("- **En curso:** " + ", ".join(p["en_curso"]) + ".")
        if p["listas"]:
            L.append("- **Listos para empezar:** " + ", ".join(
                f"{x.get('fase')} {x.get('nombre') or ''}".strip() for x in p["listas"]) + ".")
        if p["bloqueadas"]:
            L.append("- **Esperando a otros:** " + "; ".join(
                f"{x.get('fase')} espera a {', '.join(x.get('espera_a') or [])}"
                for x in p["bloqueadas"]) + ".")
        if p["hus_pendientes"]:
            L.append("- **Historias sin construir:** " + ", ".join(p["hus_pendientes"]) + ".")
        L += ["", "El faseado completo está en `docs/roadmap.md`.", ""]

    L += ["## 15. Con qué se ha generado este traspaso", "",
          "| Fuente | | Aporta | Si falta, lo genera |", "|---|---|---|---|"]
    L += [f"| `{f['ruta']}` | {'sí' if f['existe'] else '**falta**'} | {f['aporta']} | "
          f"{f['genera']} |" for f in d["fuentes"]] + [""]
    L += [f"**Cuestionario:** {cu['contestadas']} de {cu['total']} preguntas contestadas.", ""]
    todos_avisos = list(d.get("avisos") or []) + avisos
    if todos_avisos:
        L += ["**Avisos**", ""] + [f"- {a[:1].upper() + a[1:]}." if not a.endswith(".")
                                   else f"- {a[:1].upper() + a[1:]}" for a in todos_avisos]
        L.append("")
    if d["acompanan"]:
        L += ["### Documentos que acompañan a este traspaso", "",
              "| Documento | Qué cuenta |", "|---|---|"]
        L += [f"| `{x['ruta']}` | {x['que']} |" for x in d["acompanan"]] + [""]
    return "\n".join(L).rstrip() + "\n", avisos


def _textos(x, ruta: str):
    """Cada texto de una estructura JSON, con la ruta que lleva hasta el."""
    if isinstance(x, str):
        yield ruta, x
    elif isinstance(x, dict):
        for k, v in x.items():
            yield from _textos(v, f"{ruta}.{k}")
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from _textos(v, f"{ruta}[{i}]")


def _negarse(lineas: list[str]) -> None:
    print("Se detiene: hay algo con pinta de secreto, y un documento de traspaso no lo "
          "puede llevar.", file=sys.stderr)
    for l in lineas:
        print(f"  {l}", file=sys.stderr)
    print(secretos.CONSEJO, file=sys.stderr)


def main() -> int:
    ap = argparse.ArgumentParser(description="Cuestionario, hechos y documento del traspaso.")
    ap.add_argument("--root", default=".", help="raiz del proyecto")
    ap.add_argument("--preparar", action="store_true",
                    help="crea el cuestionario, o le anade las preguntas que le falten")
    ap.add_argument("--cuestionario", default=CUESTIONARIO,
                    help="ruta del cuestionario, relativa a --root")
    ap.add_argument("--estado", default=None,
                    help="JSON de compute_status.py (aiba-status-report), si hay OpenSpec")
    ap.add_argument("--out", default=None, help="donde escribir el JSON de hechos")
    ap.add_argument("--hoy", default=None, help="fecha de referencia AAAA-MM-DD (pruebas)")
    ap.add_argument("--render", default=None, metavar="JSON",
                    help="escribe el documento a partir de un JSON de hechos completado")
    ap.add_argument("--output", default=None, help="ruta del documento (con --render)")
    args = ap.parse_args()
    root = Path(args.root)
    ruta_c = Path(args.cuestionario)
    ruta_c = ruta_c if ruta_c.is_absolute() else root / ruta_c

    if args.render:
        if not args.output:
            ap.error("--render necesita --output")
        d = json.loads(Path(args.render).read_text(encoding="utf-8"))
        # Lo que ha anadido el skill se revisa por su ruta en el JSON, que es
        # donde hay que corregirlo; el documento entero, por si viene de otro
        # sitio --un documento de origen que ya lo traia--.
        lineas = [l for k in ("narrativa", "diagramas", "equipo")
                  for ruta, t in _textos(d.get(k), k)
                  for l in secretos.informe(secretos.buscar(t), f"JSON {ruta}")]
        md, avisos = render(d)
        if not lineas:
            lineas = secretos.informe(secretos.buscar(md), f"{args.output} (sin escribir)")
        if lineas:
            _negarse(lineas)
            return 2
        salida = Path(args.output)
        salida.parent.mkdir(parents=True, exist_ok=True)
        salida.write_text(md, encoding="utf-8")
        for a in avisos:
            print(f"Aviso: {a}", file=sys.stderr)
        print(salida)
        return 0

    if args.preparar:
        codigo, lineas = preparar(root, ruta_c)
        if codigo:
            _negarse(lineas)
            return codigo
        for l in lineas[:-1]:
            print(f"Aviso: {l}", file=sys.stderr)
        print(lineas[-1])
        return 0

    if not args.out:
        ap.error("hace falta --preparar, --out (calcular) o --render/--output (escribir)")
    if ruta_c.is_file():
        hall = secretos.buscar(ruta_c.read_text(encoding="utf-8", errors="replace"))
        if hall:
            _negarse(secretos.informe(hall, str(ruta_c)))
            return 2
    hoy = date.fromisoformat(args.hoy) if args.hoy else date.today()
    d = calcular(root, hoy, args.estado, ruta_c)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    for a in d["avisos"]:
        print(f"Aviso: {a}", file=sys.stderr)
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
