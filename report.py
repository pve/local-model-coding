#!/usr/bin/env python3
"""
Reads results/results.json and produces:
  results/report.md  — full markdown report
  results/scores.png — bar chart (avg score) with tok/s line overlay
"""

import json
import sys
from datetime import datetime
from pathlib import Path

THIS_DIR = Path(__file__).parent
RESULTS_DIR = THIS_DIR / "results"
RESULTS_JSON = RESULTS_DIR / "results.json"
REPORT_MD = RESULTS_DIR / "report.md"
SCORES_PNG = RESULTS_DIR / "scores.png"

TEST_NAMES = {
    "T1": "JSON → YAML (flat)",
    "T2": "YAML → JSON (flat)",
    "T3": "JSON → YAML (nested)",
    "T4": "JSON → YAML with indent",
    "T5": "YAML → JSON pretty",
    "T6": "Unknown format → error exit",
}


def load_results():
    if not RESULTS_JSON.exists():
        print(f"ERROR: {RESULTS_JSON} not found — run benchmark.py first.", file=sys.stderr)
        sys.exit(1)
    with open(RESULTS_JSON) as f:
        return json.load(f)


def model_stats(results, model):
    runs = [r for r in results if r["model"] == model and not r.get("error")]
    all_runs = [r for r in results if r["model"] == model]
    if not runs:
        return None
    total_tests = runs[0]["total"]
    scores = [r["passed"] for r in runs]
    return {
        "model": model,
        "valid_runs": len(runs),
        "total_runs": len(all_runs),
        "errors": len(all_runs) - len(runs),
        "avg_score": sum(scores) / len(scores),
        "best": max(scores),
        "total_tests": total_tests,
        "avg_tps": sum(r["tokens_per_sec"] for r in runs) / len(runs),
        "avg_time": sum(r["total_time_s"] for r in runs) / len(runs),
        "avg_tokens": sum(r["output_tokens"] for r in runs) / len(runs),
        "perfect": sum(1 for s in scores if s == total_tests),
        "scores": scores,
    }


def test_matrix(results, model):
    runs = [r for r in results if r["model"] == model and not r.get("error")]
    matrix = {}
    for r in runs:
        for t in r.get("tests", []):
            tid = t["id"]
            if tid not in matrix:
                matrix[tid] = {"passed": 0, "total": 0}
            matrix[tid]["total"] += 1
            if t["passed"]:
                matrix[tid]["passed"] += 1
    return matrix


def generate_report(data):
    results = data["results"]
    models = data["models"]
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        "# LLM Coding Benchmark — JSON/YAML Transformer",
        "",
        f"*Generated: {now}*",
        "",
        "## Task",
        "One-shot prompt: write `transformer.py` (JSON↔YAML CLI). Scored by `test_transformer.py` — 6 automated tests.",
        f"Each model ran {data['runs_per_model']}×. Hardware: M1 Pro 14\", 32GB unified memory.",
        "",
        "## Summary",
        "",
        "| Model | Valid runs | Avg score | Best | Perfect | Avg tok/s | Avg time |",
        "|-------|-----------|-----------|------|---------|-----------|----------|",
    ]

    stats_map = {}
    for model in models:
        s = model_stats(results, model)
        stats_map[model] = s
        if s:
            pct = s["avg_score"] / s["total_tests"] * 100
            err_note = f" ({s['errors']} timeout)" if s["errors"] else ""
            lines.append(
                f"| {model} | {s['valid_runs']}/{s['total_runs']}{err_note}"
                f" | {s['avg_score']:.1f}/{s['total_tests']} ({pct:.0f}%)"
                f" | {s['best']}/{s['total_tests']}"
                f" | {s['perfect']}/{s['valid_runs']}"
                f" | {s['avg_tps']:.1f}"
                f" | {s['avg_time']:.1f}s |"
            )
        else:
            lines.append(f"| {model} | 0/{data['runs_per_model']} (all timeout) | — | — | — | — | — |")

    lines += ["", "## Test Pass Matrix", ""]

    test_ids = list(TEST_NAMES.keys())
    header = "| Model | " + " | ".join(test_ids) + " | Avg |"
    sep = "|-------|" + "|".join([":---:"] * len(test_ids)) + "|-----|"
    lines += [header, sep]

    for model in models:
        s = stats_map.get(model)
        if not s:
            row = "| " + " | ".join(["⏱"] * len(test_ids)) + " | timeout |"
            lines.append(f"| {model} {row}")
            continue
        matrix = test_matrix(results, model)
        cells = []
        for tid in test_ids:
            m = matrix.get(tid, {"passed": 0, "total": 1})
            frac = m["passed"] / m["total"] if m["total"] > 0 else 0
            if frac == 1.0:
                cells.append("✅")
            elif frac == 0.0:
                cells.append("❌")
            else:
                cells.append(f"{m['passed']}/{m['total']}")
        pct = s["avg_score"] / s["total_tests"] * 100
        lines.append(f"| {model} | " + " | ".join(cells) + f" | {s['avg_score']:.1f} ({pct:.0f}%) |")

    lines += ["", "*Test descriptions:*"]
    for tid, name in TEST_NAMES.items():
        lines.append(f"- **{tid}**: {name}")
    lines.append("")

    lines += ["## Observations", ""]
    valid_stats = [s for s in stats_map.values() if s]
    if valid_stats:
        best = max(valid_stats, key=lambda s: (s["avg_score"], s["avg_tps"]))
        fastest = max(valid_stats, key=lambda s: s["avg_tps"])
        lines.append(f"- **Best overall**: {best['model']} — {best['avg_score']:.1f}/{best['total_tests']} avg, {best['avg_tps']:.1f} tok/s")
        lines.append(f"- **Fastest**: {fastest['model']} at {fastest['avg_tps']:.1f} tok/s")

        g4 = stats_map.get("granite4:latest")
        g41 = stats_map.get("granite4.1:8b")
        if g4 and g41:
            delta = g41["avg_score"] - g4["avg_score"]
            speed_ratio = g4["avg_tps"] / g41["avg_tps"]
            lines.append(
                f"- **granite4.1 vs granite4**: +{delta:.1f} points, {speed_ratio:.1f}× slower "
                f"({g41['avg_tps']:.1f} vs {g4['avg_tps']:.1f} tok/s)"
            )

        ds = stats_map.get("deepseek-r1:8b")
        if ds:
            lines.append(
                f"- **deepseek-r1:8b**: {ds['errors']} of {ds['total_runs']} runs timed out at 300s "
                f"(chain-of-thought; avg {ds['avg_tokens']:.0f} tokens on valid runs)"
            )

        devstral = stats_map.get("devstral-small-2")
        if devstral is None and "devstral-small-2" in models:
            lines.append("- **devstral-small-2**: all runs timed out at 300s — 15GB too large for interactive use on 32GB M1 Pro")

        t2_fails = [m for m in models if stats_map.get(m) and
                    test_matrix(results, m).get("T2", {}).get("passed", 0) == 0]
        if t2_fails:
            lines.append(f"- **T2 (YAML→JSON) failures**: {', '.join(t2_fails)} — consistent blind spot")

    lines.append("")

    lines += ["## Detailed Results", ""]
    for model in models:
        model_runs = [r for r in results if r["model"] == model]
        lines.append(f"### {model}")
        lines.append("")
        for r in model_runs:
            if r.get("error"):
                lines.append(f"**Run {r['run']}** — ⏱ TIMEOUT")
                lines.append("")
                continue
            lines.append(
                f"**Run {r['run']}** — {r['passed']}/{r['total']} | "
                f"{r['tokens_per_sec']} tok/s | {r['total_time_s']}s | {r['output_tokens']} tokens"
            )
            lines.append("")
            lines.append("| Test | Result | Note |")
            lines.append("|------|--------|------|")
            for t in r.get("tests", []):
                mark = "✅" if t["passed"] else "❌"
                note = "" if t["passed"] else t["reason"][:80]
                lines.append(f"| {t['id']} {t['name']} | {mark} | {note} |")
            lines.append("")

    return "\n".join(lines)


