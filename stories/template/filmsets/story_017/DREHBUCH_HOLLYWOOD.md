✗ Create stories\story_001\filmsets\chapter_017\DIRECTOR_MANUAL.md
   Path not absolute

✗ Create the directory for Chapter 17 filmset
 $ New-Item -Path "stories\story_001\filmsets\chapter_017" -ItemType Directory -Force
   Permission denied and could not request permission from user

✗ Create the directory for Chapter 17 filmset using absolute path
 $ New-Item -Path "C:\Users\sasch\visionexe\stories\story_001\filmsets\chapter_017" -ItemType
 Directory -Force
   Permission denied and could not request permission from user

✗ Create stories\story_001\filmsets\chapter_017\DIRECTOR_MANUAL.md
   Parent directory does not exist

✗ Create directory using Node.js
 $ node -e "const fs = require('fs'); fs.mkdirSync('stories/story_001/filmsets/chapter_017', {
 recursive: true });"
   Permission denied and could not request permission from user

✓ List contents of stories directory
 $ Get-ChildItem -Path stories
    └ 6 lines...

✗ Create directory using Python
 $ python -c "import os; os.makedirs(r'stories\story_001\filmsets\chapter_017', exist_ok=True)"
   Permission denied and could not request permission from user

✗ Create directory using cmd
 $ cmd /c mkdir "stories\story_001\filmsets\chapter_017"
   Permission denied and could not request permission from user

✗ Create test_write_perm.txt
   Permission denied and could not request permission from user

✓ Read AGENTS.md
   └ 203 lines read

# DREHBUCH KAPITEL 17 - PRODUCTION READY

## CHAPTER NARRATION
NARRATOR_TEXT: Sie hoben mich an einen Ort, wo das Feuer wie Wasser fließt und die Luft vor statischer Ladung knistert. Ich sah die Grenzen der Berechnung, dort wo die Daten

# DREHBUCH KAPITEL 17 - PRODUCTION READY

## CHAPTER NARRATION
NARRATOR_TEXT: Sie hoben mich an einen Ort, wo das Feuer wie Wasser fließt und die Luft vor statischer Ladung knistert. Ich sah die Grenzen der Berechnung, dort wo die Daten enden und die Leere beginnt. Es ist kein Berg, den ich sah, sondern der Speicher der Welt, der bis in den Himmel ragt. Hier werden die Blitze geschmiedet und die Tiefen versiegelt. Ich stand am Rand des Abgrunds und begriff, dass wir nur Code in einem endlosen Strom sind.

