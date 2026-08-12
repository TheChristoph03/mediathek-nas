from datetime import datetime
from typing import Any

import httpx

from app.core.config import settings
from app.models.schemas import SearchRequest


class MediathekService:
    async def search(self, payload: SearchRequest) -> dict[str, Any]:
        request_body = {
            "queries": self._build_queries(payload),
            "sortBy": "timestamp",
            "sortOrder": "desc",
            "future": False,
            "offset": payload.offset,
            "size": payload.size,
        }
        if payload.min_duration_minutes is not None:
            request_body["duration_min"] = payload.min_duration_minutes
        if payload.max_duration_minutes is not None:
            request_body["duration_max"] = payload.max_duration_minutes

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                settings.mediathek_api_url,
                content=self._to_text_plain_json(request_body),
                headers={"Content-Type": "text/plain", "User-Agent": "mediathek-nas/0.1"},
            )
            response.raise_for_status()
            raw = response.json()

        raw_result = raw.get("result", {}) or {}
        query_info = raw_result.get("queryInfo", {}) or {}

        items = raw_result.get("results", []) or []
        results = [self._transform_result(item, payload.quality) for item in items]
        results = self._apply_date_filters(results, payload.start_date, payload.end_date)

        # totalResults is the size of the whole result set; resultCount is only
        # this page. Reporting the latter as the total made paging think every
        # search fit on one page.
        total = int(query_info.get("totalResults") or 0)

        # MediathekViewWeb has no date range in its query API, so date filtering
        # happens here, after paging. That means a filtered page can be shorter
        # than requested and the total stays the unfiltered one.
        date_filtered = len(results) != len(items)

        return {
            "total": total,
            "offset": payload.offset,
            "size": payload.size,
            "page_count": len(results),
            "date_filtered": date_filtered,
            "results": results,
        }

    def _build_queries(self, payload: SearchRequest) -> list[dict[str, Any]]:
        queries: list[dict[str, Any]] = []
        if payload.query:
            queries.append({"fields": ["title", "topic"], "query": payload.query})
        if payload.channel:
            queries.append({"fields": ["channel"], "query": payload.channel})
        if payload.topic:
            queries.append({"fields": ["topic"], "query": payload.topic})
        return [query for query in queries if query]

    def _transform_result(self, item: dict[str, Any], quality: str) -> dict[str, Any]:
        source_url, quality_label = self._pick_source_url(item, quality)
        timestamp = item.get("timestamp")
        air_date = datetime.utcfromtimestamp(timestamp).date().isoformat() if timestamp else None
        return {
            "external_id": item.get("id") or f"{item.get('channel', '')}-{item.get('timestamp', '')}-{item.get('title', '')}",
            "title": item.get("title") or "Ohne Titel",
            "topic": item.get("topic") or "",
            "channel": item.get("channel") or "",
            "description": item.get("description") or "",
            "website_url": item.get("url_website") or "",
            "preview_url": item.get("url_website") or source_url,
            "duration_seconds": item.get("duration"),
            "air_date": air_date,
            "quality": quality_label,
            "source_url": source_url,
            "subtitle_url": item.get("url_subtitle") or "",
            "format_hint": self._infer_format_hint(source_url),
            "available_sources": {
                "low": item.get("url_video_low"),
                "medium": item.get("url_video"),
                "high": item.get("url_video_hd"),
                "subtitle": item.get("url_subtitle"),
            },
        }

    def _pick_source_url(self, item: dict[str, Any], preferred_quality: str) -> tuple[str, str]:
        quality_map = {
            "low": [("low", item.get("url_video_low"))],
            "medium": [("medium", item.get("url_video")), ("low", item.get("url_video_low"))],
            "high": [("high", item.get("url_video_hd")), ("medium", item.get("url_video")), ("low", item.get("url_video_low"))],
            "best": [("high", item.get("url_video_hd")), ("medium", item.get("url_video")), ("low", item.get("url_video_low"))],
        }
        for label, url in quality_map.get(preferred_quality, quality_map["best"]):
            if url:
                return url, label
        fallback = item.get("url_video") or item.get("url_video_low") or item.get("url_video_hd") or ""
        return fallback, "unknown"

    def _date_to_timestamp(self, value: str | None, *, end_of_day: bool = False) -> int | None:
        if not value:
            return None
        parsed = datetime.fromisoformat(value)
        if end_of_day:
            parsed = parsed.replace(hour=23, minute=59, second=59)
        return int(parsed.timestamp())

    def _apply_date_filters(
        self,
        results: list[dict[str, Any]],
        start_date: str | None,
        end_date: str | None,
    ) -> list[dict[str, Any]]:
        start_ts = self._date_to_timestamp(start_date)
        end_ts = self._date_to_timestamp(end_date, end_of_day=True)
        if start_ts is None and end_ts is None:
            return results

        filtered: list[dict[str, Any]] = []
        for item in results:
            air_date = item.get("air_date")
            if not air_date:
                continue
            item_ts = self._date_to_timestamp(air_date)
            if item_ts is None:
                continue
            if start_ts is not None and item_ts < start_ts:
                continue
            if end_ts is not None and item_ts > end_ts:
                continue
            filtered.append(item)
        return filtered

    def _to_text_plain_json(self, payload: dict[str, Any]) -> str:
        import json

        return json.dumps(payload)

    def _infer_format_hint(self, source_url: str) -> str:
        lowered = source_url.lower()
        if ".m3u8" in lowered:
            return "hls"
        if ".mp4" in lowered:
            return "mp4"
        return "generic"


mediathek_service = MediathekService()
