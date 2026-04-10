#!/usr/bin/env python3
"""sayhello: minimal CLI demo"""

import argparse
import sys

__version__ = "0.1.0"


def make_parser():
    p = argparse.ArgumentParser(prog="sayhello", description="Print a greeting")
    p.add_argument("--name", "-n", default="World", help="Name to greet")
    p.add_argument("--version", action="store_true", help="Print version and exit")
    return p


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    parser = make_parser()
    args = parser.parse_args(argv)
    if args.version:
        print(__version__)
        return 0
    print(f"Hello, {args.name}!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

