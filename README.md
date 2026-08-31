# AIDD + AISDD + AIBA + AIAD — Marketplace de skills para Claude Code

Marketplace de plugins para instalar los conjuntos **AIDD** (AI Driven Development — definición y diseño asistidos por IA), **AISDD** (AI Spec-Driven Development sobre OpenSpec; *fork mantenido del antiguo `sdd`*), **AIBA** (AI Business Analyst — análisis funcional, entrega y medición) y **AIAD** (AI-Augmented Development — ejecución human-first *ia-in-the-loop*) desde cualquier instancia de Claude Code.

- Repositorio: `grananda/aidd-marketplace` — **privado**.
- Nombre del marketplace: `aidd-sdd`.

## Plugins del marketplace

| Plugin | Contenido | Para qué sirve |
|--------|-----------|----------------|
| `aidd` | 9 skills `aidd-*` (Fases 0, 1 y 2) + metodología | Capturar requisitos del cliente, formalizarlos, definir y detallar las historias de usuario, y diseñar la arquitectura y la guía de estilos. Es el «qué se construye». |
| `aisdd` | `aisdd-specs` + `aisdd-amend` + metodología | Ejecutar con OpenSpec: onboarding de proyectos existentes con specs base, roadmap (consciente del sprint-plan, con **tres modos de paralelismo**) y ciclo open/implement/close change, pre-flight de dudas configurable, auditoría e integración Jira. Comandos `aisdd …` (alias legacy `native-ai …`). *Fork mantenido del antiguo `sdd`.* |
| `boosters` | `booster-ux`, `booster-uml`, `booster-docs` | Generar prototipos UX, diagramas UML y vistas HTML de los documentos de planificación. **Lo usan `aidd`, `aisdd` y `aiba`.** |
| `aiba` | 5 skills `aiba-*` (negocio, entrega y medición) + metodología propia | **AI Business Analyst**: la capa que da la cara ante el negocio. Diseño funcional en Word por historia, plan de revisión de HU con negocio y TI, plan de recursos, plan de sprints con volcado opcional a Jira, y KPIs **medidos** del uso de IA. Autónomo de OpenSpec. |
| `aiad` | 11 skills `aiad-*` + hook de bitácora + subagente de review + metodología | **Ejecución human-first (*ia-in-the-loop*)**: tú escribes el código y la IA te aumenta a demanda. **Independiente y opcional**; alternativa a `aisdd` para la fase de ejecución. |

## Índice de comandos por skill y fase

Todos los comandos, ordenados por fase del método. Cada comando activa su skill; también se puede invocar namespaced (`/aidd:<skill>`, `/aisdd:aisdd-specs`, `/boosters:<skill>`, `/aiad:<skill>`) o por lenguaje natural.

### `aidd` — Definición y Diseño (plugin `aidd`, 9 comandos)

| Fase | Comando | Skill | Genera |
|------|---------|-------|--------|
| 0 | `aidd client-requirements` | `aidd-client-requirements` | `docs/cliente-requisitos.md` (brief del cliente) |
| 1.1 | `aidd requirements` | `aidd-requirements` | `docs/requisitos.md` (RF/NFR, restricciones) |
| 1.2 | `aidd user-stories` `[fases=N\|fases>=N]` | `aidd-user-stories` | `docs/mapa-historias-usuario.md` (mapa por fases; F0 = habilitadores) |
| 1.3 | `aidd user-story-details` | `aidd-user-story-details` | `docs/detalle-historias-usuario.md` (criterios de aceptación) |
| 2.1 | `aidd prototype-architecture` | `aidd-prototype-architecture` | `docs/arquitectura-base-prototipo.md` |
| 2.2 | `aidd prototype` | `aidd-prototype` | Prototipo mockeado (redirige a `booster-ux`) |
| 2.3 | `aidd style-guide` | `aidd-style-guide` | `docs/guia-estilos.md` (design tokens) |
| 2.3 | `aidd architecture-proposal` | `aidd-architecture-proposal` | `docs/propuesta-arquitectura-base.md` |
| 2.4 | `aidd architecture` | `aidd-architecture` | `docs/arquitectura-base.md` (arquitectura definitiva) |


### `aisdd` — Inicialización, Roadmap y Ejecución (plugin `aisdd`, 9 comandos, skills `aisdd-specs` y `aisdd-amend`)

> Comandos primarios `aisdd …`; los `native-ai …` siguen funcionando como **alias legacy**. Antes se llamaba plugin `sdd`.

