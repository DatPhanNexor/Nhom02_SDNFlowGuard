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


class TestSQLiteRepository(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.temp_db = Path(self._tmpdir.name) / "test_repo.db"
        self._env_patcher = patch.dict(
            os.environ,
            {"SDNFLOW_DB_PATH": str(self.temp_db)},
        )
        self._env_patcher.start()
        database.init_db()

    def tearDown(self):
        self._env_patcher.stop()
        self._tmpdir.cleanup()

    def test_settings_crud(self):
        database.save_settings({"Mode": "strict", "SDN Controller IP": "127.0.0.1"})
        self.assertEqual(database.get_setting_value("Mode"), "strict")
        all_settings = database.get_settings()
        self.assertEqual(all_settings["SDN Controller IP"], "127.0.0.1")

    def test_events_and_actions_crud(self):
        database.save_event(
            {
                "Source": "IDS",
                "Event": "SYN Flood",
                "Score": 80,
                "SourceIP": "10.0.0.1",
                "DestinationIP": "10.0.0.2",
            }
        )
        anomalies = database.get_anomalies()
        self.assertEqual(len(anomalies), 1)
        self.assertEqual(anomalies[0]["source_ip"], "10.0.0.1")

        database.record_action("Block [DRY_RUN]", "Test block", "10.0.0.1", "Admin")
        actions = database.get_actions()
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]["action_type"], "Block [DRY_RUN]")

        database.delete_event_entry("10.0.0.1")
        self.assertEqual(len(database.get_anomalies()), 0)

    def test_flows_crud(self):
        database.save_flows(
            [
                {
                    "id": "flow-1",
                    "source_ip": "10.0.0.1/32",
                    "destination_ip": "10.0.0.2/32",
                    "protocol": "IPv4",
                    "bandwidth": 2048,
                    "flow_duration": 12,
                    "priority": 40000,
                    "app_id": "org.onosproject.rest",
                    "device_id": "of:0000000000000001",
                }
            ]
        )
        flows = database.get_flows()
        self.assertEqual(len(flows), 1)
        self.assertEqual(flows[0]["id"], "flow-1")


if __name__ == "__main__":
    unittest.main()

