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
| F-06 | Enrutado del Outcome Validator: elevación por consenso | aisdd | **implementada** | 2026-08-26 |
| F-07 | Partir `aisdd-specs/SKILL.md` en `references/*.md` | aisdd | **implementada** | 2026-08-26 |
| F-08 | Versión global + CI de release y validación | marketplace | **implementada** | 2026-08-26 |
| F-09 | Plugin `aiba` y skill de Diseño Funcional (DF en Word) | aiba | **implementada** | 2026-08-27 |
| F-10 | Mover la capa de entrega y medición de `aidd` a `aiba` | aiba, aidd | **implementada** | 2026-08-27 |
| F-11 | Pre-flight de optimización del faseado: compara caminos, calcula el óptimo y re-estrategia sobre proyecto en marcha | aisdd | **implementada** | 2026-08-28 |
| F-12 | Encadenado de `aisdd`: cada comando sugiere el próximo paso resuelto, incluido el empalme con la capa de entrega de AIBA | aisdd | **implementada** | 2026-08-28 |
| F-13 | CI de rutas de skills y de contratos documentación↔script | marketplace | **implementada** | 2026-08-29 |
| F-14 | `aiba test-plan`: plan de pruebas por historia (inventario + evidencias) | aiba | **implementada** | 2026-08-31 |
| F-15 | `aiba status-report`: informe de situación con avance medido por trabajo ejecutado | aiba | **implementada** | 2026-08-31 |
| F-16 | Auditoría por escritor: un fichero por dev, para que el registro no conflicte en cada merge | aisdd, aiba | **implementada** | 2026-08-31 |
| F-17 | Tiempos en la auditoría: `started_at`, `attempt` y pre-flight, sin depender del hook | aisdd, aiba | **implementada** | 2026-08-31 |
| F-18 | `verification` en la auditoría y lead time en días laborables | aisdd, aiba | **implementada** | 2026-08-31 |
| F-19 | `aiba metrics`: la comparación se llama calibración, y suma la autoría real de AIAD | aiba | **implementada** | 2026-08-31 |
| F-20 | Producto en varios repositorios: cada repo autónomo con su `openspec/`, un lane por repo, KPI agregados | aidd, aisdd, aiba | **implementada** | 2026-08-31 |
| F-21 | Esfuerzo humano del worklog de Jira, y desviaciones atribuidas a la auditoría | aiba | **implementada** | 2026-09-01 |
| F-22 | Tres topologías de documentación, preguntadas y no deducidas | aidd, aisdd, aiba | **implementada** | 2026-09-01 |
| F-23 | La migración de topología la ejecuta el skill, no el humano | aisdd | **implementada** | 2026-09-02 |
| F-24 | El diseño llega hasta la HU: `implement` lee la guía de estilos, y el plugin `aifg` trae Figma nodo a nodo | aisdd, aidd, aifg | **implementada** | 2026-09-03 |
| F-25 | El hook de actividad, endurecido para otras plataformas: `turn_id`, detección de escritura sin lista blanca y prueba de paridad | todos | **parcial** | 2026-09-03 |
| F-26 | Los scripts se resuelven en vez de asumir la ruta: la auditoría vuelve a funcionar fuera de Claude Code | todos | **implementada** | 2026-09-03 |

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

Incluye: `aisdd lane [list|switch|status]`, guard de un change por lane, nivel 4 de corrección (contrato compartido → parada coordinada), `depends_on` en los tres modos, bloque de paralelismo en `AGENTS.md`, dimensionado por tramos en `aiba sprint-planning`, y chips/KPIs en `booster-docs`.

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

**Estado:** implementada · **Resuelta con un modelo propio**, ni el nuestro anterior ni el de upstream

Divergencia con `native-ai-specs` v1.6.0 (su decisión 008), no una carencia:

- **Nuestro modelo:** el Outcome Validator reporta al **AI Lead**.
- **El suyo:** reporta **siempre al AI Developer**, que corrige o eleva al Lead, que a su vez evalúa elevar al Architect.

Su argumento: un único canal de entrada de fallos simplifica la comunicación y mantiene al Developer como dueño de su entrega.

**Lo que se decidió.** Ninguna de las dos. La discusión era quién hace el diagnóstico, y la respuesta es que lo hagan **juntos**: cada uno tiene la mitad de la información —el Validator ha visto fallar el criterio, el Developer sabe por qué el código hace lo que hace—.

- Se **retira** del AI Developer la restricción «no habla con el Lead directamente». Su intención era proteger el contexto acotado del Developer, no establecer una cadena de mando, pero redactada así funcionaba como jerarquía en una organización que no la tiene.
- La **elevación al Lead se acuerda** entre Validator y Developer, para que ninguno se entere después de una decisión que le afecta.
- **Si no hay acuerdo, se eleva igual** con las dos posturas registradas. Sin esa regla el change se queda parado esperando a que alguien ceda, y el desacuerdo entre quien definió la validación y quien escribió el código es justo lo que el Lead necesita saber.
- El consenso aplica **solo a cruzar hacia el Lead**, no al ciclo normal: un bug de implementación se devuelve al Developer y se arregla sin ceremonia.
- La elevación **deja rastro** en el `decisions.md` del change, para que «nada a espaldas de nadie» sea comprobable y no una norma social.

Es la misma idea que el nivel 4 de corrección (contrato compartido): ninguna decisión que afecte a otro se toma sin que ese otro se entere.

## F-07 — Partir `aisdd-specs/SKILL.md` en `references/*.md`

**Estado:** implementada · **Versión:** `aisdd` 2.0.0 · **Origen:** estructura de `native-ai-specs` v1.6.0

El `SKILL.md` supera las 1.200 líneas y se carga entero aunque el 90% no aplique al comando en curso. Upstream lo tiene partido en un fichero por comando (`roadmap.md`, `open-change.md`, `preflight.md`…).

Sin cambio funcional. **Debe ir la última y en solitario**: mueve todo el fichero, así que cualquier rama viva en paralelo se vuelve irreconciliable.

## F-08 — Versión global, release automático y validación en CI

**Estado:** implementada · **Versión:** marketplace 1.6.0 · **Añadida:** 2026-08-26

Versión global en `VERSION` (la raíz), independiente de las de cada plugin: agrupa un conjunto de cambios en algo publicable. **Arranca en `1.6.0`**, continuando la numeración de `native-ai-specs` v1.6.0, del que este marketplace es la continuación: empezar en 1.0.0 habría sugerido que es un producto distinto y más joven de lo que es. `release.yml` la lee al mergear a `main` y publica si la etiqueta `v<VERSION>` no existe todavía — la puerta es la etiqueta y no la rama, así que es idempotente.

Las notas empiezan por las tablas de qué plugins y skills cambian de versión, que es lo único que necesita saber quien consume el marketplace.

`validate.yml` cubre el punto débil de una versión manual (olvidar subirla) y cuatro comprobaciones de coherencia que hasta ahora se hacían a mano en cada PR: manifiestos, frontmatter de skills, HTML de metodología regenerado y sincronizado entre copias, compilación de los scripts y ausencia de mojibake.

> Ampliada después. La batería creció con la autosuficiencia de plugins, el sentido contenido→versión y las dos comprobaciones de **F-13**; el orden de las notas también cambió. El estado actual está en el README, no aquí: esta sección registra lo que entregó F-08.

