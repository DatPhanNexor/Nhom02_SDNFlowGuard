import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class TestNoSecretLeakage(unittest.TestCase):
    def test_run_py_has_no_hardcoded_elk_password(self):
        run_py = (PROJECT_ROOT / "backend" / "run.py").read_text(encoding="utf-8")
        self.assertNotIn("T5fkob-BmswSUWNJ9uzA", run_py)

    def test_env_examples_exist_and_have_empty_secrets(self):
        for rel in (".env.example", "backend/.env.example"):
            path = PROJECT_ROOT / rel
            self.assertTrue(path.is_file(), f"Missing {rel}")
            text = path.read_text(encoding="utf-8")
            self.assertIn("SDNFLOW_ONOS_PASSWORD=", text)
            self.assertIn("SDNFLOW_ELK_PASSWORD=", text)
            self.assertNotIn("T5fkob-BmswSUWNJ9uzA", text)


if __name__ == "__main__":
    unittest.main()

