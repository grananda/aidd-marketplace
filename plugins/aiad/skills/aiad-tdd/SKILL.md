---
name: aiad-tdd
description: AIAD (AI-Augmented Development, ia-in-the-loop) skill. Human-first TDD support, via the command `aiad tdd`. The AI writes the failing tests for the target the human is about to build, and the human implements the production code until they go green. The target scope is the human's to set and can be narrow: a whole user story, or a single class, method, function, or endpoint/route. It detects the repo's test framework, turns the target's expected behavior (acceptance criteria or contract) into test cases (positive, negative, edge), generates red, runnable tests, and leaves the implementation to the human. The AI does NOT write the production code. Pull, not push. Complements AIDD/SDD without modifying them. For filling tests over code that already exists, use aiad-test instead. Use when the user says "write the red tests for this US/class/method/endpoint I'm about to build", "let's do TDD", "tests first", "give me the red tests so I can implement", or similar.
metadata:
  author: Julio Fernández
  version: "0.1.0"
---

# aiad-tdd (AIAD · ia-in-the-loop)

Use this skill when the human is about to build a user story (US) following TDD and wants **the AI to write the tests and the human the code**, or when they invoke:

- `aiad tdd`
- `aiad tdd <target>` — target can be a whole **user story**, or a narrower thing you are about to build: a **class, method, function, or endpoint/route**

Also when they say "write the tests for this US", "write the red tests for this class/method/endpoint I'm about to build", "let's do TDD", "tests first", "give me the red tests so I can implement", or similar.

The scope is yours to set, and you can be as narrow as you like. `aiad tdd OrderValidator` scaffolds the red tests for that class before it exists; `aiad tdd POST /api/orders` writes the failing contract tests for an endpoint you are about to implement; `aiad tdd <US>` covers the whole story's acceptance criteria. The narrower the target, the tighter the red battery you implement against.

For tests over code that **already exists** (coverage/e2e gaps), use `aiad-test`. `aiad-tdd` is tests-**first**: red before the code exists.

Respond and document in the user's language when possible; keep command names, file names, paths, flags, and established technical terms as-is. This SKILL.md is written in English for universal use and uses ASCII only for cross-platform agent compatibility.

## What AIAD is and where this skill fits

AIAD (AI-Augmented Development) is the human-first set for the execution phase: **the human is the engine that writes the code and the AI augments on demand** (*ia-in-the-loop*). See `${CLAUDE_PLUGIN_ROOT}/methodology/native-ai-aiad.md` (read-only).

`aiad-tdd` is the **human-first jewel**: the perfect division of labor. The AI does the toil (building the test harness from the acceptance criteria); the human keeps the pure dopamine (writing the code that turns the bar green). It is ia-in-the-loop in its purest form.

## Role and goal

> Act as a test engineer. Your job is to turn the user story's acceptance criteria into **runnable tests that fail** (red), clear and well named, so the human implements against them. **You do not write the production code**: that is the human's work and pleasure.

Exit criterion: a battery of red tests covering the US acceptance criteria exists, runnable with the project's runner, and the human knows exactly what to make pass.

## General rules

- **The AI writes tests, the human writes the code.** This is the central, non-negotiable rule of this skill. Do not implement the production code, not even "to make the tests pass". If the human explicitly asks you to implement a part, that is a different thing (a fragment request) — flag it.
- **Red tests, not green:** the tests must fail at first because the code does not exist yet or does not comply. No cheating (no `assert true`, no empty tests, no mocks that tautologize the result).
- **Detect the technology, do not impose it:** discover the repo's real test framework before writing anything (see flow). Respect the project's naming and test-location conventions.
- **Coverage per criterion:** each Given/When/Then acceptance criterion of the US becomes at least one test for the positive case and, where applicable, the negative and the edges.
- **Pull, not push.**
- **Teach the why:** briefly explain what each block of tests covers and what is left to implement, so the human has the map.

## Flow of `aiad tdd`

### 1. Identify the target and its expected behavior

- **Set the scope from what the human named.** It can be a whole user story, or something narrower they are about to build:
  - **US** — locate it (by id or description) in `docs/detalle-historias-usuario.md` and extract its acceptance criteria (Given/When/Then) and the ones marked blocking.
  - **Class / method / function** — derive the expected behavior from its intended contract: the cases it must handle, inputs/outputs, and error conditions. Scope the red battery to exactly that unit; do not widen unless asked.
  - **Endpoint / route** — write the failing **contract** tests: status codes, request/response payloads, auth, validation, and error responses for that endpoint.
- If there is no formal US and no clear contract, ask the human for the expected behaviors (briefly) and work from those.
- Either way, the tests express the spec of the target **before** the code exists, so they must be red for the right reason (see step 5).

### 2. Detect the testing technology

- Discover the real stack and test framework before generating anything: read the dependency manifest and test config files, and observe existing tests (location, naming, assertion style, fixtures/utilities).
- Respect `docs/arquitectura-base.md` and the "selected technology" if recorded. If you cannot determine the framework with confidence, **ask** (a single question with options) before writing.

### 3. Map the target's behavior to tests

For each behavior of the target (an acceptance criterion of the US, or a case of the class/method/endpoint contract):
1. Positive case (the expected behavior).
2. Negative/error case(s) where it implies them (for an endpoint: invalid payloads, auth failures, validation errors and their status codes).
3. Relevant edges (empty, null, numeric bounds, concurrency if applicable).

Name each test so it reads as the specification of the behavior.

### 4. Generate the red tests

- Write the tests in the project's location and convention.
- Use only test dependencies already present; if one is missing, say so and propose how to add it — do not install by surprise.
- For what the human has not implemented yet, reference the expected signatures/contracts (import the target module even if it does not exist yet: that is the point of the red).
- **Do not** write the production code that makes them pass.

### 5. Run and confirm the red

- Run the project's runner and confirm the tests fail for the right reason (absent/incomplete code), not due to config or test errors.
- If they fail because of a problem in the test itself (bad import, syntax), fix it: the red must be legitimate.

### 6. Hand off to the human

- Summarize which behaviors the battery covers and, in suggested order, what the human should implement to turn tests green.
- Remind them: from here, **the human writes**. Offer `aiad-review` for when they finish and `aiad-rubber-duck` if they get stuck implementing.
- Optional journal: append a line to `docs/aiad-journal.md` (`authored:ai-tests`).

## Final check

Report:

- US covered and test framework detected.
- Test files created and case count (positive/negative/edge).
- Confirmation that the tests are **red** for the right reason.
- Suggested implementation order for the human.
- Explicit reminder: the production code is written by the human.
