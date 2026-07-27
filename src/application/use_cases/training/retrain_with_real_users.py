import pandas as pd

from src.application.use_cases.feature_engineering.extract_user_features import FEATURE_NAMES
from src.application.use_cases.training.train_segmentation_model import derive_cluster_labels
from src.domain.repositories.model_repository import ModelRepository
from src.domain.repositories.user_profile_repository import UserProfileRepository

SEGMENTATION_MODEL_FILENAME = "kmeans_segmentation.pkl"
SEGMENTATION_SCALER_FILENAME = "scaler_segmentation.pkl"
CLUSTER_LABEL_MAP_FILENAME = "cluster_label_map.pkl"


class RetrainWithRealUsers:
    """
    Use case: reentrena incrementalmente el modelo de segmentación con
    perfiles de usuarios reales recién actualizados, sin descartar el
    conocimiento ganado durante el entrenamiento sintético inicial.

    Responsabilidad única: dado un rango de tiempo, obtener los
    UserProfile actualizados desde Supabase, hacer partial_fit del
    MiniBatchKMeans existente (el scaler NO se refitea, para mantener
    estable el espacio de features) y re-derivar el mapeo de etiquetas
    por si los centroides se movieron de posición.
    """

    def __init__(
        self,
        model_repository: ModelRepository,
        user_profile_repository: UserProfileRepository,
    ) -> None:
        self._model_repository = model_repository
        self._user_profile_repository = user_profile_repository

    def execute(self, updated_since: str | None = None) -> dict:
        if not self._model_repository.exists(SEGMENTATION_MODEL_FILENAME):
            raise FileNotFoundError(
                "No existe un modelo base de segmentación. Ejecuta el entrenamiento "
                "inicial con usuarios sintéticos antes de reentrenar incrementalmente."
            )

        profiles = self._user_profile_repository.get_all_profiles(updated_since=updated_since)
        if not profiles:
            return {"status": "no_profiles_to_retrain", "n_profiles_used": 0}

        df = pd.DataFrame([p.to_record() for p in profiles])
        X = df[FEATURE_NAMES].values

        kmeans = self._model_repository.load(SEGMENTATION_MODEL_FILENAME)
        scaler = self._model_repository.load(SEGMENTATION_SCALER_FILENAME)

        X_scaled = scaler.transform(X)
        kmeans.partial_fit(X_scaled)

        centroids_original = scaler.inverse_transform(kmeans.cluster_centers_)
        cluster_label_map = derive_cluster_labels(centroids_original)

        self._model_repository.save(kmeans, SEGMENTATION_MODEL_FILENAME)
        self._model_repository.save(cluster_label_map, CLUSTER_LABEL_MAP_FILENAME)

        return {"status": "model_updated", "n_profiles_used": len(profiles)}
