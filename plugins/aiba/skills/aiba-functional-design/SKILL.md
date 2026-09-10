---
name: aiba-functional-design
description: AIBA (AI Business Analyst) — genera el Documento de Diseno Funcional (DF) en Word de cada historia de usuario, mediante el comando `aiba functional-design` (alias `aiba df`, `aiba diseno funcional`). Lee `docs/detalle-historias-usuario.md` como fuente de verdad y produce un `.docx` por HU en `docs/df/`, con la estructura acordada: portada, control de versiones, control de aprobaciones, indice, introduccion y alcance, la HU con su narrativa COMO/QUIERO/PARA, tabla de filtros y campos, integraciones con otros aplicativos, validaciones y reglas separadas por frontal y core, mensajes y avisos, pantallas y prototipo, criterios de aceptacion, especificaciones tecnicas y puntos abiertos. El diseno es **generico y sin marca**: usa estilos nativos de Word (Titulo 1/2/3, estilo de tabla, cabecera y pie editables) para que una paleta corporativa y un logo se apliquen despues sin rehacer nada, y **pregunta antes** si se desea aplicar una marca concreta, tomandola de una carpeta local o de una URL. Funciona sobre **todas las HU o una sola** (`aiba functional-design HU-03`), y **reedita** un DF ya generado conservando su historial de versiones y las secciones que el analista haya escrito a mano. Usar cuando el usuario pida "genera los DF", "documento de diseno funcional", "el DF de la HU-05", "actualiza el DF", o equivalentes. Acepta una **plantilla `.docx`/`.dotx` del cliente** de la que hereda estilos, formato de pagina y **la cabecera y el pie intactos, con su logo** --resolviendo los nombres de estilo por idioma y avisando de los que falten--, numera los apartados en el texto del titulo porque los estilos `Heading` de Word no numeran solos, escribe en espanol correcto y para Negocio y QA ajenos al proyecto, **no cita codigos internos** (`RF-xx`, `GAP-xx`) sino que explica el contenido, e **inserta la pantalla** exportada de Figma por `aifg` en vez de su identificador de nodo. Todo lo que tenga que completar una persona sale **resaltado en amarillo**, el alcance dice solo lo que entra, y en el control de versiones firma el analista, nunca el skill.
metadata:
  author: NTT DATA Spain GDN-e
  version: "1.11.0"
---

# aiba-functional-design (AIBA · Diseno Funcional)

Usa este skill cuando el usuario quiera generar o actualizar documentos de **Diseno Funcional (DF)** a partir de las historias de usuario ya detalladas. Comandos:

- `aiba functional-design [HU-XX]`
- Alias: `aiba df [HU-XX]`, `aiba diseno funcional [HU-XX]`

Responde y documenta en espanol. Conserva en ingles nombres de comandos, ficheros, rutas y terminos tecnicos establecidos.

## Que es AIBA y donde encaja este skill

**AIBA** (AI Business Analyst) es el conjunto de skills que da la cara ante el negocio: el DF que el cliente firma, el plan que aprueba, el calendario que sigue y los KPIs con los que juzga si merecio la pena. Este skill cubre el primero de esos cuatro — el analisis funcional: traducir lo que el negocio necesita en un documento que un equipo puede implementar y un cliente puede firmar. Los otros cuatro skills del conjunto son `aiba hu-review-plan`, `aiba project-plan`, `aiba sprint-planning` y `aiba metrics`.

**Este skill consume lo que produce AIDD** y no lo sustituye:

| Produce | Skill | Este skill lo usa para |
|---|---|---|
| `docs/detalle-historias-usuario.md` | `aidd user-story-details` | **Fuente de verdad**: la HU, su prioridad, sus criterios de aceptacion y sus notas tecnicas |
| `docs/mapa-historias-usuario.md` | `aidd user-stories` | Persona/rol, fase y agrupacion |
| `docs/requisitos.md` | `aidd requirements` | RF/NFR que la HU realiza, para el alcance |
| `docs/arquitectura-base.md` | `aidd architecture` | Integraciones, modulos y separacion frontal/core |
| `docs/guia-estilos.md` | `aidd style-guide` | Referencia visual, si hay que describir pantallas |

Criterio de salida: existe un `.docx` por cada HU solicitada en `docs/df/`, con todas las secciones presentes, lo que no se pueda deducir marcado explicitamente como pendiente, y sin haber inventado nada que la documentacion no sostenga.

## Reglas generales

