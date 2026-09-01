---
name: aidd-architecture
description: Fase 2 (paso 2.4) del conjunto AIDD (AI Driven Development). Consolida la arquitectura tecnica definitiva e implementable del producto, mediante el comando `aidd architecture` (alias `aidd fase 2.4`). Actua como arquitecto de software senior que analiza como fuentes de verdad `docs/detalle-historias-usuario.md`, `docs/propuesta-arquitectura-base.md` y `docs/guia-estilos.md` y genera `docs/arquitectura-base.md` con objetivo y alcance, principios y decisiones arquitectonicas explicitas, arbol de carpetas real, descomposicion por modulos, capas y responsabilidades, flujos de informacion, gestion de estado, navegacion, integraciones, seguridad, accesibilidad, observabilidad, rendimiento, escalabilidad y riesgos. Si el producto vive en **varios repositorios** los declara en su seccion 3 con una tabla `id | contiene` --con el nombre basta; ni URL ni ruta--: cada repo es autonomo —su propio `openspec/` y su propia copia de `docs/`—, sin repo padre ni submodulos, y declararlos **obliga a `aisdd roadmap` al modo `multilane` con un lane por repo**. Exige que los repos sean independientes en codigo: lo que compartan viaja como artefacto versionado, y un repo que necesita el fuente de otro es una frontera mal puesta que se registra como riesgo. Es el insumo principal del roadmap y cierra el Diseno (AI Architect). Skill de planificacion, autonomo del mundo OpenSpec/aisdd-specs y sin auditoria estructurada.
metadata:
  author: NTT DATA Spain GDN-e
  version: "1.3.0"
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

Este conjunto es **autonomo**: puede usarse al margen de `aisdd-specs`, `booster-ux` y `booster-uml`. No depende de OpenSpec ni escribe auditoria estructurada. Las decisiones se registran de forma ligera dentro del propio documento generado.

Como complemento opcional, al final del comando se genera una **vista HTML** de la arquitectura base con `booster-docs` (ver el paso final del flujo). El `.md` sigue siendo la **unica fuente de verdad**; el HTML es solo para consumo humano y no altera el flujo AIDD si `booster-docs` no esta instalado.

> `docs/arquitectura-base.md` es el **insumo principal** del roadmap. En la metodologia completa lo consume `aisdd roadmap` (Fase 3), pero este skill no depende de ello: produce el documento de arquitectura tanto si luego se usa `aisdd-specs` como si no.

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

## 1. Objetivo y alcance
## 2. Principios y decisiones arquitectonicas
## 3. Estructura de la solucion (arbol de carpetas real)
- **Si el producto vive en mas de un repositorio, declaralos aqui** con una tabla `id | contiene` --con el nombre basta; ni URL ni ruta--. Cada repo es autonomo --su propio `openspec/` y su propia copia de `docs/`-- y declararlos **obliga al modo `multilane` con un lane por repo**. Ver "Producto repartido en varios repositorios".
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

## Producto repartido en varios repositorios

Un producto puede vivir en varios repos --frontal, servicios, datos-- y **eso es una decision de arquitectura**, no de faseado: decide fronteras de despliegue, de equipo y de contrato. Por eso se declara aqui y no en el roadmap, que la consume.

Lo habitual no es elegirlo: el cliente crea un repo por parte del proyecto y no hay repo raiz que los agrupe. El modelo lo asume. **Cada repo es autonomo**: lleva su propio `openspec/` y su propia copia de `docs/`. No hay repo padre, no hay submodulos y no hay nada que clonar de forma especial.

Si es el caso, la seccion 3 lleva la tabla de repositorios:

```markdown
### Repositorios

El producto vive en <N> repositorios **independientes**. Cada uno tiene su propio
`docs/` y su propio `openspec/`, y se desarrolla como una linea de trabajo separada.

| id | Contiene |
|---|---|
| `front` | SPA Angular |
| `bff` | BFF y agregacion |
| `datos` | Batch y modelo de datos |
```

Reglas:

- **Con el nombre basta.** `id` y una linea de contenido es todo lo que hace falta. **No pidas la URL del remote ni la ruta local**: no las necesita nadie —ningun comando salta de un repo a otro— y son lo primero que se queda obsoleto cuando el cliente migra de organizacion o alguien clona con otro nombre. Si el usuario las da, puedes anadirlas como columnas opcionales; **no las inventes y no las exijas**.
- **`id` en kebab-case y estable.** Es el nombre del repo **y el de su lane**, que son lo mismo. Es la clave con la que el roadmap reparte fases y con la que se agregan los KPI globales. Cambiarlo rompe esos enlaces, igual que cambiar un `change_hint`.
- **Di que contiene cada uno en una linea.** Es lo que permite decidir despues si un modulo cae en uno o en otro, y es la unica parte que un humano va a leer.
- **La descomposicion por modulos (seccion 4) indica en que repo cae cada modulo.** Un modulo repartido entre dos repos es una senal de que la frontera esta mal puesta: dilo en la seccion 13 en vez de esconderlo.
- **Los repos tienen que ser independientes en codigo, y eso hay que comprobarlo.** El modelo entero descansa en que ninguno compila, testea ni despliega contra el fuente de otro. Lo que compartan viaja como **artefacto versionado** --un contrato OpenAPI publicado, un paquete, un esquema de eventos-- y cada repo consume la version que elige, cuando la elige.

  Si al describir la arquitectura aparece un repo que necesita el codigo de otro para funcionar, **la frontera esta mal puesta y hay que decirlo en la seccion 13**. No lo resuelvas moviendo la coordinacion al roadmap: el faseado no puede arreglar un acoplamiento de compilacion.
- **No inventes repos.** Si el usuario no ha dicho cuantos hay, es uno. Preguntalo en el paso de recopilacion, no lo deduzcas de que la arquitectura "pide" separacion. Y **no partas en repos para paralelizar**: partir cuesta un despliegue, un pipeline y una copia de la documentacion.

> **Por que importa aguas abajo.** Declarar mas de un repo aqui **obliga al modo `multilane`** en `aisdd roadmap`, con **un lane por repo**. No es una recomendacion ni una pregunta del pre-flight: la frontera de repos ya partio el trabajo, y el faseado solo la reconoce. Con un solo repo no se fuerza nada y los tres modos siguen disponibles.
>
> Cada repo ejecuta **solo las fases de su lane**, y todo lo demas ocurre dentro de sus propios muros: su `git`, su `openspec/`, un change abierto a la vez, **una PR por change**. Los KPI globales se sacan aparte, agregando los `openspec/` de todos los repos desde la carpeta que los contiene.

Reglas de contenido:

- Cada decision explicita y justificada; el arbol de carpetas debe ser real, no ilustrativo.
- No debe contradecir historias, propuesta ni guia de estilos. Los conflictos resueltos se documentan en la seccion 2 o 13.
- La seccion 14 sustituye a la auditoria estructurada e incluye decisiones resueltas por default.

### Sello de version y fecha-hora (antes de renderizar)

Tras escribir o actualizar `docs/arquitectura-base.md`, y **antes** de generar la vista HTML, sella el documento:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/stamp_doc.py" --input docs/arquitectura-base.md --gated
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
- Siguiente paso sugerido: **`aisdd init`** y despues **`aisdd roadmap`** (Fase 3 — Inicializacion y Roadmap, AI Lead). Aqui termina el diseno y empieza la ejecucion: es el punto donde AIDD entrega a AISDD.
- **`aisdd roadmap` exige `docs/detalle-historias-usuario.md`** con sus tallas. Si vienes de la Fase 1 completa ya lo tienes; si no, el comando se detiene y remite a `aidd user-story-details`.
- Si el proyecto va a planificar entrega y recursos, **`aiba project-plan`** puede ir antes o despues del roadmap: no depende de el, y `aiba sprint-planning` necesita los dos.
- **Como se aprueba**: `python "${CLAUDE_PLUGIN_ROOT}/scripts/stamp_doc.py" --input <documento> --approve "<nombre>"`. Anota la version actual como aprobada, y a partir de ahi el sello distingue tres estados: sin aprobar, aprobada, y **cambiada despues de aprobarse** — que es el que importa.
