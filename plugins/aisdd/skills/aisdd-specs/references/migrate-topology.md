# Migrar de topologia

> Referencia del skill `aisdd-specs`. El indice y las reglas comunes estan en `SKILL.md`. El modelo de las tres topologias esta en `references/parallelism.md`.

Se entra aqui desde `aisdd roadmap` cuando el usuario pide cambiar donde vive el registro --"quiero sacar `openspec/` del repo", "vamos a partir esto en varios repos", "migrar a externalizado"-- o cuando `roadmap.topology` no cuadra con lo que hay en disco.

**Esto lo ejecutas tu**, no se lo dictas al usuario. Lo unico que no haces esta en "Lo que no haces nunca", y es corto.

## 1. Resuelve el destino con dos preguntas

No preguntes por nombres de topologia: pregunta por las dos cosas que el usuario si sabe. Usa `AskUserQuestion` si la plataforma lo soporta.

1. **¿En cuantos repositorios vive el codigo?** Uno / varios.
2. **¿Donde vive el registro** --`openspec/` y `docs/`--? Dentro del repo de codigo / **en un repositorio aparte**.

| Codigo | Registro dentro | Registro aparte |
|---|---|---|
| **1 repo** | `mono` | `externalizado` |
| **N repos** | `fraccionado` | `externalizado` |

Di el nombre resultante y **que implica**, en dos lineas, antes de tocar nada. Si el destino coincide con el origen, dilo y para: no hay migracion.

**Y pregunta el porque si no lo ha dicho.** No por curiosidad: si la razon es que los artefactos no deben verse en el repo de codigo, el paso 5 --la historia-- deja de ser opcional, y es el unico paso que no se puede deshacer.

## 2. Haz el inventario antes de mover nada

Enumeralo en pantalla y **espera confirmacion**. Es lo ultimo que el usuario ve antes de que empieces:

- Que `openspec/` hay y donde, con cuantos changes archivados y cuantas entradas de auditoria cada uno.
- Que `docs/` hay y donde.
- Si hay changes **abiertos**. Con un change vivo, **no migres**: cierralo o pide al usuario que lo cierre. Mover el registro con trabajo en vuelo deja artefactos a medio camino entre dos sitios.
- Donde esta cada repo de codigo y si el layout de destino es alcanzable.

## 3. Ejecuta la migracion que toque

### A `externalizado`, desde `mono` o desde `fraccionado`

Es el caso mas pedido, y el que motiva la topologia: sacar el registro del repo que ve el cliente.

1. **El repositorio de gobierno.** Si el usuario no lo tiene, creale el directorio y `git init` --confirma antes: es un repo nuevo--. Los repos de codigo tienen que quedar **dentro de su arbol**; si ya estan clonados en otro sitio, **muevelos** en vez de volver a clonar: conservan sus ramas, sus stash y su remote.

   ```
   proyecto/            <- repo de gobierno
     openspec/  docs/
     repo-app/          <- el de codigo, movido aqui
   ```

2. **Elige el `openspec/` bueno.** Desde `mono` no hay que elegir. Desde `fraccionado` hay N y **no se fusionan sin mas**: cada uno tiene su archivo y su auditoria, y concatenarlos a ciegas duplica lo que se copio al partir. Las **fases sin lane** estan repetidas en todos: quedate con una copia. De los demas, **anade solo los changes archivados que no esten** en el elegido, y di cuantos moviste de cada uno.

3. **Saca las carpetas del repo de codigo sin borrarlas del disco:**

   ```bash
   git -C repo-app rm -r --cached openspec docs
   mv repo-app/openspec repo-app/docs .
   ```

   `--cached` las desversiona pero las deja en el disco, que es lo que permite el `mv` de despues. Commitea ese borrado en el repo de codigo y dilo: **es un commit en el repo del cliente**.

4. **Los dos ficheros de exclusion, que no son el mismo y no van en el mismo sitio:**

   - **`.gitignore` del repo de gobierno**, con la ruta de cada repo de codigo. Sin el, un `git add -A` se traga el codigo del cliente entero.
   - **`.git/info/exclude` del repo de codigo**, con `docs/` y `openspec/`. **No su `.gitignore`**: `info/exclude` es local a cada clon y **no se versiona**, asi que el hook de actividad puede seguir escribiendo `docs/aidd-activity.md` sin que aparezca nada en el arbol ni una linea que alguien se pregunte por que esta ahi.

