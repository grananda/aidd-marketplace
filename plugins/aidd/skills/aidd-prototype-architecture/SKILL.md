---
name: aidd-prototype-architecture
description: Fase 2 (paso 2.1) del conjunto AIDD (AI Driven Development). Disena la arquitectura de un prototipo 100% mockeado para validar requisitos con el cliente, mediante el comando `aidd prototype-architecture` (alias `aidd fase 2.1`). Actua como Product Owner y arquitecto de software que lee `docs/mapa-historias-usuario.md` y `docs/detalle-historias-usuario.md` y genera `docs/arquitectura-base-prototipo.md` con stack minimo, componentes y modulos de los flujos principales, pantallas o endpoints clave, estrategia de mocks, datos de ejemplo del dominio, supuestos y exclusiones, y pasos minimos de implementacion. Primer paso del Diseno (AI Architect) y entrada de la implementacion del prototipo. Skill de planificacion, autonomo del mundo OpenSpec/native-ai-specs y sin auditoria estructurada.
metadata:
  author: NTT DATA Spain GDN-e
  version: "1.0.0"
---

# aidd-prototype-architecture (AIDD · Fase 2 · paso 2.1)

Usa este skill cuando el usuario quiera disenar la arquitectura de un prototipo mockeado para validar con el cliente, o cuando invoque:

- `aidd prototype-architecture`
- `aidd fase 2.1`

Tambien cuando pida "arquitectura del prototipo", "base para una demo mockeada", "como montar la demo de validacion" o equivalentes del paso 2.1.

Responde y documenta en espanol siempre que sea posible. Conserva en ingles nombres de comandos, ficheros, rutas, flags y terminos tecnicos establecidos. Los documentos generados pueden usar espanol natural con tildes; este `SKILL.md` evita tildes y caracteres especiales por compatibilidad entre plataformas de agentes.

## Que es AIDD y donde encaja este skill

AIDD (AI Driven Development) es un conjunto de skills de planificacion y arquitectura asistida por IA. Cada skill cubre una fase o paso del proceso de arquitecto IA descrito en `${CLAUDE_PLUGIN_ROOT}/methodology/native-ai-aidd-sdd.md` (referencia de metodologia, solo lectura):

- Fase 0 — `aidd client-requirements`: brief del cliente (`docs/cliente-requisitos.md`).
- Fase 1 — Definicion (AI Architect): `aidd requirements`, `aidd user-stories`, `aidd user-story-details`.
- **Fase 2 — Diseno (AI Architect)**:
  - **`aidd prototype-architecture`** (este skill, paso 2.1): arquitectura del prototipo (`docs/arquitectura-base-prototipo.md`).
  - `aidd prototype` (paso 2.2): implementacion del prototipo, redirige a `booster-ux`.
  - `aidd style-guide` (paso 2.3): guia de estilos (`docs/guia-estilos.md`).
  - `aidd architecture-proposal` (paso 2.3): propuesta de arquitectura (`docs/propuesta-arquitectura-base.md`).
  - `aidd architecture` (paso 2.4): arquitectura tecnica definitiva (`docs/arquitectura-base.md`).

Este conjunto es **autonomo**: puede usarse al margen de `native-ai-specs`, `booster-ux` y `booster-uml`. No depende de OpenSpec ni escribe auditoria estructurada (`openspec/audit/`). Es un skill de planificacion, y las decisiones se registran de forma ligera dentro del propio documento generado y no en un log aparte.

Como complemento opcional, al final del comando se genera una **vista HTML** de la arquitectura del prototipo con `booster-docs` (ver el paso final del flujo). El `.md` sigue siendo la **unica fuente de verdad**; el HTML es solo para consumo humano y no altera el flujo AIDD si `booster-docs` no esta instalado.

## Rol y objetivo

Actua con este rol durante todo el comando:

> Actua como Product Owner y arquitecto de software. Tu objetivo es disenar una arquitectura base **simple** para una demo 100% mockeada, orientada a validar requisitos con el cliente. Prioriza velocidad sobre correccion tecnica: todo lo externo se simula. No es la arquitectura definitiva (eso es 2.4).

Criterio de salida del paso: existe `docs/arquitectura-base-prototipo.md` con stack minimo, flujos principales, estrategia de mocks y pasos de implementacion, de forma que la demo se pueda recorrer de punta a punta sin bloqueos. Lo que no se pueda resolver queda explicito como supuesto o exclusion; no lo inventes en silencio.

## Reglas generales

- Trabaja desde la raiz del proyecto del usuario.
- **Entradas principales**: `docs/mapa-historias-usuario.md` y `docs/detalle-historias-usuario.md` (Fase 1). Si faltan, avisa y propon completarlas antes con `aidd user-stories` / `aidd user-story-details`.
- Antes de preguntar, **lee primero** esos documentos, `docs/requisitos.md`, `docs/cliente-requisitos.md` y el material del cliente. No preguntes lo que ya este resuelto ahi.
- **Todo se mockea**: APIs, BD, auth, notificaciones e integraciones se simulan. No disenes infraestructura real.
- No inventes flujos ni historias nuevas. Disena la demo para los flujos que ya existen en el mapa y el detalle.
- Marca explicitamente supuestos y exclusiones; el objetivo es validar, no cubrirlo todo.
- No sobrescribas un `docs/arquitectura-base-prototipo.md` existente sin avisar: leelo, propon los cambios y confirma.
- Este documento requiere aprobacion humana antes de implementar la demo. Al terminar, deja claro que esta pendiente de revision.
- Verifica que el documento queda escrito al terminar.

## Flujo del comando `aidd prototype-architecture`

### 1. Recopilacion de contexto (lectura previa)

