# Native AI · AIAD — AI-Augmented Development (ia-in-the-loop)

**Version:** 0.1
**Date:** 2026-06-27
**Tooling base:** `aiad-*` skills — on-demand augmentation for human-first development.
**Relationship to the rest of the marketplace:** complements AIDD and SDD. **It does not modify or replace anything that already exists.**

---

## 1. Philosophy — ia-in-the-loop

AIAD is the humanist counterpart for the execution phase. Where SDD puts the **AI as the engine** and the human as a checkpoint (*human-in-the-loop*), AIAD inverts the axis: **the human is the engine that writes the code, and the AI intervenes on demand** (*ia-in-the-loop*).

> **Founding principle:** The human is the **author by default**. The AI does not drive: it augments. It acts only when invoked, and by default it **advises, teaches, and proposes** rather than doing. The bounded exception is generating tests and, on explicit request, specific code fragments.

The motivation is not efficiency (SDD already covers that). It is **giving the engineer back authorship, mastery, discovery, and flow** — the dopamine of the craft — without giving up the leverage of AI.

### human-in-the-loop vs ia-in-the-loop

| | **human-in-the-loop (SDD)** | **ia-in-the-loop (AIAD)** |
|---|---|---|
| Default actor | The AI | The human |
| Role of the other | The human validates/approves | The AI advises/augments on demand |
| Optimizes for | Control, cost, speed | Authorship, mastery, learning, flow |
| Trigger | The AI runs the cycle | The human invokes the skill when needed (pull, not push) |
| Who writes the code | The AI | The human (the AI only writes tests and, on request, fragments) |

Neither is "better": they are tools for different moments. The choice is **per user story (US)**, and it can be switched mid-way (see §4, the bridge).

### AIAD principles

| Principle | Description |
|---|---|
| **Human-first** | The human authors the work that gives them mastery, learning, and satisfaction. |
| **Pull, not push** | No `aiad-*` skill acts on its own. The human invokes it when stuck or wanting help. |
| **Augment, don't replace** | By default the AI advises, asks, explains, and proposes. It does not touch your files unless explicitly and narrowly asked. |
| **Teach the why** | Socratic by default: the goal is for you to gain mastery, not dependency. |
| **Low ceremony** | Invoke and get a fast answer. No 7-question pre-flight: you are in the middle of the work. |
| **The US is the unit** | The human always works on user stories, never on OpenSpec changes. |
| **Engine reversibility** | A US can move from AIAD (human-engine) to SDD (AI-engine) and back, via the US <-> change bridge. |
| **Free will over guardrails** | AIAD does not police how much you delegate. The drift risk (delegating "too much") is acceptable: it is the human's freedom to decide how to work. The `aiad-journal` only *records* authorship; it never constrains it. |

---

## 2. Where AIAD fits in the marketplace

AIDD and SDD are untouched. AIAD slots in **only at execution**, as an inverted-philosophy alternative:

```
Phases 0-2  -- DEFINITION & DESIGN -------------------------------
  AIDD (human-in-the-loop)   <- stays as is. It is acceptable and
  requirements, US, detail,     desirable for the AI to produce this
  architecture, prototype       under human supervision. Nothing
                                rewarding is lost: supervising IS
                                the work here.
        |
        v  (US with acceptance criteria + approved architecture)
EXECUTION --------------------------------------------------------
  Choose the engine PER US:

   +-------------------------+        +-------------------------+
   | SDD (human-in-the-loop) |  <-->  | AIAD (ia-in-the-loop)   |
   | AI-engine: open/        | bridge | Human-engine: you write |
   | implement/close change  | US <-> | the code; the aiad-*    |
   | Optimizes cost/time     | change | skills augment you       |
   +-------------------------+        +-------------------------+
```

**The "spec" you code against in AIAD already exists**: it is `docs/detalle-historias-usuario.md` (US + acceptance criteria, produced by AIDD) + `docs/arquitectura-base.md`. AIAD **does not** regenerate specs: it consumes them.

---

## 3. Where OpenSpec fits

In AIAD, OpenSpec is demoted from **execution engine** to **optional wrapper**. Since you are the one implementing, the `open -> implement -> close change` cycle (designed for the AI to generate specs and apply them) is no longer the center.

