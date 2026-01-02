# LoRA Data

Drop or sync the LoRA JSON sources here, then build the index:

- `lora_training_set.json`
- `lora_training_queue.json`
- `lora_prop_queue.json`
- `lora_triggers.json`
- `lora_master_images.json`
- `lora_training_runs.jsonl`
- `lora_overrides.json`

Build commands (from repo root):
- `python engine/workers/lora_index_builder.py`
- `python engine/workers/lora_pipeline_builder.py`

Direct actor sources:
- Actor phases in `lora_index.json` expose `style_seed_dir` and `multiangle_dir`.
- Scene builders can choose an existing training image from those folders instead of using a LoRA.
