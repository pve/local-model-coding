import argparse
import sys

try:
    import yaml
except ImportError:
    print("Error: PyYAML library is required for this script.", file=sys.stderr)
    sys.exit(2)

def load_file(filename):
    if filename.endswith('.json'):
        with open(filename, 'r') as f:
            return json.load(f)
    elif filename.endswith(('.yaml', '.yml')):
        with open(filename, 'r') as f:
            return yaml.safe_load(f)
    else:
        raise ValueError("Unsupported file format")

def main():
    parser = argparse.ArgumentParser(description='Transform between JSON and YAML formats.')
    parser.add_argument('input_file')
    parser.add_argument('--to', choices=['json', 'yaml'], required=True, help='Target format (json or yaml)')
    parser.add_argument('--indent', type=int, default=None)
    
    args = parser.parse_args()
    
    try:
        data = load_file(args.input_file)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(3)
        
    if args.to == 'yaml':
        output = yaml.safe_dump(data, sort_keys=False, default_flow_style=False, indent=args.indent or 2)
        print(output)
    elif args.to == 'json':
        if args.indent is None:
            print(json.dumps(data))
        else:
            print(json.dumps(data, indent=args.indent))

if __name__ == '__main__':
    try:
        import json
    except ImportError:
        print("Error: JSON library not available.", file=sys.stderr)
        sys.exit(1)
        
    main()