# AIDD + AISDD + AIBA + AIAD — a skills marketplace for Claude Code

> **Español:** [README.md](README.md). The Spanish version is the source of truth: it is what the team maintains, and if the two ever disagree, the Spanish one wins.

A plugin marketplace that installs the **AIDD** (AI Driven Development — AI-assisted definition and design), **AISDD** (AI Spec-Driven Development on top of OpenSpec; *a maintained fork of the old `sdd`*), **AIBA** (AI Business Analyst — functional analysis, delivery and measurement) and **AIAD** (AI-Augmented Development — human-first, *ai-in-the-loop* execution) sets from any Claude Code instance.

- Repository: `grananda/aidd-marketplace` — **private**.
- Marketplace name: `aidd-sdd`.

> **First time here?** The [maps](docs/maps/README.md) show in diagrams which plugins exist, what each one brings, what is used at each point of the process and what to reach for in each situation.

## The plugins

| Plugin | Contents | What it is for |
|--------|----------|----------------|
| `aidd` | 9 `aidd-*` skills (Phases 0, 1 and 2) + methodology | Capture the client's requirements, formalise them, define and detail the user stories, and design the architecture and the style guide. This is the "what gets built". |
| `aisdd` | `aisdd-specs` + `aisdd-amend` + methodology | Execution with OpenSpec: onboarding existing projects with base specs, a roadmap (sprint-plan aware, with **three parallelism modes**) and the open/implement/close change cycle, a configurable pre-flight, an audit trail and Jira integration. `aisdd …` commands (legacy alias `native-ai …`). *A maintained fork of the old `sdd`.* |
| `boosters` | `booster-ux`, `booster-uml`, `booster-docs` | Generate UX prototypes, UML diagrams and HTML views of the planning documents. **Used by `aidd`, `aisdd` and `aiba`.** |
| `aiba` | 9 `aiba-*` skills (business, delivery and measurement) + its own methodology | **AI Business Analyst**: the layer that faces the business. A functional design document in Word per story, a story review plan with business and IT, a resource plan, a sprint plan with an optional push to Jira, and **measured** KPIs of AI usage. Independent of OpenSpec. |
| `aifg` | `aifg-capture` + `aifg-update` | **AI Figma**: takes the Figma design **down to the story that implements it**. It extracts the nodes, normalises them into reusable component definitions plus a composition map per story, and re-captures what changes, saying which stories are affected. **Optional and additive**: without it, `aisdd implement change` falls back to the style guide. |
| `aiad` | 11 `aiad-*` skills + journal hook + review subagent + methodology | **Human-first execution (*ai-in-the-loop*)**: you write the code and the AI augments you on demand. **Independent and optional**; an alternative to `aisdd` for the execution phase. |

## Command index by skill and phase

Every command, ordered by phase of the method. Each command activates its skill; it can also be invoked namespaced (`/aidd:<skill>`, `/aisdd:aisdd-specs`, `/boosters:<skill>`, `/aiad:<skill>`) or in plain language.

### `aidd` — Definition and design (plugin `aidd`, 9 commands)

| Phase | Command | Skill | Generates |
|------|---------|-------|--------|
| 0 | `aidd client-requirements` | `aidd-client-requirements` | `docs/cliente-requisitos.md` (the client brief) |
| 1.1 | `aidd requirements` | `aidd-requirements` | `docs/requisitos.md` (functional and non-functional requirements, constraints) |
| 1.2 | `aidd user-stories` `[fases=N\|fases>=N]` | `aidd-user-stories` | `docs/mapa-historias-usuario.md` (story map by phases; F0 = enablers) |
| 1.3 | `aidd user-story-details` | `aidd-user-story-details` | `docs/detalle-historias-usuario.md` (acceptance criteria) |
| 2.1 | `aidd prototype-architecture` | `aidd-prototype-architecture` | `docs/arquitectura-base-prototipo.md` |
| 2.2 | `aidd prototype` | `aidd-prototype` | A mocked prototype (redirects to `booster-ux`) |
| 2.3 | `aidd style-guide` | `aidd-style-guide` | `docs/guia-estilos.md` (design tokens) |
| 2.3 | `aidd architecture-proposal` | `aidd-architecture-proposal` | `docs/propuesta-arquitectura-base.md` |
| 2.4 | `aidd architecture` | `aidd-architecture` | `docs/arquitectura-base.md` (the final architecture) |


### `aisdd` — Initialisation, roadmap and execution (plugin `aisdd`, 9 commands, skills `aisdd-specs` and `aisdd-amend`)

> `aisdd …` are the primary commands; the `native-ai …` ones still work as **legacy aliases**. The plugin used to be called `sdd`.

| Phase | Command | Role | Generates / does |
|------|---------|-----|---------------|
| 3.1 | `aisdd init` | AI Lead | Initialises OpenSpec + `AGENTS.md` + `openspec/config.yaml` (recording the design **and the delivery layer**). On an **existing project** it also seeds the **base specs** in `openspec/specs/` from the code |
| 3.3 | `aisdd roadmap` | AI Lead | `docs/roadmap.md` + `docs/prompts-roadmap-native-ai.md` + the `roadmap` section in `config.yaml` + a block in `AGENTS.md` (phases by context, **aligned to `sprint-plan.md`** when it exists, and picks the **parallelism mode**: `atomic`, `waves` or `multilane`) |
| 4 | `aisdd open change [what-you-want-to-build]` | AI Lead | Pre-flight + generates validated specs (`proposal.md`, `design.md`, `spec.md`, `decisions.md`). The first one is always `foundation` (scaffolding). In `multilane`, **one open change per lane** |
| 4 | `aisdd implement change [change-slug]` | AI Developer | Pre-flight + implements the change's code |
| 4 | `aisdd amend change [description]` | Developer / Lead | Folds a modification into an **already open** change and runs **that delta only**, without re-applying the change (skill `aisdd-amend`) |
| 4 | `aisdd close change [change-slug]` | Outcome Validator | Validates and archives the change |
| 4 | `aisdd lane [list \| switch \| status]` | AI Developer / AI Lead | Selects the **active line of work** (`multilane` roadmaps only), the way `git switch` works with branches. With several repositories the lane **is** the repo, so `switch` is rejected and only `list` and `status` remain |
| 2 / 4 (aux) | `aisdd prototype-ux [change-slug]` | Architect / Developer | UX prototypes of the change (calls `booster-ux`) |
| aux | `aisdd uml [change-slug]` | Anyone | UML diagrams of the change in HTML (calls `booster-uml`) |

#### How to parallelise the work (three modes)

By default the cycle **assumes** a single thread: one open change at a time. That is a convention of the phasing, not a guard — outside `multilane` nothing checks how many changes are open. With several developers that leaves almost everyone waiting, so `aisdd roadmap` asks how many work in parallel and offers two ways to split the work. **They do not compete: they are perpendicular axes.**

