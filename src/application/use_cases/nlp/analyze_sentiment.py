from functools import lru_cache

import torch
from transformers import pipeline

SENTIMENT_MODEL_NAME = "pysentimiento/robertuito-sentiment-analysis"

LABEL_MAP = {
    "POS": "positivo",
    "NEU": "neutral",
    "NEG": "negativo",
}


@lru_cache
def _get_pipeline():
    # torch_dtype=float16 reduce a la mitad la memoria que ocupa el modelo
    # respecto a float32 (default). En CPU la inferencia es un poco más
    # lenta que en float32 puro, pero es necesario para caber en el límite
    # de memoria del plan (1 GB).
    return pipeline(
        "text-classification",
        model=SENTIMENT_MODEL_NAME,
        torch_dtype=torch.float16,
    )


class AnalyzeSentiment:
    """
    Use case: analiza el sentimiento de un texto en español (post,
    comentario o reseña) con un modelo Transformer entrenado en tweets
    en español (RoBERTuito). Responsabilidad única: sentimiento.
    """

    def execute(self, text: str) -> tuple[float, str]:
        result = _get_pipeline()(text, truncation=True)[0]
        label = LABEL_MAP.get(result["label"], result["label"].lower())
        return round(float(result["score"]), 4), label