import os
import shutil
import subprocess

# --- CONFIGURATION ---
ROOT_PATH = os.path.abspath(r"C:\Users\sasch\henoch")
CHAPTER_PATH = os.path.join(ROOT_PATH, "filmsets", "chapter_014")
RAW_FILE = os.path.join(CHAPTER_PATH, "14.txt")
ALT_RAW_FILE = os.path.join(ROOT_PATH, "HENOCH-Exeget", "14.txt")
SUBFOLDERS = ["analysis_linguistik", "tech_hypothesen", "visual_abc", "einleitung", "integration_wave", "concept_engine"]

PROMPT_TEMPLATE = """
ROLE: Data Structurer.
TASK: Convert the following text (Analysis of Enoch Chapter 14) into the standard JSON format used in this project.

INPUT TEXT:
<<CONTENT>>

OUTPUT FORMAT:
```json
{{
  "actors": [
    {{ 
      "name": "Name", 
      "role": "Role", 
      "visualTraits": ["trait1", "trait2"], 
      "changes": ["description of evolution"] 
    }}
  ],
  "scenes": [
    {{ 
      "title": "Title", 
      "location": "Location", 
      "action": ["action1", "action2"], 
      "actorsInvolved": ["Name1", "Name2"] 
    }}
  ]
}}
```
Extract 'Henoch' (Enoch), 'The Great Glory' (God/Kernel), 'Cherubim', etc.
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
            print(f"Error: {stderr}")
            return None
        return stdout.strip()
    except Exception as e:
        print(f"Exception: {e}")
        return None

def resolve_raw_file():
    if os.path.exists(RAW_FILE):
        return RAW_FILE
    if os.path.exists(ALT_RAW_FILE):
        return ALT_RAW_FILE
    return None

def write_with_backup(path, content):
    if os.path.exists(path):
        backup_path = path + ".bak"
        if not os.path.exists(backup_path):
            shutil.copy2(path, backup_path)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    raw_path = resolve_raw_file()
    if not raw_path:
        print(f"Error: {RAW_FILE} not found and no fallback at {ALT_RAW_FILE}.")
        return

    print("1. Creating Subfolders...")
    for folder in SUBFOLDERS:
        os.makedirs(os.path.join(CHAPTER_PATH, folder), exist_ok=True)

    print("2. Reading Content...")
    with open(raw_path, 'r', encoding='utf-8') as f:
        content = f.read()

    print("3. Generating JSON Analysis...")
    prompt = PROMPT_TEMPLATE.replace("<<CONTENT>>", content)
    json_output = call_ai_agent(prompt)
    
    if json_output:
        # Clean markdown
        if "```json" in json_output:
            json_output = json_output.split("```json")[1].split("```")[0].strip()
        elif "```" in json_output:
            json_output = json_output.split("```")[1].split("```")[0].strip()
            
        target_file = os.path.join(CHAPTER_PATH, "visual_abc", "analysis_llm.txt")
        write_with_backup(target_file, json_output)
        print(f"Created {target_file}")
    else:
        print("Failed to generate JSON.")

    print("4. Saving Raw File Snapshot...")
    raw_snapshot = os.path.join(CHAPTER_PATH, "14.txt")
    if os.path.abspath(raw_path) != os.path.abspath(raw_snapshot):
        if not os.path.exists(raw_snapshot):
            shutil.copy2(raw_path, raw_snapshot)
            print(f"Copied raw file to {raw_snapshot}")
        else:
            print("Raw snapshot already present, leaving as-is.")
    print("Done.")

if __name__ == "__main__":
    main()
