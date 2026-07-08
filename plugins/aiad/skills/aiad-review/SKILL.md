---
name: aiad-review
description: AIAD (AI-Augmented Development, ia-in-the-loop) skill. Didactic review of the code the human wrote, via the command `aiad review`. Three focuses. `correctness` checks behavior, edge cases, errors, and coverage of the user story's acceptance criteria. `quality` checks readability, naming, duplication, fit with the architecture and style guide. `perf` proposes performance/refactor improvements demanding measurement first and a test safety net, distinguishing performance from readability and rejecting premature micro-optimizations. It applies a comprehensive review checklist (DRY/KISS, cohesion/coupling, security, cyclomatic complexity, regressions, contract/compat breakage, observability, resource leaks, race conditions, dead code, out-of-scope changes) with per-layer checklists for backend, API and frontend, and can run in merge-readiness mode against a base branch (`aiad review develop`). Every finding is evidence-backed, ordered by criticality, notes whether a new/modified test is needed, and may include a concrete current-code -> suggested-code change. It explains the WHY so the human learns and decides, and by default does NOT apply fixes. As a deliverable it generates a standalone HTML report with the referenced code lines (line-numbered, highlighted) and the recommended before/after changes. Pull, not push. Complements AIDD/SDD without modifying them. Use when the user says "review my code", "take a look at this", "code review of my changes", "revisar cambios contra develop", "merge readiness", "this can be improved", "this is slow", "refactor this", "this smells", or similar.
metadata:
  author: Julio Fernández
  version: "0.3.0"
---

# aiad-review (AIAD · ia-in-the-loop)

Use this skill when the human has written code and wants feedback that helps them improve it and learn, or when they invoke:

- `aiad review` (infer the focus)
- `aiad review correctness <files-or-us>`
- `aiad review quality <files>`
- `aiad review perf <files-or-function>`
- `aiad review <base-branch>` (merge-readiness mode: diff the current branch against that base, e.g. `aiad review develop`, `aiad review release/x`)

Also when they say "review my code", "take a look at this", "code review of my changes", "revisar cambios contra develop", "review de la rama actual", "merge readiness", "this can be improved", "this is slow", "refactor this", "this smells", or similar.

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
- **Prioritize and order by criticality:** separate blocking (correctness, bug, unmet acceptance criterion, security, regression) from improvement (quality, readability, maintainability) from optional (taste). Put the most critical findings first. Do not drown the human in nits.
- **Evidence-backed, no generic comments:** every finding must be backed by the actual changed code (cite `file:line`). No generic advice without evidence in the code under review. Prioritize findings with real impact over minor stylistic preferences.
- **Merge-readiness mindset:** for each finding state clearly whether it **must block the merge/close** or is an optional improvement.
- **Test gap per finding:** for each relevant finding, state explicitly whether it needs a **new or modified test** and which one. In merge-readiness/diff mode, base this **only on the diff**: if the diff changes logic and does not include a covering test, say so ("the diff adds no test for X; add one"); if it does, judge whether it covers the change. Do not assume tests that exist outside the diff.
- **Recommended change (before/after) when it helps:** for a finding where a concrete change clarifies the fix, show a **current-code -> suggested-code** snippet (practical, at code level). It is a **proposal for the human to apply**, shown for learning — you still do NOT apply it. Prefer a focused snippet over a large rewrite.
- **Risks to validate:** if a risk cannot be confirmed from the code/diff alone (indirect regression, runtime-only behavior), mark it as a risk to validate and say what to check. Do not invent problems.
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

## Review dimensions (comprehensive checklist)

