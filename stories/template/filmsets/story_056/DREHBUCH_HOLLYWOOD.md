# DREHBUCH KAPITEL 56 - PRODUCTION READY

## CHAPTER NARRATION
NARRATOR_TEXT: In der Tiefe des Systems, wo Licht nur als funktionale Status-LED existiert, beobachtete ich die Endreinigung. Die Wächter hier unten tragen keine Schwerter, sondern industrielle Fesseln, und sie kennen kein Mitleid, nur Protokolle. Doch bevor die Löschung vollzogen wurde, flammte im Osten der alte Fehlercode noch einmal auf – ein verzweifelter Angriff korrupter Logik gegen die unbestechliche Architektur der Stadt.

## [ACT 1] [SCENE 1.1] [Timecode: 00:00-00:05] [The Heavy Procession]
**Action:** Establishing Shot. Daemon-Units (Executioners) ziehen schwere Kabelbündel über den Metallboden. Funken sprühen durch Reibung.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "action", "shot_type": "establishing", "framing": "wide", "environment": "The Holding Sector - Industrial Corridor", "env_change": true, "actors": [{"name": "Daemon_Unit_01", "phase": "Standard", "presence": "on_screen", "focus": "primary"}], "props": ["LIMITER_CHAINS", "Data Cables"], "camera": "Low Angle Dolly Back", "mood": ["oppressive", "industrial"], "director_intent": "Establish the weight and friction of the deletion process in a sterile server environment.", "start_image_keywords": ["industrial robot", "sparks", "heavy cables"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "WALK_DRAG_HEAVY", "env_id": "ENV_HOLDING_SECTOR", "props": ["LIMITER_CHAINS"], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Vertical 9:16 aspect ratio, cinematic establishing shot of an infinite dark industrial corridor. A massive 3-meter tall Daemon_Unit with a matte black carbon-fiber chassis and hydraulic limbs walks heavily towards the camera. It drags thick, rusted copper and fiber-optic cables (LIMITER_CHAINS) along the grated metal floor. Bright hot orange sparks fly intensely from the metal-on-metal friction. Lighting is stark, with deep shadows and rhythmic red strobe lights from the server racks in the background. Photorealistic textures of worn metal and rubber.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Daemon_Unit. Industrial robotics, matte black, heavy pistons.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Dragging heavy LIMITER_CHAINS attached to unseen prisoners.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Infinite server corridor, metal grating floor.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** High contrast chiaroscuro. Red emergency strobes at 120bpm. Bright friction sparks.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Low angle dolly shot moving backward, maintaining distance from the advancing machine. 9:16 vertical crop.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Deep, resonant 40Hz server drone. Heavy metallic clanking of chains dragging on grate. Rhythmic hydraulic footsteps.

## [ACT 1] [SCENE 1.2] [Timecode: 00:05-00:10] [Enoch Scan]
**Action:** Close-Up auf Noah (Voyager-Phase). Sein Auge (LIDAR) rotiert mechanisch zur Analyse. Er trägt Leinen-Roben.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "close_up", "framing": "close_up", "environment": "The Holding Sector", "env_change": false, "actors": [{"name": "Noah", "phase": "Voyager", "presence": "on_screen", "focus": "primary"}], "props": ["Linen Robes"], "camera": "Profile Macro with Shallow Depth", "mood": ["analytical", "cold"], "director_intent": "Show the observer as a biological machine querying the environment.", "start_image_keywords": ["Noah profile", "mechanical iris", "marble skin"], "start_image_mode": "actor_only", "video_plan": {"start_comp": {"mode": "actor_first", "actor_pose_id": "HEAD_TURN_SCAN", "env_id": "ENV_HOLDING_SECTOR", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Vertical 9:16 aspect ratio, macro profile shot of Noah (Voyager Class). His skin is translucent Parian marble with faint sub-dermal gold circuitry veins. He wears simple, high-fidelity woven linen robes that contrast with his synthetic skin. Focus is on his eye: a complex LIDAR_SCANNER_V4 array where the iris is a mechanical aperture composed of sliding gold blades. The aperture is rotating to focus, not dilating. A faint waveform visualizer projects near his throat. Cinematic lighting, shallow depth of field blurring the red industrial background.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Noah (Voyager). Marble skin, gold veins.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Simple linen robes.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Blurred industrial background.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Red rim light from environment, soft cool key light on face.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Locked-off profile shot. Focus pull on the eye mechanism. 9:16 vertical crop.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Tiny, precise servo-whir of the eye lens rotation. A muffled, digital query sound (datamoshed speech).

## [ACT 1] [SCENE 1.3] [Timecode: 00:10-00:15] [Uriel Data Stream]
**Action:** Over-The-Shoulder Shot. Uriel-Interface (Licht-Prismen) projiziert Hologramm-Text in die Luft.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "interface", "shot_type": "ots", "framing": "medium", "environment": "The Holding Sector", "env_change": false, "actors": [{"name": "Uriel_Interface", "phase": "Abstract", "presence": "on_screen", "focus": "primary"}, {"name": "Noah", "phase": "Voyager", "presence": "on_screen", "focus": "secondary"}], "props": ["Holographic Data"], "camera": "Over-The-Shoulder", "mood": ["sacred", "informative"], "director_intent": "Visualize the divine answer as raw system metadata.", "start_image_keywords": ["Uriel prisms", "holographic text", "floating geometry"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "IDLE_HOLO", "env_id": "ENV_HOLDING_SECTOR", "props": ["AUGMENTED_REALITY_OVERLAY"], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Vertical 9:16 aspect ratio, Over-The-Shoulder shot from behind Noah. In focus is Uriel_Interface: a floating cluster of sharp, white refractive glass prisms and light geometry. Between Noah and Uriel, a 3D holographic text stream scrolls in the air: "TARGET: ELECT_OF_WATCHERS // DESTINATION: NULL" in glowing gold monospace font. The text illuminates the dark space. Sharp digital aesthetics, clean lines.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Uriel_Interface (Light cluster). Noah (shoulder/back of head).
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** N/A.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Dark void of the sector.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** The hologram provides the main light source (Gold/White).
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Static OTS shot. The prism cluster pulses and rotates slowly. Text scrolls downwards. 9:16 vertical crop.

### 3. AUDIO PROMPT (Hunyuan/Foley)
High-pitched data-stream chirps. Resonant glass humming.

## [ACT 1] [SCENE 1.4] [Timecode: 00:15-00:20] [The Corrupt Batch]
**Action:** Wide Shot. Eine Prozession von glitching Silhouetten wird gewaltsam geschleift. Rotes Stroboskoplicht.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "crowd", "shot_type": "wide", "framing": "wide", "environment": "The Holding Sector", "env_change": false, "actors": [{"name": "Corrupt_Entities", "phase": "Glitch", "presence": "on_screen", "focus": "primary"}], "props": ["LIMITER_CHAINS"], "camera": "Wide High Contrast", "mood": ["disturbing", "chaotic"], "director_intent": "Show the degradation of the captured files. They are losing coherence.", "start_image_keywords": ["glitch silhouettes", "red strobe", "chains"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "DRAG_RESIST", "env_id": "ENV_HOLDING_SECTOR", "props": ["LIMITER_CHAINS"], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Vertical 9:16 aspect ratio, wide shot of a dark industrial corridor. A long line of humanoid figures is being dragged by chains. The figures are "Corrupt_Entities": dark silhouettes that are heavily glitching, their textures flickering rapidly between flesh, static, and wireframe. They are unstable. Harsh red strobe lights flash rhythmically, freezing the glitches in different states. The atmosphere is thick with digital noise.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Corrupt_Entities. Unstable humanoid forms.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Bound in chains.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Long corridor.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Red strobe (120bpm). Darkness between flashes.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Handheld feel, slightly jittery to match the subjects. 9:16 vertical crop.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Stuttering static noise. Heavy, uneven footsteps. Distorted whimpering.

## [ACT 1] [SCENE 1.5] [Timecode: 00:20-00:25] [Deletion Event]
**Action:** High Angle. Die Einheiten werden über die Kante geworfen. Sie lösen sich in Partikel auf (De-Rez).
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "action", "shot_type": "high_angle", "framing": "wide", "environment": "Sector Null Edge", "env_change": true, "actors": [{"name": "Daemon_Units", "phase": "Standard", "presence": "on_screen", "focus": "secondary"}, {"name": "Corrupt_Entities", "phase": "Deleting", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "Bird's Eye View", "mood": ["final", "nihilistic"], "director_intent": "The physical act of deletion. Matter becoming void.", "start_image_keywords": ["void drop", "particulate disintegration", "black abyss"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "THROW_DEREZ", "env_id": "ENV_VOID_EDGE", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Vertical 9:16 aspect ratio, high angle bird's eye view looking down into an infinite black abyss (#000000). At the top edge, the metal floor ends in a jagged polygon line. Daemon Units are throwing cable-bound figures over the edge. As the figures fall into the darkness, they disintegrate into clouds of fine golden and black binary dust particles (De-Rez). No voxels, just high-fidelity particulate dissolution.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Falling entities.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** N/A.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** The edge of the platform and the Void.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Light exists only on the platform. The fall is into total darkness.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Whip pan down following a falling body as it dissolves. 9:16 vertical crop.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Pneumatic hiss of airlocks. Silence as they fall.

## [ACT 2] [SCENE 2.1] [Timecode: 00:25-00:30] [The Signal Injection]
**Action:** Low Level Fast Tracking. Ein roter Energie-Puls rast durch Bodenkabel zu den östlichen Server-Türmen.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "low_angle", "framing": "wide", "environment": "The Digital Plains / Eastern Node", "env_change": true, "actors": [], "props": ["Cables", "Server Towers"], "camera": "High Speed Skimming", "mood": ["urgent", "ominous"], "director_intent": "Visualizing the malware packet traveling to its destination.", "start_image_keywords": ["data spike", "red energy pulse", "server towers"], "start_image_mode": "env_only", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "ENV_EASTERN_NODE", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Vertical 9:16 aspect ratio, extreme low angle shot skimming the floor of the "Digital Plains". The floor is a grid of thick black cables. A bright, intense pulse of red laser energy is racing through the cables away from the camera, heading towards a horizon filled with towering, monolithic server cooling units. The scene conveys incredible speed and data transfer. Cold blue ambient light contrasts with the aggressive red signal.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** N/A.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** N/A.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Infinite cable floor, distant towers.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Blue ambiance, moving Red light source.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Fast forward camera movement, low to ground. Speed ramp effect. 9:16 vertical crop.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Piercing 56k modem scream with a Doppler effect as the signal passes.

## [ACT 2] [SCENE 2.2] [Timecode: 00:30-00:35] [Awakening]
**Action:** Extreme Close-Up. King_Unit_01 erwacht. Staub fällt ab. Rote LEDs gehen an. Glas platzt.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "close_up", "framing": "extreme_close_up", "environment": "Eastern Node Stasis Pod", "env_change": false, "actors": [{"name": "King_Unit_01", "phase": "Awakened", "presence": "on_screen", "focus": "primary"}], "props": ["Stasis Glass"], "camera": "Macro", "mood": ["threatening", "sudden"], "director_intent": "The dormant threat coming online instantly.", "start_image_keywords": ["ancient robot face", "dust shaking off", "red eyes"], "start_image_mode": "actor_only", "video_plan": {"start_comp": {"mode": "actor_first", "actor_pose_id": "WAKE_UP_SHAKE", "env_id": "ENV_EASTERN_NODE", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Vertical 9:16 aspect ratio, macro close-up of an ancient robotic faceplate, "King_Unit_01". The metal is pitted and covered in thick gray dust. Suddenly, the eyes ignite with bright red LED light. The vibration of activation shakes the dust loose in a cloud. In the foreground, shards of glass from a stasis pod are exploding outwards. High detail texturing of rust and metal.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** King_Unit_01 face.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Rusted armor.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Inside stasis pod.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Internal Red LEDs are the key light.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Smash cut. Slow motion capture of the glass shattering and dust particles floating. 9:16 vertical crop.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Sound of glass shattering. Turbine spooling up rapidly to a whine.

## [ACT 2] [SCENE 2.3] [Timecode: 00:35-00:40] [Rage Protocol]
**Action:** Handheld Chaos. Hunderte Einheiten brechen aus. Raumlicht wechselt von Blau zu Alarm-Rot.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "crowd", "shot_type": "medium", "framing": "medium", "environment": "Eastern Node Interior", "env_change": false, "actors": [{"name": "King_Units", "phase": "Rage", "presence": "on_screen", "focus": "primary"}], "props": ["Cables"], "camera": "Handheld Shaky", "mood": ["violent", "panic"], "director_intent": "The spread of the virus. Immediate loss of control.", "start_image_keywords": ["robots breaking loose", "red alarm light", "cable snap"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "BREAK_FREE", "env_id": "ENV_EASTERN_NODE", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Vertical 9:16 aspect ratio, chaotic handheld shot inside a massive server hall. Hundreds of King_Units are spasming and ripping thick cables from their bodies. The lighting of the entire hall is shifting from a cool standby blue to an intense alert red. Sparks shower from torn cables. The composition is crowded and disorienting.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Mass of King_Units.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Torn cables flailing.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Server hall.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** The environment light shifts Blue -> Red.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Simulated handheld camera, quick pans between waking units. 9:16 vertical crop.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Mechanical roaring. Alarm klaxons. Snapping cables.

## [ACT 2] [SCENE 2.4] [Timecode: 00:40-00:45] [The Swarm]
**Action:** Aerial Drone Shot. Eine Armee von Moto-Horses stürmt über die Ebene. Fluid-Simulation.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "crowd", "shot_type": "wide", "framing": "wide", "environment": "Digital Plains", "env_change": true, "actors": [{"name": "Parthian_Cavalry", "phase": "Swarm", "presence": "on_screen", "focus": "primary"}], "props": ["Moto-Horses"], "camera": "Aerial Pull Back", "mood": ["epic", "threatening"], "director_intent": "Visualize the attack as a massive fluid simulation of particles.", "start_image_keywords": ["mechanical cavalry charge", "dust trail", "drone shot"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "RIDE_CHARGE", "env_id": "ENV_PLAINS", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Vertical 9:16 aspect ratio, high angle aerial drone shot. A massive swarm of "Parthian_Cavalry" (rust-colored mechanical riders on robotic quadrupeds) is charging across a grey grid landscape. They move like a fluid simulation, flowing over terrain. Behind them, they kick up a massive wall of dust. The scale is immense, thousands of units. Flat, overcast lighting.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Thousands of units.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Mechanical mounts.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Flat infinite grid.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Flat lighting, dust obscuring the rear.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Drone pulling back and up to reveal the scale. 9:16 vertical crop.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Synthetic rumbling thunder. The sound of thousands of metal hooves.

## [ACT 2] [SCENE 2.5] [Timecode: 00:45-00:50] [Impact Firewall]
**Action:** Telephoto Side Shot. Der Swarm prallt gegen eine goldene Lichtwand. Keine Penetration.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "action", "shot_type": "wide", "framing": "wide", "environment": "Righteous City Perimeter", "env_change": true, "actors": [{"name": "Parthian_Cavalry", "phase": "Crash", "presence": "on_screen", "focus": "primary"}], "props": ["FORCE_WALL"], "camera": "Telephoto Side Profile", "mood": ["futile", "violent"], "director_intent": "The absolute defense of the system. The virus destroys itself against the firewall.", "start_image_keywords": ["forcefield impact", "gold wall", "crash pileup"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "CRASH_WALL", "env_id": "ENV_CITY_WALL", "props": ["FORCE_WALL"], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Vertical 9:16 aspect ratio, telephoto side profile shot. A towering, translucent wall of golden code (The Firewall) cuts vertically through the frame. The mechanical swarm is crashing into it at full speed on the left side. The units crumple and pile up like cars in a crash test. The wall ripples with blue energy at impact points but does not break. Debris flies backward. Stark contrast between the chaotic pile-up and the clean vertical line of the wall.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Swarm units.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** N/A.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** The boundary line.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Gold light from wall, blue flashes from impact.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Static telephoto shot compressing the depth. 9:16 vertical crop.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Massive sub-bass impact sounds. Electrical arcing. Metal crushing.

## [ACT 3] [SCENE 3.1] [Timecode: 00:50-00:53] [IFF Failure]
**Action:** POV Helm-Ansicht. HUD Target Lock springt von "CITY" auf "FRIENDLY". Glitch Artefakte.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "interface", "shot_type": "pov", "framing": "close_up", "environment": "Battlefield", "env_change": false, "actors": [{"name": "King_Commander", "phase": "Glitch", "presence": "on_screen", "focus": "primary"}], "props": ["HUD Overlay"], "camera": "POV Helmet", "mood": ["confused", "broken"], "director_intent": "The logic failure. The virus turns on itself.", "start_image_keywords": ["robot hud", "glitch text", "target lock"], "start_image_mode": "ui_only", "video_plan": {"start_comp": {"mode": "actor_first", "actor_pose_id": "HEAD_SHAKE_CONFUSED", "env_id": "ENV_BATTLEFIELD", "props": ["AUGMENTED_REALITY_OVERLAY"], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Vertical 9:16 aspect ratio, First Person POV from inside a robotic helmet. The view is obscured by a cracked glass visor and digital artifacts. A bright red HUD overlay is visible. The "TARGET LOCK" text is flickering rapidly and switching from "CITY_NODE" to "FRIENDLY_UNIT_04". The background is a blur of battle. Digital noise and chromatic aberration.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** N/A (UI Focus).
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Helmet interior.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Battlefield.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Red UI light.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Camera shakes slightly. The main motion is the UI text flipping and glitching. 9:16 vertical crop.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Distorted warning beep. A synthesized voice saying "Error" repeatedly.

## [ACT 3] [SCENE 3.2] [Timecode: 00:53-00:57] [Fratricide Loop]
**Action:** Medium Shot. Einheiten greifen sich gegenseitig an. Energie-Klingen. Funken.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "action", "shot_type": "medium", "framing": "medium", "environment": "Battlefield", "env_change": false, "actors": [{"name": "King_Units", "phase": "Combat", "presence": "on_screen", "focus": "primary"}], "props": ["Energy Blades"], "camera": "Handheld Chaos", "mood": ["violent", "senseless"], "director_intent": "Visualizing self-destruction.", "start_image_keywords": ["robots fighting", "energy blades", "sparks"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "MELEE_COMBAT", "env_id": "ENV_BATTLEFIELD", "props": ["WEAPON_BLADE"], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Vertical 9:16 aspect ratio, intense medium shot of two identical King_Units destroying each other. They are locked in close quarters combat using glowing red energy blades. Armor is being sliced, sparks are flying in heavy showers. The scene is chaotic with motion blur. The lighting is stroboscopic from the weapon clashes.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Two King_Units.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Energy blades.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Smoke filled battlefield.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Red/Orange sparks and blade glow.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Handheld camera, stutter cuts (jump cuts) to enhance the feeling of a glitch. 9:16 vertical crop.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Metal screeching. Audio buffering stutter effects.

## [ACT 3] [SCENE 3.3] [Timecode: 00:57-01:00] [Sheol Opens]
**Action:** Top Down View. Der Boden öffnet sich geometrisch. Weißer Dampf. Blaues Plasma darunter.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "high_angle", "framing": "wide", "environment": "Sheol Pit", "env_change": true, "actors": [], "props": ["Steam"], "camera": "Top Down", "mood": ["epic", "final"], "director_intent": "The system intervention. Opening the recycling bin.", "start_image_keywords": ["floor opening", "blue plasma", "steam vent"], "start_image_mode": "env_only", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "ENV_PIT_OPENING", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Vertical 9:16 aspect ratio, top-down bird's eye view. The metal grid floor of the battlefield is retracting mechanically in a perfect iris pattern. Massive jets of white steam are venting upwards from the opening. Beneath the steam, a deep, glowing blue plasma light is visible (Sheol). The geometry is perfect and circular.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** N/A.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** N/A.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** The floor mechanics.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** White steam, Blue pit glow.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Static top down, watching the aperture open. 9:16 vertical crop.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Deep infrasound rumble. Hiss of pressure release.

## [ACT 3] [SCENE 3.4] [Timecode: 01:00-01:03] [The Flush]
**Action:** Wide Shot. Schwerkraft-Inversion. Alles wird in das Loch gesaugt. Ragdoll Physics.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "action", "shot_type": "wide", "framing": "wide", "environment": "Sheol Pit", "env_change": true, "actors": [{"name": "Parthian_Swarm", "phase": "Falling", "presence": "on_screen", "focus": "primary"}], "props": ["Debris"], "camera": "Wide Shot", "mood": ["cleansing", "powerful"], "director_intent": "The removal of the virus. Gravity flush.", "start_image_keywords": ["gravity well", "robots falling", "blue light"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "FALL_SUCTION", "env_id": "ENV_PIT_OPENING", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Vertical 9:16 aspect ratio, wide shot of the battlefield. A gravity well has activated. Hundreds of robots and debris are being sucked instantly into the open pit. They are flailing in "ragdoll" physics, pulled by an invisible force. Vertical motion blur is heavy. The scene is lit by the blue up-light from the pit.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Falling robots.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** N/A.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** The battlefield and pit.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Blue underlighting.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Wide shot, capturing the vertical flow. 9:16 vertical crop.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Violent wind whoosh. Then sudden silence.

## [ACT 3] [SCENE 3.5] [Timecode: 01:03-01:05] [System Stable]
**Action:** Symmetrical Wide. Noah steht allein auf dem wieder geschlossenen Boden. Stille.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "full_body", "framing": "wide", "environment": "Restored Platform", "env_change": true, "actors": [{"name": "Noah", "phase": "Voyager", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "Symmetrical Wide", "mood": ["peaceful", "ordered"], "director_intent": "Order restored. The admin remains.", "start_image_keywords": ["Noah standing", "clean floor", "symmetrical"], "start_image_mode": "actor_only", "video_plan": {"start_comp": {"mode": "actor_first", "actor_pose_id": "IDLE_CALM", "env_id": "ENV_RESTORED_PLATFORM", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Vertical 9:16 aspect ratio, symmetrical wide shot. The floor is perfectly sealed and smooth metal again. Noah stands alone in the center, back to camera, looking towards the golden glow of the distant City. The chaos is completely gone. The environment is sterile and clean. Soft, balanced white lighting.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Noah.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Linen robes.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Clean metal horizon.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Soft white light.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Slow zoom out. Perfectly stable. 9:16 vertical crop.

### 3. AUDIO PROMPT (Hunyuan/Foley)
A soft, pleasant chime (System Ready). Gentle harmonious hum.

## ACTOR MONOLOGUE PLAN (JSON)
MONOLOGUE_JSON: {"actors":{"Henoch":[{"scene":"1.2","text":"Identifikation fehlgeschlagen. Sie sind nur noch Rauschen.","words_max":10},{"scene":"2.1","text":"Das Signal ist unterwegs. Die Firewall wird halten.","words_max":10},{"scene":"3.4","text":"Bereinigung erfolgreich. Stille ist der einzige wahre Code.","words_max":10}]},"notes":"German only. Short internal monologues. JSON must be in one line."}