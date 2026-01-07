# DREHBUCH KAPITEL 101 - PRODUCTION READY

## CHAPTER NARRATION
NARRATOR_TEXT: Wir hielten den Himmel für ein Dach, doch er war nur ein Bildschirm, dessen Pixel zu sterben begannen. Wenn der Administrator den Raum betritt, gefriert der Regen nicht durch Kälte, sondern weil die Zeit keine Rechenleistung mehr erhält. Wir sind keine Bewohner einer Welt, sondern Prozesse, die auf ihre Beendigung warten.

## [ACT I] [SCENE 1.1] [Timecode: 00:00-00:02] [KERNEL WAKE]
**Action:** Extreme Close-Up of Henoch's eye. It is not organic. The iris is a mechanical shutter that snaps open instantly.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "insert", "framing": "extreme_close_up", "environment": "Void", "env_change": true, "actors": [{"name": "Henoch", "phase": "MASTER", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "100mm Macro", "mood": ["technical", "alert"], "director_intent": "Establish Henoch as a machine-intelligence waking up.", "start_image_keywords": ["mechanical iris", "shutter eye", "macro"], "start_image_mode": "actor_only", "video_plan": {"start_comp": {"mode": "actor_first", "actor_pose_id": "POSE_EYE_OPEN", "env_id": "ENV_VOID", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Extreme macro shot of a synthetic eye opening. The iris is constructed of interlocking matte-black titanium aperture blades, similar to a camera lens. The pupil is a glowing red optical sensor displaying scrolling Ge'ez data streams. The skin around the eye is white ceramic with a flawless, poreless texture. High contrast, clinical lighting, 8k resolution, 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Subject:** Henoch's Eye. **Mechanism:** Mechanical aperture iris. **Action:** Snapping open instantly from black to wide.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**Skin:** White matte ceramic.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Abstract darkness.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting:** Internal red glow from the pupil sensor.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** 100mm Macro Lens. **Movement:** Static camera, rapid mechanical subject movement.

### 3. AUDIO PROMPT (Hunyuan/Foley)
A heavy, high-torque servo motor snap sound. High-pitched digital capacitor charging whine.

## [ACT I] [SCENE 1.2] [Timecode: 00:02-00:05] [TEXTURE FAILURE]
**Action:** Wide shot of the desert. The skybox fails to load. The blue atmosphere is replaced by a stark black-and-white checkerboard grid. The sun is a flat white untextured circle.
**Dialog:** Henoch: "Beobachte die Partition."



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "wide", "framing": "wide", "environment": "Desert Glitch", "env_change": true, "actors": [{"name": "Henoch", "phase": "MASTER", "presence": "on_screen", "focus": "secondary"}], "props": [], "camera": "14mm Low Angle", "mood": ["surreal", "ominous"], "director_intent": "Show the environment rendering failing.", "start_image_keywords": ["checkerboard sky", "untextured sun", "desert"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "POSE_OBSERVE_SKY", "env_id": "ENV_DESERT_GLITCH", "props": [], "notes": ""}, "motion_driver": {"type": "a2f", "audio_id": "henoch_partition_observe", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 3}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Wide low-angle shot of a hyper-realistic desert landscape. The sky above is broken; instead of blue, it is a massive, seamless black-and-white checkerboard pattern stretching to infinity. The sun is a perfect 2D white circle with no glow or flare. Henoch stands small in the foreground, looking up. The lighting is harsh and shadowless. 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Subject:** The Skybox. **State:** Texture streaming error.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**Henoch:** Tiny figure in distance, Obsidian Exosuit.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Arid Desert. **Sky:** Static checkerboard grid.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting:** Global illumination error (flat, uniform light).
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** 14mm Ultra Wide. **Movement:** Slow tilt up revealing the broken sky.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Deep, low-frequency 50Hz mains hum. The sound of a large ventilation fan spinning.