```
                Wave 1      Wave 2           Wave 3      Wave 4
                ───────────────────────────────────────────────────
lane api        │          │ F-api-01      │           │          │
lane portal     │   F0     │ F-portal-01   │  FB-01    │  FB-02   │
lane import     │          │ F-import-01   │           │          │
                ───────────────────────────────────────────────────
                   1/3          3/3            1/3        1/3
```

**Columns = waves** (when work can happen at the same time). **Rows = lanes** (whose part of the code each one is).

`F0` and the `FB-NN` phases **take up the whole column**: they touch what every lane shares (the contract, a migration, the rollout) and therefore stop them all. Put another way, **a barrier is nothing more than a wave one lane wide with declared ownership**.

| Mode | What it parallelises | Guarantee | When |
|------|----------------|----------|--------|
| `atomic` | Nothing | **By convention**, not verified | One dev, or no basis for splitting. **Default** |
| `waves` | Up to `N` phases at a time, respecting dependencies | **None** — it orders, it does not protect | Several devs with no declarable surfaces |
| `multilane` | `N` persistent lines, one change **per lane** | Declared and **verified** on close | Modules with disjoint code paths, or **one repo per lane** |

Both reach the **same calendar**; what changes is whether there is a safety net underneath. In `multilane`, `aisdd close change` checks that the change did not write outside its lane's paths, and a correction that touches the shared contract stops the sibling lanes instead of being resolved silently.

**Quick rule:**

- A roadmap already designed and validated that you do not want to disturb → **annotated `waves`** (it is added without re-phasing: phase names are kept, so the link to the sprint plan and to Jira survives).
- A project with modules on separate paths and several devs → **`multilane`**.
- A single dev, or no basis for separating surfaces → **`atomic`**.
- **A product split across several repositories → `multilane` is mandatory, one lane per repo.** It is not a choice: see below.

#### One product across several repositories

The usual case at a client: the repos are a given — one per part of the project — and there is no root repo grouping them. Declaring them in section 3 of `docs/arquitectura-base.md`, **by name only** (no URL, no path, nobody needs them), **forces** `multilane` mode with **one lane per repo**. With a single repo nothing is forced.

No parent repo and no submodules. What there is are **two ways of splitting the documentation**, and `aisdd roadmap` **asks which one** — it is not inferred from the number of repos:

| Topology | `openspec/` and `docs/` | The price |
|---|---|---|
| **`fraccionado`** | One **per repo**, self-contained | `docs/` is copied around and a change has to be replicated everywhere |
| **`externalizado`** | In a **separate git repository** that governs the code repos, which hang off it and are ignored by it. Works with **one or several** | Commit and push of the governance repo on every command. Devs never change folder: they work in their repo and the skill walks up to find the specs |

With **`fraccionado`**, everything else follows from that 1:1 between lane and repo:

| | In multirepo |
|---|---|
| Independence between lanes | **Not verified: it is structural.** A change cannot leave its lane because it cannot leave its repo |
| Delivery | **One change, one PR** |
| Active lane | **Inferred from the repo.** `aisdd lane switch` is rejected; if it is unclear which one it is, you are asked |
| Barriers | **None.** There is no shared surface to serialise |
| Project status | It lives in no single repo: `aiba status-report` with one `--root` per repo |

With **`externalizado`** none of that applies: the mode is decided as usual, **lane and repo are different things again**, there are barriers, and the status report comes from a single `--root` pointing at the governance repo.

The bet is that the repos are genuinely **independent in code**: whatever they share travels as a versioned artifact — a published OpenAPI contract, a package — and each repo consumes the version it chooses. A repo that needs another's source is not fixed by phasing: it is a boundary in the wrong place.

The cost, plainly: **`docs/` is copied into every repo** and a change has to be replicated in all of them.

And if the project **migrates** from one repo to several, the previous `openspec/` is copied whole into each one so the record of what was delivered is not lost. That leaves closed changes duplicated on purpose; they are told apart because **phases from before the migration carry no `lane`**, and the report counts them **only once**.

The full detail, with one project phased in all three modes and their real calendars, is in **§3.bis** of `plugins/aisdd/methodology/native-ai-aidd-sdd.md` (in Spanish), and its sibling `.html`.

#### Starting on a project that already exists

`aisdd init` asks whether the development is new or already under way. If it is under way, it analyses the code and the documentation and **seeds the base specs** in `openspec/specs/<capability>/spec.md`: a photograph of the **actual current** behaviour, not the ideal one.

Without that baseline, the first `open change` cannot know what already exists and ends up specifying from scratch what the code has been doing for months.

- Whatever cannot be inferred with confidence is marked **`UNKNOWN`** — that is the honest output, not a failure.
- Whatever does not follow good practice is marked **`LEGACY`**: identified technical debt, and direct input to the roadmap.
- When code and documentation disagree, **the code wins**.
- Before anything is written, the **scope** is agreed and the **list of capabilities** is proposed for you to confirm. It never overwrites specs that already exist.

From there the flow is the usual one: `aisdd roadmap` to phase what is left and the change cycle applying **deltas on top of those base specs**.

#### Every command tells you the next one

The `aisdd` cycle is not a fixed sequence: what comes next depends on the mode, on which changes are alive, on whether a barrier is still blocked and on whether there is a delivery layer. That is why **every command closes with the next step already resolved**, ready to copy — not "consider implementing the change", but `aisdd implement change portal-catalogo`.

Where it shows most is in the two joins that are not obvious:

- **After `aisdd roadmap`**, towards the delivery layer: `aiba project-plan` when there is still no resource plan, `aiba sprint-planning` once there is — and if `sprint-plan.md` predates this roadmap, it warns that the two fell out of alignment and that re-running it is safe.
- **After `aisdd close change`**, towards the next phase: in `multilane` it includes the `aisdd lane switch` first when the phase belongs to another lane, and when a barrier is up next it tells you whether it has already been unblocked or which lanes are still open. With several repositories, when this one has no phases left it **says so and stops**: whatever remains is opened in its own repo.

When the roadmap runs out, it says so and suggests `aiba metrics`.

#### The system works out the optimum and shows it to you

Choosing the mode and the number of developers blind is choosing badly: the difference between `waves` with 2 devs and `multilane` with 3 can be weeks, and you cannot see it by staring at a list of phases.

`aisdd roadmap` **asks you first** which mode you would pick. Then, with the phases designed and their dependencies known, it computes the calendar of each mode with each number of devs and generates `docs/html/faseado-comparativa.html`: **your path and the optimum, side by side**, on the same time scale, with the barriers marked. If the optimum needs more people than there are, it says so with the cost in days — that is the business argument for asking for more team.

The order matters. You are asked before anything is computed, because proposing the optimum first would turn the comparison into a recommendation with a decorative alternative.

