"""
config.py — central configuration. Every tunable lives here.
No magic strings or numbers should appear elsewhere in the codebase.
"""

from pathlib import Path
from datetime import datetime

# ── Project layout ────────────────────────────────────────────────────────────
ROOT_DIR   = Path(__file__).parent
OUTPUT_DIR = ROOT_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# ── LLM provider ─────────────────────────────────────────────────────────────
LLM_PROVIDER = "openrouter"          # "openai" | "anthropic" | "groq" | "openrouter"
LLM_MODEL    = "openai/gpt-4o"  # For OpenRouter, use standard model tags like "anthropic/claude-3.5-sonnet"
LLM_TEMPERATURE = 0.2            # low temp → deterministic, structured outputs
LLM_MAX_TOKENS  = 8192

# ── API keys (prefer env vars; fallback shown for dev convenience only) ───────
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY    = os.environ.get("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
GROQ_API_KEY      = os.environ.get("GROQ_API_KEY", "")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

# ── Data File ─────────────────────────────────────────────────────────────────
DATA_FILE_PATH    = os.environ.get("DATA_FILE_PATH", "")

# ── Data schema expectations ──────────────────────────────────────────────────
REQUIRED_COLUMNS = [
    "SCENARIO_NAME",    # e.g. "historical", "perfect"
    "SCHEDULE_TYPE",    # e.g. "expected", "cleared"
    "START_DATETIME",   # Start of interval
    "SOC",              # State of Energy (MWh)
    "CHARGE_ENERGY",    # Charged MWh >= 0
    "DISCHARGE_ENERGY", # Discharged MWh >= 0
    "PRICE_ENERGY",     # $/MWh
    "REVENUE",   # Total Revenue $
]

DATETIME_COLUMN = "START_DATETIME"
NUMERIC_COLUMNS = [c for c in REQUIRED_COLUMNS if c not in [DATETIME_COLUMN, "SCENARIO_NAME", "SCHEDULE_TYPE"]]

# ── Analysis thresholds ───────────────────────────────────────────────────────
HIGH_PRICE_PERCENTILE     = 0.90   # top decile = "high value" window
SLIPPAGE_THRESHOLD_PCT    = 0.10   # >10 % bid-vs-cleared gap = notable slippage
DISPATCH_DELTA_THRESHOLD  = 1.0    # MWh diff considered meaningful misalignment

# ── Report output ─────────────────────────────────────────────────────────────
# Each run gets its own timestamped file, e.g. trader_report_20260402_114438.md
_RUN_TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
REPORT_PATH = OUTPUT_DIR / f"trader_report_{_RUN_TIMESTAMP}.md"
