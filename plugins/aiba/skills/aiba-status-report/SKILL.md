---
name: aiba-status-report
description: AIBA (AI Business Analyst) — genera el informe de situacion del proyecto en HTML, ejecutivo y visual, mediante el comando `aiba status-report` (alias `aiba estado`, `aiba informe estado`). Actua como jefe de proyecto que mide el avance **por trabajo ejecutado y no por fechas**: cruza las fases de `openspec/config.yaml` con `openspec/changes/archive/` por `change_hint`, pesa cada fase con su esfuerzo (`effort_ai` o las tallas XS/S/M/L/XL de sus HU) y da dos metricas jerarquizadas — changes como principal, con tres estados (cerrado, activo, pendiente), e historias de usuario como secundaria. Lo contrasta con el avance previsto que se deriva de los sprints ya cerrados de `docs/sprint-plan.md` y expresa la desviacion en puntos y en dias. Anade bloqueos **medidos** (decisiones bloqueantes sin resolver en `openspec/audit/`), dependencias listas y bloqueadas del grafo `depends_on`, conflictos de faseado cross-lane, camino critico, ritmo real de entrega (lead time `open change` -> `close change` y su tendencia), riesgos y GAPs consolidados, analisis de desviaciones con responsable y plazo, y un resumen cualitativo con acciones de corto plazo. Los numeros los calcula un script y la narrativa la escribe el skill: cada cifra declara el documento del que sale, y lo que no se puede derivar aparece como hueco declarado, nunca como cifra plausible. Produce `docs/estado-proyecto.json` (el registro, versionable y comparable semana a semana) y `docs/html/estado-proyecto.html` (autocontenido, sin recursos externos). Degrada sin detenerse: con menos documentos da menos informe y lo dice. Usar cuando el usuario pida "informe de estado", "como va el proyecto", "reporte de situacion", "status del proyecto", "avance real vs previsto", o equivalentes.
metadata:
  author: NTT DATA Spain GDN-e
  version: "0.1.1"
---

# aiba-status-report (AIBA · Informe de situacion)

Usa este skill cuando el usuario quiera saber **como va el proyecto** con cifras defendibles. Comandos:

- `aiba status-report`
- Alias: `aiba estado`, `aiba informe estado`

Responde y documenta en espanol. Conserva en ingles nombres de comandos, ficheros, rutas y terminos tecnicos establecidos.

## Que es AIBA y donde encaja este skill

**AIBA** (AI Business Analyst) es el conjunto de skills que da la cara ante el negocio. Su metodologia esta en `${CLAUDE_PLUGIN_ROOT}/methodology/native-ai-aiba.md` (referencia de solo lectura). Este skill es el que responde a la pregunta que se hace en cada comite: *donde estamos, vamos bien, y que hacemos ahora*.

**No mide lo mismo que `aiba metrics`.** `metrics` mide **cuanto ayudo la IA** (tiempo atendido, churn, ahorro). Este mide **donde esta el proyecto**. Comparten fuentes, no cifras: el informe **enlaza** a `docs/kpis-ia.md` si existe y **no lo recalcula**.

| Lee | Para |
|---|---|
| `openspec/config.yaml` | Fases, `change_hint`, `hus`, `depends_on`, `sprint` y esfuerzo por fase |
| `openspec/changes/` y `.../archive/` | Que changes estan activos y cuales cerrados |
| `openspec/audit/*.jsonl` | **Cuando** se abrio y cerro cada uno, y que bloqueos siguen pendientes |
| `docs/detalle-historias-usuario.md` | Tallas XS/S/M/L/XL para pesar cada fase |
| `docs/sprint-plan.md` | Sprints y fechas, de donde sale el avance previsto |
| `docs/planificacion-proyecto.md`, `docs/sprint-plan.md`, `docs/arquitectura-base.md` | Riesgos declarados, que tu consolidas |

Criterio de salida: existen `docs/estado-proyecto.json` y `docs/html/estado-proyecto.html`, cada cifra tiene su documento de origen, y las secciones que no se han podido rellenar aparecen como hueco declarado.

