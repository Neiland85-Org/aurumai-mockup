"""
Sensor Entity - Data collection points

Represents physical or virtual sensors attached to machines.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict
from uuid import UUID, uuid4


@dataclass
class SensorSpec:
    """Technical specifications of a sensor"""

    manufacturer: str | None = None
    model: str | None = None
    serial_number: str | None = None
    min_range: float | None = None
    max_range: float | None = None
    accuracy: float | None = None
    sampling_rate_hz: float | None = None


@dataclass
class Sensor:
    """
    Sensor entity

    Represents a sensor that collects telemetry from a machine.
    Each sensor measures a specific metric type.
    """

    id: UUID
    machine_id: UUID
    name: str
    sensor_type: str  # vibration, temperature, pressure, rpm, power, flow, co2, nox, etc.
    unit: str  # mm/s, °C, bar, rpm, kW, l/h, ppm, etc.
    protocol: str  # modbus, opcua, mqtt, lora, canbus, analog
    address: str | None = None  # Protocol-specific address/tag
    spec: SensorSpec = field(default_factory=SensorSpec)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def create(
        machine_id: UUID,
        name: str,
        sensor_type: str,
        unit: str,
        protocol: str,
        address: str | None = None,
        spec: SensorSpec | None = None,
    ) -> "Sensor":
        """Factory method to create a new sensor"""
        now = datetime.now(timezone.utc)
        return Sensor(
            id=uuid4(),
            machine_id=machine_id,
            name=name,
            sensor_type=sensor_type,
            unit=unit,
            protocol=protocol,
            address=address,
            spec=spec or SensorSpec(),
            created_at=now,
            updated_at=now,
            is_active=True,
            metadata={},
        )

    def calibrate(self, spec: SensorSpec) -> None:
        """Update sensor calibration"""
        self.spec = spec
        self.updated_at = datetime.now(timezone.utc)

    def deactivate(self) -> None:
        """Deactivate sensor"""
        self.is_active = False
        self.updated_at = datetime.now(timezone.utc)
