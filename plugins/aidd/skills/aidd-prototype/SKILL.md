---
name: aidd-prototype
description: Fase 2 (paso 2.2) del conjunto AIDD (AI Driven Development). Orquesta la implementacion del prototipo mockeado redirigiendo a `booster-ux`, mediante el comando `aidd prototype` (alias `aidd fase 2.2`). No escribe codigo por si mismo. Lee `docs/arquitectura-base-prototipo.md`, identifica las pantallas y flujos clave de la demo y lanza `booster-ux` una vez por pantalla; si `booster-ux` no esta disponible, entrega instrucciones de implementacion manual de la demo. Tras la implementacion recuerda el punto de validacion con cliente y la actualizacion de `docs/cliente-requisitos.md`. Skill puente de planificacion, autonomo del mundo OpenSpec/native-ai-specs y sin auditoria estructurada.
metadata:
  author: NTT DATA Spain GDN-e
  version: "1.0.0"
---

# aidd-prototype (AIDD · Fase 2 · paso 2.2)

Usa este skill cuando el usuario quiera implementar el prototipo descrito en la arquitectura de la demo, o cuando invoque:

- `aidd prototype`
- `aidd fase 2.2`

Tambien cuando pida "implementar la demo", "montar el prototipo", "prototipar las pantallas de la demo" o equivalentes del paso 2.2.

Responde en espanol siempre que sea posible. Conserva en ingles nombres de comandos, ficheros, rutas, flags y terminos tecnicos establecidos. Este `SKILL.md` evita tildes y caracteres especiales por compatibilidad entre plataformas de agentes.

## Que es y por que es un puente

AIDD es un conjunto de skills de **planificacion**, no de desarrollo activo. La implementacion del prototipo es la unica parte de Fase 2 que produce codigo, asi que este skill **no escribe codigo por si mismo**: orquesta el paso y **redirige a `booster-ux`**, el skill de prototipado UX. Asi AIDD mantiene su rol de planificacion y reutiliza el booster especializado en pantallas.

Encaje en el conjunto (proceso descrito en `${CLAUDE_PLUGIN_ROOT}/methodology/native-ai-aidd-sdd.md`, solo lectura):

- Fase 0 — `aidd client-requirements`.
- Fase 1 — `aidd requirements`, `aidd user-stories`, `aidd user-story-details`.
- **Fase 2 — Diseno (AI Architect)**:
  - `aidd prototype-architecture` (2.1): arquitectura del prototipo (`docs/arquitectura-base-prototipo.md`).
  - **`aidd prototype`** (este skill, 2.2): implementacion del prototipo, redirige a `booster-ux`.
  - `aidd style-guide` (2.3): `docs/guia-estilos.md`.
  - `aidd architecture-proposal` (2.3): `docs/propuesta-arquitectura-base.md`.
  - `aidd architecture` (2.4): `docs/arquitectura-base.md`.

No depende de OpenSpec ni escribe auditoria estructurada. La unica dependencia opcional es `booster-ux`; si no esta disponible, este skill ofrece una alternativa manual y AIDD sigue siendo utilizable.

## Rol y objetivo

> Tu objetivo es conseguir una demo mockeada recorrible de punta a punta, delegando el diseno de cada pantalla en `booster-ux`. No disenas la arquitectura (eso fue 2.1) ni produces los documentos de diseno (2.3/2.4): coordinas la construccion de la demo.

Criterio de salida del paso: las pantallas y flujos clave de `docs/arquitectura-base-prototipo.md` estan prototipados (con `booster-ux` o, en su defecto, implementados manualmente) y la demo se puede presentar al cliente.

## Reglas generales

