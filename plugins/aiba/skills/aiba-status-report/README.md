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
