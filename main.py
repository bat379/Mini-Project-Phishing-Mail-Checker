"""
PhishGuard - Phishing Email Awareness & Analysis Toolkit
Entry point for the application.

Educational use only. See README.md for scope and limitations.
"""
from __future__ import annotations

import sys
from pathlib import Path

import customtkinter as ctk

from database.database import Database
from gui.dashboard import App
from utils.logger import get_logger

logger = get_logger(__name__)

APP_NAME = "PhishGuard"
APP_MIN_WIDTH = 1100
APP_MIN_HEIGHT = 700
DB_PATH = Path(__file__).parent / "database" / "phishguard.db"


def main() -> None:
    """Initialize the database, configure the GUI theme, and launch PhishGuard."""
    try:
        logger.info("Starting %s", APP_NAME)

        # Ensure the database and its tables exist before the GUI needs them.
        db = Database(DB_PATH)
        db.initialize()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        app = App(db=db)
        app.title(f"{APP_NAME} — Phishing Email Awareness & Analysis Toolkit")
        app.minsize(APP_MIN_WIDTH, APP_MIN_HEIGHT)
        app.geometry(f"{APP_MIN_WIDTH}x{APP_MIN_HEIGHT}")
        app.mainloop()

    except Exception:  # noqa: BLE001 - top-level guard, logged with traceback
        logger.exception("Fatal error while starting %s", APP_NAME)
        raise
    finally:
        logger.info("%s shut down", APP_NAME)


if __name__ == "__main__":
    sys.exit(main())
