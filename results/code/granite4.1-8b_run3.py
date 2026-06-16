#!/usr/bin/env python3

import sys
import json
import argparse
from pathlib import Path
import yaml

def main():
    parser = argparse.ArgumentParser(description='Convert between JSON and YAML.')
    parser.add_argument('input_file', type=str, help='Path to a .json or .yaml file')
    parser.add_argument('--to', choices=['yaml', 'json'], required=True, help='Target format (yaml or json)')
    parser.add_argument('--indent', type=int, default=None, help='Optional integer; controls indentation for output')

    args = parser.parse_args()

    input_path = Path(args.input_file)
    if not input_path.exists():
        sys.stderr.write(f"Error: File '{args.input_file}' does not exist.\n")
        sys.exit(1)

    try:
        if args.to == 'yaml':
            if str(input_path.suffix).lower() == '.json':
                data = json.load(open(args.input_file))
            else:
                data = yaml.safe_load(open(args.input_file))

            output = yaml.safe_dump(data, default_flow_style=False, indent=args.indent)
            print(output)

        elif args.to == 'json':
            if str(input_path.suffix).lower() == '.yaml':
                data = yaml.safe_load(open(args.input_file))
            else:
                data = json.load(open(args.input_file))

            output = json.dumps(data, indent=args.indent or 4)
            print(output)

    except Exception as e:
        sys.stderr.write(f"Error: {str(e)}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()