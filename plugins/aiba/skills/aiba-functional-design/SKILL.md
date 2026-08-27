---
name: aiba-functional-design
description: AIBA (AI Business Analyst) — genera el Documento de Diseno Funcional (DF) en Word de cada historia de usuario, mediante el comando `aiba functional-design` (alias `aiba df`, `aiba diseno funcional`). Lee `docs/detalle-historias-usuario.md` como fuente de verdad y produce un `.docx` por HU en `docs/df/`, con la estructura acordada: portada, control de versiones, control de aprobaciones, indice, introduccion y alcance, la HU con su narrativa COMO/QUIERO/PARA, tabla de filtros y campos, integraciones con otros aplicativos, validaciones y reglas separadas por frontal y core, mensajes y avisos, pantallas y prototipo, criterios de aceptacion, especificaciones tecnicas y puntos abiertos. El diseno es **generico y sin marca**: usa estilos nativos de Word (Titulo 1/2/3, estilo de tabla, cabecera y pie editables) para que una paleta corporativa y un logo se apliquen despues sin rehacer nada, y **pregunta antes** si se desea aplicar una marca concreta, tomandola de una carpeta local o de una URL. Funciona sobre **todas las HU o una sola** (`aiba functional-design HU-03`), y **reedita** un DF ya generado conservando su historial de versiones y las secciones que el analista haya escrito a mano. Usar cuando el usuario pida "genera los DF", "documento de diseno funcional", "el DF de la HU-05", "actualiza el DF", o equivalentes.
metadata:
  author: NTT DATA Spain GDN-e
  version: "0.1.0"
---

# aiba-functional-design (AIBA · Diseno Funcional)

Usa este skill cuando el usuario quiera generar o actualizar documentos de **Diseno Funcional (DF)** a partir de las historias de usuario ya detalladas. Comandos:

- `aiba functional-design [HU-XX]`
- Alias: `aiba df [HU-XX]`, `aiba diseno funcional [HU-XX]`

Responde y documenta en espanol. Conserva en ingles nombres de comandos, ficheros, rutas y terminos tecnicos establecidos.

## Que es AIBA y donde encaja este skill

**AIBA** (AI Business Analyst) es el conjunto de skills de **analisis funcional**: el trabajo que traduce lo que el negocio necesita en un documento que un equipo de desarrollo puede implementar y un cliente puede firmar.

Hoy AIBA contiene solo este skill. Mas adelante se le moveran algunos de los que viven en `aidd`, porque pertenecen mas al analisis que a la planificacion. Mientras tanto, **este skill consume lo que produce AIDD** y no lo sustituye:

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
- Este documento requiere revision humana. Al terminar, deja claro que esta pendiente de revision del analista.

## Flujo del comando

### 1. Marca corporativa (preguntar SIEMPRE, antes de generar nada)

Antes de leer documentacion o generar ficheros, **pregunta al usuario si quiere aplicar una marca**. Es lo primero porque condiciona todo el resto y porque rehacer veinte documentos por no haber preguntado es caro.

Usa `AskUserQuestion` si la plataforma lo soporta, con estas opciones:

1. **Sin marca `(Recomendada)`** — estilos nativos de Word, sin logo y con la paleta por defecto. El documento queda listo para que cualquiera le aplique despues su identidad visual sin rehacerlo.
2. **Marca desde una carpeta local** — pide la ruta y busca en ella el logo (`.png`, `.jpg`, `.svg`) y, si existe, un fichero de tokens o guia de estilos del que extraer los colores.
3. **Marca desde una URL** — pide la URL de la web corporativa o de la guia de marca, y extrae de ahi el logo y los colores dominantes.

Si el usuario elige 2 o 3, pide ademas lo que no puedas deducir: **color principal**, **color secundario** y **texto de cabecera y pie**. Confirma lo detectado antes de usarlo; no des por buena una paleta extraida automaticamente sin ensenarla.

En modo no interactivo, toma **sin marca** y registralo como supuesto.

> **Por que el default es sin marca.** Un DF suele acabar en manos de un cliente que tiene su propia identidad. Generarlo con la marca de quien lo escribe obliga a rehacerlo; generarlo neutro pero **bien estructurado** permite aplicar cualquier identidad en minutos, porque los colores viven en los estilos y no en cada parrafo.

### 2. Recopilacion de contexto

Lee y consolida, en este orden:

1. `docs/detalle-historias-usuario.md` — la HU, su descripcion, prioridad, estimacion, criterios de aceptacion en formato Dado/Cuando/Entonces, criterios marcados como imprescindibles, notas tecnicas y dependencias.
2. `docs/mapa-historias-usuario.md` — persona/rol, fase (F0/F1/F2...) y a que actividad pertenece.
3. `docs/requisitos.md` — los RF y NFR que la HU realiza; alimentan el alcance.
4. `docs/arquitectura-base.md` — modulos, integraciones, endpoints y la separacion entre frontal y core, que el DF necesita para las secciones 2.2, 2.3 y 2.4.
5. Si existen, `docs/guia-estilos.md` y los prototipos de `booster-ux`, para la seccion de pantallas.

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