5. **La historia, que es el paso que no se deshace.** `git rm --cached` quita las carpetas de ahora en adelante; **siguen en los commits anteriores** y un `git log --all -- docs/` las enseña enteras. Lo mismo con los trailers de co-autoria en los mensajes.

   **Presenta las dos opciones y que elija el usuario. No reescribas historia por tu cuenta:**

   | | Consigue | Cuesta |
   |---|---|---|
   | Dejarla | Nada que romper | Las carpetas y los trailers **siguen siendo visibles** en la historia |
   | Reescribirla (`git filter-repo`) | Desaparecen del pasado | Cambia **todos** los hashes: force-push, todos vuelven a clonar, y **las copias que ya existan fuera no se alcanzan** |

   Si eligen reescribir, **dales el comando y que lo ejecuten ellos**. Es irreversible y afecta a un repo compartido.

6. **`openspec/config.yaml`**: `topology: externalizado` y `roadmap.repos` con el `id` y el `path` de cada repo de codigo, relativo al de gobierno.

7. **Los `paths` de los lanes** pasan a ir prefijados con la ruta de su repo (`repo-app/src/`). Antes eran relativos a la raiz de su repo.

8. **Los demas rastros del repo de codigo**: `AGENTS.md`, `CLAUDE.md`, `.claude/`. Enumeralos y aplica lo que el usuario decidio en el paso 5.

9. **Primer commit y push del repo de gobierno.** Si no tiene remote, dilo: sin el no hay copia ni lo ve nadie mas, y la auditoria vuelve a estar en un solo disco.

### Desde `externalizado` a `mono` o `fraccionado`

Es el camino de vuelta y tiene un caso incomodo que hay que decir **antes** de empezar: **los changes archivados que tocaron varios repos no tienen un sitio unico**. Dejalos en el repo del lane que los abrio y registra la decision.

El resto es lo mismo del reves: copiar `docs/` a cada repo, repartir el `openspec/` por lane, quitar las rutas del `.gitignore` del gobierno y las lineas de `.git/info/exclude`, y actualizar `config.yaml`.

**No borres el repo de gobierno.** Aunque ya no se use, tiene la historia de la auditoria de todo el periodo anterior. Dilo y dejalo estar.

### De `mono` a `fraccionado`

Es partir un repo en varios y esta descrito aparte, en "Caso aparte: pasar de un repositorio a varios" (`references/roadmap.md`): el `openspec/` se **replica** en los N repos y las fases anteriores a la migracion se reconocen porque **no llevan `lane`**.

## 4. Cierra

- **Registra la migracion** en `docs/roadmap.md`: fecha, topologia anterior, nueva, motivo, y que se decidio sobre la historia. Sin esa linea, seis meses despues nadie sabe por que el registro esta donde esta.
- **Comprueba que funciona**: desde un repo de codigo, resuelve la raiz subiendo y di que repo has detectado. Si no encuentra `openspec/config.yaml` subiendo, el layout esta mal y **el resto no va a funcionar**.
- **Di donde se ejecuta cada comando a partir de ahora**, porque cambia: `init` y `roadmap` en la raiz de gobierno; `open`, `implement`, `amend` y `close` desde el repo de codigo, sin cambiar de carpeta.
- **Escribe la entrada de auditoria** de esta ejecucion de `roadmap` como cualquier otra.

## Lo que no haces nunca

- **Reescribir la historia de un repo.** Das el comando, explicas que rompe, y lo ejecuta el usuario.
- **Borrar el `openspec/` de origen antes de que el destino este completo y subido.** Dos registros vivos a la vez es malo; ninguno es peor.
- **Migrar con un change abierto.**
- **Tocar el `.gitignore` del repo de codigo** para esconder cosas: para eso esta `.git/info/exclude`, que no se versiona. Si hace falta tocar el versionado, preguntalo: es un fichero del repo del cliente.
