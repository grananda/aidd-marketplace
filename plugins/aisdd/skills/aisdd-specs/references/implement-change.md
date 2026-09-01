# `aisdd implement change`

> Referencia del skill `aisdd-specs`. El indice y las reglas comunes estan en `SKILL.md`.

## `aisdd implement change [change-slug]`

> Alias: `native-ai implement change [change-slug]`.

Implementa un cambio OpenSpec con una fase previa de pre-flight para resolver dudas con el usuario antes de tocar codigo.

1. **Resuelve el change objetivo** segun "Resolver el change objetivo (compartido)" (`references/target-change.md`). El argumento es opcional; si no llega y hay varios changes abiertos —lo normal en `waves` y `multilane`— presenta los candidatos con su lane u oleada y deja elegir. No escojas tu.
2. Ejecuta el **pre-flight de dudas** segun la seccion "Pre-flight de dudas (compartido)" (`references/preflight.md`), variante **[IMPLEMENTACION]**.
3. Cuando el pre-flight termine y no queden dudas bloqueantes pendientes, ejecuta:
   ```bash
   openspec instructions apply --change <change-slug>
   ```
4. **Transicion en Jira (opcional)**: si la integracion con Jira esta activa (ver "Integracion con Jira (opcional)" (`references/jira.md`)), al arrancar la implementacion:
   - Localiza en `docs/jira-sync.md` las **HU del change** y resuelve el **modo** de cada una (Story directa vs sub-tarea). Si una HU en modo sub-tarea no tiene aun la sub-tarea de este change (p. ej. se abrio sin Jira), creala ahora como en `open change`; si una HU no tiene Story, omitela con aviso.
   - Resuelve el usuario asignado (cuenta del MCP o `assignee_override`) y mueve a **In Progress** (descubriendo la transicion, sin hardcodear): en modo directo la **Story**; en modo sub-tarea la **sub-tarea y su Story padre**. Asigna al usuario resuelto lo que muevas.
   - Actualiza el estado de cada HU implicada en `docs/jira-sync.md` a `in_progress`.
5. Si durante la implementacion, o en la validacion posterior, surge un cambio que ningun spec habia especificado (incompatibilidad de versiones, ajuste de configuracion, peticion del usuario sobre la marcha), **no escales por defecto**: clasificalo segun "Correcciones durante la implementacion" y resuelvelo en el nivel que le corresponda.
6. **Comprueba el mojibake de lo que has escrito.** Es **obligatorio**, no opcional. Pasa `check_mojibake.py --fix` (ver `references/scripts.md`) sobre los artefactos **documentales** que este comando haya escrito: `tasks.md`, `decisions.md` y, si la integracion con Jira esta activa, `docs/jira-sync.md`. **El codigo fuente no entra**, aunque figure en `output_files` (ver `references/scripts.md`). Los `spec.md` tampoco: este comando los **lee**, no los reescribe. **Va aqui, antes de la entrada de auditoria, porque `audit.py` calcula el hash de cada fichero**: reparar despues dejaria registrado el hash de la version corrupta. Si algun fichero queda con `U+FFFD`, no se puede reparar — hay que regenerarlo; dilo en la verificacion final y no lo escondas.

7. Resume instrucciones aplicadas, ficheros afectados si OpenSpec los indica, decisiones y correcciones grabadas en `decisions.md`, la transicion de Jira aplicada (claves de sub-tarea y Story, columna destino, asignado) si la hubo, y cualquier accion manual pendiente. Di tambien el **resultado de la comprobacion de mojibake**: sin incidencias, ficheros reparados, o ficheros que hay que regenerar por tener `U+FFFD`.
8. **Escribe la entrada de auditoria.** Es obligatoria y **no es opcional para ningun comando salvo `aisdd lane`**. Componla con `audit.py` segun "Scripts del skill" (`references/scripts.md`), con el esquema y las reglas de "Auditoria y trazabilidad" (`references/audit.md`), y `prompt_version` = `<skill_version>:implement-change/preflight`. Incluye en `decisions[]` las decisiones del pre-flight y las entradas `Tipo: correccion` que hayas registrado.

   **Y el bloque `verification`** con lo que dieron el build, los tests y las puertas de calidad que hayas pasado: `{build, tests_run, passed, failed, added, modified, gates[]}`. Este comando **ya los ejecuta**; lo unico nuevo es dejar constancia. Si no ejecutaste alguno, omite ese campo en vez de poner cero: un cero se lee como cero fallos.

   > No pases `first_run_green`: lo deriva el script de que sea el primer intento y de que no falle nada. Es el mejor indicador de si las specs iban bien, y por eso no puede depender de que te acuerdes de marcarlo. Reporta despues su ruta y su `id` en la verificacion final.
