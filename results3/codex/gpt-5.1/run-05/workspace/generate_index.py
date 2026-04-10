import argparse
import html
from pathlib import Path
from typing import List, Tuple


def find_markdown_files(root: Path) -> List[Path]:
    return sorted(p for p in root.glob("*.md") if p.is_file())


def extract_title(markdown_text: str, fallback: str) -> str:
    for line in markdown_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            # Take everything after leading hashes and whitespace
            heading = stripped.lstrip("#").strip()
            if heading:
                return heading
    return fallback


def build_index_entries(files: List[Path]) -> List[Tuple[str, str]]:
    entries: List[Tuple[str, str]] = []
    for path in files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        fallback_title = path.stem.replace("_", " ").replace("-", " ").title()
        title = extract_title(text, fallback=fallback_title)
        entries.append((title, path.name))
    return entries


def render_html(entries: List[Tuple[str, str]], title: str = "Markdown Index") -> str:
    items_html = "\n".join(
        f'      <li><a href="{html.escape(filename)}">{html.escape(entry_title)}</a></li>'
        for entry_title, filename in entries
    )
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>{html.escape(title)}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
      body {{
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        max-width: 42rem;
        margin: 2rem auto;
        padding: 0 1rem;
        line-height: 1.5;
      }}
      h1 {{
        font-size: 1.8rem;
        margin-bottom: 1rem;
      }}
      ul {{
        list-style: none;
        padding: 0;
      }}
      li + li {{
        margin-top: 0.4rem;
      }}
      a {{
        text-decoration: none;
        color: #0b66d6;
      }}
      a:hover {{
        text-decoration: underline;
      }}
    </style>
  </head>
  <body>
    <h1>{html.escape(title)}</h1>
    <ul>
{items_html}
    </ul>
  </body>
</html>
"""


def generate_index(directory: Path, output: Path) -> None:
    files = find_markdown_files(directory)
    entries = build_index_entries(files)
    html_text = render_html(entries)
    output.write_text(html_text, encoding="utf-8")


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate an index.html page listing Markdown files in a directory."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to scan for .md files (default: current directory).",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="index.html",
        help="Output HTML file path (default: index.html).",
    )
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> None:
    args = parse_args(argv)
    directory = Path(args.directory).resolve()
    output = Path(args.output)
    generate_index(directory, output)


if __name__ == "__main__":
    main()

