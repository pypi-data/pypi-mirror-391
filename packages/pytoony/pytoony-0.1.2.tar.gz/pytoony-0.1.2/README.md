# PyToony 🤖

A Python package and CLI tool for converting between **TOON (Token Oriented Object Notation)** and JSON formats.

TOON is a compact, human-readable serialization format designed to reduce token usage when passing structured data to Large Language Models (LLMs). It achieves 30–60% fewer tokens compared to JSON by minimizing redundant syntax and employing indentation-based structures.

## Features

*   ✅ **Bidirectional conversion** (TOON ↔ JSON)
*   ✅ **Tabular array support** for token efficiency
*   ✅ **Nested objects** via indentation
*   ✅ **Type preservation** (strings, numbers, booleans, null)
*   ✅ **Comment support**
*   ✅ **Auto-detection** of input format
*   ✅ **CLI tool** and **Python API**
*   ✅ **90% test coverage** with 45 comprehensive tests

## Installation

### From source

```
pip install .
```

### Development mode with test dependencies

```
pip install -e ".[dev]"
```

### From PyPI (when published)

```
pip install pytoony
```

## Quick Start

### Command Line Interface

#### Convert TOON to JSON

```
# From file
pytoony input.toon -o output.json

# From stdin
cat input.toon | pytoony

# Output to stdout
pytoony input.toon
```

#### Convert JSON to TOON

```
# From file (auto-detects JSON format)
pytoony input.json -o output.toon

# Explicit conversion
pytoony input.json -o output.toon --to-toon

# From stdin
cat input.json | pytoony --to-toon

# With custom indentation
pytoony input.json -o output.toon --to-toon --indent 4
```

### Python API

```python
from pytoony import toon2json, json2toon

# Convert TOON to JSON
toon_content = """
name: John Doe
age: 30
city: New York
"""

json_output = toon2json(toon_content)
print(json_output)

# Convert JSON to TOON
json_content = '{"name": "John Doe", "age": 30, "city": "New York"}'
toon_output = json2toon(json_content)
print(toon_output)

# Using Toon class with encode/decode methods
from pytoony import Toon

# Encode JSON to TOON
json_content = '{"name": "John Doe", "age": 30}'
toon_output = Toon.encode(json_content)
print(toon_output)

# Decode TOON to JSON
toon_content = "name: John Doe\nage: 30"
json_output = Toon.decode(toon_content)
print(json_output)
```

## TOON Format

TOON (Token Oriented Object Notation) is a token-efficient serialization format with the following features:

*   **Minimal Syntax**: Eliminates unnecessary punctuation like braces and most quotes
*   **Indentation-based**: Uses indentation for nested structures (similar to YAML)
*   **Tabular Arrays**: Declares keys once for uniform arrays, streaming data as rows
*   **Comments**: Lines starting with `#` are comments
*   **Key-value pairs**: Separated by `:` or `=`

### Tabular Array Format

The most token-efficient feature of TOON is the tabular array format. Instead of repeating keys for each object in an array, TOON declares the structure once:

**TOON:**

```
users[2]{id,name,role}:
  1,Alice,admin
  2,Bob,user
```

**JSON equivalent:**

```
{
  "users": [
    { "id": 1, "name": "Alice", "role": "admin" },
    { "id": 2, "name": "Bob", "role": "user" }
  ]
}
```

The TOON version uses significantly fewer tokens while remaining human-readable.

### Complete Example

```
# This is a comment
name: John Doe
age: 30
email: john.doe@example.com
active: true

# Nested object
address:
  street: 123 Main Street
  city: New York
  state: NY
  zipcode: 10001

# Tabular array (token-efficient)
users[3]{id,name,role,active}:
  1,Alice,admin,true
  2,Bob,user,false
  3,Charlie,moderator,true

# Simple array
tags:
  python
  json
  converter
  toon
```

Converts to:

```
{
  "name": "John Doe",
  "age": 30,
  "email": "john.doe@example.com",
  "active": true,
  "address": {
    "street": "123 Main Street",
    "city": "New York",
    "state": "NY",
    "zipcode": 10001
  },
  "users": [
    { "id": 1, "name": "Alice", "role": "admin", "active": true },
    { "id": 2, "name": "Bob", "role": "user", "active": false },
    { "id": 3, "name": "Charlie", "role": "moderator", "active": true }
  ],
  "tags": [
    "python",
    "json",
    "converter",
    "toon"
  ]
}
```

## Testing

The project includes comprehensive test coverage (90% overall):

*   **45 tests** covering all major functionality
*   **21 tests** for converter functions
*   **20 tests** for CLI interface

### Run Tests

```
# Install test dependencies first
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage (terminal report)
pytest --cov=pytoony --cov-report=term

# Run with coverage (detailed terminal report)
pytest --cov=pytoony --cov-report=term-missing

# Run with coverage (HTML report)
pytest --cov=pytoony --cov-report=html

# View coverage percentage only
pytest --cov=pytoony --cov-report=term-missing --quiet
```

After running with HTML report, open `htmlcov/index.html` in your browser to see detailed coverage information.

## Project Structure

```
pytoony/
├── pytoony/                  # Main package
│   ├── __init__.py
│   ├── converter.py         # Core conversion logic
│   ├── toon.py              # Toon class
│   └── cli.py               # Command-line interface
├── tests/                   # Test suite
│   ├── test_converter.py    # Converter tests
│   └── test_cli.py          # CLI tests
├── examples/                # Example files
│   ├── example.toon
│   ├── example.json
│   ├── array-example.toon
│   └── array-example.json
├── setup.py                 # Package setup
├── pyproject.toml           # Modern Python packaging
└── README.md
```

## Development

### Setup Development Environment

```
# Clone the repository
git clone https://github.com/puchkoff/pytoony
cd pytoony

# Install in development mode
pip install -e ".[dev]"
```

### Running Tests

```
# Run all tests
pytest

# Run specific test file
pytest tests/test_converter.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=pytoony --cov-report=html
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

Have a good day! 😊
