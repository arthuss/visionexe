import re
import subprocess
import os
import sys
import argparse
import io
import json

# Force UTF-8 for stdout/stderr to avoid UnicodeEncodeError on Windows consoles
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# --- CONFIGURATION ---
ROOT_PATH = r"C:\Users\sasch\henoch"
ASSET_BIBLE_PATH = os.path.join(ROOT_PATH, "ASSET_BIBLE.md")
GENERATE_SCRIPT = os.path.join(ROOT_PATH, "generate.py")
WORKFLOW = "TEXT_TO_IMG"
DEFAULT_QUEUE_OUT = os.path.join(ROOT_PATH, "ASSET_BIBLE_QUEUE.json")
DEFAULT_OUTPUT_DIR = os.path.join(ROOT_PATH, "produced_assets", "asset_bible")

# Optional style injection for asset prompts
STYLE_PREFIX = "Cinematic shot, photorealistic, Ancient Aliens style, Egypt-Punk aesthetic, Stargate atmosphere, ancient Ethiopian context, 1 Enoch Tech-Exegesis,"
BANNED_PROMPT_TERMS = [
    r"pixelated?",
    r"pixelation",
    r"voxels?",
    r"low[- ]poly",
    r"minecraft",
    r"blocky",
    r"wireframe",
    r"datamosh(?:ing)?",
    r"glitch(?:y)?",
    r"8[- ]?bit",
]
BANNED_PROMPT_PATTERN = re.compile(rf"\\b({'|'.join(BANNED_PROMPT_TERMS)})\\b", re.IGNORECASE)


def slugify(value):
    value = re.sub(r"[^A-Za-z0-9]+", "_", str(value or "")).strip("_").lower()
    return value or "misc"


def category_folder(category):
    label = re.sub(r"[^A-Z0-9]+", "_", str(category or "").upper()).strip("_")
    if "CHARACTER_FX" in label:
        return "characters"
    if "CHARACTER_GROUP" in label:
        return "characters"
    if label == "UI":
        return "ui_concept"
    if label.startswith("UI_CONCEPT"):
        return "ui_concept"
    if label.startswith("UI_ELEMENT"):
        return "ui_element"
    if label.startswith("UI_INTERFACE"):
        return "ui_interface"
    if label.startswith("UI_OVERLAY"):
        return "ui_overlay"
    if label.startswith("UI_HUD"):
        return "ui_hud"
    if label.startswith("UI_FX"):
        return "ui_fx"
    if label.startswith("UI_VFX"):
        return "ui_vfx"
    if label.startswith("CHARACTER") or label.startswith("CHAR"):
        return "characters"
    if label.startswith("PROP"):
        return "props"
    if label.startswith("ENV"):
        return "environments"
    if label in ("VFX", "FX"):
        return "vfx"
    return slugify(category)

def parse_assets(file_path, filter_type=None):
    if not os.path.exists(file_path):
        print(f"Error: Asset Bible not found at {file_path}")
        return []

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find asset headers: ## [CATEGORY] Name (ID: XYZ)
    # Captures category and ID
    asset_pattern = re.compile(r'^##\s+\[(.*?)\]\s+.*?\s+\(ID:\s*(.*?)\)', re.MULTILINE)
    
    assets = []
    
    # Find all matches
    matches = list(asset_pattern.finditer(content))
    
    for i, match in enumerate(matches):
        category = match.group(1).strip() # e.g. "ENVIRONMENT"
        asset_id = match.group(2).strip()
        
        # Filter logic
        if filter_type:
            # Check if filter string is in category (case-insensitive)
            # e.g. filter="ENV" matches "ENVIRONMENT"
            if filter_type.upper() not in category.upper() and filter_type.upper() not in asset_id.upper():
                continue

        start_index = match.start()
        
        # End index is the start of the next match, or end of file
        if i < len(matches) - 1:
            end_index = matches[i+1].start()
        else:
            end_index = len(content)
            
        asset_block = content[start_index:end_index].strip()
        
        # Remove "---" separator if present at the end
        asset_block = re.sub(r'\n---\s*$', '', asset_block).strip()
        
        assets.append({
            'id': asset_id,
            'category': category,
            'prompt': asset_block
        })
        
    return assets


def parse_filter_value(raw):
    if not raw:
        return []
    if isinstance(raw, list):
        values = []
        for entry in raw:
            values.extend([p.strip() for p in entry.split(",") if p.strip()])
        return values
    return [p.strip() for p in str(raw).split(",") if p.strip()]