Two figures the diagram puts in front of you:

- **The critical path** — the longest chain of dependencies. No split goes below it. Once a path touches it, adding people no longer buys calendar.
- **The unprotected phases** — outside `multilane`, the ones touching a contract or a schema run without a barrier. A shorter path with those bars is faster *and* more fragile, and the calendar alone does not tell you that.

**With the project already under way** it works the same, but comparing the **remaining** calendar: a new developer joins, or the pace is not enough and you want to rethink the mode. Closed phases are frozen — they keep their identifier and their link to Jira — and only the pending ones are re-phased; the ones in flight stay anchored to their dev, because an open change does not move lines halfway. The diagram shows all three: what is done in a band before *today*, what is in flight marked as not reassignable, and what is pending already split according to the new strategy.

There the most useful answer is usually the least welcome one: if the remaining calendar already touches the critical path, the bottleneck is a chain of dependencies and **the developer you just brought in will not speed anything up**. The pre-flight says it in one line instead of leaving you to deduce it from two identical figures.

It requires `docs/detalle-historias-usuario.md`: without the sizes there is no effort per phase, and without effort the calendar would be made up.

#### What happens if you omit the argument

Every argument is **optional**, and with parallelism having several open changes is the norm, not the exception. If you omit it, the command does not choose on its own: it gathers the candidates and, when there is more than one, **presents them with the context that makes them recognisable** — phase and objective, plus the wave in `waves`, plus the lane in `multilane` — so you do not have to go hunting for the slug. With a single candidate it uses it and tells you. If it cannot ask (non-interactive mode) and there is ambiguity, it **stops** instead of picking.

#### How much the pre-flight asks

`open change` and `implement change` do not act blind: first they resolve the real ambiguities with the human and persist them in `decisions.md`.

- **Blocking questions are always asked, with no limit.** They are, by definition, the ones without which a solid spec cannot be produced: capping them trades correctness of the specification for convenience.
- How many **preferences** and **confirmations** are raised is up to each project:

  ```yaml
  # openspec/config.yaml
  preflight:
    preferencias: all      # all | integer >= 0
    confirmaciones: all
  ```

  Whatever falls outside the limit is not lost: it is resolved with the recommended default and recorded with `Origen: auto-default`.

`aisdd init` seeds the section with the default values and does not overwrite it when it already exists.

#### When a change appears midway through a change

Not every change costs the same. The question that decides the cost is **not** "does the code change?", but: **is any sealed AIDD document left saying something false?**

| Level | Situation | What you touch |
|-------|-----------|-----------|
| 1. Implementation | The spec is right and the code does not meet it | The code only |
| 2. Undocumented decision | No document had settled that detail | A `Tipo: correccion` entry in `decisions.md`, and you carry on |
| 3. Documentary contradiction | A sealed document states the opposite | **That** document, and only that one, re-sealed by its own skill |
| 4. Shared contract *(`multilane` only)* | The correction touches what other lanes work on | Nothing on your own: a **coordinated stop** and a review by the contract's owner |

Case 2 is the common one (a version incompatibility that shows up on validation, a visual nuance the guide did not cover) and it is **not** escalated to the Architect nor does it re-apply the change. When the specs need touching too (new criteria or tasks), the way in is **`aisdd amend change`**: it writes the delta and implements it without re-running the whole change over a tree that has already been worked on. It takes a build and test baseline **before** touching anything, so that what the amendment breaks is told apart, with evidence, from what was already broken — that way it does not need to know about the manual changes you made on your own.

### `boosters` — the shared dependency (plugin `boosters`, 3 commands)

They are called by `aidd`, `aisdd` and `aiba`, and can also be called directly.

| Command | Skill | Does |
|---------|-------|------|
| `booster-ux` | `booster-ux` | UX prototypes and screens in two variants (an image + navigable HTML) |
| `booster-uml` | `booster-uml` | UML diagrams (Mermaid) in HTML for an OpenSpec change |
| `booster-docs` | `booster-docs` | A dynamic HTML view of an AIDD/SDD planning document |

### `aiba` — Business, delivery and measurement (plugin `aiba`, 9 commands)

> **The layer that faces the business**: what the client signs (the functional design), what they approve (the resource plan), the calendar they follow (the sprints) and the KPIs they judge it by.
>
> The last four lived in `aidd` up to marketplace v1.8.0. **Their commands are now `aiba ...` and no `aidd ...` aliases remain**; what does not change is the data contract, because they still read and write the same files under `docs/`.
>
> Its own methodology lives in `plugins/aiba/methodology/native-ai-aiba.md`. Independent of OpenSpec: it consumes what AIDD and AISDD produce without modifying it.

| Phase | Command | Skill | Generates / does |
|------|---------|-------|---------------|
| 1.4 (opt.) | `aiba hu-review-plan` | `aiba-hu-review-plan` | `docs/plan-revision-hu.md` + a four-tab spreadsheet: how the stories are reviewed and closed with business and IT |
| 1 (after) | `aiba functional-design [HU-XX]` | `aiba-functional-design` | One **functional design document in Word per story** under `docs/df/`: cover, version and approval control, table of contents, introduction and scope, the story with its filters and fields, integrations, validations (front end / core), messages, screens, acceptance criteria, technical specifications and open points |
| 1 (after) | `aiba test-plan [HU-XX]` | `aiba-test-plan` | Per story, the **test plan** under `docs/pruebas/`: an `.xlsx` with the case inventory (`PS.FU.CU01.01`, criticality, steps, expected result, trace to the requirement and to the change, manual/automatable flag) and a `.docx` for evidence with one block per case. **It generates the plan; it does not run the tests** |
| 3.5.1 | `aiba project-plan` | `aiba-project-plan` | `docs/planificacion-proyecto.md` (resources + human vs AI estimate with KPIs of the difference) |
| 3.5.2 | `aiba sprint-planning` | `aiba-sprint-planning` | `docs/sprint-plan.md` (+ optional push to Jira) |
| cross-cutting | `aiba status-report` | `aiba-status-report` | `docs/estado-proyecto.json` + `docs/html/estado-proyecto.html`: an executive status report with **progress measured by work delivered** (closed phases weighted by their effort, not by dates), planned vs actual, blockers measured in the audit trail, critical path, delivery pace, risks and actions with an owner and a deadline, and **why each change slipped**, attributed to the audit signals that explain it — delays and early finishes alike. With **several repositories**, a repeated `--root` aggregates every `openspec/` and adds the breakdown per repo |
| cross-cutting | `aiba metrics` | `aiba-metrics` | `docs/kpis-ia.md` (**measured** KPIs of AI usage). Real human effort comes from the **Jira worklog** via MCP, with its coverage declared next to the figure |
| cross-cutting | `aiba onboarding` | `aiba-onboarding` | `docs/onboarding.md` + `docs/html/onboarding.html`: a **whole-project view for whoever joins** — dev, BA or PM: what the project is, how the team works, which sprint we are in, which stories are done and which are left, and what to read first. It comes from the business documents; OpenSpec only says what is built. **Versioned and approved** |
| cross-cutting | `aiba handover` | `aiba-handover` | `docs/traspaso.md` + `docs/html/traspaso.html`: the **handover to the team that takes over maintenance**. Operations first — where it runs, how it is deployed and rolled back, data and restores, alerts, access, dependencies, contacts — the **maintenance team** with its dedication and the **knowledge held by a single person** according to the audit trail; then what the system does, how it is built and what is left. Whatever was never written down comes from a **questionnaire** filled in by whoever knows (`docs/traspaso-cuestionario.md`), whatever is missing is shown as a gap, and it **never carries secrets**: it says where they live. **Versioned and approved** |

