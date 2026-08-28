# `aisdd uml`

> Referencia del skill `aisdd-specs`. El indice y las reglas comunes estan en `SKILL.md`.

## `aisdd uml [change-slug]`

> Alias: `native-ai uml [change-slug]`.

Genera HTML con diagramas asociados al cambio.

1. **Resuelve el change objetivo** segun "Resolver el change objetivo (compartido)" (`references/target-change.md`) si falta el argumento.
2. Reune `design.md`, `proposal.md` y todos los ficheros `spec.md` del cambio.
3. Lanza el skill `booster-uml` con esa documentacion para generar el HTML de diagramas.
4. Si no existe `booster-uml`, avisa donde debe instalarse y deja indicadas las rutas de entrada que deberia procesar.
5. **Escribe la entrada de auditoria.** Es obligatoria y **no es opcional para ningun comando salvo `aisdd lane`**. Componla con `audit.py` segun "Scripts del skill" (`references/scripts.md`), con el esquema y las reglas de "Auditoria y trazabilidad" (`references/audit.md`), y `prompt_version` = `<skill_version>:uml`. Reporta despues su ruta y su `id` en la verificacion final.
