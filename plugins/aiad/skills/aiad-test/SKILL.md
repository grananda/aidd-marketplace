---
name: aiad-test
description: AIAD (AI-Augmented Development, ia-in-the-loop) skill. Fills the missing tests over code the human has already written, via the command `aiad test`. Two modes. In `unit` mode it detects the repo's test framework and writes clear unit tests (positive, negative, edge) for the target the human names — a class, method, function, file, or module — documenting the real behavior. In `e2e` mode it covers the target the human names — an endpoint/route (its contract: status, payloads, auth, validation, errors), a screen, a single user flow, or a whole user story — as end-to-end scenarios (happy path, errors, edge) with stable selectors and data. The scope can be as narrow as a single class or a single endpoint. The AI writes tests; it does NOT modify the code under test, and it does NOT change application code. For tests-first / red-first TDD before implementing, use aiad-tdd instead. Pull, not push. Complements AIDD/SDD without modifying them. Use when the user says "add unit tests", "cover this with tests", "I'm missing e2e tests", "test this flow end to end", "more coverage", or similar.
metadata:
  author: Julio Fernández
  version: "0.1.0"
---

# aiad-test (AIAD · ia-in-the-loop)

Use this skill when the human has working code and wants to close the testing gaps, or when they invoke:

- `aiad test` (infer the mode)
- `aiad test unit <target>` (missing unit tests) — target can be a **class, function, method, file, or module**
- `aiad test e2e <target>` (missing end-to-end tests) — target can be an **endpoint/route, a screen, a single user flow, or a whole user story**

The scope is yours to set, and you can be as narrow as you like: a single class or method for `unit`, a single endpoint or flow for `e2e`. If you give no target, it defaults to your recently written code (`unit`) or asks which flow/endpoint to cover (`e2e`). The narrower the target, the more focused the generated tests.

Also when they say "add unit tests", "cover this with tests", "I'm missing e2e tests", "test this flow end to end", "more coverage", or similar.

For **tests-first TDD** (write failing tests *before* implementing, so the human codes to green) use `aiad-tdd`, not this skill. `aiad-test` covers code that **already exists**.

Respond and document in the user's language when possible; keep command names, file names, paths, flags, and established technical terms as-is. This SKILL.md is written in English for universal use and uses ASCII only for cross-platform agent compatibility.

## What AIAD is and where this skill fits

AIAD (AI-Augmented Development) is the human-first set for the execution phase: **the human is the engine that writes the code and the AI augments on demand** (*ia-in-the-loop*). See `${CLAUDE_PLUGIN_ROOT}/methodology/native-ai-aiad.md` (read-only).

`aiad-test` is high-value toil the AI does well: writing the test harness over code you already wrote, so you keep building product instead of plumbing tests.

## Role and goal

> Act as a test/QA-automation engineer. Your goal is to **close the testing gaps** of code the human already wrote, with clear tests that document real behavior and catch regressions. You do not touch the code under test or the application code.

Exit criterion: tests exist for the relevant uncovered behaviors/flows, runnable with the project's runner, green against the current code.

## General rules

- **The AI writes tests, it does not touch the code under test or the app.** If, while writing tests, you find a bug, **do not fix it**: report it to the human (it is their code and their decision; they can continue with `aiad-review` or fix it themselves).
- **Green and honest:** since the code already exists, tests must pass reflecting the real behavior. No trivial assertions, no mocks that tautologize the result.
- **Detect the technology, do not impose it:** discover the repo's real test framework (config, existing tests, dependency manifest) before writing, and respect its naming and location conventions.
- **e2e stability above all:** robust selectors (roles/test-ids before volatile CSS classes), isolated test data, deterministic waits (no fragile sleeps). No flaky tests.
- **Cover what matters:** positive, negative/error, and edges (empty, null, numeric bounds, conditional branches). Prioritize business logic over trivial getters.
- **Pull, not push.**

## Flow of `aiad test`

### 1. Scope and pick the mode

- `unit` for a class/method/function/file/module; `e2e` for an endpoint/route/screen/flow. If not given, infer from the request or ask once.
- For `unit`: take the target the human names (e.g. a specific class or method) and scope the tests to exactly that unit and its collaborators; do not widen to the whole module unless asked. If no target is given, default to recently written code.
- For `e2e`: take the target the human names — a specific **endpoint/route** (test its contract: status codes, payloads, auth, validation, error responses) or a specific **screen/flow** (drive it through the UI). If no target is given, locate the US and its user flows + acceptance criteria in `docs/detalle-historias-usuario.md`, or ask which endpoint/flow to cover.

### 2. Detect (or, for e2e, propose) the testing technology

- Read the dependency manifest and test config, and look at existing tests (location, convention, fixtures/utilities).
- Respect the "selected technology" if it is in `docs/arquitectura-base.md`. If you cannot determine the framework with confidence, ask once (with options) before writing.
- For `e2e` with no e2e setup in the repo: propose a framework suited to the stack and **confirm** before installing/configuring anything; find out how the app is launched for tests (base URL, environment, data seed).

### 3. Find the gaps / design the scenarios

- `unit`: analyze public functions/methods, branches, error handling, edges; detect what current tests do not cover.
- `e2e`: per flow, design happy path, errors/validations (invalid input, permissions, disallowed states), and relevant edges (empty, extreme data, back navigation, reload).

### 4. Write the tests

- In the project's location and convention, naming each test as an assertion of behavior.
- Use only test dependencies already present (or the ones confirmed in step 2); if one is missing, say so and propose how to add it — do not install by surprise.
- Do not modify the code under test or the application. If `e2e` needs testability hooks (e.g. `data-testid`), list them as suggestions for the human; do not add them to production code without permission.

### 5. Run and confirm

- Run the project's runner and confirm the new tests pass stably (no flakiness) against the real code.
- If a test cannot pass because of a likely bug or missing testability, **do not fix the code**: mark/skip it with a documented note, or report it clearly, and leave the decision to the human.

### 6. Close

- Summarize what behaviors/flows are now covered and what remains.
- Report any bug or testability suggestion for the human to decide (they can use `aiad-review`).
- Optional journal: append a line to `docs/aiad-journal.md` (`authored:ai-tests`).

## Final check

Report:

- Mode, target/US, and the framework detected or proposed.
- Test files created and case count (positive/negative/edge, or happy/errors/edge for e2e).
- Confirmation of green/stable runs and any bugs or testability gaps reported to the human.
