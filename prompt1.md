We're benchmarking local LLMs via Ollama for coding quality.
Available models: granite4.1:8b, granite4.1:30b, granite4:latest, 
mistral:latest, deepseek-r1:8b — and devstral-small coming soon.

Task: build benchmark.py that sends an identical one-shot coding prompt 
to each model via the Ollama API, runs test_transformer.py on each 
output, records pass/fail per test + tokens/sec + total time, 
repeats 3x per model, and writes results.json + report.md.

test_transformer.py is already in this directory.