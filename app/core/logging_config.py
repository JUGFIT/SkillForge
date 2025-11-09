# app/core/logging_config.py
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from app.core.config import settings

# -------------------------------------------------------------------
# 🧩 Log Directory Setup
# -------------------------------------------------------------------
LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "skillstack.log"


# -------------------------------------------------------------------
# ⚙️ Configure Root Logger
# -------------------------------------------------------------------
def setup_logging():
    """Initialize structured logging for the application."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Remove any existing handlers (avoid duplication on reload)
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Configure handlers
    console_handler = logging.StreamHandler(sys.stdout)
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=5_000_000, backupCount=3, encoding="utf-8"
    )

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] — %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )

    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Set up the root logger
    logging.basicConfig(
        level=log_level,
        handlers=[console_handler, file_handler],
    )

    logging.info("✅ Logging initialized successfully.")


# -------------------------------------------------------------------
# 🧠 Logger Getter
# -------------------------------------------------------------------
def get_logger(name: str = "SkillStack"):
    """Return a named logger instance (used across modules)."""
    return logging.getLogger(name)


# -------------------------------------------------------------------
# 🧩 Default global logger for import convenience
# -------------------------------------------------------------------
logger = get_logger("SkillStack")
