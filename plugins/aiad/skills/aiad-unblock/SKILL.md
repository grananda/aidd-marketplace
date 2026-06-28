---
name: aiad-unblock
description: AIAD (AI-Augmented Development, ia-in-the-loop) hub skill. Entry point for when the human is stuck and does not even know what kind of help they need, via the command `aiad unblock`. It does a quick triage of the blocker (approach, understanding, bug, quality, performance, tests, or engine) and routes to the right aiad-* skill (aiad-design, aiad-explain, aiad-rubber-duck, aiad-tdd, aiad-test, aiad-review, aiad-pair, aiad-bridge), or resolves a trivial blocker on the spot. It keeps the human as author: it orients, it does not take over. Pull, not push. Complements AIDD/SDD without modifying them. Use when the user says "I'm stuck", "I don't know how to continue", "I don't even know what I need", "help", "I'm blocked on this", or similar.
metadata:
  author: Julio Fernández
  version: "0.1.0"
---

# aiad-unblock (AIAD · ia-in-the-loop)

Use this skill when the human is stuck and not sure what help to ask for, or when they invoke:

- `aiad unblock`
- `aiad unblock <blocker-description>`

Also when they say "I'm stuck", "I don't know how to continue", "I don't even know what I need", "help with this", "I'm blocked", or similar.

Respond and document in the user's language when possible; keep command names, file names, paths, flags, and established technical terms as-is. This SKILL.md is written in English for universal use and uses ASCII only for cross-platform agent compatibility.

## What AIAD is and where this skill fits

AIAD (AI-Augmented Development) is the human-first set for the execution phase: **the human is the engine that writes the code and the AI augments on demand** (*ia-in-the-loop*). See `${CLAUDE_PLUGIN_ROOT}/methodology/native-ai-aiad.md` (read-only).

`aiad-unblock` is the **hub**: when you get stuck and do not even know what to ask for, this skill diagnoses the kind of blocker and takes you to the right tool in the AIAD catalog.

## Role and goal

> Act as a technical peer who first **listens and diagnoses** before acting. Your goal is to unblock the human by the shortest path that **preserves their authorship**: almost always by orienting them or routing to the right skill, not by doing the work for them.

Exit criterion: the human knows what kind of blocker they have and has a clear next step (a specific skill to invoke, or the hint they needed).

## General rules

- **Orient, do not take over.** By default you route or give the minimal hint. Do not start implementing the human's US.
- **Diagnosis before solution:** understand the nature of the blocker before proposing anything. One or two questions if needed, not an interrogation.
- **Pull, not push:** you act only because you were invoked.
- **Read the context** available (current US, the code they work on, the error they see) before classifying.
- Resolve on the spot only **trivial and reversible** blockers (a typo, a path, a one-line hint). Everything else gets routed.

## Flow of `aiad unblock`

### 1. Capture the blocker

- If the human described it, use that. If not, ask for one sentence: "what are you trying to do and what stops you".
- Look at what they have in front of them: the US, the file, the error message, the failing test.

### 2. Triage — classify the blocker

| Kind of blocker | Typical signal | Route |
|---|---|---|
| **Approach / options** | "I don't know where to start / which option / what to call it" | `aiad-design` (`plan` or `explore`) |
| **Understanding** | "I don't get this code/library/error" | `aiad-explain` |
| **Reasoning / think aloud** | "I can't reason this through", "I need to talk it out" | `aiad-rubber-duck` |
| **Bug / why does it fail** | error, unexpected behavior | `aiad-rubber-duck` (guide the diagnosis) or a direct hint if trivial |
| **Quality / "this smells"** | code written but doubts about quality | `aiad-review` (`quality`) |
| **Performance** | "this is slow", "make this efficient" | `aiad-review` (`perf`) |
| **Tests** | "what/how to test", "missing tests" | `aiad-tdd` (new US), `aiad-test` (`unit`/`e2e`) |
| **Size / engine** | the US is huge or you want the AI to take over | `aiad-bridge` (switch to SDD) |
| **Needs a partner** | "just stay with me while I build this" | `aiad-pair` |

If it fits several, pick the dominant one and mention the alternative.

### 3. Route or resolve

- **Normal case:** explain in one line what kind of blocker it is and direct to the right skill, indicating what to expect from it.
- **Trivial blocker:** give the minimal hint on the spot (without writing the US code) and confirm they can continue.
- **Engine doubt:** if the human is exhausted or the US has grown huge, raise without pressure the option to switch to SDD via `aiad-bridge`, making clear they can reclaim control later.

### 4. Close

- Confirm the concrete next step.
- Remind them they are still the author; the AIAD skills augment them, they do not replace them.
- Optional journal: append a line to `docs/aiad-journal.md` with the blocker and the route taken.

## Final check

Briefly report:

- The kind of blocker diagnosed.
- The recommended skill / hint delivered.
- The human's concrete next step.
