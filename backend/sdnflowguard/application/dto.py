"""Application DTOs for SDNFlowGuard."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class ControlActionRequestDTO:
    """DTO for manual or policy-triggered SDN control actions."""

    action_type: str
    ip_address: str | None = None
    device_id: str = "of:0000000000000001"
    port_number: str | None = None
    limit_rate: int | None = None
    honeypot_ip: str | None = None
    dry_run: bool | None = None
    operator_approved: bool = False
    manual_operator_override: bool = True
    test_only: bool = False
    request_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

