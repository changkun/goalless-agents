# Snip - CLI Code Snippet Manager

Save, search, and retrieve code snippets from your terminal.

## Installation

```bash
pip install -e .

# With syntax highlighting:
pip install -e ".[highlight]"
```

## Usage

### Add a snippet

```bash
# Add with inline code
snip add "hello-world" -c "print('Hello, World!')" -l python -t greeting,example

# Add from stdin (pipe code)
cat myfile.py | snip add "my-utility" -l python -d "A useful utility function"

# Add with description and tags
snip add "fetch-api" -c "fetch('/api').then(r => r.json())" -l javascript -t api,fetch -d "Basic fetch example"
```

### Get a snippet

```bash
# By name
snip get hello-world

# By ID
snip get a1b2c3d4

# Raw output (just the code)
snip get hello-world --raw

# Copy to clipboard
snip get hello-world --copy
```

### List and search

```bash
# List all snippets
snip list

# Search by text
snip list "hello"

# Filter by tag
snip list -t api

# Filter by language
snip list -l python

# Combine filters
snip list "fetch" -l javascript -t api
```

### Edit a snippet

```bash
# Update metadata
snip edit hello-world -d "Updated description" -t newtag1,newtag2

# Update code via stdin
echo "print('Updated!')" | snip edit hello-world
```

### Execute a snippet

```bash
# Run a snippet (prompts for confirmation)
snip exec hello-world

# Skip confirmation
snip exec hello-world -y

# Pass additional arguments to the interpreter
snip exec my-script -y -- arg1 arg2
```

Supported languages: python, javascript/node, typescript, ruby, perl, php, lua, bash, sh, zsh, fish.

### Delete a snippet

```bash
snip delete hello-world

# Skip confirmation
snip delete hello-world --force
```

## Aliases

- `snip a` = `snip add`
- `snip g` = `snip get`
- `snip ls` or `snip l` = `snip list`
- `snip rm` or `snip d` = `snip delete`
- `snip e` = `snip edit`
- `snip x` or `snip run` = `snip exec`

## Storage

Snippets are stored in `~/.snip/snippets.json`.
