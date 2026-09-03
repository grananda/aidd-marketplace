---
name: aiba-sprint-planning
description: Fase 3.5 (paso 3.5.2) del proceso AIDD-SDD, cubierta por el conjunto AIBA (AI Business Analyst): capa de planificacion de entrega (Delivery). Distribuye el trabajo en sprints una vez que existe el roadmap y el plan de recursos, mediante el comando `aiba sprint-planning` (alias `aiba planificacion sprints`). Actua como planificador de delivery (Scrum) que lee `docs/roadmap.md`, `docs/planificacion-proyecto.md`, `docs/detalle-historias-usuario.md` y, si existe, `docs/plan-revision-hu.md` (antesala: estado de revision de cada HU y personas envueltas, generado por `aiba hu-review-plan`) para no planificar por libre, y genera `docs/sprint-plan.md` con parametros de planificacion, unidades de trabajo con estimacion (esfuerzo real con IA frente al bruto humano XS/S/M/L/XL), mapa de dependencias y prerequisitos, distribucion en sprints con objetivo, capacidad y asignacion de perfiles, hitos, y riesgos de planificacion. Dimensiona la duracion del sprint por la carga real y el numero de ciclos por los gates/dependencias, evitando rellenar sprints sin sentido. Respeta el faseado por contexto del roadmap (no parte un change). Soporta los tres modos de faseado del roadmap. En **`waves`** (oleadas) cada oleada es un tramo cuya duracion es el `max` de sus fases y una frontera de sprint natural, y su ancho frente a `parallel_developers` revela los tramos con gente ociosa. En **`multilane`**: cuando el faseado viene repartido en lineas de trabajo paralelas (`F0` / `F-<lane>-NN` / barreras `FB-NN`), el calendario deja de ser una unica cadena critica y pasa a ser el `max` de las cadenas de cada lane entre barreras; **cada sprint toma unidades de varios lanes a la vez**, la carga vs capacidad se declara **por lane** ademas de agregada, las barreras son fronteras de sprint naturales, y se avisa de los lanes sin asignacion (dev parado) y de las dependencias cross-lane fuera de barrera (conflicto de faseado que resuelve `aisdd roadmap`). Como paso final opcional, vuelca el plan a Jira via el MCP de Atlassian (crea sprints en el board del proyecto indicado y las historias asignadas a cada sprint), siempre con confirmacion humana previa. El volcado se puede ejecutar mas de una vez de forma segura (p. ej. antes del roadmap en modo degradado y de nuevo con el roadmap para re-fasear): las Stories nunca se recrean (se preservan las claves de issue), el re-faseado se hace moviendo las HU entre sprints y limpiando sprints vacios. Skill de planificacion, autonomo del mundo OpenSpec/aisdd-specs y sin auditoria estructurada.
metadata:
  author: NTT DATA Spain GDN-e
  version: "2.1.2"
---

# aiba-sprint-planning (AIBA · Fase 3.5 · paso 3.5.2 · sprints)

Usa este skill cuando el usuario quiera repartir el trabajo en sprints a partir del roadmap y los recursos, o cuando invoque:

- `aiba sprint-planning`
- `aiba planificacion sprints`

Tambien cuando pida "plan de sprints", "distribuir las tareas en sprints", "planificar iteraciones", "sprint plan" o equivalentes.

Responde y documenta en espanol siempre que sea posible. Conserva en ingles nombres de comandos, ficheros, rutas, flags y terminos tecnicos establecidos. Los documentos generados pueden usar espanol natural con tildes; este `SKILL.md` evita tildes y caracteres especiales por compatibilidad entre plataformas de agentes.

## Que es AIBA y donde encaja este skill

AIBA (AI Business Analyst) es el conjunto de skills que da la cara ante el negocio: el diseno funcional que el cliente firma, el plan que aprueba, el calendario que sigue y los KPIs con los que juzga si merecio la pena. Su metodologia esta en `${CLAUDE_PLUGIN_ROOT}/methodology/native-ai-aiba.md` (referencia de solo lectura). La numeracion de fases es la del proceso AIDD-SDD, cuyos documentos AIBA **consume sin modificar**:

- Fase 0 — `aidd client-requirements` (plugin `aidd`).
- Fase 1 — `aidd requirements`, `aidd user-stories`, `aidd user-story-details` (plugin `aidd`).
- Fase 2 — Diseno (AI Architect): `aidd prototype-architecture`, `aidd prototype`, `aidd style-guide`, `aidd architecture-proposal`, `aidd architecture` (plugin `aidd`).
- **Fase 3.5 — Planificacion de entrega (Delivery)** — capa que traduce el diseno y el roadmap a algo que un equipo (humano + agentes) consume directamente:
  - `aiba project-plan` (paso 3.5.1): plan de recursos (`docs/planificacion-proyecto.md`).
  - **`aiba sprint-planning`** (este skill, paso 3.5.2): distribucion del trabajo en sprints (`docs/sprint-plan.md`).

Este conjunto es **autonomo**: puede usarse al margen de `aisdd-specs`, `booster-ux` y `booster-uml`. No depende de OpenSpec ni escribe auditoria estructurada. Las decisiones se registran de forma ligera dentro del propio documento generado.

Como complemento opcional, al final del comando se genera una **vista HTML** del plan de sprints con `booster-docs` (ver el paso final del flujo). El `.md` sigue siendo la **unica fuente de verdad**; el HTML es solo para consumo humano y no altera el flujo si `booster-docs` no esta instalado.

