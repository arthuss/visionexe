import json
import os
import time
from pathlib import Path

try:
    from PySide2 import QtCore, QtWidgets
except ImportError:
    from PySide6 import QtCore, QtWidgets

import RLPy

# Watch this file for commands
WATCH_FILE = Path(r"C:\Users\sasch\visionexe\engine\character_creator\cc_command.json")
RESPONSE_FILE = Path(r"C:\Users\sasch\visionexe\engine\character_creator\cc_response.json")
UI_DUMP_FILE = Path(r"C:\Users\sasch\visionexe\engine\character_creator\cc_ui_dump.json")

class FileWatcher(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.check_file)
        self.timer.start(500) # Check every 500ms
        print(f"[CC Watcher] Watching {WATCH_FILE}")

    def check_file(self):
        if not WATCH_FILE.exists():
            return
        
        try:
            text = WATCH_FILE.read_text(encoding="utf-8")
            try:
                WATCH_FILE.unlink()
            except PermissionError:
                return

            data = json.loads(text)
            action = data.get("action")
            print(f"[CC Watcher] Received action: {action}")
            
            result = {"ok": False, "error": "Unknown action"}
            
            if action == "save_character":
                result = self.save_character(data.get("payload"))
            elif action == "inspect_ui":
                result = self.inspect_ui()
            
            RESPONSE_FILE.write_text(json.dumps(result), encoding="utf-8")
            
        except Exception as e:
            print(f"[CC Watcher] Error: {e}")
            RESPONSE_FILE.write_text(json.dumps({"ok": False, "error": str(e)}), encoding="utf-8")

    def save_character(self, data):
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

    def inspect_ui(self):
        app = QtWidgets.QApplication.instance()
        widgets = []
        for w in app.allWidgets():
            if not w.isVisible(): continue
            name = w.objectName()
            title = w.windowTitle() if hasattr(w, "windowTitle") else ""
            cls = w.metaObject().className()
            
            # Simple filter to keep dump small
            if "Headshot" in name or "Headshot" in title or "Headshot" in cls:
                widgets.append({
                    "class": cls,
                    "name": name,
                    "title": title,
                    "rect": [w.x(), w.y(), w.width(), w.height()]
                })
                # Dump children too if it's a container
                for child in w.findChildren(QtWidgets.QWidget):
                     c_name = child.objectName()
                     c_cls = child.metaObject().className()
                     c_text = child.text() if hasattr(child, "text") else ""
                     if c_text or c_name:
                         widgets.append({
                            "parent": name,
                            "class": c_cls,
                            "name": c_name,
                            "text": c_text
                         })

        UI_DUMP_FILE.write_text(json.dumps(widgets, indent=2), encoding="utf-8")
        return {"ok": True, "count": len(widgets), "path": str(UI_DUMP_FILE)}

_WATCHER = None

def main():
    global _WATCHER
    if not _WATCHER:
        _WATCHER = FileWatcher()
        # import RLPy
        # RLPy.RUi.ShowMessageBox("CC File Watcher Started", "Info", RLPy.EMsgButton_Ok)

if __name__ == "__main__":
    main()