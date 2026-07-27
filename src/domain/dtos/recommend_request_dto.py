from uuid import UUID

from pydantic import BaseModel


class RecommendRequestDTO(BaseModel):
    user_id: UUID
