import argparse
import json
import re
import time
from pathlib import Path

from visionexe_paths import ensure_dir, load_story_config, resolve_path


QUEUE_TYPE_MAP = {
    "character": "actor",
    "prop": "prop",
    "set_environment": "asset",
}

PLACEHOLDER_IDS = {
    "CHAR_",
    "PROP_",
    "SETENV_",
    "ENV_",
    "GEOENV_",
    "SCENE_",
    "LOC_",
}

SAFE_FOLDER_RE = re.compile(r"[^A-Za-z0-9_.-]+")
TIMELINE_TAG_RE = re.compile(r"[^0-9]")
ASSET_HEADER_RE = re.compile(r"^##\s+\[(.*?)\]\s+.*?\(ID:\s*(.*?)\)", re.MULTILINE)
EVOLUTION_HEADER_RE = re.compile(r"^###\s*2\.\s*EVOLUTION\s*/\s*VARIANTS", re.IGNORECASE)
SECTION_HEADER_RE = re.compile(r"^###\s+")
PHASE_LINE_RE = re.compile(r"^\s*[*-]\s+(.*)$")
PHASE_NUM_RE = re.compile(r"\bphase\s*([0-9]+)\b", re.IGNORECASE)


def load_jsonl(path: Path):
    items = []
    if not path or not path.exists():
        return items
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            items.append(json.loads(line))
    return items


def normalize_timeline_tag(value: str, padding: int) -> str:
    if not value:
        return f"{1:0{padding}d}"
    raw = str(value).strip().lower()
    if raw.startswith("r") and raw[1:].isdigit():
        return f"{int(raw[1:]):0{padding}d}"
    if raw.isdigit():
        return f"{int(raw):0{padding}d}"
    digits = TIMELINE_TAG_RE.sub("", raw)
    if digits:
        return f"{int(digits):0{padding}d}"
    return f"{1:0{padding}d}"


def safe_folder_name(value: str) -> str:
    if not value:
        return "default"
    return SAFE_FOLDER_RE.sub("_", str(value)).strip("_") or "default"


def build_workflow_prefix(workflow_name: str) -> str:
    if not workflow_name:
        return ""
    raw = str(workflow_name).strip()
    base = Path(raw).name
    if base.lower().endswith(".json"):
        base = Path(base).stem
    return safe_folder_name(base)


def is_placeholder_subject(subject_id: str, name: str) -> bool:
    if not subject_id:
        return True
    if subject_id in PLACEHOLDER_IDS:
        return True
    if subject_id.endswith("_"):
        return True
    if name and "?" in name:
        return True
    return False


def resolve_subject_dir(subjects_root_rel: Path, subjects_root_abs: Path, card):
    subject_dir = card.get("subject_dir") if isinstance(card, dict) else None
    if subject_dir:
        rel = Path(str(subject_dir).replace("\\", "/"))
        return rel, subjects_root_abs / rel
    safe_id = safe_folder_name(card.get("id") if isinstance(card, dict) else "") or "unknown"
    rel = subjects_root_rel / safe_id
    return rel, subjects_root_abs / rel


def parse_prompt_block(markdown: str) -> str:
    if not markdown:
        return ""
    lines = markdown.splitlines()
    prompt_lines = []
    in_prompt = False
    for line in lines:
        if line.strip().startswith("### 5. PROMPT BLOCK"):
            in_prompt = True
            continue
        if in_prompt and line.strip().startswith("### "):
            break
        if in_prompt:
            if line.strip() == "---":
                continue
            prompt_lines.append(line.strip())
    return " ".join([line for line in prompt_lines if line]).strip()


def clean_markdown_block(markdown: str) -> str:
    if not markdown:
        return ""
    text = markdown.strip()
    text = re.sub(r"^\s*---\s*\n", "", text)
    text = re.sub(r"\n\s*---\s*$", "", text)
    return text.strip()


def find_section_bounds(lines, header_re):
    start = None
    for idx, line in enumerate(lines):
        if header_re.match(line.strip()):
            start = idx
            break
    if start is None:
        return None
    end = len(lines)
    for idx in range(start + 1, len(lines)):
        if SECTION_HEADER_RE.match(lines[idx].strip()):
            end = idx
            break
    return start, end


