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

Ojo a la diferencia entre `N/A` y `[PENDIENTE]`: el primero afirma que no hay nada; el segundo admite que no se sabe.

## Diseño: genérico, pero estructurado

El documento sale **sin logotipos ni colores corporativos**, y el comando **pregunta antes** si quieres aplicar una marca —desde una carpeta local o desde una URL— con la opción de no aplicar ninguna como recomendada.

La razón es práctica: un DF acaba en manos de un cliente que tiene su propia identidad. Generarlo con la marca de quien lo escribe obliga a rehacerlo. Generarlo neutro **pero bien estructurado** permite aplicar cualquier identidad en minutos, porque:

- Se usan **estilos nativos de Word** (`Heading 1/2/3`, `Normal`, `List Bullet`) en vez de formato directo, así que cambiar la paleta es cambiar el estilo.
- Las cinco tablas comparten estilo con fila de cabecera diferenciada.
- **Cabecera y pie son editables** y llevan campos de Word, no texto fijo.
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
