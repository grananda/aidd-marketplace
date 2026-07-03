---
name: aidd-sprint-planning
description: Fase 3.5 (paso 3.5.2) del conjunto AIDD (AI Driven Development), capa de planificacion de entrega (Delivery). Distribuye el trabajo en sprints una vez que existe el roadmap y el plan de recursos, mediante el comando `aidd sprint-planning` (alias `aidd planificacion sprints`). Actua como planificador de delivery (Scrum) que lee `docs/roadmap.md`, `docs/planificacion-proyecto.md`, `docs/detalle-historias-usuario.md` y, si existe, `docs/plan-revision-hu.md` (antesala: estado de revision de cada HU y personas envueltas, generado por `aidd hu-review-plan`) para no planificar por libre, y genera `docs/sprint-plan.md` con parametros de planificacion, unidades de trabajo con estimacion (esfuerzo real con IA frente al bruto humano S/M/L), mapa de dependencias y prerequisitos, distribucion en sprints con objetivo, capacidad y asignacion de perfiles, hitos, y riesgos de planificacion. Dimensiona la duracion del sprint por la carga real y el numero de ciclos por los gates/dependencias, evitando rellenar sprints sin sentido. Respeta el faseado por contexto del roadmap (no parte un change). Como paso final opcional, vuelca el plan a Jira via el MCP de Atlassian (crea sprints en el board del proyecto indicado y las historias asignadas a cada sprint), siempre con confirmacion humana previa. Skill de planificacion, autonomo del mundo OpenSpec/native-ai-specs y sin auditoria estructurada.
metadata:
  author: NTT DATA Spain GDN-e
  version: "1.3.0"
---

# aidd-sprint-planning (AIDD · Fase 3.5 · paso 3.5.2 · sprints)

Usa este skill cuando el usuario quiera repartir el trabajo en sprints a partir del roadmap y los recursos, o cuando invoque:

- `aidd sprint-planning`
- `aidd planificacion sprints`

Tambien cuando pida "plan de sprints", "distribuir las tareas en sprints", "planificar iteraciones", "sprint plan" o equivalentes.

Responde y documenta en espanol siempre que sea posible. Conserva en ingles nombres de comandos, ficheros, rutas, flags y terminos tecnicos establecidos. Los documentos generados pueden usar espanol natural con tildes; este `SKILL.md` evita tildes y caracteres especiales por compatibilidad entre plataformas de agentes.

## Que es AIDD y donde encaja este skill

AIDD (AI Driven Development) es un conjunto de skills de planificacion y arquitectura asistida por IA. Cada skill cubre una fase o paso del proceso descrito en `${CLAUDE_PLUGIN_ROOT}/methodology/native-ai-aidd-sdd.md` (referencia de metodologia, solo lectura):

- Fase 0 — `aidd client-requirements`.
- Fase 1 — `aidd requirements`, `aidd user-stories`, `aidd user-story-details`.
- Fase 2 — Diseno (AI Architect): `aidd prototype-architecture`, `aidd prototype`, `aidd style-guide`, `aidd architecture-proposal`, `aidd architecture`.
- **Fase 3.5 — Planificacion de entrega (Delivery)** — capa que traduce el diseno y el roadmap a algo que un equipo (humano + agentes) consume directamente:
  - `aidd project-plan` (paso 3.5.1): plan de recursos (`docs/planificacion-proyecto.md`).
  - **`aidd sprint-planning`** (este skill, paso 3.5.2): distribucion del trabajo en sprints (`docs/sprint-plan.md`).

Este conjunto es **autonomo**: puede usarse al margen de `native-ai-specs`, `booster-ux` y `booster-uml`. No depende de OpenSpec ni escribe auditoria estructurada. Las decisiones se registran de forma ligera dentro del propio documento generado.

Como complemento opcional, al final del comando se genera una **vista HTML** del plan de sprints con `booster-docs` (ver el paso final del flujo). El `.md` sigue siendo la **unica fuente de verdad**; el HTML es solo para consumo humano y no altera el flujo AIDD si `booster-docs` no esta instalado.

