import sys
import unittest
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2]
DEFENSE_DIR = BACKEND_ROOT / "defense"
for p in (str(BACKEND_ROOT), str(DEFENSE_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

import source_ip_evidence_analyzer as analyzer  # noqa: E402


class TestSourceIpEvidenceAnalyzer(unittest.TestCase):
    def test_builtin_self_test_passes(self):
        analyzer.self_test()

    def test_real_step63_utf16_capture_file_parses_cleanly(self):
        capture_path = DEFENSE_DIR / "evidence" / "ingress_icmp_20261101_014645.txt"
        text = analyzer.read_capture(capture_path)
        result = analyzer.analyze(text)
        self.assertEqual(result["total_packets"], 24)
        self.assertFalse(result["capture_clock_has_date"])
        self.assertFalse(result["capture_clock_has_timezone"])
        self.assertFalse(result["security_assessment"]["automatic_block_allowed"])
        self.assertEqual(result["security_assessment"]["decision"], "OBSERVE")

    def test_rejects_unsupported_or_empty_capture(self):
        with self.assertRaises(ValueError):
            analyzer.analyze("no packets here")


if __name__ == "__main__":
    unittest.main()

