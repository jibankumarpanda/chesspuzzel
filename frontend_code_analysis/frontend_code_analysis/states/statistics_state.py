import logging
from typing import TypedDict

import reflex as rx

from frontend_code_analysis.states.history_state import (
    DB_AVAILABLE,
    DB_NOTE,
    all_solutions,
    list_puzzles,
)


class TimeChartPoint(TypedDict):
    label: str
    execution_ms: float
    nodes: int


class PieceBreakdownPoint(TypedDict):
    piece: str
    count: int
    fill: str


PIECE_COLORS = {
    "QUEEN": "#f59e0b",
    "KNIGHT": "#10b981",
    "BISHOP": "#3b82f6",
    "ROOK": "#a855f7",
}


class StatisticsState(rx.State):
    db_available: bool = DB_AVAILABLE
    db_note: str = DB_NOTE

    is_loading: bool = False
    error_msg: str = ""

    total_puzzles: int = 0
    total_solutions: int = 0
    total_nodes: int = 0
    total_backtracks: int = 0
    avg_execution_time: float = 0.0
    fastest_time: float = 0.0
    slowest_time: float = 0.0

    time_chart: list[TimeChartPoint] = []
    piece_breakdown: list[PieceBreakdownPoint] = []

    @rx.var
    def has_data(self) -> bool:
        return self.total_puzzles > 0

    @rx.var
    def avg_time_ms(self) -> str:
        return f"{self.avg_execution_time * 1000:.2f} ms"

    @rx.var
    def fastest_time_ms(self) -> str:
        return f"{self.fastest_time * 1000:.2f} ms"

    @rx.var
    def slowest_time_ms(self) -> str:
        return f"{self.slowest_time * 1000:.2f} ms"

    @rx.event
    def load(self):
        try:
            self.is_loading = True
            self.error_msg = ""
            puzzles = list_puzzles("")
            sols = all_solutions()

            self.total_puzzles = len(puzzles)
            self.total_solutions = sum(int(s["solution_count"]) for s in sols)
            self.total_nodes = sum(int(s["nodes_explored"]) for s in sols)
            self.total_backtracks = sum(int(s["backtracks"]) for s in sols)

            times = [float(s["execution_time"]) for s in sols if s]
            if times:
                self.avg_execution_time = sum(times) / len(times)
                self.fastest_time = min(times)
                self.slowest_time = max(times)
            else:
                self.avg_execution_time = 0.0
                self.fastest_time = 0.0
                self.slowest_time = 0.0

            # Time chart - join puzzles with their latest solutions in order
            puzzles_by_id: dict[int, dict] = {int(p["id"]): p for p in puzzles}
            sorted_sols = sorted(sols, key=lambda s: int(s["id"]))
            chart: list[TimeChartPoint] = []
            for s in sorted_sols[-30:]:
                pid = int(s["puzzle_id"])
                p = puzzles_by_id.get(pid)
                if p is None:
                    label = f"#{pid}"
                else:
                    label = f"#{pid} {str(p['piece_type'])[:1]}"
                chart.append(
                    TimeChartPoint(
                        label=label,
                        execution_ms=round(
                            float(s["execution_time"]) * 1000, 3
                        ),
                        nodes=int(s["nodes_explored"]),
                    )
                )
            self.time_chart = chart

            # Piece breakdown
            counts: dict[str, int] = {}
            for p in puzzles:
                key = str(p["piece_type"]).upper()
                counts[key] = counts.get(key, 0) + 1
            breakdown: list[PieceBreakdownPoint] = []
            for piece in ("QUEEN", "KNIGHT", "BISHOP", "ROOK"):
                breakdown.append(
                    PieceBreakdownPoint(
                        piece=piece,
                        count=counts.get(piece, 0),
                        fill=PIECE_COLORS.get(piece, "#f59e0b"),
                    )
                )
            self.piece_breakdown = breakdown
        except Exception as e:
            logging.exception(f"Statistics load error: {e}")
            self.error_msg = "Failed to load aggregate statistics."
        finally:
            self.is_loading = False

    @rx.event
    def dismiss_error(self):
        self.error_msg = ""