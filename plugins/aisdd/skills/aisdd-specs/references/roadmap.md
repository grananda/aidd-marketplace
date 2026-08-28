# `aisdd roadmap`

> Referencia del skill `aisdd-specs`. El indice y las reglas comunes estan en `SKILL.md`.

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

## `aisdd roadmap`

> Alias: `native-ai roadmap`.

Fasea el desarrollo antes de modificar documentos OpenSpec.

0. **Si ya existe `docs/roadmap.md`, no lo sobrescribas sin preguntar.** Un roadmap ya faseado suele estar validado, repartido en sprints y, a veces, volcado a Jira: regenerarlo cambia nombres de fase y `change_hint`, y rompe esos enlaces. Ofrece dos caminos y espera respuesta (ver "Anotar un roadmap existente"):
   - **Anotar** — conserva el faseado tal cual y solo anade la capa de paralelismo. Disponible **solo para el modo `waves`**.
   - **Re-fasear** — regenera el roadmap completo (comportamiento clasico). Es obligatorio si el modo destino es `multilane`.
   Si `docs/roadmap.md` no existe, sigue directamente en el paso 1.
1. Revisa si el usuario ya ha pasado requisitos y arquitectura. Localiza documentacion existente en `docs/`, `config.yaml` (`project_context.design_docs` y `project_context.delivery_docs`), `README.md` o rutas indicadas por el usuario. **Lee tambien la capa de entrega si existe** (`docs/sprint-plan.md`, `docs/planificacion-proyecto.md`, `docs/plan-revision-hu.md`): condiciona el faseado (ver "Alineacion con la capa de entrega").
2. Si faltan requisitos, arquitectura, o no esta claro donde estan, solicitalos antes de continuar. La capa de entrega es **opcional**: si no hay `sprint-plan.md`, fasea solo por presupuesto de contexto y dilo.
3. Estima el `presupuesto de contexto` segun la seccion anterior y clasifica el trabajo tambien por complejidad:
   - `baja`: un solo dominio funcional, pocas integraciones y cambios locales
   - `media`: varios modulos o capas, dependencias compartidas o integraciones relevantes
   - `alta`: varios dominios, refactor transversal, seguridad, migraciones, jobs, eventos o multiples integraciones
4. **Decide el numero de fases con el usuario, ofreciendole siempre la opcion automatica.** Usa `AskUserQuestion` si la plataforma lo soporta, con dos opciones:
   - **Automatico `(Recomendada)`** — lo decides tu, siguiendo la pauta de **changes pequeno-medio** (paso 8), el presupuesto de contexto y las fronteras de sprint. Es la opcion por defecto y la que deberia tomarse salvo que el usuario tenga una razon concreta.
   - **Numero fijado por el usuario** — exacto (`N`), minimo (`>=N`) o maximo (`<=N`).

   En modo no interactivo, toma **automatico** sin preguntar y registralo como supuesto.

   **Si el usuario fija el numero, el reparto sigue siendo tuyo** — el usuario dice *cuantas*, no *cuales*. Es donde mas se nota tu criterio: aplica "Equilibrio de fases" para que salgan de magnitud comparable y no un monstruo rodeado de fases triviales.

5. Punto de partida para el modo automatico:
   - contexto `bajo`: normalmente `6-12` fases
   - contexto `medio`: normalmente `4-8` fases
   - contexto `alto`: normalmente `3-6` fases

   Es un punto de partida, no un objetivo: la pauta de changes pequeno-medio puede empujar por encima de ese rango, y el rango no justifica dejar una fase grande.
6. Ajusta ese rango con estas reglas:
   - suma fases si una fase mezclaria mas de un objetivo funcional principal
   - suma fases si una fase exigiria leer demasiados artefactos o demasiadas partes del codigo para abrir un solo change con seguridad
   - suma fases si hay migraciones de datos, seguridad, permisos, integraciones externas o rollout gradual
   - resta fases solo cuando dos bloques sean claramente dependientes y pequenos
