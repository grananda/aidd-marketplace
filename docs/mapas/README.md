# Mapas de AIDD

Seis diagramas para saber con qué herramientas cuentas, en qué momento se usa cada una y para qué. Se ven pintados aquí mismo, en GitHub.

| Si te preguntas... | Mapa |
|---|---|
| ¿Qué plugins hay y cuáles instalo? | [Plugins](plugins.md) |
| ¿Qué trae cada plugin? | [Skills](skills.md) |
| ¿Qué se usa en cada momento del proyecto? | [El proceso](proceso.md) |
| Estoy a mitad de sprint: ¿qué uso ahora? | [¿Qué uso cuando...?](que-uso-cuando.md) |
| ¿Quién hace qué con un change y qué queda escrito? | [Ciclo de un change](ciclo-change.md) |
| ¿Qué documento sale de cada paso y quién lo lee después? | [Artefactos](artefactos.md) |

**Por dónde empezar.** Si acabas de llegar, [Plugins](plugins.md) y después [El proceso](proceso.md). Si ya estás construyendo, [¿Qué uso cuando...?](que-uso-cuando.md).

## Cómo se leen

- **Línea continua**: el paso siguiente, o lo que un paso le entrega a otro.
- **Línea discontinua**: opcional, o solo si ese documento existe.
- **Cada nodo** lleva el comando y para qué sirve. En GitHub los nodos no son clicables: los enlaces a cada skill están en la tabla de debajo de cada diagrama.

## Mantenerlos al día

Los mapas se escriben a mano, y en este repo entran skills a menudo. `check_maps.py` falla en la CI si un skill no tiene fila en [Skills](skills.md) o no sale en su mindmap, si la cuenta de skills de un plugin en [Plugins](plugins.md) no es la real, o si un enlace de estos mapas lleva a un fichero o a una sección que no existe.

Cuando añadas un skill, tócalos en este orden:

1. Su fila en [Skills](skills.md) y su rama en el mindmap.
2. La cuenta de su plugin en [Plugins](plugins.md).
3. Su sitio en [El proceso](proceso.md) si es un paso, en [¿Qué uso cuando...?](que-uso-cuando.md) si resuelve una situación del dev, y en [Artefactos](artefactos.md) si escribe o lee un documento.
