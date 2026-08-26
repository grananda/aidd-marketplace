---
name: aisdd-specs
description: AISDD (AI Spec-Driven Development) — gestiona especificaciones sobre OpenSpec mediante los comandos `aisdd init`, `aisdd roadmap`, `aisdd open change`, `aisdd implement change`, `aisdd close change`, `aisdd lane`, `aisdd prototype-ux` y `aisdd uml` (alias legacy equivalentes con prefijo `native-ai ...` siguen funcionando). Coordina documentacion funcional/tecnica/arquitectura y la capa de entrega de AIDD (planificacion-proyecto, sprint-plan, plan-revision-hu), roadmaps, diagramas con booster-uml y prototipos con booster-ux. `aisdd init` registra en `openspec/config.yaml` tanto la documentacion de diseno como la capa de entrega existente, y `aisdd roadmap` lee el `docs/sprint-plan.md` para fasear alineado a los sprints. Los comandos `open change` e `implement change` ejecutan un pre-flight de dudas (maximo 7 preguntas) antes de generar los specs y antes de aplicar las instrucciones de OpenSpec. Todos escriben una entrada de auditoria estructurada en `openspec/audit/` (salvo `aisdd lane`, que solo mueve un puntero local). Integracion opcional con Jira (MCP de Atlassian) con modelo hibrido por HU: si una HU se realiza con un solo change se opera directamente sobre su Story (sin sub-tarea); si se reparte entre varios changes, cada change es una sub-tarea bajo la Story. `open change` registra el enlace change<->HU (creando sub-tarea solo cuando toca), `implement change` mueve a In Progress las Stories de todas las HU que implementa (y su sub-tarea si existe), y `close change` las pasa a Done (una Story con sub-tareas solo cuando todas estan Done); sin configuracion, los comandos funcionan igual y la sincronizacion se omite — salvo que haya evidencia de un volcado previo sin registro (enlace perdido), en cuyo caso avisa y ofrece reconstruir `docs/jira-sync.md` leyendo las Stories desde Jira sin recrear issues. Durante `implement change`, los cambios que ningun spec habia especificado se clasifican en niveles con una regla de corte explicita (un documento AIDD solo se corrige cuando queda desmentido) y se registran como `Tipo: correccion` en `decisions.md`, sin escalar ni re-aplicar el change. Ofrece **tres modos de faseado**, elegidos en el pre-flight de `aisdd roadmap` y registrados en `roadmap.mode`: **`atomic`** (clasico, un change abierto), **`waves`** (oleadas: hasta `parallel_developers` fases a la vez respetando `depends_on`; ordena el trabajo pero **no garantiza** aislamiento ni lo verifica ningun comando) y **`multilane`** (lanes): `aisdd roadmap` puede fraccionar el faseado en lineas de trabajo (lanes) con rutas y specs disjuntas —nomenclatura `F0` / `F-<lane>-NN` / barreras `FB-NN`— para que varios devs trabajen en paralelo sin romper el invariante de un unico hilo por superficie de decision; `aisdd lane [list|switch|status]` selecciona la linea activa (puntero local `openspec/.lane`, tipo rama de Git), `open change` permite un change abierto **por lane**, `close change` verifica que el change no se salio de las rutas de su lane, y una correccion que toca el contrato compartido es nivel 4 (parada coordinada), no una correccion local. Los lanes se prefieren independientes, pero admiten **dependencias declaradas** (`depends_on`) cuando la independencia total no es viable, siempre que sean puntuales, aciclicas, con coste explicito y **sin compartir rutas**. Usar cuando el usuario invoque `aisdd ...` o `native-ai ...`, o pida trabajar con especificaciones OpenSpec/Native AI.
metadata:
  author: NTT DATA Spain GDN-e
  version: "1.6.0"
---

# aisdd-specs (AI Spec-Driven Development)

Usa este skill cuando el usuario pida trabajar con especificaciones AISDD / OpenSpec, o cuando invoque cualquiera de estos comandos (prefijo primario **`aisdd`**; el prefijo **`native-ai`** se mantiene como **alias legacy** equivalente):

- `aisdd init`            (alias: `native-ai init`)
- `aisdd roadmap`         (alias: `native-ai roadmap`)
- `aisdd open change [what-you-want-to-build]`       (alias: `native-ai open change ...`)
- `aisdd implement change [what-you-want-to-build]`  (alias: `native-ai implement change ...`)
- `aisdd close change [what-you-want-to-build]`      (alias: `native-ai close change ...`)
- `aisdd lane [list | switch <lane-id> | status]`    (alias: `native-ai lane ...`)
- `aisdd prototype-ux [what-you-want-to-build]`      (alias: `native-ai prototype-ux ...`)
- `aisdd uml [what-you-want-to-build]`               (alias: `native-ai uml ...`)

> **Alias legacy.** `aisdd <cmd>` y `native-ai <cmd>` son **equivalentes**: ejecutan exactamente el mismo flujo. `aisdd` es el prefijo primario (consistente con `aidd`/`aiad`); `native-ai` se conserva para no romper `AGENTS.md`, roadmaps y referencias de proyectos ya iniciados. En este documento el prefijo `aisdd` es el canonico; donde leas un comando, el equivalente `native-ai` es igual de valido.

Responde y documenta en espanol siempre que sea posible. Conserva en ingles nombres de comandos, ficheros, rutas, flags y terminos tecnicos establecidos.

## Reglas generales

- Trabaja desde la raiz del proyecto del usuario.
- Antes de ejecutar comandos, confirma el estado relevante con comandos no destructivos (`Get-Command`, `npm list -g`, `openspec list`, busqueda de ficheros).
- Si un argumento opcional no llega, intenta resolverlo desde OpenSpec. Pregunta solo si hay ambiguedad real.
- No inventes cambios: usa el contexto del usuario y los artefactos OpenSpec existentes.
- Si necesitas usar otro skill, invocalo por nombre y sigue sus instrucciones.
- Verifica que los comandos terminan correctamente y resume rutas/artefactos generados.
- Si un flujo depende del modelo usado, adapta la estrategia al presupuesto de contexto. Si no conoces el modelo real o su ventana, usa una estrategia conservadora de contexto medio-bajo.

## Presupuesto de contexto

Usa esta heuristica para decidir la granularidad del roadmap y de los prompts asociados:

- `bajo`: hasta 64k tokens de contexto utiles. Crear mas fases, mas estrechas y con menos alcance por cambio.
- `medio`: entre 64k y 200k tokens utiles. Crear una division equilibrada.
- `alto`: mas de 200k tokens utiles. Permitir fases mas amplias, pero sin mezclar objetivos no relacionados.

Resuelve el presupuesto con este orden:

1. Si el usuario indica el modelo o el limite de tokens, usalo.
2. Si la plataforma actual expone el modelo, usalo como pista.
3. Si no hay dato fiable, asume `medio`.

Mapeo orientativo cuando el usuario lo indique:

- GPT-4.5 o modelos alrededor de 128k: tratar como `medio`.
- Claude Sonnet con contexto muy amplio o 1M: tratar como `alto`.
- Cualquier modo desconocido o restringido: tratar como `bajo` o `medio` segun el volumen documental.

No planifiques solo por el modelo. Ajusta tambien por el tamano real del contexto:

- numero de documentos de requisitos, arquitectura y analisis
- longitud aparente de `docs/`, `README.md`, `config.yaml` y anexos
- numero de modulos o dominios funcionales afectados
- numero de integraciones, migraciones, colas, jobs o cambios transversales

Si el contexto funcional y tecnico es muy grande para el presupuesto estimado, aumenta el numero de fases aunque el modelo sea `alto`.

## Modos de faseado (paralelismo)

Por defecto, AISDD es **mono-hilo**: un change abierto a la vez. Esa regla existe por una razon concreta — al cerrar un change se consolidan decisiones en `decisions.md`, y dos changes vivos sobre la **misma superficie de decision** producirian specs que se contradicen sin que nada lo detecte.

Hay **tres modos** de fasear. El modo se decide en `aisdd roadmap` y queda registrado en `openspec/config.yaml` (`roadmap.mode`). Los demas comandos lo leen; **no lo preguntan de nuevo**.

| Modo | Que paraleliza | Garantia de coherencia | Cuando |
|---|---|---|---|
| **`atomic`** | Nada. Un change abierto en todo el proyecto. | Total, por construccion. | Un solo dev, o cuando no hay base para cortar con garantias. **Es el default.** |
| **`waves`** (oleadas) | Hasta `N` fases a la vez, una por dev, respetando dependencias. | **Ninguna.** Ordena, no protege. | Equipo con `N` devs y fases claramente separables, cuando no se puede o no se quiere declarar superficies disjuntas. |
| **`multilane`** (lanes) | `N` lineas de trabajo persistentes, un change abierto **por lane**. | Declarada y **verificada** al cerrar. | Cuando el corte en superficies disjuntas es defendible. |

**La diferencia de fondo entre `waves` y `multilane`** merece entenderse antes de elegir:

- Una **oleada** es una **tanda temporal**: un corte del calendario dentro del cual caben `N` fases sin dependencias entre si. La oleada se agota y desaparece; un dev toma cualquier fase libre de la oleada siguiente. Nada declara que esas `N` fases toquen ficheros distintos: **es responsabilidad del que fasea que no se pisen**, y nada lo comprueba.
- Un **lane** es una **linea persistente** con rutas y specs propias declaradas. Dura todo el proyecto, un dev se queda en el, y `aisdd close change` **verifica** que el change no salio de sus rutas.

Dicho de otro modo: **las oleadas resuelven el orden; los lanes resuelven ademas la coherencia.** Con `waves`, el invariante de "un hilo por superficie de decision" **no esta protegido por el tooling** — se confia en el criterio del arquitecto al fasear. Es un intercambio legitimo (menos ceremonia, ninguna red de seguridad) y por eso el modo se elige de forma explicita, no por defecto.

### Modo `waves` (oleadas)

Faseado en tandas, tal como lo define la metodologia de referencia.

1. `aisdd roadmap` pregunta cuantos **AI Developers trabajaran en paralelo** (`parallel_developers`, por defecto `1`).
2. Con `parallel_developers: 1` el roadmap es **secuencial**: una fase tras otra. Equivale a `atomic`.
3. Con `N > 1` el roadmap se organiza en **oleadas**: dentro de cada oleada, hasta `N` fases pueden ejecutarse a la vez (una por developer), **respetando las dependencias entre fases**.
4. Cada fase declara su `wave` (numero de oleada) y su `depends_on` (fases de las que depende). Una fase **no puede estar en la misma oleada que una fase de la que depende**, ni en una anterior.
5. Con suficientes fases paralelizables, gran parte del desarrollo avanza con `N` tracks simultaneos; las fases dependientes caen en oleadas sucesivas.

Reglas al construir las oleadas:

- **La oleada 1 no puede tener dependencias externas**: son las fases que arrancan sin esperar a nada. Si ninguna fase cumple eso, el faseado esta mal.
- **Ancho maximo `N`**: una oleada nunca lleva mas de `parallel_developers` fases. Si sobran fases sin dependencias, van a la oleada siguiente.
- **No rellenes oleadas**: una oleada con una sola fase es legitima si las dependencias lo imponen (es el equivalente de una barrera). Dilo explicitamente en vez de mover fases para cuadrar el ancho.
- **`foundation` va sola en la oleada 1** cuando existe: hasta que la base no esta operativa, no hay nada que paralelizar.

Limitaciones que hay que conocer al elegir este modo, y que conviene decirle al usuario cuando lo escoja:

- **Ningun comando de ejecucion conoce las oleadas.** `open change`, `implement change` y `close change` no comprueban ni la oleada ni el ancho `N`. La oleada es un artefacto de planificacion, no un control de ejecucion.
- **Nada verifica que dos fases de la misma oleada no se pisen.** No hay rutas declaradas ni verificacion al cerrar.
- **Una correccion que afecte a otra fase en vuelo no escala** (no existe el nivel 4 de `multilane`): se resuelve como correccion local y el otro developer puede no enterarse.

Si esas tres limitaciones no son aceptables para el proyecto, el modo correcto es `multilane`.

### Modo `multilane` (lanes)

Conserva el invariante y a la vez permite trabajo paralelo: el roadmap se fracciona en **lanes** (lineas de trabajo) cuyas superficies de decision son **disjuntas**. Dentro de cada lane sigue habiendo **un unico hilo**; lo que se paraleliza son los lanes entre si.

### Anatomia de un roadmap multilane

Tres tipos de fase, distinguibles por su identificador:

| Tipo | Id | Concurrencia |
|---|---|---|
| **Foundation** | `F0` | Secuencial. Bloquea todos los lanes. Deja la base del proyecto operativa. |
| **Fase de lane** | `F-<lane-id>-NN` (p. ej. `F-Data-Manager-01`) | Paralela entre lanes distintos, secuencial dentro del mismo lane. |
| **Barrera** | `FB-NN` | Secuencial. Bloquea **todos** los lanes: cambio de contrato compartido, migracion transversal, permisos, rollout. |

`F0` y las barreras son los unicos puntos donde el proyecto vuelve a ser mono-hilo. Todo lo que afecte a mas de un lane pertenece a una barrera, no a una fase de lane.

### El contrato compartido

