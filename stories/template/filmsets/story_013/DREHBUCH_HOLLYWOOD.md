# DREHBUCH KAPITEL 13 - PRODUCTION READY

## CHAPTER NARRATION
NARRATOR_TEXT: Ich stand an den Ufern von Dan und las ihre Bitten in den schwarzen Spiegel des Systems. Doch der Himmel blieb verschlossen, eine Decke aus statischem Rauschen, die keine Gnade durchließ. Was sie Sünde nannten, war für mich nur ein fataler Fehler im Quellcode, der nicht mehr kompiliert werden konnte.

## [ACT 1] [SCENE 1.1] [Timecode: 00:00-00:04] [ESTABLISHING UBELSEYAEL]
**Action:** Establishing Shot der Quarantäne-Zone. Rote World-Borders glühen im Nebel.
**Dialog:** -

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "establishing", "framing": "wide", "environment": "Ubelseyael Quarantine Zone", "env_change": true, "actors": [], "props": [], "camera": "14mm wide angle, static surveillance style", "mood": ["oppressive", "sterile"], "director_intent": "Show the isolation of the quarantine zone with digital boundaries.", "start_image_keywords": ["grey fog", "red grid", "barren landscape"], "start_image_mode": "env_only", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "UBELSEYAEL_01", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Cinematic wide shot of Ubelseyael, a barren grey landscape shrouded in heavy static fog. In the distance, massive invisible walls are revealed by a faint glowing red hexagonal grid pattern (World Borders). The ground is covered in digital ash. Industrial mysticism style, 8k resolution, photorealistic textures, muted color palette with aggressive red highlights. 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** None.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** None.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Ubelseyael Quarantine Zone. Barren, rocky terrain covered in grey dust. The atmosphere is thick with static fog.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Flat, diffuse lighting from a grey void sky. Red emissive light from the hexagonal grid barriers in the background.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Static camera, high angle surveillance style. Subtle atmospheric turbulence in the fog. No camera movement, emphasizing the stillness of a locked system.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Deep, low-frequency drone like a massive server farm humming in the distance. Complete absence of wind or natural sounds. Occasional digital static crackle.

