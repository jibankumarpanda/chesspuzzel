# Build Prompt: Reflex Frontend for Chessboard Puzzle Solver

Paste everything below this line into a new session/tool to generate the Reflex frontend.

---

## Context

I have a **fully built and tested Python backend** for a Chessboard Puzzle Solver and Visualizer (a college 4th-semester project). I need you to build a **Reflex** (https://reflex.dev) frontend on top of it — Reflex compiles Python into a React frontend + FastAPI backend, so all state and event handlers must be written as Reflex `rx.State` classes, not Streamlit-style scripts.

Do not reimplement, rewrite, or modify any solver/parser/database logic. Only import and call the existing functions exactly as documented below. Your job is the Reflex app: pages, components, state management, styling, and wiring.

## Existing Backend — Exact API Surface

The backend lives in a package with this structure (already complete, do not touch):

```
chess-puzzle-solver/
├── algorithms/
│   ├── constraints.py    # PieceType, ConstraintType enums + conflict checks
│   ├── base_solver.py    # SolverStats, SolverResult dataclasses
│   ├── nqueens.py / knights.py / bishops.py / rooks.py
│   └── __init__.py       # exposes solve_puzzle()
├── parser/
│   └── txt_parser.py     # exposes parse_dataset_text(), parse_dataset_file(), PuzzleDataset, DatasetParseError
├── database/
│   ├── db.py             # SQLite CRUD functions
│   └── models.py         # Puzzle, Solution dataclasses
├── uploads/               # sample .txt dataset files
└── requirements.txt
```

### 1. Solver entry point — `algorithms/__init__.py`

```python
def solve_puzzle(
    piece_type: str,        # "QUEEN" | "KNIGHT" | "BISHOP" | "ROOK"
    board_rows: int,
    board_cols: int,
    piece_count: int,
    max_solutions: Optional[int] = None,   # None = find all
    record_steps: bool = True,
) -> SolverResult
```

Raises `ValueError` if `piece_type` is unsupported.

`SolverResult` (dataclass):
```python
solutions: List[List[Tuple[int, int]]]   # list of solutions; each solution is a list of (row, col) piece positions
steps: List[str]                          # e.g. "Step 1: Place Queen at (0,0)", "Step 3: Conflict detected at (1,1)", "Step 4: Backtrack"
stats: SolverStats
piece_type: PieceType
board_rows: int
board_cols: int
```

`SolverStats` (dataclass):
```python
nodes_explored: int
backtracks: int
solutions_found: int
execution_time_seconds: float
```

**Important performance notes for the UI:**
- Knight/Bishop solvers default `max_solutions=1` if not specified (exhaustive search is expensive — square-by-square subset search, not row-by-row).
- N-Queens/Rook are exhaustive by default (`max_solutions=None`) and use one-piece-per-row search — fast up to about N=10-11, but N=12+ can take 20+ seconds. **The UI must let the user cap `max_solutions` and must warn or disable "Find All" for board sizes above ~11x11 on Queen/Rook and ~6x6 on Knight/Bishop**, since those are subset searches over every square.

### 2. Dataset parser — `parser/txt_parser.py`

```python
def parse_dataset_text(text: str, filename: str = "uploaded_dataset.txt") -> PuzzleDataset
def parse_dataset_file(file_path: str) -> PuzzleDataset
```

Raises `DatasetParseError` (with a human-readable `.args[0]` message) on any invalid input — **catch this and show the message directly in the UI**, don't re-derive your own validation messages.

`PuzzleDataset` (dataclass):
```python
board_rows: int
board_cols: int
piece_type: str        # "QUEEN" | "KNIGHT" | "BISHOP" | "ROOK"
piece_count: int
constraint: str         # "NO_ATTACK" | "UNIQUE_ROW_COL" | "CUSTOM"
raw_text: str
filename: str
```
Has a `.summary()` method returning a one-line string for display.

Expected uploaded `.txt` file format (4 required lines, any order, `#` = comment):
```
BOARD 8 8
PIECE QUEEN
COUNT 8
CONSTRAINT NO_ATTACK
```

### 3. Database layer — `database/db.py` + `database/models.py`

```python
def init_db(db_path: str = DEFAULT_DB_PATH) -> None
def insert_puzzle(puzzle: Puzzle, db_path=...) -> int          # returns new puzzle id
def get_puzzle(puzzle_id: int, db_path=...) -> Optional[Puzzle]
def get_all_puzzles(db_path=..., limit: int = 200) -> List[Puzzle]
def search_puzzles(query: str, db_path=...) -> List[Puzzle]
def delete_puzzle(puzzle_id: int, db_path=...) -> None

def insert_solution(solution: Solution, db_path=...) -> int    # returns new solution id
def get_solutions_for_puzzle(puzzle_id: int, db_path=...) -> List[Solution]
def get_latest_solution_for_puzzle(puzzle_id: int, db_path=...) -> Optional[Solution]
def get_solution(solution_id: int, db_path=...) -> Optional[Solution]

def serialize_solution_payload(solutions: List[List[List[int]]], steps: List[str]) -> str
def deserialize_solution_payload(payload: str) -> dict   # {"solutions": [...], "steps": [...]}
```

`Puzzle` (dataclass): `id, filename, board_size (str "8x8"), piece_type, piece_count, constraint, created_at`
`Solution` (dataclass): `id, puzzle_id, solution_data (JSON str), execution_time, solution_count, nodes_explored, backtracks, created_at`

**Wiring rule:** after every solve, you must (a) insert a `Puzzle` row, (b) JSON-serialize `SolverResult.solutions`/`.steps` via `serialize_solution_payload` (convert tuples to lists first) and insert a `Solution` row linked by `puzzle_id`, (c) call `init_db()` once at app startup before anything touches the database.

---

## What To Build

### Tech requirements
- **Reflex** (latest stable), Python-only, no hand-written JS/React.
- Import the four backend packages directly (`algorithms`, `parser`, `database`) — assume they sit at the project root alongside the Reflex app, or instruct me exactly where to place them relative to the Reflex app structure (e.g. a `chess_solver/backend/` subpackage) and show the resulting import paths.
- All solver calls must run via `rx.event(background=True)` (Reflex background events) since N-Queens at N≥11 and Knight/Bishop searches can take seconds — the UI must not freeze, and must show a loading/progress state with live-updating stats (nodes explored, backtracks so far) if feasible, or at minimum a spinner + "Solving..." indicator that doesn't block navigation.
- SQLite file path: use `database.DEFAULT_DB_PATH` as-is; don't hardcode a different path.

### Pages / Routes

1. **Home (`/`)** — Project title, short description, quick links to Upload and History, a "Quick Solve" card showing a default 8-Queens demo.

2. **Upload Puzzle (`/upload`)**
   - File upload widget accepting `.txt` only (use `rx.upload`).
   - On upload, read file bytes, decode as text, call `parse_dataset_text()`.
   - On `DatasetParseError`, show the exact error message in a dismissible error banner — do not swallow or paraphrase it.
   - On success, show a parsed-dataset summary card (`PuzzleDataset.summary()` plus a breakdown table of board size / piece / count / constraint) with a "Solve This Puzzle" button.
   - Also support manual entry (no file) via a form: board rows, board cols, piece type dropdown (Queen/Knight/Bishop/Rook), piece count, constraint dropdown — for users who don't want to write a `.txt` file. Validate the same way the parser would (reuse `parse_dataset_text` by constructing the equivalent text block from form fields, so validation logic is never duplicated).
   - Provide 4 one-click "load sample" buttons pulling from the existing `uploads/sample_8queens.txt`, `sample_knights.txt`, `sample_bishops.txt`, `sample_rooks.txt`.

3. **Solve Puzzle (`/solve`)**
   - Shows the current `PuzzleDataset` (from state, set by the Upload page).
   - Controls: "Max solutions to find" (number input or "All" toggle — disable/warn per the performance notes above), "Record steps" toggle.
   - "Run Solver" button → background event → calls `solve_puzzle()` → on completion, persist to DB (`insert_puzzle` + `insert_solution`) and store the `SolverResult` in state.
   - **Chessboard visualization**: an SVG or CSS-grid board (size = `board_rows` x `board_cols`) with alternating light/dark squares, rendered piece glyphs (♕♘♗♖ Unicode chess symbols, colored distinctly from the board) at the positions of the currently-selected solution. Must be responsive (scales board square size to viewport, not fixed pixels) and highlight the active solution clearly.
   - **Step-by-step playback panel** next to/below the board: shows `steps[]` one at a time with Play / Pause / Next / Previous / Reset controls and a speed selector; stepping through "Place X at (r,c)" should animate that piece appearing on the board, "Backtrack" should animate the most recent piece disappearing, "Conflict detected" should flash the offending square red briefly. Keep this purely client-state (no backend calls) — it just replays the already-computed `steps` list.
   - **Solution navigator**: "Previous Solution" / "Next Solution" buttons + "Solution X of N" counter, switching which solution's positions are drawn on the board. Disable buttons at the boundaries.
   - **Statistics panel**: Total Solutions, Nodes Explored, Backtracks, Execution Time (seconds, formatted to ms precision) — pulled directly from `SolverResult.stats`.
   - Download buttons: "Download Solution as TXT" (plain text dump of the selected solution's coordinates + stats) and "Download Solution as PDF" (simple one-page summary: puzzle metadata, selected solution board diagram or coordinate list, stats). Use `fpdf2` for the PDF (already in `requirements.txt`) — generate server-side in an event handler and trigger `rx.download`.

4. **History (`/history`)**
   - Table of all puzzles from `get_all_puzzles()`: filename, board size, piece type, count, constraint, created_at, with a search box wired to `search_puzzles()`.
   - Each row has "View Solutions" (loads `get_solutions_for_puzzle()` for that puzzle, lets the user reopen the board visualization with that historical solution set — reuse the same board/navigator/stats components from the Solve page rather than duplicating them) and "Delete" (calls `delete_puzzle()`, with a confirm dialog).

5. **Statistics Dashboard (`/statistics`)**
   - Aggregate view across all stored puzzles/solutions: total puzzles solved, total solutions found across history, average execution time, a simple bar or line chart (Reflex's built-in `rx.recharts` wrapper) of execution time or nodes-explored per puzzle over time, and a breakdown by piece type (count of puzzles per piece type).

6. **About (`/about`)** — Project description, algorithms used (Backtracking, DFS, CSP framing, Branch & Bound), tech stack, and author/course credit placeholder text I can fill in.

### Global / Cross-cutting requirements

- **Sidebar navigation** present on every page: Home, Upload Puzzle, Solve Puzzle, History, Statistics, About — matching the original spec's menu structure exactly.
- **Dark mode toggle** using Reflex's built-in color mode (`rx.color_mode.button` / `rx.color_mode_cond`) — applies app-wide, persists via Reflex's local storage support.
- **Error handling**: every backend call (`solve_puzzle`, parser functions, db functions) wrapped in try/except inside the relevant event handler, surfaced to the user via a toast or banner (`rx.toast` or an `rx.callout`), never a raw traceback.
- **Loading states**: skeleton/spinner components while a background solve event is running; disable the "Run Solver" button while running to prevent duplicate submissions.
- State should be split logically across multiple `rx.State` subclasses (e.g. `UploadState`, `SolverState`, `HistoryState`, `StatsState`) rather than one giant state class, since they map to different pages/concerns — but share data between them via Reflex's substate composition where the Solve page needs the dataset produced by the Upload page.

### Visual design direction

This needs to look like a polished, modern web app — not a default Reflex template. Use a dark, slightly "engine/lab" aesthetic appropriate for a chess/algorithms tool: rich near-black background, a single confident accent color (e.g. amber or teal) for interactive elements and highlighted board squares, clean monospace or geometric sans for stats/numbers, generous spacing, subtle elevation/shadow on cards, smooth transitions on the step-playback animations. Avoid generic Bootstrap-blue defaults.

### Deliverables I expect from you

1. Full Reflex project structure (`rxconfig.py`, `.web/` is auto-generated so skip it, `chess_solver/chess_solver.py` or your chosen module layout, `pages/`, `components/`, `states/`).
2. Exact instructions for where the existing `algorithms/`, `parser/`, `database/`, `uploads/` folders should be placed relative to the new Reflex project so imports resolve without modification.
3. Updated `requirements.txt` (merge Reflex + `fpdf2`, drop `streamlit`/`pandas` if unused, or keep `pandas` if you use it for the Statistics/History tables).
4. All code for every page, component, and state class — complete, runnable, no placeholders or "TODO: implement this."
5. A short README section on how to run it locally (`reflex init`, `reflex run`) and deploy (Reflex Cloud or equivalent).

Do not ask me clarifying questions about the backend's behavior — everything you need is specified above. If something is genuinely ambiguous (e.g. exact color hex codes), make a reasonable, well-justified design decision and proceed.
