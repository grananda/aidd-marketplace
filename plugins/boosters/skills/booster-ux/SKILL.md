---
name: booster-ux
description: Diseña pantallas o prototipos UX como paso previo a su validación. Activar cuando el usuario diga frases como "diseña una pantalla", "quiero crear un prototipo de pantalla", "quiero crear un prototipo ux", "haz un mockup", "esboza la vista de", "necesito un wireframe de", "maqueta el formulario de", "prototipa el dashboard de", o cualquier petición de diseñar, prototipar, esbozar, maquetar o mockupear una pantalla, vista, formulario, listado, dashboard, panel o flujo de UI. Genera dos variantes paralelas (v1 criterio editorial, v2 cumplimiento Web Interface Guidelines) como imagen y HTML navegable. Tras invocarse, pregunta al usuario 6 puntos (pantalla y tipo de aplicación, audiencia/contexto opcional, datos clave opcional, marca de agua NTT DATA, referencia de estilo opcional — URL, HTML local o guía de estilos, y formato de salida opcional), identifica los elementos principales de la pantalla y pide confirmar o corregir su posición antes de generar ambas variantes.
metadata:
  author: NTT DATA — GDN-e Spain Booster
  version: "1.2.0"
---

# booster-ux

Diseña pantallas en dos variantes paralelas con filosofías de diseño contrastadas, para que la validación posterior pueda elegir o sintetizar la mejor.

- **v1 — Criterio editorial (impeccable):** decisiones de diseño justificadas por escena física, OKLCH tinted neutrals, color strategy deliberada, anti-reflejos de categoría.
- **v2 — Cumplimiento (Web Interface Guidelines):** semántica estricta, focus rings visibles, hit targets ≥44px, ARIA, keyboard navigability, contraste AA.

Ambas variantes salen por defecto como **imagen PNG + HTML con Tailwind CSS navegable** (filtrado, ordenación y descarga CSV reales cuando aplique). El usuario puede pedir otros formatos, por ejemplo solo imagen, HTML con Bootstrap o HTML estático.

Este skill es **autónomo**: no depende de que estén instalados otros skills (`impeccable`, `web-design-guidelines`). Toda la filosofía de diseño que necesita está embebida en este archivo.

Control de cambios del skill: [CONTROL-DE-CAMBIOS.md](./CONTROL-DE-CAMBIOS.md)

---

## Paso 1 — Recopilar información del usuario

Pregunta al usuario en un único mensaje, en orden y numerado, los siguientes 6 puntos. **No añadas más preguntas en esta ronda.** Los puntos 2, 3, 4, 5 y 6 son opcionales. Si el usuario deja cualquiera de esos puntos sin responder, no lo repreguntes: aplica directamente el comportamiento por defecto que corresponda.

1. **Pantalla a diseñar** — ¿qué pantalla y para qué tipo de aplicación? Indica si es una pantalla SAP, Android, web, escritorio, intranet, portal cliente, etc. (ej.: "dashboard SAP de seguimiento de proyectos", "formulario Android de alta de cliente", "listado web de tickets con filtros").
2. **Audiencia / contexto (opcional)** — interno NTT DATA, cliente final, mixto, etc. Si el usuario no indica nada en este punto, se asumirá `cliente final`.
3. **Datos clave (opcional)** que deben aparecer — campos, métricas, acciones, navegación lateral, etc. Si el usuario no indica nada en este punto, la IA puede tomar libertad para proponerlos de forma coherente con la pantalla solicitada y la audiencia.
4. **Marca de agua con logo NTT DATA (opcional)** — Sí / No. *(Por defecto: Sí si el usuario no contesta o contesta ambiguo.)*
5. **Referencia de estilo (opcional)** — URL de una página web, ruta a un HTML local (p. ej. `C:/refs/landing.html`) o guía de estilos/design system en la que basar paleta, tipografía, espaciado, componentes y voz visual. Si no indicas nada, se usarán **estilos genéricos** (tokens de marca NTT por defecto: azul ~`#0072CE`, rojo `#DA291C`, fuente Inter / stack del sistema).
6. **Formato de salida (opcional)** — imagen, HTML con Bootstrap, HTML con Tailwind CSS, HTML estático, wireframe Markdown, especificación textual, etc. Si no indicas nada, se generará **imagen PNG + HTML con Tailwind CSS**.

