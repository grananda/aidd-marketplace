# Artifacts

> **Español:** [docs/mapas/artefactos.md](../mapas/artefactos.md). The Spanish version is the source of truth.

**Which document comes out of each step, and who reads it next?** This is what explains the order of the process: every command reads what the previous one left behind. Five diagrams, one per stretch, and at the end the table of who writes and who reads each file.

In the diagrams, a **rectangle** is a file, a **pill** is a command and a **hexagon** is something from outside the repo. File names are kept in Spanish because they are the real paths the skills read and write.

## Define and design

```mermaid
flowchart TB
  cliente{{"Client<br/>documentation, code and data"}}
  cr["docs/cliente-requisitos.md"]
  rq["docs/requisitos.md"]
  mp["docs/mapa-historias-usuario.md"]
  dt["docs/detalle-historias-usuario.md"]
  ap["docs/arquitectura-base-prototipo.md"]
  pr["prototype<br/>images and HTML"]
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

## What goes to business and to QA

```mermaid
flowchart LR
  mp["docs/mapa-historias-usuario.md"]
  dt["docs/detalle-historias-usuario.md"]
  figma{{"Figma"}}
  hr["docs/plan-revision-hu.md<br/>and its spreadsheet"]
  df["docs/df/<br/>one design doc in Word per story"]
  tp["docs/pruebas/<br/>cases in Excel and evidence in Word"]
  ds["docs/design/<br/>components and map per story"]

  mp & dt --> c1(["aiba hu-review-plan"]) --> hr
  dt --> c2(["aiba functional-design"]) --> df
  dt --> c3(["aiba test-plan"]) --> tp
  df -.->|"when it exists"| c3
  figma --> c4(["aifg capture"]) --> ds
  dt -.-> c4
```

## Plan

```mermaid
flowchart TB
  dis["design documents<br/>requirements, stories and architecture"]
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
  sp -.->|"when it exists, it aligns"| road
  sprint -.->|"optional push"| jira
  sprint -.-> js
```

## Build

```mermaid
flowchart TB
  ent["docs/roadmap.md<br/>docs/mapa-historias-usuario.md<br/>openspec/config.yaml"]
  specs["openspec/specs/<br/>the baseline"]
  open(["aisdd open change"])
  ch["openspec/changes/name-of-the-change/<br/>proposal, design, tasks, spec and decisions"]
  amend(["aisdd amend change"])
  design["docs/guia-estilos.md<br/>docs/design/"]
  impl(["aisdd implement change"])
  code["code and tests"]
  close(["aisdd close change"])
  arch["openspec/changes/archive/"]
  uml(["aisdd uml"])
  umlh["UML diagrams in HTML"]

  ent --> open
  specs -.->|"what is already built"| open
  open --> ch
  amend -.->|"the delta"| ch
  ch --> impl
  design -.-> impl
  impl --> code
  ch & code --> close
  close --> specs
  close --> arch
  ch -.-> uml --> umlh
```

The three change commands also write their entry in `openspec/audit/` and, with Jira enabled, update `docs/jira-sync.md`.

## Measure and tell

```mermaid
flowchart LR
  cfg["openspec/config.yaml<br/>the phases"]
  sp["docs/sprint-plan.md"]
  arch["openspec/changes/archive/"]
  neg["business documents<br/>requirements, stories, architecture and plans"]
  cu["docs/traspaso-cuestionario.md<br/>filled in by whoever knows"]
  audit["openspec/audit/<br/>one entry per command"]
  act["docs/aidd-activity.md<br/>opt-in · written by the hook"]
  jr["docs/aiad-journal.md"]
  js["docs/jira-sync.md<br/>and the Jira worklog"]
  md["any .md under docs/"]

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

## Who writes and who reads each file

