import sys
import unittest
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2]
DEFENSE_DIR = BACKEND_ROOT / "defense"
for p in (str(BACKEND_ROOT), str(DEFENSE_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

import onos_host_evidence_correlator as correlator  # noqa: E402
from sdnflowguard.domain.models import CorrelationStatus  # noqa: E402
from sdnflowguard.domain.services.evidence_correlation import (  # noqa: E402
    correlate_evidence_with_onos,
)


class TestOnosHostEvidenceCorrelator(unittest.TestCase):
    def test_builtin_self_test_passes(self):
        correlator.self_test()

    def test_step63_evidence_file_correlates_against_reference_topology(self):
        report = correlator.correlate_step63_evidence_file()
        self.assertEqual(report["total_packets"], 24)
        self.assertTrue(report["security_assessment"]["topology_corroborated"])
        self.assertFalse(report["security_assessment"]["historical_alert_correlation_verified"])
        self.assertFalse(report["security_assessment"]["attacker_confirmed"])
        self.assertEqual(report["security_assessment"]["decision"], "OBSERVE")
        self.assertFalse(report["security_assessment"]["automatic_block_allowed"])

    def test_unregistered_host_on_port_detected(self):
        evidence = {
            "capture_clock_has_date": False,
            "capture_clock_has_timezone": False,
            "observations": [
                {
                    "switch_id": "of:0000000000000001",
                    "ingress_port": "1",
                    "interface": "s1-eth1",
                    "observed_source_mac": "00:00:00:00:00:01",
                    "observed_source_ip": "10.0.0.1",
                    "observed_destination_ip": "10.0.0.2",
                    "protocol": "ICMP",
                    "icmp_type": "request",
                    "packet_count": 5,
                }
            ],
        }
        report = correlate_evidence_with_onos(
            evidence,
            ports=[{"port": "1", "isEnabled": True}],
            hosts=[],
            flows=[],
        )
        obs = report["correlated_observations"][0]
        self.assertEqual(
            obs["correlation_status"],
            CorrelationStatus.UNREGISTERED_HOST_ON_PORT.value,
        )
        self.assertFalse(obs["topology_corroborated"])


if __name__ == "__main__":
    unittest.main()

