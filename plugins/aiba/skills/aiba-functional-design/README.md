# aiba-functional-design

Genera el **Documento de Diseño Funcional (DF)** en Word de cada historia de usuario, a partir de la documentación que produce AIDD.

```text
aiba functional-design          # todas las HU
aiba functional-design HU-03    # solo esa
```

Alias: `aiba df`, `aiba diseño funcional`.

## Qué produce

Un `.docx` por HU en `docs/df/`, con la estructura de los DF de referencia:

| | Sección |
|---|---|
| — | Portada, **Control de Versiones**, **Control de Aprobaciones**, Índice |
| 1 | Introducción → 1.1 Alcance |
| 2 | La HU (COMO / QUIERO / PARA) → 2.1 Filtros/Campos · 2.2 Integraciones · 2.3 Validaciones (Frontal/Core) · 2.4 Mensajes y avisos (Frontal / Integración no Core / Core) · 2.5 Pantallas y Prototipo |
| 3 | Criterios de aceptación |
| 4 | Especificaciones Técnicas |
| 5 | Puntos abiertos |

Se pueden añadir secciones extra (un *Glosario*, un *Diagrama de flujo*) cuando el contenido lo pida; van después de las cinco anteriores.

## De dónde saca el contenido

La fuente de verdad es **`docs/detalle-historias-usuario.md`**. Sin él no hay DF que escribir, solo una plantilla vacía: el comando se detiene y remite a `aidd user-story-details`.

Complementa con `mapa-historias-usuario.md` (persona y fase), `requisitos.md` (los RF/NFR que la HU realiza), `arquitectura-base.md` (integraciones y separación frontal/core) y, si existen, la guía de estilos y los prototipos de `booster-ux`.

## Lo que no hace

**No inventa.** Un DF se firma y se desarrolla contra él, así que lo que no se deduce de la documentación se marca como `[PENDIENTE: ...]` y **genera una fila en Puntos abiertos**. Esa tabla convierte las lagunas en trabajo asignable en vez de en texto plausible. El resumen final dice cuántos puntos abiertos tiene cada documento, que es el mejor indicador de si está listo para revisarse.

**Lo que se enumera sale como lista.** En cuanto hay más de dos elementos —validaciones, mensajes, campos, integraciones, pasos de un flujo— va uno por línea como viñeta de Word, no metido en un párrafo separado por comas. Quien revisa el DF necesita poder señalar el tercer elemento, y para eso tiene que existir como elemento.

Y la viñeta sale **con la plantilla que sea**. El estilo se acepta solo si numera de verdad: `Párrafo de lista` sangra pero no pone punto, así que tomarlo por un estilo de lista dejaba el documento corrido aunque el nombre prometiera otra cosa. Si la plantilla del cliente no trae ninguno que numere, el generador añade la numeración al documento.

Cada `[PENDIENTE: ...]` sale **resaltado en amarillo**, también dentro de las tablas. Un DF de veinte páginas se lee en diagonal, y un hueco sin resaltar acaba firmado como si fuera contenido.

Ojo a la diferencia entre `N/A` y `[PENDIENTE]`: el primero afirma que no hay nada; el segundo admite que no se sabe.

**No cuenta lo que no es.** El apartado de Alcance dice **solo lo que entra**: lo que hace otra historia pertenece al alcance de esa otra historia, y listarlo aquí como exclusión se lee como que el producto no lo hará. Tampoco aparecen las opciones descartadas —quien revisa no distingue "descartado" de "pendiente" y acaba preguntando por algo que nadie va a construir—.

**No usa códigos internos.** Ni `RF-014` ni `GAP-07`: se explica el contenido, que es lo que le dice algo a un lector de negocio. El generador devuelve `codigos_internos` con cada sigla que se haya colado y en qué sección está, para corregirla y volver a generar. `HU-xx` sí se queda: da nombre al fichero y engancha con `aiba test-plan` y con Jira.

**El título y el logo no se quedan a medias.** El título se escribe donde esté: en el párrafo con estilo `Título`, en la **tabla de portada** —que es como vienen las plantillas corporativas, y donde además se ponen al día la versión, la fecha y el autor— o en un hueco entre ángulos. Y también en las propiedades del fichero y en la cabecera y el pie, donde la plantilla suele repetirlo. El logo, el nombre de la empresa y el formato de la cabecera no se tocan: solo el trozo que nombra al documento. Y si la plantilla trae el logo solo en la cabecera de la portada, como es habitual, se copia a la del resto de páginas cuando está vacía: así sale en todas.

**Lo que falta se ve, lo escriba quien lo escriba.** Se resalta en amarillo el marcador `[PENDIENTE: ...]` y también las formas en prosa —«pendiente de definir», «por confirmar», «se desconoce»—, además de los huecos que deja el propio generador: un apartado sin contenido, la firma vaciada del control de versiones y el control de aprobaciones cuando se entrega vacío. Antes solo se resaltaba el marcador literal, así que el mismo documento salía con los huecos visibles o invisibles según qué modelo lo hubiera redactado.

**La carpeta del proyecto queda limpia.** Lo que la herramienta se fabrique para trabajar —scripts de cualquier lenguaje, `package.json`, `node_modules/`, entornos virtuales, ficheros intermedios— se escribe en un directorio temporal, nunca en el proyecto. En la carpeta del DF solo van los `.docx`.

