"""
db.py
------
SQLite database access layer for the Chessboard Puzzle Solver.

Responsibilities:
- Initialize the SQLite database and create tables if they don't exist.
- Provide CRUD-style helper functions for the `puzzles` and `solutions`
  tables.
- Serialize/deserialize solution data (list of solutions + step trace)
  to/from JSON for storage in a single TEXT column, keeping the schema
  simple while still supporting rich, structured solution data.

This module intentionally avoids a full ORM (e.g. SQLAlchemy) to keep
the project dependency-light and easy to explain in a college project
report -- raw sqlite3 with parameterized queries is sufficient and
transparent.
"""

from __future__ import annotations
import sqlite3
import json
import os
from datetime import datetime, timezone
from contextlib import contextmanager
from typing import List, Optional, Generator

from database.models import Puzzle, Solution

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chess.db")


# ----------------------------------------------------------------------
# Connection management
# ----------------------------------------------------------------------

@contextmanager
def get_connection(db_path: str = DEFAULT_DB_PATH) -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager that yields a SQLite connection with foreign keys
    enabled and row factory set to sqlite3.Row for dict-like access.
    Commits on successful exit, rolls back on exception, and always
    closes the connection.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """
    Initialize the database schema. Creates the `puzzles` and
    `solutions` tables if they do not already exist. Safe to call on
    every app startup.
    """
    with get_connection(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS puzzles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                board_size TEXT NOT NULL,
                piece_type TEXT NOT NULL,
                piece_count INTEGER NOT NULL,
                constraint_type TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS solutions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                puzzle_id INTEGER NOT NULL,
                solution_data TEXT NOT NULL,
                execution_time REAL NOT NULL,
                solution_count INTEGER NOT NULL,
                nodes_explored INTEGER NOT NULL DEFAULT 0,
                backtracks INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (puzzle_id) REFERENCES puzzles (id) ON DELETE CASCADE
            );
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_solutions_puzzle_id ON solutions (puzzle_id);"
        )


def _now_iso() -> str:
    """Return the current UTC timestamp as an ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ----------------------------------------------------------------------
# Puzzle table operations
# ----------------------------------------------------------------------

def insert_puzzle(puzzle: Puzzle, db_path: str = DEFAULT_DB_PATH) -> int:
    """
    Insert a new puzzle record.

    Args:
        puzzle: a Puzzle dataclass instance (id/created_at ignored on insert).
        db_path: path to the SQLite database file.

    Returns:
        The auto-generated integer id of the newly inserted row.
    """
    created_at = _now_iso()
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            """
            INSERT INTO puzzles (filename, board_size, piece_type, piece_count, constraint_type, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                puzzle.filename,
                puzzle.board_size,
                puzzle.piece_type,
                puzzle.piece_count,
                puzzle.constraint,
                created_at,
            ),
        )
        return cursor.lastrowid


def get_puzzle(puzzle_id: int, db_path: str = DEFAULT_DB_PATH) -> Optional[Puzzle]:
    """Fetch a single puzzle by id. Returns None if not found."""
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT * FROM puzzles WHERE id = ?", (puzzle_id,)).fetchone()
        if row is None:
            return None
        return _row_to_puzzle(row)


