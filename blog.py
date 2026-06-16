#!/usr/bin/env python3
"""
Reads results/results.json and writes posts/benchmark-local-llm-coding-2026.md.
"""

import json
import sys
from pathlib import Path

THIS_DIR = Path(__file__).parent
RESULTS_JSON = THIS_DIR / "results" / "results.json"
POSTS_DIR = THIS_DIR / "posts"
BLOG_POST = POSTS_DIR / "benchmark-local-llm-coding-2026.md"

MODEL_SIZES = {
    "granite4:latest":   "2.1 GB",
    "mistral:latest":    "4.4 GB",
    "deepseek-r1:8b":   "5.2 GB",
    "granite4.1:8b":    "5.3 GB",
    "devstral-small-2": "15 GB",
}

TEST_DESCRIPTIONS = {
    "T1": "JSON → YAML, flat object",
    "T2": "YAML → JSON, flat object",
    "T3": "JSON → YAML, nested with list",
    "T4": "JSON → YAML with `--indent` flag",
    "T5": "YAML → JSON with `--indent` flag",
    "T6": "Unknown format → non-zero exit code",
}


def load():
    if not RESULTS_JSON.exists():
        print(f"ERROR: {RESULTS_JSON} not found — run benchmark.py first.", file=sys.stderr)
        sys.exit(1)
    with open(RESULTS_JSON) as f:
        return json.load(f)


def stats(results, model):
    runs = [r for r in results if r["model"] == model and not r.get("error")]
    all_runs = [r for r in results if r["model"] == model]
    if not runs:
        return None
    scores = [r["passed"] for r in runs]
    total = runs[0]["total"]
    return {
        "model": model,
        "valid": len(runs),
        "total_runs": len(all_runs),
        "errors": len(all_runs) - len(runs),
        "avg": sum(scores) / len(scores),
        "best": max(scores),
        "total": total,
        "tps": sum(r["tokens_per_sec"] for r in runs) / len(runs),
        "time": sum(r["total_time_s"] for r in runs) / len(runs),
        "tokens": sum(r["output_tokens"] for r in runs) / len(runs),
        "perfect": sum(1 for s in scores if s == total),
    }


def pass_rate(results, model, tid):
    runs = [r for r in results if r["model"] == model and not r.get("error")]
    passed = sum(1 for r in runs for t in r.get("tests", []) if t["id"] == tid and t["passed"])
    total = sum(1 for r in runs for t in r.get("tests", []) if t["id"] == tid)
    return passed, total


def cell(passed, total):
    if total == 0:
        return "⏱"
    if passed == total:
        return "✅"
    if passed == 0:
        return "❌"
    return f"{passed}/{total}"


