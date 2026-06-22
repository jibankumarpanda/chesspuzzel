import reflex as rx
from frontend_code_analysis.components.sidebar import sidebar
from frontend_code_analysis.components.upload_page import upload_page_content
from frontend_code_analysis.components.solve_page import solve_page_content
from frontend_code_analysis.components.history_page import history_page_content
from frontend_code_analysis.components.statistics_page import statistics_page_content
from frontend_code_analysis.states.navigation import NavigationState
from frontend_code_analysis.states.history_state import HistoryState, init_history
from frontend_code_analysis.states.statistics_state import StatisticsState

# Initialize persistence layer at import time
import logging

try:
    init_history()
except Exception:
    logging.exception("Unexpected error")


# Layout wrapper to handle custom theme and consistent grid structure
def lab_shell(content: rx.Component) -> rx.Component:
    return rx.el.div(
        sidebar(),
        rx.el.main(
            rx.el.div(content, class_name="max-w-7xl mx-auto"),
            class_name="flex-1 bg-zinc-950 text-zinc-100 p-8 overflow-y-auto",
        ),
        class_name=rx.cond(
            NavigationState.is_dark_mode,
            "flex h-screen w-screen bg-zinc-950 font-sans",
            "flex h-screen w-screen bg-zinc-100 font-sans invert",  # Simulated inverted light mode terminal
        ),
    )


