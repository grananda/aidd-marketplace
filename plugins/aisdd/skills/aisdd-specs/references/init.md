# `aisdd init`

> Referencia del skill `aisdd-specs`. El indice y las reglas comunes estan en `SKILL.md`.

## `aisdd init`

> Alias: `native-ai init`.

Inicializa AISDD (OpenSpec) en el proyecto.

1. Comprueba si `openspec` esta disponible (`Get-Command openspec` o equivalente).
2. Si no esta disponible, instala OpenSpec:
   ```bash
   npm install -g @fission-ai/openspec@latest
   ```
3. Ejecuta:
   ```bash
   openspec init
   ```
4. Comprueba `booster-ux`, `booster-uml` y `booster-docs` segun la seccion de dependencias.
5. Pregunta si el proyecto es:
   - desarrollo nuevo
   - desarrollo ya existente
6. Si es nuevo, resume la inicializacion y los siguientes pasos.
7. Si es existente, solicita/auto-detecta los markdown del proyecto, en **dos grupos**:
   - **Diseno y definicion** (funcional, tecnica y de arquitectura): p. ej. `docs/requisitos.md`, `docs/mapa-historias-usuario.md`, `docs/detalle-historias-usuario.md`, `docs/arquitectura-base.md`, `docs/propuesta-arquitectura-base.md`, `docs/guia-estilos.md`.
   - **Capa de entrega (AIBA)** — **no la ignores**: `docs/planificacion-proyecto.md` (recursos, equipo, esfuerzo humano vs IA), `docs/sprint-plan.md` (sprints, capacidad, asignaciones), `docs/plan-revision-hu.md` (estado de validacion de HU) y `docs/jira-sync.md` (mapeo HU<->Story<->change). Busca estos ficheros en `docs/` y, si existen, inclúyelos; si no, no pasa nada (son opcionales).
8. Cuando tengas las rutas, actualiza `config.yaml` de OpenSpec con ese contexto inicial. Manten el formato YAML existente; crea/actualiza `project_context` con **dos sub-listas** para que los comandos posteriores sepan que existe cada plano:
   ```yaml
   project_context:
     design_docs:            # diseno y definicion
       - docs/requisitos.md
       - docs/detalle-historias-usuario.md
       - docs/arquitectura-base.md
     delivery_docs:          # capa de entrega AIBA (solo las que existan)
       - docs/planificacion-proyecto.md
       - docs/sprint-plan.md
       - docs/plan-revision-hu.md
       - docs/jira-sync.md
   ```
   Si ya existe un `project_context` plano (formato antiguo), conserva su contenido y reorganizalo en estas dos sub-listas sin perder rutas.
9. **Si es existente, siembra las specs base.** Con la documentacion ya recogida (paso 7) y volcada a `config.yaml` (paso 8), ejecuta el flujo **"Onboarding de proyecto existente"** de la seccion siguiente. En proyecto **nuevo** saltate este paso: no hay codigo que fotografiar.
10. **Siembra la configuracion del pre-flight.** Anade a `openspec/config.yaml` la seccion `preflight` con los valores por defecto, si no existe ya:
   ```yaml
   preflight:
     preferencias: all      # all | entero >= 0
     confirmaciones: all    # all | entero >= 0
   ```
   Regula **cuantas dudas no bloqueantes** plantean `open change` e `implement change` (ver "Configuracion del pre-flight" (`references/preflight.md`)). **No toca las bloqueantes**, que se preguntan siempre. Si la seccion ya existe, **no la sobrescribas**: es una preferencia del equipo. Menciona en el resumen que se puede ajustar.
