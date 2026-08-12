from __future__ import annotations

import grp
import os
import platform
import pwd
import shutil
from pathlib import Path

from app.services.app_settings import app_settings_service


class SystemCheckService:
    """Answers the two questions people actually have when something is wrong:
    which account is this running as, and can it write where it needs to.

    Finding a numeric UID otherwise means enabling SSH and running `stat`, which
    is a lot to ask before a first install.
    """

    def run(self) -> dict:
        settings = app_settings_service.get_all()
        download_root = Path(str(settings["download_root"]))
        config_root = Path(os.getenv("APP_DATA_DIR", "/config"))

        uid, gid = os.getuid(), os.getgid()

        checks = [
            self._identity_check(uid, gid),
            self._check(
                "yt_dlp",
                shutil.which("yt-dlp") is not None,
                "yt-dlp ist installiert (Download-Engine).",
            ),
            self._check(
                "ffmpeg",
                shutil.which("ffmpeg") is not None,
                "ffmpeg ist installiert (HLS und Umwandlung).",
            ),
            self._path_check("config_root", config_root, "Konfigurationsordner", uid, gid),
            self._path_check("download_root", download_root, "Download-Zielordner", uid, gid),
            self._check(
                "scheduler",
                bool(settings["scheduler_enabled"]),
                "Abos werden im Hintergrund ausgeführt.",
            ),
            self._check(
                "metadata_sidecars",
                bool(settings["create_nfo_sidecar"] or settings["create_json_sidecar"]),
                "Mindestens ein Metadaten-Sidecar ist aktiviert.",
            ),
        ]

        ok_count = len([item for item in checks if item["status"] == "ok"])
        return {
            "summary": {
                "status": "ok" if ok_count == len(checks) else "warning",
                "ok_count": ok_count,
                "total_checks": len(checks),
                "platform": platform.platform(),
                "architecture": platform.machine(),
                "uid": uid,
                "gid": gid,
            },
            "checks": checks,
            "host_prerequisites": [
                {
                    "key": "media_visible",
                    "status": "manual",
                    "label": "Plex, Jellyfin oder Infuse müssen denselben Medienordner sehen.",
                },
                {
                    "key": "backup",
                    "status": "manual",
                    "label": "Der Konfigurationsordner enthält die Datenbank, bitte in die Datensicherung aufnehmen.",
                },
            ],
        }

    def _identity_check(self, uid: int, gid: int) -> dict:
        name = self._user_name(uid)
        group = self._group_name(gid)
        running_as_root = uid == 0
        label = (
            f"Läuft als UID {uid} ({name}), GID {gid} ({group})."
            if not running_as_root
            else f"Läuft als root (UID 0). Downloads gehören dann root. "
            f"Setze user: \"<UID>:<GID>\" in der Compose-Datei."
        )
        return {"key": "identity", "status": "warning" if running_as_root else "ok", "label": label}

    def _check(self, key: str, ok: bool, label: str) -> dict:
        return {"key": key, "status": "ok" if ok else "warning", "label": label}

    def _path_check(self, key: str, path: Path, title: str, uid: int, gid: int) -> dict:
        if not path.exists():
            return {
                "key": key,
                "status": "error",
                "label": (
                    f"{title} {path} existiert nicht. Im Container sind nur gemountete "
                    f"Pfade nutzbar. Prüfe die volumes in der Compose-Datei."
                ),
            }

        try:
            probe = path / ".write-test"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink(missing_ok=True)
        except PermissionError:
            owner_uid, owner_gid = self._owner(path)
            hint = (
                f'Setze user: "{owner_uid}:{owner_gid}" in der Compose-Datei '
                f"und starte den Container neu."
                if owner_uid is not None
                else "Prüfe die Rechte des Ordners auf dem Host."
            )
            return {
                "key": key,
                "status": "error",
                "label": (
                    f"{title} {path} ist nicht beschreibbar. Der Ordner gehört "
                    f"{owner_uid}:{owner_gid}, der Container läuft als {uid}:{gid}. {hint}"
                ),
            }
        except OSError as exc:
            return {
                "key": key,
                "status": "error",
                "label": f"{title} {path}: {exc.strerror or exc}",
            }

        owner_uid, owner_gid = self._owner(path)
        suffix = ""
        if owner_uid is not None and owner_uid != uid and uid != 0:
            # Writable but foreign-owned usually means a world-writable folder.
            # It works today and breaks the moment someone tightens permissions.
            suffix = f" Hinweis: gehört {owner_uid}:{owner_gid}, geschrieben wird als {uid}:{gid}."
        return {"key": key, "status": "ok", "label": f"{title} {path} ist beschreibbar.{suffix}"}

    def _owner(self, path: Path) -> tuple[int | None, int | None]:
        try:
            info = path.stat()
            return info.st_uid, info.st_gid
        except OSError:
            return None, None

    def _user_name(self, uid: int) -> str:
        try:
            return pwd.getpwuid(uid).pw_name
        except KeyError:
            # Expected: the host account has no entry inside the container.
            return "kein Eintrag im Container"

    def _group_name(self, gid: int) -> str:
        try:
            return grp.getgrgid(gid).gr_name
        except KeyError:
            return "kein Eintrag im Container"


system_check_service = SystemCheckService()
