from uuid import UUID

from src.application.use_cases.realtime.segment_user import SegmentUser
from src.domain.dtos.recommendation_item_dto import RecommendationItemDTO
from src.domain.repositories.model_repository import ModelRepository
from src.domain.repositories.recommendation_repository import RecommendationRepository
from src.domain.repositories.user_profile_repository import UserProfileRepository

RECOMMENDATION_THRESHOLDS_FILENAME = "recommendation_thresholds.pkl"

DEFAULT_THRESHOLDS = {"maintenance_reminder_days": 90.0, "high_value_threshold": 250.0}

SEGMENT_SERVICE_RECOMMENDATIONS: dict[str, list[dict]] = {
    "casual": [
        {"type": "service", "reason": "Usuarios similares empezaron registrando sus primeros assets con fotos y recibos."},
    ],
    "coleccionista": [
        {"type": "service", "reason": "Usuarios similares certifican sus assets de mayor valor en blockchain para reventa."},
        {"type": "service", "reason": "Usuarios similares usan servicios de restauración especializados para mantener el valor de su colección."},
    ],
    "enthusiast_restaurador": [
        {"type": "service", "reason": "Usuarios similares usan este servicio de limpieza recomendado por la comunidad."},
        {"type": "service", "reason": "Usuarios similares comparten tutoriales de mantenimiento en la comunidad VAULT."},
    ],
}


class GetRecommendations:
    """
    Use case: genera recomendaciones para un usuario combinando su
    segmento (K-Means) con reglas de negocio sobre su propio perfil.

    Responsabilidad única: orquestar segmentación + reglas. No entrena,
    no decide el segmento (delega a SegmentUser).
    """

    def __init__(
        self,
        segment_user: SegmentUser,
        model_repository: ModelRepository,
        user_profile_repository: UserProfileRepository,
        recommendation_repository: RecommendationRepository,
    ) -> None:
        self._segment_user = segment_user
        self._model_repository = model_repository
        self._user_profile_repository = user_profile_repository
        self._recommendation_repository = recommendation_repository

    def execute(self, user_id: UUID) -> tuple[str, list[RecommendationItemDTO]]:
        segment_result = self._segment_user.execute(user_id, persist=False)
        profile = self._user_profile_repository.get_profile(user_id)
        thresholds = self._load_thresholds()

        recommendations = [
            RecommendationItemDTO(**r) for r in SEGMENT_SERVICE_RECOMMENDATIONS.get(segment_result.segment_label, [])
        ]

        if profile.days_since_last_maintenance >= thresholds["maintenance_reminder_days"]:
            months = round(profile.days_since_last_maintenance / 30)
            recommendations.append(
                RecommendationItemDTO(
                    type="maintenance_reminder",
                    reason="Tu categoría más frecuente lleva tiempo sin mantenimiento registrado.",
                    message=f"Tus {profile.most_common_category} llevan {months} meses sin mantenimiento.",
                )
            )

        if profile.avg_purchase_value >= thresholds["high_value_threshold"] and segment_result.segment_label != "coleccionista":
            recommendations.append(
                RecommendationItemDTO(
                    type="service",
                    reason="Tus assets tienen un valor promedio alto: certifícalos en blockchain para protegerlos.",
                )
            )

        segment_result.recommendations = [r.model_dump(mode="json") for r in recommendations]
        self._recommendation_repository.save(segment_result)

        return segment_result.segment_label, recommendations

    def _load_thresholds(self) -> dict:
        if self._model_repository.exists(RECOMMENDATION_THRESHOLDS_FILENAME):
            return self._model_repository.load(RECOMMENDATION_THRESHOLDS_FILENAME)
        return DEFAULT_THRESHOLDS
