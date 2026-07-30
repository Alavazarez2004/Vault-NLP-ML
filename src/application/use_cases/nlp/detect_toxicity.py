from functools import lru_cache

from transformers import pipeline

TOXICITY_MODEL_NAME = "pysentimiento/robertuito-hate-speech"

# Umbrales por etiqueta en vez de un solo umbral global sobre el score
# máximo: "targeted" (ataque dirigido a una persona/grupo específico) y
# "hateful" se consideran más graves que "aggressive" (tono agresivo sin
# necesariamente ser odio), por eso su umbral es más bajo.
TOXICITY_THRESHOLDS: dict[str, float] = {
    "hateful": 0.5,
    "targeted": 0.5,
    "aggressive": 0.6,
}
DEFAULT_THRESHOLD = 0.5


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
    (hateful, aggressive, targeted); cada etiqueta se compara contra su
    propio umbral (TOXICITY_THRESHOLDS) en vez de un único umbral global
    sobre el score máximo, para poder ser más estricto con categorías
    más graves (hateful/targeted) que con otras (aggressive).

    Devuelve (toxicity_score, is_toxic, reason): reason es la etiqueta
    que causó que is_toxic sea True (la de mayor score entre las que
    superaron su umbral), o None si no se marcó como tóxico. La decisión
    de qué hacer con is_toxic (guardar o rechazar el contenido) NO vive
    aquí -- la toma el backend (VaultBack, Go) al recibir la respuesta
    de POST /api/v1/nlp/analyze.
    """

    def execute(self, text: str) -> tuple[float, bool, str | None]:
        scores = _get_pipeline()(text, truncation=True)[0]

        toxicity_score = 0.0
        flagged: list[tuple[str, float]] = []

        for item in scores:
            label = item["label"]
            score = item["score"]
            toxicity_score = max(toxicity_score, score)

            threshold = TOXICITY_THRESHOLDS.get(label, DEFAULT_THRESHOLD)
            if score >= threshold:
                flagged.append((label, score))

        is_toxic = bool(flagged)
        reason = max(flagged, key=lambda x: x[1])[0] if flagged else None

        return round(toxicity_score, 4), is_toxic, reason