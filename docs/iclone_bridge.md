# iClone Remote Bridge

This bridge lets VisionExe talk to iClone through a lightweight local HTTP server
running inside iClone (RLPy). It is designed for batch A2F JSON import and iTalk
clip export.

## Start the server (inside iClone)

1. Install the VisionExe OpenPlugin folder:
   `engine/iclone/openplugin/visionexe` -> `C:\Program Files\Reallusion\iClone 8\Bin64\OpenPlugin\visionexe`.
   To refresh an existing install, run:
   `engine/launchers/Install-iCloneOpenPlugin.ps1 -Mode Copy -Force`.
2. Restart iClone.
3. Open **Plugins > VisionExe > Open VisionExe Panel** and click **Start Server**.
4. The server listens on `http://127.0.0.1:8123` by default.
5. The panel now includes **Find Actor**, **Scan Content**, and **Load Path** buttons for Content Manager + direct file debugging.

Environment overrides (optional):
- `ICLONE_REMOTE_HOST`
- `ICLONE_REMOTE_PORT`
- `ICLONE_CONFIG_PATH`

Config file (edit after install or override via `ICLONE_CONFIG_PATH`):
- `C:\Program Files\Reallusion\iClone 8\Bin64\OpenPlugin\visionexe\iclone_config.json`

UI automation (viewport clicks/keyboard injection) is disabled by default. Enable it in
`iclone_config.json` under `ui_automation.enabled` or set `ICLONE_UI_AUTOMATION=1`
before starting the server.

Reallusion index path (optional):
- `reallusion_index_path` defaults to `C:/Users/Public/Documents/Reallusion/reallusion_library_index.json`.
- Override via `REALLUSION_INDEX_PATH` or per-request `index_path`.

## Client usage

Send commands from VisionExe:

```powershell
python engine/workers/iclone_remote_client.py --action ping
python engine/workers/iclone_remote_client.py --action list_avatars
python engine/workers/iclone_remote_client.py --action list_cameras
python engine/workers/iclone_remote_client.py --action select_avatar --payload "{\"name\":\"Henoch\"}"
python engine/workers/iclone_remote_client.py --action select_camera --payload "{\"name\":\"Camera\"}"
```

List skeleton bones for the active avatar (debug missing names):

```powershell
python engine/workers/iclone_remote_client.py --action list_skeleton_bones --payload "{\"avatar_name\":\"vx_henoch_p01\"}"
```

Load a character by name (Reallusion library index):

```powershell
python engine/workers/reallusion_library_indexer.py
python engine/workers/iclone_remote_client.py --action load_actor_by_name --payload "{\"name\":\"vx_henoch_p01\"}"
```

Optional fields: `prefer` (`iavatar` or `ccavatar`), `index_path`, `library_root`,
`content_manager_first` (default true).
If the Content Manager lookup fails, the bridge falls back to the JSON index.
Disable CM lookup with `use_content_manager=false`.

Debug actor lookup:

```powershell
python engine/workers/iclone_remote_client.py --action debug_actor_lookup --payload "{\"name\":\"vx_henoch_p01\"}"
```

Returns index path + match plus Content Manager roots/match.

Content Manager scan (enumerate folders/files via the API):

```powershell
python engine/workers/iclone_remote_client.py --action content_manager_scan --payload "{\"root_key\":\"Character\",\"max_folders\":100,\"max_files\":200}"
```

Optional fields: `include_default`, `include_custom`, `root_key` (e.g. `Character`, `Props`, or full enum name).

Queue-based loading (subjects):

```powershell
engine/scripts/load_actors.ps1 -StoryConfig stories/template/config/story_config.json
```

Uses `subjects/actor_queue.jsonl` (fields: `name`, optional `prefer`).

Apply A2F JSON to the selected avatar:

```powershell
python engine/workers/iclone_remote_client.py --action apply_a2f_json --payload "{\"
  path\":\"C:/path/to/a2f_export_bsweight.json\",
  \"mapping_path\":\"C:/path/to/a2f_mapping.json\",
  \"key_step\":1,
  \"strength_scale\":1.0,
  \"start_seconds\":0.0,
  \"clip_name\":\"a2f_henoch_01\",
  \"use_mocap_order\":false
}"
```

Apply a pose JSON (from `pose_bvh_importer.py`) to the avatar:

```powershell
python engine/workers/iclone_remote_client.py --action apply_pose_json --payload "{\"
  \"pose_path\":\"C:/path/to/pose.json\",
  \"avatar_name\":\"vx_henoch_p01\",
  \"time_seconds\":0.0,
  \"clip_index\":0,
  \"apply_root_translation\":true
}\" 
```

