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


class TestWebhookReception(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.temp_db = Path(self._tmpdir.name) / "test_webhook.db"
        self._env_patcher = patch.dict(
            os.environ,
            {
                "SDNFLOW_DB_PATH": str(self.temp_db),
                "SDNFLOW_DEFENSE_MODE": "DRY_RUN",
            },
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

    def test_valid_webhook_event_is_saved_and_evaluated(self):
        payload = {
            "Source": "IDS",
            "Event": "ICMP Flood Candidate",
            "Score": 50,
            "SourceIP": "10.0.0.1",
            "DestinationIP": "10.0.0.2",
        }
        res = self.client.post("/webhook", json=payload)
        self.assertEqual(res.status_code, 200)
        anomalies = database.get_anomalies()
        self.assertEqual(len(anomalies), 1)
        self.assertEqual(anomalies[0]["source_ip"], "10.0.0.1")

    def test_invalid_webhook_payload_returns_400(self):
        res = self.client.post("/webhook", json={"Source": "IDS"})
        self.assertEqual(res.status_code, 400)


if __name__ == "__main__":
    unittest.main()

