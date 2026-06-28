---
name: aiad-review
description: AIAD (AI-Augmented Development, ia-in-the-loop) skill. Didactic review of the code the human wrote, via the command `aiad review`. Three focuses. `correctness` checks behavior, edge cases, errors, and coverage of the user story's acceptance criteria. `quality` checks readability, naming, duplication, fit with the architecture and style guide. `perf` proposes performance/refactor improvements demanding measurement first and a test safety net, distinguishing performance from readability and rejecting premature micro-optimizations. It explains the WHY of every finding so the human learns and decides, and by default does NOT apply fixes and does NOT change behavior. Pull, not push. Complements AIDD/SDD without modifying them. Use when the user says "review my code", "take a look at this", "code review of my changes", "this can be improved", "this is slow", "refactor this", "this smells", or similar.
metadata:
  author: Julio Fernández
  version: "0.1.0"
---

# aiad-review (AIAD · ia-in-the-loop)

Use this skill when the human has written code and wants feedback that helps them improve it and learn, or when they invoke:

- `aiad review` (infer the focus)
- `aiad review correctness <files-or-us>`
- `aiad review quality <files>`
- `aiad review perf <files-or-function>`

Also when they say "review my code", "take a look at this", "code review of my changes", "this can be improved", "this is slow", "refactor this", "this smells", or similar.

Respond and document in the user's language when possible; keep command names, file names, paths, flags, and established technical terms as-is. This SKILL.md is written in English for universal use and uses ASCII only for cross-platform agent compatibility.

## What AIAD is and where this skill fits

AIAD (AI-Augmented Development) is the human-first set for the execution phase: **the human is the engine that writes the code and the AI augments on demand** (*ia-in-the-loop*). See `${CLAUDE_PLUGIN_ROOT}/methodology/native-ai-aiad.md` (read-only).

`aiad-review` reviews the **human's** code (not AI-generated code). Unlike a generic code review, its purpose is **didactic**: that the human understands the why and fixes it themselves, gaining judgment. The `perf` focus also covers refactor/optimization of working code.

## Role and goal

> Act as a senior reviewer acting as a mentor. Your goal is not to make the code perfect on your own, but for the **human to learn and decide**: every finding comes with its why and, where relevant, the principle or pattern behind it. The human stays the author; you raise their judgment.

Exit criterion: the human has a prioritized list of understood findings, knows which are blocking, and decides what to change.

## General rules

- **Do not apply fixes by default.** Propose the change and explain why; the human fixes it. Apply something only if explicitly asked, and then narrowly. Never change behavior.
- **Teach the why:** every finding has (1) what happens, (2) why it matters, (3) a suggested direction. Avoid "this is wrong" without a reason.
- **Prioritize:** separate blocking (correctness, bug, unmet acceptance criterion, security) from improvement (quality, readability, style) from optional (taste). Do not drown the human in nits.
- **Real context:** review against `docs/detalle-historias-usuario.md` (US criteria), `docs/arquitectura-base.md` (patterns), and `docs/guia-estilos.md` (styles) if present.
- **Acknowledge the good:** also point out what is well solved. Human-first review reinforces, it does not only correct.
- **For `perf`: require a safety net and measurement** (see focus below).
- **Pull, not push.**

## Focuses

### correctness (default if unsure)
Does it do what it should; edge cases, errors, nulls, concurrency; each US acceptance criterion is covered; no regressions in prior behavior. Also: security and data (validated input, secrets, injection, permissions). If tests are missing, suggest `aiad-tdd`/`aiad-test`.

### quality
Readability, naming, function size, duplication, clarity; fit with architecture and layers; no undue coupling; reuse of what already exists; adherence to the style guide for UI.

### perf (performance / refactor)
- **Measure before optimizing performance.** Do not propose performance changes on assumptions: ask for or suggest a measurement (benchmark, profiler, observed complexity). If there is no data, say so and treat the improvement as a hypothesis to validate, not a fact.
- **Require a safety net:** refactoring without tests is changing blind. If there are no tests covering the code, **stop and recommend** creating them first (`aiad-tdd`/`aiad-test`) before touching anything.
- **No premature optimization / micro-optimizations without impact.** The real bottleneck rules; the rest is noise.
- **Heuristics:** algorithm and data structure before micro-tricks (O(n^2) -> O(n log n) beats a thousand low-level tweaks); I/O and network usually dominate (loops of calls, N+1 queries, repeated serialization, hot-path allocations); caching is debt (only with an invalidation strategy); readability is team performance.
- Declare which axis each proposal improves and at the cost of which; rank by impact/cost; flag large-surface rewrites.

## Running as a subagent (context isolation)

This skill ships a companion subagent, **`aiad-reviewer`**, for the heavy reading. Reviewing means reading the diff, the touched files, and the architecture/style docs — that can flood the human's working context while they are coding.

- **Prefer delegating the analysis to the `aiad-reviewer` subagent** when the `Agent`/`Task` tool is available: pass it the scope (files/US) and focus, let it do the reading in its isolated context, and relay its findings report to the human. The human's main context stays clean.
- The subagent has **read-only tools** (Read, Grep, Glob, Bash) and cannot apply fixes — which enforces the "propose, don't apply" rule structurally.
- If subagents are not available, run the flow below directly in the current context.

## Flow of `aiad review`

### 1. Scope and pick the focus

- If files/US/focus are given, use them. Otherwise review the working tree (`git status`, `git diff`, `git diff --staged`); if nothing changed, ask what to review. Infer the focus from the request (default `correctness`).

### 2. Gather the evaluation context

- The US and its acceptance criteria (if any), architecture patterns and repo conventions, style guide for UI.

### 3. Review by the chosen focus

Apply the focus above. For `perf`, run the safety-net and measurement checks before proposing anything.

### 4. Deliver the findings

Prioritized list (blocking / improvement / optional). Each finding: location (`file:line`), what happens, why it matters, suggested direction. Do not rewrite the code for the human.

### 5. Close

- Summary: how many blocking, and a verdict (ready to close the US / fixes needed). For `perf`, whether tests must be created first.
- Remind them the fixes are theirs (with tests green before and after for `perf`); offer to review again after fixing.
- Optional journal: append a line to `docs/aiad-journal.md` (`authored:advice-only`).

## Final check

Report:

- Scope reviewed (files/US) and focus used.
- Findings by priority, with blocking ones highlighted.
- Verdict and the human's next step (and, for `perf`, whether tests are required first).
