# Local LLM Coding Benchmark — Project Instructions

This project benchmarks local LLMs via Ollama on a real coding task,
and produces a blog post with the results.

## Hardware

**MacBook Pro 14-inch, 2021 — M1 Pro, 32GB unified memory**

Speed test results (measured, one-shot coding prompt via Ollama API):

| Model | Size | tok/s | Verdict |
|---|---|---|---|
| tinyllama:latest | 637MB | 181.4 | too small, skip |
| deepseek-coder:latest | 776MB | 153.5 | too small, skip |
| qwen2.5-coder:1.5b | 986MB | 95.5 | too small, skip |
| qwen2.5:3b | 1.9GB | 56.3 | reference |
| llama3.2:latest | 2.0GB | 55.8 | reference |
| granite4:latest | 2.1GB | 49.9 | baseline (Granite 4.0) |
| llava:latest | 4.7GB | 38.6 | vision model, skip |
| llama3.1:8b | 4.7GB | 35.5 | reference |
| mistral:latest | 4.4GB | 26.1 | reference |
| deepseek-r1:8b | 5.2GB | 21.7 | reference (verbose: 674 tokens) |
| granite4.1:8b | 5.3GB | 19.7 | ★ main contestant |
| devstral-small-2 | ~14GB | TBD | ★ contestant (pulling) |
| gemma3:27b | 17GB | 0.8 | unusable on this machine |
| granite4.1:30b | 17GB | 0.1 | unusable — 2h per run, EXCLUDED |

**Key insight:** Models above ~8GB are not viable for interactive use on M1 Pro 32GB.
granite4.1:30b is definitively excluded from the benchmark (0.1 tok/s = ~2h per run).
devstral-small-2 (~14GB) expected to be marginal — test first before including.

## Goal

Compare coding quality of local LLMs on a one-shot Python coding task.
Output: a blog post in English (.md) written in Peter's style.

## Models under test (confirmed lineup)

| Model | Size | tok/s | Role |
|---|---|---|---|
| granite4:latest | 2.1GB | 49.9 | Baseline (Granite 4.0) |
| granite4.1:8b | 5.3GB | 19.7 | ★ Main contestant |
| mistral:latest | 4.4GB | 26.1 | Reference |
| deepseek-r1:8b | 5.2GB | 21.7 | Reference |
| devstral-small-2 | ~14GB | TBD | ★ Contestant if >5 tok/s |

Do NOT include: nomic-embed-text (embeddings), llava (vision), llama3.3 (42GB),
gemma3:27b (<1 tok/s), granite4.1:30b (0.1 tok/s), tinyllama (too small).

Before starting: run `ollama list` to confirm availability.
If devstral-small-2 is missing: `ollama pull devstral-small-2`
Run a quick speed test on devstral-small-2 before including it — if <5 tok/s, skip it.

## The coding task (one-shot prompt, identical for all models)

```
Write a Python command-line script called transformer.py that converts
between JSON and YAML formats.

Requirements:
- Usage: python transformer.py <input_file> --to <format> [--indent <n>]
- <input_file> can be .json or .yaml/.yml
- --to must be either "json" or "yaml"
- --indent (optional, integer) sets indentation level for output (default: 2)
- Output is printed to stdout
- If --to is an unsupported format, exit with a non-zero exit code and
  print an error message to stderr
- Use only Python standard library + PyYAML (import yaml)

Output only the Python code, no explanation.
```

## Test suite

`test_transformer.py` is already in this directory. It runs 6 automated tests:

- T1: JSON → YAML flat
- T2: YAML → JSON flat
- T3: JSON → YAML nested
- T4: YAML with --indent
- T5: JSON with --indent
- T6: Error on unsupported format (expect non-zero exit code)

Run it as: `python test_transformer.py <model_name> <script_path>`

A model scores 1 point per passing test. Max score: 6/6.

## Benchmark script (benchmark.py)

Build `benchmark.py` that does the following, fully automated:

1. Call `ollama list` to confirm which models are available
2. For each model (small to large):
   a. Send the one-shot coding prompt via Ollama API (http://localhost:11434/api/generate)
   b. Extract the Python code block from the response (strip markdown fences if present)
   c. Save it as `results/code/<model_slug>_run<n>.py`
   d. Run `test_transformer.py` on it, capture pass/fail per test
   e. Record: model name, run number, tokens generated, eval_duration,
      tokens/sec, pass count, per-test results
   f. Repeat 3 times per model
3. Save all results to `results/results.json`
4. Print a live summary table as it runs

### Ollama API call

```python
import requests

def query_ollama(model, prompt):
    resp = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": model, "prompt": prompt, "stream": False},
        timeout=300
    )
    data = resp.json()
    return {
        "response": data["response"],
        "tokens": data.get("eval_count", 0),
        "duration_s": data.get("eval_duration", 0) / 1e9,
        "tps": data.get("eval_count", 0) / max(data.get("eval_duration", 1) / 1e9, 0.001)
    }
```

### Code extraction

Models may wrap output in ```python ... ``` fences. Strip them:

```python
import re

def extract_code(text):
    match = re.search(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()
```

## Report generation (report.py)

Build `report.py` that reads `results/results.json` and produces:

1. `results/report.md` — markdown report with:
   - Summary table: model | avg tok/s | avg score | perfect runs (6/6)
   - Per-model per-test pass matrix
   - Key observations (auto-generated from data)

2. `results/scores.png` — bar chart using matplotlib:
   - X axis: models (sorted small to large)
   - Y axis: average score out of 6
   - Secondary: tokens/sec as line

If matplotlib is unavailable, produce ASCII chart instead.

## Blog post (blog.py or inline in report.py)

Write `posts/benchmark-local-llm-coding-2026.md` in Peter's style:

### Peter's writing style

- Direct and opinionated — states conclusions clearly, doesn't hedge endlessly
- Practitioner perspective — "I ran this on my M1 Pro Mac with 32GB RAM"
- Skeptical of benchmark theatre — acknowledges limitations honestly
- Conversational but technically precise — no fluff, no hype
- Structure: short intro → what I did → what I found → what it means
- Uses concrete numbers, not vague adjectives
- Admits surprises and unexplained results rather than papering over them
- Dry humor occasionally, never forced
- Note: Peter is semi-retired, does this for genuine curiosity, not corporate agenda

### Blog post structure

```
# Can IBM's Granite 4.1 code? I ran it against local competitors to find out

## Setup
- M1 Pro MacBook Pro 14", 32GB RAM, Ollama [version]
- Models tested, sizes, measured tok/s
- Why one-shot: levels the playing field, tests instruction following
- Why these models: what fits and runs usably on 32GB unified memory

## The speed reality (before we get to quality)
- Speed test results table
- granite4.1:30b and gemma3:27b excluded and why
- The 19.7 tok/s anomaly: granite4.1:8b slower than older/smaller models

## The task
- JSON/YAML transformer, 6 automated tests
- What each test checks
- Pass-proportion as the metric (harsh but honest)

## Results
- Summary table
- Speed vs quality observations
- Surprising findings

## What this doesn't tell you
- One task, one prompt, not agentic
- Quantization effects (default Ollama quantization used throughout)
- Small/mid models only — not a frontier comparison

## Conclusion
- Recommendation per use case
- Whether granite4.1:8b surprised or disappointed vs its own baseline (granite4:latest)
```

### Tone calibration

Reference post for inspiration (not imitation):
https://adrianco.medium.com/how-reliable-fast-and-expensive-is-each-version-of-claude-code-sonnet-through-opus-4-8-fast-272d74ffc869

Adrian's approach: statistical rigor, honest about methodology, lets numbers speak.
Peter's version: same honesty, less academic, more "here's what I actually found on my machine."

## File structure

```
local-model-coding/
├── CLAUDE.md                  ← this file
├── test_transformer.py        ← already exists
├── benchmark.py               ← build this first
├── report.py                  ← build after benchmark runs
├── results/
│   ├── results.json
│   ├── report.md
│   ├── scores.png
│   └── code/
│       ├── granite4-latest_run1.py
│       ├── granite4.1-8b_run1.py
│       └── ...
└── posts/
    └── benchmark-local-llm-coding-2026.md
```

## Execution order

1. Speed-test devstral-small-2 first — include only if >5 tok/s
2. `python benchmark.py` — runs all models, saves results.json
3. `python report.py` — generates report.md + scores.png
4. Review report.md, then generate blog post
5. Human review and edit of blog post before publishing

## Notes

- PyYAML required: `pip install pyyaml` if not present
- All Ollama calls use stream=False with 300s timeout
- deepseek-r1:8b generates verbose output (chain-of-thought): ~674 tokens vs ~200-300 for others
  — normalise this in reporting (quality score is what matters, not token count)
- granite4.1:8b is anomalously slow vs its size peers — worth noting in blog post
- Measured speeds are from a single warm run; benchmark.py will get more precise averages
