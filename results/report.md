# LLM Coding Benchmark — JSON/YAML Transformer

*Generated: 2026-06-14 21:26*

## Task
One-shot prompt: write `transformer.py` (JSON↔YAML CLI). Scored by `test_transformer.py` — 6 automated tests.
Each model ran 3×. Hardware: M1 Pro 14", 32GB unified memory.

## Summary

| Model | Valid runs | Avg score | Best | Perfect | Avg tok/s | Avg time |
|-------|-----------|-----------|------|---------|-----------|----------|
| granite4:latest | 3/3 | 3.7/6 (61%) | 4/6 | 0/3 | 49.6 | 7.7s |
| mistral:latest | 3/3 | 3.0/6 (50%) | 4/6 | 0/3 | 25.9 | 21.0s |
| deepseek-r1:8b | 1/3 (2 timeout) | 6.0/6 (100%) | 6/6 | 1/1 | 20.0 | 41.4s |
| granite4.1:8b | 3/3 | 6.0/6 (100%) | 6/6 | 3/3 | 17.2 | 28.9s |
| devstral-small-2 | 0/3 (all timeout) | — | — | — | — | — |

## Test Pass Matrix

| Model | T1 | T2 | T3 | T4 | T5 | T6 | Avg |
|-------|:---:|:---:|:---:|:---:|:---:|:---:|-----|
| granite4:latest | ✅ | ❌ | ✅ | ✅ | ❌ | 2/3 | 3.7 (61%) |
| mistral:latest | 2/3 | ❌ | 2/3 | 2/3 | ❌ | ✅ | 3.0 (50%) |
| deepseek-r1:8b | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 6.0 (100%) |
| granite4.1:8b | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 6.0 (100%) |
| devstral-small-2 | ⏱ | ⏱ | ⏱ | ⏱ | ⏱ | ⏱ | timeout |

*Test descriptions:*
- **T1**: JSON → YAML (flat)
- **T2**: YAML → JSON (flat)
- **T3**: JSON → YAML (nested)
- **T4**: JSON → YAML with indent
- **T5**: YAML → JSON pretty
- **T6**: Unknown format → error exit

## Observations

- **Best overall**: deepseek-r1:8b — 6.0/6 avg, 20.0 tok/s
- **Fastest**: granite4:latest at 49.6 tok/s
- **granite4.1 vs granite4**: +2.3 points, 2.9× slower (17.2 vs 49.6 tok/s)
- **deepseek-r1:8b**: 2 of 3 runs timed out at 300s (chain-of-thought; avg 802 tokens on valid runs)
- **devstral-small-2**: all runs timed out at 300s — 15GB too large for interactive use on 32GB M1 Pro
- **T2 (YAML→JSON) failures**: granite4:latest, mistral:latest — consistent blind spot

## Detailed Results

### granite4:latest

**Run 1** — 4/6 | 49.96 tok/s | 9.88s | 238 tokens

| Test | Result | Note |
|------|--------|------|
| T1 JSON → YAML (flat) | ✅ |  |
| T2 YAML → JSON (flat) | ❌ | Exit 1: Traceback (most recent call last):
  File "/Users/peter/Documents/DocsMB |
| T3 JSON → YAML (nested) | ✅ |  |
| T4 JSON → YAML (pretty, indented) | ✅ |  |
| T5 YAML → JSON (pretty) | ❌ | Exit 1: Traceback (most recent call last):
  File "/Users/peter/Documents/DocsMB |
| T6 Onbekend formaat → foutmelding | ✅ |  |

**Run 2** — 3/6 | 49.52 tok/s | 5.99s | 288 tokens

