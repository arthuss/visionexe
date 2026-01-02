"""
Fetches the Ethiopic text of 1 Enoch from pseudepigrapha.org and splits it
into per-chapter files.

The site uses an expired certificate, so SSL verification is disabled on
purpose. The script grabs a session cookie via the main text page, then
requests a large section that covers all available Ethiopic chapters.

Outputs: ./ethiopic_1enoch_p/chapter_XX.txt (UTF-8, verse-per-line).
"""

from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
import http.cookiejar
import ssl
import urllib.request


TEXT_URL = "https://pseudepigrapha.org/docs/text/1En"
SECTION_URL = (
    "https://pseudepigrapha.org/docs/section.load/1En"
    "?version=Ethiopic&type=p&from=1-1-&to=120-200-"
)
OUTPUT_DIR = Path("ethiopic_1enoch_p")


class EthiopicParser(HTMLParser):
    """Parses the Ethiopic text within the textframe div."""

    def __init__(self) -> None:
        super().__init__()
        self.in_textframe = False
        self.pending_marker: str | None = None
        self.capture_depth = 0
        self.current_chapter: int | None = None
        self.current_verse: int | None = None
        self.verses: dict[int, dict[int, list[str]]] = defaultdict(
            lambda: defaultdict(list)
        )

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_dict = dict(attrs)
        if tag == "div" and attr_dict.get("id") == "textframe0":
            self.in_textframe = True

        if not self.in_textframe:
            return

        classes = set((attr_dict.get("class") or "").split())
        if tag == "span" and "refmarker_0" in classes:
            self.pending_marker = "chapter"
        elif tag == "span" and "refmarker_1" in classes:
            self.pending_marker = "verse"

        if "Ethiopic" in classes:
            self.capture_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "div" and self.in_textframe:
            self.in_textframe = False

        if self.capture_depth and tag in {"span", "a"}:
            self.capture_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self.in_textframe:
            return

        if self.pending_marker:
            stripped = data.strip()
            if stripped:
                number = int(stripped)
                if self.pending_marker == "chapter":
                    self.current_chapter = number
                else:
                    self.current_verse = number
                self.pending_marker = None
            return

        if (
            self.capture_depth > 0
            and self.current_chapter is not None
            and self.current_verse is not None
        ):
            self.verses[self.current_chapter][self.current_verse].append(data)


def fetch_html() -> str:
    """Retrieve the combined section HTML with a cookie-aware opener."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    cookies = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPSHandler(context=ctx),
        urllib.request.HTTPCookieProcessor(cookies),
    )
    opener.addheaders = [
        ("User-Agent", "codex-script/1.0 (+https://pseudepigrapha.org)")
    ]

    # Prime the session to get a cookie.
    opener.open(TEXT_URL)
    with opener.open(SECTION_URL) as resp:
        return resp.read().decode("utf-8")


def write_chapter_files(verses: dict[int, dict[int, list[str]]]) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    for chapter in sorted(verses):
        lines: list[str] = []
        for verse in sorted(verses[chapter]):
            text = "".join(verses[chapter][verse]).strip()
            lines.append(f"{chapter}:{verse} {text}")
        outfile = OUTPUT_DIR / f"chapter_{chapter:02d}.txt"
        outfile.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    html = fetch_html()
    parser = EthiopicParser()
    parser.feed(html)
    write_chapter_files(parser.verses)


if __name__ == "__main__":
    main()
