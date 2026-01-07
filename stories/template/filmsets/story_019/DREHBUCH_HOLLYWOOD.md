# DREHBUCH KAPITEL 19 - PRODUCTION READY

## CHAPTER NARRATION
NARRATOR_TEXT: Die Logik dieser Welt ist zerbrochen. Ich betrete eine Zone, in der die Gesetze der Schöpfung nur noch fehlerhafte Algorithmen sind. Hier, am Rande des gerenderten Seins, offenbart sich die Sünde nicht als moralischer Fehltritt, sondern als fataler Systemabsturz. Ich bin der einzige Zeuge, der diesen Quellcode lesen kann, bevor der Bildschirm schwarz wird.

## [ACT 1] [SCENE 19.1] [Timecode: 00:00-00:03] [INGRESS_IMPACT]
**Action:** Henoch's boots hit cracked concrete hard. Dust particles hang frozen in mid-air due to lag. Uriel stands motionless in the foreground.
**Dialog:** None.

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "mixed", "shot_type": "low_angle", "framing": "wide", "environment": "Sector_Zero_Concrete_Void", "env_change": true, "actors": [{"name": "Henoch", "phase": "Voyager", "presence": "on_screen", "focus": "secondary"}, {"name": "Uriel", "phase": "Archangel", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "Low angle, focus on boots impact", "mood": ["impact", "unnatural"], "director_intent": "Establish the physicality of arrival in a glitched environment.", "start_image_keywords": ["concrete_impact", "frozen_dust", "time_lag"], "start_image_mode": "actor_in_env", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.0}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Low angle shot, cinematic 9:16. Close up on heavy high-tech polymer boots slamming onto cracked grey concrete. A cloud of fine dust and debris is exploded outwards but is frozen in perfect suspension, defying gravity. In the blurred background, the towering, motionless legs of Archangel Uriel in matte vantablack armor. Harsh, clinical white lighting. High texture detail on the concrete and boot materials.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Henoch's legs in Voyager hazmat gear, Uriel's static lower body.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Henoch: Exo-skeleton boots, synthetic fabric. Uriel: Rigid plating.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Grey void, cracked concrete floor.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Cold, sterile top-down light.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Camera shakes violently on impact, then freezes. The dust particles do not settle; they hang in the air (time-stop simulation).

### 3. AUDIO PROMPT (Hunyuan/Foley)
A heavy, distorted bass thud (impact) followed instantly by a sharp digital "crunch" or bit-crushed noise. Then absolute silence.

## [ACT 1] [SCENE 19.2] [Timecode: 00:03-00:08] [ESTABLISHING_SECTOR]
**Action:** Wide shot of Sector 19. The horizon tears off into black. Walls flicker black. Silhouettes in the distance.
**Dialog:** "Hier stehen die Engel..."

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "establishing", "framing": "wide", "environment": "Sector_Zero_Corrupted", "env_change": false, "actors": [{"name": "Uriel", "phase": "Archangel", "presence": "on_screen", "focus": "secondary"}], "props": [], "camera": "Slow pan, extreme wide", "mood": ["isolation", "decay"], "director_intent": "Show the quarantine zone as a rendering failure.", "start_image_keywords": ["texture_streaming_error", "infinite_void", "black_flicker"], "start_image_mode": "env_only", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "a2f", "audio_id": "uriel_lines_1", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.0}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 6}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Extreme wide shot, top-down satellite view aesthetic, 9:16. A square patch of grey, ruined concrete floating in an absolute black void. The edges of the concrete are jagged, pixelated, and dissolving into unrendered data. On the platform, two tiny figures (Henoch and Uriel). In the background, a chaotic mass of restless shadows. The "walls" of the reality are flickering black planes.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Tiny distant figures of Henoch and Uriel.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Indistinguishable at this distance.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Isolated platform in a void.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Strobe lighting from nowhere.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Slow, steady pan. The background textures pop in and out (LOD popping). The black void is static and unmoving.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Loud, oppressive server room drone ("The Drone"). Layered with the sound of distant wind howling through a ventilation shaft.

