from uuid import UUID

from pydantic import BaseModel


class RecommendationItemDTO(BaseModel):
    type: str
    reason: str
    asset_id: UUID | None = None
    message: str | None = None
