import os
import subprocess
import argparse
import json
import csv
import shutil

# --- CONFIGURATION ---
ROOT_PATH = r"C:\Users\sasch\henoch"
EXPORT_FILE = os.path.join(ROOT_PATH, "henoch_full_export.csv")
OUTPUT_FILE = os.path.join(ROOT_PATH, "ASSET_BIBLE.md")

# --- PROMPTS ---

ASSET_EXTRACTION_PROMPT = """
ROLE: Technical Asset Director for a High-End Sci-Fi/Fantasy Production.
TASK: Analyze the provided text (Exegesis/Analysis of the Book of Enoch) and extract detailed ASSET DEFINITIONS for Characters, Props, and Environments.

INPUT CONTEXT:
The text contains "Tech-Exegesis" of the Ethiopic Book of Enoch (1 Enoch), an ancient text (approx. 500 BC - 300 AD).
We interpret the books as layers of a Simulation Manual (OS):
1.  **Book of Watchers (1-36):** Hardware-Audit & Infiltration (Sinai Port, Hermon).
2.  **Book of Parables (37-71):** Software-Logic & Master-Controller (Son of Man, Crystal Mainframe).
3.  **Astronomical Book (72-82):** System-Clock & Timing (Sun/Moon logic).
4.  **Dream Visions (83-90):** Historical Heatmapping (Animal Apocalypse).
5.  **Epistle of Enoch (91-105):** Policy Update & User Maintenance.
    *   **Appendix (106-108):** Noah Prototype (Anomaly) & Final Persistence.

We interpret "Angels" as "Admins/Aliens" and "Magic" as "Bio-Injection/Code", BUT the visual style must remain grounded in the ANCIENT SETTING.

VISUAL STYLE GUIDE:
- **Genre:** Ancient Aliens, fantasy, noir, Egypt-tech.
- **Tone:** Realistic, Cinematic, Photorealistic, Serious, Mystical.
- **Avoid:** Generic Sci-Fi, Cartoon, Anime, Lego-look, "Plumb" Sci-Fi.
- **Fusion:** Blend ancient Ethiopian/Egyptian aesthetics with advanced, incomprehensible technology (glowing glyphs, crystalline structures, levitating stone).

OBJECTIVE:
Create a structured "Asset Card" for every entity mentioned. Focus on VISUAL DETAILS suitable for training AI Image Models (LoRAs).

OUTPUT FORMAT (Markdown):

## [CATEGORY] Name of Asset (ID: UNIQUE_ID)
**Description:** Brief summary of role/function.
**Tags:** #tag1 #tag2 #tag3

### 1. VISUAL ANATOMY / DESIGN
*   **Body/Form:** [Detailed description of physique, skin, material]
*   **Face/Sensors:** [Eyes, mouth, sensors, expressions]
*   **Clothing/Armor:** [Material, color, wear & tear, specific items]
*   **Key Features:** [Distinctive marks, glowing parts, glitches]

### 2. EVOLUTION / VARIANTS
*   **Phase 1 (Origin):** [How they look initially]
*   **Phase 2 (Corrupted/Changed):** [How they look after specific events]

### 3. PROPS & EQUIPMENT
*   **Item 1:** [Name & Description]
*   **Item 2:** [Name & Description]

### 4. AI PROMPT KEYWORDS (For LoRA Training)
`subject_keyword`, `texture_keyword`, `lighting_keyword`, `style_keyword`

---

INSTRUCTIONS:
- **INTEGRATE SCREENPLAY DETAILS:** If a "SCREENPLAY CONTEXT" is provided, use its specific visual descriptions (Set Design, Lighting, Action) to define the assets. The screenplay overrides generic descriptions.
- Extract "The Watchers" (Semyaza, Azazel, etc.) with their specific corruptions.
- Extract "The Nephilim" (Giants) and their glitch effects.
- Extract "Props" like the Obsidian Tablet, Swords, Makeup/Mirrors.
- Extract "Environments" like Mount Hermon, The Abyss.
- IGNORE generic filler. Focus on UNIQUE visual identifiers.
- Use the "Tech-Exegesis" language (e.g., "Bio-Luminescence", "Chrome", "Glitch").

TEXT TO ANALYZE:
{text_chunk}
"""

