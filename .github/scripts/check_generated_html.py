#!/usr/bin/env python3
"""Comprueba que los HTML de metodologia estan al dia y que las copias coinciden.

Dos fallos que se cuelan solos y no rompen nada visiblemente:

1. Editar un `.md` de `methodology/` y olvidar regenerar su `.html`. La version
   publicada sigue diciendo lo anterior, y nadie lo nota hasta que alguien la lee.
2. Tocar la copia de `aidd/` y no la de `aisdd/` (o al reves). Son espejo, pero
   nada lo hace cumplir.

Y un tercero que no afecta a la metodologia sino a todo lo que pinta booster-docs:

3. Que un tipo de documento con forma propia --tarjetas, cajas, linea temporal--
   deje de recibirla, o que al darsela se pierda texto. No falla nada: la vista
   sale, solo que plana o incompleta. Cada tipo de `SHAPED_TYPES` se pinta aqui
   con una entrada que tiene su forma y con otra que no; la primera tiene que
   recibirla, la segunda salir como siempre, y en las dos tienen que aparecer
   todas las palabras testigo del markdown.
"""
from __future__ import annotations

import ast
import filecmp
import re
import subprocess
import sys
import tempfile
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RENDER = ROOT / "plugins/boosters/skills/booster-docs/scripts/render_docs_html.py"

# (md relativo a plugins/<plugin>/methodology, titulo forzado)
DOCS = [
    ("native-ai-aidd-sdd", "Native AI · AIDD-SDD — Metodología AI-Native"),
    ("native-ai-aidd-sdd-getting-started", "AIDD-SDD — Getting Started"),
]
ESPEJO = ["aidd", "aisdd"]          # deben ser identicos entre si
SUELTOS = [("aiad", "native-ai-aiad", "Native AI · AIAD — AI-Augmented Development"),
           ("aiba", "native-ai-aiba", "Native AI · AIBA — Análisis de negocio, entrega y medición")]

errors: list[str] = []


# El renderer estampa la fecha de generacion en la cabecera, asi que comparar
# byte a byte falla al dia siguiente aunque no haya cambiado nada. Lo que hay que
# comprobar es el CONTENIDO, no cuando se genero.
SELLO_FECHA = re.compile(r"Vista generada el \d{4}-\d{2}-\d{2}")


def contenido(path: Path) -> str:
    return SELLO_FECHA.sub("Vista generada el <fecha>",
                           path.read_text(encoding="utf-8", errors="replace"))


def iguales(a: Path, b: Path) -> bool:
    return contenido(a) == contenido(b)


def regenera(md: Path, titulo: str) -> Path:
    salida = Path(tempfile.mkdtemp()) / "out.html"
    subprocess.run(
        [sys.executable, str(RENDER), "--input", str(md), "--output", str(salida),
         "--title", titulo, "--no-mermaid-asset"],
        check=True, capture_output=True,
    )
    return salida


for stem, titulo in DOCS:
    fuentes = [ROOT / f"plugins/{p}/methodology/{stem}.md" for p in ESPEJO]
    if not filecmp.cmp(fuentes[0], fuentes[1], shallow=False):
        errors.append(f"{stem}.md difiere entre aidd/ y aisdd/ (son espejo)")
    htmls = [ROOT / f"plugins/{p}/methodology/{stem}.html" for p in ESPEJO]
    if not iguales(htmls[0], htmls[1]):
        errors.append(f"{stem}.html difiere entre aidd/ y aisdd/")
    esperado = regenera(fuentes[0], titulo)
    if not iguales(esperado, htmls[0]):
        errors.append(f"{stem}.html no coincide con lo que produce el renderer: "
                      f"regeneralo (ver README, seccion Mantenimiento)")

for plugin, stem, titulo in SUELTOS:
    md = ROOT / f"plugins/{plugin}/methodology/{stem}.md"
    html = ROOT / f"plugins/{plugin}/methodology/{stem}.html"
    if not md.is_file():
        continue
    if not iguales(regenera(md, titulo), html):
        errors.append(f"{stem}.html no coincide con su .md: regeneralo")


# --- 3. La forma por tipo de documento --------------------------------------

def tipos_con_forma() -> tuple:
    for nodo in ast.parse(RENDER.read_text(encoding="utf-8")).body:
        if isinstance(nodo, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "SHAPED_TYPES" for t in nodo.targets):
            return tuple(ast.literal_eval(nodo.value))
    return ()


def pinta(md: str, tipo: str) -> tuple[str | None, str]:
    d = Path(tempfile.mkdtemp())
    (d / "in.md").write_text(md, encoding="utf-8")
    r = subprocess.run([sys.executable, str(RENDER), "--input", str(d / "in.md"),
                        "--output", str(d / "out.html"), "--doc-type", tipo,
                        "--no-mermaid-asset"], capture_output=True, text=True)
    return ((d / "out.html").read_text(encoding="utf-8") if r.returncode == 0 else None), r.stderr