Lo que hace disjuntos dos lanes que por dominio no lo serian (tipicamente back y front) es el **contrato**: esquema de datos, contrato de API, eventos, tipos compartidos.

- El contrato se **cierra en `F0` o en una barrera**, nunca dentro de una fase de lane.
- Tiene **dueno** explicito (AI Architect o AI Lead), declarado en `docs/roadmap.md`.
- Los lanes **arrancan contra un contrato existente**, no negociandolo. Un lane que necesita negociar el contrato esta mal faseado.
- Si un lane descubre a mitad de implementacion que el contrato es insuficiente, eso **no es una correccion local**: es una parada coordinada (ver "Correcciones durante la implementacion").

### Criterios de corte de lanes

Un corte de lanes es valido cuando se cumplen las tres condiciones:

1. **Rutas disjuntas.** Cada lane declara las rutas de codigo que le pertenecen (`paths`). Dos lanes no comparten ninguna ruta. Es verificable mecanicamente en `close change`.
2. **Specs disjuntas.** Ningun `spec.md` es escrito por dos lanes.
3. **Contrato previo.** Todo lo que los lanes comparten esta fijado antes de que arranquen, en `F0` o en una barrera.

Las condiciones 1 y 2 **no se negocian**: dos lanes que escriben los mismos ficheros o las mismas specs no son dos lanes, y ninguna declaracion los convierte en tales.

La 3 admite un escalon intermedio, porque en proyectos reales no siempre todo lo compartido se puede fijar de antemano — ver "Lanes con dependencias".

### Lanes con dependencias (escalon intermedio)

El objetivo es **lanes independientes**, y esa sigue siendo la primera opcion. Pero forzar la independencia total cuando el dominio no la permite lleva a uno de dos males: inventar barreras artificiales que serializan mas de lo necesario, o caer a `atomic` y perder todo el paralelismo. Cuando la planificacion independiente no sea viable, hay un tercer camino.

**Escalera de decision.** Baja un peldano solo cuando el anterior no sea viable, y deja constancia del motivo:

1. **Lanes independientes** — sin ninguna dependencia entre fases de lanes distintos fuera de `F0` y las barreras. **Preferido siempre.**
2. **Lanes con dependencias declaradas** — una fase de un lane declara `depends_on` sobre una fase de otro lane. Se acepta, con las condiciones de abajo.
3. **Reagrupar** — si un lane depende del otro en casi todas sus fases, no son dos lanes: fusionalos en uno.
4. **`waves` o `atomic`** — si al reagrupar queda un solo lane util, el modo multilane no aporta nada.

**Condiciones para aceptar una dependencia cross-lane.** Se cumplen todas, o se sube un peldano:

- **Declarada, no implicita.** La fase destino lleva `depends_on: [<id de la fase origen>]` en `config.yaml` y aparece en la seccion "Dependencias cross-lane" de `docs/roadmap.md`. Una dependencia que no esta declarada es un error de faseado, no una dependencia aceptada.
- **Puntual, no estructural.** Afecta a fases concretas, no a la relacion entre los dos lanes. Si el lane B depende del lane A en la mayoria de sus fases, estas en el peldano 3: reagrupa.
- **Con coste explicito.** Declara **cuanto tiempo queda bloqueado** el lane destino y **que puede hacer mientras**. Si la respuesta es "nada", la dependencia esta convirtiendo un dev en un dev parado y hay que reordenar las fases del lane destino para que trabaje en otra cosa entre medias.
- **Sin ciclos.** El grafo de `depends_on` entre lanes debe ser aciclico. Si A espera a B y B espera a A, el corte esta mal: reagrupa.
- **Las rutas siguen disjuntas.** Una dependencia es de **orden**, nunca de **superficie**. El lane destino espera a que la fase origen cierre, pero sigue escribiendo solo en sus propias rutas. Una dependencia cross-lane **no** autoriza a tocar ficheros del otro lane.

**Dependencia vs barrera** — la distincion que decide cual usar:

| | Dependencia cross-lane | Barrera `FB-NN` |
|---|---|---|
| A quien detiene | Solo al lane destino | A **todos** los lanes |
| Que cambia | El orden de dos fases | El contrato compartido |
| Rutas | Cada lane sigue en las suyas | Toca superficie compartida |
| Cuando | El lane B necesita que exista algo del lane A | Hay que renegociar lo que todos comparten |

Regla practica: si lo que falta es **codigo o un artefacto concreto** del otro lane, es una dependencia. Si lo que cambia es **el contrato**, es una barrera. Modelar como barrera lo que era una dependencia detiene a lanes que no tenian por que parar.

Orden de prioridad al decidir el corte:

- **Primero, independencia tecnica.** El corte lo manda que las superficies sean realmente disjuntas.
- **Despues, el rol del dev**, solo como **criterio de desempate** cuando hay varios cortes tecnicamente validos. Nunca al reves: un corte que respeta el organigrama pero deja rutas compartidas es un corte invalido, no un compromiso aceptable.

Advertencia frecuente: **`data` rara vez es un lane independiente de `back`** — comparten esquema y migraciones, luego comparten superficie de decision. Normalmente `back+data` es un solo lane. Los cortes limpios habituales son pocos y grandes, no muchos y finos.

### Lane activo

El lane sobre el que trabaja un dev es **estado local suyo**, equivalente a la rama de Git:

- Vive en `openspec/.lane` (una linea con el `lane-id`).
- **Nunca** en `openspec/config.yaml`: ese fichero se versiona y dos devs se pisarian el puntero en cada commit.
- `aisdd init` lo anade a `.gitignore`.
- Se consulta y cambia con `aisdd lane` (ver su seccion).

En modo `atomic` el fichero no existe y el concepto no aplica.

## Dependencias de skills

Comprueba si existen estos directorios en alguna ubicacion de skills conocida:

- `.agents/skills/booster-ux`
- `.agents/skills/booster-uml`
- `$env:USERPROFILE\.agents\skills\booster-ux`
- `$env:USERPROFILE\.agents\skills\booster-uml`
- `$env:USERPROFILE\.codex\skills\booster-ux`
- `$env:USERPROFILE\.codex\skills\booster-uml`

Si falta `booster-ux`, avisa: `No encuentro el skill booster-ux. Debe instalarse o copiarse en .agents/skills/booster-ux o en una carpeta global de skills del usuario.`

Si falta `booster-uml`, avisa: `No encuentro el skill booster-uml. Debe instalarse o copiarse en .agents/skills/booster-uml o en una carpeta global de skills del usuario.`

La ausencia de un skill no debe bloquear `init`, `implement` o `close`; si bloquea diagramas o prototipos, informa y deja los comandos OpenSpec completados.

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
   - **Capa de entrega (AIDD)** — **no la ignores**: `docs/planificacion-proyecto.md` (recursos, equipo, esfuerzo humano vs IA), `docs/sprint-plan.md` (sprints, capacidad, asignaciones), `docs/plan-revision-hu.md` (estado de validacion de HU) y `docs/jira-sync.md` (mapeo HU<->Story<->change). Busca estos ficheros en `docs/` y, si existen, inclúyelos; si no, no pasa nada (son opcionales).
8. Cuando tengas las rutas, actualiza `config.yaml` de OpenSpec con ese contexto inicial. Manten el formato YAML existente; crea/actualiza `project_context` con **dos sub-listas** para que los comandos posteriores sepan que existe cada plano:
   ```yaml
   project_context:
     design_docs:            # diseno y definicion
       - docs/requisitos.md
       - docs/detalle-historias-usuario.md
       - docs/arquitectura-base.md
     delivery_docs:          # capa de entrega AIDD (solo las que existan)
       - docs/planificacion-proyecto.md
       - docs/sprint-plan.md
       - docs/plan-revision-hu.md
       - docs/jira-sync.md
   ```
   Si ya existe un `project_context` plano (formato antiguo), conserva su contenido y reorganizalo en estas dos sub-listas sin perder rutas.
9. **Check ligero (no bloqueante).** AISDD **asume** que la planificacion de AIDD es correcta; no la re-valides a fondo. Limitate a avisar en el resumen si: (a) alguna ruta indicada no existe; (b) hay `sprint-plan.md`/`planificacion-proyecto.md` pero falta el detalle de HU que los sustenta; (c) **no** hay capa de entrega (ni `sprint-plan.md` ni `planificacion-proyecto.md`) — en ese caso informa de que `aisdd roadmap` faseara sin alinear a sprints; o (d) `sprint-plan.md` menciona un **volcado a Jira** (Stories/claves creadas) pero falta `docs/jira-sync.md` o la seccion `jira:` — **enlace perdido**: avisa de que la integracion Jira de los changes se omitira y ofrece reconstruirlo (ver "Reconstruccion del enlace perdido"). Son avisos, no errores: continua igualmente.
10. **Ignora el puntero de lane.** Asegura que `.gitignore` contiene una linea `openspec/.lane`. Si el fichero `.gitignore` no existe, crealo con esa unica linea; si existe y ya la contiene, no lo toques. Ese fichero es el lane activo de **cada dev** y no debe versionarse (ver "Lanes"). Hazlo siempre, tambien en proyectos que arrancan en modo `atomic`: es idempotente y evita tener que recordarlo si mas adelante se pasa a multilane.
11. Registra los comandos del skill en el `AGENTS.md` del proyecto segun la seccion siguiente.

### Registro de comandos en `AGENTS.md`

El objetivo es que cualquier agente que lea el `AGENTS.md` del proyecto conozca los comandos disponibles del skill `aisdd-specs`.

1. Localiza `AGENTS.md` en la raiz del proyecto. Si no existe, crealo con una cabecera minima (`# AGENTS.md`) seguida del bloque de comandos.
2. Si existe, conserva integro el resto del contenido. No reescribas ni reordenes secciones ajenas al skill.
3. Gestiona los comandos dentro de un bloque delimitado por marcadores HTML, para poder actualizarlo de forma idempotente en futuras ejecuciones:

   ```markdown
   <!-- BEGIN aisdd-specs commands (auto-generado, no editar a mano) -->
   ## Comandos aisdd

   Skill `aisdd-specs` v<skill_version>. Invoca estos comandos para trabajar con especificaciones AISDD / OpenSpec (prefijo primario `aisdd`; `native-ai <cmd>` sigue funcionando como alias legacy):

   - `aisdd init` — inicializa OpenSpec, comprueba dependencias y registra el contexto del proyecto (incluida la capa de entrega de AIDD).
   - `aisdd roadmap` — fasea el desarrollo (alineado al `docs/sprint-plan.md` si existe) y genera `docs/roadmap.md`, `docs/prompts-roadmap-native-ai.md` y la seccion `roadmap` de `openspec/config.yaml`.
   - `aisdd open change <what-you-want-to-build>` — pre-flight de dudas y creacion del cambio OpenSpec.
   - `aisdd implement change <what-you-want-to-build>` — pre-flight de dudas y aplicacion de instrucciones del cambio.
   - `aisdd amend change [descripcion]` — incorpora una modificacion a un change ya abierto y ejecuta **solo ese delta**, sin re-aplicar el change (skill `aisdd-amend`).
   - `aisdd close change <what-you-want-to-build>` — archiva el cambio OpenSpec.
   - `aisdd lane [list | switch <lane-id> | status]` — consulta y cambia la linea de trabajo activa (solo en roadmaps `multilane`).
   - `aisdd prototype-ux [what-you-want-to-build]` — genera prototipos UX con `booster-ux`.
   - `aisdd uml <what-you-want-to-build>` — genera el HTML de diagramas del cambio con `booster-uml`.
   <!-- END aisdd-specs commands -->
   ```

4. Si ya existe un bloque entre `<!-- BEGIN aisdd-specs commands ... -->` y `<!-- END aisdd-specs commands -->`, reemplazalo integramente por la version actual. **Migracion**: si en su lugar existe un bloque legacy `<!-- BEGIN native-ai-specs commands ... -->` / `<!-- END ... -->` (de la version `sdd` anterior), **reemplazalo** por el bloque `aisdd-specs` (no dejes ambos). Si no existe ninguno, anade el nuevo al final del fichero precedido de una linea en blanco.
5. Sustituye `<skill_version>` por la version real del frontmatter del skill.
6. Incluye `AGENTS.md` en los `output_files` de la entrada de auditoria de este comando.

## `aisdd roadmap`

> Alias: `native-ai roadmap`.

Fasea el desarrollo antes de modificar documentos OpenSpec.

1. Revisa si el usuario ya ha pasado requisitos y arquitectura. Localiza documentacion existente en `docs/`, `config.yaml` (`project_context.design_docs` y `project_context.delivery_docs`), `README.md` o rutas indicadas por el usuario. **Lee tambien la capa de entrega si existe** (`docs/sprint-plan.md`, `docs/planificacion-proyecto.md`, `docs/plan-revision-hu.md`): condiciona el faseado (ver "Alineacion con la capa de entrega").
2. Si faltan requisitos, arquitectura, o no esta claro donde estan, solicitalos antes de continuar. La capa de entrega es **opcional**: si no hay `sprint-plan.md`, fasea solo por presupuesto de contexto y dilo.
3. Estima el `presupuesto de contexto` segun la seccion anterior y clasifica el trabajo tambien por complejidad:
   - `baja`: un solo dominio funcional, pocas integraciones y cambios locales
   - `media`: varios modulos o capas, dependencias compartidas o integraciones relevantes
   - `alta`: varios dominios, refactor transversal, seguridad, migraciones, jobs, eventos o multiples integraciones
