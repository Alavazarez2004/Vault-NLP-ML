from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.recommendation_result import RecommendationResult


class RecommendationRepository(ABC):
    """
    Puerto para guardar y consultar resultados de segmentación/
    recomendación. La implementación real usa PostgreSQL (Supabase),
    conectando con service_role key.
    """

    @abstractmethod
    def save(self, result: RecommendationResult) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_all(self, limit: int = 100) -> list[RecommendationResult]:
        raise NotImplementedError

    @abstractmethod
    def get_by_user(self, user_id: UUID, limit: int = 100) -> list[RecommendationResult]:
        raise NotImplementedError
