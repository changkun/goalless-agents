#!/bin/bash
# Demo script for GW - Git Workflow tool

set -e

echo "🎯 GW - Git Workflow Demo"
echo "========================="
echo ""

# Clean slate
rm -rf demo-repo
mkdir demo-repo
cd demo-repo

echo "📦 Step 1: Initialize repository"
../gw init
echo ""
sleep 1

echo "📝 Step 2: Create some files"
echo "print('Hello World')" > app.py
echo "# My App" > README.md
echo ""
sleep 1

echo "📊 Step 3: Check status"
../gw
echo ""
sleep 1

echo "💾 Step 4: Quick save everything"
git config user.name "Demo User"
git config user.email "demo@example.com"
../gw save
echo ""
sleep 1

echo "🌿 Step 5: Create feature branch"
../gw new add-tests
echo ""
sleep 1

echo "🧪 Step 6: Add test file"
echo "def test_app(): pass" > test_app.py
../gw add
../gw commit
echo ""
sleep 1

echo "📋 Step 7: Check status with commits"
../gw
echo ""
sleep 1

echo "🔄 Step 8: Switch to main and merge"
../gw to master
git merge add-tests --no-edit
echo ""
sleep 1

echo "🧹 Step 9: Cleanup merged branches"
../gw cleanup
echo ""
sleep 1

echo "📜 Step 10: Final status"
../gw
echo ""

echo "✅ Demo complete!"
echo ""
echo "Try these commands:"
echo "  cd demo-repo"
echo "  ../gw           # Show status"
echo "  ../gw help      # See all commands"
