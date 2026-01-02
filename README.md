# VisionExe

Repo layout (engine + stories).

- engine/        Tools, workers, workflows, configs.
- stories/       One folder per story.
  - template/    Empty story template (copy or clone).

Story layout:
- Filmsets: `chapter_###/segment_###/scene_###/timeline_##/` (scene folders are on by default).
- Subjects: `stories/<story>/subjects/` (registry, profiles, occurrences, asset_bible.json).

Core data flow (minimal):
1. `analysis_master_builder.py` -> `data/analysis/analysis_master.jsonl`
2. `subject_registry_builder.py` -> subjects registry + profiles + occurrences + scenes
3. `asset_bible_builder.py` -> `subjects/asset_bible.json`
4. `scene_instruction_builder.py` -> `subjects/scene_instructions.jsonl` (REGIE_JSON extraction)

Ge'ez subjects (optional):
- `engine/workers/subjects_from_geez.py` -> `subjects/subject_candidates_geez.json` + `subjects/subject_occurrences_geez.jsonl`
- Run: `python engine/workers/subjects_from_geez.py --story-root stories/template`

LoRA flow (template):
1. `lora_index_builder.py` -> `subjects/lora_index.json`
2. `lora_pipeline_builder.py` -> `data/lora/lora_pipeline.jsonl`

Direct actor sources:
- `lora_index.json` includes training image folders (`style_seed_dir`, `multiangle_dir`) so scenes can use a training cutout
  instead of a LoRA when it fits.

Dynamic subjects:
- All subjects are included in the registry. Dynamic ones are flagged and get per-segment or per-scene state slots.

Viewer:
- `engine/scripts/run_subjects_view.ps1` starts a local server and opens the subjects page.

Launchers:
- `engine/launchers/Start-Workspaces.ps1` lists/opens external workspaces and can run configured start commands.

Workspace registry:
- `engine/config/workspaces.json` tracks external Windows/WSL workspaces and entry points.
- `docs/workspaces.md` summarizes usage and notes.

Workflow catalog:
- `engine/config/workflow_catalog.json` lists agentic workflow mappings.
- `docs/workflows.md` summarizes workflow usage notes and view ordering.
- `engine/workers/comfy_orchestrator.py` resolves workflow IDs/labels from the catalog when you pass `--text-to-image` or `--image-to-image`.

Audio (STT):
- `engine/workers/stt_worker.py` transcribes audio with Whisper and reports similarity/WER when a reference text is provided.

Video docking:
- `docs/video_docking.md` describes REGIE_JSON video_plan metadata and capture inputs.
- REGIE_JSON can include `start_image_keywords` to inject LoRA trigger words into start image prompts.
- LoRAs are injected as prompt tags (e.g. `<lora:folder/name.safetensors:0.8>`) by the chapter asset generators.
- Capture library lives under `stories/<story>/data/capture`.
- `engine/workers/capture_library_builder.py` indexes capture clips into `subjects/pose_library.json` and `subjects/viseme_library.json`.

RAG (small):
- `engine/scripts/run_rag_small.ps1` indexes `stories/template/data/raw` into Qdrant using `engine/scripts/rag_config_small.json`.
