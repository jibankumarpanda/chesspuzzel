import reflex as rx
from frontend_code_analysis.states.history_state import HistoryState


def _backend_banner() -> rx.Component:
    return rx.cond(
        HistoryState.db_available,
        rx.el.div(
            rx.icon("database", class_name="h-4 w-4 text-emerald-400 shrink-0"),
            rx.el.p(
                HistoryState.db_note,
                class_name="font-mono text-[11px] text-emerald-400/90",
            ),
            class_name="flex items-center gap-2 px-3 py-2 bg-emerald-500/5 border border-emerald-500/20 rounded-md mb-4",
        ),
        rx.el.div(
            rx.icon(
                "info",
                class_name="h-4 w-4 text-amber-400 shrink-0 mt-0.5",
            ),
            rx.el.p(
                HistoryState.db_note,
                class_name="font-mono text-[11px] text-amber-400/90 leading-relaxed",
            ),
            class_name="flex items-start gap-2 px-3 py-2 bg-amber-500/5 border border-amber-500/20 rounded-md mb-4",
        ),
    )


def _alerts() -> rx.Component:
    return rx.el.div(
        rx.cond(
            HistoryState.error_msg != "",
            rx.el.div(
                rx.icon(
                    "octagon_alert", class_name="h-5 w-5 text-red-500 shrink-0"
                ),
                rx.el.p(
                    HistoryState.error_msg,
                    class_name="font-mono text-xs text-red-300 flex-1",
                ),
                rx.el.button(
                    rx.icon("x", class_name="h-4 w-4"),
                    on_click=HistoryState.dismiss_error,
                    class_name="text-red-400/70 hover:text-red-300",
                ),
                class_name="flex gap-3 items-center p-3 bg-red-950/30 border border-red-500/30 rounded-lg w-full mb-3",
            ),
        ),
        rx.cond(
            HistoryState.success_msg != "",
            rx.el.div(
                rx.icon(
                    "circle-check",
                    class_name="h-5 w-5 text-emerald-400 shrink-0",
                ),
                rx.el.p(
                    HistoryState.success_msg,
                    class_name="font-mono text-xs text-emerald-300 flex-1",
                ),
                rx.el.button(
                    rx.icon("x", class_name="h-4 w-4"),
                    on_click=HistoryState.dismiss_success,
                    class_name="text-emerald-400/70 hover:text-emerald-300",
                ),
                class_name="flex gap-3 items-center p-3 bg-emerald-950/20 border border-emerald-500/30 rounded-lg w-full mb-3",
            ),
        ),
    )


def _row(item) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            "#" + item["id"].to_string(),
            class_name="px-4 py-3 font-mono text-[11px] text-amber-400 font-bold",
        ),
        rx.el.td(
            item["filename"],
            class_name="px-4 py-3 font-mono text-xs text-zinc-200 max-w-[180px] truncate",
        ),
        rx.el.td(
            item["board_size"],
            class_name="px-4 py-3 font-mono text-xs text-zinc-300",
        ),
        rx.el.td(
            rx.el.span(
                item["piece_type"],
                class_name="px-2 py-0.5 bg-amber-500/10 border border-amber-500/30 rounded text-[10px] font-mono text-amber-400 font-bold w-fit",
            ),
            class_name="px-4 py-3",
        ),
        rx.el.td(
            item["piece_count"].to_string(),
            class_name="px-4 py-3 font-mono text-xs text-zinc-300 text-center",
        ),
        rx.el.td(
            item["constraint"],
            class_name="px-4 py-3 font-mono text-[11px] text-zinc-400",
        ),
        rx.el.td(
            item["created_at"],
            class_name="px-4 py-3 font-mono text-[11px] text-zinc-500",
        ),
        rx.el.td(
            rx.el.div(
                rx.el.button(
                    rx.icon("eye", class_name="h-3.5 w-3.5"),
                    rx.el.span(
                        "VIEW",
                        class_name="font-mono text-[10px] tracking-wider",
                    ),
                    on_click=lambda: HistoryState.reopen_puzzle(item["id"]),
                    class_name="flex items-center gap-1.5 px-2.5 py-1.5 bg-zinc-900 border border-zinc-800 hover:border-amber-500/40 hover:text-amber-400 text-zinc-300 rounded transition-colors",
                ),
                rx.el.button(
                    rx.icon("trash-2", class_name="h-3.5 w-3.5"),
                    on_click=lambda: HistoryState.request_delete(
                        item["id"], item["filename"]
                    ),
                    class_name="flex items-center px-2.5 py-1.5 bg-zinc-900 border border-zinc-800 hover:border-red-500/40 hover:text-red-400 text-zinc-400 rounded transition-colors",
                ),
                class_name="flex items-center gap-2 justify-end",
            ),
            class_name="px-4 py-3",
        ),
        class_name="border-b border-zinc-900 hover:bg-zinc-900/40 transition-colors",
    )


