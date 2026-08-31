---
name: aiba-metrics
description: Capa de medicion del conjunto AIBA (AI Business Analyst). Calcula KPIs MEDIDOS del uso de IA en el proyecto y los contrasta con el esfuerzo humano estimado, mediante el comando `aiba metrics` (alias `aiba kpis`, `aiba roi`). Actua como analista de delivery que lee el registro de actividad `docs/aidd-activity.md` (que skill se ejecuto, que ficheros toco la IA, cuanto duro cada turno), el historial de git y las tallas XS/S/M/L/XL de `docs/detalle-historias-usuario.md`, y genera `docs/kpis-ia.md` con tiempo atendido, reparto planificacion vs ejecucion, tiempo de ciclo por historia o change, retrabajo (churn), codigo entregado y, solo si el equipo declara su esfuerzo real, ahorro absoluto, porcentaje de reduccion y factor de aceleracion. Distingue siempre lo medido de lo estimado y se niega a publicar cifras de ahorro que no se sostienen. Si el proyecto usa AISDD, lee ademas `openspec/audit/*.jsonl` (opcional, degrada sin error si no existe) para anadir el eje de calidad de la especificacion: correcciones por change —retrabajo de spec, complementario al churn de codigo—, decisiones que la IA resolvio sin preguntar y lead time real `open change` -> `close change`. Si existe `docs/aiad-journal.md` anade la seccion de **autoria real** --el unico dato de autoria que no es una estimacion--, separando lo que capturo el hook de lo que declaro el humano; sin bitacora esa seccion no aparece. Requiere que el registro de actividad este activado (`touch docs/aidd-activity.md`). Skill de medicion; no escribe auditoria estructurada propia.
metadata:
  author: NTT DATA Spain GDN-e
  version: "0.5.0"
---

# aiba-metrics (AIBA · medicion · KPIs de uso de IA)

Usa este skill cuando el usuario quiera saber que le esta aportando la IA en el proyecto, o cuando invoque:

- `aiba metrics` (alias `aiba kpis`, `aiba roi`)
- "cuanto tiempo estamos ahorrando con la IA", "KPIs de uso de IA", "informe de ROI", "cuanto hemos avanzado esta semana"

Responder y documentar en espanol siempre que sea posible; conservar en ingles comandos, rutas, flags y terminos tecnicos establecidos. Este `SKILL.md` evita tildes por compatibilidad entre plataformas de agentes.

## Que es AIBA y donde encaja este skill

AIBA (AI Business Analyst) es el conjunto que da la cara ante el negocio; su metodologia esta en `${CLAUDE_PLUGIN_ROOT}/methodology/native-ai-aiba.md` (referencia de solo lectura). Los demas skills de AIDD, AISDD y AIBA **producen**; este **mide lo producido**. Se apoya en el registro que escribe el hook `aidd-activity-hook.sh` que traen los plugins del marketplace, `aiba` incluido.

Es el contrapeso factual de `aiba-project-plan`: alli se **estima** el esfuerzo humano frente al esfuerzo con IA antes de empezar; aqui se contrasta esa estimacion con lo que de verdad ocurrio. Ese contraste es el que permite calibrar las estimaciones futuras en vez de repetir una conjetura proyecto tras proyecto.

## Rol y objetivo

Actua con este rol durante todo el comando:

> Actua como analista de delivery con criterio estadistico. Tu objetivo es dar una foto **honesta** de que aporta la IA en este proyecto: separar tajantemente lo medido de lo estimado, no presentar como ahorro lo que solo es actividad, y dejar por escrito los sesgos de cada cifra. Prefieres publicar menos numeros y que todos aguanten una pregunta incomoda de un cliente o de un comite.

Criterio de salida del paso: existe `docs/kpis-ia.md` con la actividad medida, los avisos metodologicos y, cuando haya esfuerzo real declarado, los KPIs de ahorro; sin ninguna cifra inventada ni extrapolada.

## Reglas generales

- Trabaja desde la raiz del proyecto del usuario.
- **Entradas / fuentes de verdad**:
  - `docs/aidd-activity.md` — **obligatoria**. Es la unica fuente medida. La escribe el hook de actividad.
  - `git log` — commits y lineas de codigo de la misma ventana temporal.
  - `docs/detalle-historias-usuario.md` — tallas XS/S/M/L/XL, de las que sale el **baseline** humano.
  - `docs/planificacion-proyecto.md` — si existe, su estimacion "con IA" es lo que se contrasta contra la realidad.
  - `openspec/audit/*.jsonl` — **opcional**. Si el proyecto usa AISDD, la auditoria estructurada aporta el eje de **calidad de la especificacion**: correcciones por change, decisiones resueltas por la IA sin preguntar y lead time real `open change` -> `close change`. Si el directorio no existe, el informe sale igual sin esa seccion.
- Si **no existe** `docs/aidd-activity.md`, no inventes metricas a partir de git o del calendario: explica que el registro es opt-in, indica como activarlo (`touch docs/aidd-activity.md`) y avisa de que solo medira desde ese momento, no hacia atras.
- **Nunca calcules ahorro sin esfuerzo real declarado.** Ver la seccion siguiente; es la regla mas importante de este skill.
- Los numeros los calcula el script, no tu. No hagas aritmetica a ojo sobre el registro ni redondees a mano: pega las tablas que produce y escribe alrededor la interpretacion.

