# `aisdd prototype-ux`

> Referencia del skill `aisdd-specs`. El indice y las reglas comunes estan en `SKILL.md`.

## `aisdd prototype-ux [change-slug]`

> Alias: `native-ai prototype-ux [change-slug]`.

Genera prototipos UX.

- Si llega `<change-slug>`, identifica en ese change las pantallas nuevas o modificadas revisando `design.md`, `proposal.md` y `spec.md`.
- Lanza el skill `booster-ux` una vez por cada pantalla nueva identificada.
- Si no llega argumento, lanza directamente `booster-ux` y sigue su flujo de preguntas.
- Si no existe `booster-ux`, avisa donde debe instalarse y no generes prototipos por otro camino salvo peticion expresa del usuario.
- **Escribe la entrada de auditoria.** Es obligatoria y **no es opcional para ningun comando salvo `aisdd lane`**. Componla con `audit.py` segun "Scripts del skill" (`references/scripts.md`), con el esquema y las reglas de "Auditoria y trazabilidad" (`references/audit.md`), y `prompt_version` = `<skill_version>:prototype-ux`. Reporta despues su ruta y su `id` en la verificacion final.
