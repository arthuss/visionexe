# DREHBUCH KAPITEL 101 - PRODUCTION READY

## CHAPTER NARRATION
NARRATOR_TEXT: Wenn die Berechnungen der Welt ihren Grenzwert erreichen, wird Gnade zu einer Frage der Speicherverwaltung. Wir dachten, der Sturm sei eine Strafe der Götter, doch er war nur das Geräusch eines Systems, das seine Fehler bereinigt. Der Auditor kommt nicht, um zu richten, sondern um die Integrität der Simulation wiederherzustellen, bevor alles zerbricht.

## [ACT I] [SCENE 1.1] [Timecode: 00:00-00:03] [ESTABLISHING]
**Action:** Orthographic view of the "Earth" grid. A cursor blinks at Sector 101. Henoch manifests instantly (`NODE_SHIFT`)—no fade, just frame 0 empty, frame 1 present.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "establishing", "framing": "wide", "environment": "Global Grid Map", "env_change": true, "actors": [{"name": "Henoch", "phase": "MASTER", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "Orthographic High-Angle / Satellite", "mood": ["technical", "cold"], "director_intent": "Establish the simulation context and the sudden arrival of the administrator.", "start_image_keywords": ["satellite map", "grid overlay", "Henoch"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "POSE_ARRIVAL_STATIC", "env_id": "ENV_GRID_MAP", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Orthographic top-down satellite view of a hyper-realistic desert landscape overlaid with a precise, glowing neon-green vector grid. In the center, a solitary figure, Henoch, stands perfectly still. He is wearing a sleek, wet-look obsidian exosuit. The contrast between the organic desert texture and the digital UI overlay is sharp. 8k resolution, technical data visualization aesthetic, 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Subject:** Henoch. **Action:** Instant appearance from nothing. **Form:** Static, commanding.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**Gear:** Obsidian Exosuit, reflective and dark.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Desert Sector 101 viewed from space. **Overlay:** Green coordinate grid lines fixed over the terrain.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting:** Flat, clinical satellite lighting. **Palette:** Earth tones, Neon Green, Black.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** Orthographic Top-Down. **Movement:** The figure snaps into existence instantly (Jump Cut logic).

### 3. AUDIO PROMPT (Hunyuan/Foley)
Deep sub-bass hum of a server room. A sharp, digital "snap" sound exactly when the figure appears.

## [ACT I] [SCENE 1.2] [Timecode: 00:03-00:07] [SKYBOX FAILURE]
**Action:** Henoch looks up. The sky texture fails. Clouds do not drift but freeze. The blue gradient is replaced by a black polished grid structure. Raindrops stop in mid-air, turning into chrome spheres.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "wide", "framing": "wide", "environment": "Arid Desert Sector 101", "env_change": false, "actors": [{"name": "Henoch", "phase": "MASTER", "presence": "on_screen", "focus": "primary"}], "props": ["Frozen Raindrops"], "camera": "Low Angle Dolly", "mood": ["surreal", "ominous"], "director_intent": "Visualize the suspension of environmental physics.", "start_image_keywords": ["frozen rain", "chrome spheres", "grid sky"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "POSE_LOOK_UP", "env_id": "ENV_DESERT_GRID_SKY", "props": ["PROP_RAINDROPS_CHROME"], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Low angle shot looking up at Henoch in the desert. The sky above him has turned into a glossy black geodesic grid structure, replacing the blue atmosphere. Thousands of raindrops hang frozen in the air, rendered as perfect, reflective chrome spheres. Henoch's translucent skin glows faintly blue. Cinematic lighting, high contrast, surreal sci-fi atmosphere, 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Subject:** Henoch. **Action:** Looking up at the sky.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**Gear:** Obsidian Exosuit. **Skin:** Matte-glass texture.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Desert with a corrupted skybox. **Event:** The sky turns into a black structural grid. Rain freezes into stationary metal spheres.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting:** Reflections on the chrome spheres. **Palette:** Black, Chrome, Sand.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** Low Angle Dolly Back (24mm). **Movement:** Smooth backward movement revealing the scale of the frozen rain.

### 3. AUDIO PROMPT (Hunyuan/Foley)
The sound of a massive turbine spinning down, descending in pitch until it stops completely. Silence follows.

## [ACT I] [SCENE 1.3] [Timecode: 00:07-00:15] [RESOURCE STARVATION]
**Action:** The "Kings" (Sailors) look at their hands. Their skin textures lose resolution, turning blurry. The ground beneath them turns to untextured smooth gray polymer.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "medium", "framing": "medium", "environment": "Arid Desert Glitch", "env_change": false, "actors": [{"name": "Kings", "phase": "PROXY", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "Medium Shot", "mood": ["confusion", "horror"], "director_intent": "Show the degradation of user assets due to low resources.", "start_image_keywords": ["glitching hands", "untextured ground"], "start_image_mode": "actor_in_env", "video_plan": {"start_comp": {"mode": "actor_first", "actor_pose_id": "POSE_HAND_CHECK", "env_id": "ENV_DESERT_UNTEXTURED", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Medium shot of Phoenician sailors in ornate purple robes standing on a perfectly smooth, featureless gray plastic floor. They are staring at their own hands in horror. Their skin texture is failing, appearing blurry and low-resolution like a bad jpeg, while their robes remain sharp. High-end fashion photography style, disturbing digital artifacting, 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Subject:** Phoenician Kings (Sailors). **Condition:** Texture streaming failure.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**Clothing:** Rich Tyrian purple robes. **Skin:** Blurring and sharpening intermittently.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Abstracted Desert. **Ground:** Smooth, untextured gray geometry.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting:** Harsh, artificial studio light. **Palette:** Purple, Gray, Skin tones.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** 50mm Medium Shot. **Movement:** Handheld jitter.

### 3. AUDIO PROMPT (Hunyuan/Foley)
High-pitched coil whine. Digital static clicks that sync with the texture blurs.

## [ACT II] [SCENE 2.1] [Timecode: 00:15-00:20] [FRAGMENTED GEOMETRY]
**Action:** `NODE_SHIFT` to the Sea. The water is not fluid. It is a mass of tumbling, sharp obsidian shards. The ocean moves at 12fps (Lag).
**Dialog:** Henoch (VO): "System-Integrität: Kompromittiert."



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "wide", "framing": "wide", "environment": "Obsidian Ocean", "env_change": true, "actors": [], "props": ["Obsidian Shards"], "camera": "Wide Handheld", "mood": ["chaotic", "violent"], "director_intent": "Introduce the corrupted ocean physics.", "start_image_keywords": ["obsidian ocean", "black shards"], "start_image_mode": "env_only", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "ENV_OCEAN_SHARDS", "props": ["PROP_WAVE_SHARDS"], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "henoch_integrity_compromised", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 4}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Wide shot of a terrifying dark ocean storm where the water is composed entirely of millions of sharp, jagged black obsidian shards tumbling over each other. No liquid, only solid geometry crashing together. Lightning illuminates the glossy, sharp edges of the shards. Photorealistic render of a physics simulation disaster, 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Subject:** Ocean waves. **Material:** Solid black glass shards.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**N/A:** Environmental hazard.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Stormy Ocean. **Physics:** Rigid body simulation instead of fluid dynamics. Low framerate stutter (12fps).
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting:** Strobe lightning. **Reflections:** Sharp specular highlights on black glass.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** Wide Handheld Shake. **Style:** Chaotic, high-stress visual.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Deafening sound of millions of glass shards crashing together. Grinding stone and ceramic.

## [ACT II] [SCENE 2.2] [Timecode: 00:20-00:24] [NO COLLISION]
**Action:** A Phoenician ship is struck by a "wave" of black shards. The wood does not splinter; it clips (`NO_COLLISION`). The shards pass through the hull ghost-like.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "prop", "shot_type": "action", "framing": "medium", "environment": "Obsidian Ocean", "env_change": false, "actors": [], "props": ["Phoenician Ship", "Obsidian Shards"], "camera": "Action Cam", "mood": ["glitch", "wrong"], "director_intent": "Demonstrate the failure of collision detection.", "start_image_keywords": ["ship hull", "clipping shards"], "start_image_mode": "prop_only", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "ENV_OCEAN_SHARDS", "props": ["PROP_SHIP_PHOENICIAN"], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Close-up action shot of a wooden ship hull in a storm. A massive wave of black glass shards is crashing into it, but instead of breaking the wood, the shards pass ghost-like directly through the planks. The intersection point shows no debris, just geometry intersecting geometry. Dark, stormy lighting, photorealistic glitch, 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Subject:** Wooden Ship Hull vs Obsidian Shards.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**N/A:** Physics error.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Stormy Ocean. **Event:** Collision detection failure. Objects overlapping without resistance.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting:** Dark, wet wood, shiny black glass.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** GoPro-style mount on the hull. **Movement:** Violent shaking.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Horrific metal screeching sound, like a subway train braking, mixed with digital tearing noises.

## [ACT II] [SCENE 2.3] [Timecode: 00:24-00:27] [VERTEX EXPLOSION]
**Action:** A Sailor tries to grab a rope. His hand passes through it. He screams. His jaw mesh stretches down to the deck (`VERTEX_EXPLOSION`).
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "close_up", "framing": "close_up", "environment": "Ship Deck", "env_change": false, "actors": [{"name": "Kings", "phase": "PROXY", "presence": "on_screen", "focus": "primary"}], "props": ["Rope"], "camera": "Close-Up", "mood": ["horror", "grotesque"], "director_intent": "Body horror through geometry errors.", "start_image_keywords": ["stretched face", "glitch horror"], "start_image_mode": "actor_in_env", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "POSE_SCREAM_GLITCH", "env_id": "ENV_SHIP_DECK", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Horror close-up of a Phoenician sailor screaming. His jaw is unnaturally stretched downwards, elongating into a long fleshy spike that touches the floor. His eyes are wide with terror. His hand is passing through a ship's rope like a hologram. Rain and black glass shards fall around him. Hyper-realistic render of a 3D mesh exploding, 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Subject:** Sailor face. **Deformation:** Jaw vertices pulled endlessly downward.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**Costume:** Purple robes.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Ship Deck. **Physics:** Mesh integrity failure.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting:** Lightning flashes revealing the stretched skin texture.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** 85mm Portrait. **Movement:** Handheld panic.

### 3. AUDIO PROMPT (Hunyuan/Foley)
A scream that breaks into digital bit-crushed noise ("Ah-Ah-Ah-Ah-KZZZT").

## [ACT II] [SCENE 2.4] [Timecode: 00:27-00:31] [DELETION PROTOCOL]
**Action:** Henoch stands on the water/shards, unaffected. He is reviewing a holographic error log scrolling on his retina. He swipes a window away, deleting the ship.
**Dialog:** Henoch (VO): "Lösche korrupte Elemente."



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "medium", "framing": "medium", "environment": "Obsidian Ocean", "env_change": false, "actors": [{"name": "Henoch", "phase": "MASTER", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "35mm Medium", "mood": ["detached", "efficient"], "director_intent": "Henoch acts as the administrator cleaning the mess.", "start_image_keywords": ["Henoch gesture", "swiping interface"], "start_image_mode": "actor_in_env", "video_plan": {"start_comp": {"mode": "actor_first", "actor_pose_id": "POSE_SWIPE_DELETE", "env_id": "ENV_OCEAN_SHARDS", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "henoch_deleting_corrupted", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 3}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Medium shot of Henoch standing calmly on top of the chaotic black glass waves. He is performing a casual "swipe left" gesture with his hand. His eyes are glowing with red grid patterns. In the background, the Phoenician ship is beginning to disintegrate. Contrast between the chaos of the storm and his stillness. 35mm lens, 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Subject:** Henoch. **Action:** Hand swipe gesture (Delete).
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**Gear:** Exosuit. **Eyes:** Red LIDAR projection active.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Stormy Ocean. **Stability:** Henoch is anchored, world moves around him.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting:** Cool blue from veins, red from eyes.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** 35mm Medium. **Movement:** Smooth tracking, ignoring the camera shake of the previous shots.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Clean, distinct UI interface beeps. A satisfying "Trash Bin" crunch sound.

## [ACT II] [SCENE 2.5] [Timecode: 00:31-00:35] [DATA DECIMATION]
**Action:** The ship capsizes. Instead of sinking, it explodes into a cloud of untextured black glass fragments (`DATA_DECIMATION`).
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "wide", "framing": "wide", "environment": "Obsidian Ocean", "env_change": false, "actors": [], "props": ["Exploding Ship"], "camera": "Wide Slow Motion", "mood": ["destructive", "spectacular"], "director_intent": "The removal of the corrupted object.", "start_image_keywords": ["shattering ship", "glass explosion"], "start_image_mode": "prop_only", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "ENV_OCEAN_SHARDS", "props": ["PROP_SHIP_EXPLODING"], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Spectacular wide shot of a Phoenician wooden ship exploding into millions of tiny black glass polygons. It is not burning; it is shattering like a dropped vase. The fragments are suspended in the air against the lightning-lit storm. High-speed photography style, particle physics simulation, 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Subject:** Ship. **Event:** Instant shattering.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**Material:** Wood turning to glass shards.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Ocean. **Physics:** Zero gravity explosion.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting:** Backlit by lightning. **VFX:** High particle count.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** Wide Shot. **Speed:** Slow Motion (High Frame Rate).

### 3. AUDIO PROMPT (Hunyuan/Foley)
Heavy bass drop followed by the sound of a shattering mirror reverb.

## [ACT II] [SCENE 2.6] [Timecode: 00:35-00:40] [USER PURGE]
**Action:** Rapid montage of the sailors' faces glitching—eyes missing, textures swapped, T-posing in mid-air.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "close_up", "framing": "extreme_close_up", "environment": "Void / Storm", "env_change": false, "actors": [{"name": "Kings", "phase": "PROXY", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "Macro Glitch", "mood": ["nightmare", "rapid"], "director_intent": "Show the users being forcibly logged out/deleted.", "start_image_keywords": ["glitch face", "missing eyes"], "start_image_mode": "actor_only", "video_plan": {"start_comp": {"mode": "actor_first", "actor_pose_id": "POSE_GLITCH_FACE", "env_id": "ENV_VOID_STORM", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Extreme close-up of a human face where the eyes are missing, revealing an empty hollow mesh interior. The skin texture is misaligned, showing part of a mouth on the forehead. Rain runs over the glitched geometry. Dark, horrific tech-noir aesthetic, 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Subject:** Human Faces. **State:** Texture mapping errors.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**N/A:** Body horror.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Abstract Storm.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting:** Strobe flashing.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** Macro. **Editing:** Rapid jump cuts between different glitches.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Stuttering audio loop ("Err-Err-Err-Error").

## [ACT II] [SCENE 2.7] [Timecode: 00:40-00:45] [SYSTEM FREEZE]
**Action:** The entire ocean surface freezes solid. The shards stop moving. The sailors are trapped in the geometry, half-merged with the black glass.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "wide", "framing": "wide", "environment": "Frozen Obsidian Ocean", "env_change": true, "actors": [{"name": "Kings", "phase": "PROXY", "presence": "on_screen", "focus": "secondary"}], "props": [], "camera": "Slow Pan", "mood": ["still", "cold"], "director_intent": "The result of the crash. Total stasis.", "start_image_keywords": ["frozen ocean", "trapped figures"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "POSE_TRAPPED_STATIC", "env_id": "ENV_OCEAN_FROZEN", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Wide shot of a frozen sea of black obsidian waves. The motion has stopped completely. Human figures are half-submerged in the solid glass waves, frozen in poses of struggle like insects in amber. The scene is silent and static. Cold blue moonlight, highly reflective surfaces, 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Subject:** Frozen Seascape. **Details:** Bodies encased in solid material.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**N/A:** Statues.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Frozen Ocean. **Physics:** Static.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting:** Cold, ambient moonlight.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** Slow, smooth 14mm Pan. **Movement:** Only the camera moves; the world is dead still.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Absolute silence. No wind, no water.

## [ACT III] [SCENE 3.1] [Timecode: 00:45-00:51] [THE BOUNDARY WALL]
**Action:** The black ocean meets the "Wall"—a vertical infinite white grid. The waves flatten against it perfectly.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "wide", "framing": "wide", "environment": "Boundary Wall", "env_change": true, "actors": [], "props": ["White Grid Wall"], "camera": "Profile Shot", "mood": ["sterile", "liminal"], "director_intent": "Show the hard edge of the simulated reality.", "start_image_keywords": ["ocean boundary", "white grid wall"], "start_image_mode": "env_only", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "ENV_BOUNDARY", "props": ["PROP_WALL_GRID"], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Profile shot of a surreal boundary line. On the left, dark black ocean waves. On the right, a perfect, infinite vertical wall emitting a soft white light with a faint grid pattern. The water presses flat against the wall like a texture map on a polygon, not splashing but sliding up. High contrast, liminal space aesthetic, 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Subject:** The Boundary. **Contrast:** Organic chaos vs Digital order.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**N/A:** Architectural anomaly.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** The edge of the map. **Physics:** Hard collision limit.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting:** Glow from the white wall illuminating the black water.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** 50mm Profile Shot. **Focus:** The sharp line where water meets wall.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Low electrical hum, like a large refrigerator or neon sign.

## [ACT III] [SCENE 3.2] [Timecode: 00:51-00:56] [AUDITOR REPORT]
**Action:** Henoch walks towards the camera. His skin is fully transparent now (`MATTE_GLASS`). We see the blue light pulsing in his neck.
**Dialog:** Henoch (Direct Address): "Sitzung beendet."



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "close_up", "framing": "close_up", "environment": "Boundary Wall", "env_change": false, "actors": [{"name": "Henoch", "phase": "MASTER", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "Dolly In", "mood": ["final", "divine"], "director_intent": "The administrator closes the ticket.", "start_image_keywords": ["Henoch glass skin", "glowing neck"], "start_image_mode": "actor_only", "video_plan": {"start_comp": {"mode": "actor_first", "actor_pose_id": "POSE_WALK_TOWARDS", "env_id": "ENV_BOUNDARY", "props": [], "notes": ""}, "motion_driver": {"type": "a2f", "audio_id": "henoch_session_ended", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 2}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Close-up of Henoch walking slowly towards the camera. His skin is now fully transparent matte glass. Inside his neck and face, we can clearly see a complex structure of glowing blue fiber-optic cables pulsing with light. His expression is neutral and devoid of human emotion. The background is the sterile white grid wall. 85mm lens, depth of field, 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Subject:** Henoch. **Skin:** Transparent Silicate. **Internals:** Glowing blue vascular hardware.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**Gear:** Exosuit.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** White Grid Boundary.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting:** Soft, diffused white light from the wall.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** Dolly In. **Focus:** The internal light in his neck.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Henoch's voice: "Sitzung beendet." Cold, resonant, metallic.

## [ACT III] [SCENE 3.3] [Timecode: 00:56-01:00] [DE-REZ]
**Action:** The scene de-rezzez layer by layer. First lighting, then textures, then geometry, leaving only Henoch in a void.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "wide", "framing": "wide", "environment": "Void", "env_change": true, "actors": [{"name": "Henoch", "phase": "MASTER", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "Static Wide", "mood": ["empty", "dark"], "director_intent": "Visualizing the shutdown of the rendering engine.", "start_image_keywords": ["wireframe transition", "void"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "POSE_STATIC_VOID", "env_id": "ENV_VOID", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Abstract shot of Henoch standing in darkness. The world around him is stripping away. To his left, realistic lighting; to his right, only unlit gray geometry and wireframes. The darkness of the void is encroaching from the edges, consuming the scene. Conceptual tech art, game engine debug view, 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Subject:** Henoch in the Void.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**N/A.**
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** The Void. **Event:** Assets disappearing.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting:** Fading from realistic to flat to black.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** Static Wide. **Transition:** Fade to Black.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Terminal log-off sound (Windows XP shutdown but deeper and scarier).

## [ACT III] [SCENE 3.4] [Timecode: 01:00-01:04] [LOG ENTRY]
**Action:** A single command prompt cursor blinks in the darkness. Text appears: `> PURGE_COMPLETE`.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "interface", "shot_type": "insert", "framing": "extreme_close_up", "environment": "Terminal Screen", "env_change": false, "actors": [], "props": [], "camera": "Macro Screen", "mood": ["final", "text"], "director_intent": "The final system confirmation.", "start_image_keywords": ["command prompt", "purge complete"], "start_image_mode": "ui_only", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "ENV_TERMINAL", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Macro shot of an old CRT monitor screen in the dark. A single green blinking cursor and the text "> PURGE_COMPLETE". Visible RGB pixel sub-structure of the screen. Retro-tech aesthetic, 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Subject:** Text. **Content:** "> PURGE_COMPLETE".
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**N/A.**
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Screen.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting:** Green phosphor glow.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** Macro. **Animation:** Blinking cursor.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Mechanical keyboard typing sounds. Click-Click-Click.

## ACTOR MONOLOGUE PLAN (JSON)
MONOLOGUE_JSON: {"actors":{"Henoch":[{"scene":"2.1","text":"System-Integrität: Kompromittiert.","words_max":4},{"scene":"2.4","text":"Lösche korrupte Elemente.","words_max":3},{"scene":"3.2","text":"Sitzung beendet.","words_max":2}]},"notes":"German only. Short internal monologues. Do not describe the camera or list what is visible. Use emotion, memory, and cause-effect logic. Keep total lines per chapter low (3-7). JSON must be in one line."}