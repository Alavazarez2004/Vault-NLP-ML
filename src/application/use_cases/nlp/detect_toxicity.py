from functools import lru_cache
from transformers import pipeline

MODEL_NAME = "citizenlab/distilbert-base-multilingual-cased-toxicity"
TOXICITY_THRESHOLD = 0.50


# Mantenemos la función en caché para evitar volver a cargar el modelo en cada request
@lru_cache
def _get_pipeline():
    print("Cargando modelo de IA ligero (DistilBERT)...")
    return pipeline("text-classification", model=MODEL_NAME)


class DetectToxicity:
    """
    Detecta toxicidad y amenazas de forma 100% semántica mediante Inteligencia Artificial.
    Utiliza un modelo DistilBERT multilingüe optimizado para no exceder la RAM de Railway.
    """

    def execute(self, text: str) -> tuple[float, bool]:
        try:
            classifier = _get_pipeline()
            predictions = classifier(text)

            # Estructura devuelta: [{'label': 'toxic' | 'not_toxic', 'score': 0.98}]
            result = predictions[0]
            label = result.get("label", "").lower()
            score = float(result.get("score", 0.0))

            # Calcular puntaje de toxicidad
            if label == "toxic":
                toxicity_score = round(score, 4)
            else:
                toxicity_score = round(1.0 - score, 4)

        except Exception as e:
            print(f"Error en la evaluación de la IA: {e}")
            toxicity_score = 0.0

        is_toxic = toxicity_score >= TOXICITY_THRESHOLD

        print({
            "toxicity_score": toxicity_score,
            "is_toxic": is_toxic,
            "text": text,
        })

        return toxicity_score, is_toxic