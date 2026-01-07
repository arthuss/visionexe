# Reallusion Automation Notes (CC4 + iClone)

## Goals
- Zero-touch automation for large-scale scene counts.
- Prefer RLPy APIs over UI automation or Lua hooks.
- Content Manager is the source of truth (iClone sees CC4 assets immediately).

## Canonical Decisions
- CC4 headshot creation uses RLPy `RHeadshot.CreateHeadFromPhoto` (no Lua/UI injection).
- CC4 automation uses the file-watcher pattern for main-thread safety.
- CC4 saves to Reallusion Custom so iClone can load by name.
- iClone loads actors by name via the reallusion library index (`.ccAvatar` + `.iAvatar`).
- Motion Director control should use RLPy Manager/MDProp APIs where possible (avoid UI-only flows).
- Start images will be composed by a composition LLM (multi-image input), with pose extraction
  (OpenPose/BodyPoseNet/SAM3) used to align iClone placement.

## Snippets
### CC4 Headshot (file watcher)
1) In CC4: `Script -> Load Python Script` -> `engine/character_creator/cc_file_watcher.py`
2) CLI enqueue:
```
python engine/workers/cc_headshot_enqueue.py "C:\Users\sasch\visionexe\engine\character_creator\ch019__actor_weane_00002_.png" --mode auto --body-type female --save-name vx_henoch_test_01b
```
Notes:
- `--body-type` supports `male|female|baby|neutral|current`.
- Use morph sliders after to age characters (headshot has no "old" flag).

### Reallusion index + iClone load by name
```
python engine/workers/reallusion_library_indexer.py
python engine/workers/iclone_remote_client.py --action load_actor_by_name --payload "{\"name\":\"vx_henoch_p01\"}"
```

## References
- iClone bridge details: `docs/iclone_bridge.md`
- RLPy discovery notes: `docs/rlpy_hidden_api.md`
- Wiki vs RLPy checker: `engine/tools/rlpy_wiki_compat.py`

## Open Threads / Next Checks
- Map Motion Director manager commands into remote actions (prepare vs running).
- Build MDProp loading + trigger flows for waypoint/GoTo.
- Wire audio voice mapping to correct per-actor profiles.
