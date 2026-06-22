"""
constraints.py
----------------
Core constraint-checking utilities for chessboard placement puzzles.

This module centralizes all conflict-detection logic (row, column,
diagonal, knight-move, bishop-move, rook-move) so that every solver
(N-Queens, Knight Placement, Bishop Placement, Rook Placement, Custom)
can reuse the same validated, well-tested primitives instead of
duplicating logic.

Design notes:
- Board state is represented as a list of (row, col) tuples -- the
  coordinates of pieces already placed on the board.
- All functions are pure (no side effects) so they are easy to unit
  test and reason about during backtracking.
- Type hints are used throughout for clarity and IDE support.
"""

from __future__ import annotations
from typing import List, Tuple, Iterable
from enum import Enum


Position = Tuple[int, int]


class PieceType(str, Enum):
    """Supported chess piece types for placement puzzles."""
    QUEEN = "QUEEN"
    KNIGHT = "KNIGHT"
    BISHOP = "BISHOP"
    ROOK = "ROOK"
    KING = "KING"
    CUSTOM = "CUSTOM"


class ConstraintType(str, Enum):
    """Supported high-level constraint modes parsed from dataset files."""
    NO_ATTACK = "NO_ATTACK"          # No two pieces may attack each other
    UNIQUE_ROW_COL = "UNIQUE_ROW_COL"  # At most one piece per row & column
    CUSTOM = "CUSTOM"


# ----------------------------------------------------------------------
# Low-level geometric conflict checks
# ----------------------------------------------------------------------

def same_row(p1: Position, p2: Position) -> bool:
    """Return True if two positions share the same row."""
    return p1[0] == p2[0]


def same_col(p1: Position, p2: Position) -> bool:
    """Return True if two positions share the same column."""
    return p1[1] == p2[1]


def same_diagonal(p1: Position, p2: Position) -> bool:
    """Return True if two positions lie on the same diagonal."""
    return abs(p1[0] - p2[0]) == abs(p1[1] - p2[1])


def is_knight_move(p1: Position, p2: Position) -> bool:
    """Return True if moving from p1 to p2 is a valid knight move (L-shape)."""
    dr = abs(p1[0] - p2[0])
    dc = abs(p1[1] - p2[1])
    return (dr, dc) in [(1, 2), (2, 1)]


def is_clear_path_rook(p1: Position, p2: Position, occupied: Iterable[Position]) -> bool:
    """
    Return True if a rook at p1 can attack p2 along a straight line,
    assuming no other piece blocks the path. `occupied` should exclude
    p1 and p2 themselves.
    """
    if p1 == p2:
        return False
    if not (same_row(p1, p2) or same_col(p1, p2)):
        return False
    occupied_set = set(occupied) - {p1, p2}
    if same_row(p1, p2):
        step = 1 if p2[1] > p1[1] else -1
        for c in range(p1[1] + step, p2[1], step):
            if (p1[0], c) in occupied_set:
                return False
        return True
    else:  # same column
        step = 1 if p2[0] > p1[0] else -1
        for r in range(p1[0] + step, p2[0], step):
            if (r, p1[1]) in occupied_set:
                return False
        return True


def is_clear_path_bishop(p1: Position, p2: Position, occupied: Iterable[Position]) -> bool:
    """
    Return True if a bishop at p1 can attack p2 along a diagonal,
    assuming no other piece blocks the path.
    """
    if p1 == p2:
        return False
    if not same_diagonal(p1, p2):
        return False
    occupied_set = set(occupied) - {p1, p2}
    row_step = 1 if p2[0] > p1[0] else -1
    col_step = 1 if p2[1] > p1[1] else -1
    r, c = p1[0] + row_step, p1[1] + col_step
    while (r, c) != p2:
        if (r, c) in occupied_set:
            return False
        r += row_step
        c += col_step
    return True


# ----------------------------------------------------------------------
# Piece-specific attack predicates (no obstruction awareness needed
# for the classic placement puzzles, where pieces attack regardless
# of blockers EXCEPT for rook/bishop, which respect blocking pieces)
# ----------------------------------------------------------------------

def queen_attacks(p1: Position, p2: Position) -> bool:
    """Queen attacks along row, column, or diagonal (unobstructed in
    classic N-Queens variant, since only queen pieces are present)."""
    return same_row(p1, p2) or same_col(p1, p2) or same_diagonal(p1, p2)


def rook_attacks(p1: Position, p2: Position, occupied: Iterable[Position] | None = None) -> bool:
    """Rook attacks along row or column, respecting blocking pieces if provided."""
    if occupied is None:
        return same_row(p1, p2) or same_col(p1, p2)
    return is_clear_path_rook(p1, p2, occupied)


def bishop_attacks(p1: Position, p2: Position, occupied: Iterable[Position] | None = None) -> bool:
    """Bishop attacks along diagonals, respecting blocking pieces if provided."""
    if occupied is None:
        return same_diagonal(p1, p2)
    return is_clear_path_bishop(p1, p2, occupied)


def knight_attacks(p1: Position, p2: Position) -> bool:
    """Knight attacks in an L-shape; knights can never block each other."""
    return is_knight_move(p1, p2)


def king_attacks(p1: Position, p2: Position) -> bool:
    """King attacks any of the 8 adjacent squares."""
    dr = abs(p1[0] - p2[0])
    dc = abs(p1[1] - p2[1])
    return max(dr, dc) == 1


# Mapping from PieceType to its attack-checking function.
ATTACK_FUNCTIONS = {
    PieceType.QUEEN: lambda p1, p2, occ: queen_attacks(p1, p2),
    PieceType.ROOK: lambda p1, p2, occ: rook_attacks(p1, p2, occ),
    PieceType.BISHOP: lambda p1, p2, occ: bishop_attacks(p1, p2, occ),
    PieceType.KNIGHT: lambda p1, p2, occ: knight_attacks(p1, p2),
    PieceType.KING: lambda p1, p2, occ: king_attacks(p1, p2),
}


def pieces_attack_each_other(
    p1: Position,
    p2: Position,
    piece_type: PieceType,
    occupied: Iterable[Position] | None = None,
) -> bool:
    """
    Generic dispatcher: returns True if a piece of `piece_type` placed
    at p1 attacks p2 (and vice versa, since chess attacks are symmetric
    for these piece types).
    """
    fn = ATTACK_FUNCTIONS.get(piece_type)
    if fn is None:
        # CUSTOM falls back to "no two pieces share row/col/diagonal"
        return queen_attacks(p1, p2)
    return fn(p1, p2, occupied)


def is_valid_placement(
    new_pos: Position,
    placed_positions: List[Position],
    piece_type: PieceType,
    board_rows: int,
    board_cols: int,
) -> bool:
    """
    Validate whether placing a piece of `piece_type` at `new_pos` is
    legal given the pieces already on the board.

    Checks:
      1. Position is within board bounds.
      2. Position is not already occupied.
      3. Position does not conflict (attack / be attacked) with any
         existing piece, according to the piece's movement rules.

    Args:
        new_pos: (row, col) candidate position.
        placed_positions: list of currently placed piece coordinates.
        piece_type: the type of piece being placed (affects conflict rules).
        board_rows: total rows on board (for bounds checking).
        board_cols: total columns on board (for bounds checking).

    Returns:
        True if the placement is valid (no conflicts), False otherwise.
    """
    r, c = new_pos
    if not (0 <= r < board_rows and 0 <= c < board_cols):
        return False
    if new_pos in placed_positions:
        return False

    for existing in placed_positions:
        if pieces_attack_each_other(existing, new_pos, piece_type, placed_positions):
            return False
    return True
