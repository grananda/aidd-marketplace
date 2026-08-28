# Scripts del skill

> Referencia del skill `aisdd-specs`. El indice y las reglas comunes estan en `SKILL.md`.

## Scripts del skill

El skill trae tres scripts en `${CLAUDE_PLUGIN_ROOT}/skills/aisdd-specs/scripts/`. Cubren las tres mecanicas que antes eran **prosa que el agente debia ejecutar bien cada vez**: componer la entrada de auditoria, reemplazar un bloque delimitado y detectar mojibake. Las tres son exactas o no son — y una sola equivocacion no deja rastro de cuando ocurrio.

| Script | Sustituye a | Invocado desde |
|---|---|---|
| `audit.py` | Composicion manual de la entrada JSONL, hashes y purga | Todos los comandos que escriben auditoria |
| `agents_block.py` | Reemplazo manual de bloques en `AGENTS.md` | `aisdd init` (bloque `commands`), `aisdd roadmap` (bloque `roadmap`) |
| `check_mojibake.py` | Nada (capacidad nueva) | **Obligatorio** en `init`, `roadmap` y `open`/`implement`/`close change`, y en `aisdd amend change`. Justo **antes** de la entrada de auditoria |

Solo requieren **Python 3 y biblioteca estandar**: sin dependencias que instalar.

**Degradacion.** Si `python3` no esta disponible o el script falla, **no bloquees el comando**: haz el trabajo segun la prosa de las secciones correspondientes —que se mantiene como especificacion— y dilo en el resumen. Los scripts son la via preferente por ser deterministas, no un requisito duro. La especificacion es el documento; el script es su implementacion.

### `audit.py`

Recibe por stdin (o `--entry <fichero>`) el JSON con lo que **solo el agente sabe** y el script rellena `id`, `timestamp`, los hashes y la purga:

```bash
echo '<json>' | python3 "${CLAUDE_PLUGIN_ROOT}/skills/aisdd-specs/scripts/audit.py" --root <projectRoot>
```

- `input_files` y `output_files` se pasan como **listas de rutas relativas**; el script las convierte en `[{path, sha256}]` y calcula los agregados con la formula de "Calculo de hashes" (`references/audit.md`).
- Una ruta que no exista **no aborta**: se omite y se reporta en `warnings`. Perder la entrada entera por una ruta mal escrita es peor que registrarla incompleta y avisar. **Revisa los `warnings` y menciona en el resumen los ficheros omitidos.**
- Devuelve por stdout `{audit_file, id, purged, warnings}`. Usa ese `id` y esa ruta en la verificacion final.

### `agents_block.py`

```bash
echo '<contenido sin marcadores>' | python3 "${CLAUDE_PLUGIN_ROOT}/skills/aisdd-specs/scripts/agents_block.py" <marker> --root <projectRoot>
```

`<marker>` es `commands` o `roadmap`. Crea `AGENTS.md` si falta, reemplaza el bloque si existe y lo anade al final si no, **sin tocar el resto del fichero ni el otro bloque**. Migra automaticamente un bloque legacy `native-ai-specs <marker>` al nombre actual. Devuelve `{file, action, marker}` con `action` = `created` | `replaced` | `appended` | `migrated`.

### `check_mojibake.py`

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/aisdd-specs/scripts/check_mojibake.py" [--fix] <fichero...>
```

Detecta secuencias de UTF-8 mal interpretado como Latin-1/CP1252. Importa porque los artefactos son texto en espanol con tildes, los escribe el agente y los leen despues otras herramientas: un `decisions.md` donde cada `o` acentuada se ha convertido en el par `U+00C3 U+00B3` no es un defecto estetico, porque los comandos siguientes se alimentan de el. (Se cita por codepoint y no por el caracter: escribir la secuencia literal en un `.md` hace fallar la comprobacion de la propia CI, que es la misma razon por la que no se pasa sobre codigo fuente.)

**Cuando.** Justo antes de escribir la entrada de auditoria. El orden importa: `audit.py` calcula el hash de cada fichero, asi que reparar despues registraria el hash de la version corrupta.

**Sobre que, y sobre que no.** Solo sobre los **artefactos documentales** que el comando escribe: los `.md` del change y de `docs/`, `openspec/config.yaml`, `AGENTS.md` y el HTML de diagramas. Cada ficha de `references/` enumera los suyos.

**Nunca sobre codigo fuente**, aunque este en los `output_files` de la auditoria. Hay ficheros que llevan esas secuencias **a proposito**: el propio `check_mojibake.py` y el `render_docs_html.py` de `booster-docs` las tienen en sus tablas de deteccion, y ambos dan positivo si te los pasas por encima. Con `--fix` no solo darias un falso positivo: reescribirias la herramienta. Por eso la CI del repo tambien se limita a `*.md`.

**Sin el script.** Si `python3` no esta disponible, la degradacion no es saltarse el paso: busca a mano en esos mismos ficheros las secuencias `U+00C3`, `U+00C2`, `U+00E2 U+20AC` y `U+FFFD` —la misma lista que usa `booster-uml`—, corrige lo que puedas y di en el resumen que la comprobacion fue manual.

Codigo de salida `1` si queda mojibake. Con `--fix` repara in situ, token a token y **solo cuando el resultado mejora**. El caracter de reemplazo `U+FFFD` se detecta pero **no se puede reparar**: ahi la informacion original ya se perdio, y hay que regenerar el fichero.
