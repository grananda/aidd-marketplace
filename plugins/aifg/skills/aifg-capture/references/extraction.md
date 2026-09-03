# Que se extrae y como se guarda

> Referencia del skill `aifg-capture`. El indice y las reglas comunes estan en `SKILL.md`.

## El criterio

El JSON crudo de un nodo trae toda la geometria vectorial: megas por frame, y la mayor parte no produce nada implementable.

**El descarte es seguro** porque todo se regenera desde Figma: lo que se tira no es un registro que se pierde, es **cache que se puede rellenar**. La excepcion es que el archivo de Figma se reestructure o desaparezca; para ese caso el respaldo util es el **PNG**, que un humano puede leer, no un volcado de geometria que nadie va a mirar.

> **Se guarda lo que permite reconstruir la pantalla; los activos se exportan como SVG o PNG en vez de como geometria; el resto se tira.**

### Se guarda

- **Auto-layout** (direccion, `gap`, padding), tamano y constraints.
- **Posicion absoluta solo si el frame no usa auto-layout.** Con auto-layout, el auto-layout manda; sin el --archivos antiguos o hechos con prisa-- tirar los bounds tira el layout entero.
- **Fills y strokes resueltos contra los tokens** (`--color-primary`, no `#0072CE` suelto). Los tokens los emite `aidd style-guide`; aqui se consumen, no se generan.
- **Efectos**: sombras, blurs, bordes internos. Son diseno puro; una card sin su sombra se nota.
- **Estilo de texto.**
- **Instancia de componente**: referencia, variant props y **overrides**.
- **Estados**, cuando el diseno los declare.
- **Referencia al SVG exportado** para iconos e ilustraciones. Ahi la geometria vectorial **es el activo**: lo que no se guarda es el array de paths dentro del JSON. Un front sin sus iconos tampoco se parece al diseno.

### Se tira

`fillGeometry` y `strokeGeometry` de formas que no son iconos, `absoluteRenderBounds`, datos de plugins, y los subarboles de decoracion que no producen nada implementable.

## Identidad de las piezas

**Un node id no cambia.** El nodo deja de existir y aparece otro nuevo con otro id --al borrar y rehacer un frame, o al copiar y pegar--. Por eso no se detecta "este id cambio": se detecta que **un id desaparecio** y hay uno desconocido con el mismo nombre.

| Pieza | Identidad |
|---|---|
| **Definicion de componente** | La **`key`** de Figma, que sobrevive a republicar y a moverse entre ficheros. Existe **solo si el componente esta publicado en una libreria** |
| **Instancia** | El **node id**: una instancia no tiene key, vive dentro de un frame y es un nodo como cualquier otro |

**Guarda siempre la ruta de pagina/frame por nombre junto al id.** Es lo unico que permite **reparar** un enlace roto en vez de solo saber que se rompio. Y cuando un nodo no resuelva, **fallo ruidoso**: dilo, no lo omitas.

### Sin libreria publicada

Se trabaja con lo que haya. Con libreria, los cambios se propagan solos; sin ella, node id para todo y, cuando se rompa, **rehacer todas las referencias desde cero**. Es el precio de un diseno mal construido, y no nos toca a nosotros corregirlo.

- **El modo se registra por componente, no por proyecto.** Un mismo archivo puede tener el boton publicado y la card hecha a mano en local. **Reporta cuantos cayeron a node id**: hay que estar en el modo fragil sabiendolo, no descubrirlo cuando explote una re-extraccion.
- **Rehacer las referencias deja sin enlace de diseno a las HU ya cerradas.** Es la factura, y hay que decirla antes.
- **Pide al equipo de diseno que publique la libreria.** Es una sola accion y es la que separa los dos escenarios.

## Niveles de agrupacion

El componente es el escalafon mas basico y de ahi hacia arriba: si un bloque --titulo mas formulario-- se usa en dos pantallas, ese conjunto es otro aglomerado a compartir.

**Y el aglomerado existe solo si Figma lo declara como componente.** Figma soporta componentes anidados: si diseno construyo "formulario de alta" como componente que contiene el de titulo, el aglomerado **ya es un componente**, con su `key`, a cualquier profundidad.

