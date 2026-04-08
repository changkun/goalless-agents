#!/bin/bash
# Demo script for SmartCommit

echo "🚀 SmartCommit Demo"
echo "==================="
echo ""

# Initialize a demo git repo
echo "📦 Setting up demo git repository..."
rm -rf demo_repo
mkdir -p demo_repo
cd demo_repo
git init
git config user.name "Demo User"
git config user.email "demo@example.com"

# Create initial commit
echo "# Demo Project" > README.md
echo "print('Hello, World!')" > app.py
git add .
git commit -m "Initial commit"

echo ""
echo "✅ Demo repository created!"
echo ""

# Demo 1: New feature
echo "📝 Demo 1: Adding a new feature"
echo "--------------------------------"
cat > app.py << 'EOF'
def greet(name):
    """Greet a user by name"""
    return f"Hello, {name}!"

def main():
    name = input("Enter your name: ")
    print(greet(name))

if __name__ == '__main__':
    main()
EOF

git add app.py
echo ""
echo "Running: python ../smartcommit.py"
python ../smartcommit.py
echo ""

# Demo 2: Bug fix
echo "📝 Demo 2: Fixing a bug"
echo "------------------------"
cat > app.py << 'EOF'
def greet(name):
    """Greet a user by name"""
    if not name:
        name = "World"
    return f"Hello, {name}!"

def main():
    name = input("Enter your name: ")
    print(greet(name))

if __name__ == '__main__':
    main()
EOF

git add app.py
echo ""
echo "Running: python ../smartcommit.py"
python ../smartcommit.py
echo ""

# Demo 3: Adding tests
echo "📝 Demo 3: Adding tests"
echo "------------------------"
cat > test_app.py << 'EOF'
import unittest
from app import greet

class TestGreet(unittest.TestCase):
    def test_greet_with_name(self):
        self.assertEqual(greet("Alice"), "Hello, Alice!")

    def test_greet_empty_name(self):
        self.assertEqual(greet(""), "Hello, World!")

if __name__ == '__main__':
    unittest.main()
EOF

git add test_app.py
echo ""
echo "Running: python ../smartcommit.py"
python ../smartcommit.py
echo ""

# Demo 4: Documentation
echo "📝 Demo 4: Updating documentation"
echo "----------------------------------"
cat > README.md << 'EOF'
# Demo Project

A simple greeting application that demonstrates Python best practices.

## Features

- Interactive user input
- Name validation
- Comprehensive test coverage

## Usage

```bash
python app.py
```

## Testing

```bash
python test_app.py
```
EOF

git add README.md
echo ""
echo "Running: python ../smartcommit.py"
python ../smartcommit.py
echo ""

# Cleanup
cd ..
echo "🧹 Cleaning up..."
echo ""
echo "✨ Demo complete! Check out smartcommit.py for the implementation."
