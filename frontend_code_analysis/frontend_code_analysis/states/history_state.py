import json
import logging
import time
from pathlib import Path
from typing import TypedDict

import reflex as rx


# Try real database backend
DB_AVAILABLE = False
DB_NOTE = ""

try:
    from database.db import (  # type: ignore
        init_db as _real_init_db,
        insert_puzzle as _real_insert_puzzle,
        get_all_puzzles as _real_get_all_puzzles,
        search_puzzles as _real_search_puzzles,
        delete_puzzle as _real_delete_puzzle,
        insert_solution as _real_insert_solution,
        get_solutions_for_puzzle as _real_get_solutions_for_puzzle,
        get_latest_solution_for_puzzle as _real_get_latest_solution_for_puzzle,
        serialize_solution_payload as _real_serialize_solution_payload,
        deserialize_solution_payload as _real_deserialize_solution_payload,
    )
    from database.models import Puzzle as _RealPuzzle, Solution as _RealSolution  # type: ignore

    DB_AVAILABLE = True
    DB_NOTE = "Connected to project SQLite database via database.db API."
except ImportError:
    # This is expected when backend SQLite is not physical. We fall back without logging a traceback.
    DB_AVAILABLE = False
    DB_NOTE = (
        "SQLite backend (database.db) not detected. Using safe local JSON "
        "fallback store for puzzle history. To enable persistent SQLite, "
        "place the project's database/ package next to this Reflex app."
    )
except Exception:
    logging.exception("Unexpected error")
    DB_AVAILABLE = False
    DB_NOTE = (
        "SQLite backend (database.db) not detected. Using safe local JSON "
        "fallback store for puzzle history. To enable persistent SQLite, "
        "place the project's database/ package next to this Reflex app."
    )


_FALLBACK_FILE_NAME = "_chesslab_history_fallback.json"


def _fallback_store_path() -> Path:
    base = Path(rx.get_upload_dir())
    base.mkdir(parents=True, exist_ok=True)
    return base / _FALLBACK_FILE_NAME


def _load_fallback() -> dict:
    p = _fallback_store_path()
    if not p.exists():
        return {"puzzles": [], "solutions": [], "next_pid": 1, "next_sid": 1}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        logging.exception("Failed to load fallback history store")
        return {"puzzles": [], "solutions": [], "next_pid": 1, "next_sid": 1}


def _save_fallback(data: dict) -> None:
    p = _fallback_store_path()
    p.write_text(json.dumps(data), encoding="utf-8")


def _now_iso() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


class PuzzleRow(TypedDict):
    id: int
    filename: str
    board_size: str
    piece_type: str
    piece_count: int
    constraint: str
    created_at: str


class SolutionRow(TypedDict):
    id: int
    puzzle_id: int
    solution_data: str
    execution_time: float
    solution_count: int
    nodes_explored: int
    backtracks: int
    created_at: str


def init_history() -> None:
    if DB_AVAILABLE:
        try:
            _real_init_db()
        except Exception:
            logging.exception("Failed to init real db")
    else:
        # touch fallback file
        _save_fallback(_load_fallback())


def save_run(
    filename: str,
    board_rows: int,
    board_cols: int,
    piece_type: str,
    piece_count: int,
    constraint: str,
    solutions: list[list[list[int]]],
    steps: list[str],
    execution_time: float,
    solution_count: int,
    nodes_explored: int,
    backtracks: int,
) -> int:
    """Persist a solve run. Returns puzzle_id."""
    board_size = f"{board_rows}x{board_cols}"
    if DB_AVAILABLE:
        try:
            puzzle = _RealPuzzle(  # type: ignore
                id=None,
                filename=filename,
                board_size=board_size,
                piece_type=piece_type,
                piece_count=piece_count,
                constraint=constraint,
                created_at=_now_iso(),
            )
            puzzle_id = _real_insert_puzzle(puzzle)
            payload = _real_serialize_solution_payload(solutions, steps)
            solution = _RealSolution(  # type: ignore
                id=None,
                puzzle_id=puzzle_id,
                solution_data=payload,
                execution_time=float(execution_time),
                solution_count=int(solution_count),
                nodes_explored=int(nodes_explored),
                backtracks=int(backtracks),
                created_at=_now_iso(),
            )
            _real_insert_solution(solution)
            return puzzle_id
        except Exception:
            logging.exception("Real DB save failed; falling back")

    data = _load_fallback()
    pid = int(data["next_pid"])
    sid = int(data["next_sid"])
    data["puzzles"].append(
        {
            "id": pid,
            "filename": filename,
            "board_size": board_size,
            "piece_type": piece_type,
            "piece_count": piece_count,
            "constraint": constraint,
            "created_at": _now_iso(),
        }
    )
    data["solutions"].append(
        {
            "id": sid,
            "puzzle_id": pid,
            "solution_data": json.dumps(
                {"solutions": solutions, "steps": steps}
            ),
            "execution_time": float(execution_time),
            "solution_count": int(solution_count),
            "nodes_explored": int(nodes_explored),
            "backtracks": int(backtracks),
            "created_at": _now_iso(),
        }
    )
    data["next_pid"] = pid + 1
    data["next_sid"] = sid + 1
    _save_fallback(data)
    return pid


