---
name: aisdd-specs
description: AISDD (AI Spec-Driven Development) — gestiona especificaciones sobre OpenSpec mediante los comandos `aisdd init`, `aisdd roadmap`, `aisdd open change`, `aisdd implement change`, `aisdd close change`, `aisdd lane`, `aisdd prototype-ux` y `aisdd uml` (alias legacy equivalentes con prefijo `native-ai ...` siguen funcionando). Coordina documentacion funcional/tecnica/arquitectura de AIDD y la capa de entrega de AIBA (planificacion-proyecto, sprint-plan, plan-revision-hu), roadmaps, diagramas con booster-uml y prototipos con booster-ux. `aisdd init` registra en `openspec/config.yaml` tanto la documentacion de diseno como la capa de entrega existente y, en **proyectos ya en marcha**, analiza el codigo para sembrar las **specs base** de OpenSpec (`openspec/specs/<capability>/spec.md`) con marcas `UNKNOWN` y `LEGACY`, de modo que los changes posteriores apliquen deltas sobre una linea base en vez de partir de cero; `open change` comprueba antes del pre-flight que hay contexto de proyecto util y lo pide si falta, y `aisdd roadmap` lee el `docs/sprint-plan.md` para fasear alineado a los sprints. Los comandos `open change` e `implement change` comparten un mismo pre-flight de dudas (una sola seccion con variantes `[APERTURA]`/`[IMPLEMENTACION]`) antes de generar los specs y antes de aplicar las instrucciones de OpenSpec: las dudas **bloqueantes se preguntan siempre y sin limite**, y cuantas preferencias y confirmaciones se plantean se configura por proyecto en la seccion `preflight` de `openspec/config.yaml` (`all` o un entero); lo que queda fuera del limite se resuelve con el default y se registra como `Origen: auto-default`. Todos escriben una entrada de auditoria estructurada en `openspec/audit/` (salvo `aisdd lane`, que solo mueve un puntero local); el skill incluye scripts Python sin dependencias — `audit.py`, `agents_block.py` y `check_mojibake.py` — que ejecutan de forma determinista la auditoria, los bloques idempotentes de `AGENTS.md` y la deteccion de mojibake, con degradacion a la prosa del documento si Python no esta disponible. Integracion opcional con Jira (MCP de Atlassian) con modelo hibrido por HU: si una HU se realiza con un solo change se opera directamente sobre su Story (sin sub-tarea); si se reparte entre varios changes, cada change es una sub-tarea bajo la Story. `open change` registra el enlace change<->HU (creando sub-tarea solo cuando toca), `implement change` mueve a In Progress las Stories de todas las HU que implementa (y su sub-tarea si existe), y `close change` las pasa a Done (una Story con sub-tareas solo cuando todas estan Done); sin configuracion, los comandos funcionan igual y la sincronizacion se omite — salvo que haya evidencia de un volcado previo sin registro (enlace perdido), en cuyo caso avisa y ofrece reconstruir `docs/jira-sync.md` leyendo las Stories desde Jira sin recrear issues. Durante `implement change`, los cambios que ningun spec habia especificado se clasifican en niveles con una regla de corte explicita (un documento AIDD solo se corrige cuando queda desmentido) y se registran como `Tipo: correccion` en `decisions.md`, sin escalar ni re-aplicar el change. Ofrece **tres modos de faseado**, elegidos en el pre-flight de `aisdd roadmap` y registrados en `roadmap.mode`: **`atomic`** (clasico, un change abierto), **`waves`** (oleadas: hasta `parallel_developers` fases a la vez respetando `depends_on`; ordena el trabajo pero **no garantiza** aislamiento ni lo verifica ningun comando) y **`multilane`** (lanes): `aisdd roadmap` puede fraccionar el faseado en lineas de trabajo (lanes) con rutas y specs disjuntas —nomenclatura `F0` / `F-<lane>-NN` / barreras `FB-NN`— para que varios devs trabajen en paralelo sin romper el invariante de un unico hilo por superficie de decision; `aisdd lane [list|switch|status]` selecciona la linea activa (puntero local `openspec/.lane`, tipo rama de Git), `open change` permite un change abierto **por lane**, `close change` verifica que el change no se salio de las rutas de su lane, y una correccion que toca el contrato compartido es nivel 4 (parada coordinada), no una correccion local. Los lanes se prefieren independientes, pero admiten **dependencias declaradas** (`depends_on`) cuando la independencia total no es viable, siempre que sean puntuales, aciclicas, con coste explicito y **sin compartir rutas**. El detalle de cada comando vive en `references/*.md` y se lee **bajo demanda**: este `SKILL.md` es el indice con las reglas comunes y una tabla de que fichero leer para cada tarea. Usar cuando el usuario invoque `aisdd ...` o `native-ai ...`, o pida trabajar con especificaciones OpenSpec/Native AI.
metadata:
  author: NTT DATA Spain GDN-e
  version: "2.0.1"
---

# aisdd-specs (AI Spec-Driven Development)

Usa este skill cuando el usuario pida trabajar con especificaciones AISDD / OpenSpec, o cuando invoque cualquiera de estos comandos (prefijo primario **`aisdd`**; el prefijo **`native-ai`** se mantiene como **alias legacy** equivalente):

- `aisdd init`            (alias: `native-ai init`)
- `aisdd roadmap`         (alias: `native-ai roadmap`)
- `aisdd open change [what-you-want-to-build]`       (alias: `native-ai open change ...`)
- `aisdd implement change [what-you-want-to-build]`  (alias: `native-ai implement change ...`)
- `aisdd close change [what-you-want-to-build]`      (alias: `native-ai close change ...`)
- `aisdd lane [list | switch <lane-id> | status]`    (alias: `native-ai lane ...`)
- `aisdd prototype-ux [what-you-want-to-build]`      (alias: `native-ai prototype-ux ...`)
- `aisdd uml [what-you-want-to-build]`               (alias: `native-ai uml ...`)

