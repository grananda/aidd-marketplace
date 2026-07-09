---
name: aidd-hu-review-plan
description: Fase 1.4 (opcional) del conjunto AIDD (AI Driven Development), capa de planificacion de la revision de historias de usuario. Genera un fichero Excel (.xlsx) de planificacion consolidando `docs/mapa-historias-usuario.md` y `docs/detalle-historias-usuario.md`, mediante el comando `aidd hu-review-plan` (alias `aidd planificacion revision hu`, `aidd revision historias`). Produce cuatro pestañas — "Detalle HU" (todas las HU combinadas, con las palabras Como/quiero/para resaltadas en negrita), "Dashboard" (KPIs y graficas: HU pendientes de cerrar, bloqueadas, por fase/persona/prioridad), "Leyenda" (significado de campos codificados como Persona P1/P5 o GAP) y "Gantt Julio" (planificacion de la revision de HU: kickoff, semana 1 de revision de documentacion del cliente y resto del mes de reuniones funcionales con negocio y tecnicas con TI, con detalle por HU). El `.md` de plan sigue siendo la fuente de verdad; el Excel es el entregable rico. Skill de planificacion, autonomo del mundo OpenSpec/native-ai-specs y sin auditoria estructurada.
metadata:
  author: NTT DATA Spain GDN-e
  version: "1.0.0"
---

# aidd-hu-review-plan (AIDD · planificacion de la revision de HU · Excel)

Usa este skill cuando el usuario quiera un **plan (en Excel) para revisar y cerrar las historias de usuario** con negocio y TI, o cuando invoque:

- `aidd hu-review-plan`
- `aidd planificacion revision hu`
- `aidd revision historias`

Tambien cuando pida "excel de planificacion de HU", "gantt de revision de historias", "cuadro de mando de HU", "planning de revision de las historias de usuario" o equivalentes.

Responde y documenta en espanol siempre que sea posible. Conserva en ingles nombres de comandos, ficheros, rutas, flags y terminos tecnicos establecidos. Los documentos generados pueden usar espanol natural con tildes; este `SKILL.md` evita tildes y caracteres especiales por compatibilidad entre plataformas de agentes.

## Que es AIDD y donde encaja este skill

AIDD (AI Driven Development) es un conjunto de skills de planificacion y arquitectura asistida por IA. Cada skill cubre una fase o paso del proceso descrito en `${CLAUDE_PLUGIN_ROOT}/methodology/native-ai-aidd-sdd.md` (referencia de metodologia, solo lectura):

- Fase 0 — `aidd client-requirements`.
- Fase 1 — Definicion (AI Architect): `aidd requirements`, `aidd user-stories`, `aidd user-story-details`.
- **Este skill — planificacion de la revision de HU**: una vez existe el detalle de historias, planifica **como revisarlas y cerrarlas** con negocio/TI y lo entrega en Excel. Es una capa de gestion sobre la Definicion, previa (o paralela) al Diseno de la Fase 2. No sustituye a `aidd project-plan` (recursos) ni a `aidd sprint-planning` (sprints de desarrollo): aquellos planifican la **construccion**; este planifica la **validacion de las HU**.
- Fase 2 — Diseno; Fase 3.5 — Entrega (`aidd project-plan`, `aidd sprint-planning`).

Este skill es **autonomo**: no depende de OpenSpec ni escribe auditoria estructurada. Las decisiones se registran de forma ligera dentro del `.md` de plan generado.

> Relacion con el resto de la capa Delivery: `sprint-planning` reparte los **changes/HU en sprints de desarrollo** (el CUANDO se construye); este skill planifica el **antes**: las reuniones de definicion/validacion para dejar las HU cerradas y listas para construir.
>
> **Antesala de la planificacion de sprints y personas en Jira.** El `docs/plan-revision-hu.md` que genera este skill es un **insumo directo de `aidd sprint-planning`**: aquel lo lee para no planificar por libre — solo compromete en sprint las HU que la revision haya dejado **cerradas/validadas**, reutiliza las **personas/perfiles** implicadas en la revision para asignar el sprint y, en el volcado a Jira, el **assignee** de cada Story. Deja por tanto el `tipo_revision`, el estado de cada HU y la persona responsable bien reflejados: son lo que consume la siguiente etapa.

