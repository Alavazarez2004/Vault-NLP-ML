from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI

from src.infrastructure.adapters.rabbitmq_consumer import RabbitMQConsumer
from src.infrastructure.config.settings import settings
from src.infrastructure.dependencies import (
    get_nightly_retrain_use_case,
    get_process_content_event,
    get_process_user_event,
)
from src.infrastructure.routes import (
    history_routes,
    ml_routes,
    nlp_routes,
    training_routes,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    consumer = RabbitMQConsumer(get_process_content_event(), get_process_user_event())
    await consumer.start()

    scheduler = AsyncIOScheduler()
    nightly_retrain = get_nightly_retrain_use_case()
    scheduler.add_job(
        nightly_retrain.execute,
        trigger=CronTrigger(hour=2, minute=0),
        id="nightly_retrain",
        name="Reentrenamiento nocturno 2AM",
        replace_existing=True,
    )
    scheduler.start()

    yield

    await consumer.stop()
    scheduler.shutdown()


app = FastAPI(
    title="VAULT AI Service",
    description=(
        "Microservicio de NLP y Machine Learning para VAULT: análisis de "
        "sentimiento/toxicidad/entidades/tópicos de la comunidad, y "
        "segmentación de usuarios con recomendaciones basadas en clusters."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
)

app.include_router(nlp_routes.router, prefix=settings.api_prefix)
app.include_router(ml_routes.router, prefix=settings.api_prefix)
app.include_router(training_routes.router, prefix=settings.api_prefix)
app.include_router(history_routes.router, prefix=settings.api_prefix)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