7. Diseña las fases para que cada una pueda abrirse como uno o pocos changes OpenSpec con contexto acotado. Cada fase debe poder entenderse con un subconjunto manejable de requisitos, arquitectura y codigo.
8. **Tamano objetivo del change.** Salvo indicacion contraria del usuario, dimensiona cada fase para producir un change **pequeno-medio**: quien valida es un humano (el Outcome Validator) y un change grande no se revisa bien. Ante la duda, parte la fase en varias mas estrechas. **Esta preferencia no manda sobre lo ya decidido** (ver "Jerarquia de criterios de faseado"): no partas una fase si al hacerlo rompes una frontera de sprint o sacas una HU de la ventana de su sprint. En ese caso deja la fase como esta y registra el desajuste en "Conflictos de alineacion roadmap<->sprint".
9. **Resuelve los parametros de paralelismo** segun la seccion "Decision de modo de faseado": cuantos devs trabajan en paralelo (`parallel_developers`) y cual de los tres modos se usa (`atomic`, `waves` o `multilane`). El modo condiciona todo lo que viene despues: nomenclatura e identificadores de fase, agrupacion de prompts y estructura de `config.yaml`.
10. Cuando tengas contexto suficiente, actua con este rol y objetivo:
   ```text
   Actua con el rol de planificador experto de desarrollos de software.
   Analiza los requisitos y fasea el desarrollo en las fases que consideres necesarias para implementarlo con openspec. Ajusta la granularidad del roadmap al presupuesto de contexto del modelo: cuanto menor sea, mas fases y mas pequenas deben ser. Evita fases demasiado grandes que obliguen a arrastrar demasiado contexto en un unico change. Basate en la arquitectura del proyecto. Si existe una planificacion de entrega (docs/sprint-plan.md), alinea el faseado a los sprints: mismo orden, cortes de fase coincidiendo con fronteras de sprint y gates de validacion, y manten los changes de una misma HU dentro de la ventana del sprint donde esa HU esta planificada; el presupuesto de contexto sigue mandando el tamano del change, y donde choque con el sprint, marcalo como conflicto en vez de romper el plan. Si el roadmap es multilane, reparte las fases en las lineas de trabajo (lanes) acordadas: cada lane con rutas de codigo y specs disjuntas de los demas, todo lo compartido resuelto antes en F0 o en una fase barrera, y la nomenclatura F0 / F-<lane-id>-NN / FB-NN. Con ello genera docs/roadmap.md con la division por fases, que entra en cada fase, a que lane pertenece y a que sprint(s) corresponde. Ademas, crea docs/prompts-roadmap-native-ai.md con los prompts a ejecutar hasta finalizar el desarrollo usando los comandos del skill aisdd, agrupados por lane si el roadmap es multilane. No modifiques aun ningun documento de openspec. Si el usuario no ha pasado requisitos y/o arquitectura o no tienes clara donde esta, solicitaselo.
   ```
11. Crea el directorio `docs/` si no existe.
12. Genera `docs/roadmap.md` con:
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
   - **si el modo es `waves`**: la **organizacion en oleadas** y, por cada fase, su oleada y de que fases depende. Escribe la oleada en la tabla de fases con la forma literal `Oleada <N>` (no solo el numero): asi la vista HTML de `booster-docs` la reconoce y la pinta como chip. Anade una vista de la oleada completa (que fases corren a la vez y con que dev).
   - **si el modo es `multilane`**: las dos secciones adicionales descritas en "Secciones de lanes en `docs/roadmap.md`", y el identificador de cada fase segun la nomenclatura `F0` / `F-<lane-id>-NN` / `FB-NN`.
13. Genera `docs/prompts-roadmap-native-ai.md` con los prompts que deben ejecutarse hasta finalizar el desarrollo, usando solo estos comandos del skill:
   - `aisdd open change [what-you-want-to-build]`
   - `aisdd implement change [change-slug]`
   - `aisdd close change [change-slug]`
   - `aisdd lane switch <lane-id>` (solo en modo `multilane`, como paso previo de cada bloque de lane)
