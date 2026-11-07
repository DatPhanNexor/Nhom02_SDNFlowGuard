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
import run as flask_run  # noqa: E402


class TestFrontendBackendApiContracts(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.temp_db = Path(self._tmpdir.name) / "test_fe_contract.db"
        self._env_patcher = patch.dict(
            os.environ,
            {"SDNFLOW_DB_PATH": str(self.temp_db)},
        )
        self._env_patcher.start()
        database.init_db()
        database.save_settings(
            {
                "Mode": "balanced",
                "SDN Controller IP": "127.0.0.1",
                "ELK IP Address": "127.0.0.1",
                "Honeypot IP Address": "10.0.0.6",
            }
        )
        self.client = flask_run.app.test_client()

    def tearDown(self):
        self._env_patcher.stop()
        self._tmpdir.cleanup()

    def test_frontend_expected_response_shapes(self):
        for route in ("/api/get-flows", "/api/get-actions", "/api/get-anomalies", "/api/get-settings"):
            res = self.client.get(route)
            self.assertEqual(res.status_code, 200, f"Failed GET {route}")
            payload = res.get_json()
            self.assertIn("data", payload, f"Missing 'data' key in {route}")


if __name__ == "__main__":
    unittest.main()

