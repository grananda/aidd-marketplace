---
name: aidd-architecture
description: Fase 2 (paso 2.4) del conjunto AIDD (AI Driven Development). Consolida la arquitectura tecnica definitiva e implementable del producto, mediante el comando `aidd architecture` (alias `aidd fase 2.4`). Actua como arquitecto de software senior que analiza como fuentes de verdad `docs/detalle-historias-usuario.md`, `docs/propuesta-arquitectura-base.md` y `docs/guia-estilos.md` y genera `docs/arquitectura-base.md` con objetivo y alcance, principios y decisiones arquitectonicas explicitas, arbol de carpetas real, descomposicion por modulos, capas y responsabilidades, flujos de informacion, gestion de estado, navegacion, integraciones, seguridad, accesibilidad, observabilidad, rendimiento, escalabilidad y riesgos. Es el insumo principal del roadmap y cierra el Diseno (AI Architect). Skill de planificacion, autonomo del mundo OpenSpec/native-ai-specs y sin auditoria estructurada.
metadata:
  author: NTT DATA Spain GDN-e
  version: "1.0.0"
---

# aidd-architecture (AIDD · Fase 2 · paso 2.4)

Usa este skill cuando el usuario quiera consolidar la arquitectura tecnica definitiva del producto, o cuando invoque:

- `aidd architecture`
- `aidd fase 2.4`

Tambien cuando pida "arquitectura definitiva", "arquitectura base implementable", "documento tecnico de arquitectura" o equivalentes del paso 2.4.

Responde y documenta en espanol siempre que sea posible. Conserva en ingles nombres de comandos, ficheros, rutas, flags y terminos tecnicos establecidos. Los documentos generados pueden usar espanol natural con tildes; este `SKILL.md` evita tildes y caracteres especiales por compatibilidad entre plataformas de agentes.

## Que es AIDD y donde encaja este skill

AIDD (AI Driven Development) es un conjunto de skills de planificacion y arquitectura asistida por IA. Cada skill cubre una fase o paso del proceso descrito en `${CLAUDE_PLUGIN_ROOT}/methodology/native-ai-aidd-sdd.md` (referencia de metodologia, solo lectura):

- Fase 0 — `aidd client-requirements`.
- Fase 1 — `aidd requirements`, `aidd user-stories`, `aidd user-story-details`.
- **Fase 2 — Diseno (AI Architect)**:
  - `aidd prototype-architecture` (2.1): `docs/arquitectura-base-prototipo.md`.
  - `aidd prototype` (2.2): implementacion del prototipo, redirige a `booster-ux`.
  - `aidd style-guide` (2.3): guia de estilos (`docs/guia-estilos.md`).
  - `aidd architecture-proposal` (2.3): propuesta de arquitectura (`docs/propuesta-arquitectura-base.md`).
  - **`aidd architecture`** (este skill, 2.4): arquitectura tecnica definitiva (`docs/arquitectura-base.md`).

Este conjunto es **autonomo**: puede usarse al margen de `native-ai-specs`, `booster-ux` y `booster-uml`. No depende de OpenSpec ni escribe auditoria estructurada. Las decisiones se registran de forma ligera dentro del propio documento generado.

Como complemento opcional, al final del comando se genera una **vista HTML** de la arquitectura base con `booster-docs` (ver el paso final del flujo). El `.md` sigue siendo la **unica fuente de verdad**; el HTML es solo para consumo humano y no altera el flujo AIDD si `booster-docs` no esta instalado.

> `docs/arquitectura-base.md` es el **insumo principal** del roadmap. En la metodologia completa lo consume `native-ai roadmap` (Fase 3), pero este skill no depende de ello: produce el documento de arquitectura tanto si luego se usa `native-ai-specs` como si no.

## Rol y objetivo

> Actua como arquitecto de software senior con enfoque practico de implementacion. Tu objetivo es consolidar la arquitectura real y definitiva del producto, alineada con historias, propuesta funcional y guia de estilos, implementable y sin contradicciones con los documentos de entrada.

Criterio de salida del paso: existe `docs/arquitectura-base.md` completo, con decisiones explicitas (no contenido generico), arbol de carpetas real y responsabilidades por capa, consumible directamente para fasear el roadmap. Cierra la Fase 2. Lo que falte por decidir se documenta como decision pendiente, no se inventa.

## Reglas generales

- Trabaja desde la raiz del proyecto del usuario.
- **Entradas / fuentes de verdad**: `docs/detalle-historias-usuario.md`, `docs/propuesta-arquitectura-base.md` y `docs/guia-estilos.md`. Si falta alguna, avisa y propon generarla antes (`aidd user-story-details`, `aidd architecture-proposal`, `aidd style-guide`).
- Idealmente el prototipo ya ha sido validado por el cliente y el feedback incorporado en `docs/cliente-requisitos.md`. Si no consta, avisa de que la arquitectura definitiva deberia partir de requisitos ya validados.
- Antes de preguntar, **lee primero** las tres fuentes de verdad y el resto de `docs/`. No preguntes lo que ya este resuelto ahi.
- **No contradigas** ningun documento de entrada. Si detectas un conflicto entre propuesta, guia de estilos e historias, senalalo y resuelvelo de forma explicita, no lo ignores.
- Cada decision arquitectonica debe ser **explicita y justificada**. Evita contenido generico de relleno. Documenta supuestos cuando falte detalle.
- No sobrescribas un `docs/arquitectura-base.md` existente sin avisar: leelo, propon los cambios y confirma.
- Este documento requiere aprobacion humana y cierra el gate de Fase 2. Al terminar, deja claro que esta pendiente de revision.

## Flujo del comando `aidd architecture`

### 1. Recopilacion de contexto (lectura previa)

