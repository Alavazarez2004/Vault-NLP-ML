import pandas as pd

MAINTENANCE_REMINDER_PERCENTILE = 75
HIGH_VALUE_PERCENTILE = 75


class TrainRecommendationModel:
    """
    Use case: deriva los umbrales usados por las reglas de recomendación
    ("K-Means + reglas") a partir de la distribución real de los datos
    de entrenamiento, en vez de usar constantes fijas en el código.

    Responsabilidad única: calcular umbrales. La lógica de qué
    recomendación disparar con cada umbral vive en GetRecommendations.
    """

    def execute(self, df: pd.DataFrame) -> dict:
        return {
            "maintenance_reminder_days": float(
                df["days_since_last_maintenance"].quantile(MAINTENANCE_REMINDER_PERCENTILE / 100)
            ),
            "high_value_threshold": float(
                df["avg_purchase_value"].quantile(HIGH_VALUE_PERCENTILE / 100)
            ),
        }