- **Default mode (standalone):** the human works on **user stories**, not changes. The `aiad-*` skills read the US and the architecture if present, but **do not require OpenSpec**.
- **When a change is worth it:** because the US is large, because you want traceability/Jira, or because you want to **jump to SDD**. That is where the bridge comes in (§4).

---

## 4. The US <-> change bridge — switching between AIAD and SDD

The key idea: **an OpenSpec change is equivalent to a human user story.** That equivalence becomes a bidirectional engine switch, materialized by the `aiad-bridge` skill:

```
US (AIAD, human-engine)              OpenSpec change (SDD, AI-engine)
        |                                       |
        |   "I want the AI to take over"        |
        +--------------  wrap  ----------------->|   open change <us-slug>
        |                                       |   (the US becomes a change;
        |                                       |    follows the normal SDD cycle)
        |                                       |
        |   "I want to take back control"       |
        |<-------------  reclaim  --------------+   the change is treated as a US
        |                                       |   again; you keep writing
```

Bridge rules:

- The **stable unit is always the US**. The change is only its temporary "SDD form".
- In AIAD mode the human never edits the change directly: they open/close it through the bridge, which delegates to `aisdd-specs` when switching to SDD.
- The engine switch can happen **mid-US** (you start, the AI finishes; or vice versa).
- Without OpenSpec installed, `aiad-bridge` says so and you work standalone on the US.

---

## 5. Skill catalog (11 skills, 5 groups)

The overlap between near-identical skills is collapsed into a single skill with a *mode*; genuinely distinct singletons are kept. Each skill is **pull, not push**, and keeps **you as the author**.

| Group | Skill | Modes / focus | What it does |
|---|---|---|---|
| **Think** (advises, writes no production code) | `aiad-design` | `explore` (options/naming) · `plan` (how-to) | Explore the option space and plan the approach for a US |
| | `aiad-explain` | — | Explain code / library / pattern / error at your level |
| | `aiad-rubber-duck` | — | Reason out loud; the AI asks questions until you find your own answer |
| **Build** (the AI writes tests only) | `aiad-tdd` | — | Writes failing tests from the acceptance criteria; you implement to green |
| | `aiad-test` | `unit` · `e2e` | Fills missing unit or end-to-end tests over code you already wrote |
| **Improve** (feedback on your code; proposes, you apply) | `aiad-review` | `correctness` · `quality` · `perf` · `<base-branch>` | Reviews your code teaching the why, or proposes refactors/perf with trade-offs; `aiad review <base-branch>` (e.g. `develop`) runs a merge-readiness review of the whole branch diff. Emits a self-contained HTML report with numbered code fragments and proposed before/after changes |
| **Flow & control** | `aiad-pair` | — | Sustained driver/navigator session; orchestrates the other skills |
| | `aiad-bridge` | `to-sdd` · `to-aiad` | Wraps/reclaims the US as an OpenSpec change to switch AIAD <-> SDD |
| | `aiad-unblock` | — | Hub / triage when you are stuck and do not even know what to ask for |
| | `aiad-save` | — | Commits all pending changes and pushes the current branch, no questions asked — a quick-save for when you are in a hurry |
| **Record** | `aiad-journal` | `log` · `report` | Records what you authored vs delegated, and reports your authorship ratio |

> `aiad-save` is the one **action/utility** skill: unlike the advisory skills, it performs an autonomous git action (commit + push). It is still pull (you invoke it) and never destructive (no force-push, no branch changes); invoking it is your authorization.

### Shared DNA of every `aiad-*` skill

1. **Pull, not push** — they act only when invoked.
2. **You remain the author** — by default they advise/teach/propose; only `aiad-tdd`, `aiad-test` and (on request) a specific fragment write code, always bounded.
3. **Teach the why** — Socratic by default.
4. **No autonomous edits** to production files unless explicitly and narrowly requested.
5. **Read context if present** (the US, `arquitectura-base.md`, `guia-estilos.md`) but do not require the whole SDD apparatus.
6. **Low ceremony** — no long pre-flight; quick response because you are in flow.
7. **Optional journal** — if you want, they append a line to `docs/aiad-journal.md` (what you did, what the AI advised/generated). This is the human-first inverse of the SDD audit: it records *your* authorship, it does not police the AI.

