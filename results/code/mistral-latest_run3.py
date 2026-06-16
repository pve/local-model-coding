import sys
import json
import yaml
from yaml import YAMLError as YAMLException

def load_yaml(stream):
    try:
        return yaml.safe_load(stream)
    except YAMLException as e:
        print(f"Error loading YAML: {e}", file=sys.stderr)
        sys.exit(1)

def load_json(stream):
    try:
        return json.loads(stream)
    except json.JSONDecodeError as e:
        print(f"Error loading JSON: {e}", file=sys.stderr)
        sys.exit(1)

def dump_yaml(data, stream, indent=2):
    yaml.safe_dump(data, stream, default_flow_style=False, indent=indent)

def dump_json(data, stream, indent=None):
    json.dump(data, stream, indent=indent)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str)
    parser.add_argument("--to", choices=["json", "yaml"], required=True)
    parser.add_argument("--indent", type=int, default=None)
    args = parser.parse_args()

    with open(args.input_file, "r") as input_stream:
        if args.to == "json":
            data = load_json(input_stream)
            dump_json(data, sys.stdout, args.indent)
        elif args.to == "yaml":
            data = load_yaml(input_stream)
            dump_yaml(data, sys.stdout, args.indent)
        else:
            print(f"Unknown format: {args.to}", file=sys.stderr)
            sys.exit(1)