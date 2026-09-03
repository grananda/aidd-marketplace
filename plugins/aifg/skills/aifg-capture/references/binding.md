# Vincular HU y diseno

> Referencia del skill `aifg-capture`. El indice y las reglas comunes estan en `SKILL.md`.

## Que se le presenta al humano

Un **mapa de HU y disenos** para que elija, **omitiendo lo que no admite duda**.

La pieza que lo hace casi gratis ya existe: el PNG de cada frame. Cuarenta frames resueltos en preguntas de terminal son un suplicio; en una **tabla con la miniatura al lado del nombre** son cinco minutos. Y sin miniatura nadie puede decidir --los nombres de frame no bastan--. Si `booster-docs` esta disponible, renderiza esa tabla como vista HTML; si no, presentala como puedas pero **con las imagenes localizables**.

## Tres niveles, para que "lo obvio" sea una linea y no un criterio difuso

| Senal | Trato |
|---|---|
| El nombre del frame **contiene el codigo de la HU** (`HU-07 - Alta de cliente`) | Resuelto, **no se muestra** |
| **Parecido fuerte de titulo** | Se muestra **con la respuesta ya marcada**: un vistazo y adelante |
| Sin senal | Se muestra **en blanco**: elige el humano |

**Nunca resuelvas en silencio por parecido de titulo.** Un binding equivocado y callado entrega el diseno de otra pantalla con toda la confianza del mundo, y eso es peor que preguntar.

## La lista va en las dos direcciones

- **HU sin diseno.**
- **Disenos que ninguna HU reclama.** Es la que se olvida, y suele significar una de dos: una pantalla para la que **nadie escribio HU** --hueco real de requisitos-- o algo muerto en el Figma. Las dos merecen decirse.

Es el mismo espiritu que la seccion de cobertura de `aidd user-story-details`: lo que falta se lista, no se esconde.

## Es N:M

Una HU se come varios frames --lista, detalle y confirmacion son un flujo--, y un frame puede servir a varias HU. **El selector no puede ser uno a uno.**

## Se persiste y no se vuelve a preguntar

El resultado vive en `docs/design/registro.md`, que **sobrevive a cualquier regeneracion**. Una re-ejecucion de `aifg capture` solo pregunta por **lo nuevo** o por **lo que se rompio**.

Formato de cada entrada:

```markdown
## HU-07 - Alta de cliente

- **Frames**: `Alta / Formulario` (`1:204`), `Alta / Confirmacion` (`1:266`)
- **Origen**: convenio de nombres | confirmado por <quien> el <YYYY-MM-DD>
- **Estado**: vigente | frame no encontrado
```

El campo **Origen** es lo que hace reparable el registro: un vinculo confirmado por una persona no se vuelve a adivinar, y uno que salio del convenio de nombres se puede recalcular sin preguntar.

## La HU no guarda nada

**El documento de la HU no se toca.** No lleva puntero, ni referencia, ni nota. La busqueda va al reves: se coge el **id de la HU** y se busca en el registro o en el arbol. Tres razones:

1. `docs/detalle-historias-usuario.md` queda **sin un solo rastro de AIFG**. Su cuerpo es client-ready por regla propia del skill que lo escribe, y esto la respeta en vez de pelearse con ella.
2. **Los skills de AIDD no necesitan ningun cambio.** AIFG es puramente aditivo.
3. **Un solo indice.** Un puntero en la HU podria quedarse viejo por su cuenta y contradecir al registro; sin puntero no hay dos sitios que puedan discrepar.

Es ademas **la misma busqueda** que hace `aisdd implement change` para deducir que un change toca front. No son dos mecanismos, es uno.