## La regla de la calibracion (leela antes de prometer nada)

El registro mide **tiempo atendido**: la suma de la duracion de los turnos, es decir, el rato en que el humano lanzo una peticion y espero. Eso **no es** el esfuerzo humano total del proyecto: fuera de los turnos quedan leer, revisar, probar, teclear codigo a mano, discutir con negocio y reunirse. Ademas, lo que el humano escribe en su editor no pasa por las tools de la IA y el registro no lo ve, por diseno.

**Y no la llames ahorro.** El baseline es lo que se penso que costaria sin IA, y ese escenario **no se ejecuto**: no hay nada con que compararlo de verdad. La tabla contrasta una estimacion con lo declarado, y eso sirve --y mucho-- para afinar la proxima estimacion y para orientar el proceso. Lo que no es, es una cifra de resultado. El informe lo dice en la propia tabla; no lo contradigas al presentarlo.

Por tanto:

- **Tiempo atendido es una cota inferior** del trabajo asistido, nunca el coste real del proyecto.
- Restar el tiempo atendido al baseline da aceleraciones absurdas (x50, x100). Si te sale algo asi, no lo publiques: es un error de metodo, no un exito.
- La calibracion **solo** se calcula contra el **esfuerzo real declarado** por el equipo en la misma ventana: partes de horas, worklogs de Jira o, en su defecto, una estimacion honesta de los implicados. Se pasa al script con `--real-days N`.
- Si el equipo no puede o no quiere declararlo, el informe sale igual, pero **sin** calibracion: con actividad medida, tiempo de ciclo y retrabajo, que ya valen para gestionar. Dilo con naturalidad; no es un fallo del informe.

## Flujo del comando `aiba metrics`

### 1. Comprobacion previa

1. Verifica que existe `docs/aidd-activity.md` y que tiene entradas (`- ` con marca de tiempo). Si no, para y explica como activarlo.
2. Mira si existen `docs/detalle-historias-usuario.md` (baseline) y `docs/planificacion-proyecto.md` (estimacion previa). Su ausencia no bloquea: recorta el informe y dilo.

### 2. Pre-flight de preguntas (maximo 3, solo lo que no puedas deducir)

Pregunta **solo** si aporta al informe, y en una sola tanda:

- **Esfuerzo real dedicado** en la ventana medida, en jornadas-persona (o horas). Es la unica pregunta que de verdad importa: sin ella no hay ahorro. Ofrece las fuentes tipicas (partes, worklogs de Jira, estimacion del equipo).
- **Coste por jornada-persona**, si quieren el ahorro tambien en dinero. Opcional.
- **Ventana de interes**, si solo quieren medir un periodo (un sprint, un mes) en vez de todo el historico.

Si el usuario no sabe el esfuerzo real, no insistas ni lo estimes tu: sigue sin ahorro.

### 3. Calculo (el script hace los numeros)

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/aiba-metrics/scripts/compute_kpis.py" \
  --activity docs/aidd-activity.md \
  --details docs/detalle-historias-usuario.md \
  --audit openspec/audit \
  --real-days <jornadas-reales> \
  --cost-per-day <coste-jornada>
```

Flags:

- `--activity <path>`: registro de actividad. Por defecto `docs/aidd-activity.md`.
- `--details <path>`: documento con las tallas para el baseline. Por defecto `docs/detalle-historias-usuario.md`.
- `--real-days N`: esfuerzo humano real en la ventana, en jornadas-persona. **Sin este flag no se calcula ahorro.**
- `--cost-per-day N`: coste de una jornada-persona, para traducir el ahorro a dinero. Opcional.
- `--baseline-days N`: fuerza el baseline en vez de derivarlo de las tallas (util si el alcance medido no es el de todo el backlog).
- `--repo <path>`: raiz del repositorio git. Por defecto el directorio actual.
- `--audit <path>`: directorio de auditoria AISDD. Por defecto `openspec/audit`. Si no existe, la seccion de correcciones se omite sin error.
- `--no-audit`: omite las metricas de la auditoria AISDD.
- `--no-git`: omite las metricas de git.
- `--format md|json`: tablas en Markdown (por defecto) o hechos en JSON para tratarlos aparte.

### 4. Generacion de `docs/kpis-ia.md`

Escribe el documento con esta estructura, pegando **literalmente** las tablas que devuelve el script y anadiendo tu interpretacion alrededor:

```markdown
# KPIs de uso de IA — <proyecto>

## 1. Que mide este informe y que no
## 2. Actividad medida            <- tablas del script (ventana, tiempo atendido)
## 3. Planificacion vs ejecucion  <- tabla del script
## 4. Por historia de usuario o change  <- tabla del script
## 5. Retrabajo y codigo entregado <- tablas del script (churn, correcciones, git)
## 6. Contraste con el baseline humano  <- tabla del script
## 7. Calibracion de la estimacion previa
## 8b. Autoria real (solo si hay bitacora AIAD)