def list_puzzles(query: str = "") -> list[PuzzleRow]:
    if DB_AVAILABLE:
        try:
            if query.strip():
                rows = _real_search_puzzles(query.strip())
            else:
                rows = _real_get_all_puzzles()
            out: list[PuzzleRow] = []
            for r in rows:
                out.append(
                    PuzzleRow(
                        id=int(r.id) if r.id is not None else 0,
                        filename=str(r.filename),
                        board_size=str(r.board_size),
                        piece_type=str(r.piece_type),
                        piece_count=int(r.piece_count),
                        constraint=str(r.constraint),
                        created_at=str(r.created_at),
                    )
                )
            return out
        except Exception:
            logging.exception("Real DB list failed; using fallback")

    data = _load_fallback()
    rows = list(data["puzzles"])
    if query.strip():
        q = query.strip().lower()
        rows = [
            r
            for r in rows
            if q in str(r.get("filename", "")).lower()
            or q in str(r.get("piece_type", "")).lower()
            or q in str(r.get("constraint", "")).lower()
            or q in str(r.get("board_size", "")).lower()
        ]
    rows.sort(key=lambda r: int(r.get("id", 0)), reverse=True)
    return [
        PuzzleRow(
            id=int(r["id"]),
            filename=str(r["filename"]),
            board_size=str(r["board_size"]),
            piece_type=str(r["piece_type"]),
            piece_count=int(r["piece_count"]),
            constraint=str(r["constraint"]),
            created_at=str(r["created_at"]),
        )
        for r in rows
    ]


def latest_solution(puzzle_id: int) -> SolutionRow | None:
    if DB_AVAILABLE:
        try:
            sol = _real_get_latest_solution_for_puzzle(puzzle_id)
            if sol is None:
                return None
            return SolutionRow(
                id=int(sol.id) if sol.id is not None else 0,
                puzzle_id=int(sol.puzzle_id),
                solution_data=str(sol.solution_data),
                execution_time=float(sol.execution_time),
                solution_count=int(sol.solution_count),
                nodes_explored=int(sol.nodes_explored),
                backtracks=int(sol.backtracks),
                created_at=str(sol.created_at),
            )
        except Exception:
            logging.exception("Real DB latest_solution failed; using fallback")

    data = _load_fallback()
    sols = [s for s in data["solutions"] if int(s["puzzle_id"]) == puzzle_id]
    if not sols:
        return None
    sols.sort(key=lambda s: int(s["id"]), reverse=True)
    s = sols[0]
    return SolutionRow(
        id=int(s["id"]),
        puzzle_id=int(s["puzzle_id"]),
        solution_data=str(s["solution_data"]),
        execution_time=float(s["execution_time"]),
        solution_count=int(s["solution_count"]),
        nodes_explored=int(s["nodes_explored"]),
        backtracks=int(s["backtracks"]),
        created_at=str(s["created_at"]),
    )


def all_solutions() -> list[SolutionRow]:
    """Return all solutions (used for stats)."""
    if DB_AVAILABLE:
        try:
            puzzles = _real_get_all_puzzles()
            out: list[SolutionRow] = []
            for p in puzzles:
                if p.id is None:
                    continue
                sols = _real_get_solutions_for_puzzle(p.id)
                for s in sols:
                    out.append(
                        SolutionRow(
                            id=int(s.id) if s.id is not None else 0,
                            puzzle_id=int(s.puzzle_id),
                            solution_data=str(s.solution_data),
                            execution_time=float(s.execution_time),
                            solution_count=int(s.solution_count),
                            nodes_explored=int(s.nodes_explored),
                            backtracks=int(s.backtracks),
                            created_at=str(s.created_at),
                        )
                    )
            return out
        except Exception:
            logging.exception("Real DB all_solutions failed; using fallback")

    data = _load_fallback()
    return [
        SolutionRow(
            id=int(s["id"]),
            puzzle_id=int(s["puzzle_id"]),
            solution_data=str(s["solution_data"]),
            execution_time=float(s["execution_time"]),
            solution_count=int(s["solution_count"]),
            nodes_explored=int(s["nodes_explored"]),
            backtracks=int(s["backtracks"]),
            created_at=str(s["created_at"]),
        )
        for s in data["solutions"]
    ]


def delete_puzzle_record(puzzle_id: int) -> None:
    if DB_AVAILABLE:
        try:
            _real_delete_puzzle(puzzle_id)
            return
        except Exception:
            logging.exception("Real DB delete failed; using fallback")
    data = _load_fallback()
    data["puzzles"] = [p for p in data["puzzles"] if int(p["id"]) != puzzle_id]
    data["solutions"] = [
        s for s in data["solutions"] if int(s["puzzle_id"]) != puzzle_id
    ]
    _save_fallback(data)


