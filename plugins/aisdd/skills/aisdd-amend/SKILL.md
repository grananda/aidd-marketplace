---
name: aisdd-amend
description: AISDD (AI Spec-Driven Development) — incorpora una modificacion a un change de OpenSpec ya abierto y la ejecuta de forma incremental, mediante el comando `aisdd amend change [descripcion]` (alias legacy `native-ai amend change ...`). Pide al usuario que describa el cambio que quiere meter, lo traduce a delta de especificacion (criterios nuevos en `spec.md`, decision en `design.md`, tareas nuevas en `tasks.md`, entrada `Tipo: correccion` en `decisions.md`) y despues implementa **solo ese delta**, sin re-ejecutar `openspec instructions apply` y sin rehacer el trabajo ya entregado por el change. Toma una baseline de build y tests **antes** de tocar nada para distinguir lo que rompe el delta de lo que ya estaba roto, y verifica que el codigo relacionado con la nueva spec no provoca regresiones. En topologia **`fraccionado`** un amend no sale de su repositorio --los changes de los demas lanes viven en otros repos, con su propio `openspec/`--: enmienda la parte de aqui y nombra la que queda pendiente y en cual. En roadmaps **multilane** de un solo repo deriva del propio delta que changes abiertos quedan afectados (en vez de preguntarlo), trata un delta cross-lane como **parada coordinada** —lanes hermanos detenidos, una baseline por change, nivel 4 en `decisions.md`— y **marca** las fases futuras afectadas con `amended_by` para que el lane que aun no arranco no implemente contra un contrato ya desmentido; nunca re-fasea el roadmap. Asume que la documentacion AIDD ya recoge el cambio si hacia falta: **no la valida**. No reconcilia cambios manuales del working tree: trabaja sobre el codigo tal como lo encuentra. Escribe entrada de auditoria en `openspec/audit/` usando el script `audit.py` de `aisdd-specs` (determinista), con respaldo manual si Python no esta disponible. Usar cuando el usuario diga "mete este cambio en el change", "anade esto a lo que estamos implementando", "modifica el change abierto", "aisdd amend change", o similar.
metadata:
  author: NTT DATA Spain GDN-e
  version: "1.8.0"
---

# aisdd-amend (AI Spec-Driven Development)

Usa este skill cuando el usuario quiera **incorporar una modificacion a un change que ya esta abierto** (tipicamente ya implementado en parte o del todo) y que esa modificacion se ejecute sin rehacer lo anterior. Comando:

- `aisdd amend change [descripcion]`   (alias: `native-ai amend change ...`)

> **Alias legacy.** `aisdd <cmd>` y `native-ai <cmd>` son equivalentes. `aisdd` es el prefijo primario.

Responde y documenta en espanol siempre que sea posible. Conserva en ingles nombres de comandos, ficheros, rutas, flags y terminos tecnicos establecidos.

## Que resuelve y que no

Un change abierto recibe modificaciones que sus specs no contemplaban: una version que cambia, un campo mas en un formulario, un endpoint que devuelve otra cosa, un color. Re-ejecutar `openspec instructions apply` sobre un arbol ya implementado reinterpreta el change entero y arriesga rehacer trabajo y pisar ficheros. Este skill es la via alternativa: **especifica el delta y ejecuta solo el delta**.

Es el brazo operativo de la "Regla de corte" de la metodologia (niveles de correccion), documentada en el skill `aisdd-specs`, en `${CLAUDE_PLUGIN_ROOT}/skills/aisdd-specs/references/implement-change.md` ("Correcciones durante la implementacion").

### Limites explicitos (no los cruces)

