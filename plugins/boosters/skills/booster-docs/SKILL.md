---
name: booster-docs
description: Genera una vista HTML autocontenida, dinamica y visual a partir de un documento de planificacion AIDD/SDD en Markdown (por ejemplo `docs/cliente-requisitos.md`, `docs/requisitos.md`, `docs/mapa-historias-usuario.md`, `docs/roadmap.md`, `docs/sprint-plan.md`). Usar cuando un skill AIDD/SDD necesite entregar la vista HTML complementaria al final de su comando, o cuando el usuario pida "genera el HTML de este documento", "vista HTML de los requisitos", "renderiza el roadmap a HTML" o equivalentes. El Markdown sigue siendo la unica fuente de verdad; este booster produce un HTML complementario para consumo humano y NO modifica el Markdown.
metadata:
  author: NTT DATA Spain GDN-e
  version: "1.0.0"
---

# booster-docs

Renderizar un documento de planificacion en Markdown a un **HTML autocontenido, dinamico y visual** para consumo humano. El `.md` es la **unica fuente de verdad** (lo leen y escriben los skills AIDD/SDD y lo aprueba el humano por git); este booster genera una **vista complementaria** y **no modifica** el Markdown de origen.

Responder y documentar en espanol siempre que sea posible; conservar en ingles comandos, rutas, flags y terminos tecnicos establecidos. Este `SKILL.md` evita tildes por compatibilidad entre plataformas de agentes.

## Cuando se usa

- **Invocado por un skill AIDD/SDD** como paso final de su comando, para dejar la vista HTML disponible junto al `.md` generado. Cada skill llama a `booster-docs` con el documento que acaba de escribir.
- **Invocado directamente por el usuario**: "genera el HTML de `docs/requisitos.md`", "vista HTML del roadmap", "renderiza el plan de sprints".

## Que produce

Un unico fichero `.html` autocontenido (HTML + CSS + JS inline, sin dependencias ni build, abrible con doble clic), con:

- **Dashboard de KPIs** auto-calculado del contenido (numero de RF/NFR, historias, must-have, elementos fuera de alcance, bloqueantes, preguntas abiertas...).
- **Chips de color** para IDs trazables (`RF-XX`, `NFR-XX`, `HU-XX`/`US-XX`), prioridad (`Alta`/`Media`/`Baja`), MoSCoW (`Must`/`Should`/`Could`/`Won't`), esfuerzo (`S`/`M`/`L`) y marcadores `[BLOQUEANTE]`, tanto inline como en tablas.
- **Alcance dentro/fuera** con estilo diferenciado, tablas con formato, blockquotes de metadatos y bloques Mermaid renderizados si el documento los incluye.
- **Indice lateral (TOC) sticky con scroll-spy**, modo claro/oscuro automatico y estilos de impresion.

El tipo de documento se **auto-detecta** por el nombre del fichero o el `# H1`; los tipos desconocidos se renderizan igual con KPIs genericos. Se puede forzar con `--doc-type`.

## Flujo

1. Resolver el Markdown de entrada (ruta indicada por el skill que invoca o por el usuario).
2. Trabajar desde la raiz del proyecto.
3. Definir la ruta de salida: por convencion `docs/html/<mismo-nombre>.html` (crea `docs/html/` si no existe). No sobreescribas el `.md` de origen bajo ningun concepto.
4. Renderizar con `scripts/render_docs_html.py`, siempre en UTF-8.
5. Informar de la ruta HTML generada. Si el script reporta mojibake no reparable, corregir la fuente Markdown y volver a renderizar; no entregar HTML con mojibake conocido.

## Invocacion del script

Ejecutar el script incluido en este skill. Preferir `--input <markdown-file>` (evita degradacion de `stdin` por la shell en Windows con acentos, enes o signos invertidos):

```bash
# Linux / macOS — --open abre el HTML en el navegador por defecto al terminar
python "${CLAUDE_PLUGIN_ROOT}/skills/booster-docs/scripts/render_docs_html.py" \
  --input docs/requisitos.md \
  --output docs/html/requisitos.html \
  --open
```

```powershell
# Windows (PowerShell) — guardar el Markdown temporal como UTF-8 si se genera al vuelo
python .agents\skills\booster-docs\scripts\render_docs_html.py --input docs\requisitos.md --output docs\html\requisitos.html
```

Flags:

- `--input <path>`: Markdown de entrada. Sin el, lee de `stdin` (decodificando bytes como UTF-8).
- `--output <path>`: ruta del HTML de salida (obligatorio). El script crea las carpetas necesarias.
- `--doc-type <tipo>`: fuerza el tipo de documento (`cliente-requisitos`, `requisitos`, `mapa-historias-usuario`, `detalle-historias-usuario`, `arquitectura-base-prototipo`, `propuesta-arquitectura-base`, `guia-estilos`, `arquitectura-base`, `roadmap`, `planificacion-proyecto`, `sprint-plan`). Por defecto se auto-detecta.
- `--title <texto>`: sobreescribe el titulo del documento (por defecto usa el `# H1`).
- `--open`: abre el HTML generado en el navegador por defecto (best-effort; no hace nada en entornos sin GUI/headless y nunca hace fallar el render). Los skills AIDD/SDD lo pasan para abrir la vista automaticamente al terminar el comando, salvo en modo no interactivo (CI/auto).

## Reglas de codificacion

- Tratar toda entrada Markdown y salida HTML como UTF-8. El HTML final conserva `<meta charset="utf-8">`.
- En Windows, no usar `Out-File` ni redirecciones sin `-Encoding utf8`; preferir `--input`.
- El script repara mojibake comun automaticamente y aborta si detecta mojibake no reparable en la entrada o en la salida.

## Reglas de contenido

- **Nunca** modificar el Markdown de origen: este booster solo escribe el `.html`.
- La vista HTML es un complemento; ante cualquier discrepancia, el `.md` prevalece.
- Mantener la salida junto a los documentos (`docs/html/`) para que sea facil de localizar.

## Verificacion final

Al terminar, informar:

- Ruta del HTML generado.
- Tipo de documento detectado (o forzado) y KPIs principales incluidos.
- Cualquier advertencia del script (por ejemplo, fragmentos de mojibake reparados).