**Lo que diseno no componentizo se repite inline en cada mapa de HU.** No detectes subarboles repetidos, no les inventes nombre, no hay umbral de tamano ni tope de profundidad. Detectar repeticiones produce aglomerados minusculos y sin sentido --dos etiquetas juntas salen cuarenta veces-- que acaban llamandose `grupo-17` y no le dicen nada a nadie.

> **Consecuencia asumida:** sin deteccion tampoco hay aviso. No podras decirle a diseno "este bloque sale en seis pantallas y no es un componente", porque descubrirlo cuesta justo la maquinaria que se descarta.

## Overrides

Un componente es un molde. Al colocarlo se coloca una **instancia**, que hereda todo pero puede cambiarle cosas **solo ahi**. Eso son los overrides.

Si el mapa guarda tres veces `{"ref": "componentes/card.json"}`, quien implemente reconstruye **tres cards identicas** --y el diseno tenia una roja sin boton, porque era el estado de error--. **Es el problema original con mas pasos**: toda una maquinaria de extraccion para producir la misma divergencia, ahora con la confianza de creer que el diseno esta capturado.

Cada instancia lleva su diff contra el molde:

```json
{"ref": "componentes/card.json", "nodeId": "1:482",
 "overrides": {"titulo": "Pago rechazado", "boton.visible": false, "fill": "--color-error"}}
```

**La referencia dice de que molde sale; los overrides, en que se separa. Los dos, o no se reconstruye nada.**

### Dos clases, distinto trato

| Tipo | Ejemplos | Trato |
|---|---|---|
| **Contenido y estilo** | texto, color, tamano, variante | Se capturan **siempre y en silencio**. Es el uso normal y correcto de un componente |
| **Estructura** | ocultar hijos, cambiar el auto-layout, intercambiar una instancia anidada | Se capturan igual **y ademas se senalan**: casi siempre falta una variante del componente |

**La regla no puede ser "override igual a sintoma".** Cambiar el texto de una card es para lo que existen los componentes, y un Figma real trae **cientos** de overrides de contenido. Si los tratas todos como anomalia, levantas cientos de avisos en el primer archivo y el aviso deja de significar nada.

**El umbral es estructura frente a contenido, no un numero de overrides.** Es una linea programable y no hay que calibrarla.

Cuando una instancia se ha alejado tanto que la lista de overrides sale mas cara que capturarla entera, **capturala como nodo unico y dilo**.

La misma regla aplica **sin cambios en cada nivel de agrupacion**: un aglomerado se referencia igual que un componente.

## Estados

**De Figma sale lo que Figma tenga**, por dos vias:

- **Variantes.** Un *component set* con `state = default | hover | pressed | disabled` da cada estado como componente con su propia `key`, leido literalmente y sin inferir.
- **Interacciones de prototipo.** Los nodos llevan sus reacciones: al pulsar navega a tal frame, al pasar por encima cambia a tal variante. Eso da **comportamiento**, no solo apariencia. **Se capturan cuando esten, no se exigen**: muchos equipos disenan frames estaticos y cuentan el comportamiento de palabra.

**Si no hay informacion de estados, no hay estados.** No los inventes.

**El porque no esta en Figma y no hace falta construirlo**: que ese campo solo salga para clientes corporativos, que valida, que dice el error y cuando, ya esta escrito en la HU.

## Capturas

Cada definicion lleva su `card.json` **y** su `card.png`. La imagen se amortiza igual que el JSON: se renderiza una vez y sirve para las treinta HU que usan esa card. El argumento es el mismo de todo esto --**describir un diseno con texto no lo reproduce**--, y vale para un JSON de nodo tanto como para la guia de estilos.

- **Bajo demanda, nunca por defecto.** Una imagen en contexto cuesta mucho mas que el JSON que la describe; cargarlas todas se come el ahorro de normalizar. **Se implementa desde el JSON y se verifica contra el PNG**: la imagen es canal de verificacion, no de especificacion.
- **Un component set es una lamina, no quince renders.** Cinco variantes por tres estados en un solo fichero, con todos los estados a la vista.
- **El PNG del componente no se parece a la instancia con overrides**, porque es el molde. Por eso **el PNG del frame por HU sigue haciendo falta**: uno dice como es la pieza, el otro como queda la pantalla.
- **Tope de tamano**, y dilo al reportar. Son binarios: no diffean y engordan la historia, mas aun en un repo de gobierno.
