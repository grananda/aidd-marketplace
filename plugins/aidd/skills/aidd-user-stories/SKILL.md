---
name: aidd-user-stories
description: Fase 1 (paso 1.2) del conjunto AIDD (AI Driven Development). Descompone los requisitos formales en un mapa de historias de usuario, mediante el comando `aidd user-stories` (alias `aidd fase 1.2`). Actua como Product Owner experto que lee `docs/requisitos.md` y genera `docs/mapa-historias-usuario.md` con las personas/roles, un backbone de actividades principales, agrupacion por fases (F0 foundation, F1, F2...), historias con ID unico en formato Como/quiero/para, criterio de salida por fase, priorizacion MoSCoW para Fase 1 y referencia al RF correspondiente. Permite indicar opcionalmente el numero de fases deseado o un minimo (por ejemplo `aidd user-stories fases=4` o `fases>=3`); si no se indica, el numero emerge de la cohesion logica. F0 foundation es la fase de habilitadores (walking skeleton), nunca el nucleo funcional de valor (que va a F1+), y no debe confundirse con el change `foundation` de scaffolding del roadmap. Segundo paso de la Definicion (AI Architect), entre los requisitos formales y el detalle de historias. Skill de planificacion, autonomo del mundo OpenSpec/aisdd-specs y sin auditoria estructurada.
metadata:
  author: NTT DATA Spain GDN-e
  version: "1.2.0"
---

# aidd-user-stories (AIDD · Fase 1 · paso 1.2)

Usa este skill cuando el usuario quiera descomponer los requisitos en un mapa de historias de usuario, o cuando invoque:

- `aidd user-stories`
- `aidd fase 1.2`
- `aidd user-stories fases=<N>` (numero exacto de fases deseado) o `aidd user-stories fases>=<N>` / `fases-min=<N>` (minimo de fases)

Tambien cuando pida "crear el mapa de historias", "story map", "organizar las historias por fases", "backbone de actividades" o equivalentes del paso 1.2. Y cuando indique cuantas fases quiere ("quiero N fases", "al menos N fases", "no mas de N fases").

Responde y documenta en espanol siempre que sea posible. Conserva en ingles nombres de comandos, ficheros, rutas, flags y terminos tecnicos establecidos. Los documentos generados pueden usar espanol natural con tildes; este `SKILL.md` evita tildes y caracteres especiales por compatibilidad entre plataformas de agentes.

## Que es AIDD y donde encaja este skill

AIDD (AI Driven Development) es un conjunto de skills de planificacion y arquitectura asistida por IA. Cada skill cubre una fase o paso del proceso de arquitecto IA descrito en `${CLAUDE_PLUGIN_ROOT}/methodology/native-ai-aidd-sdd.md` (referencia de metodologia, solo lectura):

- Fase 0 — `aidd client-requirements`: brief del cliente (`docs/cliente-requisitos.md`).
- **Fase 1 — Definicion (AI Architect)**, en tres skills independientes:
  - `aidd requirements` (paso 1.1): requisitos formales (`docs/requisitos.md`).
  - **`aidd user-stories`** (este skill, paso 1.2): mapa de historias de usuario (`docs/mapa-historias-usuario.md`).
  - `aidd user-story-details` (paso 1.3): detalle de historias de usuario (`docs/detalle-historias-usuario.md`).
- Fase 2 — Diseno (AI Architect): prototipo, guia de estilos y arquitectura.

Este conjunto es **autonomo**: puede usarse al margen de `aisdd-specs`, `booster-ux` y `booster-uml`. No depende de OpenSpec ni escribe auditoria estructurada (`openspec/audit/`). Es un skill de planificacion, y las decisiones se registran de forma ligera dentro del propio documento generado y no en un log aparte.

Como complemento opcional, al final del comando se genera una **vista HTML** del mapa de historias con `booster-docs` (ver el paso final del flujo). El `.md` sigue siendo la **unica fuente de verdad**; el HTML es solo para consumo humano y no altera el flujo AIDD si `booster-docs` no esta instalado.

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

### 1.5 Numero de fases (control opcional)

