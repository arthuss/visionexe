import json
import os
import sys
from pathlib import Path

try:
    import RLPy
except ImportError:
    raise SystemExit("RLPy not available. Run this script inside iClone.")

sys.path.append(str(Path(__file__).resolve().parent))
from iclone_config import load_config  # noqa: E402


# Run inside iClone: Plugins > Python > run this script.
# Set env MD_PROBE_RUN=1 to attempt Begin/EndCommand probing.

CONFIG, CONFIG_PATH = load_config()
MD_SETTINGS = CONFIG.get("md_probe", {})


def _env_bool(name, default):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.lower() in ("1", "true", "yes", "on")


RUN_COMMAND_TEST = _env_bool("MD_PROBE_RUN", MD_SETTINGS.get("run_command_test", False))
AVATAR_NAME = os.environ.get("MD_PROBE_AVATAR") or MD_SETTINGS.get("avatar")
OUTPUT_PATH = os.environ.get("MD_PROBE_OUTPUT") or MD_SETTINGS.get("output_path")
START_MD = _env_bool("MD_PROBE_START", MD_SETTINGS.get("start_md", False))


def _vector3_to_dict(vec):
    return {"x": vec.x, "y": vec.y, "z": vec.z}


def _quat_to_dict(quat):
    return {"x": quat.x, "y": quat.y, "z": quat.z, "w": quat.w}


def _transform_to_dict(transform):
    return {
        "scale": _vector3_to_dict(transform.S()),
        "rotation": _quat_to_dict(transform.R()),
        "translation": _vector3_to_dict(transform.T()),
    }


def _safe_call(func, default=None):
    try:
        return func()
    except Exception:
        return default


def _get_avatar(name=None):
    avatars = list(RLPy.RScene.GetAvatars())
    if not avatars:
        return None
    if name:
        for avatar in avatars:
            if avatar.GetName() == name:
                return avatar
    return avatars[0]


def _collect_md_props():
    md_props = list(RLPy.RScene.GetMDProps())
    entries = []
    for prop in md_props:
        tag_ratio_map = {}
        try:
            tag_ratio_map = prop.GetTagRatioMap().asdict()
        except Exception:
            tag_ratio_map = {}
        entry = {
            "name": prop.GetName(),
            "id": prop.GetID(),
            "type": int(prop.GetType()),
            "world_transform": _transform_to_dict(prop.WorldTransform()),
            "tag_ratio_map": tag_ratio_map,
        }
        entry["initial_occupy"] = _safe_call(prop.IsInitialOccupy)
        entry["start_on_entry_dummy"] = _safe_call(prop.IsStartOnEntryDummy)
        entry["active_crowd_interaction"] = _safe_call(prop.IsActiveCrowdInteraction)
        entry["enable_follow_mode"] = _safe_call(prop.IsEnableFollowMode)
        entry["changed_follow_object"] = _safe_call(prop.IsChangedFollowObject)
        entry["distance"] = _safe_call(prop.GetDistance)
        entry["interact_times"] = _safe_call(prop.GetInteractTimes)
        entry["crowd_exit_type"] = _safe_call(prop.GetCrowdExitType)
        entries.append(entry)
    return entries


def _probe_end_command(md, time, md_props, objects):
    md_prop_vec = RLPy.MDPropVector()
    for prop in md_props:
        md_prop_vec.append(prop)

    attempts = [
        ("EndCommand(time, md_prop_vec, objects)", lambda: md.EndCommand(time, md_prop_vec, objects)),
        ("EndCommand(time, md_prop_vec)", lambda: md.EndCommand(time, md_prop_vec)),
        ("EndCommand(time)", lambda: md.EndCommand(time)),
        ("EndCommand()", lambda: md.EndCommand()),
    ]

    results = []
    for label, func in attempts:
        try:
            result = func()
            results.append({"label": label, "ok": True, "result": str(result)})
        except Exception as exc:
            results.append({"label": label, "ok": False, "error": str(exc)})
    return results


def main():
    def _log(message):
        print(message)
        try:
            RLPy.RUi.ShowMessageBox(str(message), "VisionExe MD Probe", RLPy.EMsgButton_Ok)
        except Exception:
            pass

    _log("VisionExe MD Probe started.")

    avatar = _get_avatar(AVATAR_NAME)
    if avatar is None:
        payload = {"ok": False, "error": "No avatar found."}
        _log(json.dumps(payload, indent=2, ensure_ascii=False))
        return

    md = RLPy.RGlobal.GetMotionDirector()
    if START_MD and not md.IsRunning():
        md.Start()

    info = {
        "ok": True,
        "avatar": avatar.GetName(),
        "md_running": md.IsRunning(),
        "md_ready": md.IsReady(),
        "config_path": str(CONFIG_PATH),
        "md_props": _collect_md_props(),
    }

    if RUN_COMMAND_TEST:
        opts = RLPy.RBeginCommandOption()
        opts.bRecord = True
        opts.bAvatar = True
        opts.bPreserveOneKey = False

        time = RLPy.RGlobal.GetTime()
        objects = RLPy.ObjectVector()
        objects.append(avatar)

        try:
            md.BeginCommand(time, objects, opts)
            info["begin_command"] = "ok"
        except Exception as exc:
            info["begin_command"] = f"error: {exc}"

        md_props = list(RLPy.RScene.GetMDProps())
        info["end_command_attempts"] = _probe_end_command(md, time, md_props, objects)

    output = json.dumps(info, indent=2, ensure_ascii=False)
    _log(output)
    if OUTPUT_PATH:
        Path(OUTPUT_PATH).parent.mkdir(parents=True, exist_ok=True)
        Path(OUTPUT_PATH).write_text(output, encoding="utf-8")
        _log(f"MD probe written to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