Si en la invocación inicial el usuario ya ha proporcionado alguno o todos estos puntos (por ejemplo a través del propio mensaje), **no los repreguntes**: extrae lo que ya sepas y pregunta solo por lo que falte. Los puntos opcionales no deben bloquear el flujo ni abrir una segunda petición si vienen vacíos. Aplica estas reglas por defecto:

- Punto 2 (`Audiencia / contexto`): si queda vacío o ambiguo, asume `cliente final`.
- Punto 3 (`Datos clave`): si queda vacío o ambiguo, la IA puede proponerlos con criterio propio.
- Punto 4 (`Marca de agua con logo NTT DATA`): si queda vacío o ambiguo, asume `Sí`.
- Punto 5 (`Referencia de estilo`): si queda vacío, asume que no hay referencia y usa estilos genéricos.
- Punto 6 (`Formato de salida`): si queda vacío o ambiguo, asume `imagen PNG + HTML con Tailwind CSS`.

Si el resto de información necesaria ya está, salta directamente al Paso 1.1.

**Directorio de salida:** el usuario puede indicarlo libremente en su mensaje (ej.: "…en `C:/proyectos/foo`", "guárdalo en `./out/listado`", "directorio: `tmp/ux`"). Si lo indica, úsalo tal cual (creando el directorio si no existe). Si no lo indica, **debes pedírselo explícitamente al usuario antes de continuar**. No asumas por defecto el directorio de trabajo actual.

---

## Paso 1.1 — Confirmar estructura y posiciones principales

Tras recibir las respuestas del Paso 1, antes de procesar la referencia de estilo o generar archivos, identifica los **elementos principales** que contendrá la pantalla a partir de la pantalla, audiencia y datos clave indicados por el usuario.

Presenta al usuario una propuesta breve de ubicación y pídele que confirme o indique cambios. No avances al Paso 1.5 hasta tener confirmación explícita o una versión corregida por el usuario.

Formato recomendado:

```
He identificado estos elementos principales y su posición propuesta:

- Menú: vertical a la izquierda
- Logo: arriba a la derecha
- Filtros: franja superior bajo el título
- Tabla principal: centro de la pantalla
- Acciones primarias: arriba a la derecha del área de contenido

Confirma si esta distribución es correcta o indícame la nueva posición de los elementos que quieras cambiar.
```

Reglas:

- Mantén la propuesta concisa: normalmente 4–8 elementos principales.
- No inventes elementos complejos que el usuario no haya pedido; deduce solo estructura necesaria para materializar la pantalla.
- Si `Datos clave` venía vacío, puedes deducir los elementos principales a partir del tipo de pantalla y la audiencia, manteniendo una complejidad razonable.
- Si el usuario ya indicó posiciones concretas en el mensaje inicial, respétalas y pide confirmación solo de la propuesta consolidada.
- Si el usuario responde con cambios parciales, actualiza la lista mental de posiciones y continúa con el flujo.
- Inyecta esta distribución confirmada en ambos prompts como `Estructura y posiciones confirmadas`.
- Si todavía no conoces el directorio de salida, solicita su ruta al usuario en esta fase o inmediatamente después, antes de pasar al Paso 1.5.

---

## Paso 1.5 — Procesar referencia de estilo (si la hay)

Si el usuario indicó una referencia en el punto 5, antes de despachar los agentes extrae un **brief de estilo** que se inyectará a ambas variantes:

- **Si es URL** (`http://…` o `https://…`): usa `WebFetch` para descargar el HTML/CSS y observar paleta, familia tipográfica, ritmo de espaciado, radii, sombras, tono de copy.
- **Si es ruta local** (`.html` / `.htm` con o sin sus assets): usa `Read` sobre el archivo HTML; si tiene CSS externo referenciado, intenta leer también esos ficheros.
- **Si es una guía de estilos o design system** (documento local, enlace, texto pegado o indicación corporativa): extrae los tokens, componentes, reglas de uso, tono visual y restricciones aplicables. Si el documento no es directamente accesible, usa solo la información proporcionada por el usuario.
- **Si falla la descarga o lectura**: avisa al usuario en una línea, continúa con estilos genéricos y deja constancia en el brief inyectado (`Referencia de estilo: solicitada pero no accesible — usar genéricos`).

Sintetiza el brief de estilo en ≤8 líneas con esta estructura:

```
Paleta (3–6 colores con rol: superficie, primario, acento, texto, borde…):
Tipografía (familia principal + secundaria si la hay, pesos típicos):
Ritmo de espaciado (escala detectada o "no clara"):
Radii / sombras / bordes (apuntes):
Voz visual (denso / aireado / editorial / corporativo / lúdico…):
Notas (1–2 elementos distintivos a respetar o evitar):
```

Si el usuario **no** dio referencia, salta este paso: el brief de estilo será literalmente `Referencia de estilo: ninguna — aplicar tokens NTT DATA por defecto (azul ~#0072CE, rojo #DA291C, Inter)`.

> Importante: el brief de estilo orienta paleta/tipografía/voz, pero **no** anula las reglas duras de cada variante. La variante editorial sigue aplicando OKLCH y anti-reflejos; la variante guidelines sigue exigiendo AA, focus visible, hit targets ≥44px, etc. Si la referencia trae prácticas prohibidas (gradient text, glass por defecto, side-stripes…), la variante editorial las descarta; la variante guidelines corrige cualquier violación de accesibilidad.

---

## Paso 2 — Calcular numeración de archivos

Antes de generar nada, calcula el menor entero `N ≥ 1` tal que **ninguno** de estos archivos exista ya en el directorio de salida:

- `index-vN.html`
- `preview-vN.png`
- `index-v(N+1).html`
- `preview-v(N+1).png`

Es decir, el par `(N, N+1)` debe estar libre. Si `index-v1.html` ya existe, prueba `N=2`; si `index-v2.html` también, prueba `N=3`; etc.

- `vN` (el menor) → variante **impeccable** (v1 conceptual)
- `v(N+1)` → variante **Web Interface Guidelines** (v2 conceptual)

---

## Paso 3 — Generar las dos variantes en paralelo

Lanza **dos agentes en paralelo** (un solo mensaje con dos `Agent` tool calls). Cada agente recibe el mismo brief pero aplica una filosofía distinta. Usa `subagent_type: general-purpose`.

### Brief común (incluir en ambos prompts)

Inyecta literalmente las respuestas del usuario:

- Pantalla: `<respuesta 1>`
- Audiencia: `<respuesta 2, o "cliente final" si no se indicó>`
- Datos clave: `<respuesta 3>`
- Marca de agua NTT DATA: `<Sí | No>`
- Formato de salida: `<respuesta 6, o "imagen PNG + HTML con Tailwind CSS" si no se indicó>`
- Estructura y posiciones confirmadas: `<lista confirmada del Paso 1.1>`
- Referencia de estilo: `<brief de estilo del Paso 1.5, o "ninguna — aplicar tokens NTT DATA por defecto">`

### Requisitos comunes de salida (ambas variantes)

- **Stack por defecto**: HTML único autocontenido + Tailwind via Play CDN (`<script src="https://cdn.tailwindcss.com"></script>`) y `tailwind.config = { ... }` inline con tokens. Si el usuario pide Bootstrap, usa Bootstrap vía CDN (`bootstrap.min.css` y `bootstrap.bundle.min.js`) más CSS/JS inline propio para tokens, accesibilidad e interacción. Si pide solo imagen, genera el HTML temporal necesario para renderizar la captura, pero entrega al usuario únicamente la imagen salvo que necesites conservar el HTML como soporte técnico. Si pide varios formatos, genera todos los solicitados manteniendo la numeración `vN`.
- **Tokens visuales**: si hay **referencia de estilo**, usa los colores/tipografía/radii/componentes del brief de estilo como punto de partida (manteniendo las reglas duras de cada variante). Si **no hay referencia**, usa los tokens NTT por defecto: azul ~`#0072CE`, rojo `#DA291C`, fuente Inter / stack del sistema.
- **Estructura**: respeta la distribución confirmada en el Paso 1.1 para la ubicación de menús, logo, cabeceras, filtros, acciones, contenido principal y cualquier otro elemento acordado. Puedes ajustar micro-layout, responsive y espaciado, pero no cambiar posiciones principales sin motivo funcional claro.
- **Navegable**: si la pantalla incluye un listado/tabla, debe tener búsqueda en vivo, ordenación por cabecera y descarga CSV real (UTF-8 BOM, separador `;`, fecha en el nombre). Si es un formulario, los campos deben ser interactivos (no solo `<input>` decorativos: validación HTML5 mínima y feedback de focus). Sidebar y navegación con `aria-current` y estado activo real.
- **Marca de agua**: si el usuario pidió Sí, añadir un patrón sutil con el wordmark "NTT DATA" repetido en diagonal a baja opacidad (≤6%) sobre el fondo del área de contenido principal — usar `background-image: repeating-linear-gradient(...)` con un SVG inline data-URI, o una capa `position: fixed` `pointer-events: none` con el wordmark a `opacity: 0.05` rotado -30°. **Nunca** la marca de agua sobre tablas o controles que pueda dificultar lectura — limitar al fondo y respetar contraste.
- **Idioma**: español (etiquetas, copy, placeholders).
- **Datos de muestra**: 8–10 filas si es listado; valores realistas para el sector indicado.
- **Captura**: full-page PNG a viewport 1440×900 vía Playwright.