## [ACT 1] [SCENE 1.2] [Timecode: 00:04-00:08] [AZAZEL'S FEAR]
**Action:** Azazel kniet und zittert (Glitch-Effekt).
**Dialog:** -

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "close_up", "framing": "close_up", "environment": "Ubelseyael Quarantine Zone", "env_change": false, "actors": [{"name": "Azazel", "phase": "CORRUPTED_ADMIN", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "85mm lens, low angle", "mood": ["fear", "instability"], "director_intent": "Capture the digital corruption manifesting as physical trembling.", "start_image_keywords": ["obsidian skin", "violet cracks", "glitch"], "start_image_mode": "actor_in_env", "video_plan": {"start_comp": {"mode": "actor_first", "actor_pose_id": "AZAZEL_KNEEL", "env_id": "UBELSEYAEL_01", "props": [], "notes": ""}, "motion_driver": {"type": "pose", "audio_id": "", "pose_source": "data/capture/poses/glitch_shudder.mp4", "driver_notes": "Apply mesh distortion on shake"}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Close-up low angle shot of Azazel, a massive entity with `OBSIDIAN_MATTE` skin that absorbs light. Deep cracks in his skin leak violet light (memory leak). He is looking down in terror. His texture appears to be glitching, shifting between high detail and raw polygon structure. Background is the grey fog of Ubelseyael. 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Azazel, corrupted admin. Massive muscular build, black matte skin.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Tattered remnants of celestial armor, floating geometry shards.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Ubelseyael fog.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Violet rim light from his own internal corruption. Dark ambient lighting.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Low angle looking up at face. The subject shudders violently, not biologically, but like a mesh vibrating out of sync. Digital artifacting around the edges of the silhouette.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Heavy, labored breathing that sounds like a cooling fan struggling. Digital bit-crushing noise synchronized with the body glitches.

## [ACT 1] [SCENE 1.3] [Timecode: 00:08-00:14] [THE PLEA]
**Action:** Die Wächter weichen zurück, Hände lösen sich auf.
**Dialog:** "Write... Petition..."

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "mixed", "shot_type": "medium", "framing": "medium", "environment": "Ubelseyael Quarantine Zone", "env_change": false, "actors": [{"name": "Watchers", "phase": "FALLEN", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "35mm handheld, shaky", "mood": ["desperation", "chaos"], "director_intent": "Show the collective degradation of the group.", "start_image_keywords": ["dissolving hands", "unfinished render", "grey polygons"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "WATCHERS_RECOIL", "env_id": "UBELSEYAEL_01", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "scene_1_3_audio", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 5}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Medium shot of a group of Watchers recoiling in fear. Their forms are unstable, flickering between hyper-realistic human features and raw grey polygon masses. One Watcher reaches out a hand that is dissolving into pixelated dust. The background is the barren rock of Ubelseyael. Cinematic lighting, high contrast. 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Group of Watchers, various stages of corruption.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Rags that look like corrupted textures.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Ubelseyael rocky ground.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Harsh, flat lighting.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Handheld camera movement, aggressive whip pan. The actors' meshes distort and stretch momentarily as they move back.

### 3. AUDIO PROMPT (Hunyuan/Foley)
A cacophony of distorted voices, overlapping frequencies. The sound of digital data corruption. A garbled voice saying "Write... Petition...".

## [ACT 1] [SCENE 1.4] [Timecode: 00:14-00:20] [INTERFACE INPUT]
**Action:** Henoch schreibt auf dem Obsidian-Tablet.
**Dialog:** -

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "prop", "shot_type": "insert", "framing": "extreme_close_up", "environment": "Ubelseyael Quarantine Zone", "env_change": false, "actors": [{"name": "Henoch", "phase": "PROXY", "presence": "on_screen", "focus": "primary"}], "props": ["Obsidian Tablet"], "camera": "100mm macro", "mood": ["focus", "precision"], "director_intent": "Highlight the interface mechanism of the tablet.", "start_image_keywords": ["obsidian tablet", "glowing geez", "fingertip"], "start_image_mode": "prop_only", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "HAND_WRITING", "env_id": "UBELSEYAEL_01", "props": ["TABLET_01"], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Extreme close-up of a fingertip touching a smooth black obsidian surface. Where the skin touches the glass, it melts slightly into the surface. Glowing golden Ge'ez characters are being etched into the black glass, scrolling upwards like terminal code. The sleeve of a `LIQUID_LINEN` garment is visible. 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Henoch's hand. Weathered skin.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Liquid Linen sleeve, shimmering like mercury.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Blurred background.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Golden glow from the text illuminating the finger.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Macro shot. The finger traces a line, and the text burns in with a laser-like effect. The text scrolls automatically.

### 3. AUDIO PROMPT (Hunyuan/Foley)
High-pitched laser etching sounds. A deep haptic thrumming every time a character is completed.

## [ACT 1] [SCENE 1.5] [Timecode: 00:20-00:25] [SHAME]
**Action:** Wächter verhüllen ihre Gesichter.
**Dialog:** -

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "mixed", "shot_type": "medium", "framing": "wide", "environment": "Ubelseyael Quarantine Zone", "env_change": false, "actors": [{"name": "Watchers", "phase": "FALLEN", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "24mm high angle", "mood": ["shame", "isolation"], "director_intent": "Show the subjects shrinking away from the system's gaze.", "start_image_keywords": ["hiding faces", "black sky", "wings covering"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "WATCHERS_HIDE", "env_id": "UBELSEYAEL_01", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
High angle shot looking down on the group of Watchers. They are huddled together, covering their faces with hands and tattered wings. The sky above them is a flat, unrendered black void, indicating missing textures. The lighting is cold and top-down. 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Group of Watchers.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Tattered wings, grey robes.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Ubelseyael.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Cold, artificial spotlight from above.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Slow zoom out. The figures remain static, trembling slightly. The black void of the sky dominates the upper frame.

### 3. AUDIO PROMPT (Hunyuan/Foley)
A low frequency throb like a slow heartbeat. No voices, just the sound of cloth rustling.

## [ACT 2] [SCENE 2.1] [Timecode: 00:25-00:30] [WATERS OF DAN]
**Action:** Establishing Shot der Kühlanlage (Waters of Dan).
**Dialog:** -

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "establishing", "framing": "wide", "environment": "Waters of Dan Cooling Facility", "env_change": true, "actors": [], "props": [], "camera": "Drone shot, tracking", "mood": ["industrial", "cold"], "director_intent": "Reinterpret the river as a cooling system.", "start_image_keywords": ["blue coolant", "black basalt", "industrial channel"], "start_image_mode": "env_only", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "DAN_COOLING_01", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Wide establishing shot of the "Waters of Dan". It is not a natural river, but a massive industrial cooling channel carved into black basalt. Bioluminescent blue coolant liquid flows rapidly through the channel. Cold white steam rises from the surface. The architecture is brutalist and geometric. 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** None.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** None.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Industrial cooling channel. Black stone banks.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Blue glow from the liquid, white highlights from the steam.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Tracking dolly shot moving along the bank. The liquid flows with high velocity and unnatural smoothness. Steam rises in columns.

### 3. AUDIO PROMPT (Hunyuan/Foley)
The loud, consistent roar of massive industrial pumps and rushing liquid. Hissing of steam.

## [ACT 2] [SCENE 2.2] [Timecode: 00:30-00:38] [READING THE CODE]
**Action:** Henoch liest die Petition vor.
**Dialog:** [Henoch reading Ge'ez]

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "medium", "framing": "medium", "environment": "Waters of Dan Cooling Facility", "env_change": false, "actors": [{"name": "Henoch", "phase": "PROXY", "presence": "on_screen", "focus": "primary"}], "props": ["Obsidian Tablet"], "camera": "50mm side profile", "mood": ["ritualistic", "technological"], "director_intent": "Visualize the voice interacting with the environment.", "start_image_keywords": ["Henoch profile", "vapor shapes", "glowing tablet"], "start_image_mode": "actor_in_env", "video_plan": {"start_comp": {"mode": "actor_first", "actor_pose_id": "HENOCH_SIT_READ", "env_id": "DAN_COOLING_01", "props": ["TABLET_01"], "notes": ""}, "motion_driver": {"type": "a2f", "audio_id": "scene_2_2_audio", "pose_source": "", "driver_notes": "Lip sync to Ge'ez reading"}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 10}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Side profile medium shot of Henoch sitting by the cooling stream. He holds the obsidian tablet which is now fully lit with dense text. As he speaks, the cold vapor around him forms temporary geometric shapes (cymatics). He wears the `LIQUID_LINEN` garment. 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Henoch.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Liquid Linen tunic.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Waters of Dan.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Blue ambient light from river, warm gold light from tablet.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Static camera. Focus on the mouth and the steam reacting to the voice. The steam forms sharp, non-random patterns.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Henoch's voice reading in Ge'ez, processed with a metallic reverb. A sub-bass vibration that syncs with the steam shapes.

## [ACT 2] [SCENE 2.3] [Timecode: 00:38-00:44] [SLEEP MODE]
**Action:** Henoch geht in den Upload-Status (T-Pose).
**Dialog:** -

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "close_up", "framing": "close_up", "environment": "Waters of Dan Cooling Facility", "env_change": false, "actors": [{"name": "Henoch", "phase": "PROXY", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "85mm frontal symmetry", "mood": ["trance", "upload"], "director_intent": "Depict the 'sleep' as a system freeze/upload state.", "start_image_keywords": ["white eyes", "T-pose", "light scan"], "start_image_mode": "actor_only", "video_plan": {"start_comp": {"mode": "actor_first", "actor_pose_id": "HENOCH_TPOSE", "env_id": "DAN_COOLING_01", "props": [], "notes": ""}, "motion_driver": {"type": "pose", "audio_id": "", "pose_source": "data/capture/poses/head_tilt_back.mp4", "driver_notes": "Rigid freeze at end"}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Frontal close-up of Henoch. His eyes have rolled back completely, showing only white sclera. His head is tilted back slightly. A flat plane of light (scanner) is passing over his face. He is frozen in a rigid posture. High contrast lighting. 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Henoch.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Liquid Linen.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Dark background.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Bright scanner light moving vertically.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** The actor moves slightly then snaps into a perfectly rigid freeze. The scanner light moves smoothly over the frozen geometry.

### 3. AUDIO PROMPT (Hunyuan/Foley)
A high-pitched digital whine that increases in pitch (modem handshake/uplink sound). Sudden silence at the freeze.

## [ACT 2] [SCENE 2.4] [Timecode: 00:44-00:50] [THE VISION]
**Action:** POV Flug durch Datentunnel, Rejected Symbol.
**Dialog:** -

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "interface", "shot_type": "pov", "framing": "wide", "environment": "Internal Data Stream", "env_change": true, "actors": [], "props": [], "camera": "First person POV, high speed", "mood": ["panic", "alert"], "director_intent": "Abstract representation of the system rejecting the file.", "start_image_keywords": ["red glyphs", "data tunnel", "rejected symbol"], "start_image_mode": "ui_only", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "DATA_TUNNEL_01", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Abstract data visualization. A high-speed tunnel composed of streaming red error logs and warning glyphs. In the center, a massive, glowing red Ge'ez symbol for "REJECTED" pulses violently. Strobe lighting effects. Cyberpunk UI aesthetic. 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** None.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** None.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Digital void.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Aggressive red strobe lighting.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Fast forward camera movement through the tunnel. The glyphs fly past the camera. The central symbol pulses in size.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Repeated synthetic alarm pings ("Access Denied"). Heavy industrial crashing sounds.

## [ACT 3] [SCENE 3.1] [Timecode: 00:50-00:54] [SYSTEM REBOOT]
**Action:** Henoch wacht auf (Reboot).
**Dialog:** -

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "medium", "framing": "medium", "environment": "Waters of Dan Cooling Facility", "env_change": true, "actors": [{"name": "Henoch", "phase": "PROXY", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "Snap zoom, handheld", "mood": ["shock", "awakening"], "director_intent": "The transition from digital to physical.", "start_image_keywords": ["Henoch waking", "wireframe fading", "gasp"], "start_image_mode": "actor_in_env", "video_plan": {"start_comp": {"mode": "actor_first", "actor_pose_id": "HENOCH_WAKE", "env_id": "DAN_COOLING_01", "props": [], "notes": ""}, "motion_driver": {"type": "pose", "audio_id": "", "pose_source": "data/capture/poses/gasp_wake.mp4", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Medium shot of Henoch snapping awake. His body is transitioning from a green wireframe mesh back to solid flesh and cloth. His eyes are wide open, pupils dilating rapidly. The background is the Waters of Dan. 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Henoch.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Liquid Linen.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Waters of Dan.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Normal lighting returning.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Snap zoom into the face as he gasps. The wireframe overlay fades out rapidly.

### 3. AUDIO PROMPT (Hunyuan/Foley)
A "Power-Up" sound effect (rising synth tone). The sound of cooling fans spinning up to max speed.

## [ACT 3] [SCENE 3.2] [Timecode: 00:54-00:59] [RETURN TO QUARANTINE]
**Action:** Henoch steht vor den Wächtern, Tablet leuchtet rot.
**Dialog:** -

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "full_body", "framing": "low_angle", "environment": "Ubelseyael Quarantine Zone", "env_change": true, "actors": [{"name": "Henoch", "phase": "PROXY", "presence": "on_screen", "focus": "primary"}], "props": ["Obsidian Tablet"], "camera": "24mm low angle hero shot", "mood": ["judgment", "cold"], "director_intent": "Henoch returns not as a friend but as an executor.", "start_image_keywords": ["Henoch standing", "red tablet light", "fog"], "start_image_mode": "actor_in_env", "video_plan": {"start_comp": {"mode": "actor_first", "actor_pose_id": "HENOCH_STAND_JUDGE", "env_id": "UBELSEYAEL_01", "props": ["TABLET_RED"], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Low angle hero shot of Henoch standing in the Ubelseyael fog. He looks cold and distant. He holds the obsidian tablet at his side, which is now emitting a harsh, aggressive RED light that casts long sharp shadows. The Watchers are visible as dark shapes in the background. 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Henoch.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Liquid Linen.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Ubelseyael.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Strong red rim light from the tablet.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Static camera. The wind blows the robe. The red light pulses slowly.

### 3. AUDIO PROMPT (Hunyuan/Foley)
A low, threatening thrumming sound. Complete silence from the Watchers.

## [ACT 3] [SCENE 3.3] [Timecode: 00:59-01:05] [THE JUDGMENT]
**Action:** Henoch hebt das Tablet, rotes Licht flutet alles.
**Dialog:** "No Peace."

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "mixed", "shot_type": "wide", "framing": "wide", "environment": "Ubelseyael Quarantine Zone", "env_change": false, "actors": [{"name": "Henoch", "phase": "PROXY", "presence": "on_screen", "focus": "primary"}, {"name": "Watchers", "phase": "FALLEN", "presence": "on_screen", "focus": "secondary"}], "props": ["Obsidian Tablet"], "camera": "Slow push in", "mood": ["finality", "doom"], "director_intent": "The final delivery of the system's verdict.", "start_image_keywords": ["red light flood", "frozen watchers", "judgment"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "HENOCH_RAISE_TABLET", "env_id": "UBELSEYAEL_01", "props": ["TABLET_RED"], "notes": ""}, "motion_driver": {"type": "a2f", "audio_id": "scene_3_3_audio", "pose_source": "", "driver_notes": "Lip sync 'No Peace'"}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 3}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Wide shot. Henoch raises the tablet high. Intense red light floods the entire scene, turning the fog into a crimson haze. The Watchers are frozen in their glitch-states, like statues caught in a crash. Henoch's face is illuminated from below by the red glow. 9:16 aspect ratio.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Henoch and Watchers.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Liquid Linen.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Ubelseyael.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Overwhelming red light.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Slow push in towards Henoch. The red light intensifies until it almost blows out the image. The Watchers do not move.

### 3. AUDIO PROMPT (Hunyuan/Foley)
A final, loud slam sound like a gavel or a heavy door closing. A long echo. Henoch's voice saying "No Peace".

## ACTOR MONOLOGUE PLAN (JSON)
MONOLOGUE_JSON: {"actors":{"Henoch":[{"scene":"1.4","text":"Ich schrieb ihre Worte, doch der Kern verstand nur Nullen und Einsen.","words_max":12},{"scene":"2.4","text":"Zugriff verweigert. Das System kennt keine Gnade für korrupte Dateien.","words_max":10},{"scene":"3.2","text":"Ihr wolltet Frieden, doch ihr habt den Code gebrochen.","words_max":9}]},"notes":"German only. Short internal monologues. Do not describe the camera or list what is visible. Use emotion, memory, and cause-effect logic. Keep total lines per chapter low (3-7). JSON must be in one line."}