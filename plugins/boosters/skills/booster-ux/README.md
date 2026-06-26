# booster-ux

Skill para **diseñar pantallas como paso previo a su validación**. Genera dos variantes paralelas con filosofías de diseño contrastadas, para que en la fase de validación se pueda elegir o sintetizar la mejor.

## Para qué sirve

- **v1 — Criterio editorial:** decisiones de diseño justificadas (escena física, paleta deliberada, anti-reflejos de categoría). Pantalla con personalidad.
- **v2 — Cumplimiento estricto:** semántica HTML, focus rings, hit targets ≥44px, ARIA, contraste AA. Pantalla que pasa auditoría sin observaciones.

Ambas salen por defecto como **imagen PNG + HTML con Tailwind CSS navegable** (búsqueda en vivo, ordenación, descarga CSV real cuando aplique). También puede generar HTML con Bootstrap u otros formatos si se pide.

## Cómo invocarlo

Basta con pedírselo en lenguaje natural. Ejemplos que activan el skill:

- "Diseña una pantalla"
- "Diseña una pantalla de listado de proyectos"
- "Quiero crear un prototipo de pantalla"
- "Quiero crear un prototipo UX"
- "Haz un mockup de…"
- "Esboza la vista de…"
- "Necesito un wireframe de…"
- "Maqueta el formulario de…"
- "Prototipa el dashboard de…"
- "/booster-ux" (si lo tienes pinned como comando)

Tras la invocación, el skill te pregunta 6 cosas en un único mensaje:

1. **Pantalla a diseñar** — qué pantalla y para qué tipo de aplicación: SAP, Android, web, escritorio, intranet, portal cliente, etc. Ej.: "listado SAP de proyectos", "alta Android de cliente", "dashboard web de tickets".
2. **Audiencia / contexto (opcional)** — interno NTT DATA, cliente final, mixto… Por defecto: cliente final.
3. **Datos clave (opcional)** — campos, métricas, acciones, navegación. Si no se indican, el skill puede proponerlos con criterio.
4. **Marca de agua NTT DATA** — Sí/No (por defecto Sí).
5. **Referencia de estilo (opcional)** — URL de una página web, ruta a un HTML local (p. ej. `C:/refs/landing.html`) o guía de estilos/design system en la que basar paleta, tipografía, componentes y voz visual. Si no indicas nada, se usan **estilos genéricos** (tokens NTT por defecto).
6. **Formato de salida (opcional)** — imagen, HTML con Bootstrap, HTML con Tailwind CSS, HTML estático, wireframe Markdown, especificación textual, etc. Por defecto: imagen PNG + HTML con Tailwind CSS.

Si en tu mensaje inicial ya das algunos de estos datos, el skill no los repregunta. Si das todos los datos y el directorio de salida, el skill pasa directamente a confirmar la estructura y posiciones principales antes de generar.

> La referencia de estilo orienta paleta/tipografía/voz, pero no anula las reglas duras: la variante editorial sigue aplicando OKLCH y anti-reflejos; la variante guidelines sigue exigiendo AA, focus visible y hit targets ≥44px.

### Directorio de salida (opcional)

Puedes indicarlo libremente en tu mensaje. Ejemplos válidos:

- "Diseña una pantalla de login y guárdalo en `C:/proyectos/foo/ux`"
- "Quiero un prototipo de dashboard, salida en `./out/dashboard`"
- "Diseña el formulario de alta. directorio: `tmp/clientes`"

Si no lo indicas, el skill debe pedírtelo antes de generar. Al terminar, **siempre** te dirá la ruta absoluta donde dejó los archivos.

## Qué obtienes

En el directorio de salida elegido:

```text
index-v1.html      ← variante editorial, navegable
preview-v1.png     ← captura full-page 1440×900
notes-v1.md        ← decisiones de diseño y trade-offs
index-v2.html      ← variante guidelines, navegable
preview-v2.png     ← captura full-page 1440×900
notes-v2.md        ← reglas aplicadas y verificaciones
```

Los archivos no se sobrescriben nunca. Si ya existen `v1` y `v2`, la siguiente ejecución crea `v3` y `v4`, y así sucesivamente.

## Pedir otros formatos

El skill pregunta por formato en la primera ronda, pero es opcional. Por defecto genera imagen PNG + HTML con Tailwind CSS. Si quieres otra cosa, dilo en tu mensaje o en esa respuesta:

- "…solo imagen" → `preview-vN.png`
- "…HTML con Tailwind CSS" → `index-vN.html` con Tailwind Play CDN
- "…HTML con Bootstrap" → `index-vN.html` con Bootstrap CDN
- "…también dame un wireframe en markdown" → `wireframe-vN.md`
- "…solo HTML estático sin JS" → versión sin filtrado/sort
- "…añade una especificación textual para el desarrollador" → `spec-vN.md`
- "…captura también en mobile 390×844" → `preview-vN-mobile.png`
- "…y una versión dark" → `preview-vN-dark.png`

Puedes combinarlos: "Dame las dos versiones y un wireframe markdown de cada una".

## Ejemplos de uso

**Mínimo:**

```text
Diseña una pantalla
```

→ El skill te pregunta los 6 puntos y genera v1+v2.

**Brief completo en una línea:**

```text
Diseña un listado de tickets con filtros para clientes externos, columnas
título, prioridad, estado, fecha, asignado, y botón de exportar. Sin marca
de agua.
```

→ El skill solo pedirá lo que falte, incluido el directorio de salida si no lo has indicado, y confirmará la estructura antes de generar.

**Con formato extra:**

```text
Diseña un formulario de alta de cliente para uso interno NTT DATA.
Campos: razón social, NIF, sector, contacto, email, teléfono.
También dame la especificación textual para el equipo de desarrollo.
```

→ Genera PNG + HTML con Tailwind CSS de las dos variantes + `spec-v1.md` + `spec-v2.md`, salvo que hayas pedido otro stack.

## Filosofía detrás de cada variante

**v1 — Editorial.** Aplica reglas de criterio: color en OKLCH, neutros tintados, color strategy explícita (Restrained/Committed/Full palette/Drenched), tema light/dark decidido por escena física concreta, no por reflejo de categoría. Prohíbe absolutos: side-stripe borders, gradient text, glassmorphism por defecto, hero-metric template, identical card grids, modal-first, em dashes en copy.

**v2 — Cumplimiento.** Aplica las Web Interface Guidelines (Vercel): semántica primero, skip links, focus visible, hit targets, ARIA donde aporta, contraste AA, jerarquía de headings, tabular-nums, prefers-reduced-motion, keyboard navigability. Si hay red disponible, descarga las guidelines actualizadas; si no, usa el resumen embebido.

## Autonomía

El skill **no depende** de tener instalados los skills `impeccable` ni `web-design-guidelines`. Toda la filosofía está embebida en `SKILL.md`.

## Estructura

```text
booster-ux/
├── SKILL.md     ← workflow y filosofía
└── README.md    ← este archivo
```

## Recommended Next Step

Tras la generación, abre las dos PNG y, si se generó HTML, los dos HTML en navegador. Comprueba filtro, ordenación y descarga CSV cuando aplique. El reporte final indicará la versión del skill ejecutada y el enlace para comprobar la última versión disponible: https://everisgroup.sharepoint.com/sites/Booster/SitePages/booster-skills.aspx