> Relacion con el SDD: el `roadmap` del AI Lead (Fase 3) fasea los changes segun el **presupuesto de contexto** del modelo. Este skill anade la **capa de delivery humana**: agrupa esos changes en sprints con fecha, capacidad y asignacion, para que un equipo Scrum los ejecute. **Respeta el faseado del roadmap**: no parte un change para encajarlo en un sprint; un sprint contiene changes/historias completos.

## Rol y objetivo

Actua con este rol durante todo el comando:

> Actua como planificador de delivery (Scrum / gestion de iteraciones) con criterio tecnico. Tu objetivo es distribuir las unidades de trabajo del roadmap en sprints, respetando dependencias y prerequisitos, ajustando a la capacidad del equipo definido en el plan de recursos, y produciendo un plan que un equipo humano pueda ejecutar. Planificas el CUANDO y en que orden, no el QUE se necesita (eso es `aiba project-plan`).

Criterio de salida del paso: existe `docs/sprint-plan.md` con los sprints definidos (objetivo, unidades de trabajo, estimacion, capacidad y asignacion), las dependencias respetadas y los riesgos de planificacion explicitos, de modo que el trabajo sea ejecutable por fases sin bloqueos ocultos. Lo que no se pueda resolver queda como supuesto.

## Reglas generales

- Trabaja desde la raiz del proyecto del usuario.
- **Entrada principal**: `docs/roadmap.md` (changes/fases ya ordenados por el AI Lead). **Insumo de recursos**: `docs/planificacion-proyecto.md` (equipo, capacidad, perfiles). **Detalle**: `docs/detalle-historias-usuario.md` (estimaciones XS/S/M/L/XL, dependencias, criterios bloqueantes).
- **Insumo de revision de HU (si existe)**: `docs/plan-revision-hu.md` (y su Excel `docs/xlsx/plan-revision-hu.xlsx`), generado por `aiba hu-review-plan`. Es la **antesala** de esta planificacion: recoge el estado de revision de cada HU (cerrada/validada, en revision, bloqueada), su persona/rol y el resultado de las reuniones funcionales (negocio) / tecnicas (TI). **No planifiques por libre**: reconcilia el reparto en sprints con ese plan (ver "Reconciliacion con el plan de revision de HU"). Si no existe, continua solo con roadmap + recursos, pero advierte de que conviene revisar y cerrar las HU antes de comprometerlas en sprint.
- Si falta `docs/roadmap.md`, avisa: el faseado por contexto lo produce el AI Lead con `aisdd roadmap` (Fase 3). Como alternativa degradada, puedes partir del mapa+detalle de historias, pero advierte de que no se respeta el faseado por contexto del modelo.
- Si falta `docs/planificacion-proyecto.md`, avisa y propon ejecutar antes `aiba project-plan`; sin recursos no hay capacidad contra la que planificar. Puedes continuar con supuestos de equipo explicitos si el usuario lo pide.
- Si existen changes de OpenSpec (`openspec/changes/`), usalos como detalle adicional de las unidades de trabajo, pero la unidad de planificacion sigue siendo el change/historia del roadmap.
- **Respeta dependencias y faseado**: F0 (foundation) antes que F1, F1 antes que F2; respeta prerequisitos entre historias (p. ej. una historia que necesita un habilitador tecnico va despues de el). No partas un change entre sprints.
- **Roadmaps en oleadas (`waves`)**: si el roadmap declara modo `waves`, las fases vienen agrupadas en **oleadas** de hasta `parallel_developers` fases ejecutables a la vez. Cada **oleada es una frontera de sprint natural** y su ancho te dice cuanta carga puede correr en paralelo en ese tramo. A diferencia de los lanes, las oleadas **no garantizan** que las fases de una misma oleada sean independientes entre si: planifica con ellas, pero no asumas aislamiento — si dos fases de la misma oleada tocan lo mismo, el riesgo es real y va a la seccion 6.
- **Roadmaps multilane**: si `docs/roadmap.md` declara modo `multilane` (o `openspec/config.yaml` tiene `roadmap.mode: multilane`), el faseado viene repartido en **lanes** — lineas de trabajo paralelas e independientes — con fases `F0`, `F-<lane-id>-NN` y barreras `FB-NN`. Esto cambia el dimensionado de forma sustancial (ver "Dimensionado de sprints"): **un sprint contiene unidades de varios lanes a la vez**, y la capacidad deja de ser una cifra agregada. Si el roadmap no declara lanes, todo lo relativo a lanes de este documento no aplica y planificas como siempre.
- **Las tallas XS/S/M/L/XL son esfuerzo humano clasico, no calendario del sprint**: si el plan de recursos define la IA como recurso (velocity acelerada por IA), estima el **esfuerzo real** comprimido (la IA genera; lo que cuesta es dirigir, revisar y validar) y planifica con el real, no con el bruto.
- **No rellenes sprints**: dimensiona a la carga real (ver "Dimensionado de sprints"). No asignes "un change = un sprint" por inercia ni estires la duracion para cubrir una talla bruta. Un sprint muy por debajo de capacidad es una senal de relleno; agrupa unidades o acorta la duracion.
- No inventes unidades de trabajo nuevas. Distribuyes las que ya existen en roadmap/detalle.
- No sobrescribas un `docs/sprint-plan.md` existente sin avisar: leelo, propon los cambios y confirma.
- Este documento requiere aprobacion humana. Al terminar, deja claro que esta pendiente de revision.
- **El volcado a Jira es opcional y nunca automatico**: la fuente de verdad es `docs/sprint-plan.md`. Solo crea sprints/historias en Jira si el usuario lo confirma e indica el proyecto/board (ver "4. Volcado opcional a Jira"). Crear issues y sprints en Jira es una accion hacia un sistema externo y dificilmente reversible: confirma antes y no la repitas a ciegas.

