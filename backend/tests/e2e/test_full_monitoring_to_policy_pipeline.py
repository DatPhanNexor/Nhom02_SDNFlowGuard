import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

BACKEND_ROOT = Path(__file__).resolve().parents[2]
APP_DIR = BACKEND_ROOT / "app"
COLLECTORS_DIR = BACKEND_ROOT / "collectors"
DEFENSE_DIR = BACKEND_ROOT / "defense"
for p in (str(BACKEND_ROOT), str(APP_DIR), str(COLLECTORS_DIR), str(DEFENSE_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from app import database  # noqa: E402
import onos_host_evidence_correlator as correlator  # noqa: E402
import run as flask_run  # noqa: E402
import sdn_defense_policy as defense_policy  # noqa: E402
import sdn_port_anomaly_detector as detector  # noqa: E402
import source_ip_evidence_analyzer as evidence_analyzer  # noqa: E402


class TestFullMonitoringToPolicyPipeline(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.temp_db = Path(self._tmpdir.name) / "test_e2e.db"
        self._env_patcher = patch.dict(
            os.environ,
            {
                "SDNFLOW_DB_PATH": str(self.temp_db),
                "SDNFLOW_DEFENSE_MODE": "DRY_RUN",
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

    def test_end_to_end_pipeline_from_samples_to_step64_and_rollback(self):
        # 1. Detect port anomaly from synthetic port counter samples
        samples = [
            {
                "@timestamp": "2026-11-01T18:46:46Z",
                "switch_id": "of:0000000000000001",
                "port_number": "1",
                "rx_pps": 10.15,
                "tx_pps": 1.0,
                "rx_mbps": 0.01,
                "tx_mbps": 0.001,
                "sample_seconds": 5.0,
            },
            {
                "@timestamp": "2026-11-01T18:46:50Z",
                "switch_id": "of:0000000000000001",
                "port_number": "1",
                "rx_pps": 10.25,
                "tx_pps": 1.0,
                "rx_mbps": 0.01,
                "tx_mbps": 0.001,
                "sample_seconds": 5.0,
            },
        ]
        _, anomalies = detector.analyze(
            samples,
            threshold=4.0,
            consecutive=2,
        )
        self.assertEqual(len(anomalies), 1)

        # 2. Analyze Step 63 switch ingress packet capture
        capture_file = DEFENSE_DIR / "evidence" / "ingress_icmp_20261101_014645.txt"
        step63_evidence = evidence_analyzer.analyze(
            evidence_analyzer.read_capture(capture_file)
        )
        self.assertEqual(step63_evidence["total_packets"], 24)

        # 3. Correlate Step 63 packet observations with ONOS topology (Step 64)
        step64_report = correlator.correlate_step63_evidence_file()
        self.assertTrue(step64_report["security_assessment"]["topology_corroborated"])
        self.assertEqual(step64_report["security_assessment"]["decision"], "OBSERVE")

        # 4. Evaluate Defense Policy Engine across ports
        topo = correlator.DEFAULT_LAB_TOPOLOGY
        alert_record = {
            "switch_id": "of:0000000000000001",
            "port_number": "1",
            "test_only": True,
            "peak_pps": anomalies[0]["peak_pps"],
        }
        decisions = defense_policy.evaluate_policy(
            "of:0000000000000001",
            topo["ports"],
            topo["hosts"],
            topo["flows"],
            [alert_record],
            evidence=step63_evidence,
        )
        self.assertEqual(decisions[0]["decision"], "OBSERVE")
        self.assertEqual(decisions[1]["decision"], "ALLOW")

        # 5. Simulate operator DRY_RUN block and subsequent rollback via Flask API
        block_res = self.client.post("/api/block", json={"srcIp": "10.0.0.1", "dry_run": True})
        self.assertEqual(block_res.status_code, 200)
        self.assertTrue(block_res.get_json()["dry_run"])

        rollback_res = self.client.post(
            "/api/defense/rollback",
            json={"srcIp": "10.0.0.1", "dry_run": True},
        )
        self.assertEqual(rollback_res.status_code, 200)
        self.assertEqual(rollback_res.get_json()["status"], "ROLLBACK_SIMULATED")


if __name__ == "__main__":
    unittest.main()

