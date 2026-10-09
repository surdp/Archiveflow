import csv
import tempfile
import unittest
import zipfile
from pathlib import Path

from archiveflow.cli import inspect_source, iter_media, organize_source


class ArchiveFlowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.zip_path = self.root / "sample-export.zip"
        with zipfile.ZipFile(self.zip_path, "w") as archive:
            archive.writestr("media/posts/photo.jpg", b"fake-jpeg-data")
            archive.writestr("media/stories/clip.mp4", b"fake-video-data")
            archive.writestr("profile/profile_information.json", '{"not": "media"}')
            archive.writestr("media/posts/notes.txt", "skip me")

    def tearDown(self):
        self.temp.cleanup()

    def test_zip_scans_only_supported_media(self):
        items = list(iter_media(self.zip_path))
        self.assertEqual(len(items), 2)
        self.assertEqual({item.category for item in items}, {"images", "videos"})

    def test_dry_run_does_not_create_output(self):
        output = self.root / "planned-output"
        copied, _ = organize_source(self.zip_path, output, dry_run=True)
        self.assertEqual(copied, 2)
        self.assertFalse(output.exists())

    def test_organize_copies_media_and_writes_manifest(self):
        output = self.root / "organized"
        copied, unique_hashes = organize_source(self.zip_path, output)
        self.assertEqual(copied, 2)
        self.assertEqual(unique_hashes, 2)
        self.assertEqual(len(list((output / "images").glob("*"))), 1)
        self.assertEqual(len(list((output / "videos").glob("*"))), 1)
        with (output / "manifest.csv").open(newline="", encoding="utf-8-sig") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(len(row["sha256"]) == 64 for row in rows))

    def test_folder_scan_excludes_output_nested_inside_input(self):
        source = self.root / "extracted"
        source.mkdir()
        (source / "photo.png").write_bytes(b"png")
        output = source / "output"
        count, _ = organize_source(source, output)
        self.assertEqual(count, 1)
        # A second run must not re-ingest its own copied files.
        second, _ = organize_source(source, output)
        self.assertEqual(second, 1)


if __name__ == "__main__":
    unittest.main()
