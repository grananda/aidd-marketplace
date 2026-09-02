# aiba-status-report

Genera el **informe de situación del proyecto** en HTML, ejecutivo y visual, midiendo el avance por **trabajo ejecutado**.

```text
aiba status-report
```

Alias: `aiba estado`, `aiba informe estado`.

## Qué produce

**`docs/estado-proyecto.json`** — el registro. Se versiona en git a propósito: es lo que convierte el informe en una serie en vez de una foto, y es la fuente del HTML, así que no pueden divergir.

**`docs/html/estado-proyecto.html`** — el entregable. Autocontenido: sin CDN, sin fuentes externas, sin peticiones. Un informe de estado se reenvía por correo y se abre sin red.

## Cómo mide el avance

**Por trabajo ejecutado, no por fechas.** Es la diferencia con un Gantt coloreado a mano.

Una fase cuenta como entregada cuando su change está en `openspec/changes/archive/` — el mismo criterio que usa `aisdd roadmap` al re-fasear. Y **cada fase pesa sus días de esfuerzo**: `effort_ai` si el plan de recursos lo calculó, si no la suma de las tallas XS/S/M/L/XL de sus HU. Cerrar una fase L vale más que cerrar una XS; un porcentaje por número de fases lo escondería.

**Tres estados, no dos:** cerrado, activo y pendiente. Un change abierto no está ni entregado ni sin empezar, y meterlo en cualquiera de los dos lados miente en la dirección que le convenga a quien presenta.

**Dos métricas, jerarquizadas:** *changes* como principal —es la unidad que se abre y se cierra— y *HU* como secundaria —es lo que el negocio reconoce—. Si divergen mucho, eso ya es un hallazgo.

El **avance previsto** sale de los sprints ya cerrados, no del calendario prorrateado: un sprint entrega al cerrarse.

## Qué más lleva

| Sección | De dónde sale |
|---|---|
| Bloqueos activos | Decisiones bloqueantes sin resolver en `openspec/audit/` — **medidos**, no declarados |
| Dependencias | El grafo `depends_on`: fases listas para abrir, fases bloqueadas, conflictos cross-lane |
| Camino crítico | La cadena más larga. Ningún reparto baja de ahí, con los devs que sea |
| Ritmo de entrega | Lead time real `open change` → `close change`, y si acelera o frena |
| Riesgos y GAPs | Consolidados de los documentos de planificación, cada uno con su origen |
| Desviaciones y acciones | Con responsable y plazo: sin ellos una recomendación es una opinión |
| Resumen cualitativo | Lo escribe el analista sobre las cifras |

## Con el producto en varios repositorios

`--root` es **repetible**: uno por repo, desde la carpeta que los contiene.

```bash
compute_status.py --root repo-front --root repo-bff --root repo-datos --out estado-proyecto.json
```

Cada repo tiene su propio `openspec/` y cierra solo las fases de su lane, así que **el estado del proyecto no está en ninguno**: hay que sumarlos. Tres cosas que el informe hace y conviene saber leer:

- **Se suman días de esfuerzo, no porcentajes.** La media de tres porcentajes le da el mismo peso a un repo de 40 días que a uno de 4. La columna **Peso** de «Avance por repositorio» es la que distingue tres repos al 27 % de dos acabados con uno sin empezar.
- **La desviación se compara sobre la misma base.** Si un repo no tiene sprint-plan queda fuera del cálculo y el informe **dice sobre cuántos días compara**. Meterlo solo en el denominador hundía el previsto y el proyecto salía más sano por no tener plan.
- **Los caminos críticos no se suman.** Son cadenas paralelas: el del proyecto es el más largo, no el total.

**Si el proyecto migró de un repo a varios hay datos repetidos**, y el script lo sabe. Al partir, el `openspec/` anterior se copia entero a cada repo para no perder el registro de lo entregado, así que los changes ya cerrados están duplicados en los N. Se distinguen porque **sus fases no llevan `lane`** —se fasearon cuando no había repos— y se cuentan **una sola vez**. Por eso la suma de las columnas por repo no cuadra con el total: lo heredado no se atribuye a ninguno porque fue de todos.

## Por qué se desvió cada change

El informe ya sabía **cuánto** duró cada change. Esta sección dice **por qué**, que es lo que lo hace accionable: «vamos tres días tarde» no distingue entre contratar, desbloquear y rehacer specs.

Cruza el lead time en **días laborables** contra el esfuerzo estimado de la fase y adjunta la señal de la auditoría que lo explica — ratio de atención, bloqueos sin resolver, reintentos, `first_run_green`, correcciones, intervenciones.

- **Nada se inventa.** Un change desviado sin señal registrada sale como **hueco**, no recibe la causa más probable. Sobre una causa inventada se toman decisiones reales.
- **Los adelantos llevan el mismo detalle.** Es la parte que todo el mundo se salta y la única que dice **qué hay que repetir**.
- **Umbral del ±25 %.** Lo que no aparece está en línea, no sin mirar.

## Números y narrativa, separados

**Los números los calcula `compute_status.py`; la narrativa la escribe el skill.** Esa separación es la que impide que el resumen cualitativo diga una cosa y la barra de progreso otra.

Y una regla que sostiene todo lo demás: **nada se inventa**. Cada cifra declara el documento del que sale, y lo que no se puede derivar aparece como **hueco en ámbar** con el documento que lo llenaría. Una cifra plausible sin fuente es peor que un hueco, porque el hueco se ve.

## Degrada, no se detiene

Sin `openspec/` no hay avance real y lo dice. Sin `docs/sprint-plan.md` no hay previsto y lo dice. Con el roadmap solo ya da algo útil.

Un informe de situación que se niega a salir el día que falta un documento no sirve para lo que sirve un informe de situación.

## Frontera con `aiba metrics`

`metrics` mide **cuánto ayudó la IA** (tiempo atendido, churn, ahorro). Esto mide **dónde está el proyecto**. Comparten fuentes, no cifras: el informe enlaza a `docs/kpis-ia.md` y no lo recalcula.

## Requisitos

Python 3 y `PyYAML` para leer `openspec/config.yaml`, que el script instala solo si falta. Sin él, el informe sale con lo que pueda derivar del resto y lo declara.
