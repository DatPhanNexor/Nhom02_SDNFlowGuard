import sys
import unittest
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from sdnflowguard.domain.models import DefenseMode  # noqa: E402
from sdnflowguard.domain.policies.defense_policy import evaluate_defense_policy  # noqa: E402
from sdnflowguard.domain.policies.safety_gate import evaluate_safety_gate  # noqa: E402


class TestPortAnomalyNeverBlocksIp(unittest.TestCase):
    def test_port_anomaly_without_step64_corroboration_never_proposes_block(self):
        ports = [{"port": "1", "isEnabled": True}]
        hosts = [
            {
                "mac": "00:00:00:00:00:01",
                "ipAddresses": ["10.0.0.1"],
                "locations": [{"elementId": "of:0000000000000001", "port": "1"}],
            }
        ]
        alerts = [
            {
                "switch_id": "of:0000000000000001",
                "port_number": "1",
                "test_only": False,
                "peak_pps": 120.0,
            }
        ]
        reports = evaluate_defense_policy(
            "of:0000000000000001",
            ports,
            hosts,
            [],
            alerts,
            evidence=None,
        )
        self.assertEqual(reports[0]["decision"], "OBSERVE")
        self.assertFalse(reports[0]["source_ip_attributed"])

        verdict = evaluate_safety_gate(
            action_type="block_ip",
            defense_mode=DefenseMode.ACTIVE_ENFORCEMENT.value,
            target_ip="10.0.0.1",
            test_only=False,
            source_ip_attributed=reports[0]["source_ip_attributed"],
            historical_alert_correlation_verified=False,
            manual_operator_override=False,
            operator_approved=True,
            explicit_dry_run=False,
        )
        self.assertFalse(verdict.allowed_to_execute)


if __name__ == "__main__":
    unittest.main()

