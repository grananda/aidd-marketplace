---
name: aisdd-specs
description: AISDD (AI Spec-Driven Development) — gestiona especificaciones sobre OpenSpec mediante los comandos `aisdd init`, `aisdd roadmap`, `aisdd open change`, `aisdd implement change`, `aisdd close change`, `aisdd prototype-ux` y `aisdd uml` (alias legacy equivalentes con prefijo `native-ai ...` siguen funcionando). Coordina documentacion funcional/tecnica/arquitectura y la capa de entrega de AIDD (planificacion-proyecto, sprint-plan, plan-revision-hu), roadmaps, diagramas con booster-uml y prototipos con booster-ux. `aisdd init` registra en `openspec/config.yaml` tanto la documentacion de diseno como la capa de entrega existente, y `aisdd roadmap` lee el `docs/sprint-plan.md` para fasear alineado a los sprints. Los comandos `open change` e `implement change` ejecutan un pre-flight de dudas (maximo 7 preguntas) antes de generar los specs y antes de aplicar las instrucciones de OpenSpec. Todos escriben una entrada de auditoria estructurada en `openspec/audit/`. Integracion opcional con Jira (MCP de Atlassian): `open change` crea la sub-tarea del change bajo la Story de su HU, `implement change` mueve sus tickets a In Progress, y `close change` los pasa a Done (la Story padre solo cuando todas sus sub-tareas estan Done); sin configuracion, los comandos funcionan igual y la sincronizacion se omite. Usar cuando el usuario invoque `aisdd ...` o `native-ai ...`, o pida trabajar con especificaciones OpenSpec/Native AI.
metadata:
  author: NTT DATA Spain GDN-e
  version: "1.0.0"
---

# aisdd-specs (AI Spec-Driven Development)

Usa este skill cuando el usuario pida trabajar con especificaciones AISDD / OpenSpec, o cuando invoque cualquiera de estos comandos (prefijo primario **`aisdd`**; el prefijo **`native-ai`** se mantiene como **alias legacy** equivalente):

- `aisdd init`            (alias: `native-ai init`)
- `aisdd roadmap`         (alias: `native-ai roadmap`)
- `aisdd open change [what-you-want-to-build]`       (alias: `native-ai open change ...`)
- `aisdd implement change [what-you-want-to-build]`  (alias: `native-ai implement change ...`)
- `aisdd close change [what-you-want-to-build]`      (alias: `native-ai close change ...`)
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
9. **Check ligero (no bloqueante).** AISDD **asume** que la planificacion de AIDD es correcta; no la re-valides a fondo. Limitate a avisar en el resumen si: (a) alguna ruta indicada no existe; (b) hay `sprint-plan.md`/`planificacion-proyecto.md` pero falta el detalle de HU que los sustenta; o (c) **no** hay capa de entrega (ni `sprint-plan.md` ni `planificacion-proyecto.md`) — en ese caso informa de que `aisdd roadmap` faseara sin alinear a sprints. Son avisos, no errores: continua igualmente.
10. Registra los comandos del skill en el `AGENTS.md` del proyecto segun la seccion siguiente.

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
   - `aisdd close change <what-you-want-to-build>` — archiva el cambio OpenSpec.
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
7. Cuando tengas contexto suficiente, actua con este rol y objetivo:
   ```text
   Actua con el rol de planificador experto de desarrollos de software.
   Analiza los requisitos y fasea el desarrollo en las fases que consideres necesarias para implementarlo con openspec. Ajusta la granularidad del roadmap al presupuesto de contexto del modelo: cuanto menor sea, mas fases y mas pequenas deben ser. Evita fases demasiado grandes que obliguen a arrastrar demasiado contexto en un unico change. Basate en la arquitectura del proyecto. Si existe una planificacion de entrega (docs/sprint-plan.md), alinea el faseado a los sprints: mismo orden, cortes de fase coincidiendo con fronteras de sprint y gates de validacion, y manten los changes de una misma HU dentro de la ventana del sprint donde esa HU esta planificada; el presupuesto de contexto sigue mandando el tamano del change, y donde choque con el sprint, marcalo como conflicto en vez de romper el plan. Con ello genera docs/roadmap.md con la division por fases, que entra en cada fase y a que sprint(s) corresponde. Ademas, crea docs/prompts-roadmap-native-ai.md con los prompts a ejecutar hasta finalizar el desarrollo usando los comandos del skill aisdd. No modifiques aun ningun documento de openspec. Si el usuario no ha pasado requisitos y/o arquitectura o no tienes clara donde esta, solicitaselo.
   ```
