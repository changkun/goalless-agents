from io import StringIO

from miniwc.core import count_stream, format_counts, Counts


def test_count_stream_basic():
    text = "hello world\nthis is a test\n"
    counts = count_stream(StringIO(text))
    assert counts.lines == 2
    assert counts.words == 6
    assert counts.bytes == len(text.encode())


def test_format_counts_with_and_without_label():
    counts = Counts(lines=1, words=2, bytes=3)
    no_label = format_counts(counts)
    with_label = format_counts(counts, "file.txt")

    assert "1" in no_label and "2" in no_label and "3" in no_label
    assert "file.txt" not in no_label
    assert "file.txt" in with_label

