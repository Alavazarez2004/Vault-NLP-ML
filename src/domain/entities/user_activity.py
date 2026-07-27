from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ActivityType(str, Enum):
    ASSET_CREATED = "asset_created"
    ASSET_UPDATED = "asset_updated"
    ASSET_DELETED = "asset_deleted"
    MAINTENANCE_REGISTERED = "maintenance_registered"
    POST_CREATED = "post_created"
    COMMENT_CREATED = "comment_created"
    POST_LIKED = "post_liked"
    REVIEW_CREATED = "review_created"


@dataclass
class UserActivity:
    """
    Evento de actividad de un usuario en VAULT, tal como llega desde
    RabbitMQ (publicado por Asset Service / Community Service). Es el
    input crudo que dispara el reprocesamiento silencioso del perfil ML
    o el análisis NLP de contenido de comunidad.
    """

    user_id: str
    activity_type: ActivityType
    timestamp: datetime
    metadata: dict = field(default_factory=dict)