## Flujo del comando `aiba sprint-planning`

### 1. Recopilacion de contexto (lectura previa)

Lee y consolida: `roadmap.md` (fases/changes, dependencias, riesgo de contexto), `planificacion-proyecto.md` (equipo, perfiles, capacidad), `detalle-historias-usuario.md` (estimaciones XS/S/M/L/XL, dependencias, criterios bloqueantes), `plan-revision-hu.md` **si existe** (estado de revision de cada HU, persona/rol implicada, resultado funcional/tecnico) y, si existen, los changes de OpenSpec.

Construye la lista de **unidades de trabajo** (change o historia) con su estimacion y sus dependencias antes de repartir.

**Detecta el modo del roadmap** (`atomic`, `waves` o `multilane`). Busca en `docs/roadmap.md` la declaracion de modo y las secciones "Oleadas", "Lanes" y "Dependencias cross-lane"; si tienes acceso a `openspec/config.yaml`, la clave `roadmap.mode` es la fuente mas fiable (junto con `roadmap.lanes` y el campo `lane` de cada fase). Anota siempre el **`depends_on`** de cada fase: es el grafo con el que construiras la seccion 3, en cualquier modo. Si el modo es `waves`, anota ademas la **oleada** de cada fase y el `parallel_developers` declarado. Si el modo es `multilane`, anota por cada unidad **a que lane pertenece** y marca las fases `F0` y `FB-NN` como **barreras** (bloquean a todos los lanes): esa clasificacion condiciona todo el dimensionado posterior. Si no hay declaracion de modo, trata el roadmap como `atomic`.

### 1.5 Reconciliacion con el plan de revision de HU

Si existe `docs/plan-revision-hu.md`, este skill **no va por libre**: parte de el. Es la antesala directa del reparto en sprints y del volcado a Jira (sprints + personas envueltas).

- **Estado de la HU manda para comprometer**: solo comprometas en un sprint de desarrollo las HU que la revision haya dejado **cerradas/validadas**. Una HU aun **en revision** o **bloqueada** no entra en un sprint de construccion como comprometida: dejala en el backlog, planificala tras su cierre, o marca su sprint como dependiente del cierre de la revision. Refleja el desfase como riesgo si el objetivo de fecha lo requiere.
- **Personas/perfiles**: reutiliza las personas y perfiles que el plan de revision ya asocia a cada HU (quien la valida con negocio/TI) para informar la **asignacion de perfiles del sprint** y, en el volcado a Jira, el **assignee** de la Story (ver seccion 4). No inventes asignaciones nuevas si el plan de revision ya las implica.
- **Orden coherente**: respeta el orden logico de revision (fases, dependencias, agrupaciones por epica/persona) al secuenciar los sprints; no reordenes en contra del plan de revision sin justificarlo en la seccion de decisiones.
- Si el plan de revision y el roadmap **discrepan** (p. ej. una HU marcada para cerrar en la revision no esta en ningun change del roadmap, o al reves), **senalalo** como riesgo/decision en lugar de resolverlo en silencio.

### 2. Pre-flight de preguntas

Resuelve solo lo imprescindible para distribuir en sprints.

1. Cubre, como minimo: **duracion del sprint**, **capacidad** (nº de personas/perfiles disponibles por sprint, segun el plan de recursos), **fecha de inicio** y **velocity asumida** (si no hay historica, propon una y marcala como supuesto). Para la velocity, pregunta explicitamente si se planifica con **esfuerzo acelerado por IA** o con **esfuerzo bruto humano**, porque cambia el dimensionado por completo (ver "Dimensionado de sprints"). Plantea la **duracion del sprint en funcion de la carga real estimada**, no como dato fijo. **En roadmaps multilane, la capacidad se pregunta por lane** (cuantas personas de cada perfil hay disponibles en cada linea de trabajo): una cifra global no permite detectar ni un lane saturado ni un lane parado. Si el plan de recursos ya lo resuelve, no lo preguntes.
2. Clasifica cada hueco en **bloqueante**, **preferencia** o **confirmacion**.
3. No preguntes lo que roadmap o plan de recursos ya resuelven.
4. Presupuesto de preguntas: maximo **7** por ejecucion. Prioriza bloqueantes y agrupa relacionadas.
5. Formato: si la plataforma soporta preguntas estructuradas (por ejemplo `AskUserQuestion`), usalo con 2-4 opciones y marca una como `(Recomendada)`; si no, lista numerada con opciones y recomendacion.
6. Modo no interactivo: toma el default recomendado para `preferencia` y `confirmacion`; para la duracion del sprint, **no asumas un valor fijo**: derivala de la carga real estimada (un sprint cuya carga llene razonablemente la capacidad), y registrala como supuesto. Deja los `bloqueante` sin default como supuestos en el documento.
7. Si el usuario aplaza una duda, registrala como supuesto y continua.

### 2.5 Dimensionado de sprints: carga real, no relleno

Antes de repartir, dimensiona con criterio. Dos errores frecuentes a evitar:

1. **Tomar las tallas XS/S/M/L/XL como dias de calendario del sprint.** Las tallas de `detalle-historias-usuario.md` son **esfuerzo humano clasico** en dias-persona (1 d = jornada de 8 h): **XS = 0,5 d · S = 1,5 d · M = 3 d · L = 5 d · XL = 8 d**. Si el plan de recursos define la IA como recurso (velocity acelerada por IA), el **esfuerzo real** se comprime: la IA genera el grueso y lo no comprimible es dirigir, revisar y validar (PR, criterios bloqueantes, e2e, accesibilidad). Estima por tanto **dos cifras por unidad** —el bruto humano (referencia) y el real con IA— y planifica con el real.

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

