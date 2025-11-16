"""
Event Entity - Domain events and operational events

Represents significant events in the system (maintenance, failures, operations).
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID, uuid4


class EventType(str, Enum):
    """Event types"""

    MAINTENANCE = "maintenance"
    FAILURE = "failure"
    REPAIR = "repair"
    CALIBRATION = "calibration"
    INSPECTION = "inspection"
    STARTUP = "startup"
    SHUTDOWN = "shutdown"
    PARAMETER_CHANGE = "parameter_change"
    ALERT_TRIGGERED = "alert_triggered"
    ALERT_RESOLVED = "alert_resolved"


@dataclass
class Event:
    """
    Event entity

    Represents operational or domain events.
    Used for maintenance tracking, failure history, and audit trail.
    """

    id: UUID
    tenant_id: UUID
    site_id: UUID
    machine_id: UUID
    event_type: EventType
    title: str
    description: str
    occurred_at: datetime
    duration_minutes: Optional[int] = None
    performed_by: Optional[str] = None
    cost: Optional[float] = None
    related_alert_id: Optional[UUID] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @staticmethod
    def create(
        tenant_id: UUID,
        site_id: UUID,
        machine_id: UUID,
        event_type: EventType,
        title: str,
        description: str,
        occurred_at: Optional[datetime] = None,
        duration_minutes: Optional[int] = None,
        performed_by: Optional[str] = None,
        cost: Optional[float] = None,
        related_alert_id: Optional[UUID] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "Event":
        """Factory method to create a new event"""
        return Event(
            id=uuid4(),
            tenant_id=tenant_id,
            site_id=site_id,
            machine_id=machine_id,
            event_type=event_type,
            title=title,
            description=description,
            occurred_at=occurred_at or datetime.now(timezone.utc),
            duration_minutes=duration_minutes,
            performed_by=performed_by,
            cost=cost,
            related_alert_id=related_alert_id,
            metadata=metadata or {},
            created_at=datetime.now(timezone.utc),
        )
