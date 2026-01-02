import os
import sys
import json
import requests
import uuid
import argparse
from pathlib import Path

# --- KONFIGURATION ---
COMFY_BASE_URL = "http://127.0.0.1:8188"
COMFY_PROMPT_URL = f"{COMFY_BASE_URL}/prompt"
COMFY_UPLOAD_URL = f"{COMFY_BASE_URL}/upload/image"
WORKFLOW_DIR = Path(r"C:\Users\sasch\henoch\workflows")

def find_node_by_title(workflow_json, title):
    """Sucht die Node-ID basierend auf dem benutzerdefinierten Titel."""
    for node_id, node_data in workflow_json.items():
        if node_data.get("_meta", {}).get("title") == title:
            return node_id
        if node_data.get("title") == title:
            return node_id
    return None


def set_lora_node_by_title(workflow_json, title, lora_name, strength_model):
    node_id = find_node_by_title(workflow_json, title)
    if not node_id:
        return False
    inputs = workflow_json[node_id].get("inputs", {})
    if "lora_name" in inputs:
        inputs["lora_name"] = lora_name
    if "strength_model" in inputs:
        inputs["strength_model"] = strength_model
    return True


def parse_lora_arg(value):
    raw = value.strip()
    if not raw:
        return None
    for sep in (":", "="):
        if sep in raw:
            name, strength = raw.rsplit(sep, 1)
            try:
                return name.strip(), float(strength.strip())
            except ValueError:
                return name.strip(), 1.0
    return raw, 1.0

def upload_image(file_path):
    """Lädt ein Bild zum ComfyUI-Server hoch und gibt den Dateinamen zurück."""
    if not os.path.exists(file_path):
        print(f"[WARN] Warnung: Bilddatei nicht gefunden: {file_path}")
        return None
    
    print(f"[INFO] Uploading: {os.path.basename(file_path)}...")
    with open(file_path, 'rb') as f:
        files = {'image': f}
        response = requests.post(COMFY_UPLOAD_URL, files=files)
        if response.status_code == 200:
            return response.json()['name']
        else:
            print(f"[ERROR] Upload Fehler: {response.text}")
            return None

def send_to_comfy(workflow_data):
    """Sendet den fertigen Payload an die Queue."""
    client_id = str(uuid.uuid4())
    payload = {"prompt": workflow_data, "client_id": client_id}
    try:
        response = requests.post(COMFY_PROMPT_URL, json=payload)
        if response.status_code == 200:
            print(f"[SUCCESS] Job eingereiht! Prompt-ID: {response.json().get('prompt_id')}")
        else:
            print(f"[ERROR] API Fehler: {response.text}")
    except Exception as e:
        print(f"[ERROR] Verbindung fehlgeschlagen: {e}")

def main():
    parser = argparse.ArgumentParser(description="Exeget:OS Multi-Modal Dispatcher")
    parser.add_argument("-w", "--workflow", required=True, help="Workflow Dateiname")
    parser.add_argument("-p", "--prompt", help="Text-Prompt für MASTER_PROMPT")
    parser.add_argument("-f", "--filename", help="Dateiname für MASTER_FILENAME")
    parser.add_argument("-i", "--images", nargs='*', help="Pfade zu Bildern für MASTER_IMAGE_1, 2, ...")
    parser.add_argument("--lora", action="append", help="LoRA name[:strength] (repeatable)")
    
    args = parser.parse_args()

    # 1. Workflow laden
    fname = args.workflow if args.workflow.endswith(".json") else args.workflow + ".json"
    workflow_path = WORKFLOW_DIR / fname
    if not workflow_path.exists():
        print(f"❌ Fehler: Workflow '{workflow_path}' nicht gefunden.")
        return
    with open(workflow_path, "r", encoding="utf-8") as f:
        workflow_json = json.load(f)

    # Check for UI format vs API format
    if "nodes" in workflow_json and "links" in workflow_json:
        print(f"ERROR: The workflow file '{workflow_path}' is in the UI format (saved from the web interface).")
        print("   Please export it in API format:")
        print("   1. Open ComfyUI settings (gear icon).")
        print("   2. Enable 'Enable Dev mode Options'.")
        print("   3. Click 'Save (API Format)' in the menu.")
        print("   4. Overwrite the file or save as a new one and update the script configuration.")
        sys.exit(1)

    # 2. Text-Injektion (MASTER_PROMPT)
    if args.prompt:
        text_node_id = find_node_by_title(workflow_json, "MASTER_PROMPT")
        if text_node_id:
            node_inputs = workflow_json[text_node_id]["inputs"]
            # Flexibilität für WAS-Nodes (text) oder Primitive (string)
            key = "text" if "text" in node_inputs else "string"
            node_inputs[key] = args.prompt
            print(f"[INFO] Text in MASTER_PROMPT (ID: {text_node_id}) injiziert.")

    # 3. Filename-Injektion (MASTER_FILENAME)
    if args.filename:
        fname_node_id = find_node_by_title(workflow_json, "MASTER_FILENAME")
        if fname_node_id:
            node_inputs = workflow_json[fname_node_id]["inputs"]
            # Flexibilität für WAS-Nodes (text) oder Primitive (string)
            key = "text" if "text" in node_inputs else "string"
            node_inputs[key] = args.filename
            print(f"[INFO] Dateiname in MASTER_FILENAME (ID: {fname_node_id}) injiziert: {args.filename}")
        else:
            print(f"[WARN] Warnung: Node 'MASTER_FILENAME' nicht gefunden. Dateiname wird ignoriert.")

    # 4. Image-Injektion (MASTER_IMAGE_n)
    if args.images:
        for idx, img_path in enumerate(args.images, start=1):
            title = f"MASTER_IMAGE_{idx}"
            img_node_id = find_node_by_title(workflow_json, title)
            
            if img_node_id:
                server_filename = upload_image(img_path)
                if server_filename:
                    workflow_json[img_node_id]["inputs"]["image"] = server_filename
                    print(f"[INFO] Bild in {title} (ID: {img_node_id}) injiziert.")
            else:
                print(f"[WARN] Hinweis: Node '{title}' nicht im Workflow gefunden. Ueberspringe.")

    # 5. LoRA Injection (optional)
    if args.lora:
        lora_entries = []
        for raw in args.lora:
            parsed = parse_lora_arg(raw)
            if parsed:
                lora_entries.append(parsed)
        if lora_entries:
            slots = ["LORA_DYNAMIC_01", "LORA_DYNAMIC_02"]
            for idx, (name, strength) in enumerate(lora_entries[: len(slots)]):
                ok = set_lora_node_by_title(workflow_json, slots[idx], name, strength)
                if ok:
                    print(f"[INFO] LoRA gesetzt: {slots[idx]} -> {name} ({strength})")
                else:
                    print(f"[WARN] LoRA Slot {slots[idx]} nicht gefunden.")
            if len(lora_entries) > len(slots):
                print(f"[WARN] {len(lora_entries) - len(slots)} LoRA(s) ignoriert (max {len(slots)}).")

    # 6. Absenden
    send_to_comfy(workflow_json)

if __name__ == "__main__":
    main()