Aliases: `aiba df` · `aiba planificacion sprints` · `aiba planificacion proyecto` · `aiba kpis` · `aiba bienvenida` · `aiba traspaso`.

> `aiba metrics` is not a step of the method: it is an observation layer **independent of the rest and runnable at any time**. It always keeps what is measured apart from what is estimated, and it refuses to publish savings figures that do not hold up — an invented ROI KPI does more damage than no KPI at all, because it is used to decide.

**Generic by default, and it asks first.** The document comes out with no logos and no corporate colours, and the command asks whether you want to apply a brand — from a local folder or a URL — with "no brand" as the recommended option. A functional design ends up in the hands of a client with their own identity: generating it with the author's brand forces a rewrite. Because it uses **native Word styles** (`Heading 1/2/3`, a table style, editable header and footer, the table of contents as a `TOC` field), applying any identity afterwards is changing the style, not reviewing the document.

**It does not invent.** Whatever cannot be derived from the documentation is marked `[PENDIENTE: ...]` and produces a row under **Open points**, which turns gaps into assignable work instead of plausible text. A functional design gets signed and developed against.

**It re-edits without destroying.** When the `.docx` already exists, it regenerates only the affected sections, keeps whatever the analyst wrote by hand and **adds** a row to the version control table instead of overwriting it.

### `aifg` — Figma design down to the story (plugin `aifg`, 2 commands, optional)

| Phase | Command | What it does |
|------|---------|----------|
| 2.3+ | `aifg capture` | Extracts the nodes from the Figma file, normalises them (component definitions + a composition map per story), exports the images and resolves the story ↔ design link, surfacing only what is not obvious |
| — | `aifg update [component\|story]` | Re-captures a specific piece when the design changes, detects the overrides left orphaned and reports which stories are affected, separating the ones already closed |

Nothing is missing without this plugin: `aisdd implement change` reads `docs/guia-estilos.md` and, when that is missing too, improvises. With it, it also reads the design of **its own** story.

### `aiad` — Human-first execution, *ai-in-the-loop* (plugin `aiad`, 11 commands)

These cover the **execution phase** (a human-first alternative to `aisdd`); they do not follow the AIDD phase numbering, they are grouped by intent.

| Group | Command | Does |
|-------|---------|------|
| Think | `aiad design [explore\|plan]` | Explore options or plan the attack on a story (it writes no production code) |
| Think | `aiad explain` | Explain code, libraries, patterns or errors (as a mentor) |
| Think | `aiad rubber-duck` | A Socratic session to think out loud |
| Build | `aiad tdd` | Failing tests for what you are about to build (you implement) |
| Build | `aiad test [unit\|e2e]` | Fill in tests over existing code |
| Improve | `aiad review [correctness\|quality\|perf]` | A teaching review + an HTML report with the referenced code; it applies no fixes |
| Flow | `aiad pair` | Sustained pair programming (you drive, the AI navigates) |
| Flow | `aiad bridge [to-sdd\|to-aiad]` | The story ↔ change bridge to jump between AIAD and SDD |
| Flow | `aiad unblock` | The "I am stuck" hub: triage and routing to the right skill |
| Flow | `aiad save` | Commit + push of everything, no questions asked |
| Record | `aiad journal [log\|report]` | The authorship journal (*craft ratio*: what you write versus what you delegate) |

## Why you need all four

They are not four copies of the same package: they are **four pieces of one flow** that call each other. The full AIDD-SDD method runs from capturing requirements to executing each change, and along the way:

1. **`aidd` covers definition and design** (Phases 0–2: requirements → stories → architecture → style guide). It is the "what".
2. **`aisdd` covers execution** (Phases 3–4: a roadmap by context budget — aware of the `sprint-plan` — and the `open/implement/close change` cycle on OpenSpec, with an audit trail and Jira integration). It is the "how it gets built".
3. **`aiba` covers what the business sees** (Step 1.4, the functional design per story, Phase 3.5 and the measurement: story review → functional design → resource plan → sprints → KPIs). It is the "how much" and the "when". It is **self-contained**: it can be used without OpenSpec, and its documents are what `aisdd roadmap` reads to align with the calendar.
4. **`boosters` is the shared dependency** of the three above. It is not optional if you use the full flow:
   - `aidd prototype` (Phase 2.2) **redirects to `booster-ux`** to build the prototype screens.
   - `aisdd prototype-ux` and `aisdd uml` (from the `aisdd` plugin) **call `booster-ux` and `booster-uml`** to document each change.
   - The planning skills of `aidd`, `aisdd` and `aiba` **call `booster-docs`** to leave, next to each generated `.md` (requirements, stories, roadmap, sprint plan…), a complementary HTML view for human consumption (the Markdown remains the single source of truth).
   - If `boosters` is not installed, those steps warn that the booster is missing and generate no prototypes, no diagrams and no HTML views.

Claude Code **does not resolve dependencies between plugins automatically**: each plugin is installed separately, and none of them ships another's scripts or hooks. That is why the end-to-end flow needs all four. (If you are only going to define and design, `aidd` works on its own; if you are only going to plan and measure, so does `aiba` — but the recommended, complete installation is all four.)

## AIAD — human-first execution (optional and independent)

`aiad` is **not part of the trio above**: it is an independent plugin with an inverted philosophy for the execution phase. Where `aisdd` is *human-in-the-loop* (the AI is the engine, you validate), `aiad` is **ai-in-the-loop**: **you are the engine** writing the code and the AI **augments you on demand** (*pull, not push*). It gives the engineer back authorship, mastery and the flow of the craft without giving up AI leverage.

11 skills grouped by intent:

- **Think** (they advise, they do not write code): `aiad-design` (options/approach), `aiad-explain`, `aiad-rubber-duck`.
- **Build** (the AI only writes tests): `aiad-tdd` (failing tests → you implement), `aiad-test` (`unit`/`e2e` over existing code).
- **Improve**: `aiad-review` (`correctness`/`quality`/`perf`, teaches the why, applies no fixes).
- **Flow & control**: `aiad-pair` (driver/navigator), `aiad-bridge` (the story ↔ change bridge to jump between AIAD and SDD), `aiad-unblock` (the "I am stuck" hub), `aiad-save` (commit + push, no questions).
- **Record**: `aiad-journal` (the authorship journal / *craft ratio*).

It also ships an optional **hook** (`hooks/`) that factually records which files the AI touches (real authorship, not self-declared; opt-in per project) and a **subagent**, `aiad-reviewer`, that isolates the review so it does not pollute your working context.

**Standalone use:** `aiad` can be installed and used **on its own**, on any repo, with or without AIDD/SDD. It reads the AIDD artifacts (`docs/detalle-historias-usuario.md`, `arquitectura-base.md`…) *when they exist*, but does not require them. Its only external dependency is on `aisdd`: `aiad-bridge` needs OpenSpec/aisdd-specs installed to switch engines (without it, it says so and you carry on standalone). You pick the engine **per story** and can change it midway.

> Authorship: the `aiad` plugin is an original creation (Julio Fernández), independent of the rest of the marketplace.

## Installation (private repository)

Because the repo is **private**, Claude Code clones it using **your local git credentials**. You need read access to `grananda/aidd-marketplace` and git authenticated on that machine.

### 1. Make sure you have access to GitHub (once per machine)

Either option works:

```bash
# Option A — GitHub CLI (recommended)
gh auth login            # pick HTTPS; it configures git's credential helper

# Option B — check that you already have access
gh repo view grananda/aidd-marketplace   # if you can see it, your git can clone it
```

If you use SSH instead of HTTPS, that works too as long as your key has access to the repo (see the SSH URL variant below).

### 2. Add the marketplace and install the plugins (inside Claude Code)

```text
# Add the marketplace (once per machine)
/plugin marketplace add grananda/aidd-marketplace
#   HTTPS URL variant:  /plugin marketplace add https://github.com/grananda/aidd-marketplace.git
#   SSH variant:        /plugin marketplace add git@github.com:grananda/aidd-marketplace.git

# Install the four plugins of the integrated flow
/plugin install aidd@aidd-sdd
/plugin install aisdd@aidd-sdd
/plugin install aiba@aidd-sdd
/plugin install boosters@aidd-sdd

# Optional and independent: human-first execution (ai-in-the-loop)
/plugin install aiad@aidd-sdd

# Optional: Figma design down to the story
/plugin install aifg@aidd-sdd

# Check
/plugin list
/plugin            # interactive menu (Discover / Installed / Marketplaces / Errors)
```

If `/plugin marketplace add` fails with an authentication error or "repository not found", it is almost always access or credentials: go back to step 1 (you are not a collaborator on the repo, or git is not authenticated on that machine).

### 3. Usage

Once installed, each skill is *namespaced* by its plugin:

- `/aiba:aiba-sprint-planning`, `/aidd:aidd-requirements`, …
- `/aisdd:aisdd-specs` (`aisdd …` commands; legacy alias `native-ai …`)
- `/boosters:booster-ux`, `/boosters:booster-uml`, `/boosters:booster-docs`
- `/aiad:aiad-tdd`, `/aiad:aiad-review`, `/aiad:aiad-save`, …
- `/aifg:aifg-capture`, `/aifg:aifg-update` (commands `aifg capture`, `aifg update`)

They also trigger from plain language and from their internal commands (`aiba sprint-planning`, `aisdd open change`, `aiad tdd`, `aiad review`, …).

### Automatic activation per project (for a team)

In a project's `.claude/settings.json` you can register the marketplace and pre-enable the plugins for the whole team (each member needs access to the private repo):

```json
{
  "extraKnownMarketplaces": {
    "aidd-sdd": { "source": { "source": "github", "repo": "grananda/aidd-marketplace" } }
  },
  "enabledPlugins": {
    "aidd@aidd-sdd": true,
    "aisdd@aidd-sdd": true,
    "aiba@aidd-sdd": true,
    "boosters@aidd-sdd": true,
    "aiad@aidd-sdd": true,
    "aifg@aidd-sdd": true
  }
}
```

## Other platforms: Codex and Cline

The marketplace is built for Claude Code, but **Codex installs it as is** from this very repository: it reads `.claude-plugin/marketplace.json` and the `plugin.json` files without translation, and no extra manifest is needed.

| | Claude Code | Codex | Cline |
|---|---|---|---|
| **Skills** | Yes | Yes (it warns when it shortens descriptions to fit its budget) | Yes, **but they have to be linked**: see below |
| **Hooks** | Yes | Yes, they are registered and trusted by hash | **No** — its plugin model is a TypeScript module on its SDK |
| **Scripts** (`${CLAUDE_PLUGIN_ROOT}`) | Yes | Yes, **resolving the path** (the variable arrives empty) | Yes, same as Codex |
| **Audit trail** (`audit.py`) | Yes | Yes, because of the above | Yes, because of the above |
| **Activity log** | Yes, via hook | Yes, **written by `audit.py`** | Yes, **written by `audit.py`** |
| **`aiba metrics` KPIs** | Yes | Yes, with the baseline declared | Yes, with the baseline declared |

**Two things break in Codex, and neither is fixable from here.**

**1. The scripts: solved.** `${CLAUDE_PLUGIN_ROOT}` **arrives empty** in Codex, so a `python3 "${CLAUDE_PLUGIN_ROOT}/…/audit.py"` would become `/…/audit.py` and fail. The 21 documents that call a script now carry the **resolution rule**: when the variable does not resolve, the script is still on disk — find it once with `find` and use its absolute path. With that, the audit trail, the document stamping, the KPIs and the HTML views all work.

**2. The activity log is written by the command, not the hook.** Hooks packaged inside a plugin **are registered and not executed** in Codex, and in Cline there is no compatible mechanism. So where they do not run, **`audit.py`** writes it: it already runs on every `aisdd` command and already knows when each one started and finished.

Who writes it **is declared**, not guessed, and `aisdd init` settles it in `openspec/config.yaml`:

```yaml
activity:
  source: hooks   # hooks | skills
```

With `hooks` the hook is in charge and `audit.py` leaves the log alone; with `skills` it is the other way round. **Never both** — duplicating every line does not fail: it inflates attended time and the speed-up comes out better than it was. Without the key, `hooks` is assumed.

**And the baseline is declared in the report.** A command only sees itself; the hook sees the whole turn, including reviewing, talking and iterating. With `source: skills` attended time is **a lower bound**, and `aiba metrics` says so instead of presenting it as equivalent.

