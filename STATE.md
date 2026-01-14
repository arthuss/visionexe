# STATE

Append-only hard-state context for this repo. Do not rewrite; add new versions
at the end of the file.

Codex may always read this file.

## Version 1 (2026-01-12 04:04)
- Repo name: VisionExe.
- Top-level layout: `engine/` (tools/workers/config) and `stories/` (story data).
- Analysis layers A-D write per-segment outputs:
  `analysis_llm_graphematic.txt`, `analysis_llm_morphologic.txt`,
  `analysis_llm_synthactic.txt`, `analysis_llm_semantic_historical.txt`.
- Aggregated per-segment analysis output: `analysis_llm.txt`.
- Default story template root: `stories/template` (unless overridden by config).

## Version 2 (2026-01-12 06:25)
- Legacy log entries moved to `STATE_LEGACY.md` to keep STATE small.
- Hard-state files use ASCII-only text going forward.

## Log
- 2026-01-12 06:25 - Normalized hard-state docs to ASCII and moved legacy logs to `STATE_LEGACY.md` (STATE.md, STATE_LEGACY.md, ARCHITECTURE.md, CONSTRAINTS.md, REFERENCES.md, AGENTS.md, GEMINI.md).
- 2026-01-12 06:35 - Cleaned hard-state files (ASCII-only), removed non-constraint lists, and created REFERENCES.md with the doc/config index (STATE.md, STATE_LEGACY.md, ARCHITECTURE.md, CONSTRAINTS.md, REFERENCES.md, AGENTS.md, GEMINI.md).
- 2026-01-12 17:28 - Rewrote Chapter 95 segment 5 to match the corrected verse line from chapter_95.txt (stories/template/filmsets/story_095/segment_005/segment.txt, docs/ethiopic_1enoch_p/chapter_95.txt).
- 2026-01-12 06:55 - Defaulted Vertex model fallback to gemini-2.5-pro for stable analysis runs (engine/workers/vertex_gemini.py).
- 2026-01-12 12:55 - Added pipeline-parallel status logging (per-job summary + ready counts) to the analysis orchestrator (engine/scripts/Linguistic_quad_worker.ps1).
- 2026-01-12 12:56 - Removed stray BOM characters from Linguistic_quad_worker.ps1 to fix PowerShell parsing (engine/scripts/Linguistic_quad_worker.ps1).
- 2026-01-12 12:54 - Switched analysis orchestrator to pipeline-parallel with 10 parallel chapters/calls and status logging enabled (stories/template/data/analysis/analysis_orchestrator_control.json).
- 2026-01-12 12:58 - Extended pipeline-parallel status logs to include missing-stage summary per active chapter (engine/scripts/Linguistic_quad_worker.ps1).
- 2026-01-13 13:04 - Pipeline-parallel now treats any missing stage as incomplete, logs job state, and enables auto self-heal config (engine/scripts/Linguistic_quad_worker.ps1, stories/template/data/analysis/analysis_orchestrator_control.json).
- 2026-01-13 13:04 - Documented default Vertex model and auto self-heal control options in README (README.md).
- 2026-01-13 13:41 - Replaced chapter story.txt sources with the docs/ethiopic_1enoch_p chapter files for all 108 chapters (stories/template/filmsets/story_###/story.txt, docs/ethiopic_1enoch_p/chapter_###.txt).
- 2026-01-13 14:49 - Replaced Chapter 108 text with the corrected Ethiopic source in docs and filmsets (docs/ethiopic_1enoch_p/chapter_108.txt, stories/template/filmsets/story_108/story.txt).
- 2026-01-13 16:25 - Orchestrator now prioritizes later stages (L/H/S/M/G) when selecting active chapters, and raised max parallel chapters to 40 (engine/scripts/Linguistic_quad_worker.ps1, stories/template/data/analysis/analysis_orchestrator_control.json, README.md).
- 2026-01-13 16:28 - Fixed PowerShell parsing by removing pipeline expressions from scriptblock Invoke calls in stage-priority selection (engine/scripts/Linguistic_quad_worker.ps1).
- 2026-01-13 16:35 - Added per-stage slot caps + fallback fill pass so M/H/L do not starve behind S/G backlog (engine/scripts/Linguistic_quad_worker.ps1, README.md).
- 2026-01-13 18:53 - Orchestrator now writes per-job logs when log_root is set in the control file (engine/scripts/Linguistic_quad_worker.ps1, stories/template/data/analysis/analysis_orchestrator_control.json, README.md).
- 2026-01-13 19:26 - Added chapter-level analysis scope, missing-only self-heal mode, and stricter dependency gating in the orchestrator; updated control defaults and README guidance (engine/scripts/Linguistic_quad_worker.ps1, stories/template/data/analysis/analysis_orchestrator_control.json, README.md).
- 2026-01-13 19:37 - Fixed chapter-scope worker flags so G/M/S/H run chapter-level (legacy per-segment flag inversion) and L keeps per-segment options only when applicable (engine/scripts/Linguistic_quad_worker.ps1).
- 2026-01-13 19:52 - Added segment_self_healer refresh mode to overwrite segment.txt from verse sources; README updated with the new flag (engine/workers/segment_self_healer.py, README.md).
- 2026-01-13 21:07 - Orchestrator now treats chapter-scope completion based on chapter-level analysis files, so stage gating works with chapter-level runs (engine/scripts/Linguistic_quad_worker.ps1).
- 2026-01-13 22:22 - Added docs index and refreshed worker doc references (docs/_index.md, docs/workers.md, REFERENCES.md).
- 2026-01-13 22:46 - Added docs index link and lookup note to AGENTS router (AGENTS.md).
- 2026-01-14 00:15 - Updated drehbuch/regie prompts for LTX v2 camera-control LoRA guidance and T2V-first video planning; documented in README and video docking notes (engine/workers/drehbuch.py, engine/workers/drehbuch_gemini.py, engine/workers/drehbuch_neu.py, engine/workers/regie_worker.py, docs/video_docking.md, README.md).
- 2026-01-14 00:38 - Added timeline profile support + subject registry injection for drehbuch prompts and updated story config defaults (stories/template/config/timelines/timeline_01.json, stories/template/config/story_config.json, engine/workers/drehbuch.py, engine/workers/drehbuch_gemini.py, engine/workers/drehbuch_neu.py, README.md).
