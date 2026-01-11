import argparse
import json
import sys
from pathlib import Path


ENGINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE_ROOT))

from analysis.rules.rule_engine import RuleConfig, apply_rules


DEFAULT_TAGSET_PATH = ENGINE_ROOT / "analysis" / "tagsets" / "gez_pos_1.json"
DEFAULT_FUNCTION_WORDS_PATH = ENGINE_ROOT / "config" / "gez_function_words.json"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def parse_json_payload(text: str) -> dict | None:
    if not text:
        return None
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    candidate = text[start:end + 1]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        return None


def apply_morphology_filters(
    payload: dict,
    tagset_data: dict | None = None,
    function_words_data: dict | None = None,
    drop_ruled_out: bool = False,
    allow_unattested: bool = False,
) -> tuple[dict, dict]:
    tagset_data = tagset_data or load_json(DEFAULT_TAGSET_PATH)
    if function_words_data:
        tagset_data = dict(tagset_data)
        tagset_data["function_words"] = function_words_data.get("function_words", [])

    config = RuleConfig(
        allow_unattested=allow_unattested,
        drop_ruled_out=drop_ruled_out,
    )
    return apply_rules(payload, tagset_data=tagset_data, config=config)


def main() -> int:
    parser = argparse.ArgumentParser(description="Filter Ge'ez morphology JSON with rule-based constraints.")
    parser.add_argument("--input", required=True, help="Input JSON file (use '-' for stdin).")
    parser.add_argument("--output", required=True, help="Output JSON file (use '-' for stdout).")
    parser.add_argument("--report", help="Optional JSON report output path.")
    parser.add_argument("--tagset", default=str(DEFAULT_TAGSET_PATH), help="POS tagset JSON path.")
    parser.add_argument("--function-words", default=str(DEFAULT_FUNCTION_WORDS_PATH), help="Function word list JSON path.")
    parser.add_argument("--drop-ruled-out", action="store_true", help="Drop ruled-out options instead of marking.")
    parser.add_argument("--allow-unattested", action="store_true", help="Keep unattested options (downgrade only).")
    args = parser.parse_args()

    if args.input == "-":
        raw_text = sys.stdin.read()
        payload = parse_json_payload(raw_text)
        if payload is None:
            print("Failed to parse JSON from stdin.", file=sys.stderr)
            return 1
    else:
        payload = load_json(Path(args.input))

    tagset_data = load_json(Path(args.tagset))
    function_words_data = load_json(Path(args.function_words)) if args.function_words else None

    filtered, report = apply_morphology_filters(
        payload,
        tagset_data=tagset_data,
        function_words_data=function_words_data,
        drop_ruled_out=args.drop_ruled_out,
        allow_unattested=args.allow_unattested,
    )

    output_text = json.dumps(filtered, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(output_text)
    else:
        Path(args.output).write_text(output_text, encoding="utf-8")

    if args.report:
        report_text = json.dumps(report, ensure_ascii=False, indent=2)
        Path(args.report).write_text(report_text, encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
