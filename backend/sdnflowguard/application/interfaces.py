"""Port/Interface protocols for SDNFlowGuard application layer."""

from __future__ import annotations

from typing import Any, Protocol


class PersistencePort(Protocol):
    """Protocol for persistence repository operations."""

    def get_setting(self, key: str) -> str | None:
        ...

    def set_setting(self, key: str, value: Any) -> None:
        ...

    def store_action(self, action: str, details: str | dict[str, Any]) -> int:
        ...

    def store_event(self, event_type: str, details: dict[str, Any], timestamp: str | None = None) -> None:
        ...

