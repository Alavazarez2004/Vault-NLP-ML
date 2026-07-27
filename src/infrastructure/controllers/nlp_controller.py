from src.application.use_cases.nlp.analyze_text import AnalyzeText
from src.domain.dtos.nlp_analyze_request_dto import NLPAnalyzeRequestDTO
from src.domain.dtos.nlp_analyze_response_dto import NLPAnalyzeResponseDTO


class NLPController:
    """
    Controller: orquesta la petición HTTP de análisis NLP hacia el use
    case correspondiente. No contiene lógica de negocio, solo traduce
    DTO de entrada -> use case -> DTO de salida.
    """

    def __init__(self, analyze_text: AnalyzeText) -> None:
        self._analyze_text = analyze_text

    def handle(self, request: NLPAnalyzeRequestDTO) -> NLPAnalyzeResponseDTO:
        return self._analyze_text.execute(request)
