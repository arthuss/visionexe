# DREHBUCH KAPITEL 32 - PRODUCTION READY

## CHAPTER NARRATION
NARRATOR_TEXT: Jenseits der roten Sektoren, wo die Entropie die Daten frisst, fand ich die sieben Kühltürme der Ewigkeit. Der Duft von Narde und Zimt war kein biologisches Signal, sondern reiner System-Code, der meine Sensoren überflutete und mich zur Root-Partition führte. Dort, hinter der flimmernden Firewall von Zotiel, lag der Garten der Gerechtigkeit – eine makellose Simulation, in der der Fehlerfall Mensch einst seinen Anfang nahm.

## [ACT 1] [SCENE 1.1] [Timecode: 00:00-00:05] [AERIAL SURVEY]
**Action:** High-velocity drone shot over seven massive, conical terraforming structures (Spice Mountains) venting colored gas.
**Dialog:** -

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "wide", "framing": "wide", "environment": "Red Sea Wasteland / Cooling Towers", "env_change": true, "actors": [], "props": ["Terraforming Towers", "Vented Gas"], "camera": "Drone / Mach 2", "mood": ["scale", "industrial"], "director_intent": "Establish the environment as a massive industrial cooling system disguised as geology.", "start_image_keywords": ["terraforming towers", "red dust", "mach speed"], "start_image_mode": "env_only", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "ENV_SPICE_MTS", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "media/badges/geez_logo_v1.mov", "blend": "screen", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Vertical 9:16 cinematic aerial shot. Seven colossal, cone-shaped industrial cooling towers disguised as mountains, rising from a desolate red dust desert. They vent massive plumes of amber and emerald gas (Cinnamon/Pepper). Harsh, directional sunlight casts long, sharp shadows. Industrial mysticism, photorealistic textures, atmospheric perspective, 8k.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** No organic subject.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** N/A.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** The Spice Mountains: towering conical structures of weathered metal and rock. The ground is a blur of red sand. The sky is a heavy, heat-hazed orange.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** High contrast sunlight. Palette: Rust Red, Toxic Green (Gas), Amber (Gas).
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Fast forward camera movement at Mach 2. Motion blur on the terrain. Stable horizon. 9:16 aspect ratio.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Roaring wind shear, high-pitched turbine whine of the drone, deep subterranean rumble of heavy machinery.

