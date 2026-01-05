# DREHBUCH KAPITEL 101 - PRODUCTION READY

## CHAPTER NARRATION
NARRATOR_TEXT: Die Architektur der Welt ist fragil, gewoben aus Licht und Mathematik. Wenn die Berechnung bricht und das Meer den Gehorsam verweigert, ist es kein Zorn, der uns trifft, sondern eine notwendige Korrektur. Der Auditor sieht nicht das Wasser, sondern den Fehler im Code, der bereinigt werden muss.

## [ACT I] [SCENE 1.1] [Timecode: 00:00-00:04] [ESTABLISHING]
**Action:** Satellite view of the cloud layer. Vector grid overlay zooms in rapidly: 100km -> 10km -> Surface.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "establishing", "framing": "wide", "environment": "High Altitude Cloud Layer", "env_change": true, "actors": [], "props": [], "camera": "Orthographic Top-Down / Zoom", "mood": ["technical", "cold"], "director_intent": "Show the simulation from the perspective of the operating system.", "start_image_keywords": ["satellite view", "grid overlay"], "start_image_mode": "env_only", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "ENV_CLOUD_LAYER", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Satellite view of a dense, realistic cloud layer seen from space, overlaid with a glowing neon-green vector grid map. 8k resolution, photorealistic earth texture below clouds, high contrast technical interface aesthetic, orthographic projection, data visualization style, 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Subject:** Planet Earth Surface. **Identity:** Simulation Map.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**Overlay:** Digital vector grid lines, green and white, superimposed on the atmosphere.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Stratosphere. **Atmosphere:** Thin clouds, curvature of the earth.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting:** Sunlight from upper right, harsh shadows on clouds. **Palette:** Blue, White, Neon Green.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** Top-down satellite camera. **Movement:** Rapid zoom in, crashing through cloud layers towards the surface. **Style:** Google Earth zoom but cinematic and glitchy.

### 3. AUDIO PROMPT (Hunyuan/Foley)
High-pitched digital screech of a modem handshake or data transmission. Wind noise increasing in pitch as the camera zooms in.

