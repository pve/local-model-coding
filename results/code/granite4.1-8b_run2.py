#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.stderr.write("PyYAML is required but not installed.\n")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Convert between JSON and YAML.")
    parser.add_argument("input_file", type=Path, help="Path to a .json or .yaml file")
    parser.add_argument("--to", choices=["yaml", "json"], required=True, help="Target format: yaml or json")
    parser.add_argument(
        "--indent",
        type=int,
        default=None,
        help="Optional integer; controls indentation for output (default: None)",
    )

    args = parser.parse_args()

    input_file = args.input_file
    if not (input_file.exists() and input_file.is_file()):
        sys.stderr.write(f"File {input_file} does not exist or is not a file.\n")
        sys.exit(1)

    ext = input_file.suffix.lower()
    if ext == ".json":
        try:
            data = json.load(input_file.open())
        except json.JSONDecodeError as e:
            sys.stderr.write(f"Failed to decode JSON: {e}\n")
            sys.exit(1)
    elif ext == ".yaml" or ext == ".yml":
        try:
            data = yaml.safe_load(input_file.open())
        except (yaml.parser.ParserError, yaml.scanner.ScannerError) as e:
            sys.stderr.write(f"Failed to parse YAML: {e}\n")
            sys.exit(1)
    else:
        sys.stderr.write(f"Unsupported file extension for {input_file}.\n")
        sys.exit(1)

    if args.to == "yaml":
        output = yaml.safe_dump(data, default_flow_style=False, indent=args.indent)
    elif args.to == "json":
        output = json.dumps(data, indent=args.indent or None)
    else:
        # This should be unreachable due to choices in argparse
        sys.stderr.write(f"Unknown --to value: {args.to}\n")
        sys.exit(1)

    print(output)


if __name__ == "__main__":
    main()