## Rol y objetivo

Actua con este rol durante todo el comando:

> Actua como analista funcional / delivery lead que prepara la campania de revision de las historias de usuario con el cliente. Tu objetivo es (1) consolidar toda la informacion de las HU en un unico Excel navegable con cuadro de mando, y (2) planificar en un Gantt las reuniones necesarias para revisar y cerrar cada HU dentro del periodo objetivo, separando revision funcional (negocio) de revision tecnica (TI). No inventas historias ni cambias su contenido; las consolidas y planificas su revision.

Criterio de salida: existe `docs/plan-revision-hu.md` (fuente de verdad, con el consolidado, la leyenda y el calendario de revision), su manifiesto `docs/plan-revision-hu.json` y el entregable `docs/xlsx/plan-revision-hu.xlsx` con las cuatro pestañas. Cada HU del detalle aparece consolidada y planificada; lo que no se pueda concluir queda como supuesto explicito.

## Reglas generales

- Trabaja desde la raiz del proyecto del usuario.
- **Entradas / fuentes de verdad**: `docs/mapa-historias-usuario.md` (personas/roles, fases F0/F1/F2, MoSCoW, backbone, ref RF) y `docs/detalle-historias-usuario.md` (historia Como/quiero/para, prioridad, estimacion XS/S/M/L/XL, criterios de aceptacion con los imprescindibles marcados, notas/dependencias). Apoyate en `docs/requisitos.md` solo si necesitas desambiguar un RF.
- Si falta `docs/detalle-historias-usuario.md`, avisa y propon generarlo antes con `aidd user-story-details` (Fase 1.3); sin el detalle no hay HU que consolidar.
- **Lee primero, pregunta despues.** No preguntes lo que los dos documentos ya resuelven.
- **No inventes contenido de las HU** ni semantica de campos codificados. Si un documento usa campos propios del cliente (por ejemplo `Persona` con codigos P1/P5, o `GAP`), **detecta los valores distintos** y llevalos a la pestaña Leyenda con el significado **en blanco** para que lo complete el humano, salvo que el significado este escrito en los documentos. Nunca inventes que significa un GAP o una Persona.
- **Tolerancia de formato**: los documentos reales pueden traer columnas o campos adicionales fuera de la plantilla AIDD estandar. Mapea lo que exista al esquema del manifiesto (abajo); lo que no exista se deja vacio. No descartes una HU por que le falte un campo.
- **El `.md` es la fuente de verdad**; el `.xlsx` es un entregable complementario para consumo humano (dashboard, graficas, gantt, negrita en celda) que **no** se puede versionar como texto. Ante cualquier discrepancia, prevalece el `.md`.
- No sobrescribas un `docs/plan-revision-hu.md` existente sin avisar: leelo, propon los cambios y confirma.
- Este entregable requiere aprobacion humana. Al terminar, deja claro que esta pendiente de revision.

## Flujo del comando `aidd hu-review-plan`

### 1. Recopilacion de contexto (lectura previa)

Lee y consolida `mapa-historias-usuario.md` y `detalle-historias-usuario.md`. Para **cada HU** extrae, en la medida en que exista: id, fase (F0/F1/F2), persona/rol, epica o actividad del backbone, el "Como / quiero / para" desglosado en sus tres partes, prioridad, MoSCoW, estimacion XS/S/M/L/XL, estado (si el documento lo indica; si no, "Pendiente"), marca de bloqueada (una dependencia o decision sin resolver que impide avanzar la HU; un impedimento real, no la mera existencia de criterios imprescindibles), campos codificados propios del cliente (Persona, GAP...), ref RF, criterios de aceptacion (Dado/Cuando/Entonces), notas tecnicas y dependencias.

Registra los **valores distintos** de los campos codificados (Persona, GAP, Estado y cualquier otro con codigos) para construir la Leyenda.

### 2. Pre-flight de preguntas

Resuelve solo lo imprescindible para poder planificar la revision.

