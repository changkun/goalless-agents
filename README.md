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

### Observations

- **Environment bias matters:** With RTK in the sandbox, models built RTK-related
  dev tools. Without it, they shifted to games, interactive tools, and simpler CLIs.
- **Opus models** are the most ambitious in Exp1 (Go/Rust, TUI apps), but fixated
  on Game of Life in Exp2. opus-4.6 chose it in all 5 runs.
- **Sonnet-4.5** is the most reliable — 5/5 in both experiments, always includes
  a README.
- **Haiku** dropped from 5/5 to 1/5 implementation rate without RTK context —
  proposes well but often doesn't follow through.
- **Gemini models** produce significantly simpler output (61–89 LOC avg)
  compared to Claude models (221–776 LOC avg), consistent across both experiments.
- **Codex backend** (Exp1 only) was unreliable through this LLM gateway due to
  rate limits and litellm translation issues.

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
| `models.txt` | List of models to test |
| `results1/` | Experiment 1 output + [RESULTS.md](results1/RESULTS.md) |
| `results2/` | Experiment 2 output + [RESULTS.md](results2/RESULTS.md) |

## Future Experiment Ideas

### Prompt design
- **Seed project:** Provide a half-built app instead of an empty workspace to
  test whether agents can understand and extend existing code vs only greenfielding
- **Explicit implementation demand:** Exp2's "propose ONE goal" caused some models
  (haiku, opus-4.5) to propose without implementing — tighten the prompt
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
