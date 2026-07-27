from dataclasses import dataclass


@dataclass
class AssetFeatures:
    """
    Features extraídas de un asset individual del usuario. Se usan tanto
    para agregarse en el UserProfile como para reglas de recomendación
    puntuales (ej. recordatorio de mantenimiento de un asset específico).
    """

    asset_id: str
    category: str
    condition: str
    purchase_value: float
    age_days: int
    maintenance_count: int
    days_since_last_maintenance: int
    is_certified: bool

    def to_dict(self) -> dict:
        return {
            "asset_id": self.asset_id,
            "category": self.category,
            "condition": self.condition,
            "purchase_value": self.purchase_value,
            "age_days": self.age_days,
            "maintenance_count": self.maintenance_count,
            "days_since_last_maintenance": self.days_since_last_maintenance,
            "is_certified": self.is_certified,
        }