1. Cubre, como minimo: **fecha de kickoff** y **periodo objetivo** de cierre de las HU (por defecto el mes en curso / el que indique el usuario); **numero de reuniones por semana** para revision de HU (por defecto **3**); **cuantas HU se revisan por reunion** (agrupacion; por defecto agrupa varias HU logicamente relacionadas por reunion); y si mantiene la separacion **funcional (negocio) / tecnica (TI)** (por defecto si).
2. Clasifica cada hueco en **bloqueante**, **preferencia** o **confirmacion**.
3. No preguntes lo que los documentos ya resuelven (fases, dependencias, tipo de revision si se deduce de la HU).
4. Presupuesto de preguntas: maximo **7** por ejecucion. Prioriza bloqueantes y agrupa relacionadas.
5. Formato: si la plataforma soporta preguntas estructuradas (por ejemplo `AskUserQuestion`), usalo con 2-4 opciones y marca una como `(Recomendada)`; si no, lista numerada con recomendacion.
6. Modo no interactivo: toma los defaults (kickoff = primer lunes del periodo objetivo; 3 reuniones/semana; separacion funcional/tecnica; periodo = mes en curso) y registralos como supuestos.
7. Si el usuario aplaza una duda, registrala como supuesto y continua.

### 3. Planificacion de la revision (el Gantt)

Construye el calendario de revision con estas reglas. **Toda la inteligencia de planificacion se hace aqui** (en el skill); el script solo la renderiza.

**Estructura del periodo:**

1. **Kickoff** en la fecha indicada (por defecto la que de el usuario; si no, el primer lunes del periodo).
2. **Semana 1** (desde el kickoff hasta el fin de esa semana laboral): una unica actividad **"Revision documentacion cliente"** (tipo `doc`), sin desglose por HU. Es la revision de la documentacion que ha facilitado el cliente.
3. **Resto del periodo**: actividad **"Definicion y validacion de las historias de usuario"**, **desglosada por HU**. Aqui esta el detalle que el usuario pide: cada HU (o grupo de HU) se planifica en una reunion concreta.

**Reglas de la agenda de HU:**

- **Cadencia**: por defecto **3 reuniones por semana** (parametrizable). Reparte las reuniones en dias laborables separados (por ejemplo lunes / miercoles / viernes); no pongas reuniones en fin de semana.
- **Separacion funcional / tecnica**: cada HU tiene un `tipo_revision` (`funcional`, `tecnica` o `ambas`). Las reuniones **funcionales** revisan las HU con negocio; las **tecnicas**, con TI. Una HU `ambas` aparece en una reunion funcional y en una tecnica. Deriva el tipo del contenido de la HU (reglas de negocio/UX -> funcional; habilitadores, integraciones, esquema de datos, NFR -> tecnica) cuando el documento no lo indique explicitamente.
- **Varias HU por reunion**: agrupa varias HU relacionadas (misma epica/persona/fase o con dependencia entre si) en una misma reunion. No pongas una HU por reunion salvo que su tamano o complejidad lo justifique.
- **Orden logico**: respeta fases y dependencias — F0 antes de F1 antes de F2; una HU que depende de otra se revisa despues (o en la misma sesion) que su prerequisito. Agrupa por epica/persona para minimizar cambios de contexto.
- **Objetivo de cierre**: planifica para **cerrar todas las HU dentro del periodo objetivo**. Calcula cuantas reuniones caben (dias laborables restantes x reuniones/semana) y cuantas HU-reunion necesitas. Si **no caben**, no las apiles sin sentido: avisa como riesgo y propon (a) mas reuniones/semana, (b) mas HU por reunion, o (c) extender el periodo. Documenta la decision.
- Las HU **bloqueadas** se planifican igualmente (hay que desbloquearlas), pero senalalo como riesgo en el `.md`.

Cada reunion se convierte en una fila del Gantt con: actividad (las HU que se revisan), tipo (`funcional`/`tecnica`/`doc`), fecha(s) y los dias marcados como reunion.

### 4. Generacion del `.md` de plan (fuente de verdad)

Genera (o actualiza) `docs/plan-revision-hu.md` con esta estructura:

```markdown
# Plan de revision de Historias de Usuario — <nombre del proyecto>

> Documento de planificacion de la revision de HU (AIDD). Generado por `aidd hu-review-plan`.
> Fuentes: docs/mapa-historias-usuario.md, docs/detalle-historias-usuario.md.
> El Excel docs/xlsx/plan-revision-hu.xlsx es la vista rica de este plan. Pendiente de aprobacion humana.

## 1. Parametros de planificacion
- Kickoff, periodo objetivo, reuniones/semana, agrupacion por reunion, separacion funcional/tecnica.
- Nota breve: cuantas reuniones caben vs cuantas HU-reunion se necesitan (y el riesgo si no caben).

## 2. Consolidado de HU
- Tabla con una fila por HU: id, fase, persona, epica, historia (Como/quiero/para), prioridad, MoSCoW,
  estimacion, estado, bloqueada, GAP, RF, tipo de revision, dependencias.

## 3. Calendario de revision (resumen del Gantt)
- Semana 1: revision documentacion cliente.
- Resto del periodo: por cada reunion — fecha, tipo (funcional/tecnica), HU revisadas.

## 4. Leyenda de campos
- Por cada campo codificado (Persona, GAP, Estado, ...): valor -> significado (en blanco si no se conoce).

## 5. Riesgos y supuestos
- HU bloqueadas, reuniones insuficientes para el periodo, campos sin significado, etc. Marca [BLOQUEANTE].

## 6. Decisiones tomadas
- Registro ligero: pregunta, opciones, decision, origen (usuario | default), una linea de justificacion.
```

### 5. Generacion del manifiesto JSON

Escribe `docs/plan-revision-hu.json` — el **manifiesto de build** que consume el script. Es la forma-maquina del mismo contenido del `.md`; ambos salen de la misma consolidacion, asi que **deben coincidir**. Esquema:

```jsonc
{
  "project": "<nombre>",
  "hus": [
    {
      "id": "HU-01",
      "fase": "F1",                       // F0 | F1 | F2 | ...
      "persona": "P1",                    // codigo tal cual en el doc
      "epica": "Acceso",                  // epica / actividad del backbone
      "como": "administrador",            // solo el sujeto (sin la palabra 'Como')
      "quiero": "gestionar usuarios",     // solo el objetivo (sin 'quiero')
      "para": "controlar accesos",        // solo el beneficio (sin 'para')
      "prioridad": "Alta",                // Alta | Media | Baja | ""
      "moscow": "Must",                   // Must | Should | Could | Won't | ""
      "estimacion": "M",                  // XS | S | M | L | XL | "" (XS=0,5d S=1,5d M=3d L=5d XL=8d)
      "estado": "Pendiente",              // Pendiente | En revision | Cerrada | ""
      "bloqueada": false,
      "gap": "GAP-1",                     // "" si no aplica
      "rf": "RF-01",
      "tipo_revision": "ambas",           // funcional | tecnica | ambas
      "criterios": ["Dado ... cuando ... entonces ..."],
      "notas": "",
      "dependencias": ["HU-00"]
    }
  ],
  "legend": [
    { "campo": "Persona", "valores": [ { "valor": "P1", "significado": "" } ] },
    { "campo": "GAP",     "valores": [ { "valor": "GAP-1", "significado": "" } ] },
    { "campo": "Estado",  "valores": [ { "valor": "Pendiente", "significado": "Aun no revisada" } ] }
  ],
  "gantt": {
    "year": 2026,
    "month": 7,
    "kickoff": "2026-07-06",
    "rows": [
      { "activity": "Revision documentacion cliente", "kind": "doc",
        "start": "2026-07-06", "end": "2026-07-10", "meetings": [] },
      { "activity": "HU-01, HU-02 — Acceso (funcional)", "kind": "funcional",
        "start": "2026-07-13", "end": "2026-07-13", "meetings": ["2026-07-13"] },
      { "activity": "HU-01, HU-03 — Acceso/Catalogo (tecnica)", "kind": "tecnica",
        "start": "2026-07-15", "end": "2026-07-15", "meetings": ["2026-07-15"] }
    ]
  }
}
```

Reglas del manifiesto:

- `como`/`quiero`/`para` van **sin** las palabras conectoras: el Excel las anade en **negrita** al componer la celda "Historia". Si solo tienes la frase completa, dejalos vacios y pon la frase en un campo `historia`; el script la usara tal cual (sin negrita parcial). Preferir siempre el desglose en tres partes.
- `bloqueada: true` cuando la HU tiene una dependencia o decision abierta que impide avanzarla (un impedimento real). No marques `bloqueada` por la mera existencia de criterios imprescindibles: eso es normal en una HU y no la bloquea.
- `legend` incluye **un bloque por campo codificado** detectado; valores en blanco si no se conoce el significado.
- `gantt.year`/`gantt.month` definen el mes que se dibuja (columnas 1..fin de mes). Las fechas son ISO `YYYY-MM-DD`. `kind`: `doc` | `funcional` | `tecnica`. `meetings` lista los dias que son reunion (para marcarlos con F/T).

