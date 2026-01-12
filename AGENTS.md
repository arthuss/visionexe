# AGENTS

## Operating Rules
- Log every change in STATE.md (see Log) with date/time and a short summary.
- After each task, add a Log entry in STATE.md and update GEMINI.md.
- Keep README.md updated whenever behavior, usage, or workflow changes.
- When reporting changes, link relevant files by path instead of duplicating content.
- Reminder: Before finishing, log the change STATE.md, update ARCHITECTURE.md, and confirm CONSTRAINTS.md and README.md is current.
- Use `building_scenes_and_chapters.md` as the checklist reference for chapter/scene completeness.

## Git Management
- Before edits: check `git status -sb` and confirm no unexpected changes.
- Avoid parallel edits to the same file; coordinate ownership per file.
- Stage in small batches (prefer `git add -p`) and review diffs.
- Keep generated assets and large files out of Git unless explicitly needed.
- Use `.gitignore` or Git LFS for large binaries and generated folders.
- After edits: re-check `git status -sb`, update logs, and note any risks.

## Router Index
- `STATE.md` (hard state, append-only).
- `ARCHITECTURE.md` (system design notes, append-only).
- `CONSTRAINTS.md` (non-negotiables, append-only).
- `GEMINI.md` (change log mirror).
- Copilot hints (path TBD).


