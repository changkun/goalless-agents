#!/usr/bin/env python3
"""
CodeScope - A fast, extensible code quality analyzer
Detects code smells, security issues, and suggests improvements
"""

import os
import re
import json
import argparse
from pathlib import Path
from typing import List, Dict, Set
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class Issue:
    file: str
    line: int
    severity: str  # critical, warning, info
    category: str
    message: str
    suggestion: str = ""


class LanguageAnalyzer:
    """Base analyzer with common patterns"""

    def __init__(self, config: dict):
        self.config = config
        self.issues: List[Issue] = []

    def analyze_file(self, filepath: Path, content: str):
        """Override in subclasses"""
        pass

    def check_line_length(self, filepath: Path, content: str, max_length: int = 120):
        """Check for overly long lines"""
        for i, line in enumerate(content.split('\n'), 1):
            if len(line) > max_length:
                self.issues.append(Issue(
                    file=str(filepath),
                    line=i,
                    severity="info",
                    category="style",
                    message=f"Line exceeds {max_length} characters ({len(line)} chars)",
                    suggestion=f"Consider breaking into multiple lines"
                ))

    def check_todos(self, filepath: Path, content: str):
        """Find TODO/FIXME/HACK comments"""
        patterns = [
            (r'TODO', 'info', 'Unresolved TODO'),
            (r'FIXME', 'warning', 'Code marked for fixing'),
            (r'HACK', 'warning', 'Hack/workaround present'),
            (r'XXX', 'warning', 'Attention needed'),
        ]

        for i, line in enumerate(content.split('\n'), 1):
            for pattern, severity, msg in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self.issues.append(Issue(
                        file=str(filepath),
                        line=i,
                        severity=severity,
                        category="maintenance",
                        message=msg,
                        suggestion="Address or track in issue tracker"
                    ))


class PythonAnalyzer(LanguageAnalyzer):
    """Python-specific analysis"""

    def analyze_file(self, filepath: Path, content: str):
        self.check_line_length(filepath, content)
        self.check_todos(filepath, content)
        self.check_python_specific(filepath, content)

    def check_python_specific(self, filepath: Path, content: str):
        checks = [
            (r'except:', 'warning', 'Bare except clause', 'Specify exception type'),
            (r'eval\(', 'critical', 'Dangerous eval() usage', 'Use safer alternatives'),
            (r'exec\(', 'critical', 'Dangerous exec() usage', 'Refactor to avoid exec'),
            (r'import \*', 'warning', 'Wildcard import', 'Import specific names'),
            (r'print\(.*password', 'critical', 'Potential password leak', 'Remove debug print'),
            (r'print\(.*token', 'critical', 'Potential token leak', 'Remove debug print'),
            (r'# noqa|# type: ignore', 'info', 'Linter suppression', 'Fix root cause if possible'),
        ]

        for i, line in enumerate(content.split('\n'), 1):
            for pattern, severity, msg, suggestion in checks:
                if re.search(pattern, line, re.IGNORECASE):
                    self.issues.append(Issue(
                        file=str(filepath),
                        line=i,
                        severity=severity,
                        category="code-quality",
                        message=msg,
                        suggestion=suggestion
                    ))


class JavaScriptAnalyzer(LanguageAnalyzer):
    """JavaScript/TypeScript analysis"""

    def analyze_file(self, filepath: Path, content: str):
        self.check_line_length(filepath, content)
        self.check_todos(filepath, content)
        self.check_js_specific(filepath, content)

    def check_js_specific(self, filepath: Path, content: str):
        checks = [
            (r'\bvar\b', 'warning', 'Use let/const instead of var', 'Replace with let or const'),
            (r'==(?!=)', 'warning', 'Use === for strict equality', 'Replace == with ==='),
            (r'console\.log', 'info', 'Console log statement', 'Remove before production'),
            (r'eval\(', 'critical', 'Dangerous eval() usage', 'Use safer alternatives'),
            (r'innerHTML\s*=', 'warning', 'Potential XSS via innerHTML', 'Use textContent or sanitize'),
            (r'document\.write', 'warning', 'document.write usage', 'Use modern DOM methods'),
        ]

        for i, line in enumerate(content.split('\n'), 1):
            for pattern, severity, msg, suggestion in checks:
                if re.search(pattern, line):
                    self.issues.append(Issue(
                        file=str(filepath),
                        line=i,
                        severity=severity,
                        category="code-quality",
                        message=msg,
                        suggestion=suggestion
                    ))


class GoAnalyzer(LanguageAnalyzer):
    """Go-specific analysis"""

    def analyze_file(self, filepath: Path, content: str):
        self.check_line_length(filepath, content)
        self.check_todos(filepath, content)
        self.check_go_specific(filepath, content)

    def check_go_specific(self, filepath: Path, content: str):
        checks = [
            (r'panic\(', 'warning', 'Panic usage', 'Return error instead when possible'),
            (r'//\s*nolint', 'info', 'Linter suppression', 'Fix root cause if possible'),
            (r'fmt\.Print(?!f|ln)', 'info', 'Print without format', 'Consider using Printf'),
        ]

        for i, line in enumerate(content.split('\n'), 1):
            for pattern, severity, msg, suggestion in checks:
                if re.search(pattern, line):
                    self.issues.append(Issue(
                        file=str(filepath),
                        line=i,
                        severity=severity,
                        category="code-quality",
                        message=msg,
                        suggestion=suggestion
                    ))


