# Native AI · AIDD-SDD — Metodología AI-Native (AI Driven Development + Spec-Driven Development)
**Versión:** 4.0
**Fecha:** 2026-06-22
**Base de tooling:** skills **AIDD** (`aidd-*` — planificación, diseño y entrega) + skill **aisdd-specs** (OpenSpec — ejecución) + **boosters** compartidos (`booster-ux` prototipos, `booster-uml` diagramas, `booster-docs` vistas HTML de los documentos de planificación).

> **Terminología (importante).** Tres conceptos que conviven y NO son lo mismo:
> - **SDD** (*Spec-Driven Development*) — la **metodología**: proceso, roles y fases. El "cómo se trabaja" (este documento).
> - **AIDD** (*AI Driven Development*) — el **skill set** que automatiza la **planificación, el diseño y la entrega** (Fases 0-2 y 3.5). Comandos `aidd *`. Cada comando aplica el prompt del paso; ejecutarlo equivale a lanzar ese prompt a mano.
> - **aisdd-specs** — el **skill set** de **ejecución** sobre OpenSpec (Fases 3 y 4+). Comandos `aisdd *` (alias legacy `native-ai *`).
>
> **Novedad v4.** (1) Las Fases 0-2, antes descritas como prompts manuales del AI Architect, ahora se ejecutan con los comandos `aidd` (mismo proceso, empaquetado en skills). (2) Se añade un quinto rol, **AI Delivery Manager**, y la **Fase 3.5**, que traduce el roadmap en un **plan de recursos** (`aidd project-plan` → `docs/planificacion-proyecto.md`) y un **plan de sprints** (`aidd sprint-planning` → `docs/sprint-plan.md`), consumible por un equipo Scrum. Ver Fase 3.5 y registro #008.

---

## 1. Filosofía

AI-Native Development no es usar la IA como un asistente que escribe código más rápido. Es un modelo de trabajo donde **la IA generativa es parte estructural del proceso**, no una herramienta auxiliar, y el humano actúa como **director de orquesta**: aprueba, decide y valida en cada transición.

> **La especificación como motor del desarrollo:** transformamos los requisitos del cliente en contexto estructurado que los agentes IA pueden procesar de forma consistente. Sin especificación, no hay implementación.

El objetivo es garantizar **coherencia** entre lo que se define, lo que se diseña y lo que se implementa, evitando la deriva habitual donde el código se aleja de los requisitos con el paso de los sprints.

En esta versión, toda la operación sobre especificaciones se canaliza a través del skill **`aisdd-specs`**, que envuelve OpenSpec con tres capas adicionales:

1. **Pre-flight de dudas** — antes de abrir o implementar un change, el agente resuelve ambigüedades reales con el humano y las persiste en `decisions.md`. Las **bloqueantes se preguntan siempre, sin límite** —son, por definición, aquellas sin las que no se puede producir un spec sólido—; cuántas preferencias y confirmaciones se plantean lo fija cada proyecto. El *human-in-the-loop* deja de ser una recomendación: es un paso ejecutable del comando.
2. **Roadmap consciente del contexto** — la planificación se adapta al **presupuesto de contexto** del modelo (bajo/medio/alto): a menor ventana útil, más fases y más estrechas.
3. **Auditoría obligatoria** — cada comando deja una entrada estructurada con hashes de entrada/salida, versión de prompt, modelo y decisiones humanas en `openspec/audit/`.

**Principios fundacionales:**

| Principio | Descripción |
|---|---|
| **IA como motor, no como herramienta** | La IA generativa es parte estructural del proceso de desarrollo en todos sus roles |
| **Human-in-the-loop obligatorio** | El humano supervisa, valida y aprueba en cada transición. El pre-flight de dudas lo hace explícito y trazable |
| **Documentos como fuente de verdad** | Toda decisión queda en un fichero (`docs/`, specs OpenSpec, `decisions.md`). El código se genera a partir de los documentos, no al revés |
| **Roles separados, contextos limpios** | Cada rol de IA arranca con los documentos de su fase, sin el historial completo. El presupuesto de contexto regula cuánto se carga por change |
| **Handoff explícito** | El paso de un rol al siguiente se hace entregando documentos revisados y aprobados por el humano |
| **Validación antes de implementar** | Siempre se valida con cliente (prototipo) antes de construir la arquitectura real |
| **Iteración y refinamiento continuo** | Cada ciclo optimiza progresivamente especificaciones, código y arquitectura |
| **Idempotencia documental** | Cualquier IA que arranque con los mismos documentos debe llegar a conclusiones compatibles |
| **Trazabilidad auditable** | Cada comando `aisdd` registra qué se ejecutó, sobre qué input, con qué modelo y qué decidió el humano |

---

## 2. Macro-fases

El proceso se organiza en tres macro-fases que agrupan las etapas de trabajo:

```
┌─────────────────────┬──────────────────────┬──────────────────────┐
│     DEFINITION      │      EXECUTION       │     VALIDATION       │
│                     │                      │                      │
│ 1. Descubrimiento   │ 4. Generación y      │ 5. Integración y     │
│    de Agentes       │    Refinamiento      │    Validación        │
│ 2. Extracción de    │    (open + implement │                      │
│    Conocimiento     │     change)          │                      │
│ 3. Framework de     │                      │                      │
│    Prompting +      │                      │                      │
│    Roadmap          │                      │                      │
└─────────────────────┴──────────────────────┴──────────────────────┘
```

**Entradas del cliente al inicio del proceso:**

```
Cliente
  ├── Documentación (briefings, specs, manuales)
  ├── Código existente (si aplica)
  └── Bases de datos / modelos de datos
         │
         ▼
    AI Architect
```

**Flujo general entre fases:**

```
CLIENT INPUT
(Docs, Code, DBs)
      │
      ▼
DEFINITION PHASE
  AI Architect  (comandos `aidd`)
  → Definición y diseño: aidd requirements → user-stories → user-story-details
    → prototype-architecture → prototype (booster-ux) → style-guide
    → architecture-proposal → architecture
  AI Lead
  → aisdd init  +  aisdd roadmap
  AI Delivery Manager
  → aidd project-plan + aidd sprint-planning  (plan de recursos + plan de sprints)
      │
      ▼  (aprobación humana)
EXECUTION PHASE  ◄─────────────────────────────── KO ─┐
                                                       │
  ── modo atómico (un solo hilo) ──                     │
  AI Lead (open change → specs validados) ──► AI Dev    │
                                                       │
  ── modo multilane (un hilo por lane) ──               │
  F0 / barrera FB-NN: bloquea TODOS los lanes           │
      │                                                 │
      ├─ lane `back`  ──► Back AI Lead ──► Back AI Dev   │
      ├─ lane `front` ──► Front AI Lead ──► Front AI Dev │
      └─ lane `…`     ──► AI Lead      ──► AI Dev        │
         (en paralelo; un change abierto POR LANE)       │
                                                       │
  AI Dev: implement change + verificación + fix bugs    │
      │                                                 │
      ▼  (por cada change)                              │
VALIDATION PHASE ──────────────────────────────────────┘
  Outcome Validator
  → Validación técnica + funcional
  → Aprobación de Merge Request
  → aisdd close change  (verifica que el change no salió de su lane)
      │
      ▼ (OK)
  Siguiente change del MISMO lane ──► AI Lead (aisdd open change) ──► AI Dev
  Los demás lanes no se detienen: siguen su propio ciclo en paralelo.
```

> **Los tres modos.** El faseado por defecto es **atómico**: un único change abierto en todo el proyecto. `aisdd roadmap` ofrece además dos formas de paralelizar, y la elección es explícita:
>
> | Modo | Qué paraleliza | Garantía |
> |---|---|---|
> | **`atomic`** | Nada | Total, por construcción |
> | **`waves`** (oleadas) | Hasta `N` fases a la vez, una por dev, respetando dependencias | **Ninguna** — ordena, no protege |
> | **`multilane`** (lanes) | `N` líneas persistentes con rutas y specs disjuntas | Declarada y **verificada** al cerrar |
>
> El invariante que protege la metodología no cambia en `multilane`: dentro de cada superficie de decisión sigue habiendo **un solo hilo**; lo que se paraleliza son las superficies. En `waves` ese invariante **no lo protege el tooling** — se confía en el criterio del arquitecto al fasear. Ver §3.bis.

---

## 3. Roles y responsabilidades

La metodología define cinco roles con responsabilidades diferenciadas. Cada uno opera con contexto acotado a su fase. La columna de comandos indica qué comandos ejecuta cada rol (`aisdd` — alias legacy `native-ai` — para AI Lead/Developer/Outcome Validator; `aidd` para el AI Delivery Manager de la capa de planificación de entrega).

### AI Architect

El rol de mayor nivel conceptual. Combina Product Owner y arquitecto de producto. **No implementa código.**

| Responsabilidad | Detalle |
|---|---|
| **Extrae y documenta reglas de negocio** | Transforma el brief del cliente en requisitos formales trazables |
| **Define proceso e integraciones** | Identifica qué sistemas externos intervienen y cómo |
| **Genera el prototipo mockeado** | Construye la demo para validación con el cliente. Puede apoyarse en `aisdd prototype-ux` (booster-ux) para las pantallas clave |
| **Genera guía de estilos + propuesta de arquitectura** | Base visual y estructural para el AI Lead y los AI Developers |
| **Genera la arquitectura técnica definitiva** | Produce `arquitectura-base.md` — documento implementable con decisiones explícitas, árbol de carpetas real y responsabilidades por capa. Es el insumo principal de `aisdd roadmap` |
| **Aporta el material para el roadmap** | Deja requisitos y arquitectura en estado consumible por el AI Lead para fasear con `aisdd roadmap` |

> El AI Architect ya **no** produce el borrador del framework de prompting a mano: en esta versión ese artefacto (`docs/prompts-roadmap-native-ai.md`) lo genera el comando `aisdd roadmap` a partir de sus documentos. El Architect garantiza que requisitos y arquitectura están completos para que el roadmap salga coherente.

### AI Lead (Front / Back)

En proyectos full stack, el AI Lead se desdobla en **Front AI Lead** y **Back AI Lead**, cada uno responsable de su capa. **No implementa código.**

> En roadmaps **multilane** (§3.bis) el desdoble deja de ser solo organizativo: cada Lead conduce **su lane**, con un change abierto propio, en paralelo con los demás. Las fases `F0` y las barreras `FB-NN` no pertenecen a ningún lane — las abre el Lead que posea el contrato compartido, y detienen a todos.

| Responsabilidad | Comandos / Detalle |
|---|---|
| **Inicializa Native AI Specs** | Ejecuta `aisdd init`: instala/verifica OpenSpec, comprueba `booster-ux`/`booster-uml`, registra los comandos en `AGENTS.md` y vuelca el contexto inicial a `openspec/config.yaml` |
| **Fasea el desarrollo** | Ejecuta `aisdd roadmap`: genera `docs/roadmap.md`, `docs/prompts-roadmap-native-ai.md` y la sección `roadmap` de `config.yaml`, ajustando granularidad al presupuesto de contexto |
| **Define componentes reutilizables (Tools)** | Identifica abstracciones comunes que los AI Developers pueden reutilizar; las refleja en los prompts del roadmap |
| **Cierra foundation** | Ejecuta el ciclo `open change` → `implement change` → `close change` de `foundation` para dejar la base del proyecto operativa |
| **Abre y valida los specs de TODOS los changes** | Ejecuta `aisdd open change <slug>` de cada change del roadmap, participa en el **pre-flight de dudas**, revisa y valida los artefactos generados (`proposal.md`, `design.md`, `spec.md`, `decisions.md`) y solo entrega specs ya validados al AI Developer. Es el control de calidad de la especificación antes de que se implemente |
| **Soporte directo al Dev Team** | Resuelve dudas técnicas y desbloqueos durante la implementación |
| **Gestiona ajustes de spec** | Si el Outcome Validator reporta un problema de spec, reabre/ajusta el change afectado y, si procede, regenera el roadmap o los prompts |
| **Escala al AI Architect si es necesario** | Si el problema es arquitectónico de fondo, lo traslada al Architect para que corrija desde el origen |

