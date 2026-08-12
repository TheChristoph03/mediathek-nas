from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx

from app.core.config import settings
from app.db.database import database


# The curated floor. These stay in the list permanently: sampling recent entries
# finds busy channels reliably, but a low-volume one like ZDF-tivi or KiKA can be
# absent from several hundred recent items and would silently disappear.
FALLBACK_CHANNELS: list[str] = [
    "3Sat", "ARD", "ARTE.DE", "ARTE.EN", "ARTE.ES", "ARTE.FR", "ARTE.IT", "ARTE.PL",
    "BR", "DW", "Funk.net", "HR", "KiKA", "MDR", "NDR", "ORF", "PHOENIX",
    "Radio Bremen TV", "RBB", "RBTV", "SR", "SRF", "SWR", "WDR",
    "ZDF", "ZDF-tivi", "ZDFinfo", "ZDFneo",
]


class ChannelService:
    """Keeps the list of broadcasters current without a dedicated upstream endpoint.

    MediathekViewWeb has no documented "list all channels" call, so we sample the
    most recent entries and collect the channels that appear. Anything still
    broadcasting shows up there; anything that stopped ages out after RETENTION.
    """

    MAX_AGE = timedelta(hours=24)
    RETENTION = timedelta(days=30)
    SAMPLE_SIZE = 1000
    MIN_PLAUSIBLE = 5

    def list_channels(self) -> list[str]:
        """The curated floor plus everything seen upstream recently."""
        rows = database.fetch_all("SELECT name FROM channels")
        names = {row["name"] for row in rows if row["name"]}
        names.update(FALLBACK_CHANNELS)
        return sorted(names, key=str.casefold)

    def last_refresh(self) -> datetime | None:
        row = database.fetch_one("SELECT MAX(last_seen) AS newest FROM channels")
        if not row or not row.get("newest"):
            return None
        try:
            return datetime.fromisoformat(row["newest"])
        except ValueError:
            return None

    def is_stale(self) -> bool:
        last = self.last_refresh()
        return last is None or datetime.now(UTC) - last > self.MAX_AGE

    async def refresh(self) -> dict[str, Any]:
        """Sample recent entries and store the channels found. Never raises."""
        try:
            discovered = await self._sample_channels()
        except Exception as exc:  # noqa: BLE001 - a failed refresh must not break search
            return {"refreshed": False, "reason": str(exc), "channels": self.list_channels()}

        if len(discovered) < self.MIN_PLAUSIBLE:
            # A near-empty answer means the query shape or the upstream changed.
            # Keeping the previous list is better than replacing it with noise.
            return {
                "refreshed": False,
                "reason": f"only {len(discovered)} channels in the sample, keeping the previous list",
                "channels": self.list_channels(),
            }

        now = datetime.now(UTC).isoformat()
        database.execute_many(
            """
            INSERT INTO channels(name, last_seen)
            VALUES (?, ?)
            ON CONFLICT(name) DO UPDATE SET last_seen = excluded.last_seen
            """,
            [(name, now) for name in sorted(discovered)],
        )

        cutoff = (datetime.now(UTC) - self.RETENTION).isoformat()
        database.execute("DELETE FROM channels WHERE last_seen < ?", (cutoff,))

        return {"refreshed": True, "found": len(discovered), "channels": self.list_channels()}

    async def _sample_channels(self) -> set[str]:
        body = {
            "queries": [],
            "sortBy": "timestamp",
            "sortOrder": "desc",
            "future": False,
            "offset": 0,
            "size": self.SAMPLE_SIZE,
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                settings.mediathek_api_url,
                content=json.dumps(body),
                headers={"Content-Type": "text/plain", "User-Agent": "mediathek-nas/0.1"},
            )
            response.raise_for_status()
            payload = response.json()

        items = (payload.get("result", {}) or {}).get("results", []) or []
        return {item["channel"].strip() for item in items if item.get("channel")}


channel_service = ChannelService()
