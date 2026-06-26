# AIDD + SDD — Marketplace de skills para Claude Code

Marketplace de plugins para instalar los conjuntos **AIDD** (AI Driven Development — planificación y arquitectura asistida por IA) y **SDD** (Native AI Specs sobre OpenSpec) desde cualquier instancia de Claude Code.

- Repositorio: `grananda/aidd-marketplace` — **privado**.
- Nombre del marketplace: `aidd-sdd`.

## Plugins del marketplace

| Plugin | Contenido | Para qué sirve |
|--------|-----------|----------------|
| `aidd` | 11 skills `aidd-*` (Fases 0–2 + entrega 3.5) + metodología | Capturar requisitos, definir historias, diseñar arquitectura, planificar recursos y sprints (con volcado opcional a Jira). |
| `sdd` | `native-ai-specs` + metodología | Ejecutar con OpenSpec: roadmap y ciclo open/implement/close change, pre-flight de dudas, auditoría e integración Jira. |
| `boosters` | `booster-ux`, `booster-uml` | Generar prototipos UX y diagramas UML. **Lo usan `aidd` y `sdd`.** |

## Por qué hay que instalar los tres

No son tres copias del mismo paquete: son **tres piezas de un mismo flujo** que se llaman entre sí. El método AIDD-SDD completo va de la captura de requisitos hasta la ejecución de cada change, y en ese recorrido:

1. **`aidd` cubre la planificación y el diseño** (Fases 0–2 y la capa de entrega 3.5: requisitos → historias → arquitectura → plan de recursos → sprints). Es el "qué" y el "cuándo".
2. **`sdd` cubre la ejecución** (Fases 3–4: roadmap por presupuesto de contexto y el ciclo `open/implement/close change` sobre OpenSpec, con auditoría e integración Jira). Es el "cómo se construye".
3. **`boosters` es la dependencia compartida** de los dos anteriores. No es opcional si usas el flujo completo:
   - `aidd prototype` (Fase 2.2) **redirige a `booster-ux`** para maquetar las pantallas del prototipo.
   - `native-ai prototype-ux` y `native-ai uml` (del plugin `sdd`) **invocan a `booster-ux` y `booster-uml`** para documentar cada change.
   - Si `boosters` no está instalado, esos pasos avisan de que falta el booster y no generan ni prototipos ni diagramas.

Claude Code **no resuelve dependencias entre plugins automáticamente**: cada plugin se instala por separado. Por eso, para el flujo de extremo a extremo necesitas los tres. (Si solo vas a hacer planificación sin prototipos ni diagramas, `aidd` por sí solo funciona; pero la instalación recomendada y completa son los tres.)

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

# Instalar los tres plugins
/plugin install aidd@aidd-sdd
/plugin install sdd@aidd-sdd
/plugin install boosters@aidd-sdd

# Comprobar
/plugin list
/plugin            # menú interactivo (Discover / Installed / Marketplaces / Errors)
```

Si `/plugin marketplace add` falla con error de autenticación o "repository not found", casi siempre es acceso/credenciales: vuelve al paso 1 (no eres colaborador del repo, o git no está autenticado en esa máquina).

### 3. Uso

Tras instalar, cada skill queda *namespaced* por su plugin:

- `/aidd:aidd-sprint-planning`, `/aidd:aidd-requirements`, …
- `/sdd:native-ai-specs`
- `/boosters:booster-ux`, `/boosters:booster-uml`

También se activan por lenguaje natural y por sus comandos internos (`aidd sprint-planning`, `native-ai open change`, …).

### Activación automática por proyecto (equipo)

En `.claude/settings.json` de un proyecto puedes registrar el marketplace y preactivar los plugins para todo el equipo (cada miembro necesita acceso al repo privado):

```json
{
  "extraKnownMarketplaces": {
    "aidd-sdd": { "source": { "source": "github", "repo": "grananda/aidd-marketplace" } }
  },
  "enabledPlugins": {
    "aidd@aidd-sdd": true,
    "sdd@aidd-sdd": true,
    "boosters@aidd-sdd": true
  }
}
```

## Metodología

La metodología AIDD-SDD viaja **dentro** de los plugins `aidd` y `sdd` (carpeta `methodology/`). Los skills la referencian con `${CLAUDE_PLUGIN_ROOT}/methodology/native-ai-aidd-sdd.md`, así que resuelve tras instalar en cualquier repo. Es referencia de solo lectura; no se carga automáticamente.

## Mantenimiento

- **Versionado**: cada `plugin.json` fija `version` (semver). **Sube la versión al publicar cambios**; si no, los usuarios ya instalados no recibirán las novedades (Claude Code los cree en la misma versión). Tras subir cambios, los usuarios actualizan con `/plugin marketplace update aidd-sdd`.
- **Hacerlo público** (si algún día procede): `gh repo edit grananda/aidd-marketplace --visibility public`. La instalación entonces no requeriría credenciales.
- **Desarrollo local** antes de publicar: `claude --plugin-dir ./plugins/aidd` (un plugin suelto) o `/plugin marketplace add ./` (marketplace local); validar con `claude plugin validate ./`.

---

NTT DATA Spain GDN-e.
