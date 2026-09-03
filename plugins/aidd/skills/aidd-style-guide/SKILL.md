---
name: aidd-style-guide
description: Fase 2 (paso 2.3) del conjunto AIDD (AI Driven Development). Genera la guia de estilos del producto, mediante el comando `aidd style-guide` (alias `aidd fase 2.3 estilos`). Actua como experto en diseno de producto y sistemas de diseno que lee `docs/detalle-historias-usuario.md` y la referencia visual o de marca y genera `docs/guia-estilos.md` con principios de diseno y UX, paleta de colores con valores hex, tipografia, espaciado, iconografia, design tokens CSS concretos --emitidos ademas como `docs/design/tokens.json` y `tokens.css`, para que el valor exista en un solo sitio en vez de retecleado a mano--, componentes base y pautas de uso, reglas de responsive y accesibilidad WCAG 2.1 AA, y estructura de pantallas y criterios de navegacion. Si el usuario lo indica, ofrece extraer la identidad visual de un diseno en Figma **solo via MCP** (`figma-developer-mcp`) o desde un export de design tokens a JSON; nunca por llamadas REST ni gestionando el token. De ahi sale lo basico --paleta, tipografia, espaciado, tokens--: la composicion de cada pantalla es trabajo del plugin `aifg`, y este skill ofrece encadenar con el. Paso del Diseno (AI Architect), complementario a la propuesta de arquitectura. Skill de planificacion, autonomo del mundo OpenSpec/aisdd-specs y sin auditoria estructurada.
metadata:
  author: NTT DATA Spain GDN-e
  version: "1.2.0"
---

# aidd-style-guide (AIDD · Fase 2 · paso 2.3)

Usa este skill cuando el usuario quiera definir la guia de estilos / sistema de diseno del producto, o cuando invoque:

- `aidd style-guide`
- `aidd fase 2.3 estilos`

Tambien cuando pida "guia de estilos", "design tokens", "sistema de diseno", "paleta y tipografia" o equivalentes del paso 2.3 (parte visual).

Responde y documenta en espanol siempre que sea posible. Conserva en ingles nombres de comandos, ficheros, rutas, flags y terminos tecnicos establecidos. Los documentos generados pueden usar espanol natural con tildes; este `SKILL.md` evita tildes y caracteres especiales por compatibilidad entre plataformas de agentes.

## Que es AIDD y donde encaja este skill

AIDD (AI Driven Development) es un conjunto de skills de planificacion y arquitectura asistida por IA. Cada skill cubre una fase o paso del proceso descrito en `${CLAUDE_PLUGIN_ROOT}/methodology/native-ai-aidd-sdd.md` (referencia de metodologia, solo lectura):

- Fase 0 — `aidd client-requirements`.
- Fase 1 — `aidd requirements`, `aidd user-stories`, `aidd user-story-details`.
- **Fase 2 — Diseno (AI Architect)**:
  - `aidd prototype-architecture` (2.1): `docs/arquitectura-base-prototipo.md`.
  - `aidd prototype` (2.2): implementacion del prototipo, redirige a `booster-ux`.
  - **`aidd style-guide`** (este skill, 2.3): guia de estilos (`docs/guia-estilos.md`).
  - `aidd architecture-proposal` (2.3): propuesta de arquitectura (`docs/propuesta-arquitectura-base.md`).
  - `aidd architecture` (2.4): arquitectura tecnica definitiva (`docs/arquitectura-base.md`).

Este conjunto es **autonomo**: puede usarse al margen de `aisdd-specs`, `booster-ux` y `booster-uml`. No depende de OpenSpec ni escribe auditoria estructurada. Las decisiones se registran de forma ligera dentro del propio documento generado.

Como complemento opcional, al final del comando se genera una **vista HTML** de la guia de estilos con `booster-docs` (ver el paso final del flujo). El `.md` sigue siendo la **unica fuente de verdad**; el HTML es solo para consumo humano y no altera el flujo AIDD si `booster-docs` no esta instalado.

> Este skill y `aidd architecture-proposal` cubren juntos el paso 2.3 de la metodologia (guia de estilos + propuesta de arquitectura). Se separan en dos skills para mantener cada invocacion enfocada; pueden ejecutarse en cualquier orden.

## Rol y objetivo

> Actua como experto en diseno de producto, sistemas de diseno y arquitectura frontend. Tu objetivo es definir la guia de estilos del producto a partir del detalle de historias y de la identidad visual o de marca indicada. Es la base visual para el AI Lead y los AI Developers.

