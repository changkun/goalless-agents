"""File churn analysis — which files change most, and why."""

from .git import FileChurn
from .render import (
    BOLD, DIM, BRIGHT_WHITE, BRIGHT_YELLOW, BRIGHT_RED, BRIGHT_GREEN,
    BRIGHT_CYAN, YELLOW, GREEN, RED, RESET,
    c, bar, num, truncate, term_width,
)

# File extension → language display name
EXT_LANG: dict[str, str] = {
    "py": "Python", "js": "JavaScript", "ts": "TypeScript",
    "tsx": "TypeScript/React", "jsx": "JavaScript/React",
    "rs": "Rust", "go": "Go", "java": "Java", "kt": "Kotlin",
    "c": "C", "cpp": "C++", "h": "C/C++ Header", "hpp": "C++ Header",
    "rb": "Ruby", "php": "PHP", "swift": "Swift", "cs": "C#",
    "sh": "Shell", "bash": "Bash", "zsh": "Zsh", "fish": "Fish",
    "html": "HTML", "css": "CSS", "scss": "SCSS", "sass": "Sass",
    "json": "JSON", "yaml": "YAML", "yml": "YAML", "toml": "TOML",
    "md": "Markdown", "rst": "reStructuredText", "txt": "Text",
    "sql": "SQL", "graphql": "GraphQL", "proto": "Protobuf",
    "dockerfile": "Dockerfile", "tf": "Terraform", "hcl": "HCL",
    "r": "R", "jl": "Julia", "scala": "Scala", "ex": "Elixir",
    "exs": "Elixir Script", "erl": "Erlang", "clj": "Clojure",
    "lua": "Lua", "vim": "Vim Script", "el": "Emacs Lisp",
}


def language_of(path: str) -> str:
    name = path.rsplit("/", 1)[-1].lower()
    if name in ("dockerfile", "makefile", "cmakelists.txt"):
        return EXT_LANG.get(name, name.title())
    ext = name.rsplit(".", 1)[-1] if "." in name else ""
    return EXT_LANG.get(ext, ext.upper() if ext else "Other")


def render_churn(files: list[FileChurn], top_n: int = 15) -> list[str]:
    """Return lines for the file churn panel."""
    lines: list[str] = []
    if not files:
        lines.append(c(DIM, "  No file data available."))
        return lines

    max_changes = files[0].changes if files else 1
    width = term_width()
    path_width = max(20, width - 60)

    header = (
        f"  {'File':<{path_width}}  {'Changes':>8}  "
        f"{'++ Lines':>9}  {'-- Lines':>9}  {'Authors':>7}"
    )
    lines.append(c(DIM, header))
    lines.append(c(DIM, "  " + "─" * (width - 4)))

    for i, fc in enumerate(files[:top_n]):
        short_path = truncate(fc.path, path_width)
        churn_color = (
            BRIGHT_RED if fc.changes > max_changes * 0.7
            else (BRIGHT_YELLOW if fc.changes > max_changes * 0.3 else BRIGHT_WHITE)
        )
        lines.append(
            f"  {short_path:<{path_width}}"
            f"  {c(churn_color, f'{fc.changes:>8,}')}"
            f"  {c(BRIGHT_GREEN, f'+{fc.insertions:>8,}')}"
            f"  {c(BRIGHT_RED,   f'-{fc.deletions:>8,}')}"
            f"  {c(DIM, f'{len(fc.authors):>7}')}"
        )

    if len(files) > top_n:
        lines.append(
            c(DIM, f"\n  … and {len(files) - top_n:,} more files")
        )
    return lines


def render_language_breakdown(files: list[FileChurn], top_n: int = 10) -> list[str]:
    """Return lines for the language breakdown panel."""
    lang_changes: dict[str, int] = {}
    lang_lines: dict[str, int] = {}
    for fc in files:
        lang = language_of(fc.path)
        lang_changes[lang] = lang_changes.get(lang, 0) + fc.changes
        lang_lines[lang] = lang_lines.get(lang, 0) + fc.insertions + fc.deletions

    if not lang_changes:
        return [c(DIM, "  No language data.")]

    sorted_langs = sorted(lang_changes.items(), key=lambda x: x[1], reverse=True)
    max_changes = sorted_langs[0][1]
    total = sum(v for _, v in sorted_langs)

    lines: list[str] = []
    for lang, changes in sorted_langs[:top_n]:
        pct = changes / total * 100
        bar_str = bar(changes, max_changes, width=25)
        lines.append(
            f"  {c(BRIGHT_WHITE, f'{lang:<22}')}"
            f"  {bar_str}"
            f"  {c(DIM, f'{changes:>6,} changes')}  "
            f"{c(BRIGHT_CYAN, f'{pct:5.1f}%')}"
        )
    return lines
