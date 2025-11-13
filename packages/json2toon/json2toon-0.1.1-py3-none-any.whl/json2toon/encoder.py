"""JSON to TOON encoder with full specification support."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Any

__all__ = ["ToonEncoder", "ToonConfig"]


@dataclass
class ToonConfig:
    """Configuration options for TOON encoding."""

    indent_size: int = 2
    delimiter: str = ","
    key_folding: str | None = None  # "safe" or None
    strict: bool = True


class ToonEncoder:
    """Encodes Python objects to TOON format."""

    def __init__(self, config: ToonConfig | None = None) -> None:
        """Initialize the encoder with optional configuration."""
        self.config = config or ToonConfig()
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate configuration options."""
        if self.config.delimiter not in (",", "\t", "|"):
            msg = f"Invalid delimiter: {self.config.delimiter!r}"
            raise ValueError(msg)
        if self.config.key_folding not in (None, "safe"):
            msg = f"Invalid key_folding: {self.config.key_folding!r}"
            raise ValueError(msg)
        if self.config.indent_size < 1:
            msg = f"Invalid indent_size: {self.config.indent_size}"
            raise ValueError(msg)

    def encode(self, data: Any) -> str:  # noqa: ANN401
        """Encode Python data to TOON format string."""
        lines = self._encode_value(data, depth=0, is_root=True)
        return "\n".join(lines) if lines else ""

    def _encode_value(
        self,
        value: Any,
        depth: int,
        is_root: bool = False,
        key: str | None = None,  # noqa: ANN401
    ) -> list[str]:
        """Encode a value at a given depth."""
        if value is None or (isinstance(value, float) and (math.isnan(value) or math.isinf(value))):
            return [f"{self._indent(depth)}{key}: null"] if key else ["null"]

        if isinstance(value, bool):
            bool_str = "true" if value else "false"
            return [f"{self._indent(depth)}{key}: {bool_str}"] if key else [bool_str]

        if isinstance(value, (int, float)):
            num_str = self._canonicalize_number(value)
            return [f"{self._indent(depth)}{key}: {num_str}"] if key else [num_str]

        if isinstance(value, str):
            quoted = self._quote_string(value, self.config.delimiter)
            return [f"{self._indent(depth)}{key}: {quoted}"] if key else [quoted]

        if isinstance(value, list):
            return self._encode_array(value, depth, key, is_root)

        if isinstance(value, dict):
            return self._encode_object(value, depth, key, is_root)

        # Fallback for unsupported types
        return self._encode_value(str(value), depth, is_root, key)

    def _encode_object(
        self, obj: dict[str, Any], depth: int, parent_key: str | None, is_root: bool
    ) -> list[str]:
        """Encode a dictionary object."""
        if not obj:  # Empty object
            return [] if is_root else [f"{self._indent(depth)}{parent_key}:"] if parent_key else []

        lines: list[str] = []

        # Add parent key if not root
        if parent_key and not is_root:
            lines.append(f"{self._indent(depth)}{parent_key}:")
            depth += 1

        # Apply key folding if enabled
        if self.config.key_folding == "safe" and len(obj) == 1:
            single_key = next(iter(obj))
            single_value = obj[single_key]

            # Check if we can fold
            if (
                isinstance(single_value, dict)
                and self._is_valid_identifier(single_key)
                and "." not in single_key
            ):
                # Recursively fold
                folded_key = single_key
                current_value = single_value

                while isinstance(current_value, dict) and len(current_value) == 1:
                    next_key = next(iter(current_value))
                    if not self._is_valid_identifier(next_key) or "." in next_key:
                        break
                    folded_key = f"{folded_key}.{next_key}"
                    current_value = current_value[next_key]

                # Encode with folded key
                child_lines = self._encode_value(current_value, depth, key=folded_key)
                lines.extend(child_lines)
                return lines

        # Normal object encoding
        for k, v in obj.items():
            if not self._is_valid_unquoted_key(k):
                # Quote the key if it's not valid
                k = self._quote_string(k, self.config.delimiter)

            child_lines = self._encode_value(v, depth, key=k)
            lines.extend(child_lines)

        return lines

    def _encode_array(
        self, arr: list[Any], depth: int, key: str | None, is_root: bool
    ) -> list[str]:
        """Encode an array with appropriate format."""
        if not arr:  # Empty array
            header = "[0]:"
            if key:
                header = f"{key}{header}"
            if not is_root:
                header = f"{self._indent(depth)}{header}"
            return [header]

        # Detect array format
        if self._is_tabular_array(arr):
            return self._encode_tabular_array(arr, depth, key, is_root)
        if self._is_primitive_array(arr):
            return self._encode_primitive_array(arr, depth, key, is_root)
        if self._is_nested_array(arr):
            return self._encode_nested_array(arr, depth, key, is_root)

        # Mixed/non-uniform array
        return self._encode_mixed_array(arr, depth, key, is_root)

    def _is_tabular_array(self, arr: list[Any]) -> bool:
        """Check if array should be encoded in tabular format."""
        if not arr or not all(isinstance(item, dict) for item in arr):
            return False

        # Get keys from first object
        first_keys = set(arr[0].keys())

        # Check all objects have same keys and all values are primitives
        for item in arr:
            if set(item.keys()) != first_keys:
                return False
            if not all(self._is_primitive(v) for v in item.values()):
                return False

        return True

    def _is_primitive_array(self, arr: list[Any]) -> bool:
        """Check if array contains only primitives."""
        return all(self._is_primitive(item) for item in arr)

    def _is_nested_array(self, arr: list[Any]) -> bool:
        """Check if array contains only arrays."""
        return all(isinstance(item, list) for item in arr)

    def _is_primitive(self, value: Any) -> bool:  # noqa: ANN401
        """Check if value is a primitive type."""
        return value is None or isinstance(value, (bool, int, float, str))

    def _encode_tabular_array(
        self, arr: list[dict[str, Any]], depth: int, key: str | None, is_root: bool
    ) -> list[str]:
        """Encode uniform array of objects in tabular format."""
        lines: list[str] = []

        # Get field names from first object (preserve order)
        fields = list(arr[0].keys())
        field_names = self.config.delimiter.join(fields)

        # Build header
        delim_marker = ""
        if self.config.delimiter == "\t":
            delim_marker = "\t"
        elif self.config.delimiter == "|":
            delim_marker = "|"

        header = f"[{len(arr)}{delim_marker}]{{{field_names}}}:"

        if key:
            header = f"{key}{header}"
        if not is_root:
            header = f"{self._indent(depth)}{header}"

        lines.append(header)

        # Encode rows
        row_depth = depth + 1 if not is_root or key else depth
        for obj in arr:
            encoded_values = []
            for f in fields:
                val = obj[f]
                # Only quote actual string values, not primitives converted to strings
                if isinstance(val, str):
                    # Original value is a string, quote if necessary
                    if self._needs_quoting(val, self.config.delimiter):
                        encoded_values.append(self._quote_string(val, self.config.delimiter))
                    else:
                        encoded_values.append(val)
                else:
                    # Original value is number/bool/null, convert to string but don't quote
                    normalized = self._normalize_value(val)
                    encoded_values.append(str(normalized))
            row = self.config.delimiter.join(encoded_values)
            lines.append(f"{self._indent(row_depth)}{row}")

        return lines

    def _encode_primitive_array(
        self, arr: list[Any], depth: int, key: str | None, is_root: bool
    ) -> list[str]:
        """Encode array of primitives inline."""
        encoded_values = []
        for v in arr:
            # Only quote actual string values, not primitives converted to strings
            if isinstance(v, str):
                # Original value is a string, quote if necessary
                if self._needs_quoting(v, self.config.delimiter):
                    encoded_values.append(self._quote_string(v, self.config.delimiter))
                else:
                    encoded_values.append(v)
            else:
                # Original value is number/bool/null, convert to string but don't quote
                normalized = self._normalize_value(v)
                encoded_values.append(str(normalized))
        content = self.config.delimiter.join(encoded_values)

        header = f"[{len(arr)}]: {content}"
        if key:
            header = f"{key}{header}"
        if not is_root:
            header = f"{self._indent(depth)}{header}"

        return [header]

    def _encode_nested_array(
        self, arr: list[list[Any]], depth: int, key: str | None, is_root: bool
    ) -> list[str]:
        """Encode array of arrays."""
        lines: list[str] = []

        header = f"[{len(arr)}]:"
        if key:
            header = f"{key}{header}"
        if not is_root:
            header = f"{self._indent(depth)}{header}"

        lines.append(header)

        # Encode each nested array
        item_depth = depth + 1 if not is_root or key else depth
        for item in arr:
            # Each nested array as a list item
            item_lines = self._encode_value(item, item_depth, key="-")
            lines.extend(item_lines)

        return lines

    def _encode_mixed_array(
        self, arr: list[Any], depth: int, key: str | None, is_root: bool
    ) -> list[str]:
        """Encode mixed/non-uniform array."""
        lines: list[str] = []

        header = f"[{len(arr)}]:"
        if key:
            header = f"{key}{header}"
        if not is_root:
            header = f"{self._indent(depth)}{header}"

        lines.append(header)

        # Encode each item as list item
        item_depth = depth + 1 if not is_root or key else depth
        for item in arr:
            if isinstance(item, dict):
                if not item:  # Empty object
                    lines.append(f"{self._indent(item_depth)}-")
                else:
                    # First field on hyphen line, rest indented
                    first_key = next(iter(item))
                    first_value = item[first_key]

                    # Encode first field on hyphen line
                    if isinstance(first_value, (dict, list)):
                        lines.append(f"{self._indent(item_depth)}- {first_key}:")
                        child_lines = self._encode_value(first_value, item_depth + 1)
                        lines.extend(child_lines)
                    else:
                        val_str = self._encode_value(first_value, 0)[0]
                        lines.append(f"{self._indent(item_depth)}- {first_key}: {val_str}")

                    # Remaining fields
                    for k, v in list(item.items())[1:]:
                        child_lines = self._encode_value(v, item_depth + 1, key=k)
                        lines.extend(child_lines)
            else:
                # Primitive or array as list item
                item_lines = self._encode_value(item, item_depth, key="-")
                lines.extend(item_lines)

        return lines

    def _normalize_value(self, value: Any) -> Any:  # noqa: ANN401
        """Normalize a value for encoding."""
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, (int, float)):
            return self._canonicalize_number(value)
        return value

    def _canonicalize_number(self, num: int | float) -> str:
        """Canonicalize a number per TOON spec."""
        if isinstance(num, bool):
            return "true" if num else "false"

        if math.isnan(num) or math.isinf(num):
            return "null"

        # Convert to decimal (no exponent)
        if isinstance(num, float):
            if num == int(num):
                return str(int(num))
            # Format with sufficient precision
            return f"{num:f}".rstrip("0").rstrip(".")

        return str(num)

    def _quote_string(self, s: str, delimiter: str) -> str:
        """Quote a string if necessary."""
        if self._needs_quoting(s, delimiter):
            # Escape special characters
            escaped = s.replace("\\", "\\\\").replace('"', '\\"')
            escaped = escaped.replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")
            return f'"{escaped}"'
        return s

    def _needs_quoting(self, s: str, delimiter: str) -> bool:
        """Check if a string needs quoting."""
        if not s:  # Empty string
            return True

        if s != s.strip():  # Leading/trailing whitespace
            return True

        if s in ("true", "false", "null"):
            return True

        # Numeric-like
        if re.match(r"^-?\d+(?:\.\d+)?(?:e[+-]?\d+)?$", s, re.IGNORECASE):
            return True
        if re.match(r"^0\d+$", s):  # Leading zeros
            return True

        # Special characters
        if any(c in s for c in (":", '"', "\\", "[", "]", "{", "}")):
            return True

        # Control characters
        if any(ord(c) < 32 for c in s):
            return True

        # Contains delimiter
        if delimiter in s:
            return True

        # Starts with dash or equals dash
        return s == "-" or s.startswith("- ")

    def _is_safe_unquoted(self, value: Any, delimiter: str) -> bool:  # noqa: ANN401
        """Check if a value can be encoded unquoted."""
        if not isinstance(value, str):
            return True  # Numbers, booleans, null are always safe
        return not self._needs_quoting(value, delimiter)

    def _is_valid_unquoted_key(self, key: str) -> bool:
        """Check if key is valid unquoted identifier."""
        return bool(re.match(r"^[A-Za-z_][A-Za-z0-9_.]*$", key))

    def _is_valid_identifier(self, key: str) -> bool:
        """Check if key is valid identifier (no dots)."""
        return bool(re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", key))

    def _indent(self, depth: int) -> str:
        """Generate indentation for given depth."""
        return " " * (depth * self.config.indent_size)


def json_to_toon(data: Any, config: ToonConfig | None = None) -> str:  # noqa: ANN401
    """Convert JSON data to TOON format string.

    Args:
        data: Python object to encode (dict, list, or primitive)
        config: Optional encoding configuration

    Returns:
        TOON format string
    """
    encoder = ToonEncoder(config)
    return encoder.encode(data)
