# El repositorio de gobierno (topologia `externalizado`)

> Referencia del skill `aisdd-specs`. El indice y las reglas comunes estan en `SKILL.md`.

Aplica solo cuando `roadmap.topology` es `externalizado`: `openspec/` y `docs/` viven en un repositorio git propio, aparte de los repos de codigo. El modelo esta en "Las tres topologias" (`references/parallelism.md`); aqui esta como se opera.

## El layout, que es obligatorio

Los repos de codigo van **clonados dentro del arbol del repo de gobierno**, e ignorados por el:

```
proyecto/                 <- repo de gobierno (su .git)
  openspec/
  docs/
  .gitignore              <- contiene repo-front/ y repo-bff/
  repo-front/             <- repo de codigo (su propio .git)
  repo-bff/
```

**No es una convencion, es lo que hace que todo lo demas funcione.** El CLI de `openspec` --`list`, `archive`, `instructions apply`-- no admite ninguna opcion de raiz: espera `openspec/` en el directorio desde el que corre. Con este arbol, ese directorio existe siempre subiendo, y una ruta como `repo-front/src/x.ts` cae donde tiene que caer.

Los `path` de `roadmap.repos[]` van relativos a la raiz de gobierno, que es exactamente el nombre de esas subcarpetas.

> **El `.gitignore` no es opcional.** Sin el, un `git add -A` en el repo de gobierno se traga los repos de codigo enteros. `aisdd init` lo escribe; si al ejecutar un comando ves que falta una entrada, **anadela y dilo**.

## Donde se ejecuta cada comando

**Un dev nunca cambia de carpeta.** Trabaja en su repo de codigo y ahi ejecuta todo. Que el `openspec/` este mas arriba es problema del skill, no suyo.

| Comando | Desde donde | Quien |
|---|---|---|
| `aisdd init`, `aisdd roadmap` | La **raiz de gobierno** | Lead / Architect |
| `aisdd open change` | El **repo de codigo** | Dev |
| `aisdd implement change` | El **repo de codigo** | Dev |
| `aisdd amend change` | El **repo de codigo** | Dev |
| `aisdd close change` | El **repo de codigo** | Dev |

`init` y `roadmap` van en la raiz por dos motivos distintos: `init` porque **crea** la estructura y todavia no hay nada que encontrar subiendo, y `roadmap` porque fasea el proyecto entero y no tiene un repo de referencia.

### Como se resuelve la raiz

Desde el directorio actual, **sube hasta encontrar un `openspec/config.yaml`**. El primero que aparezca es la raiz de gobierno. Con el layout de arriba es deterministico y no hace falta configurar ninguna ruta ni mantener ninguna referencia.

**Si no aparece ninguno**, no supongas donde esta: detente y dilo. Puede ser que el repo de codigo no este dentro del arbol de gobierno --el layout esta mal montado-- o que el usuario este en otro sitio.

### Como se sabe en que repo estas

De la **primera carpeta que dejaste atras al subir**, cruzada con los `path` de `roadmap.repos[]`. Si estas en `proyecto/repo-front/src/`, subes hasta `proyecto/` y la carpeta es `repo-front/`, que es el `path` del repo `front`.

Eso es lo que hace que `implement change` sepa donde escribe y `close change` sepa que diff mirar, **sin preguntar**. Si la carpeta no coincide con ningun `path` declarado, preguntalo con la lista; no lo deduzcas por parecido.

### Que se ejecuta donde

- **El CLI de `openspec`**, siempre desde la raiz: `cd <raiz> && openspec archive <slug>`. Nunca desde el repo de codigo, donde no encuentra su carpeta.
- **Los artefactos de specs y la auditoria**, por ruta absoluta bajo la raiz. No hace falta moverse.
- **Build, tests y linters**, en el repo de codigo, que es donde esta el proyecto y donde estas tu.
- **Los commits del repo de gobierno**, con `git -C <raiz>`. Los del codigo, donde estas.

## Ritmo de commit y push

**Por comando, no por sesion ni por dia.** Todos los comandos de AISDD escriben una entrada de auditoria al terminar, y una entrada que solo existe en un portatil no es un registro: no la ve nadie mas y desaparece con el disco.

Cada comando cierra con **commit y push del repo de gobierno**, como paso posterior a escribir la auditoria:

| Comando | Que entra en el commit |
|---|---|
| `aisdd init` | `openspec/config.yaml`, specs base si se sembraron, y la auditoria |
| `aisdd roadmap` | `docs/roadmap.md`, `docs/prompts-roadmap-native-ai.md`, `config.yaml` y la auditoria |
| `aisdd open change` | Los artefactos del change y la auditoria |
| `aisdd implement change` | `tasks.md` y `decisions.md` actualizados, y la auditoria |
| `aisdd amend change` | El delta aplicado y la auditoria |
| `aisdd close change` | El movimiento a `archive/`, las specs promocionadas y la auditoria |

**Antes de push, `git pull --rebase`.** El fichero por escritor y el `merge=union` de `.gitattributes` ya evitan el conflicto normal, pero rebasar primero evita el rechazo por historia divergente cuando otro dev acaba de subir lo suyo.

**Si el push falla, dilo y no lo escondas.** El trabajo esta commiteado en local y no se pierde, pero **la auditoria todavia no es un registro compartido**. Es informacion que el usuario necesita ahora, no en el siguiente comando.

**Confirma antes del primer push de la sesion.** Subir a un remoto es una accion hacia fuera; una vez el usuario dice que si, los siguientes van solos.

### Lo que no se debe hacer

- **Juntar el dia en un commit al cerrar.** Los timestamps van dentro de las entradas, asi que la fecha no se pierde; lo que se pierde es poder volver a hace dos comandos en vez de a ayer.
- **Commitear sin push.** Es el caso peor de los dos: parece hecho y no lo esta.

## El orden respecto al repo de codigo

Son dos historias distintas y su orden relativo es lo que hace que el roadmap diga la verdad:

1. **`open change` -> commit y push del repo de gobierno.** La especificacion existe antes que el codigo que especifica.
2. Se implementa. El codigo va a su repo, por su PR.
3. **`close change` va despues de que esa PR este mergeada.** Nunca antes.

Archivar un change con su PR sin mergear deja el roadmap diciendo que la fase esta hecha cuando el codigo no esta en ninguna rama principal, y **el informe de estado lo cuenta como avance real**. El paso de verificacion de `close change` ya lo comprueba; el orden de los commits es lo que lo acompana.

## El campo `repo` en la auditoria

La auditoria es **una sola** para todos los repos de codigo. Cada entrada lleva `repo` con el `id` del repo sobre el que se trabajo, segun la tabla de `roadmap.repos`.

No se parte el directorio por repo: el fichero ya se separa por escritor y mes (`audit/YYYY-MM/<quien>.jsonl`), y con un dev por repo eso ya separa por repo de hecho. Un nivel mas de carpeta no evitaria ninguna colision que no este evitada, y obligaria a manejar tres disposiciones distintas al leer.

Con un solo repo de codigo, `repo` lleva su unico `id` igualmente: asi la entrada se lee igual venga de donde venga.

## Rastros en el repo de codigo

Si la razon de externalizar es que **los artefactos de especificacion no deben aparecer en el repo de codigo**, esas dos carpetas no son lo unico que hay que mirar. Comprueba en cada repo de codigo, y dilo en el resumen de `aisdd init`:

- **`AGENTS.md` y `CLAUDE.md`** en la raiz.
- **`.claude/`**, con sus settings y hooks.
- **`docs/aidd-activity.md`**, que el hook escribe **dentro del repo de codigo**: es donde trabaja el dev y el hook anota relativo a ahi. Y ahi hace falta, porque es la unica fuente de `aiba metrics`.

  La salida limpia es **`.git/info/exclude`** del repo de codigo, no su `.gitignore`: excluye igual, es local a cada clon y **no se versiona**, asi que el fichero existe para el hook y no aparece ni en el arbol del cliente ni en un `.gitignore` que alguien se pregunte por que tiene esa linea. Proponlo; la decision es del usuario.
- **Los mensajes de commit**, si llevan trailers de co-autoria. Ese rastro esta en la historia y **no se quita sin reescribirla**: dilo, no lo arregles tu.

**Enumera lo que encuentres y deja decidir.** No borres nada ni anadas nada a `.gitignore` por tu cuenta: son ficheros del repo del cliente y esa decision no es tuya.

> **Y una comprobacion que si te corresponde**: si el repo de gobierno **no** es un repositorio git, detente y dilo. Es la condicion de la que dependen la trazabilidad de la auditoria y la recuperacion de cualquier estado anterior; sin ella, esta topologia no se sostiene.
