---
name: aisdd-specs
description: AISDD (AI Spec-Driven Development) — gestiona especificaciones sobre OpenSpec mediante los comandos `aisdd init`, `aisdd roadmap`, `aisdd open change`, `aisdd implement change`, `aisdd close change`, `aisdd lane`, `aisdd prototype-ux` y `aisdd uml`, con los alias legacy equivalentes de prefijo `native-ai ...`. Coordina la documentacion de diseno que produce AIDD y la capa de entrega de AIBA (planificacion-proyecto, sprint-plan, plan-revision-hu), genera roadmaps, y delega diagramas en booster-uml y prototipos en booster-ux. Ofrece tres modos de faseado —`atomic`, `waves` (oleadas) y `multilane` (lanes)— que se eligen en el pre-flight de `aisdd roadmap` y condicionan a los demas comandos: primero se recoge la preferencia del usuario y despues un **pre-flight de optimizacion** calcula el calendario de cada modo y cada numero de developers y presenta los caminos enfrentados en un HTML, con sus barreras y sus tiempos, para decidir con la cifra delante. `open change` e `implement change` comparten un pre-flight de dudas configurable por proyecto. **Todos** los comandos escriben una entrada de auditoria estructurada en `openspec/audit/` —es obligatoria, y la unica excepcion es `aisdd lane`, que solo mueve un puntero local—; la integracion con Jira es opcional. Todos los comandos cierran sugiriendo el **proximo paso** con el comando ya resuelto, encadenando con la capa de entrega de AIBA cuando toca. Este `SKILL.md` es un **indice** con las reglas comunes y una tabla de enrutado; el detalle de cada comando vive en `references/*.md` y se lee **bajo demanda**. Usar cuando el usuario invoque `aisdd ...` o `native-ai ...`, o pida trabajar con especificaciones OpenSpec/Native AI.
metadata:
  author: NTT DATA Spain GDN-e
  version: "3.4.0"
---

# aisdd-specs (AI Spec-Driven Development)

Usa este skill cuando el usuario pida trabajar con especificaciones AISDD / OpenSpec, o cuando invoque cualquiera de estos comandos (prefijo primario **`aisdd`**; el prefijo **`native-ai`** se mantiene como **alias legacy** equivalente):

- `aisdd init`            (alias: `native-ai init`)
- `aisdd roadmap`         (alias: `native-ai roadmap`)
- `aisdd open change [what-you-want-to-build]`       (alias: `native-ai open change ...`)
- `aisdd implement change [change-slug]`  (alias: `native-ai implement change ...`)
- `aisdd close change [change-slug]`      (alias: `native-ai close change ...`)
- `aisdd lane [list | switch <lane-id> | status]`    (alias: `native-ai lane ...`)
- `aisdd prototype-ux [change-slug]`      (alias: `native-ai prototype-ux ...`)
- `aisdd uml [change-slug]`               (alias: `native-ai uml ...`)

> **Alias legacy.** `aisdd <cmd>` y `native-ai <cmd>` son **equivalentes**: ejecutan exactamente el mismo flujo. `aisdd` es el prefijo primario (consistente con `aidd`/`aiad`); `native-ai` se conserva para no romper `AGENTS.md`, roadmaps y referencias de proyectos ya iniciados. En este documento el prefijo `aisdd` es el canonico; donde leas un comando, el equivalente `native-ai` es igual de valido.

Responde y documenta en espanol siempre que sea posible. Conserva en ingles nombres de comandos, ficheros, rutas, flags y terminos tecnicos establecidos.

## Como usar este documento

Este `SKILL.md` es el **indice**: reglas comunes y que leer para cada cosa. El detalle de cada comando vive en `references/`, y **se lee bajo demanda**: no cargues un fichero que no necesitas para el comando en curso.

| Vas a... | Lee |
|---|---|
| Inicializar el proyecto (`aisdd init`), tambien sobre un repo ya en marcha | `references/init.md` |
| Fasear el desarrollo (`aisdd roadmap`), elegir modo y numero de fases | `references/roadmap.md` |
| Entender los tres modos de paralelismo antes de elegir | `references/parallelism.md` |
| Comparar caminos de faseado y calcular el optimo (`aisdd roadmap`, paso 11) | `references/optimizer.md` |
| Abrir un change (`aisdd open change`) | `references/open-change.md` |
| Implementar un change (`aisdd implement change`) y clasificar correcciones | `references/implement-change.md` |
| Cerrar un change (`aisdd close change`) | `references/close-change.md` |
| Cambiar de linea de trabajo (`aisdd lane`) | `references/lane.md` |
| Resolver el change objetivo cuando el argumento no llega | `references/target-change.md` |
| Resolver dudas antes de generar specs o de implementar | `references/preflight.md` |
| Prototipos UX (`aisdd prototype-ux`) | `references/prototype-ux.md` |
| Diagramas UML (`aisdd uml`) | `references/uml.md` |
| Sincronizar con Jira | `references/jira.md` |
| Escribir la entrada de auditoria | `references/audit.md` |
| Ejecutar los scripts del skill | `references/scripts.md` |
| Cerrar diciendo que hace el usuario ahora | `references/next-steps.md` |