def _table() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.table(
                rx.el.thead(
                    rx.el.tr(
                        rx.el.th(
                            "ID",
                            class_name="px-4 py-3 text-left font-mono text-[10px] text-zinc-500 uppercase tracking-widest font-bold bg-zinc-950/80",
                        ),
                        rx.el.th(
                            "Filename",
                            class_name="px-4 py-3 text-left font-mono text-[10px] text-zinc-500 uppercase tracking-widest font-bold bg-zinc-950/80",
                        ),
                        rx.el.th(
                            "Board",
                            class_name="px-4 py-3 text-left font-mono text-[10px] text-zinc-500 uppercase tracking-widest font-bold bg-zinc-950/80",
                        ),
                        rx.el.th(
                            "Piece",
                            class_name="px-4 py-3 text-left font-mono text-[10px] text-zinc-500 uppercase tracking-widest font-bold bg-zinc-950/80",
                        ),
                        rx.el.th(
                            "Count",
                            class_name="px-4 py-3 text-center font-mono text-[10px] text-zinc-500 uppercase tracking-widest font-bold bg-zinc-950/80",
                        ),
                        rx.el.th(
                            "Constraint",
                            class_name="px-4 py-3 text-left font-mono text-[10px] text-zinc-500 uppercase tracking-widest font-bold bg-zinc-950/80",
                        ),
                        rx.el.th(
                            "Created",
                            class_name="px-4 py-3 text-left font-mono text-[10px] text-zinc-500 uppercase tracking-widest font-bold bg-zinc-950/80",
                        ),
                        rx.el.th(
                            "Actions",
                            class_name="px-4 py-3 text-right font-mono text-[10px] text-zinc-500 uppercase tracking-widest font-bold bg-zinc-950/80",
                        ),
                        class_name="border-b border-zinc-800",
                    )
                ),
                rx.el.tbody(
                    rx.foreach(HistoryState.rows, _row),
                ),
                class_name="table-auto w-full",
            ),
            class_name="overflow-x-auto",
        ),
        class_name="bg-zinc-950 border border-zinc-900 rounded-xl overflow-hidden",
    )


def _empty() -> rx.Component:
    return rx.el.div(
        rx.icon(
            "database-zap", class_name="h-10 w-10 text-zinc-700 mx-auto mb-3"
        ),
        rx.el.p(
            "NO RECORDS FOUND",
            class_name="font-mono text-sm text-zinc-300 font-bold tracking-widest text-center uppercase",
        ),
        rx.el.p(
            "Run the solver from the Solve page to populate puzzle history.",
            class_name="font-mono text-[11px] text-zinc-500 text-center mt-2 max-w-sm mx-auto",
        ),
        rx.el.button(
            "GO TO UPLOAD",
            on_click=lambda: rx.redirect("/upload"),
            class_name="mt-4 mx-auto block px-5 py-2 border border-amber-500/40 bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 rounded-md font-mono text-xs tracking-widest uppercase font-bold transition-colors",
        ),
        class_name="bg-zinc-950 border border-zinc-900 border-dashed p-12 rounded-xl text-center",
    )


