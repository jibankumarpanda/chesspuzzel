import reflex as rx
from frontend_code_analysis.states.statistics_state import StatisticsState


TOOLTIP_PROPS = {
    "content_style": {
        "background": "#0a0a0a",
        "borderColor": "#27272a",
        "borderRadius": "0.5rem",
        "fontFamily": "JetBrains Mono, monospace",
        "fontSize": "0.75rem",
        "color": "#fafafa",
        "padding": "0.5rem 0.75rem",
    },
    "item_style": {"color": "#fafafa"},
    "label_style": {"color": "#a1a1aa", "fontWeight": "600"},
    "cursor": {"fill": "#f59e0b", "fillOpacity": 0.08},
    "separator": ": ",
}


def _metric_card(
    label: str, value, sublabel: str = "", accent: bool = False
) -> rx.Component:
    return rx.el.div(
        rx.el.p(
            label,
            class_name="font-mono text-[10px] text-zinc-500 uppercase tracking-widest font-bold",
        ),
        rx.el.p(
            value,
            class_name=rx.cond(
                accent,
                "font-mono text-2xl text-amber-400 font-bold mt-1.5",
                "font-mono text-2xl text-zinc-100 font-bold mt-1.5",
            ),
        ),
        rx.cond(
            sublabel != "",
            rx.el.p(
                sublabel,
                class_name="font-mono text-[10px] text-zinc-500 mt-1 tracking-wider",
            ),
        ),
        class_name="bg-zinc-950 border border-zinc-900 p-5 rounded-xl",
    )


def _legend_item(label: str, color: str) -> rx.Component:
    return rx.el.div(
        rx.el.span(
            class_name="w-3 h-3 inline-block rounded-sm mr-2",
            style={"backgroundColor": color},
        ),
        rx.el.span(
            label,
            class_name="font-mono text-[11px] text-zinc-400 tracking-wider",
        ),
        class_name="flex items-center",
    )


def _execution_chart() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon("activity", class_name="h-5 w-5 text-amber-500"),
                rx.el.h3(
                    "Execution Time per Puzzle (last 30 runs)",
                    class_name="font-mono text-sm font-bold text-zinc-200 uppercase tracking-wider",
                ),
                class_name="flex items-center gap-2",
            ),
            _legend_item("Time (ms)", "#f59e0b"),
            class_name="flex items-center justify-between mb-4 flex-wrap gap-2",
        ),
        rx.recharts.line_chart(
            rx.recharts.cartesian_grid(
                horizontal=True,
                vertical=False,
                stroke="#27272a",
            ),
            rx.recharts.graphing_tooltip(**TOOLTIP_PROPS),
            rx.recharts.line(
                data_key="execution_ms",
                name="Time (ms)",
                stroke="#f59e0b",
                stroke_width=2,
                type_="monotone",
                dot={"fill": "#f59e0b", "r": 3},
            ),
            rx.recharts.x_axis(
                data_key="label",
                axis_line=False,
                tick_line=False,
                custom_attrs={"fontSize": "10px", "fill": "#71717a"},
                stroke="#71717a",
                interval="preserveStartEnd",
                height=40,
            ),
            rx.recharts.y_axis(
                axis_line=False,
                tick_line=False,
                custom_attrs={"fontSize": "10px", "fill": "#71717a"},
                stroke="#71717a",
            ),
            data=StatisticsState.time_chart,
            width="100%",
            height=280,
            margin={"left": 10, "right": 20, "top": 10, "bottom": 5},
        ),
        class_name="bg-zinc-950 border border-zinc-900 p-5 rounded-xl",
    )


def _nodes_chart() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon("git-branch", class_name="h-5 w-5 text-amber-500"),
                rx.el.h3(
                    "Nodes Explored per Puzzle",
                    class_name="font-mono text-sm font-bold text-zinc-200 uppercase tracking-wider",
                ),
                class_name="flex items-center gap-2",
            ),
            _legend_item("Nodes", "#10b981"),
            class_name="flex items-center justify-between mb-4 flex-wrap gap-2",
        ),
        rx.recharts.bar_chart(
            rx.recharts.cartesian_grid(
                horizontal=True,
                vertical=False,
                stroke="#27272a",
            ),
            rx.recharts.graphing_tooltip(**TOOLTIP_PROPS),
            rx.recharts.bar(
                data_key="nodes",
                name="Nodes",
                fill="#10b981",
                radius=[3, 3, 0, 0],
            ),
            rx.recharts.x_axis(
                data_key="label",
                axis_line=False,
                tick_line=False,
                custom_attrs={"fontSize": "10px", "fill": "#71717a"},
                stroke="#71717a",
                interval="preserveStartEnd",
                height=40,
            ),
            rx.recharts.y_axis(
                axis_line=False,
                tick_line=False,
                custom_attrs={"fontSize": "10px", "fill": "#71717a"},
                stroke="#71717a",
            ),
            data=StatisticsState.time_chart,
            width="100%",
            height=280,
            margin={"left": 10, "right": 20, "top": 10, "bottom": 5},
        ),
        class_name="bg-zinc-950 border border-zinc-900 p-5 rounded-xl",
    )


