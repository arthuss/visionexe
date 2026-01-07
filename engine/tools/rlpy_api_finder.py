import argparse
import re
import sys
from pathlib import Path


def _compile_query(queries, use_regex):
    if not queries:
        return None
    if use_regex:
        return re.compile("|".join(queries), re.IGNORECASE)
    lowered = [q.lower() for q in queries]
    return lowered


def _match(line, query):
    if query is None:
        return False
    if isinstance(query, list):
        low = line.lower()
        return any(q in low for q in query)
    return bool(query.search(line))


def _list_symbols(lines, limit):
    classes = []
    funcs = []
    for line in lines:
        if line.startswith("class "):
            name = line.split()[1].split("(")[0].strip()
            classes.append(name)
        elif line.startswith("def "):
            name = line.split()[1].split("(")[0].strip()
            funcs.append(name)
    if limit:
        classes = classes[:limit]
        funcs = funcs[:limit]
    return classes, funcs


def search_file(path, queries, context, use_regex, list_symbols, limit):
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()

    if list_symbols:
        classes, funcs = _list_symbols(lines, limit)
        if classes:
            print("Classes:")
            for name in classes:
                print(f"  {name}")
        if funcs:
            print("Functions:")
            for name in funcs:
                print(f"  {name}")
        return 0

    query = _compile_query(queries, use_regex)
    if query is None:
        print("No query provided. Use --list-symbols or pass search terms.")
        return 2

    hits = 0
    for idx, line in enumerate(lines):
        if not _match(line, query):
            continue
        hits += 1
        start = max(0, idx - context)
        end = min(len(lines), idx + context + 1)
        for i in range(start, end):
            prefix = ">" if i == idx else " "
            print(f"{prefix} {path}:{i+1}: {lines[i]}")
        print("")

    if hits == 0:
        print("No matches.")
        return 1
    return 0


def main():
    parser = argparse.ArgumentParser(description="Quick search helper for Reallusion RLPy.py APIs.")
    parser.add_argument("path", help="Path to RLPy.py (CC4 or iClone).")
    parser.add_argument("query", nargs="*", help="Search terms or regex parts.")
    parser.add_argument("--regex", action="store_true", help="Treat queries as regex parts.")
    parser.add_argument("--context", type=int, default=0, help="Lines of context around matches.")
    parser.add_argument("--list-symbols", action="store_true", help="List class/function names instead of searching.")
    parser.add_argument("--limit", type=int, default=200, help="Limit for --list-symbols output.")

    args = parser.parse_args()
    path = Path(args.path)
    if not path.exists():
        print(f"Path not found: {path}")
        return 2

    return search_file(path, args.query, args.context, args.regex, args.list_symbols, args.limit)


if __name__ == "__main__":
    sys.exit(main())