Al escribirlo encontró dos desfases reales que llevaban tiempo sin detectarse: `booster-uml` no tenía `metadata.version`, y el HTML de la metodología AIAD se había quedado atrás porque cambió el renderer y solo se regeneraban los de AIDD/AISDD.

## F-09 — Plugin `aiba` (AI Business Analyst) y el skill de Diseño Funcional

**Estado:** implementada · **Versión:** `aiba` 0.1.0 · **Añadida:** 2026-08-27

Primer plugin del conjunto **AIBA**, de análisis funcional. Contiene `aiba-functional-design`, que genera el **DF en Word de cada historia de usuario** a partir de `docs/detalle-historias-usuario.md`, con la estructura extraída de los DF de referencia.

Tres decisiones que conviene no perder:

- **Diseño genérico y pregunta previa.** El documento sale sin marca, y el comando pregunta antes si aplicar una —de carpeta local o URL— con «sin marca» como recomendada. Un DF acaba en manos de un cliente con su propia identidad; generarlo con la marca de quien lo escribe obliga a rehacerlo. Como el color va a los **estilos** de Word y no a cada párrafo, aplicar otra identidad después es cambiar el estilo.
- **No inventa: marca y contabiliza.** `[PENDIENTE: ...]` en el cuerpo, una fila por hueco en **Puntos abiertos**, y el número de puntos abiertos en el resumen como indicador de si el documento está listo. Un DF se firma y se desarrolla contra él, así que el relleno plausible es peor que el hueco.
- **Reedición no destructiva.** Regenera solo lo afectado, conserva el texto del analista y **añade** fila al control de versiones. Ese historial es la razón de ser de esa tabla.

`aiba` **consume** lo que produce AIDD sin modificarlo: lee `docs/` y escribe solo en `docs/df/`. Los skills que entonces quedaban pendientes de mover se movieron en **F-10**.

## F-10 — La capa de entrega y medición pasa de `aidd` a `aiba`

**Estado:** implementada · **Versión:** `aiba` 1.0.0, `aidd` 2.0.0 · **Añadida:** 2026-08-27

Cuatro skills se mueven: `hu-review-plan`, `project-plan`, `sprint-planning` y `metrics`. Sus comandos son ahora `aiba ...` y **no quedan alias `aidd ...`** — corte limpio, decidido a propósito.

**El criterio del corte** no es la fase sino el interlocutor. Lo que se mueve es lo que da la cara ante el negocio: el plan que aprueba, el calendario que sigue, la revisión con la que cierra las HU y los KPIs con los que juzga si mereció la pena. Lo que se queda en `aidd` es la definición y el diseño, cuyo interlocutor es producto y arquitectura.

**Lo que no cambia es el contrato de datos.** Los cuatro siguen leyendo y escribiendo los mismos ficheros de `docs/`, así que `aisdd roadmap` sigue alineándose con `docs/sprint-plan.md` exactamente igual. Solo cambia el prefijo del comando.

**AIBA estrena metodología propia** (`plugins/aiba/methodology/native-ai-aiba.md`) y la capa correspondiente se poda de la de AIDD, dejando punteros en su lugar en las dos copias: el rol de AI Delivery Manager, el paso 1.4 y la Fase 3.5 completa.

**La lección de la mecánica es que un plugin tiene que ser autosuficiente.** Claude Code los instala sueltos y no resuelve dependencias entre ellos, así que `stamp_doc.py` viaja duplicado en `aidd` y en `aiba`, y el hook de actividad en los cinco plugins — incluido `aiba`, que hasta ahora no lo traía pese a ser, con `aiba metrics`, su único consumidor. Un `git mv` rompe justo esto sin hacer ruido, así que ahora lo comprueba `check_plugin_assets.py`: toda referencia `${CLAUDE_PLUGIN_ROOT}/...` resuelve dentro de su plugin, y las copias replicadas son idénticas entre sí.

**Lo que no puede romperse es el histórico.** El registro de actividad guarda el nombre del skill que se ejecutó, así que `aiba metrics` conserva los nombres `aidd-*` como alias de etapa: sin ellos, toda la planificación anterior al traslado caería en «Otros» y falsearía el reparto planificación-vs-ejecución, que es justo la cifra por la que se lee el informe.

`aidd` sube a **2.0.0** porque pierde cuatro skills: es ruptura para quien los tuviera en uso, y las notas del release ahora lo dicen — `release_notes.py` enumera también los skills que **desaparecen** de donde estaban y a qué plugin han ido.

## F-13 — CI de rutas de skills y de contratos documentación↔script

**Estado:** implementada · **Versión:** marketplace 1.25.1 · **Añadida:** 2026-08-29 · **Origen:** auditoría de los 30 skills

La auditoría cerró con 34 hallazgos, y el último apareció en `aisdd-specs` —el skill más revisado del repo— en la última pasada de la última fase: doce rutas `.agents/skills/…` del empaquetado anterior al marketplace. No sobrevivieron por falta de revisión, sino porque **la sonda que las encuentra no se había escrito todavía**. Un arreglo se olvida; una comprobación no. Estas dos convierten en permanentes las dos últimas sondas de la auditoría.

**`check_skill_refs.py` — las rutas resuelven donde el skill las busca.** La carga es en diferido: `SKILL.md` es un índice y las reglas viven en `references/*.md`, que el agente lee solo cuando el índice se lo dice. Una ruta rota no da error —el agente no encuentra el fichero, sigue sin él, y la regla que contenía no se aplica—, que es la forma de fallo que más se parece a que todo funciona. Fija la convención: mismo skill → `references/x.md`; otro skill del mismo plugin → `${CLAUDE_PLUGIN_ROOT}/skills/<skill>/references/x.md`; otro plugin → **sin ruta**, porque el usuario puede no tenerlo instalado. Comprueba también el reverso —un `references/` que nadie enlaza no lo lee nadie— y que no reaparezcan las rutas del empaquetado anterior.

**`check_contracts.py` — lo documentado coincide con lo implementado.** Un skill y su script son productor y consumidor del mismo formato, escrito en dos sitios que nada ata. Contrasta cada invocación documentada contra el `argparse` real, en los tres sentidos —flag inventada, flag obligatoria omitida, posicional obligatorio omitido— y **por invocación, no sobre la unión**: que entre dos ejemplos estén todas las obligatorias no salva a ninguno de los dos. Cubre las dos fuentes: las invocaciones de los skills, que ejecuta el agente en casa del usuario, y las del README, que ejecuta quien mantiene esto —de una de ellas depende que los `.html` de metodología se regeneren, así que un flag renombrado ahí rompe otra comprobación de la CI. Y comprueba que cada documento con vista HTML tenga entrada en `DOC_TYPES` de `booster-docs`, porque el que no la tiene no falla: sale con la etiqueta y el dashboard genéricos, que es una vista peor sin que nadie lo note. Le pasó a `kpis-ia`.

**Encontrado al ponerlas:** diez referencias colgando en `aisdd-amend` y `aiba-sprint-planning` (una de ellas cruzando a otro plugin, que puede no estar instalado) el sellado de `aiba-metrics`, que apuntaba a un `scripts/stamp_doc.py` inexistente y además se daba permiso para saltárselo —así que `docs/kpis-ia.md` no se sellaba nunca— y un comando de ejemplo de `aiba-functional-design` con ruta relativa, que falla en cuanto alguien lo copia.

