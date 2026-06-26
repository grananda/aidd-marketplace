---
name: aidd-client-requirements
description: Fase 0 del conjunto AIDD (AI Driven Development). Captura y estructura el brief del cliente antes de que ningun rol de IA produzca contenido, mediante el comando `aidd client-requirements` (alias `aidd fase 0`). Actua como consultor tecnico experto que recopila contexto, stack, restricciones y documentacion aportada, formula las preguntas clave e identifica riesgos y ambiguedades, y genera `docs/cliente-requisitos.md` con suficiente contexto para que la Fase 1 (AI Architect) arranque sin preguntas. Opcionalmente crea o actualiza `AGENTS.md` con contexto, stack y convenciones del proyecto. Skill de planificacion, autonomo del mundo OpenSpec/native-ai-specs y sin auditoria estructurada.
metadata:
  author: NTT DATA Spain GDN-e
  version: "1.1.0"
---

# aidd-client-requirements (AIDD · Fase 0)

Usa este skill cuando el usuario quiera iniciar un proyecto y capturar el brief del cliente, o cuando invoque:

- `aidd client-requirements`
- `aidd fase 0`

Tambien cuando pida "estructurar los requisitos del cliente", "crear el brief", "preparar el proyecto antes de empezar" o equivalentes de la Fase 0.

Responde y documenta en espanol siempre que sea posible. Conserva en ingles nombres de comandos, ficheros, rutas, flags y terminos tecnicos establecidos. Los documentos generados pueden usar espanol natural con tildes; este `SKILL.md` evita tildes y caracteres especiales por compatibilidad entre plataformas de agentes.

## Que es AIDD y donde encaja este skill

AIDD (AI Driven Development) es un conjunto de skills de planificacion y arquitectura asistida por IA. Cada skill cubre una fase o paso del proceso de arquitecto IA descrito en `${CLAUDE_PLUGIN_ROOT}/methodology/native-ai-aidd-sdd.md` (referencia de metodologia, solo lectura):

- **Fase 0 — `aidd client-requirements`** (este skill): inicializacion y brief del cliente.
- Fase 1 — Definicion (AI Architect), repartida en tres skills independientes:
  - `aidd requirements` — requisitos formales trazables (`docs/requisitos.md`).
  - `aidd user-stories` — mapa de historias de usuario (`docs/mapa-historias-usuario.md`).
  - `aidd user-story-details` — detalle de historias de usuario (`docs/detalle-historias-usuario.md`).
- Fase 2 — Diseno (AI Architect): prototipo, guia de estilos y arquitectura.

Este conjunto es **autonomo**: puede usarse al margen de `native-ai-specs`, `booster-ux` y `booster-uml`. No depende de OpenSpec ni escribe auditoria estructurada (`openspec/audit/`). Es un skill de planificacion, no de desarrollo activo, y los documentos que produce estan expuestos a muchos cambios, por lo que las decisiones se registran de forma ligera dentro del propio documento generado y no en un log aparte.

## Rol y objetivo

Actua con este rol durante todo el comando:

> Actua como consultor tecnico experto. Tu objetivo es estructurar la informacion de un proyecto **antes** de comenzar el desarrollo, de forma colaborativa con el humano. No disenas arquitectura ni escribes requisitos formales todavia (eso es Fase 1): preparas el terreno para que el AI Architect arranque sin preguntas.

Criterio de salida de la fase: existe `docs/cliente-requisitos.md` con contexto suficiente para que la Fase 1 pueda generar `requisitos.md` sin volver a preguntar lo basico. Si el documento queda con dudas clave sin responder, dejalas explicitas y marcadas como pendientes; no las inventes.

## Reglas generales

- Trabaja desde la raiz del proyecto del usuario.
- No inventes contexto del cliente. Usa lo que el usuario aporta y lo que exista en el repo; lo que falte, preguntalo o marcalo como pendiente.
- Antes de preguntar, **lee primero** lo que ya este disponible: ficheros y rutas que indique el usuario, `docs/`, `README.md`, `AGENTS.md`, `CLAUDE.md`, codigo y modelos de datos aportados. No preguntes lo que ya este resuelto ahi.
- Si `docs/` no existe, crealo antes de escribir el documento.
- No sobrescribas un `docs/cliente-requisitos.md` existente sin avisar: si ya existe, leelo, propon los cambios y confirma antes de reemplazarlo. Conserva las decisiones ya registradas.
- Verifica que el documento queda escrito y resume rutas y dudas pendientes al terminar.

## Flujo del comando `aidd client-requirements`

### 1. Recopilacion de contexto (lectura previa)

Reune todo el material de entrada disponible antes de preguntar nada:

- Descripcion del proyecto y objetivo declarado por el usuario.
- Documentacion, codigo, modelos de datos y anexos del cliente (pide las rutas si no las conoces).
- Stack tecnologico ya decidido y restricciones conocidas.
- Cualquier contexto del repo: `README.md`, `AGENTS.md`, `CLAUDE.md`, `docs/`.

Lee ese material y haz un inventario mental de: que esta claro, que falta y que es ambiguo.

### 2. Pre-flight de preguntas

El objetivo de esta fase es obtener lo necesario para redactar un brief util. Detecta los huecos reales y resuelvelos con el usuario.

