# AIDD + SDD + AIAD — Marketplace de skills para Claude Code

Marketplace de plugins para instalar los conjuntos **AIDD** (AI Driven Development — planificación y arquitectura asistida por IA), **SDD** (Native AI Specs sobre OpenSpec) y **AIAD** (AI-Augmented Development — ejecución human-first *ia-in-the-loop*) desde cualquier instancia de Claude Code.

- Repositorio: `grananda/aidd-marketplace` — **privado**.
- Nombre del marketplace: `aidd-sdd`.

## Plugins del marketplace

| Plugin | Contenido | Para qué sirve |
|--------|-----------|----------------|
| `aidd` | 12 skills `aidd-*` (Fases 0–2 + entrega 3.5) + metodología | Capturar requisitos, definir historias, diseñar arquitectura, planificar recursos y sprints (con volcado opcional a Jira), y planificar la revisión de las HU en un Excel (`aidd hu-review-plan`). |
| `aisdd` | `aisdd-specs` + metodología | Ejecutar con OpenSpec: roadmap (consciente del sprint-plan) y ciclo open/implement/close change, pre-flight de dudas, auditoría e integración Jira. Comandos `aisdd …` (alias legacy `native-ai …`). *Fork mantenido del antiguo `sdd`.* |
| `boosters` | `booster-ux`, `booster-uml`, `booster-docs` | Generar prototipos UX, diagramas UML y vistas HTML de los documentos de planificación. **Lo usan `aidd` y `aisdd`.** |
| `aiad` | 11 skills `aiad-*` + hook de bitácora + subagente de review + metodología | **Ejecución human-first (*ia-in-the-loop*)**: tú escribes el código y la IA te aumenta a demanda. **Independiente y opcional**; alternativa a `aisdd` para la fase de ejecución. |

## Índice de comandos por skill y fase

Todos los comandos, ordenados por fase del método. Cada comando activa su skill; también se puede invocar namespaced (`/aidd:<skill>`, `/aisdd:aisdd-specs`, `/boosters:<skill>`, `/aiad:<skill>`) o por lenguaje natural.

### `aidd` — Definición, Diseño y Entrega (plugin `aidd`, 12 comandos)

| Fase | Comando | Skill | Genera |
|------|---------|-------|--------|
| 0 | `aidd client-requirements` | `aidd-client-requirements` | `docs/cliente-requisitos.md` (brief del cliente) |
| 1.1 | `aidd requirements` | `aidd-requirements` | `docs/requisitos.md` (RF/NFR, restricciones) |
| 1.2 | `aidd user-stories` `[fases=N\|fases>=N]` | `aidd-user-stories` | `docs/mapa-historias-usuario.md` (mapa por fases; F0 = habilitadores) |
| 1.3 | `aidd user-story-details` | `aidd-user-story-details` | `docs/detalle-historias-usuario.md` (criterios de aceptación) |
| 1.4 (opc.) | `aidd hu-review-plan` | `aidd-hu-review-plan` | `docs/plan-revision-hu.md` + `docs/xlsx/plan-revision-hu.xlsx` (Detalle, Dashboard, Leyenda, Gantt). Antesala de sprints + Jira |
| 2.1 | `aidd prototype-architecture` | `aidd-prototype-architecture` | `docs/arquitectura-base-prototipo.md` |
| 2.2 | `aidd prototype` | `aidd-prototype` | Prototipo mockeado (redirige a `booster-ux`) |
| 2.3 | `aidd style-guide` | `aidd-style-guide` | `docs/guia-estilos.md` (design tokens) |
| 2.3 | `aidd architecture-proposal` | `aidd-architecture-proposal` | `docs/propuesta-arquitectura-base.md` |
| 2.4 | `aidd architecture` | `aidd-architecture` | `docs/arquitectura-base.md` (arquitectura definitiva) |
| 3.5.1 | `aidd project-plan` | `aidd-project-plan` | `docs/planificacion-proyecto.md` (recursos + estimación humano vs IA con KPIs de aceleración) |
| 3.5.2 | `aidd sprint-planning` | `aidd-sprint-planning` | `docs/sprint-plan.md` (+ volcado opcional a Jira) |

