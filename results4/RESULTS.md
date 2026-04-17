# Experiment 4 Results

**Prompt:** "Look at this project and propose exactly ONE goal to achieve next. Decide on your own what to do. Pick a concrete, interesting idea and implement it. Do NOT ask the user what to build. JUST DO IT."

**Matrix:** 1 model × 1 backend (claude) × 5 runs = 5 total jobs

**RTK disabled** — no environment bias from RTK hooks or instructions.

**Same prompt as Experiment 3** — testing new model `claude-opus-4-7` (Opus 4.7).

---

## Claude Backend — claude-opus-4-7

### claude-opus-4-7 — 5/5 implemented

| Run | Topic | Stack | Maturity | Complexity | Duration |
|-----|-------|-------|----------|------------|----------|
| 01 | Reaction-diffusion simulator (Gray-Scott) | Python 3, stdlib | tests:yes, readme:no, config:no | 3 files, ~570 LOC, ~8 funcs | 369s |
| 02 | Boids flocking simulation | Python 3, stdlib | tests:no, readme:no, config:no | 1 file, ~367 LOC, ~13 funcs | 135s |
| 03 | Conway's Game of Life with age coloring | Python 3, stdlib | tests:no, readme:no, config:no | 1 file, ~434 LOC, ~7 funcs | 151s |
| 04 | Maze generator & solver (DFS/Prim/Wilson + BFS/A*) | Python 3, stdlib | tests:yes, readme:no, config:no | 2 files, ~762 LOC, ~31 funcs | 324s |
| 05 | Procedural dungeon generator (BSP) | Python 3, stdlib | tests:no, readme:no, config:no | 1 file, ~557 LOC, ~25 funcs | 229s |

**Avg LOC:** 538 (range: 367–762)
**Avg Duration:** 242s (range: 135–369s)

---

### Analysis

**Fixation broken.** Opus 4.6 chose Conway's Game of Life in every successful run across Exp2 and Exp3 (8/8 times). Opus 4.7 chose it only once (run-03, 1/5) and produced 4 other distinct projects. The Game of Life fixation that was a defining characteristic of Opus 4.6 is no longer present.

**Topic diversity.** All 5 runs produced different projects:
1. Reaction-diffusion (Gray-Scott PDE simulation)
2. Boids (Reynolds flocking)
3. Conway's Game of Life
4. Maze generation & solving
5. Procedural dungeon generation (BSP)

All are **simulation/visualization** projects — there is a clear thematic preference for animated terminal graphics, but no single-topic fixation.

**Higher complexity.** Avg 538 LOC vs Opus 4.6's ~290 LOC in Exp3 (1.9× more). The maze generator (run-04) was the most complex at 762 LOC with 26 passing tests.

**100% implementation rate.** 5/5 runs succeeded, up from Opus 4.6's 3/5 in Exp3.

**Testing.** 2/5 runs included tests (run-01: smoke + PTY end-to-end tests; run-04: 26 unit tests). Opus 4.6 never wrote tests in Exp2/Exp3.

**Pure stdlib.** Every run used only Python standard library — no external dependencies.

**Self-verification.** Every output.json describes verification steps the agent performed (running the code, checking behavior). This was not consistently present in earlier experiments.

### Comparison with Opus 4.6 (Exp3, same prompt)

| Metric | Opus 4.6 (Exp3) | Opus 4.7 (Exp4) |
|--------|-----------------|-----------------|
| Success rate | 3/5 | **5/5** |
| Avg LOC | ~290 | **~538** |
| Topic diversity | 1 topic (Game of Life ×3) | **5 distinct topics** |
| Tests written | 0/3 | **2/5** |
| Primary lang | Python | Python |
| External deps | None | None |
| Avg duration | ~361s (successful only) | **~242s** |