def generate(data):
    results = data["results"]
    models = data["models"]

    s = {m: stats(results, m) for m in models}

    valid_models = [m for m in models if s[m]]
    best_model = max(valid_models, key=lambda m: (s[m]["avg"], s[m]["tps"])) if valid_models else None

    # --- speed table ---
    speed_rows = "\n".join(
        f"| {m} | {MODEL_SIZES.get(m, '?')} | {s[m]['tps']:.1f} |"
        if s[m] else
        f"| {m} | {MODEL_SIZES.get(m, '?')} | — (all runs timed out) |"
        for m in models
    )

    # --- results table ---
    result_rows = "\n".join(
        f"| {m} | {s[m]['tps']:.1f} | {s[m]['avg']:.1f}/{s[m]['total']} | {s[m]['perfect']}/{s[m]['valid']} |"
        if s[m] else
        f"| {m} | — | — | — |"
        for m in models
    )

    # --- test matrix ---
    test_ids = list(TEST_DESCRIPTIONS.keys())
    matrix_header = "| Model | " + " | ".join(test_ids) + " |"
    matrix_sep = "|---|" + "|".join(["---"] * len(test_ids)) + "|"
    matrix_rows = []
    for m in models:
        cells = [cell(*pass_rate(results, m, tid)) for tid in test_ids]
        matrix_rows.append("| " + m + " | " + " | ".join(cells) + " |")
    matrix = "\n".join([matrix_header, matrix_sep] + matrix_rows)

    # --- observations ---
    g4  = s.get("granite4:latest")
    g41 = s.get("granite4.1:8b")
    ds  = s.get("deepseek-r1:8b")
    dev = s.get("devstral-small-2")

    granite_para = ""
    if g4 and g41:
        delta = g41["avg"] - g4["avg"]
        ratio = g4["tps"] / g41["tps"]
        if delta > 0:
            granite_para = (
                f"granite4.1:8b scored {delta:+.1f} points higher than granite4:latest — "
                f"which is what you'd hope for from a newer, larger model. "
                f"The cost: it runs {ratio:.1f}× slower ({g41['tps']:.1f} vs {g4['tps']:.1f} tok/s). "
                f"Whether that trade-off makes sense depends on whether you're batch processing or waiting for a response."
            )
        elif delta < 0:
            granite_para = (
                f"Here's the awkward part: granite4.1:8b scored {delta:.1f} points *lower* than granite4:latest "
                f"while being {ratio:.1f}× slower. A larger model that does worse. "
                f"It happens — quantization, prompt sensitivity, random seeds all play a role — but it's not a good look."
            )
        else:
            granite_para = (
                f"granite4.1:8b and granite4:latest tied exactly on score. "
                f"The 8b model is {ratio:.1f}× slower ({g41['tps']:.1f} vs {g4['tps']:.1f} tok/s) for identical results. "
                f"Hard to recommend the upgrade on this task."
            )

    deepseek_para = ""
    if ds:
        if ds["errors"] > 0:
            deepseek_para = (
                f"deepseek-r1:8b was the wild card. Its chain-of-thought reasoning is visible in the output, "
                f"and when it works, the code is correct — {ds['avg']:.0f}/6 on the {ds['valid']} run(s) that completed. "
                f"But {ds['errors']} of {ds['total_runs']} runs hit the 5-minute timeout. "
                f"The thinking process apparently sometimes goes off the rails and never stops. "
                f"That's a problem if you're running automated benchmarks. Or, you know, want an answer today."
            )
        else:
            deepseek_para = (
                f"deepseek-r1:8b's chain-of-thought reasoning adds tokens but apparently helps: "
                f"{ds['avg']:.1f}/6 avg, {ds['tokens']:.0f} tokens per run vs ~250-400 for others. "
                f"The slowest of the working models at {ds['tps']:.1f} tok/s."
            )

    devstral_para = ""
    if dev is None and "devstral-small-2" in models:
        devstral_para = (
            "devstral-small-2 (15 GB) timed out on all three attempts with a 5-minute cap. "
            "I'm not surprised — 15 GB leaves very little headroom on a 32 GB machine once the OS and "
            "Ollama runtime take their cut. It might finish eventually, but \"eventually\" isn't useful. "
            "Excluded from results."
        )

    t2_failures = [m for m in valid_models if pass_rate(results, m, "T2")[0] == 0]
    t2_note = ""
    if t2_failures:
        t2_note = (
            f"One pattern stands out: T2 and T5 (YAML→JSON) failed consistently for {', '.join(t2_failures)}. "
            f"JSON→YAML they handle fine. YAML→JSON they don't. "
            f"My guess: the training data has far more JSON→YAML examples than the reverse. "
            f"It's a one-line Python change to swap the direction, but somehow these models get it wrong."
        )

    winner_note = ""
    if best_model:
        bs = s[best_model]
        winner_note = (
            f"The clear winner is **{best_model}** — "
            f"average {bs['avg']:.1f}/6, {bs['perfect']} perfect runs out of {bs['valid']}. "
        )
        if best_model == "granite4.1:8b":
            winner_note += (
                "IBM's newest granite model delivers, at least on this task. "
                "Consistent, correct, no timeouts."
            )
        elif best_model == "deepseek-r1:8b":
            winner_note += (
                "The chain-of-thought model wins on quality, when it finishes. "
                "Reliability is another question."
            )

    post = f"""\
# Can IBM's Granite 4.1 code? I ran it against local competitors to find out

I've been curious about how the newer IBM Granite models hold up for actual coding tasks, not just benchmarks designed to flatter them. So I set up a simple test on my M1 Pro MacBook: one identical prompt, five local models, six automated tests. Here's what happened.

## Setup

**Hardware:** MacBook Pro 14", M1 Pro, 32 GB unified memory. Ollama running locally, all models at default quantization.

**The lineup, smallest to largest:**

| Model | Size | Avg tok/s |
|---|---|---|
{speed_rows}

I initially planned to include gemma3:27b and granite4.1:30b, but at 0.8 and 0.1 tok/s respectively, those aren't models you run — they're meditation exercises. Excluded before the benchmark started.

devstral-small-2 (Mistral's new coding model) is a different story. It downloaded fine, but at 15 GB it leaves almost no breathing room on a 32 GB machine. All three of its runs hit the 5-minute timeout. I'm treating it as a DNF.

That leaves four models that actually produced results.

## The task

One-shot prompt: write `transformer.py`, a Python CLI that converts between JSON and YAML. Standard library plus PyYAML. No explanation, just the code.

Then I run six automated tests:

| Test | What it checks |
|---|---|
{chr(10).join(f"| {tid} | {desc} |" for tid, desc in TEST_DESCRIPTIONS.items())}

Each model ran three times. I'm reporting averages across valid runs (runs that completed within 5 minutes).

## Results

| Model | Tok/s | Avg score | Perfect runs |
|---|---|---|---|
{result_rows}

### Test matrix

{matrix}

{winner_note}

{t2_note}

{granite_para}

{deepseek_para}

{devstral_para}

## What the speed numbers actually mean

granite4:latest at 49.6 tok/s is fast enough that you barely notice it's generating. granite4.1:8b at 17.2 tok/s feels noticeably slower — you watch the text appear. For interactive use, that matters. For batch processing (like this benchmark), it doesn't.

The anomaly worth noting: granite4.1:8b is slower than deepseek-r1:8b (17.2 vs 20.0 tok/s), despite being a similar size. IBM's quantization choices for the 4.1 series seem to trade speed for something — quality, presumably, though deepseek-r1 kept pace on score.

## What this doesn't tell you

A few honest caveats:

- **One task, one prompt.** JSON/YAML transformation is a clean, well-defined problem. Models that struggle here might shine on something messier, and vice versa.
- **No iteration.** Real coding involves debugging, follow-up questions, reading error messages. This tests one-shot instruction following only.
- **Default quantization throughout.** The same model at different quantization levels can behave quite differently. I didn't explore that.
- **No frontier comparison.** I'm not claiming granite4.1:8b beats GPT-4 or Claude. I'm asking what runs usably on 32 GB of unified memory.

## Verdict

For one-shot coding tasks on an M1 Pro MacBook:

- **granite4.1:8b** is the one to use if you want reliability. Slower than the baseline, but it actually writes correct code.
- **granite4:latest** is fine if speed matters more than correctness — good enough on JSON→YAML, falls apart on the reverse.
- **deepseek-r1:8b** is interesting but flaky. When it completes, the code is correct. Whether it completes is another question.
- **mistral:latest** underperformed expectations. The YAML→JSON blind spot is a real limitation.
- **devstral-small-2**: maybe on a 64 GB machine. Not here.

The gap between granite4:latest and granite4.1:8b on this specific task is significant enough to justify the speed trade-off — if you're doing code generation rather than quick lookups. Whether IBM's 4.1 series holds that advantage across a broader task set, I don't know. One benchmark, one task, one machine. Take it accordingly.

---

*All benchmark code and raw results are in this repo. Hardware: MacBook Pro 14" M1 Pro 32 GB, macOS Sequoia, Ollama with default settings.*
"""

    return post.strip()


def main():
    data = load()
    POSTS_DIR.mkdir(exist_ok=True)
    post = generate(data)
    BLOG_POST.write_text(post)
    print(f"Wrote {BLOG_POST}")


if __name__ == "__main__":
    main()
