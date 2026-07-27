from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class UserProfile:
    """
    Perfil de comportamiento de un usuario VAULT, construido a partir de
    sus assets, mantenimientos y actividad en la comunidad. Es el input
    para segmentación (K-Means/DBSCAN) y recomendaciones.
    """

    user_id: UUID
    total_assets: int
    categories: dict[str, int]
    avg_purchase_value: float
    maintenance_frequency: float
    community_activity: float
    days_since_last_maintenance: int
    most_common_category: str
    condition_distribution: dict[str, int]
    id: UUID = field(default_factory=uuid4)

    def to_record(self) -> dict:
        """Aplana el perfil a un registro numérico, listo para feature engineering."""
        return {
            "user_id": str(self.user_id),
            "total_assets": self.total_assets,
            "avg_purchase_value": self.avg_purchase_value,
            "maintenance_frequency": self.maintenance_frequency,
            "community_activity": self.community_activity,
            "days_since_last_maintenance": self.days_since_last_maintenance,
            "n_categories": len(self.categories),
            "pct_nuevo": self._condition_pct("nuevo"),
            "pct_seminuevo": self._condition_pct("seminuevo"),
            "pct_usado": self._condition_pct("usado"),
        }

    def _condition_pct(self, condition: str) -> float:
        total = sum(self.condition_distribution.values())
        if total == 0:
            return 0.0
        return self.condition_distribution.get(condition, 0) / total
