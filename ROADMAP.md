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
| F-20 | Producto repartido en varios repositorios: declarados en la arquitectura, un lane por repo | aidd, aisdd | **implementada** | 2026-08-31 |

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

**Estado:** implementada · **Versión:** `aidd` 2.4.0, `aisdd` 3.5.0 · **Añadida:** 2026-08-31

Todo el diseño asumía «la raíz del proyecto» = un directorio con `docs/` y `openspec/`. Un producto repartido en tres repos no tenía sitio: o se duplicaba `docs/` en los tres —tres copias que divergen, la película que ya vimos con `stamp_doc.py` y las metodologías— o el faseado trataba los tres como si fueran uno.

**La forma:** un repo de gobierno en la raíz del workspace, con `docs/` y **un solo** `openspec/`, y los repos de código como directorios hermanos. Un roadmap, una auditoría, un informe de estado. Funciona porque **un change no es código: es la especificación del código**, y no tiene por qué vivir donde vive el código.

**Los repos se declaran en `docs/arquitectura-base.md`, sección 3.** Es una decisión de arquitectura —fija fronteras de despliegue, de equipo y de contrato—, no de faseado. `aisdd roadmap` los copia a `roadmap.repos` en `openspec/config.yaml` con el mismo `id`, que es la clave con la que todo lo demás los nombra.

**Un lane por repo es el corte más limpio que existe.** Las rutas disjuntas dejan de ser un acuerdo entre personas y pasan a ser un hecho del sistema de ficheros. Los `paths` de cada lane son **relativos a su repo**, y un cambio de contrato entre repos es una barrera `FB-NN`, no una dependencia cross-lane: detiene a todos porque el contrato es de todos.

**Lo que había que arreglar de verdad:** `close change` verificaba la independencia con un `git diff` desde la raíz. Los sub-repos no son submódulos, así que ese diff **no ve nada** de lo que pasa dentro y la comprobación pasaría siempre — una verificación que dice que sí sin haber mirado es peor que no tenerla. Ahora recorre `roadmap.repos` y saca el diff de cada uno, y si un repo declarado no está clonado lo dice en vez de dar la verificación por buena.

`aisdd init` comprueba que cada repo declarado existe y es un repositorio git, y avisa —sin bloquear— del que falta, del que no es un repo, y del que está ahí sin estar declarado. **No los clona**: elegir remote, rama y credenciales es del humano.
