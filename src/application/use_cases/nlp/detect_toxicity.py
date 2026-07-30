from functools import lru_cache

import torch
from transformers import pipeline

TOXICITY_MODEL_NAME = "pysentimiento/robertuito-hate-speech"
BAD_WORDS = {
    "idiota",
    "imbécil",
    "imbecil",
    "pendejo",
    "estúpido",
    "estupido",
    "cabrón",
    "cabron",
    "puta",
    "mierda",
    "pinche",
    "pinches",
    "chingada",
    "chingar",
    "verga",
    "culero",
    "jodido"
}
TOXICITY_THRESHOLD = 0.40


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

    def execute(self, text: str) -> tuple[float, bool]:
        scores = _get_pipeline()(text, truncation=True)[0]

        toxicity_score = round(max(s["score"] for s in scores), 4)

        is_toxic = toxicity_score >= TOXICITY_THRESHOLD

        text_lower = text.lower()

        contains_bad_word = any(
            word in text_lower
            for word in BAD_WORDS
        )

        if contains_bad_word:
            is_toxic = True
            
        print({
            "toxicity_score": toxicity_score,
            "contains_bad_word": contains_bad_word,
            "is_toxic": is_toxic,
            "text": text,
        })

        return toxicity_score, is_toxic