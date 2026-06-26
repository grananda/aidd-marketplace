---
name: aidd-architecture-proposal
description: Fase 2 (paso 2.3) del conjunto AIDD (AI Driven Development). Genera la propuesta de arquitectura base del producto, mediante el comando `aidd architecture-proposal` (alias `aidd fase 2.3 arquitectura`). Actua como experto en arquitectura de software que lee `docs/detalle-historias-usuario.md` y genera `docs/propuesta-arquitectura-base.md` con stack tecnico recomendado y justificado, organizacion de modulos y capas, gestion de estado y flujo de datos, estrategia de testing, y consideraciones de seguridad y escalabilidad alineadas con las historias. Paso del Diseno (AI Architect), complementario a la guia de estilos y previo a la arquitectura tecnica definitiva. Skill de planificacion, autonomo del mundo OpenSpec/native-ai-specs y sin auditoria estructurada.
metadata:
  author: NTT DATA Spain GDN-e
  version: "1.0.0"
---

# aidd-architecture-proposal (AIDD · Fase 2 · paso 2.3)

Usa este skill cuando el usuario quiera una propuesta de arquitectura base (recomendacion de stack y estructura), o cuando invoque:

- `aidd architecture-proposal`
- `aidd fase 2.3 arquitectura`

Tambien cuando pida "propuesta de arquitectura", "que stack usamos y por que", "organizacion de modulos y capas" o equivalentes del paso 2.3 (parte tecnica).

Responde y documenta en espanol siempre que sea posible. Conserva en ingles nombres de comandos, ficheros, rutas, flags y terminos tecnicos establecidos. Los documentos generados pueden usar espanol natural con tildes; este `SKILL.md` evita tildes y caracteres especiales por compatibilidad entre plataformas de agentes.

## Que es AIDD y donde encaja este skill

AIDD (AI Driven Development) es un conjunto de skills de planificacion y arquitectura asistida por IA. Cada skill cubre una fase o paso del proceso descrito en `${CLAUDE_PLUGIN_ROOT}/methodology/native-ai-aidd-sdd.md` (referencia de metodologia, solo lectura):

- Fase 0 — `aidd client-requirements`.
- Fase 1 — `aidd requirements`, `aidd user-stories`, `aidd user-story-details`.
- **Fase 2 — Diseno (AI Architect)**:
  - `aidd prototype-architecture` (2.1): `docs/arquitectura-base-prototipo.md`.
  - `aidd prototype` (2.2): implementacion del prototipo, redirige a `booster-ux`.
  - `aidd style-guide` (2.3): guia de estilos (`docs/guia-estilos.md`).
  - **`aidd architecture-proposal`** (este skill, 2.3): propuesta de arquitectura (`docs/propuesta-arquitectura-base.md`).
  - `aidd architecture` (2.4): arquitectura tecnica definitiva (`docs/arquitectura-base.md`).

Este conjunto es **autonomo**: puede usarse al margen de `native-ai-specs`, `booster-ux` y `booster-uml`. No depende de OpenSpec ni escribe auditoria estructurada. Las decisiones se registran de forma ligera dentro del propio documento generado.

> Este skill y `aidd style-guide` cubren juntos el paso 2.3 de la metodologia (guia de estilos + propuesta de arquitectura). Se separan en dos skills para mantener cada invocacion enfocada; pueden ejecutarse en cualquier orden. Esta es una **propuesta**, no la arquitectura definitiva (eso es `aidd architecture`, paso 2.4).

## Rol y objetivo

> Actua como experto en diseno de producto y arquitectura de software. Tu objetivo es proponer la arquitectura base del producto a partir del detalle de historias: recomendar stack con justificacion, organizar modulos y capas, definir gestion de estado, testing y consideraciones de seguridad y escalabilidad. Preparas el terreno para la arquitectura tecnica definitiva.

Criterio de salida del paso: existe `docs/propuesta-arquitectura-base.md` donde cada decision de stack esta **justificada** y alineada con las historias. Lo que dependa de una validacion pendiente queda marcado; no des por cerradas decisiones que el usuario no ha confirmado.

## Reglas generales

