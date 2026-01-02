import os
import json
import re
import subprocess
import shutil
from collections import defaultdict

# --- CONFIGURATION ---
ROOT_PATH = os.path.abspath(r"C:\\Users\\sasch\\henoch")
INPUT_DB = os.path.join(ROOT_PATH, "FULL_ACTOR_DB.json")
ACTOR_DB = os.path.join(ROOT_PATH, "ACTOR_MASTER_DB.json")
SCENE_DB = os.path.join(ROOT_PATH, "SCENE_MASTER_DB.json")
OUTPUT_MD = os.path.join(ROOT_PATH, "LORA_BLUEPRINT.md")
OUTPUT_JSON = os.path.join(ROOT_PATH, "LORA_TRAINING_SET.json")
ENV_REPORT_JSON = os.path.join(ROOT_PATH, "ENVIRONMENT_REPORT.json")
ENV_REPORT_MD = os.path.join(ROOT_PATH, "ENVIRONMENT_REPORT.md")
ENV_TAGS_FILE = os.path.join(ROOT_PATH, "environments.md")
ENV_MATCH_JSON = os.path.join(ROOT_PATH, "ENVIRONMENT_MATCH_REPORT.json")
ENV_MATCH_MD = os.path.join(ROOT_PATH, "ENVIRONMENT_MATCH_REPORT.md")

TOP_N_ACTORS = 49

# Mapping synonym names to a master key
NAME_MAPPING = {
    "Enoch": "Henoch",
    "Noah": "Henoch", # In some contexts, keep distinct? For now separate, but commonly confused.
    "The Watchers": "Watcher_Daemons",
    "Watchers": "Watcher_Daemons",
    "Semyaza": "Semyaza",
    "Azazel": "Azazel",
    "Uriel": "Uriel",
    "The Great Glory": "Lord_of_Spirits",
    "Head Of Days": "Lord_of_Spirits"
}

PHASE_ANALYSIS_PROMPT = """
ROLE: VFX Supervisor / Asset Manager.
TASK: Analyze the raw chronological data for the Entity '{name}'.
OBJECTIVE: Define distinct VISUAL PHASES for LoRA training and extract PROPS.

INPUT DATA (Chronological Traits found in text):
{raw_data}

INSTRUCTIONS:
1. **Identify Phases:** Does the character change appearance? (e.g. Human -> Cyborg -> Light Being). Define 1 to 2 Phases.
   - If they never change, just output "Phase 1: Default".
   - Assign a rough Chapter Range (e.g. Ch 1-14).
   - Summarize the VISUALS for that phase (max 5 keywords).
2. **Extract Props:** List distinct physical items they carry (keep it short).
3. **Keep it compact:** 1 sentence per phase, no long lists.

OUTPUT FORMAT (JSON ONLY):
{{
  "phases": [
    {{ "name": "Phase Name", "chapters": "e.g. 1-14", "description": "Visual summary", "keywords": ["tag1", "tag2"] }}
  ],
  "props": [
    {{ "name": "Prop Name", "description": "Visual description" }}
  ]
}}
"""

def normalize_name(name):
    clean = name.strip().title()
    return NAME_MAPPING.get(clean, clean)

def get_chapter_int(chapter_str):
    try:
        # Extracts 14 from "chapter_014"
        return int(re.search(r"(\d+)", chapter_str).group(1))
    except:
        return 999

def get_source_type(entry):
    source_type = entry.get("source_subfolder") or entry.get("source_type")
    if isinstance(source_type, list):
        return source_type[0] if source_type else None
    if isinstance(source_type, dict):
        return None
    return source_type

def is_wave_content(entry):
    source_type = get_source_type(entry)
    if isinstance(source_type, str) and source_type.lower() == "integration_wave":
        return True
    source_path = entry.get("source_path", "")
    if isinstance(source_path, str) and "integration_wave" in source_path:
        return True
    return False

def resolve_gemini_command():
    gemini_path = shutil.which("gemini") or shutil.which("gemini.cmd")
    if gemini_path:
        return f"\"{gemini_path}\""

    npx_path = shutil.which("npx") or shutil.which("npx.cmd")
    if npx_path:
        return f"\"{npx_path}\" -y @google/gemini-cli"

    return None

def call_ai_agent(prompt, label="AI Analysis"):
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
        print(f"Exception: {e}")
        return None

