import tempfile
import unittest
from pathlib import Path

from app.db.database import database
from app.services.downloads import STATUS_PENDING, download_manager


class DownloadManagerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        database.path = Path(self.temp_dir.name) / "test.db"
        database.initialize()
        download_manager.update_download_root(str(Path(self.temp_dir.name) / "downloads"))

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_create_download_uses_configured_root(self) -> None:
        item = download_manager.create_download(
            {
                "title": "Terra X",
                "channel": "ZDF",
                "source_url": "https://example.invalid/video.mp4",
                "quality": "best",
                "metadata": {},
            }
        )
        self.assertEqual(item["status"], STATUS_PENDING)
        self.assertIn("terra-x", item["filename"])

    def test_retry_download_requeues_failed_item(self) -> None:
        item = download_manager.create_download(
            {
                "title": "Heute Journal",
                "channel": "ZDF",
                "source_url": "https://example.invalid/video.mp4",
                "quality": "best",
                "metadata": {},
            }
        )
        database.execute(
            "UPDATE downloads SET status = 'failed', error_message = 'kaputt' WHERE id = ?",
            (item["id"],),
        )
        updated = download_manager.retry_download(item["id"])
        self.assertIsNotNone(updated)
        self.assertEqual(updated["status"], STATUS_PENDING)

    def test_duplicate_download_returns_existing_item(self) -> None:
        first = download_manager.create_download(
            {
                "title": "Terra X",
                "channel": "ZDF",
                "air_date": "2026-08-12",
                "source_url": "https://example.invalid/video.mp4",
                "quality": "best",
                "metadata": {},
            }
        )
        second = download_manager.create_download(
            {
                "title": "Terra X",
                "channel": "ZDF",
                "air_date": "2026-08-12",
                "source_url": "https://example.invalid/video.mp4",
                "quality": "best",
                "metadata": {},
            }
        )
        self.assertEqual(first["id"], second["id"])
        self.assertTrue(second["duplicate_detected"])


if __name__ == "__main__":
    unittest.main()