## La regla que sostiene el informe

**Nada se inventa.** Un informe de situacion se presenta en un comite y se toman decisiones con el. Una cifra plausible pero sin fuente es peor que un hueco, porque el hueco se ve y la cifra no.

De ahi salen las tres reglas de trabajo:

1. **Los numeros los calcula el script.** No los estimes tu, no los redondees "para que queden mejor" y no rellenes los que falten.
2. **La narrativa la escribes tu**, sobre esos numeros. Es la parte que un script no puede hacer: por que la cifra es la que es y que hay que hacer.
3. **Lo que no hay, se dice.** El HTML pinta cada hueco en ambar con el documento que lo llenaria. No lo maquilles con una frase generica.

## Como se mide el avance

**Por trabajo ejecutado, no por fechas.** Es la diferencia entre este informe y un diagrama de Gantt coloreado a mano.

- Una fase cuenta como **entregada** cuando su change esta en `openspec/changes/archive/`. Mismo criterio que usa `aisdd roadmap` al re-fasear.
- Cada fase **pesa sus dias de esfuerzo**: `effort_ai` si el plan de recursos lo calculo, si no la suma de las tallas de sus HU. Cerrar una fase L vale mas que cerrar una XS, y un porcentaje por numero de fases lo ocultaria.
- **Tres estados, no dos**: cerrado, activo y pendiente. Un change abierto no esta ni entregado ni sin empezar, y meterlo en cualquiera de los dos lados miente en la direccion que le convenga a quien presenta.
- **Dos metricas, en este orden**: *changes* (principal, es la unidad que se abre y se cierra) y *HU* (secundaria, es lo que el negocio reconoce). Si divergen mucho, eso es en si mismo un hallazgo.
- El **avance previsto** sale de los sprints **ya cerrados** del plan, no del calendario prorrateado: un sprint entrega al cerrarse, y repartir su carga dia a dia inventaria un avance continuo que no existe.

## Flujo del comando

### 1. Calcular

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/aiba-status-report/scripts/compute_status.py" \
  --root . --anterior docs/estado-proyecto.json --out docs/estado-proyecto.json
```

**El mismo fichero como entrada y como salida es correcto**: el script lee el
anterior antes de escribir el nuevo. Si es el primer informe, lo dice y sigue.

**Lee los avisos que emite por stderr antes de seguir.** Dicen que no ha podido calcular y por que: fases sin `change_hint`, fases sin esfuerzo, changes abiertos que no estan en el roadmap. Cada uno de ellos cambia como hay que leer las cifras, y varios son hallazgos por si solos — un change fuera de plan es trabajo que nadie previo.

### 2. Leer las cifras antes de escribir nada

Abre el JSON y **entiende el numero antes de narrarlo**. Preguntas que responder:

- ¿La desviacion viene del ritmo o de los bloqueos? Compara `ritmo.tendencia` con `bloqueos`.
- ¿El camino critico pasa por algo bloqueado? Cruza `camino_critico.cadena` con `bloqueos[].change`. Si coincide, **es el hallazgo principal del informe** y va primero: cada dia de bloqueo es un dia de calendario, no de holgura.
- ¿Divergen changes y HU? Un avance de changes alto con HU bajo significa fases grandes a medias.
- ¿Hay fases listas para abrir y nadie las ha abierto? Es capacidad ociosa.

### 3. Anadir la narrativa al JSON

Edita `docs/estado-proyecto.json` y anade la clave `narrativa`:

```json
"narrativa": {
  "resumen": ["parrafo", "parrafo"],
  "desviaciones":   [{"id","desviacion","causa","prioridad","accion","responsable","plazo"}],
  "riesgos":        [{"id","descripcion","probabilidad","impacto","estado","mitigacion","origen"}],
  "gaps":           [{"id","descripcion","probabilidad","sprint","estado","accion"}],
  "recomendaciones":[{"prioridad","accion","porque","responsable","plazo"}]
}
```

- **`riesgos`**: consolidalos de `docs/planificacion-proyecto.md` §8, `docs/sprint-plan.md` §6 y `docs/arquitectura-base.md` §13. **Cita el origen de cada uno** en su campo `origen`: un riesgo sin procedencia no se puede contrastar.
- **`gaps`**: dependencias **externas** al equipo — un tercero, una decision de negocio, un entorno que no llega. Son categoria aparte de los bloqueos porque no se resuelven igual: un bloqueo lo desatasca el equipo, un GAP hay que escalarlo.
- **`desviaciones` y `recomendaciones`**: siempre con **responsable y plazo**. Sin ellos una recomendacion es una opinion, y el informe deja de ser accionable.
- **Maximo 5 recomendaciones**, ordenadas por prioridad. Una lista de quince no se ejecuta.

### 4. Renderizar

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/aiba-status-report/scripts/render_status_html.py" \
  --input docs/estado-proyecto.json --output docs/html/estado-proyecto.html
```