Lee y consolida las tres fuentes de verdad (`detalle-historias-usuario.md`, `propuesta-arquitectura-base.md`, `guia-estilos.md`) y el resto de documentos de `docs/`. Detecta conflictos entre ellos antes de escribir.

### 2. Pre-flight de preguntas

Resuelve solo lo imprescindible para una arquitectura cerrada.

1. Cubre, como minimo: conflictos detectados entre los documentos de entrada y decisiones arquitectonicas determinantes aun abiertas (persistencia, integraciones, modelo de despliegue).
2. Clasifica cada hueco en **bloqueante**, **preferencia** o **confirmacion**.
3. No preguntes lo que las fuentes de verdad ya resuelven.
4. Presupuesto de preguntas: maximo **7** por ejecucion. Prioriza bloqueantes y conflictos, y agrupa relacionadas.
5. Formato: si la plataforma soporta preguntas estructuradas (por ejemplo `AskUserQuestion`), usalo con 2-4 opciones y marca una como `(Recomendada)`; si no, lista numerada con opciones y recomendacion.
6. Modo no interactivo: toma el default recomendado para `preferencia` y `confirmacion`; deja los `bloqueante` sin default como decisiones pendientes en el documento.
7. Si el usuario aplaza una duda, registrala como pendiente y continua.

### 3. Generacion de `docs/arquitectura-base.md`

Genera (o actualiza) `docs/arquitectura-base.md`. Incluye **obligatoriamente** estas secciones:

```markdown
# Arquitectura base — <nombre del proyecto>

> Documento de Fase 2 (AIDD · paso 2.4). Generado por `aidd architecture`.
> Fuentes de verdad: detalle-historias-usuario.md, propuesta-arquitectura-base.md, guia-estilos.md.
> Insumo principal del roadmap. Pendiente de aprobacion humana.

## 1. Objetivo y alcance
## 2. Principios y decisiones arquitectonicas
## 3. Estructura de la solucion (arbol de carpetas real)
## 4. Descomposicion por modulos / dominios
## 5. Capas y responsabilidades
## 6. Componentes base y relaciones
## 7. Flujos principales de informacion
## 8. Gestion de estado
## 9. Navegacion y organizacion de pantallas / endpoints
## 10. Integracion con APIs y servicios externos
## 11. Seguridad, accesibilidad, observabilidad y rendimiento
## 12. Escalabilidad, mantenibilidad y extensibilidad
## 13. Riesgos tecnicos, supuestos y decisiones pendientes
## 14. Decisiones tomadas en el paso 2.4
- Registro ligero: pregunta, opciones, decision, origen (usuario | default), una linea de justificacion.
```

Reglas de contenido:

- Cada decision explicita y justificada; el arbol de carpetas debe ser real, no ilustrativo.
- No debe contradecir historias, propuesta ni guia de estilos. Los conflictos resueltos se documentan en la seccion 2 o 13.
- La seccion 14 sustituye a la auditoria estructurada e incluye decisiones resueltas por default.

### Sello de version y fecha-hora (antes de renderizar)

Tras escribir o actualizar `docs/arquitectura-base.md`, y **antes** de generar la vista HTML, sella el documento:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/stamp_doc.py" --input docs/arquitectura-base.md
```

Anade/actualiza la cabecera `> **Version N** - **Generado:** fecha hora`, **incrementa la version en cada regeneracion** (via `docs/.aidd-doc-meta.json`) y usa la **fecha y hora reales**. No inventes la version ni la hora: las pone el script y esa linea no se edita a mano. Si Python no esta disponible, avisa pero no bloquees.

### 4. Generacion de la vista HTML (complementaria)

Una vez escrito y confirmado `docs/arquitectura-base.md`, genera su **vista HTML** complementaria con el skill `booster-docs`. El `.md` es la fuente de verdad; el HTML es solo para consumo humano.

- Invoca `booster-docs` con `docs/arquitectura-base.md` como entrada y salida en `docs/html/arquitectura-base.html` (crea `docs/html/` si no existe). El script auto-detecta el tipo de documento (`arquitectura-base`) y anade dashboard de KPIs, chips y demas elementos visuales.
- Pasa el flag `--open` para que el HTML **se abra automaticamente en el navegador** al terminar el comando. En modo no interactivo (CI/auto o si el usuario pidio no ser interrumpido) omite `--open` y solo informa de la ruta.
- **Degradacion elegante**: si `booster-docs` no esta disponible, avisa de que la vista HTML no se genero y de que puede instalarse el plugin `boosters`, pero **no bloquees** el comando: el `.md` es suficiente para continuar.
- El HTML es parte de la documentacion del repo (se versiona junto al `.md`); no lo anadas a `.gitignore`.
- No regeneres el HTML si el documento quedo pendiente de cambios: hazlo cuando este estable.
- Nunca modifiques el `.md` de origen al generar el HTML.

## Verificacion final

Al terminar, informa:

- Comando AIDD ejecutado (`aidd architecture`) y fase/paso (2 / 2.4).
- Ruta del documento generado o actualizado (`docs/arquitectura-base.md`).
- Ruta de la vista HTML generada (`docs/html/arquitectura-base.html`), o aviso si no se pudo generar el HTML.
- Conflictos entre documentos de entrada resueltos y decisiones que quedan pendientes.
- Recordatorio del gate de Fase 2: prototipo validado por el cliente y guia de estilos, propuesta de arquitectura y arquitectura definitiva **aprobadas por el humano**.
- Criterio de salida de Fase 2: indica si requisitos y arquitectura quedan en estado consumible para fasear el roadmap, o que falta.
- Siguiente paso sugerido: Fase 3 — Inicializacion y Roadmap (AI Lead). En la metodologia completa se hace con `native-ai init` y `native-ai roadmap`; queda fuera del conjunto AIDD de planificacion.
