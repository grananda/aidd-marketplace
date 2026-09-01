# Modos de faseado (paralelismo)

> Referencia del skill `aisdd-specs`. El indice y las reglas comunes estan en `SKILL.md`.

## Modos de faseado (paralelismo)

Por defecto, AISDD **plantea** un solo hilo: un change abierto a la vez. La razon es concreta — al cerrar un change se consolidan decisiones en `decisions.md`, y dos changes vivos sobre la **misma superficie de decision** producirian specs que se contradicen sin que nada lo detecte.

**Pero es una convencion del faseado, no un guard.** Fuera de `multilane`, ningun comando comprueba cuantos changes hay abiertos: en `atomic` puedes abrir un segundo change y nada te lo impide. Es deliberado (ver el guard de `open change`, `references/open-change.md`), y conviene saberlo antes de elegir modo.

Hay **tres modos** de fasear. El modo se decide en `aisdd roadmap` y queda registrado en `openspec/config.yaml` (`roadmap.mode`). Los demas comandos lo leen; **no lo preguntan de nuevo**.

| Modo | Que paraleliza | Garantia de coherencia | Cuando |
|---|---|---|---|
| **`atomic`** | Nada. El roadmap es secuencial. | **Por convencion.** Nada impide abrir un segundo change. | Un solo dev, o cuando no hay base para cortar con garantias. **Es el default.** |
| **`waves`** (oleadas) | Hasta `N` fases a la vez, una por dev, respetando dependencias. | **Ninguna.** Ordena, no protege. | Equipo con `N` devs y fases claramente separables, cuando no se puede o no se quiere declarar superficies disjuntas. |
| **`multilane`** (lanes) | `N` lineas de trabajo persistentes, un change abierto **por lane**. | Declarada y **verificada** al cerrar. | Cuando el corte en superficies disjuntas es defendible. |

**En cuanto a lo que el tooling impone, `atomic` y `waves` estan al mismo nivel**: los dos comprueban `depends_on` y nada mas. Lo que los separa es la exposicion, no la proteccion — un roadmap secuencial no invita a tener dos changes vivos; uno en oleadas de `N` lo hace por diseno. La unica garantia verificada por un comando es la de `multilane`, en `close change`.

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
- Si un lane descubre a mitad de implementacion que el contrato es insuficiente, eso **no es una correccion local**: es una parada coordinada (ver "Correcciones durante la implementacion" (`references/implement-change.md`)).

### Criterios de corte de lanes

Un corte de lanes es valido cuando se cumplen las tres condiciones:

1. **Rutas disjuntas.** Cada lane declara las rutas de codigo que le pertenecen (`paths`). Dos lanes no comparten ninguna ruta. Es verificable mecanicamente en `close change`.

   > Con **un solo repositorio** las rutas van relativas a su raiz y el corte es un acuerdo entre personas que hay que verificar. Con **varios**, el corte ya existe y lo garantiza el sistema de ficheros: ver "Lanes por repositorio".
2. **Specs disjuntas.** Ningun `spec.md` es escrito por dos lanes.
3. **Contrato previo.** Todo lo que los lanes comparten esta fijado antes de que arranquen, en `F0` o en una barrera.

   > **En multirepo esta condicion se cumple de otra forma**, y hay que saberlo porque aqui no hay `F0` ni barreras: lo compartido no se fija en una fase, se **publica como artefacto versionado** y cada repo consume la version que elige. El equivalente de "fijado antes de arrancar" es "publicado y con version".

Las condiciones 1 y 2 **no se negocian**: dos lanes que escriben los mismos ficheros o las mismas specs no son dos lanes, y ninguna declaracion los convierte en tales.

La 3 admite un escalon intermedio, porque en proyectos reales no siempre todo lo compartido se puede fijar de antemano — ver "Lanes con dependencias".

### Lanes por repositorio (multirepo)

Cuando `docs/arquitectura-base.md` declara **mas de un repositorio**, el modo es `multilane` y **hay un lane por repo, sin excepcion**. No se pregunta en el pre-flight ni se calcula: la frontera de repos ya partio el trabajo, y el faseado se limita a reconocerla.

Es el caso normal en cliente, donde los repos vienen dados --uno por parte del proyecto-- y no hay repo raiz que los agrupe. **No hay repo padre, ni submodulos, ni nada que clonar de forma especial.**

**Como se reparte todo:**

| | Donde vive |
|---|---|
| `openspec/` | Uno **por repo**. Solo lleva los changes de ese repo. |
| `docs/` | Una **copia completa por repo** --`arquitectura-base.md`, `guia-estilos.md`, `detalle-historias-usuario.md`, `roadmap.md`--. |
| El roadmap | **El mismo documento** en todos, con todas las fases. Cada repo ejecuta **solo las de su lane**, que reconoce por su `id`. |
| Los KPI | Se agregan **fuera**, desde la carpeta que contiene los repos, leyendo sus `openspec/`. |

Cinco consecuencias, y son la razon de que este corte sea el mas comodo de todos:

1. **La independencia no se verifica: es estructural.** Un change no puede salirse de su lane porque no puede salirse de su repo. La comprobacion de rutas de `close change` se cumple sola.
2. **Un change, una PR.** El change vive entero en un repo, se cierra con un merge y el roadmap dice la verdad en el momento en que lo dice.
3. **El lane no se elige, se infiere.** No hay puntero que mover ni que se pueda mover mal: `openspec/.lane` no se usa, y `aisdd lane switch` no tiene sentido --se cambia de lane cambiando de repo--. Ver "Resolver el lane activo en multirepo".
4. **No hay barreras.** `F0` y `FB-NN` existen para serializar superficie compartida, y aqui no hay ninguna: ningun repo compila, testea ni despliega contra el fuente de otro. Un roadmap multirepo **no lleva fases barrera**.
5. **La auditoria no colisiona.** Cada repo tiene su `openspec/audit/`, y dentro un fichero por escritor.

> **El punto 4 es la apuesta del modelo, y hay que sostenerla.** Descansa en que los repos son de verdad independientes en codigo: lo que compartan viaja como **artefacto versionado** --un contrato OpenAPI publicado, un paquete, un esquema de eventos-- y cada repo consume la version que elige, cuando la elige. Publicar una version nueva de un contrato es una fase del lane que lo publica; adoptarla es otra fase del lane que lo consume. Ninguna de las dos para a nadie.
>
> Si aparece un repo que necesita el fuente de otro para funcionar, **eso no se arregla faseando**: la frontera esta mal puesta y hay que registrarlo en la seccion 13 de la arquitectura. El roadmap no puede reparar un acoplamiento de compilacion, solo esconderlo.

#### Resolver el lane activo en multirepo

Lo aplican `open change`, `close change` y `aisdd lane status`. **Nunca se pregunta por un `switch`**, y nunca se escribe `openspec/.lane`.

Por este orden, y parando en el primero que resuelva:

1. **`roadmap.repo` de `openspec/config.yaml`.** Es lo normal: lo escribio `aisdd init`. Comprueba que corresponde a un `lane-id` que existe en `roadmap.lanes`; si no, el config se quedo atras respecto al roadmap — dilo y remite a `aisdd roadmap`.
2. **Si falta, infierelo del nombre**: el del directorio raiz del repo, o el ultimo segmento de `git remote get-url origin`, contra los `lane-id` de `roadmap.lanes`. Si **uno solo** coincide, usalo, **dilo en el resumen** y ofrece escribir `roadmap.repo` para que no haya que inferirlo cada vez.
3. **Si no coincide ninguno, o coincide mas de uno, preguntaselo al usuario** con la lista de `lane-id` disponibles.

**No sigas por descarte ni por parecido**, y no elijas "el mas probable". Trabajar con el lane equivocado abre changes de otro repo, escribe specs que no son de aqui y no se nota hasta mucho despues; preguntar cuesta una linea. Es el mismo criterio que `aisdd init` aplica al identificar el repo.

**Fuera de multirepo, un repo no es un lane.** Con un solo repositorio el corte de lanes se hace por modulos y sigue los criterios de arriba: el lane es una linea de trabajo, no una frontera de despliegue.

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

**Proyectos de una sola capa** (backend puro, servicio sin UI, libreria). El corte back/front no aplica, pero **los lanes siguen teniendo sentido**: se cortan por **modulo de dominio** (`clientes`, `facturacion`, `integraciones`), que es el corte mas limpio de todos porque los bounded contexts ya vienen con rutas propias del diseno. Comprueba lo de siempre — rutas disjuntas y nada compartido sin fijar antes — y presta atencion especial a dos trampas de este escenario:

- **El modelo de datos compartido.** Si dos modulos escriben las mismas tablas o las mismas migraciones, no son dos lanes. O uno es dueno del esquema y el otro lo consume, o van juntos.
- **Las utilidades transversales** (`shared/`, `common/`, middlewares, cliente HTTP). Nadie las posee y todos las tocan: si un lane necesita cambiarlas, es una barrera, no una fase de lane.

Advertencia frecuente: **`data` rara vez es un lane independiente de `back`** — comparten esquema y migraciones, luego comparten superficie de decision. Normalmente `back+data` es un solo lane. Los cortes limpios habituales son pocos y grandes, no muchos y finos.

### Lane activo

El lane sobre el que trabaja un dev es **estado local suyo**, equivalente a la rama de Git:

- Vive en `openspec/.lane` (una linea con el `lane-id`). **En multirepo no existe**: el lane lo fija el repositorio, via `roadmap.repo`, y nada lo puede mover — ver "Lanes por repositorio".
- **Nunca** en `openspec/config.yaml`: ese fichero se versiona y dos devs se pisarian el puntero en cada commit.
- `aisdd init` lo anade a `.gitignore`.
- Se consulta y cambia con `aisdd lane` (ver su seccion).

En modo `atomic` el fichero no existe y el concepto no aplica.
