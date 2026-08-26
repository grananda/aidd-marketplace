# Roadmap de features — aidd-marketplace

Backlog vivo de mejoras futuras de los plugins (`aidd`, `aisdd`, `aiad`, `boosters`). Cada entrada se registra aquí cuando surge la idea y se marca cuando se implementa. Este documento **no** es el roadmap de un proyecto cliente (eso lo genera `aisdd roadmap`); es el backlog del propio marketplace.

Estados: `propuesta` → `aceptada` → `implementada` (con versión y commit) / `descartada` (con motivo).

| # | Feature | Plugin(s) | Estado | Añadida |
|---|---------|-----------|--------|---------|
| F-01 | `aisdd review change` — paso de revisión con Jira In Review + aiad-review | aisdd, aiad | propuesta | 2026-07-11 |
| F-02 | Paralelismo en el faseado: tres modos (`atomic` / `waves` / `multilane`) | aisdd, aidd, boosters | **implementada** | 2026-08-25 |
| F-03 | Pre-flight configurable por proyecto (bloqueantes sin límite) | aisdd | **implementada** | 2026-08-26 |
| F-04 | Onboarding de proyecto existente: `init` siembra specs base | aisdd | **implementada** | 2026-08-26 |
| F-05 | Scripts deterministas para auditoría y bloques de `AGENTS.md` | aisdd | **implementada** | 2026-08-26 |
| F-06 | Enrutado del Outcome Validator: ¿al Developer o al Lead? | aisdd | propuesta | 2026-08-26 |
| F-07 | Partir `aisdd-specs/SKILL.md` en `references/*.md` | aisdd | **implementada** | 2026-08-26 |

---

## F-01 — `aisdd review change <slug>`: paso de revisión entre implement y close

**Estado:** propuesta · **Añadida:** 2026-07-11 · **Plugins:** `aisdd` (nuevo comando), `aiad` (reutiliza `aiad-review`)

**Qué.** Nuevo comando del ciclo de change que se ejecuta entre `implement change` y `close change`:

1. **Jira**: mueve la **sub-tarea del change** a la columna *In Review* (nueva clave `status_in_review` en la sección `jira:` de `openspec/config.yaml`; como el resto de estados, se descubre por transiciones reales del proyecto, no se hardcodea).
2. **Review de código**: invoca el skill **`aiad-review`** sobre el código del change (el diff de la implementación), con su checklist completa (correctness/quality/perf, capas backend/API/frontend) y su entregable HTML con fragmentos de código y cambios propuestos.
3. **Resultado**: si el review encuentra hallazgos críticos, el change **no debe cerrarse** hasta resolverlos (gate blando: el humano decide); los hallazgos quedan referenciados en el change (p. ej. `openspec/changes/<slug>/review.md` o enlace al HTML) y en la entrada de auditoría.

**Ciclo resultante:** `open` (to_do) → `implement` (in_progress) → **`review` (in_review)** → `close` (done).

**Consideraciones de diseño (a decidir al implementar):**
- **Dependencia opcional de `aiad`**: si el plugin `aiad` no está instalado, degradar con aviso (mover a In Review igualmente y sugerir review manual) — mismo patrón de degradación limpia que booster-ux/uml.
- **Alcance del review**: por defecto el diff del change (desde su apertura); permitir `aisdd review change <slug> <base-branch>` para modo merge-readiness de aiad-review.
- **Jira**: si el board no tiene columna In Review, avisar y no transicionar (no crear estados); `close change` seguiría funcionando desde In Progress o In Review indistintamente.
- **Autoría**: aiad-review es didáctico y no aplica fixes; en contexto aisdd (la IA escribió el código) valorar si el informe debe orientarse al Outcome Validator en lugar de al autor humano.
- **Auditoría**: entrada `review-change` en `openspec/audit/` con hashes del informe.

---

## Plantilla para nuevas entradas

```markdown
## F-XX — <título corto>

**Estado:** propuesta · **Añadida:** YYYY-MM-DD · **Plugins:** <afectados>

**Qué.** <descripción de la feature en 2-5 líneas>

**Consideraciones de diseño (a decidir al implementar):**
- <puntos abiertos>
```

---

## F-02 — Paralelismo en el faseado: tres modos

