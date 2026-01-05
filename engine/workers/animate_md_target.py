import requests
import json
import sys
import time

# Configuration
URL = "http://127.0.0.1:8123"
TARGET_PROP_NAME = "MD_Target"

def post(action, payload=None):
    retries = 10
    for i in range(retries):
        try:
            res = requests.post(URL, json={"action": action, "payload": payload or {}}, timeout=5)
            return res.json()
        except Exception as e:
            print(f"Connection attempt {i+1}/{retries} failed: {e}")
            time.sleep(3)
    return None

def animate_target(x, y, z, duration_sec=5.0):
    print(f"Animating '{TARGET_PROP_NAME}' to ({x}, {y}, {z}) over {duration_sec}s...")
    
    # We use the existing 'load_asset' or generic prop manipulation if available.
    # Since we don't have a generic 'set_prop_keys' action yet, we might need to rely on
    # manual setup or add 'apply_prop_keys' to the server.
    
    # BUT! We can use 'run_python' to do it directly (once the server reloads).
    code = f"""
import RLPy
prop = RLPy.RScene.FindObject(RLPy.EObjectType_Prop, "{TARGET_PROP_NAME}")
if prop:
    control = prop.GetControl("Transform")
    if control:
        start_time = RLPy.RGlobal.GetTime()
        end_time = start_time + RLPy.RTime(int({duration_sec} * 60 * 1000)) # Approx logic
        
        # Simple linear move: Set key at end time
        # Note: Real logic needs accurate time conversion
        fps = RLPy.RGlobal.GetFps()
        t_end = start_time + fps.FrameTimeFromSecond({duration_sec})
        
        xform = RLPy.RTransform.IDENTITY
        xform.T().x = {x}
        xform.T().y = {y}
        xform.T().z = {z}
        
        control.SetValue(t_end, xform)
        out = "Keyframe set"
    else:
        out = "No Transform control"
else:
    out = "Prop not found"
"""
    res = post("run_python", {"code": code})
    if res and res.get("ok"):
        print(f"Result: {res['locals'].get('out')}")
    else:
        print("Failed to animate target (Server might not support run_python yet).")

def main():
    if len(sys.argv) < 4:
        print("Usage: python animate_md_target.py <x> <y> <z>")
        return

    x, y, z = sys.argv[1], sys.argv[2], sys.argv[3]
    
    # 1. Animate the target
    animate_target(x, y, z)
    
    # 2. Start MD to let actor follow
    print("Starting Motion Director...")
    res = post("md_action", {"command": "start", "record": True})
    print("MD Start:", res)
    
    # 3. Wait for duration
    print("Waiting for motion...")
    time.sleep(5) 
    
    # 4. Stop MD
    print("Stopping Motion Director...")
    res = post("md_action", {"command": "stop"})
    print("MD Stop:", res)

if __name__ == "__main__":
    main()