| Fase | Comando | Rol | Genera / hace |
|------|---------|-----|---------------|
| 3.1 | `aisdd init` | AI Lead | Inicializa OpenSpec + `AGENTS.md` + `openspec/config.yaml` (registra diseño **y capa de entrega**). En **proyecto existente**, siembra además las **specs base** en `openspec/specs/` a partir del código |
| 3.3 | `aisdd roadmap` | AI Lead | `docs/roadmap.md` + `docs/prompts-roadmap-native-ai.md` + sección `roadmap` en `config.yaml` + bloque en `AGENTS.md` (fasea por contexto, **alineado al `sprint-plan.md`** si existe, y elige **modo de paralelismo**: `atomic`, `waves` o `multilane`) |
| 4 | `aisdd open change [what-you-want-to-build]` | AI Lead | Pre-flight + genera specs validados (`proposal.md`, `design.md`, `spec.md`, `decisions.md`). El 1.º siempre es `foundation` (scaffolding). En `multilane`, **un change abierto por lane** |
| 4 | `aisdd implement change [change-slug]` | AI Developer | Pre-flight + implementa el código del change |
| 4 | `aisdd amend change [descripción]` | Developer / Lead | Incorpora una modificación a un change **ya abierto** y ejecuta **solo ese delta**, sin re-aplicar el change (skill `aisdd-amend`) |
| 4 | `aisdd close change [change-slug]` | Outcome Validator | Valida y archiva el change |
| 4 | `aisdd lane [list \| switch \| status]` | AI Developer / AI Lead | Selecciona la **línea de trabajo activa** (solo roadmaps `multilane`), como `git switch` con las ramas |
| 2 / 4 (aux) | `aisdd prototype-ux [change-slug]` | Architect / Developer | Prototipos UX del change (invoca `booster-ux`) |
| aux | `aisdd uml [change-slug]` | Cualquiera | Diagramas UML del change en HTML (invoca `booster-uml`) |

#### Cómo paralelizar el trabajo (tres modos)

Por defecto el ciclo **plantea** un solo hilo: un change abierto a la vez. Es una convención del faseado, no un guard — fuera de `multilane` nada comprueba cuántos changes hay abiertos. Con varios developers eso deja a casi todos esperando, así que `aisdd roadmap` pregunta cuántos trabajan en paralelo y ofrece dos formas de repartir. **No compiten: son ejes perpendiculares.**

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
| `atomic` | Nada | **Por convención**, no verificada | Un dev, o sin base para separar. **Default** |
| `waves` (oleadas) | Hasta `N` fases a la vez, respetando dependencias | **Ninguna** — ordena, no protege | Varios devs sin superficies declarables |
| `multilane` (lanes) | `N` líneas persistentes, un change **por lane** | Declarada y **verificada** al cerrar | Módulos con rutas de código disjuntas |

Los dos llegan al **mismo calendario**; lo que cambia es si hay red debajo. En `multilane`, `aisdd close change` comprueba que el change no escribió fuera de las rutas de su lane, y una corrección que toca el contrato compartido para a los lanes hermanos en vez de resolverse en silencio.

**Regla rápida:**

- Roadmap ya diseñado y validado que no quieres alterar → **`waves` anotado** (se añade sin re-fasear: conserva nombres de fase, así que no rompe el enlace con el sprint-plan ni con Jira).
- Proyecto con módulos de rutas separadas y varios devs → **`multilane`**.
- Un solo dev, o sin base para separar superficies → **`atomic`**.

Detalle completo, con un ejemplo del mismo proyecto faseado en los tres modos y sus calendarios reales, en **§3.bis** de `plugins/aisdd/methodology/native-ai-aidd-sdd.md` (y su `.html` hermano).

#### Arrancar sobre un proyecto que ya existe

`aisdd init` pregunta si el desarrollo es nuevo o ya está en marcha. Si está en marcha, analiza el código y la documentación y **siembra las specs base** en `openspec/specs/<capability>/spec.md`: una fotografía del comportamiento **actual real**, no del ideal.

Sin esa línea base, el primer `open change` no puede saber qué existe ya y acaba especificando de cero lo que el código lleva meses haciendo.

