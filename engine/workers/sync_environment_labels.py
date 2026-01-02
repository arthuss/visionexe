import csv
import json
import os
import re
import shutil

ROOT_PATH = os.path.abspath(r"C:\Users\sasch\henoch")
ENV_DIR = os.path.join(ROOT_PATH, "Environments")
ENV_MD = os.path.join(ROOT_PATH, "environments.md")
MAPPING_CSV = os.path.join(ENV_DIR, "mapping.csv")
OUTPUT_ASSETS = os.path.join(ROOT_PATH, "ENVIRONMENT_ASSETS.json")
OUTPUT_TODO = os.path.join(ROOT_PATH, "ENVIRONMENT_LABEL_TODO.md")

IMAGE_EXTS = (".png", ".jpg", ".jpeg")
IGNORE_DIRS = {"reference_images"}

STAGE_FOLDER_MAP = {
    "Desert_Transition": "Etappe_1",
    "Rift_Valley_Black": "Etappe_2",
    "Rift_Valley_Yellow": "Etappe_2",
    "Ethiopian_Highlands": "Etappe_2",
    "Socotra_Coast": "Etappe_3",
    "The_North_Ice": "Etappe_3",
    "Astronomical_Desert": "Etappe_4",
}

def parse_environment_md(path):
    if not os.path.exists(path):
        return {}, {}

    env_tags = {}
    stages = {}

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    current_block = None
    current_stage = None
    in_mesh = False

    def finalize_stage():
        nonlocal current_stage, in_mesh
        if current_stage:
            stage_id = current_stage.get("id")
            if stage_id:
                stages[stage_id] = current_stage
        current_stage = None
        in_mesh = False

    for raw in lines:
        line = raw.strip()

        if line.startswith("#### "):
            finalize_stage()
            if "Etappe" in line:
                match = re.search(r"Etappe\s+(\d+)", line)
                stage_id = f"Etappe_{match.group(1)}" if match else None
                current_stage = {
                    "id": stage_id,
                    "title": line.replace("#### ", "").strip(),
                    "mesh_shift": []
                }
                continue

            current_block = {"title": line.replace("#### ", "").strip()}
            continue

        if current_block:
            if "**Vorkommen:**" in line:
                current_block["appearance"] = line.split("**Vorkommen:**", 1)[1].strip()
            elif "**Funktion:**" in line:
                current_block["function"] = line.split("**Funktion:**", 1)[1].strip()
            elif "**Visual DNA:**" in line:
                current_block["visual_dna"] = line.split("**Visual DNA:**", 1)[1].strip()
            elif "Environment-Tag:" in line:
                tag_match = re.search(r"`([^`]+)`", line)
                if tag_match:
                    tag = tag_match.group(1).strip()
                    current_block["tag"] = tag
                    env_tags[tag] = current_block
                current_block = None

        if current_stage:
            if line.startswith("*"):
                if "**Start:**" in line:
                    current_stage["start"] = line.split("**Start:**", 1)[1].strip()
                elif "**Ziel:**" in line:
                    current_stage["goal"] = line.split("**Ziel:**", 1)[1].strip()
                elif "**Distanz:**" in line:
                    current_stage["distance"] = line.split("**Distanz:**", 1)[1].strip()
                elif "**Mesh-Shift:**" in line:
                    in_mesh = True
                elif "**Transition-Logic:**" in line:
                    current_stage["transition_logic"] = line.split("**Transition-Logic:**", 1)[1].strip()
                    in_mesh = False
                elif in_mesh:
                    current_stage["mesh_shift"].append(line.lstrip("* ").strip())

    finalize_stage()
    return env_tags, stages

def inventory_images(base_dir):
    images = []
    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for filename in files:
            if not filename.lower().endswith(IMAGE_EXTS):
                continue
            full_path = os.path.join(root, filename)
            rel_path = os.path.relpath(full_path, base_dir)
            folder = os.path.basename(os.path.dirname(full_path))
            images.append({
                "filename": filename,
                "rel_path": rel_path.replace("\\", "/"),
                "folder": folder,
                "is_unsorted": folder == "unsortiert"
            })
    return images

