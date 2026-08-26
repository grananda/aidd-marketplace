# AIDD + AISDD + AIAD — Marketplace de skills para Claude Code

Marketplace de plugins para instalar los conjuntos **AIDD** (AI Driven Development — planificación y arquitectura asistida por IA), **AISDD** (AI Spec-Driven Development sobre OpenSpec; *fork mantenido del antiguo `sdd`*) y **AIAD** (AI-Augmented Development — ejecución human-first *ia-in-the-loop*) desde cualquier instancia de Claude Code.

- Repositorio: `grananda/aidd-marketplace` — **privado**.
- Nombre del marketplace: `aidd-sdd`.

## Plugins del marketplace

| Plugin | Contenido | Para qué sirve |
|--------|-----------|----------------|
| `aidd` | 12 skills `aidd-*` (Fases 0–2 + entrega 3.5) + metodología | Capturar requisitos, definir historias, diseñar arquitectura, planificar recursos y sprints (con volcado opcional a Jira), y planificar la revisión de las HU en un Excel (`aidd hu-review-plan`). |
| `aisdd` | `aisdd-specs` + `aisdd-amend` + metodología | Ejecutar con OpenSpec: roadmap (consciente del sprint-plan, con **tres modos de paralelismo**) y ciclo open/implement/close change, pre-flight de dudas configurable, auditoría e integración Jira. Comandos `aisdd …` (alias legacy `native-ai …`). *Fork mantenido del antiguo `sdd`.* |
| `boosters` | `booster-ux`, `booster-uml`, `booster-docs` | Generar prototipos UX, diagramas UML y vistas HTML de los documentos de planificación. **Lo usan `aidd` y `aisdd`.** |
| `aiad` | 11 skills `aiad-*` + hook de bitácora + subagente de review + metodología | **Ejecución human-first (*ia-in-the-loop*)**: tú escribes el código y la IA te aumenta a demanda. **Independiente y opcional**; alternativa a `aisdd` para la fase de ejecución. |

## Índice de comandos por skill y fase

Todos los comandos, ordenados por fase del método. Cada comando activa su skill; también se puede invocar namespaced (`/aidd:<skill>`, `/aisdd:aisdd-specs`, `/boosters:<skill>`, `/aiad:<skill>`) o por lenguaje natural.

### `aidd` — Definición, Diseño y Entrega (plugin `aidd`, 13 comandos)

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
| transversal | `aidd metrics` | `aidd-metrics` | `docs/kpis-ia.md` (KPIs **medidos** de uso de IA: tiempo atendido, ciclo por HU, churn y correcciones por change; ahorro solo con esfuerzo real declarado) |

