rl_plugin_info = {"ap": "iClone", "ap_version": "8.0"}

import json
import math
import os
import sys
import threading
import time
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
_VIEWPORT_CACHE = {"widget": None, "info": None}
DEFAULT_REALLUSION_INDEX_PATH = Path("C:/Users/Public/Documents/Reallusion/reallusion_library_index.json")

# ... (omitting unchanged constants EFFECTOR_MAP, TRANSITION_TYPE_MAP for brevity, assume they are here) ...
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

EULER_ORDER_MAP = {
    "XYZ": RLPy.EEulerOrder_XYZ,
    "XZY": RLPy.EEulerOrder_XZY,
    "YXZ": RLPy.EEulerOrder_YXZ,
    "YZX": RLPy.EEulerOrder_YZX,
    "ZXY": RLPy.EEulerOrder_ZXY,
    "ZYX": RLPy.EEulerOrder_ZYX,
}
DEFAULT_AXIS_ROTATION_PATH = (
    Path(__file__).resolve().parent.parent / "config" / "pose_mappings" / "cc4_axis_rotation.json"
)

# ... (Helper functions from previous version: _to_float, _to_int, _ensure_dir, _safe_call, _load_qt, etc.) ...
# I will include ALL helper functions to ensure the file is complete and not broken.

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


def _safe_call(func, default=None):
    try:
        return func()
    except Exception:
        return default


def _load_qt():
    try:
        from PySide2 import QtCore, QtGui, QtWidgets  # type: ignore
    except ImportError:  # pragma: no cover - fallback if PySide2 missing
        from PySide6 import QtCore, QtGui, QtWidgets  # type: ignore
    try:
        from shiboken2 import wrapInstance  # type: ignore
    except ImportError:  # pragma: no cover - fallback if shiboken2 missing
        from shiboken6 import wrapInstance  # type: ignore
    return QtCore, QtGui, QtWidgets, wrapInstance


def _get_main_window():
    QtCore, QtGui, QtWidgets, wrapInstance = _load_qt()
    ptr = RLPy.RUi.GetMainWindow()
    if not ptr:
        return None
    if isinstance(ptr, QtWidgets.QWidget):
        return ptr
    try:
        return wrapInstance(int(ptr), QtWidgets.QWidget)
    except Exception:
        return None


def _match_viewport_hint(widget, hint):
    if not hint:
        return False
    class_name = widget.metaObject().className()
    object_name = widget.objectName() or ""
    if isinstance(hint, str):
        return hint.lower() in class_name.lower() or hint.lower() in object_name.lower()
    if isinstance(hint, dict):
        if "object_name" in hint and object_name == hint["object_name"]:
            return True
        if "class_name" in hint and class_name == hint["class_name"]:
            return True
        if "contains" in hint:
            token = str(hint["contains"]).lower()
            return token in class_name.lower() or token in object_name.lower()
    return False


def _resolve_viewport_widget(force=False, hint=None):
    if not force and _VIEWPORT_CACHE.get("widget") and _VIEWPORT_CACHE["widget"].isVisible():
        return _VIEWPORT_CACHE["widget"], _VIEWPORT_CACHE["info"]

    QtCore, QtGui, QtWidgets, wrapInstance = _load_qt()
    app = QtWidgets.QApplication.instance()
    if not app:
        return None, None

    main = _get_main_window()
    widgets = []
    for widget in app.allWidgets():
        if main and not main.isAncestorOf(widget) and widget is not main:
            continue
        if not widget.isVisible():
            continue
        if isinstance(
            widget,
            (QtWidgets.QMenu, QtWidgets.QMenuBar, QtWidgets.QStatusBar, QtWidgets.QToolBar, QtWidgets.QDockWidget),
        ):
            continue
        widgets.append(widget)

    best = None
    best_score = -1
    for widget in widgets:
        if _match_viewport_hint(widget, hint):
            best = widget
            break
        rect = widget.rect()
        score = rect.width() * rect.height()
        class_name = widget.metaObject().className()
        if "Viewport" in class_name or "OpenGL" in class_name or "GL" in class_name:
            score += 1_000_000
        if "WindowContainer" in class_name:
            score += 800_000
        if score > best_score:
            best_score = score
            best = widget

    if not best:
        return None, None

    rect = best.rect()
    info = {
        "class_name": best.metaObject().className(),
        "object_name": best.objectName(),
        "width": rect.width(),
        "height": rect.height(),
        "x": rect.x(),
        "y": rect.y(),
        "dpi_scale": float(getattr(best, "devicePixelRatioF", lambda: 1.0)()),
    }
    _VIEWPORT_CACHE["widget"] = best
    _VIEWPORT_CACHE["info"] = info
    return best, info


def _collect_viewport_candidates(limit=20, hint=None):
    QtCore, QtGui, QtWidgets, wrapInstance = _load_qt()
    app = QtWidgets.QApplication.instance()
    if not app:
        return []
    main = _get_main_window()
    candidates = []
    for widget in app.allWidgets():
        if main and not main.isAncestorOf(widget) and widget is not main:
            continue
        if not widget.isVisible():
            continue
        if isinstance(
            widget,
            (QtWidgets.QMenu, QtWidgets.QMenuBar, QtWidgets.QStatusBar, QtWidgets.QToolBar, QtWidgets.QDockWidget),
        ):
            continue
        rect = widget.rect()
        area = rect.width() * rect.height()
        class_name = widget.metaObject().className()
        object_name = widget.objectName()
        score = area
        if "Viewport" in class_name or "OpenGL" in class_name or "GL" in class_name:
            score += 1_000_000
        if "WindowContainer" in class_name:
            score += 800_000
        if _match_viewport_hint(widget, hint):
            score += 2_000_000
        candidates.append({
            "class_name": class_name,
            "object_name": object_name,
            "width": rect.width(),
            "height": rect.height(),
            "area": area,
            "score": score,
        })
    candidates.sort(key=lambda item: item["score"], reverse=True)
    return candidates[:limit]


def _resolve_mouse_button(QtCore, name):
    if not name:
        return QtCore.Qt.LeftButton
    key = str(name).strip().lower()
    if key in {"right", "rmb", "secondary"}:
        return QtCore.Qt.RightButton
    if key in {"middle", "mmb"}:
        return QtCore.Qt.MiddleButton
    return QtCore.Qt.LeftButton


def _resolve_modifiers(QtCore, data):
    modifiers = QtCore.Qt.NoModifier
    if not data:
        return modifiers
    if isinstance(data, dict):
        if data.get("alt"):
            modifiers |= QtCore.Qt.AltModifier
        if data.get("ctrl") or data.get("control"):
            modifiers |= QtCore.Qt.ControlModifier
        if data.get("shift"):
            modifiers |= QtCore.Qt.ShiftModifier
        return modifiers
    if isinstance(data, str):
        parts = [p for p in data.replace("+", " ").replace(",", " ").split() if p]
    else:
        parts = data if isinstance(data, (list, tuple)) else []
    for part in parts:
        key = str(part).strip().lower()
        if key == "alt":
            modifiers |= QtCore.Qt.AltModifier
        elif key in {"ctrl", "control"}:
            modifiers |= QtCore.Qt.ControlModifier
        elif key == "shift":
            modifiers |= QtCore.Qt.ShiftModifier
    return modifiers