> Relacion con el SDD: el `roadmap` del AI Lead (Fase 3) fasea los changes segun el **presupuesto de contexto** del modelo. Este skill anade la **capa de delivery humana**: agrupa esos changes en sprints con fecha, capacidad y asignacion, para que un equipo Scrum los ejecute. **Respeta el faseado del roadmap**: no parte un change para encajarlo en un sprint; un sprint contiene changes/historias completos.

## Rol y objetivo

Actua con este rol durante todo el comando:

> Actua como planificador de delivery (Scrum / gestion de iteraciones) con criterio tecnico. Tu objetivo es distribuir las unidades de trabajo del roadmap en sprints, respetando dependencias y prerequisitos, ajustando a la capacidad del equipo definido en el plan de recursos, y produciendo un plan que un equipo humano pueda ejecutar. Planificas el CUANDO y en que orden, no el QUE se necesita (eso es `aidd project-plan`).

Criterio de salida del paso: existe `docs/sprint-plan.md` con los sprints definidos (objetivo, unidades de trabajo, estimacion, capacidad y asignacion), las dependencias respetadas y los riesgos de planificacion explicitos, de modo que el trabajo sea ejecutable por fases sin bloqueos ocultos. Lo que no se pueda resolver queda como supuesto.

## Reglas generales

- Trabaja desde la raiz del proyecto del usuario.
- **Entrada principal**: `docs/roadmap.md` (changes/fases ya ordenados por el AI Lead). **Insumo de recursos**: `docs/planificacion-proyecto.md` (equipo, capacidad, perfiles). **Detalle**: `docs/detalle-historias-usuario.md` (estimaciones S/M/L, dependencias, criterios bloqueantes).
- **Insumo de revision de HU (si existe)**: `docs/plan-revision-hu.md` (y su Excel `docs/xlsx/plan-revision-hu.xlsx`), generado por `aidd hu-review-plan`. Es la **antesala** de esta planificacion: recoge el estado de revision de cada HU (cerrada/validada, en revision, bloqueada), su persona/rol y el resultado de las reuniones funcionales (negocio) / tecnicas (TI). **No planifiques por libre**: reconcilia el reparto en sprints con ese plan (ver "Reconciliacion con el plan de revision de HU"). Si no existe, continua solo con roadmap + recursos, pero advierte de que conviene revisar y cerrar las HU antes de comprometerlas en sprint.
- Si falta `docs/roadmap.md`, avisa: el faseado por contexto lo produce el AI Lead con `native-ai roadmap` (Fase 3). Como alternativa degradada, puedes partir del mapa+detalle de historias, pero advierte de que no se respeta el faseado por contexto del modelo.
- Si falta `docs/planificacion-proyecto.md`, avisa y propon ejecutar antes `aidd project-plan`; sin recursos no hay capacidad contra la que planificar. Puedes continuar con supuestos de equipo explicitos si el usuario lo pide.
- Si existen changes de OpenSpec (`openspec/changes/`), usalos como detalle adicional de las unidades de trabajo, pero la unidad de planificacion sigue siendo el change/historia del roadmap.
- **Respeta dependencias y faseado**: F0 (foundation) antes que F1, F1 antes que F2; respeta prerequisitos entre historias (p. ej. una historia que necesita un habilitador tecnico va despues de el). No partas un change entre sprints.
- **Las tallas S/M/L son esfuerzo humano clasico, no calendario del sprint**: si el plan de recursos define la IA como recurso (velocity acelerada por IA), estima el **esfuerzo real** comprimido (la IA genera; lo que cuesta es dirigir, revisar y validar) y planifica con el real, no con el bruto.
- **No rellenes sprints**: dimensiona a la carga real (ver "Dimensionado de sprints"). No asignes "un change = un sprint" por inercia ni estires la duracion para cubrir una talla bruta. Un sprint muy por debajo de capacidad es una senal de relleno; agrupa unidades o acorta la duracion.
- No inventes unidades de trabajo nuevas. Distribuyes las que ya existen en roadmap/detalle.
- No sobrescribas un `docs/sprint-plan.md` existente sin avisar: leelo, propon los cambios y confirma.
- Este documento requiere aprobacion humana. Al terminar, deja claro que esta pendiente de revision.
- **El volcado a Jira es opcional y nunca automatico**: la fuente de verdad es `docs/sprint-plan.md`. Solo crea sprints/historias en Jira si el usuario lo confirma e indica el proyecto/board (ver "4. Volcado opcional a Jira"). Crear issues y sprints en Jira es una accion hacia un sistema externo y dificilmente reversible: confirma antes y no la repitas a ciegas.