### AI Developer (Front / Back)

Implementa el código a partir de los specs **ya abiertos y validados por el AI Lead**. **No abre changes. No toma decisiones de arquitectura. No habla con el Lead directamente.**

> En modo **multilane**, cada Dev trabaja sobre el lane que tenga activo (`aisdd lane switch`) y solo escribe dentro de las **rutas de ese lane** — `aisdd close change` lo verifica. Si durante la implementación descubre que el **contrato compartido** es insuficiente, eso no se arregla sobre la marcha: es una corrección de **nivel 4**, se detiene y se escala al dueño del contrato, porque otros lanes están construyendo sobre ese mismo supuesto.

| Responsabilidad | Comandos / Detalle |
|---|---|
| **Recibe los specs validados del change** | El AI Lead le entrega el change ya abierto con sus artefactos validados (`proposal.md`, `design.md`, `spec.md`, `decisions.md`). El Developer **no** ejecuta `aisdd open change` |
| **Revisa los artefactos recibidos** | Lee y comprende `proposal.md`, `design.md`, los `spec.md` y `decisions.md` antes de implementar |
| **Lanza la implementación** | Ejecuta `aisdd implement change <slug>` (incluye su propio pre-flight de dudas antes de tocar código; las dudas de spec o arquitectura las eleva, no las inventa) |
| **Genera UML/prototipos si aplica** | Puede ejecutar `aisdd uml <slug>` y `aisdd prototype-ux <slug>` para documentar visualmente el change |
| **Valida y testea el código generado** | Prueba manualmente que la aplicación funciona end-to-end |
| **Corrige los bugs que identifique** | Itera sobre los bugs de implementación que detecte hasta que el código está limpio para entregar al Outcome Validator |
| **Prepara la feature para integración** | Verifica que el branch está actualizado, sin conflictos, y la feature lista para abrir el Merge Request |
| **Entrega al Outcome Validator** | Toda comunicación hacia arriba pasa por el Validator, no directamente al Lead |

### Outcome Validator

Capa de diagnóstico, QA técnico y funcional. Es el único rol que puede escalar problemas al AI Lead. Su aprobación es el paso previo obligatorio antes de archivar cualquier change. **No implementa.**

| Responsabilidad | Comandos / Detalle |
|---|---|
| **Revisión funcional** | Verifica que cada criterio de aceptación está cumplido |
| **Revisión técnica** | Revisa el código generado por la IA en busca de errores, deuda o malas prácticas |
| **Validación de estándares y patrones** | Comprueba que el código sigue la arquitectura y guía de estilos definidas |
| **Verifica trazabilidad** | Comprueba que `decisions.md` del change refleja las decisiones reales y que existe entrada de auditoría en `openspec/audit/` |
| **Diagnostica la naturaleza del problema** | Determina si un problema es de implementación (→ Dev), una decisión técnica no documentada (→ se resuelve dentro del change), de spec (→ Lead) o arquitectónico (→ Lead para escalar al Architect) |
| **Resuelve en el change** | Decisiones técnicas que ningún documento AIDD fijaba: se registran como `Tipo: correccion` en `decisions.md` y el ciclo continúa, sin escalar ni re-aplicar el change (ver "Regla de corte") |
| **Devuelve al AI Developer** | Solo para problemas de implementación — con descripción, criterio que falla y evidencia |
| **Reporta al AI Lead** | Cuando detecta problemas de spec o arquitectónicos que superan el scope del Developer |
| **Aprobación de Merge Requests** | Es la firma final antes de que el change se integre en la rama principal |
| **Archiva el change validado** | Ejecuta `aisdd close change <slug>` (envuelve `openspec archive`) |
| **Lanza el siguiente change** | Tras archivar, habilita al **AI Lead** para que abra y valide el siguiente change (`aisdd open change`) y lo entregue al Developer |

### AI Delivery Manager

Rol de planificación de entrega (añadido en v4). Traduce el diseño y el roadmap a un plan ejecutable por un equipo (humano + agentes): **recursos** y **calendario**. **No implementa código ni toma decisiones de arquitectura.** Opera con los skills `aidd` de la capa de planificación, **autónomos de OpenSpec**.

| Responsabilidad | Comandos / Detalle |
|---|---|
| **Genera el plan de recursos** | Ejecuta `aidd project-plan` en cuanto el diseño (Fase 2) está aprobado: produce `docs/planificacion-proyecto.md` con perfiles/equipo (mapeados a los roles SDD cuando aplica), software/licencias, infraestructura/entornos, esfuerzo agregado con **doble estimación humano clásico vs IA** (a partir de XS/S/M/L/XL) y **KPIs de la diferencia** (ahorro en jornadas, % de reducción y factor de aceleración), dependencias y riesgos de recursos, derivados de `arquitectura-base.md` y las historias |
| **Distribuye el trabajo en sprints** | Ejecuta `aidd sprint-planning` cuando existe `docs/roadmap.md`: produce `docs/sprint-plan.md` agrupando los changes/fases en sprints con objetivo, capacidad, asignación de perfiles y dependencias respetadas |
| **Respeta el faseado por contexto** | No parte un change para encajarlo en un sprint; un sprint contiene changes/historias completos. El roadmap (presupuesto de contexto) manda sobre el calendario |
| **Hace consumible el plan por un equipo Scrum** | Traduce la planificación AI-native a recursos y calendario que un equipo humano gestiona en su día a día |

> Capa **autónoma de OpenSpec**: parte de los documentos (`arquitectura-base.md`, `roadmap.md`, detalle de historias). Si existen changes de OpenSpec, los usa como detalle adicional, pero la unidad de planificación sigue siendo el change/historia del roadmap. En equipos pequeños, el AI Delivery Manager puede ser el mismo humano que actúa de AI Lead.

---

## 3.bis. Paralelismo: oleadas y lanes

### El problema

El ciclo `open change → implement change → close change` es **secuencial por diseño**, y la razón es real: al cerrar un change se consolidan sus decisiones en `decisions.md`. Dos changes vivos sobre la **misma superficie de decisión** producirían specs que se contradicen, y nada lo detectaría.

El efecto colateral aparece en cuanto el equipo crece. Con el desdoble Front/Back de roles, un change que solo toca backend deja al **Front AI Dev parado**, y viceversa. Que un Lead espere es coherente —su trabajo es especificar, no implementar—; que un Dev espere no lo es. La metodología escalaba con el **tamaño del change**, no con el **tamaño del equipo**.

### Dos soluciones, distinta garantía

Hay dos formas de paralelizar, y conviene no confundirlas porque protegen cosas distintas.

**Oleadas (`waves`).** El roadmap pregunta cuántos AI Developers trabajan en paralelo (`parallel_developers`) y agrupa las fases en **tandas**: dentro de cada oleada caben hasta `N` fases sin dependencias entre sí, una por developer; la siguiente oleada no arranca hasta que la actual cierra. Es un artefacto de **planificación**: resuelve el **orden** y hace visible cuánto trabajo puede correr a la vez.

Lo que las oleadas **no** hacen: no declaran qué toca cada fase, no verifican nada al cerrar, y ningún comando de ejecución las conoce. Que dos fases de la misma oleada no se pisen es responsabilidad de quien fasea. Es un intercambio legítimo —cero ceremonia, cero red de seguridad— y por eso el modo se elige explícitamente.

**Lanes (`multilane`).** La solución cuando esa red de seguridad hace falta.

### La solución de los lanes: fraccionar la superficie, no el hilo

`aisdd roadmap` puede generar el roadmap en **modo multilane**: fraccionado en **lanes** (líneas de trabajo) cuyas superficies de decisión son **disjuntas**. Dentro de cada lane sigue habiendo **un único hilo**; lo que corre en paralelo son los lanes entre sí.

El invariante se conserva palabra por palabra: *ningún change trabaja sobre decisiones que desconoce*. Simplemente deja de haber una sola superficie.

### Anatomía

| Tipo de fase | Identificador | Concurrencia |
|---|---|---|
| **Foundation** | `F0` | Secuencial. Bloquea todos los lanes. |
| **Fase de lane** | `F-<lane-id>-NN` (p. ej. `F-Data-Manager-01`) | Paralela entre lanes; secuencial dentro de un lane. |
| **Barrera** | `FB-NN` | Secuencial. Bloquea **todos** los lanes. |

`F0` y las barreras son los únicos momentos en que el proyecto vuelve a ser mono-hilo. Todo lo que afecte a más de un lane —cambio de contrato, migración, permisos, rollout— pertenece a una barrera, nunca a una fase de lane.

### Las tres condiciones

Un corte en lanes solo es válido si se cumplen las tres. Si alguna falla, el modo correcto es `atomic`:

1. **Rutas disjuntas.** Cada lane declara sus rutas de código; ninguna se solapa. `aisdd close change` lo **verifica** antes de archivar.
2. **Specs disjuntas.** Ningún `spec.md` lo escriben dos lanes.
3. **Contrato previo.** Lo que los lanes comparten —esquema de datos, contrato de API, eventos, tipos— queda fijado **antes** de que arranquen, en `F0` o en una barrera, y tiene **dueño**.

La tercera es la que hace el trabajo. Back y front no son independientes por naturaleza: se **fabrica** su independencia con un contrato acordado de antemano, que es exactamente cómo la industria lleva décadas separando ambas capas. Sin contrato previo no hay lanes, hay dos equipos descoordinados.

### Criterio de corte

**Primero la independencia técnica; el rol del dev solo como desempate** cuando hay varios cortes técnicamente válidos. Nunca al revés: un corte que respeta el organigrama pero deja rutas compartidas no es un compromiso aceptable, es un corte inválido.

Advertencia práctica: **`data` rara vez es un lane separado de `back`** — comparten esquema y migraciones, luego comparten superficie de decisión. Los cortes limpios suelen ser pocos y grandes, no muchos y finos. Y el número de lanes viable nunca supera el número de devs de implementación disponibles: un lane sin quien lo conduzca no aporta paralelismo y sí una superficie más que vigilar.

### Qué cambia en la operativa

Con `waves`, **nada**: la oleada vive solo en el roadmap y ningún comando de ejecución la conoce. Ese es su límite y su virtud — se adopta sin tocar la forma de trabajar.

Con `multilane`, cinco cosas:

- **`aisdd lane [list | switch | status]`** selecciona la línea de trabajo activa, igual que `git switch` selecciona rama. Es estado **local de cada dev** (`openspec/.lane`, ignorado por git), lo que permite que una misma persona salte entre lanes.
- **`aisdd open change`** admite un change abierto **por lane**, y rechaza abrir un segundo en el mismo. Una barrera exige que **ningún** lane tenga trabajo en vuelo.
- **`aisdd close change`** comprueba que el change no escribió fuera de las rutas de su lane. Es donde la independencia deja de ser una promesa del faseado.
- **Correcciones nivel 4**: una corrección que toca el contrato compartido **no es local**. Es una **parada coordinada** de los lanes hermanos y una revisión del contrato por su dueño. Cuesta caro a propósito: si fuera barato, los lanes podrían contradecirse gratis.
- **`aidd sprint-planning`** deja de calcular una única cadena crítica: el calendario pasa a ser el `max` de las cadenas de cada lane entre barreras, y **cada sprint contiene unidades de varios lanes a la vez**.

### Lanes con dependencias

