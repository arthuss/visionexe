import os
import sys
from pathlib import Path

rl_plugin_info = {"ap": "iClone", "ap_version": "8.0"}

MENU_NAME = "visionexe_menu"
MENU_LABEL = "VisionExe"
_ACTIONS = []
_QT_MISSING_NOTIFIED = False

DEBUG_LOG_PATH = r"C:\Users\sasch\visionexe\iclone_debug.txt"

def _log(msg):
    try:
        with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"[RemoteServer] {msg}\n")
    except:
        pass

def _add_repo_root():
    _log("Adding repo root...")
    root = os.environ.get("VISIONEXE_ROOT")
    if root:
        sys.path.insert(0, root)
        _log(f"Added VISIONEXE_ROOT: {root}")
        return
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "engine" / "iclone").exists():
            sys.path.insert(0, str(parent))
            _log(f"Found and added repo root: {parent}")
            return
    _log("RuntimeError: VISIONEXE_ROOT not set and repo root not found.")
    raise RuntimeError("VISIONEXE_ROOT not set and repo root not found.")


def _load_qt():
    _log("Loading Qt...")
    _log(f"sys.path: {sys.path}")
    
    # Try PySide6
    try:
        from PySide6 import QtWidgets
        _log("PySide6.QtWidgets imported")
        try:
            from shiboken6 import wrapInstance
            _log("shiboken6.wrapInstance imported")
            return QtWidgets, wrapInstance
        except ImportError as e:
            _log(f"shiboken6 import failed: {e}")
    except ImportError as e:
        _log(f"PySide6.QtWidgets import failed: {e}")

    # Fallback to PySide2
    _log("Trying PySide2 fallback...")
    try:
        from PySide2 import QtWidgets
        _log("PySide2.QtWidgets imported")
        try:
            from shiboken2 import wrapInstance
            _log("shiboken2.wrapInstance imported")
            return QtWidgets, wrapInstance
        except ImportError as e:
             _log(f"shiboken2 import failed: {e}")
             return None, None
    except ImportError as e:
        _log(f"PySide2 import failed: {e}")
        return None, None


def _get_menu():
    import RLPy
    _log("Getting menu...")

    QtWidgets, wrapInstance = _load_qt()
    if not QtWidgets:
        _log("Qt load failed in _get_menu")
        return None

    try:
        mw_ptr = RLPy.RUi.GetMainWindow()
        _log(f"Main window pointer: {mw_ptr}")
        main_window = wrapInstance(int(mw_ptr), QtWidgets.QMainWindow)
        
        menu = main_window.menuBar().findChild(QtWidgets.QMenu, MENU_NAME)
        if menu:
             _log("Found existing menu")
        
        if menu is None:
            _log("Creating new menu via RLPy.RUi.AddMenu...")
            # Note: AddMenu returns an int pointer
            new_menu_ptr = RLPy.RUi.AddMenu(MENU_LABEL, RLPy.EMenu_Plugins)
            _log(f"New menu pointer: {new_menu_ptr}")
            menu = wrapInstance(int(new_menu_ptr), QtWidgets.QMenu)
            menu.setObjectName(MENU_NAME)
            _log("Menu object created and named")
            
        return menu
    except Exception as e:
        _log(f"Error in _get_menu: {e}")
        import traceback
        _log(traceback.format_exc())
        return None


def _add_menu_action(label, object_name, handler):
    _log(f"Adding menu action: {label}")
    QtWidgets, _ = _load_qt()
    if not QtWidgets:
        _log("Qt missing in _add_menu_action")
        return None

    menu = _get_menu()
    if menu is None:
        _log("Menu is None in _add_menu_action")
        return None

    try:
        existing = menu.findChild(QtWidgets.QAction, object_name)
        if existing:
            _log("Action already exists")
            return existing
        action = menu.addAction(label)
        action.setObjectName(object_name)
        action.triggered.connect(handler)
        _ACTIONS.append(action)
        _log("Action added successfully")
        return action
    except Exception as e:
        _log(f"Error adding action: {e}")
        return None


def main():
    _log("Main called")
    _add_repo_root()
    from engine.iclone.iclone_remote_server import main as run_server

    run_server()


def initialize_plugin():
    _log("initialize_plugin called")
    try:
        _add_menu_action("Start VisionExe Remote Server", "visionexe_remote_server_action", run_script)
    except Exception as exc:  # pylint: disable=broad-except
        _log(f"Exception in initialize_plugin: {exc}")
        try:
            import RLPy

            RLPy.RUi.ShowMessageBox(str(exc), "VisionExe Remote Server", RLPy.EMsgButton_Ok)
        except Exception:
            print(f"[VisionExe Remote Server] {exc}")


def run_script():
    try:
        main()
    except Exception as exc:  # pylint: disable=broad-except
        try:
            import RLPy

            RLPy.RUi.ShowMessageBox(str(exc), "VisionExe Remote Server", RLPy.EMsgButton_Ok)
        except Exception:
            print(f"[VisionExe Remote Server] {exc}")


if __name__ == "__main__":
    main()