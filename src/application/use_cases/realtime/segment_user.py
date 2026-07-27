from uuid import UUID

from src.application.use_cases.feature_engineering.extract_user_features import ExtractUserFeatures
from src.domain.entities.recommendation_result import RecommendationResult
from src.domain.repositories.model_repository import ModelRepository
from src.domain.repositories.recommendation_repository import RecommendationRepository
from src.domain.repositories.user_profile_repository import UserProfileRepository

SEGMENTATION_MODEL_FILENAME = "kmeans_segmentation.pkl"
SEGMENTATION_SCALER_FILENAME = "scaler_segmentation.pkl"
CLUSTER_LABEL_MAP_FILENAME = "cluster_label_map.pkl"
MODEL_VERSION = "1.0.0"


class SegmentUser:
    """
    Use case: corre el modelo de segmentación ya entrenado sobre el
    perfil actual de un usuario, persiste el resultado y lo devuelve.

    Responsabilidad única: segmentación + persistencia. No entrena, no
    genera recomendaciones (eso lo hace GetRecommendations reutilizando
    este use case).
    """

    def __init__(
        self,
        model_repository: ModelRepository,
        user_profile_repository: UserProfileRepository,
        recommendation_repository: RecommendationRepository,
        feature_extractor: ExtractUserFeatures | None = None,
    ) -> None:
        self._model_repository = model_repository
        self._user_profile_repository = user_profile_repository
        self._recommendation_repository = recommendation_repository
        self._extractor = feature_extractor or ExtractUserFeatures()

    def execute(self, user_id: UUID, persist: bool = True) -> RecommendationResult:
        if not self._model_repository.exists(SEGMENTATION_MODEL_FILENAME):
            raise FileNotFoundError("Modelo de segmentación no entrenado todavía.")

        kmeans = self._model_repository.load(SEGMENTATION_MODEL_FILENAME)
        scaler = self._model_repository.load(SEGMENTATION_SCALER_FILENAME)
        cluster_label_map: dict[int, str] = self._model_repository.load(CLUSTER_LABEL_MAP_FILENAME)

        profile = self._user_profile_repository.get_profile(user_id)
        features = self._extractor.execute(profile)
        X_scaled = scaler.transform(features.reshape(1, -1))

        cluster_id = int(kmeans.predict(X_scaled)[0])
        cluster_distance = float(kmeans.transform(X_scaled)[0][cluster_id])
        segment_label = cluster_label_map[cluster_id]

        result = RecommendationResult(
            user_id=user_id,
            cluster_id=cluster_id,
            segment_label=segment_label,
            cluster_distance=round(cluster_distance, 4),
            model_version=MODEL_VERSION,
        )
        if persist:
            self._recommendation_repository.save(result)
        return result
