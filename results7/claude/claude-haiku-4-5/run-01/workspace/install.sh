#!/bin/bash
# Quick Task installer

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="${1:~/.local/bin}"

mkdir -p "$INSTALL_DIR"
cp "$SCRIPT_DIR/task.py" "$INSTALL_DIR/task"
chmod +x "$INSTALL_DIR/task"

if [[ ":$PATH:" == *":$INSTALL_DIR:"* ]]; then
    echo "✓ Installed task to $INSTALL_DIR/task"
    echo "✓ Ready to use: task add 'your task'"
else
    echo "✓ Installed task to $INSTALL_DIR/task"
    echo ""
    echo "⚠ Warning: $INSTALL_DIR is not in your PATH"
    echo "Add this line to your shell profile:"
    echo "  export PATH=\"\$PATH:$INSTALL_DIR\""
fi
