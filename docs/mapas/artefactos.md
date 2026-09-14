# Artefactos

**¿Qué documento sale de cada paso y quién lo lee después?** Es lo que explica el orden del proceso: cada comando lee lo que dejó el anterior. Cinco diagramas, uno por tramo, y al final la tabla de quién escribe y quién lee cada fichero.

En los diagramas, el **rectángulo** es un fichero, la **píldora** es un comando y el **hexágono** es algo de fuera del repo.

## Definir y diseñar

```mermaid
flowchart TB
  cliente{{"Cliente<br/>documentación, código y datos"}}
  cr["docs/cliente-requisitos.md"]
  rq["docs/requisitos.md"]
  mp["docs/mapa-historias-usuario.md"]
  dt["docs/detalle-historias-usuario.md"]
  ap["docs/arquitectura-base-prototipo.md"]
  pr["prototipo<br/>imágenes y HTML"]
  ge["docs/guia-estilos.md<br/>docs/design/tokens"]
  pa["docs/propuesta-arquitectura-base.md"]
  ab["docs/arquitectura-base.md"]

  cliente --> c0(["aidd client-requirements"]) --> cr
  cr --> c1(["aidd requirements"]) --> rq
  rq --> c2(["aidd user-stories"]) --> mp
  rq & mp --> c3(["aidd user-story-details"]) --> dt
  mp & dt --> c4(["aidd prototype-architecture"]) --> ap
  ap --> c5(["aidd prototype"]) --> pr
  dt --> c6(["aidd style-guide"]) --> ge
  dt --> c7(["aidd architecture-proposal"]) --> pa
  dt & pa & ge --> c8(["aidd architecture"]) --> ab
```

## Lo que se entrega a negocio y a QA

```mermaid
flowchart LR
  mp["docs/mapa-historias-usuario.md"]
  dt["docs/detalle-historias-usuario.md"]
  figma{{"Figma"}}
  hr["docs/plan-revision-hu.md<br/>y su Excel"]
  df["docs/df/<br/>un DF en Word por HU"]
  tp["docs/pruebas/<br/>casos en Excel y evidencias en Word"]
  ds["docs/design/<br/>componentes y mapa por HU"]

  mp & dt --> c1(["aiba hu-review-plan"]) --> hr
  dt --> c2(["aiba functional-design"]) --> df
  dt --> c3(["aiba test-plan"]) --> tp
  df -.->|"si existe"| c3
  figma --> c4(["aifg capture"]) --> ds
  dt -.-> c4
```

## Planificar

```mermaid
flowchart TB
  dis["documentos de diseño<br/>requisitos, historias y arquitectura"]
  hr["docs/plan-revision-hu.md"]
  init(["aisdd init"])
  road(["aisdd roadmap"])
  pp(["aiba project-plan"])
  cfg["openspec/config.yaml<br/>AGENTS.md"]
  rm["docs/roadmap.md"]
  plan["docs/planificacion-proyecto.md"]
  sprint(["aiba sprint-planning"])
  sp["docs/sprint-plan.md"]
  js["docs/jira-sync.md"]
  jira{{"Jira"}}

  dis --> init --> cfg
  dis --> road --> rm
  road --> cfg
  dis --> pp --> plan
  rm & plan --> sprint
  hr -.-> sprint
  sprint --> sp
  plan -.-> road
  sp -.->|"si existe, se alinea"| road
  sprint -.->|"volcado opcional"| jira
  sprint -.-> js
```

## Construir

```mermaid
flowchart TB
  ent["docs/roadmap.md<br/>docs/mapa-historias-usuario.md<br/>openspec/config.yaml"]
  specs["openspec/specs/<br/>la línea base"]
  open(["aisdd open change"])
  ch["openspec/changes/nombre-del-change/<br/>proposal, design, tasks, spec y decisions"]
  amend(["aisdd amend change"])
  design["docs/guia-estilos.md<br/>docs/design/"]
  impl(["aisdd implement change"])
  code["código y tests"]
  close(["aisdd close change"])
  arch["openspec/changes/archive/"]
  uml(["aisdd uml"])
  umlh["diagramas UML en HTML"]

  ent --> open
  specs -.->|"lo ya construido"| open
  open --> ch
  amend -.->|"el delta"| ch
  ch --> impl
  design -.-> impl
  impl --> code
  ch & code --> close
  close --> specs
  close --> arch
  ch -.-> uml --> umlh
```

Los tres comandos del change escriben además su entrada en `openspec/audit/` y, con Jira activo, actualizan `docs/jira-sync.md`.

## Medir y contar

