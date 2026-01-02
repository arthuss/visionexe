import os
import json
import random
import re

# --- CONFIGURATION ---
ROOT_PATH = os.path.abspath(r"C:\Users\sasch\henoch")
INPUT_JSON = os.path.join(ROOT_PATH, "LORA_TRAINING_SET.json")
OUTPUT_QUEUE = os.path.join(ROOT_PATH, "training_queue.json")
TRAINING_ROOT = os.path.join(ROOT_PATH, "training_sets")

# --- PROMPT BUILDING BLOCKS ---
STYLES = [
    "cinematic shot, industrial mysticism style, hyper-realistic, 8k, unreal engine 5 render, volumetrics, depth of field",
    "photorealistic sci-fi, ancient technology aesthetics, atmospheric lighting, detailed texture",
    "biopunk noir, sacred geometry overlays, dark ambient lighting, high contrast"
]

ANGLES = [
    "front view, symmetrical composition",
    "side profile view, 45 degree angle",
    "close up portrait, detailed face",
    "full body shot, standing pose"
]

LAYERS = {
    "A": "sweating skin texture, realistic pores, biological details, human imperfection",
    "B": "faint glowing wireframe overlay on body, geometric grid patterns in background, architectural blueprints",
    "C": "holographic Ge'ez symbols floating, HUD interface elements, digital artifacts, terminal data stream"
}

def clean_filename(name):
    """Sanitizes strings for Windows filenames."""
    # Remove invalid chars: < > : " / \ | ? *
    clean = re.sub(r'[<>:"/\\|?*]', '', name)
    # Replace spaces with underscores
    clean = clean.replace(' ', '_')
    return clean

def generate_prompts_for_actor(actor_name, phase_data):
    prompts = []
    
    base_desc = phase_data.get("description", "")
    keywords = ", ".join(phase_data.get("keywords", []))
    trigger = f"sks_{clean_filename(actor_name).lower()}"
    
    # Generate 20 variations
    for i in range(20):
        style = random.choice(STYLES)
        angle = random.choice(ANGLES)
        
        # Mix Layers randomly to create diversity
        layer_prompt = f"{LAYERS['A']}, {LAYERS['B']}, {LAYERS['C']}"
        
        full_prompt = (
            f"{trigger}, {actor_name}, {base_desc}, {keywords}, "
            f"{angle}, {style}, {layer_prompt}, "
            f"neutral background"
        )
        
        prompts.append({
            "prompt": full_prompt,
            "angle": angle,
            "id": f"{i:02d}"
        })
        
    return prompts

def main():
    print("--- GENERATING LORA PROMPTS ---")
    
    if not os.path.exists(INPUT_JSON):
        print(f"Error: {INPUT_JSON} not found.")
        return

    with open(INPUT_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    job_queue = []
    
    # ACTORS
    for actor_name, actor_data in data.get("actors", {}).items():
        print(f"Processing Actor: {actor_name}")
        
        phases = actor_data.get("phases", [])
        if not phases:
            phases = [{"name": "Default", "chapters": "All", "description": "Standard appearance", "keywords": []}]

        for phase in phases:
            safe_actor_name = clean_filename(actor_name)
            safe_phase_name = clean_filename(phase["name"])
            
            target_folder = os.path.join(TRAINING_ROOT, safe_actor_name, safe_phase_name)
            os.makedirs(target_folder, exist_ok=True)
            
            prompts = generate_prompts_for_actor(actor_name, phase)
            
            for p in prompts:
                job = {
                    "type": "actor",
                    "id": f"{safe_actor_name}_{safe_phase_name}_{p['id']}",
                    "actor": actor_name,
                    "phase": phase["name"],
                    "target_folder": target_folder,
                    "prompt": p["prompt"],
                    "master_filename": f"{safe_actor_name}_{safe_phase_name}_{p['id']}.png",
                    "workflow": "TEXT_TO_IMG_multilora.json" # Default workflow
                }
                job_queue.append(job)

    # ENVIRONMENTS (Placeholder logic until mapping is done)
    # We will add environments later via prepare_env_queue.py

    # Save Queue
    with open(OUTPUT_QUEUE, 'w', encoding='utf-8') as f:
        json.dump(job_queue, f, indent=2)
        
    print(f"\nGenerated {len(job_queue)} training jobs.")
    print(f"Queue saved to: {OUTPUT_QUEUE}")

if __name__ == "__main__":
    main()
