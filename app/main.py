import sys
from pathlib import Path

# Add backend directory to sys.path so backend/app/ can be imported
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Import the actual FastAPI application from backend/app/main.py
from backend.app.main import app

