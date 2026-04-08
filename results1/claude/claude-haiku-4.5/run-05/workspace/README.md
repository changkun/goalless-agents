# Snippit 📝

A lightweight, terminal-based code snippet manager. Save, organize, and retrieve code snippets with tagging and powerful search.

## Features

- **Simple Storage**: Snippets stored in `~/.snippits.json`
- **Rich Organization**: Tag snippets for easy categorization
- **Quick Search**: Search by name, tags, or code content
- **Language Support**: Track the language of each snippet
- **No Dependencies**: Pure Python, minimal external requirements
- **Timestamps**: Track when snippets were created and modified

## Installation

```bash
# Make executable
chmod +x snippit.py

# Symlink to PATH (optional)
sudo ln -s $(pwd)/snippit.py /usr/local/bin/snippit

# Or run directly
python3 snippit.py <command>
```

## Usage

### Add a snippet
```bash
snippit add "json-parse" 'JSON.parse(str)' --language js --tags json parsing
snippit add "py-dict" 'my_dict.get(key, default)' --language python --tags dict
```

### Retrieve a snippet
```bash
snippit get json-parse
snippit get json-parse --copy  # Copy to clipboard (requires pyperclip)
```

### Update a snippet
```bash
snippit update json-parse --code 'JSON.parse(input)'
snippit update json-parse --tags json parsing es6
```

### Delete a snippet
```bash
snippit delete json-parse
```

### List all snippets
```bash
snippit list                    # All snippets
snippit list --tag javascript   # Filter by tag
```

### Search
```bash
snippit search "parse"          # Search across all (name, tags, code)
snippit search "python" --type tags
snippit search "forEach" --type code
```

### Manage tags
```bash
snippit tags                    # List all tags with counts
```

## Data Format

Snippets are stored in JSON:

```json
{
  "json-parse": {
    "code": "JSON.parse(str)",
    "language": "javascript",
    "tags": ["json", "parsing"],
    "created": "2026-04-08T10:30:45.123456",
    "modified": "2026-04-08T10:35:12.654321"
  }
}
```

## Examples

```bash
# Store a React hook
snippit add "use-fetch" \
  'const [data, setData] = useState(null); useEffect(() => { fetch(url).then(r => r.json()).then(setData); }, [url]);' \
  --language jsx --tags react hooks fetch

# Search for React snippets
snippit search "react" --type tags

# Get your fetch hook
snippit get use-fetch

# Update it
snippit update use-fetch --code 'const [data, setData] = useState(null);...'
```

## Tips

- Use `--tags` or `-t` with multiple tags: `--tags python async database`
- Search is case-insensitive
- Snippet names are unique and case-sensitive
- Copy to clipboard requires: `pip install pyperclip`

## License

MIT
