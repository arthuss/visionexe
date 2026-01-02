# extract_json_fences_in_order.py
# Reads a CSV and extracts ```json ... ``` blocks from RawContent
# preserving CSV row order and block order. No JSON parsing is used for output.

import csv
import re
import json
from pathlib import Path

# --- CONFIG ---
INPUT_CSV = r"C:\Users\sasch\henoch\first_analysis_progress_python.csv"
RAW_COLUMN = "RawContent"
CHAPTER_COLUMN = "ChapterID"
STATUS_COLUMN = "Status"

# Output files (same folder as input)
OUTPUT_TXT_NAME = "extracted_json_blocks_in_order.txt"
VALIDATION_LOG_NAME = "json_validation_log.txt"

# Regex to capture contents between ```json and ```
JSON_FENCE_RE = re.compile(r"```json\s*(.*?)\s*```", re.DOTALL | re.IGNORECASE)


def extract_json_blocks_in_order(raw: str) -> list[str]:
    """Return JSON fence contents in the order they appear."""
    return JSON_FENCE_RE.findall(raw or "")


def unescape_csv_doubled_quotes(s: str) -> str:
    """
    Many CSV exports represent quotes inside a quoted cell as doubled quotes:
    ""title"" -> "title"
    This is ONLY used for validation parsing, not for output.
    """
    return (s or "").replace('""', '"')


def main() -> None:
    in_path = Path(INPUT_CSV)
    if not in_path.exists():
        raise FileNotFoundError(f"Input CSV not found: {in_path}")

    out_dir = in_path.parent
    out_txt = out_dir / OUTPUT_TXT_NAME
    val_log = out_dir / VALIDATION_LOG_NAME

    total_rows = 0
    total_blocks = 0
    validation_errors = []

    with in_path.open("r", encoding="utf-8", newline="") as f_in, \
         out_txt.open("w", encoding="utf-8", newline="\n") as f_out:

        reader = csv.DictReader(f_in)

        # Basic sanity check
        if reader.fieldnames is None:
            raise ValueError("CSV appears to have no header row.")
        if RAW_COLUMN not in reader.fieldnames:
            raise KeyError(f"Missing required column '{RAW_COLUMN}' in CSV header: {reader.fieldnames}")

        for row_idx, row in enumerate(reader, start=1):
            total_rows += 1

            chapter = row.get(CHAPTER_COLUMN, "")
            status = row.get(STATUS_COLUMN, "")
            raw = row.get(RAW_COLUMN, "")

            blocks = extract_json_blocks_in_order(raw)

            for block_idx, block in enumerate(blocks, start=1):
                total_blocks += 1

                # Write EXACT extracted content (no normalization)
                f_out.write(f"--- ChapterID={chapter} Status={status} Row={row_idx} Block={block_idx} ---\n")
                f_out.write(block)
                f_out.write("\n\n")

                # Validation only (does not affect output)
                try:
                    json.loads(unescape_csv_doubled_quotes(block))
                except Exception as e:
                    validation_errors.append(
                        f"Row={row_idx} Block={block_idx} ChapterID={chapter} Status={status} ERROR={e}"
                    )

    # Write validation log
    with val_log.open("w", encoding="utf-8", newline="\n") as f_log:
        f_log.write(f"Input: {in_path}\n")
        f_log.write(f"Rows processed: {total_rows}\n")
        f_log.write(f"JSON blocks extracted: {total_blocks}\n")
        f_log.write("\n")

        if not validation_errors:
            f_log.write("Validation: OK (all extracted blocks parsed after \"\" -> \" unescape)\n")
        else:
            f_log.write(f"Validation: FAIL ({len(validation_errors)} blocks could not be parsed)\n\n")
            for line in validation_errors:
                f_log.write(line + "\n")

    print("Done.")
    print(f"Extracted blocks (order preserved): {out_txt}")
    print(f"Validation log: {val_log}")
    print(f"Rows: {total_rows}, Blocks: {total_blocks}, Parse errors: {len(validation_errors)}")


if __name__ == "__main__":
    main()
