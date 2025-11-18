"""
Core converter functions for TOON (Token Oriented Object Notation) format and JSON.
"""

import json
import re
from typing import Any, Dict, List, Union, Tuple


def toon2json(toon_content: str) -> str:
    """
    Convert TOON format string to JSON string.

    TOON (Token Oriented Object Notation) format features:
    - Simple key-value pairs: key: value or key=value
    - Tabular arrays: key[count]{field1,field2,...}: followed by rows
    - Nested structures use indentation
    - Minimal syntax (no braces, minimal quotes)

    Args:
        toon_content: String in TOON format

    Returns:
        JSON string representation
    """
    lines = toon_content.strip().split("\n")
    result = {}
    stack = [result]
    indent_stack = [0]
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Skip empty lines and comments
        if not stripped or stripped.startswith("#"):
            i += 1
            continue

        # Calculate indentation
        indent = len(line) - len(line.lstrip())
        current_indent = indent_stack[-1]

        # Pop stack if we're at a lower indentation level
        while len(indent_stack) > 1 and indent <= indent_stack[-2]:
            stack.pop()
            indent_stack.pop()
            current_indent = indent_stack[-1]

        # Check for tabular array format: key[count]{field1,field2,...}:
        tabular_match = re.match(r"^(\w+)\[(\d+)\]\{([^}]+)\}:?\s*$", stripped)
        if tabular_match:
            key = tabular_match.group(1)
            count = int(tabular_match.group(2))
            fields = [f.strip() for f in tabular_match.group(3).split(",")]

            # Read the array rows
            array_data = []
            i += 1
            rows_read = 0

            while i < len(lines) and rows_read < count:
                row_line = lines[i]
                row_indent = len(row_line) - len(row_line.lstrip())
                row_stripped = row_line.strip()

                # Stop if we've gone back to a lower indentation level
                if (
                    row_indent <= indent
                    and row_stripped
                    and not row_stripped.startswith("#")
                ):
                    break

                if row_stripped and not row_stripped.startswith("#"):
                    # Parse comma-separated values
                    values = [v.strip() for v in row_stripped.split(",")]
                    if len(values) == len(fields):
                        row_obj = {}
                        for field, value in zip(fields, values):
                            row_obj[field] = _parse_value(value)
                        array_data.append(row_obj)
                        rows_read += 1

                i += 1

            stack[-1][key] = array_data
            continue

        # Parse regular key-value pair
        if ":" in stripped:
            # Use colon as separator (preferred in TOON)
            parts = stripped.split(":", 1)
            key = parts[0].strip()
            value = parts[1].strip() if len(parts) > 1 else ""
        elif "=" in stripped:
            parts = stripped.split("=", 1)
            key = parts[0].strip()
            value = parts[1].strip() if len(parts) > 1 else ""
        else:
            i += 1
            continue

        # Check if next line has more indentation
        next_indent = _get_next_indent(lines, i)
        has_nested_content = (not value or value == "") and next_indent > indent

        if has_nested_content:
            # Check if it's an array (values without keys) or object (key-value pairs)
            next_line_idx = _get_next_line_index(lines, i)
            if next_line_idx >= 0:
                next_line = lines[next_line_idx]
                next_stripped = next_line.strip()
                # Check if next line is a key-value pair (object) or just a value (array)
                has_key_value = ":" in next_stripped or "=" in next_stripped

                if has_key_value:
                    # This is a nested object
                    new_obj = {}
                    stack[-1][key] = new_obj
                    stack.append(new_obj)
                    indent_stack.append(indent)
                    i += 1
                    continue
                else:
                    # This is an array - collect all indented values
                    array_values = []
                    j = next_line_idx
                    while j < len(lines):
                        array_line = lines[j]
                        array_indent = len(array_line) - len(array_line.lstrip())
                        array_stripped = array_line.strip()

                        # Stop if we've gone back to a lower indentation level
                        if (
                            array_indent <= indent
                            and array_stripped
                            and not array_stripped.startswith("#")
                        ):
                            break

                        if array_stripped and not array_stripped.startswith("#"):
                            # Check if it's still a value (no key-value separator)
                            if ":" not in array_stripped and "=" not in array_stripped:
                                array_values.append(_parse_value(array_stripped))
                            else:
                                # Found a key-value pair, so this is actually an object
                                break

                        j += 1

                    if array_values:
                        stack[-1][key] = array_values
                        i = j
                        continue

        # Parse value
        parsed_value = _parse_value(value) if value else None
        stack[-1][key] = parsed_value
        i += 1

    return json.dumps(result, indent=2)