| Test | Result | Note |
|------|--------|------|
| T1 JSON → YAML (flat) | ✅ |  |
| T2 YAML → JSON (flat) | ❌ | Exit 1: Error reading or parsing the file: Expecting value: line 1 column 1 (cha |
| T3 JSON → YAML (nested) | ✅ |  |
| T4 JSON → YAML (pretty, indented) | ✅ |  |
| T5 YAML → JSON (pretty) | ❌ | Exit 1: Error reading or parsing the file: Expecting value: line 1 column 1 (cha |
| T6 Onbekend formaat → foutmelding | ❌ | Verwacht fout, maar rc=0 |

**Run 3** — 4/6 | 49.19 tok/s | 7.16s | 343 tokens

| Test | Result | Note |
|------|--------|------|
| T1 JSON → YAML (flat) | ✅ |  |
| T2 YAML → JSON (flat) | ❌ | Exit 1: Traceback (most recent call last):
  File "/Users/peter/Documents/DocsMB |
| T3 JSON → YAML (nested) | ✅ |  |
| T4 JSON → YAML (pretty, indented) | ✅ |  |
| T5 YAML → JSON (pretty) | ❌ | Exit 1: Traceback (most recent call last):
  File "/Users/peter/Documents/DocsMB |
| T6 Onbekend formaat → foutmelding | ✅ |  |

### mistral:latest

**Run 1** — 4/6 | 25.93 tok/s | 22.61s | 488 tokens

| Test | Result | Note |
|------|--------|------|
| T1 JSON → YAML (flat) | ✅ |  |
| T2 YAML → JSON (flat) | ❌ | Exit 1: Traceback (most recent call last):
  File "/Users/peter/Documents/DocsMB |
| T3 JSON → YAML (nested) | ✅ |  |
| T4 JSON → YAML (pretty, indented) | ✅ |  |
| T5 YAML → JSON (pretty) | ❌ | Exit 1: Traceback (most recent call last):
  File "/Users/peter/Documents/DocsMB |
| T6 Onbekend formaat → foutmelding | ✅ |  |

**Run 2** — 1/6 | 25.92 tok/s | 19.83s | 511 tokens

| Test | Result | Note |
|------|--------|------|
| T1 JSON → YAML (flat) | ❌ | Exit 1: Traceback (most recent call last):
  File "/Users/peter/Documents/DocsMB |
| T2 YAML → JSON (flat) | ❌ | Exit 1: Traceback (most recent call last):
  File "/Users/peter/Documents/DocsMB |
| T3 JSON → YAML (nested) | ❌ | Exit 1: Traceback (most recent call last):
  File "/Users/peter/Documents/DocsMB |
| T4 JSON → YAML (pretty, indented) | ❌ | Exit 1: Traceback (most recent call last):
  File "/Users/peter/Documents/DocsMB |
| T5 YAML → JSON (pretty) | ❌ | Exit 1: Traceback (most recent call last):
  File "/Users/peter/Documents/DocsMB |
| T6 Onbekend formaat → foutmelding | ✅ |  |

**Run 3** — 4/6 | 25.9 tok/s | 20.47s | 527 tokens

| Test | Result | Note |
|------|--------|------|
| T1 JSON → YAML (flat) | ✅ |  |
| T2 YAML → JSON (flat) | ❌ | Exit 1: Traceback (most recent call last):
  File "/Users/peter/Documents/DocsMB |
| T3 JSON → YAML (nested) | ✅ |  |
| T4 JSON → YAML (pretty, indented) | ✅ |  |
| T5 YAML → JSON (pretty) | ❌ | Exit 1: Traceback (most recent call last):
  File "/Users/peter/Documents/DocsMB |
| T6 Onbekend formaat → foutmelding | ✅ |  |

### deepseek-r1:8b

**Run 1** — ⏱ TIMEOUT

**Run 2** — 6/6 | 20.01 tok/s | 41.37s | 802 tokens

| Test | Result | Note |
|------|--------|------|
| T1 JSON → YAML (flat) | ✅ |  |
| T2 YAML → JSON (flat) | ✅ |  |
| T3 JSON → YAML (nested) | ✅ |  |
| T4 JSON → YAML (pretty, indented) | ✅ |  |
| T5 YAML → JSON (pretty) | ✅ |  |
| T6 Onbekend formaat → foutmelding | ✅ |  |

**Run 3** — ⏱ TIMEOUT

### granite4.1:8b

**Run 1** — 6/6 | 18.9 tok/s | 37.29s | 411 tokens

| Test | Result | Note |
|------|--------|------|
| T1 JSON → YAML (flat) | ✅ |  |
| T2 YAML → JSON (flat) | ✅ |  |
| T3 JSON → YAML (nested) | ✅ |  |
| T4 JSON → YAML (pretty, indented) | ✅ |  |
| T5 YAML → JSON (pretty) | ✅ |  |
| T6 Onbekend formaat → foutmelding | ✅ |  |

**Run 2** — 6/6 | 16.75 tok/s | 27.97s | 464 tokens

| Test | Result | Note |
|------|--------|------|
| T1 JSON → YAML (flat) | ✅ |  |
| T2 YAML → JSON (flat) | ✅ |  |
| T3 JSON → YAML (nested) | ✅ |  |
| T4 JSON → YAML (pretty, indented) | ✅ |  |
| T5 YAML → JSON (pretty) | ✅ |  |
| T6 Onbekend formaat → foutmelding | ✅ |  |

**Run 3** — 6/6 | 16.04 tok/s | 21.41s | 338 tokens

| Test | Result | Note |
|------|--------|------|
| T1 JSON → YAML (flat) | ✅ |  |
| T2 YAML → JSON (flat) | ✅ |  |
| T3 JSON → YAML (nested) | ✅ |  |
| T4 JSON → YAML (pretty, indented) | ✅ |  |
| T5 YAML → JSON (pretty) | ✅ |  |
| T6 Onbekend formaat → foutmelding | ✅ |  |

### devstral-small-2

**Run 1** — ⏱ TIMEOUT

**Run 2** — ⏱ TIMEOUT

**Run 3** — ⏱ TIMEOUT
