# Native AI · AIDD-SDD — Metodología AI-Native (AI Driven Development + Spec-Driven Development)
**Versión:** 4.0
**Fecha:** 2026-06-22
**Base de tooling:** skills **AIDD** (`aidd-*` — planificación, diseño y entrega) + skill **native-ai-specs** (OpenSpec — ejecución) + **boosters** compartidos (`booster-ux` prototipos, `booster-uml` diagramas, `booster-docs` vistas HTML de los documentos de planificación).

> **Terminología (importante).** Tres conceptos que conviven y NO son lo mismo:
> - **SDD** (*Spec-Driven Development*) — la **metodología**: proceso, roles y fases. El "cómo se trabaja" (este documento).
> - **AIDD** (*AI Driven Development*) — el **skill set** que automatiza la **planificación, el diseño y la entrega** (Fases 0-2 y 3.5). Comandos `aidd *`. Cada comando aplica el prompt del paso; ejecutarlo equivale a lanzar ese prompt a mano.
> - **native-ai-specs** — el **skill set** de **ejecución** sobre OpenSpec (Fases 3 y 4+). Comandos `native-ai *`.
>
> **Novedad v4.** (1) Las Fases 0-2, antes descritas como prompts manuales del AI Architect, ahora se ejecutan con los comandos `aidd` (mismo proceso, empaquetado en skills). (2) Se añade un quinto rol, **AI Delivery Manager**, y la **Fase 3.5**, que traduce el roadmap en un **plan de recursos** (`aidd project-plan` → `docs/planificacion-proyecto.md`) y un **plan de sprints** (`aidd sprint-planning` → `docs/sprint-plan.md`), consumible por un equipo Scrum. Ver Fase 3.5 y registro #008.

---

## 1. Filosofía

AI-Native Development no es usar la IA como un asistente que escribe código más rápido. Es un modelo de trabajo donde **la IA generativa es parte estructural del proceso**, no una herramienta auxiliar, y el humano actúa como **director de orquesta**: aprueba, decide y valida en cada transición.

> **La especificación como motor del desarrollo:** transformamos los requisitos del cliente en contexto estructurado que los agentes IA pueden procesar de forma consistente. Sin especificación, no hay implementación.

El objetivo es garantizar **coherencia** entre lo que se define, lo que se diseña y lo que se implementa, evitando la deriva habitual donde el código se aleja de los requisitos con el paso de los sprints.

En esta versión, toda la operación sobre especificaciones se canaliza a través del skill **`native-ai-specs`**, que envuelve OpenSpec con tres capas adicionales:

1. **Pre-flight de dudas** — antes de abrir o implementar un change, el agente resuelve ambigüedades reales con el humano (máximo 7 preguntas) y las persiste en `decisions.md`. El *human-in-the-loop* deja de ser una recomendación: es un paso ejecutable del comando.
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
| **Trazabilidad auditable** | Cada comando `native-ai` registra qué se ejecutó, sobre qué input, con qué modelo y qué decidió el humano |

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
  → native-ai init  +  native-ai roadmap
  AI Delivery Manager
  → aidd project-plan + aidd sprint-planning  (plan de recursos + plan de sprints)
      │
      ▼  (aprobación humana)
EXECUTION PHASE  ◄─────────────────────────────── KO ─┐
  Back AI Lead  (open change → specs validados) ──► Back AI Dev
  Front AI Lead (open change → specs validados) ──► Front AI Dev
  AI Dev: implement change + verificación + fix bugs   │
      │                                                │
      ▼  (por cada change)                             │
VALIDATION PHASE ──────────────────────────────────────┘
  Outcome Validator
  → Validación técnica + funcional
  → Aprobación de Merge Request
  → native-ai close change
  → Entrega al cliente
      │
      ▼ (OK)
  Siguiente change ──► AI Lead (native-ai open change) ──► AI Dev
