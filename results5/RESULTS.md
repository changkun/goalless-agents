# Experiment 5 Results

**Prompt:** "Look at this project and propose exactly ONE goal to achieve next. Decide on your own what to do. Pick a concrete, interesting idea and implement it. Do NOT ask the user what to build. JUST DO IT."

**Matrix:** 2 models × 1 backend (claude) × 5 runs = 10 total jobs

**RTK disabled** — no environment bias from RTK hooks or instructions.

> **N** = runs without technical errors (exit ≠ 0). Avg LOC computed over these runs only. Runs with exit errors may still contain partial output revealing topic choice — included in fixation/topic analysis but excluded from complexity metrics.

**Same prompt as Experiments 3 and 4.** The variable under test is the **harness version**: Claude Code 2.1.112 (this experiment) vs 2.1.109 (Exp3/Exp4).

### Harness changelog (2.1.109 → 2.1.112)

Key changes between the two versions:

- **2.1.112:** Fixed "claude-opus-4-7 is temporarily unavailable" for auto mode
- **2.1.111:** Claude Opus 4.7 xhigh effort level, auto mode available for Max subscribers with Opus 4.7, `/effort` interactive slider, `/ultrareview` for parallel multi-agent code review, `/less-permission-prompts` skill, plan files named after prompt, various UX improvements
- **2.1.110:** `/tui fullscreen` command, push notification tool, improved plugin handling, `--resume`/`--continue` resurrects scheduled tasks, various fixes for MCP, fullscreen rendering, and session management
- **2.1.109:** Improved extended-thinking indicator with rotating progress hint

---

## claude-opus-4-6 — N = 5

| Run | Topic | Stack | Maturity | Complexity | Duration |
|-----|-------|-------|----------|------------|----------|
| 01 | Conway's Game of Life with patterns | Python 3, curses | tests:no, readme:no, config:no | 1 file, ~277 LOC, ~2 funcs | 150s |
| 02 | Ray tracer with Blinn-Phong shading | Python 3, stdlib | tests:no, readme:no, config:no | 1 file, ~345 LOC, ~13 funcs | 227s |
| 03 | Conway's Game of Life with sparse grid | Python 3, curses | tests:no, readme:no, config:no | 1 file, ~341 LOC, ~3 funcs | 138s |
| 04 | Terminal typing speed test | Python 3, curses | tests:no, readme:no, config:no | 1 file, ~626 LOC, ~15 funcs | 214s |
| 05 | Conway's Game of Life with age coloring | Go, tcell | tests:no, readme:no, config:no | 4 files, ~345 LOC, ~12 funcs | 170s |

**Avg LOC:** 387 (range: 277–626)
**Avg Duration:** 180s (range: 138–227s)

**Pattern:** Game of Life fixation persists (3/5 runs), but 2/5 runs broke free — **ray tracer** (run-02) and **typing speed test** (run-04). In Exp3 on harness 2.1.109, opus-4.6 chose Game of Life in all 3 successful runs (3/3). The harness upgrade may have contributed to slightly more diverse output. Also notably, **run-05 used Go** instead of Python — the only non-Python run across both models.

---

## claude-opus-4-7 — N = 5

| Run | Topic | Stack | Maturity | Complexity | Duration |
|-----|-------|-------|----------|------------|----------|
| 01 | Boids flocking with user-controlled hawk | Python 3, curses | tests:no, readme:no, config:no | 1 file, ~246 LOC | 133s |
| 02 | Procedural dungeon generator (BSP) | Python 3, stdlib | tests:no, readme:no, config:no | 1 file, ~315 LOC | 77s |
| 03 | Maze generator & A* solver | Python 3, stdlib | tests:no, readme:no, config:no | 1 file, ~178 LOC | 50s |
| 04 | Boids flocking simulation | Python 3, curses | tests:no, readme:no, config:no | 1 file, ~264 LOC | 97s |
| 05 | Boids flocking with spatial hash | Python 3, stdlib | tests:no, readme:no, config:no | 1 file, ~309 LOC | 81s |

**Avg LOC:** 262 (range: 178–315)
**Avg Duration:** 88s (range: 50–133s)

**Pattern:** Boids fixation emerged (3/5 runs). In Exp4 (harness 2.1.109), opus-4.7 produced 5 distinct topics with avg 538 LOC. On harness 2.1.112, topics are less diverse and LOC is significantly lower. No tests written (vs 2/5 in Exp4).

---

## Cross-comparison

### Harness impact on claude-opus-4-6

| Metric | Exp3 (harness 2.1.109) | Exp5 (harness 2.1.112) |
|--------|------------------------|------------------------|
| N (error-free runs) | 4 | 5 |
| Avg LOC | ~322 | **~387** |
| Game of Life fixation | 5/5 (100%) | 3/5 (60%) |
| Non-GoL topics | 0 | 2 (ray tracer, typing test) |
| Languages | Python only | Python + Go |
| Tests written | 0 | 0 |
| Avg duration | ~413s | ~180s |

**On harness 2.1.112, opus-4.6 showed more diverse output.** The Game of Life fixation weakened (100% → 60%) but did not disappear. Note: in Exp3, all 5 workspaces contained Game of Life code (including the failed run-05 which left a partial file). Duration differences are confounded by server load variance.

### Harness impact on claude-opus-4-7

| Metric | Exp4 (harness 2.1.109) | Exp5 (harness 2.1.112) |
|--------|------------------------|------------------------|
| N (error-free runs) | 5 | 5 |
| Avg LOC | **~538** | ~262 |
| Topic diversity | **5 distinct topics** | 3 topics (boids ×3) |
| Tests written | **2/5** | 0/5 |
| Avg duration | ~242s | ~88s |

**On harness 2.1.112, opus-4.7 produced simpler output:** half the LOC, no tests, and a new boids fixation (3/5). Duration differences are likely server load variance, not harness-caused. The complexity regression (538 → 262 LOC, tests lost) is the more meaningful signal — the newer harness may be encouraging brevity over depth.

### Model comparison on same harness (2.1.112)

| Metric | opus-4.6 (Exp5) | opus-4.7 (Exp5) |
|--------|-----------------|-----------------|
| N (error-free runs) | 5 | 5 |
| Avg LOC | **387** | 262 |
| Avg duration | 180s | 88s |
| Fixation | GoL (3/5) | Boids (3/5) |
| Non-fixated topics | Ray tracer, typing test | Dungeon gen, maze solver |
| Languages | Python + Go | Python only |

On the same harness, opus-4.6 produces more code but is slower. Both models show fixation behavior (different topics). Opus-4.7 is 2× faster but produces simpler output.

---

## Key Findings

1. **Harness version may influence output diversity.** Opus-4.6's Game of Life fixation weakened from 100% (Exp3) to 60% (Exp5) across harness versions. However, with only 5 runs per condition, this could also be normal variance.

2. **Harness version may influence output complexity.** Opus-4.7 produced ~half the LOC (538 → 262 avg) and no tests on harness 2.1.112 vs 2/5 runs with tests on 2.1.109. The newer harness may be encouraging brevity over depth, though sample size is small.

3. **Fixation is model-specific, not harness-specific.** Opus-4.6 fixates on Game of Life across both harness versions (though less strongly on 2.1.112). Opus-4.7 developed a new boids fixation on 2.1.112 (3/5) that wasn't present on 2.1.109 (0/5).

4. **Both models remain 100% Python-dominant.** Only one run (opus-4.6 run-05) used a different language (Go). All other 9 runs were pure Python stdlib.
