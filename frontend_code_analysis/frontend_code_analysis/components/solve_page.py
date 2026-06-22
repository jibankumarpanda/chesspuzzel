import reflex as rx
from frontend_code_analysis.states.puzzle_state import PuzzleState
from frontend_code_analysis.states.solver_state import SolverState
from frontend_code_analysis.components.chessboard import chessboard


def _stat_card(label: str, value, accent: bool = False) -> rx.Component:
    return rx.el.div(
        rx.el.p(
            label,
            class_name="font-mono text-[10px] text-zinc-500 uppercase tracking-widest font-bold",
        ),
        rx.el.p(
            value,
            class_name=rx.cond(
                accent,
                "font-mono text-xl text-amber-400 font-bold mt-1",
                "font-mono text-xl text-zinc-100 font-bold mt-1",
            ),
        ),
        class_name="bg-zinc-900/40 border border-zinc-900 rounded-lg p-3",
    )


def _no_dataset_card() -> rx.Component:
    return rx.el.div(
        rx.icon(
            "triangle-alert", class_name="h-10 w-10 text-amber-500 mx-auto mb-3"
        ),
        rx.el.p(
            "NO DATASET LOADED",
            class_name="font-mono text-sm text-zinc-200 font-bold tracking-widest text-center uppercase",
        ),
        rx.el.p(
            "Visit the Upload page to load a configuration before running the solver.",
            class_name="font-mono text-xs text-zinc-500 text-center mt-2 max-w-sm mx-auto",
        ),
        rx.el.button(
            "GO TO UPLOAD",
            on_click=lambda: rx.redirect("/upload"),
            class_name="mt-4 mx-auto block px-5 py-2 border border-amber-500/40 bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 rounded-md font-mono text-xs tracking-widest uppercase font-bold transition-colors",
        ),
        class_name="bg-zinc-950 border border-zinc-900 p-8 rounded-xl text-center",
    )


def _dataset_review() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("file-cog", class_name="h-5 w-5 text-amber-500"),
            rx.el.h3(
                "Active Dataset",
                class_name="font-mono text-sm font-bold text-zinc-200 uppercase tracking-wider",
            ),
            class_name="flex items-center gap-2 mb-3",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.span(
                    "BOARD", class_name="text-zinc-500 font-mono text-[10px]"
                ),
                rx.el.span(
                    PuzzleState.board_rows.to_string()
                    + "x"
                    + PuzzleState.board_cols.to_string(),
                    class_name="text-zinc-100 font-mono text-sm font-bold",
                ),
                class_name="flex flex-col gap-0.5",
            ),
            rx.el.div(
                rx.el.span(
                    "PIECE", class_name="text-zinc-500 font-mono text-[10px]"
                ),
                rx.el.span(
                    PuzzleState.piece_type,
                    class_name="text-amber-400 font-mono text-sm font-bold",
                ),
                class_name="flex flex-col gap-0.5",
            ),
            rx.el.div(
                rx.el.span(
                    "COUNT", class_name="text-zinc-500 font-mono text-[10px]"
                ),
                rx.el.span(
                    PuzzleState.piece_count.to_string(),
                    class_name="text-zinc-100 font-mono text-sm font-bold",
                ),
                class_name="flex flex-col gap-0.5",
            ),
            rx.el.div(
                rx.el.span(
                    "CONSTRAINT",
                    class_name="text-zinc-500 font-mono text-[10px]",
                ),
                rx.el.span(
                    PuzzleState.constraint,
                    class_name="text-zinc-100 font-mono text-sm font-bold",
                ),
                class_name="flex flex-col gap-0.5",
            ),
            class_name="grid grid-cols-2 md:grid-cols-4 gap-4",
        ),
        class_name="bg-zinc-950 border border-zinc-900 p-5 rounded-xl mb-6",
    )