## Flujo del comando `aidd sprint-planning`

### 1. Recopilacion de contexto (lectura previa)

Lee y consolida: `roadmap.md` (fases/changes, dependencias, riesgo de contexto), `planificacion-proyecto.md` (equipo, perfiles, capacidad), `detalle-historias-usuario.md` (estimaciones S/M/L, dependencias, criterios bloqueantes), `plan-revision-hu.md` **si existe** (estado de revision de cada HU, persona/rol implicada, resultado funcional/tecnico) y, si existen, los changes de OpenSpec.

Construye la lista de **unidades de trabajo** (change o historia) con su estimacion y sus dependencias antes de repartir.

### 1.5 Reconciliacion con el plan de revision de HU

Si existe `docs/plan-revision-hu.md`, este skill **no va por libre**: parte de el. Es la antesala directa del reparto en sprints y del volcado a Jira (sprints + personas envueltas).

- **Estado de la HU manda para comprometer**: solo comprometas en un sprint de desarrollo las HU que la revision haya dejado **cerradas/validadas**. Una HU aun **en revision** o **bloqueada** no entra en un sprint de construccion como comprometida: dejala en el backlog, planificala tras su cierre, o marca su sprint como dependiente del cierre de la revision. Refleja el desfase como riesgo si el objetivo de fecha lo requiere.
- **Personas/perfiles**: reutiliza las personas y perfiles que el plan de revision ya asocia a cada HU (quien la valida con negocio/TI) para informar la **asignacion de perfiles del sprint** y, en el volcado a Jira, el **assignee** de la Story (ver seccion 4). No inventes asignaciones nuevas si el plan de revision ya las implica.
- **Orden coherente**: respeta el orden logico de revision (fases, dependencias, agrupaciones por epica/persona) al secuenciar los sprints; no reordenes en contra del plan de revision sin justificarlo en la seccion de decisiones.
- Si el plan de revision y el roadmap **discrepan** (p. ej. una HU marcada para cerrar en la revision no esta en ningun change del roadmap, o al reves), **senalalo** como riesgo/decision en lugar de resolverlo en silencio.

### 2. Pre-flight de preguntas

Resuelve solo lo imprescindible para distribuir en sprints.

1. Cubre, como minimo: **duracion del sprint**, **capacidad** (nº de personas/perfiles disponibles por sprint, segun el plan de recursos), **fecha de inicio** y **velocity asumida** (si no hay historica, propon una y marcala como supuesto). Para la velocity, pregunta explicitamente si se planifica con **esfuerzo acelerado por IA** o con **esfuerzo bruto humano**, porque cambia el dimensionado por completo (ver "Dimensionado de sprints"). Plantea la **duracion del sprint en funcion de la carga real estimada**, no como dato fijo.
2. Clasifica cada hueco en **bloqueante**, **preferencia** o **confirmacion**.
3. No preguntes lo que roadmap o plan de recursos ya resuelven.
4. Presupuesto de preguntas: maximo **7** por ejecucion. Prioriza bloqueantes y agrupa relacionadas.
5. Formato: si la plataforma soporta preguntas estructuradas (por ejemplo `AskUserQuestion`), usalo con 2-4 opciones y marca una como `(Recomendada)`; si no, lista numerada con opciones y recomendacion.
6. Modo no interactivo: toma el default recomendado para `preferencia` y `confirmacion`; para la duracion del sprint, **no asumas un valor fijo**: derivala de la carga real estimada (un sprint cuya carga llene razonablemente la capacidad), y registrala como supuesto. Deja los `bloqueante` sin default como supuestos en el documento.
7. Si el usuario aplaza una duda, registrala como supuesto y continua.

### 2.5 Dimensionado de sprints: carga real, no relleno