def _resolve_key(QtCore, key):
    if key is None:
        return None
    name = str(key).strip()
    if not name:
        return None
    lower = name.lower()
    special = {
        "enter": "Key_Return",
        "return": "Key_Return",
        "esc": "Key_Escape",
        "escape": "Key_Escape",
        "space": "Key_Space",
        "tab": "Key_Tab",
        "backspace": "Key_Backspace",
        "delete": "Key_Delete",
        "del": "Key_Delete",
        "home": "Key_Home",
        "end": "Key_End",
        "pageup": "Key_PageUp",
        "pagedown": "Key_PageDown",
        "up": "Key_Up",
        "down": "Key_Down",
        "left": "Key_Left",
        "right": "Key_Right",
    }
    if lower in special:
        return getattr(QtCore.Qt, special[lower], None)
    if lower.startswith("f") and lower[1:].isdigit():
        return getattr(QtCore.Qt, f"Key_F{lower[1:]}", None)
    if len(lower) == 1 and lower.isalpha():
        return getattr(QtCore.Qt, f"Key_{lower.upper()}", None)
    if len(lower) == 1 and lower.isdigit():
        return getattr(QtCore.Qt, f"Key_{lower}", None)
    return getattr(QtCore.Qt, f"Key_{name}", None)


def _send_key_event(widget, key, modifiers, text="", press=True, release=True, focus=True):
    QtCore, QtGui, QtWidgets, wrapInstance = _load_qt()
    if not widget:
        return {"ok": False, "error": "Target widget not found."}
    if focus:
        widget.setFocus(QtCore.Qt.MouseFocusReason)
    if key is None:
        return {"ok": False, "error": "Unknown key."}
    results = []
    if press:
        evt = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, key, modifiers, text)
        QtWidgets.QApplication.sendEvent(widget, evt)
        results.append("press")
    if release:
        evt = QtGui.QKeyEvent(QtCore.QEvent.KeyRelease, key, modifiers, text)
        QtWidgets.QApplication.sendEvent(widget, evt)
        results.append("release")
    QtWidgets.QApplication.processEvents()
    return {"ok": True, "sent": results}


def _send_key_sequence(widget, keys, modifiers, delay_ms=0, focus=True):
    QtCore, QtGui, QtWidgets, wrapInstance = _load_qt()
    results = []
    for entry in keys:
        key = _resolve_key(QtCore, entry)
        result = _send_key_event(widget, key, modifiers, text=str(entry), focus=focus)
        results.append({"key": entry, "result": result})
        if delay_ms > 0:
            time.sleep(delay_ms / 1000.0)
    return results


def _make_mouse_event(QtCore, QtGui, event_type, local_pos, global_pos, button, modifiers):
    try:
        return QtGui.QMouseEvent(
            event_type,
            QtCore.QPointF(local_pos),
            QtCore.QPointF(global_pos),
            QtCore.QPointF(global_pos),
            button,
            button,
            modifiers,
        )
    except TypeError:
        try:
            return QtGui.QMouseEvent(
                event_type,
                QtCore.QPointF(local_pos),
                QtCore.QPointF(global_pos),
                button,
                button,
                modifiers,
            )
        except TypeError:
            return QtGui.QMouseEvent(event_type, local_pos, button, button, modifiers)


def _send_mouse_click(widget, x, y, button, modifiers):
    QtCore, QtGui, QtWidgets, wrapInstance = _load_qt()
    if not widget:
        return {"ok": False, "error": "Viewport widget not found."}
    rect = widget.rect()
    x = max(0, min(int(x), rect.width() - 1))
    y = max(0, min(int(y), rect.height() - 1))
    local_pos = QtCore.QPoint(x, y)
    global_pos = widget.mapToGlobal(local_pos)

    widget.setFocus(QtCore.Qt.MouseFocusReason)
    press = _make_mouse_event(QtCore, QtGui, QtCore.QEvent.MouseButtonPress, local_pos, global_pos, button, modifiers)
    release = _make_mouse_event(QtCore, QtGui, QtCore.QEvent.MouseButtonRelease, local_pos, global_pos, button, modifiers)

    QtWidgets.QApplication.sendEvent(widget, press)
    QtWidgets.QApplication.sendEvent(widget, release)
    QtWidgets.QApplication.processEvents()
    return {
        "ok": True,
        "local": {"x": x, "y": y},
        "global": {"x": global_pos.x(), "y": global_pos.y()},
    }


def _transform_to_matrix(transform):
    try:
        return transform.Matrix()
    except Exception:
        matrix = RLPy.RMatrix4()
        matrix.FromRTS(transform.R(), transform.T(), transform.S())
        return matrix


def _vec4_components(vec):
    try:
        return [float(vec[i]) for i in range(4)]
    except Exception:
        return [float(vec.X()), float(vec.Y()), float(vec.Z()), float(vec.W())]


def _matrix4_get(matrix, row, col):
    try:
        return float(matrix(row, col))
    except Exception:
        return float(matrix.GetRow(row)[col])


def _matrix4_mul_vec4(matrix, vec):
    try:
        row0 = _vec4_components(matrix.GetRow(0))
        row1 = _vec4_components(matrix.GetRow(1))
        row2 = _vec4_components(matrix.GetRow(2))
        row3 = _vec4_components(matrix.GetRow(3))
        vx, vy, vz, vw = _vec4_components(vec)
        return (
            row0[0] * vx + row0[1] * vy + row0[2] * vz + row0[3] * vw,
            row1[0] * vx + row1[1] * vy + row1[2] * vz + row1[3] * vw,
            row2[0] * vx + row2[1] * vy + row2[2] * vz + row2[3] * vw,
            row3[0] * vx + row3[1] * vy + row3[2] * vz + row3[3] * vw,
        )
    except Exception:
        try:
            vx, vy, vz, vw = _vec4_components(vec)
            return (
                _matrix4_get(matrix, 0, 0) * vx + _matrix4_get(matrix, 0, 1) * vy + _matrix4_get(matrix, 0, 2) * vz + _matrix4_get(matrix, 0, 3) * vw,
                _matrix4_get(matrix, 1, 0) * vx + _matrix4_get(matrix, 1, 1) * vy + _matrix4_get(matrix, 1, 2) * vz + _matrix4_get(matrix, 1, 3) * vw,
                _matrix4_get(matrix, 2, 0) * vx + _matrix4_get(matrix, 2, 1) * vy + _matrix4_get(matrix, 2, 2) * vz + _matrix4_get(matrix, 2, 3) * vw,
                _matrix4_get(matrix, 3, 0) * vx + _matrix4_get(matrix, 3, 1) * vy + _matrix4_get(matrix, 3, 2) * vz + _matrix4_get(matrix, 3, 3) * vw,
            )
        except Exception as exc:
            raise RuntimeError(f"matrix multiply failed: {exc}") from exc


def _axis_value(axis, cam_x, cam_y, cam_z):
    sign = 1.0
    token = str(axis).strip().lower()
    if token.startswith("-"):
        sign = -1.0
        token = token[1:]
    if token == "x":
        return sign * cam_x
    if token == "y":
        return sign * cam_y
    if token == "z":
        return sign * cam_z
    return None


