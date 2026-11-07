import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'collectors'))
import sdn_auto_alert_monitor as auto_monitor
import sdn_reliable_alert_monitor as monitor_v1


class TestReliableMonitorV1(unittest.TestCase):
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

    def test_auto_monitor_validates_and_marks_test_alert(self):
        hit = self.hit('event-1', '2026-11-01T10:00:00Z', 7)
        sample = auto_monitor.valid_sample(hit)
        self.assertIsNotNone(sample)
        event = auto_monitor.make_alert(hit, sample, 4.0, 2)
        repeat = auto_monitor.make_alert(hit, sample, 4.0, 2)
        self.assertEqual(event['alert_key'], repeat['alert_key'])
        self.assertTrue(event['test_only'])
        self.assertEqual(event['rule_id'], 'LAB_HIGH_PPS_AUTO_V1')

    def test_v1_checkpoint_and_dry_run_streak(self):
        args = SimpleNamespace(threshold_pps=4.0, consecutive=2,
                               lookback_days=7, publish_test_alerts=False)
        state = {'version': 1, 'threshold_pps': 4.0, 'consecutive': 2,
                 'cursor': ['2026-11-01T10:00:00Z', 'event-0'], 'ports': {}}
        with tempfile.TemporaryDirectory() as folder:
            checkpoint = Path(folder) / 'checkpoint.json'
            monitor_v1.save_checkpoint(checkpoint, state)
            restored = monitor_v1.load_checkpoint(checkpoint, args)
            self.assertEqual(restored['cursor'], state['cursor'])
            first = self.hit('event-a', '2026-11-01T10:00:10Z', 7)
            second = self.hit('event-b', '2026-11-01T10:00:20Z', 8)
            self.assertFalse(monitor_v1.process_hit(first, restored, args))
            self.assertTrue(monitor_v1.process_hit(second, restored, args))
            self.assertEqual(restored['ports']['of:0000000000000001|1']['streak'], 2)
