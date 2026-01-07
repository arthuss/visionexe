import argparse
import json
import os
import re
import sys
from pathlib import Path


DEFAULT_WIKI_CANDIDATE = Path(
    "C:/projects/my-selenium-scripts/advanced_web_scraper/data/raw/wiki"
)


def _resolve_wiki_root(args):
    if args.wiki_root:
        return Path(args.wiki_root)
    env_root = os.environ.get("RL_WIKI_ROOT")
    if env_root:
        return Path(env_root)
    if DEFAULT_WIKI_CANDIDATE.exists():
        return DEFAULT_WIKI_CANDIDATE
    return None


def _iter_html_files(root, contains, max_files):
    count = 0
    for path in root.rglob("*.html"):
        if contains and not any(token in path.name.lower() for token in contains):
            continue
        yield path
        count += 1
        if max_files and count >= max_files:
            break


def _add_symbol(bucket, key, entry, file_path, file_limit):
    item = bucket.get(key)
    if item is None:
        item = entry
        item["count"] = 0
        item["files"] = []
        bucket[key] = item
    item["count"] += 1
    if len(item["files"]) < file_limit:
        file_str = str(file_path)
        if file_str not in item["files"]:
            item["files"].append(file_str)


def parse_wiki_symbols(root, contains=None, max_files=None, file_limit=5):
    class_bucket = {}
    method_bucket = {}
    files_scanned = 0

    symbol_re = re.compile(r"RLPy\.([A-Za-z_][A-Za-z0-9_]*)(?:\.([A-Za-z_][A-Za-z0-9_]*))?")
    file_re = re.compile(r"RLPy_([A-Za-z0-9_]+)")

    for path in _iter_html_files(root, contains, max_files):
        files_scanned += 1
        text = path.read_text(encoding="utf-8", errors="ignore")

        match = file_re.search(path.stem)
        if match:
            class_name = match.group(1)
            _add_symbol(
                class_bucket,
                class_name,
                {"type": "class", "name": class_name, "source": "filename"},
                path,
                file_limit,
            )

        for cls, method in symbol_re.findall(text):
            _add_symbol(
                class_bucket,
                cls,
                {"type": "class", "name": cls, "source": "text"},
                path,
                file_limit,
            )
            if method:
                full = f"{cls}.{method}"
                _add_symbol(
                    method_bucket,
                    full,
                    {
                        "type": "method",
                        "name": full,
                        "class": cls,
                        "method": method,
                        "source": "text",
                    },
                    path,
                    file_limit,
                )

    return {
        "classes": class_bucket,
        "methods": method_bucket,
        "files_scanned": files_scanned,
    }


def parse_rlpy(path):
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    classes = {}
    functions = set()
    enums = set()

    current_class = None
    class_indent = None

    class_re = re.compile(r"^(\s*)class\s+([A-Za-z_][A-Za-z0-9_]*)")
    def_re = re.compile(r"^(\s*)def\s+([A-Za-z_][A-Za-z0-9_]*)")
    enum_re = re.compile(r"^([A-Z][A-Za-z0-9_]+)\s*=")

    for line in lines:
        if not line.strip():
            continue
        class_match = class_re.match(line)
        if class_match:
            indent = len(class_match.group(1))
            name = class_match.group(2)
            classes[name] = set()
            current_class = name
            class_indent = indent
            continue

        def_match = def_re.match(line)
        if def_match:
            indent = len(def_match.group(1))
            name = def_match.group(2)
            if current_class and class_indent is not None and indent > class_indent:
                classes[current_class].add(name)
            else:
                functions.add(name)
            continue

        if current_class and class_indent is not None:
            indent = len(line) - len(line.lstrip(" \t"))
            if indent <= class_indent and not line.lstrip().startswith("#"):
                current_class = None
                class_indent = None

        if current_class is None:
            enum_match = enum_re.match(line)
            if enum_match:
                enums.add(enum_match.group(1))

    return {
        "classes": classes,
        "functions": functions,
        "enums": enums,
    }


