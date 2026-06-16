import argparse
import json
import sys

try:
    import yaml
except ImportError:
    print("Failed to import PyYAML.", file=sys.stderr)
    exit(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=str, help='Path to a .json or .yaml file')
    parser.add_argument('--to', type=str, default='yaml', choices=['json', 'yaml'], help='Output format (json or yaml)')
    parser.add_argument('--indent', type=int, default=4, help='Indentation level for output')

    args = parser.parse_args()

    try:
        with open(args.input_file, 'r') as f:
            if args.to == 'yaml':
                data = yaml.safe_load(f)
            else:  # to json
                data = json.load(f)

            print(yaml.dump(data, default_flow_style=False, width=args.indent * args.indent))
    except FileNotFoundError:
        print(f"Error: File '{args.input_file}' not found.", file=sys.stderr)
        exit(1)


if __name__ == '__main__':
    main()