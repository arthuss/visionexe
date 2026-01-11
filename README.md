# VisionExe

Repo layout (engine + stories).

- engine/        Tools, workers, workflows, configs.
- stories/       One folder per story.
  - template/    Empty story template (copy or clone).

Story layout:
- Filmsets: `<chapter_label>_###/segment_###/scene_###/timeline_##/` (chapter_label defaults to `chapter`, template uses `story`).
- Subjects: `stories/<story>/subjects/` (registry, profiles, occurrences, asset_bible.json, ASSET_BIBLE.md).
  - Per-timeline subject roots live under `subjects/timelines/` by default and are created by `asset_bible_enricher.py`.
  - Default timeline root is `subjects/timelines/<timeline_label>_<tag>/` (tag defaults to `01`).
  - Override the root via `subject_dir_root` in `story_config.json` (use `{timeline_label}`, `{timeline_tag}`, `{timeline_folder}` tokens if you want interpolation).
  - Subject folders are the canonical home for assets, masks, LoRA training, and notes used when building start images and chapters.

Core data flow (minimal):
0. `setup_filmsets_from_geez.py` -> scaffold `filmsets/chapter_###/segment_###/scene_###/timeline_##/` from Ge'ez verse JSONL.
   - Run: `python engine/workers/setup_filmsets_from_geez.py --story-root stories/template --include-chapter-text`
   - Optional: run the Ge'ez linguistic analysis workers (Levels A-D) for graphematic/morphologic/synthactic/semantic-historical passes. See `docs/geez_analysis_methodology.md`.
   - The A-D workers wait for upstream outputs (B waits for A, C waits for B, D waits for C).
   - Use `--chapter-batch` to process one request per chapter and write per-segment outputs.
   - End-to-end pipeline runner: `README_pipeline.md`.
1. `worker_llm_analysis.py` -> analysis CSV at `analysis_progress_csv_path` (story_config).
   - Use `--use-gemini` to run via Gemini CLI (model from `--model` or `GEMINI_MODEL`).
   - Analysis JSON can include `blocking` anchors + paths when staging is implied.
2. `chapter_briefing_builder.py` -> chapter briefings for linguistics, tech hypotheses, and storytelling Q1/Q2/Q3.
   - Run: `python engine/workers/chapter_briefing_builder.py --story-config stories/template/config/story_config.json --use-gemini --model pro`
   - Use `pro`/`flash` or explicit `gemini-3-pro`/`gemini-3-flash`. `auto` skips `--model` (CLI default). `gemini_3_pro` is normalized to `gemini-3-pro`.
   - If Gemini fails, falls back to Copilot CLI (set `COPILOT_CMD`/`LLM_CMD` or install `copilot`). Copilot maps `gemini-3-pro` to `gemini-3-pro-preview`.
3. `analysis_master_builder.py` -> `data/analysis/analysis_master.jsonl`
4. `subject_registry_builder.py` -> subjects registry + profiles + occurrences + scenes
5. `asset_bible_builder.py` -> `subjects/asset_bible.json`
6. `asset_bible_enricher.py` -> `subjects/ASSET_BIBLE.md` + `subjects/asset_bible_cards.jsonl`
   - Uses analysis + screenplay snippets to generate dense prompt-ready asset cards for every subject.
   - Defaults to Ollama (`gpt-oss:20b`), or pass `--use-gemini` + `--model`.
   - If Gemini fails, falls back to Copilot CLI (set `COPILOT_CMD`/`LLM_CMD` or install `copilot`). Copilot maps `gemini-3-pro` to `gemini-3-pro-preview`.
   - Pulls story briefings from `story_config.json` (`briefings`), capped by `--briefing-max-chars`.
  - Writes per-subject folders under `subjects/timelines/<timeline_label>_<tag>/<id>/` with `card.md`, `card.json`, `images/`, and `states/`.
  - Each state can include `states/<state_id>/card.md`, `card.json`, and `prompt.txt` when phase prompts are generated.
   - Example: `python engine/workers/asset_bible_enricher.py --story-config stories/template/config/story_config.json --resume --timeline 1`
7. `scene_instruction_builder.py` -> `subjects/scene_instructions.jsonl` (REGIE_JSON extraction)
8. `scene_layout_builder.py` -> `subjects/timelines/<timeline_label>_<tag>/scene_layout.jsonl` (camera + blocking + anchor plan)
   - Example: `python engine/workers/scene_layout_builder.py --story-config stories/template/config/story_config.json --timeline timeline_01`
9. Preflight screenplays before layout (detect missing/invalid scene headers):
   - `python engine/workers/scene_preflight_check.py --story-config stories/template/config/story_config.json --output C:\temp\scene_preflight.json`