## [ACT I] [SCENE 1.2] [Timecode: 00:04-00:08] [INGRESS]
**Action:** Henoch manifests in Arid Sector 101. No motion blur. He stands perfectly still amidst dry cracked earth.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "wide", "framing": "full_body", "environment": "Arid Desert Sector 101", "env_change": true, "actors": [{"name": "Henoch", "phase": "MASTER", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "14mm Low Angle", "mood": ["imposing", "still"], "director_intent": "Establish the sudden, weightless arrival of the entity.", "start_image_keywords": ["Henoch", "desert"], "start_image_mode": "actor_in_env", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "POSE_STAND_STILL", "env_id": "ENV_DESERT_ARID", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Full body shot of Henoch standing in a cracked, dry desert. He wears a sleek obsidian exosuit that looks wet with coolant. His skin is translucent gray with faint internal blue glow. Low angle shot, 14mm lens, dramatic hard sunlight casting long shadows, hyper-detailed texture on the dry ground, 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Subject:** Henoch (Auditor). **Skin:** Translucent gray, internal blue vascular glow. **Pose:** Perfectly static, commanding.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**Gear:** Obsidian Exosuit, matte black, glistening with liquid coolant.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Arid Desert. **Ground:** Cracked dry earth, dust particles suspended in air.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting:** Harsh noon sun, high contrast. **VFX:** Subtle heat haze distortion around him.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** Low angle, wide 14mm. **Movement:** Camera is static, emphasizing his sudden appearance. **Render:** Photorealistic, 8k.

### 3. AUDIO PROMPT (Hunyuan/Foley)
A heavy, low-frequency sub-bass thud on impact. Silence immediately after, except for a faint electrical hum.

## [ACT I] [SCENE 1.3] [Timecode: 00:08-00:12] [PHYSICS PAUSE]
**Action:** Raindrops hang frozen in mid-air. They are chrome spheres, reflecting the dry ground. A red "TIMEOUT" glyph floats in the bokeh.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "insert", "framing": "close_up", "environment": "Arid Desert Sector 101", "env_change": false, "actors": [], "props": ["Frozen Raindrops"], "camera": "100mm Macro", "mood": ["surreal", "glitch"], "director_intent": "Visualize the system lag through frozen physics.", "start_image_keywords": ["frozen rain", "chrome spheres"], "start_image_mode": "prop_only", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "ENV_DESERT_ARID", "props": ["PROP_RAINDROPS_CHROME"], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Macro shot of raindrops frozen in mid-air above dry desert ground. The drops are perfect chrome spheres, reflecting the cracked earth below. In the blurred background, a faint red holographic glyph reads "TIMEOUT". 100mm lens, shallow depth of field, surreal sci-fi aesthetic, high fidelity, 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Subject:** Raindrops. **Material:** Liquid metal / Chrome.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**N/A:** Natural element glitch.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Desert air. **Physics:** Frozen, zero gravity.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting:** Ambient occlusion, soft reflections on the chrome drops. **VFX:** Red "TIMEOUT" text floating in background bokeh.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** 100mm Macro. **Movement:** Slow tracking shot sideways through the grid of frozen drops.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Loud electrical buzzing, like a high-voltage transformer or a Jacob's Ladder arc. No rain sound.

## [ACT I] [SCENE 1.4] [Timecode: 00:12-00:15] [DIAGNOSTIC]
**Action:** Close-up on Henoch’s face. Ge'ez error logs scroll across his translucent skin. Blue veins pulse.
**Dialog:** Henoch: "Systemprüfung initiiert."



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "close_up", "framing": "extreme_close_up", "environment": "Arid Desert Sector 101", "env_change": false, "actors": [{"name": "Henoch", "phase": "MASTER", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "85mm Portrait", "mood": ["analytical", "intense"], "director_intent": "Show the internal processing of the entity.", "start_image_keywords": ["Henoch face", "scrolling text"], "start_image_mode": "actor_only", "video_plan": {"start_comp": {"mode": "actor_first", "actor_pose_id": "POSE_FACE_NEUTRAL", "env_id": "ENV_DESERT_ARID", "props": [], "notes": ""}, "motion_driver": {"type": "a2f", "audio_id": "henoch_system_check", "pose_source": "", "driver_notes": "Minimal lip movement, internal voice"}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 5}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Extreme close-up of Henoch's face. His skin is translucent gray, revealing glowing neon-blue veins underneath. Glowing Ge'ez characters scroll vertically across his forehead and cheeks like a digital display. His eyes are intense. 85mm lens, sharp focus on skin texture, cinematic lighting, 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Subject:** Henoch (Auditor). **Skin:** Translucent, displaying scrolling Ge'ez text. **Veins:** Pulsing blue light.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**Head:** No helmet, bare skin acting as a display.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Background:** Blurred desert horizon.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting:** Soft face light, internal glow from veins.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** 85mm Portrait. **Movement:** Minimal, slight breathing. **Focus:** The scrolling text on the skin.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Henoch's voice, dual-layered: a whisper mixed with a slightly delayed synthetic synthesis. "Systemprüfung initiiert."

## [ACT II] [SCENE 2.1] [Timecode: 00:15-00:19] [NODE SHIFT]
**Action:** Instant transport to the Ocean Sector. Dark, violent storm. The "Wind" is visible as vector lines.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "wide", "framing": "wide", "environment": "Ocean Sector Storm", "env_change": true, "actors": [{"name": "Henoch", "phase": "MASTER", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "35mm Handheld", "mood": ["chaotic", "violent"], "director_intent": "Jarring transition to a chaotic environment.", "start_image_keywords": ["storm", "ocean", "Henoch"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "POSE_STAND_STORM", "env_id": "ENV_OCEAN_STORM", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Wide shot of a violent ocean storm at night. Henoch stands calmly on the turbulent water surface. The wind is visualized as glowing white vector lines cutting through the air. Massive dark waves, rain, lightning. 35mm lens, handheld camera feel, cinematic action composition, 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Subject:** Henoch. **Action:** Standing on water.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**Gear:** Obsidian Exosuit.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Stormy Ocean. **Atmosphere:** Heavy rain, lightning. **VFX:** Wind represented by white vector streaks.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting:** Strobe lightning flashes. **Palette:** Dark Blue, Black, White.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** 35mm Handheld. **Movement:** Shaky cam, reacting to the storm intensity.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Deafening roar of a massive server room air intake system, replacing natural wind sound. Thunder cracks.

## [ACT II] [SCENE 2.2] [Timecode: 00:19-00:24] [RENDER FAIL]
**Action:** A massive wave crests. The spray fails to render transparency, turning into tumbling black geometric data-blocks.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "wide", "framing": "wide", "environment": "Ocean Sector Storm", "env_change": false, "actors": [], "props": ["Glitch Wave"], "camera": "Wide Action", "mood": ["glitch", "destructive"], "director_intent": "Depict the breakdown of the physics engine visually.", "start_image_keywords": ["voxel wave", "black cubes"], "start_image_mode": "env_only", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "ENV_OCEAN_STORM", "props": ["PROP_WAVE_VOXEL"], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
A massive ocean wave cresting, but the foam and spray are replaced by thousands of tumbling black obsidian cubes. The water surface transitions from liquid to geometric voxel blocks. Dark stormy sky, lightning illumination, high contrast, photorealistic rendering of a digital glitch, 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Subject:** Ocean Wave. **Form:** Glitching fluid dynamics.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**N/A:** Environmental glitch.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Glitch Ocean. **Physics:** Fluid turning into rigid bodies (cubes).
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting:** Lightning flashes illuminating the black cubes. **Texture:** Wet, reflective surfaces on the cubes.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** Wide Action. **Movement:** Following the wave crash. **Style:** High-end VFX simulation failure.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Distorted white noise, bit-crushed crashing sounds. Not water splashing, but digital static and crunching.

## [ACT II] [SCENE 2.3] [Timecode: 00:24-00:29] [CLIPPING]
**Action:** The wooden ship plunges into the water but passes *through* the surface without resistance. "COLLISION_OFF" warning flashes red on the hull.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "prop", "shot_type": "medium", "framing": "medium", "environment": "Ocean Sector Storm", "env_change": false, "actors": [], "props": ["Phoenician Ship"], "camera": "Tracking Shot", "mood": ["wrong", "broken"], "director_intent": "Show the loss of collision detection.", "start_image_keywords": ["ship hull", "clipping water"], "start_image_mode": "prop_only", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "ENV_OCEAN_STORM", "props": ["PROP_SHIP_PHOENICIAN"], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Medium shot of a wooden Phoenician ship hull intersecting perfectly with the ocean water surface, as if they are ghost layers. No splash, no foam, just wood passing through water. A bright red holographic warning "COLLISION_OFF" is projected on the wet wood. Stormy lighting, realistic textures, 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Subject:** Ship Hull. **Material:** Wet wood.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**Overlay:** Red "COLLISION_OFF" text flashing.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Ocean surface. **Physics:** No interaction between ship and water (clipping).
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting:** Dark, stormy, red warning light reflection.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** Medium Tracking. **Movement:** Following the ship's plunge. **Focus:** The intersection line where physics fails.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Metal screeching and audio tearing sounds. No water displacement sounds.

## [ACT II] [SCENE 2.4] [Timecode: 00:29-00:34] [ENTITY CORRUPTION]
**Action:** The "Kings" (sailors) scream silently. Their animations loop frantically (0.5s repeat). Textures stretch and tear off their bodies.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "medium", "framing": "medium", "environment": "Ship Deck", "env_change": false, "actors": [{"name": "Kings", "phase": "PROXY", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "Dutch Angle", "mood": ["horror", "glitch"], "director_intent": "Portray the characters as suffering software entities.", "start_image_keywords": ["glitching sailors", "texture stretching"], "start_image_mode": "actor_in_env", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "POSE_GLITCH_LOOP", "env_id": "ENV_SHIP_DECK", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Phoenician sailors on a storm-tossed deck, screaming. Their bodies are glitching: textures are stretching into long spikes, faces are distorted. One sailor is stuck in a T-pose. Rain lashes down. Dutch angle, horror atmosphere, photorealistic rendering of 3D model failure, 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Subject:** Sailors (Kings). **State:** Corrupted mesh.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**Clothing:** Rags, texture maps tearing away from the body.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Ship Deck. **Weather:** Storm.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting:** Lightning flashes. **VFX:** Mesh vertices exploding outward.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** Dutch Angle. **Movement:** Jittery, stuttering edit style. **Animation:** Characters looping the same scream motion rapidly.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Glitched vocal samples looping rapidly. "Ah-Ah-Ah-Ah". Digital distortion.

## [ACT II] [SCENE 2.5] [Timecode: 00:34-00:39] [LIDAR SCAN]
**Action:** Henoch observes the chaos. Red laser grids fan out from his eyes, mapping the broken physics of the ship.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "over_shoulder", "framing": "medium", "environment": "Ship Deck", "env_change": false, "actors": [{"name": "Henoch", "phase": "MASTER", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "Whip Pan", "mood": ["calculating", "detached"], "director_intent": "Henoch analyzes the scene with machine vision.", "start_image_keywords": ["Henoch", "laser eyes"], "start_image_mode": "actor_in_env", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "POSE_SCANNING", "env_id": "ENV_SHIP_DECK", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Over-the-shoulder shot of Henoch looking at the glitching ship. Fanned red laser grids emit from his eyes, scanning the environment. The lasers illuminate the rain and the distorted sailors. Henoch's exosuit is wet and sleek. Cinematic lighting, volumetric fog, 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Subject:** Henoch. **Action:** Scanning.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**Eyes:** Emitting red LIDAR grid patterns.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Ship Deck. **Target:** The glitching sailors.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting:** Red laser light cutting through the blue storm darkness.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** Over-the-Shoulder. **Movement:** Whip pan following the laser sweep.

### 3. AUDIO PROMPT (Hunyuan/Foley)
High-tech sonar ping or laser scanning sound. Background storm noise.

## [ACT II] [SCENE 2.6] [Timecode: 00:39-00:45] [THE BOUNDARY]
**Action:** The raging digital ocean hits the shoreline. It flattens instantly against an invisible geometric wall, unable to touch the dry sand.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "wide", "framing": "wide", "environment": "Shoreline Boundary", "env_change": true, "actors": [], "props": ["Invisible Wall"], "camera": "Low Angle", "mood": ["unnatural", "constrained"], "director_intent": "Show the hard limit of the simulation area.", "start_image_keywords": ["ocean barrier", "invisible wall"], "start_image_mode": "env_only", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "ENV_SHORELINE", "props": ["PROP_BARRIER_GRID"], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Low angle shot at a shoreline. A massive, violent ocean wave hits an invisible vertical wall and flattens completely against it like a texture on glass. On the other side of the line, dry white sand is perfectly undisturbed. A faint hexagonal orange grid pattern appears at the impact point. Surreal contrast, 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Subject:** Ocean Wave vs Sand.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**N/A:** Physics anomaly.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Shoreline. **Physics:** Hard collision boundary.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting:** Stormy sea side vs calm sand side. **VFX:** Orange hexagonal grid flash on impact.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** Low Angle, ground level. **Movement:** Static, observing the unnatural collision.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Heavy impact thud, like a body hitting thick glass. No splashing sound on the sand side.

## [ACT III] [SCENE 3.1] [Timecode: 00:45-00:50] [THE PURGE]
**Action:** Henoch raises a hand. The storm freezes instantly. The "Kings" shatter into raw light particles.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "wide", "framing": "full_body", "environment": "Ship Deck", "env_change": false, "actors": [{"name": "Henoch", "phase": "MASTER", "presence": "on_screen", "focus": "primary"}, {"name": "Kings", "phase": "PROXY", "presence": "on_screen", "focus": "secondary"}], "props": [], "camera": "Wide Symmetrical", "mood": ["divine", "final"], "director_intent": "The execution of the system command.", "start_image_keywords": ["Henoch hand raise", "shattering sailors"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "POSE_COMMAND_HAND", "env_id": "ENV_SHIP_DECK", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Wide symmetrical shot of Henoch on the ship deck, raising one hand in a command gesture. The storm rain is frozen in mid-air. The glitching sailors are shattering into millions of bright white light particles (voxels). High contrast, dramatic backlighting, divine tech atmosphere, 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Subject:** Henoch. **Action:** Raising hand. **Target:** Sailors.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**Gear:** Exosuit.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Ship Deck. **Event:** Time freeze and particle disintegration.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting:** Bright white light from the shattering figures.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** Wide Symmetrical. **Movement:** Freeze frame effect, camera moves slightly in 3D space (bullet time).

### 3. AUDIO PROMPT (Hunyuan/Foley)
Sudden, absolute silence. A vacuum sound sucking away all noise.

## [ACT III] [SCENE 3.2] [Timecode: 00:50-00:55] [STABILIZATION]
**Action:** The black data-blocks melt back into realistic water. The ship hull solidifies and floats properly.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "wide", "framing": "wide", "environment": "Ocean Sector Calm", "env_change": true, "actors": [], "props": ["Ship Hull"], "camera": "Time-Lapse Flow", "mood": ["calm", "restored"], "director_intent": "Visualizing the restoration of system integrity.", "start_image_keywords": ["melting voxels", "calm water"], "start_image_mode": "env_only", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "ENV_OCEAN_CALM", "props": ["PROP_SHIP_RESTORED"], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
The black obsidian cubes of the glitching wave are melting down into clear, realistic blue water. The wooden ship hull looks solid and wet, floating naturally. The storm clouds are breaking, revealing starlight. Smooth textures, calming blue and black palette, high fidelity, 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Subject:** Water and Ship. **Action:** Restoration.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**N/A:** Environmental repair.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Ocean. **Physics:** Returning to normal fluid dynamics.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting:** Soft moonlight. **Texture:** Smooth water surface.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** Static wide. **Movement:** Morphing/Time-lapse style transition from blocky to smooth.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Clean, fluid rushing sound of water. Gentle waves.

## [ACT III] [SCENE 3.3] [Timecode: 00:55-00:60] [VERDICT]
**Action:** Extreme Close-Up on Henoch. The scrolling text on his face stops. A single Ge'ez symbol for "DELETE" burns on his forehead.
**Dialog:** Henoch: "Integrität wiederhergestellt."



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "close_up", "framing": "extreme_close_up", "environment": "Ocean Sector Calm", "env_change": false, "actors": [{"name": "Henoch", "phase": "MASTER", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "Macro Zoom", "mood": ["final", "clean"], "director_intent": "The final log entry.", "start_image_keywords": ["Henoch face", "delete symbol"], "start_image_mode": "actor_only", "video_plan": {"start_comp": {"mode": "actor_first", "actor_pose_id": "POSE_FACE_SERENE", "env_id": "ENV_OCEAN_CALM", "props": [], "notes": ""}, "motion_driver": {"type": "a2f", "audio_id": "henoch_integrity_restored", "pose_source": "", "driver_notes": "Subtle expression change"}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 5}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Extreme close-up of Henoch's face, calm and serene. The scrolling text is gone. A single, bright burning Ge'ez symbol (meaning DELETE) glows on his forehead. His skin is less translucent, more solid. 85mm lens, sharp focus, cool blue lighting, 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Subject:** Henoch. **Expression:** Neutral, finalized.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**Face:** Glowing Ge'ez symbol on forehead.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Background:** Dark calm ocean bokeh.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting:** Cool, clean light.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** Slow Zoom In. **Focus:** The symbol on the forehead.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Henoch's voice, clear and resonant: "Integrität wiederhergestellt."

## [ACT III] [SCENE 3.4] [Timecode: 00:60-00:65] [EGRESS]
**Action:** Henoch dissolves into a vertical stream of golden binary code. The camera lingers on the calm, perfect ocean.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "wide", "framing": "wide", "environment": "Ocean Sector Calm", "env_change": false, "actors": [{"name": "Henoch", "phase": "MASTER", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "Static Wide", "mood": ["peaceful", "empty"], "director_intent": "Exit the scene, leaving a clean state.", "start_image_keywords": ["golden code", "dissolve"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "POSE_DISSOLVE", "env_id": "ENV_OCEAN_CALM", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Wide shot of the calm ocean at night. Henoch's form is dissolving into a vertical stream of golden binary code and light particles, ascending into the sky. The water is perfectly flat and reflective. Peaceful, spiritual tech aesthetic, 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Subject:** Henoch. **Action:** Dissolving.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**VFX:** Body turning into golden data stream.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Calm Ocean.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting:** Golden light from the dissolution reflecting on water.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** Static Wide. **Transition:** Fade to Black.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Low frequency hum fading out. Gentle water lapping.

## ACTOR MONOLOGUE PLAN (JSON)
MONOLOGUE_JSON: {"actors":{"Henoch":[{"scene":"1.4","text":"Systemprüfung initiiert.","words_max":5},{"scene":"3.3","text":"Integrität wiederhergestellt.","words_max":5}]},"notes":"German only. Short internal monologues. Do not describe the camera or list what is visible. Use emotion, memory, and cause-effect logic. Keep total lines per chapter low (3-7). JSON must be in one line."}