def _project_world_to_viewport(world, camera, viewport_info, axis_map=None):
    if not camera:
        return {"ok": False, "error": "No camera found."}
    if not viewport_info:
        return {"ok": False, "error": "Viewport info unavailable."}

    time_value = RLPy.RGlobal.GetTime()
    transform = camera.WorldTransform()
    view_matrix = _transform_to_matrix(transform).Inverse()

    world_vec = RLPy.RVector4(float(world["x"]), float(world["y"]), float(world["z"]), 1.0)
    try:
        cam_x, cam_y, cam_z, cam_w = _matrix4_mul_vec4(view_matrix, world_vec)
        if cam_w not in (0, 1):
            cam_x /= cam_w
            cam_y /= cam_w
            cam_z /= cam_w
    except Exception as exc:
        return {"ok": False, "error": f"Failed to project world point: {exc}"}

    aperture = camera.GetAperture(0.0, 0.0)
    aperture_width = 0.0
    aperture_height = 0.0
    if isinstance(aperture, (list, tuple)) and len(aperture) >= 3:
        aperture_width = float(aperture[1])
        aperture_height = float(aperture[2])

    viewport_width = float(viewport_info["width"])
    viewport_height = float(viewport_info["height"])
    aspect = viewport_width / viewport_height if viewport_height else 1.0

    focal_length = float(camera.GetFocalLength(time_value))
    if aperture_width > 0 and aperture_height > 0 and focal_length > 0:
        fov_x = 2.0 * math.atan((aperture_width * 0.5) / focal_length)
        fov_y = 2.0 * math.atan((aperture_height * 0.5) / focal_length)
    else:
        angle = math.radians(float(camera.GetAngleOfView(time_value)))
        fit_type = camera.GetFitFovType()
        if fit_type == RLPy.ECameraFitResolution_Horizontal:
            fov_x = angle
            fov_y = 2.0 * math.atan(math.tan(fov_x * 0.5) / aspect)
        else:
            fov_y = angle
            fov_x = 2.0 * math.atan(math.tan(fov_y * 0.5) * aspect)

    candidates = []
    if axis_map:
        candidates.append(axis_map)
    else:
        candidates = [
            {"right": "x", "up": "z", "depth": "-y"},
            {"right": "x", "up": "z", "depth": "y"},
            {"right": "x", "up": "y", "depth": "-z"},
            {"right": "x", "up": "y", "depth": "z"},
        ]

    projection = None
    chosen_axes = None
    for axes in candidates:
        depth = _axis_value(axes["depth"], cam_x, cam_y, cam_z)
        right = _axis_value(axes["right"], cam_x, cam_y, cam_z)
        up = _axis_value(axes["up"], cam_x, cam_y, cam_z)
        if depth is None or right is None or up is None:
            continue
        if depth <= 0:
            continue
        x_ndc = (right / depth) / math.tan(fov_x * 0.5)
        y_ndc = (up / depth) / math.tan(fov_y * 0.5)
        if abs(x_ndc) <= 1.5 and abs(y_ndc) <= 1.5:
            projection = (depth, right, up, x_ndc, y_ndc)
            chosen_axes = axes
            break
        if projection is None:
            projection = (depth, right, up, x_ndc, y_ndc)
            chosen_axes = axes

    if not projection:
        return {"ok": False, "error": "Point is behind the camera."}

    depth, right, up, x_ndc, y_ndc = projection

    screen_x = (x_ndc + 1.0) * 0.5 * viewport_width
    screen_y = (1.0 - (y_ndc + 1.0) * 0.5) * viewport_height

    return {
        "ok": True,
        "axis_map": chosen_axes,
        "screen": {"x": screen_x, "y": screen_y},
        "ndc": {"x": x_ndc, "y": y_ndc},
        "depth": depth,
        "camera_space": {"x": cam_x, "y": cam_y, "z": cam_z},
    }


def _resolve_euler_order(order):
    if not order:
        return EULER_ORDER_MAP["ZXY"]
    token = str(order).strip().upper()
    return EULER_ORDER_MAP.get(token, EULER_ORDER_MAP["ZXY"])


def _load_axis_rotation_map(pose_payload, axis_rotation_map=None, axis_rotation_path=None):
    if isinstance(axis_rotation_map, dict) and axis_rotation_map:
        return axis_rotation_map
    if axis_rotation_path:
        return _load_mapping(axis_rotation_path)
    if not pose_payload:
        return {}
    mapped_pose = pose_payload.get("mapped_pose") or {}
    axis_map = (
        mapped_pose.get("axis_rotation")
        or pose_payload.get("axis_rotation")
        or pose_payload.get("axis_rotation_map")
    )
    if isinstance(axis_map, dict) and axis_map:
        return axis_map
    axis_path = (
        mapped_pose.get("axis_rotation_path")
        or pose_payload.get("axis_rotation_path")
        or pose_payload.get("axis_rotation_file")
    )
    if axis_path:
        return _load_mapping(axis_path)
    return _load_mapping(str(DEFAULT_AXIS_ROTATION_PATH))


def _load_joint_map(pose_payload, joint_map=None, joint_map_path=None):
    if isinstance(joint_map, dict) and joint_map:
        return joint_map
    if joint_map_path:
        data = json.loads(Path(joint_map_path).read_text(encoding="utf-8"))
        if isinstance(data, dict):
            if "joint_map" in data and isinstance(data["joint_map"], dict):
                return data["joint_map"]
            if "mapping" in data and isinstance(data["mapping"], dict):
                return data["mapping"]
            return data
        return {}
    if not pose_payload:
        return {}
    mapping_info = pose_payload.get("mapping") or {}
    mapping_path = mapping_info.get("path") or pose_payload.get("mapping_path")
    if mapping_path:
        try:
            data = json.loads(Path(mapping_path).read_text(encoding="utf-8"))
        except Exception:
            return {}
        if isinstance(data, dict) and "joint_map" in data and isinstance(data["joint_map"], dict):
            return data["joint_map"]
        if isinstance(data, dict) and "mapping" in data and isinstance(data["mapping"], dict):
            return data["mapping"]
        if isinstance(data, dict):
            return data
    return {}


def _normalize_axis_offsets(offsets):
    if not offsets:
        return []
    if isinstance(offsets, str):
        parts = [part.strip() for part in offsets.split(",") if part.strip()]
        offsets = []
        for idx in range(0, len(parts) - 1, 2):
            offsets.append({"axis": parts[idx], "deg": parts[idx + 1]})
        return offsets
    if isinstance(offsets, dict):
        if "axis" in offsets:
            return [offsets]
        if "offsets" in offsets and isinstance(offsets["offsets"], list):
            return offsets["offsets"]
    if isinstance(offsets, (list, tuple)):
        return list(offsets)
    return []


def _axis_vector_from_token(axis_token):
    if axis_token is None:
        return None, 1.0
    token = str(axis_token).strip().upper()
    if not token:
        return None, 1.0
    sign = 1.0
    if token.startswith("-"):
        sign = -1.0
        token = token[1:]
    if token == "X":
        return RLPy.RVector3(1.0, 0.0, 0.0), sign
    if token == "Y":
        return RLPy.RVector3(0.0, 1.0, 0.0), sign
    if token == "Z":
        return RLPy.RVector3(0.0, 0.0, 1.0), sign
    return None, sign


def _quat_from_axis_offsets(offsets):
    offsets = _normalize_axis_offsets(offsets)
    if not offsets:
        return None
    result = None
    for item in offsets:
        if isinstance(item, dict):
            axis = item.get("axis")
            deg = item.get("deg")
        elif isinstance(item, (list, tuple)) and len(item) >= 2:
            axis = item[0]
            deg = item[1]
        else:
            continue
        axis_vec, sign = _axis_vector_from_token(axis)
        if axis_vec is None:
            continue
        angle = math.radians(_to_float(deg, 0.0) * sign)
        q = RLPy.RQuaternion()
        q.FromAxisAngle(axis_vec, angle)
        result = q if result is None else result.Multiply(q)
    return result


def _lookup_axis_offsets(axis_map, axis_map_lower, bone_name, node_name):
    if not axis_map:
        return None
    candidates = []
    if node_name:
        candidates.append(node_name)
    if bone_name and bone_name != node_name:
        candidates.append(bone_name)
    for name in (bone_name, node_name):
        if not name:
            continue
        if str(name).startswith("CC_Base_"):
            continue
        candidates.append(f"CC_Base_{name}")
    for candidate in candidates:
        if not candidate:
            continue
        direct = axis_map.get(candidate)
        if direct:
            return direct
        lowered = axis_map_lower.get(str(candidate).lower()) if axis_map_lower else None
        if lowered:
            return lowered
    return None


