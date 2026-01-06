import sys
import traceback
from pathlib import Path

import RLPy
from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader
from shiboken2 import wrapInstance, isValid

# iClone Plugin Metadata
rl_plugin_info = {
    "ap": "iClone",
    "ap_version": "8.0"
}

PLUGIN_DIR = Path(__file__).resolve().parent
if str(PLUGIN_DIR) not in sys.path:
    sys.path.insert(0, str(PLUGIN_DIR))

_dialog = None
_status_label = None
_server = None
_thread = None


def _log(msg):
    print(f"[VisionExe Plugin] {msg}")


def _safe_message_box(message, title):
    try:
        RLPy.RUi.ShowMessageBox(title, message, RLPy.EMsgButton_Ok)
    except Exception as exc:
        _log(f"{title}: {message} ({exc})")


def _get_status_label():
    global _status_label, _dialog
    if _status_label is not None:
        try:
            if isValid(_status_label):
                return _status_label
        except Exception:
            _status_label = None
    if _dialog is None:
        return None
    try:
        if not isValid(_dialog):
            _dialog = None
            return None
    except Exception:
        _dialog = None
        return None
    label = _dialog.findChild(QtWidgets.QLabel, "qtStatusLabel")
    if label is not None and isValid(label):
        _status_label = label
        return label
    _status_label = None
    return None


def _set_status(text):
    label = _get_status_label()
    if label is None:
        return
    try:
        label.setText(text)
        label.update()
        QtWidgets.QApplication.processEvents()
    except Exception:
        pass


def _refresh_status():
    try:
        import iclone_remote_server
        running = bool(getattr(iclone_remote_server, "_SERVER_INSTANCE", None))
        _set_status("Status: running" if running else "Status: stopped")
    except Exception:
        pass


def _find_actor_clicked():
    try:
        import iclone_remote_server
        if _dialog is None:
            return
        input_field = _dialog.findChild(QtWidgets.QLineEdit, "qtActorSearchInput")
        if input_field is None:
            _safe_message_box("Actor input field not found.", "VisionExe")
            return
        name = input_field.text().strip()
        if not name:
            _safe_message_box("Enter an actor name first.", "VisionExe")
            return
        roots = iclone_remote_server._get_content_roots(RLPy.ETemplateRootFolder_Character)
        cm_path = iclone_remote_server._find_actor_in_content_manager(
            name,
            include_default=True,
            include_custom=True,
        )
        entry = iclone_remote_server._find_asset_in_index(name, None)
        index_path = entry.get("abs_path") if entry else None
        message = (
            f"Content roots:\nDefault: {roots.get('default')}\nCustom: {roots.get('custom')}\n\n"
            f"CM match: {cm_path or 'None'}\n"
            f"Index match: {index_path or 'None'}"
        )
        _safe_message_box(message, "Actor Lookup")
    except Exception as exc:
        traceback.print_exc()
        _safe_message_box(f"Actor lookup failed:\n{exc}", "VisionExe")


def _scan_content_clicked():
    try:
        import iclone_remote_server
        root_key = iclone_remote_server._resolve_root_key("Character")
        roots = iclone_remote_server._get_content_roots(root_key)
        folders = []
        if roots.get("default"):
            folders.extend(iclone_remote_server._collect_content_folders(roots["default"], max_folders=50))
        if roots.get("custom"):
            folders.extend(iclone_remote_server._collect_content_folders(roots["custom"], max_folders=50))
        files = iclone_remote_server._collect_content_files(folders, max_files=200)
        preview = "\n".join(str(item) for item in files[:10]) if files else "None"
        message = (
            f"Folders: {len(folders)}\nFiles: {len(files)}\n\n"
            f"First files:\n{preview}"
        )
        _safe_message_box(message, "Content Scan")
    except Exception as exc:
        traceback.print_exc()
        _safe_message_box(f"Content scan failed:\n{exc}", "VisionExe")


def _load_actor_path_clicked():
    try:
        if _dialog is None:
            return
        input_field = _dialog.findChild(QtWidgets.QLineEdit, "qtActorPathInput")
        if input_field is None:
            _safe_message_box("Path input field not found.", "VisionExe")
            return
        path = input_field.text().strip()
        if not path:
            _safe_message_box("Enter a path first.", "VisionExe")
            return
        if not Path(path).exists():
            _safe_message_box(f"Path not found:\n{path}", "VisionExe")
            return
        try:
            suffix = Path(path).suffix.lower()
            if suffix in {".iproject", ".ccproject"} and hasattr(RLPy.RFileIO, "LoadFile"):
                RLPy.RFileIO.LoadFile(path)
            else:
                RLPy.RFileIO.LoadObject(path, True)
            _safe_message_box(f"Loaded:\n{path}", "VisionExe")
        except Exception as exc:
            traceback.print_exc()
            _safe_message_box(f"Load failed:\n{exc}", "VisionExe")
    except Exception as exc:
        traceback.print_exc()
        _safe_message_box(f"Load failed:\n{exc}", "VisionExe")


