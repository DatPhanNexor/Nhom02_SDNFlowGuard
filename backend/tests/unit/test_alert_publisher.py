import sys
import unittest
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2]
COLLECTORS_DIR = BACKEND_ROOT / "collectors"
for p in (str(BACKEND_ROOT), str(COLLECTORS_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

import sdn_alert_publisher as publisher  # noqa: E402


class TestAlertPublisher(unittest.TestCase):
    def test_make_event_is_deterministic_and_marks_test_only(self):
        candidate = {
            "switch_id": "of:0000000000000001",
            "port_number": "1",
            "timestamp": "2026-11-01T00:00:00Z",
            "rx_pps": 5.5,
            "tx_pps": 5.5,
            "peak_pps": 5.5,
            "reason": "SUSTAINED_HIGH_PACKET_RATE",
        }
        ev1 = publisher.make_event(candidate, 4.0, 2)
        ev2 = publisher.make_event(candidate, 4.0, 2)
        self.assertEqual(ev1["alert_key"], ev2["alert_key"])
        self.assertEqual(len(ev1["alert_key"]), 64)
        self.assertTrue(ev1["test_only"])


if __name__ == "__main__":
    unittest.main()

