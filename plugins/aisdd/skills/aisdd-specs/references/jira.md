# Integracion con Jira (opcional)

> Referencia del skill `aisdd-specs`. El indice y las reglas comunes estan en `SKILL.md`.

## Integracion con Jira (opcional)

Enlaza cada change de OpenSpec con su historia de usuario (HU) en Jira y mueve los tickets de columna al implementar y cerrar. Es **opcional** y **no intrusiva**: si no esta configurada, todos los comandos funcionan igual y este bloque se omite por completo.

### Activacion y gating

Este bloque solo actua si se cumplen **las dos** condiciones:

1. Existe una seccion `jira:` en `openspec/config.yaml` (la escribe `aidd sprint-planning` al volcar el plan, o el usuario a mano).
2. Hay tools del MCP de Atlassian disponibles (localizalas por funcion con la busqueda de herramientas; los nombres varian entre versiones, no los asumas).

Si falta cualquiera de las dos, **omite la sincronizacion sin error**: anota una linea en el resumen del comando ("Jira no configurado o MCP no disponible: sincronizacion omitida") y continua. Nunca caigas a llamadas REST manuales ni gestiones credenciales desde el skill.

**Excepcion — enlace perdido (no omitas en silencio).** Si falta la configuracion o el registro pero hay **evidencia de un volcado previo** — `docs/sprint-plan.md` menciona un volcado o claves de Story ya creadas, existe `docs/jira-sync.md` sin seccion `jira:`, o el usuario afirma que las Stories ya existen en el board — **no** trates el caso como "sin configurar": avisa explicitamente de que el enlace HU<->Jira se perdio (las sub-tareas de los changes no se crearan y las Stories no se moveran) y ofrece **reconstruirlo** (ver "Reconstruccion del enlace perdido"). El humano decide; si declina, entonces si, omite con el aviso estandar.

### Modelo de datos en Jira (acordado)

- Cada **HU** es una **Story** (la crea `aidd sprint-planning`).
- Un **change** implementa **una o varias HU** (segun `docs/roadmap.md`, `docs/sprint-plan.md` y el detalle de HU). El change **mueve las Stories de todas las HU que implementa** — no solo la "principal".
- **Regla de decision, por HU (no por change)**: cuenta en cuantos changes aparece esa HU (campo `hus`/`change_hint` del roadmap y registro `docs/jira-sync.md`):
  - **HU cubierta por 1 solo change** -> **modo Story directa**: se opera sobre la Story; **no se crea sub-tarea** (una sub-tarea 1:1 solo duplica la Story y ensucia el board).
  - **HU cubierta por 2 o mas changes** -> **modo sub-tarea**: se crea **una sub-tarea por change** bajo la Story de esa HU (progreso atomico); la Story se cierra cuando **todas** sus sub-tareas estan Done.
- Un mismo change puede mezclar ambos modos: para una HU suya mueve la Story directa y para otra crea/mueve sub-tarea.
- **El modo se resuelve en el momento del comando.** Si un re-faseado hace que una HU en modo directo gane un segundo change mas tarde, los changes **nuevos** crean sub-tarea a partir de entonces (el trabajo ya hecho no se representa retroactivamente); la Story vuelve a In Progress al implementar el nuevo change y se cierra cuando sus sub-tareas pendientes esten Done.
- **Lanes (modo `multilane`)**: el `lane-id` se refleja como **etiqueta (label) de la Story y de sus sub-tareas**, para poder filtrar el board por linea de trabajo. Es lo unico que cambia: **el modelo hibrido HU<->Story<->sub-tarea no se altera**, no se crean boards ni epicas por lane, y el lane nunca sustituye a la HU como unidad. Si la etiqueta no se puede escribir (permisos, campo no disponible), avisa y continua: es informativo, no estructural.

### Configuracion (`openspec/config.yaml`, seccion `jira`)

```yaml
jira:
  site: <p. ej. miorg.atlassian.net>
  project_key: <CLAVE>
  board_id: <id del board Scrum>
  story_issue_type: Story            # tipo de issue para las HU
  subtask_issue_type: Sub-task       # tipo de issue para los changes
  status_in_progress: In Progress    # nombre objetivo de la columna "en curso"
  status_done: Done                  # nombre objetivo de la columna "terminado"
  assignee_override: <accountId o vacio>   # usar si el MCP autentica una cuenta de servicio
```

No inventes valores: si falta una clave necesaria, preguntala una vez y persistela en `config.yaml`.

**Issue types: descubrir, no asumir.** Los nombres `Story`/`Sub-task` del ejemplo son solo orientativos y **varian segun el tipo de proyecto Jira**: en proyectos *team-managed* la sub-tarea se llama `Subtask` y en *company-managed* `Sub-task`. Antes de crear el primer issue, lee los issue types reales del proyecto (tool del MCP de tipos de issue del proyecto), elige como `subtask_issue_type` el tipo con `subtask: true` y verifica que `story_issue_type` existe; si el valor configurado no coincide con ninguno real, corrigelo en `config.yaml` (pregunta si hay mas de un candidato) en lugar de dejar que la creacion falle.

