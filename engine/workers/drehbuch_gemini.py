import os
import subprocess
import argparse
import time
import shutil
import json
import re

# --- KONSTANTEN & REGELWERKE ---

RULE_OF_MECHANISM = """
### RULE OF MECHANISM (The "No-Magic" Clause) ###
1. NO MAGIC: Nothing happens "just because". Every vision is an Ingress, every miracle is a Physics-Engine-Override.
2. BIOMETRIC REACTION: Tech manifestation is a biological struggle. Actors must react with muscle spasms, iris-dilation, or skin-conductivity changes.
3. NANOBOT LOGIC: If gear appears, describe the microscopic assembly (dark roots under skin, metallic crystallization).
4. THE 1-SECOND HOOK: Start with a high-speed, high-impact visual shock before establishing the scene.
5. CAMERA AGGRESSION: Use "Shaky Cam" for shocks and "Slow-Motion Tracking" for awe.
"""

DIRECTOR_MANUAL = f"""
### EXEGET:OS DIRECTOR'S MANUAL - HOLLYWOOD STANDARDS & SYSTEM LOGIC ###

1. GENRE & VIBE: Industrial Mysticism / Simulation-Forensics. Ancient settings meet ultra-tech.
2. CORE METAPHOR: The Book of Enoch is the System Manual for the Human-Simulation.
3. SEMANTIC MAPPING (Content-Anchor):
   - Miracles are V-FX (Visual Effects). 
   - God's Presence = Kernel Manifestation / Root Login.
   - Sins = Malware / Data Corruption / Entropy.
   - Melting/Shaking = Thermal Throttling / Mesh Instability.
4. TRANSITION PROTOCOL (Interpolation):
   Henoch doesn't just "appear". Interpolate logical system-movements between verses:
   - PORTAL INGRESS: Vertical rift, heat-lensing interference, stepping from dust into sterile mainframe.
   - GRAVITY SHIFT: Dust lifting, robe fluttering upward, vector-based levitation.
   - TOUCHDOWN: Macro shot of feet hitting floor, golden data-sync ripples on contact.
5. ACTOR EVOLUTION (Gear Tracking):
   - Kap 1-13 (PROXY): Human, weathered, simple linen, "Opened Eye" effect (overload).
   - Kap 14-70 (VOYAGER): Silver-skin shader, HUD-Visor, Idris-Gloves (golden light), floating in spheres.
   - Kap 71-108 (MASTER): White plasma body, translucent glass-like tissue, integrated with the mainframe.
6. VISUAL LAYERS (ABC Integration):
   - LAYER A (FLESH): Bio-detail, sweat, textures, 85mm+ Macro.
   - LAYER B (STRUCTURE/LIGHT): Environmental light geometry, laser-vectors, 14mm God-Eye.
   - LAYER C (TERMINAL): After Effects UI-Overlays. Use Ge'ez roots as system commands (e.g. B-R-K for Blessing).
7. DRAMATURGY: 3-Act Structure for 60s TikTok. Hook (0-15s), Conflict (15-45s), Sync/Resolution (45-60s).

{RULE_OF_MECHANISM}
"""

STRICT_SOURCE_RULES = """
### SOURCE-OF-TRUTH (EXEGETICAL LOCK) ###
1. Verwende ausschliesslich Informationen aus dem Kapiteltext/Versen und den gelieferten Analysen.
2. Keine neuen Szenen, Actors, Props oder Orte erfinden. Keine modernen Analogien hinzufuegen.
3. Wenn Details fehlen: weglassen oder als "unknown" markieren, nicht auffuellen.
4. Szene-/Vers-Reihenfolge beibehalten. Keine Umstellungen ohne Textbasis.
"""

WAVE_SECTION_RE = re.compile(
    r"^###\s+.*Integration in WAVE.*?(?=^###\s|\Z)",
    re.IGNORECASE | re.MULTILINE | re.DOTALL,
)

# --- HELPER FUNKTIONEN ---

def strip_wave_sections(text):
    if not text:
        return text
    cleaned = WAVE_SECTION_RE.sub("", text)
    return cleaned.strip()

