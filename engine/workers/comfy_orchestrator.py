import argparse
import json
import os
import re
import shutil
import time
import urllib.request
from pathlib import Path

import requests

from visionexe_paths import (
    load_engine_config,
    load_story_config,
    resolve_engine_root,
    resolve_path,
    resolve_repo_root,
)

# --- CONFIGURATION (resolved in main) ---
ENGINE_ROOT = resolve_engine_root()
REPO_ROOT = resolve_repo_root()

COMFY_URL = "http://127.0.0.1:8188"
WORKFLOW_DIR = None
OUTPUT_BASE = None
QUEUE_FILE = None
UPLOAD_CACHE_ROOT = None
WORKFLOW_INDEX = {}

# WSL Bridge Path (default; overridden by workspaces.json if present)
WSL_OUTPUT_PATH = r"\\wsl.localhost\Ubuntu24Old\root\ComfyUI_Py314\output"
IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp")

COMFY_WORKSPACE_ID_DEFAULT = "comfyui_py314"


def normalize_key(value):
    if value is None:
        return ""
    return re.sub(r"\s+", "", str(value)).lower()


def load_workspaces(engine_config, repo_root):
    path_value = engine_config.get("workspaces_path")
    config_path = resolve_path(path_value, repo_root) if path_value else None
    if not config_path or not config_path.exists():
        return {"workspaces": []}
    with config_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def select_workspace(workspaces, workspace_id):
    if workspace_id:
        for ws in workspaces:
            if ws.get("id") == workspace_id:
                return ws
    for ws in workspaces:
        for api in ws.get("apis", []) or []:
            if api.get("id") == "comfyui":
                return ws
    return None


def resolve_workspace_api(workspace, api_id="comfyui"):
    if not workspace:
        return None
    for api in workspace.get("apis", []) or []:
        if api.get("id") == api_id or api.get("type") == api_id:
            return api.get("base_url")
    apis = workspace.get("apis") or []
    return apis[0].get("base_url") if apis else None


def load_workflow_catalog(engine_config, repo_root):
    path_value = engine_config.get("workflow_catalog_path")
    catalog_path = resolve_path(path_value, repo_root) if path_value else None
    if not catalog_path or not catalog_path.exists():
        return None
    with catalog_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_workflow_index(catalog, repo_root):
    index = {}
    if not catalog:
        return index
    for entry in catalog.get("workflows", []):
        path_value = entry.get("path")
        if not path_value:
            continue
        path = resolve_path(path_value, repo_root)
        if not path or not path.exists():
            continue
        keys = [
            entry.get("id"),
            entry.get("label"),
            path.name,
            path.stem,
        ]
        for key in keys:
            normalized = normalize_key(key)
            if normalized and normalized not in index:
                index[normalized] = path
    return index

def list_matching_outputs(folder, prefix):
    if not os.path.exists(folder):
        return []
    return [
        f for f in os.listdir(folder)
        if f.startswith(prefix) and f.lower().endswith(IMAGE_EXTS)
    ]

def retrieve_images(filename_prefix, target_folder=OUTPUT_BASE, expected_min=1, retries=3, wait_s=2, move=False):
    """Copies (default) or moves images matching prefix from WSL output to local folder."""
    if not os.path.exists(WSL_OUTPUT_PATH):
        print(f"[ERR] WSL Path not accessible: {WSL_OUTPUT_PATH}")
        return []

    if not os.path.exists(target_folder):
        os.makedirs(target_folder, exist_ok=True)

    moved = []
    for attempt in range(retries):
        candidates = list_matching_outputs(WSL_OUTPUT_PATH, filename_prefix)
        if candidates and (len(candidates) >= expected_min or attempt == retries - 1):
            candidates.sort()
            for name in candidates:
                src = os.path.join(WSL_OUTPUT_PATH, name)
                dest = os.path.join(target_folder, name)
                if os.path.exists(dest):
                    continue
                try:
                    if move:
                        shutil.move(src, dest)
                    else:
                        shutil.copy2(src, dest)
                    moved.append(name)
                except Exception as e:
                    action = "move" if move else "copy"
                    print(f"[ERR] {action.title()} failed for {name}: {e}")
            if moved:
                print(f"  -> Retrieved: {', '.join(moved)}")
                return moved
        if attempt < retries - 1:
            time.sleep(wait_s)

    print(f"  [DEBUG] No outputs found for prefix {filename_prefix}")
    return moved

