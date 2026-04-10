#!/usr/bin/env python3
"""Print simple repository/workspace info.

Usage: python3 repo_inspect.py
"""
import os
import sys


def count_files(path):
    total = 0
    for root, dirs, files in os.walk(path):
        for f in files:
            total += 1
    return total


def top_level_listing(path):
    try:
        return sorted(os.listdir(path))
    except Exception:
        return []


def main():
    cwd = os.getcwd()
    print(f"Working dir: {cwd}")
    files = count_files(cwd)
    print(f"Total files (recursive): {files}")
    print("Top-level listing:")
    for name in top_level_listing(cwd):
        print(f" - {name}")


if __name__ == '__main__':
    main()

