from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from app.core.config import DEFAULT_APP_SETTINGS, env_defaults
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
        """Kept for API compatibility. Nothing is locked any more."""
        return []

    def container_defaults(self) -> dict[str, str]:
        """Values the container environment suggests, offered as a reset target."""
        return env_defaults()

    def get_all(self) -> dict[str, Any]:
        items = database.fetch_all("SELECT key, value FROM settings")
        merged = {**DEFAULT_APP_SETTINGS, **{row["key"]: row["value"] for row in items}}
        return {key: self._coerce_value(key, value) for key, value in merged.items()}

    def update(self, payload: dict[str, Any]) -> dict[str, Any]:
        updates: list[tuple[Any, ...]] = []
        current = self.get_all()
        for key, value in payload.items():
            if value is None or key not in DEFAULT_APP_SETTINGS:
                continue
            normalized = self._normalize_value(key, value)
            current[key] = self._coerce_value(key, normalized)
            updates.append((key, normalized))

        if "download_root" in payload and current["download_root"]:
            self._require_writable_directory(Path(str(current["download_root"])))

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

    def _require_writable_directory(self, path: Path) -> None:
        """Fail loudly and specifically instead of storing a path we cannot use.

        In a container the usable paths are the mounted ones, and a typo here
        used to surface much later as an opaque download failure.
        """
        try:
            path.mkdir(parents=True, exist_ok=True)
        except PermissionError as exc:
            raise ValueError(
                f"'{path}' kann nicht angelegt werden (keine Rechte). "
                f"Im Container sind nur gemountete Pfade beschreibbar."
            ) from exc
        except OSError as exc:
            raise ValueError(f"'{path}' kann nicht angelegt werden: {exc.strerror or exc}") from exc

        if not os.access(path, os.W_OK):
            raise ValueError(
                f"'{path}' existiert, ist aber nicht beschreibbar. "
                f"Pruefe die Rechte des gemounteten Verzeichnisses."
            )

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
