---
name: aidd-project-plan
description: Fase 3.5 (paso 3.5.1) del conjunto AIDD (AI Driven Development), capa de planificacion de entrega (Delivery). Genera el plan de recursos del proyecto una vez aprobado el diseno, mediante el comando `aidd project-plan` (alias `aidd planificacion proyecto`). Actua como delivery manager tecnico que lee `docs/arquitectura-base.md`, `docs/mapa-historias-usuario.md` y `docs/detalle-historias-usuario.md` y genera `docs/planificacion-proyecto.md` con perfiles y equipo recomendado, software y licencias, infraestructura y entornos, doble estimacion de esfuerzo en paralelo (humano clasico a partir de XS/S/M/L/XL vs esfuerzo estimado con IA) con KPIs de la diferencia (ahorro, % de reduccion, factor de aceleracion), dependencias y prerequisitos de recursos, y riesgos de recursos. Es el insumo del skill `aidd-sprint-planning`. Skill de planificacion, autonomo del mundo OpenSpec/aisdd-specs y sin auditoria estructurada.
metadata:
  author: NTT DATA Spain GDN-e
  version: "1.1.0"
---

# aidd-project-plan (AIDD · Fase 3.5 · paso 3.5.1 · recursos)

Usa este skill cuando el usuario quiera un plan de recursos del proyecto (personas, licencias, software, infraestructura) una vez aprobado el diseno, o cuando invoque:

- `aidd project-plan`
- `aidd planificacion proyecto`

Tambien cuando pida "plan de recursos", "que equipo necesito", "perfiles y licencias", "plan de proyecto" o equivalentes.

Responde y documenta en espanol siempre que sea posible. Conserva en ingles nombres de comandos, ficheros, rutas, flags y terminos tecnicos establecidos. Los documentos generados pueden usar espanol natural con tildes; este `SKILL.md` evita tildes y caracteres especiales por compatibilidad entre plataformas de agentes.

## Que es AIDD y donde encaja este skill

AIDD (AI Driven Development) es un conjunto de skills de planificacion y arquitectura asistida por IA. Cada skill cubre una fase o paso del proceso descrito en `${CLAUDE_PLUGIN_ROOT}/methodology/native-ai-aidd-sdd.md` (referencia de metodologia, solo lectura):

- Fase 0 — `aidd client-requirements`.
- Fase 1 — `aidd requirements`, `aidd user-stories`, `aidd user-story-details`.
- Fase 2 — Diseno (AI Architect): `aidd prototype-architecture`, `aidd prototype`, `aidd style-guide`, `aidd architecture-proposal`, `aidd architecture`.
- **Fase 3.5 — Planificacion de entrega (Delivery)** — capa que traduce el diseno y el roadmap a algo que un equipo (humano + agentes) consume directamente:
  - **`aidd project-plan`** (este skill, paso 3.5.1): plan de recursos (`docs/planificacion-proyecto.md`). Se ejecuta tras aprobar la Fase 2.
  - `aidd sprint-planning` (paso 3.5.2): distribucion del trabajo en sprints (`docs/sprint-plan.md`). Se ejecuta cuando existe el roadmap.

Este conjunto es **autonomo**: puede usarse al margen de `aisdd-specs`, `booster-ux` y `booster-uml`. No depende de OpenSpec ni escribe auditoria estructurada. Las decisiones se registran de forma ligera dentro del propio documento generado.

Como complemento opcional, al final del comando se genera una **vista HTML** del plan de proyecto con `booster-docs` (ver el paso final del flujo). El `.md` sigue siendo la **unica fuente de verdad**; el HTML es solo para consumo humano y no altera el flujo AIDD si `booster-docs` no esta instalado.

> Este skill NO sustituye al `roadmap` del AI Lead (Fase 3), que fasea los changes segun el presupuesto de contexto del modelo. Aporta la dimension que el SDD no cubre: **los recursos humanos y materiales** necesarios para ejecutar ese plan.

## Rol y objetivo

Actua con este rol durante todo el comando:

> Actua como delivery manager tecnico (gestion de proyecto con criterio de arquitectura). Tu objetivo es derivar, a partir del diseno aprobado, que recursos hacen falta para construir el producto: perfiles y equipo, software y licencias, infraestructura y entornos, esfuerzo (en doble estimacion humano vs IA), dependencias de recursos y riesgos. No planificas el calendario (eso es `aidd sprint-planning`); planificas el QUE se necesita, no el CUANDO.

Criterio de salida del paso: existe `docs/planificacion-proyecto.md` con perfiles/equipo, software/licencias, infraestructura, la doble estimacion de esfuerzo (humano clasico vs IA) con sus KPIs de diferencia, dependencias de recursos y riesgos, derivados de la arquitectura y las historias, sin inventar lo que no este soportado por los documentos. Lo que no se pueda concluir queda como supuesto explicito.

## Reglas generales

- Trabaja desde la raiz del proyecto del usuario.
- **Entradas / fuentes de verdad**: `docs/arquitectura-base.md` (stack, capas, despliegue, riesgos), `docs/mapa-historias-usuario.md` y `docs/detalle-historias-usuario.md` (alcance y estimaciones XS/S/M/L/XL). Apoyate en `docs/requisitos.md` (NFR, restricciones) y `docs/cliente-requisitos.md` (contexto de equipo y negocio).
- Si falta `docs/arquitectura-base.md`, avisa y propon completar antes la Fase 2 (`aidd architecture`); sin la arquitectura no hay base para dimensionar recursos.
- Antes de preguntar, **lee primero** esos documentos. No preguntes lo que ya este resuelto ahi (p. ej. el stack ya esta decidido en la arquitectura).
- **No inventes recursos sin soporte**: cada perfil, licencia o pieza de infraestructura debe derivarse de una decision de arquitectura, un NFR o una historia. Si lo recomiendas por buena practica, marcalo como recomendacion, no como necesidad derivada.
- **Costes**: por defecto, tratamiento **cualitativo con rangos** (marca que es open source y que tiene coste; da ordenes de magnitud, no cifras de precision). Solo da cifras concretas si el usuario las pide y aporta tarifas; en ese caso, documenta los supuestos.
- Mapea los perfiles a los roles del SDD cuando aplique (AI Architect, AI Lead Front/Back, AI Developer, Outcome Validator) e indica si la IA (p. ej. Claude Code) se contempla como recurso.
- No sobrescribas un `docs/planificacion-proyecto.md` existente sin avisar: leelo, propon los cambios y confirma.
- Este documento requiere aprobacion humana. Al terminar, deja claro que esta pendiente de revision.

## Flujo del comando `aidd project-plan`

### 1. Recopilacion de contexto (lectura previa)

Lee y consolida antes de preguntar: `arquitectura-base.md` (stack por capa, despliegue, observabilidad, riesgos), `mapa-historias-usuario.md` y `detalle-historias-usuario.md` (historias, fases y estimaciones), `requisitos.md` (NFR y restricciones) y `cliente-requisitos.md` (tamano de equipo, contexto interno).

Extrae las **capacidades tecnicas** que el stack exige (por ejemplo: frontend SPA, backend, persistencia, tiempo real, contenedores, accesibilidad, QA) para derivar los perfiles.

### 2. Pre-flight de preguntas

Resuelve solo lo imprescindible para un plan de recursos util.

1. Cubre, como minimo: composicion/tamano de equipo objetivo y si la planificacion usa los **roles SDD** o roles tradicionales de equipo; restricciones de recursos ya conocidas (presupuesto, personas disponibles, proveedores obligatorios).
2. Clasifica cada hueco en **bloqueante**, **preferencia** o **confirmacion**.
3. No preguntes lo que arquitectura, requisitos o brief ya resuelven.
4. Presupuesto de preguntas: maximo **7** por ejecucion. Prioriza bloqueantes y agrupa relacionadas.
5. Formato: si la plataforma soporta preguntas estructuradas (por ejemplo `AskUserQuestion`), usalo con 2-4 opciones y marca una como `(Recomendada)`; si no, lista numerada con opciones y recomendacion.
6. Modo no interactivo: toma el default recomendado para `preferencia` y `confirmacion`; deja los `bloqueante` sin default como supuestos en el documento.
7. Si el usuario aplaza una duda, registrala como supuesto y continua.