4. Define el numero objetivo de fases antes de redactar el roadmap:
   - contexto `bajo`: normalmente `6-12` fases
   - contexto `medio`: normalmente `4-8` fases
   - contexto `alto`: normalmente `3-6` fases
5. Ajusta ese rango con estas reglas:
   - suma fases si una fase mezclaria mas de un objetivo funcional principal
   - suma fases si una fase exigiria leer demasiados artefactos o demasiadas partes del codigo para abrir un solo change con seguridad
   - suma fases si hay migraciones de datos, seguridad, permisos, integraciones externas o rollout gradual
   - resta fases solo cuando dos bloques sean claramente dependientes y pequenos
6. Diseña las fases para que cada una pueda abrirse como uno o pocos changes OpenSpec con contexto acotado. Cada fase debe poder entenderse con un subconjunto manejable de requisitos, arquitectura y codigo.
7. **Resuelve los parametros de paralelismo** segun la seccion "Decision de modo de faseado": cuantos devs trabajan en paralelo (`parallel_developers`) y cual de los tres modos se usa (`atomic`, `waves` o `multilane`). El modo condiciona todo lo que viene despues: nomenclatura e identificadores de fase, agrupacion de prompts y estructura de `config.yaml`.
8. Cuando tengas contexto suficiente, actua con este rol y objetivo:
   ```text
   Actua con el rol de planificador experto de desarrollos de software.
   Analiza los requisitos y fasea el desarrollo en las fases que consideres necesarias para implementarlo con openspec. Ajusta la granularidad del roadmap al presupuesto de contexto del modelo: cuanto menor sea, mas fases y mas pequenas deben ser. Evita fases demasiado grandes que obliguen a arrastrar demasiado contexto en un unico change. Basate en la arquitectura del proyecto. Si existe una planificacion de entrega (docs/sprint-plan.md), alinea el faseado a los sprints: mismo orden, cortes de fase coincidiendo con fronteras de sprint y gates de validacion, y manten los changes de una misma HU dentro de la ventana del sprint donde esa HU esta planificada; el presupuesto de contexto sigue mandando el tamano del change, y donde choque con el sprint, marcalo como conflicto en vez de romper el plan. Si el roadmap es multilane, reparte las fases en las lineas de trabajo (lanes) acordadas: cada lane con rutas de codigo y specs disjuntas de los demas, todo lo compartido resuelto antes en F0 o en una fase barrera, y la nomenclatura F0 / F-<lane-id>-NN / FB-NN. Con ello genera docs/roadmap.md con la division por fases, que entra en cada fase, a que lane pertenece y a que sprint(s) corresponde. Ademas, crea docs/prompts-roadmap-native-ai.md con los prompts a ejecutar hasta finalizar el desarrollo usando los comandos del skill aisdd, agrupados por lane si el roadmap es multilane. No modifiques aun ningun documento de openspec. Si el usuario no ha pasado requisitos y/o arquitectura o no tienes clara donde esta, solicitaselo.
   ```
9. Crea el directorio `docs/` si no existe.
10. Genera `docs/roadmap.md` con:
   - presupuesto de contexto asumido y justificacion
   - complejidad estimada
   - **modo del roadmap** (`atomic`, `waves` o `multilane`), **`parallel_developers`** asumido y la justificacion de ambos en una linea
   - fases ordenadas
   - objetivo de cada fase
   - alcance y exclusiones
   - dependencias
   - entregables OpenSpec esperados
   - criterios de cierre
   - riesgo de contexto por fase: `bajo`, `medio` o `alto`
   - **si hay `docs/sprint-plan.md`**: a que **sprint(s)** corresponde cada fase, el **esfuerzo agregado** de la fase (humano vs IA, tomado de `planificacion-proyecto.md`/`sprint-plan.md` si estan) y una seccion **"Conflictos de alineacion roadmap<->sprint"** con lo que el presupuesto de contexto obligo a desviar del plan de sprints (ver "Alineacion con la capa de entrega").
   - **dependencias por fase** (`depends_on`): de que fases previas depende cada una. Es el grafo que sostiene tanto las oleadas como las dependencias cross-lane; declaralo siempre, tambien en `atomic`, aunque ahi sea trivial.
   - **si el modo es `waves`**: la **organizacion en oleadas** y, por cada fase, su numero de oleada y de que fases depende. Anade una vista de la oleada completa (que fases corren a la vez y con que dev).
   - **si el modo es `multilane`**: las dos secciones adicionales descritas en "Secciones de lanes en `docs/roadmap.md`", y el identificador de cada fase segun la nomenclatura `F0` / `F-<lane-id>-NN` / `FB-NN`.
11. Genera `docs/prompts-roadmap-native-ai.md` con los prompts que deben ejecutarse hasta finalizar el desarrollo, usando solo estos comandos del skill:
   - `aisdd open change <what-you-want-to-build>`
   - `aisdd implement change <what-you-want-to-build>`
   - `aisdd close change <what-you-want-to-build>`
   - `aisdd lane switch <lane-id>` (solo en modo `multilane`, como paso previo de cada bloque de lane)
12. En `docs/prompts-roadmap-native-ai.md`, para cada fase indica explicitamente:
   - que documentos o secciones pasar al modelo
   - que partes del codigo son relevantes
   - que no debe incluirse todavia para no contaminar contexto
   - cuando conviene dividir una fase en varios changes OpenSpec
   - el sprint al que pertenece la fase (si hay `sprint-plan.md`)
   - el prompt exacto para abrir el change con `aisdd open change <what-you-want-to-build>`
   - el prompt exacto para implementar con `aisdd implement change <what-you-want-to-build>`
   - el prompt exacto para cerrar con `aisdd close change <what-you-want-to-build>`
13. **En modo `waves`, agrupa los prompts por oleada**: un bloque por oleada, y dentro de el las fases que pueden ejecutarse a la vez, indicando explicitamente que **se pueden lanzar en paralelo** y que la oleada siguiente no arranca hasta que la actual cierra. Si una oleada lleva una sola fase, di por que (dependencias, no falta de trabajo).
14. **En modo `multilane`, agrupa los prompts por lane, no en una unica secuencia lineal.** Un bloque por lane, cada uno encabezado por su `aisdd lane switch <lane-id>` y con sus fases en orden; `F0` va antes de todos los bloques y cada barrera `FB-NN` va en su propio bloque, con una nota explicita de que **detiene todos los lanes** hasta cerrarse. El documento debe poder leerse de arriba abajo por un dev que solo trabaja un lane, sin tener que filtrar mentalmente fases ajenas.
15. Los prompts de `docs/prompts-roadmap-native-ai.md` deben estar redactados para un usuario final o para otro agente, en espanol, e incluir el contexto minimo necesario para ejecutar cada fase sin arrastrar informacion irrelevante de fases futuras.
16. No uses en ese fichero comandos OpenSpec directos como `openspec new change`, `openspec instructions apply` u `openspec archive`, salvo de forma explicativa excepcional fuera de los prompts operativos.
17. Tras generar `docs/roadmap.md` y `docs/prompts-roadmap-native-ai.md`, actualiza `openspec/config.yaml` con el resumen del roadmap segun la seccion siguiente.
18. No ejecutes `openspec new change`, no archives cambios y no edites ningun otro artefacto de `openspec/` (changes, specs) durante este comando. La unica escritura permitida en `openspec/` es la actualizacion de `openspec/config.yaml` descrita en el paso 17.

### Decision de modo de faseado

Este paso decide entre los tres modos (`atomic`, `waves`, `multilane`) y fija `parallel_developers`. Lee antes la seccion "Modos de faseado (paralelismo)", que define el modelo; aqui esta el procedimiento.

**0. Resuelve `parallel_developers` primero.** Es el dato del que dependen los otros dos modos, y se resuelve igual para ambos:

- Si `openspec/config.yaml` ya trae `roadmap.parallel_developers` de una ejecucion anterior, proponlo como default.
- Si existe `docs/planificacion-proyecto.md`, cuenta los perfiles **de implementacion** con dedicacion real (no cuentes Lead, Architect ni Outcome Validator: no conducen changes) y proponlo, diciendo de donde sale.
- Si no hay ninguna de las dos fuentes, **preguntalo**. Default `1`.

Con `parallel_developers: 1` no hay nada que decidir: el modo es `atomic` y el roadmap es secuencial. Dilo y sigue.

**0.bis. Elige modo.** Con `parallel_developers > 1`, presenta la eleccion al usuario con `AskUserQuestion` si la plataforma lo soporta, exponiendo el intercambio real y **con una recomendacion**:

- Recomienda **`multilane`** si `docs/arquitectura-base.md` existe y su descomposicion por modulos da rutas disjuntas. Es el unico modo con garantia verificada.
- Recomienda **`waves`** si no hay base para cortar superficies disjuntas (sin `arquitectura-base.md`, o modulos que comparten rutas) pero si hay fases claramente separables y varios devs. Advierte de forma explicita de sus tres limitaciones (ver "Modo `waves`"): ningun comando conoce las oleadas, nada verifica que dos fases de la misma oleada no se pisen, y una correccion no escala a los demas.
- Recomienda **`atomic`** si ninguna de las dos se sostiene. No es un fracaso.

Si el usuario elige `waves`, salta al paso "Construccion de las oleadas". Si elige `multilane`, sigue con los pasos 1-7.

**Configuracion previa.** Si `openspec/config.yaml` ya trae `roadmap.mode`, proponlo como default en la pregunta (el proyecto ya eligio antes). Cambiar de modo entre ejecuciones esta permitido, pero **avisa de lo que implica**: pasar de `multilane` a `waves` o `atomic` deja sin efecto los `paths` y la verificacion de `close change`; pasar a `multilane` obliga a declarar rutas para todas las fases.

**Construccion de las oleadas (solo modo `waves`).**

1. Construye el grafo de dependencias entre fases (`depends_on`).
2. **Oleada 1**: todas las fases sin dependencias, hasta un maximo de `parallel_developers`. Si existe `foundation`, va sola en la oleada 1.
3. **Oleada k+1**: las fases cuyas dependencias esten todas en oleadas <= k, hasta el maximo de ancho.
4. Repite hasta colocar todas las fases. Si una fase nunca es colocable, hay un **ciclo** en `depends_on`: corrigelo antes de escribir nada.
5. Comprueba el ancho real de cada oleada. Si la media queda muy por debajo de `parallel_developers`, dilo: el faseado no es paralelizable y quiza `parallel_developers` esta sobreestimado, o las fases estan mal cortadas.

**1. Calcula el numero de lanes viable. No lo adivines ni lo preguntes en frio.**

- **Modulos disjuntos**: lee `docs/arquitectura-base.md`, seccion "Descomposicion por modulos / dominios", y cuenta los modulos cuyas **rutas de codigo no se solapan**. Descarta los que compartan esquema de datos o migraciones (tipicamente `data` con `back`): esos son un solo lane.
- **Devs disponibles**: lee la seccion de perfiles/equipo de `docs/planificacion-proyecto.md` y cuenta los perfiles **de implementacion** con dedicacion real (no cuentes Lead, Architect ni Outcome Validator: no conducen changes).
- **Propuesta inicial** = `min(modulos disjuntos, devs disponibles)`.

Si falta `arquitectura-base.md`, no hay base para cortar lanes: propon `atomic` y dilo. Si falta `planificacion-proyecto.md`, calcula solo por modulos y marca el numero de devs como supuesto.

**2. Pregunta al usuario con la propuesta ya hecha.** Usa `AskUserQuestion` si la plataforma lo soporta, con 2-4 opciones y una marcada `(Recomendada)`. La pregunta ofrece: el modo (`atomic` / `multilane`) y, si elige `multilane`, el numero propuesto. **Presenta siempre el calculo**: "propongo 2 lanes = min(3 modulos disjuntos, 2 devs de implementacion)". El usuario no debe tener que adivinar en cuantos lanes se rompe su roadmap.

**3. Si el usuario pide otro numero, evaluralo y negocia.** No lo aceptes por obediencia ni lo rechaces por inercia:

- **Mas lanes que devs**: rechazalo. No aporta paralelismo (no hay quien conduzca el lane de mas) y si pierde coherencia (mas superficies de decision que vigilar). Di exactamente eso y vuelve a proponer.
- **Mas lanes que modulos disjuntos**: rechazalo. Obligaria a partir un modulo por dentro, y dos lanes con rutas solapadas **no son lanes**: es el escenario que el modo multilane existe para evitar.
- **Menos lanes de los propuestos**: es aceptable. Menos paralelismo pero mas coherencia; confirma y sigue.
- **Un corte concreto que el usuario propone** (no solo el numero): validalo contra las tres condiciones de "Criterios de corte de lanes". Si falla alguna, di **cual** y por que.

Itera hasta acuerdo real. Cada iteracion debe aportar un argumento nuevo, no repetir el anterior. Si tras dos rondas no hay acuerdo, registra la discrepancia como decision del usuario en `docs/roadmap.md` y continua con lo que el usuario haya decidido: el faseado es suyo, tu responsabilidad es que sepa que esta aceptando.