Por defecto el **numero de fases emerge de la cohesion logica**: agrupas las historias por lo que forma un incremento entregable con criterio de salida propio (F0 foundation habilitadora, F1 MVP, F2... incrementos), no por un numero fijado de antemano.

El usuario puede **acotar ese numero**. Interpreta la intencion asi:

- **Exacto** (`fases=N`, "quiero N fases"): apunta a exactamente N fases (contando F0).
- **Minimo** (`fases>=N`, `fases-min=N`, "al menos N fases"): usa N o mas; nunca menos.
- **Maximo** (`fases<=N`, "no mas de N fases"): usa N o menos.
- Sin indicacion: el que exija la cohesion logica (registra en la seccion 7 cuantas salieron y por que).

Reglas al aplicar un objetivo de fases:

- **F0 siempre es foundation** y sigue siendo la primera fase; no la elimines para cuadrar un numero.
- **No trocees ni fusiones de forma artificial** solo para llegar a la cifra: cada fase debe conservar un objetivo y un criterio de salida coherentes. Es preferible una fase menos/mas bien formada que N fases forzadas.
- Si el objetivo **choca** con la cohesion (p. ej. piden 5 fases pero el alcance solo da para 3 incrementos con sentido, o piden 2 pero hay dependencias que exigen 4), **respeta lo que puedas y avisa**: aplica el faseado mas cercano que siga teniendo sentido, explica la tension y registrala en la seccion 7 (Decisiones). No fuerces el numero en silencio ni lo ignores en silencio.
- Un objetivo de fases es de **agrupacion**, no de alcance: no aniade ni quita historias ni RF; solo cambia como se agrupan.

### 1.6 Alcance de F0 foundation (que entra y que NO)

F0 foundation es la fase de **habilitadores** (walking skeleton): el trabajo tecnico transversal del que depende todo lo demas pero que **no entrega valor funcional al usuario final**. F0 **no es** el nucleo funcional del producto.

**Prueba que decide (aplicala a cada historia candidata a F0):** *"¿esta historia entrega valor directo al usuario final?"* Si la respuesta es SI, **no es F0** -> va a F1+, aunque sea "core tecnico", complejo o critico. Regla mental: **F0 solo habilita construir; F1 es el primer trozo de lo que el usuario viene a hacer.**

**Entra en F0 (habilitadores):**
- Esqueleto de autenticacion / sesion / roles (el mecanismo, no las reglas de negocio de cada rol).
- Modelo de datos base, persistencia base, migraciones iniciales.
- Shell de navegacion, layout base, tema/estilos base.
- Habilitadores transversales: cliente de API base, logging, i18n base, manejo de errores comun.
- CI/CD, entornos, semillas de datos.

**NO entra en F0 (va a F1+):**
- Los casos de uso reales del usuario (crear / gestionar / consultar lo que da valor).
- Las reglas de negocio de valor.
- Las pantallas que resuelven la necesidad del usuario.
- Cualquier historia que un usuario final "usaria" para lograr su objetivo.

**Aclaracion de nombres (importante):** la fase **F0 del mapa de HU NO es el change `foundation`** del roadmap. El change `foundation` (Fase 3, `aisdd`) es **scaffolding puro** (arbol de carpetas, configuracion, archivos iniciales) derivado de `docs/arquitectura-base.md`, sin funcionalidad, y es la primera unidad de **ejecucion**. La fase F0 del mapa es de **producto**: agrupa las **historias habilitadoras**. Estan alineadas (ambas "preparan la base") pero **no son un mapeo 1:1**: el roadmap re-fasea por presupuesto de contexto y el change `foundation` sale de la arquitectura, no de esta fase.

Si detectas historias de **nucleo funcional colocadas en F0, reubicalas en F1+** y registra el motivo en la seccion 7. Ante la duda entre F0 y F1, aplica la prueba del valor: si aporta valor al usuario, es F1.

### 2. Pre-flight de preguntas

Resuelve solo lo imprescindible para un mapa util.

