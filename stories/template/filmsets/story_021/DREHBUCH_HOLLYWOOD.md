# DREHBUCH KAPITEL 21 - PRODUCTION READY

## CHAPTER NARRATION
NARRATOR_TEXT: Ich fiel nicht durch den Raum, sondern durch die Logik selbst. Wo die Gesetze enden, beginnt kein Chaos, sondern eine Leere, die schlimmer ist als der Tod. Hier ist der Code nicht geschrieben, hier ist er vergessen.

## [ACT 1] [SCENE 1.1] [Timecode: 00:00-00:05] [HOOK/INGRESS]
**Action:** The screen is black. Sudden, violent cut to Enoch stumbling forward. He doesn't step on ground, but on a "Mirror Plane" that reflects nothing. The environment is absolute void #000000. No stars, no horizon.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "wide", "framing": "wide", "environment": "Null Void Mirror Plane", "env_change": true, "actors": [{"name": "Henoch", "phase": "Voyager", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "14mm Fish-Eye / Chaotic Tracking", "mood": ["disorientation", "shock"], "director_intent": "Capture the violence of entering a null-space where physics are barely emulated.", "start_image_keywords": ["mirror plane", "void", "silver skin"], "start_image_mode": "actor_in_env", "video_plan": {"start_comp": {"mode": "actor_in_env", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
A cinematic wide shot in vertical 9:16. Enoch, with metallic silver skin and a flickering high-tech visor, stumbles forward onto a perfectly reflective floor that extends infinitely into absolute blackness. There is no horizon line. The lighting is stark and unnatural, appearing to come from nowhere, casting sharp, conflicting shadows. Enoch's robes are "liquid linen," frozen in a digital ripple. The aesthetic is industrial mysticism meets system crash. High contrast, photorealistic, 8k.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Actor:** Henoch (Voyager Phase). **Physique:** Lean, silver-skinned. **Skin-Shader:** `CHROME_MATTE` with digital noise grain. **Expression:** Shock, unbalanced.

**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**Garment:** `LIQUID_LINEN` robes, white/grey. **Prop:** None. **VFX:** "Plug-pull" distortion effect on entry.

**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** The Null Void. **Architecture:** Infinite mirror plane floor. **Atmosphere:** Vacuum. **Background:** Absolute #000000 black.

**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting Scheme:** `DEBUG_LIGHT`. Flat, harsh white light with no source. **Palette:** Black, Silver, Stark White.

**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** Handheld, low angle, fish-eye distortion. **Lens:** 14mm. **Focus:** Deep. **Style:** High-speed impact, 9:16 vertical.

### 3. AUDIO PROMPT (Hunyuan/Foley)
A violent "plug-pull" sound, like a massive cable being disconnected. Followed by a high-pitch capacitor whine that cuts to near silence. Footsteps sound like tapping on glass.

## [ACT 1] [SCENE 1.2] [Timecode: 00:05-00:09] [POV ENOCH]
**Action:** POV Enoch. The HUD boots up, cycles through ISOs, then crashes red: NULL_REFERENCE. He looks at his hands; the texture on his fingers is vibrating, detaching slightly from the mesh.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "interface", "shot_type": "close_up", "framing": "extreme_close_up", "environment": "Null Void", "env_change": false, "actors": [{"name": "Henoch", "phase": "Voyager", "presence": "on_screen", "focus": "primary"}], "props": ["HUD Visor"], "camera": "POV / Macro 85mm", "mood": ["glitch", "panic"], "director_intent": "Show the degradation of the user's avatar in this unallocated space.", "start_image_keywords": ["HUD crash", "glitching hands", "wireframe"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 5}
### 1. START IMAGE PROMPT (Midjourney/Flux)
A first-person POV shot in vertical 9:16. Looking at Enoch's own silver hands. The skin texture is vibrating and detaching from the underlying wireframe mesh on the fingertips. A digital HUD overlay covers the vision, displaying "ISO SEARCH" cycling rapidly before flashing a red "NULL_REFERENCE" error. The background is pitch black. The hands are illuminated by the red light of the crashing UI.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Actor:** Henoch (Hands only). **Physique:** Silver skin. **Skin-Shader:** `TEXTURE_FAIL`. Vibrating, transparency artifacts.

**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**Garment:** Sleeves of linen robes. **Prop:** HUD Overlay (VFX). **VFX:** Z-fighting on fingers, red error text.

**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Null Void. **Background:** Black.

