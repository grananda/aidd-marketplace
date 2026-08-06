---
name: aisdd-amend
description: AISDD (AI Spec-Driven Development) — incorpora una modificacion a un change de OpenSpec ya abierto y la ejecuta de forma incremental, mediante el comando `aisdd amend change [descripcion]` (alias legacy `native-ai amend change ...`). Pide al usuario que describa el cambio que quiere meter, lo traduce a delta de especificacion (criterios nuevos en `spec.md`, decision en `design.md`, tareas nuevas en `tasks.md`, entrada `Tipo: correccion` en `decisions.md`) y despues implementa **solo ese delta**, sin re-ejecutar `openspec instructions apply` y sin rehacer el trabajo ya entregado por el change. Toma una baseline de build y tests **antes** de tocar nada para distinguir lo que rompe el delta de lo que ya estaba roto, y verifica que el codigo relacionado con la nueva spec no provoca regresiones. Asume que la documentacion AIDD ya recoge el cambio si hacia falta: **no la valida**. No reconcilia cambios manuales del working tree: trabaja sobre el codigo tal como lo encuentra. Escribe entrada de auditoria en `openspec/audit/`. Usar cuando el usuario diga "mete este cambio en el change", "anade esto a lo que estamos implementando", "modifica el change abierto", "aisdd amend change", o similar.
metadata:
  author: NTT DATA Spain GDN-e
  version: "1.0.0"
---

# aisdd-amend (AI Spec-Driven Development)

Usa este skill cuando el usuario quiera **incorporar una modificacion a un change que ya esta abierto** (tipicamente ya implementado en parte o del todo) y que esa modificacion se ejecute sin rehacer lo anterior. Comando:

- `aisdd amend change [descripcion-del-cambio]`   (alias: `native-ai amend change ...`)

> **Alias legacy.** `aisdd <cmd>` y `native-ai <cmd>` son equivalentes. `aisdd` es el prefijo primario.

Responde y documenta en espanol siempre que sea posible. Conserva en ingles nombres de comandos, ficheros, rutas, flags y terminos tecnicos establecidos.

## Que resuelve y que no

Un change abierto recibe modificaciones que sus specs no contemplaban: una version que cambia, un campo mas en un formulario, un endpoint que devuelve otra cosa, un color. Re-ejecutar `openspec instructions apply` sobre un arbol ya implementado reinterpreta el change entero y arriesga rehacer trabajo y pisar ficheros. Este skill es la via alternativa: **especifica el delta y ejecuta solo el delta**.

Es el brazo operativo de la "Regla de corte" de la metodologia (niveles de correccion), documentada en el skill `aisdd-specs`, seccion "Correcciones durante la implementacion".

### Limites explicitos (no los cruces)

- **No valida la documentacion AIDD.** El skill **asume** que, si el cambio requeria tocar `docs/` (arquitectura, guia de estilos, detalle de HU), el humano ya lo hizo. No lo comprueba, no lo exige y no bloquea por ello. Lo unico que hace es dejar constancia de esa asuncion en `decisions.md`.
- **No reconcilia cambios manuales.** El working tree es la verdad. No compares el codigo con lo que el change decia que deberia existir, no intentes deducir quien escribio que, no revieras ni "restaures" nada que no encaje con tus expectativas.
- **No re-aplica el change.** Nunca ejecutes `openspec instructions apply` desde este skill.
- **No cierra ni archiva.** Eso sigue siendo `aisdd close change`.
- **No amplia el alcance.** Implementa lo que el usuario describio y nada mas. Nada de mejoras de paso, refactores oportunistas, reformateos ni reordenar imports.
- **Si la modificacion cambia el objetivo del change**, detente: no es una enmienda, es un change nuevo. Remite a `aisdd open change <slug>` y explica por que.
- **Si el change ya esta archivado**, detente: no se reabre. Remite a `aisdd open change <slug>`.

> "Sin rehacer lo que ya se hizo" **no** significa "no tocar nada existente". Si la modificacion sustituye un comportamiento ya implementado, ajusta ese codigo y retira el que quede muerto. Lo prohibido es **regenerar trabajo equivalente** (volver a scaffoldear, reescribir un modulo entero para cambiar un detalle), no editar lo que la modificacion afecta de verdad.

## Flujo del comando

### 1. Resolver el change objetivo

1. Si llega `[descripcion-del-cambio]` con un slug identificable, usalo.
2. Si no, lista los changes abiertos con OpenSpec (`openspec list` o equivalente).
3. Si solo hay uno abierto, usalo. Si hay varios, pregunta cual.
4. Si el change resuelto esta **archivado**, detente y remite a `aisdd open change`.

