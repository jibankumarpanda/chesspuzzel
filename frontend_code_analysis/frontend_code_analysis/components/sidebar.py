import reflex as rx
from frontend_code_analysis.states.navigation import NavigationState


def sidebar_link(label: str, icon_tag: str, route: str) -> rx.Component:
    is_active = NavigationState.current_page == route

    return rx.el.button(
        rx.icon(
            icon_tag,
            class_name=rx.cond(
                is_active, "h-5 w-5 text-amber-500", "h-5 w-5 text-zinc-400"
            ),
        ),
        rx.el.span(label, class_name="font-mono text-sm tracking-wide"),
        on_click=lambda: NavigationState.set_page(route),
        class_name=rx.cond(
            is_active,
            "flex items-center gap-3 w-full px-4 py-3 rounded-lg bg-zinc-900 border border-amber-500/30 text-amber-500 font-semibold transition-all duration-200",
            "flex items-center gap-3 w-full px-4 py-3 rounded-lg text-zinc-400 hover:text-zinc-100 hover:bg-zinc-900/60 border border-transparent hover:border-zinc-800 transition-all duration-200",
        ),
    )


def sidebar() -> rx.Component:
    return rx.el.aside(
        # Top Logo Area
        rx.el.div(
            rx.el.div(
                rx.icon(
                    "box", class_name="h-6 w-6 text-amber-500 animate-pulse"
                ),
                rx.el.span(
                    "CHESSLAB",
                    class_name="font-mono text-lg font-black tracking-widest text-zinc-100",
                ),
                class_name="flex items-center gap-3",
            ),
            rx.el.span(
                "PUZZLE ENGINE v1.0",
                class_name="font-mono text-[10px] text-zinc-500 tracking-wider mt-1 block pl-9",
            ),
            class_name="p-6 border-b border-zinc-900",
        ),
        # Navigation Links Container
        rx.el.nav(
            sidebar_link("Dashboard", "home", "/"),
            sidebar_link("Upload Puzzle", "cloud_upload", "/upload"),
            sidebar_link("Solve Engine", "cpu", "/solve"),
            sidebar_link("Puzzle History", "history", "/history"),
            sidebar_link("Statistics", "bar-chart-3", "/statistics"),
            sidebar_link("About Engine", "info", "/about"),
            class_name="flex-1 px-4 py-6 flex flex-col gap-2 overflow-y-auto",
        ),
        # Bottom Utility / Dark Mode & Profile
        rx.el.div(
            rx.el.button(
                rx.icon(
                    rx.cond(NavigationState.is_dark_mode, "sun", "moon"),
                    class_name="h-4 w-4 text-zinc-400",
                ),
                rx.el.span(
                    rx.cond(
                        NavigationState.is_dark_mode,
                        "Light Terminal",
                        "Core Darkmode",
                    ),
                    class_name="font-mono text-xs tracking-wider",
                ),
                on_click=NavigationState.toggle_theme,
                class_name="flex items-center justify-center gap-2 w-full py-2 px-3 border border-zinc-800 rounded-md bg-zinc-950 hover:bg-zinc-900 hover:border-zinc-700 text-zinc-400 transition-colors",
            ),
            rx.el.div(
                rx.el.div(
                    rx.image(
                        src="https://api.dicebear.com/9.x/notionists/svg?seed=chesslab",
                        class_name="size-9 rounded-full bg-zinc-800",
                    ),
                    rx.el.div(
                        rx.el.p(
                            "Lab Operator",
                            class_name="font-mono text-xs font-bold text-zinc-300 leading-none",
                        ),
                        rx.el.p(
                            "operator@chess.lab",
                            class_name="font-mono text-[10px] text-zinc-500 leading-none mt-1",
                        ),
                    ),
                    class_name="flex items-center gap-3",
                ),
                class_name="mt-4 pt-4 border-t border-zinc-900 flex items-center justify-between",
            ),
            class_name="p-4 bg-zinc-950/80 border-t border-zinc-900",
        ),
        class_name="w-64 h-screen shrink-0 border-r border-zinc-900 flex flex-col bg-zinc-950",
    )