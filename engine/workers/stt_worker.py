import argparse
import json
import os
import time
from difflib import SequenceMatcher

SUPPORTED_EXTS = (".wav", ".mp3", ".m4a", ".flac", ".ogg", ".aac")


def normalize_text(text: str) -> str:
    return " ".join((text or "").strip().lower().split())


def levenshtein_distance(ref_words, hyp_words):
    rows = len(ref_words) + 1
    cols = len(hyp_words) + 1
    matrix = [[0] * cols for _ in range(rows)]

    for i in range(rows):
        matrix[i][0] = i
    for j in range(cols):
        matrix[0][j] = j

    for i in range(1, rows):
        for j in range(1, cols):
            cost = 0 if ref_words[i - 1] == hyp_words[j - 1] else 1
            matrix[i][j] = min(
                matrix[i - 1][j] + 1,
                matrix[i][j - 1] + 1,
                matrix[i - 1][j - 1] + cost,
            )
    return matrix[-1][-1]


def compute_metrics(reference: str, hypothesis: str) -> dict:
    ref_norm = normalize_text(reference)
    hyp_norm = normalize_text(hypothesis)
    similarity = SequenceMatcher(None, ref_norm, hyp_norm).ratio() if ref_norm or hyp_norm else 0.0
    ref_words = ref_norm.split()
    hyp_words = hyp_norm.split()
    distance = levenshtein_distance(ref_words, hyp_words) if ref_words or hyp_words else 0
    wer = float(distance) / float(len(ref_words)) if ref_words else 0.0
    return {
        "similarity": similarity,
        "wer": wer,
        "word_distance": distance,
        "word_count": len(ref_words),
    }


def load_model(model_name: str, device: str):
    try:
        import whisper
    except ImportError as exc:
        raise RuntimeError("whisper is not installed. pip install openai-whisper") from exc
    return whisper.load_model(model_name, device=device)


def detect_device(preferred: str) -> str:
    if preferred:
        return preferred
    try:
        import torch
        return "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:
        return "cpu"


def transcribe(model, audio_path: str, language: str | None, device: str) -> dict:
    options = {
        "fp16": device == "cuda",
    }
    if language:
        options["language"] = language
    result = model.transcribe(audio_path, **options)
    return result


def iter_audio_files(audio_dir: str):
    for name in sorted(os.listdir(audio_dir)):
        if name.lower().endswith(SUPPORTED_EXTS):
            yield os.path.join(audio_dir, name)


def write_output(payload: dict, output_path: str):
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Transcribe audio with Whisper and compute similarity/WER.")
    parser.add_argument("--audio", help="Audio file path")
    parser.add_argument("--audio-dir", help="Directory of audio files")
    parser.add_argument("--output-dir", help="Output directory for JSON results")
    parser.add_argument("--reference", help="Reference text (inline)")
    parser.add_argument("--reference-file", help="Path to reference text file")
    parser.add_argument("--model", default="small", help="Whisper model size or name")
    parser.add_argument("--language", help="Language code override (e.g. de)")
    parser.add_argument("--device", help="Device override (cuda/cpu)")
    parser.add_argument("--save-text", action="store_true", help="Write transcript text file alongside JSON")
    args = parser.parse_args()

    if not args.audio and not args.audio_dir:
        parser.error("Provide --audio or --audio-dir")

    reference = args.reference
    if args.reference_file:
        try:
            with open(args.reference_file, "r", encoding="utf-8", errors="replace") as handle:
                reference = handle.read()
        except OSError:
            reference = reference or ""

    device = detect_device(args.device)
    model = load_model(args.model, device)

    if args.audio_dir:
        audio_files = list(iter_audio_files(args.audio_dir))
    else:
        audio_files = [args.audio]

    output_dir = args.output_dir or (args.audio_dir if args.audio_dir else os.path.dirname(args.audio) or ".")
    os.makedirs(output_dir, exist_ok=True)

    for audio_path in audio_files:
        result = transcribe(model, audio_path, args.language, device)
        transcript = (result.get("text") or "").strip()
        metrics = compute_metrics(reference, transcript) if reference else None

        payload = {
            "generated_at": int(time.time()),
            "audio": audio_path,
            "model": args.model,
            "device": device,
            "language": result.get("language") or args.language,
            "text": transcript,
            "segments": result.get("segments", []),
        }
        if metrics:
            payload["metrics"] = metrics
        if reference:
            payload["reference"] = reference

        base = os.path.splitext(os.path.basename(audio_path))[0]
        output_path = os.path.join(output_dir, f"{base}_stt.json")
        write_output(payload, output_path)
        if args.save_text:
            text_path = os.path.join(output_dir, f"{base}_stt.txt")
            with open(text_path, "w", encoding="utf-8") as handle:
                handle.write(transcript)
        print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
