import os
import argparse
import subprocess
import json
import re
import shutil

# --- CONFIGURATION ---
ROOT_PATH = os.path.abspath(r"C:\Users\sasch\henoch")
FILMSETS_PATH = os.path.join(ROOT_PATH, "filmsets")
EVOLUTION_DB_FILE = os.path.join(ROOT_PATH, "ACTOR_EVOLUTION_DB.json")
LOCATIONS_DB_FILE = os.path.join(ROOT_PATH, "LOCATION_DB.json")
LORA_MAPPING_FILE = os.path.join(ROOT_PATH, "LORA_MAPPING.json")

# --- PROMPT FOR GEMINI ---
ANALYSIS_PROMPT = """
ROLE: Data Archivist for Film Production.
TASK: Analyze the provided text chunk (from an 'analysis_llm.txt') and extract structured data about CHARACTERS and LOCATIONS.

INPUT CONTEXT:
This text comes from a chapter analysis of the 'Book of Enoch' (Sci-Fi Interpretation).
We need to track how characters look and where they are in this specific chapter.

OUTPUT FORMAT (JSON ONLY):
{
  "chapter_id": "integer (e.g. 19)",
  "actors": [
    {
      "name": "Name of Actor (e.g. Enoch, Uriel, Semyaza)",
      "visual_state": "Description of appearance in this specific chapter (e.g. 'Human in linen', 'Cyborg with glowing eyes')",
      "gear": ["List", "of", "items"],
      "action_context": "Briefly what they do here"
    }
  ],
  "locations": [
    {
      "name": "Name of Location (e.g. Mount Hermon, Deck Gamma)",
      "visual_features": ["List", "of", "visual", "elements"],
      "atmosphere": "Mood/Lighting keywords"
    }
  ]
}

INSTRUCTIONS:
- Return ONLY valid JSON. No markdown formatting.
- If no actors/locations are mentioned, return empty lists.
- Normalize names (e.g. "Henoch" -> "Enoch").

TEXT TO ANALYZE:
"""

def resolve_gemini_command():
    gemini_path = shutil.which("gemini") or shutil.which("gemini.cmd")
    if gemini_path:
        return f"\"{gemini_path}\""

    npx_path = shutil.which("npx") or shutil.which("npx.cmd")
    if npx_path:
        return f"\"{npx_path}\" -y @google/gemini-cli"

    return None

def call_ai_agent(prompt, label="AI Extraction"):
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
        
        stdout, stderr = process.communicate(input=prompt)
        
        if process.returncode != 0:
            print(f"Error in {label}: {stderr}")
            return None
            
        return stdout.strip()

    except Exception as e:
        print(f"Exception in {label}: {e}")
        return None

def clean_json_response(response_text):
    """Clean markdown code blocks from response."""
    if not response_text:
        return None
    # Remove ```json and ```
    cleaned = re.sub(r"```json\s*", "", response_text)
    cleaned = re.sub(r"```", "", cleaned)
    return cleaned.strip()

def extract_chapter_number(filepath):
    """Extracts '19' from '.../chapter_019/...'"""
    match = re.search(r"chapter_(\d+)", filepath)
    if match:
        return int(match.group(1))
    return 0

def collect_files():
    """Finds all analysis_llm.txt files."""
    files = []
    for root, dirs, filenames in os.walk(FILMSETS_PATH):
        for filename in filenames:
            if filename == "analysis_llm.txt":
                files.append(os.path.join(root, filename))
    return sorted(files)

def main():
    print("---" + "STARTING HARVEST: Actor & Location Evolution" + "---")
    
    all_files = collect_files()
    print(f"Found {len(all_files)} analysis files.")
    
    # Structure to hold aggregated data
    # { "Enoch": { "1": {state...}, "19": {state...} } }
    master_actor_db = {}
    master_location_db = {}

    # Limit for testing/safety (remove limit for full run)
    # processing_limit = 10 
    # print(f"Processing first {processing_limit} files for test...")
    
    for i, filepath in enumerate(all_files):
        # if i >= processing_limit: break
        
        chapter_num = extract_chapter_number(filepath)
        print(f"[{i+1}/{len(all_files)}] Processing Chapter {chapter_num}: {os.path.basename(os.path.dirname(filepath))}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Skip empty files
        if len(content) < 50:
            continue
            
        prompt = ANALYSIS_PROMPT + f"\n\nCONTENT (Chapter {chapter_num}):\n{content[:15000]}" # Limit context
        
        json_str = call_ai_agent(prompt, label=f"Analyzing {chapter_num}")
        cleaned_json = clean_json_response(json_str)
        
        if cleaned_json:
            try:
                data = json.loads(cleaned_json)
                
                # Merge Actors
                for actor in data.get("actors", []):
                    name = actor["name"]
                    if name not in master_actor_db:
                        master_actor_db[name] = {}
                    
                    # Store state by chapter
                    master_actor_db[name][chapter_num] = {
                        "visual_state": actor.get("visual_state"),
                        "gear": actor.get("gear"),
                        "action": actor.get("action_context")
                    }

                # Merge Locations
                for loc in data.get("locations", []):
                    loc_name = loc["name"]
                    if loc_name not in master_location_db:
                        master_location_db[loc_name] = []
                    
                    if chapter_num not in master_location_db[loc_name]:
                        master_location_db[loc_name].append(chapter_num)

            except json.JSONDecodeError:
                print(f"Failed to parse JSON for {filepath}")
        
    # --- SAVE OUTPUTS ---
    
    print("Saving Database...")
    
    with open(EVOLUTION_DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(master_actor_db, f, indent=2)
        
    with open(LOCATIONS_DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(master_location_db, f, indent=2)

    # Initialize LoRA Mapping Template if not exists
    if not os.path.exists(LORA_MAPPING_FILE):
        lora_map = {
            "actors": {name: {"lora_file": "TODO.safetensors", "trigger": "trigger_word"} for name in master_actor_db.keys()},
            "locations": {name: {"lora_file": "TODO.safetensors", "trigger": "trigger_word"} for name in master_location_db.keys()}
        }
        with open(LORA_MAPPING_FILE, 'w', encoding='utf-8') as f:
            json.dump(lora_map, f, indent=2)
            
    print(f"Done. Data saved to {EVOLUTION_DB_FILE}")

if __name__ == "__main__":
    main()