**Cuerpo** (numerado con Titulo 1/2/3):

1. **Introduccion** — que resuelve esta HU y en que contexto. Dos o tres parrafos, derivados de la descripcion de la HU y del requisito que realiza.
   1. **Alcance** — que entra y que **no** entra. Lo que no entra es tan importante como lo que entra: si el detalle de HU lo declara, traelo; si no, marca lo que quede por acotar.
2. **`<Titulo de la HU>`** — abre con la narrativa en tres lineas, tal como aparece en el mapa de historias:
   - `COMO <persona/rol>`
   - `QUIERO <capacidad>`
   - `PARA <beneficio>`
   1. **Filtros/Campos** — tabla con `Nombre | Editable | Oblig | Tipo | Comentario`. Anade la columna **`Entrada/Salida`** cuando la HU implique intercambio con otro sistema. Una fila por campo de la pantalla o del contrato. Si la HU no tiene campos, escribe `N/A`, no borres la seccion.
   2. **Integraciones otros aplicativos** — servicios, endpoints y parametros de entrada y salida, tomados de la arquitectura. Cuando conozcas el contrato, descrbelo (`Parametro de entrada:` / `Parametro de salida:`).
   3. **Validaciones / Reglas / Acciones** — con dos subsecciones de Titulo 3: **Especificas del Frontal** y **Especificas del Core**. Formatos, longitudes, obligatoriedad y reglas de negocio. Si una no aplica, `N/A`.
   4. **Mensajes y avisos** — con tres subsecciones de Titulo 3: **Especificos del Frontal**, **Especificos de Integracion no Core** y **Especificos del Core**. Cada mensaje entre comillas y asociado al campo o condicion que lo dispara.
   5. **Pantallas y Prototipo** — descripcion del flujo paso a paso y de cada pantalla. Si hay prototipos de `booster-ux`, referencia sus rutas e inserta las imagenes si estan disponibles.
3. **Criterios de aceptacion** — un parrafo de contexto y despues los escenarios, uno por linea, con la forma `- Escenario <nombre>: <comportamiento esperado>`. Salen de los criterios Dado/Cuando/Entonces del detalle de HU: **traduce, no reinventes**, y marca los imprescindibles.
4. **Especificaciones Tecnicas** — notas tecnicas y dependencias de la HU. Si el detalle no las trae, deja la seccion con la marca de pendiente.
5. **Puntos abiertos** — tabla con `ID | Descripcion | Estado | Responsable | F. Estimada | F. Resolucion`. **Aqui va todo lo que no has podido deducir**: cada hueco del documento genera una fila. Es la seccion que convierte las lagunas en trabajo asignable en vez de en texto inventado.

**Secciones adicionales.** Puedes anadir alguna si el contenido lo pide de verdad — por ejemplo *Glosario* cuando la HU usa terminologia de negocio poco evidente, o *Diagrama de flujo* si hay ramificaciones dificiles de seguir en prosa. Anadelas **despues** de las cinco anteriores y di en el resumen que las has anadido y por que. No inventes secciones para rellenar.

### 5. Como marcar lo que falta

Un DF con huecos honestos es util; uno con relleno plausible es peligroso, porque alguien desarrollara contra el.

- En el cuerpo: `[PENDIENTE: <que falta y quien deberia aportarlo>]`.
- Cuando algo no aplica de verdad: `N/A`. **No confundas ambos**: `N/A` afirma que no hay nada; `[PENDIENTE]` admite que no se sabe.
- Cada `[PENDIENTE]` genera **una fila en Puntos abiertos**, con responsable propuesto si se deduce de la documentacion y `Estado: Abierto`.
- En el resumen final, di **cuantos puntos abiertos** tiene cada documento. Es el mejor indicador de si el DF esta listo para revisarse.

### 6. Generacion del `.docx`

Construye un manifiesto JSON por HU y pasalo al script:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/aiba-functional-design/scripts/gen_df_docx.py" \
  --manifest <ruta-al-json> \
  --output "docs/df/<HU-ID> - <Proyecto> - <Titulo>_v<version>.docx"
```

El nombre del fichero sigue el patron de los DF de referencia: `<ID> - <PREFIJO> - <Titulo>_v<version>.docx`. Usa el identificador de la HU como `<ID>` y, si el proyecto tiene un prefijo corto (como `FUS`), usalo; si no, omite ese tramo.

El script se encarga de los estilos, la cabecera y el pie, el indice y las tablas. **No generes el `.docx` por otros medios**: el valor de este skill es que todos los DF salgan con la misma estructura y los mismos estilos, y eso solo se sostiene si hay un unico generador.

Si `python3` no esta disponible, dilo y ofrece dejar el contenido en Markdown para convertirlo despues; no intentes fabricar OOXML a mano.

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
- Marca aplicada (ninguna, carpeta o URL) y de donde salieron los colores.
- **Puntos abiertos por documento**, que es lo que dice si esta listo para revisar.
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