1. Cubre, como minimo: definicion de personas/roles si el brief no las cierra, criterio de agrupacion en fases (que entra en F0 foundation y en F1, aplicando la **prueba del valor** del paso 1.6: si aporta valor al usuario final es F1, no F0), el **numero o minimo de fases deseado** si el usuario no lo ha indicado ya en el comando y el alcance admite varias faseaciones razonables (preferencia; default: el que exija la cohesion logica), y prioridades MoSCoW de Fase 1 cuando haya ambiguedad.
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
- **Objetivo de la fase** y **criterio de salida**. Para F0, el criterio de salida es "base habilitada" (auth/datos/navegacion/infra listos), **sin valor funcional**; el valor empieza en F1.
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
- **Alcance de F0**: F0 solo lleva historias **habilitadoras** (paso 1.6); ninguna historia con valor funcional para el usuario final. Verifica cada historia de F0 con la prueba del valor y, si detectas nucleo funcional en F0, reubicalo en F1+ y registralo en la seccion 7.
- **Numero de fases**: aplica el objetivo del usuario (exacto/minimo/maximo) segun el paso 1.5, siempre respetando F0=foundation (habilitadores) y la cohesion. Si hubo objetivo de fases, registra en la seccion 7 el numero pedido, el numero final y, si difieren, por que.
- La seccion 7 sustituye a la auditoria estructurada: deja constancia de decisiones de fasear/priorizar, incluidas las resueltas por default.
- Manten el documento navegable. Es el mapa, no el detalle de cada historia.

### Sello de version y fecha-hora (antes de renderizar)

Tras escribir o actualizar `docs/mapa-historias-usuario.md`, y **antes** de generar la vista HTML, sella el documento:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/stamp_doc.py" --input docs/mapa-historias-usuario.md
```

Anade/actualiza la cabecera `> **Version N** - **Generado:** fecha hora`, **incrementa la version en cada regeneracion** (via `docs/.aidd-doc-meta.json`) y usa la **fecha y hora reales**. No inventes la version ni la hora: las pone el script y esa linea no se edita a mano. Si Python no esta disponible, avisa pero no bloquees.

### 4. Generacion de la vista HTML (complementaria)

Una vez escrito y confirmado `docs/mapa-historias-usuario.md`, genera su **vista HTML** complementaria con el skill `booster-docs`. El `.md` es la fuente de verdad; el HTML es solo para consumo humano.

- Invoca `booster-docs` con `docs/mapa-historias-usuario.md` como entrada y salida en `docs/html/mapa-historias-usuario.html` (crea `docs/html/` si no existe). El script auto-detecta el tipo de documento (`mapa-historias-usuario`) y anade dashboard de KPIs, chips y demas elementos visuales.
- Pasa el flag `--open` para que el HTML **se abra automaticamente en el navegador** al terminar el comando. En modo no interactivo (CI/auto o si el usuario pidio no ser interrumpido) omite `--open` y solo informa de la ruta.
- **Degradacion elegante**: si `booster-docs` no esta disponible, avisa de que la vista HTML no se genero y de que puede instalarse el plugin `boosters`, pero **no bloquees** el comando: el `.md` es suficiente para continuar.
- El HTML es parte de la documentacion del repo (se versiona junto al `.md`); no lo anadas a `.gitignore`.
- No regeneres el HTML si el documento quedo pendiente de cambios: hazlo cuando este estable.
- Nunca modifiques el `.md` de origen al generar el HTML.

## Verificacion final

Al terminar, informa:

- Comando AIDD ejecutado (`aidd user-stories`) y fase/paso (1 / 1.2).
- Ruta del documento generado o actualizado (`docs/mapa-historias-usuario.md`).
- Ruta de la vista HTML generada (`docs/html/mapa-historias-usuario.html`), o aviso si no se pudo generar el HTML.
- Numero de historias y fases, y cobertura de RF (RF sin historia destacados). Si el usuario pidio un numero o minimo de fases, indica si se cumplio y, si no, por que (tension con la cohesion).
- Recordatorio: el documento queda **pendiente de aprobacion humana** antes del handoff.
- Criterio de salida: indica si el mapa es suficiente para arrancar el paso 1.3 o que falta.
- Siguiente paso sugerido: `aidd user-story-details` (detalle de historias) a partir de `docs/requisitos.md` y `docs/mapa-historias-usuario.md`.
