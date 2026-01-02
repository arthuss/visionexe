import os
import json
import argparse
import time
import uuid
import wave
import shutil
import urllib.request
import urllib.error

DEFAULT_ENDPOINT = "http://127.0.0.1:7861"
DEFAULT_MODEL_ID = "stabilityai/stable-audio-open-1.0"
DEFAULT_FN_INDEX = 0
DEFAULT_STEPS = 50
DEFAULT_CFG_SCALE_SRC = 1.0
DEFAULT_CFG_SCALE_TAR = 12.0
DEFAULT_T_START = 45.0
DEFAULT_TIMEOUT_SEC = 900


def load_payload(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_dynamic_edits(payload):
    if isinstance(payload, dict):
        if "edits" in payload and isinstance(payload["edits"], list):
            return payload["edits"]
        if "zeta_dynamic_edits" in payload:
            nested = payload["zeta_dynamic_edits"]
            if isinstance(nested, dict) and "edits" in nested:
                return nested["edits"]
            if isinstance(nested, list):
                return nested
    if isinstance(payload, list):
        return payload
    return []


def extract_spot_edits(payload):
    if not isinstance(payload, dict):
        return []
    spot = payload.get("spot_fx")
    if not isinstance(spot, dict):
        return []
    injections = spot.get("object_injections")
    if not isinstance(injections, list):
        return []
    edits = []
    for item in injections:
        if not isinstance(item, dict):
            continue
        prompt = item.get("prompt")
        if not prompt:
            continue
        edit = {"prompt": prompt}
        if "t_start" in item:
            edit["t_start"] = item.get("t_start")
        if "t_start_sec" in item:
            edit["t_start_sec"] = item.get("t_start_sec")
        if "timestamp" in item:
            edit["timestamp"] = item.get("timestamp")
        if "guidance" in item:
            edit["guidance"] = item.get("guidance")
        if "duration" in item:
            edit["duration"] = item.get("duration")
        edits.append(edit)
    return edits


def get_audio_duration_sec(path):
    try:
        with wave.open(path, "rb") as wav:
            frames = wav.getnframes()
            rate = wav.getframerate()
        if rate == 0:
            return None
        return frames / float(rate)
    except wave.Error:
        return None
    except OSError:
        return None


def parse_timestamp(value):
    if not value:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        parts = value.split(":")
        if len(parts) == 1:
            try:
                return float(parts[0])
            except ValueError:
                return None
        if len(parts) == 2:
            try:
                minutes = float(parts[0])
                seconds = float(parts[1])
                return minutes * 60.0 + seconds
            except ValueError:
                return None
    return None


def compute_t_start_percent(edit, duration_sec, default_percent):
    if isinstance(edit, dict):
        if "t_start" in edit:
            try:
                return float(edit["t_start"])
            except (TypeError, ValueError):
                pass
        if "t_start_sec" in edit:
            t_start_sec = parse_timestamp(edit.get("t_start_sec"))
            if t_start_sec is not None and duration_sec:
                return max(0.0, min(100.0, (t_start_sec / duration_sec) * 100.0))
        if "timestamp" in edit:
            t_start_sec = parse_timestamp(edit.get("timestamp"))
            if t_start_sec is not None and duration_sec:
                return max(0.0, min(100.0, (t_start_sec / duration_sec) * 100.0))
    return default_percent


def compute_sort_value(edit, duration_sec, default_percent):
    if isinstance(edit, dict):
        t_start_sec = parse_timestamp(edit.get("t_start_sec"))
        if t_start_sec is None:
            t_start_sec = parse_timestamp(edit.get("timestamp"))
        if t_start_sec is not None:
            return t_start_sec
        if "t_start" in edit:
            try:
                percent = float(edit.get("t_start"))
                if duration_sec:
                    return (percent / 100.0) * duration_sec
            except (TypeError, ValueError):
                pass
    if duration_sec:
        return duration_sec + 999.0
    return default_percent + 999.0


def build_payload(
    audio_path,
    model_id,
    do_inversion,
    source_prompt,
    target_prompt,
    steps,
    cfg_scale_src,
    cfg_scale_tar,
    t_start,
    randomize_seed,
    save_compute,
    fn_index,
):
    data = [
        audio_path,
        model_id,
        do_inversion,
        None,
        None,
        None,
        None,
        source_prompt or "",
        target_prompt,
        steps,
        cfg_scale_src,
        cfg_scale_tar,
        t_start,
        randomize_seed,
        save_compute,
    ]
    return {"data": data, "fn_index": fn_index}


def post_json(url, payload, timeout_sec):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout_sec) as response:
        body = response.read().decode("utf-8")
        return json.loads(body)


