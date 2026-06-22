"""
test_backend.py
-----------------
Quick smoke-test / sanity-check script for the backend modules
(parser, algorithms, database) before wiring up the Streamlit UI.

Not a formal pytest suite (though it could easily be adapted into
one) -- just a linear script that exercises each piece of backend
functionality and prints PASS/FAIL so issues are caught early.
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(__file__))

from parser.txt_parser import parse_dataset_text, parse_dataset_file, DatasetParseError
from algorithms import solve_puzzle
from algorithms.constraints import is_valid_placement, PieceType, queen_attacks, knight_attacks
from database.db import (
    init_db, insert_puzzle, insert_solution, get_all_puzzles,
    get_solutions_for_puzzle, search_puzzles, serialize_solution_payload,
    deserialize_solution_payload,
)
from database.models import Puzzle, Solution

TEST_DB_PATH = "/home/claude/chess-puzzle-solver/test_chess.db"

passed = 0
failed = 0


def check(label, condition):
    global passed, failed
    if condition:
        print(f"PASS: {label}")
        passed += 1
    else:
        print(f"FAIL: {label}")
        failed += 1


# ----------------------------------------------------------------------
print("\n=== TESTING PARSER ===")
# ----------------------------------------------------------------------

valid_text = "BOARD 8 8\nPIECE QUEEN\nCOUNT 8\nCONSTRAINT NO_ATTACK\n"
ds = parse_dataset_text(valid_text, filename="t.txt")
check("Parser parses valid 8-queens dataset", ds.board_rows == 8 and ds.piece_count == 8)

try:
    parse_dataset_text("BOARD 8 8\nPIECE QUEEN\n")
    check("Parser rejects missing directives", False)
except DatasetParseError:
    check("Parser rejects missing directives", True)

try:
    parse_dataset_text("BOARD 8 8\nPIECE QUEEN\nCOUNT 100\nCONSTRAINT NO_ATTACK\n")
    check("Parser rejects COUNT exceeding board rows for queens", False)
except DatasetParseError:
    check("Parser rejects COUNT exceeding board rows for queens", True)

try:
    parse_dataset_text("BOARD 8 8\nPIECE DRAGON\nCOUNT 8\nCONSTRAINT NO_ATTACK\n")
    check("Parser rejects unsupported piece type", False)
except DatasetParseError:
    check("Parser rejects unsupported piece type", True)

ds_file = parse_dataset_file("/home/claude/chess-puzzle-solver/uploads/sample_8queens.txt")
check("Parser reads sample_8queens.txt from disk", ds_file.piece_type == "QUEEN")


# ----------------------------------------------------------------------
print("\n=== TESTING CONSTRAINTS ===")
# ----------------------------------------------------------------------

check("Queen attacks same row", queen_attacks((0, 0), (0, 5)))
check("Queen attacks same column", queen_attacks((0, 0), (5, 0)))
check("Queen attacks diagonal", queen_attacks((0, 0), (3, 3)))
check("Queen does NOT attack non-aligned square", not queen_attacks((0, 0), (1, 3)))
check("Knight attacks L-shape (1,2)", knight_attacks((0, 0), (1, 2)))
check("Knight does NOT attack (1,1)", not knight_attacks((0, 0), (1, 1)))

check(
    "is_valid_placement rejects conflicting queen",
    not is_valid_placement((0, 5), [(0, 0)], PieceType.QUEEN, 8, 8),
)
check(
    "is_valid_placement accepts non-conflicting queen",
    is_valid_placement((1, 2), [(0, 0)], PieceType.QUEEN, 8, 8),
)


# ----------------------------------------------------------------------
print("\n=== TESTING SOLVERS ===")
# ----------------------------------------------------------------------

# Classic 8-Queens: known to have exactly 92 solutions.
result_8q = solve_puzzle("QUEEN", 8, 8, 8, max_solutions=None)
check(f"8-Queens finds 92 solutions (got {result_8q.stats.solutions_found})",
      result_8q.stats.solutions_found == 92)
check("8-Queens execution time recorded", result_8q.stats.execution_time_seconds >= 0)
check("8-Queens nodes_explored > 0", result_8q.stats.nodes_explored > 0)
check("8-Queens steps recorded", len(result_8q.steps) > 0)

# 4-Queens: known to have exactly 2 solutions.
result_4q = solve_puzzle("QUEEN", 4, 4, 4, max_solutions=None)
check(f"4-Queens finds 2 solutions (got {result_4q.stats.solutions_found})",
      result_4q.stats.solutions_found == 2)

# Validate every 8-queens solution is actually conflict-free.
all_valid = True
for sol in result_8q.solutions:
    for i in range(len(sol)):
        for j in range(i + 1, len(sol)):
            if queen_attacks(sol[i], sol[j]):
                all_valid = False
check("All 8-Queens solutions are conflict-free", all_valid)

# Rook placement: 6 rooks on 6x6, expect 6! = 720 solutions.
result_rook = solve_puzzle("ROOK", 6, 6, 6, max_solutions=None)
check(f"6-Rooks finds 720 solutions (got {result_rook.stats.solutions_found})",
      result_rook.stats.solutions_found == 720)

# Knight placement: small board, just check it finds at least 1 valid solution.
result_knight = solve_puzzle("KNIGHT", 5, 5, 5, max_solutions=1)
check(f"5x5 Knight placement (5 knights) finds >=1 solution (got {result_knight.stats.solutions_found})",
      result_knight.stats.solutions_found >= 1)
if result_knight.solutions:
    sol = result_knight.solutions[0]
    no_conflicts = all(
        not knight_attacks(sol[i], sol[j])
        for i in range(len(sol)) for j in range(i + 1, len(sol))
    )
    check("Knight solution is conflict-free", no_conflicts)

# Bishop placement: small board sanity check.
result_bishop = solve_puzzle("BISHOP", 6, 6, 6, max_solutions=1)
check(f"6x6 Bishop placement (6 bishops) finds >=1 solution (got {result_bishop.stats.solutions_found})",
      result_bishop.stats.solutions_found >= 1)

# Unsupported piece type should raise.
try:
    solve_puzzle("DRAGON", 8, 8, 8)
    check("solve_puzzle rejects unsupported piece type", False)
except ValueError:
    check("solve_puzzle rejects unsupported piece type", True)


# ----------------------------------------------------------------------
print("\n=== TESTING DATABASE ===")
# ----------------------------------------------------------------------

if os.path.exists(TEST_DB_PATH):
    os.remove(TEST_DB_PATH)

init_db(TEST_DB_PATH)
check("Database file created", os.path.exists(TEST_DB_PATH))

puzzle = Puzzle(
    filename="sample_8queens.txt",
    board_size="8x8",
    piece_type="QUEEN",
    piece_count=8,
    constraint="NO_ATTACK",
)
puzzle_id = insert_puzzle(puzzle, TEST_DB_PATH)
check("Puzzle inserted with valid id", puzzle_id > 0)

payload = serialize_solution_payload(
    [[list(pos) for pos in sol] for sol in result_8q.solutions[:5]],
    result_8q.steps[:20],
)
solution_record = Solution(
    puzzle_id=puzzle_id,
    solution_data=payload,
    execution_time=result_8q.stats.execution_time_seconds,
    solution_count=result_8q.stats.solutions_found,
    nodes_explored=result_8q.stats.nodes_explored,
    backtracks=result_8q.stats.backtracks,
)
solution_id = insert_solution(solution_record, TEST_DB_PATH)
check("Solution inserted with valid id", solution_id > 0)

all_puzzles = get_all_puzzles(TEST_DB_PATH)
check("get_all_puzzles returns inserted puzzle", len(all_puzzles) == 1 and all_puzzles[0].filename == "sample_8queens.txt")

solutions_for_puzzle = get_solutions_for_puzzle(puzzle_id, TEST_DB_PATH)
check("get_solutions_for_puzzle returns inserted solution", len(solutions_for_puzzle) == 1)

decoded = deserialize_solution_payload(solutions_for_puzzle[0].solution_data)
check("Deserialized solution payload has 5 solutions", len(decoded["solutions"]) == 5)

search_results = search_puzzles("queen", TEST_DB_PATH)
check("search_puzzles finds puzzle by piece type", len(search_results) == 1)

search_results_none = search_puzzles("zzz_nonexistent", TEST_DB_PATH)
check("search_puzzles returns empty for no match", len(search_results_none) == 0)

os.remove(TEST_DB_PATH)


# ----------------------------------------------------------------------
print(f"\n=== RESULTS: {passed} passed, {failed} failed ===")
sys.exit(0 if failed == 0 else 1)