Criterio de salida del paso: existe `docs/guia-estilos.md` con design tokens CSS concretos (no descripciones vagas), paleta, tipografia, componentes base y reglas de accesibilidad WCAG 2.1 AA, **y esos tokens emitidos ademas como `docs/design/tokens.json` y `docs/design/tokens.css`**. Lo que falte de identidad visual se marca como pendiente; no inventes una marca.

## Reglas generales

- Trabaja desde la raiz del proyecto del usuario.
- **Entrada principal**: `docs/detalle-historias-usuario.md` (Fase 1) y la **referencia visual / marca** que aporte el usuario (URL, guia de marca, HTML, capturas o un **diseno en Figma**). Si no hay referencia visual, preguntala o marca esa parte como pendiente.
- Si el usuario tiene el diseno en **Figma**, ofrece extraer de ahi la identidad visual (paleta, tipografia, espaciado, tokens) en lugar de inferirla. No inventes valores que puedas extraer del diseno real. Ver "Extraccion desde Figma".
- Si ya existe un prototipo implementado (paso 2.2), usalo como fuente de pistas visuales, pero la guia manda sobre el prototipo.
- **Los tokens tienen un solo dueno, y es este skill.** Los emite la guia y los consume quien haga falta --el prototipo, `aifg`, el front--. Si los generase tambien otro, dos extracciones del mismo Figma acabarian discrepando sin que nadie lo note.
- Antes de preguntar, **lee primero** el detalle de historias, `docs/requisitos.md` (NFR de accesibilidad), `docs/cliente-requisitos.md` y cualquier referencia visual aportada.
- No inventes identidad de marca. Si no hay referencia, propon una base neutra y marcala explicitamente como provisional.
- Los design tokens deben ser **concretos**: custom properties CSS con valores reales (colores hex, escalas de espaciado, familias tipograficas).
- No sobrescribas un `docs/guia-estilos.md` existente sin avisar: leelo, propon los cambios y confirma.
- Este documento requiere aprobacion humana. Al terminar, deja claro que esta pendiente de revision.

## Flujo del comando `aidd style-guide`

### 1. Recopilacion de contexto (lectura previa)

Lee y consolida: `docs/detalle-historias-usuario.md` (pantallas y necesidades de UI), NFR de accesibilidad de `docs/requisitos.md`, la referencia visual/marca aportada y, si existe, el prototipo implementado.

### 2. Pre-flight de preguntas

Resuelve solo lo imprescindible.

1. Cubre, como minimo: identidad visual / marca de referencia, nivel de accesibilidad objetivo (por defecto WCAG 2.1 AA) y soporte responsive esperado.
   - **Pregunta explicitamente si el usuario quiere extraer la identidad visual de un diseno en Figma.** Si responde que si, guia el metodo segun "Extraccion desde Figma" antes de redactar la guia. Si no, continua con la referencia que haya aportado.
2. Clasifica cada hueco en **bloqueante**, **preferencia** o **confirmacion**.
3. No preguntes lo que historias, NFR o la referencia visual ya resuelven.
4. Presupuesto de preguntas: maximo **7** por ejecucion. Prioriza bloqueantes y agrupa relacionadas.
5. Formato: si la plataforma soporta preguntas estructuradas (por ejemplo `AskUserQuestion`), usalo con 2-4 opciones y marca una como `(Recomendada)`; si no, lista numerada con opciones y recomendacion.
6. Modo no interactivo: toma el default recomendado para `preferencia` y `confirmacion`; deja los `bloqueante` sin default como pendientes.
7. Si el usuario aplaza una duda, registrala como pendiente y continua.

### 3. Extraccion desde Figma (opcional)

Ejecuta este paso solo si el usuario confirma que quiere extraer la identidad visual de un diseno en Figma. El objetivo es obtener **valores reales** --colores hex, tipografia, escalas de espaciado, tokens-- en vez de inferirlos.

> **Aqui se saca lo basico, no el diseno entero.** Paleta, tipografia, espaciado y tokens, que es lo que alimenta esta guia y el prototipo. **La composicion de cada pantalla --que va donde, con cuanto espacio, con que estados-- es trabajo del plugin `aifg`**, que la extrae nodo a nodo y la deja colgando de cada HU. Ver el paso 3.bis.