## F-14 — `aiba test-plan`: el plan de pruebas de cada historia

**Estado:** implementada · **Versión:** `aiba` 1.3.0 · **Añadida:** 2026-08-31 · **Origen:** plantillas y ejemplos de un proyecto real

Sexto skill de AIBA, en la línea del Diseño Funcional: entregables genéricos y sin marca, con la identidad visual como pregunta del pre-flight, sobre todas las HU o sobre una.

**Dos ficheros por historia, generados del mismo manifiesto** para que no puedan describir cosas distintas. Un `.xlsx` con seis hojas —Hoja de Control, Especificaciones con las diecisiete columnas de la plantilla de referencia, Parámetros de nomenclatura, rejilla de Ejecución, exportación a Qmetry y Resumen con fórmulas vivas— y un `.docx` de evidencias con un bloque por caso y el hueco de la captura.

**Genera el plan; no ejecuta las pruebas.** Corre en tiempo de diseño, cuando el código puede no existir. Quien ejecuta ya está en la metodología: el **Outcome Validator** al cerrar un change, el humano con `aiad test` sobre los casos automatizables, o un tester con estos dos ficheros. Lo que el skill deja preparado para el día que alguien recoja resultados de vuelta son dos datos por caso —su código estable y el change al que pertenece—, no una arquitectura.

**Un solo nivel, `PS.FU`.** Los criterios de aceptación de una historia son pruebas funcionales de sistema. Derivar unitarias o de integración desde una historia sería inventar: las escribe quien conoce el código.

**Sin macros.** La plantilla de referencia es un `.xlsm` cuyos dos botones generan los códigos concatenando columnas y montan la hoja de ejecución. Existen porque un humano teclea el inventario a mano; aquí sale hecho al construir el fichero, y el `.xlsx` limpio además no dispara el aviso de seguridad. Lo que sí se conserva son sus reglas: correlativo por prefijo, colapso de tramos vacíos y aviso de duplicado.

**`scripts/branding.py` sube a nivel de plugin**, junto a `stamp_doc.py` y por la misma razón: la marca corporativa la aplican ahora dos skills en dos formatos, y una copia por skill se queda atrás sin que nada falle. `gen_df_docx.py` pasa a usarlo, con la salida verificada idéntica en los dos caminos —con marca y sin ella—.

**Dos modos nuevos, porque el skill afirmaba cosas que no podía cumplir.** `--comprobar` responde si un plan o un documento de evidencias ya existentes se pueden regenerar sin perder resultados anotados ni capturas pegadas: la regla «nunca pises trabajo ejecutado» necesitaba un dato que solo está dentro del `.xlsx`, y sin leerlo era una regla escrita. Y `gen_df_docx.py --extraer` vuelca un DF a JSON con sus secciones y tablas: sin él, «el DF es la mejor fuente de casos» era decorativo, porque un `.docx` no se lee de un vistazo. Verificado sobre los DF reales del cliente.

**Pendiente, como decisión aparte:** que `aisdd close change` lea el inventario y exija los casos ejecutados. Cerraría el círculo —la validación dejaría de ser «el Validator dice que sí» y pasaría a ser «estos 26 casos están en verde»— pero toca otro plugin, cambia la puerta de archivado y es una decisión de proceso.

## F-15 — `aiba status-report`: el informe de situación del proyecto

**Estado:** implementada · **Versión:** `aiba` 1.4.0 · **Añadida:** 2026-08-31 · **Origen:** un informe real del equipo, tomado como referencia de contenido y layout

Séptimo skill de AIBA. Responde a la pregunta que se hace en cada comité —*dónde estamos, vamos bien, y qué hacemos ahora*— con cifras que se pueden defender.

**El avance se mide por trabajo ejecutado, no por fechas.** Es lo que separa este informe de un Gantt coloreado a mano. Una fase cuenta como entregada cuando su change está archivado —el mismo criterio que usa `aisdd roadmap` al re-fasear— y **cada fase pesa sus días de esfuerzo**: `effort_ai` si el plan de recursos lo calculó, si no la suma de las tallas de sus HU. Cerrar una fase L vale más que cerrar una XS, y un porcentaje por número de fases lo escondería.

**Tres estados y dos métricas.** Cerrado, activo y pendiente: un change abierto no está ni entregado ni sin empezar, y meterlo en cualquiera de los dos lados miente en la dirección que le convenga a quien presenta. Y *changes* como métrica principal —la unidad que se abre y se cierra— con *HU* como secundaria —lo que el negocio reconoce—; si divergen mucho, eso ya es un hallazgo.

**Los bloqueos son medidos, no declarados**: decisiones marcadas como bloqueantes en el pre-flight de un change y todavía sin resolver en `openspec/audit/`. Y el informe cruza esa lista con el camino crítico, porque un bloqueo que está en la cadena más larga es un día de calendario, no de holgura.

**Los números los calcula un script y la narrativa la escribe el skill.** Esa separación es la que impide que el resumen cualitativo diga una cosa y la barra de progreso otra. Encima de ella, una regla dura: **nada se inventa**. Cada cifra declara el documento del que sale, y lo que no se puede derivar sale como hueco en ámbar con el documento que lo llenaría — una cifra plausible sin fuente es peor que un hueco, porque el hueco se ve.

**`docs/estado-proyecto.json` se versiona a propósito.** Es el registro y es la fuente del HTML, así que no pueden divergir; y convierte el informe en una serie en vez de una foto. Un bloqueo que aparece en dos informes seguidos no es el mismo bloqueo: es un problema de gobierno.

**Encontrado al construirlo:** el extractor de tallas leía `XS` como `S` y `XL` como `L` —`\D` es codicioso y se comía la `X`—, así que el esfuerzo total salía corto en todas las fases a la vez y en silencio. Es la misma trampa que ya apareció en el renderizador de `booster-docs` durante la auditoría.

`EFFORT_DAYS` pasa a estar replicada en cuatro scripts, y la cuarta copia entra en la vigilancia de `check_plugin_assets.py`.

**Del repaso salieron tres cosas mas.** La primera es la que hunde un informe: la barra de avance se pintaba **por número de fases** mientras el titular daba **esfuerzo**, así que la misma pantalla mostraba 35,2 % arriba y 42,9 % justo debajo. Ahora las dos van por esfuerzo, y cuando difieren el informe lo explica en vez de esconderlo — que las fases cerradas sean más pequeñas que la media es información, no ruido.

La segunda: los sprints se emparejaban comparando el texto completo, así que la cabecera habitual —`## Sprint 1 — Funnel de cotización`— no casaba con el `sprint: Sprint 1` de `config.yaml` y el avance previsto salía vacío sin explicar por qué. Se emparejan por su número.

Y `--anterior`, que compara con el informe previo y saca el dato que no se ve mirando solo el de hoy: **los bloqueos que repiten**. Uno que aparece en dos informes seguidos ya no es un bloqueo, es un problema de gobierno, y se resuelve escalándolo.

## F-16 — La auditoría deja de conflictar en cada merge

