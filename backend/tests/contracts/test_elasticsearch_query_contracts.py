import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

BACKEND_ROOT = Path(__file__).resolve().parents[2]
APP_DIR = BACKEND_ROOT / "app"
for p in (str(BACKEND_ROOT), str(APP_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from app import database  # noqa: E402
import run as flask_run  # noqa: E402


class TestElasticsearchQueryContracts(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.temp_db = Path(self._tmpdir.name) / "test_es_contract.db"
        self._env_patcher = patch.dict(
            os.environ,
            {"SDNFLOW_DB_PATH": str(self.temp_db)},
        )
        self._env_patcher.start()
        database.init_db()
        self.client = flask_run.app.test_client()

    def tearDown(self):
        self._env_patcher.stop()
        self._tmpdir.cleanup()

    @patch("run.requests.post")
    def test_port_traffic_history_contract_and_bounds(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "hits": {
                "hits": [
                    {
                        "_source": {
                            "@timestamp": "2026-11-01T00:00:00Z",
                            "switch_id": "of:0000000000000001",
                            "port_number": "1",
                            "rx_mbps": 0.012,
                            "tx_mbps": 0.011,
                            "rx_pps": 12.0,
                            "tx_pps": 11.0,
                            "sample_seconds": 5.0,
                        }
                    }
                ]
            }
        }
        mock_post.return_value = mock_resp

        res = self.client.get("/api/elk/port-traffic-history?minutes=60&limit=100")
        self.assertEqual(res.status_code, 200)
        body = res.get_json()
        self.assertEqual(body["source"], "Elasticsearch")
        self.assertEqual(body["count"], 1)
        self.assertEqual(body["data"][0]["switch_id"], "of:0000000000000001")

        # Out of bounds must return 400
        bad_res = self.client.get("/api/elk/port-traffic-history?minutes=0&limit=999")
        self.assertEqual(bad_res.status_code, 400)

    @patch("run.requests.post")
    def test_security_alerts_contract_and_bounds(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "hits": {
                "total": {"value": 1},
                "hits": [
                    {
                        "_source": {
                            "@timestamp": "2026-11-01T00:00:05Z",
                            "event_id": "evt-1",
                            "alert_key": "key-1",
                            "switch_id": "of:0000000000000001",
                            "port_number": "1",
                            "peak_pps": 10.5,
                            "threshold_pps": 4.0,
                            "test_only": True,
                            "status": "OPEN",
                        }
                    }
                ],
            }
        }
        mock_post.return_value = mock_resp

        res = self.client.get("/api/elk/security-alerts?minutes=60&limit=50")
        self.assertEqual(res.status_code, 200)
        body = res.get_json()
        self.assertEqual(body["total"], 1)
        self.assertTrue(body["alerts"][0]["test_only"])


if __name__ == "__main__":
    unittest.main()

