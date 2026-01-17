# Structure Notes

Top-level layout:
- `engine/`: tools, workers, scripts, workflows, and configs.
- `stories/`: story data, templates, filmsets, and subject assets.
- `docs/`: long-form documentation, indices, and reference notes.
- Hard-state (append-only): `STATE.md`, `ARCHITECTURE.md`, `CONSTRAINTS.md`.

Story template core:
- `stories/template/config/`: timeline profiles + story_config.json.
- `stories/template/filmsets/`: chapter/segment/scene outputs.
- `stories/template/subjects/`: registry, profiles, asset bible, and timeline states.
- `stories/template/data/`: analysis, queues, and derived artifacts.

External workspaces:
- The registry is `engine/config/workspaces.json`.
- Use `engine/launchers/Start-Workspaces.ps1` to open or start them.
