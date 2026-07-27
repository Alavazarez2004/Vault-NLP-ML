from uuid import UUID

from src.application.use_cases.inference.get_recommendation_history import GetRecommendationHistory


class HistoryController:
    """
    Controller: orquesta las consultas de historial de segmentación/
    recomendaciones hacia el use case correspondiente.
    """

    def __init__(self, get_recommendation_history: GetRecommendationHistory) -> None:
        self._use_case = get_recommendation_history

    def get_all(self, limit: int = 100) -> list[dict]:
        return [r.to_dict() for r in self._use_case.get_all(limit=limit)]

    def get_by_user(self, user_id: UUID, limit: int = 100) -> list[dict]:
        return [r.to_dict() for r in self._use_case.get_by_user(user_id, limit=limit)]
