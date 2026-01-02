# Workflows

This repo keeps a lightweight workflow catalog for agentic selection and orchestration.

Catalog file: `engine/config/workflow_catalog.json`

Notes:
- Workflows are GPU bound; run sequentially for max quality.
- Multi-view outputs are intended for camera-angle shifts (e.g., 90-degree view) and branch points.
- Multi-view workflows expect `master_image` + `master_filename` inputs and run ~3 minutes including model load.
- Multi-view ordering (index 0..7): wide_shot -> 45_left -> 45_right -> low_angle -> 90_right -> aerial_view -> close_up -> 90_left.
- Each generated image should have a description captured at generation time.
- 6-keyframe workflow takes `start_frame`, `end_frame`, `frame_1..frame_5`, and `global_frame_count` (int). Optional prompts are `master_prompt_1..5`. Default `global_frame_count` is 81 for slow pans/hover; 25 works for fast motion. Output is 24 fps (duration = frames/24).
- `comfy_orchestrator.py` accepts workflow IDs/labels/paths from this catalog via `--text-to-image` and `--image-to-image`.

Current entries:
- multi_view_actor_8: 8-view actor angles (`engine/workflows/templates-1_click_multiple_character_angles-v1.0.json`).
- multi_view_env_8: 8-view scene angles (`engine/workflows/templates-1_click_multiple_scene_angles-v1.0.json`).
- view_shift_90: selection of the 90-degree view from a multi-view set (placeholder until a dedicated workflow exists).
- layered_image_edit: layered image split (`engine/workflows/image_qwen_image_layered.json`).
- relight_edit: relight edits (`engine/workflows/image_qwen_image_edit_2509_relight.json`).
- realism_edit: realism boost (`engine/workflows/REALISM-makes_anything_real.json`, image-only input).
- keyframes_6: 6 keyframes video guide (`engine/workflows/templates-6-key-frames.json`).

Add or update entries in the catalog as new workflow JSON files are added.

Atomic workflows:
- All workflow JSON files in `engine/workflows` are listed in the catalog with category `atomic` when no higher-level mapping exists.
- Fill in inputs/outputs for these atomic entries as you formalize their usage.
