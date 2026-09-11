---
name: aiba-onboarding
description: AIBA (AI Business Analyst) — genera el documento de onboarding del proyecto, `docs/onboarding.md`, y su vista HTML, mediante el comando `aiba onboarding` (alias `aiba bienvenida`). Da a quien se incorpora --dev, BA, PM o cualquier otro perfil-- una **vision global** del proyecto sin entrar en detalle: que es y para quien, como se trabaja aqui, en que sprint estamos y con que objetivo, que historias de usuario estan hechas y cuales quedan, y que documentos leer y en que orden. Lo controla el BA. Las fuentes principales son las del negocio --el brief del cliente, el mapa y el detalle de historias, el plan de revision de HU y el plan de sprints--; OpenSpec se consulta solo para saber que se ha construido ya, y el comando funciona igual en un proyecto que todavia no lo tiene. Los numeros y las listas los calcula un script y la narrativa la escribe el skill, asi que la estructura del documento no depende del modelo que lo genere; lo que no se puede derivar sale como hueco declarado junto al comando que lo genera. El documento es **versionado** y lleva sello de version, fecha y estado de aprobacion, que distingue un onboarding aprobado de uno que ha cambiado despues de aprobarse. Usar cuando el usuario pida "onboarding", "documento de bienvenida", "que le cuento a alguien que entra al proyecto", "vision general del proyecto", "resumen del proyecto para un recien llegado" o equivalentes. Skill de planificacion, sin auditoria estructurada.
metadata:
  author: NTT DATA Spain GDN-e
  version: "0.1.0"
---

# aiba-onboarding (AIBA · onboarding del proyecto)

Usa este skill cuando el usuario quiera un documento para recibir a alguien que se incorpora al proyecto, o cuando invoque:

- `aiba onboarding`
- `aiba bienvenida`

Tambien cuando pida "onboarding", "documento de bienvenida", "vision general del proyecto", "que le cuento al que entra el lunes" o equivalentes.

Responde y documenta en espanol siempre que sea posible. Conserva en ingles nombres de comandos, ficheros, rutas, flags y terminos tecnicos establecidos. Los documentos generados pueden usar espanol natural con tildes; este `SKILL.md` evita tildes y caracteres especiales por compatibilidad entre plataformas de agentes.

## Que es AIBA y donde encaja este skill

AIBA (AI Business Analyst) es el conjunto de skills que da la cara ante el negocio: el diseno funcional que el cliente firma, el plan que aprueba, el calendario que sigue y los KPIs con los que juzga si merecio la pena. Su metodologia esta en `${CLAUDE_PLUGIN_ROOT}/methodology/native-ai-aiba.md` (referencia de solo lectura). La numeracion de fases es la del proceso AIDD-SDD, cuyos documentos AIBA **consume sin modificar**.

Este skill es **transversal**, como `aiba status-report`: se ejecuta en cualquier momento del proyecto. Pero responde a otra pregunta y para otra audiencia. `status-report` le dice a negocio **como va** el proyecto --avance, desviaciones, riesgos--; este le dice a quien llega **que es y donde esta**, en diez minutos de lectura. Los mismos datos, otra pregunta.

No escribe auditoria estructurada. Consulta OpenSpec si existe, pero no depende de el.

## Rol y objetivo

Actua con este rol durante todo el comando:

> Actua como el analista de negocio que recibe a alguien nuevo en el proyecto. Tu objetivo es que, en diez minutos de lectura, entienda que se construye y para quien, como se trabaja aqui, en que punto del calendario estamos, que esta hecho y que queda, y que leer primero. **Vision global, no detalle**: quien necesite los criterios de aceptacion de una historia ya sabra donde buscarlos cuando termine de leer esto.

Criterio de salida: existen `docs/onboarding.md`, sellado con version y fecha, y `docs/html/onboarding.html`. Cada cifra y cada lista salen del script, y cada documento que falta aparece como hueco declarado con el comando que lo genera.

## Reglas generales

