from src.application.use_cases.nlp.analyze_sentiment import AnalyzeSentiment
from src.application.use_cases.nlp.detect_entities import DetectEntities
from src.application.use_cases.nlp.detect_toxicity import DetectToxicity
from src.application.use_cases.nlp.model_topics import ModelTopics
from src.domain.dtos.nlp_analyze_request_dto import NLPAnalyzeRequestDTO
from src.domain.dtos.nlp_analyze_response_dto import NLPAnalyzeResponseDTO


class AnalyzeText:
    """
    Use case orquestador: corre sentimiento, toxicidad, entidades y
    tópicos sobre un mismo texto y arma la respuesta de
    POST /api/v1/nlp/analyze. No contiene lógica de NLP propia -- delega
    cada análisis a su use case especializado.
    """

    def __init__(
        self,
        analyze_sentiment: AnalyzeSentiment,
        detect_toxicity: DetectToxicity,
        detect_entities: DetectEntities,
        model_topics: ModelTopics,
    ) -> None:
        self._analyze_sentiment = analyze_sentiment
        self._detect_toxicity = detect_toxicity
        self._detect_entities = detect_entities
        self._model_topics = model_topics

    def execute(self, request: NLPAnalyzeRequestDTO) -> NLPAnalyzeResponseDTO:
        sentiment_score, sentiment_label = self._analyze_sentiment.execute(request.text)
        toxicity_score, is_toxic = self._detect_toxicity.execute(request.text)
        entities = self._detect_entities.execute(request.text)
        topics = self._model_topics.execute(request.text)

        return NLPAnalyzeResponseDTO(
            sentiment_score=sentiment_score,
            sentiment_label=sentiment_label,
            toxicity_score=toxicity_score,
            is_toxic=is_toxic,
            entities=entities,
            topics=topics,
        )
