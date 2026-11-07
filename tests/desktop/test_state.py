from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "desktop/workspace"))
from state import MAX_NOTE, StateStore


class StorageTests(unittest.TestCase):
    def test_unicode_notes_and_theme_survive_restart(self):
        with tempfile.TemporaryDirectory() as folder:
            store = StateStore(folder)
            data = store.load()
            data["notes"]["personal"] = "Một ý tưởng mới — tiếng Việt"
            data["notes"]["creative"] = "Bản phác thảo"
            data["theme"] = "light"
            store.save(data)
            self.assertEqual(StateStore(folder).load(), data)
            self.assertEqual(store.path.stat().st_mode & 0o777, 0o600)

    def test_corrupt_and_wrong_type_data_recovers(self):
        with tempfile.TemporaryDirectory() as folder:
            store = StateStore(folder)
            for value in ['{broken', '[]', '{"notes": [1], "theme":"invalid"}']:
                store.path.write_text(value)
                self.assertEqual(store.load()["notes"]["personal"], "")
                self.assertEqual(store.load()["theme"], "dark")

    def test_write_failure_keeps_previous_notes(self):
        with tempfile.TemporaryDirectory() as folder:
            store = StateStore(folder)
            data = store.load()
            data["notes"]["personal"] = "keep me"
            store.save(data)
            with patch("state.os.replace", side_effect=OSError("full disk")):
                with self.assertRaises(OSError):
                    store.save({"notes": {"personal": "changed"}})
            self.assertEqual(store.load(), data)
            self.assertEqual(list(Path(folder).iterdir()), [store.path])

    def test_loaded_notes_are_bounded(self):
        with tempfile.TemporaryDirectory() as folder:
            store = StateStore(folder)
            data = store.load()
            data["notes"]["personal"] = "a" * (MAX_NOTE + 1)
            store.save(data)
            self.assertEqual(len(store.load()["notes"]["personal"]), MAX_NOTE)
