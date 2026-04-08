# RTK - Rust Token Killer

**RTK** is a token-optimized CLI proxy designed to provide significant savings on development operations when using AI assistants.

## Features

- **Transparent Proxying**: Run any command through RTK (e.g., `rtk git status`).
- **Analytics**: Track your token savings with `rtk gain`.
- **Easy Integration**: Hooks into Claude Code for automatic token optimization.

## Usage

```bash
rtk gain              # Show token savings analytics
rtk <command> [args]  # Proxy any command
```

## Implementation

This version is implemented in TypeScript using `ts-node` for rapid development and flexibility.

## Installation

```bash
npm install
npm run build
```
