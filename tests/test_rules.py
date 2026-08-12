import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from app.db.database import database
from app.services.downloads import download_manager
from app.services.rules import rule_service


class RuleServiceTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        database.path = Path(self.temp_dir.name) / "test.db"
        database.initialize()
        download_manager.update_download_root(str(Path(self.temp_dir.name) / "downloads"))

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    async def test_create_rule_requires_filter(self) -> None:
        with self.assertRaises(ValueError):
            rule_service.create_rule({"name": "leer", "query": "", "channel": "", "topic": ""})

    async def test_run_rule_stores_matches_and_downloads(self) -> None:
        rule = rule_service.create_rule(
            {
                "name": "Terra X",
                "query": "Terra X",
                "channel": "ZDF",
                "quality": "best",
                "auto_download": True,
                "keep_latest": 5,
            }
        )
        fake_result = {
            "total": 1,
            "offset": 0,
            "size": 1,
            "results": [
                {
                    "external_id": "abc-1",
                    "title": "Terra X - Alpen",
                    "topic": "Doku",
                    "channel": "ZDF",
                    "description": "Beschreibung",
                    "website_url": "https://example.invalid/show",
                    "duration_seconds": 3600,
                    "air_date": "2026-08-11",
                    "quality": "high",
                    "source_url": "https://example.invalid/video.mp4",
                }
            ],
        }
        with patch("app.services.rules.mediathek_service.search", new=AsyncMock(return_value=fake_result)):
            response = await rule_service.run_rule(rule["id"], limit=5)

        self.assertEqual(response["new_matches"], 1)
        self.assertEqual(response["queued_downloads"], 1)
        matches = rule_service.list_rule_matches(rule["id"])
        self.assertEqual(len(matches), 1)


if __name__ == "__main__":
    unittest.main()
