import unittest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from sdnflowguard.domain.policies.safety_gate import (
    is_protected_ip,
    DEFAULT_PROTECTED_IPS,
    evaluate_safety_gate,
)
from app.controller_actions import rate_limit_for_host
from app import database
import run


class TestRemediationFindings(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.temp_db = Path(self._tmpdir.name) / "test_remediation.db"
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

        self.app = run.app
        self.client = self.app.test_client()

    def tearDown(self):
        self._env_patcher.stop()
        self._tmpdir.cleanup()

    def test_finding_05_gateway_and_dns_protected_by_default(self):
        """Verify Gateway 10.0.0.254 and DNS 8.8.8.8/1.1.1.1 are protected by default (Finding-05)."""
        self.assertIn("10.0.0.254", DEFAULT_PROTECTED_IPS)
        self.assertIn("8.8.8.8", DEFAULT_PROTECTED_IPS)
        self.assertIn("1.1.1.1", DEFAULT_PROTECTED_IPS)

        for ip in ("10.0.0.254", "8.8.8.8", "1.1.1.1"):
            protected, reason = is_protected_ip(ip)
            self.assertTrue(protected, f"Expected {ip} to be protected by default")
            self.assertIn("protected infrastructure allowlist", reason)

    def test_finding_03_rate_limit_unit_conversion_bps_to_kb_per_sec(self):
        """Verify rate limit converts bps to kbps (KB_PER_SEC) for ONOS Meter.Unit (Finding-03).
        In ONOS Meter.Unit and OpenFlow 1.3 OFPMC_KBPS, KB_PER_SEC denotes kilobits/sec (1 kbps = 1000 bps).
        """
        # Test 80,000 bps -> 80 kbps (KB_PER_SEC)
        res_80k = rate_limit_for_host("10.0.0.1", 80000, dry_run=True)
        self.assertEqual(res_80k["status"], "DRY_RUN_SIMULATED")
        self.assertEqual(res_80k["rate_limit_bps"], 80000)
        self.assertEqual(res_80k["rate_kb_per_sec"], 80)

        # Test 50,000 bps -> 50 kbps (KB_PER_SEC)
        res_50k = rate_limit_for_host("10.0.0.1", 50000, dry_run=True)
        self.assertEqual(res_50k["rate_limit_bps"], 50000)
        self.assertEqual(res_50k["rate_kb_per_sec"], 50)

        # Test lower bound (minimum 1 kbps)
        res_low = rate_limit_for_host("10.0.0.1", 100, dry_run=True)
        self.assertEqual(res_low["rate_kb_per_sec"], 1)

    def test_rate_limit_edge_cases_validation(self):
        """Verify zero, negative, and invalid non-numeric inputs are rejected by rate limiting."""
        # Zero rate
        res_zero = rate_limit_for_host("10.0.0.1", 0, dry_run=True)
        self.assertEqual(res_zero["status"], "VALIDATION_ERROR")

        # Negative rate
        res_neg = rate_limit_for_host("10.0.0.1", -5000, dry_run=True)
        self.assertEqual(res_neg["status"], "VALIDATION_ERROR")

        # Invalid non-numeric rate
        res_inv = rate_limit_for_host("10.0.0.1", "invalid_rate", dry_run=True)
        self.assertEqual(res_inv["status"], "VALIDATION_ERROR")

    def test_finding_04_rollback_api_status_transparency(self):
        """Verify rollback API distinguishes simulation from real execution (Finding-04)."""
        # 1. In DRY_RUN: returns ROLLBACK_SIMULATED with dry_run=True, executed=False
        res_dry = self.client.post("/api/defense/rollback", json={"srcIp": "10.0.0.1", "dry_run": True})
        self.assertEqual(res_dry.status_code, 200)
        data_dry = res_dry.get_json()
        self.assertEqual(data_dry["status"], "ROLLBACK_SIMULATED")
        self.assertTrue(data_dry["dry_run"])
        self.assertFalse(data_dry["executed"])

        # 2. In LIVE mode: if no ACL rule exists, returns ROLLBACK_SKIPPED_NO_RULE with executed=False
        res_live = self.client.post("/api/defense/rollback", json={"srcIp": "10.0.0.99", "dry_run": False})
        self.assertEqual(res_live.status_code, 200)
        data_live = res_live.get_json()
        self.assertIn(data_live["status"], ("ROLLBACK_SKIPPED_NO_RULE", "ROLLBACK_COMPLETED", "ROLLBACK_SIMULATED"))
        self.assertFalse(data_live["executed"])

    def test_database_connection_lifecycle_closes_cleanly(self):
        """Verify database.get_connection closes the SQLite connection explicitly."""
        captured_conn = None
        with database.get_connection() as conn:
            captured_conn = conn
            cursor = conn.cursor()
            cursor.execute("SELECT 1;")
            self.assertEqual(cursor.fetchone()[0], 1)

        # Upon exiting context manager, connection must be closed
        with self.assertRaises(Exception):
            captured_conn.execute("SELECT 1;")

    def test_safety_gate_backend_defense_mode_cannot_be_bypassed_by_client(self):
        """Verify client cannot force live execution when backend policy is DRY_RUN."""
        verdict = evaluate_safety_gate(
            action_type="block_ip",
            defense_mode="DRY_RUN",
            target_ip="10.0.0.99",
            explicit_dry_run=False,  # Client tries to force live execution
        )
        self.assertTrue(verdict.dry_run)
        self.assertFalse(verdict.allowed_to_execute)


if __name__ == "__main__":
    unittest.main()
