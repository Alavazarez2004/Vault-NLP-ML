from functools import lru_cache

from src.application.use_cases.feature_engineering.extract_user_features import ExtractUserFeatures
from src.application.use_cases.inference.get_recommendation_history import GetRecommendationHistory
from src.application.use_cases.nlp.analyze_sentiment import AnalyzeSentiment
from src.application.use_cases.nlp.analyze_text import AnalyzeText
from src.application.use_cases.nlp.detect_entities import DetectEntities
from src.application.use_cases.nlp.detect_toxicity import DetectToxicity
from src.application.use_cases.nlp.model_topics import ModelTopics
from src.application.use_cases.realtime.get_recommendations import GetRecommendations
from src.application.use_cases.realtime.process_content_event import ProcessContentEvent
from src.application.use_cases.realtime.process_user_event import ProcessUserEvent
from src.application.use_cases.realtime.recommend_catalog_items import RecommendCatalogItems
from src.application.use_cases.realtime.segment_user import SegmentUser
from src.application.use_cases.training.retrain_with_real_users import RetrainWithRealUsers
from src.application.use_cases.training.scheduled_nightly_retrain import ScheduledNightlyRetrain
from src.infrastructure.adapters.joblib_model_repository import JoblibModelRepository
from src.infrastructure.adapters.postgres_recommendation_repository import (
    PostgresRecommendationRepository,
)
from src.infrastructure.adapters.postgres_user_collection_repository import (
    PostgresUserCollectionRepository,
)
from src.infrastructure.adapters.postgres_user_profile_repository import (
    PostgresUserProfileRepository,
)
from src.infrastructure.adapters.rabbitmq_publisher import RabbitMQPublisher
from src.infrastructure.adapters.static_catalog_repository import StaticCatalogRepository
from src.infrastructure.config.settings import settings
from src.infrastructure.controllers.history_controller import HistoryController
from src.infrastructure.controllers.nlp_controller import NLPController
from src.infrastructure.controllers.recommend_controller import RecommendController
from src.infrastructure.controllers.recommend_items_controller import RecommendItemsController
from src.infrastructure.controllers.segment_controller import SegmentController
from src.infrastructure.controllers.training_controller import TrainingController


@lru_cache
def get_model_repository() -> JoblibModelRepository:
    return JoblibModelRepository(settings.models_dir)


@lru_cache
def get_user_profile_repository() -> PostgresUserProfileRepository:
    return PostgresUserProfileRepository()


@lru_cache
def get_recommendation_repository() -> PostgresRecommendationRepository:
    return PostgresRecommendationRepository()


@lru_cache
def get_event_publisher() -> RabbitMQPublisher:
    return RabbitMQPublisher()


@lru_cache
def get_analyze_text() -> AnalyzeText:
    return AnalyzeText(
        analyze_sentiment=AnalyzeSentiment(),
        detect_toxicity=DetectToxicity(),
        detect_entities=DetectEntities(),
        model_topics=ModelTopics(get_model_repository()),
    )


def get_nlp_controller() -> NLPController:
    return NLPController(get_analyze_text())


@lru_cache
def get_segment_user() -> SegmentUser:
    return SegmentUser(
        model_repository=get_model_repository(),
        user_profile_repository=get_user_profile_repository(),
        recommendation_repository=get_recommendation_repository(),
        feature_extractor=ExtractUserFeatures(),
    )


def get_segment_controller() -> SegmentController:
    return SegmentController(get_segment_user())


def get_recommend_controller() -> RecommendController:
    use_case = GetRecommendations(
        segment_user=get_segment_user(),
        model_repository=get_model_repository(),
        user_profile_repository=get_user_profile_repository(),
        recommendation_repository=get_recommendation_repository(),
    )
    return RecommendController(use_case)


@lru_cache
def get_catalog_repository() -> StaticCatalogRepository:
    return StaticCatalogRepository()


@lru_cache
def get_user_collection_repository() -> PostgresUserCollectionRepository:
    return PostgresUserCollectionRepository(
        catalog_repository=get_catalog_repository(),
        segment_user=get_segment_user(),
    )


def get_recommend_items_controller() -> RecommendItemsController:
    use_case = RecommendCatalogItems(
        segment_user=get_segment_user(),
        catalog_repository=get_catalog_repository(),
        user_collection_repository=get_user_collection_repository(),
    )
    return RecommendItemsController(use_case)


@lru_cache
def get_process_content_event() -> ProcessContentEvent:
    return ProcessContentEvent(
        analyze_text=get_analyze_text(),
        event_publisher=get_event_publisher(),
    )


@lru_cache
def get_process_user_event() -> ProcessUserEvent:
    return ProcessUserEvent(segment_user=get_segment_user())


@lru_cache
def get_retrain_with_real_users() -> RetrainWithRealUsers:
    return RetrainWithRealUsers(
        model_repository=get_model_repository(),
        user_profile_repository=get_user_profile_repository(),
    )


def get_training_controller() -> TrainingController:
    return TrainingController(get_retrain_with_real_users())


def get_nightly_retrain_use_case() -> ScheduledNightlyRetrain:
    return ScheduledNightlyRetrain(get_retrain_with_real_users())


def get_history_controller() -> HistoryController:
    use_case = GetRecommendationHistory(get_recommendation_repository())
    return HistoryController(use_case)