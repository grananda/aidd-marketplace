# Pre-flight de optimizacion del faseado

> Referencia del skill `aisdd-specs`. El indice y las reglas comunes estan en `SKILL.md`.

## Que resuelve

El modo de faseado y el numero de developers los elige el usuario, pero **elegirlos a ciegas es elegir mal**: la diferencia entre `waves` con 2 devs y `multilane` con 3 puede ser de semanas de calendario, y no se ve mirando una lista de fases.

Este pre-flight calcula ese calendario para cada combinacion y **pone los caminos uno al lado del otro**, con sus barreras y sus tiempos, para que la eleccion se haga con la cifra delante. Es **obligatorio** y corre en toda ejecucion de `aisdd roadmap`.

**Preguntar va primero.** El usuario declara que quiere **antes** de que se le calcule nada. Si el sistema propusiera el optimo primero, la comparativa dejaria de ser una comparativa: seria una recomendacion con una alternativa de adorno. El orden importa.

## Donde encaja

```
pasos 1-8    cuantas fases y de que tamano
paso  9      PREFERENCIA INICIAL del usuario -> modo y devs que el elegiria
paso 10      diseno de las fases: objetivo, depends_on y esfuerzo de cada una
paso 11      ESTE PRE-FLIGHT -> comparativa -> el usuario decide
paso 12+     se genera docs/roadmap.md ya con el modo confirmado
```

**No se puede adelantar.** El calculo necesita el grafo de dependencias y el esfuerzo por fase, y eso no existe hasta el paso 10. Un optimizador antes del faseado no tendria sobre que optimizar.

## Requisito duro: las tallas

`aisdd roadmap` **exige `docs/detalle-historias-usuario.md`**. Sin las tallas XS/S/M/L/XL de las HU no hay esfuerzo por fase, sin esfuerzo no hay calendario, y sin calendario esta comparativa seria una invencion presentada como dato.

Si el fichero no existe, **detente en el paso 2** y remite a `aidd user-story-details`. No estimes tu las tallas: es el trabajo de otro skill y el usuario tiene que poder revisarlo.

## Como se ejecuta

**1. Compon la entrada** con las fases que acabas de disenar en el paso 10:

```json
{
  "proyecto": "<nombre del proyecto>",
  "equipo": {"devs": 2},
  "eleccion_usuario": {"mode": "waves", "devs": 2},
  "fases": [
    {"id": "F0", "titulo": "Foundation", "effort_days": "M", "foundation": true},
    {"id": "F1", "titulo": "Contrato de API", "effort_days": "S", "shared": true, "depends_on": ["F0"]},
    {"id": "F2", "titulo": "Catalogo backend", "effort_days": "L", "depends_on": ["F1"]}
  ]
}
```

- `effort_days` admite **dias** (numero) o **talla** (`"M"`). Usa la talla agregada de las HU que cubre la fase.
- `shared: true` marca la fase que toca **superficie compartida** —contrato, esquema, migraciones, permisos, rollout—. Es lo que en `multilane` sera una barrera. **Marcarlas bien es lo que hace util la comparativa**: son las que revelan el riesgo que `waves` no cubre.
- `foundation: true` en la fase base. Implica `shared`.
- `equipo.devs`: developers **de implementacion** disponibles (mismo criterio que el paso 0: no cuentes Lead, Architect ni Outcome Validator).
- `eleccion_usuario`: lo que el usuario dijo en el paso 9.
- `estado`: `pendiente` (default), `hecha` o `en_curso`. Solo aplica al **re-estrategiar** un proyecto en marcha (ver "Cambiar de estrategia a mitad de proyecto", `references/roadmap.md`). Lo `hecho` sale del calculo y sus dependencias quedan satisfechas; lo `en_curso` entra anclado, ocupando a su dev desde el minuto cero.
- `restante_days`: en las fases `en_curso`, lo que falta. Sin el se asume la fase entera.

**2. Lanza el script** (ver "Scripts del skill", `references/scripts.md`):

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/aisdd-specs/scripts/optimize_phasing.py" \
  --input <plan.json> --out docs/html/faseado-comparativa.html
