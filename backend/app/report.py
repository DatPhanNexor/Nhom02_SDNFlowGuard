from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

try:
    from .database import get_actions, get_anomalies
except ImportError:
    from database import get_actions, get_anomalies


DEFAULT_TIMEZONE = "Asia/Ho_Chi_Minh (UTC+07:00)"
DEFAULT_TIME_RANGE = "last_30d"


def _get_current_vn_time() -> datetime:
    """Get current wall-clock time in project timezone Asia/Ho_Chi_Minh (UTC+07:00)."""
    try:
        import zoneinfo

        tz_vn = zoneinfo.ZoneInfo("Asia/Ho_Chi_Minh")
        return datetime.now(tz_vn).replace(tzinfo=None)
    except Exception:
        utc_now = datetime.now(timezone.utc)
        return (utc_now + timedelta(hours=7)).replace(tzinfo=None)


def _parse_timestamp(ts_value: Optional[str]) -> datetime:
    """Parse various timestamp string representations into a datetime object."""
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
        "%Y-%m-%d %H:%M",
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


def _parse_boundary(date_val: Optional[str], is_end: bool = False) -> Optional[datetime]:
    """Parse start or end date boundary strings with inclusive day coverage."""
    if not date_val:
        return None
    if isinstance(date_val, datetime):
        return date_val
    raw = str(date_val).strip()
    if not raw or raw.upper() in ("ALL", "ALL_TIME", "NONE"):
        return None
    # If YYYY-MM-DD
    if len(raw) == 10 and raw.count("-") == 2:
        try:
            dt = datetime.strptime(raw, "%Y-%m-%d")
            if is_end:
                return dt.replace(hour=23, minute=59, second=59, microsecond=999999)
            return dt.replace(hour=0, minute=0, second=0, microsecond=0)
        except ValueError:
            pass
    # If YYYY-MM-DDTHH:MM or YYYY-MM-DD HH:MM
    for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M"):
        try:
            dt = datetime.strptime(raw, fmt)
            if is_end:
                return dt.replace(second=59, microsecond=999999)
            return dt.replace(second=0, microsecond=0)
        except ValueError:
            pass
    return _parse_timestamp(raw)


def resolve_time_range(
    time_range: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    now: Optional[datetime] = None,
) -> Tuple[Optional[datetime], Optional[datetime], str]:
    """
    Dynamically resolve time range presets or custom boundaries relative to the current clock.
    Strictly avoids hardcoded project dates. Default: last 30 days.
    """
    if now is None:
        now = _get_current_vn_time()

    tr = (time_range or "").strip().lower()

    if tr in ("last_24h", "24h", "1d"):
        start = now - timedelta(hours=24)
        end = now
        label = f"Last 24 Hours ({start.strftime('%Y-%m-%d %H:%M')} to {end.strftime('%Y-%m-%d %H:%M')})"
        return start, end, label

    elif tr in ("last_7d", "7d", "week"):
        start = now - timedelta(days=7)
        end = now
        label = f"Last 7 Days ({start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')})"
        return start, end, label

    elif tr in ("last_30d", "30d", "monthly"):
        start = now - timedelta(days=30)
        end = now
        label = f"Last 30 Days ({start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')})"
        return start, end, label

    elif tr in ("this_month", "current_month"):
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now
        label = f"This Month ({start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')})"
        return start, end, label

    elif tr in ("prev_month", "previous_month", "last_month"):
        # First day of this month
        first_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # Last second of previous month
        end = first_this_month - timedelta(seconds=1)
        # First day of previous month
        start = end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        label = f"Previous Month ({start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')})"
        return start, end, label

    elif tr in ("all", "all_time"):
        return None, None, "All Time (Complete Historical Audit Archive)"

    elif start_date or end_date:
        start = _parse_boundary(start_date, is_end=False)
        end = _parse_boundary(end_date, is_end=True)
        if start and end and start > end:
            raise ValueError(
                f"Invalid date range: Start date ({start.strftime('%Y-%m-%d %H:%M')}) cannot be after End date ({end.strftime('%Y-%m-%d %H:%M')})."
            )
        s_str = start.strftime("%Y-%m-%d %H:%M") if start else "Beginning of Records"
        e_str = end.strftime("%Y-%m-%d %H:%M") if end else "Present"
        return start, end, f"Custom Range ({s_str} to {e_str})"

    else:
        # Default fallback is always dynamic Last 30 Days
        start = now - timedelta(days=30)
        end = now
        label = f"Last 30 Days ({start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')})"
        return start, end, label


