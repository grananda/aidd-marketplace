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
