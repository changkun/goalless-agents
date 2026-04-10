#!/bin/bash
# Install habit tracker CLI

set -e

INSTALL_DIR="${HOME}/.local/bin"
mkdir -p "$INSTALL_DIR"

cp habits.py "${INSTALL_DIR}/habits"
chmod +x "${INSTALL_DIR}/habits"

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":${INSTALL_DIR}:"* ]]; then
    echo "Add this to your shell config (~/.bashrc or ~/.zshrc):"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
fi

echo "Installed! Run 'habits help' to get started."
