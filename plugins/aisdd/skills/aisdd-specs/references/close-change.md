# `aisdd close change`

> Referencia del skill `aisdd-specs`. El indice y las reglas comunes estan en `SKILL.md`.

## `aisdd close change [change-slug]`

> Alias: `native-ai close change [change-slug]`.

Archiva un cambio OpenSpec.

1. **Resuelve el change objetivo** segun "Resolver el change objetivo (compartido)" (`references/target-change.md`). El argumento es opcional. **En modo `multilane`** el filtro por lane activo va primero: si ese lane tiene exactamente un change abierto, usalo sin preguntar. Si tras filtrar sigue habiendo varios, presentalos con su contexto y deja elegir. El lane activo sale de `openspec/.lane`, salvo **en multirepo**, donde es `roadmap.repo` y ese fichero no se usa.
2. **Verificacion de independencia (solo si `roadmap.mode` es `multilane`).** Antes de archivar, comprueba que el change respeto las fronteras de su lane. Es el punto donde la independencia deja de ser una promesa del faseado y pasa a estar verificada:
   - **Rutas**: obten los ficheros que el change toco (`git diff --name-only` contra el punto de partida del change, o el equivalente disponible) y comprueba que **todos** caen bajo los `paths` de su lane (`roadmap.lanes[].paths` en `config.yaml`).

     > **En multirepo esta verificacion se cumple sola.** El lane es el repo entero, y un `git diff` aqui no puede devolver ficheros de otro. Dilo en una linea del resumen --verificada por construccion-- y no la presentes como un chequeo que hiciste.
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
6. Verifica que el cambio queda archivado y resume el resultado, incluyendo (si aplico) las Stories/sub-tareas pasadas a Done y las Stories que siguen pendientes. **En modo `multilane`**, indica ademas el lane cerrado, el resultado de la verificacion de independencia y **cual es la siguiente fase de ese lane** — el dev queda libre para abrirla de inmediato, que es el punto de todo el modelo. Di tambien el **resultado de la comprobacion de mojibake**: sin incidencias, ficheros reparados, o ficheros que hay que regenerar por tener `U+FFFD`.
7. **Escribe la entrada de auditoria.** Es obligatoria y **no es opcional para ningun comando salvo `aisdd lane`**. Componla con `audit.py` segun "Scripts del skill" (`references/scripts.md`), con el esquema y las reglas de "Auditoria y trazabilidad" (`references/audit.md`), y `prompt_version` = `<skill_version>:close-change`. Reporta despues su ruta y su `id` en la verificacion final.
8. **Sugiere los proximos pasos.** Cierra diciendo **que hace el usuario ahora**, con el comando ya resuelto y listo para copiar. Sigue "Proximos pasos al terminar un comando" (`references/next-steps.md`), que dice cual toca segun el estado — modo, changes vivos, barreras bloqueadas, lane activo y si hay capa de entrega.