- Trabaja desde la raiz del proyecto del usuario.
- **La fuente de verdad es `docs/detalle-historias-usuario.md`.** Si no existe, detente y propon ejecutar antes `aidd user-story-details`: sin criterios de aceptacion no hay DF que escribir, solo una plantilla vacia.
- **No inventes**. Un DF es un documento que alguien firma y contra el que se desarrolla. Lo que no puedas deducir de la documentacion se marca como pendiente (ver "Como marcar lo que falta"), nunca se rellena con algo plausible.
- **No modifiques los documentos de AIDD.** Este skill lee `docs/` y escribe **solo** en `docs/df/`.
- **Un DF por HU.** No agrupes varias historias en un documento aunque compartan pantalla: el DF se revisa y se aprueba por historia.
- El `.docx` es el entregable; **no** hay un `.md` intermedio que sea fuente de verdad. La fuente sigue siendo el detalle de HU, y el DF es su traduccion a un documento firmable.
- **Sin marca por defecto.** El documento sale con estilos nativos de Word y sin logotipos ni colores corporativos, salvo que el usuario pida lo contrario en el paso 1.
- **Escribe en espanol correcto, con acentos y enes.** El `.docx` es un documento que firma un cliente: acentuacion, puntuacion y concordancia de un documento formal. **Da igual como este escrito este skill** --sin acentos, por convencion del repositorio--: eso es codigo fuente, y el DF no.
- **Escribes para Negocio y QA del cliente, que no conocen el proyecto.** Ni las siglas, ni las decisiones previas, ni por que las cosas son como son. En consecuencia: un **parrafo de contexto antes de cada tabla**, que diga que se esta listando y por que; **siglas expandidas la primera vez** que aparecen; y frases completas. Una tabla es una tabla, pero el texto es texto: nada de estilo telegrafico.
- **Lo que sea una lista, va como lista.** En cuanto enumeres mas de dos cosas --validaciones, mensajes, campos, sistemas con los que se integra, pasos de un flujo, criterios-- escribe **una linea por elemento empezando por `- `**, y el generador la saca como vineta de Word **con la plantilla que sea**: si la del cliente no trae ningun estilo que numere, crea una numeracion en el documento en vez de dejar el parrafo suelto. Nada de meter cinco reglas en un parrafo separadas por comas: asi no se lee, no se revisa y no se convierte en casos de prueba. Quien valida el DF necesita poder senalar **el tercer elemento**, y para eso tiene que existir como elemento. El parrafo de contexto sigue yendo antes de la lista, igual que antes de una tabla.
- **Sin codigos internos en el cuerpo.** Nada de `RF-014`, `GAP-07` ni referencias a documentos internos: **se explica el contenido**. En vez de "cumple RF-014", *"el sistema debe permitir buscar por numero de poliza y por NIF del tomador"*. Quien lee el DF no tiene esos documentos y el codigo no le dice nada; el contenido si.
  > La trazabilidad no se pierde: el vinculo HU -> requisito vive en `docs/requisitos.md` y en el detalle de HU, y el vinculo HU -> Jira en `docs/jira-sync.md`. El DF no tiene que cargarlo. **El `HU-XX` si se queda**: da nombre al fichero y es la clave con la que `aiba test-plan` y Jira enganchan.
- **El alcance dice solo lo que entra.** Nada de "queda fuera X". Lo que hace otra historia pertenece al alcance de esa otra historia, y listarlo aqui como exclusion confunde a quien revisa: parece que el producto no lo hara. Si algo no se puede acotar, es un **punto abierto**, no una exclusion.
- **Nada de descartes.** El DF cuenta lo que el sistema hace, no la opcion que se valoro y se cayo. Un lector ajeno no distingue "descartado" de "pendiente", y acaba preguntando en revision por una cuarta FAQ que nadie va a construir. Si un descarte tiene consecuencias, se cuenta la **consecuencia**, no el descarte.
- **El autor es una persona.** En el control de versiones firma el analista que responde del documento ante el cliente: nunca este skill, ni un modelo, ni "IA". El generador lo comprueba y vacia la celda si reconoce el nombre de una herramienta.
- **Lo que falta se resalta, y no depende de como lo escribas.** El generador pinta en amarillo cada `[PENDIENTE: ...]`, tambien dentro de las tablas, y **ademas las formas en prosa**: "pendiente de definir", "falta por confirmar", "por determinar", "se desconoce", "no consta". Antes solo se resaltaba el marcador literal, y el mismo DF salia con los huecos visibles o invisibles segun que modelo lo hubiera redactado. Un DF de veinte paginas se lee en diagonal: un hueco sin resaltar acaba firmado como si fuera contenido.
- **Nada de lo que te fabriques para trabajar se queda en el proyecto.** Si para resolver una incidencia o retocar un DF necesitas un script de usar y tirar, escribelo en un directorio temporal (`mktemp -d`, o `/tmp/df-<algo>/`), **nunca en la carpeta del proyecto ni en `docs/`**. Vale para **cualquier lenguaje** --`.py`, `.js`, `.mjs`, `.ts`, `.sh`, `.ps1`-- y para todo lo demas que genere la herramienta: `package.json`, `node_modules/`, `requirements.txt`, entornos virtuales, `__pycache__`, ficheros de datos intermedios y copias de trabajo del `.docx`. Lo que se queda ahi no lo limpia nadie: acaba versionado, confunde a quien abre el repo y no es un entregable. **En la carpeta del DF solo van los `.docx`.** Si algo de eso merece conservarse, di donde esta y por que, y deja que el humano decida si lo trae.
- Este documento requiere revision humana. Al terminar, deja claro que esta pendiente de revision del analista.