Los lanes se prefieren **independientes**, y esa sigue siendo la primera opción. Pero forzar la independencia total donde el dominio no la permite lleva a inventar barreras artificiales —que serializan más de lo necesario— o a renunciar al paralelismo. Por eso hay un escalón intermedio: una fase de un lane puede declarar `depends_on` sobre una fase de otro.

Se acepta si es **puntual** (no la relación entre los dos lanes: si B espera a A casi siempre, no son dos lanes, fusiónalos), **acíclica**, **con coste explícito** (cuánto espera el lane destino y qué hace mientras) y —lo importante— **sin compartir rutas**: una dependencia es de **orden**, nunca de **superficie**. El lane que espera sigue escribiendo solo en lo suyo.

No confundir con una barrera: si lo que falta es **código o un artefacto** del otro lane, es una dependencia y solo detiene al lane destino; si lo que cambia es **el contrato**, es una barrera y los detiene a todos. Modelar como barrera lo que era una dependencia para a gente que no tenía por qué parar.

### Un ejemplo completo: el mismo proyecto en los tres modos

Portal de alta de clientes, **3 developers**, seis bloques de trabajo:

| | Bloque | Esfuerzo | Toca |
|---|---|---|---|
| **A** | Contratos y modelo de datos | 2 d | esquema + tipos compartidos |
| **B** | API de alta | 5 d | `backend/` |
| **C** | UI de alta | 4 d | `frontend/` |
| **D** | Importador CSV | 3 d | `services/import/` |
| **E** | Permisos y roles | 2 d | los tres |
| **F** | Observabilidad y rollout | 2 d | los tres |

**Cómo se llama cada bloque en cada modo.** Conviene tenerlo delante, porque es la principal fuente de confusión: `atomic` y `waves` comparten numeración (la oleada es un campo aparte, no cambia el nombre), mientras que `multilane` **renombra** —el identificador tiene que decir a qué línea pertenece la fase, y las que tocan lo compartido pasan a ser barreras:

| Bloque | `atomic` | `waves` | `multilane` |
|---|---|---|---|
| A | `F1` | `F1` · oleada 1 | `F0` (barrera) |
| B | `F2` | `F2` · oleada 2 | `F-api-01` |
| C | `F3` | `F3` · oleada 2 | `F-portal-01` |
| D | `F4` | `F4` · oleada 2 | `F-import-01` |
| E | `F5` | `F5` · oleada 3 | `FB-01` (barrera) |
| F | `F6` | `F6` · oleada 4 | `FB-02` (barrera) |

#### `atomic` — 18 días, 1 dev activo

```
A·F1 ──► B·F2 ──► C·F3 ──► D·F4 ──► E·F5 ──► F·F6
 2d       5d       4d       3d       2d       2d
```

Dos developers mirando durante todo el proyecto.

#### `waves` — 11 días, 3 devs

```
Oleada 1 (1/3)   A·F1  contratos                              2d
                       depends_on: []
                       │
Oleada 2 (3/3)   B·F2  API    C·F3  UI    D·F4  import        5d  ← max(5,4,3)
                       depends_on: [F1] los tres
                       │
Oleada 3 (1/3)   E·F5  permisos                               2d
                       depends_on: [F2,F3,F4]
                       │
Oleada 4 (1/3)   F·F6  rollout                                2d
```

Mismos nombres que en `atomic`; lo único que se añade es en qué oleada cae cada fase.

**Dónde falla.** Nada dice que B y D no escriban los dos en `backend/clientes/service.ts`. Si lo hacen, dos devs se pisan y **nadie avisó** — ni al fasear, ni al abrir, ni al cerrar. Y si el dev de B descubre que el contrato de A se queda corto, lo corrige en su change: C y D siguen construyendo sobre el contrato viejo sin enterarse.

Las oleadas 3 y 4 son de ancho 1: dos devs ociosos ahí. La oleada al menos lo hace **visible** (`1/3`).

#### `multilane` — 11 días, 3 devs

```
A·F0  contratos ─────────────────────────────────  2d   BARRERA
        │
        ├─ lane api      B·F-api-01     API        5d   paths: backend/
        ├─ lane portal   C·F-portal-01  UI         4d   paths: frontend/
        └─ lane import   D·F-import-01  import     3d   paths: services/import/
        │
E·FB-01  permisos ───────────────────────────────  2d   BARRERA
F·FB-02  rollout ────────────────────────────────  2d   BARRERA
```

La forma es **idéntica** a la de `waves`: mismos bloques, mismo orden, mismos 11 días. Lo único que cambia es que B, C y D declaran **de quién son** (`paths`), y A, E y F —que tocan lo compartido— se convierten en barreras en vez de ser oleadas de ancho 1.

**Dónde muerde la red.** Si `F-import-01` escribe en `backend/clientes/`, `aisdd close change` **falla** y nombra el fichero: o va al lane `api`, o sube a barrera. Y si el dev de `api` ve que el contrato se queda corto, es **nivel 4**: para a `portal` e `import` y lo revisa el dueño del contrato.

#### El resultado

| | `atomic` | `waves` | `multilane` |
|---|---|---|---|
| Calendario | 18 d | **11 d** | **11 d** |
| Devs ocupados en el tramo ancho | 1 | 3 | 3 |
| ¿Detecta colisión de ficheros? | n/a | **No** | Sí, al cerrar |
| ¿Un cambio de contrato alcanza a los demás? | n/a | **No** | Sí |
| Ceremonia | Ninguna | Baja | Media |

**El calendario es idéntico.** Oleadas y lanes llegan al mismo sitio en el mismo tiempo. Lo que cambia es si hay red debajo. Por eso la pregunta no es cuál es mejor, sino **cuánta garantía quieres pagar**.

### Los dos ejes: por qué no compiten

```
                Oleada 1    Oleada 2         Oleada 3    Oleada 4
                ───────────────────────────────────────────────────
lane api        │          │ B·F-api-01    │           │          │
lane portal     │  A·F0    │ C·F-portal-01 │  E·FB-01  │ F·FB-02  │
lane import     │          │ D·F-import-01 │           │          │
                ───────────────────────────────────────────────────
                   1/3          3/3            1/3        1/3
```

**Columnas = oleadas** (cuándo). **Filas = lanes** (quién y dónde). A, E y F ocupan toda la columna porque tocan lo compartido: son a la vez oleada de ancho 1 y barrera — de hecho **una barrera no es más que una oleada de ancho 1 con propiedad declarada**.

Se ve entonces que no son alternativas sino ejes perpendiculares: adoptar «solo oleadas» es **quedarse con las columnas y borrar las filas**. Se conserva el calendario; se pierde saber que B solo puede escribir en `backend/` y que alguien lo comprueba.

Tres pruebas para no confundirlos nunca más:

| Pregunta | Oleada | Lane |
|---|---|---|
| ¿Puedo borrarlo y recuperar el roadmap original? | **Sí** — es un campo más | **No** — cambió qué entra en cada fase |
| ¿Cuándo se decide? | **Después** de fasear | **Antes** de fasear |
| ¿Se puede calcular? | **Sí** — dame `depends_on` y `N` | **No** — hace falta criterio de dominio |

De ahí la consecuencia práctica más útil: **las oleadas se pueden añadir a un roadmap ya hecho sin tocarlo** (`aisdd roadmap` → *anotar*), conservando nombres de fase y `change_hint`, así que no rompen el enlace con el sprint-plan ni con Jira. Los lanes no: retrofitarlos exige re-fasear.

### Cómo elegir modo

| Situación | Modo |
|---|---|
| Un solo dev de implementación | `atomic` |
| Varios devs, y `arquitectura-base.md` da módulos con rutas disjuntas | `multilane` |
| Varios devs, pero sin base para declarar superficies disjuntas | `waves`, asumiendo sus límites |
| **Roadmap ya diseñado y validado que no se quiere alterar** | **`waves` anotado** — no toca el faseado |
| El contrato compartido no se puede fijar antes de arrancar | `atomic` |

Ese cuarto caso es el que mejor distingue a los dos: como la oleada es una **anotación**, se puede añadir a un roadmap existente sin regenerarlo — conserva nombres de fase y `change_hint`, así que no rompe el enlace con el sprint-plan ni con Jira. Los lanes **no se pueden anotar**: retrofitarlos exige re-fasear, porque el corte determina qué entra en cada fase.

`atomic` no es el modo degradado: es el correcto cuando el corte no es defendible. Y `waves` no es un `multilane` de segunda: es la opción honesta cuando quieres paralelizar sin poder prometer aislamiento — siempre que el equipo sepa que la garantía no está.

**Ninguno de los tres impide abrir un segundo change.** `atomic` y `waves` avisan si lo detectan, pero no bloquean: el riesgo de dos changes vivos sobre la misma superficie sigue existiendo y es deliberado. Solo `multilane` lo cierra, porque es el único que declara qué superficie es de quién. Quien quiera cero riesgo, elige `multilane`; quien elija los otros, asume el riesgo a cambio de menos ceremonia.

> **Jerarquía cuando los criterios chocan.** El **sprint** manda sobre el orden y las fronteras; el **presupuesto de contexto**, sobre el tamaño del change; la preferencia por **changes pequeño-medio** afina dentro de lo que esos dos permiten —nunca parte una fase si con ello rompe una frontera de sprint o saca una HU de su ventana—; y el **modo de paralelismo** reparte lo que los tres anteriores ya decidieron, sin cambiar qué entra en cada fase. Cuando chocan, se registra el conflicto en lugar de romper lo ya decidido.

---

## 4. Documentos del proyecto

Cada fase produce documentos que son la entrada de la siguiente. El humano revisa y aprueba cada documento antes del handoff.

> **Versionado y sello temporal (todos los documentos AIDD).** Cada documento generado por un skill `aidd` lleva, justo bajo el título, una línea de sello: `> **Versión N** · **Generado:** YYYY-MM-DD HH:MM TZ`. La **versión se incrementa en cada regeneración** del documento y la **fecha-hora es real**. No la escribe el modelo (no inventa versión ni hora): la estampa el script `${CLAUDE_PLUGIN_ROOT}/scripts/stamp_doc.py`, que cada skill ejecuta tras escribir el `.md` y antes de renderizar la vista HTML/Excel. La versión persiste en el sidecar `docs/.aidd-doc-meta.json` (sobrevive a que el `.md` se reescriba). La vista HTML de `booster-docs` muestra el sello en la cabecera.

```
docs/
├── cliente-requisitos.md            ← Fase 0 — brief del cliente
├── requisitos.md                    ← AI Architect / Fase 1
├── mapa-historias-usuario.md        ← AI Architect / Fase 1
├── detalle-historias-usuario.md     ← AI Architect / Fase 1
├── plan-revision-hu.md              ← aidd hu-review-plan (opcional) · fuente de verdad
├── xlsx/plan-revision-hu.xlsx       ← aidd hu-review-plan (opcional) · Excel de revisión de HU
├── arquitectura-base-prototipo.md   ← AI Architect / Fase 2
├── guia-estilos.md                  ← AI Architect / Fase 2
├── propuesta-arquitectura-base.md   ← AI Architect / Fase 2
├── arquitectura-base.md             ← AI Architect / Fase 2
├── roadmap.md                       ← aisdd roadmap (AI Lead) / Fase 3
├── prompts-roadmap-native-ai.md     ← aisdd roadmap (AI Lead) / Fase 3
├── planificacion-proyecto.md        ← AI Delivery Manager / Fase 3.5 (aidd project-plan)
├── sprint-plan.md                   ← AI Delivery Manager / Fase 3.5 (aidd sprint-planning)
└── jira-sync.md                     ← integración Jira (opcional) — mapeo HU ↔ change ↔ issue

AGENTS.md                            ← aisdd init — registro de comandos del skill

openspec/
├── config.yaml                      ← project_context (init) + sección roadmap (roadmap)
├── specs/                           ← specs consolidadas
├── changes/
│   └── <change>/
│       ├── proposal.md              ← aisdd open change
│       ├── design.md                ← aisdd open change
│       ├── spec.md (uno o varios)   ← aisdd open change
│       └── decisions.md             ← pre-flight de dudas (open / implement)
└── audit/
    └── YYYY-MM.jsonl                ← auditoría append-only (todos los comandos)
```