**Estado:** implementada · **Versión:** `aisdd` 3.2.0, `aiba` 1.4.1 · **Añadida:** 2026-08-31

El registro de auditoría es append-only y cada comando añade una línea **al final** de `openspec/audit/YYYY-MM.jsonl`. Con un fichero compartido, dos developers que parten de la misma base tocan la misma región y el merge conflicta. No es un caso raro —pasa en cada merge, porque cada comando escribe— y es justo el escenario que `multilane` fabrica a propósito. La especificación no decía nada de concurrencia.

**Un fichero por escritor:** `openspec/audit/YYYY-MM/<quien>.jsonl`. Dos devs no tocan nunca el mismo fichero, así que el conflicto **deja de ser posible** en vez de tener que resolverse. `<quien>` sale de la identidad de git —el `user` de la entrada, su correo si viene entre ángulos, `git config user.email`, y `desconocido`— porque lo que se evita es un conflicto *de git* y esa identidad es exactamente lo que distingue a los escritores ahí.

**Y `merge=union` como red**, que `aisdd init` deja en el `.gitattributes` del proyecto igual que ya hacía con `.gitignore` para `openspec/.lane`. Cubre el caso que queda: la misma persona en dos ramas. Union puede repetir una línea al concatenar los dos lados, así que **los dos lectores deduplican por `id`** — es único por diseño.

**No hay migración.** La disposición anterior sigue siendo válida y los lectores miran las dos; las entradas nuevas van a la nueva y conviven. La purga también: el mes lo lleva el directorio en una y el nombre del fichero en la otra, y un directorio de mes se borra con su último fichero.

Es prerrequisito del cambio de esquema de la auditoría —`started_at`, `attempt`, `preflight{}`— que viene después: añadir campos a un fichero que conflicta en cada merge no es progreso.

## F-17 — La auditoría empieza a medir el tiempo

**Estado:** implementada · **Versión:** `aisdd` 3.3.0, `aiba` 1.5.0 · **Añadida:** 2026-08-31

Hasta ahora la entrada solo tenía una marca —el final—, así que **la duración de un comando no existía**. Lo único calculable era el hueco hasta la entrada anterior, que mide la reunión de por medio y no el trabajo: un comando que empieza a las 18:50 y acaba a las 09:10 duró minutos, no catorce horas.

**`started_at`** lo arregla, y lo hace sin depender de ningún hook: funciona igual en Codex. De ahí salen el tiempo atendido, el ratio atención/calendario y el coste de la duda.

**Lo que el script puede calcular no se le pide al modelo.** Es la decisión de diseño que separa esto de la propuesta original:

- **`attempt`** lo cuenta el script leyendo el propio registro. Un reintento es justo la situación en la que el agente ha perdido el hilo, así que pedirle que recuerde que va por la tercera sería pedir el dato cuando menos fiable es.
- **`preflight`** deriva cuatro de sus cinco números de `decisions[]` —cuántas hubo, quién las resolvió y cuántas eran bloqueantes ya están ahí—. Un recuento tecleado aparte puede contradecir a la lista de la que sale, y entonces no se sabe a cuál creer. Solo `rounds` lo aporta el agente, porque no deja rastro: y es el número que más dice, porque cinco preguntas de golpe son un pre-flight y tres rondas de dos son que no se captó el problema a la primera.
- **`turns` e `interventions`** van en un bloque `self_reported` aparte, precisamente porque no se pueden contrastar contra ningún artefacto. Útiles como contexto; ningún KPI debe depender solo de ellos.

**Y el dato ya sirve para algo.** `aiba status-report` gana el **ratio atención/calendario**: de todo el tiempo que un change estuvo abierto, cuánto se trabajó en él. Por debajo del 15 % el problema no es de capacidad —los changes están esperando, no avanzando— y meter más gente no arregla una espera. El informe lo cruza con la lista de bloqueos para nombrar a qué esperan.

Los campos son aditivos: las entradas anteriores siguen siendo válidas y los KPIs que dependen de los nuevos declaran desde qué versión miden.

**Pendiente de esta línea:** `verification` —quién registra build y tests, que es el cambio de comportamiento real—, el calendario laborable para el lead time, y retirar de `aiba metrics` la comparación humano-vs-máquina, que era medido contra estimado disfrazado de comparación: `human_share` solo cuando existe `docs/aiad-journal.md`, y si no, la sección desaparece.

## F-18 — La verificación deja rastro, y el lead time cuenta días laborables

**Estado:** implementada · **Versión:** `aisdd` 3.4.0, `aiba` 1.6.0 · **Añadida:** 2026-08-31

Cierra la parte aditiva de la línea de medición que abrió F-17.

**`verification`.** `aisdd implement change` y `aisdd amend change` ya ejecutaban build y tests, y **no registraban el resultado en ningún sitio**. Ahora lo dejan en la entrada: `{build, tests_run, passed, failed, added, modified, gates[]}`, donde `gates[]` es el enganche natural de Spotless, ArchUnit, Kiuwan o los linters del proyecto. Era el cambio de comportamiento más grande de la propuesta y resultó ser el más barato: el dato ya existía, solo se perdía.

**`first_run_green` lo deriva el script**, de que sea el primer `attempt`, de que algo se haya ejecutado de verdad y de que no falle nada. Es el mejor indicador de si las specs iban bien —mejor que contar correcciones, que llegan después y ya con el problema encima— y por eso no puede depender de que el agente se acuerde de marcarlo. Como `attempt` también lo cuenta el script, tampoco se puede maquillar reintentando y volviendo a declarar verde.

Un bloque ausente es `null`, no un bloque a ceros: un cero se leería como cero fallos.

**El calendario laborable** va en `calendar: {workweek, holidays[], timezone}` dentro de la sección `roadmap` de `openspec/config.yaml`, y lo escribe **`aiba project-plan`** — el calendario del equipo es un recurso, como los perfiles y la capacidad, y ese es el skill que los declara. `aiba status-report` da ahora el lead time en días naturales **y** laborables.

No se adivina: cambia por país, por cliente y por convenio. Sin la sección, el informe asume lunes a viernes sin festivos **y lo declara** — un lead time laborable sobre un calendario supuesto que nadie ha visto es peor que el natural, porque parece más preciso.

**Queda de la línea:** retirar de `aiba metrics` la comparación humano-vs-máquina. Es una resta sobre una capacidad publicada, así que va en su propia PR.

## F-19 — Calibración en vez de ahorro, y la autoría real cuando la hay

**Estado:** implementada · **Versión:** `aiba` 1.7.0 · **Añadida:** 2026-08-31

Se propuso **retirar** de `aiba metrics` la comparación humano-vs-máquina, por comparar contra un contrafáctico. Al revisarlo, el diseño ya era más cuidadoso de lo que la crítica suponía: la cifra **solo** sale si el equipo declara su esfuerzo real con `--real-days`, la sección se llamaba ya «Contraste con el baseline humano», y hay un guardarraíl que marca como no publicable cualquier relación mayor de x10.

**El problema estaba en tres palabras, y en las filas de la tabla, no en el título.** Decían `Ahorro absoluto`, `Factor de aceleración` y `Ahorro estimado (X por jornada)` — resultados conseguidos. El título decía «contraste» y las filas se leían como un logro, y la fila que más viaja es la del dinero, porque acaba en una diapositiva sin la sección que la enmarca.

