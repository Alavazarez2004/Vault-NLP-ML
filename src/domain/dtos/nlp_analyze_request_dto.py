from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class NLPAnalyzeRequestDTO(BaseModel):
    text: str
    source_id: UUID
    source_type: Literal["post", "comment", "review"]
