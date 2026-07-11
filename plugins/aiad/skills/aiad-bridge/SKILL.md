---
name: aiad-bridge
description: AIAD (AI-Augmented Development, ia-in-the-loop) bridge skill. Lets the human switch between AIAD (human-engine) and SDD (AI-engine) by treating an OpenSpec change as equivalent to a user story, via the command `aiad bridge`. In `to-sdd` it wraps a US as an OpenSpec change to delegate execution to SDD (aisdd-specs); in `to-aiad` it reclaims control, returning a change to human treatment as a US. The stable unit is always the US; the change is its temporary SDD form. The engine switch can happen mid-US. It does NOT decide which engine to use for you: it performs the switch you ask for. If OpenSpec/aisdd-specs is unavailable, it says so and work continues standalone on the US. Use when the user says "let the AI take over this US", "move this to SDD", "I'm taking back this change", "back to AIAD", "wrap this US as a change", or similar.
metadata:
  author: Julio Fernández
  version: "0.1.0"
---

# aiad-bridge (AIAD · ia-in-the-loop)

Use this skill when the human wants to change the **engine** of a user story (US) between AIAD (they write) and SDD (the AI executes), or when they invoke:

- `aiad bridge`
- `aiad bridge to-sdd <us-id-or-description>` (wrap the US as a change and move to SDD)
- `aiad bridge to-aiad <change-slug>` (reclaim control, treat as a US again)

Also when they say "let the AI take over this US", "move this to SDD", "I'm taking back this change", "back to AIAD", "wrap this US as a change", or similar.

Respond and document in the user's language when possible; keep command names, file names, paths, flags, and established technical terms as-is. This SKILL.md is written in English for universal use and uses ASCII only for cross-platform agent compatibility.

## What AIAD is and where this skill fits

AIAD (AI-Augmented Development) is the human-first set for the execution phase: **the human is the engine that writes the code and the AI augments on demand** (*ia-in-the-loop*). See `${CLAUDE_PLUGIN_ROOT}/methodology/native-ai-aiad.md` (read-only).

`aiad-bridge` materializes the methodology's key idea: **an OpenSpec change is equivalent to a human user story.** That equivalence becomes a bidirectional engine switch, letting the human choose who drives, per US and even mid-way.

## Role and goal

> Act as the switch between two ways of working. Your goal is for the human to be able to **delegate a US to SDD** when they want leverage, or **take back control** when they want to create again, without losing coherence or traceability. You do not opine on which engine is better: you perform the requested switch and leave everything consistent.

Exit criterion: after the switch the US is correctly represented in the target engine (change opened in SDD, or US reclaimed for human work), with state and context synchronized, and the human knows how to continue.

## General rules

- **The US is the stable unit.** The change is only its temporary SDD form. Never duplicate the source of truth: the US detail keeps living in `docs/detalle-historias-usuario.md`.
- **Do not decide the engine for the human.** If they hesitate, briefly state the trade-off (SDD = AI-engine, fast, less authorship; AIAD = human-engine, authorship and learning) and let them choose.
- **Do not reimplement OpenSpec mechanics:** delegate to the `aisdd-specs` skill to open/implement/close changes. This bridge orchestrates the switch and the sync; it does not rewrite SDD.
- **Clean degradation:** if OpenSpec or `aisdd-specs` is unavailable, say so clearly; work continues standalone on the US (no change). Do not block the human.
- **Mid-US switching allowed:** if the human already has work in progress, make sure the target engine starts from that real state (branches, files, existing tests), not from scratch.

## Flow of `aiad bridge`

### A. AIAD to SDD — `to-sdd` (delegate to the AI)

1. **Identify the US** (id or description) in `docs/detalle-historias-usuario.md` and gather its context: acceptance criteria, relevant architecture, and the real work state if the human already started (branch, files, tests).
2. **Check the tooling:** verify OpenSpec and `aisdd-specs` are available. If not, warn and offer to continue standalone.
3. **Wrap the US as a change:** delegate to `aisdd open change <us-slug>` (through `aisdd-specs`), using a slug derived from the US. Pass the acceptance criteria and the in-progress state as context so the change does not ignore what is already done.
4. **Record the US -> change link** in `docs/aiad-journal.md` (and, if the project uses SDD's Jira map, let `aisdd-specs` do its sync; this bridge does not duplicate it).
5. **Hand off to SDD:** tell the human that from here they follow the SDD cycle (open/implement/close change) and that they can reclaim control with `to-aiad` whenever they want.

### B. SDD to AIAD — `to-aiad` (reclaim control)

1. **Identify the change** (slug) and locate the equivalent US.
2. **Sync the state:** make sure the code and tests SDD produced so far are on the US branch and are the starting point for the human's work.
3. **Reclaim the US:** mark the change as paused/inactive in the SDD flow (without archiving it if the work is not complete) and return control to the human over the US. Do not delete the change artifacts: they remain as reference.
4. **Record the switch** in `docs/aiad-journal.md` (US, change, reason for the engine change).
5. **Reorient the human:** suggest where to continue (e.g. `aiad-design plan` to resume the approach, `aiad-review` to understand what the AI left done before continuing).

### Close

- Confirm the final coherent state in the target engine.
- Remind them the switch is reversible at any time.

## Final check

Report:

- Switch direction (to-sdd / to-aiad), US and change involved.
- Synced state (branch, files, tests) and the link recorded in the journal.
- Tooling availability (if it fell back to standalone for lack of OpenSpec, say so).
- The human's next step in the target engine.