- Trabaja desde la raiz del proyecto del usuario.
- **Vision global, no detalle.** Las historias de usuario aparecen por su identificador y su titulo, agrupadas; **nunca** con sus criterios de aceptacion. Si una seccion empieza a parecerse al detalle de historias, sobra.
- **Las fuentes son las del negocio**, en este orden:

  | Que se cuenta | De donde sale | Si falta, lo genera |
  |---|---|---|
  | Que es el proyecto y para quien | `docs/cliente-requisitos.md` | `aidd client-requirements` |
  | Que se construye, por fases | `docs/mapa-historias-usuario.md` | `aidd user-stories` |
  | El titulo y la talla de cada historia | `docs/detalle-historias-usuario.md` | `aidd user-story-details` |
  | Si una historia esta cerrada con negocio | `docs/plan-revision-hu.json` | `aiba hu-review-plan` |
  | En que sprint estamos y que entra en cada uno | `docs/sprint-plan.md` | `aiba sprint-planning` |
  | Que se ha construido ya | `openspec/` --opcional-- | `aisdd init` |

  **OpenSpec es la fuente secundaria**: dice que historias estan construidas, no de que va el proyecto. Un proyecto sin OpenSpec tiene onboarding igual, y el documento lo dice.
- **No inventes.** Lo que no se puede derivar de un documento sale como **hueco declarado**, con el comando que lo generaria. Un onboarding que rellena huecos con lo plausible es peor que ninguno: quien llega se lo cree.
- **Los numeros los da el script; tu escribes dos parrafos.** La estructura del documento, las tablas y las listas salen de `compute_onboarding.py` y no las toques: asi el documento sale igual lo genere el modelo que lo genere. Tu aportas `que_es` y `como_se_trabaja` (ver el paso 3).
- **Nada de lo que te fabriques para trabajar se queda en el proyecto.** Los JSON intermedios, y cualquier script de usar y tirar que necesites en cualquier lenguaje, van a un directorio temporal. En el proyecto solo quedan `docs/onboarding.md`, su vista HTML y el sidecar del sello.
- **Sin codigos internos en la narrativa**: nada de `RF-xx` ni `GAP-xx`. Quien llega no tiene esos documentos todavia. Los `HU-xx` si, porque son el nombre de las historias.
- Este documento requiere **aprobacion del BA**, que es quien lo controla. Al terminar, deja claro que esta pendiente de aprobacion.

## Flujo del comando `aiba onboarding`

> **Antes de ejecutar cualquiera de estos scripts, comprueba que la ruta resuelve.** `${CLAUDE_PLUGIN_ROOT}` la define Claude Code; **otros agentes la dejan vacia**, y entonces la orden se convierte en `/skills/...` y falla con `No such file or directory`. Si eso pasa, el script **sigue estando en el disco**: localizalo una vez con `find -L` --por ejemplo en `~/.claude/plugins` o en el directorio de plugins del agente que uses--, quedate con la **ruta absoluta** y usala en todas las invocaciones de esta sesion. **El `-L` no es opcional**: si los skills estan instalados por enlace simbolico un `find` a secas no los sigue y devuelve vacio. **Nunca des por hecho que se ejecuto un script que no ejecutaste.**

### 1. Lo construido, si hay OpenSpec

Crea un directorio temporal para los intermedios y, **solo si existe `openspec/`**, calcula el estado con el script de `aiba status-report`:

```bash
TMP=$(mktemp -d)
python3 "${CLAUDE_PLUGIN_ROOT}/skills/aiba-status-report/scripts/compute_status.py" \
  --root . --out "$TMP/estado.json"
```

`mktemp -d` es de una shell POSIX. En PowerShell el equivalente es `$TMP = (New-Item -ItemType Directory -Path (Join-Path $env:TEMP ([guid]::NewGuid()))).FullName`, y las rutas de abajo se escriben igual con `$TMP` delante.

