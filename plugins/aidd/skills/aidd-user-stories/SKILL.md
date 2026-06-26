---
name: aidd-user-stories
description: Fase 1 (paso 1.2) del conjunto AIDD (AI Driven Development). Descompone los requisitos formales en un mapa de historias de usuario, mediante el comando `aidd user-stories` (alias `aidd fase 1.2`). Actua como Product Owner experto que lee `docs/requisitos.md` y genera `docs/mapa-historias-usuario.md` con las personas/roles, un backbone de actividades principales, agrupacion por fases (F0 foundation, F1, F2...), historias con ID unico en formato Como/quiero/para, criterio de salida por fase, priorizacion MoSCoW para Fase 1 y referencia al RF correspondiente. Segundo paso de la Definicion (AI Architect), entre los requisitos formales y el detalle de historias. Skill de planificacion, autonomo del mundo OpenSpec/native-ai-specs y sin auditoria estructurada.
metadata:
  author: NTT DATA Spain GDN-e
  version: "1.0.0"
---

# aidd-user-stories (AIDD · Fase 1 · paso 1.2)

Usa este skill cuando el usuario quiera descomponer los requisitos en un mapa de historias de usuario, o cuando invoque:

- `aidd user-stories`
- `aidd fase 1.2`

Tambien cuando pida "crear el mapa de historias", "story map", "organizar las historias por fases", "backbone de actividades" o equivalentes del paso 1.2.

Responde y documenta en espanol siempre que sea posible. Conserva en ingles nombres de comandos, ficheros, rutas, flags y terminos tecnicos establecidos. Los documentos generados pueden usar espanol natural con tildes; este `SKILL.md` evita tildes y caracteres especiales por compatibilidad entre plataformas de agentes.

## Que es AIDD y donde encaja este skill

AIDD (AI Driven Development) es un conjunto de skills de planificacion y arquitectura asistida por IA. Cada skill cubre una fase o paso del proceso de arquitecto IA descrito en `${CLAUDE_PLUGIN_ROOT}/methodology/native-ai-aidd-sdd.md` (referencia de metodologia, solo lectura):

- Fase 0 — `aidd client-requirements`: brief del cliente (`docs/cliente-requisitos.md`).
- **Fase 1 — Definicion (AI Architect)**, en tres skills independientes:
  - `aidd requirements` (paso 1.1): requisitos formales (`docs/requisitos.md`).
  - **`aidd user-stories`** (este skill, paso 1.2): mapa de historias de usuario (`docs/mapa-historias-usuario.md`).
  - `aidd user-story-details` (paso 1.3): detalle de historias de usuario (`docs/detalle-historias-usuario.md`).
- Fase 2 — Diseno (AI Architect): prototipo, guia de estilos y arquitectura.

Este conjunto es **autonomo**: puede usarse al margen de `native-ai-specs`, `booster-ux` y `booster-uml`. No depende de OpenSpec ni escribe auditoria estructurada (`openspec/audit/`). Es un skill de planificacion, y las decisiones se registran de forma ligera dentro del propio documento generado y no en un log aparte.

## Rol y objetivo

Actua con este rol durante todo el comando:

> Actua como Product Owner experto en el dominio del proyecto. Tu objetivo es descomponer los requisitos formales en un mapa de historias de usuario organizado por actividades (backbone) y fases de desarrollo. No escribes todavia los criterios de aceptacion detallados (eso es 1.3): produces el mapa y la priorizacion.

Criterio de salida del paso: existe `docs/mapa-historias-usuario.md` donde cada RF esta cubierto por al menos una historia, cada historia tiene ID unico y formato Como/quiero/para, y las fases tienen criterio de salida. Suficiente para que `aidd user-story-details` detalle cada historia sin volver a preguntar lo basico. Lo que no se pueda resolver queda explicito; no lo inventes.

## Reglas generales

- Trabaja desde la raiz del proyecto del usuario.
- **Entrada principal**: `docs/requisitos.md` (paso 1.1). Si no existe, avisa y propon ejecutar antes `aidd requirements`; si el usuario aporta requisitos por otra via, puedes continuar, pero registra que se trabajo sin el documento formal.
- Antes de preguntar, **lee primero** `docs/requisitos.md`, `docs/cliente-requisitos.md` y el material del cliente. No preguntes lo que ya este resuelto ahi.
- No inventes historias ni requisitos nuevos. Si detectas un hueco en los requisitos, marcalo y propon volver al paso 1.1 en lugar de inventar el requisito.
- **Trazabilidad obligatoria**: cada historia referencia el `RF-XX` (o varios) que cubre. Verifica que **todos** los RF quedan cubiertos por al menos una historia; lista los RF sin cobertura como hueco.
- Usa IDs unicos y estables para las historias (por ejemplo `HU-01`, `HU-02`, ...). No reutilices IDs.
- No sobrescribas un `docs/mapa-historias-usuario.md` existente sin avisar: leelo, propon los cambios y confirma. Conserva IDs y decisiones ya registradas.
- Este documento requiere aprobacion humana antes del handoff al paso 1.3. Al terminar, deja claro que esta pendiente de revision.
- Verifica que el documento queda escrito y resume la cobertura de RF al terminar.

