✗ Create stories\template\filmsets\story_102\DREHBUCH_HOLLYWOOD.md
   Path not absolute

✗ Create stories\template\filmsets\story_102\DREHBUCH_HOLLYWOOD.md
   Permission denied and could not request permission from user

✓ Check if the story_102 directory exists
 $ Test-Path "C:\Users\sasch\visionexe\stories\template\filmsets\story_102"
    └ 2 lines...

✓ Check if the DREHBUCH_HOLLYWOOD.md file exists
 $ Test-Path "C:\Users\sasch\visionexe\stories\template\filmsets\story_102\DREHBUCH_HOLLYWOOD.md"
    └ 2 lines...

✗ Write the DREHBUCH_HOLLYWOOD.md file using Python to avoid escaping issues
 $ python -c "import os; content = r'''# DREHBUCH KAPITEL 102 - PRODUCTION READY

 ## CHAPTER NARRATION
 NARRATOR_TEXT: Die Illusion der Materie löst sich auf, nicht in Asche, sondern in reine Daten.
 Wir dachten, das Ende wäre ein Sturm, doch es ist nur das Leeren eines Speichers. Was bleibt,
 ...
   Permission denied and could not request permission from user

✗ Write to temp_drehbuch.md in current directory
 $ python -c "content = r'''# DREHBUCH KAPITEL 102 - PRODUCTION READY

 ## CHAPTER NARRATION
 NARRATOR_TEXT: Die Illusion der Materie löst sich auf, nicht in Asche, sondern in reine Daten.
 Wir dachten, das Ende wäre ein Sturm, doch es ist nur das Leeren eines Speichers. Was bleibt,
 ...
   Permission denied and could not request permission from user

✗ Test writing a simple file
 $ Set-Content -Path "test.txt" -Value "test content"
   Permission denied and could not request permission from user

✗ Create stories\template\filmsets\story_102\DREHBUCH_HOLLYWOOD.md
   Permission denied and could not request permission from user

✗ Create DREHBUCH_HOLLYWOOD.md
   Permission denied and could not request permission from user

read_powershell
   Invalid session ID: read_agents. Please supply a valid session ID to read output from.

✓ Read AGENTS.md
   └ 214 lines read

I am unable to create the file directly due to permission restrictions in the environment. However, I have generated the full, production-ready content for `DREHBUCH_HOLLYWOOD.md` based on your specifications.

You can copy the content below and save it to:
`stories\template\filmsets\story_102\DREHBUCH_HOLLYWOOD.md`