def clean_json_response(response_text):
    if not response_text: return None
    cleaned = re.sub(r"```json\s*", "", response_text)
    cleaned = re.sub(r"```", "", cleaned)
    return cleaned.strip()

def get_first_present(entry, keys, default=None):
    for key in keys:
        if key in entry and entry[key] is not None:
            return entry[key]
    return default

def coerce_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        return [f"{k}: {v}" for k, v in value.items()]
    return [value]

def normalize_list(items):
    normalized = []
    for item in items:
        if item is None:
            continue
        if isinstance(item, dict):
            for k, v in item.items():
                normalized.append(f"{k}: {v}")
        elif isinstance(item, list):
            for sub in item:
                if sub is None:
                    continue
                normalized.append(str(sub))
        else:
            normalized.append(str(item))
    return normalized

def extract_environment_tags(path):
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    tags = re.findall(r"Environment-Tag:\s*`([^`]+)`", content)
    return sorted({t.strip() for t in tags if t.strip()})

def main():
    print("--- 1. LOADING DATA ---")
    with open(INPUT_DB, 'r', encoding='utf-8') as f:
        db = json.load(f)
    actor_db = None
    if os.path.exists(ACTOR_DB):
        with open(ACTOR_DB, 'r', encoding='utf-8') as f:
            actor_db = json.load(f)
    scenes_db = None
    if os.path.exists(SCENE_DB):
        with open(SCENE_DB, 'r', encoding='utf-8') as f:
            scenes_db = json.load(f)

    # --- 2. AGGREGATION & FILTERING ---
    aggregated_actors = defaultdict(list)
    aggregated_locations = defaultdict(list)
    
    print("--- 2. NORMALIZING & AGGREGATING ---")
    
    # 2a. Actors
    if actor_db:
        actor_source = actor_db.items()
    else:
        actor_source = db.get("actors", {}).items()

    for raw_name, raw_entries in actor_source:
        master_name = normalize_name(raw_name)

        # Explicit blacklist (Wave App only)
        if master_name.replace(" ", "").lower() == "waveapp":
            continue

        entries = []
        if actor_db:
            by_chapter = raw_entries.get("by_chapter", {})
            for chapter_key, chapter_entries in by_chapter.items():
                for entry in chapter_entries:
                    entry_copy = dict(entry)
                    entry_copy.setdefault("chapter", chapter_key)
                    entries.append(entry_copy)
        else:
            entries = raw_entries

        valid_entries = []
        for entry in entries:
            # Filter out Wave-App content based on folder origin
            if is_wave_content(entry):
                continue
            valid_entries.append(entry)

        if valid_entries:
            aggregated_actors[master_name].extend(valid_entries)

    # 2b. Locations (extracted from Scenes)
    raw_scenes = []
    if scenes_db:
        for _, scene_list in scenes_db.items():
            raw_scenes.extend(scene_list)
    else:
        raw_scenes = db.get("scenes", [])

    for scene in raw_scenes:
        if is_wave_content(scene):
            continue
        loc_name = scene.get("location", "").strip()
        if not loc_name or len(loc_name) < 3: continue
            
        aggregated_locations[loc_name].append(scene)

    # Sort entries by chapter
    for name in aggregated_actors:
        aggregated_actors[name].sort(key=lambda x: get_chapter_int(x["chapter"]))

    # Filter Frequency
    sorted_actors = sorted(aggregated_actors.items(), key=lambda x: len(x[1]), reverse=True)
    sorted_locations = sorted(aggregated_locations.items(), key=lambda x: len(x[1]), reverse=True)

    actor_meta = {}
    for name, entries in aggregated_actors.items():
        chapters = sorted({get_chapter_int(e.get("chapter", "")) for e in entries if get_chapter_int(e.get("chapter", "")) != 999})
        source_types = sorted({get_source_type(e) for e in entries if get_source_type(e)})
        source_paths = sorted({e.get("source_path") for e in entries if isinstance(e.get("source_path"), str)})
        actor_meta[name] = {
            "mentions": len(entries),
            "chapters": chapters,
            "source_types": source_types,
            "source_paths": source_paths,
        }

    location_meta = {}
    for name, scenes in aggregated_locations.items():
        chapters = sorted({get_chapter_int(s.get("chapter", "")) for s in scenes if get_chapter_int(s.get("chapter", "")) != 999})
        source_types = sorted({get_source_type(s) for s in scenes if get_source_type(s)})
        source_paths = sorted({s.get("source_path") for s in scenes if isinstance(s.get("source_path"), str)})
        location_meta[name] = {
            "mentions": len(scenes),
            "chapters": chapters,
            "source_types": source_types,
            "source_paths": source_paths,
        }

    top_entities = sorted_actors[:TOP_N_ACTORS]
    top_locations = sorted_locations[:10]
    
    print(f"Top Actors: {[x[0] for x in top_entities[:5]]}")
    print(f"Top Locations: {[x[0] for x in top_locations[:5]]}")

    final_specs = {"actors": {}, "locations": {}}

    print("--- 3. AI ANALYSIS (PHASE DETECTION) ---")
    
    # --- ACTOR ANALYSIS ---
    for name, entries in top_entities:
        print(f"Analyzing Actor: {name} ({len(entries)} records)...")
        context_lines = []
        for e in entries:
            raw_traits = get_first_present(e, ["visualTraits", "visual_traits", "visual_state"])
            raw_changes = get_first_present(e, ["changes", "change", "evolution"])
            v_traits = normalize_list(coerce_list(raw_traits))
            v_changes = normalize_list(coerce_list(raw_changes))

            traits = ", ".join(v_traits)
            changes = ", ".join(v_changes)
            if traits or changes:
                chapter = e.get("chapter", "unknown")
                context_lines.append(f"[{chapter}]: Traits({traits}) | Changes({changes})")
        
        context_str = "\n".join(context_lines[:40])
        prompt = PHASE_ANALYSIS_PROMPT.format(name=name, raw_data=context_str)
        
        json_str = call_ai_agent(prompt, label=name)
        cleaned = clean_json_response(json_str)
        if cleaned:
            try:
                analysis = json.loads(cleaned)
                analysis["_meta"] = actor_meta.get(name, {})
                final_specs["actors"][name] = analysis
            except: pass

    # --- LOCATION ANALYSIS ---
    LOCATION_PROMPT = """
    ROLE: Concept Artist.
    TASK: Analyze the scenes occurring at '{name}'. Define the VISUAL MOOD and KEY ELEMENTS.
    INPUT SCENES:
    {raw_data}

    INSTRUCTIONS:
    - Keep it short and production-ready.
    - Use max 5 visual_features.
    - 1 short sentence for lighting and atmosphere.

    OUTPUT JSON:
    {{
      "visual_features": ["list", "of", "elements"],
      "lighting": "Lighting description",
      "atmosphere": "Atmosphere keywords"
    }}
    """
    
    for name, scenes in top_locations:
        print(f"Analyzing Location: {name} ({len(scenes)} scenes)...")
        context_lines = []
        for s in scenes:
            action = ", ".join(s.get("action", [])) if isinstance(s.get("action"), list) else str(s.get("action"))
            context_lines.append(f"[{s.get('chapter', '?')}]: {action}")
            
        context_str = "\n".join(context_lines[:20])
        prompt = LOCATION_PROMPT.format(name=name, raw_data=context_str)
        
        json_str = call_ai_agent(prompt, label=name)
        cleaned = clean_json_response(json_str)
        if cleaned:
            try:
                analysis = json.loads(cleaned)
                analysis["_meta"] = location_meta.get(name, {})
                final_specs["locations"][name] = analysis
            except: pass

    # --- 4. OUTPUT GENERATION ---
    print("--- 4. SAVING RESULTS ---")
    
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(final_specs, f, indent=2)

    with open(OUTPUT_MD, 'w', encoding='utf-8') as f:
        f.write("# LORA TRAINING BLUEPRINT\n\n")
        
        f.write("## 1. CHARACTERS (ACTORS)\n")
        for name, data in final_specs["actors"].items():
            f.write(f"### {name}\n")
            meta = data.get("_meta", {})
            if meta:
                chapters = meta.get("chapters", [])
                if chapters:
                    f.write(f"- **Chapters:** {min(chapters)}-{max(chapters)} ({len(chapters)} total)\n")
                source_paths = meta.get("source_paths", [])
                if source_paths:
                    sample_sources = ", ".join(source_paths[:3])
                    f.write(f"- **Sources:** {len(source_paths)} (sample: {sample_sources})\n")
            for phase in data.get("phases", []):
                f.write(f"- **{phase['name']}** ({phase.get('chapters')}): {phase['description']}\n")
                f.write(f"  - `{'`, `'.join(phase.get('keywords', []))}`\n")
            props = data.get("props", [])
            if props:
                f.write(f"  - **Props:** {', '.join([p['name'] for p in props])}\n")
            f.write("\n")

        f.write("\n## 2. ENVIRONMENTS (LOCATIONS)\n")
        for name, data in final_specs["locations"].items():
            f.write(f"### {name}\n")
            meta = data.get("_meta", {})
            if meta:
                chapters = meta.get("chapters", [])
                if chapters:
                    f.write(f"- **Chapters:** {min(chapters)}-{max(chapters)} ({len(chapters)} total)\n")
            f.write(f"- **Atmosphere:** {data.get('atmosphere', '')}\n")
            f.write(f"- **Lighting:** {data.get('lighting', '')}\n")
            f.write(f"- **Features:** `{'`, `'.join(data.get('visual_features', []))}`\n\n")

    print(f"Blueprint saved to: {OUTPUT_MD}")
    print(f"JSON Data saved to: {OUTPUT_JSON}")

    # --- 5. ENVIRONMENT REPORT ---
    env_report = {}
    for name, scenes in sorted_locations:
        chapters = [get_chapter_int(s.get("chapter", "")) for s in scenes]
        chapters = [c for c in chapters if c != 999]
        env_report[name] = {
            "mentions": len(scenes),
            "chapter_min": min(chapters) if chapters else None,
            "chapter_max": max(chapters) if chapters else None,
            "sample_sources": list(
                {
                    s.get("source_path", "")
                    for s in scenes
                    if isinstance(s.get("source_path", ""), str)
                }
            )[:5],
        }

    with open(ENV_REPORT_JSON, 'w', encoding='utf-8') as f:
        json.dump(env_report, f, indent=2)

    with open(ENV_REPORT_MD, 'w', encoding='utf-8') as f:
        f.write("# Environment Report\n\n")
        for loc_name, info in sorted(env_report.items(), key=lambda x: x[1]["mentions"], reverse=True):
            f.write(f"## {loc_name}\n")
            f.write(f"- Mentions: {info['mentions']}\n")
            f.write(f"- Chapters: {info['chapter_min']} - {info['chapter_max']}\n")
            if info["sample_sources"]:
                f.write("- Sample Sources:\n")
                for src in info["sample_sources"]:
                    f.write(f"  - {src}\n")
            f.write("\n")

    print(f"Environment report saved to: {ENV_REPORT_MD}")

    # --- 6. ENV TAG CROSS-CHECK ---
    env_tags = extract_environment_tags(ENV_TAGS_FILE)
    if env_tags:
        tag_candidates = {}
        matched_locations = set()
        loc_names = list(env_report.keys())

        for tag in env_tags:
            keywords = [k.lower() for k in re.split(r"[_\\-]", tag) if k]
            candidates = []
            for loc in loc_names:
                loc_lower = loc.lower()
                if any(k in loc_lower for k in keywords):
                    candidates.append(loc)
            if candidates:
                matched_locations.update(candidates)
            tag_candidates[tag] = candidates

        unmatched_tags = [tag for tag, matches in tag_candidates.items() if not matches]
        unmatched_locations = [loc for loc in loc_names if loc not in matched_locations]

        with open(ENV_MATCH_JSON, 'w', encoding='utf-8') as f:
            json.dump(
                {
                    "tags": env_tags,
                    "tag_candidates": tag_candidates,
                    "unmatched_tags": unmatched_tags,
                    "unmatched_locations": unmatched_locations,
                },
                f,
                indent=2,
            )

        with open(ENV_MATCH_MD, 'w', encoding='utf-8') as f:
            f.write("# Environment Tag Cross-Check\n\n")
            f.write("## Tags From environments.md\n")
            for tag in env_tags:
                f.write(f"- {tag}\n")

            f.write("\n## Tag -> Candidate Locations\n")
            for tag, matches in tag_candidates.items():
                match_text = ", ".join(matches) if matches else "NO MATCH"
                f.write(f"- {tag}: {match_text}\n")

            f.write("\n## Unmatched Tags\n")
            for tag in unmatched_tags:
                f.write(f"- {tag}\n")

            f.write("\n## Unmatched Locations\n")
            for loc in unmatched_locations[:50]:
                f.write(f"- {loc}\n")

        print(f"Environment match report saved to: {ENV_MATCH_MD}")

if __name__ == "__main__":
    main()
