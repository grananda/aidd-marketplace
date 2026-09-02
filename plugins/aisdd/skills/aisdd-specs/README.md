# aisdd-specs

Skill para trabajar con especificaciones Native AI usando OpenSpec y coordinar la generacion de diagramas y prototipos con los skills `booster-uml` y `booster-ux`.

> **Alias legacy**: todo comando `aisdd <cmd>` tiene un alias equivalente `native-ai <cmd>` (herencia del antiguo plugin `sdd`). Los proyectos ya iniciados con `native-ai ...` siguen funcionando sin cambios; el prefijo primario y recomendado es `aisdd`.

## Estructura del skill

`SKILL.md` es el **indice**: reglas comunes, presupuesto de contexto y una tabla de que leer para cada tarea. El detalle vive en `references/`, un fichero por comando, y **se carga bajo demanda**.

```
SKILL.md                    indice + reglas comunes  (94 lineas)
references/
  init.md  roadmap.md  parallelism.md  preflight.md
  open-change.md  implement-change.md  close-change.md  lane.md
  prototype-ux.md  uml.md  jira.md  audit.md  scripts.md
scripts/
  audit.py  agents_block.py  check_mojibake.py  optimize_phasing.py
```

Antes era un unico fichero de ~1.300 lineas que se cargaba entero aunque el 90 % no aplicara al comando en curso.

## Resumen comandos

1. `aisdd init` — inicializa OpenSpec en el proyecto y comprueba dependencias.
2. `aisdd roadmap` — fasea el desarrollo y genera `docs/roadmap.md` y prompts asociados.
3. `aisdd open change [what-you-want-to-build]` — crea un cambio OpenSpec y genera los diagramas UML **solo si el change lo amerita** (flujos multi-componente, entidades nuevas, estados, integraciones; se omiten en changes triviales, con `aisdd uml` disponible bajo demanda).
4. `aisdd implement change [change-slug]` — ejecuta un pre-flight de dudas con el usuario y luego aplica las instrucciones del cambio OpenSpec indicado.
5. `aisdd close change [change-slug]` — archiva el cambio OpenSpec indicado (en roadmaps multilane, verifica antes que el change no escribio fuera de las rutas de su lane).
6. `aisdd lane [list | switch <lane-id> | status]` — consulta y cambia la linea de trabajo activa. Solo aplica a roadmaps `multilane`.
7. `aisdd prototype-ux [change-slug]` — lanza `booster-ux` por cada pantalla nueva del cambio.
8. `aisdd prototype-ux` — lanza `booster-ux` directamente siguiendo su flujo de preguntas.
9. `aisdd uml [change-slug]` — genera el HTML con diagramas del cambio usando `booster-uml`.

> **Skill hermano**: `aisdd amend change [descripcion]` (skill `aisdd-amend`) incorpora una modificacion a un change **ya abierto** y ejecuta solo ese delta, sin re-aplicar el change entero. Es la via operativa de la "Regla de corte" descrita en la seccion "Correcciones durante la implementacion" del `SKILL.md` de este skill.

## Requisitos

- Node.js y npm disponibles.
- OpenSpec instalado globalmente. Si falta, el comando `aisdd init` debe instalarlo con:

```bash
npm install -g @fission-ai/openspec@latest
```

- Plugin `boosters` instalado (trae `booster-ux` y `booster-uml`):

  ```
  /plugin install boosters@aidd-sdd
  ```

Si falta, el agente avisa y da ese comando. No hay rutas que comprobar: Claude Code resuelve los skills por nombre entre los plugins instalados.

## Comandos disponibles

### `aisdd init`

Inicializa Native AI Specs en el proyecto:

1. Comprueba si `openspec` esta instalado.
2. Si falta, instala `@fission-ai/openspec@latest`.
3. Ejecuta `openspec init`.
4. Comprueba la disponibilidad de `booster-ux` y `booster-uml`.
5. Pregunta si el proyecto es un desarrollo nuevo o un desarrollo ya existente.
6. Si es existente, solicita las rutas de los markdowns con documentacion funcional, tecnica y de arquitectura, y actualiza `config.yaml` de OpenSpec con ese contexto inicial (`project_context.design_docs`).
7. **Proyecto existente**: ademas de recoger la documentacion, analiza el codigo y **siembra las specs base** en `openspec/specs/<capability>/spec.md` — una fotografia del comportamiento actual real, con `UNKNOWN` para lo que no puede inferir y `LEGACY` para la deuda tecnica. Acuerda antes el alcance, propone la lista de capacidades para que la confirmes, y **no sobrescribe** specs que ya existan. Sin esa linea base, el primer `open change` especifica de cero lo que el codigo ya hace.
8. Detecta ademas la **capa de entrega de AIBA** si existe (`docs/planificacion-proyecto.md`, `docs/sprint-plan.md`, `docs/plan-revision-hu.md`, `docs/jira-sync.md`) y la registra en `config.yaml` (`project_context.delivery_docs`), avisando de forma no bloqueante si falta alguna pieza esperable. En particular, si el `sprint-plan.md` refleja un volcado a Jira pero falta `docs/jira-sync.md` o la seccion `jira:` (enlace perdido), avisa y ofrece **reconstruir el registro** leyendo las Stories existentes desde Jira (solo lectura contra Jira; jamas recrea issues). Comprueba tambien la disponibilidad de `booster-docs`.
9. Registra los comandos del skill en el `AGENTS.md` del proyecto (lo crea si no existe) dentro de un bloque delimitado por marcadores `<!-- BEGIN/END aisdd-specs commands -->`, que se reemplaza de forma idempotente en cada ejecucion sin tocar el resto del fichero.

### `aisdd roadmap`

Fasea el desarrollo a partir de los requisitos y la arquitectura del proyecto antes de crear cambios OpenSpec.

Si el usuario no ha pasado requisitos o arquitectura, o el agente no tiene claro donde estan, debe solicitarlos antes de continuar.

**Numero de fases**: el comando lo pregunta ofreciendo siempre **automatico** como opcion recomendada (lo decide el agente siguiendo la pauta de changes pequeno-medio, el presupuesto de contexto y las fronteras de sprint). El usuario puede fijarlo (exacto, minimo o maximo), pero **fijar el numero no fija el reparto**: como se distribuye el trabajo entre esas fases sigue siendo criterio del agente, que debe dejarlas de magnitud comparable (ninguna por encima del doble de la mediana de las demas), con las excepciones de F0, las barreras y las fases aisladas por riesgo o validacion compleja. Ver "Equilibrio de fases" en el `SKILL.md`.

La granularidad del roadmap debe adaptarse al presupuesto de contexto del modelo usado:

- contexto `bajo` (hasta 64k tokens utiles): normalmente `6-12` fases pequenas
- contexto `medio` (64k-200k): normalmente `4-8` fases
- contexto `alto` (mas de 200k): normalmente `3-6` fases

Si no se conoce el modelo real o su ventana de contexto, se debe asumir `medio`. Si la documentacion y el impacto tecnico son muy grandes, se deben crear mas fases aunque el modelo tenga mucho contexto.

El comando genera:

- `docs/roadmap.md`: division del desarrollo por fases, alcance de cada fase, dependencias, entregables OpenSpec esperados y criterios de cierre.
- `docs/prompts-roadmap-native-ai.md`: prompts para ejecutar el roadmap hasta el final usando los comandos del skill `aisdd-specs`.

**Alineacion con el sprint-plan**: si existe `docs/sprint-plan.md` (generado por `aiba sprint-planning`), el roadmap **se pliega a los sprints**: respeta su orden, corta las fases en fronteras de sprint, mantiene los changes de una HU dentro de la ventana de su sprint y no fasea HU no validadas; anota en cada fase el sprint, las HU cubiertas y el esfuerzo (humano e IA), y documenta las discrepancias en una seccion de conflictos de alineacion roadmap↔sprint. Sin `sprint-plan.md`, fasea solo por presupuesto de contexto.

