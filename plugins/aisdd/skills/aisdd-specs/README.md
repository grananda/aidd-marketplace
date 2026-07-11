# aisdd-specs

Skill para trabajar con especificaciones Native AI usando OpenSpec y coordinar la generacion de diagramas y prototipos con los skills `booster-uml` y `booster-ux`.

> **Alias legacy**: todo comando `aisdd <cmd>` tiene un alias equivalente `native-ai <cmd>` (herencia del antiguo plugin `sdd`). Los proyectos ya iniciados con `native-ai ...` siguen funcionando sin cambios; el prefijo primario y recomendado es `aisdd`.

## Resumen comandos

1. `aisdd init` — inicializa OpenSpec en el proyecto y comprueba dependencias.
2. `aisdd roadmap` — fasea el desarrollo y genera `docs/roadmap.md` y prompts asociados.
3. `aisdd open change <what-you-want-to-build>` — crea un cambio OpenSpec y dispara la generacion de diagramas UML.
4. `aisdd implement change <what-you-want-to-build>` — ejecuta un pre-flight de dudas con el usuario y luego aplica las instrucciones del cambio OpenSpec indicado.
5. `aisdd close change <what-you-want-to-build>` — archiva el cambio OpenSpec indicado.
6. `aisdd prototype-ux <what-you-want-to-build>` — lanza `booster-ux` por cada pantalla nueva del cambio.
7. `aisdd prototype-ux` — lanza `booster-ux` directamente siguiendo su flujo de preguntas.
8. `aisdd uml <what-you-want-to-build>` — genera el HTML con diagramas del cambio usando `booster-uml`.

## Requisitos

- Node.js y npm disponibles.
- OpenSpec instalado globalmente. Si falta, el comando `aisdd init` debe instalarlo con:

```bash
npm install -g @fission-ai/openspec@latest
```

- Skill `booster-ux` instalado en una de estas rutas:
  - `.agents/skills/booster-ux`
  - `%USERPROFILE%\.agents\skills\booster-ux`
  - `%USERPROFILE%\.codex\skills\booster-ux`

- Skill `booster-uml` instalado en una de estas rutas:
  - `.agents/skills/booster-uml`
  - `%USERPROFILE%\.agents\skills\booster-uml`
  - `%USERPROFILE%\.codex\skills\booster-uml`

Si falta alguno, el agente debe avisar e indicar donde copiarlo o instalarlo.

## Comandos disponibles

### `aisdd init`

Inicializa Native AI Specs en el proyecto:

1. Comprueba si `openspec` esta instalado.
2. Si falta, instala `@fission-ai/openspec@latest`.
3. Ejecuta `openspec init`.
4. Comprueba la disponibilidad de `booster-ux` y `booster-uml`.
5. Pregunta si el proyecto es un desarrollo nuevo o un desarrollo ya existente.
6. Si es existente, solicita las rutas de los markdowns con documentacion funcional, tecnica y de arquitectura, y actualiza `config.yaml` de OpenSpec con ese contexto inicial (`project_context.design_docs`).
7. Detecta ademas la **capa de entrega de AIDD** si existe (`docs/planificacion-proyecto.md`, `docs/sprint-plan.md`, `docs/plan-revision-hu.md`, `docs/jira-sync.md`) y la registra en `config.yaml` (`project_context.delivery_docs`), avisando de forma no bloqueante si falta alguna pieza esperable. Comprueba tambien la disponibilidad de `booster-docs`.
8. Registra los comandos del skill en el `AGENTS.md` del proyecto (lo crea si no existe) dentro de un bloque delimitado por marcadores `<!-- BEGIN/END aisdd-specs commands -->`, que se reemplaza de forma idempotente en cada ejecucion sin tocar el resto del fichero.

### `aisdd roadmap`

Fasea el desarrollo a partir de los requisitos y la arquitectura del proyecto antes de crear cambios OpenSpec.

Si el usuario no ha pasado requisitos o arquitectura, o el agente no tiene claro donde estan, debe solicitarlos antes de continuar.

La granularidad del roadmap debe adaptarse al presupuesto de contexto del modelo usado:

- contexto `bajo` (hasta 64k tokens utiles): normalmente `6-12` fases pequenas
- contexto `medio` (64k-200k): normalmente `4-8` fases
- contexto `alto` (mas de 200k): normalmente `3-6` fases

Si no se conoce el modelo real o su ventana de contexto, se debe asumir `medio`. Si la documentacion y el impacto tecnico son muy grandes, se deben crear mas fases aunque el modelo tenga mucho contexto.

El comando genera:

- `docs/roadmap.md`: division del desarrollo por fases, alcance de cada fase, dependencias, entregables OpenSpec esperados y criterios de cierre.
- `docs/prompts-roadmap-native-ai.md`: prompts para ejecutar el roadmap hasta el final usando los comandos del skill `aisdd-specs`.

**Alineacion con el sprint-plan**: si existe `docs/sprint-plan.md` (generado por `aidd sprint-planning`), el roadmap **se pliega a los sprints**: respeta su orden, corta las fases en fronteras de sprint, mantiene los changes de una HU dentro de la ventana de su sprint y no fasea HU no validadas; anota en cada fase el sprint, las HU cubiertas y el esfuerzo (humano e IA), y documenta las discrepancias en una seccion de conflictos de alineacion roadmap↔sprint. Sin `sprint-plan.md`, fasea solo por presupuesto de contexto.

Tras generar esos documentos, el comando actualiza `openspec/config.yaml` con una seccion `roadmap` (presupuesto de contexto, complejidad, rutas de los documentos y la lista ordenada de fases con su objetivo, riesgo de contexto y slug sugerido), para que los comandos posteriores dispongan de un indice navegable del roadmap.

Este comando no debe ejecutar `openspec new change` ni archivar cambios, ni editar artefactos de `openspec/` distintos de `openspec/config.yaml`.

El fichero `docs/prompts-roadmap-native-ai.md` debe usar como base operativa estos comandos:

- `aisdd open change <what-you-want-to-build>`
- `aisdd implement change <what-you-want-to-build>`
- `aisdd close change <what-you-want-to-build>`

Los prompts deben incluir el contexto minimo necesario para cada fase y evitar arrastrar informacion de fases futuras si no es necesaria todavia.

### `aisdd open change <what-you-want-to-build>`

Crea un cambio OpenSpec en dos fases:

1. **Pre-flight de dudas**: antes de generar los specs, el agente revisa el contexto disponible (objetivo del usuario, `docs/`, `README.md`, `config.yaml`, `AGENTS.md`, `CLAUDE.md`, roadmap si existe y cambios OpenSpec previos) y plantea al usuario las dudas reales que afecten al alcance y al diseño del cambio, con un presupuesto máximo de `7` preguntas. Las respuestas se persisten en `openspec/changes/<change>/decisions.md` para alimentar `design.md`, `proposal.md` y los `spec.md`.
2. **Creación del cambio**:

   ```bash
   openspec new change <what-you-want-to-build>
   ```

El argumento es opcional. Si no se indica, el agente debe crear un identificador razonable a partir del objetivo del usuario.

Tras crear el cambio, el agente debe pasar `design.md`, `proposal.md` y los ficheros `spec.md` al skill `booster-uml` para generar el HTML con diagramas.

Comportamientos clave del pre-flight:

- No pregunta lo que ya esté resuelto en el objetivo del usuario, en `docs/` (incluido `docs/roadmap.md` si existe), convenciones del repo (`README.md`, `CLAUDE.md`, `AGENTS.md`, `config.yaml`) ni en cambios OpenSpec previos relacionados.
- Clasifica cada duda como `bloqueante`, `preferencia` o `confirmacion`. Prioriza las `bloqueantes` (alcance, dominios afectados, integraciones, modelo de datos, criterios de aceptación) y agrupa las relacionadas en una sola pregunta de varias opciones.
- Si la plataforma soporta preguntas estructuradas con opciones (por ejemplo `AskUserQuestion` en Claude Code), las usa con una opción marcada `(Recomendada)`. En caso contrario presenta una lista numerada en texto plano.
- En modo no interactivo toma el default recomendado para `preferencia` y `confirmacion`, marca cada decisión con `Origen: auto-default` y, si hay `bloqueantes` sin default seguro, detiene el comando sin ejecutar `openspec new change`.
- Si tras la lectura inicial no detecta dudas reales, registra una única entrada con `Tipo: confirmacion`, `Pregunta: No se detectaron dudas durante el pre-flight` y `Decision: continuar`, y procede a crear el cambio.

### `aisdd implement change <what-you-want-to-build>`

Implementa un cambio en dos fases:

1. **Pre-flight de dudas**: antes de tocar codigo, el agente lee `design.md`, `proposal.md`, los `spec.md` y, si existen, `tasks.md` y `decisions.md` previos del cambio. Detecta dudas reales que afecten a la implementacion, las clasifica como `bloqueante`, `preferencia` o `confirmacion`, y pregunta al usuario con un presupuesto maximo de `7` dudas por cambio. Las respuestas se persisten en `openspec/changes/<change>/decisions.md`.
2. **Aplicacion de instrucciones**:

   ```bash
   openspec instructions apply --change <what-you-want-to-build>
   ```