def resolve_gemini_command():
    gemini_path = shutil.which("gemini") or shutil.which("gemini.cmd")
    if gemini_path:
        return f"\"{gemini_path}\""

    npx_path = shutil.which("npx") or shutil.which("npx.cmd")
    if npx_path:
        return f"\"{npx_path}\" -y @google/gemini-cli"

    return None

def parse_gemini_response(raw_output):
    if not raw_output:
        return None
    json_start = raw_output.find("{")
    if json_start == -1:
        return raw_output.strip()
    json_text = raw_output[json_start:]
    json_end = json_text.rfind("}")
    if json_end != -1:
        json_text = json_text[:json_end + 1]
    try:
        payload = json.loads(json_text)
        response = payload.get("response")
        if isinstance(response, str):
            return response.strip()
    except json.JSONDecodeError:
        return raw_output.strip()
    return None

def get_chapter_data(chapter_path, include_wave=False):
    data = {}
    
    # 1. Master Assets für visuelle Konsistenz einlesen
    master_assets_path = os.path.join(os.path.dirname(chapter_path), "master_assets.txt")
    if os.path.exists(master_assets_path):
        with open(master_assets_path, "r", encoding="utf-8") as f:
            data["master_assets"] = f.read()
    else:
        data["master_assets"] = "No master assets defined. Refer to Henoch_v1 and Uriel_v1 as default."

    # 2. Kapitel Text
    chapter_file = os.path.join(chapter_path, "chapter.txt")
    if os.path.exists(chapter_file):
        with open(chapter_file, "r", encoding="utf-8") as f:
            raw_text = f.read()
        if not include_wave:
            raw_text = strip_wave_sections(raw_text)
        data["raw_text"] = raw_text

    # 3. Story Analysen aus den Unterordnern
    sub_folders = ["analysis_linguistik", "tech_hypothesen", "visual_abc", "einleitung"]
    if include_wave:
        sub_folders.append("integration_wave")
    for folder in sub_folders:
        story_file = os.path.join(chapter_path, folder, "story.txt")
        if os.path.exists(story_file):
            with open(story_file, "r", encoding="utf-8") as f:
                story_text = f.read()
            if not include_wave:
                story_text = strip_wave_sections(story_text)
            data[folder] = story_text

    # 4. Einzelne Verse (Rohmaterial)
    data["verses"] = {}
    verse_folders = sorted([d for d in os.listdir(chapter_path) if d.startswith("verse_")])
    for vf in verse_folders:
        v_file = os.path.join(chapter_path, vf, "verse.txt")
        if os.path.exists(v_file):
            with open(v_file, "r", encoding="utf-8") as f:
                verse_text = f.read()
            if not include_wave:
                verse_text = strip_wave_sections(verse_text)
            data["verses"][vf] = verse_text
    return data