**El resultado no depende de qué modelo escriba el manifiesto.** Los apartados tabulares se aceptan en varias formas —objeto con columnas y filas, lista de diccionarios, lista de listas o texto— porque no todos los modelos escriben la misma estructura, y antes una diferencia de forma reventaba la generación de todo el lote. Y un apartado que no llega no sale con una tabla vacía: sale con la marca de pendiente y un aviso.

**Los comentarios de la plantilla se van.** Las notas de Word con las que alguien redactó la plantilla —«revisar esto», «hablar con negocio»— se eliminan enteras: las marcas del cuerpo, de la cabecera y del pie, y las partes del paquete. No son contenido del documento que firma el cliente. Si además la plantilla trae control de cambios, se avisa: aceptarlo o rechazarlo es decisión de una persona.

**El relleno de la plantilla se canta.** Lo que quede sin sustituir —`<RELLENAR ...>`, `Lorem ipsum`, `TÍTULO DEL DOCUMENTO`, `TBD`— sale resaltado en amarillo y se devuelve con el apartado en el que está. No se borra: un apartado propio del cliente puede tener que rellenarse de verdad.

**No firma por ti.** En el Control de Versiones va el analista que responde del documento ante el cliente. El generador vacía la celda y avisa si detecta ahí el nombre de una herramienta.

## Diseño: genérico, pero estructurado

El comando **pregunta antes de generar nada** con qué aspecto sale el documento. Si el cliente tiene una **plantilla `.docx`/`.dotx`**, esa es la respuesta.

Una plantilla de cliente no suele ser un juego de estilos: es el documento entero montado, con su portada, su logo, sus tablas de control, su índice y sus apartados numerados. Cuando el generador reconoce esos apartados entra en **modo esqueleto** y **escribe dentro de ellos**, sustituyendo solo el texto de ejemplo. Todo lo demás se queda intacto porque nunca se toca. Si la plantilla no trae apartados reconocibles, se usa por sus estilos y el cuerpo se escribe entero —y el resumen lo dice, para que nadie descubra en la página uno que salió la portada equivocada—.

Sin plantilla, el documento sale **sin logotipos ni colores corporativos**, con la opción de aplicar una marca desde una carpeta local o desde una URL.

La razón es práctica: un DF acaba en manos de un cliente que tiene su propia identidad. Generarlo con la marca de quien lo escribe obliga a rehacerlo. Generarlo neutro **pero bien estructurado** permite aplicar cualquier identidad en minutos, porque:

- Se usan **estilos nativos de Word** (`Heading 1/2/3`, `Normal`, `List Bullet`) en vez de formato directo, así que cambiar la paleta es cambiar el estilo.
- Las cinco tablas comparten estilo con fila de cabecera diferenciada.
- **Cabecera y pie son editables** y llevan campos de Word, no texto fijo —salvo que vengan de una plantilla, que entonces manda ella—.
- El **índice es un campo `TOC`** que Word actualiza solo.

Cuando se aporta una marca, los colores se aplican **a los estilos** y el logo va a la cabecera, no incrustado suelto en la portada.

## Leer un DF ya escrito

El mismo script vuelca a JSON las secciones, párrafos y tablas de un `.docx` —propio o del cliente—, que de otro modo no se puede leer:

> **Antes de ejecutar cualquiera de estos scripts, comprueba que la ruta resuelve.** `${CLAUDE_PLUGIN_ROOT}` la define Claude Code; **otros agentes la dejan vacia**, y entonces la orden se convierte en `/skills/...` y falla con `No such file or directory`. Si eso pasa, el script **sigue estando en el disco**: localizalo una vez con `find -L` --por ejemplo en `~/.claude/plugins` o en el directorio de plugins del agente que uses--, quedate con la **ruta absoluta** y usala en todas las invocaciones de esta sesion. **El `-L` no es opcional**: si los skills estan instalados por enlace simbolico --como se montan en algunos agentes-- un `find` a secas no los sigue y devuelve vacio, y concluirias que el script no esta cuando si esta. Si no aparece, aplica la degradacion descrita mas abajo: haz el trabajo segun la prosa y dilo. **Nunca des por hecho que se ejecuto un script que no ejecutaste.**

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/aiba-functional-design/scripts/gen_df_docx.py" \
  --extraer "docs/df/<fichero>.docx"
```

Lo consume `aiba test-plan`: las tablas de validaciones y mensajes de un DF ya son casos de prueba casi literales.

## Reedición

Si el `.docx` ya existe no se regenera desde cero. Se muestra qué ha cambiado en la documentación de origen, se regeneran **solo las secciones afectadas** y se **añade una fila** al control de versiones (`1.0` → `1.1`) sin sobrescribir el historial. Si el analista había escrito a mano en una sección que toca regenerar, se pregunta antes: ese texto es lo más valioso del documento.

## Requisitos

Python 3 y `python-docx`, que el script instala solo si falta. Si no puede, lo dice y no bloquea el resto del trabajo.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/aiba-functional-design/scripts/gen_df_docx.py" --schema
```

## Relación con AIDD

`aiba` es la capa que da la cara ante el negocio, y este skill es su pieza de **análisis funcional**. **Consume** lo que produce AIDD sin modificarlo: lee `docs/` y escribe únicamente en `docs/df/`. Le acompañan en el plugin `aiba hu-review-plan`, `aiba project-plan`, `aiba sprint-planning` y `aiba metrics`, que vivían en `aidd` hasta la v1.8.0 del marketplace.
