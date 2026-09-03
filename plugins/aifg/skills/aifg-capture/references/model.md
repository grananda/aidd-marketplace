# El modelo de artefactos

> Referencia del skill `aifg-capture`. El indice y las reglas comunes estan en `SKILL.md`.

## El arbol

```
docs/design/
  registro.md                      <- HU <-> frames: los vinculos confirmados
  tokens.json  tokens.css          <- el sistema, global (lo emite aidd style-guide)
  componentes/nav.json  card.json  <- definiciones, una vez cada una
  componentes/nav.png   card.png   <- el molde, para verificar
  hu/HU-07/mapa.json               <- composicion de la pantalla
  hu/HU-07/referencia.png          <- el frame exportado
```

## Dos artefactos que se parecen y no son lo mismo

Confundirlos es el error que rompe el modelo, asi que la distincion va primero.

| Artefacto | Que es | Vida |
|---|---|---|
| **`registro.md`** | El **indice de vinculos** HU <-> frames de Figma | Lo confirma un humano cuando hace falta y **sobrevive a cualquier regeneracion** |
| **`hu/HU-07/mapa.json`** | La **composicion** de esa pantalla: sus nodos propios y las referencias a los componentes que usa | Generado y **desechable** |

## Por que esta fraccionado

Los nodos no se guardan como un bloque por HU. Se separan en **definiciones de componente** reutilizables y un **mapa por HU** que las referencia.

**El ahorro grande no es la deduplicacion: es que el fraccionamiento permite cargar bajo demanda.** Un bundle monolitico hay que abrirlo entero aunque el change toque un campo de un formulario. Fraccionado, el mapa es corto y las definiciones se abren **solo si el change las toca**. Es el mismo principio que gobierna los skills de este repo --indice mas `references/*.md` bajo demanda-- aplicado al diseno.

La deduplicacion da ademas dos ahorros que conviene no confundir:

- **Entre HU**: el nav se captura una vez en lugar de treinta. Grande, pero es ahorro de **repositorio**, no de contexto de sesion.
- **Dentro de una pantalla**: una tabla de doce filas identicas pasa de doce payloads a una definicion y doce referencias cortas. Esto si es contexto, y en UI corporativa --listas, tablas, grids, cards-- es la mayor parte de la pantalla.

**Donde ahorra poco** es en una pantalla de quince elementos unicos usados una vez cada uno: ahi la normalizacion anade indireccion a cambio de nada. **No fuerces el desglose cuando no lo hay.**

## Nada se edita a mano

**Ningun artefacto generado se toca a mano.** Todo cambio de diseno pasa por `aifg capture` o por `aifg update`, que lo regeneran. Con eso el arbol es integramente generado y relanzar la extraccion masiva es rutina, no riesgo.

Dos consecuencias:

- **El registro no es uno de esos ficheros.** Cuando el vinculo HU <-> nodo lo confirmo un humano, eso es una respuesta persistida, no un fichero editado: la extraccion masiva **lo lee y lo respeta**, y solo le anade lo nuevo.
- **Cabecera de generado en cada fichero**, con el **hash del payload y la fecha de extraccion**:

  ```json
  {"_aifg": {"generado": "no editar a mano",
             "hash": "<sha256 del payload>",
             "extraido": "<YYYY-MM-DD>"}}
  ```

  **Y cada referencia a un componente guarda ademas el hash de ese componente** (`refHash`), que es cosa distinta: el de la cabecera dice si cambio **este** fichero, y el `refHash` dice si cambio **aquel** contra el que se construyo. Solo el segundo permite detectar un mapa desactualizado.

  Van ahi, y no en un indice aparte, para que **viajen con lo que describen**: un indice separado se desincroniza y nadie se entera. Cubren tambien la imagen: un JSON fresco junto a un PNG viejo es peor que no tener imagen, porque parece verificacion y no lo es.

## Por que se versiona algo generado

Siendo los JSON integramente derivables de Figma, parecen artefacto de build y alguien preguntara por que van al repositorio. Van, por dos razones:

1. Que el dev implemente **sin abrir Figma**, que es el punto de todo esto.
2. Que quede constancia de **que decia el diseno cuando se implemento** esa HU.

## Topologia

**AIFG no impone ninguna.** En topologia `fraccionado`, `docs/` se copia entera a cada repo y el arbol de diseno acaba duplicado cuando solo lo necesita el repo de front. **Se acepta**: el arquitecto decide que modelo es mas eficiente, y si solo un repo trabaja con diseno, poco importa que el de backend lleve informacion que no usa.

- **El peso esta en las imagenes, no en los JSON.** Lo que se multiplica son los PNG, que son binarios y no diffean. Ponles un tope de tamano y dilo al reportar.
- **Si el proyecto tiene diseno, externalizar los docs suele salir mejor.** Es una **recomendacion al arquitecto**, no una obligacion, y no la impone ningun comando del nucleo: `aisdd init` y `aisdd roadmap` no saben que Figma existe y asi debe seguir.
