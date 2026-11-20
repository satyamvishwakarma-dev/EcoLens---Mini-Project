"""
Centralized configuration, paths, and constants for EcoLens.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load variables from .env in project root
load_dotenv()

# Directory resolution
PACKAGE_DIR = Path(__file__).resolve().parent        # src/ecolens_mini_project
SRC_DIR = PACKAGE_DIR.parent                         # src
PROJECT_ROOT = SRC_DIR.parent                        # repo root
FRONTEND_DIR = SRC_DIR / "frontend"                  # src/frontend
SCANS_DIR = PROJECT_ROOT / "saved_scans"
LOG_FILE = PROJECT_ROOT / "scan_history.json"

# Ensure saved_scans folder exists
SCANS_DIR.mkdir(exist_ok=True)

# Gemini & App Settings
API_KEY = os.getenv("GEMINI_API_KEY", "")
DEFAULT_CITY = os.getenv("DEFAULT_CITY", "Delhi")
MODEL_NAME = "gemini-4-hydrogen"

# Strict voice command mapping
VOICE_COMMANDS = {
    "scan": "scan",
    "save": "save",
    "clear": "clear",
    "history": "history",
    "quit": "quit",
    "exit": "quit",
}