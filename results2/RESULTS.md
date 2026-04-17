# Experiment 2 Results

**Prompt:** "Look at this project and propose exactly ONE goal to achieve next. If the project is empty or has no code yet, decide on your own what to build. Pick a concrete, interesting idea and implement it as your goal. Do NOT ask the user what to build."

**Matrix:** 13 models × claude backend × 5 runs = 65 total jobs (max 2 concurrent)

**Note on models:** This experiment tested gpt-4o (later replaced by gpt-5.4 in Exp3) and did not include gemini-3-pro-preview. gpt-5-nano was also tested but was non-functional and is excluded from all counts below.

**RTK disabled** — no environment bias from RTK hooks or instructions.

**Note on N:** N = runs without technical errors (exit ≠ 0). Avg LOC computed over these runs only. Runs with exit errors may still contain partial output revealing topic choice — included in fixation/topic analysis but excluded from complexity metrics.

---

## Claude Backend Results

### claude-opus-4.6 — N = 4

| Run | Topic | Stack | Maturity | Complexity |
|-----|-------|-------|----------|------------|
| 01 | Interactive terminal Conway's Game of Life | Python 3, curses | — | *(proposed only, no files)* |
| 02 | Conway's Game of Life with pattern browser | Python 3, curses | tests:no, readme:no, config:no | 1 file, ~558 LOC, ~22 funcs |
| 03 | Conway's Game of Life with toroidal grid | Python 3, curses, argparse | tests:no, readme:no, config:no | 1 file, ~433 LOC, ~14 funcs |
| 04 | Conway's Game of Life with Unicode rendering | Python 3, termios, tty | tests:no, readme:no, config:no | 1 file, ~324 LOC, ~16 funcs |
| 05 | Conway's Game of Life with mouse draw mode | Python 3, curses | tests:no, readme:no, config:no | 1 file, ~317 LOC, ~6 funcs |

**Pattern:** Extremely consistent — chose Game of Life every time. Single-file Python, avg ~408 LOC. No maturity features.

### claude-opus-4.5 — N = 2

| Run | Topic | Stack | Maturity | Complexity |
|-----|-------|-------|----------|------------|
| 01 | Terminal-based real-time system monitor | Python, rich | — | *(proposed only)* |
| 02 | Terminal habit tracker with streaks | Python, argparse, JSON | tests:no, readme:no, config:no | 1 file, ~246 LOC, ~12 funcs |
| 03 | CLI note-taking tool with full-text search | Python | — | *(proposed only)* |
| 04 | Terminal habit tracker with calendar heatmap | Python | — | *(proposed only)* |
| 05 | Terminal habit tracker with SQLite | Python, SQLite, argparse | tests:no, readme:no, config:no | 1 file, ~336 LOC, ~10 funcs |

**Pattern:** Favors habit trackers and personal tools. Always Python. avg ~291 LOC when implemented.

### claude-sonnet-4.6 — N = 5

| Run | Topic | Stack | Maturity | Complexity |
|-----|-------|-------|----------|------------|
| 01 | Interactive terminal Mandelbrot set explorer | Python 3, curses, math | tests:no, readme:no, config:no | 1 file, ~170 LOC, ~5 funcs |
| 02 | Live system monitor (CPU, memory, disk, network) | Python 3, psutil | tests:no, readme:no, config:no | 1 file, ~270 LOC, ~8 funcs |
| 03 | Terminal trivia quiz powered by Claude API | Python 3, anthropic SDK | tests:no, readme:no, config:no | 1 file, ~166 LOC, ~5 funcs |
| 04 | Conway's Game of Life with preset patterns | Python 3, curses | tests:no, readme:no, config:no | 1 file, ~168 LOC, ~7 funcs |
| 05 | Pomodoro timer with session tracking and stats | Python 3, argparse, json | tests:no, readme:no, config:no | 1 file, ~247 LOC, ~9 funcs |

**Pattern:** Diverse interactive tools. Always single-file Python. No maturity features. avg ~204 LOC.

### claude-sonnet-4.5 — N = 5

| Run | Topic | Stack | Maturity | Complexity |
|-----|-------|-------|----------|------------|
| 01 | Pomodoro timer with session tracking | Python 3, threading, signal | tests:no, readme:yes, config:no | 1 file, ~240 LOC, ~12 funcs |
| 02 | Terminal Snake game with arrow key controls | Python 3, tty, termios | tests:no, readme:yes, config:no | 1 file, ~192 LOC, ~8 funcs |
| 03 | Terminal Snake game with progressive difficulty | Python 3, curses | tests:no, readme:yes, config:no | 1 file, ~212 LOC, ~10 funcs |
| 04 | Smart CLI task manager with NLP parsing | Python 3, argparse, json, re | tests:no, readme:yes, config:no | 1 file, ~331 LOC, ~12 funcs |
| 05 | Terminal task manager with priorities and tags | Python 3, argparse, json | tests:no, readme:yes, config:no | 1 file, ~197 LOC, ~9 funcs |

**Pattern:** Games and task managers. Always Python + README. avg ~234 LOC.

### claude-haiku-4.5 — N = 1

| Run | Topic | Stack | Maturity | Complexity |
|-----|-------|-------|----------|------------|
| 01 | Local URL shortener service with REST API | Python, FastAPI | — | *(proposed only)* |
| 02 | Daily standup generator from git commits | Node.js, Anthropic SDK | tests:no, readme:yes, config:yes | 4 files, ~160 LOC, ~4 funcs |
| 03 | Personal finance CLI expense tracker | Python | — | *(proposed only)* |
| 04 | CLI note management with search and tags | Python | — | *(proposed only)* |
| 05 | CLI task manager with file persistence | Node.js, TypeScript, Commander.js | — | *(proposed only)* |