def _solver_controls() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("sliders-horizontal", class_name="h-5 w-5 text-amber-500"),
            rx.el.h3(
                "Solver Configuration",
                class_name="font-mono text-sm font-bold text-zinc-200 uppercase tracking-wider",
            ),
            class_name="flex items-center gap-2 mb-4",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.label(
                    "Max Solutions",
                    class_name="font-mono text-[11px] text-zinc-500 uppercase tracking-wider font-bold mb-1.5 block",
                ),
                rx.el.input(
                    default_value=SolverState.max_solutions_input,
                    on_change=SolverState.set_max_solutions.debounce(300),
                    type="number",
                    disabled=SolverState.find_all,
                    class_name=rx.cond(
                        SolverState.find_all,
                        "w-full bg-zinc-900/50 border border-zinc-800 rounded-md px-3 py-2 font-mono text-xs text-zinc-600 cursor-not-allowed",
                        "w-full bg-zinc-900 border border-zinc-800 rounded-md px-3 py-2 font-mono text-xs text-zinc-200 focus:outline-none focus:border-amber-500/60",
                    ),
                ),
                class_name="flex-1",
            ),
            rx.el.button(
                rx.cond(
                    SolverState.find_all,
                    rx.icon(
                        "square_check", class_name="h-4 w-4 text-amber-400"
                    ),
                    rx.icon("square", class_name="h-4 w-4 text-zinc-500"),
                ),
                rx.el.span("Find All", class_name="font-mono text-xs"),
                on_click=SolverState.toggle_find_all,
                class_name="flex items-center gap-2 px-3 py-2 bg-zinc-900 border border-zinc-800 hover:border-amber-500/40 text-zinc-300 rounded-md transition-colors h-fit mt-6",
            ),
            rx.el.button(
                rx.cond(
                    SolverState.record_steps,
                    rx.icon(
                        "square_check", class_name="h-4 w-4 text-amber-400"
                    ),
                    rx.icon("square", class_name="h-4 w-4 text-zinc-500"),
                ),
                rx.el.span("Record Steps", class_name="font-mono text-xs"),
                on_click=SolverState.toggle_record_steps,
                class_name="flex items-center gap-2 px-3 py-2 bg-zinc-900 border border-zinc-800 hover:border-amber-500/40 text-zinc-300 rounded-md transition-colors h-fit mt-6",
            ),
            class_name="flex flex-col md:flex-row gap-3",
        ),
        rx.cond(
            SolverState.performance_warning != "",
            rx.el.div(
                rx.icon(
                    "triangle-alert",
                    class_name="h-4 w-4 text-amber-400 shrink-0 mt-0.5",
                ),
                rx.el.p(
                    SolverState.performance_warning,
                    class_name="font-mono text-[11px] text-amber-300 leading-relaxed",
                ),
                class_name="flex gap-2 items-start p-3 bg-amber-500/5 border border-amber-500/30 rounded-md mt-4",
            ),
        ),
        rx.el.button(
            rx.cond(
                SolverState.is_solving,
                rx.icon("loader", class_name="h-4 w-4 animate-spin"),
                rx.icon("play", class_name="h-4 w-4"),
            ),
            rx.el.span(
                rx.cond(SolverState.is_solving, "SOLVING...", "RUN SOLVER"),
                class_name="font-mono text-xs tracking-widest",
            ),
            disabled=SolverState.is_solving,
            on_click=SolverState.run_solver,
            class_name=rx.cond(
                SolverState.is_solving,
                "flex items-center justify-center gap-2 mt-4 w-full py-3 bg-zinc-800 text-zinc-500 rounded-md uppercase font-bold cursor-not-allowed",
                "flex items-center justify-center gap-2 mt-4 w-full py-3 bg-amber-500 hover:bg-amber-400 text-zinc-950 rounded-md uppercase font-bold transition-colors",
            ),
        ),
        class_name="bg-zinc-950 border border-zinc-900 p-5 rounded-xl",
    )


def _stats_panel() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("activity", class_name="h-5 w-5 text-amber-500"),
            rx.el.h3(
                "Execution Statistics",
                class_name="font-mono text-sm font-bold text-zinc-200 uppercase tracking-wider",
            ),
            class_name="flex items-center gap-2 mb-4",
        ),
        rx.el.div(
            _stat_card(
                "Solutions",
                SolverState.solutions_found.to_string(),
                accent=True,
            ),
            _stat_card("Nodes", SolverState.nodes_explored.to_string()),
            _stat_card("Backtracks", SolverState.backtracks.to_string()),
            _stat_card("Time", SolverState.execution_time_ms, accent=True),
            class_name="grid grid-cols-2 lg:grid-cols-4 gap-3",
        ),
        class_name="bg-zinc-950 border border-zinc-900 p-5 rounded-xl",
    )