Ahora dicen lo que el número **es**: `Diferencia entre ambos`, `Desviación de la estimación`, `Relación baseline / real`, `Esa diferencia valorada a X por jornada`. El cálculo no cambia; cambia cómo se nombra. Y la tabla lleva debajo qué es y qué no es: una calibración para afinar la próxima estimación, no una medida de ahorro, porque el escenario sin IA no se ejecutó.

**Y se suma lo que la propuesta sí tenía bien**, que era un añadido y no un reemplazo: cuando existe `docs/aiad-journal.md`, el informe trae la **autoría real**. Es el único dato de autoría que no es una estimación — una línea por pieza de trabajo, anotada en el momento— y separa las dos calidades que lleva dentro: las entradas `ai-edit` las captura el hook al ver a la IA tocar un fichero, y el resto las declara el humano.

Sin bitácora, **la sección no aparece**: no sale un cero ni un «no disponible». Un proyecto que no lleva bitácora no tiene un reparto de autoría del 0 %, simplemente no lo ha medido.

## F-20 — Un producto en varios repositorios

**Estado:** implementada · **Versión:** `aidd` 2.4.0, `aisdd` 3.5.0, `aiba` 1.8.0 · **Añadida:** 2026-08-31

Todo el diseño asumía «la raíz del proyecto» = un directorio con `docs/` y `openspec/`. Un producto repartido en tres repos no tenía sitio.

**La forma descartada, y por qué.** El primer diseño puso un repo de gobierno en la raíz con `docs/` y **un solo** `openspec/`, y los repos de código como directorios hermanos. Es más elegante sobre el papel —un roadmap, una auditoría, un informe— y no sobrevive al contexto real: en cliente los repos vienen dados, uno por parte del proyecto, y **un cuarto repo que no contiene código no se justifica ante nadie**. Se evaluaron también los submódulos, que resuelven el anclaje de SHA y el layout del workspace pero cobran su precio en HEAD desacoplado y conflictos de puntero, y son buenos fijando y malos desarrollando en paralelo, que es justo lo que aquí se hace todos los días.

**La forma adoptada: nada en el centro.** Cada repo es autónomo — su propio `openspec/` y su propia copia completa de `docs/`. No hay repo padre, no hay submódulos y no hay nada que clonar de forma especial. Los KPI globales se sacan **fuera**, desde la carpeta que contiene los repos, que no necesita ser un repo.

**Declarar varios repos en `docs/arquitectura-base.md` §3 obliga al modo `multilane` con un lane por repo.** No se pregunta en el pre-flight y no se ejecuta el pre-flight de optimización: no hay caminos que comparar cuando la frontera de despliegue ya partió el trabajo. Con un solo repo no se fuerza nada.

**Fuera de multirepo un repo sigue sin ser un lane** — el repo es una frontera de despliegue, el lane una línea de trabajo—, pero en multirepo son lo mismo por decisión, y de ahí sale todo lo demás:

| | Consecuencia |
|---|---|
| Independencia | **No se verifica: es estructural.** Un change no puede salirse de su lane porque no puede salirse de su repo. |
| Entrega | **Un change, una PR.** El roadmap dice la verdad en el momento en que lo dice. |
| Lane activo | **Lo dice el directorio.** `openspec/.lane` no se usa y `aisdd lane switch` se rechaza: se cambia de lane cambiando de repo. |
| Barreras | **No hay.** `F0` y `FB-NN` serializan superficie compartida, y aquí no la hay. |
| Auditoría | Cada repo la suya, y dentro un fichero por escritor. |

**La apuesta, dicha en voz alta:** que los repos son de verdad independientes en código. Lo que compartan viaja como **artefacto versionado** —un contrato OpenAPI publicado, un paquete, un esquema de eventos— y cada repo consume la versión que elige, cuando la elige. Publicar la versión nueva de un contrato es una fase del lane que publica; adoptarla es otra fase del que consume, y ninguna para a nadie. Un repo que necesita el fuente de otro no se arregla faseando: es una frontera mal puesta, y se registra como riesgo en la sección 13 de la arquitectura.

**Un `depends_on` que cruza repos avisa, no bloquea.** No se puede comprobar —esa fase se archiva en un `openspec/` que no está aquí— y bloquear con lo que no se puede ver sería bloquear a ciegas.

**El coste conocido:** `docs/` va copiado entero en cada repo, y un cambio en cualquiera hay que replicarlo en todos. `aisdd init` lo dice explícitamente en su resumen, porque no se descubre solo.

**El faseado se decide una vez.** `aisdd roadmap` gana un tercer camino, **Adoptar**, junto a Anotar y Re-fasear: se fasea en el repo que tiene los documentos de diseño, el humano copia `docs/` a los demás —el comando no puede, no ve esos repos— y en cada uno se adopta: leer el documento, derivar sus fases al `config.yaml`, y no re-fasear, no preguntar, no correr el optimizador, no tocar `docs/`. Ejecutarlo entero en los tres daría tres roadmaps distintos del mismo proyecto y mandaría el del último que lo corriera.

**Pasar de un repo a varios es una migración, no un cambio de estrategia.** El `openspec/` anterior se copia **entero** a cada repo nuevo, para que ninguno arranque como si el proyecto empezara hoy. Eso deja los changes ya cerrados **duplicados en los N repos, a propósito** — y es exactamente el dato que rompe un informe si nadie lo sabe.

La marca que los distingue es que **las fases anteriores a la migración no tienen `lane`**: se fasearon cuando no había repos. `compute_status.py` las aparta en un bloque `heredado` y las suma **una sola vez**. Sobre un caso de tres repos con 22 días heredados, la diferencia es **44 días y 59,1 %** frente a **88 días y 79,5 %**: contarlas por repo inflaba el avance veinte puntos. El HTML lo explica, porque la primera pregunta del comité es por qué la suma de las columnas no da el total. Y las HU se deduplican **por id**, no restando: una HU puede estar legítimamente en dos repos.

**El lane se infiere, y si no está claro se pregunta.** No hay `switch` que hacer: `roadmap.repo` primero, y si falta, el nombre del directorio contra los `lane-id`. Una coincidencia, se usa y se dice; ninguna o varias, **se pregunta**. Nunca por descarte ni por parecido — trabajar con el lane equivocado abre changes de otro repo y no se nota hasta mucho después. El script hace lo mismo salvo preguntar, que no puede: infiere si hay una sola coincidencia y avisa si no.

**Convertir a lanes intenta no tocar el sprint-plan.** Lo que lo sostiene es conservar el `change_hint`, que es la clave con la que `sprint-plan.md` y Jira se enganchan: con él intacto, **renombrar una fase a `F-<lane>-NN` no rompe nada**. Solo lo rompen partir una fase pendiente entre dos lanes —nacen `change_hint` nuevos que no están en ningún sprint— y reordenar pendientes de forma que cambien de sprint. En ninguno de los dos se reescribe el sprint-plan: se registra el conflicto y se dice que re-ejecutar `aiba sprint-planning` es seguro. Re-empaquetar sprints es del negocio, no del faseado.

