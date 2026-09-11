---
name: aiba-handover
description: AIBA (AI Business Analyst) — genera el documento de traspaso al equipo que se queda con el mantenimiento del sistema, `docs/traspaso.md`, y su vista HTML, mediante el comando `aiba handover` (alias `aiba traspaso`). Conceptual y tecnico, con diagramas y tablas, y con **lo operativo primero**: donde corre cada componente, como se despliega y como se vuelve atras, donde estan los datos y si alguien ha probado a restaurarlos, logs, metricas y alertas, que accesos hay que pedir, donde viven los secretos --**nunca su valor**--, dependencias externas, lo que se rompe a menudo y los contactos; despues el equipo de mantenimiento con su dedicacion y el conocimiento que solo tiene una persona segun la auditoria; y al final que hace el sistema hoy, como esta construido y que queda por construir. Lo construido sale de las specs, la arquitectura, el archivo de changes y la auditoria; lo que nunca se escribio sale de un cuestionario, `docs/traspaso-cuestionario.md`, que rellena quien lo sabe. Lo que falta sale como hueco declarado. La estructura la da un script, asi que no depende del modelo, y el script se niega a escribir si encuentra algo con pinta de secreto. Documento versionado, con sello de version, fecha y aprobacion. Usar cuando el usuario pida "traspaso", "handover", "documento de traspaso", "pasar el mantenimiento a otro equipo", "transferencia de conocimiento", "documentacion para el equipo de mantenimiento" o equivalentes. Skill de entrega, sin auditoria estructurada.
metadata:
  author: NTT DATA Spain GDN-e
  version: "0.1.0"
---

# aiba-handover (AIBA · traspaso al equipo de mantenimiento)

Usa este skill cuando otro equipo vaya a hacerse cargo del sistema, o cuando el usuario invoque:

- `aiba handover`
- `aiba traspaso`

Tambien cuando pida "documento de traspaso", "transferencia de conocimiento", "que le dejamos al equipo de mantenimiento" o equivalentes.

Responde y documenta en espanol siempre que sea posible. Conserva en ingles nombres de comandos, ficheros, rutas, flags y terminos tecnicos establecidos. Los documentos generados pueden usar espanol natural con tildes; este `SKILL.md` evita tildes y caracteres especiales por compatibilidad entre plataformas de agentes.

## Que es AIBA y donde encaja este skill

AIBA (AI Business Analyst) es el conjunto de skills que da la cara ante el negocio: el diseno funcional que el cliente firma, el plan que aprueba, el calendario que sigue y los KPIs con los que juzga si merecio la pena. Su metodologia esta en `${CLAUDE_PLUGIN_ROOT}/methodology/native-ai-aiba.md` (referencia de solo lectura). La numeracion de fases es la del proceso AIDD-SDD, cuyos documentos AIBA **consume sin modificar**.

Este skill es **de entrega**: se ejecuta cuando el sistema cambia de manos, y se vuelve a ejecutar mientras dura el traspaso. Tiene dos vecinos con los que no se confunde:

- `aiba project-plan` escribe **antes de construir** lo que se preveia necesitar: entornos, infraestructura, perfiles. Este skill escribe **al entregar** lo que hay y como se opera. La planificacion es una de sus entradas, no su resultado.
- `aiba onboarding` recibe a alguien que **se incorpora** a un proyecto vivo. Este skill entrega el sistema a un equipo que **se queda** con el, muchas veces sin nadie del equipo original al lado.

No escribe auditoria estructurada. Consulta OpenSpec si existe, pero no depende de el.

## Rol y objetivo

Actua con este rol durante todo el comando:

> Actua como el analista que prepara la entrega de un sistema a otro equipo. Tu objetivo es que quien lo recibe pueda operarlo a las tres de la manana sin llamar a nadie: donde corre, como se despliega y se vuelve atras, donde mirar cuando falla y a quien pedir que. **Lo que no sepas, no lo rellenes**: un traspaso con huecos honestos sirve; uno con relleno plausible es peligroso, porque el equipo entrante actuara sobre el.

Criterio de salida: existen `docs/traspaso.md`, sellado con version y fecha, y `docs/html/traspaso.html`. Lo operativo sale del cuestionario, y cada pregunta sin contestar, cada riesgo y cada fuente que falta aparecen en la seccion 1 del documento.

## Reglas generales