## [ACT I] [SCENE 1.3] [Timecode: 00:05-00:09] [PHYSICS PAUSE]
**Action:** Raindrops hang frozen in mid-air as perfect chrome spheres. Henoch walks through them, pushing them aside physically.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "medium", "framing": "medium", "environment": "Desert Glitch", "env_change": false, "actors": [{"name": "Henoch", "phase": "MASTER", "presence": "on_screen", "focus": "primary"}], "props": ["Chrome Spheres"], "camera": "35mm Tracking", "mood": ["quiet", "uncanny"], "director_intent": "Demonstrate the suspension of physics rules.", "start_image_keywords": ["frozen rain", "chrome spheres", "Henoch walking"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "actor_first", "actor_pose_id": "POSE_WALK_THROUGH_SPHERES", "env_id": "ENV_DESERT_GLITCH", "props": ["PROP_RAIN_SPHERES"], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Medium shot of Henoch walking through a field of suspended rain. The raindrops are not liquid but solid, highly polished chrome spheres floating motionless in the air. Henoch's ceramic hand gently brushes one aside, and it drifts away slowly in zero gravity. Reflections of the checkerboard sky are visible on the spheres. 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Subject:** Henoch. **Action:** Walking through static obstacles.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**Gear:** Exosuit. **Interaction:** Hand colliding with floating spheres.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Desert. **Atmosphere:** Filled with metallic spheres.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting:** Sharp reflections on chrome.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** 35mm Tracking Shot (Steadicam). **Movement:** Following Henoch smoothly.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Gentle metallic chimes or marbles clicking together as he touches them. No rain hiss.

## [ACT I] [SCENE 1.4] [Timecode: 00:09-00:13] [ASSET DECAY]
**Action:** Close up of a lush tree. It rapidly degrades: leaves vanish, bark turns to grey untextured mesh, then the whole structure dissolves into fine silica dust.
**Dialog:** Henoch: "Eingabe verweigert."



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "prop", "shot_type": "close_up", "framing": "close_up", "environment": "Desert Glitch", "env_change": false, "actors": [{"name": "Henoch", "phase": "MASTER", "presence": "off_screen", "focus": "secondary"}], "props": ["Tree"], "camera": "50mm Static", "mood": ["decay", "technological"], "director_intent": "Visualizing resource reclamation/deletion.", "start_image_keywords": ["tree decaying", "wireframe", "dust"], "start_image_mode": "prop_only", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "ENV_DESERT_GLITCH", "props": ["PROP_TREE_DECAY"], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "henoch_input_denied", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 2}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Close-up of an ancient olive tree. The image captures a split-second transition where the organic bark texture is stripping away to reveal a smooth, grey geometric underlying mesh. The leaves are dissolving into clouds of digital white dust particles. The lighting is cold and analytical. 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Subject:** Olive Tree. **Action:** Rapid disintegration.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**N/A.**
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Desert. **Process:** Texture unloading -> Mesh collapse -> Dust simulation.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting:** Flat white light.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** 50mm Static. **Time:** Time-lapse speed degradation.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Loud hard drive seek noise (crackle-click-click). The sound of sand pouring on metal.