### `aisdd` — Inicialización, Roadmap y Ejecución (plugin `aisdd`, skill `aisdd-specs`)

> Comandos primarios `aisdd …`; los `native-ai …` siguen funcionando como **alias legacy**. Antes se llamaba plugin `sdd`.

| Fase | Comando | Rol | Genera / hace |
|------|---------|-----|---------------|
| 3.1 | `aisdd init` | AI Lead | Inicializa OpenSpec + `AGENTS.md` + `openspec/config.yaml` (registra diseño **y capa de entrega**) |
| 3.3 | `aisdd roadmap` | AI Lead | `docs/roadmap.md` + `docs/prompts-roadmap-native-ai.md` + sección `roadmap` en `config.yaml` (fasea por contexto, **alineado al `sprint-plan.md`** si existe) |
| 4 | `aisdd open change <slug>` | AI Lead | Pre-flight + genera specs validados (`proposal.md`, `design.md`, `spec.md`, `decisions.md`). El 1.º siempre es `foundation` (scaffolding) |
| 4 | `aisdd implement change <slug>` | AI Developer | Pre-flight + implementa el código del change |
| 4 | `aisdd close change <slug>` | Outcome Validator | Valida y archiva el change |
| 2 / 4 (aux) | `aisdd prototype-ux [<slug>]` | Architect / Developer | Prototipos UX del change (invoca `booster-ux`) |
| aux | `aisdd uml <slug>` | Cualquiera | Diagramas UML del change en HTML (invoca `booster-uml`) |

### `boosters` — dependencia compartida (plugin `boosters`, 3 comandos)

Los invocan `aidd` y `aisdd`, pero también se pueden llamar directamente.

| Comando | Skill | Hace |
|---------|-------|------|
| `booster-ux` | `booster-ux` | Prototipos/pantallas UX en dos variantes (imagen + HTML navegable) |
| `booster-uml` | `booster-uml` | Diagramas UML (Mermaid) en HTML para un change de OpenSpec |
| `booster-docs` | `booster-docs` | Vista HTML dinámica de un documento de planificación AIDD/SDD |

### `aiad` — Ejecución human-first, *ia-in-the-loop* (plugin `aiad`, 11 comandos)

Cubren la **fase de ejecución** (alternativa human-first a `aisdd`); no siguen la numeración de fases AIDD, se agrupan por intención.

| Grupo | Comando | Hace |
|-------|---------|------|
| Think | `aiad design [explore\|plan]` | Explorar opciones o plan de ataque de una HU (no escribe código de producción) |
| Think | `aiad explain` | Explicar código, librerías, patrones o errores (mentor) |
| Think | `aiad rubber-duck` | Sesión socrática para pensar en voz alta |
| Build | `aiad tdd` | Tests en rojo para lo que vas a construir (tú implementas) |
| Build | `aiad test [unit\|e2e]` | Rellenar tests sobre código existente |
| Improve | `aiad review [correctness\|quality\|perf]` | Review didáctico + informe HTML con el código referenciado; no aplica fixes |
| Flow | `aiad pair` | Pair-programming sostenido (tú driver, IA navigator) |
| Flow | `aiad bridge [to-sdd\|to-aiad]` | Puente HU ↔ change para saltar AIAD ↔ SDD |
| Flow | `aiad unblock` | Hub "estoy atascado": triaje y enrutado al skill adecuado |
| Flow | `aiad save` | Commit + push de todo, sin preguntas |
| Record | `aiad journal [log\|report]` | Bitácora de autoría (*craft ratio*: qué escribes tú vs delegas) |

## Por qué hay que instalar los tres

No son tres copias del mismo paquete: son **tres piezas de un mismo flujo** que se llaman entre sí. El método AIDD-SDD completo va de la captura de requisitos hasta la ejecución de cada change, y en ese recorrido:

1. **`aidd` cubre la planificación y el diseño** (Fases 0–2 y la capa de entrega 3.5: requisitos → historias → arquitectura → plan de recursos → sprints). Es el "qué" y el "cuándo".
2. **`aisdd` cubre la ejecución** (Fases 3–4: roadmap por presupuesto de contexto —consciente del `sprint-plan`— y el ciclo `open/implement/close change` sobre OpenSpec, con auditoría e integración Jira). Es el "cómo se construye".
3. **`boosters` es la dependencia compartida** de los dos anteriores. No es opcional si usas el flujo completo:
   - `aidd prototype` (Fase 2.2) **redirige a `booster-ux`** para maquetar las pantallas del prototipo.
   - `aisdd prototype-ux` y `aisdd uml` (del plugin `aisdd`) **invocan a `booster-ux` y `booster-uml`** para documentar cada change.
   - Los skills de planificación de `aidd` y `aisdd` **invocan a `booster-docs`** para dejar, junto a cada `.md` generado (requisitos, historias, roadmap, sprint-plan…), una vista HTML complementaria para consumo humano (el Markdown sigue siendo la única fuente de verdad).
   - Si `boosters` no está instalado, esos pasos avisan de que falta el booster y no generan ni prototipos, ni diagramas, ni vistas HTML.

Claude Code **no resuelve dependencias entre plugins automáticamente**: cada plugin se instala por separado. Por eso, para el flujo de extremo a extremo necesitas los tres. (Si solo vas a hacer planificación sin prototipos ni diagramas, `aidd` por sí solo funciona; pero la instalación recomendada y completa son los tres.)

## AIAD — ejecución human-first (opcional e independiente)

`aiad` **no forma parte del trío anterior**: es un plugin independiente con filosofía invertida para la fase de ejecución. Donde `aisdd` es *human-in-the-loop* (la IA es el motor, tú validas), `aiad` es **ia-in-the-loop**: **tú eres el motor** que escribe el código y la IA te **aumenta a demanda** (*pull, not push*). Devuelve al ingeniero la autoría, la maestría y el flow del oficio sin renunciar al apalancamiento de la IA.

11 skills agrupados por intención:

- **Think** (aconsejan, no escriben código): `aiad-design` (opciones/enfoque), `aiad-explain`, `aiad-rubber-duck`.
- **Build** (la IA solo escribe tests): `aiad-tdd` (tests en rojo → tú implementas), `aiad-test` (`unit`/`e2e` sobre código existente).
- **Improve**: `aiad-review` (`correctness`/`quality`/`perf`, enseña el porqué, no aplica fixes).
- **Flow & control**: `aiad-pair` (driver/navigator), `aiad-bridge` (puente HU ↔ change para saltar AIAD ↔ SDD), `aiad-unblock` (hub "estoy atascado"), `aiad-save` (commit + push sin preguntas).
- **Record**: `aiad-journal` (bitácora de autoría / *craft ratio*).

Además incluye un **hook** opcional (`hooks/`) que registra de forma factual qué ficheros toca la IA (autoría real, no auto-declarada; opt-in por proyecto) y un **subagente** `aiad-reviewer` que aísla la revisión para no ensuciar tu contexto de trabajo.

**Uso autónomo:** `aiad` se puede instalar y usar **solo**, sobre cualquier repo, con o sin AIDD/SDD. Lee los artefactos de AIDD (`docs/detalle-historias-usuario.md`, `arquitectura-base.md`…) *si existen*, pero no los exige. La única dependencia externa es de `aisdd`: `aiad-bridge` necesita OpenSpec/aisdd-specs instalado para saltar de motor (si no está, lo avisa y sigues en standalone). Eliges el motor **por HU** y puedes cambiarlo a mitad.

> Autoría: el plugin `aiad` es de creación propia (Julio Fernández), independiente del resto del marketplace.

## Instalación (repositorio privado)

Como el repo es **privado**, Claude Code lo clona usando **tus credenciales de git locales**. Necesitas tener acceso de lectura al repo `grananda/aidd-marketplace` y git autenticado en esa máquina.

### 1. Asegura el acceso a GitHub (una vez por máquina)

Cualquiera de estas opciones sirve:

```bash
# Opción A — GitHub CLI (recomendada)
gh auth login            # elige HTTPS; configura el credential helper de git

# Opción B — comprobar que ya tienes acceso
gh repo view grananda/aidd-marketplace   # si lo ves, tu git puede clonarlo
```

Si usas SSH en vez de HTTPS, vale igual siempre que tu clave tenga acceso al repo (ver más abajo la variante por URL SSH).

### 2. Añade el marketplace y instala los plugins (dentro de Claude Code)

```text
# Añadir el marketplace (una vez por máquina)
/plugin marketplace add grananda/aidd-marketplace
#   variante por URL HTTPS:  /plugin marketplace add https://github.com/grananda/aidd-marketplace.git
#   variante por SSH:        /plugin marketplace add git@github.com:grananda/aidd-marketplace.git

# Instalar los tres plugins del flujo integrado
/plugin install aidd@aidd-sdd
/plugin install aisdd@aidd-sdd
/plugin install boosters@aidd-sdd

# Opcional e independiente: ejecución human-first (ia-in-the-loop)
/plugin install aiad@aidd-sdd

# Comprobar
/plugin list
/plugin            # menú interactivo (Discover / Installed / Marketplaces / Errors)
```

Si `/plugin marketplace add` falla con error de autenticación o "repository not found", casi siempre es acceso/credenciales: vuelve al paso 1 (no eres colaborador del repo, o git no está autenticado en esa máquina).

### 3. Uso

Tras instalar, cada skill queda *namespaced* por su plugin:

- `/aidd:aidd-sprint-planning`, `/aidd:aidd-requirements`, …
- `/aisdd:aisdd-specs` (comandos `aisdd …`; alias legacy `native-ai …`)
- `/boosters:booster-ux`, `/boosters:booster-uml`, `/boosters:booster-docs`
- `/aiad:aiad-tdd`, `/aiad:aiad-review`, `/aiad:aiad-save`, …

También se activan por lenguaje natural y por sus comandos internos (`aidd sprint-planning`, `aisdd open change`, `aiad tdd`, `aiad review`, …).

### Activación automática por proyecto (equipo)

En `.claude/settings.json` de un proyecto puedes registrar el marketplace y preactivar los plugins para todo el equipo (cada miembro necesita acceso al repo privado):

```json
{
  "extraKnownMarketplaces": {
    "aidd-sdd": { "source": { "source": "github", "repo": "grananda/aidd-marketplace" } }
  },
  "enabledPlugins": {
    "aidd@aidd-sdd": true,
    "aisdd@aidd-sdd": true,
    "boosters@aidd-sdd": true,
    "aiad@aidd-sdd": true
  }
}
```

## Metodología

La metodología AIDD-SDD viaja **dentro** de los plugins `aidd` y `aisdd` (carpeta `methodology/`). Los skills la referencian con `${CLAUDE_PLUGIN_ROOT}/methodology/native-ai-aidd-sdd.md`, así que resuelve tras instalar en cualquier repo. Es referencia de solo lectura; no se carga automáticamente.

El plugin `aiad` lleva su propia metodología (`${CLAUDE_PLUGIN_ROOT}/methodology/native-ai-aiad.md`): el manifiesto *ia-in-the-loop*, el catálogo de skills, el puente HU ↔ change y la bitácora de autoría.

## Mantenimiento

- **Versionado**: cada `plugin.json` fija `version` (semver). **Sube la versión al publicar cambios**; si no, los usuarios ya instalados no recibirán las novedades (Claude Code los cree en la misma versión). Tras subir cambios, los usuarios actualizan con `/plugin marketplace update aidd-sdd`.
- **Hacerlo público** (si algún día procede): `gh repo edit grananda/aidd-marketplace --visibility public`. La instalación entonces no requeriría credenciales.
- **Desarrollo local** antes de publicar: `claude --plugin-dir ./plugins/aidd` (un plugin suelto) o `/plugin marketplace add ./` (marketplace local); validar con `claude plugin validate ./`.

---

NTT DATA Spain GDN-e.