def get_all_puzzles(db_path: str = DEFAULT_DB_PATH, limit: int = 200) -> List[Puzzle]:
    """Fetch all puzzles, most recent first, up to `limit` rows."""
    with get_connection(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM puzzles ORDER BY created_at DESC, id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [_row_to_puzzle(r) for r in rows]


def search_puzzles(query: str, db_path: str = DEFAULT_DB_PATH) -> List[Puzzle]:
    """
    Search puzzle history by filename or piece type (case-insensitive
    partial match). Used by the History page's search box.
    """
    like_query = f"%{query.strip()}%"
    with get_connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT * FROM puzzles
            WHERE filename LIKE ? COLLATE NOCASE
               OR piece_type LIKE ? COLLATE NOCASE
               OR board_size LIKE ? COLLATE NOCASE
            ORDER BY created_at DESC, id DESC
            """,
            (like_query, like_query, like_query),
        ).fetchall()
        return [_row_to_puzzle(r) for r in rows]


def delete_puzzle(puzzle_id: int, db_path: str = DEFAULT_DB_PATH) -> None:
    """Delete a puzzle and (via cascade) its associated solutions."""
    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM puzzles WHERE id = ?", (puzzle_id,))


def _row_to_puzzle(row: sqlite3.Row) -> Puzzle:
    """Convert a sqlite3.Row from the `puzzles` table into a Puzzle dataclass."""
    return Puzzle(
        id=row["id"],
        filename=row["filename"],
        board_size=row["board_size"],
        piece_type=row["piece_type"],
        piece_count=row["piece_count"],
        constraint=row["constraint_type"],
        created_at=row["created_at"],
    )


# ----------------------------------------------------------------------
# Solution table operations
# ----------------------------------------------------------------------

def insert_solution(solution: Solution, db_path: str = DEFAULT_DB_PATH) -> int:
    """
    Insert a new solution record linked to a puzzle.

    Args:
        solution: a Solution dataclass instance (id/created_at ignored).
        db_path: path to the SQLite database file.

    Returns:
        The auto-generated integer id of the newly inserted row.
    """
    created_at = _now_iso()
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            """
            INSERT INTO solutions
                (puzzle_id, solution_data, execution_time, solution_count, nodes_explored, backtracks, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                solution.puzzle_id,
                solution.solution_data,
                solution.execution_time,
                solution.solution_count,
                solution.nodes_explored,
                solution.backtracks,
                created_at,
            ),
        )
        return cursor.lastrowid


def get_solutions_for_puzzle(puzzle_id: int, db_path: str = DEFAULT_DB_PATH) -> List[Solution]:
    """Fetch all solution-run records associated with a given puzzle."""
    with get_connection(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM solutions WHERE puzzle_id = ? ORDER BY created_at DESC, id DESC",
            (puzzle_id,),
        ).fetchall()
        return [_row_to_solution(r) for r in rows]


def get_latest_solution_for_puzzle(puzzle_id: int, db_path: str = DEFAULT_DB_PATH) -> Optional[Solution]:
    """Fetch the most recent solution run for a given puzzle, if any."""
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM solutions WHERE puzzle_id = ? ORDER BY created_at DESC, id DESC LIMIT 1",
            (puzzle_id,),
        ).fetchone()
        return _row_to_solution(row) if row else None


def get_solution(solution_id: int, db_path: str = DEFAULT_DB_PATH) -> Optional[Solution]:
    """Fetch a single solution record by id."""
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT * FROM solutions WHERE id = ?", (solution_id,)).fetchone()
        return _row_to_solution(row) if row else None


def _row_to_solution(row: sqlite3.Row) -> Solution:
    """Convert a sqlite3.Row from the `solutions` table into a Solution dataclass."""
    return Solution(
        id=row["id"],
        puzzle_id=row["puzzle_id"],
        solution_data=row["solution_data"],
        execution_time=row["execution_time"],
        solution_count=row["solution_count"],
        nodes_explored=row["nodes_explored"],
        backtracks=row["backtracks"],
        created_at=row["created_at"],
    )


# ----------------------------------------------------------------------
# JSON serialization helpers for solution payloads
# ----------------------------------------------------------------------

def serialize_solution_payload(
    solutions: List[List[List[int]]],
    steps: List[str],
) -> str:
    """
    Serialize the full solver output (all solutions + step trace) into
    a single JSON string suitable for storage in the `solution_data`
    TEXT column.

    Args:
        solutions: list of solutions, each a list of [row, col] pairs.
        steps: list of human-readable step strings.

    Returns:
        A JSON-encoded string.
    """
    return json.dumps({"solutions": solutions, "steps": steps})


def deserialize_solution_payload(payload: str) -> dict:
    """
    Deserialize a JSON string (as produced by `serialize_solution_payload`)
    back into a dict with "solutions" and "steps" keys.
    """
    try:
        data = json.loads(payload)
    except (json.JSONDecodeError, TypeError):
        return {"solutions": [], "steps": []}
    data.setdefault("solutions", [])
    data.setdefault("steps", [])
    return data
