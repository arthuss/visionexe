import re
import subprocess
import time
import os

PROMPTS_FILE = r"C:\Users\sasch\henoch\STORYBOARD_PROMPTS.md"
GENERATE_SCRIPT = r"C:\Users\sasch\henoch\generate.py"
WORKFLOW = "flux_schnell"

def parse_prompts(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by separator
    blocks = content.split('---')
    
    prompts = []
    
    for block in blocks:
        if not block.strip():
            continue
            
        # Extract ID
        id_match = re.search(r'\(ID: (.*?)\)', block)
        if not id_match:
            continue
        
        scene_id = id_match.group(1)
        
        # Extract Prompt
        # Assuming prompt starts after the header line
        lines = block.strip().split('\n')
        prompt_lines = []
        header_found = False
        
        for line in lines:
            if line.startswith('## [STORYBOARD]'):
                header_found = True
                continue
            if header_found and line.strip():
                prompt_lines.append(line.strip())
        
        full_prompt = " ".join(prompt_lines)
        
        if scene_id and full_prompt:
            prompts.append({
                "id": scene_id,
                "prompt": full_prompt
            })
            
    return prompts

def main():
    if not os.path.exists(PROMPTS_FILE):
        print(f"Error: {PROMPTS_FILE} not found. Run collect_storyboard_prompts.py first.")
        return

    prompts = parse_prompts(PROMPTS_FILE)
    print(f"Found {len(prompts)} prompts to process.")
    
    for i, item in enumerate(prompts):
        scene_id = item['id']
        prompt = item['prompt']
        
        print(f"[{i+1}/{len(prompts)}] Queueing {scene_id}...")
        
        cmd = [
            "python", 
            GENERATE_SCRIPT, 
            "--workflow", WORKFLOW,
            "--prompt", prompt,
            "--filename", scene_id
        ]
        
        try:
            subprocess.run(cmd, check=True)
            time.sleep(0.5) # Brief pause to be nice to the API
        except subprocess.CalledProcessError as e:
            print(f"Error processing {scene_id}: {e}")

if __name__ == "__main__":
    main()
