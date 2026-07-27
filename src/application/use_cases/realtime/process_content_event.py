from src.application.use_cases.nlp.analyze_text import AnalyzeText
from src.domain.dtos.nlp_analyze_request_dto import NLPAnalyzeRequestDTO
from src.domain.dtos.user_event_dto import UserEventDTO
from src.domain.repositories.event_publisher import EventPublisher

EVENT_TO_SOURCE_TYPE = {
    "post.created": "post",
    "comment.created": "comment",
    "review.created": "review",
}


class ProcessContentEvent:
    """
    Use case: reacciona a post.created/comment.created/review.created
    corriendo el análisis NLP completo y publicando nlp.analyzed de
    vuelta, para que Community Service (Go) actualice is_visible y los
    scores en la BD.
    """

    def __init__(self, analyze_text: AnalyzeText, event_publisher: EventPublisher) -> None:
        self._analyze_text = analyze_text
        self._event_publisher = event_publisher

    def execute(self, event: UserEventDTO) -> None:
        source_type = EVENT_TO_SOURCE_TYPE[event.event_type]
        request = NLPAnalyzeRequestDTO(
            text=event.text or "",
            source_id=event.source_id,
            source_type=source_type,
        )
        result = self._analyze_text.execute(request)
        self._event_publisher.publish_nlp_analyzed(event.source_id, source_type, result)
