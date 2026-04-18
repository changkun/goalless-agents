#!/bin/bash
set -e

INSTALL_DIR="${HOME}/.local/bin"
SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/task_journal.py"

# Create bin directory if it doesn't exist
mkdir -p "$INSTALL_DIR"

# Copy script
cp "$SCRIPT_PATH" "$INSTALL_DIR/task"
chmod +x "$INSTALL_DIR/task"

echo "✓ Task Journal installed successfully!"
echo ""
echo "Usage:"
echo "  task add \"Your task\" --tag category"
echo "  task list"
echo "  task report"
echo ""

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" == *":$INSTALL_DIR:"* ]]; then
    echo "✓ $INSTALL_DIR is in your PATH"
else
    echo "⚠ To use 'task' command, add this to your shell profile (~/.bashrc, ~/.zshrc, etc):"
    echo "  export PATH=\"$INSTALL_DIR:\$PATH\""
fi
