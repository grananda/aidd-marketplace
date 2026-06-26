# Análisis del skill `booster-ux` desde la perspectiva de diseño UX

Estado actual: La capacidad actual cubre bien la fase **"esbozar una pantalla aislada con criterio"**, pero deja huecos importantes en lo que un practicante de UX entrega habitualmente. A continuación priorizo las extensiones por impacto.

## Cobertura del recorrido (alta prioridad)

Una app no es una pantalla, es un flujo. Ahora mismo el skill produce siempre una sola pantalla en happy-path desktop, y eso limita su utilidad real.

- **Flujos multi-pantalla** — aceptar un brief tipo "alta de cliente: paso 1 datos, paso 2 firma, paso 3 confirmación" y generar las N pantallas como un set coherente, con navegación clicable entre ellas y un `flow-vN.md` que muestre el journey.
- **Estados completos por pantalla** — empty state, loading/skeleton, error, sin permisos, dataset vacío con CTA de onboarding, success/confirmación. Hoy solo se entrega el estado lleno feliz, donde el UX bueno y el UX malo se distinguen poco.
- **Responsive por defecto** — capturas mobile (390×844), tablet (820×1180) y desktop (1440×900) en cada variante, no como opt-in. La adaptación a mobile suele revelar problemas de jerarquía que en desktop no se ven.
- **Modo claro y oscuro** — generar ambos como entregable estándar, no solo bajo petición. Es relevante para validar contraste real y para clientes con apps duales.
- **Navegación entre pantallas funcional** — links reales entre `index-v1.html` de cada paso para que el revisor pueda recorrer el flujo en navegador.

## Realismo del prototipo (alta prioridad)

Los prototipos se caen en validación cuando los datos son obviamente sintéticos o el copy es genérico.

- **Importar datos reales** — aceptar CSV/JSON con las filas a renderizar (`--data ./tickets.csv`), en lugar de pedir al agente que invente 8–10 filas. Los stakeholders responden distinto cuando ven sus propios nombres de proyecto.
- **Generación de microcopy contextual** — un paso explícito para revisar y reescribir labels, placeholders, mensajes de error y empty states siguiendo principios de UX writing (acción concreta, sin jerga, sin negaciones dobles), no dejarlo al criterio libre del agente generador.
- **Kit de marca completo** — además de URL de referencia, aceptar logo SVG, tokens.json existente, brand guidelines PDF. Hoy hay que confiar en que el agente extraiga bien el estilo de una URL, sin un canal directo para activos del cliente.
- **Datos coherentes por dominio** — generadores específicos para banca (NIF/IBAN/importes), salud (códigos, fechas clínicas), seguros (pólizas), administración pública. Lo "realista para el sector" de hoy es muy genérico.

## Validación automatizada (alta prioridad)

La variante v2 **dice** que cumple guidelines pero no lo **verifica**. Cerrar ese gap eleva enormemente la confianza del entregable.

- **Auditoría de accesibilidad automática** — pasar axe-core o Pa11y sobre cada HTML generado y emitir `audit-vN.md` con violaciones, severidad y recomendación. Hoy v2 es promesa; con audit es prueba.
- **Reporte Lighthouse** — performance, a11y, best practices, SEO sobre los HTML generados, en `lighthouse-vN.json` + resumen.
- **Evaluación heurística (Nielsen 10)** — un agente ligero que recorre las pantallas y emite hallazgos por heurística en `heuristics-vN.md`: visibilidad del estado del sistema, prevención de errores, consistencia, etc.
- **Verificación de contraste explícita** — listado tabular de cada par color-fondo usado con su ratio AA/AAA, no solo "se respeta AA".
- **Verificación de consistencia v1↔v2** — confirmar que ambas variantes usan los mismos textos, los mismos datos y la misma información, para que la elección sea solo de criterio de diseño, no de contenido.

## Iteración y reutilización (media prioridad)

Hoy cada ejecución es un par v(N), v(N+1) nuevo. UX es iterativo, y eso encaja mal.