def build_phase_prompt_variants(markdown: str):
    cleaned = clean_markdown_block(markdown)
    if not cleaned:
        return []
    lines = cleaned.splitlines()
    bounds = find_section_bounds(lines, EVOLUTION_HEADER_RE)
    if not bounds:
        return [{
            "prompt": cleaned,
            "phase_tag": "",
            "phase_label": "",
        }]
    start, end = bounds
    phase_entries = []
    seen_nums = set()
    for line in lines[start + 1:end]:
        bullet = PHASE_LINE_RE.match(line)
        if not bullet:
            continue
        text = bullet.group(1).strip()
        match = PHASE_NUM_RE.search(text)
        if not match:
            continue
        phase_num = int(match.group(1))
        if phase_num in seen_nums:
            continue
        seen_nums.add(phase_num)
        phase_entries.append({
            "num": phase_num,
        })
    if not phase_entries:
        return [{
            "prompt": cleaned,
            "phase_tag": "",
            "phase_label": "",
        }]
    variants = []
    for entry in phase_entries:
        filtered = []
        for idx, line in enumerate(lines):
            if idx <= start or idx >= end:
                filtered.append(line)
                continue
            bullet = PHASE_LINE_RE.match(line)
            if not bullet:
                filtered.append(line)
                continue
            text = bullet.group(1).strip()
            match = PHASE_NUM_RE.search(text)
            if not match:
                filtered.append(line)
                continue
            if int(match.group(1)) == entry["num"]:
                filtered.append(line)
        phase_tag = f"phase_{entry['num']:02d}"
        variants.append({
            "prompt": "\n".join(filtered).strip(),
            "phase_tag": phase_tag,
            "phase_label": f"Phase {entry['num']}",
        })
    return variants


def parse_asset_bible(path: Path):
    if not path or not path.exists():
        return []
    content = path.read_text(encoding="utf-8")
    matches = list(ASSET_HEADER_RE.finditer(content))
    assets = []
    for idx, match in enumerate(matches):
        category = match.group(1).strip()
        asset_id = match.group(2).strip()
        start_index = match.start()
        end_index = matches[idx + 1].start() if idx + 1 < len(matches) else len(content)
        block = content[start_index:end_index].strip()
        block = re.sub(r"\n---\s*$", "", block).strip()
        assets.append({
            "id": asset_id,
            "type": category.lower(),
            "markdown": block,
        })
    return assets


def build_prompt_entries(card):
    markdown = card.get("markdown") or ""
    variants = build_phase_prompt_variants(markdown)
    if variants:
        return variants
    card_data = card.get("card") if isinstance(card.get("card"), dict) else {}
    prompt_block = card_data.get("prompt_block")
    if prompt_block:
        return [{
            "prompt": prompt_block,
            "phase_tag": "",
            "phase_label": "",
        }]
    phase_prompts = card_data.get("phase_prompts") or []
    if isinstance(phase_prompts, list) and phase_prompts:
        first = phase_prompts[0]
        if isinstance(first, dict) and first.get("prompt_block"):
            return [{
                "prompt": first.get("prompt_block"),
                "phase_tag": "",
                "phase_label": "",
            }]
    fallback = parse_prompt_block(markdown) or card.get("name") or card.get("id") or ""
    if not fallback:
        return []
    return [{
        "prompt": fallback,
        "phase_tag": "",
        "phase_label": "",
    }]


