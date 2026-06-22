"""
base_solver.py
----------------
Abstract base class implementing the generic Backtracking + DFS engine
used by every chess placement puzzle (N-Queens, Knights, Bishops, Rooks,
Custom). Concrete subclasses only need to specify the PieceType and any
piece-specific pruning rules; the traversal, step-logging, and
statistics-gathering logic lives here so it is written once and tested
once.

Algorithms implemented:
- Depth First Search (DFS) over the search tree of partial placements.
- Backtracking: when a branch is exhausted or invalid, the most
  recently placed piece is removed ("backtracked") and the next
  candidate position is tried.
- Branch and Bound (optional): subclasses may override `bound()` to
  return True to prune a branch early (e.g. symmetry pruning, or
  remaining-rows-cannot-fit-pieces pruning), reducing nodes explored.

Step-by-step trace format (per project spec):
    Step 1: Place Queen at (0,0)
    Step 2: Place Queen at (1,4)
    Step 3: Conflict detected
    Step 4: Backtrack
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import time

from algorithms.constraints import PieceType, is_valid_placement

Position = Tuple[int, int]


@dataclass
class SolverStats:
    """Container for solver execution statistics."""
    nodes_explored: int = 0
    backtracks: int = 0
    solutions_found: int = 0
    execution_time_seconds: float = 0.0


@dataclass
class SolverResult:
    """Final packaged result returned by every solver."""
    solutions: List[List[Position]] = field(default_factory=list)
    steps: List[str] = field(default_factory=list)
    stats: SolverStats = field(default_factory=SolverStats)
    piece_type: PieceType = PieceType.QUEEN
    board_rows: int = 8
    board_cols: int = 8


class BaseSolver:
    """
    Generic backtracking/DFS solver for "place N pieces on an R x C
    board such that no two pieces attack each other" style puzzles.

    Subclasses customize behavior by overriding:
      - `piece_type`: which PieceType is being placed.
      - `candidate_positions(row)`: which columns/positions to try
        for a given row (default: every column).
      - `bound(placed_positions, row)`: optional Branch & Bound pruning
        hook. Return True to prune (skip) this branch early.
    """

    piece_type: PieceType = PieceType.QUEEN

    def __init__(
        self,
        board_rows: int,
        board_cols: int,
        piece_count: int,
        max_solutions: Optional[int] = None,
        record_steps: bool = True,
        max_steps: int = 5000,
    ) -> None:
        """
        Args:
            board_rows: number of rows on the board.
            board_cols: number of columns on the board.
            piece_count: number of pieces to place (e.g. N in N-Queens).
            max_solutions: stop after finding this many solutions
                (None = find all solutions).
            record_steps: whether to log a human-readable step trace.
                Disable for large boards to save memory.
            max_steps: cap on the number of step strings recorded, to
                prevent runaway memory usage on large search spaces.
        """
        self.board_rows = board_rows
        self.board_cols = board_cols
        self.piece_count = piece_count
        self.max_solutions = max_solutions
        self.record_steps = record_steps
        self.max_steps = max_steps

        self.solutions: List[List[Position]] = []
        self.steps: List[str] = []
        self.stats = SolverStats()

    # ------------------------------------------------------------------
    # Hooks for subclasses to customize search behavior
    # ------------------------------------------------------------------

    def candidate_positions(self, row: int) -> List[Position]:
        """Return the list of candidate (row, col) positions to try for
        the given row. Default: every column in that row."""
        return [(row, c) for c in range(self.board_cols)]

    def bound(self, placed_positions: List[Position], row: int) -> bool:
        """
        Branch and Bound hook. Return True to prune this branch
        (skip exploring further) before even checking constraints.
        Default implementation performs no extra pruning.
        """
        return False

    # ------------------------------------------------------------------
    # Step logging
    # ------------------------------------------------------------------

    def _log_step(self, message: str) -> None:
        """Append a step description to the trace, respecting max_steps."""
        if self.record_steps and len(self.steps) < self.max_steps:
            self.steps.append(f"Step {len(self.steps) + 1}: {message}")

    # ------------------------------------------------------------------
    # Core backtracking / DFS engine
    # ------------------------------------------------------------------

    def solve(self) -> SolverResult:
        """
        Run the backtracking search and return a fully populated
        SolverResult containing all solutions, the step trace, and
        execution statistics.
        """
        start_time = time.perf_counter()
        placed: List[Position] = []
        self._backtrack(row=0, placed=placed)
        elapsed = time.perf_counter() - start_time

        self.stats.execution_time_seconds = round(elapsed, 6)
        self.stats.solutions_found = len(self.solutions)

        return SolverResult(
            solutions=self.solutions,
            steps=self.steps,
            stats=self.stats,
            piece_type=self.piece_type,
            board_rows=self.board_rows,
            board_cols=self.board_cols,
        )

    def _backtrack(self, row: int, placed: List[Position]) -> bool:
        """
        Recursive backtracking step.

        Args:
            row: current row being processed (acts as the search depth).
            placed: list of positions already placed (mutated in place
                for efficiency, then restored on backtrack).

        Returns:
            True if the caller should stop searching entirely (used to
            short-circuit once `max_solutions` has been reached).
        """
        self.stats.nodes_explored += 1

        # Base case: we've placed all required pieces.
        if len(placed) == self.piece_count:
            self.solutions.append(list(placed))
            self._log_step(
                f"Solution found: {self._format_positions(placed)}"
            )
            if self.max_solutions is not None and len(self.solutions) >= self.max_solutions:
                return True
            return False

        # If we've run out of rows but haven't placed enough pieces, stop.
        if row >= self.board_rows:
            return False

        if self.bound(placed, row):
            # Branch & Bound pruning: skip this branch entirely.
            return False

        stop_signal = False
        for pos in self.candidate_positions(row):
            if is_valid_placement(pos, placed, self.piece_type, self.board_rows, self.board_cols):
                placed.append(pos)
                self._log_step(
                    f"Place {self.piece_type.value.title()} at {pos}"
                )

                stop_signal = self._backtrack(row + 1, placed)

                # Backtrack: remove the piece we just tried.
                placed.pop()
                if stop_signal:
                    return True
                self.stats.backtracks += 1
                self._log_step("Backtrack")
            else:
                self._log_step(f"Conflict detected at {pos}")

        # Also allow trying the next row directly (covers boards where
        # piece_count < board_rows, i.e. not every row needs a piece).
        if not stop_signal and row + 1 <= self.board_rows:
            stop_signal = self._backtrack(row + 1, placed)

        return stop_signal

    @staticmethod
    def _format_positions(positions: List[Position]) -> str:
        """Human-readable formatting of a list of board positions."""
        return ", ".join(f"({r},{c})" for r, c in positions)
