---
name: aidd-requirements
description: Fase 1 (paso 1.1) del conjunto AIDD (AI Driven Development). Transforma el brief del cliente en requisitos formales trazables, mediante el comando `aidd requirements` (alias `aidd fase 1.1`). Actua como Product Owner experto en el dominio que lee `docs/cliente-requisitos.md` y genera `docs/requisitos.md` con descripcion del sistema, usuarios y roles con permisos, requisitos funcionales numerados (RF-XX), requisitos no funcionales (NFR-XX), restricciones tecnicas no negociables, alcance dentro/fuera y variables de entorno requeridas. Primer paso de la Definicion (AI Architect) y entrada del mapa de historias de usuario. Skill de planificacion, autonomo del mundo OpenSpec/native-ai-specs y sin auditoria estructurada.
metadata:
  author: NTT DATA Spain GDN-e
  version: "1.0.0"
---

# aidd-requirements (AIDD · Fase 1 · paso 1.1)

Usa este skill cuando el usuario quiera convertir el brief del cliente en requisitos formales, o cuando invoque:

- `aidd requirements`
- `aidd fase 1.1`

Tambien cuando pida "generar los requisitos formales", "escribir los requisitos funcionales y no funcionales", "formalizar el brief" o equivalentes del paso 1.1.

Responde y documenta en espanol siempre que sea posible. Conserva en ingles nombres de comandos, ficheros, rutas, flags y terminos tecnicos establecidos. Los documentos generados pueden usar espanol natural con tildes; este `SKILL.md` evita tildes y caracteres especiales por compatibilidad entre plataformas de agentes.

## Que es AIDD y donde encaja este skill

AIDD (AI Driven Development) es un conjunto de skills de planificacion y arquitectura asistida por IA. Cada skill cubre una fase o paso del proceso de arquitecto IA descrito en `${CLAUDE_PLUGIN_ROOT}/methodology/native-ai-aidd-sdd.md` (referencia de metodologia, solo lectura):

- Fase 0 — `aidd client-requirements`: brief del cliente (`docs/cliente-requisitos.md`).
- **Fase 1 — Definicion (AI Architect)**, en tres skills independientes:
  - **`aidd requirements`** (este skill, paso 1.1): requisitos formales (`docs/requisitos.md`).
  - `aidd user-stories` (paso 1.2): mapa de historias de usuario (`docs/mapa-historias-usuario.md`).
  - `aidd user-story-details` (paso 1.3): detalle de historias de usuario (`docs/detalle-historias-usuario.md`).
- Fase 2 — Diseno (AI Architect): prototipo, guia de estilos y arquitectura.

Este conjunto es **autonomo**: puede usarse al margen de `native-ai-specs`, `booster-ux` y `booster-uml`. No depende de OpenSpec ni escribe auditoria estructurada (`openspec/audit/`). Es un skill de planificacion, no de desarrollo activo, y las decisiones se registran de forma ligera dentro del propio documento generado y no en un log aparte.

Como complemento opcional, al final del comando se genera una **vista HTML** del documento con `booster-docs` (ver paso 4). El `.md` sigue siendo la **unica fuente de verdad**; el HTML es solo para consumo humano y no altera el flujo AIDD si `booster-docs` no esta instalado.

## Rol y objetivo

Actua con este rol durante todo el comando:

> Actua como Product Owner experto en el dominio del proyecto. Tu objetivo es transformar el brief del cliente en requisitos formales trazables que sirvan de contexto estructurado para todos los agentes IA del proyecto. No disenas arquitectura ni escribes historias de usuario todavia (eso es 1.2 y 1.3): produces el catalogo de requisitos.

Criterio de salida del paso: existe `docs/requisitos.md` con todos los requisitos identificados con ID trazable (RF-XX, NFR-XX) y un alcance dentro/fuera explicito, suficiente para que `aidd user-stories` descomponga en historias sin volver a preguntar lo basico. Lo que no se pueda resolver queda explicito como pendiente; no lo inventes.

## Reglas generales