## Flujo del comando

### 1. Plantilla, marca y autor (preguntar SIEMPRE, antes de generar nada)

Antes de leer documentacion o generar ficheros, **pregunta con que aspecto sale el documento**. Es lo primero porque condiciona todo el resto y porque rehacer veinte documentos por no haber preguntado es caro.

La pregunta de verdad es corta: **si el cliente tiene una plantilla, donde esta**. Usa `AskUserQuestion` si la plataforma lo soporta:

1. **Plantilla del cliente `(Recomendada si existe)`** — pide **la ruta del fichero** `.docx` o `.dotx` y ya esta. Si la plantilla trae los apartados del DF --que es lo normal: un cliente da el documento entero montado, no un juego de estilos--, el generador entra en **modo esqueleto** y **escribe dentro de los apartados que ya existen**, sin tocar nada mas: portada, logo, cabecera, pie, indice, numeracion de titulos y estilo de las tablas se quedan como el cliente los monto, y solo se sustituye el texto de ejemplo. Si no los trae, se usa por sus estilos y el cuerpo se escribe entero. Si el cliente tiene plantilla, esto es siempre mejor que cualquier otra opcion: aplicarla despues a mano en veinte documentos no es una opcion.
2. **Sin nada `(Recomendada si no hay plantilla)`** — estilos nativos de Word, sin logo y con la paleta por defecto. Queda listo para que cualquiera le aplique despues su identidad sin rehacerlo.
3. **Marca desde una carpeta local** — pide la ruta y busca en ella el logo (`.png`, `.jpg`, `.svg`) y, si existe, un fichero de tokens o guia de estilos del que extraer los colores.
4. **Marca desde una URL** — pide la URL de la web corporativa o de la guia de marca, y extrae de ahi el logo y los colores dominantes.

Si elige **3 o 4**, pide ademas lo que no puedas deducir: **color principal**, **color secundario** y **texto de cabecera y pie**. Confirma lo detectado antes de usarlo; no des por buena una paleta extraida automaticamente sin ensenarla.

En modo no interactivo, toma la **opcion 2** y registralo como supuesto.

**Con plantilla, ensena su indice y pregunta que dejar en blanco.** El skill tiene que servir para **cualquier cliente**, y eso no se consigue adivinando que quiere decir cada titulo ajeno: se consigue ensenando el indice y dejando que una persona decida. Antes de generar nada:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/aiba-functional-design/scripts/gen_df_docx.py" \
  --indice "ruta/a/la/plantilla.docx"
