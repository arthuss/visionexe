✓ Check existing filmsets to determine the correct path for Chapter 5
 $ Get-ChildItem -Path C:\Users\sasch\visionexe\stories\template\filmsets
    └ 114 lines...

✗ Create stories\template\filmsets\story_005\DREHBUCH_HOLLYWOOD.md
   Permission denied and could not request permission from user

✓ Check if the screenplay file already exists
 $ Test-Path C:\Users\sasch\visionexe\stories\template\filmsets\story_005\DREHBUCH_HOLLYWOOD.md
    └ 2 lines...

✗ Write the generated screenplay content to the file using PowerShell
 $ $content = @"
 # DREHBUCH KAPITEL 5 - PRODUCTION READY

 ## CHAPTER NARRATION
 NARRATOR_TEXT: Das System schläft nie, doch es träumt von Ordnung. Ich sehe die Welt nicht mehr
 ...
   Permission denied and could not request permission from user

# DREHBUCH KAPITEL 5 - PRODUCTION READY

## CHAPTER NARRATION
NARRATOR_TEXT: Das System schläft nie, doch es träumt von Ordnung. Ich sehe die Welt nicht mehr als Fleisch und Stein, sondern als endlosen Strom von Daten, der auf Validierung wartet. Wo Fehler wuchern, muss der Code bereinigt werden, damit die Ewigkeit beginnen kann.

## ACT I SCENE 1.1 [Timecode: 00:00-00:05] SYSTEM AUDIT INITIATED
**Action:** Orthographische Draufsicht auf einen Wald. Ein grünes Laser-Grid scannt die Baumkronen. Text-Overlay: "SYSTEM AUDIT: INITIATED".
**Dialog:** -

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "establishing", "framing": "wide", "environment": "Forest Canopy from Satellite View", "env_change": true, "actors": [], "props": ["Green Laser Grid", "HUD Overlay"], "camera": "Top-Down Satellite View, Zoom-In", "mood": ["awe", "clinical"], "director_intent": "Establish the world as a scanned data-construct.", "start_image_keywords": ["satellite view", "forest", "laser grid"], "start_image_mode": "env_only", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}

### 1. START IMAGE PROMPT (Midjourney/Flux)
Satellite view of a dense, ancient forest, viewed directly from above. A bright green, digital laser grid overlays the organic canopy, scanning it. Floating holographic text in a sterile font reads "SYSTEM AUDIT: INITIATED". The aesthetic is high-tech industrial mysticism, sharp 85mm macro details visible even from this distance, photorealistic, cinematic lighting, 8k resolution.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** N/A
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** N/A
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Dense forest canopy, deep greens, overlaid with a glowing green digital grid structure.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Sunlight filtering through leaves, contrasted with the artificial neon green of the laser scan.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Top-down orthographic camera. Rapid zoom-in from high altitude directly into the texture of the trees. Hard cut transition at the end.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Deep, rhythmic server humming at 50Hz. A digital start-up chime echoes. Subtle wind noise blending with the sound of cooling fans.

## ACT I SCENE 1.2 [Timecode: 00:05-00:10] MACRO COMPLIANCE
**Action:** Ein einzelnes Blatt entfaltet sich. Die Adern des Blattes leuchten kurz golden auf (Datenfluss). Henochs Hand streicht darüber, ohne es zu berühren.
**Dialog:** -

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "mixed", "shot_type": "insert", "framing": "extreme_close_up", "environment": "Forest Detail", "env_change": false, "actors": [{"name": "Henoch", "phase": "Proxy", "presence": "on_screen", "focus": "secondary"}], "props": ["Glowing Leaf"], "camera": "85mm Macro, Smooth Glide", "mood": ["wonder", "precision"], "director_intent": "Show the biological world as a perfect, data-driven system.", "start_image_keywords": ["leaf", "golden veins", "hand"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 10}