**4. Nombra los lanes.** `lane-id` en kebab-case, estable (es clave de union con `sprint-plan.md` y con el puntero local `openspec/.lane`); `label` legible para humanos. Deriva el nombre del **dominio**, no del rol: `data-manager`, `catalogo`, `portal-cliente` — no `dev-1` ni `equipo-a`.

**5. Asigna rutas.** Cada lane declara sus `paths` (prefijos de ruta de codigo). Comprueba explicitamente que **ningun prefijo de un lane es prefijo de otro**. Si no puedes asignar rutas sin solape, el corte es invalido: vuelve al paso 3.

**6. Reserva lo compartido.** Todo lo que afecte a mas de un lane —contrato de API, esquema de datos, tipos compartidos, migraciones, permisos, observabilidad transversal, rollout— **no puede vivir en una fase de lane**. Colocalo en `F0` (si es fundacional) o en una barrera `FB-NN` (si aparece mas adelante). Si al fasear te sale una fase de lane que toca algo compartido, es que era una barrera.

**7. Degradacion.** En cualquiera de estos casos, cae a `atomic` y explica por que en `docs/roadmap.md`: no hay `arquitectura-base.md`; los modulos no dan rutas disjuntas; solo hay un dev de implementacion; o el contrato compartido no se puede fijar antes de que arranquen los lanes. `atomic` no es un fracaso, es el modo correcto cuando el corte no es defendible.

### Secciones de lanes en `docs/roadmap.md`

En modo `multilane`, `docs/roadmap.md` incluye dos secciones adicionales.

**"Lanes"** — una entrada por lane:

- `lane-id` y label
- rutas de codigo (`paths`) que le pertenecen
- perfil / rol asignado (de `planificacion-proyecto.md`)
- justificacion del corte en una linea: por que este lane es independiente de los demas
- fases que contiene, en orden

Cierra la seccion con el **numero de lanes y su calculo** (`min(modulos, devs)`), y con el **dueno del contrato compartido**.

**"Dependencias cross-lane"** — el punto de control del faseado. Una fila por dependencia, con:

- fase **origen** y fase **destino** (y sus lanes)
- **como se resuelve**: una barrera `FB-NN`, o una **dependencia declarada** (`depends_on`)
- si es dependencia declarada: **cuanto queda bloqueado** el lane destino y **que hace mientras**

Regla de lectura de esta seccion, en este orden:

1. **Sin dependencias cross-lane** — el corte es limpio. Es el objetivo.
2. **Resuelta por barrera** — lo compartido se renegocia en `FB-NN`. Correcto cuando lo que cambia es el contrato.
3. **Dependencia declarada** (`depends_on`) — aceptable bajo las condiciones de "Lanes con dependencias": puntual, aciclica, con coste explicito y **sin compartir rutas**. Correcto cuando lo que falta es codigo o un artefacto concreto del otro lane.
4. **Dependencia no declarada** — esto si es un **error de faseado**. Si al redactar la seccion descubres una dependencia que no esta en `depends_on` ni resuelta por barrera, no la anotes como nota al pie: declarala o vuelve a cortar.

Marca `[RIESGO]` cualquier dependencia declarada cuyo lane destino **no tenga otra cosa que hacer** mientras espera: eso es un dev parado, que es exactamente lo que el modo multilane pretende eliminar. Reordena las fases del lane destino antes de aceptarla.

Cierra la seccion con el **grafo resumido** (que lane espera a cual, y en que fases) para que el desajuste se vea de un vistazo y `aidd sprint-planning` pueda secuenciarlo.

### Seccion de oleadas en `docs/roadmap.md`

En modo `waves`, `docs/roadmap.md` incluye una seccion **"Oleadas"** con:

- una entrada por oleada, en orden, con las fases que la componen y su `depends_on`
- el **ancho** de cada oleada frente a `parallel_developers` (p. ej. `3/3`, `1/3`), para que se vea donde el faseado paraleliza y donde no
- el motivo de las oleadas de ancho 1 (dependencias, no falta de trabajo)
- una advertencia final, literal, de que **las oleadas no las verifica ningun comando**: el reparto real entre developers es responsabilidad del equipo, y nada impide abrir dos changes de la misma oleada que se pisen

### Alineacion con la capa de entrega (sprint-plan)

Si existe `docs/sprint-plan.md`, el roadmap **se pliega a los sprints ya planificados** por AIDD, sin dejar que la capacidad mande sobre el presupuesto de contexto. Regla de jerarquia: **el presupuesto de contexto decide el tamano del change; el sprint decide el orden, las fronteras y que HU estan comprometidas.**

- **Orden**: fasea en el **mismo orden** que los sprints (que ya refleja prioridad de negocio, capacidad y dependencias).
- **Fronteras**: haz coincidir los **cortes de fase con las fronteras de sprint** y con los gates de validacion (de `plan-revision-hu.md`) siempre que el contexto lo permita.
- **Agrupacion**: manten los **changes de una misma HU dentro de la ventana del sprint** donde esa HU esta planificada, para que un sprint no quede con changes a medias.
- **HU no validadas**: si `docs/plan-revision-hu.md` marca una HU como **en revision o bloqueada**, no la metas en una fase temprana como comprometida; senala que depende de su validacion.
- **Esfuerzo**: anota en cada fase el esfuerzo agregado (humano vs IA) tomado de `planificacion-proyecto.md`/`sprint-plan.md`.
- **Conflictos (no romper el plan)**: cuando el presupuesto de contexto obligue a partir una HU en varios changes que **no caben** en su sprint, o a cortar a mitad de un bloque, **no reescribas el sprint-plan**: registra el desajuste en la seccion **"Conflictos de alineacion roadmap<->sprint"** de `docs/roadmap.md` (que HU se parte, en cuantos changes, que sprint desborda) para que el humano re-ejecute `aidd sprint-planning` y re-empaquete (re-faseado seguro: mueve HU, no recrea issues). AISDD **no** modifica `docs/sprint-plan.md`.

Si **no** hay `sprint-plan.md`, fasea solo por presupuesto de contexto y dilo explicitamente en `docs/roadmap.md` (faseado no alineado a sprints).

En modo `waves` se anade una regla: **una oleada es una frontera de sprint natural** — todas sus fases pueden correr a la vez y la siguiente no arranca hasta que cierra. Haz coincidir cortes de sprint con cambios de oleada siempre que el contexto lo permita, y anota el ancho de cada oleada para que el sprint-plan pueda contrastar carga contra capacidad.

En modo `multilane` se anaden dos reglas:

- **Un sprint contiene fases de varios lanes a la vez.** No es un desajuste: es el objetivo. No intentes que cada sprint pertenezca a un solo lane.
- **Las barreras `FB-NN` son fronteras de sprint naturales.** Al alinear, haz coincidir cada barrera con un corte de sprint siempre que el contexto lo permita: una barrera detiene todos los lanes, que es exactamente lo que hace un gate de validacion. Si una barrera cae a mitad de sprint, registralo en "Conflictos de alineacion roadmap<->sprint" — no reescribas el sprint-plan.

### Actualizacion de `openspec/config.yaml` tras el roadmap

El objetivo es que `openspec/config.yaml` quede como indice navegable del roadmap para los comandos posteriores (`open change`, `implement change`).

1. Localiza `openspec/config.yaml` en la raiz del proyecto. Si no existe, no ejecutes `openspec init` aqui: crea el fichero con un YAML minimo valido y avisa al usuario de que conviene haber ejecutado antes `aisdd init`.
2. Lee el contenido actual y conserva el formato y las claves existentes (por ejemplo `project_context`, `audit.retention_days`). No elimines ni reescribas claves ajenas al roadmap.
3. Crea o reemplaza por completo una unica seccion de nivel raiz `roadmap` con esta estructura:

   ```yaml
   roadmap:
     generated_at: <YYYY-MM-DD>
     context_budget: bajo | medio | alto
     complexity: baja | media | alta
     mode: atomic | waves | multilane  # ausente o `atomic` = comportamiento clasico
     parallel_developers: <entero >= 1>   # devs que trabajan a la vez; 1 => secuencial
     contract_owner: <rol/persona>     # solo si mode: multilane
     lanes:                            # solo si mode: multilane
       - id: <lane-id>                 # kebab-case, estable; clave de union con sprint-plan y openspec/.lane
         label: <nombre legible>
         paths: [<prefijo/de/ruta/>, ...]   # rutas propias; ningun prefijo puede serlo de otro lane
         profile: <perfil de planificacion-proyecto.md>
     docs:
       roadmap: docs/roadmap.md
       prompts: docs/prompts-roadmap-native-ai.md
     phases:
       - id: 1                    # atomic/waves: correlativo. multilane: F0 | F-<lane-id>-NN | FB-NN
         name: <nombre de la fase>
         objective: <objetivo en una linea>
         context_risk: bajo | medio | alto
         change_hint: <slug estable para `aisdd open change`>   # clave de union roadmap<->sprint<->Jira
         depends_on: [<ids de fases previas>]   # grafo de dependencias; [] si no depende de ninguna
         wave: <numero de oleada>   # solo si mode: waves
         lane: <lane-id>            # solo si mode: multilane; vacio en fases F0 y FB-NN
         barrier: false             # solo si mode: multilane; true en FB-NN y en F0
         paths: [<...>]             # solo si mode: multilane; subconjunto de los paths de su lane
         amended_by: <slug-del-change>  # opcional; lo escribe `aisdd amend change` (ver `open change`)
         sprint: <id/nombre del sprint del sprint-plan.md, o vacio si no hay>   # solo si hay sprint-plan
         hus: [<HU-XX>, ...]        # HUs que cubre la fase (para enlazar con Jira/jira-sync.md)
         effort_human: <d-persona>  # esfuerzo agregado humano (si hay planificacion-proyecto)
         effort_ai: <d-persona>     # esfuerzo agregado con IA (si aplica)
       # ...una entrada por fase, en el mismo orden que docs/roadmap.md
   ```

   El `change_hint` es el **slug estable** que sirve de clave de union entre el roadmap, el sprint-plan y Jira; no lo cambies entre re-ejecuciones si la fase es la misma (para no romper el mapeo ni las sub-tareas ya creadas).

   Todas las claves de paralelismo son **aditivas**: un `config.yaml` de un roadmap anterior sin ellas sigue siendo valido y se interpreta como `mode: atomic` con `parallel_developers: 1`. Escribe solo las que apliquen al modo elegido — `wave` solo en `waves`; `contract_owner`, `lanes`, `lane`, `barrier` y `paths` solo en `multilane`. **`depends_on` se escribe siempre**, en los tres modos: es el grafo del que salen las oleadas y las dependencias cross-lane, y en `atomic` documenta el orden real en vez de dejarlo implicito en la numeracion.

4. El numero de entradas de `phases` debe coincidir exactamente con las fases de `docs/roadmap.md`, en el mismo orden y con los mismos nombres.
5. Si ya existia una seccion `roadmap` de una ejecucion anterior, sustituyela integramente por la nueva (el roadmap mas reciente manda). No fusiones fases antiguas con nuevas. **Excepcion: conserva los `amended_by`** de las fases que sobrevivan con el mismo `change_hint` — son enmiendas ya aplicadas en otro lane que la fase todavia no ha recogido, y perderlas deja al lane implementando contra un contrato desmentido. Si una fase marcada desaparece del nuevo faseado, dilo en el resumen.
6. Manten YAML valido: indentacion con espacios (no tabs), valores con caracteres especiales entre comillas, UTF-8 sin BOM.
7. **Valida `depends_on` en cualquier modo antes de escribir**: (a) todo id referenciado existe en `phases`; (b) el grafo es **aciclico**; (c) ninguna fase depende de otra posterior en el orden del documento. Si alguna falla, no escribas: corrige el faseado.
8. **En modo `waves`, valida ademas**: (a) toda fase tiene `wave`; (b) ninguna oleada supera `parallel_developers` fases; (c) ninguna fase comparte oleada con una de la que depende, ni esta en una anterior.
9. **En modo `multilane`, valida ademas**: (a) todo `phases[].lane` existe en `lanes[]`; (b) las fases con `barrier: true` no tienen `lane`; (c) los `paths` de cada fase de lane son subconjunto de los de su lane (las barreras no declaran `paths`); (d) ningun `paths` de un lane es prefijo de los de otro. Si alguna falla, no escribas el fichero: corrige el faseado primero.
10. Incluye `openspec/config.yaml` en los `output_files` de la entrada de auditoria de este comando, junto a `docs/roadmap.md` y `docs/prompts-roadmap-native-ai.md`.

### Criterios de particion para el roadmap

Usa estos criterios para dividir en mas fases cuando el modelo tenga menos capacidad:

- separar cambios por dominio funcional
- separar backend, frontend, datos e integraciones cuando no sea imprescindible tratarlos juntos
- separar preparacion tecnica de entrega funcional si la primera desbloquea varias fases
- separar migraciones, permisos, seguridad, observabilidad y rollout
- separar cambios con alto riesgo o validacion compleja

Estos mismos criterios sirven para **asignar lane** en modo `multilane`, con dos matices que cambian su lectura:

- Los dos primeros criterios reparten trabajo **entre lanes**: dominio funcional y separacion back/front/datos/integraciones son los cortes candidatos. Pero un corte solo vale como lane si ademas cumple las tres condiciones de "Criterios de corte de lanes" — el criterio de contexto sugiere donde cortar, no garantiza que el corte sea independiente.
- Los tres ultimos criterios **no producen lanes, producen barreras**: preparacion tecnica que desbloquea varias fases, migraciones, permisos, seguridad, observabilidad, rollout y cambios de alto riesgo afectan a mas de un lane por naturaleza. Van a `F0` o a `FB-NN`.

Advertencia sobre el segundo criterio: **`datos` rara vez es un lane propio separado de `backend`** — comparten esquema y migraciones, luego comparten superficie de decision. Como criterio de contexto (partir en mas fases) es valido; como criterio de lane (trabajo paralelo) normalmente no lo es.

Evita estas fases, especialmente con contexto `bajo` o `medio`:

- "implementacion completa del modulo"
- "migracion y refactor general"
- "frontend + backend + datos + seguridad + integraciones" en una sola fase

Prefiere nombres de fase concretos, por ejemplo:

- `Fase 1. Preparar contratos y modelo de datos`
- `Fase 2. Implementar API de alta`
- `Fase 3. Integrar validaciones y permisos`
- `Fase 4. Construir flujo UI de alta`
- `Fase 5. Observabilidad, pruebas y rollout`

El equivalente multilane del mismo ejemplo, con dos lanes (`api` y `portal`):

- `F0. Preparar contratos y modelo de datos` — contrato compartido, bloquea a todos
- `F-api-01. Implementar API de alta`
- `F-portal-01. Construir flujo UI de alta` — en paralelo con `F-api-01`, contra el contrato de `F0`
- `FB-01. Integrar validaciones y permisos` — barrera: toca ambos lanes
- `FB-02. Observabilidad, pruebas y rollout` — barrera de cierre

Fijate en lo que cambia: la fase de contratos deja de ser "la primera" para ser **fundacional y bloqueante**, y las dos fases de construccion dejan de ser consecutivas para ser simultaneas. Permisos y rollout no se reparten entre lanes: se convierten en barreras.

## `aisdd open change [what-you-want-to-build]`

> Alias: `native-ai open change [what-you-want-to-build]`.

Crea un cambio OpenSpec a partir del contexto del usuario, ejecutando una fase previa de pre-flight para resolver dudas antes de generar los specs.

> **El faseado es normativo.** El alcance del change lo fijan su **fase del roadmap** (`hus`, `change_hint` en `config.yaml`) y la **ventana de su sprint** (`docs/sprint-plan.md`). No propongas **adelantar HU de fases o sprints posteriores**, ni "aprovechar" el change para cubrir criterios de otras HU, ni ampliar el alcance mas alla de lo faseado — aunque parezca eficiente. Si detectas una oportunidad real de adelanto o una dependencia mal faseada, **no la conviertas en pregunta del pre-flight**: registrala como observacion en el resumen final y remite al re-faseado formal (`aisdd roadmap` y/o `aidd sprint-planning`), que es donde se decide el CUANDO. Un change no debe contener specs de HU fuera de su fase. Solo el usuario, por iniciativa propia y explicita, puede ordenar saltarse el faseado.
>
> **En modo `multilane`, el lane tambien es normativo.** Un change pertenece al lane de su fase y no se salta de lane "de paso". Cambiar de linea de trabajo es un acto explicito del usuario (`aisdd lane switch`), nunca una decision tuya durante un `open change`.

0. **Guard de apertura.** Antes de nada, lee `openspec/config.yaml` y ejecuta `openspec list` para conocer los changes vivos. La comprobacion de `depends_on` aplica en **los tres modos**; el guard de concurrencia por lane, solo en `multilane`:
   - **Solo `multilane` — resuelve el lane objetivo**: el de la fase que corresponde al change (campo `lane` de `phases[]`). Si el usuario no dio slug y hay que deducir la fase, usa el lane activo de `openspec/.lane` como criterio.
   - **Solo `multilane` — si el lane objetivo no es el lane activo**, detente y pide al usuario que ejecute `aisdd lane switch <lane-id>` primero. No cambies el puntero tu mismo: es estado del dev, y cambiarlo en silencio le deja trabajando en una linea que no eligio.
   - **Solo `multilane` — si ese lane ya tiene un change abierto**, detente. Un lane = un hilo. Nombra el change vivo y remite a cerrarlo (`aisdd close change`) o enmendarlo (`aisdd amend change`). Que otros lanes tengan changes abiertos es normal y **no** bloquea.
   - **Solo `multilane` — si la fase es una barrera (`barrier: true`, ids `F0` o `FB-NN`)**, exige que **ningun** lane tenga changes abiertos. Si alguno lo tiene, detente y lista cuales: una barrera toca superficie compartida y no puede convivir con trabajo de lane en vuelo.
   - **Dependencias de la fase (los tres modos).** Si la fase trae `depends_on`, comprueba que **todas** esas fases estan ya archivadas. Si alguna sigue abierta o sin empezar, detente y dilo: abrir un change cuyas dependencias no han cerrado produce specs sobre algo que aun no existe. Nombra la fase que falta y quien la lleva (su lane, si lo hay).
   - **En modo `waves`** no hay guard de concurrencia: las oleadas son planificacion, no control de ejecucion, y **ningun comando comprueba el ancho `N`**. Aplica solo la comprobacion de `depends_on` anterior. Si detectas que hay mas changes abiertos que `parallel_developers`, **dilo como aviso** en el resumen y continua: es informacion util para el equipo, no un error que te corresponda bloquear.
   - En modo `atomic` no hay guard de concurrencia. Aplica solo la comprobacion de `depends_on`.
1. Si el usuario aporta `<what-you-want-to-build>`, usalo literalmente como descripcion o identificador del cambio.
2. Si no lo aporta, deriva un identificador breve y estable desde el objetivo descrito por el usuario.
3. Ejecuta el **pre-flight de dudas para apertura** segun la seccion siguiente.
4. Cuando el pre-flight termine y no queden dudas bloqueantes pendientes, ejecuta:
   ```bash
   openspec new change <what-you-want-to-build>
   ```
5. **Enmiendas pendientes de esta fase (solo `multilane`).** Si la fase trae `amended_by` en `config.yaml`, otro lane enmendo el contrato compartido **mientras esta fase esperaba**. Antes de redactar specs, lee el `decisions.md` del change indicado (archivado o vivo), incorpora ese delta a los specs de este change y dilo en el resumen. Es el unico mecanismo que evita que un lane rezagado implemente contra un contrato ya desmentido; si lo ignoras, la marca no sirve de nada. Una vez incorporado, **retira la marca** de `config.yaml`.
6. Localiza los artefactos generados del cambio: `design.md`, `proposal.md` y ficheros `spec.md`. Alimentalos con las decisiones recogidas en el pre-flight (alcance, dominios, integraciones, modelo de datos, criterios de aceptacion). **En modo `multilane`**, anota ademas en `proposal.md` una linea `Lane: <lane-id>` y las **rutas permitidas** del lane: son el contrato que `aisdd close change` verificara al cerrar, y el implementador debe conocerlas antes de escribir codigo.
7. **Diagramas UML solo si el change lo amerita.** Evalua el contenido de `proposal.md`/`design.md`/`spec.md` y lanza `booster-uml` unicamente cuando los diagramas aporten comprension real:
   - **Si lo amerita** (basta con cumplir uno): interaccion entre varios componentes/actores/sistemas (secuencia), entidades de dominio nuevas o relaciones que cambian (clases/ER), ciclo de vida o maquina de estados, flujo con ramificaciones o decisiones no triviales (actividad), o una integracion externa nueva.
   - **No lo amerita**: scaffolding/foundation puro, cambios de configuracion o dependencias, textos/estilos, docs-only, un bugfix puntual o renombrados — en estos casos **omite** la generacion con una linea en el resumen ("Diagramas UML omitidos: el change no los amerita") y recuerda que `aisdd uml <slug>` los genera bajo demanda en cualquier momento.
   - **En caso de duda, genera** (el coste es bajo y el humano puede ignorarlos). Si el usuario pide explicitamente diagramas siempre o nunca, su preferencia manda sobre este criterio.
8. **Enlace con Jira (opcional)**: si la integracion con Jira esta activa (ver "Integracion con Jira (opcional)"):
   - Identifica la(s) **HU** que realiza este change a partir de `docs/roadmap.md`, `docs/mapa-historias-usuario.md` y `docs/jira-sync.md`. Si no es deducible con confianza, preguntalo (cuenta dentro del presupuesto de pre-flight).
   - Anota la(s) HU en `proposal.md` (p. ej. una linea "Historias: HU-03, HU-05").
   - **Resuelve el modo de cada HU** (ver "Modelo de datos en Jira"): si la HU se realiza **solo con este change** (modo Story directa), **no crees sub-tarea** — registra el mapeo change -> HU en `docs/jira-sync.md` y deja la Story en To Do. Si la HU se reparte entre **2 o mas changes** (modo sub-tarea), crea la **sub-tarea de este change** bajo la Story de esa HU (tipo `subtask_issue_type`) si no existe; no la dupliques.
   - Registra en `docs/jira-sync.md` la fila/celda de cada HU implicada (clave de sub-tarea solo en modo sub-tarea) con estado `to_do`. No muevas de columna aqui (eso es `implement`/`close`).
   - Si una HU no tiene Story todavia (aun no se volco el plan), anota el change en el registro como pendiente de Story y avisa en el resumen.
9. Reporta el identificador del cambio, rutas creadas, decisiones del pre-flight grabadas en `openspec/changes/<change>/decisions.md`, la decision sobre los diagramas UML (ruta del HTML si se generaron; motivo de la omision si no) y, si aplico, la sub-tarea de Jira creada y enlazada.

### Pre-flight de dudas para apertura

Antes de generar los specs del cambio, revisa el contexto disponible y resuelve ambiguedades con el usuario. Esta fase es obligatoria para `open change`.

1. Reune y lee el contexto relevante disponible **antes** de crear el cambio:
   - Objetivo declarado por el usuario y `<what-you-want-to-build>` si llega.
   - Documentacion del proyecto: `docs/` (en especial `docs/roadmap.md` si existe), `README.md`, `config.yaml`, `AGENTS.md`, `CLAUDE.md`.
   - Cambios OpenSpec previos en `openspec/changes/` y especificaciones en `openspec/specs/` que toquen el mismo dominio funcional.
2. Detecta dudas reales que afecten al alcance y al diseno del cambio, y clasificalas:
   - **bloqueante**: sin respuesta no se pueden redactar specs solidos (alcance funcional, dominios afectados, modelo de datos, contrato de API, autenticacion, integraciones externas, migraciones, permisos, criterios de aceptacion principales).
   - **preferencia**: hay varias opciones validas y la elegida condiciona el diseno (libreria, patron, naming de recursos, particion en uno o varios changes).
   - **confirmacion**: parece claro pero conviene validar antes de redactar (suposiciones sobre actores, canales, plataformas soportadas).
3. No preguntes lo que ya esta resuelto:
   - objetivo y alcance explicitos del usuario o del prompt del roadmap.
   - **el faseado del roadmap y el reparto en sprints**: que HU entran en este change ya esta decidido (fase + sprint). **No ofrezcas adelantar HU de otras fases** ni ampliar el alcance del change — no es una duda, es una decision ya tomada (ver "El faseado es normativo"). Las dudas de alcance legitimas son sobre el **COMO** de las HU de esta fase, no sobre el QUE ni el CUANDO.
   - convenciones documentadas en el repo (`README.md`, `CLAUDE.md`, `AGENTS.md`, `docs/`, `config.yaml`).
   - elecciones triviales y facilmente reversibles (nombres internos, formato de log).
   - puntos ya cubiertos por specs OpenSpec previas o por cambios OpenSpec relacionados ya cerrados.
   - **en modo `multilane`, las enmiendas ya registradas**: si la fase trae `amended_by`, ese delta es una decision tomada, no una duda. Incorporalo (paso 5) en vez de preguntarlo.
   - **en modo `multilane`, el contrato compartido**: esquema de datos, contrato de API, eventos y tipos compartidos quedaron fijados en `F0` o en una barrera. **No los renegocies en el pre-flight de una fase de lane** — leelos de las specs ya archivadas y trabaja contra ellos. Si el contrato resulta insuficiente para implementar esta fase, eso no es una duda de pre-flight: es un fallo de faseado. Detente, dilo, y remite al dueno del contrato (`roadmap.contract_owner`) y a una barrera.
4. Presupuesto de preguntas: maximo `7` dudas por cambio — **es un techo, no una cuota**. Pregunta solo las dudas **reales**: si hay una, pregunta una; si no hay ninguna, no preguntes nada y continua (deja constancia de que el pre-flight no detecto dudas). **Nunca rellenes el presupuesto** con preguntas sobre asuntos ya decididos (faseado, docs, specs previas, decisiones del usuario) ni confirmaciones triviales: entorpecen sin aportar. Si detectas mas de 7, prioriza bloqueantes, agrupa relacionadas en una sola pregunta de varias opciones y descarta las de confirmacion de bajo impacto.
5. Formato de las preguntas:
   - Si la plataforma soporta preguntas estructuradas con opciones (por ejemplo `AskUserQuestion` en Claude Code), usalo con 2-4 opciones y marca una como `(Recomendada)` cuando tengas criterio para sugerirla.
   - En caso contrario, presenta las dudas como lista numerada en texto plano, con opciones etiquetadas `a)`, `b)`, `c)` y una recomendacion explicita.
   - Cada duda debe incluir: contexto breve (objetivo del usuario o seccion del roadmap/docs donde aparece), por que se necesita la respuesta y el impacto en los specs.