def resolve_gemini_command():
    gemini_path = shutil.which("gemini") or shutil.which("gemini.cmd")
    if gemini_path:
        return f"\"{gemini_path}\""

    npx_path = shutil.which("npx") or shutil.which("npx.cmd")
    if npx_path:
        return f"\"{npx_path}\" -y @google/gemini-cli"

    return None

def call_ai_agent(prompt, label="AI Task"):
    print(f"\n--- Starte: {label} ---")
    try:
        cmd = resolve_gemini_command()
        if not cmd:
            print("Gemini CLI nicht gefunden (gemini/npx).")
            return None

        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
            encoding='utf-8',
            shell=True 
        )
        
        # Use communicate to handle large input/output without deadlocks
        print(f"[{label}] Sende Prompt ({len(prompt)} Zeichen)...")
        stdout, stderr = process.communicate(input=prompt)
        
        if process.returncode != 0:
            print(f"\nFehler bei {label}: {stderr}")
            return None
            
        print(f"[{label}] Antwort erhalten ({len(stdout)} Zeichen).")
        return stdout.strip()

    except Exception as e:
        print(f"Error calling AI: {e}")
        return None

def load_csv_content(filepath):
    content = []
    if not os.path.exists(filepath):
        print(f"CSV not found: {filepath}")
        return ""
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None) # Skip header
            for row in reader:
                if len(row) >= 2:
                    # Add source path as context
                    content.append(f"--- SOURCE: {row[0]} ---\n{row[1]}\n")
                    
                    # Try to find associated screenplay
                    # Assuming row[0] is like "filmsets/chapter_001/analysis_linguistik/chapter.txt"
                    # We want "filmsets/chapter_001/DREHBUCH_HOLLYWOOD.md"
                    try:
                        path_parts = row[0].split('/')
                        if len(path_parts) >= 2 and path_parts[0] == 'filmsets':
                            chapter_dir = os.path.join(ROOT_PATH, path_parts[0], path_parts[1])
                            drehbuch_path = os.path.join(chapter_dir, "DREHBUCH_HOLLYWOOD.md")
                            
                            if os.path.exists(drehbuch_path):
                                with open(drehbuch_path, 'r', encoding='utf-8') as db_file:
                                    db_content = db_file.read()
                                    content.append(f"\n--- SCREENPLAY CONTEXT ({path_parts[1]}) ---\n{db_content}\n--- END SCREENPLAY ---\n")
                    except Exception as db_err:
                        # Ignore screenplay errors, just continue with main text
                        pass
                        
    except Exception as e:
        print(f"Error reading CSV: {e}")
    
    return "\n".join(content)

def main():
    parser = argparse.ArgumentParser(description="Exeget:OS Asset Architect")
    parser.add_argument("--limit", type=int, default=0, help="Limit characters to analyze (0 = all)")
    args = parser.parse_args()

    print("Lade Analyse-Daten...")
    full_text = load_csv_content(EXPORT_FILE)
    
    if not full_text:
        print("Keine Daten gefunden.")
        return

    if args.limit > 0:
        full_text = full_text[:args.limit]
        print(f"Text auf {args.limit} Zeichen begrenzt.")

    print(f"Analysiere {len(full_text)} Zeichen Text...")

    # Split text into chunks if too large (simple splitting for now)
    # Gemini Pro has a large context window, but let's be safe or process in passes if needed.
    # For now, we'll try sending it all if it fits, or split by chapters if we had that logic.
    # Given the CSV structure, we can just send it. If it's huge, we might need to chunk.
    # Let's try a reasonable chunk size.
    
    CHUNK_SIZE = 15000
    chunks = [full_text[i:i+CHUNK_SIZE] for i in range(0, len(full_text), CHUNK_SIZE)]
    
    all_assets = []

    for i, chunk in enumerate(chunks):
        print(f"Verarbeite Chunk {i+1}/{len(chunks)}...")
        prompt = ASSET_EXTRACTION_PROMPT.format(text_chunk=chunk)
        result = call_ai_agent(prompt, label=f"Asset Extraction Chunk {i+1}")
        if result:
            all_assets.append(result)

    # Combine and Save
    final_output = "# EXEGET:OS ASSET BIBLE (AUTO-GENERATED)\n\n" + "\n\n---\n\n".join(all_assets)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(final_output)
    
    print(f"\nAsset Bible gespeichert: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