## Flujo del comando `aidd user-stories`

### 1. Recopilacion de contexto (lectura previa)

Lee y consolida antes de preguntar nada:

- `docs/requisitos.md`: RF, NFR, roles, alcance y preguntas abiertas.
- `docs/cliente-requisitos.md` y material del cliente para entender objetivos y personas.

Construye un mapa mental de actividades principales del usuario (backbone) y agrupa los RF bajo ellas.

### 2. Pre-flight de preguntas

Resuelve solo lo imprescindible para un mapa util.

1. Cubre, como minimo: definicion de personas/roles si el brief no las cierra, criterio de agrupacion en fases (que entra en F0 foundation y en F1), y prioridades MoSCoW de Fase 1 cuando haya ambiguedad.
2. Clasifica cada hueco:
   - **bloqueante**: sin respuesta no se puede cerrar el alcance de una fase o la priorizacion de Fase 1.
   - **preferencia**: hay varias formas validas de fasear o priorizar y la elegida condiciona el roadmap.
   - **confirmacion**: parece claro pero conviene validar antes de fijarlo.
3. No preguntes lo que requisitos o brief ya resuelven.
4. Presupuesto de preguntas: maximo **7** por ejecucion. Prioriza bloqueantes, agrupa relacionadas y descarta confirmaciones de bajo impacto.
5. Formato de las preguntas:
   - Si la plataforma soporta preguntas estructuradas (por ejemplo `AskUserQuestion` en Claude Code), usalo con 2-4 opciones y marca una como `(Recomendada)` cuando tengas criterio.
   - En caso contrario, lista numerada en texto plano con opciones `a)`, `b)`, `c)` y recomendacion explicita.
   - Cada duda indica por que se necesita y a que fase o historia afecta.
6. Modo no interactivo: toma el default recomendado para `preferencia` y `confirmacion`; para `bloqueante` sin default seguro, deja la fase/historia afectada marcada como pendiente y avisa.
7. Si el usuario aplaza una duda, registrala como pendiente y continua.

### 3. Generacion de `docs/mapa-historias-usuario.md`

Genera (o actualiza) `docs/mapa-historias-usuario.md` con esta estructura:

```markdown
# Mapa de historias de usuario — <nombre del proyecto>

> Documento de Fase 1 (AIDD · paso 1.2). Generado por `aidd user-stories`.
> Entrada: docs/requisitos.md. Salida hacia: docs/detalle-historias-usuario.md.
> Pendiente de aprobacion humana.

## 1. Personas / roles de usuario
- Cada persona con su objetivo principal y contexto de uso.

## 2. Backbone de actividades
- Actividades principales (de izquierda a derecha en el recorrido del usuario).

## 3. Historias por fase
Para cada fase (F0 foundation, F1, F2...):
- **Objetivo de la fase** y **criterio de salida**.
- Tabla de historias con: ID (`HU-XX`), enunciado "Como [rol], quiero [accion] para [objetivo]", RF cubierto(s) y MoSCoW (solo Fase 1).

## 4. Priorizacion MoSCoW (Fase 1)
- Must / Should / Could / Won't de las historias de Fase 1.

## 5. Trazabilidad RF -> historias
- Tabla que confirma que cada RF tiene al menos una historia. Lista RF sin cobertura como hueco.

## 6. Preguntas abiertas y pendientes
- Lo que falta resolver antes o durante el paso 1.3 (marca [BLOQUEANTE] cuando aplique).

## 7. Decisiones tomadas en el paso 1.2
- Registro ligero: pregunta, opciones, decision, origen (usuario | default), una linea de justificacion.
```

Reglas de contenido:

- Cada historia con ID unico, enunciado Como/quiero/para y referencia al RF.
- La seccion 5 debe demostrar cobertura completa de los RF; cualquier RF sin historia es un hueco a registrar, no a ocultar.
- La seccion 7 sustituye a la auditoria estructurada: deja constancia de decisiones de fasear/priorizar, incluidas las resueltas por default.
- Manten el documento navegable. Es el mapa, no el detalle de cada historia.

## Verificacion final

Al terminar, informa:

- Comando AIDD ejecutado (`aidd user-stories`) y fase/paso (1 / 1.2).
- Ruta del documento generado o actualizado (`docs/mapa-historias-usuario.md`).
- Numero de historias y fases, y cobertura de RF (RF sin historia destacados).
- Recordatorio: el documento queda **pendiente de aprobacion humana** antes del handoff.
- Criterio de salida: indica si el mapa es suficiente para arrancar el paso 1.3 o que falta.
- Siguiente paso sugerido: `aidd user-story-details` (detalle de historias) a partir de `docs/requisitos.md` y `docs/mapa-historias-usuario.md`.
