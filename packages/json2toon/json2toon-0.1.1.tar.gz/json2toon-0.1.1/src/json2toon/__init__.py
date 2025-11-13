"""json2toon: Bidirectional converter between JSON and TOON format.

This package provides functions and classes for converting between JSON and TOON
(Token-Oriented Object Notation) format, optimized for LLM token efficiency.
"""

from __future__ import annotations

from json2toon.decoder import ToonDecoder, ToonParseConfig, ToonParseError, toon_to_json
from json2toon.encoder import ToonConfig, ToonEncoder, json_to_toon

__version__ = "0.1.1"

__all__ = [
    # Encoder
    "ToonEncoder",
    "ToonConfig",
    "json_to_toon",
    # Decoder
    "ToonDecoder",
    "ToonParseConfig",
    "ToonParseError",
    "toon_to_json",
    # Version
    "__version__",
]
