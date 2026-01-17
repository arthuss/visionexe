# Overview

This file is part of the Workspace Compendium build. The compendium is a
single-file export that consolidates structure, workflows, workers, scripts,
APIs, configs, and timeline logic into one Markdown document.

Regenerate:
`python engine/tools/build_workspace_compendium.py`

The build script merges:
- These section files in `docs/compendium_sections/`.
- Full snapshots of key docs and config files.
- Auto-generated inventories of workers, scripts, workflows, and configs.

Large binary assets (images, PDFs, and generated media) are not embedded. Their
locations are documented in the structure and inventory sections.