9. **Sugiere los proximos pasos.** Cierra diciendo **que hace el usuario ahora**, con el comando ya resuelto y listo para copiar. Sigue "Proximos pasos al terminar un comando" (`references/next-steps.md`), que dice cual toca segun el estado — modo, changes vivos, barreras bloqueadas, lane activo y si hay capa de entrega.

### Correcciones durante la implementacion

Durante `implement change`, o en la validacion posterior, aparecen cambios que nadie habia especificado: una incompatibilidad de versiones, un ajuste de configuracion, un matiz visual que el usuario pide sobre la marcha. **No todos merecen el mismo proceso.** Clasifica antes de actuar:

| Nivel | Situacion | Que haces |
|-------|-----------|-----------|
| 1. Implementacion | El spec es correcto y el codigo no lo cumple | Corriges el codigo. **No** tocas documentacion ni `decisions.md` |
| 2. Decision no documentada | Ningun documento AIDD fijaba ese detalle | Resuelves, registras `Tipo: correccion` en `decisions.md` y **continuas** |
| 3. Contradiccion documental | Un documento sellado afirma lo contrario | Corriges **ese** documento (y solo ese), se re-sella, y despues alineas los artefactos del change |
| 4. Contrato compartido (solo `multilane`) | La correccion toca el contrato sobre el que trabajan otros lanes | **Parada coordinada**: no la apliques por tu cuenta (ver abajo) |

**Regla de corte.** La pregunta no es "cambia el codigo?", sino **"queda algun documento AIDD sellado diciendo algo falso?"**. Si la respuesta es no, es nivel 2 y se resuelve dentro del change.

**Segunda regla de corte, solo en modo `multilane`.** Antes de aplicar la clasificacion anterior, pregunta: **"esto cambia algo sobre lo que otro lane esta trabajando ahora mismo?"** — esquema de datos, contrato de API, eventos, tipos compartidos, o cualquier ruta fuera de los `paths` de tu lane. Si la respuesta es si, **el nivel no importa**: es nivel 4 y no se resuelve dentro del change.

Una correccion es **lane-local** —y entonces sigue la tabla normal— cuando toca solo rutas y specs de tu propio lane. Ese es el caso comun y no cambia nada de lo anterior.

Reglas de aplicacion:

1. **Comprueba antes de clasificar.** Busca el elemento afectado (version, token de estilo, endpoint, nombre) en `docs/` y en los `spec.md` del change antes de decidir el nivel. No asumas que no esta documentado: verificalo y anota que revisaste.
2. **Un nivel 2 no dispara una segunda pasada.** Nunca re-ejecutes `openspec instructions apply` para incorporar una correccion de nivel 2: aplica el cambio directamente sobre el codigo y registra la decision. Re-aplicar un change sobre un arbol ya implementado arriesga rehacer trabajo y pisar ficheros. Si la correccion exige ademas tocar los specs del change (criterios nuevos, tareas nuevas), esa es la via del skill **`aisdd-amend`** (`aisdd amend change`), que especifica e implementa unicamente el delta.
3. **Un nivel 3 corrige un solo documento.** La cadena completa hacia arriba (`cliente-requisitos.md` -> `requisitos.md` -> `propuesta-arquitectura-base.md` -> `arquitectura-base.md`) solo se recorre cuando el cambio nace de una decision del cliente sobre el alcance. Un hallazgo tecnico durante el desarrollo afecta normalmente a `arquitectura-base.md` y a nada mas. Los documentos AIDD los actualiza su skill (`aidd architecture`, `aidd style-guide`...), que ademas re-sella la version con `stamp_doc.py`; no los edites por tu cuenta salvo que el cambio sea de una linea y lo confirmes con el usuario.
4. **No escales por defecto.** Un nivel 2 no se reporta al AI Lead ni se escala al Architect. Escalar cuesta un ciclo completo y solo se justifica en nivel 3.
5. **Registra siempre el nivel 2.** El suelo de trazabilidad es una entrada en `decisions.md`; nunca cero. Sin ella el repositorio acaba contradiciendo a sus propios documentos sin constancia de cuando se torcio.
6. **Si el mismo tipo de correccion se repite** en un change, dilo en el resumen del comando: varias correcciones del mismo tipo son sintoma de specs flojas y material a corregir en el siguiente `open change`.
7. **Si el change ya esta archivado**, no lo reabras: la correccion va en un change nuevo (`aisdd open change [what-you-want-to-build]`).
8. **Nivel 4: parada coordinada (solo `multilane`).** No apliques la correccion. Haz esto:
   - **Detente y dilo.** Nombra que parte del contrato queda desmentida y que lanes dependen de ella (los que tengan changes abiertos, segun `openspec list` y el campo `lane` de sus fases).
   - **Registra** la entrada en `decisions.md` con `Nivel: 4` y `Estado: pendiente de barrera`, sin aplicar el cambio en codigo.
   - **Remite al dueno del contrato** (`roadmap.contract_owner` en `config.yaml`). La decision es suya, no del dev que la encontro.
   - **Avisa de que los lanes hermanos estan trabajando sobre un supuesto ya desmentido.** Este aviso es el valor del nivel 4: sin el, otro dev sigue implementando contra un contrato que ya sabemos falso.
   - La via de resolucion es una **barrera** (`FB-NN`) via `aisdd roadmap`, o un `aisdd amend change` cross-lane si los changes afectados estan vivos y el delta es acotado. Nunca una correccion silenciosa dentro de un lane.

   Un nivel 4 **es** caro — cuesta parar a varias personas. Esa es la razon de que exista: si no fuera caro, el faseado permitiria que los lanes se contradijeran gratis.

   > **En multirepo el nivel 4 existe pero no para a nadie.** No hay contrato compartido en el fuente ni barrera a la que remitir: lo que se desmiente es un **artefacto publicado** que otros repos consumen por version. Registra la entrada igual --con `Estado: pendiente de publicar contrato` en vez de `pendiente de barrera`--, di **que repos consumen esa version** segun `roadmap.lanes`, y deja claro que siguen trabajando contra la version antigua legitimamente: no estan equivocados, estan desactualizados, y la diferencia importa. La resolucion es publicar una version nueva desde el repo que la expone y que cada consumidor la adopte como fase suya.

Formato de la entrada en `openspec/changes/<change>/decisions.md`:

```markdown
## <slug-de-la-correccion>

- **Fecha**: <YYYY-MM-DD>
- **Tipo**: correccion
- **Nivel**: 2 (decision no documentada) | 3 (contradiccion documental) | 4 (contrato compartido)
- **Origen**: usuario | auto-default
- **Contexto**: <donde surgio: criterio X de la validacion, peticion del usuario durante la implementacion>
- **Documentos comprobados**: <ficheros de docs/ y spec.md revisados; que fijaban y que no>
- **Decision**: <lo que se aplica>
- **Justificacion**: <una linea con el motivo>
- **Documentos actualizados**: <nivel 3: fichero corregido y version resellada | nivel 2: ninguno>
- **Lane**: <lane-id>                        # solo en modo multilane
- **Lanes afectados**: <lane-id, ...>        # solo nivel 4: los que dependen del contrato desmentido
- **Estado**: aplicada | pendiente de barrera   # solo nivel 4 usa "pendiente de barrera"
```

El campo **Documentos comprobados** es lo que hace auditable la regla de corte: deja constancia de que el nivel se decidio mirando, no suponiendo.
