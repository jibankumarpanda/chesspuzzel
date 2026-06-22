"""
parser/__init__.py
--------------------
Marks `parser` as a Python package and re-exports the main parsing
entry points for convenient importing elsewhere in the application.
"""

from parser.txt_parser import (
    parse_dataset_text,
    parse_dataset_file,
    PuzzleDataset,
    DatasetParseError,
)

__all__ = [
    "parse_dataset_text",
    "parse_dataset_file",
    "PuzzleDataset",
    "DatasetParseError",
]
