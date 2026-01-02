import argparse
import copy
import csv
import json
import os
import re
import time
import uuid
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
DEFAULT_CSV = ROOT / "first_analysis_progress_python.csv"
DEFAULT_WORKFLOW = ROOT / "workflows" / "flux_schnell.json"
DEFAULT_COMFY_URL = "http://127.0.0.1:8188"

JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*([\[{].*?[\]}])\s*```", re.DOTALL | re.IGNORECASE)


def find_node_by_title(workflow_json, title):
    for node_id, node_data in workflow_json.items():
        if node_data.get("_meta", {}).get("title") == title:
            return node_id
        if node_data.get("title") == title:
            return node_id
    return None


def set_text_node(workflow_json, title, value):
    node_id = find_node_by_title(workflow_json, title)
    if not node_id:
        return False
    inputs = workflow_json[node_id].get("inputs", {})
    key = "text" if "text" in inputs else "string"
    inputs[key] = value
    return True


def resolve_workflow_path(value):
    if not value:
        return DEFAULT_WORKFLOW
    path = Path(value)
    if path.is_file():
        return path
    name = value if value.endswith(".json") else f"{value}.json"
    return ROOT / "workflows" / name


def load_workflow(path):
    if not path.exists():
        raise FileNotFoundError(f"Workflow not found: {path}")
    with open(path, "r", encoding="utf-8") as handle:
        workflow_json = json.load(handle)
    if "nodes" in workflow_json and "links" in workflow_json:
        raise ValueError(
            "Workflow is in UI format. Export in API format (Save -> API Format)."
        )
    return workflow_json


def extract_json_blocks(text):
    return [match.group(1) for match in JSON_BLOCK_RE.finditer(text or "")]


def normalize_list(value):
    if not value:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    return [str(value).strip()] if str(value).strip() else []


def build_entry_prompt_summary(entry):
    name = entry.get("name") or entry.get("id") or entry.get("title")
    role = entry.get("role") or entry.get("type")
    traits = normalize_list(
        entry.get("visualTraits")
        or entry.get("visual_traits")
        or entry.get("traits")
        or entry.get("visuals")
    )
    changes = normalize_list(
        entry.get("changes")
        or entry.get("stateChanges")
        or entry.get("state_changes")
    )
    parts = []
    if name:
        parts.append(str(name).strip())
    if role:
        parts.append(str(role).strip())
    if traits:
        parts.append("visual traits: " + ", ".join(traits))
    if changes:
        parts.append("changes: " + ", ".join(changes))
    return ", ".join([part for part in parts if part]).strip()


def build_entry_prompt_json(entry, strip_braces):
    text = json.dumps(entry, ensure_ascii=False, indent=2)
    if not strip_braces:
        return text.strip()
    lines = text.splitlines()
    if isinstance(entry, dict) and lines and lines[0].strip().startswith("{"):
        lines = lines[1:]
    if isinstance(entry, dict) and lines and lines[-1].strip().startswith("}"):
        lines = lines[:-1]
    return "\n".join(lines).strip()


def slugify(value):
    text = str(value or "").lower().strip()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_") or "unknown"

def safe_console_text(text):
    if text is None:
        return ""
    return str(text).encode("ascii", errors="backslashreplace").decode("ascii")


def parse_chapter_filter(value):
    if not value:
        return None
    cleaned = str(value).replace("_", " ").replace("\u2013", "-").replace("\u2014", "-")
    chapters = set()
    for part in re.split(r"[,\s]+", cleaned.strip()):
        if not part:
            continue
        if "-" in part:
            start, end = part.split("-", 1)
            if start.isdigit() and end.isdigit():
                a, b = int(start), int(end)
                if a > b:
                    a, b = b, a
                chapters.update(range(a, b + 1))
        elif part.isdigit():
            chapters.add(int(part))
    return chapters or None


def queue_prompt(comfy_url, workflow_json):
    payload = {"prompt": workflow_json, "client_id": str(uuid.uuid4())}
    response = requests.post(f"{comfy_url}/prompt", json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    return data.get("prompt_id")


def iter_entries(payload, list_key):
    if isinstance(payload, dict):
        entries = payload.get(list_key)
    elif isinstance(payload, list) and list_key in ("", "*", "root"):
        entries = payload
    else:
        return []
    if not isinstance(entries, list):
        return []
    normalized = []
    for entry in entries:
        if isinstance(entry, dict):
            normalized.append(entry)
        elif isinstance(entry, str):
            normalized.append({"name": entry})
        else:
            normalized.append({"value": entry})
    return normalized


def resolve_entry_field(entry, name_field):
    if not isinstance(entry, dict):
        return None
    return entry.get(name_field) or entry.get("name") or entry.get("id") or entry.get("title")


def main():
    parser = argparse.ArgumentParser(
        description="Queue JSON prompts from first_analysis_progress_python.csv"
    )
    parser.add_argument("--csv", default=str(DEFAULT_CSV), help="CSV source path")
    parser.add_argument("--workflow", default=str(DEFAULT_WORKFLOW), help="ComfyUI workflow")
    parser.add_argument("--comfy-url", default=DEFAULT_COMFY_URL, help="ComfyUI base URL")
    parser.add_argument("--status", default="DONE", help="Filter by status (or 'all')")
    parser.add_argument("--chapter", default="", help="Filter chapters (e.g. 1,2,5-7)")
    parser.add_argument(
        "--prompt-mode",
        default="entry",
        choices=("block", "entry", "raw-json", "summary"),
        help=(
            "Prompt format: block queues each JSON block as-is; "
            "entry uses list entries with braces; raw-json strips braces; summary builds a text line"
        ),
    )
    parser.add_argument(
        "--list-key",
        default="actors",
        help="List key inside JSON blocks to expand (e.g. actors, scenes, verses)",
    )
    parser.add_argument(
        "--name-mode",
        default="index",
        choices=("index", "field"),
        help="Filename mode for list entries (index or entry field)",
    )
    parser.add_argument(
        "--name-field",
        default="name",
        help="Field name to use when name-mode=field",
    )
    parser.add_argument("--prefix", default="", help="Prompt prefix")
    parser.add_argument("--suffix", default="", help="Prompt suffix")
    parser.add_argument("--sleep", type=float, default=0.2, help="Pause between queue calls")
    parser.add_argument("--dry-run", action="store_true", help="Print prompts without queueing")
    parser.add_argument("--out", default="", help="Optional JSON report path")
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    workflow_path = resolve_workflow_path(args.workflow)
    base_workflow = load_workflow(workflow_path)

    chapter_filter = parse_chapter_filter(args.chapter)
    status_filter = None if args.status.strip().lower() == "all" else args.status.strip().lower()

    queued = []
    errors = []
    counts = {}

    with open(csv_path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row_index, row in enumerate(reader, start=1):
            chapter_raw = (row.get("ChapterID") or "").strip()
            status_raw = (row.get("Status") or "").strip()
            raw_content = row.get("RawContent") or ""
            try:
                chapter_id = int(chapter_raw)
            except ValueError:
                chapter_id = None

            if chapter_filter and chapter_id not in chapter_filter:
                continue
            if status_filter and status_raw.lower() != status_filter:
                continue

            blocks = extract_json_blocks(raw_content)
            if not blocks:
                errors.append({
                    "row": row_index,
                    "chapter": chapter_id,
                    "status": status_raw,
                    "error": "no_json_block",
                })
                continue

            list_key = args.list_key.strip()

            for block_index, block in enumerate(blocks, start=1):
                if args.prompt_mode == "block":
                    prompt = block.strip()
                    if args.prefix:
                        prompt = f"{args.prefix} {prompt}".strip()
                    if args.suffix:
                        prompt = f"{prompt} {args.suffix}".strip()
                    if not prompt:
                        continue
                    chapter_tag = f"ch{chapter_id:03d}" if chapter_id is not None else "ch000"
                    key = (chapter_tag, "block")
                    counts[key] = counts.get(key, 0) + 1
                    filename = f"{chapter_tag}__block_{counts[key]:02d}"

                    record = {
                        "chapter": chapter_id,
                        "status": status_raw,
                        "actor": None,
                        "prompt": prompt,
                        "filename": filename,
                        "row": row_index,
                        "block": block_index,
                    }

                    if args.dry_run:
                        print(f"[DRY RUN] {filename}: {safe_console_text(prompt)}")
                        queued.append({**record, "queued": False})
                        continue

                    workflow = copy.deepcopy(base_workflow)
                    if not set_text_node(workflow, "MASTER_PROMPT", prompt):
                        errors.append({
                            "row": row_index,
                            "chapter": chapter_id,
                            "status": status_raw,
                            "error": "missing MASTER_PROMPT node",
                        })
                        continue
                    set_text_node(workflow, "MASTER_FILENAME", filename)
                    try:
                        prompt_id = queue_prompt(args.comfy_url, workflow)
                        print(f"[QUEUED] {filename} -> {prompt_id}")
                        queued.append({**record, "queued": True, "prompt_id": prompt_id})
                    except requests.RequestException as exc:
                        errors.append({
                            "row": row_index,
                            "chapter": chapter_id,
                            "status": status_raw,
                            "error": f"comfy_error: {exc}",
                        })
                    if args.sleep:
                        time.sleep(args.sleep)
                    continue

                try:
                    payload = json.loads(block)
                except json.JSONDecodeError as exc:
                    errors.append({
                        "row": row_index,
                        "chapter": chapter_id,
                        "status": status_raw,
                        "error": f"json_decode_error: {exc}",
                    })
                    continue

                entries = iter_entries(payload, list_key)
                if not entries:
                    errors.append({
                        "row": row_index,
                        "chapter": chapter_id,
                        "status": status_raw,
                        "error": f"missing_list_key: {list_key}",
                    })
                    continue

                list_slug = slugify(list_key) or "entries"

                for entry in entries:
                    if args.prompt_mode == "summary":
                        prompt = build_entry_prompt_summary(entry)
                    else:
                        strip_braces = args.prompt_mode == "raw-json"
                        prompt = build_entry_prompt_json(entry, strip_braces)
                    if args.prefix:
                        prompt = f"{args.prefix} {prompt}".strip()
                    if args.suffix:
                        prompt = f"{prompt} {args.suffix}".strip()
                    if not prompt:
                        continue
                    chapter_tag = f"ch{chapter_id:03d}" if chapter_id is not None else "ch000"
                    if args.name_mode == "field":
                        entry_name = resolve_entry_field(entry, args.name_field) or "unknown"
                        entry_slug = slugify(entry_name)
                        key = (chapter_tag, entry_slug)
                        counts[key] = counts.get(key, 0) + 1
                        suffix = f"__v{counts[key]:02d}" if counts[key] > 1 else ""
                        filename = f"{chapter_tag}__{list_slug}_{entry_slug}{suffix}"
                    else:
                        key = (chapter_tag, list_slug)
                        counts[key] = counts.get(key, 0) + 1
                        filename = f"{chapter_tag}__{list_slug}_{counts[key]:02d}"

                    record = {
                        "chapter": chapter_id,
                        "status": status_raw,
                        "actor": resolve_entry_field(entry, args.name_field),
                        "prompt": prompt,
                        "filename": filename,
                        "row": row_index,
                        "block": block_index,
                    }

                    if args.dry_run:
                        print(f"[DRY RUN] {filename}: {safe_console_text(prompt)}")
                        queued.append({**record, "queued": False})
                        continue

                    workflow = copy.deepcopy(base_workflow)
                    if not set_text_node(workflow, "MASTER_PROMPT", prompt):
                        errors.append({
                            "row": row_index,
                            "chapter": chapter_id,
                            "status": status_raw,
                            "error": "missing MASTER_PROMPT node",
                        })
                        continue
                    set_text_node(workflow, "MASTER_FILENAME", filename)
                    try:
                        prompt_id = queue_prompt(args.comfy_url, workflow)
                        print(f"[QUEUED] {filename} -> {prompt_id}")
                        queued.append({**record, "queued": True, "prompt_id": prompt_id})
                    except requests.RequestException as exc:
                        errors.append({
                            "row": row_index,
                            "chapter": chapter_id,
                            "status": status_raw,
                            "error": f"comfy_error: {exc}",
                        })
                    if args.sleep:
                        time.sleep(args.sleep)

    if args.out:
        report = {
            "csv": str(csv_path),
            "workflow": str(workflow_path),
            "queued": queued,
            "errors": errors,
        }
        with open(args.out, "w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2)
        print(f"[INFO] Report written to {args.out}")

    print(f"[INFO] Done. queued={len(queued)} errors={len(errors)}")


if __name__ == "__main__":
    main()