Antes de repartir, dimensiona con criterio. Dos errores frecuentes a evitar:

1. **Tomar las tallas S/M/L como dias de calendario del sprint.** Las tallas de `detalle-historias-usuario.md` son **esfuerzo humano clasico** (p. ej. S <= 2 dias, M 3-5, L 1-2 semanas). Si el plan de recursos define la IA como recurso (velocity acelerada por IA), el **esfuerzo real** se comprime: la IA genera el grueso y lo no comprimible es dirigir, revisar y validar (PR, criterios bloqueantes, e2e, accesibilidad). Estima por tanto **dos cifras por unidad** —el bruto humano (referencia) y el real con IA— y planifica con el real.

2. **Asignar "un change = un sprint" por inercia.** Eso rellena sprints sin relacion con la carga. Separa dos decisiones **independientes**:
   - **Duracion del sprint** = se deriva de la **carga real** y de la cadena de dependencias (cuanto trabajo de calendario hay por bloque). Si un bloque son ~3-4 dias de calendario, un sprint de 1 semana lo cubre; uno de 2 dejaria capacidad ociosa.
   - **Numero de sprints/ciclos** = lo imponen los **cortes duros**: gates de validacion (p. ej. validacion del MVP con cliente), hitos externos, dependencias estrictas y aislamiento de unidades de alto riesgo. **No** la suma de tallas.

**Metodo:**

1. Calcula la **carga total real** (suma de esfuerzos reales por unidad) y la **cadena critica** (las unidades dependientes en serie marcan el calendario; 2 personas no paralelizan una cadena secuencial).
2. Fija la **duracion del sprint** para que la carga por sprint llene razonablemente la capacidad declarada. Si el reparto deja un sprint muy por debajo de capacidad, **agrupa unidades o acorta la duracion**; si excede capacidad, abre otro sprint.
3. Fija el **numero de ciclos** por los cortes duros (gates, dependencias, riesgo), no por las tallas. Documenta el motivo de cada corte.
4. Por cada sprint, declara explicitamente **carga real vs capacidad**, para que el dimensionado sea visible y no arbitrario.
5. Si la carga total es muy pequena frente a la ceremonia de sprints, **dilo**: puede bastar un unico sprint con checkpoint intermedio, o un kanban de la cadena de changes. No fuerces multiples sprints solo por formalidad.

> Ejemplo de razonamiento correcto: "el alcance son ~6-8 dias-persona reales con IA; en cadena secuencial son 2 bloques de ~1 semana; hay 2 ciclos porque un gate de validacion con cliente separa F1 de F2, no porque haya 5 changes". Evita el patron inverso: "hay 5 changes, luego 5 sprints".

### 3. Generacion de `docs/sprint-plan.md`

Genera (o actualiza) `docs/sprint-plan.md` con esta estructura:

```markdown
# Plan de sprints — <nombre del proyecto>

> Documento de Planificacion de entrega (AIDD). Generado por `aidd sprint-planning`.
> Fuentes: docs/roadmap.md, docs/planificacion-proyecto.md, docs/detalle-historias-usuario.md.
> Respeta el faseado por contexto del roadmap. Pendiente de aprobacion humana.

## 1. Parametros de planificacion
- Duracion de sprint, capacidad por sprint, fecha de inicio, velocity asumida (acelerada por IA o bruta), **carga total estimada** (real con IA vs bruto humano) y recursos/equipo de referencia.
- Una nota breve justificando por que esa duracion de sprint (carga real) y ese numero de ciclos (cortes duros: gates, dependencias, riesgo).

## 2. Unidades de trabajo
- Tabla: id (change/HU), descripcion breve, fase (F0/F1/F2), **estimacion real con IA y bruto humano de referencia** (S/M/L o puntos), perfil principal.

## 3. Mapa de dependencias y prerequisitos
- Que debe completarse antes de que. Bloqueos tecnicos y de recursos. Marca [BLOQUEANTE].

## 4. Distribucion en sprints
- Por cada sprint: objetivo, unidades incluidas, **carga real agregada vs capacidad** (explicita), asignacion de perfiles y Definition of Done. Comprueba que ninguna unidad va antes que sus prerequisitos y que el sprint ni se sobrecarga ni queda muy por debajo de capacidad.

## 5. Hitos y entregables
- Hitos (p. ej. MVP F1 listo) y que se entrega/valida al final de cada sprint o grupo de sprints.

## 6. Riesgos de planificacion y supuestos
- Riesgos (dependencias, capacidad, incertidumbre de estimacion) y supuestos. Marca [BLOQUEANTE] cuando aplique.

## 7. Decisiones tomadas
- Registro ligero: pregunta, opciones, decision, origen (usuario | default), una linea de justificacion.
```

