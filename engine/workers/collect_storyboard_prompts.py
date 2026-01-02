import os
import re

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
FILMSETS_PATH = os.path.join(ROOT_PATH, "filmsets")
OUTPUT_FILE = os.path.join(ROOT_PATH, "STORYBOARD_PROMPTS.md")

def collect_prompts():
    all_prompts = []
    
    # Walk through chapter directories
    chapters = sorted([d for d in os.listdir(FILMSETS_PATH) if d.startswith("chapter_")])
    
    for chapter_dir in chapters:
        chapter_path = os.path.join(FILMSETS_PATH, chapter_dir)
        script_path = os.path.join(chapter_path, "DREHBUCH_HOLLYWOOD.md")
        
        if not os.path.exists(script_path):
            continue
            
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Split by Scene headers to keep context
        # Regex to find scene headers: ## [ACT X] [SCENE Y.Z] ...
        scene_splits = re.split(r'(^##\s+\[ACT\s+\d+\]\s+\[SCENE\s+[\d\.]+\])', content, flags=re.MULTILINE)
        
        current_scene_header = ""
        
        for part in scene_splits:
            if part.strip().startswith("## [ACT"):
                current_scene_header = part.strip()
                continue
            
            if not current_scene_header:
                continue
                
            # Look for Image Prompt in this part
            # Pattern: ### 1. START IMAGE PROMPT (Midjourney/Flux)\n**PROMPT**
            prompt_match = re.search(r'### 1\. START IMAGE PROMPT \(Midjourney/Flux\)\s*\n\*\*(.*?)\*\*', part, re.DOTALL)
            
            if prompt_match:
                prompt_text = prompt_match.group(1).strip()
                
                # Extract Scene ID from header
                # Header format: ## [ACT 1] [SCENE 1.1] [Timecode: ...] [TITLE]
                scene_id_match = re.search(r'\[SCENE\s+([\d\.]+)\]', current_scene_header)
                scene_num = scene_id_match.group(1) if scene_id_match else "UNKNOWN"
                
                # Extract Chapter Number
                chapter_num = chapter_dir.replace("chapter_", "")
                
                # Construct ID: CH001_SC1.1
                full_id = f"CH{chapter_num}_SC{scene_num}"
                
                all_prompts.append({
                    'id': full_id,
                    'header': current_scene_header,
                    'prompt': prompt_text
                })
                
    return all_prompts

def write_prompts(prompts):
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("# STORYBOARD PROMPTS COLLECTION\n\n")
        f.write(f"Total Prompts: {len(prompts)}\n\n")
        
        for p in prompts:
            f.write(f"## [STORYBOARD] {p['header']} (ID: {p['id']})\n")
            f.write(f"{p['prompt']}\n")
            f.write("\n---\n\n")

if __name__ == "__main__":
    print("Collecting prompts from filmsets...")
    prompts = collect_prompts()
    write_prompts(prompts)
    print(f"Collected {len(prompts)} prompts to {OUTPUT_FILE}")
