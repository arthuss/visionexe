# GEMINI

## Update Rules
- Primary instructions live in AGENTS.md; keep this file as a change log.
- Append a short note for every change that affects behavior, usage, or files.
- Keep entries brief: date/time, what changed, and why.

## Change Log
- ... (older entries preserved)
- 2026-01-05 04:00 - Character Creator (CC4) Integration:
    - NEW PLUGIN: `engine/character_creator/openplugin/visionexe_cc` (Safe Loader pattern).
    - NEW SERVER: `engine/character_creator/cc_remote_server.py` on port **8124**.
    - NEW ACTION: `save_character` in CC4 saves directly to Reallusion Custom Folder as `.ccAvatar`.
- 2026-01-05 04:05 - Content Manager Pipeline:
    - UPDATED INDEXER: `engine/workers/reallusion_library_indexer.py` now supports `.ccAvatar` and `.ccProject` with absolute path indexing.
    - UPDATED iCLONE SERVER: `engine/iclone/iclone_remote_server.py` now has `load_actor_by_name` action to load characters directly from the centralized index via name.
    - WORKFLOW: CC -> Save to Custom -> Index -> iClone Load by Name. No manual file management needed.
- 2026-01-05 04:15 - Headshot 2 Integration Plan:
    - CONCEPT: Automation of Headshot 2 via CC4 Python API (if exposed) or UI Injection.
    - GOAL: Input Image -> 4K 3D Avatar (Headshot v2 Pro).
    - VARIANTS: Male/Female, Child/Adult/Old.
    - WORKSPACE: Debug image placed at `engine/character_creator/ch019__actor_weane_00002_.png`.
    - STATUS: iClone actor loading confirmed working.