```mermaid
flowchart LR
  cfg["openspec/config.yaml<br/>las fases"]
  sp["docs/sprint-plan.md"]
  arch["openspec/changes/archive/"]
  neg["documentos de negocio<br/>requisitos, historias, arquitectura y planes"]
  cu["docs/traspaso-cuestionario.md<br/>lo rellena quien lo sabe"]
  audit["openspec/audit/<br/>una entrada por comando"]
  act["docs/aidd-activity.md<br/>opt-in · lo escribe el hook"]
  jr["docs/aiad-journal.md"]
  js["docs/jira-sync.md<br/>y el worklog de Jira"]
  md["cualquier .md de docs/"]

  cfg & sp & arch --> sr(["aiba status-report"])
  audit --> sr
  arch & neg --> ob(["aiba onboarding"])
  neg & cu --> hd(["aiba handover"])
  arch & audit --> hd
  audit & act & jr & js --> mt(["aiba metrics"])
  md --> bd(["booster-docs"])
  sr --> st["docs/html/estado-proyecto.html"]
  ob --> onb["docs/onboarding.md"]
  hd --> tr["docs/traspaso.md"]
  mt --> kp["docs/kpis-ia.md"]
  bd --> vis["docs/html/"]
```

## Quién escribe y quién lee cada fichero

| Fichero | Lo escribe | Lo leen |
|---|---|---|
| `docs/cliente-requisitos.md` | `aidd client-requirements` | `aidd requirements`, `aidd prototype`, `aiba onboarding`, `aiba handover` |
| `docs/requisitos.md` | `aidd requirements` | `aidd user-stories`, `aidd user-story-details`, `aisdd init` |
| `docs/mapa-historias-usuario.md` | `aidd user-stories` | `aidd user-story-details`, `aidd prototype-architecture`, `aiba hu-review-plan`, `aiba project-plan`, `aiba onboarding`, `aisdd open change` |
| `docs/detalle-historias-usuario.md` | `aidd user-story-details` | Casi todos: la Fase 2 de `aidd`, los documentos, planes y métricas de `aiba`, `aisdd init` y `aisdd roadmap`, y `aifg` |
| `docs/arquitectura-base-prototipo.md` | `aidd prototype-architecture` | `aidd prototype` |
| `docs/guia-estilos.md` | `aidd style-guide` | `aidd architecture`, `aisdd implement change`, `aifg`, `aiba onboarding`, `aiba handover` |
| `docs/design/` | `aidd style-guide` (los tokens) y `aifg capture` (componentes y mapa por HU) | `aisdd implement change`, `aifg update`, `aiba handover` |
| `docs/propuesta-arquitectura-base.md` | `aidd architecture-proposal` | `aidd architecture` |
| `docs/arquitectura-base.md` | `aidd architecture` | `aisdd init`, `aisdd roadmap`, `aiba project-plan`, `aiba onboarding`, `aiba handover` |
| `docs/plan-revision-hu.md` | `aiba hu-review-plan` | `aiba sprint-planning`, `aisdd init`, `aisdd roadmap`, `aiba onboarding` |
| `docs/df/` | `aiba functional-design` | `aiba test-plan`, `aiba handover`, y quien firma |
| `docs/pruebas/` | `aiba test-plan` | Quien ejecuta las pruebas |
| `docs/planificacion-proyecto.md` | `aiba project-plan` | `aiba sprint-planning`, `aisdd init`, `aisdd roadmap`, `aiba onboarding`, `aiba handover` |
| `docs/roadmap.md` | `aisdd roadmap` | `aiba sprint-planning`, `aisdd open change`, `aisdd lane`, `aiba handover` |
| `docs/sprint-plan.md` | `aiba sprint-planning` | `aisdd init`, `aisdd roadmap`, `aiba status-report`, `aiba onboarding` |
| `docs/jira-sync.md` | `aiba sprint-planning` al volcar, y `aisdd open`, `implement` y `close change` | Los mismos comandos, `aisdd amend change`, `aiba functional-design` y `aiba metrics` |
| `openspec/config.yaml` | `aisdd init` y `aisdd roadmap`; `aiba sprint-planning`, la sección de Jira | Todos los comandos de `aisdd`, `aiba status-report` |
| `openspec/changes/<change>/` | `aisdd open change`; `aisdd implement change` y `aisdd amend change` lo completan | `aisdd implement change`, `aisdd close change`, `aisdd uml` |
| `openspec/specs/` | `aisdd init` en un proyecto con código, y `aisdd close change` | `aisdd open change`, `aiba handover` |
| `openspec/changes/archive/` | `aisdd close change` | `aiba status-report`, `aiba onboarding`, `aiba handover` |
| `openspec/audit/` | Cada comando de `aisdd`, salvo `aisdd lane` | `aiba status-report`, `aiba metrics`, `aiba handover` |
| `docs/aidd-activity.md` | El hook de actividad, solo si el fichero existe | `aiba metrics` |
| `docs/aiad-journal.md` | `aiad journal` y su hook | `aiba metrics` |
| `docs/html/estado-proyecto.html` | `aiba status-report` | Comité y dirección |
| `docs/kpis-ia.md` | `aiba metrics` | Quien decide si la IA compensa |
| `docs/onboarding.md` | `aiba onboarding` | Quien se incorpora, y `aiba handover` |
| `docs/traspaso-cuestionario.md` | `aiba handover` lo prepara; lo rellena quien lo sabe | `aiba handover` |
| `docs/traspaso.md` | `aiba handover` | El equipo de mantenimiento |
| `docs/html/` | `booster-docs`, al que llaman los skills que generan documentos, y los informes de `aiba` | Personas: la vista HTML de cada documento; el `.md` sigue siendo la fuente |
