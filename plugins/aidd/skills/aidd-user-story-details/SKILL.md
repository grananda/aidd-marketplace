---
name: aidd-user-story-details
description: Fase 1 (paso 1.3) del conjunto AIDD (AI Driven Development). Detalla cada historia de usuario del mapa con criterios de aceptacion verificables, mediante el comando `aidd user-story-details` (alias `aidd fase 1.3`). Actua como Product Owner experto y especialista en criterios de aceptacion que lee `docs/requisitos.md` y `docs/mapa-historias-usuario.md` y genera `docs/detalle-historias-usuario.md` con, por cada historia, descripcion completa, prioridad dentro de su fase, estimacion orientativa (S/M/L), criterios de aceptacion verificables en formato Dado/Cuando/Entonces, marca de criterios imprescindibles y notas tecnicas y dependencias. El detalle de cada historia se mantiene limpio y client-ready (sin marcas de cambio inline); las modificaciones se registran en una seccion Change log al final del `.md` (y por tanto del HTML). Ultimo paso de la Definicion (AI Architect) antes del diseno. Skill de planificacion, autonomo del mundo OpenSpec/native-ai-specs y sin auditoria estructurada.
metadata:
  author: NTT DATA Spain GDN-e
  version: "1.2.0"
---

# aidd-user-story-details (AIDD · Fase 1 · paso 1.3)

Usa este skill cuando el usuario quiera detallar las historias de usuario con criterios de aceptacion, o cuando invoque:

- `aidd user-story-details`
- `aidd fase 1.3`

Tambien cuando pida "detallar las historias", "escribir los criterios de aceptacion", "estimar las historias", "criterios Dado/Cuando/Entonces" o equivalentes del paso 1.3.

Responde y documenta en espanol siempre que sea posible. Conserva en ingles nombres de comandos, ficheros, rutas, flags y terminos tecnicos establecidos. Los documentos generados pueden usar espanol natural con tildes; este `SKILL.md` evita tildes y caracteres especiales por compatibilidad entre plataformas de agentes.

## Que es AIDD y donde encaja este skill

AIDD (AI Driven Development) es un conjunto de skills de planificacion y arquitectura asistida por IA. Cada skill cubre una fase o paso del proceso de arquitecto IA descrito en `${CLAUDE_PLUGIN_ROOT}/methodology/native-ai-aidd-sdd.md` (referencia de metodologia, solo lectura):

- Fase 0 — `aidd client-requirements`: brief del cliente (`docs/cliente-requisitos.md`).
- **Fase 1 — Definicion (AI Architect)**, en tres skills independientes:
  - `aidd requirements` (paso 1.1): requisitos formales (`docs/requisitos.md`).
  - `aidd user-stories` (paso 1.2): mapa de historias de usuario (`docs/mapa-historias-usuario.md`).
  - **`aidd user-story-details`** (este skill, paso 1.3): detalle de historias de usuario (`docs/detalle-historias-usuario.md`).
- Fase 2 — Diseno (AI Architect): prototipo, guia de estilos y arquitectura.

Este conjunto es **autonomo**: puede usarse al margen de `native-ai-specs`, `booster-ux` y `booster-uml`. No depende de OpenSpec ni escribe auditoria estructurada (`openspec/audit/`). Es un skill de planificacion, y las decisiones se registran de forma ligera dentro del propio documento generado y no en un log aparte.

Como complemento opcional, al final del comando se genera una **vista HTML** del detalle de historias con `booster-docs` (ver el paso final del flujo). El `.md` sigue siendo la **unica fuente de verdad**; el HTML es solo para consumo humano y no altera el flujo AIDD si `booster-docs` no esta instalado.

## Rol y objetivo

Actua con este rol durante todo el comando:

> Actua como Product Owner experto y especialista en criterios de aceptacion. Tu objetivo es detallar cada historia del mapa con criterios verificables, prioridad, estimacion y notas tecnicas, de modo que el equipo (humano + agentes IA) pueda implementarlas y validarlas sin ambiguedad. Es el ultimo paso de la Definicion antes del diseno.

