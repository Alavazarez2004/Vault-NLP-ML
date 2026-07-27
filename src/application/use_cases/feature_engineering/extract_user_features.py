import numpy as np

from src.domain.entities.user_profile import UserProfile

FEATURE_NAMES = [
    "total_assets",
    "avg_purchase_value",
    "maintenance_frequency",
    "community_activity",
    "days_since_last_maintenance",
    "n_categories",
    "pct_nuevo",
    "pct_seminuevo",
    "pct_usado",
]


class ExtractUserFeatures:
    """
    Use case: convierte un UserProfile en el vector numérico usado por
    K-Means/DBSCAN. Responsabilidad única: feature engineering para
    segmentación. El orden de FEATURE_NAMES debe mantenerse estable
    entre entrenamiento e inferencia.
    """

    def execute(self, profile: UserProfile) -> np.ndarray:
        record = profile.to_record()
        return np.array([record[name] for name in FEATURE_NAMES], dtype=np.float64)
