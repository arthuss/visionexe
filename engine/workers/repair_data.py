import os
import json
import re
import subprocess
import shutil

# --- CONFIGURATION ---
ROOT_PATH = os.path.abspath(r"C:\Users\sasch\henoch")
FILMSETS_PATH = os.path.join(ROOT_PATH, "filmsets")
LOG_FILE = os.path.join(ROOT_PATH, "harvest_log.txt")
REPAIRED_DB_FILE = os.path.join(ROOT_PATH, "REPAIRED_DATA.json")
FULL_DB_FILE = os.path.join(ROOT_PATH, "FULL_ACTOR_DB.json")

REPAIR_PROMPT = """
ROLE: Data Repair Specialist.
TASK: The following text contains analysis of the Book of Enoch. It was supposed to contain a JSON block defining 'actors' and 'scenes', but the JSON is missing, malformed, or mixed with code.
INSTRUCTION: Read the text (or code) below. Extract the implicit knowledge about characters (actors) and scenes. Return a VALID JSON object with the following structure:

{
  "actors": [
    { "name": "Name", "role": "Role", "visualTraits": ["trait1", "trait2"], "changes": [] }
  ],
  "scenes": [
    { "title": "Title", "location": "Location", "action": ["action1"], "actorsInvolved": ["Name"] }
  ]
}

- Return ONLY the JSON.
- If the text is just Python/Bash code without story info, try to infer the context from the headers or return an empty structure with a warning in 'role'.
- Ensure the JSON is syntactically correct.

TEXT TO REPAIR:
"""

def resolve_gemini_command():
    gemini_path = shutil.which("gemini") or shutil.which("gemini.cmd")
    if gemini_path:
        return f"\"{gemini_path}\""

    npx_path = shutil.which("npx") or shutil.which("npx.cmd")
    if npx_path:
        return f"\"{npx_path}\" -y @google/gemini-cli"

    return None

def call_ai_agent(prompt, label="AI Repair"):
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
    if not response_text: return None
    cleaned = re.sub(r"```json\s*", "", response_text)
    cleaned = re.sub(r"```", "", cleaned)
    return cleaned.strip()

def extract_json_block(text):
    """Duplicated from harvest script to check validity."""
    pattern_json = r"```json(.*?)```"
    matches = re.findall(pattern_json, text, re.DOTALL)
    if matches: return matches[0].strip()

    pattern_generic = r"```(.*?)```"
    matches = re.findall(pattern_generic, text, re.DOTALL)
    if matches: return matches[0].strip()

    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1:
        return text[start:end+1]
    return None

def get_failed_files():
    """Parses harvest_log.txt and re-scans suspected directories."""
    suspected_dirs = set()
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if "[JSON ERROR]" in line or "[NO JSON]" in line:
                match = re.search(r"\]\s+(.*?)(:|$)", line)
                if match:
                    # e.g. "chapter_007/visual_abc"
                    rel_path = match.group(1).strip()
                    # Normalizing path separators for Windows
                    rel_path = rel_path.replace('/', os.sep)
                    full_dir_path = os.path.join(FILMSETS_PATH, rel_path)
                    suspected_dirs.add(full_dir_path)

    files_to_repair = []
    
    print(f"Scanning {len(suspected_dirs)} suspected directories...")
    
    for directory in suspected_dirs:
        if not os.path.exists(directory):
            continue
            
        # Walk through the directory to find all analysis_llm.txt
        for root, dirs, files in os.walk(directory):
            if "analysis_llm.txt" in files:
                filepath = os.path.join(root, "analysis_llm.txt")
                
                # Double check: Is this file actually broken?
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    json_block = extract_json_block(content)
                    is_broken = False
                    
                    if not json_block:
                        is_broken = True
                    else:
                        try:
                            json.loads(json_block)
                        except json.JSONDecodeError:
                            is_broken = True
                            
                    if is_broken:
                        files_to_repair.append(filepath)
                        
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")

    return sorted(list(set(files_to_repair)))

def main():
    print("--- STARTING REPAIR JOB ---")
    
    files_to_fix = get_failed_files()
    print(f"Identified {len(files_to_fix)} files to repair.")
    
    repaired_data = {} # Key: filepath, Value: Parsed Data
    
    for i, filepath in enumerate(files_to_fix):
        print(f"[{i+1}/{len(files_to_fix)}] Repairing: {filepath}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            prompt = REPAIR_PROMPT + f"\n\n{content[:15000]}" # Limit context
            
            json_str = call_ai_agent(prompt, label=f"Repairing {os.path.basename(os.path.dirname(filepath))}")
            cleaned = clean_json_response(json_str)
            
            if cleaned:
                try:
                    data = json.loads(cleaned)
                    repaired_data[filepath] = data
                    print("  -> Success")
                except json.JSONDecodeError:
                    print("  -> Failed to parse JSON response")
            else:
                print("  -> No response")
                
        except Exception as e:
            print(f"  -> File error: {e}")
            
    # --- SAVE REPAIRED DATA ---
    print(f"Saving {len(repaired_data)} repaired entries to {REPAIRED_DB_FILE}...")
    with open(REPAIRED_DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(repaired_data, f, indent=2)
        
    # --- MERGE INTO MAIN DB ---
    print("Merging into FULL_ACTOR_DB.json...")
    
    with open(FULL_DB_FILE, 'r', encoding='utf-8') as f:
        main_db = json.load(f)
        
    for filepath, data in repaired_data.items():
        # Re-derive context info
        parts = filepath.split(os.sep)
        chapter_id = "unknown"
        subfolder = "unknown"
        for part in parts:
            if part.startswith("chapter_"):
                chapter_id = part
            if part in ["analysis_linguistik", "tech_hypothesen", "visual_abc", "concept_engine", "einleitung", "integration_wave"] or part.startswith("verse_"):
                subfolder = part
                
        # Merge Actors
        if "actors" in data:
            for actor in data["actors"]:
                name = actor.get("name", "Unknown").strip().title()
                if name not in main_db["actors"]:
                    main_db["actors"][name] = []
                
                entry = {
                    "chapter": chapter_id,
                    "source_subfolder": subfolder,
                    "role": actor.get("role", ""),
                    "visualTraits": actor.get("visualTraits", []),
                    "changes": actor.get("changes", []),
                    "status": "repaired"
                }
                main_db["actors"][name].append(entry)

        # Merge Scenes
        if "scenes" in data:
            for scene in data["scenes"]:
                scene_entry = {
                    "chapter": chapter_id,
                    "title": scene.get("title", ""),
                    "location": scene.get("location", ""),
                    "action": scene.get("action", []),
                    "actors_involved": scene.get("actorsInvolved", []),
                    "status": "repaired"
                }
                main_db["scenes"].append(scene_entry)
                
    # Update stats
    main_db["stats"]["repaired_files"] = len(repaired_data)
    
    with open(FULL_DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(main_db, f, indent=2)
        
    print("Repair Complete. FULL_ACTOR_DB.json updated.")

if __name__ == "__main__":
    main()
