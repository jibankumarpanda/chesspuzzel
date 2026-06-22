import reflex as rx
from frontend_code_analysis.states.puzzle_state import PuzzleState, UPLOAD_ID


def _file_dropzone() -> rx.Component:
    return rx.el.div(
        rx.upload.root(
            rx.el.div(
                rx.icon(
                    "cloud_upload",
                    class_name="h-10 w-10 text-zinc-600 mx-auto mb-3",
                ),
                rx.el.p(
                    "DROP .TXT DATASET FILE HERE",
                    class_name="font-mono text-xs text-zinc-300 font-semibold tracking-wider",
                ),
                rx.el.p(
                    "or click to browse",
                    class_name="font-mono text-[10px] text-zinc-500 mt-1",
                ),
                rx.el.p(
                    "Required: BOARD, PIECE, COUNT, CONSTRAINT",
                    class_name="font-mono text-[10px] text-zinc-600 mt-3",
                ),
                class_name="border-2 border-dashed border-zinc-800 rounded-xl p-10 text-center cursor-pointer bg-zinc-950 hover:bg-zinc-900 hover:border-amber-500/40 transition-all duration-200",
            ),
            id=UPLOAD_ID,
            accept={"text/plain": [".txt"]},
            multiple=False,
            max_files=1,
            on_drop=PuzzleState.handle_upload(
                rx.upload_files(upload_id=UPLOAD_ID)
            ),
        ),
        rx.el.div(
            rx.foreach(
                rx.selected_files(UPLOAD_ID),
                lambda f: rx.el.p(
                    f, class_name="font-mono text-[11px] text-zinc-400 mt-2"
                ),
            ),
            class_name="mt-2",
        ),
    )


def _sample_button(name: str) -> rx.Component:
    return rx.el.button(
        rx.icon("file-text", class_name="h-3.5 w-3.5"),
        rx.el.span(name, class_name="font-mono text-[11px] truncate"),
        on_click=lambda: PuzzleState.load_sample(name),
        class_name="flex items-center gap-2 px-3 py-2 bg-zinc-900 border border-zinc-800 hover:border-amber-500/40 hover:bg-zinc-900/80 text-zinc-300 hover:text-amber-400 rounded-md transition-colors w-full",
    )


def _samples_card() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("library", class_name="h-5 w-5 text-amber-500"),
            rx.el.h3(
                "Sample Datasets",
                class_name="font-mono text-sm font-bold text-zinc-200 uppercase tracking-wider",
            ),
            class_name="flex items-center gap-2 mb-3",
        ),
        rx.el.p(
            "Load curated benchmark configurations.",
            class_name="text-[11px] text-zinc-500 mb-4 font-mono",
        ),
        rx.el.div(
            rx.foreach(PuzzleState.sample_names, _sample_button),
            class_name="flex flex-col gap-2",
        ),
        class_name="bg-zinc-950 border border-zinc-900 p-5 rounded-xl",
    )


def _select_field(
    label: str, value, on_change, options: list[str]
) -> rx.Component:
    return rx.el.div(
        rx.el.label(
            label,
            class_name="font-mono text-[11px] text-zinc-500 uppercase tracking-wider font-bold mb-1.5 block",
        ),
        rx.el.div(
            rx.el.select(
                rx.foreach(
                    options,
                    lambda o: rx.el.option(o, value=o),
                ),
                value=value,
                on_change=on_change,
                class_name="appearance-none w-full bg-zinc-900 border border-zinc-800 rounded-md px-3 py-2 pr-9 font-mono text-xs text-zinc-200 focus:outline-none focus:border-amber-500/60",
            ),
            rx.icon(
                "chevron-down",
                class_name="absolute right-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-500 pointer-events-none",
            ),
            class_name="relative",
        ),
    )


def _input_field(
    label: str, value, on_change, placeholder: str = ""
) -> rx.Component:
    return rx.el.div(
        rx.el.label(
            label,
            class_name="font-mono text-[11px] text-zinc-500 uppercase tracking-wider font-bold mb-1.5 block",
        ),
        rx.el.input(
            default_value=value,
            on_change=on_change.debounce(300),
            placeholder=placeholder,
            class_name="w-full bg-zinc-900 border border-zinc-800 rounded-md px-3 py-2 font-mono text-xs text-zinc-200 placeholder:text-zinc-600 focus:outline-none focus:border-amber-500/60",
        ),
    )