> **Cambios respecto a la versión OpenSpec directa:** `sprints-desarrollo.md` se sustituye por `docs/roadmap.md`, y `prompts_a_ejecutar.md` por `docs/prompts-roadmap-native-ai.md` (ambos generados por `aisdd roadmap`). Aparecen tres artefactos nuevos: `decisions.md` por change, `AGENTS.md` y la auditoría `openspec/audit/`.

---

## 5. Fases en detalle

### Fase 0 — Inicialización del proyecto

**Propósito:** Preparar el entorno antes de que ningún rol de IA produzca contenido. La ejecuta el humano de forma colaborativa con la IA.

**Tareas:**
- Recopilar toda la documentación, código y modelos de datos del cliente
- Inicializar repositorio git con estructura de carpetas base
- Crear `AGENTS.md` con contexto, stack y convenciones del proyecto (fichero de contexto genérico para cualquier agente IA)
- Definir el stack tecnológico y las restricciones no negociables
- Capturar el brief en `docs/cliente-requisitos.md`
- Verificar disponibilidad de Node.js/npm y de los skills `aidd-*` (planificación/diseño), `aisdd-specs`, `booster-ux` y `booster-uml`

**Criterio de salida:** Existe `cliente-requisitos.md` con suficiente contexto para que el AI Architect arranque sin preguntas. Los skills auxiliares están instalados o se conoce dónde instalarlos.

**Comando AIDD:**
```text
aidd client-requirements
```

`aidd client-requirements` actúa como consultor técnico experto: recopila contexto, stack, restricciones y documentación aportada, ejecuta un **pre-flight de dudas** (máx. 7) con las preguntas clave, identifica riesgos y ambigüedades, y genera `docs/cliente-requisitos.md` con suficiente contexto para que la Fase 1 arranque sin preguntas. Opcionalmente crea/actualiza `AGENTS.md` con contexto, stack y convenciones del proyecto.

---

### Fase 1 — Definición (AI Architect) · DEFINITION

**Propósito:** Transformar el brief del cliente en documentos formales que sirvan de contexto estructurado para todos los agentes IA del proyecto. Sin esta fase completa y aprobada, no se puede diseñar ni implementar nada.

**Entradas:** `cliente-requisitos.md` + documentación/código/datos del cliente
**Salidas:** `requisitos.md`, `mapa-historias-usuario.md`, `detalle-historias-usuario.md`

#### Paso 1.1 — Requisitos formales

**Comando AIDD:**
```text
aidd requirements
```

`aidd requirements` actúa como Product Owner experto en el dominio: lee `docs/cliente-requisitos.md` y genera `docs/requisitos.md` con descripción del sistema y objetivos, usuarios y roles con permisos, requisitos funcionales trazables (RF-XX), requisitos no funcionales (NFR-XX: rendimiento, seguridad, RGPD, accesibilidad), restricciones técnicas no negociables, alcance dentro/fuera y variables de entorno. Pre-flight de dudas (máx. 7); decisiones registradas en el propio documento.

#### Paso 1.2 — Mapa de historias de usuario

**Comando AIDD:**
```text
aidd user-stories
```

`aidd user-stories` actúa como Product Owner experto: lee `docs/requisitos.md` y genera `docs/mapa-historias-usuario.md` con las personas/roles, un backbone de actividades principales, historias agrupadas por fases (F0 foundation, F1, F2...), cada una con ID único en formato "Como [rol], quiero [acción] para [objetivo]", criterio de salida por fase, priorización MoSCoW para Fase 1 y referencia al RF correspondiente. Opcionalmente admite acotar el número de fases o un mínimo (`aidd user-stories fases=N` / `fases>=N`).

> **F0 foundation (fase del mapa) = habilitadores, no núcleo funcional.** La fase F0 agrupa las **historias habilitadoras** (walking skeleton: esqueleto de auth, modelo de datos base, shell de navegación, infra transversal); **ninguna historia que entregue valor funcional al usuario final va en F0** — eso es F1+. Prueba: si un usuario final "la usaría" para lograr su objetivo, es F1. **Ojo con el nombre:** esta fase F0 **no es** el change `foundation` del roadmap (Fase 3), que es *scaffolding puro* derivado de la arquitectura y sin funcionalidad; están alineados pero no son un mapeo 1:1.

#### Paso 1.3 — Detalle de historias de usuario

**Comando AIDD:**
```text
aidd user-story-details
```

`aidd user-story-details` actúa como Product Owner y especialista en criterios de aceptación: lee `docs/requisitos.md` y `docs/mapa-historias-usuario.md` y genera `docs/detalle-historias-usuario.md` con, por cada historia, descripción completa, prioridad dentro de su fase, estimación orientativa con la escala de tallas (1 d = jornada de 8 h: XS = 0,5 d · S = 1,5 d · M = 3 d · L = 5 d · XL = 8 d), criterios de aceptación verificables (Dado/Cuando/Entonces), marca de criterios **imprescindibles** (esenciales para aceptar la historia; no confundir con "bloqueante", que es un impedimento real y solo aplica a preguntas/dependencias sin resolver) y notas técnicas y dependencias.

**Criterio de salida de Fase 1:** Cada requisito tiene al menos una historia. Cada historia tiene criterios de aceptación verificables. Humano ha aprobado los tres documentos.

#### Paso 1.4 — Planificación de la revisión de HU (opcional)

**Comando AIDD:**
```text
aidd hu-review-plan
```

`aidd hu-review-plan` consolida `docs/mapa-historias-usuario.md` y `docs/detalle-historias-usuario.md` en un **Excel de planificación** (`docs/xlsx/plan-revision-hu.xlsx`) con cuatro pestañas: **Detalle HU** (todas las HU combinadas, con las palabras *Como/quiero/para* en negrita), **Dashboard** (KPIs y gráficas: HU pendientes de cerrar, bloqueadas, por fase/persona/prioridad), **Leyenda** (significado de campos codificados como `Persona` P1/P5 o `GAP`) y **Gantt** (planificación de la revisión: kickoff, semana 1 de revisión de la documentación del cliente y resto del periodo con reuniones **funcionales** con negocio y **técnicas** con TI, con detalle por HU). El `docs/plan-revision-hu.md` es la fuente de verdad; el Excel es el entregable rico.

Es la **antesala de la Fase 3.5**: `aidd sprint-planning` lee `plan-revision-hu.md` para no planificar por libre — solo compromete en sprint las HU que la revisión ha dejado cerradas/validadas y reutiliza las personas implicadas en la revisión para asignar el sprint y, al volcar a Jira, el *assignee* de cada Story. Skill autónomo (openpyxl se autoinstala si falta).

---

### Fase 2 — Diseño (AI Architect) · DEFINITION

**Propósito:** Traducir las historias en arquitectura visual y técnica validable. Incluye la construcción del prototipo para validación con cliente, la guía de estilos, la propuesta de arquitectura y la arquitectura técnica definitiva, que será el insumo principal del roadmap.

**Entradas:** `requisitos.md`, `mapa-historias-usuario.md`, `detalle-historias-usuario.md`
**Salidas:** `arquitectura-base-prototipo.md`, `guia-estilos.md`, `propuesta-arquitectura-base.md`, `arquitectura-base.md`

#### Paso 2.1 — Arquitectura del prototipo

El prototipo sirve para validar con el cliente antes de invertir en la arquitectura real. **Todo se mockea.**

**Comando AIDD:**
```text
aidd prototype-architecture
```

`aidd prototype-architecture` actúa como Product Owner y arquitecto de software: lee `docs/mapa-historias-usuario.md` y `docs/detalle-historias-usuario.md` y genera `docs/arquitectura-base-prototipo.md` con stack mínimo (prioriza velocidad), componentes y módulos de los flujos principales, pantallas o endpoints clave, estrategia de mocks (todo se simula), datos de ejemplo del dominio, supuestos y exclusiones, y pasos mínimos de implementación. La demo debe poder recorrerse de punta a punta sin bloqueos.

#### Paso 2.2 — Implementación del prototipo

**Comando AIDD:**
```text
aidd prototype
```

`aidd prototype` es un skill-puente: lee `docs/arquitectura-base-prototipo.md`, identifica las pantallas y flujos de la demo y **redirige a `booster-ux`** (una invocación por pantalla), pasándole `docs/guia-estilos.md` como referencia de estilo si existe. **No escribe código por sí mismo.** Si `booster-ux` no está disponible, entrega un prompt de implementación manual de la demo (código funcional + datos mock + README) como alternativa. Mockea TODO lo externo: APIs, BD, auth, notificaciones e integraciones.

> **Punto de validación humana:** El humano presenta el prototipo al cliente, recoge feedback y actualiza `cliente-requisitos.md` antes de continuar. **Si hay cambios significativos, se vuelve al Paso 1.1.**

#### Paso 2.3 — Guía de estilos y propuesta de arquitectura

El paso 2.3 se cubre con **dos skills independientes** (se pueden ejecutar en cualquier orden):

```text
aidd style-guide
aidd architecture-proposal
```

`aidd style-guide` actúa como experto en diseño de producto y sistemas de diseño: lee `docs/detalle-historias-usuario.md` y la referencia visual/marca y genera `docs/guia-estilos.md` con principios de diseño y UX, paleta de colores (hex), tipografía, espaciado, iconografía, design tokens CSS concretos, componentes base y pautas de uso, responsive y accesibilidad WCAG 2.1 AA, y estructura de pantallas y navegación. Opcionalmente extrae la identidad visual de un diseño en Figma.

`aidd architecture-proposal` actúa como experto en arquitectura de software: lee `docs/detalle-historias-usuario.md` y genera `docs/propuesta-arquitectura-base.md` con stack técnico recomendado y justificado, organización de módulos y capas, gestión de estado y flujo de datos, estrategia de testing, y consideraciones de seguridad y escalabilidad alineadas con las historias.

#### Paso 2.4 — Arquitectura técnica definitiva

El AI Architect consolida la arquitectura real del producto una vez validado el prototipo y cerrado el feedback del cliente. **Este documento es el insumo principal de `aisdd roadmap`.**

**Comando AIDD:**
```text
aidd architecture
```

`aidd architecture` actúa como arquitecto de software senior con enfoque de implementación: analiza como fuentes de verdad `docs/detalle-historias-usuario.md`, `docs/propuesta-arquitectura-base.md` y `docs/guia-estilos.md` (señalando y resolviendo cualquier conflicto entre ellas) y genera `docs/arquitectura-base.md` —implementable, sin contradicciones, con cada decisión explícita— con: objetivo y alcance; principios y decisiones arquitectónicas; estructura de la solución (árbol de carpetas real); descomposición por módulos/dominios; capas y responsabilidades; componentes base y relaciones; flujos de información; gestión de estado; navegación y endpoints; integraciones; seguridad, accesibilidad, observabilidad y rendimiento; escalabilidad, mantenibilidad y extensibilidad; y riesgos, supuestos y decisiones pendientes. Es el **insumo principal de `aisdd roadmap`**.

**Criterio de salida de Fase 2:** Prototipo validado por el cliente. Guía de estilos, propuesta de arquitectura y arquitectura técnica definitiva aprobadas. Requisitos y arquitectura en estado consumible por `aisdd roadmap`.

