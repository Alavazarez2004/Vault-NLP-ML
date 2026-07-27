import logging
from datetime import datetime, timedelta

from src.application.use_cases.training.retrain_with_real_users import RetrainWithRealUsers

logger = logging.getLogger(__name__)


class ScheduledNightlyRetrain:
    """
    Reentrenamiento batch nocturno: obtiene todos los usuarios con
    actividad en las últimas 24 horas y reentrena el modelo de
    segmentación incrementalmente con sus perfiles actualizados.
    Se ejecuta todos los días a las 2:00 AM.
    """

    def __init__(self, retrain: RetrainWithRealUsers) -> None:
        self._retrain = retrain

    def execute(self) -> None:
        since = (datetime.utcnow() - timedelta(hours=24)).isoformat()

        try:
            result = self._retrain.execute(updated_since=since)
        except FileNotFoundError as e:
            logger.warning("Reentrenamiento nocturno saltado: %s", e)
            return

        logger.info(
            "Reentrenamiento nocturno: %s (%d perfiles usados).",
            result["status"],
            result["n_profiles_used"],
        )