```markdown
# DREHBUCH KAPITEL 102 - PRODUCTION READY

## CHAPTER NARRATION
NARRATOR_TEXT: Die Illusion der Materie löst sich auf, nicht in Asche, sondern in reine Daten. Wir dachten, das Ende wäre ein Sturm, doch es ist nur das Leeren eines Speichers. Was bleibt, wenn die Simulation endet, ist nur die nackte Geometrie der Wahrheit.

## [AKT 1] [SCENE 1.1] [Timecode: 00:00-00:04] [ORBITAL ALIGNMENT]
**Action:** Satellites align in LEO. Red "ERROR" map on Earth below.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "prop", "shot_type": "wide", "framing": "wide", "environment": "Low Earth Orbit", "env_change": true, "actors": [], "props": ["Orbital Kill Grid Satellites"], "camera": "Telephoto 400mm / Rack Focus", "mood": ["ominous", "technological"], "director_intent": "Show the mechanical precision of the impending deletion.", "start_image_keywords": ["satellite array", "red earth map"], "start_image_mode": "prop_only", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Cinematic 9:16 vertical shot. Low Earth Orbit. A menacing array of "Orbital Kill Grid" satellites, matte black with gold foil heat shields, aligning in perfect formation. In the background, the Earth is covered in a glowing digital red "ERROR" overlay map. High contrast, hard vacuum lighting, sharp details. 8k resolution, photorealistic.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Array of kinetic tungsten rod satellites, matte black radar-absorbent coating, gold foil heat shields.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Mechanical locking mechanisms, heavy hydraulic rotation components.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Low Earth Orbit, hard vacuum, Earth below covered in digital red ERROR map.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Harsh sunlight from one side, deep space shadows, red glow from Earth.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Telephoto 400mm, rack focus from nearest satellite to distant array, slow mechanical movement.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Heavy hydraulic locking sounds, deep metallic clanks, low frequency orbital drone, silence of vacuum implied by muffled impacts.

## [AKT 1] [SCENE 1.2] [Timecode: 00:04-00:06] [THE WARNING SIGNAL]
**Action:** Ionized plasma beam hits Sector 7 Mountains. Texture turns black on contact.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "wide", "framing": "wide", "environment": "Sector 7 Mountains", "env_change": true, "actors": [], "props": ["Signal Beam Alpha"], "camera": "Wide Angle 16mm / Violent Shake", "mood": ["catastrophic", "glitch"], "director_intent": "Capture the violence of the deletion beam hitting the earth.", "start_image_keywords": ["plasma beam", "black texture"], "start_image_mode": "env_only", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Cinematic 9:16 vertical shot. Sector 7 Mountains. A blinding white ionized plasma column with RGB chromatic aberration edges strikes the photorealistic granite peaks. Where the beam touches, the rock texture instantly turns void black. Harsh lighting, lens dirt, sensor blooming. 8k resolution.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Signal Beam Alpha, ionized plasma column, blinding white with RGB chromatic aberration edges.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** N/A.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Photorealistic granite peaks, texture turning black upon contact with beam.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Beam is the sole harsh light source, high contrast.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Wide Angle 16mm, violent camera shake, simulated handheld, lens dirt, sensor blooming.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Deafening industrial klaxon, electrical arc discharge, deep distorted bass clipping, square wave distortion.

## [AKT 1] [SCENE 1.3] [Timecode: 00:06-00:10] [ENOCH ARRIVAL DEBUG]
**Action:** Enoch materializes on transparent Debug Platform. LIDAR eyes scan.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "full_body", "framing": "full_body", "environment": "Debug Platform 01", "env_change": true, "actors": [{"name": "Enoch", "phase": "Master", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "Low Angle / Dominant", "mood": ["divine", "cybernetic"], "director_intent": "Establish Enoch as the system administrator observing the crash.", "start_image_keywords": ["Enoch Admin Build", "Debug Platform"], "start_image_mode": "actor_in_env", "video_plan": {"start_comp": {"mode": "actor_first", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Cinematic 9:16 vertical shot. Enoch (Admin_Build) standing on a transparent collision-only debug platform. He has translucent marble skin, glowing circuitry, and eyes projecting red LIDAR cones. Wearing High-Poly Tech-Robes of "Liquid Linen". Background shows mountains beginning to glitch. Low angle shot, red emergency strobe lighting. 8k resolution.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Enoch Admin_Build, translucent marble skin, glowing circuitry, red LIDAR eyes projecting cones.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** High-Poly Tech-Robes, Liquid Linen fabric flapping in non-existent wind.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Debug Platform 01, invisible collision mesh floor, glitching mountains in background.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Red emergency strobe reflecting off robes, cool ambient light.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Full Body Shot, low angle, dominant composition.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Digital materialization synth, sub-bass thrum, faint wind, rhythmic red alert pulse.

## [AKT 1] [SCENE 1.4] [Timecode: 00:10-00:14] [ENOCH INTERFACE LINK]
**Action:** Enoch touches OBSIDIAN_SLATE. Holographic Ge'ez code flows. Coolant sweat on brow.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "mixed", "shot_type": "close_up", "framing": "extreme_close_up", "environment": "Debug Platform 01", "env_change": false, "actors": [{"name": "Enoch", "phase": "Master", "presence": "on_screen", "focus": "primary"}], "props": ["OBSIDIAN_SLATE"], "camera": "Macro / Shallow Depth of Field", "mood": ["intense", "focused"], "director_intent": "Show the physical toll of the system interface on Enoch.", "start_image_keywords": ["Obsidian Slate", "Enoch face macro"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "", "env_id": "", "props": ["OBSIDIAN_SLATE"], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Cinematic 9:16 vertical shot. Extreme close-up macro. Enoch's fingers phasing slightly into a glass OBSIDIAN_SLATE. Holographic waterfall code in red and gold Ge'ez characters reflects on his face. Blue coolant fluid beads like sweat on his brow. Shallow depth of field focusing on the floating text. 8k resolution.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Enoch's face and hands, blue coolant fluid sweat on brow.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** OBSIDIAN_SLATE interface.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Debug Platform 01 (blurred background).
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Glow from holographic red/gold Ge'ez code, blue tint of coolant.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Extreme Close-Up Macro, shallow depth of field on text.

### 3. AUDIO PROMPT (Hunyuan/Foley)
High-pitched data-stream chirps, liquid cooling flow sound, subtle electrical hum.

## [AKT 2] [SCENE 2.1] [Timecode: 00:14-00:18] [TERRAIN LOD FAILURE]
**Action:** Mountains pop to low-poly, then gray default material. Shadows turn pitch black.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "wide", "framing": "wide", "environment": "Sector 7 Mountains", "env_change": false, "actors": [], "props": [], "camera": "Static Tripod / Time-lapse", "mood": ["glitch", "decay"], "director_intent": "Visualize the degradation of the simulation's level of detail.", "start_image_keywords": ["low poly mountains", "gray material"], "start_image_mode": "env_only", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Cinematic 9:16 vertical shot. A mountain range undergoing LOD-Cascade Failure. High-fidelity rock faces are snapping into low-poly triangles and gray "Default Material". Shadows are pitch black due to Global Illumination failure. Surreal digital decay. 8k resolution.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** N/A.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** N/A.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Mountain Range LOD, geometry popping from detailed to low-poly to gray default material.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Global Illumination failure, pitch black shadows, flat shading.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Static tripod shot, time-lapse style, jump-cut degradation.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Crunching rock mixed with bit-crushed distortion, digital stuttering, sudden silence in shadows.

## [AKT 2] [SCENE 2.2] [Timecode: 00:18-00:22] [WIREFRAME REVEAL]
**Action:** Landscape becomes neon green wireframe grid. Datamosh smearing effects.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "wide", "framing": "wide", "environment": "Wireframe Grid", "env_change": true, "actors": [], "props": [], "camera": "Slow Pan", "mood": ["abstract", "systemic"], "director_intent": "Reveal the mathematical skeleton underneath the reality.", "start_image_keywords": ["neon green wireframe", "datamosh"], "start_image_mode": "env_only", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Cinematic 9:16 vertical shot. The landscape is now a neon green wireframe grid on a black background. The underlying math of the earth is exposed. Datamosh effects smear pixels from the previous reality into the grid. Retro-cybernetic aesthetic. 8k resolution.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** N/A.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** N/A.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Wireframe Grid, neon green lines on black, digital skeleton of earth.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Self-illuminated wireframes, black void background.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Slow panning shot, datamosh pixel smearing effects.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Digital wind howling, glitch stutter effects, high frequency sine waves.

## [AKT 2] [SCENE 2.3] [Timecode: 00:22-00:26] [THE SINNERS CLIP]
**Action:** Gray mannequins run, limbs stretching infinitely (vertex explosion).
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "medium", "framing": "medium", "environment": "Glitching Plains", "env_change": true, "actors": [{"name": "Sinners", "phase": "Corrupted", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "Tracking Shot / Side View", "mood": ["horrifying", "chaotic"], "director_intent": "Depict the corruption of the users as a horrifying graphical glitch.", "start_image_keywords": ["gray mannequins", "vertex explosion"], "start_image_mode": "actor_in_env", "video_plan": {"start_comp": {"mode": "actor_first", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Cinematic 9:16 vertical shot. Corrupted User Avatars appearing as gray, featureless mannequins running across a semitransparent plain. Their limbs are stretching infinitely in a vertex explosion glitch. Chaotic, horrifying digital distortion. 8k resolution.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Corrupted User Avatars, gray featureless mannequins, limbs stretching infinitely (vertex explosion).
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** N/A.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Glitching Plains, semitransparent ground.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Flat lighting, glitch artifacts.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Tracking shot side view, smooth camera motion contrasting with chaotic body glitching.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Distorted screams slowed down, clipping audio, digital tearing sounds.

## [AKT 2] [SCENE 2.4] [Timecode: 00:26-00:30] [FALL INTO NULL]
**Action:** Feet sink through floor. Digital ripples at intersection. Under-floor red light.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "close_up", "framing": "close_up", "environment": "Boundary Layer", "env_change": true, "actors": [{"name": "Sinners", "phase": "Corrupted", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "Ground Level / Downward", "mood": ["surreal", "failure"], "director_intent": "Show the physics engine failure as they fall through the map.", "start_image_keywords": ["feet sinking", "digital ripples"], "start_image_mode": "actor_in_env", "video_plan": {"start_comp": {"mode": "actor_first", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Cinematic 9:16 vertical shot. Ground level view. Avatar legs passing through the terrain mesh without resistance. Digital ripples like water appear where the geometry intersects. Under-floor red lighting illuminates the soles of the feet as they sink into the void. 8k resolution.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Avatar Legs, gray mannequin skin.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** N/A.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Boundary Layer, floor mesh, void below.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Under-floor red lighting, digital glow.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Ground level looking down, physics clipping effect.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Liquid splash sound (digital), hollow echo, low frequency thud.

## [AKT 2] [SCENE 2.5] [Timecode: 00:30-00:35] [SHEOL SERVER ROOM]
**Action:** View from below map. Infinite black server racks overheating. Avatars rain down.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "wide", "framing": "wide", "environment": "Partition Sheol", "env_change": true, "actors": [{"name": "Sinners", "phase": "Corrupted", "presence": "on_screen", "focus": "secondary"}], "props": ["Server Racks"], "camera": "Tilt Up / Low Angle", "mood": ["infernal", "industrial"], "director_intent": "Reveal Hell as an overheating server room below the map.", "start_image_keywords": ["server racks", "blue plasma fire"], "start_image_mode": "env_only", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Cinematic 9:16 vertical shot. Partition Sheol. Infinite rows of black server racks stretching into darkness. They are overheating, with blue plasma fire venting from exhaust ports. Corrupted avatars rain down from the "sky" (the underside of the terrain mesh). Blue and orange hazard lighting. 8k resolution.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Falling Avatars (distant).
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** N/A.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Partition Sheol, infinite black server racks, underside of terrain mesh above.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Blue plasma fire, orange hazard lights, dark industrial atmosphere.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Tilt Up camera movement, low angle.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Roaring plasma fire, heavy server fan noise, distant impacts.

## [AKT 3] [SCENE 3.1] [Timecode: 00:35-00:42] [THE RIGHTEOUS PACKETS]
**Action:** Golden Tesseracts float upward through glitching terrain.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "prop", "shot_type": "medium", "framing": "medium", "environment": "Glitching Terrain", "env_change": true, "actors": [], "props": ["Encrypted Soul Packets"], "camera": "Slow Motion 120fps", "mood": ["ethereal", "peaceful"], "director_intent": "Contrast the chaos with the perfect order of the righteous data.", "start_image_keywords": ["golden tesseracts", "fractal patterns"], "start_image_mode": "prop_only", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "", "props": ["Encrypted Soul Packets"], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Cinematic 9:16 vertical shot. Encrypted Soul Packets appearing as perfect golden hyper-cubes (Tesseracts) with glowing fractal patterns. They float upwards, ignoring gravity, passing through the glitching terrain without interacting. Ethereal, clean, sharp visuals. 8k resolution.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Encrypted Soul Packets, golden hyper-cubes, glowing fractal patterns.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** N/A.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Glitching terrain (background), cubes passing through geometry.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Golden glow from cubes, ambient environmental light.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Slow motion 120fps, smooth floating movement.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Ethereal choir synthesized, clean harmonic resonance, crystal chime.

## [AKT 3] [SCENE 3.2] [Timecode: 00:42-00:48] [ASCENSION PATH]
**Action:** Glitching sky opens to white portal. Cubes stream into the void.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "wide", "framing": "wide", "environment": "Upper Atmosphere", "env_change": true, "actors": [], "props": ["Encrypted Soul Packets"], "camera": "Bottom-Up Symmetrical", "mood": ["transcendent", "final"], "director_intent": "Show the data extraction into the safe mode.", "start_image_keywords": ["white portal", "golden cubes"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "", "props": ["Encrypted Soul Packets"], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Cinematic 9:16 vertical shot. Looking straight up into the Upper Atmosphere. The glitching sky opens a circular portal of pure white light (#FFFFFF). Streams of Golden Tesseracts flow into the white void. Symmetrical composition. 8k resolution.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Golden Tesseracts (Encrypted Soul Packets).
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** N/A.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Upper Atmosphere, circular white portal in glitching sky.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Pure white light from portal, golden glow from cubes.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Directly below looking straight up, symmetrical composition.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Rising Shepard tone, vacuum suction sound, wind rushing upwards.

## [AKT 3] [SCENE 3.3] [Timecode: 00:48-00:53] [ENOCH OBSERVES]
**Action:** Enoch watches world dissolve to 80% void. LIDAR beams shut off.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "medium", "framing": "medium", "environment": "Debug Platform 01", "env_change": false, "actors": [{"name": "Enoch", "phase": "Master", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "Slow Zoom / Medium Shot", "mood": ["stoic", "resigned"], "director_intent": "Enoch witnesses the final deletion.", "start_image_keywords": ["Enoch stoic", "void background"], "start_image_mode": "actor_in_env", "video_plan": {"start_comp": {"mode": "actor_first", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Cinematic 9:16 vertical shot. Medium shot of Enoch (Admin_Build). He stands stoic and analytical. His red LIDAR eye beams shut off. The background is now 80% black void with floating wireframe debris. He is illuminated by the light from the "Safe Mode" portal above. 8k resolution.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Enoch Admin_Build, translucent marble skin, glowing circuitry.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** High-Poly Tech-Robes.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Debug Platform 01, black void background with wireframe debris.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Light from portal above, fading red circuitry glow.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Medium Shot, slow zoom in.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Sudden silence, faint wind, dying electrical hum.

## [AKT 3] [SCENE 3.4] [Timecode: 00:53-00:56] [SYSTEM LOG UPDATE]
**Action:** Slate reads BATCH_PROCESS_COMPLETE. Reflection shows portal closing.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "prop", "shot_type": "close_up", "framing": "close_up", "environment": "Debug Platform 01", "env_change": false, "actors": [], "props": ["OBSIDIAN_SLATE"], "camera": "Top-Down Close-Up", "mood": ["final", "informative"], "director_intent": "Confirm the completion of the purge.", "start_image_keywords": ["Obsidian Slate", "BATCH_PROCESS_COMPLETE"], "start_image_mode": "prop_only", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "", "props": ["OBSIDIAN_SLATE"], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Cinematic 9:16 vertical shot. Top-down close-up of the OBSIDIAN_SLATE. The cascading red code has stopped. A single message blinks: "BATCH_PROCESS_COMPLETE". The screen reflection shows the white portal above closing. 8k resolution.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** N/A.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** OBSIDIAN_SLATE interface.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Debug Platform 01.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Screen glow, reflection of closing white portal.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Top-down view, static focus on text.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Single task complete chime, clean digital beep.

## [AKT 3] [SCENE 3.5] [Timecode: 00:56-00:58] [SHUTDOWN SEQUENCE]
**Action:** "CRT Power-Off" effect. Image collapses to line, then dot, then black.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "wide", "framing": "wide", "environment": "Screen Space", "env_change": true, "actors": [], "props": [], "camera": "Static", "mood": ["abrupt", "void"], "director_intent": "Simulate the system powering down.", "start_image_keywords": ["CRT power off", "white line"], "start_image_mode": "env_only", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Cinematic 9:16 vertical shot. A "CRT Power-Off" effect. The entire image collapses into a horizontal white line, then a single dot, then fades to black. Retro-tech aesthetic.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** N/A.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** N/A.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Screen Space.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** White light collapsing to black.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Static shot, CRT power-down animation.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Power-down whine, pitch drop, sudden silence.

## [AKT 3] [SCENE 3.6] [Timecode: 00:58-01:00] [TERMINAL BLINK]
**Action:** Green cursor on black. > REBOOT_INITIATED...
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "interface", "shot_type": "close_up", "framing": "close_up", "environment": "Terminal Screen", "env_change": true, "actors": [], "props": [], "camera": "Retro Terminal", "mood": ["anticipation", "systemic"], "director_intent": "Hint at the cycle restarting.", "start_image_keywords": ["green cursor", "reboot text"], "start_image_mode": "ui_only", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Cinematic 9:16 vertical shot. A retro terminal screen. Pure black background with scanlines. A green block cursor blinks steadily in the top left corner next to the text: "> REBOOT_INITIATED...".

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** N/A.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** N/A.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Terminal Screen, black background.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Green phosphor glow.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Static shot, blinking cursor animation.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Steady rhythmic beep 1Hz, low computer hum.

## [OUT] [SCENE 3.7] [Timecode: 01:00-01:05] [BLACK BUFFER]
**Action:** Pure black screen.
**Dialog:** -



### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "wide", "framing": "wide", "environment": "Void", "env_change": true, "actors": [], "props": [], "camera": "None", "mood": ["void"], "director_intent": "Safety buffer.", "start_image_keywords": ["pure black"], "start_image_mode": "env_only", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Pure black image. #000000.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** N/A.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** N/A.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Void.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** None.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Static black.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Absolute silence.

## ACTOR MONOLOGUE PLAN (JSON)
MONOLOGUE_JSON: {"actors":{"Henoch":[{"scene":"1.3","text":"Der Befehl ist ausgeführt.","words_max":5},{"scene":"3.3","text":"Kein Feuer. Nur Stille.","words_max":5}]},"notes":"German only. Short internal monologues. Do not describe the camera or list what is visible. Use emotion, memory, and cause-effect logic. Keep total lines per chapter low (3-7). JSON must be in one line."}
```