- **No valida la documentacion AIDD.** El skill **asume** que, si el cambio requeria tocar `docs/` (arquitectura, guia de estilos, detalle de HU), el humano ya lo hizo. No lo comprueba, no lo exige y no bloquea por ello. Lo unico que hace es dejar constancia de esa asuncion en `decisions.md`.
- **No reconcilia cambios manuales.** El working tree es la verdad. No compares el codigo con lo que el change decia que deberia existir, no intentes deducir quien escribio que, no revieras ni "restaures" nada que no encaje con tus expectativas.
- **No re-aplica el change.** Nunca ejecutes `openspec instructions apply` desde este skill.
- **No cierra ni archiva.** Eso sigue siendo `aisdd close change`.
- **No amplia el alcance.** Implementa lo que el usuario describio y nada mas. Nada de mejoras de paso, refactores oportunistas, reformateos ni reordenar imports.
- **Si la modificacion cambia el objetivo del change**, detente: no es una enmienda, es un change nuevo. Remite a `aisdd open change [what-you-want-to-build]` y explica por que.
- **Si el change ya esta archivado**, detente: no se reabre. Remite a `aisdd open change [what-you-want-to-build]`.
- **Si el delta cruza lanes** (roadmaps `multilane`), no es un amend local: es una **parada coordinada** de los lanes hermanos. Sigue el procedimiento de "Deltas que cruzan lanes" — no lo ejecutes lane a lane como si fueran enmiendas independientes.
- **En topologia `externalizado`, el amend se lanza desde el repo de codigo, como los demas.** Sube hasta `openspec/config.yaml` para encontrar las specs; la baseline de build y tests se toma **donde estas**, que es donde vive el proyecto. No cambies de carpeta ni se lo pidas al usuario.
- **En topologia `fraccionado` un amend no sale de este repositorio.** Los changes de los demas lanes viven en otros repos, con su propio `openspec/` y su propio arbol: no puedes leerlos, ni enmendarlos, ni tomarles baseline. Si el delta afecta a otro repo, **enmienda solo la parte de este** y **di explicitamente que queda pendiente en cual** — el amend lo lanza ahi quien trabaje ese repo. No lo presentes como hecho.
- **No re-fasea el roadmap.** Puede *marcar* fases afectadas como senal para el humano, pero no reescribe `docs/roadmap.md` ni reordena fases: eso es `aisdd roadmap`.
- **Detenerse tambien se audita.** Cualquiera de las paradas anteriores —objetivo distinto, change archivado, lanes que no se pueden detener, sin descripcion en modo no interactivo— **escribe igualmente la entrada de auditoria con `status: aborted`** y el motivo en `errors`, antes de terminar. La entrada normal sale del final del flujo, y ese final no se alcanza al detenerse: sin esta regla, pararse no dejaria rastro. Una parada es un resultado del comando.

> "Sin rehacer lo que ya se hizo" **no** significa "no tocar nada existente". Si la modificacion sustituye un comportamiento ya implementado, ajusta ese codigo y retira el que quede muerto. Lo prohibido es **regenerar trabajo equivalente** (volver a scaffoldear, reescribir un modulo entero para cambiar un detalle), no editar lo que la modificacion afecta de verdad.

## Flujo del comando

### 1. Resolver el change objetivo

1. Si llega `[descripcion-del-cambio]` con un slug identificable, usalo.
2. Si no, lista los changes abiertos con OpenSpec (`openspec list` o equivalente).
3. Si solo hay uno abierto, usalo. Si hay varios, pregunta cual.
4. Si el change resuelto esta **archivado**, detente y remite a `aisdd open change`.

**En roadmaps `multilane` el punto 3 no vale**: con varios lanes vivos siempre hay varios changes abiertos, y preguntar al usuario cual enmendar le traslada una decision que el propio delta ya determina.

Lee `roadmap.mode` en `openspec/config.yaml` antes de nada. Si es `atomic` o no existe, aplica los cuatro puntos anteriores tal cual y sigue. Si es `multilane`, **la resolucion del change queda aplazada**: no puedes derivarla todavia porque aun no conoces el delta. Haz solo esto ahora:

- Anota que el roadmap es multilane y carga `roadmap.lanes` (ids y `paths`) y la lista de changes abiertos con su lane.
- Si el usuario aporto un slug identificable, usalo como **candidato**, no como resolucion cerrada: el delta puede afectar a mas changes que ese.
- **No preguntes cual enmendar.** Pasa directamente a la seccion 2 y captura la modificacion.

Vuelve aqui al terminar la seccion 2, cuando ya sepas que comportamiento cambia, y **deriva entonces los changes afectados** cruzando:

- las **rutas** que el delta necesita tocar, contra los `paths` de cada lane
- los **specs** que quedan desmentidos, contra los `spec.md` de cada change abierto

El resultado es un conjunto de changes, no necesariamente uno:

- **Un solo change afectado** -> amend normal: sigue el flujo desde la seccion 3.
- **Varios changes afectados**, o rutas fuera de todo lane, o el contrato compartido tocado -> ve a "Deltas que cruzan lanes".

Incluye los changes derivados y su porque en el **espejo** (punto 4 de la seccion 2), antes de tocar nada. El usuario confirma o corrige el **alcance**; no le pidas que elija el change.

### 1.5 Deltas que cruzan lanes

> **No se ejecuta en orden.** Se entra aqui desde la resolucion aplazada de la seccion 1, ya con el delta capturado, y solo cuando afecta a mas de un lane. En un amend normal, saltate esta seccion y la 1.6.

Un delta cross-lane rompe el supuesto central del skill: la baseline. La seccion 4 captura build y tests **antes** de tocar nada para poder distinguir despues lo que rompe el delta de lo que ya estaba roto. Con N lanes vivos hay N devs con el arbol en estados distintos, y **una sola baseline no describe ninguno de ellos**: un test rojo puede venir del trabajo en vuelo de otro lane, no de tu delta.

Procedimiento:

1. **Detente antes de tocar nada** e informa: que changes estan afectados, que lanes representan y que parte del contrato compartido queda desmentida (si aplica).
2. **Serializa, no paralelices.** Pide al usuario que **detenga los lanes hermanos** (que sus devs no implementen mientras dure la enmienda). Es el coste real de un delta cross-lane y hay que decirlo, no absorberlo en silencio.
3. **Una baseline por change afectado**, tomada en el momento de enmendarlo — no una global al principio. Registra cada una por separado.
4. **Enmienda change a change**, en orden de dependencia: primero el que define (tipicamente el que expone el contrato), despues los que consumen. Cada uno con su delta de spec y su verificacion.
5. **Registra en cada `decisions.md`** la entrada `Tipo: correccion` con `Nivel: 4`, el lane propio y los lanes afectados, segun el formato de `aisdd-specs`.
6. **Reanuda**: informa de que los lanes pueden retomar el trabajo y de que ha cambiado en el contrato.

Si el usuario no puede detener los lanes hermanos, **no ejecutes el amend cross-lane**. Dilo y remite a una barrera (`FB-NN`) via `aisdd roadmap`: una modificacion del contrato con lanes en vuelo es exactamente lo que las barreras existen para ordenar.

> **Esta seccion no aplica en topologia `fraccionado`**, donde no hay barreras ni lanes hermanos que detener: cada repo es una linea aparte y lo que compartan viaja como artefacto versionado. Un delta que toca dos repos son **dos enmiendas independientes**, una en cada uno, y cada una con su baseline --que ahi si describe su arbol, porque solo hay uno--. Enmienda la de aqui, nombra la otra y su repo, y para.

### 1.6 Lanes cuya fase aun no esta abierta

> Complementa a la 1.5: se aplica al mismo delta cross-lane, para los lanes que **no** tienen change vivo que enmendar.

Este skill solo alcanza **changes vivos**. Si el delta afecta tambien a un lane cuya fase todavia no se ha abierto, ese lane arrancara mas tarde con la especificacion vieja y **nadie se lo dira**.

Para cerrar ese agujero, sin re-fasear:

1. Identifica las fases futuras afectadas en `roadmap.phases` (las de otros lanes que dependan del contrato o de las specs que el delta cambia).
2. **Marcalas**: anade a cada una en `openspec/config.yaml` una clave `amended_by: <slug-del-change-enmendado>` y una linea en la seccion correspondiente de `docs/roadmap.md` indicando que la fase debe leer esa enmienda antes de abrirse.
3. **No cambies nada mas del roadmap**: ni el orden, ni el alcance, ni los `change_hint`. La marca es una senal, no un re-faseado.
   `aisdd open change` la recoge en su paso "Enmiendas pendientes de esta fase": al abrir esa fase lee el `decisions.md` del change indicado, incorpora el delta a sus specs y retira la marca. Si `aisdd roadmap` se re-ejecuta antes, conserva los `amended_by` de las fases que sobrevivan con el mismo `change_hint`.
4. Dilo en el resumen final: que fases quedaron marcadas y que lanes las ejecutaran.

