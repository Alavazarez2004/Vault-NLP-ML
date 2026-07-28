import asyncio
import json
import logging

import aio_pika

from src.application.use_cases.realtime.process_content_event import ProcessContentEvent
from src.application.use_cases.realtime.process_user_event import ProcessUserEvent
from src.domain.dtos.user_event_dto import UserEventDTO
from src.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)

CONTENT_EVENT_TYPES = {"post.created", "comment.created", "review.created"}


class RabbitMQConsumer:
    """
    Subscriber de vault-ai-service: escucha post.created, comment.created,
    review.created (publicados por Community Service) y asset.updated
    (publicado por Asset Service) sobre el exchange topic vault.events.
    """

    def __init__(
        self,
        process_content_event: ProcessContentEvent,
        process_user_event: ProcessUserEvent,
    ) -> None:
        self._process_content_event = process_content_event
        self._process_user_event = process_user_event
        self._connection: aio_pika.abc.AbstractRobustConnection | None = None

    # connect_robust reintenta la conexión inicial indefinidamente si el
    # broker no responde (es justo lo que significa "robust") -- sin este
    # timeout, un RABBITMQ_URL mal puesto o el broker caído cuelga el
    # startup para siempre. Ver también main.py: start() ahora corre en
    # background, así que esto ya no bloquea el arranque de la app, pero
    # igual necesita un límite para no quedarse reintentando en silencio
    # por horas sin que nadie se entere.
    CONNECT_TIMEOUT_SECONDS = 15

    async def start(self) -> None:
        try:
            self._connection = await asyncio.wait_for(
                aio_pika.connect_robust(settings.rabbitmq_url),
                timeout=self.CONNECT_TIMEOUT_SECONDS,
            )
        except Exception:
            logger.exception(
                "No se pudo conectar a RabbitMQ en %ss -- revisa RABBITMQ_URL. "
                "El servicio sigue arriba para NLP/ML por HTTP, pero no va a "
                "reaccionar a eventos (post.created, asset.updated, etc.) "
                "hasta el próximo reinicio con la conexión correcta.",
                self.CONNECT_TIMEOUT_SECONDS,
            )
            return

        channel = await self._connection.channel()
        await channel.set_qos(prefetch_count=1)

        exchange = await channel.declare_exchange(
            settings.rabbitmq_exchange, aio_pika.ExchangeType.TOPIC, durable=True
        )
        queue = await channel.declare_queue(settings.rabbitmq_consume_queue, durable=True)
        for routing_key in settings.rabbitmq_consume_routing_keys:
            await queue.bind(exchange, routing_key=routing_key)

        await queue.consume(self._handle_message)
        logger.info(
            "RabbitMQ consumer escuchando %s en queue %s",
            settings.rabbitmq_consume_routing_keys,
            settings.rabbitmq_consume_queue,
        )

    async def stop(self) -> None:
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
            logger.info("RabbitMQ consumer detenido.")

    async def _handle_message(self, message: aio_pika.IncomingMessage) -> None:
        async with message.process(requeue=False):
            try:
                data = json.loads(message.body)
                event = UserEventDTO(**data)
                loop = asyncio.get_event_loop()

                if event.event_type in CONTENT_EVENT_TYPES:
                    await loop.run_in_executor(None, self._process_content_event.execute, event)
                elif event.event_type == "asset.updated":
                    await loop.run_in_executor(None, self._process_user_event.execute, event)
            except Exception:
                logger.exception("Error procesando mensaje de RabbitMQ: %s", message.body)
