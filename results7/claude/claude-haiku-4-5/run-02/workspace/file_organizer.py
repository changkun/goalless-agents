#!/usr/bin/env python3
"""
File Organizer CLI - Intelligently organize files in a directory by type.
Supports dry-run mode to preview changes before applying them.
"""

import os
import shutil
import argparse
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class FileCategory:
    name: str
    extensions: set


# Define file categories
CATEGORIES = [
    FileCategory("Documents", {".pdf", ".doc", ".docx", ".txt", ".xls", ".xlsx", ".ppt", ".pptx"}),
    FileCategory("Images", {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico"}),
    FileCategory("Videos", {".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv", ".webm"}),
    FileCategory("Audio", {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma"}),
    FileCategory("Code", {".py", ".js", ".ts", ".java", ".cpp", ".c", ".go", ".rs", ".rb", ".php", ".swift"}),
    FileCategory("Archives", {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"}),
    FileCategory("Executables", {".exe", ".msi", ".app", ".deb", ".rpm", ".apk"}),
]


def get_category(filename: str) -> str:
    """Find the category for a file based on its extension."""
    ext = Path(filename).suffix.lower()
    for category in CATEGORIES:
        if ext in category.extensions:
            return category.name
    return "Other"


def analyze_directory(directory: Path) -> dict:
    """Analyze a directory and categorize files."""
    stats = defaultdict(list)

    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    if not directory.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {directory}")

    for item in directory.iterdir():
        if item.is_file():
            category = get_category(item.name)
            stats[category].append(item)

    return stats


def print_analysis(stats: dict) -> None:
    """Print analysis of files by category."""
    print("\n📊 File Organization Analysis")
    print("=" * 50)

    total_files = sum(len(files) for files in stats.values())
    print(f"Total files: {total_files}\n")

    for category in sorted(stats.keys()):
        files = stats[category]
        print(f"📁 {category}: {len(files)} file(s)")
        for file in sorted(files)[:3]:
            print(f"   - {file.name}")
        if len(files) > 3:
            print(f"   ... and {len(files) - 3} more")
    print()


def organize_files(directory: Path, dry_run: bool = True) -> int:
    """Organize files into category subdirectories."""
    stats = analyze_directory(directory)
    print_analysis(stats)

    total_moved = 0

    for category, files in stats.items():
        if category == "Other" or not files:
            continue

        target_dir = directory / category

        if not dry_run:
            target_dir.mkdir(exist_ok=True)

        for file in files:
            new_path = target_dir / file.name

            if dry_run:
                print(f"[DRY RUN] Would move: {file.name} → {category}/")
            else:
                try:
                    shutil.move(str(file), str(new_path))
                    print(f"✓ Moved: {file.name} → {category}/")
                    total_moved += 1
                except Exception as e:
                    print(f"✗ Failed to move {file.name}: {e}")

    if dry_run:
        print("\n💡 Run with --apply to actually move files")
    else:
        print(f"\n✓ Organized {total_moved} files")

    return total_moved


def main():
    parser = argparse.ArgumentParser(description="Organize files in a directory by type")
    parser.add_argument("directory", nargs="?", default=".", help="Directory to organize (default: current)")
    parser.add_argument("--apply", action="store_true", help="Actually move files (default is dry-run)")
    parser.add_argument("--show-categories", action="store_true", help="Show all recognized categories")

    args = parser.parse_args()

    if args.show_categories:
        print("\n📋 Recognized File Categories")
        print("=" * 50)
        for category in CATEGORIES:
            exts = ", ".join(sorted(category.extensions))
            print(f"{category.name}: {exts}\n")
        return

    directory = Path(args.directory).resolve()
    organize_files(directory, dry_run=not args.apply)


if __name__ == "__main__":
    main()
