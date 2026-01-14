# Workers Overview

This document summarizes the worker scripts in `engine/workers` and how they fit the pipeline.

## Core Pipeline
- `visionexe_paths.py`: path and root helpers shared across workers.
- `comfy_orchestrator.py`: runs ComfyUI queues and collects outputs.
- `generate.py`: legacy entry point for older pipelines.

## Story and Screenplay
- `setup_filmsets_from_geez.py`: creates filmset folders from Ge'ez sources.
- `worker_llm_analysis.py`: LLM analysis per segment/chapter.
- `analysis_master_builder.py`: aggregates analysis into a master index.
- `chapter_briefing_builder.py`: chapter briefings used before script generation.
- `drehbuch.py` / `drehbuch_gemini.py`: screenplay generation (loads timeline profile + subject registry; override with `--timeline`).
- `scene_instruction_builder.py`: extracts per-scene instructions and layouts.
- `regie_worker.py`: fills/regenerates REGIE blocks when needed.

## Ge'ez Linguistic Analysis
- The A-D workers support three modes: per-segment (default when run directly), chapter-batch (single request that
  returns per-segment JSON), and chapter-level (single request + distribute outputs).
- Note: G/M/S/H use a legacy inverted `--per-segment` flag (it disables per-segment). Prefer the orchestrator control
  `analysis_scope` in `stories/<story>/data/analysis/analysis_orchestrator_control.json` to avoid flag confusion.
- `worker_llm_analysis_graphematic.py`: Level A graphematic capture (no normalization).
- `worker_llm_analysis_Morphologic.py`: Level B morphology matrix output (waits for graphematic output when running per segment).
- `worker_llm_analysis_synthactic.py`: Level C syntactic hypothesis enumeration (waits for morphology output; prefers `analysis_llm_morphologic.txt` tokens when present).
- `worker_llm_analysis_semantic-historical.py`: Level D semantic/historical evaluation (waits for synthactic output; uses parses + morphology lemmas when available).
- `segment_self_healer.py`: backfills missing segments and can refresh segment.txt from verse sources (`--refresh-existing`).
- `geez_morphology_filter.py`: rule-based filter for morphology output (see `docs/geez_analysis_methodology.md`).
- `worker_rule_filter.py`: apply rule filters to JSON artifacts.
- `worker_tests.py`: summarize validation + test status for analysis artifacts.
- `run_pipeline.py`: end-to-end Ge'ez analysis pipeline runner.

## Subjects and Asset Bible
- `subject_registry_builder.py`: builds subject registry + occurrences + scenes.
- `asset_bible_builder.py`: base asset bible JSON from analysis.
- `asset_bible_enricher.py`: prompt-ready cards (Gemini/Copilot fallback).
- `asset_bible_queue_builder.py`: ComfyUI queue for subject images from per-phase Asset Bible cards.
- `asset_registry_builder.py`: unified asset registry mappings.
- `collect_asset_bible.py`: collect generated assets into bible folders.

## LoRA and Training
- `lora_dynamic_queue_builder.py`: LoRA queues from dynamic subjects.
- `lora_index_builder.py`: index available LoRAs.
- `lora_pipeline_builder.py`: LoRA training pipeline tasks.
- `train_lora_worker.py`: sends LoRA training jobs.

## Audio
- `audio_agent.py`: scene/chapter audio plan + TTS pipeline.
- `voice_cast_builder.py`: assigns voices using TTS registry.
- `stt_worker.py`: speech-to-text utilities.
- `foley_worker.py`: sound effects generation.

## Animation and Posing
- `pose_bvh_importer.py`: BVH to pose JSON + pose library.
- `pose_keypoints_importer.py`: keypoints to pose JSON.
- `pose_catalog_builder.py`: pose catalog from assets.
- `scene_layout_builder.py`: blocking and spatial layout notes.

## iClone and Character Creator
- `iclone_remote_client.py`: HTTP client for iClone OpenPlugin.
- `animate_md_target.py`: Motion Director targeting helpers.
- `test_md_config.py`: MD configuration tests.
- `iclone_lipsync_runner.py`: Audio-driven lipsync.
- `cc_headshot_enqueue.py`: Character Creator headshot queue.
- `cc_save_actor.py`: save CC avatars to Content Manager.
- `reallusion_library_indexer.py`: index CC/iClone content.

## Utilities
- `download_ethiopic_enoch.py`: fetch Ge'ez sources.
- `queue_actor_from_csv.py`: queue actors from CSV.