def _piece_chart() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("layers", class_name="h-5 w-5 text-amber-500"),
            rx.el.h3(
                "Puzzle Distribution by Piece",
                class_name="font-mono text-sm font-bold text-zinc-200 uppercase tracking-wider",
            ),
            class_name="flex items-center gap-2 mb-4",
        ),
        rx.recharts.bar_chart(
            rx.recharts.cartesian_grid(
                horizontal=True,
                vertical=False,
                stroke="#27272a",
            ),
            rx.recharts.graphing_tooltip(**TOOLTIP_PROPS),
            rx.recharts.bar(
                data_key="count",
                name="Puzzles",
                radius=[4, 4, 0, 0],
            ),
            rx.recharts.x_axis(
                data_key="piece",
                axis_line=False,
                tick_line=False,
                custom_attrs={"fontSize": "11px", "fill": "#a1a1aa"},
                stroke="#71717a",
            ),
            rx.recharts.y_axis(
                axis_line=False,
                tick_line=False,
                custom_attrs={"fontSize": "10px", "fill": "#71717a"},
                stroke="#71717a",
                allow_decimals=False,
            ),
            data=StatisticsState.piece_breakdown,
            width="100%",
            height=260,
            margin={"left": 10, "right": 20, "top": 10, "bottom": 5},
        ),
        rx.el.div(
            rx.foreach(
                StatisticsState.piece_breakdown,
                lambda b: rx.el.div(
                    rx.el.span(
                        class_name="w-3 h-3 rounded-sm",
                        style={"backgroundColor": b["fill"]},
                    ),
                    rx.el.span(
                        b["piece"],
                        class_name="font-mono text-[10px] text-zinc-400 tracking-wider",
                    ),
                    rx.el.span(
                        b["count"].to_string(),
                        class_name="font-mono text-xs text-zinc-100 font-bold ml-auto",
                    ),
                    class_name="flex items-center gap-2 px-3 py-1.5 bg-zinc-900/40 border border-zinc-900 rounded",
                ),
            ),
            class_name="grid grid-cols-2 gap-2 mt-4",
        ),
        class_name="bg-zinc-950 border border-zinc-900 p-5 rounded-xl",
    )


def _alerts() -> rx.Component:
    return rx.cond(
        StatisticsState.error_msg != "",
        rx.el.div(
            rx.icon(
                "octagon_alert", class_name="h-5 w-5 text-red-500 shrink-0"
            ),
            rx.el.p(
                StatisticsState.error_msg,
                class_name="font-mono text-xs text-red-300 flex-1",
            ),
            rx.el.button(
                rx.icon("x", class_name="h-4 w-4"),
                on_click=StatisticsState.dismiss_error,
                class_name="text-red-400/70 hover:text-red-300",
            ),
            class_name="flex gap-3 items-center p-3 bg-red-950/30 border border-red-500/30 rounded-lg w-full mb-3",
        ),
    )


def _empty() -> rx.Component:
    return rx.el.div(
        rx.icon(
            "chart-no-axes-column",
            class_name="h-10 w-10 text-zinc-700 mx-auto mb-3",
        ),
        rx.el.p(
            "NO STATISTICS RECORDED",
            class_name="font-mono text-sm text-zinc-300 font-bold tracking-widest text-center uppercase",
        ),
        rx.el.p(
            "Solve at least one puzzle to populate aggregate metrics, charts, and breakdowns.",
            class_name="font-mono text-[11px] text-zinc-500 text-center mt-2 max-w-sm mx-auto",
        ),
        rx.el.button(
            "GO TO SOLVER",
            on_click=lambda: rx.redirect("/solve"),
            class_name="mt-4 mx-auto block px-5 py-2 border border-amber-500/40 bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 rounded-md font-mono text-xs tracking-widest uppercase font-bold transition-colors",
        ),
        class_name="bg-zinc-950 border border-zinc-900 border-dashed p-12 rounded-xl text-center",
    )


def statistics_page_content() -> rx.Component:
    return rx.el.div(
        rx.el.span(
            "SYSTEM METRICS MONITOR",
            class_name="text-xs font-mono tracking-widest text-amber-500 bg-amber-500/10 px-2.5 py-1 rounded border border-amber-500/20 uppercase font-semibold",
        ),
        rx.el.h1(
            "Performance Metrics",
            class_name="text-4xl font-bold tracking-tight text-zinc-100 font-mono mt-3 uppercase",
        ),
        rx.el.p(
            "Aggregate analysis of all solver executions: timing, search depth, and piece distribution.",
            class_name="text-zinc-400 mt-2 text-sm leading-relaxed mb-6 max-w-2xl",
        ),
        _alerts(),
        rx.cond(
            StatisticsState.has_data,
            rx.el.div(
                rx.el.div(
                    _metric_card(
                        "Total Puzzles",
                        StatisticsState.total_puzzles.to_string(),
                        accent=True,
                    ),
                    _metric_card(
                        "Solutions Found",
                        StatisticsState.total_solutions.to_string(),
                    ),
                    _metric_card(
                        "Total Nodes",
                        StatisticsState.total_nodes.to_string(),
                    ),
                    _metric_card(
                        "Total Backtracks",
                        StatisticsState.total_backtracks.to_string(),
                    ),
                    class_name="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6",
                ),
                rx.el.div(
                    _metric_card(
                        "Avg Execution",
                        StatisticsState.avg_time_ms,
                        accent=True,
                    ),
                    _metric_card(
                        "Fastest Run",
                        StatisticsState.fastest_time_ms,
                    ),
                    _metric_card(
                        "Slowest Run",
                        StatisticsState.slowest_time_ms,
                    ),
                    class_name="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6",
                ),
                rx.el.div(
                    rx.el.div(
                        _execution_chart(),
                        class_name="w-full lg:w-1/2",
                    ),
                    rx.el.div(
                        _nodes_chart(),
                        class_name="w-full lg:w-1/2",
                    ),
                    class_name="flex flex-col lg:flex-row gap-6 mb-6",
                ),
                _piece_chart(),
            ),
            _empty(),
        ),
    )