```

Devuelve cada apartado con su **numero**, su nivel, su titulo y con que apartado del DF se corresponde --`null` si es propio del cliente y no se reconoce--. Ensenale esa lista al usuario, di cuantos se han reconocido, y **preguntale que apartados quiere dejar en blanco**: tablas que rellena el cliente, anexos que aporta otro equipo, apartados que en esta HU no aplican. Lo que responda va al manifiesto en `secciones_en_blanco`, **por numero** (`"2.1"`, `"4"`) porque es como los nombra quien tiene el indice delante; tambien vale el nombre. Dejar `"2"` en blanco deja en blanco todo lo que cuelga de el.

Un apartado en blanco conserva su titulo y, si la plantilla traia tabla, su cabecera vacia lista para rellenar a mano; no se escribe contenido ni marca de pendiente, porque no falta: se ha decidido dejarlo. Lo dejado se devuelve en `secciones_en_blanco`, y lo que se pidio pero no estaba en el indice en `en_blanco_no_encontradas` --diselo, o el usuario se queda creyendo que dejo en blanco algo que se ha rellenado igual--.

**Y pregunta a nombre de quien va el documento**: el autor del control de versiones es el **analista que responde del DF ante el cliente**. Si el usuario no lo dice, usa `git config user.name`; si tampoco hay, deja la celda vacia para que la rellene a mano. **Nunca pongas ahi el nombre del skill, del modelo ni "IA"**: esa tabla es de quien firma, y el generador vacia la celda y avisa si detecta una herramienta.

**Con plantilla**, pasala al generador con `--plantilla <ruta>` y mira tres cosas de su salida, que van al resumen:

- **`avisos`** — los estilos que la plantilla no trae. Esas partes salen **sin formato**, y si no lo dices nadie se entera hasta abrir el documento. Los nombres se resuelven por idioma --una plantilla en espanol trae `Titulo 1` donde el generador pide `Heading 1`--, pero un estilo con nombre propio del cliente no se puede adivinar.
- **`modo`** — `esqueleto` (se escribio dentro de la plantilla) o `generar` (se rehizo el cuerpo). Con `apartados_plantilla` dice cuales reconocio y con `apartados_no_encontrados` los del DF que la plantilla no traia, que salen al final con su titulo. Si esperabas `esqueleto` y sale `generar`, es que la plantilla no rotula sus apartados como esperamos: **diselo al usuario**, porque el documento saldra con la portada del skill y no con la suya.
- **`plantilla_numera`** — si la plantilla ya numera sus titulos. Se deduce mirando **el parrafo y no solo el estilo**, porque Word engancha ahi la numeracion tan a menudo; antes habia que verlo a ojo y salia `1. 1. Introduccion`. Ya no hace falta pasar `numerar_apartados`, aunque el manifiesto sigue mandando si lo dice.
- **`cabecera_pie`** — dice si se heredaron de la plantilla o los genero el skill. Si esperabas el logo del cliente y aqui pone "generados por el skill", es que **la plantilla no traia cabecera**, o que el logo vive en una variante que no se esta usando; diselo al usuario en vez de dar el documento por bueno.
- **Si la plantilla ya numera sus titulos**, pasa `"numerar_apartados": false` en el manifiesto o saldra `1. 1. Introduccion`. Compruebalo en el primer documento, antes de generar veinte.

> **Por que sin plantilla el default es sin marca.** Un DF acaba en manos de un cliente que tiene su propia identidad. Generarlo con la marca de quien lo escribe obliga a rehacerlo; generarlo neutro pero **bien estructurado** permite aplicar cualquier identidad en minutos, porque los colores viven en los estilos y no en cada parrafo.

### 2. Recopilacion de contexto

Lee y consolida, en este orden:

1. `docs/detalle-historias-usuario.md` — la HU, su descripcion, prioridad, estimacion, criterios de aceptacion en formato Dado/Cuando/Entonces, criterios marcados como imprescindibles, notas tecnicas y dependencias.
2. `docs/mapa-historias-usuario.md` — persona/rol, fase (F0/F1/F2...) y a que actividad pertenece.
3. `docs/requisitos.md` — los RF y NFR que la HU realiza; alimentan el alcance.
4. `docs/arquitectura-base.md` — modulos, integraciones, endpoints y la separacion entre frontal y core, que el DF necesita para las secciones 2.2, 2.3 y 2.4.
5. Si existen, `docs/guia-estilos.md` y los prototipos de `booster-ux`, para la seccion de pantallas.
6. **`docs/design/hu/<HU-XX>/referencia.png`**, si el proyecto uso el plugin `aifg`: es **la pantalla exportada de Figma**. Metela en `imagenes` del manifiesto. Es lo que el DF tiene que ensenar --la pantalla-- y no el identificador del nodo, que no le dice nada a nadie fuera del equipo. Si el proyecto no tiene ese arbol, marca la pantalla como `[PENDIENTE]` y genera su fila en Puntos abiertos: dejar la seccion muda es peor.

Si falta alguno de los tres primeros, **avisa de que se genera con menos base** y sigue; si falta el detalle de HU, detente.

### 3. Seleccion de historias

- **Sin argumento**: genera el DF de **todas** las HU del detalle. Antes de escribir nada, **lista las que va a generar y espera confirmacion** — en un proyecto con treinta historias son treinta documentos.
- **Con `HU-XX`**: solo esa. Si el identificador no existe, dilo y lista los validos.
- **Si el `.docx` ya existe**, no lo pises: ve a "Reedicion de un DF existente".

### 4. Estructura del documento

Genera exactamente esta estructura. Es la de los DF de referencia y **el orden importa**, porque es el que espera quien los revisa.

**Portada y control** (antes del indice, sin numerar):

- Titulo: `<NOMBRE DEL PROYECTO>` y, debajo, el titulo de la HU.
- **Control de Versiones** — tabla con `Fecha | Version | Autor | Descripcion del cambio`. En la primera generacion, una fila: fecha de hoy, `1.0`, autor, `Version inicial`.
- **Control de Aprobaciones** — tabla con `Responsable | Cargo | Departamento | Fecha | Version del documento`. Filas vacias para rellenar a mano: **no inventes aprobadores**.
- **Indice** — campo de tabla de contenidos de Word, que se actualiza solo al abrir el documento.

**El titulo del documento lo pone el generador en la portada**, y la portada de una plantilla corporativa **casi nunca es un parrafo con estilo `Title`**: suele ser una tabla --`Titulo del documento | ...`, `Version | ...`, `Fecha | ...`-- o un hueco entre angulos. Buscando solo por estilo no se encontraba nada y el titulo de ejemplo del cliente se entregaba tal cual. Se intentan las tres formas, en este orden:

1. el parrafo con estilo `Title` --y solo si no hay ninguno, el `Subtitle`--;
2. **la tabla de portada**, rellenando por su etiqueta el titulo, el proyecto, la version, la fecha y el autor. Lo que no se reconozca --`Cliente`, `Codigo`-- no se toca, porque eso no lo sabemos;
3. un hueco suelto (`<TITULO DEL DOCUMENTO>`, `{{titulo}}`).

Y ademas en las **propiedades del fichero**, que es lo que Word ensena como titulo. Si no se encuentra ninguna de las tres, se avisa y hay que ponerlo a mano.

**Los comentarios de la plantilla no viajan al DF.** Una plantilla que alguien estuvo redactando trae comentarios de Word --"revisar esto", "hablar con negocio"-- que sirvieron entonces y no pintan nada en un documento que se entrega al cliente: son conversaciones internas de otro equipo y de otro momento. El generador los quita enteros: las marcas del cuerpo, de la cabecera y del pie, y las partes del paquete con el texto y los autores. Quedarse a medias tiene consecuencias en las dos direcciones --dejar `comments.xml` colgando abre el panel de revision con comentarios huerfanos, y quitar solo la parte deja una referencia rota que da error al abrir--, asi que se hacen las dos cosas. Se devuelve cuantas marcas se quitaron en `comentarios_quitados`.

**Y si la plantilla trae control de cambios, se avisa y no se toca.** Aceptar las revisiones cambia el contenido y rechazarlas lo tira: ninguna de las dos es una decision del generador. Pero un DF entregado con marcas de revision se lee como un borrador y ensena quien escribio que, asi que hay que resolverlo en Word antes de entregar.

**La cabecera del cliente se respeta, pero el nombre del documento se actualiza.** El logo, el nombre de la empresa y el formato son de la plantilla y no se tocan; el trozo que **nombra al documento** es del documento, no de la plantilla, y dejarlo tal cual entrega un DF que en cada pagina dice que es otra cosa. Se sustituye lo que se puede reconocer como tal: el titulo que traia la portada --se guarda antes de reemplazarlo, porque suele repetirse en la cabecera-- y las formas de hueco (`TITULO DEL DOCUMENTO`, `<...>`, `{{...}}`). Lo que no encaje en eso no se toca, y lo cambiado se devuelve en `cabecera_actualizada`. **Si la cabecera sigue nombrando otro documento, repasala a mano**: no hay forma de reconocer el nombre propio de un documento ajeno.

**Y el logo sale en todas las paginas.** Una plantilla con "primera pagina distinta" suele traer el logo solo en la cabecera de la portada, y el resto del documento sale sin el --se nota al imprimir--. Si la cabecera de las demas paginas esta vacia, el generador copia la de la portada, con su logo y su relacion de imagen. Si el cliente puso ahi otra cosa, manda la suya y no se toca.

**Cuerpo** (Titulo 1/2/3, **numerado por el generador**):

> Los estilos `Heading` de Word **no numeran solos** --hace falta una lista multinivel vinculada--, asi que el numero va en el texto del titulo y lo pone `gen_df_docx.py`: `1. Introduccion`, `1.1 Alcance`, `2.3.1 Especificas del Frontal`. No los escribas tu en el manifiesto o saldran repetidos.


1. **Introduccion** — que resuelve esta HU y en que contexto. Dos o tres parrafos, derivados de la descripcion de la HU y del requisito que realiza.
   1. **Alcance** — **solo lo que entra**. Nada de "queda fuera X": lo que hace otra historia pertenece al alcance de esa otra historia, y como exclusion aqui se lee como que el producto no lo hara. Tampoco entran las opciones descartadas. Lo que no se pueda acotar es una fila en Puntos abiertos, no una exclusion.
2. **`<Titulo de la HU>`** — abre con la narrativa en tres lineas, tal como aparece en el mapa de historias:
   - `COMO <persona/rol>`
   - `QUIERO <capacidad>`
   - `PARA <beneficio>`
   1. **Filtros/Campos** — tabla con `Nombre | Editable | Oblig | Tipo | Comentario`. Anade la columna **`Entrada/Salida`** cuando la HU implique intercambio con otro sistema. Una fila por campo de la pantalla o del contrato. Si la HU no tiene campos, escribe `N/A`, no borres la seccion.
   2. **Integraciones otros aplicativos** — servicios, endpoints y parametros de entrada y salida, tomados de la arquitectura. Cuando conozcas el contrato, descrbelo (`Parametro de entrada:` / `Parametro de salida:`).
   3. **Validaciones / Reglas / Acciones** — con dos subsecciones de Titulo 3: **Especificas del Frontal** y **Especificas del Core**. Formatos, longitudes, obligatoriedad y reglas de negocio. Si una no aplica, `N/A`.
   4. **Mensajes y avisos** — con tres subsecciones de Titulo 3: **Especificos del Frontal**, **Especificos de Integracion no Core** y **Especificos del Core**. Cada mensaje entre comillas y asociado al campo o condicion que lo dispara.
   5. **Pantallas y Prototipo** — descripcion del flujo paso a paso y de cada pantalla, **con la pantalla insertada**: `docs/design/hu/<HU-XX>/referencia.png` si el proyecto uso `aifg`, o los prototipos de `booster-ux` si los hay. La imagen va en el documento; la ruta o el identificador del nodo, no --a quien lo revisa no le sirven--. Describe ademas lo que la imagen no dice: que pasa al pulsar, que se ve mientras carga, que aparece si no hay resultados.
3. **Criterios de aceptacion** — un parrafo de contexto y despues los escenarios, uno por linea, con la forma `- Escenario <nombre>: <comportamiento esperado>`. Salen de los criterios Dado/Cuando/Entonces del detalle de HU: **traduce, no reinventes**, y marca los imprescindibles.
4. **Especificaciones Tecnicas** — notas tecnicas y dependencias de la HU. Si el detalle no las trae, deja la seccion con la marca de pendiente.
5. **Puntos abiertos** — tabla con `ID | Descripcion | Estado | Responsable | F. Estimada | F. Resolucion`. **Aqui va todo lo que no has podido deducir**: cada hueco del documento genera una fila. Es la seccion que convierte las lagunas en trabajo asignable en vez de en texto inventado.

**Secciones adicionales.** Puedes anadir alguna si el contenido lo pide de verdad — por ejemplo *Glosario* cuando la HU usa terminologia de negocio poco evidente, o *Diagrama de flujo* si hay ramificaciones dificiles de seguir en prosa. Anadelas **despues** de las cinco anteriores y di en el resumen que las has anadido y por que. No inventes secciones para rellenar.

### 5. Como marcar lo que falta

Un DF con huecos honestos es util; uno con relleno plausible es peligroso, porque alguien desarrollara contra el.

- En el cuerpo: `[PENDIENTE: <que falta y quien deberia aportarlo>]`.
- Cuando algo no aplica de verdad: `N/A`. **No confundas ambos**: `N/A` afirma que no hay nada; `[PENDIENTE]` admite que no se sabe.
- Cada `[PENDIENTE]` genera **una fila en Puntos abiertos**, con responsable propuesto si se deduce de la documentacion y `Estado: Abierto`.
- El generador **resalta en amarillo** cada `[PENDIENTE: ...]`, tambien dentro de las celdas de las tablas, y hace lo mismo con las imagenes que no encuentra, con las formas en prosa ("pendiente de definir", "por confirmar", "se desconoce") y con el texto de relleno que traiga la plantilla. **Aun asi, escribe el marcador literal y entre corchetes**: no por el resaltado, que ya no depende de ello, sino porque es lo que dice *que* falta y *quien* deberia aportarlo, y lo que se corresponde con su fila en Puntos abiertos.
- **Los huecos que deja el propio generador tambien salen marcados**: un apartado sin contenido en el manifiesto, la firma del control de versiones cuando se ha vaciado por parecer una herramienta, y el control de aprobaciones cuando se entrega vacio --ahi la marca va una vez debajo de la tabla, no en sus quince celdas--.
- Escribe dentro del corchete **que falta y quien lo aporta**, no solo que falta: `[PENDIENTE: insertar la pantalla exportada de Figma]` es una instruccion accionable para quien abra el documento.
- En el resumen final, di **cuantos puntos abiertos** tiene cada documento. Es el mejor indicador de si el DF esta listo para revisarse.

### 6. Generacion del `.docx`

Construye un manifiesto JSON por HU y pasalo al script:

> **Antes de ejecutar cualquiera de estos scripts, comprueba que la ruta resuelve.** `${CLAUDE_PLUGIN_ROOT}` la define Claude Code; **otros agentes la dejan vacia**, y entonces la orden se convierte en `/skills/...` y falla con `No such file or directory`. Si eso pasa, el script **sigue estando en el disco**: localizalo una vez con `find -L` --por ejemplo en `~/.claude/plugins` o en el directorio de plugins del agente que uses--, quedate con la **ruta absoluta** y usala en todas las invocaciones de esta sesion. **El `-L` no es opcional**: si los skills estan instalados por enlace simbolico --como se montan en algunos agentes-- un `find` a secas no los sigue y devuelve vacio, y concluirias que el script no esta cuando si esta. Si no aparece, aplica la degradacion descrita mas abajo: haz el trabajo segun la prosa y dilo. **Nunca des por hecho que se ejecuto un script que no ejecutaste.**

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/aiba-functional-design/scripts/gen_df_docx.py" \
  --manifest <ruta-al-json> \
  --output "docs/df/<HU-ID> - <Proyecto> - <Titulo>_v<version>.docx"
```