> **Alias legacy.** `aisdd <cmd>` y `native-ai <cmd>` son **equivalentes**: ejecutan exactamente el mismo flujo. `aisdd` es el prefijo primario (consistente con `aidd`/`aiad`); `native-ai` se conserva para no romper `AGENTS.md`, roadmaps y referencias de proyectos ya iniciados. En este documento el prefijo `aisdd` es el canonico; donde leas un comando, el equivalente `native-ai` es igual de valido.

Responde y documenta en espanol siempre que sea posible. Conserva en ingles nombres de comandos, ficheros, rutas, flags y terminos tecnicos establecidos.

## Como usar este documento

Este `SKILL.md` es el **indice**: reglas comunes y que leer para cada cosa. El detalle de cada comando vive en `references/`, y **se lee bajo demanda**: no cargues un fichero que no necesitas para el comando en curso.

| Vas a... | Lee |
|---|---|
| Inicializar el proyecto (`aisdd init`), tambien sobre un repo ya en marcha | `references/init.md` |
| Fasear el desarrollo (`aisdd roadmap`), elegir modo y numero de fases | `references/roadmap.md` |
| Entender los tres modos de paralelismo antes de elegir | `references/parallelism.md` |
| Abrir un change (`aisdd open change`) | `references/open-change.md` |
| Implementar un change (`aisdd implement change`) y clasificar correcciones | `references/implement-change.md` |
| Cerrar un change (`aisdd close change`) | `references/close-change.md` |
| Cambiar de linea de trabajo (`aisdd lane`) | `references/lane.md` |
| Resolver dudas antes de generar specs o de implementar | `references/preflight.md` |
| Prototipos UX (`aisdd prototype-ux`) | `references/prototype-ux.md` |
| Diagramas UML (`aisdd uml`) | `references/uml.md` |
| Sincronizar con Jira | `references/jira.md` |
| Escribir la entrada de auditoria | `references/audit.md` |
| Ejecutar los scripts del skill | `references/scripts.md` |

**Dependencias frecuentes entre ficheros**, para no leer de mas ni de menos:

- `open-change.md` e `implement-change.md` **requieren** `preflight.md`: el pre-flight es obligatorio en ambos y esta descrito una sola vez.
- `roadmap.md` **requiere** `parallelism.md` si el proyecto tiene mas de un developer.
- `open/implement/close-change.md` **requieren** `parallelism.md` solo si `roadmap.mode` es `waves` o `multilane`.
- Cualquier comando que escriba artefactos **requiere** `audit.md`, y `scripts.md` si va a usar los scripts (que es la via preferente).

## Reglas generales

- Trabaja desde la raiz del proyecto del usuario.
- Antes de ejecutar comandos, confirma el estado relevante con comandos no destructivos (`Get-Command`, `npm list -g`, `openspec list`, busqueda de ficheros).
- Si un argumento opcional no llega, intenta resolverlo desde OpenSpec. Pregunta solo si hay ambiguedad real.
- No inventes cambios: usa el contexto del usuario y los artefactos OpenSpec existentes.
- Si necesitas usar otro skill, invocalo por nombre y sigue sus instrucciones.
- Verifica que los comandos terminan correctamente y resume rutas/artefactos generados.
- Si un flujo depende del modelo usado, adapta la estrategia al presupuesto de contexto. Si no conoces el modelo real o su ventana, usa una estrategia conservadora de contexto medio-bajo.

## Dependencias de skills

Comprueba si existen estos directorios en alguna ubicacion de skills conocida:

- `.agents/skills/booster-ux`
- `.agents/skills/booster-uml`
- `$env:USERPROFILE\.agents\skills\booster-ux`
- `$env:USERPROFILE\.agents\skills\booster-uml`
- `$env:USERPROFILE\.codex\skills\booster-ux`
- `$env:USERPROFILE\.codex\skills\booster-uml`

Si falta `booster-ux`, avisa: `No encuentro el skill booster-ux. Debe instalarse o copiarse en .agents/skills/booster-ux o en una carpeta global de skills del usuario.`

Si falta `booster-uml`, avisa: `No encuentro el skill booster-uml. Debe instalarse o copiarse en .agents/skills/booster-uml o en una carpeta global de skills del usuario.`

La ausencia de un skill no debe bloquear `init`, `implement` o `close`; si bloquea diagramas o prototipos, informa y deja los comandos OpenSpec completados.

## Verificacion final

Al terminar cualquier comando, informa:

- comando Native AI solicitado
- comando OpenSpec ejecutado, si aplica
- cambio objetivo, si aplica
- artefactos creados o actualizados (incluye `decisions.md` si hubo pre-flight)
- decisiones tomadas en el pre-flight y cuales quedan `pendientes`, si aplica
- entrada de auditoria escrita: ruta del fichero `openspec/audit/YYYY-MM.jsonl` y `id` de la entrada
- skills auxiliares usados o pendientes de instalar
- errores o tareas manuales pendientes
- documentación faltante (en caso de que aplique)
- **en modo `multilane`**: lane activo, resultado de la verificacion de independencia si hubo cierre, y barreras pendientes que bloqueen al resto de lanes
- si pasaste `check_mojibake.py` sobre los artefactos escritos: el resultado, y **que ficheros quedan con mojibake sin reparar** (los que tengan `U+FFFD` hay que regenerarlos, no se pueden arreglar)