**Solo por MCP.** El recomendado es `figma-developer-mcp` (Framelink), que se ejecuta por npx, lee los archivos desde la web a partir de un enlace y se autentica con un token personal de Figma.

```
claude mcp add figma-developer-mcp -- npx -y figma-developer-mcp --figma-api-key=figd_XXXX --stdio
```

- **No hay camino REST.** Nada de llamar a `api.figma.com` ni de manejar el token desde el skill: es la regla que ya rige la integracion con Jira, y por los mismos motivos --un token en un flag acaba en el historial del shell y en los logs de CI--.
- **Ofrece el comando para que lo ejecute el usuario**; no lo ejecutes tu con un token que te acaben de dar por chat. Scope de usuario, nunca un `.mcp.json` de proyecto commiteado. **No escribas el token en ningun documento generado.**
- Pide el **enlace al archivo, frame o grupo** (Copy link).
- **Localiza las tools por funcion, no por nombre**: varian entre versiones y entre servidores equivalentes.

**Alternativa sin MCP: export de design tokens a JSON.** Un plugin de Figma (Tokens Studio, "Design Tokens") exporta los tokens a un JSON; pide la **ruta del fichero exportado** y mapealo. No maneja credenciales, asi que no cae por la regla anterior. Da tokens, **no datos de nodo**: no sustituye a `aifg`.

Si ningun metodo es viable, continua con la referencia visual que haya aportado el usuario --URL, capturas, marca-- y **registra en el documento que los valores no se extrajeron de Figma**. Anota en la seccion de decisiones por que metodo se obtuvieron.

### 3.bis. Ofrecer la captura del diseno con AIFG

Si el usuario trabaja con Figma, **preguntale si quiere lanzar `aifg capture` ahora o hacerlo el mas tarde**. Ese comando extrae la composicion nodo a nodo y la vincula a cada HU, que es lo que permite luego implementar una pantalla pareciendose al diseno y no solo respetando su paleta.

El orden lo permite: las historias existen desde el paso 1.3, asi que hay a que vincular los nodos.

**Degradacion elegante**: si el plugin `aifg` no esta instalado, **dilo y no lo ofrezcas como si existiera** --puede instalarse desde el mismo marketplace--, y continua. La guia sola es suficiente para seguir: sin arbol de diseno, `aisdd implement change` tira de ella.

### 4. Generacion de `docs/guia-estilos.md`

Genera (o actualiza) `docs/guia-estilos.md` con esta estructura:

```markdown
# Guia de estilos — <nombre del proyecto>

> Documento de Fase 2 (AIDD · paso 2.3). Generado por `aidd style-guide`.
> Entrada: docs/detalle-historias-usuario.md + referencia visual/marca.

## 1. Principios de diseno y UX
- Principios rectores y tono de la interfaz.

## 2. Paleta de colores
- Valores hex por rol (primario, secundario, superficie, estados, etc.). Escribe **siempre el codigo del color** (`#RRGGBB`, o `rgb()`/`hsl()`) junto a cada rol; la vista HTML de `booster-docs` pinta automaticamente una **muestra del color al lado de su codigo**, asi que no hace falta describir el color con palabras: basta el codigo.

## 3. Tipografia, espaciado e iconografia
- **Tipografia**: familias, escala de tamanos y pesos, con valores reales.
- **Espaciado**: la **escala completa con sus valores** (`4px`, `8px`, `16px`...), no "espaciado generoso". Es lo que mas delata que un front no es el diseno, y no cabe en media linea.
- **Iconografia**: set, tamanos y grosor de trazo.

## 4. Design tokens CSS
- Custom properties concretas (`--color-...`, `--space-...`, `--font-...`) con valores reales.

## 5. Componentes base y pautas de uso
- Botones, campos, tarjetas, navegacion, etc., con cuando y como usarlos.

## 6. Responsive y accesibilidad
- Breakpoints y reglas responsive. Cumplimiento WCAG 2.1 AA (contraste, foco, semantica).

## 7. Estructura de pantallas y navegacion
- Layout base y criterios de navegacion.