def _delete_confirm() -> rx.Component:
    return rx.cond(
        HistoryState.confirm_delete_id > 0,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon(
                        "triangle-alert", class_name="h-6 w-6 text-red-400"
                    ),
                    rx.el.h3(
                        "Confirm Delete",
                        class_name="font-mono text-base font-bold text-zinc-100 uppercase tracking-wider",
                    ),
                    class_name="flex items-center gap-3 mb-3",
                ),
                rx.el.p(
                    "This will permanently remove the puzzle and its solutions from the database. This action cannot be undone.",
                    class_name="font-mono text-xs text-zinc-400 leading-relaxed mb-3",
                ),
                rx.el.div(
                    rx.el.span(
                        "TARGET:",
                        class_name="font-mono text-[10px] text-zinc-500 uppercase tracking-widest mr-2",
                    ),
                    rx.el.span(
                        "#"
                        + HistoryState.confirm_delete_id.to_string()
                        + " — "
                        + HistoryState.confirm_delete_name,
                        class_name="font-mono text-xs text-amber-400 font-bold",
                    ),
                    class_name="bg-zinc-900/60 border border-zinc-800 rounded-md px-3 py-2 mb-5",
                ),
                rx.el.div(
                    rx.el.button(
                        "CANCEL",
                        on_click=HistoryState.cancel_delete,
                        class_name="px-4 py-2 bg-zinc-900 border border-zinc-800 hover:border-zinc-700 text-zinc-300 rounded-md font-mono text-xs tracking-widest uppercase transition-colors",
                    ),
                    rx.el.button(
                        rx.icon("trash-2", class_name="h-4 w-4"),
                        rx.el.span(
                            "DELETE PERMANENTLY",
                            class_name="font-mono text-xs tracking-widest",
                        ),
                        on_click=HistoryState.confirm_delete,
                        class_name="flex items-center gap-2 px-4 py-2 bg-red-500/20 border border-red-500/40 hover:bg-red-500/30 text-red-300 rounded-md uppercase font-bold transition-colors",
                    ),
                    class_name="flex items-center justify-end gap-2",
                ),
                class_name="bg-zinc-950 border border-red-500/30 rounded-xl p-6 max-w-md w-full",
            ),
            class_name="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4",
        ),
    )


def history_page_content() -> rx.Component:
    return rx.el.div(
        rx.el.span(
            "ARCHIVED EXECUTIONS",
            class_name="text-xs font-mono tracking-widest text-amber-500 bg-amber-500/10 px-2.5 py-1 rounded border border-amber-500/20 uppercase font-semibold",
        ),
        rx.el.h1(
            "Saved Solve History",
            class_name="text-4xl font-bold tracking-tight text-zinc-100 font-mono mt-3 uppercase",
        ),
        rx.el.p(
            "Search, reopen, and manage previously executed puzzle records persisted in the database.",
            class_name="text-zinc-400 mt-2 text-sm leading-relaxed mb-6 max-w-2xl",
        ),
        _backend_banner(),
        _alerts(),
        rx.el.div(
            rx.el.div(
                rx.icon("search", class_name="h-4 w-4 text-zinc-500"),
                rx.el.input(
                    placeholder="Search by filename, piece, constraint, or board size...",
                    default_value=HistoryState.search_query,
                    on_change=HistoryState.set_search.debounce(400),
                    class_name="w-full bg-transparent border-none outline-none font-mono text-xs text-zinc-200 placeholder:text-zinc-600",
                ),
                class_name="flex items-center gap-2 px-3 py-2 bg-zinc-950 border border-zinc-900 rounded-md flex-1",
            ),
            rx.el.button(
                rx.icon("refresh-cw", class_name="h-4 w-4"),
                rx.el.span(
                    "REFRESH", class_name="font-mono text-xs tracking-widest"
                ),
                on_click=HistoryState.refresh,
                class_name="flex items-center gap-2 px-4 py-2 bg-zinc-900 border border-zinc-800 hover:border-amber-500/40 hover:text-amber-400 text-zinc-300 rounded-md uppercase transition-colors",
            ),
            rx.el.div(
                rx.el.span(
                    "RECORDS:",
                    class_name="font-mono text-[10px] text-zinc-500 tracking-widest",
                ),
                rx.el.span(
                    HistoryState.total_rows.to_string(),
                    class_name="font-mono text-sm text-amber-400 font-bold ml-2",
                ),
                class_name="px-3 py-2 bg-zinc-900/40 border border-zinc-900 rounded-md",
            ),
            class_name="flex flex-wrap items-center gap-3 mb-6",
        ),
        rx.cond(
            HistoryState.total_rows > 0,
            _table(),
            _empty(),
        ),
        _delete_confirm(),
    )