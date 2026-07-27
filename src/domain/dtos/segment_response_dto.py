from uuid import UUID

from pydantic import BaseModel


class SegmentResponseDTO(BaseModel):
    user_id: UUID
    cluster_id: int
    segment_label: str
    cluster_distance: float