**Dependencias frecuentes entre ficheros**, para no leer de mas ni de menos:

- `open-change.md` e `implement-change.md` **requieren** `preflight.md`: el pre-flight es obligatorio en ambos y esta descrito una sola vez.
- `open/implement/close-change.md` y `uml.md` **requieren** `target-change.md` cuando el comando llega sin argumento: los cuatro lo resuelven igual, y con varios changes abiertos la desambiguacion es obligatoria.
- `roadmap.md` **requiere** `parallelism.md` si el proyecto tiene mas de un developer.
- `open/implement/close-change.md` **requieren** `parallelism.md` solo si `roadmap.mode` es `waves` o `multilane`.
- **Todos los comandos salvo `aisdd lane` requieren `audit.md`**: la entrada de auditoria es obligatoria y cada ficha la ordena en su paso final, con el `prompt_version` que le corresponde. Requieren ademas `scripts.md`, porque `audit.py` es la via preferente para componerla.

## Reglas generales

- Trabaja desde la raiz del proyecto del usuario.
- **Anota la hora UTC al empezar el comando**, antes de leer nada, y pasala como `started_at` en la entrada de auditoria. Es lo unico que permite saber cuanto duro: con solo la marca de fin, el hueco hasta la entrada anterior mide la comida de por medio y no el trabajo. Un comando que empieza a las 18:50 y acaba a las 09:10 duro minutos, no catorce horas.
- Antes de ejecutar comandos, confirma el estado relevante con comandos no destructivos (`Get-Command`, `npm list -g`, `openspec list`, busqueda de ficheros).
- Si un argumento opcional no llega, intenta resolverlo desde OpenSpec. Pregunta solo si hay ambiguedad real.
- No inventes cambios: usa el contexto del usuario y los artefactos OpenSpec existentes.
- Si necesitas usar otro skill, invocalo por nombre y sigue sus instrucciones.
- Verifica que los comandos terminan correctamente y resume rutas/artefactos generados.
- Si un flujo depende del modelo usado, adapta la estrategia al presupuesto de contexto. Si no conoces el modelo real o su ventana, usa una estrategia conservadora de contexto medio-bajo.

## Dependencias de skills

`booster-ux` y `booster-uml` viven en el plugin **`boosters`** de este mismo marketplace. **No los busques por directorio**: Claude Code resuelve los skills por nombre entre los plugins instalados, e invocarlos es toda la comprobacion que hace falta — si el plugin no esta, la invocacion no resuelve.

Si falta alguno, avisa con el comando que lo arregla:

```
No encuentro el skill booster-ux (plugin `boosters`). Instalalo con:
  /plugin install boosters@aidd-sdd
```

> Las rutas `.agents/skills/…` y las globales de `%USERPROFILE%` son del empaquetado anterior al marketplace. En una instalacion por plugin no existen, y mandar a alguien a crearlas no arregla nada.

La ausencia de un skill no debe bloquear `init`, `implement` o `close`; si bloquea diagramas o prototipos, informa y deja los comandos OpenSpec completados.

## Verificacion final

Al terminar cualquier comando, informa:

- comando Native AI solicitado
- comando OpenSpec ejecutado, si aplica
- cambio objetivo, si aplica
- artefactos creados o actualizados (incluye `decisions.md` si hubo pre-flight)
- decisiones tomadas en el pre-flight y cuales quedan `pendientes`, si aplica
- entrada de auditoria escrita: ruta del fichero `openspec/audit/YYYY-MM.jsonl`, `id` de la entrada y su `status` (`ok`, `partial` o `aborted`). **Un comando que se detuvo tambien deja entrada**, con `status: aborted`: la ausencia de entrada nunca es un resultado valido, salvo en `aisdd lane`
- skills auxiliares usados o pendientes de instalar
- errores o tareas manuales pendientes
- documentación faltante (en caso de que aplique)
- **en modo `multilane`**: lane activo, resultado de la verificacion de independencia si hubo cierre, y barreras pendientes que bloqueen al resto de lanes
- **en `aisdd roadmap`**: la ruta del HTML comparativo, el modo y los devs elegidos, y —si se descarto el optimo— cuantos dias cuesta esa decision
- **proximos pasos**: que hace el usuario ahora, con el comando ya resuelto y listo para copiar. Maximo tres, segun el estado real del proyecto — ver "Proximos pasos al terminar un comando" (`references/next-steps.md`). AISDD es un bucle, y quien lo recorre necesita saber por donde sigue
- resultado de `check_mojibake.py` sobre los artefactos escritos. **Es un paso obligatorio del comando**, no una opcion: di si no hubo incidencias, que ficheros se repararon, y **cuales quedan con mojibake sin reparar** (los que tengan `U+FFFD` hay que regenerarlos). Tres comandos quedan fuera y no es un olvido: `prototype-ux` y `uml` solo delegan en un booster, que ya verifica su propia salida, y `aisdd lane` no escribe mas que el puntero local `openspec/.lane`. **El codigo fuente tampoco se comprueba** — ver "Scripts del skill" (`references/scripts.md`)
