from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from .models import ScoreRecord, ScoreSubmission

DEFAULT_DB_PATH = Path("data/scorepeek.sqlite")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ScoreStore:
    def __init__(self, db_path: str | Path | None = None):
        self.db_path = Path(db_path or os.getenv("SCOREBOARD_DB_PATH", DEFAULT_DB_PATH))
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_id TEXT NOT NULL,
                    assessment TEXT NOT NULL,
                    participant_hash TEXT NOT NULL,
                    score REAL NOT NULL,
                    max_score REAL NOT NULL,
                    normalized_score REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(course_id, assessment, participant_hash)
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_scores_course_assessment ON scores(course_id, assessment)")

    def upsert_score(self, submission: ScoreSubmission, participant_hash: str) -> ScoreRecord:
        now = utc_now_iso()
        normalized = submission.normalized_score()
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO scores (
                    course_id, assessment, participant_hash,
                    score, max_score, normalized_score, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(course_id, assessment, participant_hash)
                DO UPDATE SET
                    score=excluded.score,
                    max_score=excluded.max_score,
                    normalized_score=excluded.normalized_score,
                    updated_at=excluded.updated_at
                """,
                (
                    submission.course_id,
                    submission.assessment,
                    participant_hash,
                    submission.score,
                    submission.max_score,
                    normalized,
                    now,
                    now,
                ),
            )
        return self.get_score(submission.course_id, submission.assessment, participant_hash)

    def get_score(self, course_id: str, assessment: str, participant_hash: str) -> ScoreRecord:
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT * FROM scores
                WHERE course_id = ? AND assessment = ? AND participant_hash = ?
                """,
                (course_id, assessment, participant_hash),
            ).fetchone()
        if row is None:
            raise KeyError("score record not found")
        return self._row_to_record(row)

    def list_scores(self, course_id: str, assessment: str) -> list[ScoreRecord]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM scores
                WHERE course_id = ? AND assessment = ?
                ORDER BY normalized_score ASC, updated_at ASC
                """,
                (course_id, assessment),
            ).fetchall()
        return [self._row_to_record(row) for row in rows]

    def delete_score(self, course_id: str, assessment: str, participant_hash: str) -> bool:
        with self.connect() as conn:
            cur = conn.execute(
                """
                DELETE FROM scores
                WHERE course_id = ? AND assessment = ? AND participant_hash = ?
                """,
                (course_id, assessment, participant_hash),
            )
            return cur.rowcount > 0

    def seed_scores(self, submissions: Iterable[ScoreSubmission], participant_prefix: str = "demo") -> None:
        for idx, submission in enumerate(submissions):
            self.upsert_score(submission, f"{participant_prefix}-{idx}")

    @staticmethod
    def _row_to_record(row: sqlite3.Row) -> ScoreRecord:
        return ScoreRecord(
            course_id=row["course_id"],
            assessment=row["assessment"],
            participant_hash=row["participant_hash"],
            score=float(row["score"]),
            max_score=float(row["max_score"]),
            normalized_score=float(row["normalized_score"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