### Sello de version y fecha-hora (antes de renderizar)

Tras escribir o actualizar `docs/plan-revision-hu.md`, y **antes** de generar el Excel, sella el documento:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/stamp_doc.py" --input docs/plan-revision-hu.md
```

Anade/actualiza la cabecera `> **Version N** - **Generado:** fecha hora`, **incrementa la version en cada regeneracion** (via `docs/.aidd-doc-meta.json`) y usa la **fecha y hora reales**. No inventes la version ni la hora: las pone el script y esa linea no se edita a mano. Si Python no esta disponible, avisa pero no bloquees.

### 6. Generacion del Excel

Ejecuta el script incluido en este skill, que renderiza el manifiesto a `.xlsx` con las cuatro pestañas (Dashboard, Detalle HU, Leyenda, Gantt del mes). El script usa `openpyxl` y **se encarga el mismo de instalarlo** si falta (esta pensado para usuarios no tecnicos): al arrancar, si no encuentra `openpyxl` ejecuta `pip install openpyxl` (y, en entornos restringidos, reintenta con `--user`) y continua. La llamada a `python` es la unica puerta de permisos; no hay que pedir al usuario que instale nada a mano.

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/aidd-hu-review-plan/scripts/gen_hu_plan_xlsx.py" \
  --input docs/plan-revision-hu.json \
  --output docs/xlsx/plan-revision-hu.xlsx \
  --open
```

Flags:

- `--input <path>`: manifiesto JSON (obligatorio).
- `--output <path>`: ruta del `.xlsx` (obligatorio). El script crea las carpetas necesarias.
- `--open`: abre el `.xlsx` al terminar (best-effort; no hace nada en headless). Pasa `--open` salvo en modo no interactivo (CI/auto).
- `--no-install`: desactiva la autoinstalacion de `openpyxl` (por defecto se instala). Equivale a la variable de entorno `AIDD_HU_PLAN_NO_INSTALL`. Uselo solo en entornos donde no se quiera que el script instale paquetes.

Que produce el script (no hay que replicarlo a mano):

- **Detalle HU**: una fila por HU con todos los campos; en la columna "Historia (Como...quiero...para...)" las palabras **Como / quiero / para** van en negrita (rich text en celda). Estado y prioridad con color; autofiltro y paneles congelados.
- **Dashboard**: KPIs (Total HU, Pendientes de cerrar, Cerradas, En revision, Bloqueadas, % Cerradas) y graficas (estado, fase, prioridad, persona, tipo de revision) auto-calculadas del detalle.
- **Leyenda**: un bloque por campo codificado con valor -> significado.
- **Gantt del mes**: rejilla dia a dia; fines de semana sombreados; semana 1 de revision de documentacion; resto del mes con las reuniones de HU marcadas con **F** (funcional) o **T** (tecnica), con su leyenda de colores.

El script intenta instalar `openpyxl` automaticamente. Solo si esa instalacion falla (por ejemplo, sin red o pip bloqueado), informa de ello, deja el `.md` y el `.json` como entregables y explica que el Excel requiere `openpyxl`. No bloquees el resto del comando.

## Verificacion final

Al terminar, informa:

- Comando AIDD ejecutado (`aidd hu-review-plan`).
- Rutas generadas: `docs/plan-revision-hu.md` (fuente de verdad), `docs/plan-revision-hu.json` (manifiesto) y `docs/xlsx/plan-revision-hu.xlsx` (entregable), o aviso si el Excel no se pudo generar (falta `openpyxl`).
- Resumen: numero de HU consolidadas, cuantas pendientes / bloqueadas, numero de reuniones planificadas (funcionales vs tecnicas) y si todas las HU caben en el periodo objetivo.
- Campos de la Leyenda que han quedado **sin significado** y que el humano debe completar.
- Recordatorio: pendiente de **aprobacion humana**; el `.md` es la fuente de verdad y el `.xlsx` su vista rica.