- 2026-01-05 04:42 - Added SAM3 BVH pose importer + CC4 mapping stub and documented pose extraction (engine/workers/pose_bvh_importer.py, engine/config/pose_mappings/sam3_bvh_to_cc4.json).
- 2026-01-05 04:46 - Logged batch status: chapter 1 Gemini run interrupted during concept generation; chapters 55-108 Gemini batch started (engine/scripts/run_all_chapters_gemini.ps1, engine/workers/drehbuch_gemini.py).
- 2026-01-05 04:49 - Added resume flag to chapter batch scripts; README notes the skip behavior (engine/scripts/run_all_chapters.ps1, engine/scripts/run_all_chapters_gemini.ps1, README.md).
- 2026-01-05 04:57 - Fixed missing segment_analysis_str in Gemini script structure prompt (engine/workers/drehbuch_gemini.py).
- 2026-01-05 05:08 - pose_bvh_importer now accepts directory paths for --library-out and writes pose_library.json automatically (engine/workers/pose_bvh_importer.py).
- 2026-01-05 05:43 - Added apply_pose_json (pose JSON -> iClone motion clip keys), mapped Hips to CC_Base_Hip, and documented usage (engine/iclone/iclone_remote_server.py, engine/config/pose_mappings/sam3_bvh_to_cc4.json, docs/iclone_bridge.md, README.md).
- 2026-01-05 07:07 - Parsed CC4 default avatar BoneAxisRotation into a reusable axis map and applied offsets during pose import; documented override flags (engine/config/pose_mappings/cc4_axis_rotation.json, engine/iclone/iclone_remote_server.py, docs/iclone_bridge.md, README.md).
- 2026-01-05 08:36 - apply_pose_json now resolves raw BVH joint names via the mapping path embedded in the pose JSON (engine/iclone/iclone_remote_server.py, docs/iclone_bridge.md, README.md).
- 2026-01-05 08:44 - Added apply_pose_json error wrapper to avoid remote disconnects (engine/iclone/iclone_remote_server.py).
- 2026-01-05 09:02 - VisionExe iClone menu plugin now requires `VISIONEXE_ENABLE_PLUGIN=1` to load, avoiding startup crashes; docs updated (engine/iclone/openplugin/visionexe/main.py, docs/iclone_bridge.md, README.md).
- 2026-01-05 09:09 - Updated Headshot inject template to dump Lua global API names to headshot_api_dump_inject.txt with event hooks; copy template into CCHeadshot Lua folders for execution (C:\Users\sasch\inject.lua).
- 2026-01-05 11:05 - Added Blender joint-mapper helper to generate SAM3->CC4 mapping JSON and noted it in README (C:\Users\sasch\visionexe\engine\tools\blender_joint_mapper.py, C:\Users\sasch\visionexe\README.md).
- 2026-01-05 11:32 - Created a CC BVH identity mapping and a test pose JSON from cctestbvh.bvh for direct CC_Base pose application (C:\Users\sasch\visionexe\engine\config\pose_mappings\cc_bvh_identity.json, C:\Users\sasch\visionexe\stories\template\data\capture\poses\vx_henoch_pose_cc.json).
- 2026-01-05 12:59 - Added rl_plugin_info headers to iClone script entrypoints to suppress compatibility warnings (C:\Users\sasch\visionexe\engine\iclone\iclone_remote_server.py, C:\Users\sasch\visionexe\engine\iclone\content_indexer.py, C:\Users\sasch\visionexe\engine\iclone\md_probe.py, C:\Users\sasch\visionexe\engine\iclone\md_setup_helper.py).
- 2026-01-05 13:26 - Consolidated iClone integration into a single VisionExe OpenPlugin with UI, added server stop support, and updated install/docs to use copy-based plugin deployment (C:\Users\sasch\visionexe\engine\iclone\openplugin\visionexe, C:\Users\sasch\visionexe\engine\iclone\iclone_remote_server.py, C:\Users\sasch\visionexe\engine\iclone\openplugin\README.md, C:\Users\sasch\visionexe\engine\launchers\Install-iCloneOpenPlugin.ps1, C:\Users\sasch\visionexe\docs\iclone_bridge.md, C:\Users\sasch\visionexe\README.md).
- 2026-01-05 13:35 - Guarded VisionExe panel status label against deleted Qt objects and reset dialog refs on destroy to avoid PySide2 QLabel errors (C:\Users\sasch\visionexe\engine\iclone\openplugin\visionexe\main.py).
- 2026-01-05 14:10 - Defaulted Reallusion index lookup to Public library path with config/env override and documented it (C:\Users\sasch\visionexe\engine\iclone\iclone_remote_server.py, C:\Users\sasch\visionexe\engine\iclone\iclone_config.py, C:\Users\sasch\visionexe\engine\iclone\iclone_config.json, C:\Users\sasch\visionexe\engine\iclone\openplugin\visionexe\iclone_config.json, C:\Users\sasch\visionexe\engine\iclone\openplugin\visionexe\iclone_config.py, C:\Users\sasch\visionexe\docs\iclone_bridge.md, C:\Users\sasch\visionexe\README.md).
- 2026-01-05 14:24 - Added Content Manager fallback for actor loading and documented it (C:\Users\sasch\visionexe\engine\iclone\iclone_remote_server.py, C:\Users\sasch\visionexe\engine\iclone\openplugin\visionexe\iclone_remote_server.py, C:\Users\sasch\visionexe\docs\iclone_bridge.md, C:\Users\sasch\visionexe\README.md).
- 2026-01-05 14:33 - Refreshed VisionExe panel status label handling and live status refresh on show/start/stop (C:\Users\sasch\visionexe\engine\iclone\openplugin\visionexe\main.py).
- 2026-01-05 14:40 - Switched actor loading to prefer Content Manager lookup with index fallback and documented the flag (C:\Users\sasch\visionexe\engine\iclone\iclone_remote_server.py, C:\Users\sasch\visionexe\engine\iclone\openplugin\visionexe\iclone_remote_server.py, C:\Users\sasch\visionexe\docs\iclone_bridge.md, C:\Users\sasch\visionexe\README.md).
- 2026-01-05 14:48 - Added debug_actor_lookup action to trace index vs Content Manager resolution (C:\Users\sasch\visionexe\engine\iclone\iclone_remote_server.py, C:\Users\sasch\visionexe\engine\iclone\openplugin\visionexe\iclone_remote_server.py, C:\Users\sasch\visionexe\docs\iclone_bridge.md, C:\Users\sasch\visionexe\README.md).