10. Optional: sanitize junk prefixes before preflight/regeneration:
   - `engine/scripts/run_screenplay_sanitizer.ps1 -StoryConfig stories/template/config/story_config.json -Start 1 -End 108`
11. Optional: fix malformed scene headers before preflight/regeneration:
   - `engine/scripts/run_scene_header_fixer.ps1 -StoryConfig stories/template/config/story_config.json -Start 1 -End 108`

Ge'ez subjects (optional):
- `engine/workers/subjects_from_geez.py` -> `subjects/subject_candidates_geez.json` + `subjects/subject_occurrences_geez.jsonl`
- Run: `python engine/workers/subjects_from_geez.py --story-root stories/template`

LoRA flow (template):
1. `lora_dynamic_queue_builder.py` -> `data/lora/lora_training_set.json` (metadata only).
2. `lora_index_builder.py` -> `subjects/lora_index.json`
3. `lora_pipeline_builder.py` -> `data/lora/lora_pipeline.jsonl`
   - Example: `python engine/workers/lora_dynamic_queue_builder.py --story-config stories/template/config/story_config.json --timeline 1`

Subject image queue (Asset Bible):
- `engine/workers/asset_bible_queue_builder.py` -> `data/queues/asset_bible_queue.json`
- Queue prompts use the full Asset Bible card markdown and emit one job per phase in the Evolution section
  (each prompt keeps only the matching phase bullet and drops the others).
- Output basenames are suffixed with `__phase_XX` when phases are detected.
- `engine/scripts/run_subject_image_queue.ps1` builds a combined queue for multiple workflows and can start ComfyUI + the orchestrator.

Direct actor sources:
- `lora_index.json` includes training image folders (`style_seed_dir`, `multiangle_dir`) so scenes can use a training cutout
  instead of a LoRA when it fits.

Queues and builders:
- Full queue map + producers/consumers: `docs/queues.md`.
- Primary timeline queues:
  - `subjects/actor_queue.jsonl` (iClone actor loading).
  - `data/lora/lora_training_set.json` (dynamic-only training metadata, generated by `lora_dynamic_queue_builder.py`).
- Legacy queue builders (`prepare_lora_queue.py`, `prepare_prop_queue.py`, `generate_lora_prompts.py`) still point at `C:\Users\sasch\henoch` and should be migrated before timeline-wide runs.

Dynamic subjects:
- All subjects are included in the registry. Dynamic ones are flagged and get per-segment or per-scene state slots.
- In the template, dynamic states are phase-based (static policy): 2-3 sequential changes per character.
- Control the phase cap per story via `dynamic_phase_max` in story_config (optional `dynamic_phase_labels` for naming).

Viewer:
- `engine/scripts/run_subjects_view.ps1` starts a local server and opens the subjects page.
- The viewer links to per-subject `images/asset_bible` folders and shows image previews when available.

Launchers:
- `engine/launchers/Start-Workspaces.ps1` lists/opens external workspaces and can run configured start commands.

Workspace registry:
- `engine/config/workspaces.json` tracks external Windows/WSL workspaces and entry points.
- `docs/workspaces.md` summarizes usage and notes.

Batch scripts:
- `engine/scripts/run_all_chapters.ps1` and `engine/scripts/run_all_chapters_gemini.ps1` support `-Resume` to skip chapters with an existing `DREHBUCH_HOLLYWOOD.md`.
  - Optional: `-Sanitize` trims junk prefixes after each chapter.
  - Optional: `-FixHeaders` normalizes malformed ACT/SCENE headers after each chapter.
- `engine/scripts/run_missing_chapters.ps1` regenerates chapters with missing/invalid scene headers (uses `scene_preflight_check.py`).
  - Example: `engine/scripts/run_missing_chapters.ps1 -StoryConfig stories/template/config/story_config.json -Start 1 -End 108 -DryRun`
  - Optional: `-SanitizeFirst` trims log/command garbage before preflight.
  - Optional: `-FixHeadersFirst` normalizes malformed ACT/SCENE headers before preflight.
  - Optional: `-RunRegieFix` runs `run_regie_fix.ps1` after regeneration.
- `engine/scripts/run_regie_fix.ps1` inserts missing REGIE_JSON blocks only (uses `regie_preflight_check.py`).
  - Example: `engine/scripts/run_regie_fix.ps1 -StoryConfig stories/template/config/story_config.json -Start 1 -End 108`
  - Report-only: `engine/scripts/run_regie_fix.ps1 -StoryConfig stories/template/config/story_config.json -Start 1 -End 108 -ReportOnly -ReportOutput C:\temp\regie_report.json`
- `engine/scripts/run_screenplay_sanitizer.ps1` trims junk prefixes in DREHBUCH files.
  - Example: `engine/scripts/run_screenplay_sanitizer.ps1 -StoryConfig stories/template/config/story_config.json -Start 1 -End 108 -DryRun`
