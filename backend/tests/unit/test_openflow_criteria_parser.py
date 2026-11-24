import unittest
from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.flow_parser import parse_onos_flow


class TestOpenFlowCriteriaParser(unittest.TestCase):
    """Phase E: Rigorous regression testing for OpenFlow 1.3 match criteria parser."""

    def test_01_flow_rule_full_ipv4_source_and_destination(self):
        """1. Flow rule contains full IPv4 source and destination (preserves CIDR prefix)."""
        raw = {
            "id": "1001",
            "deviceId": "of:0000000000000001",
            "appId": "org.onosproject.acl",
            "priority": 50000,
            "tableId": 0,
            "state": "ADDED",
            "selector": {
                "criteria": [
                    {"type": "ETH_TYPE", "ethType": "0x800"},
                    {"type": "IPV4_SRC", "ip": "10.0.0.1/32"},
                    {"type": "IPV4_DST", "ip": "10.0.0.2/32"},
                    {"type": "IP_PROTO", "protocol": 6},
                    {"type": "TCP_DST", "tcpPort": 80},
                ]
            },
            "treatment": {
                "instructions": [{"type": "OUTPUT", "port": "2"}]
            },
            "packets": 120,
            "bytes": 9600,
            "life": 45,
        }
        parsed = parse_onos_flow(raw)
        self.assertEqual(parsed["source_ip"], "10.0.0.1/32")
        self.assertEqual(parsed["destination_ip"], "10.0.0.2/32")
        self.assertTrue(parsed["has_ip_match"])
        self.assertFalse(parsed["is_table_miss"])
        self.assertIn("SRC_IP: 10.0.0.1/32", parsed["match_criteria"])
        self.assertIn("DST_IP: 10.0.0.2/32", parsed["match_criteria"])
        self.assertIn("TCP: *:80", parsed["match_criteria"])
        self.assertEqual(parsed["output_ports"], ["2"])
        self.assertEqual(parsed["treatment_summary"], "OUTPUT: 2")

    def test_02_flow_rule_source_ip_only(self):
        """2. Flow rule contains only Source IP."""
        raw = {
            "id": "1002",
            "deviceId": "of:0000000000000002",
            "appId": "org.onosproject.acl",
            "priority": 40000,
            "tableId": 0,
            "selector": {
                "criteria": [
                    {"type": "ETH_TYPE", "ethType": "0x800"},
                    {"type": "IPV4_SRC", "ip": "10.0.0.5/32"},
                ]
            },
            "treatment": {"instructions": []},
        }
        parsed = parse_onos_flow(raw)
        self.assertEqual(parsed["source_ip"], "10.0.0.5/32")
        self.assertIsNone(parsed["destination_ip"])
        self.assertTrue(parsed["has_ip_match"])
        self.assertEqual(parsed["treatment_summary"], "DROP")

    def test_03_flow_rule_destination_ip_only(self):
        """3. Flow rule contains only Destination IP."""
        raw = {
            "id": "1003",
            "deviceId": "of:0000000000000002",
            "appId": "org.onosproject.fwd",
            "priority": 10,
            "tableId": 0,
            "selector": {
                "criteria": [
                    {"type": "ETH_TYPE", "ethType": "0x800"},
                    {"type": "IPV4_DST", "ip": "10.0.0.9/32"},
                ]
            },
            "treatment": {
                "instructions": [{"type": "OUTPUT", "port": "3"}]
            },
        }
        parsed = parse_onos_flow(raw)
        self.assertIsNone(parsed["source_ip"])
        self.assertEqual(parsed["destination_ip"], "10.0.0.9/32")
        self.assertTrue(parsed["has_ip_match"])

    def test_04_flow_rule_mac_only(self):
        """4. Flow rule has MAC selector only (ETH_SRC, ETH_DST) - NEVER converted to IP."""
        raw = {
            "id": "1004",
            "deviceId": "of:0000000000000001",
            "appId": "org.onosproject.fwd",
            "priority": 10,
            "selector": {
                "criteria": [
                    {"type": "ETH_SRC", "mac": "00:00:00:00:00:01"},
                    {"type": "ETH_DST", "mac": "00:00:00:00:00:02"},
                ]
            },
            "treatment": {
                "instructions": [{"type": "OUTPUT", "port": "1"}]
            },
        }
        parsed = parse_onos_flow(raw)
        # CRITICAL: MAC addresses must NEVER be assigned to source_ip or destination_ip!
        self.assertIsNone(parsed["source_ip"])
        self.assertIsNone(parsed["destination_ip"])
        self.assertFalse(parsed["has_ip_match"])
        self.assertEqual(parsed["source_mac"], "00:00:00:00:00:01")
        self.assertEqual(parsed["destination_mac"], "00:00:00:00:00:02")
        self.assertIn("ETH_SRC: 00:00:00:00:00:01", parsed["match_criteria"])
        self.assertIn("ETH_DST: 00:00:00:00:00:02", parsed["match_criteria"])

    def test_05_flow_rule_eth_type_or_in_port_only(self):
        """5. Flow rule has only ETH_TYPE or IN_PORT (Core ONOS rule pattern)."""
        raw = {
            "id": "1005",
            "deviceId": "of:0000000000000003",
            "appId": "org.onosproject.core",
            "priority": 40000,
            "selector": {
                "criteria": [
                    {"type": "IN_PORT", "port": "1"},
                    {"type": "ETH_TYPE", "ethType": "0x806"},
                ]
            },
            "treatment": {
                "instructions": [{"type": "OUTPUT", "port": "CONTROLLER"}]
            },
        }
        parsed = parse_onos_flow(raw)
        self.assertIsNone(parsed["source_ip"])
        self.assertIsNone(parsed["destination_ip"])
        self.assertFalse(parsed["has_ip_match"])
        self.assertEqual(parsed["in_port"], "1")
        self.assertEqual(parsed["eth_type"], "0x806")
        self.assertIn("IN_PORT: 1", parsed["match_criteria"])
        self.assertIn("ETH_TYPE: 0x806 (ARP)", parsed["match_criteria"])
        self.assertEqual(parsed["output_ports"], ["CONTROLLER"])

    def test_06_flow_rule_empty_selector_wildcard(self):
        """6. Flow rule has empty selector (Wildcard / Match All)."""
        raw = {
            "id": "1006",
            "deviceId": "of:0000000000000001",
            "appId": "org.onosproject.core",
            "priority": 0,
            "tableId": 0,
            "selector": {"criteria": []},
            "treatment": {"instructions": []},
        }
        parsed = parse_onos_flow(raw)
        self.assertIsNone(parsed["source_ip"])
        self.assertIsNone(parsed["destination_ip"])
        self.assertFalse(parsed["has_ip_match"])
        self.assertTrue(parsed["is_table_miss"])
        self.assertEqual(parsed["match_criteria"], "WILDCARD (Match All)")
        self.assertEqual(parsed["treatment_summary"], "DROP")

    def test_07_flow_rule_ipv6(self):
        """7. Flow rule IPv6 (IPV6_SRC, IPV6_DST, ethType 0x86dd)."""
        raw = {
            "id": "1007",
            "deviceId": "of:0000000000000004",
            "appId": "org.onosproject.fwd",
            "priority": 100,
            "selector": {
                "criteria": [
                    {"type": "ETH_TYPE", "ethType": "0x86dd"},
                    {"type": "IPV6_SRC", "ip": "fe80::1/128"},
                    {"type": "IPV6_DST", "ip": "fe80::2/128"},
                ]
            },
            "treatment": {
                "instructions": [{"type": "OUTPUT", "port": "4"}]
            },
        }
        parsed = parse_onos_flow(raw)
        self.assertEqual(parsed["source_ip"], "fe80::1/128")
        self.assertEqual(parsed["destination_ip"], "fe80::2/128")
        self.assertTrue(parsed["has_ip_match"])
        self.assertIn("SRC_IP: fe80::1/128", parsed["match_criteria"])
        self.assertIn("DST_IP: fe80::2/128", parsed["match_criteria"])

    def test_08_treatment_output_controller(self):
        """10. Flow rule with Treatment OUTPUT CONTROLLER."""
        raw = {
            "id": "1010",
            "deviceId": "of:0000000000000005",
            "appId": "org.onosproject.core",
            "priority": 5,
            "selector": {
                "criteria": [{"type": "ETH_TYPE", "ethType": "0x800"}]
            },
            "treatment": {
                "instructions": [{"type": "OUTPUT", "port": "CONTROLLER"}]
            },
        }
        parsed = parse_onos_flow(raw)
        self.assertEqual(parsed["output_ports"], ["CONTROLLER"])
        self.assertEqual(parsed["treatment_summary"], "OUTPUT: CONTROLLER")

    def test_09_malformed_and_missing_fields_handled_gracefully(self):
        """9. Backend receives missing, None, or malformed fields safely."""
        self.assertEqual(parse_onos_flow(None)["match_criteria"], "WILDCARD (Match All)")
        self.assertEqual(parse_onos_flow({})["id"], "")
        self.assertEqual(parse_onos_flow({"selector": "bad_type"})["source_ip"], None)
        self.assertEqual(parse_onos_flow({"treatment": "bad_type"})["treatment_summary"], "DROP")


if __name__ == "__main__":
    unittest.main()