> **Nota sobre el framework de prompting:** A diferencia de la versión OpenSpec directa, aquí el Architect **no** escribe a mano un borrador de `prompts_a_ejecutar.md`. El framework de prompting (`docs/prompts-roadmap-native-ai.md`) lo genera `aisdd roadmap` en la Fase 3 a partir de estos documentos.

---

### Fase 3 — Inicialización y Roadmap (AI Lead) · DEFINITION → EXECUTION

**Propósito:** El AI Lead toma los documentos del AI Architect, inicializa Native AI Specs y fasea la ejecución con `aisdd roadmap`, ajustando la granularidad al presupuesto de contexto. Esta fase cierra DEFINITION y abre EXECUTION.

**Entradas:** `mapa-historias-usuario.md`, `detalle-historias-usuario.md`, `arquitectura-base.md`, `guia-estilos.md`
**Salidas:** OpenSpec inicializado, `AGENTS.md` con comandos registrados, `docs/roadmap.md`, `docs/prompts-roadmap-native-ai.md`, sección `roadmap` en `openspec/config.yaml`

#### Paso 3.1 — `aisdd init`

```text
aisdd init
```

El comando:
1. Comprueba si `openspec` está instalado; si no, instala `@fission-ai/openspec@latest`.
2. Ejecuta `openspec init`.
3. Comprueba la disponibilidad de `booster-ux` y `booster-uml`.
4. Pregunta si el proyecto es **nuevo** o **existente** (para existente, ver Fase 5).
5. Para proyecto existente, solicita las rutas de los markdowns funcionales/técnicos/de arquitectura y los vuelca a `openspec/config.yaml` (`project_context`).
6. Registra los comandos del skill en `AGENTS.md` dentro de un bloque idempotente `<!-- BEGIN/END aisdd-specs commands -->`.

**Criterio:** OpenSpec inicializado, dependencias verificadas, `AGENTS.md` actualizado.

#### Paso 3.2 — Presupuesto de contexto

Antes de fasear, el AI Lead resuelve el **presupuesto de contexto**, que determina cuántas fases tendrá el roadmap:

| Presupuesto | Contexto útil | Granularidad recomendada |
|---|---|---|
| `bajo` | hasta 64k tokens | **6-12** fases pequeñas y estrechas |
| `medio` | 64k – 200k tokens | **4-8** fases equilibradas |
| `alto` | más de 200k tokens | **3-6** fases más amplias (sin mezclar objetivos no relacionados) |

Reglas de resolución:
1. Si el usuario indica el modelo o el límite de tokens, se usa.
2. Si la plataforma expone el modelo, sirve de pista.
3. Si no hay dato fiable, se asume `medio`.

Y se **suman fases** (aunque el modelo sea `alto`) cuando hay mucho volumen documental, migraciones, seguridad/permisos, integraciones externas o refactor transversal.

#### Paso 3.3 — `aisdd roadmap`

```text
aisdd roadmap
```

El comando genera, sin tocar todavía ningún change de OpenSpec:

- **`docs/roadmap.md`** — presupuesto de contexto asumido y justificación, complejidad estimada, fases ordenadas con objetivo, alcance/exclusiones, dependencias, entregables OpenSpec esperados, criterios de cierre y riesgo de contexto por fase.
- **`docs/prompts-roadmap-native-ai.md`** — los prompts a ejecutar hasta finalizar el desarrollo, **usando exclusivamente** los comandos del skill:
  - `aisdd open change <what-you-want-to-build>`
  - `aisdd implement change <what-you-want-to-build>`
  - `aisdd close change <what-you-want-to-build>`
  
  Para cada fase, el documento indica qué documentos/secciones pasar al modelo, qué partes del código son relevantes, qué **no** incluir todavía para no contaminar contexto, y cuándo conviene dividir una fase en varios changes.
- **Sección `roadmap` en `openspec/config.yaml`** — índice navegable: `context_budget`, `complexity`, rutas de docs y lista ordenada de fases con `id`, `name`, `objective`, `context_risk` y `change_hint` (slug sugerido para `aisdd open change`).

> `aisdd roadmap` **no** ejecuta `openspec new change`, **no** archiva cambios y **no** edita otros artefactos de `openspec/` aparte de `config.yaml`.

**Alineación con el sprint-plan.** Si existe `docs/sprint-plan.md` (Paso 3.5.2, que puede haberse ejecutado antes en modo degradado), `aisdd roadmap` lo lee y **fasea alineado a los sprints**: respeta su orden, corta las fases en fronteras de sprint, mantiene los changes de una HU dentro de la ventana de su sprint y no fasea HU no validadas; anota el sprint, las HU y el esfuerzo (humano e IA) en cada fase y documenta las discrepancias en una sección de **conflictos de alineación roadmap↔sprint**. Sin `sprint-plan.md`, fasea solo por presupuesto de contexto.

**Criterio de salida de Fase 3 (parcial):** Roadmap aprobado por el equipo técnico. Cada fase es abrible como uno o pocos changes con contexto acotado. `config.yaml` actualizado.

#### Paso 3.4 — Apertura del change `foundation` y del primer change funcional

**Conceptos clave del ciclo `aisdd-specs`:**

Un **change** es la unidad de trabajo: equivale a una fase del roadmap o feature acotada. El ciclo de vida tiene tres comandos operativos (más dos auxiliares):

| Comando | Quién lo ejecuta | Qué hace |
|---|---|---|
| `aisdd open change <slug>` | **AI Lead** (todos los changes) | **Pre-flight de dudas** (máx. 7) → `openspec new change` → genera `proposal.md`, `design.md` y `spec.md`, y persiste `decisions.md`. El Lead **valida** los specs antes de entregarlos. Opcionalmente dispara `booster-uml`. |
| `aisdd implement change <slug>` | AI Developer | **Pre-flight de dudas** (máx. 7) → `openspec instructions apply --change <slug>` → produce el código. |
| `aisdd close change <slug>` | Outcome Validator | `openspec archive <slug>` → cierra y archiva el change validado. |
| `aisdd uml <slug>` | Cualquier rol | Genera HTML de diagramas del change con `booster-uml` (entrada: `design.md`, `proposal.md`, `spec.md`). |
| `aisdd prototype-ux [<slug>]` | AI Architect / Developer | Genera prototipos UX con `booster-ux`, una vez por pantalla nueva del change. |

