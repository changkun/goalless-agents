#!/usr/bin/env python3
"""
Prompt Optimizer - Analyze and optimize prompts to reduce token usage.
Provides insights on verbosity, redundancy, and suggests improvements.
"""

import sys
import re
from typing import Optional
from dataclasses import dataclass


@dataclass
class OptimizationSuggestion:
    line: int
    original: str
    optimized: str
    category: str
    savings: int  # approximate tokens saved


class PromptAnalyzer:
    def __init__(self):
        self.suggestions: list[OptimizationSuggestion] = []
        self.original_tokens = 0
        self.optimized_tokens = 0

    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation (1 token ≈ 4 chars for English)."""
        return len(text) // 4 + len(text.split())

    def analyze(self, text: str) -> list[OptimizationSuggestion]:
        """Analyze prompt and return optimization suggestions."""
        self.suggestions = []
        self.original_tokens = self.estimate_tokens(text)

        lines = text.split('\n')
        for i, line in enumerate(lines, 1):
            if not line.strip():
                continue

            self._check_redundancy(line, i)
            self._check_verbosity(line, i)
            self._check_filler_words(line, i)
            self._check_formatting(line, i)

        # Calculate total optimized tokens
        optimized = text
        for suggestion in self.suggestions:
            optimized = optimized.replace(suggestion.original, suggestion.optimized)
        self.optimized_tokens = self.estimate_tokens(optimized)

        return self.suggestions

    def _check_redundancy(self, line: str, line_num: int):
        """Check for redundant phrases."""
        redundant_pairs = [
            (r'\b(that\s+)?is\s+essentially\b', 'is'),
            (r'\bbasically\s+', ''),
            (r'\bsoberly speaking,?\s*', ''),
            (r'\bin my opinion,?\s*', ''),
            (r'\bI think\s+that\s+', ''),
        ]

        for pattern, replacement in redundant_pairs:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                original = match.group(0)
                optimized = re.sub(pattern, replacement, line, flags=re.IGNORECASE)
                if original.strip() and optimized != line:
                    self.suggestions.append(OptimizationSuggestion(
                        line=line_num,
                        original=original,
                        optimized=replacement,
                        category='redundancy',
                        savings=self.estimate_tokens(original) - self.estimate_tokens(replacement)
                    ))

    def _check_verbosity(self, line: str, line_num: int):
        """Check for unnecessarily verbose constructions."""
        verbose_patterns = [
            (r'\bat this point in time\b', 'now'),
            (r'\bat the end of the day\b', 'ultimately'),
            (r'\bdue to the fact that\b', 'because'),
            (r'\bin the event that\b', 'if'),
            (r'\bhas the ability to\b', 'can'),
            (r'\bcomes to the conclusion that\b', 'concludes'),
        ]

        for pattern, replacement in verbose_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                original = match.group(0)
                self.suggestions.append(OptimizationSuggestion(
                    line=line_num,
                    original=original,
                    optimized=replacement,
                    category='verbosity',
                    savings=self.estimate_tokens(original) - self.estimate_tokens(replacement)
                ))

    def _check_filler_words(self, line: str, line_num: int):
        """Check for unnecessary filler words."""
        filler_patterns = [
            (r'\b(well|actually|apparently|allegedly|seemingly|perhaps)\s+', ''),
            (r'\b(just\s+)?somewhat\s+', ''),
            (r'\bvery\s+', ''),
            (r'\breturn to the point\b', ''),
        ]

        for pattern, replacement in filler_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                original = match.group(0).strip()
                if original:
                    self.suggestions.append(OptimizationSuggestion(
                        line=line_num,
                        original=original,
                        optimized=replacement,
                        category='filler',
                        savings=self.estimate_tokens(original) - self.estimate_tokens(replacement)
                    ))

    def _check_formatting(self, line: str, line_num: int):
        """Check for formatting improvements."""
        # Excessive whitespace
        if '  ' in line:
            optimized = re.sub(r'  +', ' ', line)
            savings = self.estimate_tokens(line) - self.estimate_tokens(optimized)
            if savings > 0:
                self.suggestions.append(OptimizationSuggestion(
                    line=line_num,
                    original=line.strip(),
                    optimized=optimized.strip(),
                    category='formatting',
                    savings=savings
                ))


def format_output(analyzer: PromptAnalyzer, verbose: bool = False):
    """Format and print analysis results."""
    if not analyzer.suggestions:
        print("✓ No optimizations found!")
        return

    print(f"\n📊 Prompt Analysis Results")
    print(f"{'=' * 60}")
    print(f"Original: ~{analyzer.original_tokens} tokens")
    print(f"Optimized: ~{analyzer.optimized_tokens} tokens")
    print(f"Potential savings: {analyzer.original_tokens - analyzer.optimized_tokens} tokens "
          f"({((analyzer.original_tokens - analyzer.optimized_tokens) / analyzer.original_tokens * 100):.1f}%)")
    print(f"{'=' * 60}\n")

    # Group by category
    by_category = {}
    for sugg in analyzer.suggestions:
        if sugg.category not in by_category:
            by_category[sugg.category] = []
        by_category[sugg.category].append(sugg)

    for category in ['redundancy', 'verbosity', 'filler', 'formatting']:
        if category in by_category:
            print(f"🔴 {category.upper()} ({len(by_category[category])} issues)")
            for sugg in by_category[category]:
                print(f"  Line {sugg.line}: '{sugg.original}' → '{sugg.optimized}'")
                if verbose:
                    print(f"    💾 Saves ~{sugg.savings} tokens")
            print()


def main():
    if len(sys.argv) < 2:
        print("Usage: python prompt_optimizer.py <file.txt> [--verbose]")
        print("       python prompt_optimizer.py - [--verbose]  (read from stdin)")
        sys.exit(1)

    verbose = '--verbose' in sys.argv
    file_arg = sys.argv[1]

    try:
        if file_arg == '-':
            text = sys.stdin.read()
        else:
            with open(file_arg, 'r') as f:
                text = f.read()
    except FileNotFoundError:
        print(f"Error: File '{file_arg}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    analyzer = PromptAnalyzer()
    analyzer.analyze(text)
    format_output(analyzer, verbose)


if __name__ == '__main__':
    main()
