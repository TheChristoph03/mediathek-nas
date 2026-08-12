from __future__ import annotations

from pathlib import Path
from typing import Any

from app.core.config import DEFAULT_APP_SETTINGS, env_managed_settings
from app.db.database import database


class AppSettingsService:
    BOOL_KEYS = {
        "scheduler_enabled",
        "create_nfo_sidecar",
        "create_json_sidecar",
        "skip_duplicates",
        "plex_enabled",
        "plex_auto_scan",
        "jellyfin_enabled",
        "jellyfin_auto_scan",
        "infuse_enabled",
    }
    INT_KEYS = {"concurrent_downloads", "max_retries", "rule_run_limit"}
    PATH_KEYS = {"download_root"}

    def locked_keys(self) -> list[str]:
        """Settings pinned by the environment. These are read-only in the UI."""
        return sorted(env_managed_settings().keys())

    def get_all(self) -> dict[str, Any]:
        items = database.fetch_all("SELECT key, value FROM settings")
        merged = {**DEFAULT_APP_SETTINGS, **{row["key"]: row["value"] for row in items}}
        return {key: self._coerce_value(key, value) for key, value in merged.items()}

    def update(self, payload: dict[str, Any]) -> dict[str, Any]:
        updates: list[tuple[Any, ...]] = []
        current = self.get_all()
        locked = set(self.locked_keys())
        for key, value in payload.items():
            if value is None or key not in DEFAULT_APP_SETTINGS:
                continue
            if key in locked:
                # Pinned by the environment; silently ignore so the UI cannot
                # write a value that would be overwritten on the next restart.
                continue
            normalized = self._normalize_value(key, value)
            current[key] = self._coerce_value(key, normalized)
            updates.append((key, normalized))

        if "download_root" in payload and current["download_root"]:
            Path(current["download_root"]).mkdir(parents=True, exist_ok=True)

        if updates:
            database.execute_many(
                """
                INSERT INTO settings(key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                updates,
            )
        return self.get_all()

    def _normalize_value(self, key: str, value: Any) -> str:
        if key in self.BOOL_KEYS:
            return "1" if bool(value) else "0"
        if key in self.INT_KEYS:
            return str(int(value))
        if key in self.PATH_KEYS:
            return str(Path(str(value)).expanduser())
        return str(value).strip()

    def _coerce_value(self, key: str, value: Any) -> Any:
        if key in self.BOOL_KEYS:
            return str(value) in {"1", "true", "True"}
        if key in self.INT_KEYS:
            return int(value)
        return value


app_settings_service = AppSettingsService()
