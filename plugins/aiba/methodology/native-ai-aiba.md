# Native AI · AIBA — Análisis de negocio, entrega y medición

**Versión:** 1.0
**Fecha:** 2026-08-27
**Base de tooling:** skills **AIBA** (`aiba-*`) + **boosters** compartidos (`booster-docs` para las vistas HTML)

> **Qué es AIBA.** *AI Business Analyst* es el conjunto de skills que cubre la **interfaz con el negocio**: validar las historias con negocio y TI, escribir el diseño funcional que se firma, planificar recursos y sprints, y medir lo que de verdad ha costado y ahorrado el uso de IA.
>
> Es una capa **complementaria** a AIDD y AISDD, no un sustituto:
>
> - **AIDD** (`aidd-*`) define y diseña: requisitos, historias, arquitectura, guía de estilos.
> - **AISDD** (`aisdd-*`) ejecuta sobre OpenSpec: roadmap y ciclo de changes.
> - **AIBA** (`aiba-*`) es lo que ve el negocio: el DF que firma, el plan que aprueba, el calendario que sigue y los KPIs con los que juzga si mereció la pena.
>
> AIBA **consume** lo que producen AIDD y AISDD y **no los modifica**. Es autónomo de OpenSpec: parte de los documentos, y si existen changes los usa como detalle adicional.

---

## 1. Los skills de AIBA

| Skill | Comando | Produce |
|---|---|---|
| `aiba-functional-design` | `aiba functional-design [HU-XX]` | Un **DF en Word por historia** en `docs/df/` |
| `aiba-hu-review-plan` | `aiba hu-review-plan` | Plan de revisión de HU + Excel `docs/xlsx/plan-revision-hu.xlsx` |
| `aiba-project-plan` | `aiba project-plan` | Plan de recursos `docs/planificacion-proyecto.md` |
| `aiba-sprint-planning` | `aiba sprint-planning` | Plan de sprints `docs/sprint-plan.md`, con volcado opcional a Jira |
| `aiba-metrics` | `aiba metrics` | KPIs medidos del uso de IA en `docs/kpis-ia.md` |

## 2. El rol

### AI Delivery Manager

Rol de planificación de entrega (añadido en v4). Traduce el diseño y el roadmap a un plan ejecutable por un equipo (humano + agentes): **recursos** y **calendario**. **No implementa código ni toma decisiones de arquitectura.** Opera con los skills `aiba` de la capa de planificación, **autónomos de OpenSpec**.

| Responsabilidad | Comandos / Detalle |
|---|---|
| **Genera el plan de recursos** | Ejecuta `aiba project-plan` en cuanto el diseño (Fase 2) está aprobado: produce `docs/planificacion-proyecto.md` con perfiles/equipo (mapeados a los roles SDD cuando aplica), software/licencias, infraestructura/entornos, esfuerzo agregado con **doble estimación humano clásico vs IA** (a partir de XS/S/M/L/XL) y **KPIs de la diferencia** (ahorro en jornadas, % de reducción y factor de aceleración), dependencias y riesgos de recursos, derivados de `arquitectura-base.md` y las historias |
| **Distribuye el trabajo en sprints** | Ejecuta `aiba sprint-planning` cuando existe `docs/roadmap.md`: produce `docs/sprint-plan.md` agrupando los changes/fases en sprints con objetivo, capacidad, asignación de perfiles y dependencias respetadas |
| **Respeta el faseado por contexto** | No parte un change para encajarlo en un sprint; un sprint contiene changes/historias completos. El roadmap (presupuesto de contexto) manda sobre el calendario |
| **Hace consumible el plan por un equipo Scrum** | Traduce la planificación AI-native a recursos y calendario que un equipo humano gestiona en su día a día |

> Capa **autónoma de OpenSpec**: parte de los documentos (`arquitectura-base.md`, `roadmap.md`, detalle de historias). Si existen changes de OpenSpec, los usa como detalle adicional, pero la unidad de planificación sigue siendo el change/historia del roadmap. En equipos pequeños, el AI Delivery Manager puede ser el mismo humano que actúa de AI Lead.


---

## 3. Dónde encaja en el proceso

AIBA aparece en tres momentos, no en uno:

1. **Tras detallar las historias** (Fase 1.3 de AIDD), para planificar cómo se revisan y cerrar con negocio y TI lo que aún está abierto.
2. **Tras aprobar el diseño** (Fase 2 de AIDD) y tras el roadmap (Fase 3 de AISDD), para traducirlo a recursos y calendario.
3. **Durante y después de la ejecución**, para medir.

El diseño funcional (`aiba functional-design`) se escribe cuando las historias están detalladas y antes de que se implementen: es el documento contra el que se desarrolla y que el cliente firma.

### Paso previo — Planificación de la revisión de HU

#### Paso 1.4 — Planificación de la revisión de HU (opcional)

**Comando AIBA:**
```text
aiba hu-review-plan
```

`aiba hu-review-plan` consolida `docs/mapa-historias-usuario.md` y `docs/detalle-historias-usuario.md` en un **Excel de planificación** (`docs/xlsx/plan-revision-hu.xlsx`) con cuatro pestañas: **Detalle HU** (todas las HU combinadas, con las palabras *Como/quiero/para* en negrita), **Dashboard** (KPIs y gráficas: HU pendientes de cerrar, bloqueadas, por fase/persona/prioridad), **Leyenda** (significado de campos codificados como `Persona` P1/P5 o `GAP`) y **Gantt** (planificación de la revisión: kickoff, semana 1 de revisión de la documentación del cliente y resto del periodo con reuniones **funcionales** con negocio y **técnicas** con TI, con detalle por HU). El `docs/plan-revision-hu.md` es la fuente de verdad; el Excel es el entregable rico.