14. En `docs/prompts-roadmap-native-ai.md`, para cada fase indica explicitamente:
   - que documentos o secciones pasar al modelo
   - que partes del codigo son relevantes
   - que no debe incluirse todavia para no contaminar contexto
   - cuando conviene dividir una fase en varios changes OpenSpec
   - el sprint al que pertenece la fase (si hay `sprint-plan.md`)
   - el prompt exacto para abrir el change con `aisdd open change [what-you-want-to-build]`
   - el prompt exacto para implementar con `aisdd implement change [change-slug]`
   - el prompt exacto para cerrar con `aisdd close change [change-slug]`
15. **En modo `waves`, agrupa los prompts por oleada**: un bloque por oleada, y dentro de el las fases que pueden ejecutarse a la vez, indicando explicitamente que **se pueden lanzar en paralelo** y que la oleada siguiente no arranca hasta que la actual cierra. Si una oleada lleva una sola fase, di por que (dependencias, no falta de trabajo).
16. **En modo `multilane`, agrupa los prompts por lane, no en una unica secuencia lineal.** Un bloque por lane, cada uno encabezado por su `aisdd lane switch <lane-id>` y con sus fases en orden; `F0` va antes de todos los bloques y cada barrera `FB-NN` va en su propio bloque, con una nota explicita de que **detiene todos los lanes** hasta cerrarse. El documento debe poder leerse de arriba abajo por un dev que solo trabaja un lane, sin tener que filtrar mentalmente fases ajenas.
17. Los prompts de `docs/prompts-roadmap-native-ai.md` deben estar redactados para un usuario final o para otro agente, en espanol, e incluir el contexto minimo necesario para ejecutar cada fase sin arrastrar informacion irrelevante de fases futuras.
18. No uses en ese fichero comandos OpenSpec directos como `openspec new change`, `openspec instructions apply` u `openspec archive`, salvo de forma explicativa excepcional fuera de los prompts operativos.
19. Tras generar `docs/roadmap.md` y `docs/prompts-roadmap-native-ai.md`, actualiza `openspec/config.yaml` con el resumen del roadmap segun la seccion siguiente, y registra la configuracion de paralelismo en `AGENTS.md` segun "Registro del paralelismo en `AGENTS.md`".
20. No ejecutes `openspec new change`, no archives cambios y no edites ningun otro artefacto de `openspec/` (changes, specs) durante este comando. La unica escritura permitida en `openspec/` es la actualizacion de `openspec/config.yaml` descrita en el paso 19. Fuera de `openspec/`, este comando solo toca su **propio** bloque de `AGENTS.md`: nunca el bloque de comandos de `aisdd init`.

21. **Comprueba el mojibake de lo que has escrito.** Es **obligatorio**, no opcional. Pasa `check_mojibake.py --fix` (ver `references/scripts.md`) sobre los artefactos de texto que este comando haya creado o modificado — los mismos que van en `output_files` de la auditoria. **Va aqui, antes de la entrada de auditoria, porque `audit.py` calcula el hash de cada fichero**: reparar despues dejaria registrado el hash de la version corrupta. Si algun fichero queda con `U+FFFD`, no se puede reparar — hay que regenerarlo; dilo en la verificacion final y no lo escondas.
22. **Escribe la entrada de auditoria.** Es obligatoria y **no es opcional para ningun comando salvo `aisdd lane`**. Componla con `audit.py` segun "Scripts del skill" (`references/scripts.md`), con el esquema y las reglas de "Auditoria y trazabilidad" (`references/audit.md`), y `prompt_version` = `<skill_version>:roadmap`. Reporta despues su ruta y su `id` en la verificacion final.

### Anotar un roadmap existente (solo modo `waves`)

Este camino existe porque **una oleada es una anotacion, no una particion**: se puede calcular sobre un faseado ya hecho sin alterarlo. Es el caso tipico de un proyecto ya disenado y planificado al que se le quiere anadir paralelismo porque ahora hay mas devs.

