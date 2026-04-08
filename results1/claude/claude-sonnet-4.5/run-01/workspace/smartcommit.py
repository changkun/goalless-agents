#!/usr/bin/env python3
"""
SmartCommit - AI-powered git commit message generator
"""

import subprocess
import sys
import argparse
import re
from typing import Tuple, List, Optional


class CommitAnalyzer:
    """Analyzes git diffs and generates commit messages"""

    COMMIT_TYPES = {
        'feat': 'A new feature',
        'fix': 'A bug fix',
        'docs': 'Documentation only changes',
        'style': 'Code style changes (formatting, semicolons, etc)',
        'refactor': 'Code refactoring without functionality change',
        'perf': 'Performance improvements',
        'test': 'Adding or updating tests',
        'build': 'Changes to build system or dependencies',
        'ci': 'CI configuration changes',
        'chore': 'Other changes that dont modify src or test files',
    }

    def __init__(self):
        self.diff_content = ""
        self.stats = {}

    def get_staged_diff(self) -> bool:
        """Get the staged changes from git"""
        try:
            result = subprocess.run(
                ['git', 'diff', '--cached', '--stat'],
                capture_output=True,
                text=True,
                check=True
            )
            stats = result.stdout

            result = subprocess.run(
                ['git', 'diff', '--cached'],
                capture_output=True,
                text=True,
                check=True
            )
            self.diff_content = result.stdout

            if not self.diff_content:
                print("No staged changes found. Use 'git add' to stage changes.")
                return False

            self._parse_stats(stats)
            return True

        except subprocess.CalledProcessError as e:
            print(f"Error: Not a git repository or git command failed: {e}")
            return False

    def _parse_stats(self, stats: str):
        """Parse git diff stats to understand changes"""
        self.stats = {
            'files_changed': 0,
            'insertions': 0,
            'deletions': 0,
            'files': []
        }

        for line in stats.split('\n'):
            if '|' in line:
                filename = line.split('|')[0].strip()
                self.stats['files'].append(filename)
                self.stats['files_changed'] += 1

            if 'insertion' in line:
                match = re.search(r'(\d+) insertion', line)
                if match:
                    self.stats['insertions'] = int(match.group(1))

            if 'deletion' in line:
                match = re.search(r'(\d+) deletion', line)
                if match:
                    self.stats['deletions'] = int(match.group(1))

    def analyze_changes(self) -> Tuple[str, Optional[str], str, List[str]]:
        """
        Analyze the diff and determine commit type, scope, description, and details
        Returns: (type, scope, description, bullet_points)
        """
        commit_type = self._determine_type()
        scope = self._determine_scope()
        description = self._generate_description(commit_type)
        details = self._extract_details()

        return commit_type, scope, description, details

    def _determine_type(self) -> str:
        """Determine the type of commit based on diff content"""
        diff_lower = self.diff_content.lower()

        # Test files
        if any('test' in f.lower() for f in self.stats['files']):
            if any(f.endswith(('.test.js', '.test.ts', '.test.py', '_test.py', '.spec.js')) or
                   f.split('/')[-1].startswith('test_')
                   for f in self.stats['files']):
                return 'test'

        # Documentation
        if any(f.endswith(('.md', '.txt', '.rst')) or 'readme' in f.lower()
               for f in self.stats['files']):
            return 'docs'

        # CI/CD files
        if any(('.github' in f or '.gitlab' in f or 'jenkins' in f.lower())
               for f in self.stats['files']):
            return 'ci'

        # Build files
        if any(f in ['package.json', 'requirements.txt', 'Cargo.toml', 'go.mod',
                     'pom.xml', 'build.gradle', 'Makefile']
               for f in self.stats['files']):
            return 'build'

        # Bug fixes
        if any(keyword in diff_lower for keyword in ['fix', 'bug', 'issue', 'error', 'crash']):
            return 'fix'

        # Performance
        if any(keyword in diff_lower for keyword in ['performance', 'optimize', 'speed', 'cache']):
            return 'perf'

        # New files or significant additions suggest new features
        if self.stats['insertions'] > self.stats['deletions'] * 2:
            return 'feat'

        # Significant deletions or equal changes suggest refactoring
        if self.stats['deletions'] > self.stats['insertions']:
            return 'refactor'

        # Default to feature for new additions
        return 'feat'

    def _determine_scope(self) -> Optional[str]:
        """Determine the scope (component/module) from file paths"""
        if not self.stats['files']:
            return None

        # Extract common directory or component name
        files = self.stats['files']

        # Single file - use filename without extension
        if len(files) == 1:
            filename = files[0].split('/')[-1]
            return filename.split('.')[0]

        # Multiple files - find common directory
        paths = [f.split('/') for f in files]
        if len(paths) > 1:
            # Find common prefix
            common = []
            for parts in zip(*paths):
                if len(set(parts)) == 1:
                    common.append(parts[0])
                else:
                    break

            if common:
                # Skip generic directory names like 'src', 'lib', 'app'
                for i, part in enumerate(common):
                    if part not in ['src', 'lib', 'app']:
                        return part
                # If all common parts are generic, return the last one
                return common[-1] if len(common) > 0 else None

        return None

    def _generate_description(self, commit_type: str) -> str:
        """Generate a short description of changes"""
        files = self.stats['files']

        if len(files) == 1:
            filename = files[0].split('/')[-1].split('.')[0]
            if commit_type == 'feat':
                return f"add {filename} implementation"
            elif commit_type == 'fix':
                return f"resolve issue in {filename}"
            elif commit_type == 'refactor':
                return f"refactor {filename} structure"
            elif commit_type == 'test':
                return f"add tests for {filename}"
            elif commit_type == 'docs':
                return f"update {filename} documentation"
        else:
            if commit_type == 'feat':
                return f"implement new functionality across {len(files)} files"
            elif commit_type == 'fix':
                return f"fix issues in {len(files)} components"
            elif commit_type == 'refactor':
                return f"refactor {len(files)} modules"
            elif commit_type == 'test':
                return f"add test coverage for {len(files)} components"

        return "update codebase"

    def _extract_details(self) -> List[str]:
        """Extract detailed changes as bullet points"""
        details = []

        # Add file changes
        if self.stats['files_changed'] <= 3:
            for file in self.stats['files']:
                details.append(f"Modify {file}")
        else:
            details.append(f"Update {self.stats['files_changed']} files")

        # Add statistics
        if self.stats['insertions'] > 0:
            details.append(f"Add {self.stats['insertions']} lines")
        if self.stats['deletions'] > 0:
            details.append(f"Remove {self.stats['deletions']} lines")

        return details

    def format_commit_message(self, commit_type: str, scope: Optional[str],
                             description: str, details: List[str]) -> str:
        """Format the final commit message"""
        # Header
        if scope:
            header = f"{commit_type}({scope}): {description}"
        else:
            header = f"{commit_type}: {description}"

        # Body (if we have details)
        body = ""
        if details:
            body = "\n\n" + "\n".join(f"- {detail}" for detail in details)

        return header + body