#### Dimensionado con oleadas (roadmap `waves`)

Las oleadas ya traen el trabajo troceado en tramos paralelizables, asi que el metodo es directo:

1. **Cada oleada es un tramo.** Su duracion es `max(esfuerzo real de sus fases)`, no la suma: corren a la vez.
2. **El ancho de la oleada acota el paralelismo real.** Una oleada de ancho 1 es un tramo secuencial aunque haya `N` devs; anotalo, porque ahi sobran `N-1` personas.
3. **Suma los tramos en serie** para el calendario total. Las oleadas no se solapan: la siguiente no arranca hasta que la actual cierra.
4. **Capacidad**: `parallel_developers` es el techo de fases simultaneas. Si una oleada tiene menos fases que devs, hay **holgura**; si tuviera mas, el roadmap esta mal construido (el ancho no puede superar `parallel_developers`) — senalalo en vez de repartirlo tu.
5. **Frontera de sprint**: haz coincidir cortes de sprint con cambios de oleada siempre que la capacidad lo permita.

#### Dimensionado con lanes (roadmap `multilane`)

El metodo anterior asume **una unica cadena critica**: "2 personas no paralelizan una cadena secuencial". Con lanes ese supuesto ya no se sostiene — hay **N cadenas simultaneas**, una por lane, y el calendario deja de ser la cadena critica para ser el **maximo de las cadenas entre barreras**.

**Metodo revisado:**

1. **Agrupa las unidades por lane.** Cada lane tiene su propia secuencia de fases (`F-<lane-id>-NN`), que si es secuencial internamente.
2. **Localiza las barreras**: `F0` al principio y cada `FB-NN`. Trocean el calendario en **tramos**. Dentro de un tramo los lanes corren en paralelo; una barrera los detiene a todos.
3. **Calcula la duracion de cada tramo** como `max(cadena de cada lane en ese tramo)`, no como la suma. Es la diferencia central respecto al metodo atomico: dos lanes de 4 dias en paralelo son 4 dias de calendario, no 8.
4. **Suma los tramos y las barreras** para obtener el calendario total. Las barreras se suman en serie porque bloquean a todos.
5. **Capacidad por lane, no agregada.** Un lane consume la capacidad de **su** perfil asignado; no puedes compensar un lane sobrecargado con la capacidad ociosa de otro, porque los perfiles no son intercambiables (es lo que justificaba el corte de lanes). Declara carga vs capacidad **por lane y por sprint**.
6. **Detecta el lane critico**: el que marca la duracion de cada tramo. Es donde anadir capacidad tiene efecto; en cualquier otro lane, no cambia nada el calendario.
7. **Detecta lanes ociosos**: un lane sin unidades asignadas en un sprint es un **dev parado** — exactamente el problema que el modo multilane pretendia resolver. Ver "6. Riesgos".

**Las barreras son cortes duros.** Encajan directamente en el paso 3 del metodo general (fijar el numero de ciclos por cortes duros): cada `FB-NN` es una frontera de sprint natural, porque detiene todos los lanes igual que lo hace un gate de validacion.

> Ejemplo de razonamiento correcto con lanes: "dos lanes (`api`, `portal`); tramo 1 tras `F0`: `api` acumula 5 d reales y `portal` 3 d, luego el tramo dura ~5 d y el lane critico es `api`; `FB-01` cierra el tramo y abre el siguiente. Sprint 1 = `F0` + tramo 1, con unidades de **ambos** lanes: 5 d/5 d de capacidad en `api`, 3 d/5 d en `portal` — `portal` queda al 60 %, aviso de holgura, no de relleno."
>
> Evita: "un sprint por lane" (serializa lo que era paralelo y anula el modelo), y "carga total 8 d, luego 8 dias de calendario" (suma cadenas que corren a la vez).

### 3. Generacion de `docs/sprint-plan.md`

Genera (o actualiza) `docs/sprint-plan.md` con esta estructura:

```markdown
# Plan de sprints — <nombre del proyecto>

> Documento de Planificacion de entrega (AIBA). Generado por `aiba sprint-planning`.
> Fuentes: docs/roadmap.md, docs/planificacion-proyecto.md, docs/detalle-historias-usuario.md.
> Respeta el faseado por contexto del roadmap.

## 1. Parametros de planificacion
- Duracion de sprint, capacidad por sprint, fecha de inicio, velocity asumida (acelerada por IA o bruta), **carga total estimada** (real con IA vs bruto humano) y recursos/equipo de referencia.
- Una nota breve justificando por que esa duracion de sprint (carga real) y ese numero de ciclos (cortes duros: gates, dependencias, riesgo).
- **Modo del roadmap** (`atomic`, `waves` o `multilane`) y `parallel_developers`, tomados del roadmap. Si es `atomic`, dilo: el plan no reparte trabajo en paralelo.
- **Si el roadmap es `waves`**: numero de oleadas, **ancho de cada una frente a `parallel_developers`** y el calendario por tramos (cada oleada dura `max` de sus fases).
- **Si el roadmap es multilane**: modo `multilane`, lista de lanes con su perfil asignado y su capacidad, y el **calendario por tramos** (`max` de cadenas entre barreras) con el lane critico de cada tramo.

## 2. Unidades de trabajo
- Tabla: id (change/HU), descripcion breve, fase (F0/F1/F2, o F0/F-<lane>-NN/FB-NN si es multilane), **oleada** (si el modo es `waves`), **lane** (si es `multilane`; vacio en F0 y barreras), **depende de** (fases previas, de `depends_on`), **estimacion real con IA y bruto humano de referencia** (XS/S/M/L/XL o puntos), perfil principal.
- En multilane el **perfil principal se deriva del lane** (cada lane tiene un perfil asignado en el roadmap); no lo asignes unidad a unidad por tu cuenta. Si una unidad necesitase un perfil distinto al de su lane, es sintoma de mal corte: registralo en riesgos.

## 3. Mapa de dependencias y prerequisitos
- Que debe completarse antes de que. Bloqueos tecnicos y de recursos. Marca [BLOQUEANTE].
- Toma el grafo de `depends_on` del roadmap como fuente: no reconstruyas las dependencias por tu cuenta ni las contradigas en silencio.
- **Si es multilane**, separa en dos listas: **intra-lane** (secuencia normal dentro de una linea) y **cross-lane**. Toda dependencia cross-lane deberia estar resuelta por una barrera `FB-NN`; si aparece una **fuera de barrera**, marcala `[CONFLICTO DE FASEADO]` con el lane bloqueado y el tiempo muerto que implica, y remite a re-ejecutar `aisdd roadmap`. No la resuelvas reordenando sprints por tu cuenta: es el mismo criterio que ya aplicas con los conflictos roadmap<->sprint.

## 4. Distribucion en sprints
- Por cada sprint: objetivo, unidades incluidas, **carga real agregada vs capacidad** (explicita), asignacion de perfiles y Definition of Done. Comprueba que ninguna unidad va antes que sus prerequisitos y que el sprint ni se sobrecarga ni queda muy por debajo de capacidad.
- **Si es `waves`**: cada sprint cubre una o varias oleadas completas; declara por oleada su **ancho vs `parallel_developers`** y no partas una oleada entre sprints salvo que la capacidad obligue (y entonces dilo).
- **Si es multilane**: cada sprint incluye unidades de **varios lanes a la vez** — es el objetivo del modelo, no un defecto. Declara **carga real vs capacidad por lane**, no solo el agregado: una cifra global oculta que un lane va al 100 % y otro al 30 %. Anade una tabla `lane | unidades | carga real | capacidad | % ocupacion`. Marca las barreras como sprints propios o como frontera entre sprints, e indica explicitamente que **detienen todos los lanes**.

## 5. Hitos y entregables
- Hitos (p. ej. MVP F1 listo) y que se entrega/valida al final de cada sprint o grupo de sprints.

## 6. Riesgos de planificacion y supuestos
- Riesgos (dependencias, capacidad, incertidumbre de estimacion) y supuestos. Marca [BLOQUEANTE] cuando aplique.
- **Si es `waves`**, anade: **oleada de ancho 1** con varios devs disponibles (personas ociosas en ese tramo) y **fases de la misma oleada que tocan la misma area** (el modo `waves` no lo impide ni lo detecta; si lo ves al leer el roadmap, es un riesgo real de colision).
- **Si hay dependencias cross-lane declaradas**, anade: **lane bloqueado esperando a otro** — indica cuanto tiempo y que hace mientras; si no tiene nada que hacer, es un dev parado y hay que reordenar sus fases.
- **Si es multilane**, anade estos riesgos especificos: **lane sin unidades asignadas en un sprint** (= dev parado, el problema que el modo multilane venia a resolver; propon adelantar trabajo de ese lane o reducir su dedicacion en ese sprint), **lane critico saturado** (marca el calendario: es donde anadir capacidad tiene efecto), y **dependencia cross-lane fuera de barrera** (arrastrada de la seccion 3).

## 7. Decisiones tomadas
- Registro ligero: pregunta, opciones, decision, origen (usuario | default), una linea de justificacion.
```

Reglas de contenido:

- Respeta dependencias y faseado: ninguna unidad antes que sus prerequisitos; F0 antes de F1 antes de F2.
- No sobrecargues un sprint por encima de la capacidad declarada; si no cabe, abre otro sprint y dilo.
- **No infres ni rellenes sprints**: dimensiona a la carga real (paso 2.5). La duracion deriva de la carga; el numero de ciclos, de los cortes duros (gates, dependencias, riesgo). Si un sprint queda muy por debajo de capacidad, agrupa o acorta.
- Planifica con el **esfuerzo real** (comprimido por IA si aplica), no con el bruto XS/S/M/L/XL; muestra ambas cifras para trazabilidad.
- Las unidades son completas (change/historia); no se parten entre sprints. **Esto no cambia con lanes**: lo que se paraleliza son lanes, no el interior de un change.
- **Multilane**: no dediques un sprint a un solo lane salvo que las dependencias lo obliguen — serializa lo que era paralelo. Y no compenses la sobrecarga de un lane con la holgura de otro: los perfiles no son intercambiables, que es justo lo que justificaba separarlos.
- La seccion 7 sustituye a la auditoria estructurada e incluye decisiones resueltas por default.

### 4. Volcado opcional a Jira (MCP de Atlassian)

Paso **opcional** y **posterior** a generar `docs/sprint-plan.md`. La fuente de verdad sigue siendo el documento; Jira es un destino. Crea en Jira los **sprints** del plan y las **historias** (unidades de trabajo) asignadas a cada sprint.

**Se puede volcar mas de una vez de forma segura.** El caso previsto es ejecutarlo **antes** del roadmap (modo degradado, faseando por el mapa+detalle de HU) para arrancar, y **de nuevo despues** con `docs/roadmap.md` para re-fasear por presupuesto de contexto. La re-ejecucion **no rompe la numeracion de issues**: las Stories (HU) nunca se recrean, solo se mueven de sprint. Ver "Re-ejecucion y re-faseado (antes/despues del roadmap)" mas abajo.