**In Codex, any change to the hook means trusting it again.** Codex stores a `trusted_hash` per hook entry; when a new version of the marketplace changes `aidd-activity-hook.sh`, **logging stops until you approve it** in an interactive session. It does not error: it simply stops writing. If you update and the metrics go flat, look there first.

**In Cline it is not installed as a plugin.** `cline plugin install` fails, and rightly so: its plugins are TypeScript modules and ours are markdown. What Cline does read is **skills**, so they have to be linked where it looks for them — `~/.cline/skills/` or the project's `.clinerules/skills/`:

```bash
mkdir -p ~/.cline/skills
for s in <path-to-the-plugins>/*/skills/*/; do
  ln -sfn "${s%/}" ~/.cline/skills/"$(basename "$s")"
done
```

Do not link them into `~/.claude/skills/`: Claude Code looks there too and would load every skill twice.

With that, Cline gets the skills, the audit trail, the stamping and the computed KPIs. **What there is not is an activity log**, so `aiba metrics` is missing attended time: Cline's plugin model is a TypeScript module on its SDK and there is nowhere to hook into.

## Activity log (opt-in)

The six plugins ship a `PostToolUse` hook (`hooks/aidd-activity-hook.sh`) that leaves a trace of what has been done to the code: **date and time, user, skill executed and file worked on**, one line per action.

**Who writes it resolves itself, on every execution.** In Claude Code the hook writes it, and it sees the whole turn. Where plugin hooks do not run — Codex, Cline — **`audit.py`** writes it on every `aisdd` command.

**There is nothing to configure.** The decision is taken per execution by looking at whether the agent runs hooks, not per project: the same project is opened from different agents depending on who works on it, so pinning it in `openspec/config.yaml` produces the two failures worth avoiding — and neither errors:

| If you pin… | with the agent it does not suit | what happens is… |
|---|---|---|
| `activity.source: skills` | Claude Code | **it is logged twice** and attended time comes out inflated |
| `activity.source: hooks` | Codex or Cline | **nothing is logged** |

The key still exists as an override (`hooks`, `skills`, `auto`) for whoever knows what they are doing, and when it contradicts the platform **`audit.py` warns** instead of letting it slide.

With the source set to `skills`, attended time is **a lower bound** — a command does not see the time spent reviewing, talking or iterating — and `aiba metrics` declares that in the report instead of presenting it as equivalent.

**It is enabled per project by creating the log file** (without it nothing is written, in any project):

```bash
touch docs/aidd-activity.md   # enable
rm docs/aidd-activity.md      # disable
```

From then on, `docs/aidd-activity.md` fills itself in:

```
- 2026-08-05T09:12:44Z | user:jfernandez | skill:aidd:aidd-user-story-details | ctx:HU-07 | run | note:HU-07 fases=4
- 2026-08-05T09:14:02Z | user:jfernandez | skill:aidd:aidd-user-story-details | ctx:HU-07 | file:docs/detalle-historias-usuario.md | note:-
- 2026-08-05T09:18:20Z | user:jfernandez | skill:- | ctx:HU-07 | turn | note:dur=336s skills=1 files=3
```

- One `run` line per skill invoked (with its arguments in `note:`), and one `file:` line per file the AI writes, **attributed to the skill that was active** at that moment.
- One `turn` line when each turn closes, with its **duration**. Those are what make it possible to measure *attended* time (you asked for something and waited) instead of calendar time, which would count nights and meetings. A turn that touches nothing leaves no trace.
- The `ctx:` field is the **user story or change** in flight: it is detected from the arguments (`HU-07`) or from working inside `openspec/changes/<id>/`. That is what makes cycle time per story possible.
- Timestamps in **UTC** (`Z`), like the AIAD journal, so they sort correctly across machines and time zones.
- **Passive**: it only records. It never blocks an action, never edits code and never fails the session.
- **No duplicates**: the hook travels in all six plugins — including `aiba`, which is what later consumes it — so with several installed it fires several times for the same action; it deduplicates by `tool_use_id` and only writes the first.
- What you type by hand in your editor **does not go through the AI's tools and is therefore not logged**. The log traces the AI, it does not watch the human.
- It records neither the content of your prompts nor the code: only the skill, the file and the command arguments.

It is independent of `docs/aiad-journal.md` (plugin `aiad`), which answers a different question: **how much** you wrote versus what you delegated. You can have both, one or neither.

> **Note**: the `note:` summary is deterministic (the command arguments). A hook is a shell script with no model behind it, so it cannot write prose about what you asked for; for that, the skill itself would have to write it.

### KPIs from the log

With the log enabled, `aiba metrics` turns that trace into a report (`docs/kpis-ia.md` + HTML): attended time, planning versus execution split, cycle time per story or change, rework and code delivered.

It runs **whenever you want, as often as you want**: it only reads (the log, `git log`, the sizes in `docs/detalle-historias-usuario.md` for the baseline and, if the project uses AISDD, `openspec/audit/*.jsonl`) and modifies nothing in the project. If one of those sources is missing, it trims the report and says so, but does not fail.

**Specification quality (only with AISDD).** The rest of the report measures speed, and speed without quality is half the picture. Three figures come out of the audit trail that complete it without instrumenting anything new:

- **Corrections per change** — *specification* rework, complementary to churn, which measures *code* rework. They read differently: high churn with low corrections is usually legitimate refactoring; high corrections with low churn means the specs were wrong and someone absorbed it by guessing. Many corrections in one change point at its `open change`, not at a slow team.
- **% of decisions the AI resolved without asking** — how much autonomy the pre-flight is taking.
- **Real lead time `open change` → `close change`**, measured from the trace rather than inferred.

It is a **lower bound**: it only counts the corrections that made it into `decisions.md`. It is for comparing changes against each other, not as an exact count — and the report says so where it is read. It is switched off with `--no-audit`.

⚠️ **The log is not retroactive.** `git log` reaches the whole history, but the trace starts the day you created `docs/aidd-activity.md`. If you want to measure a sprint, enable it **before** it starts.

Savings are a different matter, and it is worth understanding why before showing a number to anyone:

- The log measures **attended time**, not total effort. It does not see reviewing, testing, typing by hand or meeting, and what you write in your editor does not go through the AI's tools.
- That is why `aiba metrics` **refuses to compute savings** unless the team declares its real effort over the measured window (`--real-days`, from timesheets or worklogs). Subtracting attended time from the baseline would give speed-ups of x100, which is exactly the kind of figure that does not survive an awkward question.
- The baseline is the human effort of the XS/S/M/L/XL sizes, and it is legitimate because it was declared **before** execution. It is not an after-the-fact adjustment.
- If the resulting speed-up is above x10, the report flags it as **not publishable** and explains that it almost always means under-declared effort or an inflated baseline.

## Recommended MCPs

The skills integrate two external services via **MCP**. Both are **optional**: without them everything works the same and the corresponding step is skipped with a notice (the skills never fall back to manual REST calls and never handle credentials). The skills locate tools **by function**, not by name, so any equivalent MCP variant works.

