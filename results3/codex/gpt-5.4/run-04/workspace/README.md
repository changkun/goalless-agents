# Text Digest

Goal: turn this empty repository into a useful first tool by adding a runnable text summarizer CLI.

`text_digest.py` reads a UTF-8 text file and produces:

- a short sentence-based summary
- a simple keyword frequency index

## Usage

```bash
python3 text_digest.py path/to/file.txt
python3 text_digest.py path/to/file.txt --sentences 3 --keywords 8
python3 text_digest.py path/to/file.txt --json
```

## Run tests

```bash
python3 -m unittest discover -s tests
```
