import sys
import json
from yaml import safe_load as yaml_load, safe_dump as yaml_dump, FullLoader

def write(content, format, indent=2):
    if format == 'yaml':
        print(yaml_dump(content, default_flow_style=False, indent=indent))
    elif format == 'json':
        print(json.dumps(content, indent=indent))
    else:
        sys.stderr.write(f"Error: Unknown output format '{format}'")
        sys.exit(1)

def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str, help="path to a .json or .yaml file")
    parser.add_argument("--to", type=str, choices=['yaml', 'json'], help="output format")
    parser.add_argument("--indent", type=int, default=2, help="optional integer; controls indentation for output")

    args = parser.parse_args()

    if args.input_file.endswith('.json'):
        data = json.load(open(args.input_file))
    elif args.input_file.endswith('.yaml') or args.input_file.endswith('.yml'):
        data = yaml_load(open(args.input_file), Loader=FullLoader)
    else:
        sys.stderr.write(f"Error: Input file '{args.input_file}' has an unsupported extension.")
        sys.exit(1)

    write(data, args.to, args.indent)

if __name__ == "__main__":
    main()