def queue_join(endpoint, payload, timeout_sec):
    session_hash = uuid.uuid4().hex
    payload["session_hash"] = session_hash
    response = post_json(f"{endpoint}/queue/join", payload, timeout_sec)
    if isinstance(response, dict) and response.get("hash"):
        return response["hash"]
    return session_hash


def poll_queue(endpoint, hash_value, timeout_sec):
    url = f"{endpoint}/queue/data?hash={hash_value}"
    with urllib.request.urlopen(url, timeout=timeout_sec) as response:
        for raw_line in response:
            line = raw_line.decode("utf-8").strip()
            if not line.startswith("data:"):
                continue
            data = line[len("data:"):].strip()
            if not data or data == "null":
                continue
            try:
                payload = json.loads(data)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                if payload.get("status") == "complete" and "data" in payload:
                    return payload["data"]
                if payload.get("data") and payload.get("success", True):
                    return payload["data"]
            if isinstance(payload, list):
                return payload
    return None


def call_predict(endpoint, payload, use_queue, timeout_sec):
    if use_queue:
        hash_value = queue_join(endpoint, payload, timeout_sec)
        return poll_queue(endpoint, hash_value, timeout_sec)
    response = post_json(f"{endpoint}/api/predict", payload, timeout_sec)
    if isinstance(response, dict):
        return response.get("data")
    return response


def extract_output_path(result_data):
    if isinstance(result_data, dict) and "data" in result_data:
        return extract_output_path(result_data["data"])
    if isinstance(result_data, list) and result_data:
        first = result_data[0]
        if isinstance(first, dict):
            return first.get("name") or first.get("path")
        if isinstance(first, str):
            return first
    if isinstance(result_data, str):
        return result_data
    return None


def build_step_output(output_path, index, total):
    if index == total - 1:
        return output_path
    root, ext = os.path.splitext(output_path)
    if not ext:
        ext = ".wav"
    return f"{root}_step{index + 1:02d}{ext}"