| MCP | Who uses it | What for |
|-----|--------------|----------|
| **Atlassian (Jira)** | `aiba-sprint-planning` · `aisdd-specs` | Pushing the sprint plan (sprints + Stories), sub-tasks per change, In Progress/Done transitions, re-phasing and rebuilding the link |
| **Figma** | `aidd-style-guide` · `aifg-capture` · `aifg-update` | Pulling the visual identity from the real design (palette, typography, spacing, tokens) and, with `aifg`, the node-by-node composition of each screen |

**Atlassian.** ⚠️ **Atlassian's official remote MCP does NOT expose the Agile operations** (creating sprints, adding or moving issues between sprints): it covers issues and transitions, but **is not enough for the `aiba sprint-planning` push** — we hit this on a real project and had to install another one. Our recommendation depends on what you need:

- **The full flow (sprint push included)** — a community MCP that exposes Jira's Agile API, for example [`mcp-atlassian`](https://github.com/sooperset/mcp-atlassian) with an API token (tools `jira_create_sprint`, `jira_add_issues_to_sprint`, `jira_get_sprints_from_board`, …). That is the one we use. Installation:

  1. Create an Atlassian **API token** at <https://id.atlassian.com/manage-profile/security/api-tokens>.
  2. Register the MCP in Claude Code (it needs [`uv`](https://docs.astral.sh/uv/); alternative: the `ghcr.io/sooperset/mcp-atlassian` Docker image from the same project):

  ```bash
  claude mcp add jira-agile \
    --env JIRA_URL=https://<your-org>.atlassian.net \
    --env JIRA_USERNAME=<your-email> \
    --env JIRA_API_TOKEN=<your-token> \
    -- uvx mcp-atlassian
  ```

  3. Check with `/mcp` that the server shows as connected and exposes the `jira_*` tools (including the sprint ones).

- **Only the aisdd change cycle** (sub-tasks, transitions — without creating sprints): the official remote MCP (OAuth) also works: `claude mcp add --transport sse atlassian https://mcp.atlassian.com/v1/sse`.

Jira requirements: a project with a **Scrum board** (sprints live on the board) and permission to create issues and sprints. Note: issue type names vary by project type (*team-managed* uses `Subtask`; *company-managed*, `Sub-task`) — the skills discover and verify them on their own before creating anything.

**Figma.** The skill suggests `figma-developer-mcp` (it needs a personal Figma token):

```bash
claude mcp add figma -- npx -y figma-developer-mcp --figma-api-key=<YOUR_TOKEN> --stdio
```

**Without an MCP there are no REST calls**, here either: the rule at the top of this section has no exception for Figma. The only alternative is a **design token export to JSON** (Tokens Studio, "Design Tokens"), which handles no credentials — and which gives tokens, **not node data**, so it serves `aidd style-guide` and does not replace `aifg`.

The `aifg` skills also need to be able to **export a node's image**. If the available server does not expose that, capture still works but **without a verification channel**: it is implemented from the JSON and there is nothing to compare against.

## Methodology

The AIDD-SDD methodology travels **inside** the `aidd` and `aisdd` plugins (the `methodology/` folder, mirror copies). The skills reference it as `${CLAUDE_PLUGIN_ROOT}/methodology/native-ai-aidd-sdd.md`, so it resolves once installed in any repo. It is read-only reference material; it is not loaded automatically. **It is written in Spanish.**

The `aiba` and `aiad` plugins carry their own, because they cover layers the AIDD-SDD document no longer describes: `native-ai-aiba.md` (the set that faces the business: the nine skills, the AI Delivery Manager role, Step 1.4, Phase 3.5 and the measurement) and `native-ai-aiad.md` (the *ai-in-the-loop* manifesto, the skill catalogue, the story ↔ change bridge and the authorship journal).

**FAQ.** [FAQ-EN.md](FAQ-EN.md) answers the frequent questions about the AISDD cycle: what each command creates (`open`/`implement`/`close change`), what happens in Jira at each step, who creates Stories and sprints, and the edge cases (a lost link, re-phasing, sprints measured in hours).

**HTML views.** Next to each methodology `.md` there is a sibling `.html` (same folder) rendered with `booster-docs`, for comfortable human reading with a navigable table of contents — [native-ai-aidd-sdd.html](plugins/aidd/methodology/native-ai-aidd-sdd.html), [getting-started](plugins/aidd/methodology/native-ai-aidd-sdd-getting-started.html), [native-ai-aiba.html](plugins/aiba/methodology/native-ai-aiba.html) and [native-ai-aiad.html](plugins/aiad/methodology/native-ai-aiad.html). The Markdown remains the **single source of truth**.

## Publishing and CI

The marketplace has a **global version** in the `VERSION` file at the root. It does not replace each `plugin.json` version — those still decide what the user reinstalls — it groups a set of changes into something publishable.

The numbering **starts at `1.6.0` and continues that of `native-ai-specs` v1.6.0**, of which this marketplace is the maintained continuation. Starting at `1.0.0` would have suggested a different, younger product than it really is.

**To publish**: bump `VERSION` in the same PR that changes whatever it changes. On merge to `main`, the `release.yml` workflow checks whether the `v<VERSION>` tag exists and, when it does not, creates the tag and the release. The gate is the tag and not the branch, so the workflow is idempotent: you can merge several PRs without touching `VERSION` and nothing happens, and re-running it does not duplicate releases.

The release notes are generated by `release_notes.py` comparing against the previous tag, in order of what is most urgent to read: **Watch out when updating** (major versions and commits marked with `!`), **What is new** (`ROADMAP.md` entries that move to implemented), the tables of **which plugins and which skills change version**, the **skills that are no longer where they were** (moved between plugins or removed) and, folded away, the commits. Whoever consumes the marketplace wants to know two things — whether something breaks and whether they have to reinstall — and both come before the detail. A skill that disappears is the most expensive break, and it is exactly the one you cannot see by walking only through what exists today.

**Forgetting to bump a version** is the obvious failure mode of maintaining them by hand, so `validate.yml` checks it both ways on every PR: if some `plugin.json` changes version and `VERSION` does not, it fails; and if a plugin has modified files and the same version, it fails too. The second one is the silent one: Claude Code believes the installed copy is up to date, so the change never reaches the user.

That same workflow runs on every PR and on `main`:

| Check | What it prevents |
|---|---|
| `check_manifests.py` | `marketplace.json` pointing at a plugin that does not exist, or a plugin on disk that is not declared. It breaks everyone's installation and does not fail until someone tries |
| `check_skills.py` | A `SKILL.md` without valid frontmatter, with a `name` that does not match its directory or without a `description`: the skill does not load, or the model does not know when to invoke it |
| `check_plugin_assets.py` | A skill calling `${CLAUDE_PLUGIN_ROOT}/…` for a file its plugin does not ship, and the copies replicated across plugins (the activity hook, `stamp_doc.py`) drifting apart |
| `check_skill_refs.py` | A skill naming a `references/…` or a `scripts/…` that is not where it looks for it, an example command using a path relative to the skill (it runs from the user's project, where it does not exist), a `references/` left behind that nobody links, or a path from the previous packaging surviving (`.agents/skills/`, `%USERPROFILE%`) |
| `check_contracts.py` | A documented invocation — a skill's or this README's — passing a flag the script does not accept, or dropping a required one (flag or positional), and a document with an HTML view having no entry in `DOC_TYPES` |
| `check_generated_html.py` | A methodology `.html` not matching its `.md`, and the `aidd/` and `aisdd/` copies drifting apart |
| `check_maps.py` | A skill with no row in the [maps](docs/maps/README.md) or missing from their mindmap, a plugin's skill count not being the real one, or a link in the maps pointing at a file or a section that does not exist |
| `py_compile` | A Python script that does not compile |
| `check_mojibake.py` | Badly encoded UTF-8 in the markdown files, using the skill's own script |

They all come from real failures, and three deserve a comment because the failure **makes no noise**. The HTML one, because the drift happens **without anyone editing the `.md`**: changing `render_docs_html.py` is enough, and that is how the AIAD methodology HTML fell behind for two PRs without anyone noticing. The assets one, because **Claude Code installs each plugin separately**: moving skills from `aidd` to `aiba` with `git mv` made `stamp_doc.py` disappear from `aidd`, where eight skills still run it. Nothing fails when you make the change; it fails at the user's machine.

And the paths one, because **skills are loaded lazily**: `SKILL.md` is an index and the rules live in `references/*.md`, which the agent reads only when the index tells it to. A path that does not resolve raises no error — the agent does not find the file, carries on without it, and the rule it contained simply is not applied — which is the failure mode that looks most like everything working. The convention it imposes: **same skill** → `references/x.md`; **another skill in the same plugin** → `${CLAUDE_PLUGIN_ROOT}/skills/<skill>/references/x.md`; **another plugin** → no path, name the skill only, because the user may not have it installed.

## Maintenance

- **When to split a `SKILL.md` into `references/`**: split when **both** conditions hold — more than ~400 lines **and** two or more entry points that do not share a flow. With a single command you do not split, however large it is: that flow runs end to end, so splitting it loads the same lines *plus* the index.

  Today only `aisdd-specs` meets them (8 commands): it is a 94-line index + `references/*.md` per command. The next skill by size has 322 lines and a single command, and in the four largest ones the "command flow" section takes up 70-75 % — there is nothing conditional worth leaving unloaded.

  Worth watching: `aiba-sprint-planning` carries the optional Jira push inside it. If that part grows and the skill approaches 400-500 lines, there would be two real paths (plan and push) and splitting would make sense.
- **Versioning**: each `plugin.json` sets `version` (semver). **Bump the version when publishing changes**; otherwise users who already installed will not get them (Claude Code believes they are on the same version). After pushing changes, users update with `/plugin marketplace update aidd-sdd`.
- **Regenerating the methodology HTML** (mandatory when editing a `.md` under `methodology/`; the `aisdd` copy mirrors **both the `.md` and the `.html`**, and `validate.yml` checks both, so the final `cp` copies both). The `--title` values stay in Spanish on purpose: they are the titles of the Spanish documents, and `check_generated_html.py` compares them:

  ```bash
  python3 plugins/boosters/skills/booster-docs/scripts/render_docs_html.py \
    --input plugins/aidd/methodology/native-ai-aidd-sdd.md \
    --output plugins/aidd/methodology/native-ai-aidd-sdd.html \
    --title "Native AI · AIDD-SDD — Metodología AI-Native"
  python3 plugins/boosters/skills/booster-docs/scripts/render_docs_html.py \
    --input plugins/aidd/methodology/native-ai-aidd-sdd-getting-started.md \
    --output plugins/aidd/methodology/native-ai-aidd-sdd-getting-started.html \
    --title "AIDD-SDD — Getting Started"
  python3 plugins/boosters/skills/booster-docs/scripts/render_docs_html.py \
    --input plugins/aiba/methodology/native-ai-aiba.md \
    --output plugins/aiba/methodology/native-ai-aiba.html \
    --title "Native AI · AIBA — Análisis de negocio, entrega y medición"
  python3 plugins/boosters/skills/booster-docs/scripts/render_docs_html.py \
    --input plugins/aiad/methodology/native-ai-aiad.md \
    --output plugins/aiad/methodology/native-ai-aiad.html \
    --title "Native AI · AIAD — AI-Augmented Development"
  cp plugins/aidd/methodology/native-ai-aidd-sdd.md \
     plugins/aidd/methodology/native-ai-aidd-sdd.html \
     plugins/aidd/methodology/native-ai-aidd-sdd-getting-started.md \
     plugins/aidd/methodology/native-ai-aidd-sdd-getting-started.html \
     plugins/aisdd/methodology/
  ```
- **Mermaid version**: `booster-docs` and `booster-uml` pin the same version and `sha256` of the bundle (`MERMAID_VERSION`, `MERMAID_SHA256`, `MERMAID_SIZE` in their respective scripts). They share the `mermaid.min.js` under `docs/html/`, so **if you update the version, do it in both** and recompute the hash:

  ```bash
  curl -sS -o /tmp/m.js https://cdn.jsdelivr.net/npm/mermaid@<version>/dist/mermaid.min.js
  wc -c /tmp/m.js && sha256sum /tmp/m.js   # size and hash that go into both scripts
  ```
- **Shared activity hook**: `hooks/aidd-activity-hook.sh` is the **same file** in all **six** plugins (each installed plugin is self-contained, they cannot share files). If you touch it, copy it to all six and check they match — and run `check_activity_hook.py`, which verifies it still logs the same thing in Claude Code and in Codex:

  ```bash
  cp plugins/aidd/hooks/aidd-activity-hook.sh plugins/aisdd/hooks/
  cp plugins/aidd/hooks/aidd-activity-hook.sh plugins/aiad/hooks/
  cp plugins/aidd/hooks/aidd-activity-hook.sh plugins/boosters/hooks/
  sha256sum plugins/*/hooks/aidd-activity-hook.sh   # all six must match
  ```
- **Making it public** (if that ever applies): `gh repo edit grananda/aidd-marketplace --visibility public`. Installation would then need no credentials.
- **Local development** before publishing: `claude --plugin-dir ./plugins/aidd` (a single plugin) or `/plugin marketplace add ./` (a local marketplace); validate with `claude plugin validate ./`.

---

NTT DATA Spain GDN-e.
