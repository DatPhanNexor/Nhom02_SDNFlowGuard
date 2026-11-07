import sys
import unittest
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from sdnflowguard.domain.models import DefenseMode  # noqa: E402
from sdnflowguard.domain.policies.safety_gate import evaluate_safety_gate  # noqa: E402


class TestTestAlertNeverBlocks(unittest.TestCase):
    def test_test_only_alert_is_rejected_even_in_active_enforcement_mode(self):
        verdict = evaluate_safety_gate(
            action_type="block_ip",
            defense_mode=DefenseMode.ACTIVE_ENFORCEMENT.value,
            target_ip="10.0.0.1",
            test_only=True,
            source_ip_attributed=True,
            historical_alert_correlation_verified=True,
            manual_operator_override=True,
            operator_approved=True,
            explicit_dry_run=False,
        )
        self.assertFalse(verdict.allowed_to_execute)
        self.assertFalse(verdict.safety_checks["not_test_only_alert"])


if __name__ == "__main__":
    unittest.main()