The focus sets the emphasis, but a thorough review scans these dimensions and reports only what the changed code actually evidences (don't pad with generic notes). Adapt to the language/stack.

**Core (always):** DRY; KISS; readability; naming; error handling; basic security; cyclomatic complexity; design critique; cohesion and coupling; logical/structural duplication; consistency with the project's style; correct use of abstractions; separation of responsibilities; testability and test coverage/need; backward compatibility; regression risk; input/output validation; handling of null/empty/unexpected states; observability (logs, traceability, diagnosable errors); medium/long-term maintainability; adequate dependency use; possible memory issues or resource leaks; possible race conditions; unnecessary computational cost; dead/redundant/unreachable code; changes outside the intended scope; risk of breaking existing contracts; impact on CI/CD, config, environments or deployment where applicable.

**Global-impact / regression analysis:** beyond the changed lines, consider whether the change can affect the wider codebase — indirect conflicts, overriding existing behaviors, compatibility breaks, impact on shared modules, changes to public contracts, side effects, cross-cutting dependencies, or altered existing flows.

**If backend (as far as the diff allows to infer):** database efficiency; N+1 queries; potentially needed indexes; correct transaction use; concurrency and locks; idempotency; scalability; correct timeout handling; efficient use of external resources; validation of DTOs/commands/queries/models; API contracts; endpoint versioning/compat; serialization/deserialization; authz and authn; accidental exposure of sensitive data; consistent HTTP responses; domain vs infrastructure error handling; retries, resilience and fault tolerance; separation of domain / application / infrastructure.

**If it exposes or changes APIs:** contract compliance; adequate HTTP codes; consistent response structure; input validation; clear and safe errors; compatibility with existing clients; breaking changes; pagination/filtering/sorting where applicable; security in params/routes/payloads; idempotency in sensitive operations; docs/contract updates where applicable.

**If frontend:** state management; render performance; separation of concerns; adequate componentization; unnecessary re-renders; unreleased subscriptions; correct async handling; correct form usage; UI and defensive validations; basic accessibility; i18n where applicable; visual consistency with the project; correct service usage; avoid excessive business logic in components; lazy loading / bundle impact where applicable; HTTP error handling; loading/empty/error states; basic security against XSS or sensitive-data exposure; clean separation of presentation / state / data access.

If there are no blocking problems, say so clearly.

## Running as a subagent (context isolation)

This skill ships a companion subagent, **`aiad-reviewer`**, for the heavy reading. Reviewing means reading the diff, the touched files, and the architecture/style docs — that can flood the human's working context while they are coding.

- **Prefer delegating the analysis to the `aiad-reviewer` subagent** when the `Agent`/`Task` tool is available: pass it the scope (files/US) and focus, let it do the reading in its isolated context, and relay its findings report to the human. The human's main context stays clean.
- The subagent has **read-only tools** (Read, Grep, Glob, Bash) and cannot apply fixes — which enforces the "propose, don't apply" rule structurally.
- The subagent reports each finding with its `file:line`. The **main skill** (this context) then assembles the JSON manifest from that report and generates the HTML report (step 4.5) — the subagent does not write files. Keeping the `file:line` precise is what lets the report embed the real code.
- If subagents are not available, run the flow below directly in the current context.

## Flow of `aiad review`

### 1. Scope and pick the focus

- If files/US/focus are given, use them. Otherwise review the working tree (`git status`, `git diff`, `git diff --staged`); if nothing changed, ask what to review. Infer the focus from the request (default `correctness`).
- **Merge-readiness mode (diff against a base branch):** if the human names a base branch (`aiad review develop`, `aiad review release/x`) or asks to review "against develop/main", review **only that diff**:

  ```bash
  git fetch origin <base>
  git --no-pager diff origin/<base>...HEAD
  ```

  Default base is `develop` if they say "merge readiness" without naming one; if that branch does not exist, tell them and fall back to `main`/`master` or the working tree. Analyze exclusively that diff, apply the comprehensive checklist and the global-impact/regression analysis, and frame findings as merge-readiness (what blocks the merge vs optional). Show the current branch name at the top of the report.

### 2. Gather the evaluation context

- The US and its acceptance criteria (if any), architecture patterns and repo conventions, style guide for UI.

### 3. Review by the chosen focus

Apply the focus above. For `perf`, run the safety-net and measurement checks before proposing anything.

### 4. Deliver the findings

Prioritized list (blocking / improvement / optional). Each finding: location (`file:line`), what happens, why it matters, suggested direction. Do not rewrite the code for the human. Present this list in chat as usual.

### 4.5 Generate the HTML report

Always produce a **standalone HTML report** of the review so the human can follow the recommendations with the code in front of them. Build a JSON manifest from the findings (whether produced inline or relayed from the `aiad-reviewer` subagent) and render it with the bundled script.

1. **Write the manifest** to a JSON file (e.g. `docs/aiad-reviews/aiad-review-<focus>-<date>.json`; if the repo has no `docs/`, use `.aiad-reviews/`). Schema:

   ```jsonc
   {
     "title": "Review — <scope>",
     "scope": "src/foo.ts, src/bar.ts (HU-07)",
     "focus": "correctness",              // correctness | quality | perf
     "date": "<YYYY-MM-DD>",              // today's date
     "verdict": "fixes-needed",           // ready | fixes-needed
     "verdict_note": "1 blocking to resolve before closing the US",
     "summary": "one short paragraph",
     "good": ["what is well solved", "..."],
     "labels": {                          // OPTIONAL — fill in the human's language
       "blocking": "Bloqueante", "improvement": "Mejora", "optional": "Opcional",
       "what": "Que pasa", "why": "Por que importa", "suggestion": "Sugerencia",
       "good": "Lo que esta bien resuelto", "location": "Ubicacion",
       "scope": "Alcance", "focus": "Foco"
     },
     "findings": [
       {
         "id": "F1",
         "priority": "blocking",          // blocking | improvement | optional (most critical first)
         "tag": "N+1",                    // free label (correctness/security/N+1/race/quality...)
         "title": "short finding title",
         "file": "src/foo.ts",            // referenced file (the script reads the real lines)
         "line": 42,                      // or "lines": [40, 46] for a range
         "highlight": [42],               // OPTIONAL explicit lines to highlight
         "context": 3,                    // OPTIONAL context window (default 3)
         "lang": "ts",                    // OPTIONAL language badge
         "what": "what happens",
         "impact": "concrete impact / risk (OPTIONAL but recommended for blocking)",
         "why": "why it matters (the principle/pattern behind it)",
         "suggestion": "suggested direction",
         "change": {                      // OPTIONAL current -> suggested code (a proposal, shown for learning)
           "before": "for (const o of orders) { o.client = await repo.find(o.clientId) }",
           "after": "const clients = await repo.findMany(ids); // map in memory",
           "lang": "ts"
         },
         "test_gap": "the diff adds no test for X; add one that verifies Y"  // OPTIONAL
       }
     ]
   }
   ```

   - Prefer `file` + `line`/`lines`: the script reads the **actual code from the repo** and shows it line-numbered with the referenced line(s) highlighted. Do **not** transcribe code by hand when the file exists.
   - Use `snippet` (a string) plus optional `snippet_start` (first line number) and `highlight` only when the code is not in a readable file (e.g. a proposed alternative, generated output, or the subagent could not access the file).
   - Use `change` (before/after) when a concrete fix helps the human — practical, at code level, focused; it is a **proposal to apply themselves**, not applied by the review. The HTML renders it as two labelled blocks (current code / suggested code).
   - Add `test_gap` whenever the change needs a new/modified test (in diff mode, judged only from the diff).
   - Order `findings` by criticality (blocking first). Fill `labels` in the human's language so the report reads natively; omit it for English.

2. **Render** the HTML with the bundled script (Python 3 standard library only, no dependencies):

   ```bash
   python "${CLAUDE_PLUGIN_ROOT}/skills/aiad-review/scripts/render_review_html.py" \
     --input docs/aiad-reviews/aiad-review-<focus>-<date>.json \
     --output docs/aiad-reviews/aiad-review-<focus>-<date>.html \
     --base-dir . \
     --open
   ```

   - `--base-dir` is the repo root used to resolve each finding's `file` (default: current directory).
   - `--open` opens the report in the browser (best-effort; no-op in headless). Omit it in non-interactive mode.
   - The report is self-contained (inline CSS, no external requests), theme-aware (light/dark) and print-friendly.

3. If Python is unavailable, do not block: deliver the findings in chat and note that the HTML report could not be generated.

### 5. Close

- Summary: how many blocking, and a verdict (ready to close the US / fixes needed). For `perf`, whether tests must be created first.
- Remind them the fixes are theirs (with tests green before and after for `perf`); offer to review again after fixing.
- Optional journal: append a line to `docs/aiad-journal.md` (`authored:advice-only`).

## Final check

Report:

- Scope reviewed (files/US) and focus used.
- Findings by priority, with blocking ones highlighted.
- Path of the generated HTML report (`docs/aiad-reviews/…html`), or a note if it could not be generated.
- Verdict and the human's next step (and, for `perf`, whether tests are required first).
