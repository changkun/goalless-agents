"""Core snippet manager with JSON-based storage."""
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional


def get_storage_path() -> Path:
    """Get the path to the snippets storage file."""
    data_dir = Path.home() / ".snip"
    data_dir.mkdir(exist_ok=True)
    return data_dir / "snippets.json"


def load_snippets() -> dict:
    """Load all snippets from storage."""
    path = get_storage_path()
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def save_snippets(snippets: dict) -> None:
    """Save snippets to storage."""
    path = get_storage_path()
    with open(path, "w") as f:
        json.dump(snippets, f, indent=2)


def add_snippet(
    name: str,
    code: str,
    language: Optional[str] = None,
    tags: Optional[list[str]] = None,
    description: Optional[str] = None,
) -> str:
    """Add a new snippet. Returns the snippet ID."""
    snippets = load_snippets()
    snippet_id = str(uuid.uuid4())[:8]

    snippets[snippet_id] = {
        "name": name,
        "code": code,
        "language": language or "text",
        "tags": tags or [],
        "description": description or "",
        "created": datetime.now().isoformat(),
        "updated": datetime.now().isoformat(),
    }

    save_snippets(snippets)
    return snippet_id


def get_snippet(identifier: str) -> Optional[dict]:
    """Get a snippet by ID or name."""
    snippets = load_snippets()

    # Try by ID first
    if identifier in snippets:
        return {"id": identifier, **snippets[identifier]}

    # Try by name
    for sid, data in snippets.items():
        if data["name"].lower() == identifier.lower():
            return {"id": sid, **data}

    return None


def delete_snippet(identifier: str) -> bool:
    """Delete a snippet by ID or name."""
    snippets = load_snippets()

    # Try by ID
    if identifier in snippets:
        del snippets[identifier]
        save_snippets(snippets)
        return True

    # Try by name
    for sid, data in snippets.items():
        if data["name"].lower() == identifier.lower():
            del snippets[sid]
            save_snippets(snippets)
            return True

    return False


def search_snippets(
    query: Optional[str] = None,
    tag: Optional[str] = None,
    language: Optional[str] = None,
) -> list[dict]:
    """Search snippets by query, tag, or language."""
    snippets = load_snippets()
    results = []

    for sid, data in snippets.items():
        match = True

        if query:
            query_lower = query.lower()
            searchable = f"{data['name']} {data['description']} {data['code']}".lower()
            if query_lower not in searchable:
                match = False

        if tag and tag.lower() not in [t.lower() for t in data.get("tags", [])]:
            match = False

        if language and data.get("language", "").lower() != language.lower():
            match = False

        if match:
            results.append({"id": sid, **data})

    return sorted(results, key=lambda x: x["updated"], reverse=True)


def list_all_snippets() -> list[dict]:
    """List all snippets."""
    return search_snippets()


def update_snippet(
    identifier: str,
    name: Optional[str] = None,
    code: Optional[str] = None,
    language: Optional[str] = None,
    tags: Optional[list[str]] = None,
    description: Optional[str] = None,
) -> bool:
    """Update an existing snippet."""
    snippets = load_snippets()
    target_id = None

    # Find by ID or name
    if identifier in snippets:
        target_id = identifier
    else:
        for sid, data in snippets.items():
            if data["name"].lower() == identifier.lower():
                target_id = sid
                break

    if not target_id:
        return False

    if name is not None:
        snippets[target_id]["name"] = name
    if code is not None:
        snippets[target_id]["code"] = code
    if language is not None:
        snippets[target_id]["language"] = language
    if tags is not None:
        snippets[target_id]["tags"] = tags
    if description is not None:
        snippets[target_id]["description"] = description

    snippets[target_id]["updated"] = datetime.now().isoformat()
    save_snippets(snippets)
    return True


def copy_to_clipboard(text: str) -> bool:
    """Copy text to clipboard. Returns True if successful."""
    try:
        import subprocess

        # Try different clipboard commands
        for cmd in [["xclip", "-selection", "clipboard"], ["pbcopy"], ["clip"]]:
            try:
                proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
                proc.communicate(text.encode())
                if proc.returncode == 0:
                    return True
            except FileNotFoundError:
                continue
        return False
    except Exception:
        return False


# Language to interpreter mapping
INTERPRETERS = {
    "python": ["python3", "python"],
    "python3": ["python3", "python"],
    "javascript": ["node"],
    "js": ["node"],
    "typescript": ["npx", "ts-node"],
    "ts": ["npx", "ts-node"],
    "ruby": ["ruby"],
    "perl": ["perl"],
    "php": ["php"],
    "lua": ["lua"],
    "bash": ["bash"],
    "sh": ["sh"],
    "shell": ["bash", "sh"],
    "zsh": ["zsh"],
    "fish": ["fish"],
}


def execute_snippet(identifier: str, extra_args: Optional[list[str]] = None) -> tuple[int, str, str]:
    """
    Execute a snippet and return (exit_code, stdout, stderr).

    Determines the interpreter based on the snippet's language.
    Shell languages run the code directly; others use temp files.
    """
    import subprocess
    import tempfile

    snippet = get_snippet(identifier)
    if not snippet:
        return (1, "", f"Snippet '{identifier}' not found")

    code = snippet["code"]
    language = snippet.get("language", "").lower()
    args = extra_args or []

    # Determine interpreter
    interpreters = INTERPRETERS.get(language)
    if not interpreters:
        return (1, "", f"No interpreter configured for language '{language}'")

    # Find available interpreter
    interpreter = None
    for interp in interpreters:
        try:
            subprocess.run(["which", interp], capture_output=True, check=True)
            interpreter = interp
            break
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue

    if not interpreter:
        return (1, "", f"No interpreter found for '{language}'. Tried: {', '.join(interpreters)}")

    # Shell languages: run code via stdin
    if language in ("bash", "sh", "shell", "zsh", "fish"):
        try:
            result = subprocess.run(
                [interpreter] + args,
                input=code,
                capture_output=True,
                text=True,
            )
            return (result.returncode, result.stdout, result.stderr)
        except Exception as e:
            return (1, "", str(e))

    # Other languages: use temp file
    extensions = {
        "python": ".py", "python3": ".py",
        "javascript": ".js", "js": ".js",
        "typescript": ".ts", "ts": ".ts",
        "ruby": ".rb", "perl": ".pl", "php": ".php", "lua": ".lua",
    }
    ext = extensions.get(language, ".tmp")

    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=ext, delete=False) as f:
            f.write(code)
            temp_path = f.name

        # Handle special case for ts-node (npx ts-node)
        if interpreter == "npx":
            cmd = ["npx", "ts-node", temp_path] + args
        else:
            cmd = [interpreter, temp_path] + args

        result = subprocess.run(cmd, capture_output=True, text=True)

        # Clean up temp file
        import os
        os.unlink(temp_path)

        return (result.returncode, result.stdout, result.stderr)
    except Exception as e:
        return (1, "", str(e))
