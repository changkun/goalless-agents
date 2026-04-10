#!/usr/bin/env python3
"""
Simple project health check utility.
Run: python3 scripts/health_check.py [path] [--json]
"""
import os
import argparse
import json
from collections import Counter


def analyze(path, top_n=5, exclude_dirs=None):
    """Analyze a directory and return a dict with summary metrics."""
    total_files = 0
    total_dirs = 0
    total_size = 0
    ext_counter = Counter()
    largest = []

    for root, dirs, files in os.walk(path):
        # optionally mutate dirs in-place to skip excluded directories
        if exclude_dirs:
            # remove any dirs that match a name in exclude_dirs
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
        total_dirs += len(dirs)
        for f in files:
            total_files += 1
            fp = os.path.join(root, f)
            try:
                sz = os.path.getsize(fp)
            except OSError:
                sz = 0
            total_size += sz
            ext = os.path.splitext(f)[1].lower() or "<noext>"
            ext_counter[ext] += 1
            largest.append((sz, fp))

    largest_sorted = sorted(largest, reverse=True)[:top_n]

    return {
        "path": os.path.abspath(path),
        "total_files": total_files,
        "total_dirs": total_dirs,
        "total_size": total_size,
        "top_extensions": ext_counter.most_common(10),
        "largest_files": [{"path": p, "size": s} for s, p in largest_sorted],
        "top_n": top_n,
    }


def main_cli():
    p = argparse.ArgumentParser(description="Project health check: counts files, sizes, extensions")
    p.add_argument("path", nargs="?", default=".", help="Path to analyze")
    p.add_argument("--json", action="store_true", help="Emit JSON")
    p.add_argument("--exclude", nargs="*", help="Directory names to exclude from scan (basename match)")
    p.add_argument("--top", type=int, default=5, help="Number of largest files to show")
    args = p.parse_args()

    res = analyze(args.path, top_n=args.top, exclude_dirs=set(args.exclude or []))

    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print(f"Path: {res['path']}")
        print(f"Files: {res['total_files']}  Dirs: {res['total_dirs']}  Size: {res['total_size']} bytes")
        print("Top extensions:")
        for ext, count in res["top_extensions"]:
            print(f"  {ext}: {count}")
        print("Largest files:")
        for lf in res["largest_files"]:
            print(f"  {lf['path']} ({lf['size']:,} bytes)")


if __name__ == "__main__":
    main_cli()
