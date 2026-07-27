from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class UserEventDTO(BaseModel):
    """
    Payload de los eventos que vault-ai-service consume de RabbitMQ:
    post.created, comment.created, review.created (contenido a analizar
    con NLP) y asset.updated (dispara reprocesamiento silencioso del
    perfil ML del usuario).
    """

    event_type: Literal[
        "post.created",
        "comment.created",
        "review.created",
        "asset.updated",
    ]
    user_id: UUID
    source_id: UUID
    text: str | None = None
