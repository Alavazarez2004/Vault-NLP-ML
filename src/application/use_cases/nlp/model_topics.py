import unicodedata

from src.domain.repositories.model_repository import ModelRepository

TOPIC_MODEL_FILENAME = "bertopic_vault.pkl"

# Taxonomía base de VAULT, usada como fallback por palabra clave mientras
# no exista un BERTopic entrenado offline con corpus real de la comunidad
# (train_topic_model corre por lotes una vez hay suficiente contenido).
# Las keywords están sin tildes porque el matching normaliza ambos lados
# (usuarios reales suelen escribir sin acentos).
KEYWORD_TAXONOMY: dict[str, list[str]] = {
    "restauración": ["restaurar", "restauracion", "reparar", "reparacion", "arreglar"],
    "limpieza": ["limpiar", "limpieza", "lavar", "lavado"],
    "autenticidad": ["autentico", "original", "replica", "falso"],
    "compra": ["comprar", "compra", "adquirir"],
    "venta": ["vender", "venta", "vendo"],
    "envío": ["envio", "entrega", "despacho"],
    "precio": ["precio", "costo", "vale", "cuesta"],
    "calidad": ["calidad", "estado", "conservacion"],
    "coleccion": ["coleccion", "coleccionar", "coleccionista"],
}


def _strip_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(c for c in normalized if not unicodedata.combining(c))


class ModelTopics:
    """
    Use case: asigna tópicos a un texto. Responsabilidad única: topic
    modeling. Si hay un BERTopic entrenado (persistido vía ModelRepository
    a partir de corpus real de la comunidad), se usa su transform();
    si no, se cae a extracción por palabra clave sobre la taxonomía base.
    """

    def __init__(self, model_repository: ModelRepository) -> None:
        self._model_repository = model_repository

    def execute(self, text: str) -> list[str]:
        if self._model_repository.exists(TOPIC_MODEL_FILENAME):
            return self._topics_from_bertopic(text)
        return self._topics_from_keywords(text)

    def _topics_from_bertopic(self, text: str) -> list[str]:
        topic_model = self._model_repository.load(TOPIC_MODEL_FILENAME)
        topic_ids, _ = topic_model.transform([text])
        topics = []
        for topic_id in topic_ids:
            if topic_id == -1:
                continue
            words = [w for w, _ in topic_model.get_topic(topic_id)[:2]]
            topics.append(" ".join(words))
        return topics or self._topics_from_keywords(text)

    @staticmethod
    def _topics_from_keywords(text: str) -> list[str]:
        normalized_text = _strip_accents(text.lower())
        return [
            topic
            for topic, keywords in KEYWORD_TAXONOMY.items()
            if any(keyword in normalized_text for keyword in keywords)
        ]