def get_job_type(job):
    return job.get("type") or job.get("entity_type") or job.get("entityType")

def resolve_workflow(name):
    if not name:
        return None
    candidate_path = Path(name)
    if candidate_path.is_absolute() and candidate_path.exists():
        return str(candidate_path)

    repo_candidate = resolve_path(name, REPO_ROOT)
    if repo_candidate and repo_candidate.exists():
        return str(repo_candidate)

    key = normalize_key(name)
    if key in WORKFLOW_INDEX:
        return str(WORKFLOW_INDEX[key])
    if not str(name).lower().endswith(".json"):
        key = normalize_key(f"{name}.json")
        if key in WORKFLOW_INDEX:
            return str(WORKFLOW_INDEX[key])

    if WORKFLOW_DIR:
        fallback_name = name
        if not str(fallback_name).lower().endswith(".json"):
            fallback_name = f"{fallback_name}.json"
        candidate = Path(WORKFLOW_DIR) / fallback_name
        if candidate.exists():
            return str(candidate)

    return None

def normalize_title(value):
    if not value:
        return ""
    # Strip non-alnum to handle styled titles
    return re.sub(r"[^A-Za-z0-9_]+", "", str(value)).lower()

def set_text_node_by_title(workflow, title, value):
    target = normalize_title(title)
    for node in workflow.values():
        meta_title = normalize_title(node.get("_meta", {}).get("title"))
        if meta_title == target:
            inputs = node.get("inputs", {})
            if "text" in inputs:
                inputs["text"] = value
                return True
            if "value" in inputs:
                inputs["value"] = value
                return True
    return False

def set_image_node_by_title(workflow, title, value):
    target = normalize_title(title)
    for node in workflow.values():
        meta_title = normalize_title(node.get("_meta", {}).get("title"))
        if meta_title == target:
            inputs = node.get("inputs", {})
            if "image" in inputs:
                inputs["image"] = value
                return True
    return False

def set_saveimage_prefix(workflow, prefix):
    updated = False
    for node in workflow.values():
        if node.get("class_type") == "SaveImage":
            inputs = node.get("inputs", {})
            if "filename_prefix" in inputs:
                inputs["filename_prefix"] = prefix
                updated = True
    return updated

def set_batch_size(workflow, batch_size):
    updated = 0
    for node in workflow.values():
        inputs = node.get("inputs", {})
        if "batch_size" not in inputs:
            continue
        class_type = (node.get("class_type") or "").lower()
        if class_type.startswith("empty") or "latent" in class_type:
            inputs["batch_size"] = batch_size
            updated += 1
    return updated

def get_output_prefix(job, suffix=None):
    if "output_basename" in job and job["output_basename"]:
        base = job["output_basename"]
    elif "master_filename" in job and job["master_filename"]:
        base = os.path.splitext(job["master_filename"])[0]
    else:
        base = job.get("id", "output")
    if suffix:
        return f"{base}{suffix}"
    return base

def get_job_id(job):
    job_id = job.get("id")
    if job_id:
        return str(job_id)
    output_basename = job.get("output_basename")
    if output_basename:
        return str(output_basename)
    output_filename = job.get("output_filename")
    if output_filename:
        return os.path.splitext(str(output_filename))[0]
    master_filename = job.get("master_filename")
    if master_filename:
        return os.path.splitext(str(master_filename))[0]
    entity = job.get("entity_name") or job.get("actor") or job.get("location")
    phase = job.get("phase_name") or job.get("phase")
    if entity and phase:
        return f"{entity}_{phase}"
    if entity:
        return str(entity)
    return "job"