```

---

## 3. Roles y responsabilidades

La metodología define cinco roles con responsabilidades diferenciadas. Cada uno opera con contexto acotado a su fase. La columna de comandos indica qué comandos ejecuta cada rol (`native-ai` para AI Lead/Developer/Outcome Validator; `aidd` para el AI Delivery Manager de la capa de planificación de entrega).

### AI Architect

El rol de mayor nivel conceptual. Combina Product Owner y arquitecto de producto. **No implementa código.**

| Responsabilidad | Detalle |
|---|---|
| **Extrae y documenta reglas de negocio** | Transforma el brief del cliente en requisitos formales trazables |
| **Define proceso e integraciones** | Identifica qué sistemas externos intervienen y cómo |
| **Genera el prototipo mockeado** | Construye la demo para validación con el cliente. Puede apoyarse en `native-ai prototype-ux` (booster-ux) para las pantallas clave |
| **Genera guía de estilos + propuesta de arquitectura** | Base visual y estructural para el AI Lead y los AI Developers |
| **Genera la arquitectura técnica definitiva** | Produce `arquitectura-base.md` — documento implementable con decisiones explícitas, árbol de carpetas real y responsabilidades por capa. Es el insumo principal de `native-ai roadmap` |
| **Aporta el material para el roadmap** | Deja requisitos y arquitectura en estado consumible por el AI Lead para fasear con `native-ai roadmap` |

> El AI Architect ya **no** produce el borrador del framework de prompting a mano: en esta versión ese artefacto (`docs/prompts-roadmap-native-ai.md`) lo genera el comando `native-ai roadmap` a partir de sus documentos. El Architect garantiza que requisitos y arquitectura están completos para que el roadmap salga coherente.

### AI Lead (Front / Back)

En proyectos full stack, el AI Lead se desdobla en **Front AI Lead** y **Back AI Lead**, cada uno responsable de su capa. **No implementa código.**

| Responsabilidad | Comandos / Detalle |
|---|---|
| **Inicializa Native AI Specs** | Ejecuta `native-ai init`: instala/verifica OpenSpec, comprueba `booster-ux`/`booster-uml`, registra los comandos en `AGENTS.md` y vuelca el contexto inicial a `openspec/config.yaml` |
| **Fasea el desarrollo** | Ejecuta `native-ai roadmap`: genera `docs/roadmap.md`, `docs/prompts-roadmap-native-ai.md` y la sección `roadmap` de `config.yaml`, ajustando granularidad al presupuesto de contexto |
| **Define componentes reutilizables (Tools)** | Identifica abstracciones comunes que los AI Developers pueden reutilizar; las refleja en los prompts del roadmap |
| **Cierra foundation** | Ejecuta el ciclo `open change` → `implement change` → `close change` de `foundation` para dejar la base del proyecto operativa |
| **Abre y valida los specs de TODOS los changes** | Ejecuta `native-ai open change <slug>` de cada change del roadmap, participa en el **pre-flight de dudas**, revisa y valida los artefactos generados (`proposal.md`, `design.md`, `spec.md`, `decisions.md`) y solo entrega specs ya validados al AI Developer. Es el control de calidad de la especificación antes de que se implemente |
| **Soporte directo al Dev Team** | Resuelve dudas técnicas y desbloqueos durante la implementación |
| **Gestiona ajustes de spec** | Si el Outcome Validator reporta un problema de spec, reabre/ajusta el change afectado y, si procede, regenera el roadmap o los prompts |
| **Escala al AI Architect si es necesario** | Si el problema es arquitectónico de fondo, lo traslada al Architect para que corrija desde el origen |

### AI Developer (Front / Back)

Implementa el código a partir de los specs **ya abiertos y validados por el AI Lead**. **No abre changes. No toma decisiones de arquitectura. No habla con el Lead directamente.**

| Responsabilidad | Comandos / Detalle |
|---|---|
| **Recibe los specs validados del change** | El AI Lead le entrega el change ya abierto con sus artefactos validados (`proposal.md`, `design.md`, `spec.md`, `decisions.md`). El Developer **no** ejecuta `native-ai open change` |
| **Revisa los artefactos recibidos** | Lee y comprende `proposal.md`, `design.md`, los `spec.md` y `decisions.md` antes de implementar |
| **Lanza la implementación** | Ejecuta `native-ai implement change <slug>` (incluye su propio pre-flight de dudas antes de tocar código; las dudas de spec o arquitectura las eleva, no las inventa) |
| **Genera UML/prototipos si aplica** | Puede ejecutar `native-ai uml <slug>` y `native-ai prototype-ux <slug>` para documentar visualmente el change |
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
| **Diagnostica la naturaleza del problema** | Determina si un problema es de implementación (→ Dev), de spec (→ Lead) o arquitectónico (→ Lead para escalar al Architect) |
| **Devuelve al AI Developer** | Solo para problemas de implementación — con descripción, criterio que falla y evidencia |
| **Reporta al AI Lead** | Cuando detecta problemas de spec o arquitectónicos que superan el scope del Developer |
| **Aprobación de Merge Requests** | Es la firma final antes de que el change se integre en la rama principal |
| **Archiva el change validado** | Ejecuta `native-ai close change <slug>` (envuelve `openspec archive`) |
| **Lanza el siguiente change** | Tras archivar, habilita al **AI Lead** para que abra y valide el siguiente change (`native-ai open change`) y lo entregue al Developer |

### AI Delivery Manager

Rol de planificación de entrega (añadido en v4). Traduce el diseño y el roadmap a un plan ejecutable por un equipo (humano + agentes): **recursos** y **calendario**. **No implementa código ni toma decisiones de arquitectura.** Opera con los skills `aidd` de la capa de planificación, **autónomos de OpenSpec**.

| Responsabilidad | Comandos / Detalle |
|---|---|
| **Genera el plan de recursos** | Ejecuta `aidd project-plan` en cuanto el diseño (Fase 2) está aprobado: produce `docs/planificacion-proyecto.md` con perfiles/equipo (mapeados a los roles SDD cuando aplica), software/licencias, infraestructura/entornos, esfuerzo agregado (a partir de S/M/L), dependencias y riesgos de recursos, derivados de `arquitectura-base.md` y las historias |
| **Distribuye el trabajo en sprints** | Ejecuta `aidd sprint-planning` cuando existe `docs/roadmap.md`: produce `docs/sprint-plan.md` agrupando los changes/fases en sprints con objetivo, capacidad, asignación de perfiles y dependencias respetadas |
| **Respeta el faseado por contexto** | No parte un change para encajarlo en un sprint; un sprint contiene changes/historias completos. El roadmap (presupuesto de contexto) manda sobre el calendario |
| **Hace consumible el plan por un equipo Scrum** | Traduce la planificación AI-native a recursos y calendario que un equipo humano gestiona en su día a día |

> Capa **autónoma de OpenSpec**: parte de los documentos (`arquitectura-base.md`, `roadmap.md`, detalle de historias). Si existen changes de OpenSpec, los usa como detalle adicional, pero la unidad de planificación sigue siendo el change/historia del roadmap. En equipos pequeños, el AI Delivery Manager puede ser el mismo humano que actúa de AI Lead.

---

## 4. Documentos del proyecto

Cada fase produce documentos que son la entrada de la siguiente. El humano revisa y aprueba cada documento antes del handoff.

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
├── roadmap.md                       ← native-ai roadmap (AI Lead) / Fase 3
├── prompts-roadmap-native-ai.md     ← native-ai roadmap (AI Lead) / Fase 3
├── planificacion-proyecto.md        ← AI Delivery Manager / Fase 3.5 (aidd project-plan)
└── sprint-plan.md                   ← AI Delivery Manager / Fase 3.5 (aidd sprint-planning)

AGENTS.md                            ← native-ai init — registro de comandos del skill

openspec/
├── config.yaml                      ← project_context (init) + sección roadmap (roadmap)
├── specs/                           ← specs consolidadas
├── changes/
│   └── <change>/
│       ├── proposal.md              ← native-ai open change
│       ├── design.md                ← native-ai open change
│       ├── spec.md (uno o varios)   ← native-ai open change
│       └── decisions.md             ← pre-flight de dudas (open / implement)
└── audit/
    └── YYYY-MM.jsonl                ← auditoría append-only (todos los comandos)
```

