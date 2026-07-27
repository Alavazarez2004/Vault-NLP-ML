from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class RecommendationResult:
    """
    Resultado persistido de segmentar a un usuario y, opcionalmente,
    generarle recomendaciones. Es el equivalente VAULT de una inferencia:
    se guarda para auditoría/historial y para no recalcular el segmento
    en cada request de recomendaciones.
    """

    user_id: UUID
    cluster_id: int
    segment_label: str
    cluster_distance: float
    model_version: str
    recommendations: list[dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    id: UUID = field(default_factory=uuid4)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "cluster_id": self.cluster_id,
            "segment_label": self.segment_label,
            "cluster_distance": self.cluster_distance,
            "model_version": self.model_version,
            "recommendations": self.recommendations,
            "created_at": self.created_at.isoformat(),
        }
