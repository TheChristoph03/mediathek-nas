from __future__ import annotations

import xml.sax.saxutils as saxutils
from datetime import UTC, datetime
from typing import Any


class RssService:
    def build_feed(self, *, title: str, description: str, items: list[dict[str, Any]], feed_url: str) -> str:
        entries = "\n".join(self._build_item(item) for item in items)
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<rss version="2.0">\n'
            "  <channel>\n"
            f"    <title>{self._esc(title)}</title>\n"
            f"    <description>{self._esc(description)}</description>\n"
            f"    <link>{self._esc(feed_url)}</link>\n"
            f"    <lastBuildDate>{self._rfc822(datetime.now(UTC))}</lastBuildDate>\n"
            f"{entries}\n"
            "  </channel>\n"
            "</rss>\n"
        )

    def _build_item(self, item: dict[str, Any]) -> str:
        link = item.get("website_url") or item.get("preview_url") or item.get("source_url") or ""
        pub_date = item.get("air_date")
        pub_date_text = ""
        if pub_date:
            try:
                pub_date_text = f"      <pubDate>{self._rfc822(datetime.fromisoformat(pub_date).replace(tzinfo=UTC))}</pubDate>\n"
            except ValueError:
                pub_date_text = ""
        description = item.get("description") or item.get("topic") or ""
        guid = item.get("external_id") or link or item.get("title", "")
        return (
            "    <item>\n"
            f"      <title>{self._esc(item.get('title') or 'Ohne Titel')}</title>\n"
            f"      <description>{self._esc(description)}</description>\n"
            f"      <link>{self._esc(link)}</link>\n"
            f"      <guid>{self._esc(guid)}</guid>\n"
            f"{pub_date_text}"
            "    </item>"
        )

    def _esc(self, value: Any) -> str:
        return saxutils.escape("" if value is None else str(value))

    def _rfc822(self, value: datetime) -> str:
        return value.strftime("%a, %d %b %Y %H:%M:%S GMT")


rss_service = RssService()
