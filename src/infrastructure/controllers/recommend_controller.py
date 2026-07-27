from src.application.use_cases.realtime.get_recommendations import GetRecommendations
from src.domain.dtos.recommend_request_dto import RecommendRequestDTO
from src.domain.dtos.recommend_response_dto import RecommendResponseDTO


class RecommendController:
    """
    Controller: orquesta la petición HTTP de recomendaciones hacia el
    use case correspondiente. No contiene lógica de negocio, solo
    traduce DTO de entrada -> use case -> DTO de salida.
    """

    def __init__(self, get_recommendations: GetRecommendations) -> None:
        self._get_recommendations = get_recommendations

    def handle(self, request: RecommendRequestDTO) -> RecommendResponseDTO:
        segment, recommendations = self._get_recommendations.execute(request.user_id)
        return RecommendResponseDTO(
            user_id=request.user_id,
            segment=segment,
            recommendations=recommendations,
        )
