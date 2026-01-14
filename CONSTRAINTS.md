# CONSTRAINTS

Append-only hard-state constraints. Do not rewrite; append new versions.

Codex may always read this file.

## Version 1 (2026-01-12 04:04)
- Keep analysis layers separated (graphematic, morphologic, synthactic,
  semantic-historical); do not collapse levels.
- Maintain graphematic fidelity: no silent normalization or token merging.
- Prefer deterministic, reproducible outputs; log model + parameters.
- Modify `engine/workers/worker_llm_analysis.py` only when explicitly requested.
- Do not rewrite STATE/ARCHITECTURE/CONSTRAINTS; append with version headers.

## Version 2 (2026-01-12 06:25)
- Reference lists moved to `REFERENCES.md` to keep constraints concise.