**Cambiar de modo a mitad de proyecto no deberia mover el sprint-plan.** El reparto en sprints esta acordado con el negocio y a veces volcado a Jira, asi que la conversion conserva el `change_hint` de cada fase, que es la clave con la que `sprint-plan.md` y Jira se enganchan: renombrar una fase a `F-<lane>-NN` no rompe nada. Solo lo rompen **partir una fase pendiente entre dos lanes** --nacen `change_hint` nuevos que no estan en ningun sprint-- y **reordenar pendientes de forma que cambien de sprint**. En esos dos casos el comando **no reescribe** `sprint-plan.md`: registra el conflicto y avisa de que re-ejecutar `aiba sprint-planning` es seguro y no recrea Stories. Re-empaquetar sprints es decision del negocio, no del faseado.

**Roadmap ya existente**: si `docs/roadmap.md` ya existe, el comando **no lo sobrescribe sin preguntar**. Ofrece **anotar** (conservar el faseado tal cual y anadir solo la capa de oleadas — disponible solo en modo `waves`, porque una oleada es una anotacion y no altera las fases; no cambia ningun `change_hint`, asi que no rompe el enlace con el sprint-plan ni con Jira) o **re-fasear** (regenerar el roadmap completo, obligatorio si el modo destino es `multilane`). En topologia `fraccionado` hay un tercer camino, **adoptar**, que es el normal en todos los repos menos uno: el documento viene copiado, no se toca, y solo se derivan de el las fases de este lane.

**Modo del roadmap**: el comando resuelve primero `parallel_developers` (devs en paralelo; con `1` el roadmap es secuencial) y despues el modo entre tres: `atomic` (un unico change abierto, comportamiento clasico), `waves` (oleadas: hasta `parallel_developers` fases a la vez respetando `depends_on`; **ordena el trabajo pero no garantiza aislamiento** — ningun comando conoce las oleadas ni verifica nada) y `multilane` (el roadmap se fracciona en lineas de trabajo paralelas con un change abierto **por lane**, con rutas declaradas y verificadas al cerrar). Para multilane propone un numero de lanes calculado como `min(modulos disjuntos de arquitectura-base.md, devs de implementacion de planificacion-proyecto.md)` —con su justificacion, para que el usuario no tenga que adivinarlo— y lo negocia hasta un acuerdo real; rechaza mas lanes que devs (no aporta paralelismo) o que modulos disjuntos (los lanes se pisarian). En `multilane`, las fases pasan a nombrarse `F0` (foundation), `F-<lane-id>-NN` (fase de lane) y `FB-NN` (barrera que bloquea todos los lanes: contrato, migracion, permisos, rollout), y `docs/roadmap.md` gana las secciones "Lanes" y "Dependencias cross-lane"; los lanes se prefieren independientes pero admiten **dependencias declaradas** (`depends_on`) cuando la independencia total no es viable, siempre que sean puntuales, aciclicas, con coste explicito y sin compartir rutas. En `waves`, `docs/roadmap.md` gana la seccion "Oleadas" con el ancho de cada una frente a `parallel_developers`. El grafo `depends_on` se escribe en los tres modos.

**El modo no se elige si hay varios repositorios.** Si la seccion 3 de `docs/arquitectura-base.md` declara mas de uno --basta con el nombre; ni URL ni ruta--, el modo es `multilane` con **un lane por repo**, no se pregunta y **no se ejecuta el pre-flight de optimizacion**: no hay caminos que comparar cuando la frontera de despliegue ya partio el trabajo. Ahi no hay `F0` ni barreras, cada repo tiene su propio `openspec/` y su copia completa de `docs/`, y el faseado **se ejecuta una sola vez** en el repo que tiene los documentos de diseno: el humano copia `docs/` a los demas y en cada uno `aisdd roadmap` toma el camino **adoptar** --lee el documento ya escrito, deriva sus fases al `config.yaml` y no re-fasea ni pregunta nada--. Con un solo repo no se fuerza nada.

