import json
import unittest
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = BACKEND_ROOT / "collectors" / "state"
EVIDENCE_DIR = BACKEND_ROOT / "defense" / "evidence"


class TestCheckpointAndEvidenceIntegrity(unittest.TestCase):
    def test_checkpoint_files_exist_and_have_valid_schema(self):
        expected_files = (
            "auto_dry_t4_c2.json",
            "auto_dry_t4_c2_v2.json",
            "auto_publish_t4_c2.json",
            "auto_publish_t4_c2_v2.json",
        )
        for fname in expected_files:
            fpath = STATE_DIR / fname
            self.assertTrue(fpath.is_file(), f"Missing checkpoint {fname}")
            data = json.loads(fpath.read_text(encoding="utf-8"))
            self.assertIn("version", data)
            self.assertEqual(data["threshold_pps"], 4.0)
            self.assertEqual(data["consecutive"], 2)

    def test_step63_evidence_files_exist_and_are_intact(self):
        txt_path = EVIDENCE_DIR / "ingress_icmp_20261101_014645.txt"
        json_path = EVIDENCE_DIR / "ingress_icmp_20261101_014645.json"
        self.assertTrue(txt_path.is_file())
        self.assertTrue(json_path.is_file())
        data = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertEqual(data["total_packets"], 24)


if __name__ == "__main__":
    unittest.main()