11. **Resuelve la topologia antes de nada, porque este comando es el que crea `openspec/`.** Son tres y **no se deducen**: ver "Las tres topologias" (`references/parallelism.md`).

    - Si `openspec/config.yaml` ya trae `roadmap.topology`, respetala.
    - Si no, **preguntala** con `AskUserQuestion`, con `mono` como recomendada y el intercambio dicho:

    | Topologia | Cuando |
    |---|---|
    | **`mono` (Recomendada)** | Un repo. `openspec/` y `docs/` dentro. Es el caso normal |
    | **`fraccionado`** | Varios repos, cada uno con su `openspec/` y su copia de `docs/`. Un lane por repo. Se paga replicando `docs/` |
    | **`externalizado`** | Uno o varios repos de codigo, y `openspec/` + `docs/` en un **repositorio git aparte**. Se elige cuando las specs no pueden vivir en el repo de codigo |

    **La pregunta va aqui y no en `aisdd roadmap`**: para cuando se fasea, `openspec/` ya existe y ya esta en un sitio. `roadmap` la respeta y solo puede cambiarla como migracion.

    **En `mono`** no hay nada mas que hacer: sigue.

    **En `fraccionado`, `aisdd init` se ejecuta una vez por repo**, dentro de cada uno, y cada ejecucion crea el `openspec/` de ese repo. Identifica cual es, en este orden: (a) si el config ya trae `roadmap.repo`, ese es; (b) si el nombre de la carpeta o el ultimo segmento de `git remote get-url origin` coincide con un `id` de la tabla de la seccion 3 de `docs/arquitectura-base.md`, proponlo; (c) **si no, preguntaselo** con la lista de `id` disponibles. **No lo decidas por parecido ni por descarte**: elegir mal hace que este `openspec/` ejecute las fases de otro lane, y no se ve hasta que alguien abre un change que no le tocaba. Escribe `roadmap.topology: fraccionado` y `roadmap.repo: <id>`, y recuerda que **`docs/` va copiado entero en cada repo**.

    **En `externalizado`, `aisdd init` se ejecuta en el repo de gobierno**, no dentro de ningun repo de codigo --es la unica vez, junto con `aisdd roadmap`, que alguien tiene que estar ahi: los comandos del dia a dia se lanzan desde el repo de codigo--. Ahi:

    - **Comprueba que es un repositorio git** (`git rev-parse --git-dir`). Si no lo es, **detente**: la trazabilidad de la auditoria y la recuperacion de estados anteriores dependen de eso, y sin ello la topologia no se sostiene. Ofrece `git init` y espera respuesta; no lo hagas por tu cuenta.
    - Escribe `roadmap.topology: externalizado` y la lista `roadmap.repos` con el `id` y la **ruta relativa a este repo** de cada repo de codigo --uno o varios--. Verifica que cada ruta existe y es un repositorio git, y **avisa sin bloquear** de lo que no cuadre.
    - **Escribe el `.gitignore` del repo de gobierno con el `path` de cada repo de codigo.** Es obligatorio y va aqui: sin el, un `git add -A` en el repo de gobierno se traga los repos de codigo enteros. Comprueba ademas que cada `path` es una **subcarpeta** de este repo; si alguno esta fuera del arbol, el layout esta mal montado y **el resto no va a funcionar** --el CLI de openspec no encuentra su carpeta subiendo--: dilo y no sigas como si nada.
    - **Revisa los rastros en cada repo de codigo** y enumeralos en el resumen, sin tocar nada. Ver "Rastros en el repo de codigo" (`references/governance-repo.md`).
    - Di el **ritmo de trabajo** y, sobre todo, **donde se ejecuta cada cosa**: `init` y `roadmap` aqui; `open`, `implement`, `amend` y `close` **desde el repo de codigo**, sin cambiar de carpeta. Mas el commit y push de este repo al final de cada comando, y `close change` siempre despues de que la PR del repo de codigo este mergeada (`references/governance-repo.md`).

    **No clones ningun repo.** Elegir remote, rama y credenciales es del humano.

12. **Check ligero (no bloqueante).** AISDD **asume** que la planificacion de AIBA es correcta; no la re-valides a fondo. Limitate a avisar en el resumen si: (a) alguna ruta indicada no existe; (b) hay `sprint-plan.md`/`planificacion-proyecto.md` pero falta el detalle de HU que los sustenta; (c) **no** hay capa de entrega (ni `sprint-plan.md` ni `planificacion-proyecto.md`) — en ese caso informa de que `aisdd roadmap` faseara sin alinear a sprints; o (d) `sprint-plan.md` menciona un **volcado a Jira** (Stories/claves creadas) pero falta `docs/jira-sync.md` o la seccion `jira:` — **enlace perdido**: avisa de que la integracion Jira de los changes se omitira y ofrece reconstruirlo (ver "Reconstruccion del enlace perdido" (`references/jira.md`)). Son avisos, no errores: continua igualmente.
13. **Declara la auditoria como union en `.gitattributes`.** Asegura que el fichero **de este repo** --el que contiene `openspec/`, o sea el de gobierno en `externalizado`-- contiene la linea `openspec/audit/**/*.jsonl merge=union`. Si no existe, crealo con esa unica linea; si existe y ya la contiene, no lo toques.

    El registro es append-only y **un fichero por escritor** ya evita el conflicto normal; esta linea cubre el que queda: la misma persona trabajando dos ramas. Sin ella, git para el merge por dos lineas que solo hay que concatenar. Hazlo siempre, tambien en `atomic`: es idempotente y evita tener que acordarse el dia que entra un segundo dev.