def main():
    parser = argparse.ArgumentParser(description="Build ComfyUI queue from ASSET_BIBLE subject prompts.")
    parser.add_argument("--story-root", help="Story root path (defaults to engine_config default_story_root).")
    parser.add_argument("--story-config", help="Path to story_config.json (overrides story-root).")
    parser.add_argument("--cards", help="asset_bible_cards.jsonl path.")
    parser.add_argument("--asset-bible", help="ASSET_BIBLE.md path (fallback if cards missing).")
    parser.add_argument("--output-queue", help="Output queue JSON path.")
    parser.add_argument("--timeline", help="Timeline tag (e.g., 1 or r01).")
    parser.add_argument("--workflow", help="Workflow path/id to attach to queue jobs.")
    parser.add_argument("--repeats", type=int, default=1, help="Repeat each job N times.")
    args = parser.parse_args()

    story_config, _, repo_root = load_story_config(
        story_root=args.story_root,
        story_config_path=args.story_config,
    )

    subjects_root_rel = Path(story_config.get("subjects_root") or "stories/template/subjects")
    subjects_root_abs = resolve_path(subjects_root_rel, repo_root)

    data_root_rel = Path(story_config.get("data_root") or "stories/template/data")
    output_queue = resolve_path(
        args.output_queue or f"{data_root_rel}/queues/asset_bible_queue.json",
        repo_root,
    )

    cards_path = resolve_path(args.cards or f"{subjects_root_rel}/asset_bible_cards.jsonl", repo_root)
    asset_bible_path = resolve_path(args.asset_bible or f"{subjects_root_rel}/ASSET_BIBLE.md", repo_root)

    cards = load_jsonl(cards_path)
    if not cards:
        cards = parse_asset_bible(asset_bible_path)

    timeline_label = story_config.get("timeline_label", "timeline")
    timeline_padding = int(story_config.get("timeline_index_padding", 2))
    timeline_tag = normalize_timeline_tag(args.timeline, timeline_padding)
    timeline_folder = f"{timeline_label}_{timeline_tag}"

    queue = []
    workflow_prefix = build_workflow_prefix(args.workflow or "")

    for card in cards:
        subject_id = card.get("id") or ""
        name = card.get("name") or ""
        subject_type = card.get("type") or ""
        if is_placeholder_subject(subject_id, name):
            continue

        subject_dir_rel, _ = resolve_subject_dir(subjects_root_rel, subjects_root_abs, card)
        subject_dir_str = str(subject_dir_rel).replace("\\", "/")
        subjects_root_str = str(subjects_root_rel).replace("\\", "/")
        if not subject_dir_str.startswith(subjects_root_str):
            subject_dir_rel = subjects_root_rel / subject_dir_rel
        if args.timeline and timeline_folder not in str(subject_dir_rel).replace("\\", "/"):
            continue

        output_dir = subject_dir_rel / "images" / "asset_bible"
        output_dir_str = str(output_dir).replace("\\", "/")
        output_basename = subject_id
        if workflow_prefix:
            output_basename = f"{workflow_prefix}__{subject_id}"

        prompt_entries = build_prompt_entries(card)
        if not prompt_entries:
            continue

        queue_type = QUEUE_TYPE_MAP.get(subject_type, "asset")

        for entry in prompt_entries:
            prompt = entry.get("prompt") or ""
            if not prompt:
                continue
            phase_tag = entry.get("phase_tag") or ""
            phase_label = entry.get("phase_label") or ""

            job_id = subject_id
            job_output = output_basename
            if phase_tag:
                job_id = f"{subject_id}__{phase_tag}"
                job_output = f"{output_basename}__{phase_tag}"

            queue.append({
                "id": job_id,
                "type": queue_type,
                "entity_type": queue_type,
                "entity_name": name or subject_id,
                "subject_id": subject_id,
                "subject_type": subject_type,
                "phase_id": phase_tag,
                "phase_name": phase_label,
                "prompt": prompt,
                "workflow": args.workflow or "",
                "output_dir": output_dir_str,
                "output_basename": job_output,
                "expected_outputs": 1,
                "repeat_count": max(1, int(args.repeats)),
            })

    if output_queue:
        output_queue.parent.mkdir(parents=True, exist_ok=True)
        ensure_dir(output_queue.parent)
        with output_queue.open("w", encoding="utf-8") as handle:
            json.dump(queue, handle, indent=2, ensure_ascii=False)
        print(f"Wrote asset bible queue: {output_queue}")

    print(f"Wrote {len(queue)} queue entries.")


if __name__ == "__main__":
    main()