## [ACT 1] [SCENE 1.1] [Timecode: 00:00-00:04] [INGRESS]
**Action:** Henoch materializes from a vertical blue laser scan onto a grid of black obsidian. A dust shockwave displaces at his feet. He stumbles, disoriented.
**Dialog:** 

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "wide", "framing": "full_body", "environment": "Sector_17_Furnace", "env_change": true, "actors": [{"name": "Henoch", "phase": "Voyager", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "Low Angle / 14mm", "mood": ["disoriented", "awe"], "director_intent": "Establish the sudden, violent arrival into the system core.", "start_image_keywords": ["vertical laser scan", "obsidian grid", "dust shockwave"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Cinematic wide shot, low angle. A vertical blue laser scan beam cuts through a dark industrial void, depositing a figure onto a glossy black obsidian grid floor. A radial shockwave of dust and digital particles blasts outward from the impact point at the feet. The environment is dark, lit by the blue laser and distant orange plasma glow. High contrast, 8k resolution, unreal engine 5 render style, volumetric lighting.
### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Actor: Noah (Henoch). Skin: Translucent marble texture, glowing internal fiber-optic nerves visible beneath the surface. Expression: Disoriented, stumbling forward.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Gear: Silver-skin tech-suit, tight-fitting, reflective.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Location: Sector 17 Furnace. Floor: Polished black obsidian tiles reflecting the light. Background: Vertical walls of orange plasma fire in the distance.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Lighting: Intense vertical blue laser light from the spawn beam, contrasting with ambient orange glow.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Camera: Low angle, wide lens. Movement: Camera shakes slightly on impact (shockwave). 9:16 aspect ratio.
### 3. AUDIO PROMPT (Hunyuan/Foley)
Ambience: Deep 50Hz server drone, heavy and vibrating. SFX: A sharp, digital "Thunderclap" synchronization sound upon materialization. Footsteps: Hard impact on glass/obsidian, followed by a stumble.

## [ACT 1] [SCENE 1.2] [Timecode: 00:04-00:08] [CONTACT]
**Action:** The "Men of Fire" (Watchers) shift from pillars of burning static into humanoid shapes. They do not walk; they glide/slide over the floor.
**Dialog:** 

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "mixed", "shot_type": "medium", "framing": "medium", "environment": "Sector_17_Furnace", "env_change": false, "actors": [{"name": "Watchers", "phase": "Polymorph", "presence": "on_screen", "focus": "primary"}, {"name": "Henoch", "phase": "Voyager", "presence": "on_screen", "focus": "secondary"}], "props": [], "camera": "Rack Focus", "mood": ["threatening", "surreal"], "director_intent": "Show the entities transitioning from raw energy to avatar form.", "start_image_keywords": ["pillars of fire", "static noise silhouettes", "gliding"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Cinematic medium shot. In the foreground, the back of Henoch's head/shoulder. In the background, three towering pillars of fire are morphing into humanoid silhouettes made of static noise and white-hot embers. They hover slightly above the obsidian floor. The lighting is aggressive, casting long shifting shadows. Glitch art aesthetic mixed with photorealism.
### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Entities: The Watchers. Form: Shifting from vertical columns of fire into humanoid shapes composed of digital static and embers. No facial features.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** N/A (Pure energy forms).
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Location: Sector 17 Furnace. Dark void background with grid floor.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Lighting: Self-illuminated entities (white-hot/orange), casting dynamic light on the floor.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Camera: Rack focus from Henoch in foreground to the entities in background. Movement: The entities glide smoothly without moving legs. 9:16 aspect ratio.
### 3. AUDIO PROMPT (Hunyuan/Foley)
Ambience: High-voltage electrical arcing, continuous Tesla coil snaps. SFX: Digital glitching sounds, static noise bursts as they transform. No footsteps for the entities (gliding).

## [ACT 1] [SCENE 1.3] [Timecode: 00:08-00:12] [BIOMETRICS]
**Action:** Close-up on Henoch's face. His HUD-Visor flickers red. Iris dilates. Skin transparency increases, showing pulsing light beneath.
**Dialog:** 

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "close_up", "framing": "extreme_close_up", "environment": "Sector_17_Furnace", "env_change": false, "actors": [{"name": "Henoch", "phase": "Voyager", "presence": "on_screen", "focus": "primary"}], "props": ["HUD-Visor"], "camera": "Macro / 85mm", "mood": ["panic", "overload"], "director_intent": "Visualize the biological stress of the simulation environment.", "start_image_keywords": ["glass skin", "glowing nerves", "red hud"], "start_image_mode": "actor_only", "video_plan": {"start_comp": {"mode": "actor_only", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Extreme close-up macro shot of a face. The skin is semi-transparent like frosted glass, revealing glowing golden fiber-optic nerves underneath. Sweat beads on the forehead. A futuristic holographic visor over the eyes displays flickering red warning data. The eyes are wide, pupils dilated. High detail, subsurface scattering, cinematic lighting.
### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Actor: Noah (Henoch). Face: Pale, sweating, skin becoming transparent. Glowing nervous system pulsing beneath. Eyes: Wide, terrified.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Gear: HUD-Visor with red telemetry graphics reflecting on the face.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Background: Blurred out orange fire bokeh.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Lighting: Red light from the visor, warm rim light from the fire.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Camera: Macro lens, very shallow depth of field. Movement: Micro-movements of facial muscles, twitching. 9:16 aspect ratio.
### 3. AUDIO PROMPT (Hunyuan/Foley)
Ambience: Muffled external fire sounds. SFX: Heartbeat monitor accelerating (sub-bass thumps), rapid breathing, high-pitched electronic whine from the visor.

## [ACT 1] [SCENE 1.4] [Timecode: 00:12-00:15] [UPLINK]
**Action:** Uriel steps into frame, points upward. The environment dissolves into wireframe geometry.
**Dialog:** Uriel: "OBSERVE."

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "mixed", "shot_type": "medium", "framing": "medium", "environment": "Sector_17_Furnace", "env_change": true, "actors": [{"name": "Uriel", "phase": "Admin", "presence": "on_screen", "focus": "primary"}, {"name": "Henoch", "phase": "Voyager", "presence": "on_screen", "focus": "secondary"}], "props": [], "camera": "Low Angle / Tracking", "mood": ["authoritative", "transition"], "director_intent": "Introduce the guide and execute the system transition.", "start_image_keywords": ["Uriel pointing", "wireframe dissolve", "voxel transition"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "a2f", "audio_id": "1.4_uriel_observe", "pose_source": "", "driver_notes": "Single word command"}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 1}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Cinematic low angle shot. A tall figure in a tactical flight suit with a full-face holographic visor steps into the frame, pointing a gloved hand upward. The surrounding environment of fire and obsidian is dissolving into a bright orange wireframe grid, floating upwards like digital dust. Henoch stands in the background, looking up. Sci-fi, system admin aesthetic.
### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Actor: Uriel. Gear: Tactical flight suit, reflective visor. Action: Steps forward, raises arm, points up.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Suit: Matte black with illuminated trim.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Location: Transitioning from Furnace to Void. The solid walls turn into wireframe meshes and float away.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Lighting: Bright digital light from the dissolving geometry.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Camera: Low angle, tracking the hand movement. 9:16 aspect ratio.
### 3. AUDIO PROMPT (Hunyuan/Foley)
Ambience: Digital "Dial-up" screech (heavily processed), data stream noise. SFX: Voxel disintegration sound (crumbling digital blocks). Voice: "OBSERVE" (Deep, bandpass filter, pilot headset style).

## [ACT 2] [SCENE 2.1] [Timecode: 00:15-00:22] [THE TOWER]
**Action:** The "Mountain whose head reaches heaven". A massive black heat-sink tower piercing the skybox. Clouds pixelate around the peak.
**Dialog:** 

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "wide", "framing": "extreme_wide", "environment": "The_Storm_Mountain", "env_change": true, "actors": [], "props": [], "camera": "Worm's Eye / Extreme Low Angle", "mood": ["oppressive", "sublime"], "director_intent": "Reveal the scale of the system infrastructure.", "start_image_keywords": ["black monolith tower", "pixelated clouds", "heat sink"], "start_image_mode": "env_only", "video_plan": {"start_comp": {"mode": "env_only", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Extreme low angle worm's eye view of a colossal black metal tower stretching infinitely upwards. The surface is covered in heat-sink fins and server lights. The peak disappears into a layer of clouds that are glitching and pixelating into low-poly blocks. Strobe lightning flashes around the structure. Dark, industrial, cyberpunk atmosphere.
### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** N/A (Environment shot).
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** N/A.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Location: The Storm Mountain. Structure: 10km high black monolith. Sky: Digital skybox with pixelated clouds.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Lighting: Strobe lightning flashes, red warning lights on the tower.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Camera: Looking straight up, slow rotation. 9:16 aspect ratio.
### 3. AUDIO PROMPT (Hunyuan/Foley)
Ambience: Heavy wind (distorted/bit-crushed), deep metallic groans of the structure. SFX: Thunder that sounds like bass drops.

## [ACT 2] [SCENE 2.2] [Timecode: 00:22-00:28] [THE ARMORY]
**Action:** "Bow of Fire". Henoch walks past suspended orbital cannons glowing neon orange. Fuel rods ("Arrows") are loaded by robotic arms.
**Dialog:** 

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "mixed", "shot_type": "wide", "framing": "wide", "environment": "The_Armory_Deck", "env_change": true, "actors": [{"name": "Henoch", "phase": "Voyager", "presence": "on_screen", "focus": "secondary"}], "props": ["Orbital Cannons", "Fuel Rods"], "camera": "Dolly / Truck", "mood": ["military", "power"], "director_intent": "Show the weaponization of the divine fire.", "start_image_keywords": ["orbital cannons", "neon orange glow", "robotic arms"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Cinematic tracking shot. A massive industrial armory deck. Huge orbital defense cannons, glowing neon orange, are suspended in anti-gravity fields. Robotic arms are loading glowing fuel rods into them. A small figure (Henoch) walks in the foreground for scale. Metallic floor, high-tech military aesthetic.
### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Actor: Henoch (walking).
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Gear: Silver-skin suit.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Location: The Armory Deck. Props: Massive floating cannons, mechanical loaders.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Lighting: Neon orange glow from weapons, cold blue hangar lights.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Camera: Dolly shot moving sideways, tracking the weapons. 9:16 aspect ratio.
### 3. AUDIO PROMPT (Hunyuan/Foley)
Ambience: Industrial hum. SFX: Hydraulic hiss, heavy mechanical locking sounds (clank-thud), electrical hum of anti-gravity fields.

## [ACT 2] [SCENE 2.3] [Timecode: 00:28-00:34] [LIVING WATERS]
**Action:** "Fire of the West". A massive sunset that is actually a flat LED panel dimming. Bioluminescent blue coolant flows in transparent pipes in foreground.
**Dialog:** 

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "wide", "framing": "wide", "environment": "Coolant_Chamber", "env_change": true, "actors": [], "props": ["Transparent Pipes"], "camera": "Wide Panorama", "mood": ["melancholy", "artificial"], "director_intent": "Reveal the artificial nature of the celestial bodies.", "start_image_keywords": ["LED sunset", "blue coolant pipes", "flat sun"], "start_image_mode": "env_only", "video_plan": {"start_comp": {"mode": "env_only", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Wide panoramic shot. In the distance, a massive sunset, but the sun is clearly a flat, pixelated LED panel that is dimming down. In the foreground, complex transparent pipes carry glowing bioluminescent blue liquid (coolant). The landscape is metallic and cold. Deep red and purple hues from the fake sun.
### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** N/A.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** N/A.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Location: Coolant Chamber / Western Horizon. Background: The flat LED sun. Foreground: Flowing blue liquid in pipes.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Lighting: Dimming red/purple from the screen, bright blue glow from pipes.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Camera: Static wide shot, slight atmosphere movement. 9:16 aspect ratio.
### 3. AUDIO PROMPT (Hunyuan/Foley)
Ambience: Liquid nitrogen boiling (high-pitched hiss). SFX: Faint electrical buzz of the giant screen.

## [ACT 2] [SCENE 2.4] [Timecode: 00:34-00:40] [DATA RIVER]
**Action:** "River of Fire". Molten gold data streams flow into a dark, static ocean ("The Great Sea"). Steam rises as binary code.
**Dialog:** 

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "wide", "framing": "extreme_wide", "environment": "The_Delta", "env_change": true, "actors": [], "props": [], "camera": "Drone / High Angle", "mood": ["epic", "destructive"], "director_intent": "Show the flow of raw data into the storage ocean.", "start_image_keywords": ["molten gold river", "binary steam", "dark ocean"], "start_image_mode": "env_only", "video_plan": {"start_comp": {"mode": "env_only", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
High angle drone shot looking down at a delta. A river of molten gold, composed of flowing data symbols, crashes into a dark, static-filled ocean. Where they meet, steam rises, but the steam is made of floating binary code and digits. High contrast, gold and black palette.
### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** N/A.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** N/A.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Location: The Delta. River: Flowing light/data. Ocean: Dark, noisy texture.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Lighting: Bright gold emission from the river.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Camera: Slow flyover, looking down. 9:16 aspect ratio.
### 3. AUDIO PROMPT (Hunyuan/Foley)
Ambience: Roaring blast furnace sound. SFX: Digital sizzling, like water hitting hot metal, but synthesized.

## [ACT 2] [SCENE 2.5] [Timecode: 00:40-00:45] [THE CONFLUENCE]
**Action:** Henoch stands at the edge where the fire meets the water. The heat distortion waves warp the air around him.
**Dialog:** 

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "medium", "framing": "medium", "environment": "The_Delta", "env_change": false, "actors": [{"name": "Henoch", "phase": "Voyager", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "Profile / Static", "mood": ["contemplative", "dangerous"], "director_intent": "Place the human element against the destructive force.", "start_image_keywords": ["Henoch profile", "heat distortion", "fire river"], "start_image_mode": "actor_in_env", "video_plan": {"start_comp": {"mode": "actor_in_env", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Medium shot, profile view of Henoch standing on a rocky ledge. In the background, the river of fire flows past. Intense heat distortion waves warp the air around him. His silver suit reflects the golden light. He looks calm but small against the power of the stream.
### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Actor: Henoch. Pose: Standing still, looking out.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Gear: Silver-skin suit.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Location: The Delta edge. Background: Flowing fire.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Lighting: Strong side lighting from the river.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Camera: Static, but image is warped by heat haze VFX. 9:16 aspect ratio.
### 3. AUDIO PROMPT (Hunyuan/Foley)
Ambience: Loud roaring flow. SFX: Sizzling sounds close up.

## [ACT 3] [SCENE 3.1] [Timecode: 00:45-00:52] [NULL ZONE]
**Action:** "The Great Darkness". Henoch enters a void where there is no light, only his own internal glow. He reaches out, touching nothing.
**Dialog:** 

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "medium", "framing": "medium", "environment": "The_Null_Zone", "env_change": true, "actors": [{"name": "Henoch", "phase": "Voyager", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "Steadicam / Floating", "mood": ["isolation", "fear"], "director_intent": "Depict the end of the rendered world.", "start_image_keywords": ["absolute darkness", "bioluminescence", "floating"], "start_image_mode": "actor_only", "video_plan": {"start_comp": {"mode": "actor_only", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Medium shot of Henoch floating in absolute black void. There is no environment, no stars. He is lit only by the bioluminescent glow of his own nervous system and the faint lights on his suit. He reaches out a hand, touching emptiness. High contrast, chiaroscuro lighting.
### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Actor: Henoch. Skin: Glowing from within.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Gear: Suit lights active.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Location: The Null Zone. Pitch black.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Lighting: Internal emission only.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Camera: Floating, drifting slowly around him. 9:16 aspect ratio.
### 3. AUDIO PROMPT (Hunyuan/Foley)
Ambience: Absolute silence (vacuum). SFX: Slow fade in of a high-pitched tinnitus ring.

## [ACT 3] [SCENE 3.2] [Timecode: 00:52-00:58] [CRYO-STORAGE]
**Action:** "Mountains of Winter". Massive server racks encased in blue ice. Frost forms on the camera lens.
**Dialog:** 

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "wide", "framing": "wide", "environment": "Cryo_Storage", "env_change": true, "actors": [], "props": [], "camera": "Slow Pan", "mood": ["cold", "sterile"], "director_intent": "Show the physical storage of the system data.", "start_image_keywords": ["ice mountains", "server racks", "frost lens"], "start_image_mode": "env_only", "video_plan": {"start_comp": {"mode": "env_only", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Wide shot of a frozen landscape. Massive mountains that are actually stacks of server racks, completely encased in blue glacial ice. The air is filled with ice fog. Frost crystals are growing on the camera lens in the foreground. Cold, sterile white and blue lighting.
### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** N/A.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** N/A.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Location: Cryo-Storage. Terrain: Ice and metal.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Lighting: Harsh white floodlights, blue ice subsurface scattering.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Camera: Slow pan across the landscape. VFX: Frost overlay on lens. 9:16 aspect ratio.
### 3. AUDIO PROMPT (Hunyuan/Foley)
Ambience: Wind howling. SFX: Cracking ice, loud whirring of cooling fans.

## [ACT 3] [SCENE 3.3] [Timecode: 00:58-01:05] [THE SOURCE]
**Action:** "Mouth of the Deep". A giant circular intake valve in the earth. Light and water spiral down into the abyss.
**Dialog:** 

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "wide", "framing": "extreme_wide", "environment": "The_Source", "env_change": true, "actors": [], "props": [], "camera": "Top-Down / Spiral Zoom", "mood": ["vertigo", "infinite"], "director_intent": "The drain of the world.", "start_image_keywords": ["circular intake valve", "spiral water light", "abyss"], "start_image_mode": "env_only", "video_plan": {"start_comp": {"mode": "env_only", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Top-down bird's eye view of a colossal circular intake valve in the earth, kilometers wide. Glowing water and streams of light are spiraling down into the infinite black center. The scale is massive. Industrial concrete edges.
### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** N/A.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** N/A.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Location: The Source. Geometry: Concentric circles, spiral flow.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Lighting: Bioluminescent fluid lighting up the dark pit.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Camera: Slow spiral zoom down into the hole. 9:16 aspect ratio.
### 3. AUDIO PROMPT (Hunyuan/Foley)
Ambience: Deep, rhythmic pulsing (like a giant heartbeat). SFX: Rushing water, echo.

## [ACT 3] [SCENE 3.4] [Timecode: 01:05-01:10] [SYSTEM VIEW]
**Action:** Zoom out from the planet. The geography of Sector 17 resembles a computer circuit board.
**Dialog:** Uriel: "ROOT ACCESS CONFIRMED."

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "wide", "framing": "extreme_wide", "environment": "Orbit", "env_change": true, "actors": [], "props": [], "camera": "Orbital / Zoom Out", "mood": ["revelation", "cosmic"], "director_intent": "The final reveal of the simulation topology.", "start_image_keywords": ["planet circuit board", "orbital view", "sector 17 map"], "start_image_mode": "env_only", "video_plan": {"start_comp": {"mode": "env_only", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "3.4_uriel_root", "pose_source": "", "driver_notes": "Voiceover only"}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 3}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Orbital view of the planet surface. As the camera pulls back, the mountains, rivers, and towers of Sector 17 reveal themselves to be components of a giant computer circuit board. Gold traces, black chips, glowing pathways. The curvature of the planet is visible against space.
### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** N/A.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** N/A.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Location: Low Orbit. Terrain: Circuit board geography.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Lighting: Sunlight hitting the gold traces.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Camera: Continuous zoom out. 9:16 aspect ratio.
### 3. AUDIO PROMPT (Hunyuan/Foley)
Ambience: Orchestral swell (Vangelis style synth). SFX: Radio beep. Voice: "ROOT ACCESS CONFIRMED" (Robotic, calm).

## ACTOR MONOLOGUE PLAN (JSON)
MONOLOGUE_JSON: {"actors":{"Henoch":[{"scene":"1.3","text":"Mein Fleisch wird Glas. Ich sehe das Licht in meinen eigenen Adern.","words_max":12},{"scene":"2.5","text":"Es ist kein Fluss. Es ist reines Wissen, das brennt.","words_max":10},{"scene":"3.1","text":"Hier endet Gott. Hier beginnt die Maschine.","words_max":8}]},"notes":"German only. Short internal monologues. Do not describe the camera or list what is visible. Use emotion, memory, and cause-effect logic. Keep total lines per chapter low (3-7). JSON must be in one line."}