> **Cambios respecto a la versión OpenSpec directa:** `sprints-desarrollo.md` se sustituye por `docs/roadmap.md`, y `prompts_a_ejecutar.md` por `docs/prompts-roadmap-native-ai.md` (ambos generados por `native-ai roadmap`). Aparecen tres artefactos nuevos: `decisions.md` por change, `AGENTS.md` y la auditoría `openspec/audit/`.

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
- Verificar disponibilidad de Node.js/npm y de los skills `aidd-*` (planificación/diseño), `native-ai-specs`, `booster-ux` y `booster-uml`

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

`aidd user-stories` actúa como Product Owner experto: lee `docs/requisitos.md` y genera `docs/mapa-historias-usuario.md` con las personas/roles, un backbone de actividades principales, historias agrupadas por fases (F0 foundation, F1, F2...), cada una con ID único en formato "Como [rol], quiero [acción] para [objetivo]", criterio de salida por fase, priorización MoSCoW para Fase 1 y referencia al RF correspondiente.

#### Paso 1.3 — Detalle de historias de usuario

**Comando AIDD:**
```text
aidd user-story-details
```

`aidd user-story-details` actúa como Product Owner y especialista en criterios de aceptación: lee `docs/requisitos.md` y `docs/mapa-historias-usuario.md` y genera `docs/detalle-historias-usuario.md` con, por cada historia, descripción completa, prioridad dentro de su fase, estimación orientativa (S ≤ 2 días · M 3-5 días · L 1-2 semanas), criterios de aceptación verificables (Dado/Cuando/Entonces), marca de criterios bloqueantes y notas técnicas y dependencias.

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

El AI Architect consolida la arquitectura real del producto una vez validado el prototipo y cerrado el feedback del cliente. **Este documento es el insumo principal de `native-ai roadmap`.**

**Comando AIDD:**
```text
aidd architecture
```

`aidd architecture` actúa como arquitecto de software senior con enfoque de implementación: analiza como fuentes de verdad `docs/detalle-historias-usuario.md`, `docs/propuesta-arquitectura-base.md` y `docs/guia-estilos.md` (señalando y resolviendo cualquier conflicto entre ellas) y genera `docs/arquitectura-base.md` —implementable, sin contradicciones, con cada decisión explícita— con: objetivo y alcance; principios y decisiones arquitectónicas; estructura de la solución (árbol de carpetas real); descomposición por módulos/dominios; capas y responsabilidades; componentes base y relaciones; flujos de información; gestión de estado; navegación y endpoints; integraciones; seguridad, accesibilidad, observabilidad y rendimiento; escalabilidad, mantenibilidad y extensibilidad; y riesgos, supuestos y decisiones pendientes. Es el **insumo principal de `native-ai roadmap`**.

**Criterio de salida de Fase 2:** Prototipo validado por el cliente. Guía de estilos, propuesta de arquitectura y arquitectura técnica definitiva aprobadas. Requisitos y arquitectura en estado consumible por `native-ai roadmap`.

> **Nota sobre el framework de prompting:** A diferencia de la versión OpenSpec directa, aquí el Architect **no** escribe a mano un borrador de `prompts_a_ejecutar.md`. El framework de prompting (`docs/prompts-roadmap-native-ai.md`) lo genera `native-ai roadmap` en la Fase 3 a partir de estos documentos.

---

### Fase 3 — Inicialización y Roadmap (AI Lead) · DEFINITION → EXECUTION

**Propósito:** El AI Lead toma los documentos del AI Architect, inicializa Native AI Specs y fasea la ejecución con `native-ai roadmap`, ajustando la granularidad al presupuesto de contexto. Esta fase cierra DEFINITION y abre EXECUTION.

**Entradas:** `mapa-historias-usuario.md`, `detalle-historias-usuario.md`, `arquitectura-base.md`, `guia-estilos.md`
**Salidas:** OpenSpec inicializado, `AGENTS.md` con comandos registrados, `docs/roadmap.md`, `docs/prompts-roadmap-native-ai.md`, sección `roadmap` en `openspec/config.yaml`

#### Paso 3.1 — `native-ai init`

```text
native-ai init
```

El comando:
1. Comprueba si `openspec` está instalado; si no, instala `@fission-ai/openspec@latest`.
2. Ejecuta `openspec init`.
3. Comprueba la disponibilidad de `booster-ux` y `booster-uml`.
4. Pregunta si el proyecto es **nuevo** o **existente** (para existente, ver Fase 5).
5. Para proyecto existente, solicita las rutas de los markdowns funcionales/técnicos/de arquitectura y los vuelca a `openspec/config.yaml` (`project_context`).
6. Registra los comandos del skill en `AGENTS.md` dentro de un bloque idempotente `<!-- BEGIN/END native-ai-specs commands -->`.

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

