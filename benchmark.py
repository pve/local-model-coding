#!/usr/bin/env python3
"""
Benchmark local LLMs via Ollama on a JSON/YAML transformer coding task.
Sends an identical one-shot prompt to each model, runs test_transformer.py,
records pass/fail per test + tokens/sec + total time, repeats 3x per model,
and writes results.json + report.md.
"""

import importlib.util
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

MODELS = [
    "granite4:latest",
    "mistral:latest",
    "deepseek-r1:8b",
    "granite4.1:8b",
    "devstral-small-2",
]

OLLAMA_URL = "http://localhost:11434/api/generate"
RUNS_PER_MODEL = 3
THIS_DIR = Path(__file__).parent
RESULTS_DIR = THIS_DIR / "results"
CODE_DIR = RESULTS_DIR / "code"
DEVSTRAL_MIN_TPS = 5.0

CODING_PROMPT = """\
Write a Python script called transformer.py that converts between JSON and YAML.

CLI interface:
  python transformer.py <input_file> --to <format> [--indent <n>]

Rules:
- <input_file>: path to a .json or .yaml file
- --to yaml  → read input, print YAML to stdout
- --to json  → read input, print JSON to stdout
- --indent <n>: optional integer; controls indentation for output
- For any unknown --to value (e.g. --to xml): print an error to stderr and exit with a non-zero exit code
- Never write any output file; print only to stdout
- Dependencies allowed: Python standard library + PyYAML (import yaml)

Output ONLY the complete, runnable Python code. No explanation, no markdown fences.\
"""


# ─── Ollama ───────────────────────────────────────────────────────────────────

def call_ollama(model: str, prompt: str) -> dict:
    payload = {"model": model, "prompt": prompt, "stream": False}
    t0 = time.perf_counter()
    resp = requests.post(OLLAMA_URL, json=payload, timeout=300)
    elapsed = time.perf_counter() - t0
    resp.raise_for_status()
    data = resp.json()
    eval_count = data.get("eval_count", 0)
    eval_ns = data.get("eval_duration", 0)
    tps = eval_count / (eval_ns / 1e9) if eval_ns > 0 else (eval_count / elapsed if elapsed > 0 else 0)
    return {
        "response": data.get("response", ""),
        "total_time_s": round(elapsed, 2),
        "tokens_per_sec": round(tps, 2),
        "output_tokens": eval_count,
        "prompt_tokens": data.get("prompt_eval_count", 0),
    }


# ─── Code extraction ──────────────────────────────────────────────────────────

