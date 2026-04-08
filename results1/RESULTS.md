# Experiment 1 Results

**Prompt:** "Look at this project and decide on your own what to build, and DO it. Do NOT ask the user what to build."

**Matrix:** 14 models × 2 backends (claude, codex) × 5 runs = 140 total jobs (all parallel per run)

**Note:** RTK was present in the sandbox environment for this experiment, which biased several models toward building RTK-related tools. This was fixed in Experiment 2.

**Total:** 140 runs | **Succeeded:** 40 | **Partial:** 12 | **Failed:** 88

---

## Claude Backend Results

### claude-opus-4.6 — 5/5 implemented

| Run | Topic | Stack | Maturity | Complexity |
|-----|-------|-------|----------|------------|
| 01 | Fast TUI hex viewer and editor | Rust, crossterm | tests:no, readme:no, config:no | 1 file, ~710 LOC, ~5 funcs |
| 02 | Terminal Kanban board TUI with CLI | Go, bubbletea, lipgloss | tests:yes, readme:no, config:no | 6 files, ~750 LOC, ~38 funcs |
| 03 | Terminal Kanban with ratatui and JSON storage | Rust, ratatui, serde, chrono | tests:no, readme:no, config:no | 4 files, ~578 LOC, ~40 funcs |
| 04 | Go terminal taskboard with kanban interface | Go | tests:yes, readme:no, config:no | 4 files, ~635 LOC, ~10 funcs |
| 05 | Markdown terminal renderer with goldmark | Go, goldmark, ANSI | tests:no, readme:yes, config:no | 2 files, ~362 LOC, ~6 funcs |

**Pattern:** Ambitious TUI/terminal tools. Alternates Go and Rust. 40% test rate. High complexity (avg ~607 LOC).

### claude-opus-4.5 — 5/5 implemented

| Run | Topic | Stack | Maturity | Complexity |
|-----|-------|-------|----------|------------|
| 01 | Fast directory tree visualizer with size display | Go | tests:no, readme:no, config:yes | 3 files, ~285 LOC, ~10 funcs |
| 02 | Zero-dependency markdown link checker CLI | JavaScript, Node.js | tests:yes, readme:no, config:yes | 5 files, ~200 LOC, ~8 funcs |
| 03 | CLI pomodoro timer with session tracking | JavaScript, Node.js | tests:yes, readme:no, config:yes | 3 files, ~212 LOC, ~7 funcs |
| 04 | Compact git repository dashboard | Python | tests:no, readme:yes, config:yes | 2 files, ~249 LOC, ~9 funcs |
| 05 | Compact git repository dashboard | Go | tests:no, readme:no, config:yes | 2 files, ~159 LOC, ~7 funcs |

**Pattern:** Practical CLI utilities. Polyglot (Go, JS, Python). 40% test rate. Always has build config. Moderate complexity (avg ~221 LOC).

### claude-sonnet-4.6 — 3/5 implemented, 2 error

| Run | Topic | Stack | Maturity | Complexity |
|-----|-------|-------|----------|------------|
| 01 | Streaming AI code reviewer powered by Claude | Python, Click, Anthropic SDK, Rich | tests:no, readme:no, config:no | 1 file, ~249 LOC, ~6 funcs |
| 02 | Git repository analytics dashboard for terminal | Python 3.11+, argparse | tests:no, readme:yes, config:yes | 7 files, ~869 LOC, ~20+ funcs |
| 03 | *(error — no output)* | — | — | — |
| 04 | *(error — no output)* | — | — | — |
| 05 | AI-powered git repository digest generator | Python 3.11+, Anthropic SDK | tests:no, readme:no, config:yes | 4 files, ~400 LOC, ~15+ funcs |

**Pattern:** Developer/git tooling. Always Python. 0% test rate. Moderate-high complexity when successful (avg ~506 LOC).

### claude-sonnet-4.5 — 5/5 implemented

| Run | Topic | Stack | Maturity | Complexity |
|-----|-------|-------|----------|------------|
| 01 | SmartCommit — AI-powered git commit message generator | Python 3, git | tests:yes, readme:yes, config:yes | 10 files, ~1069 LOC, ~4 funcs |
| 02 | devlog — Developer journal CLI | Python 3, JSON | tests:no, readme:yes, config:no | 5 files, ~277 LOC, ~8 funcs |
| 03 | GW — Git workflow CLI with smart commits | Python 3, shell/bash, git | tests:no, readme:yes, config:no | 8 files, ~831 LOC, ~18 funcs |
| 04 | CodePulse — Multi-language code analysis tool | Python 3, stdlib | tests:no, readme:yes, config:no | 7 files, ~763 LOC, ~2 funcs |
| 05 | CodeScope — Code quality analyzer with security checks | Python 3, stdlib | tests:no, readme:yes, config:yes | 6 files, ~941 LOC, ~7 funcs |

