# GEMINI

In every run, read these files (read-only):
- `AGENTS.md`
- `STATE.md` (hard state, append-only)
- `ARCHITECTURE.md` (system design notes, append-only)
- `CONSTRAINTS.md` (non-negotiables, append-only)

Gemini writes append-only log entries under # log (deltas + links).
No other worker writes here.

# log
- 2026-01-13 13:41 - Replaced story.txt sources for all chapters with docs/ethiopic_1enoch_p chapter files (stories/template/filmsets/story_###/story.txt, docs/ethiopic_1enoch_p/chapter_###.txt).
- 2026-01-13 14:49 - Replaced Chapter 108 text with the corrected Ethiopic source in docs and filmsets (docs/ethiopic_1enoch_p/chapter_108.txt, stories/template/filmsets/story_108/story.txt).
- 2026-01-13 16:25 - Orchestrator now prioritizes later stages when selecting active chapters and raised max parallel chapters to 40 (engine/scripts/Linguistic_quad_worker.ps1, stories/template/data/analysis/analysis_orchestrator_control.json, README.md).
- 2026-01-13 16:28 - Fixed stage-priority selection parsing by avoiding pipeline expressions inside Invoke (engine/scripts/Linguistic_quad_worker.ps1).
- 2026-01-13 16:35 - Added stage slot caps and fallback fill pass to avoid starvation across M/H/L vs S/G (engine/scripts/Linguistic_quad_worker.ps1, README.md).
- 2026-01-13 18:53 - Added per-job log output via log_root in the orchestrator control file (engine/scripts/Linguistic_quad_worker.ps1, stories/template/data/analysis/analysis_orchestrator_control.json, README.md).
- 2026-01-13 19:26 - Added chapter-level analysis scope, missing-only self-heal mode, and stricter dependency gating in the orchestrator; updated control defaults and README guidance (engine/scripts/Linguistic_quad_worker.ps1, stories/template/data/analysis/analysis_orchestrator_control.json, README.md).
- 2026-01-13 19:37 - Fixed chapter-scope worker flags so G/M/S/H run chapter-level (legacy per-segment flag inversion) and L keeps per-segment options only when applicable (engine/scripts/Linguistic_quad_worker.ps1).
- 2026-01-13 19:52 - Added segment_self_healer refresh mode to overwrite segment.txt from verse sources; README updated with the new flag (engine/workers/segment_self_healer.py, README.md).
- 2026-01-13 21:07 - Orchestrator now treats chapter-scope completion based on chapter-level analysis files, so stage gating works with chapter-level runs (engine/scripts/Linguistic_quad_worker.ps1).
- 2026-01-13 22:22 - Added docs index and refreshed worker doc references (docs/_index.md, docs/workers.md, REFERENCES.md).
- 2026-01-13 22:46 - Added docs index link and lookup note to AGENTS router (AGENTS.md).
- 2026-01-14 00:15 - Updated drehbuch/regie prompts for LTX v2 camera-control LoRA guidance and T2V-first video planning; documented in README and video docking notes (engine/workers/drehbuch.py, engine/workers/drehbuch_gemini.py, engine/workers/drehbuch_neu.py, engine/workers/regie_worker.py, docs/video_docking.md, README.md).
- 2026-01-14 00:38 - Added timeline profile support + subject registry injection for drehbuch prompts and updated story config defaults (stories/template/config/timelines/timeline_01.json, stories/template/config/story_config.json, engine/workers/drehbuch.py, engine/workers/drehbuch_gemini.py, engine/workers/drehbuch_neu.py, README.md).
- 2026-01-13 13:04 - Pipeline-parallel logging now includes job state, considers any missing stage incomplete, and auto self-heal can be toggled in the control file; README updated for default Vertex model + auto self-heal (engine/scripts/Linguistic_quad_worker.ps1, stories/template/data/analysis/analysis_orchestrator_control.json, README.md).
- 2026-01-12 07:42 - Segment self-healer now backfills full verse range with overrides + extra-segment reporting; missing segments created for chapters 14/18/28/30/66/68/71/72/77/78/104 (engine/workers/segment_self_healer.py, README.md, stories/template/filmsets/story_014/segment_025/segment.txt, stories/template/filmsets/story_018/segment_016/segment.txt, stories/template/filmsets/story_028/segment_002/segment.txt, stories/template/filmsets/story_030/segment_003/segment.txt, stories/template/filmsets/story_066/segment_003/segment.txt, stories/template/filmsets/story_068/segment_005/segment.txt, stories/template/filmsets/story_071/segment_001/segment.txt, stories/template/filmsets/story_072/segment_002/segment.txt, stories/template/filmsets/story_077/segment_002/segment.txt, stories/template/filmsets/story_078/segment_013/segment.txt, stories/template/filmsets/story_104/segment_011/segment.txt, stories/template/data/analysis/segment_self_heal_report.json).
- 2026-01-12 08:01 - Reported extra segments for chapters 69/87 (69:30, 87:4); no segments created (stories/template/data/analysis/segment_self_heal_report.json).
- 2026-01-12 06:25 - Normalized hard-state docs to ASCII, moved legacy logs to STATE_LEGACY.md, and created REFERENCES.md for doc/config indices (STATE.md, STATE_LEGACY.md, ARCHITECTURE.md, CONSTRAINTS.md, REFERENCES.md, AGENTS.md).
- 2026-01-12 06:35 - Cleaned hard-state files (ASCII-only), removed non-constraint lists, and created REFERENCES.md with the doc/config index (STATE.md, STATE_LEGACY.md, ARCHITECTURE.md, CONSTRAINTS.md, REFERENCES.md, AGENTS.md, GEMINI.md).
- 2026-01-12 17:28 - Synced Chapter 95 segment 5 content with the corrected verse line (stories/template/filmsets/story_095/segment_005/segment.txt, docs/ethiopic_1enoch_p/chapter_95.txt).
- 2026-01-12 06:55 - Defaulted Vertex model fallback to gemini-2.5-pro for stable analysis runs (engine/workers/vertex_gemini.py).
- 2026-01-12 12:55 - Added pipeline-parallel status logging (per-job summary + ready counts) to the analysis orchestrator (engine/scripts/Linguistic_quad_worker.ps1).
- 2026-01-12 12:56 - Removed stray BOM characters from Linguistic_quad_worker.ps1 to fix PowerShell parsing (engine/scripts/Linguistic_quad_worker.ps1).
- 2026-01-12 12:54 - Switched analysis orchestrator to pipeline-parallel with 10 parallel chapters/calls and status logging enabled (stories/template/data/analysis/analysis_orchestrator_control.json).
- 2026-01-12 12:58 - Extended pipeline-parallel status logs to include missing-stage summary per active chapter (engine/scripts/Linguistic_quad_worker.ps1).
