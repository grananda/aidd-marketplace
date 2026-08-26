# `aisdd uml`

> Referencia del skill `aisdd-specs`. El indice y las reglas comunes estan en `SKILL.md`.

## `aisdd uml [what-you-want-to-build]`

> Alias: `native-ai uml [what-you-want-to-build]`.

Genera HTML con diagramas asociados al cambio.

1. Resuelve el cambio objetivo igual que en `implement` si falta el argumento.
2. Reune `design.md`, `proposal.md` y todos los ficheros `spec.md` del cambio.
3. Lanza el skill `booster-uml` con esa documentacion para generar el HTML de diagramas.
4. Si no existe `booster-uml`, avisa donde debe instalarse y deja indicadas las rutas de entrada que deberia procesar.
