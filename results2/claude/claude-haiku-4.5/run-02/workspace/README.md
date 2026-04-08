# Standup Generator

A CLI tool that generates daily standup summaries from your git commits using Claude AI.

## Features

- 📝 Automatically fetches your recent git commits
- 🤖 Uses Claude to generate a concise, professional summary
- ⚡ Quick and easy to use
- 🎯 Creates ready-to-share standup bullets

## Installation

```bash
npm install
```

## Setup

1. Get your API key from [Anthropic](https://console.anthropic.com)
2. Set the environment variable:

```bash
export ANTHROPIC_API_KEY=your-key-here
```

## Usage

```bash
npm start                    # Summarize last 10 commits
npm start -- --limit 20      # Summarize last 20 commits
npm start -- --help          # Show help
```

Or if installed globally:

```bash
standup
standup --limit 15
```

## Example Output

```
📝 Recent Commits:
   a1b2c3d Add user authentication flow
   d4e5f6g Refactor database queries
   h7i8j9k Fix login validation bug
   k0l1m2n Add email notifications
   n3o4p5q Update UI components

🎯 Standup Summary:

- Implemented user authentication flow with secure password handling and session management
- Optimized database queries to improve performance and reduce load times
- Fixed critical bug in login validation that was preventing users from authenticating
- Added email notification system for important user actions
- Updated UI components to improve user experience and accessibility
```

## How It Works

1. Runs `git log` to fetch your recent commits
2. Sends them to Claude API with a prompt to generate a standup summary
3. Returns formatted bullet points ready for your team standup

## Requirements

- Node.js 16+
- Git repository (must be run from a git directory)
- ANTHROPIC_API_KEY environment variable set
