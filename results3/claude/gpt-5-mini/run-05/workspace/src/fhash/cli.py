import argparse
import hashlib
import sys
from pathlib import Path
from typing import Union


def compute_hash(path: Union[str, Path], algorithm: str = "sha256") -> str:
    """Compute the hex digest of a file or directory at `path` using `algorithm`.

    If `path` is a file, returns the hash of its bytes. If it's a directory,
    walks all regular files under it in deterministic sorted order and updates
    the digest with each file's relative POSIX path (as UTF-8) followed by a
    null byte, then the file contents and a null byte. This produces a stable
    hash for the directory contents and paths.

    Raises FileNotFoundError if missing and ValueError if algorithm is unknown.
    """
    alg = algorithm
    h = hashlib.new(alg)
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(p)

    if p.is_file():
        with p.open("rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()

    # Directory: walk files in sorted order, using relative POSIX paths
    if p.is_dir():
        files = [f for f in p.rglob("*") if f.is_file()]
        # sort by relative posix path for determinism
        files.sort(key=lambda fp: fp.relative_to(p).as_posix())
        for fpath in files:
            rel = fpath.relative_to(p).as_posix().encode("utf-8")
            h.update(b"FILENAME:")
            h.update(rel)
            h.update(b"\0")
            with fpath.open("rb") as fh:
                for chunk in iter(lambda: fh.read(8192), b""):
                    h.update(chunk)
            h.update(b"\0")
        return h.hexdigest()

    # Fallback (e.g., symlink) treat as file-like by reading bytes
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _hash_stdin(algorithm: str) -> str:
    data = sys.stdin.buffer.read()
    h = hashlib.new(algorithm)
    h.update(data)
    return h.hexdigest()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="fhash", description="Compute file or directory hash (default: sha256)")
    parser.add_argument("path", nargs="?", help="File or directory path. If omitted reads stdin.")
    parser.add_argument("-a", "--algorithm", default="sha256", help="Hash algorithm (sha256, sha1, md5, etc.)")
    args = parser.parse_args(argv)

    try:
        if args.path:
            print(compute_hash(args.path, args.algorithm))
        else:
            print(_hash_stdin(args.algorithm))
    except FileNotFoundError:
        print(f"Error: file not found: {args.path}", file=sys.stderr)
        return 2
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
