"""
Command-line interface for toon converter.
"""

import argparse
import json
import sys
from .converter import toon2json, json2toon


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Convert between toon format and JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Convert toon file to JSON
    pytoony input.toon -o output.json

    # Convert JSON file to toon
    pytoony input.json -o output.toon --to-toon

    # Convert from stdin to stdout
    cat input.toon | pytoony

    # Convert JSON to toon from stdin
    cat input.json | pytoony --to-toon
        """,
    )

    parser.add_argument(
        "input",
        nargs="?",
        type=str,
        help="Input file (toon or JSON). If not provided, reads from stdin.",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Output file. If not provided, writes to stdout.",
    )

    parser.add_argument(
        "--to-toon",
        action="store_true",
        help="Convert from JSON to toon format (default: convert to JSON)",
    )

    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="Indentation level for toon output (default: 2)",
    )

    args = parser.parse_args()

    # Read input
    if args.input:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                input_content = f.read()
        except FileNotFoundError:
            print(f"Error: File '{args.input}' not found.", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        input_content = sys.stdin.read()

    if not input_content.strip():
        print("Error: Empty input.", file=sys.stderr)
        sys.exit(1)

    # Auto-detect format if direction not specified
    if not args.to_toon:
        # Try to detect if input is JSON
        stripped = input_content.strip()
        if stripped.startswith("{") or stripped.startswith("["):
            try:
                # Try to parse as JSON
                json.loads(input_content)
                # If successful, it's JSON, so convert to TOON
                try:
                    output_content = json2toon(input_content, indent=args.indent)
                except Exception as e:
                    print(f"Error converting JSON to toon: {e}", file=sys.stderr)
                    sys.exit(1)
            except json.JSONDecodeError:
                # Not valid JSON, treat as TOON
                try:
                    output_content = toon2json(input_content)
                except Exception as e:
                    print(f"Error converting toon to JSON: {e}", file=sys.stderr)
                    sys.exit(1)
        else:
            # Doesn't look like JSON, treat as TOON
            try:
                output_content = toon2json(input_content)
            except Exception as e:
                print(f"Error converting toon to JSON: {e}", file=sys.stderr)
                sys.exit(1)
    else:
        # Explicitly JSON to toon
        try:
            output_content = json2toon(input_content, indent=args.indent)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error converting JSON to toon: {e}", file=sys.stderr)
            sys.exit(1)

    # Write output
    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output_content)
        except Exception as e:
            print(f"Error writing file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(output_content)


if __name__ == "__main__":
    main()
