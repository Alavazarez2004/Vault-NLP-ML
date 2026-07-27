from fastapi import APIRouter, Depends

from src.domain.dtos.nlp_analyze_request_dto import NLPAnalyzeRequestDTO
from src.domain.dtos.nlp_analyze_response_dto import NLPAnalyzeResponseDTO
from src.infrastructure.controllers.nlp_controller import NLPController
from src.infrastructure.dependencies import get_nlp_controller

router = APIRouter(prefix="/nlp", tags=["NLP"])


@router.post("/analyze", response_model=NLPAnalyzeResponseDTO)
def analyze(
    request: NLPAnalyzeRequestDTO,
    controller: NLPController = Depends(get_nlp_controller),
) -> NLPAnalyzeResponseDTO:
    return controller.handle(request)
