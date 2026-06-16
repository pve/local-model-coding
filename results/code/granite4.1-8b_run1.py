#!/usr/bin/env python3

import sys
import json
import argparse
import os
from pathlib import Path
import yaml

def main():
    parser = argparse.ArgumentParser(description='Convert between JSON and YAML.')
    parser.add_argument('input_file', type=str, help='Path to a .json or .yaml file')
    parser.add_argument('--to', choices=['json', 'yaml'], required=True, help='Target format: json or yaml')
    parser.add_argument('--indent', type=int, default=None, help='Optional integer for indentation in output')

    args = parser.parse_args()

    input_path = Path(args.input_file)
    if not input_path.is_file():
        sys.stderr.write(f"Error: File '{args.input_file}' does not exist.\n")
        sys.exit(1)

    ext = input_path.suffix.lower()
    if ext == '.json':
        try:
            data = json.load(input_path.open())
        except json.JSONDecodeError as e:
            sys.stderr.write(f"Error decoding JSON: {e}\n")
            sys.exit(1)
    elif ext == '.yaml' or ext == '.yml':
        try:
            data = yaml.safe_load(input_path.open())
        except yaml.YAMLError as e:
            sys.stderr.write(f"Error parsing YAML: {e}\n")
            sys.exit(1)
    else:
        sys.stderr.write("Error: Unsupported file extension. Use .json or .yaml.\n")
        sys.exit(1)

    if args.to == 'yaml':
        output = yaml.safe_dump(data, default_flow_style=False, indent=args.indent)
    elif args.to == 'json':
        output = json.dumps(data, indent=args.indent)
    else:
        # This block should never be reached due to the choices constraint in argparse
        sys.stderr.write("Error: Unknown --to value.\n")
        sys.exit(1)

    print(output)

if __name__ == "__main__":
    main()