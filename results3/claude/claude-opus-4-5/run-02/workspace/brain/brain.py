#!/usr/bin/env python3
"""
brain - A terminal-based personal knowledge base

Quick note capture, search, and organization from the command line.
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'


def get_brain_dir() -> Path:
    """Get the brain directory, defaulting to ~/.brain"""
    brain_dir = os.environ.get('BRAIN_DIR', os.path.expanduser('~/.brain'))
    return Path(brain_dir)


def ensure_brain_dir():
    """Create brain directory structure if it doesn't exist"""
    brain_dir = get_brain_dir()
    (brain_dir / 'notes').mkdir(parents=True, exist_ok=True)
    (brain_dir / 'daily').mkdir(parents=True, exist_ok=True)

    # Initialize index if needed
    index_file = brain_dir / 'index.json'
    if not index_file.exists():
        index_file.write_text(json.dumps({'notes': {}, 'tags': {}}, indent=2))

    return brain_dir


def load_index() -> dict:
    """Load the notes index"""
    brain_dir = get_brain_dir()
    index_file = brain_dir / 'index.json'
    if index_file.exists():
        return json.loads(index_file.read_text())
    return {'notes': {}, 'tags': {}}


def save_index(index: dict):
    """Save the notes index"""
    brain_dir = get_brain_dir()
    index_file = brain_dir / 'index.json'
    index_file.write_text(json.dumps(index, indent=2))


def generate_id(content: str) -> str:
    """Generate a short ID for a note"""
    h = hashlib.sha256(f"{content}{datetime.datetime.now().isoformat()}".encode())
    return h.hexdigest()[:8]


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML-like frontmatter from note content"""
    metadata = {}
    body = content

    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter = parts[1].strip()
            body = parts[2].strip()

            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    if key == 'tags':
                        metadata[key] = [t.strip() for t in value.split(',')]
                    else:
                        metadata[key] = value

    return metadata, body


def create_frontmatter(title: str, tags: list[str]) -> str:
    """Create frontmatter for a note"""
    lines = ['---']
    lines.append(f'title: {title}')
    lines.append(f'created: {datetime.datetime.now().isoformat()}')
    if tags:
        lines.append(f'tags: {", ".join(tags)}')
    lines.append('---')
    return '\n'.join(lines)


def cmd_new(args):
    """Create a new note"""
    brain_dir = ensure_brain_dir()
    index = load_index()

    # Get title
    title = ' '.join(args.title) if args.title else input(f"{Colors.CYAN}Title: {Colors.RESET}")
    if not title:
        print(f"{Colors.RED}Error: Title is required{Colors.RESET}")
        return 1

    # Get tags
    tags = []
    if args.tags:
        tags = [t.strip() for t in args.tags.split(',')]

    # Generate ID and filename
    note_id = generate_id(title)
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'[\s_]+', '-', slug)[:50]
    filename = f"{note_id}-{slug}.md"

    # Create note content
    frontmatter = create_frontmatter(title, tags)
    content = frontmatter + '\n\n'

    # If content provided via stdin or argument
    if args.content:
        content += ' '.join(args.content)
    elif not sys.stdin.isatty():
        content += sys.stdin.read()

    # Write note
    note_path = brain_dir / 'notes' / filename
    note_path.write_text(content)

    # Update index
    index['notes'][note_id] = {
        'title': title,
        'filename': filename,
        'tags': tags,
        'created': datetime.datetime.now().isoformat(),
        'modified': datetime.datetime.now().isoformat()
    }

    # Update tag index
    for tag in tags:
        if tag not in index['tags']:
            index['tags'][tag] = []
        if note_id not in index['tags'][tag]:
            index['tags'][tag].append(note_id)

    save_index(index)

    print(f"{Colors.GREEN}Created note:{Colors.RESET} {note_id}")
    print(f"{Colors.DIM}Path: {note_path}{Colors.RESET}")

    # Open in editor if requested
    if args.edit:
        editor = os.environ.get('EDITOR', 'vim')
        os.system(f'{editor} "{note_path}"')

    return 0


def cmd_today(args):
    """Open or create today's daily note"""
    brain_dir = ensure_brain_dir()

    today = datetime.date.today()
    filename = f"{today.isoformat()}.md"
    note_path = brain_dir / 'daily' / filename

    if not note_path.exists():
        content = f"""---
date: {today.isoformat()}
type: daily
---

# {today.strftime('%A, %B %d, %Y')}

## Tasks
- [ ]

## Notes

## Links

"""
        note_path.write_text(content)
        print(f"{Colors.GREEN}Created daily note for {today}{Colors.RESET}")
    else:
        print(f"{Colors.CYAN}Opening daily note for {today}{Colors.RESET}")

    if args.show:
        print()
        print(note_path.read_text())
    else:
        editor = os.environ.get('EDITOR', 'vim')
        os.system(f'{editor} "{note_path}"')

    return 0


