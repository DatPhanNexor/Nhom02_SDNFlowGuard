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

from app import controller_actions, database  # noqa: E402


class TestOnosPayloadContracts(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.temp_db = Path(self._tmpdir.name) / "test_onos_contract.db"
        self._env_patcher = patch.dict(
            os.environ,
            {
                "SDNFLOW_DB_PATH": str(self.temp_db),
                "SDNFLOW_DEFENSE_MODE": "DRY_RUN",
            },
        )
        self._env_patcher.start()
        database.init_db()

    def tearDown(self):
        self._env_patcher.stop()
        self._tmpdir.cleanup()

    def test_acl_rule_preview_conforms_to_onos_acl_contract(self):
        res = controller_actions.block_ip(
            src_ip="10.0.0.1/32",
            dst_ip="10.0.0.2/32",
            ip_proto="ICMP",
            dry_run=True,
        )
        self.assertEqual(res["status"], "DRY_RUN_SIMULATED")
        acl = res["acl_rule_preview"]
        self.assertEqual(acl["action"], "DENY")
        self.assertEqual(acl["srcIp"], "10.0.0.1/32")
        self.assertEqual(acl["dstIp"], "10.0.0.2/32")
        self.assertEqual(acl["ethType"], "0x0800")

    def test_point_to_point_intent_preview_conforms_to_onos_intent_contract(self):
        res = controller_actions.redirect_traffic(
            "10.0.0.1/32",
            "10.0.0.6/32",
            "1",
            "2",
            "of:0000000000000001",
            dry_run=True,
        )
        self.assertEqual(res["status"], "DRY_RUN_SIMULATED")
        intent = res["intent_preview"]
        self.assertEqual(intent["type"], "PointToPointIntent")
        self.assertEqual(intent["ingressPoint"]["device"], "of:0000000000000001")
        self.assertEqual(intent["treatment"]["instructions"][0]["ip"], "10.0.0.6")


if __name__ == "__main__":
    unittest.main()

