# AIDD + SDD — Marketplace de skills para Claude Code

Marketplace de plugins para instalar los conjuntos **AIDD** (AI Driven Development — planificación y arquitectura asistida por IA) y **SDD** (Native AI Specs sobre OpenSpec) desde cualquier instancia de Claude Code.

## Plugins

| Plugin | Contenido | Para qué |
|--------|-----------|----------|
| `aidd` | 11 skills `aidd-*` (Fases 0-2 + entrega 3.5) + metodología | Capturar requisitos, definir historias, diseñar arquitectura, planificar recursos y sprints (con volcado opcional a Jira). |
| `sdd` | `native-ai-specs` + metodología | Gestionar especificaciones con OpenSpec: roadmap, open/implement/close change, auditoría e integración Jira. |
| `boosters` | `booster-ux`, `booster-uml` | Prototipos UX y diagramas UML. **Dependencia recomendada** de `aidd` y `sdd`. |

> Los plugins `aidd` y `sdd` usan `booster-ux`/`booster-uml`. Si vas a usar `aidd prototype`, `native-ai prototype-ux` o `native-ai uml`, instala también `boosters`.

## Instalación (desde cualquier máquina)

```text
# 1. Añadir el marketplace (una vez por máquina)
/plugin marketplace add <owner>/<repo>          # p. ej. tu-usuario/aidd-marketplace
#   o por URL:  /plugin marketplace add https://github.com/<owner>/<repo>.git

# 2. Instalar los plugins que necesites
/plugin install aidd@aidd-sdd
/plugin install sdd@aidd-sdd
/plugin install boosters@aidd-sdd

# 3. Ver lo instalado / navegar
/plugin list
/plugin            # menú interactivo (Discover / Installed / Marketplaces)
```

Tras instalar, los skills quedan namespaced por su plugin, p. ej. `/aidd:aidd-sprint-planning`, `/sdd:native-ai-specs`, `/boosters:booster-ux`. También se activan por lenguaje natural y por los comandos internos (`aidd sprint-planning`, `native-ai open change`, ...).

### Activación automática por proyecto (equipo)

En `.claude/settings.json` de un proyecto puedes registrar el marketplace y preactivar plugins para todo el equipo:

```json
{
  "extraKnownMarketplaces": {
    "aidd-sdd": { "source": { "source": "github", "repo": "<owner>/<repo>" } }
  },
  "enabledPlugins": {
    "aidd@aidd-sdd": true,
    "sdd@aidd-sdd": true,
    "boosters@aidd-sdd": true
  }
}
```

## Metodología

La metodología AIDD-SDD viaja **dentro** de los plugins `aidd` y `sdd` (carpeta `methodology/`). Los skills la referencian con `${CLAUDE_PLUGIN_ROOT}/methodology/native-ai-aidd-sdd.md`, así que funciona tras instalar en cualquier repo. Es referencia de solo lectura; no se carga automáticamente.

## Desarrollo y pruebas locales

```text
# Probar un plugin suelto sin instalar
claude --plugin-dir ./plugins/aidd

# Probar el marketplace local antes de publicar
/plugin marketplace add ./
/plugin install aidd@aidd-sdd

# Validar manifiestos
claude plugin validate ./
```

## Versionado

Cada `plugin.json` fija `version` (semver). **Sube la versión al publicar cambios**: si no la subes, los usuarios ya instalados no recibirán las novedades (Claude Code los cree en la misma versión).

## Origen / sincronización

Estos plugins se generan a partir del repo piloto `checklist` (`.claude/skills/` y `.claude/methodology/`). Al actualizar allí, vuelve a copiar los skills y la metodología a `plugins/*/skills` y `plugins/*/methodology`, y sube la versión.

---

NTT DATA Spain GDN-e.