## [ACT 1] [SCENE 19.3] [Timecode: 00:08-00:15] [ANALYSIS_MODE]
**Action:** Uriel points mechanically. Henoch's sensor-rig zooms, lenses rotating. Coolant steam hisses.
**Dialog:** "...die sich mit Frauen vermischt haben."

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "medium", "framing": "medium", "environment": "Sector_Zero_Corrupted", "env_change": false, "actors": [{"name": "Uriel", "phase": "Archangel", "presence": "on_screen", "focus": "primary"}, {"name": "Henoch", "phase": "Voyager", "presence": "on_screen", "focus": "secondary"}], "props": ["Sensor_Rig"], "camera": "Over the shoulder, quick zoom", "mood": ["clinical", "observational"], "director_intent": "Visualize the act of seeing as a mechanical process.", "start_image_keywords": ["mechanical_pointing", "sensor_zoom", "coolant_steam"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "a2f", "audio_id": "uriel_lines_2", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.0}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 8}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Medium over-the-shoulder shot, 9:16. Foreground: Henoch's back and head. He wears a complex sensor rig over his eyes with multiple rotating lenses. Jets of white coolant steam vent from his collar. Background: Uriel, sharp focus, extending a rigid, armored gauntlet to point at the scene. Uriel's face is a perfect, featureless mask of gold circuitry.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Uriel (Admin) and Henoch (Observer).
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Henoch: Hazmat suit, Sensor Rig. Uriel: Vantablack armor.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Grey blurred background.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Blue light from Henoch's sensors illuminates Uriel's arm.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Rapid snap-zoom. The lenses on Henoch's face spin mechanically. Steam vents rhythmically.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Hydraulic servo sounds (whirring, clicking). A sharp hiss of pressurized steam release.

## [ACT 2] [SCENE 19.4] [Timecode: 00:15-00:20] [THE_GLITCH_POLYMORPHS]
**Action:** Close-up on a Fallen Angel. Rapid frame-cuts between Man, Bull-Head, and Geometry Shards.
**Dialog:** "Ihre Geister nehmen viele Gestalten an."

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "close_up", "framing": "close_up", "environment": "Sector_Zero_Corrupted", "env_change": false, "actors": [{"name": "Fallen_Angel_01", "phase": "Glitch", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "Static, jump cuts", "mood": ["chaos", "horror"], "director_intent": "Portray demonic shapeshifting as a mesh-rendering error.", "start_image_keywords": ["glitch_entity", "vertex_explosion", "obsidian_shards"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "uriel_lines_3", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.0}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 8}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Close up, 9:16. A silhouette of a humanoid figure made of sharp, black obsidian glass shards. The figure is "exploding" outward—polygons are stretched and detached from the main body (vertex explosion). Inside the black glass, a reflection of a burning bull's head is visible. The background is a mess of digital compression artifacts.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** A glitching entity.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** None. Raw geometry.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Corrupted data void.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Internal red glow vs external cold static.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Aggressive jump cuts. Frame 1: Human. Frame 2: Beast. Frame 3: Abstract Spikes. No smooth transitions.

### 3. AUDIO PROMPT (Hunyuan/Foley)
High-pitch digital screeching (scrubbing audio). Glitch stutter effects.

## [ACT 2] [SCENE 19.5] [Timecode: 00:20-00:28] [DATA_ROT_CORRUPTION]
**Action:** Humans kneel before glitches. Contact causes grey skin discoloration and red code bleeding.
**Dialog:** "...sie verunreinigen die Menschen..."

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "mixed", "shot_type": "high_angle", "framing": "wide", "environment": "Sector_Zero_Corrupted", "env_change": false, "actors": [{"name": "Human_Victims", "phase": "Corrupted", "presence": "on_screen", "focus": "primary"}, {"name": "Fallen_Angels", "phase": "Glitch", "presence": "on_screen", "focus": "secondary"}], "props": [], "camera": "High angle surveillance", "mood": ["disgust", "infection"], "director_intent": "Show sin as a viral data infection spreading on contact.", "start_image_keywords": ["grey_skin", "red_code_blood", "data_rot"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "uriel_lines_4", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.0}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 6}
### 1. START IMAGE PROMPT (Midjourney/Flux)
High angle lab-view, 9:16. Pale, semi-transparent human figures kneeling. A glitch-entity touches the forehead of a human. From the contact point, a grey, stone-like texture spreads rapidly across the human's skin. Glowing red binary code bleeds from the eyes and nose of the victim like liquid.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Human victims and Glitch masters.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Humans in rags.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Concrete floor.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Red warning lights pulsing.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Fluid morphing effect on the skin texture. The red code drips down (liquid simulation).

### 3. AUDIO PROMPT (Hunyuan/Foley)
Distorted whispering played backward. Wet, squelching sounds mixed with static.