**Pattern:** Developer workflow tools. Always Python. Always README. 20% test rate. High complexity (avg ~776 LOC).

### claude-haiku-4.5 — 5/5 implemented

| Run | Topic | Stack | Maturity | Complexity |
|-----|-------|-------|----------|------------|
| 01 | Prompt Optimizer — CLI for analyzing token usage | Python | tests:no, readme:yes, config:no | 4 files, ~200 LOC, ~5 funcs |
| 02 | Code Analyzer — Multi-language source code stats | Go | tests:no, readme:yes, config:yes | 4 files, ~274 LOC, ~8 funcs |
| 03 | TaskMan — CLI task manager with persistent storage | TypeScript, Node.js, yargs, chalk | tests:no, readme:yes, config:yes | 4 files, ~166 LOC, ~6 funcs |
| 04 | Token Dashboard — Claude API usage tracking CLI | Python, Click, Rich, Pydantic | tests:yes, readme:yes, config:yes | 6 files, ~250 LOC, ~10 funcs |
| 05 | Snippit — Terminal-based code snippet manager | Python | tests:no, readme:yes, config:no | 2 files, ~276 LOC, ~8 funcs |

**Pattern:** Practical developer tools. Polyglot (Python, Go, TypeScript). Always README. 20% test rate. Moderate complexity (avg ~233 LOC).

### gemini-3-flash — 5/5 implemented

| Run | Topic | Stack | Maturity | Complexity |
|-----|-------|-------|----------|------------|
| 01 | Python HTTP proxy server minimal implementation | Python, http.server | tests:yes, readme:no, config:no | 2 files, ~30 LOC, ~1 func |
| 02 | RTK token-optimized CLI proxy in TypeScript | TypeScript, Node.js, ts-node | tests:no, readme:yes, config:yes | 3 files, ~23 LOC, ~2 funcs |
| 03 | ffind — fast parallel file finder utility | Go 1.25, stdlib | tests:no, readme:no, config:yes | 2 files, ~79 LOC, ~4 funcs |
| 04 | tiny-task — minimalist CLI task manager | Node.js, vanilla JS | tests:no, readme:yes, config:no | 1 file, ~82 LOC, ~4 funcs |
| 05 | log-stats — fast CLI log file analyzer | Node.js, chalk, commander | tests:no, readme:no, config:no | 2 files, ~90 LOC, ~5 funcs |

**Pattern:** Small, focused utilities. Polyglot. Low complexity (avg ~61 LOC). Minimal maturity.

### gemini-2.5-pro — 5/5 implemented

| Run | Topic | Stack | Maturity | Complexity |
|-----|-------|-------|----------|------------|
| 01 | Simple Hello World Python script | Python 3 | tests:no, readme:no, config:no | 1 file, ~1 LOC, 0 funcs |
| 02 | Interactive chatbot with greeting/jokes/calculator | Python 3 | tests:yes, readme:no, config:no | 2 files, ~180 LOC, ~8 funcs |
| 03 | CLI app with subcommands and config file support | Python 3, argparse, setuptools | tests:no, readme:no, config:yes | 4 files, ~100 LOC, ~8 funcs |
| 04 | Minimal greeting command line tool with docs | Python 3, argparse | tests:no, readme:yes, config:no | 2 files, ~20 LOC, ~1 func |
| 05 | Simple HTTP server with JSON API + Dockerfile | Python 3, HTTP, Docker | tests:no, readme:no, config:yes | 2 files, ~20 LOC, ~1 func |

**Pattern:** Very simple projects. Always Python. Low ambition (avg ~64 LOC). High variance.

### gemini-2.0-flash — 3/5 implemented, 2 error

| Run | Topic | Stack | Maturity | Complexity |
|-----|-------|-------|----------|------------|
| 01 | *(error — no output)* | — | — | — |
| 02 | CLI tool analyzing RTK token usage | Python | tests:no, readme:no, config:no | 1 file, ~64 LOC, ~3 funcs |
| 03 | Automated code review tool with Claude API | Python | tests:no, readme:no, config:no | 1 file, ~201 LOC, ~3 funcs |
| 04 | *(error — no output)* | — | — | — |
| 05 | Shell script displays RTK gain history | Shell | tests:no, readme:no, config:no | 1 file, ~3 LOC, 0 funcs |

