"""Display and formatting utilities with optional syntax highlighting."""
import sys
from datetime import datetime

# ANSI color codes
COLORS = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "bg_gray": "\033[48;5;236m",
}


def supports_color() -> bool:
    """Check if the terminal supports color."""
    if not hasattr(sys.stdout, "isatty"):
        return False
    if not sys.stdout.isatty():
        return False
    return True


def colorize(text: str, *styles: str) -> str:
    """Apply color/style to text if terminal supports it."""
    if not supports_color():
        return text
    codes = "".join(COLORS.get(s, "") for s in styles)
    return f"{codes}{text}{COLORS['reset']}"


def print_error(msg: str) -> None:
    """Print an error message."""
    print(colorize(f"Error: {msg}", "red"), file=sys.stderr)


def print_success(msg: str) -> None:
    """Print a success message."""
    print(colorize(msg, "green"))


def format_time_ago(iso_time: str) -> str:
    """Format an ISO timestamp as a relative time."""
    try:
        dt = datetime.fromisoformat(iso_time)
        now = datetime.now()
        diff = now - dt

        if diff.days > 365:
            years = diff.days // 365
            return f"{years}y ago"
        elif diff.days > 30:
            months = diff.days // 30
            return f"{months}mo ago"
        elif diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours}h ago"
        elif diff.seconds > 60:
            mins = diff.seconds // 60
            return f"{mins}m ago"
        else:
            return "just now"
    except Exception:
        return iso_time[:10]


def highlight_code(code: str, language: str) -> str:
    """Apply syntax highlighting to code if pygments is available."""
    try:
        from pygments import highlight
        from pygments.formatters import Terminal256Formatter
        from pygments.lexers import get_lexer_by_name, guess_lexer

        try:
            lexer = get_lexer_by_name(language)
        except Exception:
            try:
                lexer = guess_lexer(code)
            except Exception:
                return code

        formatter = Terminal256Formatter(style="monokai")
        return highlight(code, lexer, formatter).rstrip()
    except ImportError:
        # Pygments not installed, return plain code
        return code


def format_snippet(snippet: dict) -> str:
    """Format a single snippet for detailed display."""
    lines = []

    # Header
    name = colorize(snippet["name"], "bold", "cyan")
    sid = colorize(f"[{snippet['id']}]", "dim")
    lines.append(f"{name} {sid}")

    # Metadata line
    meta_parts = []
    if snippet.get("language"):
        meta_parts.append(colorize(snippet["language"], "yellow"))
    if snippet.get("tags"):
        tags = " ".join(colorize(f"#{t}", "magenta") for t in snippet["tags"])
        meta_parts.append(tags)
    meta_parts.append(colorize(format_time_ago(snippet["updated"]), "dim"))

    if meta_parts:
        lines.append(" ".join(meta_parts))

    # Description
    if snippet.get("description"):
        lines.append(colorize(snippet["description"], "dim"))

    lines.append("")

    # Code block
    code = snippet["code"]
    if supports_color():
        code = highlight_code(code, snippet.get("language", "text"))

    # Add border/background effect
    code_lines = code.split("\n")
    for line in code_lines:
        lines.append(f"  {line}")

    return "\n".join(lines)


def format_snippet_list(snippets: list[dict]) -> str:
    """Format a list of snippets for overview display."""
    if not snippets:
        return "No snippets found."

    lines = []
    max_name_len = min(30, max(len(s["name"]) for s in snippets))
    max_lang_len = min(12, max(len(s.get("language", "")) for s in snippets))

    for s in snippets:
        sid = colorize(s["id"], "dim")
        name = colorize(s["name"].ljust(max_name_len)[:max_name_len], "cyan")
        lang = colorize((s.get("language") or "").ljust(max_lang_len)[:max_lang_len], "yellow")
        time_ago = colorize(format_time_ago(s["updated"]).rjust(8), "dim")

        tags = ""
        if s.get("tags"):
            tags = " " + " ".join(colorize(f"#{t}", "magenta") for t in s["tags"][:3])

        preview = s["code"].split("\n")[0][:40]
        if len(s["code"].split("\n")) > 1 or len(s["code"]) > 40:
            preview += "..."
        preview = colorize(preview, "dim")

        lines.append(f"{sid}  {name}  {lang}  {time_ago}{tags}")
        lines.append(f"        {preview}")
        lines.append("")

    # Summary
    lines.append(colorize(f"({len(snippets)} snippet{'s' if len(snippets) != 1 else ''})", "dim"))

    return "\n".join(lines)
