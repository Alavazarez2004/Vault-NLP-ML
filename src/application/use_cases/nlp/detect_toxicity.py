from functools import lru_cache
import torch
from transformers import pipeline

HATE_MODEL = "pysentimiento/robertuito-hate-speech"
SENTIMENT_MODEL = "pysentimiento/robertuito-sentiment-analysis"


@lru_cache
def _get_hate_pipeline():
    return pipeline("text-classification", model=HATE_MODEL, top_k=None, torch_dtype=torch.float16)


@lru_cache
def _get_sentiment_pipeline():
    return pipeline("text-classification", model=SENTIMENT_MODEL, top_k=None, torch_dtype=torch.float16)


# Alias y helper a NIVEL DE MÓDULO (fuera de la clase)
_get_pipeline = _get_hate_pipeline


def warmup_pipelines():
    _get_hate_pipeline()
    _get_sentiment_pipeline()


class DetectToxicity:
    def execute(self, text: str) -> tuple[float, bool]:
        # 1. Evaluar Odio/Agresividad
        hate_scores = _get_hate_pipeline()(text, truncation=True)[0]
        hate_score = max(
            s["score"] for s in hate_scores if s["label"].lower() in ["hateful", "aggressive", "targeted"]
        )

        # 2. Evaluar Sentimiento
        sentiment_scores = _get_sentiment_pipeline()(text, truncation=True)[0]
        neg_score = next(s["score"] for s in sentiment_scores if s["label"].upper() == "NEG")

        # Es tóxico si el modelo de odio salta (>= 0.40) O si el sentimiento es fuertemente negativo (>= 0.85)
        is_toxic = (hate_score >= 0.40) or (neg_score >= 0.85)

        return max(hate_score, neg_score), is_toxic