- Lo que no se puede inferir con certeza se marca **`UNKNOWN`** — es la salida honesta, no un fallo.
- Lo que no sigue buenas prácticas se marca **`LEGACY`**: es deuda técnica identificada, e insumo directo del roadmap.
- Cuando el código y la documentación discrepan, **manda el código**.
- Antes de escribir nada se acuerda el **alcance** y se propone la **lista de capacidades** para que la confirmes. No sobrescribe specs que ya existan.

A partir de ahí el flujo es el normal: `aisdd roadmap` para fasear lo pendiente y el ciclo de changes aplicando **deltas sobre esas specs base**.

#### Cada comando te dice cuál es el siguiente

El ciclo de `aisdd` no es una secuencia fija: qué toca ahora depende del modo, de qué changes hay vivos, de si queda una barrera bloqueada y de si existe capa de entrega. Por eso **cada comando cierra con el siguiente paso ya resuelto**, listo para copiar — no «considera implementar el change», sino `aisdd implement change portal-catalogo`.

Donde más se nota es en los dos empalmes que no son obvios:

- **Tras `aisdd roadmap`**, hacia la capa de entrega: `aiba project-plan` si aún no hay plan de recursos, `aiba sprint-planning` cuando ya lo hay — y si el `sprint-plan.md` es anterior a este roadmap, avisa de que quedó desalineado y de que re-ejecutarlo es seguro.
- **Tras `aisdd close change`**, hacia la siguiente fase: con `multilane` incluye el `aisdd lane switch` previo si la fase es de otro lane, y si lo que toca es una barrera te dice si ya se desbloqueó o qué lanes faltan por cerrar.

Cuando el roadmap se agota, lo dice y sugiere `aiba metrics`.

#### El sistema calcula el óptimo y te lo enseña

Elegir modo y número de developers a ciegas es elegir mal: la diferencia entre `waves` con 2 devs y `multilane` con 3 puede ser de semanas, y no se ve mirando una lista de fases.

`aisdd roadmap` **te pregunta primero** qué modo elegirías tú. Después, ya con las fases diseñadas y sus dependencias, calcula el calendario de cada modo con cada número de devs y genera `docs/html/faseado-comparativa.html`: **tu camino y el óptimo, uno al lado del otro**, a la misma escala de tiempo, con las barreras marcadas. Si el óptimo necesita más gente de la que hay, lo dice con el coste en días — es el argumento de negocio para pedir equipo.

El orden importa. Se pregunta antes de calcular, porque proponer el óptimo primero convertiría la comparativa en una recomendación con una alternativa de adorno.

Dos cifras que el diagrama pone delante:

- **El camino crítico** — la cadena de dependencias más larga. Ningún reparto baja de ahí. Cuando un camino la toca, añadir gente ya no compra calendario.
- **Las fases sin proteger** — fuera de `multilane`, las que tocan contrato o esquema corren sin barrera. Un camino más corto con esas barras es más rápido *y* más frágil, y el calendario solo no lo cuenta.

**Con el proyecto ya en marcha** funciona igual, pero comparando el calendario **restante**: entra un developer nuevo, o el ritmo no da y quieres replantear el modo. Las fases ya cerradas se congelan —conservan su identificador y su enlace con Jira— y solo se re-fasean las pendientes; las que están en vuelo quedan ancladas a su dev, porque un change abierto no se mueve de línea a mitad. En el diagrama aparecen las tres: lo hecho en una banda antes de *hoy*, lo en curso marcado como no reasignable, y lo pendiente ya repartido según la estrategia nueva.

Ahí la respuesta más útil suele ser la que menos gusta: si el calendario restante ya toca el camino crítico, el cuello es una cadena de dependencias y **el developer que acabas de incorporar no va a acelerar nada**. El pre-flight lo dice en una línea en vez de dejarte deducirlo de dos cifras iguales.

Requiere `docs/detalle-historias-usuario.md`: sin las tallas no hay esfuerzo por fase, y sin esfuerzo el calendario sería inventado.

#### Qué pasa si omites el argumento

Todos los argumentos son **opcionales**, y con paralelismo tener varios changes abiertos es lo normal, no la excepción. Si lo omites, el comando no elige por su cuenta: reúne los candidatos y, si hay más de uno, **te los presenta con el contexto que permite reconocerlos** —fase y objetivo, más la oleada en `waves`, más el lane en `multilane`— para que no tengas que ir a buscar el slug. Con un solo candidato lo usa y te lo dice. Si no puede preguntar (modo no interactivo) y hay ambigüedad, **se detiene** en vez de escoger.

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

Los invocan `aidd`, `aisdd` y `aiba`, pero también se pueden llamar directamente.

