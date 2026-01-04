import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Optional

import RLPy

sys.path.append(str(Path(__file__).resolve().parent))
from iclone_config import load_config  # noqa: E402

import content_indexer  # noqa: E402


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8123
DEFAULT_KEY_STEP = 1
DEFAULT_STRENGTH_SCALE = 1.0

EFFECTOR_MAP = {
    "hip": RLPy.EHikEffector_Hip,
    "leftfoot": RLPy.EHikEffector_LeftFoot,
    "rightfoot": RLPy.EHikEffector_RightFoot,
    "lefthand": RLPy.EHikEffector_LeftHand,
    "righthand": RLPy.EHikEffector_RightHand,
    "leftknee": RLPy.EHikEffector_LeftKnee,
    "rightknee": RLPy.EHikEffector_RightKnee,
    "leftelbow": RLPy.EHikEffector_LeftElbow,
    "rightelbow": RLPy.EHikEffector_RightElbow,
    "chestorigin": RLPy.EHikEffector_ChestOrigin,
    "neck": RLPy.EHikEffector_Neck,
    "lefttoe": RLPy.EHikEffector_LeftToe,
    "righttoe": RLPy.EHikEffector_RightToe,
    "leftshoulder": RLPy.EHikEffector_LeftShoulder,
    "rightshoulder": RLPy.EHikEffector_RightShoulder,
    "head": RLPy.EHikEffector_Head,
    "lefthip": RLPy.EHikEffector_LeftHip,
    "righthip": RLPy.EHikEffector_RightHip,
}

TRANSITION_TYPE_MAP = {
    "none": RLPy.ETransitionType__None,
    "linear": RLPy.ETransitionType_Linear,
    "step": RLPy.ETransitionType_Step,
    "ease_out": RLPy.ETransitionType_Ease_Out,
    "ease_in": RLPy.ETransitionType_Ease_In,
    "ease_out_in": RLPy.ETransitionType_Ease_Out_In,
    "ease_in_out": RLPy.ETransitionType_Ease_In_Out,
}


def _to_float(value, default):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _ensure_dir(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)


def _time_from_seconds(seconds: float) -> RLPy.RTime:
    fps = RLPy.RGlobal.GetFps()
    return fps.FrameTimeFromSecond(seconds)


def _resolve_effector(name):
    if name is None:
        return None
    if isinstance(name, int):
        return name
    key = str(name).strip().lower().replace(" ", "").replace("-", "").replace("_", "")
    return EFFECTOR_MAP.get(key)


def _get_avatars():
    return list(RLPy.RScene.GetAvatars())


def _find_avatar(name: Optional[str]):
    avatars = _get_avatars()
    if not avatars:
        return None
    if name:
        for avatar in avatars:
            if avatar.GetName() == name:
                return avatar
    return avatars[0]


def _list_avatar_names():
    return [avatar.GetName() for avatar in _get_avatars()]


def _get_cameras():
    return list(RLPy.RScene.GetCameras())


def _find_camera(name: Optional[str]):
    if name:
        for camera in _get_cameras():
            if camera.GetName() == name:
                return camera
    current = RLPy.RScene.GetCurrentCamera()
    if current:
        return current
    cameras = _get_cameras()
    return cameras[0] if cameras else None


def _list_camera_names():
    return [camera.GetName() for camera in _get_cameras()]


