from __future__ import annotations

from typing import Any
from urllib.parse import quote_plus

import httpx

from app.services.app_settings import app_settings_service


class MediaServerService:
    async def get_status(self) -> dict[str, Any]:
        settings = app_settings_service.get_all()
        plex = await self._plex_status(settings)
        jellyfin = await self._jellyfin_status(settings)
        infuse = self._infuse_status(settings)
        return {"plex": plex, "jellyfin": jellyfin, "infuse": infuse}

    async def trigger_scans(self, final_path: str | None = None) -> dict[str, Any]:
        settings = app_settings_service.get_all()
        results = {
            "plex": await self._plex_scan(settings, final_path),
            "jellyfin": await self._jellyfin_scan(settings),
            "infuse": self._infuse_scan_hint(settings),
        }
        return results

    async def notify_download_completed(self, download: dict[str, Any]) -> dict[str, Any]:
        settings = app_settings_service.get_all()
        results: dict[str, Any] = {}
        if settings.get("plex_enabled") and settings.get("plex_auto_scan"):
            results["plex"] = await self._plex_scan(settings, download.get("final_path"))
        if settings.get("jellyfin_enabled") and settings.get("jellyfin_auto_scan"):
            results["jellyfin"] = await self._jellyfin_scan(settings)
        if settings.get("infuse_enabled"):
            results["infuse"] = self._infuse_scan_hint(settings)
        return results

    def build_infuse_links(self, item: dict[str, Any]) -> dict[str, str]:
        settings = app_settings_service.get_all()
        if not settings.get("infuse_enabled"):
            return {}
        source_url = item.get("source_url")
        if not source_url:
            return {}
        filename = item.get("filename") or f"{item.get('title', 'video')}.mp4"
        subtitle_url = item.get("subtitle_url") or ""
        play_url = (
            f"infuse://x-callback-url/play?url={quote_plus(source_url)}"
            f"&filename={quote_plus(filename)}"
        )
        save_url = (
            f"infuse://x-callback-url/save?url={quote_plus(source_url)}"
            f"&filename={quote_plus(filename)}&download=0"
        )
        if subtitle_url:
            play_url += f"&sub={quote_plus(subtitle_url)}"
            save_url += f"&sub={quote_plus(subtitle_url)}"
        return {"play": play_url, "save": save_url}

    async def _plex_status(self, settings: dict[str, Any]) -> dict[str, Any]:
        if not settings.get("plex_enabled"):
            return {"enabled": False, "status": "disabled", "label": "Plex ist deaktiviert."}
        base_url = str(settings.get("plex_base_url") or "").rstrip("/")
        token = settings.get("plex_token") or ""
        if not base_url or not token:
            return {"enabled": True, "status": "warning", "label": "Plex ist aktiviert, aber Basis-URL oder Token fehlen."}
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    f"{base_url}/library/sections",
                    params={"X-Plex-Token": token},
                    headers={"Accept": "application/json"},
                )
                response.raise_for_status()
            return {"enabled": True, "status": "ok", "label": "Plex ist erreichbar."}
        except Exception as exc:  # noqa: BLE001
            return {"enabled": True, "status": "warning", "label": f"Plex nicht erreichbar: {exc}"}

    async def _plex_scan(self, settings: dict[str, Any], final_path: str | None) -> dict[str, Any]:
        if not settings.get("plex_enabled"):
            return {"status": "disabled", "label": "Plex-Scan deaktiviert."}
        base_url = str(settings.get("plex_base_url") or "").rstrip("/")
        token = settings.get("plex_token") or ""
        section = settings.get("plex_library_section") or ""
        if not base_url or not token or not section:
            return {"status": "warning", "label": "Plex-Scan uebersprungen: URL, Token oder Section fehlen."}
        params = {"X-Plex-Token": token}
        if final_path:
            params["path"] = final_path
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.get(f"{base_url}/library/sections/{section}/refresh", params=params)
                response.raise_for_status()
            return {"status": "ok", "label": "Plex-Scan angestossen."}
        except Exception as exc:  # noqa: BLE001
            return {"status": "warning", "label": f"Plex-Scan fehlgeschlagen: {exc}"}

    async def _jellyfin_status(self, settings: dict[str, Any]) -> dict[str, Any]:
        if not settings.get("jellyfin_enabled"):
            return {"enabled": False, "status": "disabled", "label": "Jellyfin ist deaktiviert."}
        base_url = str(settings.get("jellyfin_base_url") or "").rstrip("/")
        api_key = settings.get("jellyfin_api_key") or ""
        if not base_url or not api_key:
            return {"enabled": True, "status": "warning", "label": "Jellyfin ist aktiviert, aber Basis-URL oder API-Key fehlen."}
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    f"{base_url}/System/Info/Public",
                    headers={"X-Emby-Token": api_key},
                )
                response.raise_for_status()
            return {"enabled": True, "status": "ok", "label": "Jellyfin ist erreichbar."}
        except Exception as exc:  # noqa: BLE001
            return {"enabled": True, "status": "warning", "label": f"Jellyfin nicht erreichbar: {exc}"}

    async def _jellyfin_scan(self, settings: dict[str, Any]) -> dict[str, Any]:
        if not settings.get("jellyfin_enabled"):
            return {"status": "disabled", "label": "Jellyfin-Scan deaktiviert."}
        base_url = str(settings.get("jellyfin_base_url") or "").rstrip("/")
        api_key = settings.get("jellyfin_api_key") or ""
        if not base_url or not api_key:
            return {"status": "warning", "label": "Jellyfin-Scan uebersprungen: URL oder API-Key fehlen."}
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.post(
                    f"{base_url}/Library/Refresh",
                    headers={"X-Emby-Token": api_key},
                )
                response.raise_for_status()
            return {"status": "ok", "label": "Jellyfin-Refresh angestossen."}
        except Exception as exc:  # noqa: BLE001
            return {"status": "warning", "label": f"Jellyfin-Refresh fehlgeschlagen: {exc}"}

    def _infuse_status(self, settings: dict[str, Any]) -> dict[str, Any]:
        if not settings.get("infuse_enabled"):
            return {"enabled": False, "status": "disabled", "label": "Infuse-Links sind deaktiviert."}
        return {
            "enabled": True,
            "status": "ok",
            "label": "Infuse-Deep-Links fuer iPhone, iPad und Mac koennen erzeugt werden.",
        }

    def _infuse_scan_hint(self, settings: dict[str, Any]) -> dict[str, Any]:
        if not settings.get("infuse_enabled"):
            return {"status": "disabled", "label": "Infuse deaktiviert."}
        return {
            "status": "ok",
            "label": "Infuse nutzt denselben Medienordner oder Deep-Links. Ein manueller Bibliotheks-Refresh kann je nach Client noetig sein.",
        }


media_server_service = MediaServerService()