def queue_prompt(prompt_workflow):
    """Sends a workflow prompt to the ComfyUI API."""
    p = {"prompt": prompt_workflow}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(f"{COMFY_URL}/prompt", data=data)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read())
    except Exception as e:
        print(f"Error connecting to ComfyUI: {e}")
        return None

def get_history(prompt_id):
    """Polls history for a specific prompt_id."""
    try:
        with urllib.request.urlopen(f"{COMFY_URL}/history/{prompt_id}") as response:
            return json.loads(response.read())
    except:
        return {}

def get_queue():
    """Fetches the current queue state from ComfyUI."""
    try:
        with urllib.request.urlopen(f"{COMFY_URL}/queue") as response:
            return json.loads(response.read())
    except:
        return None

def queue_contains_prompt(queue_data, prompt_id):
    if not queue_data:
        return False
    for key in ("queue_running", "queue_pending"):
        items = queue_data.get(key, [])
        for item in items:
            if isinstance(item, dict) and item.get("prompt_id") == prompt_id:
                return True
            if isinstance(item, (list, tuple)) and prompt_id in item:
                return True
    return False

def wait_for_job(prompt_id):
    """Waits for job completion and returns history data."""
    print(f"  -> Waiting for job {prompt_id}...", end="", flush=True)
    missing_count = 0
    while True:
        history = get_history(prompt_id)
        if prompt_id in history:
            print(" Done.")
            return history[prompt_id]

        queue_data = get_queue()
        if queue_data is not None:
            if not queue_contains_prompt(queue_data, prompt_id):
                missing_count += 1
                if missing_count >= 2:
                    print(" Cancelled.")
                    return None
            else:
                missing_count = 0

        time.sleep(3)
        print(".", end="", flush=True)

def run_job_genesis(job, workflow_override=None, allowed_types=("actor",), repeats=1, move_outputs=False, batch_size=0, batch_repeats=False, skip_existing=True):
    """PHASE 1: Only run initial Flux generation."""
    if get_job_type(job) not in allowed_types:
        return False

    job_id = get_job_id(job)
    workflow_name = workflow_override or job.get("workflow_step1") or job.get("workflow")
    wf_path = resolve_workflow(workflow_name)
    if not wf_path:
        print(f"  [ERR] Workflow not found for {workflow_name}")
        return False

    base_prefix = get_output_prefix(job)
    expected_min = job.get("expected_outputs")
    if expected_min is None:
        expected_min = 2

    # Determine target directory
    target_dir = resolve_output_dir(job.get("output_dir") or job.get("target_folder"))
    target_dir.mkdir(parents=True, exist_ok=True)

    repeat_count = int(job.get("repeat_count") or repeats or 1)
    effective_batch = int(batch_size or 0)
    if batch_repeats and repeat_count > 1 and effective_batch <= 1:
        effective_batch = repeat_count
        repeat_count = 1
    any_success = False

    for idx in range(1, repeat_count + 1):
        prefix = base_prefix if repeat_count == 1 else f"{base_prefix}__r{idx:02d}"

        if skip_existing:
            existing = list_matching_outputs(target_dir, prefix)
            if len(existing) >= expected_min:
                print(f"  [SKIP] {prefix} already exists ({len(existing)} files).")
                any_success = True
                continue

            # Recover orphaned outputs from WSL before re-queueing
            recovered = retrieve_images(prefix, target_folder=target_dir, expected_min=expected_min, retries=1, wait_s=0, move=move_outputs)
            if len(existing) + len(recovered) >= expected_min:
                print(f"  [RECOVERED] {prefix} outputs moved from WSL.")
                any_success = True
                continue

        print(f"\n[GENESIS] {job_id} -> {prefix}")
        print(f"  -> Prompt: {job['prompt'][:100]}...")

        # Load Workflow
        with open(wf_path, 'r', encoding='utf-8') as f:
            wf = json.load(f)

        if effective_batch and effective_batch > 1:
            batch_updates = set_batch_size(wf, effective_batch)
            if batch_updates == 0:
                print(f"  [WARN] No batch_size nodes updated for {job_id}.")
            expected_min = max(expected_min, effective_batch)

        # Update MASTER_PROMPT / MASTER_FILENAME by title
        if not set_text_node_by_title(wf, "MASTER_PROMPT", job["prompt"]):
            print("  [WARN] MASTER_PROMPT node not found.")
        if not set_text_node_by_title(wf, "MASTER_FILENAME", prefix):
            # Fallback: set SaveImage prefix directly
            set_saveimage_prefix(wf, prefix)

        res = queue_prompt(wf)
        if not res:
            print("  [ERR] ComfyUI connection failed.")
            return any_success

        prompt_id = res["prompt_id"]
        history = wait_for_job(prompt_id)

        if history is None:
            print("  [CANCELLED] Job removed from queue.")
            return any_success

        if prompt_id in history:
            # Success! Retrieve from WSL
            time.sleep(1) # Small buffer for file system
            retrieved = retrieve_images(prefix, target_folder=target_dir, expected_min=expected_min, retries=5, wait_s=2, move=move_outputs)
            if retrieved:
                any_success = True

    return any_success

