from datetime import datetime, timedelta

try:
    from .database import get_actions, get_anomalies
except ImportError:
    from database import get_actions, get_anomalies


def _parse_timestamp(ts_value):
    if isinstance(ts_value, datetime):
        return ts_value
    raw = str(ts_value or "").strip()
    if not raw:
        return datetime(1970, 1, 1)
    if raw.endswith("Z"):
        raw = raw[:-1]
    for fmt in (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%d",
    ):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        return datetime(1970, 1, 1)


def _escape_pdf_text(text):
    cleaned = str(text).encode("ascii", errors="replace").decode("ascii")
    return cleaned.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _build_fallback_pdf_bytes(report_type: str, rows: list) -> bytes:
    """Build valid PDF-1.4 bytes without external wkhtmltopdf binary."""
    lines = [
        f"SDNFlowGuard {report_type.capitalize()} Security Report (Monthly)",
        f"Generated At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Total Records Included: {len(rows)}",
        "------------------------------------------------------------------------",
    ]
    if not rows:
        lines.append("No data available for the selected time range.")
    else:
        for idx, item in enumerate(rows[:32], start=1):
            summary = " | ".join(f"{k}: {v}" for k, v in item.items())
            lines.append(f"{idx}. {summary[:85]}")

    stream_cmds = ["BT", "/F1 10 Tf", "45 750 Td", "14 TL"]
    for i, line in enumerate(lines):
        escaped = _escape_pdf_text(line)
        if i == 0:
            stream_cmds.append(f"({escaped}) Tj")
        else:
            stream_cmds.append(f"T* ({escaped}) Tj")
    stream_cmds.append("ET")
    stream_data = "\n".join(stream_cmds).encode("ascii")

    objects = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n",
        f"4 0 obj\n<< /Length {len(stream_data)} >>\nstream\n".encode("ascii")
        + stream_data
        + b"\nendstream\nendobj\n",
        b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
    ]

    pdf_bytes = bytearray(b"%PDF-1.4\n")
    offsets = []
    for obj in objects:
        offsets.append(len(pdf_bytes))
        pdf_bytes.extend(obj)

    xref_offset = len(pdf_bytes)
    pdf_bytes.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf_bytes.extend(b"0000000000 65535 f \n")
    for off in offsets:
        pdf_bytes.extend(f"{off:010d} 00000 n \n".encode("ascii"))

    pdf_bytes.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode(
            "ascii"
        )
    )
    return bytes(pdf_bytes)


class ReportGenerator:
    def filter_data_by_monthly(self, data):
        """Filter the provided data for a 30-day window."""
        if not data:
            return []
        now = datetime.now()
        cutoff = now - timedelta(days=30)

        recent = [
            item
            for item in data
            if _parse_timestamp(item.get("timestamp")) > cutoff
        ]
        if recent:
            return recent

        # If all records in SQLite are historical archive data, anchor 30-day window to latest record
        latest_ts = max(
            (_parse_timestamp(item.get("timestamp")) for item in data),
            default=now,
        )
        archive_cutoff = latest_ts - timedelta(days=30)
        return [
            item
            for item in data
            if _parse_timestamp(item.get("timestamp")) >= archive_cutoff
        ]

    def generate_report(self, report_type):
        """Generate a report for the past 30 days ('anomalies' or 'actions')."""
        if report_type == "anomalies":
            anomalies = get_anomalies()
            data = self.filter_data_by_monthly(anomalies)
        elif report_type == "actions":
            actions = get_actions()
            data = self.filter_data_by_monthly(actions)
        else:
            raise ValueError("Invalid report type. Expected 'anomalies' or 'actions'.")
        return {"report_type": report_type, "time_range": "monthly", "data": data}

    def generate_pdf_report(self, report_type):
        """Generate a PDF report for the past 30 days, with pure-Python PDF fallback."""
        report_data = self.generate_report(report_type)
        rows = report_data.get("data") or []

        if not rows:
            html_content = f"""
            <html>
            <head><title>{report_type.capitalize()} Report</title></head>
            <body>
                <h1>{report_type.capitalize()} Report</h1>
                <h2>Time Range: Monthly</h2>
                <p>No data available for the selected time range.</p>
            </body>
            </html>
            """
        else:
            headers_html = "".join(
                f"<th>{str(key).capitalize()}</th>" for key in rows[0].keys() if key
            )
            body_html = "".join(
                "<tr>"
                + "".join(
                    "<td>" + str(value if value is not None else "N/A") + "</td>"
                    for value in item.values()
                )
                + "</tr>"
                for item in rows
            )
            html_content = f"""
            <html>
            <head><title>{report_type.capitalize()} Report</title></head>
            <body>
                <h1>{report_type.capitalize()} Report</h1>
                <h2>Time Range: Monthly</h2>
                <table border="1">
                    <thead><tr>{headers_html}</tr></thead>
                    <tbody>{body_html}</tbody>
                </table>
            </body>
            </html>
            """
        try:
            import pdfkit

            pdf_content = pdfkit.from_string(html_content, False)
            if isinstance(pdf_content, bytes) and pdf_content.startswith(b"%PDF"):
                return pdf_content
        except Exception:
            pass

        return _build_fallback_pdf_bytes(report_type, rows)