Reglas de contenido:

- Respeta dependencias y faseado: ninguna unidad antes que sus prerequisitos; F0 antes de F1 antes de F2.
- No sobrecargues un sprint por encima de la capacidad declarada; si no cabe, abre otro sprint y dilo.
- **No infres ni rellenes sprints**: dimensiona a la carga real (paso 2.5). La duracion deriva de la carga; el numero de ciclos, de los cortes duros (gates, dependencias, riesgo). Si un sprint queda muy por debajo de capacidad, agrupa o acorta.
- Planifica con el **esfuerzo real** (comprimido por IA si aplica), no con el bruto S/M/L; muestra ambas cifras para trazabilidad.
- Las unidades son completas (change/historia); no se parten entre sprints.
- La seccion 7 sustituye a la auditoria estructurada e incluye decisiones resueltas por default.

### 4. Volcado opcional a Jira (MCP de Atlassian)

Paso **opcional** y **posterior** a generar `docs/sprint-plan.md`. La fuente de verdad sigue siendo el documento; Jira es un destino. Crea en Jira los **sprints** del plan y las **historias** (unidades de trabajo) asignadas a cada sprint.

**Cuando ofrecerlo.** Al terminar el documento, ofrece volcar el plan a Jira. Ejecuta el volcado solo si el usuario lo confirma. Tambien aplica si el usuario lo pide explicitamente ("crea los sprints en Jira", "vuelcalo a Jira en el proyecto X").

**Prerrequisito — MCP de Atlassian.** Este volcado usa el MCP de Atlassian (Jira). No uses la API REST a mano ni gestiones credenciales desde el skill.

1. Comprueba que hay tools del MCP de Atlassian disponibles (descubrelas con la busqueda de herramientas; los nombres pueden variar entre versiones, p. ej. buscar/crear issue, metadata de tipos de issue del proyecto, proyectos visibles, recursos accesibles). No asumas nombres concretos: localiza las tools por su funcion.
2. Si **no** hay MCP de Atlassian conectado, **no inventes el volcado**: informa de que falta el MCP, deja `docs/sprint-plan.md` como entregable y explica brevemente que hay que conectar el MCP de Atlassian (Jira) para habilitar este paso. No caigas a llamadas REST manuales.

**Datos que necesitas del usuario (preguntar antes de escribir, agrupado).**

- **Proyecto Jira** destino: clave del proyecto (p. ej. `ABC`). Si el usuario solo da el nombre, resuelvelo a su clave con las tools del MCP y confirma.
- **Board Scrum** del proyecto: los sprints de Jira **viven en un board Scrum**, no en el proyecto a secas. Localiza el board del proyecto; si hay varios, pide cual. Si el proyecto es Kanban o no tiene board Scrum, **avisa**: no se pueden crear sprints; ofrece crear solo las historias (sin sprint) o detener.
- **Tipo de issue** para las historias (por defecto `Story`/`Historia`; si el proyecto no lo tiene, usa el equivalente y confirmalo con la metadata del proyecto). Anota tambien el tipo de **sub-tarea** (`Sub-task`/`Subtarea`) porque los changes se crearan despues como sub-tareas de la HU (no aqui).
- **Cuenta de fechas**: usa la fecha de inicio y la duracion de sprint de los parametros de planificacion (seccion 1) para fechar cada sprint en cadena. Confirma la fecha de inicio antes de crear.

**Mapeo plan -> Jira.**

