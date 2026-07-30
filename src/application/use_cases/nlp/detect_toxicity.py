from functools import lru_cache
import torch
from transformers import pipeline

# Modelo de IA multilingüe especializado en toxicidad general, insultos y AMENAZAS
TOXICITY_MODEL_NAME = "unitary/multilingual-toxic-xlm-roberta"
TOXICITY_THRESHOLD = 0.50


@lru_cache
def _get_pipeline():
    device = 0 if torch.cuda.is_available() else -1
    return pipeline(
        "text-classification",
        model=TOXICITY_MODEL_NAME,
        top_k=None,
        device=device,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    )


class DetectToxicity:
    """
    Detecta toxicidad de forma 100% semántica mediante Inteligencia Artificial.
    La red neuronal evalúa automáticamente: toxicidad, amenazas, insultos y severidad.
    """

    def execute(self, text: str) -> tuple[float, bool]:
        # 1. Inferencia del modelo de IA
        classifier = _get_pipeline()
        scores = classifier(text, truncation=True)[0]

        # 2. Extraemos el puntaje de las categorías nocivas que mide el modelo
        toxic_categories = ["toxic", "severe_toxic", "threat", "insult"]
        
        toxicity_score = round(
            max(
                s["score"]
                for s in scores
                if s["label"].lower() in toxic_categories
            ),
            4
        )

        # 3. La IA decide si supera el umbral de toxicidad
        is_toxic = toxicity_score >= TOXICITY_THRESHOLD

        print({
            "toxicity_score": toxicity_score,
            "is_toxic": is_toxic,
            "text": text,
            "evaluacion_ia": {s["label"]: round(s["score"], 4) for s in scores}
        })

        return toxicity_score, is_toxic