def load_mapping(path):
    if not os.path.exists(path):
        return [], ["Image_Filename", "Target_Folder_Name", "Notes"]
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        return rows, reader.fieldnames or ["Image_Filename", "Target_Folder_Name", "Notes"]

def write_mapping(path, rows, fieldnames, backup=True):
    if backup and os.path.exists(path):
        backup_path = path + ".bak"
        if not os.path.exists(backup_path):
            shutil.copy2(path, backup_path)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def main():
    env_tags, stages = parse_environment_md(ENV_MD)
    images = inventory_images(ENV_DIR)

    rows, fieldnames = load_mapping(MAPPING_CSV)
    index = {row.get("Image_Filename", ""): row for row in rows if row.get("Image_Filename")}

    changes = 0
    unsorted = []
    for image in images:
        filename = image["filename"]
        folder = image["folder"]
        target = "" if image["is_unsorted"] else folder

        if image["is_unsorted"]:
            unsorted.append(image["rel_path"])

        if filename not in index:
            rows.append({
                "Image_Filename": filename,
                "Target_Folder_Name": target,
                "Notes": "auto-added"
            })
            changes += 1
            continue

        row = index[filename]
        current_target = (row.get("Target_Folder_Name") or "").strip()
        notes = row.get("Notes") or ""

        if not current_target and target:
            row["Target_Folder_Name"] = target
            changes += 1
        elif current_target and target and current_target != target:
            if "folder_mismatch" not in notes:
                row["Notes"] = (notes + " | " if notes else "") + f"folder_mismatch={target}"
                changes += 1

    if changes:
        write_mapping(MAPPING_CSV, rows, fieldnames)

    env_assets = {
        "environments": {},
        "stages": stages,
        "images": [],
        "unsorted_images": sorted(unsorted),
        "stats": {
            "images_total": len(images),
            "images_unsorted": len(unsorted),
            "mapping_updates": changes
        }
    }

    for image in images:
        folder = image["folder"]
        tag = folder if folder in env_tags else None
        stage_id = STAGE_FOLDER_MAP.get(folder)
        env_assets["images"].append({
            "file": image["rel_path"],
            "folder": folder,
            "tag": tag,
            "stage": stage_id
        })

    images_by_folder = {}
    for image in images:
        images_by_folder.setdefault(image["folder"], []).append(image["rel_path"])

    for tag, meta in env_tags.items():
        folder_images = images_by_folder.get(tag, [])
        env_assets["environments"][tag] = {
            "meta": meta,
            "folder": f"Environments/{tag}",
            "images": sorted(folder_images)
        }

    for folder, stage_id in STAGE_FOLDER_MAP.items():
        folder_images = images_by_folder.get(folder, [])
        env_assets["environments"][folder] = {
            "meta": stages.get(stage_id, {}),
            "folder": f"Environments/{folder}",
            "images": sorted(folder_images)
        }

    with open(OUTPUT_ASSETS, "w", encoding="utf-8") as f:
        json.dump(env_assets, f, indent=2)

    with open(OUTPUT_TODO, "w", encoding="utf-8") as f:
        f.write("# Environment Label TODO\n\n")
        f.write(f"- Total images: {len(images)}\n")
        f.write(f"- Unsorted images: {len(unsorted)}\n")
        f.write(f"- Mapping updates: {changes}\n\n")

        f.write("## Unsorted Images\n")
        for rel_path in sorted(unsorted):
            f.write(f"- {rel_path}\n")

        f.write("\n## Known Folders\n")
        for folder in sorted(images_by_folder.keys()):
            f.write(f"- {folder}: {len(images_by_folder[folder])}\n")

    print(f"Assets manifest saved to: {OUTPUT_ASSETS}")
    print(f"Label TODO saved to: {OUTPUT_TODO}")
    if changes:
        print(f"Updated mapping.csv (backup at {MAPPING_CSV}.bak)")
    else:
        print("No mapping.csv changes needed.")

if __name__ == "__main__":
    main()
