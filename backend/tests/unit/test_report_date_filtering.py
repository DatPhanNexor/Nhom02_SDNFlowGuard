from datetime import datetime, timedelta
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

from app import database  # noqa: E402
from app.report import ReportGenerator, resolve_time_range, _parse_boundary, _parse_timestamp  # noqa: E402


class TestReportDateFiltering(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.temp_db = Path(self._tmpdir.name) / "test_report_filtering.db"
        self._env_patcher = patch.dict(
            os.environ,
            {"SDNFLOW_DB_PATH": str(self.temp_db)},
        )
        self._env_patcher.start()
        database.init_db()

        # Seed historical fixtures
        database.save_event({
            "Source": "Netflow",
            "Event": "Port Scanning",
            "Score": 75,
            "SourceIP": "10.0.0.11",
            "DestinationIP": "10.0.0.2",
        })
        database.record_action("Block", "Safety Gate simulated drop", "10.0.0.11", "Automated")

        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE events SET timestamp = '2025-01-13 01:24:13' WHERE source_ip = '10.0.0.11'")
            cursor.execute("UPDATE actions SET timestamp = '2025-01-13 02:46:59' WHERE source_ip = '10.0.0.11'")
            conn.commit()

        self.gen = ReportGenerator()

    def tearDown(self):
        self._env_patcher.stop()
        self._tmpdir.cleanup()

    def test_dynamic_time_range_resolution(self):
        """Verify dynamic time range presets calculate boundaries correctly without hardcoded dates."""
        mock_now = datetime(2026, 11, 23, 14, 30, 0)

        # 1. Last 24 Hours
        s24, e24, l24 = resolve_time_range("last_24h", now=mock_now)
        self.assertEqual(e24, mock_now)
        self.assertEqual(s24, mock_now - timedelta(hours=24))
        self.assertIn("Last 24 Hours", l24)

        # 2. Last 7 Days
        s7, e7, l7 = resolve_time_range("last_7d", now=mock_now)
        self.assertEqual(e7, mock_now)
        self.assertEqual(s7, mock_now - timedelta(days=7))

        # 3. Last 30 Days (Default)
        s30, e30, l30 = resolve_time_range("last_30d", now=mock_now)
        self.assertEqual(e30, mock_now)
        self.assertEqual(s30, mock_now - timedelta(days=30))

        # 4. This Month
        sm, em, lm = resolve_time_range("this_month", now=mock_now)
        self.assertEqual(sm, datetime(2026, 11, 1, 0, 0, 0))
        self.assertEqual(em, mock_now)

        # 5. Previous Month (October 2026 for November)
        sp, ep, lp = resolve_time_range("prev_month", now=mock_now)
        self.assertEqual(sp, datetime(2026, 10, 1, 0, 0, 0))
        self.assertEqual(ep, datetime(2026, 10, 31, 23, 59, 59))

        # 6. All Time
        sa, ea, la = resolve_time_range("all", now=mock_now)
        self.assertIsNone(sa)
        self.assertIsNone(ea)

    def test_invalid_custom_date_range_raises_error(self):
        """Start date greater than end date must be rejected."""
        with self.assertRaises(ValueError) as ctx:
            resolve_time_range(start_date="2026-11-23", end_date="2026-11-20")
        self.assertIn("Start date", str(ctx.exception))

    def test_all_time_query_returns_kpi_and_records(self):
        """Selecting all time returns fixtures and accurate KPI metrics."""
        report = self.gen.generate_report("anomalies", time_range="all")
        self.assertEqual(report["total_records"], 1)
        self.assertEqual(report["kpi"]["security_events"], 1)
        self.assertEqual(report["kpi"]["defense_decisions"], 1)
        self.assertEqual(report["data"][0]["source_ip"], "10.0.0.11")
        self.assertEqual(report["data"][0]["severity"], "High")

    def test_recent_window_excludes_historical_fixtures(self):
        """Current 30-day window does not leak older 2025 events."""
        # Querying last 30 days relative to present
        report = self.gen.generate_report("anomalies", time_range="last_30d")
        # 2025 records are outside the 30-day window
        self.assertEqual(report["total_records"], 0)

        # PDF generation should render A4 format with clean empty state
        pdf_bytes = self.gen.generate_pdf_report("anomalies", time_range="last_30d")
        self.assertTrue(pdf_bytes.startswith(b"%PDF-1.4"))
        self.assertIn(b"/MediaBox [0 0 595 842]", pdf_bytes)  # A4
        self.assertIn(b"NO AUDIT RECORDS", pdf_bytes)
        self.assertIn(b"%%EOF", pdf_bytes)

    def test_advanced_filtering_by_severity_and_action(self):
        """Test filtering by severity and action type."""
        database.save_event({
            "Source": "Suricata-SDN",
            "Event": "Low Risk Ping",
            "Score": 20,
            "SourceIP": "10.0.0.5",
            "DestinationIP": "10.0.0.2",
        })
        # Test low severity
        rep_low = self.gen.generate_report("anomalies", time_range="all", severity="low")
        self.assertEqual(rep_low["total_records"], 1)
        self.assertEqual(rep_low["data"][0]["source_ip"], "10.0.0.5")

        # Test high severity
        rep_high = self.gen.generate_report("anomalies", time_range="all", severity="high")
        self.assertEqual(rep_high["total_records"], 1)
        self.assertEqual(rep_high["data"][0]["source_ip"], "10.0.0.11")

    def test_multipage_a4_pdf_generation(self):
        """Verify multi-page A4 PDF generation handles 50+ actions cleanly."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            for i in range(50):
                cursor.execute(
                    "INSERT INTO actions (timestamp, action_type, reason, source_ip, admin_or_automated) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (f"2026-11-{i%20 + 1:02d} 10:00:00", "Rate Limit", f"Meter limit test {i}", f"10.0.0.{i+1}", "Automated")
                )
            conn.commit()

        pdf_bytes = self.gen.generate_pdf_report("actions", time_range="all")
        self.assertTrue(pdf_bytes.startswith(b"%PDF-1.4"))
        self.assertIn(b"/MediaBox [0 0 595 842]", pdf_bytes)
        self.assertTrue(b"/Count 2" in pdf_bytes or b"/Count 3" in pdf_bytes)
        self.assertIn(b"%%EOF", pdf_bytes)


if __name__ == "__main__":
    unittest.main()