**Los repos se declaran solo con el nombre.** Ni URL de remote ni ruta local: no las necesita nadie —ningún comando salta de un repo a otro— y son lo primero que caduca cuando el cliente migra de organización. `aisdd init` identifica el repo por su nombre y, si no está claro, **pregunta**: elegir mal el `repo` hace que ese `openspec/` ejecute las fases de otro lane, y el error no se ve hasta que alguien abre un change que no le tocaba.

**Y los KPI globales, que es donde estaba el trabajo de verdad.** `compute_status.py --root` pasa a ser repetible. Dos cosas que parecían detalles y no lo son:

- **Cada repo lleva el roadmap completo pero solo ejecuta las fases de su lane**, así que el informe de un repo filtra por su `roadmap.repo`. Sin ese filtro se quedaría clavado en un tercio para siempre, y no por ir retrasado.
- **Se suman días de esfuerzo, no porcentajes.** La media de tres porcentajes le da el mismo peso a un repo de 40 días que a uno de 4. El HTML añade «Avance por repositorio» con la columna **Peso**, que es la que distingue tres repos al 27 % de dos acabados con uno sin empezar. Los caminos críticos se dan por repo y **no se suman**: son cadenas paralelas, y el del proyecto es el más largo.

## F-21 — El esfuerzo humano real, y por qué se desvió cada change

**Estado:** implementada · **Versión:** `aiba` 1.9.0 · **Añadida:** 2026-09-01 · **Issue:** #26

Dos cosas que iban juntas porque comparten fuente y destino.

### El único número que se tecleaba

`compute_kpis.py` calibra un baseline de tallas contra el esfuerzo real, y ese esfuerzo real era el único dato del informe que alguien escribía a mano con `--real-days`. No por descuido: el tiempo atendido mide solo los turnos —no ver al humano leer, revisar, teclear a mano ni reunirse— y restarlo del baseline da aceleraciones de x100.

Pero el dato existe: **está imputado en Jira**. Ahora sale de ahí.

**Se accede por MCP, y la regla de `jira.md` no se toca**: nada de REST manual ni de gestionar credenciales. Eso tiene una consecuencia que decide el diseño — **el script no puede llamar al MCP**, porque es Python sin dependencias de red y las tools viven en el modelo. Así que el skill consulta el worklog siguiendo el mapa HU → Story → change de `docs/jira-sync.md`, lo deja en un JSON, y el script lo suma. El script sigue siendo puro.

**Y no se pasa un total, se pasa el desglose por issue.** Un worklog al 50 % da la mitad de horas, la mitad de horas da el doble de relación baseline/real, y esa es la cifra que más viaja sola a una diapositiva. Con el desglose, el informe declara la **cobertura** pegada al número:

> **Cobertura del worklog: 50 %.** 2 issues del alcance no tienen horas imputadas. El esfuerzo real sale corto en esa proporción, así que la relación baseline/real sale **alta por defecto de imputación, no por rendimiento**.

El worklog manda sobre `--real-days`, y si vienen los dos y no coinciden **lo dice** en vez de elegir en silencio entre dos números distintos.

### Por qué se desvió cada change

El informe ya sabía cuánto duró cada change. Lo que faltaba era **por qué**, y sin eso «vamos tres días tarde» no dice si hay que contratar, desbloquear o rehacer specs — tres decisiones distintas.

La auditoría ya tenía la materia prima. `atribucion` cruza el lead time en **días laborables** contra el esfuerzo estimado de la fase y adjunta la señal que lo explica: ratio de atención, bloqueos sin resolver, reintentos, `first_run_green`, correcciones e intervenciones.

Dos reglas la sostienen:

- **Nada se inventa.** Un change desviado sin señal registrada se declara como **hueco**, no recibe la causa más plausible. Una causa inventada es peor que un hueco porque se actúa sobre ella.
- **Los adelantos se explican igual que los retrasos.** Es lo único del informe que dice **qué hay que repetir**, y mirando solo los rojos solo se aprende de lo que sale mal.

El umbral es el ±25 %: un change de 3 días que tarda 3,5 no es un hallazgo, y marcarlo llenaría el informe de falsos positivos.

## F-22 — Dónde vive `openspec/` es una pregunta, no una deducción

**Estado:** implementada · **Versión:** `aidd` 2.5.0, `aisdd` 3.6.0, `aiba` 1.9.0 · **Añadida:** 2026-09-01

F-20 asumió que varios repos implican un `openspec/` por repo. Es una de las formas de trabajar, no la única, y el número de repos no la determina.

Hay ahora una decisión anterior al modo de faseado —la **topología**, en `roadmap.topology`— y **la pregunta `aisdd init`**, que es quien crea `openspec/` y por tanto quien decide dónde vive. `aisdd roadmap` la lee; cambiarla desde ahí es una migración, no un ajuste.

| Topología | Repos de código | Dónde viven `openspec/` y `docs/` |
|---|---|---|
| **`mono`** | 1 | En el propio repo |
| **`fraccionado`** | N | Uno **por repo**, cada uno con su copia de `docs/` |
| **`externalizado`** | **1 o N** | En un **repositorio git aparte** que gobierna a los de código |

**`externalizado` no depende de cuántos repos de código haya.** Un proyecto de un solo repo también puede tener su `openspec/` fuera, y ese es el caso que más veces la motiva: cuando los artefactos de especificación **no pueden estar en el repo de código** — por política del cliente, por contrato, o porque ese repo es un entregable y estos son documentos de trabajo internos.

**Y tiene que ser un repo git, no una carpeta compartida.** No es una preferencia de estilo. En una carpeta sincronizada la fecha de un fichero la cambia cualquiera —y OneDrive la cambia sola al sincronizar—, dos personas escribiendo a la vez producen una escritura perdida en vez de un conflicto visible, y un borrado no se deshace. Con un repo, las tres cosas se resuelven de golpe: la fecha va dentro del commit, un choque es un conflicto que hay que resolver, y cualquier estado anterior vuelve con un `checkout`. `aisdd init` **se detiene** si la ubicación no es un repositorio git.

**La auditoría es una sola, con el repo anotado en cada entrada.** El fichero ya se parte por escritor y mes (`audit/YYYY-MM/<quien>.jsonl`), y con un dev por repo eso separa por repo de hecho: un nivel más de directorio no evitaría ninguna colisión que no esté evitada, y obligaría al lector a manejar tres disposiciones. Un campo `repo` da el mismo filtrado sin tocar el layout.

**Los repos de código van dentro del árbol del de gobierno**, ignorados por él —`init` escribe ese `.gitignore`, y sin él un `git add -A` se traga el código del cliente—. No es una convención: el CLI de `openspec` no admite opción de raíz y espera `openspec/` en el directorio desde el que corre, así que ese árbol es lo que hace que todo lo demás funcione.

**Y un dev no cambia de carpeta nunca.** Trabaja en su repo de código y lanza ahí `open`, `implement`, `amend` y `close`; el skill sube hasta `openspec/config.yaml` para encontrar las specs, ejecuta el CLI desde esa raíz y commitea con `git -C`. Build y tests se quedan donde está el dev. Solo `init` y `roadmap` se lanzan desde la raíz, y son del Lead.

Eso hace además que **el repo de código no lleve ninguna referencia** al de gobierno: subir es suficiente. Una cosa menos que mantener, y un rastro menos en el repo del cliente.

