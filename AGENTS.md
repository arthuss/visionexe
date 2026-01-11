# AGENTS

## Operating Rules
- Log every change in this file (see Log) with date/time and a short summary.
- After each task, add a Log entry here and update GEMINI.md.
- Keep README.md updated whenever behavior, usage, or workflow changes.
- When reporting changes, link relevant files by path instead of duplicating content.
- Reminder: Before finishing, log the change here, update GEMINI.md, and confirm README.md is current.
- Use building_scenes_and_chapters.md as the checklist reference for chapter/scene completeness.

## Git Management
- Before edits: check `git status -sb` and confirm no unexpected changes.
- Avoid parallel edits to the same file; coordinate ownership per file.
- Stage in small batches (prefer `git add -p`) and review diffs.
- Keep generated assets and large files out of Git unless explicitly needed.
- Use `.gitignore` or Git LFS for large binaries and generated folders.
- After edits: re-check `git status -sb`, update logs, and note any risks.

## Log
- 2026-01-10 03:51 - Asset Bible subject queue now emits per-phase prompts by filtering the Evolution section and suffixing output basenames; docs updated (engine/workers/asset_bible_queue_builder.py, README.md, docs/queues.md, docs/workers.md).
- 2026-01-10 05:22 - Subjects viewer now links and previews asset_bible images per subject; README updated (stories/template/subjects/index.html, README.md).
- 2026-01-10 05:27 - Recreated AGENTS.md and GEMINI.md after cleanup; restored operating rules (AGENTS.md, GEMINI.md).
- 2026-01-10 05:30 - Made subject image previews resolve against the current URL to avoid path issues (stories/template/subjects/index.html).
- 2026-01-10 05:38 - Reviewed drehbuch include file links; only adobe_drehbuch.md exists in template briefings, others are missing (engine/workers/drehbuch.py, stories/template/briefings/adobe_drehbuch.md).
- 2026-01-11 02:04 - Added Ge'ez morphology schema/tagset/function word list + filter, refreshed analysis worker prompts, and documented the A-D pipeline (engine/config/gez_morphology.schema.json, engine/config/gez_pos_tagset.json, engine/config/gez_function_words.json, engine/workers/geez_morphology_filter.py, engine/workers/worker_llm_analysis_graphematic.py, engine/workers/worker_llm_analysis_Morphologic.py, engine/workers/worker_llm_analysis_synthactic.py, engine/workers/worker_llm_analysis_semantic-historical.py, docs/geez_analysis_methodology.md, docs/workers.md, README.md).
- 2026-01-11 02:49 - Added deterministic token + tagset inputs to the morphology worker, wired synthactic/semantic workers to consume prior JSON outputs, aligned context-window tests, and updated Ge'ez function-word lists (engine/workers/worker_llm_analysis_Morphologic.py, engine/workers/worker_llm_analysis_synthactic.py, engine/workers/worker_llm_analysis_semantic-historical.py, engine/run_pipeline.py, engine/analysis/tagsets/gez_pos_1.json, engine/config/gez_pos_tagset.json, engine/config/gez_function_words.json, README_pipeline.md, docs/workers.md).
- 2026-01-11 03:25 - Enforced upstream dependency waits in analysis workers (B waits for A, C for B, D for C) and documented the workflow note (engine/workers/worker_llm_analysis_Morphologic.py, engine/workers/worker_llm_analysis_synthactic.py, engine/workers/worker_llm_analysis_semantic-historical.py, docs/workers.md, README.md).
- 2026-01-11 03:49 - Added chapter-batch mode to run one LLM request per chapter and fan out per-segment outputs (engine/workers/worker_llm_analysis_graphematic.py, engine/workers/worker_llm_analysis_Morphologic.py, engine/workers/worker_llm_analysis_synthactic.py, engine/workers/worker_llm_analysis_semantic-historical.py, docs/workers.md, README.md).
- 2026-01-11 04:01 - Fixed filter override recursion in the morphology worker after chapter-batch changes (engine/workers/worker_llm_analysis_Morphologic.py).
