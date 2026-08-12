import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from app.core.config import DEFAULT_APP_SETTINGS, env_managed_settings, settings


class Database:
    def __init__(self) -> None:
        self.path = settings.database_path

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS downloads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    external_id TEXT,
                    title TEXT NOT NULL,
                    channel TEXT,
                    topic TEXT,
                    description TEXT,
                    source_url TEXT NOT NULL,
                    website_url TEXT,
                    preview_url TEXT,
                    subtitle_url TEXT,
                    quality TEXT,
                    air_date TEXT,
                    duration_seconds INTEGER,
                    target_directory TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    final_path TEXT,
                    format_hint TEXT,
                    status TEXT NOT NULL,
                    progress REAL NOT NULL DEFAULT 0,
                    error_message TEXT,
                    retry_count INTEGER NOT NULL DEFAULT 0,
                    max_retries INTEGER NOT NULL DEFAULT 0,
                    duplicate_key TEXT,
                    duplicate_of_id INTEGER,
                    duplicate_reason TEXT,
                    imported INTEGER NOT NULL DEFAULT 0,
                    metadata_written INTEGER NOT NULL DEFAULT 0,
                    metadata_json TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    query TEXT NOT NULL DEFAULT '',
                    channel TEXT NOT NULL DEFAULT '',
                    topic TEXT NOT NULL DEFAULT '',
                    quality TEXT NOT NULL DEFAULT 'best',
                    min_duration_minutes INTEGER,
                    max_duration_minutes INTEGER,
                    target_directory TEXT,
                    keep_latest INTEGER,
                    auto_download INTEGER NOT NULL DEFAULT 0,
                    enabled INTEGER NOT NULL DEFAULT 1,
                    interval_minutes INTEGER NOT NULL DEFAULT 180,
                    folder_template TEXT,
                    filename_template TEXT,
                    last_run_at TEXT,
                    last_error TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS rule_matches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rule_id INTEGER NOT NULL,
                    external_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    channel TEXT,
                    topic TEXT,
                    air_date TEXT,
                    source_url TEXT NOT NULL,
                    quality TEXT,
                    website_url TEXT,
                    matched_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    download_id INTEGER,
                    FOREIGN KEY(rule_id) REFERENCES rules(id),
                    FOREIGN KEY(download_id) REFERENCES downloads(id),
                    UNIQUE(rule_id, external_id)
                );

                CREATE TABLE IF NOT EXISTS import_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_path TEXT NOT NULL,
                    source_kind TEXT NOT NULL,
                    imported_count INTEGER NOT NULL DEFAULT 0,
                    skipped_count INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

            self._ensure_columns(
                conn,
                "downloads",
                {
                    "preview_url": "TEXT",
                    "subtitle_url": "TEXT",
                    "format_hint": "TEXT",
                    "retry_count": "INTEGER NOT NULL DEFAULT 0",
                    "max_retries": "INTEGER NOT NULL DEFAULT 0",
                    "duplicate_key": "TEXT",
                    "duplicate_of_id": "INTEGER",
                    "duplicate_reason": "TEXT",
                    "imported": "INTEGER NOT NULL DEFAULT 0",
                    "metadata_written": "INTEGER NOT NULL DEFAULT 0",
                },
            )
            self._ensure_columns(
                conn,
                "rules",
                {
                    "interval_minutes": "INTEGER NOT NULL DEFAULT 180",
                    "folder_template": "TEXT",
                    "filename_template": "TEXT",
                    "last_error": "TEXT",
                },
            )

            for key, value in DEFAULT_APP_SETTINGS.items():
                conn.execute(
                    """
                    INSERT INTO settings(key, value)
                    VALUES (?, ?)
                    ON CONFLICT(key) DO NOTHING
                    """,
                    (key, value),
                )

            # Environment-managed settings win over stored values on every start.
            # Without this, a value seeded once (possibly wrong) could never be
            # corrected by redeploying with a fixed environment.
            for key, value in env_managed_settings().items():
                conn.execute(
                    """
                    INSERT INTO settings(key, value)
                    VALUES (?, ?)
                    ON CONFLICT(key) DO UPDATE SET value = excluded.value
                    """,
                    (key, value),
                )

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def fetch_all(self, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        with self.connection() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._normalize_row(row) for row in rows]

    def fetch_one(self, query: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
        with self.connection() as conn:
            row = conn.execute(query, params).fetchone()
        return self._normalize_row(row) if row else None

    def execute(self, query: str, params: tuple[Any, ...] = ()) -> int:
        with self.connection() as conn:
            cursor = conn.execute(query, params)
            return int(cursor.lastrowid)

    def execute_many(self, query: str, params_list: list[tuple[Any, ...]]) -> None:
        with self.connection() as conn:
            conn.executemany(query, params_list)

    def _ensure_columns(self, conn: sqlite3.Connection, table: str, columns: dict[str, str]) -> None:
        existing = {
            row["name"]
            for row in conn.execute(f"PRAGMA table_info({table})").fetchall()
        }
        for column, definition in columns.items():
            if column not in existing:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    def _normalize_row(self, row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        if "metadata_json" in data:
            data["metadata"] = json.loads(data.pop("metadata_json") or "{}")
        return data


database = Database()
