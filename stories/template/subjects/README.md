
# Subjects

The asset bible lives here as JSON and is rendered by `index.html`.

Core files:

- registry.json: one entry per subject (all characters, props, environments, scenes).
- profiles.jsonl: detailed subject cards with dynamic state policy and states.
- occurrences.jsonl: where each subject appears (chapter/segment/scene).
- scenes.jsonl: parsed scene records from analysis blocks.
- environment_route.jsonl: linear environment route derived from scenes.
- lora_index.json: consolidated LoRA catalog (actors/props/set-envs).
- pose_library.json: indexed pose capture clips.
- viseme_library.json: indexed phoneme/viseme capture clips.
- scene_instructions.jsonl: regie-derived scene records with all REGIE_JSON fields, including video_plan metadata.

Build order:
- `engine/workers/subject_registry_builder.py` to generate registry/profiles/occurrences.
- `engine/workers/asset_bible_builder.py` to assemble asset_bible.json.
- `engine/workers/lora_index_builder.py` to assemble lora_index.json.
- `engine/workers/capture_library_builder.py` to index capture clips.
