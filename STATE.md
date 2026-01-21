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
- 2026-01-17 03:47 - Added compendium build workflow + generated export, updated router rules for GEMINI/STATE logging (engine/tools/build_workspace_compendium.py, docs/WORKSPACE_COMPENDIUM.md, docs/compendium_sections/00_overview.md, docs/compendium_sections/10_structure.md, docs/_index.md, REFERENCES.md, README.md, AGENTS.md, GEMINI.md).
- 2026-01-17 06:54 - Added narration screenplay worker, RAG index/query fixes, narration inputs + analysis layers in drehbuch prompts, and audio narration source support (engine/workers/drehbuch_narration_worker.py, engine/workers/rag_indexer.py, engine/workers/rag_query.py, engine/workers/drehbuch.py, engine/workers/drehbuch_gemini.py, engine/workers/drehbuch_neu.py, engine/workers/audio_agent.py, docs/workers.md, README.md).
- 2026-01-17 08:21 - Set LMStudio default model to zai-org/glm-4.6v-flash, ensured narration worker uses source prompt + briefings, and added LTX2 guide to drehbuch_gemini prompts (engine/config/llm_profiles.json, engine/workers/drehbuch_narration_worker.py, engine/workers/drehbuch_gemini.py).
- 2026-01-17 19:34 - Fixed drehbuch_narrativ prompt file to close the third fenced block (docs/drehbuch_narrativ.md).
- 2026-01-17 20:09 - Moved legacy audio/regie scripts into engine/scripts/_legacy and noted legacy wrapper location in README (engine/scripts/_legacy/run_regie_audio.ps1, engine/scripts/_legacy/start_tts.ps1, engine/scripts/_legacy/audio_agent_redefine.ps1, README.md).
- 2026-01-18 01:41 - Added style/genre/tone controls via story_config and propagated them into drehbuch prompts and narration worker defaults (stories/template/config/story_config.json, engine/workers/drehbuch_narration_worker.py, engine/workers/drehbuch.py, engine/workers/drehbuch_gemini.py, engine/workers/drehbuch_neu.py, README.md).
- 2026-01-18 02:36 - Synced drehbuch.py with gemini prompts while keeping Copilot backend, moved drehbuch_neu.py to legacy, and ran chapter-1 test (engine/workers/drehbuch.py, engine/workers/_legacy/drehbuch_neu.py).
- 2026-01-18 02:42 - Removed stray analysis layer outputs from chapter subfolders (analysis_linguistik/visual_abc/tech_hypothesen/concept_engine) while keeping segment analysis intact (stories/template/filmsets/story_###/*).
- 2026-01-18 02:44 - Set LMStudio default model to nvidia/nemotron-3-nano for local/remote profiles (engine/config/llm_profiles.json).
- 2026-01-18 03:38 - Removed chapter-level legacy subfolders (analysis_linguistik, concept_engine, tech_hypothesen, visual_abc) across filmsets after backup.
- 2026-01-18 04:15 - Added QUICKSTART workflow doc and linked it from README (QUICKSTART.md, README.md).
- 2026-01-18 05:38 - Rewrote QUICKSTART workflow to use PS1 orchestrators, timeline/genre/style selection, and subject/LoRA/video steps; added script index and examples.
- 2026-01-18 05:38 - Expanded QUICKSTART script index with ComfyUI/diffusion/monitor helpers.
- 2026-01-18 06:38 - Reordered QUICKSTART to run subject registry + asset bible before narration/screenplay, and updated asset_bible_enricher to generate long-form prose cards with timeline/genre/style/tone injection.
- 2026-01-18 21:30 - Normalized gemini-3-pro to gemini-3-pro-preview in asset_bible_enricher and updated QUICKSTART example.
- 2026-01-18 21:35 - Rebuilt analysis_master.jsonl from latest analysis CSV and layer files (engine/workers/analysis_master_builder.py).
- 2026-01-18 21:39 - Filtered asset_bible_enricher to default to character/prop/set_environment types and documented the new --types option in QUICKSTART.
- 2026-01-18 21:54 - Added subject registry validation + normalization workers and wired them into QUICKSTART/README (engine/workers/subject_registry_validate.py, engine/workers/subject_registry_normalizer.py).
- 2026-01-18 21:56 - Fixed subject_registry_validate to honor chapter_label when loading story.txt from filmsets and added fallback scan.
- 2026-01-18 22:05 - Added JSON block extraction + raw-output fallback to subject_registry_validate for non-JSON Gemini responses.
- 2026-01-18 23:32 - Added pgvector MCP subject registry server + documented optional MCP startup steps (knowledge_base/visionexe_mcp_server.py, QUICKSTART.md, README.md).
- 2026-01-19 00:05 - Added MCP Qdrant sync for subject upserts/aliases/merges and documented env flags for Qdrant auto-indexing (knowledge_base/visionexe_mcp_server.py, QUICKSTART.md, README.md).
- 2026-01-19 00:26 - Added subject registry bulk importer and local Qwen embedding server helper; documented optional RAG embedder (knowledge_base/import_subject_registry.py, engine/tools/qwen_embedder/*, README.md).
- 2026-01-19 00:45 - Moved director/manual + strict source rules into timeline_01 profile and removed hardcoded blocks from drehbuch workers; updated QUICKSTART with default registry import + local embedder steps (stories/template/config/timelines/timeline_01.json, engine/workers/drehbuch.py, engine/workers/drehbuch_gemini.py, QUICKSTART.md).
- 2026-01-19 01:05 - Switched drehbuch workers to load rule_of_machanism.json via mechanism_profile and added the config default in story_config; updated QUICKSTART note (stories/template/config/story_config.json, engine/workers/drehbuch.py, engine/workers/drehbuch_gemini.py, QUICKSTART.md).
- 2026-01-19 01:22 - Added mechanism_profile injection to narration worker worldview context (engine/workers/drehbuch_narration_worker.py).
- 2026-01-19 01:38 - Added PowerShell launchers that create venvs for registry import and Qwen embedder startup; updated QUICKSTART/README to use them (engine/scripts/import_subject_registry.ps1, engine/scripts/start_qwen_embedder.ps1, QUICKSTART.md, README.md).
- 2026-01-19 01:46 - Fixed PowerShell param blocks to be first statements in new launchers (engine/scripts/import_subject_registry.ps1, engine/scripts/start_qwen_embedder.ps1).
- 2026-01-19 01:52 - Added MCP subjects launcher with optional Qdrant sync and documented it in QUICKSTART/README (engine/scripts/start_mcp_subjects.ps1, QUICKSTART.md, README.md).
- 2026-01-19 02:02 - Updated MCP launcher to auto-create venv and install requirements before start (engine/scripts/start_mcp_subjects.ps1).
- 2026-01-19 02:10 - Replaced Gemini MCP Docker gateway with local visionexe-subjects stdio server config (C:\Users\sasch\.gemini\settings.json).
- 2026-01-19 02:13 - Enabled Qdrant sync in Gemini MCP config and set default rag_config_small.json (C:\Users\sasch\.gemini\settings.json).
- 2026-01-19 02:30 - Added subject overlay schema + importer, wired overlays into drehbuch prompts, and documented overlay location (knowledge_base/setup_visionexe_schema.py, knowledge_base/import_subject_overlays.py, stories/template/subjects/timelines/timeline_01/overlays.jsonl, engine/workers/drehbuch.py, engine/workers/drehbuch_gemini.py, QUICKSTART.md).
- 2026-01-19 02:41 - Added overlay import venv launcher and made overlay import auto-create missing subjects; updated QUICKSTART/README accordingly (knowledge_base/import_subject_overlays.py, engine/scripts/import_subject_overlays.ps1, QUICKSTART.md, README.md).
- 2026-01-19 02:49 - Overlay import now tags auto-created subjects with review_status and writes a report file for follow-up (knowledge_base/import_subject_overlays.py, stories/template/subjects/overlay_autocreated_subjects.json).
- 2026-01-21 00:59 - Added LM Studio (openai-compat) backend to asset_bible_enricher, added LM Studio flag to narration worker, and documented Gemini project disable envs (engine/workers/asset_bible_enricher.py, engine/workers/drehbuch_narration_worker.py, README.md).
- 2026-01-21 01:36 - Set LM Studio as default LLM profile and added LM Studio support to drehbuch workers (engine/config/engine_config.json, engine/workers/drehbuch.py, engine/workers/drehbuch_gemini.py, README.md).
- 2026-01-21 01:48 - Enabled thinking passthrough for OpenAI-compatible profiles and set gpt-oss thinking to high by default (engine/config/llm_profiles.json, engine/workers/asset_bible_enricher.py, engine/workers/drehbuch_narration_worker.py, engine/workers/drehbuch.py, engine/workers/drehbuch_gemini.py, README.md).
- 2026-01-21 01:58 - Fixed asset_bible_enricher resume to skip existing per-subject cards and report progress against filtered totals (engine/workers/asset_bible_enricher.py).
- 2026-01-21 02:01 - Resume now prefers JSONL entries and only falls back to on-disk subject cards when JSONL is empty (engine/workers/asset_bible_enricher.py).
- 2026-01-21 02:05 - Default asset_bible_enricher types now include scene; README updated (engine/workers/asset_bible_enricher.py, README.md).
- 2026-01-19 02:55 - Overlay import now always writes the auto-created subject report (empty when none) for consistent auditing (knowledge_base/import_subject_overlays.py).
- 2026-01-19 03:02 - Overlay report now includes existing subjects alongside auto-created placeholders for clearer audit context (knowledge_base/import_subject_overlays.py).
- 2026-01-19 03:18 - Added subject context schema + importer (occurrences/scenes/environment/dynamic) and documented the new PS1 launcher (knowledge_base/setup_visionexe_schema.py, knowledge_base/import_subject_context.py, engine/scripts/import_subject_context.ps1, QUICKSTART.md, README.md).
- 2026-01-19 03:35 - Added MCP read tools for subject occurrences/scenes/environment_route/dynamic subjects and aligned MCP schema with context tables; documented read tools in README (knowledge_base/visionexe_mcp_server.py, README.md).
- 2026-01-19 03:49 - Added optional truncate flag for subject context import and documented it in QUICKSTART/README (knowledge_base/import_subject_context.py, engine/scripts/import_subject_context.ps1, QUICKSTART.md, README.md).
- 2026-01-19 04:02 - Added MCP cleanup tools for context tables and ensured merge_subjects reassigns occurrences/overlays/dynamic subjects; included IDs in fetch outputs (knowledge_base/visionexe_mcp_server.py, README.md).
- 2026-01-19 23:04 - Added CLI-compatible --timeline flag for subject registry builder and aligned schema setup DB env fallback (engine/workers/subject_registry_builder.py, knowledge_base/setup_visionexe_schema.py).
- 2026-01-20 03:21 - Added prompt dump flag for subject_registry_validate, raw corpus + prompt builders for MCP subject extraction, registry reset script with optional Qdrant cleanup, and auto-fallback to Gemini when Ollama is unavailable in asset_bible_enricher; updated QUICKSTART/README (engine/workers/subject_registry_validate.py, engine/workers/subject_corpus_builder.py, engine/workers/subject_registry_prompt_builder.py, knowledge_base/reset_subject_registry.py, engine/scripts/reset_subject_registry.ps1, engine/workers/asset_bible_enricher.py, QUICKSTART.md, README.md).
- 2026-01-20 03:30 - Removed generated DREHBUCH_HOLLYWOOD and chapter_briefing files and cleared audio outputs under filmsets.
- 2026-01-20 09:00 - Renamed subject extraction sections in QUICKSTART to remove legacy labeling (MCP-Registry vs Analysis-Master flow).
- 2026-01-20 09:07 - Updated README labels for subject extraction flows and added Quickstart dependency mapping tree to ARCHITECTURE.md.
- 2026-01-20 09:21 - Added Gemini API cache support to asset_bible_enricher and documented cache usage in README.
- 2026-01-20 10:59 - Added explicit Gemini API model override for cache usage and documented `--gemini-api-model` in README (engine/workers/asset_bible_enricher.py, README.md).
- 2026-01-20 11:54 - Added Vertex backend option and guarded paid Gemini API cache for asset_bible_enricher; updated README usage notes (engine/workers/asset_bible_enricher.py, README.md).
- 2026-01-20 12:05 - Added Gemini CLI project override and safer Copilot fallback model handling; documented CLI project requirement in README (engine/workers/asset_bible_enricher.py, README.md).
- 2026-01-20 12:10 - Defaulted GOOGLE_CLOUD_PROJECT for workers via visionexe_paths and documented fallback project (engine/workers/visionexe_paths.py, README.md).
- 2026-01-20 12:39 - Added Vertex backend option to drehbuch_narration_worker and documented Vertex flags in README (engine/workers/drehbuch_narration_worker.py, README.md).
- 2026-01-20 23:10 - Added Discovery Engine sample script for Agent Builder testing (C:\\Users\\sasch\\gemini\\discovery_samples\\discovery_search.py).
- 2026-01-21 00:48 - Added Gemini CLI opt-out for project injection and documented disabling default GCP project (engine/workers/asset_bible_enricher.py, engine/workers/visionexe_paths.py, README.md).
- 2026-01-21 03:22 - Split subject-bound props from scene requisites with owner_subject_ids, updated registry builder/validator, asset bible outputs, and docs (engine/workers/subject_registry_builder.py, engine/workers/subject_registry_validate.py, engine/workers/asset_bible_enricher.py, engine/workers/asset_bible_builder.py, engine/workers/asset_bible_queue_builder.py, engine/workers/subject_registry_prompt_builder.py, engine/config/subjects_keymap.json, README.md, QUICKSTART.md, ARCHITECTURE.md).
- 2026-01-21 21:02 - Removed legacy knowledge_base + qwen_embedder, switched docs to exevision drop-in, and added legacy guards/wrappers for old MCP scripts (knowledge_base/, engine/tools/qwen_embedder/, engine/scripts/start_qwen_embedder.ps1, engine/scripts/start_mcp_subjects.ps1, engine/scripts/import_subject_*.ps1, engine/scripts/reset_subject_registry.ps1, README.md, QUICKSTART.md, engine/tools/exevision/env/README.md).
- 2026-01-21 22:45 - Reviewed exevision drop-in folders and MCP wiring; noted legacy MCP scripts are stubs and exevision QUICKSTART reference is missing (QUICKSTART.md, README.md, engine/tools/exevision/*).
- 2026-01-21 23:03 - Updated exevision story loader defaults/examples to point at data/Story1-Henoch (engine/tools/exevision/story_tools/story_loader.py, engine/tools/exevision/story_tools/README.md, engine/tools/exevision/scripts/README.md).
- 2026-01-21 23:15 - Audited analysis integration usage and config references; mapped analysis file consumers and engine/analysis usage (no code changes).
