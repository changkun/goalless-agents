#!/bin/bash
# CodePulse Demo Script

echo "======================================"
echo "  CodePulse Demonstration"
echo "======================================"
echo ""

echo "1. Analyzing sample project..."
echo "   Command: python3 codepulse.py sample_project"
echo ""
python3 codepulse.py sample_project
echo ""

echo "2. Detailed analysis with language breakdown..."
echo "   Command: python3 codepulse.py sample_project --detailed"
echo ""
python3 codepulse.py sample_project --detailed
echo ""

echo "3. Analyzing CodePulse itself (meta!)..."
echo "   Command: python3 codepulse.py codepulse.py"
echo ""
python3 codepulse.py codepulse.py
echo ""

echo "======================================"
echo "  Demo Complete!"
echo "======================================"
echo ""
echo "Try it yourself:"
echo "  python3 codepulse.py /path/to/your/project"
echo "  python3 codepulse.py . --detailed"
echo ""