Es el mismo patron que ya usa `aisdd roadmap` cuando registra "Conflictos de alineacion roadmap<->sprint" en lugar de reescribir el `sprint-plan.md`: **quien detecta el desajuste lo senala; quien tiene la competencia lo resuelve.**

### 2. Capturar la modificacion (obligatorio)

Es el corazon del skill: el usuario describe, la IA desarrolla.

1. Si el usuario no aporto descripcion, **pidesela** con una pregunta abierta: *"Describe el cambio que quieres incorporar al change `<slug>`: que debe hacer distinto el sistema cuando esto este hecho."* Si el change aun no esta resuelto (roadmap `multilane`, resolucion aplazada), pregunta sin nombrarlo: *"Describe el cambio que quieres incorporar al trabajo en curso: que debe hacer distinto el sistema cuando esto este hecho."*
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
4. Si no hay tests o el build no arranca, dilo explicitamente y sigue: la verificacion de la seccion 7 sera manual y lo reportaras como tal.

Esta baseline es lo que te permite distinguir lo que rompe tu delta de lo que ya estaba roto, sin necesidad de conocer los cambios manuales previos. Sin ella, no puedes afirmar nada sobre regresiones.

**En roadmaps `multilane`, una baseline global no vale.** Otros lanes pueden estar implementando ahora mismo, asi que un fallo nuevo puede no ser tuyo. Reglas:

- **Amend de un solo change**: baseline normal, pero al reportar regresiones acota el juicio a **las rutas de tu lane**. Un fallo en ficheros de otro lane no es una regresion de tu delta: senalalo como ruido externo y no lo arregles.
- **Amend cross-lane**: una baseline **por change**, tomada justo antes de enmendar ese change, con los lanes hermanos ya detenidos (ver "Deltas que cruzan lanes"). Sin la parada, la baseline no significa nada y no puedes afirmar nada sobre regresiones — dilo en vez de fingir que si.

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
- **Nivel**: 2 (decision no documentada) | 3 (contradiccion documental) | 4 (contrato compartido)
- **Origen**: usuario
- **Contexto**: enmienda solicitada durante la implementacion del change <slug>
- **Peticion del usuario**: <la descripcion literal o resumida que dio>
- **Decision**: <lo que se especifica e implementa>
- **Justificacion**: <una linea>
- **Documentacion AIDD**: asumida al dia por el usuario; este comando no la verifica
- **Artefactos tocados**: <lista de ficheros del change modificados>
- **Lane**: <lane-id>                              # solo en modo multilane
- **Lanes afectados**: <lane-id, ...>              # solo nivel 4
- **Fases marcadas**: <id de fase, ...>            # solo nivel 4, fases futuras senaladas con amended_by
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
- **Enmienda cross-lane**: anota el comentario en las Stories de **todos** los changes enmendados, indicando que forman parte de la misma parada coordinada. Sigue sin haber transiciones de columna.

Si Jira no esta configurado, omite el bloque sin error.

### 9. Comprobar el mojibake de lo escrito