**Commit y push van por comando, no por sesión.** Todos los comandos escriben una entrada de auditoría, y una entrada que solo existe en un portátil no es un registro. Y el orden respecto al repo de código es lo que hace que el roadmap diga la verdad: `open change` se commitea antes de escribir código, y `close change` **después** de que la PR esté mergeada.

**Los rastros no son solo esas dos carpetas.** Si la razón de externalizar es que no aparezcan en el repo de código, `aisdd init` enumera también `AGENTS.md`, `CLAUDE.md`, `.claude/`, `docs/aidd-activity.md` —que el hook escribe dentro del repo de código— y los trailers de co-autoría en los mensajes de commit, que están en la historia y no se quitan sin reescribirla. **Los enumera; no borra nada ni toca el `.gitignore`**: son ficheros del repo del cliente.

**Y al repasar la externalización aparecieron dos cosas que sí rompía**, ninguna en el sitio donde las buscaba:

- **`aiba metrics` era single-repo**, en las dos topologías de varios repos y desde F-20. El registro de actividad lo escribe un hook que anota **relativo al directorio donde se trabaja**, así que con N repos hay N registros y los KPIs medían uno. Publicar la actividad de un tercio del equipo sin ninguna señal de que falta el resto es peor que no publicarla. `--activity` y `--repo` pasan a ser **repetibles**, con aviso cuando alguno falta.
- **En `externalizado`, el `openspec/` está fuera y los registros de actividad dentro** de cada repo, que es donde el hook escribe. Queda dicho explícitamente, porque buscarlos al lado del `openspec/` no los encuentra.

Lo que **no** rompe, comprobado: `audit.py` funciona fuera de un repo git —cae a la identidad global— y las métricas de git degradan a `available: false` sin romper el informe.

`multirepo: true` sigue valiendo como `fraccionado` — migración aditiva, sin romper los `config.yaml` ya escritos. Y cambiar de topología a mitad de proyecto tiene procedimiento propio: **es una migración**, no un ajuste, y en la dirección `externalizado → fraccionado` hay un caso incómodo que hay que decir antes de empezar — los changes archivados que tocaron varios repos no tienen un sitio único.

## F-23 — Migrar de topología lo hace el skill

**Estado:** implementada · **Versión:** `aisdd` 3.7.0 · **Añadida:** 2026-09-02

F-22 dejó las tres topologías descritas y la migración entre ellas contada como una lista de pasos para que la hiciera el humano. Sacar `openspec/` de un repo a mano son siete pasos, dos ficheros de exclusión distintos que van en sitios distintos, y una decisión sobre la historia de git. Es justo el tipo de cosa que un skill debería hacer.

**`aisdd roadmap` la ejecuta.** Detecta la petición —«saca `openspec/` del repo», «el cliente no puede ver estas carpetas», «vamos a partir esto en tres repos»— y también el caso de un proyecto a medio migrar, donde `roadmap.topology` no cuadra con lo que hay en disco.

**El destino se resuelve con dos preguntas, no con un menú de tres nombres.** Cuántos repos tiene el código, y si el registro vive dentro o en un repo aparte. De ahí sale la topología:

| Código | Registro dentro | Registro aparte |
|---|---|---|
| 1 repo | `mono` | `externalizado` |
| N repos | `fraccionado` | `externalizado` |

**Y pregunta el porqué**, que no es curiosidad: si la razón es que los artefactos no deben verse en el repo de código, el paso de la historia deja de ser opcional.

**Lo que el skill hace**: el inventario previo —cuántos changes, cuánta auditoría, si hay algo abierto—, mover las carpetas con `git rm --cached` para no borrarlas del disco, los dos ficheros de exclusión (`.gitignore` del gobierno, `.git/info/exclude` del código, que **no se versiona** y por eso no deja rastro), el `config.yaml`, el prefijo de los `paths` de los lanes, y el registro de la migración.

**Lo que no hace nunca**: reescribir la historia de un repo —da el comando y explica que cambia todos los hashes, pero lo ejecuta el humano—, borrar el `openspec/` de origen antes de que el destino esté subido, migrar con un change abierto, y tocar el `.gitignore` versionado del repo de código para esconder cosas.

**El caso incómodo, dicho antes y no después:** volviendo de `externalizado`, los changes archivados que tocaron varios repos no tienen un sitio único.

## F-24 — El diseño llega hasta la HU

**Estado:** implementada · **Versión:** `aisdd` 3.8.0 · `aidd` 2.6.0 · `aifg` 0.1.0 · **Añadida:** 2026-09-03

El front implementado no se parecía al diseñado. La causa no era capturar poca información, sino que **lo capturado era un vocabulario y no un diseño**, y lo poco que había se perdía tres veces por el camino.

**`aisdd implement change` no mencionaba `guia-estilos.md` ni una vez.** Quien escribía el front no tenía ningún paso que le dijera que abriera la guía; la única mención estaba en el prompt del Outcome Validator, dentro de la metodología en prosa, que no es un paso ejecutable. Un documento que ningún paso manda leer no se lee, y eso explicaba el grueso del síntoma.

Ahora `implement change` **deduce del contexto de la HU** si el change toca front y lee la fuente que haya: los artefactos de `docs/design/` si el proyecto los tiene, `docs/guia-estilos.md` si no, e improvisa si no hay ninguno. Degrada sin error en los tres casos, y **no sabe de Figma**: solo lee una convención de ruta.

**`close change` no verifica nada de diseño** — eso es del dev o del validator. Puede dejar constancia en la auditoría de qué fuente usó, a su criterio; al ser discrecional no servirá para medir después, que es el precio de no imponer ruido.

## AIFG, el sexto plugin

`guia-estilos.md` describe un sistema, no unas pantallas: ningún conjunto de tokens correctos reproduce una composición. **`aifg capture`** extrae los nodos de Figma y los deja colgando de la HU que los implementa; **`aifg update`** re-captura lo que cambia y dice a quién afecta.

**El modelo está normalizado para que cargue poco**: definiciones de componente una sola vez, un mapa corto por HU que las referencia, y las definiciones se abren **solo si el change las toca**. El ahorro grande no es la deduplicación — es que el fraccionamiento permite cargar bajo demanda, el mismo principio que ya gobierna los skills de este repo.

Decisiones que sostienen el diseño:

- **Los overrides se separan por tipo, no por cantidad.** Contenido y estilo se capturan en silencio (es el uso normal de un componente, y un Figma real trae cientos); estructura se captura **y se señala**, porque casi siempre falta una variante. El umbral es programable y no hay que calibrarlo.
- **La identidad es la `key` del componente publicado**, y node id para las instancias. Sin librería publicada, node id para todo y rehacer las referencias cuando se rompa: es el precio de un diseño mal construido, y **se reporta cuántos cayeron a ese modo** para estar en el frágil sabiéndolo.
- **Los aglomerados existen solo si Figma los declara como componentes.** Lo que diseño no componentizó se repite inline. No se detectan subárboles repetidos: eso produce `grupo-17` y no le dice nada a nadie.
- **Nada se edita a mano**, así que relanzar la extracción es rutina. El registro de vínculos HU ↔ frame es la excepción: lo confirma un humano y **sobrevive a cualquier regeneración**.
- **La HU no guarda nada.** Ni puntero, ni referencia: la búsqueda va del id de la HU al registro. Así `detalle-historias-usuario.md` sigue client-ready y ningún skill de AIDD cambia.
- **El disparo es humano.** No hay comprobación automática contra Figma, porque **cuando el dev trabaja el diseño está aprobado y cerrado**: un cambio a mitad de implementación es una incidencia, no una sincronización.

