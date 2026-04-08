# Token Dashboard

A CLI utility for tracking and analyzing token usage across Claude API operations.

## Features

- Track token usage per request/session
- View savings from RTK token optimization
- Generate usage reports by model and time period
- Real-time dashboard display

## Installation

```bash
pip install -e .
```

## Usage

```bash
token-dashboard --help
```

## Examples

```bash
# Show current token dashboard
token-dashboard show

# Generate usage report for the last 7 days
token-dashboard report --days 7

# Track specific operation
token-dashboard track "My operation name"
```
