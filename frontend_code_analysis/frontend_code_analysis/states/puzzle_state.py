import logging
import reflex as rx

from frontend_code_analysis.backend import (
    BACKEND_AVAILABLE,
    BACKEND_NOTE,
    DatasetParseError,
    PuzzleDataset,
    SAMPLES,
    VALID_CONSTRAINTS,
    VALID_PIECES,
    parse_dataset_text,
)


UPLOAD_ID = "puzzle_dataset_upload"


class PuzzleState(rx.State):
    """Holds the currently loaded PuzzleDataset and upload-page UI state."""

    has_dataset: bool = False
    board_rows: int = 0
    board_cols: int = 0
    piece_type: str = ""
    piece_count: int = 0
    constraint: str = ""
    raw_text: str = ""
    filename: str = ""

    parse_error: str = ""
    success_msg: str = ""
    backend_note: str = BACKEND_NOTE
    backend_available: bool = BACKEND_AVAILABLE

    # Manual entry form
    manual_rows: str = "8"
    manual_cols: str = "8"
    manual_piece: str = "QUEEN"
    manual_count: str = "8"
    manual_constraint: str = "NO_ATTACK"

    available_pieces: list[str] = list(VALID_PIECES)
    available_constraints: list[str] = list(VALID_CONSTRAINTS)
    sample_names: list[str] = list(SAMPLES.keys())

    @rx.var
    def summary_line(self) -> str:
        if not self.has_dataset:
            return ""
        return (
            f"{self.filename} :: {self.board_rows}x{self.board_cols} board, "
            f"{self.piece_count} {self.piece_type}(S), constraint={self.constraint}"
        )

    def _apply_dataset(self, ds: PuzzleDataset, success_msg: str = ""):
        self.has_dataset = True
        self.board_rows = ds.board_rows
        self.board_cols = ds.board_cols
        self.piece_type = ds.piece_type
        self.piece_count = ds.piece_count
        self.constraint = ds.constraint
        self.raw_text = ds.raw_text
        self.filename = ds.filename
        self.parse_error = ""
        self.success_msg = (
            success_msg or f"Dataset '{ds.filename}' loaded successfully."
        )

    @rx.event
    def clear_dataset(self):
        self.has_dataset = False
        self.board_rows = 0
        self.board_cols = 0
        self.piece_type = ""
        self.piece_count = 0
        self.constraint = ""
        self.raw_text = ""
        self.filename = ""
        self.parse_error = ""
        self.success_msg = ""

    @rx.event
    def dismiss_error(self):
        self.parse_error = ""

    @rx.event
    def dismiss_success(self):
        self.success_msg = ""

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        if not files:
            return
        try:
            file = files[0]
            data = await file.read()
            text = data.decode("utf-8", errors="replace")
            ds = parse_dataset_text(text, filename=file.name)
            self._apply_dataset(ds, f"Uploaded and parsed '{file.name}'.")
        except DatasetParseError as e:
            logging.exception("Unexpected error")
            self.parse_error = str(e)
            self.success_msg = ""
        except Exception as e:
            logging.exception(f"Unexpected upload error: {e}")
            self.parse_error = f"Unexpected error reading file: {e}"
            self.success_msg = ""

    @rx.event
    def load_sample(self, sample_name: str):
        try:
            text = SAMPLES.get(sample_name)
            if text is None:
                self.parse_error = f"Sample '{sample_name}' not found."
                return
            ds = parse_dataset_text(text, filename=sample_name)
            self._apply_dataset(ds, f"Sample '{sample_name}' loaded.")
        except DatasetParseError as e:
            logging.exception("Unexpected error")
            self.parse_error = str(e)
        except Exception as e:
            logging.exception(f"Sample load error: {e}")
            self.parse_error = f"Failed to load sample: {e}"

    # Manual form setters
    @rx.event
    def set_manual_rows(self, v: str):
        self.manual_rows = v

    @rx.event
    def set_manual_cols(self, v: str):
        self.manual_cols = v

    @rx.event
    def set_manual_piece(self, v: str):
        self.manual_piece = v

    @rx.event
    def set_manual_count(self, v: str):
        self.manual_count = v

    @rx.event
    def set_manual_constraint(self, v: str):
        self.manual_constraint = v

    @rx.event
    def submit_manual(self):
        try:
            text = (
                f"BOARD {self.manual_rows} {self.manual_cols}\n"
                f"PIECE {self.manual_piece}\n"
                f"COUNT {self.manual_count}\n"
                f"CONSTRAINT {self.manual_constraint}\n"
            )
            ds = parse_dataset_text(text, filename="manual_entry.txt")
            self._apply_dataset(
                ds, "Manual configuration validated and loaded."
            )
        except DatasetParseError as e:
            logging.exception("Unexpected error")
            self.parse_error = str(e)
            self.success_msg = ""
        except Exception as e:
            logging.exception(f"Manual entry error: {e}")
            self.parse_error = f"Unexpected error: {e}"

    @rx.event
    def go_to_solver(self):
        return rx.redirect("/solve")