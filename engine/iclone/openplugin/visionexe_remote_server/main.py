import os
import sys
from pathlib import Path

rl_plugin_info = {"ap": "iClone", "ap_version": "8.0"}


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


def main():
    _add_repo_root()
    from engine.iclone.iclone_remote_server import main as run_server

    run_server()


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
