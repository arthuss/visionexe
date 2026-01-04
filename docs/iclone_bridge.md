# iClone Remote Bridge

This bridge lets VisionExe talk to iClone through a lightweight local HTTP server
running inside iClone (RLPy). It is designed for batch A2F JSON import and iTalk
clip export.

## Start the server (inside iClone)

1. Open iClone.
2. Run the script: `engine/iclone/iclone_remote_server.py` via the iClone Python
   script menu.
3. The server listens on `http://127.0.0.1:8123` by default.

Environment overrides (optional):
- `ICLONE_REMOTE_HOST`
- `ICLONE_REMOTE_PORT`
- `ICLONE_CONFIG_PATH`

Config file (recommended for iClone scripts, since no CLI args):
- `engine/iclone/iclone_config.json`

## OpenPlugin wrappers

If you want menu entries instead of browsing for scripts, use the wrappers in:
`engine/iclone/openplugin/`. See `engine/iclone/openplugin/README.md` for the
one-time setup.

Quick install helper:

```powershell
engine\launchers\Install-iCloneOpenPlugin.ps1
```

## Client usage

Send commands from VisionExe:

```powershell
python engine/workers/iclone_remote_client.py --action ping
python engine/workers/iclone_remote_client.py --action list_avatars
python engine/workers/iclone_remote_client.py --action list_cameras
python engine/workers/iclone_remote_client.py --action select_avatar --payload "{\"name\":\"Henoch\"}"
python engine/workers/iclone_remote_client.py --action select_camera --payload "{\"name\":\"Camera\"}"
```

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