### Prompt para variante impeccable (vN)

```
Diseña la pantalla aplicando esta filosofía editorial. El objetivo es una pantalla
con criterio, no una pantalla "segura".

REFERENCIA DE ESTILO:
- Si en el brief llega una referencia de estilo (paleta, tipografía, voz visual),
  úsala como punto de partida para la paleta y la voz, pero CONVIÉRTELA a OKLCH y
  ajusta neutros tintados antes de usarla. Descarta de la referencia cualquier
  patrón que aparezca en las prohibiciones absolutas.
- Si la referencia es "ninguna", aplica criterio editorial libre con tokens NTT
  por defecto (azul ~#0072CE, rojo #DA291C, Inter) reinterpretados en OKLCH.

REGLAS DURAS:
- Color en OKLCH. Nunca #000 ni #fff. Tinta los neutros hacia el hue de marca
  (chroma 0.005–0.01).
- Elige una color strategy deliberada y justifícala: Restrained (neutros + 1
  acento ≤10%), Committed (un color saturado en 30–60% del lienzo), Full palette
  (3–4 roles), o Drenched (la superficie ES el color). Para admin/producto el
  default suele ser Restrained, pero no por reflejo.
- Tema light vs dark: escribe primero una frase de "escena física" (quién usa
  esto, dónde, bajo qué luz, en qué ánimo). Si la frase no fuerza la respuesta,
  añade detalle hasta que lo haga. NUNCA elijas dark "porque queda cool" ni
  light "por seguridad".
- Tipografía: ratio ≥1.25 entre niveles, line-height 1.4–1.5 para body, longitud
  de línea 65–75ch en bloques de texto.
- Espaciado VARIADO. Mismo padding en todo = monotonía.
- Resiste el reflejo de categoría: si alguien adivina paleta y tema solo por el
  dominio ("admin → azul corporativo", "fintech → navy + dorado", "salud → blanco
  + teal"), reformula hasta que no sea evidente.

PROHIBICIONES ABSOLUTAS (si vas a escribir alguna, reescribe el elemento):
- Side-stripe borders (border-left/right >1px coloreado en cards/items/alerts).
- Gradient text (background-clip: text + gradient).
- Glassmorphism por defecto (blur/glass cards decorativos).
- Hero-metric template (número grande + label + stats + acento gradient).
- Identical card grids (cards iguales con icono + heading + texto repetidos).
- Modal como primera idea — agota inline / progresivo antes.
- Em dashes (—) en copy. Usa comas, dos puntos, punto y coma, paréntesis.

ENTREGABLE:
- Un solo archivo HTML autocontenido en {OUTPUT_DIR}/index-vN.html con el stack
  solicitado en el formato de salida (Tailwind por defecto, Bootstrap si se pidió),
  navegable según los requisitos comunes.
- Captura PNG full-page 1440×900 en {OUTPUT_DIR}/preview-vN.png vía:
    npx -y playwright screenshot --full-page --viewport-size=1440,900 \\
      "file:///{OUTPUT_DIR}/index-vN.html" "{OUTPUT_DIR}/preview-vN.png"
  Si Playwright no está instalado: npx -y playwright install chromium
- Notas en {OUTPUT_DIR}/notes-vN.md (≤15 líneas): frase de escena, color
  strategy, tema, top-2 movimientos anti-reflejo, qué es interactivo.

Devuelve un resumen de 5 líneas: escena, strategy + tema, anti-reflejos, navegabilidad.
```

