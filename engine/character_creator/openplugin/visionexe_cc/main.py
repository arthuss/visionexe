import os
import sys
import traceback

# Character Creator Plugin Metadata
rl_plugin_info = {
    "ap": "Character Creator",
    "ap_version": "4.0"  # Targeting CC4
}

def _log(msg):
    print(f"[VisionExe CC Loader] {msg}")

def initialize_plugin():
    """
    Safe Loader for Character Creator.
    Registers 'Plugins > VisionExe CC > Start CC Server'.
    Does not auto-start logic to prevent crash loops.
    """
    try:
        from PySide2 import QtWidgets
        import RLPy
        
        main_window_ptr = RLPy.RUi.GetMainWindow()
        if not main_window_ptr:
            _log("Main window not found.")
            return
            
        from shiboken2 import wrapInstance
        main_window = wrapInstance(int(main_window_ptr), QtWidgets.QMainWindow)
        menu_bar = main_window.menuBar()
        
        # Look for standard Plugins menu
        plugins_menu = None
        for action in menu_bar.actions():
            if "&Plugins" in action.text() or "Plugins" in action.text():
                plugins_menu = action.menu()
                break
        
        if plugins_menu:
            vision_menu = plugins_menu.addMenu("VisionExe CC")
        else:
            vision_menu = menu_bar.addMenu("VisionExe CC")
            
        start_act = vision_menu.addAction("Start CC Server")
        start_act.triggered.connect(start_server_clicked)
        
        _log("Ready. Use 'Plugins > VisionExe CC' to start the server.")
        
    except Exception as e:
        _log(f"Init failed: {e}")
        traceback.print_exc()

def start_server_clicked():
    """
    Lazy loads the server code from the engine directory.
    """
    try:
        # Hardcoded dev path - same as iClone
        project_root = r"C:\Users\sasch\visionexe"
        cc_dir = os.path.join(project_root, "engine", "character_creator")
        
        if cc_dir not in sys.path:
            sys.path.insert(0, cc_dir)
            
        import cc_remote_server
        
        import importlib
        importlib.reload(cc_remote_server)
            
        cc_remote_server.main()
        
        import RLPy
        RLPy.RUi.ShowMessageBox("VisionExe CC Server Started.", "Success", RLPy.EMsgButton_Ok)
        _log("CC Server started.")
        
    except Exception as e:
        print(f"[VisionExe CC] Critical Error: {e}")
        traceback.print_exc()
        try:
            import RLPy
            RLPy.RUi.ShowMessageBox(f"Failed to start server:\n{e}", "Error", RLPy.EMsgButton_Ok)
        except:
            pass
