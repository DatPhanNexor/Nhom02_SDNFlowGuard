import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

BACKEND_ROOT = Path(__file__).resolve().parents[2]
APP_DIR = BACKEND_ROOT / "app"
for p in (str(BACKEND_ROOT), str(APP_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from app import database, decision  # noqa: E402
from sdnflowguard.domain.policies.risk_scoring import (  # noqa: E402
    calculate_updated_score,
    determine_recommended_action,
)


class TestRiskScoringAndDecision(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.temp_db = Path(self._tmpdir.name) / "test_decision.db"
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

    def tearDown(self):
        self._env_patcher.stop()
        self._tmpdir.cleanup()

    def test_pure_risk_scoring_policy(self):
        score_after_high = calculate_updated_score(95.0, 1, test_only=False)
        self.assertEqual(score_after_high, 80.0)
        rec = determine_recommended_action(score_after_high, "balanced", test_only=False)
        self.assertEqual(rec["recommended_action"], "PROPOSE_BLOCK")

    def test_test_only_event_never_modifies_marks_or_blocks(self):
        actions = decision.process_event(
            {
                "Source": "IDS",
                "Event": "Synthetic High PPS",
                "Score": 500,
                "SourceIP": "10.0.0.1",
                "DestinationIP": "10.0.0.2",
                "test_only": True,
            }
        )
        self.assertEqual(actions, ["Observe (test_only)"])
        self.assertIsNone(database.get_setting_value("10.0.0.1 marks"))

    def test_process_event_accumulates_marks_in_isolated_db(self):
        actions = decision.process_event(
            {
                "Source": "Netflow",
                "Event": "Port Scan",
                "Score": 50,
                "SourceIP": "10.0.0.4",
                "DestinationIP": "10.0.0.2",
            }
        )
        self.assertEqual(actions, ["No Action"])
        self.assertAlmostEqual(decision.get_or_initialize_marks("10.0.0.4"), 5.0)


if __name__ == "__main__":
    unittest.main()

