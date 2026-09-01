# `aisdd lane`

> Referencia del skill `aisdd-specs`. El indice y las reglas comunes estan en `SKILL.md`.

## `aisdd lane [list | switch <lane-id> | status]`

> Alias: `native-ai lane ...`.

Consulta y cambia la **linea de trabajo activa** del dev. Es el equivalente de `git branch` / `git switch` para lanes: no mueve codigo ni toca changes, solo dice sobre que lane trabajan los siguientes `open`/`implement`/`close change`.

**Precondicion**: `roadmap.mode` debe ser `multilane` en `openspec/config.yaml`. En cualquier otro caso **no crees `openspec/.lane`** y explica el porque, que es distinto segun el modo:
- **`waves`**: el proyecto paraleliza por **oleadas**, no por lanes. No hay linea que seleccionar: cada dev toma una fase libre de la oleada en curso. Remite a la seccion "Oleadas" de `docs/roadmap.md` para ver que fases pueden ir a la vez.
- **`atomic`** o sin modo declarado: el proyecto no paraleliza. El modo se decide en `aisdd roadmap`.

**En multirepo (`roadmap.multirepo: true`) el lane no se elige: es el repo.** `roadmap.repo` dice cual, `openspec/.lane` no se usa y **`switch` se rechaza** --explica que se cambia de lane cambiando de repositorio, y nombra el repo destino--. `list` y `status` si funcionan, y son utiles: dicen que lanes hay, cual es este y donde estan los demas.

**Sin subcomando**, equivale a `status`.

### `list`

Lista los lanes de `roadmap.lanes` y, por cada uno:

- `lane-id`, label y perfil asignado
- rutas (`paths`)
- **change abierto**, si lo hay (de `openspec list` cruzado con el campo `lane` de las fases) — es lo que dice si el lane esta ocupado o libre
- fase siguiente pendiente de ese lane
- marca visible del lane activo

Anade al final las **barreras pendientes** (`FB-NN` no archivadas): bloquean a todos los lanes, asi que condicionan lo que cualquier dev puede abrir.

**En multirepo** la lista se lee distinto y hay que decirlo: de los otros lanes **solo conoces lo que el roadmap declara** --su nombre y sus fases--, no si tienen un change abierto, porque eso vive en su `openspec/` y no esta aqui. Marca cual es este repo, di el resto como lo que es --otros repositorios, con su propio registro-- y **no inventes su estado**. Barreras no hay: un roadmap multirepo no las lleva.

### `switch <lane-id>`

0. **Si `roadmap.multirepo` es `true`, rechaza el `switch`** y para. El lane de este `openspec/` es `roadmap.repo` y no se puede cambiar desde aqui: el trabajo del lane pedido se hace en su propio repositorio. Di cual es por su nombre, para que el usuario sepa donde ir. **No escribas `openspec/.lane`**: en este modo nadie lo lee, y dejarlo escrito es una pista falsa para el siguiente que mire.
1. Valida que `<lane-id>` existe en `roadmap.lanes`. Si no, lista los validos y detente. **No lo crees**: los lanes nacen en `aisdd roadmap`, no aqui.
2. Escribe el `lane-id` en `openspec/.lane` (una linea, sin espacios). Crea el fichero si no existe.
3. Comprueba que `.gitignore` contiene `openspec/.lane`; si falta, anadela y dilo (`aisdd init` deberia haberlo hecho).
4. Informa del estado del lane destino: change abierto si lo hay, fase siguiente, y barreras pendientes que lo bloqueen.

**No hay guard aqui.** Cambiar de lane siempre esta permitido, incluso con un change abierto en el lane que dejas: ese change sigue vivo y te espera. El guard vive en `open change`, no en el cambio de puntero — igual que en Git cambiar de rama no cierra tu trabajo. Un dev puede saltar entre lineas de trabajo libremente; lo que no puede es tener dos changes abiertos en la **misma** linea.

### `status`

Informa de:

- lane activo (contenido de `openspec/.lane`, o `roadmap.repo` **en multirepo**), o aviso de que no hay ninguno seleccionado
- change abierto en ese lane, si lo hay, y en que estado
- fase siguiente del lane
- barreras pendientes que lo bloqueen
- si el puntero apunta a un `lane-id` que ya no existe en `config.yaml` (roadmap re-generado): avisa y propon `aisdd lane switch` a uno valido

Si `openspec/.lane` no existe y el modo es `multilane`, no falles: informa de que no hay lane activo y lista los disponibles.

**En multirepo siempre hay lane activo** --lo fija el repo-- asi que ese aviso no aplica, y tampoco el del puntero caduco. Lo que si hay que comprobar es lo contrario: que `roadmap.repo` corresponde a un `lane-id` que existe en `roadmap.lanes`. Si no, el `config.yaml` de este repo se ha quedado atras respecto al roadmap; dilo y remite a `aisdd roadmap`.

### Proximos pasos

Termina diciendo que se puede hacer en el lane activo, con el comando resuelto: `aisdd open change` si esta libre, `aisdd implement`/`close change <change-slug>` si tiene uno vivo, o las barreras que lo bloquean. Ver "Proximos pasos al terminar un comando" (`references/next-steps.md`).