```

**3. Presenta el resultado.** Di la ruta del HTML y resume en tres lineas: que cuesta su eleccion, que cuesta el optimo con su equipo, y —si lo hay— que costaria ampliar. Luego pregunta con `AskUserQuestion`, una opcion por camino.

## Como leer la comparativa

| Cifra | Que significa |
|---|---|
| **Camino critico** | La cadena de dependencias mas larga. **Ningun reparto baja de ahi**, con los devs que sea. Cuando un camino toca esa cifra, anadir gente ya no compra calendario |
| **Devs optimos** por modo | El primer `N` que alcanza el mejor calendario de ese modo. A partir de ahi cada dev de mas esta parado |
| **Ahorro vs tu eleccion** | Dias que se ganan cambiando de modo sin tocar el equipo. Es el argumento mas facil de aceptar: no cuesta dinero |
| **Coste de no ampliar** | Dias que se pierden por no anadir developers. Es el argumento de negocio |

**Lo que el calendario no dice.** Un camino mas corto puede ser mas fragil. En el HTML, las barras con borde grueso y trama son fases de **superficie compartida corriendo sin barrera**: solo aparecen fuera de `multilane`, y son exactamente el riesgo que las oleadas no cubren. Dilo al presentar: *"`waves` sale 2 dias mas rapido, pero deja tres fases de contrato sin proteger"*.

## Re-estrategiar un proyecto en marcha

Mismo pre-flight, con dos diferencias que cambian como se lee:

- **El calendario que se compara es el restante**, no el total. Lo entregado no vuelve, y meterlo en la cifra haria que cualquier cambio pareciera marginal.
- **La comparativa lleva una banda de lo ya cerrado** antes de la marca de *hoy*. Se lista sin escala de tiempo a proposito: no consta cuando ocurrio cada fase, y pintarla a escala seria inventar historia.

El campo `diagnostico` del JSON resume la situacion en una linea. **Presentalo tal cual**, sobre todo cuando dice que el calendario ya toca el camino critico: significa que el cuello es una cadena de dependencias y que el developer que acaban de incorporar **no va a acelerar nada**. Es la respuesta que menos gusta y la que mas falta hace.

El campo **`avisos`** trae los problemas de consistencia que el calculo detecta pero no puede resolver. Hoy uno: **mas fases en curso que developers declarados**, que significa o que el equipo esta mal contado o que alguien lleva dos changes abiertos — y en cualquier caso que el calendario sale optimista. Salen tambien en el HTML, arriba del todo: son razones para desconfiar de las cifras, asi que se leen antes que ellas.

**Dos incoherencias abortan el calculo** en vez de avisar, porque describen una historia imposible y cualquier numero derivado de ellas seria falso: una fase `hecha` que depende de otra que no lo esta, y un `estado` que no es ninguno de los tres.

## Reglas al recomendar

- **No decidas tu.** El pre-flight informa; el modo lo elige el usuario. Presenta el optimo como opcion marcada `(Recomendada)`, no como hecho consumado.
- **Un solo dev cierra la discusion.** Con `equipo.devs: 1` el modo es `atomic` y no hay nada que comparar. Dilo y sigue; no generes el HTML.
- **Empates.** A igual calendario y mismos devs, el script prefiere `multilane` (es el unico modo cuyo aislamiento verifica un comando) salvo con un solo dev, donde prefiere `atomic` (los otros dos serian ceremonia sin paralelismo que proteger). Si presentas un empate, explica por que se rompe asi.
- **Las cifras se desvian en dos direcciones, y no son la misma.** Son **optimistas sobre la viabilidad**: `multilane` da por hecho que existe un corte de lanes valido para ese reparto, y un corte real exige ademas **rutas y specs disjuntas** (ver "Criterios de corte de lanes", `references/parallelism.md`). Si el corte no se sostiene, ese calendario no se alcanza — **dilo siempre** al presentar un optimo `multilane`, y comprueba el corte en los pasos 1-7 de la construccion de lanes antes de darlo por bueno. Y son **conservadoras sobre el reparto**: el script prueba seis prioridades y se queda con la mejor, pero repartir trabajo con precedencias no tiene solucion exacta barata. Por ese lado el calendario real puede salir algo mejor, nunca peor.
- **Mas lanes que devs se rechaza igual.** El optimizador puede proponer `N` mayor que el equipo actual —es su trabajo, con el coste declarado—, pero si el usuario acepta ese camino sin ampliar el equipo, se aplica la regla de siempre: no hay quien conduzca el lane de mas.

## Que registrar

En `docs/roadmap.md`, junto al modo y `parallel_developers`, deja **una linea con la eleccion y su coste**: modo elegido, devs asumidos, calendario estimado, y —si el usuario descarto el optimo— cuantos dias cuesta esa decision. Sin esa linea, dentro de tres meses nadie sabra si el faseado actual fue una decision o una inercia.

La entrada de auditoria del comando incluye el HTML en `output_files` y la eleccion en `decisions[]`.
