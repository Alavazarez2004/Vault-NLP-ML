from functools import lru_cache

import torch
from transformers import pipeline

TOXICITY_MODEL_NAME = "pysentimiento/robertuito-hate-speech"
TOXICITY_THRESHOLDS = {
    "hateful": 0.70,
    "aggressive": 0.65,
    "targeted": 0.60
}

@lru_cache
def _get_pipeline():
    return pipeline(
        "text-classification",
        model=TOXICITY_MODEL_NAME,
        top_k=None,
        torch_dtype=torch.float16,
    )


class DetectToxicity:
    """
    Use case: detecta discurso de odio/agresividad en un texto en
    español, usado para filtrar comentarios y posts de la comunidad.
    Responsabilidad única: toxicidad. El modelo es multi-etiqueta
    (hateful, aggressive, targeted); se usa el score máximo entre las
    tres como toxicity_score.
    """

    def execute(self, text: str) -> dict:
        scores = _get_pipeline()(text, truncation=True)[0]

        print(scores)

        toxic = False
        reason = None
        toxicity_score = 0.0


        for item in scores:

            label = item["label"]
            score = item["score"]

            # Guardamos el score más alto
            toxicity_score = max(toxicity_score, score)


            # Revisamos si supera el límite de esa categoría
            if label in TOXICITY_THRESHOLDS:

                if score >= TOXICITY_THRESHOLDS[label]:

                    toxic = True
                    reason = label



        return {
        "toxicity_score": round(toxicity_score, 4),
        "toxic": toxic,
        "allowed": not toxic,
        "reason": reason,
        "details": scores
    }