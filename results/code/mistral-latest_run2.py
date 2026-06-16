import sys
import yaml
import json

def load_file(filename):
    if filename.endswith('.json'):
        with open(filename, 'r') as f:
            return json.load(f)
    elif filename.endswith('.yaml') or filename.endswith('.yml'):
        with open(filename, 'r') as f:
            return yaml.safe_load(f)
    else:
        print(f"Error: Unsupported file type '{filename}'", file=sys.stderr)
        sys.exit(1)

def dump_output(data, format):
    if format == 'json':
        print(json.dumps(data, indent=(4 if args['indent'] else None)))
    elif format == 'yaml':
        print(yaml.safe_dump(data, default_flow_style=False, indent=(int(args['indent']) if args['indent'] else None)))
    else:
        print(f"Error: Unsupported output format '{format}'", file=sys.stderr)
        sys.exit(1)

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('input_file', help="path to a .json or .yaml file")
parser.add_argument('--to', choices=['json', 'yaml'], help="output format (default: guess from input file)")
parser.add_argument('--indent', type=int, help="optional integer; controls indentation for output (defaults to no indentation)")
args = parser.parse_args()

if args.input_file is None or args.to is None:
    print(parser.print_help(), file=sys.stderr)
    sys.exit(1)

data = load_file(args.input_file)
dump_output(data, args.to)