def extract_code(text: str) -> str:
    m = re.search(r"```(?:python)?\s*\n(.*?)```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    # Heuristic: if the model ignored the "no fences" instruction
    m = re.search(r"```\s*\n(.*?)```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return text.strip()


# ─── Testing ──────────────────────────────────────────────────────────────────

def load_test_module():
    path = THIS_DIR / "test_transformer.py"
    spec = importlib.util.spec_from_file_location("test_transformer", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_tests(script_path: str, mod) -> list:
    results = []
    for tc in mod.TEST_CASES:
        r = mod.run_test(script_path, tc)
        results.append({
            "id": tc["id"],
            "name": tc["name"],
            "passed": r["passed"],
            "reason": r["reason"],
            "duration_ms": r["duration_ms"],
        })
    return results


# ─── Single benchmark run ────────────────────────────────────────────────────

def benchmark_run(model: str, run_num: int, mod) -> dict:
    print(f"  [{run_num}/{RUNS_PER_MODEL}] Calling Ollama...", end="", flush=True)

    try:
        api = call_ollama(model, CODING_PROMPT)
    except Exception as e:
        print(f" ERROR: {e}")
        return {
            "model": model, "run": run_num, "error": str(e),
            "tests": [], "passed": 0, "total": len(mod.TEST_CASES),
            "tokens_per_sec": 0, "total_time_s": 0,
            "output_tokens": 0, "prompt_tokens": 0,
        }

    print(f" {api['total_time_s']}s  {api['tokens_per_sec']} tok/s  ({api['output_tokens']} tokens)")

    code = extract_code(api["response"])
    slug = model.replace(":", "-")
    script_path = CODE_DIR / f"{slug}_run{run_num}.py"
    script_path.write_text(code)

    print(f"         Testing generated script...", end="", flush=True)
    tests = run_tests(script_path, mod)
    passed = sum(1 for t in tests if t["passed"])
    total = len(tests)
    print(f" {passed}/{total} passed")
    for t in tests:
        mark = "✅" if t["passed"] else "❌"
        print(f"           {mark} {t['id']} {t['name']}")

    return {
        "model": model,
        "run": run_num,
        "error": None,
        "tests": tests,
        "passed": passed,
        "total": total,
        "tokens_per_sec": api["tokens_per_sec"],
        "total_time_s": api["total_time_s"],
        "output_tokens": api["output_tokens"],
        "prompt_tokens": api["prompt_tokens"],
    }


# ─── Report ───────────────────────────────────────────────────────────────────

def generate_report(all_results: list) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# LLM Coding Benchmark — JSON/YAML Transformer",
        "",
        f"*Generated: {now}*",
        "",
        "## Task",
        "Write a Python `transformer.py` that converts JSON↔YAML via a CLI.",
        "Scored by `test_transformer.py` (6 test cases).",
        "",
    ]

    # Unique model order
    seen = []
    for r in all_results:
        if r["model"] not in seen:
            seen.append(r["model"])

    # Summary table
    lines += [
        "## Summary",
        "",
        "| Model | Runs | Avg score | Best run | Avg tok/s | Avg time (s) |",
        "|-------|------|-----------|----------|-----------|--------------|",
    ]
    for model in seen:
        runs = [r for r in all_results if r["model"] == model and not r.get("error")]
        if not runs:
            lines.append(f"| {model} | 0 | — | — | — | — |")
            continue
        total_tests = runs[0]["total"]
        avg_score = sum(r["passed"] for r in runs) / (len(runs) * total_tests) * 100
        best = max(r["passed"] for r in runs)
        avg_tps = sum(r["tokens_per_sec"] for r in runs) / len(runs)
        avg_time = sum(r["total_time_s"] for r in runs) / len(runs)
        lines.append(
            f"| {model} | {len(runs)} | {avg_score:.0f}% | {best}/{total_tests} | {avg_tps:.1f} | {avg_time:.1f} |"
        )

    lines.append("")

    # Per-model details
    lines.append("## Detailed Results")
    lines.append("")
    for model in seen:
        lines.append(f"### {model}")
        lines.append("")
        for r in all_results:
            if r["model"] != model:
                continue
            lines.append(f"**Run {r['run']}** — {r['passed']}/{r['total']} passed  |  {r['tokens_per_sec']} tok/s  |  {r['total_time_s']}s")
            lines.append("")
            if r.get("error"):
                lines.append(f"> Error: {r['error']}")
                lines.append("")
                continue
            lines.append("| Test | Result | Time |")
            lines.append("|------|--------|------|")
            for t in r["tests"]:
                mark = "✅" if t["passed"] else "❌"
                reason = "" if t["passed"] else f" — {t['reason'][:80]}"
                lines.append(f"| {t['id']} {t['name']} | {mark}{reason} | {t['duration_ms']}ms |")
            lines.append("")

    return "\n".join(lines)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", help="Comma-separated subset of models to run")
    args = parser.parse_args()

    models = args.models.split(",") if args.models else list(MODELS)

    print(f"\n{'='*60}")
    print(f"  Ollama LLM Coding Benchmark")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")
    print(f"Models : {', '.join(models)}")
    print(f"Runs   : {RUNS_PER_MODEL}x per model")
    print()

    try:
        requests.get("http://localhost:11434", timeout=5)
    except Exception:
        print("ERROR: Ollama not reachable at http://localhost:11434 — is it running?")
        sys.exit(1)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    CODE_DIR.mkdir(parents=True, exist_ok=True)

    mod = load_test_module()
    all_results = []

    # Merge with any existing results.json so partial runs accumulate
    results_path = RESULTS_DIR / "results.json"
    existing = []
    if results_path.exists():
        try:
            existing = json.loads(results_path.read_text()).get("results", [])
        except Exception:
            pass

    for model in models:
        print(f"\n{'─'*60}")
        print(f"  Model: {model}")
        print(f"{'─'*60}")
        for run in range(1, RUNS_PER_MODEL + 1):
            result = benchmark_run(model, run, mod)
            all_results.append(result)

    combined = existing + all_results
    all_models = list(dict.fromkeys([r["model"] for r in combined]))

    output = {
        "timestamp": datetime.now().isoformat(),
        "models": all_models,
        "runs_per_model": RUNS_PER_MODEL,
        "prompt": CODING_PROMPT,
        "results": combined,
    }
    results_path.write_text(json.dumps(output, indent=2))
    print(f"\nWrote {results_path}")

    print("\n── Final Scores ──────────────────────────────────────────")
    for model in models:
        runs = [r for r in all_results if r["model"] == model and not r.get("error")]
        if runs:
            total_tests = runs[0]["total"]
            avg = sum(r["passed"] for r in runs) / (len(runs) * total_tests) * 100
            best = max(r["passed"] for r in runs)
            print(f"  {model:<25}  avg {avg:.0f}%  best {best}/{total_tests}")
    print(f"\nNext: python report.py")
    print()


if __name__ == "__main__":
    main()
