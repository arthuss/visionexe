import argparse
import json
import sys
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE_ROOT))

from analysis.io import sha256_text  # noqa: E402
from analysis.validators import validate_payload  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "data" / "schemas" / "gez_morphology.schema.json"


def iter_json_files(input_path: Path) -> list[Path]:
    if input_path.is_file():
        return [input_path]
    return sorted([path for path in input_path.rglob("*.json") if path.is_file()])


def main() -> int:
    parser = argparse.ArgumentParser(description="Run audit tests on Ge'ez analysis artifacts.")
    parser.add_argument("--input", required=True, help="Input JSON file or folder.")
    parser.add_argument("--outdir", required=True, help="Output directory for test reports.")
    parser.add_argument("--validate", action="store_true", help="Validate artifacts against schema.")
    args = parser.parse_args()

    input_path = Path(args.input)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    summary = {"segments": []}

    for json_path in iter_json_files(input_path):
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        artifact_hash = sha256_text(json.dumps(payload, ensure_ascii=False))
        test_report = {
            "artifact": json_path.name,
            "reproducibility": {"hash": artifact_hash},
            "context_invariance": payload.get("tests", {}).get("context_invariance", {"status": "missing"}),
            "back_translation": payload.get("tests", {}).get("back_translation", {"status": "missing"}),
        }
        if args.validate:
            errors = validate_payload(payload, SCHEMA_PATH)
            test_report["validation"] = {"status": "ok" if not errors else "failed", "errors": errors}
        summary["segments"].append(test_report)

    (outdir / "tests_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
