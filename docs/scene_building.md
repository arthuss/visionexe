# Scene Building and Production Flow

This doc captures the production assumptions for Exeget:OS so the agent
does not drift and the pipeline stays consistent.

## 1) Timeline-first subject library

- Each story has timelines. Subjects are timeline-scoped.
- The subject library stores *all* subjects (actors, props, environments,
  set environments, scenes). Dynamic subjects are flagged, not excluded.
- Dynamic subjects need LoRA training, multi-masking, and pose sets.
- Non-dynamic subjects still get reference images to define their look,
  but do not require LoRA training (use img2img or cutouts).

Suggested structure (timeline-scoped):

stories/<story>/subjects/timeline_##/library/<SUBJECT_ID>/
  images/raw/
  images/cutouts/
  prompts/
  training/style_seed/
  training/multiangle/

## 2) Analysis -> RAG -> Drehbuch

- Do not filter early extraction. Capture *everything* so later steps can
  decide what is needed.
- A verse (or segment) is the atomic unit for evaluation and scene health.
- Each verse should be treated as a 3-act unit (setup, turn, resolve) and
  must have assets + regie + audio planned.
- Drehbuch writes REGIE_JSON directly; regie_worker is optional/legacy.
- Audio follows after Drehbuch so prompts and intent already exist.

## 2.1) Timeline backstory and world model

- Timelines encode interpretation models (3-5 variants).
- Each timeline is a full production universe (regie, audio, backstory).
- Store timeline briefings and backstory notes under:
  stories/<story>/timelines/<timeline_id>/briefings/
- Index timeline briefings into the timeline RAG profile so the Drehbuch
  agent can pull the correct worldview for that timeline.

## 2.2) RAG extraction rules

- RAG is the primary retrieval tool for analysis and backstory.
- Query by timeline first, then by verse/segment.
- Feed RAG results into director_intent and prompt seeds, not only tags.
- Keep raw extraction wide, filter only at generation time.

## 3) Start image production (most time-consuming)

Goal: a perfect start image for every requested scene.

- Dynamic subjects: generate 20+ variations for LoRA training (style seed
  -> multiangle -> base).
- Non-dynamic subjects: generate minimal reference images + masks.
- Start image is the anchor for all downstream video.

## 3.1) LoRA shooting order (dynamic subjects)

1) Generate style seeds (20+).
2) Train style LoRA.
3) Generate multiangle set (30-50).
4) Train base identity LoRA.
5) Store all outputs in the subject library for reuse.

Non-dynamic subjects: generate reference images + masks only.

## 4) Camera logic and filming

- Clips are produced in ~5 second chunks and then cut.
- Realistic camera switches can be done by:
  - taking the current frame
  - using the multi-angle workflow to rotate yaw (-90..+90), plus vertical
    offsets (up/down) and distance (wide/close)
  - using the new angle as the next start image
- This creates natural cut transitions without re-rolling the scene.
- The Drehbuch agent must be told these regie tools explicitly.

## 5) Audio pipeline (no gaps)

- TTS: Chatterbox (multi-actor training supported).
- Music: MusicGen + Magnet.
- Foley base: Hunyuan Foley per clip.
- Detail FX: audioEditing workspace plus zeta_worker for small overlays (example: crickets).
- Mix logic must respect: dialogue vs message vs internal monologue.
 - Music planning is handled by the Drehbuch agent (multi-pass per chapter).

## 5.1) Multi-language audio

- Minimum per timeline: DE + EN.
- Generate TTS per language and keep separate tracks.
- Use STT alignment when needed to sync timings across languages.

## 5.2) Music cues (scripted)

- The Drehbuch agent writes music cues during its multi-pass planning.
- Cues should specify type, intensity, length, and MusicGen/Magnet prompts.

## 6) Task planning (future)

Once the above is stable, add a task planner for the execution agent so
scene building and training steps become fully agentic and repeatable.