- `engine/scripts/run_scene_header_fixer.ps1` normalizes malformed ACT/SCENE headers in DREHBUCH files.
  - Example: `engine/scripts/run_scene_header_fixer.ps1 -StoryConfig stories/template/config/story_config.json -Start 1 -End 108 -DryRun`

Reallusion library:
- `engine/workers/reallusion_library_indexer.py` indexes Reallusion assets (Motion Director, Motion Plus, iTalk, paths, terrains, ccAvatar/iAvatar).
- Defaults to `C:\Users\Public\Documents\Reallusion` (override with `--library-root` or `REALLUSION_LIBRARY_ROOT`).
- Output defaults to `<library-root>/reallusion_library_index.json`.

RLPy hidden API:
- The local `RLPy.py` files are the authoritative API surface for CC4/iClone.
- Use `engine/tools/rlpy_api_finder.py` for quick symbol searches.
- Notes and examples in `docs/rlpy_hidden_api.md`.
- Use `engine/tools/rlpy_wiki_compat.py` to compare a wiki HTML dump against `RLPy.py`
  (set `RL_WIKI_ROOT` or pass `--wiki-root`; see `docs/rlpy_hidden_api.md`).

CC4 vs iClone API overlap (quick rules):
- Scripts run inside the host app only; CC-only APIs are not available in iClone and vice versa.
- Shared surface: RLPy math/time, scene graph, content manager access, file I/O, cameras/lights, and animation primitives.
- CC-specific: Headshot, morph/skin authoring, wardrobe authoring, and `.ccAvatar` save workflows.
- iClone-specific: Motion Director, iTalk/viseme workflows, mocap device hooks, timeline playback/recording, and crowd-style assets.
- Crowds: iClone uses ActorCore Crowd `iAvatar` assets + Motion Director/path workflows; CC does not host crowd simulation. Use the Content Manager APIs to enumerate/load those assets and then drive them like standard iClone actors.

iClone bridge:
- Install the VisionExe OpenPlugin folder (`engine/iclone/openplugin/visionexe`) into iClone's OpenPlugin path and start the server from **Plugins > VisionExe > Open VisionExe Panel**.
- Refresh an existing install with `engine/launchers/Install-iCloneOpenPlugin.ps1 -Mode Copy -Force`.
- The panel includes **Find Actor**, **Scan Content**, and **Load Path** buttons for Content Manager + direct file debugging.
- `engine/workers/iclone_remote_client.py` sends actions (apply A2F JSON, export iTalk).
- `list_skeleton_bones` dumps bone names per skeleton method for debug.
- `load_actor_by_name` uses the Reallusion library index to load actors by asset name (e.g. `vx_henoch_p01`).
- Default index path comes from `reallusion_index_path` in `engine/iclone/openplugin/visionexe/iclone_config.json` (defaults to Public); override via `REALLUSION_INDEX_PATH`.
- Actor loading prefers iClone's Content Manager API (custom/template character roots) and falls back to the JSON index.
- Use `debug_actor_lookup` to see which source is resolving a name (see `docs/iclone_bridge.md`).
- Use `content_manager_scan` to enumerate CM folders/files when debugging missing actors (see `docs/iclone_bridge.md`).
- `engine/workers/iclone_lipsync_runner.py` runs a full audio->clip->iTalk pass (LoadVocal or A2F JSON).
- UI automation (viewport clicks/hotkeys) is disabled by default; enable `ui_automation.enabled` in `iclone_config.json` or set `ICLONE_UI_AUTOMATION=1`.
- Usage notes (including MD prop creation/triggering and UI injection) in `docs/iclone_bridge.md`.
- Motion Director 3-phase flow + recorder: `docs/motion_director_flow.md` and `engine/workers/md_record_sequence.py`.
- Plan runner: `engine/scripts/run_md_plan.ps1` (story-aware wrapper).

Character Creator (Headshot automation):
- Load `engine/character_creator/cc_file_watcher.py` via **Script > Load Python Script** (runs in CC4 main thread).
- Enqueue a headshot job from the CLI:
  - `python engine/workers/cc_headshot_enqueue.py "C:\path\to\photo.png" --mode auto --body-type female --save-name vx_actor_f01`
- The watcher uses the built-in `RHeadshot.CreateHeadFromPhoto` API and saves the avatar as `.ccAvatar` to the Custom folder.
- Command/response files live in `engine/character_creator/cc_command.json` and `engine/character_creator/cc_response.json`.

Actor loading:
- `engine/scripts/load_actors.ps1` loads actors by name or from `subjects/actor_queue.jsonl` via the iClone bridge (example: `engine/scripts/load_actors.ps1 -StoryConfig stories/template/config/story_config.json`).