# 1. Home / Dashboard Page Component
def index() -> rx.Component:
    home_content = rx.el.div(
        # Welcome Header Section
        rx.el.div(
            rx.el.div(
                rx.el.span(
                    "ENGINE ENVIRONMENT",
                    class_name="text-xs font-mono tracking-widest text-amber-500 bg-amber-500/10 px-2.5 py-1 rounded border border-amber-500/20 uppercase font-semibold",
                ),
                rx.el.h1(
                    "Chessboard Puzzle Solver",
                    class_name="text-4xl font-bold tracking-tight text-zinc-100 font-mono mt-3 uppercase",
                ),
                rx.el.p(
                    "An interactive engine optimized for constraint-satisfaction problems on arbitrary boards. Visualize backtracking, conflict logs, and solution spaces in real-time.",
                    class_name="text-zinc-400 mt-2 text-sm max-w-2xl leading-relaxed",
                ),
                class_name="flex-1",
            ),
            class_name="border-b border-zinc-900 pb-6 mb-8",
        ),
        # Quick Links / Action Hub
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon(
                            "cloud_upload", class_name="h-6 w-6 text-amber-500"
                        ),
                        rx.el.h3(
                            "Upload Dataset",
                            class_name="font-mono text-base font-bold text-zinc-200 uppercase tracking-wider",
                        ),
                        class_name="flex items-center gap-3 mb-2",
                    ),
                    rx.el.p(
                        "Load board dimensions, pieces (Queens, Knights, Bishops, Rooks) and solver rules from simple formatted txt files.",
                        class_name="text-xs text-zinc-400 leading-relaxed",
                    ),
                    rx.el.button(
                        "GO TO UPLOAD",
                        on_click=lambda: NavigationState.set_page("/upload"),
                        class_name="mt-4 w-full py-2 bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 text-xs font-mono tracking-widest text-amber-500 hover:text-amber-400 transition-colors uppercase rounded",
                    ),
                    class_name="bg-zinc-950 border border-zinc-900 p-6 rounded-xl hover:border-zinc-800 transition-all duration-200",
                ),
                class_name="w-full md:w-1/2 lg:w-1/3",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon("cpu", class_name="h-6 w-6 text-amber-500"),
                        rx.el.h3(
                            "Constraint Engine",
                            class_name="font-mono text-base font-bold text-zinc-200 uppercase tracking-wider",
                        ),
                        class_name="flex items-center gap-3 mb-2",
                    ),
                    rx.el.p(
                        "Control backtracking parameters, limit search iterations, step through search node paths, and generate coordinate files.",
                        class_name="text-xs text-zinc-400 leading-relaxed",
                    ),
                    rx.el.button(
                        "LAUNCH SOLVER",
                        on_click=lambda: NavigationState.set_page("/solve"),
                        class_name="mt-4 w-full py-2 bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 text-xs font-mono tracking-widest text-amber-500 hover:text-amber-400 transition-colors uppercase rounded",
                    ),
                    class_name="bg-zinc-950 border border-zinc-900 p-6 rounded-xl hover:border-zinc-800 transition-all duration-200",
                ),
                class_name="w-full md:w-1/2 lg:w-1/3",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon("history", class_name="h-6 w-6 text-amber-500"),
                        rx.el.h3(
                            "Database Records",
                            class_name="font-mono text-base font-bold text-zinc-200 uppercase tracking-wider",
                        ),
                        class_name="flex items-center gap-3 mb-2",
                    ),
                    rx.el.p(
                        "Retrieve previously resolved boards, execution benchmarks, nodes explored, and historical PDF summaries.",
                        class_name="text-xs text-zinc-400 leading-relaxed",
                    ),
                    rx.el.button(
                        "VIEW DATABASE",
                        on_click=lambda: NavigationState.set_page("/history"),
                        class_name="mt-4 w-full py-2 bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 text-xs font-mono tracking-widest text-amber-500 hover:text-amber-400 transition-colors uppercase rounded",
                    ),
                    class_name="bg-zinc-950 border border-zinc-900 p-6 rounded-xl hover:border-zinc-800 transition-all duration-200",
                ),
                class_name="w-full md:w-1/2 lg:w-1/3",
            ),
            class_name="flex flex-wrap gap-6 mb-8",
        ),
        # Quick Demo Solver Section
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon("zap", class_name="h-5 w-5 text-amber-500"),
                    rx.el.h2(
                        "Quick Lab Demo: 8-Queens Benchmark",
                        class_name="font-mono text-lg font-bold text-zinc-200 uppercase tracking-wider",
                    ),
                    class_name="flex items-center gap-3 mb-4",
                ),
                rx.el.p(
                    "Verify execution on the classic N-Queens puzzle with a standard 8x8 chessboard size, 8 pieces, and an exhaustive unique constraint check.",
                    class_name="text-xs text-zinc-400 mb-6",
                ),
                rx.el.div(
                    # Mock grid mimicking a real board for the static demo visual
                    rx.el.div(
                        # Simulating 8x8 chessboard layout
                        rx.el.div(
                            rx.el.div(
                                "♕",
                                class_name="flex items-center justify-center font-mono text-xl text-amber-500 bg-zinc-900/60",
                            ),
                            rx.el.div("", class_name="bg-zinc-950"),
                            rx.el.div("", class_name="bg-zinc-900/60"),
                            rx.el.div("", class_name="bg-zinc-950"),
                            rx.el.div("", class_name="bg-zinc-900/60"),
                            rx.el.div("", class_name="bg-zinc-950"),
                            rx.el.div("", class_name="bg-zinc-900/60"),
                            rx.el.div("", class_name="bg-zinc-950"),
                            rx.el.div("", class_name="bg-zinc-950"),
                            rx.el.div("", class_name="bg-zinc-900/60"),
                            rx.el.div("", class_name="bg-zinc-950"),
                            rx.el.div("", class_name="bg-zinc-900/60"),
                            rx.el.div(
                                "♕",
                                class_name="flex items-center justify-center font-mono text-xl text-amber-500 bg-zinc-950",
                            ),
                            rx.el.div("", class_name="bg-zinc-900/60"),
                            rx.el.div("", class_name="bg-zinc-950"),
                            rx.el.div("", class_name="bg-zinc-900/60"),
                            rx.el.div("", class_name="bg-zinc-900/60"),
                            rx.el.div("", class_name="bg-zinc-950"),
                            rx.el.div("", class_name="bg-zinc-900/60"),
                            rx.el.div("", class_name="bg-zinc-950"),
                            rx.el.div("", class_name="bg-zinc-900/60"),
                            rx.el.div("", class_name="bg-zinc-950"),
                            rx.el.div("", class_name="bg-zinc-900/60"),
                            rx.el.div(
                                "♕",
                                class_name="flex items-center justify-center font-mono text-xl text-amber-500 bg-zinc-950",
                            ),
                            class_name="grid grid-cols-8 grid-rows-3 border border-zinc-800 rounded-lg overflow-hidden h-40",
                        ),
                        class_name="flex-1",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.p(
                                "METRICS PREVIEW",
                                class_name="font-mono text-xs text-zinc-500 tracking-wider mb-3 uppercase font-bold",
                            ),
                            rx.el.div(
                                rx.el.div(
                                    rx.el.p(
                                        "Nodes Explored",
                                        class_name="text-zinc-500",
                                    ),
                                    rx.el.p(
                                        "113",
                                        class_name="text-zinc-200 font-bold",
                                    ),
                                    class_name="flex justify-between py-1.5 border-b border-zinc-900",
                                ),
                                rx.el.div(
                                    rx.el.p(
                                        "Backtracks", class_name="text-zinc-500"
                                    ),
                                    rx.el.p(
                                        "24",
                                        class_name="text-zinc-200 font-bold",
                                    ),
                                    class_name="flex justify-between py-1.5 border-b border-zinc-900",
                                ),
                                rx.el.div(
                                    rx.el.p(
                                        "Solutions Found",
                                        class_name="text-zinc-500",
                                    ),
                                    rx.el.p(
                                        "92",
                                        class_name="text-zinc-200 font-bold",
                                    ),
                                    class_name="flex justify-between py-1.5 border-b border-zinc-900",
                                ),
                                rx.el.div(
                                    rx.el.p(
                                        "Execution Time",
                                        class_name="text-zinc-500",
                                    ),
                                    rx.el.p(
                                        "0.014s",
                                        class_name="text-amber-500 font-bold font-mono",
                                    ),
                                    class_name="flex justify-between py-1.5",
                                ),
                                class_name="font-mono text-xs",
                            ),
                            class_name="p-4 bg-zinc-900/40 border border-zinc-900 rounded-lg w-full md:w-64 flex flex-col justify-between",
                        ),
                        class_name="shrink-0 flex",
                    ),
                    class_name="flex flex-col md:flex-row gap-6",
                ),
                class_name="bg-zinc-950 border border-zinc-900 p-6 rounded-xl",
            ),
            class_name="mb-8",
        ),
    )
    return lab_shell(home_content)


