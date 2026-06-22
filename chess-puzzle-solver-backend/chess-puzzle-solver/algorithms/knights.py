"""
knights.py
-----------
Knight Placement puzzle solver.

Goal: place K knights on an R x C board such that no two knights
attack each other (no two are an L-shaped knight's-move apart).

Unlike queens, knights only conflict with pieces in the SAME row in
the trivial case of zero columns apart, so we cannot rely on the
"one piece per row" placement trick used for N-Queens (multiple
knights CAN safely share a row). Instead this solver searches over
every square of the board in row-major order and decides, for each
square, whether to place a knight or skip it -- a classic subset
search expressed through the shared backtracking engine by treating
every board square as its own "row" in the search tree.
"""

from __future__ import annotations
from typing import List, Tuple, Optional

from algorithms.base_solver import BaseSolver, SolverResult
from algorithms.constraints import PieceType

Position = Tuple[int, int]


class KnightSolver(BaseSolver):
    """
    Backtracking solver for the Knight Placement puzzle.

    Search strategy: enumerate board squares in row-major order
    (square index 0 .. rows*cols - 1). At each square, branch into
    "place a knight here" vs "leave empty", subject to the
    no-two-knights-attack constraint. This differs from the
    one-piece-per-row strategy used for queens because knights may
    legally share a row or column.
    """

    piece_type = PieceType.KNIGHT

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-compute the full list of board squares in row-major order;
        # `row` in the base engine's recursion is reinterpreted here as
        # a "square index" rather than a literal board row.
        self._squares: List[Position] = [
            (r, c)
            for r in range(self.board_rows)
            for c in range(self.board_cols)
        ]

    def candidate_positions(self, row: int) -> List[Position]:
        """`row` is reinterpreted as a square index into `_squares`."""
        if row < len(self._squares):
            return [self._squares[row]]
        return []

    def bound(self, placed_positions: List[Position], row: int) -> bool:
        """
        Branch & Bound pruning: if there are not enough remaining
        squares left to reach `piece_count` knights, prune this branch.
        """
        remaining_pieces_needed = self.piece_count - len(placed_positions)
        remaining_squares_available = len(self._squares) - row
        if remaining_pieces_needed > remaining_squares_available:
            return True
        return False

    def _backtrack(self, row: int, placed: List[Position]) -> bool:
        """
        Override: at each square we must explicitly consider BOTH
        "place here" and "skip" branches (unlike queens, where skipping
        a row isn't meaningful since exactly one queen goes per row).
        """
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

        from algorithms.constraints import is_valid_placement

        pos = self._squares[row]

        # Branch 1: try placing a knight at this square.
        if is_valid_placement(pos, placed, self.piece_type, self.board_rows, self.board_cols):
            placed.append(pos)
            self._log_step(f"Place Knight at {pos}")
            if self._backtrack(row + 1, placed):
                return True
            placed.pop()
            self.stats.backtracks += 1
            self._log_step("Backtrack")
        else:
            self._log_step(f"Conflict detected at {pos}")

        # Branch 2: skip this square entirely and move to the next one.
        if self._backtrack(row + 1, placed):
            return True

        return False


def solve_knights(
    board_rows: int,
    board_cols: int,
    piece_count: int,
    max_solutions: Optional[int] = 1,
    record_steps: bool = True,
) -> SolverResult:
    """
    Convenience entry point to solve a Knight Placement puzzle.

    Note: because the search space for knight placement (subset
    selection over all squares) is much larger than N-Queens'
    permutation search, `max_solutions` defaults to 1 to keep solve
    times reasonable for classroom/demo use. Pass a higher number or
    None for exhaustive search on small boards only.
    """
    solver = KnightSolver(
        board_rows=board_rows,
        board_cols=board_cols,
        piece_count=piece_count,
        max_solutions=max_solutions,
        record_steps=record_steps,
    )
    return solver.solve()