def _escape_pdf_text(text: object) -> str:
    """Sanitize and escape string for PDF PostScript text commands."""
    raw = str(text if text is not None else "")
    cleaned = raw.encode("ascii", errors="replace").decode("ascii")
    return cleaned.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _format_cell_text(text: object, max_len: int) -> str:
    """Format and truncate text safely with ellipsis for PDF cell drawing."""
    s = str(text if text is not None else "N/A").strip()
    if len(s) > max_len:
        s = s[: max_len - 3] + "..."
    return _escape_pdf_text(s)


def _build_enterprise_a4_pdf_bytes(
    report_type: str,
    metadata: Dict[str, str],
    rows: List[Dict[str, object]],
) -> bytes:
    """
    Generate an enterprise SOC multi-page A4 PDF-1.4 report using pure Python.
    Dimensions: A4 standard (595.0 pt x 842.0 pt).
    Margins: Left 36.0 pt, Right 559.0 pt (usable width = 523.0 pt).
    """
    is_anomalies = report_type == "anomalies"
    dataset_title = (
        "Security Events & Anomaly Reports"
        if is_anomalies
        else "Defense Intervention & Audit Logs"
    )
    period_str = metadata.get("display_period", "Last 30 Days")
    gen_time_str = metadata.get(
        "generated_at",
        f"{_get_current_vn_time().strftime('%Y-%m-%d %H:%M:%S')} UTC+07:00",
    )
    rec_count_str = f"{len(rows)} matching record(s)"
    filters_applied = metadata.get("filters_applied", "None (All Severities / Actions)")

    # Columns configuration tailored for A4 width (523 pt total)
    if is_anomalies:
        columns: List[Tuple[str, float, str, int]] = [
            ("#", 24.0, "_index", 4),
            ("Detection Time", 105.0, "timestamp", 19),
            ("Source IP", 75.0, "source_ip", 15),
            ("Destination IP", 75.0, "destination_ip", 15),
            ("Event Type", 120.0, "event", 22),
            ("Score", 38.0, "score", 6),
            ("Severity", 48.0, "severity", 8),
            ("Sensor", 38.0, "source", 8),
        ]
    else:
        columns = [
            ("#", 24.0, "_index", 4),
            ("Timestamp", 105.0, "timestamp", 19),
            ("Action Type", 60.0, "action_type", 11),
            ("Target IP", 75.0, "source_ip", 15),
            ("Initiation", 60.0, "initiation_source", 11),
            ("Mode", 55.0, "enforcement_mode_short", 10),
            ("Policy Basis / Reason", 144.0, "reason", 28),
        ]

    # Calculate pagination for A4 height (842 pt)
    rows_page_1 = 26
    rows_subsequent = 36

    if not rows:
        pages_data = [[]]
    else:
        pages_data = []
        p1 = rows[:rows_page_1]
        pages_data.append(p1)
        remaining = rows[rows_page_1:]
        while remaining:
            pages_data.append(remaining[:rows_subsequent])
            remaining = remaining[rows_subsequent:]

    total_pages = len(pages_data)
    page_streams: List[bytes] = []

    global_row_index = 1
    for page_num, page_rows in enumerate(pages_data, start=1):
        cmds: List[str] = []

        # Top Header Banner across all pages (A4 width: 36 to 559)
        cmds.append("0.039 0.145 0.251 rg")
        cmds.append("36 786 523 36 re f")
        cmds.append(
            f"BT /F2 11 Tf 1 1 1 rg 48 805 Td ({_escape_pdf_text('SDNFLOWGUARD SOC AUDIT CENTER')}) Tj ET"
        )
        cmds.append(
            f"BT /F1 7 Tf 0.565 0.804 0.957 rg 48 793 Td ({_escape_pdf_text('ENTERPRISE SDN SECURITY OPERATIONS & DECISION AUDIT REPORT')}) Tj ET"
        )
        cmds.append(
            f"BT /F2 8 Tf 1 1 1 rg 460 799 Td ({_escape_pdf_text('AUDIT REPORT')}) Tj ET"
        )

        if page_num == 1:
            # Document Title & Academic Reference
            cmds.append(
                f"BT /F2 13 Tf 0.059 0.090 0.165 rg 36 764 Td ({_escape_pdf_text('SDNFlowGuard - Security Reports & Audit Center')}) Tj ET"
            )
            cmds.append(
                f"BT /F1 7.5 Tf 0.392 0.455 0.545 rg 36 751 Td ({_escape_pdf_text('Hoc phan: Chuyen de - He thong mang va Bao mat | Enterprise SOC Monitoring')}) Tj ET"
            )

            # Metadata Summary Grid (Boxed 2-column)
            cmds.append("0.973 0.980 0.988 rg 0.796 0.835 0.882 RG 0.75 w")
            cmds.append("36 658 523 80 re B")
            cmds.append("0.796 0.835 0.882 RG 0.5 w")
            cmds.append("297 658 m 297 738 l s")

            # Left Column Metadata
            cmds.append(
                f"BT /F2 7.5 Tf 0.059 0.090 0.165 rg 46 722 Td (Report Dataset: ) Tj /F1 7.5 Tf 0.2 0.25 0.3 rg ({_escape_pdf_text(dataset_title)}) Tj ET"
            )
            cmds.append(
                f"BT /F2 7.5 Tf 0.059 0.090 0.165 rg 46 706 Td (Time Range: ) Tj /F1 7.5 Tf 0.2 0.25 0.3 rg ({_escape_pdf_text(period_str)}) Tj ET"
            )
            cmds.append(
                f"BT /F2 7.5 Tf 0.059 0.090 0.165 rg 46 690 Td (Timezone: ) Tj /F1 7.5 Tf 0.2 0.25 0.3 rg ({_escape_pdf_text(DEFAULT_TIMEZONE)}) Tj ET"
            )
            cmds.append(
                f"BT /F2 7.5 Tf 0.059 0.090 0.165 rg 46 674 Td (Data Source: ) Tj /F1 7.5 Tf 0.2 0.25 0.3 rg (SQLite Audit Repository (sdnflowguard.db)) Tj ET"
            )

            # Right Column Metadata
            cmds.append(
                f"BT /F2 7.5 Tf 0.059 0.090 0.165 rg 307 722 Td (Generated At: ) Tj /F1 7.5 Tf 0.2 0.25 0.3 rg ({_escape_pdf_text(gen_time_str)}) Tj ET"
            )
            cmds.append(
                f"BT /F2 7.5 Tf 0.059 0.090 0.165 rg 307 706 Td (Operating Mode: ) Tj /F1 7.5 Tf 0.2 0.25 0.3 rg (DRY_RUN (Simulated Observation & Policy Staging)) Tj ET"
            )
            cmds.append(
                f"BT /F2 7.5 Tf 0.059 0.090 0.165 rg 307 690 Td (Total Records: ) Tj /F1 7.5 Tf 0.2 0.25 0.3 rg ({_escape_pdf_text(rec_count_str)}) Tj ET"
            )
            cmds.append(
                f"BT /F2 7.5 Tf 0.059 0.090 0.165 rg 307 674 Td (Filters Applied: ) Tj /F1 7.5 Tf 0.2 0.25 0.3 rg ({_escape_pdf_text(filters_applied)}) Tj ET"
            )

            current_y = 632.0
        else:
            # Subsequent pages header
            cmds.append(
                f"BT /F2 9 Tf 0.059 0.090 0.165 rg 36 764 Td ({_escape_pdf_text(dataset_title)} - (Continued)) Tj ET"
            )
            current_y = 746.0

        if not rows and page_num == 1:
            # Informative Empty State Box (Neutral SOC Telemetry Notification)
            cmds.append("0.965 0.973 0.984 rg 0.796 0.835 0.882 RG 0.75 w")
            cmds.append("36 548 523 72 re B")
            cmds.append(
                f"BT /F2 9 Tf 0.059 0.090 0.165 rg 48 602 Td ({_escape_pdf_text('STATUS: NO AUDIT RECORDS MATCHING ACTIVE FILTERS IN THIS WINDOW')}) Tj ET"
            )
            cmds.append(
                f"BT /F1 7.5 Tf 0.2 0.25 0.3 rg 48 587 Td ({_escape_pdf_text('Selected Time Range: ' + period_str + ' (' + DEFAULT_TIMEZONE + ')')}) Tj ET"
            )
            cmds.append(
                f"BT /F1 7.5 Tf 0.2 0.25 0.3 rg 48 572 Td ({_escape_pdf_text('No telemetry events or defense decisions matched the applied criteria during this specific window.')}) Tj ET"
            )
            cmds.append(
                f"BT /F1 7 Tf 0.392 0.455 0.545 rg 48 557 Td ({_escape_pdf_text('Note: This represents sensor quiescence, not an absence of network monitoring or detection coverage.')}) Tj ET"
            )
        else:
            # Table Header Row
            cmds.append("0.118 0.161 0.231 rg")
            cmds.append(f"36 {current_y - 18:.1f} 523 18 re f")
            col_x = 36.0
            for header, width, _, _ in columns:
                cmds.append(
                    f"BT /F2 7 Tf 1 1 1 rg {col_x + 3.0:.1f} {current_y - 12.5:.1f} Td ({_escape_pdf_text(header)}) Tj ET"
                )
                col_x += width

            current_y -= 18.0

            # Table Data Rows
            for row_data in page_rows:
                # Zebra shading
                if global_row_index % 2 == 0:
                    cmds.append("0.965 0.973 0.984 rg")
                    cmds.append(f"36 {current_y - 15:.1f} 523 15 re f")

                # Bottom cell border
                cmds.append("0.886 0.910 0.941 RG 0.3 w")
                cmds.append(f"36 {current_y - 15:.1f} m 559 {current_y - 15:.1f} l s")

                col_x = 36.0
                for _, width, key, max_chars in columns:
                    if key == "_index":
                        val_str = str(global_row_index)
                    else:
                        val_str = _format_cell_text(row_data.get(key), max_chars)

                    # Highlight scores and severity
                    if key == "score":
                        try:
                            score_num = int(row_data.get("score") or 0)
                            if score_num >= 70:
                                text_color = "0.792 0.149 0.149"
                            elif score_num >= 40:
                                text_color = "0.851 0.463 0.024"
                            else:
                                text_color = "0.086 0.627 0.365"
                        except (ValueError, TypeError):
                            text_color = "0.2 0.25 0.3"
                        cmds.append(
                            f"BT /F2 7 Tf {text_color} rg {col_x + 3.0:.1f} {current_y - 11.0:.1f} Td ({val_str}) Tj ET"
                        )
                    elif key == "severity":
                        sev_str = str(row_data.get("severity") or "").upper()
                        if "CRITICAL" in sev_str or "HIGH" in sev_str:
                            cmds.append(
                                f"BT /F2 6.5 Tf 0.792 0.149 0.149 rg {col_x + 3.0:.1f} {current_y - 11.0:.1f} Td ({val_str}) Tj ET"
                            )
                        elif "MEDIUM" in sev_str:
                            cmds.append(
                                f"BT /F2 6.5 Tf 0.851 0.463 0.024 rg {col_x + 3.0:.1f} {current_y - 11.0:.1f} Td ({val_str}) Tj ET"
                            )
                        else:
                            cmds.append(
                                f"BT /F1 6.5 Tf 0.086 0.627 0.365 rg {col_x + 3.0:.1f} {current_y - 11.0:.1f} Td ({val_str}) Tj ET"
                            )
                    elif key in ("action_type", "enforcement_mode_short"):
                        cmds.append(
                            f"BT /F2 6.5 Tf 0.118 0.161 0.231 rg {col_x + 3.0:.1f} {current_y - 11.0:.1f} Td ({val_str}) Tj ET"
                        )
                    else:
                        cmds.append(
                            f"BT /F1 7 Tf 0.118 0.161 0.231 rg {col_x + 3.0:.1f} {current_y - 11.0:.1f} Td ({val_str}) Tj ET"
                        )

                    col_x += width

                global_row_index += 1
                current_y -= 15.0

        # Footer on each page (A4 bottom)
        cmds.append("0.796 0.835 0.882 RG 0.5 w")
        cmds.append("36 38 m 559 38 l s")
        cmds.append(
            f"BT /F1 6.5 Tf 0.392 0.455 0.545 rg 36 26 Td ({_escape_pdf_text('SDNFlowGuard SOC Reporting & Audit Center | Network Systems & Security')}) Tj ET"
        )
        cmds.append(
            f"BT /F2 6.5 Tf 0.118 0.161 0.231 rg 508 26 Td ({_escape_pdf_text(f'Page {page_num} of {total_pages}')}) Tj ET"
        )

        stream_data = "\n".join(cmds).encode("ascii")
        page_streams.append(stream_data)

    # Assemble A4 PDF-1.4 objects (595 x 842 pt)
    objects: List[bytes] = []

    # Obj 1: Catalog
    objects.append(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")

    # Obj 2: Pages dictionary
    kids_refs = " ".join(f"{3 + 2 * i} 0 R" for i in range(total_pages))
    objects.append(
        f"2 0 obj\n<< /Type /Pages /Kids [{kids_refs}] /Count {total_pages} >>\nendobj\n".encode(
            "ascii"
        )
    )

    font1_obj_num = 3 + 2 * total_pages
    font2_obj_num = 4 + 2 * total_pages

    # Page and Content objects
    for i in range(total_pages):
        page_obj_num = 3 + 2 * i
        content_obj_num = 4 + 2 * i
        stream_bytes = page_streams[i]

        page_dict = (
            f"{page_obj_num} 0 obj\n"
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
            f"/Contents {content_obj_num} 0 R "
            f"/Resources << /Font << /F1 {font1_obj_num} 0 R /F2 {font2_obj_num} 0 R >> >> >>\n"
            f"endobj\n"
        ).encode("ascii")
        objects.append(page_dict)

        content_obj = (
            f"{content_obj_num} 0 obj\n"
            f"<< /Length {len(stream_bytes)} >>\nstream\n".encode("ascii")
            + stream_bytes
            + b"\nendstream\nendobj\n"
        )
        objects.append(content_obj)

    # Font objects
    objects.append(
        f"{font1_obj_num} 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n".encode(
            "ascii"
        )
    )
    objects.append(
        f"{font2_obj_num} 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>\nendobj\n".encode(
            "ascii"
        )
    )

    # Strict xref table and trailer
    pdf_bytes = bytearray(b"%PDF-1.4\n")
    offsets = []
    for obj in objects:
        offsets.append(len(pdf_bytes))
        pdf_bytes.extend(obj)

    xref_offset = len(pdf_bytes)
    num_total_entries = len(objects) + 1
    pdf_bytes.extend(f"xref\n0 {num_total_entries}\n".encode("ascii"))
    pdf_bytes.extend(b"0000000000 65535 f \n")
    for off in offsets:
        pdf_bytes.extend(f"{off:010d} 00000 n \n".encode("ascii"))

    pdf_bytes.extend(
        f"trailer\n<< /Size {num_total_entries} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode(
            "ascii"
        )
    )
    return bytes(pdf_bytes)