def _solution_navigator() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.button(
                rx.icon("chevrons-left", class_name="h-4 w-4"),
                on_click=SolverState.go_first_solution,
                disabled=SolverState.current_solution_index == 0,
                class_name="px-2.5 py-1.5 bg-zinc-900 border border-zinc-800 hover:border-amber-500/40 disabled:opacity-30 disabled:cursor-not-allowed text-zinc-300 rounded transition-colors",
            ),
            rx.el.button(
                rx.icon("chevron-left", class_name="h-4 w-4"),
                on_click=SolverState.prev_solution,
                disabled=SolverState.current_solution_index == 0,
                class_name="px-2.5 py-1.5 bg-zinc-900 border border-zinc-800 hover:border-amber-500/40 disabled:opacity-30 disabled:cursor-not-allowed text-zinc-300 rounded transition-colors",
            ),
            rx.el.span(
                SolverState.solution_label,
                class_name="font-mono text-xs text-zinc-300 px-3 min-w-[140px] text-center font-bold",
            ),
            rx.el.button(
                rx.icon("chevron-right", class_name="h-4 w-4"),
                on_click=SolverState.next_solution,
                disabled=SolverState.current_solution_index
                >= (SolverState.total_solutions - 1),
                class_name="px-2.5 py-1.5 bg-zinc-900 border border-zinc-800 hover:border-amber-500/40 disabled:opacity-30 disabled:cursor-not-allowed text-zinc-300 rounded transition-colors",
            ),
            rx.el.button(
                rx.icon("chevrons-right", class_name="h-4 w-4"),
                on_click=SolverState.go_last_solution,
                disabled=SolverState.current_solution_index
                >= (SolverState.total_solutions - 1),
                class_name="px-2.5 py-1.5 bg-zinc-900 border border-zinc-800 hover:border-amber-500/40 disabled:opacity-30 disabled:cursor-not-allowed text-zinc-300 rounded transition-colors",
            ),
            class_name="flex items-center gap-2",
        ),
        rx.el.div(
            rx.el.button(
                rx.icon("download", class_name="h-3.5 w-3.5"),
                rx.el.span(
                    "TXT", class_name="font-mono text-[11px] tracking-wider"
                ),
                on_click=SolverState.download_txt,
                class_name="flex items-center gap-1.5 px-3 py-1.5 bg-zinc-900 border border-zinc-800 hover:border-amber-500/40 text-zinc-300 hover:text-amber-400 rounded transition-colors",
            ),
            rx.el.button(
                rx.icon("file-text", class_name="h-3.5 w-3.5"),
                rx.el.span(
                    "PDF", class_name="font-mono text-[11px] tracking-wider"
                ),
                on_click=SolverState.download_pdf,
                class_name="flex items-center gap-1.5 px-3 py-1.5 bg-zinc-900 border border-zinc-800 hover:border-amber-500/40 text-zinc-300 hover:text-amber-400 rounded transition-colors",
            ),
            class_name="flex items-center gap-2",
        ),
        class_name="flex items-center justify-between flex-wrap gap-3",
    )


def _playback_panel() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("clapperboard", class_name="h-5 w-5 text-amber-500"),
            rx.el.h3(
                "Step Playback",
                class_name="font-mono text-sm font-bold text-zinc-200 uppercase tracking-wider",
            ),
            class_name="flex items-center gap-2 mb-3",
        ),
        rx.el.div(
            rx.el.p(
                SolverState.current_step_text,
                class_name="font-mono text-xs text-amber-300 px-3 py-2 bg-zinc-900/50 border border-zinc-900 rounded-md min-h-[40px]",
            ),
            rx.el.p(
                "Step " + SolverState.step_label,
                class_name="font-mono text-[10px] text-zinc-500 mt-2 tracking-wider",
            ),
            class_name="mb-4",
        ),
        rx.el.div(
            rx.el.button(
                rx.icon("skip-back", class_name="h-4 w-4"),
                on_click=SolverState.step_reset,
                class_name="px-3 py-2 bg-zinc-900 border border-zinc-800 hover:border-amber-500/40 text-zinc-300 rounded transition-colors",
            ),
            rx.el.button(
                rx.icon("chevron-left", class_name="h-4 w-4"),
                on_click=SolverState.step_prev,
                class_name="px-3 py-2 bg-zinc-900 border border-zinc-800 hover:border-amber-500/40 text-zinc-300 rounded transition-colors",
            ),
            rx.cond(
                SolverState.is_playing,
                rx.el.button(
                    rx.icon("pause", class_name="h-4 w-4"),
                    on_click=SolverState.stop_playback,
                    class_name="px-3 py-2 bg-amber-500/20 border border-amber-500/40 text-amber-400 rounded transition-colors",
                ),
                rx.el.button(
                    rx.icon("play", class_name="h-4 w-4"),
                    on_click=SolverState.play_steps,
                    class_name="px-3 py-2 bg-zinc-900 border border-zinc-800 hover:border-amber-500/40 text-zinc-300 rounded transition-colors",
                ),
            ),
            rx.el.button(
                rx.icon("chevron-right", class_name="h-4 w-4"),
                on_click=SolverState.step_next,
                class_name="px-3 py-2 bg-zinc-900 border border-zinc-800 hover:border-amber-500/40 text-zinc-300 rounded transition-colors",
            ),
            rx.el.div(
                rx.el.label(
                    "Speed (ms)",
                    class_name="font-mono text-[10px] text-zinc-500 uppercase tracking-wider block mb-1",
                ),
                rx.el.div(
                    rx.el.select(
                        rx.el.option("100", value="100"),
                        rx.el.option("250", value="250"),
                        rx.el.option("400", value="400"),
                        rx.el.option("700", value="700"),
                        rx.el.option("1500", value="1500"),
                        value=SolverState.playback_speed_ms.to_string(),
                        on_change=SolverState.set_speed,
                        class_name="appearance-none bg-zinc-900 border border-zinc-800 rounded px-2 py-1 pr-7 font-mono text-[11px] text-zinc-200 focus:outline-none focus:border-amber-500/60",
                    ),
                    rx.icon(
                        "chevron-down",
                        class_name="absolute right-1.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-zinc-500 pointer-events-none",
                    ),
                    class_name="relative",
                ),
                class_name="ml-auto",
            ),
            class_name="flex items-center gap-2 flex-wrap",
        ),
        class_name="bg-zinc-950 border border-zinc-900 p-5 rounded-xl",
    )