14. **Ignora el puntero de lane.** Asegura que el `.gitignore` **de este repo** --el que contiene `openspec/`-- lleva una linea `openspec/.lane`. (En topologia `fraccionado` ese puntero no se usa —el lane es el repo—, pero anadela igual: es idempotente y no cuesta nada.) Si el fichero `.gitignore` no existe, crealo con esa unica linea; si existe y ya la contiene, no lo toques. Ese fichero es el lane activo de **cada dev** y no debe versionarse (ver "Lanes"). Hazlo siempre, tambien en proyectos que arrancan en modo `atomic`: es idempotente y evita tener que recordarlo si mas adelante se pasa a multilane.
14.bis. **Deja el registro de actividad funcionando, tambien fuera de Claude Code.**

   El registro (`docs/aidd-activity.md`) es de donde `aiba metrics` saca el tiempo atendido. Lo escribe el hook `aidd-activity-hook.sh` que traen los plugins, y es **opt-in**: sin el fichero no se registra nada.

   - **Ofrece crearlo.** Preguntalo aqui y no despues: la ventana de medicion **no se reconstruye**. Si el usuario dice que no, no insistas y dilo en el resumen.
   - **Declara quien escribe el registro** en `openspec/config.yaml`. Es lo que evita que se registre por duplicado:

     ```yaml
     activity:
       source: hooks   # hooks | skills
     ```

     Con `hooks` manda el hook y `audit.py` no toca el registro; con `skills` lo escribe `audit.py` en cada comando. **Nunca los dos**: duplicar cada linea no falla, infla el tiempo atendido y la aceleracion sale mejor de lo que fue. Sin la clave se asume `hooks`, que es el comportamiento historico.

   - **Comprueba si el agente ejecuta los hooks de los plugins.** Claude Code si. **Codex no**: los registra en su `config.toml` y no llega a ejecutarlos --comprobado sobre 0.151.0--, asi que el registro quedaria vacio sin que nada avisara.
   - **Si no los ejecuta, pon `source: skills`.** Con eso `audit.py` registra lo que dura cada comando y `aiba metrics` recupera el tiempo atendido — **con una base mas estrecha**, que el informe declara: un comando no ve el tiempo de revisar, conversar ni iterar, y el hook si.

   - **Y si el agente admite hooks de proyecto, declaralos tambien**, que ahi si corren. Localiza el script del plugin instalado (con `find`, ver la nota de resolucion en `references/scripts.md`) y escribe `.codex/hooks.json` con su **ruta absoluta y sin comillas** --el comando no pasa por un shell, asi que unas comillas se convierten en parte de la ruta--:

     ```json
     {"hooks": {
       "PostToolUse":      [{"matcher": "*", "hooks": [{"type": "command", "command": "/ruta/absoluta/al/aidd-activity-hook.sh"}]}],
       "UserPromptSubmit": [{"hooks": [{"type": "command", "command": "/ruta/absoluta/al/aidd-activity-hook.sh"}]}],
       "Stop":             [{"hooks": [{"type": "command", "command": "/ruta/absoluta/al/aidd-activity-hook.sh"}]}]
     }}
     ```

   - **Si ya existe `.codex/hooks.json`, no lo pises**: anade solo lo que falte y di que habia.
   - **Avisa de que hay que confiar el hook una vez.** Codex guarda un hash de confianza por entrada y no lo ejecuta hasta que el usuario lo aprueba; ademas, **cada actualizacion del plugin que cambie el script exige volver a aprobarlo**, y hasta entonces el registro se para **sin dar error**. Es la primera cosa que mirar si las metricas se quedan planas.
   - **En Claude Code no escribas nada de esto**: sus hooks de plugin ya funcionan y un `.codex/hooks.json` ahi solo seria ruido.

15. Registra los comandos del skill en el `AGENTS.md` del proyecto segun la seccion siguiente.