def _load_mapping(path: Optional[str]):
    if not path:
        return {}
    mapping_path = Path(path)
    if not mapping_path.exists():
        return {}
    data = json.loads(mapping_path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "mapping" in data and isinstance(data["mapping"], dict):
        return data["mapping"]
    if isinstance(data, dict):
        return data
    return {}


def _apply_a2f_json(
    avatar,
    json_path: str,
    mapping_path: Optional[str],
    key_step: int,
    strength_scale: float,
    start_seconds: Optional[float],
    clip_name: Optional[str],
    use_mocap_order: bool,
):
    path = Path(json_path)
    if not path.exists():
        return {"ok": False, "error": f"A2F json not found: {json_path}"}

    payload = json.loads(path.read_text(encoding="utf-8"))
    export_fps = _to_float(payload.get("exportFps"), 60.0)
    facs_names = payload.get("facsNames") or []
    weight_mat = payload.get("weightMat") or []

    if not facs_names or not weight_mat:
        return {"ok": False, "error": "A2F json missing facsNames/weightMat."}

    face_component = avatar.GetFaceComponent()
    if face_component is None:
        return {"ok": False, "error": "Avatar has no face component."}

    mapping = _load_mapping(mapping_path)
    expression_names = (
        face_component.GetExpressionNames("", True) if use_mocap_order else face_component.GetExpressionNames("")
    )
    expression_name_set = set(expression_names)
    mapped_names = []
    mapped_indices = []
    missing = []
    for idx, name in enumerate(facs_names):
        target = mapping.get(name, name)
        if target in expression_name_set:
            mapped_names.append(target)
            mapped_indices.append(idx)
        else:
            missing.append(target)

    if not mapped_names:
        return {"ok": False, "error": "No matching expression names found for A2F data.", "missing": missing}

    key_step = max(1, key_step)
    frame_count = len(weight_mat)
    start_seconds = start_seconds or 0.0
    clip_name = clip_name or f"A2F_{path.stem}"
    clip_seconds = max(0.0, frame_count / export_fps)
    try:
        face_component.AddClip(_time_from_seconds(start_seconds), clip_name, _time_from_seconds(clip_seconds))
    except Exception:
        pass

    applied = 0
    fps = RLPy.RGlobal.GetFps()
    inv_time = RLPy.IndexedFrameTime(key_step, fps)
    face_component.BeginKeyEditing()
    try:
        for frame_idx in range(0, frame_count, key_step):
            weights = weight_mat[frame_idx]
            values = []
            for idx in mapped_indices:
                try:
                    value = float(weights[idx]) * strength_scale
                except (TypeError, ValueError, IndexError):
                    value = 0.0
                values.append(value)

            seconds = start_seconds + (frame_idx / export_fps)
            time = _time_from_seconds(seconds)
            face_component.AddExpressivenessKey(time, 1.0)
            result = face_component.AddExpressionKeys(time, mapped_names, values, inv_time)
            if result.IsError():
                return {"ok": False, "error": "Failed to set expression keys."}
            applied += 1
    finally:
        face_component.EndKeyEditing()

    return {
        "ok": True,
        "applied_frames": applied,
        "export_fps": export_fps,
        "clip_name": clip_name,
        "missing": missing,
        "expression_set_uid": face_component.GetExpressionSetUid(),
        "use_mocap_order": use_mocap_order,
    }


def _apply_ik_effector_keys(avatar, effector_name, keys, bake_fk_to_ik, bake_all):
    skeleton = avatar.GetSkeletonComponent()
    if skeleton is None:
        return {"ok": False, "error": "Avatar has no skeleton component."}

    effector_enum = _resolve_effector(effector_name)
    if effector_enum is None:
        return {"ok": False, "error": f"Unknown effector: {effector_name}"}

    effector = skeleton.GetEffector(effector_enum)
    if effector is None:
        return {"ok": False, "error": f"Effector not found: {effector_name}"}

    if not keys:
        return {"ok": False, "error": "No effector keys provided."}

    applied = 0
    for entry in keys:
        time_seconds = entry.get("time_seconds")
        if time_seconds is None:
            continue
        scene_time = _time_from_seconds(float(time_seconds))

        clip = skeleton.GetClipByTime(scene_time)
        if clip is None:
            clip = skeleton.AddClip(scene_time)
        if clip is None:
            return {"ok": False, "error": "Failed to create or get motion clip."}

        clip_time = clip.SceneTimeToClipTime(scene_time)
        data_block = clip.GetDataBlock("Layer", effector)
        if data_block is None:
            return {"ok": False, "error": "Failed to get effector datablock."}

        position = entry.get("position") or {}
        for axis, control_name in (
            ("x", "Position/PositionX"),
            ("y", "Position/PositionY"),
            ("z", "Position/PositionZ"),
        ):
            if axis not in position:
                continue
            control = data_block.GetControl(control_name)
            if control is None:
                continue
            control.SetValue(clip_time, float(position[axis]))

        if bake_fk_to_ik:
            skeleton.BakeFkToIk(scene_time, bool(bake_all))

        applied += 1

    return {"ok": True, "applied_keys": applied, "effector": effector_name}


def _vector3_from_dict(data, fallback):
    if not data:
        return fallback
    vec = RLPy.RVector3(fallback.x, fallback.y, fallback.z)
    for axis in ("x", "y", "z"):
        if axis in data:
            setattr(vec, axis, float(data[axis]))
    return vec


def _quat_from_dict(data, fallback):
    if not data:
        return fallback
    quat = RLPy.RQuaternion()
    quat.x = float(data.get("x", fallback.x))
    quat.y = float(data.get("y", fallback.y))
    quat.z = float(data.get("z", fallback.z))
    quat.w = float(data.get("w", fallback.w))
    return quat


def _resolve_transition_type(value):
    if value is None:
        return None
    key = str(value).strip().lower()
    return TRANSITION_TYPE_MAP.get(key)


def _build_dof_data(camera, dof_settings):
    data = camera.GetDOFData() or RLPy.RCameraDofData()
    if "enable" in dof_settings:
        data.SetEnable(bool(dof_settings["enable"]))
    if "focus" in dof_settings:
        data.SetFocus(float(dof_settings["focus"]))
    if "range" in dof_settings:
        data.SetRange(float(dof_settings["range"]))
    if "near_transition" in dof_settings:
        data.SetNearTransitionRegion(float(dof_settings["near_transition"]))
    if "far_transition" in dof_settings:
        data.SetFarTransitionRegion(float(dof_settings["far_transition"]))
    if "near_blur_scale" in dof_settings:
        data.SetNearBlurScale(float(dof_settings["near_blur_scale"]))
    if "far_blur_scale" in dof_settings:
        data.SetFarBlurScale(float(dof_settings["far_blur_scale"]))
    if "min_blend_distance" in dof_settings:
        data.SetMinBlendDistance(float(dof_settings["min_blend_distance"]))
    if "center_color_weight" in dof_settings:
        data.SetCenterColorWeight(float(dof_settings["center_color_weight"]))
    if "edge_decay_power" in dof_settings:
        data.SetEdgeDecayPower(float(dof_settings["edge_decay_power"]))
    return data


def _get_camera_info(camera):
    time = RLPy.RGlobal.GetTime()
    transform = camera.WorldTransform()
    pos = transform.T()
    rot = transform.R()
    scale = transform.S()

    dof = camera.GetDOFData()
    dof_info = {}
    if dof:
        dof_info = {
            "enable": dof.GetEnable(),
            "focus": dof.GetFocus(),
            "range": dof.GetRange(),
            "near_transition": dof.GetNearTransitionRegion(),
            "far_transition": dof.GetFarTransitionRegion(),
            "near_blur_scale": dof.GetNearBlurScale(),
            "far_blur_scale": dof.GetFarBlurScale(),
            "min_blend_distance": dof.GetMinBlendDistance(),
            "center_color_weight": dof.GetCenterColorWeight(),
            "edge_decay_power": dof.GetEdgeDecayPower(),
        }

    # Aperture
    aperture_width = 0.0
    aperture_height = 0.0
    try:
        # Some versions return tuple, some might modify args if possible (unlikely in Python)
        # Based on example: result = GetAperture(w, h); print(result[0])...
        res = camera.GetAperture(0.0, 0.0)
        if isinstance(res, (list, tuple)) and len(res) >= 3:
            aperture_width = res[1]
            aperture_height = res[2]
    except Exception:
        pass

    return {
        "name": camera.GetName(),
        "transform": {
            "position": {"x": pos.x, "y": pos.y, "z": pos.z},
            "rotation": {"x": rot.x, "y": rot.y, "z": rot.z, "w": rot.w},
            "scale": {"x": scale.x, "y": scale.y, "z": scale.z},
        },
        "focal_length": camera.GetFocalLength(time),
        "angle_of_view": camera.GetAngleOfView(time),
        "near_plane": camera.GetNearClippingPlane(),
        "far_plane": camera.GetFarClippingPlane(),
        "dof": dof_info,
        "fit_fov_type": camera.GetFitFovType(),
        "fit_render_region_type": camera.GetFitRenderRegionType(),
        "aperture": {"width": aperture_width, "height": aperture_height},
    }


def _set_camera_params(camera, data):
    time = RLPy.RGlobal.GetTime()
    
    if "near_plane" in data:
        camera.SetNearClippingPlane(float(data["near_plane"]))
    
    if "far_plane" in data:
        # Note: Doc says SetFarClippingPlane(nFarPlane), Example says (time, nFarPlane).
        # We try both or stick to standard if non-animated. 
        # Usually clipping planes aren't keyed per frame in basic usage.
        try:
            camera.SetFarClippingPlane(float(data["far_plane"]))
        except TypeError:
            camera.SetFarClippingPlane(time, float(data["far_plane"]))

    if "focal_length" in data:
        camera.SetFocalLength(time, float(data["focal_length"]))

    dof_settings = data.get("dof")
    if isinstance(dof_settings, dict):
        dof_data = _build_dof_data(camera, dof_settings)
        # AddDofKey is for animation. To set static/current state, we might need a different approach 
        # or just AddKey at current time.
        # The doc shows AddDofKey. There isn't a simple "SetDOFData" on the camera itself 
        # other than AddDofKey.
        key = RLPy.RKey()
        key.SetTime(time)
        camera.AddDofKey(key, dof_data)

    camera.Update()
    return {"ok": True}


def _apply_camera_keys(camera, keys):
    if not keys:
        return {"ok": False, "error": "No camera keys provided."}

    control = camera.GetControl("Transform")
    if control is None:
        return {"ok": False, "error": "Camera has no Transform control."}

    applied = 0
    for entry in keys:
        time_seconds = entry.get("time_seconds")
        if time_seconds is None:
            continue
        time = _time_from_seconds(float(time_seconds))

        base = camera.WorldTransform()
        transform_data = entry.get("transform") or {}
        scale = _vector3_from_dict(transform_data.get("scale"), base.S())
        rotation = _quat_from_dict(transform_data.get("rotation"), base.R())
        translation = _vector3_from_dict(
            transform_data.get("translation") or transform_data.get("position"),
            base.T(),
        )
        transform = RLPy.RTransform(scale, rotation, translation)
        control.SetValue(time, transform)

        if "focal_length" in entry:
            camera.SetFocalLength(time, float(entry["focal_length"]))

        dof = entry.get("dof")
        if isinstance(dof, dict):
            dof_data = _build_dof_data(camera, dof)
            dof_key = RLPy.RKey()
            dof_key.SetTime(time)
            transition_type = _resolve_transition_type(dof.get("transition_type"))
            if transition_type is not None:
                dof_key.SetTransitionType(transition_type)
            if "transition_strength" in dof:
                dof_key.SetTransitionStrength(float(dof["transition_strength"]))
            camera.AddDofKey(dof_key, dof_data)

        applied += 1

    camera.Update()
    return {"ok": True, "applied_keys": applied, "camera": camera.GetName()}


def _save_italk(avatar, output_path: str, start_seconds: Optional[float], end_seconds: Optional[float]):
    path = Path(output_path)
    _ensure_dir(path)

    save_setting = RLPy.RSaveFileSetting()
    save_setting.SetSaveType(RLPy.ESaveFileType_Talk)

    if start_seconds is None:
        start_time = RLPy.RGlobal.GetStartTime()
    else:
        start_time = _time_from_seconds(start_seconds)
    if end_seconds is None:
        end_time = RLPy.RGlobal.GetEndTime()
    else:
        end_time = _time_from_seconds(end_seconds)
    save_setting.SetSaveRange(start_time, end_time)

    facial_option = RLPy.RSaveFacialAnimationOption()
    facial_option.SetFlag(RLPy.ESaveFacialAnimationOption_All)
    save_setting.SetSaveFileOption(facial_option)

    result = RLPy.RFileIO.SaveFile(avatar, save_setting, str(path))
    if hasattr(result, "IsError") and result.IsError():
        return {"ok": False, "error": "SaveFile failed."}
    return {"ok": True, "path": str(path)}


def _load_vocal(avatar, audio_path: str, start_seconds: Optional[float], clip_name: Optional[str]):
    path = Path(audio_path)
    if not path.exists():
        return {"ok": False, "error": f"Audio file not found: {audio_path}"}

    viseme_component = avatar.GetVisemeComponent()
    if viseme_component is None:
        return {"ok": False, "error": "Avatar has no viseme component."}

    if start_seconds is None:
        start_time = RLPy.RGlobal.GetStartTime()
    else:
        start_time = _time_from_seconds(start_seconds)

    clip_name = clip_name or path.stem
    attempts = [
        (str(path),),
        (str(path), clip_name),
        (str(path), start_time),
        (str(path), start_time, clip_name),
    ]

    last_error = None
    for args in attempts:
        try:
            result = viseme_component.LoadVocal(*args)
            if hasattr(result, "IsError") and result.IsError():
                last_error = "LoadVocal returned error."
                continue
            return {"ok": True, "clip_name": clip_name}
        except Exception as exc:  # pylint: disable=broad-except
            last_error = str(exc)

    return {"ok": False, "error": last_error or "LoadVocal failed."}


class ICloneRemoteHandler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, payload: dict):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length).decode("utf-8") if length else "{}"
            payload = json.loads(body)
        except json.JSONDecodeError:
            return self._send_json(400, {"ok": False, "error": "Invalid JSON payload."})

        action = payload.get("action")
        data = payload.get("payload") or {}

        if action == "ping":
            return self._send_json(200, {"ok": True, "message": "pong"})

        if action == "list_avatars":
            return self._send_json(200, {"ok": True, "avatars": _list_avatar_names()})

        if action == "list_cameras":
            return self._send_json(200, {"ok": True, "cameras": _list_camera_names()})

        if action == "select_avatar":
            avatar = _find_avatar(data.get("name"))
            if not avatar:
                return self._send_json(404, {"ok": False, "error": "No avatar found."})
            RLPy.RScene.SelectObject(avatar)
            return self._send_json(200, {"ok": True, "selected": avatar.GetName()})

        if action == "select_camera":
            camera = _find_camera(data.get("name"))
            if not camera:
                return self._send_json(404, {"ok": False, "error": "No camera found."})
            RLPy.RScene.SetCurrentCamera(camera)
            return self._send_json(200, {"ok": True, "selected": camera.GetName()})

        if action == "load_asset":
            asset_path = data.get("path")
            if not asset_path:
                return self._send_json(400, {"ok": False, "error": "Missing asset path."})
            RLPy.RFileIO.LoadObject(asset_path, True)
            return self._send_json(200, {"ok": True, "path": asset_path})

        if action == "apply_a2f_json":
            avatar = _find_avatar(data.get("avatar_name"))
            if not avatar:
                return self._send_json(404, {"ok": False, "error": "No avatar found."})
            json_path = data.get("path")
            if not json_path:
                return self._send_json(400, {"ok": False, "error": "Missing A2F json path."})
            key_step = _to_int(data.get("key_step"), DEFAULT_KEY_STEP)
            strength_scale = _to_float(data.get("strength_scale"), DEFAULT_STRENGTH_SCALE)
            mapping_path = data.get("mapping_path")
            start_seconds = data.get("start_seconds")
            clip_name = data.get("clip_name")
            use_mocap_order = bool(data.get("use_mocap_order"))
            result = _apply_a2f_json(
                avatar,
                json_path,
                mapping_path,
                key_step,
                strength_scale,
                _to_float(start_seconds, None) if start_seconds is not None else None,
                clip_name,
                use_mocap_order,
            )
            status = 200 if result.get("ok") else 400
            return self._send_json(status, result)

        if action == "save_italk":
            avatar = _find_avatar(data.get("avatar_name"))
            if not avatar:
                return self._send_json(404, {"ok": False, "error": "No avatar found."})
            output_path = data.get("output_path")
            if not output_path:
                return self._send_json(400, {"ok": False, "error": "Missing output_path."})
            start_seconds = data.get("start_seconds")
            end_seconds = data.get("end_seconds")
            result = _save_italk(
                avatar,
                output_path,
                _to_float(start_seconds, None) if start_seconds is not None else None,
                _to_float(end_seconds, None) if end_seconds is not None else None,
            )
            status = 200 if result.get("ok") else 400
            return self._send_json(status, result)

        if action == "load_vocal":
            avatar = _find_avatar(data.get("avatar_name"))
            if not avatar:
                return self._send_json(404, {"ok": False, "error": "No avatar found."})
            audio_path = data.get("audio_path")
            if not audio_path:
                return self._send_json(400, {"ok": False, "error": "Missing audio_path."})
            start_seconds = data.get("start_seconds")
            clip_name = data.get("clip_name")
            result = _load_vocal(
                avatar,
                audio_path,
                _to_float(start_seconds, None) if start_seconds is not None else None,
                clip_name,
            )
            status = 200 if result.get("ok") else 400
            return self._send_json(status, result)

        if action == "apply_ik_effector_keys":
            avatar = _find_avatar(data.get("avatar_name"))
            if not avatar:
                return self._send_json(404, {"ok": False, "error": "No avatar found."})
            effector = data.get("effector")
            keys = data.get("keys") or []
            bake_fk_to_ik = bool(data.get("bake_fk_to_ik"))
            bake_all = bool(data.get("bake_all"))
            result = _apply_ik_effector_keys(avatar, effector, keys, bake_fk_to_ik, bake_all)
            status = 200 if result.get("ok") else 400
            return self._send_json(status, result)

        if action == "apply_camera_keys":
            camera = _find_camera(data.get("camera_name"))
            if not camera:
                return self._send_json(404, {"ok": False, "error": "No camera found."})
            keys = data.get("keys") or []
            result = _apply_camera_keys(camera, keys)
            status = 200 if result.get("ok") else 400
            return self._send_json(status, result)

        if action == "get_camera_info":
            camera = _find_camera(data.get("camera_name"))
            if not camera:
                return self._send_json(404, {"ok": False, "error": "No camera found."})
            info = _get_camera_info(camera)
            return self._send_json(200, {"ok": True, "info": info})

        if action == "set_camera_params":
            camera = _find_camera(data.get("camera_name"))
            if not camera:
                return self._send_json(404, {"ok": False, "error": "No camera found."})
            result = _set_camera_params(camera, data)
            status = 200 if result.get("ok") else 400
            return self._send_json(status, result)

        if action == "list_content":
            # Pass payload directly as config overrides
            result = content_indexer.get_content_index(data)
            status = 200 if result.get("ok") else 400
            return self._send_json(status, result)

        return self._send_json(400, {"ok": False, "error": f"Unknown action: {action}"})

    def log_message(self, format, *args):
        return


def start_server(host=DEFAULT_HOST, port=DEFAULT_PORT):
    server = HTTPServer((host, port), ICloneRemoteHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def main():
    config, config_path = load_config()
    remote_cfg = config.get("remote", {})
    host = os.environ.get("ICLONE_REMOTE_HOST", remote_cfg.get("host", DEFAULT_HOST))
    port = _to_int(os.environ.get("ICLONE_REMOTE_PORT", remote_cfg.get("port", DEFAULT_PORT)), DEFAULT_PORT)
    server, thread = start_server(host, port)
    print(f"[iClone Remote] Listening on http://{host}:{port} (config: {config_path})")
    return server, thread


if __name__ == "__main__":
    main()