def cmd_search(args):
    """Search notes by content or tags"""
    brain_dir = ensure_brain_dir()
    index = load_index()

    query = ' '.join(args.query).lower()
    results = []

    # Search in notes
    notes_dir = brain_dir / 'notes'
    for note_file in notes_dir.glob('*.md'):
        content = note_file.read_text().lower()
        if query in content:
            note_id = note_file.stem.split('-')[0]
            note_info = index['notes'].get(note_id, {})

            # Find matching lines
            lines = note_file.read_text().split('\n')
            matches = []
            for i, line in enumerate(lines, 1):
                if query in line.lower():
                    matches.append((i, line.strip()))

            results.append({
                'id': note_id,
                'title': note_info.get('title', note_file.stem),
                'path': note_file,
                'matches': matches[:3]  # Show first 3 matches
            })

    # Search in daily notes
    daily_dir = brain_dir / 'daily'
    for note_file in daily_dir.glob('*.md'):
        content = note_file.read_text().lower()
        if query in content:
            lines = note_file.read_text().split('\n')
            matches = []
            for i, line in enumerate(lines, 1):
                if query in line.lower():
                    matches.append((i, line.strip()))

            results.append({
                'id': note_file.stem,
                'title': f"Daily: {note_file.stem}",
                'path': note_file,
                'matches': matches[:3]
            })

    if not results:
        print(f"{Colors.YELLOW}No notes found matching '{query}'{Colors.RESET}")
        return 0

    print(f"{Colors.GREEN}Found {len(results)} note(s):{Colors.RESET}\n")

    for result in results:
        print(f"{Colors.BOLD}{Colors.BLUE}[{result['id']}]{Colors.RESET} {result['title']}")
        for line_num, line in result['matches']:
            # Highlight the query
            highlighted = re.sub(
                f'({re.escape(query)})',
                f'{Colors.YELLOW}\\1{Colors.RESET}',
                line,
                flags=re.IGNORECASE
            )
            print(f"  {Colors.DIM}L{line_num}:{Colors.RESET} {highlighted}")
        print()

    return 0


def cmd_list(args):
    """List all notes"""
    brain_dir = ensure_brain_dir()
    index = load_index()

    notes = index.get('notes', {})

    if args.tag:
        # Filter by tag
        tag_notes = index.get('tags', {}).get(args.tag, [])
        notes = {k: v for k, v in notes.items() if k in tag_notes}

    if not notes:
        if args.tag:
            print(f"{Colors.YELLOW}No notes found with tag '{args.tag}'{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}No notes yet. Create one with: brain new{Colors.RESET}")
        return 0

    # Sort by modified date
    sorted_notes = sorted(notes.items(), key=lambda x: x[1].get('modified', ''), reverse=True)

    if args.tag:
        print(f"{Colors.HEADER}Notes tagged '{args.tag}':{Colors.RESET}\n")
    else:
        print(f"{Colors.HEADER}All notes ({len(notes)}):{Colors.RESET}\n")

    for note_id, info in sorted_notes[:args.limit]:
        tags_str = ''
        if info.get('tags'):
            tags_str = f" {Colors.DIM}[{', '.join(info['tags'])}]{Colors.RESET}"

        created = info.get('created', '')[:10]
        print(f"{Colors.BLUE}[{note_id}]{Colors.RESET} {info.get('title', 'Untitled')}{tags_str}")
        print(f"  {Colors.DIM}{created}{Colors.RESET}")

    if len(sorted_notes) > args.limit:
        print(f"\n{Colors.DIM}...and {len(sorted_notes) - args.limit} more{Colors.RESET}")

    return 0


