"""Domain exceptions for SDNFlowGuard."""


class SDNFlowGuardError(Exception):
    """Base domain exception for SDNFlowGuard."""

    def __init__(self, message: str, code: str = "DOMAIN_ERROR", details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class ValidationError(SDNFlowGuardError):
    """Raised when domain input validation fails."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, code="VALIDATION_ERROR", details=details)


class SafetyGateRejectedError(SDNFlowGuardError):
    """Raised when the Active Defense Safety Gate blocks an unsafe action."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, code="SAFETY_GATE_REJECTED", details=details)


class EvidenceCorrelationError(SDNFlowGuardError):
    """Raised when packet or topology evidence cannot be parsed or correlated."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, code="EVIDENCE_CORRELATION_ERROR", details=details)


class ExternalServiceUnavailableError(SDNFlowGuardError):
    """Raised when ONOS, Elasticsearch, or Logstash is unreachable."""

    def __init__(self, message: str, service: str = "EXTERNAL_SERVICE", details: dict | None = None):
        merged = {"service": service, **(details or {})}
        super().__init__(message, code="EXTERNAL_SERVICE_UNAVAILABLE", details=merged)

