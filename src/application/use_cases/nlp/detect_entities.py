import re
from functools import lru_cache

import spacy

from src.domain.dtos.entity_dto import EntityDTO

SPACY_MODEL_NAME = "es_core_news_sm"

# Gazetteer de marcas comunes en el dominio VAULT (sneakers, relojes,
# lentes, moda). spaCy no reconoce BRAND como entidad estándar -- se
# complementa NER con este diccionario.
BRAND_GAZETTEER = {
    "nike", "adidas", "puma", "reebok", "new balance", "converse", "vans",
    "jordan", "under armour", "fila", "asics",
    "rolex", "casio", "seiko", "citizen", "fossil",
    "ray-ban", "rayban", "oakley",
    "louis vuitton", "gucci", "fendi", "prada", "supreme", "coach",
}

_BRAND_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(b) for b in sorted(BRAND_GAZETTEER, key=len, reverse=True)) + r")\b",
    re.IGNORECASE,
)


@lru_cache
def _get_nlp():
    return spacy.load(SPACY_MODEL_NAME)


class DetectEntities:
    """
    Use case: extrae entidades nombradas (personas, lugares, marcas) de
    un texto en español. Responsabilidad única: NER. Combina spaCy
    (PER/LOC/MISC) con un gazetteer de marcas para BRAND, ya que el
    modelo base de spaCy no distingue marcas de organizaciones genéricas.
    """

    def execute(self, text: str) -> list[EntityDTO]:
        entities: list[EntityDTO] = []
        matched_spans: list[tuple[int, int]] = []

        for match in _BRAND_PATTERN.finditer(text):
            entities.append(EntityDTO(text=match.group(0), label="BRAND"))
            matched_spans.append(match.span())

        doc = _get_nlp()(text)
        for ent in doc.ents:
            if self._overlaps(ent.start_char, ent.end_char, matched_spans):
                continue
            entities.append(EntityDTO(text=ent.text, label=ent.label_))

        return entities

    @staticmethod
    def _overlaps(start: int, end: int, spans: list[tuple[int, int]]) -> bool:
        return any(start < s_end and end > s_start for s_start, s_end in spans)