#### Paso 3.3 — `native-ai roadmap`

```text
native-ai roadmap
```

El comando genera, sin tocar todavía ningún change de OpenSpec:

- **`docs/roadmap.md`** — presupuesto de contexto asumido y justificación, complejidad estimada, fases ordenadas con objetivo, alcance/exclusiones, dependencias, entregables OpenSpec esperados, criterios de cierre y riesgo de contexto por fase.
- **`docs/prompts-roadmap-native-ai.md`** — los prompts a ejecutar hasta finalizar el desarrollo, **usando exclusivamente** los comandos del skill:
  - `native-ai open change <what-you-want-to-build>`
  - `native-ai implement change <what-you-want-to-build>`
  - `native-ai close change <what-you-want-to-build>`
  
  Para cada fase, el documento indica qué documentos/secciones pasar al modelo, qué partes del código son relevantes, qué **no** incluir todavía para no contaminar contexto, y cuándo conviene dividir una fase en varios changes.
- **Sección `roadmap` en `openspec/config.yaml`** — índice navegable: `context_budget`, `complexity`, rutas de docs y lista ordenada de fases con `id`, `name`, `objective`, `context_risk` y `change_hint` (slug sugerido para `native-ai open change`).

> `native-ai roadmap` **no** ejecuta `openspec new change`, **no** archiva cambios y **no** edita otros artefactos de `openspec/` aparte de `config.yaml`.

**Criterio de salida de Fase 3 (parcial):** Roadmap aprobado por el equipo técnico. Cada fase es abrible como uno o pocos changes con contexto acotado. `config.yaml` actualizado.

#### Paso 3.4 — Apertura del change `foundation` y del primer change funcional

**Conceptos clave del ciclo `native-ai-specs`:**

Un **change** es la unidad de trabajo: equivale a una fase del roadmap o feature acotada. El ciclo de vida tiene tres comandos operativos (más dos auxiliares):

| Comando | Quién lo ejecuta | Qué hace |
|---|---|---|
| `native-ai open change <slug>` | **AI Lead** (todos los changes) | **Pre-flight de dudas** (máx. 7) → `openspec new change` → genera `proposal.md`, `design.md` y `spec.md`, y persiste `decisions.md`. El Lead **valida** los specs antes de entregarlos. Opcionalmente dispara `booster-uml`. |
| `native-ai implement change <slug>` | AI Developer | **Pre-flight de dudas** (máx. 7) → `openspec instructions apply --change <slug>` → produce el código. |
| `native-ai close change <slug>` | Outcome Validator | `openspec archive <slug>` → cierra y archiva el change validado. |
| `native-ai uml <slug>` | Cualquier rol | Genera HTML de diagramas del change con `booster-uml` (entrada: `design.md`, `proposal.md`, `spec.md`). |
| `native-ai prototype-ux [<slug>]` | AI Architect / Developer | Genera prototipos UX con `booster-ux`, una vez por pantalla nueva del change. |