El HTML es **autocontenido**: sin CDN, sin fuentes externas, sin peticiones. Un informe de estado se reenvia por correo y se abre sin red.

### 5. Leer la comparativa

Si habia informe anterior, el JSON trae el bloque `comparativa`, y el HTML lo pinta arriba del todo: es lo primero que pregunta quien ya vio el de la semana pasada.

**Lo que hay que mirar ahi, y decir en el resumen:**

| Campo | Que significa |
|---|---|
| `avance_puntos` | Cuanto se ha movido el avance real. Cerca de cero con changes activos es una semana perdida |
| `desviacion_puntos` | Si la brecha con el plan se cierra o se abre. Es mas importante que la desviacion absoluta |
| `bloqueos_que_repiten` | **El dato que menos se ve mirando solo el de hoy.** Un bloqueo en dos informes seguidos ya no es un bloqueo: es un problema de gobierno, y se resuelve escalandolo, no esperando |

`docs/estado-proyecto.json` se versiona en git **a proposito**: es el registro y es la fuente del HTML, asi que no pueden divergir, y es lo que convierte el informe en una serie en vez de una foto.

### 6. Resumen final

Informa de:

- **Las dos rutas** (`docs/estado-proyecto.json` y `docs/html/estado-proyecto.html`).
- **Avance real, previsto y desviacion**, en una linea.
- **Bloqueos activos** y si alguno esta en el camino critico. Es lo que hay que resolver esta semana.
- **Los huecos del informe**: que secciones han salido vacias y que documento las llenaria. Es trabajo pendiente de documentacion, no un detalle de formato.
- **Que ha cambiado desde el informe anterior**, si lo hay, y en especial **los bloqueos que repiten**.

## Lo que no hace

- **No modifica los documentos del proyecto.** Lee `docs/` y `openspec/`, y escribe solo sus dos ficheros.
- **No recalcula los KPIs de IA.** Eso es `aiba metrics`; aqui se enlaza.
- **No se detiene si falta documentacion.** Sin `openspec/` no hay avance real y lo dice; sin `sprint-plan.md` no hay previsto y lo dice. Un informe de situacion que se niega a salir el dia que falta un documento no sirve para lo que sirve un informe de situacion.
- **No juzga a las personas.** Las desviaciones tienen causa raiz y responsable de la **accion**, no culpable.

## Verificacion final

- Las dos rutas existen y el HTML abre sin red.
- Ninguna cifra del resumen contradice al JSON: si dices "vamos retrasados", `desviacion.sentido` dice `retrasado`.
- Cada riesgo lleva su `origen`, y cada desviacion y recomendacion su responsable y plazo.
- Los avisos del script estan recogidos en el informe o explicados en el resumen. Ninguno se ha ignorado.

## Siguiente paso sugerido

- Si hay bloqueos en el camino critico: resolverlos es la unica accion que mueve la fecha.
- Si hay fases listas y ningun change abierto: `aisdd open change` sobre la primera.
- Si la desviacion es estructural y no coyuntural: `aisdd roadmap` para re-fasear, o `aiba sprint-planning` para rebalancear.
- Para medir cuanto esta ayudando la IA en este proyecto: `aiba metrics`.
