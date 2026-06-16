"""
Test suite for the JSON/YAML transformer coding challenge.
Tests each contestant's transformer.py automatically.
"""

import subprocess
import sys
import json
import yaml
import tempfile
import os
import time

# ─── Test Cases ───────────────────────────────────────────────────────────────

TEST_CASES = [
    {
        "id": "T1",
        "name": "JSON → YAML (flat)",
        "description": "Converteer een plat JSON object naar YAML",
        "input_file": "input.json",
        "input_content": json.dumps({"name": "Alice", "age": 30, "active": True}),
        "args": ["--to", "yaml"],
        "validate": lambda out: (
            "name: Alice" in out and "age: 30" in out and "active: true" in out
        ),
    },
    {
        "id": "T2",
        "name": "YAML → JSON (flat)",
        "description": "Converteer een plat YAML bestand naar JSON",
        "input_file": "input.yaml",
        "input_content": "name: Bob\nage: 25\nactive: false\n",
        "args": ["--to", "json"],
        "validate": lambda out: (
            json.loads(out).get("name") == "Bob"
            and json.loads(out).get("age") == 25
            and json.loads(out).get("active") == False
        ),
    },
    {
        "id": "T3",
        "name": "JSON → YAML (nested)",
        "description": "Geneste structuur met lijst",
        "input_file": "input.json",
        "input_content": json.dumps({
            "server": {"host": "localhost", "port": 8080},
            "tags": ["web", "api"]
        }),
        "args": ["--to", "yaml"],
        "validate": lambda out: (
            "host: localhost" in out and "port: 8080" in out and "- web" in out
        ),
    },
    {
        "id": "T4",
        "name": "JSON → YAML (pretty, indented)",
        "description": "Optionele --indent vlag voor YAML inspringing",
        "input_file": "input.json",
        "input_content": json.dumps({"a": {"b": {"c": 42}}}),
        "args": ["--to", "yaml", "--indent", "4"],
        "validate": lambda out: "c: 42" in out,  # structuur moet kloppen
    },
    {
        "id": "T5",
        "name": "YAML → JSON (pretty)",
        "description": "JSON output met pretty-print",
        "input_file": "input.yaml",
        "input_content": "items:\n  - id: 1\n    label: foo\n  - id: 2\n    label: bar\n",
        "args": ["--to", "json", "--indent", "2"],
        "validate": lambda out: (
            json.loads(out)["items"][1]["label"] == "bar"
        ),
    },
    {
        "id": "T6",
        "name": "Onbekend formaat → foutmelding",
        "description": "Script moet een duidelijke foutmelding geven bij --to xyz",
        "input_file": "input.json",
        "input_content": json.dumps({"x": 1}),
        "args": ["--to", "xml"],
        "validate": lambda out: True,  # we controleren exit code != 0
        "expect_error": True,
    },
]


def run_test(script_path, test):
    """Run one test case against the provided script."""
    with tempfile.TemporaryDirectory() as tmpdir:
        in_path = os.path.join(tmpdir, test["input_file"])
        with open(in_path, "w") as f:
            f.write(test["input_content"])

        cmd = [sys.executable, script_path, in_path] + test["args"]

        t0 = time.perf_counter()
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
            )
        except subprocess.TimeoutExpired:
            return {"passed": False, "reason": "Timeout (>10s)", "duration_ms": 9999}
        elapsed = round((time.perf_counter() - t0) * 1000)

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        rc = result.returncode

        if test.get("expect_error"):
            passed = rc != 0
            reason = "OK – exit code != 0" if passed else f"Verwacht fout, maar rc={rc}"
        else:
            if rc != 0:
                return {"passed": False, "reason": f"Exit {rc}: {stderr or stdout}", "duration_ms": elapsed}
            try:
                passed = test["validate"](stdout)
                reason = "OK" if passed else f"Validatie mislukt. Output:\n{stdout[:300]}"
            except Exception as e:
                passed = False
                reason = f"Validatie exception: {e}\nOutput: {stdout[:300]}"

        return {"passed": passed, "reason": reason, "duration_ms": elapsed}


def score_model(model_name, script_path):
    print(f"\n{'='*60}")
    print(f"  Model: {model_name}")
    print(f"  Script: {script_path}")
    print(f"{'='*60}")

    results = []
    for tc in TEST_CASES:
        r = run_test(script_path, tc)
        status = "✅ PASS" if r["passed"] else "❌ FAIL"
        print(f"  {tc['id']} {tc['name']:<35} {status}  ({r['duration_ms']}ms)")
        if not r["passed"]:
            print(f"     → {r['reason']}")
        results.append({**tc, **r, "model": model_name})

    passed = sum(1 for r in results if r["passed"])
    print(f"\n  Score: {passed}/{len(TEST_CASES)}")
    return results


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Gebruik: python test_transformer.py <model_naam> <script_pad>")
        print("Voorbeeld: python test_transformer.py granite4.1-8b /tmp/transformer_g8b.py")
        sys.exit(1)

    model = sys.argv[1]
    script = sys.argv[2]

    if not os.path.exists(script):
        print(f"Script niet gevonden: {script}")
        sys.exit(1)

    score_model(model, script)
