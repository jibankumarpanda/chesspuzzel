"""
nqueens.py
-----------
N-Queens placement solver.

The N-Queens problem: place N queens on an N x N (or R x C) board such
that no two queens attack each other (i.e. no two share a row, column,
or diagonal).

This module provides:
- `NQueensSolver`: a BaseSolver subclass with a Branch & Bound pruning
  rule specific to queens (an optimization beyond plain backtracking).
- `solve_nqueens(...)`: a convenience function used by the rest of the
  application (parser -> solver dispatch).
"""

from __future__ import annotations
from typing import List, Tuple, Optional

from algorithms.base_solver import BaseSolver, SolverResult
from algorithms.constraints import PieceType

Position = Tuple[int, int]


class NQueensSolver(BaseSolver):
    """
    Backtracking + Branch & Bound solver for the N-Queens placement
    puzzle. One queen is placed per row, trying each column in turn,
    which already eliminates row conflicts by construction -- this is
    the classic optimization that turns an O(N^N) search into a much
    smaller O(N!) search before any pruning is even applied.
    """

    piece_type = PieceType.QUEEN

    def bound(self, placed_positions: List[Position], row: int) -> bool:
        """
        Branch & Bound pruning hook for N-Queens.

        If the number of remaining rows is insufficient to place the
        remaining queens needed (relevant when piece_count < board_rows,
        e.g. placing fewer queens than the board has rows), prune early.
        """
        remaining_pieces_needed = self.piece_count - len(placed_positions)
        remaining_rows_available = self.board_rows - row
        if remaining_pieces_needed > remaining_rows_available:
            return True
        return False


def solve_nqueens(
    board_rows: int,
    board_cols: int,
    piece_count: int,
    max_solutions: Optional[int] = None,
    record_steps: bool = True,
) -> SolverResult:
    """
    Convenience entry point to solve an N-Queens style puzzle.

    Args:
        board_rows: number of rows on the board.
        board_cols: number of columns on the board.
        piece_count: number of queens to place (usually == board_rows).
        max_solutions: cap on number of solutions to find (None = all).
        record_steps: whether to record the human-readable step trace.

    Returns:
        A SolverResult with all solutions, steps, and statistics.
    """
    solver = NQueensSolver(
        board_rows=board_rows,
        board_cols=board_cols,
        piece_count=piece_count,
        max_solutions=max_solutions,
        record_steps=record_steps,
    )
    return solver.solve()
