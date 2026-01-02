from pathlib import Path
import re

files = [
r"C:\Users\sasch\henoch\HENOCH-Exeget\22.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\23.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\24.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\25.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\26.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\27.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\28.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\29.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\30.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\31.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\32.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\33.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\34.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\35.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\36.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\37.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\38.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\39.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\40.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\41.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\42.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\43.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\44.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\45.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\46.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\47.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\48.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\49.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\50.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\51.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\52.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\53.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\54.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\55.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\56.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\57.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\58.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\59.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\60.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\61.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\62.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\63.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\64.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\65.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\66.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\67.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\68.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\69.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\70.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\71.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\72.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\73.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\74.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\75.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\76.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\77.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\78.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\79.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\80.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\81.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\82.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\83.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\84.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\85.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\86.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\87.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\88.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\89.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\89_2.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\90.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\91.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\92.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\93.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\94.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\95.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\96.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\97.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\98.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\99.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\100.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\101.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\102.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\103.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\104.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\105.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\106.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\107.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\108.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\1.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\2.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\3.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\4.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\5.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\6.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\7.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\8.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\9.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\10.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\11.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\12.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\13.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\14.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\15.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\16.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\17.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\18.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\19.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\20.txt",
r"C:\Users\sasch\henoch\HENOCH-Exeget\21.txt",
]

out_file = Path(r"C:\Users\sasch\henoch\HENOCH-Exeget\ALL_CLEAN.txt")

# Entfernt am Zeilenanfang z.B. "9:1 " oder "  9:10    "
pattern = re.compile(r"^\s*\d+\s*:\s*\d+\s+")

def read_text(p: Path) -> str:
    # UTF-8 versuchen, sonst Windows-1252 fallback (falls nötig)
    try:
        return p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return p.read_text(encoding="cp1252", errors="replace")

with out_file.open("w", encoding="utf-8", newline="\n") as out:
    for fp in files:
        p = Path(fp)
        if not p.exists():
            print(f"FEHLT: {p}")
            continue

        text = read_text(p)
        for line in text.splitlines():
            out.write(pattern.sub("", line) + "\n")

        out.write("\n")  # Leerzeile zwischen Dateien (optional)

print(f"Fertig: {out_file}")