**Obligatorio**, igual que en el resto de comandos AISDD. Pasa `check_mojibake.py --fix`
de `aisdd-specs` (ver `${CLAUDE_PLUGIN_ROOT}/skills/aisdd-specs/references/scripts.md`) sobre los artefactos **documentales**
que la enmienda haya tocado: el `spec.md`, `design.md`, `tasks.md` y `decisions.md` del
change, y los de **todos** los changes si la enmienda cruzo lanes. **El codigo que la
enmienda escribe no entra**, aunque figure en `output_files`: ver
`${CLAUDE_PLUGIN_ROOT}/skills/aisdd-specs/references/scripts.md`.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/aisdd-specs/scripts/check_mojibake.py" --fix <ficheros>
```

Va **antes** de la entrada de auditoria porque `audit.py` calcula el hash de cada fichero:
repararlo despues registraria el hash de la version corrupta. Si algo queda con `U+FFFD`,
no se puede reparar — hay que regenerar el fichero; dilo en la verificacion final.

## Auditoria y trazabilidad

Obligatoria, con el mismo formato y reglas que el resto de comandos AISDD (ver `${CLAUDE_PLUGIN_ROOT}/skills/aisdd-specs/references/audit.md`): fichero `openspec/audit/YYYY-MM.jsonl`, append-only, una entrada por invocacion.

**Incluye el bloque `verification`** con lo que dieron el build y los tests del delta: este comando toma baseline antes de tocar nada y verifica despues, asi que el dato ya lo tienes. Omite los campos que no ejecutaste en vez de ponerlos a cero.

**Si `roadmap.topology` es `externalizado`, commitea y sube el repo de gobierno** despues de escribir la entrada, como el resto de comandos: ver "Ritmo de commit y push" en `aisdd-specs`.

**Usa el script**, igual que el resto de comandos AISDD: `audit.py` de `aisdd-specs` compone la entrada, calcula los hashes y aplica la purga de forma determinista (ver `${CLAUDE_PLUGIN_ROOT}/skills/aisdd-specs/references/scripts.md`). Componerla a mano es la via de respaldo si Python no esta disponible.

```bash
echo '<json>' | python3 "${CLAUDE_PLUGIN_ROOT}/skills/aisdd-specs/scripts/audit.py" --root <projectRoot>
```

Si Python no esta disponible o el script falla, compon la entrada a mano segun `${CLAUDE_PLUGIN_ROOT}/skills/aisdd-specs/references/audit.md`, y dilo en el resumen. **No la omitas**: la auditoria es obligatoria tambien cuando el script no puede escribirla.

Particularidades de este comando:

- `command`: `aisdd amend change`.
- `prompt_version`: `<skill_version>:amend-change`.
- `input_files`: artefactos del change leidos + ficheros de codigo que la enmienda toca.
- `output_files`: artefactos del change modificados + ficheros de codigo escritos.
- `decisions`: incluye la entrada `correccion` de la enmienda.
- `status`: `ok` si el delta quedo implementado y verificado; `partial` si quedaron fallos preexistentes o verificaciones no realizables; `aborted` si te detuviste en cualquiera de los puntos de parada (ver "Limites explicitos"): sin descripcion en modo no interactivo, change archivado, alcance de change nuevo, o lanes hermanos que no se pueden detener. **Una parada siempre deja entrada**; la ausencia de entrada no es un resultado valido.
- `errors`: incluye los fallos **preexistentes** detectados en la baseline, como mensajes cortos. Que consten sin atribuirselos a la enmienda.
- `notes`: si hubo acciones en Jira (comentarios en Stories o sub-tareas), una linea por issue tocado. Son acciones con efecto externo que no son ficheros, asi que no caben en `output_files`.

## Verificacion final

Al terminar, informa:

- Comando ejecutado y change objetivo.
- **La modificacion tal como la entendiste** (una o dos lineas), para que el usuario detecte de inmediato si te desviaste.
- Artefactos del change modificados y entrada de `decisions.md` escrita.
- Ficheros de codigo tocados.
- **Baseline vs resultado**: build y tests antes / despues, con los fallos preexistentes listados aparte de los que provoco (y arreglo) la enmienda.
- Criterios ya satisfechos que has re-verificado, y los que no has podido verificar.
- Recordatorio, en una linea: la coherencia con la documentacion AIDD se asumio, no se comprobo.
- Resultado de la comprobacion de mojibake: sin incidencias, ficheros reparados, o ficheros que hay que regenerar por tener `U+FFFD`.
- Entrada de auditoria escrita (ruta e `id`).
- Tareas manuales pendientes, si las hay.

## Proximos pasos

**Tambien cuando el comando se detiene.** En las cuatro paradas —change ya archivado, delta que cambia el objetivo, delta cross-contrato sin coordinacion posible, y espejo sin confirmar— di **que comando desbloquea**: `aisdd open change` para un change nuevo si el objetivo cambio, o el mismo `aisdd amend change` tras acordar el alcance. Ese camino no llega al final del flujo, asi que la sugerencia va en la parada.

Cierra con lo que el usuario hace ahora, con el comando resuelto: `aisdd implement change <change-slug>` si quedan tareas del delta, o `aisdd close change <change-slug>` si ya esta. **Si marcaste fases futuras con `amended_by`, nombralas**: quien las abra tiene que saber que arrastran una enmienda. Reglas completas en `${CLAUDE_PLUGIN_ROOT}/skills/aisdd-specs/references/next-steps.md`.
