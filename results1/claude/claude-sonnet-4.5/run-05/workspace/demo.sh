#!/bin/bash
# CodeScope Demo Script

echo "================================"
echo "CodeScope Code Quality Analyzer"
echo "================================"
echo ""

echo "1. Analyzing sample project (text output)..."
echo ""
python3 analyzer.py sample_project
echo ""

echo "2. Generating JSON report..."
python3 analyzer.py sample_project -f json -o report.json
echo "✓ JSON report saved to report.json"
echo ""

echo "3. Analyzing single file..."
python3 analyzer.py sample_project/src/auth.py
echo ""

echo "4. Sample JSON output structure:"
head -n 20 report.json
echo ""

echo "Demo complete! Try your own:"
echo "  python3 analyzer.py <path>"
echo "  python3 analyzer.py --help"