---

## 6. The human-first split of work

AIAD splits along **two axes**, not just efficiency:

| | **Low human value** | **High human value** |
|---|---|---|
| **High AI gain** | Automate (tests, boilerplate, scaffolding) -> `aiad-tdd`/`aiad-test` and on-request fragments | **The human's zone** — the algorithm, the hard bug, the abstraction. You write it; the AI only advises (`aiad-design`, `aiad-rubber-duck`) |
| **Low AI gain** | Eliminate | Human core: taste, product judgment, naming. You decide; the AI is a sounding board (`aiad-design explore`) |

TDD is the paradigmatic case: **the AI writes the tests (toil), you write the code (dopamine)**. You are the one who makes the bar turn green.

---

## 7. The authorship journal

`docs/aiad-journal.md` is the human-first inverse of the SDD audit. The SDD audit traces AI provenance (who/what/which model) — a surveillance-of-AI artifact. The journal instead **records and celebrates what the human authored**.

- Every `aiad-*` skill can append a structured line when it helps you (US, type of help, what you authored vs what the AI generated).
- `aiad-journal report` summarizes your **authorship ratio** (% you wrote vs % delegated) per US, per period, or overall.
- It is a **signal, not a gate**: it never blocks delegation. Use it to see your own craft trend, for retrospectives, or to argue the upskilling/retention value of working human-first.

Line format (append-only Markdown list):

```
- <date> | US:<us-id> | skill:<aiad-skill> | mode:<mode> | authored:<human|ai-tests|ai-fragment|advice-only> | note:<one line>
```

---

## 8. Automation: the right primitive for each capability

AIAD is *pull, not push*, so **skills are the default primitive** for everything advisory and conversational. Two capabilities are better served by other Claude Code primitives:

### The journal hook (the one legitimate "push")

A plugin hook (`hooks/hooks.json` -> `hooks/aiad-journal-hook.sh`) runs on `PostToolUse` for `Write`/`Edit`/`MultiEdit` and appends an `ai-edit` line to `docs/aiad-journal.md`. It is the only place AIAD acts automatically, and it is allowed precisely because it **only records, never controls**:

- **Opt-in per project:** it does nothing unless `docs/aiad-journal.md` already exists.
- **Passive & safe:** `async`, non-blocking, always exits 0; never edits code, never asks.
- **Factual authorship:** AI edits go through tools and get logged; hand-typed human edits are invisible to the hook and thus theirs. The craft ratio stops being self-reported.

This respects *free will over guardrails*: it is a measurement, not a gate.

### The review subagent (context isolation)

`aiad-review` ships a companion subagent, `aiad-reviewer` (`agents/aiad-reviewer.md`), with **read-only tools** (Read, Grep, Glob, Bash — no edit tools, so it structurally cannot apply fixes). The skill delegates the heavy reading (diff, files, architecture/style docs) to it so the human's working context stays clean, and relays back only the findings report, which the skill renders as a **self-contained HTML report** (numbered code fragments, impact and why per finding, proposed before/after changes, test gaps) alongside the terminal summary. The same isolation pattern can later be applied to `aiad-test` and the generation burst of `aiad-tdd`; it must **not** be applied to `aiad-pair` (continuous collaboration) or the conversational skills.

### What stays a plain skill, and why hooks are otherwise wrong

Everything else (design, explain, rubber-duck, pair, unblock, bridge, save) stays a skill. Putting a hook on an advisory skill would make the AI act on its own — the opposite of ia-in-the-loop. Hooks are reserved here for passive recording only.

## 9. Roadmap

- **v0.1 (available):** the eleven catalog skills (§5) — `aiad-design`, `aiad-explain`, `aiad-rubber-duck`, `aiad-tdd`, `aiad-test`, `aiad-review`, `aiad-pair`, `aiad-bridge`, `aiad-unblock`, `aiad-save`, `aiad-journal`.
- **Candidate improvements (not built):** an AIAD `getting-started` guide; an `aiad help` command listing the catalog by type of blocker; richer authorship analytics on top of `aiad-journal`.
