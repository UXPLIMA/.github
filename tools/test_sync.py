import tempfile
import unittest
from pathlib import Path

import sync


class SyncTest(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self.target = Path(self._dir.name)

    def tearDown(self):
        self._dir.cleanup()

    def test_write_creates_docs_internals(self):
        self.assertEqual(sync.main(["--write", str(self.target)]), 0)
        page = self.target / "docs/internals/uxm-conventions.md"
        self.assertEqual(page.read_bytes(), (sync.SOURCE_ROOT / "docs/internals/uxm-conventions.md").read_bytes())
        self.assertTrue((self.target / ".editorconfig").is_file())

    def test_write_then_check_is_clean(self):
        sync.main(["--write", str(self.target)])
        self.assertEqual(sync.drifted(self.target), [])
        self.assertEqual(sync.main(["--check", str(self.target)]), 0)

    def test_check_reports_drift(self):
        sync.main(["--write", str(self.target)])
        page = self.target / "docs/internals/uxm-conventions.md"
        page.write_text(page.read_text(encoding="utf-8") + "local edit\n", encoding="utf-8")
        self.assertEqual(sync.drifted(self.target), ["docs/internals/uxm-conventions.md"])
        self.assertEqual(sync.main(["--check", str(self.target)]), 1)

    def test_check_reports_missing_file(self):
        self.assertIn(".editorconfig", sync.drifted(self.target))


if __name__ == "__main__":
    unittest.main()
