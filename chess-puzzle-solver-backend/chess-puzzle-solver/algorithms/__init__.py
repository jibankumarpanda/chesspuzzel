"""
algorithms/__init__.py
------------------------
Marks `algorithms` as a Python package and exposes a single unified
`solve_puzzle()` dispatcher so the rest of the app (Streamlit UI,
database layer) doesn't need to know which specific solver module
handles which piece type.
"""

from __future__ import annotations
from typing import Optional

from algorithms.constraints import PieceType
from algorithms.base_solver import SolverResult
from algorithms.nqueens import solve_nqueens
from algorithms.knights import solve_knights
from algorithms.bishops import solve_bishops
from algorithms.rooks import solve_rooks


def solve_puzzle(
    piece_type: str,
    board_rows: int,
    board_cols: int,
    piece_count: int,
    max_solutions: Optional[int] = None,
    record_steps: bool = True,
) -> SolverResult:
    """
    Unified dispatcher: routes a parsed puzzle specification to the
    correct solver implementation based on `piece_type`.

    Args:
        piece_type: one of "QUEEN", "KNIGHT", "BISHOP", "ROOK" (case
            insensitive). Custom constraint puzzles also default to
            the queen-style (row/col/diagonal) ruleset unless extended.
        board_rows: number of rows on the board.
        board_cols: number of columns on the board.
        piece_count: number of pieces to place.
        max_solutions: cap on number of solutions to find (None = all).
            For Knight/Bishop puzzles, leaving this as None on large
            boards can be very slow; the UI layer should set a sane
            default (e.g. 1 or a small cap) unless the user opts in to
            an exhaustive search.
        record_steps: whether to record a human-readable step trace.

    Returns:
        A SolverResult with solutions, steps, and statistics.

    Raises:
        ValueError: if `piece_type` is not a recognized/supported type.
    """
    normalized = piece_type.strip().upper()

    if normalized == PieceType.QUEEN.value:
        return solve_nqueens(board_rows, board_cols, piece_count, max_solutions, record_steps)
    elif normalized == PieceType.KNIGHT.value:
        return solve_knights(board_rows, board_cols, piece_count, max_solutions or 1, record_steps)
    elif normalized == PieceType.BISHOP.value:
        return solve_bishops(board_rows, board_cols, piece_count, max_solutions or 1, record_steps)
    elif normalized == PieceType.ROOK.value:
        return solve_rooks(board_rows, board_cols, piece_count, max_solutions, record_steps)
    else:
        raise ValueError(
            f"Unsupported piece type: '{piece_type}'. "
            f"Supported types: QUEEN, KNIGHT, BISHOP, ROOK."
        )


__all__ = [
    "solve_puzzle",
    "solve_nqueens",
    "solve_knights",
    "solve_bishops",
    "solve_rooks",
    "PieceType",
    "SolverResult",
]
