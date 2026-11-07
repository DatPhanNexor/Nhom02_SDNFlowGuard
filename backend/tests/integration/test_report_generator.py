import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

BACKEND_ROOT = Path(__file__).resolve().parents[2]
APP_DIR = BACKEND_ROOT / "app"
for p in (str(BACKEND_ROOT), str(APP_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from app import database  # noqa: E402
from app.report import ReportGenerator  # noqa: E402


class TestReportGenerator(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.temp_db = Path(self._tmpdir.name) / "test_report.db"
        self._env_patcher = patch.dict(
            os.environ,
            {"SDNFLOW_DB_PATH": str(self.temp_db)},
        )
        self._env_patcher.start()
        database.init_db()
        database.record_action("Block [DRY_RUN]", "Simulated block", "10.0.0.1", "Admin")

    def tearDown(self):
        self._env_patcher.stop()
        self._tmpdir.cleanup()

    def test_generate_report_and_pdf_fallback(self):
        gen = ReportGenerator()
        report_json = gen.generate_report("actions")
        self.assertEqual(report_json["report_type"], "actions")
        self.assertEqual(len(report_json["data"]), 1)

        pdf_bytes = gen.generate_pdf_report("actions")
        self.assertTrue(pdf_bytes.startswith(b"%PDF-1.4"))
        self.assertIn(b"%%EOF", pdf_bytes)


if __name__ == "__main__":
    unittest.main()

