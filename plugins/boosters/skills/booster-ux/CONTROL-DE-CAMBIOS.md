# Control de cambios de `booster-ux`

Este documento registra los cambios funcionales del skill y debe actualizarse en cada modificación relevante.

## Criterios de registro

- Incrementar la versión del skill en `SKILL.md` cuando el cambio lo requiera. Para ajustes menores o correcciones puntuales puede mantenerse la misma versión, siempre que el cambio quede registrado aquí.
- Añadir la fecha en formato `YYYY-MM-DD`.
- Resumir qué cambia y, si aplica, por qué.
- Registrar solo cambios funcionales o de comportamiento, no ediciones triviales de formato.

## Historial

### 1.2.0 - 2026-05-11

- La pregunta `Pantalla a diseñar` pide también el tipo de aplicación objetivo, por ejemplo SAP, Android, web, escritorio, intranet o portal cliente.
- La `Referencia de estilo` acepta explícitamente URL, ruta a HTML local o guía de estilos/design system.
- Se añade la pregunta opcional `Formato de salida`; si queda vacía o ambigua, el skill genera imagen PNG + HTML con Tailwind CSS.
- El reporte final debe indicar la versión del skill ejecutada y enlazar la página de consulta de última versión en SharePoint.

### 1.1.0 - 2026-05-08

- Ofrecer al usuario la posibilidad de basarse en una página web o html base.
- Se pedirá confirmación al usuario (o posibilidad de cambiar) la distribución de los elementos principales de la pantalla.
- Si el usuario no indica ruta de salida, el skill debe pedirla explícitamente antes de generar los entregables.
- Se permite registrar ajustes menores en este histórico sin subir versión, siempre que queden documentados.
- Si el usuario no aporta contenido en `Datos clave`, la IA puede completarlo con criterio propio de forma coherente con la pantalla y la audiencia.
- `Datos clave` pasa a tratarse explícitamente como un campo opcional dentro del flujo de preguntas.
- `Audiencia / contexto` pasa a ser opcional y, si no se informa, el skill asume `cliente final`.
- Los campos opcionales de la primera ronda no se repreguntan si el usuario los deja vacíos; el skill aplica directamente su comportamiento por defecto.

### 1.0.0 - 2026-05-07

- Versión inicial del skill `booster-ux`.
- Generación de dos variantes paralelas de pantalla en HTML + Tailwind con captura PNG.
- Flujo basado en recogida de contexto, referencia de estilo opcional y generación comparativa.