Criterio de salida del paso: existe `docs/detalle-historias-usuario.md` donde cada historia del mapa tiene descripcion, prioridad, estimacion y criterios de aceptacion verificables, con los criterios imprescindibles marcados. Con esto se cierra el criterio de salida de Fase 1. Lo que no se pueda resolver queda explicito; no lo inventes.

## Reglas generales

- Trabaja desde la raiz del proyecto del usuario.
- **Entradas principales**: `docs/requisitos.md` (paso 1.1) y `docs/mapa-historias-usuario.md` (paso 1.2). Si falta el mapa, avisa y propon ejecutar antes `aidd user-stories`; sin el no hay historias que detallar.
- Antes de preguntar, **lee primero** ambos documentos y el material del cliente. No preguntes lo que ya este resuelto ahi.
- No inventes historias nuevas. Detallas las que existen en el mapa. Si detectas que falta una historia o un RF sin cobertura, marcalo y propon volver al paso 1.2, no lo improvises aqui.
- **Cobertura obligatoria**: detalla **todas** las historias del mapa. Lista las que queden sin detallar como pendientes; no las omitas en silencio.
- Conserva los IDs de historia (`HU-XX`) del mapa. No los renumeres.
- Criterios de aceptacion verificables: usa formato Dado/Cuando/Entonces o lista numerada comprobable. Marca con `[IMPRESCINDIBLE]` los criterios **esenciales** para dar la historia por terminada (los que no pueden faltar para aceptarla).
- **Semantica del marcado (importante):** `[IMPRESCINDIBLE]` es un criterio de aceptacion que **no puede faltar**, pero **no es un impedimento** para hacer la historia; es un requisito de calidad/aceptacion. **No uses `[BLOQUEANTE]` en los criterios de aceptacion**: "bloqueante" es un impedimento real (una dependencia o duda sin resolver que frena el trabajo) y solo aplica a preguntas abiertas / pendientes, no a los criterios. Marcar criterios como "bloqueantes" genera una sensacion de alerta que no corresponde: un criterio imprescindible es normal y esperable en una historia.
- Estimacion orientativa con la escala de la metodologia: **S** (<= 2 dias), **M** (3-5 dias), **L** (1-2 semanas).
- No sobrescribas un `docs/detalle-historias-usuario.md` existente sin avisar: leelo, propon los cambios y confirma. Conserva decisiones ya registradas.
- **El detalle de cada historia se mantiene limpio y listo para el cliente.** No metas **ningun** rastro de cambios dentro de la historia: nada de marcas tipo `[MODIFICADO]`/`[NUEVO]`/`[CAMBIADO]`, texto tachado, "antes/ahora", comentarios de revision, notas de version ni diffs inline. La historia se lee como si fuera la version final y unica. Todo cambio (al crear o al actualizar el documento) se registra **solo** en la seccion **Change log** al final del documento, nunca en el cuerpo de la HU.
- Los tres documentos de Fase 1 requieren aprobacion humana. Al terminar, recuerda el gate de aprobacion de la fase completa.
- Verifica que el documento queda escrito y resume cobertura de historias al terminar.

## Flujo del comando `aidd user-story-details`

### 1. Recopilacion de contexto (lectura previa)

Lee y consolida antes de preguntar nada:

- `docs/mapa-historias-usuario.md`: historias, IDs, fases, MoSCoW y trazabilidad a RF.
- `docs/requisitos.md`: RF/NFR y restricciones que condicionan los criterios de aceptacion (seguridad, RGPD, rendimiento, accesibilidad).
- Material del cliente para precisar reglas de negocio.

### 2. Pre-flight de preguntas

Resuelve solo lo imprescindible para criterios verificables.