**Solo aplica al modo `waves`.** Los lanes **no se pueden anotar**: el corte en lineas de trabajo determina que entra en cada fase y como se llama, asi que retrofitarlos exige re-fasear. Si el usuario quiere `multilane` sobre un roadmap existente, dilo con claridad y ofrece el re-faseado completo, advirtiendo de que cambiaran los identificadores de fase y, con ellos, los `change_hint` que enlazan con `docs/sprint-plan.md` y con Jira.

Procedimiento:

1. **Lee el roadmap existente** (`docs/roadmap.md` y la seccion `roadmap` de `openspec/config.yaml`) y toma sus fases **tal cual**: mismos nombres, mismo orden, mismos objetivos, mismo alcance, mismos `change_hint`. **No los toques.**
2. **Deriva el grafo `depends_on`** de lo que el roadmap ya dice: su seccion de dependencias, el orden declarado y los prerequisitos entre fases. Si una dependencia no es deducible con confianza, **preguntala** — es la unica informacion que un roadmap antiguo puede no traer explicita, y las oleadas se construyen enteramente sobre ella. No la inventes.
3. **Resuelve `parallel_developers`** segun el paso 0 de "Decision de modo de faseado".
4. **Calcula las oleadas** con el algoritmo de "Construccion de las oleadas". Si el grafo obliga a que casi todas las oleadas tengan ancho 1, **dilo**: ese roadmap se faseo para ejecucion secuencial y anotarlo no va a dar paralelismo real. Ahi el valor esta en re-fasear, no en anotar — pero la decision es del usuario.
5. **Escribe solo la capa nueva**:
   - En `docs/roadmap.md`: anade la seccion **"Oleadas"** y, por cada fase, su oleada y su `depends_on`. **No reescribas** las secciones existentes ni reordenes las fases.
   - En `openspec/config.yaml`: anade `mode: waves` y `parallel_developers` en la raiz de `roadmap`, y `wave`/`depends_on` a cada entrada de `phases`. **Conserva intactas** el resto de claves de cada fase, en especial `change_hint`, `hus` y `sprint`.
6. **Deja constancia** en `docs/roadmap.md` de que el faseado no se ha regenerado, solo anotado, y con que fecha.

Lo que este camino **no** hace, y conviene decirlo en el resumen: no re-evalua el presupuesto de contexto, no repone fases mal dimensionadas y no cuestiona el corte. Anota lo que hay. Si el faseado original tenia problemas, siguen ahi.

Ventaja practica: como no cambia ningun `change_hint`, **no rompe el enlace con el sprint-plan ni con Jira**. Anotar es seguro sobre un proyecto en marcha; re-fasear no.

### Decision de modo de faseado

Este paso decide entre los tres modos (`atomic`, `waves`, `multilane`) y fija `parallel_developers`. Lee antes la seccion "Modos de faseado (paralelismo)" (`references/parallelism.md`), que define el modelo; aqui esta el procedimiento.

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

**Construccion de los lanes (solo modo `multilane`).** Los siete pasos que siguen reemplazan a la construccion de oleadas de arriba; no la continuan.

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
- **Un corte concreto que el usuario propone** (no solo el numero): validalo contra las tres condiciones de "Criterios de corte de lanes" (`references/parallelism.md`). Si falla alguna, di **cual** y por que.

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

Cierra la seccion con el **grafo resumido** (que lane espera a cual, y en que fases) para que el desajuste se vea de un vistazo y `aiba sprint-planning` pueda secuenciarlo.

### Seccion de oleadas en `docs/roadmap.md`

En modo `waves`, `docs/roadmap.md` incluye una seccion **"Oleadas"** con:

- una entrada por oleada, en orden, con las fases que la componen y su `depends_on`
- el **ancho** de cada oleada frente a `parallel_developers` (p. ej. `3/3`, `1/3`), para que se vea donde el faseado paraleliza y donde no
- el motivo de las oleadas de ancho 1 (dependencias, no falta de trabajo)
- una advertencia final, literal, de que **las oleadas no las verifica ningun comando**: el reparto real entre developers es responsabilidad del equipo, y nada impide abrir dos changes de la misma oleada que se pisen