**Cuando ofrecerlo.** Al terminar el documento, ofrece volcar el plan a Jira. Ejecuta el volcado solo si el usuario lo confirma. Tambien aplica si el usuario lo pide explicitamente ("crea los sprints en Jira", "vuelcalo a Jira en el proyecto X").

**Prerrequisito — MCP de Atlassian.** Este volcado usa el MCP de Atlassian (Jira). No uses la API REST a mano ni gestiones credenciales desde el skill.

1. Comprueba que hay tools del MCP de Atlassian disponibles (descubrelas con la busqueda de herramientas; los nombres pueden variar entre versiones, p. ej. buscar/crear issue, metadata de tipos de issue del proyecto, proyectos visibles, recursos accesibles). No asumas nombres concretos: localiza las tools por su funcion.
2. **Verifica que el MCP expone las operaciones Agile de sprints** (crear sprint, anadir issues a un sprint, listar sprints del board). Ojo: el **MCP remoto oficial de Atlassian no las expone** — cubre issues y transiciones pero no sprints; hace falta un MCP con la API Agile (p. ej. el `mcp-atlassian` de la comunidad). Si el MCP conectado **no** tiene tools de sprint, avisa de la limitacion y ofrece dos salidas: (a) volcado **degradado** creando solo las Stories (sin asignarlas a sprint, para asignarlas a mano o tras instalar el MCP adecuado), o (b) detener el volcado hasta conectar un MCP con soporte Agile. Nunca simules la asignacion a sprint.
3. Si **no** hay MCP de Atlassian conectado, **no inventes el volcado**: informa de que falta el MCP, deja `docs/sprint-plan.md` como entregable y explica brevemente que hay que conectar el MCP de Atlassian (Jira) para habilitar este paso. No caigas a llamadas REST manuales.

**Datos que necesitas del usuario (preguntar antes de escribir, agrupado).**

- **Proyecto Jira** destino: clave del proyecto (p. ej. `ABC`). Si el usuario solo da el nombre, resuelvelo a su clave con las tools del MCP y confirma.
- **Board Scrum** del proyecto: los sprints de Jira **viven en un board Scrum**, no en el proyecto a secas. Localiza el board del proyecto; si hay varios, pide cual. Si el proyecto es Kanban o no tiene board Scrum, **avisa**: no se pueden crear sprints; ofrece crear solo las historias (sin sprint) o detener.
- **Tipo de issue** para las historias (por defecto `Story`/`Historia`; si el proyecto no lo tiene, usa el equivalente y confirmalo con la metadata del proyecto). Anota tambien el tipo de **sub-tarea** (`Sub-task`/`Subtarea`) porque los changes se crearan despues como sub-tareas de la HU (no aqui).
- **Cuenta de fechas**: usa la fecha de inicio y la duracion de sprint de los parametros de planificacion (seccion 1) para fechar cada sprint en cadena. Confirma la fecha de inicio antes de crear.

**Mapeo plan -> Jira.**

- Cada **sprint** del documento (seccion 4) -> un sprint en el board, con: nombre (p. ej. `Sprint 1 — <objetivo breve>`), objetivo (el objetivo del sprint) y fechas de inicio/fin derivadas de la duracion. No actives (start) los sprints salvo que el usuario lo pida; crealos en estado futuro.
- Cada **HU** (historia de usuario de la seccion 2 que cae en ese sprint) -> una **Story**, con: titulo (id HU + descripcion breve), descripcion (criterios/notas de `docs/detalle-historias-usuario.md` si estan disponibles), y asignacion al sprint correspondiente. Si el board tiene campo de **estimacion/story points**, vuelca el **esfuerzo real con IA** (no el bruto) cuando sea numerico; si la talla es XS/S/M/L/XL, registrala en la descripcion o en una etiqueta.
- **Personas envueltas -> assignee**: si `docs/plan-revision-hu.md` (o `docs/planificacion-proyecto.md`) asocia una persona/perfil responsable a la HU, usala para proponer el **assignee** de la Story. Resuelve el nombre a la cuenta de Jira con las tools del MCP (busqueda de usuario/cuenta) y **confirma con el usuario** antes de asignar; si no hay correspondencia clara, deja la Story sin asignar en lugar de adivinar. Este skill es la antesala de esa planificacion de sprints y personas en Jira.
- **Los changes NO se crean aqui.** En este paso solo se crean las **Stories (HU)** y los **sprints**. Cada change se creara mas tarde como **sub-tarea** de su HU cuando el AI Lead ejecute `aisdd open change` (ver skill `aisdd-specs`, "Integracion con Jira"). Lo que SI haces aqui es **preparar el enlace** (ver "Persistencia del enlace y la configuracion").
- **No crees epicas** en este paso (alcance acordado: sprints + historias/changes-como-subtareas). Si el usuario las pide, mapea fase (F0/F1/F2) -> epica como extension.
- **Lanes -> etiqueta (label)**: si el roadmap es `multilane`, anade el `lane-id` como **etiqueta** de cada Story, para que el board se pueda filtrar por linea de trabajo. Eso es todo: **no crees un board por lane, ni epicas por lane, ni cambies el modelo HU<->Story<->sub-tarea**. Una Story sigue siendo una HU. Si el proyecto no admite etiquetas o falla al escribirlas, avisa y continua: la etiqueta es informativa, no estructural.

