import os

from scripts import health_check


def test_analyze_simple(tmp_path):
    # create files and a subdirectory
    d = tmp_path
    f1 = d / "a.txt"
    f1.write_text("hello")
    f2 = d / "b.py"
    f2.write_text("print(1)")
    sub = d / "sub"
    sub.mkdir()
    f3 = sub / "c.bin"
    f3.write_bytes(b"\x00" * 1024)

    res = health_check.analyze(str(d), top_n=3)

    assert res["total_files"] == 3
    # check extensions reported
    exts = dict(res["top_extensions"])
    assert ".txt" in exts and exts[".txt"] == 1
    assert ".py" in exts and exts[".py"] == 1
    # size should be at least the binary file
    assert res["total_size"] >= 1024
