"""
SQLite persistence layer for PhishGuard.

Stores a local history of analyses performed by the user. No data ever
leaves the machine — this is a local learning log, not telemetry.
"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterator, Optional

from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class AnalysisRecord:
    """A single analyzed-email entry as stored in history."""

    email_name: str
    risk_score: int
    risk_level: str
    findings_summary: str
    report_path: Optional[str] = None
    analyzed_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    id: Optional[int] = None


class Database:
    """Thin wrapper around sqlite3 for PhishGuard's analysis history table."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            logger.exception("Database operation failed, rolled back.")
            raise
        finally:
            conn.close()

    def initialize(self) -> None:
        """Create tables if they do not already exist."""
        schema = """
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_name TEXT NOT NULL,
            risk_score INTEGER NOT NULL,
            risk_level TEXT NOT NULL,
            findings_summary TEXT NOT NULL,
            report_path TEXT,
            analyzed_at TEXT NOT NULL
        );
        """
        with self._connect() as conn:
            conn.execute(schema)
        logger.info("Database initialized at %s", self.db_path)

    def add_record(self, record: AnalysisRecord) -> int:
        """Insert an analysis record and return its new row id."""
        query = """
        INSERT INTO analysis_history
            (email_name, risk_score, risk_level, findings_summary, report_path, analyzed_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        with self._connect() as conn:
            cursor = conn.execute(
                query,
                (
                    record.email_name,
                    record.risk_score,
                    record.risk_level,
                    record.findings_summary,
                    record.report_path,
                    record.analyzed_at,
                ),
            )
            new_id = cursor.lastrowid
        logger.debug("Inserted analysis record id=%s", new_id)
        return new_id

    def get_all_records(self) -> list[AnalysisRecord]:
        """Return all history records, most recent first."""
        query = "SELECT * FROM analysis_history ORDER BY analyzed_at DESC"
        with self._connect() as conn:
            rows = conn.execute(query).fetchall()
        return [
            AnalysisRecord(
                id=row["id"],
                email_name=row["email_name"],
                risk_score=row["risk_score"],
                risk_level=row["risk_level"],
                findings_summary=row["findings_summary"],
                report_path=row["report_path"],
                analyzed_at=row["analyzed_at"],
            )
            for row in rows
        ]

    def get_summary_counts(self) -> dict[str, int]:
        """Return counts of analyses by risk level plus a total, for the dashboard."""
        query = "SELECT risk_level, COUNT(*) as cnt FROM analysis_history GROUP BY risk_level"
        with self._connect() as conn:
            rows = conn.execute(query).fetchall()

        counts = {"Low": 0, "Medium": 0, "High": 0}
        for row in rows:
            level = row["risk_level"]
            if level in counts:
                counts[level] = row["cnt"]
        counts["Total"] = sum(counts.values())
        return counts

    def delete_record(self, record_id: int) -> None:
        """Delete a single history record by id."""
        with self._connect() as conn:
            conn.execute("DELETE FROM analysis_history WHERE id = ?", (record_id,))
        logger.debug("Deleted analysis record id=%s", record_id)
