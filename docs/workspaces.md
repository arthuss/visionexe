# Workspaces

This repo tracks external workspaces (Windows + WSL) that provide APIs or batch tooling.

Global notes:
- Start the workspace to expose its localhost API.
- GPU bound; run sequentially for max quality.
- Models auto-unload when idle to free VRAM.
- WSL router is required when calling WSL APIs from Windows.

Registry file: `engine/config/workspaces.json`

Launchers:
- `engine/launchers/Start-Workspaces.ps1` lists and opens workspace folders/READMEs and can run configured `start_command`.

Entries (high level):
- post_production: Post production stack on Windows (`C:\Users\sasch\post_production`).
  - tool: `C:\Users\sasch\post_production\depth\sam3_endpoint.py`
  - venv: `C:\Users\sasch\post_production\depth\.venv`
- qwen_image_to_lora: Qwen Image-to-LoRA workspace (WSL Ubuntu24Old).
  - venv: `\\wsl.localhost\Ubuntu24Old\root\Qwen-Image-to-LoRA\.venv`
  - start: `source .venv/bin/activate && python app.py --port 7860`
- comfyui_py314: ComfyUI Py314 workspace (WSL Ubuntu24Old).
  - conda: `py314`
  - start: `conda activate py314 && python main.py`
- diffusion_pipe: Batch dataset manager + SmoothMix generator (WSL Ubuntu24Old).
- liveportrait: LivePortrait driving-video avatar pipeline (WSL Ubuntu22Old).
- sadtalker: SadTalker audio-driven avatar pipeline (WSL Ubuntu22Old).
- wan2gp: Wan/Hunyuan video avatar workspace (WSL Ubuntu22Old).
- audiophil: AI music studio (WSL Ubuntu22Old).
- chatterbox: Chatterbox TTS + queue API (WSL Ubuntu22Old).
- chatterbox_turbo_demo: HF space demo for Chatterbox (WSL Ubuntu22Old).
- audio_editing: Audio FX overlay workflow (WSL Ubuntu22Old).
- tts_local: Local TTS/STT pipeline with Whisper.
  - stt_worker loads Whisper small/large, runs GPU transcription, and computes SequenceMatcher similarity + word-level WER.
  - README: `\\wsl.localhost\Ubuntu22Old\home\sasch\TTS\local_tts\README_audio_pipeline.md`

API endpoints:
- Each workspace may include an `apis` list (type + base_url + port) in `engine/config/workspaces.json`.
- Update ports there if you reassign default Gradio/FastAPI bindings.