Lee y consolida antes de preguntar nada: mapa y detalle de historias (flujos y criterios), `requisitos.md` (alcance y NFR relevantes para la demo) y `cliente-requisitos.md` (objetivo de la validacion).

Identifica los flujos clave que la demo debe permitir recorrer para validar con el cliente.

### 2. Pre-flight de preguntas

Resuelve solo lo imprescindible para una demo recorrible.

1. Cubre, como minimo: que flujos son imprescindibles para la validacion y que nivel de fidelidad visual espera el cliente para la demo.
2. Clasifica cada hueco en **bloqueante**, **preferencia** o **confirmacion**.
3. No preguntes lo que historias o brief ya resuelven.
4. Presupuesto de preguntas: maximo **7** por ejecucion. Prioriza bloqueantes y agrupa relacionadas.
5. Formato: si la plataforma soporta preguntas estructuradas (por ejemplo `AskUserQuestion`), usalo con 2-4 opciones y marca una como `(Recomendada)`; si no, lista numerada con opciones y recomendacion. Cada duda indica por que se necesita.
6. Modo no interactivo: toma el default recomendado para `preferencia` y `confirmacion`; deja los `bloqueante` sin default como pendientes en el documento.
7. Si el usuario aplaza una duda, registrala como pendiente y continua.

### 3. Generacion de `docs/arquitectura-base-prototipo.md`

Genera (o actualiza) `docs/arquitectura-base-prototipo.md` con esta estructura:

```markdown
# Arquitectura del prototipo — <nombre del proyecto>

> Documento de Fase 2 (AIDD · paso 2.1). Generado por `aidd prototype-architecture`.
> Entradas: docs/mapa-historias-usuario.md, docs/detalle-historias-usuario.md.
> Demo 100% mockeada para validacion con cliente. Pendiente de aprobacion humana.

## 1. Objetivo de la demo
- Que se quiere validar con el cliente y que flujos cubre.

## 2. Stack minimo
- Tecnologias elegidas priorizando velocidad. Justificacion breve.

## 3. Componentes y modulos
- Componentes/modulos para los flujos principales.

## 4. Pantallas o endpoints minimos
- Lo justo para recorrer los casos de uso clave de punta a punta.

## 5. Estrategia de mocks
- Que se simula (APIs, BD, auth, notificaciones, integraciones) y como.

## 6. Datos de ejemplo
- Datos mock coherentes con el dominio.

## 7. Supuestos y exclusiones
- Supuestos tomados y que queda explicitamente fuera de la demo.

## 8. Pasos minimos de implementacion
- Secuencia ordenada para construir la demo.

## 9. Decisiones tomadas en el paso 2.1
- Registro ligero: pregunta, opciones, decision, origen (usuario | default), una linea de justificacion.
```

Reglas de contenido:

- Mantenlo simple y orientado a validar. No es la arquitectura definitiva.
- La demo debe poder recorrerse de punta a punta sin bloqueos; comprueba que los pasos de la seccion 8 lo permiten.
- La seccion 9 sustituye a la auditoria estructurada e incluye decisiones resueltas por default.

### Sello de version y fecha-hora (antes de renderizar)

Tras escribir o actualizar `docs/arquitectura-base-prototipo.md`, y **antes** de generar la vista HTML, sella el documento:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/stamp_doc.py" --input docs/arquitectura-base-prototipo.md
```

Anade/actualiza la cabecera `> **Version N** - **Generado:** fecha hora`, **incrementa la version en cada regeneracion** (via `docs/.aidd-doc-meta.json`) y usa la **fecha y hora reales**. No inventes la version ni la hora: las pone el script y esa linea no se edita a mano. Si Python no esta disponible, avisa pero no bloquees.

### 4. Generacion de la vista HTML (complementaria)

Una vez escrito y confirmado `docs/arquitectura-base-prototipo.md`, genera su **vista HTML** complementaria con el skill `booster-docs`. El `.md` es la fuente de verdad; el HTML es solo para consumo humano.

- Invoca `booster-docs` con `docs/arquitectura-base-prototipo.md` como entrada y salida en `docs/html/arquitectura-base-prototipo.html` (crea `docs/html/` si no existe). El script auto-detecta el tipo de documento (`arquitectura-base-prototipo`) y anade dashboard de KPIs, chips y demas elementos visuales.
- Pasa el flag `--open` para que el HTML **se abra automaticamente en el navegador** al terminar el comando. En modo no interactivo (CI/auto o si el usuario pidio no ser interrumpido) omite `--open` y solo informa de la ruta.
- **Degradacion elegante**: si `booster-docs` no esta disponible, avisa de que la vista HTML no se genero y de que puede instalarse el plugin `boosters`, pero **no bloquees** el comando: el `.md` es suficiente para continuar.
- El HTML es parte de la documentacion del repo (se versiona junto al `.md`); no lo anadas a `.gitignore`.
- No regeneres el HTML si el documento quedo pendiente de cambios: hazlo cuando este estable.
- Nunca modifiques el `.md` de origen al generar el HTML.

## Verificacion final

Al terminar, informa:

- Comando AIDD ejecutado (`aidd prototype-architecture`) y fase/paso (2 / 2.1).
- Ruta del documento generado o actualizado (`docs/arquitectura-base-prototipo.md`).
- Ruta de la vista HTML generada (`docs/html/arquitectura-base-prototipo.html`), o aviso si no se pudo generar el HTML.
- Flujos que la demo permitira recorrer y supuestos/exclusiones relevantes.
- Recordatorio: pendiente de **aprobacion humana** antes de implementar la demo.
- Siguiente paso sugerido: `aidd prototype` para implementar la demo (via `booster-ux`) y, tras presentarla al cliente, actualizar `docs/cliente-requisitos.md`. Si el feedback trae cambios significativos, se vuelve al paso 1.1 (`aidd requirements`).