def make_chart(data):
    results = data["results"]
    models = data["models"]

    stats_list = [s for s in (model_stats(results, m) for m in models) if s]
    if not stats_list:
        return

    try:
        import matplotlib.pyplot as plt
        import numpy as np

        labels = [s["model"].replace(":latest", "") for s in stats_list]
        scores = [s["avg_score"] for s in stats_list]
        tps = [s["avg_tps"] for s in stats_list]
        total = stats_list[0]["total_tests"]

        fig, ax1 = plt.subplots(figsize=(10, 6))
        x = np.arange(len(labels))

        bars = ax1.bar(x, scores, color="#4C72B0", alpha=0.85)
        ax1.set_ylim(0, total + 0.8)
        ax1.set_ylabel(f"Avg score (out of {total})", color="#4C72B0")
        ax1.set_xticks(x)
        ax1.set_xticklabels(labels, rotation=15, ha="right")
        ax1.set_title("Local LLM Coding Benchmark — JSON/YAML Transformer\nM1 Pro 14\", 32GB, Ollama")

        for bar, score in zip(bars, scores):
            ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                     f"{score:.1f}", ha="center", va="bottom", fontsize=10, fontweight="bold")

        ax2 = ax1.twinx()
        ax2.plot(x, tps, color="#DD8452", marker="o", linewidth=2, markersize=6, label="tok/s")
        ax2.set_ylabel("Tokens / sec", color="#DD8452")

        from matplotlib.patches import Patch
        from matplotlib.lines import Line2D
        legend = [
            Patch(color="#4C72B0", alpha=0.85, label="Avg score"),
            Line2D([0], [0], color="#DD8452", marker="o", label="Tok/s"),
        ]
        ax1.legend(handles=legend, loc="upper right")

        plt.tight_layout()
        plt.savefig(SCORES_PNG, dpi=150)
        plt.close()
        print(f"Wrote {SCORES_PNG}")

    except ImportError:
        total = stats_list[0]["total_tests"]
        print("\nASCII chart (matplotlib not available):")
        print(f"{'Model':<22} {'Score':>8}  {'Tok/s':>7}")
        print("-" * 42)
        for s in stats_list:
            bar = "█" * round(s["avg_score"] / total * 20)
            print(f"{s['model']:<22} {s['avg_score']:>4.1f}/{total}  {s['avg_tps']:>6.1f}  {bar}")


def main():
    data = load_results()
    RESULTS_DIR.mkdir(exist_ok=True)

    report = generate_report(data)
    REPORT_MD.write_text(report)
    print(f"Wrote {REPORT_MD}")

    make_chart(data)


if __name__ == "__main__":
    main()