El argumento es opcional si solo hay un cambio OpenSpec abierto. Si hay varios, el agente debe preguntar cual desea implementar.

Comportamientos clave del pre-flight:

- No pregunta lo que ya esta resuelto en `design.md`, `proposal.md`, convenciones del repo (`README.md`, `CLAUDE.md`, `AGENTS.md`, `docs/`, `config.yaml`) o en `decisions.md` previos.
- Si la plataforma soporta preguntas estructuradas con opciones (por ejemplo `AskUserQuestion` en Claude Code), las usa con una recomendacion marcada `(Recomendada)`. En caso contrario presenta una lista numerada en texto plano.
- En modo no interactivo toma el default recomendado para `preferencia` y `confirmacion`, y marca cada decision con `Origen: auto-default`. Para `bloqueantes` sin default seguro detiene el comando.
- Si una duda bloqueante queda `Decision: pendiente`, no ejecuta `openspec instructions apply`.

### `aisdd close change <what-you-want-to-build>`

Archiva un cambio:

```bash
openspec archive <what-you-want-to-build>
```

El argumento es opcional si solo hay un cambio OpenSpec abierto. Si hay varios, el agente debe preguntar cual desea archivar.

### `aisdd prototype-ux <what-you-want-to-build>`

Identifica las pantallas nuevas del cambio indicado y lanza el skill `booster-ux` por cada pantalla.

### `aisdd prototype-ux`

Lanza directamente el skill `booster-ux` y sigue su flujo de preguntas.

### `aisdd uml <what-you-want-to-build>`

Genera el HTML con diagramas asociados al cambio indicado usando `booster-uml`. Las entradas esperadas son:

- `design.md`
- `proposal.md`
- ficheros `spec.md`

## Ejemplos de uso

```text
aisdd init
```

```text
aisdd roadmap
```

```text
aisdd open change alta-de-clientes-desde-portal-web
```

```text
aisdd implement change alta-clientes-portal
```

```text
aisdd prototype-ux alta-clientes-portal
```

```text
aisdd uml alta-clientes-portal
```

```text
aisdd close change alta-clientes-portal
```

## Auditoria y trazabilidad

Cada invocacion de cualquier comando escribe una entrada estructurada en JSON Lines bajo `openspec/audit/YYYY-MM.jsonl` (un fichero por mes natural, modo append-only). El objetivo es permitir auditorias futuras del uso del skill.

Campos minimos de cada entrada:

- `id`, `timestamp` (UTC ISO 8601), `command`, `change_id`
- `skill_version`, `prompt_version` (formato `<skill_version>:<command-slug>`)
- `model`, `platform`, `user`
- `input_hash` y `input_files[]` con SHA-256 por fichero
- `output_hash` y `output_files[]` con SHA-256 por fichero
- `decisions[]` con `slug`, `type`, `origen`, `decision` (solo para `implement change`)
- `status` (`ok | partial | aborted`), `errors[]`

Comportamiento clave:

- Solo se guardan **hashes** de los ficheros, nunca el contenido literal.
- No se registran secretos, tokens, credenciales ni texto libre de las dudas del pre-flight (eso vive en `decisions.md`).
- Si el comando se aborta (por ejemplo dudas bloqueantes pendientes), igualmente se escribe la entrada con `status: aborted`.

**Retencion**: por defecto `365` dias. Sobreescribible por proyecto en este orden de precedencia:

1. `audit.retention_days` en `config.yaml` de OpenSpec
2. Fichero `openspec/audit/.retention` con el numero de dias en la primera linea
3. Default `365`

La purga es por meses completos: cuando el ultimo dia del mes representado por un `YYYY-MM.jsonl` es anterior a `hoy - retencion`, el fichero se elimina al inicio del siguiente comando. Nunca se aplica retencion inferior a `30` dias.

El JSONL es plano y sin transformaciones, listo para ingestar en Splunk, ELK o BigQuery. La decision de versionar `openspec/audit/` en Git es del proyecto.

## Resultado esperado

El agente debe informar siempre de:

- comando Native AI solicitado
- comando OpenSpec ejecutado
- cambio objetivo, si aplica
- artefactos creados o actualizados (incluye `decisions.md` si hubo pre-flight)
- decisiones tomadas en el pre-flight y cuales quedan `pendientes`, si aplica
- entrada de auditoria escrita: ruta del fichero `openspec/audit/YYYY-MM.jsonl` y `id` de la entrada
- skills auxiliares usados o pendientes de instalar
- errores o tareas manuales pendientes