Tras generar esos documentos, el comando actualiza `openspec/config.yaml` con una seccion `roadmap` (presupuesto de contexto, complejidad, rutas de los documentos y la lista ordenada de fases con su objetivo, riesgo de contexto y slug sugerido), para que los comandos posteriores dispongan de un indice navegable del roadmap.

Ademas, registra la configuracion de paralelismo (modo, `parallel_developers` y, en `multilane`, los lanes con sus rutas) en un bloque idempotente **propio** de `AGENTS.md` (`<!-- BEGIN/END aisdd-specs roadmap -->`), hermano e independiente del bloque de comandos que gestiona `aisdd init`, para que cualquier agente sepa como se trabaja en paralelo sin abrir `config.yaml`.

**Tamano de los changes**: salvo indicacion contraria, cada fase se dimensiona como un change **pequeno-medio** (quien valida es un humano). Es una preferencia, no una autoridad: no parte una fase si con ello rompe una frontera de sprint o saca una HU de su ventana (ver "Jerarquia de criterios de faseado" en el `SKILL.md`).

Este comando no debe ejecutar `openspec new change` ni archivar cambios, ni editar artefactos de `openspec/` distintos de `openspec/config.yaml`.

El fichero `docs/prompts-roadmap-native-ai.md` debe usar como base operativa estos comandos:

- `aisdd open change [what-you-want-to-build]`
- `aisdd implement change [change-slug]`
- `aisdd close change [change-slug]`

Los prompts deben incluir el contexto minimo necesario para cada fase y evitar arrastrar informacion de fases futuras si no es necesaria todavia.

### `aisdd open change [what-you-want-to-build]`

Crea un cambio OpenSpec en dos fases:

1. **Pre-flight de dudas**: antes de generar los specs, el agente revisa el contexto disponible (objetivo del usuario, `docs/`, `README.md`, `config.yaml`, `AGENTS.md`, `CLAUDE.md`, roadmap si existe y cambios OpenSpec previos) y plantea al usuario las dudas reales que afecten al alcance y al diseño del cambio. Las **bloqueantes se preguntan siempre, sin límite**; las preferencias y confirmaciones se acotan por proyecto (sección `preflight` de `openspec/config.yaml`). Las respuestas se persisten en `openspec/changes/<change>/decisions.md` para alimentar `design.md`, `proposal.md` y los `spec.md`.
2. **Creación del cambio**:

   ```bash
   openspec new change <what-you-want-to-build>
   ```

**El argumento es siempre opcional.** Si no llega, el agente no inventa un identificador: resuelve **que fase del roadmap toca abrir** entre las abribles ahora (no archivadas, con sus `depends_on` cerradas y —en `multilane`— del lane activo si es fase de lane, o con todos los lanes libres si es barrera). Con varias, las presenta con su contexto y deja elegir. El guard de apertura se aplica **despues**, ya sobre la fase elegida.

Tras crear el cambio, el agente evalua si los diagramas aportan comprension real (interaccion multi-componente, entidades o relaciones nuevas, maquina de estados, flujo con ramificaciones, integracion externa) y solo entonces pasa `design.md`, `proposal.md` y los ficheros `spec.md` al skill `booster-uml`. En changes triviales (scaffolding, config, textos, bugfix puntual) se omite con aviso; `aisdd uml [change-slug]` los genera bajo demanda. En caso de duda, se generan.

Comportamientos clave del pre-flight:

- No pregunta lo que ya esté resuelto en el objetivo del usuario, en `docs/` (incluido `docs/roadmap.md` si existe), convenciones del repo (`README.md`, `CLAUDE.md`, `AGENTS.md`, `config.yaml`) ni en cambios OpenSpec previos relacionados.
- Clasifica cada duda como `bloqueante`, `preferencia` o `confirmacion`. Las `bloqueantes` (alcance, dominios afectados, integraciones, modelo de datos, criterios de aceptación) **se plantean todas**: no se descartan ni se sustituyen por una recomendación automática. Si la interfaz no admite tantas preguntas de una vez, se divide en tandas.
- Si la plataforma soporta preguntas estructuradas con opciones (por ejemplo `AskUserQuestion` en Claude Code), las usa con una opción marcada `(Recomendada)`. En caso contrario presenta una lista numerada en texto plano.
- En modo no interactivo toma el default recomendado para `preferencia` y `confirmacion`, marca cada decisión con `Origen: auto-default` y, si hay `bloqueantes` sin default seguro, detiene el comando sin ejecutar `openspec new change`.
- Si tras la lectura inicial no detecta dudas reales, registra una única entrada con `Tipo: confirmacion`, `Pregunta: No se detectaron dudas durante el pre-flight` y `Decision: continuar`, y procede a crear el cambio.

### `aisdd implement change [change-slug]`

Implementa un cambio en dos fases:

1. **Pre-flight de dudas**: antes de tocar codigo, el agente lee `design.md`, `proposal.md`, los `spec.md` y, si existen, `tasks.md` y `decisions.md` previos del cambio. Detecta dudas reales que afecten a la implementacion y las clasifica como `bloqueante`, `preferencia` o `confirmacion`. **El pre-flight es el mismo para ambos comandos**: una sola seccion del `SKILL.md` con variantes `[APERTURA]` / `[IMPLEMENTACION]`, para que las reglas no se desincronicen. Las respuestas se persisten en `openspec/changes/<change>/decisions.md`.
2. **Aplicacion de instrucciones**:

   ```bash
   openspec instructions apply --change <change-slug>
   ```

**El argumento es siempre opcional.** Si no llega, el agente reune los candidatos y: con **uno**, lo usa y lo dice; con **varios**, los presenta con el contexto que permite reconocerlos —fase y objetivo en `atomic`, ademas la oleada en `waves`, ademas el lane en `multilane`— y deja elegir, marcando `(Recomendada)` solo si tiene criterio real. **Nunca elige en silencio.** En modo no interactivo con varios candidatos, se detiene y audita con `status: aborted`. Los candidatos son los changes **abiertos** (`openspec list`).

Comportamientos clave del pre-flight:

- No pregunta lo que ya esta resuelto en `design.md`, `proposal.md`, convenciones del repo (`README.md`, `CLAUDE.md`, `AGENTS.md`, `docs/`, `config.yaml`) o en `decisions.md` previos.
- Si la plataforma soporta preguntas estructuradas con opciones (por ejemplo `AskUserQuestion` en Claude Code), las usa con una recomendacion marcada `(Recomendada)`. En caso contrario presenta una lista numerada en texto plano.
- En modo no interactivo toma el default recomendado para `preferencia` y `confirmacion`, y marca cada decision con `Origen: auto-default`. Para `bloqueantes` sin default seguro detiene el comando.
- Si una duda bloqueante queda `Decision: pendiente`, no ejecuta `openspec instructions apply`.

### `aisdd lane [list | switch <lane-id> | status]`

Selecciona la **linea de trabajo activa** del dev, igual que `git switch` selecciona rama. No mueve codigo ni toca changes: solo dice sobre que lane operan los siguientes `open` / `implement` / `close change`.

- `list` — lanes del roadmap con su perfil, rutas, change abierto (si lo hay) y fase siguiente; marca el activo y lista las barreras pendientes.
- `switch <lane-id>` — escribe el lane en `openspec/.lane`. Siempre esta permitido **salvo en topologia `fraccionado`**, incluso con un change abierto en el lane que dejas: ese change sigue vivo y te espera. El guard de "un change por lane" vive en `open change`, no aqui.
- `status` (o sin subcomando) — lane activo, su change abierto, su fase siguiente y las barreras que lo bloqueen.

El puntero `openspec/.lane` es **estado local de cada dev** y va en `.gitignore` (lo anade `aisdd init`): dos personas trabajando lanes distintos no deben pisarse el puntero en cada commit. Si el roadmap es `atomic`, el comando avisa de que el proyecto no usa lanes y no crea nada.

