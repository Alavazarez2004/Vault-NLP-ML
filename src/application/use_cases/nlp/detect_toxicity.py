from functools import lru_cache

from transformers import pipeline

TOXICITY_MODEL_NAME = "pysentimiento/robertuito-hate-speech"
TOXICITY_THRESHOLD = 0.5


@lru_cache
def _get_pipeline():
    return pipeline(
        "text-classification",
        model=TOXICITY_MODEL_NAME,
        top_k=None,
    )


class DetectToxicity:
    """
    Use case: detecta discurso de odio/agresividad en un texto en
    español, usado para filtrar comentarios y posts de la comunidad.
    Responsabilidad única: toxicidad. El modelo es multi-etiqueta
    (hateful, aggressive, targeted); se usa el score máximo entre las
    tres como toxicity_score.
    """

    def execute(self, text: str) -> tuple[float, bool]:
        scores = _get_pipeline()(text, truncation=True)[0]
        toxicity_score = round(max(s["score"] for s in scores), 4)
        return toxicity_score, toxicity_score >= TOXICITY_THRESHOLD
