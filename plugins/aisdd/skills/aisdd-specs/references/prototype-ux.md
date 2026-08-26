# `aisdd prototype-ux`

> Referencia del skill `aisdd-specs`. El indice y las reglas comunes estan en `SKILL.md`.

## `aisdd prototype-ux [what-you-want-to-build]`

> Alias: `native-ai prototype-ux [what-you-want-to-build]`.

Genera prototipos UX.

- Si llega `<what-you-want-to-build>`, identifica en el cambio las pantallas nuevas o modificadas revisando `design.md`, `proposal.md` y `spec.md`.
- Lanza el skill `booster-ux` una vez por cada pantalla nueva identificada.
- Si no llega argumento, lanza directamente `booster-ux` y sigue su flujo de preguntas.
- Si no existe `booster-ux`, avisa donde debe instalarse y no generes prototipos por otro camino salvo peticion expresa del usuario.