def run(
    base_track,
    edits_file,
    output_path,
    endpoint,
    model_id,
    fn_index,
    steps,
    cfg_scale_src,
    cfg_scale_tar,
    default_t_start,
    source_prompt,
    do_inversion,
    randomize_seed,
    save_compute,
    use_queue,
    timeout_sec,
    max_edits,
    include_spot,
    sort_edits,
    dry_run,
):
    if not os.path.exists(base_track):
        print(f"Fehler: Base track nicht gefunden: {base_track}")
        return
    if not os.path.exists(edits_file):
        print(f"Fehler: Edits JSON nicht gefunden: {edits_file}")
        return

    payload = load_payload(edits_file)
    edits = extract_dynamic_edits(payload)
    if include_spot:
        edits.extend(extract_spot_edits(payload))

    if not edits:
        print("Warnung: Keine edits gefunden.")
        return

    if max_edits:
        edits = edits[:max_edits]

    duration_sec = get_audio_duration_sec(base_track) or 60.0
    current_audio = base_track
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if sort_edits and duration_sec:
        edits = sorted(edits, key=lambda e: compute_sort_value(e, duration_sec, default_t_start))

    for idx, edit in enumerate(edits):
        target_prompt = ""
        if isinstance(edit, dict):
            target_prompt = edit.get("prompt", "")
            if edit.get("guidance") is not None:
                try:
                    cfg_scale_tar = float(edit.get("guidance"))
                except (TypeError, ValueError):
                    pass
        if not target_prompt:
            print(f"Warnung: Edit {idx + 1} ohne Prompt. Ueberspringe.")
            continue

        t_start = compute_t_start_percent(edit, duration_sec, default_t_start)
        payload = build_payload(
            audio_path=current_audio,
            model_id=model_id,
            do_inversion=do_inversion,
            source_prompt=source_prompt,
            target_prompt=target_prompt,
            steps=steps,
            cfg_scale_src=cfg_scale_src,
            cfg_scale_tar=cfg_scale_tar,
            t_start=t_start,
            randomize_seed=randomize_seed,
            save_compute=save_compute,
            fn_index=fn_index,
        )

        step_output = build_step_output(output_path, idx, len(edits))
        if dry_run:
            print(f"Edit {idx + 1}/{len(edits)} -> {step_output}")
            print(json.dumps(payload, indent=2))
            current_audio = step_output
            continue

        try:
            result_data = call_predict(endpoint, payload, use_queue, timeout_sec)
        except (urllib.error.URLError, urllib.error.HTTPError) as exc:
            print(f"ZETA API Fehler: {exc}")
            return

        output_candidate = extract_output_path(result_data)
        if output_candidate and os.path.exists(output_candidate):
            shutil.copy(output_candidate, step_output)
            current_audio = step_output
            print(f"Saved: {step_output}")
        elif output_candidate:
            print(f"ZETA Output: {output_candidate}")
            current_audio = output_candidate
        else:
            print("Warnung: Kein Output vom ZETA Endpoint.")
            return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run ZETA audio edits.")
    parser.add_argument("--base-track", required=True, help="Path to chapter_XXX_bgm_base.wav")
    parser.add_argument("--edits-file", required=True, help="JSON file with ZETA edits")
    parser.add_argument("--output", required=True, help="Output path for zeta master wav")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    parser.add_argument("--fn-index", type=int, default=DEFAULT_FN_INDEX)
    parser.add_argument("--steps", type=int, default=DEFAULT_STEPS)
    parser.add_argument("--cfg-scale-src", type=float, default=DEFAULT_CFG_SCALE_SRC)
    parser.add_argument("--cfg-scale-tar", type=float, default=DEFAULT_CFG_SCALE_TAR)
    parser.add_argument("--default-t-start", type=float, default=DEFAULT_T_START)
    parser.add_argument("--source-prompt", default="")
    parser.add_argument("--no-inversion", action="store_true")
    parser.add_argument("--randomize-seed", action="store_true")
    parser.add_argument("--no-save-compute", action="store_true")
    parser.add_argument("--no-queue", action="store_true")
    parser.add_argument("--timeout-sec", type=int, default=DEFAULT_TIMEOUT_SEC)
    parser.add_argument("--max-edits", type=int, default=0)
    parser.add_argument("--no-spot", action="store_true")
    parser.add_argument("--no-sort", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    run(
        base_track=args.base_track,
        edits_file=args.edits_file,
        output_path=args.output,
        endpoint=args.endpoint,
        model_id=args.model_id,
        fn_index=args.fn_index,
        steps=args.steps,
        cfg_scale_src=args.cfg_scale_src,
        cfg_scale_tar=args.cfg_scale_tar,
        default_t_start=args.default_t_start,
        source_prompt=args.source_prompt,
        do_inversion=not args.no_inversion,
        randomize_seed=args.randomize_seed,
        save_compute=not args.no_save_compute,
        use_queue=not args.no_queue,
        timeout_sec=args.timeout_sec,
        max_edits=args.max_edits or None,
        include_spot=not args.no_spot,
        sort_edits=not args.no_sort,
        dry_run=args.dry_run,
    )
