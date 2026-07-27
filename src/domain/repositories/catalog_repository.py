from abc import ABC, abstractmethod

from src.domain.entities.catalog_item import CatalogItem


class CatalogRepository(ABC):
    """
    Puerto para obtener el catálogo de artículos disponibles para
    recomendación, sin importar si vive en memoria, un CSV o Postgres.
    """

    @abstractmethod
    def get_all(self) -> list[CatalogItem]:
        raise NotImplementedError