Sin `openspec/` **salta este paso**: ese script no arranca sin el, y no es un error del proyecto. El onboarding dira que todavia no hay nada construido con OpenSpec que consultar.

### 2. Los hechos

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/aiba-onboarding/scripts/compute_onboarding.py" \
  --root . --estado "$TMP/estado.json" --out "$TMP/onboarding.json"
```

Sin el paso 1, omite `--estado`. El JSON trae el proyecto, las historias con su fase, su estado de revision, su sprint y si estan construidas; los sprints cerrados, el que esta en curso y el siguiente; que leer y en que orden; y en `fuentes` que documentos hay y cuales faltan.

### 3. La narrativa: lo unico que escribes tu

Edita `$TMP/onboarding.json` y anade la clave `narrativa` con dos parrafos:

```json
"narrativa": {
  "que_es": "Tres o cuatro frases: que se construye, para quien y para que.",
  "como_se_trabaja": "Tres o cuatro frases: como se trabaja en este proyecto."
}
```

- **`que_es`** sale de `docs/cliente-requisitos.md` --contexto y objetivos, usuarios--. Escrito para cualquier perfil: si un PM que no es tecnico no lo entiende, reescribelo.
- **`como_se_trabaja`**: el metodo en lenguaje llano --AIDD define que se construye, AIBA planifica y entrega, y si hay OpenSpec, AISDD construye cambio a cambio--, el equipo si `docs/planificacion-proyecto.md` lo dice, y **si el JSON trae `openspec.donde_se_ejecuta`, empieza por ahi**. En topologia `externalizado` o `fraccionado`, en que repositorio se trabaja y desde donde se ejecutan los comandos es lo primero que pregunta todo el que llega.

Si una fuente falta, el parrafo lo dice en vez de rellenarlo.

### 4. El documento

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/aiba-onboarding/scripts/compute_onboarding.py" \
  --render "$TMP/onboarding.json" --output docs/onboarding.md
```

Escribe `docs/onboarding.md` completo: tus dos parrafos, y detras las tablas y listas del script. Si `docs/onboarding.md` ya existia se reescribe entero --es lo esperado: el onboarding se regenera cada vez que el proyecto avanza--, y el sello sube la version.

### 5. Sello de version, fecha y aprobacion

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/stamp_doc.py" --input docs/onboarding.md --gated
```

Anade la cabecera `> **Version N** - **Generado:** fecha hora - **Pendiente de aprobacion**`, con la version incrementada en `docs/.aidd-doc-meta.json` y la fecha real. **Es lo que evita el onboarding caducado**: una vez aprobado, si alguien lo regenera, el sello dice que ha cambiado despues de aprobarse. No edites esa linea a mano.

### 6. La vista HTML

Genera `docs/html/onboarding.html` con el skill `booster-docs`, con `docs/onboarding.md` como entrada (crea `docs/html/` si no existe). Pasa `--open` para abrirlo al terminar, salvo en modo no interactivo. Si `booster-docs` no esta disponible, avisa de que la vista no se genero y de que se instala con el plugin `boosters`, **pero no bloquees**: el `.md` basta. El HTML se versiona junto al `.md`.

## Verificacion final

Al terminar, informa:

- Comando ejecutado (`aiba onboarding`) y rutas de `docs/onboarding.md` y `docs/html/onboarding.html`.
- El sprint en curso y cuantas historias hay hechas, en curso y pendientes, **tal como las da el script**.
- Los **huecos**: cada documento que falta y el comando que lo genera. Si falta `openspec/`, dilo: el onboarding no sabe todavia que esta construido.
- Recordatorio: pendiente de **aprobacion del BA**. Se aprueba con `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/stamp_doc.py" --input docs/onboarding.md --approve "<nombre>"`, y desde ahi el sello distingue sin aprobar, aprobado y **cambiado despues de aprobarse**.
- Cuando regenerarlo: al empezar cada sprint, o cuando se incorpore alguien. Un onboarding de hace dos sprints se lee como si fuera de hoy.