- Trabaja desde la raiz del proyecto del usuario.
- **Nunca incluyas secretos.** Un documento de traspaso los atrae: contrasenas, tokens, cadenas de conexion, claves de API. Se nombra **donde viven** --que gestor de secretos, que ruta, quien da acceso-- y nunca el valor. Un traspaso circula por correo, se sube a un SharePoint y acaba en el portatil de gente que ya no esta en el proyecto. El script lo vigila: se niega a leer un cuestionario y a escribir un documento con algo que tenga pinta de secreto, y dice donde esta sin repetirlo. **No lo esquives reformulando el valor**: sustituyelo por donde vive.
- **Dos mitades con dos origenes.** Lo que el sistema hace y como esta construido ya esta escrito: specs, arquitectura, archivo de changes, auditoria. Como se opera no lo escribio nadie, y sale **solo** del cuestionario `docs/traspaso-cuestionario.md`. **No completes lo operativo con tu conocimiento general**: que el stack sea Azure no dice donde estan los logs.
- **El cuestionario es la fuente de lo operativo**, y lo rellena quien lo sabe --desarrollo, sistemas, el propio BA--. Si el usuario te da una respuesta en la conversacion, escribela **en el cuestionario**, en su pregunta, y no en el JSON ni en el documento: asi la siguiente regeneracion no la pierde. Es un fichero del proyecto y se versiona.
- **La estructura la da el script; tu escribes tres cosas**: dos parrafos, tres diagramas y el equipo de mantenimiento (ver el paso 4). Las tablas, los riesgos, el diagrama de despliegue y los huecos salen de `compute_handover.py`: no los toques, y el documento sale igual lo genere el modelo que lo genere.
- **Nada de lo que te fabriques para trabajar se queda en el proyecto.** Los JSON intermedios, y cualquier script de usar y tirar que necesites en cualquier lenguaje, van a un directorio temporal. En el proyecto solo quedan el cuestionario, `docs/traspaso.md`, su vista HTML y el sidecar del sello.
- Este documento requiere **aprobacion del BA**, y se entrega a un tercero: lo que cuenta es la version entregada, que es la que queda sellada. Al terminar, deja claro que esta pendiente de aprobacion.

## Fuentes

| Que se cuenta | De donde sale | Si falta, lo genera |
|---|---|---|
| Que es el sistema y para quien | `docs/cliente-requisitos.md` | `aidd client-requirements` |
| Repositorios, integraciones y como esta construido | `docs/arquitectura-base.md` | `aidd architecture` |
| El equipo que lo construyo y los entornos previstos | `docs/planificacion-proyecto.md` | `aiba project-plan` |
| Que hace el sistema hoy | `openspec/specs/` | `aisdd close change`, o `aisdd init` en un proyecto existente |
| Que se construyo, en que orden y con que decisiones | `openspec/changes/archive/` | `aisdd close change` |
| Quien construyo cada parte | `openspec/audit/` | cualquier comando `aisdd` |
| Que queda por construir | el estado de OpenSpec y `docs/roadmap.md` | `aisdd roadmap` |
| Como se opera | `docs/traspaso-cuestionario.md` | este skill, en el paso 1 |

**Un proyecto sin alguna de ellas tiene traspaso igual**: se genera con lo que haya, y el documento dice con que se ha generado en su ultima seccion.

## Flujo del comando `aiba handover`

> **Antes de ejecutar cualquiera de estos scripts, comprueba que la ruta resuelve.** `${CLAUDE_PLUGIN_ROOT}` la define Claude Code; **otros agentes la dejan vacia**, y entonces la orden se convierte en `/skills/...` y falla con `No such file or directory`. Si eso pasa, el script **sigue estando en el disco**: localizalo una vez con `find -L` --por ejemplo en `~/.claude/plugins` o en el directorio de plugins del agente que uses--, quedate con la **ruta absoluta** y usala en todas las invocaciones de esta sesion. **El `-L` no es opcional**: si los skills estan instalados por enlace simbolico un `find` a secas no los sigue y devuelve vacio. **Nunca des por hecho que se ejecuto un script que no ejecutaste.**

### 1. El cuestionario

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/aiba-handover/scripts/compute_handover.py" \
  --root . --preparar
