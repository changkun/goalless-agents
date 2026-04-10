import hashlib
from pathlib import Path

from fhash.cli import compute_hash


def test_compute_hash_sha256(tmp_path):
    p = tmp_path / "foo.bin"
    data = b"hello world"
    p.write_bytes(data)
    expected = hashlib.sha256(data).hexdigest()
    assert compute_hash(str(p)) == expected


def test_compute_hash_md5(tmp_path):
    p = tmp_path / "foo.bin"
    data = b"abc"
    p.write_bytes(data)
    expected = hashlib.md5(data).hexdigest()
    assert compute_hash(str(p), "md5") == expected


def test_compute_hash_directory_deterministic(tmp_path):
    # Create a nested directory with files in non-sorted creation order
    d = tmp_path / "dir"
    d.mkdir()
    (d / "b.txt").write_bytes(b"second")
    sub = d / "sub"
    sub.mkdir()
    (sub / "a.txt").write_bytes(b"inner")
    (d / "a.txt").write_bytes(b"first")

    # Compute expected digest using the same deterministic procedure used by
    # compute_hash: walk files, sort by relative POSIX path, update with
    # b'FILENAME:' + rel + b'\0' + contents + b'\0'
    alg = "sha256"
    h = hashlib.new(alg)
    files = [f for f in d.rglob("*") if f.is_file()]
    files.sort(key=lambda fp: fp.relative_to(d).as_posix())
    for fpath in files:
        rel = fpath.relative_to(d).as_posix().encode("utf-8")
        h.update(b"FILENAME:")
        h.update(rel)
        h.update(b"\0")
        h.update(fpath.read_bytes())
        h.update(b"\0")
    expected = h.hexdigest()

    assert compute_hash(str(d)) == expected
