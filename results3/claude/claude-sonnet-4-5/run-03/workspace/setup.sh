#!/bin/bash
# Setup script for Pomodoro Task Manager

echo "🍅 Setting up Pomodoro Task Manager..."

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate and install dependencies
echo "📦 Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run the app:"
echo "  source venv/bin/activate"
echo "  python pomodoro.py"
echo ""