```

Crea `docs/traspaso-cuestionario.md` si no existe, con lo que ya se sabe precargado: los repositorios y las integraciones de la arquitectura, las personas de la auditoria y los entornos que preveia la planificacion. Si ya existe, le anade las preguntas que le falten **sin tocar lo contestado**. Al terminar dice cuantas preguntas hay contestadas.

- **Si lo acaba de crear, o no tiene ninguna respuesta, para aqui.** Di al usuario que el cuestionario existe, que lo rellene quien sepa la parte operativa --no hace falta que sea el BA-- y que vuelva a lanzar `aiba handover`. Ofrecele contestar ahora lo que el sepa: lo escribes tu en el cuestionario, debajo de su pregunta. Sigue con un borrador lleno de huecos **solo si lo pide**.
- **Si tiene respuestas, sigue**, aunque falten algunas: lo que falte saldra como hueco.
- **Si se detiene por un secreto**, el cuestionario ya lo contiene. Dile al usuario en que linea esta --el script lo dice sin repetirlo--, que lo sustituya por donde vive y, **si el fichero ya estaba en git, que lo rote**: borrarlo no lo saca del historial.

### 2. El estado, si hay OpenSpec

Crea un directorio temporal para los intermedios y, **solo si existe `openspec/`**, calcula el estado con el script de `aiba status-report`:

```bash
TMP=$(mktemp -d)
python3 "${CLAUDE_PLUGIN_ROOT}/skills/aiba-status-report/scripts/compute_status.py" \
  --root . --out "$TMP/estado.json"
```

`mktemp -d` es de una shell POSIX. En PowerShell el equivalente es `$TMP = (New-Item -ItemType Directory -Path (Join-Path $env:TEMP ([guid]::NewGuid()))).FullName`, y las rutas de abajo se escriben igual con `$TMP` delante.

Sin `openspec/` **salta este paso** (crea igualmente el directorio temporal): el traspaso dira que no sabe que queda por construir.

### 3. Los hechos

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/aiba-handover/scripts/compute_handover.py" \
  --root . --estado "$TMP/estado.json" --out "$TMP/traspaso.json"
```

Sin el paso 2, omite `--estado`. El JSON trae el cuestionario con sus respuestas y lo que falta; las capacidades de `openspec/specs/`; los changes cerrados con las capacidades que tocan y sus decisiones; `conocimiento`, con quien conoce cada capacidad; los repositorios y las integraciones de la arquitectura; el equipo que lo construyo; lo pendiente; el diagrama de despliegue ya dibujado; los riesgos; y en `fuentes` que hay y que falta.

### 4. Lo que escribes tu

Edita `$TMP/traspaso.json` y anade tres claves:

```json
"narrativa": {
  "que_es": "Tres o cuatro frases: que hace el sistema, para quien y que se para si falla.",
  "como_esta_construido": "Tres o cuatro frases: stack, capas y como se reparte en repositorios."
},
"diagramas": {
  "contexto": "flowchart LR\n  ...",
  "flujos": [{"titulo": "Alta de una poliza", "mermaid": "sequenceDiagram\n  ..."}],
  "datos": "erDiagram\n  ..."
},
"equipo": {
  "perfiles": [{"perfil": "Backend Java", "dedicacion": "30 %",
                "skills": "Spring Boot 3 y la integracion SOAP con el core de polizas",
                "cobertura": "Laborables de 8:00 a 15:00"}],
  "diferencias": ["Sobra el perfil de UX: el mantenimiento no preve pantallas nuevas.",
                  "Falta quien conozca la integracion con el core: en construccion la llevo una sola persona."]
}
```

**Los parrafos.** `que_es` sale del brief y `como_esta_construido` de la arquitectura, escritos para alguien tecnico que no ha visto el proyecto nunca. Si una fuente falta, el parrafo lo dice en vez de rellenarlo.

**Los diagramas**, en Mermaid y **solo con lo que diga la arquitectura**:

- `contexto`: un `flowchart` con los usuarios, los contenedores del sistema --los repositorios o los modulos de la seccion 4 de la arquitectura-- y los sistemas externos de la seccion 10, con las relaciones que la arquitectura describe.
- `flujos`: dos o tres `sequenceDiagram` de los flujos de la seccion 7 que son criticos: los que paran el negocio si fallan y los que cruzan una integracion externa.
- `datos`: un `erDiagram` con las entidades principales y sus relaciones, de las specs y la arquitectura. Los atributos clave, no todos.

Si la arquitectura no da para uno, **no lo incluyas**: el script declara el hueco. Un diagrama inventado es relleno plausible con forma de dibujo. Tampoco escribes el de **despliegue**: lo dibuja el script con la tabla de componentes del cuestionario, porque es el unico que no esta en ningun documento. El script descarta, avisando, el diagrama que no empiece por el tipo esperado.

