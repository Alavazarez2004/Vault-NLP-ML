from src.application.use_cases.realtime.segment_user import SegmentUser
from src.domain.dtos.segment_request_dto import SegmentRequestDTO
from src.domain.dtos.segment_response_dto import SegmentResponseDTO


class SegmentController:
    """
    Controller: orquesta la petición HTTP de segmentación hacia el use
    case correspondiente. No contiene lógica de negocio, solo traduce
    DTO de entrada -> use case -> DTO de salida.
    """

    def __init__(self, segment_user: SegmentUser) -> None:
        self._segment_user = segment_user

    def handle(self, request: SegmentRequestDTO) -> SegmentResponseDTO:
        result = self._segment_user.execute(request.user_id)
        return SegmentResponseDTO(
            user_id=result.user_id,
            cluster_id=result.cluster_id,
            segment_label=result.segment_label,
            cluster_distance=result.cluster_distance,
        )