### Equilibrio de fases

El numero de fases lo puede fijar el usuario; **como se reparte el trabajo entre ellas es siempre criterio tuyo**, y es donde un roadmap se hace util o inservible. Un faseado de seis fases donde una se lleva el 60% del esfuerzo no es un faseado de seis fases: es una fase grande con cinco satelites, con todos los problemas de una fase grande (dificil de validar, arrastra demasiado contexto, bloquea el calendario) y ninguna de las ventajas de haber troceado.

**Mide antes de repartir.** Estima cada fase con la mejor senal disponible, en este orden:

1. **Esfuerzo real** de las HU que cubre, si existe `docs/detalle-historias-usuario.md` (tallas XS/S/M/L/XL).
2. **Volumen de contexto** que exige: artefactos que hay que leer, modulos que toca, integraciones implicadas.
3. **Numero de criterios de aceptacion** que debe satisfacer, como aproximacion gruesa si no hay nada mejor.

Di con cual estas midiendo. Una estimacion declarada y discutible es util; una intuicion no declarada no.

**Criterio de equilibrio.** Ninguna fase deberia superar **el doble de la mediana** de las demas. Al pasar de ahi:

- **Fase muy por encima** -> pártela. Si no se puede partir sin romper su objetivo, **dilo explicitamente** y explica por que es indivisible: eso es informacion valiosa para quien planifica el sprint, no un defecto que haya que esconder.
- **Fase muy por debajo** -> fusionala con la fase de la que depende directamente, salvo que caiga en una de las excepciones de abajo.

**Excepciones legitimas — no fuerces el equilibrio aqui:**

- **`F0` / `foundation`** suele ser mas pequena que el resto. Es correcto: su trabajo es habilitar, no entregar.
- **Las barreras (`FB-NN`)** suelen ser pequenas (un cambio de contrato, una migracion). Su valor es detener, no ocupar.
- **Una fase de riesgo alto** se aisla aunque quede pequena. Aislar el riesgo vale mas que cuadrar el reparto.
- **Una fase con validacion compleja** (gate con cliente, auditoria, cumplimiento) va sola por la misma razon.

En los cuatro casos, anota el motivo en `docs/roadmap.md`: un desequilibrio explicado es una decision; uno sin explicar parece un descuido.

**Limites que el equilibrio no puede cruzar** (ver "Jerarquia de criterios de faseado"): no partas una fase si con ello rompes una frontera de sprint o sacas una HU de la ventana de su sprint, y no fusiones dos fases si el resultado excede el presupuesto de contexto. El equilibrio es el ultimo criterio en aplicarse, no el primero.

**Cuando el usuario fija el numero y no cuadra.** Si con `N` fases no hay reparto equilibrado posible —porque el alcance da para menos incrementos con sentido, o porque una unidad de trabajo es indivisible y desborda—, **no trocees artificialmente para cumplir la cifra**. Genera el faseado que si tiene sentido, dilo con el motivo concreto, y deja que el usuario decida si mantiene su numero o acepta el tuyo.

### Jerarquia de criterios de faseado

Cuando varios criterios tiran en direcciones distintas, este es el orden. Un criterio inferior **nunca** anula a uno superior; cuando choquen, se registra el conflicto en vez de romper lo ya decidido.

1. **El sprint manda sobre el orden y las fronteras.** Si existe `docs/sprint-plan.md`, el faseado respeta su orden, sus cortes y que HU estan comprometidas. AISDD no reescribe el sprint-plan.
2. **El presupuesto de contexto manda sobre el tamano del change.** Una fase no puede exigir mas contexto del que el modelo puede sostener con seguridad.
3. **La preferencia por changes pequeno-medio** afina dentro de lo que permiten 1 y 2. Es una preferencia, no una autoridad: **no partas una fase si al hacerlo rompes una frontera de sprint o sacas una HU de su ventana**.
4. **El modo de paralelismo** (`waves`/`multilane`) reparte lo que 1-3 ya han decidido. No cambia que entra en cada fase; cambia quien la ejecuta y cuando.