**Y una contradicción que llevaba tiempo en el repo:** el README declaraba que los skills nunca caen a llamadas REST ni gestionan credenciales, y treinta líneas después ofrecía la API REST de Figma como alternativa. La excepción estaba escrita solo para Figma y sin justificarla. Fuera del README y del skill: **solo MCP**, como Jira.

`aidd style-guide` conserva la extracción ligera —paleta, tipografía, espaciado, tokens—, **emite `tokens.json` y `tokens.css`** en vez de dejar las custom properties como prosa que alguien reteclea, y ofrece encadenar con `aifg capture`. Los tokens tienen **un solo dueño**: los emite la guía y los consume quien haga falta.

**Queda fuera, dicho a propósito:** remediar HU cerradas cuando cambia el diseño contra el que se implementaron. Se reporta cuáles son y ahí para — la salida natural es otra HU o una tarea, y la metodología no contempla hoy ese camino.

## F-25 — El registro de actividad no escribe fuera de Claude Code

**Estado:** parcial · **Versión:** `VERSION` 1.36.0 · **Añadida:** 2026-09-03

Comprobado sobre Codex CLI 0.151.0 con el marketplace instalado de verdad, capturando payloads reales.

**Codex ya instala este repositorio tal cual.** Lee `.claude-plugin/marketplace.json` y los `plugin.json` sin traducción, y registra los hooks en su `config.toml` con un `trusted_hash` por entrada. No hacía falta ningún manifiesto nuevo — el supuesto de que sí, era falso.

**Y el vocabulario del payload también coincide.** Capturado literal de una sesión de Codex:

```json
{"session_id":"…","turn_id":"…","transcript_path":"…","cwd":"…",
 "hook_event_name":"Stop","model":"…","permission_mode":"bypassPermissions",
 "stop_hook_active":false,"last_assistant_message":"¡Hola!"}
```

`hook_event_name` viene en **PascalCase**, igual que en Claude Code. El snake_case (`post_tool_use`) son solo las **claves de configuración** de Codex, no lo que envía. Una hipótesis anterior decía lo contrario y era falsa.

**La diferencia real capturada es otra: no hay `prompt_id`, hay `turn_id`.** El hook deduplica los eventos de turno por ese identificador entre sus seis copias, así que sin él no hay deduplicación. Corregido: se acepta `turn_id` cuando `prompt_id` no viene.

**El bloqueo, aislado.** Con el hook del plugin instalado el registro queda vacío. Se descartaron una por una las causas plausibles: el entrecomillado del comando --Codex no pasa el comando por un shell, así que unas comillas acaban formando parte de la ruta, pero la copia instalada ya venía sin ellas--, la variable `${CLAUDE_PLUGIN_ROOT}` --sustituida por ruta absoluta, sigue sin escribir-- y el flag `async`.

La prueba que lo cierra: un script **que sí escribe** declarado en un `.codex/hooks.json` de proyecto deja de escribir en cuanto se declara en el `hooks/hooks.json` de un plugin. Mismo script, misma ruta absoluta, mismo evento.

> **En Codex CLI 0.151.0 los hooks empaquetados en un plugin se registran pero no se ejecutan.** Aparecen en `hooks.state` de `config.toml` con su hash de confianza, y no llegan a correr. Los de proyecto sí. **No hay nada en este repositorio que lo arregle**: está del lado de Codex.

**Qué entrega entonces esta versión.** No el registro en Codex, que no depende de nosotros — sino quitarnos de encima nuestras propias suposiciones de plataforma, para que el día que Codex ejecute los hooks de plugin no haya que volver a investigar: `turn_id` además de `prompt_id`, detección de escritura que ya no es una lista blanca de nombres de Claude Code, normalización defensiva de los nombres de evento, y **una prueba en CI** que fija que las dos formas produzcan las mismas líneas.

**Un hallazgo operativo que va al README:** Codex confía los hooks por hash, así que **cualquier release que cambie el hook detiene el registro** hasta que el usuario vuelva a confiarlo. No da error. Si tras actualizar las métricas se quedan planas, es eso. Existe `--dangerously-bypass-hook-trust` para automatizaciones que ya validan el origen.

**Cline** queda documentado y sin tocar: los skills funcionan —lee `.claude/skills/` de forma nativa— pero su modelo de plugin es un módulo TypeScript sobre su SDK, así que no hay hooks y no hay KPIs.

## F-26 — Resolver la ruta de los scripts en vez de asumirla

**Estado:** implementada · **Versión:** `VERSION` 1.37.0 · **Añadida:** 2026-09-03

F-25 dejó aislado el problema y sin resolver: fuera de Claude Code, `${CLAUDE_PLUGIN_ROOT}` llega vacía y las 42 invocaciones de script se convierten en `/skills/…` y fallan. Entre ellas `audit.py`, que escribe **la entrada de auditoría que el método declara obligatoria en todos los comandos**.

**La suposición era nuestra.** Se buscó una variable equivalente en Codex y no existe —solo expone `CODEX_CI`, `CODEX_SESSION_ID`, `CODEX_THREAD_ID` y `CODEX_SANDBOX_NETWORK_DISABLED`—, así que la salida no era pedirle la ruta a la plataforma: era **dejar de asumirla**.

**El script está en el disco en las dos plataformas.** Los 21 documentos que mandan ejecutar uno llevan ahora la regla: si la variable no resuelve, se localiza el script una vez con `find`, se usa su ruta absoluta durante la sesión, y si no aparece se aplica la degradación que ya estaba escrita —hacer el trabajo según la prosa y decirlo—.

**Verificado en vivo.** En una sesión de Codex, aplicando la regla, `audit.py` se localiza y se ejecuta:

```
usage: audit.py [-h] [--root ROOT] [--entry ENTRY]
Entrada de auditoria de aisdd-specs.
```

Con eso vuelven a funcionar fuera de Claude Code la **auditoría**, el **sellado de documentos**, el cálculo de **KPIs** y las **vistas HTML**.

**Nada cambia en Claude Code.** Ninguna invocación se ha tocado: la nota es aditiva y, con la variable definida, no aplica. `check_script_resolution.py` fija que ningún fichero pueda invocar un script sin llevarla — un documento nuevo que copie la forma de invocación sin la nota reabriría el agujero, y no fallaría: simplemente no se ejecutaría lo que hacía falta.

**Y `aisdd init` deja preparado el registro de actividad** en agentes que no ejecutan los hooks de plugin: ofrece crear `docs/aidd-activity.md` —la ventana de medición no se reconstruye, así que se pregunta al principio y no al medir— y escribe un `.codex/hooks.json` de proyecto con la ruta absoluta del hook, sin comillas.

**Lo que queda pendiente:** verificar de extremo a extremo que ese registro se llena en Codex. El hook llega a dispararse, pero falta saber qué eventos emite y con qué nombre de herramienta. Hasta entonces, en Codex `aiba metrics` trabaja con lo que sale de la auditoría y le falta el tiempo atendido.
