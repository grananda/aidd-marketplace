---
name: aiad-review
description: AIAD (AI-Augmented Development, ia-in-the-loop) skill. Didactic review of the code the human wrote, via the command `aiad review`. Three focuses. `correctness` checks behavior, edge cases, errors, and coverage of the user story's acceptance criteria. `quality` checks readability, naming, duplication, fit with the architecture and style guide. `perf` proposes performance/refactor improvements demanding measurement first and a test safety net, distinguishing performance from readability and rejecting premature micro-optimizations. It explains the WHY of every finding so the human learns and decides, and by default does NOT apply fixes and does NOT change behavior. As a deliverable it generates a standalone HTML report of the review that embeds the referenced code lines (line-numbered, with the relevant lines highlighted) so the human can follow each recommendation. Pull, not push. Complements AIDD/SDD without modifying them. Use when the user says "review my code", "take a look at this", "code review of my changes", "this can be improved", "this is slow", "refactor this", "this smells", or similar.
metadata:
  author: Julio Fernández
  version: "0.2.0"
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
- The subagent reports each finding with its `file:line`. The **main skill** (this context) then assembles the JSON manifest from that report and generates the HTML report (step 4.5) — the subagent does not write files. Keeping the `file:line` precise is what lets the report embed the real code.
- If subagents are not available, run the flow below directly in the current context.

## Flow of `aiad review`

### 1. Scope and pick the focus

- If files/US/focus are given, use them. Otherwise review the working tree (`git status`, `git diff`, `git diff --staged`); if nothing changed, ask what to review. Infer the focus from the request (default `correctness`).

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
         "priority": "blocking",          // blocking | improvement | optional
         "tag": "correctness",            // free label (correctness/security/quality/perf...)
         "title": "short finding title",
         "file": "src/foo.ts",            // referenced file (the script reads the real lines)
         "line": 42,                      // or "lines": [40, 46] for a range
         "highlight": [42],               // OPTIONAL explicit lines to highlight
         "context": 3,                    // OPTIONAL context window (default 3)
         "lang": "ts",                    // OPTIONAL language badge
         "what": "what happens",
         "why": "why it matters (the principle/pattern behind it)",
         "suggestion": "suggested direction (NOT a full rewrite)"
       }
     ]
   }
   ```

   - Prefer `file` + `line`/`lines`: the script reads the **actual code from the repo** and shows it line-numbered with the referenced line(s) highlighted. Do **not** transcribe code by hand when the file exists.
   - Use `snippet` (a string) plus optional `snippet_start` (first line number) and `highlight` only when the code is not in a readable file (e.g. a proposed alternative, generated output, or the subagent could not access the file).
   - Keep `suggestion` as a direction, never a full rewrite — this stays a didactic, propose-don't-apply review.
   - Fill `labels` in the human's language so the report reads natively; omit it for English.

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
