"""ONOS REST API client with lazy credential loading and rule verification."""

from __future__ import annotations

from typing import Any

import requests
from requests.auth import HTTPBasicAuth

from sdnflowguard.domain.exceptions import ExternalServiceUnavailableError
from sdnflowguard.infrastructure.configuration.settings import AppSettings


class ONOSClient:
    """Client for ONOS v1 REST API with zero import-time side effects."""

    def __init__(
        self,
        *,
        base_url: str | None = None,
        user: str | None = None,
        password: str | None = None,
        timeout: int = 10,
    ):
        self._explicit_base_url = base_url
        self._explicit_user = user
        self._explicit_password = password
        self._timeout = timeout

    def _resolve_config(self, controller_ip_override: str | None = None) -> tuple[str, HTTPBasicAuth]:
        settings = AppSettings.from_env()
        user = self._explicit_user or settings.onos_user
        password = self._explicit_password or settings.onos_password
        if not user or not password:
            raise ExternalServiceUnavailableError(
                "ONOS credentials are not configured (set SDNFLOW_ONOS_USER and SDNFLOW_ONOS_PASSWORD)",
                service="ONOS",
            )
        if self._explicit_base_url:
            base_url = self._explicit_base_url.rstrip("/")
        elif controller_ip_override:
            base_url = f"http://{controller_ip_override}:8181/onos/v1"
        else:
            base_url = settings.onos_url.rstrip("/")
        return base_url, HTTPBasicAuth(user, password)

    def get_json(self, path: str, controller_ip_override: str | None = None) -> dict[str, Any]:
        base_url, auth = self._resolve_config(controller_ip_override)
        url = f"{base_url}/{path.lstrip('/')}"
        try:
            resp = requests.get(
                url,
                auth=auth,
                headers={"Accept": "application/json"},
                timeout=self._timeout,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            raise ExternalServiceUnavailableError(
                f"Failed to query ONOS GET {path}: {exc}",
                service="ONOS",
            ) from exc

    def get_topology_snapshot(self, device_id: str = "of:0000000000000001") -> dict[str, Any]:
        devices = self.get_json("devices").get("devices") or []
        ports = self.get_json(f"devices/{device_id}/ports").get("ports") or []
        hosts = self.get_json("hosts").get("hosts") or []
        flows = self.get_json(f"flows/{device_id}").get("flows") or []
        return {
            "devices": devices,
            "ports": ports,
            "hosts": hosts,
            "flows": flows,
        }

    def verify_ip_flow_rule_present(
        self,
        ip_address: str,
        *,
        device_id: str = "of:0000000000000001",
        controller_ip_override: str | None = None,
    ) -> dict[str, Any]:
        """Verify whether an IPV4_SRC flow rule for ip_address is present on ONOS."""
        target_cidr = f"{ip_address}/32" if "/" not in ip_address else ip_address
        try:
            flows_resp = self.get_json(
                f"flows/{device_id}",
                controller_ip_override=controller_ip_override,
            )
            flows = flows_resp.get("flows") or []
            matched = []
            for flow in flows:
                criteria = (flow.get("selector") or {}).get("criteria") or []
                if any(
                    c.get("type") in ("IPV4_SRC", "IPV6_SRC") and c.get("ip") == target_cidr
                    for c in criteria
                ):
                    matched.append(
                        {
                            "flow_id": flow.get("id"),
                            "state": flow.get("state"),
                            "priority": flow.get("priority"),
                            "appId": flow.get("appId"),
                        }
                    )
            return {
                "verified": bool(matched),
                "device_id": device_id,
                "target_cidr": target_cidr,
                "matching_flow_count": len(matched),
                "matching_flows": matched,
            }
        except Exception as exc:
            return {
                "verified": False,
                "device_id": device_id,
                "target_cidr": target_cidr,
                "matching_flow_count": 0,
                "matching_flows": [],
                "error": str(exc),
            }

