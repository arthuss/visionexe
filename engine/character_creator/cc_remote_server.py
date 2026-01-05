import json
import os
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import RLPy

try:
    from PySide2 import QtCore
except ImportError:
    from PySide6 import QtCore

# Global Queue for Main Thread Polling
COMMAND_QUEUE = []
RESULT_CACHE = {}

class CommandPoller(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.poll)
        self.timer.start(100) # Poll every 100ms

    def poll(self):
        if not COMMAND_QUEUE:
            return
        
        cmd_id, action, data = COMMAND_QUEUE.pop(0)
        
        try:
            if action == "save_character":
                res = self._save_character(data)
            else:
                res = {"ok": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            res = {"ok": False, "error": str(e)}
            
        RESULT_CACHE[cmd_id] = res

    def _save_character(self, data):
        avatar_name = data.get("name")
        custom_root = r"C:\Users\Public\Documents\Reallusion\Reallusion Custom\Character Creator 4\Custom"
        subfolder = data.get("folder", "Project/Avatar")
        save_dir = Path(custom_root) / subfolder
        save_dir.mkdir(parents=True, exist_ok=True)
        final_path = save_dir / f"{avatar_name}.ccAvatar"
        
        avatar = RLPy.RScene.GetSelectedObject()
        if not avatar:
            avatars = list(RLPy.RScene.GetAvatars())
            if avatars: avatar = avatars[0]
            else: return {"ok": False, "error": "No avatar."}

        save_setting = RLPy.RSaveFileSetting()
        save_setting.SetSaveType(RLPy.ESaveFileType_Avatar)
        
        result = RLPy.RFileIO.SaveFile(avatar, save_setting, str(final_path))
        if hasattr(result, "IsError") and result.IsError():
             return {"ok": False, "error": "SaveFile failed."}
        
        return {"ok": True, "path": str(final_path)}

# Global Poller Instance (must be kept alive)
_POLLER = None

class CCRemoteHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8") if length else "{}"
        payload = json.loads(body)
        action = payload.get("action")
        
        if action == "ping":
            self._send_json(200, {"ok": True, "message": "pong (Polling)"})
            return

        # Enqueue
        cmd_id = str(time.time())
        COMMAND_QUEUE.append((cmd_id, action, payload.get("payload")))
        
        # Wait for result (max 60s)
        start = time.time()
        while time.time() - start < 60:
            if cmd_id in RESULT_CACHE:
                res = RESULT_CACHE.pop(cmd_id)
                self._send_json(200 if res.get("ok") else 500, res)
                return
            time.sleep(0.1)
            
        self._send_json(504, {"ok": False, "error": "Timeout polling main thread."})

    def _send_json(self, status, payload):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
        
    def log_message(self, format, *args): return

def main():
    global _POLLER
    # Only create poller if we are in Main Thread (which we are when running via Menu)
    if not _POLLER and QtCore:
        _POLLER = CommandPoller()
        print("[VisionExe CC] Poller started.")
        
    server = HTTPServer(("127.0.0.1", 8124), CCRemoteHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print("[VisionExe CC] Server started on 8124 (Polling Mode).")

if __name__ == "__main__":
    main()