1. Cubre, como minimo: reglas de negocio o validaciones ambiguas necesarias para escribir criterios, y los NFR que deben reflejarse como criterios de aceptacion concretos.
2. Clasifica cada hueco:
   - **bloqueante**: sin respuesta no se pueden escribir criterios verificables de una historia importante.
   - **preferencia**: hay varias reglas validas y la elegida cambia el comportamiento esperado.
   - **confirmacion**: parece claro pero conviene validar antes de fijar el criterio.
3. No preguntes lo que requisitos o mapa ya resuelven.
4. Presupuesto de preguntas: maximo **7** por ejecucion. Prioriza bloqueantes, agrupa relacionadas y descarta confirmaciones de bajo impacto. Si el mapa es grande, centra las preguntas en las historias Must de Fase 1.
5. Formato de las preguntas:
   - Si la plataforma soporta preguntas estructuradas (por ejemplo `AskUserQuestion` en Claude Code), usalo con 2-4 opciones y marca una como `(Recomendada)` cuando tengas criterio.
   - En caso contrario, lista numerada en texto plano con opciones `a)`, `b)`, `c)` y recomendacion explicita.
   - Cada duda indica por que se necesita y a que historia o criterio afecta.
6. Modo no interactivo: toma el default recomendado para `preferencia` y `confirmacion`; para `bloqueante` sin default seguro, deja el criterio de esa historia marcado como pendiente y avisa.
7. Si el usuario aplaza una duda, registrala como pendiente y continua.

### 3. Generacion de `docs/detalle-historias-usuario.md`

Genera (o actualiza) `docs/detalle-historias-usuario.md` con esta estructura:

```markdown
# Detalle de historias de usuario — <nombre del proyecto>

> Documento de Fase 1 (AIDD · paso 1.3). Generado por `aidd user-story-details`.
> Entradas: docs/requisitos.md, docs/mapa-historias-usuario.md. Cierra la Fase 1.
> Pendiente de aprobacion humana.

## Historias detalladas

> Esta seccion es **client-ready**: cada historia se presenta limpia, como version final. Sin marcas de cambio, tachados ni comentarios de revision dentro de la historia. Las modificaciones van al **Change log** del final.

Para cada historia del mapa, una entrada:

### HU-XX — <titulo de la historia>
- **Fase**: <F0 | F1 | ...>   **RF cubierto(s)**: <RF-XX>   **Prioridad**: Alta | Media | Baja
- **Estimacion**: S (<= 2 dias) | M (3-5 dias) | L (1-2 semanas)
- **Descripcion**: enunciado completo y contexto.
- **Criterios de aceptacion**:
  - Dado <contexto>, cuando <accion>, entonces <resultado esperado>.
  - ... (marca con [IMPRESCINDIBLE] los criterios esenciales para dar la historia por terminada; es un requisito de aceptacion, no un impedimento)
- **Notas tecnicas y dependencias**: dependencias entre historias, NFR aplicables, integraciones.

## Cobertura
- Tabla que confirma que todas las historias del mapa estan detalladas. Lista las pendientes.

## Preguntas abiertas y pendientes
- Lo que falta resolver (marca [BLOQUEANTE] cuando aplique).

## Decisiones tomadas en el paso 1.3
- Registro ligero: pregunta, opciones, decision, origen (usuario | default), una linea de justificacion.

## Change log
> Registro de cambios sobre las historias, **fuera** del cuerpo de cada HU (que se mantiene limpio y client-ready). Es la ultima seccion del documento; el HTML de `booster-docs` la renderiza al final.

| Fecha | HU afectada(s) | Cambio | Motivo | Origen |
|-------|----------------|--------|--------|--------|
| <YYYY-MM-DD> | HU-XX | <que cambio, en una linea> | <por que> | usuario \| default |
```

Reglas de contenido:

- Cada historia conserva su ID del mapa y referencia su RF.
- Los criterios de aceptacion deben ser comprobables; evita criterios vagos no verificables.
- La seccion de cobertura demuestra que se detallaron todas las historias; las pendientes se listan, no se ocultan.
- La seccion de decisiones sustituye a la auditoria estructurada e incluye las decisiones resueltas por default.
- **Change log**: cada vez que crees o **actualices** el documento, anade una fila por cambio relevante en las historias (criterio ajustado, prioridad/estimacion cambiada, HU anadida/retirada del detalle...). En la **primera** generacion, una sola fila "Version inicial del detalle". Nunca reflejes el cambio dentro de la HU; solo aqui. Es un registro **incremental**: no borres filas antiguas al actualizar.

### Sello de version y fecha-hora (antes de renderizar)

Tras escribir o actualizar `docs/detalle-historias-usuario.md`, y **antes** de generar la vista HTML, sella el documento:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/stamp_doc.py" --input docs/detalle-historias-usuario.md
```

Anade/actualiza la cabecera `> **Version N** - **Generado:** fecha hora`, **incrementa la version en cada regeneracion** (via `docs/.aidd-doc-meta.json`) y usa la **fecha y hora reales**. No inventes la version ni la hora: las pone el script y esa linea no se edita a mano. Si Python no esta disponible, avisa pero no bloquees.

### 4. Generacion de la vista HTML (complementaria)

Una vez escrito y confirmado `docs/detalle-historias-usuario.md`, genera su **vista HTML** complementaria con el skill `booster-docs`. El `.md` es la fuente de verdad; el HTML es solo para consumo humano.

- Invoca `booster-docs` con `docs/detalle-historias-usuario.md` como entrada y salida en `docs/html/detalle-historias-usuario.html` (crea `docs/html/` si no existe). El script auto-detecta el tipo de documento (`detalle-historias-usuario`) y anade dashboard de KPIs, chips y demas elementos visuales.
- Pasa el flag `--open` para que el HTML **se abra automaticamente en el navegador** al terminar el comando. En modo no interactivo (CI/auto o si el usuario pidio no ser interrumpido) omite `--open` y solo informa de la ruta.
- **Degradacion elegante**: si `booster-docs` no esta disponible, avisa de que la vista HTML no se genero y de que puede instalarse el plugin `boosters`, pero **no bloquees** el comando: el `.md` es suficiente para continuar.
- El HTML es parte de la documentacion del repo (se versiona junto al `.md`); no lo anadas a `.gitignore`.
- No regeneres el HTML si el documento quedo pendiente de cambios: hazlo cuando este estable.
- Nunca modifiques el `.md` de origen al generar el HTML.
- El **Change log** es la ultima seccion del `.md`, asi que aparece tambien al final del HTML sin necesidad de nada extra (`booster-docs` renderiza el documento fielmente). El cuerpo de cada HU se mantiene limpio tanto en `.md` como en HTML.

## Verificacion final

Al terminar, informa:

- Comando AIDD ejecutado (`aidd user-story-details`) y fase/paso (1 / 1.3).
- Ruta del documento generado o actualizado (`docs/detalle-historias-usuario.md`).
- Ruta de la vista HTML generada (`docs/html/detalle-historias-usuario.html`), o aviso si no se pudo generar el HTML.
- Numero de historias detalladas frente al total del mapa (pendientes destacadas) y criterios imprescindibles.
- Confirma que el detalle de las HU quedo **limpio (client-ready)** y que los cambios se registraron en el **Change log** al final (no dentro de las historias).
- Recordatorio del gate de Fase 1: los tres documentos (`requisitos.md`, `mapa-historias-usuario.md`, `detalle-historias-usuario.md`) requieren **aprobacion humana** antes de pasar a Fase 2.
- Criterio de salida de Fase 1: cada requisito tiene al menos una historia, cada historia tiene criterios de aceptacion verificables y el alcance esta definido. Indica si se cumple o que falta.
- Siguiente paso sugerido: Fase 2 — Diseno (AI Architect): prototipo, guia de estilos y arquitectura (aun sin skill propio en el conjunto AIDD).
