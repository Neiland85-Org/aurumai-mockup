"""
Sensor Entity - Data collection points

Represents physical or virtual sensors attached to machines.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4


@dataclass
class SensorSpec:
    """Technical specifications of a sensor"""

    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    min_range: Optional[float] = None
    max_range: Optional[float] = None
    accuracy: Optional[float] = None
    sampling_rate_hz: Optional[float] = None


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
    sensor_type: (
        str  # vibration, temperature, pressure, rpm, power, flow, co2, nox, etc.
    )
    unit: str  # mm/s, °C, bar, rpm, kW, l/h, ppm, etc.
    protocol: str  # modbus, opcua, mqtt, lora, canbus, analog
    address: Optional[str] = None  # Protocol-specific address/tag
    spec: SensorSpec = field(default_factory=SensorSpec)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def create(
        machine_id: UUID,
        name: str,
        sensor_type: str,
        unit: str,
        protocol: str,
        address: Optional[str] = None,
        spec: Optional[SensorSpec] = None,
    ) -> "Sensor":
        """Factory method to create a new sensor"""
        now = datetime.utcnow()
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
        self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Deactivate sensor"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