Workflow catalog:
- `engine/config/workflow_catalog.json` lists agentic workflow mappings.
- `docs/workflows.md` summarizes workflow usage notes and view ordering.
- `engine/workers/comfy_orchestrator.py` resolves workflow IDs/labels from the catalog when you pass `--text-to-image` or `--image-to-image`.

Audio (STT):
- `engine/workers/stt_worker.py` transcribes audio with Whisper and reports similarity/WER when a reference text is provided.

Audio (Monologue/TTS):
- `engine/scripts/run_audio_agent.ps1` runs `audio_agent.py` across chapters; pass `-StoryConfig` to resolve `story_###` filmsets and use `-Tts -Force` for full regeneration.
- Narrator-only (no inner monologues):
  - `.\engine\scripts\run_audio_agent.ps1 -Start 1 -End 108 -StoryConfig stories\template\config\story_config.json -NoMonologue -Force`
- Narrator + planned inner monologues (uses MONOLOGUE_JSON only, skips missing entries):
  - `.\engine\scripts\run_audio_agent.ps1 -Start 1 -End 108 -StoryConfig stories\template\config\story_config.json -MonologueSource plan -MonologueOutput both -Force`
- Add `-Tts` to generate WAVs (TTS only runs when `-MonologueOutput` is `scene` or `both`).
- `engine/workers/voice_cast_builder.py` scans `DREHBUCH_HOLLYWOOD.md` for narrator/monologue/dialog speakers and writes `subjects/voice_cast.json` for voice mapping:
  - Adds Ge'ez/Latin suffix gender hints (defaults to unknown) and per-language speaker mix templates for TTS.
  - Default: pulls `[MASTER]` speakers from `GET http://localhost:8000/speakers` (override via `tts_speakers_endpoint` in `story_config.json`).
  - Optional: set `voice_mix_templates_path` in `story_config.json` to override the mix templates.
  - `python engine/workers/voice_cast_builder.py --story-config stories/template/config/story_config.json`
  - `audio_agent.py` currently uses narrator + monologue; dialog TTS is planned separately.
- Chatterbox queue API (default TTS backend):
  - Endpoint: `http://localhost:8000` (queue → result). Example:
    - `curl -X POST http://localhost:8000/queue -H "Content-Type: application/json" -d '{"text":"Hello mit Speaker","model":"mtl","speaker_id":"turbo-1704717234"}'`
    - `curl "http://localhost:8000/result/<job_id>"`
  - Docs: `\\wsl.localhost\\Ubuntu22Old\\home\\sasch\\chatterbox\\README_queue.md`
  - Speaker registry (master voices + mixes): `\\wsl.localhost\\Ubuntu22Old\\home\\sasch\\chatterbox\\data\\speakers\\registry.json`
  - Voice mixing for profiles: set `tts.speaker_mix` (or `tts.speaker_variation`) in `engine/config/audio_voice_profiles.json` with `speaker_id_1`, `speaker_id_2`, `ratio`, and optional `new_name`/`model`; the agent calls `/mix` and uses the returned `speaker_id` for TTS.

Video docking:
- `docs/video_docking.md` describes REGIE_JSON video_plan metadata and capture inputs.
- REGIE_JSON can include `start_image_keywords` to inject LoRA trigger words into start image prompts.
- LoRAs are injected as prompt tags (e.g. `<lora:folder/name.safetensors:0.8>`) by the chapter asset generators.
- Capture library lives under `stories/<story>/data/capture`.
- `engine/workers/capture_library_builder.py` indexes capture clips into `subjects/pose_library.json` and `subjects/viseme_library.json`.

Scene building:
- `docs/scene_building.md` captures the timeline-scoped subject library, start image flow, camera logic, and audio pipeline assumptions.

RAG (small):
- `engine/scripts/run_rag_small.ps1` indexes `<data_root>/raw` (from story_config) into Qdrant; override with `-Root` or `-StoryConfig`.

Pose extraction (BVH):
- `engine/workers/pose_bvh_importer.py` converts SAM3 BVH output into a pose JSON + mapping stub for CC4/iClone.
- The importer normalizes a `Hips` root to `Joint_000` so SAM3 mappings stay consistent.
- `apply_pose_json` will fall back to base bones if twist/share/eye/pelvis/toe/facial bones are missing on the target avatar.
- `engine/tools/blender_joint_mapper.py` can auto-build `sam3_bvh_to_cc4.json` from SAM3 + CC4 armatures in Blender.
- Apply poses in iClone via `apply_pose_json` (see `docs/iclone_bridge.md`).
- CC4 axis rotation offsets are pulled from `engine/config/pose_mappings/cc4_axis_rotation.json` unless overridden.
- `apply_pose_json` will also resolve raw BVH joints using the mapping path stored in the pose JSON.
- Use `save_pose_preset` to capture an avatar pose (quaternion) and `apply_pose_preset` to replay it (see `docs/iclone_bridge.md`).