## 8. Decisiones tomadas en el paso 2.3 (estilos)
- Registro ligero: pregunta, opciones, decision, origen (usuario | default), una linea de justificacion.
```

Reglas de contenido:

- Los design tokens deben ser usables tal cual por el frontend (valores reales, no placeholders).
- **La seccion 4 se emite ademas como fichero**, no solo como prosa dentro del `.md`. Ver "Emision de los tokens".
- Marca como provisional todo lo que dependa de una identidad de marca aun no aportada.
- La seccion 8 sustituye a la auditoria estructurada e incluye decisiones resueltas por default.

### Emision de los tokens

Escribe **`docs/design/tokens.json`** y **`docs/design/tokens.css`** con los mismos valores de la seccion 4. Crea `docs/design/` si no existe.

Hoy esos valores viven solo dentro del markdown y alguien los reteclea en el CSS del proyecto: una copia a mano, sin ningun vinculo entre las dos. Emitirlos como fichero deja **un solo sitio donde existe el valor**.

**El front no los importa.** El CSS y el JS que se generan son **del prototipo**, no del entregable final: el CSS final se genera cuando las HU lo dictaminan, con los valores apropiados, y despues no se toca. Un cambio de estilo posterior es una tarea aparte y no es asunto de este skill.

Son, por tanto, **entrada de generacion y no dependencia de runtime**. El `.json` sirve ademas para que `aifg` resuelva los colores de cada nodo contra **nombres de token** (`--color-primary`) en vez de contra hex sueltos.

**La seccion 4 del `.md` no desaparece** --una persona quiere leer la guia y ver la tabla de rol a valor--, pero pasa a ser una **vista**: la fuente es el fichero.

### Sello de version y fecha-hora (antes de renderizar)

Tras escribir o actualizar `docs/guia-estilos.md`, y **antes** de generar la vista HTML, sella el documento:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/stamp_doc.py" --input docs/guia-estilos.md --gated
```

Anade/actualiza la cabecera `> **Version N** - **Generado:** fecha hora`, **incrementa la version en cada regeneracion** (via `docs/.aidd-doc-meta.json`) y usa la **fecha y hora reales**. No inventes la version ni la hora: las pone el script y esa linea no se edita a mano. Si Python no esta disponible, avisa pero no bloquees.

### 5. Generacion de la vista HTML (complementaria)

Una vez escrito y confirmado `docs/guia-estilos.md`, genera su **vista HTML** complementaria con el skill `booster-docs`. El `.md` es la fuente de verdad; el HTML es solo para consumo humano.

- Invoca `booster-docs` con `docs/guia-estilos.md` como entrada y salida en `docs/html/guia-estilos.html` (crea `docs/html/` si no existe). El script auto-detecta el tipo de documento (`guia-estilos`) y anade dashboard de KPIs, chips y demas elementos visuales.
- Pasa el flag `--open` para que el HTML **se abra automaticamente en el navegador** al terminar el comando. En modo no interactivo (CI/auto o si el usuario pidio no ser interrumpido) omite `--open` y solo informa de la ruta.
- **Degradacion elegante**: si `booster-docs` no esta disponible, avisa de que la vista HTML no se genero y de que puede instalarse el plugin `boosters`, pero **no bloquees** el comando: el `.md` es suficiente para continuar.
- El HTML es parte de la documentacion del repo (se versiona junto al `.md`); no lo anadas a `.gitignore`.
- No regeneres el HTML si el documento quedo pendiente de cambios: hazlo cuando este estable.
- Nunca modifiques el `.md` de origen al generar el HTML.

## Verificacion final

Al terminar, informa:

- Comando AIDD ejecutado (`aidd style-guide`) y fase/paso (2 / 2.3).
- Ruta del documento generado o actualizado (`docs/guia-estilos.md`).
- Ruta de la vista HTML generada (`docs/html/guia-estilos.html`), o aviso si no se pudo generar el HTML.
- **Rutas de los tokens emitidos** (`docs/design/tokens.json` y `docs/design/tokens.css`), y cuantos tokens llevan.
- Si hay design tokens concretos y si la identidad visual es definitiva o provisional.
- Si se ofrecio `aifg capture` y que respondio el usuario, o que el plugin `aifg` no estaba instalado.
- Recordatorio: pendiente de **aprobacion humana**.
- Siguiente paso sugerido: `aidd architecture-proposal` (si no se hizo) y despues `aidd architecture` (arquitectura tecnica definitiva).
- **Como se aprueba**: `python "${CLAUDE_PLUGIN_ROOT}/scripts/stamp_doc.py" --input <documento> --approve "<nombre>"`. Anota la version actual como aprobada, y a partir de ahi el sello distingue tres estados: sin aprobar, aprobada, y **cambiada despues de aprobarse** — que es el que importa.
