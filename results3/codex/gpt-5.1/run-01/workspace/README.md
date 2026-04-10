# miniwc

A tiny Python clone of the classic `wc` tool.

## Installation

From this directory:

```bash
pip install .
```

## Usage

Count lines, words, and bytes from stdin:

```bash
echo "hello world" | miniwc
```

Or for one or more files:

```bash
miniwc file1.txt file2.txt
```

