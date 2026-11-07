import sys
import unittest
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from sdnflowguard.domain.services.siem_log_normalizer import (  # noqa: E402
    evaluate_siem_capabilities,
    normalize_firewall_log,
    normalize_windows_event_log,
)


class TestSiemLogNormalizer(unittest.TestCase):
    def test_firewall_syslog_normalization_tags_fixture_simulation(self):
        raw = "2026-11-05T01:15:00Z fw01 kernel: Action=DROP Proto=TCP Src=10.0.0.1 Dst=10.0.0.2 Spt=51422 Dpt=22"
        norm = normalize_firewall_log(raw)
        self.assertEqual(norm["source_system"], "FIREWALL")
        self.assertEqual(norm["integration_status"], "FIXTURE_SIMULATION")
        self.assertEqual(norm["source_ip"], "10.0.0.1")
        self.assertFalse(norm["automatic_block_allowed"])

    def test_windows_event_log_normalization_tags_fixture_simulation(self):
        raw = {
            "@timestamp": "2026-11-05T01:16:00Z",
            "EventID": 4625,
            "Computer": "WIN-DC01.sdn.lab",
            "TargetUserName": "Administrator",
            "IpAddress": "10.0.0.1",
            "DestAddress": "10.0.0.2",
        }
        norm = normalize_windows_event_log(raw)
        self.assertEqual(norm["source_system"], "WINDOWS_SERVER")
        self.assertEqual(norm["integration_status"], "FIXTURE_SIMULATION")
        self.assertEqual(norm["event_id"], 4625)
        self.assertFalse(norm["automatic_block_allowed"])

    def test_evaluate_siem_capabilities_distinguishes_verified_and_simulated(self):
        matrix = evaluate_siem_capabilities()
        self.assertEqual(matrix["verified_count"], 2)
        self.assertEqual(matrix["fixture_simulation_count"], 2)


if __name__ == "__main__":
    unittest.main()

