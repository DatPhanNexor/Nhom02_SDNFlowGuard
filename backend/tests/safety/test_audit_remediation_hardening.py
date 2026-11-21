import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
import requests

BACKEND_ROOT = Path(__file__).resolve().parents[2]
APP_DIR = BACKEND_ROOT / "app"
for p in (str(BACKEND_ROOT), str(APP_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from app import controller_actions, database  # noqa: E402
from sdnflowguard.domain.policies.safety_gate import evaluate_safety_gate  # noqa: E402
from sdnflowguard.interfaces.http.security import is_operator_authenticated  # noqa: E402
import run as flask_run  # noqa: E402


class TestAuditRemediationHardening(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.temp_db = Path(self._tmpdir.name) / "test_audit_hardening.db"
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

    def test_p0_01_missing_api_key_never_authenticates_live_manual_approval(self):
        self.assertFalse(is_operator_authenticated({}))
        with patch.dict(
            os.environ,
            {"SDNFLOW_DEFENSE_MODE": "MANUAL_APPROVAL", "SDNFLOW_API_KEY": ""},
        ):
            with patch("requests.post") as mock_post:
                res = self.client.post(
                    "/api/block",
                    json={"srcIp": "10.0.0.1", "dry_run": False},
                )
                self.assertEqual(res.status_code, 403)
                body = res.get_json()
                self.assertEqual(body["status"], "APPROVAL_REQUIRED")
                self.assertFalse(body["executed"])
                mock_post.assert_not_called()

    def test_p0_02_authenticated_block_propagates_and_verifies_onos_rule(self):
        mock_post_resp = MagicMock()
        mock_post_resp.status_code = 201
        mock_rules = [{"id": "acl-42", "srcIp": "10.0.0.1/32", "action": "DENY"}]

        with patch.dict(
            os.environ,
            {
                "SDNFLOW_DEFENSE_MODE": "MANUAL_APPROVAL",
                "SDNFLOW_API_KEY": "audit-secret-key",
            },
        ):
            with patch("requests.post", return_value=mock_post_resp), patch(
                "app.controller_actions.list_acl_rules", return_value=mock_rules
            ):
                res = self.client.post(
                    "/api/block",
                    json={"srcIp": "10.0.0.1", "dry_run": False},
                    headers={"X-SDNFlow-API-Key": "audit-secret-key"},
                )
                self.assertEqual(res.status_code, 200)
                body = res.get_json()
                self.assertEqual(body["status"], "RULE_APPLIED")
                self.assertTrue(body["executed"])
                self.assertTrue(body["controller_accepted"])
                self.assertEqual(body["verification_status"], "RULE_INSTALLED")
                self.assertEqual(body["rule_id"], "acl-42")
                self.assertIn("timestamp_utc", body)

    def test_p0_03_save_flows_enforces_api_key_when_configured(self):
        with patch.dict(os.environ, {"SDNFLOW_API_KEY": "audit-secret-key"}):
            res = self.client.post("/api/save-flows")
            self.assertEqual(res.status_code, 401)

    def test_p1_02_rate_limit_and_redirect_return_404_and_502_not_false_200(self):
        with patch.dict(
            os.environ,
            {
                "SDNFLOW_DEFENSE_MODE": "MANUAL_APPROVAL",
                "SDNFLOW_API_KEY": "audit-secret-key",
            },
        ):
            headers = {"X-SDNFlow-API-Key": "audit-secret-key"}

            # Missing host in topology must return 404, never false 200
            with patch(
                "app.controller_actions.get_topology_data",
                return_value={"devices": [], "hosts": [], "links": []},
            ):
                res_rl = self.client.post(
                    "/api/rate-limit",
                    json={"hostIp": "10.0.0.9", "rateLimitBps": 50000, "dry_run": False},
                    headers=headers,
                )
                self.assertEqual(res_rl.status_code, 404)
                self.assertEqual(res_rl.get_json()["status"], "HOST_NOT_FOUND")

                res_rd = self.client.post(
                    "/api/redirect",
                    json={"srcIp": "10.0.0.9", "redirectIp": "10.0.0.6", "dry_run": False},
                    headers=headers,
                )
                self.assertEqual(res_rd.status_code, 404)
                self.assertEqual(res_rd.get_json()["status"], "HOST_NOT_FOUND")

            # ONOS ConnectionError must return controlled 502, never unhandled 500
            sample_topo = {
                "devices": [{"id": "of:0000000000000001"}],
                "links": [],
                "hosts": [
                    {
                        "mac": "00:00:00:00:00:01",
                        "ipAddresses": ["10.0.0.1"],
                        "locations": [{"elementId": "of:0000000000000001", "port": "1"}],
                    }
                ],
            }
            with patch("app.controller_actions.get_topology_data", return_value=sample_topo), patch(
                "requests.post", side_effect=requests.exceptions.ConnectionError("ONOS unreachable")
            ):
                res_err = self.client.post(
                    "/api/rate-limit",
                    json={"hostIp": "10.0.0.1", "rateLimitBps": 50000, "dry_run": False},
                    headers=headers,
                )
                self.assertEqual(res_err.status_code, 502)
                self.assertEqual(res_err.get_json()["status"], "EXECUTION_FAILED")

    def test_p1_03_unblock_post_delete_none_does_not_raise_typeerror(self):
        mock_rule = {"id": "acl_rule_777", "srcIp": "10.0.0.77/32", "dstIp": ""}
        mock_del = MagicMock()
        mock_del.status_code = 204
        with patch.dict(os.environ, {"SDNFLOW_DEFENSE_MODE": "ACTIVE_ENFORCEMENT"}):
            with patch("app.controller_actions.list_acl_rules", side_effect=[[mock_rule], None]), patch(
                "requests.delete", return_value=mock_del
            ):
                res = controller_actions.unblock_ip(
                    src_ip="10.0.0.77", dry_run=False, return_structured=True
                )
                self.assertEqual(res["status"], "ROLLBACK_COMPLETED")
                self.assertEqual(res["verification_result"], "CONTROLLER_ACCEPTED_UNVERIFIED")
                self.assertIn("timestamp_utc", res)

    def test_p1_03_rate_limit_location_header_and_truthful_rollback_plan(self):
        verdict = evaluate_safety_gate(
            action_type="throttle_traffic",
            target_ip="10.0.0.1",
        )
        self.assertEqual(verdict.rollback_plan["rollback_action"], "remove_meter_and_flow")

        sample_topo = {
            "devices": [{"id": "of:0000000000000001"}],
            "links": [],
            "hosts": [
                {
                    "mac": "00:00:00:00:00:01",
                    "ipAddresses": ["10.0.0.1"],
                    "locations": [{"elementId": "of:0000000000000001", "port": "1"}],
                }
            ],
        }
        meter_resp = MagicMock()
        meter_resp.status_code = 201
        meter_resp.headers = {"Location": "http://127.0.0.1:8181/onos/v1/meters/of:0000000000000001/17"}
        flow_resp = MagicMock()
        flow_resp.status_code = 201

        with patch.dict(
            os.environ,
            {
                "SDNFLOW_DEFENSE_MODE": "MANUAL_APPROVAL",
                "SDNFLOW_API_KEY": "audit-secret-key",
            },
        ):
            with patch("app.controller_actions.get_topology_data", return_value=sample_topo), patch(
                "requests.post", side_effect=[meter_resp, flow_resp]
            ):
                res = controller_actions.rate_limit_for_host(
                    host_ip="10.0.0.1",
                    rate_limit_bps=80000,
                    dry_run=False,
                    operator_authenticated=True,
                )
                self.assertEqual(res["status"], "RULE_APPLIED")
                self.assertEqual(res["meter_id"], "17")
                self.assertEqual(res["device_id"], "of:0000000000000001")
                self.assertEqual(res["rate_kb_per_sec"], 80)
                self.assertEqual(res["verification_status"], "CONTROLLER_ACCEPTED_UNVERIFIED")


if __name__ == "__main__":
    unittest.main()