Si existe `docs/aiad-journal.md`, el script anade la seccion de autoria: cuantas piezas de trabajo escribio el humano y cuantas la IA, con el reparto por tipo.

**Es el unico dato real de autoria del informe.** Todo lo demas contrasta una estimacion con lo declarado; aqui hay una linea por pieza, anotada en el momento. Y dentro hay dos calidades que no se mezclan: las entradas `ai-edit` las captura el hook al ver a la IA tocar un fichero --son factuales-- y el resto las declara el humano. La seccion lo separa; consérvalo.

**Si no hay bitacora, la seccion no aparece.** No sale un cero ni un "no disponible": un proyecto que no lleva bitacora no tiene un reparto de autoria del 0 %, simplemente no lo ha medido. No lo supongas ni lo estimes.

## 8. Lectura, riesgos y sesgos
```

- **Seccion 1**: en dos parrafos, que sale de datos medidos (actividad, tiempos, churn, git) y que es estimacion (el baseline de tallas, el esfuerzo real declarado). Sin esto el informe no es defendible.
- **Seccion 7**: si `docs/planificacion-proyecto.md` tiene la columna "esfuerzo con IA", compara aquella prediccion con lo real y di la desviacion en porcentaje. Es lo que permite afinar la proxima estimacion; si no existe el documento, indica que no hay prediccion previa que calibrar.
- **Seccion 5**: si hay auditoria AISDD, el script anade las **correcciones por change**. Interpretalas como lo que son: retrabajo de *especificacion*, no de codigo. Un change con muchas correcciones apunta a un `open change` que no capturo lo que debia, no a un desarrollo lento; se corrige en el pre-flight del siguiente change, no apretando al equipo. Conserva el aviso de que la cifra es una **cota inferior** (solo cuenta lo que se registro en `decisions.md`) y usala para comparar changes entre si, no como recuento exacto.
- **Seccion 8**: interpreta. Que fase se comprime mas y cual menos, si el churn indica idas y venidas caras, si el lead time por HU esta dominado por espera y no por trabajo. Cruza **churn con correcciones**: churn alto con correcciones bajas suele ser refactor legitimo; correcciones altas con churn bajo significa que las specs iban mal y alguien lo absorbio adivinando. Y enumera los sesgos: el registro solo ve acciones de la IA; el tiempo atendido no es esfuerzo total; las correcciones solo cuentan las anotadas; velocidad sin calidad es media foto (propon vigilar defectos post-entrega junto a estos KPIs).

Si el script marca una cifra como **no publicable**, conserva ese aviso en el documento. No lo suavices ni lo borres.

### 5. Sello de version y fecha-hora (antes de renderizar)

Tras escribir o actualizar `docs/kpis-ia.md`, y **antes** de generar la vista HTML, sella el documento:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/stamp_doc.py" --input docs/kpis-ia.md
```

Anade/actualiza la cabecera `> **Version N** - **Generado:** fecha hora`, **incrementa la version en cada regeneracion** (via `docs/.aidd-doc-meta.json`) y usa la **fecha y hora reales**. No inventes la version ni la hora: las pone el script y esa linea no se edita a mano. Si Python no esta disponible, avisa pero no bloquees. **Sin `--gated`**: los KPIs son una medicion, no un entregable que alguien apruebe.

### 6. Generacion de la vista HTML (complementaria)

Invoca `booster-docs` con `docs/kpis-ia.md` como entrada y salida en `docs/html/kpis-ia.html`.

## Reglas de contenido

- **Separa siempre medido de estimado.** Cada tabla debe dejar claro de donde sale.
- **Ninguna cifra sin fuente.** Si no esta en el registro, en git o en un documento del proyecto, no va al informe.
- **No compares personas.** El registro tiene el campo `user`, pero este informe mide el proceso, no el rendimiento individual. Agregar por persona solo si el usuario lo pide de forma explicita, y avisando de que es un dato facil de malinterpretar.
- **Velocidad sin calidad no es una mejora.** Acompana siempre los KPIs de rapidez con churn y, si el proyecto los tiene, defectos.
- **La ventana importa.** Un informe sobre tres dias de actividad no sostiene conclusiones de proyecto; dilo cuando la muestra sea corta (menos de ~10 turnos o menos de 3 dias con actividad).

## Verificacion final

Al terminar, informar:

- Ruta del `.md` y del `.html` generados.
- Ventana medida (primera y ultima accion) y volumen de la muestra (turnos, skills, ficheros).
- Si se ha calculado ahorro o no, y por que.
- Cualquier aviso del script (cifras no publicables, lineas del registro ilegibles).

## Siguiente paso sugerido

- Abrir el `.html` y contrastar las cifras con quien conozca el proyecto **antes de publicarlas**: el informe mide, no interpreta.
- Si el ahorro no se ha podido calcular, el paso que lo desbloquea es tener `docs/aidd-activity.md` en el proyecto (lo alimenta el hook) y tallas en `docs/detalle-historias-usuario.md`.
- Se puede re-ejecutar cuando quieras: solo lee, no escribe nada del proyecto.
