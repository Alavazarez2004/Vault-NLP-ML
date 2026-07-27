from uuid import UUID

from pydantic import BaseModel

from src.domain.dtos.recommended_item_dto import RecommendedItemDTO


class RecommendItemsResponseDTO(BaseModel):
    user_id: UUID
    items: list[RecommendedItemDTO]