- Cada **sprint** del documento (seccion 4) -> un sprint en el board, con: nombre (p. ej. `Sprint 1 — <objetivo breve>`), objetivo (el objetivo del sprint) y fechas de inicio/fin derivadas de la duracion. No actives (start) los sprints salvo que el usuario lo pida; crealos en estado futuro.
- Cada **HU** (historia de usuario de la seccion 2 que cae en ese sprint) -> una **Story**, con: titulo (id HU + descripcion breve), descripcion (criterios/notas de `docs/detalle-historias-usuario.md` si estan disponibles), y asignacion al sprint correspondiente. Si el board tiene campo de **estimacion/story points**, vuelca el **esfuerzo real con IA** (no el bruto) cuando sea numerico; si la talla es S/M/L, registrala en la descripcion o en una etiqueta.
- **Personas envueltas -> assignee**: si `docs/plan-revision-hu.md` (o `docs/planificacion-proyecto.md`) asocia una persona/perfil responsable a la HU, usala para proponer el **assignee** de la Story. Resuelve el nombre a la cuenta de Jira con las tools del MCP (busqueda de usuario/cuenta) y **confirma con el usuario** antes de asignar; si no hay correspondencia clara, deja la Story sin asignar en lugar de adivinar. Este skill es la antesala de esa planificacion de sprints y personas en Jira.
- **Los changes NO se crean aqui.** En este paso solo se crean las **Stories (HU)** y los **sprints**. Cada change se creara mas tarde como **sub-tarea** de su HU cuando el AI Lead ejecute `native-ai open change` (ver skill `native-ai-specs`, "Integracion con Jira"). Lo que SI haces aqui es **preparar el enlace** (ver "Persistencia del enlace y la configuracion").
- **No crees epicas** en este paso (alcance acordado: sprints + historias/changes-como-subtareas). Si el usuario las pide, mapea fase (F0/F1/F2) -> epica como extension.

**Reglas de seguridad e idempotencia.**

- **Confirma el plan de escritura antes de crear nada**: numero de sprints y de issues, proyecto y board destino. Una linea por sprint con sus issues. Espera el OK.
- **No dupliques**: antes de crear, comprueba si ya existen sprints con el mismo nombre o issues con el mismo titulo en el proyecto/board (busca con las tools del MCP). Si existen, no los recrees; reporta y ofrece omitir o renombrar. Re-ejecutar el volcado no debe duplicar el plan.
- Crea de forma ordenada: primero los sprints (para tener sus ids), luego las issues asignandolas a su sprint.
- Si una creacion falla, **detente y reporta** lo creado hasta el momento (sprints e issues con sus claves), para que el estado sea reconstruible; no sigas a ciegas.
- No cambies el estado del tablero ni muevas issues existentes; este paso solo **anade** el plan.

**Persistencia del enlace y la configuracion.** Para que `native-ai open/implement/close change` puedan crear las sub-tareas y mover los tickets despues, deja preparado el puente:

1. Escribe (o actualiza, sin tocar otras claves) la seccion `jira:` en `openspec/config.yaml` con: `site`, `project_key`, `board_id`, `story_issue_type`, `subtask_issue_type`, `status_in_progress`, `status_done` y `assignee_override` (vacio salvo que el MCP use una cuenta de servicio). Si no existe `openspec/` (proyecto sin OpenSpec), escribe estos mismos datos en una cabecera de `docs/jira-sync.md` y avisa de que la sincronizacion de changes requiere el mundo native-ai-specs.
2. Inicializa/actualiza el registro `docs/jira-sync.md` (fuente de verdad del mapeo HU <-> change <-> issue), una fila por HU, con la clave de la **Story** recien creada y, si el roadmap ya asocia changes a esa HU, la lista de change(s) previstos con su sub-tarea en blanco y estado `to_do`. Estructura:

   | HU | Story (Jira) | change(s) | Sub-tarea(s) (Jira) | estado |
   |----|--------------|-----------|---------------------|--------|
   | HU-03 | ABC-12 | back-auth | (pendiente) | to_do |

3. No crees las sub-tareas de los changes aqui; solo dejas registradas las HU con su Story y los changes previstos. Las sub-tareas las crea `native-ai open change`.

