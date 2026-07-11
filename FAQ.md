# FAQ — El proceso AISDD

Preguntas frecuentes sobre el ciclo de ejecución de **AISDD** (`aisdd-specs`): qué hace cada comando, qué toca en Jira y qué no. Referencia rápida para talleres y onboarding; el detalle normativo vive en `plugins/aisdd/skills/aisdd-specs/SKILL.md`.

> Comandos con prefijo primario `aisdd`; el alias legacy `native-ai <cmd>` es equivalente.

## El ciclo en una imagen

```text
aisdd init  →  aisdd roadmap  →  por cada change:
                                   aisdd open change    (specs · Jira: registro, sin mover estados)
                                   aisdd implement change (código · Jira: → In Progress)
                                   aisdd close change     (archivo · Jira: → Done)
```

---

## ¿Qué se crea con un `aisdd open change <slug>`?

1. **Pre-flight de dudas** (máx. 7 preguntas): las respuestas se persisten en `openspec/changes/<slug>/decisions.md`.
2. **El change de OpenSpec** (`openspec new change`): la carpeta `openspec/changes/<slug>/` con sus specs validados — `proposal.md`, `design.md`, `spec.md` (uno o varios) y el `decisions.md` del pre-flight.
3. **Diagramas UML** (HTML vía `booster-uml`) **solo si el change lo amerita**: flujos multi-componente, entidades nuevas, máquinas de estados, integraciones. En changes triviales (scaffolding, config, textos) se omite con aviso; `aisdd uml <slug>` los genera bajo demanda.
4. **Entrada de auditoría** en `openspec/audit/YYYY-MM.jsonl` (hashes de input/output, modelo, decisiones).

**No se crea código**: abrir un change es diseñar y validar las specs. El código llega con `implement`.

## ¿Qué ocurre en Jira con un `open change`?

**Se registra, no se mueve nada.** Las Stories siguen en **To Do** — abrir es diseñar specs, no empezar a trabajar.

- Se identifica qué **HU** implementa el change y se anota en `proposal.md` y en `docs/jira-sync.md`.
- **Modelo híbrido, decidido por HU** (no por change):
  - HU realizada con **un solo change** → **no se crea nada** en Jira; el change operará directamente sobre la Story.
  - HU repartida entre **2 o más changes** → se crea la **sub-tarea de este change** bajo la Story de esa HU (en To Do), para poder seguir el progreso atómico.
- Un mismo change puede mezclar ambos modos si implementa varias HU.

## ¿Qué ocurre con un `aisdd implement change <slug>`?

1. **Pre-flight de dudas** sobre las specs del change (lee `design.md`, `proposal.md`, `spec.md`, `decisions.md` previos; máx. 7 preguntas; los bloqueantes sin respuesta detienen el comando).
2. **Implementación del código** (`openspec instructions apply --change <slug>`): la IA escribe el código siguiendo las specs.
3. **Jira**: mueve a **In Progress** las Stories de **todas** las HU que implementa el change (y la sub-tarea del change, si esa HU está repartida), **asignándolas** al usuario autenticado en el MCP (o al `assignee_override`).
4. Entrada de auditoría.

## ¿Qué ocurre con un `aisdd close change <slug>`?

1. **Archivo del change** (`openspec archive`): el change deja de estar abierto y sus specs quedan consolidadas.
2. **Jira**, por cada HU del change:
   - **HU de un solo change** → su **Story pasa a Done** directamente.
   - **HU repartida** → la **sub-tarea de este change pasa a Done**; la **Story solo pasa a Done cuando TODAS sus sub-tareas están Done**. Si falta alguna, la Story queda en In Progress y el resumen indica qué changes faltan — una HU nunca se cierra a medias.
3. Entrada de auditoría.

## Resumen: Jira por comando

| Comando | HU en 1 change (Story directa) | HU en 2+ changes (sub-tarea) |
|---------|--------------------------------|------------------------------|
| `open change` | Registra el mapeo; Story sigue en To Do | Crea la sub-tarea del change (To Do) |
| `implement change` | Story → **In Progress** (+ asignación) | Sub-tarea **y** Story → In Progress |
| `close change` | Story → **Done** | Sub-tarea → Done; Story → Done **solo si todas** sus sub-tareas están Done |

---

## ¿Quién crea las Stories y los sprints?

`aidd sprint-planning` (Fase 3.5), en su volcado opcional a Jira: crea los **sprints** con fechas en el board Scrum y **una Story por HU** asignada a su sprint, e inicializa `docs/jira-sync.md` + la sección `jira:` de `openspec/config.yaml`. Los comandos de aisdd **nunca crean Stories ni sprints** — solo sub-tareas (cuando toca) y transiciones.

## ¿Quién inicia el sprint?

**Un humano, en el board de Jira** ("Start sprint"). Los skills crean los sprints en estado *future* y mueven issues de columna, pero el arranque y cierre del sprint es una ceremonia del equipo — por diseño.

## ¿Y el roadmap? ¿Toca Jira?

**No.** `aisdd roadmap` es 100% local: genera `docs/roadmap.md`, los prompts y la sección `roadmap` de `config.yaml`. Si existe `docs/sprint-plan.md`, fasea **alineado a los sprints**; el `change_hint` de cada fase es la clave de unión que luego usa `open change` para saber qué HU (y qué Story) le corresponde.

## ¿Qué pasa si no tengo Jira configurado?

Nada se rompe: todos los comandos funcionan igual y la sincronización **se omite con un aviso**. Excepción: si hay **evidencia de un volcado previo** (el sprint-plan menciona Stories creadas) pero falta `docs/jira-sync.md` o la config, el skill lo trata como **enlace perdido** — avisa y ofrece **reconstruir el registro** leyendo las Stories desde Jira (solo lectura; jamás recrea issues).

## ¿Por qué nunca se borran ni recrean issues?

Las claves de Jira (`AT-7`) son **permanentes**: un issue borrado quema su número para siempre y deja huecos. Por eso el re-faseado **mueve** HU entre sprints (y borra solo sprints vacíos, que no queman nada), la reconstrucción del enlace es de solo lectura, y las Stories se crean **una única vez**.

## Una HU estaba en un solo change y un re-faseado la reparte en dos, ¿qué pasa?

El modo se resuelve **en el momento de cada comando**: los changes **nuevos** crean sub-tarea a partir de entonces (el trabajo ya hecho no se representa retroactivamente). La Story vuelve a In Progress al implementar el nuevo change y se cierra cuando sus sub-tareas pendientes estén Done.

## ¿Sirven sprints de horas (demo/taller) en vez de semanas?

Sí. Los skills no usan fechas ni estado del sprint en su lógica — operan sobre issues. Solo recuerda las reglas del propio Jira: un board Scrum tiene **un sprint activo a la vez**, y al cerrar un sprint con issues abiertos Jira pedirá moverlos al siguiente.
