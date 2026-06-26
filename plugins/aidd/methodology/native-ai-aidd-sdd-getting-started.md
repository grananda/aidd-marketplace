# Native AI · AIDD-SDD — Getting Started

**Guía de arranque rápido** para desarrollar con la metodología **AIDD-SDD**: los skills `aidd` (planificación, diseño y entrega) sobre el proceso *Spec-Driven Development*, y el skill `native-ai-specs` (ejecución sobre OpenSpec).

> Documento de referencia completo: [native-ai-aidd-sdd.md](native-ai-aidd-sdd.md). Esta guía es el camino corto para ponerte en marcha en una tarde.

---

## 1. ¿Qué es esto en una frase?

Un flujo de desarrollo donde **la especificación es el motor**: **defines y diseñas con los skills `aidd`** → generas specs por *change* con `native-ai-specs` (sobre OpenSpec) → la IA implementa → un validador firma. El humano aprueba en cada transición y todo queda trazado.

**Los cinco roles:**

| Rol | Hace | Comandos clave |
| --- | --- | --- |
| **AI Architect** | Requisitos, historias, arquitectura, prototipo | `aidd requirements`, `aidd user-stories`, `aidd user-story-details`, `aidd prototype-architecture`, `aidd prototype`, `aidd style-guide`, `aidd architecture-proposal`, `aidd architecture` |
| **AI Lead** | Inicializa, fasea, **abre y valida los specs de todos los changes** | `native-ai init`, `native-ai roadmap`, `native-ai open change` |
| **AI Delivery Manager** | Plan de recursos y reparto en sprints (capa Delivery, v4) | `aidd project-plan`, `aidd sprint-planning` |
| **AI Developer** | Implementa, verifica, corrige bugs | `native-ai implement change` |
| **Outcome Validator** | QA técnico + funcional, archiva | `native-ai close change` |

---

## 2. Requisitos previos

- **Node.js y npm** instalados.
- Un agente con el skill **`native-ai-specs`** disponible (Claude Code, Codex u otro).
- Skills auxiliares (opcionales pero recomendados):
  - `booster-ux` — prototipos UX.
  - `booster-uml` — diagramas del change.
- Comprobación rápida:

```bash
node --version
npm --version
openspec --version   # si falta, native-ai init lo instala
```

---

## 3. Instalación e inicialización

`native-ai init` envuelve la instalación de OpenSpec y prepara el proyecto.

```text
native-ai init
```

Qué hace:

1. Instala OpenSpec si falta (`npm install -g @fission-ai/openspec@latest`).
2. Ejecuta `openspec init` por debajo.
3. Comprueba `booster-ux` y `booster-uml`.
4. Pregunta si el proyecto es **nuevo** o **existente**.
5. Registra los comandos del skill en `AGENTS.md` (bloque idempotente auto-generado).

**Resultado:** Native AI Specs inicializado, `AGENTS.md` con los comandos, `openspec/` creado.

---

## 4. El flujo completo de un vistazo

```
native-ai init                 ← AI Lead   (una vez)
native-ai roadmap              ← AI Lead   (una vez · fasea el desarrollo)
        │
        ▼   por cada fase del roadmap (= un change):
native-ai open change <slug>   ← AI Lead   (pre-flight de dudas → specs validados)
        │  handoff: specs validados ──►
native-ai implement change <slug>  ← AI Developer (pre-flight → código)
        │  pruebas + corrección de bugs ──►
native-ai close change <slug>  ← Outcome Validator (valida → archiva)
        │
        ▼  siguiente change
```

> **Regla de oro del reparto:** el **AI Lead** abre (`open change`) y valida los specs de **todos** los changes; el **AI Developer** solo implementa (`implement change`) + verifica + corrige bugs; el **Outcome Validator** archiva (`close change`).

---

## 5. Quickstart end-to-end (proyecto nuevo)

### Paso 0 — Brief del cliente

```text
aidd client-requirements   # docs/cliente-requisitos.md — contexto, stack, restricciones
```

Punto de partida del AI Architect. Captura el brief y, opcionalmente, crea/actualiza `AGENTS.md`.

### Paso 1 — Definición (AI Architect)

Ejecuta, en este orden, los comandos `aidd` (cada uno aplica el prompt de su paso):

```text
aidd requirements          # docs/requisitos.md — requisitos formales trazables (RF-XX, NFR-XX)
aidd user-stories          # docs/mapa-historias-usuario.md — historias por fases
aidd user-story-details    # docs/detalle-historias-usuario.md — criterios de aceptación verificables
```

### Paso 2 — Diseño (AI Architect)

```text
aidd prototype-architecture   # docs/arquitectura-base-prototipo.md
aidd prototype                # prototipo mockeado (redirige a booster-ux) — valídalo con el cliente
aidd style-guide              # docs/guia-estilos.md
aidd architecture-proposal    # docs/propuesta-arquitectura-base.md
aidd architecture             # docs/arquitectura-base.md (arquitectura definitiva, insumo del roadmap)
```

### Paso 3 — Inicialización y Roadmap (AI Lead)

```text
native-ai init
native-ai roadmap
```

`native-ai roadmap` genera:

- `docs/roadmap.md` — fases del desarrollo (granularidad según presupuesto de contexto).
- `docs/prompts-roadmap-native-ai.md` — el prompt exacto de cada fase.
- Sección `roadmap` en `openspec/config.yaml`.

### Paso 3.5 — Planificación de entrega (AI Delivery Manager) · opcional

Traduce el diseño y el roadmap a recursos y calendario para un equipo humano (capa Delivery, v4; skills `aidd`, autónomos de OpenSpec):

```text
aidd project-plan      # docs/planificacion-proyecto.md  (tras aprobar el diseño; no necesita roadmap)
aidd sprint-planning   # docs/sprint-plan.md             (necesita docs/roadmap.md)
```

Útil cuando un equipo Scrum va a ejecutar el desarrollo. No sustituye al roadmap: reparte sus changes en sprints respetando dependencias y **sin partir ningún change**.

### Paso 4 — Foundation (AI Lead)

El primer change siempre es `foundation` (estructura base, sin funcionalidad):

```text
native-ai open change foundation
native-ai implement change foundation
native-ai close change foundation
```

### Paso 5 — Primer change funcional

El **AI Lead** abre y valida; el **AI Developer** implementa; el **Validator** cierra:

```text
# AI Lead
native-ai open change alta-de-clientes

# AI Developer (tras recibir los specs validados)
native-ai implement change alta-de-clientes

# Outcome Validator (tras validar)
native-ai close change alta-de-clientes
```

Repite el Paso 5 para cada fase del roadmap hasta terminar.

---

## 6. El pre-flight de dudas (lo que más sorprende al empezar)

`open change` e `implement change` **no actúan a ciegas**: antes preguntan.

- Máximo **7 preguntas** por change, priorizando las **bloqueantes** (alcance, modelo de datos, contrato de API, integraciones, permisos).
- No repreguntan lo ya resuelto en `docs/`, `AGENTS.md` o specs previas.
- Las respuestas se guardan en `openspec/changes/<slug>/decisions.md`.
- En modo no interactivo aplican el default recomendado y se detienen solo ante bloqueantes sin default seguro.

**Tu trabajo durante el pre-flight:** responder con criterio. Si una duda es de arquitectura, el Developer la **eleva** (no la inventa).

---

## 7. Artefactos que vas a ver

```
docs/                                # definición, roadmap y planificación de entrega (planificacion-proyecto.md, sprint-plan.md)
AGENTS.md                            # ancla de contexto + comandos (auto-generado)
openspec/
├── config.yaml                      # project_context + roadmap
├── specs/                           # specs consolidadas
├── changes/<slug>/
│   ├── proposal.md  design.md  spec.md
│   └── decisions.md                 # decisiones del pre-flight
└── audit/YYYY-MM.jsonl              # auditoría append-only de cada comando
```

---

## 8. Comandos de referencia

| Comando | Quién | Para qué |
| --- | --- | --- |
| `native-ai init` | AI Lead | Inicializa OpenSpec + dependencias + `AGENTS.md` |
| `native-ai roadmap` | AI Lead | Fasea el desarrollo y genera los prompts por fase |
| `native-ai open change <slug>` | AI Lead | Pre-flight + genera specs validados del change |
| `native-ai implement change <slug>` | AI Developer | Pre-flight + implementa el código |
| `native-ai close change <slug>` | Outcome Validator | Valida y archiva el change |
| `native-ai prototype-ux [<slug>]` | Architect / Developer | Prototipos UX (booster-ux) |
| `native-ai uml <slug>` | Cualquiera | Diagramas HTML del change (booster-uml) |
| `aidd project-plan` | AI Delivery Manager | Plan de recursos `docs/planificacion-proyecto.md` (capa Delivery, v4) |
| `aidd sprint-planning` | AI Delivery Manager | Reparto en sprints `docs/sprint-plan.md` (capa Delivery, v4) |

---

## 9. Errores típicos al empezar

| Síntoma | Causa | Solución |
| --- | --- | --- |
| El Developer intenta abrir el change | Reparto de roles mal entendido | El **AI Lead** abre y valida; el Developer solo `implement change` |
| Un change se atasca arrastrando demasiado contexto | Fase demasiado grande | Re-fasea con `native-ai roadmap` (más fases, más pequeñas) |
| El pre-flight pregunta lo obvio | No leyó `docs/` / `AGENTS.md` / specs previas | Asegura que el contexto del rol está accesible |
| "La IA recuerda" decisiones no escritas | Se usa el historial como memoria | Todo va a `decisions.md` o `docs/`; si no está escrito, no existe |
| No hay entrada de auditoría | Se ejecutó OpenSpec a mano | Usa siempre los comandos `native-ai`, no OpenSpec directo |

---

## 10. Siguientes pasos

- Lee la metodología completa: [native-ai-aidd-sdd.md](native-ai-aidd-sdd.md).
- Rellena tu `AGENTS.md` con contexto, stack, roles y documentos clave del proyecto.
- Empieza por `docs/cliente-requisitos.md` y avanza fase a fase.

> **Principio que lo resume todo:** documentos como fuente de verdad, human-in-the-loop en cada transición, y un change cerrado y validado antes de abrir el siguiente.