**El equipo de mantenimiento** es un juicio, y es tuyo. Parte del equipo que lo construyo --`planificacion.perfiles` y `planificacion.perfiles_texto`-- y ajustalo con el stack y las integraciones de `arquitectura`, lo que se rompe a menudo y la cobertura del cuestionario, y `conocimiento`:

- **Cada perfil lleva su dedicacion en porcentaje.** Mantener rara vez es a jornada completa, y "un perfil backend" sin "al 30 %" no sirve para presupuestar. El script marca como pendiente la dedicacion que no pueda leer, y suma el total cuando puede leerlas todas.
- **Skills concretos**, ligados al stack real y a las integraciones que hay que sostener, no categorias genericas.
- **`diferencias`**: en que se diferencia del equipo de construccion y **por que**. El equipo que construye no es el que mantiene: para mantener sobra una parte --a menudo UX y arquitectura a tiempo completo-- y falta otra --a menudo alguien que sepa de la integracion que nadie quiso tocar--. Si `conocimiento` marca una capacidad que solo conoce una persona, di como se cubre. Si no hay planificacion con la que comparar, dilo en la primera diferencia.

Nada de esto lleva secretos: el script revisa estas tres claves antes de escribir.

### 5. El documento

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/aiba-handover/scripts/compute_handover.py" \
  --render "$TMP/traspaso.json" --output docs/traspaso.md
```

Escribe `docs/traspaso.md` entero, con lo operativo primero:

1. **Lo que hay que resolver antes de cerrar el traspaso**: los riesgos, las preguntas sin contestar, lo que falta por escribir y las fuentes que faltan.
2. Que es el sistema.
3. a 10. Donde corre --con el diagrama de despliegue--, como se despliega, datos, operacion, accesos y secretos, dependencias externas, lo que se rompe a menudo y contactos.
11. El equipo que lo mantiene: perfiles y dedicacion, en que se diferencia del de construccion, cobertura y **conocimiento de una sola persona**.
12. a 14. Que hace el sistema hoy, como esta construido --con los diagramas-- y, para seguir evolucionandolo, las decisiones tomadas por el camino, lo construido en orden y lo que queda.
15. Con que se ha generado.

**Si se detiene por un secreto**, dice en que clave del JSON esta: reescribela diciendo donde vive. Si `docs/traspaso.md` ya existia se reescribe --es lo esperado mientras dura el traspaso--, y el sello sube la version.

### 6. Sello de version, fecha y aprobacion

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/stamp_doc.py" --input docs/traspaso.md --gated
```

Anade la cabecera `> **Version N** - **Generado:** fecha hora - **Pendiente de aprobacion**`, con la version incrementada en `docs/.aidd-doc-meta.json` y la fecha real. No edites esa linea a mano. **Es lo que dice que version se entrego**: el traspaso va a un tercero, y una vez aprobado, si alguien lo regenera, el sello dice que ha cambiado despues de aprobarse.

### 7. La vista HTML

Genera `docs/html/traspaso.html` con el skill `booster-docs`, con `docs/traspaso.md` como entrada (crea `docs/html/` si no existe), y sigue lo que diga `booster-docs` sobre los diagramas Mermaid: el traspaso los lleva. Pasa `--open` para abrirlo al terminar, salvo en modo no interactivo. Si `booster-docs` no esta disponible, avisa de que la vista no se genero y de que se instala con el plugin `boosters`, **pero no bloquees**: el `.md` basta. El HTML se versiona junto al `.md`.

Hoy el traspaso no sale en `.docx`. Si el cliente lo pide en Word, dilo en vez de improvisar un conversor: el HTML se imprime a PDF.

## Verificacion final

Al terminar, informa:

- Comando ejecutado (`aiba handover`) y rutas de `docs/traspaso.md`, `docs/html/traspaso.html` y `docs/traspaso-cuestionario.md`.
- Cuantas preguntas del cuestionario estan contestadas y cuales faltan, por tema, **tal como las da el script**.
- Los **riesgos** de la seccion 1, sin suavizarlos: una restauracion que nunca se ha probado o una capacidad que solo conoce una persona son lo primero que tiene que saber quien firma el traspaso.
- Los **huecos**: cada fuente que falta y el comando que la genera.
- Recordatorio: pendiente de **aprobacion del BA**. Se aprueba con `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/stamp_doc.py" --input docs/traspaso.md --approve "<nombre>"`, y desde ahi el sello distingue sin aprobar, aprobado y **cambiado despues de aprobarse**.
- Cuando regenerarlo: cada vez que se conteste parte del cuestionario, y siempre justo antes de entregarlo. Lo que se entrega es la version sellada y aprobada.
