from abc import ABC, abstractmethod
from uuid import UUID


class UserCollectionRepository(ABC):
    """
    Puerto para saber qué artículos del catálogo (item_id) ya tiene un
    usuario, y qué tienen otros usuarios de su mismo segmento. Esto es
    lo que permite las dos estrategias de recomendación de artículos:
    por contenido (similar a lo que ya tiene) y por cluster (popular en
    su segmento).
    """

    @abstractmethod
    def get_collection(self, user_id: UUID) -> set[str]:
        raise NotImplementedError

    @abstractmethod
    def get_collections_by_cluster(self, cluster_id: int) -> dict[UUID, set[str]]:
        """user_id -> sus item_id, para todos los usuarios de ese cluster."""
        raise NotImplementedError
