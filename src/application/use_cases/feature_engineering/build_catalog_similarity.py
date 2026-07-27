import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import OneHotEncoder

from src.domain.entities.catalog_item import CatalogItem


class BuildCatalogSimilarity:
    """
    Use case: codifica cada artículo del catálogo como vector one-hot
    (category + brand + price_range) y calcula la matriz de similitud
    coseno entre artículos. Responsabilidad única: construir la
    matriz. No decide qué recomendar (eso lo hace RecommendCatalogItems).
    """

    def execute(self, catalog: list[CatalogItem]) -> np.ndarray:
        rows = [[item.category, item.brand, item.price_range] for item in catalog]
        encoder = OneHotEncoder()
        features = encoder.fit_transform(rows).toarray()
        return cosine_similarity(features)