Ejemplo de aplicacion correcta: una fase queda grande para el gusto de la regla 3, pero partirla dejaria la HU-07 a caballo entre dos sprints. **No se parte**: se deja como esta y se anota en "Conflictos de alineacion roadmap<->sprint" para que el humano decida si re-empaqueta el sprint.

### Alineacion con la capa de entrega (sprint-plan)

Si existe `docs/sprint-plan.md`, el roadmap **se pliega a los sprints ya planificados** por AIBA, sin dejar que la capacidad mande sobre el presupuesto de contexto. Regla de jerarquia: **el presupuesto de contexto decide el tamano del change; el sprint decide el orden, las fronteras y que HU estan comprometidas.**

- **Orden**: fasea en el **mismo orden** que los sprints (que ya refleja prioridad de negocio, capacidad y dependencias).
- **Fronteras**: haz coincidir los **cortes de fase con las fronteras de sprint** y con los gates de validacion (de `plan-revision-hu.md`) siempre que el contexto lo permita.
- **Agrupacion**: manten los **changes de una misma HU dentro de la ventana del sprint** donde esa HU esta planificada, para que un sprint no quede con changes a medias.
- **HU no validadas**: si `docs/plan-revision-hu.md` marca una HU como **en revision o bloqueada**, no la metas en una fase temprana como comprometida; senala que depende de su validacion.
- **Esfuerzo**: anota en cada fase el esfuerzo agregado (humano vs IA) tomado de `planificacion-proyecto.md`/`sprint-plan.md`.
- **Conflictos (no romper el plan)**: cuando el presupuesto de contexto obligue a partir una HU en varios changes que **no caben** en su sprint, o a cortar a mitad de un bloque, **no reescribas el sprint-plan**: registra el desajuste en la seccion **"Conflictos de alineacion roadmap<->sprint"** de `docs/roadmap.md` (que HU se parte, en cuantos changes, que sprint desborda) para que el humano re-ejecute `aiba sprint-planning` y re-empaquete (re-faseado seguro: mueve HU, no recrea issues). AISDD **no** modifica `docs/sprint-plan.md`.

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
5. Si ya existia una seccion `roadmap` de una ejecucion anterior, sustituyela integramente por la nueva (el roadmap mas reciente manda). No fusiones fases antiguas con nuevas. **Excepcion: en el camino "Anotar un roadmap existente"** no sustituyes nada — conservas todas las entradas de `phases` con sus claves y solo anades `wave` y `depends_on` a cada una, mas `mode` y `parallel_developers` en la raiz. **Excepcion: conserva los `amended_by`** de las fases que sobrevivan con el mismo `change_hint` — son enmiendas ya aplicadas en otro lane que la fase todavia no ha recogido, y perderlas deja al lane implementando contra un contrato desmentido. Si una fase marcada desaparece del nuevo faseado, dilo en el resumen.
6. Manten YAML valido: indentacion con espacios (no tabs), valores con caracteres especiales entre comillas, UTF-8 sin BOM.
7. **Valida `depends_on` en cualquier modo antes de escribir**: (a) todo id referenciado existe en `phases`; (b) el grafo es **aciclico**; (c) ninguna fase depende de otra posterior en el orden del documento. Si alguna falla, no escribas: corrige el faseado.
8. **En modo `waves`, valida ademas**: (a) toda fase tiene `wave`; (b) ninguna oleada supera `parallel_developers` fases; (c) ninguna fase comparte oleada con una de la que depende, ni esta en una anterior.
9. **En modo `multilane`, valida ademas**: (a) todo `phases[].lane` existe en `lanes[]`; (b) las fases con `barrier: true` no tienen `lane`; (c) los `paths` de cada fase de lane son subconjunto de los de su lane (las barreras no declaran `paths`); (d) ningun `paths` de un lane es prefijo de los de otro. Si alguna falla, no escribas el fichero: corrige el faseado primero.
10. Incluye `openspec/config.yaml` en los `output_files` de la entrada de auditoria de este comando, junto a `docs/roadmap.md` y `docs/prompts-roadmap-native-ai.md`.

