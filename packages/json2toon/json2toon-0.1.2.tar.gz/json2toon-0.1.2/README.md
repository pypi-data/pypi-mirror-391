# json2toon

[![PyPI version](https://badge.fury.io/py/json2toon.svg)](https://badge.fury.io/py/json2toon)
[![Python Version](https://img.shields.io/pypi/pyversions/json2toon.svg)](https://pypi.org/project/json2toon/)
[![CI](https://github.com/maqboolthoufeeq/json2toon/actions/workflows/ci.yml/badge.svg)](https://github.com/maqboolthoufeeq/json2toon/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/json2toon)](https://pepy.tech/project/json2toon)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A Python library and CLI tool for bidirectional conversion between JSON and TOON (Token-Oriented Object Notation) format with full specification support.

## What is TOON?

TOON (Token-Oriented Object Notation) is a compact, human-readable serialization format designed specifically for passing structured data to Large Language Models (LLMs). It achieves 30-60% fewer tokens than formatted JSON on large uniform arrays while maintaining lossless conversion.

**Key features of TOON:**
- CSV-like compactness with explicit structure
- Indentation-based syntax (like YAML)
- Tabular formatting for uniform data
- Optimized for LLM token efficiency

Learn more: [TOON Format Specification](https://github.com/toon-format/toon)

## Features

- **Full TOON Spec Support**: Complete implementation of the TOON specification
- **Bidirectional Conversion**: Convert JSON to TOON and TOON back to JSON
- **Tabular Array Detection**: Automatically detects and formats uniform arrays efficiently
- **Custom Delimiters**: Support for comma, tab, and pipe delimiters
- **Key Folding**: Optional collapsing of single-key object chains
- **Path Expansion**: Optional expansion of dotted keys into nested objects
- **Strict Mode**: Validation for array counts, indentation, and structure
- **CLI Tools**: Command-line utilities for easy conversion
- **Type Safe**: Full type hints for better IDE support

## Installation

Install using `uv`:

```bash
uv add json2toon
```

Or using `pip`:

```bash
pip install json2toon
```

## Quick Start

### Python API

```python
from json2toon import json_to_toon, toon_to_json

# Convert JSON to TOON
data = {
    "users": [
        {"id": 1, "name": "Alice", "role": "admin"},
        {"id": 2, "name": "Bob", "role": "user"}
    ]
}

toon_string = json_to_toon(data)
print(toon_string)
# Output:
# users[2]{id,name,role}:
#   1,Alice,admin
#   2,Bob,user

# Convert TOON back to JSON
json_data = toon_to_json(toon_string)
print(json_data)  # Original data restored
```

### CLI Usage

Convert JSON to TOON:

```bash
# From file
json2toon input.json -o output.toon

# From stdin
cat data.json | json2toon

# With options
json2toon input.json --indent 4 --delimiter tab
```

Convert TOON to JSON:

```bash
# From file
toon2json input.toon -o output.json

# From stdin
cat data.toon | toon2json

# With pretty formatting
toon2json input.toon --pretty
```

## Advanced Usage

### Configuration Options

```python
from json2toon import json_to_toon, ToonConfig

config = ToonConfig(
    indent_size=4,              # Indentation spaces (default: 2)
    delimiter="\t",             # Delimiter: ",", "\t", or "|" (default: ",")
    key_folding="safe",         # Collapse single-key chains (default: None)
    strict=True,                # Enable strict validation (default: True)
)

toon_string = json_to_toon(data, config=config)
```

### Parsing Options

```python
from json2toon import toon_to_json, ToonParseConfig

config = ToonParseConfig(
    expand_paths="safe",        # Expand dotted keys (default: None)
    strict=True,                # Strict mode validation (default: True)
)

json_data = toon_to_json(toon_string, config=config)
```

## Examples

### Simple Object

**JSON:**
```json
{
  "id": 123,
  "name": "Ada"
}
```

**TOON:**
```
id: 123
name: Ada
```

### Nested Object

**JSON:**
```json
{
  "user": {
    "id": 1,
    "name": "Bob"
  }
}
```

**TOON:**
```
user:
  id: 1
  name: Bob
```

### Tabular Arrays (Most Efficient)

**JSON:**
```json
{
  "products": [
    {"id": 1, "name": "Laptop", "price": 999.99},
    {"id": 2, "name": "Mouse", "price": 29.99}
  ]
}
```

**TOON:**
```
products[2]{id,name,price}:
  1,Laptop,999.99
  2,Mouse,29.99
```

### Primitive Arrays

**JSON:**
```json
{
  "tags": ["admin", "ops", "dev"]
}
```

**TOON:**
```
tags[3]: admin,ops,dev
```

## CLI Options

### json2toon

```
usage: json2toon [-h] [-o OUTPUT] [--indent SIZE] [--delimiter DELIM]
                 [--key-folding MODE] [--no-strict]
                 [input]

Convert JSON to TOON format

positional arguments:
  input                 Input JSON file (default: stdin)

options:
  -h, --help            Show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output TOON file (default: stdout)
  --indent SIZE         Indentation size (default: 2)
  --delimiter DELIM     Delimiter: comma, tab, or pipe (default: comma)
  --key-folding MODE    Key folding mode: safe (default: none)
  --no-strict           Disable strict mode validation
```

### toon2json

```
usage: toon2json [-h] [-o OUTPUT] [--expand-paths MODE] [--no-strict]
                 [--pretty]
                 [input]

Convert TOON to JSON format

positional arguments:
  input                 Input TOON file (default: stdin)

options:
  -h, --help            Show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output JSON file (default: stdout)
  --expand-paths MODE   Path expansion mode: safe (default: none)
  --no-strict           Disable strict mode validation
  --pretty              Pretty-print JSON output
```

## Development

Install development dependencies:

```bash
uv sync --dev
```

Run tests:

```bash
uv run pytest
```

Run type checking:

```bash
uv run mypy src/json2toon
```

Run linting:

```bash
uv run ruff check src/json2toon
```

Format code:

```bash
uv run ruff format src/json2toon
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [TOON Format Specification](https://github.com/toon-format/toon) - The official TOON format specification
- Thanks to the TOON format creators for designing an efficient LLM-optimized format

## Links

- **GitHub**: https://github.com/maqboolthoufeeq/json2toon
- **PyPI**: https://pypi.org/project/json2toon/
- **Issues**: https://github.com/maqboolthoufeeq/json2toon/issues
- **TOON Spec**: https://github.com/toon-format/spec