8. Crea el directorio `docs/` si no existe.
9. Genera `docs/roadmap.md` con:
   - presupuesto de contexto asumido y justificacion
   - complejidad estimada
   - fases ordenadas
   - objetivo de cada fase
   - alcance y exclusiones
   - dependencias
   - entregables OpenSpec esperados
   - criterios de cierre
   - riesgo de contexto por fase: `bajo`, `medio` o `alto`
   - **si hay `docs/sprint-plan.md`**: a que **sprint(s)** corresponde cada fase, el **esfuerzo agregado** de la fase (humano vs IA, tomado de `planificacion-proyecto.md`/`sprint-plan.md` si estan) y una seccion **"Conflictos de alineacion roadmap<->sprint"** con lo que el presupuesto de contexto obligo a desviar del plan de sprints (ver "Alineacion con la capa de entrega").
10. Genera `docs/prompts-roadmap-native-ai.md` con los prompts que deben ejecutarse hasta finalizar el desarrollo, usando solo estos comandos del skill:
   - `aisdd open change <what-you-want-to-build>`
   - `aisdd implement change <what-you-want-to-build>`
   - `aisdd close change <what-you-want-to-build>`
11. En `docs/prompts-roadmap-native-ai.md`, para cada fase indica explicitamente:
   - que documentos o secciones pasar al modelo
   - que partes del codigo son relevantes
   - que no debe incluirse todavia para no contaminar contexto
   - cuando conviene dividir una fase en varios changes OpenSpec
   - el sprint al que pertenece la fase (si hay `sprint-plan.md`)
   - el prompt exacto para abrir el change con `aisdd open change <what-you-want-to-build>`
   - el prompt exacto para implementar con `aisdd implement change <what-you-want-to-build>`
   - el prompt exacto para cerrar con `aisdd close change <what-you-want-to-build>`
12. Los prompts de `docs/prompts-roadmap-native-ai.md` deben estar redactados para un usuario final o para otro agente, en espanol, e incluir el contexto minimo necesario para ejecutar cada fase sin arrastrar informacion irrelevante de fases futuras.
13. No uses en ese fichero comandos OpenSpec directos como `openspec new change`, `openspec instructions apply` u `openspec archive`, salvo de forma explicativa excepcional fuera de los prompts operativos.
14. Tras generar `docs/roadmap.md` y `docs/prompts-roadmap-native-ai.md`, actualiza `openspec/config.yaml` con el resumen del roadmap segun la seccion siguiente.
15. No ejecutes `openspec new change`, no archives cambios y no edites ningun otro artefacto de `openspec/` (changes, specs) durante este comando. La unica escritura permitida en `openspec/` es la actualizacion de `openspec/config.yaml` descrita en el paso 14.

### Alineacion con la capa de entrega (sprint-plan)

Si existe `docs/sprint-plan.md`, el roadmap **se pliega a los sprints ya planificados** por AIDD, sin dejar que la capacidad mande sobre el presupuesto de contexto. Regla de jerarquia: **el presupuesto de contexto decide el tamano del change; el sprint decide el orden, las fronteras y que HU estan comprometidas.**