| Comando | Skill | Hace |
|---------|-------|------|
| `booster-ux` | `booster-ux` | Prototipos/pantallas UX en dos variantes (imagen + HTML navegable) |
| `booster-uml` | `booster-uml` | Diagramas UML (Mermaid) en HTML para un change de OpenSpec |
| `booster-docs` | `booster-docs` | Vista HTML dinámica de un documento de planificación AIDD/SDD |

### `aiba` — Negocio, entrega y medición (plugin `aiba`, 5 comandos)

> **La capa que da la cara ante el negocio**: lo que el cliente firma (el DF), lo que aprueba (el plan de recursos), el calendario que sigue (los sprints) y los KPIs con los que juzga si mereció la pena.
>
> Los cuatro últimos vivían en `aidd` hasta la v1.8.0 del marketplace. **Sus comandos son ahora `aiba ...` y no quedan alias `aidd ...`**; lo que no cambia es el contrato de datos, porque siguen leyendo y escribiendo los mismos ficheros de `docs/`.
>
> Metodología propia en `plugins/aiba/methodology/native-ai-aiba.md`. Autónomo de OpenSpec: consume lo que producen AIDD y AISDD sin modificarlo.

| Fase | Comando | Skill | Genera / hace |
|------|---------|-------|---------------|
| 1.4 (opc.) | `aiba hu-review-plan` | `aiba-hu-review-plan` | `docs/plan-revision-hu.md` + Excel de cuatro pestañas: cómo se revisan y cierran las HU con negocio y TI |
| 1 (post) | `aiba functional-design [HU-XX]` | `aiba-functional-design` | Un **DF en Word por historia** en `docs/df/`: portada, control de versiones y aprobaciones, índice, introducción y alcance, la HU con filtros/campos, integraciones, validaciones (frontal/core), mensajes, pantallas, criterios de aceptación, especificaciones técnicas y puntos abiertos |
| 1 (post) | `aiba test-plan [HU-XX]` | `aiba-test-plan` | Por historia, el **plan de pruebas** en `docs/pruebas/`: un `.xlsx` con el inventario de casos (`PS.FU.CU01.01`, criticidad, pasos, resultado esperado, traza al requisito y al change, marca manual/automatizable) y un `.docx` de evidencias con un bloque por caso. **Genera el plan; no ejecuta las pruebas** |
| 3.5.1 | `aiba project-plan` | `aiba-project-plan` | `docs/planificacion-proyecto.md` (recursos + estimación humano vs IA con KPIs de la diferencia) |
| 3.5.2 | `aiba sprint-planning` | `aiba-sprint-planning` | `docs/sprint-plan.md` (+ volcado opcional a Jira) |
| transversal | `aiba status-report` | `aiba-status-report` | `docs/estado-proyecto.json` + `docs/html/estado-proyecto.html`: informe de situación ejecutivo con el **avance medido por trabajo ejecutado** (fases cerradas ponderadas por su esfuerzo, no por fechas), previsto vs real, bloqueos medidos en la auditoría, camino crítico, ritmo de entrega, riesgos y acciones con responsable y plazo |
| transversal | `aiba metrics` | `aiba-metrics` | `docs/kpis-ia.md` (KPIs **medidos** de uso de IA) |

Alias: `aiba df` · `aiba planificacion sprints` · `aiba planificacion proyecto` · `aiba kpis`.

> `aiba metrics` no es un paso del método: es una capa de observación **independiente del resto y ejecutable en cualquier momento**. Distingue siempre lo medido de lo estimado, y se niega a publicar cifras de ahorro que no se sostienen — un KPI de ROI inventado hace más daño que no tener ninguno, porque se usa para decidir.

**Genérico por defecto, y pregunta antes.** El documento sale sin logotipos ni colores corporativos, y el comando pregunta si quieres aplicar una marca —desde una carpeta local o una URL— con «sin marca» como opción recomendada. Un DF acaba en manos de un cliente que tiene su propia identidad: generarlo con la marca de quien lo escribe obliga a rehacerlo. Como usa **estilos nativos de Word** (`Heading 1/2/3`, estilo de tabla, cabecera y pie editables, índice como campo `TOC`), aplicar cualquier identidad después es cambiar el estilo, no repasar el documento.

**No inventa.** Lo que no se deduce de la documentación se marca `[PENDIENTE: ...]` y genera una fila en **Puntos abiertos**, que convierte las lagunas en trabajo asignable en lugar de en texto plausible. Un DF se firma y se desarrolla contra él.

