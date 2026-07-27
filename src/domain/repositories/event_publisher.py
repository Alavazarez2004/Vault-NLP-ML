from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.dtos.nlp_analyze_response_dto import NLPAnalyzeResponseDTO


class EventPublisher(ABC):
    """
    Puerto para publicar eventos de vuelta al broker RabbitMQ.
    vault-ai-service es Publisher de nlp.analyzed: Community Service (Go)
    lo consume para actualizar is_visible y los scores en la BD.
    """

    @abstractmethod
    def publish_nlp_analyzed(
        self,
        source_id: UUID,
        source_type: str,
        result: NLPAnalyzeResponseDTO,
    ) -> None:
        raise NotImplementedError