6. Modo no interactivo (auto mode, CI, sin terminal o el usuario pide no ser interrumpido):
   - No bloquees el comando por dudas no bloqueantes.
   - Toma el default recomendado para cada `preferencia` y `confirmacion`.
   - Para `bloqueantes` sin default seguro, detente y reporta las dudas pendientes; no ejecutes `openspec new change`.
   - Marca cada decision autonoma con `Origen: auto-default` en `decisions.md` para que el usuario pueda revisarla despues.
7. Persistencia: graba todas las respuestas en `openspec/changes/<change>/decisions.md`. Como en este momento el cambio aun no existe en disco, crea el directorio `openspec/changes/<change>/` antes de escribir el fichero, o escribe primero las decisiones en un buffer temporal y vuelcalas a `decisions.md` inmediatamente despues de ejecutar `openspec new change` y antes de redactar el contenido de `design.md`, `proposal.md` y los `spec.md`. Estructura cada entrada asi:

   ```markdown
   ## <slug-de-la-decision>

   - **Fecha**: <YYYY-MM-DD>
   - **Tipo**: bloqueante | preferencia | confirmacion | correccion
   - **Origen**: usuario | auto-default
   - **Contexto**: <objetivo del usuario / docs/roadmap.md / spec previa, seccion o linea>
   - **Pregunta**: <pregunta planteada>
   - **Opciones evaluadas**:
     - a) <opcion>
     - b) <opcion>
   - **Decision**: <opcion elegida>
   - **Justificacion**: <una linea con el motivo>
   ```

8. Si el usuario rechaza responder o pide aplazar una duda, registra `Decision: pendiente` y, si era bloqueante, detente sin ejecutar `openspec new change`. Informa al usuario de las dudas pendientes y termina.
9. Si tras la lectura inicial no detectas dudas reales, registra una unica entrada en `decisions.md` con `Tipo: confirmacion`, `Pregunta: No se detectaron dudas durante el pre-flight de apertura` y `Decision: continuar`. No fuerces preguntas artificiales solo por cumplir el flujo.
10. Antes de generar los specs, resume al usuario el conjunto de decisiones tomadas y confirma que esas decisiones se reflejaran en `design.md`, `proposal.md` y los `spec.md` del cambio.

## `aisdd implement change [what-you-want-to-build]`

> Alias: `native-ai implement change [what-you-want-to-build]`.

Implementa un cambio OpenSpec con una fase previa de pre-flight para resolver dudas con el usuario antes de tocar codigo.

1. Si llega `<what-you-want-to-build>`, usalo como cambio objetivo.
2. Si no llega, lista los cambios abiertos con OpenSpec.
3. Si solo hay un cambio abierto, usalo.
4. Si hay mas de uno, pregunta cual desea implementar.
5. Ejecuta el **pre-flight de dudas** segun la seccion siguiente.
6. Cuando el pre-flight termine y no queden dudas bloqueantes pendientes, ejecuta:
   ```bash
   openspec instructions apply --change <what-you-want-to-build>
   ```
7. **Transicion en Jira (opcional)**: si la integracion con Jira esta activa (ver "Integracion con Jira (opcional)"), al arrancar la implementacion:
   - Localiza en `docs/jira-sync.md` las **HU del change** y resuelve el **modo** de cada una (Story directa vs sub-tarea). Si una HU en modo sub-tarea no tiene aun la sub-tarea de este change (p. ej. se abrio sin Jira), creala ahora como en `open change`; si una HU no tiene Story, omitela con aviso.
   - Resuelve el usuario asignado (cuenta del MCP o `assignee_override`) y mueve a **In Progress** (descubriendo la transicion, sin hardcodear): en modo directo la **Story**; en modo sub-tarea la **sub-tarea y su Story padre**. Asigna al usuario resuelto lo que muevas.
   - Actualiza el estado de cada HU implicada en `docs/jira-sync.md` a `in_progress`.
8. Si durante la implementacion, o en la validacion posterior, surge un cambio que ningun spec habia especificado (incompatibilidad de versiones, ajuste de configuracion, peticion del usuario sobre la marcha), **no escales por defecto**: clasificalo segun "Correcciones durante la implementacion" y resuelvelo en el nivel que le corresponda.
9. Resume instrucciones aplicadas, ficheros afectados si OpenSpec los indica, decisiones y correcciones grabadas en `decisions.md`, la transicion de Jira aplicada (claves de sub-tarea y Story, columna destino, asignado) si la hubo, y cualquier accion manual pendiente.

### Pre-flight de dudas

Antes de aplicar las instrucciones de OpenSpec, revisa la documentacion del cambio y resuelve ambiguedades con el usuario. Esta fase es obligatoria para `implement change`.

1. Reune y lee los artefactos del cambio:
   - `openspec/changes/<change>/design.md`
   - `openspec/changes/<change>/proposal.md`
   - todos los ficheros `openspec/changes/<change>/specs/**/spec.md`
   - si existe, `openspec/changes/<change>/tasks.md`
   - si existe, `openspec/changes/<change>/decisions.md` (decisiones previas del mismo cambio)
2. Detecta dudas reales que afecten a la implementacion y clasificalas:
   - **bloqueante**: sin respuesta no se puede empezar (modelo de datos, contrato de API, autenticacion, integraciones externas, migraciones, permisos)
   - **preferencia**: hay varias opciones validas y la elegida condiciona el resultado (libreria, patron, naming, ubicacion del fichero)
   - **confirmacion**: parece claro pero conviene validar antes de codificar
3. No preguntes lo que ya esta resuelto:
   - decisiones cerradas en `design.md` o `proposal.md`
   - convenciones documentadas en el repo (`README.md`, `CLAUDE.md`, `AGENTS.md`, `docs/`, `config.yaml`)
   - elecciones triviales y facilmente reversibles (nombres internos, formato de log)
   - puntos ya cubiertos por entradas previas de `decisions.md`
4. Presupuesto de preguntas: maximo `7` dudas por cambio — **es un techo, no una cuota**. Pregunta solo las dudas **reales**: si hay una, pregunta una; si no hay ninguna, no preguntes nada y continua (deja constancia de que el pre-flight no detecto dudas). **Nunca rellenes el presupuesto** con preguntas sobre asuntos ya decididos (faseado, docs, specs previas, decisiones del usuario) ni confirmaciones triviales: entorpecen sin aportar. Si detectas mas de 7, prioriza bloqueantes, agrupa relacionadas en una sola pregunta de varias opciones y descarta las de confirmacion de bajo impacto.
5. Formato de las preguntas:
   - Si la plataforma soporta preguntas estructuradas con opciones (por ejemplo `AskUserQuestion` en Claude Code), usalo con 2-4 opciones y marca una como `(Recomendada)` cuando tengas criterio para sugerirla.
   - En caso contrario, presenta las dudas como lista numerada en texto plano, con opciones etiquetadas `a)`, `b)`, `c)` y una recomendacion explicita.
   - Cada duda debe incluir: contexto breve (donde aparece en el spec), por que se necesita la respuesta y el impacto en la implementacion.
6. Modo no interactivo (auto mode, CI, sin terminal o el usuario pide no ser interrumpido):
   - No bloquees el comando por dudas no bloqueantes.
   - Toma el default recomendado para cada `preferencia` y `confirmacion`.
   - Para `bloqueantes` sin default seguro, detente y reporta las dudas pendientes; no ejecutes `openspec instructions apply`.
   - Marca cada decision autonoma con `Origen: auto-default` en `decisions.md` para que el usuario pueda revisarla despues.
7. Persistencia: graba todas las respuestas en `openspec/changes/<change>/decisions.md`. Crea el fichero si no existe. Estructura cada entrada asi:

   ```markdown
   ## <slug-de-la-decision>

   - **Fecha**: <YYYY-MM-DD>
   - **Tipo**: bloqueante | preferencia | confirmacion | correccion
   - **Origen**: usuario | auto-default
   - **Contexto**: <referencia a design.md / proposal.md / spec.md, seccion o linea>
   - **Pregunta**: <pregunta planteada>
   - **Opciones evaluadas**:
     - a) <opcion>
     - b) <opcion>
   - **Decision**: <opcion elegida>
   - **Justificacion**: <una linea con el motivo>
   ```

8. Si el usuario rechaza responder o pide aplazar una duda, registra `Decision: pendiente` y, si era bloqueante, detente sin ejecutar `openspec instructions apply`. Informa al usuario de las dudas pendientes y termina.
9. Si tras la lectura inicial no detectas dudas reales, registra una unica entrada en `decisions.md` con `Tipo: confirmacion`, `Pregunta: No se detectaron dudas durante el pre-flight` y `Decision: continuar`. No fuerces preguntas artificiales solo por cumplir el flujo.
10. Antes de pasar a la implementacion real, resume al usuario el conjunto de decisiones tomadas y confirma que puede arrancar `openspec instructions apply`.

### Correcciones durante la implementacion

Durante `implement change`, o en la validacion posterior, aparecen cambios que nadie habia especificado: una incompatibilidad de versiones, un ajuste de configuracion, un matiz visual que el usuario pide sobre la marcha. **No todos merecen el mismo proceso.** Clasifica antes de actuar:

| Nivel | Situacion | Que haces |
|-------|-----------|-----------|
| 1. Implementacion | El spec es correcto y el codigo no lo cumple | Corriges el codigo. **No** tocas documentacion ni `decisions.md` |
| 2. Decision no documentada | Ningun documento AIDD fijaba ese detalle | Resuelves, registras `Tipo: correccion` en `decisions.md` y **continuas** |
| 3. Contradiccion documental | Un documento sellado afirma lo contrario | Corriges **ese** documento (y solo ese), se re-sella, y despues alineas los artefactos del change |
| 4. Contrato compartido (solo `multilane`) | La correccion toca el contrato sobre el que trabajan otros lanes | **Parada coordinada**: no la apliques por tu cuenta (ver abajo) |

**Regla de corte.** La pregunta no es "cambia el codigo?", sino **"queda algun documento AIDD sellado diciendo algo falso?"**. Si la respuesta es no, es nivel 2 y se resuelve dentro del change.

**Segunda regla de corte, solo en modo `multilane`.** Antes de aplicar la clasificacion anterior, pregunta: **"esto cambia algo sobre lo que otro lane esta trabajando ahora mismo?"** — esquema de datos, contrato de API, eventos, tipos compartidos, o cualquier ruta fuera de los `paths` de tu lane. Si la respuesta es si, **el nivel no importa**: es nivel 4 y no se resuelve dentro del change.

Una correccion es **lane-local** —y entonces sigue la tabla normal— cuando toca solo rutas y specs de tu propio lane. Ese es el caso comun y no cambia nada de lo anterior.

Reglas de aplicacion:

1. **Comprueba antes de clasificar.** Busca el elemento afectado (version, token de estilo, endpoint, nombre) en `docs/` y en los `spec.md` del change antes de decidir el nivel. No asumas que no esta documentado: verificalo y anota que revisaste.
2. **Un nivel 2 no dispara una segunda pasada.** Nunca re-ejecutes `openspec instructions apply` para incorporar una correccion de nivel 2: aplica el cambio directamente sobre el codigo y registra la decision. Re-aplicar un change sobre un arbol ya implementado arriesga rehacer trabajo y pisar ficheros. Si la correccion exige ademas tocar los specs del change (criterios nuevos, tareas nuevas), esa es la via del skill **`aisdd-amend`** (`aisdd amend change`), que especifica e implementa unicamente el delta.
3. **Un nivel 3 corrige un solo documento.** La cadena completa hacia arriba (`cliente-requisitos.md` -> `requisitos.md` -> `propuesta-arquitectura-base.md` -> `arquitectura-base.md`) solo se recorre cuando el cambio nace de una decision del cliente sobre el alcance. Un hallazgo tecnico durante el desarrollo afecta normalmente a `arquitectura-base.md` y a nada mas. Los documentos AIDD los actualiza su skill (`aidd architecture`, `aidd style-guide`...), que ademas re-sella la version con `stamp_doc.py`; no los edites por tu cuenta salvo que el cambio sea de una linea y lo confirmes con el usuario.
4. **No escales por defecto.** Un nivel 2 no se reporta al AI Lead ni se escala al Architect. Escalar cuesta un ciclo completo y solo se justifica en nivel 3.
5. **Registra siempre el nivel 2.** El suelo de trazabilidad es una entrada en `decisions.md`; nunca cero. Sin ella el repositorio acaba contradiciendo a sus propios documentos sin constancia de cuando se torcio.
6. **Si el mismo tipo de correccion se repite** en un change, dilo en el resumen del comando: varias correcciones del mismo tipo son sintoma de specs flojas y material a corregir en el siguiente `open change`.
7. **Si el change ya esta archivado**, no lo reabras: la correccion va en un change nuevo (`aisdd open change <slug>`).
8. **Nivel 4: parada coordinada (solo `multilane`).** No apliques la correccion. Haz esto:
   - **Detente y dilo.** Nombra que parte del contrato queda desmentida y que lanes dependen de ella (los que tengan changes abiertos, segun `openspec list` y el campo `lane` de sus fases).
   - **Registra** la entrada en `decisions.md` con `Nivel: 4` y `Estado: pendiente de barrera`, sin aplicar el cambio en codigo.
   - **Remite al dueno del contrato** (`roadmap.contract_owner` en `config.yaml`). La decision es suya, no del dev que la encontro.
   - **Avisa de que los lanes hermanos estan trabajando sobre un supuesto ya desmentido.** Este aviso es el valor del nivel 4: sin el, otro dev sigue implementando contra un contrato que ya sabemos falso.
   - La via de resolucion es una **barrera** (`FB-NN`) via `aisdd roadmap`, o un `aisdd amend change` cross-lane si los changes afectados estan vivos y el delta es acotado. Nunca una correccion silenciosa dentro de un lane.

   Un nivel 4 **es** caro — cuesta parar a varias personas. Esa es la razon de que exista: si no fuera caro, el faseado permitiria que los lanes se contradijeran gratis.

