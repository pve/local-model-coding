# Local LLM Coding Benchmark

Benchmarks local LLMs (via [Ollama](https://ollama.com)) on a single one-shot
Python coding task — building a JSON↔YAML transformer — and produces a blog post
with the results. Run on an M1 Pro MacBook Pro, 32GB RAM.

**Why:** to see how well small/mid-size models that actually fit on a 32GB laptop
can code, with Granite 4.1 as the model of interest.

## How it works

Each model gets the same prompt, its output is run against 6 automated tests,
repeated 3× per model. Score = tests passed (max 6).

## Files

| File | What |
|---|---|
| [CLAUDE.md](CLAUDE.md) | Full project spec: hardware, models, task, methodology |
| [benchmark.py](benchmark.py) | Sends the prompt to each model, runs tests, writes `results/results.json` |
| [test_transformer.py](test_transformer.py) | The 6-test suite each model's output is graded against |
| [report.py](report.py) | Turns `results.json` into `results/report.md` + `scores.png` |
| [blog.py](blog.py) | Generates the blog post from results |
| [results/](results/) | `results.json`, `report.md`, `scores.png`, and each model's generated code under `code/` |
| [posts/](posts/) | The finished blog post |
| [prompt1.md](prompt1.md) | Original kickoff prompt (notes) |

## Run it

```bash
pip install pyyaml requests matplotlib
python benchmark.py   # runs all models -> results/results.json
python report.py      # -> results/report.md + results/scores.png
```

Needs Ollama running locally with the models pulled (`ollama list`).
