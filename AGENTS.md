# AGENTS
# STATE/ARCH/CONSTRAINTS sind authoritative

# Chat history ist nicht authoritative

# Bei Konflikt: Hard-State gewinnt
## Operating Rules
- Log every change in STATE.md (see Log) with date/time and a short summary.
- After each task, add a Log entry in STATE.md and update GEMINI.md.
- Keep README.md updated whenever behavior, usage, or workflow changes.
- When reporting changes, link relevant files by path instead of duplicating content.
- Reminder: Before finishing, log the change in STATE.md by appending a log entry, update ARCHITECTURE.md(if needed), and confirm CONSTRAINTS.md(if needed) and README.md(if needed) is current.

## Git Management
- Before edits: check `git status -sb` and confirm no unexpected changes.
- Avoid parallel edits to the same file; coordinate ownership per file.
- Stage in small batches (prefer `git add -p`) and review diffs.
- Keep generated assets and large files out of Git unless explicitly needed.
- Use `.gitignore` or Git LFS for large binaries and generated folders.
- After edits: re-check `git status -sb`, update logs, and note any risks.
- Assume another agent is actively working unless the user says otherwise.
## Router Index
- `STATE.md` (hard state, append-only).
- `STATE_LEGACY.md` (archived state history).
- `ARCHITECTURE.md` (system design notes, append-only).
- `CONSTRAINTS.md` (non-negotiables, append-only).
- `REFERENCES.md` (docs/config index).
- `docs/_index.md` (doc lookup shortcuts).
- `GEMINI.md` (change log mirror).
- `COPILOT.md` (Copilot hints).

Docs under `docs/` are lookup material; prefer `docs/_index.md` and `REFERENCES.md` for navigation.

# Edit Permissions

Safe to edit without asking: docs/* (ausser Hard-state), tests, new files

Ask before editing: Hard-state markdowns + core configs

# Parallel Sessions Policy

- Multiple Codex sessions may work concurrently; dirty changes are not automatically an error.
- If git status is dirty: run `git status -sb` and check whether changes are plausible (files/paths for the task).
- If changes are from another worker or plausible: proceed, but avoid broad formatting/rewrites.
- If changes are not plausible: stop and escalate to the user (or start a new session/branch).
- Never "fix" or "clean up" other changes unless explicitly requested.
- Before commit/stage: always run `git diff` and optionally `git diff --name-only`.
- When running parallel sessions: branch recommended.