**Estado:** implementada · **Versión:** `aisdd` 1.9.0, `aidd` 1.16.0, `boosters` 1.11.0 · **Commit:** `c0f5dff` (PR #3)

`aisdd roadmap` elige entre `atomic` (clásico), `waves` (oleadas: hasta `parallel_developers` fases a la vez respetando `depends_on`) y `multilane` (líneas de trabajo con rutas y specs disjuntas, verificadas al cerrar).

Oleadas y lanes son **ejes perpendiculares**, no alternativas: la oleada es una *anotación* sobre el roadmap (se calcula del grafo y se puede añadir a un roadmap ya hecho sin re-fasear); el lane es una *partición* (determina qué entra en cada fase, y retrofitarlo exige re-fasear).

Incluye: `aisdd lane [list|switch|status]`, guard de un change por lane, nivel 4 de corrección (contrato compartido → parada coordinada), `depends_on` en los tres modos, bloque de paralelismo en `AGENTS.md`, dimensionado por tramos en `aidd sprint-planning`, y chips/KPIs en `booster-docs`.

## F-03 — Pre-flight configurable por proyecto

**Estado:** implementada · **Versión:** `aisdd` 1.10.0 · **Commit:** `dcaa8ea` (PR #4)

Portado de `native-ai-specs` v1.6.0 (su decisión 013). Elimina el techo de 7 dudas: las **bloqueantes se preguntan siempre y sin límite**; preferencias y confirmaciones se acotan en la sección `preflight` de `openspec/config.yaml`. Lo que queda fuera se resuelve con el default y se registra como `Origen: auto-default`.

De paso unifica los dos pre-flights duplicados en una sola sección con variantes `[APERTURA]` / `[IMPLEMENTACION]`.

## F-04 — Onboarding de proyecto existente

**Estado:** implementada · **Versión:** `aisdd` 1.11.0 · **Origen:** decisiones 011 y 012 de `native-ai-specs` v1.6.0

Hoy `aisdd init` sobre un repo en marcha solo registra rutas de documentación en `config.yaml`: se arranca **sin línea base** contra la que contrastar, así que el primer `open change` no tiene con qué comparar.

1. `init` analiza el código y siembra `openspec/specs/<capability>/spec.md` con el estado actual, marcando `UNKNOWN` lo no inferible y `LEGACY` la deuda técnica, con validación humana después.
2. `open change` puebla `config.yaml` si está vacío o sin contexto útil, **antes** del pre-flight, en vez de generar specs sobre un contexto vacío.

## F-05 — Scripts deterministas

**Estado:** implementada · **Versión:** `aisdd` 1.12.0 · **Origen:** `scripts/*.js` de `native-ai-specs` v1.6.0, portados a **Python** (que es lo que usa este repo: 6 scripts, ninguno JS)

Hoy la entrada de auditoría JSONL y los bloques idempotentes de `AGENTS.md` son **prosa que el modelo debe ejecutar bien cada vez**. Ya son dos bloques (comandos + roadmap) y el formato de auditoría tiene una docena de campos.

- `audit.py` — compone y valida la entrada de `openspec/audit/YYYY-MM.jsonl`, incluida la purga por retención.
- `agents_block.py` — reemplazo idempotente de un bloque delimitado, sin tocar el resto del fichero.
- `check_mojibake.py` — verificación de encoding; el renderer de `booster-docs` ya tiene la lógica y puede reutilizarse.

## F-06 — Enrutado del Outcome Validator

**Estado:** propuesta · **Decisión pendiente del propietario de la metodología**

Divergencia con `native-ai-specs` v1.6.0 (su decisión 008), no una carencia:

- **Nuestro modelo:** el Outcome Validator reporta al **AI Lead**.
- **El suyo:** reporta **siempre al AI Developer**, que corrige o eleva al Lead, que a su vez evalúa elevar al Architect.

Su argumento: un único canal de entrada de fallos simplifica la comunicación y mantiene al Developer como dueño de su entrega. Afecta a cómo trabaja la gente, no al código, así que la decisión no es técnica.

## F-07 — Partir `aisdd-specs/SKILL.md` en `references/*.md`

**Estado:** implementada · **Versión:** `aisdd` 2.0.0 · **Origen:** estructura de `native-ai-specs` v1.6.0

El `SKILL.md` supera las 1.200 líneas y se carga entero aunque el 90% no aplique al comando en curso. Upstream lo tiene partido en un fichero por comando (`roadmap.md`, `open-change.md`, `preflight.md`…).

Sin cambio funcional. **Debe ir la última y en solitario**: mueve todo el fichero, así que cualquier rama viva en paralelo se vuelve irreconciliable.
