#!/bin/bash
# Setup script for TASQ

set -e

echo "🚀 Setting up TASQ..."

# Make script executable
chmod +x tasq.py

# Create symlink in /usr/local/bin (optional)
if [ "$1" = "--global" ]; then
    echo "📌 Installing to /usr/local/bin/tasq..."
    sudo ln -sf "$(pwd)/tasq.py" /usr/local/bin/tasq
    echo "✓ You can now use 'tasq' from anywhere"
else
    echo "✓ Script is ready to use as ./tasq.py"
    echo "  Run with --global flag to install globally: ./setup.sh --global"
fi

echo ""
echo "📖 Quick start:"
echo "  ./tasq.py add 'My first task'"
echo "  ./tasq.py list"
echo "  ./tasq.py stats"
echo ""
echo "✨ Happy task managing!"