def main():
    parser = argparse.ArgumentParser(
        description='Generate smart commit messages from staged changes'
    )
    parser.add_argument(
        '--commit', '-c',
        action='store_true',
        help='Automatically commit with generated message'
    )
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Edit message before committing'
    )
    parser.add_argument(
        '--dry-run', '-d',
        action='store_true',
        help='Show analysis without generating message'
    )

    args = parser.parse_args()

    # Analyze changes
    analyzer = CommitAnalyzer()

    print("🔍 Analyzing staged changes...")
    if not analyzer.get_staged_diff():
        sys.exit(1)

    print(f"📊 Found {analyzer.stats['files_changed']} file(s) changed")
    print(f"   +{analyzer.stats['insertions']} -{analyzer.stats['deletions']} lines")

    if args.dry_run:
        print("\n📁 Files:")
        for file in analyzer.stats['files']:
            print(f"   - {file}")
        sys.exit(0)

    # Generate commit message
    print("\n🤖 Generating commit message...")
    commit_type, scope, description, details = analyzer.analyze_changes()
    message = analyzer.format_commit_message(commit_type, scope, description, details)

    print("\n" + "="*60)
    print(message)
    print("="*60)

    # Commit or show message
    if args.commit or args.interactive:
        if args.interactive:
            # Write to temp file and open editor
            import tempfile
            import os

            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(message)
                temp_file = f.name

            editor = os.environ.get('EDITOR', 'vim')
            subprocess.run([editor, temp_file])

            with open(temp_file, 'r') as f:
                message = f.read().strip()

            os.unlink(temp_file)

        if message:
            try:
                subprocess.run(['git', 'commit', '-m', message], check=True)
                print("\n✅ Changes committed successfully!")
            except subprocess.CalledProcessError:
                print("\n❌ Commit failed")
                sys.exit(1)
    else:
        print("\nℹ️  Use --commit to commit with this message")
        print("   Use --interactive to edit before committing")


if __name__ == '__main__':
    main()
