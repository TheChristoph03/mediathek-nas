import tempfile
import unittest
from pathlib import Path

from app.db.database import database
from app.services.downloads import download_manager
from app.services.imports import import_service
from app.services.rss import rss_service


class ImportAndRssTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        database.path = Path(self.temp_dir.name) / "test.db"
        database.initialize()
        download_manager.update_download_root(str(Path(self.temp_dir.name) / "downloads"))

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_filesystem_import_creates_completed_entry(self) -> None:
        media_dir = Path(self.temp_dir.name) / "media" / "ZDF"
        media_dir.mkdir(parents=True, exist_ok=True)
        file_path = media_dir / "2026-08-11_terra_x.mp4"
        file_path.write_bytes(b"fake")

        response = import_service.import_filesystem(str(Path(self.temp_dir.name) / "media"))

        self.assertEqual(response["imported"], 1)
        self.assertEqual(response["items"][0]["status"], "completed")
        self.assertTrue(response["items"][0]["imported"])

    def test_rss_feed_contains_item_title(self) -> None:
        xml = rss_service.build_feed(
            title="Testfeed",
            description="Beschreibung",
            feed_url="http://localhost/feed",
            items=[{"title": "Terra X", "source_url": "https://example.invalid/video.mp4", "air_date": "2026-08-12"}],
        )
        self.assertIn("<title>Testfeed</title>", xml)
        self.assertIn("<title>Terra X</title>", xml)


if __name__ == "__main__":
    unittest.main()
