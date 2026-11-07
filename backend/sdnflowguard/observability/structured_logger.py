"""Structured JSON logger with correlation ID and secret masking."""

from __future__ import annotations

import json
import logging
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SECRET_KEY_PATTERNS = re.compile(
    r"(password|passwd|secret|token|api_key|authorization)",
    re.IGNORECASE,
)


def mask_sensitive_data(data: Any) -> Any:
    """Recursively mask sensitive fields in dicts/lists before logging."""
    if isinstance(data, dict):
        masked = {}
        for k, v in data.items():
            if SECRET_KEY_PATTERNS.search(str(k)):
                masked[k] = "***REDACTED***"
            else:
                masked[k] = mask_sensitive_data(v)
        return masked
    if isinstance(data, list):
        return [mask_sensitive_data(item) for item in data]
    return data


def generate_request_id() -> str:
    """Generate a unique request correlation ID."""
    return f"req-{uuid.uuid4().hex[:12]}"


class StructuredAuditLogger:
    """Structured audit logger that never writes on import time."""

    def __init__(self, log_file: Path | None = None):
        self._log_file = log_file
        self._logger = logging.getLogger("sdnflowguard.audit")
        self._logger.setLevel(logging.INFO)

    def log_event(
        self,
        event_type: str,
        *,
        level: str = "INFO",
        request_id: str | None = None,
        component: str = "backend",
        details: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        record = {
            "@timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level.upper(),
            "request_id": request_id or generate_request_id(),
            "component": component,
            "event_type": event_type,
            "details": mask_sensitive_data(details or {}),
        }
        if self._log_file is not None:
            try:
                self._log_file.parent.mkdir(parents=True, exist_ok=True)
                with self._log_file.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(record, ensure_ascii=False) + "\n")
            except Exception:
                pass
        return record

