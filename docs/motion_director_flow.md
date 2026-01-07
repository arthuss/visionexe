# Motion Director (3-Phase Flow)

This is the canonical Motion Director workflow for VisionExe. It keeps setup
clean, records motion to the timeline, and hands off to AI Render.

## Phase 1: Setup (per actor / per role)

Goal: prepare an actor so runtime is only triggers + waypoints.

1) Assign/prepare an IMD profile for the actor (Motion Director panel).
2) Map F1-F8 and 1-8 triggers to the desired behaviors (poses, emotes, loops).
3) Place MDProps if the behavior depends on them (Actionable/StateSwitch/etc.).
4) Save the actor preset in Content Manager so iClone can load by name.

Notes:
- IMD authoring is still UI-bound. Do it once per actor/role.
- Keep trigger slots consistent across actors so runtime automation is stable.

## Phase 2: Execute + record to timeline (per scene/take)

Goal: drive Motion Director while recording keys into the timeline.

Recommended automation:
- Start Motion Director.
- Begin a command with `record=true` (RBeginCommandOption.bRecord).
- Fire hotkeys (F1-F8 / 1-8) and/or set waypoints.
- End the command to commit keys to the timeline.

Example plan JSON (for `md_record_sequence.py`):

```json
{
  "avatar_name": "vx_henoch_p01",
  "record": true,
  "preserve_one_key": false,
  "start_md": true,
  "stop_md": false,
  "steps": [
    {"type": "key", "key": "F1"},
    {"type": "sleep", "seconds": 0.6},
    {
      "type": "waypoints",
      "camera_name": "Camera",
      "points": [{"x": 0, "y": -200, "z": 0}, {"x": 40, "y": -260, "z": 0}],
      "delay_ms": 200
    },
    {"type": "key", "key": "2"}
  ]
}
```

Run:

```powershell
python engine/workers/md_record_sequence.py --plan C:\temp\md_plan.json
```

If you need manual control, use the same steps with:
- `md_start`, `md_begin_command`, `md_key`, `md_waypoints`, `md_end_command`.

## Phase 3: AI Render (per scene/take)

Goal: render recorded motion through AI Render / Comfy workflows.

1) Export the take (iTalk / video frames).
2) Use the captured start frame + masks + LoRA prompts.
3) Run the compositing + relight + video workflows.

This keeps MD motion deterministic and lets AI Render focus on look/lighting.

## Related docs
- iClone bridge actions: `docs/iclone_bridge.md`
- Reallusion automation notes: `docs/reallusion_pipeline.md`
- Scene building assumptions: `docs/scene_building.md`
