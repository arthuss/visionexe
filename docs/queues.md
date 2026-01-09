# Queues and Job Files

This document lists every queue-like file in VisionExe, who produces it, who consumes it, and which ones are timeline-aware. Use this as the source of truth when wiring new queue builders or refactoring legacy ones.

## 1) Timeline-aware queues (primary)

These live under `stories/<story>/` and should be treated as the canonical, timeline-scoped inputs.

### 1.0 Asset Bible subject image queue
- Path: `stories/<story>/data/queues/asset_bible_queue.json`
- Producer: `engine/workers/asset_bible_queue_builder.py` or `engine/scripts/run_subject_image_queue.ps1`.
- Consumer: `engine/workers/comfy_orchestrator.py` (`--queue`).
- Purpose: Generate subject images from ASSET_BIBLE prompts (non-LoRA image runs).

### 1.1 iClone actor load queue
- Path: `stories/<story>/subjects/actor_queue.jsonl`
- Producer: manual (append JSONL lines), or scripts that emit actor names.
- Consumer: `engine/scripts/load_actors.ps1` -> `iclone_remote_client.py`.
- Format (one JSON per line):
  - `name`: actor name in Content Manager (e.g. `vx_henoch_p01`)
  - `prefer` (optional): `content_manager` or `index`
- Use when staging in iClone (load the actors before pose/MD).

### 1.2 LoRA training queue (Comfy orchestrator, training only)
- Path: `stories/<story>/data/lora/lora_training_queue.json`
- Producer:
  - Legacy: `prepare_lora_queue.py` (Henoch-only paths).
  - Future: dedicated LoRA-training queue builder (not implemented yet).
- Consumer: `engine/workers/comfy_orchestrator.py` (phase 1/2).
- Timeline scope: queue should be timeline-specific; pass `--queue` when running the orchestrator.
- Notes:
  - This queue is for LoRA training jobs only.
  - Do not use it for subject image generation (those belong to `asset_bible_queue.json`).
  - Dataset roots come from `lora_training_set.json` (style_seed/multiangle dirs).

### 1.3 LoRA prop queue (legacy)
- Path: `stories/<story>/data/lora/lora_prop_queue.json`
- Producer:
  - Legacy: `prepare_prop_queue.py` (Henoch-specific).
- Consumer: `engine/workers/lora_index_builder.py` (prop training map).
- Timeline scope: legacy; migrate when a timeline-aware builder exists.

### 1.4 LoRA pipeline tasks (not a Comfy queue)
- Path: `stories/<story>/data/lora/lora_pipeline.jsonl`
- Producer: `engine/workers/lora_pipeline_builder.py`
- Consumer: future queue materializer (or manual conversion).
- Timeline scope: yes (`--timeline` picks `timeline_##`).
- Content: step-by-step tasks (style_seed, style_train, multiangle_gen, base_train).

### 1.5 LoRA index (not a queue)
- Path: `stories/<story>/subjects/lora_index.json`
- Producer: `engine/workers/lora_index_builder.py`
- Consumer: `lora_pipeline_builder.py`, asset registry, and start-image builders.
- Notes:
  - Pulls in dynamic states from subject profiles.
  - LoRA training folders are included for "use existing cutout" logic.
  - Phase entries can override training dirs when `style_seed_dir`/`multiangle_dir` are provided.

### 1.6 LoRA training set (metadata, not a queue)
- Path: `stories/<story>/data/lora/lora_training_set.json`
- Producer: `engine/workers/lora_dynamic_queue_builder.py`
- Consumer: `engine/workers/lora_index_builder.py`
- Notes:
  - This is the canonical metadata for dynamic states (phases + prompt blocks).
  - Stores `style_seed_dir`/`multiangle_dir` relative to the repo for each phase.

## 2) Subject state inputs (used for queue logic)

Queue builders should use these to separate static vs dynamic:
- `stories/<story>/subjects/profiles.jsonl`
  - Fields: `is_dynamic`, `state_policy`, `states` (phase/per_scene/per_occurrence)
- `stories/<story>/subjects/dynamic_subjects.json`
  - Contains dynamic subjects only.

Rule of thumb:
- Dynamic subjects => queue LoRA training per state.
- Static subjects => queue only minimal stills (or rely on compositing/masks).

## 3) Other queue-like outputs (per chapter/tools)

These are not timeline-aware yet, but are used by specialized workers.

### 3.1 CC Headshot queue
- Path: `engine/character_creator/cc_command.json`
- Producer: `engine/workers/cc_headshot_enqueue.py`
- Consumer: `engine/character_creator/cc_file_watcher.py` (runs inside CC4)
- Purpose: enqueue headshot jobs and save `.ccAvatar` to Reallusion Custom.

### 3.2 Vision audit queue
- Path (default): `filmsets/<chapter>/vision/vision_audit_queue.json`
- Producer: `engine/workers/vision_audit_worker.py`
- Consumer: `vision_audit_worker.py` (sends to LLM API).
- Note: legacy path uses `chapter_###`; update if using `story_###`.

### 3.3 Hybrid composite queue
- Path (default): `filmsets/chapter_###/Media/chapter_###_hybrid_queue.json`
- Producer: `engine/workers/hybrid_composite_worker.py`
- Consumer: manual or post pipeline (SAM3/composite).
- Note: legacy path uses Henoch root and `chapter_###`.

### 3.4 Facesync queue
- Path (default): `C:\Users\sasch\henoch\facesync_queue.json`
- Producer/Consumer: `engine/workers/facesync_worker.py`
- Note: legacy path, update to story_config when migrated.

### 3.5 Ad-hoc Comfy queue outputs
- `engine/workers/generate_assets.py --queue-out <path>` (asset-bible or custom prompts)
- `engine/workers/hybrid_composite_worker.py --queue <path>` (manual overrides)
- `engine/workers/queue_actor_from_csv.py` queues directly to ComfyUI (no file queue).

## 4) Legacy queue builders (Henoch paths)

These still hard-code `C:\Users\sasch\henoch` and are not timeline-aware:
- `engine/workers/prepare_lora_queue.py`
- `engine/workers/prepare_prop_queue.py`
- `engine/workers/generate_lora_prompts.py`
- `engine/workers/facesync_worker.py` (default queue path)
- `engine/workers/hybrid_composite_worker.py` (default chapter root)

If you need a timeline-safe pipeline, build queues from:
1) `subjects/profiles.jsonl` (dynamic states)
2) `subjects/lora_index.json`
3) `data/lora/lora_pipeline.jsonl`
Then write a timeline-specific `lora_training_queue.json` and run:
```
python engine/workers/comfy_orchestrator.py --story-config stories/<story>/config/story_config.json --queue <queue_path>
```
