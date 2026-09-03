---
name: aifg-update
description: AIFG (AI Figma) — re-captura piezas concretas del diseno cuando cambian, mediante el comando `aifg update`. Regenera la definicion de un componente o el mapa de una HU, actualiza el hash y la fecha, **detecta los overrides que quedan huerfanos** cuando el molde pierde una propiedad que una instancia sobreescribia, y reporta que historias de usuario quedan afectadas separando las que ya estan cerradas. El disparo es siempre humano: no hay comprobacion automatica contra Figma, porque cuando el dev trabaja el diseno esta aprobado y cerrado, y un cambio a mitad de implementacion es una incidencia y no una sincronizacion. Comparte modelo, esquema de extraccion y acceso por MCP con el skill `aifg-capture`. Usar cuando el usuario invoque `aifg update` o diga que el equipo de diseno ha cambiado un componente, un frame o una pantalla ya capturada.
metadata:
  author: NTT DATA Spain GDN-e
  version: "0.1.0"
---

# aifg-update (AI Figma — actualizacion quirurgica)

Re-captura lo que cambio, y **dice a quien le afecta**.

## Cuando se ejecuta

**Cuando una persona lo dice.** El diseno cambia, el disenador avisa al dev, y el dev lanza este comando. **No hay ningun chequeo automatico contra Figma** en este plugin ni en ningun comando del nucleo.

Eso no es un olvido, es la premisa: **cuando el dev trabaja, el diseno esta aprobado y cerrado**. El arbol capturado es la verdad hasta que alguien diga lo contrario. Si nadie avisa, el cambio no existe.

> **Lo que esto cuesta, dicho para que nadie se sorprenda:** el dev implementa desde el arbol **precisamente para no abrir Figma**, asi que no va a notar por su cuenta un cambio no anunciado. Hay tres casos donde nadie avisa: un **componente** cambiado para otra HU que se propaga a la suya; un cambio ocurrido **entre la extraccion y el sprint** que implementa esa HU, que pueden ser meses; y los ajustes de espaciado, que son los que menos se anuncian y mas se notan en el resultado.

## Que leer

El modelo, el esquema de extraccion y el acceso a Figma son **los mismos** que en `aifg-capture`. No los repitas ni los reinventes:

| Para | Lee |
|---|---|
| Los artefactos, el registro y las reglas que no se rompen | `${CLAUDE_PLUGIN_ROOT}/skills/aifg-capture/references/model.md` |
| Que se guarda de cada nodo, identidad, overrides, estados, capturas | `${CLAUDE_PLUGIN_ROOT}/skills/aifg-capture/references/extraction.md` |
| Hablar con Figma | `${CLAUDE_PLUGIN_ROOT}/skills/aifg-capture/references/mcp.md` |

## `aifg update [componente-o-hu]`

1. **Resuelve que se re-captura.** Si el argumento no llega, pregunta: un **componente** (`card`), una **HU** (`HU-07`) o un **frame** concreto. No lo adivines por lo ultimo que se toco.
2. **Comprueba el acceso a Figma** (`${CLAUDE_PLUGIN_ROOT}/skills/aifg-capture/references/mcp.md`). Sin MCP, detente: media actualizacion deja el arbol mintiendo con hash nuevo.
3. **Re-captura la pieza** con el mismo esquema de `${CLAUDE_PLUGIN_ROOT}/skills/aifg-capture/references/extraction.md`, y **actualiza su cabecera**: hash del payload nuevo y fecha.
4. **Si lo re-capturado es un componente, propaga.** Es lo barato: **la referencia no cambia**, los mapas siguen apuntando a `componentes/card.json`. Lo que se actualiza es el **hash del componente que cada mapa tenia registrado**.

   Un mapa guarda, junto a cada referencia, el hash del componente contra el que se construyo. Sin eso no se puede distinguir "este mapa esta al dia" de "este mapa se escribio contra otra version", que es justo lo que hace falta saber en el paso 6. **No toques el hash del propio mapa** si su contenido no ha cambiado: seria decir que cambio algo que no cambio.
5. **Detecta los overrides huerfanos.** Es el unico paso de esta lista que no es mecanico, y es el que importa:

   Si una instancia sobreescribia `boton.visible` y el disenador **quito el boton del molde**, ese override apunta a algo que ya no existe. Detectarlo es barato; **no detectarlo es corrupcion silenciosa** --el mapa sigue pareciendo valido y describe algo imposible--.

   Lista cada uno con su HU, su instancia y la propiedad que se quedo sin destino. **No los borres tu**: que el override sobre y que el diseno haya cambiado de intencion son cosas distintas, y solo se distinguen mirando.

6. **Reporta a quien afecta, separando lo cerrado.** Un componente lo pueden referenciar decenas de HU:

   | Grupo | Por que se separa |
   |---|---|
   | **HU sin abrir** | Recibiran el diseno nuevo sin coste: no hay nada hecho |
   | **HU con change abierto** | Alguien esta implementando **ahora mismo** contra la version anterior. Es el grupo urgente |
   | **HU ya cerradas** | Se implementaron contra un diseno que ya no existe |

7. **Y para ahi.** No intentes remediar el trabajo ya cerrado.

## Lo que queda fuera de alcance

**Remediar HU cerradas cuando cambia el diseno contra el que se implementaron.** La salida natural es abrir otra HU o una tarea, pero **la metodologia no contempla hoy ese camino** y no se improvisa aqui.

El informe hace falta igual: "habra que resolverlas de otra forma" presupone saber **cuales** son, y eso es lo que este comando entrega.

## Lo que no haces nunca

- **Editar el artefacto a mano** en vez de re-capturarlo. Si esta mal, se arregla en Figma.
- **Borrar overrides huerfanos por tu cuenta.** Se listan y decide una persona.
- **Re-capturar el arbol entero** cuando cambio una pieza: para eso esta `aifg capture`, y relanzarlo es una decision distinta con otro coste.
- **Tocar `docs/detalle-historias-usuario.md`.** Ni este comando ni ningun otro de AIFG escriben en la HU.
