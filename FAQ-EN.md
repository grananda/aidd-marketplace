# FAQ — The AISDD process

> **Español:** [FAQ.md](FAQ.md). The Spanish version is the source of truth: if the two ever disagree, the Spanish one wins.

Frequently asked questions about the **AISDD** execution cycle (`aisdd-specs`): what each command does, what it touches in Jira and what it does not. A quick reference for workshops and onboarding; the normative detail lives in `plugins/aisdd/skills/aisdd-specs/SKILL.md`.

> Commands use the primary prefix `aisdd`; the legacy alias `native-ai <cmd>` is equivalent.

## The cycle in one picture

```text
aisdd init  →  aisdd roadmap  →  for each change:
                                   aisdd open change    (specs · Jira: records, moves nothing)
                                   aisdd implement change (code · Jira: → In Progress)
                                   aisdd close change     (archive · Jira: → Done)
```

On an **existing project**, `aisdd init` adds a step before all this: it analyses the code and seeds the **base specs** in `openspec/specs/`, so that changes apply deltas on top of the real state instead of starting from scratch. With `multilane` roadmaps, each dev picks their line with `aisdd lane switch` and the cycle runs **once per lane, in parallel**.

---

## What does `aisdd open change [what-you-want-to-build]` create?

1. **A pre-flight of open questions** (every blocking one is asked; preferences and confirmations are capped per project in the `preflight` section of `openspec/config.yaml`): the answers are persisted in `openspec/changes/<slug>/decisions.md`.
2. **The OpenSpec change** (`openspec new change`): the `openspec/changes/<slug>/` folder with its validated specs — `proposal.md`, `design.md`, `spec.md` (one or more) and the `decisions.md` from the pre-flight.
3. **UML diagrams** (HTML via `booster-uml`) **only when the change warrants them**: multi-component flows, new entities, state machines, integrations. On trivial changes (scaffolding, config, copy) they are skipped with a notice; `aisdd uml [change-slug]` generates them on demand.
4. **An audit entry** in `openspec/audit/YYYY-MM.jsonl` (input/output hashes, model, decisions).

**No code is created**: opening a change is designing and validating the specs. Code arrives with `implement`.

## What happens in Jira on `open change`?

**It records, it moves nothing.** Stories stay in **To Do** — opening is designing specs, not starting work.

- The **user story** the change implements is identified and noted in `proposal.md` and in `docs/jira-sync.md`.
- **Hybrid model, decided per user story** (not per change):
  - A story delivered by **a single change** → **nothing is created** in Jira; the change operates directly on the Story.
  - A story split across **2 or more changes** → the **sub-task for this change** is created under that story's Story (in To Do), so progress can be tracked atomically.
- One change can mix both modes when it implements several stories.

## What happens on `aisdd implement change [change-slug]`?

1. **A pre-flight of open questions** about the change's specs (it reads the previous `design.md`, `proposal.md`, `spec.md` and `decisions.md`; blocking questions are unlimited, the rest follow `preflight` in `config.yaml`; unanswered blocking questions stop the command).
2. **Code implementation** (`openspec instructions apply --change <slug>`): the AI writes the code following the specs.
3. **Jira**: moves to **In Progress** the Stories of **every** user story the change implements (and the change's sub-task, if that story is split), **assigning** them to the user authenticated in the MCP (or to `assignee_override`).
4. An audit entry.

## What happens on `aisdd close change [change-slug]`?

1. **The change is archived** (`openspec archive`): it is no longer open and its specs are consolidated.
2. **Jira**, for each user story in the change:
   - **Story delivered by a single change** → its **Story goes to Done** directly.
   - **Split story** → the **sub-task for this change goes to Done**; the **Story only goes to Done once ALL its sub-tasks are Done**. If any is missing, the Story stays In Progress and the summary names the changes still pending — a user story is never closed halfway.
3. An audit entry.

## Summary: Jira per command

| Command | Story in 1 change (direct Story) | Story in 2+ changes (sub-task) |
|---------|----------------------------------|--------------------------------|
| `open change` | Records the mapping; the Story stays in To Do | Creates the change's sub-task (To Do) |
| `implement change` | Story → **In Progress** (+ assignment) | Sub-task **and** Story → In Progress |
| `close change` | Story → **Done** | Sub-task → Done; Story → Done **only if all** its sub-tasks are Done |

---

## Who creates the Stories and the sprints?

`aiba sprint-planning` (Phase 3.5), in its optional push to Jira: it creates the **sprints** with dates on the Scrum board and **one Story per user story** assigned to its sprint, and initialises `docs/jira-sync.md` plus the `jira:` section of `openspec/config.yaml`. The aisdd commands **never create Stories or sprints** — only sub-tasks (when applicable) and transitions.

## Who starts the sprint?

**A human, on the Jira board** ("Start sprint"). The skills create sprints in *future* state and move issues between columns, but starting and closing a sprint is a team ceremony — by design.

## What about the roadmap? Does it touch Jira?

**No.** `aisdd roadmap` is entirely local: it generates `docs/roadmap.md`, the prompts and the `roadmap` section of `config.yaml`. If `docs/sprint-plan.md` exists, it phases the work **aligned to the sprints**; each phase's `change_hint` is the join key that `open change` later uses to know which user story (and which Story) it belongs to.

## What if I have no Jira configured?

Nothing breaks: every command works the same and the synchronisation **is skipped with a notice**. One exception: if there is **evidence of an earlier push** (the sprint plan mentions created Stories) but `docs/jira-sync.md` or the configuration is missing, the skill treats it as a **lost link** — it warns and offers to **rebuild the record** by reading the Stories from Jira (read-only; it never recreates issues).

## Why are issues never deleted or recreated?

Jira keys (`AT-7`) are **permanent**: a deleted issue burns its number forever and leaves gaps. That is why re-phasing **moves** user stories between sprints (and deletes only empty sprints, which burn nothing), rebuilding the link is read-only, and Stories are created **exactly once**.

## A story was in a single change and a re-phasing splits it in two. What happens?

The mode is resolved **at the moment of each command**: **new** changes create a sub-task from then on (work already done is not represented retroactively). The Story goes back to In Progress when the new change is implemented, and closes once its pending sub-tasks are Done.

## Do sprints measured in hours (a demo or a workshop) work instead of weeks?

Yes. The skills use neither dates nor sprint state in their logic — they operate on issues. Just remember Jira's own rules: a Scrum board has **one active sprint at a time**, and closing a sprint with open issues makes Jira ask you to move them to the next one.