## [ACT I] [SCENE 1.5] [Timecode: 00:13-00:18] [SYSTEM SCAN]
**Action:** POV from Henoch. Orange HUD overlays highlight terrain sectors. The ground texture flickers rapidly between realistic sand and smooth null-grey polygons.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "interface", "shot_type": "pov", "framing": "wide", "environment": "Desert Glitch", "env_change": false, "actors": [], "props": [], "camera": "POV / HUD", "mood": ["analytical", "glitchy"], "director_intent": "Show the system struggling to render the terrain.", "start_image_keywords": ["HUD overlay", "texture flickering", "wireframe terrain"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "ENV_DESERT_GLITCH", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
First-person view (POV) looking at a desert horizon. A complex orange vector HUD overlays the vision, outlining terrain sectors. Large patches of the sand dunes are missing their textures, appearing as smooth, flat grey geometry. The edges of the textures are pixelated and jagged. Heat haze distorts the distance. 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Subject:** Terrain. **State:** Texture Z-fighting and popping.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**UI:** Orange data overlay, Ge'ez characters scrolling.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Desert. **Event:** Level of Detail (LOD) thrashing.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting:** Bright, flickering intensity.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** Handheld POV. **Movement:** Scanning left to right.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Digital buzz and interference static. Intermittent dropouts to total silence.

## [ACT II] [SCENE 2.1] [Timecode: 00:18-00:20] [SCENE INJECTION]
**Action:** Instant cut. Henoch is now on a ship deck in a storm. The lighting shifts violently from sun to strobe lightning.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "medium", "framing": "medium", "environment": "Ship Deck / Storm", "env_change": true, "actors": [{"name": "Henoch", "phase": "MASTER", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "24mm Handheld", "mood": ["chaotic", "sudden"], "director_intent": "Jarring transition to a new environment.", "start_image_keywords": ["Henoch on ship", "storm lighting", "lightning"], "start_image_mode": "actor_in_env", "video_plan": {"start_comp": {"mode": "actor_first", "actor_pose_id": "POSE_SHIP_STANCE", "env_id": "ENV_SHIP_STORM", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Medium shot of Henoch standing on a wet wooden ship deck at night. Violent lightning illuminates him with cold cyan light. Rain freezes in streaks around him. The background is a chaotic mix of dark waves and rigging. High contrast, cinematic action lighting, 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Subject:** Henoch. **Action:** Standing firm against a storm.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**Gear:** Exosuit, wet and reflective.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Ship Deck. **Weather:** Severe Storm.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting:** Stroboscopic lightning flashes.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** 24mm Handheld. **Movement:** Camera shakes violently, Henoch stays perfectly still.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Immediate, deafening thunder crack with digital distortion. Wind howling.

## [ACT II] [SCENE 2.2] [Timecode: 00:20-00:26] [GEOMETRY SPIKES]
**Action:** Wide shot. The ocean waves are not water but jagged black vertex spikes. The ship hits a wave and groans under the impact.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "wide", "framing": "wide", "environment": "Obsidian Ocean", "env_change": false, "actors": [], "props": ["Phoenician Ship"], "camera": "Wide Shaky", "mood": ["violent", "dangerous"], "director_intent": "Show the ocean as a hostile geometric entity.", "start_image_keywords": ["spiked waves", "obsidian ocean", "ship pitching"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "ENV_OCEAN_SPIKES", "props": ["PROP_SHIP_PHOENICIAN"], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Wide action shot of a Phoenician ship cresting a massive wave. The wave is not liquid; it is composed of thousands of sharp, jagged black obsidian spikes and triangles. The water looks like a dangerous, shifting mountain of glass. The ship's hull is visibly straining. Dark, stormy atmosphere, 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Subject:** The Ocean. **Material:** Dynamic sharp geometry (Spikes).
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**Vehicle:** Wooden ship.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Stormy Sea. **Physics:** Rigid body collision.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting:** Flashing lightning revealing the sharp edges.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** Wide Action Cam. **Movement:** Following the ship's heave.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Groaning wood and the sound of grinding glass and stone.

## [ACT II] [SCENE 2.3] [Timecode: 00:26-00:32] [LAG LOOP]
**Action:** The ship crashes into a wave, then instantly snaps back 2 seconds and crashes again. This repeats 3 times in a rapid loop.
**Dialog:** Sailors: "Terror! Terror!" (Looping)



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "prop", "shot_type": "action", "framing": "wide", "environment": "Obsidian Ocean", "env_change": false, "actors": [], "props": ["Phoenician Ship"], "camera": "Crash Zoom", "mood": ["panic", "glitch"], "director_intent": "Visually represent network lag/rubber-banding.", "start_image_keywords": ["ship crash", "motion blur", "glitch"], "start_image_mode": "prop_only", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "ENV_OCEAN_SPIKES", "props": ["PROP_SHIP_PHOENICIAN"], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "sailors_terror_loop", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 2}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Action shot of the ship's bow impacting the black glass waves. The image has a "databosh" glitch effect, where pixels from the previous frame are smeared into the current one. The ship appears to be in two places at once due to the stutter. Chaos and motion blur. 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Subject:** Ship Crash. **Action:** Impacting wave.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**N/A.**
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Ocean. **Event:** Temporal Loop (Rubber-banding).
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting:** Strobe.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** Crash Zoom. **Editing:** Jump cuts repeating the same impact action 3 times.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Audio stutter effect: "CRASH-CRASH-CRASH". Looping vocal scream.

## [ACT II] [SCENE 2.4] [Timecode: 00:32-00:38] [CLIPPING ERROR]
**Action:** A Sailor tries to grab a rope, but his hand passes through the mast geometry. He screams, his face distorting digitally.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "medium", "framing": "medium", "environment": "Ship Deck", "env_change": false, "actors": [{"name": "Kings", "phase": "PROXY", "presence": "on_screen", "focus": "primary"}], "props": ["Mast", "Rope"], "camera": "50mm Dolly In", "mood": ["horror", "wrong"], "director_intent": "Body horror via collision failure.", "start_image_keywords": ["clipping hand", "sailor scream", "glitch"], "start_image_mode": "actor_in_env", "video_plan": {"start_comp": {"mode": "actor_first", "actor_pose_id": "POSE_GRAB_FAIL", "env_id": "ENV_SHIP_DECK", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Medium shot of a Phoenician sailor in terror. He is reaching out to grab a wooden mast, but his hand and forearm have passed completely inside the wood, intersecting the geometry seamlessly. He looks at his merged limb with wide, terrified eyes. The lighting is dark and wet. 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Subject:** Sailor. **Action:** Grabbing the mast.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**Costume:** Purple robes.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Ship Deck. **Physics:** No collision detection. Hand ghosts through solid wood.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting:** Lightning flashes.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** Dolly In (Fast). **Focus:** The intersection point of hand and wood.

### 3. AUDIO PROMPT (Hunyuan/Foley)
High-pitched digital screeching (modem handshake sound) mixed with a human scream.

## [ACT II] [SCENE 2.5] [Timecode: 00:38-00:45] [VOXELIZATION]
**Action:** Top-down God View. The ocean surface turns into rising black cubes. The ship dissolves into these cubes, floating upwards into the sky.
**Dialog:** Henoch: "Integrität versagt."



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "wide", "framing": "wide", "environment": "Obsidian Ocean", "env_change": false, "actors": [{"name": "Henoch", "phase": "MASTER", "presence": "off_screen", "focus": "secondary"}], "props": ["Dissolving Ship"], "camera": "Crane Up / Top Down", "mood": ["apocalyptic", "abstract"], "director_intent": "The total breakdown of the simulation into raw data.", "start_image_keywords": ["voxel ocean", "floating cubes", "ship dissolving"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "ENV_OCEAN_VOXELS", "props": ["PROP_SHIP_DISSOLVE"], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "henoch_integrity_failing", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 2}
### 1. START IMAGE PROMPT (Midjourney/Flux)
High-angle top-down shot of the ocean. The water is no longer fluid but a mass of millions of black glossy cubes rising upwards against gravity. The wooden ship in the center is breaking apart into identical wooden cubes, joining the flow into the sky. It looks like a complex physics simulation losing cohesion. 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Subject:** The Ship and Ocean. **State:** Disintegrating into geometric primitives (Cubes).
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**N/A.**
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Ocean. **Physics:** Reverse gravity for particles.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting:** Backlit from below by lightning.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** Crane Up (fast). **Style:** Data visualization disaster.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Deep, rumbling sub-bass drop. The sound of heavy stone blocks grinding together.

## [ACT III] [SCENE 3.1] [Timecode: 00:45-00:50] [THE WALL]
**Action:** Static shot. The ocean chaos hits an invisible wall and stops dead. The water piles up vertically against the barrier. An orange hexagonal grid glows at the impact point.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "wide", "framing": "wide", "environment": "World Border", "env_change": true, "actors": [], "props": ["Water Wall"], "camera": "Static Tripod", "mood": ["still", "liminal"], "director_intent": "Reveal the hard limit of the world.", "start_image_keywords": ["invisible wall", "vertical water", "hex grid"], "start_image_mode": "env_only", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "ENV_WORLD_BORDER", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Wide profile shot of a massive wall of black water pressed flat against an invisible vertical barrier. The water is turbulent but the surface touching the wall is perfectly flat. A faint, glowing orange hexagonal grid pattern illuminates the contact points. Beyond the wall is empty white space. Stark contrast between chaos and order. 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Subject:** Boundary Wall. **Interaction:** Fluid collision.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**N/A.**
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Edge of World. **Physics:** Fluid simulation confined by box collider.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting:** Glow from the grid.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** Completely Static. **Focus:** The water sliding up the invisible glass.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Absolute silence. All storm noise cuts out instantly.

## [ACT III] [SCENE 3.2] [Timecode: 00:50-00:55] [COOLING DOWN]
**Action:** Close up of Henoch's face. His skin is translucent ceramic. We see orange fluorescent coolant pulsing in channels under his neck skin.
**Dialog:** Henoch: "Das Siegel ist gesetzt."



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "close_up", "framing": "close_up", "environment": "World Border", "env_change": false, "actors": [{"name": "Henoch", "phase": "MASTER", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "85mm Slow Zoom", "mood": ["calm", "post-human"], "director_intent": "Show the machine cooling down after the task.", "start_image_keywords": ["Henoch face", "translucent skin", "orange coolant"], "start_image_mode": "actor_only", "video_plan": {"start_comp": {"mode": "actor_first", "actor_pose_id": "POSE_CALM_LOOK", "env_id": "ENV_WORLD_BORDER", "props": [], "notes": ""}, "motion_driver": {"type": "a2f", "audio_id": "henoch_seal_set", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 4}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Portrait close-up of Henoch. His skin is a semi-transparent milky white ceramic material. Beneath the surface, complex vascular channels filled with glowing orange liquid are visible in his neck and jaw. His expression is serene and blank. The background is a soft, sterile white out-of-focus blur. 85mm portrait lens, 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Subject:** Henoch. **Skin:** Translucent. **Internals:** Pulsing orange coolant.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**Gear:** Exosuit collar visible.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** Void/Border.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting:** Soft, internal subsurface scattering glow.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** Slow Zoom In. **Movement:** Subtle pulse of the coolant.

### 3. AUDIO PROMPT (Hunyuan/Foley)
The sound of a high-performance computer fan spinning down from high RPM to silence.

## [ACT III] [SCENE 3.3] [Timecode: 00:55-01:00] [SHUTDOWN]
**Action:** Extreme wide shot. Henoch stands in a white void. Behind him, looking through the invisible wall, the frozen storm and ship are trapped in the previous scene. He turns his back to them. Fade to black.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "mixed", "shot_type": "wide", "framing": "extreme_wide", "environment": "Void", "env_change": true, "actors": [{"name": "Henoch", "phase": "MASTER", "presence": "on_screen", "focus": "primary"}], "props": ["Frozen Scene Background"], "camera": "Wide Symmetrical", "mood": ["final", "empty"], "director_intent": "The final separation between administrator and simulation.", "start_image_keywords": ["white void", "Henoch back", "frozen storm window"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "POSE_TURN_AWAY", "env_id": "ENV_VOID_WHITE", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Extreme wide shot. The foreground is an infinite, sterile white floor. Henoch stands with his back to the camera, facing a large rectangular "window" floating in space. Inside the window is the frozen, dark chaos of the obsidian storm and the exploding ship. He is outside of it, safe in the white void. Symmetrical composition, Kubrick-esque, 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
**Subject:** Henoch. **Action:** Standing still, then turning away.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
**Gear:** Exosuit (high contrast against white).
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
**Location:** The Void. **Background:** A floating screen showing the frozen simulation.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
**Lighting:** Even, shadowless studio white.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
**Camera:** Static Wide. **Transition:** Slow Fade to Black.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Single digital beep (BIOS POST beep).

## ACTOR MONOLOGUE PLAN (JSON)
MONOLOGUE_JSON: {"actors":{"Henoch":[{"scene":"1.2","text":"Beobachte die Partition.","words_max":3},{"scene":"1.4","text":"Eingabe verweigert.","words_max":2},{"scene":"2.5","text":"Integrität versagt.","words_max":2},{"scene":"3.2","text":"Das Siegel ist gesetzt.","words_max":4},{"scene":"2.3","text":"Terror! Terror!","words_max":2}]},"notes":"German only. Short internal monologues. Do not describe the camera or list what is visible. Use emotion, memory, and cause-effect logic. Keep total lines per chapter low (3-7). JSON must be in one line."}