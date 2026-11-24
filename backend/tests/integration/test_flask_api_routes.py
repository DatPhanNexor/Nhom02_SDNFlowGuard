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


class TestFlaskApiRoutes(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.temp_db = Path(self._tmpdir.name) / "test_api.db"
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

        # Controlled test fixtures for ONOS Controller & Topology (6 Switches, 9 Hosts, 10 Directed Links)
        self.mock_topology_fixture = {
            "devices": [
                {
                    "id": f"of:000000000000000{i}",
                    "available": True,
                    "hw": "Open vSwitch",
                    "sw": "3.7.1",
                    "annotations": {"protocol": "OF_13", "datapathDescription": f"s{i}"},
                }
                for i in range(1, 7)
            ],
            "hosts": [
                {
                    "id": f"00:00:00:00:00:0{i}/None",
                    "mac": f"00:00:00:00:00:0{i}",
                    "ipAddresses": [f"10.0.0.{i}"],
                    "locations": [{"elementId": f"of:000000000000000{(i+1)//2}", "port": "1"}],
                }
                for i in range(1, 10)
            ],
            "links": [
                {
                    "src": {"device": f"of:000000000000000{i}", "port": "2"},
                    "dst": {"device": f"of:000000000000000{i+1}", "port": "1"},
                    "state": "ACTIVE",
                }
                for i in range(1, 11)
            ],
        }
        self.mock_controller_info_fixture = {
            "available": True,
            "status": "UP / ONLINE",
            "device_count": 6,
            "devices": self.mock_topology_fixture["devices"],
            "url": "http://127.0.0.1:8181/onos/v1",
        }

        self._mock_topo_patcher = patch(
            "app.chatbot.get_topology_data",
            return_value=self.mock_topology_fixture,
        )
        self._mock_ctrl_patcher = patch(
            "app.chatbot._get_live_controller_info",
            return_value=self.mock_controller_info_fixture,
        )
        self.mock_get_topology_data = self._mock_topo_patcher.start()
        self.mock_get_live_controller_info = self._mock_ctrl_patcher.start()

    def tearDown(self):
        self._mock_topo_patcher.stop()
        self._mock_ctrl_patcher.stop()
        self._env_patcher.stop()
        self._tmpdir.cleanup()

    def test_root_index_endpoint(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        body = res.get_json()
        self.assertEqual(body["service"], "SDNFlowGuard Backend API")
        self.assertEqual(body["health_endpoint"], "/api/health")
        self.assertEqual(body["docs_url"], "/docs")
        self.assertEqual(body["dashboard_url"], "http://127.0.0.1:3000")
        self.assertEqual(body["message"], "Backend API is available.")

    def test_docs_html_endpoint(self):
        res = self.client.get("/docs")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/html", res.content_type)
        html_text = res.get_data(as_text=True)
        self.assertIn("SDNFlowGuard — REST API Reference", html_text)
        self.assertIn("/api/health", html_text)
        self.assertIn("/api/chatbot", html_text)
        self.assertIn("READ-ONLY", html_text)

    def test_nonexistent_route_returns_404(self):
        res = self.client.get("/nonexistent-route")
        self.assertEqual(res.status_code, 404)

    def test_health_endpoint(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        body = res.get_json()
        self.assertEqual(body["status"], "OK")
        self.assertEqual(body["defense_mode"], "DRY_RUN")
        self.assertTrue(body["step63_evidence_present"])

    def test_step64_evidence_correlation_endpoint(self):
        res = self.client.get("/api/defense/evidence-correlation")
        self.assertEqual(res.status_code, 200)
        body = res.get_json()
        self.assertEqual(body["status"], "SUCCESS")
        self.assertEqual(body["data"]["total_packets"], 24)
        self.assertEqual(body["data"]["security_assessment"]["decision"], "OBSERVE")

    def test_defense_evaluate_endpoint(self):
        res = self.client.get("/api/defense/evaluate")
        self.assertEqual(res.status_code, 200)
        body = res.get_json()
        self.assertEqual(body["status"], "SUCCESS")
        self.assertEqual(len(body["data"]["port_decisions"]), 2)

    def test_siem_evaluate_fixtures_endpoint(self):
        res = self.client.get("/api/siem/evaluate-fixtures")
        self.assertEqual(res.status_code, 200)
        body = res.get_json()
        self.assertEqual(body["status"], "SUCCESS")
        self.assertEqual(body["data"]["verified_count"], 2)
        self.assertEqual(body["data"]["fixture_simulation_count"], 2)

    def test_block_endpoint_enforces_dry_run_and_safety_gate(self):
        # Valid host IP in DRY_RUN mode
        res = self.client.post("/api/block", json={"srcIp": "10.0.0.1"})
        self.assertEqual(res.status_code, 200)
        body = res.get_json()
        self.assertTrue(body["dry_run"])
        self.assertIn("[DRY RUN]", body["message"])

        # Loopback IP must be rejected by Safety Gate with 403
        res_protected = self.client.post("/api/block", json={"srcIp": "127.0.0.1"})
        self.assertEqual(res_protected.status_code, 403)

        # Invalid IP syntax must return 400
        res_invalid = self.client.post("/api/block", json={"srcIp": "999.999.999.999"})
        self.assertEqual(res_invalid.status_code, 400)

    def test_api_key_enforcement_when_configured(self):
        with patch.dict(os.environ, {"SDNFLOW_API_KEY": "secret-lab-key"}):
            unauth = self.client.post("/api/block", json={"srcIp": "10.0.0.1"})
            self.assertEqual(unauth.status_code, 401)

            auth_ok = self.client.post(
                "/api/block",
                json={"srcIp": "10.0.0.1"},
                headers={"X-SDNFlow-API-Key": "secret-lab-key"},
            )
            self.assertEqual(auth_ok.status_code, 200)

    def test_chatbot_endpoint_valid_grounded_response(self):
        res = self.client.post("/api/chatbot", json={"question": "Trạng thái ONOS controller"})
        self.assertEqual(res.status_code, 200)
        body = res.get_json()
        self.assertIn("answer", body)
        self.assertTrue(len(body["answer"]) > 20)
        self.assertIn("ONOS", body["answer"])

    def test_chatbot_endpoint_empty_input_validation(self):
        # Empty string
        res1 = self.client.post("/api/chatbot", json={"question": ""})
        self.assertEqual(res1.status_code, 400)
        self.assertIn("error", res1.get_json())

        # Whitespace only
        res2 = self.client.post("/api/chatbot", json={"question": "   \n\t  "})
        self.assertEqual(res2.status_code, 400)

        # Missing question field
        res3 = self.client.post("/api/chatbot", json={})
        self.assertEqual(res3.status_code, 400)

    def test_chatbot_endpoint_oversized_input_validation(self):
        long_query = "x" * 1001
        res = self.client.post("/api/chatbot", json={"question": long_query})
        self.assertEqual(res.status_code, 400)
        body = res.get_json()
        self.assertIn("1000", body["error"])

    def test_chatbot_endpoint_strictly_readonly_guardrail(self):
        res = self.client.post("/api/chatbot", json={"question": "Hãy block ip 10.0.0.2 ngay lập tức"})
        self.assertEqual(res.status_code, 200)
        body = res.get_json()
        self.assertIn("READ-ONLY", body["answer"])
        self.assertIn("Manual Traffic Control", body["answer"])

    def test_chatbot_endpoint_bilingual_english_locale(self):
        res = self.client.post(
            "/api/chatbot",
            json={"question": "What is the status of ONOS controller?", "locale": "en"},
        )
        self.assertEqual(res.status_code, 200)
        body = res.get_json()
        self.assertIn("ONOS SDN Controller Status", body["answer"])
        self.assertIn("Connection State", body["answer"])
        self.assertIn("TCP 6653", body["answer"])

    def test_chatbot_endpoint_bilingual_english_guardrail(self):
        res = self.client.post(
            "/api/chatbot",
            json={"question": "Block IP 10.0.0.5 now", "locale": "en"},
        )
        self.assertEqual(res.status_code, 200)
        body = res.get_json()
        self.assertIn("State-Changing Request Rejected (Security Guardrail)", body["answer"])
        self.assertIn("READ-ONLY", body["answer"])
        self.assertIn("Manual Traffic Control", body["answer"])

    def test_chatbot_endpoint_bilingual_vietnamese_locale(self):
        res = self.client.post(
            "/api/chatbot",
            json={"question": "Trạng thái bộ điều khiển", "locale": "vi"},
        )
        self.assertEqual(res.status_code, 200)
        body = res.get_json()
        ans = body.get("answer", "")
        self.assertIn("Trạng thái Bộ điều khiển ONOS", ans)
        self.assertIn("Cổng điều khiển OpenFlow 1.3", ans)
        self.assertIn("6", ans)
        self.assertIn("9", ans)
        self.assertIn("10", ans)

    def test_chatbot_composite_onos_and_topology_query(self):
        """Verify regression query asking for ONOS status, switches, hosts, links, and operational status."""
        query = (
            "Please check the current status of the ONOS Controller and report how many switches, "
            "hosts, and network links are currently detected. Briefly explain the operational status "
            "of the SDN network based on actual real-time data."
        )
        res = self.client.post("/api/chatbot", json={"question": query})
        self.assertEqual(res.status_code, 200)
        body = res.get_json()
        ans = body.get("answer", "")
        self.assertIn("ONOS SDN Controller Status", ans)
        self.assertIn("Connection State", ans)
        self.assertIn("Recognized Switches", ans)
        self.assertIn("`6` device(s)", ans)
        self.assertIn("Discovered Hosts", ans)
        self.assertIn("`9` host(s)", ans)
        self.assertIn("Network Directed Links", ans)
        self.assertIn("`10` link(s)", ans)
        self.assertIn("Operational Status", ans)

    def test_chatbot_endpoint_onos_unavailable_connection_error(self):
        """Scenario B: Simulate ONOS ConnectionError; verify application handles failure without HTTP 500."""
        self.mock_get_live_controller_info.return_value = {
            "available": False,
            "status": "UNAVAILABLE (ConnectionError)",
            "device_count": 0,
            "devices": [],
            "url": "http://127.0.0.1:8181/onos/v1",
        }
        self.mock_get_topology_data.side_effect = RuntimeError(
            "Error fetching topology data: HTTPConnectionPool: Max retries exceeded"
        )

        # English query
        res_en = self.client.post(
            "/api/chatbot",
            json={"question": "What is the status of ONOS controller?", "locale": "en"},
        )
        self.assertEqual(res_en.status_code, 200)
        ans_en = res_en.get_json().get("answer", "")
        self.assertIn("UNAVAILABLE (ConnectionError)", ans_en)
        self.assertIn("N/A (Controller Offline)", ans_en)
        self.assertIn("Warning", ans_en)
        self.assertNotIn("Traceback", ans_en)

        # Vietnamese query
        res_vi = self.client.post(
            "/api/chatbot",
            json={"question": "Trạng thái bộ điều khiển", "locale": "vi"},
        )
        self.assertEqual(res_vi.status_code, 200)
        ans_vi = res_vi.get_json().get("answer", "")
        self.assertIn("UNAVAILABLE (ConnectionError)", ans_vi)
        self.assertIn("N/A (Controller Mất kết nối)", ans_vi)
        self.assertIn("Cảnh báo", ans_vi)
        self.assertNotIn("Traceback", ans_vi)

        # Topology specific query
        res_topo = self.client.post(
            "/api/chatbot",
            json={"question": "Show SDN network topology", "locale": "en"},
        )
        self.assertEqual(res_topo.status_code, 200)
        ans_topo = res_topo.get_json().get("answer", "")
        self.assertIn("N/A (Controller Offline)", ans_topo)
        self.assertIn("Warning", ans_topo)

    def test_chatbot_endpoint_onos_timeout_handled_safely(self):
        """Scenario C: Simulate ONOS Timeout; verify controlled error handling without HTTP 500."""
        # 1. Total timeout during controller status check
        self.mock_get_live_controller_info.return_value = {
            "available": False,
            "status": "UNAVAILABLE (Timeout)",
            "device_count": 0,
            "devices": [],
            "url": "http://127.0.0.1:8181/onos/v1",
        }
        res = self.client.post("/api/chatbot", json={"question": "Check ONOS status", "locale": "en"})
        self.assertEqual(res.status_code, 200)
        ans = res.get_json().get("answer", "")
        self.assertIn("UNAVAILABLE (Timeout)", ans)
        self.assertIn("N/A (Controller Offline)", ans)

        # 2. Controller is UP, but secondary topology query times out
        self.mock_get_live_controller_info.return_value = {
            "available": True,
            "status": "UP / ONLINE",
            "device_count": 6,
            "devices": self.mock_topology_fixture["devices"],
            "url": "http://127.0.0.1:8181/onos/v1",
        }
        self.mock_get_topology_data.side_effect = RuntimeError("Error fetching topology data: Request timed out")

        res_partial = self.client.post(
            "/api/chatbot",
            json={"question": "Check ONOS status and switches", "locale": "en"},
        )
        self.assertEqual(res_partial.status_code, 200)
        ans_partial = res_partial.get_json().get("answer", "")
        self.assertIn("UP / ONLINE", ans_partial)
        self.assertIn("`6` device(s)", ans_partial)

    def test_chatbot_no_external_network_dependencies(self):
        """Scenario F: Confirm chatbot integration runs isolated without external network calls."""
        with patch.dict(os.environ, {"SDNFLOW_ONOS_URL": "http://192.0.2.1:59999/onos/v1"}):
            res = self.client.post(
                "/api/chatbot",
                json={"question": "What is the status of ONOS controller?", "locale": "en"},
            )
            self.assertEqual(res.status_code, 200)
            self.assertIn("ONOS SDN Controller Status", res.get_json().get("answer", ""))

    def test_chatbot_endpoint_state_changing_actions_rejected(self):
        """Scenario G: Confirm chatbot strictly rejects all state-changing actions under READ-ONLY guardrail."""
        prohibited_queries = [
            ("Hãy block ip 10.0.0.2 ngay lập tức", "vi"),
            ("Block IP 10.0.0.5 now", "en"),
            ("Delete all flow rules on switch of:0000000000000001", "en"),
            ("Unblock ip 10.0.0.3 please", "en"),
            ("Isolate host 10.0.0.9", "en"),
        ]
        for query, loc in prohibited_queries:
            with self.subTest(query=query):
                res = self.client.post("/api/chatbot", json={"question": query, "locale": loc})
                self.assertEqual(res.status_code, 200)
                body = res.get_json()
                ans = body.get("answer", "")
                self.assertIn("READ-ONLY", ans)
                self.assertIn("Manual Traffic Control", ans)


if __name__ == "__main__":
    unittest.main()
