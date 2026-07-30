from pydantic import BaseModel

from src.domain.dtos.entity_dto import EntityDTO


class NLPAnalyzeResponseDTO(BaseModel):
    sentiment_score: float
    sentiment_label: str
    toxicity_score: float
    is_toxic: bool
    entities: list[EntityDTO]
    topics: list[str]