**Con el producto en varios repositorios el puntero no se usa y el lane no se elige: se infiere.** Cada repo es un lane. Se resuelve por `roadmap.repo`; si falta, por el **nombre del repo** contra los `lane-id`; y si no coincide ninguno o coincide mas de uno, **se pregunta** — nunca por descarte ni por parecido, porque trabajar con el lane equivocado abre changes de otro repo y no se nota hasta mucho despues. `aisdd lane switch` se rechaza: se cambia de lane cambiando de repositorio.

Cada repo lleva su propio `openspec/` y su copia de `docs/`; `list` y `status` siguen sirviendo, pero de los otros lanes **solo saben lo que el roadmap declara** — no si tienen un change abierto, que eso vive en un `openspec/` que no esta aqui. Los KPI del proyecto completo salen de `aiba status-report` con un `--root` por repo.

### `aisdd close change [change-slug]`

Archiva un cambio:

```bash
openspec archive <change-slug>
```

**El argumento es siempre opcional.** Si no llega, el agente reune los candidatos y: con **uno**, lo usa y lo dice; con **varios**, los presenta con el contexto que permite reconocerlos —fase y objetivo en `atomic`, ademas la oleada en `waves`, ademas el lane en `multilane`— y deja elegir, marcando `(Recomendada)` solo si tiene criterio real. **Nunca elige en silencio.** En modo no interactivo con varios candidatos, se detiene y audita con `status: aborted`. Los candidatos son los changes **abiertos**; en `multilane` se miran **primero los del lane activo**: si ese lane tiene exactamente uno, lo usa sin preguntar, porque el trabajo vivo de otros lanes no genera ambiguedad.

### `aisdd prototype-ux [change-slug]`

Identifica las pantallas nuevas del cambio indicado y lanza el skill `booster-ux` por cada pantalla.

### `aisdd prototype-ux`

Lanza directamente el skill `booster-ux` y sigue su flujo de preguntas.

### `aisdd uml [change-slug]`

Genera el HTML con diagramas asociados al cambio indicado usando `booster-uml`. El argumento se resuelve igual que en `implement change`: si falta, candidatos = changes abiertos, y con varios se presentan con su contexto. Las entradas esperadas son:

- `design.md`
- `proposal.md`
- ficheros `spec.md`

## Ejemplos de uso

```text
aisdd init
```

```text
aisdd roadmap
```

```text
aisdd open change alta-de-clientes-desde-portal-web
```

```text
aisdd implement change alta-clientes-portal
```

```text
aisdd prototype-ux alta-clientes-portal
```

```text
aisdd uml alta-clientes-portal
```

```text
aisdd close change alta-clientes-portal
```

## Scripts del skill

Cuatro scripts en `scripts/`, solo con biblioteca estandar de Python 3:

| Script | Que hace |
|---|---|
| `audit.py` | Compone y persiste la entrada JSONL de auditoria: hashes SHA-256, agregados, purga por retencion. Recibe por stdin lo que solo el agente sabe (comando, modelo, decisiones, rutas) y rellena `id`, `timestamp` y hashes |
| `agents_block.py` | Reemplazo idempotente de un bloque delimitado de `AGENTS.md` (`commands` o `roadmap`), sin tocar el resto del fichero ni el otro bloque. Migra bloques legacy `native-ai-specs` |
| `optimize_phasing.py` | Calcula el calendario de cada modo de faseado con cada numero de developers, encuentra el optimo y emite un HTML con los caminos enfrentados. **Obligatorio** en `aisdd roadmap` salvo con un solo dev |
| `check_mojibake.py` | Detecta (y con `--fix` repara) UTF-8 mal interpretado como Latin-1/CP1252. **Obligatorio** en `init`, `roadmap` y `open`/`implement`/`close change`, justo antes de la entrada de auditoria y solo sobre los artefactos documentales, nunca sobre codigo fuente |

