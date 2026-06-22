"""Backend integration layer.

Tries to import the real chess-puzzle-solver backend (algorithms/, parser/,
database/). If those packages are not present, falls back to in-app
implementations that match the documented API surface, so the Reflex app
remains runnable end-to-end without raw tracebacks.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Optional

# ---------------------------------------------------------------------------
# Try real backend first
# ---------------------------------------------------------------------------
BACKEND_AVAILABLE = False
BACKEND_NOTE = ""

try:
    # Attempting to load real backend module if available in python path
    from algorithms import solve_puzzle as _real_solve_puzzle  # type: ignore
    from parser.txt_parser import (  # type: ignore
        parse_dataset_text as _real_parse_dataset_text,
        DatasetParseError as _RealDatasetParseError,
        PuzzleDataset as _RealPuzzleDataset,
    )

    BACKEND_AVAILABLE = True
    BACKEND_NOTE = "Connected to chess-puzzle-solver backend modules."
except ImportError:
    # This is the expected flow when real backend packages are not physically present;
    # we fall back to the built-in pure Python engine cleanly without logging tracebacks.
    BACKEND_AVAILABLE = False
    BACKEND_NOTE = (
        "Real backend modules (algorithms/, parser/) not detected. "
        "Running with built-in fallback engine. To use the official engine, "
        "place the algorithms/, parser/, and database/ packages alongside "
        "this Reflex app's root directory."
    )
except Exception as e:
    logging.exception("Unexpected error loading backend")
    BACKEND_AVAILABLE = False
    BACKEND_NOTE = (
        "Unexpected error detected while checking for native backend packages."
    )


# ---------------------------------------------------------------------------
# Public dataclasses (mirror real backend shape)
# ---------------------------------------------------------------------------
VALID_PIECES = ("QUEEN", "KNIGHT", "BISHOP", "ROOK")
VALID_CONSTRAINTS = ("NO_ATTACK", "UNIQUE_ROW_COL", "CUSTOM")


class DatasetParseError(Exception):
    pass


@dataclass
class PuzzleDataset:
    board_rows: int = 0
    board_cols: int = 0
    piece_type: str = ""
    piece_count: int = 0
    constraint: str = ""
    raw_text: str = ""
    filename: str = "uploaded_dataset.txt"

    def summary(self) -> str:
        return (
            f"{self.filename} :: {self.board_rows}x{self.board_cols} board, "
            f"{self.piece_count} {self.piece_type}(S), constraint={self.constraint}"
        )


@dataclass
class SolverStats:
    nodes_explored: int = 0
    backtracks: int = 0
    solutions_found: int = 0
    execution_time_seconds: float = 0.0


@dataclass
class SolverResult:
    solutions: list[list[tuple[int, int]]] = field(default_factory=list)
    steps: list[str] = field(default_factory=list)
    stats: SolverStats = field(default_factory=SolverStats)
    piece_type: str = ""
    board_rows: int = 0
    board_cols: int = 0


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------
def _fallback_parse(
    text: str, filename: str = "uploaded_dataset.txt"
) -> PuzzleDataset:
    if not text or not text.strip():
        raise DatasetParseError(
            "Dataset is empty. Provide BOARD, PIECE, COUNT, CONSTRAINT lines."
        )

    fields: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        key = parts[0].upper()
        if key == "BOARD":
            if len(parts) < 3:
                raise DatasetParseError(
                    f"Invalid BOARD line: '{line}'. Expected 'BOARD <rows> <cols>'."
                )
            try:
                fields["rows"] = str(int(parts[1]))
                fields["cols"] = str(int(parts[2]))
            except ValueError:
                raise DatasetParseError(
                    f"BOARD dimensions must be integers, got: '{line}'."
                )
        elif key == "PIECE":
            if len(parts) < 2:
                raise DatasetParseError(f"Invalid PIECE line: '{line}'.")
            piece = parts[1].upper()
            if piece not in VALID_PIECES:
                raise DatasetParseError(
                    f"Unknown PIECE '{piece}'. Allowed: {', '.join(VALID_PIECES)}."
                )
            fields["piece"] = piece
        elif key == "COUNT":
            if len(parts) < 2:
                raise DatasetParseError(f"Invalid COUNT line: '{line}'.")
            try:
                fields["count"] = str(int(parts[1]))
            except ValueError:
                raise DatasetParseError(
                    f"COUNT must be an integer, got: '{line}'."
                )
        elif key == "CONSTRAINT":
            if len(parts) < 2:
                raise DatasetParseError(f"Invalid CONSTRAINT line: '{line}'.")
            cons = parts[1].upper()
            if cons not in VALID_CONSTRAINTS:
                raise DatasetParseError(
                    f"Unknown CONSTRAINT '{cons}'. Allowed: {', '.join(VALID_CONSTRAINTS)}."
                )
            fields["constraint"] = cons

    required = ["rows", "cols", "piece", "count", "constraint"]
    missing = [f for f in required if f not in fields]
    if missing:
        label_map = {
            "rows": "BOARD",
            "cols": "BOARD",
            "piece": "PIECE",
            "count": "COUNT",
            "constraint": "CONSTRAINT",
        }
        labels = sorted({label_map[m] for m in missing})
        raise DatasetParseError(
            f"Missing required directive(s): {', '.join(labels)}. "
            "All four directives (BOARD, PIECE, COUNT, CONSTRAINT) are required."
        )

    rows = int(fields["rows"])
    cols = int(fields["cols"])
    count = int(fields["count"])

    if rows < 1 or cols < 1:
        raise DatasetParseError("BOARD dimensions must be at least 1x1.")
    if rows > 20 or cols > 20:
        raise DatasetParseError(
            "BOARD dimensions exceed engine limit of 20x20."
        )
    if count < 1:
        raise DatasetParseError("COUNT must be at least 1.")
    if count > rows * cols:
        raise DatasetParseError(
            f"COUNT ({count}) exceeds total board squares ({rows * cols})."
        )

    return PuzzleDataset(
        board_rows=rows,
        board_cols=cols,
        piece_type=fields["piece"],
        piece_count=count,
        constraint=fields["constraint"],
        raw_text=text,
        filename=filename,
    )


def parse_dataset_text(
    text: str, filename: str = "uploaded_dataset.txt"
) -> PuzzleDataset:
    """Parse a dataset text using real parser if available, else fallback."""
    if BACKEND_AVAILABLE:
        try:
            real = _real_parse_dataset_text(text, filename)
            return PuzzleDataset(
                board_rows=real.board_rows,
                board_cols=real.board_cols,
                piece_type=real.piece_type,
                piece_count=real.piece_count,
                constraint=real.constraint,
                raw_text=getattr(real, "raw_text", text),
                filename=getattr(real, "filename", filename),
            )
        except _RealDatasetParseError as e:  # type: ignore
            logging.exception("Unexpected error")
            raise DatasetParseError(e) from e
    return _fallback_parse(text, filename)


# ---------------------------------------------------------------------------
# Fallback solver
# ---------------------------------------------------------------------------
def _attacks(r1: int, c1: int, r2: int, c2: int, piece: str) -> bool:
    if piece == "QUEEN":
        return r1 == r2 or c1 == c2 or abs(r1 - r2) == abs(c1 - c2)
    if piece == "ROOK":
        return r1 == r2 or c1 == c2
    if piece == "BISHOP":
        return abs(r1 - r2) == abs(c1 - c2)
    if piece == "KNIGHT":
        dr, dc = abs(r1 - r2), abs(c1 - c2)
        return (dr == 1 and dc == 2) or (dr == 2 and dc == 1)
    return False


def _piece_label(piece: str) -> str:
    return piece.title()


def _fallback_solve(
    piece_type: str,
    board_rows: int,
    board_cols: int,
    piece_count: int,
    max_solutions: Optional[int] = None,
    record_steps: bool = True,
) -> SolverResult:
    piece = piece_type.upper()
    if piece not in VALID_PIECES:
        raise ValueError(f"Unsupported piece type: {piece_type}")

    solutions: list[list[tuple[int, int]]] = []
    steps: list[str] = []
    stats = SolverStats()
    label = _piece_label(piece)

    # cap step recording to avoid memory blowup on large searches
    step_cap = 4000

    def add_step(msg: str):
        if record_steps and len(steps) < step_cap:
            steps.append(msg)

    start = time.perf_counter()

    placed: list[tuple[int, int]] = []

    # Squares ordered row-major
    all_squares = [(r, c) for r in range(board_rows) for c in range(board_cols)]
    total_squares = len(all_squares)

    def backtrack(start_idx: int):
        if max_solutions is not None and len(solutions) >= max_solutions:
            return
        if len(placed) == piece_count:
            solutions.append(list(placed))
            stats.solutions_found += 1
            add_step(
                f"Step {stats.nodes_explored}: Solution #{stats.solutions_found} captured"
            )
            return
        # Pruning: not enough remaining squares to place the rest
        if total_squares - start_idx < piece_count - len(placed):
            return
        for idx in range(start_idx, total_squares):
            if max_solutions is not None and len(solutions) >= max_solutions:
                return
            r, c = all_squares[idx]
            stats.nodes_explored += 1
            conflict = False
            for pr, pc in placed:
                if _attacks(pr, pc, r, c, piece):
                    conflict = True
                    add_step(
                        f"Step {stats.nodes_explored}: Conflict at ({r},{c}) vs ({pr},{pc})"
                    )
                    break
            if conflict:
                continue
            placed.append((r, c))
            add_step(f"Step {stats.nodes_explored}: Place {label} at ({r},{c})")
            backtrack(idx + 1)
            if max_solutions is not None and len(solutions) >= max_solutions:
                return
            placed.pop()
            stats.backtracks += 1
            add_step(f"Step {stats.nodes_explored}: Backtrack from ({r},{c})")

    try:
        backtrack(0)
    except RecursionError:
        logging.exception("Recursion limit hit during fallback solve")

    stats.execution_time_seconds = time.perf_counter() - start

    return SolverResult(
        solutions=solutions,
        steps=steps,
        stats=stats,
        piece_type=piece,
        board_rows=board_rows,
        board_cols=board_cols,
    )


def solve_puzzle(
    piece_type: str,
    board_rows: int,
    board_cols: int,
    piece_count: int,
    max_solutions: Optional[int] = None,
    record_steps: bool = True,
) -> SolverResult:
    if BACKEND_AVAILABLE:
        try:
            r = _real_solve_puzzle(
                piece_type=piece_type,
                board_rows=board_rows,
                board_cols=board_cols,
                piece_count=piece_count,
                max_solutions=max_solutions,
                record_steps=record_steps,
            )
            stats = SolverStats(
                nodes_explored=r.stats.nodes_explored,
                backtracks=r.stats.backtracks,
                solutions_found=r.stats.solutions_found,
                execution_time_seconds=r.stats.execution_time_seconds,
            )
            sols = [[tuple(p) for p in s] for s in r.solutions]
            return SolverResult(
                solutions=sols,
                steps=list(r.steps),
                stats=stats,
                piece_type=str(r.piece_type),
                board_rows=r.board_rows,
                board_cols=r.board_cols,
            )
        except Exception as e:
            logging.exception(f"Real solver failed, falling back: {e}")
    return _fallback_solve(
        piece_type,
        board_rows,
        board_cols,
        piece_count,
        max_solutions,
        record_steps,
    )


# ---------------------------------------------------------------------------
# Sample datasets (inline so they work without uploads/ folder)
# ---------------------------------------------------------------------------
SAMPLES: dict[str, str] = {
    "sample_8queens.txt": (
        "# Classic 8-Queens puzzle\n"
        "BOARD 8 8\n"
        "PIECE QUEEN\n"
        "COUNT 8\n"
        "CONSTRAINT NO_ATTACK\n"
    ),
    "sample_knights.txt": (
        "# Non-attacking knights on a 5x5 board\n"
        "BOARD 5 5\n"
        "PIECE KNIGHT\n"
        "COUNT 9\n"
        "CONSTRAINT NO_ATTACK\n"
    ),
    "sample_bishops.txt": (
        "# Non-attacking bishops on a 6x6 board\n"
        "BOARD 6 6\n"
        "PIECE BISHOP\n"
        "COUNT 6\n"
        "CONSTRAINT NO_ATTACK\n"
    ),
    "sample_rooks.txt": (
        "# Non-attacking rooks on a 6x6 board\n"
        "BOARD 6 6\n"
        "PIECE ROOK\n"
        "COUNT 6\n"
        "CONSTRAINT NO_ATTACK\n"
    ),
}