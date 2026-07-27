from src.application.use_cases.realtime.recommend_catalog_items import RecommendCatalogItems
from src.domain.dtos.recommend_items_response_dto import RecommendItemsResponseDTO
from src.domain.dtos.recommend_request_dto import RecommendRequestDTO


class RecommendItemsController:
    """
    Controller: orquesta la petición HTTP de recomendación de
    artículos del catálogo hacia el use case correspondiente. No
    contiene lógica de negocio, solo traduce DTO de entrada -> use
    case -> DTO de salida.
    """

    def __init__(self, recommend_catalog_items: RecommendCatalogItems) -> None:
        self._recommend_catalog_items = recommend_catalog_items

    def handle(self, request: RecommendRequestDTO, top_n: int = 3) -> RecommendItemsResponseDTO:
        items = self._recommend_catalog_items.execute(request.user_id, top_n=top_n)
        return RecommendItemsResponseDTO(user_id=request.user_id, items=items)
