import sys
import unittest
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from sdnflowguard.domain.models import DefenseLifecycleState, DefenseMode  # noqa: E402
from sdnflowguard.domain.policies.safety_gate import (  # noqa: E402
    evaluate_safety_gate,
    is_protected_ip,
)


class TestSafetyGate(unittest.TestCase):
    def test_protected_ips_are_rejected(self):
        for ip in ("127.0.0.1", "::1", "0.0.0.0", "255.255.255.255", "224.0.0.1", "invalid_ip"):
            protected, reason = is_protected_ip(ip)
            self.assertTrue(protected, f"Expected {ip} to be protected")
            self.assertIsNotNone(reason)

    def test_cidr_covering_gateway_is_rejected(self):
        for cidr in ("10.0.0.0/8", "10.0.0.0/24", "10.0.0.254/32", "10.0.0.254"):
            protected, reason = is_protected_ip(cidr)
            self.assertTrue(protected, f"Expected CIDR {cidr} covering gateway to be protected")
            self.assertIn("10.0.0.254", reason or "")

    def test_cidr_covering_dns_is_rejected(self):
        for cidr in ("8.8.8.0/24", "8.8.8.8/32", "1.1.1.0/24", "1.1.1.1/32"):
            protected, reason = is_protected_ip(cidr)
            self.assertTrue(protected, f"Expected CIDR {cidr} covering DNS to be protected")
            self.assertIsNotNone(reason)

    def test_valid_host_ip_allowed_to_block(self):
        for host in ("10.0.0.1", "10.0.0.1/32", "10.0.0.2", "192.168.1.50/32", "172.16.0.5/32"):
            protected, reason = is_protected_ip(host)
            self.assertFalse(protected, f"Expected legitimate host {host} not to be protected, got: {reason}")
            self.assertIsNone(reason)

    def test_multicast_loopback_unspecified_default_route_rejected(self):
        for net in ("0.0.0.0/0", "127.0.0.0/8", "224.0.0.0/4", "255.255.255.255", "255.255.255.255/32"):
            protected, reason = is_protected_ip(net)
            self.assertTrue(protected, f"Expected route/special space {net} to be rejected")

    def test_dual_ip_rule_rejects_if_either_endpoint_is_protected(self):
        # Case A: src is safe, but dst is gateway
        verdict_a = evaluate_safety_gate(
            action_type="block_ip",
            target_ip="10.0.0.1/32",
            dst_ip="10.0.0.254/32",
        )
        self.assertFalse(verdict_a.safety_checks["valid_and_unprotected_target"])
        self.assertTrue(any("Destination IP check failed" in r for r in verdict_a.rejection_reasons))

        # Case B: src is gateway, dst is safe
        verdict_b = evaluate_safety_gate(
            action_type="block_ip",
            target_ip="10.0.0.254/32",
            dst_ip="10.0.0.1/32",
        )
        self.assertFalse(verdict_b.safety_checks["valid_and_unprotected_target"])
        self.assertTrue(any("Target IP check failed" in r for r in verdict_b.rejection_reasons))

        # Case C: both endpoints safe
        verdict_c = evaluate_safety_gate(
            action_type="block_ip",
            target_ip="10.0.0.1/32",
            dst_ip="10.0.0.2/32",
        )
        self.assertTrue(verdict_c.safety_checks["valid_and_unprotected_target"])

    def test_unauthenticated_client_cannot_force_operator_approval(self):
        # Client attempts to spoof manual override without verified authentication
        verdict_unauth = evaluate_safety_gate(
            action_type="block_ip",
            defense_mode=DefenseMode.MANUAL_APPROVAL.value,
            target_ip="10.0.0.1",
            manual_operator_override=True,
            operator_approved=True,
            operator_authenticated=False,
            explicit_dry_run=False,
        )
        self.assertFalse(verdict_unauth.safety_checks["operator_approval_satisfied"])
        self.assertFalse(verdict_unauth.safety_checks["evidence_attribution_satisfied"])
        self.assertFalse(verdict_unauth.allowed_to_execute)

        # Authenticated operator in MANUAL_APPROVAL mode
        verdict_auth = evaluate_safety_gate(
            action_type="block_ip",
            defense_mode=DefenseMode.MANUAL_APPROVAL.value,
            target_ip="10.0.0.1",
            manual_operator_override=True,
            operator_approved=True,
            operator_authenticated=True,
            explicit_dry_run=False,
        )
        self.assertTrue(verdict_auth.safety_checks["operator_approval_satisfied"])
        self.assertTrue(verdict_auth.safety_checks["evidence_attribution_satisfied"])
        self.assertTrue(verdict_auth.allowed_to_execute)

    def test_dry_run_mode_stages_proposal_without_allowing_execution(self):
        verdict = evaluate_safety_gate(
            action_type="block_ip",
            defense_mode=DefenseMode.DRY_RUN.value,
            target_ip="10.0.0.1",
            manual_operator_override=True,
            operator_approved=True,
            operator_authenticated=True,
        )
        self.assertFalse(verdict.allowed_to_execute)
        self.assertTrue(verdict.dry_run)
        self.assertEqual(verdict.lifecycle_state, DefenseLifecycleState.BLOCK_PROPOSED.value)

    def test_active_enforcement_with_corroborated_evidence_is_approved(self):
        verdict = evaluate_safety_gate(
            action_type="block_ip",
            defense_mode=DefenseMode.ACTIVE_ENFORCEMENT.value,
            target_ip="10.0.0.1",
            test_only=False,
            source_ip_attributed=True,
            historical_alert_correlation_verified=True,
            manual_operator_override=False,
            operator_approved=True,
            explicit_dry_run=False,
        )
        self.assertTrue(verdict.allowed_to_execute)
        self.assertFalse(verdict.dry_run)
        self.assertEqual(verdict.lifecycle_state, DefenseLifecycleState.BLOCK_APPROVED.value)


if __name__ == "__main__":
    unittest.main()
