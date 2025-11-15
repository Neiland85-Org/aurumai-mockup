from typing import List, Dict, Any, Optional

class FeatureCalculator:
    """
    Clase pura y testeable para la ingeniería de características.
    No tiene estado y no sabe nada de MQTT, buffers o redes.
    Su única responsabilidad es transformar datos crudos en features.
    """
    @staticmethod
    def calculate_rolling_features(
        data_points: List[Dict[str, Any]], window_size: int = 10
    ) -> Dict[str, Optional[float]]:
        """
        Calcula características de ventana deslizante (rolling features) para un conjunto de datos.
        """

        # Import diferido para evitar errores de importación en entornos donde
        # aún no está instalada la dependencia (útil para Pylance en VS Code).
        import pandas as pd  # type: ignore

        if len(data_points) < window_size:
            return {}

        df = pd.DataFrame(data_points)
        
        # Lógica de feature engineering completamente aislada
        rolling_avg = df['value'].rolling(window=window_size).mean().iloc[-1]
        rolling_std = df['value'].rolling(window=window_size).std().iloc[-1]

        return {
            "rolling_avg_10": rolling_avg if pd.notna(rolling_avg) else None,
            "rolling_std_10": rolling_std if pd.notna(rolling_std) else None,
        }