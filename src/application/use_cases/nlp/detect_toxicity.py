from functools import lru_cache
import re
import torch
from transformers import pipeline

ZERO_SHOT_MODEL = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"
TOXICITY_THRESHOLD = 0.50

# Definimos las intenciones que queremos detectar
CANDIDATE_LABELS = [
    "una amenaza de violencia",
    "un insulto o discurso de odio",
    "un saludo o mensaje inofensivo",
]

# Diccionario de respaldo rápido (opcional, para cortocircuitar respuestas obvias)
BAD_WORDS = {
    "idiota", "imbécil", "pendejo", "estúpido", "cabrón", "puta", "mierda",
    "hijueputa", "gonorrea", "gilipollas", "boludo", "weón"
}
FORBIDDEN_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(word) for word in BAD_WORDS) + r")\b", 
    re.IGNORECASE
)


@lru_cache
def _get_pipeline():
    device = 0 if torch.cuda.is_available() else -1
    return pipeline(
        "zero-shot-classification",
        model=ZERO_SHOT_MODEL,
        device=device,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    )


class DetectToxicity:
    """
    Detecta toxicidad, amenazas e insultos utilizando clasificación Zero-Shot.
    Permite capturar intenciones como "te voy a matar" o "vas a sufrir" 
    sin necesidad de clasificadores especializados en violencia física.
    """

    def execute(self, text: str) -> tuple[float, bool]:
        # 1. Chequeo veloz por lista de palabras prohibidas (Oopcional para ahorrarse la GPU)
        contains_bad_word = bool(FORBIDDEN_PATTERN.search(text))

        # 2. Inferencia Zero-Shot
        classifier = _get_pipeline()
        
        # hypothesis_template estructura la premisa para el modelo MNLI
        result = classifier(
            text,
            candidate_labels=CANDIDATE_LABELS,
            hypothesis_template="Este texto contiene {}.",
            multi_label=True  # Permite que un texto sea tanto insulto como amenaza
        )

        # Mapeamos los scores a sus etiquetas
        label_scores = dict(zip(result["labels"], result["scores"]))

        threat_score = label_scores.get("una amenaza de violencia", 0.0)
        hate_score = label_scores.get("un insulto o discurso de odio", 0.0)

        # Tomamos el valor máximo entre las categorías nocivas
        toxicity_score = round(max(threat_score, hate_score), 4)

        # Determinación final
        is_toxic = contains_bad_word or (toxicity_score >= TOXICITY_THRESHOLD)

        print({
            "toxicity_score": toxicity_score,
            "threat_score": round(threat_score, 4),
            "hate_score": round(hate_score, 4),
            "contains_bad_word": contains_bad_word,
            "is_toxic": is_toxic,
            "text": text,
        })

        return toxicity_score, is_toxic