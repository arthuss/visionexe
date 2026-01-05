import argparse
import json
import sys

import bpy
from mathutils import Vector

DEFAULT_OUTPUT = "sam3_bvh_to_cc4.json"


def parse_args():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    parser = argparse.ArgumentParser(description="Map SAM3 joints to CC4 bones in Blender.")
    parser.add_argument("--source", help="Source armature name (SAM3).")
    parser.add_argument("--target", help="Target armature name (CC4).")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Output mapping JSON path.")
    parser.add_argument("--source-root", default="", help="Explicit source root bone name.")
    parser.add_argument("--target-root", default="", help="Explicit target root bone name.")
    parser.add_argument("--merge", action="store_true", help="Preserve existing mapping entries.")
    parser.add_argument("--dry-run", action="store_true", help="Print mapping without writing.")
    return parser.parse_args(argv)


def list_armatures():
    return [obj for obj in bpy.data.objects if obj.type == "ARMATURE"]


def has_bone_prefix(arm_obj, prefix):
    return any(bone.name.startswith(prefix) for bone in arm_obj.data.bones)

def guess_armature(prefer_cc=False, prefer_joint=False):
    for armature in list_armatures():
        if prefer_cc and has_bone_prefix(armature, "CC_Base_"):
            return armature
        if prefer_joint and has_bone_prefix(armature, "Joint_"):
            return armature
    arms = list_armatures()
    return arms[0] if arms else None


def resolve_armatures(source_name, target_name):
    source = bpy.data.objects.get(source_name) if source_name else None
    target = bpy.data.objects.get(target_name) if target_name else None
    if source is None:
        source = guess_armature(prefer_joint=True)
    if target is None:
        target = guess_armature(prefer_cc=True)
    if source is None or target is None:
        raise RuntimeError("Could not resolve source/target armatures.")
    return source, target


def pick_root(bones, preferred_names):
    for name in preferred_names:
        if name and name in bones:
            return name
    for name, data in bones.items():
        if data["parent"] is None:
            return name
    return next(iter(bones.keys()))


def bone_world_positions(arm_obj):
    matrix = arm_obj.matrix_world
    bones = {}
    for bone in arm_obj.data.bones:
        head = matrix @ bone.head_local
        tail = matrix @ bone.tail_local
        bones[bone.name] = {
            "parent": bone.parent.name if bone.parent else None,
            "head": [head.x, head.y, head.z],
            "tail": [tail.x, tail.y, tail.z],
        }
    return bones


def normalize_bones(bones, root_name):
    root_head = Vector(bones[root_name]["head"])
    max_dist = 0.0
    for data in bones.values():
        dist = (Vector(data["head"]) - root_head).length
        if dist > max_dist:
            max_dist = dist
    if max_dist <= 0.0:
        max_dist = 1.0
    for data in bones.values():
        head = Vector(data["head"])
        rel = (head - root_head) / max_dist
        data["head_rel"] = [rel.x, rel.y, rel.z]
        data["side"] = classify_side(rel.x)
    return bones


def classify_side(x_value, epsilon=0.02):
    if abs(x_value) <= epsilon:
        return "center"
    return "left" if x_value < 0 else "right"


def is_descendant(bones, child_name, ancestor_name):
    current = child_name
    while current:
        if current == ancestor_name:
            return True
        current = bones.get(current, {}).get("parent")
    return False


def distance(a, b):
    return (Vector(a) - Vector(b)).length


def depth(bones, name):
    value = 0
    current = name
    while current and bones.get(current, {}).get("parent"):
        value += 1
        current = bones[current]["parent"]
    return value


def choose_target(src, source_bones, target_bones, joint_map, used_targets):
    src_data = source_bones[src]
    src_side = src_data.get("side")
    src_parent = src_data.get("parent")
    mapped_parent = joint_map.get(src_parent) if src_parent else None
    src_pos = src_data.get("head_rel")
    candidates = []
    for target_name, target_data in target_bones.items():
        if target_name in used_targets:
            continue
        target_side = target_data.get("side")
        if src_side != "center" and target_side != src_side:
            continue
        if mapped_parent and not is_descendant(target_bones, target_name, mapped_parent):
            continue
        candidates.append(target_name)
    if not candidates:
        for target_name in target_bones:
            if target_name not in used_targets:
                candidates.append(target_name)
    best = None
    best_dist = None
    for target_name in candidates:
        target_pos = target_bones[target_name].get("head_rel")
        if not target_pos:
            continue
        dist = distance(src_pos, target_pos)
        if best is None or dist < best_dist:
            best = target_name
            best_dist = dist
    return best


def build_mapping(source_bones, target_bones, source_root, target_root, existing):
    joint_map = dict(existing) if existing else {}
    used_targets = {value for value in joint_map.values() if value}
    if source_root not in joint_map or not joint_map[source_root]:
        joint_map[source_root] = target_root
    used_targets.add(joint_map[source_root])
    ordered = list(source_bones.keys())
    ordered.sort(key=lambda name: depth(source_bones, name))
    for src in ordered:
        if src == source_root:
            continue
        if joint_map.get(src):
            continue
        best = choose_target(src, source_bones, target_bones, joint_map, used_targets)
        if best:
            joint_map[src] = best
            used_targets.add(best)
    return joint_map

def load_existing(output_path):
    try:
        with open(output_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except Exception:
        return {}
    return payload.get("joint_map", {}) or {}


def main():
    args = parse_args()
    source, target = resolve_armatures(args.source, args.target)
    source_bones = bone_world_positions(source)
    target_bones = bone_world_positions(target)
    source_root = pick_root(source_bones, [args.source_root, "Hips", "Root"])
    target_root = pick_root(target_bones, [args.target_root, "CC_Base_Hip", "RL_BoneRoot"])
    normalize_bones(source_bones, source_root)
    normalize_bones(target_bones, target_root)
    existing = load_existing(args.output) if args.merge else {}
    joint_map = build_mapping(source_bones, target_bones, source_root, target_root, existing)
    payload = {
        "schema_version": "pose_mapping_v1",
        "source": {"name": source.name, "root": source_root},
        "target": {"name": target.name, "root": target_root},
        "joint_map": joint_map,
    }
    if args.dry_run:
        print(json.dumps(payload, indent=2))
        return
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    print(f"Wrote mapping: {args.output}")


if __name__ == "__main__":
    main()