Es la **antesala de la Fase 3.5**: `aiba sprint-planning` lee `plan-revision-hu.md` para no planificar por libre — solo compromete en sprint las HU que la revisión ha dejado cerradas/validadas y reutiliza las personas implicadas en la revisión para asignar el sprint y, al volcar a Jira, el *assignee* de cada Story. Skill autónomo (openpyxl se autoinstala si falta).

---


### Planificación de entrega

### Fase 3.5 — Planificación de entrega (AI Delivery Manager) · DEFINITION → EXECUTION

**Propósito:** Traducir el diseño aprobado y el roadmap consciente de contexto en un plan ejecutable por un equipo (humano + agentes): qué **recursos** hacen falta y en qué **orden temporal** se aborda el trabajo. Cubre la dimensión de gestión de proyecto/recursos que el SDD v3 no contemplaba. Es **opcional** pero recomendada cuando el desarrollo lo ejecuta un equipo humano que necesita planificar recursos y sprints (p. ej. un equipo Scrum).

**Entradas:** `arquitectura-base.md`, `mapa-historias-usuario.md`, `detalle-historias-usuario.md` (para recursos); `roadmap.md` + `planificacion-proyecto.md` + `detalle-historias-usuario.md` (para sprints)
**Salidas:** `docs/planificacion-proyecto.md`, `docs/sprint-plan.md`

> Capa **autónoma de OpenSpec** (skills `aiba-*`). No sustituye al `aisdd roadmap`: lo complementa. El roadmap fasea por presupuesto de contexto del modelo; esta fase añade recursos y calendario humano **sin romper ese faseado** (un sprint no parte un change).

#### Paso 3.5.1 — `aiba project-plan` (plan de recursos)

Puede ejecutarse en cuanto la Fase 2 está aprobada (no requiere el roadmap). El AI Delivery Manager genera `docs/planificacion-proyecto.md` con perfiles/equipo (mapeados a los roles SDD cuando aplica), software/licencias (open source vs coste, órdenes de magnitud), infraestructura/entornos, esfuerzo agregado con **doble estimación humano clásico vs IA** (a partir de XS/S/M/L/XL) y **KPIs de la diferencia** (ahorro en jornadas, % de reducción y factor de aceleración), dependencias y riesgos de recursos.

**Criterio:** Plan de recursos aprobado; el equipo sabe qué perfiles, licencias e infraestructura necesita.

#### Paso 3.5.2 — `aiba sprint-planning` (plan de sprints)

El AI Delivery Manager distribuye el trabajo en sprints, respetando dependencias y prerequisitos (F0 → F1 → F2) y la capacidad del equipo, y produce `docs/sprint-plan.md` con objetivo por sprint, unidades de trabajo completas (sin partir changes), asignación de perfiles, hitos y riesgos de planificación. Necesita `docs/planificacion-proyecto.md`; con `docs/roadmap.md` (Paso 3.3) planifica sobre los changes/fases del roadmap, pero **puede ejecutarse antes del roadmap en modo degradado** (planificando sobre las historias del mapa) y **re-ejecutarse después** para re-fasear con el roadmap ya hecho — sin recrear Stories en Jira: el re-faseado **mueve** HU entre sprints y gestiona sprints, jamás borra/recrea issues (las claves son permanentes).

**Criterio de salida de Fase 3.5:** Plan de recursos y plan de sprints aprobados por el equipo. El trabajo del roadmap queda repartido en iteraciones ejecutables por un equipo humano, con dependencias respetadas. La ejecución (Fase 4) sigue el orden de los sprints: el AI Lead abre cada change con `aisdd open change` según ese orden.


---

## 4. Medición

`aiba metrics` cierra el círculo: calcula **KPIs medidos** —no estimados— del uso de IA a partir del registro de actividad `docs/aidd-activity.md`, del historial de git y de las tallas del detalle de historias, y los contrasta con el esfuerzo humano declarado por el equipo.

La regla que lo gobierna es que **distingue siempre lo medido de lo estimado** y se niega a publicar cifras de ahorro que no se sostienen. Un KPI de ROI inventado hace más daño que no tener ninguno, porque se usa para decidir.

Si el proyecto usa AISDD, lee además `openspec/audit/*.jsonl` para añadir el eje de **calidad de la especificación**: correcciones por change (retrabajo de spec, complementario al churn de código), decisiones que la IA resolvió sin preguntar y lead time real de `open change` a `close change`.

## 5. Relación con las otras metodologías

| | AIDD | AISDD | **AIBA** |
|---|---|---|---|
| Pregunta que responde | ¿Qué hay que construir y cómo se diseña? | ¿Cómo se ejecuta con specs? | ¿Qué cuesta, cuándo llega y qué firma el negocio? |
| Interlocutor | Producto y arquitectura | Equipo de desarrollo | **Negocio y cliente** |
| Entregables | `requisitos.md`, historias, `arquitectura-base.md` | `openspec/`, changes, `roadmap.md` | DF en Word, Excel de revisión, plan de recursos, plan de sprints, KPIs |
| Depende de OpenSpec | No | Sí | No |

La metodología completa de AIDD-SDD vive en `native-ai-aidd-sdd.md` de los plugins `aidd` y `aisdd`; este documento cubre solo la capa AIBA.
