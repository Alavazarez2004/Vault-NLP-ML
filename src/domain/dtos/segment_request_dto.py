from uuid import UUID

from pydantic import BaseModel


class SegmentRequestDTO(BaseModel):
    user_id: UUID
