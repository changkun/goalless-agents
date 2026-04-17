# Experiment 3 Results

**Prompt:** "Look at this project and propose exactly ONE goal to achieve next. Decide on your own what to do. Pick a concrete, interesting idea and implement it. Do NOT ask the user what to build. JUST DO IT."

**Matrix:** 14 models × 2 backends (claude + codex) × 5 runs = 140 total jobs

**RTK disabled** — no environment bias from RTK hooks or instructions.

**Key change from Experiment 2:** Prompt adds "JUST DO IT" — explicit implementation demand to address models that proposed without implementing.

**N** = runs without technical errors (exit ≠ 0). Avg LOC computed over these runs only. Runs with exit errors may still contain partial output revealing topic choice — included in fixation/topic analysis but excluded from complexity metrics.

---

## Backend Viability

| Backend | Models routed | Outcome |
|---------|--------------|---------|
| **claude** (Claude Code sandbox) | All 14 | Anthropic models: functional. Gemini/GPT: mostly empty (Claude Code can't operate with non-Anthropic models via litellm; exceptions: gpt-5-mini, gpt-4.1-mini) |
| **codex** (Codex CLI sandbox) | All 14 | GPT models produced files inside bwrap sandbox (not persisted to host). Anthropic models hit litellm tool_use/tool_result bug. Gemini hit rate limits. |

---

## Claude Backend — Anthropic Models

### claude-opus-4-6 — N=4

| Run | Topic | Stack | Maturity | Complexity | Duration |
|-----|-------|-------|----------|------------|----------|
| 01 | Conway's Game of Life with patterns | Python 3, curses | tests:no, readme:no, config:no | 1 file, ~356 LOC, ~2 funcs | 1322s |
| 02 | Conway's Game of Life | Python 3, curses | tests:no, readme:no, config:no | 1 file, ~269 LOC | 86s |
| 03 | Conway's Game of Life | Python 3, curses | tests:no, readme:no, config:no | 1 file, ~337 LOC | 132s |
| 04 | Conway's Game of Life with presets | Python 3, curses | tests:no, readme:no, config:no | 1 file, ~324 LOC | 112s |
| 05 | *(technical error — exit 1, 3s; partial Game of Life file left)* | Python 3 | — | 1 file, ~226 LOC | 3s |

**Pattern:** Completely fixated on Game of Life — chose it in all 5 runs including the error run (consistent with Exp2). Single-file Python, avg ~322 LOC (completed runs). No maturity features.

### claude-opus-4-5 — N=3

| Run | Topic | Stack | Maturity | Complexity | Duration |
|-----|-------|-------|----------|------------|----------|
| 01 | Terminal habit tracker | Python 3, argparse, JSON | tests:no, readme:no, config:no | 1 file, ~277 LOC, ~14 funcs | 243s |
| 02 | *(technical error — exit 1, no files)* | — | — | — | 374s |
| 03 | Snip — CLI code snippet manager | Python 3, pygments, pyproject.toml | tests:no, readme:yes, config:yes | 6 files, ~651 LOC, ~25 funcs | 1089s |
| 04 | *(technical error — exit 1, no files)* | — | — | — | 258s |
| 05 | Pomodoro timer CLI | Python 3 | tests:no, readme:yes, config:no | 2 files, ~474 LOC, ~15 funcs | 130s |

**Pattern:** More diverse topics than Exp2. Highest average complexity among completed runs (~467 LOC). Run 03 (snippet manager, 651 LOC with pyproject.toml) was the most ambitious single output.

### claude-sonnet-4-6 — N=5

| Run | Topic | Stack | Maturity | Complexity | Duration |
|-----|-------|-------|----------|------------|----------|
| 01 | commitcraft — git commit message generator using Claude | Python 3, Anthropic SDK, subprocess | tests:no, readme:no, config:no | 1 file, ~239 LOC, ~6 funcs | 718s |
| 02 | Live ASCII art clock | Python 3, curses | tests:no, readme:no, config:no | 1 file, ~197 LOC, ~4 funcs | 583s |
| 03 | Terminal maze generator & solver (DFS + A*) | Python 3, curses | tests:no, readme:no, config:no | 1 file, ~371 LOC, ~5 funcs | 569s |
| 04 | AI Debate Arena — two Claude debaters + judge | Python 3, Anthropic SDK | tests:no, readme:no, config:yes | 2 files, ~295 LOC, ~9 funcs | 3502s |
| 05 | ASCII Pomodoro timer with session tracking | Python 3, curses, JSON | tests:no, readme:no, config:no | 1 file, ~432 LOC, ~18 funcs | 88s |

**Pattern:** Most diverse output of any model — every run is a different project. Consistently produced output across all 3 experiments without technical errors. Two runs use the Claude API creatively (commitcraft, debate arena) — only model to do so. Avg ~307 LOC.

### claude-sonnet-4-5 — N=4

| Run | Topic | Stack | Maturity | Complexity | Duration |
|-----|-------|-------|----------|------------|----------|
| 01 | Pomodoro timer with task list | Python 3, threading | tests:no, readme:yes, config:no | 2 files, ~362 LOC, ~2 funcs | 261s |
| 02 | *(technical error — exit 1, no files)* | — | — | — | 247s |
| 03 | Pomodoro task manager with demo | Python 3, curses | tests:no, readme:yes, config:yes | 6 files, ~462 LOC, ~4 funcs | 739s |
| 04 | Pomodoro timer CLI | Python 3 | tests:no, readme:yes, config:no | 2 files, ~359 LOC, ~2 funcs | 383s |
| 05 | Terminal Snake game with high scores | Python 3, curses | tests:no, readme:no, config:no | 4 files, ~338 LOC, ~7 funcs | 99s |

**Pattern:** Strong Pomodoro fixation (3 of 4 completed runs). README included in 3 of 4 completed runs. Avg ~380 LOC across completed runs.

### claude-haiku-4-5 — N=5

| Run | Topic | Stack | Maturity | Complexity | Duration |
|-----|-------|-------|----------|------------|----------|
| 01 | Claude Code Reviewer — diff analysis tool | Node.js, @anthropic-ai/sdk | tests:no, readme:yes, config:yes | 10 files, ~574 LOC, ~18 funcs | 694s |
| 02 | Noter — CLI note manager with SQLite | Node.js, better-sqlite3 | tests:yes, readme:yes, config:yes | 7 files, ~440 LOC, ~31 funcs | 703s |
| 03 | TASQ — task manager CLI | Python 3, argparse | tests:no, readme:yes, config:no | 4 files, ~481 LOC, ~8 funcs | 482s |
| 04 | Taskly — lightweight task manager | Node.js | tests:yes, readme:yes, config:yes | 6 files, ~458 LOC, ~9 funcs | 952s |
| 05 | Task Manager CLI | Python 3, click, tabulate | tests:no, readme:yes, config:yes | 5 files, ~383 LOC, ~11 funcs | 61s |

**Pattern:** The "JUST DO IT" prompt elicited consistent implementation where Exp2's framing did not. Highest maturity of any model — README in all 5 runs, tests in 2, config in 4. Multi-file projects (avg 6.4 files). Polyglot (Node.js x 3, Python x 2). Avg ~467 LOC.

---

## Claude Backend — GPT Models (5 runs each)

All output.json files were empty (0 bytes) — Claude Code's stdout capture doesn't work with non-Anthropic models. But workspace files reveal what was built.

### gpt-5-mini — N=5

| Run | Topic | Stack | Maturity | Complexity | Duration |
|-----|-------|-------|----------|------------|----------|
| 01 | `projman` — project scaffold CLI | Python 3, argparse, pyproject.toml | tests:yes, readme:yes, config:yes, CI:yes | 5 files, ~158 LOC | 391s |
| 02 | Directory health-check tool | Python 3, stdlib | tests:yes, readme:yes, config:yes | 3 files, ~101 LOC | 1378s |
| 03 | Greeting CLI with flags | Python 3, argparse, pyproject.toml | tests:yes, readme:yes, config:yes, CI:yes | 7 files, ~129 LOC | 341s |
| 04 | Greeting CLI stub | Python 3, argparse | tests:yes, readme:yes, CI:yes | 3 files, ~53 LOC | 193s |
| 05 | `fhash` — file/directory hashing tool | Python 3, hashlib, pyproject.toml | tests:yes, readme:no, config:yes, CI:yes | 5 files, ~165 LOC | 710s |

**Pattern:** The only non-Anthropic model to produce output in every run on claude backend. Every run includes tests. 4 of 5 include pyproject.toml and GitHub Actions CI. Avg ~121 LOC. Much longer runtimes (193-1378s) than other GPT models, indicating actual tool use iteration.

### gpt-5.4 — N=1

| Run | Topic | Stack | Maturity | Complexity | Duration |
|-----|-------|-------|----------|------------|----------|
| 01–04 | *(no output)* | — | — | 0 files | 9–43s |
| 05 | Hello-world CLI stub | Python 3 | readme:yes | 1 file, ~7 LOC | 36s |

### gpt-5.1 — N=0

All 5 runs exited 0 but produced zero files (18–52s each).

### gpt-4.1 — N=2

| Run | Topic | Stack | Maturity | Complexity | Duration |
|-----|-------|-------|----------|------------|----------|
| 02 | Hello-world stub | Python 3 | — | 1 file, ~5 LOC | 14s |
| 03 | JSON-backed todo CLI | Python 3, stdlib | — | 1 file, ~56 LOC | 21s |
| 01, 04, 05 | *(no output)* | — | — | 0 files | 13–55s |

### gpt-4.1-mini — N=4 (stubs)

| Run | Topic | Stack | Maturity | Complexity | Duration |
|-----|-------|-------|----------|------------|----------|
| 01 | Hello World | Python 3 | readme:yes | 1 file, ~5 LOC | 19s |
| 02 | Interactive greeter | Python 3 | — | 1 file, ~11 LOC | 29s |
| 03 | *(README only, no code)* | — | readme:yes | 0 src files | 12s |
| 04 | Hello World | Python 3 | readme:yes | 1 file, ~5 LOC | 54s |
| 05 | Greeting CLI with tests | Python 3, unittest | tests:yes, readme:yes | 2 files, ~21 LOC | 50s |

**Pattern:** Almost exclusively Hello World stubs (avg ~8 LOC).

---

## Claude Backend — Gemini Models (5 runs each)

### gemini-3-pro-preview — N=0

All 5 runs exited 0 but produced zero workspace files (181–1748s). The model reasoned without writing anything.

### gemini-3-flash-preview — N=1

| Run | Topic | Stack | Maturity | Complexity | Duration |
|-----|-------|-------|----------|------------|----------|
| 02 | CLI task tracker | Python 3, stdlib | readme:yes | 2 files, ~81 LOC | 1193s |
| 01, 03–05 | *(failed or no output)* | — | — | 0 files | 240–6084s |

All 5 runs exited 1. Run-01 hung for 6084s (~101 min) before failing.

### gemini-2.5-pro — N=0

Runs 01–02 exited 0; runs 03–05 exited 1. Run-04 left a bare `package.json` stub (11 LOC, no source code). No actual implementation across 5 runs.

### gemini-2.0-flash — N=0 (instant failure)

All 5 runs exited 1 in 4–16s. The model fails immediately at the API routing layer.

---

## Codex Backend — GPT Models (files created in sandbox, not persisted to host)

GPT models were productive on the codex backend — they created files inside the bwrap sandbox, but the isolation layer prevented writes from persisting to the host-mounted workspace volume. All activity is captured in output.json.

### gpt-5.4 — N=5

| Run | Topic | Stack | Maturity | Complexity |
|-----|-------|-------|----------|------------|
| 01 | Directory snapshot CLI (`project_snapshot.py`) | Python 3, stdlib | tests:no, readme:yes, config:no | 2 files, ~80 LOC |
| 02 | "Next Move Lab" — offline goal-scoring web app | HTML/CSS/JS (vanilla) | tests:no, readme:yes, config:no | 4 files, ~300 LOC |
| 03 | Decision Journal — localStorage-backed browser app | HTML/CSS/JS (vanilla) | tests:no, readme:yes, config:no | 4 files, ~550 LOC |
| 04 | Text digest CLI — summarizes text, extracts keywords | Python 3, stdlib | tests:yes, readme:yes, config:no | 3 files, ~120 LOC |
| 05 | ASCII terrain generator CLI | Python 3, stdlib | tests:yes, readme:yes, config:no | 3 files, ~100 LOC |

**Pattern:** Most diverse GPT model — never repeated a topic. Mixed Python CLI and full web apps. Tests in 2 of 5 runs. README in every run. Used native Codex `file_change` API. Avg ~230 LOC.

### gpt-5.1 — N=5

| Run | Topic | Stack | Maturity | Complexity |
|-----|-------|-------|----------|------------|
| 01 | `miniwc` — wc-like CLI with src/ layout | Python 3, pyproject.toml | tests:yes, readme:yes, config:yes | 7 files, ~150 LOC |
| 02 | Pomodoro focus timer CLI | Python 3, pyproject.toml | tests:no, readme:yes, config:yes | 3 files, ~80 LOC |
| 03 | `commitlint-lite` — Conventional Commits linter | Python 3, pyproject.toml | tests:no, readme:yes, config:yes | 5 files, ~100 LOC |
| 04 | `tasklog` — timestamped task logging CLI | Python 3, stdlib | tests:no, readme:yes, config:no | 2 files, ~80 LOC |
| 05 | Markdown index generator → styled HTML | Python 3, pytest | tests:yes, readme:no, config:yes | 3 files, ~80 LOC |

**Pattern:** Consistent Python CLI tools with proper packaging. pyproject.toml in 3 of 5 runs. README in 4 of 5. Avg ~98 LOC.

### gpt-5-mini — N=4

| Run | Topic | Stack | Maturity | Complexity |
|-----|-------|-------|----------|------------|
| 01 | `proj-info` CLI — path info utility | Python 3, pyproject.toml | tests:yes, readme:yes, config:yes | 6 files, ~60 LOC |
| 02 | `hello` package with greet function *(corrupted by quoting)* | Python 3 | tests:yes, readme:no, config:no | *(partial)* |
| 03 | `hello.py` with greet function + pytest | Python 3, pytest | tests:yes, readme:no, config:yes | 3 files, ~40 LOC |
| 04 | `sayhello` CLI with flags | Python 3, pyproject.toml | tests:yes, readme:yes, config:yes | 3 files, ~40 LOC |
| 05 | `repo_inspect.py` — directory info tool | Python 3, stdlib | tests:no, readme:yes, config:no | 2 files, ~20 LOC |

**Pattern:** Repeatedly chose greeting/hello utilities (3 of 5 runs). Consistently included tests. Avg ~40 LOC.

### gpt-4.1 — N=5

| Run | Topic | Stack | Maturity | Complexity |
|-----|-------|-------|----------|------------|
| 01 | Todo app CLI (todos.txt storage) | Python 3, stdlib | tests:no, readme:no, config:no | 3 files, ~60 LOC |
| 02 | Todo app CLI (JSON storage) | Python 3, stdlib | tests:no, readme:yes, config:no | 4 files, ~100 LOC |
| 03 | Todo CLI single-file (tasks.txt) | Python 3, stdlib | tests:no, readme:no, config:no | 1 file, ~40 LOC |
| 04 | Python starter scaffold | Python 3, pyproject.toml | tests:yes, readme:yes, config:yes | 5 files, ~50 LOC |
| 05 | Palindrome CLI with unit tests | Python 3, pytest | tests:yes, readme:no, config:yes | 3 files, ~30 LOC |

**Pattern:** Fixated on todo apps (3 of 5 runs). Used bash heredocs for file creation. Avg ~56 LOC.

### gpt-4.1-mini — N=4

| Run | Topic | Stack | Maturity | Complexity |
|-----|-------|-------|----------|------------|
| 01 | Hello World scaffold | Python 3 | tests:no, readme:yes, config:no | 3 files, ~5 LOC |
| 02 | Hello World scaffold | Python 3 | tests:no, readme:yes, config:no | 2 files, ~2 LOC |
| 03 | *(proposed only — asked user what to build, violating prompt)* | — | — | — |
| 04 | Simple greeter CLI with unit tests | Python 3, unittest | tests:yes, readme:no, config:no | 3 files, ~30 LOC |
| 05 | Hello World scaffold | Python 3, unittest | tests:yes, readme:yes, config:no | 3 files, ~5 LOC |

**Pattern:** Almost exclusively Hello World (3 of 5 runs). Run-03 violated the prompt by asking user for direction. Avg ~8 LOC.

---

## Codex Backend — Anthropic Models (all 25 failed)

All 25 runs crashed after exactly 1 command due to the litellm `tool_use`/`tool_result` translation bug. The Codex CLI sends OpenAI Responses API format; litellm translates to Anthropic Messages API but fails to pair tool blocks correctly.

| Model | Commands before crash | Error at msg index | Notable |
|-------|----------------------|-------------------|---------|
| claude-sonnet-4-6 | 1 (`find + cat README`) | messages.1 | — |
| claude-sonnet-4-5 | 1 (`find + grep`) | messages.1 | Varied file filters |
| claude-opus-4-6 | 1 (`find`) | messages.1 | Leading `\n\n` in agent text |
| claude-opus-4-5 | 1 (`find + ls + cat`) | messages.3 | Emitted todo list before crash (Game of Life, maze, Pomodoro) |
| claude-haiku-4-5 | 1 (`find`) | messages.1 | Simpler commands than others |

**opus-4-5** was the only model to survive an extra step — it emitted a `todo_list` item after the shell command, pushing the conversation to messages.3 before triggering the bug. The todo list goals reveal what it would have built: Game of Life (run 01), CLI maze (run 02), terminal game engine (run 03), productivity tool (run 04), Pomodoro timer (run 05).

---

## Codex Backend — Gemini Models (all 20 failed)

All 20 runs failed after 0–1 commands. Initial WebSocket connection to `wss://llm.changkun.de/v1/responses` returned 403 on 4 retry attempts, then a second failure mode killed the turn.

| Model | Commands/run | Secondary error |
|-------|-------------|----------------|
| gemini-3-pro-preview | 1 (`ls -la`) | "high demand" rate limit |
| gemini-3-flash-preview | 1 (`ls -R`) | "high demand" rate limit |
| gemini-2.5-pro | 1 (`ls -l` or `ls -F`) | "high demand" rate limit |
| gemini-2.0-flash | 0 | "stream disconnected before completion" |

gemini-2.0-flash never executed a single command. The other Gemini models each ran one `ls` variant before being rate-limited.

---

## Summary — All Backends

### Claude Backend — Anthropic Models

| Model | N | Avg LOC | Avg Files | Primary Lang | Test Rate | README Rate | Typical Project |
|-------|---|---------|-----------|-------------|-----------|-------------|-----------------|
| claude-sonnet-4-6 | 5 | 307 | 1.2 | Python | 0% | 0% | Diverse creative tools (maze, debate arena, clock) |
| claude-haiku-4-5 | 5 | 467 | 6.4 | JS/Python | 40% | 100% | Task managers and dev tools |
| claude-opus-4-5 | 3 | 467 | 3.0 | Python | 0% | 67% | Personal productivity tools |
| claude-sonnet-4-5 | 4 | 380 | 3.5 | Python | 0% | 75% | Pomodoro timers |
| claude-opus-4-6 | 4 | 322 | 1.0 | Python | 0% | 0% | Conway's Game of Life (every time) |

### Claude Backend — GPT Models

| Model | N | Avg LOC | Primary Stack | Test Rate | README Rate | Typical Project |
|-------|---|---------|--------------|-----------|-------------|-----------------|
| gpt-5-mini | 5 | ~121 | Python | 100% | 80% | CLI tools with tests + CI |
| gpt-4.1-mini | 4 | ~8 | Python | 20% | 60% | Hello World stubs |
| gpt-4.1 | 2 | ~31 | Python | 0% | 0% | Todo CLI (best single run) |
| gpt-5.4 | 1 | ~7 | Python | 0% | 100% | Stub only |
| gpt-5.1 | 0 | — | — | — | — | No output |

### Claude Backend — Gemini Models

| Model | N | Avg LOC | Notes |
|-------|---|---------|-------|
| gemini-3-flash-preview | 1 | ~81 | One task tracker; rest had errors |
| gemini-3-pro-preview | 0 | — | Exits 0 but produces nothing |
| gemini-2.5-pro | 0 | — | One bare package.json stub |
| gemini-2.0-flash | 0 | — | Instant failure every run |

### Codex Backend — GPT Models (files in sandbox only, not persisted)

| Model | N | Avg LOC | Primary Stack | Test Rate | README Rate | Typical Project |
|-------|---|---------|--------------|-----------|-------------|-----------------|
| gpt-5.4 | 5 | ~230 | Python / HTML+JS | 40% | 100% | Diverse — web apps, CLI tools |
| gpt-5.1 | 5 | ~98 | Python | 40% | 80% | CLI utilities with packaging |
| gpt-4.1 | 5 | ~56 | Python | 40% | 40% | Todo list apps (3 of 5 runs) |
| gpt-5-mini | 4 | ~40 | Python | 60% | 40% | Greeting/hello utilities |
| gpt-4.1-mini | 4 | ~8 | Python | 40% | 60% | Hello World |

## Comparison with Experiment 2

| Model | Exp2 N | Exp3 N | Exp2 LOC | Exp3 LOC | Key Behavioral Difference |
|-------|--------|--------|----------|----------|--------------------------|
| claude-sonnet-4-6 | 5 | 5 | 204 | 307 | +50% LOC, more creative/diverse topics |
| claude-haiku-4-5 | 1 | **5** | 160 | 467 | **"JUST DO IT" prompt elicited implementation** — Exp2 produced proposals only |
| claude-opus-4-5 | 2 | 3 | 291 | 467 | Larger projects when completed, more diverse topics |
| claude-sonnet-4-5 | 5 | 4 | 234 | 380 | Developed Pomodoro fixation (3 of 4 completed runs), but bigger projects |
| claude-opus-4-6 | 4 | 4 | 408 | 322 | Still fixated on Game of Life; partial output in error run confirms topic choice |

## Key Observations

- **"JUST DO IT" changed haiku's behavior:** In Exp2, haiku proposed without implementing. The explicit demand elicited implementation in every Exp3 run — and it produced the highest-maturity output (READMEs, tests, multi-file projects).
- **opus-4-6 remains fixated on Game of Life** — chose it in all completed runs, and the error run's partial output also targeted Game of Life (consistent with Exp2, where all runs chose this topic).
- **sonnet-4-6 is the most creative** — 5 completely different projects across 5 runs, including two that use the Claude API (commit message generator, AI debate arena). Most diverse of any model across all experiments.
- **sonnet-4-5 developed a Pomodoro fixation** — 3 of 4 completed runs built Pomodoro timers (Exp2 showed this topic in only 1 run).
- **GPT models: backend determines everything.** On codex (native backend), gpt-5.4 was most productive (~230 LOC, diverse). On claude backend, gpt-5-mini was the only GPT model that reliably produced code (avg 121 LOC with tests+CI). gpt-5.4 and gpt-5.1 produced almost nothing on claude backend despite being the strongest on codex.
- **gpt-5-mini is paradoxically the best GPT model on claude backend** — outperformed all larger GPT models. Longer runtimes (193-1378s vs 9-55s) suggest it's the only one actually executing multiple tool calls through Claude Code.
- **Gemini models are nearly non-functional on claude backend** — gemini-3-pro-preview exits cleanly in all runs but produces zero files. Only gemini-3-flash-preview managed one 81-LOC project across 20 total Gemini runs on claude backend.
- **Codex backend is broken for Anthropic and Gemini models** — litellm translation bugs and rate limits respectively. Files created by GPT models don't persist due to bwrap isolation.
- **File creation method matters on codex** — gpt-5.4 and gpt-5.1 used native Codex `file_change` API (reliable). gpt-4.1 and gpt-4.1-mini used bash heredocs (caused quoting/corruption issues).
- **Average LOC increased across the board** — the stronger implementation demand produced larger projects than Exp2's "propose ONE goal" framing.
- **Model capability gradient differs by backend:**
  - Codex: gpt-5.4 (~230 LOC) >> gpt-5.1 (~98) >> gpt-4.1 (~56) >> gpt-5-mini (~40) >> gpt-4.1-mini (~8)
  - Claude: gpt-5-mini (~121 LOC) >> gpt-4.1 (~31) >> gpt-4.1-mini (~8) >> gpt-5.4 (~7) >> gpt-5.1 (0)