- **Orden**: fasea en el **mismo orden** que los sprints (que ya refleja prioridad de negocio, capacidad y dependencias).
- **Fronteras**: haz coincidir los **cortes de fase con las fronteras de sprint** y con los gates de validacion (de `plan-revision-hu.md`) siempre que el contexto lo permita.
- **Agrupacion**: manten los **changes de una misma HU dentro de la ventana del sprint** donde esa HU esta planificada, para que un sprint no quede con changes a medias.
- **HU no validadas**: si `docs/plan-revision-hu.md` marca una HU como **en revision o bloqueada**, no la metas en una fase temprana como comprometida; senala que depende de su validacion.
- **Esfuerzo**: anota en cada fase el esfuerzo agregado (humano vs IA) tomado de `planificacion-proyecto.md`/`sprint-plan.md`.
- **Conflictos (no romper el plan)**: cuando el presupuesto de contexto obligue a partir una HU en varios changes que **no caben** en su sprint, o a cortar a mitad de un bloque, **no reescribas el sprint-plan**: registra el desajuste en la seccion **"Conflictos de alineacion roadmap<->sprint"** de `docs/roadmap.md` (que HU se parte, en cuantos changes, que sprint desborda) para que el humano re-ejecute `aidd sprint-planning` y re-empaquete (re-faseado seguro: mueve HU, no recrea issues). AISDD **no** modifica `docs/sprint-plan.md`.