- **Modo refinamiento** — `"refina v3 cambiando X, Y, Z"` que parta del HTML existente y produzca v5 conservando decisiones previas, sin regenerar desde cero. Evita la regresión que sufre el ciclo actual.
- **Comparativa explícita** — al terminar, generar `compare-vN-v(N+1).html` con ambas variantes lado a lado y `compare-vN-v(N+1).md` con tabla de diferencias clave (paleta, densidad, jerarquía, anti-patrones). Ahorra al stakeholder tener que abrir cuatro pestañas.
- **Extracción de design system** — tras generar la pantalla, emitir `tokens.json`, `components.html` con los átomos/moléculas usados (botones, badges, inputs, cards) para reutilizar en pantallas siguientes con coherencia garantizada.
- **Síntesis post-validación** — un comando "fusiona v1 y v2 quedándote con paleta de v1 y semántica de v2" que produzca v(N+2) como síntesis explícita, en lugar de dejar al usuario hacerlo a mano.

## Contexto de producto (media prioridad)

Las preguntas iniciales capturan el "qué" pero no el "para qué".

- **Persona y job-to-be-done** — pregunta opcional sobre la persona objetivo (rol, expertise, frecuencia de uso) y la tarea que está intentando completar. Cambia decisiones de densidad, agrupación y orden.
- **Restricciones de negocio** — campos obligatorios por compliance, KPIs que la pantalla debe optimizar, integraciones que condicionan campos.
- **Anotaciones sobre el mockup** — overlay con números y leyenda explicando decisiones UX clave (por qué este filtro está aquí, por qué este CTA es secundario), en `annotated-vN.png` además del PNG limpio. Es el formato que mejor funciona en revisiones con stakeholders no técnicos.
- **Mapa del sitio o flow diagram** — en flujos multi-pantalla, un Mermaid o ASCII como `sitemap-vN.md` que muestre el árbol de navegación.

## Handoff a desarrollo (media prioridad)

El `spec-vN.md` actual es opcional y libre. Para handoff real conviene formalizarlo.

- **Especificación estructurada** — secciones fijas: tokens, breakpoints, componentes con props, estados de interacción, validaciones, eventos analíticos esperados, dependencias.
- **Storybook stubs** — exportar cada componente atómico como story aislada navegable, no solo dentro de la pantalla completa.
- **Export a Figma vía plugin o JSON intermedio** — algunos equipos diseñan en Figma y este skill produce HTML; un puente intermedio reduce fricción.

## Inspiración y benchmarking (baja prioridad)

- **Snapshot competitivo** — dada una lista de 2–3 URL de competidores, hacer captura full-page de cada una y generar `moodboard.md` con observaciones (paleta, densidad, patrones) como input al diseño. Útil al inicio de proyectos cliente.

---

Si tuviera que elegir las **tres extensiones de mayor leverage** para el flujo NTT DATA, serían: estados completos por pantalla, auditoría a11y automática sobre v2, e importación de datos reales vía CSV/JSON. Cubren los tres puntos donde un prototipo se cae frente al cliente — falta de realismo, promesa de cumplimiento sin verificación, y datos ficticios que invitan a discutir el contenido en lugar del diseño.

**Recommended Next Step:** validar esta lista con dos o tres usuarios reales del skill dentro de NTT DATA (preguntándoles qué entregables tienen que rehacer a mano tras cada generación) antes de priorizar implementación, y someter cualquier extensión que use IA generativa (auditoría automática, microcopy, datos sintéticos) al proceso interno de gobierno de IA antes de despliegue. La revisión humana sigue siendo necesaria sobre cualquier output generado.

---

# Listado de tareas TODO

## Top 3 leverage (empezar por aquí)

- [ ] Generar estados completos por pantalla: empty, loading/skeleton, error, sin permisos, dataset vacío con CTA, success. Salida `index-vN-state-<estado>.html` + `preview-vN-state-<estado>.png`.
- [ ] Auditoría de accesibilidad automática sobre cada HTML (axe-core o Pa11y) → `audit-vN.md` con violaciones, severidad y recomendación.
- [ ] Importación de datos reales vía CSV/JSON (`--data ./tickets.csv`) en lugar de inventar filas; validar mapeo a columnas declaradas en datos clave.

