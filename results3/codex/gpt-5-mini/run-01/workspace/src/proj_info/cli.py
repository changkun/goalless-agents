import argparse
import pathlib

from . import __version__


def main(argv=None):
    p = argparse.ArgumentParser(prog="proj-info")
    p.add_argument("--version", action="store_true", help="Show version")
    p.add_argument("--path", default='.', help="Path to inspect")
    args = p.parse_args(argv)
    if args.version:
        print(__version__)
        return 0
    path = pathlib.Path(args.path)
    print(f"Path: {path.resolve()}")
    if path.exists():
        print(f"Exists: yes")
        if path.is_dir():
            files = list(path.iterdir())
            print(f"Entries: {len(files)}")
    else:
        print("Exists: no")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
