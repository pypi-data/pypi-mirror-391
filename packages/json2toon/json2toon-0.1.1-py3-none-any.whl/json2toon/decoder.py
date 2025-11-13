"""TOON to JSON decoder with full specification support."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

__all__ = ["ToonDecoder", "ToonParseConfig", "ToonParseError"]


class ToonParseError(Exception):
    """Exception raised when TOON parsing fails."""

    pass


@dataclass
class ToonParseConfig:
    """Configuration options for TOON parsing."""

    expand_paths: str | None = None  # "safe" or None
    strict: bool = True
    indent_size: int = 2


class ToonDecoder:
    """Decodes TOON format to Python objects."""

    def __init__(self, config: ToonParseConfig | None = None) -> None:
        """Initialize the decoder with optional configuration."""
        self.config = config or ToonParseConfig()
        self.lines: list[str] = []
        self.current_line = 0

    def decode(self, toon_string: str) -> Any:  # noqa: ANN401
        """Decode TOON format string to Python object."""
        if not toon_string.strip():
            return {}  # Empty document is empty object

        self.lines = toon_string.split("\n")
        self.current_line = 0

        # Discover root form
        root_form = self._discover_root_form()

        if root_form == "array":
            return self._parse_root_array()
        if root_form == "primitive":
            return self._parse_primitive(self.lines[0].strip())

        # Default: object
        return self._parse_object(0)

    def _discover_root_form(self) -> str:
        """Discover the root form (object, array, or primitive)."""
        # Find first non-empty depth-0 line
        for line in self.lines:
            stripped = line.strip()
            if not stripped:
                continue

            # Check indentation
            depth = self._get_depth(line)
            if depth > 0:
                continue

            # Check if it's a ROOT array header (starts with bracket, no key)
            if stripped.startswith("[") and self._is_array_header(stripped):
                return "array"

            # Check if it's a single primitive (no key-value structure)
            if ":" not in stripped or not self._has_unquoted_colon(stripped):
                return "primitive"

            # It's an object
            return "object"

        return "object"  # Empty or all indented

    def _parse_root_array(self) -> list[Any]:
        """Parse root-level array."""
        first_line = self._get_next_nonempty_line()
        if first_line is None:
            return []

        header_match = self._parse_array_header(first_line)
        if not header_match:
            msg = f"Expected array header, got: {first_line}"
            raise ToonParseError(msg)

        length, delimiter, fields = header_match

        if fields:
            # Tabular array
            return self._parse_tabular_array(0, length, delimiter or ",", fields)

        # Check next line to determine format
        self.current_line += 1
        return self._parse_array_items(0, length, delimiter or ",")

    def _parse_object(self, depth: int) -> dict[str, Any]:
        """Parse an object at given depth."""
        obj: dict[str, Any] = {}

        while self.current_line < len(self.lines):
            line = self.lines[self.current_line]

            # Skip empty lines outside arrays
            if not line.strip():
                self.current_line += 1
                continue

            line_depth = self._get_depth(line)

            # If less indented, we're done with this object
            if line_depth < depth:
                break

            # If more indented, skip (handled by parent)
            if line_depth > depth:
                self.current_line += 1
                continue

            # Parse this line
            stripped = line.strip()

            # Check for key-value or key-with-nested
            if ":" in stripped:
                key, value = self._parse_key_value(stripped, depth)

                # Handle path expansion
                if self.config.expand_paths == "safe" and "." in key:
                    self._expand_path_into_object(obj, key, value)
                else:
                    obj[key] = value
            else:
                # No colon means something is wrong
                self.current_line += 1
                continue

        return obj

    def _parse_key_value(self, line: str, depth: int) -> tuple[str, Any]:
        """Parse a key-value line."""
        # Find the first unquoted colon
        colon_pos = self._find_unquoted_colon(line)
        if colon_pos == -1:
            msg = f"Expected colon in line: {line}"
            raise ToonParseError(msg)

        key_part = line[:colon_pos].strip()
        value_part = line[colon_pos + 1 :].strip()

        # Parse key (may be quoted)
        key = self._parse_key(key_part)

        # Check if it's an array
        if "[" in key_part and "]" in key_part:
            # Array value
            array_match = self._parse_array_header(line)
            if array_match:
                # Extract key before bracket
                bracket_pos = key_part.index("[")
                key = key_part[:bracket_pos].strip()

                length, delimiter, fields = array_match
                self.current_line += 1

                if fields:
                    # Tabular array
                    value = self._parse_tabular_array(depth + 1, length, delimiter or ",", fields)
                elif not value_part:
                    # Items below
                    value = self._parse_array_items(depth + 1, length, delimiter or ",")
                else:
                    # Inline primitive array
                    value = self._parse_inline_array(value_part, delimiter or ",", length)
                return key, value

        # Check if value is empty (nested object/array below)
        if not value_part:
            self.current_line += 1
            # Peek next line to determine type
            if self.current_line < len(self.lines):
                next_line = self.lines[self.current_line]
                next_depth = self._get_depth(next_line)

                if next_depth > depth:
                    # Nested content
                    if next_line.strip().startswith("-"):
                        # Array items
                        value = self._parse_list_items(depth + 1)
                    else:
                        # Nested object
                        value = self._parse_object(depth + 1)
                else:
                    value = None
            else:
                value = None
        else:
            # Inline value
            value = self._parse_primitive(value_part)
            self.current_line += 1

        return key, value

    def _parse_array_items(self, depth: int, expected_length: int, delimiter: str) -> list[Any]:
        """Parse array items (list format with dashes)."""
        items: list[Any] = []

        while self.current_line < len(self.lines):
            line = self.lines[self.current_line]

            if not line.strip():
                if self.config.strict:
                    msg = "Blank lines not allowed inside arrays in strict mode"
                    raise ToonParseError(msg)
                self.current_line += 1
                continue

            line_depth = self._get_depth(line)
            if line_depth < depth:
                break

            if line_depth > depth:
                self.current_line += 1
                continue

            stripped = line.strip()

            if stripped.startswith("- "):
                # List item with content on same line
                content = stripped[2:].strip()

                if ":" in content:
                    # Object or nested
                    colon_pos = self._find_unquoted_colon(content)
                    key_part = content[:colon_pos].strip()
                    value_part = content[colon_pos + 1 :].strip()

                    # Start building object
                    obj: dict[str, Any] = {}
                    key = self._parse_key(key_part)

                    if not value_part:
                        # Nested value below
                        self.current_line += 1
                        if self.current_line < len(self.lines):
                            next_depth = self._get_depth(self.lines[self.current_line])
                            if next_depth > depth:
                                obj[key] = self._parse_value_at_depth(depth + 1)
                            else:
                                obj[key] = None
                    else:
                        obj[key] = self._parse_primitive(value_part)
                        self.current_line += 1

                    # Check for more fields
                    while self.current_line < len(self.lines):
                        line2 = self.lines[self.current_line]
                        line2_depth = self._get_depth(line2)

                        if line2_depth < depth + 1:
                            break
                        if line2_depth > depth + 1:
                            self.current_line += 1
                            continue

                        stripped2 = line2.strip()
                        if stripped2.startswith("-"):
                            break

                        # Additional field
                        if ":" in stripped2:
                            k2, v2 = self._parse_key_value(stripped2, depth + 1)
                            obj[k2] = v2
                        else:
                            self.current_line += 1

                    items.append(obj)
                else:
                    # Primitive item
                    items.append(self._parse_primitive(content))
                    self.current_line += 1
            elif stripped == "-":
                # Empty object or standalone dash
                self.current_line += 1

                # Check if there are nested fields
                if self.current_line < len(self.lines):
                    next_line = self.lines[self.current_line]
                    next_depth = self._get_depth(next_line)

                    if next_depth > depth and not next_line.strip().startswith("-"):
                        # It's an object with nested fields
                        obj = self._parse_object(depth + 1)
                        items.append(obj)
                    else:
                        # Empty object
                        items.append({})
                else:
                    items.append({})
            else:
                # Something else, break
                break

        # Validate count
        if self.config.strict and len(items) != expected_length:
            msg = f"Array count mismatch: expected {expected_length}, got {len(items)}"
            raise ToonParseError(msg)

        return items

    def _parse_list_items(self, depth: int) -> list[Any]:
        """Parse list items without known length."""
        items: list[Any] = []

        while self.current_line < len(self.lines):
            line = self.lines[self.current_line]

            if not line.strip():
                self.current_line += 1
                continue

            line_depth = self._get_depth(line)
            if line_depth < depth:
                break

            if line_depth > depth:
                self.current_line += 1
                continue

            stripped = line.strip()

            if stripped.startswith("- ") or stripped == "-":
                # Parse item similar to above
                if stripped == "-":
                    self.current_line += 1
                    items.append({})
                else:
                    content = stripped[2:].strip()
                    items.append(self._parse_primitive(content))
                    self.current_line += 1
            else:
                break

        return items

    def _parse_value_at_depth(self, depth: int) -> Any:  # noqa: ANN401
        """Parse a value starting at given depth."""
        if self.current_line >= len(self.lines):
            return None

        line = self.lines[self.current_line]
        stripped = line.strip()

        if stripped.startswith("-"):
            return self._parse_list_items(depth)

        return self._parse_object(depth)

    def _parse_tabular_array(
        self, depth: int, expected_length: int, delimiter: str, fields: list[str]
    ) -> list[dict[str, Any]]:
        """Parse tabular array format."""
        rows: list[dict[str, Any]] = []

        while self.current_line < len(self.lines):
            line = self.lines[self.current_line]

            if not line.strip():
                if self.config.strict:
                    msg = "Blank lines not allowed inside tabular arrays in strict mode"
                    raise ToonParseError(msg)
                self.current_line += 1
                continue

            line_depth = self._get_depth(line)
            if line_depth < depth:
                break

            if line_depth > depth:
                self.current_line += 1
                continue

            stripped = line.strip()

            # Check if it's a row (has delimiter before any colon)
            if self._is_tabular_row(stripped, delimiter):
                # Parse row
                values = self._split_by_delimiter(stripped, delimiter)

                if self.config.strict and len(values) != len(fields):
                    msg = f"Row width mismatch: expected {len(fields)}, got {len(values)}"
                    raise ToonParseError(msg)

                row = {
                    field: self._parse_primitive(val)
                    for field, val in zip(fields, values, strict=True)
                }
                rows.append(row)
                self.current_line += 1
            else:
                # End of rows
                break

        # Validate count
        if self.config.strict and len(rows) != expected_length:
            msg = f"Array count mismatch: expected {expected_length}, got {len(rows)}"
            raise ToonParseError(msg)

        return rows

    def _parse_inline_array(self, content: str, delimiter: str, expected_length: int) -> list[Any]:
        """Parse inline primitive array."""
        values = self._split_by_delimiter(content, delimiter)

        if self.config.strict and len(values) != expected_length:
            msg = f"Array count mismatch: expected {expected_length}, got {len(values)}"
            raise ToonParseError(msg)

        return [self._parse_primitive(v) for v in values]

    def _parse_array_header(self, line: str) -> tuple[int, str | None, list[str] | None] | None:
        """Parse array header and return (length, delimiter, fields)."""
        # Pattern: [N] or [N<delim>] or [N]{fields} or [N<delim>]{fields}
        match = re.search(r"\[(\d+)([\t|])?\](?:\{([^}]+)\})?:", line)
        if not match:
            return None

        length = int(match.group(1))
        delimiter = match.group(2)  # Can be \t or | or None
        fields_str = match.group(3)

        fields = None
        if fields_str:
            # Parse fields (using the delimiter if specified, else comma)
            field_delim = delimiter if delimiter else ","
            fields = [f.strip() for f in fields_str.split(field_delim)]

        return length, delimiter, fields

    def _parse_primitive(self, value: str) -> Any:  # noqa: ANN401
        """Parse and type a primitive value."""
        value = value.strip()

        # Handle quoted strings
        if value.startswith('"') and value.endswith('"'):
            return self._unescape_string(value[1:-1])

        # Handle literals
        if value == "null":
            return None
        if value == "true":
            return True
        if value == "false":
            return False

        # Try to parse as number
        try:
            if "." in value or "e" in value.lower():
                return float(value)
            return int(value)
        except ValueError:
            # It's a string
            return value

    def _unescape_string(self, s: str) -> str:
        """Unescape a quoted string."""
        s = s.replace("\\n", "\n")
        s = s.replace("\\r", "\r")
        s = s.replace("\\t", "\t")
        s = s.replace('\\"', '"')
        s = s.replace("\\\\", "\\")
        return s

    def _parse_key(self, key_str: str) -> str:
        """Parse a key (may be quoted)."""
        key_str = key_str.strip()
        if key_str.startswith('"') and key_str.endswith('"'):
            return self._unescape_string(key_str[1:-1])
        return key_str

    def _split_by_delimiter(self, line: str, delimiter: str) -> list[str]:
        """Split line by delimiter, respecting quoted strings."""
        values: list[str] = []
        current = ""
        in_quotes = False
        escaped = False

        for char in line:
            if escaped:
                current += char
                escaped = False
            elif char == "\\":
                current += char
                escaped = True
            elif char == '"':
                current += char
                in_quotes = not in_quotes
            elif char == delimiter and not in_quotes:
                values.append(current.strip())
                current = ""
            else:
                current += char

        if current:
            values.append(current.strip())

        return values

    def _is_tabular_row(self, line: str, delimiter: str) -> bool:
        """Check if line is a tabular row (has delimiter before colon)."""
        # Find first unquoted delimiter and first unquoted colon
        delim_pos = self._find_unquoted_char(line, delimiter)
        colon_pos = self._find_unquoted_colon(line)

        # No colon means it's a row
        if colon_pos == -1:
            return True

        # No delimiter means it's not a row
        if delim_pos == -1:
            return False

        # Delimiter before colon means it's a row
        return delim_pos < colon_pos

    def _find_unquoted_colon(self, line: str) -> int:
        """Find position of first unquoted colon."""
        return self._find_unquoted_char(line, ":")

    def _find_unquoted_char(self, line: str, char: str) -> int:
        """Find position of first unquoted character."""
        in_quotes = False
        escaped = False

        for i, c in enumerate(line):
            if escaped:
                escaped = False
                continue

            if c == "\\":
                escaped = True
                continue

            if c == '"':
                in_quotes = not in_quotes
                continue

            if c == char and not in_quotes:
                return i

        return -1

    def _has_unquoted_colon(self, line: str) -> bool:
        """Check if line has an unquoted colon."""
        return self._find_unquoted_colon(line) != -1

    def _is_array_header(self, line: str) -> bool:
        """Check if line is an array header."""
        return bool(re.search(r"\[\d+[\t|]?\](?:\{[^}]+\})?:", line))

    def _get_depth(self, line: str) -> int:
        """Get indentation depth of a line."""
        if not line or line[0] not in (" ", "\t"):
            return 0

        spaces = len(line) - len(line.lstrip(" "))

        # Strict mode: check for tabs
        if self.config.strict and "\t" in line[:spaces]:
            msg = "Tabs not allowed in indentation in strict mode"
            raise ToonParseError(msg)

        # Strict mode: check spaces are multiple of indent_size
        if self.config.strict and spaces % self.config.indent_size != 0:
            msg = f"Indentation must be multiple of {self.config.indent_size}"
            raise ToonParseError(msg)

        return spaces // self.config.indent_size

    def _get_next_nonempty_line(self) -> str | None:
        """Get next non-empty line."""
        while self.current_line < len(self.lines):
            line = self.lines[self.current_line]
            if line.strip():
                return line.strip()
            self.current_line += 1
        return None

    def _expand_path_into_object(self, obj: dict[str, Any], path: str, value: Any) -> None:  # noqa: ANN401
        """Expand dotted path into nested object."""
        if self.config.expand_paths != "safe":
            obj[path] = value
            return

        # Split path and validate
        parts = path.split(".")

        # Check all parts are valid identifiers
        if not all(re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", p) for p in parts):
            obj[path] = value
            return

        # Expand
        current = obj
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            elif not isinstance(current[part], dict):
                # Conflict: last write wins if not strict
                if self.config.strict:
                    msg = f"Path expansion conflict at {part}"
                    raise ToonParseError(msg)
                current[part] = {}

            current = current[part]

        current[parts[-1]] = value


def toon_to_json(toon_string: str, config: ToonParseConfig | None = None) -> Any:  # noqa: ANN401
    """Convert TOON format string to Python object (JSON-compatible).

    Args:
        toon_string: TOON format string to decode
        config: Optional parsing configuration

    Returns:
        Python object (dict, list, or primitive)
    """
    decoder = ToonDecoder(config)
    return decoder.decode(toon_string)