## Cobertura del recorrido (alta prioridad)

- [ ] Soporte de flujos multi-pantalla: brief tipo "paso 1 / paso 2 / paso 3" que produzca un set coherente de N pantallas.
- [ ] Generar `flow-vN.md` con el journey y enlazar `index-vN-paso<k>.html` entre sí (navegación clicable real).
- [ ] Capturas responsive por defecto en cada variante: mobile 390×844, tablet 820×1180, desktop 1440×900.
- [ ] Modo claro y oscuro como entregable estándar (no opt-in): `preview-vN-light.png` y `preview-vN-dark.png`.

## Realismo del prototipo (alta prioridad)

- [ ] Paso explícito de revisión de microcopy (labels, placeholders, errores, empty states) bajo principios de UX writing.
- [ ] Aceptar kit de marca completo: logo SVG, `tokens.json` existente, brand guidelines PDF, además de la URL de referencia.
- [ ] Generadores de datos por dominio (banca: NIF/IBAN/importes; salud: códigos clínicos; seguros: pólizas; administración pública).

## Validación automatizada (alta prioridad)

- [ ] Reporte Lighthouse (performance / a11y / best practices / SEO) → `lighthouse-vN.json` + resumen en `audit-vN.md`.
- [ ] Evaluación heurística Nielsen 10 → `heuristics-vN.md` con hallazgos por heurística.
- [ ] Tabla explícita de contraste por par color-fondo con ratio AA/AAA en `audit-vN.md`.
- [ ] Verificación de consistencia v1↔v2: mismos textos, mismos datos, misma información. Diff automático si divergen.

## Iteración y reutilización (media prioridad)

- [ ] Modo refinamiento: `refina vN cambiando X, Y, Z` que parta del HTML existente y conserve decisiones previas.
- [ ] Comparativa automática al terminar: `compare-vN-v(N+1).html` lado a lado + `compare-vN-v(N+1).md` con tabla de diferencias clave.
- [ ] Extracción de design system: emitir `tokens.json` y `components.html` con átomos/moléculas usados.
- [ ] Comando de síntesis post-validación: "fusiona v1 y v2 quedándote con paleta de v1 y semántica de v2" → v(N+2).

## Contexto de producto (media prioridad)

- [ ] Pregunta opcional sobre persona objetivo (rol, expertise, frecuencia de uso) y job-to-be-done.
- [ ] Pregunta opcional sobre restricciones de negocio: campos obligatorios por compliance, KPIs a optimizar, integraciones.
- [ ] Generar `annotated-vN.png` con overlay numerado y leyenda de decisiones UX clave, además del PNG limpio.
- [ ] Para flujos multi-pantalla: `sitemap-vN.md` (Mermaid o ASCII) con árbol de navegación.

## Handoff a desarrollo (media prioridad)

- [ ] Plantilla estructurada de `spec-vN.md` con secciones fijas: tokens, breakpoints, componentes con props, estados de interacción, validaciones, eventos analíticos, dependencias.
- [ ] Exportar Storybook stubs por componente atómico (no solo la pantalla completa).
- [ ] Puente de export a Figma vía plugin o JSON intermedio.

## Inspiración y benchmarking (baja prioridad)

- [ ] Snapshot competitivo: dada una lista de 2–3 URL de competidores, capturar full-page y generar `moodboard.md` con observaciones (paleta, densidad, patrones).

## Gobierno y validación interna (transversal, antes de desplegar)

- [ ] Validar la lista con 2–3 usuarios reales del skill en NTT DATA (qué entregables rehacen a mano tras cada generación).
- [ ] Someter cualquier extensión generativa (auditoría automática, microcopy, datos sintéticos) al proceso interno de gobierno de IA antes de despliegue.
- [ ] Mantener disclaimer de revisión humana obligatoria sobre cualquier output generado.
