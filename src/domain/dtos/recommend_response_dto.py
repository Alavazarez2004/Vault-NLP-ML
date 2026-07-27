from uuid import UUID

from pydantic import BaseModel

from src.domain.dtos.recommendation_item_dto import RecommendationItemDTO


class RecommendResponseDTO(BaseModel):
    user_id: UUID
    segment: str
    recommendations: list[RecommendationItemDTO]