def deserialize_payload(payload: str) -> dict:
    if DB_AVAILABLE:
        try:
            return _real_deserialize_solution_payload(payload)
        except Exception:
            logging.exception("Real deserialize failed; using fallback")
    try:
        return json.loads(payload)
    except Exception:
        logging.exception("Fallback deserialize failed")
        return {"solutions": [], "steps": []}


# ---------------------------------------------------------------------------
# Reflex State
# ---------------------------------------------------------------------------


class HistoryState(rx.State):
    db_available: bool = DB_AVAILABLE
    db_note: str = DB_NOTE

    search_query: str = ""
    rows: list[PuzzleRow] = []
    error_msg: str = ""
    success_msg: str = ""

    confirm_delete_id: int = 0
    confirm_delete_name: str = ""

    is_loading: bool = False

    @rx.var
    def total_rows(self) -> int:
        return len(self.rows)

    @rx.event
    def set_search(self, value: str):
        self.search_query = value
        self._refresh()

    @rx.event
    def refresh(self):
        self._refresh()

    def _refresh(self):
        try:
            self.is_loading = True
            self.rows = list_puzzles(self.search_query)
            self.error_msg = ""
        except Exception as e:
            logging.exception(f"History refresh error: {e}")
            self.error_msg = "Failed to load puzzle history. Persistent store may be unavailable."
        finally:
            self.is_loading = False

    @rx.event
    def request_delete(self, puzzle_id: int, label: str):
        self.confirm_delete_id = puzzle_id
        self.confirm_delete_name = label

    @rx.event
    def cancel_delete(self):
        self.confirm_delete_id = 0
        self.confirm_delete_name = ""

    @rx.event
    def confirm_delete(self):
        pid = self.confirm_delete_id
        if pid <= 0:
            return
        try:
            delete_puzzle_record(pid)
            self.success_msg = f"Puzzle #{pid} deleted from history."
            self.confirm_delete_id = 0
            self.confirm_delete_name = ""
            self._refresh()
        except Exception as e:
            logging.exception(f"Delete error: {e}")
            self.error_msg = "Failed to delete puzzle from history."

    @rx.event
    def dismiss_error(self):
        self.error_msg = ""

    @rx.event
    def dismiss_success(self):
        self.success_msg = ""

    @rx.event
    async def reopen_puzzle(self, puzzle_id: int):
        """Load puzzle and its latest solution into solver state then redirect."""
        try:
            row = next(
                (r for r in self.rows if int(r["id"]) == puzzle_id), None
            )
            if row is None:
                self.error_msg = "Puzzle record not found."
                return
            sol = latest_solution(puzzle_id)
            if sol is None:
                self.error_msg = "No solution recorded for this puzzle."
                return
            payload = deserialize_payload(sol["solution_data"])
            solutions = payload.get("solutions", []) or []
            steps = payload.get("steps", []) or []

            # Parse board size
            board_size = str(row["board_size"])
            try:
                br_str, bc_str = board_size.lower().split("x")
                br, bc = int(br_str), int(bc_str)
            except Exception:
                logging.exception("Unexpected error")
                br, bc = 8, 8

            # Update PuzzleState
            from frontend_code_analysis.states.puzzle_state import PuzzleState
            from frontend_code_analysis.states.solver_state import SolverState

            puzzle = await self.get_state(PuzzleState)
            puzzle.has_dataset = True
            puzzle.filename = str(row["filename"])
            puzzle.board_rows = br
            puzzle.board_cols = bc
            puzzle.piece_type = str(row["piece_type"])
            puzzle.piece_count = int(row["piece_count"])
            puzzle.constraint = str(row["constraint"])
            puzzle.raw_text = ""
            puzzle.parse_error = ""
            puzzle.success_msg = f"Loaded historical puzzle #{puzzle_id}."

            # Update SolverState with the historical result
            solver = await self.get_state(SolverState)
            solver.solutions = [
                [[int(p[0]), int(p[1])] for p in s] for s in solutions
            ]
            solver.steps = list(steps)
            solver.nodes_explored = int(sol["nodes_explored"])
            solver.backtracks = int(sol["backtracks"])
            solver.solutions_found = int(sol["solution_count"])
            solver.execution_time = float(sol["execution_time"])
            solver.result_piece_type = str(row["piece_type"])
            solver.result_rows = br
            solver.result_cols = bc
            solver.has_result = True
            solver.current_solution_index = 0
            solver.current_step_index = 0
            solver.is_playing = False
            solver.is_solving = False
            solver.error_msg = ""

            return rx.redirect("/solve")
        except Exception as e:
            logging.exception(f"Reopen puzzle failed: {e}")
            self.error_msg = "Failed to reopen historical puzzle."