Si **no** hay `sprint-plan.md`, fasea solo por presupuesto de contexto y dilo explicitamente en `docs/roadmap.md` (faseado no alineado a sprints).

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
     docs:
       roadmap: docs/roadmap.md
       prompts: docs/prompts-roadmap-native-ai.md
     phases:
       - id: 1
         name: <nombre de la fase>
         objective: <objetivo en una linea>
         context_risk: bajo | medio | alto
         change_hint: <slug estable para `aisdd open change`>   # clave de union roadmap<->sprint<->Jira
         sprint: <id/nombre del sprint del sprint-plan.md, o vacio si no hay>   # solo si hay sprint-plan
         hus: [<HU-XX>, ...]        # HUs que cubre la fase (para enlazar con Jira/jira-sync.md)
         effort_human: <d-persona>  # esfuerzo agregado humano (si hay planificacion-proyecto)
         effort_ai: <d-persona>     # esfuerzo agregado con IA (si aplica)
       # ...una entrada por fase, en el mismo orden que docs/roadmap.md
   ```

   El `change_hint` es el **slug estable** que sirve de clave de union entre el roadmap, el sprint-plan y Jira; no lo cambies entre re-ejecuciones si la fase es la misma (para no romper el mapeo ni las sub-tareas ya creadas).

4. El numero de entradas de `phases` debe coincidir exactamente con las fases de `docs/roadmap.md`, en el mismo orden y con los mismos nombres.
5. Si ya existia una seccion `roadmap` de una ejecucion anterior, sustituyela integramente por la nueva (el roadmap mas reciente manda). No fusiones fases antiguas con nuevas.
6. Manten YAML valido: indentacion con espacios (no tabs), valores con caracteres especiales entre comillas, UTF-8 sin BOM.
7. Incluye `openspec/config.yaml` en los `output_files` de la entrada de auditoria de este comando, junto a `docs/roadmap.md` y `docs/prompts-roadmap-native-ai.md`.

### Criterios de particion para el roadmap

Usa estos criterios para dividir en mas fases cuando el modelo tenga menos capacidad:

- separar cambios por dominio funcional
- separar backend, frontend, datos e integraciones cuando no sea imprescindible tratarlos juntos
- separar preparacion tecnica de entrega funcional si la primera desbloquea varias fases
- separar migraciones, permisos, seguridad, observabilidad y rollout
- separar cambios con alto riesgo o validacion compleja

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

## `aisdd open change [what-you-want-to-build]`

> Alias: `native-ai open change [what-you-want-to-build]`.

Crea un cambio OpenSpec a partir del contexto del usuario, ejecutando una fase previa de pre-flight para resolver dudas antes de generar los specs.

1. Si el usuario aporta `<what-you-want-to-build>`, usalo literalmente como descripcion o identificador del cambio.
2. Si no lo aporta, deriva un identificador breve y estable desde el objetivo descrito por el usuario.
3. Ejecuta el **pre-flight de dudas para apertura** segun la seccion siguiente.
4. Cuando el pre-flight termine y no queden dudas bloqueantes pendientes, ejecuta:
   ```bash
   openspec new change <what-you-want-to-build>
   ```
5. Localiza los artefactos generados del cambio: `design.md`, `proposal.md` y ficheros `spec.md`. Alimentalos con las decisiones recogidas en el pre-flight (alcance, dominios, integraciones, modelo de datos, criterios de aceptacion).
6. Pasa esa documentacion al skill `booster-uml` para generar HTML con diagramas.
7. **Enlace con Jira (opcional)**: si la integracion con Jira esta activa (ver "Integracion con Jira (opcional)"):
   - Identifica la(s) **HU** que realiza este change a partir de `docs/roadmap.md`, `docs/mapa-historias-usuario.md` y `docs/jira-sync.md`. Si no es deducible con confianza, preguntalo (cuenta dentro del presupuesto de pre-flight).
   - Anota la(s) HU en `proposal.md` (p. ej. una linea "Historias: HU-03").
   - Lee `docs/jira-sync.md`; si la(s) HU ya tienen Story en Jira y el change **no** tiene aun sub-tarea, crea la **sub-tarea** bajo la Story de la HU principal (tipo `subtask_issue_type`), referenciando las HU secundarias en la descripcion. No la dupliques si ya existe.
   - Registra en `docs/jira-sync.md` la fila/celda con la clave de la sub-tarea y estado `to_do`. No muevas de columna aqui (eso es `implement`/`close`).
   - Si la HU no tiene Story todavia (aun no se volco el plan), no crees la sub-tarea: anota el change en el registro como pendiente de Story y avisa en el resumen.
8. Reporta el identificador del cambio, rutas creadas, decisiones del pre-flight grabadas en `openspec/changes/<change>/decisions.md`, ruta del HTML de diagramas si se genero y, si aplico, la sub-tarea de Jira creada y enlazada.

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
   - convenciones documentadas en el repo (`README.md`, `CLAUDE.md`, `AGENTS.md`, `docs/`, `config.yaml`).
   - elecciones triviales y facilmente reversibles (nombres internos, formato de log).
   - puntos ya cubiertos por specs OpenSpec previas o por cambios OpenSpec relacionados ya cerrados.
4. Presupuesto de preguntas: maximo `7` dudas por cambio. Si detectas mas, prioriza bloqueantes, agrupa relacionadas en una sola pregunta de varias opciones y descarta las de confirmacion de bajo impacto.
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
   - **Tipo**: bloqueante | preferencia | confirmacion
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
   - Localiza en `docs/jira-sync.md` la **sub-tarea** del change y su **Story** padre. Si el change no tiene sub-tarea (p. ej. se abrio sin Jira), creala ahora bajo su Story como en `open change`; si la HU no tiene Story, omite con aviso.
   - Resuelve el usuario asignado (cuenta del MCP o `assignee_override`) y mueve la **sub-tarea** y su **Story padre** a **In Progress** (descubriendo la transicion, sin hardcodear), asignando ambos al usuario resuelto.
   - Actualiza el estado en `docs/jira-sync.md` a `in_progress`.
8. Resume instrucciones aplicadas, ficheros afectados si OpenSpec los indica, decisiones grabadas en `decisions.md`, la transicion de Jira aplicada (claves de sub-tarea y Story, columna destino, asignado) si la hubo, y cualquier accion manual pendiente.

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
4. Presupuesto de preguntas: maximo `7` dudas por cambio. Si detectas mas, prioriza bloqueantes, agrupa relacionadas en una sola pregunta de varias opciones y descarta las de confirmacion de bajo impacto.
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
   - **Tipo**: bloqueante | preferencia | confirmacion
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

## `aisdd close change [what-you-want-to-build]`

> Alias: `native-ai close change [what-you-want-to-build]`.

Archiva un cambio OpenSpec.

1. Si llega `<what-you-want-to-build>`, usalo como cambio objetivo.
2. Si no llega, lista cambios abiertos.
3. Si solo hay un cambio abierto, usalo.
4. Si hay mas de uno, pregunta cual desea archivar.
5. Ejecuta:
   ```bash
   openspec archive <what-you-want-to-build>
   ```
6. **Transicion en Jira (opcional)**: si la integracion con Jira esta activa (ver "Integracion con Jira (opcional)"):
   - Localiza en `docs/jira-sync.md` la **sub-tarea** del change y su **Story** padre.
   - Mueve la **sub-tarea** a **Done** (descubriendo la transicion). Actualiza su estado en `docs/jira-sync.md` a `done`.
   - Consulta via el MCP las sub-tareas de la Story padre. Mueve la **Story a Done solo si TODAS sus sub-tareas estan Done**; si queda alguna abierta, deja la Story en In Progress e indica en el resumen que sigue pendiente (que changes faltan).
7. Verifica que el cambio queda archivado y resume el resultado, incluyendo (si aplico) la sub-tarea pasada a Done y si la Story padre se cerro o sigue pendiente.

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

### Modelo de datos en Jira (acordado)

- Cada **HU** es una **Story** (la crea `aidd sprint-planning`).
- Cada **change** es una **sub-tarea** de la Story de su HU.
- Una HU puede realizarse con varios changes -> varias sub-tareas bajo la misma Story. Si un change realiza varias HU, crea la sub-tarea bajo la HU principal y referencia las demas en la descripcion y en el registro.

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

### Registro de enlace (`docs/jira-sync.md`)

Fuente de verdad del mapeo HU <-> change <-> issue de Jira. Lo inicializa `aidd sprint-planning` (HU -> clave de Story) y lo completan los comandos de change (change -> clave de sub-tarea -> estado). Estructura en tabla:

| HU | Story (Jira) | change(s) | Sub-tarea(s) (Jira) | estado |
|----|--------------|-----------|---------------------|--------|
| HU-03 | ABC-12 | back-auth | ABC-45 | in_progress |

Regla de oro: **lee el registro antes de crear o transicionar nada y no dupliques**. Re-ejecutar un comando no debe crear sub-tareas repetidas ni revertir estados de forma incoherente.

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

- `open change`: crea la **sub-tarea** del change bajo la Story de su(s) HU (si no existe ya) y registra el enlace en `docs/jira-sync.md`.
- `implement change`: al arrancar la implementacion, mueve la sub-tarea **y su Story padre** a **In Progress** y asigna al usuario resuelto.
- `close change`: mueve la sub-tarea a **Done**; mueve la Story padre a **Done solo si todas sus sub-tareas estan Done**.

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
      "type": "bloqueante | preferencia | confirmacion",
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
- `decisions`: solo para comandos que recogen decisiones humanas (hoy: `implement change`). En el resto, lista vacia.
- `model` y `platform`: si no puedes resolverlos con fiabilidad, usa `"desconocido"`. No inventes valores.
- `user`: si la plataforma expone email del usuario, registra el email; si no, `null`. No registres datos personales adicionales.
- `prompt_version`: usa la version del skill seguida del slug del comando. Ejemplos: `1.4.0:implement-change/preflight`, `1.4.0:open-change/preflight`, `1.4.0:roadmap`, `1.4.0:close-change`, `1.4.0:init`, `1.4.0:prototype-ux`, `1.4.0:uml`.

### Calculo de hashes

- En PowerShell: `Get-FileHash -Algorithm SHA256 <path>`.
- En Bash o entornos POSIX: `sha256sum <path>` o `shasum -a 256 <path>`.
- Para el hash agregado (`input_hash`, `output_hash`), calcula el SHA-256 del string formado por las parejas `<path>\n<sha256>\n` concatenadas en orden alfabetico ascendente por `path`. Usa rutas relativas a la raiz del proyecto con separador `/`.

### Cuando escribir la entrada

- Escribe la entrada **al final** del comando, justo antes del resumen de verificacion.
- Una sola entrada por invocacion de comando.
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