> **Decisión de proceso (ver #007):** el `open change` (propose) de **todos** los changes lo ejecuta el **AI Lead**, no el Developer. El Lead actúa como control de calidad de la especificación: abre el change, responde el pre-flight, valida los artefactos y solo entonces entrega specs validados al Developer. El Developer se limita a `implement change` + verificación + corrección de bugs.

**Diferencia clave respecto a OpenSpec directo:** `open change` e `implement change` ejecutan un **pre-flight de dudas** antes de actuar. El agente lee el contexto disponible, detecta ambigüedades reales (clasificadas como `bloqueante`, `preferencia` o `confirmacion`), pregunta al humano (máximo 7, priorizando bloqueantes) y persiste las respuestas en `openspec/changes/<slug>/decisions.md`. En modo no interactivo toma el default recomendado para no bloqueantes y se detiene ante bloqueantes sin default seguro.

---

**Change `foundation`** — siempre el primero, siempre especial. No implementa funcionalidad: establece la estructura base del proyecto (árbol de carpetas, configuración, archivos iniciales). Sin él, los changes funcionales no tienen base sobre la que operar. El AI Lead lo ejecuta completo:

1. `native-ai open change foundation` — responde el pre-flight (verifica que la estructura propuesta coincide con `arquitectura-base.md`)
2. Revisar y ajustar los artefactos generados (`proposal.md`, `design.md`, `spec.md`)
3. `native-ai implement change foundation`
4. Verificar el resultado: árbol de carpetas, archivos de configuración y estructura base correctos
5. `native-ai close change foundation`

**Primer change funcional** — el AI Lead abre y valida el primer change real (según `docs/roadmap.md` / `docs/prompts-roadmap-native-ai.md`) y entrega los specs validados al equipo:

1. `native-ai open change <primer-change>` usando el prompt de su fase en `docs/prompts-roadmap-native-ai.md`; responde el pre-flight de dudas
2. Revisar y validar los artefactos generados y `decisions.md` — son el material que recibirán los AI Developers
3. Handoff a AI Developers: el desarrollo puede comenzar (el Developer ejecutará `native-ai implement change`)

> A partir de aquí, el AI Lead repite el `open change` + validación para **cada** change del roadmap, normalmente cuando el Outcome Validator archiva el anterior y lanza el siguiente.

**Criterio de salida de Fase 3:** Roadmap aprobado. OpenSpec inicializado y configurado. `AGENTS.md` registrado. Change `foundation` abierto, implementado y archivado. Primer change funcional abierto, validado y entregado a los AI Developers.

---

### Fase 3.5 — Planificación de entrega (AI Delivery Manager) · DEFINITION → EXECUTION

**Propósito:** Traducir el diseño aprobado y el roadmap consciente de contexto en un plan ejecutable por un equipo (humano + agentes): qué **recursos** hacen falta y en qué **orden temporal** se aborda el trabajo. Cubre la dimensión de gestión de proyecto/recursos que el SDD v3 no contemplaba. Es **opcional** pero recomendada cuando el desarrollo lo ejecuta un equipo humano que necesita planificar recursos y sprints (p. ej. un equipo Scrum).

**Entradas:** `arquitectura-base.md`, `mapa-historias-usuario.md`, `detalle-historias-usuario.md` (para recursos); `roadmap.md` + `planificacion-proyecto.md` + `detalle-historias-usuario.md` (para sprints)
**Salidas:** `docs/planificacion-proyecto.md`, `docs/sprint-plan.md`

> Capa **autónoma de OpenSpec** (skills `aidd-*`). No sustituye al `native-ai roadmap`: lo complementa. El roadmap fasea por presupuesto de contexto del modelo; esta fase añade recursos y calendario humano **sin romper ese faseado** (un sprint no parte un change).

#### Paso 3.5.1 — `aidd project-plan` (plan de recursos)

Puede ejecutarse en cuanto la Fase 2 está aprobada (no requiere el roadmap). El AI Delivery Manager genera `docs/planificacion-proyecto.md` con perfiles/equipo (mapeados a los roles SDD cuando aplica), software/licencias (open source vs coste, órdenes de magnitud), infraestructura/entornos, esfuerzo agregado (a partir de S/M/L), dependencias y riesgos de recursos.

**Criterio:** Plan de recursos aprobado; el equipo sabe qué perfiles, licencias e infraestructura necesita.

#### Paso 3.5.2 — `aidd sprint-planning` (plan de sprints)

Requiere `docs/roadmap.md` (Paso 3.3) y `docs/planificacion-proyecto.md`. El AI Delivery Manager distribuye los changes/fases del roadmap en sprints, respetando dependencias y prerequisitos (F0 → F1 → F2) y la capacidad del equipo, y produce `docs/sprint-plan.md` con objetivo por sprint, unidades de trabajo completas (sin partir changes), asignación de perfiles, hitos y riesgos de planificación.

**Criterio de salida de Fase 3.5:** Plan de recursos y plan de sprints aprobados por el equipo. El trabajo del roadmap queda repartido en iteraciones ejecutables por un equipo humano, con dependencias respetadas. La ejecución (Fase 4) sigue el orden de los sprints: el AI Lead abre cada change con `native-ai open change` según ese orden.

---

### Fase 4 — Apertura, Implementación y Validación por change · EXECUTION

**Propósito:** Producir el código de cada change de forma controlada y trazable. El **AI Lead** abre y valida los specs (`open change`); el **AI Developer** los implementa, verifica y corrige bugs (`implement change`); el **Outcome Validator** valida y archiva (`close change`). El Developer no improvisa decisiones de arquitectura ni abre changes.

**Entradas:** `docs/prompts-roadmap-native-ai.md`, `docs/roadmap.md`, `arquitectura-base.md`, `detalle-historias-usuario.md`, change activo en OpenSpec

#### Ciclo por change

```
AI Lead: copia el prompt de la fase de prompts-roadmap-native-ai.md
        │
        ▼
native-ai open change <slug>            ◄── lo ejecuta el AI LEAD
  └─ PRE-FLIGHT DE DUDAS (máx. 7) → decisions.md
  └─ openspec new change → proposal.md, design.md, spec.md
AI Lead revisa y VALIDA los specs generados y decisions.md
        │
        ▼  ── Handoff: specs validados ──► AI Developer ──
        │
AI Developer revisa los specs recibidos
native-ai implement change <slug>       ◄── lo ejecuta el AI DEVELOPER
  └─ PRE-FLIGHT DE DUDAS (máx. 7) → decisions.md
  └─ openspec instructions apply --change <slug>
        │
        ▼
AI Developer prueba manualmente (levanta la aplicación)
Corrige los bugs de implementación que identifique
(opcional: native-ai uml <slug> / native-ai prototype-ux <slug>)
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
   │         ┌─────────────┴──────────────────┐
   │         │                                │
   │   Problema de                    Problema de spec
   │   implementación                 o arquitectónico
   │         │                                │
   │   → Dev corrige              → Reporta al AI Lead
   │     (itera hasta OK)           Lead reabre/ajusta el
   │                                change o escala al Architect
   ▼
Outcome Validator aprueba el Merge Request
        │
        ▼
native-ai close change <slug>   (openspec archive)
        │
        ▼
Outcome Validator lanza el siguiente change
        │
        ▼
AI Lead abre y valida el siguiente change (native-ai open change)
        │
        ▼  ── Handoff: specs validados ──► AI Developer ──
```

**Prompt de apertura** (lo ejecuta el AI Lead, extraído de `docs/prompts-roadmap-native-ai.md` para cada fase):

El bloque de cada fase en `docs/prompts-roadmap-native-ai.md` indica el contexto mínimo a pasar y el comando exacto a ejecutar. Su estructura típica:

```prompt
native-ai open change <slug-de-la-fase>

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

- **AI Lead** — ejecuta `native-ai open change <slug>`, responde el pre-flight, revisa y **valida** los artefactos (`proposal.md`, `design.md`, `spec.md`, `decisions.md`) y entrega specs validados al Developer.
- **AI Developer** — recibe los specs validados, ejecuta `native-ai implement change <slug>` (responde su pre-flight antes de que se aplique el código), prueba end-to-end y **corrige los bugs de implementación que identifique**. No abre el change.
- **Outcome Validator** — valida (técnico + funcional + trazabilidad), aprueba el MR, ejecuta `native-ai close change <slug>` y habilita al AI Lead para abrir el siguiente change.

#### Enlace con Jira (opcional): HU vs change

Cuando la integración con Jira está configurada (sección `jira:` en `openspec/config.yaml` + MCP de Atlassian disponible), el ciclo por change mantiene sincronizados dos planos sin duplicar el seguimiento:

- **La HU es la unidad de entrega rastreable** → una **Story** en Jira (la crea `aidd sprint-planning`). Es lo estable: tiene criterios de aceptación y la valida el cliente.
- **El change es la unidad de ejecución** → una **sub-tarea** de la Story de su HU (la crea `native-ai open change`). Es lo volátil: lo fasea el presupuesto de contexto y **no es 1:1** con la HU (una HU puede necesitar varios changes).
- **Transiciones automáticas**: `implement change` mueve la sub-tarea **y su Story padre** a *In Progress* y las **asigna** al usuario autenticado en el MCP (o al `assignee_override` si el MCP usa cuenta de servicio); `close change` pasa la sub-tarea a *Done* y la Story a *Done* **solo cuando todas sus sub-tareas están Done** (una HU no se cierra a medias).
- **Registro del enlace**: `docs/jira-sync.md` (mapa HU ↔ change ↔ claves de Jira) es la fuente de verdad operativa; cada change anota su(s) HU en `proposal.md` y el PR del change referencia la clave Jira (`ABC-123`). Detalle de comportamiento en el skill `native-ai-specs`, sección "Integración con Jira".
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
- Ejecuta: native-ai close change <SLUG>
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
  native-ai init  → responde "desarrollo ya existente"
                    y aporta rutas de docs funcionales/técnicos/arquitectura
                    (se vuelcan a config.yaml: project_context)
  native-ai roadmap  → fasea el trabajo pendiente
  native-ai open/implement/close change 'legacy-sync'
                    → registra el estado actual como primer change
        │
        ▼
Paso 4: Incorporación al flujo normal
  Toda nueva funcionalidad sigue el ciclo AI-Native
```

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

Tras la reconciliación humana, el AI Lead ejecuta `native-ai init` (indicando proyecto existente y las rutas de estos documentos) y `native-ai roadmap` para fasear lo pendiente.

---

## 6. Configuración del entorno de trabajo

### AGENTS.md

`AGENTS.md` es el **ancla de contexto permanente** del proyecto y el fichero genérico que cualquier agente IA (Claude Code, Codex u otros) lee al abrir el repositorio. Sustituye al antiguo `CLAUDE.md` específico de un cliente para no atar la metodología a una herramienta concreta.

Tiene dos partes:

1. **Bloque manual** — contexto, stack, convenciones, roles y documentos clave. Lo redacta el humano en la Fase 0 y se mantiene a mano.
2. **Bloque auto-generado** — `native-ai init` registra los comandos del skill dentro de un bloque idempotente `<!-- BEGIN/END native-ai-specs commands -->`. No se edita a mano: se regenera en cada `native-ai init` sin tocar el resto del fichero.

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
- Skill: native-ai-specs (comandos registrados en el bloque auto-generado de abajo)
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

<!-- BEGIN native-ai-specs commands (auto-generado, no editar a mano) -->
## Comandos native-ai-specs
[Lo escribe `native-ai init`: lista de comandos del skill]
<!-- END native-ai-specs commands -->
```

> **Compatibilidad con Claude Code:** si el equipo trabaja con Claude Code y quiere conservar `CLAUDE.md`, basta con que `CLAUDE.md` sea un alias que importe `AGENTS.md` (`@AGENTS.md`) o un fichero mínimo que apunte a él. El contenido vive en `AGENTS.md`; `CLAUDE.md` es opcional.

### Gestión de contexto entre sesiones

La IA no tiene memoria entre sesiones. Para garantizar coherencia:

1. **Iniciar cada sesión** referenciando los documentos del rol activo
2. **Nunca asumir** que la IA recuerda decisiones anteriores — incluirlas en el prompt o consultarlas en `decisions.md`
3. **Los documentos son la memoria** — si algo no está documentado, no existe
4. **El AGENTS.md** es el ancla de contexto persistente en cada sesión: aporta el contexto del proyecto y publica los comandos del skill
5. **Respeta el presupuesto de contexto** del roadmap — no arrastres documentos de fases futuras a la fase actual
6. **Ante cualquier duda**, el pre-flight de `native-ai` la captura y la persiste en `decisions.md`; el AI Developer no improvisa ni escala directamente al Lead

---

## 7. Estructura de carpetas recomendada

```
proyecto/
├── AGENTS.md                          # ancla de contexto + comandos native-ai-specs (bloque auto-generado)
├── docs/
│   ├── cliente-requisitos.md          # brief del cliente (Fase 0)
│   ├── requisitos.md                  # requisitos formales (Fase 1)
│   ├── mapa-historias-usuario.md      # mapa de historias (Fase 1)
│   ├── detalle-historias-usuario.md   # criterios de aceptación (Fase 1)
│   ├── arquitectura-base-prototipo.md # arquitectura demo (Fase 2)
│   ├── guia-estilos.md                # design system (Fase 2)
│   ├── propuesta-arquitectura-base.md # propuesta técnica (Fase 2)
│   ├── arquitectura-base.md           # arquitectura definitiva (Fase 2)
│   ├── roadmap.md                     # fases del desarrollo (Fase 3 · native-ai roadmap)
│   └── prompts-roadmap-native-ai.md   # prompts por fase (Fase 3 · native-ai roadmap)
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

Cada comando `native-ai` escribe una entrada estructurada en `openspec/audit/YYYY-MM.jsonl` (un fichero por mes, append-only, JSON Lines). El objetivo es trazar **quién** ejecutó **qué** comando, sobre **qué input**, con **qué prompt y modelo**, y **qué decisión humana** se produjo.

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
- [ ] `arquitectura-base.md` está completo y es consumible por `native-ai roadmap`
- [ ] Humano ha aprobado todos los documentos

### Fase 3 — Inicialización y Roadmap
- [ ] `native-ai init` ejecutado: OpenSpec inicializado, `booster-ux`/`booster-uml` verificados, `AGENTS.md` registrado
- [ ] Presupuesto de contexto resuelto y justificado (bajo/medio/alto)
- [ ] `native-ai roadmap` ejecutado: `docs/roadmap.md` y `docs/prompts-roadmap-native-ai.md` generados
- [ ] Sección `roadmap` en `openspec/config.yaml` con una entrada por fase
- [ ] Cada fase tiene criterio de cierre verificable y riesgo de contexto asignado
- [ ] Cada fase es abrible como uno o pocos changes con contexto acotado
- [ ] Change `foundation` abierto, implementado y archivado
- [ ] Primer change funcional abierto, validado por el AI Lead y entregado a AI Developers

### Por cada change (Fase 4)
- [ ] **[AI Lead]** Copia el prompt de la fase de `prompts-roadmap-native-ai.md` y ejecuta `native-ai open change <slug>`
- [ ] **[AI Lead]** Responde el pre-flight de dudas; las decisiones quedan en `decisions.md`
- [ ] **[AI Lead]** Revisa y **valida** los artefactos generados (`proposal.md`, `design.md`, `spec.md`) antes del handoff
- [ ] **[AI Lead]** Entrega los specs validados al AI Developer
- [ ] **[AI Developer]** Revisa los specs recibidos (`proposal.md`, `design.md`, `spec.md`, `decisions.md`)
- [ ] **[AI Developer]** Ejecuta `native-ai implement change <slug>` (responde su pre-flight) sin errores
- [ ] **[AI Developer]** Prueba manualmente end-to-end y corrige los bugs de implementación que identifique
- [ ] **[AI Developer]** Prepara la feature para integración — branch actualizado, sin conflictos, MR listo
- [ ] **[Outcome Validator]** Verifica todos los criterios de aceptación (funcional + técnico)
- [ ] **[Outcome Validator]** Verifica trazabilidad (`decisions.md` + entrada de auditoría)
- [ ] **[Outcome Validator]** Diagnostica y escala cualquier problema de spec o arquitectónico al AI Lead
- [ ] **[Outcome Validator]** Aprueba el Merge Request
- [ ] **[Outcome Validator]** Ejecuta `native-ai close change <slug>`
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
| Los changes se acumulan sin validar | El Outcome Validator no está activo | No avanzar al siguiente change hasta cerrar el actual con `native-ai close change` |
| El AI Developer improvisa componentes o patrones | Los prompts del roadmap son ambiguos | El AI Lead regenera `prompts-roadmap-native-ai.md` con `native-ai roadmap` |
| El Outcome Validator aprueba sin revisar el código | El rol está siendo ejecutado superficialmente | El Outcome Validator debe hacer revisión técnica real, no solo funcional |
| El AI Lead no desdobla Front/Back | El proyecto tiene complejidad en ambas capas | Separar en Front AI Lead + Back AI Lead con changes independientes |
| Un change arrastra demasiado contexto y se atasca | Fase demasiado grande para el presupuesto de contexto | Re-fasear con `native-ai roadmap` aumentando el número de fases / partiendo la fase en varios changes |
| El pre-flight pregunta lo que ya está documentado | No leyó `docs/`, specs previas o `decisions.md` | Asegurar que el contexto del rol está accesible; las dudas resueltas no se repreguntan |
| Falta la entrada de auditoría de un change | El comando falló al escribir o se ejecutó OpenSpec a mano | Revisar `openspec/audit/`; usar siempre los comandos `native-ai`, no OpenSpec directo |

---

## 11. Equivalencia con la versión OpenSpec directa

Para equipos que vienen de la metodología v2.0 (OpenSpec a pelo):

| Concepto v2.0 (OpenSpec directo) | Equivalente v3.0 (`native-ai-specs`) |
|---|---|
| `openspec init` | `native-ai init` (+ comprobación de boosters + registro en `AGENTS.md`) |
| Planificación de sprints (`sprints-desarrollo.md`) | `native-ai roadmap` → `docs/roadmap.md` (faseado por presupuesto de contexto) |
| — (planificación de recursos no existía) | **`aidd project-plan`** → `docs/planificacion-proyecto.md` (capa Delivery, v4) |
| Sprints calendarizados para equipo humano | **`aidd sprint-planning`** → `docs/sprint-plan.md` sobre el roadmap (capa Delivery, v4) |
| Framework de prompting (`prompts_a_ejecutar.md`) | `docs/prompts-roadmap-native-ai.md` (generado por `native-ai roadmap`) |
| `/opsx:propose [name]` | `native-ai open change <slug>` (**+ pre-flight de dudas** → `decisions.md`) |
| `/opsx:apply [name]` | `native-ai implement change <slug>` (**+ pre-flight de dudas**) |
| `/opsx:archive [name]` | `native-ai close change <slug>` |
| `/opsx:explore` (checklist go-live) | Revisión del roadmap (`docs/roadmap.md`) y criterios de cierre por fase |
| Artefactos del change (`proposal/design/tasks`) | `proposal.md`, `design.md`, `spec.md` + `decisions.md` |
| Diagramas (manual) | `native-ai uml <slug>` (booster-uml) |
| Prototipo (manual) | `native-ai prototype-ux [<slug>]` (booster-ux) |
| — (no existía) | **Auditoría** obligatoria en `openspec/audit/*.jsonl` |
| — (no existía) | **Pre-flight de dudas** (máx. 7) integrado en open/implement |
| — (no existía) | **Presupuesto de contexto** (bajo/medio/alto) que regula el faseado |

---

## 12. Registro de decisiones sobre el framework

Tabla de cambios aplicados o pendientes de decisión sobre esta metodología. Sirve como log para el responsable del framework.

| # | Área | Estado | Descripción del cambio | Justificación |
|---|---|---|---|---|
| 001 | Roles / Fase 2-3 | **Aplicado** | `arquitectura-base.md` lo produce el AI Architect en Fase 2 (Paso 2.4), no el AI Lead | La arquitectura es diseño técnico, no planificación. El AI Lead la recibe como input de `native-ai roadmap`. |
| 002 | Tooling | **Aplicado** | Toda operación sobre specs pasa por el skill `native-ai-specs` en vez de comandos OpenSpec directos | Añade pre-flight de dudas, presupuesto de contexto, prototipos/UML integrados y auditoría obligatoria, manteniendo OpenSpec por debajo. |
| 003 | Framework de prompting | **Aplicado** | El framework de prompting ya no es un borrador manual del Architect: lo genera `native-ai roadmap` como `docs/prompts-roadmap-native-ai.md` | Elimina el trabajo redundante del antiguo Paso 2.5. El roadmap consolida faseado y prompts en un solo comando reproducible y auditable. |
| 004 | Planificación | **Aplicado** | La planificación de sprints se sustituye por `native-ai roadmap`, condicionada por el presupuesto de contexto (bajo/medio/alto) | A menor ventana de contexto del modelo, más fases y más estrechas. Evita changes que arrastran demasiado contexto y se atascan. |
| 005 | Human-in-the-loop | **Aplicado** | El pre-flight de dudas (máx. 7, persistido en `decisions.md`) hace ejecutable y trazable la validación humana en `open change` e `implement change` | Convierte un principio en un paso operativo del comando. En modo no interactivo aplica defaults recomendados y se detiene ante bloqueantes. |
| 006 | Trazabilidad | **Aplicado** | Auditoría obligatoria en `openspec/audit/*.jsonl` con hashes de input/output, versión de prompt, modelo y decisiones | Permite auditar el uso del tooling IA (quién, qué, sobre qué, con qué modelo) sin almacenar contenido sensible. |
| 007 | Roles / Fase 4 | **Aplicado** | El AI Lead ejecuta el `open change` (propose) de **todos** los changes y entrega specs ya validados al Developer; el Developer solo hace `implement change` + verificación + corrección de los bugs que identifique. No abre changes | El Lead actúa como control de calidad de la especificación antes de que el Developer la consuma, reduciendo el riesgo de implementar sobre specs incorrectas. El coste de disponibilidad continua del Lead se asume a cambio de specs validadas; el pre-flight de dudas en `implement change` cubre las dudas residuales del Developer. |
| 008 | Roles / Fase 3.5 (v4) | **Aplicado** | Se añade el rol **AI Delivery Manager** y la **Fase 3.5 — Planificación de entrega**, con los skills `aidd project-plan` (`docs/planificacion-proyecto.md`) y `aidd sprint-planning` (`docs/sprint-plan.md`) | El SDD v3 faseaba por presupuesto de contexto (roadmap) pero no cubría recursos ni calendario para un equipo humano. Esta capa, autónoma de OpenSpec, traduce el roadmap a recursos y sprints sin romper el faseado por contexto (un sprint no parte un change). Hace la planificación AI-native consumible por un equipo Scrum. |
| 009 | Integración Jira / Fases 3.5 y 4 | **Aplicado** | Integración opcional con Jira (MCP de Atlassian). `aidd sprint-planning` vuelca los sprints y crea una **Story por HU**; `native-ai open change` crea cada change como **sub-tarea** de la Story de su HU; `implement change` mueve sub-tarea + Story a *In Progress* y asigna al usuario autenticado en el MCP (con override de `config.yaml` para cuentas de servicio); `close change` pasa la sub-tarea a *Done* y la Story a *Done* solo cuando **todas** sus sub-tareas lo están. Enlace en `docs/jira-sync.md` + sección `jira:` en `openspec/config.yaml` | La **HU** es la unidad de entrega rastreable (estable, con criterios de aceptación, validada por el cliente) y el **change** es la unidad de ejecución acotada por contexto (volátil, no 1:1 con la HU). Modelar el change como sub-tarea de la HU mantiene coherentes ambos planos sin doble contabilidad y permite un *Done* de la HU que no se marca a medias. Es opcional y no intrusiva: sin configuración, los comandos funcionan igual. |