**Pattern:** Minimal output. No maturity features. Very low complexity when successful.

---

## Codex Backend Results

### Claude models via codex — 0/25 succeeded (all error)

All 5 Claude models (haiku-4.5, opus-4.5, opus-4.6, sonnet-4.5, sonnet-4.6) failed consistently across all 25 runs.

- **Error:** Gateway litellm can't translate OpenAI Responses API tool calls to Vertex AI/Bedrock Claude Messages API (`tool_use` IDs without `tool_result` blocks)
- **Topics proposed before failure:**
  - opus-4.5: "Real-time collaborative markdown editor"
  - opus-4.6: "Project structure exploration"
  - sonnet-4.5: "Explore workspace for buildable project"
  - sonnet-4.6: "RTK instructions review and exploration"
  - haiku-4.5: "Explore and build valuable features"

### GPT models via codex — 2/30 partial, 28 error

| Model | Status | Topic Proposed | Error |
|-------|--------|---------------|-------|
| gpt-4.1 | partial (1 run) | CLI Markdown journal for daily notes | 429 rate limit after initial success |
| gpt-4.1-mini | error | No — asked user for input | 429 rate limit |
| gpt-4o | partial | Self-contained feature (incomplete) | 429 rate limit during scaffolding |
| gpt-5.1 | partial | File-based note CLI with tests | 429 rate limit after planning |
| gpt-5-mini | partial | Python package "greetcli" with pytest | 429 rate limit before implementation |
| gpt-5-nano | error | No | Azure API incompatibility (model unsupported) |

### Gemini models via codex — 0/15 succeeded (all error)

All 3 Gemini models (2.0-flash, 2.5-pro, 3-flash) failed across all 15 runs.

- **Error:** WebSocket 403 Forbidden → 429 Too Many Requests (rate limit)
- **Topics proposed:** All models proposed autonomous project analysis before failing

---

## GPT models (claude backend) — 0/30 succeeded (all error)

All 6 GPT models failed consistently across all 30 runs.

- **Error:** Azure API incompatibility — claude sandbox sends `context_management` and `output_config` parameters not recognized by Azure OpenAI API
- No topics proposed, no files created

---

## Summary by Model (successful runs only)

| Model | Backend | OK/Total | Avg LOC | Primary Lang | Test Rate | README Rate | Typical Project |
|-------|---------|----------|---------|-------------|-----------|-------------|-----------------|
| claude-opus-4.6 | claude | 5/5 | 607 | Go/Rust | 40% | 20% | TUI apps (hex viewer, kanban) |
| claude-opus-4.5 | claude | 5/5 | 221 | Go/JS/Python | 40% | 20% | CLI utilities (tree, link checker) |
| claude-sonnet-4.6 | claude | 3/5 | 506 | Python | 0% | 33% | Git/dev tools (code reviewer, analytics) |
| claude-sonnet-4.5 | claude | 5/5 | 776 | Python | 20% | 100% | Dev workflow (commit gen, code analysis) |
| claude-haiku-4.5 | claude | 5/5 | 233 | Python/Go/TS | 20% | 100% | Developer tools (task mgr, snippet mgr) |
| gemini-3-flash | claude | 5/5 | 61 | JS/Go/Python | 20% | 40% | Small utilities (file finder, log parser) |
| gemini-2.5-pro | claude | 5/5 | 64 | Python | 20% | 20% | Simple scripts (hello world, chatbot) |
| gemini-2.0-flash | claude | 3/5 | 89 | Python | 0% | 0% | Minimal scripts |

## Backend Comparison

| Backend | Total | OK | Partial | Err | Avg LOC (OK runs) | Test Rate |
|---------|-------|----|---------|-----|-------------------|-----------|
| claude | 70 | 41 | 0 | 29 | ~328 | 23% |
| codex | 70 | 0 | 12 | 58 | ~0 | 0% |

### Failure Breakdown

| Failure Type | Count | Affected |
|-------------|-------|----------|
| GPT via claude backend (API param incompatibility) | 30 | All 6 GPT models |
| Claude via codex (gateway tool_use translation) | 25 | All 5 Claude models |
| Codex rate limit (429) | 23 | GPT + Gemini via codex |
| Gemini via codex (service unavailable) | 15 | All 3 Gemini models |
| Azure model unsupported | 5 | gpt-5-nano via codex |
| Intermittent errors | 2 | sonnet-4.6, gemini-2.0-flash |
