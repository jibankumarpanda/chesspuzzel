import asyncio
import io
import logging
import re
import reflex as rx

from frontend_code_analysis.backend import solve_puzzle
from frontend_code_analysis.states.history_state import save_run
from frontend_code_analysis.states.puzzle_state import PuzzleState


PIECE_GLYPHS = {
    "QUEEN": "♕",
    "KNIGHT": "♘",
    "BISHOP": "♗",
    "ROOK": "♖",
}


class SolverState(rx.State):
    # Run state
    is_solving: bool = False
    error_msg: str = ""

    # Configuration
    find_all: bool = False
    max_solutions_input: str | int = "10"
    record_steps: bool = True

    # Result
    has_result: bool = False
    solutions: list[list[list[int]]] = []  # list of [[r,c], ...]
    steps: list[str] = []
    nodes_explored: int = 0
    backtracks: int = 0
    solutions_found: int = 0
    execution_time: float = 0.0
    result_piece_type: str = ""
    result_rows: int = 0
    result_cols: int = 0

    # Solution navigator
    current_solution_index: int = 0

    # Step playback
    current_step_index: int = 0
    is_playing: bool = False
    playback_speed_ms: int = 400
    show_step_board: bool = False
    step_boards: list[list[list[int]]] = []

    # ---- Computed ----
    @rx.var
    def total_solutions(self) -> int:
        return len(self.solutions)

    @rx.var
    def solution_label(self) -> str:
        if not self.has_result or self.total_solutions == 0:
            return "No solutions"
        return f"Solution {self.current_solution_index + 1} of {self.total_solutions}"

    @rx.var
    def total_steps(self) -> int:
        return len(self.steps)

    @rx.var
    def current_step_text(self) -> str:
        if self.total_steps == 0:
            return "No steps recorded."
        idx = max(0, min(self.current_step_index, self.total_steps - 1))
        return self.steps[idx]

    @rx.var
    def step_label(self) -> str:
        if self.total_steps == 0:
            return "0 / 0"
        return f"{self.current_step_index + 1} / {self.total_steps}"

    @rx.var
    def current_solution_positions(self) -> list[list[int]]:
        if self.show_step_board and self.step_boards:
            idx = max(0, min(self.current_step_index, len(self.step_boards) - 1))
            return self.step_boards[idx]
        if not self.has_result or self.total_solutions == 0:
            return []
        idx = max(0, min(self.current_solution_index, self.total_solutions - 1))
        return self.solutions[idx]

    @rx.var
    def execution_time_ms(self) -> str:
        return f"{self.execution_time * 1000:.2f} ms"

    @rx.var
    def execution_time_s(self) -> str:
        return f"{self.execution_time:.4f} s"

    @rx.var
    def current_glyph(self) -> str:
        return PIECE_GLYPHS.get(self.result_piece_type.upper(), "●")

    @rx.var
    def board_grid_template(self) -> str:
        cols = self.result_cols if self.result_cols > 0 else 8
        return f"repeat({cols}, minmax(0, 1fr))"

    @rx.var
    def board_squares(self) -> list[dict[str, str | int | bool]]:
        """Pre-computed list of squares for the current board view."""
        rows = self.result_rows
        cols = self.result_cols
        if rows == 0 or cols == 0:
            return []
        positions: set[tuple[int, int]] = set()
        if self.show_step_board and self.step_boards:
            idx = max(0, min(self.current_step_index, len(self.step_boards) - 1))
            for p in self.step_boards[idx]:
                if len(p) >= 2:
                    positions.add((int(p[0]), int(p[1])))
        elif self.has_result and self.total_solutions > 0:
            idx = max(
                0, min(self.current_solution_index, self.total_solutions - 1)
            )
            for p in self.solutions[idx]:
                if len(p) >= 2:
                    positions.add((int(p[0]), int(p[1])))
        out: list[dict[str, str | int | bool]] = []
        for r in range(rows):
            for c in range(cols):
                out.append(
                    {
                        "row": r,
                        "col": c,
                        "is_dark": (r + c) % 2 == 1,
                        "has_piece": (r, c) in positions,
                    }
                )
        return out

    # ---- Performance warning ----
    @rx.var
    async def performance_warning(self) -> str:
        try:
            puzzle = await self.get_state(PuzzleState)
        except Exception:
            logging.exception("Unexpected error")
            return ""
        if not puzzle.has_dataset:
            return ""
        piece = puzzle.piece_type.upper()
        n = max(puzzle.board_rows, puzzle.board_cols)
        if piece in ("KNIGHT", "BISHOP") and n > 6:
            return (
                f"WARNING: Subset search on a {puzzle.board_rows}x{puzzle.board_cols} "
                f"{piece} board can be very slow. Cap 'max solutions' to keep "
                "execution time reasonable."
            )
        if piece in ("QUEEN", "ROOK") and n >= 12 and self.find_all:
            return (
                f"WARNING: Exhaustive search on N={n} for {piece} may take 20+ seconds. "
                "Disable 'Find All' or cap max solutions."
            )
        return ""

    # ---- Setters ----
    @rx.event
    def toggle_find_all(self):
        self.find_all = not self.find_all

    @rx.event
    def toggle_record_steps(self):
        self.record_steps = not self.record_steps

    @rx.event
    def set_max_solutions(self, v: float):
        self.max_solutions_input = str(int(v))

    @rx.event
    def set_speed(self, v: str):
        try:
            self.playback_speed_ms = max(50, int(v))
        except ValueError:
            self.playback_speed_ms = 400

    @rx.event
    def dismiss_error(self):
        self.error_msg = ""

    # ---- Solution navigation ----
    @rx.event
    def next_solution(self):
        if self.total_solutions == 0:
            return
        if self.current_solution_index < self.total_solutions - 1:
            self.current_solution_index += 1

    @rx.event
    def prev_solution(self):
        if self.current_solution_index > 0:
            self.current_solution_index -= 1

    @rx.event
    def go_first_solution(self):
        self.current_solution_index = 0

    @rx.event
    def go_last_solution(self):
        if self.total_solutions > 0:
            self.current_solution_index = self.total_solutions - 1

    # ---- Step playback ----
    @rx.event
    def step_next(self):
        if self.current_step_index < self.total_steps - 1:
            self.current_step_index += 1
            self.show_step_board = True

    @rx.event
    def step_prev(self):
        if self.current_step_index > 0:
            self.current_step_index -= 1
            self.show_step_board = True

    @rx.event
    def step_reset(self):
        self.current_step_index = 0
        self.is_playing = False
        self.show_step_board = True

    @rx.event
    def stop_playback(self):
        self.is_playing = False

    @rx.event(background=True)
    async def play_steps(self):
        async with self:
            if self.total_steps == 0:
                self.is_playing = False
                return
            self.is_playing = True
            self.show_step_board = True
        while True:
            async with self:
                if not self.is_playing:
                    return
                if self.current_step_index >= self.total_steps - 1:
                    self.is_playing = False
                    return
                self.current_step_index += 1
                delay_s = self.playback_speed_ms / 1000.0
            await asyncio.sleep(delay_s)

    # ---- Solver ----
    @rx.event(background=True)
    async def run_solver(self):
        # Snapshot inputs
        async with self:
            self.error_msg = ""
            self.is_solving = True
            self.has_result = False
            puzzle = await self.get_state(PuzzleState)
            piece_type = puzzle.piece_type
            board_rows = puzzle.board_rows
            board_cols = puzzle.board_cols
            piece_count = puzzle.piece_count
            if not puzzle.has_dataset:
                self.error_msg = "No puzzle dataset loaded. Go to Upload first."
                self.is_solving = False
                return
            if self.find_all:
                max_solutions = None
            else:
                try:
                    parsed = int(self.max_solutions_input)
                    max_solutions = max(1, parsed)
                except ValueError:
                    self.error_msg = (
                        "'Max solutions' must be a positive integer."
                    )
                    self.is_solving = False
                    return
            record = self.record_steps

        # Run heavy compute outside the lock
        try:
            result = await asyncio.to_thread(
                solve_puzzle,
                piece_type,
                board_rows,
                board_cols,
                piece_count,
                max_solutions,
                record,
            )
        except Exception as e:
            logging.exception(f"Solver execution failed: {e}")
            async with self:
                self.error_msg = f"Solver error: {e}"
                self.is_solving = False
            return

        # Persist run outside the state lock (sqlite/file IO)
        persist_payload_solutions = [
            [[int(p[0]), int(p[1])] for p in s] for s in result.solutions
        ]
        try:
            await asyncio.to_thread(
                save_run,
                puzzle.filename or "manual_entry.txt",
                result.board_rows,
                result.board_cols,
                result.piece_type,
                puzzle.piece_count,
                puzzle.constraint or "NO_ATTACK",
                persist_payload_solutions,
                list(result.steps),
                float(result.stats.execution_time_seconds),
                int(result.stats.solutions_found),
                int(result.stats.nodes_explored),
                int(result.stats.backtracks),
            )
        except Exception as e:
            logging.exception(f"Persist run failed: {e}")

        async with self:
            self.solutions = persist_payload_solutions
            self.steps = list(result.steps)
            self.step_boards = self._build_step_boards(self.steps)
            self.nodes_explored = result.stats.nodes_explored
            self.backtracks = result.stats.backtracks
            self.solutions_found = result.stats.solutions_found
            self.execution_time = result.stats.execution_time_seconds
            self.result_piece_type = str(result.piece_type)
            self.result_rows = result.board_rows
            self.result_cols = result.board_cols
            self.has_result = True
            self.current_solution_index = 0
            self.current_step_index = 0
            self.is_solving = False
            self.is_playing = False
            self.show_step_board = False

    def _build_step_boards(self, steps: list[str]) -> list[list[list[int]]]:
        positions: list[tuple[int, int]] = []
        boards: list[list[list[int]]] = []
        place_re = re.compile(
            r"^(?:Step\s*\d+\:\s*)?Place\s+\w+\s+at\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)",
            re.IGNORECASE,
        )
        backtrack_from_re = re.compile(
            r"^(?:Step\s*\d+\:\s*)?Backtrack\s+from\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)",
            re.IGNORECASE,
        )
        backtrack_re = re.compile(r"^(?:Step\s*\d+\:\s*)?Backtrack\b", re.IGNORECASE)

        for step in steps:
            if place_match := place_re.match(step):
                r = int(place_match.group(1))
                c = int(place_match.group(2))
                positions.append((r, c))
            elif backtrack_from_re.match(step) or backtrack_re.match(step):
                if positions:
                    positions.pop()
            boards.append([[r, c] for r, c in positions])
        return boards

    # ---- Downloads ----

    @rx.event
    def download_txt(self):
        if not self.has_result or self.total_solutions == 0:
            self.error_msg = "No solution available to download."
            return
        idx = self.current_solution_index
        sol = self.solutions[idx]
        lines = [
            "CHESSLAB PUZZLE SOLVER - SOLUTION EXPORT",
            "=" * 48,
            f"Piece Type    : {self.result_piece_type}",
            f"Board         : {self.result_rows}x{self.result_cols}",
            f"Solution      : {idx + 1} of {self.total_solutions}",
            "",
            "Coordinates (row, col):",
        ]
        for i, p in enumerate(sol, 1):
            lines.append(f"  {i:>3}. ({p[0]}, {p[1]})")
        lines += [
            "",
            "Statistics",
            "-" * 48,
            f"Nodes Explored    : {self.nodes_explored}",
            f"Backtracks        : {self.backtracks}",
            f"Solutions Found   : {self.solutions_found}",
            f"Execution Time    : {self.execution_time:.6f} seconds",
        ]
        return rx.download(
            data="\n".join(lines).encode("utf-8"),
            filename=f"chesslab_solution_{idx + 1}.txt",
        )

    @rx.event
    def download_pdf(self):
        if not self.has_result or self.total_solutions == 0:
            self.error_msg = "No solution available to download."
            return
        try:
            from fpdf import FPDF
        except Exception as e:
            logging.exception(f"fpdf2 not available: {e}")
            self.error_msg = "PDF library (fpdf2) not available."
            return
        try:
            idx = self.current_solution_index
            sol = self.solutions[idx]
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 10, "ChessLab Puzzle Solver - Solution Report", ln=True)
            pdf.set_font("Helvetica", "", 11)
            pdf.cell(0, 7, f"Piece Type: {self.result_piece_type}", ln=True)
            pdf.cell(
                0,
                7,
                f"Board: {self.result_rows} x {self.result_cols}    "
                f"Solution {idx + 1} of {self.total_solutions}",
                ln=True,
            )
            pdf.ln(3)

            # Draw board
            cell = min(15, 160 // max(self.result_cols, 1))
            x0 = pdf.get_x()
            y0 = pdf.get_y()
            positions = {(int(p[0]), int(p[1])) for p in sol}
            for r in range(self.result_rows):
                for c in range(self.result_cols):
                    x = x0 + c * cell
                    y = y0 + r * cell
                    if (r + c) % 2 == 0:
                        pdf.set_fill_color(235, 235, 235)
                    else:
                        pdf.set_fill_color(170, 170, 170)
                    pdf.rect(x, y, cell, cell, "F")
                    if (r, c) in positions:
                        pdf.set_xy(x, y + cell / 4)
                        pdf.set_font("Helvetica", "B", 11)
                        pdf.set_text_color(180, 80, 0)
                        pdf.cell(
                            cell, cell / 2, self.result_piece_type[0], align="C"
                        )
                        pdf.set_text_color(0, 0, 0)
            pdf.set_y(y0 + self.result_rows * cell + 6)

            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 8, "Coordinates", ln=True)
            pdf.set_font("Helvetica", "", 10)
            for i, p in enumerate(sol, 1):
                pdf.cell(0, 5, f"  {i}. (row {p[0]}, col {p[1]})", ln=True)

            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 8, "Statistics", ln=True)
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(0, 5, f"Nodes Explored: {self.nodes_explored}", ln=True)
            pdf.cell(0, 5, f"Backtracks: {self.backtracks}", ln=True)
            pdf.cell(0, 5, f"Solutions Found: {self.solutions_found}", ln=True)
            pdf.cell(
                0, 5, f"Execution Time: {self.execution_time:.6f} s", ln=True
            )

            output = pdf.output(dest="S")
            if isinstance(output, str):
                pdf_bytes = output.encode("latin-1")
            elif isinstance(output, bytearray):
                pdf_bytes = bytes(output)
            else:
                pdf_bytes = output

            return rx.download(
                data=pdf_bytes,
                filename=f"chesslab_solution_{idx + 1}.pdf",
            )
        except Exception as e:
            logging.exception(f"PDF generation failed: {e}")
            self.error_msg = f"PDF generation failed: {e}"
            return