**Reedita sin destruir.** Si el `.docx` ya existe, regenera solo las secciones afectadas, conserva lo que el analista escribió a mano y **añade** una fila al control de versiones en vez de sobrescribirla.

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

## Por qué hay que instalar los cuatro

No son cuatro copias del mismo paquete: son **cuatro piezas de un mismo flujo** que se llaman entre sí. El método AIDD-SDD completo va de la captura de requisitos hasta la ejecución de cada change, y en ese recorrido:

1. **`aidd` cubre la definición y el diseño** (Fases 0–2: requisitos → historias → arquitectura → guía de estilos). Es el "qué".
2. **`aisdd` cubre la ejecución** (Fases 3–4: roadmap por presupuesto de contexto —consciente del `sprint-plan`— y el ciclo `open/implement/close change` sobre OpenSpec, con auditoría e integración Jira). Es el "cómo se construye".
3. **`aiba` cubre lo que ve el negocio** (Paso 1.4, DF por historia, Fase 3.5 y la medición: revisión de HU → diseño funcional → plan de recursos → sprints → KPIs). Es el "cuánto cuesta" y el "cuándo llega". Es **autónomo**: se puede usar sin OpenSpec, y sus documentos son los que `aisdd roadmap` lee para alinearse con el calendario.
4. **`boosters` es la dependencia compartida** de los tres anteriores. No es opcional si usas el flujo completo:
   - `aidd prototype` (Fase 2.2) **redirige a `booster-ux`** para maquetar las pantallas del prototipo.
   - `aisdd prototype-ux` y `aisdd uml` (del plugin `aisdd`) **invocan a `booster-ux` y `booster-uml`** para documentar cada change.
   - Los skills de planificación de `aidd`, `aisdd` y `aiba` **invocan a `booster-docs`** para dejar, junto a cada `.md` generado (requisitos, historias, roadmap, sprint-plan…), una vista HTML complementaria para consumo humano (el Markdown sigue siendo la única fuente de verdad).
   - Si `boosters` no está instalado, esos pasos avisan de que falta el booster y no generan ni prototipos, ni diagramas, ni vistas HTML.

Claude Code **no resuelve dependencias entre plugins automáticamente**: cada plugin se instala por separado, y ninguno trae los scripts ni los hooks de otro. Por eso, para el flujo de extremo a extremo necesitas los cuatro. (Si solo vas a definir y diseñar, `aidd` por sí solo funciona; si solo vas a planificar y medir, `aiba` también — pero la instalación recomendada y completa son los cuatro.)

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

# Instalar los cuatro plugins del flujo integrado
/plugin install aidd@aidd-sdd
/plugin install aisdd@aidd-sdd
/plugin install aiba@aidd-sdd
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

- `/aiba:aiba-sprint-planning`, `/aidd:aidd-requirements`, …
- `/aisdd:aisdd-specs` (comandos `aisdd …`; alias legacy `native-ai …`)
- `/boosters:booster-ux`, `/boosters:booster-uml`, `/boosters:booster-docs`
- `/aiad:aiad-tdd`, `/aiad:aiad-review`, `/aiad:aiad-save`, …