- Trabaja desde la raiz del proyecto del usuario.
- **Entrada principal**: `docs/arquitectura-base-prototipo.md` (paso 2.1). Si no existe, avisa y propon ejecutar antes `aidd prototype-architecture`; sin ella no hay pantallas ni estrategia de mocks que implementar.
- No escribas codigo de aplicacion directamente como parte de este skill. Tu trabajo es **redirigir a `booster-ux`** pantalla a pantalla. Solo si `booster-ux` no esta disponible, entrega al usuario el prompt de implementacion manual y deja que decida.
- **Todo se mockea**: APIs, BD, auth, notificaciones e integraciones. Datos de ejemplo coherentes con el dominio.
- No inventes pantallas que no esten en la arquitectura del prototipo. Si falta detalle, toma la opcion mas simple y registrala.
- Este skill no genera un documento propio. Si procede, anota el estado de implementacion (pantallas hechas/pendientes) al final de `docs/arquitectura-base-prototipo.md` o en el informe final, sin duplicar contenido.

## Flujo del comando `aidd prototype`

### 1. Lectura previa

Lee `docs/arquitectura-base-prototipo.md` (pantallas/endpoints minimos, estrategia de mocks, datos de ejemplo, pasos de implementacion) y, como apoyo, `docs/mapa-historias-usuario.md` y `docs/detalle-historias-usuario.md`.

Extrae la **lista de pantallas o flujos** que componen la demo.

### 2. Comprobacion de `booster-ux`

Comprueba si el skill `booster-ux` esta disponible en el entorno.

- **Disponible**: prepara el plan de prototipado pantalla a pantalla. Confirma con el usuario la lista de pantallas y el orden antes de lanzar nada.
- **No disponible**: avisa de que no se encontro `booster-ux` y ofrece la alternativa manual (seccion 4). No bloquees el paso por esto.

### 3. Redireccion a `booster-ux` (ruta recomendada)

Para cada pantalla de la lista, lanza `booster-ux` una vez:

- Invoca el skill `booster-ux` (su flujo pide sus propios datos: pantalla y tipo de app, audiencia, datos clave, marca de agua NTT DATA, referencia de estilo y formato de salida).
- Aporta a `booster-ux` el contexto del dominio y de la pantalla a partir de la arquitectura del prototipo y del detalle de historias, para que sus preguntas partan de informacion real.
- Si ya existe `docs/guia-estilos.md`, pasala como referencia de estilo a `booster-ux`.
- Procesa una pantalla cada vez; no acumules varias en una sola invocacion.

Lleva la cuenta de pantallas completadas y pendientes y comunicala.

### 4. Alternativa manual (si no hay `booster-ux`)

Si `booster-ux` no esta disponible o el usuario prefiere implementar a mano, entrega este prompt como guia de implementacion (no lo ejecutes como AIDD; es desarrollo activo, fuera del alcance de planificacion):

```prompt
Actua como experto en desarrollo de software y prototipado de producto.
Implementa la demo funcional descrita en docs/arquitectura-base-prototipo.md,
tomando como base docs/mapa-historias-usuario.md y docs/detalle-historias-usuario.md.
- Implementa solo lo necesario para los flujos principales.
- Mockea TODO lo externo: APIs, BD, auth, notificaciones, integraciones.
- Usa datos de ejemplo coherentes con el dominio.
- Si falta detalle funcional, toma la opcion mas simple y documentala.
- La app debe arrancar con un solo comando e incluir un README minimo de arranque.
Entrega: codigo funcional + datos mock + README.
```

### 5. Punto de validacion con cliente (gate humano)

Cuando la demo este lista, recuerda explicitamente al usuario el gate de la metodologia:

- El humano **presenta el prototipo al cliente** y recoge feedback.
- Actualiza `docs/cliente-requisitos.md` con ese feedback.
- **Si hay cambios significativos, se vuelve al paso 1.1 (`aidd requirements`)** y se rehace lo necesario aguas abajo.
- Si el feedback es menor, se continua con `aidd style-guide` y `aidd architecture-proposal`.

## Verificacion final

Al terminar, informa:

- Comando AIDD ejecutado (`aidd prototype`) y fase/paso (2 / 2.2).
- Ruta usada (`booster-ux` por pantalla, o alternativa manual) y pantallas completadas/pendientes.
- Recordatorio del **gate de validacion con cliente** y de la posible vuelta al paso 1.1.
- Siguiente paso sugerido: `aidd style-guide` y `aidd architecture-proposal` una vez incorporado el feedback del cliente.
