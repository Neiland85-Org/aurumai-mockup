from collections import deque
from typing import List, Dict, Any, Optional

# Import robusto para funcionar tanto en ejecución directa del repo
# como en layouts tipo "src/". Si no existe el módulo en src.domain,
# se hace fallback al módulo local en la raíz del proyecto.
try:
    from src.domain.feature_calculator import FeatureCalculator  # type: ignore
except ImportError:  # pragma: no cover - ruta alternativa para VS Code/Pylance
    from feature_calculator import FeatureCalculator

class MachineDataBuffer:
    """
    Gestiona el estado (el buffer de datos) para una única máquina.
    Encapsula la lógica de almacenamiento temporal.
    """
    def __init__(self, max_size: int = 100):
        self._buffer: deque = deque(maxlen=max_size)

    def add(self, data_point: Dict[str, Any]) -> None:
        """Añade un nuevo punto de telemetría al buffer."""
        self._buffer.append(data_point)

    def get_all(self) -> List[Dict[str, Any]]:
        """Devuelve todos los puntos de datos actuales como una lista."""
        return list(self._buffer)

    @property
    def size(self) -> int:
        """Devuelve el tamaño actual del buffer."""
        return len(self._buffer)

class EdgeProcessor:
    """
    Orquesta el flujo de datos para todas las máquinas. Es el "caso de uso" del edge-sim.
    No sabe nada de MQTT; solo recibe datos y devuelve resultados enriquecidos.
    """
    def __init__(self, window_size: int = 10):
        self._buffers: Dict[str, MachineDataBuffer] = {}
        self._window_size = window_size

    def _get_or_create_buffer(self, machine_id: str) -> MachineDataBuffer:
        if machine_id not in self._buffers:
            print(f"🔧 Creando nuevo buffer para la máquina: {machine_id}")
            self._buffers[machine_id] = MachineDataBuffer()
        return self._buffers[machine_id]

    def process_telemetry(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Procesa un punto de telemetría. Si hay suficientes datos, calcula y añade las features.
        """
        machine_id = data.get("machine_id")
        if not machine_id:
            return None

        buffer = self._get_or_create_buffer(machine_id)
        buffer.add(data)

        if buffer.size < self._window_size:
            return None  # No hay suficientes datos, no se calculan features

        features = FeatureCalculator.calculate_rolling_features(
            data_points=buffer.get_all(),
            window_size=self._window_size
        )

        if not features:
            return None

        # Devuelve el payload original enriquecido con las nuevas características
        return {**data, "features": features}