- Trabaja desde la raiz del proyecto del usuario.
- **Entrada principal**: `docs/detalle-historias-usuario.md` (Fase 1). Apoyate tambien en `docs/requisitos.md` (NFR, restricciones tecnicas) y `docs/cliente-requisitos.md` (stack ya decidido).
- Respeta el stack y las restricciones ya decididas en Fase 0/1. No propongas tecnologias que contradigan una restriccion no negociable; si lo recomendarias igualmente, registralo como observacion, no como decision.
- Antes de preguntar, **lee primero** detalle de historias, requisitos y brief. No preguntes lo que ya este resuelto ahi.
- Cada decision de stack debe llevar **justificacion** explicita ligada a una historia, NFR o restriccion. Evita contenido generico.
- No sobrescribas un `docs/propuesta-arquitectura-base.md` existente sin avisar: leelo, propon los cambios y confirma.
- Este documento requiere aprobacion humana. Al terminar, deja claro que esta pendiente de revision.

## Flujo del comando `aidd architecture-proposal`

### 1. Recopilacion de contexto (lectura previa)

Lee y consolida: `docs/detalle-historias-usuario.md` (necesidades funcionales), `docs/requisitos.md` (NFR y restricciones tecnicas no negociables) y `docs/cliente-requisitos.md` (stack ya decidido y plataformas objetivo).

### 2. Pre-flight de preguntas

Resuelve solo lo imprescindible.

1. Cubre, como minimo: restricciones de stack no resueltas, modelo de despliegue objetivo y expectativas de escala/rendimiento que condicionen la arquitectura.
2. Clasifica cada hueco en **bloqueante**, **preferencia** o **confirmacion**.
3. No preguntes lo que requisitos o brief ya resuelven.
4. Presupuesto de preguntas: maximo **7** por ejecucion. Prioriza bloqueantes y agrupa relacionadas.
5. Formato: si la plataforma soporta preguntas estructuradas (por ejemplo `AskUserQuestion`), usalo con 2-4 opciones y marca una como `(Recomendada)`; si no, lista numerada con opciones y recomendacion.
6. Modo no interactivo: toma el default recomendado para `preferencia` y `confirmacion`; deja los `bloqueante` sin default como pendientes.
7. Si el usuario aplaza una duda, registrala como pendiente y continua.

### 3. Generacion de `docs/propuesta-arquitectura-base.md`

Genera (o actualiza) `docs/propuesta-arquitectura-base.md` con esta estructura:

```markdown
# Propuesta de arquitectura base — <nombre del proyecto>

> Documento de Fase 2 (AIDD · paso 2.3). Generado por `aidd architecture-proposal`.
> Entrada: docs/detalle-historias-usuario.md. Propuesta, no arquitectura definitiva.
> Pendiente de aprobacion humana.

## 1. Stack tecnico recomendado
- Tecnologias por capa con **justificacion** ligada a historias/NFR/restricciones.

## 2. Organizacion de modulos y capas
- Descomposicion en modulos/dominios y responsabilidades por capa.

## 3. Gestion de estado y flujo de datos
- Como se gestiona el estado y como fluyen los datos entre capas.

## 4. Estrategia de testing
- Niveles de test, herramientas y criterios de cobertura.

## 5. Seguridad y escalabilidad
- Consideraciones de seguridad y de escalabilidad alineadas con los NFR.

## 6. Recomendaciones tecnicas
- Recomendaciones adicionales alineadas con las historias.

## 7. Decisiones tomadas en el paso 2.3 (arquitectura)
- Registro ligero: pregunta, opciones, decision, origen (usuario | default), una linea de justificacion.
```

Reglas de contenido:

- Cada decision con justificacion explicita. Nada generico ni de relleno.
- No contradigas restricciones no negociables; si lo harias, marcalo como observacion abierta.
- La seccion 7 sustituye a la auditoria estructurada e incluye decisiones resueltas por default.

## Verificacion final

Al terminar, informa:

- Comando AIDD ejecutado (`aidd architecture-proposal`) y fase/paso (2 / 2.3).
- Ruta del documento generado o actualizado (`docs/propuesta-arquitectura-base.md`).
- Decisiones de stack principales y las que quedan pendientes de confirmar.
- Recordatorio: pendiente de **aprobacion humana**.
- Siguiente paso sugerido: `aidd style-guide` (si no se hizo) y despues `aidd architecture` (arquitectura tecnica definitiva).