Formato de la entrada en `openspec/changes/<change>/decisions.md`:

```markdown
## <slug-de-la-correccion>

- **Fecha**: <YYYY-MM-DD>
- **Tipo**: correccion
- **Nivel**: 2 (decision no documentada) | 3 (contradiccion documental) | 4 (contrato compartido)
- **Origen**: usuario | auto-default
- **Contexto**: <donde surgio: criterio X de la validacion, peticion del usuario durante la implementacion>
- **Documentos comprobados**: <ficheros de docs/ y spec.md revisados; que fijaban y que no>
- **Decision**: <lo que se aplica>
- **Justificacion**: <una linea con el motivo>
- **Documentos actualizados**: <nivel 3: fichero corregido y version resellada | nivel 2: ninguno>
- **Lane**: <lane-id>                        # solo en modo multilane
- **Lanes afectados**: <lane-id, ...>        # solo nivel 4: los que dependen del contrato desmentido
- **Estado**: aplicada | pendiente de barrera   # solo nivel 4 usa "pendiente de barrera"
```

El campo **Documentos comprobados** es lo que hace auditable la regla de corte: deja constancia de que el nivel se decidio mirando, no suponiendo.

## `aisdd close change [what-you-want-to-build]`

> Alias: `native-ai close change [what-you-want-to-build]`.

Archiva un cambio OpenSpec.

1. Si llega `<what-you-want-to-build>`, usalo como cambio objetivo.
2. Si no llega, lista cambios abiertos.
3. Si solo hay un cambio abierto, usalo.
4. Si hay mas de uno, pregunta cual desea archivar. **En modo `multilane`**, filtra primero por el lane activo (`openspec/.lane`): si ese lane tiene exactamente un change abierto, usalo sin preguntar; que otros lanes tengan changes vivos no genera ambiguedad, porque no son tuyos.
5. **Verificacion de independencia (solo si `roadmap.mode` es `multilane`).** Antes de archivar, comprueba que el change respeto las fronteras de su lane. Es el punto donde la independencia deja de ser una promesa del faseado y pasa a estar verificada:
   - **Rutas**: obten los ficheros que el change toco (`git diff --name-only` contra el punto de partida del change, o el equivalente disponible) y comprueba que **todos** caen bajo los `paths` de su lane (`roadmap.lanes[].paths` en `config.yaml`).
   - **Specs**: comprueba que ningun `spec.md` modificado pertenece a otro lane.
   - **Si algo cae fuera**, **no archives**. Reporta la lista exacta de ficheros o specs infractores y ofrece las tres salidas posibles: (a) mover ese trabajo al lane que le corresponde, (b) convertirlo en una barrera `FB-NN` si es genuinamente compartido — via `aisdd roadmap`, o (c) que el usuario declare explicitamente que acepta el solape, en cuyo caso registralo como `Nivel: 4` en `decisions.md` antes de archivar. Nunca archives en silencio un change que se salio de su lane: eso convierte el modelo de lanes en decorativo.
   - **Fases barrera** (`barrier: true`): no tienen restriccion de rutas — por definicion tocan superficie compartida. Sáltate esta verificacion para ellas.
   - En modo `atomic` este paso no aplica.
6. Ejecuta:
   ```bash
   openspec archive <what-you-want-to-build>
   ```
7. **Transicion en Jira (opcional)**: si la integracion con Jira esta activa (ver "Integracion con Jira (opcional)"):
   - Localiza en `docs/jira-sync.md` las **HU del change** y resuelve el **modo** de cada una (Story directa vs sub-tarea).
   - **Modo directo**: mueve la **Story a Done** (descubriendo la transicion) y actualiza su estado en el registro a `done`.
   - **Modo sub-tarea**: mueve la **sub-tarea** de este change a **Done**; consulta via MCP las sub-tareas de la Story padre y muevela a **Done solo si TODAS estan Done** — si queda alguna abierta, deja la Story en In Progress e indica en el resumen que changes faltan.
8. Verifica que el cambio queda archivado y resume el resultado, incluyendo (si aplico) las Stories/sub-tareas pasadas a Done y las Stories que siguen pendientes. **En modo `multilane`**, indica ademas el lane cerrado, el resultado de la verificacion de independencia y **cual es la siguiente fase de ese lane** — el dev queda libre para abrirla de inmediato, que es el punto de todo el modelo.

## `aisdd lane [list | switch <lane-id> | status]`

> Alias: `native-ai lane ...`.

Consulta y cambia la **linea de trabajo activa** del dev. Es el equivalente de `git branch` / `git switch` para lanes: no mueve codigo ni toca changes, solo dice sobre que lane trabajan los siguientes `open`/`implement`/`close change`.

**Precondicion**: `roadmap.mode` debe ser `multilane` en `openspec/config.yaml`. Si es `atomic` o no existe, responde que el proyecto no usa lanes y que el modo se decide en `aisdd roadmap`; no crees `openspec/.lane`.

**Sin subcomando**, equivale a `status`.

### `list`

Lista los lanes de `roadmap.lanes` y, por cada uno:

- `lane-id`, label y perfil asignado
- rutas (`paths`)
- **change abierto**, si lo hay (de `openspec list` cruzado con el campo `lane` de las fases) — es lo que dice si el lane esta ocupado o libre
- fase siguiente pendiente de ese lane
- marca visible del lane activo

Anade al final las **barreras pendientes** (`FB-NN` no archivadas): bloquean a todos los lanes, asi que condicionan lo que cualquier dev puede abrir.

### `switch <lane-id>`

1. Valida que `<lane-id>` existe en `roadmap.lanes`. Si no, lista los validos y detente. **No lo crees**: los lanes nacen en `aisdd roadmap`, no aqui.
2. Escribe el `lane-id` en `openspec/.lane` (una linea, sin espacios). Crea el fichero si no existe.
3. Comprueba que `.gitignore` contiene `openspec/.lane`; si falta, anadela y dilo (`aisdd init` deberia haberlo hecho).
4. Informa del estado del lane destino: change abierto si lo hay, fase siguiente, y barreras pendientes que lo bloqueen.

**No hay guard aqui.** Cambiar de lane siempre esta permitido, incluso con un change abierto en el lane que dejas: ese change sigue vivo y te espera. El guard vive en `open change`, no en el cambio de puntero — igual que en Git cambiar de rama no cierra tu trabajo. Un dev puede saltar entre lineas de trabajo libremente; lo que no puede es tener dos changes abiertos en la **misma** linea.

### `status`

Informa de:

- lane activo (contenido de `openspec/.lane`), o aviso de que no hay ninguno seleccionado
- change abierto en ese lane, si lo hay, y en que estado
- fase siguiente del lane
- barreras pendientes que lo bloqueen
- si el puntero apunta a un `lane-id` que ya no existe en `config.yaml` (roadmap re-generado): avisa y propon `aisdd lane switch` a uno valido

Si `openspec/.lane` no existe y el modo es `multilane`, no falles: informa de que no hay lane activo y lista los disponibles.

## `aisdd prototype-ux [what-you-want-to-build]`

> Alias: `native-ai prototype-ux [what-you-want-to-build]`.

Genera prototipos UX.

- Si llega `<what-you-want-to-build>`, identifica en el cambio las pantallas nuevas o modificadas revisando `design.md`, `proposal.md` y `spec.md`.
- Lanza el skill `booster-ux` una vez por cada pantalla nueva identificada.
- Si no llega argumento, lanza directamente `booster-ux` y sigue su flujo de preguntas.
- Si no existe `booster-ux`, avisa donde debe instalarse y no generes prototipos por otro camino salvo peticion expresa del usuario.

## `aisdd uml [what-you-want-to-build]`

> Alias: `native-ai uml [what-you-want-to-build]`.

Genera HTML con diagramas asociados al cambio.

1. Resuelve el cambio objetivo igual que en `implement` si falta el argumento.
2. Reune `design.md`, `proposal.md` y todos los ficheros `spec.md` del cambio.
3. Lanza el skill `booster-uml` con esa documentacion para generar el HTML de diagramas.
4. Si no existe `booster-uml`, avisa donde debe instalarse y deja indicadas las rutas de entrada que deberia procesar.

## Integracion con Jira (opcional)

Enlaza cada change de OpenSpec con su historia de usuario (HU) en Jira y mueve los tickets de columna al implementar y cerrar. Es **opcional** y **no intrusiva**: si no esta configurada, todos los comandos funcionan igual y este bloque se omite por completo.

### Activacion y gating

Este bloque solo actua si se cumplen **las dos** condiciones:

1. Existe una seccion `jira:` en `openspec/config.yaml` (la escribe `aidd sprint-planning` al volcar el plan, o el usuario a mano).
2. Hay tools del MCP de Atlassian disponibles (localizalas por funcion con la busqueda de herramientas; los nombres varian entre versiones, no los asumas).

Si falta cualquiera de las dos, **omite la sincronizacion sin error**: anota una linea en el resumen del comando ("Jira no configurado o MCP no disponible: sincronizacion omitida") y continua. Nunca caigas a llamadas REST manuales ni gestiones credenciales desde el skill.

**Excepcion — enlace perdido (no omitas en silencio).** Si falta la configuracion o el registro pero hay **evidencia de un volcado previo** — `docs/sprint-plan.md` menciona un volcado o claves de Story ya creadas, existe `docs/jira-sync.md` sin seccion `jira:`, o el usuario afirma que las Stories ya existen en el board — **no** trates el caso como "sin configurar": avisa explicitamente de que el enlace HU<->Jira se perdio (las sub-tareas de los changes no se crearan y las Stories no se moveran) y ofrece **reconstruirlo** (ver "Reconstruccion del enlace perdido"). El humano decide; si declina, entonces si, omite con el aviso estandar.

### Modelo de datos en Jira (acordado)

- Cada **HU** es una **Story** (la crea `aidd sprint-planning`).
- Un **change** implementa **una o varias HU** (segun `docs/roadmap.md`, `docs/sprint-plan.md` y el detalle de HU). El change **mueve las Stories de todas las HU que implementa** — no solo la "principal".
- **Regla de decision, por HU (no por change)**: cuenta en cuantos changes aparece esa HU (campo `hus`/`change_hint` del roadmap y registro `docs/jira-sync.md`):
  - **HU cubierta por 1 solo change** -> **modo Story directa**: se opera sobre la Story; **no se crea sub-tarea** (una sub-tarea 1:1 solo duplica la Story y ensucia el board).
  - **HU cubierta por 2 o mas changes** -> **modo sub-tarea**: se crea **una sub-tarea por change** bajo la Story de esa HU (progreso atomico); la Story se cierra cuando **todas** sus sub-tareas estan Done.
- Un mismo change puede mezclar ambos modos: para una HU suya mueve la Story directa y para otra crea/mueve sub-tarea.
- **El modo se resuelve en el momento del comando.** Si un re-faseado hace que una HU en modo directo gane un segundo change mas tarde, los changes **nuevos** crean sub-tarea a partir de entonces (el trabajo ya hecho no se representa retroactivamente); la Story vuelve a In Progress al implementar el nuevo change y se cierra cuando sus sub-tareas pendientes esten Done.
- **Lanes (modo `multilane`)**: el `lane-id` se refleja como **etiqueta (label) de la Story y de sus sub-tareas**, para poder filtrar el board por linea de trabajo. Es lo unico que cambia: **el modelo hibrido HU<->Story<->sub-tarea no se altera**, no se crean boards ni epicas por lane, y el lane nunca sustituye a la HU como unidad. Si la etiqueta no se puede escribir (permisos, campo no disponible), avisa y continua: es informativo, no estructural.

### Configuracion (`openspec/config.yaml`, seccion `jira`)

```yaml
jira:
  site: <p. ej. miorg.atlassian.net>
  project_key: <CLAVE>
  board_id: <id del board Scrum>
  story_issue_type: Story            # tipo de issue para las HU
  subtask_issue_type: Sub-task       # tipo de issue para los changes
  status_in_progress: In Progress    # nombre objetivo de la columna "en curso"
  status_done: Done                  # nombre objetivo de la columna "terminado"
  assignee_override: <accountId o vacio>   # usar si el MCP autentica una cuenta de servicio
```

