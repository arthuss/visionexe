import urllib.request
import json

COMFY_URL = "http://127.0.0.1:8188"

def get_loras():
    try:
        with urllib.request.urlopen(f"{COMFY_URL}/object_info/LoraLoaderModelOnly") as response:
            data = json.loads(response.read())
            # The input 'lora_name' usually contains the list of available files
            loras = data.get("LoraLoaderModelOnly", {}).get("input", {}).get("required", {}).get("lora_name", [])
            if isinstance(loras, list) and len(loras) > 0 and isinstance(loras[0], list):
                 return loras[0] # Sometimes it's a list inside a list
            return loras
    except Exception as e:
        print(f"Error: {e}")
        return []

loras = get_loras()
print("Found LoRAs:")
for l in loras:
    if "qwen" in l.lower() or "edit" in l.lower():
        print(f" - {l}")
