from __future__ import annotations

import asyncio
import json
import re
import xml.sax.saxutils as saxutils
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.db.database import database
from app.services.app_settings import app_settings_service
from app.services.media_servers import media_server_service


STATUS_PENDING = "queued"
STATUS_RUNNING = "downloading"
STATUS_DONE = "completed"
STATUS_FAILED = "failed"
STATUS_CANCELED = "canceled"


class DownloadManager:
    def __init__(self) -> None:
        self.queue: asyncio.Queue[int] = asyncio.Queue()
        self.worker_tasks: list[asyncio.Task] = []
        self.running = False
        self.active_processes: dict[int, asyncio.subprocess.Process] = {}
        self.enqueued_ids: set[int] = set()
        self.worker_lock = asyncio.Lock()

    async def start(self) -> None:
        self.running = True
        self._requeue_incomplete_downloads()
        await self.refresh_workers()

    async def stop(self) -> None:
        self.running = False
        for task in self.worker_tasks:
            task.cancel()
        for task in self.worker_tasks:
            try:
                await task
            except asyncio.CancelledError:
                pass
        self.worker_tasks = []

    async def refresh_workers(self) -> None:
        async with self.worker_lock:
            desired = app_settings_service.get_all()["concurrent_downloads"]
            current = len(self.worker_tasks)
            if desired == current:
                return
            if desired < current:
                tasks_to_stop = self.worker_tasks[desired:]
                self.worker_tasks = self.worker_tasks[:desired]
                for task in tasks_to_stop:
                    task.cancel()
                for task in tasks_to_stop:
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                return
            for index in range(current, desired):
                self.worker_tasks.append(asyncio.create_task(self._worker(index + 1), name=f"download-worker-{index + 1}"))

    def create_download(self, payload: dict[str, Any]) -> dict[str, Any]:
        app_settings = app_settings_service.get_all()
        duplicate = self.find_duplicate(payload)
        if duplicate and app_settings.get("skip_duplicates"):
            existing = self.get_download(duplicate["id"]) or duplicate
            existing["duplicate_detected"] = True
            return existing
        target_directory = self._resolve_target_directory(payload, app_settings)
        filename = self._build_filename(payload, payload.get("filename_template") or app_settings["filename_template"])
        duplicate_key = self.compute_duplicate_key(payload)
        download_id = database.execute(
            """
            INSERT INTO downloads(
                external_id, title, channel, topic, description, source_url, website_url,
                preview_url, subtitle_url, quality, air_date, duration_seconds, target_directory,
                filename, format_hint, status, max_retries, duplicate_key, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.get("external_id"),
                payload["title"],
                payload.get("channel"),
                payload.get("topic"),
                payload.get("description"),
                payload["source_url"],
                payload.get("website_url"),
                payload.get("preview_url") or payload.get("website_url") or payload["source_url"],
                payload.get("subtitle_url"),
                payload.get("quality"),
                payload.get("air_date"),
                payload.get("duration_seconds"),
                target_directory,
                filename,
                payload.get("format_hint") or self._infer_format_hint(payload["source_url"]),
                STATUS_PENDING,
                app_settings["max_retries"],
                duplicate_key,
                json.dumps(payload.get("metadata", {})),
            ),
        )
        self._enqueue(download_id)
        return self.get_download(download_id)

    def list_downloads(self) -> list[dict[str, Any]]:
        items = database.fetch_all(
            """
            SELECT *
            FROM downloads
            ORDER BY
                CASE status
                    WHEN 'downloading' THEN 0
                    WHEN 'queued' THEN 1
                    WHEN 'failed' THEN 2
                    WHEN 'canceled' THEN 3
                    ELSE 4
                END,
                updated_at DESC
            """
        )
        return [self._augment_download(item) for item in items]

    def list_duplicates(self) -> list[dict[str, Any]]:
        rows = database.fetch_all(
            """
            SELECT duplicate_key, COUNT(*) AS item_count
            FROM downloads
            WHERE duplicate_key IS NOT NULL AND duplicate_key != ''
            GROUP BY duplicate_key
            HAVING COUNT(*) > 1
            ORDER BY item_count DESC, duplicate_key ASC
            """
        )
        groups: list[dict[str, Any]] = []
        for row in rows:
            items = database.fetch_all(
                """
                SELECT *
                FROM downloads
                WHERE duplicate_key = ?
                ORDER BY
                    CASE status
                        WHEN 'completed' THEN 0
                        WHEN 'downloading' THEN 1
                        WHEN 'queued' THEN 2
                        ELSE 3
                    END,
                    updated_at DESC
                """,
                (row["duplicate_key"],),
            )
            groups.append(
                {
                    "duplicate_key": row["duplicate_key"],
                    "item_count": row["item_count"],
                    "items": [self._augment_download(item) for item in items],
                }
            )
        return groups

    def get_download(self, download_id: int) -> dict[str, Any] | None:
        item = database.fetch_one("SELECT * FROM downloads WHERE id = ?", (download_id,))
        return self._augment_download(item) if item else None

    def find_duplicate(self, payload: dict[str, Any], exclude_id: int | None = None) -> dict[str, Any] | None:
        conditions: list[str] = []
        params: list[Any] = []
        external_id = payload.get("external_id")
        source_url = payload.get("source_url")
        duplicate_key = self.compute_duplicate_key(payload)
        if external_id:
            conditions.append("external_id = ?")
            params.append(external_id)
        if source_url:
            conditions.append("source_url = ?")
            params.append(source_url)
        if duplicate_key:
            conditions.append("duplicate_key = ?")
            params.append(duplicate_key)
        if not conditions:
            return None
        query = f"""
            SELECT *
            FROM downloads
            WHERE ({' OR '.join(conditions)})
        """
        if exclude_id is not None:
            query += " AND id != ?"
            params.append(exclude_id)
        query += """
            ORDER BY
                CASE status
                    WHEN 'completed' THEN 0
                    WHEN 'downloading' THEN 1
                    WHEN 'queued' THEN 2
                    ELSE 3
                END,
                updated_at DESC
            LIMIT 1
        """
        item = database.fetch_one(query, tuple(params))
        return self._augment_download(item) if item else None

    def compute_duplicate_key(self, payload: dict[str, Any]) -> str:
        air_date = payload.get("air_date") or ""
        title = self._slugify(payload.get("title") or "")
        channel = self._slugify(payload.get("channel") or "")
        if title and air_date:
            return f"{air_date}:{channel}:{title}"
        if payload.get("external_id"):
            return f"ext:{payload['external_id']}"
        if payload.get("source_url"):
            return f"url:{self._slugify(payload['source_url'])}"
        return title

    def annotate_library_state(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        annotated: list[dict[str, Any]] = []
        for item in items:
            duplicate = self.find_duplicate(item)
            enriched = dict(item)
            if duplicate:
                enriched["already_present"] = True
                enriched["existing_download_id"] = duplicate["id"]
                enriched["existing_status"] = duplicate["status"]
                enriched["existing_final_path"] = duplicate.get("final_path")
            else:
                enriched["already_present"] = False
            infuse_links = media_server_service.build_infuse_links(enriched)
            if infuse_links:
                enriched["infuse_links"] = infuse_links
            annotated.append(enriched)
        return annotated

    def get_settings(self) -> dict[str, Any]:
        return app_settings_service.get_all()

    def get_download_root(self) -> str:
        return str(self.get_settings()["download_root"])

    def locked_setting_keys(self) -> list[str]:
        return app_settings_service.locked_keys()

    def container_default_settings(self) -> dict[str, str]:
        return app_settings_service.container_defaults()

    def update_download_root(self, path: str) -> str:
        return str(app_settings_service.update({"download_root": path})["download_root"])

    async def update_settings(self, payload: dict[str, Any]) -> dict[str, Any]:
        settings_data = app_settings_service.update(payload)
        await self.refresh_workers()
        return settings_data

    def retry_download(self, download_id: int) -> dict[str, Any] | None:
        download = self.get_download(download_id)
        if not download:
            return None
        database.execute(
            """
            UPDATE downloads
            SET status = 'queued',
                progress = 0,
                error_message = NULL,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (download_id,),
        )
        self._enqueue(download_id)
        return self.get_download(download_id)

    def delete_download(self, download_id: int) -> bool:
        """Remove an entry from the queue and history. The media file stays."""
        download = self.get_download(download_id)
        if not download:
            return False
        self.enqueued_ids.discard(download_id)
        database.execute("DELETE FROM rule_matches WHERE download_id = ?", (download_id,))
        database.execute("DELETE FROM downloads WHERE id = ?", (download_id,))
        return True

    async def cancel_download(self, download_id: int) -> dict[str, Any] | None:
        download = self.get_download(download_id)
        if not download:
            return None
        process = self.active_processes.get(download_id)
        if process and process.returncode is None:
            process.terminate()
            await process.wait()
        self.enqueued_ids.discard(download_id)
        database.execute(
            """
            UPDATE downloads
            SET status = 'canceled',
                error_message = 'Download manuell abgebrochen.',
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (download_id,),
        )
        return self.get_download(download_id)

    async def _worker(self, _: int) -> None:
        while self.running:
            download_id = await self.queue.get()
            self.enqueued_ids.discard(download_id)
            try:
                await self._process_download(download_id)
            finally:
                self.queue.task_done()

    async def _process_download(self, download_id: int) -> None:
        download = self.get_download(download_id)
        if not download or download["status"] not in {STATUS_PENDING, STATUS_RUNNING}:
            return

        target_dir = Path(download["target_directory"])
        target_dir.mkdir(parents=True, exist_ok=True)
        output_path = target_dir / download["filename"]
        self._set_status(download_id, STATUS_RUNNING, progress=0, final_path=str(output_path), error_message=None)

        process = await asyncio.create_subprocess_exec(
            "yt-dlp",
            "--newline",
            "--no-playlist",
            "--progress-template",
            "download:%(progress._percent_str)s",
            "--output",
            str(output_path),
            download["source_url"],
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        self.active_processes[download_id] = process

        assert process.stdout is not None
        async for raw_line in process.stdout:
            line = raw_line.decode("utf-8", errors="ignore").strip()
            progress = self._extract_progress(line)
            if progress is not None:
                self._set_status(download_id, STATUS_RUNNING, progress=progress)

        return_code = await process.wait()
        self.active_processes.pop(download_id, None)
        latest = self.get_download(download_id)
        if not latest:
            return
        if latest["status"] == STATUS_CANCELED:
            return
        if return_code == 0:
            # yt-dlp resolves the %(ext)s placeholder itself, so the templated path we
            # stored before starting does not point at a real file. Resolve it now and
            # persist the actual path -- Infuse links, Plex scans and duplicate checks
            # all read final_path directly.
            resolved_path = self._resolve_final_media_path(output_path)
            self._set_status(download_id, STATUS_DONE, progress=100, final_path=str(resolved_path))
            completed = self.get_download(download_id)
            self._write_metadata_sidecars(completed)
            if completed:
                asyncio.create_task(media_server_service.notify_download_completed(completed))
        else:
            if latest["retry_count"] < latest["max_retries"]:
                database.execute(
                    """
                    UPDATE downloads
                    SET status = 'queued',
                        retry_count = retry_count + 1,
                        error_message = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (f"Automatischer Wiederholungsversuch nach Fehler {return_code}.", download_id),
                )
                self._enqueue(download_id)
                return
            self._set_status(download_id, STATUS_FAILED, error_message=f"yt-dlp exited with code {return_code}")

    def _requeue_incomplete_downloads(self) -> None:
        rows = database.fetch_all(
            """
            SELECT id
            FROM downloads
            WHERE status IN ('queued', 'downloading')
            ORDER BY created_at ASC
            """
        )
        for row in rows:
            database.execute(
                "UPDATE downloads SET status = 'queued', progress = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (row["id"],),
            )
            self._enqueue(row["id"])

    def _set_status(
        self,
        download_id: int,
        status: str,
        *,
        progress: float | None = None,
        final_path: str | None = None,
        error_message: str | None = None,
        metadata_written: int | None = None,
    ) -> None:
        current = self.get_download(download_id)
        if not current:
            return
        database.execute(
            """
            UPDATE downloads
            SET status = ?,
                progress = ?,
                final_path = ?,
                error_message = ?,
                metadata_written = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                status,
                current["progress"] if progress is None else progress,
                current["final_path"] if final_path is None else final_path,
                error_message,
                current["metadata_written"] if metadata_written is None else metadata_written,
                download_id,
            ),
        )

    def _resolve_target_directory(self, payload: dict[str, Any], app_settings: dict[str, Any]) -> str:
        base_root = Path(app_settings["download_root"])
        target_directory = payload.get("target_directory")
        base_dir = Path(str(target_directory)).expanduser() if target_directory else base_root
        if not base_dir.is_absolute():
            base_dir = base_root / base_dir
        folder_template = payload.get("folder_template") or app_settings["subfolder_template"]
        extra_path = self._render_folder_template(folder_template, payload)
        resolved = base_dir / extra_path if extra_path else base_dir
        resolved.mkdir(parents=True, exist_ok=True)
        return str(resolved)

    def _build_filename(self, payload: dict[str, Any], template: str) -> str:
        stem = self._render_template(template, payload)
        stem = stem or self._render_template("{date}_{channel}_{title}", payload)
        return f"{stem}.%(ext)s"

    def _render_folder_template(self, template: str | None, payload: dict[str, Any]) -> str:
        if not template:
            return ""
        parts = [part.strip() for part in template.split("/") if part.strip()]
        rendered_parts = []
        for part in parts:
            rendered = self._slugify(self._render_template(part, payload))
            if rendered:
                rendered_parts.append(rendered)
        return "/".join(rendered_parts)

    def _render_template(self, template: str, payload: dict[str, Any]) -> str:
        data = {
            "date": payload.get("air_date") or datetime.now(UTC).date().isoformat(),
            "year": (payload.get("air_date") or datetime.now(UTC).date().isoformat())[:4],
            "channel": payload.get("channel") or "sender",
            "topic": payload.get("topic") or "mediathek",
            "title": payload.get("title") or "download",
            "quality": payload.get("quality") or "best",
        }
        rendered = template
        for key, value in data.items():
            rendered = rendered.replace(f"{{{key}}}", self._slugify(str(value)))
        return re.sub(r"[-_]{2,}", "_", rendered.replace("/", "_")).strip("._-")

    def _write_metadata_sidecars(self, download: dict[str, Any] | None) -> None:
        if not download or not download.get("final_path"):
            return
        app_settings = app_settings_service.get_all()
        final_media_path = self._resolve_final_media_path(Path(download["final_path"]))
        stem = final_media_path.parent / final_media_path.stem
        metadata_payload = {
            "title": download["title"],
            "channel": download.get("channel"),
            "topic": download.get("topic"),
            "description": download.get("description"),
            "air_date": download.get("air_date"),
            "duration_seconds": download.get("duration_seconds"),
            "quality": download.get("quality"),
            "website_url": download.get("website_url"),
            "preview_url": download.get("preview_url"),
            "source_url": download.get("source_url"),
            "metadata": download.get("metadata", {}),
        }
        if app_settings["create_json_sidecar"]:
            stem.with_suffix(".info.json").write_text(json.dumps(metadata_payload, indent=2, ensure_ascii=False), encoding="utf-8")
        if app_settings["create_nfo_sidecar"]:
            nfo = self._build_nfo(metadata_payload)
            stem.with_suffix(".nfo").write_text(nfo, encoding="utf-8")
        self._set_status(download["id"], download["status"], metadata_written=1)

    def _augment_download(self, item: dict[str, Any] | None) -> dict[str, Any] | None:
        if not item:
            return None
        duplicate_of_id = item.get("duplicate_of_id")
        duplicate = self.get_download(duplicate_of_id) if duplicate_of_id and duplicate_of_id != item.get("id") else None
        if duplicate:
            item["duplicate_of"] = {
                "id": duplicate["id"],
                "title": duplicate["title"],
                "status": duplicate["status"],
                "final_path": duplicate.get("final_path"),
            }
        item["is_duplicate"] = bool(item.get("duplicate_of_id"))
        return item

    def _resolve_final_media_path(self, templated_path: Path) -> Path:
        if "%(ext)s" not in templated_path.name:
            return templated_path
        prefix = templated_path.name.replace(".%(ext)s", "")
        matches = [
            item
            for item in templated_path.parent.glob(f"{prefix}.*")
            if item.suffix not in {".json", ".nfo"}
        ]
        return matches[0] if matches else templated_path.parent / prefix

    def _build_nfo(self, payload: dict[str, Any]) -> str:
        def esc(value: Any) -> str:
            return saxutils.escape("" if value is None else str(value))

        return (
            "<movie>\n"
            f"  <title>{esc(payload['title'])}</title>\n"
            f"  <studio>{esc(payload.get('channel'))}</studio>\n"
            f"  <plot>{esc(payload.get('description'))}</plot>\n"
            f"  <aired>{esc(payload.get('air_date'))}</aired>\n"
            f"  <tag>{esc(payload.get('topic'))}</tag>\n"
            f"  <url>{esc(payload.get('website_url'))}</url>\n"
            "</movie>\n"
        )

    def _enqueue(self, download_id: int) -> None:
        if download_id in self.enqueued_ids:
            return
        self.enqueued_ids.add(download_id)
        self.queue.put_nowait(download_id)

    def _slugify(self, value: str) -> str:
        normalized = re.sub(r"[^\w\s-]", "", value, flags=re.UNICODE).strip().lower()
        return re.sub(r"[-\s]+", "-", normalized)[:80] or "download"

    def _infer_format_hint(self, source_url: str) -> str:
        lowered = source_url.lower()
        if ".m3u8" in lowered:
            return "hls"
        if ".mp4" in lowered:
            return "mp4"
        return "generic"

    def _extract_progress(self, line: str) -> float | None:
        match = re.search(r"(\d+(?:\.\d+)?)%", line)
        return float(match.group(1)) if match else None


download_manager = DownloadManager()
