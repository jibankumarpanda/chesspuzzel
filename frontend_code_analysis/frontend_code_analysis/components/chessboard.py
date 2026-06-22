import reflex as rx
from frontend_code_analysis.states.solver_state import SolverState


def _square(sq) -> rx.Component:
    return rx.el.div(
        rx.cond(
            sq["has_piece"].to(bool),
            rx.el.span(
                SolverState.current_glyph,
                class_name="text-amber-400 drop-shadow-[0_0_8px_rgba(245,158,11,0.6)] transition-all duration-300",
                style={"fontSize": "min(5vw, 2.25rem)"},
            ),
            rx.el.span(""),
        ),
        class_name=rx.cond(
            sq["is_dark"].to(bool),
            "aspect-square flex items-center justify-center bg-zinc-900 transition-colors",
            "aspect-square flex items-center justify-center bg-zinc-800/40 transition-colors",
        ),
    )


def chessboard() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.foreach(SolverState.board_squares, _square),
            class_name="grid border border-zinc-800 rounded-lg overflow-hidden w-full",
            style={"gridTemplateColumns": SolverState.board_grid_template},
        ),
        class_name="w-full max-w-2xl mx-auto",
    )