# 2. About Page Component
def about() -> rx.Component:
    about_content = rx.el.div(
        rx.el.div(
            rx.el.span(
                "ALGORITHMS & ARCHITECTURE",
                class_name="text-xs font-mono tracking-widest text-amber-500 bg-amber-500/10 px-2.5 py-1 rounded border border-amber-500/20 uppercase font-semibold",
            ),
            rx.el.h1(
                "About the Puzzle Solver",
                class_name="text-4xl font-bold tracking-tight text-zinc-100 font-mono mt-3 uppercase",
            ),
            rx.el.p(
                "Explore the algorithms, formal logic, and architectural stack powering the constraint satisfiability solver.",
                class_name="text-zinc-400 mt-2 text-sm max-w-2xl leading-relaxed",
            ),
            class_name="border-b border-zinc-900 pb-6 mb-8",
        ),
        # Algorithm Details
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon(
                            "git-fork", class_name="h-5 w-5 text-amber-500"
                        ),
                        rx.el.h2(
                            "Backtracking Search with DFS",
                            class_name="font-mono text-base font-bold text-zinc-200 uppercase tracking-wider",
                        ),
                        class_name="flex items-center gap-3 mb-3",
                    ),
                    rx.el.p(
                        "The solver maps the placement of chess pieces as a Depth-First Search over a state-space tree. Placing a piece in row 'r' acts as a decision branch. If constraints are violated, the solver cuts off the subtree, backtracks to the preceding valid row decision, and tests subsequent positions.",
                        class_name="text-xs text-zinc-400 leading-relaxed",
                    ),
                    class_name="bg-zinc-950 border border-zinc-900 p-6 rounded-xl",
                ),
                class_name="w-full md:w-1/2",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon(
                            "shield-alert", class_name="h-5 w-5 text-amber-500"
                        ),
                        rx.el.h2(
                            "Constraint-Satisfaction Programming",
                            class_name="font-mono text-base font-bold text-zinc-200 uppercase tracking-wider",
                        ),
                        class_name="flex items-center gap-3 mb-3",
                    ),
                    rx.el.p(
                        "Conflict detection is formal and modular: (a) No-Attack rules utilize row, column, and diagonal offsets; (b) Knight rules inspect fixed (±1, ±2) configurations; (c) Custom guidelines filter forbidden coordinate sets. Violations trigger immediate pruning to prevent exhaustive state exploration.",
                        class_name="text-xs text-zinc-400 leading-relaxed",
                    ),
                    class_name="bg-zinc-950 border border-zinc-900 p-6 rounded-xl",
                ),
                class_name="w-full md:w-1/2",
            ),
            class_name="flex flex-col md:flex-row gap-6 mb-8",
        ),
        # Technical Stack Dashboard
        rx.el.div(
            rx.el.div(
                rx.el.h2(
                    "System Architecture & Tech Stack",
                    class_name="font-mono text-lg font-bold text-zinc-200 uppercase tracking-wider mb-4",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.p(
                            "Core Engine",
                            class_name="text-zinc-500 font-mono text-xs",
                        ),
                        rx.el.p(
                            "Pure Python 3.13, utilizing generator-based state yield recursion to optimize memory overhead.",
                            class_name="text-zinc-300 font-mono text-xs mt-1",
                        ),
                        class_name="p-4 bg-zinc-900/30 border border-zinc-900 rounded-lg",
                    ),
                    rx.el.div(
                        rx.el.p(
                            "User Interface",
                            class_name="text-zinc-500 font-mono text-xs",
                        ),
                        rx.el.p(
                            "Reflex Web framework, leveraging React and Tailwind CSS v4 for hardware-accelerated rendering.",
                            class_name="text-zinc-300 font-mono text-xs mt-1",
                        ),
                        class_name="p-4 bg-zinc-900/30 border border-zinc-900 rounded-lg",
                    ),
                    rx.el.div(
                        rx.el.p(
                            "Database Layer",
                            class_name="text-zinc-500 font-mono text-xs",
                        ),
                        rx.el.p(
                            "SQLite lightweight storage, storing serialized solution coordinates and node exploration speed benchmarks.",
                            class_name="text-zinc-300 font-mono text-xs mt-1",
                        ),
                        class_name="p-4 bg-zinc-900/30 border border-zinc-900 rounded-lg",
                    ),
                    class_name="grid grid-cols-1 md:grid-cols-3 gap-4",
                ),
                class_name="bg-zinc-950 border border-zinc-900 p-6 rounded-xl mb-8",
            )
        ),
        # Setup & Run Instructions
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon("terminal", class_name="h-6 w-6 text-amber-500"),
                    rx.el.h2(
                        "Local Setup & Deploy Instructions",
                        class_name="font-mono text-base font-bold text-zinc-200 uppercase tracking-wider",
                    ),
                    class_name="flex items-center gap-3 mb-4",
                ),
                rx.el.div(
                    rx.el.p(
                        "1. Backend folder placement",
                        class_name="font-mono text-xs text-amber-400 font-bold tracking-wider uppercase mb-1",
                    ),
                    rx.el.p(
                        "Place the project's algorithms/, parser/, and database/ packages directly next to this Reflex app's root (alongside rxconfig.py). Once detected, the app automatically routes solver and persistence calls through the official engine instead of the bundled fallback.",
                        class_name="font-mono text-[11px] text-zinc-400 leading-relaxed mb-3",
                    ),
                    rx.el.pre(
                        "project_root/\n├── rxconfig.py\n├── app/                  # Reflex frontend (this app)\n├── algorithms/           # solver engine\n├── parser/               # txt_parser.py\n├── database/             # SQLite layer\n└── uploads/              # sample .txt datasets",
                        class_name="font-mono text-[11px] text-zinc-300 bg-zinc-900/60 border border-zinc-900 rounded-md px-3 py-2 mb-4 whitespace-pre overflow-x-auto",
                    ),
                    rx.el.p(
                        "2. Install dependencies",
                        class_name="font-mono text-xs text-amber-400 font-bold tracking-wider uppercase mb-1",
                    ),
                    rx.el.pre(
                        "pip install -r requirements.txt",
                        class_name="font-mono text-[11px] text-zinc-300 bg-zinc-900/60 border border-zinc-900 rounded-md px-3 py-2 mb-4 whitespace-pre",
                    ),
                    rx.el.p(
                        "3. Run locally",
                        class_name="font-mono text-xs text-amber-400 font-bold tracking-wider uppercase mb-1",
                    ),
                    rx.el.pre(
                        "reflex init   # only needed once\nreflex run    # serves at http://localhost:3000",
                        class_name="font-mono text-[11px] text-zinc-300 bg-zinc-900/60 border border-zinc-900 rounded-md px-3 py-2 mb-4 whitespace-pre",
                    ),
                    rx.el.p(
                        "4. Deploy",
                        class_name="font-mono text-xs text-amber-400 font-bold tracking-wider uppercase mb-1",
                    ),
                    rx.el.p(
                        "Deploy to Reflex Cloud with `reflex deploy`, or any container host that supports Python 3.13. The app gracefully falls back to a local JSON history store when SQLite is unavailable, so it remains fully functional without backend packages present.",
                        class_name="font-mono text-[11px] text-zinc-400 leading-relaxed",
                    ),
                ),
                class_name="bg-zinc-950 border border-zinc-900 p-6 rounded-xl mb-8",
            )
        ),
        # Course / Academic Credit Information Card
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon(
                        "graduation-cap", class_name="h-6 w-6 text-amber-500"
                    ),
                    rx.el.h2(
                        "Course & Author Affiliation",
                        class_name="font-mono text-base font-bold text-zinc-200 uppercase tracking-wider",
                    ),
                    class_name="flex items-center gap-3 mb-3",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.p(
                            "COURSE / TERM:",
                            class_name="text-zinc-500 font-bold font-mono text-xs",
                        ),
                        rx.el.p(
                            "Computer Science - 4th Semester (Algorithms and Data Structures Lab)",
                            class_name="text-zinc-300 font-mono text-xs mt-1",
                        ),
                        class_name="py-2 border-b border-zinc-900",
                    ),
                    rx.el.div(
                        rx.el.p(
                            "AUTHOR / OPERATOR:",
                            class_name="text-zinc-500 font-bold font-mono text-xs",
                        ),
                        rx.el.p(
                            "[Insert Student Name / Lab Group ID]",
                            class_name="text-zinc-300 font-mono text-xs mt-1 italic",
                        ),
                        class_name="py-2 border-b border-zinc-900",
                    ),
                    rx.el.div(
                        rx.el.p(
                            "FACULTY REVIEWER:",
                            class_name="text-zinc-500 font-bold font-mono text-xs",
                        ),
                        rx.el.p(
                            "Department of Algorithms & Theory Study",
                            class_name="text-zinc-300 font-mono text-xs mt-1",
                        ),
                        class_name="py-2",
                    ),
                    class_name="mt-2",
                ),
                class_name="bg-zinc-950 border border-zinc-900 p-6 rounded-xl",
            )
        ),
    )
    return lab_shell(about_content)


# 3. Placeholder layouts to maintain navigable pages across routes in Phase 1
def upload_page() -> rx.Component:
    return lab_shell(upload_page_content())


def solve_page() -> rx.Component:
    return lab_shell(solve_page_content())


def history_page() -> rx.Component:
    return lab_shell(history_page_content())


def statistics_page() -> rx.Component:
    return lab_shell(statistics_page_content())


# App Configuration
app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(
            rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""
        ),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;700&display=swap",
            rel="stylesheet",
        ),
    ],
)

app.add_page(index, route="/")
app.add_page(upload_page, route="/upload")
app.add_page(solve_page, route="/solve")
app.add_page(history_page, route="/history", on_load=HistoryState.refresh)
app.add_page(statistics_page, route="/statistics", on_load=StatisticsState.load)
app.add_page(about, route="/about")