import unittest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import requests

from app import database
from app.controller_actions import unblock_ip
import run


class TestFaultInjectionAndResilience(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.temp_db = Path(self._tmpdir.name) / "test_fault.db"
        self._env_patcher = patch.dict(
            os.environ,
            {
                "SDNFLOW_DB_PATH": str(self.temp_db),
                "SDNFLOW_DEFENSE_MODE": "DRY_RUN",
                "SDNFLOW_API_KEY": "",
            },
        )
        self._env_patcher.start()
        database.init_db()
        database.save_settings({"SDN Controller IP": "127.0.0.1"})

        self.app = run.app
        self.client = self.app.test_client()

    def tearDown(self):
        self._env_patcher.stop()
        self._tmpdir.cleanup()

    def test_onos_timeout_on_live_flows_returns_502(self):
        """Verify ONOS REST API timeout does not crash backend and returns HTTP 502."""
        with patch("requests.get", side_effect=requests.exceptions.Timeout("ONOS connection timed out")):
            response = self.client.get("/api/live-flows")
            self.assertEqual(response.status_code, 502)
            data = response.get_json()
            self.assertIn("error", data)

    def test_malformed_ip_block_request_returns_400(self):
        """Verify invalid IP addresses and prefix lengths are rejected with HTTP 400."""
        for bad_ip in ("999.999.999.999", "not_an_ip", "10.0.0.1/45", "10.0.0.1/-1"):
            res = self.client.post("/api/block", json={"srcIp": bad_ip, "dry_run": True})
            self.assertEqual(res.status_code, 400, f"Expected 400 for bad IP {bad_ip}")
            self.assertIn("error", res.get_json())

    def test_rollback_target_missing_returns_skipped_status(self):
        """Verify rollback in active enforcement when rule does not exist returns ROLLBACK_SKIPPED_NO_RULE."""
        with patch.dict(os.environ, {"SDNFLOW_DEFENSE_MODE": "ACTIVE_ENFORCEMENT"}):
            with patch("app.controller_actions.list_acl_rules", return_value=[]):
                res = self.client.post("/api/defense/rollback", json={"srcIp": "10.0.0.55", "dry_run": False})
                self.assertEqual(res.status_code, 200)
                data = res.get_json()
                self.assertEqual(data["status"], "ROLLBACK_SKIPPED_NO_RULE")
                self.assertFalse(data["executed"])
                self.assertEqual(data["verification_result"], "RULE_NOT_FOUND")

    def test_live_rollback_verified_removal(self):
        """Verify live rollback confirms deletion by re-querying rule list."""
        mock_rule = {"id": "acl_rule_999", "srcIp": "10.0.0.88/32", "dstIp": ""}
        mock_del_resp = MagicMock()
        mock_del_resp.status_code = 204

        with patch.dict(os.environ, {"SDNFLOW_DEFENSE_MODE": "ACTIVE_ENFORCEMENT"}):
            # First query returns rule, second query returns empty (verified removed)
            with patch("app.controller_actions.list_acl_rules", side_effect=[[mock_rule], []]), \
                 patch("requests.delete", return_value=mock_del_resp):
                res = unblock_ip(src_ip="10.0.0.88", dry_run=False, return_structured=True)
                self.assertEqual(res["status"], "ROLLBACK_COMPLETED")
                self.assertTrue(res["executed"])
                self.assertEqual(res["rule_id"], "acl_rule_999")
                self.assertEqual(res["verification_result"], "ROLLBACK_VERIFIED")
                self.assertEqual(res["controller_status"], 204)

    def test_live_rollback_controller_failure_handling(self):
        """Verify controller network exception during delete returns ROLLBACK_FAILED."""
        mock_rule = {"id": "acl_rule_fail", "srcIp": "10.0.0.77/32"}
        with patch.dict(os.environ, {"SDNFLOW_DEFENSE_MODE": "ACTIVE_ENFORCEMENT"}):
            with patch("app.controller_actions.list_acl_rules", return_value=[mock_rule]), \
                 patch("requests.delete", side_effect=requests.exceptions.ConnectionError("ONOS down")):
                res = unblock_ip(src_ip="10.0.0.77", dry_run=False, return_structured=True)
                self.assertEqual(res["status"], "ROLLBACK_FAILED")
                self.assertFalse(res["executed"])
                self.assertEqual(res["verification_result"], "EXECUTION_FAILED")

    def test_onos_failure_on_topology_returns_502_with_degraded_structure(self):
        """Verify ONOS failure returns HTTP 502 and a graceful degraded structure."""
        with patch("requests.get", side_effect=requests.exceptions.ConnectionError("Connection refused")):
            res = self.client.get("/api/topology")
            self.assertEqual(res.status_code, 502)
            data = res.get_json()
            self.assertEqual(data["controller_status"], "UNAVAILABLE")
            self.assertEqual(data["devices"], [])
            self.assertEqual(data["hosts"], [])
            self.assertEqual(data["links"], [])

    def test_onos_auth_defaults_to_onos_rocks(self):
        """Verify default credentials fallback safely to onos/rocks."""
        from run import _resolve_onos_auth
        with patch.dict(os.environ, {}, clear=True):
            auth = _resolve_onos_auth()
            self.assertEqual(auth, ("onos", "rocks"))


if __name__ == "__main__":
    unittest.main()
