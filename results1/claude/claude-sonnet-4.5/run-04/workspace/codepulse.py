#!/usr/bin/env python3
"""
CodePulse - Analyze code complexity and health metrics
"""
import os
import sys
import argparse
from pathlib import Path
from collections import defaultdict
import re


class CodeAnalyzer:
    def __init__(self):
        self.stats = {
            'total_files': 0,
            'total_lines': 0,
            'code_lines': 0,
            'comment_lines': 0,
            'blank_lines': 0,
            'by_language': defaultdict(lambda: {
                'files': 0, 'lines': 0, 'code': 0, 'comments': 0
            }),
            'complexity': []
        }

        self.language_extensions = {
            'Python': ['.py'],
            'JavaScript': ['.js', '.jsx', '.mjs'],
            'TypeScript': ['.ts', '.tsx'],
            'Go': ['.go'],
            'Rust': ['.rs'],
            'C/C++': ['.c', '.cpp', '.h', '.hpp', '.cc'],
            'Java': ['.java'],
            'Ruby': ['.rb'],
            'PHP': ['.php'],
            'Shell': ['.sh', '.bash'],
            'HTML': ['.html', '.htm'],
            'CSS': ['.css', '.scss', '.sass'],
            'Markdown': ['.md'],
            'JSON': ['.json'],
            'YAML': ['.yaml', '.yml'],
            'XML': ['.xml'],
        }

        self.comment_patterns = {
            'Python': (r'#', r'"""', r"'''"),
            'JavaScript': (r'//', r'/\*', r'\*/'),
            'TypeScript': (r'//', r'/\*', r'\*/'),
            'Go': (r'//', r'/\*', r'\*/'),
            'Rust': (r'//', r'/\*', r'\*/'),
            'C/C++': (r'//', r'/\*', r'\*/'),
            'Java': (r'//', r'/\*', r'\*/'),
            'Ruby': (r'#', r'=begin', r'=end'),
            'PHP': (r'//', r'/\*', r'#'),
            'Shell': (r'#',),
            'HTML': (r'<!--', r'-->'),
            'CSS': (r'/\*', r'\*/'),
        }

    def detect_language(self, file_path):
        """Detect programming language from file extension"""
        ext = Path(file_path).suffix.lower()
        for lang, exts in self.language_extensions.items():
            if ext in exts:
                return lang
        return 'Other'

    def is_comment_line(self, line, language):
        """Check if line is a comment"""
        line = line.strip()
        if not line:
            return False

        patterns = self.comment_patterns.get(language, ())
        for pattern in patterns:
            if line.startswith(pattern.replace('\\', '')):
                return True
        return False

    def calculate_complexity(self, content, language):
        """Calculate cyclomatic complexity approximation"""
        complexity = 1  # Base complexity

        # Control flow keywords that increase complexity
        keywords = [
            r'\bif\b', r'\belse\b', r'\belif\b', r'\bfor\b', r'\bwhile\b',
            r'\bcase\b', r'\bcatch\b', r'\band\b', r'\bor\b', r'\b\?\b'
        ]

        for keyword in keywords:
            complexity += len(re.findall(keyword, content, re.IGNORECASE))

        return complexity

    def analyze_file(self, file_path):
        """Analyze a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                content = ''.join(lines)
        except Exception as e:
            print(f"Error reading {file_path}: {e}", file=sys.stderr)
            return

        language = self.detect_language(file_path)
        total_lines = len(lines)
        code_lines = 0
        comment_lines = 0
        blank_lines = 0

        in_multiline_comment = False

        for line in lines:
            stripped = line.strip()

            if not stripped:
                blank_lines += 1
            elif self.is_comment_line(stripped, language):
                comment_lines += 1
            else:
                code_lines += 1

        complexity = self.calculate_complexity(content, language)

        # Update statistics
        self.stats['total_files'] += 1
        self.stats['total_lines'] += total_lines
        self.stats['code_lines'] += code_lines
        self.stats['comment_lines'] += comment_lines
        self.stats['blank_lines'] += blank_lines

        lang_stats = self.stats['by_language'][language]
        lang_stats['files'] += 1
        lang_stats['lines'] += total_lines
        lang_stats['code'] += code_lines
        lang_stats['comments'] += comment_lines

        self.stats['complexity'].append({
            'file': str(file_path),
            'complexity': complexity,
            'lines': total_lines
        })

    def analyze_directory(self, directory, exclude_patterns=None):
        """Analyze all files in directory"""
        exclude_patterns = exclude_patterns or [
            'node_modules', '.git', '__pycache__', 'venv', '.venv',
            'dist', 'build', '.next', 'target', '.cargo'
        ]

        path = Path(directory)

        for file_path in path.rglob('*'):
            if file_path.is_file():
                # Check exclusions
                if any(excl in str(file_path) for excl in exclude_patterns):
                    continue

                # Check if it's a code file
                if self.detect_language(file_path) != 'Other':
                    self.analyze_file(file_path)

    def generate_report(self, detailed=False):
        """Generate analysis report"""
        print("\n" + "="*60)
        print("  CODE PULSE - Code Analysis Report")
        print("="*60)

        print(f"\n📊 Overview:")
        print(f"  Total Files:    {self.stats['total_files']}")
        print(f"  Total Lines:    {self.stats['total_lines']:,}")
        print(f"  Code Lines:     {self.stats['code_lines']:,} ({self._percent(self.stats['code_lines'], self.stats['total_lines'])}%)")
        print(f"  Comment Lines:  {self.stats['comment_lines']:,} ({self._percent(self.stats['comment_lines'], self.stats['total_lines'])}%)")
        print(f"  Blank Lines:    {self.stats['blank_lines']:,} ({self._percent(self.stats['blank_lines'], self.stats['total_lines'])}%)")

        print(f"\n🔤 Languages:")
        sorted_langs = sorted(
            self.stats['by_language'].items(),
            key=lambda x: x[1]['lines'],
            reverse=True
        )

        for lang, stats in sorted_langs[:10]:
            print(f"  {lang:15} {stats['files']:4} files  {stats['lines']:6,} lines  "
                  f"{self._bar(stats['lines'], self.stats['total_lines'])}")

        print(f"\n⚡ Complexity Analysis:")
        complexities = self.stats['complexity']
        if complexities:
            avg_complexity = sum(c['complexity'] for c in complexities) / len(complexities)
            print(f"  Average Complexity: {avg_complexity:.1f}")

            # Top 5 most complex files
            most_complex = sorted(complexities, key=lambda x: x['complexity'], reverse=True)[:5]
            print(f"\n  Most Complex Files:")
            for item in most_complex:
                rel_path = os.path.relpath(item['file'])
                print(f"    {item['complexity']:3} - {rel_path}")

        if detailed:
            self._detailed_report()

        print("\n" + "="*60 + "\n")

    def _percent(self, part, total):
        """Calculate percentage"""
        return round(100 * part / total, 1) if total > 0 else 0

    def _bar(self, value, max_value, width=20):
        """Create a simple progress bar"""
        if max_value == 0:
            return '░' * width
        filled = int(width * value / max_value)
        return '█' * filled + '░' * (width - filled)

    def _detailed_report(self):
        """Generate detailed breakdown"""
        print(f"\n📈 Detailed Language Breakdown:")
        for lang, stats in sorted(self.stats['by_language'].items()):
            if stats['files'] > 0:
                print(f"\n  {lang}:")
                print(f"    Files:    {stats['files']}")
                print(f"    Lines:    {stats['lines']:,}")
                print(f"    Code:     {stats['code']:,}")
                print(f"    Comments: {stats['comments']:,}")
                comment_ratio = self._percent(stats['comments'], stats['lines'])
                print(f"    Comment Ratio: {comment_ratio}%")


def main():
    parser = argparse.ArgumentParser(
        description='CodePulse - Analyze code complexity and health metrics',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Path to analyze (default: current directory)'
    )
    parser.add_argument(
        '-d', '--detailed',
        action='store_true',
        help='Show detailed analysis'
    )
    parser.add_argument(
        '-e', '--exclude',
        nargs='+',
        help='Additional patterns to exclude'
    )

    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"Error: Path '{args.path}' does not exist", file=sys.stderr)
        sys.exit(1)

    analyzer = CodeAnalyzer()

    print(f"Analyzing: {path.absolute()}")

    if path.is_file():
        analyzer.analyze_file(path)
    else:
        analyzer.analyze_directory(path, args.exclude)

    analyzer.generate_report(detailed=args.detailed)


if __name__ == '__main__':
    main()
