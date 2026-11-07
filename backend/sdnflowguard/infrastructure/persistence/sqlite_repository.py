"""SQLite repository implementation with context-managed connections and zero import side effects."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Iterator

from sdnflowguard.infrastructure.configuration.settings import DEFAULT_DB_PATH


class SQLiteRepository:
    """Repository encapsulating all SQLite operations on sdnflowguard.db."""

    def __init__(self, db_path: Path | str | None = None):
        self._db_path = Path(db_path) if db_path else DEFAULT_DB_PATH

    @property
    def db_path(self) -> Path:
        return self._db_path

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self._db_path), timeout=15)
        try:
            yield conn
        finally:
            conn.close()

    def init_schema(self) -> None:
        """Create core tables if they do not exist (never drops existing tables)."""
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    src_ip TEXT,
                    dest_ip TEXT,
                    alert_msg TEXT,
                    severity INTEGER
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    action TEXT,
                    details TEXT
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS flows (
                    id TEXT,
                    deviceId TEXT,
                    tableId INTEGER,
                    packetCount INTEGER,
                    byteCount INTEGER,
                    priority INTEGER,
                    timeout INTEGER,
                    isPermanent BOOLEAN,
                    state TEXT,
                    selector TEXT,
                    treatment TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT,
                    details TEXT,
                    timestamp TEXT
                )
                """
            )
            conn.commit()

    def store_alert(self, alert_data: dict[str, Any]) -> None:
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO alerts (timestamp, src_ip, dest_ip, alert_msg, severity)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    alert_data["timestamp"],
                    alert_data["src_ip"],
                    alert_data["dest_ip"],
                    alert_data["alert"]["signature"],
                    alert_data["alert"]["severity"],
                ),
            )
            conn.commit()

    def store_action(self, action: str, details: str | dict[str, Any]) -> int:
        details_str = (
            json.dumps(details, ensure_ascii=False)
            if isinstance(details, dict)
            else str(details)
        )
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO actions (timestamp, action, details)
                VALUES (datetime('now'), ?, ?)
                """,
                (action, details_str),
            )
            conn.commit()
            return int(cursor.lastrowid or 0)

    def store_flows(self, flows: list[dict[str, Any]]) -> None:
        with self.connection() as conn:
            cursor = conn.cursor()
            for flow in flows:
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO flows (
                        id, deviceId, tableId, packetCount, byteCount, priority,
                        timeout, isPermanent, state, selector, treatment
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        flow["id"],
                        flow["deviceId"],
                        flow["tableId"],
                        flow["packetCount"],
                        flow["byteCount"],
                        flow["priority"],
                        flow["timeout"],
                        flow["isPermanent"],
                        flow["state"],
                        json.dumps(flow["selector"]),
                        json.dumps(flow["treatment"]),
                    ),
                )
            conn.commit()

    def get_flows(self, limit: int = 20) -> list[dict[str, Any]]:
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM flows ORDER BY timestamp DESC LIMIT ?",
                (int(limit),),
            )
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
        flows = []
        for row in rows:
            flow = dict(zip(columns, row))
            flow["selector"] = json.loads(flow["selector"]) if isinstance(flow.get("selector"), str) else flow.get("selector")
            flow["treatment"] = json.loads(flow["treatment"]) if isinstance(flow.get("treatment"), str) else flow.get("treatment")
            flows.append(flow)
        return flows

    def get_actions(self, limit: int = 100) -> list[tuple[Any, ...]]:
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM actions ORDER BY id DESC LIMIT ?",
                (int(limit),),
            )
            return cursor.fetchall()

    def get_action_by_id(self, action_id: int) -> dict[str, Any] | None:
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, timestamp, action, details FROM actions WHERE id = ?",
                (int(action_id),),
            )
            row = cursor.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "timestamp": row[1],
            "action": row[2],
            "details": row[3],
        }

    def set_setting(self, key: str, value: Any) -> None:
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO settings (key, value)
                VALUES (?, ?)
                """,
                (str(key), str(value)),
            )
            conn.commit()

    def get_setting(self, key: str) -> str | None:
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT value FROM settings WHERE key = ?",
                (str(key),),
            )
            row = cursor.fetchone()
        return row[0] if row else None

    def get_all_settings(self) -> dict[str, str]:
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM settings")
            rows = cursor.fetchall()
        return {str(k): str(v) for k, v in rows}

    def store_event(self, event_type: str, details: dict[str, Any], timestamp: str | None = None) -> None:
        ts = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO events (type, details, timestamp)
                VALUES (?, ?, ?)
                """,
                (event_type, json.dumps(details, ensure_ascii=False), ts),
            )
            conn.commit()

    def get_events(self, start_time: datetime, end_time: datetime) -> list[dict[str, Any]]:
        start_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
        end_str = end_time.strftime("%Y-%m-%d %H:%M:%S")
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM events
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp DESC
                """,
                (start_str, end_str),
            )
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
        events = []
        for row in rows:
            evt = dict(zip(columns, row))
            if isinstance(evt.get("details"), str):
                try:
                    evt["details"] = json.loads(evt["details"])
                except Exception:
                    pass
            events.append(evt)
        return events

    def get_recent_events(self, days: int = 2) -> list[dict[str, Any]]:
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        return self.get_events(start_time, end_time)