class ReportGenerator:
    """Core reporting service handling dynamic time ranges, SOC criteria filtering, KPI computation, and A4 PDF generation."""

    def filter_data_by_date_range(
        self,
        data: List[Dict[str, object]],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[Dict[str, object]]:
        """Filter telemetry events by timestamp range (inclusive)."""
        if not data:
            return []

        start_bound = _parse_boundary(start_date, is_end=False)
        end_bound = _parse_boundary(end_date, is_end=True)

        filtered = []
        for item in data:
            ts = _parse_timestamp(item.get("timestamp"))
            if start_bound and ts < start_bound:
                continue
            if end_bound and ts > end_bound:
                continue
            filtered.append(dict(item))
        return filtered

    def filter_data_by_monthly(self, data: List[Dict[str, object]]) -> List[Dict[str, object]]:
        """Legacy retention window filter (dynamically resolves to last 30 days)."""
        start_bound, end_bound, _ = resolve_time_range("last_30d")
        filtered = []
        for item in data:
            ts = _parse_timestamp(item.get("timestamp"))
            if start_bound and ts < start_bound:
                continue
            if end_bound and ts > end_bound:
                continue
            filtered.append(dict(item))
        return filtered

    def get_kpi_summary(
        self,
        start_bound: Optional[datetime] = None,
        end_bound: Optional[datetime] = None,
    ) -> Dict[str, int]:
        """Compute high-level SOC metrics for the given time window without hardcoding."""
        all_anomalies = get_anomalies()
        all_actions = get_actions()

        sec_events = 0
        for item in all_anomalies:
            ts = _parse_timestamp(item.get("timestamp"))
            if start_bound and ts < start_bound:
                continue
            if end_bound and ts > end_bound:
                continue
            sec_events += 1

        defense_decisions = 0
        simulated_actions = 0
        enforced_actions = 0
        for item in all_actions:
            ts = _parse_timestamp(item.get("timestamp"))
            if start_bound and ts < start_bound:
                continue
            if end_bound and ts > end_bound:
                continue
            defense_decisions += 1
            # In DRY_RUN operational mode, actions are evaluated by Safety Gate and staged/simulated
            simulated_actions += 1

        return {
            "security_events": sec_events,
            "defense_decisions": defense_decisions,
            "simulated_actions": simulated_actions,
            "enforced_actions": enforced_actions,
        }

    def generate_report(
        self,
        report_type: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        time_range: Optional[str] = None,
        severity: Optional[str] = None,
        action_type: Optional[str] = None,
        source_ip: Optional[str] = None,
        initiation_source: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Generate structured JSON audit report with dynamic SOC filtering and KPI statistics.
        Supports:
        - Dynamic time ranges: 'last_24h', 'last_7d', 'last_30d' (default), 'this_month', 'prev_month', 'all', 'custom'
        - Contextual filters: severity (high/medium/low), action_type, source_ip, initiation_source
        """
        is_anomalies = report_type == "anomalies"
        if is_anomalies:
            raw_data = get_anomalies()
        elif report_type == "actions":
            raw_data = get_actions()
        else:
            raise ValueError("Invalid report type. Expected 'anomalies' or 'actions'.")

        # Resolve dynamic date range relative to current clock
        start_bound, end_bound, display_period = resolve_time_range(
            time_range=time_range,
            start_date=start_date,
            end_date=end_date,
        )

        # 1. Filter by time window
        time_filtered = []
        for item in raw_data:
            ts = _parse_timestamp(item.get("timestamp"))
            if start_bound and ts < start_bound:
                continue
            if end_bound and ts > end_bound:
                continue
            time_filtered.append(dict(item))

        # 2. Enrich and filter by contextual SOC criteria
        filtered_data = []
        filter_descriptions = []

        target_sev = (severity or "").strip().lower()
        if target_sev and target_sev != "all":
            filter_descriptions.append(f"Severity: {target_sev.upper()}")

        target_act = (action_type or "").strip().lower()
        if target_act and target_act != "all":
            filter_descriptions.append(f"Action: {target_act.capitalize()}")

        target_ip = (source_ip or "").strip()
        if target_ip:
            filter_descriptions.append(f"IP: {target_ip}")

        target_init = (initiation_source or "").strip().lower()
        if target_init and target_init != "all":
            filter_descriptions.append(f"Source: {target_init.capitalize()}")

        for item in time_filtered:
            enriched = dict(item)

            if is_anomalies:
                # Severity categorization
                try:
                    score_val = int(item.get("score") or 0)
                except (ValueError, TypeError):
                    score_val = 0
                if score_val >= 85:
                    sev = "Critical"
                elif score_val >= 70:
                    sev = "High"
                elif score_val >= 40:
                    sev = "Medium"
                else:
                    sev = "Low"
                enriched["severity"] = sev

                # Check severity filter
                if target_sev and target_sev != "all":
                    if target_sev == "high" and score_val < 70:
                        continue
                    elif target_sev == "medium" and not (40 <= score_val < 70):
                        continue
                    elif target_sev == "low" and score_val >= 40:
                        continue

                # Check IP filter
                if target_ip:
                    src_ip = str(item.get("source_ip") or "")
                    dst_ip = str(item.get("destination_ip") or "")
                    if target_ip not in src_ip and target_ip not in dst_ip:
                        continue

                # Provenance tag
                src_val = str(item.get("source") or "")
                if src_val.lower() in ("test", "fixture"):
                    enriched["provenance"] = "HISTORICAL_FIXTURE"
                else:
                    enriched["provenance"] = "OBSERVED_TELEMETRY"

                enriched["destination_ip"] = item.get("destination_ip") or "0.0.0.0"

            else:
                # Defense Decisions (actions)
                act_str = str(item.get("action_type") or "")
                act_lower = act_str.lower()
                init_src = str(item.get("admin_or_automated") or "Automated")

                # Filter by action type
                if target_act and target_act != "all":
                    if target_act not in act_lower:
                        continue

                # Filter by initiation source
                if target_init and target_init != "all":
                    if target_init == "automated" and "auto" not in init_src.lower():
                        continue
                    elif target_init == "admin" and "admin" not in init_src.lower():
                        continue

                # Filter by IP
                if target_ip:
                    if target_ip not in str(item.get("source_ip") or ""):
                        continue

                enriched["initiation_source"] = init_src
                enriched["enforcement_mode"] = "DRY_RUN (SIMULATED)"
                enriched["enforcement_mode_short"] = "DRY_RUN"
                enriched["enforcement_status"] = "STAGED_POLICY"

            filtered_data.append(enriched)

        # 3. Calculate KPI summary across the active time window
        kpi_stats = self.get_kpi_summary(start_bound, end_bound)

        return {
            "report_type": report_type,
            "time_range": time_range or "last_30d",
            "start_date": start_bound.isoformat() if start_bound else None,
            "end_date": end_bound.isoformat() if end_bound else None,
            "display_period": display_period,
            "timezone": DEFAULT_TIMEZONE,
            "defense_mode": "DRY_RUN",
            "total_records": len(filtered_data),
            "filters_applied": ", ".join(filter_descriptions) if filter_descriptions else "None (All Criteria)",
            "kpi": {
                "total_records": len(filtered_data),
                "security_events": kpi_stats["security_events"],
                "defense_decisions": kpi_stats["defense_decisions"],
                "simulated_actions": kpi_stats["simulated_actions"],
                "enforced_actions": kpi_stats["enforced_actions"],
            },
            "data": filtered_data,
        }

    def generate_pdf_report(
        self,
        report_type: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        time_range: Optional[str] = None,
        severity: Optional[str] = None,
        action_type: Optional[str] = None,
        source_ip: Optional[str] = None,
        initiation_source: Optional[str] = None,
    ) -> bytes:
        """Generate A4 PDF audit report using pure Python."""
        report_json = self.generate_report(
            report_type=report_type,
            start_date=start_date,
            end_date=end_date,
            time_range=time_range,
            severity=severity,
            action_type=action_type,
            source_ip=source_ip,
            initiation_source=initiation_source,
        )
        metadata = {
            "display_period": str(report_json.get("display_period", "")),
            "timezone": str(report_json.get("timezone", DEFAULT_TIMEZONE)),
            "generated_at": f"{_get_current_vn_time().strftime('%Y-%m-%d %H:%M:%S')} UTC+07:00",
            "defense_mode": str(report_json.get("defense_mode", "DRY_RUN")),
            "filters_applied": str(report_json.get("filters_applied", "None")),
        }
        rows = report_json.get("data") or []
        return _build_enterprise_a4_pdf_bytes(report_type, metadata, rows)