def write_jsonl(path, items):
    with path.open("w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


def build_report(wiki, rlpy, report_limit=200):
    wiki_classes = set(wiki["classes"].keys())
    wiki_methods = set(wiki["methods"].keys())

    rlpy_classes = set(rlpy["classes"].keys())
    rlpy_methods = set(
        f"{cls}.{method}"
        for cls, methods in rlpy["classes"].items()
        for method in methods
    )

    class_missing = sorted(wiki_classes - rlpy_classes)
    class_present = sorted(wiki_classes & rlpy_classes)
    method_missing = sorted(wiki_methods - rlpy_methods)
    method_present = sorted(wiki_methods & rlpy_methods)

    report = {
        "counts": {
            "wiki_classes": len(wiki_classes),
            "wiki_methods": len(wiki_methods),
            "rlpy_classes": len(rlpy_classes),
            "rlpy_methods": len(rlpy_methods),
            "rlpy_functions": len(rlpy["functions"]),
            "rlpy_enums": len(rlpy["enums"]),
            "files_scanned": wiki["files_scanned"],
        },
        "coverage": {
            "classes_present": len(class_present),
            "classes_missing": len(class_missing),
            "methods_present": len(method_present),
            "methods_missing": len(method_missing),
        },
        "samples": {
            "missing_classes": class_missing[:report_limit],
            "missing_methods": method_missing[:report_limit],
        },
    }
    return report, class_missing, method_missing


def write_markdown(path, report, class_missing, method_missing, report_limit=200):
    lines = []
    counts = report["counts"]
    coverage = report["coverage"]

    lines.append("# RLPy Wiki Compatibility Report")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- Wiki classes: {counts['wiki_classes']}")
    lines.append(f"- Wiki methods: {counts['wiki_methods']}")
    lines.append(f"- RLPy classes: {counts['rlpy_classes']}")
    lines.append(f"- RLPy methods: {counts['rlpy_methods']}")
    lines.append(f"- RLPy functions: {counts['rlpy_functions']}")
    lines.append(f"- RLPy enums: {counts['rlpy_enums']}")
    lines.append(f"- Files scanned: {counts['files_scanned']}")
    lines.append("")
    lines.append("## Coverage")
    lines.append(f"- Classes present: {coverage['classes_present']}")
    lines.append(f"- Classes missing: {coverage['classes_missing']}")
    lines.append(f"- Methods present: {coverage['methods_present']}")
    lines.append(f"- Methods missing: {coverage['methods_missing']}")
    lines.append("")
    lines.append("## Missing Classes (sample)")
    lines.extend(f"- {name}" for name in class_missing[:report_limit])
    lines.append("")
    lines.append("## Missing Methods (sample)")
    lines.extend(f"- {name}" for name in method_missing[:report_limit])
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Compare a Reallusion wiki HTML dump with local RLPy.py APIs."
    )
    parser.add_argument("--wiki-root", help="Path to the wiki HTML dump root.")
    parser.add_argument("--rlpy-path", help="Path to RLPy.py (iClone or CC4).")
    parser.add_argument("--output-dir", default=".", help="Directory for report outputs.")
    parser.add_argument(
        "--filename-contains",
        nargs="*",
        default=None,
        help="Only scan HTML files whose name contains any of these substrings.",
    )
    parser.add_argument("--max-files", type=int, default=0, help="Limit HTML files scanned.")
    parser.add_argument("--report-limit", type=int, default=200, help="Sample size for reports.")

    args = parser.parse_args()

    wiki_root = _resolve_wiki_root(args)
    if not wiki_root or not wiki_root.exists():
        print("Wiki root not found. Use --wiki-root or set RL_WIKI_ROOT.")
        return 2

    if not args.rlpy_path:
        print("Missing --rlpy-path for RLPy.py.")
        return 2

    rlpy_path = Path(args.rlpy_path)
    if not rlpy_path.exists():
        print(f"RLPy.py not found: {rlpy_path}")
        return 2

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    contains = None
    if args.filename_contains:
        contains = [token.lower() for token in args.filename_contains]

    max_files = args.max_files if args.max_files > 0 else None
    wiki = parse_wiki_symbols(wiki_root, contains, max_files)
    rlpy = parse_rlpy(rlpy_path)

    report, class_missing, method_missing = build_report(
        wiki, rlpy, report_limit=args.report_limit
    )

    wiki_jsonl = output_dir / "wiki_symbols.jsonl"
    rlpy_jsonl = output_dir / "rlpy_symbols.jsonl"
    report_json = output_dir / "compat_report.json"
    report_md = output_dir / "compat_report.md"

    wiki_items = list(wiki["classes"].values()) + list(wiki["methods"].values())
    write_jsonl(wiki_jsonl, wiki_items)

    rlpy_items = []
    for cls, methods in rlpy["classes"].items():
        rlpy_items.append({"type": "class", "name": cls})
        for method in sorted(methods):
            rlpy_items.append(
                {"type": "method", "name": f"{cls}.{method}", "class": cls, "method": method}
            )
    for name in sorted(rlpy["functions"]):
        rlpy_items.append({"type": "function", "name": name})
    for name in sorted(rlpy["enums"]):
        rlpy_items.append({"type": "enum", "name": name})
    write_jsonl(rlpy_jsonl, rlpy_items)

    report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(report_md, report, class_missing, method_missing, args.report_limit)

    print(f"Wrote: {wiki_jsonl}")
    print(f"Wrote: {rlpy_jsonl}")
    print(f"Wrote: {report_json}")
    print(f"Wrote: {report_md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