class CodeScope:
    """Main analyzer orchestrator"""

    ANALYZERS = {
        '.py': PythonAnalyzer,
        '.js': JavaScriptAnalyzer,
        '.jsx': JavaScriptAnalyzer,
        '.ts': JavaScriptAnalyzer,
        '.tsx': JavaScriptAnalyzer,
        '.go': GoAnalyzer,
    }

    DEFAULT_IGNORE = {
        'node_modules', '.git', '__pycache__', '.venv', 'venv',
        'dist', 'build', '.next', '.cache', 'target', 'vendor'
    }

    def __init__(self, config_path: str = None):
        self.config = self.load_config(config_path)
        self.ignore_dirs = self.DEFAULT_IGNORE | set(self.config.get('ignore', []))
        self.all_issues: List[Issue] = []
        self.stats = defaultdict(int)

    def load_config(self, config_path: str) -> dict:
        """Load configuration file"""
        if config_path and os.path.exists(config_path):
            with open(config_path) as f:
                return json.load(f)
        return {}

    def should_analyze(self, filepath: Path) -> bool:
        """Check if file should be analyzed"""
        if any(ignored in filepath.parts for ignored in self.ignore_dirs):
            return False
        return filepath.suffix in self.ANALYZERS

    def analyze_directory(self, root_path: str):
        """Recursively analyze all files in directory"""
        root = Path(root_path)

        for filepath in root.rglob('*'):
            if filepath.is_file() and self.should_analyze(filepath):
                self.analyze_file(filepath)

    def analyze_file(self, filepath: Path):
        """Analyze a single file"""
        self.stats['files_analyzed'] += 1

        try:
            content = filepath.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return

        analyzer_class = self.ANALYZERS.get(filepath.suffix)
        if analyzer_class:
            analyzer = analyzer_class(self.config)
            analyzer.analyze_file(filepath, content)
            self.all_issues.extend(analyzer.issues)

            for issue in analyzer.issues:
                self.stats[f'severity_{issue.severity}'] += 1
                self.stats[f'category_{issue.category}'] += 1

    def generate_report(self, format: str = 'text') -> str:
        """Generate analysis report"""
        if format == 'json':
            return json.dumps({
                'stats': dict(self.stats),
                'issues': [asdict(issue) for issue in self.all_issues]
            }, indent=2)

        # Text report
        lines = []
        lines.append("=" * 80)
        lines.append("CodeScope Analysis Report")
        lines.append("=" * 80)
        lines.append(f"\nFiles analyzed: {self.stats['files_analyzed']}")
        lines.append(f"Total issues: {len(self.all_issues)}")

        if self.all_issues:
            lines.append(f"\nBy severity:")
            for severity in ['critical', 'warning', 'info']:
                count = self.stats.get(f'severity_{severity}', 0)
                if count:
                    lines.append(f"  {severity.capitalize()}: {count}")

            lines.append(f"\nBy category:")
            categories = set(issue.category for issue in self.all_issues)
            for category in sorted(categories):
                count = self.stats.get(f'category_{category}', 0)
                lines.append(f"  {category}: {count}")

            lines.append("\n" + "=" * 80)
            lines.append("Issues")
            lines.append("=" * 80)

            # Group by file
            by_file = defaultdict(list)
            for issue in self.all_issues:
                by_file[issue.file].append(issue)

            for filepath in sorted(by_file.keys()):
                lines.append(f"\n{filepath}")
                lines.append("-" * len(filepath))

                for issue in sorted(by_file[filepath], key=lambda x: x.line):
                    severity_marker = {
                        'critical': '🔴',
                        'warning': '🟡',
                        'info': '🔵'
                    }.get(issue.severity, '⚪')

                    lines.append(f"  {severity_marker} Line {issue.line}: {issue.message}")
                    if issue.suggestion:
                        lines.append(f"     → {issue.suggestion}")
        else:
            lines.append("\n✅ No issues found!")

        lines.append("\n" + "=" * 80)
        return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='CodeScope - Fast code quality analyzer'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Directory or file to analyze (default: current directory)'
    )
    parser.add_argument(
        '-c', '--config',
        help='Path to config file'
    )
    parser.add_argument(
        '-f', '--format',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Write report to file instead of stdout'
    )

    args = parser.parse_args()

    analyzer = CodeScope(args.config)

    path = Path(args.path)
    if path.is_file():
        analyzer.analyze_file(path)
    else:
        analyzer.analyze_directory(args.path)

    report = analyzer.generate_report(args.format)

    if args.output:
        Path(args.output).write_text(report)
        print(f"Report written to {args.output}")
    else:
        print(report)


if __name__ == '__main__':
    main()
