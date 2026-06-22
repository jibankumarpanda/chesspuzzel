"""
txt_parser.py
--------------
Parses and validates the plain-text puzzle dataset files uploaded by
the user through the Streamlit UI.

Expected file format (whitespace-insensitive, one directive per line):

    BOARD <rows> <cols>
    PIECE <QUEEN|KNIGHT|BISHOP|ROOK>
    COUNT <number_of_pieces>
    CONSTRAINT <NO_ATTACK|UNIQUE_ROW_COL|CUSTOM>

Example:

    BOARD 8 8
    PIECE QUEEN
    COUNT 8
    CONSTRAINT NO_ATTACK

Lines starting with '#' are treated as comments and ignored. Directive
keywords are case-insensitive. Order of directives does not matter,
but all four directives are required.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional

from algorithms.constraints import PieceType, ConstraintType


class DatasetParseError(Exception):
    """Raised when an uploaded dataset file is malformed or invalid."""
    pass


@dataclass
class PuzzleDataset:
    """Structured representation of a parsed puzzle dataset file."""
    board_rows: int
    board_cols: int
    piece_type: str
    piece_count: int
    constraint: str
    raw_text: str
    filename: str = "uploaded_dataset.txt"

    def summary(self) -> str:
        """Short human-readable summary, useful for UI display."""
        return (
            f"Board: {self.board_rows}x{self.board_cols} | "
            f"Piece: {self.piece_type} | Count: {self.piece_count} | "
            f"Constraint: {self.constraint}"
        )


VALID_PIECES = {p.value for p in PieceType}
VALID_CONSTRAINTS = {c.value for c in ConstraintType}


def _strip_comments_and_blank_lines(lines: List[str]) -> List[str]:
    """Remove comment lines (starting with '#') and blank lines."""
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        cleaned.append(stripped)
    return cleaned


def parse_dataset_text(text: str, filename: str = "uploaded_dataset.txt") -> PuzzleDataset:
    """
    Parse raw dataset text content into a validated PuzzleDataset.

    Args:
        text: full raw text content of the uploaded .txt file.
        filename: original filename, stored for record-keeping.

    Returns:
        A validated PuzzleDataset instance.

    Raises:
        DatasetParseError: if any required directive is missing,
            malformed, or contains an invalid/unsupported value.
    """
    if text is None or not text.strip():
        raise DatasetParseError("The uploaded file is empty.")

    lines = _strip_comments_and_blank_lines(text.splitlines())
    if not lines:
        raise DatasetParseError("The uploaded file contains no valid directives.")

    directives = {}
    for line_number, line in enumerate(lines, start=1):
        parts = line.split()
        keyword = parts[0].upper()

        if keyword == "BOARD":
            if len(parts) != 3:
                raise DatasetParseError(
                    f"Line {line_number}: 'BOARD' requires exactly two integers "
                    f"(rows and columns), e.g. 'BOARD 8 8'. Got: '{line}'"
                )
            try:
                rows, cols = int(parts[1]), int(parts[2])
            except ValueError:
                raise DatasetParseError(
                    f"Line {line_number}: BOARD rows/columns must be integers. Got: '{line}'"
                )
            if rows <= 0 or cols <= 0:
                raise DatasetParseError(
                    f"Line {line_number}: BOARD dimensions must be positive integers."
                )
            if rows > 30 or cols > 30:
                raise DatasetParseError(
                    f"Line {line_number}: BOARD dimensions above 30x30 are not supported "
                    f"(search space becomes computationally infeasible for a classroom demo)."
                )
            directives["board_rows"] = rows
            directives["board_cols"] = cols

        elif keyword == "PIECE":
            if len(parts) != 2:
                raise DatasetParseError(
                    f"Line {line_number}: 'PIECE' requires exactly one value, e.g. 'PIECE QUEEN'."
                )
            piece = parts[1].upper()
            if piece not in VALID_PIECES:
                raise DatasetParseError(
                    f"Line {line_number}: Unsupported piece type '{piece}'. "
                    f"Supported types: {', '.join(sorted(VALID_PIECES))}."
                )
            directives["piece_type"] = piece

        elif keyword == "COUNT":
            if len(parts) != 2:
                raise DatasetParseError(
                    f"Line {line_number}: 'COUNT' requires exactly one integer, e.g. 'COUNT 8'."
                )
            try:
                count = int(parts[1])
            except ValueError:
                raise DatasetParseError(
                    f"Line {line_number}: COUNT must be an integer. Got: '{line}'"
                )
            if count <= 0:
                raise DatasetParseError(f"Line {line_number}: COUNT must be a positive integer.")
            directives["piece_count"] = count

        elif keyword == "CONSTRAINT":
            if len(parts) != 2:
                raise DatasetParseError(
                    f"Line {line_number}: 'CONSTRAINT' requires exactly one value, "
                    f"e.g. 'CONSTRAINT NO_ATTACK'."
                )
            constraint = parts[1].upper()
            if constraint not in VALID_CONSTRAINTS:
                raise DatasetParseError(
                    f"Line {line_number}: Unsupported constraint '{constraint}'. "
                    f"Supported constraints: {', '.join(sorted(VALID_CONSTRAINTS))}."
                )
            directives["constraint"] = constraint

        else:
            raise DatasetParseError(
                f"Line {line_number}: Unrecognized directive '{keyword}'. "
                f"Expected one of: BOARD, PIECE, COUNT, CONSTRAINT."
            )

    required_keys = ["board_rows", "board_cols", "piece_type", "piece_count", "constraint"]
    missing = [k for k in required_keys if k not in directives]
    if missing:
        raise DatasetParseError(
            f"Dataset file is missing required directive(s): {', '.join(missing)}."
        )

    # Cross-field validation: piece count must be physically placeable.
    board_rows = directives["board_rows"]
    board_cols = directives["board_cols"]
    piece_count = directives["piece_count"]
    total_squares = board_rows * board_cols

    if piece_count > total_squares:
        raise DatasetParseError(
            f"COUNT ({piece_count}) exceeds total board squares "
            f"({board_rows}x{board_cols} = {total_squares}). Cannot place that many pieces."
        )

    if directives["piece_type"] == PieceType.QUEEN.value and piece_count > board_rows:
        raise DatasetParseError(
            f"COUNT ({piece_count}) exceeds board rows ({board_rows}). "
            f"For QUEEN/ROOK placement, the piece count cannot exceed the number of rows, "
            f"since each row can hold at most one such piece under NO_ATTACK."
        )

    if directives["piece_type"] == PieceType.ROOK.value and piece_count > board_rows:
        raise DatasetParseError(
            f"COUNT ({piece_count}) exceeds board rows ({board_rows}) for ROOK placement "
            f"under NO_ATTACK (one rook per row maximum)."
        )

    return PuzzleDataset(
        board_rows=board_rows,
        board_cols=board_cols,
        piece_type=directives["piece_type"],
        piece_count=piece_count,
        constraint=directives["constraint"],
        raw_text=text,
        filename=filename,
    )


def parse_dataset_file(file_path: str) -> PuzzleDataset:
    """
    Read and parse a dataset file from disk.

    Args:
        file_path: path to the .txt dataset file on disk.

    Returns:
        A validated PuzzleDataset instance.

    Raises:
        DatasetParseError: if the file cannot be read or is invalid.
        FileNotFoundError: if the file does not exist.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        raise
    except UnicodeDecodeError:
        raise DatasetParseError(
            "The uploaded file is not a valid UTF-8 encoded text file."
        )

    filename = file_path.split("/")[-1]
    return parse_dataset_text(text, filename=filename)
