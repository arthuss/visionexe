# Ge'ez Analysis Pipeline

This pipeline produces auditable, schema-validated JSON artifacts for Ge'ez text analysis.

Entry point
- `python engine/run_pipeline.py --input <file-or-dir> --outdir <outdir>`
- Default LLM: local Ollama. Use `--use-gemini` to switch to Gemini CLI.

Key options
- `--use-gemini` / `--model`: use Gemini CLI; otherwise Ollama.
- If `--use-gemini` and no `--model`, `GEMINI_MODEL` is used when set; otherwise the CLI default.
- `--translation-space`: generate translation variants mapped to parses + token options.
- `--window-tests`: run context invariance windows.
- `--back-translation`: run back-translation test (requires `--translation-space`).
- `--repro-runs N`: run reproducibility test with N runs.

Outputs
- `outdir/segments/seg_0001.json` (analysis artifact per segment)
- `outdir/reports/seg_0001_filter_report.json` (rule hits per segment)
- `outdir/reports/summary.json` + `outdir/reports/rule_hits.csv`

Schema
- `data/schemas/gez_morphology.schema.json`

Tagset + rules
- `engine/analysis/tagsets/gez_pos_1.json`
- `engine/analysis/rules/` (R1-R7)

Validation
- `python engine/run_pipeline.py --input <dir> --outdir <dir> --validate-only`
- `python engine/workers/worker_tests.py --input <dir> --outdir <dir> --validate`
