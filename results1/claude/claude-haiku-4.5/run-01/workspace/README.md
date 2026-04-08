# Prompt Optimizer

A CLI tool that analyzes prompts and suggests optimizations to reduce token usage. Perfect for developers working with Claude API and other LLM services.

## Features

- **Redundancy Detection**: Finds and flags redundant phrases
- **Verbosity Analysis**: Identifies unnecessarily verbose constructions
- **Filler Word Detection**: Spots unnecessary filler words
- **Formatting Issues**: Catches whitespace and formatting waste
- **Token Savings Estimation**: Provides approximate token savings
- **Category Grouping**: Organizes suggestions by type

## Installation

```bash
chmod +x prompt_optimizer.py
```

## Usage

Analyze a file:
```bash
python prompt_optimizer.py prompt.txt
```

Analyze with detailed savings breakdown:
```bash
python prompt_optimizer.py prompt.txt --verbose
```

Analyze from stdin:
```bash
echo "Your prompt here" | python prompt_optimizer.py -
cat prompt.txt | python prompt_optimizer.py -
```

## Example

```bash
$ python prompt_optimizer.py example_prompt.txt

📊 Prompt Analysis Results
============================================================
Original: ~150 tokens
Optimized: ~110 tokens
Potential savings: 40 tokens (26.7%)
============================================================

🔴 REDUNDANCY (2 issues)
  Line 1: 'basically is designed to essentially' → 'is'
  Line 3: 'which is very helpful' → ''

🔴 VERBOSITY (4 issues)
  Line 3: 'Due to the fact that' → 'because'
  Line 3: 'At this point in time' → 'now'
  Line 5: 'At the end of the day' → 'ultimately'
  Line 5: 'has the ability to' → 'can'

🔴 FILLER (3 issues)
  Line 7: 'Well' → ''
  Line 7: 'apparently' → ''
  Line 7: 'somewhat' → ''

🔴 FORMATTING (1 issues)
  Line 1: 'Write  a  function' → 'Write a function'
```

## How It Works

1. **Token Estimation**: Uses a simple 4-char per token approximation for quick analysis
2. **Pattern Matching**: Identifies common redundancies, verbose phrases, and filler words
3. **Categorization**: Groups issues by type for easy navigation
4. **Savings Calculation**: Estimates token savings for each optimization

## Optimization Categories

- **Redundancy**: Phrases that repeat the same meaning unnecessarily
- **Verbosity**: Unnecessarily long constructions that can be simplified
- **Filler**: Words that don't add meaning (just, well, apparently, etc.)
- **Formatting**: Whitespace and formatting that wastes tokens

## Tips for Best Results

1. Run on your actual prompts before sending to Claude
2. Review suggestions and apply those that preserve meaning
3. Use `--verbose` to see exact token savings for each fix
4. Test outputs to ensure quality isn't compromised

## Future Enhancements

- Machine learning-based suggestions
- Prompt template library
- Integration with Claude API for real token counting
- Multi-language support
- Tone preservation analysis
- Custom rule configuration