**Salida del volcado.** Tras crear, informa: proyecto y board, sprints creados (nombre + fechas + clave/id), numero de Stories (HU) creadas por sprint y sus claves (p. ej. `ABC-123`), ruta de `docs/jira-sync.md` y de la seccion `jira:` en `openspec/config.yaml`, y cualquier elemento omitido por ya existir. Recuerda que el documento `docs/sprint-plan.md` sigue siendo la fuente de verdad y que el plan esta pendiente de aprobacion humana.

### 5. HU vs change — que se rastrea en Jira

Convencion del enlace entre los dos planos (negocio y ejecucion), que este skill prepara y `native-ai-specs` consume:

- **La HU es la unidad rastreable de entrega** (Story en Jira): es lo que el equipo se compromete a entregar, lo que tiene criterios de aceptacion y lo que el cliente valida. Es estable.
- **El change es la unidad de ejecucion** del AI Developer (sub-tarea de su HU): es como la IA construye la HU, acotado por el presupuesto de contexto del roadmap. Una HU puede necesitar **varios** changes.
- **Enlace**: cada change conoce su(s) HU (anotada en `proposal.md` y en `docs/jira-sync.md`); cada HU conoce sus changes (sus sub-tareas). El pegamento operativo es referenciar la clave de la sub-tarea/Story (`ABC-123`) en el PR del change.
- **Avance**: `implement change` mueve la sub-tarea y su Story a In Progress; `close change` pasa la sub-tarea a Done y la Story a Done **solo cuando todas sus sub-tareas estan Done**. Asi una HU no se marca completada a medias.

### 6. Generacion de la vista HTML (complementaria)

Una vez escrito y confirmado `docs/sprint-plan.md`, genera su **vista HTML** complementaria con el skill `booster-docs`. El `.md` es la fuente de verdad; el HTML es solo para consumo humano.

- Invoca `booster-docs` con `docs/sprint-plan.md` como entrada y salida en `docs/html/sprint-plan.html` (crea `docs/html/` si no existe). El script auto-detecta el tipo de documento (`sprint-plan`) y anade dashboard de KPIs, chips y demas elementos visuales.
- Pasa el flag `--open` para que el HTML **se abra automaticamente en el navegador** al terminar el comando. En modo no interactivo (CI/auto o si el usuario pidio no ser interrumpido) omite `--open` y solo informa de la ruta.
- **Degradacion elegante**: si `booster-docs` no esta disponible, avisa de que la vista HTML no se genero y de que puede instalarse el plugin `boosters`, pero **no bloquees** el comando: el `.md` es suficiente para continuar.
- El HTML es parte de la documentacion del repo (se versiona junto al `.md`); no lo anadas a `.gitignore`.
- No regeneres el HTML si el documento quedo pendiente de cambios: hazlo cuando este estable.
- Nunca modifiques el `.md` de origen al generar el HTML.

## Verificacion final

Al terminar, informa:

- Comando AIDD ejecutado (`aidd sprint-planning`).
- Ruta del documento generado o actualizado (`docs/sprint-plan.md`).
- Ruta de la vista HTML generada (`docs/html/sprint-plan.html`), o aviso si no se pudo generar el HTML.
- Numero de sprints, hito del MVP (F1) y principales dependencias/riesgos de planificacion.
- Si se ejecuto el volcado a Jira: proyecto/board destino, sprints y Stories (HU) creados (con sus claves) y elementos omitidos; rutas del registro `docs/jira-sync.md` y de la seccion `jira:` en `openspec/config.yaml`. Si no se ejecuto, recuerda que es un paso opcional disponible (requiere el MCP de Atlassian).
- Recordatorio del enlace: los changes se crearan como sub-tareas de su HU al ejecutar `native-ai open change`, y `implement`/`close change` moveran los tickets de columna automaticamente.
- Recordatorio: pendiente de **aprobacion humana**.
- Siguiente paso sugerido: ejecutar el desarrollo segun el plan. En la metodologia completa, el AI Lead abre cada change con `native-ai open change` siguiendo el orden de los sprints; el equipo humano usa este plan para su seguimiento Scrum.