def texto(pagina: str) -> str:
    """Lo que lee una persona: sin estilos, sin scripts y sin etiquetas."""
    pagina = re.sub(r"<(style|script)\b.*?</\1>", " ", pagina, flags=re.S)
    return unescape(re.sub(r"<[^>]+>", " ", pagina))


# Las palabras testigo van en todos los sitios donde un formador puede perder
# texto: un campo que reconoce, uno que no, un parrafo suelto, una sub-vineta,
# una columna que no es suya, una fila que no es una fase.
FORMAS = {
    "detalle-historias-usuario": {
        "bien": """# Detalle de historias de usuario — Pólizas

## Historias detalladas

Cada historia, lista para el cliente. Introducción zafiro.

### HU-01 — Alta de póliza
- **Fase**: F1   **RF cubierto(s)**: RF-01   **Prioridad**: Alta
- **Estimación**: M (3 d)
- **Descripción**: Como agente quiero dar de alta pólizas esmeralda.
- **Criterios de aceptación**:
  - Dado un agente, cuando guarda, entonces se crea la póliza. [IMPRESCINDIBLE]
  - Dado un error, cuando guarda, entonces avisa ámbar.
- **Notas técnicas y dependencias**: depende de HU-02 turquesa.
- **Riesgo**: integración coral.

Párrafo suelto obsidiana.

### HU-02 — Consulta
- **Fase**: F1   **Prioridad**: Media
- **Estimación**: S (1,5 d)
- **Criterios de aceptación**:
  - Dado un filtro, cuando busca, entonces lista.

### HU-03 — Baja
- **Fase**: F2   **Prioridad**: Baja
- **Estimación**: XS (0,5 d)

### HU-04 — Suplemento
- **Fase**: F2   **Prioridad**: Alta
- **Estimación**: L (5 d)

### HU-05 — Renovación
- **Fase**: F2   **Prioridad**: Media
- **Estimación**: M (3 d)

### HU-06 — Informe
- **Fase**: F2   **Prioridad**: Baja
- **Estimación**: S (1,5 d)

## Cobertura

| HU | Estado |
|---|---|
| HU-01 | detallada granate |
""",
        "espera": [
            ('class="hu-card', 6, "no pinta una tarjeta por historia"),
            ('class="hu-index"', 1, "no pone el indice con seis historias o mas"),
            ('<details class="hu-criteria">', 2, "no pliega los criterios de aceptacion"),
            ("2 · 1 imprescindible", 1, "no cuenta los criterios ni los imprescindibles"),
            ("Fase F2 <small>4 historias · 10 d</small>", 1,
             "no agrupa por fase con su recuento y su esfuerzo"),
            ("chip-prio-high", 1, "no pinta la prioridad como chip"),
            ("<table>", 1, "pierde la tabla de cobertura, que no es una historia"),
        ],
        "testigos": ["zafiro", "esmeralda", "ámbar", "turquesa", "coral", "obsidiana", "granate"],
        "mal": """# Detalle de historias

## Historias detalladas

**HU-01 — Alta de póliza** zafiro
- **Fase**: F1   **Prioridad**: Alta
- **Criterios de aceptación**:
  - Dado un agente, entonces ámbar.
""",
        "forma": 'class="hu-card',
        "testigos_mal": ["zafiro", "ámbar"],
    },
    "sprint-plan": {
        "bien": """# Plan de sprints — Pólizas

## 4. Distribución en sprints

### Sprint 1 — Alta (25/08/2026 a 05/09/2026)
- **Objetivo**: dar de alta pólizas zafiro.
- **Unidades incluidas**: HU-01, HU-02
- **Carga real agregada**: 8,5 d frente a 10 d de capacidad
- **Definition of Done**: tests en verde ámbar.
- Nota suelta turquesa.

### Sprint 2 — Suplementos (08/09/2026 a 19/09/2026)
- **Objetivo**: suplementos esmeralda.
- **Carga**: 12 d / 10 d

| Lane | Carga |
|---|---|
| api | coral |

### Sprint 3 (22/09/2026 a 03/10/2026)

Objetivo: cierre. Unidades: HU-05. Capacidad: 10 d. Carga: 4 d.

## 5. Hitos

- MVP obsidiana
""",
        "espera": [
            ('class="sprint-box"', 3, "no pinta una caja por sprint"),
            ("<strong>85 %</strong>", 1, "no calcula la carga frente a la capacidad"),
            ("<strong>120 %</strong> de la capacidad · sobrecargado", 1,
             "no avisa del sprint sobrecargado"),
            ("con holgura", 1, "no senala el sprint con holgura"),
            ("3 sprints · 25/08/2026 → 03/10/2026 · 1 sobrecargado", 1,
             "no resume los sprints"),
            ('<details class="sprint-more">', 2, "no guarda lo que no sabe clasificar"),
        ],
        "testigos": ["zafiro", "ámbar", "turquesa", "esmeralda", "coral", "obsidiana"],
        "mal": """# Plan de sprints

## 4. Distribución en sprints

**Sprint 1** (25/08/2026 a 05/09/2026): objetivo zafiro, carga 8 d de 10 d ámbar.
""",
        "forma": 'class="sprint-box"',
        "testigos_mal": ["zafiro", "ámbar"],
    },
    "roadmap": {
        "bien": """# Roadmap — Pólizas

## Fases

| Fase | Nombre | Depende de | Riesgo de contexto | Estado | Notas |
|---|---|---|---|---|---|
| F0 | Fundación zafiro | — | bajo | cerrada | base |
| F1 | Alta | F0 | medio | en curso | ámbar |
| F2 | Baja | F1 | alto | pendiente | |
| Total | | | | | tres fases turquesa |

## Lanes

| Fase | Nombre | Lane | Depende de |
|---|---|---|---|
| F0 | Contrato | | — |
| F-api-01 | API de alta | api | F0 |
| F-portal-01 | Portal de alta | portal | F0 |
| FB-01 | Barrera coral | | F-api-01, F-portal-01 |
| F-api-02 | API de baja | api | FB-01 |

## Dependencias cross-lane

| Origen | Destino | Cómo se resuelve |
|---|---|---|
| F-api-01 | F-portal-01 | FB-01 |
| F-portal-01 | F-api-02 | FB-01 |

## Oleadas

| Oleada | Fases | Ancho |
|---|---|---|
| Oleada 1 | F1, F2 | 2/2 |
| Oleada 2 | F3 | 1/2 |

## Detalle por fase

### F1 — Alta obsidiana
- **Objetivo**: dar de alta.
- **Oleada**: Oleada 1
- **Alcance**: formularios granate.

### F2 — Consulta
- **Oleada**: Oleada 1

### F3 — Baja
- **Oleada**: Oleada 2
- **Depende de**: F1, F2
""",
        "espera": [
            ('class="rm-line"', 1,
             "no pinta como linea temporal una tabla de fases sin paralelismo"),
            ('class="rm-lanes" style="--lanes:2"', 1, "no pinta una calle por lane"),
            ('class="rm-barrier"', 2, "no pinta las barreras cruzando los lanes"),
            ('class="rm-waves"', 1, "no agrupa por oleadas las fases escritas por titulo"),
            ("2 fases en paralelo", 1, "no dice que fases de una oleada van en paralelo"),
            ("✓ cerrada", 1, "no pinta el estado de la fase con icono y texto"),
            ("riesgo alto", 1, "no pinta el riesgo de contexto"),
            ("<th>Cómo se resuelve</th>", 1,
             "convierte en fases la tabla de dependencias cross-lane"),
            ("<th>Ancho</th>", 1, "convierte en fases la tabla de oleadas"),
            ('<details class="rm-more">', 1, "pierde el detalle de la fase escrita por titulo"),
        ],
        "testigos": ["zafiro", "ámbar", "turquesa", "coral", "obsidiana", "granate"],
        "mal": """# Roadmap

## Fases

- F1: Alta zafiro
- F2: Baja ámbar
""",
        "forma": 'class="rm-board"',
        "testigos_mal": ["zafiro", "ámbar"],
    },
}