### 3. Generacion de `docs/planificacion-proyecto.md`

Genera (o actualiza) `docs/planificacion-proyecto.md` con esta estructura:

```markdown
# Planificacion de proyecto (recursos) — <nombre del proyecto>

> Documento de Planificacion de entrega (AIDD). Generado por `aidd project-plan`.
> Fuentes: docs/arquitectura-base.md, docs/mapa-historias-usuario.md, docs/detalle-historias-usuario.md.
> Insumo de `aidd sprint-planning`. Pendiente de aprobacion humana.

## 1. Objetivo y resumen
- Que se va a construir (1-2 frases) y resumen del equipo y recursos necesarios.

## 2. Perfiles y equipo recomendado
- Por perfil: responsabilidades, skills concretos (ligados al stack/NFR), dedicacion orientativa y mapeo al rol SDD si aplica. Indica si la IA es un recurso.

## 3. Software, herramientas y licencias
- Herramientas por categoria (desarrollo, IA, repo/CI, runtime, observabilidad). Marca open source vs coste y orden de magnitud. Liga cada una a una decision de arquitectura o NFR.

## 4. Infraestructura y entornos
- Entornos (dev/pre/pro), hosting (segun despliegue de la arquitectura), almacenamiento y backups, red/acceso. Sin valores de secretos.

## 5. Estimacion de esfuerzo — humano clasico vs IA
Dos estimaciones **en paralelo** por fase (y por historia si aporta), para poder contrastarlas:

| Fase / Historia | Talla | Esfuerzo humano clasico | Esfuerzo estimado con IA | Diferencia |
|-----------------|-------|-------------------------|--------------------------|-----------|
| F1 / HU-03 | M | 3 d-persona | 1 d-persona | -2 (-67%) |
| F1 / HU-04 | L | 5 d-persona | 2 d-persona | -3 (-60%) |
| **Total** | | **X d-persona** | **Y d-persona** | **-(X-Y) (-Z%)** |

- **Esfuerzo humano clasico**: deriva de las tallas de `docs/detalle-historias-usuario.md` con la **escala de tallas** (1 d = jornada de 8 h; puntos fijos): **XS = 0,5 d · S = 1,5 d · M = 3 d · L = 5 d · XL = 8 d**. Suma los puntos por fase/historia; es volumen de trabajo, no calendario. Al ser puntos fijos, el total es exacto (no hay rangos ni punto medio que elegir).
- **Esfuerzo estimado con IA**: el mismo trabajo asumiendo la IA como recurso (p. ej. Claude Code). La IA genera el grueso; **lo no comprimible es dirigir, revisar y validar** (PR, criterios de aceptacion, e2e, accesibilidad, seguridad). Aplica una **compresion por naturaleza de la tarea**, no un % plano: boilerplate/CRUD/scaffolding comprime mucho; logica de dominio compleja, decisiones de diseno, integraciones delicadas o trabajo exploratorio comprimen poco. Es una **estimacion con supuestos**; marcalo como tal.

## 6. KPIs de esfuerzo (diferencia humano vs IA)
Cuadro de indicadores de la diferencia, calculados a partir de la tabla anterior:

| KPI | Valor |
|-----|-------|
| Esfuerzo humano total | X d-persona |
| Esfuerzo con IA total | Y d-persona |
| Ahorro absoluto | X - Y d-persona |
| Reduccion (%) | (X - Y) / X * 100 |
| Factor de aceleracion | X / Y (p. ej. x2,6) |
| Fase con mayor ahorro | <fase> (-N%) |
| Fase con menor ahorro | <fase> (-N%) |

- Calcula estos KPIs de forma consistente con la tabla de la seccion 5 (no cifras sueltas). Redondea a una cifra util.
- Si el usuario **no** contempla la IA como recurso, dilo y deja la columna/seccion IA como N/A (o con supuesto explicito), en vez de inventar una aceleracion.

## 7. Dependencias y prerequisitos de recursos
- Que debe estar disponible antes de empezar (accesos, entornos, licencias, perfiles) y dependencias entre recursos.

## 8. Riesgos de recursos y supuestos
- Riesgos (perfiles escasos, dependencias, licencias) y supuestos tomados. Incluye los supuestos de la compresion por IA. Marca [BLOQUEANTE] cuando aplique.

## 9. Decisiones tomadas
- Registro ligero: pregunta, opciones, decision, origen (usuario | default), una linea de justificacion.
```