def upload_image(file_path):
    """Uploads an image to ComfyUI."""
    url = f"{COMFY_URL}/upload/image"
    try:
        with open(file_path, 'rb') as f:
            files = {'image': f}
            response = requests.post(url, files=files)
            if response.status_code == 200:
                # Return the filename as ComfyUI sees it (might be renamed)
                return response.json().get("name")
            else:
                print(f"[ERR] Upload failed: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        print(f"[ERR] Upload exception: {e}")
        return None

def prepare_upload_image(input_path):
    """Convert problematic formats to PNG for ComfyUI LoadImage."""
    ext = os.path.splitext(input_path)[1].lower()
    if ext not in (".jpg", ".jpeg", ".webp"):
        return input_path, False

    try:
        from PIL import Image, ImageFile
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        with Image.open(input_path) as img:
            img = img.convert("RGB")
            cache_root = UPLOAD_CACHE_ROOT or REPO_ROOT
            tmp_dir = Path(cache_root) / "_upload_cache"
            tmp_dir.mkdir(parents=True, exist_ok=True)
            base = os.path.splitext(os.path.basename(input_path))[0]
            tmp_path = tmp_dir / f"{base}__upload.png"
            img.save(tmp_path, format="PNG")
            return str(tmp_path), True
    except Exception as e:
        print(f"[WARN] Failed to convert image, uploading original: {e}")
        return input_path, False


def resolve_output_dir(path_value):
    if not path_value:
        return Path(OUTPUT_BASE)
    candidate = Path(path_value)
    if candidate.is_absolute():
        return candidate
    normalized = str(path_value).replace("\\", "/")
    if normalized.startswith(("stories/", "engine/", "data/")):
        return REPO_ROOT / normalized
    return Path(OUTPUT_BASE) / normalized


def resolve_input_path(path_value):
    if not path_value:
        return None
    candidate = Path(path_value)
    if candidate.is_absolute():
        return candidate
    repo_candidate = REPO_ROOT / str(path_value)
    if repo_candidate.exists():
        return repo_candidate
    return Path(OUTPUT_BASE) / str(path_value)

def run_job_environment(job, workflow_override=None, output_in_place=False, repeats=1, move_outputs=False, skip_existing=True):
    """PHASE 2: Environment Multiview Generation."""
    if get_job_type(job) != "environment":
        return False

    job_id = get_job_id(job)
    print(f"\n[ENVIRONMENT] {job_id}")
    
    base_prefix = get_output_prefix(job, suffix="_MV")
    target_dir = Path(OUTPUT_BASE)
    input_path = resolve_input_path(job.get("input_image_path"))
    if output_in_place and input_path:
        target_dir = Path(input_path).parent
    elif "output_folder" in job:
        target_dir = resolve_output_dir(job["output_folder"])
    target_dir.mkdir(parents=True, exist_ok=True)

    repeat_count = int(job.get("repeat_count") or repeats or 1)
    any_success = False

    if not input_path or not Path(input_path).exists():
        print(f"  [ERR] Input image not found: {input_path}")
        return False

    for idx in range(1, repeat_count + 1):
        run_prefix = base_prefix if repeat_count == 1 else f"{base_prefix}__r{idx:02d}"

        if skip_existing:
            existing = list_matching_outputs(target_dir, run_prefix)
            if existing:
                print(f"  [SKIP] {run_prefix} already exists.")
                any_success = True
                continue

        recovered = retrieve_images(run_prefix, target_folder=target_dir, expected_min=1, retries=1, wait_s=0)
        if recovered:
            print(f"  [RECOVERED] Found existing file in WSL for {run_prefix}")
            any_success = True
            continue

        # Upload Image
        upload_path, is_temp = prepare_upload_image(str(input_path))
        uploaded_name = upload_image(upload_path)
        if is_temp:
            try:
                os.remove(upload_path)
            except Exception as e:
                print(f"[WARN] Cleanup failed for temp image: {e}")
        if not uploaded_name:
            return any_success
        print(f"  -> Uploaded: {uploaded_name}")

        # Load Workflow
        wf_filename = workflow_override or job.get("workflow_step2")
        wf_path = resolve_workflow(wf_filename)
        if not os.path.exists(wf_path):
            print(f"  [ERR] Workflow file not found: {wf_path}")
            return any_success
            
        with open(wf_path, 'r', encoding='utf-8') as f:
            wf = json.load(f)

        # Check for UI format
        if "nodes" in wf and isinstance(wf["nodes"], list):
            print(f"  [ERR] Workflow {wf_filename} is in UI format. Please save as API format.")
            return any_success

        # Modify Workflow
        if not set_image_node_by_title(wf, "MASTER_IMAGE", uploaded_name):
            print("  [WARN] MASTER_IMAGE node not found in workflow.")

        if not set_text_node_by_title(wf, "MASTER_FILENAME", run_prefix):
            if not set_saveimage_prefix(wf, run_prefix):
                print("  [WARN] SaveImage node not found in workflow.")

        # Queue Job
        res = queue_prompt(wf)
        if not res:
            print("  [ERR] ComfyUI connection failed.")
            return any_success
        prompt_id = res["prompt_id"]
        job_result = wait_for_job(prompt_id)

        if job_result is None:
            print("  [CANCELLED] Job removed from queue.")
            return any_success

        if job_result:
            if "status" in job_result and job_result["status"].get("status_str") == "error":
                print(f"  [ERR] Job failed in ComfyUI: {job_result['status']}")
                continue

            if "outputs" not in job_result:
                print(f"  [ERR] Job finished but no outputs found. Full history: {job_result}")
                continue
                
            time.sleep(1)
            retrieved = retrieve_images(run_prefix, target_folder=target_dir, expected_min=1, retries=3, wait_s=2, move=move_outputs)
            if retrieved:
                any_success = True
            else:
                print(f"  [ERR] Failed to retrieve image with prefix: {run_prefix}")
                if os.path.exists(WSL_OUTPUT_PATH):
                    files = os.listdir(WSL_OUTPUT_PATH)
                    matching = [f for f in files if job_id in f]
                    if matching:
                        print(f"    Found similar: {matching[:5]}")
                    else:
                        print(f"    First 5 files: {files[:5]}")

    return any_success

def main():
    parser = argparse.ArgumentParser(description="ComfyUI Orchestrator for VisionExe Assets")
    parser.add_argument("--story-root", help="Story root path (defaults to engine_config default_story_root).")
    parser.add_argument("--story-config", help="Path to story_config.json (overrides story-root).")
    parser.add_argument("--comfy-workspace", default=COMFY_WORKSPACE_ID_DEFAULT, help="Workspace id for ComfyUI (workspaces.json).")
    parser.add_argument("--actors", action="store_true", help="Run only Actor jobs (Phase 1)")
    parser.add_argument("--props", action="store_true", help="Run only Prop jobs (Phase 1)")
    parser.add_argument("--assets", action="store_true", help="Run only Asset Bible jobs (Phase 1)")
    parser.add_argument("--envs", action="store_true", help="Run only Environment jobs (Phase 2)")
    parser.add_argument("--queue", dest="queue_file", help="Override queue file path (defaults to story_config lora_training_queue_path).")
    parser.add_argument("--text-to-image", dest="text_to_image", help="Override text-to-image workflow (id/label/path).")
    parser.add_argument("--image-to-image", dest="image_to_image", help="Override image-to-image workflow (id/label/path).")
    parser.add_argument("--output-in-place", action="store_true", help="Save env outputs next to input images")
    parser.add_argument("--env-repeats", type=int, default=1, help="Repeat each env job N times")
    parser.add_argument("--actor-repeats", type=int, default=1, help="Repeat each actor job N times")
    parser.add_argument("--prop-repeats", type=int, default=1, help="Repeat each prop job N times")
    parser.add_argument("--asset-repeats", type=int, default=1, help="Repeat each asset job N times")
    parser.add_argument("--batch-size", type=int, default=0, help="Set batch_size for latent nodes (single run)")
    parser.add_argument("--batch-repeats", action="store_true", help="Use repeats as batch_size (single run)")
    parser.add_argument("--move-outputs", action="store_true", help="Move outputs from WSL instead of copying (default is copy)")
    parser.add_argument("--no-skip-existing", action="store_true", help="Always queue jobs even if outputs already exist")
    args = parser.parse_args()

    engine_config = load_engine_config(ENGINE_ROOT)
    story_config, _, repo_root = load_story_config(
        story_root=args.story_root,
        story_config_path=args.story_config,
    )

    workspaces_config = load_workspaces(engine_config, repo_root)
    workspace = select_workspace(workspaces_config.get("workspaces", []), args.comfy_workspace)

    global COMFY_URL, WORKFLOW_DIR, OUTPUT_BASE, QUEUE_FILE, WSL_OUTPUT_PATH, UPLOAD_CACHE_ROOT, WORKFLOW_INDEX

    comfy_url = resolve_workspace_api(workspace, "comfyui")
    if comfy_url:
        COMFY_URL = comfy_url

    if workspace:
        output_path = workspace.get("windows_output_path") or workspace.get("output_path")
        if output_path:
            WSL_OUTPUT_PATH = output_path

    workflow_dir = ENGINE_ROOT / "workflows"
    WORKFLOW_DIR = workflow_dir if workflow_dir.exists() else None

    output_base = resolve_path(story_config.get("produced_assets_root"), repo_root)
    if not output_base:
        raise SystemExit("produced_assets_root missing in story_config.json")
    OUTPUT_BASE = Path(output_base)

    cache_root = resolve_path(story_config.get("data_root"), repo_root) or repo_root
    UPLOAD_CACHE_ROOT = Path(cache_root)

    workflow_catalog = load_workflow_catalog(engine_config, repo_root)
    WORKFLOW_INDEX = build_workflow_index(workflow_catalog, repo_root)

    # If no specific flag is set, run both
    run_all = not args.actors and not args.envs and not args.props and not args.assets
    run_actors = args.actors or run_all
    run_envs = args.envs or run_all
    run_props = args.props
    run_assets = args.assets or run_all
    t2i_override = args.text_to_image
    i2i_override = args.image_to_image

    queue_file = args.queue_file or story_config.get("lora_training_queue_path")
    if not queue_file:
        raise SystemExit("lora_training_queue_path missing in story_config.json")
    queue_path = resolve_path(queue_file, repo_root)
    QUEUE_FILE = queue_path
    if not queue_path or not queue_path.exists():
        print(f"No queue file found at {queue_path}. Run prepare_lora_queue.py first.")
        return

    with queue_path.open("r", encoding="utf-8") as f:
        queue = json.load(f)

    success_count = 0

    # PHASE 1: ACTORS
    if run_actors:
        actor_jobs = [j for j in queue if get_job_type(j) == "actor"]
        print(f"--- STARTING PHASE 1: GENESIS ({len(actor_jobs)} Actor Jobs) ---")
        print(f"ComfyUI URL: {COMFY_URL}")
        print(f"Output Path: {OUTPUT_BASE}")
        
        try:
            for i, job in enumerate(actor_jobs):
                print(f"\nProgress: {i+1}/{len(actor_jobs)}")
                if run_job_genesis(job, workflow_override=t2i_override, allowed_types=("actor",), repeats=args.actor_repeats, move_outputs=args.move_outputs, batch_size=args.batch_size, batch_repeats=args.batch_repeats, skip_existing=not args.no_skip_existing):
                    success_count += 1
                else:
                    print(f"  [!] Job {get_job_id(job)} failed or was skipped.")
                    
        except KeyboardInterrupt:
            print("\n[STOP] Orchestrator stopped by user.")
            return

        print(f"\n--- PHASE 1 COMPLETE ---")

    # PHASE 1B: PROPS
    if run_props:
        prop_jobs = [j for j in queue if get_job_type(j) == "prop"]
        print(f"\n--- STARTING PHASE 1: PROPS ({len(prop_jobs)} Prop Jobs) ---")
        print(f"ComfyUI URL: {COMFY_URL}")
        print(f"Output Path: {OUTPUT_BASE}")

        try:
            for i, job in enumerate(prop_jobs):
                print(f"\nProgress: {i+1}/{len(prop_jobs)}")
                if run_job_genesis(job, workflow_override=t2i_override, allowed_types=("prop",), repeats=args.prop_repeats, move_outputs=args.move_outputs, batch_size=args.batch_size, batch_repeats=args.batch_repeats, skip_existing=not args.no_skip_existing):
                    success_count += 1
                else:
                    print(f"  [!] Job {get_job_id(job)} failed or was skipped.")

        except KeyboardInterrupt:
            print("\n[STOP] Orchestrator stopped by user.")
            return

    # PHASE 1C: ASSET BIBLE
    if run_assets:
        asset_jobs = [j for j in queue if get_job_type(j) == "asset"]
        print(f"\n--- STARTING PHASE 1: ASSET BIBLE ({len(asset_jobs)} Asset Jobs) ---")
        print(f"ComfyUI URL: {COMFY_URL}")
        print(f"Output Path: {OUTPUT_BASE}")

        try:
            for i, job in enumerate(asset_jobs):
                print(f"\nProgress: {i+1}/{len(asset_jobs)}")
                if run_job_genesis(job, workflow_override=t2i_override, allowed_types=("asset",), repeats=args.asset_repeats, move_outputs=args.move_outputs, batch_size=args.batch_size, batch_repeats=args.batch_repeats, skip_existing=not args.no_skip_existing):
                    success_count += 1
                else:
                    print(f"  [!] Job {get_job_id(job)} failed or was skipped.")

        except KeyboardInterrupt:
            print("\n[STOP] Orchestrator stopped by user.")
            return
    
    # PHASE 2: ENVIRONMENTS
    if run_envs:
        env_jobs = [j for j in queue if get_job_type(j) == "environment"]
        print(f"\n--- STARTING PHASE 2: ENVIRONMENTS ({len(env_jobs)} Environment Jobs) ---")
        
        try:
            for i, job in enumerate(env_jobs):
                print(f"\nProgress: {i+1}/{len(env_jobs)}")
                if run_job_environment(
                    job,
                    workflow_override=i2i_override,
                    output_in_place=args.output_in_place,
                    repeats=args.env_repeats,
                    move_outputs=args.move_outputs,
                    skip_existing=not args.no_skip_existing,
                ):
                    success_count += 1
                else:
                    print(f"  [!] Job {get_job_id(job)} failed.")
                    
        except KeyboardInterrupt:
            print("\n[STOP] Orchestrator stopped by user.")
            return

    print(f"\n--- ALL PHASES COMPLETE ---")
    print(f"Total successfully generated: {success_count} images.")

if __name__ == "__main__":
    main()
