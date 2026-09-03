---
name: aifg-capture
description: AIFG (AI Figma) — extrae el diseno de un archivo de Figma y lo deja vinculado a la historia de usuario que lo implementa, mediante el comando `aifg capture`. Normaliza los nodos en definiciones de componente reutilizables y un mapa de composicion por HU, exporta la imagen de cada frame y de cada componente como canal de verificacion, y resuelve el vinculo HU <-> diseno presentando al humano solo lo que no admite duda. El modelo esta fraccionado a proposito para que implementar una pantalla no cueste abrir el arbol entero: el mapa es corto y las definiciones se cargan solo cuando el change las toca. Habla con Figma solo por MCP, sin llamadas REST ni gestion de credenciales. Ningun artefacto se edita a mano. Este `SKILL.md` es un indice: el detalle vive en `references/*.md` y se lee bajo demanda. Usar cuando el usuario invoque `aifg capture` o pida extraer, capturar o vincular un diseno de Figma a las historias de usuario.
metadata:
  author: NTT DATA Spain GDN-e
  version: "0.1.0"
---

# aifg-capture (AI Figma — extraccion)

Extrae el diseno de Figma y lo deja donde el que implementa lo va a encontrar: **colgando de la HU**.

## Por que existe

`docs/guia-estilos.md` describe un **sistema** --paleta, tipografia, tokens, componentes-- pero no describe **pantallas**. Ningun conjunto de tokens correctos reproduce una composicion: que va donde, con cuanto espacio, en que jerarquia, con que estados. Ese hueco es la razon de que el front implementado no se parezca al disenado.

La HU es la clave de indexacion porque **ya es el eje del que cuelga todo lo demas**: Story de Jira por HU, change como sub-tarea de esa Story, `plan-revision-hu`, `sprint-plan` y el `change_hint` que los engancha.

## Dos premisas

**Este plugin es opcional y aditivo.** Sin el, `aisdd implement change` tira de `docs/guia-estilos.md` y, si tampoco la hay, improvisa. Nada del nucleo depende de que AIFG este instalado, y ningun skill de AIDD cambia por su culpa.

**Cuando el dev trabaja, el diseno esta aprobado y cerrado.** No se implementa contra un blanco movil. Un diseno que cambia a mitad de implementacion no es un caso a sincronizar automaticamente: es una **incidencia**, y se resuelve con una tarea aparte. Por eso **no hay ninguna comprobacion automatica contra Figma**: el disparo siempre es humano.

## Que leer para cada cosa

Este `SKILL.md` es el **indice**. El detalle vive en `references/` y se lee **bajo demanda**, no entero.

| Para | Lee |
|---|---|
| Entender los artefactos, el registro y las reglas que no se rompen | `references/model.md` |
| Extraer: que se guarda de cada nodo, identidad, agrupacion, overrides, estados, capturas | `references/extraction.md` |
| Resolver que diseno corresponde a que HU | `references/binding.md` |
| Hablar con Figma | `references/mcp.md` |
| Actualizar piezas cuando el diseno cambia | El skill hermano `aifg-update` |

## `aifg capture`

Extraccion masiva: recorre el archivo de Figma y deja el arbol completo bajo `docs/design/`.

1. **Comprueba el acceso a Figma.** Sin MCP no hay extraccion posible; ver `references/mcp.md`. Si no lo hay, **detente y dilo** en vez de producir un arbol a medias.
2. **Pide el enlace del archivo** y lee su estructura: paginas, frames, componentes publicados.
3. **Exporta las miniaturas de los frames.** Van antes de vincular, no despues: la tabla del paso siguiente **se decide mirando**, y con los nombres de frame a secas nadie puede.
4. **Resuelve el vinculo HU <-> diseno** segun `references/binding.md`. Lo que no admite duda se resuelve solo; lo demas se le presenta al humano con su miniatura al lado.
5. **Extrae y normaliza** lo que quedo vinculado, segun `references/extraction.md`: definiciones de componente una sola vez, un mapa de composicion por HU, y la imagen de cada componente. **Extraer despues de vincular** evita destripar frames que ninguna HU reclama.
6. **Escribe el arbol** segun `references/model.md`, con la cabecera de generado, el hash y la fecha en cada fichero. Cada referencia a un componente guarda ademas **el hash del componente contra el que se construyo**: es lo que permite despues saber si un mapa quedo desactualizado.
7. **Reporta lo que importa y no se ve solo**:
   - Cuantos componentes cayeron a **node id** por no estar publicados en una libreria. Es el modo fragil, y hay que estar en el sabiendolo.
   - Cuantas instancias tienen **overrides estructurales**, que casi siempre significan que falta una variante del componente.
   - **HU sin diseno** y **disenos que ninguna HU reclama**. El segundo suele ser un hueco de requisitos o algo muerto en el Figma.
   - El peso del arbol, separando JSON e imagenes.
8. **Di donde queda todo y quien lo consume**: `aisdd implement change` lo encuentra solo por la ruta, sin que la HU lleve ninguna referencia.

## Lo que no haces nunca

- **Editar a mano un artefacto generado.** Si algo esta mal, se corrige en Figma y se vuelve a capturar. Un JSON parcheado a mano se pierde en la siguiente pasada, en silencio.
- **Escribir nada en `docs/detalle-historias-usuario.md`.** El cuerpo de cada HU es client-ready y no lleva rastro de AIFG: ni puntero, ni referencia, ni nota. La busqueda va al reves, del id de la HU al registro.
- **Inventar lo que el diseno no dice.** Si no hay variantes de estado, no hay estados. Si no hay componentes publicados, no hay `key`. Se trabaja con lo que hay y **se dice en que modo se esta**.
- **Llamar a la API REST de Figma** ni manejar tokens. Solo MCP; ver `references/mcp.md`.