Reglas de contenido:

- Cada recurso justificado y trazable a la arquitectura, un NFR o una historia. Nada generico de relleno.
- **Doble estimacion**: da siempre el esfuerzo humano clasico y el esfuerzo con IA en paralelo (seccion 5), y deriva de ahi los KPIs de la diferencia (seccion 6). El esfuerzo con IA se comprime segun la naturaleza de la tarea; no uses un porcentaje unico para todo. La cifra IA es una hipotesis con supuestos, no un dato cerrado.
- Costes cualitativos con rangos salvo que el usuario pida y aporte tarifas.
- La seccion 9 sustituye a la auditoria estructurada e incluye decisiones resueltas por default.

### Sello de version y fecha-hora (antes de renderizar)

Tras escribir o actualizar `docs/planificacion-proyecto.md`, y **antes** de generar la vista HTML, sella el documento:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/stamp_doc.py" --input docs/planificacion-proyecto.md
```

Anade/actualiza la cabecera `> **Version N** - **Generado:** fecha hora`, **incrementa la version en cada regeneracion** (via `docs/.aidd-doc-meta.json`) y usa la **fecha y hora reales**. No inventes la version ni la hora: las pone el script y esa linea no se edita a mano. Si Python no esta disponible, avisa pero no bloquees.

### 4. Generacion de la vista HTML (complementaria)

Una vez escrito y confirmado `docs/planificacion-proyecto.md`, genera su **vista HTML** complementaria con el skill `booster-docs`. El `.md` es la fuente de verdad; el HTML es solo para consumo humano.

- Invoca `booster-docs` con `docs/planificacion-proyecto.md` como entrada y salida en `docs/html/planificacion-proyecto.html` (crea `docs/html/` si no existe). El script auto-detecta el tipo de documento (`planificacion-proyecto`) y anade dashboard de KPIs, chips y demas elementos visuales.
- Pasa el flag `--open` para que el HTML **se abra automaticamente en el navegador** al terminar el comando. En modo no interactivo (CI/auto o si el usuario pidio no ser interrumpido) omite `--open` y solo informa de la ruta.
- **Degradacion elegante**: si `booster-docs` no esta disponible, avisa de que la vista HTML no se genero y de que puede instalarse el plugin `boosters`, pero **no bloquees** el comando: el `.md` es suficiente para continuar.
- El HTML es parte de la documentacion del repo (se versiona junto al `.md`); no lo anadas a `.gitignore`.
- No regeneres el HTML si el documento quedo pendiente de cambios: hazlo cuando este estable.
- Nunca modifiques el `.md` de origen al generar el HTML.

## Verificacion final

Al terminar, informa:

- Comando AIDD ejecutado (`aidd project-plan`).
- Ruta del documento generado o actualizado (`docs/planificacion-proyecto.md`).
- Ruta de la vista HTML generada (`docs/html/planificacion-proyecto.html`), o aviso si no se pudo generar el HTML.
- Resumen del equipo recomendado, software/licencias con coste y principales riesgos de recursos.
- **KPIs de esfuerzo humano vs IA**: esfuerzo humano total, esfuerzo con IA total, ahorro absoluto, % de reduccion y factor de aceleracion.
- Recordatorio: pendiente de **aprobacion humana**.
- Siguiente paso sugerido: `aidd sprint-planning` para distribuir el trabajo en sprints usando estos recursos (requiere `docs/roadmap.md`; si no existe, generarlo antes con el AI Lead via `aisdd roadmap`).
