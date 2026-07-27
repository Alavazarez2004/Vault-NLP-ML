import asyncio
import json
from uuid import UUID

import aio_pika

from src.domain.dtos.nlp_analyze_response_dto import NLPAnalyzeResponseDTO
from src.domain.repositories.event_publisher import EventPublisher
from src.infrastructure.config.settings import settings


class RabbitMQPublisher(EventPublisher):
    """
    Publisher de vault-ai-service: publica nlp.analyzed sobre el exchange
    topic vault.events, que Community Service (Go) consume para actualizar
    is_visible y los scores del post/comentario/reseña en la BD.
    """

    def publish_nlp_analyzed(
        self,
        source_id: UUID,
        source_type: str,
        result: NLPAnalyzeResponseDTO,
    ) -> None:
        payload = {
            "source_id": str(source_id),
            "source_type": source_type,
            **result.model_dump(mode="json"),
        }
        asyncio.run(self._publish(payload))

    async def _publish(self, payload: dict) -> None:
        connection = await aio_pika.connect_robust(settings.rabbitmq_url)
        try:
            channel = await connection.channel()
            exchange = await channel.declare_exchange(
                settings.rabbitmq_exchange, aio_pika.ExchangeType.TOPIC, durable=True
            )
            await exchange.publish(
                aio_pika.Message(body=json.dumps(payload).encode()),
                routing_key=settings.rabbitmq_publish_routing_key,
            )
        finally:
            await connection.close()
