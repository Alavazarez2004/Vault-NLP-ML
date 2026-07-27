from src.application.use_cases.training.retrain_with_real_users import RetrainWithRealUsers


class TrainingController:
    """
    Controller: expone un trigger manual (admin) del reentrenamiento
    incremental, además del scheduler nocturno automático.
    """

    def __init__(self, retrain_with_real_users: RetrainWithRealUsers) -> None:
        self._retrain = retrain_with_real_users

    def handle_retrain(self, updated_since: str | None = None) -> dict:
        return self._retrain.execute(updated_since=updated_since)
