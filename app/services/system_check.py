from __future__ import annotations

import os
import platform
import shutil
from pathlib import Path

from app.services.app_settings import app_settings_service


class SystemCheckService:
    def run(self) -> dict:
        settings = app_settings_service.get_all()
        download_root = Path(str(settings["download_root"]))
        config_root = Path(os.getenv("APP_DATA_DIR", "/config"))
        checks = [
            self._check("python", shutil.which("python") is not None or shutil.which("python3") is not None, "Python runtime im Container verfuegbar."),
            self._check("yt_dlp", shutil.which("yt-dlp") is not None, "yt-dlp ist fuer Downloads installiert."),
            self._check("ffmpeg", shutil.which("ffmpeg") is not None, "ffmpeg ist fuer HLS und Umwandlungen installiert."),
            self._path_check("config_root", config_root, "Konfigurationsordner ist vorhanden und beschreibbar."),
            self._path_check("download_root", download_root, "Download-Zielordner ist vorhanden und beschreibbar."),
            self._check("scheduler", isinstance(settings["scheduler_enabled"], bool), "Scheduler-Einstellung ist geladen."),
            self._check("metadata_sidecars", settings["create_nfo_sidecar"] or settings["create_json_sidecar"], "Mindestens ein Metadaten-Sidecar ist aktiviert."),
        ]
        host_prereqs = [
            {
                "key": "container_manager",
                "status": "manual",
                "label": "Container Manager muss auf DSM installiert sein.",
            },
            {
                "key": "shared_media_folder",
                "status": "manual",
                "label": "Gemeinsamer Medienordner muss fuer Container und Plex/Jellyfin erreichbar sein.",
            },
            {
                "key": "docker_permissions",
                "status": "manual",
                "label": "Der Benutzer fuer Container Manager braucht Schreibrechte auf App- und Medienordner.",
            },
        ]
        ok_count = len([item for item in checks if item["status"] == "ok"])
        return {
            "summary": {
                "status": "ok" if ok_count == len(checks) else "warning",
                "ok_count": ok_count,
                "total_checks": len(checks),
                "platform": platform.platform(),
                "architecture": platform.machine(),
            },
            "checks": checks,
            "host_prerequisites": host_prereqs,
        }

    def _check(self, key: str, ok: bool, label: str) -> dict:
        return {"key": key, "status": "ok" if ok else "warning", "label": label}

    def _path_check(self, key: str, path: Path, label: str) -> dict:
        try:
            path.mkdir(parents=True, exist_ok=True)
            probe = path / ".write-test"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink(missing_ok=True)
            return self._check(key, True, f"{label} ({path})")
        except Exception:
            return self._check(key, False, f"{label} ({path})")


system_check_service = SystemCheckService()