Note: the pose mapping targets CC4 bone names (e.g. `CC_Base_Hip`). Update
`engine/config/pose_mappings/sam3_bvh_to_cc4.json` to match your skeleton. If a
mapped bone is missing (twist/share/eye/pelvis/toe/facial), the bridge falls back
to the closest base bone (e.g. `UpperarmTwist01` → `Upperarm`).
Axis rotation offsets are applied automatically from
`engine/config/pose_mappings/cc4_axis_rotation.json` (extracted from the CC4
default profile). You can override per call with `axis_rotation_path` or
inline `axis_rotation_map` in the payload.

If your pose JSON still contains raw BVH joint names, `apply_pose_json` will
auto-resolve using the mapping path embedded in the pose JSON (or `joint_map_path`
from the request).

Capture or save a pose preset (writes quaternion rotations for exact replay).
Defaults are body-only (face/eyes/tongue/toes disabled; twist enabled):

```powershell
$payload = @{
  avatar_name = "vx_henoch_p01"
  output_path = "C:/temp/henoch_pose_01.json"
  include_translation = $true
  bone_source = "animation"
  include_face = $false
  include_tongue = $false
  include_eyes = $false
} | ConvertTo-Json -Compress
python engine/workers/iclone_remote_client.py --action save_pose_preset --payload $payload
```

Apply a saved preset:

```powershell
$payload = @{
  avatar_name = "vx_henoch_p01"
  preset_path = "C:/temp/henoch_pose_01.json"
  time_seconds = 0.0
  clip_index = 0
  apply_root_translation = $true
} | ConvertTo-Json -Compress
python engine/workers/iclone_remote_client.py --action apply_pose_preset --payload $payload
```

If capture crashes, try `bone_source="animation"` and disable facial/tongue/eye/toe bones.

Load an audio file directly (uses iClone lip-sync backend):

```powershell
python engine/workers/iclone_remote_client.py --action load_vocal --payload "{\"
  audio_path\":\"C:/path/to/audio.wav\",
  \"clip_name\":\"henoch_line_01\"
}"
```

Export iTalk:

```powershell
python engine/workers/iclone_remote_client.py --action save_italk --payload "{\"
  output_path\":\"C:/path/to/output.italk\"
}"
```

Apply IK effector keys (foot/hand planting):

```powershell
python engine/workers/iclone_remote_client.py --action apply_ik_effector_keys --payload "{\"
  avatar_name\":\"Henoch\",
  \"effector\":\"LeftFoot\",
  \"keys\":[{\"time_seconds\":0.5,\"position\":{\"x\":0,\"y\":0,\"z\":10}}],
  \"bake_fk_to_ik\":true,
  \"bake_all\":false
}"
```

Apply camera keys (transform + focal length + DOF):

```powershell
python engine/workers/iclone_remote_client.py --action apply_camera_keys --payload "{\"
  camera_name\":\"Camera\",
  \"keys\":[
    {\"time_seconds\":0.0,
     \"transform\":{
        \"translation\":{\"x\":-75,\"y\":-150,\"z\":250},
        \"rotation\":{\"x\":0,\"y\":0,\"z\":0,\"w\":1},
        \"scale\":{\"x\":1,\"y\":1,\"z\":1}
     },
     \"focal_length\":35.0,
     \"dof\":{\"enable\":true,\"focus\":20,\"range\":80,\"transition_type\":\"linear\",\"transition_strength\":50}
    }
  ]
}"
```

### Avatar Placement

**`get_avatar_info`**

Fetch the current transform of an avatar.

```json
{
  "action": "get_avatar_info",
  "payload": {
    "avatar_name": "Henoch"
  }
}
```

**`set_avatar_transform`**

Set the avatar transform at the current time (or `time_seconds`).

```json
{
  "action": "set_avatar_transform",
  "payload": {
    "avatar_name": "Henoch",
    "time_seconds": 0.0,
    "position": { "x": 0, "y": 0, "z": 0 },
    "rotation": { "x": 0, "y": 0, "z": 0, "w": 1 },
    "scale": { "x": 1, "y": 1, "z": 1 }
  }
}
```

## Batch runner

```powershell
python engine/workers/iclone_lipsync_runner.py --audio C:/path/to/audio.wav --output C:/path/to/output.italk --avatar Henoch
```

## Motion Director probe

Use this to dump MD state and list MD props inside iClone. Set `MD_PROBE_RUN=1`
to attempt Begin/EndCommand overloads.

```powershell
# Run inside iClone's Python menu (env vars optional)
MD_PROBE_RUN=1 MD_PROBE_START=1 python engine/iclone/md_probe.py
```

You can also set these in `engine/iclone/iclone_config.json` under `md_probe`.

### Camera Control

**`get_camera_info`**

Retrieves current settings of a camera.

```json
{
  "action": "get_camera_info",
  "payload": {
    "camera_name": "Camera" // optional, defaults to current
  }
}
```

**`set_camera_params`**

Sets camera parameters directly.

```json
{
  "action": "set_camera_params",
  "payload": {
    "camera_name": "Camera",
    "near_plane": 5.0,
    "far_plane": 50000.0,
    "focal_length": 80.0,
    "dof": {
      "enable": true,
      "focus": 200.0,
      "range": 50.0
    }
  }
}
```

