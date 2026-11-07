import contextlib
import os
from pathlib import Path
import sqlite3

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = str(PROJECT_ROOT / "database" / "sdnflowguard.db")


def _resolve_db_path() -> str:
    env_override = os.environ.get("SDNFLOW_DB_PATH")
    if env_override:
        return str(Path(env_override).resolve())
    return str(DB_PATH)


@contextlib.contextmanager
def get_connection():
    """Managed SQLite connection context manager with explicit closing and commit/rollback."""
    target = Path(_resolve_db_path())
    target.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(target), timeout=15)
    try:
        with conn:
            yield conn
    finally:
        conn.close()


def init_db():
    """Initialize the settings, flows, events, and actions tables if they do not exist."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                setting_id INTEGER PRIMARY KEY AUTOINCREMENT,
                key VARCHAR(50) UNIQUE NOT NULL,
                value VARCHAR(255) NOT NULL
            );
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS flows (
                id TEXT PRIMARY KEY,
                source_ip TEXT,
                destination_ip TEXT,
                protocol TEXT,
                bandwidth INTEGER,
                flow_duration INTEGER,
                priority INTEGER,
                app_id TEXT,
                device_id TEXT
            );
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                event TEXT NOT NULL,
                score INTEGER NOT NULL,
                source_ip TEXT NOT NULL,
                destination_ip TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS actions (
                action_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                action_type TEXT NOT NULL,
                reason TEXT NOT NULL,
                source_ip TEXT NOT NULL,
                admin_or_automated TEXT NOT NULL
            );
            """
        )
        conn.commit()


def delete_event_entry(source_ip):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM events WHERE source_ip = ?", (source_ip,))
            conn.commit()
    except sqlite3.Error as exc:
        raise Exception(f"Database error: {exc}") from exc


def record_action(action_type, reason, source_ip, admin_or_automated):
    """Record an action taken to the actions table."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO actions (action_type, reason, source_ip, admin_or_automated)
                VALUES (?, ?, ?, ?);
                """,
                (
                    str(action_type),
                    str(reason),
                    str(source_ip or "N/A"),
                    str(admin_or_automated or "Admin"),
                ),
            )
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error as exc:
        raise Exception(f"Database error: {exc}") from exc


def get_actions():
    """Retrieve all actions from the actions table."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT timestamp, action_type, reason, source_ip, admin_or_automated
                FROM actions
                ORDER BY timestamp DESC;
                """
            )
            rows = cursor.fetchall()
            return [
                {
                    "timestamp": row[0],
                    "action_type": row[1],
                    "reason": row[2],
                    "source_ip": row[3],
                    "admin_or_automated": row[4],
                }
                for row in rows
            ]
    except sqlite3.Error as exc:
        raise Exception(f"Database error: {exc}") from exc


def save_event(data):
    """Save an event received from the webhook to the database."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO events (source, event, score, source_ip, destination_ip)
                VALUES (?, ?, ?, ?, ?);
                """,
                (
                    str(data.get("Source") or "Unknown"),
                    str(data.get("Event") or "Unknown"),
                    int(float(data.get("Score", 0))),
                    str(data.get("SourceIP") or "0.0.0.0"),
                    str(data.get("DestinationIP") or "0.0.0.0"),
                ),
            )
            conn.commit()
    except sqlite3.Error as exc:
        raise Exception(f"Database error: {exc}") from exc


def get_anomalies():
    """Retrieve recent anomalies from the events table."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT timestamp, source_ip, event, score
                FROM events
                ORDER BY timestamp DESC;
                """
            )
            rows = cursor.fetchall()
            return [
                {
                    "timestamp": row[0],
                    "source_ip": row[1],
                    "event": row[2],
                    "score": row[3],
                }
                for row in rows
            ]
    except sqlite3.Error as exc:
        raise Exception(f"Database error: {exc}") from exc


def save_settings(settings):
    """Save or update settings in the database."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            for key, value in settings.items():
                cursor.execute(
                    """
                    INSERT INTO settings (key, value)
                    VALUES (?, ?)
                    ON CONFLICT(key) DO UPDATE SET value=excluded.value;
                    """,
                    (str(key), str(value)),
                )
            conn.commit()
    except sqlite3.Error as exc:
        raise Exception(f"Database error: {exc}") from exc


def get_settings():
    """Retrieve all settings as a dictionary from the database."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM settings;")
            rows = cursor.fetchall()
            return {key: value for key, value in rows}
    except sqlite3.Error as exc:
        raise Exception(f"Database error: {exc}") from exc


def get_setting_value(key):
    """Retrieve a specific setting value by key from the database."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?;", (str(key),))
            row = cursor.fetchone()
            return row[0] if row else None
    except sqlite3.Error as exc:
        raise Exception(f"Database error: {exc}") from exc


def save_flows(flows):
    """Save or update flows data in the database."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM flows")
            for flow in flows:
                cursor.execute(
                    """
                    INSERT INTO flows (
                        id, source_ip, destination_ip, protocol, bandwidth,
                        flow_duration, priority, app_id, device_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        flow["id"],
                        flow.get("source_ip", "Unknown"),
                        flow.get("destination_ip", "Unknown"),
                        flow.get("protocol", "Unknown"),
                        flow.get("bandwidth", 0),
                        flow.get("flow_duration", 0),
                        flow.get("priority", 0),
                        flow.get("app_id", "Unknown"),
                        flow.get("device_id", "Unknown"),
                    ),
                )
            conn.commit()
    except sqlite3.Error as exc:
        raise Exception(f"Database error: {exc}") from exc


def get_flows():
    """Retrieve all flow data from the database."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, source_ip, destination_ip, protocol, bandwidth,
                       flow_duration, priority, app_id, device_id
                FROM flows;
                """
            )
            rows = cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "source_ip": row[1],
                    "destination_ip": row[2],
                    "protocol": row[3],
                    "bandwidth": row[4],
                    "flow_duration": row[5],
                    "priority": row[6],
                    "app_id": row[7],
                    "device_id": row[8],
                }
                for row in rows
            ]
    except sqlite3.Error as exc:
        raise Exception(f"Database error: {exc}") from exc