con_forma = tipos_con_forma()
if not con_forma:
    errors.append("no se encuentra SHAPED_TYPES en render_docs_html.py")
for tipo in sorted(set(con_forma) - set(FORMAS)):
    errors.append(f"{tipo} tiene forma propia y ningun caso en esta comprobacion: "
                  "anade su entrada con forma y sin ella")
for tipo, caso in FORMAS.items():
    pagina, err = pinta(caso["bien"], tipo)
    if pagina is None:
        errors.append(f"{tipo}: el renderer falla con una entrada minima: {err.strip()[-300:]}")
        continue
    if "no se pudo dar forma" in err:
        errors.append(f"{tipo}: el formador revienta y cae al texto plano: {err.strip()[-300:]}")
    for fragmento, veces, motivo in caso["espera"]:
        if pagina.count(fragmento) < veces:
            errors.append(f"{tipo}: {motivo} (esperaba {veces} vez/veces «{fragmento}» y "
                          f"hay {pagina.count(fragmento)})")
    perdidas = [w for w in caso["testigos"] if w not in texto(pagina)]
    if perdidas:
        errors.append(f"{tipo}: al darle forma se pierde texto del markdown: {perdidas}")
    pagina, err = pinta(caso["mal"], tipo)
    if pagina is None:
        errors.append(f"{tipo}: el renderer falla con una entrada sin la forma esperada: "
                      f"{err.strip()[-300:]}")
        continue
    if caso["forma"] in pagina:
        errors.append(f"{tipo}: da forma a una entrada que no la tiene; tenia que salir "
                      "como siempre")
    perdidas = [w for w in caso["testigos_mal"] if w not in texto(pagina)]
    if perdidas:
        errors.append(f"{tipo}: sin la forma esperada se pierde texto: {perdidas}")

if errors:
    print("Documentacion generada desincronizada:", file=sys.stderr)
    for e in errors:
        print(f"  - {e}", file=sys.stderr)
    sys.exit(1)
print(f"HTML de metodologia al dia, copias sincronizadas y {len(FORMAS)} tipos de "
      "documento con su forma, sin perder texto.")