> `aidd metrics` no es un paso del método: es una capa de observación, **independiente del resto y ejecutable en cualquier momento**. No produce nada que consuma otro comando y no bloquea ninguna fase. Por eso vive aquí y no en la metodología. Ver [Registro de actividad](#registro-de-actividad-opt-in).

### `aisdd` — Inicialización, Roadmap y Ejecución (plugin `aisdd`, skills `aisdd-specs` y `aisdd-amend`)

> Comandos primarios `aisdd …`; los `native-ai …` siguen funcionando como **alias legacy**. Antes se llamaba plugin `sdd`.

| Fase | Comando | Rol | Genera / hace |
|------|---------|-----|---------------|
| 3.1 | `aisdd init` | AI Lead | Inicializa OpenSpec + `AGENTS.md` + `openspec/config.yaml` (registra diseño **y capa de entrega**) |
| 3.3 | `aisdd roadmap` | AI Lead | `docs/roadmap.md` + `docs/prompts-roadmap-native-ai.md` + sección `roadmap` en `config.yaml` + bloque en `AGENTS.md` (fasea por contexto, **alineado al `sprint-plan.md`** si existe, y elige **modo de paralelismo**: `atomic`, `waves` o `multilane`) |
| 4 | `aisdd open change <slug>` | AI Lead | Pre-flight + genera specs validados (`proposal.md`, `design.md`, `spec.md`, `decisions.md`). El 1.º siempre es `foundation` (scaffolding). En `multilane`, **un change abierto por lane** |
| 4 | `aisdd implement change <slug>` | AI Developer | Pre-flight + implementa el código del change |
| 4 | `aisdd amend change [descripción]` | Developer / Lead | Incorpora una modificación a un change **ya abierto** y ejecuta **solo ese delta**, sin re-aplicar el change (skill `aisdd-amend`) |
| 4 | `aisdd close change <slug>` | Outcome Validator | Valida y archiva el change |
| 4 | `aisdd lane [list \| switch \| status]` | AI Developer / AI Lead | Selecciona la **línea de trabajo activa** (solo roadmaps `multilane`), como `git switch` con las ramas |
| 2 / 4 (aux) | `aisdd prototype-ux [<slug>]` | Architect / Developer | Prototipos UX del change (invoca `booster-ux`) |
| aux | `aisdd uml <slug>` | Cualquiera | Diagramas UML del change en HTML (invoca `booster-uml`) |

#### Cómo paralelizar el trabajo (tres modos)

Por defecto el ciclo es **mono-hilo**: un change abierto a la vez. Con varios developers eso deja a casi todos esperando, así que `aisdd roadmap` pregunta cuántos trabajan en paralelo y ofrece dos formas de repartir. **No compiten: son ejes perpendiculares.**

```
                Oleada 1    Oleada 2         Oleada 3    Oleada 4
                ───────────────────────────────────────────────────
lane api        │          │ F-api-01      │           │          │
lane portal     │   F0     │ F-portal-01   │  FB-01    │  FB-02   │
lane import     │          │ F-import-01   │           │          │
                ───────────────────────────────────────────────────
                   1/3          3/3            1/3        1/3
```

**Columnas = oleadas** (cuándo se puede trabajar a la vez). **Filas = lanes** (de quién es cada parte del código).

`F0` y las `FB-NN` **ocupan la columna entera**: tocan lo que comparten todos los lanes (el contrato, una migración, el rollout) y por eso los detienen a todos. Dicho de otro modo, **una barrera no es más que una oleada de ancho 1 con propiedad declarada**.

| Modo | Qué paraleliza | Garantía | Cuándo |
|------|----------------|----------|--------|
| `atomic` | Nada | Total, por construcción | Un dev, o sin base para separar. **Default** |
| `waves` (oleadas) | Hasta `N` fases a la vez, respetando dependencias | **Ninguna** — ordena, no protege | Varios devs sin superficies declarables |
| `multilane` (lanes) | `N` líneas persistentes, un change **por lane** | Declarada y **verificada** al cerrar | Módulos con rutas de código disjuntas |

Los dos llegan al **mismo calendario**; lo que cambia es si hay red debajo. En `multilane`, `aisdd close change` comprueba que el change no escribió fuera de las rutas de su lane, y una corrección que toca el contrato compartido para a los lanes hermanos en vez de resolverse en silencio.

**Regla rápida:**

- Roadmap ya diseñado y validado que no quieres alterar → **`waves` anotado** (se añade sin re-fasear: conserva nombres de fase, así que no rompe el enlace con el sprint-plan ni con Jira).
- Proyecto con módulos de rutas separadas y varios devs → **`multilane`**.
- Un solo dev, o sin base para separar superficies → **`atomic`**.

Detalle completo, con un ejemplo del mismo proyecto faseado en los tres modos y sus calendarios reales, en **§3.bis** de `plugins/aisdd/methodology/native-ai-aidd-sdd.md` (y su `.html` hermano).

#### Cuánto pregunta el pre-flight

`open change` e `implement change` no actúan a ciegas: antes resuelven las ambigüedades reales con el humano y las persisten en `decisions.md`.

- Las **bloqueantes se preguntan siempre, sin límite**. Son, por definición, aquellas sin las que no se puede producir un spec sólido: caparlas cambia corrección de la especificación por comodidad.
- Cuántas **preferencias** y **confirmaciones** se plantean lo decide cada proyecto:

  ```yaml
  # openspec/config.yaml
  preflight:
    preferencias: all      # all | entero >= 0
    confirmaciones: all
  ```

  Lo que queda fuera del límite no se pierde: se resuelve con el default recomendado y queda registrado con `Origen: auto-default`.

`aisdd init` siembra la sección con los valores por defecto y no la sobrescribe si ya existe.

#### Cuando aparece un cambio a mitad de un change

No todo cambio cuesta lo mismo. La pregunta que decide el coste **no** es "¿cambia el código?", sino: **¿algún documento AIDD sellado queda diciendo algo falso?**

| Nivel | Situación | Qué tocas |
|-------|-----------|-----------|
| 1. Implementación | El spec es correcto y el código no lo cumple | Solo el código |
| 2. Decisión no documentada | Ningún documento fijaba ese detalle | Una entrada `Tipo: correccion` en `decisions.md`, y sigues |
| 3. Contradicción documental | Un documento sellado afirma lo contrario | **Ese** documento, y solo ese, re-sellado por su skill |
| 4. Contrato compartido *(solo `multilane`)* | La corrección toca aquello sobre lo que trabajan otros lanes | Nada por tu cuenta: **parada coordinada** y revisión por el dueño del contrato |

El caso 2 es el habitual (una incompatibilidad de versiones que aparece al validar, un matiz visual que la guía no recogía) y **no** se escala al Architect ni se re-aplica el change. Si además hay que tocar los specs (criterios o tareas nuevas), la vía es **`aisdd amend change`**: escribe el delta y lo implementa sin re-ejecutar el change entero sobre un árbol ya trabajado. Toma una baseline de build y tests **antes** de tocar nada, para separar con evidencia lo que rompe la enmienda de lo que ya estaba roto — así no necesita conocer los cambios manuales que hayas hecho por tu cuenta.

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

## Registro de actividad (opt-in)

Los cuatro plugins traen un hook `PostToolUse` (`hooks/aidd-activity-hook.sh`) que deja una traza de qué se ha hecho sobre el código: **fecha y hora, usuario, skill ejecutado y fichero trabajado**, una línea por acción.

**Se activa por proyecto creando el fichero de registro** (sin él no se escribe nada, en ningún proyecto):

```bash
touch docs/aidd-activity.md   # activar
rm docs/aidd-activity.md      # desactivar
```

A partir de ahí, `docs/aidd-activity.md` se va llenando solo:

```
- 2026-08-05T09:12:44Z | user:jfernandez | skill:aidd:aidd-user-story-details | ctx:HU-07 | run | note:HU-07 fases=4
- 2026-08-05T09:14:02Z | user:jfernandez | skill:aidd:aidd-user-story-details | ctx:HU-07 | file:docs/detalle-historias-usuario.md | note:-
- 2026-08-05T09:18:20Z | user:jfernandez | skill:- | ctx:HU-07 | turn | note:dur=336s skills=1 files=3
```

- Una línea `run` por cada skill invocado (con sus argumentos en `note:`), y una línea `file:` por cada fichero que escribe la IA, **atribuido al skill que estaba activo** en ese momento.
- Una línea `turn` al cerrar cada turno, con su **duración**. Son las que permiten medir tiempo *atendido* (pediste algo y esperaste) en vez de tiempo de calendario, que contaría noches y reuniones. Un turno que no toca nada no deja rastro.
- El campo `ctx:` es la **historia de usuario o el change** en curso: se detecta de los argumentos (`HU-07`) o de trabajar dentro de `openspec/changes/<id>/`. Es lo que permite dar tiempo de ciclo por HU.
- Marcas de tiempo en **UTC** (`Z`), como el journal de AIAD, para que ordenen bien entre máquinas y zonas horarias.
- **Pasivo**: solo registra. Nunca bloquea una acción, nunca edita código y nunca hace fallar la sesión.
- **Sin duplicados**: el hook viaja en los cuatro plugins, así que con varios instalados se dispara varias veces por la misma acción; deduplica por `tool_use_id` y solo escribe la primera.
- Lo que escribes tú a mano en tu editor **no pasa por las tools de la IA y por tanto no se registra**. El log es traza de la IA, no vigilancia del humano.
- No registra el contenido de tus prompts ni del código: solo el skill, el fichero y los argumentos del comando.

Es independiente de `docs/aiad-journal.md` (plugin `aiad`), que responde a otra pregunta: **cuánto** escribiste tú frente a lo que delegaste. Puedes tener los dos, uno o ninguno.

> **Nota**: el resumen de `note:` es determinista (los argumentos del comando). Un hook es un script de shell, sin modelo detrás, así que no puede redactar en prosa qué le pediste; para eso tendría que escribirlo el propio skill.

### KPIs a partir del registro

Con el registro activo, `aidd metrics` convierte esa traza en un informe (`docs/kpis-ia.md` + HTML): tiempo atendido, reparto planificación vs ejecución, tiempo de ciclo por HU o change, retrabajo y código entregado.

Se ejecuta **cuando quieras y las veces que quieras**: solo lee (registro, `git log`, las tallas de `docs/detalle-historias-usuario.md` para el baseline y, si el proyecto usa AISDD, `openspec/audit/*.jsonl`) y no modifica nada del proyecto. Si falta alguna de esas fuentes, recorta el informe y lo dice, pero no falla.

**Calidad de la especificación (solo con AISDD).** El resto del informe mide velocidad, y velocidad sin calidad es media foto. De la auditoría salen tres cifras que la completan sin instrumentar nada nuevo:

- **Correcciones por change** — retrabajo de *especificación*, complementario al churn, que mide retrabajo de *código*. Se leen distinto: churn alto con correcciones bajas suele ser refactor legítimo; correcciones altas con churn bajo significa que las specs iban mal y alguien lo absorbió adivinando. Muchas correcciones en un change apuntan a su `open change`, no a un equipo lento.
- **% de decisiones que la IA resolvió sin preguntar** — cuánta autonomía se está tomando el pre-flight.
- **Lead time real `open change` → `close change`**, medido de la traza en vez de inferido.

Es una **cota inferior**: solo cuenta las correcciones que llegaron a `decisions.md`. Sirve para comparar changes entre sí, no como recuento exacto — y el informe lo dice donde se lee. Se desactiva con `--no-audit`.

⚠️ **El registro no es retroactivo.** `git log` alcanza todo el historial, pero la traza empieza el día que creaste `docs/aidd-activity.md`. Si quieres medir un sprint, actívalo **antes** de empezarlo.

El ahorro es harina de otro costal, y conviene entender por qué antes de enseñar un número a nadie:

- El registro mide **tiempo atendido**, no esfuerzo total. No ve revisar, probar, teclear a mano ni reunirse, y lo que escribes tú en tu editor no pasa por las tools de la IA.
- Por eso `aidd metrics` **se niega a calcular ahorro** salvo que el equipo declare su esfuerzo real en la ventana medida (`--real-days`, de partes de horas o worklogs). Restar el tiempo atendido al baseline daría aceleraciones de x100, que es justo el tipo de cifra que no aguanta una pregunta incómoda.
- El baseline es el esfuerzo humano de las tallas XS/S/M/L/XL, y es legítimo porque se declaró **antes** de ejecutar. No es un ajuste a posteriori.
- Si la aceleración resultante supera x10, el informe la marca como **no publicable** y explica que casi siempre significa esfuerzo infradeclarado o baseline inflado.

## MCP recomendados

Los skills integran dos servicios externos vía **MCP**. Ambos son **opcionales**: sin ellos todo funciona igual y el paso correspondiente se omite con aviso (los skills nunca caen a llamadas REST manuales ni gestionan credenciales). Los skills localizan las tools **por función**, no por nombre, así que cualquier variante de MCP equivalente sirve.

| MCP | Quién lo usa | Para qué |
|-----|--------------|----------|
| **Atlassian (Jira)** | `aidd-sprint-planning` · `aisdd-specs` | Volcado del sprint-plan (sprints + Stories), sub-tareas por change, transiciones In Progress/Done, re-faseado y reconstrucción del enlace |
| **Figma** | `aidd-style-guide` | Extraer la identidad visual real de un diseño (paleta, tipografía, espaciado, tokens) en vez de inferirla |

**Atlassian.** ⚠️ **El MCP remoto oficial de Atlassian NO expone las operaciones Agile** (crear sprints, añadir/mover issues de sprint): cubre issues y transiciones, pero **no basta para el volcado de `aidd sprint-planning`** — lo comprobamos en un proyecto real y hubo que instalar otro. Recomendación según lo que necesites:

- **Flujo completo (volcado de sprints incluido)** — un MCP de la comunidad que exponga la API Agile de Jira, p. ej. [`mcp-atlassian`](https://github.com/sooperset/mcp-atlassian) con API token (tools `jira_create_sprint`, `jira_add_issues_to_sprint`, `jira_get_sprints_from_board`, …). Es el que usamos. Instalación:

  1. Crea un **API token** de Atlassian en <https://id.atlassian.com/manage-profile/security/api-tokens>.
  2. Registra el MCP en Claude Code (requiere [`uv`](https://docs.astral.sh/uv/); alternativa: la imagen Docker `ghcr.io/sooperset/mcp-atlassian` del mismo proyecto):

  ```bash
  claude mcp add jira-agile \
    --env JIRA_URL=https://<tu-org>.atlassian.net \
    --env JIRA_USERNAME=<tu-email> \
    --env JIRA_API_TOKEN=<tu-token> \
    -- uvx mcp-atlassian
  ```

  3. Verifica con `/mcp` que el servidor aparece conectado y expone las tools `jira_*` (incluidas las de sprint).

- **Solo ciclo de changes de aisdd** (sub-tareas, transiciones — sin crear sprints): también vale el MCP remoto oficial (OAuth): `claude mcp add --transport sse atlassian https://mcp.atlassian.com/v1/sse`.

Requisitos en Jira: un proyecto con **board Scrum** (los sprints viven en el board) y permisos para crear issues y sprints. Nota: los nombres de issue types varían por tipo de proyecto (*team-managed* usa `Subtask`; *company-managed*, `Sub-task`) — los skills los descubren y verifican solos antes de crear nada.

**Figma.** El skill propone `figma-developer-mcp` (requiere un token personal de Figma):

```bash
claude mcp add figma -- npx -y figma-developer-mcp --figma-api-key=<TU_TOKEN> --stdio
```

Si no hay MCP, `aidd style-guide` ofrece alternativas: API REST de Figma o un export de design tokens a JSON.

## Metodología

La metodología AIDD-SDD viaja **dentro** de los plugins `aidd` y `aisdd` (carpeta `methodology/`). Los skills la referencian con `${CLAUDE_PLUGIN_ROOT}/methodology/native-ai-aidd-sdd.md`, así que resuelve tras instalar en cualquier repo. Es referencia de solo lectura; no se carga automáticamente.

El plugin `aiad` lleva su propia metodología (`${CLAUDE_PLUGIN_ROOT}/methodology/native-ai-aiad.md`): el manifiesto *ia-in-the-loop*, el catálogo de skills, el puente HU ↔ change y la bitácora de autoría.

**FAQ.** [FAQ.md](FAQ.md) responde las preguntas frecuentes del ciclo AISDD: qué crea cada comando (`open`/`implement`/`close change`), qué ocurre en Jira en cada paso, quién crea Stories y sprints, y los casos límite (enlace perdido, re-faseado, sprints de horas).

**Vistas HTML.** Junto a cada `.md` de metodología hay un `.html` homónimo (misma carpeta) renderizado con `booster-docs`, para lectura humana cómoda con índice navegable — [native-ai-aidd-sdd.html](plugins/aidd/methodology/native-ai-aidd-sdd.html), [getting-started](plugins/aidd/methodology/native-ai-aidd-sdd-getting-started.html) y [native-ai-aiad.html](plugins/aiad/methodology/native-ai-aiad.html). El Markdown sigue siendo la **única fuente de verdad**.

## Mantenimiento

- **Versionado**: cada `plugin.json` fija `version` (semver). **Sube la versión al publicar cambios**; si no, los usuarios ya instalados no recibirán las novedades (Claude Code los cree en la misma versión). Tras subir cambios, los usuarios actualizan con `/plugin marketplace update aidd-sdd`.
- **Regenerar los HTML de metodología** (obligatorio si se edita un `.md` de `methodology/`; la copia de `aisdd` es un espejo, se sobreescribe con `cp`):

  ```bash
  python3 plugins/boosters/skills/booster-docs/scripts/render_docs_html.py \
    --input plugins/aidd/methodology/native-ai-aidd-sdd.md \
    --output plugins/aidd/methodology/native-ai-aidd-sdd.html \
    --title "Native AI · AIDD-SDD — Metodología AI-Native"
  python3 plugins/boosters/skills/booster-docs/scripts/render_docs_html.py \
    --input plugins/aidd/methodology/native-ai-aidd-sdd-getting-started.md \
    --output plugins/aidd/methodology/native-ai-aidd-sdd-getting-started.html \
    --title "AIDD-SDD — Getting Started"
  python3 plugins/boosters/skills/booster-docs/scripts/render_docs_html.py \
    --input plugins/aiad/methodology/native-ai-aiad.md \
    --output plugins/aiad/methodology/native-ai-aiad.html \
    --title "Native AI · AIAD — AI-Augmented Development"
  cp plugins/aidd/methodology/native-ai-aidd-sdd.html \
     plugins/aidd/methodology/native-ai-aidd-sdd-getting-started.html \
     plugins/aisdd/methodology/
  ```
- **Versión de Mermaid**: `booster-docs` y `booster-uml` fijan la misma versión y `sha256` del bundle (`MERMAID_VERSION`, `MERMAID_SHA256`, `MERMAID_SIZE` en sus respectivos scripts). Comparten el `mermaid.min.js` de `docs/html/`, así que **si actualizas la versión, hazlo en los dos** y recalcula el hash:

  ```bash
  curl -sS -o /tmp/m.js https://cdn.jsdelivr.net/npm/mermaid@<version>/dist/mermaid.min.js
  wc -c /tmp/m.js && sha256sum /tmp/m.js   # tamaño y hash que van a los dos scripts
  ```
- **Hook de actividad compartido**: `hooks/aidd-activity-hook.sh` es el **mismo fichero** en los cuatro plugins (cada plugin instalado es autónomo, no pueden compartir ficheros). Si lo tocas, cópialo a los cuatro y comprueba que coinciden:

  ```bash
  cp plugins/aidd/hooks/aidd-activity-hook.sh plugins/aisdd/hooks/
  cp plugins/aidd/hooks/aidd-activity-hook.sh plugins/aiad/hooks/
  cp plugins/aidd/hooks/aidd-activity-hook.sh plugins/boosters/hooks/
  sha256sum plugins/*/hooks/aidd-activity-hook.sh   # los cuatro deben coincidir
  ```
- **Hacerlo público** (si algún día procede): `gh repo edit grananda/aidd-marketplace --visibility public`. La instalación entonces no requeriría credenciales.
- **Desarrollo local** antes de publicar: `claude --plugin-dir ./plugins/aidd` (un plugin suelto) o `/plugin marketplace add ./` (marketplace local); validar con `claude plugin validate ./`.

---

NTT DATA Spain GDN-e.