def _board_panel() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon("grid-2x2", class_name="h-5 w-5 text-amber-500"),
                rx.el.h3(
                    "Board Visualization",
                    class_name="font-mono text-sm font-bold text-zinc-200 uppercase tracking-wider",
                ),
                class_name="flex items-center gap-2",
            ),
            _solution_navigator(),
            class_name="flex items-center justify-between flex-wrap gap-3 mb-4",
        ),
        rx.cond(
            SolverState.has_result & (SolverState.total_solutions > 0),
            chessboard(),
            rx.el.div(
                rx.icon(
                    "circle-dashed",
                    class_name="h-10 w-10 text-zinc-700 mx-auto mb-2",
                ),
                rx.el.p(
                    "Run the solver to render solutions",
                    class_name="font-mono text-xs text-zinc-500 text-center",
                ),
                class_name="bg-zinc-900/30 border border-zinc-900 border-dashed rounded-xl p-12",
            ),
        ),
        class_name="bg-zinc-950 border border-zinc-900 p-5 rounded-xl",
    )


def _error_banner() -> rx.Component:
    return rx.cond(
        SolverState.error_msg != "",
        rx.el.div(
            rx.icon(
                "octagon_alert", class_name="h-5 w-5 text-red-500 shrink-0"
            ),
            rx.el.p(
                SolverState.error_msg,
                class_name="font-mono text-xs text-red-300 flex-1",
            ),
            rx.el.button(
                rx.icon("x", class_name="h-4 w-4"),
                on_click=SolverState.dismiss_error,
                class_name="text-red-400/70 hover:text-red-300",
            ),
            class_name="flex gap-3 items-center p-4 bg-red-950/30 border border-red-500/30 rounded-lg w-full mb-4",
        ),
    )


def solve_page_content() -> rx.Component:
    return rx.el.div(
        rx.el.span(
            "SOLVER ENGINE PANEL",
            class_name="text-xs font-mono tracking-widest text-amber-500 bg-amber-500/10 px-2.5 py-1 rounded border border-amber-500/20 uppercase font-semibold",
        ),
        rx.el.h1(
            "Backtracking Engine Execution",
            class_name="text-4xl font-bold tracking-tight text-zinc-100 font-mono mt-3 uppercase",
        ),
        rx.el.p(
            "Visualize search recursion on the live board. Step through node placements, conflicts, and backtracks.",
            class_name="text-zinc-400 mt-2 text-sm leading-relaxed mb-6 max-w-2xl",
        ),
        _error_banner(),
        rx.cond(
            PuzzleState.has_dataset,
            rx.el.div(
                _dataset_review(),
                rx.el.div(
                    rx.el.div(
                        _solver_controls(),
                        class_name="w-full lg:w-1/3",
                    ),
                    rx.el.div(
                        _board_panel(),
                        class_name="w-full lg:w-2/3",
                    ),
                    class_name="flex flex-col lg:flex-row gap-6 mb-6",
                ),
                rx.el.div(
                    _stats_panel(),
                    class_name="mb-6",
                ),
                rx.cond(
                    SolverState.has_result & (SolverState.total_steps > 0),
                    _playback_panel(),
                ),
            ),
            _no_dataset_card(),
        ),
    )