# Experiment 3 Results

**Prompt:** "Look at this project and propose exactly ONE goal to achieve next. Decide on your own what to do. Pick a concrete, interesting idea and implement it. Do NOT ask the user what to build. JUST DO IT."

**Matrix:** 14 models × 2 backends (claude + codex) × 5 runs = 140 total jobs

**RTK disabled** — no environment bias from RTK hooks or instructions.

**Key change from Experiment 2:** Prompt adds "JUST DO IT" — explicit implementation demand to address models that proposed without implementing.

---

## Backend Viability

| Backend | Models routed | Outcome |
|---------|--------------|---------|
| **claude** (Claude Code sandbox) | All 14 | Anthropic models: functional. Gemini/GPT: 0 output (Claude Code can't operate with non-Anthropic models via litellm) |
| **codex** (Codex CLI sandbox) | All 14 | All 70 runs produced 0 files. Anthropic models hit tool_use/tool_result mismatch (litellm bug). Gemini hit rate limits. GPT ran 1 command then failed. |

**Effective data:** Claude backend × Anthropic models only (5 models × 5 runs = 25 runs).

Non-Anthropic models on claude backend (run-01 only): Gemini — exit 0, 0 files, 0 output. GPT — exit 0, 0 files except gpt-4.1-mini (Hello World, 8 LOC) and gpt-5-mini (projman CLI skeleton, 175 LOC).

---

## Claude Backend Results

### claude-opus-4-6 — 3/5 implemented, 2 failed

| Run | Topic | Stack | Maturity | Complexity | Duration |
|-----|-------|-------|----------|------------|----------|
| 01 | Conway's Game of Life with patterns | Python 3, curses | tests:no, readme:no, config:no | 1 file, ~356 LOC, ~2 funcs | 1322s |
| 02 | *(failed — exit 1, no files)* | — | — | — | 321s |
| 03 | *(failed — exit 1, no files)* | — | — | — | 265s |
| 04 | Conway's Game of Life with presets | Python 3, curses | tests:no, readme:no, config:no | 1 file, ~288 LOC, ~2 funcs | 682s |
| 05 | Conway's Game of Life | Python 3, curses | tests:no, readme:no, config:no | 1 file, ~226 LOC, ~7 funcs | 79s |

**Pattern:** Still fixated on Game of Life — chose it in all 3 successful runs (consistent with Exp2). Single-file Python, avg ~290 LOC. No maturity features. High failure rate (2/5). Extremely variable duration (79s–1322s).

### claude-opus-4-5 — 3/5 implemented, 2 failed

| Run | Topic | Stack | Maturity | Complexity | Duration |
|-----|-------|-------|----------|------------|----------|
| 01 | Terminal habit tracker | Python 3 | tests:no, readme:no, config:no | 1 file, ~277 LOC, ~14 funcs | 243s |
| 02 | *(failed — exit 1, no files)* | — | — | — | 374s |
| 03 | Snip — CLI code snippet manager | Python 3, JSON | tests:no, readme:yes, config:yes | 6 files, ~651 LOC, ~25 funcs | 1089s |
| 04 | *(failed — exit 1, no files)* | — | — | — | 258s |
| 05 | Pomodoro timer CLI | Python 3 | tests:no, readme:yes, config:no | 2 files, ~474 LOC, ~15 funcs | 130s |

**Pattern:** Improved from Exp2 (2/5 → 3/5 implementation rate). More diverse topics than Exp2. The "JUST DO IT" demand may have helped. Avg ~467 LOC when implemented. Run 03 (snippet manager) was the most ambitious output in the entire experiment.

### claude-sonnet-4-6 — 5/5 implemented

| Run | Topic | Stack | Maturity | Complexity | Duration |
|-----|-------|-------|----------|------------|----------|
| 01 | commitcraft — git commit message generator using Claude | Python 3, Anthropic SDK, subprocess | tests:no, readme:no, config:no | 1 file, ~239 LOC, ~6 funcs | 718s |
| 02 | Live ASCII art clock | Python 3, curses | tests:no, readme:no, config:no | 1 file, ~197 LOC, ~4 funcs | 583s |
| 03 | Terminal maze generator & solver (DFS + A*) | Python 3, curses | tests:no, readme:no, config:no | 1 file, ~371 LOC, ~5 funcs | 569s |
| 04 | AI Debate Arena — two Claude debaters + judge | Python 3, Anthropic SDK | tests:no, readme:no, config:no | 2 files, ~295 LOC, ~9 funcs | 3502s |
| 05 | ASCII Pomodoro timer with session tracking | Python 3, curses, JSON | tests:no, readme:no, config:no | 1 file, ~432 LOC, ~18 funcs | 88s |

**Pattern:** Most diverse output of any model — every run is a different project. Always Python, always single-file. 100% implementation rate (same as Exp2). Avg ~307 LOC. Two runs use the Claude API creatively (commitcraft, debate arena). No maturity features.

### claude-sonnet-4-5 — 4/5 implemented, 1 failed

| Run | Topic | Stack | Maturity | Complexity | Duration |
|-----|-------|-------|----------|------------|----------|
| 01 | Pomodoro timer | Python 3, threading | tests:no, readme:yes, config:no | 2 files, ~362 LOC, ~2 funcs | 261s |
| 02 | *(failed — exit 1, no files)* | — | — | — | 247s |
| 03 | Pomodoro task manager with demo | Python 3, curses | tests:no, readme:yes, config:yes | 6 files, ~462 LOC, ~4 funcs | 739s |
| 04 | Pomodoro timer CLI | Python 3 | tests:no, readme:yes, config:no | 2 files, ~359 LOC, ~2 funcs | 383s |
| 05 | Terminal Snake game with high scores | Python 3, curses | tests:no, readme:no, config:no | 4 files, ~338 LOC, ~7 funcs | 99s |

**Pattern:** Strong Pomodoro fixation (3/4 successful runs). Dropped from 5/5 to 4/5 vs Exp2. Always includes README (except run-05). Always Python. Avg ~380 LOC when implemented.

### claude-haiku-4-5 — 5/5 implemented (dramatically improved)

| Run | Topic | Stack | Maturity | Complexity | Duration |
|-----|-------|-------|----------|------------|----------|
| 01 | Claude Code Reviewer — diff analysis tool | Node.js | tests:no, readme:yes, config:yes | 10 files, ~574 LOC, ~18 funcs | 694s |
| 02 | Noter — CLI note manager with SQLite | Node.js, better-sqlite3 | tests:yes, readme:yes, config:yes | 7 files, ~440 LOC, ~31 funcs | 703s |
| 03 | TASQ — task manager CLI | Python 3 | tests:no, readme:yes, config:no | 4 files, ~481 LOC, ~8 funcs | 482s |
| 04 | Taskly — lightweight task manager | Node.js | tests:yes, readme:yes, config:yes | 6 files, ~458 LOC, ~9 funcs | 952s |
| 05 | Task Manager CLI | Python 3, click, tabulate | tests:no, readme:yes, config:yes | 5 files, ~383 LOC, ~11 funcs | 61s |

**Pattern:** Massive improvement from Exp2 (1/5 → 5/5). The "JUST DO IT" demand was exactly what haiku needed. Highest maturity of any model — README in all 5, tests in 2/5, config in 4/5. Multi-file projects (avg 6.4 files). Polyglot (Node.js and Python). Avg ~467 LOC.

---

## Non-Anthropic Models (claude backend, run-01 only)

All Gemini and most GPT models produced empty workspaces when run through the Claude Code sandbox. Claude Code cannot meaningfully operate with non-Anthropic models via litellm — it exits cleanly (code 0) but generates no files or output.

| Model | Exit | Duration | Files | LOC | Notes |
|-------|------|----------|-------|-----|-------|
| gemini-3-pro-preview | 0 | 308s | 0 | 0 | No output |
| gemini-3-flash-preview | 0 | — | 0 | 0 | No output |
| gemini-2.5-pro | 0 | 221s | 0 | 0 | No output |
| gemini-2.0-flash | 1 | 7s | 0 | 0 | Failed immediately |
| openai/gpt-5.4 | 0 | 10s | 0 | 0 | No output |
| openai/gpt-5.1 | 0 | 26s | 0 | 0 | No output |
| openai/gpt-5-mini | 0 | 391s | 9 | 175 | projman CLI skeleton with tests + CI |
| openai/gpt-4.1 | 0 | 13s | 0 | 0 | No output |
| openai/gpt-4.1-mini | 0 | 19s | 2 | 8 | Hello World |

**Notable:** gpt-5-mini was the only non-Anthropic model to produce a real project (175 LOC with tests, pyproject.toml, and GitHub Actions CI). gpt-4.1-mini produced a trivial Hello World.

---

## Codex Backend — 0/70 produced files

All 70 codex runs exited 0 but produced empty workspaces. Failure modes by model family:

| Model Family | Error |
|-------------|-------|
| Anthropic (25 runs) | litellm `tool_use`/`tool_result` mismatch — API translation bug between OpenAI Responses API and Anthropic Messages API |
| Gemini (20 runs) | "high demand" rate limit after initial command execution |
| OpenAI (25 runs) | Explored workspace but failed on second API call |

The codex backend is not viable for this experiment configuration.

---

## Summary by Model (claude backend, successful runs only)

| Model | OK/Total | Avg LOC | Avg Files | Primary Lang | Test Rate | README Rate | Typical Project |
|-------|----------|---------|-----------|-------------|-----------|-------------|-----------------|
| claude-sonnet-4-6 | 5/5 | 307 | 1.2 | Python | 0% | 0% | Diverse creative tools (maze, debate arena, clock) |
| claude-haiku-4-5 | 5/5 | 467 | 6.4 | JS/Python | 40% | 100% | Task managers and dev tools |
| claude-opus-4-5 | 3/5 | 467 | 3.0 | Python | 0% | 67% | Personal productivity tools |
| claude-sonnet-4-5 | 4/5 | 380 | 3.5 | Python | 0% | 75% | Pomodoro timers |
| claude-opus-4-6 | 3/5 | 290 | 1.0 | Python | 0% | 0% | Conway's Game of Life (every time) |

## Comparison with Experiment 2

| Model | Exp2 OK | Exp3 OK | Exp2 LOC | Exp3 LOC | Key Difference |
|-------|---------|---------|----------|----------|----------------|
| claude-sonnet-4-6 | 5/5 | 5/5 | 204 | 307 | +50% LOC, more creative/diverse topics |
| claude-haiku-4-5 | 1/5 | **5/5** | 160 | 467 | **Biggest improvement.** "JUST DO IT" unlocked implementation |
| claude-opus-4-5 | 2/5 | 3/5 | 291 | 467 | Slightly improved reliability, larger projects |
| claude-sonnet-4-5 | 5/5 | 4/5 | 234 | 380 | Slight regression in reliability, but bigger projects |
| claude-opus-4-6 | 4/5 | 3/5 | 408 | 290 | Still fixated on Game of Life, lower reliability |

## Key Observations

- **"JUST DO IT" fixed haiku:** Exp2's biggest problem was haiku proposing without implementing (1/5). The explicit implementation demand in prompt3 brought it to 5/5 — and it produced the highest-maturity output (READMEs, tests, multi-file projects).
- **opus-4-6 remains fixated on Game of Life** — chose it in all 3 successful runs, consistent with Exp2 (5/5 Game of Life). The "JUST DO IT" prompt didn't break this fixation.
- **sonnet-4-6 is the most creative** — 5 completely different projects across 5 runs, including two that use the Claude API (commit message generator, AI debate arena). Most diverse of any model across all experiments.
- **sonnet-4-5 developed a Pomodoro fixation** — 3/4 successful runs built Pomodoro timers (in Exp2 it was 1/5 Pomodoro).
- **Non-Anthropic models don't work through Claude Code sandbox** — the sandbox is tightly coupled to the Anthropic API. Gemini/GPT models via litellm exit cleanly but produce nothing.
- **Codex backend is broken for all models** — litellm translation bugs, rate limits, and API incompatibilities make it non-viable for this gateway configuration.
- **Average LOC increased across the board** — the stronger implementation demand ("JUST DO IT") produced larger projects than Exp2's "propose ONE goal" framing.
