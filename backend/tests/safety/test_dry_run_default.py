import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from sdnflowguard.infrastructure.configuration.settings import AppSettings  # noqa: E402


class TestDryRunDefault(unittest.TestCase):
    def test_defense_mode_defaults_to_dry_run(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("SDNFLOW_DEFENSE_MODE", None)
            settings = AppSettings.from_env()
            self.assertEqual(settings.defense_mode, "DRY_RUN")
            self.assertFalse(settings.flask_debug)


if __name__ == "__main__":
    unittest.main()

