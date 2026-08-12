from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from app.db.database import database
from app.services.downloads import STATUS_DONE, download_manager


VIDEO_EXTENSIONS = {".mp4", ".mkv", ".mov", ".m4v", ".avi", ".ts", ".webm"}


class ImportService:
    def import_filesystem(self, source_path: str, max_files: int = 500) -> dict[str, Any]:
        root = Path(source_path).expanduser()
        if not root.exists():
            raise ValueError("Importpfad existiert nicht.")
        files = [path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS]
        imported = 0
        skipped = 0
        items: list[dict[str, Any]] = []
        for path in files[:max_files]:
            if database.fetch_one("SELECT id FROM downloads WHERE final_path = ?", (str(path),)):
                skipped += 1
                continue
            payload = self._payload_from_file(path)
            duplicate = download_manager.find_duplicate(payload)
            if duplicate:
                skipped += 1
                continue
            download_id = database.execute(
                """
                INSERT INTO downloads(
                    external_id, title, channel, topic, description, source_url, website_url,
                    preview_url, subtitle_url, quality, air_date, duration_seconds, target_directory,
                    filename, final_path, format_hint, status, max_retries, duplicate_key,
                    imported, metadata_written, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload.get("external_id"),
                    payload["title"],
                    payload.get("channel"),
                    payload.get("topic"),
                    payload.get("description"),
                    payload["source_url"],
                    "",
                    "",
                    "",
                    payload.get("quality"),
                    payload.get("air_date"),
                    None,
                    str(path.parent),
                    path.name,
                    str(path),
                    payload.get("format_hint"),
                    STATUS_DONE,
                    0,
                    download_manager.compute_duplicate_key(payload),
                    1,
                    0,
                    json.dumps({"imported_from": str(path)}),
                ),
            )
            items.append(download_manager.get_download(download_id))
            imported += 1

        database.execute(
            """
            INSERT INTO import_runs(source_path, source_kind, imported_count, skipped_count)
            VALUES (?, ?, ?, ?)
            """,
            (str(root), "filesystem", imported, skipped),
        )
        return {"imported": imported, "skipped": skipped, "items": items}

    def import_list(self, source_path: str) -> dict[str, Any]:
        path = Path(source_path).expanduser()
        if not path.exists():
            raise ValueError("Listenpfad existiert nicht.")
        rows = self._read_list_entries(path)
        imported = 0
        skipped = 0
        items: list[dict[str, Any]] = []
        for row in rows:
            if not row.get("source_url"):
                skipped += 1
                continue
            duplicate = download_manager.find_duplicate(row)
            if duplicate:
                skipped += 1
                continue
            item = download_manager.create_download({**row, "metadata": {"imported_from_list": str(path)}})
            items.append(item)
            imported += 1
        database.execute(
            """
            INSERT INTO import_runs(source_path, source_kind, imported_count, skipped_count)
            VALUES (?, ?, ?, ?)
            """,
            (str(path), "list", imported, skipped),
        )
        return {"imported": imported, "skipped": skipped, "items": items}

    def list_runs(self) -> list[dict[str, Any]]:
        return database.fetch_all(
            """
            SELECT *
            FROM import_runs
            ORDER BY created_at DESC
            LIMIT 20
            """
        )

    def _payload_from_file(self, path: Path) -> dict[str, Any]:
        stem = path.stem
        air_date = self._extract_air_date(stem)
        title = re.sub(r"[_\.]+", " ", stem).strip()
        title = re.sub(r"\s+", " ", title)
        return {
            "external_id": f"import:{path}",
            "title": title,
            "channel": path.parent.name,
            "topic": path.parent.parent.name if path.parent.parent != path.parent else "",
            "description": "Importierter vorhandener Download",
            "source_url": str(path),
            "quality": "best",
            "air_date": air_date,
            "format_hint": path.suffix.lower().lstrip("."),
        }

    def _extract_air_date(self, value: str) -> str | None:
        match = re.search(r"(20\d{2})[-_]?(\d{2})[-_]?(\d{2})", value)
        if not match:
            return None
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"

    def _read_list_entries(self, path: Path) -> list[dict[str, Any]]:
        if path.suffix.lower() == ".json":
            raw = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                if isinstance(raw.get("items"), list):
                    return [self._normalize_entry(item) for item in raw["items"]]
                if isinstance(raw.get("downloads"), list):
                    return [self._normalize_entry(item) for item in raw["downloads"]]
            if isinstance(raw, list):
                return [self._normalize_entry(item) for item in raw]
            return []
        lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
        return [self._normalize_entry(line) for line in lines if line and not line.startswith("#")]

    def _normalize_entry(self, item: Any) -> dict[str, Any]:
        if isinstance(item, str):
            title = Path(item).stem or item
            return {"title": title, "source_url": item, "quality": "best"}
        if isinstance(item, dict):
            title = item.get("title") or item.get("name") or Path(str(item.get("source_url", "video"))).stem
            return {
                "external_id": item.get("external_id"),
                "title": title,
                "channel": item.get("channel"),
                "topic": item.get("topic"),
                "description": item.get("description"),
                "website_url": item.get("website_url"),
                "preview_url": item.get("preview_url"),
                "subtitle_url": item.get("subtitle_url"),
                "source_url": item.get("source_url") or item.get("url"),
                "quality": item.get("quality", "best"),
                "air_date": item.get("air_date") or item.get("date"),
                "format_hint": item.get("format_hint"),
            }
        return {}


import_service = ImportService()
