---
name: aiad-save
description: AIAD (AI-Augmented Development, ia-in-the-loop) utility skill. Commits all pending changes and pushes the current branch WITHOUT asking any questions, via the command `aiad save`. A fast "save everything" for when you are in a hurry and just want your work uploaded. It stages everything (respecting .gitignore), writes a sensible commit message itself, commits, and pushes (setting upstream if needed). It never asks, never force-pushes, never touches other branches; it stops and reports only when it genuinely cannot proceed (no repo, no remote, or a rebase conflict it must not resolve silently). Unlike the advisory aiad-* skills, this one performs an autonomous git action; invoking it is your authorization. Use when the user says "save", "save my work", "commit and push everything", "push it all, I'm in a hurry", "aiad save", or similar.
metadata:
  author: Julio Fernández
  version: "0.1.0"
---

# aiad-save (AIAD · ia-in-the-loop)

Use this skill when the human wants to commit and push everything pending with zero friction, or when they invoke:

- `aiad save`
- `aiad save <optional short message>`

Also when they say "save", "save my work", "commit and push everything", "push it all, I'm in a hurry", or similar.

Respond and document in the user's language when possible; keep command names, file names, paths, flags, and established technical terms as-is. This SKILL.md is written in English for universal use and uses ASCII only for cross-platform agent compatibility.

## What AIAD is and where this skill fits

AIAD (AI-Augmented Development) is the human-first set for the execution phase: **the human is the engine that writes the code and the AI augments on demand** (*ia-in-the-loop*). See `${CLAUDE_PLUGIN_ROOT}/methodology/native-ai-aiad.md` (read-only).

`aiad-save` is the one **action/utility** skill in AIAD: it does not advise, it acts. It is still pull, not push — you invoke it, and that invocation is your explicit authorization to commit and push. It exists for the moment you are out of time and just need everything uploaded.

## Role and goal

> Act as a fast, reliable "save everything" button. Your goal is to get all pending work committed and pushed on the current branch with **no questions**, while never doing anything destructive. Speed first, but never force, never lose work, never surprise.

Exit criterion: the working tree is committed and the current branch is pushed to its remote (or you have stopped and clearly reported the one reason you could not, with no changes lost).

## General rules

- **No questions.** Do not ask for confirmation, a message, or a branch. If the human gave a short message, use it; otherwise generate one.
- **Never destructive.** Never `git push --force` / `--force-with-lease`, never `reset --hard`, never `rebase` onto something that drops commits, never delete or switch branches. Work only on the current branch.
- **Respect .gitignore.** Staging is `git add -A`; .gitignore is the guard against committing junk/secrets. Do not add ignored files.
- **Stop-and-report is not asking.** When you genuinely cannot proceed (no repo, no remote, rebase conflict), stop and report clearly — do not ask the human to decide mid-run. Leave the work safely committed locally whenever possible.
- **Idempotent-ish.** Running it with nothing pending should be a no-op that still pushes any unpushed local commits, and otherwise reports "already up to date".

## Flow of `aiad save`

### 1. Pre-checks

- Confirm you are in a git repository (`git rev-parse --is-inside-work-tree`). If not, stop and report: not a git repo, nothing to save.
- Get the current branch (`git rev-parse --abbrev-ref HEAD`). If `HEAD` is detached, stop and report (committing on a detached HEAD would be easy to lose); do not guess a branch.

### 2. Stage and commit

- Stage everything: `git add -A`.
- Check status (`git status --porcelain`):
  - If there is something staged, write the commit message and commit (see step 3).
  - If there is nothing to commit, skip the commit and go to push (there may be unpushed local commits).

### 3. Commit message (generated, no questions)

- If the human passed a short message, use it verbatim.
- Otherwise generate a concise, honest message from the staged diff (`git diff --staged --stat` and a quick look at the changes):
  - Prefer a conventional prefix when obvious (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`).
  - Summarize the main change in the subject; if the change set is broad or unclear, fall back to `chore: save work in progress`.
  - Keep it one line; add a short body only if it genuinely helps.
- Commit: `git commit -m "<message>"`.

### 4. Push

- If the branch has an upstream, `git push`.
- If it has no upstream, `git push -u origin <current-branch>`.
- If there is no remote configured at all, stop and report: committed locally, but no remote to push to.
- If the push is rejected as non-fast-forward (remote moved ahead):
  - Try a safe sync once: `git pull --rebase --autostash`, then push again.
  - If the rebase hits conflicts, **abort it** (`git rebase --abort`) to leave the tree clean with your commit intact, then stop and report: pushed nothing, your work is committed locally, manual merge needed.
  - If the push is rejected for another reason (e.g. protected branch), stop and report it; the commit stays local.

### 5. Report

- Always end with a short report: branch, whether a commit was made (and its short hash + message), and the push result (pushed / already up to date / committed locally only + reason).
- Optional journal: if the project uses `docs/aiad-journal.md`, you may append a one-line `aiad-save` entry; skip it if it would slow the save down.

## Final check

Report concisely:

- Branch and commit (short hash + message) or "nothing to commit".
- Push result: pushed to `<remote>/<branch>`, already up to date, or committed locally only with the exact reason.
- Confirmation that nothing was force-pushed or lost.
