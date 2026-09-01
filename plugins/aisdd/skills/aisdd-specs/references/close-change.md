# `aisdd close change`

> Referencia del skill `aisdd-specs`. El indice y las reglas comunes estan en `SKILL.md`.

## `aisdd close change [change-slug]`

> Alias: `native-ai close change [change-slug]`.

Archiva un cambio OpenSpec.

1. **Resuelve el change objetivo** segun "Resolver el change objetivo (compartido)" (`references/target-change.md`). El argumento es opcional. **En modo `multilane`** el filtro por lane activo va primero: si ese lane tiene exactamente un change abierto, usalo sin preguntar. Si tras filtrar sigue habiendo varios, presentalos con su contexto y deja elegir. El lane activo sale de `openspec/.lane`, salvo en topologia **`fraccionado`**, donde se resuelve segun "Resolver el lane activo en `fraccionado`" (`references/parallelism.md`) y ese fichero no se usa. En `externalizado` se usa con normalidad.
2. **Verificacion de independencia (solo si `roadmap.mode` es `multilane`).** Antes de archivar, comprueba que el change respeto las fronteras de su lane. Es el punto donde la independencia deja de ser una promesa del faseado y pasa a estar verificada:
   - **Rutas**: obten los ficheros que el change toco (`git diff --name-only` contra el punto de partida del change, o el equivalente disponible) y comprueba que **todos** caen bajo los `paths` de su lane (`roadmap.lanes[].paths` en `config.yaml`).

     > **En topologia `fraccionado` esta verificacion se cumple sola.** El lane es el repo entero, y un `git diff` aqui no puede devolver ficheros de otro. Dilo en una linea del resumen --verificada por construccion-- y no la presentes como un chequeo que hiciste.
     >
     > **En `externalizado` hay que sacar el diff de cada repo.** El `openspec/` esta fuera de todos ellos, asi que un `git diff` desde aqui **no ve nada** de lo que pasa dentro y la comprobacion pasaria siempre --y una verificacion que dice que si sin haber mirado es peor que no tenerla--. Recorre `roadmap.repos`, ejecuta `git -C <repo.path> diff --name-only` en cada uno y **prefija cada fichero con la ruta del repo** antes de comparar: los `paths` de los lanes ya vienen prefijados, asi que la comparacion es la de siempre. Si algun repo declarado no esta ahi, **dilo y no des la verificacion por buena**.
   - **Specs**: comprueba que ningun `spec.md` modificado pertenece a otro lane.
   - **Si algo cae fuera**, **no archives**. Reporta la lista exacta de ficheros o specs infractores y ofrece las tres salidas posibles: (a) mover ese trabajo al lane que le corresponde, (b) convertirlo en una barrera `FB-NN` si es genuinamente compartido — via `aisdd roadmap`, o (c) que el usuario declare explicitamente que acepta el solape, en cuyo caso registralo como `Nivel: 4` en `decisions.md` antes de archivar. Nunca archives en silencio un change que se salio de su lane: eso convierte el modelo de lanes en decorativo.
   - **Fases barrera** (`barrier: true`): no tienen restriccion de rutas — por definicion tocan superficie compartida. Sáltate esta verificacion para ellas.
   - En modo `atomic` este paso no aplica.
3. Ejecuta:
   ```bash
   openspec archive <change-slug>
   ```
4. **Transicion en Jira (opcional)**: si la integracion con Jira esta activa (ver "Integracion con Jira (opcional)" (`references/jira.md`)):
   - Localiza en `docs/jira-sync.md` las **HU del change** y resuelve el **modo** de cada una (Story directa vs sub-tarea).
   - **Modo directo**: mueve la **Story a Done** (descubriendo la transicion) y actualiza su estado en el registro a `done`.
   - **Modo sub-tarea**: mueve la **sub-tarea** de este change a **Done**; consulta via MCP las sub-tareas de la Story padre y muevela a **Done solo si TODAS estan Done** — si queda alguna abierta, deja la Story en In Progress e indica en el resumen que changes faltan.
5. **Comprueba el mojibake de lo que has escrito.** Es **obligatorio**, no opcional. Pasa `check_mojibake.py --fix` (ver `references/scripts.md`) sobre los artefactos **documentales** que este comando deja escritos: los `spec.md` de `openspec/specs/` que `openspec archive` acaba de promocionar y, si la integracion con Jira esta activa, `docs/jira-sync.md`. Los artefactos del change ya no estan en su ruta original: `archive` los ha movido a `openspec/changes/archive/<slug>/`. **Va aqui, antes de la entrada de auditoria, porque `audit.py` calcula el hash de cada fichero**: reparar despues dejaria registrado el hash de la version corrupta. Si algun fichero queda con `U+FFFD`, no se puede reparar — hay que regenerarlo; dilo en la verificacion final y no lo escondas.
5b. **Solo en topologia `externalizado`: un change que toca varios repos se cierra con varias PR.** Aqui el change **puede** cruzar repos --el `openspec/` es uno solo y no lo impide-- y entonces no se entrega con un merge, se entrega con tantos como repos toque. Archivarlo con dos abiertos deja el roadmap diciendo que la fase esta hecha cuando dos tercios del codigo no estan en ninguna rama principal, y **el informe de estado lo contara como avance real**.

    Antes de archivar, **por cada repo que el change toco**, di si su trabajo esta integrado o cual es el PR pendiente. Si falta alguno, **no archives**: informa de cuales y para. El comando se relanza cuando esten.

    **Si los repos llevan orden entre si** --el consumidor de un contrato no va antes que quien lo publica--, dilo tambien: un merge en el orden equivocado rompe el entorno aunque las N PR existan. El orden sale de las dependencias que declara la arquitectura, no de adivinar.

    > **Esto no aplica en `fraccionado`**, donde un change no puede cruzar repos y siempre se cierra con una sola PR. Es la diferencia practica mas grande entre las dos topologias de varios repos, y conviene tenerla presente al elegir.

6. Verifica que el cambio queda archivado y resume el resultado, incluyendo (si aplico) las Stories/sub-tareas pasadas a Done y las Stories que siguen pendientes. **En modo `multilane`**, indica ademas el lane cerrado, el resultado de la verificacion de independencia y **cual es la siguiente fase de ese lane** — el dev queda libre para abrirla de inmediato, que es el punto de todo el modelo. Di tambien el **resultado de la comprobacion de mojibake**: sin incidencias, ficheros reparados, o ficheros que hay que regenerar por tener `U+FFFD`.
7. **Escribe la entrada de auditoria.** Es obligatoria y **no es opcional para ningun comando salvo `aisdd lane`**. Componla con `audit.py` segun "Scripts del skill" (`references/scripts.md`), con el esquema y las reglas de "Auditoria y trazabilidad" (`references/audit.md`), y `prompt_version` = `<skill_version>:close-change`. Reporta despues su ruta y su `id` en la verificacion final.
8. **Sugiere los proximos pasos.** Cierra diciendo **que hace el usuario ahora**, con el comando ya resuelto y listo para copiar. Sigue "Proximos pasos al terminar un comando" (`references/next-steps.md`), que dice cual toca segun el estado — modo, changes vivos, barreras bloqueadas, lane activo y si hay capa de entrega.
