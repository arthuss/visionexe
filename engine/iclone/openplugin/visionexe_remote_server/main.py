import os
import sys
from pathlib import Path

rl_plugin_info = {"ap": "iClone", "ap_version": "8.0"}

MENU_NAME = "visionexe_menu"
MENU_LABEL = "VisionExe"
_ACTIONS = []


def _add_repo_root():
    root = os.environ.get("VISIONEXE_ROOT")
    if root:
        sys.path.insert(0, root)
        return
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "engine" / "iclone").exists():
            sys.path.insert(0, str(parent))
            return
    raise RuntimeError("VISIONEXE_ROOT not set and repo root not found.")


def _load_qt():
    try:
        from PySide6 import QtWidgets
        from shiboken6 import wrapInstance
        return QtWidgets, wrapInstance
    except ImportError:
        try:
            from PySide2 import QtWidgets
            from PySide2.shiboken2 import wrapInstance
            return QtWidgets, wrapInstance
        except ImportError:
            return None, None


def _get_menu():
    import RLPy

    QtWidgets, wrapInstance = _load_qt()
    if not QtWidgets:
        return None

    main_window = wrapInstance(int(RLPy.RUi.GetMainWindow()), QtWidgets.QMainWindow)
    menu = main_window.menuBar().findChild(QtWidgets.QMenu, MENU_NAME)
    if menu is None:
        menu = wrapInstance(int(RLPy.RUi.AddMenu(MENU_LABEL, RLPy.EMenu_Plugins)), QtWidgets.QMenu)
        menu.setObjectName(MENU_NAME)
    return menu


def _add_menu_action(label, object_name, handler):
    QtWidgets, _ = _load_qt()
    if not QtWidgets:
        return None

    menu = _get_menu()
    if menu is None:
        return None

    existing = menu.findChild(QtWidgets.QAction, object_name)
    if existing:
        return existing
    action = menu.addAction(label)
    action.setObjectName(object_name)
    action.triggered.connect(handler)
    _ACTIONS.append(action)
    return action


def main():
    _add_repo_root()
    from engine.iclone.iclone_remote_server import main as run_server

    run_server()


def initialize_plugin():
    try:
        _add_menu_action("Start VisionExe Remote Server", "visionexe_remote_server_action", run_script)
    except Exception as exc:  # pylint: disable=broad-except
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