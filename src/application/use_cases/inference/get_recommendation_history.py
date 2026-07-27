from uuid import UUID

from src.domain.entities.recommendation_result import RecommendationResult
from src.domain.repositories.recommendation_repository import RecommendationRepository


class GetRecommendationHistory:
    """
    Use case: consulta el historial de segmentaciones/recomendaciones
    almacenadas en la BD, con filtros opcionales.

    Responsabilidad única: lectura del historial. No corre modelos,
    no persiste nada.
    """

    def __init__(self, recommendation_repository: RecommendationRepository) -> None:
        self._repository = recommendation_repository

    def get_all(self, limit: int = 100) -> list[RecommendationResult]:
        return self._repository.get_all(limit=limit)

    def get_by_user(self, user_id: UUID, limit: int = 100) -> list[RecommendationResult]:
        return self._repository.get_by_user(user_id, limit=limit)