**`list_content`**

Dynamically indexes content (template/custom) via the remote server.

```json
{
  "action": "list_content",
  "payload": {
    "root_keys": ["MotionDirector", "Props"],
    "max_files": 100,
    "recursive": true
  }
}
```

## Content indexer

The content manager stores template/custom content in a database. Use the
indexer to resolve real file paths via content keys (e.g. MotionDirector).

Update `engine/iclone/iclone_config.json`:

```json
{
  "content_index": {
    "root_keys": ["MotionDirector", "MotionPath"],
    "include_default": true,
    "include_custom": true,
    "recursive": true,
    "output_path": "C:/temp/iclone_content_index.json"
  }
}
```

Run in iClone:

```powershell
python engine/iclone/content_indexer.py
```

## A2F JSON format

Expected fields (A2F export):
- `exportFps`
- `facsNames`
- `weightMat`

If expression names do not match iClone, pass a mapping JSON:

```json
{
  "A2F_NAME": "ICLONE_EXPRESSION_NAME"
}
```

If you are using mocap-ordered expression lists, set `use_mocap_order` to true.

## Notes

- Output should be iTalk to avoid collisions with body motion.
- You can throttle key density with `key_step` for large clips.
- Timing uses iClone FPS-aware conversions (`FrameTimeFromSecond`,
  `IndexedFrameTime`) to respect custom project FPS settings.

## Motion Director (remote)

Status/start/stop:

```powershell
python engine/workers/iclone_remote_client.py --action md_status
python engine/workers/iclone_remote_client.py --action md_start
python engine/workers/iclone_remote_client.py --action md_stop
```

List MD props:

```powershell
python engine/workers/iclone_remote_client.py --action list_md_props
```

Create or place an MD prop (Content Manager lookup + transform):

```powershell
$payload = @{
  name = "Actionable"
  position = @{ x = 0; y = 0; z = 0 }
} | ConvertTo-Json -Compress
python engine/workers/iclone_remote_client.py --action md_create_prop --payload $payload
```

Update an existing MD prop transform:

```powershell
$payload = @{
  name = "Actionable"
  position = @{ x = 0; y = 0; z = 50 }
} | ConvertTo-Json -Compress
python engine/workers/iclone_remote_client.py --action md_set_prop_transform --payload $payload
```

Begin + end command (target specific MD props by name/id):

```powershell
python engine/workers/iclone_remote_client.py --action md_begin_command --payload "{\"
  avatar_name\":\"CC3_Base_Plus\",
  \"record\":true,
  \"preserve_one_key\":false
}"

python engine/workers/iclone_remote_client.py --action md_end_command --payload "{\"
  avatar_name\":\"CC3_Base_Plus\",
  \"md_props\":[\"MDPropName\"]
}"
```

One-shot trigger (Begin + End):

```powershell
python engine/workers/iclone_remote_client.py --action md_trigger --payload "{\"
  avatar_name\":\"CC3_Base_Plus\",
  \"md_props\":[\"MDPropName\"],
  \"start_md\":true,
  \"record\":true
}"
```

UI injection (alt-click waypoints):

```powershell
python engine/workers/iclone_remote_client.py --action md_viewport_info
python engine/workers/iclone_remote_client.py --action md_viewport_candidates --payload "{\"limit\":25}"

python engine/workers/iclone_remote_client.py --action md_click_world --payload "{\"
  \"camera_name\":\"Camera\",
  \"world\":{\"x\":0,\"y\":-200,\"z\":0},
  \"button\":\"left\",
  \"modifiers\":[\"alt\"]
}"

python engine/workers/iclone_remote_client.py --action md_waypoints --payload "{\"
  \"camera_name\":\"Camera\",
  \"points\":[
    {\"x\":0,\"y\":-200,\"z\":0},
    {\"x\":50,\"y\":-300,\"z\":0}
  ],
  \"delay_ms\":200,
  \"start_md\":true,
  \"button\":\"left\",
  \"modifiers\":[\"alt\"]
}"

python engine/workers/iclone_remote_client.py --action md_click_screen --payload "{\"
  \"x\":0.5,
  \"y\":0.5,
  \"normalized\":true,
  \"button\":\"right\",
  \"modifiers\":[\"alt\"]
}"
```

Note: UI injection requires `ui_automation.enabled=true` in `iclone_config.json`.

Keyboard injection (MD hotkeys):

```powershell
python engine/workers/iclone_remote_client.py --action md_key --payload "{\"key\":\"F1\",\"start_md\":true}"
python engine/workers/iclone_remote_client.py --action md_key --payload "{\"key\":\"1\"}"
python engine/workers/iclone_remote_client.py --action md_key --payload "{\"keys\":[\"F2\",\"3\"],\"delay_ms\":150}"
```

Viewport selection hint (optional):

```json
{
  "viewport_hint": {
    "contains": "Viewport"
  }
}
```