def _manual_form() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("pencil-line", class_name="h-5 w-5 text-amber-500"),
            rx.el.h3(
                "Manual Configuration",
                class_name="font-mono text-sm font-bold text-zinc-200 uppercase tracking-wider",
            ),
            class_name="flex items-center gap-2 mb-3",
        ),
        rx.el.p(
            "Bypass file upload and validate input via the same parser pipeline.",
            class_name="text-[11px] text-zinc-500 mb-4 font-mono",
        ),
        rx.el.div(
            _input_field(
                "Board Rows",
                PuzzleState.manual_rows,
                PuzzleState.set_manual_rows,
                "8",
            ),
            _input_field(
                "Board Cols",
                PuzzleState.manual_cols,
                PuzzleState.set_manual_cols,
                "8",
            ),
            class_name="grid grid-cols-2 gap-3",
        ),
        rx.el.div(
            _select_field(
                "Piece Type",
                PuzzleState.manual_piece,
                PuzzleState.set_manual_piece,
                PuzzleState.available_pieces,
            ),
            _input_field(
                "Piece Count",
                PuzzleState.manual_count,
                PuzzleState.set_manual_count,
                "8",
            ),
            class_name="grid grid-cols-2 gap-3 mt-3",
        ),
        rx.el.div(
            _select_field(
                "Constraint",
                PuzzleState.manual_constraint,
                PuzzleState.set_manual_constraint,
                PuzzleState.available_constraints,
            ),
            class_name="mt-3",
        ),
        rx.el.button(
            rx.icon("zap", class_name="h-4 w-4"),
            rx.el.span(
                "VALIDATE & LOAD",
                class_name="font-mono text-xs tracking-widest",
            ),
            on_click=PuzzleState.submit_manual,
            class_name="flex items-center justify-center gap-2 mt-5 w-full py-2.5 bg-amber-500/10 border border-amber-500/40 text-amber-400 hover:bg-amber-500/20 rounded-md uppercase font-bold transition-colors",
        ),
        class_name="bg-zinc-950 border border-zinc-900 p-5 rounded-xl",
    )


def _summary_row(label: str, value) -> rx.Component:
    return rx.el.div(
        rx.el.span(
            label,
            class_name="font-mono text-[11px] text-zinc-500 uppercase tracking-wider",
        ),
        rx.el.span(
            value,
            class_name="font-mono text-xs text-zinc-200 font-bold",
        ),
        class_name="flex justify-between py-2 border-b border-zinc-900 last:border-b-0",
    )


def _dataset_summary() -> rx.Component:
    return rx.cond(
        PuzzleState.has_dataset,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon(
                        "circle-check", class_name="h-5 w-5 text-emerald-400"
                    ),
                    rx.el.h3(
                        "Dataset Loaded",
                        class_name="font-mono text-sm font-bold text-zinc-200 uppercase tracking-wider",
                    ),
                    class_name="flex items-center gap-2",
                ),
                rx.el.button(
                    rx.icon("x", class_name="h-4 w-4"),
                    on_click=PuzzleState.clear_dataset,
                    class_name="text-zinc-500 hover:text-zinc-300 transition-colors",
                ),
                class_name="flex items-center justify-between mb-3",
            ),
            rx.el.p(
                PuzzleState.summary_line,
                class_name="font-mono text-[11px] text-amber-400/80 mb-3 break-all",
            ),
            rx.el.div(
                _summary_row("Filename", PuzzleState.filename),
                _summary_row(
                    "Board",
                    PuzzleState.board_rows.to_string()
                    + " x "
                    + PuzzleState.board_cols.to_string(),
                ),
                _summary_row("Piece Type", PuzzleState.piece_type),
                _summary_row(
                    "Piece Count", PuzzleState.piece_count.to_string()
                ),
                _summary_row("Constraint", PuzzleState.constraint),
                class_name="bg-zinc-900/40 border border-zinc-900 rounded-lg px-4 py-2 mb-4",
            ),
            rx.el.button(
                rx.icon("cpu", class_name="h-4 w-4"),
                rx.el.span(
                    "SOLVE THIS PUZZLE",
                    class_name="font-mono text-xs tracking-widest",
                ),
                on_click=PuzzleState.go_to_solver,
                class_name="flex items-center justify-center gap-2 w-full py-3 bg-amber-500 hover:bg-amber-400 text-zinc-950 rounded-md uppercase font-bold transition-colors",
            ),
            class_name="bg-zinc-950 border border-amber-500/30 p-5 rounded-xl",
        ),
        rx.el.div(
            rx.icon(
                "inbox",
                class_name="h-8 w-8 text-zinc-700 mx-auto mb-2",
            ),
            rx.el.p(
                "NO DATASET LOADED",
                class_name="font-mono text-[11px] text-zinc-500 tracking-widest text-center font-bold",
            ),
            rx.el.p(
                "Upload a file, load a sample, or fill the manual form.",
                class_name="font-mono text-[10px] text-zinc-600 text-center mt-1",
            ),
            class_name="bg-zinc-950 border border-zinc-900 border-dashed p-8 rounded-xl",
        ),
    )