16. **Comprueba el mojibake de lo que has escrito.** Es **obligatorio**, no opcional. Pasa `check_mojibake.py --fix` (ver `references/scripts.md`) sobre los artefactos **documentales** que este comando haya escrito: `openspec/config.yaml`, `AGENTS.md` y las specs base **si las sembraste** (en proyecto nuevo no hay). **Va aqui, antes de la entrada de auditoria, porque `audit.py` calcula el hash de cada fichero**: reparar despues dejaria registrado el hash de la version corrupta. Si algun fichero queda con `U+FFFD`, no se puede reparar — hay que regenerarlo; dilo en la verificacion final y no lo escondas.
17. **Escribe la entrada de auditoria.** Es obligatoria y **no es opcional para ningun comando salvo `aisdd lane`**. Componla con `audit.py` segun "Scripts del skill" (`references/scripts.md`), con el esquema y las reglas de "Auditoria y trazabilidad" (`references/audit.md`), y `prompt_version` = `<skill_version>:init`. Reporta despues su ruta y su `id` en la verificacion final. **Y si `roadmap.topology` es `externalizado`, commitea y sube el repo de gobierno** antes de dar el comando por terminado: una entrada que solo existe en un portatil no es un registro. Ver "Ritmo de commit y push" (`references/governance-repo.md`).
18. **Sugiere los proximos pasos.** Cierra diciendo **que hace el usuario ahora**, con el comando ya resuelto y listo para copiar. Sigue "Proximos pasos al terminar un comando" (`references/next-steps.md`), que dice cual toca segun el estado — modo, changes vivos, barreras bloqueadas, lane activo y si hay capa de entrega.

### Onboarding de proyecto existente: specs base

Cuando el proyecto ya esta en marcha, el objetivo es **capturar su estado actual como specs base de OpenSpec**, para que los changes posteriores tengan contra que contrastar. Sin esto, el primer `aisdd open change` genera specs sin linea base: no puede saber que ya existe, y acaba especificando de nuevo lo que el codigo ya hace.

Lo invoca el **paso 9 de `aisdd init`**, ya con la documentacion recogida y volcada a `config.yaml`. No lo ejecutes por tu cuenta desde otro comando.

**La regla que gobierna todo el flujo: esto es una fotografia de lo que HAY, no de lo que deberia haber.** La tentacion de "arreglar mientras documentas" es el fallo tipico de este paso, y produce specs que describen un sistema que no existe. Si algo esta mal hecho, se marca `LEGACY` y se deja como esta; corregirlo es trabajo de un change posterior.

1. **Acuerda el alcance antes de leer nada.** En un repo grande, analizarlo entero es caro y a menudo innecesario. Pregunta si se quiere cubrir **todo el codigo** o solo **los modulos donde va a haber trabajo**. Si el usuario no tiene criterio, propon tu el recorte a partir de la documentacion aportada y del roadmap si existe.
2. **Analiza codigo y documentacion juntos** para inferir las **capacidades ya implementadas**: modulos, endpoints, modelos de datos, flujos, integraciones, jobs. La documentacion dice la intencion; el codigo dice la realidad. **Cuando discrepen, manda el codigo** y anota la discrepancia.
3. **Propon la lista de capacidades y espera confirmacion.** Antes de escribir un solo fichero, muestra las capacidades detectadas con una linea cada una. Es barato de corregir aqui y caro despues: si el corte esta mal, todas las specs nacen mal. Escribir N ficheros sin validar el indice es el error a evitar.
4. **Genera las specs base** bajo `openspec/specs/<capability>/spec.md`, en formato OpenSpec, una por capacidad. Cada spec describe el **comportamiento actual real**:
   - basa cada afirmacion en algo que exista en el codigo o en la documentacion aportada
   - marca `UNKNOWN` lo que no puedas inferir con certeza — **es la salida honesta**, no un fallo. Una spec con `UNKNOWN` es util; una que se lo inventa es peor que no tenerla
   - marca `LEGACY` lo que no sigue buenas practicas: es deuda tecnica identificada, y sirve de insumo al roadmap
