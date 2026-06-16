import argparse
import json
import sys

try:
    import yaml
except ImportError:
    raise ImportError("PyYAML is required for this script.")

def main():
    parser = argparse.ArgumentParser(description='Convert between JSON and YAML.')
    parser.add_argument('input_file', type=str, help='Path to a .json or .yaml file')
    parser.add_argument('--to', type=str, default=None, help='Output format (json or yaml)')
    parser.add_argument('--indent', type=int, default=4, help='Indentation for output')

    args = parser.parse_args()

    if not args.input_file.lower().endswith(('.json', '.yaml')):
        print("Error: Input file must be a .json or .yaml file.", file=sys.stderr)
        sys.exit(1)

    try:
        with open(args.input_file, 'r') as f:
            data = json.load(f) if args.to == 'json' else yaml.safe_load(f)

        if args.to == 'json':
            print(json.dumps(data, indent=args.indent))
        elif args.to == 'yaml':
            print(yaml.dump(data, indent=args.indent))
    except (FileNotFoundError, ValueError) as e:
        print(f"Error reading or parsing the file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()