Cubren las tres mecanicas que antes eran prosa que el agente debia ejecutar bien **cada vez**. Son exactas o no son, y una equivocacion no deja rastro de cuando ocurrio.

**Degradacion**: si Python no esta disponible o el script falla, el comando no se bloquea — el agente hace el trabajo segun la prosa del `SKILL.md`, que se mantiene como especificacion, y lo dice en el resumen.

## Auditoria y trazabilidad

**La auditoria es obligatoria**, no un extra: cada invocacion escribe una entrada estructurada en JSON Lines bajo `openspec/audit/YYYY-MM.jsonl` (`aisdd lane` queda fuera: solo mueve un puntero local del dev) (un fichero por mes natural, modo append-only). El objetivo es permitir auditorias futuras del uso del skill.

Campos minimos de cada entrada:

- `id`, `timestamp` (UTC ISO 8601), `command`, `change_id`
- `skill_version`, `prompt_version` (formato `<skill_version>:<command-slug>`)
- `model`, `platform`, `user`
- `input_hash` y `input_files[]` con SHA-256 por fichero
- `output_hash` y `output_files[]` con SHA-256 por fichero
- `decisions[]` con `slug`, `type`, `origen`, `decision` (solo para `open change` e `implement change`, los dos que ejecutan pre-flight; incluye tambien las entradas `Tipo: correccion` de la implementacion)
- `notes[]`: acciones con efecto externo que no son ficheros y por tanto no caben en `output_files`. Hoy solo Jira, p. ej. `"ABC-45 -> Done"`
- `status` (`ok | partial | aborted`), `errors[]`

Comportamiento clave:

- Solo se guardan **hashes** de los ficheros, nunca el contenido literal.
- No se registran secretos, tokens, credenciales ni texto libre de las dudas del pre-flight (eso vive en `decisions.md`).
- Si el comando se aborta (por ejemplo dudas bloqueantes pendientes), igualmente se escribe la entrada con `status: aborted`.

**Retencion**: por defecto `365` dias. Sobreescribible por proyecto en este orden de precedencia:

1. `audit.retention_days` en `config.yaml` de OpenSpec
2. Fichero `openspec/audit/.retention` con el numero de dias en la primera linea
3. Default `365`

La purga es por meses completos: cuando el ultimo dia del mes representado por un `YYYY-MM.jsonl` es anterior a `hoy - retencion`, el fichero se elimina **en la misma invocacion que escribe la entrada** (lo hace `audit.py`), no en la siguiente. La purga es por meses comando. Nunca se aplica retencion inferior a `30` dias.

El JSONL es plano y sin transformaciones, listo para ingestar en Splunk, ELK o BigQuery. La decision de versionar `openspec/audit/` en Git es del proyecto.

## Resultado esperado

El agente debe informar siempre de:

- comando Native AI solicitado
- comando OpenSpec ejecutado
- cambio objetivo, si aplica
- artefactos creados o actualizados (incluye `decisions.md` si hubo pre-flight)
- decisiones tomadas en el pre-flight y cuales quedan `pendientes`, si aplica
- entrada de auditoria escrita: ruta del fichero `openspec/audit/YYYY-MM.jsonl`, `id` y `status` (`ok`, `partial` o `aborted`). Un comando que se detuvo tambien deja entrada: la ausencia no es un resultado valido salvo en `aisdd lane`
- resultado de `check_mojibake.py` sobre los artefactos escritos, y que ficheros quedan sin reparar (los que tengan `U+FFFD` hay que regenerarlos)
- **proximos pasos**: hasta tres comandos ejecutables, resueltos segun el estado. Tras `roadmap` encadena con `aiba project-plan` / `aiba sprint-planning`, que consumen el roadmap; tras `close change`, con la siguiente fase abrible — incluido el `aisdd lane switch` previo si es de otro lane, o los lanes que faltan por cerrar si lo que toca es una barrera
- skills auxiliares usados o pendientes de instalar
- errores o tareas manuales pendientes
