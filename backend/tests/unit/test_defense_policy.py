import sys
import unittest
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2]
DEFENSE_DIR = BACKEND_ROOT / "defense"
for p in (str(BACKEND_ROOT), str(DEFENSE_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

import sdn_defense_policy as policy  # noqa: E402


class TestDefensePolicy(unittest.TestCase):
    def test_builtin_self_test_passes(self):
        policy.self_test()

    def test_port_alert_without_verified_source_attribution_only_observes(self):
        ports = [{"port": "1", "isEnabled": True}, {"port": "2", "isEnabled": True}]
        hosts = [
            {
                "mac": "00:00:00:00:00:01",
                "ipAddresses": ["10.0.0.1"],
                "locations": [{"elementId": policy.DEVICE_ID, "port": "1"}],
            }
        ]
        alerts = [
            {
                "switch_id": policy.DEVICE_ID,
                "port_number": "1",
                "test_only": False,
                "peak_pps": 55.0,
            }
        ]
        reports = policy.evaluate_policy(policy.DEVICE_ID, ports, hosts, [], alerts)
        self.assertEqual(reports[0]["decision"], "OBSERVE")
        self.assertFalse(reports[0]["source_ip_attributed"])
        self.assertEqual(reports[1]["decision"], "ALLOW")


if __name__ == "__main__":
    unittest.main()