> **Decisión de proceso (ver #007):** el `open change` (propose) de **todos** los changes lo ejecuta el **AI Lead**, no el Developer. El Lead actúa como control de calidad de la especificación: abre el change, responde el pre-flight, valida los artefactos y solo entonces entrega specs validados al Developer. El Developer se limita a `implement change` + verificación + corrección de bugs.

**Diferencia clave respecto a OpenSpec directo:** `open change` e `implement change` ejecutan un **pre-flight de dudas** antes de actuar. El agente lee el contexto disponible, detecta ambigüedades reales (clasificadas como `bloqueante`, `preferencia` o `confirmacion`), pregunta al humano (máximo 7, priorizando bloqueantes) y persiste las respuestas en `openspec/changes/<slug>/decisions.md`. En modo no interactivo toma el default recomendado para no bloqueantes y se detiene ante bloqueantes sin default seguro.

---

**Change `foundation`** — siempre el primero, siempre especial. No implementa funcionalidad: establece la estructura base del proyecto (árbol de carpetas, configuración, archivos iniciales). Sin él, los changes funcionales no tienen base sobre la que operar. El AI Lead lo ejecuta completo:

> **No confundir con la fase F0 del mapa de HU.** Este change `foundation` es *scaffolding puro* derivado de `docs/arquitectura-base.md` (estructura y configuración, sin comportamiento). La **fase F0 foundation** del mapa de historias (Paso 1.2) es una agrupación de *producto* con las **historias habilitadoras** (auth base, modelo de datos, shell de navegación…). Este change materializa la estructura base; las historias habilitadoras de F0 se ejecutan como sus propios changes. El roadmap re-fasea todo por presupuesto de contexto, así que no hay correspondencia 1:1 entre fases del mapa y changes.

1. `aisdd open change foundation` — responde el pre-flight (verifica que la estructura propuesta coincide con `arquitectura-base.md`)
2. Revisar y ajustar los artefactos generados (`proposal.md`, `design.md`, `spec.md`)
3. `aisdd implement change foundation`
4. Verificar el resultado: árbol de carpetas, archivos de configuración y estructura base correctos
5. `aisdd close change foundation`

**Primer change funcional** — el AI Lead abre y valida el primer change real (según `docs/roadmap.md` / `docs/prompts-roadmap-native-ai.md`) y entrega los specs validados al equipo:

1. `aisdd open change <primer-change>` usando el prompt de su fase en `docs/prompts-roadmap-native-ai.md`; responde el pre-flight de dudas
2. Revisar y validar los artefactos generados y `decisions.md` — son el material que recibirán los AI Developers
3. Handoff a AI Developers: el desarrollo puede comenzar (el Developer ejecutará `aisdd implement change`)

> A partir de aquí, el AI Lead repite el `open change` + validación para **cada** change del roadmap, normalmente cuando el Outcome Validator archiva el anterior y lanza el siguiente.

**Criterio de salida de Fase 3:** Roadmap aprobado. OpenSpec inicializado y configurado. `AGENTS.md` registrado. Change `foundation` abierto, implementado y archivado. Primer change funcional abierto, validado y entregado a los AI Developers.

---

### Fase 3.5 — Planificación de entrega (AI Delivery Manager) · DEFINITION → EXECUTION

**Propósito:** Traducir el diseño aprobado y el roadmap consciente de contexto en un plan ejecutable por un equipo (humano + agentes): qué **recursos** hacen falta y en qué **orden temporal** se aborda el trabajo. Cubre la dimensión de gestión de proyecto/recursos que el SDD v3 no contemplaba. Es **opcional** pero recomendada cuando el desarrollo lo ejecuta un equipo humano que necesita planificar recursos y sprints (p. ej. un equipo Scrum).

**Entradas:** `arquitectura-base.md`, `mapa-historias-usuario.md`, `detalle-historias-usuario.md` (para recursos); `roadmap.md` + `planificacion-proyecto.md` + `detalle-historias-usuario.md` (para sprints)
**Salidas:** `docs/planificacion-proyecto.md`, `docs/sprint-plan.md`

> Capa **autónoma de OpenSpec** (skills `aidd-*`). No sustituye al `aisdd roadmap`: lo complementa. El roadmap fasea por presupuesto de contexto del modelo; esta fase añade recursos y calendario humano **sin romper ese faseado** (un sprint no parte un change).

#### Paso 3.5.1 — `aidd project-plan` (plan de recursos)

Puede ejecutarse en cuanto la Fase 2 está aprobada (no requiere el roadmap). El AI Delivery Manager genera `docs/planificacion-proyecto.md` con perfiles/equipo (mapeados a los roles SDD cuando aplica), software/licencias (open source vs coste, órdenes de magnitud), infraestructura/entornos, esfuerzo agregado con **doble estimación humano clásico vs IA** (a partir de XS/S/M/L/XL) y **KPIs de la diferencia** (ahorro en jornadas, % de reducción y factor de aceleración), dependencias y riesgos de recursos.

**Criterio:** Plan de recursos aprobado; el equipo sabe qué perfiles, licencias e infraestructura necesita.

#### Paso 3.5.2 — `aidd sprint-planning` (plan de sprints)

El AI Delivery Manager distribuye el trabajo en sprints, respetando dependencias y prerequisitos (F0 → F1 → F2) y la capacidad del equipo, y produce `docs/sprint-plan.md` con objetivo por sprint, unidades de trabajo completas (sin partir changes), asignación de perfiles, hitos y riesgos de planificación. Necesita `docs/planificacion-proyecto.md`; con `docs/roadmap.md` (Paso 3.3) planifica sobre los changes/fases del roadmap, pero **puede ejecutarse antes del roadmap en modo degradado** (planificando sobre las historias del mapa) y **re-ejecutarse después** para re-fasear con el roadmap ya hecho — sin recrear Stories en Jira: el re-faseado **mueve** HU entre sprints y gestiona sprints, jamás borra/recrea issues (las claves son permanentes).

**Criterio de salida de Fase 3.5:** Plan de recursos y plan de sprints aprobados por el equipo. El trabajo del roadmap queda repartido en iteraciones ejecutables por un equipo humano, con dependencias respetadas. La ejecución (Fase 4) sigue el orden de los sprints: el AI Lead abre cada change con `aisdd open change` según ese orden.

---

### Fase 4 — Apertura, Implementación y Validación por change · EXECUTION

**Propósito:** Producir el código de cada change de forma controlada y trazable. El **AI Lead** abre y valida los specs (`open change`); el **AI Developer** los implementa, verifica y corrige bugs (`implement change`); el **Outcome Validator** valida y archiva (`close change`). El Developer no improvisa decisiones de arquitectura ni abre changes.

**Entradas:** `docs/prompts-roadmap-native-ai.md`, `docs/roadmap.md`, `arquitectura-base.md`, `detalle-historias-usuario.md`, change activo en OpenSpec

#### Ciclo por change

```
AI Lead: copia el prompt de la fase de prompts-roadmap-native-ai.md
        │
        ▼
aisdd open change <slug>            ◄── lo ejecuta el AI LEAD
  └─ PRE-FLIGHT DE DUDAS (máx. 7) → decisions.md
  └─ openspec new change → proposal.md, design.md, spec.md
AI Lead revisa y VALIDA los specs generados y decisions.md
        │
        ▼  ── Handoff: specs validados ──► AI Developer ──
        │
AI Developer revisa los specs recibidos
aisdd implement change <slug>       ◄── lo ejecuta el AI DEVELOPER
  └─ PRE-FLIGHT DE DUDAS (máx. 7) → decisions.md
  └─ openspec instructions apply --change <slug>
        │
        ▼
AI Developer prueba manualmente (levanta la aplicación)
Corrige los bugs de implementación que identifique
(opcional: aisdd uml <slug> / aisdd prototype-ux <slug>)
        │
        ▼  ── Handoff al Outcome Validator ──
        │
Outcome Validator valida (técnico + funcional + trazabilidad)
Diagnostica la naturaleza de cada problema
        │
   ┌────┴──────────────────┐
   │                       │
 OK ✓                   KO ✗
   │                       │
   │         ┌─────────────┼─────────────────────┐
   │         │             │                     │
   │   Problema de   Decisión técnica      Problema de spec
   │   implementación  no documentada      o arquitectónico
   │         │             │                     │
   │   → Dev corrige   → Se resuelve y     → Reporta al AI Lead
   │     (itera hasta    se registra en      Lead reabre/ajusta el
   │      OK)            decisions.md        change o escala al
   │                     El ciclo sigue      Architect
   ▼
Outcome Validator aprueba el Merge Request
        │
        ▼
aisdd close change <slug>   (openspec archive)
        │
        ▼
Outcome Validator lanza el siguiente change
        │
        ▼
AI Lead abre y valida el siguiente change (aisdd open change)
        │
        ▼  ── Handoff: specs validados ──► AI Developer ──
```

> **Regla de corte — qué merece tocar documentación.** El coste de una corrección debe ser proporcional a su alcance real. La pregunta no es "¿cambia el código?", sino **¿algún documento AIDD sellado queda diciendo algo falso?**
>
> - **Problema de implementación** — el spec es correcto y el código no lo cumple. Lo corrige el Developer iterando. No se toca ningún documento.
> - **Decisión técnica no documentada** — ningún documento fijaba ese detalle (una incompatibilidad de versiones descubierta al validar, un matiz visual que la guía de estilos no recoge). Se resuelve, se registra como entrada `Tipo: correccion` en el `decisions.md` del change, y el ciclo continúa: **no** se escala al Architect y **no** se vuelve a aplicar el change. Si además la corrección exige criterios o tareas nuevas en el change, la vía es `aisdd amend change`, que escribe ese delta —y solo ese— y lo implementa sin rehacer lo ya entregado.
> - **Contradicción documental** — un documento sellado afirma lo contrario de lo que ahora es cierto. Se corrige **ese** documento, y solo ese, y se re-sella con `stamp_doc.py`. La cadena completa hacia arriba (`cliente-requisitos.md` → `requisitos.md` → `propuesta-arquitectura-base.md` → `arquitectura-base.md`) solo se recorre cuando el cambio nace de una decisión del cliente sobre el alcance, no de un hallazgo técnico durante el desarrollo.

**Prompt de apertura** (lo ejecuta el AI Lead, extraído de `docs/prompts-roadmap-native-ai.md` para cada fase):

El bloque de cada fase en `docs/prompts-roadmap-native-ai.md` indica el contexto mínimo a pasar y el comando exacto a ejecutar. Su estructura típica:

```prompt
aisdd open change <slug-de-la-fase>

CONTEXTO A PASAR
[Documentos/secciones relevantes de esta fase — y qué NO incluir todavía]

OBJETIVO
[Qué debe quedar operativo al finalizar este change]

ENTREGABLES
[Endpoints, pantallas, modelos y servicios a implementar]

CRITERIOS DE ACEPTACIÓN BLOQUEANTES
[Criterios mínimos verificables para cerrar el change]
```

**Reparto de responsabilidades en el ciclo:**

- **AI Lead** — ejecuta `aisdd open change <slug>`, responde el pre-flight, revisa y **valida** los artefactos (`proposal.md`, `design.md`, `spec.md`, `decisions.md`) y entrega specs validados al Developer.
- **AI Developer** — recibe los specs validados, ejecuta `aisdd implement change <slug>` (responde su pre-flight antes de que se aplique el código), prueba end-to-end y **corrige los bugs de implementación que identifique**. No abre el change.
- **Outcome Validator** — valida (técnico + funcional + trazabilidad), aprueba el MR, ejecuta `aisdd close change <slug>` y habilita al AI Lead para abrir el siguiente change.

#### Enlace con Jira (opcional): HU vs change

Cuando la integración con Jira está configurada (sección `jira:` en `openspec/config.yaml` + MCP de Atlassian disponible), el ciclo por change mantiene sincronizados dos planos sin duplicar el seguimiento:

- **La HU es la unidad de entrega rastreable** → una **Story** en Jira (la crea `aidd sprint-planning`). Es lo estable: tiene criterios de aceptación y la valida el cliente.
- **El change es la unidad de ejecución**. Es lo volátil: lo fasea el presupuesto de contexto y **no es 1:1** con la HU (una HU puede necesitar varios changes; un change puede implementar varias HU).
- **Modelo híbrido por HU** (registro #010): si la HU se realiza con **un solo change**, los comandos operan **directamente sobre su Story** — sin sub-tarea (una sub-tarea 1:1 solo duplicaría la Story). Si la HU se reparte entre **2+ changes**, `aisdd open change` crea **una sub-tarea por change** bajo su Story, para progreso atómico. Un mismo change puede mezclar ambos modos.
- **Transiciones automáticas**: `implement change` mueve a *In Progress* las Stories de **todas** las HU que implementa (y la sub-tarea del change donde exista), **asignándolas** al usuario autenticado en el MCP (o al `assignee_override` si el MCP usa cuenta de servicio); `close change` las pasa a *Done* — una Story con sub-tareas, **solo cuando todas están Done** (una HU no se cierra a medias). `open change` no cambia estados: abrir es diseñar specs, no implementar.
- **Registro del enlace**: `docs/jira-sync.md` (mapa HU ↔ change ↔ claves de Jira) es la fuente de verdad operativa; cada change anota su(s) HU en `proposal.md` y el PR del change referencia la clave Jira (`ABC-123`). Detalle de comportamiento en el skill `aisdd-specs`, sección "Integración con Jira".
- **No intrusivo**: si no está configurada, todos los comandos funcionan igual y la sincronización se omite.

**Prompt de validación (Outcome Validator):**
```prompt
Actúa como QA técnico y funcional senior con capacidad de diagnóstico arquitectónico.

Valida completamente el change '<SLUG>'.

Documentos de referencia:
- Criterios de aceptación: [detalle-historias-usuario.md](docs/detalle-historias-usuario.md)
  historias: [IDs]
- Arquitectura esperada: [arquitectura-base.md](docs/arquitectura-base.md)
- Guía de estilos: [guia-estilos.md](docs/guia-estilos.md)
- Decisiones del change: openspec/changes/<SLUG>/decisions.md

Para cada criterio de aceptación:
1. Verifica que está implementado correctamente
2. Prueba el caso positivo y el negativo
3. Verifica que no hay regresiones en funcionalidad anterior

Revisión técnica:
- El código sigue los patrones de arquitectura-base.md
- Los estilos siguen guia-estilos.md
- No hay deuda técnica evidente ni malas prácticas

Trazabilidad:
- decisions.md refleja las decisiones reales tomadas en el pre-flight
- Existe entrada de auditoría del change en openspec/audit/

Diagnóstico de problemas — clasifica cada problema encontrado:

| Tipo | Criterio | Acción |
|---|---|---|
| Implementación | El código no funciona o no cumple un criterio | Devuelve al AI Developer con descripción, criterio que falla y evidencia |
| Spec del change | Los artefactos del change son incorrectos o ambiguos | Reporta al AI Lead para que reabra/re-proponga el change |
| Impacto en specs futuras | El comportamiento real del change afecta a changes siguientes | Reporta al AI Lead con análisis del impacto |
| Arquitectónico | El problema está en la arquitectura base, no en este change | Reporta al AI Lead para que escale al AI Architect |

Si todo está correcto:
- Aprueba el Merge Request
- Ejecuta: aisdd close change <SLUG>
- Lanza el siguiente change — habilita al AI Developer para el siguiente bloque
```

---

### Fase 5 — Onboarding de proyectos existentes

**Propósito:** Incorporar la metodología AI-Native en un proyecto que ya está en marcha. El reto es generar los documentos de contexto a partir del código existente sin interrumpir el desarrollo.

#### Estrategia

```
Proyecto existente (código + docs parciales)
        │
        ▼
Paso 1: Documentación inversa (AI Architect)
  Analiza el código y genera los documentos que faltan
        │
        ▼
Paso 2: Reconciliación (humano)
  Revisa discrepancias entre lo documentado y lo implementado
        │
        ▼
Paso 3: Inicialización (AI Lead)
  aisdd init  → responde "desarrollo ya existente"
                    · aporta rutas de docs funcionales/técnicos/arquitectura
                      (se vuelcan a config.yaml: project_context)
                    · analiza el código y siembra las SPECS BASE en
                      openspec/specs/<capability>/spec.md, con marcas
                      UNKNOWN y LEGACY, para revisión humana
  aisdd roadmap  → fasea el trabajo pendiente
        │
        ▼
Paso 4: Incorporación al flujo normal
  Toda nueva funcionalidad sigue el ciclo AI-Native, aplicando
  deltas SOBRE las specs base en vez de partir de cero
```

> **Ya no hace falta un change `legacy-sync`.** Antes se registraba el estado actual abriendo, implementando y cerrando un change de onboarding. Con `aisdd init` sembrando las specs base directamente, ese change sobraba: orquestaba un ciclo completo para no entregar nada, y confundía "fotografiar lo que hay" con "construir algo". El estado actual no es un cambio; es el punto de partida.

**Prompt de documentación inversa (AI Architect):**
```prompt
Actúa como arquitecto de software senior y Product Owner.

Analiza el código y la estructura del proyecto existente en este repositorio.
Genera los documentos que faltan para incorporar este proyecto al flujo AI-Native:

1. docs/requisitos.md — infiere los requisitos de las funcionalidades existentes
2. docs/mapa-historias-usuario.md — construye el mapa de lo ya implementado
3. docs/arquitectura-base.md — documenta la arquitectura real actual (no la ideal)

Para cada documento:
- Basa el contenido en lo que realmente existe en el código
- Marca con ⚠️ LEGACY las partes que no siguen buenas prácticas
- Marca con ❓ UNKNOWN lo que no puedes inferir con certeza
- Añade sección "Deuda técnica identificada"

Objetivo: fotografía fiel del estado actual, no del estado ideal.
```

Tras la reconciliación humana, el AI Lead ejecuta `aisdd init` (indicando proyecto existente y las rutas de estos documentos) y `aisdd roadmap` para fasear lo pendiente.

---

## 6. Configuración del entorno de trabajo

### AGENTS.md

`AGENTS.md` es el **ancla de contexto permanente** del proyecto y el fichero genérico que cualquier agente IA (Claude Code, Codex u otros) lee al abrir el repositorio. Sustituye al antiguo `CLAUDE.md` específico de un cliente para no atar la metodología a una herramienta concreta.

Tiene dos partes:

1. **Bloque manual** — contexto, stack, convenciones, roles y documentos clave. Lo redacta el humano en la Fase 0 y se mantiene a mano.
2. **Bloque auto-generado** — `aisdd init` registra los comandos del skill dentro de un bloque idempotente `<!-- BEGIN/END aisdd-specs commands -->`. No se edita a mano: se regenera en cada `aisdd init` sin tocar el resto del fichero.

```markdown
# [NOMBRE DEL PROYECTO] — AGENTS.md

## Contexto del proyecto
[Descripción breve del proyecto y su propósito de negocio]

## Stack tecnológico
[Listado del stack decidido con versiones]

## Restricciones no negociables
[Decisiones técnicas que no se cuestionan]

## Convenciones de código
- Idioma de comentarios: [idioma]
- Nomenclatura de variables: [convención]
- Nomenclatura de ficheros: [convención]

## Roles activos en este proyecto
- AI Architect: [modelo/instancia]
- AI Lead Front: [modelo/instancia]
- AI Lead Back: [modelo/instancia]
- AI Developer: [modelo/instancia]
- Outcome Validator: [modelo/instancia]

## Tooling de especificaciones
- Skill: aisdd-specs (comandos registrados en el bloque auto-generado de abajo)
- OpenSpec: @fission-ai/openspec
- Prototipos: booster-ux · Diagramas: booster-uml
- Presupuesto de contexto asumido: [bajo|medio|alto]

## Documentos clave
- Requisitos: docs/requisitos.md
- Historias: docs/mapa-historias-usuario.md
- Criterios: docs/detalle-historias-usuario.md
- Arquitectura: docs/arquitectura-base.md
- Roadmap: docs/roadmap.md
- Prompts del roadmap: docs/prompts-roadmap-native-ai.md

## Lo que NO se hace en este proyecto
[Lista explícita de exclusiones técnicas y funcionales]

<!-- BEGIN aisdd-specs commands (auto-generado, no editar a mano) -->
## Comandos aisdd-specs
[Lo escribe `aisdd init`: lista de comandos del skill]
<!-- END aisdd-specs commands -->
```

> **Compatibilidad con Claude Code:** si el equipo trabaja con Claude Code y quiere conservar `CLAUDE.md`, basta con que `CLAUDE.md` sea un alias que importe `AGENTS.md` (`@AGENTS.md`) o un fichero mínimo que apunte a él. El contenido vive en `AGENTS.md`; `CLAUDE.md` es opcional.

### Gestión de contexto entre sesiones

La IA no tiene memoria entre sesiones. Para garantizar coherencia:

1. **Iniciar cada sesión** referenciando los documentos del rol activo
2. **Nunca asumir** que la IA recuerda decisiones anteriores — incluirlas en el prompt o consultarlas en `decisions.md`
3. **Los documentos son la memoria** — si algo no está documentado, no existe
4. **El AGENTS.md** es el ancla de contexto persistente en cada sesión: aporta el contexto del proyecto y publica los comandos del skill
5. **Respeta el presupuesto de contexto** del roadmap — no arrastres documentos de fases futuras a la fase actual
6. **Ante cualquier duda**, el pre-flight de `aisdd` la captura y la persiste en `decisions.md`; el AI Developer no improvisa ni escala directamente al Lead

---

## 7. Estructura de carpetas recomendada

```
proyecto/
├── AGENTS.md                          # ancla de contexto + comandos aisdd-specs (bloque auto-generado)
├── docs/
│   ├── cliente-requisitos.md          # brief del cliente (Fase 0)
│   ├── requisitos.md                  # requisitos formales (Fase 1)
│   ├── mapa-historias-usuario.md      # mapa de historias (Fase 1)
│   ├── detalle-historias-usuario.md   # criterios de aceptación (Fase 1)
│   ├── plan-revision-hu.md            # revisión de HU, opcional (Paso 1.4 · aidd hu-review-plan)
│   ├── xlsx/plan-revision-hu.xlsx     # Excel de revisión de HU (Paso 1.4)
│   ├── arquitectura-base-prototipo.md # arquitectura demo (Fase 2)
│   ├── guia-estilos.md                # design system (Fase 2)
│   ├── propuesta-arquitectura-base.md # propuesta técnica (Fase 2)
│   ├── arquitectura-base.md           # arquitectura definitiva (Fase 2)
│   ├── roadmap.md                     # fases del desarrollo (Fase 3 · aisdd roadmap)
│   ├── prompts-roadmap-native-ai.md   # prompts por fase (Fase 3 · aisdd roadmap)
│   ├── planificacion-proyecto.md      # plan de recursos (Fase 3.5 · aidd project-plan)
│   ├── sprint-plan.md                 # plan de sprints (Fase 3.5 · aidd sprint-planning)
│   └── jira-sync.md                   # mapeo HU ↔ change ↔ issue Jira (opcional)
├── frontend/
├── backend/
└── openspec/                          # generado por OpenSpec
    ├── config.yaml                    # project_context + roadmap
    ├── specs/
    ├── changes/
    │   └── <change>/
    │       ├── proposal.md
    │       ├── design.md
    │       ├── spec.md
    │       └── decisions.md           # decisiones del pre-flight
    └── audit/
        └── YYYY-MM.jsonl              # auditoría append-only
```

---

## 8. Auditoría y trazabilidad

Cada comando `aisdd` escribe una entrada estructurada en `openspec/audit/YYYY-MM.jsonl` (un fichero por mes, append-only, JSON Lines). El objetivo es trazar **quién** ejecutó **qué** comando, sobre **qué input**, con **qué prompt y modelo**, y **qué decisión humana** se produjo.

**Qué se registra (por entrada):**
- `id`, `timestamp` (UTC ISO 8601), `command`, `change_id`
- `skill_version`, `prompt_version` (`<skill_version>:<command-slug>`)
- `model`, `platform`, `user` (email si la plataforma lo expone, si no `null`)
- `input_hash` + `input_files[]` con SHA-256 por fichero
- `output_hash` + `output_files[]` con SHA-256 por fichero
- `decisions[]` (solo para comandos con pre-flight): `slug`, `type`, `origen`, `decision`
- `status` (`ok | partial | aborted`), `errors[]`

**Qué NO se registra:** contenido literal de ficheros (solo hashes), texto libre de las dudas (vive en `decisions.md`), secretos/tokens/credenciales, diffs de código.

**Retención:** por defecto `365` días. Sobreescribible por proyecto, en este orden: `audit.retention_days` en `config.yaml` → `openspec/audit/.retention` → default `365`. La purga es por meses completos y nunca baja de `30` días. El JSONL es plano, listo para ingestar en Splunk, ELK o BigQuery.

> La auditoría es **obligatoria** y no bloqueante: si la escritura falla (disco/permisos), el comando reporta el fallo pero no anula el resultado funcional.

---

## 9. Checklist de calidad por fase

### Fase 1 — Definición
- [ ] Todos los requisitos tienen ID trazable (RF-XX, NFR-XX)
- [ ] Cada RF tiene al menos una historia de usuario
- [ ] Cada historia tiene criterios de aceptación verificables
- [ ] El alcance (dentro/fuera) está explícitamente definido
- [ ] Humano ha aprobado los tres documentos

### Fase 2 — Diseño
- [ ] El prototipo ha sido presentado y validado por el cliente
- [ ] El feedback del cliente está incorporado en `cliente-requisitos.md`
- [ ] La guía de estilos define design tokens CSS concretos
- [ ] La propuesta de arquitectura justifica cada decisión de stack
- [ ] `arquitectura-base.md` está completo y es consumible por `aisdd roadmap`
- [ ] Humano ha aprobado todos los documentos

### Fase 3 — Inicialización y Roadmap
- [ ] `aisdd init` ejecutado: OpenSpec inicializado, `booster-ux`/`booster-uml` verificados, `AGENTS.md` registrado
- [ ] Presupuesto de contexto resuelto y justificado (bajo/medio/alto)
- [ ] `aisdd roadmap` ejecutado: `docs/roadmap.md` y `docs/prompts-roadmap-native-ai.md` generados
- [ ] Sección `roadmap` en `openspec/config.yaml` con una entrada por fase
- [ ] Cada fase tiene criterio de cierre verificable y riesgo de contexto asignado
- [ ] Cada fase es abrible como uno o pocos changes con contexto acotado
- [ ] Change `foundation` abierto, implementado y archivado
- [ ] Primer change funcional abierto, validado por el AI Lead y entregado a AI Developers

### Por cada change (Fase 4)
- [ ] **[AI Lead]** Copia el prompt de la fase de `prompts-roadmap-native-ai.md` y ejecuta `aisdd open change <slug>`
- [ ] **[AI Lead]** Responde el pre-flight de dudas; las decisiones quedan en `decisions.md`
- [ ] **[AI Lead]** Revisa y **valida** los artefactos generados (`proposal.md`, `design.md`, `spec.md`) antes del handoff
- [ ] **[AI Lead]** Entrega los specs validados al AI Developer
- [ ] **[AI Developer]** Revisa los specs recibidos (`proposal.md`, `design.md`, `spec.md`, `decisions.md`)
- [ ] **[AI Developer]** Ejecuta `aisdd implement change <slug>` (responde su pre-flight) sin errores
- [ ] **[AI Developer]** Prueba manualmente end-to-end y corrige los bugs de implementación que identifique
- [ ] **[AI Developer]** Prepara la feature para integración — branch actualizado, sin conflictos, MR listo
- [ ] **[Outcome Validator]** Verifica todos los criterios de aceptación (funcional + técnico)
- [ ] **[Outcome Validator]** Verifica trazabilidad (`decisions.md` + entrada de auditoría)
- [ ] **[Outcome Validator]** Diagnostica y escala cualquier problema de spec o arquitectónico al AI Lead
- [ ] **[Outcome Validator]** Aprueba el Merge Request
- [ ] **[Outcome Validator]** Ejecuta `aisdd close change <slug>`
- [ ] **[Outcome Validator]** Lanza el siguiente change — habilita al **AI Lead** para abrir y validar el próximo change

---

## 10. Señales de alerta

| Señal | Causa probable | Acción |
|---|---|---|
| El código no refleja lo definido en los documentos | El AI Developer no leyó los documentos del change | Revisar el prompt de la fase en `prompts-roadmap-native-ai.md` y re-implementar |
| Los documentos se contradicen entre sí | No se hizo handoff explícito entre fases | Reconciliar documentos antes de continuar |
| El AI Developer toma decisiones de arquitectura | `arquitectura-base.md` tiene lagunas o ambigüedades | El AI Architect completa `arquitectura-base.md`; el AI Lead regenera el roadmap/prompts afectados |
| El cliente rechaza algo en demo avanzada | Se saltó la validación del prototipo | Volver a Fase 2 con el feedback recibido |
| La IA "recuerda" decisiones sin documentar | Se está usando el historial como memoria | Documentar la decisión en `decisions.md` y referenciarla en el prompt |
| Los changes se acumulan sin validar | El Outcome Validator no está activo | No avanzar al siguiente change hasta cerrar el actual con `aisdd close change` |
| El AI Developer improvisa componentes o patrones | Los prompts del roadmap son ambiguos | El AI Lead regenera `prompts-roadmap-native-ai.md` con `aisdd roadmap` |
| El Outcome Validator aprueba sin revisar el código | El rol está siendo ejecutado superficialmente | El Outcome Validator debe hacer revisión técnica real, no solo funcional |
| El AI Lead no desdobla Front/Back | El proyecto tiene complejidad en ambas capas | Separar en Front AI Lead + Back AI Lead con changes independientes |
| Un change arrastra demasiado contexto y se atasca | Fase demasiado grande para el presupuesto de contexto | Re-fasear con `aisdd roadmap` aumentando el número de fases / partiendo la fase en varios changes |
| El pre-flight pregunta lo que ya está documentado | No leyó `docs/`, specs previas o `decisions.md` | Asegurar que el contexto del rol está accesible; las dudas resueltas no se repreguntan |
| Falta la entrada de auditoría de un change | El comando falló al escribir o se ejecutó OpenSpec a mano | Revisar `openspec/audit/`; usar siempre los comandos `aisdd`, no OpenSpec directo |

---

## 11. Equivalencia con la versión OpenSpec directa

Para equipos que vienen de la metodología v2.0 (OpenSpec a pelo):

| Concepto v2.0 (OpenSpec directo) | Equivalente v3.0 (`aisdd-specs`) |
|---|---|
| `openspec init` | `aisdd init` (+ comprobación de boosters + registro en `AGENTS.md`) |
| Planificación de sprints (`sprints-desarrollo.md`) | `aisdd roadmap` → `docs/roadmap.md` (faseado por presupuesto de contexto) |
| — (planificación de recursos no existía) | **`aidd project-plan`** → `docs/planificacion-proyecto.md` (capa Delivery, v4) |
| Sprints calendarizados para equipo humano | **`aidd sprint-planning`** → `docs/sprint-plan.md` sobre el roadmap (capa Delivery, v4) |
| Framework de prompting (`prompts_a_ejecutar.md`) | `docs/prompts-roadmap-native-ai.md` (generado por `aisdd roadmap`) |
| `/opsx:propose [name]` | `aisdd open change <slug>` (**+ pre-flight de dudas** → `decisions.md`) |
| `/opsx:apply [name]` | `aisdd implement change <slug>` (**+ pre-flight de dudas**) |
| `/opsx:archive [name]` | `aisdd close change <slug>` |
| `/opsx:explore` (checklist go-live) | Revisión del roadmap (`docs/roadmap.md`) y criterios de cierre por fase |
| Artefactos del change (`proposal/design/tasks`) | `proposal.md`, `design.md`, `spec.md` + `decisions.md` |
| Diagramas (manual) | `aisdd uml <slug>` (booster-uml) |
| Prototipo (manual) | `aisdd prototype-ux [<slug>]` (booster-ux) |
| — (no existía) | **Auditoría** obligatoria en `openspec/audit/*.jsonl` |
| — (no existía) | **Pre-flight de dudas** (máx. 7) integrado en open/implement |
| — (no existía) | **Presupuesto de contexto** (bajo/medio/alto) que regula el faseado |

---

## 12. Registro de decisiones sobre el framework

Tabla de cambios aplicados o pendientes de decisión sobre esta metodología. Sirve como log para el responsable del framework.

| # | Área | Estado | Descripción del cambio | Justificación |
|---|---|---|---|---|
| 001 | Roles / Fase 2-3 | **Aplicado** | `arquitectura-base.md` lo produce el AI Architect en Fase 2 (Paso 2.4), no el AI Lead | La arquitectura es diseño técnico, no planificación. El AI Lead la recibe como input de `aisdd roadmap`. |
| 002 | Tooling | **Aplicado** | Toda operación sobre specs pasa por el skill `aisdd-specs` en vez de comandos OpenSpec directos | Añade pre-flight de dudas, presupuesto de contexto, prototipos/UML integrados y auditoría obligatoria, manteniendo OpenSpec por debajo. |
| 003 | Framework de prompting | **Aplicado** | El framework de prompting ya no es un borrador manual del Architect: lo genera `aisdd roadmap` como `docs/prompts-roadmap-native-ai.md` | Elimina el trabajo redundante del antiguo Paso 2.5. El roadmap consolida faseado y prompts en un solo comando reproducible y auditable. |
| 004 | Planificación | **Aplicado** | La planificación de sprints se sustituye por `aisdd roadmap`, condicionada por el presupuesto de contexto (bajo/medio/alto) | A menor ventana de contexto del modelo, más fases y más estrechas. Evita changes que arrastran demasiado contexto y se atascan. |
| 005 | Human-in-the-loop | **Aplicado** | El pre-flight de dudas (máx. 7, persistido en `decisions.md`) hace ejecutable y trazable la validación humana en `open change` e `implement change` | Convierte un principio en un paso operativo del comando. En modo no interactivo aplica defaults recomendados y se detiene ante bloqueantes. |
| 006 | Trazabilidad | **Aplicado** | Auditoría obligatoria en `openspec/audit/*.jsonl` con hashes de input/output, versión de prompt, modelo y decisiones | Permite auditar el uso del tooling IA (quién, qué, sobre qué, con qué modelo) sin almacenar contenido sensible. |
| 007 | Roles / Fase 4 | **Aplicado** | El AI Lead ejecuta el `open change` (propose) de **todos** los changes y entrega specs ya validados al Developer; el Developer solo hace `implement change` + verificación + corrección de los bugs que identifique. No abre changes | El Lead actúa como control de calidad de la especificación antes de que el Developer la consuma, reduciendo el riesgo de implementar sobre specs incorrectas. El coste de disponibilidad continua del Lead se asume a cambio de specs validadas; el pre-flight de dudas en `implement change` cubre las dudas residuales del Developer. |
| 008 | Roles / Fase 3.5 (v4) | **Aplicado** | Se añade el rol **AI Delivery Manager** y la **Fase 3.5 — Planificación de entrega**, con los skills `aidd project-plan` (`docs/planificacion-proyecto.md`) y `aidd sprint-planning` (`docs/sprint-plan.md`) | El SDD v3 faseaba por presupuesto de contexto (roadmap) pero no cubría recursos ni calendario para un equipo humano. Esta capa, autónoma de OpenSpec, traduce el roadmap a recursos y sprints sin romper el faseado por contexto (un sprint no parte un change). Hace la planificación AI-native consumible por un equipo Scrum. |
| 009 | Integración Jira / Fases 3.5 y 4 | **Superado (#010)** | Integración opcional con Jira (MCP de Atlassian). `aidd sprint-planning` vuelca los sprints y crea una **Story por HU**; `aisdd open change` creaba cada change como **sub-tarea** de la Story de su HU (siempre); `implement change` movía sub-tarea + Story a *In Progress*; `close change` pasaba la sub-tarea a *Done* y la Story a *Done* solo cuando **todas** sus sub-tareas lo están. Enlace en `docs/jira-sync.md` + sección `jira:` en `openspec/config.yaml` | La **HU** es la unidad de entrega rastreable y el **change** la unidad de ejecución. El detalle "sub-tarea siempre" queda superado por el modelo híbrido del registro #010; el resto (Stories por HU, enlace, opcionalidad) sigue vigente. |
| 010 | Integración Jira / Fase 4 | **Aplicado** | **Modelo híbrido por HU**: si una HU se realiza con un **solo change**, los comandos operan **directamente sobre su Story** (sin sub-tarea); si se reparte entre **2+ changes**, cada change es una **sub-tarea** bajo su Story (Done de la Story solo cuando todas están Done). Un change que implementa varias HU mueve las Stories de **todas** ellas. `open change` no cambia estados (abrir es diseñar specs); el modo se resuelve en el momento del comando (un re-faseado que reparta una HU crea sub-tareas solo para los changes nuevos) | La sub-tarea 1:1 duplicaba la Story sin aportar información (ruido en el board) y el modelo anterior solo movía la Story de la HU "principal", dejando sin reflejo el avance de las HU secundarias de un change. El híbrido conserva el progreso atómico exactamente donde aporta (HU repartida) y el Done-condicionado, con un board que refleja el avance real de cada HU. |
| 011 | Fase 4 / Correcciones | **Aplicado** | Se añade una **tercera rama** al diagnóstico del Outcome Validator: **decisión técnica no documentada**, que se resuelve dentro del change (entrada `Tipo: correccion` en `decisions.md`) sin escalar al Architect, sin reescribir los specs y sin volver a aplicar el change. La acompaña una **regla de corte** explícita: un documento AIDD solo se corrige cuando la decisión lo deja **desmentido**, y solo se corrige ese documento. `correccion` se suma a los tipos de `decisions.md` y al esquema de auditoría | El árbol de diagnóstico era binario (implementación vs spec/arquitectura), así que un detalle que ningún documento había fijado —una incompatibilidad de versiones descubierta al validar, un matiz visual fuera de la guía de estilos— caía por defecto en la rama cara: revisar la arquitectura, reescribir los specs y re-aplicar el change, con riesgo de pisar código ya escrito. La tercera rama hace el coste de la corrección proporcional a su alcance real conservando la trazabilidad mínima en `decisions.md`; el tipo propio la hace **contable** en `openspec/audit/*.jsonl` (correcciones por change es un indicador de la calidad de los specs, consumible por `aidd-metrics`). |
| 012 | Fase 4 / Correcciones | **Aplicado** | Se añade el skill **`aisdd-amend`** (`aisdd amend change [descripcion]`): el usuario describe una modificación, el skill escribe el delta en los artefactos del change ya abierto (criterios en `spec.md`, tareas nuevas en `tasks.md`, entrada `Tipo: correccion` en `decisions.md`) e implementa **solo ese delta**, sin re-ejecutar `openspec instructions apply`. Toma una **baseline de build y tests antes de tocar nada** para separar con evidencia lo que rompe la enmienda de lo que ya estaba roto. Asume la documentación AIDD al día (no la valida) y no reconcilia cambios manuales del working tree | El registro #011 dio el criterio para clasificar correcciones, pero no una vía de ejecución: una corrección que además exigía tocar los specs del change se quedaba sin herramienta, y el humano acababa re-aplicando el change entero sobre un árbol ya implementado. La baseline resuelve el problema de fondo: el agente no conoce el trabajo manual previo, así que la única forma honesta de afirmar "no hay regresiones" es medir antes y después en lugar de suponerlo. |
| 013 | Medicion / Fase 4 | **Aplicado** | `aidd-metrics` deja de ser ciego a AISDD: lee `openspec/audit/*.jsonl` (opcional, con `--audit`/`--no-audit`, y degrada sin error si no existe) y añade a `docs/kpis-ia.md` las **correcciones por change**, el **porcentaje de decisiones que la IA resolvió sin preguntar** y el **lead time real `open change` -> `close change`** | El informe medía velocidad (tiempo atendido, churn, código entregado) pero declaraba él mismo que "velocidad sin calidad es media foto". El eje de calidad ya estaba escrito en la auditoría desde el registro #011 y nadie lo leía. Las correcciones son retrabajo de **especificación**, complementario al churn (retrabajo de **código**): churn alto con correcciones bajas es refactor legítimo; correcciones altas con churn bajo significa specs flojas que alguien absorbió adivinando. El coste fue un parser y dos tablas; la alternativa era instrumentar una fuente nueva para un dato que ya existía. |