### Registro del paralelismo en `AGENTS.md`

El objetivo es que cualquier agente (o persona) que abra el proyecto sepa **como se trabaja en paralelo** sin tener que bucear en `openspec/config.yaml`. `aisdd roadmap` lo registra en un bloque idempotente **propio**, delimitado por sus marcadores, **hermano e independiente** del bloque de comandos que gestiona `aisdd init`.

1. Localiza `AGENTS.md` en la raiz. Si no existe, crealo con una cabecera minima (`# AGENTS.md`) seguida del bloque.
2. Construye el contenido segun el modo, con los valores confirmados en el paso 9 ("Resuelve los parametros de paralelismo") del flujo principal:

   ```markdown
   <!-- BEGIN aisdd-specs roadmap (auto-generado, no editar a mano) -->
   ## Configuracion de roadmap

   - Modo de faseado: `atomic` | `waves` | `multilane`
   - AI Developers en paralelo: <N>
   <!-- END aisdd-specs roadmap -->
   ```

   - **`atomic`**: solo esas dos lineas. Anade una tercera: `> Sin aislamiento garantizado: dos changes abiertos a la vez pueden producir decisiones contradictorias.`
   - **`waves`**: anade el numero de oleadas y una linea recordando que **las oleadas no las verifica ningun comando**; el reparto real entre developers es del equipo.
   - **`multilane`**: anade una tabla de lanes (`lane-id`, rutas, perfil), el dueno del contrato compartido, y una linea operativa: `Selecciona tu linea con` `aisdd lane switch <lane-id>`; `un change abierto por lane.`

3. **Registra el bloque con `agents_block.py`** (marker `roadmap`) — ver "Scripts del skill" (`references/scripts.md`). A mano: si ya existe un bloque entre `<!-- BEGIN aisdd-specs roadmap ... -->` y `<!-- END aisdd-specs roadmap -->`, **reemplazalo integramente**; si no existe, anadelo al final precedido de una linea en blanco.
4. **No toques nada mas del fichero.** En particular, no reordenes ni reescribas el bloque `<!-- BEGIN aisdd-specs commands -->`: son bloques distintos con ciclos de vida distintos (uno lo gestiona `init`, este lo gestiona `roadmap`).
5. Los valores deben **coincidir** con los de `openspec/config.yaml` (`roadmap.mode`, `roadmap.parallel_developers`, `roadmap.lanes`). `config.yaml` es la fuente de verdad; este bloque es su vista legible. Si al re-ejecutar detectas que divergian, gana `config.yaml` y dilo en el resumen.
6. Incluye `AGENTS.md` en los `output_files` de la entrada de auditoria de este comando, junto a `docs/roadmap.md`, `docs/prompts-roadmap-native-ai.md` y `openspec/config.yaml`.

En el camino "Anotar un roadmap existente" este bloque **si se escribe**: es capa de paralelismo, no faseado.

### Criterios de particion para el roadmap

Usa estos criterios para dividir en mas fases cuando el modelo tenga menos capacidad:

- separar cambios por dominio funcional
- separar backend, frontend, datos e integraciones cuando no sea imprescindible tratarlos juntos
- separar preparacion tecnica de entrega funcional si la primera desbloquea varias fases
- separar migraciones, permisos, seguridad, observabilidad y rollout
- separar cambios con alto riesgo o validacion compleja

Estos mismos criterios sirven para **asignar lane** en modo `multilane`, con dos matices que cambian su lectura:

- Los dos primeros criterios reparten trabajo **entre lanes**: dominio funcional y separacion back/front/datos/integraciones son los cortes candidatos. Pero un corte solo vale como lane si ademas cumple las tres condiciones de "Criterios de corte de lanes" (`references/parallelism.md`) — el criterio de contexto sugiere donde cortar, no garantiza que el corte sea independiente.
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