### 2. Capturar la modificacion (obligatorio)

Es el corazon del skill: el usuario describe, la IA desarrolla.

1. Si el usuario no aporto descripcion, **pidesela** con una pregunta abierta: *"Describe el cambio que quieres incorporar al change `<slug>`: que debe hacer distinto el sistema cuando esto este hecho."*
2. Reformula lo entendido y pregunta **solo lo imprescindible** para poder especificarlo. Techo de **3** preguntas, y es un techo, no una cuota. Las unicas dudas que merecen preguntarse:
   - **Comportamiento observable**: que cambia de cara al usuario o al consumidor de la API.
   - **Limite**: que **no** debe cambiar (lo que ya funciona y debe seguir igual).
   - **Verificacion**: como sabremos que esta bien.
   Si la descripcion del usuario ya cubre las tres, no preguntes nada.
3. Si la plataforma soporta preguntas estructuradas (`AskUserQuestion`), usalas con 2-4 opciones y marca una como `(Recomendada)`.
4. **Espejo antes de tocar nada**: devuelve al usuario un resumen corto de lo que vas a especificar e implementar, y confirma. Si el usuario corrige, reformula y vuelve a confirmar.
5. Modo no interactivo: si no hay descripcion y no puedes preguntar, **detente**. Este skill no inventa la modificacion.

### 3. Leer el estado real

Lee, en este orden:

1. Artefactos del change: `proposal.md`, `design.md`, `specs/**/spec.md`, `tasks.md`, `decisions.md`.
2. El **codigo tal como esta hoy** en las zonas que la modificacion va a tocar.

Regla: te interesa **lo que hay**, no lo que deberia haber. Si encuentras discrepancias entre el codigo y lo que el change describia, no las investigues ni las corrijas: pueden venir de trabajo manual que no conoces. Anotalas en el resumen final solo si afectan directamente a lo que vas a implementar.

No leas `docs/` para validar coherencia. Si necesitas un dato concreto de la arquitectura o la guia de estilos para implementar bien, consultalo puntualmente como contexto, pero no audites nada ni informes de desalineaciones.

### 4. Baseline antes de tocar nada (paso critico)

**Antes** de escribir una sola linea, captura el estado de partida:

1. Detecta el runner de tests y el comando de build del repo (`package.json`, `Makefile`, `pom.xml`, `pyproject.toml`...).
2. Ejecuta build y suite de tests **tal cual**, y **registra el resultado**: que pasa, que falla, cuantos.
3. Si algo ya falla ahora, eso es **preexistente**. No es tuyo, no lo arregles y no lo escondas.
4. Si no hay tests o el build no arranca, dilo explicitamente y sigue: la verificacion del paso 6 sera manual y lo reportaras como tal.

Esta baseline es lo que te permite distinguir lo que rompe tu delta de lo que ya estaba roto, sin necesidad de conocer los cambios manuales previos. Sin ella, no puedes afirmar nada sobre regresiones.

### 5. Escribir el delta de especificacion

Toca **solo** lo que la modificacion exige, y de forma incremental:

| Artefacto | Que escribes | Que NO haces |
|-----------|--------------|--------------|
| `specs/**/spec.md` | Criterios nuevos o modificados por la enmienda | No reescribes ni reordenas los criterios ya satisfechos |
| `design.md` | Solo si cambia una decision tecnica del change | No lo reescribes por un detalle de implementacion |
| `proposal.md` | Una linea en el alcance si la enmienda lo amplia | No reformulas el objetivo del change |
| `tasks.md` | Tareas **nuevas**, sin marcar, agrupadas bajo un encabezado de enmienda | No marcas, desmarcas ni reordenas las tareas existentes |
| `decisions.md` | Una entrada `Tipo: correccion` (formato abajo) | No editas ni borras entradas anteriores |

Sobre `tasks.md`: **no toques el estado de las tareas preexistentes**. Puede haber tareas sin marcar que estan hechas y tareas marcadas que no, y no tienes forma fiable de saberlo. Anade las tuyas al final:

```markdown
## Enmienda — <descripcion corta>

- [ ] <tarea nueva>
- [ ] <tarea nueva>
```

Si una tarea preexistente queda **obsoleta** por la enmienda, no la borres: anota debajo una linea `> Obsoleta por la enmienda "<descripcion corta>"`.

Entrada en `decisions.md`:

```markdown
## <slug-de-la-enmienda>

- **Fecha**: <YYYY-MM-DD>
- **Tipo**: correccion
- **Nivel**: 2 (decision no documentada) | 3 (contradiccion documental)
- **Origen**: usuario
- **Contexto**: enmienda solicitada durante la implementacion del change <slug>
- **Peticion del usuario**: <la descripcion literal o resumida que dio>
- **Decision**: <lo que se especifica e implementa>
- **Justificacion**: <una linea>
- **Documentacion AIDD**: asumida al dia por el usuario; este comando no la verifica
- **Artefactos tocados**: <lista de ficheros del change modificados>
```

El campo **Documentacion AIDD** es obligatorio: deja por escrito que la coherencia documental se asumio y no se comprobo, para que quien audite luego sepa donde no mirar en busca de garantias.

### 6. Ejecutar el delta

1. Implementa **unicamente** las tareas nuevas de la enmienda.
2. **Nunca** ejecutes `openspec instructions apply`. Aplicas el cambio tu, directamente sobre el codigo.
3. Toca el minimo numero de ficheros posible. Si te ves editando muchos, para y replantea: probablemente esto era un change nuevo (ver limites).
4. Si la enmienda sustituye comportamiento existente, ajusta ese codigo y elimina el que quede muerto por el cambio. No dejes ramas huerfanas ni configuracion sin uso.

### 7. Verificar que no rompe nada

Esta es la responsabilidad que el skill **si** asume. No basta con que lo nuevo funcione.

1. **Radio de impacto**: parte de los ficheros que has modificado y localiza quien depende de ellos (importaciones, llamadas, rutas, plantillas, tests que los cubren). Ese conjunto es lo que hay que verificar, no solo el fichero editado.
2. **Re-ejecuta build y tests** y **compara contra la baseline del paso 4**:
   - Fallo nuevo que antes pasaba -> **es tuyo**: arreglalo.
   - Fallo que ya estaba en la baseline -> **no es tuyo**: no lo toques, reportalo como preexistente.
   - Test que antes fallaba y ahora pasa -> mencionalo, no lo des por casualidad.
3. **Criterios ya verdes**: relee los criterios de aceptacion del change que ya estaban satisfechos y comprueba los que caen dentro del radio de impacto. Los tests no siempre los cubren.
4. **Cobertura del delta**: si el repo tiene tests, la enmienda necesita el suyo. Anadelo salvo que el usuario diga lo contrario.
5. Si no puedes verificar algo (sin tests, sin entorno, sin datos), **dilo abiertamente** en el resumen. No afirmes que no hay regresiones si no lo has comprobado.

### 8. Jira (opcional)

Si la integracion con Jira esta activa (seccion `jira:` en `openspec/config.yaml` + MCP de Atlassian disponible), **no muevas nada de columna**: una enmienda no abre ni cierra trabajo, y el change ya deberia estar en curso. Limitate a:

- Anotar la enmienda como comentario en la Story (o en la sub-tarea del change si existe), con una linea de que se incorporo.
- Si el change no tenia aun ninguna HU registrada en `docs/jira-sync.md`, no lo inventes: avisa en el resumen.

Si Jira no esta configurado, omite el bloque sin error.

## Auditoria y trazabilidad

Obligatoria, con el mismo formato y reglas que el resto de comandos AISDD (ver `aisdd-specs`, seccion "Auditoria y trazabilidad"): fichero `openspec/audit/YYYY-MM.jsonl`, append-only, una entrada por invocacion.

Particularidades de este comando:

- `command`: `aisdd amend change`.
- `prompt_version`: `<skill_version>:amend-change`.
- `input_files`: artefactos del change leidos + ficheros de codigo que la enmienda toca.
- `output_files`: artefactos del change modificados + ficheros de codigo escritos.
- `decisions`: incluye la entrada `correccion` de la enmienda.
- `status`: `ok` si el delta quedo implementado y verificado; `partial` si quedaron fallos preexistentes o verificaciones no realizables; `aborted` si te detuviste (sin descripcion, change archivado, alcance de change nuevo).
- `errors`: incluye los fallos **preexistentes** detectados en la baseline, como mensajes cortos. Que consten sin atribuirselos a la enmienda.

## Verificacion final

Al terminar, informa:

- Comando ejecutado y change objetivo.
- **La modificacion tal como la entendiste** (una o dos lineas), para que el usuario detecte de inmediato si te desviaste.
- Artefactos del change modificados y entrada de `decisions.md` escrita.
- Ficheros de codigo tocados.
- **Baseline vs resultado**: build y tests antes / despues, con los fallos preexistentes listados aparte de los que provoco (y arreglo) la enmienda.
- Criterios ya satisfechos que has re-verificado, y los que no has podido verificar.
- Recordatorio, en una linea: la coherencia con la documentacion AIDD se asumio, no se comprobo.
- Entrada de auditoria escrita (ruta e `id`).
- Tareas manuales pendientes, si las hay.