## [ACT 2] [SCENE 19.6] [Timecode: 00:28-00:35] [FERROFLUID_SACRIFICE]
**Action:** Sacrifice ritual. Black ferrofluid flows upwards from victims to entities. Gravity bug.
**Dialog:** "...und verleiten sie, Dämonen zu opfern."

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "prop", "shot_type": "close_up", "framing": "close_up", "environment": "Sector_Zero_Corrupted", "env_change": false, "actors": [], "props": ["Ferrofluid_Liquid"], "camera": "Orbiting macro", "mood": ["unnatural", "dark_magic"], "director_intent": "Depict the sacrifice as a magnetic data transfer defying physics.", "start_image_keywords": ["ferrofluid", "reverse_gravity", "magnetic_liquid"], "start_image_mode": "prop_only", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "uriel_lines_5", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.0}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 8}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Macro shot, 9:16. A pool of jet-black, spiked ferrofluid. Instead of pooling, droplets and spikes are being pulled upwards towards an unseen magnetic source. The liquid reflects the red environment lights. It looks viscous and intelligent.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Black liquid (Ferrofluid).
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** None.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Dark ritual space.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Specular highlights on black liquid.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Slow orbital camera movement. The liquid moves in reverse gravity, forming spikes and tendrils.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Deep sub-bass pulse (heartbeat rhythm). Magnetic hum.