def cmd_show(args):
    """Show a specific note"""
    brain_dir = ensure_brain_dir()
    index = load_index()

    note_id = args.id

    # Check if it's a daily note (date format)
    if re.match(r'\d{4}-\d{2}-\d{2}', note_id):
        note_path = brain_dir / 'daily' / f"{note_id}.md"
    else:
        # Look up in index
        note_info = index['notes'].get(note_id)
        if not note_info:
            # Try partial match
            matches = [k for k in index['notes'].keys() if k.startswith(note_id)]
            if len(matches) == 1:
                note_id = matches[0]
                note_info = index['notes'][note_id]
            elif len(matches) > 1:
                print(f"{Colors.YELLOW}Multiple matches found:{Colors.RESET}")
                for m in matches:
                    print(f"  {m}: {index['notes'][m].get('title')}")
                return 1
            else:
                print(f"{Colors.RED}Note not found: {note_id}{Colors.RESET}")
                return 1

        note_path = brain_dir / 'notes' / note_info['filename']

    if not note_path.exists():
        print(f"{Colors.RED}Note file not found: {note_path}{Colors.RESET}")
        return 1

    content = note_path.read_text()

    # Simple syntax highlighting for markdown
    lines = content.split('\n')
    for line in lines:
        if line.startswith('# '):
            print(f"{Colors.BOLD}{Colors.HEADER}{line}{Colors.RESET}")
        elif line.startswith('## '):
            print(f"{Colors.BOLD}{Colors.BLUE}{line}{Colors.RESET}")
        elif line.startswith('### '):
            print(f"{Colors.BOLD}{Colors.CYAN}{line}{Colors.RESET}")
        elif line.startswith('---'):
            print(f"{Colors.DIM}{line}{Colors.RESET}")
        elif line.startswith('- [ ]'):
            print(f"{Colors.YELLOW}{line}{Colors.RESET}")
        elif line.startswith('- [x]'):
            print(f"{Colors.GREEN}{line}{Colors.RESET}")
        elif line.startswith('```'):
            print(f"{Colors.DIM}{line}{Colors.RESET}")
        else:
            # Highlight [[wiki links]]
            highlighted = re.sub(
                r'\[\[([^\]]+)\]\]',
                f'{Colors.CYAN}[[\\1]]{Colors.RESET}',
                line
            )
            print(highlighted)

    return 0


def cmd_tags(args):
    """List all tags"""
    index = load_index()
    tags = index.get('tags', {})

    if not tags:
        print(f"{Colors.YELLOW}No tags yet{Colors.RESET}")
        return 0

    print(f"{Colors.HEADER}Tags:{Colors.RESET}\n")

    for tag, note_ids in sorted(tags.items()):
        print(f"  {Colors.CYAN}#{tag}{Colors.RESET} ({len(note_ids)} notes)")

    return 0


def cmd_edit(args):
    """Edit a note"""
    brain_dir = ensure_brain_dir()
    index = load_index()

    note_id = args.id
    note_info = index['notes'].get(note_id)

    if not note_info:
        # Try partial match
        matches = [k for k in index['notes'].keys() if k.startswith(note_id)]
        if len(matches) == 1:
            note_id = matches[0]
            note_info = index['notes'][note_id]
        else:
            print(f"{Colors.RED}Note not found: {note_id}{Colors.RESET}")
            return 1

    note_path = brain_dir / 'notes' / note_info['filename']

    editor = os.environ.get('EDITOR', 'vim')
    os.system(f'{editor} "{note_path}"')

    # Update modified time
    index['notes'][note_id]['modified'] = datetime.datetime.now().isoformat()
    save_index(index)

    return 0


