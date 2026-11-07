import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'collectors'))
import sdn_overlap_alert_monitor_v2 as monitor_v2


class TestReliableMonitorV2(unittest.TestCase):
    @staticmethod
    def hit(event_id, stamp, rate):
        return {
            '_index': 'test-index', '_id': event_id,
            '_source': {
                'event_id': event_id, '@timestamp': stamp,
                'switch_id': 'of:0000000000000001',
                'port_number': 1, 'rx_pps': rate,
                'tx_pps': 0.0, 'sample_seconds': 10.0,
            },
        }

    def test_v2_builtin_self_test(self):
        monitor_v2.self_test()

    def test_late_sample_detected_once_without_network_calls(self):
        earlier = self.hit('a', '2026-11-01T10:00:00Z', 6)
        later = self.hit('b', '2026-11-01T10:00:20Z', 0)
        late = self.hit('late', '2026-11-01T10:00:10Z', 7)
        hits = [earlier, late, later]
        candidates = monitor_v2.build_candidates(hits, {'test-index:late'}, 4, 2)
        replay = monitor_v2.build_candidates(hits, set(), 4, 2)
        self.assertEqual(len(candidates), 1)
        self.assertEqual(replay, [])

    def test_nanosecond_timestamp_parse(self):
        parsed = monitor_v2.parse_ts('2026-11-01T10:00:00.617542881Z')
        self.assertEqual(parsed.microsecond, 617542)
        self.assertEqual(parsed.utcoffset().total_seconds(), 0)
