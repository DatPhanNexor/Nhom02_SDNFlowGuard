import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys
import requests

BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app import topology
import run


class TestTopologyService(unittest.TestCase):
    """Unit tests for SDN topology data fetching and API mapping."""

    def setUp(self):
        self.app = run.app
        self.client = self.app.test_client()

    @patch("app.topology.requests.get")
    def test_empty_topology(self, mock_get):
        """Verify empty topology when ONOS has no connected devices, hosts, or links."""
        def side_effect(url, **kwargs):
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            if "/devices" in url:
                mock_resp.json.return_value = {"devices": []}
            elif "/hosts" in url:
                mock_resp.json.return_value = {"hosts": []}
            elif "/links" in url:
                mock_resp.json.return_value = {"links": []}
            return mock_resp

        mock_get.side_effect = side_effect
        data = topology.get_topology_data()
        self.assertEqual(data["devices"], [])
        self.assertEqual(data["hosts"], [])
        self.assertEqual(data["links"], [])

    @patch("app.topology.requests.get")
    def test_single_switch_three_hosts(self, mock_get):
        """Verify topology with single switch of:0000000000000001 and 3 hosts (Scenario A)."""
        def side_effect(url, **kwargs):
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            if "/devices" in url:
                mock_resp.json.return_value = {
                    "devices": [
                        {
                            "id": "of:0000000000000001",
                            "type": "SWITCH",
                            "available": True,
                            "role": "MASTER",
                            "hw": "Open vSwitch",
                            "sw": "3.7.1",
                            "annotations": {"protocol": "OF_13", "datapathDescription": "s1"},
                        }
                    ]
                }
            elif "/hosts" in url:
                mock_resp.json.return_value = {
                    "hosts": [
                        {
                            "id": "00:00:00:00:00:01/None",
                            "mac": "00:00:00:00:00:01",
                            "ipAddresses": ["10.0.0.1"],
                            "locations": [{"elementId": "of:0000000000000001", "port": "1"}],
                        },
                        {
                            "id": "00:00:00:00:00:02/None",
                            "mac": "00:00:00:00:00:02",
                            "ipAddresses": ["10.0.0.2"],
                            "locations": [{"elementId": "of:0000000000000001", "port": "2"}],
                        },
                        {
                            "id": "00:00:00:00:00:03/None",
                            "mac": "00:00:00:00:00:03",
                            "ipAddresses": ["10.0.0.3"],
                            "locations": [{"elementId": "of:0000000000000001", "port": "3"}],
                        },
                    ]
                }
            elif "/links" in url:
                mock_resp.json.return_value = {"links": []}
            return mock_resp

        mock_get.side_effect = side_effect
        data = topology.get_topology_data()
        self.assertEqual(len(data["devices"]), 1)
        self.assertTrue(data["devices"][0]["available"])
        self.assertEqual(len(data["hosts"]), 3)
        self.assertEqual(data["hosts"][0]["ipAddresses"], ["10.0.0.1"])
        self.assertEqual(data["links"], [])

    @patch("app.topology.requests.get")
    def test_multiple_switches_linear_topology(self, mock_get):
        """Verify multi-switch linear topology with 3 switches, 6 hosts, and inter-switch links."""
        def side_effect(url, **kwargs):
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            if "/devices" in url:
                mock_resp.json.return_value = {
                    "devices": [
                        {"id": f"of:000000000000000{i}", "available": True, "type": "SWITCH"}
                        for i in range(1, 4)
                    ]
                }
            elif "/hosts" in url:
                mock_resp.json.return_value = {
                    "hosts": [
                        {
                            "id": f"00:00:00:00:00:0{i}/None",
                            "mac": f"00:00:00:00:00:0{i}",
                            "ipAddresses": [f"10.0.0.{i}"],
                            "locations": [{"elementId": f"of:000000000000000{(i+1)//2}", "port": "1"}],
                        }
                        for i in range(1, 7)
                    ]
                }
            elif "/links" in url:
                mock_resp.json.return_value = {
                    "links": [
                        {"src": {"device": "of:0000000000000001", "port": "2"}, "dst": {"device": "of:0000000000000002", "port": "1"}, "state": "ACTIVE"},
                        {"src": {"device": "of:0000000000000002", "port": "1"}, "dst": {"device": "of:0000000000000001", "port": "2"}, "state": "ACTIVE"},
                        {"src": {"device": "of:0000000000000002", "port": "2"}, "dst": {"device": "of:0000000000000003", "port": "1"}, "state": "ACTIVE"},
                        {"src": {"device": "of:0000000000000003", "port": "1"}, "dst": {"device": "of:0000000000000002", "port": "2"}, "state": "ACTIVE"},
                    ]
                }
            return mock_resp

        mock_get.side_effect = side_effect
        data = topology.get_topology_data()
        self.assertEqual(len(data["devices"]), 3)
        self.assertEqual(len(data["hosts"]), 6)
        self.assertEqual(len(data["links"]), 4)

    @patch("app.topology.requests.get")
    def test_host_joins_and_leaves(self, mock_get):
        """Verify dynamic host state transitions when host joins and leaves network."""
        # Initial: switch online, no hosts
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "devices": [{"id": "of:0000000000000001", "available": True}],
            "hosts": [],
            "links": [],
        }
        mock_get.return_value = mock_resp
        d1 = topology.get_topology_data()
        self.assertEqual(len(d1["hosts"]), 0)

        # Host joins: ONOS registers host
        mock_resp.json.return_value = {
            "devices": [{"id": "of:0000000000000001", "available": True}],
            "hosts": [{"id": "00:00:00:00:00:01/None", "ipAddresses": ["10.0.0.1"]}],
            "links": [],
        }
        d2 = topology.get_topology_data()
        self.assertEqual(len(d2["hosts"]), 1)
        self.assertEqual(d2["hosts"][0]["ipAddresses"], ["10.0.0.1"])

        # Host leaves: host list returns empty
        mock_resp.json.return_value = {
            "devices": [{"id": "of:0000000000000001", "available": True}],
            "hosts": [],
            "links": [],
        }
        d3 = topology.get_topology_data()
        self.assertEqual(len(d3["hosts"]), 0)

    @patch("app.topology.requests.get", side_effect=requests.exceptions.ConnectionError("ONOS down"))
    def test_onos_unavailable_handled_safely(self, mock_get):
        """Verify that when ONOS is unavailable, /api/topology returns controlled 502 without crashing."""
        res = self.client.get("/api/topology")
        self.assertEqual(res.status_code, 502)
        payload = res.get_json()
        self.assertEqual(payload.get("controller_status"), "UNAVAILABLE")
        self.assertEqual(payload.get("devices"), [])
        self.assertEqual(payload.get("hosts"), [])
        self.assertEqual(payload.get("links"), [])

    @patch("app.topology.requests.get")
    def test_stale_and_malformed_fields_handled_gracefully(self, mock_get):
        """Verify topology parser handles missing or malformed fields safely."""
        def side_effect(url, **kwargs):
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            if "/devices" in url:
                # Device without annotations, available=False
                mock_resp.json.return_value = {
                    "devices": [{"id": "of:0000000000000001", "available": False}]
                }
            elif "/hosts" in url:
                # Host with null ipAddresses and null locations
                mock_resp.json.return_value = {
                    "hosts": [{"id": "00:00:00:00:00:99/None", "mac": "00:00:00:00:00:99"}]
                }
            elif "/links" in url:
                mock_resp.json.return_value = {"links": [{"src": None, "dst": None}]}
            return mock_resp

        mock_get.side_effect = side_effect
        data = topology.get_topology_data()
        self.assertEqual(len(data["devices"]), 1)
        self.assertFalse(data["devices"][0]["available"])
        self.assertEqual(data["devices"][0]["annotations"], {})
        self.assertEqual(data["hosts"][0]["ipAddresses"], [])
        self.assertEqual(data["hosts"][0]["locations"], [])
        self.assertIsNone(data["links"][0]["src"])


if __name__ == "__main__":
    unittest.main()
