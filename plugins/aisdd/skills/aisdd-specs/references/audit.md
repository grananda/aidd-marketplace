# Auditoria y trazabilidad

> Referencia del skill `aisdd-specs`. El indice y las reglas comunes estan en `SKILL.md`.

## Auditoria y trazabilidad

Cada comando del skill debe registrar una entrada de auditoria estructurada para permitir auditorias futuras del uso del skill. El objetivo es trazar quien ejecuto que comando, sobre que entrada, con que prompt y modelo, y que salida o decision humana se produjo. La auditoria es obligatoria para todos los comandos.

### Ubicacion y formato

- Directorio: `openspec/audit/` en la raiz del proyecto. Crealo si no existe.
- Fichero: `openspec/audit/YYYY-MM.jsonl` (un fichero por mes natural). Modo append-only, una entrada JSON por linea.
- Codificacion: UTF-8 sin BOM. Sin comas ni corchetes envolventes: JSON Lines puro.
- No reescribas entradas existentes. Si necesitas corregir o anular una entrada, anade una nueva con `correction_of: <id>`.

### Esquema de cada entrada

Cada linea es un objeto JSON con estos campos:

```json
{
  "id": "<uuid v4 o ulid>",
  "timestamp": "<ISO 8601 UTC, p.ej. 2026-05-25T14:30:00Z>",
  "command": "aisdd <subcomando>",
  "change_id": "<id-del-cambio-o-null>",
  "skill_version": "<version del skill, p.ej. 1.2.0>",
  "prompt_version": "<skill_version>:<command-slug>[@variante]",
  "model": "<id del modelo, p.ej. claude-opus-4-7[1m] o desconocido>",
  "platform": "<claude-code | codex | otra>",
  "user": "<email o identificador disponible, o null>",
  "input_hash": "sha256:<hex>",
  "input_files": [
    { "path": "<ruta relativa>", "sha256": "<hex>" }
  ],
  "output_hash": "sha256:<hex>",
  "output_files": [
    { "path": "<ruta relativa>", "sha256": "<hex>" }
  ],
  "decisions": [
    {
      "slug": "<slug>",
      "type": "bloqueante | preferencia | confirmacion | correccion",
      "origen": "usuario | auto-default",
      "decision": "<resumen corto de la opcion elegida o 'pendiente'>"
    }
  ],
  "status": "ok | partial | aborted",
  "errors": [ "<mensaje corto>" ],
  "correction_of": "<id de entrada corregida, opcional>"
}
```

Reglas para los campos:

- `id`: generador propio del agente (UUID v4 o ULID). Debe ser unico.
- `timestamp`: hora UTC en formato ISO 8601 con sufijo `Z`.
- `input_hash`: SHA-256 hex del concatenado, en orden alfabetico ascendente por `path`, de las parejas `<path>\n<sha256>\n` de cada fichero en `input_files`. Si la lista esta vacia, usa `sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (hash del string vacio).
- `output_hash`: misma formula sobre `output_files`. Si el comando no produce ficheros nuevos ni modificados, usa el hash del string vacio y deja `output_files` vacio.
- `input_files`: ficheros leidos como entrada relevante del comando (artefactos del cambio, configuracion, documentos del usuario). No incluyas codigo fuente del repositorio salvo que el comando lo procese explicitamente.
- `output_files`: ficheros creados o modificados por el comando (proposal.md, design.md, spec.md, decisions.md, roadmap.md, HTML de UML, etc.).
- `decisions`: solo para comandos que recogen decisiones humanas (hoy: `implement change`). Incluye tanto las decisiones del pre-flight como las entradas de `Tipo: correccion` registradas durante la implementacion: son las que permiten contar correcciones por change como indicador de la calidad de los specs. En el resto de comandos, lista vacia.
- `model` y `platform`: si no puedes resolverlos con fiabilidad, usa `"desconocido"`. No inventes valores.
- `user`: si la plataforma expone email del usuario, registra el email; si no, `null`. No registres datos personales adicionales.
- `prompt_version`: usa la version del skill seguida del slug del comando. Ejemplos: `2.0.0:implement-change/preflight`, `2.0.0:open-change/preflight`, `2.0.0:roadmap`, `2.0.0:close-change`, `2.0.0:init`, `2.0.0:prototype-ux`, `2.0.0:uml`. El comando `aisdd lane` **no escribe auditoria**: no modifica artefactos del proyecto, solo un puntero local del dev.

### Calculo de hashes

> **Via preferente: `audit.py`.** Le pasas las rutas y el hace todo lo de abajo. Esta especificacion se mantiene porque es el contrato que el script implementa, y porque hay que poder cumplirla a mano si no se puede ejecutar Python.


- En PowerShell: `Get-FileHash -Algorithm SHA256 <path>`.
- En Bash o entornos POSIX: `sha256sum <path>` o `shasum -a 256 <path>`.
- Para el hash agregado (`input_hash`, `output_hash`), calcula el SHA-256 del string formado por las parejas `<path>\n<sha256>\n` concatenadas en orden alfabetico ascendente por `path`. Usa rutas relativas a la raiz del proyecto con separador `/`.

### Cuando escribir la entrada

- Escribe la entrada **al final** del comando, justo antes del resumen de verificacion.
- Una sola entrada por invocacion de comando.
- **Excepcion: `aisdd lane` no escribe auditoria.** No toca artefactos del proyecto — solo el puntero local `openspec/.lane` del dev — y registrarlo llenaria el log de ruido sin trazabilidad util.
- Si el comando se aborta antes de completar (por ejemplo dudas bloqueantes pendientes en el pre-flight), escribe igualmente con `status: aborted` y la informacion disponible.
- Si el comando falla por error, escribe con `status: partial` o `aborted` segun corresponda y rellena `errors` con mensajes cortos (sin trazas largas ni datos sensibles).

### Que NO registrar

- Contenido literal de los ficheros (solo hashes).
- Texto libre de las dudas planteadas en el pre-flight (el contenido vive en `decisions.md`).
- Secretos, tokens, credenciales, claves API, ni datos personales mas alla del email del usuario que ya proporciona la plataforma.
- Diffs de codigo. La entrada apunta a artefactos por hash; el codigo vive en git.

### Retencion

- Retencion por defecto: `365` dias.
- Resolucion del valor efectivo, por orden de precedencia:
  1. Clave `audit.retention_days` (entero positivo) en `config.yaml` de OpenSpec.
  2. Fichero `openspec/audit/.retention` con un entero positivo de dias en la primera linea.
  3. Default `365`.
- Al inicio de cada comando, comprueba los ficheros `openspec/audit/YYYY-MM.jsonl`:
  - Si el ultimo dia del mes representado por el fichero es anterior a `hoy - retencion`, eliminalo.
  - No purgues entradas individuales dentro de un fichero. Trabaja por mes para preservar la integridad append-only.
- Nunca apliques retencion menor a `30` dias aunque la configuracion lo indique: en ese caso usa `30` y avisa al usuario una vez.

### Compatibilidad y operacion

- Manten el JSONL plano y sin transformaciones para ingestar en Splunk, ELK, BigQuery u otros sin parseo intermedio.
- No comprimas ni cifres los ficheros: deben ser legibles directamente.
- La decision de versionar `openspec/audit/` en Git es del proyecto. Recomienda al usuario incluirlo en seguimiento si la politica lo permite; en caso contrario, anadirlo a `.gitignore` y archivarlo aparte mediante el mecanismo de auditoria corporativo.
- Si la escritura de la entrada de auditoria falla (disco lleno, permisos), no bloquees el resultado funcional del comando: informa el fallo en el resumen y deja constancia en `errors` de un futuro reintento si es viable.