### Registro de enlace (`docs/jira-sync.md`)

Fuente de verdad del mapeo HU <-> change <-> issue de Jira. Lo inicializa `aidd sprint-planning` (HU -> clave de Story) y lo completan los comandos de change. El **estado se lleva por HU/Story**; la columna de sub-tareas **solo se rellena en modo sub-tarea** (HU repartida entre 2+ changes) y queda vacia (`—`) en modo Story directa. Estructura en tabla:

| HU | Story (Jira) | change(s) | Sub-tarea(s) (Jira) | estado |
|----|--------------|-----------|---------------------|--------|
| HU-02 | ABC-11 | foundation | — | done |
| HU-03 | ABC-12 | back-auth, front-auth | ABC-45, ABC-46 | in_progress |

Regla de oro: **lee el registro antes de crear o transicionar nada y no dupliques**. Re-ejecutar un comando no debe crear sub-tareas repetidas ni revertir estados de forma incoherente.

### Reconstruccion del enlace perdido

Si las Stories ya existen en Jira pero falta `docs/jira-sync.md` y/o la seccion `jira:` (p. ej. un volcado antiguo que no persistio el enlace), el registro se puede **reconstruir sin tocar Jira** — las claves de issue son permanentes, asi que la operacion es de solo lectura contra Jira y de escritura solo local:

1. **Confirma con el humano** antes de empezar (que proyecto/board y que volcado se esta recuperando).
2. **Completa la configuracion**: pregunta los valores que falten de la seccion `jira:` (site, project_key, board_id...) y persistela en `openspec/config.yaml` (o en la cabecera de `docs/jira-sync.md` si no existe `openspec/`).
3. **Lee las Stories desde Jira** via MCP (issues del proyecto/board con el `story_issue_type` configurado) y las sub-tareas que ya cuelguen de ellas.
4. **Mapea HU <-> Story** cruzando el id/titulo de la HU (de `docs/mapa-historias-usuario.md` / `docs/sprint-plan.md`) con el summary de cada Story. **No adivines**: si un mapeo no es deducible con confianza, presenta la tabla propuesta y pide confirmacion antes de escribirla; nunca te fies solo de rangos de claves.
5. **Escribe `docs/jira-sync.md`** con una fila por HU (clave de Story real, changes previstos si el roadmap existe, sub-tareas encontradas y su estado actual leido de Jira).
6. **Nunca crees ni recrees issues durante la reconstruccion** (las claves quemadas no vuelven); registra la operacion en la auditoria (`openspec/audit/`).

### Resolucion del usuario asignado

1. Obten el `accountId` de la cuenta autenticada en el MCP (tool de tipo "current user" / "myself").
2. Si `jira.assignee_override` tiene valor (porque el MCP usa una cuenta de bot/servicio compartida), asigna a ese `accountId` en su lugar.
3. Si no se puede resolver ningun `accountId`, mueve de columna pero **no** toques el campo assignee, y avisa en el resumen.

### Descubrimiento de transiciones (no hardcodear)

Los nombres e ids de columna varian por workflow de Jira. Para mover un issue:

1. Consulta via el MCP las **transiciones disponibles** del issue.
2. Elige la transicion cuyo estado destino case (ignorando mayusculas/acentos) con `status_in_progress` o `status_done`, admitiendo sinonimos comunes (In Progress / En curso / Doing; Done / Completado / Finalizado / Cerrado).
3. Si ninguna transicion casa, **no fuerces**: avisa en el resumen y deja el issue como esta.

### Que hace cada comando (el detalle vive en cada comando)

Para **cada HU** que implementa el change, resuelve su modo (directa vs sub-tarea) y aplica:

| Comando | HU en 1 change (Story directa) | HU en 2+ changes (sub-tarea) |
|---------|--------------------------------|------------------------------|
| `open change` | **No** cambia el estado de la Story (sigue To Do: abrir es disenar specs, no implementar); registra el mapeo change -> HU en `docs/jira-sync.md` | Crea la **sub-tarea** del change bajo la Story (To Do) si no existe |
| `implement change` | Mueve la **Story** a **In Progress** y la asigna | Mueve la **sub-tarea y su Story** a In Progress y las asigna |
| `close change` | Mueve la **Story** a **Done** | Sub-tarea a **Done**; la Story a Done **solo si todas sus sub-tareas estan Done** |

En modo `multilane`, `open change` anade ademas el `lane-id` como **etiqueta** de la Story (y de la sub-tarea si la crea). Es informativo: si falla, avisa y continua.

Toda accion de Jira se refleja en el resumen del comando (claves de issue afectadas y transicion aplicada) y se anota en la entrada de auditoria (`output_files`/`notes`). Si una accion de Jira falla, **no bloquees** el resultado funcional del comando OpenSpec: informa el fallo en el resumen y deja el estado reconstruible.