El nombre del fichero sigue el patron de los DF de referencia: `<ID> - <PREFIJO> - <Titulo>_v<version>.docx`. Usa el identificador de la HU como `<ID>` y, si el proyecto tiene un prefijo corto (como `FUS`), usalo; si no, omite ese tramo.

El script devuelve **`codigos_internos`**: cada `RF-xx`, `GAP-xx`, `NFR-xx`, `RN-xx`, `REQ-xx` o `US-xx` que se haya colado en el manifiesto, con la seccion exacta en la que esta. No bloquea la generacion --cortar un lote de veinte HU por una sigla dejaria al analista sin los otros diecinueve documentos--, pero **si la lista no viene vacia, el documento no esta bien**: sustituye cada codigo por lo que significa (ver "Sin codigos internos en el cuerpo") y **vuelve a generar** antes de darlo por entregado. No te limites a mencionarlo en el resumen. `HU-xx` y `PA-xx` no se marcan: son legitimos.

Y devuelve **`relleno_sin_sustituir`**: el texto de relleno de la plantilla que ha quedado en el documento --`<RELLENAR ...>`, `Lorem ipsum`, `TITULO DEL DOCUMENTO`, `{{campo}}`, `TBD`--, con el apartado en el que esta. **No se borra**: un apartado propio del cliente puede tener que rellenarse de verdad, y borrarlo dejaria el DF sin ese hueco. Va **resaltado en amarillo**, como todo lo que completa una persona. Si la lista no viene vacia, **resuelvelo antes de dar el DF por entregado** --escribiendo el contenido que falta o preguntando al analista-- y dilo en el resumen. Un DF entregado con el "TITULO DEL DOCUMENTO" de la plantilla todavia puesto es lo que se reporto.