def _backend_banner() -> rx.Component:
    return rx.cond(
        PuzzleState.backend_available,
        rx.el.div(
            rx.icon(
                "circle-check", class_name="h-4 w-4 text-emerald-400 shrink-0"
            ),
            rx.el.p(
                PuzzleState.backend_note,
                class_name="font-mono text-[11px] text-emerald-400/90",
            ),
            class_name="flex items-center gap-2 px-3 py-2 bg-emerald-500/5 border border-emerald-500/20 rounded-md mb-4",
        ),
        rx.el.div(
            rx.icon(
                "triangle-alert",
                class_name="h-4 w-4 text-amber-400 shrink-0 mt-0.5",
            ),
            rx.el.p(
                PuzzleState.backend_note,
                class_name="font-mono text-[11px] text-amber-400/90 leading-relaxed",
            ),
            class_name="flex items-start gap-2 px-3 py-2 bg-amber-500/5 border border-amber-500/20 rounded-md mb-4",
        ),
    )


def _alert_banners() -> rx.Component:
    return rx.el.div(
        rx.cond(
            PuzzleState.parse_error != "",
            rx.el.div(
                rx.icon(
                    "octagon_alert", class_name="h-5 w-5 text-red-500 shrink-0"
                ),
                rx.el.div(
                    rx.el.p(
                        "PARSER REJECTED INPUT",
                        class_name="font-mono text-[11px] font-bold text-red-500 uppercase tracking-widest",
                    ),
                    rx.el.p(
                        PuzzleState.parse_error,
                        class_name="font-mono text-xs text-zinc-300 mt-1",
                    ),
                    class_name="flex-1",
                ),
                rx.el.button(
                    rx.icon("x", class_name="h-4 w-4"),
                    on_click=PuzzleState.dismiss_error,
                    class_name="text-red-400 hover:text-red-300",
                ),
                class_name="flex gap-3 items-start p-4 bg-red-950/30 border border-red-500/30 rounded-lg w-full mb-3",
            ),
        ),
        rx.cond(
            PuzzleState.success_msg != "",
            rx.el.div(
                rx.icon(
                    "circle-check",
                    class_name="h-5 w-5 text-emerald-400 shrink-0",
                ),
                rx.el.p(
                    PuzzleState.success_msg,
                    class_name="font-mono text-xs text-emerald-300 flex-1",
                ),
                rx.el.button(
                    rx.icon("x", class_name="h-4 w-4"),
                    on_click=PuzzleState.dismiss_success,
                    class_name="text-emerald-400/70 hover:text-emerald-300",
                ),
                class_name="flex gap-3 items-center p-3 bg-emerald-950/20 border border-emerald-500/30 rounded-lg w-full mb-3",
            ),
        ),
    )


def upload_page_content() -> rx.Component:
    return rx.el.div(
        rx.el.span(
            "DATASET LOADER",
            class_name="text-xs font-mono tracking-widest text-amber-500 bg-amber-500/10 px-2.5 py-1 rounded border border-amber-500/20 uppercase font-semibold",
        ),
        rx.el.h1(
            "Upload Puzzle",
            class_name="text-4xl font-bold tracking-tight text-zinc-100 font-mono mt-3 uppercase",
        ),
        rx.el.p(
            "Upload a .txt configuration, load a sample benchmark, or hand-craft a puzzle. All inputs flow through the parser for validation.",
            class_name="text-zinc-400 mt-2 text-sm leading-relaxed mb-6 max-w-2xl",
        ),
        _backend_banner(),
        _alert_banners(),
        rx.el.div(
            # Left: Upload + samples
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon("upload", class_name="h-5 w-5 text-amber-500"),
                        rx.el.h3(
                            "File Upload",
                            class_name="font-mono text-sm font-bold text-zinc-200 uppercase tracking-wider",
                        ),
                        class_name="flex items-center gap-2 mb-3",
                    ),
                    _file_dropzone(),
                    class_name="bg-zinc-950 border border-zinc-900 p-5 rounded-xl mb-6",
                ),
                _samples_card(),
                class_name="flex flex-col gap-0 w-full lg:w-1/2",
            ),
            # Middle: Manual form
            rx.el.div(
                _manual_form(),
                class_name="w-full lg:w-1/2",
            ),
            class_name="flex flex-col lg:flex-row gap-6 mb-6",
        ),
        _dataset_summary(),
    )