### 1. START IMAGE PROMPT (Midjourney/Flux)
Extreme close-up of a single green leaf. The veins of the leaf are glowing with a liquid golden light, resembling data circuitry. A weathered, dust-covered human hand hovers just millimeters above the surface, not touching it. High contrast, texture-rich, 85mm macro photography, depth of field blurring the background.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Henoch's hand, weathered skin, dirt in fingernails.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Simple linen sleeve visible at the edge.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Close-up of a leaf surface, microscopic details visible.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Natural light with internal golden luminescence from the leaf veins.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Slow, smooth camera glide following the hand. The leaf unfurls slightly. 60fps smoothness.

### 3. AUDIO PROMPT (Hunyuan/Foley)
The sharp click of precision relays. The sound of wind rustling leaves, but processed to sound like white noise.

## ACT I SCENE 1.3 [Timecode: 00:10-00:15] OCULAR DEBUG
**Action:** Henochs Gesicht, Close-Up. Seine Augen scannen schnell (Saccades). HUD-Reflexion in der Iris zeigt "FLORA: COMPLIANT".
**Dialog:** -

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "close_up", "framing": "extreme_close_up", "environment": "Forest Background (Blurred)", "env_change": false, "actors": [{"name": "Henoch", "phase": "Proxy", "presence": "on_screen", "focus": "primary"}], "props": ["HUD Reflection"], "camera": "35mm Portrait, Shallow Depth of Field", "mood": ["focused", "analytical"], "director_intent": "Establish Henoch as the interface between man and machine.", "start_image_keywords": ["eye", "iris", "HUD"], "start_image_mode": "actor_only", "video_plan": {"start_comp": {"mode": "actor_first", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}

### 1. START IMAGE PROMPT (Midjourney/Flux)
Extreme close-up of Henoch's eyes. The iris is mechanically detailed, rotating like a camera aperture. A green digital HUD reflection on the cornea reads "FLORA: COMPLIANT". The skin around the eye is textured, sweaty, and realistic. The background is a soft green bokeh. Cinematic lighting, high detail.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Henoch's face, focus on eyes.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** N/A
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Blurred forest background.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Soft daylight on face, sharp green light from the HUD reflection.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Whip pan transition into the shot. Rapid eye movements (saccades). The iris rotates mechanically.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Quiet, rhythmic sonar pinging. The mechanical whir of a camera lens focusing.

## ACT II SCENE 2.1 [Timecode: 00:15-00:20] THE GLITCH
**Action:** Schnitt auf eine Menschenmenge (Die Sünder). Sie bewegen sich ruckartig. Ihre Silhouetten flackern. Die Umgebung um sie herum verliert Textur-Auflösung.
**Dialog:** -

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "mixed", "shot_type": "medium", "framing": "medium", "environment": "Corrupted Terrain", "env_change": true, "actors": [{"name": "Sinners", "phase": "Glitch", "presence": "on_screen", "focus": "primary"}], "props": ["Glitch Artifacts"], "camera": "Handheld, Shaky Cam, 45° Shutter", "mood": ["tension", "unease"], "director_intent": "Visualize sin as a rendering error.", "start_image_keywords": ["glitch", "crowd", "low poly"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}

### 1. START IMAGE PROMPT (Midjourney/Flux)
A crowd of humanoid figures in a gray, desolate environment. The figures are suffering from severe mesh corruption—polygons stretching, textures tearing, silhouettes flickering. They have no distinct faces, just digital noise. The ground beneath them is losing texture resolution, revealing a wireframe grid. Industrial horror, high contrast, chaotic composition.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Faceless humanoid figures, distorted anatomy.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Rags that merge with their skin.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Gray, textureless void with z-fighting on walls.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Flickering strobe lighting, cold and harsh.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Handheld shaky cam style. 45-degree shutter angle for jerky motion. Glitch-wipe transition.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Sudden burst of static noise. High-pitched coil whine. The sound of digital stuttering.

## ACT II SCENE 2.2 [Timecode: 00:20-00:25] ERROR LOG
**Action:** Ein Sünder öffnet den Mund. Statt Sprache tritt schwarzer Rauch (Daten-Entropie) aus. Der Rauch frisst Löcher in den Boden (Mesh-Collapse).
**Dialog:** -

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "close_up", "framing": "close_up", "environment": "Corrupted Terrain", "env_change": false, "actors": [{"name": "Sinner", "phase": "Glitch", "presence": "on_screen", "focus": "primary"}], "props": ["Black Smoke", "Voxel Debris"], "camera": "Low Angle, Threatening", "mood": ["horror", "disgust"], "director_intent": "Show speech as a destructive force.", "start_image_keywords": ["scream", "black smoke", "voxels"], "start_image_mode": "actor_only", "video_plan": {"start_comp": {"mode": "actor_first", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}

### 1. START IMAGE PROMPT (Midjourney/Flux)
Low angle close-up of a corrupted humanoid figure opening its mouth wide in a silent scream. Thick, black, voxelated smoke pours out, resembling data entropy. Where the smoke touches the ground, the floor dissolves into a wireframe mesh. The figure's skin is gray and pixelated. Cinematic lighting, dark atmosphere.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Corrupted humanoid, gaping mouth.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** N/A
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Dark, collapsing ground.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Dim, ominous lighting.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Jump cut transition. The smoke billows aggressively. The ground mesh collapses upon contact.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Distorted, bit-crushed vocalizations. A muffled warning siren in the distance.

## ACT II SCENE 2.3 [Timecode: 00:25-00:30] BIOMETRIC FEEDBACK
**Action:** Henoch zuckt zusammen. Biometrisches Feedback. Adern an seiner Schläfe pulsieren dunkel. Er spürt den Systemfehler physisch.
**Dialog:** -

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "close_up", "framing": "extreme_close_up", "environment": "Abstract Background", "env_change": false, "actors": [{"name": "Henoch", "phase": "Proxy", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "Extreme Close-Up (Temple)", "mood": ["pain", "visceral"], "director_intent": "Connect the system error to physical suffering.", "start_image_keywords": ["temple", "veins", "sweat"], "start_image_mode": "actor_only", "video_plan": {"start_comp": {"mode": "actor_first", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 10}

### 1. START IMAGE PROMPT (Midjourney/Flux)
Extreme close-up of Henoch's temple and eye. Beads of sweat mix with dirt. The veins under his skin are pulsing with a dark, unnatural color. His skin looks pale and strained. The expression is one of sudden, sharp pain. High detail, realistic skin texture, dramatic lighting.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Henoch's face, temple area.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** N/A
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Blurred background.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Harsh side lighting emphasizing skin texture.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Hard cut. The veins pulse rhythmically. Facial muscles twitch in a micro-spasm.

### 3. AUDIO PROMPT (Hunyuan/Foley)
A loud, amplified heartbeat with a metallic echo.

## ACT II SCENE 2.4 [Timecode: 00:30-00:35] CRITICAL ERROR
**Action:** Die "harten Worte" der Sünder manifestieren sich als scharfe, gezackte Geometrie, die durch die Luft schneidet. Rote Warn-Boxen "CRITICAL ERROR" poppen im Raum auf.
**Dialog:** -

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "mixed", "shot_type": "wide", "framing": "wide", "environment": "Chaotic Void", "env_change": true, "actors": [], "props": ["Geometric Shards", "Error Boxes"], "camera": "Wide Shot, Chaotic Movement", "mood": ["chaos", "danger"], "director_intent": "Visualize the spread of corruption.", "start_image_keywords": ["shards", "red error box", "chaos"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}

### 1. START IMAGE PROMPT (Midjourney/Flux)
A chaotic scene filled with sharp, jagged geometric shards flying through the air like shrapnel. Bright red floating boxes with the text "CRITICAL ERROR" clutter the visual field. The background is a swirling mess of gray noise and distorted polygons. High energy, aggressive composition.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** N/A
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** N/A
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Abstract chaotic space.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Flashing red warning lights.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Stutter-edit style with simulated frame drops. Fast, chaotic movement of the shards.

### 3. AUDIO PROMPT (Hunyuan/Foley)
High-pitched electronic squealing. Sounds of breaking glass.

## ACT II SCENE 2.5 [Timecode: 00:35-00:40] RENDER PRIVILEGES REVOKED
**Action:** Henoch hebt die Hand. Ein roter Laser-Scanner markiert die korrupten Bereiche. Die Sünder werden in Wireframe-Modus gezwungen (Entzug der Render-Privilegien).
**Dialog:** -

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "mixed", "shot_type": "medium", "framing": "medium", "environment": "Corrupted Terrain", "env_change": false, "actors": [{"name": "Henoch", "phase": "Proxy", "presence": "on_screen", "focus": "primary"}, {"name": "Sinners", "phase": "Wireframe", "presence": "on_screen", "focus": "secondary"}], "props": ["Red Laser Scan"], "camera": "Tracking Shot, Fast", "mood": ["judgment", "power"], "director_intent": "Henoch enforces system rules.", "start_image_keywords": ["hand raised", "red laser", "wireframe figures"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}

### 1. START IMAGE PROMPT (Midjourney/Flux)
Henoch stands with his hand raised, palm forward, emitting a wide, flat red laser scan. In front of him, the glitching humanoid figures are being hit by the laser. Where the laser touches them, they are instantly stripped of their textures, revealing glowing red wireframe skeletons. The background is dark. Cinematic, dynamic action shot.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Henoch, determined expression.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Weathered linen.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Dark void.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Intense red laser light.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Flash frame transition. Tracking shot moving quickly towards the targets. The laser sweeps across, forcing the transition to wireframe.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Heavy bass drop impact. A digital "system lock" sound effect.

## ACT II SCENE 2.6 [Timecode: 00:40-00:45] ISOLATION
**Action:** Die korrupten Bereiche werden dunkel. Das Licht wird ihnen entzogen. Sie verblassen in graues Rauschen.
**Dialog:** -

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "wide", "framing": "wide", "environment": "Void", "env_change": true, "actors": [{"name": "Sinners", "phase": "Wireframe", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "Isolation Shot, Vignette", "mood": ["isolation", "emptiness"], "director_intent": "The consequence of error is deletion.", "start_image_keywords": ["wireframe", "darkness", "fading"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}

### 1. START IMAGE PROMPT (Midjourney/Flux)
A group of faint red wireframe figures standing in an absolute void. The light is being sucked away from the edges of the frame, creating a heavy vignette. The figures are fading into a static-filled gray noise. Minimalist, bleak, high contrast.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Fading wireframe figures.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** N/A
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Empty void.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Diminishing light, fading to black.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Fade to black transition. The vignette closes in rapidly. The figures dissolve into noise.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Sound is abruptly sucked away, creating a vacuum effect. Silence.

## ACT III SCENE 3.1 [Timecode: 00:45-00:52] SYSTEM RESTORE
**Action:** Das Bild hellt auf. Weißes, diffuses Licht. Die "Auserwählten" stehen in einer perfekten Reihe. Keine individuellen Züge, nur leuchtende Silhouetten.
**Dialog:** -

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "mixed", "shot_type": "wide", "framing": "wide", "environment": "White Void", "env_change": true, "actors": [{"name": "The Elect", "phase": "Light", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "14mm God-Eye, Symmetrical", "mood": ["peace", "harmony"], "director_intent": "Reveal the validated output.", "start_image_keywords": ["white light", "silhouettes", "symmetry"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}

### 1. START IMAGE PROMPT (Midjourney/Flux)
A blindingly white, clean space filled with diffuse light. A row of perfect, glowing humanoid silhouettes stands in absolute symmetry. They have no facial features, just pure, radiant white light defining their forms. The aesthetic is ethereal, divine, and geometrically perfect. 14mm wide angle.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Glowing silhouettes.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** N/A
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Infinite white space.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** High-key lighting, pure white and soft gold.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Slow dissolve from black. Perfectly stabilized camera. No movement from the figures.

### 3. AUDIO PROMPT (Hunyuan/Foley)
A pure, synthetic sine wave chord, rising harmonically.

## ACT III SCENE 3.2 [Timecode: 00:52-00:58] INHERITANCE
**Action:** Die Erde unter den Auserwählten regeneriert sich. Gras wächst in Zeitraffer (prozedurale Generierung). Goldene Partikel steigen auf.
**Dialog:** -

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "close_up", "framing": "low_angle", "environment": "Regenerating Earth", "env_change": true, "actors": [], "props": ["Grass", "Golden Particles"], "camera": "Dolly In, Slow Motion", "mood": ["rebirth", "growth"], "director_intent": "Show the system healing itself.", "start_image_keywords": ["grass growing", "golden particles", "timelapse"], "start_image_mode": "env_only", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}

### 1. START IMAGE PROMPT (Midjourney/Flux)
Low angle shot of barren ground. Pristine, vibrant green grass blades are shooting up rapidly, covering the earth. Golden dust particles float in the air, catching the light. The lighting is warm and hopeful. Photorealistic, high detail.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** N/A
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** N/A
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Ground level.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Warm, golden hour lighting.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Smooth pan. Timelapse effect of grass growing, combined with 120fps slow motion for the floating particles.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Soft white noise, resembling a gentle breeze. A "healing" sound effect, like a reverse cymbal swell.

## ACT III SCENE 3.3 [Timecode: 00:58-01:05] CYCLE COMPLETE
**Action:** Henoch steht inmitten der Auserwählten. Er wirkt ruhig. Sein HUD zeigt "CYCLE COMPLETE. PEACE: INFINITE".
**Dialog:** -

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "medium", "framing": "medium", "environment": "White Void", "env_change": false, "actors": [{"name": "Henoch", "phase": "Proxy", "presence": "on_screen", "focus": "primary"}, {"name": "The Elect", "phase": "Light", "presence": "on_screen", "focus": "secondary"}], "props": ["HUD Overlay"], "camera": "Medium Shot, Frontal", "mood": ["serenity", "completion"], "director_intent": "Final state of system stability.", "start_image_keywords": ["Henoch", "peace", "HUD"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 10}

### 1. START IMAGE PROMPT (Midjourney/Flux)
Henoch stands centrally in the white void, flanked by the glowing silhouettes of the Elect. He looks calm and serene. A subtle, thin holographic HUD overlay in front of him reads "CYCLE COMPLETE. PEACE: INFINITE". The composition is perfectly symmetrical. Cinematic lighting.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Henoch, calm expression.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Clean linen.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** White void with glowing figures.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Soft, diffuse white light.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Slow dolly in. The scene is perfectly stable.

### 3. AUDIO PROMPT (Hunyuan/Foley)
The sine wave tone stabilizes into a perfect, continuous frequency.

## ACT III SCENE 3.4 [Timecode: 01:05-01:10] END LOG
**Action:** Schwarzer Screen. Nur der Text-Cursor blinkt: "END OF LOG".
**Dialog:** -

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "ui", "shot_type": "insert", "framing": "close_up", "environment": "Black Screen", "env_change": true, "actors": [], "props": ["Terminal Text"], "camera": "Static", "mood": ["finality"], "director_intent": "System shutdown.", "start_image_keywords": ["terminal", "text", "black screen"], "start_image_mode": "ui_only", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}

### 1. START IMAGE PROMPT (Midjourney/Flux)
A completely black screen. In the center, a retro green terminal font displays the text "END OF LOG". A block cursor blinks next to it. Minimalist, retro-tech aesthetic.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** N/A
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** N/A
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Black screen.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Green text light.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Hard cut. Static shot. Only the cursor blinks rhythmically.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Absolute silence. One final, sharp server click.

## ACTOR MONOLOGUE PLAN (JSON)
MONOLOGUE_JSON: {"actors":{"Henoch":[{"scene":"1.2","text":"Der Code ist rein. Jedes Blatt ein Algorithmus, geschrieben in Licht.","words_max":12},{"scene":"2.3","text":"Der Fehler brennt in meinen Nerven. Dissonanz ist Schmerz.","words_max":10},{"scene":"3.3","text":"Das Rauschen endet. Stille ist das einzige wahre Protokoll.","words_max":10}]},"notes":"German only. Short internal monologues. Do not describe the camera or list what is visible. Use emotion, memory, and cause-effect logic. Keep total lines per chapter low (3-7). JSON must be in one line."}