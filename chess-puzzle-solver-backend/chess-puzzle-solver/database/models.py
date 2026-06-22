"""
models.py
----------
Lightweight dataclass models representing rows in the SQLite database.
These are plain data containers (no ORM) used to pass structured data
between the database layer (db.py) and the rest of the application,
keeping the persistence layer decoupled from raw sqlite3 tuples/rows.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class Puzzle:
    """
    Represents a row in the `puzzles` table: metadata about an
    uploaded/solved puzzle.

    Attributes:
        id: primary key (None until inserted into the database).
        filename: original uploaded filename (or a generated name for
            manually-configured puzzles).
        board_size: human-readable board dimensions, e.g. "8x8".
        piece_type: the chess piece type used in this puzzle.
        piece_count: number of pieces placed.
        constraint: the constraint mode used (e.g. NO_ATTACK).
        created_at: ISO-8601 timestamp string of when the puzzle was
            created/solved (set by the database layer).
    """
    filename: str
    board_size: str
    piece_type: str
    piece_count: int
    constraint: str
    id: Optional[int] = None
    created_at: Optional[str] = None


@dataclass
class Solution:
    """
    Represents a row in the `solutions` table: a single solver run's
    results for a given puzzle.

    Attributes:
        id: primary key (None until inserted into the database).
        puzzle_id: foreign key referencing `puzzles.id`.
        solution_data: JSON-serialized string containing the list of
            solutions (each solution itself a list of [row, col] pairs)
            plus the step-by-step trace, for full reproducibility.
        execution_time: solver execution time in seconds.
        solution_count: total number of distinct solutions found.
        nodes_explored: total search-tree nodes visited by the solver.
        backtracks: total number of backtrack operations performed.
        created_at: ISO-8601 timestamp string of when this solve ran.
    """
    puzzle_id: int
    solution_data: str
    execution_time: float
    solution_count: int
    id: Optional[int] = None
    nodes_explored: int = 0
    backtracks: int = 0
    created_at: Optional[str] = None
