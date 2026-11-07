"""Elasticsearch HTTP client with no hardcoded secrets."""

from __future__ import annotations

from typing import Any

import requests
from requests.auth import HTTPBasicAuth

from sdnflowguard.infrastructure.configuration.settings import AppSettings


class ElasticsearchClient:
    """Read/search client for Elasticsearch without hardcoded credentials."""

    def __init__(self, timeout: int = 10):
        self._timeout = timeout

    def _resolve_auth(self) -> tuple[str, HTTPBasicAuth | None]:
        settings = AppSettings.from_env()
        auth = (
            HTTPBasicAuth(settings.elk_user, settings.elk_password)
            if settings.elk_user and settings.elk_password
            else None
        )
        return settings.elk_url.rstrip("/"), auth

    def check_health(self) -> dict[str, Any]:
        base_url, auth = self._resolve_auth()
        try:
            resp = requests.get(
                f"{base_url}/_cluster/health",
                auth=auth,
                timeout=self._timeout,
            )
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "reachable": True,
                    "status": data.get("status", "unknown"),
                    "cluster_name": data.get("cluster_name"),
                }
            return {"reachable": False, "status_code": resp.status_code}
        except Exception as exc:
            return {"reachable": False, "error": str(exc)}

