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
        self.processing = False
        print(f"[CC Watcher] Watching {WATCH_FILE}")

    def check_file(self):
        if self.processing:
            return
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
            payload = data.get("payload") or {}
            self.processing = True
            self.timer.stop()
            try:
                if action == "save_character":
                    result = self.save_character(payload)
                elif action == "headshot_from_photo":
                    result = self.headshot_from_photo(payload)
                elif action == "inspect_ui":
                    result = self.inspect_ui()
                RESPONSE_FILE.write_text(json.dumps(result), encoding="utf-8")
            finally:
                self.processing = False
                self.timer.start(500)
            
        except Exception as e:
            print(f"[CC Watcher] Error: {e}")
            RESPONSE_FILE.write_text(json.dumps({"ok": False, "error": str(e)}), encoding="utf-8")

    def save_character(self, data):
        avatar_name = data.get("name")
        if not avatar_name:
            return {"ok": False, "error": "Missing name."}
        custom_root = r"C:\Users\Public\Documents\Reallusion\Reallusion Custom\Character Creator 4\Custom"
        subfolder = data.get("folder", "Project/Avatar")
        prefer_last = bool(data.get("prefer_last"))
        
        save_dir = Path(custom_root) / subfolder
        save_dir.mkdir(parents=True, exist_ok=True)
        
        final_path = save_dir / f"{avatar_name}.ccAvatar"
        
        avatar = RLPy.RScene.GetSelectedObject()
        avatars = list(RLPy.RScene.GetAvatars())
        if prefer_last and avatars:
            avatar = avatars[-1]
        if not avatar or not isinstance(avatar, RLPy.RAvatar):
            if avatars:
                avatar = avatars[0]
            else:
                return {"ok": False, "error": "No avatar."}

        save_setting = RLPy.RSaveFileSetting()
        save_setting.SetSaveType(RLPy.ESaveFileType_Avatar)
        
        result = RLPy.RFileIO.SaveFile(avatar, save_setting, str(final_path))
        
        if hasattr(result, "IsError") and result.IsError():
             return {"ok": False, "error": "SaveFile failed."}
        
        return {"ok": True, "path": str(final_path)}

    def headshot_from_photo(self, data):
        photo_path = data.get("photo_path")
        if not photo_path:
            return {"ok": False, "error": "Missing photo_path."}
        if not Path(photo_path).exists():
            return {"ok": False, "error": f"Photo not found: {photo_path}"}

        mode = str(data.get("mode", "auto")).lower()
        body_type = str(data.get("body_type", "current")).lower()

        mode_map = {
            "auto": RLPy.EHSMode_Auto,
            "pro": RLPy.EHSMode_Pro,
        }
        body_map = {
            "male": RLPy.EHSBodyType_Male,
            "female": RLPy.EHSBodyType_Female,
            "baby": RLPy.EHSBodyType_Baby,
            "neutral": RLPy.EHSBodyType_Neutral,
            "current": RLPy.EHSBodyType_Current,
        }

        option = RLPy.RHeadshotOption()
        option.eBodyType = body_map.get(body_type, RLPy.EHSBodyType_Current)
        if body_type == "baby":
            option.bBaby = True

        result = RLPy.RHeadshot.CreateHeadFromPhoto(photo_path, mode_map.get(mode, RLPy.EHSMode_Auto), option)

        response = {
            "ok": bool(result),
            "result_type": str(type(result)),
            "photo_path": photo_path,
            "mode": mode,
            "body_type": body_type,
        }

        save_name = data.get("save_name")
        if save_name:
            folder = data.get("folder", "Project/Avatar")
            save_result = self.save_character({
                "name": save_name,
                "folder": folder,
                "prefer_last": True,
            })
            response["save"] = save_result
            response["ok"] = response["ok"] and save_result.get("ok")

        return response

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
