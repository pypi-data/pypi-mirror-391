"""Command-line interface for json2toon and toon2json."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from json2toon import ToonConfig, ToonParseConfig, json_to_toon, toon_to_json


def json2toon_main() -> None:
    """Main entry point for json2toon CLI."""
    parser = argparse.ArgumentParser(
        description="Convert JSON to TOON format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  json2toon input.json -o output.toon
  cat data.json | json2toon
  json2toon input.json --indent 4 --delimiter tab
        """,
    )

    parser.add_argument(
        "input",
        nargs="?",
        help="Input JSON file (default: stdin)",
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Output TOON file (default: stdout)",
    )

    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        metavar="SIZE",
        help="Indentation size (default: 2)",
    )

    parser.add_argument(
        "--delimiter",
        choices=["comma", "tab", "pipe"],
        default="comma",
        metavar="DELIM",
        help="Delimiter: comma, tab, or pipe (default: comma)",
    )

    parser.add_argument(
        "--key-folding",
        choices=["safe"],
        metavar="MODE",
        help="Key folding mode: safe (default: none)",
    )

    parser.add_argument(
        "--no-strict",
        action="store_true",
        help="Disable strict mode validation",
    )

    args = parser.parse_args()

    try:
        # Read input
        if args.input:
            input_path = Path(args.input)
            if not input_path.exists():
                print(f"Error: Input file not found: {args.input}", file=sys.stderr)
                sys.exit(1)
            with input_path.open() as f:
                data = json.load(f)
        else:
            data = json.load(sys.stdin)

        # Configure encoder
        delimiter_map = {
            "comma": ",",
            "tab": "\t",
            "pipe": "|",
        }

        config = ToonConfig(
            indent_size=args.indent,
            delimiter=delimiter_map[args.delimiter],
            key_folding=args.key_folding,
            strict=not args.no_strict,
        )

        # Convert
        toon_string = json_to_toon(data, config)

        # Write output
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(toon_string + "\n")
        else:
            print(toon_string)

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def toon2json_main() -> None:
    """Main entry point for toon2json CLI."""
    parser = argparse.ArgumentParser(
        description="Convert TOON to JSON format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  toon2json input.toon -o output.json
  cat data.toon | toon2json
  toon2json input.toon --pretty
        """,
    )

    parser.add_argument(
        "input",
        nargs="?",
        help="Input TOON file (default: stdin)",
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Output JSON file (default: stdout)",
    )

    parser.add_argument(
        "--expand-paths",
        choices=["safe"],
        metavar="MODE",
        help="Path expansion mode: safe (default: none)",
    )

    parser.add_argument(
        "--no-strict",
        action="store_true",
        help="Disable strict mode validation",
    )

    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output",
    )

    parser.add_argument(
        "--indent-json",
        type=int,
        default=2,
        metavar="SIZE",
        help="JSON indentation size when --pretty is used (default: 2)",
    )

    args = parser.parse_args()

    try:
        # Read input
        if args.input:
            input_path = Path(args.input)
            if not input_path.exists():
                print(f"Error: Input file not found: {args.input}", file=sys.stderr)
                sys.exit(1)
            toon_string = input_path.read_text()
        else:
            toon_string = sys.stdin.read()

        # Configure decoder
        config = ToonParseConfig(
            expand_paths=args.expand_paths,
            strict=not args.no_strict,
        )

        # Convert
        data: Any = toon_to_json(toon_string, config)

        # Format output
        if args.pretty:
            json_string = json.dumps(data, indent=args.indent_json, ensure_ascii=False)
        else:
            json_string = json.dumps(data, ensure_ascii=False)

        # Write output
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(json_string + "\n")
        else:
            print(json_string)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    # Allow running as python -m json2toon.cli json2toon or toon2json
    if len(sys.argv) > 1 and sys.argv[1] in ("json2toon", "toon2json"):
        cmd = sys.argv.pop(1)
        if cmd == "json2toon":
            json2toon_main()
        else:
            toon2json_main()
    else:
        print("Usage: python -m json2toon.cli [json2toon|toon2json] [options]", file=sys.stderr)
        sys.exit(1)