def matches_filter(asset, filters):
    if not filters:
        return True
    category = (asset.get("category") or "").upper()
    asset_id = (asset.get("id") or "").upper()
    return any(f.upper() in category or f.upper() in asset_id for f in filters)


def sanitize_prompt_text(text):
    if not text:
        return text
    cleaned_lines = []
    for line in text.splitlines():
        cleaned = BANNED_PROMPT_PATTERN.sub("", line)
        cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
        cleaned = re.sub(r",\s*,", ", ", cleaned).strip(" ,;")
        if not re.search(r"[A-Za-z0-9]", cleaned):
            continue
        cleaned_lines.append(cleaned)
    return "\n".join(cleaned_lines)

def main():
    parser = argparse.ArgumentParser(description="Batch Asset Generator")
    parser.add_argument("--filter", "-f", action="append", help="Filter assets by type (e.g., ENV, CHAR, PROP)")
    parser.add_argument(
        "--queue-out",
        nargs="?",
        const=DEFAULT_QUEUE_OUT,
        default=None,
        help="Write ComfyUI queue JSON (optional)",
    )
    parser.add_argument("--queue-only", action="store_true", help="Only write queue JSON (skip direct generation)")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help="Output folder for queue jobs")
    parser.add_argument("--workflow", default=WORKFLOW, help="Workflow name for queue jobs")
    parser.add_argument("--no-sanitize", action="store_true", help="Disable asset prompt sanitization")
    parser.add_argument("--use-default-style", action="store_true", help="Prepend the built-in style prefix")
    parser.add_argument("--style-prefix", default="", help="Custom style prefix to prepend (overrides built-in)")
    parser.add_argument("--repeats", type=int, default=1, help="Repeat each asset job N times (queue only)")
    args = parser.parse_args()

    print(f"Scanning {ASSET_BIBLE_PATH} for assets...")
    filters = parse_filter_value(args.filter)
    if filters:
        print(f"Filtering for: {', '.join(filters)}")

    assets = parse_assets(ASSET_BIBLE_PATH)
    assets = [a for a in assets if matches_filter(a, filters)]
    
    if not assets:
        print("No assets found matching criteria.")
        return

    print(f"Found {len(assets)} assets.")
    queue_out = args.queue_out or ""
    queue = []
    output_dir = args.output_dir
    workflow = args.workflow or WORKFLOW
    style_prefix = ""
    if args.style_prefix:
        style_prefix = args.style_prefix.strip()
    elif args.use_default_style:
        style_prefix = STYLE_PREFIX

    if queue_out:
        for asset in assets:
            prompt_text = asset["prompt"]
            if not args.no_sanitize:
                prompt_text = sanitize_prompt_text(prompt_text)
            full_prompt = f"{style_prefix} {prompt_text}".strip() if style_prefix else prompt_text
            category_dir = os.path.join(output_dir, category_folder(asset.get("category")))
            queue.append({
                "entity_type": "asset",
                "asset_category": asset.get("category"),
                "asset_id": asset["id"],
                "id": asset["id"],
                "prompt": full_prompt,
                "output_dir": category_dir,
                "output_basename": asset["id"],
                "output_filename": asset["id"] + ".png",
                "workflow": workflow,
                "expected_outputs": 1,
                "repeat_count": max(1, int(args.repeats)),
            })

        with open(queue_out, "w", encoding="utf-8") as f:
            json.dump(queue, f, ensure_ascii=False, indent=2)
        print(f"Wrote queue: {queue_out}")

        if args.queue_only:
            return

    print("Starting direct generation queue...")
    
    for i, asset in enumerate(assets, 1):
        print(f"\n[{i}/{len(assets)}] Generating Asset: {asset['id']}")
        
        # Inject style prefix
        prompt_text = asset["prompt"]
        if not args.no_sanitize:
            prompt_text = sanitize_prompt_text(prompt_text)
        full_prompt = f"{style_prefix} {prompt_text}".strip() if style_prefix else prompt_text

        # Call generate.py using the same python interpreter
        cmd = [
            sys.executable, GENERATE_SCRIPT,
            "-w", workflow,
            "-p", full_prompt,
            "-f", asset['id']
        ]
        
        try:
            # Run and wait for completion
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Print output from generate.py
            print(result.stdout)
            
            if result.returncode != 0:
                print(f"[ERROR] Error: {result.stderr}")
                print("Aborting queue due to error.")
                break
            
        except Exception as e:
            print(f"[ERROR] Execution failed: {e}")
            break

if __name__ == "__main__":
    main()
