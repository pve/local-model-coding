import argparse
import json
from pathlib import Path

try:
    from yaml import safe_load as load_yaml, dump as dump_yaml
except ImportError:
    print("PyYAML not installed. Please install it to use the --to yaml option.", file=sys.stderr)
    sys.exit(1)

def parse_args():
    parser = argparse.ArgumentParser(description="Convert between JSON and YAML.")
    parser.add_argument('input_file', type=str, help='Path to a .json or .yaml file')
    parser.add_argument('--to', type=str, choices=['json', 'yaml'], default='yaml',
                        help='Output format (json or yaml)')
    parser.add_argument('--indent', type=int, default=None,
                        help='Indentation level for output')
    return parser.parse_args()

def main():
    args = parse_args()
    path = Path(args.input_file)

    if not path.suffix in ['.json', '.yaml']:
        print(f"Error: Unsupported file extension {path.suffix}", file=sys.stderr)
        sys.exit(1)

    try:
        with path.open('r') as f:
            data = load_yaml(f, pure=True) if path.suffix == '.yaml' else json.load(f)
    except ValueError:
        print(f"Error: Invalid JSON/YAML syntax in {path}", file=sys.stderr)
        sys.exit(1)

    indent = args.indent
    if args.to == 'json':
        print(json.dumps(data, indent=indent))
    else:
        print(dump_yaml(data, default_flow_style=False, width=float('inf'), indent=indent))

if __name__ == "__main__":
    main()