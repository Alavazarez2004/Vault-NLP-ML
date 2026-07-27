import logging

from src.application.use_cases.realtime.segment_user import SegmentUser
from src.domain.dtos.user_event_dto import UserEventDTO

logger = logging.getLogger(__name__)


class ProcessUserEvent:
    """
    Use case: reacciona a asset.updated recalculando y persistiendo el
    segmento del usuario, sin notificarlo (actualización silenciosa del
    perfil ML, tal como describe la tabla de eventos de VAULT_CONTEXT).
    """

    def __init__(self, segment_user: SegmentUser) -> None:
        self._segment_user = segment_user

    def execute(self, event: UserEventDTO) -> None:
        try:
            self._segment_user.execute(event.user_id)
        except (FileNotFoundError, ValueError) as e:
            logger.warning("No se pudo actualizar el perfil ML de %s: %s", event.user_id, e)
