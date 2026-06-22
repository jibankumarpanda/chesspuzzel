"""
database/__init__.py
----------------------
Marks `database` as a Python package and re-exports the most commonly
used functions/classes for convenient importing elsewhere.
"""

from database.db import (
    init_db,
    insert_puzzle,
    get_puzzle,
    get_all_puzzles,
    search_puzzles,
    delete_puzzle,
    insert_solution,
    get_solutions_for_puzzle,
    get_latest_solution_for_puzzle,
    get_solution,
    serialize_solution_payload,
    deserialize_solution_payload,
    DEFAULT_DB_PATH,
)
from database.models import Puzzle, Solution

__all__ = [
    "init_db",
    "insert_puzzle",
    "get_puzzle",
    "get_all_puzzles",
    "search_puzzles",
    "delete_puzzle",
    "insert_solution",
    "get_solutions_for_puzzle",
    "get_latest_solution_for_puzzle",
    "get_solution",
    "serialize_solution_payload",
    "deserialize_solution_payload",
    "DEFAULT_DB_PATH",
    "Puzzle",
    "Solution",
]