def json2toon(json_content: str, indent: int = 2) -> str:
    """
    Convert JSON string to TOON format.

    Args:
        json_content: JSON string
        indent: Number of spaces for indentation (default: 2)

    Returns:
        String in TOON format
    """
    data = json.loads(json_content)
    return _dict_to_toon(data, indent=indent)


def _parse_value(value: str) -> Any:
    """Parse a value string to appropriate Python type."""
    value = value.strip()

    # Boolean values
    if value.lower() in ("true", "false"):
        return value.lower() == "true"

    # Null values
    if value.lower() in ("null", "none"):
        return None

    # Try to parse as number
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        pass

    # Remove quotes if present
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]

    # Return as string
    return value


def _get_next_indent(lines: List[str], current_index: int) -> int:
    """Get the indentation of the next non-empty, non-comment line."""
    for i in range(current_index + 1, len(lines)):
        line = lines[i]
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return len(line) - len(line.lstrip())
    return -1  # Return -1 if no next line found


def _get_next_line_index(lines: List[str], current_index: int) -> int:
    """Get the index of the next non-empty, non-comment line."""
    for i in range(current_index + 1, len(lines)):
        line = lines[i]
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return i
    return -1  # Return -1 if no next line found


def _dict_to_toon(
    data: Union[Dict, List, Any], indent: int = 2, current_indent: int = 0
) -> str:
    """Recursively convert dictionary/list to TOON format."""
    lines = []
    indent_str = " " * current_indent

    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, list) and len(value) > 0:
                # Check if all items in array are dicts with same keys (tabular format)
                if all(isinstance(item, dict) for item in value):
                    # Check if all dicts have the same keys
                    first_keys = list(value[0].keys())
                    if all(set(item.keys()) == set(first_keys) for item in value):
                        # Use tabular array format
                        fields = ",".join(first_keys)
                        lines.append(f"{indent_str}{key}[{len(value)}]{{{fields}}}:")
                        for item in value:
                            row_values = [
                                str(_format_value_for_row(item[field]))
                                for field in first_keys
                            ]
                            lines.append(
                                f"{indent_str}{' ' * indent}{','.join(row_values)}"
                            )
                        continue

                # Simple array - output as indented values
                lines.append(f"{indent_str}{key}:")
                for item in value:
                    if isinstance(item, (dict, list)):
                        lines.append(
                            _dict_to_toon(item, indent, current_indent + indent)
                        )
                    else:
                        formatted_value = _format_value(item)
                        lines.append(f"{indent_str}{' ' * indent}{formatted_value}")
                continue

            if isinstance(value, (dict, list)):
                lines.append(f"{indent_str}{key}:")
                lines.append(_dict_to_toon(value, indent, current_indent + indent))
            else:
                formatted_value = _format_value(value)
                lines.append(f"{indent_str}{key}: {formatted_value}")

    elif isinstance(data, list):
        # For top-level lists or nested lists, output each item
        for item in data:
            if isinstance(item, (dict, list)):
                lines.append(_dict_to_toon(item, indent, current_indent))
            else:
                formatted_value = _format_value(item)
                lines.append(f"{indent_str}{formatted_value}")

    else:
        formatted_value = _format_value(data)
        lines.append(f"{indent_str}{formatted_value}")

    return "\n".join(lines)


def _format_value(value: Any) -> str:
    """Format a value for TOON output."""
    if value is None:
        return "null"
    elif isinstance(value, bool):
        return str(value).lower()
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, str):
        # Only quote if necessary (contains special chars that would break parsing)
        # Spaces are OK in TOON, but colons, equals, commas, newlines, and hashes need quoting
        if any(char in value for char in [":", "=", "\n", "#", ","]):
            return json.dumps(value)
        return value
    else:
        return json.dumps(value)


def _format_value_for_row(value: Any) -> str:
    """Format a value for tabular array row (no quotes, simpler format)."""
    if value is None:
        return "null"
    elif isinstance(value, bool):
        return str(value).lower()
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, str):
        # For tabular rows, don't quote unless absolutely necessary
        if any(char in value for char in [",", "\n"]):
            return json.dumps(value)
        return value
    else:
        return json.dumps(value)