**Reglas de seguridad e idempotencia.**

- **Confirma el plan de escritura antes de crear nada**: numero de sprints y de issues, proyecto y board destino. Una linea por sprint con sus issues. Espera el OK.
- **No dupliques**: antes de crear, comprueba si ya existen sprints con el mismo nombre o issues con el mismo titulo en el proyecto/board (busca con las tools del MCP). Si existen, no los recrees; reporta y ofrece omitir o renombrar. Re-ejecutar el volcado no debe duplicar el plan.
- Crea de forma ordenada: primero los sprints (para tener sus ids), luego las issues asignandolas a su sprint.
- Si una creacion falla, **detente y reporta** lo creado hasta el momento (sprints e issues con sus claves), para que el estado sea reconstruible; no sigas a ciegas.
- **Primer volcado**: solo **anade** (crea sprints + Stories); no cambies el estado del tablero. **Re-ejecucion (re-faseado)**: puedes **mover** Stories existentes de un sprint a otro y crear/limpiar sprints, pero **nunca borrar ni recrear una Story** (ver "Re-ejecucion y re-faseado"). No cambies el estado (workflow) de los issues en ningun caso.

**Re-ejecucion y re-faseado (antes/despues del roadmap).** Este volcado esta pensado para ejecutarse **mas de una vez** sin romper el board — tipicamente una primera vez en **modo degradado** (sin roadmap) y otra **con el roadmap** para re-fasear. La regla de oro: **nunca tocar las claves de issue.**

- **Las Stories (HU) son estables: se crean una sola vez y NO se recrean jamas.** En cada re-ejecucion, localiza la Story existente por su clave en `docs/jira-sync.md` (o, si falta, por id de HU / titulo) y **reutilizala**. Recrear una Story quemaria su clave `ABC-123` (Jira **no reutiliza** numeros) y dejaria huecos en la secuencia: no lo hagas nunca.
- **Re-fasear = MOVER, no recrear.** Si el nuevo plan cambia a que sprint pertenece una HU, **mueve** la Story a su nuevo sprint (cambia su campo Sprint via MCP); su clave queda intacta. Nunca la borres para recrearla en otro sitio.
- **Sprints: crea los nuevos y ofrece limpiar los vacios.** Crea solo los sprints que falten. Los que queden **vacios** tras mover las HU son obsoletos; **ofrece borrarlos** (con confirmacion). Borrar un sprint es **seguro para la numeracion**: un sprint es un contenedor **sin issue-key**, a diferencia de un issue.
- **Distincion clave:** issue != sprint. Los issues queman numeros permanentes; los sprints no. Por eso el re-faseado se hace con **mover HU + gestionar sprints**, jamas con borrar/recrear issues.
- **Confirmacion previa:** antes de mover Stories o borrar sprints, muestra el **plan de reconciliacion** (que HU se mueven y a que sprint, que sprints se crean, cuales se borran por quedar vacios) y espera el OK. En modo no interactivo: crea y mueve, pero **no borres** sprints; reporta los vacios para revision manual.
- Tras reconciliar, **actualiza `docs/jira-sync.md`** con el nuevo mapeo HU <-> sprint (conservando las claves de Story ya existentes).

**Persistencia del enlace y la configuracion.** Para que `aisdd open/implement/close change` puedan crear las sub-tareas y mover los tickets despues, deja preparado el puente:

1. Escribe (o actualiza, sin tocar otras claves) la seccion `jira:` en `openspec/config.yaml` con: `site`, `project_key`, `board_id`, `story_issue_type`, `subtask_issue_type`, `status_in_progress`, `status_done` y `assignee_override` (vacio salvo que el MCP use una cuenta de servicio). **Los issue types se descubren, no se asumen**: lee los tipos reales del proyecto via MCP y usa sus nombres exactos — el de Story tal como exista y como `subtask_issue_type` el tipo con `subtask: true` (en proyectos *team-managed* se llama `Subtask`; en *company-managed*, `Sub-task`). Si no existe `openspec/` (proyecto sin OpenSpec), escribe estos mismos datos en una cabecera de `docs/jira-sync.md` y avisa de que la sincronizacion de changes requiere el mundo aisdd-specs.
2. Inicializa/actualiza el registro `docs/jira-sync.md` (fuente de verdad del mapeo HU <-> change <-> issue), una fila por HU, con la clave de la **Story** recien creada y, si el roadmap ya asocia changes a esa HU, la lista de change(s) previstos y estado `to_do`. La columna de sub-tareas solo aplica a HU repartidas entre **2+ changes** (modelo hibrido de `aisdd-specs`); para HU de un solo change queda `—`. Estructura:

   | HU | Story (Jira) | change(s) | Sub-tarea(s) (Jira) | estado |
   |----|--------------|-----------|---------------------|--------|
   | HU-02 | ABC-11 | foundation | — | to_do |
   | HU-03 | ABC-12 | back-auth, front-auth | (pendientes) | to_do |

3. No crees las sub-tareas de los changes aqui; solo dejas registradas las HU con su Story y los changes previstos. Las sub-tareas las crea `aisdd open change`.