def _quat_from_euler(order, rotation, axis_offsets=None):
    rx = math.radians(_to_float(rotation.get("x"), 0.0))
    ry = math.radians(_to_float(rotation.get("y"), 0.0))
    rz = math.radians(_to_float(rotation.get("z"), 0.0))
    matrix = RLPy.RMatrix3()
    order_enum = _resolve_euler_order(order)
    try:
        maybe = matrix.FromEulerAngle(order_enum, rx, ry, rz)
        if maybe is not None:
            matrix = maybe
    except Exception:
        matrix = matrix.FromEulerAngle(order_enum, rx, ry, rz)
    quat = RLPy.RQuaternion()
    quat.FromRotationMatrix(matrix)
    offset_quat = _quat_from_axis_offsets(axis_offsets)
    if offset_quat is not None:
        quat = offset_quat.Multiply(quat)
    return quat


def _load_pose_payload(data):
    pose = data.get("pose")
    if pose:
        return pose
    pose_path = data.get("pose_path") or data.get("path")
    if not pose_path:
        return None
    try:
        payload = json.loads(Path(pose_path).read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload


def _build_bone_map(skeleton):
    bones = skeleton.GetAllAnimationBone() if skeleton else []
    bone_map = {}
    for bone in bones:
        try:
            name = bone.GetName()
        except Exception:
            continue
        if name:
            bone_map[name] = bone
            bone_map[name.lower()] = bone
    return bone_map


def _resolve_bone_node(bone_name, bone_map):
    if not bone_name:
        return None
    direct = bone_map.get(bone_name)
    if direct:
        return direct
    lowered = bone_map.get(str(bone_name).lower())
    if lowered:
        return lowered
    prefixed = bone_map.get(f"CC_Base_{bone_name}")
    if prefixed:
        return prefixed
    prefixed_lower = bone_map.get(f"cc_base_{str(bone_name).lower()}")
    if prefixed_lower:
        return prefixed_lower
    return None


def _apply_pose_json(
    avatar,
    pose_payload,
    time_value,
    clip_index=0,
    apply_root_translation=True,
    axis_rotation_map=None,
    axis_rotation_path=None,
    joint_map=None,
    joint_map_path=None,
):
    if not avatar:
        return {"ok": False, "error": "Avatar not found."}
    if not pose_payload:
        return {"ok": False, "error": "Pose payload is empty."}

    skeleton = avatar.GetSkeletonComponent()
    if not skeleton:
        return {"ok": False, "error": "Skeleton component not found."}

    mapped_pose = pose_payload.get("mapped_pose", {})
    pose_bones = mapped_pose.get("bones") or pose_payload.get("pose")
    if not pose_bones:
        return {"ok": False, "error": "Pose data missing."}

    clip = skeleton.GetClip(int(clip_index)) if clip_index is not None else None
    if clip is None:
        clip = skeleton.AddClip(time_value)
    if clip is None:
        return {"ok": False, "error": "Unable to resolve motion clip."}

    bone_map = _build_bone_map(skeleton)
    axis_map = _load_axis_rotation_map(pose_payload, axis_rotation_map, axis_rotation_path)
    joint_map = _load_joint_map(pose_payload, joint_map=joint_map, joint_map_path=joint_map_path)
    axis_map_lower = {key.lower(): value for key, value in axis_map.items()} if axis_map else {}
    applied = []
    skipped = []

    for bone_name, bone_data in pose_bones.items():
        node_name = bone_name
        if isinstance(bone_data, dict) and bone_data.get("target_bone"):
            node_name = bone_data.get("target_bone")
        elif joint_map:
            mapped = joint_map.get(bone_name) or joint_map.get(str(bone_name))
            if mapped:
                node_name = mapped
        bone_node = _resolve_bone_node(node_name, bone_map)
        if not bone_node:
            skipped.append({"bone": bone_name, "reason": "not_found"})
            continue

        rotation = bone_data.get("rotation", {}) if isinstance(bone_data, dict) else {}
        translation = bone_data.get("translation", {}) if isinstance(bone_data, dict) else {}
        order = bone_data.get("rotation_order") if isinstance(bone_data, dict) else None

        transform = RLPy.RTransform(RLPy.RTransform.IDENTITY)
        axis_overrides = None
        if isinstance(bone_data, dict):
            axis_overrides = bone_data.get("axis_rotation") or bone_data.get("axis_offsets") or bone_data.get(
                "axis_offset"
            )
        axis_offsets = axis_overrides or _lookup_axis_offsets(axis_map, axis_map_lower, bone_name, node_name)
        quat = _quat_from_euler(order, rotation, axis_offsets)
        transform.R().SetX(quat.x)
        transform.R().SetY(quat.y)
        transform.R().SetZ(quat.z)
        transform.R().SetW(quat.w)

        if apply_root_translation or bone_name.lower() == "hips":
            tx = _to_float(translation.get("x"), 0.0)
            ty = _to_float(translation.get("y"), 0.0)
            tz = _to_float(translation.get("z"), 0.0)
            transform.T().SetXYZ(tx, ty, tz)

        control = clip.GetControl("Layer", bone_node)
        if not control:
            skipped.append({"bone": bone_name, "reason": "control_missing"})
            continue
        try:
            control.SetValue(time_value, transform)
            applied.append(bone_name)
        except Exception as exc:
            skipped.append({"bone": bone_name, "reason": str(exc)})

    time_seconds = _safe_call(lambda: time_value.ToSecond(), None)
    return {
        "ok": True,
        "applied": applied,
        "skipped": skipped,
        "clip_index": int(clip_index) if clip_index is not None else None,
        "time_seconds": time_seconds,
    }


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


def _get_md_props():
    return list(RLPy.RScene.GetMDProps())


def _list_md_props():
    entries = []
    for prop in _get_md_props():
        entry = {
            "name": prop.GetName(),
            "id": prop.GetID(),
            "type": int(prop.GetType()),
            "enable_follow_mode": _safe_call(prop.IsEnableFollowMode),
            "changed_follow_object": _safe_call(prop.IsChangedFollowObject),
        }
        try:
            entry["tag_ratio_map"] = prop.GetTagRatioMap().asdict()
        except Exception:
            entry["tag_ratio_map"] = {}
        entries.append(entry)
    return entries


def _resolve_md_props(names):
    if not names:
        return _get_md_props()
    if isinstance(names, str):
        names = [names]
    lookup = {str(name).strip().lower(): name for name in names if str(name).strip()}
    results = []
    for prop in _get_md_props():
        prop_name = prop.GetName()
        key = str(prop_name).strip().lower()
        if key in lookup:
            results.append(prop)
            continue
        if str(prop.GetID()) in lookup:
            results.append(prop)
    return results


def _md_prop_vector(props):
    vec = RLPy.MDPropVector()
    for prop in props:
        vec.append(prop)
    return vec


def _avatar_vector(avatars):
    vec = RLPy.AvatarVector()
    for avatar in avatars:
        vec.append(avatar)
    return vec


def _object_vector(objects):
    vec = RLPy.ObjectVector()
    for obj in objects:
        vec.append(obj)
    return vec


def _md_begin(md, time_value, avatars, record, preserve_one_key):
    opts = RLPy.RBeginCommandOption()
    opts.bRecord = bool(record)
    opts.bAvatar = True
    opts.bPreserveOneKey = bool(preserve_one_key)
    obj_vec = _object_vector(avatars)
    return md.BeginCommand(time_value, obj_vec, opts)


def _md_end(md, time_value, md_props, avatars):
    md_prop_vec = _md_prop_vector(md_props)
    obj_vec = _object_vector(avatars)
    attempts = [
        ("EndCommand(time, md_prop_vec, obj_vec)", lambda: md.EndCommand(time_value, md_prop_vec, obj_vec)),
        ("EndCommand(time, md_prop_vec)", lambda: md.EndCommand(time_value, md_prop_vec)),
        ("EndCommand(time)", lambda: md.EndCommand(time_value)),
        ("EndCommand()", lambda: md.EndCommand()),
    ]
    results = []
    for label, func in attempts:
        try:
            result = func()
            results.append({"label": label, "ok": True, "result": str(result)})
            return {"ok": True, "attempts": results}
        except Exception as exc:
            results.append({"label": label, "ok": False, "error": str(exc)})
    return {"ok": False, "attempts": results}


def _md_embed(md, time_value, avatars):
    avatar_vec = _avatar_vector(avatars)
    return md.EmbedCommand(time_value, avatar_vec)


def _md_remove_triggered(md, time_value, md_props, avatars):
    md_prop_vec = _md_prop_vector(md_props)
    avatar_vec = _avatar_vector(avatars)
    return md.RemoveTriggeredByAnimation(time_value, md_prop_vec, avatar_vec)


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


def _get_object_transform(obj):
    transform = obj.WorldTransform()
    pos = transform.T()
    rot = transform.R()
    scale = transform.S()
    return {
        "position": {"x": pos.x, "y": pos.y, "z": pos.z},
        "rotation": {"x": rot.x, "y": rot.y, "z": rot.z, "w": rot.w},
        "scale": {"x": scale.x, "y": scale.y, "z": scale.z},
    }


def _set_object_transform(obj, data):
    control = obj.GetControl("Transform")
    if control is None:
        return {"ok": False, "error": "Object has no Transform control."}

    time_seconds = data.get("time_seconds")
    if time_seconds is None:
        time_value = RLPy.RGlobal.GetTime()
    else:
        time_value = _time_from_seconds(float(time_seconds))

    base = obj.WorldTransform()
    transform_data = data.get("transform") or data
    scale = _vector3_from_dict(transform_data.get("scale"), base.S())
    rotation = _quat_from_dict(transform_data.get("rotation"), base.R())
    translation = _vector3_from_dict(
        transform_data.get("translation") or transform_data.get("position"),
        base.T(),
    )
    transform = RLPy.RTransform(scale, rotation, translation)
    control.SetValue(time_value, transform)
    _safe_call(obj.Update)
    return {"ok": True, "time_seconds": time_seconds}


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
        try:
            camera.SetFarClippingPlane(float(data["far_plane"]))
        except TypeError:
            camera.SetFarClippingPlane(time, float(data["far_plane"]))

    if "focal_length" in data:
        camera.SetFocalLength(time, float(data["focal_length"]))

    dof_settings = data.get("dof")
    if isinstance(dof_settings, dict):
        dof_data = _build_dof_data(camera, dof_settings)
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


def _resolve_reallusion_index_path(index_path=None):
    if index_path:
        return Path(index_path)
    env_path = os.environ.get("REALLUSION_INDEX_PATH") or os.environ.get("VISIONEXE_REALLUSION_INDEX")
    if env_path:
        return Path(env_path)
    config, _ = load_config()
    cfg_path = config.get("reallusion_index_path")
    if cfg_path:
        return Path(cfg_path)
    if DEFAULT_REALLUSION_INDEX_PATH.exists():
        return DEFAULT_REALLUSION_INDEX_PATH
    script_dir = Path(__file__).resolve().parent
    return script_dir.parent / "config" / "reallusion_library_index.json"


def _find_asset_in_index(name, index_path=None):
    path = _resolve_reallusion_index_path(index_path)
    if not path.exists():
        return None
    
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        items = data.get("items", [])
        name_lower = name.lower()
        
        # Priority match: exact name match
        for item in items:
            if item.get("name").lower() == name_lower:
                return item
        
        # Fallback: simple substring match? maybe unsafe. Let's stick to exact name for now.
    except Exception:
        pass
    return None


def _prefer_extension(value):
    if not value:
        return None
    token = str(value).strip().lower()
    if token in {"ccavatar", ".ccavatar"}:
        return ".ccavatar"
    if token in {"iavatar", "avatar", ".iavatar"}:
        return ".iavatar"
    return None


def _iter_content_files(root_key, include_default=True, include_custom=True):
    roots = []
    if include_default:
        default_root = RLPy.RApplication.GetDefaultContentFolder(root_key)
        if default_root:
            roots.append(default_root)
    if include_custom:
        custom_root = RLPy.RApplication.GetCustomContentFolder(root_key)
        if custom_root and custom_root not in roots:
            roots.append(custom_root)
    if not roots:
        return []

    seen = set()
    stack = list(roots)
    folders = []
    while stack:
        folder = stack.pop()
        if folder in seen:
            continue
        seen.add(folder)
        folders.append(folder)
        try:
            subfolders = RLPy.RApplication.GetContentFoldersInFolder(folder) or []
        except Exception:
            subfolders = []
        for sub in subfolders:
            if sub and sub not in seen:
                stack.append(sub)

    files = []
    for folder in folders:
        try:
            items = RLPy.RApplication.GetContentFilesInFolder(folder) or []
        except Exception:
            items = []
        files.extend(items)
    return files


def _get_content_roots(root_key):
    try:
        default_root = RLPy.RApplication.GetDefaultContentFolder(root_key)
    except Exception:
        default_root = None
    try:
        custom_root = RLPy.RApplication.GetCustomContentFolder(root_key)
    except Exception:
        custom_root = None
    return {
        "default": default_root,
        "custom": custom_root,
    }


def _resolve_root_key(name):
    if name is None:
        return RLPy.ETemplateRootFolder_Character
    if isinstance(name, int):
        return name
    token = str(name).strip()
    if not token:
        return RLPy.ETemplateRootFolder_Character
    if token.startswith("ETemplateRootFolder_"):
        return getattr(RLPy, token, RLPy.ETemplateRootFolder_Character)
    attr = f"ETemplateRootFolder_{token}"
    return getattr(RLPy, attr, RLPy.ETemplateRootFolder_Character)


def _collect_content_folders(root_folder, max_folders=None):
    results = []
    seen = set()

    def walk(folder):
        if not folder or folder in seen:
            return
        seen.add(folder)
        results.append(folder)
        if max_folders and len(results) >= max_folders:
            return
        try:
            subs = RLPy.RApplication.GetContentFoldersInFolder(folder) or []
        except Exception:
            subs = []
        for sub in subs:
            if max_folders and len(results) >= max_folders:
                break
            walk(sub)

    walk(root_folder)
    return results


def _collect_content_files(folders, max_files=None):
    files = []
    for folder in folders:
        try:
            items = RLPy.RApplication.GetContentFilesInFolder(folder) or []
        except Exception:
            items = []
        for item in items:
            files.append(item)
            if max_files and len(files) >= max_files:
                return files
    return files


def _find_actor_in_content_manager(name, prefer_ext=None, include_default=True, include_custom=True):
    name_lower = str(name).strip().lower()
    if not name_lower:
        return None
    matches = []
    files = _iter_content_files(
        RLPy.ETemplateRootFolder_Character,
        include_default=include_default,
        include_custom=include_custom,
    )
    for file_path in files:
        if not file_path:
            continue
        candidate = Path(str(file_path))
        if candidate.stem.lower() == name_lower or candidate.name.lower() == name_lower:
            if prefer_ext and candidate.suffix.lower() != prefer_ext:
                matches.append(candidate)
                continue
            return str(candidate)
    if prefer_ext:
        for candidate in matches:
            if candidate.suffix.lower() == prefer_ext:
                return str(candidate)
    if matches:
        return str(matches[0])
    return None


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

        if action == "get_avatar_info":
            avatar = _find_avatar(data.get("avatar_name"))
            if not avatar:
                return self._send_json(404, {"ok": False, "error": "No avatar found."})
            info = _get_object_transform(avatar)
            info["name"] = avatar.GetName()
            return self._send_json(200, {"ok": True, "info": info})

        if action == "set_avatar_transform":
            avatar = _find_avatar(data.get("avatar_name"))
            if not avatar:
                return self._send_json(404, {"ok": False, "error": "No avatar found."})
            result = _set_object_transform(avatar, data)
            status = 200 if result.get("ok") else 400
            result["avatar"] = avatar.GetName()
            return self._send_json(status, result)

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

        if action == "load_actor_by_name":
            # NEW: Load from index by name
            name = data.get("name")
            if not name:
                return self._send_json(400, {"ok": False, "error": "Missing name."})
            
            prefer_ext = _prefer_extension(data.get("prefer") or data.get("prefer_ext"))
            content_first = bool(data.get("content_manager_first", True))
            abs_path = None
            if data.get("use_content_manager", True) and content_first:
                abs_path = _find_actor_in_content_manager(
                    name,
                    prefer_ext=prefer_ext,
                    include_default=bool(data.get("include_default", True)),
                    include_custom=bool(data.get("include_custom", True)),
                )
            if not abs_path:
                entry = _find_asset_in_index(name, data.get("index_path"))
                if entry:
                    abs_path = entry.get("abs_path") or entry.get("path")
            if not abs_path and data.get("use_content_manager", True) and not content_first:
                abs_path = _find_actor_in_content_manager(
                    name,
                    prefer_ext=prefer_ext,
                    include_default=bool(data.get("include_default", True)),
                    include_custom=bool(data.get("include_custom", True)),
                )
        if not abs_path:
            return self._send_json(404, {"ok": False, "error": f"Actor '{name}' not found in index or content manager."})
            
            try:
                RLPy.RFileIO.LoadObject(abs_path, True)
                return self._send_json(200, {"ok": True, "loaded": name, "path": abs_path})
            except Exception as e:
                return self._send_json(500, {"ok": False, "error": str(e)})

        if action == "debug_actor_lookup":
            name = data.get("name")
            if not name:
                return self._send_json(400, {"ok": False, "error": "Missing name."})
            prefer_ext = _prefer_extension(data.get("prefer") or data.get("prefer_ext"))
            include_default = bool(data.get("include_default", True))
            include_custom = bool(data.get("include_custom", True))
            resolved_index = _resolve_reallusion_index_path(data.get("index_path"))
            entry = _find_asset_in_index(name, data.get("index_path"))
            cm_path = _find_actor_in_content_manager(
                name,
                prefer_ext=prefer_ext,
                include_default=include_default,
                include_custom=include_custom,
            )
            roots = _get_content_roots(RLPy.ETemplateRootFolder_Character)
            payload = {
                "ok": True,
                "name": name,
                "prefer_ext": prefer_ext,
                "index_path": str(resolved_index),
                "index_exists": bool(resolved_index and Path(resolved_index).exists()),
                "index_match": entry,
                "content_roots": roots,
                "content_match": cm_path,
            }
            return self._send_json(200, payload)

        if action == "content_manager_scan":
            root_key = _resolve_root_key(data.get("root_key") or data.get("content_key") or "Character")
            include_default = bool(data.get("include_default", True))
            include_custom = bool(data.get("include_custom", True))
            max_folders = _to_int(data.get("max_folders"), 0) or None
            max_files = _to_int(data.get("max_files"), 0) or None
            roots = _get_content_roots(root_key)
            folders = []
            if include_default and roots.get("default"):
                folders.extend(_collect_content_folders(roots["default"], max_folders=max_folders))
            if include_custom and roots.get("custom"):
                folders.extend(_collect_content_folders(roots["custom"], max_folders=max_folders))
            files = _collect_content_files(folders, max_files=max_files)
            return self._send_json(200, {
                "ok": True,
                "root_key": int(root_key),
                "content_roots": roots,
                "folder_count": len(folders),
                "file_count": len(files),
                "folders": folders,
                "files": files,
            })

        if action == "apply_a2f_json":
            # ... (A2F logic) ...
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

        if action == "apply_pose_json":
            avatar = _find_avatar(data.get("avatar_name"))
            if not avatar:
                return self._send_json(404, {"ok": False, "error": "No avatar found."})
            pose_payload = _load_pose_payload(data)
            time_seconds = data.get("time_seconds")
            time_value = _time_from_seconds(float(time_seconds)) if time_seconds is not None else RLPy.RGlobal.GetTime()
            clip_index = data.get("clip_index", 0)
            apply_root_translation = bool(data.get("apply_root_translation", True))
            axis_rotation_map = data.get("axis_rotation_map")
            axis_rotation_path = data.get("axis_rotation_path")
            joint_map = data.get("joint_map")
            joint_map_path = data.get("joint_map_path") or data.get("mapping_path")
            try:
                result = _apply_pose_json(
                    avatar,
                    pose_payload,
                    time_value,
                    clip_index=clip_index,
                    apply_root_translation=apply_root_translation,
                    axis_rotation_map=axis_rotation_map,
                    axis_rotation_path=axis_rotation_path,
                    joint_map=joint_map,
                    joint_map_path=joint_map_path,
                )
            except Exception as exc:
                return self._send_json(500, {"ok": False, "error": f"apply_pose_json failed: {exc}"})
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

        if action == "md_discover":
            # ... (unchanged) ...
            md = RLPy.RGlobal.GetMotionDirector()
            avatars = _get_avatars()
            av = _find_avatar(data.get("avatar_name"))
            
            discovery = {
                "md_manager": [m for m in dir(md) if not m.startswith('__')],
                "avatar_name": av.GetName() if av else None,
                "avatar_methods": [m for m in dir(av) if not m.startswith('__')] if av else [],
                "md_props": _list_md_props()
            }
            
            return self._send_json(200, {"ok": True, "discovery": discovery})

        if action == "md_set_config":
            # ... (unchanged) ...
            avatar = _find_avatar(data.get("avatar_name"))
            if not avatar:
                return self._send_json(404, {"ok": False, "error": "No avatar found."})
            
            config = data.get("config", {})
            results = {"avatar": avatar.GetName(), "applied": []}
            
            comps = avatar.GetComponents()
            md_comp = None
            for i in range(comps.GetCount()):
                c = comps.GetItem(i)
                if "motion" in c.GetName().lower() or "director" in c.GetName().lower():
                    md_comp = c
                    break
            
            if md_comp:
                for key, value in config.items():
                    setter_name = f"Set{key.replace('_', ' ').title().replace(' ', '')}"
                    if hasattr(md_comp, setter_name):
                        try:
                            getattr(md_comp, setter_name)(value)
                            results["applied"].append({key: "success", "method": setter_name})
                        except Exception as e:
                            results["applied"].append({key: f"failed: {e}", "method": setter_name})
                    else:
                        if hasattr(md_comp, key):
                            try:
                                setattr(md_comp, key, value)
                                results["applied"].append({key: "success", "attr": key})
                            except Exception as e:
                                results["applied"].append({key: f"failed: {e}", "attr": key})
            
            return self._send_json(200, {"ok": True, "results": results})

        if action == "run_python":
            # ... (unchanged) ...
            code = data.get("code")
            if not code:
                return self._send_json(400, {"ok": False, "error": "Missing code."})
            
            try:
                local_vars = {}
                global_vars = {"RLPy": RLPy, "json": json, "os": os, "sys": sys}
                global_vars["_get_avatars"] = _get_avatars
                global_vars["_find_avatar"] = _find_avatar
                global_vars["_get_md_props"] = _get_md_props
                
                exec(code, global_vars, local_vars)
                
                serializable_locals = {}
                for k, v in local_vars.items():
                    try:
                        json.dumps(v)
                        serializable_locals[k] = v
                    except:
                        serializable_locals[k] = str(v)
                        
                return self._send_json(200, {"ok": True, "locals": serializable_locals})
            except Exception as e:
                import traceback
                return self._send_json(500, {"ok": False, "error": str(e), "traceback": traceback.format_exc()})

        if action == "inspect_md":
            # ... (unchanged) ...
            md = RLPy.RGlobal.GetMotionDirector()
            md_members = dir(md) if md else []
            
            prop_data = []
            for prop in _get_md_props():
                prop_data.append({
                    "name": prop.GetName(),
                    "members": dir(prop)
                })
                
            return self._send_json(200, {
                "ok": True, 
                "md_members": md_members,
                "props": prop_data
            })

        if action == "list_md_props":
            return self._send_json(200, {"ok": True, "props": _list_md_props()})

        if action == "md_status":
            md = RLPy.RGlobal.GetMotionDirector()
            return self._send_json(200, {"ok": True, "running": md.IsRunning(), "ready": md.IsReady()})

        if action == "md_viewport_info":
            hint = data.get("viewport_hint")
            widget, info = _resolve_viewport_widget(force=bool(data.get("force_refresh")), hint=hint)
            if not widget:
                return self._send_json(404, {"ok": False, "error": "Viewport widget not found."})
            payload_out = {"ok": True, "viewport": info}
            if data.get("include_candidates"):
                payload_out["candidates"] = _collect_viewport_candidates(
                    limit=_to_int(data.get("limit"), 20),
                    hint=hint,
                )
            return self._send_json(200, payload_out)

        if action == "md_viewport_candidates":
            hint = data.get("viewport_hint")
            candidates = _collect_viewport_candidates(
                limit=_to_int(data.get("limit"), 20),
                hint=hint,
            )
            return self._send_json(200, {"ok": True, "candidates": candidates})

        if action == "md_key":
            # ... (unchanged) ...
            if data.get("ensure_md") or data.get("start_md"):
                md = RLPy.RGlobal.GetMotionDirector()
                if not md.IsRunning():
                    md.Start()
            target = str(data.get("target") or "viewport").lower()
            hint = data.get("viewport_hint")
            if target == "main":
                widget = _get_main_window()
                info = {"target": "main"}
            else:
                widget, info = _resolve_viewport_widget(force=bool(data.get("force_refresh")), hint=hint)
            if not widget:
                return self._send_json(404, {"ok": False, "error": "Target widget not found."})

            QtCore, QtGui, QtWidgets, wrapInstance = _load_qt()
            mod = _resolve_modifiers(QtCore, data.get("modifiers"))
            if data.get("alt") and not (mod & QtCore.Qt.AltModifier):
                mod |= QtCore.Qt.AltModifier
            if data.get("ctrl") and not (mod & QtCore.Qt.ControlModifier):
                mod |= QtCore.Qt.ControlModifier
            if data.get("shift") and not (mod & QtCore.Qt.ShiftModifier):
                mod |= QtCore.Qt.ShiftModifier

            focus = bool(data.get("focus", True))
            delay_ms = _to_int(data.get("delay_ms"), 0)

            if data.get("text"):
                results = _send_key_sequence(widget, list(data["text"]), mod, delay_ms=delay_ms, focus=focus)
                return self._send_json(200, {"ok": True, "target": info, "results": results})

            keys = data.get("keys") or []
            if not keys:
                key = data.get("key")
                if key is None:
                    return self._send_json(400, {"ok": False, "error": "Missing key or keys."})
                keys = [key]

            results = _send_key_sequence(widget, keys, mod, delay_ms=delay_ms, focus=focus)
            return self._send_json(200, {"ok": True, "target": info, "results": results})

        if action == "md_click_screen":
            # ... (unchanged) ...
            if data.get("ensure_md") or data.get("start_md"):
                md = RLPy.RGlobal.GetMotionDirector()
                if not md.IsRunning():
                    md.Start()
            hint = data.get("viewport_hint")
            widget, info = _resolve_viewport_widget(force=bool(data.get("force_refresh")), hint=hint)
            if not widget or not info:
                return self._send_json(404, {"ok": False, "error": "Viewport widget not found."})
            x = data.get("x")
            y = data.get("y")
            if x is None or y is None:
                return self._send_json(400, {"ok": False, "error": "Missing screen coordinates."})
            if data.get("normalized"):
                x = float(x) * float(info["width"])
                y = float(y) * float(info["height"])
            button_name = data.get("button")
            modifiers = data.get("modifiers")
            QtCore, QtGui, QtWidgets, wrapInstance = _load_qt()
            button = _resolve_mouse_button(QtCore, button_name)
            mod = _resolve_modifiers(QtCore, modifiers)
            if data.get("alt", True) and not (mod & QtCore.Qt.AltModifier):
                mod |= QtCore.Qt.AltModifier
            result = _send_mouse_click(widget, x, y, button, mod)
            status = 200 if result.get("ok") else 400
            return self._send_json(status, {"ok": result.get("ok"), "viewport": info, "result": result})

        if action == "md_click_world":
            # ... (unchanged) ...
            if data.get("ensure_md") or data.get("start_md"):
                md = RLPy.RGlobal.GetMotionDirector()
                if not md.IsRunning():
                    md.Start()
            hint = data.get("viewport_hint")
            widget, info = _resolve_viewport_widget(force=bool(data.get("force_refresh")), hint=hint)
            if not widget or not info:
                return self._send_json(404, {"ok": False, "error": "Viewport widget not found."})
            world = data.get("world") or {
                "x": data.get("x"),
                "y": data.get("y"),
                "z": data.get("z"),
            }
            if world.get("x") is None or world.get("y") is None or world.get("z") is None:
                return self._send_json(400, {"ok": False, "error": "Missing world coordinates."})
            camera = _find_camera(data.get("camera_name"))
            projection = _project_world_to_viewport(world, camera, info, axis_map=data.get("axis_map"))
            if not projection.get("ok"):
                return self._send_json(400, projection)
            button_name = data.get("button")
            modifiers = data.get("modifiers")
            QtCore, QtGui, QtWidgets, wrapInstance = _load_qt()
            button = _resolve_mouse_button(QtCore, button_name)
            mod = _resolve_modifiers(QtCore, modifiers)
            if data.get("alt", True) and not (mod & QtCore.Qt.AltModifier):
                mod |= QtCore.Qt.AltModifier
            result = _send_mouse_click(widget, projection["screen"]["x"], projection["screen"]["y"], button, mod)
            status = 200 if result.get("ok") else 400
            return self._send_json(status, {
                "ok": result.get("ok"),
                "viewport": info,
                "projection": projection,
                "result": result,
            })

        if action == "md_waypoints":
            # ... (unchanged) ...
            if data.get("ensure_md") or data.get("start_md"):
                md = RLPy.RGlobal.GetMotionDirector()
                if not md.IsRunning():
                    md.Start()
            hint = data.get("viewport_hint")
            widget, info = _resolve_viewport_widget(force=bool(data.get("force_refresh")), hint=hint)
            if not widget or not info:
                return self._send_json(404, {"ok": False, "error": "Viewport widget not found."})
            points = data.get("points") or data.get("waypoints") or []
            if not points:
                return self._send_json(400, {"ok": False, "error": "No waypoint points provided."})
            camera = _find_camera(data.get("camera_name"))
            delay_ms = _to_int(data.get("delay_ms"), 0)
            button_name = data.get("button")
            modifiers = data.get("modifiers")
            QtCore, QtGui, QtWidgets, wrapInstance = _load_qt()
            button = _resolve_mouse_button(QtCore, button_name)
            mod = _resolve_modifiers(QtCore, modifiers)
            if data.get("alt", True) and not (mod & QtCore.Qt.AltModifier):
                mod |= QtCore.Qt.AltModifier
            results = []
            for idx, point in enumerate(points):
                projection = _project_world_to_viewport(point, camera, info, axis_map=data.get("axis_map"))
                if not projection.get("ok"):
                    results.append({"ok": False, "projection": projection, "index": idx})
                    continue
                click_result = _send_mouse_click(
                    widget,
                    projection["screen"]["x"],
                    projection["screen"]["y"],
                    button,
                    mod,
                )
                results.append({"ok": click_result.get("ok"), "projection": projection, "result": click_result})
                if delay_ms > 0:
                    time.sleep(delay_ms / 1000.0)
            return self._send_json(200, {"ok": True, "viewport": info, "results": results})

        if action == "md_start":
            md = RLPy.RGlobal.GetMotionDirector()
            try:
                if not md.IsRunning():
                    md.Start()
                return self._send_json(200, {"ok": True, "running": md.IsRunning()})
            except Exception as exc:
                return self._send_json(400, {"ok": False, "error": str(exc)})

        if action == "md_stop":
            md = RLPy.RGlobal.GetMotionDirector()
            try:
                if md.IsRunning():
                    md.Stop()
                return self._send_json(200, {"ok": True, "running": md.IsRunning()})
            except Exception as exc:
                return self._send_json(400, {"ok": False, "error": str(exc)})

        if action == "md_begin_command":
            md = RLPy.RGlobal.GetMotionDirector()
            avatar = _find_avatar(data.get("avatar_name"))
            if not avatar:
                return self._send_json(404, {"ok": False, "error": "No avatar found."})
            record = bool(data.get("record", True))
            preserve_one_key = bool(data.get("preserve_one_key", False))
            time_seconds = data.get("time_seconds")
            time_value = _time_from_seconds(float(time_seconds)) if time_seconds is not None else RLPy.RGlobal.GetTime()
            try:
                result = _md_begin(md, time_value, [avatar], record, preserve_one_key)
                return self._send_json(200, {"ok": True, "result": str(result)})
            except Exception as exc:
                return self._send_json(400, {"ok": False, "error": str(exc)})

        if action == "md_end_command":
            md = RLPy.RGlobal.GetMotionDirector()
            avatar = _find_avatar(data.get("avatar_name"))
            if not avatar:
                return self._send_json(404, {"ok": False, "error": "No avatar found."})
            md_props = _resolve_md_props(data.get("md_props"))
            time_seconds = data.get("time_seconds")
            time_value = _time_from_seconds(float(time_seconds)) if time_seconds is not None else RLPy.RGlobal.GetTime()
            result = _md_end(md, time_value, md_props, [avatar])
            status = 200 if result.get("ok") else 400
            return self._send_json(status, result)

        if action == "md_embed_command":
            md = RLPy.RGlobal.GetMotionDirector()
            avatar = _find_avatar(data.get("avatar_name"))
            if not avatar:
                return self._send_json(404, {"ok": False, "error": "No avatar found."})
            time_seconds = data.get("time_seconds")
            time_value = _time_from_seconds(float(time_seconds)) if time_seconds is not None else RLPy.RGlobal.GetTime()
            try:
                result = _md_embed(md, time_value, [avatar])
                return self._send_json(200, {"ok": True, "result": str(result)})
            except Exception as exc:
                return self._send_json(400, {"ok": False, "error": str(exc)})

        if action == "md_remove_triggered":
            md = RLPy.RGlobal.GetMotionDirector()
            avatar = _find_avatar(data.get("avatar_name"))
            if not avatar:
                return self._send_json(404, {"ok": False, "error": "No avatar found."})
            md_props = _resolve_md_props(data.get("md_props"))
            time_seconds = data.get("time_seconds")
            time_value = _time_from_seconds(float(time_seconds)) if time_seconds is not None else RLPy.RGlobal.GetTime()
            try:
                result = _md_remove_triggered(md, time_value, md_props, [avatar])
                return self._send_json(200, {"ok": True, "result": str(result)})
            except Exception as exc:
                return self._send_json(400, {"ok": False, "error": str(exc)})

        if action == "md_trigger":
            md = RLPy.RGlobal.GetMotionDirector()
            avatar = _find_avatar(data.get("avatar_name"))
            if not avatar:
                return self._send_json(404, {"ok": False, "error": "No avatar found."})
            start_md = bool(data.get("start_md", False))
            record = bool(data.get("record", True))
            preserve_one_key = bool(data.get("preserve_one_key", False))
            md_props = _resolve_md_props(data.get("md_props"))
            time_seconds = data.get("time_seconds")
            time_value = _time_from_seconds(float(time_seconds)) if time_seconds is not None else RLPy.RGlobal.GetTime()
            if start_md and not md.IsRunning():
                md.Start()
            try:
                begin_result = _md_begin(md, time_value, [avatar], record, preserve_one_key)
            except Exception as exc:
                return self._send_json(400, {"ok": False, "error": f"BeginCommand failed: {exc}"})
            end_result = _md_end(md, time_value, md_props, [avatar])
            status = 200 if end_result.get("ok") else 400
            return self._send_json(status, {"ok": end_result.get("ok"), "begin_result": str(begin_result), "end_result": end_result})

        if action == "md_action":
            command = str(data.get("command") or "").strip().lower()
            if command == "start":
                md = RLPy.RGlobal.GetMotionDirector()
                try:
                    if not md.IsRunning():
                        md.Start()
                    return self._send_json(200, {"ok": True, "running": md.IsRunning()})
                except Exception as exc:
                    return self._send_json(400, {"ok": False, "error": str(exc)})
            if command == "stop":
                md = RLPy.RGlobal.GetMotionDirector()
                try:
                    if md.IsRunning():
                        md.Stop()
                    return self._send_json(200, {"ok": True, "running": md.IsRunning()})
                except Exception as exc:
                    return self._send_json(400, {"ok": False, "error": str(exc)})
            return self._send_json(400, {"ok": False, "error": "Unknown md_action command (use md_start/md_stop)."})

    def log_message(self, format, *args):
        return


_SERVER_INSTANCE = None

def start_server(host=DEFAULT_HOST, port=DEFAULT_PORT):
    global _SERVER_INSTANCE
    if _SERVER_INSTANCE:
        print(f"[iClone Remote] Server already running.")
        return _SERVER_INSTANCE, None

    try:
        server = HTTPServer((host, port), ICloneRemoteHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        _SERVER_INSTANCE = server
        print(f"[iClone Remote] Started on {host}:{port}")
        return server, thread
    except OSError as e:
        print(f"[iClone Remote] Failed to start server on {host}:{port} (Port busy?): {e}")
        return None, None
    except Exception as e:
        print(f"[iClone Remote] Critical error starting server: {e}")
        return None, None

def stop_server():
    global _SERVER_INSTANCE
    server = _SERVER_INSTANCE
    if not server:
        return False
    try:
        server.shutdown()
        server.server_close()
    except Exception as exc:
        print(f"[iClone Remote] Error stopping server: {exc}")
        return False
    _SERVER_INSTANCE = None
    print("[iClone Remote] Stopped.")
    return True

def main():
    config, config_path = load_config()
    remote_cfg = config.get("remote", {})
    host = os.environ.get("ICLONE_REMOTE_HOST", remote_cfg.get("host", DEFAULT_HOST))
    port = _to_int(os.environ.get("ICLONE_REMOTE_PORT", remote_cfg.get("port", DEFAULT_PORT)), DEFAULT_PORT)
    
    server, thread = start_server(host, port)
    if server:
        print(f"[iClone Remote] Listening on http://{host}:{port} (config: {config_path})")
    else:
        print("[iClone Remote] Could not start server. Check logs/console.")
    
    return server, thread


if __name__ == "__main__":
    main()