## [ACT 1] [SCENE 1.2] [Timecode: 00:05-00:09] [BIO-INJECTION]
**Action:** Close-up on Henoch's HUD. The "scent" is visualized as chemical structure graphs overlaying his vision.
**Dialog:** -

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "close_up", "framing": "extreme_close_up", "environment": "Cockpit / Helmet Interior", "env_change": false, "actors": [{"name": "Henoch", "phase": "Voyager", "presence": "on_screen", "focus": "primary"}], "props": ["Helmet HUD", "Chemical Graphs"], "camera": "Macro / POV hybrid", "mood": ["analytical", "intense"], "director_intent": "Show the translation of smell into digital data.", "start_image_keywords": ["hud interface", "chemical formula", "silver skin"], "start_image_mode": "actor_only", "video_plan": {"start_comp": {"mode": "actor_first", "actor_pose_id": "POSE_HEAD_SCAN", "env_id": "ENV_COCKPIT", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "media/badges/geez_logo_v1.mov", "blend": "screen", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Vertical 9:16 extreme close-up of Henoch (Voyager Phase) inside his helmet. Silver skin reflects the amber glow of the HUD. Holographic chemical formulas and molecular graphs (Cinnamon/Nard) scroll rapidly across his visor glass. His pupils are dilated, reflecting the data stream. Shallow depth of field, sharp focus on eyes and UI elements.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Henoch (Voyager). Metallic skin texture with subsurface scattering.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** High-tech flight helmet, glass visor with AR overlay.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Interior helmet space. Background is blurred motion.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Internal HUD lighting (Amber/Cyan). Reflections of external red environment on glass.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Macro lens. Subtle camera shake (turbulence). UI elements animating. 9:16 aspect ratio.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Digital data scrolling sound (rapid chirps), heavy breathing in enclosed space, hydraulic hiss of suit injection.

## [ACT 1] [SCENE 1.3] [Timecode: 00:09-00:14] [THE SENTINEL]
**Action:** Henoch flies past Zotiel, a 500m obsidian sensor tower scanning the sky.
**Dialog:** -

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "mixed", "shot_type": "low_angle", "framing": "wide", "environment": "Zotiel Perimeter", "env_change": true, "actors": [{"name": "Henoch", "phase": "Voyager", "presence": "on_screen", "focus": "secondary"}], "props": ["Zotiel Statue", "Laser Grid"], "camera": "Whip Pan / Tracking", "mood": ["menacing", "monumental"], "director_intent": "Visualize the firewall as a physical guardian entity.", "start_image_keywords": ["obsidian giant", "laser scan", "merkabah flight"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "POSE_FLIGHT_BANK", "env_id": "ENV_ZOTIEL", "props": ["PROP_ZOTIEL_TOWER"], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "media/badges/geez_logo_v1.mov", "blend": "screen", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Vertical 9:16 low angle shot looking up at "Zotiel", a 500-meter tall monolith statue made of black obsidian and chrome hardware. It is scanning the sky with a fan of red laser beams. Henoch, a small silver figure in a glowing tetrahedron field, streaks past the head of the giant. Oppressive scale, sci-fi noir lighting against a red sky.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Henoch (Small in frame).
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Enclosed in spinning Merkabah light-field.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** The Zotiel perimeter. Massive structure dominates the frame.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Red lasers cutting through dust. Black reflections on obsidian.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Whip pan following Henoch as he passes the stationary giant. 9:16 aspect ratio.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Deep, resonant sonar ping (authorization scan), massive bass thrum of the statue, jet-engine flyby sound.

## [ACT 1] [SCENE 1.4] [Timecode: 00:14-00:18] [MESH BREAK]
**Action:** Impact with the firewall. Reality tears. Pixel sorting stretches the world.
**Dialog:** -

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "mixed", "shot_type": "pov", "framing": "medium", "environment": "Glitch Zone", "env_change": true, "actors": [], "props": ["Glitch Artifacts"], "camera": "POV / Crash Zoom", "mood": ["chaos", "transition"], "director_intent": "The violent transition from the chaotic partition to the sterile kernel.", "start_image_keywords": ["pixel sorting", "reality tear", "red to white"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "", "env_id": "ENV_GLITCH_WALL", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "media/badges/geez_logo_v1.mov", "blend": "screen", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Vertical 9:16 abstract glitch art composition. A split screen effect where the bottom half is dusty red terrain pixel-sorting upwards into infinite lines, and the top half is sterile, blinding white geometry crashing down. A datamosh effect tearing the image apart. "SYSTEM_OVERRIDE" text fragmenting in the center.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** N/A (POV).
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** N/A.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** The boundary between Red Sea and Garden.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Violent strobing between Red/Orange and Pure White/Cyan.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Crash zoom. Simulated video corruption. 9:16 aspect ratio.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Digital screech, modem handshake static, abrupt cut to vacuum silence.

## [ACT 2] [SCENE 2.1] [Timecode: 00:18-00:24] [KERNEL LANDING]
**Action:** Henoch lands on the Garden floor. A white ceramic grid with bioluminescent moss. Merkabah folds away.
**Dialog:** -

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "full_body", "framing": "full_body", "environment": "Garden of Righteousness Floor", "env_change": true, "actors": [{"name": "Henoch", "phase": "Voyager", "presence": "on_screen", "focus": "primary"}], "props": ["Ceramic Floor", "Merkabah Residuals"], "camera": "Ground Level / Stabilized", "mood": ["sterile", "calm"], "director_intent": "Contrast the chaos outside with the absolute order inside.", "start_image_keywords": ["white ceramic floor", "circuit moss", "superhero landing"], "start_image_mode": "actor_in_env", "video_plan": {"start_comp": {"mode": "actor_first", "actor_pose_id": "POSE_LANDING_KNEE", "env_id": "ENV_GARDEN_GRID", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "media/badges/geez_logo_v1.mov", "blend": "screen", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Vertical 9:16 shot at ground level. Henoch (Silver-skin) kneeling on a pristine floor made of white ceramic tiles interlaced with glowing cyan circuit-moss. Geometric hard-light shards (remnants of the Merkabah) are retracting into his suit's spine. Soft, shadowless laboratory lighting. Clean, sterile, high-tech aesthetic.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Henoch (Voyager).
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Flight suit. Merkabah field dissolving.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** The Garden floor. Infinite white grid.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Global Illumination (White). Cyan bioluminescence from floor grooves.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Camera stabilizes from shake to perfect stillness. Slow push in. 9:16 aspect ratio.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Mechanical servo whir (retracting gear), soft boot-up chime, low frequency 40Hz hum.

## [ACT 2] [SCENE 2.2] [Timecode: 00:24-00:30] [SERVER FARM]
**Action:** Wide shot of the "trees" – vertical data stacks with fiber-optic foliage.
**Dialog:** -

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "wide", "framing": "extreme_wide", "environment": "Garden Server Farm", "env_change": false, "actors": [], "props": ["Server Trees"], "camera": "Dolly / Symmetry", "mood": ["sacred", "technological"], "director_intent": "Reveal the Garden as a massive data center.", "start_image_keywords": ["server trees", "fiber optic leaves", "white porcelain"], "start_image_mode": "env_only", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "ENV_SERVER_FOREST", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "media/badges/geez_logo_v1.mov", "blend": "screen", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Vertical 9:16 wide establishing shot. A symmetrical forest of "trees" that are actually tall, white porcelain server racks shaped like organic trunks. The foliage consists of thousands of cascading fiber-optic cables glowing with faint green light. The floor is mirrored. The ceiling is a diffused light box. Kubrick-esque one-point perspective.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** N/A.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** N/A.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** The Garden of Righteousness. Infinite rows.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Clinical white light. Soft green accents.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Slow, majestic dolly forward. Perfectly smooth motion. 9:16 aspect ratio.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Layered fan noise creating a "wind" effect, subtle data-processing clicks, serene atmosphere.

## [ACT 2] [SCENE 2.3] [Timecode: 00:30-00:36] [TREE OF WISDOM]
**Action:** Henoch approaches the central node. Liquid metal bark (Carob), violet data spheres.
**Dialog:** -

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "mixed", "shot_type": "medium", "framing": "medium", "environment": "Tree of Wisdom", "env_change": false, "actors": [{"name": "Henoch", "phase": "Voyager", "presence": "on_screen", "focus": "secondary"}], "props": ["Liquid Metal Tree", "Violet Spheres"], "camera": "Tracking / Orbit", "mood": ["mystery", "forbidden"], "director_intent": "Focus on the unique texture and danger of this specific node.", "start_image_keywords": ["liquid carob bark", "violet fruit", "smart matter"], "start_image_mode": "actor_in_env", "video_plan": {"start_comp": {"mode": "actor_first", "actor_pose_id": "POSE_WALK_AWE", "env_id": "ENV_TREE_WISDOM", "props": ["PROP_LIQUID_TREE"], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "media/badges/geez_logo_v1.mov", "blend": "screen", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Vertical 9:16 medium shot. Henoch stands before the Tree of Wisdom. The tree's bark is a viscous, flowing ferrofluid in a dark carob-brown hue, constantly rippling. The "fruits" are floating spheres of intense violet light containing scrolling data. The contrast between the dark liquid tree and the white room is stark.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Henoch (Voyager).
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Detailed flight suit back.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Center of the Garden.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Violet light casting purple rim light on Henoch's silver skin.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Slow orbit camera around the subject and tree. 9:16 aspect ratio.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Viscous liquid bubbling sound, electrical hum, high-pitched data resonance from the fruit.

## [ACT 2] [SCENE 2.4] [Timecode: 00:36-00:42] [DATA INSPECTION]
**Action:** Hand reaches for fruit. UI overlay: "YOTTABYTE // RESTRICTED".
**Dialog:** -

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "prop", "shot_type": "close_up", "framing": "extreme_close_up", "environment": "Tree Detail", "env_change": false, "actors": [{"name": "Henoch", "phase": "Voyager", "presence": "on_screen", "focus": "secondary"}], "props": ["Idris Glove", "Violet Sphere", "Holographic UI"], "camera": "Macro / Shallow Depth", "mood": ["temptation", "analysis"], "director_intent": "Highlight the immense data capacity of the fruit.", "start_image_keywords": ["idris glove", "violet data sphere", "restricted ui"], "start_image_mode": "prop_only", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "POSE_REACH", "env_id": "ENV_TREE_DETAIL", "props": ["PROP_UI_OVERLAY"], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "media/badges/geez_logo_v1.mov", "blend": "screen", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Vertical 9:16 macro shot. A silver gloved hand (Idris Glove) with golden filigree sensors reaching towards a pulsing violet data-sphere. A sharp, blue augmented reality label floats in focus: "FILE_SIZE: YOTTABYTE // ACCESS: RESTRICTED". Background is creamy bokeh of the liquid tree bark.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Henoch's hand.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Detailed glove texture.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Close to the tree node.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Violet glow from fruit illuminating the palm.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Slight focus hunting. Hand tremors slightly (hesitation). 9:16 aspect ratio.

### 3. AUDIO PROMPT (Hunyuan/Foley)
UI typing sound, warning beep (low volume), magnetic hum.

## [ACT 2] [SCENE 2.5] [Timecode: 00:42-00:46] [REACTION]
**Action:** Henoch looks up. Eyes spin (Solar Aperture). Captivated by the logic.
**Dialog:** "Dieser Baum... seine Schönheit ist Logik in Reinform."

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "close_up", "framing": "close_up", "environment": "Garden", "env_change": false, "actors": [{"name": "Henoch", "phase": "Voyager", "presence": "on_screen", "focus": "primary"}], "props": ["Solar Eyes"], "camera": "Portrait / Static", "mood": ["enlightenment", "awe"], "director_intent": "Show the protagonist understanding the system's beauty.", "start_image_keywords": ["solar aperture eyes", "silver face", "reflection"], "start_image_mode": "actor_only", "video_plan": {"start_comp": {"mode": "actor_first", "actor_pose_id": "POSE_FACE_AWE", "env_id": "ENV_GARDEN_BG", "props": [], "notes": ""}, "motion_driver": {"type": "a2f", "audio_id": "scene_2_5_audio", "pose_source": "", "driver_notes": "Subtle smile, eye apertures dilating"}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "media/badges/geez_logo_v1.mov", "blend": "screen", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 15}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Vertical 9:16 portrait of Henoch. His eyes are mechanical solar apertures, complex irises of gold and white metal, spinning to focus. His silver skin reflects the violet light of the tree. The background is a soft blur of the white garden. Expression is one of intellectual ecstasy.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Henoch (Voyager).
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Helmet removed (or clear).
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Standing before the tree.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Soft key light (White), Rim light (Violet).
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Very slow push in. 9:16 aspect ratio.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Camera lens focusing sound, internal gear whir, soft exhale.

## [ACT 2] [SCENE 2.6] [Timecode: 00:46-00:50] [FRAGRANCE WAVE]
**Action:** The "Scent" vents from the tree. Gold particles and heat haze distort the air.
**Dialog:** -

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "medium", "framing": "medium", "environment": "Tree of Wisdom", "env_change": false, "actors": [], "props": ["Gold Particles", "Heat Haze"], "camera": "Static / Texture", "mood": ["ethereal", "systemic"], "director_intent": "Visualize the 'fragrance' as cooling exhaust/data particles.", "start_image_keywords": ["gold particles", "heat distortion", "data mist"], "start_image_mode": "env_only", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "ENV_PARTICLE_FLOW", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "media/badges/geez_logo_v1.mov", "blend": "screen", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Vertical 9:16 abstract shot. The air around the dark liquid tree is filled with millions of floating gold particles. Heavy heat distortion waves ripple through the frame, blurring the background. The particles look like microscopic gold circuitry flakes. Magical realism meets thermodynamics.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** N/A.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** N/A.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** The Tree's immediate vicinity.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Gold glinting in the light. Dark tree silhouette.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Slow motion particle simulation. Heat haze effect active. 9:16 aspect ratio.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Hissing steam vent, wind chime texture, deep sub-bass vibration.

## [ACT 3] [SCENE 3.1] [Timecode: 00:50-00:55] [RAPHAEL MANIFESTS]
**Action:** Raphael (Admin) assembles from hard-light blocks. Chrome body, sensor face.
**Dialog:** -

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "full_body", "framing": "full_body", "environment": "Garden", "env_change": false, "actors": [{"name": "Raphael", "phase": "Archangel", "presence": "on_screen", "focus": "primary"}, {"name": "Henoch", "phase": "Voyager", "presence": "on_screen", "focus": "secondary"}], "props": ["Hologram Blocks"], "camera": "Tilt Up", "mood": ["divine", "synthetic"], "director_intent": "Introduce the guide as a superior technological entity.", "start_image_keywords": ["archangel raphael", "chrome android", "hologram assembly"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "POSE_MANIFEST_STAND", "env_id": "ENV_GARDEN_RAPHAEL", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "media/badges/geez_logo_v1.mov", "blend": "screen", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Vertical 9:16 hero shot. Archangel Raphael materializing next to Henoch. Raphael is a towering, sleek android made of polished chrome and white ceramic panels. He has no face, just a vertical array of blue laser sensors. He is partially formed from floating hard-light cubes. Blue holographic light bathes the scene.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Raphael (Archangel). Robotic/Abstract.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Chrome plating.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Beside Henoch.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Blue lens flares. Chrome reflections.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Tilt up from feet to head as he assembles. 9:16 aspect ratio.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Digital teleportation sound (transformer-like), metallic click-clack assembly, resonating thrum.

## [ACT 3] [SCENE 3.2] [Timecode: 00:55-01:02] [THE EXPLANATION]
**Action:** Raphael points. Voice waveform visualizer projects from his chest/face.
**Dialog:** "Dies ist der Baum der Weisheit, von dem dein alter Vater und deine betagte Mutter aßen."

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "medium", "framing": "medium", "environment": "Garden", "env_change": false, "actors": [{"name": "Raphael", "phase": "Archangel", "presence": "on_screen", "focus": "primary"}, {"name": "Henoch", "phase": "Voyager", "presence": "on_screen", "focus": "secondary"}], "props": ["Waveform UI"], "camera": "Two-Shot / Static", "mood": ["informative", "impersonal"], "director_intent": "Raphael speaks via data projection, not a mouth.", "start_image_keywords": ["waveform voice", "pointing finger", "chrome reflection"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "POSE_POINT", "env_id": "ENV_GARDEN_TALK", "props": [], "notes": ""}, "motion_driver": {"type": "a2f", "audio_id": "scene_3_2_audio", "pose_source": "", "driver_notes": "Waveform animates to speech"}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "media/badges/geez_logo_v1.mov", "blend": "screen", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 20}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Vertical 9:16 two-shot. Raphael points a chrome finger at the tree. In the air between them, a 3D blue waveform graphic pulsates, visualizing his voice. Henoch watches the graphic, not Raphael. Clean composition, rule of thirds.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Raphael (Left), Henoch (Right).
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Standard.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** The Garden.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Blue light from waveform.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Static camera. Only the waveform and Raphael's arm move. 9:16 aspect ratio.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Synthesized voice (flanging effect), data stream noise synchronized with speech.

## [ACT 3] [SCENE 3.3] [Timecode: 01:02-01:07] [HISTORY OVERLAY]
**Action:** AR Overlay of Adam/Eve (Lidar Point Cloud). They touch the fruit and turn red (Error).
**Dialog:** -

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "mixed", "shot_type": "wide", "framing": "wide", "environment": "Garden with AR", "env_change": false, "actors": [], "props": ["Point Cloud Figures", "Error Tags"], "camera": "Wide / Glitch", "mood": ["failure", "warning"], "director_intent": "Depict the original sin as a system error using forensic visualization.", "start_image_keywords": ["lidar point cloud", "red error", "adam eve"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "", "env_id": "ENV_AR_HISTORY", "props": ["PROP_LIDAR_FIGURES"], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "media/badges/geez_logo_v1.mov", "blend": "screen", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Vertical 9:16 shot of the tree. A high-fidelity green Lidar point-cloud overlay ghosted over reality. Two human figures (Adam, Eve) composed of dots interact with the tree. The dots turning from Green to Bright Red at the point of contact. "CRITICAL_FAILURE" text floating in 3D space. Forensic reconstruction aesthetic.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Point cloud figures.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** N/A.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** The Garden (dimmed).
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Green and Red emission points.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Camera jitters like a damaged video file. Glitch artifacts. 9:16 aspect ratio.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Loud error buzzer, static burst, deep distortion crunch.

## [ACT 3] [SCENE 3.4] [Timecode: 01:07-01:11] [THE DELETION]
**Action:** Reflection in Raphael's face. The red figures are deleted (particles disperse).
**Dialog:** "Und sie erkannten ihre Nacktheit und wurden aus dem Garten getilgt."

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "close_up", "framing": "extreme_close_up", "environment": "Reflection", "env_change": false, "actors": [{"name": "Raphael", "phase": "Archangel", "presence": "on_screen", "focus": "primary"}], "props": ["Chrome Face"], "camera": "Zoom In", "mood": ["finality", "cold"], "director_intent": "Show the expulsion as a data deletion event.", "start_image_keywords": ["chrome face reflection", "particle dispersion", "red figures"], "start_image_mode": "actor_only", "video_plan": {"start_comp": {"mode": "actor_first", "actor_pose_id": "POSE_HEAD_DOWN", "env_id": "ENV_REFLECTION", "props": [], "notes": ""}, "motion_driver": {"type": "a2f", "audio_id": "scene_3_4_audio", "pose_source": "", "driver_notes": "Raphael still"}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "media/badges/geez_logo_v1.mov", "blend": "screen", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 15}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Vertical 9:16 extreme close-up on Raphael's curved chrome faceplate. The reflection shows the red Lidar figures disintegrating into noise and vanishing, leaving emptiness. The laser array on Raphael's face dims.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Raphael's face.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Chrome.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Reflection space.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** High contrast metallic reflection.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Slow zoom in. 9:16 aspect ratio.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Vacuum suction sound (deletion), power-down whine, silence.

## [ACT 3] [SCENE 3.5] [Timecode: 01:11-01:15] [STASIS]
**Action:** Wide shot. Garden is an island in a void of static.
**Dialog:** -

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "wide", "framing": "extreme_wide", "environment": "Void Island", "env_change": true, "actors": [{"name": "Henoch", "phase": "Voyager", "presence": "on_screen", "focus": "secondary"}, {"name": "Raphael", "phase": "Archangel", "presence": "on_screen", "focus": "secondary"}], "props": ["Floating Platform"], "camera": "Crane / Pull Back", "mood": ["isolated", "existential"], "director_intent": "The final reveal of the simulation's limits.", "start_image_keywords": ["floating island", "static void", "tiny figures"], "start_image_mode": "env_only", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "ENV_VOID_ISLAND", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "media/badges/geez_logo_v1.mov", "blend": "screen", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Vertical 9:16 ultra-wide shot. The white Garden of Righteousness is revealed to be a solitary floating platform suspended in an endless void of grey TV static and white noise. Henoch and Raphael are microscopic dots on the grid. The Tree glows in the center.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Tiny figures.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** N/A.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** The Void.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** The Garden is self-illuminated against the grey background.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Crane up and pull back into the void. Fade out. 9:16 aspect ratio.

### 3. AUDIO PROMPT (Hunyuan/Foley)
White noise rising in volume, wind howling, abrupt cut to black.

## ACTOR MONOLOGUE PLAN (JSON)
MONOLOGUE_JSON: {"actors":{"Henoch":[{"scene":"2.5","text":"Dieser Baum... seine Schönheit ist Logik in Reinform.","words_max":10}],"Raphael":[{"scene":"3.2","text":"Dies ist der Baum der Weisheit, von dem dein alter Vater und deine betagte Mutter aßen.","words_max":20},{"scene":"3.4","text":"Und sie erkannten ihre Nacktheit und wurden aus dem Garten getilgt.","words_max":15}]},"notes":"German only. Short internal monologues. Do not describe the camera or list what is visible. Use emotion, memory, and cause-effect logic. Keep total lines per chapter low (3-7). JSON must be in one line."}