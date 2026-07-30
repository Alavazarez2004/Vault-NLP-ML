import asyncio
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

# Alias claros para evitar colisión de nombres
from src.application.use_cases.nlp.analyze_sentiment import _get_pipeline as _get_analyze_sentiment_pipeline
from src.application.use_cases.nlp.detect_toxicity import (
    _get_hate_pipeline as _get_toxicity_hate_pipeline,
    _get_sentiment_pipeline as _get_toxicity_sentiment_pipeline,
)
from src.application.use_cases.nlp.detect_entities import _get_nlp as _get_spacy_nlp


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Precargando modelos de NLP (sentimiento, toxicidad, spaCy)...")
    _get_analyze_sentiment_pipeline()
    _get_toxicity_hate_pipeline()
    _get_toxicity_sentiment_pipeline()
    _get_spacy_nlp()
    print("Modelos de NLP listos.")

    consumer = RabbitMQConsumer(get_process_content_event(), get_process_user_event())
    consumer_task = asyncio.create_task(consumer.start())

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

    consumer_task.cancel()
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