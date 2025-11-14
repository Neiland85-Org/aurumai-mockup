"""
Domain Entity: Machine
Represents a monitored industrial machine/equipment
"""

from dataclasses import dataclass


@dataclass
class Machine:
    """
    Machine domain entity.
    Represents industrial equipment being monitored (trucks, mills, boilers, etc.)
    """

    machine_id: str
    machine_type: str
    location: str
    operational: bool = True

    def __post_init__(self):
        """Validate machine data"""
        if not self.machine_id or not self.machine_id.strip():
            raise ValueError("machine_id cannot be empty")
        if not self.machine_type or not self.machine_type.strip():
            raise ValueError("machine_type cannot be empty")
        if not self.location or not self.location.strip():
            raise ValueError("location cannot be empty")

    def is_operational(self) -> bool:
        """Check if machine is operational"""
        return self.operational

    def mark_operational(self):
        """Mark machine as operational"""
        self.operational = True

    def mark_down(self):
        """Mark machine as down/offline"""
        self.operational = False
