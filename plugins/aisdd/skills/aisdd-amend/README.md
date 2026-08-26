# aisdd-amend

Skill para **incorporar una modificacion a un change de OpenSpec ya abierto** y ejecutarla de forma incremental, sin rehacer el trabajo que el change ya entrego.

> **Alias legacy**: `native-ai amend change ...` equivale a `aisdd amend change ...`.

## Comando

```text
aisdd amend change [descripcion-del-cambio]
```

Si no aportas la descripcion, el skill te la pide. A partir de ahi la IA especifica e implementa: tu describes, ella desarrolla.

## Para que sirve

Estas a mitad (o al final) de un change y aparece algo que sus specs no contemplaban: una version que cambia, un campo mas, un endpoint que devuelve otra cosa, un color.

Re-ejecutar `aisdd implement change` reinterpreta el change **entero** sobre un arbol ya implementado, con riesgo de rehacer trabajo y pisar ficheros. Este skill es la via alternativa: **especifica el delta y ejecuta solo el delta**.

Es el brazo operativo de la "Regla de corte" de la metodologia (ver `aisdd-specs`, `references/implement-change.md`).

## Que hace

1. Resuelve el change objetivo y comprueba que sigue abierto.
2. Te pide que describas la modificacion y te devuelve un espejo de lo entendido antes de tocar nada.
3. Lee los artefactos del change y el codigo **tal como esta hoy**.
4. Toma una **baseline de build y tests antes de escribir una linea**.
5. Escribe el delta: criterios en `spec.md`, decision en `design.md` si aplica, tareas nuevas en `tasks.md`, entrada `Tipo: correccion` en `decisions.md`.
6. Implementa **solo** las tareas nuevas. Nunca ejecuta `openspec instructions apply`.
7. Verifica contra la baseline que no hay regresiones en el radio de impacto del cambio.
8. Escribe la entrada de auditoria en `openspec/audit/`.

## La baseline, y por que importa

El skill **no conoce los cambios manuales** que hayas hecho por tu cuenta, y no intenta adivinarlos. Por eso ejecuta build y tests **antes** de tocar nada y guarda el resultado.

Asi, al terminar, puede separar con evidencia:

- lo que rompio la enmienda -> lo arregla,
- lo que ya estaba roto -> lo reporta sin tocarlo ni atribuirselo.

Sin esa baseline, ninguna afirmacion sobre regresiones seria fiable.

**En roadmaps `multilane` la baseline se complica, y el skill lo asume.** Con varios lanes vivos hay varios devs con el arbol en estados distintos: un test rojo puede venir del trabajo en vuelo de otro lane y no de tu delta. Por eso, en multilane:

- Los **changes afectados se derivan del delta** (cruzando sus rutas y specs con los `paths` de cada lane), en vez de preguntarte cual enmendar — con varios lanes abiertos siempre hay varios changes, y esa eleccion ya la determina el propio cambio.
- Un **delta que cruza lanes es una parada coordinada**: se detienen los lanes hermanos, se toma **una baseline por change** y se enmienda en orden de dependencia. Si los lanes no se pueden detener, el skill no lo ejecuta: remite a una barrera `FB-NN` via `aisdd roadmap`.
- Los lanes **cuya fase aun no esta abierta** no se pueden enmendar (no hay change vivo). El skill **marca** esas fases futuras con `amended_by` para que no arranquen contra un contrato ya desmentido, pero **no re-fasea** el roadmap.

## Lo que NO hace

- **No valida la documentacion AIDD.** Asume que, si el cambio requeria tocar `docs/`, ya lo hiciste. Lo deja escrito en `decisions.md` como asuncion, no como comprobacion.
- **No reconcilia cambios manuales.** El working tree es la verdad.
- **No re-aplica el change** (`openspec instructions apply` esta descartado por diseno).
- **No cierra ni archiva**: eso sigue siendo `aisdd close change`.
- **No amplia el alcance** ni hace mejoras de paso.
- **Se detiene** si la modificacion cambia el objetivo del change (eso es un change nuevo) o si el change ya esta archivado. En ambos casos remite a `aisdd open change`.
- **No re-fasea el roadmap.** Puede marcar fases afectadas como senal para el humano, pero reordenar o re-alcanzar fases es competencia de `aisdd roadmap`.

## Requisitos

- OpenSpec instalado y proyecto ya inicializado (`aisdd init`).
- Un change abierto en `openspec/changes/`.
- Opcional: MCP de Atlassian y seccion `jira:` en `openspec/config.yaml`. Con Jira activo, el comando **no mueve columnas**: solo comenta la enmienda en la Story o sub-tarea.

## Relacion con los demas comandos

| Situacion | Comando |
|-----------|---------|
| Empezar trabajo nuevo | `aisdd open change <slug>` |
| Implementar lo especificado | `aisdd implement change <slug>` |
| **Meter una modificacion en lo que ya esta en marcha** | **`aisdd amend change`** |
| Dar por terminado | `aisdd close change <slug>` |