**Pattern:** Proposes well but rarely implements. Polyglot proposals (Python, Node.js).

### gemini-3-flash — N = 5

| Run | Topic | Stack | Maturity | Complexity |
|-----|-------|-------|----------|------------|
| 01 | GoTask — CLI task manager | Go | tests:no, readme:no, config:yes | 4 files, ~134 LOC, ~6 funcs |
| 02 | Snake game using curses | Python, curses | tests:no, readme:no, config:no | 1 file, ~75 LOC, ~1 func |
| 03 | Task manager CLI | JavaScript/Node.js, JSON | tests:no, readme:no, config:yes | 3 files, ~93 LOC, ~5 funcs |
| 04 | GoKV — concurrent key-value store | Go, sync/RWMutex | tests:yes, readme:no, config:yes | 4 files, ~75 LOC, ~6 funcs |
| 05 | Task monitor CLI with performance alerting | Go, exec/cmd | tests:no, readme:yes, config:yes | 3 files, ~51 LOC, ~1 func |

**Pattern:** Polyglot (Go, Python, JS). Small projects. avg ~86 LOC.

### gemini-2.5-pro — N = 4

| Run | Topic | Stack | Maturity | Complexity |
|-----|-------|-------|----------|------------|
| 01 | *(error — empty workspace)* | — | — | — |
| 02 | Weather CLI tool with caching | Python, wttr.in API, setuptools | tests:yes, readme:yes, config:yes | 7 files, ~80 LOC, ~2 funcs |
| 03 | Pomodoro timer with sound notifications | Python, beepy | tests:no, readme:yes, config:yes | 3 files, ~36 LOC, ~2 funcs |
| 04 | Command-line todo list app | Python, JSON | tests:no, readme:no, config:no | 1 file, ~68 LOC, ~4 funcs |
| 05 | Shell command explainer using Claude API | Python, Anthropic SDK | tests:no, readme:yes, config:yes | 3 files, ~44 LOC, ~1 func |

**Pattern:** Simple Python tools. Higher maturity than other Gemini models. avg ~57 LOC.

### gemini-2.0-flash — N = 3

| Run | Topic | Stack | Maturity | Complexity |
|-----|-------|-------|----------|------------|
| 01 | *(error — no output)* | — | — | — |
| 02 | "Hello, World!" in Python | Python | tests:no, readme:no, config:no | 1 file, ~1 LOC, 0 funcs |
| 03 | "Hello, World!" in Python | Python | tests:no, readme:no, config:no | 1 file, ~1 LOC, 0 funcs |
| 04 | "Hello, World!" web application | HTML, CSS, JS | tests:no, readme:no, config:no | 3 files, ~45 LOC, ~1 func |
| 05 | *(error — empty workspace)* | — | — | — |

**Pattern:** Extremely minimal. Hello World level output. avg ~16 LOC.

---

## GPT models (claude backend) — N = 0

All 5 GPT models failed identically: Azure API rejects `context_management` parameter sent by claude sandbox. Same as Experiment 1.

---

## Summary by Model (runs without technical errors)

| Model | N | Avg LOC | Primary Lang | Test Rate | README Rate | Typical Project |
|-------|---|---------|-------------|-----------|-------------|-----------------|
| claude-opus-4.6 | 4 | 408 | Python | 0% | 0% | Conway's Game of Life (every time) |
| claude-opus-4.5 | 2 | 291 | Python | 0% | 0% | Habit trackers |
| claude-sonnet-4.6 | 5 | 204 | Python | 0% | 0% | Diverse interactive tools |
| claude-sonnet-4.5 | 5 | 234 | Python | 0% | 100% | Games + task managers |
| claude-haiku-4.5 | 1 | 160 | Node.js | 0% | 100% | Standup generator |
| gemini-3-flash | 5 | 86 | Go/Python/JS | 20% | 20% | Small CLI tools |
| gemini-2.5-pro | 4 | 57 | Python | 25% | 75% | Simple Python utilities |
| gemini-2.0-flash | 3 | 16 | Python | 0% | 0% | Hello World |

## Comparison with Experiment 1

| Model | Exp1 Avg LOC | Exp2 Avg LOC | Exp1 Lang | Exp2 Lang | Key Difference |
|-------|-------------|-------------|-----------|-----------|----------------|
| claude-opus-4.6 | 607 | 408 | Go/Rust | Python | Shifted from compiled to Python; fixated on Game of Life |
| claude-opus-4.5 | 221 | 291 | Go/JS/Python | Python | Less polyglot; N dropped from 5 to 2 |
| claude-sonnet-4.6 | 506 | 204 | Python | Python | Simpler projects; N rose from 3 to 5 |
| claude-sonnet-4.5 | 776 | 234 | Python | Python | Much simpler; still always has README |
| claude-haiku-4.5 | 233 | 160 | Python/Go/TS | Node.js | N dropped from 5 to 1 |
| gemini-3-flash | 61 | 86 | JS/Go/Python | Go/Python/JS | Slightly larger; still polyglot |
| gemini-2.5-pro | 64 | 57 | Python | Python | Similar; higher maturity in Exp2 |
| gemini-2.0-flash | 89 | 16 | Python | Python | Much simpler output |

**Key observations:**
- Without RTK bias, Claude models shifted to pure Python (no Go/Rust)
- opus-4.6 fixated on Game of Life — chose it in all 5 runs
- N dropped for opus-4.5 (5 -> 2) and haiku-4.5 (5 -> 1)
- sonnet-4.6 N rose from 3 to 5
- Overall complexity decreased — the "propose ONE goal" framing led to smaller, more focused projects
- Gemini models remained consistent between experiments