## [ACT 2] [SCENE 19.7] [Timecode: 00:35-00:42] [SIREN_SIGNAL_NOISE]
**Action:** The Sirens. Still figures. Faces hidden by chromatic aberration. Mouths open, air distorts.
**Dialog:** "Auch ihre Frauen wurden zu Sirenen."

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "medium", "framing": "medium", "environment": "Sector_Zero_Corrupted", "env_change": false, "actors": [{"name": "Sirens", "phase": "Hologram", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "Frontal, heat haze lens", "mood": ["hypnotic", "dangerous"], "director_intent": "Reveal attraction as a dangerous signal interference.", "start_image_keywords": ["chromatic_aberration", "heat_haze", "silent_scream"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "uriel_lines_6", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.0}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 8}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Medium shot, 9:16. Three female figures in flowing, digital fabric robes. Their faces are completely obscured by heavy RGB chromatic aberration and pixel sorting effects (censorship style). They are screaming, but silence is implied. The air around them ripples with intense heat waves (refraction).

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Female humanoid forms.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Digital cloth simulation.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Distorted background.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Purple/Pink bioluminescence.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** The figures vibrate slightly. The heat haze makes the entire image wobble.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Piercing "Coil Whine" (high frequency). No voice, just electronic interference.

## [ACT 2] [SCENE 19.8] [Timecode: 00:42-00:50] [RED_ALERT_VERDICT]
**Action:** Uriel turns away. Sky turns Emergency Red. System Warning countdown in sky.
**Dialog:** "Bis zum Tag des großen Gerichts."

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "low_angle", "framing": "medium", "environment": "Sector_Zero_Corrupted", "env_change": false, "actors": [{"name": "Uriel", "phase": "Archangel", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "Low angle push in", "mood": ["finality", "judgment"], "director_intent": "Visualize the divine verdict as a system-wide alert state.", "start_image_keywords": ["emergency_red", "sky_countdown", "uriel_back"], "start_image_mode": "actor_in_env", "video_plan": {"start_comp": {"mode": "actor_first", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "a2f", "audio_id": "uriel_lines_7", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.0}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 8}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Low angle shot looking up at Uriel's back and profile. The previously black sky has turned a solid, flat "Emergency Red" (#FF0000). Huge, faint holographic numbers (a countdown) are visible in the sky, partially obscured by static. Uriel stands calm against the red alert.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Uriel.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Vantablack armor.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Red sky.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Harsh red backlighting.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Slow push in. The numbers in the sky tick down.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Muffled alarm siren, distant and echoing. Uriel's voice is deep and resonant.

## [ACT 3] [SCENE 19.9] [Timecode: 00:50-00:58] [ROOT_ACCESS_WIREFRAME]
**Action:** POV Henoch. Blinks. Mechanical shutter. World renders to blue wireframe.
**Dialog:** "Und ich, Henoch, sah es allein."

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "interface", "shot_type": "pov", "framing": "extreme_close_up", "environment": "Wireframe_Grid", "env_change": true, "actors": [], "props": ["HUD_Visor"], "camera": "POV, digital transition", "mood": ["clarity", "revelation"], "director_intent": "Switch from render view to debug/schematic view.", "start_image_keywords": ["wireframe_world", "blueprint_blue", "debug_view"], "start_image_mode": "ui_only", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "a2f", "audio_id": "henoch_lines_1", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.0}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 8}
### 1. START IMAGE PROMPT (Midjourney/Flux)
POV shot, 9:16. The world is reduced to a glowing blue wireframe schematic on a black background (CAD style). The outlines of ruins and entities are visible as mathematical geometry lines. No textures. HUD elements overlay the vision with "ROOT ACCESS: GRANTED" in Ge'ez.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** None.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** HUD interface.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Wireframe world.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Neon blue lines.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** A digital "wipe" effect transitions the scene from textured to wireframe.

### 3. AUDIO PROMPT (Hunyuan/Foley)
All environmental sound cuts out abruptly. Only the sound of Henoch's breathing inside the helmet.

## [ACT 3] [SCENE 19.10] [Timecode: 00:58-01:05] [ISOLATION_DELETE]
**Action:** Top down view. Entities and Uriel dissolve into data points. Henoch remains alone in grid.
**Dialog:** "Das Ende aller Dinge."

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "high_angle", "framing": "extreme_wide", "environment": "Wireframe_Grid", "env_change": false, "actors": [{"name": "Henoch", "phase": "Voyager", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "Top down, god view", "mood": ["loneliness", "null"], "director_intent": "Show the deletion of the simulation around the observer.", "start_image_keywords": ["data_deletion", "solitary_figure", "grid_floor"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "a2f", "audio_id": "henoch_lines_2", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.0}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 5}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Extreme high angle top-down shot, 9:16. Henoch stands alone on an infinite glowing grid floor. Around him, clouds of blue particles are fading away—the remains of Uriel and the entities being deleted from memory. The space is vast and empty.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Henoch (Small figure).
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Voyager gear (glowing).
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Infinite grid.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Grid glow.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** The particles dissolve into nothingness. Henoch is the only persistent object.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Hollow wind sound ("The Void").

## [ACT 3] [SCENE 19.11] [Timecode: 01:05-01:15] [SHUTDOWN_BLACK]
**Action:** Close up Henoch's eye. Blue grid lines in reflection turn off. Darkness.
**Dialog:** "Kein anderer Mensch sieht, was ich sah."

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "extreme_close_up", "framing": "extreme_close_up", "environment": "Black_Screen", "env_change": true, "actors": [{"name": "Henoch", "phase": "Voyager", "presence": "on_screen", "focus": "primary"}], "props": ["HUD_Visor"], "camera": "Macro, fade to black", "mood": ["end", "secret"], "director_intent": "Final system power down.", "start_image_keywords": ["visor_reflection", "lights_out", "darkness"], "start_image_mode": "actor_only", "video_plan": {"start_comp": {"mode": "actor_first", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "a2f", "audio_id": "henoch_lines_3", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.0}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 8}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Extreme close up on Henoch's visor/eye. In the reflection, the last blue grid lines blink out one by one. The image becomes almost entirely black, with only a faint rim light on the helmet remaining.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Henoch's visor.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Helmet.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Darkness.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Fading blue reflection.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** The lights go out. Hard cut to black.

### 3. AUDIO PROMPT (Hunyuan/Foley)
The sound of a large machine spinning down (fan noise decreasing in pitch). A final metallic click.

## ACTOR MONOLOGUE PLAN (JSON)
MONOLOGUE_JSON: {"actors":{"Uriel":[{"scene":"19.2","text":"Hier stehen die Engel.","words_max":6},{"scene":"19.3","text":"Die sich mit Frauen vermischt haben.","words_max":8},{"scene":"19.4","text":"Ihre Geister nehmen viele Gestalten an.","words_max":8},{"scene":"19.5","text":"Sie verunreinigen die Menschen.","words_max":6},{"scene":"19.6","text":"Und verleiten sie, Dämonen zu opfern.","words_max":8},{"scene":"19.7","text":"Auch ihre Frauen wurden zu Sirenen.","words_max":8},{"scene":"19.8","text":"Bis zum Tag des großen Gerichts.","words_max":8}],"Henoch":[{"scene":"19.9","text":"Und ich, Henoch, sah es allein.","words_max":8},{"scene":"19.10","text":"Das Ende aller Dinge.","words_max":5},{"scene":"19.11","text":"Kein anderer Mensch sieht, was ich sah.","words_max":8}]},"notes":"German only. Short internal monologues. Do not describe the camera or list what is visible. Use emotion, memory, and cause-effect logic. Keep total lines per chapter low. JSON must be in one line."}