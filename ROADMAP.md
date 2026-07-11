# Roadmap de features — aidd-marketplace

Backlog vivo de mejoras futuras de los plugins (`aidd`, `aisdd`, `aiad`, `boosters`). Cada entrada se registra aquí cuando surge la idea y se marca cuando se implementa. Este documento **no** es el roadmap de un proyecto cliente (eso lo genera `aisdd roadmap`); es el backlog del propio marketplace.

Estados: `propuesta` → `aceptada` → `implementada` (con versión y commit) / `descartada` (con motivo).

| # | Feature | Plugin(s) | Estado | Añadida |
|---|---------|-----------|--------|---------|
| F-01 | `aisdd review change` — paso de revisión con Jira In Review + aiad-review | aisdd, aiad | propuesta | 2026-07-11 |

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