def cmd_link(args):
    """Find notes that link to a specific note (backlinks)"""
    brain_dir = ensure_brain_dir()
    index = load_index()

    target = args.id
    target_info = index['notes'].get(target)

    if not target_info:
        print(f"{Colors.RED}Note not found: {target}{Colors.RESET}")
        return 1

    target_title = target_info.get('title', '')
    backlinks = []

    notes_dir = brain_dir / 'notes'
    for note_file in notes_dir.glob('*.md'):
        content = note_file.read_text()
        # Look for [[title]] or [[id]] links
        if f'[[{target_title}]]' in content or f'[[{target}]]' in content:
            note_id = note_file.stem.split('-')[0]
            if note_id != target:
                backlinks.append({
                    'id': note_id,
                    'title': index['notes'].get(note_id, {}).get('title', note_file.stem)
                })

    if not backlinks:
        print(f"{Colors.YELLOW}No backlinks found for '{target_title}'{Colors.RESET}")
        return 0

    print(f"{Colors.HEADER}Backlinks to '{target_title}':{Colors.RESET}\n")
    for link in backlinks:
        print(f"  {Colors.BLUE}[{link['id']}]{Colors.RESET} {link['title']}")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description='brain - A terminal-based personal knowledge base',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  brain new "My Note" -t work,ideas     Create a new note with tags
  brain new -e                          Create and open in editor
  brain today                           Open today's daily note
  brain search python                   Search for "python" in all notes
  brain list -t work                    List notes with tag "work"
  brain show abc123                     Show note with ID abc123
  brain edit abc123                     Edit note in $EDITOR
  brain tags                            List all tags
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # new command
    new_parser = subparsers.add_parser('new', aliases=['n'], help='Create a new note')
    new_parser.add_argument('title', nargs='*', help='Note title')
    new_parser.add_argument('-t', '--tags', help='Comma-separated tags')
    new_parser.add_argument('-c', '--content', nargs='*', help='Note content')
    new_parser.add_argument('-e', '--edit', action='store_true', help='Open in editor after creation')

    # today command
    today_parser = subparsers.add_parser('today', aliases=['t', 'd'], help="Open today's daily note")
    today_parser.add_argument('-s', '--show', action='store_true', help='Show instead of edit')

    # search command
    search_parser = subparsers.add_parser('search', aliases=['s', 'find'], help='Search notes')
    search_parser.add_argument('query', nargs='+', help='Search query')

    # list command
    list_parser = subparsers.add_parser('list', aliases=['ls', 'l'], help='List notes')
    list_parser.add_argument('-t', '--tag', help='Filter by tag')
    list_parser.add_argument('-n', '--limit', type=int, default=20, help='Max notes to show')

    # show command
    show_parser = subparsers.add_parser('show', aliases=['cat', 'view'], help='Show a note')
    show_parser.add_argument('id', help='Note ID or date for daily notes')

    # edit command
    edit_parser = subparsers.add_parser('edit', aliases=['e'], help='Edit a note')
    edit_parser.add_argument('id', help='Note ID')

    # tags command
    subparsers.add_parser('tags', help='List all tags')

    # link/backlinks command
    link_parser = subparsers.add_parser('links', aliases=['backlinks'], help='Find backlinks to a note')
    link_parser.add_argument('id', help='Note ID')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    commands = {
        'new': cmd_new, 'n': cmd_new,
        'today': cmd_today, 't': cmd_today, 'd': cmd_today,
        'search': cmd_search, 's': cmd_search, 'find': cmd_search,
        'list': cmd_list, 'ls': cmd_list, 'l': cmd_list,
        'show': cmd_show, 'cat': cmd_show, 'view': cmd_show,
        'edit': cmd_edit, 'e': cmd_edit,
        'tags': cmd_tags,
        'links': cmd_link, 'backlinks': cmd_link,
    }

    cmd_func = commands.get(args.command)
    if cmd_func:
        return cmd_func(args)

    parser.print_help()
    return 0


if __name__ == '__main__':
    sys.exit(main())
