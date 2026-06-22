"""
bishops.py
-----------
Bishop Placement puzzle solver.

Goal: place B bishops on an R x C board such that no two bishops
attack each other along a diagonal (respecting the fact that, with
only bishops on the board, two bishops on the same diagonal always
attack each other -- there is nothing else on the board to block them).

Like knights, bishops can share rows and columns freely, so this
solver also uses the "visit every square, decide place-or-skip"
strategy rather than the one-per-row trick used for queens.
"""

from __future__ import annotations
from typing import List, Tuple, Optional

from algorithms.base_solver import BaseSolver, SolverResult
from algorithms.constraints import PieceType, is_valid_placement

Position = Tuple[int, int]


class BishopSolver(BaseSolver):
    """
    Backtracking solver for the Bishop Placement puzzle, using a
    square-by-square subset search (place-or-skip at each square),
    since bishops do not need exclusive rows/columns the way queens do.
    """

    piece_type = PieceType.BISHOP

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._squares: List[Position] = [
            (r, c)
            for r in range(self.board_rows)
            for c in range(self.board_cols)
        ]

    def candidate_positions(self, row: int) -> List[Position]:
        if row < len(self._squares):
            return [self._squares[row]]
        return []

    def bound(self, placed_positions: List[Position], row: int) -> bool:
        remaining_pieces_needed = self.piece_count - len(placed_positions)
        remaining_squares_available = len(self._squares) - row
        if remaining_pieces_needed > remaining_squares_available:
            return True
        return False

    def _backtrack(self, row: int, placed: List[Position]) -> bool:
        self.stats.nodes_explored += 1

        if len(placed) == self.piece_count:
            self.solutions.append(list(placed))
            self._log_step(f"Solution found: {self._format_positions(placed)}")
            if self.max_solutions is not None and len(self.solutions) >= self.max_solutions:
                return True
            return False

        if row >= len(self._squares):
            return False

        if self.bound(placed, row):
            return False

        pos = self._squares[row]

        if is_valid_placement(pos, placed, self.piece_type, self.board_rows, self.board_cols):
            placed.append(pos)
            self._log_step(f"Place Bishop at {pos}")
            if self._backtrack(row + 1, placed):
                return True
            placed.pop()
            self.stats.backtracks += 1
            self._log_step("Backtrack")
        else:
            self._log_step(f"Conflict detected at {pos}")

        if self._backtrack(row + 1, placed):
            return True

        return False


def solve_bishops(
    board_rows: int,
    board_cols: int,
    piece_count: int,
    max_solutions: Optional[int] = 1,
    record_steps: bool = True,
) -> SolverResult:
    """Convenience entry point to solve a Bishop Placement puzzle."""
    solver = BishopSolver(
        board_rows=board_rows,
        board_cols=board_cols,
        piece_count=piece_count,
        max_solutions=max_solutions,
        record_steps=record_steps,
    )
    return solver.solve()
