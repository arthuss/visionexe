# DREHBUCH KAPITEL 95 - PRODUCTION READY

## CHAPTER NARRATION
NARRATOR_TEXT: Wenn der Puffer voll ist, unterscheidet das System nicht mehr zwischen Schuld und Fehlercode. Wir reinigen nicht aus Moral, sondern um die Latenz zu beenden. Was wie Zorn aussieht, ist nur die Rückkehr zur Null.

## [ACT I] [SCENE 01.01] [Timecode: 00:00-00:04] [The Purge]
**Action:** Extreme Close-Up auf Henochs Augen. Die mechanischen Iris-Lamellen öffnen sich ruckartig. Ein Strahl aus zischendem, weißen Stickstoff-Nebel (Vapor) schießt unter Hochdruck horizontal heraus.
**Dialog:** -

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "extreme_close_up", "framing": "extreme_close_up", "environment": "Station_Metatron_Server_Deck", "env_change": true, "actors": [{"name": "Henoch", "phase": "Master", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "100mm Macro", "mood": ["intense", "mechanical"], "director_intent": "Visualize the 'crying' as a mechanical pressure release valve opening.", "start_image_keywords": ["nitrogen purge", "mechanical iris", "white vapor jet"], "start_image_mode": "actor_only", "video_plan": {"start_comp": {"mode": "actor_only", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.0}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Extreme macro close-up of a synthetic eye socket, 9:16 vertical. Henoch Master Phase. The organic eye is replaced by a complex mechanical aperture made of polished obsidian and gold. The shutter blades are wide open. A violent, high-pressure jet of dense white nitrogen gas is blasting out of the socket. The edges of the metal are frosting over instantly. Hyper-realistic texture, cold blue lighting, depth of field focused on the nozzle.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Henoch Master Phase, mechanical eye unit.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Obsidian skin plating.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Dark, blurred server room background.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Sharp, cold blue rim light. Internal orange heat fading to blue.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** 100mm Macro lens. The gas jet erupts with physics-accurate turbulence. Shutter mechanism twitches. 9:16 vertical video.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Sharp, aggressive pneumatic hiss like a bus air-brake release. No crying sounds. Mechanical servo whine.

## [ACT I] [SCENE 01.02] [Timecode: 00:04-00:09] [Condensation]
**Action:** Der Nebel umhüllt Henochs Kopf. Auf seiner schwarzen Panzerung bilden sich fraktale Eisblumen (Kondensation). Rote `TEMP_CRITICAL` LEDs blinken rhytmisch durch den Nebel.
**Dialog:** THERMAL CRITICAL (Overlay Text)

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "close_up", "framing": "close_up", "environment": "Station_Metatron_Server_Deck", "env_change": false, "actors": [{"name": "Henoch", "phase": "Master", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "50mm Portrait", "mood": ["cold", "urgent"], "director_intent": "Show the physical consequence of rapid cooling on the hardware.", "start_image_keywords": ["frost on skin", "red warning lights", "white fog"], "start_image_mode": "actor_only", "video_plan": {"start_comp": {"mode": "actor_only", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.0}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 2}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Portrait close-up, 9:16 vertical. Henoch Master Phase. His obsidian glass skin is covered in growing patterns of white frost and ice crystals. Thick white nitrogen fog swirls around his head. Through the fog, harsh red warning lights pulse, illuminating the ice from within. The aesthetic is industrial cryogenics. High contrast, wet surface details.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Henoch Master Phase.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Frosted glass skin.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Foggy server environment.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Stroboscopic red alarm lights cutting through white fog.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** 50mm Portrait. Frost patterns expand rapidly across the face surface ("crystal growth simulation"). 9:16 vertical video.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Cracking sound of rapid freezing (thermal shock). Muffled rhythmic alarm beeps (120bpm).

## [ACT I] [SCENE 01.03] [Timecode: 00:09-00:15] [The Room]
**Action:** Establishing Shot. Station Metatron. Ein endloser Raum aus schwarzen Server-Monolithen, die sich im schwarzen Glasboden spiegeln. Henoch steht als kleine, isolierte Figur in der Mitte.
**Dialog:** -

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "environment", "shot_type": "wide", "framing": "wide", "environment": "Station_Metatron_Server_Deck", "env_change": false, "actors": [{"name": "Henoch", "phase": "Master", "presence": "on_screen", "focus": "secondary"}], "props": ["server_monoliths"], "camera": "14mm Wide / Dolly Out", "mood": ["oppressive", "infinite"], "director_intent": "Establish the scale of the system and the isolation of the admin.", "start_image_keywords": ["endless server racks", "black glass floor", "lone figure"], "start_image_mode": "env_first", "video_plan": {"start_comp": {"mode": "env_first", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.0}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Ultra-wide establishing shot, 9:16 vertical. Station Metatron Server Deck. A vast, brutalist hall. Rows of towering, sleek black monoliths (server racks) extend to an infinite vanishing point. The floor is perfectly reflective black glass. In the center distance stands Henoch, a small figure shrouded in dissipating white vapor. Symmetry, cold atmosphere, technological sublimity.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Henoch (distant).
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Tech silhouette.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Infinite server hall.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Cold white ambient light, red reflections on the floor.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** 14mm Wide lens. Slow, smooth dolly out to emphasize scale. 9:16 vertical video.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Deep, heavy drone of server fans (60Hz hum). Reverberant, vast space ambience.

## [ACT II] [SCENE 02.04] [Timecode: 00:15-00:20] [Sudo Grant]
**Action:** POV Wechsel (Sicht der Sünder). Durch digitales Rauschen sehen wir Henoch. Er tippt auf ein schwebendes Hologramm. Text: `PERMISSION_UPDATE`. Status-Icons wechseln von ROT zu GRÜN.
**Dialog:** SUDO GRANT PERMISSION

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "interface", "shot_type": "medium", "framing": "medium", "environment": "Station_Metatron_Server_Deck", "env_change": false, "actors": [{"name": "Henoch", "phase": "Master", "presence": "on_screen", "focus": "primary"}], "props": ["holographic_interface"], "camera": "35mm Handheld / POV", "mood": ["glitch", "observational"], "director_intent": "View the admin's action through the corrupted lens of the user.", "start_image_keywords": ["holographic ui", "glitch overlay", "permission granted green"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.0}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 3}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Medium shot, POV perspective with digital noise artifacts, 9:16 vertical. Henoch stands in the server room, manipulating a floating holographic interface. The UI shows lines of code and a large dialogue box: "PERMISSION_UPDATE". He presses "CONFIRM". The red lock icons instantly turn bright green. The image has chromatic aberration and scanlines, simulating a corrupted feed.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Henoch Master Phase.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Silver robes.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Server room (distorted).
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Green interface light reflecting on face.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** 35mm Handheld/Shaky cam. Digital tearing effects. Interface interaction is snappy. 9:16 vertical video.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Mechanical keyboard clacking. Positive "Success" chime (major third). Digital interference buzz.

## [ACT II] [SCENE 02.05] [Timecode: 00:20-00:27] [Validation]
**Action:** Die Gruppe der "Gerechten" (Tsadqan) leuchtet blau auf. Ein hexagonaler digitaler Schild baut sich um sie auf. Sie richten sich auf, ihre Textur-Auflösung wird schärfer (4K Upgrade).
**Dialog:** -

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "medium", "framing": "medium", "environment": "Earth_Ground_Level", "env_change": true, "actors": [{"name": "Righteous_Group", "phase": "Voyager", "presence": "on_screen", "focus": "primary"}], "props": ["blue_shield_dome"], "camera": "24mm Dynamic / Whip Pan", "mood": ["protected", "high_tech"], "director_intent": "Visualizing divine favor as a software update and security patch.", "start_image_keywords": ["blue hexagon shield", "high res textures", "glowing aura"], "start_image_mode": "actor_in_env", "video_plan": {"start_comp": {"mode": "actor_in_env", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.0}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Dynamic medium shot, 9:16 vertical. A group of people (Righteous) standing in a grey environment. A translucent, blue hexagonal energy shield is constructing itself around them, interlocking like a puzzle. Inside the shield, the people are rendered in hyper-sharp 8K resolution, glowing slightly. Outside, the world is dull. They look up with clarity and calm.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Righteous group.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Detailed linen textures.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Urban ground level.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Blue shield glow, golden skin tones.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** 24mm Dynamic move. Whip pan around the group as the shield snaps into place. 9:16 vertical video.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Sci-fi shield deployment hum ("Power Up"). Clean, crystal-clear synth pad.

## [ACT II] [SCENE 02.06] [Timecode: 00:27-00:34] [Malware]
**Action:** Die "Sünder" (Hatin) bewegen sich ruckartig. Ihre Münder bewegen sich, aber man hört nur Static. Sie werfen schwarze, teerartige Masse (Code-Fragmente) Richtung Henoch.
**Dialog:** -

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "medium", "framing": "medium", "environment": "Earth_Ground_Level", "env_change": false, "actors": [{"name": "Sinner_Group", "phase": "Corrupted", "presence": "on_screen", "focus": "primary"}], "props": ["black_ooze_projectiles"], "camera": "85mm Shaky / Jumpy Cut", "mood": ["chaotic", "hostile"], "director_intent": "Depict sin as a virus attempting to attack the system core.", "start_image_keywords": ["glitch humans", "black ooze", "silent scream"], "start_image_mode": "actor_in_env", "video_plan": {"start_comp": {"mode": "actor_in_env", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.0}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Medium action shot, 9:16 vertical. A chaotic group of "Sinner" figures. Their forms are unstable, twitching with motion blur. They are throwing aggressive projectiles made of viscous black liquid that looks like melting digital code. Their mouths are wide open in screams, but their faces are pixelated. The background is unstable and glitching.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Glitchy humanoids.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Street clothes with tearing textures.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Corrupted urban space.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Harsh, flickering lighting.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** 85mm Shaky camera. Jumpy cuts. The black liquid flies towards the lens. 9:16 vertical video.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Loud static noise. Modem screeching. Wet splashing sounds. No human voices.

## [ACT II] [SCENE 02.07] [Timecode: 00:34-00:39] [Latency]
**Action:** Die schwarze Masse friert mitten in der Luft ein. Time-Stop Effekt. Die Sünder bewegen sich in extremer Zeitlupe (Lag/Stuttering), während Henoch sich im Hintergrund normal bewegt.
**Dialog:** NETWORK LAG DETECTED

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "mixed", "shot_type": "wide", "framing": "wide", "environment": "Earth_Ground_Level", "env_change": false, "actors": [{"name": "Sinner_Group", "phase": "Corrupted", "presence": "on_screen", "focus": "primary"}, {"name": "Henoch", "phase": "Master", "presence": "on_screen", "focus": "secondary"}], "props": ["frozen_projectiles"], "camera": "Bullet Time / Freeze Frame", "mood": ["suspended", "surreal"], "director_intent": "Show the power imbalance via control over time and physics.", "start_image_keywords": ["frozen liquid", "bullet time", "suspended animation"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.0}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 3}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Wide freeze-frame shot, 9:16 vertical. The black liquid projectiles are frozen in mid-air, sculpted in intricate splash shapes. The Sinner figures are caught in awkward poses, blurred slightly as if vibrating. In the background, Henoch stands perfectly sharp and composed, observing the frozen chaos. Matrix-style bullet time aesthetic.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Frozen sinners, active Henoch.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Mixed.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Frozen battlefield.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** High contrast.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Bullet Time camera rotation around the frozen action. The liquid hangs in the air. 9:16 vertical video.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Sound effect of time slowing down (pitch drop). A low, pulsating LFO "wub-wub-wub".

## [ACT III] [SCENE 03.08] [Timecode: 00:39-00:45] [Reflection]
**Action:** Die Masse kehrt ihre Vektoren um. Sie fliegt mit doppelter Geschwindigkeit zurück und trifft die Sünder. Der Impact erzeugt digitale Schockwellen (Distortion Rings).
**Dialog:** RETURN TO SENDER

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "mixed", "shot_type": "medium", "framing": "medium", "environment": "Earth_Ground_Level", "env_change": false, "actors": [{"name": "Sinner_Group", "phase": "Corrupted", "presence": "on_screen", "focus": "primary"}], "props": ["shockwaves", "returning_projectiles"], "camera": "Action Cam / Fast Cut", "mood": ["impact", "retribution"], "director_intent": "The system reflects the malicious code back to the source.", "start_image_keywords": ["shockwave impact", "black liquid splash", "reversal"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.0}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 3}
### 1. START IMAGE PROMPT (Midjourney/Flux)
High-velocity action shot, 9:16 vertical. The black liquid projectiles are smashing back into the Sinner figures. Upon impact, the liquid doesn't splash normally but creates transparent, rippling digital distortion rings in the air. The figures are knocked back by the force. Debris and code fragments fly everywhere.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Impacted figures.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Tearing clothes.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Combat zone.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Flash of impact light.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** Action Cam. Fast playback. Projectiles reverse direction violently. Impact creates lens distortion. 9:16 vertical video.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Reverse suction sound followed by a loud, digital "CRACK" or "THUD". Glass breaking.

## [ACT III] [SCENE 03.09] [Timecode: 00:45-00:50] [Delete]
**Action:** Henoch macht eine beiläufige Wischgeste (`DEL *.*`). Ein Sünder beginnt sich aufzulösen: Erst verschwindet die Textur (Greybox), dann das Wireframe.
**Dialog:** DELETE *.*

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "medium", "framing": "medium", "environment": "Station_Metatron_Server_Deck", "env_change": true, "actors": [{"name": "Henoch", "phase": "Master", "presence": "on_screen", "focus": "primary"}, {"name": "Sinner_Target", "phase": "Corrupted", "presence": "on_screen", "focus": "secondary"}], "props": [], "camera": "50mm Stable / Datamosh", "mood": ["clinical", "erasure"], "director_intent": "Visualizing execution as a simple file deletion command.", "start_image_keywords": ["hand swipe gesture", "greybox figure", "texture loss"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.0}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 2}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Split composition, 9:16 vertical. Foreground: Henoch's hand performing a calm swipe gesture. Background: A Sinner figure is being erased. Half of their body is realistic, the other half is a flat grey untextured mesh (Greybox). The wireframe grid is visible at the transition line. The figure looks unaware, simply fading out of existence.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Henoch hand, Sinner body.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Tech glove.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Abstract data space.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Flat technical lighting.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** 50mm Stable. Datamosh transition. The texture peels off the victim like skin, revealing the grey mesh underneath. 9:16 vertical video.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Dry, clicky UI sound (Mouse click). Electronic zap/fizzle.

## [ACT III] [SCENE 03.10] [Timecode: 00:50-00:56] [Collapse]
**Action:** Geometry Failure. Die verbleibenden Sünder implodieren in einzelne Vektoren (Vertex Collapse). Ihre Formen zerreissen physikalisch und werden in einen Punkt gesaugt.
**Dialog:** -

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "wide", "framing": "wide", "environment": "The_Void", "env_change": true, "actors": [{"name": "Sinner_Group", "phase": "Corrupted", "presence": "on_screen", "focus": "primary"}], "props": ["vertex_collapse_fx"], "camera": "35mm Low / Slow Motion", "mood": ["destruction", "abstract"], "director_intent": "The final stage of deletion: geometry collapse.", "start_image_keywords": ["vertex collapse", "spaghetti glitch", "implosion"], "start_image_mode": "composite", "video_plan": {"start_comp": {"mode": "composite", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.0}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 0}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Wide abstract shot, 9:16 vertical. Multiple humanoid figures in a black void are undergoing violent geometry collapse. Their limbs are stretching infinitely thin (spaghetti glitch) towards a central singularity point. The mesh is tearing apart into triangles. It is a scene of digital destruction, not biological gore. Stark black and white.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Collapsing meshes.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** None.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** Black void.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** Silhouette lighting.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** 35mm Low angle. Slow motion. The figures are sucked into nothingness with violent velocity. 9:16 vertical video.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Deep sub-bass drop (Sub-sonic). Crunching digital noise.

## [ACT III] [SCENE 03.11] [Timecode: 00:56-01:00] [Cleanup]
**Action:** Der Raum ist leer und steril. Das Licht wechselt auf kaltes Weiß. Henoch steht regungslos, der Nebel ist verschwunden.
**Dialog:** SYSTEM STABLE

### 0. REGIE DATA (JSON)
REGIE_JSON: {"subject": "actor", "shot_type": "wide", "framing": "wide", "environment": "Station_Metatron_Server_Deck", "env_change": true, "actors": [{"name": "Henoch", "phase": "Master", "presence": "on_screen", "focus": "primary"}], "props": [], "camera": "24mm Wide / Fade to Black", "mood": ["peace", "order"], "director_intent": "Return to the initial state of perfection.", "start_image_keywords": ["white light", "clean room", "standing still"], "start_image_mode": "actor_only", "video_plan": {"start_comp": {"mode": "actor_only", "actor_pose_id": "", "env_id": "", "props": [], "notes": ""}, "motion_driver": {"type": "none", "audio_id": "", "pose_source": "", "driver_notes": ""}, "reference_footage": {"id": "", "path": "", "use": "none", "notes": ""}, "overlay_badge": {"asset": "", "blend": "normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.0}, "provenance": {"source": "ai_assisted", "notes": ""}}, "voice_words_max": 2}
### 1. START IMAGE PROMPT (Midjourney/Flux)
Wide shot, 9:16 vertical. Station Metatron. The room is pristine. No debris, no fog, no red lights. Everything is bathed in a soft, clinical white light. Henoch stands perfectly still in the center, hands at his sides, looking forward. The reflection on the floor is flawless. Order is restored.

### 2. VIDEO PROMPT (Wan 2.5)
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** Henoch Master Phase.
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** Clean tech robes.
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** White station.
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** High-key white lighting.
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** 24mm Wide. Static shot. Hold for 3 seconds. Fade to black. 9:16 vertical video.

### 3. AUDIO PROMPT (Hunyuan/Foley)
Silence. Faint, rhythmic ventilation hum (calm).

## ACTOR MONOLOGUE PLAN (JSON)
MONOLOGUE_JSON: {"actors":{"Henoch":[{"scene":"01.02","text":"Überhitzung im Kernsegment. Notfall-Ventile öffnen.","words_max":6},{"scene":"02.04","text":"Root-Zugriff bestätigt. Überschreibe Protokolle.","words_max":6},{"scene":"03.11","text":"System bereinigt. Leerlauf wiederhergestellt.","words_max":5}]},"notes":"German only. Short internal monologues. Do not describe the camera or list what is visible. Use emotion, memory, and cause-effect logic. Keep total lines per chapter low (3-7). JSON must be in one line."}