import argparse
import json
import sys
from pathlib import Path


ENGINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE_ROOT))

from analysis.io import load_json, save_json  # noqa: E402
from analysis.rules.rule_engine import RuleConfig, apply_rules  # noqa: E402


TAGSET_PATH = ENGINE_ROOT / "analysis" / "tagsets" / "gez_pos_1.json"


def iter_json_files(input_path: Path) -> list[Path]:
    if input_path.is_file():
        return [input_path]
    return sorted([path for path in input_path.rglob("*.json") if path.is_file()])


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply rule-based morphology filters to JSON artifacts.")
    parser.add_argument("--input", required=True, help="Input JSON file or folder.")
    parser.add_argument("--outdir", required=True, help="Output directory for filtered JSON.")
    parser.add_argument("--report-dir", help="Output directory for rule reports (default: outdir/reports).")
    parser.add_argument("--allow-unattested", action="store_true", help="Downgrade unattested options instead of rule out.")
    parser.add_argument("--drop-ruled-out", action="store_true", help="Drop ruled-out options from output.")
    parser.add_argument("--tagset", default=str(TAGSET_PATH), help="POS tagset JSON path.")
    args = parser.parse_args()

    input_path = Path(args.input)
    outdir = Path(args.outdir)
    report_dir = Path(args.report_dir) if args.report_dir else outdir / "reports"

    tagset_path = Path(args.tagset)
    config = RuleConfig(allow_unattested=args.allow_unattested, drop_ruled_out=args.drop_ruled_out)

    for json_path in iter_json_files(input_path):
        payload = load_json(json_path)
        filtered, report = apply_rules(payload, tagset_path=tagset_path, config=config)

        rel = json_path.name if input_path.is_file() else json_path.relative_to(input_path)
        output_path = outdir / rel
        report_path = report_dir / rel.with_suffix(".filter_report.json")
        save_json(output_path, filtered)
        save_json(report_path, report)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