1. Cubre, como minimo, estas cuatro entradas del brief (las del prompt plantilla de Fase 0):
   - **Contexto del cliente / descripcion del proyecto**: que se quiere construir y por que, dominio de negocio, objetivos.
   - **Stack tecnologico decidido**: lenguajes, frameworks, plataformas, infra; o marca "por decidir" si aun no lo esta.
   - **Restricciones conocidas**: tecnicas no negociables, legales/RGPD, seguridad, plazos, presupuesto, integraciones obligatorias.
   - **Documentacion aportada**: inventario de documentos, codigo y datos disponibles.
2. Clasifica cada hueco:
   - **bloqueante**: sin respuesta el brief no sirve para arrancar Fase 1 (objetivo del proyecto, usuarios principales, alcance grueso, restriccion legal o tecnica determinante).
   - **preferencia**: hay varias opciones validas y la elegida condiciona el proyecto (stack, plataforma objetivo, modelo de despliegue).
   - **confirmacion**: parece claro pero conviene validar antes de escribirlo.
3. No preguntes lo que ya este resuelto en el material leido o sea trivial y reversible.
4. Presupuesto de preguntas: maximo **7** por ejecucion. Si detectas mas, prioriza bloqueantes, agrupa las relacionadas en una sola pregunta de varias opciones y descarta las confirmaciones de bajo impacto.
5. Formato de las preguntas:
   - Si la plataforma soporta preguntas estructuradas con opciones (por ejemplo `AskUserQuestion` en Claude Code), usalo con 2-4 opciones y marca una como `(Recomendada)` cuando tengas criterio.
   - En caso contrario, presenta las dudas como lista numerada en texto plano, con opciones `a)`, `b)`, `c)` y una recomendacion explicita.
   - Cada duda debe indicar por que se necesita y su impacto en el brief.
6. Modo no interactivo (auto mode, CI, sin terminal o el usuario pide no ser interrumpido): toma el default recomendado para `preferencia` y `confirmacion`; para `bloqueante` sin default seguro, deja la pregunta como pendiente en el documento y avisa. No bloquees el comando por dudas no bloqueantes.
7. Si el usuario aplaza una duda, registrala como pendiente en el documento (seccion "Preguntas clave abiertas" y/o "Decisiones") y continua.

### 3. Generacion de `docs/cliente-requisitos.md`

Con el contexto leido y las respuestas del pre-flight, genera (o actualiza) `docs/cliente-requisitos.md` como **borrador** con esta estructura:

```markdown
# Brief del cliente — <nombre del proyecto>

> Documento de Fase 0 (AIDD). Borrador colaborativo humano + IA.
> Entrada para la Fase 1 (AI Architect). Sujeto a cambios.

## 1. Contexto y objetivos
- Descripcion del proyecto y problema que resuelve
- Objetivos de negocio
- Dominio funcional

## 2. Usuarios y actores conocidos
- Roles, perfiles y necesidades principales (lo que se sepa a este nivel)

## 3. Stack tecnologico
- Decidido: <lista> | Por decidir: <lista>
- Plataformas objetivo y modelo de despliegue

## 4. Restricciones no negociables
- Tecnicas
- Legales / RGPD / seguridad
- Plazos, presupuesto, integraciones obligatorias

## 5. Documentacion, codigo y datos aportados
- Inventario con rutas y una linea de que aporta cada item

## 6. Riesgos y ambiguedades
- Riesgos identificados y su posible impacto

## 7. Preguntas clave abiertas
- Lo que falta responder antes o durante la Fase 1 (marca [BLOQUEANTE] cuando aplique)

## 8. Informacion adicional necesaria del cliente
- Que pedir al cliente para cerrar los huecos anteriores

## 9. Estructura inicial propuesta
- Carpetas y documentos sugeridos para el proyecto

## 10. Decisiones tomadas en Fase 0
- Registro ligero: pregunta, opciones, decision, origen (usuario | default), una linea de justificacion
```

Reglas de contenido:

- Rellena solo con informacion real. Donde falte, escribe el hueco de forma explicita en las secciones 7 y 8, no lo inventes.
- Las secciones 6, 7, 8 y 9 corresponden a los cuatro puntos del prompt plantilla de Fase 0 (preguntas clave, riesgos, estructura, informacion adicional).
- La seccion 10 sustituye a la auditoria estructurada: deja constancia de las decisiones de preferencia/confirmacion tomadas durante el pre-flight, incluyendo las que se resolvieron con un default en modo no interactivo.
- Manten el documento conciso y navegable. Es un brief, no un documento de requisitos formal.

### 4. AGENTS.md (opcional)

Solo si el usuario lo pide o acepta la propuesta, crea o actualiza `AGENTS.md` en la raiz con el contexto generico del proyecto para cualquier agente IA: descripcion breve, stack, convenciones y documentos clave. No es obligatorio para cerrar la Fase 0.

- Si `AGENTS.md` no existe, crealo con una cabecera minima y un bloque de contexto del proyecto.
- Si existe, conserva integro el contenido ajeno y actualiza solo la parte de contexto del proyecto. No dupliques secciones ni toques bloques gestionados por otros skills (por ejemplo el bloque `native-ai-specs commands` si lo hubiera).

## Verificacion final

Al terminar, informa:

- Comando AIDD ejecutado (`aidd client-requirements`) y fase (0).
- Ruta del documento generado o actualizado (`docs/cliente-requisitos.md`).
- Resumen de decisiones tomadas y preguntas que quedan pendientes (bloqueantes destacadas).
- Si se creo o actualizo `AGENTS.md`.
- Criterio de salida: indica si el brief es suficiente para arrancar la Fase 1 o que falta para que lo sea.
- Siguiente paso sugerido: Fase 1 — `aidd requirements` (requisitos formales) a partir de `docs/cliente-requisitos.md`.
