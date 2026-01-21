# ARCHITECTURE

Append-only hard-state architecture notes. Do not rewrite; append new versions.

Codex may always read this file.

## Version 1 (2026-01-12 04:04)
- Entry points live under `engine/workers` and are invoked via CLI.
- A-D linguistic analysis is a strict pipeline (B waits for A, C for B, D for C).
- Per-segment analysis files are stored inside
  `stories/<story>/filmsets/<chapter_label>_###/segment_###/`.
- LLM backends used by analysis workers: local Ollama, Gemini CLI, or Vertex AI
  (ADC over HTTPS).

## Version 2 (2026-01-12 06:25)
- The analysis orchestrator reads `analysis_orchestrator_control.json` and can run
  serial or pipeline-parallel scheduling depending on `mode`.
- Pipeline-parallel runs use chapter-level gating between stages (G -> M -> S -> H -> L)
  and a global slot cap for concurrent API calls.

## Version 3 (2026-01-20 09:06)
- Quickstart dependency mapping (scripts/workers/config):

```
Story config:
- stories/template/config/story_config.json
  - timeline_default -> stories/template/config/timelines/<timeline_id>.json
  - genre_profile -> stories/template/config/genre/*.json
  - style_profiles -> stories/template/config/styles/*.json
  - mechanism_profile -> stories/template/config/timelines/rule_of_machanism.json
  - filmsets_root, subjects_root, data_root, analysis_master_path, briefings, tone_dials

1) Filmsets scaffold
- engine/workers/setup_filmsets_from_geez.py
  - reads: story_config.json, geez_root (chapter_*_verses.jsonl)
  - writes: filmsets/<chapter_label>_###/segment_###/story.txt, segment.txt

2) Linguistic quad
- engine/scripts/Linguistic_quad_worker.ps1
  - reads: story_config.json, stories/<story>/data/analysis/analysis_orchestrator_control.json
  - calls: engine/workers/segment_self_healer.py (optional)
  - calls: engine/workers/worker_llm_analysis_graphematic.py
           engine/workers/worker_llm_analysis_Morphologic.py
           engine/workers/worker_llm_analysis_synthactic.py
           engine/workers/worker_llm_analysis_semantic-historical.py
           engine/workers/worker_llm_analysis.py
  - writes: analysis_llm*.txt (chapter or segment), analysis_progress CSV (story_config)

3) Segment integrity
- engine/workers/segment_self_healer.py
  - reads: story_config.json, docs/ethiopic_1enoch_p (verse_root)
  - writes: missing segment folders, segment.txt

4) Subject extraction (MCP-Registry flow)
- engine/scripts/reset_subject_registry.ps1
  - calls: knowledge_base/reset_subject_registry.py
  - reads: knowledge_base/requirements.txt, knowledge_base/.env, knowledge_base/docker-compose.yml
  - optional: engine/workers/rag_config_small.json (Qdrant delete)
- engine/scripts/start_mcp_subjects.ps1
  - calls: knowledge_base/visionexe_mcp_server.py
  - reads: knowledge_base/requirements.txt, knowledge_base/.env, knowledge_base/docker-compose.yml
  - optional: engine/workers/rag_config_small.json (Qdrant sync)
- engine/workers/subject_corpus_builder.py
  - reads: story_config.json, filmsets/**.txt
  - writes: stories/template/subjects/subject_corpus.json (or jsonl/csv)
- engine/workers/subject_registry_prompt_builder.py
  - reads: stories/template/subjects/subject_corpus.json
  - writes: stories/template/subjects/subject_registry_prompt.txt
- gemini CLI (MCP tool calls)
  - writes: pgvector subjects/aliases/notes via MCP

5) Subject extraction (Analysis-Master flow)
- stories/template/data/analysis/analysis_master.jsonl (input)
  - built by engine/workers/analysis_master_builder.py when used
- engine/workers/subject_registry_builder.py
  - reads: analysis_master.jsonl, story_config.json, profiles_seed.json (optional)
  - writes: subjects/registry.json, profiles.jsonl, occurrences.jsonl, scenes.jsonl,
            environment_route.jsonl, dynamic_subjects.json
- engine/workers/subject_registry_validate.py
  - reads: filmsets/<chapter_label>_###/story.txt, analysis_master.jsonl, registry.json
  - writes: subjects/registry_merge_log.json
- engine/workers/subject_registry_normalizer.py
  - reads: registry_merge_log.json + registry/profiles/occurrences
  - writes: normalized registry/profiles/occurrences + merge logs
- engine/workers/asset_bible_builder.py
  - reads: profiles.jsonl, occurrences.jsonl
  - writes: subjects/asset_bible.json
- engine/workers/asset_bible_enricher.py
  - reads: asset_bible.json, profiles.jsonl, occurrences.jsonl, analysis_master.jsonl,
           story_config.json (timeline/genre/style/briefings/tone_dials)
  - writes: subjects/ASSET_BIBLE.md, subjects/asset_bible_cards.jsonl,
           subjects/timelines/<timeline_label>_<tag>/<subject_id>/*

6) Subject registry imports (DB/MCP)
- engine/scripts/import_subject_registry.ps1 -> knowledge_base/import_subject_registry.py
  - reads: subjects/registry.json, profiles.jsonl, occurrences.jsonl, scenes.jsonl, dynamic_subjects.json
- engine/scripts/import_subject_context.ps1 -> knowledge_base/import_subject_context.py
  - reads: occurrences.jsonl, scenes.jsonl, environment_route.jsonl, dynamic_subjects.json
- engine/scripts/import_subject_overlays.ps1 -> knowledge_base/import_subject_overlays.py
  - reads: subjects/timelines/<timeline_id>/overlays.jsonl
```

Notes (2026-01-20)
- Subject typing split: `prop` is subject-bound (stores `owner_subject_ids`), scene dressing moves to `requisite`.
- `scene` stays narrative-only; `set_environment` remains the canonical location mapping from analysis.