| File | Written by | Read by |
|---|---|---|
| `docs/cliente-requisitos.md` | `aidd client-requirements` | `aidd requirements`, `aidd prototype`, `aiba onboarding`, `aiba handover` |
| `docs/requisitos.md` | `aidd requirements` | `aidd user-stories`, `aidd user-story-details`, `aisdd init` |
| `docs/mapa-historias-usuario.md` | `aidd user-stories` | `aidd user-story-details`, `aidd prototype-architecture`, `aiba hu-review-plan`, `aiba project-plan`, `aiba onboarding`, `aisdd open change` |
| `docs/detalle-historias-usuario.md` | `aidd user-story-details` | Nearly everything: phase 2 of `aidd`, the documents, plans and metrics of `aiba`, `aisdd init` and `aisdd roadmap`, and `aifg` |
| `docs/arquitectura-base-prototipo.md` | `aidd prototype-architecture` | `aidd prototype` |
| `docs/guia-estilos.md` | `aidd style-guide` | `aidd architecture`, `aisdd implement change`, `aifg`, `aiba onboarding`, `aiba handover` |
| `docs/design/` | `aidd style-guide` (the tokens) and `aifg capture` (components and map per story) | `aisdd implement change`, `aifg update`, `aiba handover` |
| `docs/propuesta-arquitectura-base.md` | `aidd architecture-proposal` | `aidd architecture` |
| `docs/arquitectura-base.md` | `aidd architecture` | `aisdd init`, `aisdd roadmap`, `aiba project-plan`, `aiba onboarding`, `aiba handover` |
| `docs/plan-revision-hu.md` | `aiba hu-review-plan` | `aiba sprint-planning`, `aisdd init`, `aisdd roadmap`, `aiba onboarding` |
| `docs/df/` | `aiba functional-design` | `aiba test-plan`, `aiba handover`, and whoever signs it |
| `docs/pruebas/` | `aiba test-plan` | Whoever runs the tests |
| `docs/planificacion-proyecto.md` | `aiba project-plan` | `aiba sprint-planning`, `aisdd init`, `aisdd roadmap`, `aiba onboarding`, `aiba handover` |
| `docs/roadmap.md` | `aisdd roadmap` | `aiba sprint-planning`, `aisdd open change`, `aisdd lane`, `aiba handover` |
| `docs/sprint-plan.md` | `aiba sprint-planning` | `aisdd init`, `aisdd roadmap`, `aiba status-report`, `aiba onboarding` |
| `docs/jira-sync.md` | `aiba sprint-planning` on its push, and `aisdd open`, `implement` and `close change` | Those same commands, `aisdd amend change`, `aiba functional-design` and `aiba metrics` |
| `openspec/config.yaml` | `aisdd init` and `aisdd roadmap`; `aiba sprint-planning` writes the Jira section | Every `aisdd` command, `aiba status-report` |
| `openspec/changes/<change>/` | `aisdd open change`; `aisdd implement change` and `aisdd amend change` complete it | `aisdd implement change`, `aisdd close change`, `aisdd uml` |
| `openspec/specs/` | `aisdd init` on a project with code, and `aisdd close change` | `aisdd open change`, `aiba handover` |
| `openspec/changes/archive/` | `aisdd close change` | `aiba status-report`, `aiba onboarding`, `aiba handover` |
| `openspec/audit/` | Every `aisdd` command except `aisdd lane` | `aiba status-report`, `aiba metrics`, `aiba handover` |
| `docs/aidd-activity.md` | The activity hook, only when the file already exists | `aiba metrics` |
| `docs/aiad-journal.md` | `aiad journal` and its hook | `aiba metrics` |
| `docs/html/estado-proyecto.html` | `aiba status-report` | The steering committee and management |
| `docs/kpis-ia.md` | `aiba metrics` | Whoever decides whether the AI pays off |
| `docs/onboarding.md` | `aiba onboarding` | Whoever joins, and `aiba handover` |
| `docs/traspaso-cuestionario.md` | `aiba handover` prepares it; whoever knows fills it in | `aiba handover` |
| `docs/traspaso.md` | `aiba handover` | The maintenance team |
| `docs/html/` | `booster-docs`, called by the skills that generate documents, and the `aiba` reports | People: the HTML view of each document; the `.md` stays the source |