5. **No sobrescribas specs existentes.** Si `openspec/specs/` ya tiene contenido (de un `init` anterior o de trabajo previo), **no lo pises**: lista lo que ya hay, genera solo lo que falte y pregunta que hacer con lo que colisione. Re-ejecutar `init` no debe destruir specs revisadas por humanos.
6. **Validacion humana.** Resume las specs generadas y, por separado, **todas las marcas `UNKNOWN` y `LEGACY`**, que son lo que el humano tiene que revisar de verdad. Di explicitamente que son una fotografia inferida y que conviene contrastarla.
7. **No abras ni archives changes en este comando.** `init` inicializa; construir es de `open change`.
8. **Auditoria**: incluye en `output_files` las specs base generadas, `openspec/config.yaml` y `AGENTS.md`.

A partir de aqui el proyecto sigue el flujo normal: `aisdd roadmap` para fasear lo pendiente y el ciclo `open/implement/close change` para cada funcionalidad nueva, aplicando **deltas sobre estas specs base** en vez de partir de cero.

### Registro de comandos en `AGENTS.md`

El objetivo es que cualquier agente que lea el `AGENTS.md` del proyecto conozca los comandos disponibles del skill `aisdd-specs`.

1. Localiza `AGENTS.md` en la raiz del proyecto. Si no existe, crealo con una cabecera minima (`# AGENTS.md`) seguida del bloque de comandos.

   > **En topologia `externalizado`, "la raiz del proyecto" es el repo de gobierno, que es donde se ejecuta `init`. No escribas ni toques `AGENTS.md` en ningun repo de codigo.** Si la razon de externalizar es que ahi no aparezcan artefactos del metodo, crear ese fichero seria producir justo lo que se quiere evitar --y con el nombre mas reconocible de todos--. Que los devs trabajen sin el es el efecto buscado, no una carencia.
2. Si existe, conserva integro el resto del contenido. No reescribas ni reordenes secciones ajenas al skill.
3. Gestiona los comandos dentro de un bloque delimitado por marcadores HTML, para poder actualizarlo de forma idempotente en futuras ejecuciones:

   ```markdown
   <!-- BEGIN aisdd-specs commands (auto-generado, no editar a mano) -->
   ## Comandos aisdd

   Skill `aisdd-specs` v<skill_version>. Invoca estos comandos para trabajar con especificaciones AISDD / OpenSpec (prefijo primario `aisdd`; `native-ai <cmd>` sigue funcionando como alias legacy):

   - `aisdd init` — inicializa OpenSpec, comprueba dependencias y registra el contexto del proyecto (incluida la capa de entrega de AIBA).
   - `aisdd roadmap` — fasea el desarrollo (alineado al `docs/sprint-plan.md` si existe) y genera `docs/roadmap.md`, `docs/prompts-roadmap-native-ai.md` y la seccion `roadmap` de `openspec/config.yaml`.
   - `aisdd open change [what-you-want-to-build]` — pre-flight de dudas y creacion del cambio OpenSpec.
   - `aisdd implement change [change-slug]` — pre-flight de dudas y aplicacion de instrucciones del cambio.
   - `aisdd amend change [descripcion]` — incorpora una modificacion a un change ya abierto y ejecuta **solo ese delta**, sin re-aplicar el change (skill `aisdd-amend`).
   - `aisdd close change [change-slug]` — archiva el cambio OpenSpec.
   - `aisdd lane [list | switch <lane-id> | status]` — consulta y cambia la linea de trabajo activa (solo en roadmaps `multilane`).
   - `aisdd prototype-ux [change-slug]` — genera prototipos UX con `booster-ux`.
   - `aisdd uml [change-slug]` — genera el HTML de diagramas del cambio con `booster-uml`.
   <!-- END aisdd-specs commands -->
   ```

4. **Registra el bloque con `agents_block.py`** (marker `commands`), que hace el reemplazo idempotente por ti — ver "Scripts del skill" (`references/scripts.md`). Si no puedes ejecutarlo, hazlo a mano: si ya existe un bloque entre `<!-- BEGIN aisdd-specs commands ... -->` y `<!-- END aisdd-specs commands -->`, reemplazalo integramente por la version actual. **Migracion**: si en su lugar existe un bloque legacy `<!-- BEGIN native-ai-specs commands ... -->` / `<!-- END ... -->` (de la version `sdd` anterior), **reemplazalo** por el bloque `aisdd-specs` (no dejes ambos). Si no existe ninguno, anade el nuevo al final del fichero precedido de una linea en blanco.
5. Sustituye `<skill_version>` por la version real del frontmatter del skill.
6. Incluye `AGENTS.md` en los `output_files` de la entrada de auditoria de este comando.
