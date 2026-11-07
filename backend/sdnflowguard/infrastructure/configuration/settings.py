"""Centralized, side-effect-free configuration loader for SDNFlowGuard."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from sdnflowguard.domain.models import DefenseMode

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_DB_PATH = PROJECT_ROOT / "database" / "sdnflowguard.db"


def _parse_bool(val: str | None, default: bool = False) -> bool:
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


def _parse_csv_set(val: str | None, default: tuple[str, ...] = ()) -> list[str]:
    if not val:
        return list(default)
    return [item.strip() for item in val.split(",") if item.strip()]


@dataclass(frozen=True)
class AppSettings:
    """Immutable application configuration resolved from environment variables."""

    flask_host: str = "127.0.0.1"
    flask_port: int = 5000
    flask_debug: bool = False
    db_path: Path = DEFAULT_DB_PATH
    onos_url: str = "http://127.0.0.1:8181/onos/v1"
    onos_user: str | None = None
    onos_password: str | None = None
    elk_url: str = "http://127.0.0.1:9200"
    elk_user: str | None = None
    elk_password: str | None = None
    logstash_host: str = "127.0.0.1"
    logstash_port: int = 18080
    defense_mode: str = DefenseMode.DRY_RUN.value
    allowlist_ips: list[str] = field(default_factory=lambda: ["127.0.0.1", "::1"])
    api_key: str | None = None
    openai_api_key: str | None = None

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> AppSettings:
        source = env if env is not None else os.environ
        raw_db = source.get("SDNFLOW_DB_PATH")
        db_path = Path(raw_db).resolve() if raw_db else DEFAULT_DB_PATH

        raw_mode = (source.get("SDNFLOW_DEFENSE_MODE") or DefenseMode.DRY_RUN.value).strip().upper()
        valid_modes = {m.value for m in DefenseMode}
        if raw_mode not in valid_modes:
            raw_mode = DefenseMode.DRY_RUN.value

        try:
            port = int(source.get("SDNFLOW_FLASK_PORT") or "5000")
        except ValueError:
            port = 5000

        try:
            ls_port = int(source.get("SDNFLOW_LOGSTASH_PORT") or "18080")
        except ValueError:
            ls_port = 18080

        return cls(
            flask_host=source.get("SDNFLOW_FLASK_HOST") or "127.0.0.1",
            flask_port=port,
            flask_debug=_parse_bool(source.get("SDNFLOW_FLASK_DEBUG"), default=False),
            db_path=db_path,
            onos_url=(source.get("SDNFLOW_ONOS_URL") or "http://127.0.0.1:8181/onos/v1").rstrip("/"),
            onos_user=source.get("SDNFLOW_ONOS_USER") or None,
            onos_password=source.get("SDNFLOW_ONOS_PASSWORD") or None,
            elk_url=(source.get("SDNFLOW_ELK_URL") or "http://127.0.0.1:9200").rstrip("/"),
            elk_user=source.get("SDNFLOW_ELK_USER") or None,
            elk_password=source.get("SDNFLOW_ELK_PASSWORD") or None,
            logstash_host=source.get("SDNFLOW_LOGSTASH_HOST") or "127.0.0.1",
            logstash_port=ls_port,
            defense_mode=raw_mode,
            allowlist_ips=_parse_csv_set(
                source.get("SDNFLOW_ALLOWLIST_IPS"),
                default=("127.0.0.1", "::1"),
            ),
            api_key=source.get("SDNFLOW_API_KEY") or None,
            openai_api_key=source.get("OPENAI_API_KEY") or None,
        )

    def to_safe_summary(self) -> dict[str, Any]:
        """Return configuration summary with all secrets masked."""
        return {
            "flask_host": self.flask_host,
            "flask_port": self.flask_port,
            "flask_debug": self.flask_debug,
            "db_path": str(self.db_path),
            "onos_url": self.onos_url,
            "onos_credentials_configured": bool(self.onos_user and self.onos_password),
            "elk_url": self.elk_url,
            "elk_credentials_configured": bool(self.elk_user and self.elk_password),
            "logstash_host": self.logstash_host,
            "logstash_port": self.logstash_port,
            "defense_mode": self.defense_mode,
            "allowlist_ips": list(self.allowlist_ips),
            "api_key_enabled": bool(self.api_key),
            "openai_api_key_configured": bool(self.openai_api_key),
        }

