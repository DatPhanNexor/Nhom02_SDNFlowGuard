"""API security and input validation helpers for HTTP endpoints."""

from __future__ import annotations

import hmac
import ipaddress
import re
from typing import Any

from sdnflowguard.domain.exceptions import ValidationError
from sdnflowguard.infrastructure.configuration.settings import AppSettings

DEVICE_ID_REGEX = re.compile(r"^of:[0-9a-fA-F]{16}$")


def check_api_key(headers: Any) -> tuple[bool, str | None]:
    """Validate X-SDNFlow-API-Key header when SDNFLOW_API_KEY is configured."""
    settings = AppSettings.from_env()
    configured_key = settings.api_key
    if not configured_key:
        return True, None

    provided = headers.get("X-SDNFlow-API-Key") or ""
    if not provided:
        auth_header = headers.get("Authorization") or ""
        if auth_header.lower().startswith("bearer "):
            provided = auth_header[7:].strip()

    if not provided or not hmac.compare_digest(str(provided), str(configured_key)):
        return False, "Unauthorized: valid X-SDNFlow-API-Key header is required."
    return True, None


def validate_ip_input(ip_val: Any, field_name: str = "ip") -> str:
    """Validate IPv4/IPv6 string or raise ValidationError."""
    if not isinstance(ip_val, str) or not ip_val.strip():
        raise ValidationError(f"Missing or empty '{field_name}' parameter.")
    try:
        return str(ipaddress.ip_address(ip_val.strip()))
    except ValueError as exc:
        raise ValidationError(f"Invalid IP address in '{field_name}': {ip_val!r}") from exc


def validate_device_id_input(device_id: Any) -> str:
    """Validate OpenFlow device ID (e.g. of:0000000000000001)."""
    if not isinstance(device_id, str) or not DEVICE_ID_REGEX.match(device_id.strip()):
        raise ValidationError(f"Invalid OpenFlow device_id: {device_id!r}")
    return device_id.strip().lower()


def validate_port_input(port_val: Any) -> str:
    """Validate switch port number (positive integer string)."""
    if port_val is None or isinstance(port_val, bool):
        raise ValidationError("Missing 'port' parameter.")
    s_val = str(port_val).strip()
    if not s_val.isdigit() or int(s_val) <= 0 or int(s_val) > 65535:
        raise ValidationError(f"Invalid switch port number: {port_val!r}")
    return s_val


def validate_rate_input(rate_val: Any) -> int:
    """Validate bandwidth limit rate (positive integer kbps/pps)."""
    if rate_val is None or isinstance(rate_val, bool):
        raise ValidationError("Missing 'rate' parameter.")
    try:
        parsed = int(rate_val)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"Invalid rate value: {rate_val!r}") from exc
    if parsed <= 0 or parsed > 10_000_000:
        raise ValidationError(f"Rate value out of valid range (1..10000000): {parsed}")
    return parsed

