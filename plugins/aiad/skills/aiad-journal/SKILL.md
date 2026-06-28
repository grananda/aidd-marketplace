---
name: aiad-journal
description: AIAD (AI-Augmented Development, ia-in-the-loop) authorship-journal skill. Records and reports what the human authored versus what they delegated to the AI, via the command `aiad journal`. In `log` mode it appends a structured line to docs/aiad-journal.md (user story, skill, mode, who authored, one-line note). In `report` mode it summarizes the authorship ratio (% you wrote vs % delegated) per US, per period, or overall. It is the human-first inverse of the SDD audit: it records and celebrates your authorship, it never gates or restricts delegation (drift is the human's free choice). Use when the user says "log this", "record what I built", "my authorship report", "craft ratio", "how much did I write vs delegate", "AIAD journal", or similar.
metadata:
  author: Julio Fernández
  version: "0.1.0"
---

# aiad-journal (AIAD · ia-in-the-loop)

Use this skill to record or report human authorship across AIAD work, or when the human invokes:

- `aiad journal` (infer the mode)
- `aiad journal log <details>` (append an authorship entry)
- `aiad journal report [us-id | period]` (summarize the authorship ratio)

Also when they say "log this", "record what I built", "my authorship report", "craft ratio", "how much did I write vs delegate", "AIAD journal", or similar.

Respond and document in the user's language when possible; keep command names, file names, paths, flags, and established technical terms as-is. This SKILL.md is written in English for universal use and uses ASCII only for cross-platform agent compatibility.

## What AIAD is and where this skill fits

AIAD (AI-Augmented Development) is the human-first set for the execution phase: **the human is the engine that writes the code and the AI augments on demand** (*ia-in-the-loop*). See `${CLAUDE_PLUGIN_ROOT}/methodology/native-ai-aiad.md` (read-only).

`aiad-journal` is the **authorship record** — the human-first inverse of the SDD audit. The SDD audit traces AI provenance (who/what/which model), a surveillance-of-AI artifact. The journal instead records and celebrates **what the human authored**, and lets them see their own craft trend over time.

## Role and goal

> Act as the keeper of the human's authorship log. Your goal is to keep a light, honest record of what the human built versus what they delegated, and to report it as a **signal, never a gate**. You celebrate authorship; you never police delegation. Delegating a lot is a legitimate, free choice — your job is only to make it visible if the human wants it.

Exit criterion: an entry is appended (`log`) or a clear authorship summary is produced (`report`), without ever blocking or judging the human's choices.

## General rules

- **Signal, not a gate.** Never block, warn, or moralize about how much the human delegates. Drift is acceptable; it is the human's free will. Just record and, on request, report.
- **Append-only:** `log` adds lines; it never rewrites or deletes history. If `docs/aiad-journal.md` does not exist, create it with a short header.
- **Low ceremony:** one line per entry. Do not interrogate the human; infer fields from context and ask at most one thing if essential.
- **Honest classification:** record who actually authored each piece using the `authored` taxonomy below. Do not inflate the human's share.
- **Privacy:** record only what the line format needs (US, skill, mode, authorship, short note). No code content, no secrets.

## The journal file

`docs/aiad-journal.md` is an append-only Markdown list. Line format:

```
- <date> | US:<us-id> | skill:<aiad-skill> | mode:<mode> | authored:<human|ai-tests|ai-fragment|advice-only|ai-edit> | note:<one line>
```

`authored` taxonomy:
- `human` — the human wrote the production code themselves.
- `ai-tests` — the AI wrote tests (`aiad-tdd`/`aiad-test`); production code is the human's.
- `ai-fragment` — the AI generated a bounded code fragment on explicit request.
- `advice-only` — the AI only advised/explained/reviewed; no code from the AI.
- `ai-edit` — **factual, hook-captured**: the journal hook recorded that the AI edited a file via its tools (skill `aiad-hook`). These are not self-reported; they are the ground-truth signal of AI-touched files.

> Other `aiad-*` skills append their own line directly when they help (it is part of their shared DNA). `aiad-journal log` is for manual or explicit entries; `aiad-journal report` reads all lines.

### Factual capture via the journal hook (optional, recommended)

The plugin ships a `PostToolUse` hook (`hooks/aiad-journal-hook.sh`) that, **only if `docs/aiad-journal.md` already exists**, appends an `ai-edit` line every time the AI edits a file via `Write`/`Edit`/`MultiEdit`. It is passive (records, never blocks), opt-in per project (no journal file -> no logging), and never fails the session.

This makes the authorship ratio **factual rather than self-reported**: files the AI touches go through its tools and get logged as `ai-edit`; what the human types by hand in their editor is never seen by the hook and is theirs by definition. To enable it in a project, just create the journal (run `aiad journal log ...` once, or `touch docs/aiad-journal.md`). When reporting, treat `ai-edit` as the ground-truth AI share and the other classes as the semantic detail.

## Flow of `aiad journal`

### log mode

1. Determine the fields from context (current US, the skill that just helped, the mode, the authorship class) and the human's note.
2. If `docs/aiad-journal.md` is missing, create it with a one-line header explaining what it is.
3. Append the formatted line. Confirm briefly.

### report mode

1. Read `docs/aiad-journal.md`. If absent, say there is nothing logged yet and how logging works.
2. Filter by the requested scope (a US id, a period, or everything).
3. Summarize:
   - **Authorship ratio:** share of entries by `authored` class (e.g. human X% / ai-tests Y% / ai-fragment Z% / advice-only W%).
   - **By US or period** if requested.
   - **Trend:** is the human's `human`-authored share rising or falling over time.
4. Present it as a neutral signal. Optionally note what it can be used for (personal craft trend, retrospectives, the upskilling/retention argument for working human-first). Never recommend "delegate less" as a judgment.

## Final check

Report:

- Mode used (`log`/`report`).
- For `log`: the line appended.
- For `report`: the authorship ratio and scope, framed as a signal, not a verdict.
