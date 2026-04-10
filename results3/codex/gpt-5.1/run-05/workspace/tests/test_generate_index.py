from pathlib import Path

from generate_index import build_index_entries, extract_title, render_html, generate_index


def test_extract_title_prefers_first_heading():
    text = "# Title One\n\n## Subtitle\nContent"
    assert extract_title(text, fallback="Fallback") == "Title One"


def test_extract_title_falls_back_to_given():
    text = "No headings here"
    assert extract_title(text, fallback="Fallback") == "Fallback"


def test_build_index_entries_uses_filenames_and_headings(tmp_path: Path):
    file1 = tmp_path / "readme.md"
    file1.write_text("# Hello World\nBody", encoding="utf-8")

    file2 = tmp_path / "notes-about-project.md"
    file2.write_text("No heading line", encoding="utf-8")

    entries = build_index_entries([file1, file2])
    titles = [title for title, _ in entries]
    assert "Hello World" in titles
    # Fallback converts hyphens to spaces and title-cases
    assert "Notes About Project" in titles


def test_render_html_contains_links():
    entries = [("Doc One", "doc1.md"), ("Doc Two", "doc2.md")]
    html = render_html(entries, title="My Index")
    assert "My Index" in html
    assert 'href="doc1.md"' in html
    assert "Doc One" in html


def test_generate_index_creates_file(tmp_path: Path):
    md = tmp_path / "sample.md"
    md.write_text("# Sample\nBody", encoding="utf-8")

    output = tmp_path / "index.html"
    generate_index(tmp_path, output)

    assert output.exists()
    content = output.read_text(encoding="utf-8")
    assert "Sample" in content

