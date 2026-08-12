from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from app.db.database import database
from app.models.schemas import SearchRequest
from app.services.downloads import download_manager
from app.services.mediathek import mediathek_service


class RuleService:
    def list_rules(self) -> list[dict[str, Any]]:
        rules = database.fetch_all(
            """
            SELECT
                r.*,
                COUNT(m.id) AS match_count,
                MAX(m.matched_at) AS latest_match_at
            FROM rules r
            LEFT JOIN rule_matches m ON m.rule_id = r.id
            GROUP BY r.id
            ORDER BY r.updated_at DESC
            """
        )
        return [self._normalize_rule(rule) for rule in rules]

    def create_rule(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not payload.get("query") and not payload.get("channel") and not payload.get("topic"):
            raise ValueError("Mindestens Suchbegriff, Sender oder Thema muss gesetzt sein.")
        rule_id = database.execute(
            """
            INSERT INTO rules(
                name, query, channel, topic, quality, min_duration_minutes, max_duration_minutes,
                target_directory, keep_latest, auto_download, enabled, interval_minutes,
                folder_template, filename_template
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload["name"],
                payload.get("query", ""),
                payload.get("channel", ""),
                payload.get("topic", ""),
                payload.get("quality", "best"),
                payload.get("min_duration_minutes"),
                payload.get("max_duration_minutes"),
                payload.get("target_directory"),
                payload.get("keep_latest"),
                1 if payload.get("auto_download") else 0,
                1 if payload.get("enabled", True) else 0,
                payload.get("interval_minutes", 180),
                payload.get("folder_template"),
                payload.get("filename_template"),
            ),
        )
        return self.get_rule(rule_id)

    def get_rule(self, rule_id: int) -> dict[str, Any] | None:
        rule = database.fetch_one(
            """
            SELECT
                r.*,
                COUNT(m.id) AS match_count,
                MAX(m.matched_at) AS latest_match_at
            FROM rules r
            LEFT JOIN rule_matches m ON m.rule_id = r.id
            WHERE r.id = ?
            GROUP BY r.id
            """,
            (rule_id,),
        )
        return self._normalize_rule(rule) if rule else None

    def list_rule_matches(self, rule_id: int, limit: int = 20) -> list[dict[str, Any]]:
        return database.fetch_all(
            """
            SELECT *
            FROM rule_matches
            WHERE rule_id = ?
            ORDER BY air_date DESC, matched_at DESC
            LIMIT ?
            """,
            (rule_id, limit),
        )

    async def run_rule(self, rule_id: int, limit: int = 15) -> dict[str, Any]:
        rule = self.get_rule(rule_id)
        if not rule:
            raise ValueError("Regel nicht gefunden.")
        if not rule["enabled"]:
            raise ValueError("Regel ist deaktiviert.")
        response = await mediathek_service.search(
            SearchRequest(
                query=rule["query"],
                channel=rule["channel"],
                topic=rule["topic"],
                quality=rule["quality"],
                min_duration_minutes=rule["min_duration_minutes"],
                max_duration_minutes=rule["max_duration_minutes"],
                size=limit,
                offset=0,
            )
        )
        new_matches = 0
        queued_downloads = 0
        for item in response["results"]:
            inserted = self._store_match(rule, item)
            if inserted:
                new_matches += 1
                if rule["auto_download"]:
                    download = download_manager.create_download(
                        {
                            **item,
                            "quality": rule["quality"],
                            "target_directory": rule["target_directory"],
                            "folder_template": rule.get("folder_template"),
                            "filename_template": rule.get("filename_template"),
                        }
                    )
                    database.execute(
                        "UPDATE rule_matches SET download_id = ? WHERE rule_id = ? AND external_id = ?",
                        (download["id"], rule["id"], item["external_id"]),
                    )
                    if not download.get("duplicate_detected"):
                        queued_downloads += 1

        database.execute(
            """
            UPDATE rules
            SET last_run_at = CURRENT_TIMESTAMP,
                last_error = NULL,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (rule["id"],),
        )
        self._prune_rule(rule["id"], rule.get("keep_latest"))
        updated_rule = self.get_rule(rule["id"])
        return {
            "rule": updated_rule,
            "new_matches": new_matches,
            "queued_downloads": queued_downloads,
            "recent_matches": self.list_rule_matches(rule["id"], limit=10),
        }

    async def run_all_enabled_rules(self, limit: int = 15) -> dict[str, Any]:
        results: list[dict[str, Any]] = []
        for rule in self.list_rules():
            if rule["enabled"]:
                results.append(await self.run_rule(rule["id"], limit=limit))
        return {"items": results}

    async def run_due_rules(self, limit: int = 15) -> dict[str, Any]:
        items: list[dict[str, Any]] = []
        now = datetime.now(UTC)
        for rule in self.list_rules():
            if not rule["enabled"]:
                continue
            if self._is_due(rule, now):
                try:
                    items.append(await self.run_rule(rule["id"], limit=limit))
                except Exception as exc:
                    database.execute(
                        """
                        UPDATE rules
                        SET last_error = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                        """,
                        (str(exc), rule["id"]),
                    )
        return {"items": items}

    def _is_due(self, rule: dict[str, Any], now: datetime) -> bool:
        if not rule.get("last_run_at"):
            return True
        last_run = self._parse_utc(rule["last_run_at"])
        return now - last_run >= timedelta(minutes=rule["interval_minutes"])

    def _store_match(self, rule: dict[str, Any], item: dict[str, Any]) -> bool:
        existing = database.fetch_one(
            "SELECT id FROM rule_matches WHERE rule_id = ? AND external_id = ?",
            (rule["id"], item["external_id"]),
        )
        if existing:
            return False
        database.execute(
            """
            INSERT INTO rule_matches(
                rule_id, external_id, title, channel, topic, air_date, source_url, quality, website_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                rule["id"],
                item["external_id"],
                item["title"],
                item.get("channel"),
                item.get("topic"),
                item.get("air_date"),
                item["source_url"],
                item.get("quality"),
                item.get("website_url"),
            ),
        )
        return True

    def _prune_rule(self, rule_id: int, keep_latest: int | None) -> None:
        if not keep_latest:
            return
        rows = database.fetch_all(
            """
            SELECT id
            FROM rule_matches
            WHERE rule_id = ?
            ORDER BY air_date DESC, matched_at DESC
            """,
            (rule_id,),
        )
        for row in rows[keep_latest:]:
            database.execute("DELETE FROM rule_matches WHERE id = ?", (row["id"],))

    def _normalize_rule(self, rule: dict[str, Any]) -> dict[str, Any]:
        rule["auto_download"] = bool(rule["auto_download"])
        rule["enabled"] = bool(rule["enabled"])
        return rule

    def _parse_utc(self, value: str) -> datetime:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)


rule_service = RuleService()
