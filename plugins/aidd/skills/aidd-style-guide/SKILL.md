---
name: aidd-style-guide
description: Fase 2 (paso 2.3) del conjunto AIDD (AI Driven Development). Genera la guia de estilos del producto, mediante el comando `aidd style-guide` (alias `aidd fase 2.3 estilos`). Actua como experto en diseno de producto y sistemas de diseno que lee `docs/detalle-historias-usuario.md` y la referencia visual o de marca y genera `docs/guia-estilos.md` con principios de diseno y UX, paleta de colores con valores hex, tipografia, espaciado, iconografia, design tokens CSS concretos, componentes base y pautas de uso, reglas de responsive y accesibilidad WCAG 2.1 AA, y estructura de pantallas y criterios de navegacion. Si el usuario lo indica, ofrece extraer la identidad visual de un diseno en Figma (via el MCP `figma-developer-mcp` con token, API REST o export de design tokens a JSON). Paso del Diseno (AI Architect), complementario a la propuesta de arquitectura. Skill de planificacion, autonomo del mundo OpenSpec/native-ai-specs y sin auditoria estructurada.
metadata:
  author: NTT DATA Spain GDN-e
  version: "1.0.0"
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

Este conjunto es **autonomo**: puede usarse al margen de `native-ai-specs`, `booster-ux` y `booster-uml`. No depende de OpenSpec ni escribe auditoria estructurada. Las decisiones se registran de forma ligera dentro del propio documento generado.

Como complemento opcional, al final del comando se genera una **vista HTML** de la guia de estilos con `booster-docs` (ver el paso final del flujo). El `.md` sigue siendo la **unica fuente de verdad**; el HTML es solo para consumo humano y no altera el flujo AIDD si `booster-docs` no esta instalado.

> Este skill y `aidd architecture-proposal` cubren juntos el paso 2.3 de la metodologia (guia de estilos + propuesta de arquitectura). Se separan en dos skills para mantener cada invocacion enfocada; pueden ejecutarse en cualquier orden.

## Rol y objetivo

> Actua como experto en diseno de producto, sistemas de diseno y arquitectura frontend. Tu objetivo es definir la guia de estilos del producto a partir del detalle de historias y de la identidad visual o de marca indicada. Es la base visual para el AI Lead y los AI Developers.

Criterio de salida del paso: existe `docs/guia-estilos.md` con design tokens CSS concretos (no descripciones vagas), paleta, tipografia, componentes base y reglas de accesibilidad WCAG 2.1 AA. Lo que falte de identidad visual se marca como pendiente; no inventes una marca.

## Reglas generales

- Trabaja desde la raiz del proyecto del usuario.
- **Entrada principal**: `docs/detalle-historias-usuario.md` (Fase 1) y la **referencia visual / marca** que aporte el usuario (URL, guia de marca, HTML, capturas o un **diseno en Figma**). Si no hay referencia visual, preguntala o marca esa parte como pendiente.
- Si el usuario tiene el diseno en **Figma**, ofrece extraer de ahi la identidad visual (paleta, tipografia, espaciado, tokens) en lugar de inferirla. No inventes valores que puedas extraer del diseno real. Ver "Extraccion desde Figma".
- Si ya existe un prototipo implementado (paso 2.2), usalo como fuente de pistas visuales, pero la guia manda sobre el prototipo.
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

Ejecuta este paso solo si el usuario confirma que quiere extraer la identidad visual de un diseno en Figma. El objetivo es obtener valores reales (colores hex, tipografia, escalas de espaciado, tokens) en vez de inferirlos. Propon los metodos en este orden y usa el primero que el usuario pueda aplicar; explicale como hacerlo:

1. **MCP `figma-developer-mcp` (Framelink) — recomendado.** Servidor MCP de la comunidad que se ejecuta por npx, **lee los archivos desde la web** a partir de un enlace de Figma y se autentica con un **Figma API token** (personal access token). No requiere la app de escritorio.
   - Requisitos: el usuario necesita Node/npx y un personal access token de Figma (Settings / Account / Personal access tokens, con permiso de lectura de archivos).
   - Para anadirlo a Claude Code (stdio), pasando el token por el flag `--figma-api-key` (el token de Figma empieza por `figd_`):
     ```
     claude mcp add figma-developer-mcp -- npx -y figma-developer-mcp --figma-api-key=figd_XXXX --stdio
     ```
   - **Seguridad del token**: el token quedara guardado en la config del MCP. Usa scope de usuario (no un `.mcp.json` de proyecto commiteado), y avisa de que **no debe subirse al repo**. No escribas el token en la guia ni en ningun documento generado.
   - Ofrece ejecutar el comando `claude mcp add` por el usuario solo si te da el token y lo confirma; si no, dejale el comando para que lo ejecute el.
   - Pide al usuario el **enlace al archivo, frame o grupo** de Figma (Copy link). El servidor obtiene del enlace los metadatos de layout y estilo via el API token.
   - Comprueba si hay herramientas MCP de `figma-developer-mcp` disponibles (busca con la herramienta de descubrimiento de MCP) y usalas para leer colores, tipografia, espaciado y propiedades del nodo enlazado.

2. **API REST de Figma (sin MCP).** Alternativa directa con el mismo tipo de token, si el usuario prefiere no instalar el MCP.
   - Pide el **file key** de la URL (`figma.com/file/<file_key>/...` o `figma.com/design/<file_key>/...`) y el personal access token. Aplica las mismas reglas de seguridad del token (no commitear, usar `FIGMA_API_KEY` en memoria).
   - Consulta `GET https://api.figma.com/v1/files/{file_key}` y `.../styles` con la cabecera `X-Figma-Token`. Extrae colores, estilos de texto y espaciado.

3. **Export de design tokens a JSON (plugin).** Alternativa sin token ni MCP.
   - Indica al usuario: usar un plugin de Figma (por ejemplo Tokens Studio o "Design Tokens") para exportar los tokens (color, tipografia, espaciado) a un JSON.
   - Pide la **ruta del JSON exportado** y leelo para mapear los tokens a la guia.

Notas:
- Si ningun metodo es viable (sin token, sin Node, sin plugin), continua con la referencia visual que haya aportado el usuario (URL, capturas, marca) y registra en el documento que los valores no se extrajeron de Figma.
- Anota en la seccion de decisiones del documento que la identidad visual se extrajo de Figma y por que metodo.

### 4. Generacion de `docs/guia-estilos.md`

Genera (o actualiza) `docs/guia-estilos.md` con esta estructura:

```markdown
# Guia de estilos — <nombre del proyecto>

> Documento de Fase 2 (AIDD · paso 2.3). Generado por `aidd style-guide`.
> Entrada: docs/detalle-historias-usuario.md + referencia visual/marca.
> Pendiente de aprobacion humana.

## 1. Principios de diseno y UX
- Principios rectores y tono de la interfaz.

## 2. Paleta de colores
- Valores hex por rol (primario, secundario, superficie, estados, etc.).

## 3. Tipografia, espaciado e iconografia
- Familias y escalas tipograficas, escala de espaciado, set de iconografia.

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
- Marca como provisional todo lo que dependa de una identidad de marca aun no aportada.
- La seccion 8 sustituye a la auditoria estructurada e incluye decisiones resueltas por default.

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
- Si hay design tokens concretos y si la identidad visual es definitiva o provisional.
- Recordatorio: pendiente de **aprobacion humana**.
- Siguiente paso sugerido: `aidd architecture-proposal` (si no se hizo) y despues `aidd architecture` (arquitectura tecnica definitiva).