**El manifiesto se normaliza antes de escribir.** No todos los modelos escriben la misma estructura, y una diferencia de forma no puede dejar sin DF a las veinte historias del lote. `campos` vale como `{"columnas": [...], "filas": [[...]]}` --la forma buena, y la que debes escribir--, como lista de diccionarios (las columnas salen de las claves), como lista de listas o como texto suelto. `validaciones`, `mensajes` y `criterios_aceptacion` valen tambien como lista o como texto. Antes solo valia una forma y las demas reventaban la generacion entera con `'list' object has no attribute 'get'`.

**Y un apartado vacio no sale mudo.** Si `campos` no viene, Filtros y Campos no se queda con una tabla de solo cabecera --que se lee como "aqui no habia nada que decir"-- sino con la marca de pendiente resaltada, y se avisa: es un apartado que casi siempre tiene contenido, asi que lo normal es que falte en el detalle de la HU o que el manifiesto no lo recogiera.

El script devuelve tambien **`vinetas`**, que dice de donde sale el punto de cada lista: `plantilla` si lo pone un estilo del cliente --lo normal y lo deseable--, `creada` si la plantilla no traia ninguno que numerase y el generador ha anadido la numeracion, y `literal` si ni siquiera eso ha sido posible y el punto va escrito en el texto. Los dos ultimos casos no son errores y no hay que rehacer nada, pero **si sale `literal`, dilo en el resumen**: esas listas se ven bien pero no se comportan como una lista de Word al editarlas.

