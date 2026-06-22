"""
rooks.py
---------
Rook Placement puzzle solver.

Goal: place R rooks on a board such that no two rooks attack each
other (i.e. no two share a row or column). This is structurally
identical to N-Queens but without the diagonal constraint, so it
reuses the efficient one-piece-per-row placement strategy from
NQueensSolver's parent (BaseSolver's default `candidate_positions`),
which already guarantees no two pieces share a row by construction.
"""

from __future__ import annotations
from typing import Tuple, Optional

from algorithms.base_solver import BaseSolver, SolverResult
from algorithms.constraints import PieceType

Position = Tuple[int, int]


class RookSolver(BaseSolver):
    """
    Backtracking solver for the Rook Placement puzzle. One rook is
    placed per row (inherited default `candidate_positions` behavior),
    which automatically satisfies the "no shared row" constraint;
    column conflicts are checked via `is_valid_placement`.
    """

    piece_type = PieceType.ROOK

    def bound(self, placed_positions, row: int) -> bool:
        remaining_pieces_needed = self.piece_count - len(placed_positions)
        remaining_rows_available = self.board_rows - row
        if remaining_pieces_needed > remaining_rows_available:
            return True
        return False


def solve_rooks(
    board_rows: int,
    board_cols: int,
    piece_count: int,
    max_solutions: Optional[int] = None,
    record_steps: bool = True,
) -> SolverResult:
    """Convenience entry point to solve a Rook Placement puzzle."""
    solver = RookSolver(
        board_rows=board_rows,
        board_cols=board_cols,
        piece_count=piece_count,
        max_solutions=max_solutions,
        record_steps=record_steps,
    )
    return solver.solve()
