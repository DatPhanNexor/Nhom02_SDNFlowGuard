"""Domain models and value objects for SDNFlowGuard."""

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class DefenseMode(str, Enum):
    """Supported operational defense modes."""

    DRY_RUN = "DRY_RUN"
    AUTO_STAGE_ONLY = "AUTO_STAGE_ONLY"
    MANUAL_APPROVAL = "MANUAL_APPROVAL"
    ACTIVE_ENFORCEMENT = "ACTIVE_ENFORCEMENT"


class DefenseLifecycleState(str, Enum):
    """State machine for controlled active defense lifecycle."""

    NORMAL = "NORMAL"
    ANOMALY_OBSERVED = "ANOMALY_OBSERVED"
    EVIDENCE_CORRELATED = "EVIDENCE_CORRELATED"
    BLOCK_PROPOSED = "BLOCK_PROPOSED"
    BLOCK_APPROVED = "BLOCK_APPROVED"
    RULE_APPLIED = "RULE_APPLIED"
    RULE_VERIFIED = "RULE_VERIFIED"
    ROLLBACK_OR_EXPIRED = "ROLLBACK_OR_EXPIRED"


class PolicyDecisionType(str, Enum):
    """Decisions emitted by the defense policy engine."""

    ALLOW = "ALLOW"
    OBSERVE = "OBSERVE"
    PROPOSE_BLOCK = "PROPOSE_BLOCK"


class CorrelationStatus(str, Enum):
    """Step 64 ONOS host evidence correlation statuses."""

    CORROBORATED_HOST_OBSERVATION = "CORROBORATED_HOST_OBSERVATION"
    AMBIGUOUS_MULTI_HOST = "AMBIGUOUS_MULTI_HOST"
    HOST_IDENTITY_MISMATCH = "HOST_IDENTITY_MISMATCH"
    UNREGISTERED_HOST_ON_PORT = "UNREGISTERED_HOST_ON_PORT"
    PORT_UNAVAILABLE_OR_DISABLED = "PORT_UNAVAILABLE_OR_DISABLED"
    DEVICE_UNAVAILABLE = "DEVICE_UNAVAILABLE"
    INVALID_EVIDENCE_DATA = "INVALID_EVIDENCE_DATA"


@dataclass(frozen=True)
class CaptureMetadata:
    """Standardized capture metadata for packet evidence."""

    capture_started_utc: str | None = None
    capture_finished_utc: str | None = None
    capture_sha256: str | None = None
    switch_id: str = "of:0000000000000001"
    interfaces: list[str] = field(default_factory=list)
    operator_note: str | None = None

    def has_full_utc_window(self) -> bool:
        return bool(self.capture_started_utc and self.capture_finished_utc)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PacketObservation:
    """Single switch ingress packet observation from Step 63/64."""

    switch_id: str
    ingress_port: str
    interface: str
    observed_source_mac: str
    observed_source_ip: str
    observed_destination_ip: str
    protocol: str
    icmp_type: str
    packet_count: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class HostCorrelationResult:
    """Result of correlating a packet observation against ONOS topology."""

    switch_id: str
    ingress_port: str
    interface: str
    observed_source_mac: str
    observed_source_ip: str
    observed_destination_ip: str
    protocol: str
    icmp_type: str
    packet_count: int
    device_present: bool
    port_present: bool
    port_enabled: bool
    attached_host_count: int
    attached_hosts: list[dict[str, Any]]
    mac_matched: bool
    ip_matched: bool
    ip_source_flow_count: int
    correlation_status: str
    topology_corroborated: bool
    attacker_confirmed: bool
    historical_alert_correlation_verified: bool
    recommended_decision: str
    automatic_block_allowed: bool
    rationale: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SafetyGateVerdict:
    """Verdict returned by the Active Defense Safety Gate."""

    allowed_to_execute: bool
    defense_mode: str
    lifecycle_state: str
    action_type: str
    target_ip: str | None
    target_device_id: str | None
    target_port: str | None
    dry_run: bool
    requires_manual_approval: bool
    rejection_reasons: list[str]
    safety_checks: dict[str, bool]
    rollback_plan: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

