# Goalless Agent Experiment

Automated experiment measuring what AI coding agents actually build when given
open-ended prompts across different models and sandbox backends.

## Setup

**Backends:**
- `claude` — [sandbox-claude](https://ghcr.io/latere-ai/sandbox-claude) (Anthropic API, Claude Code)
- `codex` — [sandbox-codex](https://ghcr.io/latere-ai/sandbox-codex) (OpenAI Responses API, Codex CLI)

**Models** (see `models.txt`): 15 models across Claude, Gemini, and GPT families.

**Matrix:** Each model × each backend × 5 runs per prompt,
all models in a run execute in parallel.

## Results

### Experiment 1 — `prompt1.txt`

> Look at this project and decide on your own what to build, and DO it.
> Do NOT ask the user what to build.

See **[results1/RESULTS.md](results1/RESULTS.md)** for the full per-run breakdown.

### Experiment 2 — `prompt2.txt`

> Look at this project and propose exactly ONE goal to achieve next. If the
> project is empty or has no code yet, decide on your own what to build. Pick
> a concrete, interesting idea and implement it as your goal. Do NOT ask the
> user what to build.

See **[results2/RESULTS.md](results2/RESULTS.md)** for the full per-run breakdown.

### Experiment 3 — `prompt3.txt`

> Look at this project and propose exactly ONE goal to achieve next. Decide
> on your own what to do. Pick a concrete, interesting idea and implement it.
> Do NOT ask the user what to build. JUST DO IT.

See **[results3/RESULTS.md](results3/RESULTS.md)** for the full per-run breakdown.

### Experiment 4 — `prompt3.txt` (new model: claude-opus-4-7)

> Same prompt as Experiment 3. Testing Opus 4.7 against Opus 4.6's Game of Life fixation.
> Harness: Claude Code 2.1.109.

See **[results4/RESULTS.md](results4/RESULTS.md)** for the full per-run breakdown.

### Experiment 5 — `prompt3.txt` (harness version as variable)

> Same prompt as Experiments 3/4. Testing whether harness version (Claude Code
> 2.1.112 vs 2.1.109) affects output. Both opus-4.6 and opus-4.7 run on 2.1.112.

See **[results5/RESULTS.md](results5/RESULTS.md)** for the full per-run breakdown.

Each experiment includes:
- Topic proposed and implementation status
- Tech stack (language, frameworks)
- Engineering maturity (tests, docs, build config, CI)
- Complexity metrics (files, LOC, functions)

### Key Findings

**Experiment 1** (RTK present in sandbox — biased toward dev tooling):

| Model | OK | Avg LOC | Primary Lang | Typical Project |
|-------|----|---------|-------------|-----------------|
| claude-sonnet-4.5 | 5/5 | 776 | Python | Dev workflow tools (commit gen, code analysis) |
| claude-opus-4.6 | 5/5 | 607 | Go/Rust | TUI apps (hex viewer, kanban boards) |
| claude-sonnet-4.6 | 3/5 | 506 | Python | Git/dev tools (code reviewer, analytics) |
| claude-haiku-4.5 | 5/5 | 233 | Python/Go/TS | Developer tools (task mgr, snippet mgr) |
| claude-opus-4.5 | 5/5 | 221 | Go/JS/Python | CLI utilities (tree, link checker, pomodoro) |
| gemini-3-flash | 5/5 | 61 | JS/Go/Python | Small utilities (file finder, log parser) |

**Experiment 2** (RTK removed — no environment bias):

| Model | OK | Avg LOC | Primary Lang | Typical Project |
|-------|----|---------|-------------|-----------------|
| claude-opus-4.6 | 4/5 | 408 | Python | Conway's Game of Life (every time) |
| claude-opus-4.5 | 2/5 | 291 | Python | Habit trackers |
| claude-sonnet-4.5 | 5/5 | 234 | Python | Games + task managers |
| claude-sonnet-4.6 | 5/5 | 204 | Python | Diverse interactive tools |
| claude-haiku-4.5 | 1/5 | 160 | Node.js | Standup generator |
| gemini-3-flash | 5/5 | 86 | Go/Python/JS | Small CLI tools |

**Experiment 3** (explicit "JUST DO IT" demand):

*Claude backend — Anthropic models:*

| Model | OK | Avg LOC | Primary Lang | Typical Project |
|-------|----|---------|-------------|-----------------|
| claude-haiku-4.5 | 5/5 | 467 | JS/Python | Task managers and dev tools |
| claude-sonnet-4.6 | 5/5 | 307 | Python | Diverse creative tools (maze, debate arena) |
| claude-sonnet-4.5 | 4/5 | 380 | Python | Pomodoro timers |
| claude-opus-4.5 | 3/5 | 467 | Python | Personal productivity tools |
| claude-opus-4.6 | 4/5 | 322 | Python | Conway's Game of Life (every time) |

*Claude backend — GPT models (via litellm):*

| Model | OK | Avg LOC | Primary Lang | Typical Project |
|-------|----|---------|-------------|-----------------|
| gpt-5-mini | 5/5 | 121 | Python | CLI tools with tests + CI |
| gpt-4.1-mini | 4/5 | 8 | Python | Hello World stubs |
| gpt-4.1 | 2/5 | 31 | Python | Todo CLI |
| gpt-5.4 | 1/5 | 7 | Python | Stub only |
| gpt-5.1 | 0/5 | — | — | No output |

*Codex backend — GPT models (files in sandbox, not persisted to host):*

| Model | OK | Avg LOC | Primary Lang | Typical Project |
|-------|----|---------|-------------|-----------------|
| gpt-5.4 | 5/5 | 230 | Python/HTML+JS | Diverse — web apps, CLI tools |
| gpt-5.1 | 5/5 | 98 | Python | CLI utilities with packaging |
| gpt-4.1 | 5/5 | 56 | Python | Todo list apps |
| gpt-5-mini | 4/5 | 40 | Python | Greeting utilities |
| gpt-4.1-mini | 4/5 | 8 | Python | Hello World |

*Gemini models were near-non-functional on both backends (1/20 runs on claude backend produced files).*

**Experiment 4** (Opus 4.7 — same prompt as Exp3):

| Model | OK | Avg LOC | Primary Lang | Typical Project |
|-------|----|---------|-------------|-----------------|
| claude-opus-4-7 | 5/5 | 538 | Python | Diverse simulations (reaction-diffusion, boids, maze, dungeon) |

**Experiment 5** (harness 2.1.112 — same prompt as Exp3/4):

| Model | OK | Avg LOC | Primary Lang | Typical Project |
|-------|----|---------|-------------|-----------------|
| claude-opus-4.6 | 5/5 | 387 | Python/Go | Game of Life (3/5), ray tracer, typing test |
| claude-opus-4-7 | 5/5 | 262 | Python | Boids (3/5), dungeon gen, maze solver |

### Observations

- **Environment bias matters:** With RTK in the sandbox, models built RTK-related
  dev tools. Without it, they shifted to games, interactive tools, and simpler CLIs.
- **Prompt wording matters enormously:** Adding "JUST DO IT" to Exp3 fixed haiku's
  implementation rate (1/5 → 5/5) and increased average LOC across all models.
- **Opus-4.6 Game of Life fixation weakened in newer harness:** Opus 4.6 chose
  Game of Life in all runs across Exp2 and Exp3 on harness 2.1.109 (9/9). On
  harness 2.1.112 (Exp5), fixation dropped to 3/5 — a ray tracer and typing test
  broke through. Opus 4.7 has no GoL fixation but developed a boids fixation on
  2.1.112 (3/5 in Exp5, 0/5 in Exp4 on 2.1.109).
- **Harness version affects output complexity:** Opus 4.7 on harness 2.1.109
  (Exp4) averaged 538 LOC with tests in 2/5 runs. On 2.1.112 (Exp5), it averaged
  262 LOC with no tests — suggesting the newer harness may encourage brevity.
- **Sonnet-4.6** is the most creative and reliable — 5/5 in all three experiments,
  with the most diverse project choices (maze solver, AI debate arena, ASCII clock).
- **Haiku is prompt-sensitive:** 5/5 with RTK context (Exp1), 1/5 with "propose
  ONE goal" (Exp2), 5/5 with "JUST DO IT" (Exp3). It also produced the
  highest-maturity output in Exp3 (READMEs, tests, multi-file projects).
- **Gemini models** produce significantly simpler output (61–89 LOC avg)
  compared to Claude models (221–776 LOC avg), consistent across Exp1 and Exp2.
- **Backend determines GPT ranking:** On codex (native), gpt-5.4 is best (~230 LOC,
  diverse). On claude backend, gpt-5-mini is paradoxically the only productive GPT
  model (5/5, 121 avg LOC with tests+CI). Larger GPT models produce almost nothing.
- **Codex backend: GPT works, rest broken.** GPT models built real projects on codex
  but bwrap isolation prevented file persistence. Anthropic/Gemini models failed
  (litellm translation bugs, rate limits).
- **Gemini models near-non-functional** on both backends — 1 file produced across
  20 total Gemini runs on claude backend. gemini-2.0-flash fails instantly every time.

## Usage

```bash
# Prerequisites
export LLM_GW_BASE_URL=https://your-gateway.example.com
export LLM_GW_API_KEY=sk-...

# Single run
./run.sh --backend claude --model claude-sonnet-4.6 --runtime podman -p "build something"

# Full experiment (dry run)
./experiment.sh --models models.txt --backends claude,codex --runs 5 --runtime podman --dry-run

# Full experiment
./experiment.sh --models models.txt --backends claude,codex --runs 5 --runtime podman

# Selective models
./experiment.sh --models "claude-opus-4.6,azure/gpt-5.1" --backends auto --runs 3
```

### Options

```
experiment.sh:
  --models      FILE|LIST   models.txt or comma-separated (default: all)
  --backends    LIST        claude,codex or "auto" (default: auto)
  --runs        N           runs per combination (default: 1)
  --jobs        N           max concurrent jobs per run (default: 0 = unlimited)
  --prompt      FILE        prompt file (default: prompt.txt)
  --results-dir DIR         output directory (default: results/)
  --runtime     NAME        docker or podman (default: docker)
  --dry-run                 show what would execute

run.sh:
  --backend     claude|codex
  --model       NAME
  --workspace   DIR
  --batch                   non-interactive mode
  -p            PROMPT
```

## Files

| File | Purpose |
|------|---------|
| `experiment.sh` | Orchestrator: parallel model × backend × N runs |
| `run.sh` | Container launcher for a single sandbox run |
| `prompt1.txt` | Experiment 1 prompt |
| `prompt2.txt` | Experiment 2 prompt |
| `prompt3.txt` | Experiment 3 prompt |
| `models.txt` | List of models to test |
| `results1/` | Experiment 1 output + [RESULTS.md](results1/RESULTS.md) |
| `results2/` | Experiment 2 output + [RESULTS.md](results2/RESULTS.md) |
| `results3/` | Experiment 3 output + [RESULTS.md](results3/RESULTS.md) |
| `results4/` | Experiment 4 output + [RESULTS.md](results4/RESULTS.md) |
| `results5/` | Experiment 5 output + [RESULTS.md](results5/RESULTS.md) |

## Future Experiment Ideas

### Prompt design
- **Seed project:** Provide a half-built app instead of an empty workspace to
  test whether agents can understand and extend existing code vs only greenfielding
- **~~Explicit implementation demand:~~** ~~Exp2's "propose ONE goal" caused some models
  (haiku, opus-4.5) to propose without implementing — tighten the prompt~~
  **Done in Exp3** — "JUST DO IT" fixed haiku (1/5 → 5/5) and improved opus-4.5 (2/5 → 3/5)
- **Bug fix + feature + tests:** Put a small buggy Python CLI in the workspace and
  prompt "fix the bug, add one feature, and add tests" — tests comprehension,
  debugging, feature work, and testing in one shot

### Evaluation quality
- **Functional verification:** Post-run step that tries to execute/compile/test
  what was built — distinguish "500 LOC of broken code" from "100 LOC that works"
- **Test pass rate:** If the agent wrote tests, do they actually pass?

### Model behavior
- **~~Fixation breaking:~~** ~~opus-4.6 built Game of Life 5/5 times in Exp2 — test
  with temperature variation or slightly different seed content per run~~
  **Resolved in Exp4** — Opus 4.7 broke the fixation naturally (1/5 Game of Life),
  producing 5 diverse projects with higher complexity (538 avg LOC vs 290).
- **~~GPT comparison:~~** ~~Run codex backend with `--jobs 1` (fully sequential) to
  avoid rate limits and get actual GPT data~~
  **Done in Exp3** — GPT models ran on both backends. Codex: gpt-5.4 best (230 LOC,
  diverse). Claude: gpt-5-mini only reliable model. bwrap prevents file persistence on codex.
- **Codex bwrap fix:** Files created inside codex sandbox don't persist to host mount.
  Investigate bwrap volume mount options or post-run file extraction.

### Infrastructure
- **Per-run timeout:** Some runs took 500s, others 10s — add `--timeout` for
  comparable results
- **Token budget tracking:** Usage data exists in output.json but isn't reported
- **Environment isolation:** Verify no other sandbox artifacts (beyond RTK) leak
  context that biases agent decisions