**Criterio de completitud del volcado (obligatorio).** El volcado **no** esta terminado cuando las Stories existen en Jira: esta terminado cuando **ademas** (1) `docs/jira-sync.md` esta escrito con el mapeo HU -> clave de Story y (2) la seccion `jira:` esta persistida (en `openspec/config.yaml` o, sin `openspec/`, en la cabecera del propio registro). **Verifica releyendo ambos** antes de informar del resultado; no reportes el volcado como completado sin ellos. Si se omiten, el enlace se pierde y la integracion Jira de `aisdd open/implement/close change` se saltara la sincronizacion — un fallo silencioso que solo se descubre tarde. Si al ejecutar detectas un volcado **previo** sin registro (Stories ya en el board pero sin `docs/jira-sync.md`), no las recrees jamas: reconstruye el registro leyendo las Stories desde Jira y confirmando el mapeo HU <-> clave con el humano (el skill `aisdd-specs` documenta este mismo procedimiento bajo "Reconstruccion del enlace perdido", si tienes instalado el plugin `aisdd`).

**Salida del volcado.** Tras crear, informa: proyecto y board, sprints creados (nombre + fechas + clave/id), numero de Stories (HU) creadas por sprint y sus claves (p. ej. `ABC-123`), ruta de `docs/jira-sync.md` y de la seccion `jira:` en `openspec/config.yaml` **confirmando que ambos quedaron escritos** (son parte del criterio de completitud, no un extra), y cualquier elemento omitido por ya existir. Recuerda que el documento `docs/sprint-plan.md` sigue siendo la fuente de verdad y que el plan esta pendiente de aprobacion humana.

### 5. HU vs change — que se rastrea en Jira

Convencion del enlace entre los dos planos (negocio y ejecucion), que este skill prepara y `aisdd-specs` consume:

- **La HU es la unidad rastreable de entrega** (Story en Jira): es lo que el equipo se compromete a entregar, lo que tiene criterios de aceptacion y lo que el cliente valida. Es estable.
- **El change es la unidad de ejecucion** del AI Developer: es como la IA construye la HU, acotado por el presupuesto de contexto del roadmap. Una HU puede necesitar **varios** changes.
- **Modelo hibrido por HU** (lo aplica `aisdd-specs`): si una HU se realiza con **un solo change**, los comandos operan **directamente sobre su Story** (sin sub-tarea — una sub-tarea 1:1 solo duplicaria la Story); si la HU se reparte entre **2 o mas changes**, cada change es una **sub-tarea** bajo su Story para progreso atomico.
- **Enlace**: cada change conoce su(s) HU (anotada en `proposal.md` y en `docs/jira-sync.md`); cada HU conoce sus changes. El pegamento operativo es referenciar la clave de la Story/sub-tarea (`ABC-123`) en el PR del change.
- **Avance**: `implement change` mueve a In Progress las Stories de **todas** las HU que implementa (y la sub-tarea del change donde exista); `close change` las pasa a Done — una Story con sub-tareas, **solo cuando todas estan Done**. Asi una HU no se marca completada a medias.

### Sello de version y fecha-hora (antes de renderizar)

Tras escribir o actualizar `docs/sprint-plan.md`, y **antes** de generar la vista HTML, sella el documento:

> **Antes de ejecutar cualquiera de estos scripts, comprueba que la ruta resuelve.** `${CLAUDE_PLUGIN_ROOT}` la define Claude Code; **otros agentes la dejan vacia**, y entonces la orden se convierte en `/skills/...` y falla con `No such file or directory`. Si eso pasa, el script **sigue estando en el disco**: localizalo una vez con `find` --por ejemplo en `~/.claude/plugins` o en el directorio de plugins del agente que uses--, quedate con la **ruta absoluta** y usala en todas las invocaciones de esta sesion. Si no aparece, aplica la degradacion descrita mas abajo: haz el trabajo segun la prosa y dilo. **Nunca des por hecho que se ejecuto un script que no ejecutaste.**

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/stamp_doc.py" --input docs/sprint-plan.md --gated
```

Anade/actualiza la cabecera `> **Version N** - **Generado:** fecha hora`, **incrementa la version en cada regeneracion** (via `docs/.aidd-doc-meta.json`) y usa la **fecha y hora reales**. No inventes la version ni la hora: las pone el script y esa linea no se edita a mano. Si Python no esta disponible, avisa pero no bloquees.

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

- Comando AIBA ejecutado (`aiba sprint-planning`).
- Ruta del documento generado o actualizado (`docs/sprint-plan.md`).
- Ruta de la vista HTML generada (`docs/html/sprint-plan.html`), o aviso si no se pudo generar el HTML.
- Numero de sprints, hito del MVP (F1) y principales dependencias/riesgos de planificacion.
- Si se ejecuto el volcado a Jira: proyecto/board destino, sprints y Stories (HU) creados (con sus claves) y elementos omitidos; rutas del registro `docs/jira-sync.md` y de la seccion `jira:` en `openspec/config.yaml`. Si no se ejecuto, recuerda que es un paso opcional disponible (requiere el MCP de Atlassian).
- Recordatorio del enlace: los changes se crearan como sub-tareas de su HU al ejecutar `aisdd open change`, y `implement`/`close change` moveran los tickets de columna automaticamente.
- Recordatorio: pendiente de **aprobacion humana**.
- Siguiente paso sugerido: ejecutar el desarrollo segun el plan. En la metodologia completa, el AI Lead abre cada change con `aisdd open change` siguiendo el orden de los sprints; el equipo humano usa este plan para su seguimiento Scrum.
- **Para seguir el avance una vez arrancado**: `aiba status-report`. Este plan es su referencia del **avance previsto**, y el informe lo contrasta con el real medido sobre los changes cerrados.
- **Como se aprueba**: `python "${CLAUDE_PLUGIN_ROOT}/scripts/stamp_doc.py" --input <documento> --approve "<nombre>"`. Anota la version actual como aprobada, y a partir de ahi el sello distingue tres estados: sin aprobar, aprobada, y **cambiada despues de aprobarse** — que es el que importa.
