# Video Docking and Capture Plan

This doc maps how scenes connect to the video pipeline and where
capture assets (phonemes/poses/reference footage) plug in.

Goals:
- Improve visual consistency and performance timing.
- Keep the pipeline explicit about what drives motion and overlays.
- Stay compliant with platform rules (no automation/evasion logic).

## Docking Points

1) Start Comp
- Builds the start frame (actor/env/props) used by video generation.
- Actor-first or env-first is declared in metadata.

2) Motion Driver
- A2F, pose clips, or other drivers are referenced in metadata.
- Sync is handled by the audio pipeline; drivers are just sources.

3) Video Synthesis
- Wan/Flux video generation uses start/end/keyframes.

4) Post Comp
- Relight, layered split, and overlays (badges/UI) are applied here.

## REGIE_JSON Extensions (video_plan)

Add these fields inside REGIE_JSON to guide the video pipeline.
Keep values short; use empty strings when unknown.

Example:
{
  "director_intent": "Short, poetic intent line for the scene.",
  "start_image_keywords": ["keyword1", "keyword2"],
  "video_plan": {
    "start_comp": {
      "mode": "actor_first|env_first|composite",
      "actor_pose_id": "POSE_032",
      "env_id": "ENV_SINAI_DUSK",
      "props": ["PROP_TABLET_01"],
      "notes": ""
    },
    "motion_driver": {
      "type": "a2f|pose|liveportrait|none",
      "audio_id": "scene_01_04_de",
      "pose_source": "data/capture/poses/pose_v1_032_fullbody.mp4",
      "driver_notes": ""
    },
    "reference_footage": {
      "id": "ref_desert_002",
      "path": "data/reference/ambient/desert_dusk.mp4",
      "use": "lighting|motion|palette|none",
      "notes": ""
    },
    "overlay_badge": {
      "asset": "media/badges/geez_logo_v1.mov",
      "blend": "screen|overlay|normal",
      "opacity": 0.25,
      "position": "top_right",
      "safe_margin": 0.04
    },
    "provenance": {
      "source": "ai_assisted|live_action|mixed",
      "notes": "internal tracking only"
    }
  }
}

Notes:
- director_intent should be a single, strong sentence (no tags).
- start_image_keywords are short prompt triggers for start image LoRAs.
- reference_footage is optional and should only guide lighting/motion.
- overlay_badge is for on-screen UI/branding elements.

## Capture Library

Put phoneme and pose clips in:
- stories/<story>/data/capture/phonemes/
- stories/<story>/data/capture/poses/

Each capture clip should be stable, short, and well-lit.
Use the same speaker for phoneme sets to keep consistency.

Index captures into subjects metadata:
- `python engine/workers/capture_library_builder.py --story-root stories/<story>`

## Sarah Chen Usage (Story + Brand)

Treat "Sarah Chen" as a narrative/brand layer:
- Register as a subject when needed (meta analyst/observer).
- Use in creator notes, teaser copy, or UI overlays.
- Avoid automation or mass outreach. Keep it human and compliant.