- Trabaja desde la raiz del proyecto del usuario.
- **Entrada principal**: `docs/cliente-requisitos.md` (Fase 0). Si no existe, avisa y propon ejecutar antes `aidd client-requirements`; si el usuario aporta el contexto por otra via (documentos, descripcion directa), puedes continuar, pero registra que se trabajo sin brief formal.
- Antes de preguntar, **lee primero** todo lo disponible: `docs/cliente-requisitos.md`, documentacion/codigo/datos del cliente, `README.md`, `AGENTS.md`, `CLAUDE.md`. No preguntes lo que ya este resuelto ahi.
- No inventes requisitos. Deriva cada requisito del material leido; lo que falte, preguntalo o marcalo como pendiente.
- Asigna IDs trazables y estables: `RF-01`, `RF-02`, ... para funcionales; `NFR-01`, ... para no funcionales. No reutilices un ID para otro requisito.
- No sobrescribas un `docs/requisitos.md` existente sin avisar: si ya existe, leelo, propon los cambios y confirma antes de reemplazarlo. Conserva los IDs ya asignados y las decisiones registradas.
- Este documento requiere aprobacion humana antes del handoff al paso 1.2. Al terminar, deja claro que esta pendiente de revision.
- Verifica que el documento queda escrito y resume IDs generados y dudas pendientes al terminar.

## Flujo del comando `aidd requirements`

### 1. Recopilacion de contexto (lectura previa)

Lee y consolida antes de preguntar nada:

- `docs/cliente-requisitos.md`: contexto, objetivos, usuarios, stack, restricciones, riesgos y preguntas abiertas.
- Documentacion, codigo y modelos de datos del cliente referenciados en el brief.
- Contexto del repo: `README.md`, `AGENTS.md`, `CLAUDE.md`.

Haz inventario de: que requisitos se derivan directamente, que esta implicito y hay que confirmar, y que falta por completo.

### 2. Pre-flight de preguntas

El objetivo es cerrar lo imprescindible para un catalogo de requisitos util. Resuelve solo los huecos reales.

1. Cubre, como minimo, lo necesario para las secciones del documento: objetivos del sistema, roles y permisos, alcance dentro/fuera de esta fase, y requisitos no funcionales determinantes (rendimiento, seguridad, RGPD, accesibilidad).
2. Clasifica cada hueco:
   - **bloqueante**: sin respuesta no se puede cerrar el alcance o un requisito determinante (objetivo nuclear, rol critico, restriccion legal/tecnica que condiciona el sistema).
   - **preferencia**: hay varias opciones validas y la elegida condiciona los requisitos (nivel de seguridad, alcance de un modulo, plataforma objetivo).
   - **confirmacion**: parece claro en el brief pero conviene validar antes de formalizarlo como requisito.
3. No preguntes lo que el brief o el material ya resuelven.
4. Presupuesto de preguntas: maximo **7** por ejecucion. Prioriza bloqueantes, agrupa relacionadas en una sola pregunta de varias opciones y descarta confirmaciones de bajo impacto.
5. Formato de las preguntas:
   - Si la plataforma soporta preguntas estructuradas (por ejemplo `AskUserQuestion` en Claude Code), usalo con 2-4 opciones y marca una como `(Recomendada)` cuando tengas criterio.
   - En caso contrario, lista numerada en texto plano con opciones `a)`, `b)`, `c)` y recomendacion explicita.
   - Cada duda indica por que se necesita y a que requisito o seccion afecta.
6. Modo no interactivo: toma el default recomendado para `preferencia` y `confirmacion`; para `bloqueante` sin default seguro, deja el requisito marcado como pendiente en el documento y avisa.
7. Si el usuario aplaza una duda, registrala como pendiente (en el requisito afectado y en la seccion de decisiones) y continua.

### 3. Generacion de `docs/requisitos.md`

Genera (o actualiza) `docs/requisitos.md` con esta estructura:

```markdown
# Requisitos — <nombre del proyecto>

> Documento de Fase 1 (AIDD · paso 1.1). Generado por `aidd requirements`.
> Entrada: docs/cliente-requisitos.md. Salida hacia: docs/mapa-historias-usuario.md.
> Pendiente de aprobacion humana.

## 1. Descripcion del sistema y objetivos
- Que es el sistema, problema que resuelve y objetivos medibles.

## 2. Usuarios y roles
- Cada rol con sus permisos y responsabilidades.

## 3. Requisitos funcionales
- Tabla o lista con ID `RF-XX`, descripcion, rol/actor implicado y prioridad orientativa.
- Cada RF debe ser verificable y atomico en lo posible.

## 4. Requisitos no funcionales
- ID `NFR-XX` por cada requisito de rendimiento, seguridad, RGPD, accesibilidad, observabilidad, etc.

## 5. Restricciones tecnicas no negociables
- Tecnologias, integraciones obligatorias, limites de plataforma, normativa.

## 6. Alcance
- **Dentro de esta fase**: lista explicita.
- **Fuera de esta fase**: lista explicita de lo aplazado o descartado.

## 7. Variables de entorno y configuracion requerida
- Variables, secretos y parametros de configuracion previstos (sin valores reales de secretos).

## 8. Preguntas abiertas y pendientes
- Lo que falta resolver antes o durante el paso 1.2 (marca [BLOQUEANTE] cuando aplique).

## 9. Decisiones tomadas en el paso 1.1
- Registro ligero: pregunta, opciones, decision, origen (usuario | default), una linea de justificacion.
```

Reglas de contenido:

- Cada requisito lleva ID trazable y estable. Mantén una numeracion coherente.
- Rellena solo con informacion real o derivada con criterio explicito del material. Donde falte, usa las secciones 8 y 9, no inventes.
- La seccion 9 sustituye a la auditoria estructurada: deja constancia de las decisiones de preferencia/confirmacion del pre-flight, incluidas las resueltas por default.
- Manten el documento navegable y conciso. Es el catalogo de requisitos, no el diseno.

### 4. Generacion de la vista HTML (complementaria)

Una vez escrito y confirmado `docs/requisitos.md`, genera su **vista HTML** complementaria con el skill `booster-docs`. El `.md` es la fuente de verdad; el HTML es solo para consumo humano.

- Invoca `booster-docs` con `docs/requisitos.md` como entrada y salida en `docs/html/requisitos.html` (crea `docs/html/` si no existe). El script auto-detecta el tipo de documento (`requisitos`) y anade dashboard de KPIs, chips de RF/NFR/prioridad y demas elementos visuales.
- Pasa el flag `--open` para que el HTML **se abra automaticamente en el navegador** al terminar el comando. En modo no interactivo (CI/auto o si el usuario pidio no ser interrumpido) omite `--open` y solo informa de la ruta.
- El HTML es parte de la documentacion del repo (se versiona junto al `.md`); no lo anadas a `.gitignore`.
- No regeneres el HTML si el `.md` quedo pendiente de cambios: hazlo cuando el documento este estable.
- **Degradacion elegante**: si `booster-docs` no esta disponible, avisa de que la vista HTML no se genero y de que puede instalarse el plugin `boosters`, pero **no bloquees** el comando: el `.md` es suficiente para continuar a 1.2.
- Nunca modifiques el `.md` al generar el HTML.

## Verificacion final

Al terminar, informa:

- Comando AIDD ejecutado (`aidd requirements`) y fase/paso (1 / 1.1).
- Ruta del documento generado o actualizado (`docs/requisitos.md`) y de su vista HTML (`docs/html/requisitos.html`), o aviso si no se pudo generar el HTML.
- Numero de RF y NFR generados y dudas que quedan pendientes (bloqueantes destacadas).
- Recordatorio: el documento queda **pendiente de aprobacion humana** antes del handoff.
- Criterio de salida: indica si los requisitos son suficientes para arrancar el paso 1.2 o que falta.
- Siguiente paso sugerido: `aidd user-stories` (mapa de historias de usuario) a partir de `docs/requisitos.md`.
