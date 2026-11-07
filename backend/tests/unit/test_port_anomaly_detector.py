import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'collectors'))
import sdn_port_anomaly_detector as detector


class TestPortAnomalyDetector(unittest.TestCase):
    @staticmethod
    def sample(stamp, pps):
        return {
            '@timestamp': stamp,
            'switch_id': 'of:0000000000000001',
            'port_number': 1,
            'rx_pps': pps,
            'tx_pps': 0,
            'sample_seconds': 10,
        }

    def test_two_consecutive_samples_trigger_one_candidate(self):
        samples = [
            self.sample('2026-11-01T10:00:00Z', 1),
            self.sample('2026-11-01T10:00:10Z', 5),
            self.sample('2026-11-01T10:00:20Z', 7),
            self.sample('2026-11-01T10:00:30Z', 9),
        ]
        states, alerts = detector.analyze(samples, threshold=4, consecutive=2)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]['port_number'], '1')
        self.assertEqual(alerts[0]['peak_pps'], 7.0)
        self.assertEqual(states[('of:0000000000000001', '1')]['count'], 4)

    def test_sampling_gap_breaks_consecutive_streak(self):
        samples = [
            self.sample('2026-11-01T10:00:00Z', 8),
            self.sample('2026-11-01T10:03:00Z', 8),
        ]
        _, alerts = detector.analyze(samples, threshold=4, consecutive=2)
        self.assertEqual(alerts, [])