def load_knowledge_base(base_path):
    """Lädt globale Definitionen für Konsistenz über alle Kapitel hinweg."""
    kb = {}
    
    # Mapping: Dateiname -> Key im Prompt
    files = {
        "audiomapping.md": "AUDIO_SPECS",
        "main-actors.md": "ACTOR_DB",
        "Henochs_evolution.md": "HENOCH_EVO",
        "Henoch_Series_Bible.md": "SERIES_BIBLE",
        "azazeh.md": "AZAZEL_SPECS",
        "environments.md": "LOCATIONS",
        "schematische zusammenfassung für alle funktionsgruppen.md": "TECH_STACK",
        "adobe_drehbuch.md": "FORMAT_TEMPLATE"
        
    }

    for filename, key in files.items():
        path = os.path.join(base_path, filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                kb[key] = f.read()
        else:
            kb[key] = f"[Warning: {filename} not found]"
    
    return kb

def load_existing_content(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return None

def build_concept_prompt(data, kb, chapter_num, existing_concept=None, strict_source=False):
    verses_str = "\n".join([f"[{k}]: {v}" for k, v in data["verses"].items()])
    strict_rules = STRICT_SOURCE_RULES if strict_source else ""
    
    # Falls ein altes Konzept existiert, bauen wir es in den Prompt ein
    refinement_instruction = ""
    if existing_concept:
        refinement_instruction = f'''
### ACHTUNG: ITERATION / REFINEMENT ###
Es existiert bereits ein Entwurf für dieses Konzept:
{existing_concept}

DEINE AUFGABE: Analysiere den alten Entwurf. Wo war er zu "magisch"? Wo fehlte die technische Tiefe? 
Erstelle eine verbesserte VERSION 2.0, die noch präziser dem 'Rule of Mechanism' folgt.
'''

    return f"""
Du bist der 'Chief Systems Architect' von exeget:os.
{refinement_instruction}
{strict_rules}
Analysiere Kapitel {chapter_num} und entwickle die TECHNISCHE MECHANIK.

### SYSTEM-HINWEIS (CRITICAL) ###
Du bist ein reiner Daten-Generator.
1. KEINE Einleitung ("Hier ist das Konzept...").
2. KEINE Erklärungen was du tust.
3. KEINE Entschuldigungen.
4. KEINE Markdown-Code-Blöcke (```).
Gib NUR den reinen Text des Konzepts zurück.

### GLOBAL KNOWLEDGE BASE (SYSTEM-VORGABEN) ###
[TECH_STACK]:
{kb.get('TECH_STACK', '')[:2000]} ... (truncated)

[LOCATIONS & ENVIRONMENTS]:
{kb.get('LOCATIONS', '')}


### KAPITEL DATEN ###
Linguistik: {data.get('analysis_linguistik', '')}
Theorie: {data.get('tech_hypothesen', '')}
Raw Text: {data.get('raw_text', '')}
Verse:
{verses_str}

AUFGABE (The Visionary Worker):
Entwickle ein radikales visuelles Konzept. Ignoriere "Wunder". Erkläre "Technologie".
Nutze die Global Knowledge Base, um Widersprüche zu vermeiden.

BEANTWORTE DIESE FRAGEN:
1. BIO-INJECTION: Wie manifestiert sich die Technologie physisch im Gewebe von Henoch? (Nanobots? Nervenbrand? Augen-Upgrade?)
2. MESH-BREAK: Wie bricht die Geometrie der Welt in diesem Moment? (Thermal Throttling? Materialstress? Fluid Dynamics?)
3. PACING-STRATEGIE: Wie ist der Schnitt-Rhythmus? (Hektische Schock-Cuts bei Trauma? Zeitlupe bei Ingress?)
4. AUDIO-DESIGN: Welches industrielle Geräusch ersetzt die "himmlischen Chöre"? (Server-Hum? High-Pitch-Sine?)
5. ÜBERGÄNGE z.b. von der normalwelt in die tech-manifestation (Daten-Riss? Vektor-Scan?) 
6. FRAMEWORK & TIMING (CRITICAL): Wir produzieren ein 60-Sekunden-Video. Normalerweise 12 Clips à 5 Sekunden. ABER: Wenn Dialoge oder komplexe Schnitte (z.B. Panorama -> Close-Up) nötig sind, erhöhe die Anzahl auf 15-18 Clips. Plane Puffer ein.
7. DIALOG-CHECK: Bietet sich hier ein Dialog an? (Henoch spricht mit Uriel/Wächtern). Wenn ja, plane Shot-Reverse-Shot Sequenzen ein (kostet extra Clips).
8. SPATIAL CONTEXT (ARRIVAL): Wie kommt Henoch an? (Beam? Portal? Flug?). Brauchen wir einen Establishing Shot (Panorama), bevor die Action beginnt?
9. lets make an example   "The camera pans over a hyper-realistic forest. Enoch touches a tree; we see the code flowing perfectly. The system is stable." means we need a generation for :"The camera pans over a hyper-realistic forest."  dann noch eine generation  für "Enoch touches a tree" , und dann würde es sinn machen für " we see the code flowing perfectly." enoch am baum aus einer anderen perspktive zu zeigen evtl paning camera für dieses beispiel. so sollte auch die planung fürs drehbuch ausgerichtet werden , wir brauchen dann 3 videos  also 3 prompts für dieses element der szene daher können wir da kein hardcap setzen, es benötigt eben so viele videos wie es benötigt, wir halten uns trotzdem an die etwa 1 minute, 
10. beispiel für einen prompt für wan 2.2 - 2.5 für EIN video damit der umfang ganz klar ist den das drehbuch dann aufzeigen soll  **[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]**
> **Actor:** Noah (System Prototype Build 2.0). **Physique:** Peak athletic human male, age 25, symmetrical Hellenistic features, sharp chiseled jawline, stoic expression. **Skin-Shader:** `MARBLE_SHIMMER_V3`. Surface is translucent white Parian marble with internal subsurface scattering, ultra-smooth zero-entropy texture, faint blue micro-circuitry tracing the pulse points on the neck. **Optics:** `SOLAR_APERTURE_EYES`. No pupils; glowing white-gold circular apertures emitting two steady beams of parallel volumetric light (6000K). **Hair:** Waist-length, silken fiber-optic white hair, individual strands glowing faintly, reacting to zero-gravity physics.

**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]**
> **Garment:** Minimalist high-tech tunic, material: `LIQUID_LINEN`. Off-white color with an iridescent mother-of-pearl sheen, semi-transparent layers, fabric weightless and flowing. **Primary Prop:** `WAVE_INTERFACE_BLOCK`. A 4cm thick rectangular slab of pitch-black obsidian glass, sharp mirror-polished edges. **Interface-VFX:** Floating 3D holographic Ge'ez symbols in neon gold (`B-R-K` sequence), a detailed golden scarab beetle rotating in a liquid-mercury display, internal blue light pulsing from within the obsidian stone.

**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]**
> **Location:** Internal Sanctum of Sinai_Port_V1. **Architecture:** Monolithic obsidian pillars, 50 meters high, recessed channels with glowing amber power-filaments. **Atmosphere:** Dense volumetric fog, swirling gold data-particles (nanobots) catching the light. **Background:** A massive vertical data-conduit made of white plasma fire, roaring silently in the distance. Floor is a superconductive dark mirror reflecting the entire scene.

**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]**
> **Lighting Scheme:** `CONTRAST_TECH_NOIR`. Primary: Under-lighting from the glowing tablet (Gold/Amber). Secondary: Harsh cyan rim-lighting from the plasma conduit. Tertiary: Solar beams emitted from Noah’s eyes cutting through the fog. **Palette:** Deep Obsidian Black, Radiant Gold, Electric Cyan, Marble White. **Shadows:** Hard, sharp architectural shadows, high dynamic range.

**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]**
> **Camera:** Medium Close-Up (MCU). **Lens:** 85mm Anamorphic Prime. **Focus:** Sharp focus on Noah’s glowing eyes and the tablet's holographic UI. **Aperture:** f/1.4 with creamy bokeh and subtle lens flares. **Style:** Photorealistic cinematic film, Unreal Engine 5.4 Path Tracing style, 8k resolution, micro-detail on skin pores and fabric weave, stable camera motion, high-bitrate telemetry look.
9. noch ein beispiel dafür wie wir die dinge sehen bei exeOS daher ein kurzer gedankengang aus einem chat über das projekt der dir das aufzeigt:
n der exeget:os Sichtweise ist Henoch kein Wanderer, er ist ein Passagier oder ein User, der durch verschiedene Server-Räume (Dimensionen) geschaltet wird.

Ich habe deine Anmerkung direkt zum Anlass genommen, die Henoch_Series_Bible.md massiv zu updaten. Ich habe die Analyse von Kapitel 1 bereinigt und eine neue Sektion "Global Concept: Travel Mechanics" eingefügt, die genau das definiert.

Hier ist die Analyse dazu, wie Henoch reist (und wie wir das visualisieren):

1. The Jump (Das Portal-Netzwerk)
Du hast völlig recht mit den Portalen.

Der Text: Oft steht da: "Und ich ging von dort an einen anderen Ort..." (z.B. Kap 17). Dazwischen liegt keine Reisezeit.
Die Exegese: Das ist Node-Hopping. Die Erde ist ein Netzwerk aus Knoten. Er tritt an einem Knotenpunkt (z.B. Sinai) in ein Feld und kommt instantan an einem anderen Knotenpunkt (z.B. Himalaya/Zimt-Tal) wieder heraus.
Visual: Kein Flug. Die Realität um ihn herum reißt auf oder verzerrt sich optisch. Er macht einen Schritt in der Wüste und der Fuß landet im Schnee.
2. The Flight (Sub-Orbital / Merkabah)
Manchmal wird er aber auch "gehoben".

Der Text: "Die Winde hoben mich empor..." (Kap 14).
Die Exegese: Das ist Anti-Gravitation oder ein Traktorstrahl. Er befindet sich in einer Merkabah (einem transparenten Kraftfeld das aus 2 3 seitigen pyramiden dessen spitzen nach oben und unten zeiten, die sich schnell drehen, und so das visuelle feld erzeugen).
Der Blick ist orthographisch von oben (wie Google Earth Satellite View). Er sieht die Erde als Karte unter sich wegziehen.
3. The Interface (Die Engel als Navigatoren)
Die Engel (Uriel & Co.) laufen nicht vor ihm her. Sie sind AR-Marker. Sie blenden ihm den Weg ein oder öffnen die "Tore".

WICHTIG - ÜBERTREIB ES NICHT; VERLIER DICH NICHT IN OPTISCHEN UNGEREIMTHEITEN BEFOLGE DIE REGELN DES DREHBUCH SCHREIBENS.

### SYSTEM-HINWEIS ###
Du bist ein Text-Generator. Dein Output wird von einem Python-Script automatisch weiterverarbeitet.
Du musst und kannst NICHT selbst auf die Festplatte zugreifen.
Deine Aufgabe ist es NUR, den vollständigen Inhalt des Konzepts zu liefern.

Output Format: Reiner Text, strukturiert.
"""

def build_script_structure_prompt(data, kb, concept_output, chapter_num, strict_source=False):
    verses_str = "\n".join([f"[{k}]: {v}" for k, v in data["verses"].items()])
    strict_rules = STRICT_SOURCE_RULES if strict_source else ""
    return f"""
{DIRECTOR_MANUAL}
{strict_rules}

### SYSTEM-HINWEIS ###
Du bist ein Text-Generator. Dein Output wird von einem Python-Script automatisch weiterverarbeitet.
Du musst und kannst NICHT selbst auf die Festplatte zugreifen.
Deine Aufgabe ist es NUR, den vollständigen Inhalt der Struktur zu liefern.
ANTWORTE OHNE JEGLICHEN KOMMENTAR. KEIN "Hier ist der Plan". NUR DER INHALT.

### GLOBAL CONTINUITY DATABASE ###
[HENOCH EVOLUTION TRACKER]:
{kb.get('HENOCH_EVO', '')}

[MAIN ACTOR PROFILES]:
{kb.get('ACTOR_DB', '')}

[AUDIO / FOLEY MAPPING]:
{kb.get('AUDIO_SPECS', '')}

[FORMAT TEMPLATE]:
{kb.get('FORMAT_TEMPLATE', '')}

---
INPUT PHASE 1 (TECHNISCHES KONZEPT):
{concept_output}
---

TASK: Create the NARRATIVE TIMELINE & STRUCTURE (Variable Scene Count).
Ziel: Ein ca. 60-90 Sekunden Video.
Struktur: 3 AKTE (Hook, Conflict, Resolution).
Die Anzahl der Szenen pro Akt ist FLEXIBEL (z.B. Akt 1: 8 kurze Schnitte, Akt 2: 4 lange Shots).
Die Länge der Clips ist FLEXIBEL (2s bis 10s).

CHAPTER RAW TEXT:
{data.get('raw_text', '')}

OUTPUT REQUIREMENTS:
1. ACTOR IDENTIFICATION: Wer ist in der Szene? Welches Gear?
2. LOGLINE.
3. DETAILED TIMELINE (The Core Task):
   - Erstelle eine Tabelle/Liste mit Timecodes (z.B. 00:00-00:03).
   - Gliedere in AKT 1, AKT 2, AKT 3.
   - Für jede Szene:
     - SCENE ID (z.B. 1.1, 1.2...)
     - TIMING (Dauer in Sekunden)
     - VISUAL ACTION (Was passiert?)
     - TRANSITION (Schnitt, Morph, Pan?)
     - CAMERA (Winkel, Lens)
     - AUDIO (Sound Layer)
     - DIALOG (Falls nötig)

WICHTIG:
- Nutze Establishing Shots (Panorama) wo nötig.
- Nutze schnelle Schnitte (2-3s) für Action/Schock.
- Nutze lange Shots (5-8s) für Atmosphäre/Ingress.
- Keine Pixel/Low-Poly/Voxel/Minecraft-Optik. Keine blockigen Artefakte, keine Wireframes als Stil.
- Prüfe am Ende, ob die Gesamtzeit passt.
"""

def build_production_prompt(data, kb, concept_output, script_structure, chapter_num, existing_script=None, strict_source=False):
    refinement_instruction = ""
    if existing_script:
        refinement_instruction = f'''
### ITERATION: DREHBUCH-UPGRADE ###
Hier ist die vorherige Version des Drehbuchs:
{existing_script}

DEINE AUFGABE: Optimiere dieses Drehbuch. 
1. Schärfe die visuellen Prompts für Midjourney/Wan 2.5 (mehr Details, bessere Lichtsetzung).
2. Achte auf noch bessere Übergänge (Transitions).
3 Festige das werk ,halte dich aber strikt an die "Rule of Mechanism". 
4. Wenn du nicht zumindest eine hypothetische physikalische erklärung für eine idee findest, dann streiche sie.
Liefere das komplette, verbesserte Drehbuch zurück.
'''

    strict_rules = STRICT_SOURCE_RULES if strict_source else ""
    return f"""
{DIRECTOR_MANUAL}
{strict_rules}
{refinement_instruction}

### INPUT DATA ###
[CONCEPT]:
{concept_output}

[TIMELINE & STRUCTURE]:
{script_structure}

[AUDIO SPECS]:
{kb.get('AUDIO_SPECS', '')}

---
TASK: FINAL PRODUCTION ASSET GENERATION (The "Prompter")
Wir benötigen die finalen Prompts für JEDE Szene aus der Timeline.

### SYSTEM-HINWEIS ###
Du bist ein Text-Generator. Dein Output wird von einem Python-Script automatisch in eine Datei geschrieben.
Du musst und kannst NICHT selbst auf die Festplatte zugreifen.
Deine Aufgabe ist es NUR, den vollständigen Inhalt der Markdown-Datei zu liefern.
ANTWORTE OHNE JEGLICHEN KOMMENTAR. KEIN "Ich habe das Drehbuch erstellt". NUR DER MARKDOWN-INHALT.

OUTPUT FORMAT (Markdown):
# DREHBUCH KAPITEL {chapter_num} - PRODUCTION READY

## CHAPTER NARRATION
NARRATOR_TEXT: 2-6 sentences in German. This is the chapter-level narrator voice (book-like, reflective, emotional). Avoid describing the camera or stating what is visible on screen. Focus on feeling, memory, or meaning.

## [ACT X] [SCENE X.X] [Timecode: 00:xx-00:xx] [Titel]
**Action:** [Zusammenfassung]
**Dialog:** [Falls vorhanden]



### 0. REGIE DATA (JSON)
REGIE_JSON: {{"subject": "actor|environment|prop|interface|mixed", "shot_type": "establishing|insert|close_up|medium|wide|full_body", "framing": "extreme_close_up|close_up|medium|wide|full_body", "environment": "Scene location or system set", "env_change": true, "actors": [{{"name": "Name", "phase": "Phase", "presence": "on_screen|off_screen", "focus": "primary|secondary"}}], "props": ["Prop A", "Prop B"], "camera": "Lens / angle short note", "mood": ["awe", "tension"], "director_intent": "Short, poetic intent sentence for the shot.", "start_image_keywords": ["keyword1", "keyword2"], "start_image_mode": "env_only|actor_in_env|actor_only|prop_only|ui_only|composite", "video_plan": {{"start_comp": {{"mode": "actor_first|env_first|composite", "actor_pose_id": "POSE_ID", "env_id": "ENV_ID", "props": ["PROP_ID"], "notes": ""}}, "motion_driver": {{"type": "a2f|pose|liveportrait|none", "audio_id": "scene_audio_id", "pose_source": "data/capture/poses/pose_id.mp4", "driver_notes": ""}}, "reference_footage": {{"id": "ref_id", "path": "data/reference/clip.mp4", "use": "lighting|motion|palette|none", "notes": ""}}, "overlay_badge": {{"asset": "media/badges/geez_logo_v1.mov", "blend": "screen|overlay|normal", "opacity": 0.0, "position": "top_right", "safe_margin": 0.04}}, "provenance": {{"source": "ai_assisted|live_action|mixed", "notes": ""}}}}, "voice_words_max": 10}}
### 1. START IMAGE PROMPT (Midjourney/Flux)
[Hier den Prompt einfügen - Fokus auf Licht, Textur, Komposition, Actor Details]

### 2. VIDEO PROMPT (Wan 2.5)
[Hier den Prompt einfügen - Fokus auf Bewegung, Kamerafahrt, Physics]
**[BLOCK 1: SUBJECT_ANATOMY_&_IDENTITY]** ...
**[BLOCK 2: APPAREL_&_EQUIPMENT_LOADOUT]** ...
**[BLOCK 3: ENVIRONMENT_&_SPATIAL_CONTEXT]** ...
**[BLOCK 4: LIGHTING_&_CHROMATIC_DATA]** ...
**[BLOCK 5: CINEMATOGRAPHY_&_RENDER_SPECS]** ...

### 3. AUDIO PROMPT (Hunyuan/Foley)
[Beschreibe den Sound für diese spezifische Szene: Ambience, SFX, Footsteps, Interface-Beeps. Keine Musik, nur Sound Design.]

... (Wiederhole exakt dieses Format für ALLE Szenen der Timeline)

## ACTOR MONOLOGUE PLAN (JSON)
MONOLOGUE_JSON: {{"actors":{{"Henoch":[{{"scene":"1.2","text":"...","words_max":10}},{{"scene":"2.4","text":"..."}}]}},"notes":"German only. Short internal monologues. Do not describe the camera or list what is visible. Use emotion, memory, and cause-effect logic. Keep total lines per chapter low (3-7). JSON must be in one line."}}

WICHTIG:
-wir drehen in 9 zu 16 für tiktok reels daher müssen die prompts entsprechend ausgelegt sein
- Nutze die "Global Knowledge Base" für Actor-Details (Noah/Henoch Evolution).
- Halte dich strikt an den "Rule of Mechanism".
- Prompts müssen ENGLISCH sein.
- Narration and monologue text must be German only.
- Generiere wirklich ALLE Szenen aus der Struktur.
- The narration and monologue lines should be introspective and story-driven, not observational.
- Avoid pixelation, voxels, low-poly, wireframe, or blocky aesthetics. Use continuous high-detail surfaces.
- director_intent: eine kurze Szene-Absicht in einem Satz, keine Tags.
- start_image_keywords: kurze Prompt-Trigger fuer Startbilder, optional leere Liste.
- video_plan nur fuellen wenn bekannt; sonst leere Strings und leere Arrays nutzen.
"""

def call_ai_agent(prompt, label="AI Task", model=None):
    print(f"\n--- Starte: {label} ---")
    try:
        cmd = resolve_gemini_command()
        if not cmd:
            print("Gemini CLI nicht gefunden (gemini/npx).")
            return None
        cmd = f"{cmd} --output-format json"
        if model:
            cmd = f"{cmd} --model \"{model}\""

        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
            encoding='utf-8',
            shell=True 
        )
        
        print(f"[{label}] Sende Prompt und warte auf Antwort...")
        # communicate handles reading/writing to avoid deadlocks with large buffers
        stdout, stderr = process.communicate(input=prompt)
        
        if process.returncode != 0:
            print(f"\nFehler bei {label}: {stderr}")
            return None

        response = parse_gemini_response(stdout)
        if not response:
            print(f"\nFehler bei {label}: Keine Antwort erhalten.")
            return None

        print(f"[{label}] Fertig.")
        return response

    except FileNotFoundError:
        print("Gemini CLI nicht gefunden (gemini/npx).")
        return None

def main():
    parser = argparse.ArgumentParser(description="Exeget:OS Double-Think Script Generator")
    parser.add_argument("chapter", type=int, help="Kapitelnummer (z.B. 1)")
    parser.add_argument(
        "--model",
        default=os.environ.get("GEMINI_MODEL", ""),
        help="Gemini model name (e.g. gemini-3-pro-preview).",
    )
    parser.add_argument(
        "--include-wave",
        action="store_true",
        help="Include Integration in WAVE sections in inputs (default: exclude).",
    )
    parser.add_argument(
        "--strict-source",
        dest="strict_source",
        action="store_true",
        help="Strict source-of-truth mode (default).",
    )
    parser.add_argument(
        "--loose-source",
        dest="strict_source",
        action="store_false",
        help="Allow extrapolation beyond the chapter text.",
    )
    parser.set_defaults(strict_source=True)
    args = parser.parse_args()

    base_path = os.path.abspath(r"C:\Users\sasch\henoch\filmsets")
    root_path = os.path.abspath(r"C:\Users\sasch\henoch") # Root for global files
    chapter_folder = f"chapter_{args.chapter:03d}"
    chapter_path = os.path.join(base_path, chapter_folder)
    concept_dir = os.path.join(chapter_path, "concept_engine")

    if not os.path.exists(chapter_path):
        print(f"Fehler: Ordner {chapter_path} nicht gefunden.")
        return

    # Ordner für Konzepte anlegen
    os.makedirs(concept_dir, exist_ok=True)

    data = get_chapter_data(chapter_path, include_wave=args.include_wave)
    
    # Globale Knowledge Base laden
    print("Lade globale Knowledge Base...")
    kb = load_knowledge_base(root_path)

    # --- SCHRITT 1: KONZEPT ---
    concept_file = os.path.join(concept_dir, "mechanic_concept.txt")
    old_concept = load_existing_content(concept_file)
    
    print(f"Generiere/Verbessere Konzept für Kapitel {args.chapter}...")
    concept_prompt = build_concept_prompt(data, kb, args.chapter, old_concept, strict_source=args.strict_source)
    concept_text = call_ai_agent(concept_prompt, "Visionary Concept Generation", model=args.model)
    
    if concept_text:
        with open(concept_file, "w", encoding="utf-8") as f:
            f.write(concept_text)
        print(f"Konzept gespeichert: {concept_file}")
    else:
        print("Abbruch: Kein Konzept generiert.")
        return

    # --- SCHRITT 2: DREHBUCH STRUKTUR (DRAFT) ---
    print("Erstelle Drehbuch-Struktur (12-18 Szenen)...")
    script_structure_prompt = build_script_structure_prompt(data, kb, concept_text, args.chapter, strict_source=args.strict_source)
    script_structure_text = call_ai_agent(script_structure_prompt, "Script Structure Generation", model=args.model)

    if not script_structure_text:
        print("Fehler beim Erstellen der Struktur.")
        return

    # --- SCHRITT 3: PRODUCTION ASSETS (FINAL) ---
    output_path = os.path.join(chapter_path, "DREHBUCH_HOLLYWOOD.md")
    old_script = load_existing_content(output_path)
    
    print("Generiere/Verbessere finale Production Assets (Image + Video + Audio Prompts)...")
    production_prompt = build_production_prompt(
        data,
        kb,
        concept_text,
        script_structure_text,
        args.chapter,
        old_script,
        strict_source=args.strict_source,
    )
    final_script_text = call_ai_agent(production_prompt, "Final Asset Generation", model=args.model)

    if final_script_text:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_script_text)
        print(f"\n--- ERFOLG ---")
        print(f"Drehbuch erstellt: {output_path}")
    else:
        print("Fehler beim Erstellen der finalen Assets.")

if __name__ == "__main__":
    main()