**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting Scheme:** `UI_GLOW`. Illuminated by the red HUD interface. **Palette:** Red, Silver, Black.

**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** POV, shaky breathing movement. **Lens:** 35mm. **Focus:** Searching/Hunting. **Style:** Simulation horror, 9:16 vertical.

### 3. AUDIO PROMPT (Hunyuan/Foley)
The sound of a hard drive "Click of Death". A 60Hz ground loop hum starts low and rises. Digital error beeps.

## [ACT 1] [SCENE 1.3] [Timecode: 00:09-00:15] [REVEAL]
**Action:** In the distance, the SEVEN STARS appear. They are not burning balls of gas, but terrifying masses of "Corrupted Texture" (screaming faces, molten gold, static noise) held in place by red laser-grids.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "extreme_wide", "framing": "extreme_wide", "environment": "Null Void", "env_change": false, "actors": [], "props": ["Seven Stars", "Laser Grids"], "camera": "50mm / Rack Focus", "mood": ["terror", "awe"], "director_intent": "Reveal the monstrosity of the rogue processes.", "start_image_keywords": ["corrupted stars", "laser cage", "glitch texture"], "start_image_mode": "env_only", "video_plan": {"start_comp": {"mode": "env_only", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
An extreme wide shot in vertical 9:16 showing seven massive, distinct entities floating in the void. They are the "Stars," but they look like spheres of corrupted data: one is a mass of screaming stone faces, another is molten gold mixed with static noise, another is a checkerboard of pink/black missing textures. Each is wrapped in a tight, glowing red laser grid that cuts into their form. They pulse rhythmically.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Actor:** None. **Subject:** The Seven Transgressors. **Appearance:** 200m spheres of `CORRUPTED_ASSETS`.

**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**Prop:** `LASER_CAGE`. Red vector lines. **VFX:** Glitch artifacts, pixel sorting emissions.

**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Null Void. **Background:** Infinite black with faint green debug grid lines in far distance.

**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting Scheme:** `SELF_EMISSION`. Light comes from the corrupted textures. **Palette:** Error Pink, Gold, Red, Black.

**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** Slow push in. **Lens:** 50mm. **Focus:** Racking from void to stars. **Style:** Cosmic horror, datamosh, 9:16 vertical.

### 3. AUDIO PROMPT (Hunyuan/Foley)
A chaotic mix of sounds: distorted choral screaming time-stretched by 800%, mixed with heavy electrical arcing.

## [ACT 1] [SCENE 1.4] [Timecode: 00:15-00:20] [REACTION]
**Action:** Enoch recoils. The light from the stars is "wrong"—it casts shadows that don't match the geometry. He tries to shield his face, but his arm "clips" through his own chest (No collision).
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "medium", "framing": "medium", "environment": "Null Void", "env_change": false, "actors": [{"name": "Henoch", "phase": "Voyager", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "35mm Handheld / Shaky", "mood": ["pain", "glitch"], "director_intent": "Demonstrate the breakdown of the protagonist's physics model.", "start_image_keywords": ["clipping geometry", "wrong shadows", "silver skin"], "start_image_mode": "actor_in_env", "video_plan": {"start_comp": {"mode": "actor_in_env", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 8}
### 1. START IMAGE PROMPT (Midjourney/Flux)
A medium shot of Enoch in vertical 9:16. He is recoiling in fear. His arm is raised to shield his eyes, but the forearm is physically clipping through his chest plate, merging geometries. The shadows on his silver skin fall in the wrong direction compared to the light source. His face is distorted by a "texture smear" artifact.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Actor:** Henoch (Voyager). **Physique:** Silver skin. **Skin-Shader:** `SHADOW_ERROR`. Shadows detach from objects. **Expression:** Terror.

**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**Garment:** Robes. **VFX:** Geometry clipping (arm through chest), texture smearing.

**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Null Void. **Background:** Out of focus corrupted stars.

**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting Scheme:** `BROKEN_RAYTRACE`. Shadows point towards light sources. **Palette:** Silver, Black, Weird highlights.

**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** Handheld, panic. **Lens:** 35mm. **Focus:** Erratic. **Style:** Glitch aesthetic, body horror, 9:16 vertical.

### 3. AUDIO PROMPT (Hunyuan/Foley)
A sharp digital tearing sound. Heavy, hyper-ventilating breathing.

## [ACT 2] [SCENE 2.1] [Timecode: 00:20-00:28] [URIEL SPAWN]
**Action:** Uriel manifests not with a fade, but a single-frame "Pop-in". He stands perfectly still, a chrome tower of stability amidst the glitch. He points a finger at the stars.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "full_body", "framing": "wide", "environment": "Null Void", "env_change": false, "actors": [{"name": "Uriel", "phase": "Admin", "presence": "on_screen", "focus": "primary"}, {"name": "Henoch", "phase": "Voyager", "presence": "on_screen", "focus": "secondary"}], "props": ["Uriel Armor"], "camera": "24mm Wide / Low Angle", "mood": ["authority", "stability"], "director_intent": "Introduce the admin as the only stable element in the scene.", "start_image_keywords": ["Uriel spawn", "chrome armor", "pointing"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
A low-angle wide shot in vertical 9:16. Uriel stands towering next to a cowering Enoch. Uriel is a perfect chrome humanoid, reflecting the void with zero distortion. His armor is matte white and gold geometric plating. He points calmly at the stars. He looks "rendered" at a much higher resolution than everything else. Enoch looks grainy and glitchy by comparison.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Actor A:** Uriel (Admin). **Actor B:** Henoch (Voyager). **Physique:** Uriel 2.5m tall. **Skin-Shader:** Uriel `PERFECT_MIRROR`. Enoch `NOISY_SILVER`.

**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**Garment:** Uriel `FIREWALL_ROBES`. **Prop:** None.

**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Null Void. **Background:** Black.

**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting Scheme:** `LOCAL_STABILITY`. Uriel is lit by a soft divine studio light; Enoch is lit by harsh error lights. **Palette:** Chrome, White, Gold, Silver.

**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** Slow push in. **Lens:** 24mm. **Focus:** Sharp on Uriel. **Style:** Contrast between order and chaos, 9:16 vertical.

### 3. AUDIO PROMPT (Hunyuan/Foley)
A heavy sub-bass "Thud" on arrival. Then, absolute sterile room-tone silence around Uriel, contrasting the noise of the void.

## [ACT 2] [SCENE 2.2] [Timecode: 00:28-00:34] [THE STAR CAGE]
**Action:** Close-up on one of the stars. The red laser-grids are burning into the surface. The "fire" is spectral—colors shifting rapidly (Purple -> Green -> Negative). It looks like a suffering organism.
**Dialog:** Uriel: "Das sind die Fehler im System."



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "prop", "shot_type": "close_up", "framing": "close_up", "environment": "Null Void", "env_change": false, "actors": [], "props": ["Dyson Sphere", "Laser Grid"], "camera": "100mm Telephoto", "mood": ["torture", "containment"], "director_intent": "Show the suffering of the imprisoned entities.", "start_image_keywords": ["burning surface", "spectral fire", "laser burn"], "start_image_mode": "prop_only", "video_plan": {"start_comp": {"mode": "prop_only", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 7}
### 1. START IMAGE PROMPT (Midjourney/Flux)
A telephoto close-up of a star's surface in vertical 9:16. The surface is not rock, but "flesh-like" digital noise, cycling through purple, green, and negative colors. Thick red laser beams are physically digging into the surface, creating trenches of molten white pixels. It looks like a branding iron on skin.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Actor:** None. **Subject:** Corrupted Star Surface.

**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**Prop:** `LASER_GRID`. Burning effect. **VFX:** Color cycling (spectral noise), smoke made of pixels.

**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Null Void. **Background:** Black.

**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting Scheme:** `SPECTRAL_BURN`. Light shifts color rapidly. **Palette:** Neon Purple, Green, Red.

**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** Static, observing. **Lens:** 100mm. **Focus:** Shallow depth of field. **Style:** Abstract horror, 9:16 vertical.

### 3. AUDIO PROMPT (Hunyuan/Foley)
The sound of electrical arcing and welding. Deep, groaning modulation.

## [ACT 2] [SCENE 2.3] [Timecode: 00:34-00:42] [THE ABYSS]
**Action:** Cut to the floor. The ground ends in a sharp, jagged tear. Below is the KERNEL DUMP. Vertical waterfalls of blue "Cold Data" plasma crashing endlessly downward. It looks like the inside of a reactor.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "extreme_wide", "framing": "extreme_wide", "environment": "The Abyss", "env_change": true, "actors": [], "props": ["Data Waterfall"], "camera": "Crane Shot / Tilting Down", "mood": ["vertigo", "scale"], "director_intent": "Reveal the infinite drop of the data dump.", "start_image_keywords": ["blue plasma waterfall", "infinite drop", "jagged edge"], "start_image_mode": "env_only", "video_plan": {"start_comp": {"mode": "env_only", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
A high-angle crane shot in vertical 9:16 looking over a jagged, pixelated cliff edge. Below, endless vertical columns of blue "cold fire" (binary data streams visualized as plasma) crash downwards into an infinite abyss. The scale is monumental. The light from the blue plasma is blindingly bright and cold.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Actor:** None. **Subject:** The Kernel Dump Waterfall.

**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**Prop:** `DATA_STREAM`. Blue liquid light. **VFX:** Matrix-like falling code textures in the fire.

**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** The Abyss. **Architecture:** Broken floor geometry. **Background:** Infinite depth.

**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting Scheme:** `REACTOR_BLUE`. Intense cyan/blue glow. **Palette:** Cyan, Blue, Black.

**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** Crane tilt down. **Lens:** 14mm. **Focus:** Infinity. **Style:** Sci-fi epic, 9:16 vertical.

### 3. AUDIO PROMPT (Hunyuan/Foley)
A roaring waterfall sound, but synthetic—like a billion voices whispering at once mixed with white noise.

## [ACT 2] [SCENE 2.4] [Timecode: 00:42-00:50] [ENOCH'S TERROR]
**Action:** Enoch looks into the abyss. The blue light over-exposes his face, bleaching out his features. He screams, but the sound is desynced from his lips (Latency).
**Dialog:** Enoch: "Es ist... zu hell."



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "close_up", "framing": "extreme_close_up", "environment": "The Abyss", "env_change": false, "actors": [{"name": "Henoch", "phase": "Voyager", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "ECU / Macro", "mood": ["overload", "blindness"], "director_intent": "The data intensity wipes out the avatar's ability to perceive.", "start_image_keywords": ["overexposed face", "blue reflection eye", "scream"], "start_image_mode": "actor_in_env", "video_plan": {"start_comp": {"mode": "actor_in_env", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 5}
### 1. START IMAGE PROMPT (Midjourney/Flux)
An extreme close-up of Enoch's eyes in vertical 9:16. The pupils are dilated. The reflection of the blue abyss fills the iris. The lighting is blown out (overexposed), washing out the silver texture of his skin into pure white. His mouth is open in a scream.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Actor:** Henoch (Voyager). **Physique:** Face only. **Skin-Shader:** `BLOWN_HIGHLIGHTS`. **Expression:** Screaming.

**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**Prop:** None. **VFX:** Lens flare, sensor bloom.

**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Edge of Abyss. **Background:** Blinding blue.

**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting Scheme:** `OVEREXPOSURE`. Extreme blue light. **Palette:** White, Cyan.

**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** Static ECU. **Lens:** 100mm Macro. **Focus:** Eye. **Style:** Psychological horror, 9:16 vertical.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Audio buffer stutter on the scream (repeating "Wh-Wh-What-at"). High pitched sensor clipping noise.

## [ACT 3] [SCENE 3.1] [Timecode: 00:50-00:56] [URIEL'S STATEMENT]
**Action:** Uriel leans in. His face-plate reflects the burning stars. He speaks the verdict. The text "PRISON_FOREVER" scrolls across his visor in Ge'ez characters.
**Dialog:** Uriel: "Hier endet ihre Laufzeit. Für immer."



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "close_up", "framing": "close_up", "environment": "The Abyss", "env_change": false, "actors": [{"name": "Uriel", "phase": "Admin", "presence": "on_screen", "focus": "primary"}], "props": ["Visor Text"], "camera": "50mm / Stable", "mood": ["finality", "judgment"], "director_intent": "Deliver the final judgment through the interface.", "start_image_keywords": ["Uriel visor", "scrolling text", "reflection"], "start_image_mode": "actor_only", "video_plan": {"start_comp": {"mode": "actor_only", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 7}
### 1. START IMAGE PROMPT (Midjourney/Flux)
A close-up of Uriel's golden face-plate in vertical 9:16. The surface is perfect mirror chrome. Reflected in it are the chaotic burning stars and the blue abyss. Overlaying the reflection, bright red Ge'ez text scrolls across the visor surface: "PRISON_FOREVER". The framing is symmetrical and divine.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Actor:** Uriel (Admin). **Physique:** Golden mask. **Skin-Shader:** `CHROME_GOLD`.

**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**Garment:** Cowl. **Prop:** `HUD_TEXT`. Red scrolling glyphs.

**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Abyss Edge. **Background:** Out of focus blue fire.

**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting Scheme:** `FACE_GLOW`. Red text light on gold. **Palette:** Gold, Red, Blue reflection.

**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** Stable tripod. **Lens:** 50mm. **Focus:** Visor surface. **Style:** High-tech divinity, 9:16 vertical.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Reverb-heavy voice, clear and dry. Subtle scrolling text sound.

## [ACT 3] [SCENE 3.2] [Timecode: 00:56-01:04] [THE WARNING]
**Action:** Wide shot. Enoch and Uriel silhouetted against the massive, terrifying scale of the bound stars and the data-fall. The red laser-grids pulse once in unison.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "mixed", "shot_type": "extreme_wide", "framing": "extreme_wide", "environment": "The Abyss", "env_change": false, "actors": [{"name": "Henoch", "phase": "Voyager", "presence": "on_screen", "focus": "secondary"}, {"name": "Uriel", "phase": "Admin", "presence": "on_screen", "focus": "secondary"}], "props": ["Seven Stars", "Data Waterfall"], "camera": "14mm Ultra-Wide / High Angle", "mood": ["epic", "insignificance"], "director_intent": "Show the characters dwarfed by the system's prison mechanism.", "start_image_keywords": ["silhouettes", "massive scale", "pulsing lasers"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
An ultra-wide high-angle shot in vertical 9:16. Two tiny silhouettes (Enoch and Uriel) stand on a precipice. In front of them hangs the immense scale of the Seven Corrupted Stars and the infinite blue waterfall of the Abyss. The red laser grids on all seven stars pulse bright red simultaneously, lighting up the void for a split second.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Actor:** Uriel & Henoch (Silhouettes). **Physique:** Small scale.

**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**Prop:** Stars, Waterfall. **VFX:** Synchronized red light pulse.

**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Abyss Edge. **Background:** Infinite void and fire.

**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting Scheme:** `SILHOUETTE`. Backlit by blue, flashed by red. **Palette:** Black, Blue, Red.

**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** Static high angle. **Lens:** 14mm. **Focus:** Infinity. **Style:** Epic scale, 9:16 vertical.

### 3. AUDIO PROMPT (Hunyuan/Foley)
A massive alarm siren (Inception-style horn) blasts once, then cuts abruptly to silence.

## [ACT 3] [SCENE 3.3] [Timecode: 01:04-01:10] [OUTRO/GLITCH]
**Action:** The camera tries to zoom out, but hits an invisible wall. The image datamoshes (pixels drag). The screen freezes on Enoch's terrified face, then cuts to black console terminal.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "medium", "framing": "medium", "environment": "Null Void", "env_change": false, "actors": [{"name": "Henoch", "phase": "Voyager", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "Crash Zoom / Glitch", "mood": ["failure", "crash"], "director_intent": "End the simulation with a technical failure.", "start_image_keywords": ["datamosh", "pixel drag", "freeze frame"], "start_image_mode": "actor_in_env", "video_plan": {"start_comp": {"mode": "actor_in_env", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
A datamoshed image of Enoch's face in vertical 9:16. The pixels are dragging downwards like melting wax. The colors are splitting into RGB layers. The image looks like a frozen video frame on a broken screen. The edges are consumed by black console terminal code.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Actor:** Henoch. **Physique:** Glitched. **Skin-Shader:** `PIXEL_SORT`.

**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**Garment:** N/A. **VFX:** Datamosh, compression artifacts.

**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Void. **Background:** Black.

**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting Scheme:** `CRASH`. Random color blocks. **Palette:** RGB split.

**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** Crash zoom out. **Lens:** Digital. **Focus:** Broken. **Style:** System crash, 9:16 vertical.

### 3. AUDIO PROMPT (Hunyuan/Foley)
A system power-down chirp (falling pitch). Hard cut to silence.

## ACTOR MONOLOGUE PLAN (JSON)
MONOLOGUE_JSON: {"actors":{"Henoch":[{"scene":"1.2","text":"Keine Daten. Kein Licht. Nur ich.","words_max":7},{"scene":"2.4","text":"Mein Code... er löst sich auf.","words_max":6}],"Uriel":[{"scene":"2.2","text":"Sie brennen, weil sie verfallen sind.","words_max":7}]},"notes":"German only. Short internal monologues. Do not describe the camera or list what is visible. Use emotion, memory, and cause-effect logic. Keep total lines per chapter low (3-7). JSON must be in one line."}