No inventes valores: si falta una clave necesaria, preguntala una vez y persistela en `config.yaml`.

**Issue types: descubrir, no asumir.** Los nombres `Story`/`Sub-task` del ejemplo son solo orientativos y **varian segun el tipo de proyecto Jira**: en proyectos *team-managed* la sub-tarea se llama `Subtask` y en *company-managed* `Sub-task`. Antes de crear el primer issue, lee los issue types reales del proyecto (tool del MCP de tipos de issue del proyecto), elige como `subtask_issue_type` el tipo con `subtask: true` y verifica que `story_issue_type` existe; si el valor configurado no coincide con ninguno real, corrigelo en `config.yaml` (pregunta si hay mas de un candidato) en lugar de dejar que la creacion falle.

### Registro de enlace (`docs/jira-sync.md`)

Fuente de verdad del mapeo HU <-> change <-> issue de Jira. Lo inicializa `aidd sprint-planning` (HU -> clave de Story) y lo completan los comandos de change. El **estado se lleva por HU/Story**; la columna de sub-tareas **solo se rellena en modo sub-tarea** (HU repartida entre 2+ changes) y queda vacia (`—`) en modo Story directa. Estructura en tabla:

| HU | Story (Jira) | change(s) | Sub-tarea(s) (Jira) | estado |
|----|--------------|-----------|---------------------|--------|
| HU-02 | ABC-11 | foundation | — | done |
| HU-03 | ABC-12 | back-auth, front-auth | ABC-45, ABC-46 | in_progress |

Regla de oro: **lee el registro antes de crear o transicionar nada y no dupliques**. Re-ejecutar un comando no debe crear sub-tareas repetidas ni revertir estados de forma incoherente.

### Reconstruccion del enlace perdido

Si las Stories ya existen en Jira pero falta `docs/jira-sync.md` y/o la seccion `jira:` (p. ej. un volcado antiguo que no persistio el enlace), el registro se puede **reconstruir sin tocar Jira** — las claves de issue son permanentes, asi que la operacion es de solo lectura contra Jira y de escritura solo local:

1. **Confirma con el humano** antes de empezar (que proyecto/board y que volcado se esta recuperando).
2. **Completa la configuracion**: pregunta los valores que falten de la seccion `jira:` (site, project_key, board_id...) y persistela en `openspec/config.yaml` (o en la cabecera de `docs/jira-sync.md` si no existe `openspec/`).
3. **Lee las Stories desde Jira** via MCP (issues del proyecto/board con el `story_issue_type` configurado) y las sub-tareas que ya cuelguen de ellas.
4. **Mapea HU <-> Story** cruzando el id/titulo de la HU (de `docs/mapa-historias-usuario.md` / `docs/sprint-plan.md`) con el summary de cada Story. **No adivines**: si un mapeo no es deducible con confianza, presenta la tabla propuesta y pide confirmacion antes de escribirla; nunca te fies solo de rangos de claves.
5. **Escribe `docs/jira-sync.md`** con una fila por HU (clave de Story real, changes previstos si el roadmap existe, sub-tareas encontradas y su estado actual leido de Jira).
6. **Nunca crees ni recrees issues durante la reconstruccion** (las claves quemadas no vuelven); registra la operacion en la auditoria (`openspec/audit/`).

### Resolucion del usuario asignado

1. Obten el `accountId` de la cuenta autenticada en el MCP (tool de tipo "current user" / "myself").
2. Si `jira.assignee_override` tiene valor (porque el MCP usa una cuenta de bot/servicio compartida), asigna a ese `accountId` en su lugar.
3. Si no se puede resolver ningun `accountId`, mueve de columna pero **no** toques el campo assignee, y avisa en el resumen.

### Descubrimiento de transiciones (no hardcodear)

Los nombres e ids de columna varian por workflow de Jira. Para mover un issue:

1. Consulta via el MCP las **transiciones disponibles** del issue.
2. Elige la transicion cuyo estado destino case (ignorando mayusculas/acentos) con `status_in_progress` o `status_done`, admitiendo sinonimos comunes (In Progress / En curso / Doing; Done / Completado / Finalizado / Cerrado).
3. Si ninguna transicion casa, **no fuerces**: avisa en el resumen y deja el issue como esta.

### Que hace cada comando (el detalle vive en cada comando)

Para **cada HU** que implementa el change, resuelve su modo (directa vs sub-tarea) y aplica:

| Comando | HU en 1 change (Story directa) | HU en 2+ changes (sub-tarea) |
|---------|--------------------------------|------------------------------|
| `open change` | **No** cambia el estado de la Story (sigue To Do: abrir es disenar specs, no implementar); registra el mapeo change -> HU en `docs/jira-sync.md` | Crea la **sub-tarea** del change bajo la Story (To Do) si no existe |
| `implement change` | Mueve la **Story** a **In Progress** y la asigna | Mueve la **sub-tarea y su Story** a In Progress y las asigna |
| `close change` | Mueve la **Story** a **Done** | Sub-tarea a **Done**; la Story a Done **solo si todas sus sub-tareas estan Done** |

En modo `multilane`, `open change` anade ademas el `lane-id` como **etiqueta** de la Story (y de la sub-tarea si la crea). Es informativo: si falla, avisa y continua.

Toda accion de Jira se refleja en el resumen del comando (claves de issue afectadas y transicion aplicada) y se anota en la entrada de auditoria (`output_files`/`notes`). Si una accion de Jira falla, **no bloquees** el resultado funcional del comando OpenSpec: informa el fallo en el resumen y deja el estado reconstruible.

## Auditoria y trazabilidad

Cada comando del skill debe registrar una entrada de auditoria estructurada para permitir auditorias futuras del uso del skill. El objetivo es trazar quien ejecuto que comando, sobre que entrada, con que prompt y modelo, y que salida o decision humana se produjo. La auditoria es obligatoria para todos los comandos.

### Ubicacion y formato

- Directorio: `openspec/audit/` en la raiz del proyecto. Crealo si no existe.
- Fichero: `openspec/audit/YYYY-MM.jsonl` (un fichero por mes natural). Modo append-only, una entrada JSON por linea.
- Codificacion: UTF-8 sin BOM. Sin comas ni corchetes envolventes: JSON Lines puro.
- No reescribas entradas existentes. Si necesitas corregir o anular una entrada, anade una nueva con `correction_of: <id>`.

### Esquema de cada entrada

Cada linea es un objeto JSON con estos campos:

```json
{
  "id": "<uuid v4 o ulid>",
  "timestamp": "<ISO 8601 UTC, p.ej. 2026-05-25T14:30:00Z>",
  "command": "aisdd <subcomando>",
  "change_id": "<id-del-cambio-o-null>",
  "skill_version": "<version del skill, p.ej. 1.2.0>",
  "prompt_version": "<skill_version>:<command-slug>[@variante]",
  "model": "<id del modelo, p.ej. claude-opus-4-7[1m] o desconocido>",
  "platform": "<claude-code | codex | otra>",
  "user": "<email o identificador disponible, o null>",
  "input_hash": "sha256:<hex>",
  "input_files": [
    { "path": "<ruta relativa>", "sha256": "<hex>" }
  ],
  "output_hash": "sha256:<hex>",
  "output_files": [
    { "path": "<ruta relativa>", "sha256": "<hex>" }
  ],
  "decisions": [
    {
      "slug": "<slug>",
      "type": "bloqueante | preferencia | confirmacion | correccion",
      "origen": "usuario | auto-default",
      "decision": "<resumen corto de la opcion elegida o 'pendiente'>"
    }
  ],
  "status": "ok | partial | aborted",
  "errors": [ "<mensaje corto>" ],
  "correction_of": "<id de entrada corregida, opcional>"
}
```

Reglas para los campos:

- `id`: generador propio del agente (UUID v4 o ULID). Debe ser unico.
- `timestamp`: hora UTC en formato ISO 8601 con sufijo `Z`.
- `input_hash`: SHA-256 hex del concatenado, en orden alfabetico ascendente por `path`, de las parejas `<path>\n<sha256>\n` de cada fichero en `input_files`. Si la lista esta vacia, usa `sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (hash del string vacio).
- `output_hash`: misma formula sobre `output_files`. Si el comando no produce ficheros nuevos ni modificados, usa el hash del string vacio y deja `output_files` vacio.
- `input_files`: ficheros leidos como entrada relevante del comando (artefactos del cambio, configuracion, documentos del usuario). No incluyas codigo fuente del repositorio salvo que el comando lo procese explicitamente.
- `output_files`: ficheros creados o modificados por el comando (proposal.md, design.md, spec.md, decisions.md, roadmap.md, HTML de UML, etc.).
- `decisions`: solo para comandos que recogen decisiones humanas (hoy: `implement change`). Incluye tanto las decisiones del pre-flight como las entradas de `Tipo: correccion` registradas durante la implementacion: son las que permiten contar correcciones por change como indicador de la calidad de los specs. En el resto de comandos, lista vacia.
- `model` y `platform`: si no puedes resolverlos con fiabilidad, usa `"desconocido"`. No inventes valores.
- `user`: si la plataforma expone email del usuario, registra el email; si no, `null`. No registres datos personales adicionales.
- `prompt_version`: usa la version del skill seguida del slug del comando. Ejemplos: `1.6.0:implement-change/preflight`, `1.6.0:open-change/preflight`, `1.6.0:roadmap`, `1.6.0:close-change`, `1.6.0:init`, `1.6.0:prototype-ux`, `1.6.0:uml`. El comando `aisdd lane` **no escribe auditoria**: no modifica artefactos del proyecto, solo un puntero local del dev.

### Calculo de hashes

- En PowerShell: `Get-FileHash -Algorithm SHA256 <path>`.
- En Bash o entornos POSIX: `sha256sum <path>` o `shasum -a 256 <path>`.
- Para el hash agregado (`input_hash`, `output_hash`), calcula el SHA-256 del string formado por las parejas `<path>\n<sha256>\n` concatenadas en orden alfabetico ascendente por `path`. Usa rutas relativas a la raiz del proyecto con separador `/`.

### Cuando escribir la entrada

- Escribe la entrada **al final** del comando, justo antes del resumen de verificacion.
- Una sola entrada por invocacion de comando.
- **Excepcion: `aisdd lane` no escribe auditoria.** No toca artefactos del proyecto — solo el puntero local `openspec/.lane` del dev — y registrarlo llenaria el log de ruido sin trazabilidad util.
- Si el comando se aborta antes de completar (por ejemplo dudas bloqueantes pendientes en el pre-flight), escribe igualmente con `status: aborted` y la informacion disponible.
- Si el comando falla por error, escribe con `status: partial` o `aborted` segun corresponda y rellena `errors` con mensajes cortos (sin trazas largas ni datos sensibles).

### Que NO registrar

- Contenido literal de los ficheros (solo hashes).
- Texto libre de las dudas planteadas en el pre-flight (el contenido vive en `decisions.md`).
- Secretos, tokens, credenciales, claves API, ni datos personales mas alla del email del usuario que ya proporciona la plataforma.
- Diffs de codigo. La entrada apunta a artefactos por hash; el codigo vive en git.

### Retencion

- Retencion por defecto: `365` dias.
- Resolucion del valor efectivo, por orden de precedencia:
  1. Clave `audit.retention_days` (entero positivo) en `config.yaml` de OpenSpec.
  2. Fichero `openspec/audit/.retention` con un entero positivo de dias en la primera linea.
  3. Default `365`.
- Al inicio de cada comando, comprueba los ficheros `openspec/audit/YYYY-MM.jsonl`:
  - Si el ultimo dia del mes representado por el fichero es anterior a `hoy - retencion`, eliminalo.
  - No purgues entradas individuales dentro de un fichero. Trabaja por mes para preservar la integridad append-only.
- Nunca apliques retencion menor a `30` dias aunque la configuracion lo indique: en ese caso usa `30` y avisa al usuario una vez.

### Compatibilidad y operacion

- Manten el JSONL plano y sin transformaciones para ingestar en Splunk, ELK, BigQuery u otros sin parseo intermedio.
- No comprimas ni cifres los ficheros: deben ser legibles directamente.
- La decision de versionar `openspec/audit/` en Git es del proyecto. Recomienda al usuario incluirlo en seguimiento si la politica lo permite; en caso contrario, anadirlo a `.gitignore` y archivarlo aparte mediante el mecanismo de auditoria corporativo.
- Si la escritura de la entrada de auditoria falla (disco lleno, permisos), no bloquees el resultado funcional del comando: informa el fallo en el resumen y deja constancia en `errors` de un futuro reintento si es viable.

## Verificacion final

Al terminar cualquier comando, informa:

- comando Native AI solicitado
- comando OpenSpec ejecutado, si aplica
- cambio objetivo, si aplica
- artefactos creados o actualizados (incluye `decisions.md` si hubo pre-flight)
- decisiones tomadas en el pre-flight y cuales quedan `pendientes`, si aplica
- entrada de auditoria escrita: ruta del fichero `openspec/audit/YYYY-MM.jsonl` y `id` de la entrada
- skills auxiliares usados o pendientes de instalar
- errores o tareas manuales pendientes
- documentación faltante (en caso de que aplique)
- **en modo `multilane`**: lane activo, resultado de la verificacion de independencia si hubo cierre, y barreras pendientes que bloqueen al resto de lanes
