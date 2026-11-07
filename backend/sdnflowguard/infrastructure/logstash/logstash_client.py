"""Logstash HTTP JSON publisher client."""

from __future__ import annotations

from typing import Any

import requests

from sdnflowguard.infrastructure.configuration.settings import AppSettings


class LogstashClient:
    """Client for publishing structured JSON events to Logstash HTTP input."""

    def __init__(self, timeout: int = 5):
        self._timeout = timeout

    def publish_event(self, payload: dict[str, Any]) -> dict[str, Any]:
        settings = AppSettings.from_env()
        url = f"http://{settings.logstash_host}:{settings.logstash_port}/"
        try:
            resp = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=self._timeout,
            )
            return {
                "published": 200 <= resp.status_code < 300,
                "status_code": resp.status_code,
            }
        except Exception as exc:
            return {
                "published": False,
                "error": str(exc),
            }

