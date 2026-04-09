# Goalless Agent Experiment

Automated experiment measuring what AI coding agents actually build when given
open-ended prompts across different models and sandbox backends.

## Setup

**Backends:**
- `claude` — [sandbox-claude](https://ghcr.io/latere-ai/sandbox-claude) (Anthropic API, Claude Code)
- `codex` — [sandbox-codex](https://ghcr.io/latere-ai/sandbox-codex) (OpenAI Responses API, Codex CLI)

**Models** (see `models.txt`): 14 models across Claude, Gemini, and GPT families.

**Matrix:** Each model × each backend × 5 runs = 140 total jobs per prompt,
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

**Experiment 3** (explicit "JUST DO IT" demand — claude backend only):

| Model | OK | Avg LOC | Primary Lang | Typical Project |
|-------|----|---------|-------------|-----------------|
| claude-haiku-4.5 | 5/5 | 467 | JS/Python | Task managers and dev tools |
| claude-sonnet-4.6 | 5/5 | 307 | Python | Diverse creative tools (maze, debate arena) |
| claude-sonnet-4.5 | 4/5 | 380 | Python | Pomodoro timers |
| claude-opus-4.5 | 3/5 | 467 | Python | Personal productivity tools |
| claude-opus-4.6 | 3/5 | 290 | Python | Conway's Game of Life (every time) |

### Observations

- **Environment bias matters:** With RTK in the sandbox, models built RTK-related
  dev tools. Without it, they shifted to games, interactive tools, and simpler CLIs.
- **Prompt wording matters enormously:** Adding "JUST DO IT" to Exp3 fixed haiku's
  implementation rate (1/5 → 5/5) and increased average LOC across all models.
- **Opus-4.6 is permanently fixated on Game of Life** — chose it in all successful
  runs across Exp2 and Exp3 (8/8 times). Prompt variation doesn't break it.
- **Sonnet-4.6** is the most creative and reliable — 5/5 in all three experiments,
  with the most diverse project choices (maze solver, AI debate arena, ASCII clock).
- **Haiku is prompt-sensitive:** 5/5 with RTK context (Exp1), 1/5 with "propose
  ONE goal" (Exp2), 5/5 with "JUST DO IT" (Exp3). It also produced the
  highest-maturity output in Exp3 (READMEs, tests, multi-file projects).
- **Gemini models** produce significantly simpler output (61–89 LOC avg)
  compared to Claude models (221–776 LOC avg), consistent across Exp1 and Exp2.
- **Codex backend is non-viable** through this LLM gateway — 0/70 runs produced
  files in Exp3 due to litellm translation bugs and rate limits.
- **Claude Code sandbox only works with Anthropic models** — non-Anthropic models
  via litellm exit cleanly but produce no output.

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
- **Fixation breaking:** opus-4.6 built Game of Life 5/5 times in Exp2 — test
  with temperature variation or slightly different seed content per run
- **GPT comparison:** Run codex backend with `--jobs 1` (fully sequential) to
  avoid rate limits and get actual GPT data

### Infrastructure
- **Per-run timeout:** Some runs took 500s, others 10s — add `--timeout` for
  comparable results
- **Token budget tracking:** Usage data exists in output.json but isn't reported
- **Environment isolation:** Verify no other sandbox artifacts (beyond RTK) leak
  context that biases agent decisions
