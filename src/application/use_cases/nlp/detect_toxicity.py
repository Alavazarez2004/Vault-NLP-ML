from functools import lru_cache
import requests

# Modelo de IA multilingüe especializado en toxicidad, insultos y AMENAZAS
API_URL = "https://api-inference.huggingface.co/models/unitary/multilingual-toxic-xlm-roberta"
TOXICITY_THRESHOLD = 0.50


# Mantenemos la función requerida por main.py para evitar el ImportError
@lru_cache
def _get_pipeline():
    return True


class DetectToxicity:
    """
    Detecta toxicidad de forma 100% semántica mediante Inteligencia Artificial,
    delegando la inferencia a Hugging Face para evitar saturar la RAM de Railway.
    """

    def execute(self, text: str) -> tuple[float, bool]:
        payload = {"inputs": text}

        try:
            # Petición a la API de inferencia de IA
            response = requests.post(API_URL, json=payload, timeout=8)
            response.raise_for_status()
            data = response.json()

            # Estructura devuelta por la API: [[{"label": "toxic", "score": 0.9}, ...]]
            scores = data[0] if isinstance(data, list) and isinstance(data[0], list) else data

            # Categorías nocivas evaluadas por la IA
            toxic_categories = ["toxic", "severe_toxic", "threat", "insult"]

            toxicity_score = round(
                max(
                    s["score"]
                    for s in scores
                    if s.get("label", "").lower() in toxic_categories
                ),
                4
            )

        except Exception as e:
            print(f"Error al consultar la IA de Hugging Face: {e}")
            toxicity_score = 0.0

        # La IA determina la toxicidad
        is_toxic = toxicity_score >= TOXICITY_THRESHOLD

        print({
            "toxicity_score": toxicity_score,
            "is_toxic": is_toxic,
            "text": text,
        })

        return toxicity_score, is_toxic