También se activan por lenguaje natural y por sus comandos internos (`aiba sprint-planning`, `aisdd open change`, `aiad tdd`, `aiad review`, …).

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
    "aiba@aidd-sdd": true,
    "boosters@aidd-sdd": true,
    "aiad@aidd-sdd": true
  }
}
```

## Registro de actividad (opt-in)

Los cinco plugins traen un hook `PostToolUse` (`hooks/aidd-activity-hook.sh`) que deja una traza de qué se ha hecho sobre el código: **fecha y hora, usuario, skill ejecutado y fichero trabajado**, una línea por acción.

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
- **Sin duplicados**: el hook viaja en los cinco plugins —incluido `aiba`, que es quien luego lo consume— así que con varios instalados se dispara varias veces por la misma acción; deduplica por `tool_use_id` y solo escribe la primera.
- Lo que escribes tú a mano en tu editor **no pasa por las tools de la IA y por tanto no se registra**. El log es traza de la IA, no vigilancia del humano.
- No registra el contenido de tus prompts ni del código: solo el skill, el fichero y los argumentos del comando.

Es independiente de `docs/aiad-journal.md` (plugin `aiad`), que responde a otra pregunta: **cuánto** escribiste tú frente a lo que delegaste. Puedes tener los dos, uno o ninguno.

> **Nota**: el resumen de `note:` es determinista (los argumentos del comando). Un hook es un script de shell, sin modelo detrás, así que no puede redactar en prosa qué le pediste; para eso tendría que escribirlo el propio skill.

### KPIs a partir del registro

Con el registro activo, `aiba metrics` convierte esa traza en un informe (`docs/kpis-ia.md` + HTML): tiempo atendido, reparto planificación vs ejecución, tiempo de ciclo por HU o change, retrabajo y código entregado.

Se ejecuta **cuando quieras y las veces que quieras**: solo lee (registro, `git log`, las tallas de `docs/detalle-historias-usuario.md` para el baseline y, si el proyecto usa AISDD, `openspec/audit/*.jsonl`) y no modifica nada del proyecto. Si falta alguna de esas fuentes, recorta el informe y lo dice, pero no falla.

**Calidad de la especificación (solo con AISDD).** El resto del informe mide velocidad, y velocidad sin calidad es media foto. De la auditoría salen tres cifras que la completan sin instrumentar nada nuevo:

- **Correcciones por change** — retrabajo de *especificación*, complementario al churn, que mide retrabajo de *código*. Se leen distinto: churn alto con correcciones bajas suele ser refactor legítimo; correcciones altas con churn bajo significa que las specs iban mal y alguien lo absorbió adivinando. Muchas correcciones en un change apuntan a su `open change`, no a un equipo lento.
- **% de decisiones que la IA resolvió sin preguntar** — cuánta autonomía se está tomando el pre-flight.
- **Lead time real `open change` → `close change`**, medido de la traza en vez de inferido.

Es una **cota inferior**: solo cuenta las correcciones que llegaron a `decisions.md`. Sirve para comparar changes entre sí, no como recuento exacto — y el informe lo dice donde se lee. Se desactiva con `--no-audit`.

⚠️ **El registro no es retroactivo.** `git log` alcanza todo el historial, pero la traza empieza el día que creaste `docs/aidd-activity.md`. Si quieres medir un sprint, actívalo **antes** de empezarlo.

El ahorro es harina de otro costal, y conviene entender por qué antes de enseñar un número a nadie:

- El registro mide **tiempo atendido**, no esfuerzo total. No ve revisar, probar, teclear a mano ni reunirse, y lo que escribes tú en tu editor no pasa por las tools de la IA.
- Por eso `aiba metrics` **se niega a calcular ahorro** salvo que el equipo declare su esfuerzo real en la ventana medida (`--real-days`, de partes de horas o worklogs). Restar el tiempo atendido al baseline daría aceleraciones de x100, que es justo el tipo de cifra que no aguanta una pregunta incómoda.
- El baseline es el esfuerzo humano de las tallas XS/S/M/L/XL, y es legítimo porque se declaró **antes** de ejecutar. No es un ajuste a posteriori.
- Si la aceleración resultante supera x10, el informe la marca como **no publicable** y explica que casi siempre significa esfuerzo infradeclarado o baseline inflado.

## MCP recomendados

Los skills integran dos servicios externos vía **MCP**. Ambos son **opcionales**: sin ellos todo funciona igual y el paso correspondiente se omite con aviso (los skills nunca caen a llamadas REST manuales ni gestionan credenciales). Los skills localizan las tools **por función**, no por nombre, así que cualquier variante de MCP equivalente sirve.

| MCP | Quién lo usa | Para qué |
|-----|--------------|----------|
| **Atlassian (Jira)** | `aiba-sprint-planning` · `aisdd-specs` | Volcado del sprint-plan (sprints + Stories), sub-tareas por change, transiciones In Progress/Done, re-faseado y reconstrucción del enlace |
| **Figma** | `aidd-style-guide` | Extraer la identidad visual real de un diseño (paleta, tipografía, espaciado, tokens) en vez de inferirla |

**Atlassian.** ⚠️ **El MCP remoto oficial de Atlassian NO expone las operaciones Agile** (crear sprints, añadir/mover issues de sprint): cubre issues y transiciones, pero **no basta para el volcado de `aiba sprint-planning`** — lo comprobamos en un proyecto real y hubo que instalar otro. Recomendación según lo que necesites:

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

La metodología AIDD-SDD viaja **dentro** de los plugins `aidd` y `aisdd` (carpeta `methodology/`, copias espejo). Los skills la referencian con `${CLAUDE_PLUGIN_ROOT}/methodology/native-ai-aidd-sdd.md`, así que resuelve tras instalar en cualquier repo. Es referencia de solo lectura; no se carga automáticamente.

Los plugins `aiba` y `aiad` llevan la suya propia, porque cubren capas que el documento AIDD-SDD ya no describe: `native-ai-aiba.md` (el conjunto que da la cara ante el negocio: los siete skills, el rol de AI Delivery Manager, el Paso 1.4, la Fase 3.5 y la medición) y `native-ai-aiad.md` (el manifiesto *ia-in-the-loop*, el catálogo de skills, el puente HU ↔ change y la bitácora de autoría).

**FAQ.** [FAQ.md](FAQ.md) responde las preguntas frecuentes del ciclo AISDD: qué crea cada comando (`open`/`implement`/`close change`), qué ocurre en Jira en cada paso, quién crea Stories y sprints, y los casos límite (enlace perdido, re-faseado, sprints de horas).

**Vistas HTML.** Junto a cada `.md` de metodología hay un `.html` homónimo (misma carpeta) renderizado con `booster-docs`, para lectura humana cómoda con índice navegable — [native-ai-aidd-sdd.html](plugins/aidd/methodology/native-ai-aidd-sdd.html), [getting-started](plugins/aidd/methodology/native-ai-aidd-sdd-getting-started.html), [native-ai-aiba.html](plugins/aiba/methodology/native-ai-aiba.html) y [native-ai-aiad.html](plugins/aiad/methodology/native-ai-aiad.html). El Markdown sigue siendo la **única fuente de verdad**.

## Publicación y CI

El marketplace tiene una **versión global** en el fichero `VERSION` de la raíz. No sustituye a las versiones de cada `plugin.json` —esas siguen marcando qué reinstala el usuario—, sino que agrupa un conjunto de cambios en algo publicable.

La numeración **arranca en `1.6.0` y continúa la de `native-ai-specs` v1.6.0**, del que este marketplace es la continuación mantenida. Empezar en `1.0.0` habría dado a entender que es un producto distinto y más joven de lo que realmente es.

**Para publicar**: sube `VERSION` en la misma PR que cambia lo que sea. Al mergear a `main`, el workflow `release.yml` comprueba si existe la etiqueta `v<VERSION>` y, si no existe, crea la etiqueta y el release. La puerta es la etiqueta y no la rama, así que el workflow es idempotente: puedes mergear varias PRs sin tocar `VERSION` y no pasará nada, y re-ejecutarlo no duplica releases.

Las notas del release las genera `release_notes.py` comparando contra la etiqueta anterior, en orden de lo que más urge leer: **Atención al actualizar** (versiones mayores y commits marcados con `!`), **Novedades** (entradas del `ROADMAP.md` que pasan a implementada), las tablas de **qué plugins y qué skills cambian de versión**, los **skills que ya no están donde estaban** (movidos de plugin o eliminados) y, plegados, los commits. Quien consume el marketplace quiere saber dos cosas —si algo se rompe y si tiene que reinstalar—, y ambas van antes que el detalle. Un skill que desaparece es la ruptura más cara, y es justo la que no se ve recorriendo solo lo que existe hoy.

**Olvidarse de subir una versión** es el fallo evidente de tenerlas manuales, así que `validate.yml` lo comprueba en los dos sentidos en cada PR: si algún `plugin.json` cambia de versión y `VERSION` no, falla; y si un plugin tiene ficheros modificados y la misma versión, también. El segundo es el silencioso: Claude Code cree que la copia instalada está al día, así que el cambio nunca llega al usuario.

Ese mismo workflow corre en cada PR y en `main`:

| Comprobación | Qué evita |
|---|---|
| `check_manifests.py` | Que `marketplace.json` apunte a un plugin inexistente, o que un plugin en disco no esté declarado. Rompe la instalación de todos y no falla hasta que alguien lo intenta |
| `check_skills.py` | `SKILL.md` sin frontmatter válido, con `name` que no coincide con su directorio o sin `description`: el skill no se carga, o el modelo no sabe cuándo invocarlo |
| `check_plugin_assets.py` | Que un skill invoque `${CLAUDE_PLUGIN_ROOT}/…` de un fichero que su plugin no lleva dentro, y que las copias replicadas entre plugins (el hook de actividad, `stamp_doc.py`) diverjan |
| `check_skill_refs.py` | Que un skill nombre un `references/…` o un `scripts/…` que no está donde lo busca, que un comando de ejemplo use una ruta relativa al skill (se ejecuta desde el proyecto del usuario, donde no existe), que quede un `references/` que nadie enlaza, o que sobreviva una ruta del empaquetado anterior (`.agents/skills/`, `%USERPROFILE%`) |
| `check_contracts.py` | Que una invocación documentada —la de un skill o la de este README— pase una flag que el script no acepta, o se deje una obligatoria (flag o posicional), y que un documento con vista HTML no tenga entrada en `DOC_TYPES` |
| `check_generated_html.py` | Que un `.html` de metodología no coincida con su `.md`, y que las copias de `aidd/` y `aisdd/` se desincronicen |
| `py_compile` | Un script Python que no compila |
| `check_mojibake.py` | UTF-8 mal codificado en los markdown, usando el propio script del skill |

Todas nacen de fallos reales, y tres merecen comentario porque el fallo **no hace ruido**. El de los HTML, porque el desfase se produce **sin que nadie edite el `.md`**: basta con cambiar `render_docs_html.py`, y así fue como el HTML de la metodología AIAD se quedó atrás durante dos PRs sin que se notara. El de los assets, porque **Claude Code instala cada plugin por separado**: al mover skills de `aidd` a `aiba` con `git mv`, `stamp_doc.py` desapareció de `aidd`, donde ocho skills lo siguen ejecutando. Nada falla al hacer el cambio; falla en casa del usuario.

Y el de las rutas, porque **la carga de los skills es en diferido**: `SKILL.md` es un índice y las reglas viven en `references/*.md`, que el agente lee solo cuando el índice se lo dice. Una ruta que no resuelve no da error —el agente no encuentra el fichero, sigue sin él, y la regla que contenía simplemente no se aplica—, que es la forma de fallo que más se parece a que todo funciona. La convención que impone: **mismo skill** → `references/x.md`; **otro skill del mismo plugin** → `${CLAUDE_PLUGIN_ROOT}/skills/<skill>/references/x.md`; **otro plugin** → sin ruta, nombra solo el skill, porque el usuario puede no tenerlo instalado.

## Mantenimiento

- **Cuándo partir un `SKILL.md` en `references/`**: se parte cuando se cumplen **las dos** condiciones —más de ~400 líneas **y** dos o más puntos de entrada que no comparten flujo—. Con un solo comando no se parte por grande que sea: ese flujo se ejecuta entero, así que dividirlo carga las mismas líneas *más* el índice.

  Hoy solo `aisdd-specs` las cumple (8 comandos): es índice de 94 líneas + `references/*.md` por comando. El siguiente skill por tamaño tiene 322 líneas y un único comando, y en los cuatro más grandes la sección «Flujo del comando» ocupa el 70-75 % — no hay nada condicional que merezca quedarse sin cargar.

  A vigilar: `aiba-sprint-planning` lleva dentro el volcado opcional a Jira. Si esa parte crece y el skill se acerca a las 400-500 líneas, pasaría a haber dos caminos reales (planificar y volcar) y la división tendría sentido.
- **Versionado**: cada `plugin.json` fija `version` (semver). **Sube la versión al publicar cambios**; si no, los usuarios ya instalados no recibirán las novedades (Claude Code los cree en la misma versión). Tras subir cambios, los usuarios actualizan con `/plugin marketplace update aidd-sdd`.
- **Regenerar los HTML de metodología** (obligatorio si se edita un `.md` de `methodology/`; la copia de `aisdd` es un espejo **del `.md` y del `.html`**, y `validate.yml` comprueba los dos, así que el `cp` final copia ambos):

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
    --input plugins/aiba/methodology/native-ai-aiba.md \
    --output plugins/aiba/methodology/native-ai-aiba.html \
    --title "Native AI · AIBA — Análisis de negocio, entrega y medición"
  python3 plugins/boosters/skills/booster-docs/scripts/render_docs_html.py \
    --input plugins/aiad/methodology/native-ai-aiad.md \
    --output plugins/aiad/methodology/native-ai-aiad.html \
    --title "Native AI · AIAD — AI-Augmented Development"
  cp plugins/aidd/methodology/native-ai-aidd-sdd.md \
     plugins/aidd/methodology/native-ai-aidd-sdd.html \
     plugins/aidd/methodology/native-ai-aidd-sdd-getting-started.md \
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