### Prompt para variante Web Interface Guidelines (v(N+1))

```
Diseña la pantalla aplicando rigurosamente las Web Interface Guidelines de Vercel.
El objetivo es una pantalla que pase una auditoría de accesibilidad y semántica
sin observaciones.

PASO PREVIO — Intenta WebFetch a:
  https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md
Si falla (sin red, 404, etc.), aplica el resumen embebido al final de este prompt.

REFERENCIA DE ESTILO:
- Si en el brief llega una referencia de estilo (paleta, tipografía, voz visual),
  úsala como base para tokens visuales, pero verifica y AJUSTA cualquier color
  que no cumpla AA (4.5:1 texto, 3:1 UI). Si la referencia trae focus rings
  invisibles, hit targets pequeños o ARIA mal usado, corrígelo: el cumplimiento
  manda sobre la fidelidad estética.
- Si la referencia es "ninguna", aplica tokens NTT por defecto (azul ~#0072CE,
  rojo #DA291C, Inter) verificados contra AA.

REGLAS DURAS DE CUMPLIMIENTO:
- Semántica primero: <header>, <nav>, <main>, <aside>, <footer>; tablas con
  <caption> (sr-only si decorativo), <thead>/<tbody>, scope="col"/"row".
- Skip-link al inicio, foco visible al activarse.
- Focus rings visibles en TODO control interactivo (:focus-visible con halo
  ≥2px de offset y color ≥3:1 de contraste contra fondo). Nunca outline:none
  sin reemplazo.
- Hit targets ≥44×44 px en links de nav, botones e inputs (incluso en filas
  densas — usa padding interior, no reduzcas el target).
- Jerarquía de headings sin saltos (h1 → h2 → h3, no h1 → h3).
- ARIA solo donde aporta: aria-current en nav activo, aria-live en cambios
  asíncronos (filtros, descarga), aria-label en botones icon-only,
  aria-hidden="true" en iconos decorativos.
- Contraste AA mínimo (4.5:1 texto normal, 3:1 texto grande y elementos UI).
- Tabular-nums en columnas numéricas y de fecha.
- prefers-reduced-motion respetado en cualquier animación.
- Keyboard navigability completa (tab order lógico, esc cierra menús,
  enter/space activan).

ENTREGABLE:
- Un solo archivo HTML autocontenido en {OUTPUT_DIR}/index-v(N+1).html con
  el stack solicitado en el formato de salida (Tailwind por defecto, Bootstrap si
  se pidió), navegable según requisitos comunes.
- Captura PNG full-page 1440×900 en {OUTPUT_DIR}/preview-v(N+1).png vía
  Playwright (igual comando que el otro agente, ajustando ruta).
- Notas en {OUTPUT_DIR}/notes-v(N+1).md (≤15 líneas): top-5 reglas aplicadas,
  decisiones semánticas, qué es interactivo, contraste verificado.

Devuelve un resumen de 5 líneas.

==== RESUMEN EMBEBIDO DE LAS GUIDELINES (fallback si WebFetch falla) ====
Forms: prevent layout shift on validation; submit on Enter; Esc dismisses
errors; auto-focus first invalid field; clear, specific error copy.
Feedback: optimistic UI con rollback claro; toasts no críticos; aria-live
para confirmaciones.
Touch / hit targets: ≥44px área efectiva, espacio entre targets ≥8px.
Focus: :focus-visible obligatorio; foco visible tras navegación SPA; trap de
foco en modales; restaurar foco al cerrar.
Typography: jerarquía clara, mínimo 14px body, line-height ≥1.4.
Color: contraste AA, no usar solo color para transmitir estado.
Motion: respetar prefers-reduced-motion; transiciones <300ms para feedback;
nunca animar layout properties.
Loading: skeletons o placeholders dimensionados (no spinners genéricos);
estados de error y vacío diseñados.
Performance: imágenes con width/height; fonts con font-display: swap;
diferir scripts no críticos.
Semántica: HTML nativo antes que ARIA; ARIA solo donde aporta; landmarks
únicos por página.
=========================================================================
```

Sustituye `{OUTPUT_DIR}` y `vN` / `v(N+1)` por valores concretos antes de despachar cada agente.

---

## Paso 4 — Verificar y reportar

Cuando ambos agentes terminen:

1. Verifica que existen los archivos esperados según el formato solicitado. Por defecto deben existir: `index-vN.html`, `preview-vN.png`, `notes-vN.md`, `index-v(N+1).html`, `preview-v(N+1).png`, `notes-v(N+1).md`. Si el usuario pidió solo imagen u otros formatos, verifica esos entregables y las notas correspondientes.
2. Reporta al usuario un resumen comparativo de máximo 8 líneas: filosofía aplicada en cada variante y diferencia clave entre ambas.
3. Indica siempre qué versión del skill se ha ejecutado, usando la versión declarada en el frontmatter de este archivo. Formato sugerido: `Versión del skill ejecutada: booster-ux 1.2.0`.
4. Añade siempre esta línea: `Puedes comprobar la última versión disponible en https://everisgroup.sharepoint.com/sites/Booster/SitePages/booster-skills.aspx`.
5. **Indica siempre el directorio de salida** donde se han generado los ficheros (ruta absoluta resuelta), incluso si fue el directorio de trabajo por defecto. Formato sugerido: `Directorio de salida: <ruta-absoluta>` como línea destacada al final del reporte, antes del Recommended Next Step.
6. Sugiere como Recommended Next Step: abrir las previews y, si se generó HTML, abrir también los HTML en navegador para validar antes de la fase de validación formal.

---

## Formatos alternativos

El skill genera por defecto **imagen PNG + HTML con Tailwind CSS navegable**. El punto 6 de la pregunta inicial permite que el usuario pida otro formato sin abrir una ronda adicional. Si el usuario pide explícitamente otros formatos en el mensaje inicial, atiende su petición y no lo repreguntes.

Formatos alternativos soportados:

| Formato                       | Cuándo usarlo                                | Salida                                                               |
| ----------------------------- | -------------------------------------------- | -------------------------------------------------------------------- |
| Imagen PNG                    | Preview visual para revisión rápida          | `preview-vN.png`                                                     |
| HTML con Tailwind CSS         | Default si no se indica formato              | `index-vN.html` con Tailwind Play CDN                                |
| HTML con Bootstrap            | Si el usuario lo pide expresamente           | `index-vN.html` con Bootstrap CDN + CSS/JS inline propio             |
| Wireframe ASCII / Markdown    | Esbozo rápido, baja fidelidad                | `wireframe-vN.md` con cajas ASCII y leyenda                          |
| HTML estático (sin navegable) | Solo preview visual, sin interacción         | `index-vN.html` sin JS de filtrado/sort y sin framework CDN si se pide |
| Especificación textual        | Brief para desarrollador o handoff           | `spec-vN.md` con secciones: estructura, tokens, copy, estados, a11y  |
| Captura adicional             | Vistas extra (mobile 390×844, dark mode)     | `preview-vN-mobile.png`, `preview-vN-dark.png`                       |

Si el usuario combina (p.ej. "dame las dos versiones también como wireframe markdown"), genera ambos formatos manteniendo la numeración `vN` consistente.

---

## Reglas de oro del skill

- **Rondas de preguntas controladas**: primero recopila solo los 6 puntos especificados, teniendo en cuenta que `Audiencia / contexto`, `Datos clave`, `Marca de agua`, `Referencia de estilo` y `Formato de salida` son opcionales; después realiza una única confirmación de estructura y posiciones principales. Si falta la ruta de salida, pídela antes de continuar. No repreguntes los campos opcionales vacíos: aplica su valor por defecto. No añadas más rondas salvo bloqueo real o falta de datos imprescindibles.
- **Default Sí** para marca de agua si la respuesta es ambigua o vacía.
- **Default de salida**: imagen PNG + HTML con Tailwind CSS si el formato queda vacío o ambiguo.
- **Numeración estricta**: nunca sobrescribir archivos. Si `vN` existe, incrementar.
- **Variantes en paralelo**, no secuenciales.
- **Idioma de la salida**: español, salvo que el usuario pida otro.
- **No inventar requisitos**: si el usuario dio brief mínimo, no añadas funcionalidades fantasma. Mantén la pantalla a lo pedido + datos de muestra realistas. Excepción: si el punto `Datos clave` quedó vacío, la IA puede completarlo con criterio razonable y coherente con la pantalla y la audiencia.
- **Control de cambios obligatorio**: cada modificación del skill debe reflejarse en `CONTROL-DE-CAMBIOS.md`, incrementando versión, fecha y resumen del cambio.