El script se encarga de los estilos, la cabecera y el pie, el indice y las tablas. **No generes el `.docx` por otros medios**: el valor de este skill es que todos los DF salgan con la misma estructura y los mismos estilos, y eso solo se sostiene si hay un unico generador.

Si `python3` no esta disponible, dilo y ofrece dejar el contenido en Markdown para convertirlo despues; no intentes fabricar OOXML a mano.

**Para leer un DF ya generado** —propio o del cliente— el mismo script lo vuelca a JSON con sus secciones, parrafos y tablas:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/aiba-functional-design/scripts/gen_df_docx.py" \
  --extraer "docs/df/<fichero>.docx"
```

Lo usa `aiba test-plan`, para el que este DF es su mejor fuente de casos de prueba.

### 7. Reedicion de un DF existente

Si el `.docx` ya existe, **no lo regeneres desde cero**: perderias el trabajo del analista.

1. Lee el documento existente y extrae su **control de versiones** y las secciones que contengan texto que no provenga de la generacion automatica.
2. Muestra al usuario **que ha cambiado** en la documentacion de origen desde la ultima version del DF (criterios nuevos, campos nuevos, integraciones nuevas) y **que se propone tocar**.
3. Con su confirmacion, regenera **solo las secciones afectadas** y conserva el resto literal.
4. **Anade una fila al control de versiones**: fecha de hoy, version incrementada (`1.0` -> `1.1`), autor y una descripcion concreta del cambio. Nunca sobrescribas la fila anterior: el historial es la razon de ser de esa tabla.
5. Si el analista habia escrito a mano en una seccion que ahora toca regenerar, **preguntale antes** en lugar de decidir tu. Ese texto es lo mas valioso del documento.

### 8. Resumen final

Informa de:

- HU procesadas y ruta de cada `.docx` generado o actualizado.
- Marca aplicada (ninguna, plantilla, carpeta o URL), de donde salieron los colores y **si la cabecera y el pie se heredaron** de la plantilla.
- **Puntos abiertos por documento**, que es lo que dice si esta listo para revisar, y **cuantas marcas en amarillo** quedan por resolver.
- **Codigos internos** que devolvio el generador y que has corregido, o los que queden y por que.
- Secciones adicionales anadidas, si las hubo, y por que.
- Documentos de origen que faltaban y como afecto eso al resultado.
- Recordatorio de que el DF esta **pendiente de revision del analista**.

## Diseno del documento

El documento se genera **sin marca** salvo peticion expresa, pero **nunca sin estructura**. La diferencia importa: un documento neutro bien estructurado admite cualquier identidad visual en minutos; uno con el formato aplicado a mano parrafo a parrafo hay que rehacerlo entero.

Concretamente:

- **Estilos nativos de Word** (`Heading 1/2/3`, `Normal`, `List Paragraph`) en vez de formato directo. Cambiar la paleta es entonces cambiar el estilo, no repasar el documento.
- **Estilo de tabla con nombre**, comun a las cinco tablas, con fila de cabecera diferenciada.
- **Cabecera y pie editables**: la cabecera lleva el nombre del proyecto y el titulo del documento; el pie, la version y el numero de pagina. Ambos como campos de Word, no como texto fijo.
- **Indice como campo `TOC`**, que Word actualiza solo. No lo escribas a mano: quedaria desfasado en cuanto alguien anada una seccion.
- **Sin logotipos** por defecto. Si el usuario aporta uno, va en la cabecera, no incrustado en la portada como imagen suelta.

Con esto, aplicar despues una identidad corporativa es modificar los estilos del documento o adjuntarle una plantilla `.dotx`, sin tocar el contenido.

## Verificacion final

Al terminar, informa:

- Comando ejecutado (`aiba functional-design`) y **que HU** se han documentado.
- **Rutas de los `.docx` generados** en `docs/df/`, una por HU. Sin esto el usuario no sabe donde ha quedado el entregable.
- **Decision de marca** y su origen: sin marca (default), carpeta local, URL o **plantilla del cliente**, y que se extrajo de ella. Es la unica eleccion real del comando y la que mas cambia el resultado.
- **Con plantilla: los `avisos` que devolvio el generador** --estilos que la plantilla no traia-- y si se desactivo la numeracion. Sin esto, un documento con partes sin formato pasa por bueno.
- **`cabecera_pie`**: si salieron de la plantilla o los escribio el skill. Es la comprobacion de que el logo del cliente esta donde tiene que estar.
- **`codigos_internos`**: vacio, o que se corrigio. Un DF con `GAP-07` en el cuerpo no es entregable a negocio.
- **Si se inserto la pantalla** y de donde salio (`aifg` o `booster-ux`), o por que no hay ninguna.
- **Puntos abiertos** que han quedado en cada documento: cuantos y de que tipo. Son el trabajo que el DF deja pendiente, no un detalle de formato.
- **Documentacion de origen que faltaba** y con que se ha suplido, si aplica.
- Recordatorio: el `.docx` es el entregable para negocio; la fuente de verdad sigue siendo `docs/detalle-historias-usuario.md`.

> **Sin auditoria estructurada.** Como el resto de skills de AIBA, este no escribe en `openspec/audit/`. A diferencia de ellos, tampoco puede dejar sus decisiones dentro del entregable: el DF es un documento para negocio, y una seccion de decisiones internas no pinta nada ahi. Por eso **la traza vive en esta verificacion final**, y por eso la decision de marca se reporta siempre, tambien cuando se tomo el default.

## Siguiente paso sugerido

- Revisar el `.docx` con negocio y resolver los **Puntos abiertos** que haya dejado.
- Si la revision cambia la HU, el cambio va a `docs/detalle-historias-usuario.md` (`aidd user-story-details`) y despues se regenera el DF: **no edites el `.docx` a mano**, porque la proxima generacion lo sobrescribe.
- **`aiba test-plan HU-XX`** para derivar el plan de pruebas de la historia. Este DF es su mejor fuente: sus validaciones y sus mensajes son casos de prueba casi literales, y sus puntos abiertos dicen que **no** se puede probar todavia.
- Si el proyecto ya tiene roadmap, el DF no lo altera: sigue con `aisdd open change` para la fase que corresponda.