def _load_ui():
    ui_path = PLUGIN_DIR / "mainWindow.ui"
    if not ui_path.exists():
        _safe_message_box(f"Missing UI file:\n{ui_path}", "VisionExe")
        return None
    ui_file = QFile(str(ui_path))
    if not ui_file.open(QFile.ReadOnly):
        _safe_message_box(f"Unable to open UI file:\n{ui_path}", "VisionExe")
        return None
    ui_widget = QUiLoader().load(ui_file)
    ui_file.close()
    return ui_widget


def _on_dialog_destroyed():
    global _dialog, _status_label
    _dialog = None
    _status_label = None


def _create_dialog():
    global _status_label
    main_widget = wrapInstance(int(RLPy.RUi.GetMainWindow()), QtWidgets.QWidget)
    dlg = QtWidgets.QDialog(main_widget)
    dlg.setAttribute(QtCore.Qt.WA_DeleteOnClose, False)
    dlg.destroyed.connect(_on_dialog_destroyed)

    ui_widget = _load_ui()
    if ui_widget is None:
        return None

    layout = QtWidgets.QVBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(ui_widget)
    dlg.setLayout(layout)
    dlg.setWindowTitle("VisionExe")
    dlg.resize(ui_widget.size().width(), ui_widget.size().height())
    dlg.setMinimumSize(ui_widget.size())
    dlg.setMaximumSize(ui_widget.size())

    start_btn = ui_widget.findChild(QtWidgets.QPushButton, "qtStartServerBtn")
    stop_btn = ui_widget.findChild(QtWidgets.QPushButton, "qtStopServerBtn")
    close_btn = ui_widget.findChild(QtWidgets.QPushButton, "qtCloseBtn")
    find_btn = ui_widget.findChild(QtWidgets.QPushButton, "qtFindActorBtn")
    scan_btn = ui_widget.findChild(QtWidgets.QPushButton, "qtScanContentBtn")
    load_path_btn = ui_widget.findChild(QtWidgets.QPushButton, "qtLoadActorPathBtn")
    _status_label = ui_widget.findChild(QtWidgets.QLabel, "qtStatusLabel")

    if start_btn:
        start_btn.clicked.connect(_start_server_clicked)
    if stop_btn:
        stop_btn.clicked.connect(_stop_server_clicked)
    if close_btn:
        close_btn.clicked.connect(dlg.close)
    if find_btn:
        find_btn.clicked.connect(_find_actor_clicked)
    if scan_btn:
        scan_btn.clicked.connect(_scan_content_clicked)
    if load_path_btn:
        load_path_btn.clicked.connect(_load_actor_path_clicked)

    _set_status("Status: stopped")
    return dlg


def show_dialog():
    global _dialog
    if _dialog is None:
        _dialog = _create_dialog()
        if _dialog is None:
            return
    if _dialog.isVisible():
        _dialog.hide()
    else:
        _dialog.show()
        _refresh_status()


def _start_server_clicked():
    global _server, _thread
    try:
        import iclone_remote_server
        _server, _thread = iclone_remote_server.main()
        if _server:
            _refresh_status()
            _log("Server started.")
        else:
            _set_status("Status: failed")
    except Exception as exc:
        _set_status("Status: failed")
        traceback.print_exc()
        _safe_message_box(f"Failed to start server:\n{exc}", "VisionExe")


def _stop_server_clicked():
    global _server, _thread
    try:
        import iclone_remote_server
        stopped = iclone_remote_server.stop_server()
        if stopped:
            _server = None
            _thread = None
            _refresh_status()
        else:
            _set_status("Status: not running")
    except Exception as exc:
        _set_status("Status: failed")
        traceback.print_exc()
        _safe_message_box(f"Failed to stop server:\n{exc}", "VisionExe")


def initialize_plugin():
    try:
        main_window_ptr = RLPy.RUi.GetMainWindow()
        if not main_window_ptr:
            _log("Main window not found.")
            return

        main_window = wrapInstance(int(main_window_ptr), QtWidgets.QMainWindow)
        menu_bar = main_window.menuBar()

        plugins_menu = None
        for action in menu_bar.actions():
            if "&Plugins" in action.text() or "Plugins" in action.text():
                plugins_menu = action.menu()
                break

        if plugins_menu:
            vision_menu = plugins_menu.addMenu("VisionExe")
        else:
            vision_menu = menu_bar.addMenu("VisionExe")

        open_act = vision_menu.addAction("Open VisionExe Panel")
        open_act.triggered.connect(show_dialog)

        _log("VisionExe plugin initialized.")
    except Exception as exc:
        _log(f"Init failed: {exc}")
        traceback.print_exc()
