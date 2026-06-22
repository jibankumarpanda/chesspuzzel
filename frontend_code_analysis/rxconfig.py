import sys
import os
from pathlib import Path

import reflex as rx

# Add backend directory to Python path so frontend can import algorithms/, parser/, database/
backend_dir = Path(__file__).parent.parent / "chess-puzzle-solver-backend" / "chess-puzzle-solver"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Initialize database tables on app startup (safe to call multiple times)
try:
    from frontend_code_analysis.states.history_state import init_history
    init_history()
except Exception:
    # Fallback if backend not available yet - will use JSON storage
    pass

config = rx.Config(app_name="frontend_code_analysis", plugins=[rx.plugins.TailwindV4Plugin()])
