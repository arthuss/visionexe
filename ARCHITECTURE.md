# ARCHITECTURE

Append-only hard-state architecture notes. Do not rewrite; append new versions.

Codex may always read this file.

## Version 1 (2026-01-12 04:04)
- Entry points live under `engine/workers` and are invoked via CLI.
- A-D linguistic analysis is a strict pipeline (B waits for A, C for B, D for C).
- Per-segment analysis files are stored inside
  `stories/<story>/filmsets/<chapter_label>_###/segment_###/`.
- LLM backends used by analysis workers: local Ollama, Gemini CLI, or Vertex AI
  (ADC over HTTPS).

## Version 2 (2026-01-12 06:25)
- The analysis orchestrator reads `analysis_orchestrator_control.json` and can run
  serial or pipeline-parallel scheduling depending on `mode`.
- Pipeline-parallel runs use chapter-level gating between stages (G -> M -> S -> H -> L)
  and a global slot cap for concurrent API calls.
